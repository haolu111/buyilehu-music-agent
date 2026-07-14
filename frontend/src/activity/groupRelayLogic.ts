export type GroupRelayRound = {
  groupName: string;
  task: string;
  status: "waiting" | "active" | "performed" | "assessed";
  evidence: string;
};

export type GroupRelayResult = {
  status: "wait_turn" | "needs_performance" | "needs_music_evidence" | "ready";
  feedback: string;
};

const GENERIC_WORDS = ["好听", "喜欢", "很好", "不错", "开心", "有趣"];
const MUSIC_EVIDENCE_WORDS = ["节奏", "稳定", "休止", "停住", "强弱", "速度", "力度", "音色", "合拍", "进入", "同伴"];

export function buildGroupRelayRounds(groupTasks: string[]): GroupRelayRound[] {
  const tasks = groupTasks.length ? groupTasks : ["A组拍稳定拍", "B组接节奏", "C组做休止动作"];
  return tasks.map((task, index) => ({
    groupName: task.match(/^[A-ZＡ-Ｚ一二三四五六七八九十\d]+组/)?.[0] || `${index + 1}组`,
    task,
    status: index === 0 ? "active" : "waiting",
    evidence: "",
  }));
}

export function markGroupPerformed(rounds: GroupRelayRound[], index: number): GroupRelayRound[] {
  return rounds.map((round, currentIndex) => {
    if (currentIndex === index && round.status === "active") {
      return { ...round, status: "performed" };
    }
    return round;
  });
}

export function updateRelayEvidence(rounds: GroupRelayRound[], index: number, evidence: string): GroupRelayRound[] {
  return rounds.map((round, currentIndex) => (currentIndex === index ? { ...round, evidence } : round));
}

export function submitGroupAssessment(rounds: GroupRelayRound[], index: number): GroupRelayRound[] {
  return rounds.map((round, currentIndex) => {
    if (currentIndex === index && round.status === "performed" && hasMusicEvidence(round.evidence)) {
      return { ...round, status: "assessed" };
    }
    if (currentIndex === index + 1 && rounds[index]?.status === "performed" && hasMusicEvidence(rounds[index]?.evidence || "")) {
      return { ...round, status: round.status === "waiting" ? "active" : round.status };
    }
    return round;
  });
}

export function judgeGroupRelay(rounds: GroupRelayRound[]): GroupRelayResult {
  const activeIndex = rounds.findIndex((round) => round.status === "active");
  if (activeIndex >= 0) {
    return { status: "needs_performance", feedback: `${rounds[activeIndex].groupName}准备进入：先听上一组，再按本组任务表现。` };
  }

  const performedWithoutEvidence = rounds.find((round) => round.status === "performed" && !hasMusicEvidence(round.evidence));
  if (performedWithoutEvidence) {
    return {
      status: "needs_music_evidence",
      feedback: `${performedWithoutEvidence.groupName}评价要说音乐依据，例如节奏稳定、休止停住或进入整齐。`,
    };
  }

  const waiting = rounds.find((round) => round.status === "waiting");
  if (waiting) {
    return { status: "wait_turn", feedback: `${waiting.groupName}先听同伴表现，等轮到本组再进入。` };
  }

  return { status: "ready", feedback: "小组接力完成：每组都完成展示，并给出了音乐表现依据。" };
}

export function hasMusicEvidence(evidence: string): boolean {
  const trimmed = evidence.trim();
  if (!trimmed) return false;
  if (GENERIC_WORDS.some((word) => trimmed.includes(word)) && !MUSIC_EVIDENCE_WORDS.some((word) => trimmed.includes(word))) {
    return false;
  }
  return MUSIC_EVIDENCE_WORDS.some((word) => trimmed.includes(word));
}
