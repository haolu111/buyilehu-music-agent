from __future__ import annotations

import copy
from typing import Any

from app.services.game_template_registry import get_game_template


PRODUCTION_TEMPLATE_IDS = {
    "beat_guardian_core",
    "pitch_ladder_core",
    "rhythm_echo_core",
    "solfege_target_core",
    "timbre_detective_core",
    "form_treasure_core",
    "composition_puzzle_core",
}


PRECISE_ANSWER_TEMPLATES = {
    "beat_guardian_core",
    "pitch_ladder_core",
    "rhythm_echo_core",
    "solfege_target_core",
    "composition_puzzle_core",
}


TEMPLATE_MATERIAL_SLOTS: dict[str, list[dict[str, Any]]] = {
    "beat_guardian_core": [
        {"slot": "round_1.listen_clip", "label": "第1关试听片段", "kind": "playback", "required": False},
        {"slot": "round_1.answer_sequence", "label": "第1关强弱拍答案", "kind": "answer", "required": True},
        {"slot": "round_1.score_phrase", "label": "第1关谱面依据", "kind": "score", "required": True},
        {"slot": "summary.transfer_clip", "label": "课堂迁移片段", "kind": "playback", "required": False},
    ],
    "pitch_ladder_core": [
        {"slot": "round_1.listen_clip", "label": "第1关旋律试听", "kind": "playback", "required": False},
        {"slot": "round_1.target_melody", "label": "第1关音高路线", "kind": "answer", "required": True},
        {"slot": "round_1.playback_tokens", "label": "第1关谱面播放", "kind": "tokens", "required": True},
        {"slot": "summary.sing_back_prompt", "label": "通关后唱回材料", "kind": "score", "required": True},
    ],
    "rhythm_echo_core": [
        {"slot": "round_1.listen_clip", "label": "第1关节奏试听", "kind": "playback", "required": False},
        {"slot": "round_1.target_rhythm", "label": "第1关节奏答案", "kind": "answer", "required": True},
        {"slot": "round_1.playback_tokens", "label": "第1关节奏播放", "kind": "tokens", "required": True},
        {"slot": "summary.transfer_clip", "label": "课堂迁移片段", "kind": "playback", "required": False},
    ],
    "solfege_target_core": [
        {"slot": "round_1.listen_clip", "label": "第1关唱名试听", "kind": "playback", "required": False},
        {"slot": "round_1.target_solfege", "label": "第1关唱名答案", "kind": "answer", "required": True},
        {"slot": "round_1.playback_tokens", "label": "第1关音高播放", "kind": "tokens", "required": True},
        {"slot": "summary.sing_back_prompt", "label": "通关后唱回材料", "kind": "score", "required": True},
    ],
    "timbre_detective_core": [
        {"slot": "round_1.listen_clip", "label": "第1关音色线索", "kind": "playback", "required": True},
        {"slot": "round_1.compare_clip", "label": "第1关对比音色", "kind": "playback", "required": False},
        {"slot": "round_1.evidence_prompt", "label": "音色判断依据", "kind": "answer", "required": False},
    ],
    "form_treasure_core": [
        {"slot": "section_a.listen_clip", "label": "A段音频", "kind": "playback", "required": True},
        {"slot": "section_b.listen_clip", "label": "B段音频", "kind": "playback", "required": False},
        {"slot": "round_1.form_answer", "label": "曲式答案", "kind": "answer", "required": False},
        {"slot": "round_1.score_phrase", "label": "曲式谱面依据", "kind": "score", "required": False},
    ],
    "composition_puzzle_core": [
        {"slot": "round_1.material_cards", "label": "创编素材卡", "kind": "tokens", "required": True},
        {"slot": "round_1.constraint_checks", "label": "创编约束清单", "kind": "answer", "required": True},
        {"slot": "round_1.reference_phrase", "label": "参考音乐短句", "kind": "playback", "required": False},
        {"slot": "summary.teacher_confirm_prompt", "label": "教师确认提示", "kind": "score", "required": False},
    ],
}


