import {
  buildSolfegeEchoPlan,
  describePitchMotion,
  normalizeEchoPhrases
} from "../src/activity/solfegeEchoLogic";

function assertEqual<T>(actual: T, expected: T, label: string) {
  if (actual !== expected) {
    throw new Error(`${label}: expected ${String(expected)}, got ${String(actual)}`);
  }
}

function assertDeepEqual<T>(actual: T, expected: T, label: string) {
  const actualText = JSON.stringify(actual);
  const expectedText = JSON.stringify(expected);
  if (actualText !== expectedText) {
    throw new Error(`${label}: expected ${expectedText}, got ${actualText}`);
  }
}

const phrases = normalizeEchoPhrases({
  solfegeSet: ["do", "re", "mi", "sol", "la"],
  pitchMotion: ["do-re-mi", "mi-sol-la", ["sol", "mi"]]
});

assertDeepEqual(phrases[0], ["do", "re", "mi"], "hyphenated motion becomes solfege phrase");
assertDeepEqual(phrases[1], ["mi", "sol", "la"], "second motion becomes second phrase");
assertDeepEqual(phrases[2], ["sol", "mi"], "array motion is preserved");

const plan = buildSolfegeEchoPlan({
  solfegeSet: ["do", "re", "mi", "sol", "la", "ti"],
  pitchMotion: ["do-re-mi", "mi-sol-la"],
  bpm: 118
});

assertDeepEqual(plan.allowedSolfege, ["do", "re", "mi", "sol", "la"], "plan limits echo to five classroom pitches");
assertEqual(plan.bpm, 104, "plan clamps fast echo tempo");
assertEqual(plan.rounds.length, 2, "plan keeps teacher echo rounds");
assertEqual(plan.rounds[0].teacherCue, "教师唱：do re mi", "round says teacher sings first");
assertEqual(plan.rounds[0].studentCue, "学生回声模唱：do re mi", "round asks students to echo sing");
assertEqual(plan.rounds[0].motionHint, "上行", "round includes pitch direction");

assertEqual(describePitchMotion(["do", "re", "mi"]), "上行", "ascending motion");
assertEqual(describePitchMotion(["sol", "mi", "do"]), "下行", "descending motion");
assertEqual(describePitchMotion(["do", "mi", "re"]), "有上有下", "mixed motion");
