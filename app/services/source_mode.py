from __future__ import annotations

from typing import Any


def determine_source_mode(payload: dict[str, Any] | None) -> dict[str, Any]:
    request = payload or {}
    has_lesson = bool(request.get("lesson_source") or request.get("lesson_analysis") or request.get("uploaded_lesson"))
    if has_lesson:
        return {
            "version": "source_mode_v1",
            "source_mode": "lesson_based",
            "grounding_source": "uploaded_lesson",
            "can_claim": ["贴合上传教案中的目标、环节和材料"],
            "cannot_claim": ["不能自由扩写未出现在教案里的课堂流程"],
        }
    return {
        "version": "source_mode_v1",
        "source_mode": "direct",
        "grounding_source": "teacher_request",
        "can_claim": ["符合教师直接需求和系统音乐教育规则"],
        "cannot_claim": ["不能声称贴合某份具体教案或教材流程"],
    }