def template_material_slots(template_id: str) -> list[dict[str, Any]]:
    return copy.deepcopy(TEMPLATE_MATERIAL_SLOTS.get(str(template_id or ""), []))


def build_lesson_template_contract(
    *,
    lesson_analysis: dict[str, Any],
    workflow: dict[str, Any] | None = None,
) -> dict[str, Any]:
    lesson_context = lesson_analysis.get("lesson_context", {}) if isinstance(lesson_analysis.get("lesson_context"), dict) else {}
    lesson_fit = lesson_context.get("lesson_fit", {}) if isinstance(lesson_context.get("lesson_fit"), dict) else {}
    fit_evidence = lesson_fit.get("lesson_evidence", {}) if isinstance(lesson_fit.get("lesson_evidence"), dict) else {}
    template_decision = workflow.get("template_decision", {}) if isinstance(workflow, dict) and isinstance(workflow.get("template_decision"), dict) else {}
    instance = workflow.get("instance", {}) if isinstance(workflow, dict) and isinstance(workflow.get("instance"), dict) else {}
    template_id = str(template_decision.get("template_id") or instance.get("template_id") or "")
    template = get_game_template(template_id) or {}
    supported = template_id in PRODUCTION_TEMPLATE_IDS and template.get("runtime_status") == "production"
    has_material = has_concrete_music_material(lesson_context.get("song_material") or lesson_analysis.get("song_material") or {})
    delivery_mode = "song_anchored_game" if has_material else "element_training_game"
    return _drop_empty(
        {
            "template_id": template_id,
            "template_label": template.get("label") or instance.get("template_label") or "",
            "target_stage": fit_evidence.get("target_stage") or lesson_context.get("target_stage") or "",
            "target_music_element": fit_evidence.get("music_element") or lesson_context.get("target_music_element") or "",
            "student_task": lesson_context.get("student_task") or lesson_context.get("target_segment_task") or "",
            "teacher_confirmed": False,
            "delivery_mode": delivery_mode,
            "material_requirement": "binding_required" if has_material else "not_required",
            "template_config_overrides": template_decision.get("config_overrides", {}) if isinstance(template_decision.get("config_overrides"), dict) else {},
            "unsupported_reason": "" if supported else _unsupported_reason(template_id, template_decision),
        }
    )


def build_material_binding_plan(
    *,
    template_id: str,
    lesson_analysis: dict[str, Any],
    song_material: dict[str, Any] | None = None,
) -> dict[str, Any]:
    template_id = str(template_id or "").strip()
    lesson_context = lesson_analysis.get("lesson_context", {}) if isinstance(lesson_analysis.get("lesson_context"), dict) else {}
    material = song_material if isinstance(song_material, dict) and song_material else lesson_context.get("song_material") or lesson_analysis.get("song_material") or {}
    song_anchor = lesson_context.get("song_anchor_contract") or lesson_analysis.get("song_anchor_contract") or {}
    slots = template_material_slots(template_id)
    score_units = _score_units(material)
    audio_units = _audio_units(material)
    if not has_concrete_music_material(material):
        return {
            "version": "material_binding_plan_v1",
            "template_id": template_id,
            "status": "not_required",
            "delivery_mode": "element_training_game",
            "material_requirement": "not_required",
            "component_landing_status": "not_required",
            "requires_teacher_confirmation": False,
            "blocking_reasons": [],
            "template_material_slots": slots,
            "available_materials": {"score": [], "audio": []},
            "bindings": [],
            "component_landing": {
                "component_slots": [],
                "judgement_slots": [],
                "playback_slots": [],
                "missing_required_slots": [],
                "teacher_summary": ["常规音乐要素训练，使用模板训练材料。"],
            },
            "material_summary": {
                "score_unit_count": 0,
                "audio_unit_count": 0,
                "score_source_kind": "",
                "has_source_audio": False,
                "training_material_source": "template_defaults",
            },
            "message": "当前为常规音乐要素训练，将使用模板训练材料生成。",
        }
    selected_id = str(song_anchor.get("selected_phrase_id") or ((song_anchor.get("selected_phrase") or {}).get("id") if isinstance(song_anchor.get("selected_phrase"), dict) else "") or "")
    bindings = [
        _binding_for_slot(slot, index, score_units, audio_units, selected_id, material)
        for index, slot in enumerate(slots)
    ]
    blocking = [
        f"{item['slot_label']}缺少可绑定材料"
        for item in bindings
        if item.get("required") and not _binding_has_required_material(item)
    ]
    if template_id in PRECISE_ANSWER_TEMPLATES and not score_units:
        blocking.append("当前模板需要精确谱面/文字谱/MIDI 答案，请先确认谱子或补充文字谱。")
    if template_id not in PRODUCTION_TEMPLATE_IDS:
        blocking.append("当前教案重点没有命中可交付成熟模板。")
    status = "blocked" if blocking else "needs_confirmation"
    component_landing = _component_landing_from_bindings(bindings)
    return {
        "version": "material_binding_plan_v1",
        "template_id": template_id,
        "status": status,
        "delivery_mode": "song_anchored_game",
        "material_requirement": "binding_required",
        "component_landing_status": "blocked" if blocking else "ready_for_confirmation",
        "requires_teacher_confirmation": True,
        "blocking_reasons": blocking,
        "template_material_slots": slots,
        "available_materials": {
            "score": [_public_unit(unit) for unit in score_units],
            "audio": [_public_unit(unit) for unit in audio_units],
        },
        "bindings": bindings,
        "component_landing": component_landing,
        "material_summary": {
            "score_unit_count": len(score_units),
            "audio_unit_count": len(audio_units),
            "score_source_kind": _source_kind(material),
            "has_source_audio": bool(_source(material).get("source_audio_url")),
        },
    }


