export type StrongWeakMeter = "2/4" | "3/4" | "4/4";
export type AccentStrength = "strong" | "secondary" | "weak";
export type AccentJudgeStatus = "correct" | "wrong_accent";
export type AccentInputStatus = "correct" | "early" | "late" | "wrong_accent" | "extra" | "missing";

export type AccentBeat = {
  id: string;
  bar: number;
  beatInBar: number;
  strength: AccentStrength;
  label: string;
  action: string;
  startMs: number;
};

export type AccentJudgement = {
  status: AccentJudgeStatus;
  beat: AccentBeat;
  chosenAction: string;
  feedback: string;
};

export type AccentSummary = {
  total: number;
  correct: number;
  accuracy: number;
  teacherSuggestion: string;
};

export type AccentInputJudgement = {
  status: AccentInputStatus;
  beat: AccentBeat;
  selectedStrength?: AccentStrength;
  offsetMs?: number;
  feedback: string;
};

export type AccentInputSummary = {
  total: number;
  correct: number;
  early: number;
  late: number;
  wrongAccent: number;
  missing: number;
  extra: number;
  accuracy: number;
};

export type AccentAttemptEvaluation = {
  passed: boolean;
  feedback: string;
};

const PATTERNS: Record<StrongWeakMeter, Array<Pick<AccentBeat, "strength" | "label" | "action">>> = {
  "2/4": [
    { strength: "strong", label: "强拍", action: "拍手" },
    { strength: "weak", label: "弱拍", action: "拍腿" },
  ],
  "3/4": [
    { strength: "strong", label: "强拍", action: "拍手" },
    { strength: "weak", label: "弱拍", action: "轻拍肩" },
    { strength: "weak", label: "弱拍", action: "轻拍手" },
  ],
  "4/4": [
    { strength: "strong", label: "强拍", action: "拍手" },
    { strength: "weak", label: "弱拍", action: "拍腿" },
    { strength: "secondary", label: "次强拍", action: "轻拍手" },
    { strength: "weak", label: "弱拍", action: "拍腿" },
  ],
};

export function buildAccentRound(options: { meter?: StrongWeakMeter; bpm?: number; cycleCount?: number } = {}): AccentBeat[] {
  const meter = options.meter ?? "2/4";
  const pattern = PATTERNS[meter] ?? PATTERNS["2/4"];
  const cycleCount = Math.max(1, Math.floor(options.cycleCount ?? 2));
  const beatMs = Math.round(60000 / Math.max(40, Math.min(180, options.bpm ?? 88)));
  const beats: AccentBeat[] = [];
  for (let cycle = 0; cycle < cycleCount; cycle += 1) {
    pattern.forEach((beat, index) => {
      beats.push({
        ...beat,
        id: `${cycle + 1}-${index + 1}`,
        bar: cycle + 1,
        beatInBar: index + 1,
        startMs: beats.length * beatMs,
      });
    });
  }
  return beats;
}

export function buildCountInBeats(meter: StrongWeakMeter, bpm: number): AccentBeat[] {
  const beatMs = Math.round(60000 / Math.max(40, Math.min(180, bpm)));
  const beatsPerBar = PATTERNS[meter]?.length ?? PATTERNS["2/4"].length;
  return Array.from({ length: beatsPerBar }, (_, index) => ({
    id: `count-in-${index + 1}`,
    bar: 0,
    beatInBar: index + 1,
    strength: index === 0 ? "strong" : "weak",
    label: `预备 ${index + 1}`,
    action: "预备拍，不作答",
    startMs: index * beatMs,
  }));
}

export function judgeAccentAction(beat: AccentBeat, chosenAction: string): AccentJudgement {
  const normalized = chosenAction.trim();
  const correct = normalized === beat.action;
  return {
    status: correct ? "correct" : "wrong_accent",
    beat,
    chosenAction: normalized,
    feedback: correct
      ? `${beat.label}动作正确：第 ${beat.beatInBar} 拍用“${beat.action}”表现${beat.label}。`
      : `${beat.label}要用“${beat.action}”，刚才的动作没有表现出${beat.label}。`,
  };
}

export function accentInputChoices(meter: StrongWeakMeter): AccentStrength[] {
  return meter === "4/4" ? ["strong", "secondary", "weak"] : ["strong", "weak"];
}

export function judgeAccentInput(
  beat: AccentBeat,
  selectedStrength: AccentStrength,
  offsetMs: number,
  options: { correctWindowMs?: number } = {}
): AccentInputJudgement {
  const correctWindowMs = Math.max(60, Math.min(220, Number(options.correctWindowMs ?? 120)));
  if (offsetMs < -correctWindowMs) {
    return { status: "early", beat, selectedStrength, offsetMs, feedback: "稍早，等拍点到了再选择。" };
  }
  if (offsetMs > correctWindowMs) {
    return { status: "late", beat, selectedStrength, offsetMs, feedback: "稍晚，下一拍提前在心里数拍。" };
  }
  if (selectedStrength !== beat.strength) {
    return {
      status: "wrong_accent",
      beat,
      selectedStrength,
      offsetMs,
      feedback: `第 ${beat.beatInBar} 拍是${beat.label}，这次选错了。`
    };
  }
  return {
    status: "correct",
    beat,
    selectedStrength,
    offsetMs,
    feedback: `正确：第 ${beat.beatInBar} 拍是${beat.label}。`
  };
}

export function buildAccentInputSummary(judgements: AccentInputJudgement[]): AccentInputSummary {
  const count = (status: AccentInputStatus) => judgements.filter((item) => item.status === status).length;
  const correct = count("correct");
  const total = judgements.length;
  return {
    total,
    correct,
    early: count("early"),
    late: count("late"),
    wrongAccent: count("wrong_accent"),
    missing: count("missing"),
    extra: count("extra"),
    accuracy: total ? Math.round((correct / total) * 100) : 0
  };
}

export function evaluateAccentAttempt(summary: AccentInputSummary): AccentAttemptEvaluation {
  const passed = summary.accuracy >= 80
    && summary.missing === 0
    && summary.extra === 0
    && summary.wrongAccent === 0;
  return {
    passed,
    feedback: passed
      ? "网页判断准确，可以开始身体律动。"
      : "本轮尚未达到要求。请再听一次并重练。"
  };
}

export function buildAccentSummary(judgements: AccentJudgement[]): AccentSummary {
  const total = judgements.length;
  const correct = judgements.filter((item) => item.status === "correct").length;
  const accuracy = total ? Math.round((correct / total) * 100) : 0;
  return {
    total,
    correct,
    accuracy,
    teacherSuggestion:
      accuracy >= 80
        ? "强弱拍已经比较稳定，可以隐藏文字提示，让学生只听音乐做动作。"
        : "先保留强弱提示，放慢速度，让学生用大动作/小动作重新感受强弱拍。",
  };
}

export function accentToneOffset(strength: AccentStrength): number {
  if (strength === "strong") return 7;
  if (strength === "secondary") return 4;
  return 0;
}
