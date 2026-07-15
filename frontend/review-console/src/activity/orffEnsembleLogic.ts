export type OrffCriterionStatus = "unchecked" | "met" | "needs_work";

export type OrffPerformanceCriterion = {
  label: string;
  status: OrffCriterionStatus;
};

export type OrffGroupPerformanceRecord = {
  groupName: string;
  task: string;
  criteria: OrffPerformanceCriterion[];
  evidence: string;
};

export type OrffPerformanceJudge = {
  status: "needs_more_observation" | "needs_music_evidence" | "ready";
  feedback: string;
};

export type OrffPerformanceSummary = {
  version: "orff_group_performance_summary_v1";
  totalGroups: number;
  readyGroups: number;
  criteriaMetCounts: Record<string, number>;
  records: OrffGroupPerformanceRecord[];
  teacherNextStep: string;
};

export type OrffEntryCue = {
  groupName: string;
  task: string;
  barNumber: number;
  beatNumber: number;
  targetMs: number;
};

export type OrffEntryTimingStatus = "early" | "on_cue" | "late";

export type OrffEntryTimingResult = {
  status: OrffEntryTimingStatus;
  offsetMs: number;
  teacherSuggestion: string;
};

export type OrffEnsembleEventType = "entry" | "play";

export type OrffEnsembleEvent = {
  eventType: OrffEnsembleEventType;
  groupName: string;
  part: string;
  timestampMs: number;
  cue?: OrffEntryCue;
  entryResult?: OrffEntryTimingResult;
  rhythmStep?: number;
};

export type OrffPlaybackItem = OrffEnsembleEvent & {
  delayMs: number;
};

export type OrffEntryAttemptGroupSummary = {
  total: number;
  early: number;
  on_cue: number;
  late: number;
};

export type OrffEntryAttemptSummary = {
  version: "orff_entry_attempt_summary_v1";
  totalAttempts: number;
  byGroup: Record<string, OrffEntryAttemptGroupSummary>;
  teacherNextStep: string;
};

const DEFAULT_CRITERIA = ["节奏稳定", "按时进入", "能听同伴"];
const GENERIC_PRAISE_WORDS = ["好听", "喜欢", "很好", "不错", "开心", "有趣"];
const MUSIC_EVIDENCE_WORDS = ["节奏", "稳定", "进入", "声部", "同伴", "力度", "速度", "强弱", "合奏", "整齐", "休止"];

export function buildDefaultOrffGroupRecords(groupTasks: string[], criteria: string[] = DEFAULT_CRITERIA): OrffGroupPerformanceRecord[] {
  const tasks = groupTasks.length ? groupTasks : ["A组手鼓强拍", "B组木鱼稳定拍", "C组沙锤弱拍"];
  const rubric = normalizeCriteria(criteria);
  return tasks.map((task, index) => ({
    groupName: task.match(/^[A-ZＡ-Ｚ一二三四五六七八九十\d]+组/)?.[0] || `${index + 1}组`,
    task,
    criteria: rubric.map((label) => ({ label, status: "unchecked" })),
    evidence: "",
  }));
}

export function buildOrffEntryPlan(
  groupTasks: string[],
  options: { bpm?: number; meter?: string; entryEveryBars?: number } = {}
): OrffEntryCue[] {
  const tasks = groupTasks.length ? groupTasks : ["A组手鼓强拍", "B组木鱼稳定拍", "C组沙锤弱拍"];
  const bpm = normalizeBpm(options.bpm);
  const beatsPerBar = beatsPerBarFromMeter(options.meter);
  const entryEveryBars = Math.max(1, Math.round(Number(options.entryEveryBars || 1)));
  const beatMs = 60000 / bpm;
  const barMs = beatMs * beatsPerBar;
  return tasks.map((task, index) => ({
    groupName: task.match(/^[A-ZＡ-Ｚ一二三四五六七八九十\d]+组/)?.[0] || `${index + 1}组`,
    task,
    barNumber: index * entryEveryBars + 1,
    beatNumber: 1,
    targetMs: Math.round(index * entryEveryBars * barMs),
  }));
}

