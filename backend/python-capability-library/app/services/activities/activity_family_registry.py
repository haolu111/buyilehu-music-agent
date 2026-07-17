from __future__ import annotations

from copy import deepcopy
from typing import Any


ACTIVITY_FAMILIES: dict[str, dict[str, Any]] = {
    "beat_rhythm": {
        "name": "节拍与节奏",
        "variants": {
            "rhythm_warmup": "warmup",
            "meter_body_movement": "meter_movement",
            "strong_weak_beat_circle": "strong_weak_circle",
            "steady_beat_walk": "steady_beat_walk",
            "rhythm_question_answer": "question_answer",
        },
    },
    "lyrics_rhythm": {
        "name": "歌词节奏",
        "variants": {
            "lyrics_rhythm_practice": "tap_then_sing",
            "lyrics_rhythm_reading": "spoken_reading",
        },
    },
    "phrase_singing": {
        "name": "乐句学唱",
        "variants": {
            "phrase_singing_practice": "whole_phrase",
            "phrase_loop_singing": "phrase_loop",
            "vocal_choir_training_activity": "vocal_choir",
        },
    },
    "pitch_score": {
        "name": "音高与谱面",
        "variants": {
            "solfege_sorting": "solfege_sort",
            "solfege_echo_singing": "echo_singing",
            "melody_contour_trace": "contour_trace",
            "simple_score_following": "score_follow",
            "score_audio_sync_practice": "score_audio_sync",
            "ear_training_practice": "ear_training",
        },
    },
    "guided_listening": {
        "name": "引导聆听",
        "variants": {
            "picture_listening_intro": "picture_intro",
            "listen_choose_explain": "choose_and_explain",
            "lesson_opening_hook": "opening_hook",
            "theme_return_action": "theme_return",
            "instrument_timbre_match": "timbre_match",
            "instrument_family_sorting": "family_sort",
            "song_audio_workbench_activity": "audio_workbench",
        },
    },
    "music_structure": {
        "name": "音乐结构",
        "variants": {
            "form_ordering": "form_order",
            "graphic_score_create": "graphic_score",
        },
    },
    "music_creation": {
        "name": "音乐创编",
        "variants": {
            "body_percussion_builder": "body_percussion",
            "xylophone_creation": "xylophone",
        },
    },
    "ensemble": {
        "name": "合奏与排练",
        "variants": {
            "orff_percussion_ensemble": "orff_percussion",
            "classroom_band_roles": "band_roles",
            "ensemble_conductor_rehearsal": "conductor_rehearsal",
        },
    },
    "performance_reflection": {
        "name": "展示与反思",
        "variants": {
            "group_relay_performance": "relay_performance",
            "show_and_peer_feedback": "peer_feedback",
            "exit_ticket_review": "exit_ticket",
        },
    },
}

_ACTIVITY_INDEX = {
    activity_id: {
        "family": family_id,
        "familyName": family["name"],
        "variant": variant,
    }
    for family_id, family in ACTIVITY_FAMILIES.items()
    for activity_id, variant in family["variants"].items()
}


def get_activity_family(activity_id: str) -> dict[str, str]:
    value = _ACTIVITY_INDEX.get(str(activity_id or ""))
    if value is None:
        raise ValueError(f"activity has no family mapping: {activity_id}")
    return deepcopy(value)


def list_activity_families() -> list[dict[str, Any]]:
    return [
        {
            "family": family_id,
            "name": family["name"],
            "activities": [
                {"activityId": activity_id, "variant": variant}
                for activity_id, variant in family["variants"].items()
            ],
        }
        for family_id, family in ACTIVITY_FAMILIES.items()
    ]
