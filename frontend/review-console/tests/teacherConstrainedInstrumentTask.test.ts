import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { resolveGradeTimingWindows } from "../src/activity/rhythmWarmupLogic";
import { evaluateInstrumentTask, validateInstrumentTask, type TeacherConstrainedInstrumentTask } from "../src/virtual-instruments/core/teacherConstrainedInstrumentTask";

const timedTask: TeacherConstrainedInstrumentTask = {
  version: "teacher_constrained_instrument_task_v1",
  id: "snare-steady-beat",
  kind: "steady_beat",
  instrumentId: "virtual_snare_drum",
  gradePreset: "middle_primary",
  bpm: 120,
  targetEvents: [
    { id: "beat-1", offsetBeats: 0, zoneId: "center" },
    { id: "beat-2", offsetBeats: 1, zoneId: "center" },
  ],
};

type ParityCase = {
  id: string;
  task: TeacherConstrainedInstrumentTask;
  performanceEvents: Array<{ timeMs: number; zoneId?: string; midi?: number }>;
  expectedWindows?: { correctMs: number; outerMs: number };
  expectedEvidence: {
    evidenceStatus: "evidence_pass" | "adjust" | "participation_only";
    correctCount: number;
    earlyCount: number;
    lateCount: number;
    extraCount: number;
    missedCount: number;
    matchedTargetCount: number;
    missedTargetIds: string[];
    restErrorCount: number;
    violations: string[];
    eventStatuses: string[];
    eventIndexes: number[];
  };
};

const parityCases = JSON.parse(
  readFileSync(resolve(process.cwd(), "../../contracts/music/teacher-constrained-instrument-task-parity.v1.json"), "utf8"),
).cases as ParityCase[];

const correct = evaluateInstrumentTask(timedTask, [
  { timeMs: 0, zoneId: "center" },
  { timeMs: 500, zoneId: "center" },
]);
assert.equal(correct.evidenceStatus, "evidence_pass");
assert.equal(correct.correctCount, 2);
assert.equal(correct.missedCount, 0);

const repeated = evaluateInstrumentTask(timedTask, [
  { timeMs: 0, zoneId: "center" },
  { timeMs: 20, zoneId: "center" },
  { timeMs: 500, zoneId: "center" },
]);
assert.equal(repeated.extraCount, 1, "a target event only matches once");

const freePlay = evaluateInstrumentTask({ ...timedTask, kind: "free_play", targetEvents: undefined }, [
  { timeMs: 40, zoneId: "rim" },
]);
assert.equal(freePlay.evidenceStatus, "participation_only");
assert.equal(freePlay.correctCount, 0, "free play never gives an automatic correctness score");

const creation = evaluateInstrumentTask({
  ...timedTask,
  kind: "constrained_composition",
  compositionRules: { allowedMidi: [60, 64, 67], requiredEventCount: { min: 3, max: 4 }, endingMidi: 60 },
}, [
  { timeMs: 0, midi: 60 },
  { timeMs: 250, midi: 64 },
  { timeMs: 500, midi: 60 },
]);
assert.equal(creation.evidenceStatus, "evidence_pass");

const invalidCreation = evaluateInstrumentTask({
  ...timedTask,
  kind: "constrained_composition",
  compositionRules: { allowedMidi: [60, 64, 67], endingMidi: 60 },
}, [
  { timeMs: 0, midi: 60 },
  { timeMs: 250, midi: 64 },
]);
assert.equal(invalidCreation.evidenceStatus, "adjust");
assert.deepEqual(invalidCreation.violations, ["ending_midi_required:60"]);
assert.equal(invalidCreation.extraCount, 0, "composition constraints do not fabricate timed extra taps");
assert.deepEqual(invalidCreation.eventResults, [], "composition constraints report global violations without per-event feedback");

for (const invalidTask of [
  { ...timedTask, gradePreset: "not_a_grade" },
  (() => {
    const { gradePreset: _gradePreset, ...taskWithoutGrade } = timedTask;
    return taskWithoutGrade;
  })(),
]) {
  assert.throws(
    () => validateInstrumentTask(invalidTask as unknown as TeacherConstrainedInstrumentTask),
    (error: unknown) => !(error instanceof TypeError),
    "gradePreset must be rejected at the contract boundary with a domain error",
  );
}

assert.throws(
  () => validateInstrumentTask({
    ...timedTask,
    kind: "constrained_composition",
    compositionRules: {
      restWindowsBeats: [[1, 2]],
      requiredRestCount: { min: 2, max: 3 },
    },
  }),
  "a declared requiredRestCount must match the supplied rest windows",
);

for (const compositionRules of [
  { restWindowsBeats: [[1, 2]] as Array<[number, number]> },
  { requiredRestCount: { min: 0, max: 1 } },
]) {
  assert.throws(
    () => validateInstrumentTask({ ...timedTask, compositionRules }),
    (error: unknown) => error instanceof Error && error.message.includes("constrained_composition"),
    "rest rules must be rejected for timed tasks at the contract boundary",
  );
}

for (const invalidTask of [
  { ...timedTask, bpm: Number.NaN },
  { ...timedTask, bpm: Number.POSITIVE_INFINITY },
  { ...timedTask, targetEvents: [{ id: "invalid-offset", offsetBeats: Number.NaN, zoneId: "center" }] },
  { ...timedTask, targetEvents: [{ id: "invalid-midi", offsetBeats: 0, midi: Number.POSITIVE_INFINITY }] },
]) {
  assert.throws(
    () => validateInstrumentTask(invalidTask),
    "non-finite task timing and MIDI values must be rejected before evaluation",
  );
}

for (const invalidEvent of [
  { timeMs: Number.NaN, zoneId: "center" },
  { timeMs: Number.POSITIVE_INFINITY, zoneId: "center" },
  { timeMs: -1, zoneId: "center" },
  { timeMs: 0, zoneId: "center", midi: Number.NaN },
]) {
  assert.throws(
    () => evaluateInstrumentTask(timedTask, [invalidEvent]),
    "non-finite or negative student event values must be rejected before sorting",
  );
}

for (const parityCase of parityCases) {
  if (parityCase.expectedWindows) {
    assert.deepEqual(
      resolveGradeTimingWindows(parityCase.task.bpm ?? 100, parityCase.task.gradePreset),
      parityCase.expectedWindows,
      `${parityCase.id} must use the shared timing window`,
    );
  }
  const evidence = evaluateInstrumentTask(parityCase.task, parityCase.performanceEvents);
  assert.deepEqual(
    {
      evidenceStatus: evidence.evidenceStatus,
      correctCount: evidence.correctCount,
      earlyCount: evidence.earlyCount,
      lateCount: evidence.lateCount,
      extraCount: evidence.extraCount,
      missedCount: evidence.missedCount,
      matchedTargetCount: evidence.matchedTargetCount,
      missedTargetIds: evidence.missedTargetIds,
      restErrorCount: evidence.restErrorCount,
      violations: evidence.violations,
      eventStatuses: evidence.eventResults.map((event) => event.status),
      eventIndexes: evidence.eventResults.map((event) => event.eventIndex),
    },
    parityCase.expectedEvidence,
    `${parityCase.id} must preserve the same objective evidence in TypeScript and Python`,
  );
}

console.log("teacher constrained instrument task tests passed");
