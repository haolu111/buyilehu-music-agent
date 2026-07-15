export const FORMAL_RHYTHM_LABELS: Record<string, string> = {
  quarter: "四",
  quarter_2: "四",
  eighth_pair: "二八",
  eighth_sixteenth: "八十六",
  eighth_sixteenth_sixteenth: "八十六",
  sixteenth_eighth: "十六八",
  sixteenth_sixteenth_eighth: "十六八",
  sixteenth_four: "四个十六",
  sixteenth_run: "四个十六",
  syncopation: "小切分",
  eighth_triplet: "三连音",
  dotted_quarter: "附点四分",
  half: "二分",
  dotted_half: "附点二分",
  rest: "休止",
  eighth_rest: "八分休止",
};

export const FORMAL_RHYTHM_NAMES: Record<string, string> = {
  quarter: "四分音符",
  quarter_2: "四分音符",
  eighth_pair: "二八节奏",
  eighth_sixteenth: "八十六节奏",
  eighth_sixteenth_sixteenth: "八十六节奏",
  sixteenth_eighth: "十六八节奏",
  sixteenth_sixteenth_eighth: "十六八节奏",
  sixteenth_four: "四个十六节奏",
  sixteenth_run: "四个十六节奏",
  syncopation: "小切分节奏",
  eighth_triplet: "八分音符三连音",
  dotted_quarter: "附点四分音符",
  half: "二分音符",
  dotted_half: "附点二分音符",
  rest: "四分休止",
  eighth_rest: "八分休止符",
};

export function formalRhythmLabel(rhythm: string): string {
  return FORMAL_RHYTHM_LABELS[rhythm] ?? rhythm;
}

export function formalRhythmName(rhythm: string): string {
  return FORMAL_RHYTHM_NAMES[rhythm] ?? "节奏";
}
