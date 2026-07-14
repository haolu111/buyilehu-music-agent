import assert from "node:assert/strict";
import {
  buildCompositionPuzzleLogicConfig,
  evaluateCompositionPuzzleChecks,
  type CompositionPlacedCard,
  type CompositionPuzzleLogicConfig
} from "../src/student-game/compositionPuzzleLogic";
import {
  mergeCompositionEntityExecutionConfig,
  mergeFormEntityExecutionConfig,
  mergeMeterEntityExecutionConfig,
  mergePitchEntityExecutionConfig,
  mergeRhythmEntityExecutionConfig,
  mergeSolfegeEntityExecutionConfig,
  mergeTimbreEntityExecutionConfig,
  resolveEntitySlotBindings,
  resolveMusicEntityExecution,
  resolveVariantParameters
} from "../src/student-game/musicEntityExecution";
import { resolveFormRouteJudgement } from "../src/student-game/formTreasureLogic";
import { PitchLadderGameSystem } from "../src/student-game/pitchLadderSystem";
import { resolveRhythmRoundPlan } from "../src/student-game/rhythmEchoRoundPlan";
import { resolveSolfegeTargetShot } from "../src/student-game/solfegeTargetLogic";
import { resolveTimbreCaseJudgement } from "../src/student-game/timbreDetectiveLogic";
import type { StudentGameState } from "../src/student-game/types";

const state: StudentGameState = {
  workflow: {
    workflow_kind: "lesson_game",
    game_variant_spec: {
      version: "game_variant_spec_v1",
      template_id: "timbre_detective_core",
      music_entity: {
        canonical_id: "instrument_timbre",
        label: "乐器音色",
        entity_type: "timbre_set"
      },
      variant_parameters: {
        instrument_pool: ["笛子", "二胡"],
        timbre_traits: ["气息感", "弦鸣"]
      },
      slot_bindings: {
        "round_1.listen_clip": ["笛子", "二胡"]
      },
      entity_application: {
        template_id: "timbre_detective_core",
        canonical_id: "instrument_timbre",
        entity_type: "timbre_set",
        slot_bindings: {
          "timbre.comparison_pairs": [["笛子", "二胡"]]
        }
      }
    }
  }
};

assert.equal(resolveMusicEntityExecution(state).music_entity?.entity_type, "timbre_set");
assert.deepEqual(resolveVariantParameters(state).instrument_pool, ["笛子", "二胡"]);
assert.deepEqual(resolveEntitySlotBindings(state)["timbre.comparison_pairs"], [["笛子", "二胡"]]);

const renderSpecState: StudentGameState = {
  workflow: {
    workflow_kind: "lesson_game",
    render_spec: {
      music_entity_execution: {
        variant_parameters: { meter: "3/4", target_beats: [1] },
        entity_application: {
          entity_type: "meter",
          slot_bindings: { "meter.accent_pattern": ["strong", "weak", "weak"] }
        }
      }
    }
  }
};

assert.equal(resolveMusicEntityExecution(renderSpecState).entity_application?.entity_type, "meter");
assert.deepEqual(resolveVariantParameters(renderSpecState).target_beats, [1]);
assert.deepEqual(resolveEntitySlotBindings(renderSpecState)["meter.accent_pattern"], ["strong", "weak", "weak"]);

const staleRenderSpecState: StudentGameState = {
  workflow: {
    workflow_kind: "lesson_game",
    game_variant_spec: {
      contract_schema_version: "game_variant_spec_v2",
      variant_parameters: { meter: "3/4", target_beats: [1] },
      entity_application: {
        entity_type: "meter",
        slot_bindings: { "meter.accent_pattern": ["strong", "weak", "weak"] }
      }
    },
    render_spec: {
      music_entity_execution: {
        contract_schema_version: "stale_render_copy",
        variant_parameters: { meter: "2/4", target_beats: [2] },
        entity_application: {
          entity_type: "meter",
          slot_bindings: { "meter.accent_pattern": ["weak", "strong"] }
        }
      }
    }
  }
};

assert.equal(resolveMusicEntityExecution(staleRenderSpecState).contract_schema_version, "game_variant_spec_v2");
assert.deepEqual(resolveVariantParameters(staleRenderSpecState).target_beats, [1]);
assert.deepEqual(resolveEntitySlotBindings(staleRenderSpecState)["meter.accent_pattern"], ["strong", "weak", "weak"]);

