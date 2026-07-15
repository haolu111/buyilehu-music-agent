import { formalRhythmLabel } from "./rhythmNaming";

export type PentatonicMelodyPlanInput = {
  solfegeSet?: unknown;
  rhythmPattern?: unknown;
  meter?: unknown;
  compositionTotalBars?: unknown;
  bpm?: unknown;
};

export type PentatonicRhythmCard = {
  id: string;
  rhythm: string;
  label: string;
  beats: number;
};

export type PentatonicSlot = {
  id: string;
  beatIndex: number;
  rhythm: string;
  label: string;
};

export type PentatonicMelodyPlan = {
  allowedSolfege: string[];
  rhythmCards: PentatonicRhythmCard[];
  slots: PentatonicSlot[];
  meter: "2/4" | "3/4" | "4/4";
  compositionTotalBars: number;
  capacityBeats: number;
  bpm: number;
};

export type PentatonicEvaluation = {
  status: "incomplete" | "needs_audition" | "ready";
  message: string;
};

export type PentatonicCreationEventType = "place_note" | "undo_note" | "audition_phrase" | "teacher_confirm";

export type PentatonicCreationEvent = {
  eventType: PentatonicCreationEventType;
  note?: string;
  notes?: string[];
  slotIndex?: number;
  timestampMs: number;
};

export type PentatonicCreationSummary = {
  version: "pentatonic_creation_summary_v1";
  noteSequence: string;
  rhythmSequence: string;
  usedNotes: string[];
  revisionCount: number;
  auditionCount: number;
  readyForRelay: boolean;
  teacherNextStep: string;
  events: PentatonicCreationEvent[];
};

const CLASSROOM_PENTATONIC = ["do", "re", "mi", "sol", "la"];
const RHYTHM_BEATS: Record<string, number> = {
  quarter: 1,
  eighth_pair: 1,
  half: 2,
  rest: 1
};
export function buildPentatonicMelodyPlan(input: PentatonicMelodyPlanInput): PentatonicMelodyPlan {
  const meter = normalizeMeter(input.meter);
  const compositionTotalBars = clampInt(input.compositionTotalBars, 1, 4, 2);
  const capacityBeats = beatsPerBar(meter) * compositionTotalBars;
  const rhythmCards = normalizeRhythmPattern(input.rhythmPattern);
  const slots = rhythmCards.slice(0, capacityBeats).map((card, index) => ({
    id: `pentatonic-slot-${index + 1}`,
    beatIndex: index + 1,
    rhythm: card.rhythm,
    label: card.label
  }));
  return {
    allowedSolfege: normalizePentatonicSet(input.solfegeSet),
    rhythmCards,
    slots,
    meter,
    compositionTotalBars,
    capacityBeats,
    bpm: clampInt(input.bpm, 60, 104, 88)
  };
}

export function evaluatePentatonicMelody(plan: PentatonicMelodyPlan, placedNotes: string[], auditioned: boolean): PentatonicEvaluation {
  const validNotes = placedNotes.filter((note) => plan.allowedSolfege.includes(note));
  if (validNotes.length < plan.slots.length) {
    return { status: "incomplete", message: "还没有填满短句，请继续选择五声音级。" };
  }
  if (!auditioned) {
    return { status: "needs_audition", message: "先回放听一遍，再决定是否修改。" };
  }
  const uniqueNotes = new Set(validNotes);
  if (uniqueNotes.size < 3) {
    return { status: "incomplete", message: "至少使用 3 个不同五声音级，让短句更有旋律感。" };
  }
  return { status: "ready", message: "五声音级短句完成：可以说出用了哪些音和节奏。" };
}

export function noteOffsetForSolfege(solfege: string): number {
  const offsets: Record<string, number> = { do: 0, re: 2, mi: 4, sol: 7, la: 9 };
  return offsets[solfege] ?? 0;
}

