import {
  buildRhythmAudioEvents,
  buildRhythmPerformanceTimeline,
  buildRhythmWarmupAttemptRecord,
  evaluateRhythmAttempt,
  judgeRhythmPerformanceTap,
  resolveGradeTimingWindows,
  type RhythmTapJudgement
} from "../src/activity/rhythmWarmupLogic";

function assertEqual<T>(actual: T, expected: T, label: string) {
  if (actual !== expected) throw new Error(`${label}: expected ${String(expected)}, got ${String(actual)}`);
}

function assertDeepEqual(actual: unknown, expected: unknown, label: string) {
  const actualText = JSON.stringify(actual);
  const expectedText = JSON.stringify(expected);
  if (actualText !== expectedText) throw new Error(`${label}: expected ${expectedText}, got ${actualText}`);
}

assertDeepEqual(resolveGradeTimingWindows(72, "lower_primary"), { correctMs: 150, outerMs: 267 }, "lower-primary windows scale with a slow beat");
assertDeepEqual(resolveGradeTimingWindows(72, "middle_primary"), { correctMs: 125, outerMs: 233 }, "middle-primary windows scale with a slow beat");
assertDeepEqual(resolveGradeTimingWindows(72, "upper_primary"), { correctMs: 100, outerMs: 200 }, "upper-primary windows scale with a slow beat");
assertDeepEqual(resolveGradeTimingWindows(124, "middle_primary"), { correctMs: 90, outerMs: 160 }, "timing windows respect their fast-tempo minimums");

const timeline = buildRhythmPerformanceTimeline(["quarter", "eighth_pair", "rest", "quarter"], { bpm: 60, repeatCount: 1 });
const audioEvents = buildRhythmAudioEvents(timeline, { startMs: 320 });
assertDeepEqual(
  audioEvents.map((event) => [event.patternId, event.start, event.offset]),
  [
    ["quarter", 0.32, 0],
    ["eighth_pair", 1.32, 0],
    ["eighth_pair", 1.82, 0],
    ["quarter", 3.32, 0],
  ],
  "piano playback uses the exact displayed attack timeline and one fixed standard-note offset"
);
assertDeepEqual(
  timeline.filter((event) => event.kind === "hit").map((event) => event.targetMs),
  [0, 1000, 1500, 3000],
  "performance timeline expands every required attack"
);

const judgements: RhythmTapJudgement[] = [];
judgements.push(judgeRhythmPerformanceTap(5, timeline, judgements, { bpm: 60, gradePreset: "middle_primary" }));
judgements.push(judgeRhythmPerformanceTap(20, timeline, judgements, { bpm: 60, gradePreset: "middle_primary" }));
judgements.push(judgeRhythmPerformanceTap(800, timeline, judgements, { bpm: 60, gradePreset: "middle_primary" }));
judgements.push(judgeRhythmPerformanceTap(1500, timeline, judgements, { bpm: 60, gradePreset: "middle_primary" }));
judgements.push(judgeRhythmPerformanceTap(2300, timeline, judgements, { bpm: 60, gradePreset: "middle_primary" }));

assertDeepEqual(
  judgements.map((item) => item.status),
  ["correct", "extra", "early", "correct", "rest_error"],
  "one-to-one matching identifies duplicate taps, early taps and rest errors"
);
assertEqual(judgements[0].targetEventId === judgements[1].targetEventId, false, "duplicate taps cannot reuse a matched target");

const denseTimeline = buildRhythmPerformanceTimeline(["sixteenth_four"], { bpm: 60, repeatCount: 1 });
const denseJudgements: RhythmTapJudgement[] = [];
denseJudgements.push(judgeRhythmPerformanceTap(0, denseTimeline, denseJudgements, { bpm: 60, gradePreset: "middle_primary" }));
denseJudgements.push(judgeRhythmPerformanceTap(20, denseTimeline, denseJudgements, { bpm: 60, gradePreset: "middle_primary" }));
assertDeepEqual(
  denseJudgements.map((item) => item.status),
  ["correct", "extra"],
  "a rapid duplicate closer to the consumed attack does not steal the next sixteenth-note target"
);

const retrySummary = evaluateRhythmAttempt(timeline, judgements, { bpm: 60, gradePreset: "middle_primary" });
assertEqual(retrySummary.missedCount, 1, "unmatched targets become missed notes at the end");
assertEqual(retrySummary.extraCount, 1, "extra taps are counted");
assertEqual(retrySummary.restErrorCount, 1, "rest errors are counted");
assertEqual(retrySummary.result, "retry", "rest errors require repractice");

const exactTimeline = buildRhythmPerformanceTimeline(["sixteenth_four", "eighth_pair", "quarter"], { bpm: 60, repeatCount: 1 });
const exactJudgements: RhythmTapJudgement[] = [];
exactTimeline.filter((event) => event.kind === "hit").forEach((event) => {
  exactJudgements.push(judgeRhythmPerformanceTap(event.targetMs, exactTimeline, exactJudgements, { bpm: 60, gradePreset: "middle_primary" }));
});
const exactSummary = evaluateRhythmAttempt(exactTimeline, exactJudgements, { bpm: 60, gradePreset: "middle_primary" });
assertEqual(exactSummary.result, "correct", "a complete exact performance passes");
assertEqual(exactSummary.score, 100, "a complete exact performance scores 100");
assertEqual(exactSummary.stability.status, "stable", "mixed subdivisions can still be rhythmically stable");

const adjustTimeline = buildRhythmPerformanceTimeline(["sixteenth_four", "sixteenth_four", "sixteenth_four", "quarter"], { bpm: 60, repeatCount: 1 });
const adjustJudgements: RhythmTapJudgement[] = [];
adjustTimeline.filter((event) => event.kind === "hit").forEach((event, index) => {
  if (index === 12) return;
  const tapMs = index >= 10 ? event.targetMs - 160 : event.targetMs;
  adjustJudgements.push(judgeRhythmPerformanceTap(tapMs, adjustTimeline, adjustJudgements, { bpm: 60, gradePreset: "middle_primary" }));
});
const adjustSummary = evaluateRhythmAttempt(adjustTimeline, adjustJudgements, { bpm: 60, gradePreset: "middle_primary" });
assertEqual(adjustSummary.correctCount, 10, "adjust case keeps ten exact attacks");
assertEqual(adjustSummary.earlyCount, 2, "adjust case records two early attacks");
assertEqual(adjustSummary.missedCount, 1, "adjust case records one missed attack");
assertEqual(adjustSummary.result, "adjust", "mostly matched performance gets formative adjustment feedback");

const record = buildRhythmWarmupAttemptRecord({
  gradePreset: "middle_primary",
  practiceMode: "play_along",
  bpm: 60,
  meter: "2/4",
  repeatCount: 1,
  patternIds: ["quarter", "eighth_pair", "rest", "quarter"],
  timeline,
  judgements,
});
assertEqual(record.version, "rhythm_warmup_attempt_v2", "attempt record exposes the upgraded contract version");
assertEqual(record.summary.result, "retry", "attempt record includes the final round result");
assertEqual(record.summary.expected_hit_count, 4, "attempt record exposes expected hit count");
