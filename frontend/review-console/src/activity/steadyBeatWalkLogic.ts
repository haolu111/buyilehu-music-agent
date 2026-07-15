import { formalRhythmLabel } from "./rhythmNaming";

export type SteadyBeatWalkPlanInput = {
  meter?: unknown;
  bpm?: unknown;
  rhythmPattern?: unknown;
  movementActions?: unknown;
};

export type SteadyBeatStep = {
  id: string;
  index: number;
  rhythm: string;
  beatValue: number;
  label: string;
  expectedAction: string;
  isRest: boolean;
};

export type SteadyBeatWalkPlan = {
  meter: "2/4" | "3/4" | "4/4";
  bpm: number;
  beatsPerBar: number;
  beats: SteadyBeatStep[];
  movementActions: string[];
};

export type SteadyBeatWalkJudgement = {
  status: "correct" | "wrong_rest" | "wrong_action";
  step: SteadyBeatStep;
  chosenAction: string;
  feedback: string;
};

export type SteadyBeatWalkEvaluation = {
  status: "needs_listening" | "needs_more_movement" | "ready";
  judgements: SteadyBeatWalkJudgement[];
  correctCount: number;
  accuracy: number;
  teacherSuggestion: string;
};

export type SteadyBeatWalkSelection = {
  hasListenedBeat: boolean;
  judgements: SteadyBeatWalkJudgement[];
};

export type SteadyBeatWalkRecord = {
  version: "steady_beat_walk_record_v1";
  meter: string;
  bpm: number;
  totalAttempts: number;
  correctCount: number;
  accuracy: number;
  readyForClassWalk: boolean;
  teacherSuggestion: string;
};

const DEFAULT_PATTERN = ["quarter", "quarter", "rest", "quarter"];
const DEFAULT_ACTIONS = ["走一步", "拍手", "停住"];
const RHYTHM_BEATS: Record<string, number> = {
  quarter: 1,
  quarter_2: 1,
  eighth_pair: 1,
  rest: 1,
  half: 2,
};

export function buildSteadyBeatWalkPlan(input: SteadyBeatWalkPlanInput): SteadyBeatWalkPlan {
  const meter = normalizeMeter(input.meter);
  const beatsPerBar = Number(meter.split("/")[0]) || 2;
  const pattern = normalizeList(input.rhythmPattern, DEFAULT_PATTERN);
  const actions = normalizeList(input.movementActions, DEFAULT_ACTIONS);
  return {
    meter,
    bpm: clampNumber(input.bpm, 60, 132, 84),
    beatsPerBar,
    movementActions: actions,
    beats: pattern.map((rhythm, index) => {
      const isRest = rhythm === "rest";
      const expectedAction = isRest ? restAction(actions) : actions[index % Math.max(1, actions.length - 1)] || "走一步";
      return {
        id: `beat-${index + 1}`,
        index,
        rhythm,
        beatValue: RHYTHM_BEATS[rhythm] ?? 1,
        label: formalRhythmLabel(rhythm),
        expectedAction,
        isRest,
      };
    }),
  };
}

export function judgeSteadyBeatAction(step: SteadyBeatStep, chosenAction: string): SteadyBeatWalkJudgement {
  const normalized = chosenAction.trim();
  const correct = normalized === step.expectedAction;
  let status: SteadyBeatWalkJudgement["status"] = correct ? "correct" : "wrong_action";
  if (!correct && step.isRest) status = "wrong_rest";
  return {
    status,
    step,
    chosenAction: normalized,
    feedback: correct
      ? `${step.label} 落在稳定拍上：第 ${step.index + 1} 拍用“${step.expectedAction}”。`
      : step.isRest
        ? `休止要停住，刚才移动了。请把“休止”表现成安静。`
        : `这一拍要用“${step.expectedAction}”跟上稳定拍，再试一次。`,
  };
}

export function evaluateSteadyBeatWalk(
  plan: SteadyBeatWalkPlan,
  selection: SteadyBeatWalkSelection
): SteadyBeatWalkEvaluation {
  const total = selection.judgements.length;
  const correctCount = selection.judgements.filter((item) => item.status === "correct").length;
  const accuracy = total ? Math.round((correctCount / total) * 100) : 0;
  if (!selection.hasListenedBeat) {
    return {
      status: "needs_listening",
      judgements: selection.judgements,
      correctCount,
      accuracy,
      teacherSuggestion: "先完整听稳定拍，再开始走、拍、停。",
    };
  }
  if (total < Math.min(3, plan.beats.length)) {
    return {
      status: "needs_more_movement",
      judgements: selection.judgements,
      correctCount,
      accuracy,
      teacherSuggestion: "至少记录 3 次动作，观察学生是否能把身体落在拍点上。",
    };
  }
  return {
    status: "ready",
    judgements: selection.judgements,
    correctCount,
    accuracy,
    teacherSuggestion:
      accuracy >= 80
        ? "稳定拍行走已经成立，可以隐藏提示或改成围圈接力。"
        : "先放慢速度，保留拍点提示，特别练休止时停住。",
  };
}

export function buildSteadyBeatWalkRecord(
  plan: SteadyBeatWalkPlan,
  selection: SteadyBeatWalkSelection
): SteadyBeatWalkRecord {
  const evaluation = evaluateSteadyBeatWalk(plan, selection);
  return {
    version: "steady_beat_walk_record_v1",
    meter: plan.meter,
    bpm: plan.bpm,
    totalAttempts: selection.judgements.length,
    correctCount: evaluation.correctCount,
    accuracy: evaluation.accuracy,
    readyForClassWalk: evaluation.status === "ready" && evaluation.accuracy >= 60,
    teacherSuggestion: evaluation.teacherSuggestion,
  };
}

export function steadyBeatToneOffset(step: SteadyBeatStep): number {
  if (step.isRest) return -12;
  if (step.index % 2 === 0) return 7;
  return 0;
}

function normalizeList(value: unknown, fallback: string[]): string[] {
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

function restAction(actions: string[]): string {
  return actions.find((action) => action.includes("停")) || "停住";
}
