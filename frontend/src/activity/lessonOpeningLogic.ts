export type LessonOpeningPlanInput = {
  lessonTopic?: unknown;
  expressionTraits?: unknown;
  evidenceTerms?: unknown;
  openingQuestions?: unknown;
};

export type LessonOpeningPlan = {
  lessonTopic: string;
  expressionTraits: string[];
  evidenceTerms: string[];
  openingQuestions: string[];
};

export type LessonOpeningSelection = {
  hasListened: boolean;
  selectedTrait: string;
  selectedEvidence: string[];
  selectedQuestion: string;
};

export type LessonOpeningEvaluation = {
  status: "needs_listening" | "needs_trait" | "needs_evidence" | "needs_question" | "ready";
  feedback: string;
  teacherPrompt: string;
};

export type LessonOpeningSummary = {
  version: "lesson_opening_summary_v1";
  lessonTopic: string;
  selectedTrait: string;
  selectedEvidence: string[];
  selectedQuestion: string;
  readyForNextActivity: boolean;
  teacherPrompt: string;
  teacherNextStep: string;
};

const DEFAULT_TRAITS = ["欢快", "安静", "优美"];
const DEFAULT_EVIDENCE = ["速度较快", "力度较弱", "旋律流畅"];

export function buildLessonOpeningPlan(input: LessonOpeningPlanInput): LessonOpeningPlan {
  const lessonTopic = normalizeString(input.lessonTopic) || "本课音乐";
  return {
    lessonTopic,
    expressionTraits: normalizeStringList(input.expressionTraits, DEFAULT_TRAITS).slice(0, 6),
    evidenceTerms: normalizeStringList(input.evidenceTerms, DEFAULT_EVIDENCE).slice(0, 6),
    openingQuestions: normalizeStringList(input.openingQuestions, [
      `你听到的${lessonTopic}像在发生什么？`,
      "音乐的速度或力度给你什么感觉？",
      "你想带着哪个问题继续听或学唱？",
    ]).slice(0, 4),
  };
}

export function evaluateLessonOpening(
  plan: LessonOpeningPlan,
  selection: LessonOpeningSelection
): LessonOpeningEvaluation {
  if (!selection.hasListened) {
    return {
      status: "needs_listening",
      feedback: "先完整听一小段音乐，再选择感受或图卡。",
      teacherPrompt: `请先播放${plan.lessonTopic}片段，让学生闭眼或看投屏安静听。`,
    };
  }
  if (!plan.expressionTraits.includes(selection.selectedTrait)) {
    return {
      status: "needs_trait",
      feedback: "请选择一个听到的情绪、画面或音乐形象。",
      teacherPrompt: `追问：你觉得${plan.lessonTopic}带给你什么感觉？`,
    };
  }
  const validEvidence = selection.selectedEvidence.filter((term) => plan.evidenceTerms.includes(term));
  if (!validEvidence.length) {
    return {
      status: "needs_evidence",
      feedback: "请补一个速度、力度、旋律或音色方面的音乐依据。",
      teacherPrompt: "追问：你是从速度、力度还是旋律听出来的？",
    };
  }
  if (!plan.openingQuestions.includes(selection.selectedQuestion)) {
    return {
      status: "needs_question",
      feedback: "请选择一个带着继续学习的问题。",
      teacherPrompt: "选择一个问题，把学生的回答接到下一环节。",
    };
  }
  return {
    status: "ready",
    feedback: "导入完成，可以带着这个问题进入下一环节。",
    teacherPrompt: `刚才我们听到${plan.lessonTopic}是${selection.selectedTrait}的，因为有${validEvidence.join("、")}。接下来带着“${selection.selectedQuestion}”继续学习。`,
  };
}

export function buildLessonOpeningSummary(
  plan: LessonOpeningPlan,
  selection: LessonOpeningSelection
): LessonOpeningSummary {
  const evaluation = evaluateLessonOpening(plan, selection);
  const selectedEvidence = selection.selectedEvidence.filter((term) => plan.evidenceTerms.includes(term));
  return {
    version: "lesson_opening_summary_v1",
    lessonTopic: plan.lessonTopic,
    selectedTrait: plan.expressionTraits.includes(selection.selectedTrait) ? selection.selectedTrait : "",
    selectedEvidence,
    selectedQuestion: plan.openingQuestions.includes(selection.selectedQuestion) ? selection.selectedQuestion : "",
    readyForNextActivity: evaluation.status === "ready",
    teacherPrompt: evaluation.teacherPrompt,
    teacherNextStep: evaluation.status === "ready"
      ? "根据这个感受和问题进入学唱、复听或节奏实践。"
      : "先补齐听、选、说依据三步，再进入正式活动。",
  };
}

export function buildLessonOpeningExport(summary: LessonOpeningSummary): string {
  return JSON.stringify({
    version: "lesson_opening_record_v1",
    lesson_topic: summary.lessonTopic,
    selected_trait: summary.selectedTrait,
    selected_evidence: summary.selectedEvidence,
    selected_question: summary.selectedQuestion,
    ready_for_next_activity: summary.readyForNextActivity,
    teacher_prompt: summary.teacherPrompt,
    teacher_next_step: summary.teacherNextStep,
  }, null, 2);
}

function normalizeStringList(value: unknown, fallback: string[]): string[] {
  const raw = Array.isArray(value) ? value : fallback;
  const list = raw.map(normalizeString).filter(Boolean);
  return list.length ? Array.from(new Set(list)) : fallback;
}

function normalizeString(value: unknown): string {
  return String(value || "").trim();
}
