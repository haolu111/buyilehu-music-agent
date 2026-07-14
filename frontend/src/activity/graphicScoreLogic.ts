import { resolvePitchToken } from "../shared/pitchCatalog";
import { getRhythmPatternDefinition } from "../shared/rhythmPatternCatalog";

export type GraphicScoreElement = "pitch" | "duration" | "dynamics";
export type GraphicPitchLevel = "high" | "middle" | "low";
export type GraphicDuration = "short" | "long";
export type GraphicDynamics = "soft" | "medium" | "strong";
export type GraphicScoreMode = "graphic" | "mixed_cards";

export type GraphicSymbolInput = {
  symbol?: unknown;
  label?: unknown;
  pitch?: unknown;
  duration?: unknown;
  dynamics?: unknown;
};

export type GraphicScorePlanInput = {
  meter?: unknown;
  totalBeats?: unknown;
  symbolMeanings?: unknown;
  requiredElements?: unknown;
};

export type GraphicSymbolMeaning = {
  symbol: string;
  label: string;
  pitch: GraphicPitchLevel;
  duration: GraphicDuration;
  dynamics: GraphicDynamics;
};

export type GraphicScoreSlot = {
  beatIndex: number;
  symbol?: GraphicSymbolMeaning;
  rhythmId?: string;
  pitchId?: string;
};

export type GraphicScorePlan = {
  meter: "2/4" | "3/4" | "4/4";
  totalBeats: number;
  symbols: GraphicSymbolMeaning[];
  slots: GraphicScoreSlot[];
  requiredElements: GraphicScoreElement[];
};

export type GraphicScoreEvaluation = {
  status: "incomplete" | "needs_playback" | "ready";
  feedback: string;
};

export type GraphicScoreSummary = {
  version: "graphic_score_summary_v1";
  mode: GraphicScoreMode;
  orderedSymbols: string[];
  rhythmIds: string[];
  pitchIds: string[];
  usedPitchLevels: GraphicPitchLevel[];
  usedDurations: GraphicDuration[];
  usedDynamics: GraphicDynamics[];
  readyForPerformance: boolean;
  teacherNextStep: string;
  slots: GraphicScoreSlot[];
};

const DEFAULT_SYMBOLS: GraphicSymbolMeaning[] = [
  { symbol: "dot", label: "点", pitch: "high", duration: "short", dynamics: "soft" },
  { symbol: "line", label: "线", pitch: "middle", duration: "long", dynamics: "medium" },
  { symbol: "block", label: "块", pitch: "low", duration: "long", dynamics: "strong" },
];
const DEFAULT_REQUIRED: GraphicScoreElement[] = ["pitch", "duration", "dynamics"];

export function buildGraphicScorePlan(input: GraphicScorePlanInput): GraphicScorePlan {
  const totalBeats = clampInt(input.totalBeats, 2, 8, 4);
  const symbols = normalizeSymbols(input.symbolMeanings);
  return {
    meter: normalizeMeter(input.meter),
    totalBeats,
    symbols,
    slots: Array.from({ length: totalBeats }, (_, index) => ({ beatIndex: index + 1 })),
    requiredElements: normalizeRequiredElements(input.requiredElements),
  };
}

export function placeGraphicSymbol(
  slots: GraphicScoreSlot[],
  beatIndex: number,
  symbol: GraphicSymbolMeaning
): GraphicScoreSlot[] {
  const targetBeat = clampInt(beatIndex, 1, Math.max(1, slots.length), 1);
  return slots.map((slot) => slot.beatIndex === targetBeat ? { ...slot, symbol } : slot);
}

export function placeGraphicRhythmCard(
  slots: GraphicScoreSlot[],
  beatIndex: number,
  rhythmId: string
): GraphicScoreSlot[] {
  const targetBeat = clampInt(beatIndex, 1, Math.max(1, slots.length), 1);
  const canonicalId = getRhythmPatternDefinition(rhythmId).id;
  return slots.map((slot) => slot.beatIndex === targetBeat ? { ...slot, rhythmId: canonicalId } : slot);
}

export function placeGraphicPitchCard(
  slots: GraphicScoreSlot[],
  beatIndex: number,
  pitchId: string
): GraphicScoreSlot[] {
  const targetBeat = clampInt(beatIndex, 1, Math.max(1, slots.length), 1);
  const canonicalId = resolvePitchToken(pitchId)?.id;
  if (!canonicalId) return slots;
  return slots.map((slot) => slot.beatIndex === targetBeat ? { ...slot, pitchId: canonicalId } : slot);
}

