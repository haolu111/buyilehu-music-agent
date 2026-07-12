from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.services.activities.activity_registry import get_activity_template, list_activity_templates
from app.services.runtime.music_classroom_suite import build_default_music_media_session
from app.services.runtime.primary_music_game_runtime_builder import build_primary_music_game_runtime
from app.services.orchestration.toolkit_registry import build_toolkit_spec


_MEDIA_SESSION_ACTIVITY_IDS = {
    "song_audio_workbench_activity",
    "score_audio_sync_practice",
    "ear_training_practice",
    "vocal_choir_training_activity",
    "ensemble_conductor_rehearsal",
}


def list_available_toolkits() -> list[dict[str, Any]]:
    activity_ids = [str(activity["activity_id"]) for activity in list_activity_templates()]
    return [build_toolkit_spec(activity_id) for activity_id in activity_ids]


def build_runtime_bundle(
    *,
    activity_id: str | None,
    composition: dict[str, Any] | None,
    request_payload: dict[str, Any] | None,
) -> dict[str, Any]:
    resolved_activity_id = _resolve_activity_id(activity_id=activity_id, composition=composition)
    activity = get_activity_template(resolved_activity_id)
    toolkit = build_toolkit_spec(resolved_activity_id)
    resolved_composition = _resolve_composition(
        activity=activity,
        toolkit=toolkit,
        composition=composition,
    )
    resolved_request = deepcopy(request_payload) if isinstance(request_payload, dict) else {}
    media_session_preview = _maybe_build_media_session_preview(
        activity_id=resolved_activity_id,
        composition=resolved_composition,
        request_payload=resolved_request,
    )
    runtime = build_primary_music_game_runtime(
        composition=resolved_composition,
        request=resolved_request,
    )
    return {
        "activity_id": resolved_activity_id,
        "toolkit": toolkit,
        "composition": resolved_composition,
        "runtime": runtime,
        "media_session_preview": media_session_preview,
    }


def _resolve_activity_id(*, activity_id: str | None, composition: dict[str, Any] | None) -> str:
    resolved = str(activity_id or "").strip()
    if resolved:
        return resolved
    if isinstance(composition, dict):
        resolved = str(composition.get("selected_activity_id") or "").strip()
    if not resolved:
        raise ValueError("activity_id is required when composition.selected_activity_id is missing")
    return resolved


def _resolve_composition(
    *,
    activity: dict[str, Any],
    toolkit: dict[str, Any],
    composition: dict[str, Any] | None,
) -> dict[str, Any]:
    resolved = deepcopy(composition) if isinstance(composition, dict) else {}
    resolved.setdefault("version", "service_runtime_composition_v1")
    resolved["status"] = str(resolved.get("status") or "ready")
    resolved["selected_activity_id"] = str(resolved.get("selected_activity_id") or activity["activity_id"])
    resolved.setdefault("selected_rules", [])
    resolved.setdefault("education_alignment", deepcopy(activity["education_alignment"]))

    teacher_explanation = resolved.get("teacher_explanation")
    if not isinstance(teacher_explanation, dict):
        teacher_explanation = {}
        resolved["teacher_explanation"] = teacher_explanation
    teacher_explanation.setdefault("why_this_game", _default_why_this_game(activity))

    difficulty = resolved.get("difficulty")
    if not isinstance(difficulty, dict):
        difficulty = {}
        resolved["difficulty"] = difficulty
    difficulty.setdefault("grade_band", _preferred_grade_band(activity.get("grade_bands")))

    if not resolved.get("selected_game_template"):
        game_templates = toolkit.get("selected", {}).get("game_templates", [])
        if isinstance(game_templates, list) and game_templates:
            resolved["selected_game_template"] = str(game_templates[0])

    return resolved


def _default_why_this_game(activity: dict[str, Any]) -> str:
    elements = "、".join(str(item) for item in activity.get("education_alignment", {}).get("music_elements", []) if str(item).strip())
    behaviors = "、".join(str(item) for item in activity.get("student_music_behaviors", []) if str(item).strip())
    if elements and behaviors:
        return f"围绕{elements}组织学生进行{behaviors}。"
    if elements:
        return f"围绕{elements}组织音乐学习活动。"
    if behaviors:
        return f"组织学生进行{behaviors}。"
    return f"组织学生完成{activity.get('name', '音乐活动')}。"


def _preferred_grade_band(value: Any) -> str:
    bands = value if isinstance(value, list) else []
    if "middle_primary" in bands:
        return "middle_primary"
    if "lower_primary" in bands:
        return "lower_primary"
    if "upper_primary" in bands:
        return "upper_primary"
    return "middle_primary"


def _maybe_build_media_session_preview(
    *,
    activity_id: str,
    composition: dict[str, Any],
    request_payload: dict[str, Any],
) -> dict[str, Any] | None:
    if activity_id not in _MEDIA_SESSION_ACTIVITY_IDS:
        return None
    available_materials = (
        request_payload.get("available_materials")
        if isinstance(request_payload.get("available_materials"), dict)
        else {}
    )
    source_url = str(
        available_materials.get("audio_clip")
        or available_materials.get("audio_url")
        or available_materials.get("source_audio_url")
        or ""
    )
    return build_default_music_media_session(
        session_id=str(available_materials.get("session_id") or f"{activity_id}-session"),
        source_url=source_url,
        source_kind="teacher_upload",
        grade_preset=str(composition.get("difficulty", {}).get("grade_band") or "middle_primary"),
    )
