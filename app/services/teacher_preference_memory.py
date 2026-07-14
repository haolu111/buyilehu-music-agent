from __future__ import annotations

from copy import deepcopy
from typing import Any


def update_teacher_preference_memory(memory: dict[str, Any] | None, signal: dict[str, Any]) -> dict[str, Any]:
    updated = deepcopy(memory or {})
    grade = str(signal.get("grade_band") or "").strip()
    if grade:
        grades = updated.setdefault("grade_bands", {})
        grades[grade] = int(grades.get(grade, 0)) + 1
    if signal.get("text_density"):
        updated["text_density_preference"] = signal["text_density"]
    if signal.get("uses_group_work") is not None:
        updated["uses_group_work"] = bool(signal.get("uses_group_work"))
    if signal.get("device_condition"):
        updated["device_condition"] = signal["device_condition"]
    song = str(signal.get("song_title") or "").strip()
    if song:
        songs = updated.setdefault("common_songs", [])
        if song not in songs:
            songs.append(song)
    return updated