export function buildGraphicScorePlaybackEvents(
  slots: GraphicScoreSlot[],
  bpm: number,
  mode: GraphicScoreMode = "graphic"
): Array<{ offset: number; start: number; duration: number }> {
  const beatSeconds = 60 / Math.max(40, Math.min(180, Number(bpm) || 88));
  return slots.flatMap((slot) => {
    const beatStart = (slot.beatIndex - 1) * beatSeconds;
    if (mode === "graphic") {
      if (!slot.symbol) return [];
      return [{ offset: graphicToneOffset(slot.symbol.pitch), start: beatStart, duration: Math.min(0.38, beatSeconds * 0.72) }];
    }

    const rhythm = getRhythmPatternDefinition(slot.rhythmId || "quarter");
    const pitchOffset = resolvePitchToken(slot.pitchId)?.semitone ?? 0;
    return rhythm.hitOffsetsBeats.map((hitOffset, index) => {
      const nextOffset = rhythm.hitOffsetsBeats[index + 1] ?? rhythm.durationBeats;
      const availableBeats = Math.max(0.125, nextOffset - hitOffset);
      return {
        offset: pitchOffset,
        start: beatStart + hitOffset * beatSeconds,
        duration: Math.min(0.38, availableBeats * beatSeconds * 0.78),
      };
    });
  });
}

export function evaluateGraphicScore(
  plan: GraphicScorePlan,
  slots: GraphicScoreSlot[],
  playedBack: boolean,
  mode: GraphicScoreMode = "graphic"
): GraphicScoreEvaluation {
  if (slots.some((slot) => !slot.symbol) || slots.length < plan.totalBeats) {
    return { status: "incomplete", feedback: "图形谱还没有放满，请按顺序放入点、线或块。" };
  }
  if (mode === "mixed_cards") {
    if (slots.some((slot) => !slot.rhythmId)) {
      return { status: "incomplete", feedback: "混合模式还没有为每一拍放入节奏卡。" };
    }
    if (slots.some((slot) => getRhythmPatternDefinition(slot.rhythmId || "quarter").hitOffsetsBeats.length > 0 && !slot.pitchId)) {
      return { status: "incomplete", feedback: "有声音的节奏卡还需要绑定唱名或音高卡。" };
    }
  }
  if (!playedBack) {
    return { status: "needs_playback", feedback: "先播放听一遍，再决定是否修改图形顺序。" };
  }
  const summary = buildGraphicScoreSummary(plan, slots, true, mode);
  if (plan.requiredElements.includes("pitch") && summary.usedPitchLevels.length < 2) {
    return { status: "incomplete", feedback: "图形还没有表现高低变化，请加入高、中、低的对比。" };
  }
  if (plan.requiredElements.includes("dynamics") && summary.usedDynamics.length < 2) {
    return { status: "incomplete", feedback: "图形还没有表现强弱变化，请加入轻、中、强的对比。" };
  }
  return { status: "ready", feedback: "图形谱能表现高低、长短和强弱，可以播放后展示。" };
}

export function buildGraphicScoreSummary(
  plan: GraphicScorePlan,
  slots: GraphicScoreSlot[],
  playedBack: boolean,
  mode: GraphicScoreMode = "graphic"
): GraphicScoreSummary {
  const filled = slots.filter((slot) => slot.symbol);
  const usedPitchLevels = unique(filled.map((slot) => slot.symbol?.pitch).filter(Boolean) as GraphicPitchLevel[]);
  const usedDurations = unique(filled.map((slot) => slot.symbol?.duration).filter(Boolean) as GraphicDuration[]);
  const usedDynamics = unique(filled.map((slot) => slot.symbol?.dynamics).filter(Boolean) as GraphicDynamics[]);
  const rhythmIds = slots.map((slot) => slot.rhythmId).filter(Boolean) as string[];
  const pitchIds = slots.map((slot) => slot.pitchId).filter(Boolean) as string[];
  const mixedCardsComplete = mode === "graphic" || slots.every((slot) => (
    Boolean(slot.rhythmId)
    && (getRhythmPatternDefinition(slot.rhythmId || "quarter").hitOffsetsBeats.length === 0 || Boolean(slot.pitchId))
  ));
  const readyForPerformance = evaluateReady(plan, slots, playedBack, usedPitchLevels, usedDynamics) && mixedCardsComplete;
  return {
    version: "graphic_score_summary_v1",
    mode,
    orderedSymbols: filled.map((slot) => slot.symbol?.symbol || ""),
    rhythmIds,
    pitchIds,
    usedPitchLevels,
    usedDurations,
    usedDynamics,
    readyForPerformance,
    teacherNextStep: readyForPerformance
      ? mode === "mixed_cards"
        ? "请学生按顺序播放作品，并说明节奏卡、唱名卡和图形分别决定了什么。"
        : "请学生按顺序播放图形谱，再说明哪几个图形表示高低、长短和强弱。"
      : "先补齐图形顺序，并至少形成一种高低或强弱对比。",
    slots,
  };
}

