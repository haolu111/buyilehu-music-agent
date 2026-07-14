from __future__ import annotations

from copy import deepcopy
import re
from typing import Any

from app.services.auto_template_match_resolver import resolve_auto_template_match
from app.services.music_element_resolver import resolve_music_element_binding, retrieve_music_element_candidates


LESSON_FIT_VERSION = "lesson_fit_v1"
PRODUCTION_TEMPLATE_IDS = {
    "beat_guardian_core",
    "pitch_ladder_core",
    "rhythm_echo_core",
    "solfege_target_core",
    "timbre_detective_core",
    "form_treasure_core",
    "composition_puzzle_core",
}

MECHANISM_TEMPLATE_COMPATIBILITY: dict[str, str] = {
    "meter_gate_game": "beat_guardian_core",
    "meter_orbit_game": "beat_guardian_core",
    "rhythm_echo_chain": "rhythm_echo_core",
    "rhythm_rebuild_challenge": "composition_puzzle_core",
    "constrained_composition_lab": "composition_puzzle_core",
    "composition_puzzle_game": "composition_puzzle_core",
    "melody_rhythm_puzzle": "composition_puzzle_core",
    "note_value_race": "rhythm_echo_core",
    "dotted_rhythm_bounce": "rhythm_echo_core",
    "syncopation_flag_game": "rhythm_echo_core",
    "rest_light_game": "rhythm_echo_core",
    "pitch_ladder_game": "pitch_ladder_core",
    "melody_path_builder": "pitch_ladder_core",
    "melody_path_game": "pitch_ladder_core",
    "interval_step_game": "pitch_ladder_core",
    "sol_mi_pitch_game": "pitch_ladder_core",
    "timbre_detective_match": "timbre_detective_core",
    "timbre_detective_game": "timbre_detective_core",
    "form_treasure_game": "form_treasure_core",
    "form_map_game": "form_treasure_core",
}


def attach_lesson_fit_layer(
    lesson_analysis: dict[str, Any],
    *,
    lesson_source: dict[str, Any] | None = None,
    extra_need: str = "",
) -> dict[str, Any]:
    """Attach a stable lesson-fit contract to the analyzed lesson payload."""
    enriched = deepcopy(lesson_analysis)
    lesson_context = enriched.setdefault("lesson_context", {})
    lesson_fit = build_lesson_fit_layer(enriched, lesson_source=lesson_source, extra_need=extra_need)
    lesson_context["lesson_fit"] = lesson_fit
    lesson_context["template_workflow_hint"] = lesson_fit["template_hint"]
    lesson_context["lesson_fit_rubric"] = lesson_fit["quality_gates"]
    enriched["lesson_fit"] = lesson_fit
    return enriched


def refresh_lesson_fit_template_hint(
    lesson_analysis: dict[str, Any],
    *,
    lesson_source: dict[str, Any] | None = None,
    extra_need: str = "",
) -> dict[str, Any]:
    """Fill a missing/empty template hint without discarding an existing lesson fit."""

    enriched = deepcopy(lesson_analysis)
    lesson_context = enriched.setdefault("lesson_context", {})
    existing_fit = lesson_context.get("lesson_fit") if isinstance(lesson_context.get("lesson_fit"), dict) else {}
    existing_hint = existing_fit.get("template_hint") if isinstance(existing_fit.get("template_hint"), dict) else {}
    if existing_hint.get("template_id") in PRODUCTION_TEMPLATE_IDS:
        lesson_context["template_workflow_hint"] = existing_hint
        enriched["lesson_fit"] = existing_fit
        return enriched

    refreshed_fit = build_lesson_fit_layer(enriched, lesson_source=lesson_source, extra_need=extra_need)
    refreshed_hint = refreshed_fit.get("template_hint", {})
    if refreshed_hint.get("template_id") in PRODUCTION_TEMPLATE_IDS or not existing_fit:
        lesson_context["lesson_fit"] = refreshed_fit
        lesson_context["template_workflow_hint"] = refreshed_hint
        lesson_context["lesson_fit_rubric"] = refreshed_fit["quality_gates"]
        enriched["lesson_fit"] = refreshed_fit
        return enriched

    lesson_context["template_workflow_hint"] = existing_hint
    enriched["lesson_fit"] = existing_fit
    return enriched