const executionPlanState: StudentGameState = {
  workflow: {
    render_spec: {
      music_entity_execution: {
        contract_schema_version: "game_variant_spec_v2",
        variant_parameters: { meter: "4/4", target_beats: [1] },
        slot_bindings: { "meter.accent_pattern": ["strong", "weak", "weak", "weak"] },
        entity_application: {
          entity_type: "meter",
          game_parameters: { meter: "4/4" },
          slot_bindings: { "meter.accent_pattern": ["strong", "weak", "weak", "weak"] }
        },
        execution_plan: {
          version: "execution_plan_v1",
          status: "ready",
          parameter_writes: [
            { path: "variant_parameters.meter", value: "3/4" },
            { path: "variant_parameters.target_beats", value: [2] }
          ],
          slot_writes: [
            { path: "slot_bindings.meter.accent_pattern", value: ["weak", "strong", "weak"] }
          ],
          entity_application_writes: {
            game_parameters: { meter: "3/4", target_beats: [2] },
            slot_bindings: { "meter.accent_pattern": ["weak", "strong", "weak"] }
          }
        }
      }
    }
  }
};
assert.equal(resolveMusicEntityExecution(executionPlanState).contract_schema_version, "game_variant_spec_v2");
assert.equal(resolveMusicEntityExecution(executionPlanState).execution_plan?.status, "ready");
assert.deepEqual(resolveVariantParameters(executionPlanState).target_beats, [2]);
assert.deepEqual(resolveEntitySlotBindings(executionPlanState)["meter.accent_pattern"], ["weak", "strong", "weak"]);
const executionPlanMeterConfig = mergeMeterEntityExecutionConfig(executionPlanState, { meter: "2/4", beats_per_bar: 2 });
assert.equal(executionPlanMeterConfig.meter, "3/4");
assert.equal(executionPlanMeterConfig.beats_per_bar, 3);
assert.deepEqual(executionPlanMeterConfig.target_beats, [2]);
assert.deepEqual(executionPlanMeterConfig.accent_pattern, ["weak", "strong", "weak"]);

const timbreConfig = mergeTimbreEntityExecutionConfig(state, { skin_id: "studio_mixer" });
const timbreRounds = timbreConfig.timbre_rounds as Array<Record<string, unknown>>;
assert.deepEqual(timbreConfig.instrument_pool, ["笛子", "二胡"]);
assert.deepEqual(timbreConfig.timbre_traits, ["气息感", "弦鸣"]);
assert.equal(timbreConfig.mode, "compare_twins");
assert.equal(timbreRounds[0].target, "笛子");
assert.equal(timbreRounds[0].compare_with, "二胡");
assert.deepEqual(timbreRounds[0].evidence_answer, ["气息感"]);
assert.deepEqual(timbreRounds[0].contrast_evidence_answer, ["弦鸣"]);

