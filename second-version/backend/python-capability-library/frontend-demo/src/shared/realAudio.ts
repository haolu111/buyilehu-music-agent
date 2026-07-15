export type AudioPlaySource = "lesson_audio" | "soundfont" | "oscillator" | "unsupported" | "failed";

export type AudioPlayResult = {
  ok: boolean;
  source: AudioPlaySource;
  error?: string;
};

export type TimbreLikeProfile = {
  wave?: OscillatorType;
  frequency?: number;
  attack?: number;
  release?: number;
  brightness?: number;
  instrument?: string;
  label?: string;
  audio_url?: string;
  audio_clip_url?: string;
  source_audio_url?: string;
};

export type SequencePlaybackOptions = {
  instrument?: string;
  label?: string;
  baseMidi?: number;
  gap?: number;
  duration?: number;
  gain?: number;
  audioUrl?: string;
  offsetMs?: number;
  oscillatorWave?: OscillatorType;
  allowOscillatorFallback?: boolean;
  events?: Array<{ offset: number; start: number; duration: number }>;
};

export const REAL_AUDIO_POLICY_ID = "soundfont_first_hybrid_audio";
export const PLAYABLE_INSTRUMENT_AUDIO_POLICY_ID = "open_sample_no_oscillator_fallback";
import { runtimeAssetUrl } from "./runtimeAssets";

export const SOUNDFONT_PLAYER_PATHS = [
  runtimeAssetUrl("/runtime-assets/soundfont-player/soundfont-player.js"),
  "/static/assets/soundfont-player/soundfont-player.js",
  "https://cdn.jsdelivr.net/npm/soundfont-player@0.15.7/dist/soundfont-player.js",
  "https://unpkg.com/soundfont-player@0.15.7/dist/soundfont-player.js"
];
export const SOUNDFONT_LOCAL_BASE = runtimeAssetUrl("/runtime-assets/midi-js-soundfonts/FluidR3_GM/");
export const SOUNDFONT_STATIC_BASE = "/static/assets/midi-js-soundfonts/FluidR3_GM/";
export const SOUNDFONT_EXTERNAL_BASE = "https://gleitz.github.io/midi-js-soundfonts/FluidR3_GM/";

declare global {
  interface Window {
    webkitAudioContext?: typeof AudioContext;
    Soundfont?: {
      instrument: (
        context: AudioContext,
        instrumentName: string,
        options?: {
          soundfont?: string;
          format?: string;
          nameToUrl?: (name: string, soundfont: string, format: string) => string;
        }
      ) => Promise<SoundfontInstrument>;
    };
  }
}

type SoundfontInstrument = {
  play: (note: string | number, when?: number, options?: { duration?: number; gain?: number }) => ScheduledSoundfontNode | unknown;
};

type ScheduledSoundfontNode = {
  stop?: (when?: number) => void;
};

let sharedContext: AudioContext | null = null;
let soundfontLoader: Promise<boolean> | null = null;
const instrumentCache = new Map<string, Promise<SoundfontInstrument>>();
const activeSoundfontNodes = new Set<ScheduledSoundfontNode>();
let currentLessonAudio: HTMLAudioElement | null = null;

export function resolveInstrumentName(label = "") {
  const playableName = resolvePlayableInstrumentName(label);
  if (playableName) return playableName;
  const normalized = label.trim().toLowerCase();
  if (!normalized) return "acoustic_grand_piano";
  if (hasAny(normalized, ["钢琴", "piano"])) return "acoustic_grand_piano";
  if (hasAny(normalized, ["小提琴", "二胡", "violin", "erhu"])) return "violin";
  if (hasAny(normalized, ["笛", "长笛", "人声", "flute", "voice", "vocal"])) return "flute";
  if (hasAny(normalized, ["古筝", "guzheng", "koto"])) return "koto";
  if (hasAny(normalized, ["木琴", "木鱼", "小鼓", "xylophone", "drum", "wood"])) return "xylophone";
  return normalized.replace(/\s+/g, "_");
}

