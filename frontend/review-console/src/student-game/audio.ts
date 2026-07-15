import type { TimbreAudioProfile } from "./types";
import { playHybridTimbreProfile, playHybridToneSequence, type SequencePlaybackOptions } from "../shared/realAudio";

declare global {
  interface Window {
    webkitAudioContext?: typeof AudioContext;
  }
}

export type VoiceDirection = "higher" | "same" | "lower";

export type VoicePitchResult = {
  status: "ok" | "too_quiet" | "too_short" | "unstable" | "blocked" | "unsupported";
  direction?: VoiceDirection;
  confidence: number;
  volumeLevel: number;
  stability: number;
  pitchTrace: number[];
};

export type MusicGameAudioFacade = {
  playPitchPrompt(offsets: number[]): boolean;
  playHit(): boolean;
  playMiss(): boolean;
  playReward(): boolean;
};

export type GameAudioAssetConfig = {
  sfx?: Record<string, string | undefined>;
};

export class GameAudioManager {
  private readonly assets: GameAudioAssetConfig;

  constructor(assets?: GameAudioAssetConfig | null) {
    this.assets = assets || {};
  }

  playSfx(name: string) {
    const source = this.assets.sfx?.[name];
    if (!source) return false;
    try {
      const audio = new Audio(source);
      audio.volume = 0.5;
      void audio.play().catch(() => undefined);
      return true;
    } catch {
      return false;
    }
  }

  destroy() {}
}

export function playToneSequence(
  offsets: number[],
  wave: OscillatorType = "triangle",
  gap = 0.48,
  options: SequencePlaybackOptions = {}
) {
  return playHybridToneSequence(offsets, { oscillatorWave: wave, gap, instrument: "acoustic_grand_piano", ...options });
}

export function createMusicGameAudioFacade(): MusicGameAudioFacade {
  return {
    playPitchPrompt: (offsets: number[]) => playToneSequence(offsets, "triangle", 0.5, { instrument: "acoustic_grand_piano" }),
    playHit: () => playToneSequence([7, 12], "sine", 0.14, { instrument: "xylophone", duration: 0.18 }),
    playMiss: () => playToneSequence([0, -5], "sawtooth", 0.16, { instrument: "xylophone", duration: 0.2 }),
    playReward: () => playToneSequence([0, 4, 7, 12], "triangle", 0.12, { instrument: "xylophone", duration: 0.18 })
  };
}

export function playTimbreProfile(profile?: TimbreAudioProfile | null, options: SequencePlaybackOptions = {}) {
  return playHybridTimbreProfile(profile, options);
}

