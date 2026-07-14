from __future__ import annotations

from copy import deepcopy
from typing import Any


FRONTEND_HANDOFF_VERSION = "frontend_handoff_v1"
RADIX_COMPONENT_LIBRARY = "Radix Themes"


def build_frontend_handoff_contract(
    *,
    workflow_kind: str,
    lesson_adaptation: dict[str, Any] | None,
    template_decision: dict[str, Any] | None,
    gameplay_blueprint: dict[str, Any],
    theme_pack: dict[str, Any],
    render_spec: dict[str, Any],
) -> dict[str, Any]:
    """Define what frontend generation may polish and what it must preserve."""

    template_decision = template_decision if isinstance(template_decision, dict) else {}
    lesson_adaptation = lesson_adaptation if isinstance(lesson_adaptation, dict) else {}
    template_id = str(template_decision.get("template_id") or "")
    matched_template = bool(template_id)
    forbid_standalone_web_trio = matched_template
    if workflow_kind == "lesson_game" and not matched_template:
        mode = "freeform_presentation_with_locked_learning_contract"
        output_kind = "standalone_student_page"
        assembly_target = "lesson_specific_runtime"
    else:
        mode = "presentation_refinement_only"
        output_kind = "react_presentation_pack"
        assembly_target = "react_student_runtime"
    music_entity_execution = _music_entity_execution(gameplay_blueprint, render_spec)
    patch_feedback = _patch_feedback(music_entity_execution)
    return {
        "version": FRONTEND_HANDOFF_VERSION,
        "owner": "frontend_presentation_director",
        "recommended_executor": "opencode_frontend",
        "mode": mode,
        "output_kind": output_kind,
        "assembly_target": assembly_target,
        "component_library": RADIX_COMPONENT_LIBRARY,
        "forbid_standalone_web_trio": forbid_standalone_web_trio,
        "responsibility": "turn_locked_gameplay_into_student_facing_game_experience",
        "allowed_changes": [
            "场景世界观",
            "布局变体",
            "视觉层级",
            "动效与奖励反馈",
            "角色和皮肤资产",
            "学生可见文案润色",
        ],
        "locked_inputs": [
            "lesson_adaptation.student_learning_contract",
            "gameplay_blueprint.operation_type",
            "gameplay_blueprint.win_condition",
            "game_variant_spec.entity_application",
            "music_logic_contract",
            "template_decision.template_id",
        ],
        "must_not_change": [
            "不改教学目标",
            "不改音乐材料答案",
            "不改学生必须完成的学习动作",
            "不把模板页直接当成学生游戏交付",
        ],
        "expected_output": (
            "只输出可被 React 学生运行时消费的 Radix 表现层包，不生成独立学生页。"
            if forbid_standalone_web_trio
            else "未命中成熟模板时允许生成受教案契约约束的独立学生页。"
        ),
        "lesson_adaptation_ref": lesson_adaptation.get("version", ""),
        "template_decision_ref": template_decision.get("version", ""),
        "presentation_inputs": {
            "operation_type": gameplay_blueprint.get("operation_type", ""),
            "player_verb": gameplay_blueprint.get("player_verb", ""),
            "skin_family": theme_pack.get("skin_family", ""),
            "layout_variant": theme_pack.get("layout_variant", ""),
            "scene": deepcopy(theme_pack.get("scene", {})),
            "render_playfield": render_spec.get("screen_structure", {}).get("playfield", {}),
            "music_entity_execution": music_entity_execution,
            "template_capability_match": _template_capability_match(music_entity_execution),
            "patch_feedback": patch_feedback,
        },
    }


def _music_entity_execution(gameplay_blueprint: dict[str, Any], render_spec: dict[str, Any]) -> dict[str, Any]:
    variant = gameplay_blueprint.get("game_variant_spec")
    if isinstance(variant, dict) and variant:
        return _music_entity_execution_from_variant(variant)
    render_execution = render_spec.get("music_entity_execution")
    if isinstance(render_execution, dict) and render_execution:
        return deepcopy(render_execution)
    blueprint_execution = gameplay_blueprint.get("music_entity_execution")
    if isinstance(blueprint_execution, dict) and blueprint_execution:
        return deepcopy(blueprint_execution)
    return {}


def _music_entity_execution_from_variant(variant: dict[str, Any]) -> dict[str, Any]:
    return {
        "contract_schema_version": deepcopy(variant.get("contract_schema_version", "")),
        "music_entity": deepcopy(variant.get("music_entity", {})),
        "variant_parameters": deepcopy(variant.get("variant_parameters", {})),
        "slot_bindings": deepcopy(variant.get("slot_bindings", {})),
        "entity_application": deepcopy(variant.get("entity_application", {})),
        "material_entities": deepcopy(variant.get("material_entities", [])) if isinstance(variant.get("material_entities"), list) else [],
        "selected_entity": deepcopy(variant.get("selected_entity", {})) if isinstance(variant.get("selected_entity"), dict) else {},
        "template_capability_match": deepcopy(variant.get("template_capability_match", {}))
        if isinstance(variant.get("template_capability_match"), dict)
        else {},
        "execution_plan": deepcopy(variant.get("execution_plan", {})) if isinstance(variant.get("execution_plan"), dict) else {},
        "confirmation_gates": deepcopy(variant.get("confirmation_gates", [])) if isinstance(variant.get("confirmation_gates"), list) else [],
        "teacher_confirmation_cards": deepcopy(variant.get("teacher_confirmation_cards", []))
        if isinstance(variant.get("teacher_confirmation_cards"), list)
        else [],
        "revision_history": deepcopy(variant.get("revision_history", [])) if isinstance(variant.get("revision_history"), list) else [],
    }


def _template_capability_match(music_entity_execution: dict[str, Any]) -> dict[str, Any]:
    match = music_entity_execution.get("template_capability_match")
    return deepcopy(match) if isinstance(match, dict) else {}


def _patch_feedback(music_entity_execution: dict[str, Any]) -> dict[str, Any]:
    capability_match = _template_capability_match(music_entity_execution)
    if capability_match.get("status") == "rejected" and capability_match.get("teacher_message"):
        return {
            "latest_teacher_message": capability_match.get("teacher_message", ""),
            "latest_reason": capability_match.get("reason", "unsupported_entity_for_current_template"),
            "latest_recommended_template_id": capability_match.get("recommended_template_id", ""),
            "latest_rejected_paths": [],
        }
    history = music_entity_execution.get("revision_history") if isinstance(music_entity_execution.get("revision_history"), list) else []
    latest = next(
        (
            item
            for item in reversed(history)
            if isinstance(item, dict) and item.get("revision_type") == "patch_rejected"
        ),
        {},
    )
    if not latest:
        return {}
    return {
        "latest_teacher_message": latest.get("teacher_message", ""),
        "latest_reason": latest.get("reason", ""),
        "latest_recommended_template_id": latest.get("recommended_template_id", ""),
        "latest_rejected_paths": deepcopy(latest.get("rejected_paths", [])) if isinstance(latest.get("rejected_paths"), list) else [],
    }
