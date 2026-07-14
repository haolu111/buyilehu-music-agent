from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.services.game_variant_spec import template_capability_profile
from app.services.template_fidelity_contract import LOCKED_CORE_FIELDS


LESSON_ALIGNMENT_GATE_VERSION = "lesson_alignment_gate_v1"
TEMPLATE_FIDELITY_GATE_VERSION = "template_fidelity_gate_v1"
LESSON_SLOT_COVERAGE_VERSION = "lesson_slot_coverage_v1"


def build_lesson_contract_ref(
    *,
    lesson_context: dict[str, Any],
    lesson_fit: dict[str, Any],
    proposal_card: dict[str, Any],
) -> dict[str, Any]:
    formal_contract = lesson_fit.get("lesson_contract") if isinstance(lesson_fit.get("lesson_contract"), dict) else {}
    if formal_contract.get("version") == "lesson_contract_v1":
        return deepcopy(formal_contract)
    evidence = lesson_fit.get("lesson_evidence") if isinstance(lesson_fit.get("lesson_evidence"), dict) else {}
    material = lesson_fit.get("material_binding") if isinstance(lesson_fit.get("material_binding"), dict) else {}
    return _drop_empty(
        {
            "version": "lesson_contract_v1",
            "objective": evidence.get("target_objective")
            or lesson_context.get("teaching_objective")
            or lesson_context.get("target_objective")
            or proposal_card.get("learning_goal"),
            "stage": evidence.get("target_stage") or lesson_context.get("target_stage"),
            "music_focus": evidence.get("music_element") or lesson_context.get("target_music_element") or proposal_card.get("music_element"),
            "material_anchor": {
                "song_title": material.get("song_title"),
                "selected_phrase_label": material.get("selected_phrase_label"),
                "audio_clip_url": material.get("audio_clip_url"),
            },
            "student_must": evidence.get("segment_task") or proposal_card.get("student_mission"),
            "transfer": lesson_context.get("transfer_task") or proposal_card.get("transfer_task"),
        }
    )


def evaluate_lesson_alignment_gate(
    *,
    template_id: str,
    lesson_context: dict[str, Any],
    lesson_fit: dict[str, Any],
    proposal_card: dict[str, Any],
) -> dict[str, Any]:
    lesson_contract = build_lesson_contract_ref(
        lesson_context=lesson_context,
        lesson_fit=lesson_fit,
        proposal_card=proposal_card,
    )
    focus = str(lesson_contract.get("music_focus") or "").strip()
    capability = template_capability_profile(template_id)
    suitable = [str(item) for item in capability.get("suitable_music_elements", [])]
    not_suitable = [str(item) for item in capability.get("not_suitable_for", [])]
    blocking_reasons: list[str] = []
    warnings: list[str] = []

    if not focus:
        warnings.append("missing_music_focus")
    elif _matches_capability_term(focus, not_suitable) or not _matches_capability_term(focus, suitable):
        blocking_reasons.append("music_element_template_mismatch")

    if not lesson_contract.get("objective"):
        warnings.append("missing_objective")
    if not lesson_contract.get("student_must"):
        warnings.append("missing_student_task")

    status = "fail" if blocking_reasons else "warning" if warnings else "pass"
    score = 45 if blocking_reasons else 72 if warnings else 92
    return _drop_empty(
        {
            "version": LESSON_ALIGNMENT_GATE_VERSION,
            "status": status,
            "score": score,
            "template_id": template_id,
            "lesson_contract_ref": lesson_contract,
            "matched_music_focus": focus,
            "blocking_reasons": blocking_reasons,
            "warnings": warnings,
            "teacher_message": _alignment_teacher_message(status, focus, template_id),
        }
    )


