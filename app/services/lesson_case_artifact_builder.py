from __future__ import annotations

import html
import hashlib
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any
from uuid import uuid4
from urllib.parse import quote

from app.services.agent_internal_image_gen import get_agent_image_gen_executor
from app.services.asset_pack_file_validator import resolve_static_asset_url
from app.services.asset_visual_qa import build_asset_validation_report, build_browser_asset_qa_report
from app.services.image_generation_task_executor import apply_agent_image_gen_outputs, execute_image_generation_tasks
from app.services.template_quality_production_line import build_template_quality_production_line_report


def build_lesson_case_game_artifact(
    *,
    output_dir: Path,
    lesson_case: dict[str, Any],
    selected_segment: dict[str, Any],
    segment_game_brief: dict[str, Any],
    music_game_production_spec: dict[str, Any],
    grounding_result: dict[str, Any],
) -> dict[str, Any]:
    artifact_id = f"lesson_case_{uuid4().hex[:10]}"
    artifact_output_root = _artifact_output_root(output_dir)
    artifact_dir = artifact_output_root / "lesson_case_artifacts" / artifact_id
    student_dir = artifact_dir / "student"
    teacher_dir = artifact_dir / "teacher"
    assets_dir = artifact_dir / "assets"
    config_dir = artifact_dir / "config"
    validation_dir = artifact_dir / "validation"
    production_dir = artifact_dir / "game-production"
    origin_dir = production_dir / "origin"
    design_dir = production_dir / "design"
    music_dir = production_dir / "music"
    scene_dir = production_dir / "scene"
    runtime_dir = production_dir / "runtime"
    qa_dir = production_dir / "qa"
    for directory in (
        student_dir,
        teacher_dir,
        assets_dir,
        config_dir,
        validation_dir,
        origin_dir,
        design_dir,
        music_dir,
        scene_dir,
        runtime_dir,
        qa_dir,
    ):
        directory.mkdir(parents=True, exist_ok=True)

    music_game_production_spec = _ensure_generated_assets(music_game_production_spec)
    music_game_production_spec = _ensure_component_assembly_plan(music_game_production_spec)
    runtime_config = _runtime_config(music_game_production_spec, segment_game_brief)
    runtime_config = _materialize_runtime_assets(
        artifact_dir=artifact_dir,
        production_spec=music_game_production_spec,
        runtime_config=runtime_config,
    )
    music_game_production_spec["runtime_config"] = runtime_config
    teacher_control_config = _teacher_control_config(music_game_production_spec)
    teacher_control_state = {
        "tempo": runtime_config.get("bpm", 88),
        "paused": False,
        "show_hint": True,
        "focus": runtime_config.get("music_material", "第一乐句"),
        "difficulty": runtime_config.get("difficulty_control", "normal"),
        "selected_level": 1,
        "level_count": max(1, int(runtime_config.get("level_count") or 1)),
        "relisten_nonce": 0,
        "completed_rounds": 0,
        "attempts": 0,
    }

    _write_json(config_dir / "lesson-case.json", lesson_case)
    _write_json(config_dir / "selected-segment.json", selected_segment)
    _write_json(config_dir / "segment-game-brief.json", segment_game_brief)
    _write_json(config_dir / "music-game-production-spec.json", music_game_production_spec)
    _write_json(config_dir / "runtime-config.json", runtime_config)
    _write_json(config_dir / "teacher-control-config.json", teacher_control_config)
    _write_json(validation_dir / "lesson-segment-grounding-result.json", grounding_result)
    _write_json(validation_dir / "music-truth-result.json", music_game_production_spec.get("music_truth", {}))
    _write_json(validation_dir / "game-feel-qa-report.json", music_game_production_spec.get("qa_report", {}))
    _write_json(
        validation_dir / "image-generation-execution-report.json",
        music_game_production_spec.get("image_generation_execution_report", {"status": "not_required"}),
    )
    student_html = _student_html(runtime_config)
    asset_validation = build_asset_validation_report(
        asset_contract=music_game_production_spec.get("asset_contract", {}),
        generated_asset_registry=music_game_production_spec.get("generated_asset_registry", {}),
        image_generation_tasks=music_game_production_spec.get("image_generation_tasks", {}),
        runtime_config=runtime_config,
    )
    browser_asset_qa = build_browser_asset_qa_report(
        student_html=student_html,
        runtime_config=runtime_config,
        asset_validation=asset_validation,
    )
    production_line_checklist = build_template_quality_production_line_report(
        lesson_case=lesson_case,
        selected_segment=selected_segment,
        segment_game_brief=segment_game_brief,
        music_game_production_spec=music_game_production_spec,
        runtime_config=runtime_config,
        teacher_control_config=teacher_control_config,
        asset_validation=asset_validation,
        browser_asset_qa=browser_asset_qa,
    )
    _write_json(validation_dir / "asset-validation.json", asset_validation)
    _write_json(validation_dir / "browser-asset-qa.json", browser_asset_qa)
    _write_json(validation_dir / "production-line-checklist.json", production_line_checklist)
    _write_production_files(
        origin_dir=origin_dir,
        design_dir=design_dir,
        music_dir=music_dir,
        scene_dir=scene_dir,
        runtime_dir=runtime_dir,
        qa_dir=qa_dir,
        lesson_case=lesson_case,
        selected_segment=selected_segment,
        segment_game_brief=segment_game_brief,
        music_game_production_spec=music_game_production_spec,
        runtime_config=runtime_config,
        teacher_control_config=teacher_control_config,
        grounding_result=grounding_result,
        asset_validation=asset_validation,
        browser_asset_qa=browser_asset_qa,
        production_line_checklist=production_line_checklist,
    )
    (student_dir / "index.html").write_text(student_html, encoding="utf-8")
    (teacher_dir / "control.html").write_text(_teacher_html(teacher_control_config, teacher_control_state), encoding="utf-8")
    (artifact_dir / "README.md").write_text(_readme(lesson_case, selected_segment, segment_game_brief), encoding="utf-8")

    files = [str(path.relative_to(artifact_dir)) for path in sorted(artifact_dir.rglob("*")) if path.is_file()]
    return {
        "artifact_id": artifact_id,
        "title": f"{lesson_case.get('lesson_title', '教案')} - {segment_game_brief.get('music_learning_target', '音乐游戏')}",
        "file_path": str(artifact_dir),
        "page_url": _output_url_for_path(student_dir / "index.html", artifact_output_root),
        "teacher_url": _output_url_for_path(teacher_dir / "control.html", artifact_output_root),
        "files": files,
        "student_runtime_config": runtime_config,
        "teacher_control_state": teacher_control_state,
        "teacher_control_config": teacher_control_config,
        "asset_validation": asset_validation,
        "browser_asset_qa": browser_asset_qa,
        "production_line_checklist": production_line_checklist,
    }


def _ensure_generated_assets(production_spec: dict[str, Any]) -> dict[str, Any]:
    registry = production_spec.get("generated_asset_registry") if isinstance(production_spec.get("generated_asset_registry"), dict) else {}
    tasks = production_spec.get("image_generation_tasks") if isinstance(production_spec.get("image_generation_tasks"), dict) else {}
    if registry.get("status") != "pending_generation":
        return production_spec
    image_gen_executor = get_agent_image_gen_executor()
    updated_registry, execution_report = execute_image_generation_tasks(
        image_generation_tasks=tasks,
        generated_asset_registry=registry,
        image_gen_executor=image_gen_executor,
        overwrite=bool(image_gen_executor),
    )
    updated = dict(production_spec)
    updated["generated_asset_registry"] = updated_registry
    runtime = dict(updated.get("runtime_config", {})) if isinstance(updated.get("runtime_config"), dict) else {}
    runtime["generated_asset_registry_ref"] = "generated-asset-registry.json"
    runtime["asset_contract_ref"] = "asset-contract.json"
    runtime["image_generation_tasks_ref"] = "image-generation-tasks.json"
    updated["runtime_config"] = runtime
    updated["asset_validation"] = build_asset_validation_report(
        asset_contract=updated.get("asset_contract", {}),
        generated_asset_registry=updated_registry,
        image_generation_tasks=tasks,
        runtime_config=runtime,
    )
    updated["image_generation_execution_report"] = execution_report
    return updated


