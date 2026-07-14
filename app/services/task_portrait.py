from __future__ import annotations

from copy import deepcopy
from typing import Any


_BEHAVIOR_MAP = {
    "听": "listen",
    "唱": "sing",
    "读": "read",
    "拍": "tap",
    "动": "move",
    "奏": "play",
    "创": "create",
    "评": "assess",
}


def normalize_student_behaviors(values: Any) -> list[str]:
    raw_values = values if isinstance(values, list) else [values] if values else []
    normalized: list[str] = []
    for value in raw_values:
        text = str(value or "").strip()
        behavior = _BEHAVIOR_MAP.get(text, text)
        if behavior and behavior not in normalized:
            normalized.append(behavior)
    return normalized


def build_task_portrait_from_lesson(lesson_payload: dict[str, Any]) -> dict[str, Any]:
    context = lesson_payload.get("lesson_context", {}) if isinstance(lesson_payload.get("lesson_context"), dict) else {}
    lesson_fit = lesson_payload.get("lesson_fit", {}) if isinstance(lesson_payload.get("lesson_fit"), dict) else {}
    evidence = lesson_fit.get("lesson_evidence", {}) if isinstance(lesson_fit.get("lesson_evidence"), dict) else {}
    material = lesson_fit.get("material_binding", {}) if isinstance(lesson_fit.get("material_binding"), dict) else {}
    stage = evidence.get("target_stage") or context.get("target_stage") or context.get("classroom_stage") or ""
    music_element = evidence.get("music_element") or context.get("target_music_element") or ""
    behaviors = normalize_student_behaviors(evidence.get("student_behavior"))
    recommended_outputs = _recommended_outputs(music_element, behaviors)
    return {
        "version": "task_portrait_v1",
        "main_goal": context.get("teaching_objective") or evidence.get("target_objective") or "",
        "lesson_stage": stage,
        "student_music_behaviors": behaviors,
        "music_elements": [music_element] if music_element else [],
        "material_refs": [material.get("selected_phrase_label")] if material.get("selected_phrase_label") else [],
        "learning_difficulty": context.get("learning_difficulty") or music_element,
        "digital_entry_points": ["把教案中的学生音乐行为转成可操作活动"],
        "recommended_outputs": recommended_outputs,
        "not_suitable_outputs": ["自由新增游戏闯关"],
        "source_evidence": deepcopy(evidence),
    }


def _recommended_outputs(music_element: str, behaviors: list[str]) -> list[str]:
    outputs = ["teacher_plan_card"]
    if any(item in behaviors for item in ("read", "tap", "sing")) or any(word in music_element for word in ("节奏", "歌词", "节拍")):
        outputs.insert(0, "virtual_teaching_aid")
    if any(item in behaviors for item in ("play", "create")):
        outputs.insert(0, "virtual_instrument")
    return outputs