def evaluate_template_fidelity_gate(
    *,
    template_fidelity_contract: dict[str, Any],
    source_options: dict[str, Any],
) -> dict[str, Any]:
    blocking_reasons: list[str] = []
    locked_fields = (
        template_fidelity_contract.get("locked_core_fields")
        if isinstance(template_fidelity_contract.get("locked_core_fields"), dict)
        else {}
    )
    for field in LOCKED_CORE_FIELDS:
        expected = (locked_fields.get(field) or {}).get("expected") if isinstance(locked_fields.get(field), dict) else ""
        attempted = source_options.get(field) if isinstance(source_options, dict) else None
        if attempted and attempted != expected:
            blocking_reasons.append(f"{field}_changed")
    if not template_fidelity_contract.get("template_fidelity_pass"):
        for field, report in locked_fields.items():
            if isinstance(report, dict) and report.get("pass") is False:
                blocking_reasons.append(f"{field}_changed")
        if template_fidelity_contract.get("runtime_component_pass") is False:
            blocking_reasons.append("runtime_component_changed")
        if not template_fidelity_contract.get("selected_skin_id"):
            blocking_reasons.append("missing_allowed_skin")

    deduped = list(dict.fromkeys(blocking_reasons))
    status = "fail" if deduped else "pass"
    return _drop_empty(
        {
            "version": TEMPLATE_FIDELITY_GATE_VERSION,
            "status": status,
            "score": 40 if deduped else 95,
            "template_id": template_fidelity_contract.get("template_id", ""),
            "blocking_reasons": deduped,
            "locked_runtime_component": template_fidelity_contract.get("locked_runtime_component", ""),
            "actual_runtime_component": template_fidelity_contract.get("actual_runtime_component", ""),
            "locked_core_fields": deepcopy(locked_fields),
            "teacher_message": (
                "当前修改触碰了模板骨架，不能作为模板内个性化交付。"
                if deduped
                else "模板核心玩法、运行壳和胜负机制保持稳定。"
            ),
        }
    )


def evaluate_lesson_slot_coverage(
    *,
    template_id: str,
    lesson_alignment_result: dict[str, Any],
    game_variant_spec: dict[str, Any],
) -> dict[str, Any]:
    lesson_contract = (
        lesson_alignment_result.get("lesson_contract_ref")
        if isinstance(lesson_alignment_result.get("lesson_contract_ref"), dict)
        else {}
    )
    variant_parameters = (
        game_variant_spec.get("variant_parameters") if isinstance(game_variant_spec.get("variant_parameters"), dict) else {}
    )
    slot_bindings = game_variant_spec.get("slot_bindings") if isinstance(game_variant_spec.get("slot_bindings"), dict) else {}
    entity_application = (
        game_variant_spec.get("entity_application") if isinstance(game_variant_spec.get("entity_application"), dict) else {}
    )
    execution_plan = game_variant_spec.get("execution_plan") if isinstance(game_variant_spec.get("execution_plan"), dict) else {}
    entity_slots = entity_application.get("slot_bindings") if isinstance(entity_application.get("slot_bindings"), dict) else {}
    entity_parameters = (
        entity_application.get("game_parameters") if isinstance(entity_application.get("game_parameters"), dict) else {}
    )
    merged_slots = {**deepcopy(slot_bindings), **deepcopy(entity_slots)}
    merged_parameters = {**deepcopy(variant_parameters), **deepcopy(entity_parameters)}
    evidence_paths, covered_surfaces = _slot_coverage_for_template(
        template_id=template_id,
        parameters=merged_parameters,
        slots=merged_slots,
    )
    delivery_mode = str(game_variant_spec.get("delivery_mode") or "").strip()
    material_requirement = str(game_variant_spec.get("material_requirement") or "").strip()
    blocking_reasons: list[str] = []
    warnings: list[str] = []
    has_claimed_entity_application = bool(entity_application)
    if not lesson_contract.get("music_focus"):
        warnings.append("missing_music_focus")
    if delivery_mode == "element_training_game" and material_requirement == "not_required":
        return _drop_empty(
            {
                "version": LESSON_SLOT_COVERAGE_VERSION,
                "status": "pass" if not warnings else "warning",
                "score": 93 if not warnings else 76,
                "template_id": template_id,
                "delivery_mode": delivery_mode,
                "material_requirement": material_requirement,
                "music_focus": lesson_contract.get("music_focus", ""),
                "covered_surfaces": ["template_default_training"],
                "evidence_paths": ["template_defaults"],
                "warnings": warnings,
                "teacher_message": "常规音乐要素训练，使用模板训练材料，不要求上传课例材料。",
            }
        )
    blocked_reasons = (
        execution_plan.get("blocked_reasons")
        if isinstance(execution_plan.get("blocked_reasons"), list)
        else []
    )
    if "template_capability_rejected" in blocked_reasons and not evidence_paths:
        blocking_reasons.append("execution_plan_blocked")
    elif blocked_reasons:
        warnings.extend(str(reason) for reason in blocked_reasons)
    missing_required_slots = _missing_required_slots(template_id, evidence_paths)
    if delivery_mode == "song_anchored_game" and material_requirement == "binding_required" and missing_required_slots:
        blocking_reasons.append("uploaded_material_not_landed")
    if not evidence_paths and has_claimed_entity_application and not entity_application.get("requires_teacher_confirmation"):
        blocking_reasons.append("missing_playable_judgement_slot")
    elif not evidence_paths:
        warnings.append("missing_music_entity_binding")
    status = "fail" if blocking_reasons else "warning" if warnings else "pass"
    score = 42 if blocking_reasons else 76 if warnings else 93
    return _drop_empty(
        {
            "version": LESSON_SLOT_COVERAGE_VERSION,
            "status": status,
            "score": score,
            "template_id": template_id,
            "delivery_mode": delivery_mode,
            "material_requirement": material_requirement,
            "music_focus": lesson_contract.get("music_focus", ""),
            "covered_surfaces": covered_surfaces,
            "evidence_paths": evidence_paths,
            "missing_required_slots": missing_required_slots,
            "blocking_reasons": blocking_reasons,
            "warnings": warnings,
            "teacher_message": _slot_coverage_teacher_message(status, template_id),
        }
    )


