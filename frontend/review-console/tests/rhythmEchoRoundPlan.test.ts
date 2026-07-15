import { resolveRhythmRoundPlan } from "../src/student-game/rhythmEchoRoundPlan";

function assertDeepEqual(actual: unknown, expected: unknown, label: string) {
  const actualText = JSON.stringify(actual);
  const expectedText = JSON.stringify(expected);
  if (actualText !== expectedText) {
    throw new Error(`${label}: expected ${expectedText}, got ${actualText}`);
  }
}

const firstRound = resolveRhythmRoundPlan({
  pattern_steps: ["quarter", "quarter"],
  round_patches: {
    round_2: { pattern_steps: ["quarter", "rest", "eighth_pair"] }
  },
  active_round: 1
});

assertDeepEqual(firstRound.pattern_steps, ["quarter", "quarter"], "round 1 keeps the base rhythm");
assertDeepEqual(firstRound.pattern_timeline.map((item) => item.label), ["四分", "四分"], "round 1 timeline");

const secondRound = resolveRhythmRoundPlan({
  pattern_steps: ["quarter", "quarter"],
  round_patches: {
    round_2: { pattern_steps: ["quarter", "rest", "eighth_pair"] }
  },
  active_round: 2
});

assertDeepEqual(secondRound.pattern_steps, ["quarter", "rest", "eighth_pair"], "round 2 uses the instance patch");
assertDeepEqual(secondRound.pattern_timeline.map((item) => item.label), ["四分", "休", "八分", "八分"], "round 2 patched timeline");
assertDeepEqual(
  secondRound.pattern_timeline.map((item) => item.hit_required),
  [true, false, true, true],
  "round 2 rest is not a hit"
);