def build_lesson_fit_layer(
    lesson_analysis: dict[str, Any],
    *,
    lesson_source: dict[str, Any] | None = None,
    extra_need: str = "",
) -> dict[str, Any]:
    lesson_context = lesson_analysis.get("lesson_context", {}) if isinstance(lesson_analysis.get("lesson_context"), dict) else {}
    recommended = lesson_analysis.get("recommended_game", {}) if isinstance(lesson_analysis.get("recommended_game"), dict) else {}
    music_game = lesson_analysis.get("music_game", {}) if isinstance(lesson_analysis.get("music_game"), dict) else {}
    selected_segment = _dict_value(lesson_context.get("selected_game_segment") or lesson_analysis.get("selected_game_segment"))
    song_material = _dict_value(lesson_context.get("song_material") or lesson_analysis.get("song_material"))
    song_anchor = _dict_value(lesson_context.get("song_anchor_contract") or lesson_analysis.get("song_anchor_contract"))
    selected_phrase = _dict_value(song_anchor.get("selected_phrase"))
    music_element = _first_text(
        lesson_context.get("target_music_element"),
        recommended.get("music_element"),
        (lesson_analysis.get("specific_focus") or {}).get("element") if isinstance(lesson_analysis.get("specific_focus"), dict) else "",
        (lesson_analysis.get("music_elements") or [""])[0] if isinstance(lesson_analysis.get("music_elements"), list) else "",
        "综合音乐感知",
    )
    target_objective = _first_text(
        lesson_context.get("target_objective"),
        lesson_context.get("teaching_objective"),
        recommended.get("goal"),
        lesson_analysis.get("objective_summary"),
        "",
    )
    target_stage = _first_text(
        lesson_context.get("target_stage"),
        selected_segment.get("stage_label"),
        lesson_analysis.get("game_stage"),
        "课堂核心练习环节",
    )
    segment_task = _first_text(
        lesson_context.get("target_segment_task"),
        selected_segment.get("task_summary"),
        recommended.get("task"),
        "",
    )
    gameable_point = _first_text(
        lesson_context.get("target_segment_gameable_point"),
        selected_segment.get("gameable_point"),
        recommended.get("mechanic"),
        music_game.get("core_mechanic"),
        "",
    )
    evidence = _first_text(
        lesson_context.get("lesson_evidence"),
        selected_segment.get("selection_reason"),
        (lesson_analysis.get("specific_focus") or {}).get("evidence") if isinstance(lesson_analysis.get("specific_focus"), dict) else "",
        "",
    )
    song_title = _first_text(
        song_anchor.get("song_title"),
        song_material.get("song_title"),
        lesson_analysis.get("song_name"),
        "当前课例作品",
    )
    selected_phrase_label = _first_text(selected_phrase.get("label"), song_anchor.get("selected_phrase_id"), "")
    target_sequence = _string_list(selected_phrase.get("target_sequence") or song_anchor.get("target_sequence"))
    template_match = _template_for_lesson(
        lesson_context=lesson_context,
        recommended=recommended,
        text=" ".join(
            [
                music_element,
                target_objective,
                target_stage,
                segment_task,
                gameable_point,
                recommended.get("name", ""),
                recommended.get("type", ""),
                extra_need,
            ]
        )
    )
    auto_match = resolve_auto_template_match(
        lesson_analysis=lesson_analysis,
        lesson_fit={
            "lesson_evidence": {
                "target_objective": target_objective,
                "music_element": music_element,
                "target_stage": target_stage,
                "segment_task": segment_task,
                "gameable_point": gameable_point,
                "evidence": evidence,
            },
            "template_hint": {
                "template_id": template_match["template_id"],
                "match_status": template_match["match_status"],
                "match_basis": template_match["match_basis"],
                "reason": template_match["reason"],
            },
        },
        lesson_context=lesson_context,
    )
    template_id = auto_match["template_id"]
    semantic_music_text = " ".join(
        [
            music_element,
            target_objective,
            segment_task,
            gameable_point,
            extra_need,
        ]
    )
    music_element_retrieval = retrieve_music_element_candidates(
        semantic_text=semantic_music_text,
        song_material=song_material,
        template_id=template_id,
    )
    music_element_binding = resolve_music_element_binding(
        semantic_text=semantic_music_text,
        song_material=song_material,
        template_id=template_id,
    )
    config_overrides = _config_overrides_for_template(
        template_id,
        {
            "music_element": music_element,
            "target_objective": target_objective,
            "target_stage": target_stage,
            "song_title": song_title,
            "selected_phrase_label": selected_phrase_label,
            "target_sequence": target_sequence,
            "text": " ".join([music_element, target_objective, gameable_point, extra_need]),
        },
    )
    material_binding = {
        "song_title": song_title,
        "source_kind": (song_material.get("source") or {}).get("kind", "") if isinstance(song_material.get("source"), dict) else "",
        "source_filename": (song_material.get("source") or {}).get("filename", "") if isinstance(song_material.get("source"), dict) else "",
        "selected_phrase_id": song_anchor.get("selected_phrase_id", ""),
        "selected_phrase_label": selected_phrase_label,
        "target_sequence": target_sequence[:16],
        "audio_clip_url": selected_phrase.get("audio_clip_url", ""),
        "requires_manual_confirmation": bool(song_anchor.get("requires_manual_confirmation")),
    }
    transfer_task = _transfer_task(music_element, target_stage, song_title, selected_phrase_label)
    student_task_constraints = {
        "listen_to": _listen_target(song_title, selected_phrase_label, music_element),
        "must_do": segment_task or _student_must_do(template_id, music_element),
        "must_explain": f"学生需要说出和“{music_element}”有关的音乐依据。",
        "must_not": "不能只靠画面、文字或随机点击通关。",
    }
    lesson_contract = _build_lesson_contract(
        objective=target_objective,
        stage=target_stage,
        music_focus=music_element,
        material_binding=material_binding,
        student_task_constraints=student_task_constraints,
        transfer_task=transfer_task,
        selected_segment=selected_segment,
    )
    lesson_fit = {
        "version": LESSON_FIT_VERSION,
        "fit_summary": _fit_summary(song_title, target_stage, music_element, selected_phrase_label),
        "lesson_contract": lesson_contract,
        "lesson_evidence": {
            "target_objective": target_objective,
            "music_element": music_element,
            "target_stage": target_stage,
            "segment_task": segment_task,
            "gameable_point": gameable_point,
            "evidence": evidence,
        },
        "material_binding": material_binding,
        "song_material": deepcopy(song_material),
        "music_element_retrieval": music_element_retrieval,
        "music_element_binding": music_element_binding,
        "student_task_constraints": student_task_constraints,
        "transfer_task": transfer_task,
        "template_hint": {
            "template_id": template_id,
            "match_status": "unmatched" if auto_match["status"] in {"unsupported", "unmatched"} else "exact",
            "match_basis": auto_match["basis"],
            "reason": auto_match["reason"] or _template_reason(template_id, music_element, template_match["reason"]),
            "auto_template_match": auto_match,
            "config_overrides": config_overrides,
        },
        "quality_gates": _quality_gates(
            target_objective=target_objective,
            music_element=music_element,
            target_stage=target_stage,
            segment_task=segment_task,
            material_binding=material_binding,
            music_element_retrieval=music_element_retrieval,
            music_element_binding=music_element_binding,
            transfer_task=transfer_task,
            template_id=template_id,
        ),
        "source": deepcopy(lesson_source or {}),
    }
    lesson_fit["fit_score"] = _fit_score(lesson_fit["quality_gates"])
    return lesson_fit