def _alignment_teacher_message(status: str, focus: str, template_id: str) -> str:
    if status == "fail":
        return f"当前 {template_id} 玩法不能承接“{focus}”这个音乐目标，需要换用更匹配的模板。"
    if status == "warning":
        return "教案目标或学生任务还不够完整，建议教师确认后再交付。"
    return "当前玩法、学生任务和音乐目标已对齐。"


def _slot_coverage_for_template(
    *,
    template_id: str,
    parameters: dict[str, Any],
    slots: dict[str, Any],
) -> tuple[list[str], list[str]]:
    evidence_paths: list[str] = []
    covered_surfaces: list[str] = []

    def add(path: str, surface: str) -> None:
        if path not in evidence_paths:
            evidence_paths.append(path)
        if surface not in covered_surfaces:
            covered_surfaces.append(surface)

    if template_id == "beat_guardian_core":
        if _has_value(parameters.get("target_beats")):
            add("meter.target_beats", "judgement")
        if _has_value(slots.get("meter.accent_pattern")):
            add("meter.accent_pattern", "feedback")
        if _has_value(parameters.get("meter")) or _has_value(slots.get("meter.beat_count")):
            add("meter.beat_count", "round_setup")
    elif template_id == "rhythm_echo_core":
        if _has_value(parameters.get("pattern_steps")):
            add("rhythm.pattern_steps", "judgement")
        if _has_value(slots.get("round_1.target_rhythm")) or _has_any_round_slot(slots, "target_rhythm"):
            add("round.target_rhythm", "judgement")
        if _has_value(slots.get("rhythm.duration_beats")):
            add("rhythm.duration_beats", "feedback")
    elif template_id == "pitch_ladder_core":
        if _has_value(parameters.get("pitch_range")):
            add("pitch.pitch_range", "judgement")
        if _has_any_round_slot(slots, "target_melody"):
            add("round.target_melody", "judgement")
    elif template_id == "solfege_target_core":
        if _has_value(parameters.get("target_solfege")):
            add("solfege.target_solfege", "judgement")
        if _has_any_round_slot(slots, "target_solfege"):
            add("round.target_solfege", "judgement")
    elif template_id == "timbre_detective_core":
        if _has_value(parameters.get("instrument_pool")):
            add("timbre.instrument_pool", "answer")
        if _has_value(parameters.get("timbre_traits")) or _has_value(slots.get("timbre.trait_targets")):
            add("timbre.trait_targets", "feedback")
        if _has_value(slots.get("timbre.comparison_pairs")):
            add("timbre.comparison_pairs", "judgement")
    elif template_id == "form_treasure_core":
        if _has_value(parameters.get("form_type")):
            add("form.form_type", "round_setup")
        if _has_value(slots.get("form.answer_pattern")):
            add("form.answer_pattern", "judgement")
        if _has_value(slots.get("form.timeline_segments")):
            add("form.timeline_segments", "feedback")
    elif template_id == "composition_puzzle_core":
        if _has_value(parameters.get("melody_cards")) or _has_value(parameters.get("rhythm_cards")):
            add("composition.material_cards", "answer")
        if _has_value(parameters.get("required_elements")) or _has_value(slots.get("composition.constraint_checks")):
            add("composition.constraint_checks", "judgement")
        if _has_value(slots.get("composition.scale_degrees")):
            add("composition.scale_degrees", "round_setup")
    return evidence_paths, covered_surfaces


