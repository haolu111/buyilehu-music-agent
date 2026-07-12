import { resolveGradeTimingWindows, type GradePreset } from "../../activity/rhythmWarmupLogic";
import type { PercussionGridTile } from "./percussionGrid";
import type { MetronomeConfig } from "./metronome";

export type ClassroomActivityMode = "free_play" | "steady_beat" | "echo" | "ensemble_cue";
export type ClassroomInstrumentActivityConfig = {
  mode: ClassroomActivityMode;
  target: { type: "instrument"; instrumentId: string } | { type: "percussion_grid"; tiles: PercussionGridTile[] };
  gradePreset: GradePreset;
  metronome: MetronomeConfig;
  patternIds?: string[];
  demoSequence?: Array<{ zoneId: string; beatOffset: number; durationBeats: number }>;
};
export type ClassroomPerformanceEvidence = {
  mode: ClassroomActivityMode;
  correctCount: number;
  earlyCount: number;
  lateCount: number;
  missedCount: number;
  extraCount: number;
  restErrorCount: number;
  stability: "stable" | "rushing" | "dragging" | "unstable";
  completed: boolean;
};
export type ClassroomActivityTap = { zoneId: string; elapsedMs: number; status?: "correct" | "early" | "late" | "extra" };
export type ClassroomActivitySession = { config: ClassroomInstrumentActivityConfig; taps: ClassroomActivityTap[]; matchedTargetIndexes: Set<number> };

export function validateClassroomActivityConfig(config: ClassroomInstrumentActivityConfig): true {
  if (!config.target) throw new Error("Activity target is required");
  if ((config.mode === "steady_beat" || config.mode === "echo" || config.mode === "ensemble_cue") && !config.demoSequence?.length) throw new Error(`${config.mode} requires a demo sequence`);
  return true;
}

export function createClassroomActivitySession(config: ClassroomInstrumentActivityConfig): ClassroomActivitySession {
  validateClassroomActivityConfig(config);
  return { config: structuredClone(config), taps: [], matchedTargetIndexes: new Set() };
}

export function recordClassroomActivityTap(session: ClassroomActivitySession, tap: Omit<ClassroomActivityTap, "status">): ClassroomActivityTap {
  if (session.config.mode === "free_play") {
    const recorded = { ...tap };
    session.taps.push(recorded);
    return recorded;
  }
  const beatMs = 60000 / session.config.metronome.bpm;
  const windows = resolveGradeTimingWindows(session.config.metronome.bpm, session.config.gradePreset);
  const candidates = (session.config.demoSequence ?? []).map((target, index) => ({ target, index, targetMs: target.beatOffset * beatMs }))
    .filter(({ target, index }) => !session.matchedTargetIndexes.has(index) && target.zoneId === tap.zoneId)
    .map((candidate) => ({ ...candidate, offset: tap.elapsedMs - candidate.targetMs }))
    .filter((candidate) => Math.abs(candidate.offset) <= windows.outerMs)
    .sort((a, b) => Math.abs(a.offset) - Math.abs(b.offset));
  const nearest = candidates[0];
  const status: NonNullable<ClassroomActivityTap["status"]> = !nearest ? "extra" : Math.abs(nearest.offset) <= windows.correctMs ? "correct" : nearest.offset < 0 ? "early" : "late";
  if (nearest) session.matchedTargetIndexes.add(nearest.index);
  const recorded = { ...tap, status };
  session.taps.push(recorded);
  return recorded;
}

function resolveStability(session: ClassroomActivitySession): ClassroomPerformanceEvidence["stability"] {
  const scored = session.taps.filter((tap) => tap.status && tap.status !== "extra");
  if (scored.length < 2) return "unstable";
  const offsets = scored.map((tap, index) => tap.elapsedMs - (session.config.demoSequence?.[index]?.beatOffset ?? 0) * 60000 / session.config.metronome.bpm);
  const average = offsets.reduce((sum, value) => sum + value, 0) / offsets.length;
  const spread = Math.max(...offsets) - Math.min(...offsets);
  if (spread <= 80 && Math.abs(average) <= 70) return "stable";
  if (average < -70) return "rushing";
  if (average > 70) return "dragging";
  return "unstable";
}

export function finishClassroomActivity(session: ClassroomActivitySession): ClassroomPerformanceEvidence {
  if (session.config.mode === "free_play") return { mode: "free_play", correctCount: 0, earlyCount: 0, lateCount: 0, missedCount: 0, extraCount: 0, restErrorCount: 0, stability: "unstable", completed: session.taps.length > 0 };
  const count = (status: ClassroomActivityTap["status"]) => session.taps.filter((tap) => tap.status === status).length;
  const expected = session.config.demoSequence?.length ?? 0;
  return {
    mode: session.config.mode,
    correctCount: count("correct"), earlyCount: count("early"), lateCount: count("late"),
    missedCount: Math.max(0, expected - session.matchedTargetIndexes.size), extraCount: count("extra"), restErrorCount: 0,
    stability: resolveStability(session), completed: expected > 0 && session.matchedTargetIndexes.size === expected,
  };
}
