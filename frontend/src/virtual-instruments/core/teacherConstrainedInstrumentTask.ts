import { resolveGradeTimingWindows, type GradePreset } from "../../activity/rhythmWarmupLogic";
import { INSTRUMENT_TASK_CONTRACT, type InstrumentTaskKind } from "./instrumentTaskContract";

export type InstrumentPerformanceEvent = {
  timeMs: number;
  zoneId?: string;
  midi?: number;
  instrumentId?: string;
};

export type InstrumentTargetEvent = {
  id: string;
  offsetBeats: number;
  zoneId?: string;
  midi?: number;
};

export type CompositionRules = {
  allowedZoneIds?: string[];
  allowedMidi?: number[];
  requiredEventCount?: { min: number; max: number };
  endingMidi?: number;
  requiredBeats?: number;
  restWindowsBeats?: Array<[number, number]>;
  requiredRestCount?: { min: number; max: number };
};

export type TeacherConstrainedInstrumentTask = {
  version: "teacher_constrained_instrument_task_v1";
  id: string;
  kind: InstrumentTaskKind;
  instrumentId: string;
  gradePreset: GradePreset;
  bpm?: number;
  targetEvents?: InstrumentTargetEvent[];
  compositionRules?: CompositionRules;
};

export type InstrumentEventResult = {
  eventIndex: number;
  status: "correct" | "early" | "late" | "extra" | "rest_error";
  targetId?: string;
  offsetMs?: number;
};

export type InstrumentTaskEvidence = {
  version: "virtual_instrument_task_attempt_v1";
  taskId: string;
  kind: InstrumentTaskKind;
  evidenceStatus: "evidence_pass" | "adjust" | "participation_only";
  correctCount: number;
  earlyCount: number;
  lateCount: number;
  extraCount: number;
  missedCount: number;
  restErrorCount: number;
  participationCount: number;
  matchedTargetCount: number;
  missedTargetIds: string[];
  violations: string[];
  eventResults: InstrumentEventResult[];
};

export function validateInstrumentTask(task: TeacherConstrainedInstrumentTask): true {
  if (task.version !== INSTRUMENT_TASK_CONTRACT.version) throw new Error("Unsupported instrument task version");
  if (!INSTRUMENT_TASK_CONTRACT.taskKinds.includes(task.kind)) throw new Error(`Unsupported instrument task kind: ${task.kind}`);
  if (!task.id.trim() || !task.instrumentId.trim()) throw new Error("Instrument task id and instrumentId are required");
  if (!INSTRUMENT_TASK_CONTRACT.gradePresets.includes(task.gradePreset)) throw new Error("Instrument task gradePreset must be lower_primary, middle_primary, or upper_primary");
  if (task.bpm !== undefined && (!Number.isFinite(task.bpm) || task.bpm < 40 || task.bpm > 240)) throw new Error("Instrument task BPM must be between 40 and 240");
  if (isTimedTask(task.kind) && !task.targetEvents?.length) throw new Error(`${task.kind} requires targetEvents`);
  for (const target of task.targetEvents ?? []) {
    if (!target.id || !Number.isFinite(target.offsetBeats) || target.offsetBeats < 0) throw new Error("Every target event requires a non-negative beat offset");
    if (target.zoneId === undefined && target.midi === undefined) throw new Error("Every target event requires zoneId or midi");
    if (target.midi !== undefined && !Number.isFinite(target.midi)) throw new Error("Every target event MIDI must be finite");
  }
  validateCompositionMidiRules(task.compositionRules);
  validateCompositionRestRules(task.kind, task.compositionRules);
  return true;
}

export function evaluateInstrumentTask(task: TeacherConstrainedInstrumentTask, performanceEvents: InstrumentPerformanceEvent[]): InstrumentTaskEvidence {
  validateInstrumentTask(task);
  validateInstrumentPerformanceEvents(performanceEvents);
  const events = performanceEvents.map((event, index) => ({ ...event, index })).sort((left, right) => left.timeMs - right.timeMs || left.index - right.index);
  if (task.kind === "free_play") return participationEvidence(task, events.length);
  if (task.kind === "constrained_composition") return evaluateCompositionConstraints(task, events);
  return evaluateTimedInstrumentSequence(task, events);
}