def confirm_material_binding_plan(plan: dict[str, Any], *, expected_template_id: str = "") -> dict[str, Any]:
    if not isinstance(plan, dict):
        raise ValueError("请先确认材料绑定表。")
    confirmed = copy.deepcopy(plan)
    template_id = str(confirmed.get("template_id") or "").strip()
    if expected_template_id and template_id != expected_template_id:
        raise ValueError("材料绑定表和当前模板不一致，请重新分析教案。")
    if confirmed.get("status") == "not_required" and confirmed.get("delivery_mode") == "element_training_game":
        confirmed["teacher_confirmed"] = True
        return confirmed
    if confirmed.get("status") != "confirmed":
        raise ValueError("请先确认材料绑定表，再生成游戏。")
    blocking = [str(item) for item in confirmed.get("blocking_reasons", []) if str(item).strip()]
    if blocking:
        raise ValueError(blocking[0])
    slots = {item["slot"]: item for item in template_material_slots(template_id)}
    bindings = confirmed.get("bindings", [])
    if not isinstance(bindings, list):
        raise ValueError("材料绑定表格式不正确。")
    by_slot = {str(item.get("slot") or ""): item for item in bindings if isinstance(item, dict)}
    for slot, spec in slots.items():
        if not spec.get("required"):
            continue
        binding = by_slot.get(slot)
        if not binding or not _binding_has_required_material(binding):
            raise ValueError(f"请先为“{spec.get('label', slot)}”选择材料。")
    confirmed["teacher_confirmed"] = True
    return confirmed


def apply_confirmed_material_binding(
    proposal: dict[str, Any],
    confirmed_plan: dict[str, Any],
) -> dict[str, Any]:
    updated = copy.deepcopy(proposal)
    lesson_analysis = updated.setdefault("lesson_analysis", {})
    lesson_context = updated.setdefault("lesson_context", lesson_analysis.get("lesson_context", {}) or {})
    lesson_analysis["lesson_context"] = lesson_context
    lesson_context["material_binding_plan"] = confirmed_plan
    lesson_analysis["material_binding_plan"] = confirmed_plan
    updated["material_binding_plan"] = confirmed_plan
    contract = updated.get("lesson_template_contract") or lesson_analysis.get("lesson_template_contract") or {}
    if isinstance(contract, dict):
        contract = {**contract, "teacher_confirmed": True}
        updated["lesson_template_contract"] = contract
        lesson_analysis["lesson_template_contract"] = contract
        lesson_context["lesson_template_contract"] = contract
    return updated


