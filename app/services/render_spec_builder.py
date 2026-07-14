from __future__ import annotations

from typing import Any


def build_render_spec(
    *,
    workflow_kind: str,
    gameplay_blueprint: dict[str, Any],
    experience_script: dict[str, Any],
    theme_pack: dict[str, Any],
) -> dict[str, Any]:
    """Create the frontend-facing student game rendering contract."""

    operation_type = str(gameplay_blueprint.get("operation_type") or "")
    template_id = str(gameplay_blueprint.get("based_on_template") or "")
    playfield_type = _playfield_type(operation_type, template_id)
    controls = gameplay_blueprint.get("ui_contract", {}).get("must_have_controls", [])
    if not isinstance(controls, list) or not controls:
        controls = _default_controls(operation_type)
    return {
        "version": "render_spec_v1",
        "artifact_type": "student_game",
        "framework": "react_compatible_runtime",
        "component_library": "radix_ui",
        "runtime": "web_audio",
        "workflow_kind": workflow_kind,
        "gameplay_blueprint_ref": gameplay_blueprint.get("version", ""),
        "theme_pack_ref": theme_pack.get("theme_id", ""),
        "screen_structure": {
            "hero": {"show": True, "content": gameplay_blueprint.get("student_facing_name", "")},
            "hud": {"show_round": True, "show_progress": True, "show_score": _show_score(operation_type)},
            "playfield": {"type": playfield_type, "priority": "primary"},
            "experience_variant": {
                "id": gameplay_blueprint.get("experience_variant_id", ""),
                "play_mode": gameplay_blueprint.get("play_mode", ""),
                "game_genre": gameplay_blueprint.get("game_genre", ""),
                "composition": gameplay_blueprint.get("playfield_composition", ""),
                "scene_goal": gameplay_blueprint.get("scene_goal", ""),
            },
            "controls": controls,
            "feedback_panel": {"position": "below_playfield", "persistent": True},
            "teacher_overlay": {"show_in_student_mode": False},
        },
        "responsive_rules": {
            "desktop": "playfield_first_two_column",
            "tablet": "stacked_panels",
            "mobile": "single_column",
        },
        "experience_hooks": {
            "opening_hook": experience_script.get("opening_hook", ""),
            "closure_prompt": experience_script.get("closure_prompt", ""),
        },
        "music_entity_execution": _music_entity_execution(gameplay_blueprint),
        "visual_tokens": theme_pack.get("palette", {}),
        "presentation_contract": {
            "skin_family": theme_pack.get("skin_family", ""),
            "layout_variant": theme_pack.get("layout_variant", ""),
            "scene": theme_pack.get("scene", {}),
            "reward_token": theme_pack.get("reward_token", ""),
            "experience_variant_id": gameplay_blueprint.get("experience_variant_id", ""),
            "play_mode": gameplay_blueprint.get("play_mode", ""),
            "playfield_composition": gameplay_blueprint.get("playfield_composition", ""),
        },
    }


def _music_entity_execution(gameplay_blueprint: dict[str, Any]) -> dict[str, Any]:
    variant = gameplay_blueprint.get("game_variant_spec")
    if isinstance(variant, dict) and variant:
        return _music_entity_execution_from_variant(variant)
    execution = gameplay_blueprint.get("music_entity_execution")
    if isinstance(execution, dict) and execution:
        return {
            "contract_schema_version": execution.get("contract_schema_version", ""),
            "music_entity": execution.get("music_entity", {}) if isinstance(execution.get("music_entity"), dict) else {},
            "variant_parameters": execution.get("variant_parameters", {}) if isinstance(execution.get("variant_parameters"), dict) else {},
            "slot_bindings": execution.get("slot_bindings", {}) if isinstance(execution.get("slot_bindings"), dict) else {},
            "entity_application": execution.get("entity_application", {}) if isinstance(execution.get("entity_application"), dict) else {},
            "material_entities": execution.get("material_entities", []) if isinstance(execution.get("material_entities"), list) else [],
            "selected_entity": execution.get("selected_entity", {}) if isinstance(execution.get("selected_entity"), dict) else {},
            "template_capability_match": (
                execution.get("template_capability_match", {}) if isinstance(execution.get("template_capability_match"), dict) else {}
            ),
            "execution_plan": execution.get("execution_plan", {}) if isinstance(execution.get("execution_plan"), dict) else {},
            "confirmation_gates": execution.get("confirmation_gates", []) if isinstance(execution.get("confirmation_gates"), list) else [],
            "teacher_confirmation_cards": (
                execution.get("teacher_confirmation_cards", []) if isinstance(execution.get("teacher_confirmation_cards"), list) else []
            ),
            "revision_history": execution.get("revision_history", []) if isinstance(execution.get("revision_history"), list) else [],
        }
    return {}


