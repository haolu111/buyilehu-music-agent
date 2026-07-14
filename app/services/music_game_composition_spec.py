from __future__ import annotations

from copy import deepcopy
from typing import Any


MUSIC_GAME_COMPOSITION_SPEC_VERSION = "music_game_composition_spec_v1"

REQUIRED_COMPOSITION_FIELDS = (
    "version",
    "status",
    "selected_activity_id",
    "selected_components",
    "selected_teaching_aids",
    "selected_virtual_instruments",
    "selected_teacher_controls",
    "education_alignment",
    "material_binding",
    "missing_fields",
    "teacher_explanation",
    "quality_gates",
    "runtime",
    "lesson_runtime_generated_assets",
    "acceptance_report",
)


def validate_music_game_composition_spec(spec: dict[str, Any]) -> dict[str, Any]:
    missing = [field for field in REQUIRED_COMPOSITION_FIELDS if field not in spec]
    if missing:
        raise ValueError(f"music game composition spec missing fields: {', '.join(missing)}")
    if spec.get("version") != MUSIC_GAME_COMPOSITION_SPEC_VERSION:
        raise ValueError("music game composition spec version must be music_game_composition_spec_v1")
    if spec.get("status") not in {"ready", "needs_material"}:
        raise ValueError("music game composition status must be ready or needs_material")
    if not isinstance(spec.get("education_alignment"), dict):
        raise ValueError("music game composition education_alignment must be a dict")
    if not isinstance(spec.get("material_binding"), dict):
        raise ValueError("music game composition material_binding must be a dict")
    if not isinstance(spec.get("runtime"), dict):
        raise ValueError("music game composition runtime must be a dict")
    if not isinstance(spec.get("lesson_runtime_generated_assets"), dict):
        raise ValueError("music game composition lesson_runtime_generated_assets must be a dict")
    if not isinstance(spec.get("acceptance_report"), dict):
        raise ValueError("music game composition acceptance_report must be a dict")
    return deepcopy(spec)
