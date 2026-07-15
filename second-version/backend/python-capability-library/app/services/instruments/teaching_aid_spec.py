#校验教学工具规格
from __future__ import annotations

from copy import deepcopy
from typing import Any


REQUIRED_TEACHING_AID_FIELDS = (
    "version",
    "aid_id",
    "name",
    "audience",
    "replace_physical_aid",
    "material_entities",
    "components",
    "student_actions",
    "teacher_controls",
    "acceptance",
    "runtime",
)


def validate_teaching_aid_spec(spec: dict[str, Any]) -> dict[str, Any]:
    missing = [field for field in REQUIRED_TEACHING_AID_FIELDS if not spec.get(field)]
    if missing:
        raise ValueError(f"teaching aid spec missing fields: {', '.join(missing)}")
    if spec.get("version") != "teaching_aid_spec_v1":
        raise ValueError("teaching aid spec version must be teaching_aid_spec_v1")
    if spec.get("audience") != "primary_school":
        raise ValueError("teaching aid audience must be primary_school")
    acceptance = spec.get("acceptance")
    if not isinstance(acceptance, dict) or not acceptance.get("must_bind_material"):
        raise ValueError("teaching aid acceptance.must_bind_material must be true")
    runtime = spec.get("runtime")
    if not isinstance(runtime, dict) or runtime.get("version") != "teaching_aid_runtime_contract_v1":
        raise ValueError("teaching aid runtime must be teaching_aid_runtime_contract_v1")
    for key in ("runtime_components", "supported_activity_ids", "student_event_schema", "quality_gates", "classroom_evidence"):
        if not runtime.get(key):
            raise ValueError(f"teaching aid runtime.{key} must be provided")
    return deepcopy(spec)
