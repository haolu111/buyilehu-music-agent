from __future__ import annotations

from copy import deepcopy
from typing import Any
from uuid import uuid4

from app.services.asset_visual_qa import build_asset_validation_report


MUSIC_GAME_PRODUCTION_SPEC_VERSION = "music_game_production_spec_v1"
PRODUCTION_ARTIFACT_FILES = [
    "original-game-concept.json",
    "component-assembly-plan.json",
    "game-concept.json",
    "game-design.json",
    "music-truth.json",
    "audio-manifest.json",
    "level-curve.json",
    "game-state-machine.json",
    "scene-bible.md",
    "asset-contract.json",
    "image-generation-tasks.json",
    "generated-asset-registry.json",
    "image-generation-execution-report.json",
    "asset-validation.json",
    "animation-plan.json",
    "production-line-checklist.json",
    "runtime-config.json",
    "teacher-control-config.json",
    "qa-report.json",
]


def build_runtime_config(
    instance: dict[str, Any],
    *,
    package_id: str,
    music_truth: dict[str, Any],
    audio_manifest: dict[str, Any],
    level_curve: dict[str, Any],
    game_concept: dict[str, Any] | None = None,
    lesson_runtime_generated_assets: dict[str, Any] | None = None,
) -> dict[str, Any]:
    config = deepcopy(instance.get("config")) if isinstance(instance.get("config"), dict) else {}
    game_concept = game_concept if isinstance(game_concept, dict) else {}
    config["production_package_ref"] = package_id
    config["music_truth_ref"] = "music-truth.json"
    config["audio_manifest_ref"] = "audio-manifest.json"
    config["level_curve_ref"] = "level-curve.json"
    config["runtime_may_guess_answers"] = False
    config["music_truth_status"] = music_truth.get("truth_status", "")
    config["music_truth_contract"] = {
        "ref": "music-truth.json",
        "required_fields": [
            "source_segment_id",
            "material",
            "error_categories",
            "judgement_windows",
        ],
        "error_categories": deepcopy(music_truth.get("error_categories", [])),
        "judgement_windows": deepcopy(music_truth.get("judgement_windows", {})),
    }
    config["audio_policy"] = deepcopy(audio_manifest.get("playback_policy", {}))
    config["level_count"] = len(level_curve.get("levels", [])) if isinstance(level_curve.get("levels"), list) else 0
    if game_concept:
        config["game_concept_ref"] = "game-concept.json"
        config["source_segment_id"] = game_concept.get("source_segment_id", "")
        config["source_evidence"] = game_concept.get("source_evidence", "")
        config["student_actions"] = deepcopy(game_concept.get("student_actions", []))
        config["classroom_return"] = game_concept.get("classroom_return", "")
        config["success_condition"] = game_concept.get("success_condition", "")
    lesson_assets = lesson_runtime_generated_assets if isinstance(lesson_runtime_generated_assets, dict) else {}
    if lesson_assets:
        config["lesson_runtime_generated_assets"] = deepcopy(lesson_assets)
        config["runtime_asset_manifest"] = _runtime_asset_manifest_from_lesson_assets(lesson_assets)
        config["runtime_asset_manifest_ref"] = "assets/runtime-asset-manifest.json"
    return config


def build_teacher_control_config(
    instance: dict[str, Any],
    *,
    package_id: str,
    activity_spec: dict[str, Any] | None = None,
) -> dict[str, Any]:
    config = instance.get("config") if isinstance(instance.get("config"), dict) else {}
    controls = ["tempo", "hint_amount", "difficulty", "level_select", "reset"]
    if source_has_segment_brief(activity_spec):
        controls.append("only_practice_selected_segment")
    if config.get("allow_relisten", True):
        controls.append("relisten_limit")
    return {
        "version": "teacher_control_config_v1",
        "production_package_ref": package_id,
        "editable_controls": controls,
        "defaults": {
            "tempo": config.get("bpm"),
            "allow_relisten": config.get("allow_relisten", True),
            "round_count": config.get("round_count"),
            "runtime_ref": (activity_spec or {}).get("runtime_ref", "teacher_projection"),
        },
        "patch_policy": "teacher_changes_must_rebuild_music_truth_runtime_config_and_qa",
    }