const replacedTimbreState: StudentGameState = {
  config: {
    instrument_pool: ["木鱼", "三角铁"],
    timbre_traits: ["短促", "金属声"],
    timbre_rounds: [
      {
        id: "old_case",
        target: "木鱼",
        answer: "木鱼",
        compare_with: "三角铁",
        candidates: ["木鱼", "三角铁"],
        evidence_options: ["短促", "金属声"],
        evidence_answer: ["短促"],
        contrast_evidence_answer: ["金属声"],
        comparison_reason_required: true
      }
    ]
  },
  workflow: {
    game_variant_spec: {
      variant_parameters: {
        instrument_pool: ["笛子", "二胡"],
        timbre_traits: ["气息感", "擦弦感"]
      },
      entity_application: {
        template_id: "timbre_detective_core",
        entity_type: "timbre_set",
        game_parameters: {
          instrument_pool: ["笛子", "二胡"],
          timbre_traits: ["气息感", "擦弦感"]
        },
        slot_bindings: {
          "timbre.comparison_pairs": [["笛子", "二胡"]],
          "timbre.trait_targets": {
            "笛子": ["气息感"],
            "二胡": ["擦弦感"]
          }
        }
      },
      contract_schema_version: "game_variant_spec_v2"
    },
    render_spec: {
      music_entity_execution: {
        variant_parameters: {
          instrument_pool: ["木鱼", "三角铁"],
          timbre_traits: ["短促", "金属声"]
        },
        entity_application: {
          template_id: "timbre_detective_core",
          entity_type: "timbre_set",
          game_parameters: {
            instrument_pool: ["木鱼", "三角铁"],
            timbre_traits: ["短促", "金属声"]
          },
          slot_bindings: {
            "timbre.comparison_pairs": [["木鱼", "三角铁"]],
            "timbre.trait_targets": {
              "木鱼": ["短促"],
              "三角铁": ["金属声"]
            }
          }
        }
      }
    }
  }
};
const replacedTimbreConfig = mergeTimbreEntityExecutionConfig(replacedTimbreState, replacedTimbreState.config ?? {});
const replacedTimbreRounds = replacedTimbreConfig.timbre_rounds as Array<Record<string, unknown>>;
assert.deepEqual(replacedTimbreConfig.instrument_pool, ["笛子", "二胡"]);
assert.equal(replacedTimbreRounds[0].answer, "笛子");
assert.equal(replacedTimbreRounds[0].compare_with, "二胡");
assert.deepEqual(replacedTimbreRounds[0].evidence_answer, ["气息感"]);
assert.deepEqual(replacedTimbreRounds[0].contrast_evidence_answer, ["擦弦感"]);
assert.deepEqual((replacedTimbreConfig.clue_cases as Array<Record<string, unknown>>)[0], replacedTimbreRounds[0]);
assert.equal(
  resolveTimbreCaseJudgement(replacedTimbreRounds[0], "木鱼", ["短促"], "金属声", replacedTimbreConfig.evidence_required, true).judgement,
  "wrong",
  "old timbre case no longer judges as correct"
);
assert.equal(
  resolveTimbreCaseJudgement(replacedTimbreRounds[0], "笛子", ["气息感"], "金属声", replacedTimbreConfig.evidence_required, true).judgement,
  "evidence_missing",
  "replacement timbre case still requires the new contrast evidence"
);
assert.equal(
  resolveTimbreCaseJudgement(replacedTimbreRounds[0], "笛子", ["气息感"], "擦弦感", replacedTimbreConfig.evidence_required, true).judgement,
  "solved",
  "replacement timbre case solves with the new answer and evidence"
);

const meterConfig = mergeMeterEntityExecutionConfig(renderSpecState, { meter: "4/4", beats_per_bar: 4 });
assert.equal(meterConfig.meter, "3/4");
assert.equal(meterConfig.beats_per_bar, 3);
assert.deepEqual(meterConfig.target_beats, [1]);
assert.deepEqual(meterConfig.accent_pattern, ["strong", "weak", "weak"]);

const weakBeatMeterState: StudentGameState = {
  workflow: {
    render_spec: {
      music_entity_execution: {
        variant_parameters: { meter: "3/4" },
        entity_application: {
          slot_bindings: { "meter.accent_pattern": ["weak", "strong", "weak"] }
        }
      }
    }
  }
};
const weakBeatMeterConfig = mergeMeterEntityExecutionConfig(weakBeatMeterState, {});
assert.deepEqual(weakBeatMeterConfig.target_beats, [2]);

const rhythmState: StudentGameState = {
  workflow: {
    game_variant_spec: {
      variant_parameters: { pattern_steps: ["quarter", "rest", "eighth_pair"], round_count: 2 },
      slot_bindings: {
        "round_2.target_rhythm": ["syncopation", "quarter"],
        "rhythm.duration_beats": [1, 1, 1]
      },
      entity_application: {
        slot_bindings: {
          "rhythm.pattern_steps": ["quarter", "rest", "eighth_pair"]
        }
      }
    }
  }
};
const rhythmConfig = mergeRhythmEntityExecutionConfig(rhythmState, { pattern_steps: ["quarter"] });
assert.deepEqual(rhythmConfig.pattern_steps, ["quarter", "rest", "eighth_pair"]);
assert.equal(rhythmConfig.round_count, 2);
assert.deepEqual((rhythmConfig.round_patches as Record<string, unknown>)?.round_2, {
  pattern_steps: ["syncopation", "quarter"]
});

