export type CompositionPuzzleMode = "rhythm_puzzle_composition" | "melody_puzzle_creation" | "melody_rhythm_puzzle";
export type CompositionMeter = "2/4" | "3/4" | "4/4";
export type CompositionScaleType = "major" | "minor" | "major_pentatonic";

export type CompositionRhythmCard = {
  id: string;
  label: string;
  beats?: number;
  kind?: string;
};

export type CompositionPlacedCard = {
  id: string;
  label: string;
  rhythm?: string;
  pitch?: string;
  attackCount?: number;
  pitches?: string[];
  selectedAttackIndex?: number;
  beats: number;
};

export type CompositionConstraintCheck = {
  id: string;
  label: string;
  passed: boolean;
  kind?: "pitch_token" | "rhythm_token" | "generic" | "filled_phrase" | "auditioned" | "rhythm_variety" | "pitch_count" | "cadence";
  target?: string;
  required?: boolean;
  status?: string;
};

export type CompositionPuzzleLogicConfig = {
  mode?: CompositionPuzzleMode;
  phrase_length_bars?: number;
  composition_total_bars?: number;
  composition_segment_bars?: number;
  composition_segments?: number;
  length_clamped?: boolean;
  total_slots?: number;
  segment_slots?: number;
  slots_per_bar?: number;
  meter_options?: CompositionMeter[];
  selected_meter?: CompositionMeter;
  tonic_options?: string[];
  selected_tonic?: string;
  scale_options?: CompositionScaleType[];
  selected_scale_type?: CompositionScaleType;
  playback_tonic?: string;
  constraint_profile?: "guided" | "balanced" | "challenge";
  rhythm_cards?: Array<string | CompositionRhythmCard>;
  melody_cards?: string[];
  required_elements?: string[];
  teacher_confirm_required?: boolean;
  constraint_checks?: CompositionConstraintCheck[];
};

export function buildCompositionPuzzleLogicConfig(raw: Record<string, unknown>): Required<CompositionPuzzleLogicConfig> {
  const nested = isRecord(raw.scene_config) ? raw.scene_config : {};
  const merged = { ...raw, ...nested };
  const selectedMeter = normalizeMeter(merged.selected_meter ?? merged.meter);
  const selectedTonic = normalizeTonic(merged.selected_tonic ?? merged.tonic);
  const selectedScaleType = normalizeScaleType(merged.selected_scale_type ?? merged.scale_type);
  const rawTotalBars = Number(merged.composition_total_bars ?? merged.phrase_length_bars);
  const compositionTotalBars = clampNumber(rawTotalBars, 1, 32, 2);
  const rawSegmentBars = Number(merged.composition_segment_bars ?? merged.phrase_length_bars);
  const compositionSegmentBars = clampNumber(rawSegmentBars, 1, Math.min(4, compositionTotalBars), Math.min(4, compositionTotalBars));
  const slotsPerBar = slotsPerBarForMeter(selectedMeter);
  return {
    mode: normalizeMode(merged.mode),
    phrase_length_bars: compositionSegmentBars,
    composition_total_bars: compositionTotalBars,
    composition_segment_bars: compositionSegmentBars,
    composition_segments: Math.max(1, Math.ceil(compositionTotalBars / compositionSegmentBars)),
    length_clamped: Boolean(merged.length_clamped),
    total_slots: compositionTotalBars * slotsPerBar,
    segment_slots: compositionSegmentBars * slotsPerBar,
    slots_per_bar: slotsPerBar,
    meter_options: normalizeMeterOptions(merged.meter_options),
    selected_meter: selectedMeter,
    tonic_options: normalizeTonicOptions(merged.tonic_options),
    selected_tonic: selectedTonic,
    scale_options: normalizeScaleOptions(merged.scale_options),
    selected_scale_type: selectedScaleType,
    playback_tonic: normalizeTonic(merged.playback_tonic ?? selectedTonic),
    constraint_profile: normalizeConstraintProfile(merged.constraint_profile),
    rhythm_cards: normalizeRhythmCards(merged.rhythm_cards),
    melody_cards: Array.isArray(merged.melody_cards) && merged.melody_cards.length
      ? normalizeMelodyCards(merged.melody_cards)
      : generateScaleNoteNames(selectedTonic, selectedScaleType),
    required_elements: normalizeRequiredElements(merged.required_elements),
    teacher_confirm_required: merged.teacher_confirm_required !== false,
    constraint_checks: normalizeConstraintChecks(merged.constraint_checks, merged.required_elements) || []
  };
}

