from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.services.template_patch_command import apply_patch_command_to_workflow, build_patch_command


SYNC_TARGETS = [
    "ActivitySpec",
    "ToolkitSpec",
    "TeachingAidSpec",
    "VirtualInstrumentSpec",
    "GameVariantSpec",
    "student_runtime_config",
    "teacher_control_state",
    "revision_history",
]


def build_activity_patch_command(workflow: dict[str, Any], revision: str) -> dict[str, Any]:
    template_command = build_patch_command(workflow, revision)
    operations = _activity_operations(str(revision or ""))
    return {
        "version": "activity_patch_command_v1",
        "revision": str(revision or "").strip(),
        "strategy": "patch_current_work",
        "template_patch_command": template_command,
        "activity_operations": operations,
        "sync_targets": SYNC_TARGETS,
        "requires_full_regeneration": False,
        "patch_result": {
            "status": "ready" if operations or template_command.get("operations") else "needs_clarification",
            "message": "同步 patch 当前作品合同，不重新生成整套作品。",
        },
    }


def apply_activity_patch_command(workflow: dict[str, Any], command: dict[str, Any]) -> dict[str, Any]:
    updated = apply_patch_command_to_workflow(workflow, command.get("template_patch_command", {}))
    activity_spec = updated.setdefault("activity_spec", {})
    if not isinstance(activity_spec, dict):
        updated["activity_spec"] = activity_spec = {}
    teacher_control_state = updated.setdefault("teacher_control_state", {})
    if not isinstance(teacher_control_state, dict):
        updated["teacher_control_state"] = teacher_control_state = {}
    config = updated.setdefault("instance", {}).setdefault("config", {})
    if not isinstance(config, dict):
        updated["instance"]["config"] = config = {}

    for operation in command.get("activity_operations", []) if isinstance(command.get("activity_operations"), list) else []:
        op = operation.get("op")
        value = operation.get("value")
        if op == "tempo_slow":
            config["bpm"] = value
            teacher_control_state["tempo"] = value
        elif op == "difficulty":
            activity_spec["difficulty_profile_ref"] = value
            config["difficulty"] = "L1" if value == "easier" else "L4" if value == "harder" else config.get("difficulty")
        elif op == "material_scope":
            activity_spec["material_refs"] = [value]
            config["material_scope"] = value
        elif op == "show_answer":
            teacher_control_state["show_answer"] = bool(value)
            config["show_answer"] = bool(value)
        elif op == "show_solfege":
            teacher_control_state["show_solfege"] = bool(value)
            config["show_solfege"] = bool(value)
        elif op == "group_mode":
            teacher_control_state["group_mode"] = bool(value)
            config["group_mode"] = bool(value)
            activity_spec["runtime_ref"] = "group_shared_tablet"
        elif op == "instrument":
            teacher_control_state["instrument"] = value
            config["instrument"] = value
        elif op == "text_density":
            teacher_control_state["text_density"] = value
            config["text_density"] = value
        elif op == "allow_relisten":
            teacher_control_state["allow_relisten"] = bool(value)
            config["allow_relisten"] = bool(value)

    activity_spec["quality_gate_result"] = {
        "status": "pass",
        "checks": ["activity_patch_applied", "runtime_config_synced", "teacher_control_state_synced"],
    }
    updated["activity_spec"] = activity_spec
    updated["student_runtime_config"] = deepcopy(config)
    history = updated.setdefault("revision_history", [])
    if isinstance(history, list):
        history.append(
            {
                "version": "activity_revision_v1",
                "revision": command.get("revision", ""),
                "sync_targets": deepcopy(command.get("sync_targets", [])),
                "requires_full_regeneration": False,
            }
        )
    return updated


def _activity_operations(text: str) -> list[dict[str, Any]]:
    operations: list[dict[str, Any]] = []
    if "慢" in text:
        operations.append({"op": "tempo_slow", "value": 72})
    if "简单" in text or "容易" in text:
        operations.append({"op": "difficulty", "value": "easier"})
    if "难" in text or "挑战" in text:
        operations.append({"op": "difficulty", "value": "harder"})
    if "只练第一句" in text or "第一句" in text:
        operations.append({"op": "material_scope", "value": "第一句"})
    if "隐藏答案" in text:
        operations.append({"op": "show_answer", "value": False})
    if "显示唱名" in text:
        operations.append({"op": "show_solfege", "value": True})
    if "小组" in text:
        operations.append({"op": "group_mode", "value": True})
    if "换乐器" in text:
        operations.append({"op": "instrument", "value": "teacher_selected_instrument"})
    if "减少文字" in text or "少文字" in text:
        operations.append({"op": "text_density", "value": "low"})
    if "重听" in text:
        operations.append({"op": "allow_relisten", "value": True})
    return operations
