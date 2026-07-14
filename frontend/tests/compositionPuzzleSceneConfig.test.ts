import assert from "node:assert/strict";
import {
  buildCompositionPuzzleLogicConfig,
  compositionFilledSlots,
  compositionMelodySlotCount,
  evaluateCompositionPuzzleChecks,
  numberedNoteLabel,
  rhythmAttackCount,
  type CompositionPlacedCard
} from "../src/student-game/compositionPuzzleLogic";

const config = buildCompositionPuzzleLogicConfig({
  mode: "melody_puzzle_creation",
  phrase_length_bars: 1,
  selected_meter: "4/4",
  selected_tonic: "C",
  selected_scale_type: "major_pentatonic",
  teacher_confirm_required: false,
  required_elements: ["C", "D", "E", "G", "A"]
});

assert.deepEqual(config.required_elements, ["C", "D", "E", "G", "A"]);
assert.deepEqual(config.melody_cards, ["C", "D", "E", "G", "A", "C'"]);
assert.equal(buildCompositionPuzzleLogicConfig({ selected_meter: "2/4" }).slots_per_bar, 2);
assert.equal(buildCompositionPuzzleLogicConfig({ selected_meter: "3/4" }).slots_per_bar, 3);
assert.equal(buildCompositionPuzzleLogicConfig({ selected_meter: "4/4" }).slots_per_bar, 4);
const longCompositionConfig = buildCompositionPuzzleLogicConfig({
  composition_total_bars: 16,
  composition_segment_bars: 4,
  phrase_length_bars: 4,
  selected_meter: "4/4"
});
assert.equal(longCompositionConfig.composition_total_bars, 16);
assert.equal(longCompositionConfig.composition_segment_bars, 4);
assert.equal(longCompositionConfig.composition_segments, 4);
assert.equal(longCompositionConfig.phrase_length_bars, 4);
assert.equal(longCompositionConfig.slots_per_bar, 4);
assert.equal(longCompositionConfig.total_slots, 64);
assert.equal(longCompositionConfig.segment_slots, 16);
assert.deepEqual(buildCompositionPuzzleLogicConfig({ selected_tonic: "D", selected_scale_type: "major_pentatonic" }).melody_cards, ["D", "E", "F#", "A", "B", "D'"]);
assert.deepEqual(buildCompositionPuzzleLogicConfig({ selected_tonic: "A", selected_scale_type: "minor" }).melody_cards, ["A", "B", "C'", "D'", "E'", "F'", "G'", "A'"]);
assert.deepEqual(["do", "re", "mi", "sol", "la"].map(numberedNoteLabel), ["1", "2", "3", "5", "6"]);
assert.deepEqual(["C", "D", "E", "G", "A", "C'"].map(numberedNoteLabel), ["1", "2", "3", "5", "6", "1'"]);
assert.deepEqual(["D", "E", "F#", "A", "B", "D'"].map((note) => numberedNoteLabel(note, "D")), ["1", "2", "3", "5", "6", "1'"]);

const incompletePhrase: CompositionPlacedCard[] = ["C", "D", "E", "G"].map((pitch, index) => ({
  id: `quarter_${index}`,
  label: "四分",
  rhythm: "quarter",
  attackCount: 1,
  pitches: [pitch],
  beats: 1
}));

const incompleteChecks = evaluateCompositionPuzzleChecks(config, incompletePhrase, false);
assert.equal(incompleteChecks.find((check) => check.id === "pitch_token_A")?.passed, false);

const completePhrase: CompositionPlacedCard[] = [
  { id: "quarter_1", label: "四分", rhythm: "quarter", attackCount: 1, pitches: ["C"], beats: 1 },
  { id: "quarter_2", label: "四分", rhythm: "quarter", attackCount: 1, pitches: ["D"], beats: 1 },
  { id: "eighth_pair_1", label: "二八", rhythm: "eighth_pair", attackCount: 2, pitches: ["E", "G"], beats: 1 },
  { id: "quarter_3", label: "四分", rhythm: "quarter", attackCount: 1, pitches: ["A"], beats: 1 }
];

const completeChecks = evaluateCompositionPuzzleChecks(config, completePhrase, false);
assert.equal(completeChecks.every((check) => check.passed), true);

