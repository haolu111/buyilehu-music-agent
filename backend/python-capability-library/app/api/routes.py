from __future__ import annotations

import sys

from fastapi import APIRouter, status

from app.api.errors import ApiException
from app.api.models import (
    HealthData,
    HealthResponse,
    RuntimeBuildData,
    RuntimeBuildRequest,
    RuntimeBuildResponse,
    ToolkitsData,
    ToolkitsResponse,
)
from app.services.runtime.runtime_api_service import build_runtime_bundle, list_available_toolkits


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
            request_payload=payload.request,
        )
    except ValueError as exc:
        raise _translate_value_error(exc) from exc
    return RuntimeBuildResponse(data=RuntimeBuildData(**result))


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
