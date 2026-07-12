from __future__ import annotations

from copy import deepcopy
import re
from typing import Any

from app.services.music.pitch_catalog import PITCH_DEFINITIONS, pitch_tokens_from_text, resolve_pitch_token

from app.services.games.auto_template_match_resolver import resolve_auto_template_match
from app.services.games.game_template_registry import get_game_template
from app.services.materials.music_element_resolver import retrieve_music_element_candidates


MUSIC_ELEMENT_ADJUSTMENT_VERSION = "music_element_adjustment_contract_v1"

PRODUCTION_TEMPLATE_IDS = {
    "beat_guardian_core",
    "pitch_ladder_core",
    "rhythm_echo_core",
    "solfege_target_core",
    "timbre_detective_core",
    "form_treasure_core",
    "composition_puzzle_core",
}

TEMPLATE_OVERRIDE_ALLOWLIST: dict[str, set[str]] = {
    "rhythm_echo_core": {
        "template_id",
        "difficulty",
        "skin_id",
        "music_concept",
        "teacher_prompt",
        "pattern_steps",
        "bpm",
        "bars_per_round",
        "timing_tolerance_ms",
        "mode",
        "round_count",
        "allow_relisten",
    },
    "beat_guardian_core": {
        "template_id",
        "difficulty",
        "skin_id",
        "music_concept",
        "teacher_prompt",
        "meter",
        "target_beats",
        "mode",
        "bpm",
        "round_count",
        "bars_per_round",
        "timing_tolerance_ms",
        "allow_relisten",
    },
    "pitch_ladder_core": {
        "template_id",
        "difficulty",
        "skin_id",
        "music_concept",
        "teacher_prompt",
        "pitch_range",
        "mode",
        "notes_per_round",
        "tonic",
        "scale_type",
        "show_solfege_hint",
        "show_direction_hint",
        "show_staff_hint",
        "require_sing_back",
        "sing_back_required",
        "retry_limit",
        "pass_score",
        "mistake_limit",
        "round_count",
        "allow_relisten",
    },
    "solfege_target_core": {
        "template_id",
        "difficulty",
        "skin_id",
        "music_concept",
        "teacher_prompt",
        "target_solfege",
        "mode",
        "notes_per_round",
        "require_sing_back",
        "sing_back_required",
        "solfege_system",
        "show_solfege_hint",
        "round_count",
        "allow_relisten",
    },
    "timbre_detective_core": {
        "template_id",
        "difficulty",
        "skin_id",
        "music_concept",
        "teacher_prompt",
        "instrument_pool",
        "timbre_traits",
        "mode",
        "choices_per_round",
        "evidence_required",
        "show_wave_hint",
        "show_family_hint",
        "round_count",
        "allow_relisten",
    },
    "form_treasure_core": {
        "template_id",
        "difficulty",
        "skin_id",
        "music_concept",
        "teacher_prompt",
        "form_type",
        "mode",
        "section_length_bars",
        "hint_mode",
        "round_count",
        "allow_relisten",
    },
    "composition_puzzle_core": {
        "template_id",
        "difficulty",
        "skin_id",
        "music_concept",
        "teacher_prompt",
        "mode",
        "phrase_length_bars",
        "slots_per_bar",
        "constraint_profile",
        "rhythm_cards",
        "melody_cards",
        "required_elements",
        "teacher_confirm_required",
        "round_count",
        "allow_relisten",
    },
}

PITCH_ORDER = [str(pitch["id"]) for pitch in PITCH_DEFINITIONS]
INSTRUMENTS = ["笛子", "长笛", "二胡", "小提琴", "古筝", "钢琴", "木鱼", "小鼓", "锣", "钹"]
TIMBRE_TRAITS = ["明亮", "柔和", "短促", "持续", "气息感", "弦鸣", "敲击感"]
UNSUPPORTED_EXPRESSION_KEYWORDS = ("力度", "强弱变化", "渐强", "渐弱", "速度", "快慢", "表情", "情绪变化")