def _ensure_component_assembly_plan(production_spec: dict[str, Any]) -> dict[str, Any]:
    plan = production_spec.get("component_assembly_plan") if isinstance(production_spec.get("component_assembly_plan"), dict) else {}
    if _component_assembly_plan_ready(plan):
        return production_spec
    reusable = plan.get("reusable_components") if isinstance(plan.get("reusable_components"), list) else []
    if not reusable:
        return production_spec

    updated_plan = dict(plan)
    capability_matches = list(plan.get("capability_matches", [])) if isinstance(plan.get("capability_matches"), list) else []
    runtime_bindings = dict(plan.get("runtime_bindings", {})) if isinstance(plan.get("runtime_bindings"), dict) else {}
    matched_component_ids = {
        str(match.get("registered_component_id") or "")
        for match in capability_matches
        if isinstance(match, dict)
    }
    for item in reusable:
        if not isinstance(item, dict):
            continue
        source_component_id = str(item.get("component_id") or "").strip()
        registered_component_id = _registered_component_id_for_legacy_component(source_component_id)
        if not registered_component_id:
            continue
        if registered_component_id not in matched_component_ids:
            capability_matches.append(
                {
                    "source_component_id": source_component_id,
                    "registered_component_id": registered_component_id,
                    "registered_component": True,
                    "match_source": "artifact_builder_legacy_component_plan_upgrade",
                }
            )
            matched_component_ids.add(registered_component_id)
        runtime_bindings.setdefault(
            registered_component_id,
            _runtime_bindings_for_registered_component(registered_component_id),
        )

    updated_plan["capability_matches"] = capability_matches
    updated_plan["runtime_bindings"] = runtime_bindings
    updated_plan["missing_required_capabilities"] = (
        []
        if not isinstance(plan.get("missing_required_capabilities"), list)
        else [
            item
            for item in plan.get("missing_required_capabilities", [])
            if str(item).strip() and str(item).strip() not in matched_component_ids
        ]
    )
    updated = dict(production_spec)
    updated["component_assembly_plan"] = updated_plan
    return updated


def _component_assembly_plan_ready(plan: dict[str, Any]) -> bool:
    if not isinstance(plan.get("reusable_components"), list) or not plan.get("reusable_components"):
        return False
    matches = plan.get("capability_matches")
    if not isinstance(matches, list) or not matches:
        return False
    if plan.get("missing_required_capabilities"):
        return False
    runtime_bindings = plan.get("runtime_bindings")
    if not isinstance(runtime_bindings, dict) or not runtime_bindings:
        return False
    for match in matches:
        if not isinstance(match, dict):
            return False
        component_id = str(match.get("registered_component_id") or "").strip()
        if not component_id or not match.get("registered_component"):
            return False
        if not runtime_bindings.get(component_id):
            return False
    return True


def _registered_component_id_for_legacy_component(component_id: str) -> str:
    mapping = {
        "audio_unlock_and_playback": "audio_player",
        "beat_timeline_judge": "tap_feedback",
        "teacher_control_protocol": "teacher_control_bar",
        "asset_loader_registry": "game_hud",
        "choice_drag_order_input": "drag_sort_board",
    }
    if component_id in mapping:
        return mapping[component_id]
    known = {
        "audio_player",
        "compare_player",
        "rhythm_card_bank",
        "meter_track",
        "tap_feedback",
        "solfege_card_bank",
        "instrument_card_grid",
        "picture_prompt_cards",
        "form_card_timeline",
        "graphic_score_canvas",
        "rubric_panel",
        "teacher_control_bar",
        "game_hud",
        "drag_sort_board",
    }
    return component_id if component_id in known else ""


def _runtime_bindings_for_registered_component(component_id: str) -> list[str]:
    bindings = {
        "audio_player": ["audio-manifest.json", "music-truth.json"],
        "compare_player": ["audio-manifest.json", "music-truth.json"],
        "rhythm_card_bank": ["game-state-machine.json", "runtime-config.json"],
        "meter_track": ["music_truth.judgement_windows", "runtime-config.json"],
        "tap_feedback": ["music_truth.judgement_windows", "game-state-machine.json"],
        "solfege_card_bank": ["music-truth.json", "runtime-config.json"],
        "instrument_card_grid": ["audio-manifest.json", "music-truth.json"],
        "picture_prompt_cards": ["runtime-config.json", "asset-contract.json"],
        "form_card_timeline": ["audio-manifest.json", "game-state-machine.json"],
        "graphic_score_canvas": ["runtime-config.json", "assessment-record.json"],
        "rubric_panel": ["music-truth.json", "runtime-config.json"],
        "teacher_control_bar": ["teacher-control-config.json", "runtime-config.json"],
        "game_hud": ["runtime-config.json", "level-curve.json"],
        "drag_sort_board": ["game-state-machine.json", "runtime-config.json"],
    }
    return list(bindings.get(component_id, ["runtime-config.json"]))


