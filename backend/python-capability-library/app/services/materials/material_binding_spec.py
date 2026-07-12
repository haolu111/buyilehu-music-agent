from __future__ import annotations

from copy import deepcopy
from typing import Any


MATERIAL_BINDING_SPEC_VERSION = "material_binding_spec_v1"


def build_material_binding_spec(
    *,
    source_request: dict[str, Any],
    required_material_entities: list[str],
    available_materials: dict[str, Any],
) -> dict[str, Any]:
    available = available_materials if isinstance(available_materials, dict) else {}
    missing = [entity for entity in required_material_entities if not _has_material(entity, available)]
    return {
        "version": MATERIAL_BINDING_SPEC_VERSION,
        "detected_targets": list(required_material_entities),
        "game_ready_entities": {
            entity: deepcopy(available[entity])
            for entity in required_material_entities
            if entity in available and _has_material(entity, available)
        },
        "missing_fields": missing,
        "teacher_confirm_fields": _teacher_confirm_fields(required_material_entities, available),
        "source_summary": {
            "teacher_request": str(source_request.get("teacher_request") or "").strip(),
            "grade_band": str(source_request.get("grade_band") or "").strip(),
        },
    }


def _has_material(entity: str, available: dict[str, Any]) -> bool:
    if entity in available and available[entity] not in ("", None, [], {}):
        return True
    if entity == "meter":
        return bool(available.get("meter") or available.get("lyrics_rhythm_phrases"))
    if entity == "rhythm_pattern":
        return bool(available.get("rhythm_pattern") or available.get("pattern_steps") or available.get("rhythm_cards") or available.get("lyrics_rhythm_phrases"))
    if entity == "audio_clip":
        return bool(available.get("audio_clip") or available.get("audio_url") or available.get("source_audio_url"))
    if entity == "lesson_topic":
        return bool(available.get("lesson_topic") or available.get("song_title") or available.get("work_title") or available.get("title"))
    if entity == "lyrics_phrase":
        return bool(available.get("lyrics_phrase") or available.get("lyrics_text") or available.get("lyrics_rhythm_phrases"))
    if entity == "melody_phrase":
        return bool(available.get("melody_phrase") or available.get("target_solfege"))
    if entity == "pitch_motion":
        return bool(
            available.get("pitch_motion")
            or available.get("melody_contour")
            or available.get("contour_steps")
            or available.get("direction_steps")
        )
    if entity == "expression_trait":
        return bool(
            available.get("expression_trait")
            or available.get("expression_traits")
            or available.get("mood_options")
            or available.get("listening_traits")
            or available.get("accepted_moods")
        )
    if entity == "timbre_set":
        return bool(
            available.get("timbre_set")
            or available.get("timbre_traits")
            or available.get("evidence_terms")
            or available.get("music_evidence_terms")
        )
    if entity == "solfege_set":
        return bool(
            available.get("solfege_set")
            or available.get("melody_cards")
            or available.get("pitch_range")
            or available.get("scale_degrees")
        )
    if entity == "instrument_pool":
        return bool(
            available.get("instrument_pool")
            or available.get("instruments")
            or available.get("instrument_cards")
        )
    if entity == "instrument_family_set":
        return bool(
            available.get("instrument_family_set")
            or available.get("instrument_families")
            or available.get("family_targets")
            or available.get("families")
        )
    if entity == "form_structure":
        return bool(
            available.get("form_structure")
            or available.get("form_type")
            or available.get("structure")
            or available.get("answer_pattern")
            or available.get("section_labels")
        )
    if entity == "graphic_symbol_meanings":
        return bool(
            available.get("graphic_symbol_meanings")
            or available.get("symbol_meanings")
            or available.get("graphic_symbols")
            or available.get("shape_meanings")
        )
    if entity == "theme_windows":
        return bool(
            available.get("theme_windows")
            or available.get("theme_return_windows")
            or available.get("theme_time_windows")
            or available.get("return_windows")
        )
    if entity == "classroom_group_task":
        return bool(
            available.get("classroom_group_task")
            or available.get("group_tasks")
            or available.get("part_assignments")
            or available.get("ensemble_parts")
            or available.get("group_count")
        )
    if entity == "assessment_criteria":
        return bool(available.get("assessment_criteria") or available.get("rubric"))
    if entity == "music_focus":
        return bool(available.get("music_focus") or available.get("focus") or available.get("objective"))
    return False


def _teacher_confirm_fields(required_material_entities: list[str], available: dict[str, Any]) -> list[str]:
    fields: list[str] = []
    if "audio_clip" in required_material_entities and _has_material("audio_clip", available):
        fields.append("audio_clip_boundary")
    if "melody_phrase" in required_material_entities:
        fields.append("singback_teacher_confirmation")
    if "bpm" in available or "meter" in required_material_entities:
        fields.append("tempo_or_meter")
    phrase_items = available.get("lyrics_rhythm_phrases")
    if isinstance(phrase_items, list) and any(
        isinstance(item, dict)
        and (item.get("source") == "recognized_draft" or not item.get("teacherConfirmed"))
        for item in phrase_items
    ):
        fields.append("lyrics_rhythm_score_confirmation")
    return fields