export function normalizeMode(value: unknown): CompositionPuzzleMode {
  const mode = String(value || "");
  if (mode === "melody_puzzle_creation" || mode === "melody_rhythm_puzzle") return mode;
  return "rhythm_puzzle_composition";
}

export function normalizeConstraintProfile(value: unknown): "guided" | "balanced" | "challenge" {
  const profile = String(value || "");
  return profile === "balanced" || profile === "challenge" ? profile : "guided";
}

export function normalizeRhythmCards(value: unknown): Array<string | CompositionRhythmCard> {
  if (!Array.isArray(value) || !value.length) return ["quarter", "eighth_pair", "sixteenth_four", "eighth_sixteenth_sixteenth", "sixteenth_sixteenth_eighth", "rest"];
  return value.slice(0, 8).map((item) => isRecord(item) ? {
    id: String(item.id || item.label || "quarter"),
    label: String(item.label || item.id || "四分"),
    beats: Number(item.beats || 1),
    kind: String(item.kind || "hit")
  } : String(item));
}

export function normalizeMelodyCards(value: unknown): string[] {
  const allowed = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B", "C'"];
  const aliases: Record<string, string> = {
    do: "C",
    re: "D",
    mi: "E",
    fa: "F",
    sol: "G",
    la: "A",
    ti: "B",
    si: "B",
    do_high: "C'"
  };
  if (!Array.isArray(value)) return ["C", "D", "E", "G", "A"];
  const normalized = value.map((item) => aliases[String(item)] || String(item).toUpperCase().replace("C_HIGH", "C'"));
  const cards = allowed.filter((note) => normalized.includes(note));
  return cards.length >= 2 ? cards : ["C", "D", "E", "G", "A"];
}

export function normalizeMeter(value: unknown): CompositionMeter {
  const meter = String(value || "");
  return meter === "2/4" || meter === "3/4" || meter === "4/4" ? meter : "4/4";
}

export function slotsPerBarForMeter(meter: CompositionMeter): number {
  return meter === "2/4" ? 2 : meter === "3/4" ? 3 : 4;
}

export function normalizeMeterOptions(value: unknown): CompositionMeter[] {
  const options = Array.isArray(value) ? value.map(normalizeMeter) : ["2/4", "3/4", "4/4"];
  return unique(options).filter((meter): meter is CompositionMeter => meter === "2/4" || meter === "3/4" || meter === "4/4");
}

export function normalizeTonic(value: unknown): string {
  const normalized = String(value || "C").trim().replace("♯", "#").replace("♭", "b");
  const semitone = noteSemitone(normalized);
  return semitone === undefined ? "C" : noteNameFromSemitone(semitone);
}

export function normalizeTonicOptions(value: unknown): string[] {
  const options = Array.isArray(value) ? value.map(normalizeTonic) : ["C", "D", "E", "F", "G", "A"];
  const normalized = unique(options);
  return normalized.length ? normalized : ["C", "D", "E", "F", "G", "A"];
}

export function normalizeScaleType(value: unknown): CompositionScaleType {
  const scale = String(value || "");
  if (scale === "major" || scale === "minor" || scale === "major_pentatonic") return scale;
  return "major_pentatonic";
}