export function evaluateTimedInstrumentSequence(
  task: TeacherConstrainedInstrumentTask,
  performanceEvents: Array<InstrumentPerformanceEvent & { index?: number }>,
): InstrumentTaskEvidence {
  const bpm = task.bpm ?? 100;
  const beatMs = 60000 / bpm;
  const windows = resolveGradeTimingWindows(bpm, task.gradePreset);
  const targets = task.targetEvents ?? [];
  const matched = new Set<number>();
  const eventResults: InstrumentEventResult[] = [];
  let correctCount = 0;
  let earlyCount = 0;
  let lateCount = 0;
  let extraCount = 0;

  performanceEvents.forEach((event, fallbackIndex) => {
    const candidates = targets
      .map((target, targetIndex) => ({ target, targetIndex, offsetMs: event.timeMs - target.offsetBeats * beatMs }))
      .filter(({ target, targetIndex, offsetMs }) => !matched.has(targetIndex) && matchesTarget(event, target) && Math.abs(offsetMs) <= windows.outerMs)
      .sort((left, right) => Math.abs(left.offsetMs) - Math.abs(right.offsetMs));
    const nearest = candidates[0];
    const eventIndex = event.index ?? fallbackIndex;
    if (!nearest) {
      extraCount += 1;
      eventResults.push({ eventIndex, status: "extra" });
      return;
    }
    matched.add(nearest.targetIndex);
    const status: InstrumentEventResult["status"] = Math.abs(nearest.offsetMs) <= windows.correctMs ? "correct" : nearest.offsetMs < 0 ? "early" : "late";
    if (status === "correct") correctCount += 1;
    if (status === "early") earlyCount += 1;
    if (status === "late") lateCount += 1;
    eventResults.push({ eventIndex, status, targetId: nearest.target.id, offsetMs: nearest.offsetMs });
  });

  const missedTargetIds = targets.filter((_, index) => !matched.has(index)).map((target) => target.id);
  const missedCount = missedTargetIds.length;
  return buildInstrumentPerformanceEvidence(task, {
    correctCount, earlyCount, lateCount, extraCount, missedCount, restErrorCount: 0,
    participationCount: performanceEvents.length, matchedTargetCount: matched.size,
    missedTargetIds, violations: [], eventResults,
  });
}

export function evaluateCompositionConstraints(
  task: TeacherConstrainedInstrumentTask,
  performanceEvents: Array<InstrumentPerformanceEvent & { index?: number }>,
): InstrumentTaskEvidence {
  const rules = task.compositionRules ?? {};
  const violations: string[] = [];
  const eventResults: InstrumentEventResult[] = [];
  let restErrorCount = 0;
  const beatMs = 60000 / (task.bpm ?? 100);
  for (const [fallbackIndex, event] of performanceEvents.entries()) {
    if (rules.allowedZoneIds?.length && (!event.zoneId || !rules.allowedZoneIds.includes(event.zoneId))) violations.push(`zone_not_allowed:${event.zoneId ?? "none"}`);
    if (rules.allowedMidi?.length && (event.midi === undefined || !rules.allowedMidi.includes(event.midi))) violations.push(`midi_not_allowed:${event.midi ?? "none"}`);
    const restWindowIndex = rules.restWindowsBeats?.findIndex(([startBeat, endBeat]) => {
      const eventBeat = event.timeMs / beatMs;
      return eventBeat >= startBeat && eventBeat < endBeat;
    }) ?? -1;
    if (restWindowIndex >= 0) {
      restErrorCount += 1;
      violations.push(`rest_window_played:${restWindowIndex}`);
      eventResults.push({ eventIndex: event.index ?? fallbackIndex, status: "rest_error" });
    }
  }
  if (rules.requiredEventCount && (performanceEvents.length < rules.requiredEventCount.min || performanceEvents.length > rules.requiredEventCount.max)) {
    violations.push(`event_count_required:${rules.requiredEventCount.min}-${rules.requiredEventCount.max}`);
  }
  const lastPerformanceEvent = performanceEvents[performanceEvents.length - 1];
  if (rules.endingMidi !== undefined && lastPerformanceEvent?.midi !== rules.endingMidi) violations.push(`ending_midi_required:${rules.endingMidi}`);
  if (rules.requiredBeats !== undefined && performanceEvents.length) {
    const lastBeat = lastPerformanceEvent!.timeMs / (60000 / (task.bpm ?? 100));
    if (lastBeat > rules.requiredBeats) violations.push(`duration_beats_exceeded:${rules.requiredBeats}`);
  }
  return buildInstrumentPerformanceEvidence(task, {
    correctCount: 0, earlyCount: 0, lateCount: 0, extraCount: 0, missedCount: 0, restErrorCount,
    participationCount: performanceEvents.length, matchedTargetCount: 0,
    missedTargetIds: [], violations, eventResults,
  });
}