export function judgeOrffEntryTiming(cue: OrffEntryCue, performedAtMs: number, bpm = 88): OrffEntryTimingResult {
  const toleranceMs = Math.max(140, Math.round((60000 / normalizeBpm(bpm)) * 0.45));
  const offsetMs = Math.round(performedAtMs - cue.targetMs);
  if (offsetMs < -toleranceMs) {
    return {
      status: "early",
      offsetMs,
      teacherSuggestion: `${cue.groupName}进入偏早，要等到第 ${cue.barNumber} 小节第 ${cue.beatNumber} 拍再进。`,
    };
  }
  if (offsetMs > toleranceMs) {
    return {
      status: "late",
      offsetMs,
      teacherSuggestion: `${cue.groupName}进入偏晚，提前准备并看教师指挥。`,
    };
  }
  return {
    status: "on_cue",
    offsetMs,
    teacherSuggestion: `${cue.groupName}进入准时，可以继续和其他声部合奏。`,
  };
}

export function updateOrffCriterion(
  records: OrffGroupPerformanceRecord[],
  groupIndex: number,
  criterionLabel: string,
  status: OrffCriterionStatus
): OrffGroupPerformanceRecord[] {
  return records.map((record, index) => {
    if (index !== groupIndex) return record;
    return {
      ...record,
      criteria: record.criteria.map((criterion) => (
        criterion.label === criterionLabel ? { ...criterion, status } : criterion
      )),
    };
  });
}

export function updateOrffEvidence(records: OrffGroupPerformanceRecord[], groupIndex: number, evidence: string): OrffGroupPerformanceRecord[] {
  return records.map((record, index) => (index === groupIndex ? { ...record, evidence } : record));
}

export function judgeOrffPerformanceRecord(record: OrffGroupPerformanceRecord): OrffPerformanceJudge {
  if (!hasOrffMusicEvidence(record.evidence)) {
    return {
      status: "needs_music_evidence",
      feedback: `${record.groupName}还需要一句音乐依据，例如“节奏稳定、进入整齐、能听同伴声部”。`,
    };
  }
  const metCount = record.criteria.filter((criterion) => criterion.status === "met").length;
  if (metCount < Math.min(2, record.criteria.length)) {
    return {
      status: "needs_more_observation",
      feedback: `${record.groupName}至少记录两个音乐表现维度，再进入展示评价。`,
    };
  }
  return {
    status: "ready",
    feedback: `${record.groupName}可以记录：${record.evidence.trim()}`,
  };
}

export function summarizeOrffPerformance(records: OrffGroupPerformanceRecord[]): OrffPerformanceSummary {
  const criteriaMetCounts: Record<string, number> = {};
  for (const record of records) {
    for (const criterion of record.criteria) {
      if (!(criterion.label in criteriaMetCounts)) criteriaMetCounts[criterion.label] = 0;
      if (criterion.status === "met") criteriaMetCounts[criterion.label] += 1;
    }
  }
  const readyGroups = records.filter((record) => judgeOrffPerformanceRecord(record).status === "ready").length;
  const nextRecord = records.find((record) => judgeOrffPerformanceRecord(record).status !== "ready");
  return {
    version: "orff_group_performance_summary_v1",
    totalGroups: records.length,
    readyGroups,
    criteriaMetCounts,
    records,
    teacherNextStep: nextRecord
      ? `${nextRecord.groupName}继续观察：补充节奏、进入或倾听同伴的音乐依据。`
      : "所有小组都有音乐表现记录，可以进入全班展示或课后复盘。",
  };
}

export function buildOrffPerformanceExport(summary: OrffPerformanceSummary): string {
  return JSON.stringify({
    version: "orff_group_performance_record_v1",
    total_groups: summary.totalGroups,
    ready_groups: summary.readyGroups,
    criteria_met_counts: summary.criteriaMetCounts,
    teacher_next_step: summary.teacherNextStep,
    records: summary.records.map((record) => ({
      group_name: record.groupName,
      task: record.task,
      evidence: record.evidence,
      criteria: record.criteria,
      status: judgeOrffPerformanceRecord(record).status,
    })),
  }, null, 2);
}

export function recordOrffEnsembleEvent(
  events: OrffEnsembleEvent[],
  event: OrffEnsembleEvent
): OrffEnsembleEvent[] {
  const normalized: OrffEnsembleEvent = {
    ...event,
    groupName: event.groupName.trim() || "未命名小组",
    part: event.part.trim() || "percussion",
    timestampMs: Math.max(0, Math.round(Number(event.timestampMs) || 0)),
  };
  return [...events, normalized].sort((left, right) => left.timestampMs - right.timestampMs);
}

