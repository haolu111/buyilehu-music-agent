from __future__ import annotations

from typing import Any


REQUIRED_BLUEPRINT_FIELDS = [
    "student_facing_name",
    "player_verb",
    "operation_type",
    "core_loop",
    "win_condition",
    "retry_rule",
    "feedback_rules",
    "rounds",
]


def evaluate_delivery_gate(
    *,
    workflow_kind: str,
    gameplay_blueprint: dict[str, Any],
    experience_script: dict[str, Any],
    theme_pack: dict[str, Any],
    render_spec: dict[str, Any],
) -> dict[str, Any]:
    """Decide whether a workflow has enough structure to become a student game."""

    blocked_by: list[str] = []
    if any(not gameplay_blueprint.get(field) for field in REQUIRED_BLUEPRINT_FIELDS):
        blocked_by.append("gameplay_blueprint_incomplete")
    if not experience_script.get("opening_hook") or not experience_script.get("closure_prompt"):
        blocked_by.append("experience_script_incomplete")
    if not theme_pack.get("theme_name") or not theme_pack.get("palette"):
        blocked_by.append("theme_pack_incomplete")
    if not _has_distinct_game_variant(gameplay_blueprint, theme_pack):
        blocked_by.append("experience_variant_incomplete")
    screen = render_spec.get("screen_structure", {}) if isinstance(render_spec.get("screen_structure"), dict) else {}
    playfield = screen.get("playfield", {}) if isinstance(screen.get("playfield"), dict) else {}
    controls = screen.get("controls", []) if isinstance(screen.get("controls"), list) else []
    if playfield.get("priority") != "primary" or not controls:
        blocked_by.append("render_spec_not_student_ready")
    if workflow_kind == "lesson_game":
        transfer = gameplay_blueprint.get("learning_transfer", {})
        if not isinstance(transfer, dict) or not transfer.get("classroom_transfer"):
            blocked_by.append("lesson_transfer_missing")

    approved = not blocked_by
    score = max(0, 100 - 18 * len(blocked_by))
    return {
        "version": "delivery_decision_v1",
        "status": "approved" if approved else "rejected",
        "score": score,
        "reasons": _reasons(workflow_kind, gameplay_blueprint, approved),
        "blocked_by": blocked_by,
        "fallback_action": None if approved else "return_to_gameplay_blueprint",
    }


def _reasons(workflow_kind: str, blueprint: dict[str, Any], approved: bool) -> list[str]:
    if not approved:
        return ["学生成品游戏的必要结构尚未齐备。"]
    reasons = [
        f"已明确学生动作：{blueprint.get('player_verb', '完成挑战')}。",
        "已具备完整的开始、操作、反馈、重试和通关结构。",
        "页面渲染以主游戏舞台为中心，而不是模板说明页。",
        f"已绑定体验变体：{blueprint.get('experience_variant_id') or '课堂专属变体'}。",
    ]
    if workflow_kind == "lesson_game":
        reasons.append("已保留课堂迁移闭环。")
    return reasons


def _has_distinct_game_variant(blueprint: dict[str, Any], theme_pack: dict[str, Any]) -> bool:
    required = (
        blueprint.get("experience_variant_id"),
        blueprint.get("play_mode"),
        blueprint.get("scene_goal"),
        blueprint.get("interaction_feedback"),
        blueprint.get("failure_feedback"),
        blueprint.get("reward_loop"),
        blueprint.get("playfield_composition") or theme_pack.get("playfield_composition"),
    )
    return all(bool(item) for item in required)
