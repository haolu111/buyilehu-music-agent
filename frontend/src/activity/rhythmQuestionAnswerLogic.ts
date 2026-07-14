import { formalRhythmLabel } from "./rhythmNaming";

export type RhythmQuestionAnswerPlanInput = {
  meter?: unknown;
  bpm?: unknown;
  questionPattern?: unknown;
  answerPattern?: unknown;
};

export type RhythmQuestionAnswerPlan = {
  meter: "2/4" | "3/4" | "4/4";
  bpm: number;
  beatsPerBar: number;
  questionPattern: string[];
  answerPattern: string[];
};

export type RhythmAnswerSelection = {
  hasListenedQuestion: boolean;
  answerPattern: string[];
  tappedAnswerCount: number;
};

export type RhythmAnswerEvaluation = {
  status: "needs_question_listening" | "bar_incomplete" | "bar_overflow" | "needs_tap_back" | "ready";
  feedback: string;
};

export type RhythmQuestionAnswerSummary = {
  version: "rhythm_question_answer_summary_v1";
  meter: string;
  questionPattern: string[];
  answerPattern: string[];
  questionBeats: number;
  answerBeats: number;
  tappedAnswerCount: number;
  readyForGroupShare: boolean;
  teacherNextStep: string;
};

const DEFAULT_QUESTION = ["quarter", "eighth_pair"];
const DEFAULT_ANSWER = ["eighth_pair", "quarter"];
const RHYTHM_BEATS: Record<string, number> = {
  quarter: 1,
  quarter_2: 1,
  eighth_pair: 1,
  eighth_sixteenth: 1,
  eighth_sixteenth_sixteenth: 1,
  sixteenth_eighth: 1,
  sixteenth_sixteenth_eighth: 1,
  sixteenth_four: 1,
  sixteenth_run: 1,
  syncopation: 1,
  rest: 1,
  half: 2,
};

export function buildRhythmQuestionAnswerPlan(input: RhythmQuestionAnswerPlanInput): RhythmQuestionAnswerPlan {
  const meter = normalizeMeter(input.meter);
  const beatsPerBar = Number(meter.split("/")[0]) || 2;
  return {
    meter,
    bpm: clampNumber(input.bpm, 60, 132, 92),
    beatsPerBar,
    questionPattern: normalizePattern(input.questionPattern, DEFAULT_QUESTION),
    answerPattern: normalizePattern(input.answerPattern, DEFAULT_ANSWER),
  };
}

export function rhythmPatternBeats(pattern: string[]): number {
  return pattern.reduce((total, item) => total + (RHYTHM_BEATS[item] ?? 1), 0);
}

export function evaluateRhythmAnswer(
  plan: RhythmQuestionAnswerPlan,
  selection: RhythmAnswerSelection
): RhythmAnswerEvaluation {
  if (!selection.hasListenedQuestion) {
    return { status: "needs_question_listening", feedback: "先听教师节奏问句，再回拍答句。" };
  }
  const answerBeats = rhythmPatternBeats(selection.answerPattern);
  if (answerBeats < plan.beatsPerBar) {
    return { status: "bar_incomplete", feedback: "答句还没填满一个小节，请补足拍数。" };
  }
  if (answerBeats > plan.beatsPerBar) {
    return { status: "bar_overflow", feedback: "答句超过一个小节，请删掉多余节奏卡。" };
  }
  if (selection.tappedAnswerCount < selection.answerPattern.length) {
    return { status: "needs_tap_back", feedback: "答句已经排好，请用节奏垫回拍出来。" };
  }
  return { status: "ready", feedback: "节奏问答成立：问句和答句小节完整，可以小组接答。" };
}

export function buildRhythmQuestionAnswerSummary(
  plan: RhythmQuestionAnswerPlan,
  selection: RhythmAnswerSelection
): RhythmQuestionAnswerSummary {
  const evaluation = evaluateRhythmAnswer(plan, selection);
  return {
    version: "rhythm_question_answer_summary_v1",
    meter: plan.meter,
    questionPattern: plan.questionPattern,
    answerPattern: selection.answerPattern,
    questionBeats: rhythmPatternBeats(plan.questionPattern),
    answerBeats: rhythmPatternBeats(selection.answerPattern),
    tappedAnswerCount: selection.tappedAnswerCount,
    readyForGroupShare: evaluation.status === "ready",
    teacherNextStep: evaluation.status === "ready"
      ? "请 A 组拍问句，B 组拍答句，再交换角色。"
      : "先保证听问句、答句满小节、回拍稳定三步成立。",
  };
}

export function buildRhythmQuestionAnswerExport(summary: RhythmQuestionAnswerSummary): string {
  return JSON.stringify({
    version: "rhythm_question_answer_record_v1",
    meter: summary.meter,
    question_pattern: summary.questionPattern,
    answer_pattern: summary.answerPattern,
    question_beats: summary.questionBeats,
    answer_beats: summary.answerBeats,
    tapped_answer_count: summary.tappedAnswerCount,
    ready_for_group_share: summary.readyForGroupShare,
    teacher_next_step: summary.teacherNextStep,
  }, null, 2);
}

export function rhythmLabel(step: string): string {
  return formalRhythmLabel(step);
}

function normalizePattern(value: unknown, fallback: string[]): string[] {
  const raw = Array.isArray(value) ? value : fallback;
  const cleaned = raw.map((item) => String(item || "").trim()).filter(Boolean);
  return cleaned.length ? cleaned : fallback;
}

function normalizeMeter(value: unknown): "2/4" | "3/4" | "4/4" {
  const text = String(value || "").trim();
  if (text === "3/4" || text === "4/4") return text;
  return "2/4";
}

function clampNumber(value: unknown, min: number, max: number, fallback: number): number {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return fallback;
  return Math.max(min, Math.min(max, Math.round(parsed)));
}
