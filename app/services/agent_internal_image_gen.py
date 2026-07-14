from __future__ import annotations

from typing import Any

from app.services.image_generation_task_executor import AgentImageGenerator


_EXECUTOR: AgentImageGenerator | None = None


def register_agent_image_gen_executor(executor: AgentImageGenerator) -> None:
    """Attach the intelligent agent's internal image_gen executor for game assets."""

    if not callable(executor):
        raise TypeError("agent image_gen executor must be callable")
    global _EXECUTOR
    _EXECUTOR = executor


def clear_agent_image_gen_executor() -> None:
    global _EXECUTOR
    _EXECUTOR = None


def get_agent_image_gen_executor() -> AgentImageGenerator | None:
    return _EXECUTOR


def agent_image_gen_runtime_status() -> dict[str, Any]:
    return {
        "provider_boundary": "agent_internal_image_gen_only_not_image2_or_chat_ecnu",
        "executor_registered": _EXECUTOR is not None,
        "usage": "lesson_game_runtime_assets_only",
        "must_not_use": ["image2_asset_pack_queue", "chat_ecnu_atmosphere_generation"],
    }