export function buildOrffPlaybackQueue(events: OrffEnsembleEvent[]): OrffPlaybackItem[] {
  const ordered = [...events].sort((left, right) => left.timestampMs - right.timestampMs);
  const startMs = ordered[0]?.timestampMs ?? 0;
  return ordered.map((event) => ({
    ...event,
    delayMs: Math.max(0, Math.round(event.timestampMs - startMs)),
  }));
}

export function summarizeOrffEntryAttempts(events: OrffEnsembleEvent[]): OrffEntryAttemptSummary {
  const entryEvents = events.filter((event) => event.eventType === "entry" && event.entryResult);
  const byGroup: Record<string, OrffEntryAttemptGroupSummary> = {};
  for (const event of entryEvents) {
    const groupName = event.groupName || "未命名小组";
    if (!byGroup[groupName]) {
      byGroup[groupName] = { total: 0, early: 0, on_cue: 0, late: 0 };
    }
    byGroup[groupName].total += 1;
    byGroup[groupName][event.entryResult!.status] += 1;
  }
  const nextGroup = Object.entries(byGroup).find(([, summary]) => summary.early > 0 || summary.late > 0)?.[0];
  return {
    version: "orff_entry_attempt_summary_v1",
    totalAttempts: entryEvents.length,
    byGroup,
    teacherNextStep: nextGroup
      ? `${nextGroup}需要再练进入时机：先听稳定拍，再看教师指挥。`
      : entryEvents.length
        ? "各组进入时机稳定，可以进入完整合奏回放和展示。"
        : "还没有记录声部进入，先开始计时并记录各组进入。",
  };
}

export function buildOrffSessionExport(events: OrffEnsembleEvent[], entrySummary = summarizeOrffEntryAttempts(events)): string {
  return JSON.stringify({
    version: "orff_ensemble_session_record_v1",
    events: events.map((event) => ({
      event_type: event.eventType,
      group_name: event.groupName,
      part: event.part,
      timestamp_ms: event.timestampMs,
      rhythm_step: event.rhythmStep,
      cue: event.cue
        ? {
            group_name: event.cue.groupName,
            bar_number: event.cue.barNumber,
            beat_number: event.cue.beatNumber,
            target_ms: event.cue.targetMs,
          }
        : undefined,
      entry_result: event.entryResult
        ? {
            status: event.entryResult.status,
            offset_ms: event.entryResult.offsetMs,
            teacher_suggestion: event.entryResult.teacherSuggestion,
          }
        : undefined,
    })),
    playback_queue: buildOrffPlaybackQueue(events).map((item) => ({
      event_type: item.eventType,
      group_name: item.groupName,
      part: item.part,
      delay_ms: item.delayMs,
    })),
    entry_attempt_summary: {
      version: entrySummary.version,
      total_attempts: entrySummary.totalAttempts,
      by_group: entrySummary.byGroup,
      teacher_next_step: entrySummary.teacherNextStep,
    },
  }, null, 2);
}

export function hasOrffMusicEvidence(evidence: string): boolean {
  const trimmed = evidence.trim();
  if (!trimmed) return false;
  const hasMusicWord = MUSIC_EVIDENCE_WORDS.some((word) => trimmed.includes(word));
  if (!hasMusicWord) return false;
  return !(GENERIC_PRAISE_WORDS.some((word) => trimmed.includes(word)) && !hasMusicWord);
}

function normalizeCriteria(criteria: string[]): string[] {
  const clean = criteria.map((item) => item.trim()).filter(Boolean);
  return clean.length ? clean : DEFAULT_CRITERIA;
}

function normalizeBpm(value: unknown): number {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return 88;
  return Math.max(56, Math.min(132, Math.round(parsed)));
}

function beatsPerBarFromMeter(meter: unknown): number {
  const text = String(meter || "2/4");
  const match = text.match(/^(\d+)\/\d+$/);
  const beats = match ? Number(match[1]) : 2;
  return Number.isFinite(beats) ? Math.max(2, Math.min(4, Math.round(beats))) : 2;
}