def _missing_required_slots(template_id: str, evidence_paths: list[str]) -> list[str]:
    required = {
        "beat_guardian_core": {
            "round_1.answer_sequence": ["meter.target_beats", "meter.accent_pattern"],
            "round_1.score_phrase": ["meter.beat_count", "meter.accent_pattern"],
        },
        "rhythm_echo_core": {
            "round_1.target_rhythm": ["rhythm.pattern_steps", "round.target_rhythm"],
            "round_1.playback_tokens": ["rhythm.pattern_steps", "round.target_rhythm"],
        },
        "pitch_ladder_core": {
            "round_1.target_melody": ["pitch.pitch_range", "round.target_melody"],
            "round_1.playback_tokens": ["pitch.pitch_range", "round.target_melody"],
        },
        "solfege_target_core": {
            "round_1.target_solfege": ["solfege.target_solfege", "round.target_solfege"],
            "round_1.playback_tokens": ["solfege.target_solfege", "round.target_solfege"],
        },
        "timbre_detective_core": {
            "round_1.listen_clip": ["timbre.instrument_pool", "timbre.comparison_pairs"],
            "round_1.evidence_prompt": ["timbre.trait_targets"],
        },
        "form_treasure_core": {
            "section_a.listen_clip": ["form.timeline_segments", "form.answer_pattern"],
            "round_1.form_answer": ["form.answer_pattern", "form.form_type"],
        },
        "composition_puzzle_core": {
            "round_1.material_cards": ["composition.material_cards", "composition.scale_degrees"],
            "round_1.constraint_checks": ["composition.constraint_checks"],
        },
    }
    paths = set(evidence_paths)
    missing: list[str] = []
    for slot, alternatives in required.get(template_id, {}).items():
        if not paths.intersection(alternatives):
            missing.append(slot)
    return missing


def _slot_coverage_teacher_message(status: str, template_id: str) -> str:
    if status == "fail":
        hints = {
            "beat_guardian_core": "请把强拍、弱拍或目标拍位写入游戏判定。",
            "rhythm_echo_core": "请把目标节奏写入游戏目标轨道和判定点。",
            "pitch_ladder_core": "请把目标旋律路线写入游戏答案路线。",
            "solfege_target_core": "请把目标唱名写入靶点和唱回确认。",
            "timbre_detective_core": "请把乐器池、对比组或音色证据写入推理条件。",
            "form_treasure_core": "请把曲式答案和段落时间线写入排序判定。",
            "composition_puzzle_core": "请把素材卡和创编约束写入通关检查。",
        }
        return hints.get(template_id, "请把本课音乐目标写入游戏答案、反馈或通关条件。")
    if status == "warning":
        return "玩法槽位已覆盖，但教案目标还需要教师补充确认。"
    return "本课音乐目标已经进入游戏答案、反馈或通关条件。"


def _matches_capability_term(value: str, terms: list[str]) -> bool:
    value_keys = _capability_keywords(value)
    for term in terms:
        if value == term or value in term or term in value:
            return True
        if value_keys.intersection(_capability_keywords(term)):
            return True
    return False


def _capability_keywords(value: str) -> set[str]:
    keyword_groups = {
        "节奏": ("节奏", "时值", "四分", "八分", "休止", "切分", "附点"),
        "音高": ("音高", "旋律", "高低", "级进", "跳进"),
        "唱名": ("唱名", "do", "re", "mi", "sol", "la", "ti"),
        "音色": ("音色", "乐器", "笛子", "二胡", "气息感", "弦鸣"),
        "曲式": ("曲式", "ABA", "回旋", "段落", "重复对比"),
        "创编": ("创编", "五声音阶", "素材卡", "宫商角徵羽"),
        "节拍": ("节拍", "强弱拍", "强弱规律", "稳定拍", "拍号", "强拍", "弱拍", "二拍子", "三拍子", "四拍子", "第一拍", "第1拍"),
    }
    return {label for label, keywords in keyword_groups.items() if any(keyword in value for keyword in keywords)}


def _has_any_round_slot(slots: dict[str, Any], suffix: str) -> bool:
    return any(str(key).startswith("round_") and str(key).endswith(f".{suffix}") and _has_value(value) for key, value in slots.items())


def _has_value(value: Any) -> bool:
    if value is None or value == "":
        return False
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True


def _drop_empty(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if value not in (None, "", [], {})}