def _template_for_lesson(
    *,
    lesson_context: dict[str, Any],
    recommended: dict[str, Any],
    text: str,
) -> dict[str, str]:
    mechanic = _first_text(
        (lesson_context.get("music_element_mechanic") or {}).get("mechanism_id")
        if isinstance(lesson_context.get("music_element_mechanic"), dict)
        else "",
        recommended.get("mechanism_id"),
        lesson_context.get("recommended_game_type"),
        recommended.get("type"),
    )
    if mechanic:
        template_id = MECHANISM_TEMPLATE_COMPATIBILITY.get(mechanic, "")
        if template_id:
            return {
                "template_id": template_id,
                "match_status": "exact",
                "match_basis": "mechanism_id",
                "reason": f"教案机制“{mechanic}”可由成熟模板“{template_id}”直接承接。",
            }
        return {
            "template_id": "",
            "match_status": "unmatched",
            "match_basis": "mechanism_id",
            "reason": f"教案机制“{mechanic}”目前没有对应的成熟模板，不能硬套现有玩法。",
        }
    if any(keyword in text for keyword in ("拼图创编", "拼图创作", "节奏拼图", "节奏创编", "时值拼图", "旋律拼图", "旋律创作", "音级创编", "旋律节奏拼图", "音符拼图", "旋律和节奏")):
        return {
            "template_id": "composition_puzzle_core",
            "match_status": "exact",
            "match_basis": "keyword_fallback",
            "reason": "教案重点需要用节奏、旋律或音符素材进行拼图式创编。",
        }
    if any(keyword in text for keyword in ("音色", "乐器", "发声方式", "声音证据", "声音线索", "笛子", "二胡", "小提琴", "钢琴", "木鱼")):
        return {
            "template_id": "timbre_detective_core",
            "match_status": "exact",
            "match_basis": "keyword_fallback",
            "reason": "教案重点要求依据听觉证据识别音色或乐器。",
        }
    if any(keyword in text for keyword in ("曲式", "ABA", "回旋", "重复对比", "段落结构", "主题再现", "段落", "结构")):
        return {
            "template_id": "form_treasure_core",
            "match_status": "exact",
            "match_basis": "keyword_fallback",
            "reason": "教案重点需要听辨段落重复、对比与再现关系。",
        }
    if any(keyword in text for keyword in ("强拍", "弱拍", "节拍", "拍号", "稳拍", "进入时机", "准确进入", "二拍子", "三拍子", "四拍子", "律动")):
        return {
            "template_id": "beat_guardian_core",
            "match_status": "exact",
            "match_basis": "keyword_fallback",
            "reason": "教案重点需要稳定拍感和拍位判断。",
        }
    if any(keyword in text for keyword in ("节奏复刻", "跟拍", "模仿", "接龙", "听后拍回", "听后拍", "节奏", "时值", "附点", "切分", "休止", "拍手", "复刻")):
        return {
            "template_id": "rhythm_echo_core",
            "match_status": "exact",
            "match_basis": "keyword_fallback",
            "reason": "教案重点需要节奏听辨、复刻和修正。",
        }
    if any(keyword in text for keyword in ("音高高低", "旋律走向", "旋律线", "音高", "旋律", "级进", "跳进", "高低", "上行", "下行", "sol-mi")):
        return {
            "template_id": "pitch_ladder_core",
            "match_status": "exact",
            "match_basis": "keyword_fallback",
            "reason": "教案重点需要判断音高关系或旋律走向。",
        }
    if _matches_solfege_text(text):
        return {
            "template_id": "solfege_target_core",
            "match_status": "exact",
            "match_basis": "keyword_fallback",
            "reason": "教案重点是听目标音、确认唱名并唱回。",
        }
    return {
        "template_id": "",
        "match_status": "unmatched",
        "match_basis": "none",
        "reason": "当前成熟模板库还没有能准确承载该教学重点的模板。",
    }


