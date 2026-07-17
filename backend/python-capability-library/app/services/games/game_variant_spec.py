# 基于核心模板生成某一节课专属的游戏实例规格
from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.services.games.game_template_registry import get_game_template
from app.services.materials.music_element_resolver import retrieve_music_element_candidates, retrieve_music_element_entities


TEMPLATE_CAPABILITY_VERSION = "template_capability_v2"
GAME_VARIANT_SPEC_VERSION = "game_variant_spec_v1"
GAME_VARIANT_SPEC_CONTRACT_SCHEMA_VERSION = "game_variant_spec_v2"
MUSIC_ENTITY_AUTHORED_PARAMETERS = {
    "pattern_steps",
    "target_beats",
    "pitch_range",
    "target_solfege",
    "instrument_pool",
    "timbre_traits",
    "form_type",
    "melody_cards",
    "rhythm_cards",
    "required_elements",
}
COMMON_LOCKED_TEMPLATE_FIELDS = [
    "config.template_id",
    "config.engine",
    "config.scene_id",
    "config.runtime_shell",
    "config.runtime_component",
    "instance.template_id",
    "template_id",
    "engine",
    "scene_id",
    "runtime_shell",
    "runtime_component",
    "workflow_kind",
]
COMMON_WRITABLE_LESSON_SLOTS = [
    "lesson_contract.objective",
    "lesson_contract.stage",
    "lesson_contract.music_focus",
    "lesson_contract.material_anchor",
    "lesson_contract.student_must",
    "lesson_contract.transfer",
    "student_task.listen",
    "student_task.do",
    "student_task.pass",
]
COMMON_TEACHER_CONFIRMATION_FIELDS = [
    "source_clip",
    "audio_clip_url",
    "source_audio_url",
    "low_confidence_music_entity",
    "teacher_confirmation_card",
]
SUPPORTED_ENTITY_TYPES_BY_TEMPLATE = {
    "beat_guardian_core": ["meter"],
    "rhythm_echo_core": ["rhythm_pattern"],
    "pitch_ladder_core": ["pitch_motion", "solfege_set"],
    "solfege_target_core": ["solfege_set", "pitch_motion"],
    "timbre_detective_core": ["timbre_set", "source_clip"],
    "form_treasure_core": ["form_structure", "source_clip"],
    "composition_puzzle_core": ["scale", "composition_material", "rhythm_pattern", "pitch_motion"],
}
MODE_ALLOWED_VALUES = {
    "beat_guardian_core": ["beat_defense", "strong_beat_guard", "meter_gate"],
    "rhythm_echo_core": ["echo_tap", "echo_body_percussion", "echo_chain"],
    "pitch_ladder_core": ["high_low_steps", "solfege_ladder", "melody_climb"],
    "solfege_target_core": ["listen_and_hit", "aim_and_sing", "target_chain"],
    "timbre_detective_core": ["instrument_clue", "family_sorting", "compare_twins"],
    "form_treasure_core": ["aba_treasure", "rondo_treasure", "repeat_contrast"],
    "composition_puzzle_core": ["rhythm_puzzle_composition", "melody_puzzle_creation", "melody_rhythm_puzzle"],
}
PARAMETER_CONSTRAINTS = {
    "difficulty": {"type": "enum", "allowed_values": ["L1", "L2", "L3", "L4", "L5"]},
    "bpm": {"type": "number", "min": 48, "max": 160},
    "round_count": {"type": "integer", "min": 1, "max": 12},
    "bars_per_round": {"type": "integer", "min": 1, "max": 8},
    "notes_per_round": {"type": "integer", "min": 1, "max": 8},
    "choices_per_round": {"type": "integer", "min": 2, "max": 8},
    "section_length_bars": {"type": "integer", "min": 1, "max": 32},
    "phrase_length_bars": {"type": "integer", "min": 1, "max": 8},
    "sing_back_required": {"type": "boolean"},
    "meter": {"type": "enum", "allowed_values": ["2/4", "3/4", "4/4"]},
    "target_beats": {"type": "integer_list", "min_items": 1, "max_items": 4, "item_min": 1, "item_max": 4},
    "pattern_steps": {
        "type": "enum_list",
        "min_items": 1,
        "max_items": 16,
        "allowed_values": ["quarter", "eighth_pair", "rest", "half", "whole", "dotted_quarter", "syncopation", "sixteenth_four"],
    },
    "pitch_range": {"type": "string_list", "min_items": 2, "max_items": 12},
    "target_solfege": {"type": "string_list", "min_items": 1, "max_items": 12},
    "tonic": {"type": "string", "allowed_values": ["C", "D", "E", "F", "G", "A", "B"]},
    "scale_type": {"type": "string", "allowed_values": ["major", "minor", "major_pentatonic", "chinese_pentatonic"]},
    "instrument_pool": {"type": "string_list", "min_items": 1, "max_items": 8},
    "timbre_traits": {"type": "string_list", "min_items": 1, "max_items": 10},
    "form_type": {"type": "string", "allowed_values": ["ABA", "AABA", "AB", "回旋", "重复对比"]},
    "hint_mode": {"type": "string", "allowed_values": ["guided", "minimal", "none"]},
    "melody_cards": {"type": "string_list", "min_items": 1, "max_items": 12},
    "rhythm_cards": {"type": "string_list", "min_items": 1, "max_items": 12},
    "required_elements": {"type": "string_list", "min_items": 1, "max_items": 12},
    "constraint_profile": {"type": "string", "allowed_values": ["balanced", "guided", "challenge"]},
    "skin_id": {"type": "string"},
}

