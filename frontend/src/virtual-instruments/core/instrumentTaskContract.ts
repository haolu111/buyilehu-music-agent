import contractData from "../../../../contracts/music/teacher-constrained-instrument-task.v1.json";

export type InstrumentTaskKind =
  | "free_play"
  | "steady_beat"
  | "rhythm_echo"
  | "melody_sequence"
  | "ensemble_cue"
  | "constrained_composition";

export type InstrumentTaskContract = {
  version: "teacher_constrained_instrument_task_v1";
  taskKinds: InstrumentTaskKind[];
  gradePresets: Array<"lower_primary" | "middle_primary" | "upper_primary">;
  eventFields: Array<"timeMs" | "zoneId" | "midi">;
  timedEventStatuses: Array<"correct" | "early" | "late" | "extra" | "missed" | "rest_error">;
  compositionRuleFields: string[];
  restWindowDefinition: {
    field: "restWindowsBeats";
    appliesTo: "constrained_composition";
    item: "[startBeat, endBeat)";
    studentEventViolation: "rest_window_played:<index>";
    requiredRestCount: string;
  };
  evidenceStatuses: Array<"evidence_pass" | "adjust" | "participation_only">;
  evidenceBoundary: "objective_only";
  teacherOnlyJudgements: string[];
};

export const INSTRUMENT_TASK_CONTRACT = contractData as InstrumentTaskContract;
