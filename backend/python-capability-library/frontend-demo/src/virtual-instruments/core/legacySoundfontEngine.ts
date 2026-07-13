import type { VirtualInstrumentAudioEngine } from "./audioEngine";
import { getAuditedClassroomAudioAsset } from "./virtualInstrumentCatalog";
import { runtimeAssetUrl } from "../../shared/runtimeAssets";

type PlayingSample = { stop: () => void };
type FallbackFormat = "midi-js-mp3" | "legacy-wav-map";

type LegacySoundfontEngineOptions = {
  loadText?: (url: string) => Promise<string>;
  decodeDataUrl?: (dataUrl: string) => Promise<AudioBuffer>;
  playBuffer?: (buffer: AudioBuffer, gain: number) => PlayingSample;
  playDataUrl?: (dataUrl: string, gain: number) => PlayingSample;
  onStage?: (stage: string) => void;
  createAudioContext?: () => AudioContext;
};

export async function mapWithConcurrency<T, R>(
  values: T[],
  limit: number,
  mapper: (value: T, index: number) => Promise<R>,
): Promise<R[]> {
  const results = new Array<R>(values.length);
  let nextIndex = 0;
  const workers = Array.from({ length: Math.min(Math.max(1, limit), values.length) }, async () => {
    while (nextIndex < values.length) {
      const index = nextIndex;
      nextIndex += 1;
      results[index] = await mapper(values[index], index);
    }
  });
  await Promise.all(workers);
  return results;
}

export function midiToSampleName(midi: number): string {
  const names = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"];
  return `${names[midi % 12]}${Math.floor(midi / 12) - 1}`;
}

export function parseLegacySampleMap(source: string): Record<string, string> {
  const assignmentStart = source.lastIndexOf("= {");
  const objectEnd = source.lastIndexOf("}");
  if (assignmentStart < 0 || objectEnd <= assignmentStart) {
    throw new Error("Invalid virtual instrument fallback sample map");
  }
  const parsed = JSON.parse(source.slice(assignmentStart + 2, objectEnd + 1)) as Record<string, unknown>;
  for (const [note, dataUrl] of Object.entries(parsed)) {
    if (!/^[A-G](?:b)?-?\d+$/.test(note) || typeof dataUrl !== "string" || !dataUrl.startsWith("data:audio/")) {
      throw new Error("Invalid virtual instrument fallback sample entry");
    }
  }
  return parsed as Record<string, string>;
}

export function shouldPredecodeFallback(format: FallbackFormat): boolean {
  return format === "legacy-wav-map";
}

export class LegacySoundfontEngine implements VirtualInstrumentAudioEngine {
  readonly id = "legacy_soundfont" as const;
  private readonly buffers = new Map<number, AudioBuffer>();
  private readonly dataUrls = new Map<number, string>();
  private readonly playing = new Map<number, Set<PlayingSample>>();
  private readonly loadText: (url: string) => Promise<string>;
  private readonly decodeDataUrl: ((dataUrl: string) => Promise<AudioBuffer>) | null;
  private readonly playBuffer: ((buffer: AudioBuffer, gain: number) => PlayingSample) | null;
  private readonly playDataUrl: (dataUrl: string, gain: number) => PlayingSample;
  private readonly onStage: (stage: string) => void;
  private readonly createAudioContext: () => AudioContext | null;
  private readonly customPlayback: boolean;
  private sustainActive = false;
  private readonly sustainedNotes = new Set<number>();
  private ownedContext: AudioContext | null = null;

  constructor(options: LegacySoundfontEngineOptions = {}) {
    this.onStage = options.onStage ?? (() => undefined);
    this.createAudioContext = options.createAudioContext ?? (() => typeof AudioContext === "undefined" ? null : new AudioContext({ latencyHint: "interactive" }));
    this.loadText = options.loadText ?? (async (url) => {
      const response = await fetch(url);
      if (!response.ok) throw new Error(`Fallback sample map load failed (${response.status}): ${url}`);
      return response.text();
    });
    this.customPlayback = Boolean(options.decodeDataUrl || options.playBuffer || options.playDataUrl);
    if (options.decodeDataUrl && options.playBuffer) {
      this.decodeDataUrl = options.decodeDataUrl;
      this.playBuffer = options.playBuffer;
      this.playDataUrl = options.playDataUrl ?? (() => { throw new Error("URL sample playback is not configured"); });
    } else {
      this.decodeDataUrl = null;
      this.playBuffer = null;
      this.playDataUrl = options.playDataUrl ?? ((dataUrl, gainValue) => {
        const audio = new Audio(dataUrl);
        audio.preload = "auto";
        audio.volume = gainValue;
        void audio.play();
        return { stop: () => {
          audio.pause();
          audio.currentTime = 0;
        } };
      });
    }
  }

