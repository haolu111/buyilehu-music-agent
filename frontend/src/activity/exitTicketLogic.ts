export type ExitTicketStatus = "needs_focus" | "needs_evidence" | "needs_reason" | "ready";

export type ExitTicketResult = {
  status: ExitTicketStatus;
  feedback: string;
};

export type ExitTicketSubmission = {
  focus: string;
  selectedEvidence: string;
  reason: string;
  submittedAt: string;
};

export type ExitTicketClassSummary = {
  version: "exit_ticket_class_summary_v1";
  total: number;
  focus: string;
  evidenceCounts: Record<string, number>;
  topEvidence: string;
  reviewSuggestion: string;
  submissions: ExitTicketSubmission[];
};

const GENERIC_WORDS = ["好听", "喜欢", "开心", "有趣", "很好", "不错"];

export function buildEvidenceTerms(criteria: string[], focus: string): string[] {
  const terms = new Set<string>();
  for (const item of [...criteria, focus]) {
    if (item.includes("节奏")) terms.add("节奏稳定");
    if (item.includes("拍") || item.includes("强弱")) terms.add("强弱拍清楚");
    if (item.includes("速度")) terms.add("速度变化");
    if (item.includes("力度")) terms.add("力度变化");
    if (item.includes("音色") || item.includes("乐器")) terms.add("音色特点");
    if (item.includes("曲式") || item.includes("重复") || item.includes("对比") || item.includes("再现")) terms.add("重复/对比");
    if (item.includes("旋律") || item.includes("音高") || item.includes("唱名")) terms.add("旋律走向");
    if (item.includes("合作") || item.includes("合奏")) terms.add("合作倾听");
  }
  if (!terms.size) {
    ["节奏稳定", "力度变化", "音色特点", "旋律走向"].forEach((term) => terms.add(term));
  }
  return Array.from(terms);
}

export function judgeExitTicket(input: {
  focus: string;
  selectedEvidence: string;
  reason: string;
}): ExitTicketResult {
  const focus = input.focus.trim();
  const evidence = input.selectedEvidence.trim();
  const reason = input.reason.trim();
  if (!focus) {
    return { status: "needs_focus", feedback: "出口票必须回到本课音乐目标。" };
  }
  if (!evidence) {
    return { status: "needs_evidence", feedback: "请选择一个音乐依据词，例如节奏、力度、音色或曲式。" };
  }
  if (reason.length < 6 || GENERIC_WORDS.some((word) => reason === word || reason.endsWith(word))) {
    return { status: "needs_reason", feedback: "请补一句具体理由，不只说喜欢或好听。" };
  }
  return {
    status: "ready",
    feedback: `出口票完成：你用“${evidence}”说明了“${focus}”。`,
  };
}

export function buildExitTicketSentence(focus: string, evidence: string, reason: string): string {
  return `今天我理解了${focus || "本课音乐要素"}，我的依据是${evidence || "____"}：${reason || "____"}。`;
}

export function summarizeExitTickets(submissions: ExitTicketSubmission[]): ExitTicketClassSummary {
  const cleanSubmissions = submissions
    .map((item) => ({
      focus: item.focus.trim(),
      selectedEvidence: item.selectedEvidence.trim(),
      reason: item.reason.trim(),
      submittedAt: item.submittedAt.trim(),
    }))
    .filter((item) => item.focus && item.selectedEvidence && item.reason);
  const evidenceCounts: Record<string, number> = {};
  for (const item of cleanSubmissions) {
    evidenceCounts[item.selectedEvidence] = (evidenceCounts[item.selectedEvidence] ?? 0) + 1;
  }
  const topEvidence = Object.entries(evidenceCounts).sort((left, right) => right[1] - left[1] || left[0].localeCompare(right[0]))[0]?.[0] ?? "";
  const focus = cleanSubmissions[0]?.focus ?? "本课音乐要素";
  return {
    version: "exit_ticket_class_summary_v1",
    total: cleanSubmissions.length,
    focus,
    evidenceCounts,
    topEvidence,
    reviewSuggestion: buildReviewSuggestion(cleanSubmissions.length, topEvidence, focus),
    submissions: cleanSubmissions,
  };
}

export function buildExitTicketExport(summary: ExitTicketClassSummary): string {
  return JSON.stringify(summary, null, 2);
}

function buildReviewSuggestion(total: number, topEvidence: string, focus: string): string {
  if (!total) return "还没有提交记录，先让学生完成一张出口票。";
  if (!topEvidence) return `下节课先复盘“${focus}”，请学生补充一个具体音乐依据。`;
  return `下节课可先围绕“${topEvidence}”复听或复唱，请学生说明它怎样证明“${focus}”。`;
}