def _config_overrides_for_template(template_id: str, evidence: dict[str, Any]) -> dict[str, Any]:
    text = str(evidence.get("text") or "")
    overrides: dict[str, Any] = {
        "music_concept": evidence.get("music_element") or "综合音乐感知",
        "teacher_prompt": _teacher_prompt(evidence),
    }
    if template_id == "beat_guardian_core":
        if "三拍" in text or "3/4" in text:
            overrides["meter"] = "3/4"
        elif "二拍" in text or "2/4" in text:
            overrides["meter"] = "2/4"
        if "强拍" in text:
            overrides["target_beats"] = [1]
            overrides["mode"] = "strong_beat_guard"
    elif template_id == "pitch_ladder_core":
        pitch_range = _pitch_range_from_sequence(evidence.get("target_sequence"))
        if pitch_range:
            overrides["pitch_range"] = pitch_range
        if any(keyword in text for keyword in ("唱名", "do", "re", "mi")):
            overrides["mode"] = "solfege_ladder"
    elif template_id == "solfege_target_core":
        target_solfege = _pitch_range_from_sequence(evidence.get("target_sequence"))
        if target_solfege:
            overrides["target_solfege"] = target_solfege
    elif template_id == "timbre_detective_core":
        if any(keyword in text for keyword in ("家族", "管乐", "弦乐", "打击乐")):
            overrides["mode"] = "family_sorting"
    elif template_id == "form_treasure_core":
        if "回旋" in text:
            overrides["form_type"] = "回旋"
            overrides["mode"] = "rondo_treasure"
        elif "重复对比" in text or "重复与对比" in text:
            overrides["form_type"] = "重复对比"
            overrides["mode"] = "repeat_contrast"
        elif "ABA" in text:
            overrides["form_type"] = "ABA"
            overrides["mode"] = "aba_treasure"
    elif template_id == "composition_puzzle_core":
        if any(keyword in text for keyword in ("旋律节奏拼图", "音符拼图", "旋律和节奏", "音高和时值")):
            overrides["mode"] = "melody_rhythm_puzzle"
            overrides["skin_id"] = "composition_studio"
        elif any(keyword in text for keyword in ("旋律拼图", "旋律创作", "音级创编")):
            overrides["mode"] = "melody_puzzle_creation"
            overrides["skin_id"] = "melody_garden"
        else:
            overrides["mode"] = "rhythm_puzzle_composition"
            overrides["skin_id"] = "rhythm_tile_table"
        if "挑战" in text or "开放" in text:
            overrides["constraint_profile"] = "challenge"
        elif "引导" in text or "提示" in text:
            overrides["constraint_profile"] = "guided"
        else:
            overrides["constraint_profile"] = "balanced"
    elif template_id == "rhythm_echo_core":
        if any(keyword in text for keyword in ("身体", "拍腿", "跺脚", "律动")):
            overrides["mode"] = "echo_body_percussion"
    return overrides