TEMPLATE_CAPABILITIES: dict[str, dict[str, Any]] = {
    "beat_guardian_core": {
        "suitable_music_elements": ["强弱拍", "强弱规律", "稳定拍", "拍号", "二拍子", "三拍子", "四拍子", "进入时机"],
        "required_slots": ["round_1.answer_sequence", "round_1.score_phrase"],
        "variant_parameters": ["meter", "target_beats", "bpm", "round_count", "difficulty", "skin_id"],
        "writable_variant_parameters": ["meter", "target_beats", "bpm", "round_count", "difficulty", "skin_id", "mode"],
        "writable_slot_bindings": ["meter.accent_pattern", "meter.beat_count"],
        "rejected_variant_parameters": ["instrument_pool", "timbre_traits", "form_type", "melody_cards", "required_elements"],
        "not_suitable_for": ["音色听辨", "曲式结构排序", "自由旋律创编"],
        "adaptable_mechanics": ["强拍守卫", "小组进入挑战", "身体律动拍点"],
    },
    "rhythm_echo_core": {
        "suitable_music_elements": ["节奏型", "切分节奏", "休止节奏", "附点节奏", "时值"],
        "required_slots": ["round_1.target_rhythm", "round_1.playback_tokens"],
        "variant_parameters": ["pattern_steps", "bpm", "bars_per_round", "round_count", "difficulty", "skin_id"],
        "writable_variant_parameters": ["pattern_steps", "bpm", "bars_per_round", "round_count", "difficulty", "skin_id"],
        "writable_slot_bindings": ["rhythm.pattern_steps", "rhythm.duration_beats", "round_*.target_rhythm"],
        "rejected_variant_parameters": ["instrument_pool", "timbre_traits", "form_type", "pitch_range", "target_solfege", "melody_cards", "required_elements"],
        "not_suitable_for": ["音色听辨", "曲式结构排序", "纯音高路线"],
        "adaptable_mechanics": ["节奏复刻", "节奏接龙", "身体打击乐", "听后排序"],
    },
    "pitch_ladder_core": {
        "suitable_music_elements": ["音高高低", "旋律走向", "级进", "跳进"],
        "required_slots": ["round_1.target_melody", "round_1.playback_tokens"],
        "variant_parameters": ["pitch_range", "notes_per_round", "tonic", "scale_type", "difficulty", "skin_id"],
        "writable_variant_parameters": ["pitch_range", "notes_per_round", "tonic", "scale_type", "difficulty", "skin_id", "round_count"],
        "writable_slot_bindings": ["round_*.target_melody"],
        "rejected_variant_parameters": ["instrument_pool", "timbre_traits", "form_type", "pattern_steps"],
        "not_suitable_for": ["音色听辨", "强弱拍守卫"],
        "adaptable_mechanics": ["旋律爬梯", "路线选择", "模唱复盘"],
    },
    "solfege_target_core": {
        "suitable_music_elements": ["唱名", "听音定位", "模唱确认"],
        "required_slots": ["round_1.target_solfege", "round_1.playback_tokens"],
        "variant_parameters": ["target_solfege", "notes_per_round", "sing_back_required", "difficulty", "skin_id"],
        "writable_variant_parameters": ["target_solfege", "notes_per_round", "sing_back_required", "difficulty", "skin_id", "round_count"],
        "writable_slot_bindings": ["round_*.target_solfege"],
        "rejected_variant_parameters": ["instrument_pool", "timbre_traits", "form_type", "pattern_steps"],
        "not_suitable_for": ["曲式结构排序", "纯节拍强弱"],
        "adaptable_mechanics": ["唱名打靶", "听音击中", "唱回确认"],
    },
    "timbre_detective_core": {
        "suitable_music_elements": ["音色听辨", "乐器识别", "乐器家族"],
        "required_slots": ["round_1.listen_clip", "round_1.evidence_prompt"],
        "variant_parameters": ["instrument_pool", "timbre_traits", "choices_per_round", "difficulty", "skin_id"],
        "writable_variant_parameters": ["instrument_pool", "timbre_traits", "choices_per_round", "difficulty", "skin_id", "mode"],
        "writable_slot_bindings": ["timbre.comparison_pairs", "timbre.trait_targets"],
        "rejected_variant_parameters": ["pattern_steps", "pitch_range", "target_solfege", "form_type", "melody_cards"],
        "not_suitable_for": ["节奏复刻", "音高路线"],
        "adaptable_mechanics": ["音色侦探", "证据推理", "乐器家族分类"],
    },
    "form_treasure_core": {
        "suitable_music_elements": ["曲式结构", "ABA", "重复对比", "回旋", "段落"],
        "required_slots": ["round_1.form_answer", "section_a.listen_clip"],
        "variant_parameters": ["form_type", "section_length_bars", "hint_mode", "difficulty", "skin_id"],
        "writable_variant_parameters": ["form_type", "section_length_bars", "hint_mode", "difficulty", "skin_id"],
        "writable_slot_bindings": ["form.answer_pattern", "form.timeline_segments", "segment_*.form_label"],
        "rejected_variant_parameters": ["pattern_steps", "instrument_pool", "timbre_traits", "pitch_range", "target_solfege"],
        "not_suitable_for": ["单一节奏复刻", "音色猜谜"],
        "adaptable_mechanics": ["曲式寻宝", "段落排序", "主题再现路线"],
    },
    "composition_puzzle_core": {
        "suitable_music_elements": ["五声音阶", "节奏创编", "旋律创编", "素材卡创编"],
        "required_slots": ["round_1.material_cards", "round_1.constraint_checks"],
        "variant_parameters": ["melody_cards", "rhythm_cards", "constraint_profile", "phrase_length_bars", "difficulty", "skin_id"],
        "writable_variant_parameters": ["melody_cards", "rhythm_cards", "required_elements", "constraint_profile", "phrase_length_bars", "difficulty", "skin_id", "mode"],
        "writable_slot_bindings": ["composition.scale_degrees", "composition.constraint_checks"],
        "rejected_variant_parameters": ["instrument_pool", "timbre_traits", "form_type"],
        "not_suitable_for": ["实时音色听辨", "强拍反应闯关"],
        "adaptable_mechanics": ["旋律拼图", "节奏拼图", "约束创编", "试听修正"],
    },
}


