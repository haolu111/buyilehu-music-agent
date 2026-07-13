from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class HealthData(BaseModel):
    status: Literal["ok"] = "ok"
    service: str
    python_version: str


class HealthResponse(BaseModel):
    success: Literal[True] = True
    data: HealthData


class ToolkitsData(BaseModel):
    count: int
    items: list[dict[str, Any]]


class ToolkitsResponse(BaseModel):
    success: Literal[True] = True
    data: ToolkitsData


class RuntimeBuildRequest(BaseModel):
    activity_id: str | None = Field(
        default=None,
        description="Activity template id. If omitted, the service uses composition.selected_activity_id.",
    )
    composition: dict[str, Any] | None = Field(
        default=None,
        description="Existing composition payload passed through to build_primary_music_game_runtime(...).",
    )
    request: dict[str, Any] = Field(
        default_factory=dict,
        description="Existing runtime request content passed through to build_primary_music_game_runtime(...).",
    )


class RuntimeBuildData(BaseModel):
    activity_id: str
    toolkit: dict[str, Any]
    composition: dict[str, Any]
    runtime: dict[str, Any]
    media_session_preview: dict[str, Any] | None = None


class RuntimeBuildResponse(BaseModel):
    success: Literal[True] = True
    data: RuntimeBuildData
