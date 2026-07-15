# 根据教案音乐要素和活动机制，自动选择最合适的核心游戏模板
# 这是自动选游戏的核心。

# resolve_auto_template_match() 会综合考虑：

# 教案中出现的音乐要素；
# 已解析出的材料实体；
# 教学目标；
# 学生行为；
# 推荐的交互机制；
# 模板支持范围；
# 当前是否缺少关键材料。
from __future__ import annotations

from copy import deepcopy
import re
from typing import Any

from app.services.games.game_template_registry import get_game_template
from app.services.materials.music_element_resolver import retrieve_music_element_candidates, retrieve_music_element_entities


AUTO_TEMPLATE_MATCH_VERSION = "auto_template_match_v1"

PRODUCTION_TEMPLATE_IDS = {
    "beat_guardian_core",
    "pitch_ladder_core",
    "rhythm_echo_core",
    "solfege_target_core",
    "timbre_detective_core",
    "form_treasure_core",
    "composition_puzzle_core",
}

TEMPLATE_FAMILIES = {
    "beat_guardian_core": "meter",
    "pitch_ladder_core": "pitch",
    "rhythm_echo_core": "rhythm",
    "solfege_target_core": "solfege",
    "timbre_detective_core": "timbre",
    "form_treasure_core": "form",
    "composition_puzzle_core": "composition",
}

FAMILY_TEMPLATE = {family: template_id for template_id, family in TEMPLATE_FAMILIES.items()}

UNSUPPORTED_EXPRESSION_KEYWORDS = ("力度", "声音强弱", "强弱变化", "渐强", "渐弱", "f 与 p", "f和p", "速度", "快慢", "表情", "情绪变化")