const pendingRhythmState: StudentGameState = {
  workflow: {
    game_variant_spec: {
      requires_teacher_confirmation: true,
      confirmation_reason: "节奏来自教师文本推断，请确认后作为游戏答案。",
      confirmation_gates: [
        {
          gate_type: "low_confidence_music_entity",
          entity_type: "rhythm_pattern",
          status: "pending",
          proposed_value: ["quarter", "rest", "eighth_pair", "syncopation"]
        }
      ],
      variant_parameters: {
        pattern_steps: ["quarter", "rest", "eighth_pair", "syncopation"],
        round_count: 3
      },
      slot_bindings: {
        "round_2.target_rhythm": ["syncopation", "quarter"]
      },
      entity_application: {
        requires_teacher_confirmation: true,
        confirmation_reason: "节奏来自教师文本推断，请确认后作为游戏答案。",
        game_parameters: {
          pattern_steps: ["quarter", "rest", "eighth_pair", "syncopation"]
        },
        slot_bindings: {
          "rhythm.pattern_steps": ["quarter", "rest", "eighth_pair", "syncopation"]
        }
      }
    }
  }
};
const pendingRhythmConfig = mergeRhythmEntityExecutionConfig(pendingRhythmState, { pattern_steps: ["quarter", "quarter"] });
assert.deepEqual(pendingRhythmConfig.pattern_steps, ["quarter", "quarter"]);
assert.equal(pendingRhythmConfig.round_count, 3);
assert.equal(pendingRhythmConfig.music_entity_confirmation_required, true);
assert.equal(pendingRhythmConfig.music_entity_confirmation_reason, "节奏来自教师文本推断，请确认后作为游戏答案。");
assert.deepEqual(pendingRhythmConfig.pending_music_entity_value, ["quarter", "rest", "eighth_pair", "syncopation"]);
assert.equal(pendingRhythmConfig.round_patches, undefined);

const pendingRhythmWithBasePlan = mergeRhythmEntityExecutionConfig(pendingRhythmState, {
  pattern_steps: ["quarter", "quarter"],
  pattern_timeline: [
    { step: "quarter", label: "四", time_beats: 0, duration_beats: 1, hit_required: true },
    { step: "quarter", label: "四", time_beats: 1, duration_beats: 1, hit_required: true }
  ],
  round_patches: {
    round_2: { pattern_steps: ["quarter", "rest"] }
  }
});
assert.deepEqual(pendingRhythmWithBasePlan.pattern_steps, ["quarter", "quarter"]);
assert.deepEqual(pendingRhythmWithBasePlan.pattern_timeline, [
  { step: "quarter", label: "四", time_beats: 0, duration_beats: 1, hit_required: true },
  { step: "quarter", label: "四", time_beats: 1, duration_beats: 1, hit_required: true }
]);
assert.deepEqual(pendingRhythmWithBasePlan.round_patches, {
  round_2: { pattern_steps: ["quarter", "rest"] }
});

const confirmedRhythmState: StudentGameState = {
  workflow: {
    game_variant_spec: {
      requires_teacher_confirmation: false,
      confirmation_gates: [
        {
          gate_type: "low_confidence_music_entity",
          entity_type: "rhythm_pattern",
          status: "confirmed",
          proposed_value: ["quarter", "rest", "eighth_pair", "syncopation"],
          confirmed_value: ["quarter", "rest", "eighth_pair", "syncopation"]
        }
      ],
      variant_parameters: {
        pattern_steps: ["quarter", "rest", "eighth_pair", "syncopation"]
      },
      entity_application: {
        requires_teacher_confirmation: false,
        game_parameters: {
          pattern_steps: ["quarter", "rest", "eighth_pair", "syncopation"]
        },
        slot_bindings: {
          "rhythm.pattern_steps": ["quarter", "rest", "eighth_pair", "syncopation"]
        }
      }
    }
  }
};
const confirmedRhythmConfig = mergeRhythmEntityExecutionConfig(confirmedRhythmState, { pattern_steps: ["quarter", "quarter"] });
assert.deepEqual(confirmedRhythmConfig.pattern_steps, ["quarter", "rest", "eighth_pair", "syncopation"]);
assert.equal(confirmedRhythmConfig.music_entity_confirmation_required, undefined);

