export type PhrasePracticeVariant = "phrase_loop_singing" | "difficult_phrase_repair";

export type PhraseRepairPlanInput = {
  lyricsPhrases: string[];
  melodyPhrases?: string[];
  difficultPhrase?: string;
  breathPoints?: string[];
  bpm?: number;
};

export type PhraseRepairPlan = {
  variant: PhrasePracticeVariant;
  activeIndex: number;
  difficultPhrase: string;
  breathHints: string[];
  melodyHint: string;
  bpm: number;
  slowLoopLabel: string;
};

export function buildPhraseRepairPlan(input: PhraseRepairPlanInput): PhraseRepairPlan {
  const lyrics = input.lyricsPhrases.length ? input.lyricsPhrases : ["第一乐句"];
  const difficultPhrase = String(input.difficultPhrase || "").trim();
  const activeIndex = difficultPhrase
    ? Math.max(0, lyrics.findIndex((phrase) => phrase.includes(difficultPhrase) || difficultPhrase.includes(phrase)))
    : 0;
  const resolvedIndex = activeIndex >= 0 ? activeIndex : 0;
  const variant: PhrasePracticeVariant = difficultPhrase ? "difficult_phrase_repair" : "phrase_loop_singing";
  const bpm = normalizeSingingBpm(input.bpm);
  return {
    variant,
    activeIndex: resolvedIndex,
    difficultPhrase: difficultPhrase || lyrics[resolvedIndex] || lyrics[0],
    breathHints: (input.breathPoints || []).map(formatBreathPoint).filter(Boolean),
    melodyHint: input.melodyPhrases?.[resolvedIndex] || "",
    bpm,
    slowLoopLabel: `${variant === "difficult_phrase_repair" ? "慢速循环" : "循环"} ${bpm} BPM`,
  };
}

export function normalizeSingingBpm(value: unknown): number {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return 86;
  return Math.max(60, Math.min(108, Math.round(parsed)));
}

export function formatBreathPoint(value: string): string {
  return String(value || "")
    .replace(/\s*\/\s*/g, " / ")
    .trim();
}
