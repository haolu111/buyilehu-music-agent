from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.services.games.game_template_registry import build_game_instance


GAME_RENDERERS = {
    "beat_guardian_core": "rhythm-drag",
    "rhythm_echo_core": "rhythm-drag",
    "timbre_detective_core": "timbre-match",
    "form_treasure_core": "form-order",
    "composition_puzzle_core": "creation-panel",
    "pitch_ladder_core": "melody-trace",
    "solfege_target_core": "solfege-sort",
}


def build_game_node(spec: dict[str, Any]) -> dict[str, Any]:
    template_id = str(spec.get("templateId") or spec.get("template_id") or "")
    renderer = GAME_RENDERERS.get(template_id)
    if renderer is None:
        raise ValueError(f"unsupported interactive game template: {template_id}")
    payload = deepcopy(spec.get("payload") or {})
    payload.setdefault("template_id", template_id)
    instance = build_game_instance(payload)
    props = deepcopy(spec.get("props") or {})
    props.setdefault("prompt", str(spec.get("prompt") or "完成音乐游戏挑战。"))
    if renderer == "rhythm-drag":
        props.setdefault("maxBeats", 4)
        props.setdefault("cards", [
            {"name": "ta", "pattern": "X"},
            {"name": "ti-ti", "pattern": "X X"},
            {"name": "rest", "pattern": "-"},
        ])
        props.setdefault("targetSequence", ["ta", "ti-ti", "ta", "rest"])
    return {
        "game": instance,
        "runtime": {
            "schemaVersion": "interactive-node-runtime.v2",
            "nodeType": "game",
            "family": "music_game",
            "variant": template_id,
            "renderer": renderer,
            "legacyRenderer": renderer,
            "props": props,
            "assets": [],
            "assessment": {
                "mode": "rule",
                "resultType": renderer,
                "maxScore": 100,
                "answerKey": {"sequence": props.get("targetSequence", [])}
                if renderer == "rhythm-drag" else {},
            },
            "mediaSession": None,
        },
    }
