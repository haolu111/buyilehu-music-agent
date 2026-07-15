import assert from "node:assert/strict";
import compositionWorkflowState from "./fixtures/lesson-composition-runtime-state.json";
import formWorkflowState from "./fixtures/lesson-form-runtime-state.json";
import meterWorkflowState from "./fixtures/lesson-meter-runtime-state.json";
import patchedPitchWorkflowState from "./fixtures/lesson-pitch-patched-runtime-state.json";
import patchedRhythmWorkflowState from "./fixtures/lesson-rhythm-patched-runtime-state.json";
import patchedTimbreWorkflowState from "./fixtures/lesson-timbre-patched-runtime-state.json";
import pitchWorkflowState from "./fixtures/lesson-pitch-runtime-state.json";
import rhythmWorkflowState from "./fixtures/lesson-rhythm-runtime-state.json";
import timbreWorkflowState from "./fixtures/lesson-timbre-runtime-state.json";
import {
  buildCompositionPuzzleLogicConfig,
  evaluateCompositionPuzzleChecks,
  type CompositionPlacedCard
} from "../src/student-game/compositionPuzzleLogic";
import {
  mergeCompositionEntityExecutionConfig,
  mergeFormEntityExecutionConfig,
  mergeMeterEntityExecutionConfig,
  mergePitchEntityExecutionConfig,
  mergeRhythmEntityExecutionConfig,
  mergeTimbreEntityExecutionConfig,
  resolveEntitySlotBindings,
  resolveMusicEntityExecution,
  resolveVariantParameters
} from "../src/student-game/musicEntityExecution";
import { resolveFormRouteJudgement } from "../src/student-game/formTreasureLogic";
import { PitchLadderGameSystem } from "../src/student-game/pitchLadderSystem";
import { resolveRhythmRoundPlan } from "../src/student-game/rhythmEchoRoundPlan";
import { resolveTimbreCaseJudgement } from "../src/student-game/timbreDetectiveLogic";
import type { StudentGameState } from "../src/student-game/types";

assertWorkflowExecutionContract(meterWorkflowState as StudentGameState);
assertWorkflowExecutionContract(rhythmWorkflowState as StudentGameState);
assertWorkflowExecutionContract(patchedRhythmWorkflowState as StudentGameState);
assertWorkflowExecutionContract(pitchWorkflowState as StudentGameState);
assertWorkflowExecutionContract(patchedPitchWorkflowState as StudentGameState);
assertWorkflowExecutionContract(timbreWorkflowState as StudentGameState);
assertWorkflowExecutionContract(patchedTimbreWorkflowState as StudentGameState);
assertWorkflowExecutionContract(formWorkflowState as StudentGameState);
assertWorkflowExecutionContract(compositionWorkflowState as StudentGameState);

const meterState = meterWorkflowState as StudentGameState;
const meterVariantParameters = resolveVariantParameters(meterState);
const meterSlotBindings = resolveEntitySlotBindings(meterState);
const meterConfig = mergeMeterEntityExecutionConfig(meterState, {
  meter: "2/4",
  beats_per_bar: 2,
  target_beats: [2]
});

assert.deepEqual(meterVariantParameters.target_beats, [1]);
assert.deepEqual(meterSlotBindings["meter.accent_pattern"], ["strong", "weak", "weak"]);
assert.equal(meterConfig.meter, "3/4");
assert.equal(meterConfig.beats_per_bar, 3);
assert.deepEqual(meterConfig.target_beats, [1]);
assert.deepEqual(meterConfig.accent_pattern, ["strong", "weak", "weak"]);

const rhythmState = rhythmWorkflowState as StudentGameState;
const rhythmConfig = mergeRhythmEntityExecutionConfig(rhythmState, { pattern_steps: ["quarter", "quarter"] });
const rhythmPlan = resolveRhythmRoundPlan(rhythmConfig);

assert.deepEqual(rhythmConfig.pattern_steps, ["quarter", "rest", "eighth_pair", "syncopation"]);
assert.deepEqual(rhythmPlan.pattern_steps, ["quarter", "rest", "eighth_pair", "syncopation"]);
assert.equal(rhythmPlan.pattern_timeline.find((item) => item.step === "rest")?.hit_required, false);
assert.equal(rhythmPlan.pattern_timeline.filter((item) => item.step === "eighth").length, 3);
assert.equal(rhythmPlan.pattern_timeline.filter((item) => item.step === "sixteenth").length, 2);
assert.equal(rhythmPlan.pattern_timeline.filter((item) => item.hit_required).length, 6);

const patchedRhythmState = patchedRhythmWorkflowState as StudentGameState;
const patchedRhythmConfig = mergeRhythmEntityExecutionConfig(patchedRhythmState, {
  pattern_steps: ["quarter", "quarter"],
  active_round: 2
});
const patchedRhythmPlan = resolveRhythmRoundPlan(patchedRhythmConfig);

