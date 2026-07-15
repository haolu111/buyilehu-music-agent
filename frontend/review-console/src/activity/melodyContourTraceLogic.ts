export type MelodyContourDirection = "up" | "down" | "same";

export type MelodyContourPlanInput = {
  pitchMotion?: unknown;
  melodyPhrases?: unknown;
  bpm?: unknown;
};

export type MelodyContourStep = {
  id: string;
  index: number;
  direction: MelodyContourDirection;
  label: string;
  gesture: string;
  y: number;
};

export type MelodyContourTracePlan = {
  bpm: number;
  melodyPhrases: string[];
  steps: MelodyContourStep[];
};

export type MelodyContourJudgement = {
  status: "correct" | "wrong_direction";
  step: MelodyContourStep;
  chosenGesture: string;
  feedback: string;
};

export type MelodyContourSelection = {
  hasListenedMelody: boolean;
  judgements: MelodyContourJudgement[];
};

export type MelodyContourEvaluation = {
  status: "needs_listening" | "needs_more_trace" | "ready";
  judgements: MelodyContourJudgement[];
  correctCount: number;
  accuracy: number;
  teacherSuggestion: string;
};

export type MelodyContourRecord = {
  version: "melody_contour_trace_record_v1";
  melodyPhrases: string[];
  totalAttempts: number;
  correctCount: number;
  accuracy: number;
  readyForSingingTransfer: boolean;
  teacherSuggestion: string;
};

const DEFAULT_MOTION: MelodyContourDirection[] = ["up", "down", "same"];
const DEFAULT_MELODY = ["do re mi sol mi"];
const LABELS: Record<MelodyContourDirection, string> = {
  up: "上行",
  down: "下行",
  same: "平稳",
};
const GESTURES: Record<MelodyContourDirection, string> = {
  up: "手势向上",
  down: "手势向下",
  same: "手势平稳",
};

export function buildMelodyContourTracePlan(input: MelodyContourPlanInput): MelodyContourTracePlan {
  const directions = normalizeDirections(input.pitchMotion);
  let currentY = 50;
  const steps = directions.map((direction, index) => {
    if (direction === "up") currentY = Math.max(18, currentY - 16);
    if (direction === "down") currentY = Math.min(82, currentY + 16);
    return {
      id: `contour-${index + 1}`,
      index,
      direction,
      label: LABELS[direction],
      gesture: GESTURES[direction],
      y: currentY,
    };
  });
  return {
    bpm: clampNumber(input.bpm, 60, 120, 86),
    melodyPhrases: normalizeStringList(input.melodyPhrases, DEFAULT_MELODY),
    steps,
  };
}

export function judgeMelodyContourGesture(step: MelodyContourStep, chosenGesture: string): MelodyContourJudgement {
  const normalized = chosenGesture.trim();
  const correct = normalized === step.gesture;
  return {
    status: correct ? "correct" : "wrong_direction",
    step,
    chosenGesture: normalized,
    feedback: correct
      ? `${step.label}听出来了：这一段旋律用“${step.gesture}”跟踪。`
      : `这一段是${step.label}，请用“${step.gesture}”跟着旋律线走。`,
  };
}

export function evaluateMelodyContourTrace(
  plan: MelodyContourTracePlan,
  selection: MelodyContourSelection
): MelodyContourEvaluation {
  const total = selection.judgements.length;
  const correctCount = selection.judgements.filter((item) => item.status === "correct").length;
  const accuracy = total ? Math.round((correctCount / total) * 100) : 0;
  if (!selection.hasListenedMelody) {
    return {
      status: "needs_listening",
      judgements: selection.judgements,
      correctCount,
      accuracy,
      teacherSuggestion: "先听完整旋律短句，再看旋律线和做手势。",
    };
  }
  if (total < Math.min(3, plan.steps.length)) {
    return {
      status: "needs_more_trace",
      judgements: selection.judgements,
      correctCount,
      accuracy,
      teacherSuggestion: "至少跟踪 3 次旋律方向，观察学生是否真的听到高低变化。",
    };
  }
  return {
    status: "ready",
    judgements: selection.judgements,
    correctCount,
    accuracy,
    teacherSuggestion:
      accuracy >= 80
        ? "旋律线跟踪稳定了，请让学生用唱名或哼唱把短句唱回。"
        : "先放慢速度，保留上行、下行、平稳提示，再复听一次。",
  };
}

export function buildMelodyContourRecord(
  plan: MelodyContourTracePlan,
  selection: MelodyContourSelection
): MelodyContourRecord {
  const evaluation = evaluateMelodyContourTrace(plan, selection);
  return {
    version: "melody_contour_trace_record_v1",
    melodyPhrases: plan.melodyPhrases,
    totalAttempts: selection.judgements.length,
    correctCount: evaluation.correctCount,
    accuracy: evaluation.accuracy,
    readyForSingingTransfer: evaluation.status === "ready" && evaluation.accuracy >= 60,
    teacherSuggestion: evaluation.teacherSuggestion,
  };
}

export function contourToneOffsets(plan: MelodyContourTracePlan): number[] {
  let current = 0;
  return plan.steps.map((step) => {
    if (step.direction === "up") current += 2;
    if (step.direction === "down") current -= 2;
    return current;
  });
}

function normalizeDirections(value: unknown): MelodyContourDirection[] {
  const raw = Array.isArray(value) ? value : DEFAULT_MOTION;
  const mapped = raw
    .map((item) => normalizeDirection(String(item || "")))
    .filter((item): item is MelodyContourDirection => Boolean(item));
  return mapped.length ? mapped : DEFAULT_MOTION;
}

function normalizeDirection(text: string): MelodyContourDirection | "" {
  const normalized = text.trim().toLowerCase();
  if (["up", "上行", "向上", "升"].includes(normalized)) return "up";
  if (["down", "下行", "向下", "降"].includes(normalized)) return "down";
  if (["same", "flat", "level", "平稳", "保持", "同音"].includes(normalized)) return "same";
  return "";
}

function normalizeStringList(value: unknown, fallback: string[]): string[] {
  const raw = Array.isArray(value) ? value : fallback;
  const cleaned = raw.map((item) => String(item || "").trim()).filter(Boolean);
  return cleaned.length ? cleaned : fallback;
}

function clampNumber(value: unknown, min: number, max: number, fallback: number): number {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return fallback;
  return Math.max(min, Math.min(max, Math.round(parsed)));
}