def revise_lesson_case_game_artifact(artifact: dict[str, Any], revision: dict[str, Any]) -> dict[str, Any]:
    updated = dict(artifact)
    state = dict(updated.get("teacher_control_state", {})) if isinstance(updated.get("teacher_control_state"), dict) else {}
    if "tempo" in revision:
        state["tempo"] = int(revision.get("tempo") or state.get("tempo") or 88)
    if "show_hint" in revision:
        state["show_hint"] = bool(revision.get("show_hint"))
    if "focus" in revision:
        state["focus"] = str(revision.get("focus") or state.get("focus") or "第一乐句")
    if "paused" in revision:
        state["paused"] = bool(revision.get("paused"))
    if "difficulty" in revision:
        state["difficulty"] = str(revision.get("difficulty") or state.get("difficulty") or "normal")
    if "selected_level" in revision:
        state["selected_level"] = max(1, int(revision.get("selected_level") or state.get("selected_level") or 1))
    if "relisten_nonce" in revision:
        state["relisten_nonce"] = max(0, int(revision.get("relisten_nonce") or state.get("relisten_nonce") or 0))
    updated["teacher_control_state"] = state

    artifact_dir = Path(str(updated.get("file_path") or ""))
    if artifact_dir.exists():
        runtime_path = artifact_dir / "config" / "runtime-config.json"
        teacher_path = artifact_dir / "config" / "teacher-control-config.json"
        spec_path = artifact_dir / "config" / "music-game-production-spec.json"
        runtime = _read_json(runtime_path)
        teacher_config = _read_json(teacher_path)
        if "tempo" in state:
            runtime["bpm"] = state["tempo"]
            teacher_config.setdefault("defaults", {})["tempo"] = state["tempo"]
        runtime["show_hint"] = state.get("show_hint", True)
        runtime["focus"] = state.get("focus", "")
        runtime["difficulty_control"] = state.get("difficulty", "normal")
        runtime["selected_level"] = state.get("selected_level", 1)
        runtime["relisten_nonce"] = state.get("relisten_nonce", 0)
        production_spec = _read_json(spec_path)
        if production_spec:
            production_spec["runtime_config"] = runtime
            production_spec["teacher_control_config"] = teacher_config
        student_html = _student_html(runtime)
        asset_validation = build_asset_validation_report(
            asset_contract=runtime.get("asset_contract", {}),
            generated_asset_registry=runtime.get("generated_asset_registry", {}),
            image_generation_tasks=runtime.get("image_generation_tasks", {}),
            runtime_config=runtime,
        )
        browser_asset_qa = build_browser_asset_qa_report(
            student_html=student_html,
            runtime_config=runtime,
            asset_validation=asset_validation,
        )
        production_line_checklist = build_template_quality_production_line_report(
            lesson_case=_read_json(artifact_dir / "config" / "lesson-case.json"),
            selected_segment=_read_json(artifact_dir / "config" / "selected-segment.json"),
            segment_game_brief=_read_json(artifact_dir / "config" / "segment-game-brief.json"),
            music_game_production_spec=production_spec or {
                "runtime_config": runtime,
                "teacher_control_config": teacher_config,
                "asset_contract": runtime.get("asset_contract", {}),
                "generated_asset_registry": runtime.get("generated_asset_registry", {}),
                "image_generation_tasks": runtime.get("image_generation_tasks", {}),
            },
            runtime_config=runtime,
            teacher_control_config=teacher_config,
            asset_validation=asset_validation,
            browser_asset_qa=browser_asset_qa,
        )
        _write_json(runtime_path, runtime)
        _write_json(teacher_path, teacher_config)
        if production_spec:
            production_spec["asset_validation"] = asset_validation
            _write_json(spec_path, production_spec)
        _write_json(artifact_dir / "game-production" / "runtime" / "runtime-config.json", runtime)
        _write_json(artifact_dir / "game-production" / "runtime" / "teacher-control-config.json", teacher_config)
        _write_json(artifact_dir / "validation" / "asset-validation.json", asset_validation)
        _write_json(artifact_dir / "validation" / "browser-asset-qa.json", browser_asset_qa)
        _write_json(artifact_dir / "validation" / "production-line-checklist.json", production_line_checklist)
        _write_json(artifact_dir / "game-production" / "scene" / "asset-validation.json", asset_validation)
        _write_json(artifact_dir / "game-production" / "scene" / "production-line-checklist.json", production_line_checklist)
        _write_json(artifact_dir / "game-production" / "qa" / "browser-asset-qa.json", browser_asset_qa)
        _write_json(artifact_dir / "game-production" / "qa" / "production-line-checklist.json", production_line_checklist)
        _write_json(artifact_dir / "game-production" / "qa" / "browser-qa-report.json", _pending_browser_qa(browser_asset_qa))
        _write_json(artifact_dir / "validation" / "browser-qa-report.json", _pending_browser_qa(browser_asset_qa))
        (artifact_dir / "student" / "index.html").write_text(student_html, encoding="utf-8")
        (artifact_dir / "teacher" / "control.html").write_text(_teacher_html(teacher_config, state), encoding="utf-8")
        updated["student_runtime_config"] = runtime
        updated["teacher_control_config"] = teacher_config
        updated["asset_validation"] = asset_validation
        updated["browser_asset_qa"] = browser_asset_qa
        updated["production_line_checklist"] = production_line_checklist
    return updated


def apply_agent_image_gen_outputs_to_lesson_case_artifact(
    artifact: dict[str, Any],
    outputs: list[dict[str, Any]],
) -> dict[str, Any]:
    updated = dict(artifact)
    artifact_dir = Path(str(updated.get("file_path") or ""))
    if not artifact_dir.exists():
        return updated
    spec_path = artifact_dir / "config" / "music-game-production-spec.json"
    production_spec = _read_json(spec_path)
    if not production_spec:
        return updated
    registry, execution_report = apply_agent_image_gen_outputs(
        image_generation_tasks=production_spec.get("image_generation_tasks", {}),
        generated_asset_registry=production_spec.get("generated_asset_registry", {}),
        outputs=outputs,
    )
    production_spec["generated_asset_registry"] = registry
    production_spec["image_generation_execution_report"] = execution_report
    runtime = _read_json(artifact_dir / "config" / "runtime-config.json")
    runtime["generated_asset_registry"] = registry
    runtime["image_generation_tasks"] = production_spec.get("image_generation_tasks", {})
    runtime["generated_asset_registry_ref"] = "generated-asset-registry.json"
    runtime["image_generation_tasks_ref"] = "image-generation-tasks.json"
    runtime = _materialize_runtime_assets(
        artifact_dir=artifact_dir,
        production_spec=production_spec,
        runtime_config=runtime,
    )
    teacher_config = _read_json(artifact_dir / "config" / "teacher-control-config.json")
    student_html = _student_html(runtime)
    asset_validation = build_asset_validation_report(
        asset_contract=production_spec.get("asset_contract", {}),
        generated_asset_registry=registry,
        image_generation_tasks=production_spec.get("image_generation_tasks", {}),
        runtime_config=runtime,
    )
    browser_asset_qa = build_browser_asset_qa_report(
        student_html=student_html,
        runtime_config=runtime,
        asset_validation=asset_validation,
    )
    production_spec["runtime_config"] = runtime
    production_spec["asset_validation"] = asset_validation
    production_line_checklist = build_template_quality_production_line_report(
        lesson_case=_read_json(artifact_dir / "config" / "lesson-case.json"),
        selected_segment=_read_json(artifact_dir / "config" / "selected-segment.json"),
        segment_game_brief=_read_json(artifact_dir / "config" / "segment-game-brief.json"),
        music_game_production_spec=production_spec,
        runtime_config=runtime,
        teacher_control_config=teacher_config,
        asset_validation=asset_validation,
        browser_asset_qa=browser_asset_qa,
    )
    _write_json(spec_path, production_spec)
    _write_json(artifact_dir / "config" / "runtime-config.json", runtime)
    _write_json(artifact_dir / "game-production" / "runtime" / "runtime-config.json", runtime)
    _write_json(artifact_dir / "game-production" / "scene" / "generated-asset-registry.json", registry)
    _write_json(artifact_dir / "game-production" / "scene" / "image-generation-execution-report.json", execution_report)
    _write_json(artifact_dir / "game-production" / "scene" / "asset-validation.json", asset_validation)
    _write_json(artifact_dir / "game-production" / "scene" / "production-line-checklist.json", production_line_checklist)
    _write_json(artifact_dir / "validation" / "asset-validation.json", asset_validation)
    _write_json(artifact_dir / "validation" / "browser-asset-qa.json", browser_asset_qa)
    _write_json(artifact_dir / "validation" / "production-line-checklist.json", production_line_checklist)
    _write_json(artifact_dir / "game-production" / "qa" / "browser-asset-qa.json", browser_asset_qa)
    _write_json(artifact_dir / "game-production" / "qa" / "production-line-checklist.json", production_line_checklist)
    _write_json(artifact_dir / "game-production" / "qa" / "browser-qa-report.json", _pending_browser_qa(browser_asset_qa))
    _write_json(artifact_dir / "validation" / "browser-qa-report.json", _pending_browser_qa(browser_asset_qa))
    (artifact_dir / "student" / "index.html").write_text(student_html, encoding="utf-8")
    updated["student_runtime_config"] = runtime
    updated["asset_validation"] = asset_validation
    updated["browser_asset_qa"] = browser_asset_qa
    updated["production_line_checklist"] = production_line_checklist
    updated["music_game_production_spec"] = production_spec
    return updated


def _pending_browser_qa(browser_asset_qa: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "pending_browser_screenshot" if browser_asset_qa.get("status") == "ready_for_browser_screenshot" else "blocked",
        "target": "student/index.html",
        "preflight_ref": "browser-asset-qa.json",
        "next_gate": "playwright_screenshot_and_rendered_asset_check",
    }