def _teacher_prompt(evidence: dict[str, Any]) -> str:
    song_title = evidence.get("song_title") or "当前作品"
    phrase_label = evidence.get("selected_phrase_label") or "目标片段"
    music_element = evidence.get("music_element") or "音乐要素"
    objective = evidence.get("target_objective") or f"理解{music_element}"
    return f"先回到《{song_title}》{phrase_label}听辨“{music_element}”，再进入游戏操作；完成后请学生用唱、拍或说解释：{objective}"


def _quality_gates(
    *,
    target_objective: str,
    music_element: str,
    target_stage: str,
    segment_task: str,
    material_binding: dict[str, Any],
    music_element_retrieval: dict[str, Any],
    music_element_binding: dict[str, Any],
    transfer_task: str,
    template_id: str,
) -> list[dict[str, str]]:
    return [
        _gate("objective_alignment", "教学目标对齐", "pass" if target_objective and music_element else "warning", f"目标：{target_objective or music_element}"),
        _gate("classroom_stage", "课堂环节保留", "pass" if target_stage else "warning", f"投放环节：{target_stage or '未明确'}"),
        _gate("segment_task", "环节任务绑定", "pass" if segment_task else "warning", f"环节任务：{segment_task or '需要教师确认'}"),
        _gate(
            "material_binding",
            "作品材料绑定",
            "pass" if material_binding.get("selected_phrase_label") or material_binding.get("target_sequence") else "warning",
            f"作品：{material_binding.get('song_title') or '当前课例作品'} {material_binding.get('selected_phrase_label') or ''}".strip(),
        ),
        _gate(
            "music_element_entity_binding",
            "音乐实体绑定",
            "pass" if music_element_binding.get("status") == "resolved" else "warning",
            (
                f"实体：{(music_element_binding.get('canonical_element') or {}).get('label') or '待确认'}；"
                f"模板槽位：{', '.join(music_element_binding.get('game_slots', [])[:2]) or '待确认'}"
            ),
        ),
        _gate(
            "music_element_retrieval",
            "音乐要素检索候选",
            "pass" if music_element_retrieval.get("candidates") else "warning",
            (
                "候选："
                + ", ".join(
                    str(((candidate.get("template_match") or {}).get("template_id") or ""))
                    for candidate in music_element_retrieval.get("candidates", [])[:3]
                    if isinstance(candidate, dict)
                )
                or "待确认"
            ),
        ),
        _gate("student_agency", "学生学习行为", "pass", "学生必须听、做、解释，不能由游戏替代学习。"),
        _gate("transfer_closure", "课堂迁移闭环", "pass" if transfer_task else "warning", transfer_task or "需要补充游戏后的唱、拍、说或创编任务。"),
        _gate(
            "template_fit",
            "模板匹配",
            "pass" if template_id else "warning",
            f"优先模板：{template_id}" if template_id else "暂无精确匹配模板，将进入教案专属生成。",
        ),
    ]