export function buildGraphicScoreExport(summary: GraphicScoreSummary): string {
  return JSON.stringify({
    version: "graphic_score_record_v1",
    mode: summary.mode,
    ordered_symbols: summary.orderedSymbols,
    rhythm_card_ids: summary.rhythmIds,
    pitch_card_ids: summary.pitchIds,
    used_pitch_levels: summary.usedPitchLevels,
    used_durations: summary.usedDurations,
    used_dynamics: summary.usedDynamics,
    ready_for_performance: summary.readyForPerformance,
    teacher_next_step: summary.teacherNextStep,
    slots: summary.slots.map((slot) => ({
      beat_index: slot.beatIndex,
      symbol: slot.symbol?.symbol,
      label: slot.symbol?.label,
      pitch: slot.symbol?.pitch,
      duration: slot.symbol?.duration,
      dynamics: slot.symbol?.dynamics,
      rhythm_id: slot.rhythmId,
      pitch_id: slot.pitchId,
    })),
  }, null, 2);
}

export function graphicToneOffset(pitch: string): number {
  if (pitch === "high") return 7;
  if (pitch === "low") return -5;
  return 0;
}

function evaluateReady(
  plan: GraphicScorePlan,
  slots: GraphicScoreSlot[],
  playedBack: boolean,
  usedPitchLevels: GraphicPitchLevel[],
  usedDynamics: GraphicDynamics[]
): boolean {
  if (!playedBack || slots.some((slot) => !slot.symbol) || slots.length < plan.totalBeats) return false;
  if (plan.requiredElements.includes("pitch") && usedPitchLevels.length < 2) return false;
  if (plan.requiredElements.includes("dynamics") && usedDynamics.length < 2) return false;
  return true;
}

function normalizeSymbols(value: unknown): GraphicSymbolMeaning[] {
  const raw = Array.isArray(value) && value.length ? value : DEFAULT_SYMBOLS;
  const symbols = raw.map((item, index) => {
    const source = item && typeof item === "object" ? item as GraphicSymbolInput : {};
    return {
      symbol: normalizeString(source.symbol) || DEFAULT_SYMBOLS[index % DEFAULT_SYMBOLS.length].symbol,
      label: normalizeString(source.label) || DEFAULT_SYMBOLS[index % DEFAULT_SYMBOLS.length].label,
      pitch: normalizePitch(source.pitch),
      duration: normalizeDuration(source.duration),
      dynamics: normalizeDynamics(source.dynamics),
    };
  });
  return symbols.slice(0, 6);
}

function normalizeRequiredElements(value: unknown): GraphicScoreElement[] {
  const allowed = new Set(DEFAULT_REQUIRED);
  const raw = Array.isArray(value) ? value.map(normalizeString) : DEFAULT_REQUIRED;
  const elements = raw.filter((item): item is GraphicScoreElement => allowed.has(item as GraphicScoreElement));
  return elements.length ? unique(elements) : DEFAULT_REQUIRED;
}

function normalizePitch(value: unknown): GraphicPitchLevel {
  const text = normalizeString(value);
  if (text === "high" || text === "low") return text;
  return "middle";
}

function normalizeDuration(value: unknown): GraphicDuration {
  return normalizeString(value) === "short" ? "short" : "long";
}

function normalizeDynamics(value: unknown): GraphicDynamics {
  const text = normalizeString(value);
  if (text === "soft" || text === "strong") return text;
  return "medium";
}

function normalizeMeter(value: unknown): "2/4" | "3/4" | "4/4" {
  const text = normalizeString(value);
  if (text === "3/4" || text === "4/4") return text;
  return "2/4";
}

function normalizeString(value: unknown): string {
  return String(value || "").trim();
}

function clampInt(value: unknown, min: number, max: number, fallback: number): number {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return fallback;
  return Math.max(min, Math.min(max, Math.round(parsed)));
}

function unique<T>(items: T[]): T[] {
  return Array.from(new Set(items));
}
