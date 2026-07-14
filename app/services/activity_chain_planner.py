from __future__ import annotations

from copy import deepcopy
from typing import Any


def plan_activity_chain(activity_spec: dict[str, Any], *, portrait: dict[str, Any] | None = None) -> dict[str, Any]:
    source_mode = str(activity_spec.get("source_mode") or "")
    if source_mode == "lesson_based":
        evidence = activity_spec.get("lesson_evidence") if isinstance(activity_spec.get("lesson_evidence"), dict) else {}
        if not evidence:
            raise ValueError("lesson_based activity chain requires lesson evidence")
        evidence_summary = (
            evidence.get("source_quote_or_summary")
            or evidence.get("stage")
            or evidence.get("material_ref")
            or activity_spec.get("activity_goal")
            or "lesson_evidence"
        )
        node = {
            "source_mode": "lesson_based",
            "activity": activity_spec.get("activity_goal") or "教案绑定课堂活动",
            "lesson_stage": evidence.get("stage") or activity_spec.get("classroom_stage"),
            "source_evidence": evidence_summary,
            "classroom_time": activity_spec.get("classroom_time") or "5分钟",
            "student_music_behaviors": deepcopy(activity_spec.get("student_music_behaviors", [])),
            "music_material": evidence.get("material_ref") or "",
            "recommended_outputs": [
                item
                for item in (portrait or {}).get("recommended_outputs", [activity_spec.get("activity_shape")])
                if item != "自由新增游戏闯关"
            ],
            "fallback_outputs": ["虚拟教具", "教师方案卡", "确认卡"],
        }
        return {"version": "activity_chain_v1", "source_mode": "lesson_based", "nodes": [node]}

    return {
        "version": "activity_chain_v1",
        "source_mode": "direct",
        "nodes": [
            {
                "source_mode": "direct",
                "activity": activity_spec.get("activity_goal") or "直接生成课堂活动",
                "lesson_stage": activity_spec.get("classroom_stage") or "",
                "source_evidence": activity_spec.get("teacher_request") or "",
                "classroom_time": activity_spec.get("classroom_time") or "5分钟",
                "student_music_behaviors": deepcopy(activity_spec.get("student_music_behaviors", [])),
                "music_material": deepcopy(activity_spec.get("material_refs", [])),
                "recommended_outputs": [activity_spec.get("activity_shape") or "confirmation_card"],
                "fallback_outputs": ["互动练习", "虚拟教具", "教师方案卡", "课堂问题卡", "确认卡"],
            }
        ],
    }