assert.deepEqual(patchedRhythmConfig.pattern_steps, ["quarter", "rest", "eighth_pair", "syncopation"]);
assert.deepEqual(patchedRhythmConfig.round_patches?.round_2?.pattern_steps, ["quarter", "rest", "eighth_pair"]);
assert.deepEqual(patchedRhythmPlan.pattern_steps, ["quarter", "rest", "eighth_pair"]);
assert.equal(patchedRhythmPlan.pattern_steps.includes("syncopation"), false);
assert.equal(patchedRhythmPlan.pattern_timeline.find((item) => item.step === "rest")?.hit_required, false);
assert.equal(patchedRhythmPlan.pattern_timeline.filter((item) => item.step === "eighth").length, 2);

const pitchState = pitchWorkflowState as StudentGameState;
const pitchConfig = mergePitchEntityExecutionConfig(pitchState, {
  ...(pitchState.config ?? {}),
  pitch_range: ["do", "re"],
  pitch_rounds: [{ id: "old_round", sequence: ["do", "re"], answer: "higher" }]
});
const pitchRounds = pitchConfig.pitch_rounds as Array<Record<string, unknown>>;
const pitchSystem = new PitchLadderGameSystem({
  rounds: pitchRounds,
  energyMax: 100,
  mistakeLimit: 3
});

assert.deepEqual(pitchConfig.pitch_range, ["do", "mi", "sol", "do_high"]);
assert.deepEqual(pitchRounds[0].sequence, ["do", "mi", "sol", "do_high"]);
assert.deepEqual(pitchRounds[0].answer, ["do", "mi", "sol", "do_high"]);
assert.deepEqual(pitchSystem.currentSequence(), ["do", "mi", "sol", "do_high"]);
assert.equal(pitchSystem.chooseNode("do").judgement, "partial");
assert.equal(pitchSystem.chooseNode("mi").judgement, "partial");
assert.equal(pitchSystem.chooseNode("sol").judgement, "partial");
assert.equal(pitchSystem.chooseNode("do_high").judgement, "correct");

const patchedPitchState = patchedPitchWorkflowState as StudentGameState;
const patchedPitchConfig = mergePitchEntityExecutionConfig(patchedPitchState, {
  ...(patchedPitchState.config ?? {}),
  pitch_range: ["do", "mi", "sol", "do_high"]
});
const patchedPitchRounds = patchedPitchConfig.pitch_rounds as Array<Record<string, unknown>>;
const patchedPitchSystem = new PitchLadderGameSystem({
  rounds: [patchedPitchRounds[1]],
  energyMax: 100,
  mistakeLimit: 3
});

assert.deepEqual(patchedPitchConfig.pitch_range, ["do", "mi", "sol", "do_high"]);
assert.deepEqual(patchedPitchRounds[1].sequence, ["do", "mi", "sol"]);
assert.deepEqual(patchedPitchRounds[1].answer, ["do", "mi", "sol"]);
assert.deepEqual(patchedPitchSystem.currentSequence(), ["do", "mi", "sol"]);
assert.equal(patchedPitchSystem.chooseNode("do").judgement, "partial");
assert.equal(patchedPitchSystem.chooseNode("mi").judgement, "partial");
assert.equal(patchedPitchSystem.chooseNode("sol").judgement, "correct");

const timbreState = timbreWorkflowState as StudentGameState;
const timbreConfig = mergeTimbreEntityExecutionConfig(timbreState, {
  instrument_pool: ["木鱼", "三角铁"],
  timbre_traits: ["短促", "金属声"]
});
const timbreRounds = timbreConfig.timbre_rounds as Array<Record<string, unknown>>;

assert.deepEqual(timbreConfig.instrument_pool, ["笛子", "二胡"]);
assert.deepEqual(timbreConfig.timbre_traits, ["气息感", "弦鸣"]);
assert.equal(timbreRounds[0].answer, "笛子");
assert.equal(timbreRounds[0].compare_with, "二胡");
assert.deepEqual(timbreRounds[0].evidence_answer, ["气息感"]);
assert.deepEqual(timbreRounds[0].contrast_evidence_answer, ["弦鸣"]);
assert.equal(
  resolveTimbreCaseJudgement(timbreRounds[0], "笛子", ["气息感"], "弦鸣", timbreConfig.evidence_required, true).judgement,
  "solved"
);

const patchedTimbreState = patchedTimbreWorkflowState as StudentGameState;
const patchedTimbreConfig = mergeTimbreEntityExecutionConfig(patchedTimbreState, {
  instrument_pool: ["木鱼", "三角铁"],
  timbre_traits: ["短促", "金属声"]
});
const patchedTimbreRounds = patchedTimbreConfig.timbre_rounds as Array<Record<string, unknown>>;