const arcadeConfig = buildCompositionPuzzleLogicConfig({
  mode: "melody_rhythm_puzzle",
  phrase_length_bars: 2,
  slots_per_bar: 4,
  teacher_confirm_required: true,
  constraint_profile: "balanced",
  rhythm_cards: [
    { id: "quarter", label: "四分", beats: 1 },
    { id: "eighth_pair", label: "二八", beats: 1 },
    { id: "sixteenth_four", label: "四个十六", beats: 1 },
    { id: "eighth_sixteenth_sixteenth", label: "前八后十六", beats: 1 },
    { id: "sixteenth_sixteenth_eighth", label: "前十六后八", beats: 1 },
    { id: "rest", label: "休止", beats: 1 }
  ],
  selected_tonic: "C",
  selected_scale_type: "major_pentatonic",
  required_elements: ["填满小节", "试听后提交", "至少使用 2 种节奏材料", "至少出现 3 个音高", "结束音回到 C 或 A"]
});

assert.equal(rhythmAttackCount("quarter"), 1);
assert.equal(rhythmAttackCount("eighth_pair"), 2);
assert.equal(rhythmAttackCount("sixteenth_four"), 4);
assert.equal(rhythmAttackCount("eighth_sixteenth_sixteenth"), 3);
assert.equal(rhythmAttackCount("sixteenth_sixteenth_eighth"), 3);
assert.equal(rhythmAttackCount("rest"), 0);

const mixedPhrase: CompositionPlacedCard[] = [
  { id: "quarter_1", label: "四分", rhythm: "quarter", beats: 1, attackCount: 1, pitches: ["C"] },
  { id: "eighth_pair_1", label: "二八", rhythm: "eighth_pair", beats: 1, attackCount: 2, pitches: ["D", "E"] },
  { id: "sixteenth_four_1", label: "四个十六", rhythm: "sixteenth_four", beats: 1, attackCount: 4, pitches: ["G", "A", "C", "D"] },
  { id: "eighth_sixteenth_sixteenth_1", label: "前八后十六", rhythm: "eighth_sixteenth_sixteenth", beats: 1, attackCount: 3, pitches: ["E", "G", "A"] },
  { id: "sixteenth_sixteenth_eighth_1", label: "前十六后八", rhythm: "sixteenth_sixteenth_eighth", beats: 1, attackCount: 3, pitches: ["C", "D", "E"] },
  { id: "rest_1", label: "休止", rhythm: "rest", beats: 1, attackCount: 0, pitches: [] },
  { id: "quarter_2", label: "四分", rhythm: "quarter", beats: 1, attackCount: 1, pitches: ["G"] },
  { id: "quarter_3", label: "四分", rhythm: "quarter", beats: 1, attackCount: 1, pitches: ["A"] }
];

assert.equal(compositionFilledSlots(mixedPhrase), 8);
assert.equal(compositionMelodySlotCount(mixedPhrase), 15);

const rhythmOnlyPhrase: CompositionPlacedCard[] = mixedPhrase.map((item) => ({ ...item, pitches: Array(rhythmAttackCount(item.rhythm)).fill("") }));
const rhythmOnlyChecks = evaluateCompositionPuzzleChecks(arcadeConfig, rhythmOnlyPhrase, true, true);
assert.equal(rhythmOnlyChecks.find((check) => check.id === "melody_filled")?.passed, false);

const beforeAuditionChecks = evaluateCompositionPuzzleChecks(arcadeConfig, mixedPhrase, true, false);
assert.equal(beforeAuditionChecks.find((check) => check.id === "required_auditioned")?.passed, false);
assert.equal(beforeAuditionChecks.every((check) => check.passed), false);

const afterAuditionChecks = evaluateCompositionPuzzleChecks(arcadeConfig, mixedPhrase, true, true);
assert.equal(afterAuditionChecks.find((check) => check.id === "required_auditioned")?.passed, true);
assert.equal(afterAuditionChecks.find((check) => check.id === "required_rhythm_variety")?.passed, true);
assert.equal(afterAuditionChecks.find((check) => check.id === "required_pitch_count")?.passed, true);
assert.equal(afterAuditionChecks.find((check) => check.id === "required_cadence")?.passed, true);
assert.equal(afterAuditionChecks.every((check) => check.passed), true);

assert.equal(mixedPhrase.find((item) => item.rhythm === "rest")?.pitches?.length, 0);
