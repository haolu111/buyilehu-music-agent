import assert from "node:assert/strict";
import {
  PLAYABLE_INSTRUMENT_AUDIO_POLICY_ID,
  resolveInstrumentName,
  resolvePlayableInstrumentName
} from "../src/shared/realAudio";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

function assertEqual<T>(actual: T, expected: T, label: string) {
  if (actual !== expected) {
    throw new Error(`${label}: expected ${String(expected)}, got ${String(actual)}`);
  }
}

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const source = readFileSync(join(root, "src/shared/realAudio.ts"), "utf8");

assertEqual(PLAYABLE_INSTRUMENT_AUDIO_POLICY_ID, "open_sample_no_oscillator_fallback", "strict playable policy id is stable");
assertEqual(resolveInstrumentName("小鼓"), "taiko_drum", "小鼓 maps to sampled drum");
assertEqual(resolveInstrumentName("手鼓"), "taiko_drum", "手鼓 maps to sampled drum");
assertEqual(resolveInstrumentName("木鱼"), "woodblock", "木鱼 maps to sampled woodblock");
assertEqual(resolveInstrumentName("响板"), "woodblock", "响板 maps to sampled woodblock");

assert.match(source, /options: \{ audition\?: boolean \} = \{\}/, "sample preparation exposes a silent preload option");
assert.match(source, /if \(options\.audition !== false\)/, "silent preload skips the audible test note");
assertEqual(resolveInstrumentName("三角铁"), "glockenspiel", "三角铁 maps to sampled glockenspiel");
assertEqual(resolveInstrumentName("音条琴"), "xylophone", "音条琴 maps to sampled xylophone");
assertEqual(resolveInstrumentName("竖笛"), "flute", "竖笛 maps to sampled flute");
assertEqual(resolveInstrumentName("口风琴"), "acoustic_grand_piano", "口风琴 maps to sampled keyboard sound");
assertEqual(resolvePlayableInstrumentName("classroom_percussion_kit"), "", "percussion kit is not a single playable instrument");

if (!source.includes("playPlayableInstrumentSequence")) {
  throw new Error("realAudio must expose playPlayableInstrumentSequence");
}
if (!source.includes("allowOscillatorFallback: false")) {
  throw new Error("playable instruments must disable oscillator fallback");
}
const stopPlaybackStart = source.indexOf("export function stopActiveSampledPlayback");
const stopPlaybackEnd = source.indexOf("\n}\n\nexport function", stopPlaybackStart) + 2;
const stopPlaybackSource = source.slice(stopPlaybackStart, stopPlaybackEnd);
if (!stopPlaybackSource.includes("currentLessonAudio.pause()")) {
  throw new Error("stopping a classroom round must also stop the current song clip");
}
