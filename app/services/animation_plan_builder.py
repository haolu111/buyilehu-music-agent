from __future__ import annotations

from typing import Any


DEFAULT_STATES = ["idle", "listen", "ready", "action", "success", "fail", "reward", "retry"]


def build_animation_plan(instance: dict[str, Any]) -> dict[str, Any]:
    config = instance.get("config") if isinstance(instance.get("config"), dict) else {}
    template_id = str(instance.get("template_id") or config.get("template_id") or "").strip()
    return {
        "version": "animation_plan_v1",
        "template_id": template_id,
        "states": [
            {
                "state": state,
                "asset_required": state in {"idle", "action", "success", "fail"} and template_id != "rhythm_echo_core",
                "fallback": "css_or_canvas_runtime",
            }
            for state in DEFAULT_STATES
        ],
        "sync_policy": "animation_must_not_change_music_judgement",
    }
