export type PeerFeedbackShowcase = {
  id: string;
  groupName: string;
  task: string;
  status: "waiting" | "active" | "reviewed";
  evidenceTerms: string[];
  suggestion: string;
};

export type PeerFeedbackEvaluation = {
  status: "needs_showcase" | "needs_evidence" | "needs_specific_suggestion" | "ready";
  reviewedCount: number;
  feedback: string;
  teacherSuggestion: string;
};

export type PeerFeedbackRecord = {
  version: "peer_feedback_record_v1";
  totalShowcases: number;
  reviewedCount: number;
  readyForTeacherSummary: boolean;
  entries: Array<{
    groupName: string;
    task: string;
    evidenceTerms: string[];
    suggestion: string;
  }>;
};

const GENERIC_WORDS = ["好听", "喜欢", "很好", "不错", "开心", "有趣", "厉害"];
const MUSIC_EVIDENCE_WORDS = [
  "节奏",
  "稳定",
  "休止",
  "停住",
  "强弱",
  "速度",
  "力度",
  "音色",
  "合拍",
  "进入",
  "同伴",
  "合作",
  "声音",
  "自然",
  "乐句",
  "旋律",
  "音准",
];

export function buildPeerFeedbackShowcases(groupTasks: string[], criteria: string[]): PeerFeedbackShowcase[] {
  const tasks = groupTasks.length ? groupTasks : ["A组展示节奏创编", "B组展示身体打击", "C组展示五声短句"];
  return tasks.map((task, index) => ({
    id: `showcase-${index + 1}`,
    groupName: task.match(/^[A-ZＡ-Ｚ一二三四五六七八九十\d]+组/)?.[0] || `${index + 1}组`,
    task,
    status: index === 0 ? "active" : "waiting",
    evidenceTerms: [],
    suggestion: "",
  }));
}

export function updatePeerFeedbackEvidence(
  showcases: PeerFeedbackShowcase[],
  index: number,
  evidence: string
): PeerFeedbackShowcase[] {
  return showcases.map((showcase, currentIndex) => {
    if (currentIndex !== index) return showcase;
    const next = showcase.evidenceTerms.includes(evidence)
      ? showcase.evidenceTerms.filter((item) => item !== evidence)
      : [...showcase.evidenceTerms, evidence];
    return { ...showcase, evidenceTerms: next };
  });
}

export function updatePeerFeedbackSuggestion(
  showcases: PeerFeedbackShowcase[],
  index: number,
  suggestion: string
): PeerFeedbackShowcase[] {
  return showcases.map((showcase, currentIndex) => (
    currentIndex === index ? { ...showcase, suggestion } : showcase
  ));
}

export function submitPeerFeedback(showcases: PeerFeedbackShowcase[], index: number): PeerFeedbackShowcase[] {
  const target = showcases[index];
  if (!target || !isReviewReady(target)) return showcases;
  return showcases.map((showcase, currentIndex) => {
    if (currentIndex === index) return { ...showcase, status: "reviewed" };
    if (currentIndex === index + 1 && showcase.status === "waiting") return { ...showcase, status: "active" };
    return showcase;
  });
}

export function evaluatePeerFeedback(showcases: PeerFeedbackShowcase[]): PeerFeedbackEvaluation {
  const activeIndex = showcases.findIndex((showcase) => showcase.status === "active");
  const active = activeIndex >= 0 ? showcases[activeIndex] : undefined;
  const reviewedCount = showcases.filter((showcase) => showcase.status === "reviewed").length;

  if (active && !active.evidenceTerms.length) {
    return {
      status: "needs_evidence",
      reviewedCount,
      feedback: `${active.groupName}展示后，请先选择一个音乐依据。`,
      teacherSuggestion: "提醒学生先听完整展示，再围绕节奏、力度、进入或合作倾听评价。",
    };
  }
  if (active && !hasSpecificMusicEvidence(active.suggestion)) {
    return {
      status: "needs_specific_suggestion",
      reviewedCount,
      feedback: `${active.groupName}还需要一句具体建议，不能只说好听或喜欢。`,
      teacherSuggestion: "请把建议改成“哪里稳定、哪里可改进”的音乐语言。",
    };
  }
  if (active) {
    return {
      status: "needs_showcase",
      reviewedCount,
      feedback: `${active.groupName}可以提交评价，然后请下一组展示。`,
      teacherSuggestion: "提交后让下一组带着同伴建议继续展示。",
    };
  }
  return {
    status: "ready",
    reviewedCount,
    feedback: "展示互评完成：每组都有同伴音乐依据和具体建议。",
    teacherSuggestion: "请教师汇总最常见的优点和下一轮要改进的音乐点。",
  };
}

export function buildPeerFeedbackRecord(showcases: PeerFeedbackShowcase[]): PeerFeedbackRecord {
  const reviewed = showcases.filter((showcase) => showcase.status === "reviewed");
  return {
    version: "peer_feedback_record_v1",
    totalShowcases: showcases.length,
    reviewedCount: reviewed.length,
    readyForTeacherSummary: showcases.length > 0 && reviewed.length === showcases.length,
    entries: reviewed.map((showcase) => ({
      groupName: showcase.groupName,
      task: showcase.task,
      evidenceTerms: [...showcase.evidenceTerms],
      suggestion: showcase.suggestion,
    })),
  };
}

export function hasSpecificMusicEvidence(text: string): boolean {
  const trimmed = text.trim();
  if (!trimmed) return false;
  const hasMusicWord = MUSIC_EVIDENCE_WORDS.some((word) => trimmed.includes(word));
  if (!hasMusicWord) return false;
  if (GENERIC_WORDS.some((word) => trimmed.includes(word)) && trimmed.length < 12) return false;
  return true;
}

function isReviewReady(showcase: PeerFeedbackShowcase): boolean {
  return showcase.status === "active" && showcase.evidenceTerms.length > 0 && hasSpecificMusicEvidence(showcase.suggestion);
}
