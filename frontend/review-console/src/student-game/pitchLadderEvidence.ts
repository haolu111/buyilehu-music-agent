export type PitchEvidenceMode = "direction_pair" | "single_solfege" | "melody_path";

export type PitchEvidenceSnapshot = {
  currentMode: PitchEvidenceMode;
  sequence: string[];
  labels?: string[];
  selected: string[];
  mistakes: number;
  totalRounds: number;
  cleared: number;
  status: "ready" | "listening" | "playing" | "round_clear" | "mission_success" | "mission_failed";
};

export type PitchEvidenceSummary = {
  target: string;
  studentAction: string;
  checkpoint: string;
  review: string;
  nextAction: string;
  teacherCheckpoint: string;
  process: PitchEvidenceStep[];
};

export type PitchEvidenceStep = {
  id: "listen" | "decide" | "sing" | "explain";
  label: string;
  detail: string;
  state: "pending" | "active" | "done" | "risk";
};

export function buildPitchEvidenceSummary(snapshot: PitchEvidenceSnapshot): PitchEvidenceSummary {
  const target = displaySequence(snapshot.labels?.length ? snapshot.labels : snapshot.sequence);
  const studentAction = studentActionForSnapshot(snapshot);
  const checkpoint = checkpointForMode(snapshot.currentMode);
  const review = reviewForSnapshot(snapshot);
  const nextAction = nextActionForSnapshot(snapshot);
  const teacherCheckpoint = teacherCheckpointForSnapshot(snapshot);
  const process = processForSnapshot(snapshot);
  return { target, studentAction, checkpoint, review, nextAction, teacherCheckpoint, process };
}

function studentActionForSnapshot(snapshot: PitchEvidenceSnapshot) {
  if (snapshot.currentMode === "direction_pair") {
    const direction = snapshot.selected[0];
    return `判断：${directionLabel(direction)}`;
  }
  if (snapshot.currentMode === "single_solfege") {
    return `唱名：${displaySequence(snapshot.selected) || "待定位"}`;
  }
  return `路线：${displaySequence(snapshot.selected) || "待走路线"}`;
}

function checkpointForMode(mode: PitchEvidenceMode) {
  if (mode === "direction_pair") return "唱/哼出方向";
  if (mode === "single_solfege") return "唱回目标唱名";
  return "唱完整路线";
}

function reviewForSnapshot(snapshot: PitchEvidenceSnapshot) {
  if (snapshot.status === "mission_failed" || snapshot.mistakes > 0) {
    if (snapshot.currentMode === "melody_path") return "复盘：路线顺序还不稳，回到目标音列逐个唱名再走一遍。";
    if (snapshot.currentMode === "single_solfege") return "复盘：唱名定位还不稳，先听目标音，再在音阶位置上找它。";
    return "复盘：高低方向还不稳，请学生先用手势画出声音走向。";
  }
  if (snapshot.currentMode === "melody_path") return "追问：这条旋律是上行、下行还是有转折？请学生唱完整路线。";
  if (snapshot.currentMode === "single_solfege") return "追问：这个唱名在音阶的哪个位置？请学生唱回确认。";
  return "追问：第二个音为什么更高？请学生用手势或声音再表现一次。";
}

function nextActionForSnapshot(snapshot: PitchEvidenceSnapshot) {
  if (snapshot.status === "mission_failed") {
    if (snapshot.currentMode === "melody_path") return "回到目标音列逐个唱名";
    if (snapshot.currentMode === "single_solfege") return "先听目标音再找位置";
    return "用手势重做高低方向";
  }
  if (snapshot.status === "ready") {
    if (snapshot.currentMode === "melody_path") return "先听短旋律";
    if (snapshot.currentMode === "direction_pair") return "先听目标音组";
    return "先听目标音";
  }
  if (snapshot.status === "listening") return snapshot.currentMode === "melody_path" ? "记住旋律走向" : "准备定位";
  if (snapshot.status === "round_clear" || snapshot.status === "mission_success") return checkpointForMode(snapshot.currentMode);
  if (snapshot.currentMode === "direction_pair") {
    return snapshot.selected.length ? "唱出所选方向" : "选择高/平/低";
  }
  if (snapshot.currentMode === "single_solfege") {
    return snapshot.selected.length ? "唱回目标唱名" : "点出目标唱名";
  }
  return snapshot.selected.length ? "继续走完路线" : "按听到的顺序走台阶";
}