export function buildInstrumentPerformanceEvidence(
  task: TeacherConstrainedInstrumentTask,
  counts: Omit<InstrumentTaskEvidence, "version" | "taskId" | "kind" | "evidenceStatus">,
): InstrumentTaskEvidence {
  const evidenceStatus = counts.violations.length || counts.earlyCount || counts.lateCount || counts.extraCount || counts.missedCount || counts.restErrorCount ? "adjust" : "evidence_pass";
  return { version: "virtual_instrument_task_attempt_v1", taskId: task.id, kind: task.kind, evidenceStatus, ...counts };
}

function participationEvidence(task: TeacherConstrainedInstrumentTask, participationCount: number): InstrumentTaskEvidence {
  return {
    version: "virtual_instrument_task_attempt_v1", taskId: task.id, kind: task.kind,
    evidenceStatus: "participation_only", correctCount: 0, earlyCount: 0, lateCount: 0, extraCount: 0, missedCount: 0, restErrorCount: 0,
    participationCount, matchedTargetCount: 0, missedTargetIds: [], violations: [], eventResults: [],
  };
}

function isTimedTask(kind: InstrumentTaskKind): boolean {
  return kind === "steady_beat" || kind === "rhythm_echo" || kind === "melody_sequence" || kind === "ensemble_cue";
}

function validateCompositionRestRules(kind: InstrumentTaskKind, rules: CompositionRules | undefined): void {
  const hasRestRule = rules !== undefined && (
    Object.prototype.hasOwnProperty.call(rules, "restWindowsBeats")
    || Object.prototype.hasOwnProperty.call(rules, "requiredRestCount")
  );
  if (hasRestRule && kind !== "constrained_composition") {
    throw new Error("restWindowsBeats and requiredRestCount are only supported by constrained_composition tasks");
  }
  const restWindows = rules?.restWindowsBeats;
  if (restWindows === undefined) return;
  for (const window of restWindows) {
    if (!Array.isArray(window) || window.length !== 2 || !Number.isFinite(window[0]) || !Number.isFinite(window[1]) || window[0] < 0 || window[1] <= window[0]) {
      throw new Error("Every rest window must be [startBeat, endBeat) with a non-negative start and later end");
    }
  }
  const requiredRestCount = rules?.requiredRestCount;
  if (requiredRestCount === undefined) return;
  if (!Number.isInteger(requiredRestCount.min) || !Number.isInteger(requiredRestCount.max) || requiredRestCount.min < 0 || requiredRestCount.max < requiredRestCount.min || restWindows.length < requiredRestCount.min || restWindows.length > requiredRestCount.max) {
    throw new Error("requiredRestCount must contain the supplied restWindowsBeats count");
  }
}

function validateCompositionMidiRules(rules: CompositionRules | undefined): void {
  if (rules?.allowedMidi?.some((midi) => !Number.isFinite(midi))) throw new Error("allowedMidi values must be finite");
  if (rules?.endingMidi !== undefined && !Number.isFinite(rules.endingMidi)) throw new Error("endingMidi must be finite");
}

function validateInstrumentPerformanceEvents(events: InstrumentPerformanceEvent[]): void {
  for (const event of events) {
    if (!Number.isFinite(event.timeMs) || event.timeMs < 0) throw new Error("Every student event requires a finite, non-negative timeMs");
    if (event.midi !== undefined && !Number.isFinite(event.midi)) throw new Error("Every student event MIDI must be finite");
  }
}

function matchesTarget(event: InstrumentPerformanceEvent, target: InstrumentTargetEvent): boolean {
  return (target.zoneId === undefined || target.zoneId === event.zoneId) && (target.midi === undefined || target.midi === event.midi);
}
