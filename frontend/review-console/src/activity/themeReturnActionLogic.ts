export type ThemeReturnWindowInput = {
  startSec?: unknown;
  endSec?: unknown;
  label?: unknown;
};

export type ThemeReturnPlanInput = {
  themeLabel?: unknown;
  themeWindows?: unknown;
  actionChoices?: unknown;
  correctAction?: unknown;
  evidenceTerms?: unknown;
  replayRequired?: unknown;
};

export type ThemeReturnWindow = {
  id: string;
  startSec: number;
  endSec: number;
  label: string;
};

export type ThemeReturnPlan = {
  themeLabel: string;
  themeWindows: ThemeReturnWindow[];
  actionChoices: string[];
  correctAction: string;
  evidenceTerms: string[];
  replayRequired: boolean;
};

export type ThemeReturnAttempt = {
  action: string;
  evidenceTerms: string[];
  heardTheme: boolean;
  timestampSec: number;
  status: ThemeReturnJudgement["status"];
  feedback: string;
};

export type ThemeReturnJudgement = {
  status: "needs_replay" | "early" | "late" | "wrong_action" | "needs_evidence" | "correct";
  feedback: string;
  matchedWindow?: ThemeReturnWindow;
};

export type ThemeReturnSummary = {
  version: "theme_return_action_summary_v1";
  themeLabel: string;
  attemptCount: number;
  correctCount: number;
  evidenceTerms: string[];
  readyForClassShare: boolean;
  teacherNextStep: string;
  attempts: ThemeReturnAttempt[];
};

const DEFAULT_ACTIONS = ["举主题卡", "画圆", "拍肩"];
const DEFAULT_EVIDENCE = ["旋律相同", "节奏相似", "力度变化"];

export function buildThemeReturnPlan(input: ThemeReturnPlanInput): ThemeReturnPlan {
  const actionChoices = normalizeStringList(input.actionChoices, DEFAULT_ACTIONS).slice(0, 4);
  const evidenceTerms = normalizeStringList(input.evidenceTerms, DEFAULT_EVIDENCE).slice(0, 5);
  const themeWindows = normalizeThemeWindows(input.themeWindows);
  const correctAction = normalizeString(input.correctAction) || actionChoices[0] || DEFAULT_ACTIONS[0];
  return {
    themeLabel: normalizeString(input.themeLabel) || "A 主题",
    themeWindows,
    actionChoices: actionChoices.includes(correctAction) ? actionChoices : [correctAction, ...actionChoices].slice(0, 4),
    correctAction,
    evidenceTerms,
    replayRequired: input.replayRequired === undefined ? true : Boolean(input.replayRequired),
  };
}

export function judgeThemeReturnAction(
  plan: ThemeReturnPlan,
  timestampSec: number,
  action: string,
  evidenceTerms: string[],
  heardTheme: boolean
): ThemeReturnJudgement {
  const time = clampNumber(timestampSec, 0, 600, 0);
  if (plan.replayRequired && !heardTheme) {
    return { status: "needs_replay", feedback: "先完整复听主题，再在主题出现时做动作。" };
  }
  const matchedWindow = plan.themeWindows.find((window) => time >= window.startSec && time <= window.endSec);
  if (!matchedWindow) {
    const nextWindow = plan.themeWindows.find((window) => time < window.startSec);
    if (nextWindow) {
      return { status: "early", feedback: "还没到主题再现，请继续听开头旋律是否回来。" };
    }
    return { status: "late", feedback: "主题已经过去，请回到主题出现的位置复听。" };
  }
  if (normalizeString(action) !== plan.correctAction) {
    return { status: "wrong_action", feedback: "动作和主题再现约定不一致，请看清主题动作卡。" , matchedWindow};
  }
  const cleanEvidence = evidenceTerms.map(normalizeString).filter((term) => plan.evidenceTerms.includes(term));
  if (!cleanEvidence.length) {
    return { status: "needs_evidence", feedback: "动作做对了，还要说出听到的音乐依据。" , matchedWindow};
  }
  return { status: "correct", feedback: "听到主题再现，并能用音乐依据说明。", matchedWindow };
}

