import {
  buildRhythmQuestionAnswerExport,
  buildRhythmQuestionAnswerPlan,
  buildRhythmQuestionAnswerSummary,
  evaluateRhythmAnswer,
  rhythmPatternBeats
} from "../src/activity/rhythmQuestionAnswerLogic";

function assertEqual<T>(actual: T, expected: T, label: string) {
  if (actual !== expected) {
    throw new Error(`${label}: expected ${String(expected)}, got ${String(actual)}`);
  }
}

const plan = buildRhythmQuestionAnswerPlan({
  meter: "2/4",
  bpm: 92,
  questionPattern: ["quarter", "eighth_pair"],
  answerPattern: ["eighth_pair", "quarter"],
});

assertEqual(plan.meter, "2/4", "meter is kept");
assertEqual(plan.questionPattern.length, 2, "question pattern is kept");
assertEqual(rhythmPatternBeats(plan.questionPattern), 2, "question fills one 2/4 bar");

const beforeListen = evaluateRhythmAnswer(plan, {
  hasListenedQuestion: false,
  answerPattern: plan.answerPattern,
  tappedAnswerCount: 2,
});
assertEqual(beforeListen.status, "needs_question_listening", "students must hear the question first");

const shortAnswer = evaluateRhythmAnswer(plan, {
  hasListenedQuestion: true,
  answerPattern: ["quarter"],
  tappedAnswerCount: 1,
});
assertEqual(shortAnswer.status, "bar_incomplete", "short answer is incomplete");

const notTapped = evaluateRhythmAnswer(plan, {
  hasListenedQuestion: true,
  answerPattern: plan.answerPattern,
  tappedAnswerCount: 0,
});
assertEqual(notTapped.status, "needs_tap_back", "answer must be performed");

const ready = evaluateRhythmAnswer(plan, {
  hasListenedQuestion: true,
  answerPattern: plan.answerPattern,
  tappedAnswerCount: 2,
});
assertEqual(ready.status, "ready", "complete listened and tapped answer is ready");
assertEqual(ready.feedback.includes("问答"), true, "ready feedback names call response");

const summary = buildRhythmQuestionAnswerSummary(plan, {
  hasListenedQuestion: true,
  answerPattern: plan.answerPattern,
  tappedAnswerCount: 2,
});
assertEqual(summary.version, "rhythm_question_answer_summary_v1", "summary has stable version");
assertEqual(summary.readyForGroupShare, true, "ready answer can be shared");

const exported = JSON.parse(buildRhythmQuestionAnswerExport(summary));
assertEqual(exported.version, "rhythm_question_answer_record_v1", "export has stable version");
assertEqual(exported.ready_for_group_share, true, "export keeps ready flag");
