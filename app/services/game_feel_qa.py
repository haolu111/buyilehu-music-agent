from __future__ import annotations

from typing import Any


def build_game_feel_qa_report(
    *,
    production_status: str,
    game_design: dict[str, Any],
    music_truth: dict[str, Any],
    audio_manifest: dict[str, Any],
    runtime_config: dict[str, Any],
    teacher_control_config: dict[str, Any],
    original_game_concept: dict[str, Any] | None = None,
    component_assembly_plan: dict[str, Any] | None = None,
    game_state_machine: dict[str, Any] | None = None,
    scene_bible: str = "",
    asset_contract: dict[str, Any] | None = None,
    image_generation_tasks: dict[str, Any] | None = None,
    generated_asset_registry: dict[str, Any] | None = None,
    asset_validation: dict[str, Any] | None = None,
    animation_plan: dict[str, Any] | None = None,
) -> dict[str, Any]:
    blocking_issues: list[str] = []
    original_game_concept = original_game_concept if isinstance(original_game_concept, dict) else {}
    component_assembly_plan = component_assembly_plan if isinstance(component_assembly_plan, dict) else {}
    game_state_machine = game_state_machine if isinstance(game_state_machine, dict) else {}
    asset_contract = asset_contract if isinstance(asset_contract, dict) else {}
    image_generation_tasks = image_generation_tasks if isinstance(image_generation_tasks, dict) else {}
    generated_asset_registry = generated_asset_registry if isinstance(generated_asset_registry, dict) else {}
    asset_validation = asset_validation if isinstance(asset_validation, dict) else {}
    animation_plan = animation_plan if isinstance(animation_plan, dict) else {}
    if production_status == "blocked" or music_truth.get("truth_status") == "blocked":
        blocking_issues.append("teacher_confirmation_required")
    if not game_design.get("mechanic_contract"):
        blocking_issues.append("missing_mechanic_contract")
    sounds = audio_manifest.get("sounds") if isinstance(audio_manifest.get("sounds"), list) else []
    if not sounds:
        blocking_issues.append("missing_audio_manifest")
    if not runtime_config.get("template_id"):
        blocking_issues.append("missing_runtime_config")
    if not teacher_control_config.get("editable_controls"):
        blocking_issues.append("missing_teacher_controls")
    if not original_game_concept.get("not_template_skin_reason"):
        blocking_issues.append("missing_original_game_concept")
    reusable_components = component_assembly_plan.get("reusable_components")
    if not isinstance(reusable_components, list) or not reusable_components:
        blocking_issues.append("missing_component_assembly_plan")
    if not _component_capability_matches_ready(component_assembly_plan):
        blocking_issues.append("missing_registered_component_capability_matches")
    required_states = {"start", "listen", "student_action", "judge", "feedback", "retry", "reward", "classroom_return"}
    states = game_state_machine.get("states") if isinstance(game_state_machine.get("states"), list) else []
    state_ids = {str(state.get("id")) for state in states if isinstance(state, dict)}
    if not required_states.issubset(state_ids):
        blocking_issues.append("missing_template_quality_state_machine")
    if not scene_bible or "资产需求" not in scene_bible:
        blocking_issues.append("missing_scene_bible_asset_direction")
    assets = asset_contract.get("assets") if isinstance(asset_contract.get("assets"), list) else []
    if not assets:
        blocking_issues.append("missing_asset_contract")
    registry_status = str(generated_asset_registry.get("status") or "")
    if registry_status == "blocked_missing_assets":
        blocking_issues.append("missing_generated_asset_registry")
    if not isinstance(image_generation_tasks.get("tasks"), list):
        blocking_issues.append("missing_image_generation_tasks")
    if asset_validation.get("status") == "blocked":
        blocking_issues.extend(str(issue) for issue in asset_validation.get("blocking_issues", []))
    animation_states = animation_plan.get("states") if isinstance(animation_plan.get("states"), list) else []
    animation_state_ids = {str(state.get("state")) for state in animation_states if isinstance(state, dict)}
    if not {"idle", "action", "success", "fail", "retry"}.issubset(animation_state_ids):
        blocking_issues.append("missing_animation_state_plan")
    warning_issues = []
    if music_truth.get("truth_status") == "draft":
        warning_issues.append("teacher_confirmation_required")
    if generated_asset_registry.get("pending_generation_assets"):
        warning_issues.append("image_generation_assets_pending")
    return {
        "version": "qa_report_v1",
        "status": "blocked" if blocking_issues else "pass",
        "checked_contracts": [
            "original_game_concept",
            "component_assembly_plan",
            "game_design",
            "music_truth",
            "audio_manifest",
            "game_state_machine",
            "scene_bible",
            "asset_contract",
            "image_generation_tasks",
            "generated_asset_registry",
            "asset_validation",
            "animation_plan",
            "runtime_config",
            "teacher_control_config",
        ],
        "blocking_issues": blocking_issues,
        "warning_issues": warning_issues,
        "manual_browser_qa_required": True,
        "checks": [
            {"id": "first_screen_understandable", "status": "planned"},
            {"id": "audio_button_no_error", "status": "planned"},
            {"id": "mobile_layout_playable", "status": "planned"},
            {"id": "three_minute_round", "status": "planned"},
        ],
    }


def _component_capability_matches_ready(component_assembly_plan: dict[str, Any]) -> bool:
    matches = component_assembly_plan.get("capability_matches")
    if not isinstance(matches, list) or not matches:
        return False
    if component_assembly_plan.get("missing_required_capabilities"):
        return False
    runtime_bindings = component_assembly_plan.get("runtime_bindings")
    if not isinstance(runtime_bindings, dict) or not runtime_bindings:
        return False
    for match in matches:
        if not isinstance(match, dict):
            return False
        component_id = str(match.get("registered_component_id") or "").strip()
        if not component_id or not match.get("registered_component"):
            return False
        bindings = runtime_bindings.get(component_id)
        if not isinstance(bindings, list) or not bindings:
            return False
    return True
