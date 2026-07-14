import {
  buildMelodyContourRecord,
  buildMelodyContourTracePlan,
  evaluateMelodyContourTrace,
  judgeMelodyContourGesture
} from "../src/activity/melodyContourTraceLogic";

function assertEqual<T>(actual: T, expected: T, label: string) {
  if (actual !== expected) {
    throw new Error(`${label}: expected ${String(expected)}, got ${String(actual)}`);
  }
}

const plan = buildMelodyContourTracePlan({
  pitchMotion: ["up", "up", "down", "same"],
  melodyPhrases: ["do re mi sol mi"],
  bpm: 86,
});

assertEqual(plan.steps.length, 4, "plan builds contour steps");
assertEqual(plan.steps[0].direction, "up", "first contour step is up");
assertEqual(plan.steps[2].gesture, "手势向下", "down contour uses downward gesture");

const beforeListen = evaluateMelodyContourTrace(plan, {
  hasListenedMelody: false,
  judgements: [],
});
assertEqual(beforeListen.status, "needs_listening", "melody contour must start from listening");

const correct = judgeMelodyContourGesture(plan.steps[0], "手势向上");
assertEqual(correct.status, "correct", "up gesture passes for up step");
assertEqual(correct.feedback.includes("上行"), true, "feedback names ascending contour");

const wrong = judgeMelodyContourGesture(plan.steps[2], "手势平稳");
assertEqual(wrong.status, "wrong_direction", "flat gesture fails for down step");
assertEqual(wrong.feedback.includes("下行"), true, "feedback names descending contour");

const ready = evaluateMelodyContourTrace(plan, {
  hasListenedMelody: true,
  judgements: [
    correct,
    judgeMelodyContourGesture(plan.steps[1], "手势向上"),
    judgeMelodyContourGesture(plan.steps[2], "手势向下"),
  ],
});
assertEqual(ready.status, "ready", "three listened contour gestures are ready");
assertEqual(ready.teacherSuggestion.includes("唱回"), true, "ready suggestion returns to singing");

const record = buildMelodyContourRecord(plan, {
  hasListenedMelody: true,
  judgements: ready.judgements,
});
assertEqual(record.version, "melody_contour_trace_record_v1", "record has stable version");
assertEqual(record.readyForSingingTransfer, true, "ready record can transfer to singing");