  async initialize(instrumentId: string): Promise<void> {
    this.onStage("主引擎不可用，正在载入后备采样");
    this.allNotesOff();
    this.buffers.clear();
    this.dataUrls.clear();
    const asset = getAuditedClassroomAudioAsset(instrumentId);
    if (!asset) throw new Error(`No audited fallback sample map for ${instrumentId}`);
    if (!this.customPlayback && shouldPredecodeFallback(asset.fallback.format)) this.prepareOwnedContext();
    const sampleMap = parseLegacySampleMap(await this.loadText(runtimeAssetUrl(asset.fallback.path)));
    this.onStage(`正在载入 ${Object.keys(sampleMap).length} 个后备采样`);
    for (const [noteName, dataUrl] of Object.entries(sampleMap)) this.dataUrls.set(sampleNameToMidi(noteName), dataUrl);
    if (this.decodeDataUrl && this.playBuffer) {
      await mapWithConcurrency(Object.entries(sampleMap), 4, async ([noteName, dataUrl]) => {
        const buffer = await rejectAfter(this.decodeDataUrl!(dataUrl), 8_000, `sample decode ${noteName}`);
        this.buffers.set(sampleNameToMidi(noteName), buffer);
      });
    } else if (this.ownedContext && shouldPredecodeFallback(asset.fallback.format)) {
      await mapWithConcurrency(Object.entries(sampleMap), 4, async ([noteName, dataUrl]) => {
        this.buffers.set(sampleNameToMidi(noteName), await decodeDataUrlWithContext(this.ownedContext!, dataUrl));
      });
    }
  }

  noteOn(midi: number, velocity: number): void {
    if (this.ownedContext?.state === "suspended") void this.ownedContext.resume().catch(() => undefined);
    const gain = Math.max(0, Math.min(127, velocity)) / 127;
    const buffer = this.buffers.get(midi);
    const dataUrl = this.dataUrls.get(midi);
    if (!buffer && !dataUrl) throw new Error(`Fallback sample is missing MIDI note ${midi}`);
    const playing = buffer
      ? (this.playBuffer ? this.playBuffer(buffer, gain) : this.playOwnedBuffer(buffer, gain))
      : this.playDataUrl(dataUrl!, gain);
    const voices = this.playing.get(midi) ?? new Set<PlayingSample>();
    voices.add(playing);
    this.playing.set(midi, voices);
  }

  noteOff(midi: number): void {
    if (this.sustainActive) {
      this.sustainedNotes.add(midi);
      return;
    }
    this.stopMidi(midi);
  }

  setSustain(active: boolean): void {
    this.sustainActive = active;
    if (active) return;
    for (const midi of this.sustainedNotes) this.stopMidi(midi);
    this.sustainedNotes.clear();
  }

  private stopMidi(midi: number): void {
    const voices = this.playing.get(midi);
    if (!voices) return;
    for (const voice of voices) voice.stop();
    this.playing.delete(midi);
  }

  allNotesOff(): void {
    for (const voices of this.playing.values()) for (const voice of voices) voice.stop();
    this.playing.clear();
    this.sustainedNotes.clear();
    this.sustainActive = false;
  }

  async destroy(): Promise<void> {
    this.allNotesOff();
    this.buffers.clear();
    this.dataUrls.clear();
    await this.ownedContext?.close();
    this.ownedContext = null;
  }

  private prepareOwnedContext(): void {
    this.ownedContext ??= this.createAudioContext();
  }

  private playOwnedBuffer(buffer: AudioBuffer, gainValue: number): PlayingSample {
    if (!this.ownedContext) throw new Error("Fallback AudioContext is not initialized");
    const source = this.ownedContext.createBufferSource();
    const gain = this.ownedContext.createGain();
    source.buffer = buffer; gain.gain.value = gainValue;
    source.connect(gain); gain.connect(this.ownedContext.destination); source.start();
    return { stop: () => { try { source.stop(); } catch { /* voice already ended */ } } };
  }
}

async function decodeDataUrlWithContext(context: AudioContext, dataUrl: string): Promise<AudioBuffer> {
  const encoded = dataUrl.slice(dataUrl.indexOf(",") + 1);
  const binary = atob(encoded);
  const bytes = new Uint8Array(binary.length);
  for (let index = 0; index < binary.length; index += 1) bytes[index] = binary.charCodeAt(index);
  return context.decodeAudioData(bytes.buffer.slice(0));
}

function rejectAfter<T>(promise: Promise<T>, timeoutMs: number, stage: string): Promise<T> {
  return new Promise((resolve, reject) => {
    const timeout = globalThis.setTimeout(() => reject(new Error(`Fallback audio timed out: ${stage}`)), timeoutMs);
    promise.then(
      (value) => { globalThis.clearTimeout(timeout); resolve(value); },
      (error) => { globalThis.clearTimeout(timeout); reject(error); },
    );
  });
}

function sampleNameToMidi(noteName: string): number {
  const match = noteName.match(/^([A-G])(?:b)?(-?\d+)$/);
  if (!match) throw new Error(`Invalid sample note name: ${noteName}`);
  const semitones: Record<string, number> = { C: 0, D: 2, E: 4, F: 5, G: 7, A: 9, B: 11 };
  const flat = noteName.includes("b") ? -1 : 0;
  return (Number(match[2]) + 1) * 12 + semitones[match[1]] + flat;
}