export function normalizeScaleOptions(value: unknown): CompositionScaleType[] {
  const options = Array.isArray(value) ? value.map(normalizeScaleType) : ["major", "minor", "major_pentatonic"];
  const normalized = unique(options).filter((scale): scale is CompositionScaleType => scale === "major" || scale === "minor" || scale === "major_pentatonic");
  return normalized.length ? normalized : ["major", "minor", "major_pentatonic"];
}

export function generateScaleNoteNames(tonic: string, scaleType: CompositionScaleType): string[] {
  const root = noteSemitone(tonic) ?? 0;
  const intervals = {
    major: [0, 2, 4, 5, 7, 9, 11, 12],
    minor: [0, 2, 3, 5, 7, 8, 10, 12],
    major_pentatonic: [0, 2, 4, 7, 9, 12]
  }[scaleType];
  return intervals.map((interval) => noteNameFromSemitone(root + interval));
}

export function transposeNoteName(note: string | undefined, fromTonic: string, toTonic: string): string | undefined {
  const semitone = noteSemitone(note);
  const from = noteSemitone(fromTonic) ?? 0;
  const to = noteSemitone(toTonic) ?? from;
  if (semitone === undefined) return note;
  return noteNameFromSemitone(semitone + to - from);
}

export function noteSemitone(note: string | undefined): number | undefined {
  const normalized = String(note || "").trim().replace("♯", "#").replace("♭", "b");
  const aliases: Record<string, string> = {
    do: "C",
    re: "D",
    mi: "E",
    fa: "F",
    sol: "G",
    la: "A",
    ti: "B",
    si: "B",
    do_high: "C'"
  };
  const target = aliases[normalized] || normalized;
  const octaveShift = target.endsWith("'") ? 12 : 0;
  const plain = target.replace(/'/g, "");
  const map: Record<string, number> = {
    C: 0,
    "C#": 1,
    Db: 1,
    D: 2,
    "D#": 3,
    Eb: 3,
    E: 4,
    F: 5,
    "F#": 6,
    Gb: 6,
    G: 7,
    "G#": 8,
    Ab: 8,
    A: 9,
    "A#": 10,
    Bb: 10,
    B: 11
  };
  const value = map[plain];
  return value === undefined ? undefined : value + octaveShift;
}

export function noteNameFromSemitone(value: number): string {
  const names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];
  const semitone = ((value % 12) + 12) % 12;
  return `${names[semitone]}${value >= 12 ? "'" : ""}`;
}

export function numberedNoteLabel(note: string | undefined, tonic = "C"): string {
  const semitone = noteSemitone(note);
  const tonicSemitone = noteSemitone(tonic) ?? 0;
  if (semitone === undefined) return String(note || "");
  const scaleDegreeBySemitone: Record<number, string> = {
    0: "1",
    2: "2",
    4: "3",
    5: "4",
    7: "5",
    9: "6",
    11: "7"
  };
  const relative = semitone - tonicSemitone;
  const degree = scaleDegreeBySemitone[((relative % 12) + 12) % 12];
  if (!degree) return String(note || "");
  return `${degree}${relative >= 12 ? "'" : ""}`;
}

export function normalizeRequiredElements(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  const seen = new Set<string>();
  return value
    .map(String)
    .map((item) => item.trim())
    .filter((item) => {
      if (!item || seen.has(item)) return false;
      seen.add(item);
      return true;
    })
    .slice(0, 8);
}

export function normalizeConstraintChecks(value: unknown, requiredElements: unknown): CompositionConstraintCheck[] | undefined {
  if (Array.isArray(value) && value.length) {
    return value.filter(isRecord).map((item) => ({
      id: String(item.id || item.label || "check"),
      label: String(item.label || item.id || "创编约束"),
      passed: Boolean(item.passed),
      kind: normalizeCheckKind(item.kind, String(item.label || item.id || "")),
      target: item.target === undefined ? undefined : String(item.target),
      required: item.required === undefined ? undefined : Boolean(item.required),
      status: item.status === undefined ? undefined : String(item.status)
    }));
  }
  const required = normalizeRequiredElements(requiredElements);
  const pitchTokens = new Set(["C", "D", "E", "F", "G", "A", "B", "C'", "do", "re", "mi", "fa", "sol", "la", "ti", "si", "do_high"]);
  return required.length
    ? required.map((label, index) => ({
        id: pitchTokens.has(label) ? `pitch_token_${label}` : `required_${index + 1}`,
        label: pitchTokens.has(label) ? `必须使用 ${numberedNoteLabel(label)}` : label,
        passed: false,
        kind: pitchTokens.has(label) ? "pitch_token" : inferGenericCheckKind(label),
        target: label,
        required: true,
        status: "pending"
      }))
    : undefined;
}