def assemble_music_game_production_spec(
    *,
    workflow_kind: str,
    activity_spec: dict[str, Any],
    source: dict[str, Any],
    instance: dict[str, Any],
    game_design: dict[str, Any],
    music_truth: dict[str, Any],
    audio_manifest: dict[str, Any],
    level_curve: dict[str, Any],
    scene_bible: str,
    asset_contract: dict[str, Any],
    original_game_concept: dict[str, Any],
    component_assembly_plan: dict[str, Any],
    game_state_machine: dict[str, Any],
    image_generation_tasks: dict[str, Any],
    generated_asset_registry: dict[str, Any],
    lesson_runtime_generated_assets: dict[str, Any] | None = None,
    animation_plan: dict[str, Any],
    game_concept: dict[str, Any] | None = None,
    qa_builder,
) -> dict[str, Any]:
    package_id = f"mgp_{uuid4().hex[:12]}"
    game_concept = game_concept if isinstance(game_concept, dict) else {}
    runtime_config = build_runtime_config(
        instance,
        package_id=package_id,
        music_truth=music_truth,
        audio_manifest=audio_manifest,
        level_curve=level_curve,
        game_concept=game_concept,
        lesson_runtime_generated_assets=lesson_runtime_generated_assets,
    )
    runtime_config["original_game_concept_ref"] = "original-game-concept.json"
    runtime_config["component_assembly_plan_ref"] = "component-assembly-plan.json"
    runtime_config["game_state_machine_ref"] = "game-state-machine.json"
    runtime_config["scene_bible_ref"] = "scene-bible.md"
    runtime_config["asset_contract_ref"] = "asset-contract.json"
    runtime_config["image_generation_tasks_ref"] = "image-generation-tasks.json"
    runtime_config["generated_asset_registry_ref"] = "generated-asset-registry.json"
    runtime_config["animation_plan_ref"] = "animation-plan.json"
    runtime_config["state_asset_bindings"] = deepcopy(game_state_machine.get("state_asset_bindings", {}))
    lesson_runtime_generated_assets = (
        lesson_runtime_generated_assets if isinstance(lesson_runtime_generated_assets, dict) else {}
    )
    runtime_config["lesson_runtime_generated_assets"] = deepcopy(lesson_runtime_generated_assets)
    runtime_config["runtime_asset_manifest"] = _runtime_asset_manifest(lesson_runtime_generated_assets)
    teacher_control_config = build_teacher_control_config(
        instance,
        package_id=package_id,
        activity_spec=activity_spec,
    )
    asset_validation = build_asset_validation_report(
        asset_contract=asset_contract,
        generated_asset_registry=generated_asset_registry,
        image_generation_tasks=image_generation_tasks,
        runtime_config=runtime_config,
    )
    image_generation_execution_report = _image_generation_execution_report(generated_asset_registry, image_generation_tasks)
    production_status = "blocked" if music_truth.get("truth_status") == "blocked" else "ready_for_runtime"
    qa_report = qa_builder(
        production_status=production_status,
        game_design=game_design,
        music_truth=music_truth,
        audio_manifest=audio_manifest,
        runtime_config=runtime_config,
        teacher_control_config=teacher_control_config,
        original_game_concept=original_game_concept,
        component_assembly_plan=component_assembly_plan,
        game_state_machine=game_state_machine,
        scene_bible=scene_bible,
        asset_contract=asset_contract,
        image_generation_tasks=image_generation_tasks,
        generated_asset_registry=generated_asset_registry,
        asset_validation=asset_validation,
        animation_plan=animation_plan,
    )
    if game_concept:
        checked = qa_report.setdefault("checked_contracts", [])
        if isinstance(checked, list) and "lesson_segment_grounding" not in checked:
            checked.append("lesson_segment_grounding")
    if qa_report.get("status") == "blocked":
        production_status = "blocked"
    return {
        "version": MUSIC_GAME_PRODUCTION_SPEC_VERSION,
        "package_id": package_id,
        "workflow_kind": workflow_kind,
        "template_id": instance.get("template_id") or runtime_config.get("template_id", ""),
        "production_status": production_status,
        "artifact_manifest": {
            "version": "music_game_artifact_manifest_v1",
            "required_files": list(PRODUCTION_ARTIFACT_FILES),
            "files": {
                "original-game-concept.json": "original_game_concept",
                "component-assembly-plan.json": "component_assembly_plan",
                "game-concept.json": "game_concept",
                "game-design.json": "game_design",
                "music-truth.json": "music_truth",
                "audio-manifest.json": "audio_manifest",
                "level-curve.json": "level_curve",
                "game-state-machine.json": "game_state_machine",
                "scene-bible.md": "scene_bible",
                "asset-contract.json": "asset_contract",
                "image-generation-tasks.json": "image_generation_tasks",
                "generated-asset-registry.json": "generated_asset_registry",
                "image-generation-execution-report.json": "image_generation_execution_report",
                "asset-validation.json": "asset_validation",
                "animation-plan.json": "animation_plan",
                "production-line-checklist.json": "production_line_checklist",
                "runtime-config.json": "runtime_config",
                "teacher-control-config.json": "teacher_control_config",
                "qa-report.json": "qa_report",
            },
        },
        "activity_spec_ref": deepcopy(activity_spec),
        "source_summary": _source_summary(source),
        "game_concept": game_concept,
        "original_game_concept": original_game_concept,
        "component_assembly_plan": component_assembly_plan,
        "game_design": game_design,
        "music_truth": music_truth,
        "audio_manifest": audio_manifest,
        "level_curve": level_curve,
        "game_state_machine": game_state_machine,
        "scene_bible": scene_bible,
        "asset_contract": asset_contract,
        "image_generation_tasks": image_generation_tasks,
        "generated_asset_registry": generated_asset_registry,
        "lesson_runtime_generated_assets": lesson_runtime_generated_assets,
        "image_generation_execution_report": image_generation_execution_report,
        "asset_validation": asset_validation,
        "animation_plan": animation_plan,
        "runtime_config": runtime_config,
        "teacher_control_config": teacher_control_config,
        "qa_report": qa_report,
    }


