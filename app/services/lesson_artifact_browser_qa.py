from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.services.template_quality_production_line import final_delivery_status


def build_lesson_artifact_browser_qa_report(
    *,
    artifact_dir: Path,
    viewport_reports: list[dict[str, Any]],
    screenshot_paths: list[Path],
    console_errors: list[str] | None = None,
) -> dict[str, Any]:
    console_errors = console_errors or []
    student_path = artifact_dir / "student" / "index.html"
    failures: list[str] = []
    if not student_path.exists():
        failures.append("student_index_missing")
    if not viewport_reports:
        failures.append("missing_viewport_reports")
    for report in viewport_reports:
        name = str(report.get("name") or "viewport")
        if report.get("opened") is not True:
            failures.append(f"{name}:not_opened")
        if report.get("runtime_assets_visible") is not True:
            failures.append(f"{name}:runtime_assets_not_visible")
        if report.get("level_curve_visible") is not True:
            failures.append(f"{name}:level_curve_not_visible")
        if report.get("error_feedback_visible") is not True:
            failures.append(f"{name}:error_feedback_not_visible")
        if report.get("music_truth_judge_active") is not True:
            failures.append(f"{name}:music_truth_judge_not_active")
        if int(report.get("rendered_image_count") or 0) <= 0:
            failures.append(f"{name}:runtime_asset_images_not_rendered")
        if report.get("state_machine_visible") is not True:
            failures.append(f"{name}:state_machine_not_visible")
        if report.get("state_machine_runtime_active") is not True:
            failures.append(f"{name}:state_machine_runtime_not_active")
        if report.get("state_machine_runtime_transitioned") is not True:
            failures.append(f"{name}:state_machine_runtime_not_transitioned")
        if report.get("teacher_control_bridge_visible") is not True:
            failures.append(f"{name}:teacher_control_bridge_missing")
        if report.get("teacher_control_bridge_synced") is not True:
            failures.append(f"{name}:teacher_control_bridge_not_synced")
        if report.get("teacher_control_multicontrol_synced") is not True:
            failures.append(f"{name}:teacher_control_multicontrol_not_synced")
        if report.get("teacher_progress_visible") is not True:
            failures.append(f"{name}:teacher_progress_not_visible")
        if report.get("teacher_progress_counts_success_only") is not True:
            failures.append(f"{name}:teacher_progress_counts_failures_as_completed")
        if report.get("reward_path_completed") is not True:
            failures.append(f"{name}:reward_path_not_completed")
        if report.get("play_button_visible") is not True:
            failures.append(f"{name}:play_button_missing")
        if report.get("tap_button_visible") is not True:
            failures.append(f"{name}:tap_button_missing")
        if report.get("reset_button_visible") is not True:
            failures.append(f"{name}:reset_button_missing")
        if report.get("horizontal_overflow") is True:
            failures.append(f"{name}:horizontal_overflow")
    if not screenshot_paths:
        failures.append("missing_screenshot")
    missing_screenshots = [str(path) for path in screenshot_paths if not path.exists()]
    if missing_screenshots:
        failures.append("screenshot_file_missing")
    if console_errors:
        failures.append("console_errors")
    return {
        "version": "lesson_artifact_browser_qa_v1",
        "status": "pass" if not failures else "blocked",
        "opened": bool(viewport_reports) and all(report.get("opened") is True for report in viewport_reports),
        "target": "student/index.html",
        "viewports": {
            str(report.get("name") or f"viewport_{index + 1}"): report
            for index, report in enumerate(viewport_reports)
        },
        "screenshot": str(screenshot_paths[0]) if screenshot_paths else "",
        "screenshots": [str(path) for path in screenshot_paths],
        "console_errors": console_errors,
        "blocking_issues": failures,
    }


def write_lesson_artifact_browser_qa_report(artifact_dir: Path, report: dict[str, Any]) -> Path:
    qa_dir = artifact_dir / "game-production" / "qa"
    qa_dir.mkdir(parents=True, exist_ok=True)
    report_path = qa_dir / "browser-qa-report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    validation_dir = artifact_dir / "validation"
    if validation_dir.exists():
        (validation_dir / "browser-qa-report.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    _update_production_line_checklists(artifact_dir, report)
    return report_path


def _update_production_line_checklists(artifact_dir: Path, browser_report: dict[str, Any]) -> None:
    for path in (
        artifact_dir / "validation" / "production-line-checklist.json",
        artifact_dir / "game-production" / "qa" / "production-line-checklist.json",
        artifact_dir / "game-production" / "scene" / "production-line-checklist.json",
    ):
        if not path.exists():
            continue
        try:
            checklist = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if not isinstance(checklist, dict):
            continue
        updated = _checklist_with_browser_qa_result(checklist, browser_report)
        path.write_text(json.dumps(updated, ensure_ascii=False, indent=2), encoding="utf-8")


def _checklist_with_browser_qa_result(checklist: dict[str, Any], browser_report: dict[str, Any]) -> dict[str, Any]:
    steps = checklist.get("steps") if isinstance(checklist.get("steps"), list) else []
    browser_passed = browser_report.get("status") == "pass"
    for step in steps:
        if not isinstance(step, dict) or step.get("id") != "automatic_qa":
            continue
        if browser_passed:
            step["status"] = "pass"
            step.pop("warning_reason", None)
            step["browser_qa_report_ref"] = "browser-qa-report.json"
        else:
            step["status"] = "blocked"
            step["blocking_issues"] = browser_report.get("blocking_issues", [])
    blocking_steps = [str(step.get("id")) for step in steps if isinstance(step, dict) and step.get("status") == "blocked"]
    warning_steps = [str(step.get("id")) for step in steps if isinstance(step, dict) and step.get("status") == "warning"]
    delivery_status = final_delivery_status(blocking_steps, warning_steps)
    checklist["blocking_steps"] = blocking_steps
    checklist["warning_steps"] = warning_steps
    checklist["status"] = "blocked" if blocking_steps else "ready_with_warnings" if warning_steps else "pass"
    checklist["preview_only"] = delivery_status == "preview_ready_needs_agent_image_gen"
    checklist["final_delivery_status"] = delivery_status
    return checklist
