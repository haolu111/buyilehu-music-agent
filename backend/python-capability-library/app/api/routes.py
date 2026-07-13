from __future__ import annotations

import sys

from fastapi import APIRouter, status

from app.api.errors import ApiException
from app.api.models import (
    ActivityAssessmentRequest,
    ActivityAssessmentResponse,
    HealthData,
    HealthResponse,
    PackageBuildData,
    PackageBuildRequest,
    PackageBuildResponse,
    PackageDesignRequest,
    PackageDesignResponse,
    PackageNodeBuildData,
    RuntimeBuildData,
    RuntimeBuildRequest,
    RuntimeBuildResponse,
    ToolkitsData,
    ToolkitsResponse,
)
from app.services.assessment.activity_assessment_service import assess_activity_submission
from app.services.runtime.runtime_api_service import build_runtime_bundle, list_available_toolkits
from app.services.orchestration.package_design_agent import design_interactive_package


router = APIRouter(prefix="/api/v1", tags=["music-capability"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        data=HealthData(
            service="python-capability-library",
            python_version=sys.version.split(" ")[0],
        )
    )


@router.get("/toolkits", response_model=ToolkitsResponse)
def get_toolkits() -> ToolkitsResponse:
    try:
        items = list_available_toolkits()
    except ValueError as exc:
        raise _translate_value_error(exc) from exc
    return ToolkitsResponse(data=ToolkitsData(count=len(items), items=items))


@router.post("/runtime/build", response_model=RuntimeBuildResponse)
def build_runtime(payload: RuntimeBuildRequest) -> RuntimeBuildResponse:
    try:
        result = build_runtime_bundle(
            activity_id=payload.activity_id,
            composition=payload.composition,
            request=payload.request,
        )
    except ValueError as exc:
        raise _translate_value_error(exc) from exc
    return RuntimeBuildResponse(data=RuntimeBuildData(**result))


@router.post("/packages/build", response_model=PackageBuildResponse)
def build_package(payload: PackageBuildRequest) -> PackageBuildResponse:
    nodes = []
    try:
        for node in payload.nodes:
            result = build_runtime_bundle(
                activity_id=node.activity_id,
                composition=node.composition,
                request=node.request,
            )
            nodes.append(PackageNodeBuildData(client_ref=node.client_ref, **result))
    except ValueError as exc:
        raise _translate_value_error(exc) from exc
    return PackageBuildResponse(data=PackageBuildData(nodes=nodes))


@router.post("/packages/design", response_model=PackageDesignResponse)
def design_package(payload: PackageDesignRequest) -> PackageDesignResponse:
    return PackageDesignResponse(data=design_interactive_package(
        lesson=payload.lesson,
        preferences=payload.preferences,
    ))


@router.post("/assessments/grade", response_model=ActivityAssessmentResponse)
def grade_activity(payload: ActivityAssessmentRequest) -> ActivityAssessmentResponse:
    result = assess_activity_submission(
        activity_id=payload.activity_id,
        renderer=payload.renderer,
        title=payload.title,
        result=payload.result,
        assessment=payload.assessment,
    )
    return ActivityAssessmentResponse(data=result)


def _translate_value_error(exc: ValueError) -> ApiException:
    message = str(exc)
    if "unknown activity template" in message:
        return ApiException(
            code="activity_not_found",
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return ApiException(
        code="invalid_request",
        message=message,
        status_code=status.HTTP_400_BAD_REQUEST,
    )
