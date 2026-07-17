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
    activity_runtime: dict[str, Any]


class RuntimeBuildResponse(BaseModel):
    success: Literal[True] = True
    data: RuntimeBuildData


class PackageNodeBuildRequest(BaseModel):
    client_ref: str
    activity_id: str
    composition: dict[str, Any] | None = None
    request: dict[str, Any] = Field(default_factory=dict)


class PackageBuildRequest(BaseModel):
    nodes: list[PackageNodeBuildRequest] = Field(min_length=1)


class PackageNodeBuildData(RuntimeBuildData):
    client_ref: str


class PackageBuildData(BaseModel):
    schema_version: Literal["activity-package.v1"] = "activity-package.v1"
    nodes: list[PackageNodeBuildData]


class PackageBuildResponse(BaseModel):
    success: Literal[True] = True
    data: PackageBuildData


class PackageDesignRequest(BaseModel):
    lesson: dict[str, Any]
    preferences: dict[str, Any] = Field(default_factory=dict)


class PackageDesignResponse(BaseModel):
    success: Literal[True] = True
    data: dict[str, Any]


class PackageDesignWorkflowRequest(PackageDesignRequest):
    quality_review_mode: Literal["rules", "hybrid"] = "hybrid"


class PackageDesignReviewRequest(BaseModel):
    decision: Literal["approve", "edit", "reject"]
    feedback: str = Field(default="", max_length=2000)
    node_feedback: list[dict[str, Any]] = Field(default_factory=list, max_length=7)


class PackageDesignWorkflowResponse(BaseModel):
    success: Literal[True] = True
    data: dict[str, Any]


class PackageNodeRevisionRequest(BaseModel):
    lesson: dict[str, Any] = Field(default_factory=dict)
    node: dict[str, Any]
    feedback: str = Field(min_length=1, max_length=2000)


class ActivityAssessmentRequest(BaseModel):
    activity_id: str = ""
    renderer: str
    title: str = ""
    result: dict[str, Any] = Field(default_factory=dict)
    assessment: dict[str, Any] = Field(default_factory=dict)


class ActivityAssessmentResponse(BaseModel):
    success: Literal[True] = True
    data: dict[str, Any]