def template_capability_profile(template_id: str) -> dict[str, Any]:
    template_id = str(template_id or "").strip()
    template = get_game_template(template_id) or {}
    profile = deepcopy(TEMPLATE_CAPABILITIES.get(template_id, {}))
    writable_parameters = profile.get("writable_variant_parameters", profile.get("variant_parameters", []))
    rejected_parameters = profile.get("rejected_variant_parameters", [])
    return {
        "version": TEMPLATE_CAPABILITY_VERSION,
        "template_id": template_id,
        "template_label": template.get("label", ""),
        "runtime_status": template.get("runtime_status", ""),
        "supported_entity_types": SUPPORTED_ENTITY_TYPES_BY_TEMPLATE.get(template_id, []),
        "suitable_music_elements": profile.get("suitable_music_elements", []),
        "required_slots": profile.get("required_slots", []),
        "variant_parameters": profile.get("variant_parameters", []),
        "variant_parameter_constraints": _variant_parameter_constraints(template_id, writable_parameters),
        "writable_variant_parameters": writable_parameters,
        "writable_slot_bindings": profile.get("writable_slot_bindings", profile.get("required_slots", [])),
        "writable_lesson_slots": _writable_lesson_slots(template_id, profile),
        "locked_template_fields": COMMON_LOCKED_TEMPLATE_FIELDS,
        "teacher_confirmation_fields": _teacher_confirmation_fields(template_id),
        "rejected_variant_parameters": profile.get("rejected_variant_parameters", []),
        "refusal_reasons": _refusal_reasons(template_id, rejected_parameters),
        "adaptable_mechanics": profile.get("adaptable_mechanics", []),
        "not_suitable_for": profile.get("not_suitable_for", []),
    }


def _variant_parameter_constraints(template_id: str, writable_parameters: list[str]) -> dict[str, dict[str, Any]]:
    constraints: dict[str, dict[str, Any]] = {}
    for parameter in writable_parameters:
        if parameter == "mode":
            constraints[parameter] = {"type": "enum", "allowed_values": MODE_ALLOWED_VALUES.get(template_id, [])}
        else:
            constraints[parameter] = deepcopy(PARAMETER_CONSTRAINTS.get(parameter, {"type": "any"}))
    return constraints


def _writable_lesson_slots(template_id: str, profile: dict[str, Any]) -> list[str]:
    slots = list(COMMON_WRITABLE_LESSON_SLOTS)
    slots.extend(f"game_slot.{slot}" for slot in profile.get("required_slots", []))
    slots.extend(f"music_entity.{slot}" for slot in profile.get("writable_slot_bindings", []))
    return slots


def _teacher_confirmation_fields(template_id: str) -> list[str]:
    fields = list(COMMON_TEACHER_CONFIRMATION_FIELDS)
    if template_id in {"timbre_detective_core", "form_treasure_core"}:
        fields.extend(["audio_answer_boundary", "audio_evidence_label"])
    if template_id in {"rhythm_echo_core", "pitch_ladder_core", "solfege_target_core", "beat_guardian_core"}:
        fields.extend(["semantic_text_candidate", "material_conflict"])
    return fields


def _refusal_reasons(template_id: str, rejected_parameters: list[str]) -> dict[str, Any]:
    return {
        "rejected_variant_parameters": {
            str(parameter): f"{template_id} 不支持写入 {parameter}，该字段不属于当前模板可个性化范围。"
            for parameter in rejected_parameters
        },
        "locked_template_fields": {
            field: "模板骨架字段不可由教案或对话 patch 改写；如需改变玩法，应走受控模板切换。"
            for field in COMMON_LOCKED_TEMPLATE_FIELDS
        },
        "unsupported_music_element": "当前音乐目标超出模板能力时，应返回推荐模板而不是硬套当前模板。",
        "out_of_range_parameter": "参数值超出模板声明范围时拒绝写入当前实例。",
    }


