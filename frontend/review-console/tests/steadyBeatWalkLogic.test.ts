import {
  buildSteadyBeatWalkPlan,
  buildSteadyBeatWalkRecord,
  evaluateSteadyBeatWalk,
  judgeSteadyBeatAction
} from "../src/activity/steadyBeatWalkLogic";

function assertEqual<T>(actual: T, expected: T, label: string) {
  if (actual !== expected) {
    throw new Error(`${label}: expected ${String(expected)}, got ${String(actual)}`);
  }
}

const plan = buildSteadyBeatWalkPlan({
  meter: "2/4",
  bpm: 84,
  rhythmPattern: ["quarter", "quarter", "rest", "quarter"],
  movementActions: ["走一步", "拍手", "停住"],
});

assertEqual(plan.meter, "2/4", "meter is kept");
assertEqual(plan.beats.length, 4, "plan builds four movement beats");
assertEqual(plan.beats[2].expectedAction, "停住", "rest beat expects freeze");
assertEqual(plan.beats[0].expectedAction, "走一步", "beat action starts with walking");

const beforeListen = evaluateSteadyBeatWalk(plan, {
  hasListenedBeat: false,
  judgements: [],
});
assertEqual(beforeListen.status, "needs_listening", "students must listen before moving");

const correctWalk = judgeSteadyBeatAction(plan.beats[0], "走一步");
assertEqual(correctWalk.status, "correct", "walking on beat passes");
assertEqual(correctWalk.feedback.includes("稳定拍"), true, "feedback names steady beat");

const wrongRest = judgeSteadyBeatAction(plan.beats[2], "走一步");
assertEqual(wrongRest.status, "wrong_rest", "moving on rest is rejected");
assertEqual(wrongRest.feedback.includes("休止"), true, "rest feedback names rest");

const ready = evaluateSteadyBeatWalk(plan, {
  hasListenedBeat: true,
  judgements: [
    correctWalk,
    judgeSteadyBeatAction(plan.beats[1], "拍手"),
    judgeSteadyBeatAction(plan.beats[2], "停住"),
  ],
});
assertEqual(ready.status, "ready", "three listened movement attempts are ready");
assertEqual(ready.teacherSuggestion.includes("隐藏提示"), true, "ready state suggests hiding hints");

const record = buildSteadyBeatWalkRecord(plan, {
  hasListenedBeat: true,
  judgements: ready.judgements,
});
assertEqual(record.version, "steady_beat_walk_record_v1", "record has stable export version");
assertEqual(record.readyForClassWalk, true, "ready record can move to class walking");