export function resolvePlayableInstrumentName(label = ""): string {
  const normalized = label.trim().toLowerCase().replace(/\s+/g, "_");
  if (!normalized) return "";
  if (hasAny(normalized, ["rhythm_pad", "节奏垫", "virtual_hand_drum", "hand_drum", "手鼓", "小鼓", "drum"])) return "taiko_drum";
  if (hasAny(normalized, ["woodblock_claves", "woodblock", "claves", "木鱼", "响板"])) return "woodblock";
  if (hasAny(normalized, ["shaker", "沙锤", "沙槌", "maraca"])) return "agogo";
  if (hasAny(normalized, ["triangle_bell", "triangle", "bell", "三角铁", "碰铃"])) return "glockenspiel";
  if (hasAny(normalized, ["tambourine", "铃鼓"])) return "reverse_cymbal";
  if (hasAny(normalized, ["virtual_xylophone", "pentatonic_grid", "xylophone", "音条琴", "木琴", "五声宫格"])) return "xylophone";
  if (hasAny(normalized, ["simple_keyboard", "melodica_keyboard_board", "keyboard", "piano", "钢琴", "键盘", "口风琴", "melodica"])) return "acoustic_grand_piano";
  if (hasAny(normalized, ["recorder_fingering_board", "recorder", "竖笛", "长笛", "笛", "flute"])) return "flute";
  return "";
}

export function getAudioContext() {
  const AudioContextCtor = window.AudioContext || window.webkitAudioContext;
  if (!AudioContextCtor) return null;
  if (!sharedContext) sharedContext = new AudioContextCtor();
  if (sharedContext.state === "suspended") void sharedContext.resume();
  return sharedContext;
}

export function playHybridToneSequence(offsets: number[], options: SequencePlaybackOptions = {}): boolean {
  void playHybridToneSequenceAsync(offsets, options);
  return Boolean(window.AudioContext || window.webkitAudioContext);
}

export function playPlayableInstrumentSequence(offsets: number[], options: SequencePlaybackOptions = {}): boolean {
  void playHybridToneSequenceAsync(offsets, {
    ...options,
    instrument: resolvePlayableInstrumentName(options.instrument || options.label || "") || options.instrument,
    allowOscillatorFallback: false
  });
  return Boolean(window.AudioContext || window.webkitAudioContext);
}

export async function playHybridToneSequenceAsync(offsets: number[], options: SequencePlaybackOptions = {}): Promise<AudioPlayResult> {
  const audioUrl = firstText(options.audioUrl);
  if (audioUrl) {
    const lessonResult = await playLessonAudio(audioUrl, options.offsetMs);
    if (lessonResult.ok) return lessonResult;
  }

  const context = getAudioContext();
  if (!context) return { ok: false, source: "unsupported", error: "AudioContext unavailable" };

  const baseMidi = Number(options.baseMidi ?? 60);
  const playbackEvents = options.events?.length ? options.events : undefined;
  const midiNotes = playbackEvents
    ? playbackEvents.map((event) => baseMidi + Number(event.offset || 0))
    : offsets.length
      ? offsets.map((offset) => baseMidi + Number(offset || 0))
      : [baseMidi];
  try {
    const instrument = await loadInstrument(resolveInstrumentName(options.instrument || options.label || "acoustic_grand_piano"));
    const gap = Number(options.gap ?? 0.48);
    const duration = Number(options.duration ?? Math.max(0.22, gap - 0.08));
    const events = playbackEvents || midiNotes.map((midi, index) => ({ offset: midi - baseMidi, start: index * gap, duration }));
    events.forEach((event) => {
      const node = instrument.play(baseMidi + Number(event.offset || 0), context.currentTime + Math.max(0, event.start), {
        duration: Math.max(0.08, Number(event.duration || duration)),
        gain: Number(options.gain ?? 0.9)
      });
      if (node && typeof node === "object" && "stop" in node) {
        const scheduledNode = node as ScheduledSoundfontNode;
        activeSoundfontNodes.add(scheduledNode);
        window.setTimeout(() => activeSoundfontNodes.delete(scheduledNode), Math.ceil((Math.max(0, event.start) + Math.max(0.08, Number(event.duration || duration)) + 0.5) * 1000));
      }
    });
    return { ok: true, source: "soundfont" };
  } catch (error) {
    if (options.allowOscillatorFallback === false) {
      return { ok: false, source: "failed", error: String(error) };
    }
    playOscillatorSequence(options.events?.length ? options.events : offsets, {
      context,
      wave: options.oscillatorWave || "triangle",
      gap: Number(options.gap ?? 0.48),
      gain: Number(options.gain ?? 0.16),
      baseMidi
    });
    return { ok: true, source: "oscillator", error: String(error) };
  }
}