def build_game_variant_spec(
    *,
    lesson_fit: dict[str, Any],
    template_id: str,
    options: dict[str, Any] | None = None,
) -> dict[str, Any]:
    options = options if isinstance(options, dict) else {}
    binding = lesson_fit.get("music_element_binding") if isinstance(lesson_fit.get("music_element_binding"), dict) else {}
    lesson_contract = lesson_fit.get("lesson_contract") if isinstance(lesson_fit.get("lesson_contract"), dict) else {}
    capability = template_capability_profile(template_id)
    variant_parameters = _variant_parameters_from_binding(template_id, binding)
    for key in capability.get("variant_parameters", []):
        if key in MUSIC_ENTITY_AUTHORED_PARAMETERS and _has_value(variant_parameters.get(key)):
            continue
        if key in options and _has_value(options[key]):
            variant_parameters[key] = deepcopy(options[key])
    slot_bindings = _slot_bindings_from_binding(binding)
    canonical = binding.get("canonical_element") if isinstance(binding.get("canonical_element"), dict) else {}
    semantic_text = _semantic_text_for_retrieval(lesson_fit, binding)
    song_material = _song_material_from_lesson_fit(lesson_fit)
    entity_candidates = (
        retrieve_music_element_candidates(semantic_text=semantic_text, song_material=song_material, template_id=template_id).get("candidates", [])
        if semantic_text
        else []
    )
    material_entities = (
        retrieve_music_element_entities(semantic_text=semantic_text, song_material=song_material).get("entities", [])
        if semantic_text
        else []
    )
    selected_entity = _selected_material_entity(material_entities, template_id, binding)
    selected_entity = _attach_lesson_contract_trace(selected_entity, lesson_contract)
    template_capability_match = _template_capability_match(
        template_id=template_id,
        material_entities=material_entities,
        selected_entity=selected_entity,
    )
    entity_application = _entity_application(template_id, binding, variant_parameters, lesson_contract)
    confirmation_gates = _confirmation_gates(binding, variant_parameters)
    teacher_confirmation_cards = _teacher_confirmation_cards(confirmation_gates)
    execution_plan = _execution_plan(
        template_id=template_id,
        variant_parameters=variant_parameters,
        slot_bindings=slot_bindings,
        entity_application=entity_application,
        confirmation_gates=confirmation_gates,
        template_capability_match=template_capability_match,
        lesson_contract=lesson_contract,
    )
    return {
        "version": GAME_VARIANT_SPEC_VERSION,
        "contract_schema_version": GAME_VARIANT_SPEC_CONTRACT_SCHEMA_VERSION,
        "template_id": template_id,
        "lesson_contract_ref": deepcopy(lesson_contract) if lesson_contract else {},
        "template_capability": capability,
        "source_of_truth": "music_element_binding" if binding else "lesson_fit",
        "music_entity": {
            "canonical_id": canonical.get("id", ""),
            "label": canonical.get("label", ""),
            "entity_type": canonical.get("entity_type", ""),
        },
        "variant_parameters": variant_parameters,
        "slot_bindings": slot_bindings,
        "entity_application": entity_application,
        "entity_candidates": entity_candidates,
        "material_entities": material_entities,
        "selected_entity": selected_entity,
        "template_capability_match": template_capability_match,
        "execution_plan": execution_plan,
        "confirmation_gates": confirmation_gates,
        "teacher_confirmation_cards": teacher_confirmation_cards,
        "revision_history": [],
        "requires_teacher_confirmation": bool(binding.get("requires_teacher_confirmation")),
        "confirmation_reason": binding.get("confirmation_reason", ""),
    }


def teacher_confirmation_cards_from_variant_spec(spec: dict[str, Any]) -> list[dict[str, Any]]:
    gates = spec.get("confirmation_gates") if isinstance(spec.get("confirmation_gates"), list) else []
    return _teacher_confirmation_cards(gates)