function teacherCheckpointForSnapshot(snapshot: PitchEvidenceSnapshot) {
  if (snapshot.status === "mission_failed") {
    if (snapshot.currentMode === "melody_path") return "先暂停闯关，让学生按目标音列逐个唱名后再走路线。";
    if (snapshot.currentMode === "single_solfege") return "让学生回到音阶位置，用声音确认目标唱名。";
    return "让学生先用手势画出声音上行、下行或保持，再重新听。";
  }
  if (snapshot.status === "ready") {
    if (snapshot.currentMode === "melody_path") return "先完整播放短旋律，再让学生按顺序走路线。";
    if (snapshot.currentMode === "direction_pair") return "先完整播放目标音组，再让学生判断第二个音的方向。";
    return "听完后再让学生定位唱名，避免直接猜按钮。";
  }
  if (snapshot.status === "round_clear" || snapshot.status === "mission_success") {
    if (snapshot.currentMode === "melody_path") return "确认学生能唱完整路线，并说出上行、下行或转折。";
    if (snapshot.currentMode === "single_solfege") return "确认学生不是只点对按钮，而是能唱回目标唱名。";
    return "教师听学生是否真的唱/哼出了所选方向，再进入下一关。";
  }
  if (snapshot.currentMode === "direction_pair") {
    const direction = directionLabel(snapshot.selected[0]);
    return snapshot.selected.length
      ? `教师听学生是否真的唱/哼出了${direction}方向，再放行跳跃。`
      : "先让学生说出第二个音更高、一样高还是更低。";
  }
  if (snapshot.currentMode === "single_solfege") {
    return snapshot.selected.length
      ? "请学生唱回这个唱名，再追问它在音阶中的位置。"
      : "先听目标音，再让学生在唱名阶梯上定位。";
  }
  return snapshot.selected.length
    ? "观察学生是否按听到的顺序前进，必要时要求边走边唱唱名。"
    : "先听完整短旋律，再让学生开始走路线。";
}

function processForSnapshot(snapshot: PitchEvidenceSnapshot): PitchEvidenceStep[] {
  const labels = processLabelsForMode(snapshot.currentMode);
  const states = processStatesForSnapshot(snapshot);
  return [
    { id: "listen", label: "听", detail: labels.listen, state: states.listen },
    { id: "decide", label: labels.decideLabel, detail: labels.decide, state: states.decide },
    { id: "sing", label: "唱", detail: labels.sing, state: states.sing },
    { id: "explain", label: "说", detail: labels.explain, state: states.explain }
  ];
}

function processLabelsForMode(mode: PitchEvidenceMode) {
  if (mode === "melody_path") {
    return {
      listen: "短旋律",
      decideLabel: "走",
      decide: "台阶路线",
      sing: "完整路线",
      explain: "走向转折"
    };
  }
  if (mode === "single_solfege") {
    return {
      listen: "目标音",
      decideLabel: "找",
      decide: "唱名位置",
      sing: "唱回",
      explain: "音阶位置"
    };
  }
  return {
    listen: "目标音组",
    decideLabel: "辨",
    decide: "高低方向",
    sing: "唱出方向",
    explain: "说明依据"
  };
}

function processStatesForSnapshot(snapshot: PitchEvidenceSnapshot): Record<PitchEvidenceStep["id"], PitchEvidenceStep["state"]> {
  if (snapshot.status === "mission_failed") {
    return { listen: "done", decide: "risk", sing: "pending", explain: "pending" };
  }
  if (snapshot.status === "ready") {
    return { listen: "active", decide: "pending", sing: "pending", explain: "pending" };
  }
  if (snapshot.status === "listening") {
    return { listen: "active", decide: "pending", sing: "pending", explain: "pending" };
  }
  if (snapshot.status === "round_clear") {
    return { listen: "done", decide: "done", sing: "active", explain: "pending" };
  }
  if (snapshot.status === "mission_success") {
    return { listen: "done", decide: "done", sing: "done", explain: "active" };
  }
  if (snapshot.mistakes > 0) {
    return { listen: "done", decide: "risk", sing: "pending", explain: "pending" };
  }
  if (snapshot.selected.length > 0) {
    return { listen: "done", decide: "done", sing: "active", explain: "pending" };
  }
  return { listen: "done", decide: "active", sing: "pending", explain: "pending" };
}

function displaySequence(values: string[] = []) {
  return values.map(noteLabel).filter(Boolean).join(" → ");
}

function noteLabel(note: string) {
  return {
    do: "do",
    re: "re",
    mi: "mi",
    fa: "fa",
    sol: "sol",
    la: "la",
    ti: "ti",
    do_high: "do'"
  }[note] || note;
}

function directionLabel(direction: string | undefined) {
  if (direction === "higher") return "更高";
  if (direction === "same") return "一样高";
  if (direction === "lower") return "更低";
  return "待选择";
}