export function stopActiveSampledPlayback() {
  if (currentLessonAudio) {
    currentLessonAudio.pause();
    currentLessonAudio.currentTime = 0;
    currentLessonAudio = null;
  }
  const context = sharedContext;
  activeSoundfontNodes.forEach((node) => {
    try {
      node.stop?.(context?.currentTime);
    } catch {
      // The node may already have ended; removing it is sufficient.
    }
  });
  activeSoundfontNodes.clear();
}

export async function prepareSampledInstrument(
  instrument: string,
  options: { audition?: boolean } = {}
): Promise<AudioPlayResult> {
  const context = getAudioContext();
  if (!context) return { ok: false, source: "unsupported", error: "AudioContext unavailable" };
  try {
    if (context.state === "suspended") await context.resume();
    const sampledInstrument = await loadInstrument(resolveInstrumentName(instrument));
    if (options.audition !== false) {
      sampledInstrument.play(72, context.currentTime + 0.02, { duration: 0.08, gain: 0.32 });
    }
    return { ok: true, source: "soundfont" };
  } catch (error) {
    return { ok: false, source: "failed", error: String(error) };
  }
}

export function playHybridTimbreProfile(profile?: TimbreLikeProfile | null, options: SequencePlaybackOptions = {}): boolean {
  void playHybridTimbreProfileAsync(profile, options);
  return Boolean(profile && (window.AudioContext || window.webkitAudioContext));
}

export async function playHybridTimbreProfileAsync(profile?: TimbreLikeProfile | null, options: SequencePlaybackOptions = {}): Promise<AudioPlayResult> {
  if (!profile) return { ok: false, source: "failed", error: "Missing timbre profile" };
  const audioUrl = firstText(options.audioUrl, profile.audio_url, profile.audio_clip_url, profile.source_audio_url);
  if (audioUrl) {
    const lessonResult = await playLessonAudio(audioUrl, options.offsetMs);
    if (lessonResult.ok) return lessonResult;
  }
  const frequency = Number(profile.frequency || 440);
  const midi = Math.max(24, Math.min(96, Math.round(69 + 12 * Math.log2(frequency / 440))));
  const instrument = resolveInstrumentName(options.instrument || profile.instrument || profile.label || "");
  return playHybridToneSequenceAsync([midi - Number(options.baseMidi ?? 60)], {
    ...options,
    instrument,
    duration: Number(options.duration ?? 1.0),
    gap: Number(options.gap ?? 0.78),
    oscillatorWave: profile.wave || "sine"
  });
}

export async function playLessonAudio(audioUrl: string, offsetMs = 0): Promise<AudioPlayResult> {
  const source = audioUrl.trim();
  if (!source) return { ok: false, source: "failed", error: "Missing audio URL" };
  try {
    if (currentLessonAudio) {
      currentLessonAudio.pause();
      currentLessonAudio.currentTime = 0;
    }
    const audio = new Audio(source);
    currentLessonAudio = audio;
    audio.preload = "auto";
    audio.currentTime = Math.max(0, Number(offsetMs || 0) / 1000);
    await audio.play();
    return { ok: true, source: "lesson_audio" };
  } catch (error) {
    return { ok: false, source: "failed", error: String(error) };
  }
}

