import {
  buildOrffEntryPlan,
  buildOrffPlaybackQueue,
  buildDefaultOrffGroupRecords,
  buildOrffSessionExport,
  summarizeOrffEntryAttempts,
  buildOrffPerformanceExport,
  judgeOrffPerformanceRecord,
  judgeOrffEntryTiming,
  recordOrffEnsembleEvent,
  summarizeOrffPerformance,
  updateOrffCriterion,
  updateOrffEvidence
} from "../src/activity/orffEnsembleLogic";

function assertEqual<T>(actual: T, expected: T, label: string) {
  if (actual !== expected) {
    throw new Error(`${label}: expected ${String(expected)}, got ${String(actual)}`);
  }
}

const records = buildDefaultOrffGroupRecords(
  ["A组手鼓强拍", "B组木鱼稳定拍", "C组沙锤弱拍"],
  ["节奏稳定", "按时进入", "能听同伴"]
);

assertEqual(records.length, 3, "one performance record is created for each group");
assertEqual(records[0].groupName, "A组", "group name is parsed from task");
assertEqual(records[0].criteria.length, 3, "criteria are attached to each record");
assertEqual(records[0].criteria[0].status, "unchecked", "criteria start unchecked");

const oneCriterion = updateOrffCriterion(records, 0, "节奏稳定", "met");
const oneCriterionWithEvidence = updateOrffEvidence(oneCriterion, 0, "节奏稳定，能听见共同稳定拍");
assertEqual(
  judgeOrffPerformanceRecord(oneCriterionWithEvidence[0]).status,
  "needs_more_observation",
  "one positive mark is not enough for ensemble record"
);

let readyRecords = updateOrffCriterion(oneCriterion, 0, "按时进入", "met");
readyRecords = updateOrffCriterion(readyRecords, 0, "能听同伴", "met");
readyRecords = updateOrffEvidence(readyRecords, 0, "节奏稳定，进入整齐，能听同伴声部");

const readyJudge = judgeOrffPerformanceRecord(readyRecords[0]);
assertEqual(readyJudge.status, "ready", "all criteria and music evidence make record ready");
assertEqual(readyJudge.feedback.includes("可以记录"), true, "ready feedback is teacher-facing");

const weakEvidence = updateOrffEvidence(readyRecords, 1, "很好，我喜欢");
assertEqual(
  judgeOrffPerformanceRecord(weakEvidence[1]).status,
  "needs_music_evidence",
  "generic praise is rejected for Orff performance record"
);

const summary = summarizeOrffPerformance(readyRecords);
assertEqual(summary.totalGroups, 3, "summary counts all groups");
assertEqual(summary.readyGroups, 1, "summary counts ready groups");
assertEqual(summary.criteriaMetCounts["节奏稳定"], 1, "summary counts met criteria");
assertEqual(summary.teacherNextStep.includes("B组"), true, "summary names next group needing observation");

const exported = JSON.parse(buildOrffPerformanceExport(summary));
assertEqual(exported.version, "orff_group_performance_record_v1", "export has stable version");
assertEqual(exported.total_groups, 3, "export keeps group total");
assertEqual(exported.ready_groups, 1, "export keeps ready group count");

const entryPlan = buildOrffEntryPlan(["A组手鼓强拍", "B组木鱼稳定拍", "C组沙锤弱拍"], {
  bpm: 120,
  meter: "2/4",
  entryEveryBars: 1
});
assertEqual(entryPlan.length, 3, "entry plan creates one cue per group");
assertEqual(entryPlan[0].targetMs, 0, "first group enters at the beginning");
assertEqual(entryPlan[1].targetMs, 1000, "second group enters after one 2/4 bar at 120 BPM");
assertEqual(entryPlan[2].barNumber, 3, "third group enters at bar three");

const earlyEntry = judgeOrffEntryTiming(entryPlan[1], 680, 120);
assertEqual(earlyEntry.status, "early", "entry before tolerance is early");
assertEqual(earlyEntry.teacherSuggestion.includes("等"), true, "early entry asks group to wait");

const onCueEntry = judgeOrffEntryTiming(entryPlan[1], 1080, 120);
assertEqual(onCueEntry.status, "on_cue", "entry inside tolerance is on cue");

const lateEntry = judgeOrffEntryTiming(entryPlan[1], 1360, 120);
assertEqual(lateEntry.status, "late", "entry after tolerance is late");
assertEqual(lateEntry.teacherSuggestion.includes("提前准备"), true, "late entry asks group to prepare earlier");

const emptySession = [];
const sessionWithEntry = recordOrffEnsembleEvent(emptySession, {
  eventType: "entry",
  groupName: "B组",
  part: "woodblock",
  timestampMs: 1080,
  cue: entryPlan[1],
  entryResult: onCueEntry,
});
const sessionWithPlay = recordOrffEnsembleEvent(sessionWithEntry, {
  eventType: "play",
  groupName: "B组",
  part: "woodblock",
  timestampMs: 1140,
  rhythmStep: 1,
});

assertEqual(sessionWithEntry.length, 1, "recording appends entry event");
assertEqual(emptySession.length, 0, "recording does not mutate prior events");
assertEqual(sessionWithPlay[1].eventType, "play", "recording appends play event");

const playbackQueue = buildOrffPlaybackQueue(sessionWithPlay);
assertEqual(playbackQueue.length, 2, "playback queue keeps recorded events");
assertEqual(playbackQueue[0].delayMs, 0, "first playback event starts at zero");
assertEqual(playbackQueue[1].delayMs, 60, "playback delay is relative to first event");

const entrySummary = summarizeOrffEntryAttempts([
  sessionWithEntry[0],
  recordOrffEnsembleEvent([], {
    eventType: "entry",
    groupName: "B组",
    part: "woodblock",
    timestampMs: 680,
    cue: entryPlan[1],
    entryResult: earlyEntry,
  })[0],
  recordOrffEnsembleEvent([], {
    eventType: "entry",
    groupName: "C组",
    part: "shaker",
    timestampMs: 1360,
    cue: entryPlan[2],
    entryResult: lateEntry,
  })[0],
]);

assertEqual(entrySummary.version, "orff_entry_attempt_summary_v1", "entry summary has stable version");
assertEqual(entrySummary.byGroup["B组"].on_cue, 1, "entry summary counts on-cue attempts");
assertEqual(entrySummary.byGroup["B组"].early, 1, "entry summary counts early attempts");
assertEqual(entrySummary.byGroup["C组"].late, 1, "entry summary counts late attempts");
assertEqual(entrySummary.teacherNextStep.includes("B组"), true, "entry summary names group needing next attention");

const sessionExport = JSON.parse(buildOrffSessionExport(sessionWithPlay, entrySummary));
assertEqual(sessionExport.version, "orff_ensemble_session_record_v1", "session export has stable version");
assertEqual(sessionExport.events.length, 2, "session export keeps events");
assertEqual(sessionExport.entry_attempt_summary.by_group["B组"].on_cue, 1, "session export includes entry summary");
