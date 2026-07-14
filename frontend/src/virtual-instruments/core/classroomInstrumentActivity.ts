import type { GradePreset } from "../../activity/rhythmWarmupLogic";
import type { PercussionGridTile } from "./percussionGrid";
import type { MetronomeConfig } from "./metronome";
import {
  evaluateInstrumentTask,
  type InstrumentPerformanceEvent,
  type TeacherConstrainedInstrumentTask,
} from "./teacherConstrainedInstrumentTask";
import type { InstrumentTaskKind } from "./instrumentTaskContract";

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
  taskVersion: "teacher_constrained_instrument_task_v1";
  taskKind: InstrumentTaskKind;
  evidenceStatus: "evidence_pass" | "adjust" | "participation_only";
  correctCount: number;
  earlyCount: number;
  lateCount: number;
  missedCount: number;
  extraCount: number;
  restErrorCount: number;
  violations: string[];
  stability: "stable" | "rushing" | "dragging" | "unstable";
  completed: boolean;
};
export type ClassroomActivityTap = {
  zoneId: string;
  elapsedMs: number;
  midi?: number;
  instrumentId?: string;
  status?: "correct" | "early" | "late" | "extra" | "rest_error";
};
export type ClassroomActivitySession = {
  config: ClassroomInstrumentActivityConfig;
  taps: ClassroomActivityTap[];
  matchedTargetIndexes: Set<number>;
  task: TeacherConstrainedInstrumentTask;
  performanceEvents: InstrumentPerformanceEvent[];
};

export function validateClassroomActivityConfig(config: ClassroomInstrumentActivityConfig): true {
  if (!config.target) throw new Error("Activity target is required");
  if ((config.mode === "steady_beat" || config.mode === "echo" || config.mode === "ensemble_cue") && !config.demoSequence?.length) throw new Error(`${config.mode} requires a demo sequence`);
  return true;
}

export function createClassroomActivitySession(config: ClassroomInstrumentActivityConfig): ClassroomActivitySession {
  validateClassroomActivityConfig(config);
  const clonedConfig = structuredClone(config);
  return {
    config: clonedConfig,
    taps: [],
    matchedTargetIndexes: new Set(),
    task: buildLegacyInstrumentTask(clonedConfig),
    performanceEvents: [],
  };
}

export function recordClassroomActivityTap(session: ClassroomActivitySession, tap: Omit<ClassroomActivityTap, "status">): ClassroomActivityTap {
  const eventIndex = session.performanceEvents.length;
  session.performanceEvents.push({
    timeMs: tap.elapsedMs,
    zoneId: tap.zoneId,
    ...(tap.midi === undefined ? {} : { midi: tap.midi }),
    ...(tap.instrumentId === undefined ? {} : { instrumentId: tap.instrumentId }),
  });
  const taskEvidence = evaluateInstrumentTask(session.task, session.performanceEvents);
  session.matchedTargetIndexes.clear();
  for (const result of taskEvidence.eventResults) {
    if (!result.targetId) continue;
    const targetIndex = session.task.targetEvents?.findIndex((target) => target.id === result.targetId);
    if (targetIndex !== undefined && targetIndex >= 0) session.matchedTargetIndexes.add(targetIndex);
  }
  const status = taskEvidence.eventResults.find((result) => result.eventIndex === eventIndex)?.status;
  const recorded = status ? { ...tap, status } : { ...tap };
  session.taps.push(recorded);
  return recorded;
}

function resolveStability(session: ClassroomActivitySession): ClassroomPerformanceEvidence["stability"] {
  const scored = session.taps.filter((tap) => tap.status && tap.status !== "extra" && tap.status !== "rest_error");
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
  const taskEvidence = evaluateInstrumentTask(session.task, session.performanceEvents);
  const expected = session.task.targetEvents?.length ?? 0;
  return {
    mode: session.config.mode,
    taskVersion: session.task.version,
    taskKind: taskEvidence.kind,
    evidenceStatus: taskEvidence.evidenceStatus,
    correctCount: taskEvidence.correctCount,
    earlyCount: taskEvidence.earlyCount,
    lateCount: taskEvidence.lateCount,
    missedCount: taskEvidence.missedCount,
    extraCount: taskEvidence.extraCount,
    restErrorCount: taskEvidence.restErrorCount,
    violations: taskEvidence.violations,
    stability: resolveStability(session),
    completed: session.config.mode === "free_play"
      ? session.taps.length > 0
      : expected > 0 && taskEvidence.matchedTargetCount === expected,
  };
}

function buildLegacyInstrumentTask(config: ClassroomInstrumentActivityConfig): TeacherConstrainedInstrumentTask {
  const kindByMode: Record<ClassroomActivityMode, InstrumentTaskKind> = {
    free_play: "free_play",
    steady_beat: "steady_beat",
    echo: "rhythm_echo",
    ensemble_cue: "ensemble_cue",
  };
  const instrumentId = config.target.type === "instrument" ? config.target.instrumentId : "virtual_percussion_grid";
  return {
    version: "teacher_constrained_instrument_task_v1",
    id: `legacy_classroom_activity:${config.mode}:${instrumentId}`,
    kind: kindByMode[config.mode],
    instrumentId,
    gradePreset: config.gradePreset,
    bpm: config.metronome.bpm,
    targetEvents: config.demoSequence?.map((target, index) => ({
      id: `legacy_target_${index}`,
      offsetBeats: target.beatOffset,
      zoneId: target.zoneId,
    })),
  };
}