def _artifact_output_root(output_dir: Path) -> Path:
    resolved_output = output_dir.resolve()
    temp_root = Path(tempfile.gettempdir()).resolve()
    try:
        resolved_output.relative_to(temp_root)
    except ValueError:
        return output_dir
    digest = hashlib.sha1(str(resolved_output).encode("utf-8")).hexdigest()[:12]
    persistent_root = temp_root / "music-agent-runtime-artifacts" / digest
    persistent_root.mkdir(parents=True, exist_ok=True)
    return persistent_root


def _write_production_files(
    *,
    origin_dir: Path,
    design_dir: Path,
    music_dir: Path,
    scene_dir: Path,
    runtime_dir: Path,
    qa_dir: Path,
    lesson_case: dict[str, Any],
    selected_segment: dict[str, Any],
    segment_game_brief: dict[str, Any],
    music_game_production_spec: dict[str, Any],
    runtime_config: dict[str, Any],
    teacher_control_config: dict[str, Any],
    grounding_result: dict[str, Any],
    asset_validation: dict[str, Any],
    browser_asset_qa: dict[str, Any],
    production_line_checklist: dict[str, Any],
) -> None:
    _write_json(origin_dir / "lesson-case.json", lesson_case)
    _write_json(origin_dir / "selected-segment.json", selected_segment)
    _write_json(origin_dir / "segment-game-brief.json", segment_game_brief)

    _write_json(design_dir / "original-game-concept.json", music_game_production_spec.get("original_game_concept", {}))
    _write_json(design_dir / "component-assembly-plan.json", music_game_production_spec.get("component_assembly_plan", {}))
    _write_json(design_dir / "game-design.json", music_game_production_spec.get("game_design", {}))
    _write_json(design_dir / "level-curve.json", music_game_production_spec.get("level_curve", {}))
    _write_json(design_dir / "game-state-machine.json", music_game_production_spec.get("game_state_machine", {}))

    _write_json(music_dir / "music-truth.json", music_game_production_spec.get("music_truth", {}))
    _write_json(music_dir / "audio-manifest.json", music_game_production_spec.get("audio_manifest", {}))

    (scene_dir / "scene-bible.md").write_text(str(music_game_production_spec.get("scene_bible") or ""), encoding="utf-8")
    _write_json(scene_dir / "asset-contract.json", music_game_production_spec.get("asset_contract", {}))
    _write_json(scene_dir / "image-generation-tasks.json", music_game_production_spec.get("image_generation_tasks", {}))
    _write_json(scene_dir / "generated-asset-registry.json", music_game_production_spec.get("generated_asset_registry", {}))
    _write_json(scene_dir / "asset-validation.json", asset_validation)
    _write_json(
        scene_dir / "image-generation-execution-report.json",
        music_game_production_spec.get("image_generation_execution_report", {"status": "not_required"}),
    )
    _write_json(scene_dir / "animation-plan.json", music_game_production_spec.get("animation_plan", {}))
    _write_json(scene_dir / "production-line-checklist.json", production_line_checklist)

    _write_json(runtime_dir / "runtime-config.json", runtime_config)
    _write_json(runtime_dir / "teacher-control-config.json", teacher_control_config)
    _write_json(runtime_dir / "student-entry.json", {"entry": "student/index.html", "runtime_ref": "runtime-config.json"})

    _write_json(qa_dir / "lesson-segment-grounding-result.json", grounding_result)
    _write_json(qa_dir / "original-game-quality-report.json", music_game_production_spec.get("qa_report", {}))
    _write_json(qa_dir / "browser-asset-qa.json", browser_asset_qa)
    _write_json(qa_dir / "production-line-checklist.json", production_line_checklist)
    _write_json(
        qa_dir / "browser-qa-report.json",
        {
            "status": "pending_browser_screenshot" if browser_asset_qa.get("status") == "ready_for_browser_screenshot" else "blocked",
            "target": "student/index.html",
            "preflight_ref": "browser-asset-qa.json",
            "next_gate": "playwright_screenshot_and_rendered_asset_check",
        },
    )


def _runtime_config(production_spec: dict[str, Any], brief: dict[str, Any]) -> dict[str, Any]:
    config = dict(production_spec.get("runtime_config", {})) if isinstance(production_spec.get("runtime_config"), dict) else {}
    preserve = brief.get("must_preserve") if isinstance(brief.get("must_preserve"), dict) else {}
    config.setdefault("template_id", production_spec.get("template_id") or "beat_guardian_core")
    config.setdefault("bpm", 88)
    config.setdefault("meter", "2/4")
    config["source_segment_id"] = brief.get("source_segment_id", "")
    config["source_evidence"] = brief.get("source_evidence", "")
    config["game_goal"] = brief.get("game_goal", "")
    config["music_learning_target"] = brief.get("music_learning_target", "")
    config["student_actions"] = brief.get("student_actions", [])
    config["core_mechanic"] = brief.get("core_mechanic", "")
    config["success_condition"] = brief.get("success_condition", "")
    config["error_feedback"] = brief.get("error_feedback", [])
    config["classroom_return"] = brief.get("classroom_return", "")
    config["music_material"] = preserve.get("music_material") or production_spec.get("music_truth", {}).get("material", "第一乐句")
    config.setdefault("round_count", 1)
    config.setdefault("show_hint", True)
    config["original_game_concept"] = production_spec.get("original_game_concept", {})
    config["component_assembly_plan"] = production_spec.get("component_assembly_plan", {})
    config["level_curve"] = production_spec.get("level_curve", {})
    config["game_state_machine"] = production_spec.get("game_state_machine", {})
    config["asset_contract"] = production_spec.get("asset_contract", {})
    config["generated_asset_registry"] = production_spec.get("generated_asset_registry", {})
    config["image_generation_tasks"] = production_spec.get("image_generation_tasks", {})
    config["lesson_runtime_generated_assets"] = production_spec.get("lesson_runtime_generated_assets", {})
    production_runtime = production_spec.get("runtime_config") if isinstance(production_spec.get("runtime_config"), dict) else {}
    if production_runtime.get("runtime_asset_manifest"):
        config["runtime_asset_manifest"] = production_runtime["runtime_asset_manifest"]
        config["runtime_asset_manifest_ref"] = production_runtime.get("runtime_asset_manifest_ref", "assets/runtime-asset-manifest.json")
    config["animation_plan"] = production_spec.get("animation_plan", {})
    return config


