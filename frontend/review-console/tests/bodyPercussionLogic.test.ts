import {
  actionSyllable,
  buildBodyPercussionSlots,
  judgeBodyPercussion,
  updateBodyAction
} from "../src/activity/bodyPercussionLogic";

function assertEqual<T>(actual: T, expected: T, label: string) {
  if (actual !== expected) {
    throw new Error(`${label}: expected ${String(expected)}, got ${String(actual)}`);
  }
}

const slots = buildBodyPercussionSlots(["quarter", "eighth_pair", "rest", "quarter"], ["拍手", "拍腿", "跺脚"]);
assertEqual(slots.length, 4, "one slot is created for each rhythm item");
assertEqual(slots[2].action, "停住", "rest slots default to freeze");
assertEqual(judgeBodyPercussion(slots).status, "ready", "default rest-aware body percussion is ready");

const wrongRest = updateBodyAction(slots, 3, "跺脚");
assertEqual(judgeBodyPercussion(wrongRest).status, "rest_should_freeze", "rest beat must stay frozen");

const repaired = updateBodyAction(wrongRest, 3, "停住");
assertEqual(judgeBodyPercussion(repaired).status, "ready", "rest repair passes");
assertEqual(actionSyllable("拍腿"), "腿", "action syllable maps pat legs");
assertEqual(actionSyllable("停住"), "休", "action syllable maps freeze");
