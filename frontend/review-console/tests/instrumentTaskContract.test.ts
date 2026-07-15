import assert from "node:assert/strict";
import { INSTRUMENT_TASK_CONTRACT } from "../src/virtual-instruments/core/instrumentTaskContract";

assert.equal(INSTRUMENT_TASK_CONTRACT.version, "teacher_constrained_instrument_task_v1");
assert.deepEqual(INSTRUMENT_TASK_CONTRACT.taskKinds, [
  "free_play",
  "steady_beat",
  "rhythm_echo",
  "melody_sequence",
  "ensemble_cue",
  "constrained_composition",
]);
assert.equal(INSTRUMENT_TASK_CONTRACT.evidenceBoundary, "objective_only");
assert.deepEqual(INSTRUMENT_TASK_CONTRACT.compositionRuleFields, [
  "allowedZoneIds",
  "allowedMidi",
  "requiredEventCount",
  "endingMidi",
  "requiredBeats",
  "restWindowsBeats",
  "requiredRestCount",
]);
assert.equal(INSTRUMENT_TASK_CONTRACT.restWindowDefinition.appliesTo, "constrained_composition");

console.log("instrument task contract tests passed");
