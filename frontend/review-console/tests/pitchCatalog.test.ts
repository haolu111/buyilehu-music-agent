import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import {
  PITCH_CATALOG_VERSION,
  PITCH_CLASS_DEFINITIONS,
  PITCH_DEFINITIONS,
  PITCH_REGISTERS,
  REGISTERED_PITCH_DEFINITIONS,
  pitchToMidi,
  registeredPitchToMidi,
  resolveRegisteredPitchToken,
  resolvePitchToken,
  sequenceToMidiOffsets
} from "../src/shared/pitchCatalog";

assert.equal(PITCH_CATALOG_VERSION, "pitch_catalog_v1");
assert.equal(PITCH_CLASS_DEFINITIONS.length, 12, "十二平均律应有 12 个唯一半音级");
assert.deepEqual(
  PITCH_CLASS_DEFINITIONS.map((pitch) => pitch.semitone),
  Array.from({ length: 12 }, (_, index) => index),
  "半音级应完整覆盖 0–11"
);
assert.equal(PITCH_DEFINITIONS.length, 13, "单音库应额外保留高音 1' 作为音域端点");
assert.equal(PITCH_DEFINITIONS.at(-1)?.id, "do_high");
assert.equal(PITCH_DEFINITIONS.at(-1)?.semitone, 12);

assert.equal(resolvePitchToken("4")?.id, "fa");
assert.equal(resolvePitchToken("7")?.id, "ti");
for (const alias of ["♯4", "#4", "升4", "♭5", "b5", "降5"]) {
  assert.equal(resolvePitchToken(alias)?.id, "fa_sharp_sol_flat", `${alias} 应解析为升4/降5`);
}

assert.equal(pitchToMidi("do"), 60);
assert.equal(pitchToMidi("♯4"), 66);
assert.equal(pitchToMidi("♯4", 62), 68, "更换主音后应保持半音关系");
assert.deepEqual(sequenceToMidiOffsets(["do", "♯1", "re", "fa", "ti", "do_high"]), [0, 1, 2, 5, 11, 12]);

assert.deepEqual(PITCH_REGISTERS.map((register) => register.id), ["small", "small_one", "small_two"]);
assert.deepEqual(PITCH_REGISTERS.map((register) => register.baseMidi), [48, 60, 72]);
assert.equal(REGISTERED_PITCH_DEFINITIONS.length, 36, "三个音组应派生 36 个独立音高");
assert.deepEqual(
  REGISTERED_PITCH_DEFINITIONS.map((pitch) => pitch.midi),
  Array.from({ length: 36 }, (_, index) => index + 48),
  "绝对 MIDI 应连续覆盖 C3-B5"
);
for (const register of PITCH_REGISTERS) {
  const pitches = REGISTERED_PITCH_DEFINITIONS.filter((pitch) => pitch.registerId === register.id);
  assert.equal(pitches.length, 12, `${register.chineseName} 应包含 12 个音高`);
  assert.deepEqual(
    pitches.filter((pitch) => pitch.numberLabels.length === 1).map((pitch) => pitch.pitchId),
    ["do", "re", "mi", "fa", "sol", "la", "ti"],
    `${register.chineseName} 应完整包含自然音 1-7`
  );
}

assert.equal(resolveRegisteredPitchToken("small:do")?.scientificLabels[0], "C3");
assert.equal(resolveRegisteredPitchToken("C4")?.id, "small_one:do");
assert.equal(resolveRegisteredPitchToken("C#5")?.id, "small_two:do_sharp_re_flat");
assert.equal(resolveRegisteredPitchToken("D♭5")?.id, "small_two:do_sharp_re_flat");
assert.equal(registeredPitchToMidi("small:do"), 48);
assert.equal(registeredPitchToMidi("F♯4"), 66);
assert.equal(registeredPitchToMidi("B5"), 83);

const root = dirname(dirname(fileURLToPath(import.meta.url)));
for (const sourcePath of [
  "src/App.tsx",
  "src/student-game/PitchLadderScene.ts",
  "src/student-game/SolfegeTargetScene.ts",
  "src/student-game/StudentGameApp.tsx",
  "src/student-game/musicEntityExecution.ts"
]) {
  const source = readFileSync(join(root, sourcePath), "utf8");
  assert.match(source, /(?:resolvePitchToken|sequenceToMidiOffsets)/, `${sourcePath} 应使用共享音高解析器`);
  assert.doesNotMatch(source, /do:\s*0,[\s\S]{0,180}?re:\s*2,[\s\S]{0,180}?mi:\s*4/, `${sourcePath} 不应复制自然音半音表`);
}
