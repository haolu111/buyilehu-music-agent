from __future__ import annotations

from copy import deepcopy
from typing import Any


def adapt_activity_delivery(activity_spec: dict[str, Any], conditions: dict[str, Any] | None = None) -> dict[str, Any]:
    data = conditions or {}
    device = str(data.get("device") or "")
    minutes = int(data.get("minutes") or 5)
    presentation = str(data.get("presentation") or "")
    return {
        "version": "classroom_delivery_v1",
        "activity_id": activity_spec.get("toolkit_ref") or "",
        "delivery_mode": "group_shared_tablet" if device == "shared_tablet" else "teacher_projection",
        "time_profile": _time_profile(minutes),
        "text_density": "low" if presentation == "low_text" else "normal",
        "student_music_behaviors": deepcopy(activity_spec.get("student_music_behaviors", [])),
    }


def _time_profile(minutes: int) -> str:
    if minutes <= 3:
        return "3_min_warmup"
    if minutes <= 5:
        return "5_min_single_focus"
    if minutes <= 10:
        return "10_min_reinforcement"
    if minutes <= 20:
        return "20_min_group_work"
    return "40_min_full_chain"