const replacedRhythmRenderState: StudentGameState = {
  workflow: {
    game_variant_spec: {
      contract_schema_version: "game_variant_spec_v2",
      variant_parameters: { pattern_steps: ["quarter", "rest", "eighth_pair"], round_count: 2 },
      entity_application: {
        game_parameters: { pattern_steps: ["quarter", "rest", "eighth_pair"], round_count: 2 },
        slot_bindings: {
          "rhythm.pattern_steps": ["quarter", "rest", "eighth_pair"],
          "rhythm.duration_beats": [1, 1, 1]
        }
      }
    },
    render_spec: {
      music_entity_execution: {
        contract_schema_version: "stale_render_copy",
        variant_parameters: { pattern_steps: ["quarter", "quarter"], round_count: 1 },
        entity_application: {
          template_id: "rhythm_echo_core",
          entity_type: "rhythm_pattern",
          game_parameters: { pattern_steps: ["quarter", "quarter"], round_count: 1 },
          slot_bindings: {
            "rhythm.pattern_steps": ["quarter", "quarter"]
          }
        }
      }
    }
  }
};
const replacedRhythmConfig = mergeRhythmEntityExecutionConfig(replacedRhythmRenderState, {
  pattern_steps: ["quarter", "quarter"],
  round_count: 1
});
const replacedRhythmPlan = resolveRhythmRoundPlan({ ...replacedRhythmConfig, active_round: 1 });
assert.deepEqual(replacedRhythmConfig.pattern_steps, ["quarter", "rest", "eighth_pair"]);
assert.equal(replacedRhythmConfig.round_count, 2);
assert.deepEqual(replacedRhythmPlan.pattern_steps, ["quarter", "rest", "eighth_pair"]);
assert.deepEqual(
  replacedRhythmPlan.pattern_timeline.map((item) => ({ step: item.step, hit_required: item.hit_required })),
  [
    { step: "quarter", hit_required: true },
    { step: "rest", hit_required: false },
    { step: "eighth", hit_required: true },
    { step: "eighth", hit_required: true }
  ]
);

const formState: StudentGameState = {
  workflow: {
    game_variant_spec: {
      variant_parameters: { form_type: "ABA" },
      entity_application: {
        slot_bindings: {
          "form.answer_pattern": ["A", "B", "A"],
          "form.timeline_segments": [
            { id: "a1", label: "A", bars: 4 },
            { id: "b", label: "B", bars: 4 },
            { id: "a2", label: "A", bars: 4 }
          ]
        }
      }
    }
  }
};
const formConfig = mergeFormEntityExecutionConfig(formState, { form_type: "AB" });
assert.equal(formConfig.form_type, "ABA");
assert.deepEqual(formConfig.answer_pattern, ["A", "B", "A"]);
assert.equal((formConfig.timeline_segments as Array<Record<string, unknown>>)[1].label, "B");

const replacedFormState: StudentGameState = {
  config: {
    form_type: "ABA",
    answer_pattern: ["A", "B", "A"],
    structure_cards: [
      { id: "old_A", label: "A", name: "A 段" },
      { id: "old_B", label: "B", name: "B 段" }
    ],
    timeline_segments: [
      { id: "old_a1", label: "A", bars: 4 },
      { id: "old_b", label: "B", bars: 4 },
      { id: "old_a2", label: "A", bars: 4 }
    ]
  },
  workflow: {
    game_variant_spec: {
      contract_schema_version: "game_variant_spec_v2",
      variant_parameters: { form_type: "ABAC", answer_pattern: ["A", "B", "A", "C"] },
      entity_application: {
        template_id: "form_treasure_core",
        entity_type: "form_structure",
        game_parameters: { form_type: "ABAC" },
        slot_bindings: {
          "form.answer_pattern": ["A", "B", "A", "C"],
          "form.timeline_segments": [
            { id: "new_a1", label: "A", bars: 4 },
            { id: "new_b", label: "B", bars: 4 },
            { id: "new_a2", label: "A", bars: 4 },
            { id: "new_c", label: "C", bars: 4 }
          ]
        }
      }
    },
    render_spec: {
      music_entity_execution: {
        contract_schema_version: "stale_render_copy",
        variant_parameters: { form_type: "ABA", answer_pattern: ["A", "B", "A"] },
        entity_application: {
          template_id: "form_treasure_core",
          entity_type: "form_structure",
          game_parameters: { form_type: "ABA" },
          slot_bindings: {
            "form.answer_pattern": ["A", "B", "A"]
          }
        }
      }
    }
  }
};
const replacedFormConfig = mergeFormEntityExecutionConfig(replacedFormState, replacedFormState.config ?? {});
assert.equal(replacedFormConfig.form_type, "ABAC");
assert.deepEqual(replacedFormConfig.answer_pattern, ["A", "B", "A", "C"]);
assert.deepEqual((replacedFormConfig.structure_cards as Array<Record<string, unknown>>).map((item) => item.label), ["A", "B", "C"]);
assert.equal((replacedFormConfig.timeline_segments as Array<Record<string, unknown>>)[3].label, "C");
assert.equal(resolveFormRouteJudgement(["A", "B", "A"], replacedFormConfig.answer_pattern).correct, false);
assert.equal(resolveFormRouteJudgement(["A", "B", "A", "B"], replacedFormConfig.answer_pattern).correct, false);
assert.equal(resolveFormRouteJudgement(["A", "B", "A", "C"], replacedFormConfig.answer_pattern).correct, true);

