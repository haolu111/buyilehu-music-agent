from __future__ import annotations

from copy import deepcopy
from typing import Any


FALLBACK_OUTPUTS = ["完整游戏", "互动练习", "虚拟教具", "教师方案卡", "课堂问题卡", "确认卡"]


def build_fallback_plan(activity_spec: dict[str, Any], *, reason: str) -> dict[str, Any]:
    return {
        "version": "fallback_plan_v1",
        "source_mode": activity_spec.get("source_mode") or "direct",
        "reason": reason,
        "teacher_message": "当前先降级为有依据、可继续推进的课堂交付，不冒充完整游戏。",
        "ladder": [
            {
                "output": output,
                "keeps_music_value": True,
                "next_step": _next_step(output),
            }
            for output in FALLBACK_OUTPUTS
        ],
        "activity_snapshot": deepcopy(activity_spec),
    }


def _next_step(output: str) -> str:
    if output == "确认卡":
        return "补齐学段、材料或学生音乐行为。"
    if output == "课堂问题卡":
        return "让教师选择活动方向。"
    return "通过质量门禁后继续升级交付形态。"