export function recordPentatonicCreationEvent(
  events: PentatonicCreationEvent[],
  event: PentatonicCreationEvent
): PentatonicCreationEvent[] {
  const normalized: PentatonicCreationEvent = {
    ...event,
    note: event.note ? normalizeNote(event.note) : undefined,
    notes: event.notes?.map(normalizeNote).filter((note) => CLASSROOM_PENTATONIC.includes(note)),
    slotIndex: event.slotIndex === undefined ? undefined : Math.max(0, Math.round(Number(event.slotIndex) || 0)),
    timestampMs: Math.max(0, Math.round(Number(event.timestampMs) || 0)),
  };
  return [...events, normalized].sort((left, right) => left.timestampMs - right.timestampMs);
}

export function buildPentatonicCreationSummary(
  plan: PentatonicMelodyPlan,
  placedNotes: string[],
  events: PentatonicCreationEvent[],
  auditioned: boolean
): PentatonicCreationSummary {
  const cleanNotes = placedNotes.map(normalizeNote).filter((note) => plan.allowedSolfege.includes(note));
  const evaluation = evaluatePentatonicMelody(plan, cleanNotes, auditioned);
  const revisionCount = events.filter((event) => event.eventType === "undo_note").length;
  const auditionCount = events.filter((event) => event.eventType === "audition_phrase").length + (auditioned && !events.some((event) => event.eventType === "audition_phrase") ? 1 : 0);
  const readyForRelay = evaluation.status === "ready";
  return {
    version: "pentatonic_creation_summary_v1",
    noteSequence: cleanNotes.join(" "),
    rhythmSequence: plan.slots.map((slot) => slot.label).join(" "),
    usedNotes: Array.from(new Set(cleanNotes)),
    revisionCount,
    auditionCount,
    readyForRelay,
    teacherNextStep: readyForRelay
      ? "作品可以进入小组接龙：下一组保留结尾音，再改变一个节奏或一个音级。"
      : "先补齐五声音级短句，回放并修改后再进入小组接龙。",
    events,
  };
}

export function buildPentatonicCreationExport(summary: PentatonicCreationSummary): string {
  return JSON.stringify({
    version: "pentatonic_creation_record_v1",
    note_sequence: summary.noteSequence,
    rhythm_sequence: summary.rhythmSequence,
    used_notes: summary.usedNotes,
    revision_count: summary.revisionCount,
    audition_count: summary.auditionCount,
    ready_for_relay: summary.readyForRelay,
    teacher_next_step: summary.teacherNextStep,
    events: summary.events.map((event) => ({
      event_type: event.eventType,
      note: event.note,
      notes: event.notes,
      slot_index: event.slotIndex,
      timestamp_ms: event.timestampMs,
    })),
  }, null, 2);
}

function normalizeNote(note: string): string {
  return String(note || "").trim().toLowerCase();
}

function normalizePentatonicSet(value: unknown): string[] {
  const raw = Array.isArray(value) ? value.map((item) => String(item).toLowerCase().trim()) : [];
  const filtered = raw.filter((item) => CLASSROOM_PENTATONIC.includes(item));
  return filtered.length ? CLASSROOM_PENTATONIC.filter((note) => filtered.includes(note)) : CLASSROOM_PENTATONIC;
}

function normalizeRhythmPattern(value: unknown): PentatonicRhythmCard[] {
  const raw = Array.isArray(value) && value.length ? value : ["quarter", "quarter", "eighth_pair", "quarter"];
  return raw.slice(0, 8).map((item, index) => {
    const rhythm = String(item || "quarter");
    return {
      id: `pentatonic-rhythm-${index + 1}`,
      rhythm,
      label: formalRhythmLabel(rhythm),
      beats: RHYTHM_BEATS[rhythm] ?? 1
    };
  });
}

function normalizeMeter(value: unknown): "2/4" | "3/4" | "4/4" {
  const text = String(value || "");
  if (text === "3/4" || text === "4/4") return text;
  return "2/4";
}

function beatsPerBar(meter: "2/4" | "3/4" | "4/4"): number {
  return meter === "3/4" ? 3 : meter === "4/4" ? 4 : 2;
}

function clampInt(value: unknown, min: number, max: number, fallback: number): number {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return fallback;
  return Math.max(min, Math.min(max, Math.round(parsed)));
}