const compositionState: StudentGameState = {
  workflow: {
    game_variant_spec: {
      variant_parameters: {
        melody_cards: ["do", "re", "mi", "sol", "la"],
        required_elements: ["do", "sol"]
      },
      entity_application: {
        slot_bindings: {
          "composition.constraint_checks": [
            { id: "pitch_do", label: "必须用 do", kind: "pitch_token", target: "do", required: true }
          ]
        }
      }
    }
  }
};
const compositionConfig = mergeCompositionEntityExecutionConfig(compositionState, { melody_cards: ["do", "mi"] });
assert.deepEqual(compositionConfig.melody_cards, ["do", "re", "mi", "sol", "la"]);
assert.deepEqual(compositionConfig.required_elements, ["do", "sol"]);
assert.equal((compositionConfig.constraint_checks as Array<Record<string, unknown>>)[0].target, "do");

const replacedCompositionState: StudentGameState = {
  config: {
    melody_cards: ["C", "D"],
    rhythm_cards: ["quarter"],
    required_elements: ["C"],
    constraint_checks: [
      { id: "old_pitch_c", label: "必须用 C", kind: "pitch_token", target: "C", required: true }
    ]
  },
  workflow: {
    game_variant_spec: {
      contract_schema_version: "game_variant_spec_v2",
      variant_parameters: {
        melody_cards: ["do", "sol", "la"],
        rhythm_cards: [{ id: "eighth_pair", label: "二八", beats: 1 }],
        required_elements: ["la", "eighth_pair"]
      },
      entity_application: {
        template_id: "composition_puzzle_core",
        entity_type: "composition_material_set",
        game_parameters: {
          melody_cards: ["do", "sol", "la"],
          rhythm_cards: [{ id: "eighth_pair", label: "二八", beats: 1 }],
          required_elements: ["la", "eighth_pair"]
        },
        slot_bindings: {
          "composition.constraint_checks": [
            { id: "need_la", label: "必须用 la", kind: "pitch_token", target: "la", required: true },
            { id: "need_eighth_pair", label: "必须用 二八", kind: "rhythm_token", target: "eighth_pair", required: true }
          ]
        }
      }
    },
    render_spec: {
      music_entity_execution: {
        contract_schema_version: "stale_render_copy",
        variant_parameters: {
          melody_cards: ["C", "D"],
          rhythm_cards: ["quarter"],
          required_elements: ["C"]
        },
        entity_application: {
          template_id: "composition_puzzle_core",
          entity_type: "composition_material_set",
          game_parameters: {
            melody_cards: ["C", "D"],
            rhythm_cards: ["quarter"],
            required_elements: ["C"]
          },
          slot_bindings: {
            "composition.constraint_checks": [
              { id: "old_pitch_c", label: "必须用 C", kind: "pitch_token", target: "C", required: true }
            ]
          }
        }
      }
    }
  }
};
const replacedCompositionConfig = mergeCompositionEntityExecutionConfig(replacedCompositionState, replacedCompositionState.config ?? {}) as CompositionPuzzleLogicConfig;
assert.deepEqual(replacedCompositionConfig.melody_cards, ["do", "sol", "la"]);
assert.deepEqual((replacedCompositionConfig.rhythm_cards as Array<Record<string, unknown>>).map((item) => item.id), ["eighth_pair"]);
assert.deepEqual(replacedCompositionConfig.required_elements, ["la", "eighth_pair"]);
assert.deepEqual(buildCompositionPuzzleLogicConfig(replacedCompositionConfig as Record<string, unknown>).melody_cards, ["C", "G", "A"]);
const oldCompositionPhrase: CompositionPlacedCard[] = [
  { id: "quarter_C", label: "四分", rhythm: "quarter", pitch: "C", beats: 1, pitches: ["C"] }
];
const newCompositionPhrase: CompositionPlacedCard[] = [
  { id: "eighth_pair_la", label: "二八", rhythm: "eighth_pair", pitch: "la", beats: 1, pitches: ["la", "sol"] }
];
const oldCompositionChecks = evaluateCompositionPuzzleChecks(replacedCompositionConfig, oldCompositionPhrase, true, true);
const newCompositionChecks = evaluateCompositionPuzzleChecks(replacedCompositionConfig, newCompositionPhrase, true, true);
assert.equal(oldCompositionChecks.find((check) => check.id === "need_la")?.passed, false);
assert.equal(oldCompositionChecks.find((check) => check.id === "need_eighth_pair")?.passed, false);
assert.equal(newCompositionChecks.find((check) => check.id === "need_la")?.passed, true);
assert.equal(newCompositionChecks.find((check) => check.id === "need_eighth_pair")?.passed, true);

