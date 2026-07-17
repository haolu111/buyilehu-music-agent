from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.services.activities.activity_registry import ACTIVITY_TEMPLATE_REGISTRY
from app.services.activities.activity_family_registry import get_activity_family
from app.services.music_content.music_content_registry import capability_for


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

# These are the reviewed, runnable activity implementations delivered by
# frontend/review-console. New package designs may only select this catalog.
# The URL is consumed unchanged by both teacher-web and student-web.
REVIEWED_ACTIVITY_COMPONENTS: dict[str, str] = {
    "rhythm_warmup": "/template-console/rhythm-preview.html",
    "strong_weak_beat_circle": "/template-console/strong-weak-beat-preview.html",
    "steady_beat_walk": "/template-console/steady-beat-walk-preview.html",
    "rhythm_question_answer": "/template-console/rhythm-question-preview.html",
    "body_percussion_builder": "/template-console/body-percussion-preview.html",
    "phrase_singing_practice": "/template-console/phrase-singing-preview.html",
    "lyrics_rhythm_reading": "/template-console/lyrics-rhythm-preview.html",
    "solfege_echo_singing": "/template-console/solfege-echo-preview.html",
    "melody_contour_trace": "/template-console/melody-contour-preview.html",
    "simple_score_following": "/template-console/simple-score-preview.html",
    "listen_choose_explain": "/template-console/listening-choice-preview.html",
    "lesson_opening_hook": "/template-console/lesson-opening-preview.html",
    "theme_return_action": "/template-console/theme-return-action-preview.html",
    "graphic_score_create": "/template-console/graphic-score-preview.html",
    "instrument_family_sorting": "/template-console/instrument-family-preview.html",
    "xylophone_creation": "/template-console/pentatonic-melody-preview.html",
    "orff_percussion_ensemble": "/template-console/orff-ensemble-preview.html",
    "group_relay_performance": "/template-console/group-relay-preview.html",
    "show_and_peer_feedback": "/template-console/peer-feedback-preview.html",
    "exit_ticket_review": "/template-console/exit-ticket-preview.html",
}

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
            # renderer is the formal one-to-one activity component identity.
            # legacy_renderer remains only for old records and assessment data.
            "renderer": f"activity:{_activity_id}",
            "legacy_renderer": _renderer,
            "component_url": REVIEWED_ACTIVITY_COMPONENTS.get(_activity_id),
            "node_type": _NODE_TYPES[_renderer],
            "component_keys": [_renderer.replace("-", "_")],
            "music_content_capability": capability_for(_activity_id),
            **get_activity_family(_activity_id),
        }

_uncategorized = set(ACTIVITY_TEMPLATE_REGISTRY) - set(ACTIVITY_INTERACTION_REGISTRY)
if _uncategorized:
    raise RuntimeError(f"activities missing a supported interaction: {', '.join(sorted(_uncategorized))}")


def list_agent_activity_specs() -> list[dict[str, Any]]:
    return [deepcopy(spec) for spec in ACTIVITY_INTERACTION_REGISTRY.values()
            if spec.get("component_url")]


def get_activity_interaction(activity_id: str) -> dict[str, Any]:
    spec = ACTIVITY_INTERACTION_REGISTRY.get(str(activity_id or ""))
    if spec is None:
        raise ValueError(f"activity has no supported student renderer: {activity_id}")
    return deepcopy(spec)
