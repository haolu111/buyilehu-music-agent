from __future__ import annotations

from pathlib import Path
from typing import Any

from app.services.asset_pack_file_validator import resolve_static_asset_url


def build_asset_validation_report(
    *,
    asset_contract: dict[str, Any],
    generated_asset_registry: dict[str, Any],
    image_generation_tasks: dict[str, Any],
    runtime_config: dict[str, Any],
) -> dict[str, Any]:
    assets = asset_contract.get("assets") if isinstance(asset_contract.get("assets"), list) else []
    reused = generated_asset_registry.get("reused_assets") if isinstance(generated_asset_registry.get("reused_assets"), list) else []
    pending = (
        generated_asset_registry.get("pending_generation_assets")
        if isinstance(generated_asset_registry.get("pending_generation_assets"), list)
        else []
    )
    tasks = image_generation_tasks.get("tasks") if isinstance(image_generation_tasks.get("tasks"), list) else []

    checked_files = [_file_check(item) for item in reused if isinstance(item, dict)]
    task_checks = [_task_check(item) for item in tasks if isinstance(item, dict)]
    runtime_refs = _runtime_refs(runtime_config)
    blocking_issues: list[str] = []
    if not assets:
        blocking_issues.append("asset_contract_has_no_assets")
    if reused and any(check["status"] != "present" for check in checked_files):
        blocking_issues.append("reused_asset_file_missing")
    if pending and len(task_checks) < len(pending):
        blocking_issues.append("pending_assets_without_generation_tasks")
    if task_checks and any(check["status"] != "ready" for check in task_checks):
        blocking_issues.append("image_generation_task_incomplete")
    if not runtime_refs.get("generated_asset_registry_ref"):
        blocking_issues.append("runtime_missing_generated_asset_registry_ref")
    if not runtime_refs.get("asset_contract_ref"):
        blocking_issues.append("runtime_missing_asset_contract_ref")

    ready_asset_count = sum(1 for check in checked_files if check["status"] == "present")
    pending_task_count = sum(1 for check in task_checks if check["status"] == "ready")
    return {
        "version": "asset_validation_v1",
        "status": "blocked" if blocking_issues else "ready",
        "asset_contract_status": asset_contract.get("status", ""),
        "registry_status": generated_asset_registry.get("status", ""),
        "ready_asset_count": ready_asset_count,
        "pending_task_count": pending_task_count,
        "checked_files": checked_files,
        "generation_task_checks": task_checks,
        "runtime_refs": runtime_refs,
        "blocking_issues": blocking_issues,
    }


def build_browser_asset_qa_report(
    *,
    student_html: str,
    runtime_config: dict[str, Any],
    asset_validation: dict[str, Any],
) -> dict[str, Any]:
    checks = [
        {
            "id": "student_page_declares_runtime_assets",
            "status": "pass" if 'data-runtime-assets="true"' in student_html else "fail",
        },
        {
            "id": "student_page_declares_state_machine",
            "status": "pass" if "游戏状态机" in student_html else "fail",
        },
        {
            "id": "student_page_declares_runtime_state_machine",
            "status": "pass"
            if 'data-runtime-state-machine="true"' in student_html
            and "window.__LESSON_STATE_MACHINE__" in student_html
            and "setGameState" in student_html
            else "fail",
        },
        {
            "id": "student_page_declares_level_curve",
            "status": "pass" if 'data-level-curve="true"' in student_html else "fail",
        },
        {
            "id": "student_page_declares_error_feedback",
            "status": "pass"
            if 'data-error-feedback="true"' in student_html
            and "early" in student_html
            and "late" in student_html
            and "missing" in student_html
            else "fail",
        },
        {
            "id": "student_page_declares_music_truth_judge",
            "status": "pass"
            if 'data-music-truth-judge="true"' in student_html
            and "classifyTapTiming" in student_html
            and "music_truth_contract" in student_html
            else "fail",
        },
        {
            "id": "student_page_declares_teacher_control_bridge",
            "status": "pass"
            if 'data-teacher-control-bridge="true"' in student_html and "lesson-case-teacher-control" in student_html
            else "fail",
        },
        {
            "id": "runtime_has_asset_registry",
            "status": "pass" if runtime_config.get("generated_asset_registry_ref") else "fail",
        },
        {
            "id": "asset_validation_ready",
            "status": "pass" if asset_validation.get("status") == "ready" else "fail",
        },
    ]
    failed = [check["id"] for check in checks if check["status"] != "pass"]
    return {
        "version": "browser_asset_qa_v1",
        "status": "blocked" if failed else "ready_for_browser_screenshot",
        "mode": "static_runtime_asset_preflight",
        "checks": checks,
        "blocking_issues": failed,
        "next_gate": "playwright_screenshot_and_rendered_asset_check",
    }


def _file_check(item: dict[str, Any]) -> dict[str, str]:
    url = str(item.get("url") or "")
    try:
        path = resolve_static_asset_url(url)
    except Exception as exc:
        return {
            "asset_id": str(item.get("asset_id") or ""),
            "type": str(item.get("type") or ""),
            "url": url,
            "path": "",
            "status": "invalid_url",
            "reason": f"{type(exc).__name__}: {exc}",
        }
    return {
        "asset_id": str(item.get("asset_id") or ""),
        "type": str(item.get("type") or ""),
        "url": url,
        "path": str(path),
        "status": "present" if path.exists() else "missing",
        "reason": "" if path.exists() else "file_not_found",
    }


def _task_check(item: dict[str, Any]) -> dict[str, str]:
    prompt = str(item.get("prompt") or "")
    output_path = str(item.get("output_path") or "")
    negative_prompt = str(item.get("negative_prompt") or "")
    missing = []
    if not output_path:
        missing.append("output_path")
    if not prompt:
        missing.append("prompt")
    for required in ("无文字", "无logo", "无水印"):
        if required not in prompt and required not in negative_prompt:
            missing.append(required)
    return {
        "asset_id": str(item.get("asset_id") or ""),
        "type": str(item.get("type") or ""),
        "output_path": output_path,
        "status": "ready" if not missing else "incomplete",
        "missing": ",".join(missing),
        "will_write_inside_project": str(Path(output_path).as_posix().startswith("app/static/assets/")),
    }


def _runtime_refs(runtime_config: dict[str, Any]) -> dict[str, str]:
    return {
        "asset_contract_ref": str(runtime_config.get("asset_contract_ref") or ""),
        "generated_asset_registry_ref": str(runtime_config.get("generated_asset_registry_ref") or ""),
        "image_generation_tasks_ref": str(runtime_config.get("image_generation_tasks_ref") or ""),
        "scene_bible_ref": str(runtime_config.get("scene_bible_ref") or ""),
    }