def _materialize_runtime_assets(
    *,
    artifact_dir: Path,
    production_spec: dict[str, Any],
    runtime_config: dict[str, Any],
) -> dict[str, Any]:
    assets_dir = artifact_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    registry = production_spec.get("generated_asset_registry") if isinstance(production_spec.get("generated_asset_registry"), dict) else {}
    reused = _latest_runtime_assets_by_id(registry.get("reused_assets"))
    tasks = production_spec.get("image_generation_tasks") if isinstance(production_spec.get("image_generation_tasks"), dict) else {}
    task_by_asset_id = {
        str(task.get("asset_id") or ""): task
        for task in tasks.get("tasks", [])
        if isinstance(task, dict) and str(task.get("asset_id") or "")
    } if isinstance(tasks.get("tasks"), list) else {}
    lesson_assets = (
        production_spec.get("lesson_runtime_generated_assets")
        if isinstance(production_spec.get("lesson_runtime_generated_assets"), dict)
        else runtime_config.get("lesson_runtime_generated_assets")
        if isinstance(runtime_config.get("lesson_runtime_generated_assets"), dict)
        else {}
    )
    role_by_asset_id = {
        "scene_background": ("scene_background", "scene-background.png"),
        "character_pose_sheet": ("character_pose_sheet", "character-pose-sheet.png"),
        "game_props_sheet": ("game_props_sheet", "game-props-sheet.png"),
        "reward_feedback_sheet": ("reward_feedback_sheet", "reward-feedback-sheet.png"),
    }
    manifest: dict[str, Any] = {"version": "runtime_asset_manifest_v1", "assets": {}}
    runtime_manifest: dict[str, str] = {}
    for item in reused:
        if not isinstance(item, dict):
            continue
        asset_id = str(item.get("asset_id") or "")
        role_file = role_by_asset_id.get(asset_id)
        if not role_file:
            continue
        role, default_file_name = role_file
        task = task_by_asset_id.get(asset_id, {})
        contract = lesson_assets.get(asset_id) if isinstance(lesson_assets, dict) else {}
        contract = contract if isinstance(contract, dict) else {}
        file_name = str(task.get("artifact_file") or contract.get("file") or default_file_name)
        try:
            source_path = resolve_static_asset_url(str(item.get("url") or ""))
        except Exception:
            continue
        if not source_path.exists():
            continue
        target_path = assets_dir / file_name
        if source_path.resolve() != target_path.resolve():
            shutil.copyfile(source_path, target_path)
        relative_file = f"assets/{file_name}"
        runtime_manifest[role] = relative_file
        manifest["assets"][role] = {
            "asset_id": asset_id,
            "type": str(item.get("type") or ""),
            "file": relative_file,
            "source": str(item.get("source") or ""),
            "runtime_usage": str(item.get("runtime_usage") or ""),
            "provider_boundary": "agent_internal_image_gen_only_not_image2_or_chat_ecnu",
        }
    if not manifest["assets"]:
        return runtime_config
    _write_json(assets_dir / "runtime-asset-manifest.json", manifest)
    updated = dict(runtime_config)
    updated["runtime_asset_manifest"] = runtime_manifest
    updated["runtime_asset_manifest_ref"] = "assets/runtime-asset-manifest.json"
    if lesson_assets:
        updated["lesson_runtime_generated_assets"] = lesson_assets
    return updated


