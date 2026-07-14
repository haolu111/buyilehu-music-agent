import {
  buildPhraseRepairPlan,
  formatBreathPoint,
  normalizeSingingBpm
} from "../src/activity/phraseSingingLogic";

function assertEqual<T>(actual: T, expected: T, label: string) {
  if (actual !== expected) {
    throw new Error(`${label}: expected ${String(expected)}, got ${String(actual)}`);
  }
}

const plan = buildPhraseRepairPlan({
  lyricsPhrases: ["小船儿轻轻飘荡在水中", "迎面吹来了凉爽的风"],
  melodyPhrases: ["mi sol la sol mi re", "re mi sol mi re do"],
  difficultPhrase: "迎面吹来了凉爽的风",
  breathPoints: ["吹来了/凉爽的风"],
  bpm: 72,
});

assertEqual(plan.variant, "difficult_phrase_repair", "difficult phrase creates repair variant");
assertEqual(plan.activeIndex, 1, "difficult phrase focuses matching lyric");
assertEqual(plan.breathHints[0], "吹来了 / 凉爽的风", "breath point uses visible slash spacing");
assertEqual(plan.melodyHint, "re mi sol mi re do", "repair plan keeps matching melody hint");
assertEqual(plan.slowLoopLabel, "慢速循环 72 BPM", "repair plan labels slow loop tempo");

const defaultPlan = buildPhraseRepairPlan({
  lyricsPhrases: ["春天来了", "小鸟歌唱"],
  melodyPhrases: ["do re mi", "mi sol mi"],
});

assertEqual(defaultPlan.variant, "phrase_loop_singing", "normal phrase singing stays loop variant");
assertEqual(defaultPlan.activeIndex, 0, "normal phrase singing starts from first phrase");
assertEqual(defaultPlan.slowLoopLabel, "循环 86 BPM", "normal phrase singing uses classroom default tempo");
assertEqual(formatBreathPoint("小船儿/轻轻"), "小船儿 / 轻轻", "breath formatter spaces teacher slash");
assertEqual(normalizeSingingBpm(38), 60, "singing tempo lower bound keeps classroom usable");
assertEqual(normalizeSingingBpm(140), 108, "singing tempo upper bound avoids too-fast singing drill");