export function evaluateCompositionPuzzleChecks(
  config: CompositionPuzzleLogicConfig,
  placed: CompositionPlacedCard[],
  teacherConfirmed: boolean,
  auditioned = false
): CompositionConstraintCheck[] {
  const normalized = buildCompositionPuzzleLogicConfig(config as Record<string, unknown>);
  const slotCount = normalized.total_slots;
  const filled = compositionFilledSlots(placed) >= slotCount;
  const melodyFilled = normalized.mode === "rhythm_puzzle_composition" || compositionMelodyFilled(placed);
  const rhythmVariety = new Set(placed.map((item) => item.rhythm || item.id)).size >= (normalized.constraint_profile === "guided" ? 1 : 2);
  const pitches = compositionPitches(placed);
  const melodyVariety = normalized.mode === "rhythm_puzzle_composition" ? true : new Set(pitches).size >= 2;
  const teacher = !normalized.teacher_confirm_required || teacherConfirmed;
  const baseChecks: CompositionConstraintCheck[] = [
    { id: "filled", label: "完整作品已填满", passed: filled && melodyFilled },
    { id: "melody_filled", label: "音名（简谱）填入节奏格", passed: melodyFilled },
    { id: "rhythm_variety", label: "节奏材料成立", passed: rhythmVariety },
    { id: "melody_motion", label: "旋律有走向", passed: melodyVariety }
  ];
  const entityChecks = normalized.constraint_checks.map((check) => evaluateEntityCheck(check, placed, normalized, teacherConfirmed, auditioned));
  return [...baseChecks, ...entityChecks, { id: "teacher", label: "教师确认", passed: teacher }];
}

export function compositionFilledSlots(placed: CompositionPlacedCard[]): number {
  return placed.reduce((sum, item) => sum + Math.max(1, Math.round(Number(item.beats || 1))), 0);
}

export function rhythmAttackCount(id?: string): number {
  return rhythmPattern(id).filter((duration) => duration !== "rest").length;
}

export function compositionMelodySlotCount(placed: CompositionPlacedCard[]): number {
  return placed.reduce((sum, item) => sum + rhythmAttackCount(item.rhythm || item.id), 0);
}

export function compositionPitches(placed: CompositionPlacedCard[]): string[] {
  return placed.flatMap((item) => {
    if (Array.isArray(item.pitches)) return item.pitches.filter(Boolean);
    return item.pitch ? [item.pitch] : [];
  });
}

export function compositionMelodyFilled(placed: CompositionPlacedCard[]): boolean {
  return placed.every((item) => {
    const attackCount = rhythmAttackCount(item.rhythm || item.id);
    if (attackCount === 0) return !item.pitches?.length;
    return (item.pitches || []).filter(Boolean).length >= attackCount;
  });
}

export function rhythmPattern(id?: string): Array<"quarter" | "eighth" | "sixteenth" | "rest"> {
  if (id === "rest") return ["rest"];
  if (id === "eighth_pair") return ["eighth", "eighth"];
  if (id === "sixteenth_four") return ["sixteenth", "sixteenth", "sixteenth", "sixteenth"];
  if (id === "eighth_sixteenth" || id === "eighth_sixteenth_sixteenth") return ["eighth", "sixteenth", "sixteenth"];
  if (id === "sixteenth_eighth" || id === "sixteenth_sixteenth_eighth") return ["sixteenth", "sixteenth", "eighth"];
  if (id === "syncopation") return ["sixteenth", "eighth", "sixteenth"];
  if (id === "eighth_sixteenth_sixteenth_eighth") return ["eighth", "sixteenth", "sixteenth", "eighth"];
  return ["quarter"];
}