export function recordThemeReturnAttempt(
  attempts: ThemeReturnAttempt[],
  attempt: {
    action?: unknown;
    evidenceTerms?: unknown;
    heardTheme?: unknown;
    timestampSec?: unknown;
  },
  plan: ThemeReturnPlan = buildThemeReturnPlan({})
): ThemeReturnAttempt[] {
  const action = normalizeString(attempt.action) || plan.actionChoices[0];
  const evidenceTerms = normalizeStringList(attempt.evidenceTerms, []);
  const heardTheme = Boolean(attempt.heardTheme);
  const timestampSec = clampNumber(attempt.timestampSec, 0, 600, 0);
  const judgement = judgeThemeReturnAction(plan, timestampSec, action, evidenceTerms, heardTheme);
  return [
    ...attempts,
    {
      action,
      evidenceTerms,
      heardTheme,
      timestampSec,
      status: judgement.status,
      feedback: judgement.feedback,
    },
  ].sort((left, right) => left.timestampSec - right.timestampSec);
}

export function buildThemeReturnSummary(plan: ThemeReturnPlan, attempts: ThemeReturnAttempt[]): ThemeReturnSummary {
  const correctCount = attempts.filter((attempt) => attempt.status === "correct").length;
  const evidenceTerms = Array.from(new Set(attempts.flatMap((attempt) => attempt.evidenceTerms))).filter((term) =>
    plan.evidenceTerms.includes(term)
  );
  const readyForClassShare = correctCount > 0 && evidenceTerms.length > 0;
  return {
    version: "theme_return_action_summary_v1",
    themeLabel: plan.themeLabel,
    attemptCount: attempts.length,
    correctCount,
    evidenceTerms,
    readyForClassShare,
    teacherNextStep: readyForClassShare
      ? "完整复听作品：请学生在每次主题回来时做动作，并说出旋律或节奏依据。"
      : "先听清主题样子，再缩短片段复听主题出现的位置。",
    attempts,
  };
}

export function buildThemeReturnRecordExport(summary: ThemeReturnSummary): string {
  return JSON.stringify({
    version: "theme_return_action_record_v1",
    theme_label: summary.themeLabel,
    attempt_count: summary.attemptCount,
    correct_count: summary.correctCount,
    evidence_terms: summary.evidenceTerms,
    ready_for_class_share: summary.readyForClassShare,
    teacher_next_step: summary.teacherNextStep,
    attempts: summary.attempts.map((attempt) => ({
      action: attempt.action,
      evidence_terms: attempt.evidenceTerms,
      heard_theme: attempt.heardTheme,
      timestamp_sec: attempt.timestampSec,
      status: attempt.status,
      feedback: attempt.feedback,
    })),
  }, null, 2);
}

function normalizeThemeWindows(value: unknown): ThemeReturnWindow[] {
  const raw = Array.isArray(value) ? value : [];
  const windows = raw
    .map((item, index) => {
      const source = (item && typeof item === "object") ? item as ThemeReturnWindowInput : {};
      const startSec = clampNumber(source.startSec, 0, 600, index * 16);
      const endSec = Math.max(startSec + 1, clampNumber(source.endSec, 0, 600, startSec + 6));
      return {
        id: `theme-window-${index + 1}`,
        startSec,
        endSec,
        label: normalizeString(source.label) || `主题第 ${index + 1} 次出现`,
      };
    })
    .filter((window) => window.endSec > window.startSec);
  return windows.length ? windows : [
    { id: "theme-window-1", startSec: 8, endSec: 14, label: "第一次出现" },
    { id: "theme-window-2", startSec: 32, endSec: 40, label: "主题再现" },
  ];
}

function normalizeStringList(value: unknown, fallback: string[]): string[] {
  const raw = Array.isArray(value) ? value : fallback;
  const list = raw.map(normalizeString).filter(Boolean);
  return list.length ? Array.from(new Set(list)) : fallback;
}

function normalizeString(value: unknown): string {
  return String(value || "").trim();
}

function clampNumber(value: unknown, min: number, max: number, fallback: number): number {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return fallback;
  return Math.max(min, Math.min(max, parsed));
}
