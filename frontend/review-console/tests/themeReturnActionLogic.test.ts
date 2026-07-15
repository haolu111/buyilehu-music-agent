import {
  buildThemeReturnPlan,
  buildThemeReturnRecordExport,
  buildThemeReturnSummary,
  judgeThemeReturnAction,
  recordThemeReturnAttempt
} from "../src/activity/themeReturnActionLogic";

function assertEqual<T>(actual: T, expected: T, label: string) {
  if (actual !== expected) {
    throw new Error(`${label}: expected ${String(expected)}, got ${String(actual)}`);
  }
}

function assertDeepEqual<T>(actual: T, expected: T, label: string) {
  const actualText = JSON.stringify(actual);
  const expectedText = JSON.stringify(expected);
  if (actualText !== expectedText) {
    throw new Error(`${label}: expected ${expectedText}, got ${actualText}`);
  }
}

const plan = buildThemeReturnPlan({
  themeLabel: "A 主题",
  themeWindows: [
    { startSec: 8, endSec: 14, label: "第一次出现" },
    { startSec: 34, endSec: 41, label: "主题再现" },
  ],
  actionChoices: ["举主题卡", "画圆", "拍肩"],
  correctAction: "举主题卡",
  evidenceTerms: ["旋律相同", "节奏相似", "力度变强"],
  replayRequired: true,
});

assertEqual(plan.themeLabel, "A 主题", "theme label is kept");
assertEqual(plan.themeWindows.length, 2, "plan keeps theme return windows");
assertDeepEqual(plan.actionChoices, ["举主题卡", "画圆", "拍肩"], "plan keeps classroom action choices");
assertEqual(plan.replayRequired, true, "theme return requires replay");

const tooEarly = judgeThemeReturnAction(plan, 6, "举主题卡", ["旋律相同"], true);
assertEqual(tooEarly.status, "early", "action before theme window is early");
assertEqual(tooEarly.feedback.includes("还没到主题"), true, "early feedback points back to listening");

const wrongAction = judgeThemeReturnAction(plan, 35, "拍肩", ["旋律相同"], true);
assertEqual(wrongAction.status, "wrong_action", "wrong action inside window is rejected");

const noEvidence = judgeThemeReturnAction(plan, 36, "举主题卡", [], true);
assertEqual(noEvidence.status, "needs_evidence", "theme return needs music evidence");

const ready = judgeThemeReturnAction(plan, 36, "举主题卡", ["旋律相同"], true);
assertEqual(ready.status, "correct", "correct action in return window passes");
assertEqual(ready.feedback.includes("主题再现"), true, "success feedback names theme return");

const firstAttempt = recordThemeReturnAttempt([], {
  action: "拍肩",
  evidenceTerms: ["旋律相同"],
  heardTheme: true,
  timestampSec: 35,
});
const secondAttempt = recordThemeReturnAttempt(firstAttempt, {
  action: "举主题卡",
  evidenceTerms: ["旋律相同", "节奏相似"],
  heardTheme: true,
  timestampSec: 36,
});

assertEqual(firstAttempt.length, 1, "attempt recording appends first item");
assertEqual(secondAttempt.length, 2, "attempt recording appends second item");

const summary = buildThemeReturnSummary(plan, secondAttempt);
assertEqual(summary.version, "theme_return_action_summary_v1", "summary has stable version");
assertEqual(summary.correctCount, 1, "summary counts correct return actions");
assertEqual(summary.readyForClassShare, true, "correct return with evidence is ready to share");
assertEqual(summary.teacherNextStep.includes("完整复听"), true, "summary gives teacher a replay next step");

const exported = JSON.parse(buildThemeReturnRecordExport(summary));
assertEqual(exported.version, "theme_return_action_record_v1", "export has stable version");
assertEqual(exported.correct_count, 1, "export keeps correct count");
assertEqual(exported.attempts.length, 2, "export keeps attempts");
