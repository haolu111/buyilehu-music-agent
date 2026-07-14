from __future__ import annotations

from copy import deepcopy
from typing import Any


def build_audio_manifest(
    instance: dict[str, Any],
    *,
    music_truth: dict[str, Any] | None = None,
) -> dict[str, Any]:
    config = instance.get("config") if isinstance(instance.get("config"), dict) else {}
    template_id = str(instance.get("template_id") or config.get("template_id") or "").strip()
    if template_id == "rhythm_echo_core":
        return _rhythm_audio_manifest(config, music_truth=music_truth or {})
    return {
        "version": "audio_manifest_v1",
        "template_id": template_id,
        "playback_policy": {
            "preferred": "sampled_or_soundfont",
            "fallback": "webaudio_synthetic",
            "offline_ready": False,
        },
        "sounds": [
            {
                "id": "template_primary_tone",
                "role": "template_playback",
                "source_type": "soundfont_or_webaudio",
                "license": "runtime_asset_or_teacher_provided",
                "fallback": {"type": "webaudio", "wave": "triangle", "frequency": 440},
            },
            {
                "id": "template_feedback_tone",
                "role": "success_and_error_feedback",
                "source_type": "webaudio",
                "fallback": {"type": "webaudio", "wave": "sine", "frequency": 660},
            },
        ],
    }


def _rhythm_audio_manifest(config: dict[str, Any], *, music_truth: dict[str, Any]) -> dict[str, Any]:
    lesson_audio_sync = (
        config.get("lesson_audio_sync") if isinstance(config.get("lesson_audio_sync"), dict) else {}
    )
    sounds = [
        {
            "id": "tap_tick",
            "role": "rhythm_playback",
            "instrument": "woodblock",
            "source_type": "soundfont_or_sample",
            "license": "runtime_asset_or_teacher_provided",
            "fallback": {"type": "webaudio", "wave": "triangle", "frequency": 880},
        },
        {
            "id": "mistake_soft",
            "role": "error_feedback",
            "source_type": "webaudio",
            "fallback": {"type": "webaudio", "wave": "sine", "frequency": 220},
        },
        {
            "id": "success_chime",
            "role": "success_feedback",
            "source_type": "soundfont_or_sample",
            "fallback": {"type": "webaudio", "wave": "triangle", "frequency": 660},
        },
    ]
    if lesson_audio_sync.get("audio_url"):
        sounds.append(
            {
                "id": "lesson_source_clip",
                "role": "source_material",
                "source_type": "teacher_audio",
                "url": lesson_audio_sync["audio_url"],
                "fallback": {"type": "internal_pattern", "pattern_steps": _truth_pattern_steps(music_truth)},
            }
        )
    return {
        "version": "audio_manifest_v1",
        "template_id": "rhythm_echo_core",
        "playback_policy": {
            "preferred": "sampled_or_soundfont",
            "fallback": "webaudio_synthetic",
            "preload": True,
            "offline_ready": not bool(lesson_audio_sync.get("audio_url")),
        },
        "sync_policy": {
            "bpm": config.get("bpm", 92),
            "visual_audio_max_drift_ms": 80,
            "count_in_beats": config.get("count_in_beats", 4),
        },
        "sounds": sounds,
    }


def _truth_pattern_steps(music_truth: dict[str, Any]) -> list[str]:
    answers = music_truth.get("answers") if isinstance(music_truth.get("answers"), list) else []
    first = answers[0] if answers and isinstance(answers[0], dict) else {}
    steps = first.get("pattern_steps") if isinstance(first.get("pattern_steps"), list) else []
    return deepcopy(steps)