export async function captureVoicePitchDirection(options: {
  durationMs?: number;
  minRms?: number;
  sameThresholdSemitones?: number;
  directionThresholdSemitones?: number;
  onUpdate?: (update: { volumeLevel: number; pitchTrace: number[] }) => void;
} = {}): Promise<VoicePitchResult> {
  const AudioCtor = window.AudioContext || window.webkitAudioContext;
  if (!AudioCtor) return emptyVoiceResult("unsupported");
  if (!navigator.mediaDevices?.getUserMedia) return emptyVoiceResult("unsupported");

  const durationMs = options.durationMs ?? 1450;
  const minRms = options.minRms ?? 0.012;
  const sameThresholdSemitones = options.sameThresholdSemitones ?? 1.1;
  const directionThresholdSemitones = options.directionThresholdSemitones ?? 0.55;
  let stream: MediaStream | null = null;
  let context: AudioContext | null = null;

  try {
    stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    context = new AudioCtor();
    const source = context.createMediaStreamSource(stream);
    const analyser = context.createAnalyser();
    analyser.fftSize = 4096;
    analyser.smoothingTimeConstant = 0.25;
    source.connect(analyser);

    const samples = new Float32Array(analyser.fftSize);
    const startedAt = performance.now();
    const pitchTrace: number[] = [];
    const volumeTrace: number[] = [];

    await new Promise<void>((resolve) => {
      const poll = () => {
        analyser.getFloatTimeDomainData(samples);
        const rms = rootMeanSquare(samples);
        volumeTrace.push(rms);
        if (rms >= minRms) {
          const pitch = estimatePitch(samples, context?.sampleRate || 44100);
          if (pitch) pitchTrace.push(pitch);
        }
        options.onUpdate?.({
          volumeLevel: Math.min(1, rms / Math.max(minRms * 4, 0.001)),
          pitchTrace: pitchTrace.slice(-18)
        });
        if (performance.now() - startedAt >= durationMs) {
          resolve();
          return;
        }
        window.setTimeout(poll, 55);
      };
      poll();
    });

    const maxVolume = Math.max(0, ...volumeTrace);
    const normalizedVolume = Math.min(1, maxVolume / Math.max(minRms * 4, 0.001));
    if (maxVolume < minRms) {
      return { ...emptyVoiceResult("too_quiet"), volumeLevel: normalizedVolume, pitchTrace };
    }
    if (pitchTrace.length < 5) {
      return { ...emptyVoiceResult("too_short"), volumeLevel: normalizedVolume, pitchTrace };
    }

    const first = average(pitchTrace.slice(0, Math.max(2, Math.floor(pitchTrace.length * 0.38))));
    const last = average(pitchTrace.slice(Math.max(0, Math.floor(pitchTrace.length * 0.62))));
    const semitoneDelta = 12 * Math.log2(last / Math.max(1, first));
    const jitter = pitchJitter(pitchTrace);
    const stability = Math.max(0, Math.min(1, 1 - jitter / 2.8));
    if (stability < 0.25) {
      return { ...emptyVoiceResult("unstable"), volumeLevel: normalizedVolume, stability, pitchTrace };
    }

    let direction: VoiceDirection = "same";
    if (semitoneDelta >= directionThresholdSemitones) direction = "higher";
    else if (semitoneDelta <= -directionThresholdSemitones) direction = "lower";
    else if (Math.abs(semitoneDelta) > sameThresholdSemitones) {
      return { ...emptyVoiceResult("unstable"), volumeLevel: normalizedVolume, stability, pitchTrace };
    }

    return {
      status: "ok",
      direction,
      confidence: Math.max(0.2, Math.min(1, stability * 0.72 + normalizedVolume * 0.28)),
      volumeLevel: normalizedVolume,
      stability,
      pitchTrace
    };
  } catch {
    return emptyVoiceResult("blocked");
  } finally {
    stream?.getTracks().forEach((track) => track.stop());
    if (context?.state !== "closed") void context?.close();
  }
}

function emptyVoiceResult(status: VoicePitchResult["status"]): VoicePitchResult {
  return { status, confidence: 0, volumeLevel: 0, stability: 0, pitchTrace: [] };
}

function rootMeanSquare(samples: Float32Array) {
  let sum = 0;
  for (let index = 0; index < samples.length; index += 1) sum += samples[index] * samples[index];
  return Math.sqrt(sum / Math.max(1, samples.length));
}

function estimatePitch(samples: Float32Array, sampleRate: number) {
  const rms = rootMeanSquare(samples);
  if (rms < 0.008) return null;
  const minLag = Math.floor(sampleRate / 900);
  const maxLag = Math.min(Math.floor(sampleRate / 80), Math.floor(samples.length / 2));
  let bestLag = -1;
  let bestCorrelation = 0;

  for (let lag = minLag; lag <= maxLag; lag += 1) {
    let correlation = 0;
    for (let index = 0; index < samples.length - lag; index += 1) {
      correlation += samples[index] * samples[index + lag];
    }
    correlation /= samples.length - lag;
    if (correlation > bestCorrelation) {
      bestCorrelation = correlation;
      bestLag = lag;
    }
  }

  if (bestLag <= 0 || bestCorrelation < rms * rms * 0.28) return null;
  return sampleRate / bestLag;
}

function average(values: number[]) {
  return values.reduce((sum, value) => sum + value, 0) / Math.max(1, values.length);
}

function pitchJitter(pitches: number[]) {
  if (pitches.length < 2) return 0;
  const deltas: number[] = [];
  for (let index = 1; index < pitches.length; index += 1) {
    deltas.push(Math.abs(12 * Math.log2(pitches[index] / Math.max(1, pitches[index - 1]))));
  }
  return average(deltas);
}