FOCUS_KEYWORDS: dict[str, tuple[str, ...]] = {
    "timbre": ("音色", "乐器", "乐器家族", "发声方式", "声音证据", "声音线索", "笛子", "长笛", "二胡", "小提琴", "古筝", "钢琴", "木鱼"),
    "form": ("曲式", "段落结构", "ABA", "A-B-A", "回旋", "重复对比", "重复与对比", "主题再现", "再现"),
    "meter": ("强拍", "弱拍", "节拍", "拍号", "稳拍", "进入时机", "准确进入", "第1拍", "第一拍", "二拍子", "三拍子", "四拍子", "2/4", "3/4", "4/4"),
    "rhythm": ("节奏型", "节奏复刻", "节奏", "时值", "附点", "切分", "休止", "拍手复刻", "跟拍", "接龙", "听后拍回"),
    "pitch": ("音高高低", "旋律走向", "旋律线", "旋律爬坡", "旋律路线", "旋律", "音高", "音域", "级进", "跳进", "上行", "下行", "高低"),
    "solfege": ("唱名", "听音击中", "击中唱名", "听辨唱名", "唱回", "模唱确认", "内听"),
    "composition": ("拼图创编", "拼图创作", "节奏拼图", "节奏创编", "时值拼图", "旋律拼图", "旋律创作", "音级创编", "旋律节奏拼图", "音符拼图", "旋律和节奏", "音乐短句创编", "素材卡创编"),
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


def resolve_auto_template_match(
    *,
    lesson_analysis: dict[str, Any],
    lesson_fit: dict[str, Any] | None = None,
    lesson_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve the authoritative production template from the lesson's music focus."""

    lesson_context = _dict_value(lesson_context or lesson_analysis.get("lesson_context"))
    lesson_fit = _dict_value(lesson_fit or lesson_context.get("lesson_fit") or lesson_analysis.get("lesson_fit"))
    evidence = _dict_value(lesson_fit.get("lesson_evidence"))
    template_hint = _dict_value(lesson_fit.get("template_hint"))
    recommended = _dict_value(lesson_analysis.get("recommended_game"))
    music_game = _dict_value(lesson_analysis.get("music_game"))
    selected_segment = _dict_value(lesson_context.get("selected_game_segment") or lesson_analysis.get("selected_game_segment"))

    focus_text = _compact_join(
        [
            evidence.get("music_element"),
            lesson_context.get("target_music_element"),
            _dict_value(lesson_analysis.get("specific_focus")).get("element"),
            selected_segment.get("music_focus"),
            recommended.get("music_element"),
        ]
    )
    lesson_text = _compact_join(
        [
            focus_text,
            evidence.get("target_objective"),
            evidence.get("target_stage"),
            evidence.get("segment_task"),
            evidence.get("gameable_point"),
            lesson_context.get("target_objective"),
            lesson_context.get("target_segment_task"),
            lesson_context.get("target_segment_gameable_point"),
            recommended.get("mechanic"),
            recommended.get("name"),
            lesson_context.get("recommended_game_name"),
            lesson_context.get("recommended_game_type"),
            music_game.get("recommended_game_name"),
            music_game.get("recommended_game_type"),
            music_game.get("core_mechanic"),
        ]
    )
    hint_template = str(template_hint.get("template_id") or "").strip()
    mechanism_id = _mechanism_id(lesson_context, recommended)
    mechanism_template = MECHANISM_TEMPLATE_COMPATIBILITY.get(mechanism_id, "")
    recommended_template = _template_from_recommended_game(recommended, lesson_context=lesson_context, music_game=music_game)

    unsupported = _unsupported_elements(lesson_text)
    retrieval = retrieve_music_element_candidates(
        semantic_text=focus_text or lesson_text,
        song_material=_dict_value(lesson_context.get("song_material")),
        template_id="",
    )
    entity_lookup = retrieve_music_element_entities(
        semantic_text=focus_text or lesson_text,
        song_material=_dict_value(lesson_context.get("song_material")),
    )
    controlled_match = _controlled_entity_template_match(entity_lookup, hint_template=hint_template)
    retrieval_template = str(retrieval.get("selected_template_id") or "").strip()
    focus_family = _family_from_text(focus_text, include_solfege_tokens=True)
    lesson_family = _family_from_text(lesson_text, include_solfege_tokens=True)
    template_id = ""
    basis = "none"

    if unsupported and not focus_family and not lesson_family:
        template_id = ""
        basis = "mechanism_id" if mechanism_id else "unsupported_expression"
    elif retrieval_template and _retrieval_is_decisive(retrieval):
        template_id = retrieval_template
        basis = "music_element_retrieval"
    elif controlled_match.get("template_id") and not unsupported:
        template_id = controlled_match["template_id"]
        basis = "controlled_music_entity"
    elif focus_family and mechanism_template and mechanism_template == FAMILY_TEMPLATE[focus_family]:
        template_id = mechanism_template
        basis = "mechanism_id"
    elif focus_family:
        template_id = FAMILY_TEMPLATE[focus_family]
        basis = "music_element_keyword"
    elif mechanism_template:
        template_id = mechanism_template
        basis = "mechanism_id"
    elif lesson_family:
        template_id = FAMILY_TEMPLATE[lesson_family]
        basis = "lesson_text_keyword"
    elif recommended_template:
        template_id = recommended_template
        basis = "recommended_game"
    elif hint_template in PRODUCTION_TEMPLATE_IDS:
        template_id = hint_template
        basis = "template_hint"
    elif mechanism_id:
        template_id = ""
        basis = "mechanism_id"

    if template_id and not get_game_template(template_id):
        template_id = ""
        basis = "missing_template"

    family = TEMPLATE_FAMILIES.get(template_id, "expression" if unsupported else "")
    conflicts = _conflicts(
        resolved_template=template_id,
        hint_template=hint_template,
        recommended_template=recommended_template,
    )
    status = "unsupported" if unsupported and not template_id else "ready" if template_id else "unmatched"
    confidence = _confidence(basis, template_id, conflicts)

    return {
        "version": AUTO_TEMPLATE_MATCH_VERSION,
        "status": status,
        "template_id": template_id,
        "template_label": (get_game_template(template_id) or {}).get("label", ""),
        "element_family": family,
        "confidence": confidence,
        "basis": basis,
        "reason": _reason(template_id, family, basis, conflicts, unsupported, controlled_match),
        "evidence": _first_text(evidence.get("evidence"), evidence.get("segment_task"), focus_text, lesson_text),
        "conflicts": conflicts,
        "unsupported_elements": unsupported if status == "unsupported" else [],
        "inputs": {
            "focus_text": focus_text,
            "hint_template_id": hint_template,
            "recommended_template_id": recommended_template,
            "mechanism_template_id": mechanism_template,
            "mechanism_id": mechanism_id,
        },
        "entity_candidates": retrieval.get("candidates", []),
        "music_entity_lookup": entity_lookup,
        "template_capability_match": _auto_template_capability_match(
            template_id=template_id,
            basis=basis,
            controlled_match=controlled_match,
        ),
    }


def _mechanism_id(lesson_context: dict[str, Any], recommended: dict[str, Any]) -> str:
    return _first_text(
        _dict_value(lesson_context.get("music_element_mechanic")).get("mechanism_id"),
        recommended.get("mechanism_id"),
        lesson_context.get("recommended_game_type"),
        recommended.get("type"),
    )


def _template_from_recommended_game(
    recommended: dict[str, Any],
    *,
    lesson_context: dict[str, Any],
    music_game: dict[str, Any],
) -> str:
    text = _compact_join(
        [
            recommended.get("name"),
            recommended.get("type"),
            recommended.get("mechanic"),
            recommended.get("music_element"),
            lesson_context.get("recommended_game_name"),
            lesson_context.get("recommended_game_type"),
            music_game.get("recommended_game_name"),
            music_game.get("recommended_game_type"),
            music_game.get("core_mechanic"),
        ]
    )
    family = _family_from_text(text, include_solfege_tokens=True)
    return FAMILY_TEMPLATE.get(family, "")


def _retrieval_is_decisive(retrieval: dict[str, Any]) -> bool:
    candidates = retrieval.get("candidates") if isinstance(retrieval.get("candidates"), list) else []
    if not candidates:
        return False
    first = candidates[0] if isinstance(candidates[0], dict) else {}
    template_id = str(_dict_value(first.get("template_match")).get("template_id") or "")
    confidence = float(_dict_value(first.get("template_match")).get("confidence") or 0)
    canonical = _dict_value(first.get("canonical_element"))
    return (
        bool(template_id)
        and confidence >= 0.64
        and canonical.get("id") != "generic_music_element"
        and canonical.get("entity_type") in {"scale", "composition_material"}
    )


def _controlled_entity_template_match(entity_lookup: dict[str, Any], *, hint_template: str) -> dict[str, Any]:
    entities = entity_lookup.get("entities") if isinstance(entity_lookup.get("entities"), list) else []
    valid_entities = [
        entity
        for entity in entities
        if isinstance(entity, dict)
        and entity.get("entity_type") != "unknown_music_element"
        and isinstance(entity.get("compatible_template_ids"), list)
        and entity.get("compatible_template_ids")
    ]
    if not valid_entities:
        return {}
    matched = sorted(valid_entities, key=lambda item: float(item.get("confidence") or 0), reverse=True)[0]
    status = "supported" if hint_template and hint_template in matched.get("compatible_template_ids", []) else "recommended"
    return {
        "template_id": matched.get("compatible_template_ids", [""])[0],
        "matched_entity": deepcopy(matched),
        "status": status,
    }


def _auto_template_capability_match(
    *,
    template_id: str,
    basis: str,
    controlled_match: dict[str, Any],
) -> dict[str, Any]:
    matched_entity = controlled_match.get("matched_entity") if isinstance(controlled_match.get("matched_entity"), dict) else {}
    if not matched_entity:
        return {}
    status = "recommended" if basis == "controlled_music_entity" else "supported"
    return {
        "status": status,
        "template_id": template_id,
        "matched_entity": deepcopy(matched_entity),
        "basis": basis,
        "reason": _entity_match_reason(template_id, matched_entity, status),
    }


def _family_from_text(text: str, *, include_solfege_tokens: bool) -> str:
    if not text:
        return ""
    lowered = text.lower()
    if any(keyword.lower() in lowered for keyword in FOCUS_KEYWORDS["composition"]):
        return "composition"
    scores = {
        family: sum(1 for keyword in keywords if keyword.lower() in text.lower())
        for family, keywords in FOCUS_KEYWORDS.items()
    }
    if include_solfege_tokens and not scores["pitch"]:
        tokens = set(re.findall(r"\b(?:do|re|mi|fa|sol|la|ti)\b", text.lower()))
        if len(tokens) >= 2:
            scores["solfege"] += len(tokens)
    best_family, best_score = max(scores.items(), key=lambda item: item[1])
    return best_family if best_score else ""


def _unsupported_elements(text: str) -> list[str]:
    return ["expression"] if any(keyword in text for keyword in UNSUPPORTED_EXPRESSION_KEYWORDS) else []


def _conflicts(*, resolved_template: str, hint_template: str, recommended_template: str) -> list[str]:
    conflicts: list[str] = []
    if resolved_template and hint_template and hint_template != resolved_template:
        conflicts.append("overrode_hint")
    if resolved_template and recommended_template and recommended_template != resolved_template:
        conflicts.append("overrode_recommended_game")
    return conflicts


def _confidence(basis: str, template_id: str, conflicts: list[str]) -> float:
    if not template_id:
        return 0.0
    base = {
        "controlled_music_entity": 0.94,
        "music_element_retrieval": 0.92,
        "music_element_keyword": 0.9,
        "mechanism_id": 0.84,
        "lesson_text_keyword": 0.78,
        "recommended_game": 0.68,
        "template_hint": 0.62,
    }.get(basis, 0.5)
    return round(max(0.55, base - 0.04 * len(conflicts)), 2)


def _reason(
    template_id: str,
    family: str,
    basis: str,
    conflicts: list[str],
    unsupported: list[str],
    controlled_match: dict[str, Any] | None = None,
) -> str:
    if unsupported and not template_id:
        return "当前第一版六模板暂不覆盖力度、速度或表情类要素，不能硬套成熟模板。"
    if not template_id:
        return "当前教案重点没有命中六个成熟模板。"
    if basis == "controlled_music_entity":
        matched_entity = (
            controlled_match.get("matched_entity")
            if isinstance(controlled_match, dict) and isinstance(controlled_match.get("matched_entity"), dict)
            else {}
        )
        semantic_term = matched_entity.get("semantic_term") or matched_entity.get("label") or "音乐要素"
        conflict_note = "；已覆盖旧模板提示" if conflicts else ""
        return f"根据本地音乐要素库识别到“{semantic_term}”可执行实体，优先匹配{template_id}{conflict_note}。"
    family_labels = {
        "meter": "节拍、拍号或强弱拍",
        "rhythm": "节奏型、时值、附点、切分或休止",
        "pitch": "音高高低、旋律走向、级进或跳进",
        "solfege": "唱名听辨、击中唱名或唱回",
        "timbre": "音色、乐器或声音证据",
        "form": "曲式、段落结构、重复对比或再现",
        "composition": "节奏、旋律或音符素材拼图创编",
    }
    conflict_note = "；已覆盖旧模板提示" if conflicts else ""
    return f"根据{basis}识别到{family_labels.get(family, '音乐要素')}，自动匹配{template_id}{conflict_note}。"


def _entity_match_reason(template_id: str, matched_entity: dict[str, Any], status: str) -> str:
    label = matched_entity.get("semantic_term") or matched_entity.get("label") or "音乐要素"
    if status == "recommended":
        return f"“{label}”在本地音乐要素库中可由{template_id}承接。"
    return f"当前玩法可承接“{label}”。"


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
