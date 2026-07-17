#校验虚拟乐器规格是否完整合法
from __future__ import annotations

from copy import deepcopy
from typing import Any


REQUIRED_VIRTUAL_INSTRUMENT_FIELDS = (
    "version",
    "instrument_id",
    "name",
    "audience",
    "replace_physical_instrument",
    "runtime",
    "input_modes",
    "sound_source",
    "constraints",
    "teacher_controls",
    "quality_gates",
    "runtime_contract",
)


def validate_virtual_instrument_spec(spec: dict[str, Any]) -> dict[str, Any]:
    missing = [field for field in REQUIRED_VIRTUAL_INSTRUMENT_FIELDS if not spec.get(field)]
    if missing:
        raise ValueError(f"virtual instrument spec missing fields: {', '.join(missing)}")
    if spec.get("version") != "virtual_instrument_spec_v1":
        raise ValueError("virtual instrument spec version must be virtual_instrument_spec_v1")
    if spec.get("audience") != "primary_school":
        raise ValueError("virtual instrument audience must be primary_school")
    if "events_recorded" not in spec.get("quality_gates", []):
        raise ValueError("virtual instrument quality_gates must include events_recorded")
    runtime = spec.get("runtime_contract")
    if not isinstance(runtime, dict) or runtime.get("version") != "virtual_instrument_runtime_contract_v1":
        raise ValueError("virtual instrument runtime_contract must be virtual_instrument_runtime_contract_v1")
    for key in ("runtime_components", "supported_activity_ids", "student_event_schema", "quality_gates", "classroom_evidence"):
        if not runtime.get(key):
            raise ValueError(f"virtual instrument runtime_contract.{key} must be provided")
    if "instrument_id" not in runtime.get("student_event_schema", []):
        raise ValueError("virtual instrument runtime_contract.student_event_schema must include instrument_id")
    if "timestamp_ms" not in runtime.get("student_event_schema", []):
        raise ValueError("virtual instrument runtime_contract.student_event_schema must include timestamp_ms")
    return deepcopy(spec)