def build_music_element_adjustment_contract(
    *,
    lesson_analysis: dict[str, Any],
    lesson_fit: dict[str, Any] | None = None,
    lesson_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Translate a lesson focus into safe template-level music-parameter changes."""

    lesson_context = _dict_value(lesson_context or lesson_analysis.get("lesson_context"))
    lesson_fit = _dict_value(lesson_fit or lesson_context.get("lesson_fit") or lesson_analysis.get("lesson_fit"))
    evidence = _dict_value(lesson_fit.get("lesson_evidence"))
    template_hint = _dict_value(lesson_fit.get("template_hint"))
    primary_element = _first_text(
        evidence.get("music_element"),
        lesson_context.get("target_music_element"),
        _dict_value(lesson_analysis.get("specific_focus")).get("element"),
        (_list_value(lesson_analysis.get("music_elements")) or [""])[0],
        "综合音乐感知",
    )
    source_text = _compact_join(
        [
            primary_element,
            evidence.get("target_objective"),
            evidence.get("target_stage"),
            evidence.get("segment_task"),
            evidence.get("gameable_point"),
            lesson_context.get("target_objective"),
            lesson_context.get("target_segment_task"),
            lesson_context.get("target_segment_gameable_point"),
            _dict_value(lesson_analysis.get("recommended_game")).get("name"),
            _dict_value(lesson_analysis.get("recommended_game")).get("mechanic"),
        ]
    )
    auto_match = resolve_auto_template_match(
        lesson_analysis=lesson_analysis,
        lesson_fit=lesson_fit,
        lesson_context=lesson_context,
    )
    template_id = str(auto_match.get("template_id") or template_hint.get("template_id") or "").strip()
    retrieval = retrieve_music_element_candidates(
        semantic_text=source_text,
        song_material=_dict_value(lesson_context.get("song_material")),
        template_id=template_id,
    )
    selected_candidate = _selected_entity_candidate(retrieval, template_id)
    element_family = str(auto_match.get("element_family") or _element_family(source_text, template_id))
    unsupported = _unsupported_elements(primary_element, template_id, element_family)
    if auto_match.get("status") == "unsupported":
        unsupported = _list_value(auto_match.get("unsupported_elements")) or unsupported

    if not template_id or template_id not in PRODUCTION_TEMPLATE_IDS or unsupported:
        return _contract(
            status="unsupported",
            primary_element=primary_element,
            element_family=element_family or "unsupported",
            evidence=evidence.get("evidence") or evidence.get("segment_task") or source_text,
            template_id="" if unsupported else template_id,
            reason=str(auto_match.get("reason") or _unsupported_reason(unsupported, template_id)),
            confidence=0.0,
            config_overrides={},
            element_adjustments=[],
            unsupported_elements=unsupported,
            conflicts=_list_value(auto_match.get("conflicts")),
            basis=str(auto_match.get("basis") or ""),
        )

    raw_overrides = {
        **_dict_value(template_hint.get("config_overrides")),
        **_overrides_for_template(template_id, source_text, primary_element),
        **_overrides_from_entity_candidate(template_id, selected_candidate),
    }
    raw_overrides["music_concept"] = primary_element
    config_overrides = filter_template_config_overrides(template_id, raw_overrides)
    default_config = _dict_value((get_game_template(template_id) or {}).get("default_config"))
    adjustments = _element_adjustments(config_overrides, default_config, element_family)
    confidence = _confidence(source_text, template_id, config_overrides)
    status = "ready" if adjustments or config_overrides else "needs_confirmation"

    return _contract(
        status=status,
        primary_element=primary_element,
        element_family=element_family,
        evidence=evidence.get("evidence") or evidence.get("segment_task") or source_text,
        template_id=template_id,
        reason=str(auto_match.get("reason") or _reason_for_template(template_id, primary_element)),
        confidence=max(confidence, float(auto_match.get("confidence") or 0.0)),
        config_overrides=config_overrides,
        element_adjustments=adjustments,
        unsupported_elements=[],
        conflicts=_list_value(auto_match.get("conflicts")),
        basis=str(auto_match.get("basis") or ""),
        music_element_retrieval=retrieval,
        selected_entity_candidate=selected_candidate,
        entity_application=_entity_application(template_id, selected_candidate, config_overrides),
    )


def attach_music_element_adjustment_contract(
    lesson_analysis: dict[str, Any],
    *,
    lesson_fit: dict[str, Any] | None = None,
) -> dict[str, Any]:
    enriched = deepcopy(lesson_analysis)
    lesson_context = enriched.setdefault("lesson_context", {})
    fit = lesson_fit or lesson_context.get("lesson_fit") or enriched.get("lesson_fit") or {}
    contract = build_music_element_adjustment_contract(
        lesson_analysis=enriched,
        lesson_fit=fit if isinstance(fit, dict) else {},
        lesson_context=lesson_context,
    )
    if isinstance(fit, dict) and fit:
        fit = _merge_contract_into_lesson_fit(fit, contract)
        lesson_context["lesson_fit"] = fit
        enriched["lesson_fit"] = fit
    lesson_context["music_element_adjustment_contract"] = contract
    enriched["music_element_adjustment_contract"] = contract
    return enriched


def filter_template_config_overrides(template_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    allowed = TEMPLATE_OVERRIDE_ALLOWLIST.get(str(template_id or ""), set())
    if not allowed or not isinstance(payload, dict):
        return {}
    normalized = dict(payload)
    if template_id == "pitch_ladder_core" and "require_sing_back" in normalized:
        normalized["sing_back_required"] = normalized["require_sing_back"]
        normalized.pop("require_sing_back", None)
    return {key: deepcopy(value) for key, value in normalized.items() if key in allowed}


def confirmed_template_options(
    *,
    template_options: dict[str, Any] | None = None,
    adjustment_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    template_options = _dict_value(template_options)
    adjustment_payload = _dict_value(adjustment_payload)
    adjustment_template_id = str(_dict_value(adjustment_payload.get("template_match")).get("template_id") or "").strip()
    template_id = str(
        adjustment_template_id
        or template_options.get("template_id")
        or ""
    ).strip()
    if not template_id:
        return {}
    confirmed = filter_template_config_overrides(template_id, template_options)
    confirmed["template_id"] = template_id

    adjustment_overrides = filter_template_config_overrides(
        template_id,
        _dict_value(adjustment_payload.get("config_overrides")),
    )
    merged = {**adjustment_overrides, **confirmed, "template_id": template_id}
    if template_id == "pitch_ladder_core" and str(template_options.get("template_id") or "").strip() == template_id:
        merged["_strict_teacher_config"] = True
    return merged


def _merge_contract_into_lesson_fit(lesson_fit: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    updated = deepcopy(lesson_fit)
    updated["music_element_adjustment_contract"] = contract
    template_hint = updated.setdefault("template_hint", {})
    if not isinstance(template_hint, dict):
        template_hint = {}
        updated["template_hint"] = template_hint
    if contract.get("template_match", {}).get("template_id"):
        template_hint["template_id"] = contract["template_match"]["template_id"]
        template_hint["match_status"] = template_hint.get("match_status") or "exact"
    if contract.get("status") == "unsupported":
        template_hint["template_id"] = ""
        template_hint["match_status"] = "unmatched"
    existing = _dict_value(template_hint.get("config_overrides"))
    template_hint["config_overrides"] = {
        **filter_template_config_overrides(str(contract.get("template_match", {}).get("template_id") or ""), existing),
        **_dict_value(contract.get("config_overrides")),
    }
    return updated


def _overrides_for_template(template_id: str, text: str, primary_element: str) -> dict[str, Any]:
    if template_id == "beat_guardian_core":
        return _beat_overrides(text)
    if template_id == "rhythm_echo_core":
        return _rhythm_overrides(text)
    if template_id == "pitch_ladder_core":
        return _pitch_overrides(text)
    if template_id == "solfege_target_core":
        return _solfege_overrides(text)
    if template_id == "timbre_detective_core":
        return _timbre_overrides(text)
    if template_id == "form_treasure_core":
        return _form_overrides(text)
    if template_id == "composition_puzzle_core":
        return _composition_overrides(text)
    return {"music_concept": primary_element}


def _beat_overrides(text: str) -> dict[str, Any]:
    overrides: dict[str, Any] = {}
    if _has_any(text, ("三拍", "3/4")):
        overrides["meter"] = "3/4"
    elif _has_any(text, ("二拍", "2/4")):
        overrides["meter"] = "2/4"
    elif _has_any(text, ("四拍", "4/4")):
        overrides["meter"] = "4/4"
    if _has_any(text, ("每拍", "全部拍")):
        overrides["mode"] = "beat_defense"
        overrides["target_beats"] = [1, 2]
    elif _has_any(text, ("拍号", "几拍子")):
        overrides["mode"] = "meter_gate"
    elif _has_any(text, ("强拍", "弱拍", "第1拍", "第一拍")):
        overrides["mode"] = "strong_beat_guard"
        overrides["target_beats"] = [1]
    return overrides


def _rhythm_overrides(text: str) -> dict[str, Any]:
    steps = ["quarter", "eighth_pair"]
    if _has_any(text, ("休止", "空拍")):
        steps.append("rest")
    if _has_any(text, ("切分", "syncopation")):
        steps.append("syncopation")
    if _has_any(text, ("附点", "dotted")):
        steps.append("dotted_quarter")
    if _has_any(text, ("二分", "长音")) and "half" not in steps:
        steps.append("half")
    overrides: dict[str, Any] = {"pattern_steps": steps}
    bpm = _extract_int(text, (r"\bBPM\s*(\d{2,3})\b", r"速度\s*(\d{2,3})", r"每分钟\s*(\d{2,3})\s*拍"))
    if bpm:
        overrides["bpm"] = bpm
    bars_per_round = _extract_int(text, (r"每轮\s*(\d+)\s*小节", r"每回合\s*(\d+)\s*小节"))
    if bars_per_round:
        overrides["bars_per_round"] = bars_per_round
    if _has_any(text, ("身体", "拍腿", "跺脚", "律动")):
        overrides["mode"] = "echo_body_percussion"
    if _has_any(text, ("接龙", "创编")):
        overrides["mode"] = "echo_chain"
    return overrides


def _pitch_overrides(text: str) -> dict[str, Any]:
    pitches = _solfege_tokens(text)
    overrides: dict[str, Any] = {}
    if pitches:
        overrides["pitch_range"] = pitches
    if _has_any(text, ("旋律", "音列", "走向", "上行", "下行", "级进", "跳进")):
        overrides["mode"] = "melody_climb"
        if len(pitches) >= 3:
            overrides["notes_per_round"] = min(5, max(3, len(pitches)))
    elif _has_any(text, ("唱名", "do", "re", "mi", "sol", "la")):
        overrides["mode"] = "solfege_ladder"
    return overrides


def _solfege_overrides(text: str) -> dict[str, Any]:
    pitches = _solfege_tokens(text)
    overrides: dict[str, Any] = {"require_sing_back": True, "sing_back_required": True}
    if pitches:
        overrides["target_solfege"] = pitches
    if len(pitches) >= 2 or _has_any(text, ("连环", "音组", "音列")):
        overrides["mode"] = "target_chain"
        overrides["notes_per_round"] = min(4, max(2, len(pitches) or 2))
    elif _has_any(text, ("唱回", "模唱", "内听")):
        overrides["mode"] = "aim_and_sing"
    return overrides


def _timbre_overrides(text: str) -> dict[str, Any]:
    instruments = [item for item in INSTRUMENTS if item in text]
    traits = [item for item in TIMBRE_TRAITS if item in text]
    overrides: dict[str, Any] = {}
    if len(instruments) >= 2:
        overrides["instrument_pool"] = instruments[:6]
    if traits:
        merged = traits[:]
        for fallback in TIMBRE_TRAITS:
            if len(merged) >= 3:
                break
            if fallback not in merged:
                merged.append(fallback)
        overrides["timbre_traits"] = merged[:7]
    if _has_any(text, ("家族", "管乐", "弦乐", "打击乐")):
        overrides["mode"] = "family_sorting"
    if _has_any(text, ("比较", "对比", "相似")):
        overrides["mode"] = "compare_twins"
        overrides["evidence_required"] = 2
    return overrides


def _form_overrides(text: str) -> dict[str, Any]:
    if "回旋" in text:
        return {"form_type": "回旋", "mode": "rondo_treasure"}
    if "ABA" in text.upper() or "A-B-A" in text.upper():
        return {"form_type": "ABA", "mode": "aba_treasure"}
    if _has_any(text, ("重复对比", "重复与对比", "对比")):
        return {"form_type": "重复对比", "mode": "repeat_contrast"}
    return {}


def _composition_overrides(text: str) -> dict[str, Any]:
    overrides: dict[str, Any] = {}
    if _has_any(text, ("旋律节奏拼图", "音符拼图", "旋律和节奏", "音高和时值")):
        overrides["mode"] = "melody_rhythm_puzzle"
        overrides["skin_id"] = "composition_studio"
    elif _has_any(text, ("旋律拼图", "旋律创作", "音级创编", "旋律短句")):
        overrides["mode"] = "melody_puzzle_creation"
        overrides["skin_id"] = "melody_garden"
    elif _has_any(text, ("节奏拼图", "节奏创编", "时值拼图", "休止", "附点", "切分")):
        overrides["mode"] = "rhythm_puzzle_composition"
        overrides["skin_id"] = "rhythm_tile_table"
    bars = _extract_int(text, (r"(\d+)\s*小节", r"(\d+)\s*bar"))
    if bars:
        overrides["phrase_length_bars"] = min(4, max(1, bars))
    if _has_any(text, ("挑战", "少提示", "开放")):
        overrides["constraint_profile"] = "challenge"
    elif _has_any(text, ("引导", "低年级", "提示")):
        overrides["constraint_profile"] = "guided"
    else:
        overrides["constraint_profile"] = "balanced"
    pitches = _solfege_tokens(text)
    if pitches:
        overrides["melody_cards"] = pitches[:8]
    rhythm_ids: list[str] = []
    if _has_any(text, ("四分", "ta")):
        rhythm_ids.append("quarter")
    if _has_any(text, ("八分", "ti-ti")):
        rhythm_ids.append("eighth_pair")
    if _has_any(text, ("休止", "空拍")):
        rhythm_ids.append("rest")
    if _has_any(text, ("附点", "dotted")):
        rhythm_ids.append("dotted_quarter")
    if _has_any(text, ("切分", "syncopation")):
        rhythm_ids.append("syncopation")
    if rhythm_ids:
        overrides["rhythm_cards"] = rhythm_ids
    return overrides


def _selected_entity_candidate(retrieval: dict[str, Any], template_id: str) -> dict[str, Any]:
    candidates = retrieval.get("candidates") if isinstance(retrieval.get("candidates"), list) else []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        match = _dict_value(candidate.get("template_match"))
        if str(match.get("template_id") or "").strip() == template_id:
            return deepcopy(candidate)
    return deepcopy(candidates[0]) if candidates and isinstance(candidates[0], dict) else {}


def _overrides_from_entity_candidate(template_id: str, candidate: dict[str, Any]) -> dict[str, Any]:
    entity = _dict_value(candidate.get("entity"))
    canonical = _dict_value(candidate.get("canonical_element"))
    if template_id == "composition_puzzle_core":
        degrees = _standardize_pitch_cards(_string_list(entity.get("scale_degrees") or entity.get("melody_cards")))
        if degrees and canonical.get("entity_type") in {"scale", "composition_material"}:
            return {
                "mode": "melody_puzzle_creation",
                "skin_id": "melody_garden",
                "melody_cards": degrees[:8],
                "required_elements": degrees[:8],
                "constraint_profile": "guided",
            }
    return {}


def _entity_application(template_id: str, candidate: dict[str, Any], config_overrides: dict[str, Any]) -> dict[str, Any]:
    if not candidate:
        return {}
    canonical = _dict_value(candidate.get("canonical_element"))
    entity = _dict_value(candidate.get("entity"))
    slots: dict[str, Any] = {}
    if template_id == "beat_guardian_core":
        slots["meter.accent_pattern"] = deepcopy(entity.get("accent_pattern") or [])
        slots["meter.beat_count"] = entity.get("beat_count")
    elif template_id == "rhythm_echo_core":
        playback = _dict_value(entity.get("playback"))
        slots["rhythm.pattern_steps"] = deepcopy(playback.get("pattern_steps") or entity.get("answer_tokens") or [])
        slots["rhythm.duration_beats"] = deepcopy(entity.get("duration_beats") or [])
    elif template_id == "timbre_detective_core":
        slots["timbre.comparison_pairs"] = deepcopy(entity.get("comparison_pairs") or [])
        slots["timbre.trait_targets"] = deepcopy(entity.get("trait_targets") or {})
    elif template_id == "form_treasure_core":
        slots["form.answer_pattern"] = deepcopy(entity.get("answer_pattern") or [])
        slots["form.timeline_segments"] = deepcopy(entity.get("timeline_segments") or [])
    elif template_id == "composition_puzzle_core":
        slots["composition.constraint_checks"] = deepcopy(entity.get("constraint_checks") or [])
        slots["composition.scale_degrees"] = deepcopy(entity.get("scale_degrees") or entity.get("melody_cards") or [])
    else:
        slots["entity"] = deepcopy(entity)
    return _drop_empty(
        {
            "template_id": template_id,
            "canonical_id": canonical.get("id", ""),
            "entity_type": canonical.get("entity_type", ""),
            "label": canonical.get("label", ""),
            "game_parameters": deepcopy(config_overrides),
            "slot_bindings": slots,
            "requires_teacher_confirmation": bool(candidate.get("requires_teacher_confirmation")),
            "rationale": candidate.get("rationale", ""),
        }
    )


def _element_family(text: str, template_id: str) -> str:
    if template_id == "beat_guardian_core":
        return "meter"
    if template_id == "rhythm_echo_core":
        return "rhythm"
    if template_id == "pitch_ladder_core":
        return "pitch"
    if template_id == "solfege_target_core":
        return "solfege"
    if template_id == "timbre_detective_core":
        return "timbre"
    if template_id == "form_treasure_core":
        return "form"
    if template_id == "composition_puzzle_core":
        return "composition"
    if _has_any(text, UNSUPPORTED_EXPRESSION_KEYWORDS):
        return "expression"
    return ""


def _unsupported_elements(text: str, template_id: str, family: str) -> list[str]:
    unsupported: list[str] = []
    if family in {"meter", "rhythm", "pitch", "solfege", "timbre", "form", "composition"}:
        return unsupported
    if _has_any(text, UNSUPPORTED_EXPRESSION_KEYWORDS):
        unsupported.append("expression")
    return unsupported


def _element_adjustments(
    overrides: dict[str, Any],
    default_config: dict[str, Any],
    element_family: str,
) -> list[dict[str, Any]]:
    adjustments = []
    for key, value in overrides.items():
        if key in {"template_id", "difficulty", "skin_id"}:
            continue
        previous = default_config.get(key)
        adjustments.append(
            {
                "element": element_family or key,
                "from": previous,
                "to": deepcopy(value),
                "template_config_key": key,
                "teacher_label": _teacher_label(key, value),
            }
        )
    return adjustments


def _teacher_label(key: str, value: Any) -> str:
    labels = {
        "meter": "节拍",
        "target_beats": "目标拍位",
        "pattern_steps": "节奏型",
        "pitch_range": "音高范围",
        "target_solfege": "目标唱名",
        "instrument_pool": "音色材料",
        "timbre_traits": "音色证据",
        "form_type": "曲式类型",
        "phrase_length_bars": "短句长度",
        "slots_per_bar": "每小节格数",
        "constraint_profile": "约束强度",
        "rhythm_cards": "节奏素材卡",
        "melody_cards": "旋律素材卡",
        "teacher_confirm_required": "教师确认",
        "mode": "玩法模式",
        "music_concept": "音乐重点",
        "teacher_prompt": "教师提示",
        "bpm": "速度",
    }
    return f"{labels.get(key, key)}：改为{_value_label(value)}"


def _value_label(value: Any) -> str:
    if isinstance(value, list):
        return "、".join(str(item) for item in value)
    return str(value)


def _confidence(text: str, template_id: str, overrides: dict[str, Any]) -> float:
    base = 0.68 if template_id else 0.0
    if overrides:
        base += 0.12
    if template_id == "beat_guardian_core" and _has_any(text, ("强拍", "弱拍", "二拍", "三拍", "拍号")):
        base += 0.1
    if template_id == "rhythm_echo_core" and _has_any(text, ("节奏", "时值", "附点", "切分", "休止")):
        base += 0.1
    if template_id == "pitch_ladder_core" and _has_any(text, ("音高", "旋律", "上行", "下行")):
        base += 0.1
    if template_id == "solfege_target_core" and _has_any(text, ("唱名", "do", "re", "mi", "sol")):
        base += 0.1
    if template_id == "timbre_detective_core" and _has_any(text, ("音色", "乐器", "笛子", "二胡")):
        base += 0.1
    if template_id == "form_treasure_core" and _has_any(text, ("曲式", "ABA", "回旋", "重复")):
        base += 0.1
    if template_id == "composition_puzzle_core" and _has_any(text, ("拼图", "创编", "创作", "旋律节奏", "素材卡")):
        base += 0.12
    return round(min(base, 0.96), 2)


def _reason_for_template(template_id: str, primary_element: str) -> str:
    reasons = {
        "beat_guardian_core": "教案重点要求稳定拍感、拍号或强弱拍判断。",
        "rhythm_echo_core": "教案重点要求节奏听辨、复刻和时值修正。",
        "pitch_ladder_core": "教案重点要求听辨音高关系或旋律走向。",
        "solfege_target_core": "教案重点要求听辨唱名并唱回确认。",
        "timbre_detective_core": "教案重点要求依据声音证据判断音色或乐器。",
        "form_treasure_core": "教案重点要求听辨段落重复、对比或再现关系。",
        "composition_puzzle_core": "教案重点要求学生用节奏、旋律或音符素材进行拼图式创编。",
    }
    return reasons.get(template_id, f"围绕“{primary_element}”生成要素调整。")


def _unsupported_reason(unsupported: list[str], template_id: str) -> str:
    if unsupported:
        return "当前第一版六模板暂不覆盖力度、速度或表情类要素，不能硬套成熟模板。"
    if not template_id:
        return "当前教案重点没有命中可交付成熟模板。"
    return "当前模板不在第一版六个成熟模板范围内。"


def _contract(
    *,
    status: str,
    primary_element: str,
    element_family: str,
    evidence: str,
    template_id: str,
    reason: str,
    confidence: float,
    config_overrides: dict[str, Any],
    element_adjustments: list[dict[str, Any]],
    unsupported_elements: list[str],
    conflicts: list[str] | None = None,
    basis: str = "",
    music_element_retrieval: dict[str, Any] | None = None,
    selected_entity_candidate: dict[str, Any] | None = None,
    entity_application: dict[str, Any] | None = None,
) -> dict[str, Any]:
    template = get_game_template(template_id) or {}
    return {
        "version": MUSIC_ELEMENT_ADJUSTMENT_VERSION,
        "status": status,
        "requires_teacher_confirmation": True,
        "lesson_focus": {
            "primary_element": primary_element,
            "element_family": element_family,
            "evidence": evidence,
        },
        "template_match": {
            "template_id": template_id,
            "template_label": template.get("label", ""),
            "confidence": confidence,
            "reason": reason,
            "basis": basis,
            "conflicts": conflicts or [],
        },
        "element_adjustments": element_adjustments,
        "config_overrides": config_overrides,
        "unsupported_elements": unsupported_elements,
        "music_element_retrieval": deepcopy(music_element_retrieval or {}),
        "selected_entity_candidate": deepcopy(selected_entity_candidate or {}),
        "entity_application": deepcopy(entity_application or {}),
    }


def _solfege_tokens(text: str) -> list[str]:
    return pitch_tokens_from_text(text)


def _has_any(text: str, keywords: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in keywords)


def _extract_int(text: str, patterns: tuple[str, ...]) -> int | None:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None


def _compact_join(values: list[Any]) -> str:
    return " ".join(str(value or "").strip() for value in values if str(value or "").strip())


def _first_text(*values: Any) -> str:
    for value in values:
        text = str(value or "").strip()
        if text:
            return text
    return ""


def _dict_value(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _list_value(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item or "").strip()]


def _standardize_pitch_cards(values: list[str]) -> list[str]:
    gongche_to_solfege = {"宫": "do", "商": "re", "角": "mi", "徵": "sol", "羽": "la"}
    standardized: list[str] = []
    for value in values:
        token = gongche_to_solfege.get(value, value)
        pitch = resolve_pitch_token(token)
        normalized = str(pitch["id"]) if pitch else token
        if normalized and normalized not in standardized:
            standardized.append(normalized)
    return standardized


def _drop_empty(payload: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in payload.items():
        if value in ("", None, [], {}):
            continue
        result[key] = deepcopy(value)
    return result