assert.deepEqual(patchedTimbreConfig.instrument_pool, ["笛子", "二胡"]);
assert.deepEqual(patchedTimbreConfig.timbre_traits, ["气息感", "弦鸣"]);
assert.equal(patchedTimbreRounds[0].answer, "笛子");
assert.equal(patchedTimbreRounds[0].compare_with, "二胡");
assert.equal(
  resolveTimbreCaseJudgement(
    patchedTimbreRounds[0],
    "笛子",
    ["气息感"],
    "弦鸣",
    patchedTimbreConfig.evidence_required,
    true
  ).judgement,
  "solved"
);

const formState = formWorkflowState as StudentGameState;
const formConfig = mergeFormEntityExecutionConfig(formState, {
  form_type: "AB",
  answer_pattern: ["A", "B"]
});

assert.equal(formConfig.form_type, "ABA");
assert.deepEqual(formConfig.answer_pattern, ["A", "B", "A"]);
assert.equal(resolveFormRouteJudgement(["A", "B", "A"], formConfig.answer_pattern).correct, true);
assert.equal(resolveFormRouteJudgement(["A", "A", "B"], formConfig.answer_pattern).correct, false);

const compositionState = compositionWorkflowState as StudentGameState;
const compositionConfig = mergeCompositionEntityExecutionConfig(compositionState, {
  melody_cards: ["do", "mi"],
  required_elements: ["do"]
});
const compositionLogic = buildCompositionPuzzleLogicConfig(compositionConfig);
const pentatonicPhrase: CompositionPlacedCard[] = [
  { id: "quarter", label: "四分", rhythm: "quarter", pitches: ["C"], beats: 1 },
  { id: "quarter", label: "四分", rhythm: "quarter", pitches: ["D"], beats: 1 },
  { id: "quarter", label: "四分", rhythm: "quarter", pitches: ["E"], beats: 1 },
  { id: "quarter", label: "四分", rhythm: "quarter", pitches: ["G"], beats: 1 },
  { id: "quarter", label: "四分", rhythm: "quarter", pitches: ["A"], beats: 1 },
  { id: "quarter", label: "四分", rhythm: "quarter", pitches: ["A"], beats: 1 },
  { id: "quarter", label: "四分", rhythm: "quarter", pitches: ["A"], beats: 1 },
  { id: "quarter", label: "四分", rhythm: "quarter", pitches: ["A"], beats: 1 }
];
const compositionChecks = evaluateCompositionPuzzleChecks(compositionConfig, pentatonicPhrase, true, true);

assert.deepEqual(compositionConfig.melody_cards, ["do", "re", "mi", "sol", "la"]);
assert.deepEqual(compositionConfig.required_elements, ["do", "re", "mi", "sol", "la"]);
assert.deepEqual(compositionLogic.melody_cards, ["C", "D", "E", "G", "A"]);
assert.equal(compositionChecks.find((check) => check.id === "pitch_token_do")?.passed, true);
assert.equal(compositionChecks.find((check) => check.id === "pitch_token_re")?.passed, true);
assert.equal(compositionChecks.find((check) => check.id === "pitch_token_mi")?.passed, true);
assert.equal(compositionChecks.find((check) => check.id === "pitch_token_sol")?.passed, true);
assert.equal(compositionChecks.find((check) => check.id === "pitch_token_la")?.passed, true);

function assertWorkflowExecutionContract(state: StudentGameState) {
  const execution = resolveMusicEntityExecution(state);
  const executionPlan = state.workflow?.game_variant_spec?.execution_plan;
  assert.equal(state.workflow?.game_variant_spec?.contract_schema_version, "game_variant_spec_v2");
  assert.equal(execution.contract_schema_version, "game_variant_spec_v2");
  assertExecutionPlanMatch(execution.execution_plan, executionPlan);
  assertExecutionPlanMatch(state.workflow?.render_spec?.music_entity_execution?.execution_plan, executionPlan);
  assertExecutionPlanMatch(
    state.workflow?.frontend_handoff_contract?.presentation_inputs?.music_entity_execution?.execution_plan,
    executionPlan
  );
}

function assertExecutionPlanMatch(actual: unknown, expected: unknown) {
  const actualPlan = actual as Record<string, unknown>;
  const expectedPlan = expected as Record<string, unknown>;
  assert.equal(actualPlan.version, expectedPlan.version);
  assert.equal(actualPlan.template_id, expectedPlan.template_id);
  assert.equal(actualPlan.status, expectedPlan.status);
  assert.equal(actualPlan.entity_type, expectedPlan.entity_type);
  assert.equal(actualPlan.canonical_id, expectedPlan.canonical_id);
  assert.deepEqual(actualPlan.parameter_writes, expectedPlan.parameter_writes);
  assert.deepEqual(actualPlan.slot_writes, expectedPlan.slot_writes);
  assert.deepEqual(actualPlan.entity_application_writes, expectedPlan.entity_application_writes);
  assert.equal(actualPlan.requires_teacher_confirmation, expectedPlan.requires_teacher_confirmation);
  assert.equal(actualPlan.template_capability_status, expectedPlan.template_capability_status);
  assert.deepEqual(actualPlan.blocked_reasons ?? [], expectedPlan.blocked_reasons ?? []);
}