function normalizeCheckKind(value: unknown, label = ""): CompositionConstraintCheck["kind"] {
  const kind = String(value || "");
  if (
    kind === "pitch_token" ||
    kind === "rhythm_token" ||
    kind === "generic" ||
    kind === "filled_phrase" ||
    kind === "auditioned" ||
    kind === "rhythm_variety" ||
    kind === "pitch_count" ||
    kind === "cadence"
  ) {
    return kind;
  }
  return inferGenericCheckKind(label);
}

function inferGenericCheckKind(label: string): CompositionConstraintCheck["kind"] {
  if (/填满|完整|小节/.test(label)) return "filled_phrase";
  if (/试听|听后|提交/.test(label)) return "auditioned";
  if (/节奏材料|节奏种|2\s*种|两种/.test(label)) return "rhythm_variety";
  if (/音高|3\s*个音|三个音/.test(label)) return "pitch_count";
  if (/结束音|终止|回到\s*do|回到\s*la|回到\s*C|回到\s*A/.test(label)) return "cadence";
  return "generic";
}

function noteNameLabel(note: string) {
  return {
    do: "C",
    re: "D",
    mi: "E",
    fa: "F",
    sol: "G",
    la: "A",
    ti: "B",
    si: "B",
    do_high: "C'"
  }[note] || note;
}

function unique<T>(items: T[]): T[] {
  return Array.from(new Set(items));
}

function evaluateEntityCheck(
  check: CompositionConstraintCheck,
  placed: CompositionPlacedCard[],
  config: Required<CompositionPuzzleLogicConfig>,
  teacherConfirmed: boolean,
  auditioned: boolean
): CompositionConstraintCheck {
  const slotCount = config.total_slots;
  if (check.kind === "filled_phrase") {
    return { ...check, id: "required_filled_phrase", passed: compositionFilledSlots(placed) >= slotCount && compositionMelodyFilled(placed) };
  }
  if (check.kind === "auditioned") {
    return { ...check, id: "required_auditioned", passed: auditioned };
  }
  if (check.kind === "rhythm_variety") {
    return { ...check, id: "required_rhythm_variety", passed: new Set(placed.map((item) => item.rhythm || item.id)).size >= 2 };
  }
  if (check.kind === "pitch_count") {
    return { ...check, id: "required_pitch_count", passed: new Set(compositionPitches(placed)).size >= 3 };
  }
  if (check.kind === "cadence") {
    const pitches = compositionPitches(placed);
    const lastPitch = pitches[pitches.length - 1];
    return { ...check, id: "required_cadence", passed: lastPitch === "C" || lastPitch === "A" || lastPitch === "do" || lastPitch === "la" };
  }
  if (check.kind === "pitch_token" && check.target) {
    const target = noteNameLabel(check.target);
    const pitches = compositionPitches(placed);
    return { ...check, passed: pitches.some((pitch) => pitch === check.target || pitch === target) };
  }
  if (check.kind === "rhythm_token" && check.target) {
    return { ...check, passed: placed.some((item) => item.rhythm === check.target || item.id === check.target) };
  }
  if (check.target) {
    const pitches = compositionPitches(placed);
    return { ...check, passed: pitches.includes(check.target) || placed.some((item) => item.rhythm === check.target || item.id === check.target) };
  }
  if (/教师/.test(check.label)) {
    return { ...check, passed: teacherConfirmed };
  }
  return check;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function clampNumber(value: number, min: number, max: number, fallback: number) {
  if (!Number.isFinite(value)) return fallback;
  return Math.min(max, Math.max(min, Math.round(value)));
}
