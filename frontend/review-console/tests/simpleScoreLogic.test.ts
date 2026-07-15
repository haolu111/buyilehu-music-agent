import {
  buildSimpleScorePlan,
  numberedScoreToSolfege,
  rhythmLabelForScore
} from "../src/activity/simpleScoreLogic";

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

assertDeepEqual(numberedScoreToSolfege("1 2 3 | 3 5 6"), ["do", "re", "mi", "mi", "sol", "la"], "numbered score maps to classroom solfege");
assertEqual(rhythmLabelForScore("quarter"), "四", "quarter note uses formal classroom rhythm naming");
assertEqual(rhythmLabelForScore("half"), "二分", "half note uses formal classroom rhythm naming");
assertEqual(rhythmLabelForScore("rest"), "休止", "rest uses formal classroom rhythm naming");

const plan = buildSimpleScorePlan({
  numberedScore: ["1 2 3", "3 5 6"],
  rhythmPattern: ["quarter", "quarter", "half"],
  bpm: 120
});

assertEqual(plan.bpm, 104, "score following clamps fast tempo for primary classroom");
assertEqual(plan.lines.length, 2, "score plan preserves short score lines");
assertEqual(plan.lines[0].teacherCue, "先听第 1 行，再跟读简谱。", "line reminds students to listen first");
assertDeepEqual(plan.lines[0].solfege, ["do", "re", "mi"], "line includes solfege mapping");
assertDeepEqual(plan.rhythmCards.map((card) => card.label), ["四", "四", "二分"], "rhythm cards follow the provided pattern with formal rhythm names");
