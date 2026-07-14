import {
  LegacySoundfontEngine,
  mapWithConcurrency,
  midiToSampleName,
  parseLegacySampleMap,
  shouldPredecodeFallback,
} from "../src/virtual-instruments/core/legacySoundfontEngine";
import {
  SPESSA_SYNTH_CONFIG,
  SpessaSynthEngine,
  withAudioInitializationTimeout,
} from "../src/virtual-instruments/core/spessaSynthEngine";

function assertEqual<T>(actual: T, expected: T, label: string) {
  if (actual !== expected) throw new Error(`${label}: expected ${String(expected)}, got ${String(actual)}`);
}

function assertDeepEqual(actual: unknown, expected: unknown, label: string) {
  const left = JSON.stringify(actual);
  const right = JSON.stringify(expected);
  if (left !== right) throw new Error(`${label}: expected ${right}, got ${left}`);
}

assertEqual(midiToSampleName(60), "C4", "middle C sample name");
assertEqual(midiToSampleName(61), "Db4", "black-key sample uses MIDI-JS flat spelling");
assertDeepEqual(
  parseLegacySampleMap('globalThis.__VIRTUAL_INSTRUMENT_SAMPLE_MAPS__ ??= {};\nglobalThis.__VIRTUAL_INSTRUMENT_SAMPLE_MAPS__["virtual_piano"] = {"C4":"data:audio/mp3;base64,AAAA"};'),
  { C4: "data:audio/mp3;base64,AAAA" },
  "legacy map parser does not evaluate downloaded JavaScript",
);
assertEqual(SPESSA_SYNTH_CONFIG.oneOutput, false, "SpessaSynth uses 17 stereo outputs instead of an invalid 34-channel output");
assertEqual(shouldPredecodeFallback("legacy-wav-map"), true, "percussion fallback is decoded into an unlocked AudioContext");
assertEqual(shouldPredecodeFallback("midi-js-mp3"), false, "large pitched fallback remains lazy-loaded");

{
  let resumeCalls = 0;
  let contextFactoryCalls = 0;
  const decoded = { duration: 1 } as AudioBuffer;
  const suspendedContext = {
    state: "suspended",
    resume: () => { resumeCalls += 1; return new Promise<void>(() => undefined); },
    decodeAudioData: async () => decoded,
    close: async () => undefined,
  } as unknown as AudioContext;
  const engine = new LegacySoundfontEngine({
    createAudioContext: () => { contextFactoryCalls += 1; return suspendedContext; },
    loadText: async () => 'globalThis.__VIRTUAL_INSTRUMENT_SAMPLE_MAPS__["virtual_frame_drum"] = {"E4":"data:audio/wav;base64,AAAA","Eb4":"data:audio/wav;base64,AAAA"};',
  });
  let initialized = false;
  await Promise.race([
    engine.initialize("virtual_frame_drum").then(() => { initialized = true; }),
    new Promise((resolve) => setTimeout(resolve, 20)),
  ]);
  assertEqual(initialized, true, "frame-drum fallback becomes ready without waiting for AudioContext resume");
  assertEqual(contextFactoryCalls, 1, "frame-drum fallback prepares its injected real-audio context");
  assertEqual(resumeCalls, 0, "audio context resume is deferred until the student's actual tap");
}
let activeDecodes = 0;
let peakDecodes = 0;
await mapWithConcurrency([1, 2, 3, 4, 5, 6], 2, async () => {
  activeDecodes += 1;
  peakDecodes = Math.max(peakDecodes, activeDecodes);
  await new Promise((resolve) => setTimeout(resolve, 1));
  activeDecodes -= 1;
});
assertEqual(peakDecodes, 2, "legacy sample decoding obeys its concurrency limit");
let timedOut = false;
await withAudioInitializationTimeout(new Promise(() => undefined), 1, "worklet ready").catch((error) => {
  timedOut = error instanceof Error && error.message === "Audio initialization timed out: worklet ready";
});
assertEqual(timedOut, true, "a stalled AudioWorklet fails over instead of leaving the UI loading forever");

{
  const calls: string[] = [];
  const engine = new SpessaSynthEngine({
    createDriver: async () => ({
      initialize: async (soundbankUrl, program, drum) => calls.push(`init:${soundbankUrl}:${program}:${drum}`),
      noteOn: (channel, midi, velocity) => calls.push(`on:${channel}:${midi}:${velocity}`),
      noteOff: (channel, midi) => calls.push(`off:${channel}:${midi}`),
      allNotesOff: () => calls.push("all-off"),
      destroy: async () => calls.push("destroy"),
    }),
  });
  await engine.initialize("virtual_xylophone");
  engine.noteOn(60, 96);
  engine.noteOff(60);
  assertDeepEqual(
    calls,
    ["init:/runtime-assets/virtual-instruments/audio/virtual_xylophone.sf3:13:false", "on:0:60:96", "off:0:60"],
    "SpessaSynth adapter selects the audited pack and original GM program",
  );
}

{
  const playedUrls: string[] = [];
  const engine = new LegacySoundfontEngine({
    loadText: async () => 'globalThis.__VIRTUAL_INSTRUMENT_SAMPLE_MAPS__["virtual_piano"] = {"C4":"data:audio/mp3;base64,AAAA"};',
    playDataUrl: (dataUrl, gain) => {
      playedUrls.push(`${dataUrl}:${gain.toFixed(3)}`);
      return { stop: () => undefined };
    },
  });
  await engine.initialize("virtual_piano");
  engine.noteOn(60, 96);
  assertDeepEqual(
    playedUrls,
    ["data:audio/mp3;base64,AAAA:0.756"],
    "production fallback becomes ready without decoding the entire keyboard up front",
  );
}

{
  const decoded = { duration: 1 } as AudioBuffer;
  const started: string[] = [];
  const engine = new LegacySoundfontEngine({
    loadText: async () => 'globalThis.__VIRTUAL_INSTRUMENT_SAMPLE_MAPS__["virtual_snare_drum"] = {"D2":"data:audio/wav;base64,AAAA"};',
    decodeDataUrl: async () => decoded,
    playBuffer: (_buffer, gain) => {
      started.push(`play:${gain.toFixed(3)}`);
      return { stop: () => started.push("stop") };
    },
  });
  await engine.initialize("virtual_snare_drum");
  engine.noteOn(38, 64);
  engine.noteOff(38);
  assertDeepEqual(started, ["play:0.504", "stop"], "legacy adapter plays and stops the exact mapped real sample");
}
