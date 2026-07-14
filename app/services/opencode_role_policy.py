from __future__ import annotations

from typing import Any


POLICY_VERSION = "opencode_role_policy_v1"


def build_opencode_role_policy(
    *,
    workflow_kind: str,
    instance: dict[str, Any],
    frontend_handoff_contract: dict[str, Any],
    presentation_pack: dict[str, Any],
) -> dict[str, Any]:
    """Define where OpenCode may participate without entering the realtime path."""

    template_id = str(instance.get("template_id") or "").strip()
    is_matched_runtime = bool(template_id) and not bool(instance.get("opencode_required"))
    output_kind = str(frontend_handoff_contract.get("output_kind") or "")
    assembly_target = str(frontend_handoff_contract.get("assembly_target") or "")
    uses_react_runtime = output_kind == "react_presentation_pack" and assembly_target == "react_student_runtime"
    regular_route = (
        "react_runtime_without_opencode"
        if is_matched_runtime and uses_react_runtime
        else "scaffold_or_lesson_specific_generation"
    )
    return {
        "version": POLICY_VERSION,
        "owner": "orchestration_boundary_guard",
        "workflow_kind": workflow_kind,
        "regular_generation_route": regular_route,
        "realtime_opencode": {
            "enabled": False if is_matched_runtime and uses_react_runtime else bool(instance.get("opencode_required")),
            "reason": (
                "成熟模板命中后，常规生成只组装 React 学生运行时；OpenCode 不参与每次实时生成。"
                if is_matched_runtime and uses_react_runtime
                else "仅当没有成熟运行时可交付时，才允许进入受契约约束的生成或修复。"
            ),
        },
        "allowed_roles": [
            {
                "id": "presentation_pack_refiner",
                "when": "教师主动选择高级精修，或定稿前需要提升皮肤、动效、奖励反馈。",
                "allowed_files": ["config/frontend-presentation-pack.json", "config/opencode-artifact-summary.md"],
                "must_not_change": ["玩法类型", "音乐答案", "教学目标", "React 学生运行时代码"],
            },
            {
                "id": "template_factory",
                "when": "研发侧扩充成熟模板、增加新皮肤、升级某个运行时组件。",
                "allowed_scope": ["frontend/src/student-game", "app/services/game_template_registry.py", "tests"],
                "must_include": ["可运行交互", "皮肤差异", "构建或测试验证"],
            },
            {
                "id": "lesson_specific_generator",
                "when": "教案重点没有命中成熟模板，或模板运行时不是 production。",
                "must_follow": ["lesson_game_contract", "frontend_handoff_contract", "student_page_contract"],
            },
        ],
        "forbidden_roles": [
            "常规命中模板后临时重写 index.html",
            "把模板配置页当作最终学生游戏交付",
            "为了换皮肤改动音乐判定或答案",
            "在教师配置面板暴露代码、JSON 或 OpenCode 术语",
        ],
        "current_contract": {
            "template_id": template_id,
            "presentation_pack_kind": presentation_pack.get("output_kind", ""),
            "runtime_target": presentation_pack.get("runtime_target", ""),
            "frontend_mode": frontend_handoff_contract.get("mode", ""),
        },
    }


def opencode_regular_path_is_isolated(policy: dict[str, Any]) -> bool:
    realtime = policy.get("realtime_opencode", {}) if isinstance(policy.get("realtime_opencode"), dict) else {}
    allowed_roles = policy.get("allowed_roles", []) if isinstance(policy.get("allowed_roles"), list) else []
    if policy.get("regular_generation_route") == "react_runtime_without_opencode":
        return realtime.get("enabled") is False and any(
            isinstance(role, dict) and role.get("id") == "presentation_pack_refiner" for role in allowed_roles
        )
    return any(isinstance(role, dict) and role.get("id") == "lesson_specific_generator" for role in allowed_roles)
