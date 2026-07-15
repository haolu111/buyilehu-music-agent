export type SolfegeEchoPlanInput = {
  solfegeSet?: unknown;
  pitchMotion?: unknown;
  bpm?: unknown;
};

export type SolfegeEchoRound = {
  id: string;
  phrase: string[];
  teacherCue: string;
  studentCue: string;
  motionHint: string;
};

export type SolfegeEchoPlan = {
  allowedSolfege: string[];
  rounds: SolfegeEchoRound[];
  bpm: number;
};

const CLASSROOM_SOLFEGE = ["do", "re", "mi", "sol", "la"];
const PITCH_RANK: Record<string, number> = { do: 0, re: 1, mi: 2, fa: 3, sol: 4, la: 5, ti: 6 };

export function buildSolfegeEchoPlan(input: SolfegeEchoPlanInput): SolfegeEchoPlan {
  const allowedSolfege = normalizeSolfegeSet(input.solfegeSet);
  const phrases = normalizeEchoPhrases(input);
  const rounds = phrases.map((phrase, index) => ({
    id: `echo-${index + 1}`,
    phrase,
    teacherCue: `教师唱：${phrase.join(" ")}`,
    studentCue: `学生回声模唱：${phrase.join(" ")}`,
    motionHint: describePitchMotion(phrase)
  }));
  return {
    allowedSolfege,
    rounds: rounds.length ? rounds : defaultRounds(allowedSolfege),
    bpm: normalizeEchoBpm(input.bpm)
  };
}

export function normalizeEchoPhrases(input: SolfegeEchoPlanInput): string[][] {
  const allowed = normalizeSolfegeSet(input.solfegeSet);
  const source = Array.isArray(input.pitchMotion) && input.pitchMotion.length
    ? input.pitchMotion
    : [allowed.slice(0, 3), allowed.slice(2, 5)];
  return source
    .map((item) => normalizePhrase(item, allowed))
    .filter((phrase) => phrase.length >= 2)
    .slice(0, 6);
}

export function normalizeEchoBpm(value: unknown): number {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return 88;
  return Math.max(66, Math.min(104, Math.round(parsed)));
}

export function describePitchMotion(phrase: string[]): string {
  const ranks = phrase.map((token) => PITCH_RANK[token]).filter((rank): rank is number => typeof rank === "number");
  if (ranks.length < 2) return "听后判断高低";
  const steps = ranks.slice(1).map((rank, index) => rank - ranks[index]);
  const hasUp = steps.some((step) => step > 0);
  const hasDown = steps.some((step) => step < 0);
  if (hasUp && hasDown) return "有上有下";
  if (hasUp) return "上行";
  if (hasDown) return "下行";
  return "同音反复";
}

function normalizeSolfegeSet(value: unknown): string[] {
  const tokens = Array.isArray(value)
    ? value.map((item) => String(item).toLowerCase().trim())
    : [];
  const filtered = tokens.filter((token) => CLASSROOM_SOLFEGE.includes(token));
  return (filtered.length ? filtered : CLASSROOM_SOLFEGE).slice(0, 5);
}

function normalizePhrase(value: unknown, allowed: string[]): string[] {
  const raw = Array.isArray(value)
    ? value
    : String(value || "").split(/[\s,，、/-]+/);
  return raw
    .map((item) => String(item).toLowerCase().trim())
    .filter((token) => allowed.includes(token))
    .slice(0, 5);
}

function defaultRounds(allowed: string[]): SolfegeEchoRound[] {
  return [allowed.slice(0, 3), allowed.slice(Math.max(0, allowed.length - 3))]
    .filter((phrase) => phrase.length >= 2)
    .map((phrase, index) => ({
      id: `echo-${index + 1}`,
      phrase,
      teacherCue: `教师唱：${phrase.join(" ")}`,
      studentCue: `学生回声模唱：${phrase.join(" ")}`,
      motionHint: describePitchMotion(phrase)
    }));
}
