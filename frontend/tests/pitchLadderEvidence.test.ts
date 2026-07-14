import { buildPitchEvidenceSummary, type PitchEvidenceSnapshot } from "../src/student-game/pitchLadderEvidence";

function assertDeepEqual(actual: unknown, expected: unknown, label: string) {
  const actualText = JSON.stringify(actual);
  const expectedText = JSON.stringify(expected);
  if (actualText !== expectedText) {
    throw new Error(`${label}: expected ${expectedText}, got ${actualText}`);
  }
}

const directionPair: PitchEvidenceSnapshot = {
  currentMode: "direction_pair",
  sequence: ["do", "mi"],
  labels: ["do", "mi"],
  selected: ["higher"],
  mistakes: 0,
  totalRounds: 4,
  cleared: 2,
  status: "playing"
};

const directionPairReady: PitchEvidenceSnapshot = {
  ...directionPair,
  selected: [],
  status: "ready"
};

assertDeepEqual(
  buildPitchEvidenceSummary(directionPairReady).nextAction,
  "先听目标音组",
  "direction pair ready next action"
);

assertDeepEqual(
  buildPitchEvidenceSummary(directionPairReady).teacherCheckpoint,
  "先完整播放目标音组，再让学生判断第二个音的方向。",
  "direction pair ready teacher checkpoint"
);

assertDeepEqual(
  buildPitchEvidenceSummary(directionPair),
  {
    target: "do → mi",
    studentAction: "判断：更高",
    checkpoint: "唱/哼出方向",
    review: "追问：第二个音为什么更高？请学生用手势或声音再表现一次。",
    nextAction: "唱出所选方向",
    teacherCheckpoint: "教师听学生是否真的唱/哼出了更高方向，再放行跳跃。",
    process: [
      { id: "listen", label: "听", detail: "目标音组", state: "done" },
      { id: "decide", label: "辨", detail: "高低方向", state: "done" },
      { id: "sing", label: "唱", detail: "唱出方向", state: "active" },
      { id: "explain", label: "说", detail: "说明依据", state: "pending" }
    ]
  },
  "direction pair evidence"
);

const melodyPath: PitchEvidenceSnapshot = {
  currentMode: "melody_path",
  sequence: ["do", "re", "mi"],
  labels: ["do", "re", "mi"],
  selected: ["do", "re"],
  mistakes: 2,
  totalRounds: 4,
  cleared: 1,
  status: "mission_failed"
};

assertDeepEqual(
  buildPitchEvidenceSummary(melodyPath),
  {
    target: "do → re → mi",
    studentAction: "路线：do → re",
    checkpoint: "唱完整路线",
    review: "复盘：路线顺序还不稳，回到目标音列逐个唱名再走一遍。",
    nextAction: "回到目标音列逐个唱名",
    teacherCheckpoint: "先暂停闯关，让学生按目标音列逐个唱名后再走路线。",
    process: [
      { id: "listen", label: "听", detail: "短旋律", state: "done" },
      { id: "decide", label: "走", detail: "台阶路线", state: "risk" },
      { id: "sing", label: "唱", detail: "完整路线", state: "pending" },
      { id: "explain", label: "说", detail: "走向转折", state: "pending" }
    ]
  },
  "melody path evidence"
);

const singleSolfegeReady: PitchEvidenceSnapshot = {
  currentMode: "single_solfege",
  sequence: ["sol"],
  labels: ["sol"],
  selected: [],
  mistakes: 0,
  totalRounds: 3,
  cleared: 0,
  status: "ready"
};

assertDeepEqual(
  buildPitchEvidenceSummary(singleSolfegeReady),
  {
    target: "sol",
    studentAction: "唱名：待定位",
    checkpoint: "唱回目标唱名",
    review: "追问：这个唱名在音阶的哪个位置？请学生唱回确认。",
    nextAction: "先听目标音",
    teacherCheckpoint: "听完后再让学生定位唱名，避免直接猜按钮。",
    process: [
      { id: "listen", label: "听", detail: "目标音", state: "active" },
      { id: "decide", label: "找", detail: "唱名位置", state: "pending" },
      { id: "sing", label: "唱", detail: "唱回", state: "pending" },
      { id: "explain", label: "说", detail: "音阶位置", state: "pending" }
    ]
  },
  "single solfege ready evidence"
);