def _build_lesson_contract(
    *,
    objective: str,
    stage: str,
    music_focus: str,
    material_binding: dict[str, Any],
    student_task_constraints: dict[str, str],
    transfer_task: str,
    selected_segment: dict[str, Any],
) -> dict[str, Any]:
    material_anchor = _lesson_contract_material_anchor(material_binding)
    weak_points: list[str] = []
    if not material_binding.get("selected_phrase_label") and not material_binding.get("target_sequence"):
        weak_points.append("missing_material_anchor")
    if material_binding.get("requires_manual_confirmation"):
        weak_points.append("material_requires_teacher_confirmation")
    confidence_required = bool(weak_points)
    return {
        "version": "lesson_contract_v1",
        "objective": objective,
        "stage": stage,
        "music_focus": music_focus,
        "material_anchor": material_anchor,
        "student_must": {
            "listen": student_task_constraints.get("listen_to", ""),
            "do": student_task_constraints.get("must_do", ""),
            "explain": student_task_constraints.get("must_explain", ""),
            "must_not": student_task_constraints.get("must_not", ""),
        },
        "transfer": {
            "classroom_return": transfer_task,
        },
        "confidence": {
            "overall": 0.62 if confidence_required else 0.88,
            "confirmation_required": confidence_required,
            "weak_points": weak_points,
        },
        "source_trace": {
            "objective": "lesson_context.target_objective",
            "stage": "selected_game_segment.stage_label" if selected_segment.get("stage_label") else "lesson_context.target_stage",
            "music_focus": "lesson_context.target_music_element",
            "material_anchor": _material_anchor_source_trace(material_binding),
            "student_must": "selected_game_segment.task_summary"
            if selected_segment.get("task_summary")
            else "template_capability.student_action",
        },
        "not_selected_tasks": _not_selected_tasks(selected_segment),
    }


def _lesson_contract_material_anchor(material_binding: dict[str, Any]) -> dict[str, Any]:
    has_material = bool(material_binding.get("selected_phrase_label") or material_binding.get("target_sequence"))
    source_kind = material_binding.get("source_kind") or ("song_material.phrases" if has_material else "teacher_confirmation_candidate")
    return {
        "song_title": material_binding.get("song_title", ""),
        "selected_phrase_id": material_binding.get("selected_phrase_id", ""),
        "selected_phrase_label": material_binding.get("selected_phrase_label", ""),
        "source_kind": source_kind,
        "source_filename": material_binding.get("source_filename", ""),
        "target_sequence": deepcopy(material_binding.get("target_sequence", [])),
        "audio_clip_url": material_binding.get("audio_clip_url", ""),
        "confidence": 0.86 if has_material and not material_binding.get("requires_manual_confirmation") else 0.42,
        "requires_teacher_confirmation": bool(material_binding.get("requires_manual_confirmation") or not has_material),
    }


def _material_anchor_source_trace(material_binding: dict[str, Any]) -> str:
    phrase_id = str(material_binding.get("selected_phrase_id") or "").strip()
    if phrase_id:
        return f"song_material.phrases.{phrase_id}"
    if material_binding.get("target_sequence"):
        return "song_material.phrases.target_sequence"
    if material_binding.get("audio_clip_url"):
        return "song_material.audio_clip"
    return "teacher_confirmation_candidate"


def _not_selected_tasks(selected_segment: dict[str, Any]) -> list[dict[str, str]]:
    raw = selected_segment.get("not_selected") if isinstance(selected_segment.get("not_selected"), list) else []
    result: list[dict[str, str]] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        stage = str(item.get("stage") or item.get("stage_label") or "").strip()
        reason = str(item.get("reason") or "").strip()
        if stage or reason:
            result.append({"stage": stage, "reason": reason})
    return result


def _gate(gate_id: str, label: str, status: str, detail: str) -> dict[str, str]:
    return {"id": gate_id, "label": label, "status": status, "detail": detail}