def confirm_game_variant_spec_gates(
    spec: dict[str, Any],
    *,
    confirmations: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    confirmed_spec = deepcopy(spec) if isinstance(spec, dict) else {}
    gates = confirmed_spec.get("confirmation_gates") if isinstance(confirmed_spec.get("confirmation_gates"), list) else []
    confirmations = confirmations if isinstance(confirmations, list) else []
    confirmations_by_index = {
        int(item["gate_index"]): item
        for item in confirmations
        if isinstance(item, dict) and isinstance(item.get("gate_index"), int)
    }

    for index, gate in enumerate(gates):
        if not isinstance(gate, dict) or index not in confirmations_by_index:
            continue
        confirmation = confirmations_by_index[index]
        confirmed_value = confirmation.get("confirmed_value", gate.get("proposed_value"))
        if "proposed_value" in gate and confirmed_value != gate.get("proposed_value"):
            gate["status"] = "pending"
            gate["confirmation_error"] = "confirmed_value_mismatch"
            continue
        gate["status"] = "confirmed"
        gate["confirmed_value"] = deepcopy(confirmed_value)
        gate.pop("confirmation_error", None)
        if confirmation.get("confirmed_by"):
            gate["confirmed_by"] = confirmation["confirmed_by"]

    if gates and all(isinstance(gate, dict) and gate.get("status") == "confirmed" for gate in gates):
        confirmed_spec["requires_teacher_confirmation"] = False
        confirmed_spec["confirmation_reason"] = ""
        entity_application = (
            confirmed_spec.get("entity_application") if isinstance(confirmed_spec.get("entity_application"), dict) else {}
        )
        if entity_application:
            entity_application["requires_teacher_confirmation"] = False
            entity_application["confirmation_reason"] = ""
        confirmed_spec["execution_plan"] = _execution_plan(
            template_id=str(confirmed_spec.get("template_id") or ""),
            variant_parameters=confirmed_spec.get("variant_parameters")
            if isinstance(confirmed_spec.get("variant_parameters"), dict)
            else {},
            slot_bindings=confirmed_spec.get("slot_bindings") if isinstance(confirmed_spec.get("slot_bindings"), dict) else {},
            entity_application=entity_application,
            confirmation_gates=gates,
            template_capability_match=confirmed_spec.get("template_capability_match")
            if isinstance(confirmed_spec.get("template_capability_match"), dict)
            else {},
            lesson_contract=confirmed_spec.get("lesson_contract_ref")
            if isinstance(confirmed_spec.get("lesson_contract_ref"), dict)
            else {},
        )
    confirmed_spec["teacher_confirmation_cards"] = _teacher_confirmation_cards(gates)

    return confirmed_spec


def _song_material_from_lesson_fit(lesson_fit: dict[str, Any]) -> dict[str, Any]:
    material = lesson_fit.get("song_material") if isinstance(lesson_fit.get("song_material"), dict) else {}
    if material:
        return deepcopy(material)
    source = lesson_fit.get("source") if isinstance(lesson_fit.get("source"), dict) else {}
    for key in ("song_material", "material"):
        value = source.get(key) if isinstance(source.get(key), dict) else {}
        if value:
            return deepcopy(value)
    return {}


def _variant_parameters_from_binding(template_id: str, binding: dict[str, Any]) -> dict[str, Any]:
    entity = binding.get("entity") if isinstance(binding.get("entity"), dict) else {}
    if template_id == "beat_guardian_core":
        parameters: dict[str, Any] = {}
        if entity.get("meter"):
            parameters["meter"] = entity["meter"]
        if isinstance(entity.get("target_beats"), list):
            parameters["target_beats"] = deepcopy(entity["target_beats"])
        return parameters
    if template_id == "rhythm_echo_core":
        playback = entity.get("playback") if isinstance(entity.get("playback"), dict) else {}
        steps = playback.get("pattern_steps") or entity.get("answer_tokens")
        return {"pattern_steps": deepcopy(steps)} if isinstance(steps, list) and steps else {}
    if template_id == "pitch_ladder_core" and isinstance(entity.get("target_melody"), list):
        return {"pitch_range": deepcopy(entity["target_melody"])}
    if template_id == "solfege_target_core" and isinstance(entity.get("target_solfege"), list):
        return {"target_solfege": deepcopy(entity["target_solfege"])}
    if template_id == "timbre_detective_core":
        parameters = {}
        if isinstance(entity.get("instrument_pool"), list):
            parameters["instrument_pool"] = deepcopy(entity["instrument_pool"])
        if isinstance(entity.get("evidence_traits"), list):
            parameters["timbre_traits"] = deepcopy(entity["evidence_traits"])
        return parameters
    if template_id == "form_treasure_core" and entity.get("form_type"):
        return {"form_type": entity["form_type"]}
    if template_id == "composition_puzzle_core" and isinstance(entity.get("scale_degrees"), list):
        degrees = deepcopy(entity["scale_degrees"])
        return {"melody_cards": degrees, "required_elements": deepcopy(degrees)}
    if template_id == "composition_puzzle_core" and isinstance(entity.get("melody_cards"), list):
        cards = deepcopy(entity["melody_cards"])
        parameters = {"melody_cards": cards}
        if cards:
            parameters["required_elements"] = deepcopy(cards)
        return parameters
    return {}


def _slot_bindings_from_binding(binding: dict[str, Any]) -> dict[str, Any]:
    template_id = str((binding.get("template_match") or {}).get("template_id") or "").strip() if isinstance(binding.get("template_match"), dict) else ""
    entity = binding.get("entity") if isinstance(binding.get("entity"), dict) else {}
    playback = entity.get("playback") if isinstance(entity.get("playback"), dict) else {}
    specialized = _specialized_slot_bindings(template_id, entity)
    value = (
        playback.get("pattern_steps")
        or entity.get("answer_tokens")
        or entity.get("target_solfege")
        or entity.get("target_melody")
        or entity.get("scale_degrees")
        or entity.get("melody_cards")
    )
    slots = binding.get("game_slots") if isinstance(binding.get("game_slots"), list) else []
    if slots and value:
        specialized.update({str(slot): deepcopy(value) for slot in slots if str(slot or "").strip()})
    return _drop_empty(specialized)


def _specialized_slot_bindings(template_id: str, entity: dict[str, Any]) -> dict[str, Any]:
    if template_id == "beat_guardian_core":
        return {
            "meter.accent_pattern": deepcopy(entity.get("accent_pattern") or []),
            "meter.beat_count": entity.get("beat_count"),
        }
    if template_id == "rhythm_echo_core":
        playback = entity.get("playback") if isinstance(entity.get("playback"), dict) else {}
        return {
            "rhythm.pattern_steps": deepcopy(playback.get("pattern_steps") or entity.get("answer_tokens") or []),
            "rhythm.duration_beats": deepcopy(entity.get("duration_beats") or []),
        }
    if template_id == "timbre_detective_core":
        return {
            "timbre.comparison_pairs": deepcopy(entity.get("comparison_pairs") or []),
            "timbre.trait_targets": deepcopy(entity.get("trait_targets") or {}),
        }
    if template_id == "form_treasure_core":
        return {
            "form.answer_pattern": deepcopy(entity.get("answer_pattern") or []),
            "form.timeline_segments": deepcopy(entity.get("timeline_segments") or []),
        }
    if template_id == "composition_puzzle_core":
        return {
            "composition.scale_degrees": deepcopy(entity.get("scale_degrees") or entity.get("melody_cards") or []),
            "composition.constraint_checks": deepcopy(entity.get("constraint_checks") or []),
        }
    return {}


def _entity_application(
    template_id: str,
    binding: dict[str, Any],
    variant_parameters: dict[str, Any],
    lesson_contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not binding:
        return {}
    lesson_contract = lesson_contract if isinstance(lesson_contract, dict) else {}
    canonical = binding.get("canonical_element") if isinstance(binding.get("canonical_element"), dict) else {}
    entity = binding.get("entity") if isinstance(binding.get("entity"), dict) else {}
    return _drop_empty(
        {
            "template_id": template_id,
            "canonical_id": canonical.get("id", ""),
            "entity_type": canonical.get("entity_type", ""),
            "label": canonical.get("label", ""),
            "game_parameters": deepcopy(variant_parameters),
            "slot_bindings": _specialized_slot_bindings(template_id, entity),
            "source_span": deepcopy(entity.get("source_span") or {}),
            "confidence": entity.get("confidence"),
            "extraction_basis": entity.get("extraction_basis", ""),
            "lesson_contract_path": "material_anchor" if lesson_contract.get("material_anchor") else "",
            "source_trace": _lesson_contract_material_source_trace(lesson_contract),
            "requires_teacher_confirmation": bool(binding.get("requires_teacher_confirmation")),
            "confirmation_reason": binding.get("confirmation_reason", ""),
        }
    )


def _execution_plan(
    *,
    template_id: str,
    variant_parameters: dict[str, Any],
    slot_bindings: dict[str, Any],
    entity_application: dict[str, Any],
    confirmation_gates: list[dict[str, Any]],
    template_capability_match: dict[str, Any],
    lesson_contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    lesson_contract = lesson_contract if isinstance(lesson_contract, dict) else {}
    blocked_reasons: list[str] = []
    if any(isinstance(gate, dict) and gate.get("status") != "confirmed" for gate in confirmation_gates):
        blocked_reasons.append("teacher_confirmation_required")
    if template_capability_match.get("status") == "rejected":
        blocked_reasons.append("template_capability_rejected")
    writable_parameters = template_capability_profile(template_id).get("writable_variant_parameters", [])
    writable_slots = template_capability_profile(template_id).get("writable_slot_bindings", [])
    parameter_writes = [
        {"path": f"variant_parameters.{key}", "value": deepcopy(value)}
        for key, value in variant_parameters.items()
        if key in writable_parameters or key in MUSIC_ENTITY_AUTHORED_PARAMETERS
    ]
    slot_writes = [
        {"path": f"slot_bindings.{key}", "value": deepcopy(value)}
        for key, value in slot_bindings.items()
        if _slot_is_writable(key, writable_slots)
    ]
    application_parameters = (
        entity_application.get("game_parameters")
        if isinstance(entity_application.get("game_parameters"), dict)
        else {}
    )
    application_slots = (
        entity_application.get("slot_bindings")
        if isinstance(entity_application.get("slot_bindings"), dict)
        else {}
    )
    return _drop_empty(
        {
            "version": "execution_plan_v1",
            "template_id": template_id,
            "status": "blocked" if blocked_reasons else "ready",
            "blocked_reasons": blocked_reasons,
            "entity_type": entity_application.get("entity_type", ""),
            "canonical_id": entity_application.get("canonical_id", ""),
            "parameter_writes": parameter_writes,
            "slot_writes": slot_writes,
            "entity_application_writes": {
                "game_parameters": deepcopy(application_parameters),
                "slot_bindings": deepcopy(application_slots),
            },
            "requires_teacher_confirmation": bool(confirmation_gates),
            "template_capability_status": template_capability_match.get("status", ""),
            "lesson_contract_path": "material_anchor" if lesson_contract.get("material_anchor") else "",
            "source_trace": _lesson_contract_material_source_trace(lesson_contract),
        }
    )


def _slot_is_writable(slot: str, writable_slots: list[str]) -> bool:
    if slot in writable_slots:
        return True
    for pattern in writable_slots:
        if "*" not in str(pattern):
            continue
        prefix, _, suffix = str(pattern).partition("*")
        if slot.startswith(prefix) and slot.endswith(suffix):
            return True
    return False


def _confirmation_gates(binding: dict[str, Any], variant_parameters: dict[str, Any]) -> list[dict[str, Any]]:
    if not binding:
        return []
    entity = binding.get("entity") if isinstance(binding.get("entity"), dict) else {}
    canonical = binding.get("canonical_element") if isinstance(binding.get("canonical_element"), dict) else {}
    confidence = entity.get("confidence")
    low_confidence = isinstance(confidence, (int, float)) and float(confidence) < 0.75
    if not low_confidence and not binding.get("requires_teacher_confirmation"):
        return []
    proposed = (
        variant_parameters.get("pattern_steps")
        or (entity.get("playback") if isinstance(entity.get("playback"), dict) else {}).get("pattern_steps")
        or entity.get("answer_tokens")
    )
    return [
        _drop_empty(
            {
                "gate_type": "low_confidence_music_entity" if low_confidence else "teacher_confirmation_required",
                "entity_type": canonical.get("entity_type", ""),
                "canonical_id": canonical.get("id", ""),
                "label": canonical.get("label", ""),
                "confidence": confidence,
                "extraction_basis": entity.get("extraction_basis", ""),
                "source_span": deepcopy(entity.get("source_span") or {}),
                "proposed_value": deepcopy(proposed),
                "reason": binding.get("confirmation_reason", ""),
            }
        )
    ]


def _teacher_confirmation_cards(confirmation_gates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for index, gate in enumerate(confirmation_gates):
        if not isinstance(gate, dict):
            continue
        entity_type = str(gate.get("entity_type") or "")
        title = _confirmation_card_title(entity_type)
        proposed_value = deepcopy(gate.get("confirmed_value", gate.get("proposed_value")))
        status = "confirmed" if gate.get("status") == "confirmed" else "pending"
        cards.append(
            _drop_empty(
                {
                    "version": "teacher_confirmation_card_v1",
                    "gate_index": index,
                    "status": status,
                    "title": title,
                    "teacher_message": _confirmation_card_message(gate),
                    "display_value": _display_music_value(proposed_value, entity_type),
                    "raw_value": proposed_value,
                    "confidence_label": _confidence_label(gate.get("confidence")),
                    "source_label": _source_label(gate.get("source_span") if isinstance(gate.get("source_span"), dict) else {}),
                    "reason": gate.get("reason", ""),
                    "actions": [
                        {"action": "confirm", "label": "确认用于游戏"},
                        {"action": "edit", "label": "我来改一下"},
                    ],
                }
            )
        )
    return cards


def _confirmation_card_title(entity_type: str) -> str:
    titles = {
        "rhythm_pattern": "请确认目标节奏",
        "pitch_motion": "请确认旋律路线",
        "solfege_set": "请确认目标唱名",
        "meter": "请确认拍号和强拍",
        "timbre_set": "请确认乐器和音色证据",
        "form_structure": "请确认曲式结构",
        "composition_material": "请确认创编素材",
    }
    return titles.get(entity_type, "请确认音乐材料")


def _confirmation_card_message(gate: dict[str, Any]) -> str:
    label = str(gate.get("label") or "音乐材料")
    reason = str(gate.get("reason") or "这个内容来自系统推断，请确认后再作为游戏答案。")
    return f"我识别到“{label}”，{reason}"


def _display_music_value(value: Any, entity_type: str) -> str:
    if isinstance(value, list):
        if entity_type == "rhythm_pattern":
            return "、".join(_rhythm_token_label(item) for item in value)
        return "、".join(str(item) for item in value)
    if isinstance(value, dict):
        return "、".join(f"{key}: {display}" for key, display in value.items())
    return str(value or "")


def _rhythm_token_label(token: Any) -> str:
    labels = {
        "quarter": "四分音符",
        "rest": "休止符",
        "eighth_pair": "八分八分",
        "syncopation": "切分",
        "half": "二分音符",
        "whole": "全音符",
        "dotted_quarter": "附点四分",
    }
    return labels.get(str(token), str(token))


def _confidence_label(confidence: Any) -> str:
    if isinstance(confidence, (int, float)):
        if float(confidence) >= 0.85:
            return "较有把握"
        if float(confidence) >= 0.7:
            return "需要确认"
    return "需要确认"


def _source_label(source_span: dict[str, Any]) -> str:
    kind = str(source_span.get("kind") or "")
    if kind == "material_phrase":
        return str(source_span.get("phrase_label") or source_span.get("phrase_id") or "谱例片段")
    if kind == "semantic_text":
        return "教师文字描述"
    if kind == "audio_clip":
        return "音频片段"
    return "课堂材料"


def _semantic_text_for_retrieval(lesson_fit: dict[str, Any], binding: dict[str, Any]) -> str:
    evidence = lesson_fit.get("lesson_evidence") if isinstance(lesson_fit.get("lesson_evidence"), dict) else {}
    canonical = binding.get("canonical_element") if isinstance(binding.get("canonical_element"), dict) else {}
    return " ".join(
        str(value or "").strip()
        for value in [
            evidence.get("music_element"),
            evidence.get("target_objective"),
            binding.get("semantic_element"),
            canonical.get("label"),
            canonical.get("id"),
        ]
        if str(value or "").strip()
    )


def _selected_material_entity(
    material_entities: list[dict[str, Any]],
    template_id: str,
    binding: dict[str, Any],
) -> dict[str, Any]:
    if not material_entities:
        return {}
    canonical = binding.get("canonical_element") if isinstance(binding.get("canonical_element"), dict) else {}
    canonical_id = str(canonical.get("id") or "").strip()
    canonical_type = str(canonical.get("entity_type") or "").strip()

    for entity in material_entities:
        if not isinstance(entity, dict):
            continue
        if template_id and template_id in entity.get("compatible_template_ids", []):
            return deepcopy(entity)
    for entity in material_entities:
        if not isinstance(entity, dict):
            continue
        if canonical_id and canonical_id == entity.get("entity_id"):
            return deepcopy(entity)
        if canonical_type and canonical_type == entity.get("entity_type"):
            return deepcopy(entity)
    return deepcopy(material_entities[0])


def _attach_lesson_contract_trace(entity: dict[str, Any], lesson_contract: dict[str, Any]) -> dict[str, Any]:
    if not entity:
        return {}
    traced = deepcopy(entity)
    if isinstance(lesson_contract, dict) and lesson_contract.get("material_anchor"):
        traced["lesson_contract_path"] = "material_anchor"
        traced["source_trace"] = _lesson_contract_material_source_trace(lesson_contract)
    return traced


def _lesson_contract_material_source_trace(lesson_contract: dict[str, Any]) -> str:
    if not isinstance(lesson_contract, dict):
        return ""
    source_trace = lesson_contract.get("source_trace") if isinstance(lesson_contract.get("source_trace"), dict) else {}
    if source_trace.get("material_anchor"):
        return str(source_trace.get("material_anchor") or "")
    anchor = lesson_contract.get("material_anchor") if isinstance(lesson_contract.get("material_anchor"), dict) else {}
    phrase_id = str(anchor.get("selected_phrase_id") or "").strip()
    if phrase_id:
        return f"song_material.phrases.{phrase_id}"
    if anchor.get("target_sequence"):
        return "song_material.phrases.target_sequence"
    if anchor.get("audio_clip_url"):
        return "song_material.audio_clip"
    if anchor:
        return "teacher_confirmation_candidate"
    return ""


def _template_capability_match(
    *,
    template_id: str,
    material_entities: list[dict[str, Any]],
    selected_entity: dict[str, Any],
) -> dict[str, Any]:
    if not selected_entity:
        return {}
    compatible_templates = selected_entity.get("compatible_template_ids")
    compatible_templates = compatible_templates if isinstance(compatible_templates, list) else []
    semantic_term = str(selected_entity.get("semantic_term") or selected_entity.get("label") or "音乐要素")
    if template_id in compatible_templates:
        return _drop_empty(
            {
                "status": "supported",
                "template_id": template_id,
                "matched_entity": deepcopy(selected_entity),
                "recommended_template_id": template_id,
                "requires_teacher_confirmation": bool(selected_entity.get("needs_confirmation")),
                "teacher_message": (
                    f"当前玩法可以承接“{semantic_term}”。"
                    if not selected_entity.get("needs_confirmation")
                    else f"当前玩法可以承接“{semantic_term}”，但还需要教师确认音乐材料。"
                ),
            }
        )

    recommended_template = _recommended_template_for_entities(material_entities, selected_entity)
    return _drop_empty(
        {
            "status": "rejected",
            "template_id": template_id,
            "matched_entity": deepcopy(selected_entity),
            "recommended_template_id": recommended_template,
            "requires_teacher_confirmation": True,
            "reason": "unsupported_entity_for_current_template",
            "teacher_message": (
                f"当前玩法不能承接“{semantic_term}”；"
                f"建议改用“{recommended_template}”。"
                if recommended_template
                else f"当前玩法不能承接“{semantic_term}”，需要先确认可用玩法。"
            ),
        }
    )


def _recommended_template_for_entities(
    material_entities: list[dict[str, Any]],
    selected_entity: dict[str, Any],
) -> str:
    compatible = selected_entity.get("compatible_template_ids")
    if isinstance(compatible, list) and compatible:
        return str(compatible[0] or "").strip()
    for entity in material_entities:
        if not isinstance(entity, dict):
            continue
        compatible = entity.get("compatible_template_ids")
        if isinstance(compatible, list) and compatible:
            return str(compatible[0] or "").strip()
    return ""


def _has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict, tuple, set)):
        return bool(value)
    return True


def _drop_empty(payload: dict[str, Any]) -> dict[str, Any]:
    compact: dict[str, Any] = {}
    for key, value in payload.items():
        if value is None:
            continue
        if isinstance(value, str) and not value:
            continue
        if isinstance(value, (list, dict)) and not value:
            continue
        compact[key] = value
    return compact
