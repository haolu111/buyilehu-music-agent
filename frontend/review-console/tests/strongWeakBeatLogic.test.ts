import * as strongWeakLogic from "../src/activity/strongWeakBeatLogic";
import {
  buildAccentInputSummary,
  buildAccentRound,
  buildAccentSummary,
  buildCountInBeats,
  evaluateAccentAttempt,
  judgeAccentAction
} from "../src/activity/strongWeakBeatLogic";

function assertEqual<T>(actual: T, expected: T, label: string) {
  if (actual !== expected) {
    throw new Error(`${label}: expected ${String(expected)}, got ${String(actual)}`);
  }
}

const duple = buildAccentRound({ meter: "2/4", bpm: 88, cycleCount: 2 });
assertEqual(duple.length, 4, "duple meter round repeats two-beat pattern twice");
assertEqual(duple[0].strength, "strong", "duple beat one is strong");
assertEqual(duple[1].strength, "weak", "duple beat two is weak");
assertEqual(duple[0].action, "拍手", "strong beat uses visible large action");
assertEqual(duple[1].action, "拍腿", "weak beat uses smaller action");

const triple = buildAccentRound({ meter: "3/4", bpm: 96, cycleCount: 1 });
assertEqual(triple.map((beat) => beat.strength).join(","), "strong,weak,weak", "triple meter is strong-weak-weak");

const correctStrong = judgeAccentAction(duple[0], "拍手");
assertEqual(correctStrong.status, "correct", "strong beat action passes on beat one");
assertEqual(correctStrong.feedback.includes("强拍"), true, "strong beat feedback names the music concept");

const wrongWeak = judgeAccentAction(duple[1], "拍手");
assertEqual(wrongWeak.status, "wrong_accent", "large action on weak beat is rejected");
assertEqual(wrongWeak.feedback.includes("弱拍"), true, "weak beat feedback names the music concept");

const summary = buildAccentSummary([correctStrong, wrongWeak]);
assertEqual(summary.total, 2, "summary counts attempts");
assertEqual(summary.correct, 1, "summary counts correct accent actions");
assertEqual(summary.teacherSuggestion.includes("强弱"), true, "summary gives teacher a strong/weak beat suggestion");

type InputJudgement = {
  status: "correct" | "early" | "late" | "wrong_accent";
  feedback: string;
};

const judgeAccentInput = (strongWeakLogic as unknown as {
  judgeAccentInput?: (beat: typeof duple[number], selectedStrength: typeof duple[number]["strength"], offsetMs: number) => InputJudgement;
}).judgeAccentInput;

assertEqual(typeof judgeAccentInput, "function", "web judgement is separate from body action names");
assertEqual(judgeAccentInput?.(duple[0], "strong", 20).status, "correct", "matching strong beat within the time window passes");
assertEqual(judgeAccentInput?.(duple[0], "strong", -180).status, "early", "input before the target window is early");
assertEqual(judgeAccentInput?.(duple[1], "weak", 220).status, "late", "input after the target window is late");
assertEqual(judgeAccentInput?.(duple[1], "strong", 20).status, "wrong_accent", "web choice judges the accent class, not a body action");

const countIn = buildCountInBeats("3/4", 90);
assertEqual(countIn.length, 3, "one-bar count-in follows the selected meter numerator");
assertEqual(countIn.map((beat) => beat.label).join(","), "预备 1,预备 2,预备 3", "count-in labels are explicit and never reused as judged targets");

const passingAttempt = evaluateAccentAttempt(buildAccentInputSummary([
  { status: "correct", beat: duple[0], feedback: "" },
  { status: "correct", beat: duple[1], feedback: "" },
]));
assertEqual(passingAttempt.passed, true, "a clean accent judgement may proceed to body movement");

const missingAttempt = evaluateAccentAttempt(buildAccentInputSummary([
  { status: "correct", beat: duple[0], feedback: "" },
  { status: "missing", beat: duple[1], feedback: "" },
]));
assertEqual(missingAttempt.passed, false, "a missed beat requires another attempt even when other answers are correct");

const extraAttempt = evaluateAccentAttempt(buildAccentInputSummary([
  { status: "correct", beat: duple[0], feedback: "" },
  { status: "extra", beat: duple[0], feedback: "" },
]));
assertEqual(extraAttempt.passed, false, "an extra input requires another attempt");

const lowAccuracyAttempt = evaluateAccentAttempt({ total: 5, correct: 3, early: 0, late: 0, wrongAccent: 0, missing: 0, extra: 0, accuracy: 60 });
assertEqual(lowAccuracyAttempt.passed, false, "accuracy below 80 requires another attempt");