def _fit_score(gates: list[dict[str, str]]) -> int:
    if not gates:
        return 0
    score = 0
    for gate in gates:
        if gate.get("status") == "pass":
            score += 100
        elif gate.get("status") == "warning":
            score += 60
    return round(score / len(gates))


def _fit_summary(song_title: str, target_stage: str, music_element: str, phrase_label: str) -> str:
    phrase = f"的{phrase_label}" if phrase_label else ""
    return f"把《{song_title}》{phrase}放回{target_stage}，用游戏聚焦“{music_element}”。"


def _listen_target(song_title: str, phrase_label: str, music_element: str) -> str:
    if phrase_label:
        return f"聆听《{song_title}》{phrase_label}中和“{music_element}”有关的声音证据"
    return f"聆听《{song_title}》中和“{music_element}”有关的声音证据"


def _student_must_do(template_id: str, music_element: str) -> str:
    if template_id == "beat_guardian_core":
        return f"根据听到的{music_element}观察护盾周期，在每小节第 1 拍到来前预判并同步充能。"
    if template_id == "pitch_ladder_core":
        return f"根据听到的{music_element}选择音高路线或唱名，并用模唱验证。"
    if template_id == "solfege_target_core":
        return f"先听辨{music_element}，再击中对应唱名并唱回确认。"
    if template_id == "timbre_detective_core":
        return f"根据听到的{music_element}找出乐器或音色证据，并说出理由。"
    if template_id == "form_treasure_core":
        return f"根据听到的{music_element}排列段落结构卡，并说出重复、对比或再现依据。"
    if template_id == "composition_puzzle_core":
        return f"围绕{music_element}选择素材卡、拼成短句、试听修正，并说明创编依据。"
    if not template_id:
        return f"围绕“{music_element}”完成与教案目标一致的专属操作，并说出音乐依据。"
    return f"根据听到的{music_element}复刻节奏或完成拍点操作，并根据反馈修正。"


def _transfer_task(music_element: str, target_stage: str, song_title: str, phrase_label: str) -> str:
    phrase = phrase_label or "目标片段"
    return f"游戏后回到{target_stage}：学生在《{song_title}》{phrase}中唱一唱、拍一拍或说一说“{music_element}”的音乐依据。"


def _template_reason(template_id: str, music_element: str, fallback_reason: str = "") -> str:
    if template_id == "beat_guardian_core":
        return f"“{music_element}”需要稳定拍感、重音周期和提前预判，适合充能护盾式节拍守卫模板。"
    if template_id == "pitch_ladder_core":
        return f"“{music_element}”需要听辨高低或唱名映射，适合音高爬梯模板。"
    if template_id == "solfege_target_core":
        return f"“{music_element}”需要先听辨、再定位唱名、最后唱回，适合唱名打靶模板。"
    if template_id == "timbre_detective_core":
        return f"“{music_element}”需要依据声音证据判断乐器或音色，适合音色侦探模板。"
    if template_id == "form_treasure_core":
        return f"“{music_element}”需要听辨段落重复、对比与再现，适合曲式寻宝模板。"
    if template_id == "composition_puzzle_core":
        return f"“{music_element}”需要学生动手拼接并创编音乐短句，适合拼图创编工坊模板。"
    if not template_id:
        return fallback_reason or f"当前模板库还没有能准确承载“{music_element}”的成熟模板，应走教案专属生成。"
    return f"“{music_element}”需要听辨、复刻和修正，适合节奏复刻模板。"


def _pitch_range_from_sequence(sequence: Any) -> list[str]:
    allowed = {"do", "re", "mi", "fa", "sol", "la", "ti", "do_high"}
    result: list[str] = []
    for item in _string_list(sequence):
        normalized = item.strip().lower().replace("'", "_high")
        if normalized in allowed and normalized not in result:
            result.append(normalized)
    return result if len(result) >= 2 else []


def _matches_solfege_text(text: str) -> bool:
    if any(keyword in text for keyword in ("唱名", "听音击中", "模唱确认", "内听", "唱回", "击中唱名", "听辨唱名")):
        return True
    tokens = set(re.findall(r"\b(?:do|re|mi|fa|sol|la|ti)\b", text.lower()))
    return len(tokens) >= 2


def _first_text(*values: Any) -> str:
    for value in values:
        text = str(value or "").strip()
        if text:
            return text
    return ""


def _dict_value(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item or "").strip()]
