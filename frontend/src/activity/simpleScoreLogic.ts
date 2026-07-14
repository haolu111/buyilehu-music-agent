import { formalRhythmLabel, formalRhythmName } from "./rhythmNaming";

export type SimpleScorePlanInput = {
  numberedScore?: unknown;
  rhythmPattern?: unknown;
  bpm?: unknown;
};

export type SimpleScoreLine = {
  id: string;
  score: string;
  solfege: string[];
  teacherCue: string;
  studentCue: string;
};

export type SimpleScoreRhythmCard = {
  id: string;
  rhythm: string;
  label: string;
  name: string;
};

export type SimpleScorePlan = {
  lines: SimpleScoreLine[];
  rhythmCards: SimpleScoreRhythmCard[];
  bpm: number;
};

const SCORE_TO_SOLFEGE: Record<string, string> = {
  "1": "do",
  "2": "re",
  "3": "mi",
  "4": "fa",
  "5": "sol",
  "6": "la",
  "7": "ti"
};

export function buildSimpleScorePlan(input: SimpleScorePlanInput): SimpleScorePlan {
  const scoreLines = normalizeScoreLines(input.numberedScore);
  return {
    lines: scoreLines.map((score, index) => ({
      id: `score-line-${index + 1}`,
      score,
      solfege: numberedScoreToSolfege(score),
      teacherCue: `先听第 ${index + 1} 行，再跟读简谱。`,
      studentCue: `学生跟读：${numberedScoreToSolfege(score).join(" ")}`
    })),
    rhythmCards: normalizeRhythmPattern(input.rhythmPattern).map((rhythm, index) => ({
      id: `score-rhythm-${index + 1}`,
      rhythm,
      label: rhythmLabelForScore(rhythm),
      name: rhythmNameForScore(rhythm)
    })),
    bpm: normalizeScoreBpm(input.bpm)
  };
}

export function numberedScoreToSolfege(line: string): string[] {
  const cleaned = String(line || "").replace(/[|｜，、/-]/g, " ");
  return cleaned
    .split(/\s+/)
    .map((token) => SCORE_TO_SOLFEGE[token])
    .filter((token): token is string => Boolean(token));
}

export function rhythmLabelForScore(rhythm: string): string {
  return formalRhythmLabel(rhythm);
}

export function rhythmNameForScore(rhythm: string): string {
  return formalRhythmName(rhythm);
}

function normalizeScoreLines(value: unknown): string[] {
  const raw = Array.isArray(value)
    ? value
    : String(value || "").split(/\n|；|;/);
  const lines = raw.map((item) => String(item).trim()).filter(Boolean).slice(0, 6);
  return lines.length ? lines : ["1 2 3", "3 5 6"];
}

function normalizeRhythmPattern(value: unknown): string[] {
  const raw = Array.isArray(value) ? value : [];
  const pattern = raw.map((item) => String(item).trim()).filter(Boolean).slice(0, 8);
  return pattern.length ? pattern : ["quarter", "quarter", "half"];
}

function normalizeScoreBpm(value: unknown): number {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return 84;
  return Math.max(60, Math.min(104, Math.round(parsed)));
}