const pitchState: StudentGameState = {
  workflow: {
    game_variant_spec: {
      variant_parameters: { pitch_range: ["do", "mi", "sol"] },
      slot_bindings: {
        "round_2.target_melody": ["sol", "mi", "do"]
      }
    }
  }
};
const pitchConfig = mergePitchEntityExecutionConfig(pitchState, {});
assert.deepEqual(pitchConfig.pitch_range, ["do", "mi", "sol"]);
assert.deepEqual((pitchConfig.pitch_rounds as Array<Record<string, unknown>>)[1].sequence, ["sol", "mi", "do"]);
assert.equal((pitchConfig.pitch_rounds as Array<Record<string, unknown>>)[1].answer, "lower");

const chromaticPitchState: StudentGameState = {
  workflow: {
    game_variant_spec: {
      slot_bindings: {
        "round_1.target_melody": ["do", "#1", "re", "♯2", "mi"]
      }
    }
  }
};
const chromaticPitchConfig = mergePitchEntityExecutionConfig(chromaticPitchState, {});
assert.deepEqual(
  (chromaticPitchConfig.pitch_rounds as Array<Record<string, unknown>>)[0].midi_offsets,
  [0, 1, 2, 3, 4],
  "变化音旋律应使用十二平均律半音偏移"
);

const replacedPitchState: StudentGameState = {
  config: {
    pitch_range: ["do", "re"],
    pitch_rounds: [{ id: "old_route", sequence: ["do", "re"], labels: ["C", "D"], answer: ["do", "re"] }],
    current_mode: "melody_path"
  },
  workflow: {
    game_variant_spec: {
      contract_schema_version: "game_variant_spec_v2",
      variant_parameters: {
        pitch_range: ["mi", "sol", "do_high"],
        current_mode: "melody_path"
      },
      entity_application: {
        template_id: "pitch_ladder_core",
        entity_type: "pitch_motion",
        game_parameters: {
          pitch_range: ["mi", "sol", "do_high"],
          current_mode: "melody_path"
        },
        slot_bindings: {
          "round_1.target_melody": ["mi", "sol", "do_high"]
        }
      }
    },
    render_spec: {
      music_entity_execution: {
        contract_schema_version: "stale_render_copy",
        variant_parameters: {
          pitch_range: ["do", "re"],
          pitch_rounds: [{ id: "old_route", sequence: ["do", "re"], labels: ["C", "D"], answer: ["do", "re"] }]
        },
        entity_application: {
          template_id: "pitch_ladder_core",
          entity_type: "pitch_motion",
          game_parameters: {
            pitch_range: ["do", "re"]
          },
          slot_bindings: {
            "round_1.target_melody": ["do", "re"]
          }
        }
      }
    }
  }
};
const replacedPitchConfig = mergePitchEntityExecutionConfig(replacedPitchState, replacedPitchState.config ?? {});
const replacedPitchRounds = replacedPitchConfig.pitch_rounds as Array<Record<string, unknown>>;
assert.deepEqual(replacedPitchConfig.pitch_range, ["mi", "sol", "do_high"]);
assert.deepEqual(replacedPitchRounds[0].sequence, ["mi", "sol", "do_high"]);
assert.deepEqual(replacedPitchRounds[0].answer, ["mi", "sol", "do_high"]);
const replacedPitchSystem = new PitchLadderGameSystem({
  rounds: replacedPitchRounds,
  energyMax: 100,
  mistakeLimit: 3
});
replacedPitchSystem.listen();
replacedPitchSystem.enterPlaying("路线");
assert.equal(replacedPitchSystem.chooseNode("do").type, "mistake", "old pitch route no longer judges as correct");
replacedPitchSystem.reset();
replacedPitchSystem.listen();
replacedPitchSystem.enterPlaying("路线");
assert.equal(replacedPitchSystem.chooseNode("mi").type, "partial", "replacement pitch route first note is accepted");
assert.equal(replacedPitchSystem.chooseNode("sol").type, "partial", "replacement pitch route middle note is accepted");
assert.equal(replacedPitchSystem.chooseNode("do_high").type, "round_clear", "replacement pitch route reaches sing-back checkpoint");

