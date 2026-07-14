from __future__ import annotations

from copy import deepcopy
import re
from typing import Any

from app.services.game_template_registry import get_game_template


TEMPLATE_DECISION_VERSION = "template_decision_v1"
PRODUCTION_TEMPLATE_IDS = {
    "beat_guardian_core",
    "pitch_ladder_core",
    "rhythm_echo_core",
    "solfege_target_core",
    "timbre_detective_core",
    "form_treasure_core",
    "composition_puzzle_core",
}

STRONG_FOCUS_TEMPLATE_KEYWORDS: tuple[tuple[str, tuple[str, ...], str], ...] = (
    ("composition_puzzle_core", ("拼图创编", "拼图创作", "节奏拼图", "节奏创编", "时值拼图", "旋律拼图", "旋律创作", "音级创编", "旋律节奏拼图", "音符拼图", "旋律和节奏"), "二次匹配到音乐素材拼图创编任务。"),
    ("timbre_detective_core", ("音色", "乐器", "声音证据", "声音线索", "笛子", "二胡", "小提琴", "钢琴", "木鱼"), "二次匹配到音色或乐器听辨任务。"),
    ("form_treasure_core", ("曲式", "ABA", "回旋", "重复对比", "段落结构", "主题再现", "段落"), "二次匹配到曲式结构、段落或主题再现任务。"),
    ("pitch_ladder_core", ("音高高低", "旋律走向", "旋律线", "音高", "旋律", "级进", "跳进", "高低", "上行", "下行", "sol-mi"), "二次匹配到音高关系或旋律走向任务。"),
    ("solfege_target_core", ("唱名", "听音击中", "模唱确认", "内听", "唱回", "击中唱名", "听辨唱名"), "二次匹配到唱名听辨、击中和唱回任务。"),
    ("beat_guardian_core", ("强拍", "弱拍", "节拍", "拍号", "稳拍", "进入时机", "准确进入", "二拍子", "三拍子", "四拍子"), "二次匹配到稳定拍、拍位或进入时机任务。"),
    ("rhythm_echo_core", ("节奏复刻", "跟拍", "模仿", "接龙", "听后拍回", "节奏", "时值", "附点", "切分", "休止", "拍手", "复刻"), "二次匹配到节奏听辨、复刻或跟拍任务。"),
)


def _fallback_template_from_lesson_text(lesson_adaptation: dict[str, Any], lesson_fit: dict[str, Any]) -> dict[str, str]:
    lesson_evidence = lesson_fit.get("lesson_evidence", {}) if isinstance(lesson_fit.get("lesson_evidence"), dict) else {}
    template_need = lesson_adaptation.get("template_need", {}) if isinstance(lesson_adaptation.get("template_need"), dict) else {}
    student_contract = (
        lesson_adaptation.get("student_learning_contract", {})
        if isinstance(lesson_adaptation.get("student_learning_contract"), dict)
        else {}
    )
    focus_text = " ".join(
        str(value or "")
        for value in [
            lesson_evidence.get("music_element"),
            template_need.get("music_focus"),
        ]
    )
    focused = _template_from_keyword_groups(focus_text)
    if focused.get("template_id"):
        return focused
    text = " ".join(
        str(value or "")
        for value in [
            lesson_evidence.get("target_objective"),
            lesson_evidence.get("music_element"),
            lesson_evidence.get("target_stage"),
            lesson_evidence.get("segment_task"),
            lesson_evidence.get("gameable_point"),
            template_need.get("operation_type"),
            template_need.get("mechanism_id"),
            template_need.get("music_focus"),
            student_contract.get("prompt"),
            " ".join(student_contract.get("required_student_actions", []))
            if isinstance(student_contract.get("required_student_actions"), list)
            else "",
        ]
    )
    matched = _template_from_keyword_groups(text)
    if matched.get("template_id"):
        return matched
    if _matches_solfege_text(text):
        return {"template_id": "solfege_target_core", "reason": "二次匹配到唱名听辨、击中和唱回任务。"}
    return {"template_id": "", "reason": ""}


def _template_from_keyword_groups(text: str) -> dict[str, str]:
    if not text:
        return {"template_id": "", "reason": ""}
    for template_id, keywords, reason in STRONG_FOCUS_TEMPLATE_KEYWORDS:
        if any(keyword in text for keyword in keywords):
            return {"template_id": template_id, "reason": reason}
    return {"template_id": "", "reason": ""}


def _matches_solfege_text(text: str) -> bool:
    if any(keyword in text for keyword in ("唱名", "听音击中", "模唱确认", "内听", "唱回", "击中唱名", "听辨唱名")):
        return True
    tokens = set(re.findall(r"\b(?:do|re|mi|fa|sol|la|ti)\b", text.lower()))
    return len(tokens) >= 2


def route_lesson_template(
    *,
    lesson_adaptation: dict[str, Any],
    lesson_fit: dict[str, Any],
    preferred_template_id: Any = "",
) -> dict[str, Any]:
    """Choose only the reusable gameplay carrier for an already-understood lesson."""

    template_hint = lesson_fit.get("template_hint", {}) if isinstance(lesson_fit.get("template_hint"), dict) else {}
    preferred = str(preferred_template_id or "").strip()
    hinted = str(template_hint.get("template_id") or "").strip()
    chosen = preferred if get_game_template(preferred) else hinted if get_game_template(hinted) else ""
    fallback = {"template_id": "", "reason": ""}
    if not chosen:
        fallback = _fallback_template_from_lesson_text(lesson_adaptation, lesson_fit)
        fallback_id = fallback.get("template_id", "")
        if fallback_id in PRODUCTION_TEMPLATE_IDS and get_game_template(fallback_id):
            chosen = fallback_id
    match_status = str(template_hint.get("match_status") or ("exact" if chosen else "unmatched"))
    match_basis = template_hint.get("match_basis", "")
    if chosen and fallback.get("template_id") == chosen:
        match_status = "exact"
        match_basis = "secondary_keyword_fallback"
    if not chosen:
        decision = "unmatched"
    elif match_status == "exact":
        decision = "exact_match"
    else:
        decision = "adaptable_match"
    template = get_game_template(chosen) or {}
    return {
        "version": TEMPLATE_DECISION_VERSION,
        "owner": "template_mechanism_router",
        "responsibility": "choose_reusable_gameplay_carrier_only",
        "decision": decision,
        "template_id": chosen,
        "template_label": template.get("label", ""),
        "match_status": match_status if chosen else "unmatched",
        "match_basis": match_basis,
        "reason": fallback.get("reason") or template_hint.get("reason", "") or (
            "当前没有能准确承载本课学习任务的成熟模板。"
            if not chosen
            else "已为当前学习任务选定可复用玩法底盘。"
        ),
        "config_overrides": deepcopy(template_hint.get("config_overrides", {}))
        if isinstance(template_hint.get("config_overrides"), dict)
        else {},
        "input_ref": {
            "lesson_adaptation_version": lesson_adaptation.get("version", ""),
            "operation_type": (lesson_adaptation.get("template_need", {}) or {}).get("operation_type", ""),
            "mechanism_id": (lesson_adaptation.get("template_need", {}) or {}).get("mechanism_id", ""),
        },
        "owns": ["模板选择", "模板参数覆盖建议", "模板命中状态"],
        "must_not_do": ["不改写教学目标", "不改写音乐答案", "不决定最终前端表现"],
    }
