from __future__ import annotations

from copy import deepcopy
from typing import Any


MUSIC_MEDIA_SESSION_VERSION = "music_media_session_v1"
NORMALIZED_SCORE_TIMELINE_VERSION = "normalized_score_timeline_v1"
MUSIC_CLASSROOM_COMPONENT_IDS = (
    "song_audio_workbench",
    "score_audio_sync_player",
    "ear_training_engine",
    "vocal_choir_training",
    "ensemble_conductor",
)

AUTHORITATIVE_SCORE_SOURCES = {"musicxml", "midi", "teacher_manual"}


def build_default_music_media_session(
    *,
    session_id: str,
    source_url: str = "",
    source_kind: str = "teacher_upload",
    grade_preset: str = "middle_primary",
) -> dict[str, Any]:
    source_assets: list[dict[str, Any]] = []
    if source_url:
        source_assets.append(
            {
                "id": "primary_source",
                "kind": source_kind,
                "url": source_url,
                "label": "教师课堂音频" if source_kind == "teacher_upload" else "平台授权资源",
                "rights_status": (
                    "teacher_confirmation_required"
                    if source_kind == "teacher_upload"
                    else "platform_authorized"
                ),
            }
        )
    return {
        "version": MUSIC_MEDIA_SESSION_VERSION,
        "session_id": str(session_id),
        "grade_preset": grade_preset,
        "source_assets": source_assets,
        "score_timeline": None,
        "tracks": [],
        "transport": {
            "bpm": 88,
            "playback_rate": 1.0,
            "transpose_semitones": 0,
            "count_in_bars": 1,
            "loop": None,
        },
        "recording_policy": "local_session_only",
        "network_mode": "single_device_classroom",
        "teacher_confirmation": {
            "material_confirmed": False,
            "music_quality_confirmed": False,
        },
    }


def validate_normalized_score_timeline(
    value: dict[str, Any] | None,
    *,
    for_student_judgement: bool = False,
) -> dict[str, Any]:
    timeline = deepcopy(value) if isinstance(value, dict) else {}
    errors: list[str] = []
    if timeline.get("version") != NORMALIZED_SCORE_TIMELINE_VERSION:
        errors.append("invalid_version")
    source = str(timeline.get("source") or "")
    if source not in {*AUTHORITATIVE_SCORE_SOURCES, "recognized_draft"}:
        errors.append("invalid_source")
    for field in ("meter_map", "tempo_map", "key_map", "events"):
        if not isinstance(timeline.get(field), list):
            errors.append(f"invalid_{field}")
    if errors:
        return {"valid": False, "status": "invalid", "errors": errors}
    if for_student_judgement and (
        source not in AUTHORITATIVE_SCORE_SOURCES or not bool(timeline.get("teacher_confirmed"))
    ):
        return {
            "valid": False,
            "status": "teacher_confirmation_required",
            "errors": ["score_not_teacher_confirmed"],
        }
    return {"valid": True, "status": "ready", "errors": []}