def _latest_runtime_assets_by_id(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    priority = {
        "agent_internal_image_gen": 4,
        "local_generated_fallback": 3,
        "cached_generated_asset": 2,
    }
    chosen: dict[str, tuple[int, int, dict[str, Any]]] = {}
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            continue
        asset_id = str(item.get("asset_id") or "").strip()
        if not asset_id:
            continue
        score = priority.get(str(item.get("source") or ""), 1)
        previous = chosen.get(asset_id)
        if not previous or (score, index) >= (previous[0], previous[1]):
            chosen[asset_id] = (score, index, item)
    return [entry[2] for entry in sorted(chosen.values(), key=lambda entry: entry[1])]


def _teacher_control_config(production_spec: dict[str, Any]) -> dict[str, Any]:
    config = dict(production_spec.get("teacher_control_config", {})) if isinstance(production_spec.get("teacher_control_config"), dict) else {}
    controls = list(config.get("editable_controls", [])) if isinstance(config.get("editable_controls"), list) else []
    for control in (
        "start_pause",
        "reset",
        "tempo",
        "relisten_limit",
        "only_practice_selected_segment",
        "hint_visibility",
        "difficulty",
        "level_select",
        "progress_view",
    ):
        if control not in controls:
            controls.append(control)
    config["editable_controls"] = controls
    return config


def _student_html(config: dict[str, Any]) -> str:
    state = json.dumps(config, ensure_ascii=False)
    title = html.escape(str(config.get("music_learning_target") or "雨点强弱拍游戏"))
    goal = html.escape(str(config.get("game_goal") or "听辨强拍"))
    material = html.escape(str(config.get("music_material") or "第一乐句"))
    classroom_return = html.escape(str(config.get("classroom_return") or "回到歌曲，边唱边拍。"))
    assets = _runtime_assets(config)
    background = html.escape(assets.get("background", ""))
    character = html.escape(assets.get("character", ""))
    prop = html.escape(assets.get("prop", ""))
    reward = html.escape(assets.get("reward", ""))
    state_machine = config.get("game_state_machine") if isinstance(config.get("game_state_machine"), dict) else {}
    state_items = [
        {
            "id": html.escape(str(item.get("id") or "")),
            "label": html.escape(str(item.get("label") or item.get("id") or "")),
        }
        for item in state_machine.get("states", [])
        if isinstance(item, dict) and str(item.get("id") or "").strip()
    ][:8]
    state_steps = "".join(f'<li data-state-id="{item["id"]}">{item["label"]}</li>' for item in state_items)
    level_curve = config.get("level_curve") if isinstance(config.get("level_curve"), dict) else {}
    levels = level_curve.get("levels") if isinstance(level_curve.get("levels"), list) else []
    level_items = []
    for index, item in enumerate(levels[:6], start=1):
        if not isinstance(item, dict):
            continue
        focus = html.escape(str(item.get("music_focus") or "音乐任务"))
        task = html.escape(str(item.get("student_task") or item.get("teaching_reason") or "完成本关音乐挑战"))
        material_label = html.escape(str(item.get("music_material") or "课堂音乐材料"))
        hint = html.escape(str(item.get("hint_amount") or ""))
        level_items.append(
            f'<li data-level-index="{index}"><strong>第 {index} 关</strong><span>{focus}</span><small>{material_label} · {hint}</small><em>{task}</em></li>'
        )
    level_steps = "".join(level_items)
    error_feedback = _error_feedback_items(config)
    error_feedback_state = json.dumps(error_feedback, ensure_ascii=False)
    error_feedback_steps = "".join(
        f'<li data-error-type="{html.escape(item["type"])}"><strong>{html.escape(item["type"])}</strong><span>{html.escape(item["message"])}</span></li>'
        for item in error_feedback
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", sans-serif; background: #edf3ea; color: #172721; }}
    main {{ min-height: 100vh; display: grid; align-content: center; gap: 18px; padding: 22px; background-image: linear-gradient(90deg, rgba(237,243,234,.92), rgba(237,243,234,.68)), var(--scene-bg); background-size: cover; background-position: center; }}
    .panel {{ max-width: 920px; margin: 0 auto; width: 100%; background: rgba(255,253,250,.94); border: 1px solid rgba(24,35,31,.14); border-radius: 8px; padding: 22px; box-shadow: 0 16px 36px rgba(30,54,45,.14); }}
    h1 {{ margin: 0 0 8px; font-size: clamp(28px, 7vw, 54px); letter-spacing: 0; }}
    p {{ line-height: 1.65; }}
    .stage {{ display: grid; grid-template-columns: minmax(120px, 180px) 1fr minmax(90px, 140px); gap: 16px; align-items: center; margin: 16px 0; }}
    .asset {{ min-height: 120px; border: 1px solid rgba(23,39,33,.12); border-radius: 8px; background: rgba(255,255,255,.72); display: grid; place-items: center; overflow: hidden; }}
    .asset img {{ max-width: 100%; max-height: 160px; object-fit: contain; display: block; }}
    .beat {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; margin: 18px 0; }}
    .beat div {{ border: 2px solid rgba(23,39,33,.14); border-radius: 8px; padding: 18px; text-align: center; font-weight: 800; font-size: 24px; background: #f7f1d6; }}
    .beat .strong {{ background: #176a5b; color: #fffdfa; }}
    .states {{ display: flex; flex-wrap: wrap; gap: 8px; padding: 0; margin: 12px 0 0; list-style: none; }}
    .states li {{ border-radius: 8px; padding: 8px 10px; background: #e9f2e8; font-weight: 700; }}
    .states li.is-active {{ background: #176a5b; color: #fffdfa; }}
    .runtime-state {{ min-height: 28px; font-weight: 800; color: #176a5b; }}
    .level-curve {{ margin: 14px 0; padding: 12px; border: 1px solid rgba(23,39,33,.14); border-radius: 8px; background: #f8fbf4; }}
    .level-curve ol {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 8px; margin: 8px 0 0; padding: 0; list-style: none; }}
    .level-curve li {{ min-height: 92px; border: 1px solid rgba(23,39,33,.12); border-radius: 8px; padding: 9px; background: #fffdfa; display: grid; gap: 4px; }}
    .level-curve li.is-active {{ outline: 3px solid #176a5b; }}
    .level-curve strong, .level-curve span, .level-curve small, .level-curve em {{ display: block; }}
    .level-curve em {{ font-style: normal; font-size: 13px; line-height: 1.35; }}
    .error-feedback {{ margin: 14px 0; padding: 12px; border: 1px solid rgba(23,39,33,.14); border-radius: 8px; background: #fff8e7; }}
    .error-feedback strong {{ display: block; margin-bottom: 6px; }}
    .error-feedback ul {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 8px; margin: 8px 0 0; padding: 0; list-style: none; }}
    .error-feedback li {{ min-height: 74px; border: 1px solid rgba(93,63,18,.16); border-radius: 8px; padding: 9px; background: #fffdfa; }}
    .error-feedback li.is-active {{ outline: 3px solid #d28b17; }}
    .error-feedback li strong {{ color: #5d3f12; }}
    .error-feedback li span {{ display: block; line-height: 1.45; }}
    .teacher-sync {{ min-height: 28px; font-weight: 800; color: #5d3f12; }}
    button {{ border: 0; border-radius: 8px; background: #172721; color: #fffdfa; padding: 14px 18px; font-size: 18px; font-weight: 800; cursor: pointer; }}
    .row {{ display: flex; gap: 10px; flex-wrap: wrap; }}
    #feedback {{ min-height: 34px; font-weight: 800; color: #176a5b; }}
  </style>
</head>
<body style="--scene-bg: url('{background}')">
<main>
  <section class="panel">
    <h1>{title}</h1>
    <p>{goal}</p>
    <p>音乐材料：{material}</p>
    <div class="level-curve" data-level-curve="true" aria-label="关卡曲线">
      <strong id="current-level-title">第 1 关</strong>
      <p id="current-level-task">先理解游戏规则，只处理最清楚的一次音乐目标。</p>
      <ol>{level_steps}</ol>
    </div>
    <div class="stage" data-runtime-assets="true">
      <div class="asset" aria-label="角色姿势图"><img src="{character}" alt="" /></div>
      <div>
        <div class="beat" aria-label="二拍子强弱">
          <div class="strong">强</div><div>弱</div><div class="strong">强</div><div>弱</div>
        </div>
        <ul class="states" aria-label="游戏状态机">{state_steps}</ul>
        <p id="runtime-state" class="runtime-state" data-runtime-state-machine="true" data-current-state="start">当前状态：开始</p>
      </div>
      <div class="asset" aria-label="游戏道具图"><img src="{prop}" alt="" /></div>
    </div>
    <div class="error-feedback" data-error-feedback="true" data-music-truth-judge="true" aria-label="音乐错误反馈">
      <strong>音乐错误反馈</strong>
      <ul>{error_feedback_steps}</ul>
    </div>
    <div class="row">
      <button id="play" type="button">播放节拍</button>
      <button id="tap" type="button">强拍拍一下</button>
      <button id="reset" type="button">重来</button>
    </div>
    <p id="feedback">先听，再在强拍同步点击。</p>
    <p id="teacher-sync" class="teacher-sync" data-teacher-control-bridge="true">教师控制已连接。</p>
    <div class="asset" aria-label="奖励反馈图" style="max-width:140px;min-height:90px;margin-top:10px;"><img id="reward" src="{reward}" alt="" hidden /></div>
    <p id="return" hidden>{classroom_return}</p>
  </section>
</main>
<script>
window.__LESSON_GAME_RUNTIME__ = {state};
const errorFeedbackItems = {error_feedback_state};
let hits = 0;
let successfulHits = 0;
let beat = 0;
let targetBeatAtMs = 0;
let missingTimer = 0;
let currentGameState = "start";
const stateLabels = Object.fromEntries(Array.from(document.querySelectorAll("[data-state-id]")).map((item) => [item.dataset.stateId, item.textContent || item.dataset.stateId]));
let teacherState = {{ tempo: window.__LESSON_GAME_RUNTIME__.bpm || 88, paused: false, show_hint: window.__LESSON_GAME_RUNTIME__.show_hint !== false, focus: window.__LESSON_GAME_RUNTIME__.focus || window.__LESSON_GAME_RUNTIME__.music_material || "", difficulty: window.__LESSON_GAME_RUNTIME__.difficulty_control || "normal", selected_level: window.__LESSON_GAME_RUNTIME__.selected_level || 1, level_count: window.__LESSON_GAME_RUNTIME__.level_count || 1, relisten_nonce: window.__LESSON_GAME_RUNTIME__.relisten_nonce || 0 }};
let lastRelistenNonce = Number(teacherState.relisten_nonce || 0);
const feedback = document.querySelector("#feedback");
const teacherSync = document.querySelector("#teacher-sync");
const teacherChannelName = "lesson-case-teacher-control";
const studentProgressChannelName = "lesson-case-student-progress";
const teacherChannel = "BroadcastChannel" in window ? new BroadcastChannel(teacherChannelName) : null;
const studentProgressChannel = "BroadcastChannel" in window ? new BroadcastChannel(studentProgressChannelName) : null;
const context = () => new (window.AudioContext || window.webkitAudioContext)();
function setGameState(nextState) {{
  currentGameState = stateLabels[nextState] ? nextState : "start";
  const label = stateLabels[currentGameState] || currentGameState;
  const node = document.querySelector("#runtime-state");
  if (node) {{
    node.dataset.currentState = currentGameState;
    node.textContent = `当前状态：${{label}}`;
  }}
  document.querySelectorAll("[data-state-id]").forEach((item) => item.classList.toggle("is-active", item.dataset.stateId === currentGameState));
  return currentGameState;
}}
window.__LESSON_STATE_MACHINE__ = {{
  states: Object.keys(stateLabels),
  transition_log: [],
  get current_state() {{ return currentGameState; }},
  setState(state) {{
    const next = setGameState(state);
    this.transition_log.push(next);
    return next;
  }}
}};
const musicTruthContract = window.__LESSON_GAME_RUNTIME__.music_truth_contract || {{}};
const judgementWindows = musicTruthContract.judgement_windows || window.__LESSON_GAME_RUNTIME__.judgement_windows || {{}};
function beatIntervalMs() {{
  return Math.max(280, Math.round(60000 / Number(teacherState.tempo || window.__LESSON_GAME_RUNTIME__.bpm || 88)));
}}
function classifyTapTiming(deltaMs) {{
  const goodMs = Number(judgementWindows.good_ms || window.__LESSON_GAME_RUNTIME__.timing_tolerance_ms || 210);
  const lateMs = Number(judgementWindows.late_ms || Math.round(goodMs * 1.5));
  if (deltaMs < -goodMs) return "early";
  if (deltaMs > lateMs) return "missing";
  if (deltaMs > goodMs) return "late";
  return "success";
}}
function classifyCurrentTap(nowMs) {{
  if (!targetBeatAtMs) return "missing";
  return classifyTapTiming(Number(nowMs) - targetBeatAtMs);
}}
function scheduleMissingFeedback() {{
  clearTimeout(missingTimer);
  const lateMs = Number(judgementWindows.late_ms || 320);
  missingTimer = setTimeout(() => {{
    if (targetBeatAtMs) {{
      window.__LESSON_STATE_MACHINE__.setState("feedback");
      showErrorFeedback("missing");
      targetBeatAtMs = 0;
      publishStudentProgress();
    }}
  }}, Math.max(0, targetBeatAtMs - performance.now() + lateMs + 40));
}}
window.__LESSON_TIMING_JUDGE__ = {{
  judgement_windows: judgementWindows,
  music_truth_contract: musicTruthContract,
  classifyTapTiming,
  classifyCurrentTap,
  beatIntervalMs,
  get targetBeatAtMs() {{ return targetBeatAtMs; }},
  get successfulHits() {{ return successfulHits; }},
  get attempts() {{ return hits; }}
}};
function showErrorFeedback(type) {{
  const item = errorFeedbackItems.find((entry) => entry.type === type) || errorFeedbackItems[0] || {{ message: "再听一次，回到音乐拍点。" }};
  document.querySelectorAll("[data-error-type]").forEach((node) => node.classList.toggle("is-active", node.dataset.errorType === item.type));
  feedback.textContent = item.message;
}}
function updateLevelCurve() {{
  const levels = window.__LESSON_GAME_RUNTIME__.level_curve?.levels || [];
  const selectedLevel = Math.max(1, Number(window.__LESSON_GAME_RUNTIME__.selected_level || 1));
  const current = levels[selectedLevel - 1] || levels[0] || {{}};
  document.querySelector("#current-level-title").textContent = `第 ${{selectedLevel}} 关：${{current.music_focus || "音乐任务"}}`;
  document.querySelector("#current-level-task").textContent = current.student_task || current.teaching_reason || "完成本关音乐挑战。";
  document.querySelectorAll("[data-level-index]").forEach((item) => item.classList.toggle("is-active", Number(item.dataset.levelIndex) === selectedLevel));
}}
function applyTeacherControl(next) {{
  teacherState = {{ ...teacherState, ...(next || {{}}) }};
  window.__LESSON_GAME_RUNTIME__.bpm = Number(teacherState.tempo || window.__LESSON_GAME_RUNTIME__.bpm || 88);
  window.__LESSON_GAME_RUNTIME__.show_hint = teacherState.show_hint !== false;
  window.__LESSON_GAME_RUNTIME__.focus = teacherState.focus || "";
  window.__LESSON_GAME_RUNTIME__.difficulty_control = teacherState.difficulty || "normal";
  window.__LESSON_GAME_RUNTIME__.selected_level = Number(teacherState.selected_level || 1);
  updateLevelCurve();
  const relistenNonce = Number(teacherState.relisten_nonce || 0);
  const difficultyLabel = teacherState.difficulty === "easy" ? "降低难度" : teacherState.difficulty === "challenge" ? "挑战难度" : "标准难度";
  teacherSync.textContent = `教师控制：${{teacherState.paused ? "暂停" : "进行"}} · 第 ${{window.__LESSON_GAME_RUNTIME__.selected_level}} 关 · ${{difficultyLabel}} · ${{window.__LESSON_GAME_RUNTIME__.bpm}} BPM · ${{window.__LESSON_GAME_RUNTIME__.show_hint ? "提示开" : "提示关"}}`;
  feedback.hidden = window.__LESSON_GAME_RUNTIME__.show_hint === false;
  if (relistenNonce > lastRelistenNonce) {{
    feedback.textContent = "教师发起重听：再听一遍，准备抓住强拍。";
    lastRelistenNonce = relistenNonce;
  }}
}}
function publishStudentProgress() {{
  const payload = {{ completed_rounds: Math.floor(successfulHits / 2), attempts: hits, successful_hits: successfulHits, selected_level: window.__LESSON_GAME_RUNTIME__.selected_level || 1 }};
  try {{ localStorage.setItem(studentProgressChannelName, JSON.stringify(payload)); }} catch (error) {{}}
  if (studentProgressChannel) studentProgressChannel.postMessage(payload);
}}
try {{ applyTeacherControl(JSON.parse(localStorage.getItem(teacherChannelName) || "null")); }} catch (error) {{ applyTeacherControl({{}}); }}
if (teacherChannel) teacherChannel.addEventListener("message", (event) => applyTeacherControl(event.data));
window.addEventListener("storage", (event) => {{
  if (event.key === teacherChannelName) {{
    try {{ applyTeacherControl(JSON.parse(event.newValue || "null")); }} catch (error) {{ applyTeacherControl({{}}); }}
  }}
}});
function tone(freq, duration) {{
  const audio = context();
  const osc = audio.createOscillator();
  const gain = audio.createGain();
  osc.frequency.value = freq;
  gain.gain.value = 0.12;
  osc.connect(gain).connect(audio.destination);
  osc.start();
  setTimeout(() => {{ osc.stop(); audio.close(); }}, duration);
}}
document.querySelector("#play").addEventListener("click", () => {{
  if (teacherState.paused) {{ feedback.textContent = "教师已暂停，等待开始。"; return; }}
  beat = 1;
  window.__LESSON_STATE_MACHINE__.setState("listen");
  targetBeatAtMs = performance.now() + beatIntervalMs();
  scheduleMissingFeedback();
  feedback.textContent = teacherState.focus ? `听${{teacherState.focus}}，准备拍强拍。` : "听第 1 拍更重，准备拍强拍。";
  tone(196, 140);
  setTimeout(() => {{
    if (targetBeatAtMs) window.__LESSON_STATE_MACHINE__.setState("student_action");
    tone(392, 90);
  }}, beatIntervalMs());
}});
document.querySelector("#tap").addEventListener("click", () => {{
  if (teacherState.paused) {{ feedback.textContent = "教师已暂停，等待开始。"; return; }}
  hits += 1;
  clearTimeout(missingTimer);
  window.__LESSON_STATE_MACHINE__.setState("judge");
  const judgement = classifyCurrentTap(performance.now());
  targetBeatAtMs = 0;
  if (judgement === "success") successfulHits += 1;
  if (judgement === "success" && successfulHits >= 2) {{
    window.__LESSON_STATE_MACHINE__.setState("reward");
    feedback.textContent = "完成一轮：回到第一乐句，边唱边拍强拍。";
  }} else if (judgement === "success") {{
    window.__LESSON_STATE_MACHINE__.setState("feedback");
    feedback.textContent = "命中强拍，再听下一小节。";
  }} else {{
    window.__LESSON_STATE_MACHINE__.setState("feedback");
    showErrorFeedback(judgement);
  }}
  if (judgement === "success" && successfulHits >= 2) {{ document.querySelector("#return").hidden = false; document.querySelector("#reward").hidden = false; }}
  publishStudentProgress();
}});
document.querySelector("#reset").addEventListener("click", () => {{
  clearTimeout(missingTimer);
  hits = 0; successfulHits = 0; beat = 0; targetBeatAtMs = 0; feedback.textContent = "先听，再在强拍同步点击。"; document.querySelector("#return").hidden = true; document.querySelector("#reward").hidden = true;
  window.__LESSON_STATE_MACHINE__.setState("start");
  publishStudentProgress();
}});
setGameState("start");
publishStudentProgress();
</script>
</body>
</html>"""


def _error_feedback_items(config: dict[str, Any]) -> list[dict[str, str]]:
    prompts = config.get("music_reason_prompts") if isinstance(config.get("music_reason_prompts"), dict) else {}
    defaults = {
        "early": "early / 抢拍了：你比音乐拍点早了一点，先听到强拍再出手。",
        "late": "late / 晚拍了：你听到强拍后才按，下一次提前准备。",
        "missing": "missing / 漏拍了：第 1 拍过去了，下一小节重新找强拍。",
    }
    items: list[dict[str, str]] = []
    for error_type, default_message in defaults.items():
        raw_message = str(prompts.get(error_type) or default_message).strip()
        message = raw_message if raw_message.startswith(f"{error_type} /") else f"{error_type} / {raw_message}"
        items.append({"type": error_type, "message": message})
    return items


def _runtime_assets(config: dict[str, Any]) -> dict[str, str]:
    manifest = config.get("runtime_asset_manifest") if isinstance(config.get("runtime_asset_manifest"), dict) else {}
    registry = config.get("generated_asset_registry") if isinstance(config.get("generated_asset_registry"), dict) else {}
    reused = registry.get("reused_assets") if isinstance(registry.get("reused_assets"), list) else []
    assets = {
        "background": _student_asset_url(str(manifest.get("scene_background") or "")),
        "character": _student_asset_url(str(manifest.get("character_pose_sheet") or "")),
        "prop": _student_asset_url(str(manifest.get("game_props_sheet") or "")),
        "reward": _student_asset_url(str(manifest.get("reward_feedback_sheet") or "")),
    }
    for item in reused:
        if not isinstance(item, dict):
            continue
        asset_type = str(item.get("type") or "")
        url = str(item.get("url") or "")
        if asset_type == "background" and not assets["background"]:
            assets["background"] = url
        elif asset_type in {"character_pose", "character_pose_sheet"} and not assets["character"]:
            assets["character"] = url
        elif asset_type in {"prop", "prop_sheet"} and not assets["prop"]:
            assets["prop"] = url
        elif asset_type == "reward_feedback" and not assets["reward"]:
            assets["reward"] = url
    return assets


def _student_asset_url(value: str) -> str:
    if value.startswith("assets/"):
        return f"../{value}"
    return value


def _teacher_html(config: dict[str, Any], state: dict[str, Any]) -> str:
    state_json = json.dumps(state, ensure_ascii=False)
    controls = "、".join(str(item) for item in config.get("editable_controls", []))
    level_count = max(1, int(state.get("level_count") or 1))
    selected_level = max(1, int(state.get("selected_level") or 1))
    difficulty = html.escape(str(state.get("difficulty") or "normal"))
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>教师控制端</title>
  <style>
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", sans-serif; background: #f6f7f1; color: #172721; }}
    main {{ max-width: 760px; margin: 0 auto; padding: 24px; }}
    section {{ background: #fffdfa; border: 1px solid rgba(24,35,31,.14); border-radius: 8px; padding: 20px; }}
    button {{ border: 0; border-radius: 8px; background: #172721; color: #fffdfa; padding: 12px 14px; margin: 6px; font-weight: 800; cursor: pointer; }}
    input {{ width: 100%; }}
  </style>
</head>
<body>
<main>
  <section>
    <h1>教师控制端</h1>
    <p>可用控制：{html.escape(controls)}</p>
    <button id="pause" type="button">开始/暂停</button>
    <button id="reset" type="button">重置</button>
    <button id="relisten" type="button">重听</button>
    <button id="hint" type="button">显示/隐藏提示</button>
    <label>速度 <input id="tempo" type="range" min="60" max="120" value="{int(state.get('tempo', 88))}" /></label>
    <label>关卡 <input id="level" type="number" min="1" max="{level_count}" value="{selected_level}" /></label>
    <label>难度
      <select id="difficulty">
        <option value="easy" {"selected" if difficulty == "easy" else ""}>降低难度</option>
        <option value="normal" {"selected" if difficulty == "normal" else ""}>标准难度</option>
        <option value="challenge" {"selected" if difficulty == "challenge" else ""}>挑战难度</option>
      </select>
    </label>
    <p id="status"></p>
    <p id="progress" data-teacher-progress="true">完成情况：等待学生操作。</p>
  </section>
</main>
<script>
const state = {state_json};
const defaultState = {{ ...state }};
const status = document.querySelector("#status");
const progress = document.querySelector("#progress");
const teacherChannelName = "lesson-case-teacher-control";
const studentProgressChannelName = "lesson-case-student-progress";
const teacherChannel = "BroadcastChannel" in window ? new BroadcastChannel(teacherChannelName) : null;
const studentProgressChannel = "BroadcastChannel" in window ? new BroadcastChannel(studentProgressChannelName) : null;
function publish() {{
  const payload = {{ ...state, bridge: "teacher_control_v1" }};
  try {{ localStorage.setItem(teacherChannelName, JSON.stringify(payload)); }} catch (error) {{}}
  if (teacherChannel) teacherChannel.postMessage(payload);
}}
function difficultyLabel(value) {{ return value === "easy" ? "降低难度" : value === "challenge" ? "挑战难度" : "标准难度"; }}
function render() {{ status.textContent = `第 ${{state.selected_level || 1}} 关，${{difficultyLabel(state.difficulty)}}，速度 ${{state.tempo}} BPM，提示 ${{state.show_hint ? "显示" : "隐藏"}}，焦点：${{state.focus || "当前环节"}}`; publish(); }}
function renderProgress(next) {{
  const completed = Number(next?.completed_rounds || 0);
  const attempts = Number(next?.attempts || 0);
  const level = Number(next?.selected_level || state.selected_level || 1);
  progress.textContent = `完成情况：第 ${{level}} 关完成 ${{completed}} 轮，学生操作 ${{attempts}} 次。`;
}}
document.querySelector("#pause").addEventListener("click", () => {{ state.paused = !state.paused; render(); }});
document.querySelector("#reset").addEventListener("click", () => {{ state.paused = false; state.tempo = Number(defaultState.tempo || 88); state.show_hint = defaultState.show_hint !== false; state.difficulty = defaultState.difficulty || "normal"; state.selected_level = Number(defaultState.selected_level || 1); document.querySelector("#tempo").value = state.tempo; document.querySelector("#difficulty").value = state.difficulty; document.querySelector("#level").value = state.selected_level; render(); }});
document.querySelector("#relisten").addEventListener("click", () => {{ state.relisten_nonce = Number(state.relisten_nonce || 0) + 1; render(); }});
document.querySelector("#hint").addEventListener("click", () => {{ state.show_hint = !state.show_hint; render(); }});
document.querySelector("#tempo").addEventListener("input", (event) => {{ state.tempo = Number(event.target.value); render(); }});
document.querySelector("#difficulty").addEventListener("change", (event) => {{ state.difficulty = event.target.value; render(); }});
document.querySelector("#level").addEventListener("input", (event) => {{ state.selected_level = Math.max(1, Math.min(Number(state.level_count || {level_count}), Number(event.target.value || 1))); render(); }});
if (studentProgressChannel) studentProgressChannel.addEventListener("message", (event) => renderProgress(event.data));
window.addEventListener("storage", (event) => {{
  if (event.key === studentProgressChannelName) {{
    try {{ renderProgress(JSON.parse(event.newValue || "null")); }} catch (error) {{ renderProgress({{}}); }}
  }}
}});
try {{ renderProgress(JSON.parse(localStorage.getItem(studentProgressChannelName) || "null")); }} catch (error) {{ renderProgress({{}}); }}
render();
</script>
</body>
</html>"""


def _readme(lesson_case: dict[str, Any], selected_segment: dict[str, Any], brief: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"# {lesson_case.get('lesson_title', '教案游戏作品')}",
            "",
            f"- 选中环节：{selected_segment.get('segment_id', '')}",
            f"- 教案依据：{brief.get('source_evidence', '')}",
            f"- 游戏目标：{brief.get('game_goal', '')}",
            f"- 课堂回扣：{brief.get('classroom_return', '')}",
        ]
    )


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _output_url_for_path(path: Path, output_dir: Path) -> str:
    try:
        relative = path.resolve().relative_to(output_dir.resolve()).as_posix()
    except ValueError:
        return ""
    encoded = "/".join(quote(part) for part in relative.split("/"))
    return f"/output/{encoded}"
