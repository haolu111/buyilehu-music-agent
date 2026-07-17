import { VIRTUAL_INSTRUMENT_SOUNDBANK_BUILD_PLAN } from "../src/virtual-instruments/core/soundbankBuildPlan";

function assertEqual<T>(actual: T, expected: T, label: string) {
  if (actual !== expected) throw new Error(`${label}: expected ${String(expected)}, got ${String(actual)}`);
}

function assertDeepEqual(actual: unknown, expected: unknown, label: string) {
  const left = JSON.stringify(actual);
  const right = JSON.stringify(expected);
  if (left !== right) throw new Error(`${label}: expected ${right}, got ${left}`);
}

assertEqual(VIRTUAL_INSTRUMENT_SOUNDBANK_BUILD_PLAN.length, 10, "build plan covers ten instruments");
assertDeepEqual(
  VIRTUAL_INSTRUMENT_SOUNDBANK_BUILD_PLAN.slice(0, 4).map((item) => item.program),
  [0, 13, 12, 9],
  "pitched instruments use MuseScore General GM presets",
);
const frameDrumPlan = VIRTUAL_INSTRUMENT_SOUNDBANK_BUILD_PLAN.find((item) => item.instrumentId === "virtual_frame_drum");
assertEqual(frameDrumPlan?.sourceId, "vcsl_frame_drum_cc0", "frame drum uses an exact CC0 frame-drum recording, not a conga proxy");
assertEqual(frameDrumPlan?.outputFormat, "sf2", "custom frame-drum bank honestly declares uncompressed SoundFont2");
assertEqual(frameDrumPlan?.drum, false, "custom frame-drum bank uses its independent melodic preset instead of GM channel 10");
assertEqual(
  VIRTUAL_INSTRUMENT_SOUNDBANK_BUILD_PLAN.slice(5).every((item) => item.drum),
  true,
  "remaining classroom percussion is extracted from the real GM drum preset",
);
assertDeepEqual(
  VIRTUAL_INSTRUMENT_SOUNDBANK_BUILD_PLAN.find((item) => item.instrumentId === "virtual_woodblock")?.midiNotes,
  [76, 77],
  "woodblock pack contains only high and low woodblock samples",
);
assertDeepEqual(
  VIRTUAL_INSTRUMENT_SOUNDBANK_BUILD_PLAN.find((item) => item.instrumentId === "virtual_shaker")?.midiNotes,
  [70],
  "Chinese classroom shakers use the real GM Maracas sample, not Small Shaker",
);
