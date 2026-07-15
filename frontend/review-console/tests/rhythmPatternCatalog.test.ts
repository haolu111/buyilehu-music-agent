import {
  buildRhythmPatternTimeline,
  generateRhythmEchoQuestion,
  getRhythmPatternDefinition,
  resolveRhythmExerciseInput,
  RHYTHM_PATTERN_DEFINITIONS
} from "../src/shared/rhythmPatternCatalog";

function assertEqual<T>(actual: T, expected: T, label: string) {
  if (actual !== expected) throw new Error(`${label}: expected ${String(expected)}, got ${String(actual)}`);
}

function assertDeepEqual(actual: unknown, expected: unknown, label: string) {
  const actualText = JSON.stringify(actual);
  const expectedText = JSON.stringify(expected);
  if (actualText !== expectedText) throw new Error(`${label}: expected ${expectedText}, got ${actualText}`);
}

assertDeepEqual(
  getRhythmPatternDefinition("sixteenth_four").hitOffsetsBeats,
  [0, 0.25, 0.5, 0.75],
  "four sixteenths expose all four attack positions"
);
assertDeepEqual(
  getRhythmPatternDefinition("eighth_sixteenth_sixteenth").hitOffsetsBeats,
  [0, 0.5, 0.75],
  "eighth-sixteenth-sixteenth exposes its real inner timing"
);
assertDeepEqual(
  getRhythmPatternDefinition("sixteenth_sixteenth_eighth").hitOffsetsBeats,
  [0, 0.25, 0.5],
  "sixteenth-sixteenth-eighth exposes its real inner timing"
);
assertDeepEqual(
  getRhythmPatternDefinition("eighth_triplet").hitOffsetsBeats,
  [0, 1 / 3, 2 / 3],
  "triplets divide one beat equally"
);
assertDeepEqual(getRhythmPatternDefinition("rest").restWindowsBeats, [[0, 1]], "quarter rest owns a full-beat silence window");
assertDeepEqual(getRhythmPatternDefinition("eighth_rest").restWindowsBeats, [[0, 0.5]], "eighth rest owns a half-beat silence window");

const timeline = buildRhythmPatternTimeline(
  ["sixteenth_four", "eighth_pair", "rest", "eighth_rest", "quarter"],
  { repeatCount: 1 }
);
assertDeepEqual(
  timeline.filter((event) => event.kind === "hit").map((event) => [event.rhythmId, event.targetBeat]),
  [
    ["sixteenth_four", 0],
    ["sixteenth_four", 0.25],
    ["sixteenth_four", 0.5],
    ["sixteenth_four", 0.75],
    ["eighth_pair", 1],
    ["eighth_pair", 1.5],
    ["quarter", 3.5]
  ],
  "the shared timeline expands inner attacks and advances through rests"
);
assertDeepEqual(
  timeline.filter((event) => event.kind === "rest").map((event) => [event.rhythmId, event.targetBeat, event.endBeat]),
  [["rest", 2, 3], ["eighth_rest", 3, 3.5]],
  "the shared timeline preserves exact rest windows"
);
assertEqual(RHYTHM_PATTERN_DEFINITIONS.length >= 12, true, "catalog covers the common primary rhythm review set");

const lowerQuestion = generateRhythmEchoQuestion({
  gradePreset: "lower_primary",
  meter: "3/4",
  random: () => 0,
});
assertEqual(lowerQuestion.barCount, 2, "lower primary questions contain two bars");
assertDeepEqual(lowerQuestion.barPatternIds, [["quarter", "quarter", "quarter"], ["quarter", "quarter", "quarter"]], "low grade draws only its approved pool and fills every bar");

const upperQuestion = generateRhythmEchoQuestion({
  gradePreset: "upper_primary",
  meter: "4/4",
  random: () => 0.999,
});
assertEqual(upperQuestion.barCount, 4, "middle and upper primary questions contain four bars");
upperQuestion.barPatternIds.forEach((bar, index) => {
  const beats = bar.reduce((sum, id) => sum + getRhythmPatternDefinition(id).durationBeats, 0);
  assertEqual(beats, 4, `upper-primary bar ${index + 1} fills the selected meter`);
});

const changedQuestion = generateRhythmEchoQuestion({
  gradePreset: "lower_primary",
  meter: "2/4",
  previousPatternIds: ["quarter", "quarter", "quarter", "quarter"],
  random: () => 0,
});
assertEqual(changedQuestion.patternIds.join("|") === "quarter|quarter|quarter|quarter", false, "a new question cannot repeat the previous sequence exactly");

const teacherSequence = resolveRhythmExerciseInput({
  patternIds: ["quarter", "eighth_pair", "rest", "sixteenth_four"],
  meter: "2/4",
  gradePreset: "middle_primary",
  bpm: 92,
  mode: "echo",
});
assertEqual(teacherSequence.ok, true, "a complete teacher sequence is accepted");
assertEqual(teacherSequence.source, "teacher_sequence", "teacher sequence has priority over random generation");
assertDeepEqual(teacherSequence.patternIds, ["quarter", "eighth_pair", "rest", "sixteenth_four"], "teacher sequence is preserved exactly");

const restricted = resolveRhythmExerciseInput({
  allowedPatternIds: ["quarter", "rest"],
  meter: "2/4",
  gradePreset: "lower_primary",
  bpm: 88,
  mode: "echo",
  random: () => 0.999,
});
assertEqual(restricted.source, "teacher_pool", "teacher-limited pool is distinguished from unrestricted random fallback");
assertEqual(restricted.patternIds.every((id) => id === "quarter" || id === "rest"), true, "restricted generation uses only teacher-approved ids");

const invalidId = resolveRhythmExerciseInput({ patternIds: ["unknown"], meter: "2/4", gradePreset: "middle_primary", bpm: 92, mode: "echo" });
assertEqual(invalidId.ok, false, "unknown rhythm ids are rejected instead of becoming quarter notes");
const incomplete = resolveRhythmExerciseInput({ patternIds: ["quarter"], meter: "2/4", gradePreset: "middle_primary", bpm: 92, mode: "echo" });
assertEqual(incomplete.ok, false, "teacher material that cannot fill complete bars is rejected instead of padded");