def _source_summary(source: dict[str, Any]) -> dict[str, Any]:
    return {
        "has_lesson_fit": isinstance(source.get("lesson_fit"), dict) and bool(source.get("lesson_fit")),
        "has_lesson_source": isinstance(source.get("lesson_source"), dict) and bool(source.get("lesson_source")),
        "need": str(source.get("need") or "")[:160],
    }


def _runtime_asset_manifest_from_lesson_assets(lesson_assets: dict[str, Any]) -> dict[str, Any]:
    manifest: dict[str, Any] = {"version": "runtime_asset_manifest_v1", "assets": {}}
    scene = lesson_assets.get("scene_background") if isinstance(lesson_assets.get("scene_background"), dict) else {}
    if scene:
        scene_file = f"{str(scene.get('save_dir') or 'assets/').rstrip('/')}/{str(scene.get('file') or 'scene-background.png')}"
        manifest["scene_background"] = scene_file
        manifest["assets"]["scene_background"] = {
            "file": scene_file,
            "provider": scene.get("provider", "agent_internal_image_gen"),
            "ratio": scene.get("ratio", "16:9"),
            "reason": scene.get("reason", ""),
        }
    return manifest


def _image_generation_execution_report(
    generated_asset_registry: dict[str, Any],
    image_generation_tasks: dict[str, Any],
) -> dict[str, Any]:
    tasks = image_generation_tasks.get("tasks") if isinstance(image_generation_tasks.get("tasks"), list) else []
    registry_status = str(generated_asset_registry.get("status") or "")
    if registry_status == "pending_generation":
        status = "pending_generation"
    elif tasks:
        status = "not_executed"
    else:
        status = "not_required"
    return {
        "version": "image_generation_execution_report_v1",
        "status": status,
        "executor": "not_required" if not tasks else "",
        "provider_boundary": "agent_internal_image_gen_only_not_image2_or_chat_ecnu",
        "provider_policy": image_generation_tasks.get("provider_policy", {}) if isinstance(image_generation_tasks, dict) else {},
        "task_count": len(tasks),
        "generated_count": 0,
        "results": [],
    }


def _runtime_asset_manifest(lesson_runtime_generated_assets: dict[str, Any]) -> dict[str, str]:
    manifest: dict[str, str] = {}
    for asset_id, asset in lesson_runtime_generated_assets.items():
        if not isinstance(asset, dict):
            continue
        save_dir = str(asset.get("save_dir") or "assets/")
        file_name = str(asset.get("file") or "").strip()
        if not file_name:
            continue
        manifest[str(asset_id)] = f"{save_dir.rstrip('/')}/{file_name}"
    return manifest


def build_game_concept_from_segment_brief(segment_game_brief: dict[str, Any] | None) -> dict[str, Any]:
    brief = segment_game_brief if isinstance(segment_game_brief, dict) else {}
    if not brief:
        return {}
    return {
        "version": "game_concept_v1",
        "source": "segment_game_brief",
        "source_segment_id": str(brief.get("source_segment_id") or ""),
        "source_evidence": str(brief.get("source_evidence") or ""),
        "game_goal": str(brief.get("game_goal") or ""),
        "music_learning_target": str(brief.get("music_learning_target") or ""),
        "student_actions": deepcopy(brief.get("student_actions", [])) if isinstance(brief.get("student_actions"), list) else [],
        "core_mechanic": str(brief.get("core_mechanic") or ""),
        "success_condition": str(brief.get("success_condition") or ""),
        "error_feedback": deepcopy(brief.get("error_feedback", [])) if isinstance(brief.get("error_feedback"), list) else [],
        "classroom_return": str(brief.get("classroom_return") or ""),
    }


def source_has_segment_brief(activity_spec: dict[str, Any] | None) -> bool:
    return bool(isinstance(activity_spec, dict) and activity_spec.get("source_segment_id"))