def has_concrete_music_material(material: dict[str, Any] | None) -> bool:
    if not isinstance(material, dict) or not material:
        return False
    source = _source(material)
    if source.get("source_audio_url"):
        return True
    if source.get("kind") in {
        "midi",
        "musicxml",
        "staff_omr_musicxml",
        "text_score",
        "teacher_confirmed_score_hint",
        "audio_transcribed_midi",
        "audio_phrase_slices",
        "audio_reference",
    }:
        return True
    for phrase in material.get("phrases", []) if isinstance(material.get("phrases"), list) else []:
        if not isinstance(phrase, dict):
            continue
        if phrase.get("target_sequence") or phrase.get("playback_tokens") or phrase.get("main_melody") or phrase.get("audio_clip_url"):
            return True
    return bool(_companion_materials(material))


def apply_material_binding_to_workflow(workflow: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    updated = copy.deepcopy(workflow)
    updated["material_binding_plan"] = plan
    source = updated.setdefault("source", {})
    if isinstance(source, dict):
        source["material_binding_plan"] = plan
    proposal_card = updated.setdefault("proposal_card", {})
    if isinstance(proposal_card, dict):
        proposal_card["material_binding_plan"] = plan
    instance = updated.setdefault("instance", {})
    config = instance.setdefault("config", {}) if isinstance(instance, dict) else {}
    scene_config = config.setdefault("scene_config", {}) if isinstance(config, dict) else {}
    if isinstance(config, dict):
        config["material_binding_plan"] = plan
    if isinstance(scene_config, dict):
        scene_config["material_binding_plan"] = plan
        audio_sync = _lesson_audio_sync_from_plan(plan)
        if audio_sync and not scene_config.get("lesson_audio_sync"):
            scene_config["lesson_audio_sync"] = audio_sync
            scene_config["audio_mode"] = "lesson_audio"
    return updated


def _binding_for_slot(
    slot: dict[str, Any],
    index: int,
    score_units: list[dict[str, Any]],
    audio_units: list[dict[str, Any]],
    selected_id: str,
    material: dict[str, Any],
) -> dict[str, Any]:
    kind = str(slot.get("kind") or "")
    score_unit = _select_unit(score_units, index, selected_id)
    audio_unit = _select_unit(audio_units, index, selected_id)
    if kind == "playback":
        unit = audio_unit or score_unit
        return _drop_empty(
            {
                "slot": slot.get("slot", ""),
                "slot_label": slot.get("label", ""),
                "slot_kind": kind,
                "required": bool(slot.get("required")),
                "source_kind": "audio_clip" if unit and unit.get("audio_clip_url") else "source_audio" if _source(material).get("source_audio_url") else unit.get("source_kind", "") if unit else "",
                "source_id": unit.get("id", "") if unit else "",
                "display_label": unit.get("label", "") if unit else "",
                "answer_data": {},
                "playback_tokens": (unit or {}).get("playback_tokens", []),
                "playback_url": (unit or {}).get("audio_clip_url") or _source(material).get("source_audio_url") or "",
                "confidence": _confidence(unit, material),
                "needs_teacher_confirmation": True,
            }
        )
    unit = score_unit or audio_unit
    return _drop_empty(
        {
            "slot": slot.get("slot", ""),
            "slot_label": slot.get("label", ""),
            "slot_kind": kind,
            "required": bool(slot.get("required")),
            "source_kind": unit.get("source_kind", "") if unit else "",
            "source_id": unit.get("id", "") if unit else "",
            "display_label": unit.get("label", "") if unit else "",
            "answer_data": _answer_data(unit or {}),
            "playback_url": (unit or {}).get("audio_clip_url", ""),
            "confidence": _confidence(unit, material),
            "needs_teacher_confirmation": True,
        }
    )


def _score_units(material: dict[str, Any]) -> list[dict[str, Any]]:
    return [unit for unit in _all_phrase_units(material) if unit.get("has_answer")]


def _audio_units(material: dict[str, Any]) -> list[dict[str, Any]]:
    units = [unit for unit in _all_phrase_units(material) if unit.get("audio_clip_url")]
    if units:
        return units
    token_units = [unit for unit in _all_phrase_units(material) if unit.get("playback_tokens")]
    if token_units:
        return token_units
    source = _source(material)
    if source.get("source_audio_url"):
        return [
            {
                "id": "source_audio",
                "label": material.get("song_title") or "整段音频",
                "source_kind": "source_audio",
                "audio_clip_url": source.get("source_audio_url"),
                "has_answer": False,
            }
        ]
    return []


def _all_phrase_units(material: dict[str, Any]) -> list[dict[str, Any]]:
    units: list[dict[str, Any]] = []
    for source_material in [material, *_companion_materials(material)]:
        source = _source(source_material)
        source_kind = _source_kind(source_material)
        for index, phrase in enumerate(source_material.get("phrases", []) if isinstance(source_material.get("phrases"), list) else [], start=1):
            if not isinstance(phrase, dict):
                continue
            target_sequence = phrase.get("target_sequence", []) if isinstance(phrase.get("target_sequence"), list) else []
            playback_tokens = phrase.get("playback_tokens", []) if isinstance(phrase.get("playback_tokens"), list) else []
            main_melody = phrase.get("main_melody", []) if isinstance(phrase.get("main_melody"), list) else []
            units.append(
                {
                    "id": str(phrase.get("id") or f"phrase_{index}"),
                    "label": str(phrase.get("label") or f"第{index}乐句"),
                    "source_kind": _binding_source_kind(source_kind),
                    "target_sequence": target_sequence,
                    "playback_tokens": playback_tokens,
                    "main_melody": main_melody,
                    "rhythm_features": phrase.get("rhythm_features", []) if isinstance(phrase.get("rhythm_features"), list) else [],
                    "audio_clip_url": phrase.get("audio_clip_url") or "",
                    "has_answer": bool(target_sequence or playback_tokens or main_melody),
                    "requires_manual_confirmation": bool(source.get("requires_manual_confirmation")),
                    "analysis_quality": source.get("analysis_quality", ""),
                }
            )
    return units


def _companion_materials(material: dict[str, Any]) -> list[dict[str, Any]]:
    source = _source(material)
    companions = source.get("companion_materials", [])
    return [item for item in companions if isinstance(item, dict)]


def _select_unit(units: list[dict[str, Any]], index: int, selected_id: str) -> dict[str, Any]:
    if selected_id:
        for unit in units:
            if unit.get("id") == selected_id:
                return unit
    return units[index % len(units)] if units else {}


def _binding_has_required_material(binding: dict[str, Any]) -> bool:
    return bool(binding.get("playback_url") or binding.get("source_id") or binding.get("answer_data") or binding.get("playback_tokens"))


def _component_landing_from_bindings(bindings: list[dict[str, Any]]) -> dict[str, Any]:
    component_slots: list[str] = []
    judgement_slots: list[str] = []
    playback_slots: list[str] = []
    missing_required_slots: list[str] = []
    teacher_summary: list[str] = []
    for binding in bindings:
        if not isinstance(binding, dict):
            continue
        slot = str(binding.get("slot") or "").strip()
        if not slot:
            continue
        kind = str(binding.get("slot_kind") or "")
        has_material = _binding_has_required_material(binding)
        has_kind_material = _binding_has_slot_kind_material(binding)
        if binding.get("required") and not has_material:
            missing_required_slots.append(slot)
        if kind == "playback" and has_material:
            component_slots.append(slot)
            playback_slots.append(slot)
        elif kind in {"tokens", "score"} and has_kind_material:
            playback_slots.append(slot)
        elif kind == "answer" and has_kind_material:
            judgement_slots.append(slot)
        if binding.get("required") and has_material and not has_kind_material:
            missing_required_slots.append(slot)
        if has_material:
            label = str(binding.get("slot_label") or slot)
            if kind == "answer":
                teacher_summary.append(f"{_friendly_material_label(label)}进入{slot}通关判定。")
            elif kind in {"tokens", "score"}:
                teacher_summary.append(f"{_friendly_material_label(label)}进入{slot}播放或谱面组件。")
            else:
                teacher_summary.append(f"{label}进入{slot}试听组件。")
    return {
        "component_slots": list(dict.fromkeys(component_slots)),
        "judgement_slots": list(dict.fromkeys(judgement_slots)),
        "playback_slots": list(dict.fromkeys(playback_slots)),
        "missing_required_slots": list(dict.fromkeys(missing_required_slots)),
        "teacher_summary": teacher_summary,
    }


def _binding_has_slot_kind_material(binding: dict[str, Any]) -> bool:
    kind = str(binding.get("slot_kind") or "")
    if kind == "answer":
        return bool(binding.get("answer_data"))
    if kind in {"tokens", "score"}:
        return bool(binding.get("playback_tokens") or binding.get("answer_data"))
    return _binding_has_required_material(binding)


def _friendly_material_label(label: str) -> str:
    if "节奏答案" in label:
        return "目标节奏"
    if "音高路线" in label:
        return "目标旋律"
    if "唱名答案" in label:
        return "目标唱名"
    if "强弱拍答案" in label:
        return "强弱拍答案"
    return label


def _answer_data(unit: dict[str, Any]) -> dict[str, Any]:
    return _drop_empty(
        {
            "target_sequence": unit.get("target_sequence", []),
            "playback_tokens": unit.get("playback_tokens", []),
            "main_melody": unit.get("main_melody", []),
            "rhythm_features": unit.get("rhythm_features", []),
        }
    )


def _public_unit(unit: dict[str, Any]) -> dict[str, Any]:
    return _drop_empty(
        {
            "id": unit.get("id", ""),
            "label": unit.get("label", ""),
            "source_kind": unit.get("source_kind", ""),
            "answer_data": _answer_data(unit),
            "playback_tokens": unit.get("playback_tokens", []),
            "playback_url": unit.get("audio_clip_url", ""),
            "confidence": unit.get("analysis_quality", ""),
        }
    )


def _lesson_audio_sync_from_plan(plan: dict[str, Any]) -> dict[str, Any]:
    for binding in plan.get("bindings", []) if isinstance(plan.get("bindings"), list) else []:
        if not isinstance(binding, dict):
            continue
        if binding.get("playback_url"):
            return {
                "audio_url": binding.get("playback_url"),
                "segment_label": binding.get("display_label") or binding.get("slot_label") or "作品片段",
            }
    return {}


def _confidence(unit: dict[str, Any] | None, material: dict[str, Any]) -> str:
    if unit and unit.get("requires_manual_confirmation"):
        return "low"
    quality = str((unit or {}).get("analysis_quality") or _source(material).get("analysis_quality") or "")
    if quality in {"high", "confirmed"}:
        return "high"
    if quality in {"medium", "parsed"}:
        return "medium"
    return "medium" if unit else "missing"


def _source(material: dict[str, Any]) -> dict[str, Any]:
    return material.get("source", {}) if isinstance(material, dict) and isinstance(material.get("source"), dict) else {}


def _source_kind(material: dict[str, Any]) -> str:
    return str(_source(material).get("kind") or "")


def _binding_source_kind(source_kind: str) -> str:
    if source_kind in {"midi", "musicxml", "staff_omr_musicxml"}:
        return "score"
    if source_kind in {"text_score", "teacher_confirmed_score_hint"}:
        return "text_score"
    if source_kind == "audio_transcribed_midi":
        return "midi_transcription"
    if source_kind in {"audio_phrase_slices", "audio_reference"}:
        return "audio_clip"
    return source_kind or "score"


def _unsupported_reason(template_id: str, template_decision: dict[str, Any]) -> str:
    if not template_id:
        return template_decision.get("reason") or "当前教案重点没有命中可交付成熟模板。"
    template = get_game_template(template_id) or {}
    if template.get("runtime_status") != "production":
        return f"模板“{template_id}”还不是可交付运行时。"
    return ""


def _drop_empty(value: dict[str, Any]) -> dict[str, Any]:
    return {key: item for key, item in value.items() if item not in ("", None, [], {})}