async function loadInstrument(instrumentName: string) {
  const context = getAudioContext();
  if (!context) throw new Error("AudioContext unavailable");
  await loadSoundfontPlayer();
  if (!window.Soundfont?.instrument) throw new Error("Soundfont player unavailable");
  const normalized = resolveInstrumentName(instrumentName);
  if (!instrumentCache.has(normalized)) {
    const instrumentPromise = window.Soundfont.instrument(context, normalized, {
        soundfont: "FluidR3_GM",
        format: "mp3",
        nameToUrl: (name, _soundfont, format) => `${SOUNDFONT_LOCAL_BASE}${name}-${format}.js`
      }).catch(async () =>
        window.Soundfont!.instrument(context, normalized, {
          soundfont: "FluidR3_GM",
          format: "mp3",
          nameToUrl: (name, _soundfont, format) => `${SOUNDFONT_STATIC_BASE}${name}-${format}.js`
        })
      ).catch(() =>
        window.Soundfont!.instrument(context, normalized, {
          soundfont: "FluidR3_GM",
          format: "mp3",
          nameToUrl: (name, _soundfont, format) => `${SOUNDFONT_EXTERNAL_BASE}${name}-${format}.js`
        })
      ).catch((error) => {
        instrumentCache.delete(normalized);
        throw error;
      });
    instrumentCache.set(normalized, instrumentPromise);
  }
  return instrumentCache.get(normalized)!;
}

async function loadSoundfontPlayer() {
  if (window.Soundfont?.instrument) return true;
  if (!soundfontLoader) {
    soundfontLoader = loadFirstScript(SOUNDFONT_PLAYER_PATHS)
      .then(() => Boolean(window.Soundfont?.instrument))
      .catch((error) => {
        soundfontLoader = null;
        throw error;
      });
  }
  return soundfontLoader;
}

async function loadFirstScript(urls: string[]) {
  let lastError: unknown = null;
  for (const url of urls) {
    try {
      await injectScript(url);
      return;
    } catch (error) {
      lastError = error;
    }
  }
  throw lastError || new Error("No SoundFont script loaded");
}

function injectScript(src: string) {
  return new Promise<void>((resolve, reject) => {
    const existing = document.querySelector<HTMLScriptElement>(`script[data-buyilehu-soundfont][src="${src}"]`);
    if (existing) {
      if (existing.dataset.loaded === "true") resolve();
      else existing.addEventListener("load", () => resolve(), { once: true });
      return;
    }
    const script = document.createElement("script");
    script.src = src;
    script.async = true;
    script.dataset.buyilehuSoundfont = "true";
    script.addEventListener("load", () => {
      script.dataset.loaded = "true";
      resolve();
    }, { once: true });
    script.addEventListener("error", () => reject(new Error(`Failed to load ${src}`)), { once: true });
    document.head.appendChild(script);
  });
}

function playOscillatorSequence(
  offsets: Array<number | { offset: number; start: number; duration: number }>,
  options: { context: AudioContext; wave: OscillatorType; gap: number; gain: number; baseMidi?: number }
) {
  offsets.forEach((item, index) => {
    const isEvent = typeof item === "object";
    const offset = isEvent ? item.offset : item;
    const oscillator = options.context.createOscillator();
    const gain = options.context.createGain();
    const start = options.context.currentTime + (isEvent ? Math.max(0, item.start) : index * options.gap);
    const duration = isEvent ? Math.max(0.08, item.duration) : options.gap;
    oscillator.type = options.wave;
    oscillator.frequency.value = 261.63 * Math.pow(2, Number(offset || 0) / 12);
    gain.gain.setValueAtTime(0.0001, start);
    gain.gain.exponentialRampToValueAtTime(Math.max(0.01, options.gain), start + 0.03);
    gain.gain.exponentialRampToValueAtTime(0.0001, start + Math.max(0.08, duration - 0.04));
    oscillator.connect(gain);
    gain.connect(options.context.destination);
    oscillator.start(start);
    oscillator.stop(start + duration);
  });
}

function hasAny(text: string, needles: string[]) {
  return needles.some((needle) => text.includes(needle.toLowerCase()));
}

function firstText(...values: Array<string | undefined | null>) {
  return values.map((value) => String(value || "").trim()).find(Boolean) || "";
}