def _music_entity_execution_from_variant(variant: dict[str, Any]) -> dict[str, Any]:
    return {
        "contract_schema_version": variant.get("contract_schema_version", ""),
        "music_entity": variant.get("music_entity", {}) if isinstance(variant.get("music_entity"), dict) else {},
        "variant_parameters": variant.get("variant_parameters", {}) if isinstance(variant.get("variant_parameters"), dict) else {},
        "slot_bindings": variant.get("slot_bindings", {}) if isinstance(variant.get("slot_bindings"), dict) else {},
        "entity_application": variant.get("entity_application", {}) if isinstance(variant.get("entity_application"), dict) else {},
        "material_entities": variant.get("material_entities", []) if isinstance(variant.get("material_entities"), list) else [],
        "selected_entity": variant.get("selected_entity", {}) if isinstance(variant.get("selected_entity"), dict) else {},
        "template_capability_match": variant.get("template_capability_match", {}) if isinstance(variant.get("template_capability_match"), dict) else {},
        "execution_plan": variant.get("execution_plan", {}) if isinstance(variant.get("execution_plan"), dict) else {},
        "confirmation_gates": variant.get("confirmation_gates", []) if isinstance(variant.get("confirmation_gates"), list) else [],
        "teacher_confirmation_cards": variant.get("teacher_confirmation_cards", [])
        if isinstance(variant.get("teacher_confirmation_cards"), list)
        else [],
        "revision_history": variant.get("revision_history", []) if isinstance(variant.get("revision_history"), list) else [],
    }


def _playfield_type(operation_type: str, template_id: str = "") -> str:
    template_scene = {
        "beat_guardian_core": "beat_guardian_scene",
        "rhythm_echo_core": "rhythm_echo_scene",
        "pitch_ladder_core": "pitch_ladder_scene",
        "solfege_target_core": "solfege_target_scene",
        "timbre_detective_core": "timbre_detective_desk",
        "form_treasure_core": "form_treasure_scene",
        "composition_puzzle_core": "composition_puzzle_scene",
    }.get(template_id)
    if template_scene:
        return template_scene
    if operation_type == "melody_path_draw":
        return "path_grid"
    if "beat" in operation_type:
        return "beat_lane"
    if "rhythm" in operation_type:
        return "rhythm_timeline"
    if "timbre" in operation_type:
        return "evidence_caseboard"
    if "form" in operation_type:
        return "form_timeline"
    if "composition" in operation_type:
        return "composition_puzzle_scene"
    if "solfege" in operation_type:
        return "target_arena"
    return "sequence_stage"


def _default_controls(operation_type: str) -> list[str]:
    if operation_type == "melody_path_draw":
        return ["听乐句", "播放我的路线", "检查路线", "重画"]
    if "beat" in operation_type:
        return ["开始节拍", "充能", "重新开始"]
    if "rhythm" in operation_type:
        return ["听示范", "拍一下", "下一轮", "重来"]
    if "form" in operation_type:
        return ["听段落", "验证路线", "重置结构卡"]
    if "composition" in operation_type:
        return ["选择素材", "试听作品", "检查约束", "教师确认", "重来"]
    return ["试听目标", "检查挑战", "重来"]


def _show_score(operation_type: str) -> bool:
    return any(keyword in operation_type for keyword in ["beat", "rhythm", "target", "timbre", "form", "composition"])