const solfegeState: StudentGameState = {
  workflow: {
    game_variant_spec: {
      variant_parameters: { target_solfege: ["do", "re", "mi"] },
      slot_bindings: {
        "round_2.target_solfege": ["mi", "re"]
      }
    }
  }
};
const solfegeConfig = mergeSolfegeEntityExecutionConfig(solfegeState, {});
assert.deepEqual(solfegeConfig.target_solfege, ["do", "re", "mi"]);
assert.deepEqual((solfegeConfig.solfege_rounds as Array<Record<string, unknown>>)[1].answer, ["mi", "re"]);

const chromaticSolfegeState: StudentGameState = {
  workflow: {
    game_variant_spec: {
      slot_bindings: {
        "round_1.target_solfege": ["♯4", "♭5", "ti"]
      }
    }
  }
};
const chromaticSolfegeConfig = mergeSolfegeEntityExecutionConfig(chromaticSolfegeState, {});
assert.deepEqual(
  (chromaticSolfegeConfig.solfege_rounds as Array<Record<string, unknown>>)[0].midi_offsets,
  [6, 6, 11],
  "同音异名应保留序列但共用同一半音偏移"
);

const replacedSolfegeState: StudentGameState = {
  config: {
    target_solfege: ["do", "re"],
    solfege_rounds: [{ id: "old_target", sequence: ["do", "re"], labels: ["C", "D"], answer: ["do", "re"] }]
  },
  workflow: {
    game_variant_spec: {
      contract_schema_version: "game_variant_spec_v2",
      variant_parameters: {
        target_solfege: ["mi", "sol", "la"],
        current_mode: "target_chain"
      },
      entity_application: {
        template_id: "solfege_target_core",
        entity_type: "solfege_set",
        game_parameters: {
          target_solfege: ["mi", "sol", "la"],
          current_mode: "target_chain"
        },
        slot_bindings: {
          "round_1.target_solfege": ["mi", "sol", "la"]
        }
      }
    },
    render_spec: {
      music_entity_execution: {
        contract_schema_version: "stale_render_copy",
        variant_parameters: {
          target_solfege: ["do", "re"],
          solfege_rounds: [{ id: "old_target", sequence: ["do", "re"], labels: ["C", "D"], answer: ["do", "re"] }]
        },
        entity_application: {
          template_id: "solfege_target_core",
          entity_type: "solfege_set",
          game_parameters: {
            target_solfege: ["do", "re"]
          },
          slot_bindings: {
            "round_1.target_solfege": ["do", "re"]
          }
        }
      }
    }
  }
};
const replacedSolfegeConfig = mergeSolfegeEntityExecutionConfig(replacedSolfegeState, replacedSolfegeState.config ?? {});
const replacedSolfegeRounds = replacedSolfegeConfig.solfege_rounds as Array<Record<string, unknown>>;
assert.deepEqual(replacedSolfegeConfig.target_solfege, ["mi", "sol", "la"]);
assert.deepEqual(replacedSolfegeRounds[0].sequence, ["mi", "sol", "la"]);
assert.deepEqual(replacedSolfegeRounds[0].answer, ["mi", "sol", "la"]);
assert.equal(
  resolveSolfegeTargetShot(replacedSolfegeRounds[0].answer, ["do"], "do").ok,
  false,
  "old solfege target no longer judges as correct"
);
assert.equal(
  resolveSolfegeTargetShot(replacedSolfegeRounds[0].answer, ["mi"], "mi").ok,
  true,
  "replacement solfege first target is accepted"
);
assert.equal(
  resolveSolfegeTargetShot(replacedSolfegeRounds[0].answer, ["mi", "sol"], "sol").completed,
  false,
  "replacement solfege chain waits for the final target"
);
assert.equal(
  resolveSolfegeTargetShot(replacedSolfegeRounds[0].answer, ["mi", "sol", "la"], "la").completed,
  true,
  "replacement solfege chain reaches sing-back checkpoint"
);
