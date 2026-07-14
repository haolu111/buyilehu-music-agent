#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.lesson_artifact_browser_qa import (
    build_lesson_artifact_browser_qa_report,
    write_lesson_artifact_browser_qa_report,
)


VIEWPORTS = [
    {"name": "desktop_projection", "width": 1366, "height": 900, "is_mobile": False},
    {"name": "mobile_touch", "width": 390, "height": 844, "is_mobile": True},
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run browser QA for a generated lesson-case game artifact.")
    parser.add_argument("artifact_dir", type=Path)
    args = parser.parse_args()
    artifact_dir = args.artifact_dir.resolve()
    qa_dir = artifact_dir / "game-production" / "qa"
    qa_dir.mkdir(parents=True, exist_ok=True)

    viewport_reports = []
    screenshots = []
    console_errors = []
    server = _start_server(artifact_dir)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            for viewport in VIEWPORTS:
                context = browser.new_context(
                    viewport={"width": viewport["width"], "height": viewport["height"]},
                    is_mobile=viewport["is_mobile"],
                )
                page = context.new_page()
                page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
                page.on("pageerror", lambda exc: console_errors.append(str(exc)))
                page.goto(f"{server['origin']}/student/index.html", wait_until="load")
                page.wait_for_timeout(300)
                teacher_synced = False
                teacher_multicontrol_synced = False
                teacher_progress_visible = False
                reward_path_completed = False
                teacher_sync_error = ""
                teacher_page = page.context.new_page()
                teacher_page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
                teacher_page.on("pageerror", lambda exc: console_errors.append(str(exc)))
                try:
                    teacher_page.goto(f"{server['origin']}/teacher/control.html", wait_until="load")
                    teacher_page.locator("#pause").click()
                    page.wait_for_timeout(300)
                    teacher_synced = page.evaluate(
                        """() => {
                          const bridge = document.querySelector('[data-teacher-control-bridge="true"]');
                          const text = bridge?.textContent || '';
                          return text.includes('暂停');
                        }"""
                    )
                    teacher_page.locator("#pause").click()
                    teacher_page.locator("#level").fill("2")
                    teacher_page.locator("#difficulty").select_option("easy")
                    teacher_page.locator("#relisten").click()
                    page.wait_for_timeout(300)
                    teacher_multicontrol_synced = page.evaluate(
                        """() => {
                          const bridge = document.querySelector('[data-teacher-control-bridge="true"]');
                          const text = bridge?.textContent || '';
                          const feedback = document.querySelector('#feedback')?.textContent || '';
                          const levelTitle = document.querySelector('#current-level-title')?.textContent || '';
                          return text.includes('第 2 关') && levelTitle.includes('第 2 关') && text.includes('降低难度') && feedback.includes('重听');
                        }"""
                    )
                    page.locator("#tap").click()
                    page.locator("#tap").click()
                    page.wait_for_timeout(300)
                    teacher_progress_visible = teacher_page.evaluate(
                        """() => {
                          const progress = document.querySelector('[data-teacher-progress="true"]');
                          const text = progress?.textContent || '';
                          return text.includes('完成 0 轮') && text.includes('操作 2 次');
                        }"""
                    )
                    page.locator("#reset").click()
                    for _ in range(2):
                        page.locator("#play").click()
                        beat_wait_ms = int(page.evaluate("() => window.__LESSON_TIMING_JUDGE__?.beatIntervalMs?.() || 680"))
                        page.wait_for_function(
                            "() => Number(window.__LESSON_TIMING_JUDGE__?.targetBeatAtMs || 0) > performance.now()",
                            timeout=max(800, beat_wait_ms),
                        )
                        wait_ms = page.evaluate(
                            "() => Math.max(0, Math.round(Number(window.__LESSON_TIMING_JUDGE__?.targetBeatAtMs || 0) - performance.now()))"
                        )
                        page.wait_for_timeout(max(0, int(wait_ms) - 12))
                        page.evaluate("() => document.querySelector('#tap')?.click()")
                        page.wait_for_timeout(120)
                    reward_path_completed = page.evaluate(
                        """() => {
                          const reward = document.querySelector('#reward');
                          const classroomReturn = document.querySelector('#return');
                          const state = window.__LESSON_STATE_MACHINE__?.current_state || '';
                          return !!reward && reward.hidden === false
                            && !!classroomReturn && classroomReturn.hidden === false
                            && state === 'reward';
                        }"""
                    )
                except Exception as exc:  # noqa: BLE001
                    teacher_sync_error = f"{type(exc).__name__}: {exc}"
                    teacher_multicontrol_synced = False
                    teacher_progress_visible = False
                    reward_path_completed = False
                finally:
                    teacher_page.close()
                report = page.evaluate(
                    """(args) => {
                      const { name, teacherSynced, teacherMultiControlSynced, teacherProgressVisible, teacherSyncError } = args;
                      const assetStage = document.querySelector('[data-runtime-assets="true"]');
                      const levelCurve = document.querySelector('[data-level-curve="true"]');
                      const errorFeedback = document.querySelector('[data-error-feedback="true"]');
                      const truthJudge = window.__LESSON_TIMING_JUDGE__;
                      const musicTruthJudgeActive = !!truthJudge
                        && typeof truthJudge.classifyTapTiming === 'function'
                        && truthJudge.classifyTapTiming(-500) === 'early'
                        && truthJudge.classifyTapTiming(260) === 'late'
                        && truthJudge.classifyTapTiming(500) === 'missing';
                      const stateMachine = document.querySelector('[aria-label="游戏状态机"]');
                      const runtimeStateNode = document.querySelector('[data-runtime-state-machine="true"]');
                      const runtimeStateMachine = window.__LESSON_STATE_MACHINE__;
                      const transitionLog = Array.isArray(runtimeStateMachine?.transition_log) ? runtimeStateMachine.transition_log : [];
                      const stateMachineRuntimeTransitioned = transitionLog.includes('judge') && transitionLog.includes('feedback');
                      const previousState = runtimeStateMachine?.current_state || 'start';
                      const stateMachineRuntimeActive = !!runtimeStateNode
                        && !!runtimeStateMachine
                        && typeof runtimeStateMachine.setState === 'function'
                        && runtimeStateMachine.setState('listen') === 'listen'
                        && runtimeStateNode.dataset.currentState === 'listen';
                      if (stateMachineRuntimeActive) runtimeStateMachine.setState(previousState);
                      const teacherBridge = document.querySelector('[data-teacher-control-bridge="true"]');
                      const buttons = Array.from(document.querySelectorAll('button')).map((button) => button.textContent || '');
                      const images = Array.from(document.querySelectorAll('[data-runtime-assets="true"] img'));
                      return {
                        name,
                        opened: true,
                        title: document.title,
                        h1: document.querySelector('h1')?.textContent || '',
                        runtime_assets_visible: !!assetStage && assetStage.getBoundingClientRect().width > 0,
                        level_curve_visible: !!levelCurve && levelCurve.getBoundingClientRect().width > 0,
                        error_feedback_visible: !!errorFeedback && errorFeedback.getBoundingClientRect().width > 0,
                        music_truth_judge_active: musicTruthJudgeActive,
                        state_machine_visible: !!stateMachine && stateMachine.getBoundingClientRect().width > 0,
                        state_machine_runtime_active: stateMachineRuntimeActive,
                        state_machine_runtime_transitioned: stateMachineRuntimeTransitioned,
                        teacher_control_bridge_visible: !!teacherBridge && teacherBridge.getBoundingClientRect().width > 0,
                        teacher_control_bridge_synced: !!teacherSynced,
                        teacher_control_multicontrol_synced: !!teacherMultiControlSynced,
                        teacher_progress_visible: !!teacherProgressVisible,
                        teacher_progress_counts_success_only: !!teacherProgressVisible,
                        reward_path_completed: !!args.rewardPathCompleted,
                        teacher_control_bridge_error: teacherSyncError,
                        play_button_visible: buttons.some((text) => text.includes('播放')),
                        tap_button_visible: buttons.some((text) => text.includes('拍')),
                        reset_button_visible: buttons.some((text) => text.includes('重')),
                        rendered_image_count: images.filter((img) => img.getBoundingClientRect().width > 0).length,
                        horizontal_overflow: document.documentElement.scrollWidth > window.innerWidth + 2
                      };
                    }""",
                    {
                        "name": viewport["name"],
                        "teacherSynced": teacher_synced,
                        "teacherMultiControlSynced": teacher_multicontrol_synced,
                        "teacherProgressVisible": teacher_progress_visible,
                        "rewardPathCompleted": reward_path_completed,
                        "teacherSyncError": teacher_sync_error,
                    },
                )
                screenshot_path = qa_dir / f"browser-qa-{viewport['name']}.png"
                page.screenshot(path=screenshot_path, full_page=True)
                screenshots.append(screenshot_path)
                viewport_reports.append(report)
                context.close()
        finally:
            browser.close()
            server["shutdown"]()

    report = build_lesson_artifact_browser_qa_report(
        artifact_dir=artifact_dir,
        viewport_reports=viewport_reports,
        screenshot_paths=screenshots,
        console_errors=console_errors,
    )
    report_path = write_lesson_artifact_browser_qa_report(artifact_dir, report)
    print(json.dumps({"status": report["status"], "report_path": str(report_path)}, ensure_ascii=False))
    return 0 if report["status"] == "pass" else 1


def _start_server(artifact_dir: Path) -> dict[str, object]:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            path = unquote(self.path.split("?", 1)[0])
            if path == "/":
                path = "/student/index.html"
            if path.startswith("/static/assets/"):
                file_path = ROOT / "app" / path.lstrip("/")
            else:
                file_path = artifact_dir / path.lstrip("/")
            if not _inside(file_path, artifact_dir) and not _inside(file_path, ROOT / "app" / "static" / "assets"):
                self.send_error(403)
                return
            if not file_path.exists() or not file_path.is_file():
                self.send_error(404)
                return
            content = file_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", _content_type(file_path))
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)

        def log_message(self, _format: str, *_args: object) -> None:
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return {
        "origin": f"http://127.0.0.1:{server.server_port}",
        "shutdown": lambda: (server.shutdown(), server.server_close(), thread.join(timeout=2)),
    }


def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _content_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".html":
        return "text/html; charset=utf-8"
    if suffix == ".js":
        return "text/javascript; charset=utf-8"
    if suffix == ".css":
        return "text/css; charset=utf-8"
    if suffix == ".png":
        return "image/png"
    if suffix == ".svg":
        return "image/svg+xml"
    if suffix in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if suffix == ".json":
        return "application/json; charset=utf-8"
    return "application/octet-stream"


if __name__ == "__main__":
    raise SystemExit(main())
