export type BodyPercussionSlot = {
  beatIndex: number;
  rhythm: string;
  action: string;
};

export type BodyPercussionResult = {
  status: "incomplete" | "rest_should_freeze" | "ready";
  feedback: string;
};

export function buildBodyPercussionSlots(rhythmPattern: string[], actions: string[]): BodyPercussionSlot[] {
  return rhythmPattern.map((rhythm, index) => ({
    beatIndex: index + 1,
    rhythm,
    action: rhythm === "rest" ? "停住" : actions[index % Math.max(1, actions.length)] || "拍手",
  }));
}

export function updateBodyAction(slots: BodyPercussionSlot[], beatIndex: number, action: string): BodyPercussionSlot[] {
  return slots.map((slot) => (slot.beatIndex === beatIndex ? { ...slot, action } : slot));
}

export function judgeBodyPercussion(slots: BodyPercussionSlot[]): BodyPercussionResult {
  if (!slots.length || slots.some((slot) => !slot.action)) {
    return { status: "incomplete", feedback: "每个拍点都要有动作或停住。" };
  }
  const restMistake = slots.find((slot) => slot.rhythm === "rest" && slot.action !== "停住");
  if (restMistake) {
    return { status: "rest_should_freeze", feedback: `第 ${restMistake.beatIndex} 拍是休止，身体动作要停住。` };
  }
  return { status: "ready", feedback: "身体打击编排完成：动作能落在拍点上，休止也表现出来了。" };
}

export function actionSyllable(action: string): string {
  if (action.includes("腿")) return "腿";
  if (action.includes("跺")) return "脚";
  if (action.includes("肩")) return "肩";
  if (action.includes("停")) return "休";
  return "拍";
}
