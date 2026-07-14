import {
  buildLessonOpeningExport,
  buildLessonOpeningPlan,
  buildLessonOpeningSummary,
  evaluateLessonOpening
} from "../src/activity/lessonOpeningLogic";

function assertEqual<T>(actual: T, expected: T, label: string) {
  if (actual !== expected) {
    throw new Error(`${label}: expected ${String(expected)}, got ${String(actual)}`);
  }
}

const plan = buildLessonOpeningPlan({
  lessonTopic: "小雨沙沙",
  expressionTraits: ["欢快", "安静", "优美"],
  evidenceTerms: ["速度较快", "力度较弱", "旋律流畅"],
  openingQuestions: ["你听到的小雨像在做什么？", "音乐速度给你什么感觉？"],
});

assertEqual(plan.lessonTopic, "小雨沙沙", "lesson topic is kept");
assertEqual(plan.expressionTraits.length, 3, "expression traits are kept");
assertEqual(plan.openingQuestions[0], "你听到的小雨像在做什么？", "opening question is kept");

const beforeListening = evaluateLessonOpening(plan, {
  hasListened: false,
  selectedTrait: "欢快",
  selectedEvidence: ["速度较快"],
  selectedQuestion: "你听到的小雨像在做什么？",
});
assertEqual(beforeListening.status, "needs_listening", "opening must start from listening");

const noTrait = evaluateLessonOpening(plan, {
  hasListened: true,
  selectedTrait: "",
  selectedEvidence: ["速度较快"],
  selectedQuestion: "你听到的小雨像在做什么？",
});
assertEqual(noTrait.status, "needs_trait", "opening needs a student feeling");

const noEvidence = evaluateLessonOpening(plan, {
  hasListened: true,
  selectedTrait: "欢快",
  selectedEvidence: [],
  selectedQuestion: "你听到的小雨像在做什么？",
});
assertEqual(noEvidence.status, "needs_evidence", "opening needs music evidence");

const ready = evaluateLessonOpening(plan, {
  hasListened: true,
  selectedTrait: "欢快",
  selectedEvidence: ["速度较快"],
  selectedQuestion: "你听到的小雨像在做什么？",
});
assertEqual(ready.status, "ready", "opening is ready after listen, trait, evidence, question");
assertEqual(ready.teacherPrompt.includes("小雨沙沙"), true, "teacher prompt names lesson topic");

const summary = buildLessonOpeningSummary(plan, {
  hasListened: true,
  selectedTrait: "欢快",
  selectedEvidence: ["速度较快"],
  selectedQuestion: "你听到的小雨像在做什么？",
});
assertEqual(summary.version, "lesson_opening_summary_v1", "summary has stable version");
assertEqual(summary.readyForNextActivity, true, "ready summary can enter next activity");

const exported = JSON.parse(buildLessonOpeningExport(summary));
assertEqual(exported.version, "lesson_opening_record_v1", "export has stable version");
assertEqual(exported.lesson_topic, "小雨沙沙", "export keeps topic");
assertEqual(exported.ready_for_next_activity, true, "export keeps ready flag");
