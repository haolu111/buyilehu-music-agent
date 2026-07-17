from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.services.activities.activity_registry import ACTIVITY_TEMPLATE_REGISTRY
from app.services.activities.activity_family_registry import get_activity_family


SUPPORTED_RENDERERS = frozenset({
    "meter-compare",
    "rhythm-drag",
    "creation-panel",
    "summary",
    "singing-practice",
    "listening-choice",
    "solfege-sort",
    "melody-trace",
    "timbre-match",
    "form-order",
    "virtual-instrument",
    "ensemble-roles",
})

_RENDERER_ACTIVITIES: dict[str, tuple[str, ...]] = {
    "meter-compare": (
        "meter_body_movement", "strong_weak_beat_circle", "steady_beat_walk",
    ),
    "rhythm-drag": (
        "rhythm_warmup", "rhythm_question_answer", "lyrics_rhythm_practice",
    ),
    "creation-panel": (
        "body_percussion_builder", "graphic_score_create",
    ),
    "summary": ("exit_ticket_review",),
    "singing-practice": (
        "phrase_singing_practice", "phrase_loop_singing", "lyrics_rhythm_reading",
        "vocal_choir_training_activity",
    ),
    "listening-choice": (
        "picture_listening_intro", "listen_choose_explain", "lesson_opening_hook",
        "theme_return_action", "song_audio_workbench_activity",
    ),
    "solfege-sort": (
        "solfege_sorting", "solfege_echo_singing", "ear_training_practice",
    ),
    "melody-trace": (
        "melody_contour_trace", "simple_score_following", "score_audio_sync_practice",
    ),
    "timbre-match": (
        "instrument_timbre_match", "instrument_family_sorting",
    ),
    "form-order": ("form_ordering",),
    "virtual-instrument": ("xylophone_creation",),
    "ensemble-roles": (
        "orff_percussion_ensemble", "classroom_band_roles", "group_relay_performance",
        "show_and_peer_feedback", "ensemble_conductor_rehearsal",
    ),
}

_NODE_TYPES = {
    "meter-compare": "meter_experience",
    "rhythm-drag": "rhythm_game",
    "creation-panel": "creation_workshop",
    "summary": "summary",
    "singing-practice": "singing_practice",
    "listening-choice": "listening_activity",
    "solfege-sort": "solfege_activity",
    "melody-trace": "melody_activity",
    "timbre-match": "timbre_activity",
    "form-order": "form_activity",
    "virtual-instrument": "instrument_activity",
    "ensemble-roles": "ensemble_activity",
}


ACTIVITY_INTERACTION_REGISTRY: dict[str, dict[str, Any]] = {}
for _renderer, _activity_ids in _RENDERER_ACTIVITIES.items():
    for _activity_id in _activity_ids:
        _activity = ACTIVITY_TEMPLATE_REGISTRY.get(_activity_id)
        if _activity is None:
            raise RuntimeError(f"interaction registry references unknown activity: {_activity_id}")
        ACTIVITY_INTERACTION_REGISTRY[_activity_id] = {
            "activity_id": _activity_id,
            "name": str(_activity.get("name") or _activity_id),
            "renderer": _renderer,
            "node_type": _NODE_TYPES[_renderer],
            "component_keys": [_renderer.replace("-", "_")],
            **get_activity_family(_activity_id),
        }

_uncategorized = set(ACTIVITY_TEMPLATE_REGISTRY) - set(ACTIVITY_INTERACTION_REGISTRY)
if _uncategorized:
    raise RuntimeError(f"activities missing a supported interaction: {', '.join(sorted(_uncategorized))}")


def list_agent_activity_specs() -> list[dict[str, Any]]:
    return [deepcopy(spec) for spec in ACTIVITY_INTERACTION_REGISTRY.values()
            if spec["renderer"] in SUPPORTED_RENDERERS]


def get_activity_interaction(activity_id: str) -> dict[str, Any]:
    spec = ACTIVITY_INTERACTION_REGISTRY.get(str(activity_id or ""))
    if spec is None or spec["renderer"] not in SUPPORTED_RENDERERS:
        raise ValueError(f"activity has no supported student renderer: {activity_id}")
    return deepcopy(spec)
