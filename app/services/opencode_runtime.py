from __future__ import annotations

import json
import os
import shutil
import subprocess
import hashlib
import re
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.services.component_library import component_specs_for_ids
from app.services.env_bootstrap import ensure_env_loaded
from app.services.execution_orchestrator import EXECUTION_AGENTS
from app.services.generation_contracts import (
    AGENT_ROLES,
    ALLOWED_TECH_ROUTE,
    PYTHON_PLUGIN_CONTRACT,
    SAMPLED_AUDIO_REQUIREMENTS,
    STUDENT_PAGE_CONTRACT,
)
from app.services.music_education_knowledge import compact_prompt_context
from app.services.runtime_paths import output_url_for_path
from app.services.runtime_paths import runtime_root

_MODEL_CACHE_LOCK = threading.Lock()
_MODEL_CACHE: dict[str, list[str]] = {}


def _generation_mode_for_spec(spec: dict[str, Any]) -> str:
    mode = str(spec.get("generation_mode") or spec.get("lesson_generation_policy", {}).get("mode") or "fast").strip().lower()
    return mode if mode in {"fast", "strict"} else "fast"


def _candidate_opencode_paths(command: str) -> list[Path]:
    home = Path.home()
    candidates = [
        home / ".npm-global" / "bin" / command,
        home / ".local" / "bin" / command,
        home / "bin" / command,
    ]
    return [path for path in candidates if path.exists() and path.is_file()]


def _resolve_opencode_executable(command: str) -> str:
    if Path(command).expanduser().exists():
        return str(Path(command).expanduser())
    executable = shutil.which(command)
    if executable:
        return executable
    for candidate in _candidate_opencode_paths(command):
        return str(candidate)
    return ""


def opencode_status() -> dict[str, Any]:
    ensure_env_loaded()
    command = os.getenv("OPENCODE_COMMAND", "opencode")
    executable = _resolve_opencode_executable(command)
    configured_model = os.getenv("OPENCODE_MODEL", "").strip()
    return {
        "enabled": bool(executable),
        "command": command,
        "resolved_path": executable or "",
        "mode": "opencode_cli" if executable else "prepared_task_package",
        "server_url": os.getenv("OPENCODE_SERVER_URL", ""),
        "model": configured_model,
        "allowed_tech_route": ALLOWED_TECH_ROUTE,
    }


def _available_opencode_models(executable: str, run_env: dict[str, str], workspace_dir: Path) -> list[str]:
    cache_key = f"{executable}|{run_env.get('HOME','')}|{run_env.get('XDG_DATA_HOME','')}"
    with _MODEL_CACHE_LOCK:
        cached = _MODEL_CACHE.get(cache_key)
        if cached is not None:
            return cached

    try:
        completed = subprocess.run(
            [executable, "models"],
            cwd=workspace_dir,
            capture_output=True,
            timeout=30,
            check=False,
            env=run_env,
        )
        stdout = _decode_process_output(completed.stdout)
        stderr = _decode_process_output(completed.stderr)
        output = f"{stdout}\n{stderr}"
        models = [
            line.strip()
            for line in output.splitlines()
            if "/" in line and not line.strip().startswith("opencode models")
        ]
    except Exception:
        models = []

    with _MODEL_CACHE_LOCK:
        _MODEL_CACHE[cache_key] = models
    return models


def _select_opencode_model(configured_model: str, executable: str, run_env: dict[str, str], workspace_dir: Path) -> tuple[str, str]:
    configured = str(configured_model or "").strip()
    if not configured:
        return "", ""

    available = _available_opencode_models(executable, run_env, workspace_dir)
    if not available or configured in available:
        return configured, ""

    provider = configured.split("/", 1)[0] if "/" in configured else configured
    provider_matches = [model for model in available if model.startswith(f"{provider}/")]
    preferred_suffixes = ["ecnu-max", "deepseek-v4-pro", "deepseek-v4-flash", "kimi-k2.6", "k2p6", "k2p5", "kimi-k2-thinking"]
    for suffix in preferred_suffixes:
        for model in provider_matches:
            if model.endswith(f"/{suffix}") or model == f"{provider}/{suffix}":
                return model, configured
    if provider_matches:
        return provider_matches[0], configured
    return configured, ""


def build_opencode_task(spec: dict[str, Any]) -> dict[str, Any]:
    activity_type = spec.get("activity_type", "mixed")
    return {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "runtime": opencode_status(),
        "task": {
            "title": spec.get("title", "音乐课堂工具"),
            "activity_type": activity_type,
            "song_name": spec.get("song_name", "自选歌曲"),
            "grade_band": spec.get("grade_band", "小学"),
            "instruction": _instruction_for_activity(activity_type),
        },
        "agents": AGENT_ROLES,
        "execution_agents": EXECUTION_AGENTS,
        "music_education_context": compact_prompt_context(
            f"{spec.get('title', '')} {spec.get('subtitle', '')} {spec.get('song_name', '')}",
            spec,
        ),
        "allowed_tech_route": ALLOWED_TECH_ROUTE,
        "python_plugin_contract": PYTHON_PLUGIN_CONTRACT,
        "expected_outputs": expected_outputs_for_spec(spec),
        "guardrails": [
            "智能体主界面只展示生成控制台和产物卡片，不直接承载聆听编辑、表现闯关或创造拼图页面。",
            "生成的页面是独立产物，可预览、导出、继续修改。",
            "只有聆听产物允许触发 Basic Pitch、MIDI 分析和 MIDI 改写。",
            "表现产物只生成关卡、活动说明、评价规则和互动组件。",
            "创造产物只生成音乐素材、拼图/网格创作规则和交互组件。",
            *STUDENT_PAGE_CONTRACT,
            *SAMPLED_AUDIO_REQUIREMENTS,
        ],
    }


def expected_outputs_for_spec(spec: dict[str, Any]) -> list[dict[str, str]]:
    outputs: list[dict[str, str]] = [
        {
            "kind": "artifact_page",
            "path": "index.html",
            "description": "智能体生成的独立音乐课堂网页产物。",
        },
        {
            "kind": "config",
            "path": "config/tool-spec.json",
            "description": "页面渲染和继续修改所需的结构化规格。",
        },
    ]

    if spec.get("listening", {}).get("enabled"):
        outputs.extend(
            [
                {
                    "kind": "python_plugin",
                    "path": "python/transforms/modal_mapper.py",
                    "description": "调性、调式、同主音大小调互换与音高映射插件。",
                },
                {
                    "kind": "python_plugin",
                    "path": "python/transforms/rhythm_density.py",
                    "description": "节奏密集/舒缓变换插件。",
                },
                {
                    "kind": "python_plugin",
                    "path": "python/transforms/instrument_tempo.py",
                    "description": "BPM 和乐器音色变换插件。",
                },
            ]
        )

    if spec.get("performance", {}).get("enabled"):
        outputs.extend(
            [
                {
                    "kind": "lesson_config",
                    "path": "config/levels.json",
                    "description": "表现性阶梯闯关关卡、通关条件和教师提示。",
                },
                {
                    "kind": "component",
                    "path": "components/LevelController.js",
                    "description": "关卡解锁、完成状态和课堂反馈组件。",
                },
            ]
        )

    if spec.get("creation", {}).get("enabled"):
        outputs.extend(
            [
                {
                    "kind": "creation_config",
                    "path": "config/creation-pieces.json",
                    "description": "音乐拼图素材、调式规则、结构功能和评价建议。",
                },
                {
                    "kind": "component",
                    "path": "components/CreationBoard.js",
                    "description": "拖拽拼图与网格旋律线创作组件。",
                },
            ]
        )

    if spec.get("music_game", {}).get("enabled"):
        outputs.extend(
            [
                {
                    "kind": "game_config",
                    "path": "config/music-game.json",
                    "description": "音乐小游戏规则、角色、玩法、反馈和胜利条件。",
                },
                {
                    "kind": "component",
                    "path": "components/MusicGameRunner.js",
                    "description": "小游戏状态、操作反馈、动画和重新挑战组件。",
                },
            ]
        )
        if isinstance(spec.get("lesson_adaptation"), dict) and spec.get("lesson_adaptation"):
            outputs.append(
                {
                    "kind": "lesson_adaptation",
                    "path": "config/lesson-adaptation.json",
                    "description": "教案适配层输出：锁定本课真正要学什么。",
                }
            )
        if isinstance(spec.get("template_decision"), dict) and spec.get("template_decision"):
            outputs.append(
                {
                    "kind": "template_decision",
                    "path": "config/template-decision.json",
                    "description": "模板机制路由结果：只决定玩法底盘，不决定前端。",
                }
            )
        if isinstance(spec.get("frontend_handoff_contract"), dict) and spec.get("frontend_handoff_contract"):
            outputs.append(
                {
                    "kind": "frontend_handoff",
                    "path": "config/frontend-handoff-contract.json",
                    "description": "前端表现层交接契约：规定 OpenCode 可改与不可改的边界。",
                }
            )
        if isinstance(spec.get("opencode_role_policy"), dict) and spec.get("opencode_role_policy"):
            outputs.append(
                {
                    "kind": "opencode_role_policy",
                    "path": "config/opencode-role-policy.json",
                    "description": "OpenCode 介入边界：常规生成不进实时链路，只做表现层精修、模板工厂或未命中兜底。",
                }
            )
        if isinstance(spec.get("presentation_pack"), dict) and spec.get("presentation_pack"):
            outputs.append(
                {
                    "kind": "frontend_presentation_pack",
                    "path": "config/frontend-presentation-pack.json",
                    "description": "React 学生端可消费的表现层包：皮肤、布局、动效和奖励风格。",
                }
            )
        if isinstance(spec.get("music_game", {}).get("playable_game"), dict):
            outputs.append(
                {
                    "kind": "playable_game_config",
                    "path": "config/playable-music-game.json",
                    "description": "教案小游戏的可执行协议：材料、目标序列、音频事件、检查规则和反馈。",
                }
            )
        if isinstance(spec.get("lesson_game_contract"), dict) and spec.get("lesson_game_contract"):
            outputs.append(
                {
                    "kind": "lesson_game_contract",
                    "path": "config/lesson-game-contract.json",
                    "description": "教案转游戏强契约：无模板、真实音色、QA 修复和禁止模板兜底。",
                }
            )
        if _has_active_song_anchor(spec.get("song_anchor_contract", {})):
            outputs.extend(
                [
                    {
                        "kind": "song_material_config",
                        "path": "config/song-material.json",
                        "description": "从谱面、MIDI 或文字旋律中提取的歌曲片段材料。",
                    },
                    {
                        "kind": "song_anchor_config",
                        "path": "config/song-anchor-contract.json",
                        "description": "要求页面、播放和判定必须贴合当前歌曲片段的约束。",
                    },
                ]
            )

    return outputs


def materialize_opencode_package(spec: dict[str, Any], target_dir: Path, brain_report: dict[str, Any] | None = None) -> dict[str, Any]:
    task = build_opencode_task(spec)
    config_dir = target_dir / "config"
    python_dir = target_dir / "python" / "transforms"
    component_dir = target_dir / "components"
    config_dir.mkdir(parents=True, exist_ok=True)
    python_dir.mkdir(parents=True, exist_ok=True)
    component_dir.mkdir(parents=True, exist_ok=True)

    _write_json(config_dir / "tool-spec.json", spec)
    _write_json(config_dir / "opencode-spec.json", _opencode_execution_spec(spec))
    _write_json(config_dir / "opencode-task.json", task)
    if brain_report:
        _write_json(config_dir / "agent-brain.json", brain_report)

    if spec.get("performance", {}).get("enabled"):
        _write_json(config_dir / "levels.json", spec["performance"].get("levels", []))
        (component_dir / "LevelController.js").write_text(_level_controller_stub(), encoding="utf-8")

    if spec.get("creation", {}).get("enabled"):
        _write_json(config_dir / "creation-pieces.json", spec["creation"].get("pieces", []))
        (component_dir / "CreationBoard.js").write_text(_creation_board_stub(), encoding="utf-8")

    music_logic_contract = _music_logic_contract_for_spec(spec)
    if music_logic_contract:
        _write_json(config_dir / "music-logic-contract.json", music_logic_contract)

    if spec.get("music_game", {}).get("enabled"):
        _write_json(config_dir / "music-game.json", spec.get("music_game", {}))
        if isinstance(spec.get("lesson_adaptation"), dict) and spec.get("lesson_adaptation"):
            _write_json(config_dir / "lesson-adaptation.json", spec.get("lesson_adaptation", {}))
        if isinstance(spec.get("template_decision"), dict) and spec.get("template_decision"):
            _write_json(config_dir / "template-decision.json", spec.get("template_decision", {}))
        if isinstance(spec.get("frontend_handoff_contract"), dict) and spec.get("frontend_handoff_contract"):
            _write_json(config_dir / "frontend-handoff-contract.json", spec.get("frontend_handoff_contract", {}))
        if isinstance(spec.get("opencode_role_policy"), dict) and spec.get("opencode_role_policy"):
            _write_json(config_dir / "opencode-role-policy.json", spec.get("opencode_role_policy", {}))
        if isinstance(spec.get("presentation_pack"), dict) and spec.get("presentation_pack"):
            _write_json(config_dir / "frontend-presentation-pack.json", spec.get("presentation_pack", {}))
        if isinstance(spec.get("lesson_game_contract"), dict) and spec.get("lesson_game_contract"):
            _write_json(config_dir / "lesson-game-contract.json", spec.get("lesson_game_contract", {}))
        if isinstance(spec.get("song_material"), dict) and spec.get("song_material") and _has_active_song_anchor(spec.get("song_anchor_contract", {})):
            _write_json(config_dir / "song-material.json", spec.get("song_material", {}))
        if _has_active_song_anchor(spec.get("song_anchor_contract", {})):
            _write_json(config_dir / "song-anchor-contract.json", spec.get("song_anchor_contract", {}))
        if isinstance(spec.get("music_game", {}).get("playable_game"), dict):
            _write_json(config_dir / "playable-music-game.json", spec.get("music_game", {}).get("playable_game", {}))
        (component_dir / "MusicGameRunner.js").write_text(_music_game_runner_stub(), encoding="utf-8")

    if spec.get("listening", {}).get("enabled"):
        (python_dir / "modal_mapper.py").write_text(_python_plugin_stub("modal_mapper"), encoding="utf-8")
        (python_dir / "rhythm_density.py").write_text(_python_plugin_stub("rhythm_density"), encoding="utf-8")
        (python_dir / "instrument_tempo.py").write_text(_python_plugin_stub("instrument_tempo"), encoding="utf-8")

    _write_json(config_dir / "selected-components.json", _selected_component_specs(spec))

    return {
        "runtime": task["runtime"],
        "task_url": _relative_output_url(target_dir / "config" / "opencode-task.json"),
        "spec_url": _relative_output_url(target_dir / "config" / "tool-spec.json"),
        "opencode_spec_url": _relative_output_url(target_dir / "config" / "opencode-spec.json"),
        "brain_url": _relative_output_url(target_dir / "config" / "agent-brain.json") if brain_report else "",
        "expected_outputs": task["expected_outputs"],
        "agents": task["agents"],
        "execution_agents": task["execution_agents"],
        "guardrails": task["guardrails"],
    }


def write_agent_brain_report(target_dir: Path, brain_report: dict[str, Any]) -> str:
    path = target_dir / "config" / "agent-brain.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    _write_json(path, brain_report)
    return _relative_output_url(path)


def run_opencode_task(
    spec: dict[str, Any],
    target_dir: Path,
    *,
    action: str = "generate",
    revision: str = "",
    brain_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    status = opencode_status()
    run_path = target_dir / "config" / "opencode-run.json"
    if not status["enabled"]:
        result = {
            "enabled": False,
            "executed": False,
            "status": "skipped",
            "reason": "OpenCode is not available.",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        _write_json(run_path, result)
        return result

    index_path = target_dir / "index.html"
    fallback_index = index_path.read_text(encoding="utf-8") if index_path.exists() else ""
    request_path = target_dir / "config" / "opencode-artifact-request.md"
    request_path.write_text(_build_artifact_request(spec, action=action, revision=revision, brain_report=brain_report), encoding="utf-8")
    before_snapshot = _snapshot_artifact_files(target_dir)
    prompt = _build_fast_generate_prompt(spec) if action == "generate" else _build_runtime_prompt(spec, action=action, revision=revision)
    command = [
        status["resolved_path"],
        "run",
        prompt,
        "--format",
        "json",
    ]
    configured_model = str(status.get("model") or "").strip()
    selected_model = configured_model
    model_fallback_from = ""
    run_env = os.environ.copy()
    resolved_dir = str(Path(status["resolved_path"]).resolve().parent) if status["resolved_path"] else ""
    if resolved_dir:
        run_env["PATH"] = f"{resolved_dir}:{run_env.get('PATH', '')}"
    run_env = _prepare_isolated_opencode_env(run_env, target_dir, label=f"artifact-{action}")
    selected_model, model_fallback_from = _select_opencode_model(configured_model, status["resolved_path"], run_env, target_dir)
    if selected_model:
        command.extend(["--model", selected_model])
    attached_files = [
        "config/opencode-spec.json",
        "config/opencode-task.json",
        "config/opencode-artifact-request.md",
    ]
    if _should_read_existing_index(spec, action=action):
        attached_files.append("index.html")
    playable_game = spec.get("music_game", {}).get("playable_game", {}) if isinstance(spec.get("music_game"), dict) else {}
    if _music_logic_contract_for_spec(spec):
        attached_files.append("config/music-logic-contract.json")
    if _has_active_song_anchor(spec.get("song_anchor_contract", {})):
        attached_files.append("config/song-anchor-contract.json")
    if isinstance(playable_game, dict) and playable_game:
        attached_files.append("config/playable-music-game.json")
    if isinstance(spec.get("lesson_game_contract"), dict) and spec.get("lesson_game_contract"):
        attached_files.append("config/lesson-game-contract.json")
    if brain_report and action != "generate":
        attached_files.append("config/agent-brain.json")
    for attached_file in attached_files:
        command.extend(["--file", attached_file])
    command.extend(["--dir", str(target_dir.resolve())])
    if os.getenv("OPENCODE_SKIP_PERMISSIONS", "").lower() in {"1", "true", "yes"}:
        command.append("--dangerously-skip-permissions")

    timeout = float(os.getenv("OPENCODE_ARTIFACT_TIMEOUT", os.getenv("OPENCODE_RUN_TIMEOUT", "300")))
    if action == "generate":
        timeout = max(timeout, float(os.getenv("OPENCODE_GENERATE_MIN_TIMEOUT", "300")))
    started_at = datetime.now(timezone.utc).isoformat()
    try:
        completed = subprocess.run(
            command,
            cwd=target_dir,
            capture_output=True,
            timeout=timeout,
            check=False,
            env=run_env,
        )
        stdout = _decode_process_output(completed.stdout)
        stderr = _decode_process_output(completed.stderr)
        result = {
            "enabled": True,
            "executed": True,
            "status": "completed" if completed.returncode == 0 else "failed",
            "returncode": completed.returncode,
            "started_at": started_at,
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "stdout": stdout[-12000:],
            "stderr": stderr[-4000:],
            "command": _redacted_command(command),
        }
    except subprocess.TimeoutExpired as exc:
        result = {
            "enabled": True,
            "executed": True,
            "status": "timeout",
            "returncode": None,
            "started_at": started_at,
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "stdout": _decode_timeout_output(exc.stdout)[-12000:],
            "stderr": _decode_timeout_output(exc.stderr)[-4000:],
            "command": _redacted_command(command),
        }

    opencode_error_kind = _classify_opencode_runtime_error(result.get("stderr", ""), result.get("stdout", ""))
    if opencode_error_kind:
        result["error_kind"] = opencode_error_kind
    if selected_model:
        result["resolved_model"] = selected_model
    if model_fallback_from and model_fallback_from != selected_model:
        result["requested_model"] = model_fallback_from
        result["model_fallback"] = True

    validation_errors = _validate_artifact_page(target_dir)
    after_snapshot = _snapshot_artifact_files(target_dir)
    changed_files = _changed_artifact_files(before_snapshot, after_snapshot)
    index_changed = "index.html" in changed_files
    visible_changed_files = _visible_artifact_files(changed_files)
    visible_artifact_changed = bool(visible_changed_files)
    produced_required_artifact = index_changed if action == "generate" else visible_artifact_changed
    should_restore_fallback = bool(fallback_index) and (bool(validation_errors) or not produced_required_artifact)
    if should_restore_fallback:
        index_path.write_text(fallback_index, encoding="utf-8")
        result["status"] = f"{result.get('status', 'failed')}_restored"
        result["restored_fallback"] = True
        result["missing_required_artifact"] = not produced_required_artifact
        changed_files = []
        visible_changed_files = []
        visible_artifact_changed = False
        index_changed = False
    else:
        result["restored_fallback"] = False
        result["missing_required_artifact"] = not produced_required_artifact
        if result.get("status") != "completed" and changed_files:
            result["status"] = f"{result.get('status', 'partial')}_with_artifact"

    result["action"] = action
    result["index_changed"] = index_changed
    result["artifact_changed"] = index_changed if action == "generate" else visible_artifact_changed
    result["visible_artifact_changed"] = visible_artifact_changed
    result["changed_files"] = changed_files
    result["visible_changed_files"] = visible_changed_files
    result["validation_errors"] = validation_errors
    result["summary"] = _extract_opencode_reply(result.get("stdout", ""))[-1200:]
    _write_json(run_path, result)
    result["run_url"] = _relative_output_url(run_path)
    return result


def run_opencode_advice(message: str, workspace_dir: Path) -> dict[str, Any]:
    """Ask OpenCode for conversational music-teaching advice without editing files."""

    status = opencode_status()
    if not status["enabled"]:
        return {
            "enabled": False,
            "executed": False,
            "status": "skipped",
            "reason": "OpenCode is not available.",
            "reply": "",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    prompt = _build_advice_prompt(message)
    command = [
        status["resolved_path"],
        "run",
        prompt,
        "--format",
        "json",
        "--dir",
        str(workspace_dir),
    ]
    configured_model = str(status.get("model") or "").strip()
    if configured_model:
        command.extend(["--model", configured_model])
    if os.getenv("OPENCODE_SKIP_PERMISSIONS", "").lower() in {"1", "true", "yes"}:
        command.append("--dangerously-skip-permissions")

    timeout = float(os.getenv("OPENCODE_CHAT_TIMEOUT", os.getenv("OPENCODE_RUN_TIMEOUT", "30")))
    started_at = datetime.now(timezone.utc).isoformat()
    run_env = _prepare_isolated_opencode_env(os.environ.copy(), workspace_dir, label="advice")
    try:
        completed = subprocess.run(
            command,
            cwd=workspace_dir,
            capture_output=True,
            timeout=timeout,
            check=False,
            env=run_env,
        )
        stdout = _decode_process_output(completed.stdout)
        stderr = _decode_process_output(completed.stderr)
        reply = _extract_opencode_reply(stdout)
        return {
            "enabled": True,
            "executed": True,
            "status": "completed" if completed.returncode == 0 and reply else "failed",
            "returncode": completed.returncode,
            "started_at": started_at,
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "reply": reply,
            "stdout": stdout[-4000:],
            "stderr": stderr[-1600:],
            "command": _redacted_command(command),
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "enabled": True,
            "executed": True,
            "status": "timeout",
            "returncode": None,
            "started_at": started_at,
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "reply": _extract_opencode_reply(_decode_timeout_output(exc.stdout)),
            "stdout": _decode_timeout_output(exc.stdout)[-4000:],
            "stderr": _decode_timeout_output(exc.stderr)[-1600:],
            "command": _redacted_command(command),
        }


def run_opencode_presentation_pack_task(
    *,
    presentation_pack: dict[str, Any],
    frontend_handoff_contract: dict[str, Any],
    target_dir: Path,
    revision: str,
    opencode_role_policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Let OpenCode refine only the React presentation pack, never the page."""

    target_dir.mkdir(parents=True, exist_ok=True)
    config_dir = target_dir / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    pack_path = config_dir / "frontend-presentation-pack.json"
    handoff_path = config_dir / "frontend-handoff-contract.json"
    policy_path = config_dir / "opencode-role-policy.json"
    request_path = config_dir / "opencode-presentation-pack-request.md"
    run_path = config_dir / "opencode-presentation-pack-run.json"
    _write_json(pack_path, presentation_pack or {})
    _write_json(handoff_path, frontend_handoff_contract or {})
    if opencode_role_policy:
        _write_json(policy_path, opencode_role_policy)
    request_path.write_text(
        _build_presentation_pack_request(presentation_pack, frontend_handoff_contract, revision),
        encoding="utf-8",
    )

    status = opencode_status()
    if not status["enabled"]:
        result = {
            "enabled": False,
            "executed": False,
            "status": "skipped",
            "reason": "OpenCode is not available.",
            "allowed_files": ["config/frontend-presentation-pack.json", "config/opencode-artifact-summary.md"],
        }
        _write_json(run_path, result)
        return result

    before_snapshot = _snapshot_artifact_files(target_dir)
    prompt = "\n".join(
        [
            "你是不亦乐乎的前端表现层执行智能体。",
            "本次绝对不要生成 index.html，也不要修改任何页面代码。",
            "你只能读取并修改 config/frontend-presentation-pack.json，并可写 config/opencode-artifact-summary.md。",
            "请根据 config/opencode-presentation-pack-request.md 调整皮肤、布局气质、动效、奖励反馈和视觉词汇。",
            "不能改教学目标、玩法类型、音乐答案、学生必须完成的学习动作。",
            "如存在 config/opencode-role-policy.json，以其中的角色边界为最高优先级。",
            "完成后只回复：已完成。",
        ]
    )
    command = [
        status["resolved_path"],
        "run",
        prompt,
        "--format",
        "json",
        "--file",
        "config/frontend-presentation-pack.json",
        "--file",
        "config/frontend-handoff-contract.json",
        "--file",
        "config/opencode-presentation-pack-request.md",
        "--dir",
        str(target_dir.resolve()),
    ]
    if opencode_role_policy:
        command.extend(["--file", "config/opencode-role-policy.json"])
    configured_model = str(status.get("model") or "").strip()
    run_env = os.environ.copy()
    resolved_dir = str(Path(status["resolved_path"]).resolve().parent) if status["resolved_path"] else ""
    if resolved_dir:
        run_env["PATH"] = f"{resolved_dir}:{run_env.get('PATH', '')}"
    run_env = _prepare_isolated_opencode_env(run_env, target_dir, label="presentation-pack")
    selected_model, model_fallback_from = _select_opencode_model(configured_model, status["resolved_path"], run_env, target_dir)
    if selected_model:
        command.extend(["--model", selected_model])
    if os.getenv("OPENCODE_SKIP_PERMISSIONS", "").lower() in {"1", "true", "yes"}:
        command.append("--dangerously-skip-permissions")

    timeout = float(os.getenv("OPENCODE_PRESENTATION_PACK_TIMEOUT", os.getenv("OPENCODE_RUN_TIMEOUT", "180")))
    started_at = datetime.now(timezone.utc).isoformat()
    try:
        completed = subprocess.run(
            command,
            cwd=target_dir,
            capture_output=True,
            timeout=timeout,
            check=False,
            env=run_env,
        )
        stdout = _decode_process_output(completed.stdout)
        stderr = _decode_process_output(completed.stderr)
        result = {
            "enabled": True,
            "executed": True,
            "status": "completed" if completed.returncode == 0 else "failed",
            "returncode": completed.returncode,
            "started_at": started_at,
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "stdout": stdout[-8000:],
            "stderr": stderr[-2400:],
            "command": _redacted_command(command),
        }
    except subprocess.TimeoutExpired as exc:
        result = {
            "enabled": True,
            "executed": True,
            "status": "timeout",
            "returncode": None,
            "started_at": started_at,
            "finished_at": datetime.now(timezone.utc).isoformat(),
            "stdout": _decode_timeout_output(exc.stdout)[-8000:],
            "stderr": _decode_timeout_output(exc.stderr)[-2400:],
            "command": _redacted_command(command),
        }

    after_snapshot = _snapshot_artifact_files(target_dir)
    changed_files = _changed_artifact_files(before_snapshot, after_snapshot)
    unexpected_files = [
        item
        for item in changed_files
        if item not in {"config/frontend-presentation-pack.json", "config/opencode-artifact-summary.md", "config/opencode-presentation-pack-run.json"}
    ]
    validation_errors = _validate_presentation_pack_file(pack_path)
    if unexpected_files or validation_errors:
        result["status"] = "failed_contract"
        result["unexpected_files"] = unexpected_files
        result["validation_errors"] = validation_errors
    result["changed_files"] = changed_files
    result["pack_path"] = str(pack_path)
    result["pack_url"] = _relative_output_url(pack_path)
    result["summary"] = _extract_opencode_reply(result.get("stdout", ""))[-800:]
    if selected_model:
        result["resolved_model"] = selected_model
    if model_fallback_from and model_fallback_from != selected_model:
        result["requested_model"] = model_fallback_from
        result["model_fallback"] = True
    _write_json(run_path, result)
    result["run_url"] = _relative_output_url(run_path)
    return result


def _build_presentation_pack_request(
    presentation_pack: dict[str, Any],
    frontend_handoff_contract: dict[str, Any],
    revision: str,
) -> str:
    return "\n".join(
        [
            "# Frontend Presentation Pack Request",
            "",
            "## 任务",
            "",
            "只改 React 学生端可消费的表现层包，不生成独立网页。",
            "",
            "## 老师的调整要求",
            "",
            revision.strip() or "让学生端游戏更有课堂游戏感，同时保持学习目标不变。",
            "",
            "## 必须锁定",
            "",
            *[f"- {item}" for item in frontend_handoff_contract.get("locked_inputs", []) if isinstance(item, str)],
            *[f"- {item}" for item in frontend_handoff_contract.get("must_not_change", []) if isinstance(item, str)],
            "",
            "## 当前表现层方向",
            "",
            json.dumps(_compact_presentation_pack(presentation_pack), ensure_ascii=False, indent=2),
        ]
    )


def _validate_presentation_pack_file(path: Path) -> list[str]:
    if not path.exists():
        return ["frontend-presentation-pack.json missing"]
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"frontend-presentation-pack.json invalid json: {exc}"]
    errors: list[str] = []
    if payload.get("output_kind") != "react_presentation_pack":
        errors.append("output_kind must remain react_presentation_pack")
    if payload.get("runtime_target") != "react_student_runtime":
        errors.append("runtime_target must remain react_student_runtime")
    frontend_stack = payload.get("frontend_stack", {})
    if not isinstance(frontend_stack, dict):
        errors.append("frontend_stack must be an object")
    elif frontend_stack.get("component_library") != "Radix Themes":
        errors.append("frontend_stack.component_library must remain Radix Themes")
    if not isinstance(payload.get("palette", {}), dict):
        errors.append("palette must be an object")
    return errors


def _prepare_isolated_opencode_env(base_env: dict[str, str], workspace_dir: Path, *, label: str) -> dict[str, str]:
    """Prepare the env for backend OpenCode tasks.

    By default we keep the caller's real HOME/XDG environment. Recent OpenCode
    runs rely on provider config, auth, and session bootstrap state from the
    user's shared runtime; forcing a fresh synthetic HOME/XDG caused
    ``Session not found`` / provider model resolution failures and prevented
    ``index.html`` from being written at all.

    If explicit isolation is still desired for debugging, set
    ``OPENCODE_ISOLATE_RUNTIME=1`` to opt back into the old synthetic-home
    behavior.
    """

    run_env = dict(base_env)
    if os.getenv("OPENCODE_ISOLATE_RUNTIME", "").strip().lower() not in {"1", "true", "yes"}:
        return run_env

    isolated_root = _isolated_opencode_data_home(workspace_dir, label=label)
    synthetic_home = isolated_root / "home"
    synthetic_home.mkdir(parents=True, exist_ok=True)
    # OpenCode's database/logs follow XDG_DATA_HOME/opencode on working runs.
    # Keep auth beside that data directory, while config still lives under HOME/.config/opencode.
    opencode_data_dir = isolated_root / "opencode"
    opencode_config_dir = synthetic_home / ".config" / "opencode"
    opencode_data_dir.mkdir(parents=True, exist_ok=True)
    opencode_config_dir.mkdir(parents=True, exist_ok=True)

    shared_auth = Path.home() / ".local" / "share" / "opencode" / "auth.json"
    isolated_auth = opencode_data_dir / "auth.json"
    if shared_auth.exists() and not isolated_auth.exists():
        shutil.copy2(shared_auth, isolated_auth)

    shared_config_dir = Path.home() / ".config" / "opencode"
    for name in ["config.json", "opencode.json", "opencode.jsonc"]:
        source = shared_config_dir / name
        target = opencode_config_dir / name
        if source.exists() and source.is_file() and not target.exists():
            shutil.copy2(source, target)
    shared_node_modules = shared_config_dir / "node_modules"
    target_node_modules = opencode_config_dir / "node_modules"
    if shared_node_modules.exists() and shared_node_modules.is_dir() and not target_node_modules.exists():
        shutil.copytree(shared_node_modules, target_node_modules, symlinks=True)
    for name in ["package.json", "package-lock.json", ".gitignore"]:
        source = shared_config_dir / name
        target = opencode_config_dir / name
        if source.exists() and source.is_file() and not target.exists():
            shutil.copy2(source, target)

    run_env["XDG_DATA_HOME"] = str(isolated_root)
    run_env["HOME"] = str(synthetic_home)
    return run_env


def _isolated_opencode_data_home(workspace_dir: Path, *, label: str) -> Path:
    workspace_key = hashlib.sha1(
        f"{label}:{workspace_dir.resolve()}:{os.getpid()}:{datetime.now(timezone.utc).isoformat()}".encode("utf-8")
    ).hexdigest()[:12]
    return runtime_root() / "opencode-xdg" / workspace_key


def _classify_opencode_runtime_error(stderr: str, stdout: str) -> str:
    text = f"{stderr or ''}\n{stdout or ''}".lower()
    if "wal_checkpoint" in text or "sqlite" in text or "database migration" in text:
        return "runtime_db_conflict"
    if "model not found" in text or "providermodelnotfounderror" in text:
        return "model_unavailable"
    return ""


def _instruction_for_activity(activity_type: str) -> str:
    instructions = {
        "listening": "生成独立聆听编辑页：上传音频后静默调用 Basic Pitch 转 MIDI，并提供调性、调式、节奏、BPM、音色改编控件。",
        "performance": "生成独立表现关卡页：根据曲目、年级和教学目标生成阶梯式闯关游戏。",
        "creation": "生成独立创造拼图页：根据音乐要素生成拖拽拼图和网格旋律线创作工具。",
        "music_game": "生成独立音乐小游戏页：根据音乐概念、角色、规则和玩法生成可操作的课堂小游戏。",
        "mixed": "生成综合课堂工具产物：包含聆听、表现、创造三个独立活动区，但仍作为产物页面呈现。",
    }
    return instructions.get(activity_type, instructions["mixed"])


def _should_read_existing_index(spec: dict[str, Any], *, action: str) -> bool:
    return action == "revise" or (
        action == "generate"
        and str(spec.get("direct_generation_route") or "") == "template_seed_then_opencode_refine"
    )


def _opencode_execution_spec(spec: dict[str, Any]) -> dict[str, Any]:
    """Keep OpenCode's first-pass context small and centered on the active page."""

    activity_type = str(spec.get("activity_type") or "mixed")
    prompt_contract = _compact_prompt_contract(spec.get("user_prompt_contract", {}), spec)
    music_logic_contract = _music_logic_contract_for_spec(spec)
    brief: dict[str, Any] = {
        "activity_type": activity_type,
        "title": spec.get("title", "音乐课堂工具"),
        "subtitle": spec.get("subtitle", ""),
        "grade_band": spec.get("grade_band", "小学"),
        "song_name": spec.get("song_name", "自选歌曲"),
        "original_user_need": _short_text(spec.get("original_user_need", ""), 700),
        "user_prompt_contract": prompt_contract,
        "blueprint_plan": spec.get("blueprint_plan", {}),
        "generation_strategy": spec.get("generation_strategy", {}),
        "interaction_model": spec.get("interaction_model", {}),
        "scoring": spec.get("scoring", {}),
        "runtime_behaviors": spec.get("runtime_behaviors", {}),
        "visual_theme": spec.get("visual_theme", {}),
        "visual_asset_pack": spec.get("visual_asset_pack", {}),
        "music_logic_contract": music_logic_contract,
        "song_material": _compact_song_material(spec.get("song_material", {})),
        "song_anchor_contract": _compact_song_anchor_contract(spec.get("song_anchor_contract", {})),
        "lesson_game_contract": spec.get("lesson_game_contract", {}) if isinstance(spec.get("lesson_game_contract"), dict) else {},
        "lesson_adaptation": _compact_lesson_adaptation(spec.get("lesson_adaptation", {})),
        "template_decision": _compact_template_decision(spec.get("template_decision", {})),
        "gameplay_blueprint": _compact_gameplay_blueprint(spec.get("gameplay_blueprint", {})),
        "experience_script": _compact_experience_script(spec.get("experience_script", {})),
        "theme_pack": _compact_theme_pack(spec.get("theme_pack", {})),
        "presentation_pack": _compact_presentation_pack(spec.get("presentation_pack", {})),
        "render_spec": _compact_render_spec(spec.get("render_spec", {})),
        "frontend_handoff_contract": _compact_frontend_handoff(spec.get("frontend_handoff_contract", {})),
        "lesson_generation_policy": spec.get("lesson_generation_policy", {}) if isinstance(spec.get("lesson_generation_policy"), dict) else {},
        "student_page_contract": {
            "audience": "students",
            "copy": "short labels, one-sentence task, no long teacher-facing rationale",
            "layout": "large first-screen operation area, no wasted blank space",
            "controls": "touch targets >= 56px; primary cards/drop zones/canvas dominate the page",
            "fun": "game progress, role/mission feeling, badges, motion, immediate feedback",
        },
    }
    if isinstance(spec.get("lesson_context"), dict):
        brief["lesson_context"] = _compact_lesson_context(spec.get("lesson_context", {}))

    if _is_listening_spec(spec):
        brief["listening_contract"] = _listening_runtime_contract()

    for key in [
        "target_stage",
        "target_objective",
        "target_music_element",
        "target_segment_task",
        "assessment_closure",
    ]:
        value = spec.get(key)
        if value:
            brief[key] = value

    active_payload = spec.get(activity_type)
    if isinstance(active_payload, dict):
        brief[activity_type] = _compact_active_payload(activity_type, active_payload)

    if activity_type == "music_game" and isinstance(spec.get("music_game"), dict):
        playable_game = spec["music_game"].get("playable_game")
        if isinstance(playable_game, dict) and playable_game:
            brief["playable_game"] = _compact_playable_game(playable_game)

    return brief


def _music_logic_contract_for_spec(spec: dict[str, Any]) -> dict[str, Any]:
    top_level = spec.get("music_logic_contract", {}) if isinstance(spec.get("music_logic_contract"), dict) else {}
    if top_level:
        return top_level
    music_game = spec.get("music_game", {}) if isinstance(spec.get("music_game"), dict) else {}
    nested = music_game.get("music_logic_contract", {}) if isinstance(music_game.get("music_logic_contract"), dict) else {}
    return nested


def _has_active_song_anchor(contract: Any) -> bool:
    if not isinstance(contract, dict) or not contract:
        return False
    if not bool(contract.get("must_anchor_to_song")):
        return False
    selected_phrase = contract.get("selected_phrase", {})
    return isinstance(selected_phrase, dict) and bool(selected_phrase)


def _short_text(value: Any, limit: int = 500) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "..."


def _short_list(value: Any, limit: int = 8, item_limit: int = 90) -> list[str]:
    if not isinstance(value, list):
        return []
    return [_short_text(item, item_limit) for item in value[:limit] if str(item or "").strip()]


def _compact_prompt_contract(contract: Any, spec: dict[str, Any]) -> dict[str, Any]:
    contract = contract if isinstance(contract, dict) else {}
    return {
        "original_user_need": _short_text(
            contract.get("original_user_need") or spec.get("original_user_need", ""),
            700,
        ),
        "must_include": _short_list(contract.get("must_include", []), 12, 60),
        "must_not_include": _short_list(contract.get("must_not_include", []), 10, 50),
    }


def _compact_lesson_context(lesson_context: dict[str, Any]) -> dict[str, Any]:
    selected_segment = lesson_context.get("selected_game_segment", {})
    if not isinstance(selected_segment, dict):
        selected_segment = {}
    playable = lesson_context.get("playable_game", {})
    if not isinstance(playable, dict):
        playable = {}
    return {
        "song_name": lesson_context.get("song_name", ""),
        "target_stage": lesson_context.get("target_stage", ""),
        "target_objective": _short_text(lesson_context.get("target_objective", ""), 220),
        "target_music_element": lesson_context.get("target_music_element", ""),
        "target_segment_task": _short_text(lesson_context.get("target_segment_task", ""), 220),
        "target_segment_gameable_point": _short_text(lesson_context.get("target_segment_gameable_point", ""), 220),
        "lesson_evidence": _short_text(lesson_context.get("lesson_evidence", ""), 240),
        "student_task": _short_text(lesson_context.get("student_task", ""), 220),
        "assessment_closure": _short_text(lesson_context.get("assessment_closure", ""), 220),
        "selected_game_segment": {
            "stage_label": selected_segment.get("stage_label", ""),
            "task_summary": _short_text(selected_segment.get("task_summary", ""), 180),
            "gameable_point": _short_text(selected_segment.get("gameable_point", ""), 180),
        },
        "recommended_game_name": lesson_context.get("recommended_game_name", ""),
        "recommended_game_type": lesson_context.get("recommended_game_type", ""),
        "recommended_game_actions": _short_list(lesson_context.get("recommended_game_actions", []), 5, 90),
        "recommended_game_rules": _short_list(lesson_context.get("recommended_game_rules", []), 5, 90),
        "playable_game": _compact_playable_game(playable),
        "song_anchor_contract": _compact_song_anchor_contract(lesson_context.get("song_anchor_contract", {})),
        "lesson_adaptation": _compact_lesson_adaptation(lesson_context.get("lesson_adaptation", {})),
    }


def _compact_song_material(song_material: Any) -> dict[str, Any]:
    if not isinstance(song_material, dict):
        return {}
    phrases = []
    for phrase in song_material.get("phrases", [])[:2] if isinstance(song_material.get("phrases"), list) else []:
        if not isinstance(phrase, dict):
            continue
        phrases.append(
            {
                "id": phrase.get("id", ""),
                "label": phrase.get("label", ""),
                "target_sequence": phrase.get("target_sequence", [])[:16],
                "audio_clip_url": phrase.get("audio_clip_url", ""),
                "audio_clip_range": phrase.get("audio_clip_range", {}) if isinstance(phrase.get("audio_clip_range"), dict) else {},
                "playback_tokens": [
                    {
                        "id": item.get("id", ""),
                        "label": item.get("label", ""),
                        "pitch": item.get("pitch", 60),
                        "duration": item.get("duration", 1),
                        "rest": bool(item.get("rest")),
                    }
                    for item in phrase.get("playback_tokens", [])[:12]
                    if isinstance(item, dict)
                ],
                "main_melody": [
                    {
                        "id": item.get("id", ""),
                        "label": item.get("label", ""),
                        "pitch": item.get("pitch", 60),
                        "duration": item.get("duration", 1),
                    }
                    for item in phrase.get("main_melody", [])[:8]
                    if isinstance(item, dict)
                ],
            }
        )
    return {
        "version": song_material.get("version", ""),
        "song_title": song_material.get("song_title", ""),
        "source": _compact_source(song_material.get("source", {})),
        "phrases": phrases,
    }


def _compact_song_anchor_contract(contract: Any) -> dict[str, Any]:
    if not isinstance(contract, dict):
        return {}
    phrase = contract.get("selected_phrase", {}) if isinstance(contract.get("selected_phrase"), dict) else {}
    return {
        "version": contract.get("version", ""),
        "song_title": contract.get("song_title", ""),
        "must_anchor_to_song": bool(contract.get("must_anchor_to_song")),
        "selected_phrase_id": contract.get("selected_phrase_id", ""),
        "selected_phrase": {
            "id": phrase.get("id", ""),
            "label": phrase.get("label", ""),
            "target_sequence": phrase.get("target_sequence", [])[:16],
            "audio_clip_url": phrase.get("audio_clip_url", ""),
            "audio_clip_range": phrase.get("audio_clip_range", {}) if isinstance(phrase.get("audio_clip_range"), dict) else {},
            "playback_tokens": [
                {
                    "id": item.get("id", ""),
                    "label": item.get("label", ""),
                    "pitch": item.get("pitch", 60),
                    "duration": item.get("duration", 1),
                    "rest": bool(item.get("rest")),
                }
                for item in phrase.get("playback_tokens", [])[:12]
                if isinstance(item, dict)
            ],
            "main_melody": [
                {
                    "id": item.get("id", ""),
                    "label": item.get("label", ""),
                    "pitch": item.get("pitch", 60),
                    "duration": item.get("duration", 1),
                }
                for item in phrase.get("main_melody", [])[:8]
                if isinstance(item, dict)
            ],
        },
    }


def _compact_playable_game(playable: dict[str, Any]) -> dict[str, Any]:
    learning_transfer = playable.get("learning_transfer", {}) if isinstance(playable.get("learning_transfer"), dict) else {}
    return {
        "version": playable.get("version", ""),
        "operation_type": playable.get("operation_type", ""),
        "music_goal": playable.get("music_goal", ""),
        "prompt": _short_text(playable.get("prompt", ""), 180),
        "materials": [
            {
                "id": item.get("id", ""),
                "label": item.get("label", ""),
                "music_value": item.get("music_value", ""),
                "pitch": item.get("pitch", 60),
                "duration": item.get("duration", 0.5),
                "audio_clip_url": item.get("audio_clip_url", ""),
                "playback_tokens": [
                    {
                        "id": token.get("id", ""),
                        "label": token.get("label", ""),
                        "pitch": token.get("pitch", 60),
                        "duration": token.get("duration", 0.5),
                    }
                    for token in item.get("playback_tokens", [])[:6]
                    if isinstance(token, dict)
                ],
                "feedback": _short_text(item.get("feedback", ""), 90),
            }
            for item in playable.get("materials", [])[:8]
            if isinstance(item, dict)
        ],
        "target_sequence": playable.get("target_sequence", [])[:16],
        "rounds": playable.get("rounds", [])[:4] if isinstance(playable.get("rounds"), list) else [],
        "feedback": playable.get("feedback", {}),
        "playback": playable.get("playback", {}),
        "required_student_actions": _short_list(playable.get("required_student_actions", []), 5, 90),
        "completion_condition": _short_text(playable.get("completion_condition", ""), 180),
        "student_facing_task": playable.get("student_facing_task", {}) if isinstance(playable.get("student_facing_task"), dict) else {},
        "learning_transfer": {
            "domain": learning_transfer.get("domain", ""),
            "listen_target": _short_text(learning_transfer.get("listen_target", ""), 120),
            "music_evidence": _short_list(learning_transfer.get("music_evidence", []), 4, 120),
            "student_operation": _short_text(learning_transfer.get("student_operation", ""), 120),
            "classroom_transfer": _short_text(learning_transfer.get("classroom_transfer", ""), 120),
            "teacher_check": _short_text(learning_transfer.get("teacher_check", ""), 120),
        },
    }


def _compact_lesson_adaptation(contract: Any) -> dict[str, Any]:
    if not isinstance(contract, dict):
        return {}
    student_learning = contract.get("student_learning_contract", {}) if isinstance(contract.get("student_learning_contract"), dict) else {}
    template_need = contract.get("template_need", {}) if isinstance(contract.get("template_need"), dict) else {}
    return {
        "version": contract.get("version", ""),
        "owner": contract.get("owner", ""),
        "lesson_focus": contract.get("lesson_focus", {}) if isinstance(contract.get("lesson_focus"), dict) else {},
        "student_learning_contract": {
            "operation_type": student_learning.get("operation_type", ""),
            "prompt": _short_text(student_learning.get("prompt", ""), 180),
            "required_student_actions": _short_list(student_learning.get("required_student_actions", []), 6, 90),
            "completion_condition": _short_text(student_learning.get("completion_condition", ""), 180),
        },
        "template_need": {
            "operation_type": template_need.get("operation_type", ""),
            "mechanism_id": template_need.get("mechanism_id", ""),
            "music_focus": template_need.get("music_focus", ""),
        },
    }


def _compact_template_decision(contract: Any) -> dict[str, Any]:
    if not isinstance(contract, dict):
        return {}
    return {
        "version": contract.get("version", ""),
        "owner": contract.get("owner", ""),
        "decision": contract.get("decision", ""),
        "template_id": contract.get("template_id", ""),
        "template_label": contract.get("template_label", ""),
        "match_status": contract.get("match_status", ""),
        "reason": _short_text(contract.get("reason", ""), 180),
    }


def _compact_frontend_handoff(contract: Any) -> dict[str, Any]:
    if not isinstance(contract, dict):
        return {}
    presentation_inputs = contract.get("presentation_inputs", {}) if isinstance(contract.get("presentation_inputs"), dict) else {}
    return {
        "version": contract.get("version", ""),
        "owner": contract.get("owner", ""),
        "recommended_executor": contract.get("recommended_executor", ""),
        "mode": contract.get("mode", ""),
        "output_kind": contract.get("output_kind", ""),
        "assembly_target": contract.get("assembly_target", ""),
        "component_library": contract.get("component_library", ""),
        "forbid_standalone_web_trio": contract.get("forbid_standalone_web_trio", False),
        "responsibility": contract.get("responsibility", ""),
        "allowed_changes": _short_list(contract.get("allowed_changes", []), 8, 40),
        "locked_inputs": _short_list(contract.get("locked_inputs", []), 8, 70),
        "must_not_change": _short_list(contract.get("must_not_change", []), 8, 60),
        "presentation_inputs": {
            "operation_type": presentation_inputs.get("operation_type", ""),
            "player_verb": presentation_inputs.get("player_verb", ""),
            "skin_family": presentation_inputs.get("skin_family", ""),
            "layout_variant": presentation_inputs.get("layout_variant", ""),
            "scene": presentation_inputs.get("scene", {}) if isinstance(presentation_inputs.get("scene"), dict) else {},
        },
    }


def _compact_gameplay_blueprint(contract: Any) -> dict[str, Any]:
    if not isinstance(contract, dict):
        return {}
    return {
        "version": contract.get("version", ""),
        "student_facing_name": contract.get("student_facing_name", ""),
        "player_verb": contract.get("player_verb", ""),
        "operation_type": contract.get("operation_type", ""),
        "music_focus": contract.get("music_focus", ""),
        "prompt": _short_text(contract.get("prompt", ""), 180),
        "win_condition": _short_text(contract.get("win_condition", ""), 180),
        "rounds": contract.get("rounds", [])[:6] if isinstance(contract.get("rounds"), list) else [],
    }


def _compact_experience_script(contract: Any) -> dict[str, Any]:
    if not isinstance(contract, dict):
        return {}
    return {
        "version": contract.get("version", ""),
        "opening_hook": _short_text(contract.get("opening_hook", ""), 180),
        "tutorial": contract.get("tutorial", {}) if isinstance(contract.get("tutorial"), dict) else {},
        "progression": contract.get("progression", [])[:6] if isinstance(contract.get("progression"), list) else [],
        "replay_hook": _short_text(contract.get("replay_hook", ""), 120),
        "closure_prompt": _short_text(contract.get("closure_prompt", ""), 180),
    }


def _compact_presentation_pack(contract: Any) -> dict[str, Any]:
    if not isinstance(contract, dict):
        return {}
    return {
        "version": contract.get("version", ""),
        "runtime_target": contract.get("runtime_target", ""),
        "output_kind": contract.get("output_kind", ""),
        "engine_target": contract.get("engine_target", ""),
        "template_id": contract.get("template_id", ""),
        "frontend_stack": contract.get("frontend_stack", {}) if isinstance(contract.get("frontend_stack"), dict) else {},
        "skin_family": contract.get("skin_family", ""),
        "layout_variant": contract.get("layout_variant", ""),
        "palette": contract.get("palette", {}) if isinstance(contract.get("palette"), dict) else {},
        "scene": contract.get("scene", {}) if isinstance(contract.get("scene"), dict) else {},
        "scene_skin": contract.get("scene_skin", {}) if isinstance(contract.get("scene_skin"), dict) else {},
        "motif": contract.get("motif", ""),
        "hud_density": contract.get("hud_density", ""),
        "hud_layout": contract.get("hud_layout", {}) if isinstance(contract.get("hud_layout"), dict) else {},
        "reward_style": contract.get("reward_style", {}) if isinstance(contract.get("reward_style"), dict) else {},
        "motion_profile": contract.get("motion_profile", {}) if isinstance(contract.get("motion_profile"), dict) else {},
        "animation_profile": contract.get("animation_profile", {}) if isinstance(contract.get("animation_profile"), dict) else {},
        "background_layers": contract.get("background_layers", []) if isinstance(contract.get("background_layers"), list) else [],
        "css_variables": contract.get("css_variables", {}) if isinstance(contract.get("css_variables"), dict) else {},
    }


def _template_id_for_frontend_policy(
    spec: dict[str, Any],
    frontend_handoff_contract: dict[str, Any],
    presentation_pack: dict[str, Any],
) -> str:
    template_decision = spec.get("template_decision", {}) if isinstance(spec.get("template_decision"), dict) else {}
    music_game = spec.get("music_game", {}) if isinstance(spec.get("music_game"), dict) else {}
    return _first_text(
        spec.get("template_id"),
        template_decision.get("template_id"),
        music_game.get("template_id"),
        presentation_pack.get("template_id"),
        frontend_handoff_contract.get("template_id"),
    )


def _forbid_standalone_web_trio(
    spec: dict[str, Any],
    frontend_handoff_contract: dict[str, Any],
    presentation_pack: dict[str, Any],
    template_id: str,
) -> bool:
    if frontend_handoff_contract.get("forbid_standalone_web_trio") is True:
        return True
    if spec.get("forbid_standalone_web_trio") is True:
        return True
    if presentation_pack.get("forbid_standalone_web_trio") is True:
        return True
    return bool(template_id)


def _first_text(*values: Any) -> str:
    for value in values:
        text = str(value or "").strip()
        if text:
            return text
    return ""


def _compact_theme_pack(contract: Any) -> dict[str, Any]:
    if not isinstance(contract, dict):
        return {}
    return {
        "version": contract.get("version", ""),
        "theme_id": contract.get("theme_id", ""),
        "theme_name": contract.get("theme_name", ""),
        "visual_direction": contract.get("visual_direction", ""),
        "skin_family": contract.get("skin_family", ""),
        "layout_variant": contract.get("layout_variant", ""),
        "reward_token": contract.get("reward_token", ""),
        "scene": contract.get("scene", {}) if isinstance(contract.get("scene"), dict) else {},
        "palette": contract.get("palette", {}) if isinstance(contract.get("palette"), dict) else {},
        "avatar": contract.get("avatar", {}) if isinstance(contract.get("avatar"), dict) else {},
    }


def _compact_render_spec(contract: Any) -> dict[str, Any]:
    if not isinstance(contract, dict):
        return {}
    return {
        "version": contract.get("version", ""),
        "artifact_type": contract.get("artifact_type", ""),
        "screen_structure": contract.get("screen_structure", {}) if isinstance(contract.get("screen_structure"), dict) else {},
        "presentation_contract": contract.get("presentation_contract", {}) if isinstance(contract.get("presentation_contract"), dict) else {},
    }


def _compact_source(source: Any) -> dict[str, Any]:
    if not isinstance(source, dict):
        return {}
    return {
        "filename": source.get("filename", ""),
        "kind": source.get("kind", ""),
        "analysis_quality": source.get("analysis_quality", ""),
        "requires_manual_confirmation": source.get("requires_manual_confirmation", False),
        "engine": source.get("engine", ""),
        "combined_material_count": source.get("combined_material_count", ""),
        "source_audio_url": source.get("source_audio_url", ""),
    }


def _compact_active_payload(activity_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    if activity_type != "music_game":
        return payload
    playable = payload.get("playable_game", {}) if isinstance(payload.get("playable_game"), dict) else {}
    return {
        "enabled": payload.get("enabled", True),
        "game_type": payload.get("game_type", payload.get("type", "")),
        "game_name": payload.get("game_name", payload.get("name", "")),
        "music_concept": payload.get("music_concept", ""),
        "goal": _short_text(payload.get("goal", ""), 200),
        "mechanic": _short_text(payload.get("mechanic", ""), 220),
        "rules": _short_list(payload.get("rules", []), 5, 90),
        "student_actions": _short_list(payload.get("student_actions", []), 5, 90),
        "win_condition": _short_text(payload.get("win_condition", ""), 160),
        "target_segment_task": _short_text(payload.get("target_segment_task", ""), 180),
        "target_segment_gameable_point": _short_text(payload.get("target_segment_gameable_point", ""), 180),
        "playable_game": {
            "version": playable.get("version", ""),
            "operation_type": playable.get("operation_type", ""),
            "music_goal": playable.get("music_goal", ""),
            "prompt": _short_text(playable.get("prompt", ""), 180),
            "materials": [
                {
                    "id": item.get("id", ""),
                    "label": item.get("label", ""),
                    "music_value": item.get("music_value", ""),
                    "pitch": item.get("pitch", 60),
                    "duration": item.get("duration", 0.5),
                    "audio_clip_url": item.get("audio_clip_url", ""),
                    "feedback": _short_text(item.get("feedback", ""), 90),
                }
                for item in playable.get("materials", [])[:8]
                if isinstance(item, dict)
            ],
            "target_sequence": playable.get("target_sequence", [])[:16],
            "check_rule": playable.get("check_rule", ""),
            "completion_condition": _short_text(playable.get("completion_condition", ""), 180),
            "feedback": playable.get("feedback", {}),
            "rounds": playable.get("rounds", [])[:4] if isinstance(playable.get("rounds"), list) else [],
        },
        "song_anchor_contract": payload.get("song_anchor_contract", {}),
    }


def _is_listening_spec(spec: dict[str, Any]) -> bool:
    listening = spec.get("listening", {})
    return (
        str(spec.get("activity_type") or "") == "listening"
        or str(spec.get("template_id") or "") in {"Blueprint_Listen", "Template_Listen"}
        or (isinstance(listening, dict) and bool(listening.get("enabled")))
    )


def _listening_runtime_contract() -> dict[str, Any]:
    return {
        "route": "Blueprint_Listen",
        "must_preserve": [
            "audio upload form with name=audio",
            "tonic/mode/tempo/rhythm_density/instrument controls",
            "POST /api/listening/upload to create a listening session and preserve source_audio_url",
            "POST /api/listening/transform to return original-audio DSP previews or MIDI-based transformed_audio",
            "original/transformed compare playback",
            "real sampled SoundFont or rendered transformed_audio playback first",
        ],
        "defaults": {
            "mode": "preserve",
            "rhythm_density": "preserve",
            "tempo_multiplier": 1.0,
            "instrument": "preserve",
        },
        "forbidden": [
            "static explanation page",
            "music game instead of listening editor",
            "front-end-only fake sliders that do not call listening APIs",
            "oscillator-only main playback",
        ],
    }


def _build_runtime_prompt(spec: dict[str, Any], *, action: str = "generate", revision: str = "") -> str:
    activity_type = spec.get("activity_type", "mixed")
    freeform_music_game = activity_type == "music_game" and str(spec.get("artifact_generation_mode") or "") == "freeform"
    frontend_handoff_contract = spec.get("frontend_handoff_contract", {}) if isinstance(spec.get("frontend_handoff_contract"), dict) else {}
    presentation_pack = spec.get("presentation_pack", {}) if isinstance(spec.get("presentation_pack"), dict) else {}
    template_id = _template_id_for_frontend_policy(spec, frontend_handoff_contract, presentation_pack)
    forbid_standalone_web_trio = _forbid_standalone_web_trio(spec, frontend_handoff_contract, presentation_pack, template_id)
    title = spec.get("title", "音乐课堂工具")
    song_name = spec.get("song_name", "自选歌曲")
    grade_band = spec.get("grade_band", "小学")
    action_label = "继续修改已有网页产物" if action == "revise" else "生成新的网页产物"
    read_existing_index = _should_read_existing_index(spec, action=action)
    if forbid_standalone_web_trio:
        edit_instruction = (
            "这是继续修改任务。请只读取 config/frontend-presentation-pack.json、config/frontend-handoff-contract.json 和相关规格，"
            "只更新 React 学生运行时可消费的 Radix 表现层包。"
            if action == "revise"
            else "这是首次生成任务。禁止生成独立 HTML 学生页；请根据规格输出 React 学生运行时可消费的 Radix 表现层包。"
        )
    elif action == "revise":
        edit_instruction = (
            "这是继续修改任务。请读取现有 index.html 和相关本地资源，保留原页面整体结构、视觉风格和已有功能，只对用户要求的部分做最小必要修改。"
            if read_existing_index
            else "这是继续修改任务，但不要读取旧 index.html；请直接根据紧凑规格重新写出完整 index.html，避免被旧兜底页和大文件拖慢。"
        )
    else:
        edit_instruction = (
            "这是首次生成任务。请先读取当前目录里已经生成好的 index.html 母版页，再基于这个活动母版保留活动结构、交互骨架和对应模块，只做贴合需求的增强与改写。"
            if read_existing_index
            else "这是首次生成任务。不要先读取现有 index.html；请直接根据 config/opencode-spec.json、config/opencode-task.json、config/opencode-artifact-request.md、config/music-logic-contract.json 和 config/playable-music-game.json 生成一个完整可玩的课堂音乐游戏页。"
        )
    revision_lines = []
    if revision.strip():
        revision_lines = [
            "用户本次修改要求：",
            revision.strip(),
        ]
    return "\n".join(
        [
            "你是不亦乐乎-音乐游戏生成智能体的 OpenCode 网页产物生成执行层。",
            f"本次任务：{action_label}。",
            "请优先读取随消息附带的 config/opencode-spec.json、config/opencode-artifact-request.md、config/music-logic-contract.json、config/playable-music-game.json、config/frontend-handoff-contract.json。",
            edit_instruction,
            "你需要真正生成或修改页面代码，而不是只做确认。",
            (
                "允许修改范围：只能在当前任务目录内创建或修改 config/frontend-presentation-pack.json、config/opencode-artifact-summary.md。禁止创建或改写 index.html、styles.css、app.js。"
                if forbid_standalone_web_trio
                else "允许修改范围：只能在当前任务目录内创建或修改 index.html、styles.css、app.js、assets/、components/、python/transforms/、config/opencode-artifact-summary.md。"
            ),
            "禁止修改当前目录之外的任何文件；禁止删除 config/opencode-spec.json 和 config/opencode-task.json。",
            (
                "非音高游戏模板必须由 React + Vite + Radix Themes + Lucide React 学生运行时承载；Phaser 只保留为玩法画布，不生成网页三件套。"
                if forbid_standalone_web_trio
                else (
                    "首次生成和继续修改都要保留当前页面里与目标模块一致的母版基础，不要无视现有活动母版从零换成完全不同的页面类型。"
                    if not freeform_music_game
                    else "当前请求没有命中现成游戏模板，必须根据教案、歌曲材料和音乐逻辑契约自由生成，不要再硬套通用母版。"
                )
            ),
            "页面面向音乐教师和学生，界面不要出现 OpenCode、技术路线、代码、模型、API、Basic Pitch 等后台字样。",
            *(
                [
                    "只输出/修改 React presentation pack；学生可见 UI 由现有 Radix 组件壳承载。",
                ]
                if forbid_standalone_web_trio
                else [
                    "优先生成单文件 index.html，把 CSS 和 JS 内联到同一个文件，避免半成品引用缺失资源。",
                    "如果你引用 styles.css 或 app.js，必须在结束前实际创建对应文件，否则不要引用。",
                    "必须保留可直接打开的 index.html。",
                ]
            ),
            "表现模块要尽量生成真实闯关交互：关卡地图、解锁进度、开始/重置、反馈、通关标准，而不是纯文字卡片。",
            "创造模块要尽量生成真实创作交互：拖拽拼图、网格作曲、双声部、音色选择、试听、保存/重置。",
            "音乐小游戏要生成真实玩法：角色或卡牌、可拖拽/点击操作、开始挑战、动画反馈、胜利条件和重新挑战。",
            "学生页必须少字、大模块、不浪费空间：每个规则/任务块最多一两行，主按钮和卡片要适合学生触控，首屏主要面积给可操作区。",
            "不要把教学依据、设计原因、质量检查、目标映射做成学生可见的大段文字；这些只允许短标签、折叠或写入摘要。",
            "趣味性要通过关卡、角色、徽章、进度、动画和音频反馈体现，不能用长说明替代可玩交互。",
            "凡是有试听、播放、模唱或音乐反馈，必须优先引入本地 /runtime-assets/soundfont-player/soundfont-player.js，并使用 Soundfont.instrument + /runtime-assets/midi-js-soundfonts/FluidR3_GM 采样钢琴作为主要音色；外部 CDN/GitHub 只能作为备用，oscillator 只能作为采样加载失败后的降级。",
            (
                "音乐小游戏首屏任务信息必须通过 React/Radix 学生运行时表现层呈现：本关任务、听什么、做什么、怎样过关。"
                if forbid_standalone_web_trio
                else "音乐小游戏首屏必须由 OpenCode 自己写出 `<section data-lesson-panel=\"true\">`，其中必须有“本关任务”，并用一句话说明：听什么、拖什么、怎样过关。"
            ),
            "聆听模块要保留上传音频和音乐要素调节表单，表单仍应能调用现有后端接口。",
            "所有文案使用中文，课堂说明清晰，视觉风格应根据主题变化，不要每次都生成同一种布局。",
            "完成后请写入 config/opencode-artifact-summary.md，简要说明你实际修改了哪些文件和新增了哪些交互。",
            (
                "完成 frontend-presentation-pack.json 和摘要后立即结束，不要继续阅读无关文件，不要继续规划下一步。"
                if forbid_standalone_web_trio
                else "完成 index.html 和摘要后立即结束，不要继续阅读无关文件，不要继续规划下一步。"
            ),
            f"工具标题：{title}",
            f"活动类型：{activity_type}",
            f"曲目：{song_name}",
            f"学段：{grade_band}",
            *revision_lines,
            "最后只输出一段给系统日志看的中文摘要。",
        ]
    )


def _build_fast_generate_prompt(spec: dict[str, Any]) -> str:
    activity_type = spec.get("activity_type", "mixed")
    generation_mode = _generation_mode_for_spec(spec)
    direct_template_seed = str(spec.get("direct_generation_route") or "") == "template_seed_then_opencode_refine"
    direct_template_reference = str(spec.get("direct_generation_route") or "") == "template_reference_then_opencode_generate"
    prompt_contract = spec.get("user_prompt_contract", {}) if isinstance(spec.get("user_prompt_contract"), dict) else {}
    original_need = _short_text(prompt_contract.get("original_user_need") or spec.get("original_user_need") or "", 320)
    target_stage = _short_text(spec.get("target_stage", ""), 80)
    target_music_element = _short_text(spec.get("target_music_element", ""), 80)
    target_objective = _short_text(spec.get("target_objective", ""), 120)
    target_segment_task = _short_text(spec.get("target_segment_task", ""), 100)
    must_include = prompt_contract.get("must_include", []) if isinstance(prompt_contract.get("must_include"), list) else []
    must_not_include = (
        prompt_contract.get("must_not_include", []) if isinstance(prompt_contract.get("must_not_include"), list) else []
    )
    music_logic_contract = _music_logic_contract_for_spec(spec)
    song_anchor_contract = spec.get("song_anchor_contract", {}) if isinstance(spec.get("song_anchor_contract"), dict) else {}
    selected_phrase = song_anchor_contract.get("selected_phrase", {}) if isinstance(song_anchor_contract.get("selected_phrase"), dict) else {}
    has_active_song_anchor = _has_active_song_anchor(song_anchor_contract)
    lesson_game_contract = spec.get("lesson_game_contract", {}) if isinstance(spec.get("lesson_game_contract"), dict) else {}
    frontend_handoff_contract = spec.get("frontend_handoff_contract", {}) if isinstance(spec.get("frontend_handoff_contract"), dict) else {}
    presentation_pack = spec.get("presentation_pack", {}) if isinstance(spec.get("presentation_pack"), dict) else {}
    template_id = _template_id_for_frontend_policy(spec, frontend_handoff_contract, presentation_pack)
    forbid_standalone_web_trio = _forbid_standalone_web_trio(spec, frontend_handoff_contract, presentation_pack, template_id)
    music_tokens = [
        f"{item.get('id', '')}:{item.get('label', '')}"
        for item in music_logic_contract.get("tokens", [])
        if isinstance(item, dict)
    ]
    activity_instruction = {
        "listening": "做成聆听编辑页，必须有上传、对比试听和音乐要素控件。",
        "performance": "做成表现闯关页，必须有开始挑战、关卡状态、反馈、重试和通关。",
        "creation": "做成创作页，必须有可操作创作区、试听、重置和反馈。",
        "music_game": "做成音乐小游戏页，必须有开始、玩家操作、动画反馈、胜利条件和重玩。",
        "mixed": "做成课堂工具页，但首屏只能有一个主操作区。",
    }.get(activity_type, "做成真实可操作的音乐课堂工具页。")
    lesson_contract_instruction = ""
    if lesson_game_contract:
        sound_source_policy = lesson_game_contract.get("sound_source_policy", {}) if isinstance(lesson_game_contract.get("sound_source_policy"), dict) else {}
        uploaded_material_policy = lesson_game_contract.get("uploaded_material_policy", {}) if isinstance(lesson_game_contract.get("uploaded_material_policy"), dict) else {}
        lesson_contract_instruction = "\n".join(
            [
                "教案转游戏强契约：",
                "- 不要使用任何本地模板页或活动母版兜底，必须从零生成当前网页。",
                f"- selected stage: {lesson_game_contract.get('selected_stage', '')}",
                f"- music focus: {lesson_game_contract.get('music_focus', '')}",
                f"- game mechanic: {lesson_game_contract.get('game_mechanic', '')}",
                f"- win condition: {lesson_game_contract.get('win_condition', '')}",
                (
                    f"- 已上传课堂音频：{sound_source_policy.get('source_audio_url', '')}。页面里必须至少有一个学生可见播放入口实际播放这份上传音频或它切出的 audio_clip_url 片段，不能只保留 SoundFont/合成音试听。"
                    if uploaded_material_policy.get("uploaded_audio_must_render")
                    else "- 如果后续补充上传音频，页面播放链路要优先接入真实音频或片段。"
                ),
                "- 谱面材料按需使用：只有当当前任务依赖具体歌曲乐句、片段顺序、读谱或判定材料时，才强制把谱面解析结果落到页面。",
                "- fast 首轮先优先做出可玩的页面骨架和主交互。",
            ]
        )
    frontend_handoff_instruction = ""
    if frontend_handoff_contract:
        frontend_handoff_instruction = "\n".join(
            [
                "前端职责边界：",
                f"- mode: {frontend_handoff_contract.get('mode', '')}",
                f"- output kind: {frontend_handoff_contract.get('output_kind', '')}",
                f"- assembly target: {frontend_handoff_contract.get('assembly_target', '')}",
                f"- component library: {frontend_handoff_contract.get('component_library', '')}",
                f"- forbid standalone web trio: {frontend_handoff_contract.get('forbid_standalone_web_trio', False)}",
                f"- allowed changes: {'、'.join(frontend_handoff_contract.get('allowed_changes', []))}",
                f"- locked inputs: {'、'.join(frontend_handoff_contract.get('locked_inputs', []))}",
                "- 你只负责表现层深化，不能改写教学目标、音乐答案、学生必须完成的学习动作。",
                (
                    "- 若 output kind 为 react_presentation_pack，你只能输出/修改 config/frontend-presentation-pack.json，不能把匹配模板重新写成独立 HTML 学生页；Radix Themes 是学生端 UI 组件库。"
                    if frontend_handoff_contract.get("output_kind") == "react_presentation_pack"
                    else ""
                ),
            ]
        )
    listening_contract_instruction = ""
    if _is_listening_spec(spec):
        listening_contract_instruction = "\n".join(
            [
                "聆听工具强契约：",
                "- 本页必须是聆听编辑工具，不是音乐小游戏、规则说明页或静态展示页。",
                "- 必须保留音频上传表单：id=\"listening-form\"，上传字段 name=\"audio\"。",
                "- 必须保留音乐要素控件：name=\"tonic\"、name=\"mode\"、name=\"tempo_multiplier\"、name=\"rhythm_density\"、name=\"instrument\"。",
                "- 用户上传后先调用 /api/listening/upload 获取 session_id 和 source_audio_url；切换要素后调用 /api/listening/transform，接口会按情况返回原音频保真处理或 MIDI 改编后的 transformed_audio。",
                "- 默认不改变音乐：mode/rhythm_density/instrument 为 preserve，tempo_multiplier 为 1.0；只有用户主动切换才改对应要素。",
                "- 播放必须优先使用接口返回的真实音频或 SoundFont 采样音色；oscillator 只能做最后降级。",
                "- 可以美化视觉，但不能删除上传、要素切换、原版/改编版对比试听和处理状态反馈。",
            ]
        )
    template_instruction = (
        "本次命中非音高游戏模板。禁止生成独立 HTML；请只产出 React 学生运行时可消费的 Radix presentation pack。"
        if forbid_standalone_web_trio
        else (
            "本次是直接生成且已命中活动母版。活动母版只存在于 config/opencode-spec.json 和 config/opencode-artifact-request.md 的说明中；当前目录没有可复用的模板 index.html。请参考母版能力说明，直接新写完整 index.html。"
            if direct_template_reference
            else (
                "本次是直接生成且已命中活动母版。请先读取当前目录已有的 index.html，在这个母版基础上保留上传/控件/播放/API 等核心结构，只围绕用户原始需求做增量调动；不要从零重写成另一种页面。"
                if direct_template_seed
                else "首次生成禁止读取、沿用或复制当前目录里已有的 index.html 本地母版；请只根据核心规格重写一个新的完整单文件 index.html。"
            )
        )
    )

    return "\n".join(
        [
            (
                "你是 React 学生运行时表现层执行层。请在当前目录直接更新 config/frontend-presentation-pack.json。"
                if forbid_standalone_web_trio
                else "你是网页产物执行层。请在当前目录直接生成完整单文件 index.html。"
            ),
            f"当前生成模式：{generation_mode}。fast 模式优先先做出可运行网页并减少无谓返工；strict 模式再补齐完整验收与细节。",
            (
                "请直接输出可被 React + Vite + Radix Themes 学生端消费的表现层配置，不要写网页三件套。"
                if forbid_standalone_web_trio
                else "请直接输出一个能打开、能操作、能播放的首版页面，不要先追求所有扩展细节一次到位。"
            ),
            template_instruction,
            (
                "必须实际改写 config/frontend-presentation-pack.json；只写摘要、只回复说明、或创建 index.html 都会被判定为失败。"
                if forbid_standalone_web_trio
                else "必须实际改写 index.html；只写 config/opencode-artifact-summary.md、只回复说明、或保留本地兜底模板都会被判定为生成失败。"
            ),
            (
                "React/Radix 表现层只负责视觉布局、HUD、控件意图、反馈和奖励风格；不能改玩法答案或教学目标。"
                if forbid_standalone_web_trio
                else "如果命中了活动母版，母版只提供参考方向、模块能力和交互骨架；视觉布局、文案组织、操作细节和课堂贴合必须针对当前需求重新生成，不能搜索旧产物、不能复制历史页面、不能把模板页面原样复用。"
            ),
            f"用户原始需求：{original_need}",
            f"页面可见文字必须逐字出现教学重点：{target_music_element or '音乐要素'}；不要只写游戏名或歌曲名。",
            f"本关任务必须可见写出：环节={target_stage or '课堂环节'}；目标={target_objective or '课堂目标'}。",
            f"本关任务还必须呈现选中环节任务关键词：{target_segment_task or '听辨、排序、说明理由'}。",
            f"必须保留的关键要素：{'、'.join(_short_text(item, 50) for item in must_include[:8])}",
            f"不要添加的无关大功能：{'、'.join(_short_text(item, 50) for item in must_not_include[:8])}",
            f"音乐逻辑契约：{music_logic_contract.get('focus', 'none')}；材料表：{'、'.join(music_tokens[:8])}",
            (
                f"歌曲锚定：{song_anchor_contract.get('song_title', 'none')}；片段：{selected_phrase.get('label', '')}；序列：{' -> '.join(str(item) for item in selected_phrase.get('target_sequence', [])[:10])}"
                if has_active_song_anchor
                else "歌曲锚定：none；当前未锁定具体歌曲片段，请优先生成可直接使用的通用音乐概念游戏。"
            ),
            lesson_contract_instruction,
            frontend_handoff_instruction,
            listening_contract_instruction,
            activity_instruction,
            "学生界面少字，不能是规则说明页；必须能点击、拖拽、播放或产生动画反馈。",
            "主操作区要大：按钮/卡片/拖拽区/画布/跑道至少占首屏主体，触控按钮高度至少 56px，不能留大块空白或只放装饰。",
            "首屏必须能直接操作：开始按钮、试听按钮或主游戏板要在首屏中央；主游戏板请使用 id=\"game-area\" 或 class=\"game-board/main-stage\"，拖拽区请使用 id=\"challenge-zone\" 或 class=\"drop-zone\"。",
            "优先完成用户原始需求，不要把模板功能、美化组件或未要求的大模块强行加入页面。",
            "如果是音乐小游戏，页面的符号、名称、播放和判定答案必须尽量来自 config/music-logic-contract.json，不要自己发明额外答案材料。",
            "如果存在 config/frontend-handoff-contract.json，你只负责其中 allowed_changes 列出的表现层深化；locked_inputs 和 must_not_change 绝对不能改。",
            (
                "如果存在歌曲片段锚定，页面、播放和判定优先使用该片段。"
                if has_active_song_anchor
                else "当前没有锁定歌曲片段时，可以直接生成通用音乐概念游戏；不要伪造歌曲乐句、片段标签或不存在的音频。"
            ),
            "页面首屏必须显性写出当前教案环节任务；如果存在歌曲片段标签，也必须在学生可见区域写出该片段标签。",
            (
                "音乐小游戏首屏任务信息必须由 React/Radix 学生运行时承载，可见文字包含“本关任务”，并用短标签写清“听：... 做：... 过关：...”。"
                if forbid_standalone_web_trio
                else "音乐小游戏首屏必须由你在 index.html 里写出 `<section data-lesson-panel=\"true\">`，可见文字必须包含“本关任务”，并用短标签写清“听：... 做：... 过关：...”。"
            ),
            "播放优先使用 soundfont-player + FluidR3_GM；如果采样暂时没接稳，也要先保证页面有可恢复的播放链路和主玩法。",
            "不要在页面显示 OpenCode、API、代码、模型、Basic Pitch、后台等技术词。",
            (
                "写完 config/frontend-presentation-pack.json 后写 config/opencode-artifact-summary.md，最后只回复：已完成。"
                if forbid_standalone_web_trio
                else "写完 index.html 后写 config/opencode-artifact-summary.md，最后只回复：已完成。"
            ),
        ]
    )


def _build_artifact_request(
    spec: dict[str, Any],
    *,
    action: str,
    revision: str,
    brain_report: dict[str, Any] | None = None,
) -> str:
    activity_type = spec.get("activity_type", "mixed")
    generation_mode = _generation_mode_for_spec(spec)
    read_existing_index = _should_read_existing_index(spec, action=action)
    blueprint_plan = spec.get("blueprint_plan", {})
    generation_strategy = spec.get("generation_strategy", {})
    if action == "generate":
        return _build_compact_artifact_request(spec)
    must_do = (
        "Incrementally modify the existing page files in place. Preserve current working features and only change what the user requested."
        if action == "revise"
        else (
            "Read the existing `index.html` blueprint page first, then refine it into a complete, polished, standalone classroom tool page that stays within the selected activity type."
            if read_existing_index
            else "Do not spend time reading the existing `index.html` blueprint page first. Build the page directly from the lesson spec and the playable game contract so the playable interaction lands before timeout."
        )
    )
    asset_instruction = (
        "If the current page already uses separate `styles.css` or `app.js`, update those existing files consistently; otherwise keep the page self-contained."
        if action == "revise"
        else "Prefer a single self-contained `index.html` with inline CSS and JavaScript."
    )
    lines = [
        "# OpenCode Artifact Request",
        "",
        f"- Action: {action}",
        f"- Title: {spec.get('title', '音乐课堂工具')}",
        f"- Activity type: {activity_type}",
        f"- Generation mode: {generation_mode}",
        f"- Song: {spec.get('song_name', '自选歌曲')}",
        f"- Grade band: {spec.get('grade_band', '小学')}",
        "",
        "## Must Do",
        "",
        f"- {must_do}",
        f"- {asset_instruction}",
        "- Only reference `styles.css` or `app.js` if you also create those files before finishing.",
        "- Do not mention OpenCode, APIs, code, models, Basic Pitch, or backend technical routes in the UI.",
        "- Keep all edits inside this artifact directory.",
        "- Write a short Chinese summary to `config/opencode-artifact-summary.md`.",
        "- Stop immediately after the page and summary are written.",
        "- Keep visible student text short. Avoid large lesson-analysis blocks, design rationale paragraphs, or teacher-only sections on the student page.",
        "- Fast mode should stop once the page is clearly playable and coherent; strict mode should spend the extra effort on verification and cleanup.",
        "- Student page contract: few words, large modules, no wasted blank space, playful classroom game feel.",
        "- Copy budget: one-sentence task, short chips, no visible long paragraphs; hide or omit teacher-only rationale/checklists from the student page.",
        "- Scale contract: primary buttons/cards/drop zones/canvas/race lanes must visually dominate the first screen; touch targets should be at least 56px tall.",
        "- The student-visible page must show the selected lesson segment task in short Chinese, so teachers can see which classroom step this game serves.",
        "- If a song anchor phrase label exists, render that phrase label in the visible task area instead of hiding it only inside data/config.",
        "- When the music concept is a fixed pitch class or fixed solfege set such as sol/mi/do/re, keep the gameplay materials concrete. Do not replace fixed notes with abstract direction-only labels.",
        "- For lower-primary pages, use a more playful cartoon style and add real game progression such as rounds, lives, stars, or unlock steps.",
        "- Use sampled SoundFont playback for instruments. Do not make oscillator-only synth tones the primary sound.",
        "- Recommended browser setup: local /runtime-assets/soundfont-player/soundfont-player.js + /runtime-assets/midi-js-soundfonts/FluidR3_GM first, with an explicit nameToUrl callback. External CDN/GitHub hosts are fallback only.",
        "- Instrument mapping: piano/acoustic_grand_piano, violin, flute, koto for guzheng-like timbre, acoustic_guitar_nylon, cello, clarinet, xylophone.",
        "- Web Audio oscillator tones are allowed only as fallback when the sampled SoundFont fails to load.",
        "",
        "## Interaction Expectations",
        "",
        f"- Blueprint label: {blueprint_plan.get('blueprint_label', 'not specified')}",
        f"- Blueprint reason: {blueprint_plan.get('selection_reason', 'not specified')}",
        f"- Primary interaction: {blueprint_plan.get('primary_interaction', 'not specified')}",
        f"- Gameplay focus: {blueprint_plan.get('gameplay_focus', 'not specified')}",
        f"- Progression strategy: {blueprint_plan.get('progression_strategy', 'not specified')}",
        f"- Generation mode: {generation_strategy.get('mode', 'not specified')}",
        f"- Artifact goal: {generation_strategy.get('artifact_goal', 'not specified')}",
        f"- OpenCode target: {generation_strategy.get('opencode_execution_target', 'not specified')}",
        f"- Render priority: {' / '.join(generation_strategy.get('render_priority', []))}",
        "- Performance tools should include a real game flow, not only text cards.",
        "- Creation tools should include real manipulation such as drag/drop, grid composition, playback, reset, and voice selection when relevant.",
        "- Music game tools should include an actual playable loop: game objects, user input, start/retry, animated feedback, win condition, and reflection prompt.",
        "- Listening tools should preserve the existing upload and music-element controls so the backend endpoints can still work.",
    ]
    if isinstance(spec.get("lesson_game_contract"), dict) and spec.get("lesson_game_contract"):
        lines.extend(
            [
                "",
                "## Lesson Game Contract",
                "",
                json.dumps(spec.get("lesson_game_contract", {}), ensure_ascii=False, indent=2),
            ]
        )
    if revision.strip():
        lines.extend(["", "## User Revision", "", revision.strip()])

    if brain_report:
        planning = brain_report.get("planning", {})
        critique = brain_report.get("self_critique", {})
        hardening = brain_report.get("auto_hardening", {})
        lines.extend(
            [
                "",
                "## Agent Brain Checklist",
                "",
                f"- Objective: {planning.get('objective', 'not specified')}",
                f"- Self-critique score: {critique.get('score', 'not scored')} ({critique.get('verdict', 'unknown')})",
                f"- Self-critique summary: {critique.get('summary', '')}",
                f"- Auto hardening applied: {hardening.get('applied', False)}",
                "- Do not expose hidden reasoning. Use these visible checklist items to improve the classroom tool.",
                "- Must address high-priority failed or warning checks before adding decorative features.",
            ]
        )
        fixes = critique.get("recommended_fixes", [])
        if fixes:
            lines.append("- Recommended fixes:")
            for fix in fixes[:6]:
                lines.append(f"  - {fix}")
        subgoals = brain_report.get("subgoals", [])
        if subgoals:
            lines.append("- Subgoals:")
            for subgoal in subgoals[:8]:
                lines.append(
                    f"  - {subgoal.get('title', 'subgoal')}: {subgoal.get('deliverable', '')}"
                )

    interaction_model = spec.get("interaction_model", {})
    scoring = spec.get("scoring", {})
    runtime_behaviors = spec.get("runtime_behaviors", {})
    visual_theme = spec.get("visual_theme", {})
    visual_asset_pack = spec.get("visual_asset_pack", {})
    image_generation = spec.get("image_generation", {})
    performance = spec.get("performance", {}) if isinstance(spec.get("performance"), dict) else {}
    music_game = spec.get("music_game", {}) if isinstance(spec.get("music_game"), dict) else {}
    playable_game = music_game.get("playable_game", {}) if isinstance(music_game.get("playable_game"), dict) else {}
    music_logic_contract = _music_logic_contract_for_spec(spec)
    song_anchor_contract = spec.get("song_anchor_contract", {}) if isinstance(spec.get("song_anchor_contract"), dict) else {}
    song_phrase = song_anchor_contract.get("selected_phrase", {}) if isinstance(song_anchor_contract.get("selected_phrase"), dict) else {}
    has_active_song_anchor = _has_active_song_anchor(song_anchor_contract)
    lesson_context = spec.get("lesson_context", {})
    education_context = compact_prompt_context(
        f"{spec.get('title', '')} {spec.get('subtitle', '')} {spec.get('song_name', '')}",
        spec,
    )
    lines.extend(
        [
            "",
            "## Lesson Context",
            "",
            f"- Target stage: {spec.get('target_stage', lesson_context.get('target_stage', 'not specified'))}",
            f"- Target objective: {spec.get('target_objective', lesson_context.get('target_objective', 'not specified'))}",
            f"- Target music element: {spec.get('target_music_element', lesson_context.get('target_music_element', 'not specified'))}",
            f"- Lesson evidence: {spec.get('lesson_evidence', lesson_context.get('lesson_evidence', 'not specified'))}",
            f"- Selected segment task: {spec.get('target_segment_task', lesson_context.get('target_segment_task', 'not specified'))}",
            f"- Selected segment gameable point: {spec.get('target_segment_gameable_point', lesson_context.get('target_segment_gameable_point', 'not specified'))}",
            f"- Selected segment mechanic: {spec.get('target_segment_mechanic', lesson_context.get('target_segment_mechanic', 'not specified'))}",
            f"- Music mechanic rule: {(spec.get('music_element_mechanic') or lesson_context.get('music_element_mechanic', {})).get('mechanism_id', 'not specified')}",
            f"- Stage reason: {lesson_context.get('stage_reason', 'not specified')}",
            f"- Student task: {lesson_context.get('student_task', 'not specified')}",
            f"- Assessment closure: {spec.get('assessment_closure', lesson_context.get('assessment_closure', 'not specified'))}",
            f"- Why this game fits this lesson: {spec.get('why_this_game_fits_this_lesson', lesson_context.get('why_this_game_fits_this_lesson', 'not specified'))}",
            "- Musical game logic contract:",
            *[f"  - {item}" for item in (spec.get("musical_game_logic_contract") or lesson_context.get("musical_game_logic_contract", {})).get("non_negotiables", [])],
            "- Goal-task-game mapping:",
            *[f"  - {item}" for item in (lesson_context.get("transfer_payload", {}).get("goal_task_mapping_summary", []) or [])],
            "- Decision trace:",
            *[f"  - {item}" for item in lesson_context.get("decision_trace", [])],
            "- Prompt chain:",
            *[f"  - {item.get('name', 'step')}: {item.get('instruction', '')}" for item in (spec.get("lesson_prompt_chain") or lesson_context.get("prompt_chain", []))],
            "- Teacher guidance:",
            *[f"  - {item}" for item in (spec.get("teacher_guidance") or lesson_context.get("teacher_guidance", []))],
            "",
            "## Music Education Knowledge",
            "",
            f"- Grade profile: {education_context['grade']['label']}",
            f"- Grade abilities: {' / '.join(education_context['grade']['abilities'])}",
            f"- Grade interaction guidance: {' / '.join(education_context['grade']['interaction'])}",
            f"- Curriculum anchors: {' / '.join(anchor['title'] for anchor in education_context['curriculum'])}",
            f"- Repertoire teaching points: {' / '.join((education_context.get('repertoire') or {}).get('teaching_points', []))}",
            "",
            "## Interaction Plan",
            "",
            f"- Blueprint label: {blueprint_plan.get('blueprint_label', 'not specified')}",
            f"- Blueprint reason: {blueprint_plan.get('selection_reason', 'not specified')}",
            f"- Blueprint component focus: {', '.join(blueprint_plan.get('component_focus', []))}",
            f"- Generation mode: {generation_strategy.get('mode', 'not specified')}",
            f"- Artifact goal: {generation_strategy.get('artifact_goal', 'not specified')}",
            f"- Render priority: {' / '.join(generation_strategy.get('render_priority', []))}",
            f"- Primary interaction model: {interaction_model.get('primary', 'not specified')}",
            f"- Components: {', '.join(interaction_model.get('components', []))}",
            f"- Student actions: {' / '.join(interaction_model.get('student_actions', []))}",
            f"- Teacher controls: {' / '.join(interaction_model.get('teacher_controls', []))}",
            f"- Artifact outputs: {' / '.join(interaction_model.get('artifact_outputs', []))}",
            f"- Performance template: {performance.get('template_label', 'none')} ({performance.get('template_variant', 'not selected')})",
            f"- Performance template fit: {(performance.get('template_selection') or {}).get('score', 'not scored')}",
            f"- Playable music game: {playable_game.get('operation_type', 'not specified')}",
            f"- Playable materials: {', '.join(item.get('label', '') for item in playable_game.get('materials', []) if isinstance(item, dict))}",
            f"- Target sequence: {' -> '.join(playable_game.get('target_sequence', []))}",
            f"- Music logic contract focus: {music_logic_contract.get('focus', 'not specified')}",
            f"- Music logic tokens: {', '.join(item.get('id', '') + ':' + item.get('label', '') for item in music_logic_contract.get('tokens', []) if isinstance(item, dict))}",
            f"- Song anchor: {song_anchor_contract.get('song_title', 'not specified')} / {song_phrase.get('label', 'not specified')}",
            f"- Song anchor target sequence: {' -> '.join(str(item) for item in song_phrase.get('target_sequence', [])[:24])}",
            "",
            "## Scoring Plan",
            "",
            f"- Enabled: {scoring.get('enabled', False)}",
            f"- Pass score: {scoring.get('pass_score', 0)}",
            f"- Feedback mode: {scoring.get('feedback_mode', 'not specified')}",
            "- Metrics:",
        ]
    )
    for metric in scoring.get("metrics", []):
        if isinstance(metric, dict):
            lines.append(
                f"  - {metric.get('label', metric.get('id', 'metric'))}: weight {metric.get('weight', 0)}; feedback: {metric.get('feedback', '')}"
            )
    lines.extend(
        [
            "",
            "## Runtime Behaviors",
            "",
            f"- Save progress: {runtime_behaviors.get('save_progress', False)}",
            f"- Unlock next step: {runtime_behaviors.get('unlock_next_step', False)}",
            f"- Countdown: {runtime_behaviors.get('countdown', False)}",
            f"- Auto play after start: {runtime_behaviors.get('auto_play_after_start', False)}",
            f"- Resettable: {runtime_behaviors.get('resettable', True)}",
            f"- Teacher override: {runtime_behaviors.get('allow_teacher_override', False)}",
            f"- Requires audio upload: {runtime_behaviors.get('requires_audio_upload', False)}",
            f"- Playback: {runtime_behaviors.get('playback', 'not specified')}",
            "",
            "## Visual Theme",
            "",
            f"- Name: {visual_theme.get('name', 'not specified')}",
            f"- Mood: {visual_theme.get('mood', 'not specified')}",
            f"- Layout: {visual_theme.get('layout', 'not specified')}",
            f"- Palette: {', '.join(visual_theme.get('palette', []))}",
            f"- Illustration style: {visual_theme.get('illustration_style', 'not specified')}",
            f"- Motion: {visual_theme.get('motion', 'not specified')}",
            f"- Preset asset pack: {visual_asset_pack.get('label', 'not specified')} ({visual_asset_pack.get('id', 'none')})",
            f"- Hero image: {visual_asset_pack.get('hero', 'not specified')}",
            f"- Badge image: {visual_asset_pack.get('badge', 'not specified')}",
            f"- Component image: {visual_asset_pack.get('component', 'not specified')}",
            f"- Generated background image: {visual_asset_pack.get('background_image', 'not specified')}",
            f"- Image generation status: {image_generation.get('status', 'not_run')} via {image_generation.get('provider', 'not specified')}",
        ]
    )
    if playable_game:
        material_ids = [
            str(item.get("id", "")).strip()
            for item in playable_game.get("materials", [])
            if isinstance(item, dict) and str(item.get("id", "")).strip()
        ]
        learning_transfer = playable_game.get("learning_transfer", {}) if isinstance(playable_game.get("learning_transfer"), dict) else {}
        student_task = playable_game.get("student_facing_task", {}) if isinstance(playable_game.get("student_facing_task"), dict) else {}
        lines.extend(
            [
                "",
                "## Mandatory Playable Game Contract",
                "",
                "- This is a lesson-generated music game. Implement the playable game contract exactly; do not replace it with explanation cards.",
                "- Add one compact student-facing guide labeled `本关任务` near the top: answer `我听什么？我做什么？怎样算过关？` in three short chips.",
                f"- Student-facing chips: listen={student_task.get('listen', '')}; do={student_task.get('do', '')}; pass={student_task.get('pass', '')}.",
                f"- Learning transfer loop: listen={learning_transfer.get('listen_target', '')}; evidence={'; '.join(str(item) for item in learning_transfer.get('music_evidence', [])[:3])}; operation={learning_transfer.get('student_operation', '')}; transfer={learning_transfer.get('classroom_transfer', '')}.",
                "- If the learning transfer mentions 情绪、声音、动作、演唱方法、连贯、跳跃、重复 or 对比, the game must include visible evidence cards for those ideas. Students must click or drag those evidence cards as part of the winning answer; note/phrase ordering alone is invalid.",
                "- The student-facing page must include these controls: 试听目标、试听我的排列、检查挑战、重来.",
                "- The student-facing page must include a card/material area, a challenge/drop area, immediate feedback, and a success state.",
                "- Preserve material ids and labels from `config/playable-music-game.json`; do not add extra answer levels that are not in the materials.",
                "- Use `config/music-logic-contract.json` as the single source of truth for music symbols, labels, playback duration/pitch, target sequence, scoring, and animation timing.",
                (
                    "- If `config/song-anchor-contract.json` exists, use it as the required fragment source and keep the game anchored to the selected song phrase."
                    if has_active_song_anchor
                    else "- No song phrase is locked for this run. Build a generic but playable concept-focused music game and do not invent a fake song fragment."
                ),
                "- Do not invent animal ids, note symbols, target answers, or playback pitches that are absent from the music logic contract.",
                f"- Allowed material ids only: {', '.join(material_ids)}.",
                f"- Required target sequence: {' -> '.join(str(item) for item in playable_game.get('target_sequence', []))}.",
                "- The check button must compare the student's sequence with the required target sequence and show success/wrong/partial feedback.",
                "- Passing the game cannot stop at scores; after success, display the classroom transfer action and ask students to sing, clap, move, explain, play, or create as required by the learning transfer loop.",
                "- A static rule page, a decorative card wall, or an unrelated drag-and-drop toy is invalid even if it looks polished.",
                "- Teacher quality checks such as “是否服务于...” or “是否真正聚焦...” must never appear as student game rules.",
                "- Keep visible text short. Use concise rules, large buttons, visual cards, sound playback, and animated feedback.",
            ]
        )

    selected_components = _selected_component_specs(spec)
    if selected_components:
        lines.extend(["", "## Selected Component Library Specs", ""])
        for component in selected_components:
            lines.extend(
                [
                    f"### {component['id']} - {component['name']}",
                    f"- Purpose: {component['purpose']}",
                    f"- Required elements: {', '.join(component['required_elements'])}",
                    f"- Behaviors: {' / '.join(component['behaviors'])}",
                    "",
                ]
            )

    music_game = spec.get("music_game", {})
    if music_game.get("enabled"):
        lines.extend(
            [
                "",
                "## Music Game Blueprint",
                "",
                f"- Game type: {music_game.get('game_type', 'custom_music_game')}",
                f"- Game family: {music_game.get('game_family', 'mission')}",
                f"- Game name: {music_game.get('game_name', '音乐小游戏')}",
                f"- Music concept: {music_game.get('music_concept', '音乐要素')}",
                f"- Goal: {music_game.get('goal', '')}",
                f"- Mechanic: {music_game.get('mechanic', '')}",
                f"- Core loop: {' -> '.join(music_game.get('core_loop', []))}",
                f"- Progression: {' / '.join(music_game.get('progression', []))}",
                f"- Failure/reset: {music_game.get('failure_state', '')}",
                f"- Target session minutes: {music_game.get('target_session_minutes', '')}",
                f"- Student actions: {' / '.join(music_game.get('student_actions', []))}",
                f"- Win condition: {music_game.get('win_condition', '')}",
                "- Rules:",
            ]
        )
        for rule in music_game.get("rules", []):
            if isinstance(rule, dict):
                lines.append(
                    f"  - {rule.get('music_element', '')} = {rule.get('value', '')}; character: {rule.get('character', '')}; motion: {rule.get('motion', '')}; feedback: {rule.get('feedback', '')}"
                )

    performance = spec.get("performance", {})
    if performance.get("enabled"):
        lines.extend(
            [
                "",
                "## Performance Levels",
                "",
                f"- Theme: {performance.get('theme', '音乐探险')}",
                f"- Target skill: {performance.get('target_skill', '音乐要素综合感知')}",
            ]
        )
        for index, level in enumerate(performance.get("levels", []), start=1):
            lines.append(
                f"- Level {index}: {level.get('title', '')} | Task: {level.get('student_task', '')} | Rule: {level.get('success_rule', '')}"
            )

    creation = spec.get("creation", {})
    if creation.get("enabled"):
        lines.extend(
            [
                "",
                "## Creation Setup",
                "",
                f"- Mode: {creation.get('creation_mode', 'free_assembly')}",
                f"- Tonic: {creation.get('tonic', 'C')}",
                f"- Scale/mode: {creation.get('mode', 'western_major')}",
                f"- Bars: {creation.get('bars', 4)}",
                f"- Mood: {creation.get('mood', '明亮')}",
                f"- Piece count: {len(creation.get('pieces', []))}",
            ]
        )

    listening = spec.get("listening", {})
    if listening.get("enabled"):
        lines.extend(
            [
                "",
                "## Listening Setup",
                "",
                f"- Tonic: {listening.get('tonic', 'C')}",
                f"- Mode: {listening.get('mode', 'western_major')}",
                f"- Instrument: {listening.get('instrument', 'piano')}",
                f"- Rhythm density: {listening.get('rhythm_density', 'relaxed')}",
            ]
        )

    return "\n".join(lines) + "\n"


def _build_compact_artifact_request(spec: dict[str, Any]) -> str:
    activity_type = str(spec.get("activity_type") or "mixed")
    generation_mode = _generation_mode_for_spec(spec)
    freeform_music_game = activity_type == "music_game" and str(spec.get("artifact_generation_mode") or "") == "freeform"
    frontend_handoff_contract = spec.get("frontend_handoff_contract", {}) if isinstance(spec.get("frontend_handoff_contract"), dict) else {}
    presentation_pack = spec.get("presentation_pack", {}) if isinstance(spec.get("presentation_pack"), dict) else {}
    template_id = _template_id_for_frontend_policy(spec, frontend_handoff_contract, presentation_pack)
    forbid_standalone_web_trio = _forbid_standalone_web_trio(spec, frontend_handoff_contract, presentation_pack, template_id)
    blueprint_plan = spec.get("blueprint_plan", {}) if isinstance(spec.get("blueprint_plan"), dict) else {}
    generation_strategy = spec.get("generation_strategy", {}) if isinstance(spec.get("generation_strategy"), dict) else {}
    interaction_model = spec.get("interaction_model", {}) if isinstance(spec.get("interaction_model"), dict) else {}
    prompt_contract = spec.get("user_prompt_contract", {}) if isinstance(spec.get("user_prompt_contract"), dict) else {}
    active_payload = spec.get(activity_type, {}) if isinstance(spec.get(activity_type), dict) else {}
    playable_game = active_payload.get("playable_game", {}) if activity_type == "music_game" else {}
    music_logic_contract = _music_logic_contract_for_spec(spec)
    song_anchor_contract = spec.get("song_anchor_contract", {}) if isinstance(spec.get("song_anchor_contract"), dict) else {}
    song_phrase = song_anchor_contract.get("selected_phrase", {}) if isinstance(song_anchor_contract.get("selected_phrase"), dict) else {}
    has_active_song_anchor = _has_active_song_anchor(song_anchor_contract)

    lines = [
        "# OpenCode Artifact Request",
        "",
        "- Action: generate",
        f"- Activity type: {activity_type}",
        f"- Generation mode: {generation_mode}",
        f"- Title: {spec.get('title', '音乐课堂工具')}",
        f"- Blueprint: {blueprint_plan.get('blueprint_label', spec.get('blueprint_id', 'not specified'))}",
        f"- Primary interaction: {blueprint_plan.get('primary_interaction', interaction_model.get('primary', 'not specified'))}",
        f"- Artifact goal: {generation_strategy.get('artifact_goal', '生成真实可操作的课堂网页。')}",
        f"- Render priority: {' / '.join(generation_strategy.get('render_priority', []))}",
        f"- Original user need: {_short_text(prompt_contract.get('original_user_need', spec.get('original_user_need', '')), 700)}",
        f"- Must include: {', '.join(_short_text(item, 50) for item in prompt_contract.get('must_include', [])[:12])}",
        f"- Must not include: {', '.join(_short_text(item, 50) for item in prompt_contract.get('must_not_include', [])[:10])}",
        f"- Music logic focus: {music_logic_contract.get('focus', 'not specified')}",
        f"- Music logic tokens: {', '.join(item.get('id', '') + ':' + item.get('label', '') for item in music_logic_contract.get('tokens', []) if isinstance(item, dict))}",
        (
            f"- Song anchor: {song_anchor_contract.get('song_title', 'not specified')} / {song_phrase.get('label', 'not specified')}"
            if has_active_song_anchor
            else "- Song anchor: none (generate a generic concept-focused game first)"
        ),
        (
            f"- Song phrase sequence: {' -> '.join(str(item) for item in song_phrase.get('target_sequence', [])[:24])}"
            if has_active_song_anchor
            else "- Song phrase sequence: none"
        ),
        "",
        "## Must Do",
        "",
        "- Create `config/opencode-artifact-summary.md` after writing the page.",
        "- Keep all edits inside this artifact directory.",
        "- Keep visible student text short and make the main interaction directly operable.",
        "- Student page contract: few words, large modules, no wasted blank space, playful classroom game feel.",
        "- Copy budget: one-sentence task, short chips, no visible long paragraphs; hide or omit teacher-only rationale/checklists from the student page.",
        "- Scale contract: primary buttons/cards/drop zones/canvas/race lanes must visually dominate the first screen; touch targets should be at least 56px tall.",
        "- Fast mode should stop once the page is clearly playable and coherent; strict mode should spend the extra effort on verification and cleanup.",
        "- Implement the original user need before adding polish.",
        "- Do not add major features that are absent from the original user need.",
        "- If this is a music game, use `config/music-logic-contract.json` as the only source for symbols, labels, pitch/duration playback, answers, scoring and animation timing.",
        (
            "- If `config/song-anchor-contract.json` exists, the selected song phrase is mandatory; build the game around that phrase and do not replace it with generic materials."
            if has_active_song_anchor
            else "- No selected song phrase is available for this run; keep the game generic and playable instead of fabricating song-specific material."
        ),
        "- Do not invent extra musical tokens, answer ids, animals, notes or playback mappings outside the music logic contract.",
        "- Use sampled SoundFont playback when the page plays instrument notes; oscillator can only be fallback.",
        "- Do not mention OpenCode, APIs, code, models, Basic Pitch, or backend routes in the UI.",
    ]
    if isinstance(spec.get("lesson_game_contract"), dict) and spec.get("lesson_game_contract"):
        lines.extend(
            [
                "",
                "## Lesson Game Contract",
                "",
                json.dumps(spec.get("lesson_game_contract", {}), ensure_ascii=False, indent=2),
            ]
        )
    if forbid_standalone_web_trio:
        lines[18:18] = [
            "- This game template must use the React 学生运行时 with Radix Themes and Lucide React.",
            "- 禁止创建或改写 `index.html`、`styles.css`、`app.js`；只能输出/修改 `config/frontend-presentation-pack.json` 和 `config/opencode-artifact-summary.md`。",
            "- Phaser may remain the game canvas engine, but the student-facing shell, HUD, controls, feedback and result UI must be represented as React/Radix presentation-pack intent.",
        ]
    elif freeform_music_game:
        lines[18:18] = [
            "- This request did not match an existing game template; do not force any built-in blueprint or generic classroom shell.",
            "- You may create `index.html`, `styles.css`, and `app.js` from scratch as long as the result is playable, musical, and faithful to `config/opencode-spec.json`.",
        ]
    else:
        lines[18:18] = [
            "- Read the existing `index.html` blueprint first and keep its selected activity structure, then refine it from `config/opencode-spec.json`.",
            "- Build a complete self-contained `index.html` on top of that blueprint; do not switch to another generic page type.",
        ]
    if activity_type == "creation":
        lines.extend(
            [
                "- Prioritize the creation workspace, playback controls, reset, and student feedback.",
                "- If melody grid is present, x-axis is sixteenth notes and y-axis is semitones with movable-do labels.",
                "- If voice controls are present, keep two voices separated and make piano usable by default.",
            ]
        )
    elif activity_type == "music_game":
        lines.extend(
            [
                "- Include a start/retry loop, game objects, feedback, and win condition.",
                "- The first visible game area must answer for students: `我听什么？我拖什么？怎样算过关？` Use short labels, not paragraphs.",
                "- Do not turn rules into a static explanation page.",
            ]
        )
        if isinstance(playable_game, dict) and playable_game:
            learning_transfer = playable_game.get("learning_transfer", {}) if isinstance(playable_game.get("learning_transfer"), dict) else {}
            student_task = playable_game.get("student_facing_task", {}) if isinstance(playable_game.get("student_facing_task"), dict) else {}
            lines.extend(
                [
                    "- Follow the playable game contract exactly.",
                    "- Follow the music logic contract exactly.",
                    f"- Materials: {', '.join(item.get('label', '') for item in playable_game.get('materials', []) if isinstance(item, dict))}",
                    f"- Target sequence: {' -> '.join(str(item) for item in playable_game.get('target_sequence', []))}",
                    f"- Student-facing task chips: listen={student_task.get('listen', '')}; do={student_task.get('do', '')}; pass={student_task.get('pass', '')}",
                    f"- Learning loop: listen={learning_transfer.get('listen_target', '')}; evidence={'; '.join(str(item) for item in learning_transfer.get('music_evidence', [])[:3])}; operation={learning_transfer.get('student_operation', '')}; transfer={learning_transfer.get('classroom_transfer', '')}",
                    "- The page must implement that learning loop as playable interaction: hear music, make a music-evidence choice/order, preview the answer, check it, then show the classroom transfer action.",
                    "- A page that only displays rules, cards, or decorative labels without music-evidence play/check behavior is invalid.",
                ]
            )
            if music_logic_contract.get("focus") == "song_phrase_structure_match":
                lines.extend(
                    [
                        "- This is a real song phrase and expression game, not single-note ear training.",
                        "- Phrase cards come from the uploaded song; evidence cards represent singing, emotion, movement, repetition, contrast, or closure.",
                        "- Clicking a phrase card or preview control must play the whole fragment when audio_clip_url or playback_tokens exist.",
                        "- Student task is to match song fragments with musical evidence, then return to singing, movement, or classroom explanation.",
                    ]
                )
    elif activity_type == "performance":
        lines.append("- Include challenge start, level state, feedback, retry, and completion.")
    elif activity_type == "listening":
        lines.extend(
            [
                "- This must remain a Blueprint_Listen listening editor, not a game or a static explainer.",
                "- Preserve `id=\"listening-form\"`, `name=\"audio\"`, `name=\"tonic\"`, `name=\"mode\"`, `name=\"tempo_multiplier\"`, `name=\"rhythm_density\"`, and `name=\"instrument\"`.",
                "- Upload must call `/api/listening/upload`; element changes must call `/api/listening/transform` so the backend can return either original-audio DSP previews or MIDI-based transformed playback.",
                "- Defaults must preserve the original music: mode/rhythm_density/instrument=`preserve`, tempo_multiplier=`1.0`.",
                "- Keep original vs transformed compare playback and prefer returned real audio or sampled SoundFont playback; oscillator is fallback only.",
            ]
        )

    return "\n".join(lines) + "\n"


def _selected_component_specs(spec: dict[str, Any]) -> list[dict[str, Any]]:
    component_ids = spec.get("interaction_model", {}).get("components", [])
    return component_specs_for_ids(component_ids if isinstance(component_ids, list) else [])


def _snapshot_artifact_files(target_dir: Path) -> dict[str, str]:
    snapshot: dict[str, str] = {}
    if not target_dir.exists():
        return snapshot

    for path in target_dir.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(target_dir).as_posix()
        if relative == "config/opencode-run.json":
            continue
        try:
            snapshot[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError:
            continue
    return snapshot


def _changed_artifact_files(before: dict[str, str], after: dict[str, str]) -> list[str]:
    changed = []
    for path, digest in after.items():
        if before.get(path) != digest:
            changed.append(path)
    for path in before:
        if path not in after:
            changed.append(path)
    return sorted(changed)


def _visible_artifact_files(paths: list[str]) -> list[str]:
    visible: list[str] = []
    for raw_path in paths:
        path = str(raw_path or "").strip()
        if not path:
            continue
        if path in {"index.html", "styles.css", "app.js"}:
            visible.append(path)
            continue
        if path.startswith(("assets/", "components/", "python/transforms/")):
            visible.append(path)
            continue
        if path.startswith("config/") and path not in {
            "config/opencode-run.json",
            "config/opencode-artifact-request.md",
            "config/opencode-artifact-summary.md",
            "config/opencode-spec.json",
            "config/opencode-task.json",
            "config/tool-spec.json",
            "config/agent-brain.json",
            "config/execution-report.json",
        }:
            visible.append(path)
    return visible


def _validate_artifact_page(target_dir: Path) -> list[str]:
    errors: list[str] = []
    index_path = target_dir / "index.html"
    if not index_path.exists():
        return ["index.html missing"]

    try:
        content = index_path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"index.html unreadable: {exc}"]

    if "</html>" not in content.lower():
        errors.append("index.html appears incomplete")

    referenced_files = _local_asset_references(content)
    for reference in referenced_files:
        if not (target_dir / reference).exists():
            errors.append(f"missing referenced asset: {reference}")
    return errors


def _local_asset_references(content: str) -> list[str]:
    references: list[str] = []
    patterns = [
        r"""<link[^>]+href=["']([^"']+)["']""",
        r"""<script[^>]+src=["']([^"']+)["']""",
    ]
    for pattern in patterns:
        for match in re.findall(pattern, content, flags=re.IGNORECASE):
            reference = match.strip()
            if not reference or reference.startswith(("#", "/", "http://", "https://", "data:", "mailto:")):
                continue
            if ".." in Path(reference).parts:
                references.append(reference)
                continue
            references.append(reference.split("?", 1)[0].split("#", 1)[0])
    return references


def _build_advice_prompt(message: str) -> str:
    return "\n".join(
        [
            "你是不亦乐乎-音乐游戏生成智能体的对话顾问。",
            "请直接用中文回答用户的问题，可以给教学建议、活动设计建议、工具设计建议或提示词优化建议。",
            "你不是代码生成器，不允许输出 HTML、CSS、JavaScript、Python、MIDI、命令行、文件结构或 Markdown 代码块。",
            "如果用户要求你生成代码、网页或文件，只能把需求整理成可放入生成框的设计描述，并提示由页面生成流程执行。",
            "如果用户没有要求生成网页，就不要说正在生成网页。",
            "不要展示后台技术路线、命令、代码、模型或实现细节。",
            "回答要友好、具体、适合音乐教师快速理解；必要时给 3-5 条建议。",
            "如果用户想继续生成工具，请在最后用一句话提示：可以把这段想法放进生成框继续制作。",
            "",
            "用户问题：",
            message.strip(),
        ]
    )


def _extract_opencode_reply(stdout: str) -> str:
    lines = [line.strip() for line in stdout.splitlines() if line.strip()]
    collected: list[str] = []

    for line in lines:
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        _collect_text_parts(payload, collected)

    if collected:
        return "\n".join(_dedupe_text_parts(collected)).strip()

    text_lines = [line for line in lines if not line.startswith("{")]
    return "\n".join(text_lines[-8:]).strip()


def _collect_text_parts(value: Any, collected: list[str]) -> None:
    if isinstance(value, dict):
        part_type = value.get("type")
        if part_type in {"text", "message"} and isinstance(value.get("text"), str):
            collected.append(value["text"])
        if isinstance(value.get("content"), str) and part_type in {"assistant", "text", "message"}:
            collected.append(value["content"])
        for key in ("message", "part", "parts", "content", "data", "result"):
            if key in value:
                _collect_text_parts(value[key], collected)
    elif isinstance(value, list):
        for item in value:
            _collect_text_parts(item, collected)


def _dedupe_text_parts(parts: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for part in parts:
        cleaned = part.strip()
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        result.append(cleaned)
    return result


def _redacted_command(command: list[str]) -> list[str]:
    return [str(part) for part in command]


def _decode_timeout_output(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return _decode_process_output(value)
    return str(value)


def _decode_process_output(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        for encoding in ("utf-8", "utf-8-sig", "gb18030", "gbk"):
            try:
                return value.decode(encoding)
            except UnicodeDecodeError:
                continue
        return value.decode("utf-8", errors="replace")
    return str(value)


def _relative_output_url(path: Path) -> str:
    return output_url_for_path(path)


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _initial_opencode_seed(spec: dict[str, Any]) -> str:
    title = str(spec.get("title", "音乐课堂工具"))
    activity_type = str(spec.get("activity_type", "mixed"))
    return f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{title}</title>
  </head>
  <body>
    <main>
      <h1>{title}</h1>
      <p>请根据 config/tool-spec.json 和 config/opencode-artifact-request.md 生成完整课堂工具页面。</p>
      <p>活动类型：{activity_type}</p>
    </main>
  </body>
</html>
"""


def _python_plugin_stub(name: str) -> str:
    return f'''"""OpenCode 生成目标：{name}

这个文件是受限 OpenCode 任务包中的 Python 插件占位实现。
真实运行时应由 python-music-coder agent 按 MidiTransform 接口生成或改写。
"""

from __future__ import annotations


class MidiTransform:
    name = "{name}"
    description = "遵循受限音乐技术路线的 MIDI 分析与变换插件。"

    def analyze(self, midi_path: str) -> dict:
        return {{
            "input_midi": midi_path,
            "analysis": "等待 OpenCode 生成具体音乐分析逻辑。",
        }}

    def transform(self, midi_path: str, output_path: str, params: dict) -> dict:
        return {{
            "analysis": self.analyze(midi_path),
            "changed_elements": [],
            "music_reasoning": "等待 OpenCode 生成具体 MIDI 变换逻辑。",
            "output_midi": output_path,
            "preview_audio": "",
        }}
'''


def _level_controller_stub() -> str:
    return """export class LevelController {
  constructor(levels) {
    this.levels = levels;
    this.completed = new Set();
  }

  complete(index) {
    if (index === 0 || this.completed.has(index - 1)) {
      this.completed.add(index);
    }
    return this.progress();
  }

  progress() {
    return this.levels.length ? Math.round((this.completed.size / this.levels.length) * 100) : 0;
  }
}
"""


def _creation_board_stub() -> str:
    return """export class CreationBoard {
  constructor({ pieces, mode, bars }) {
    this.pieces = pieces;
    this.mode = mode;
    this.bars = bars;
    this.composition = [];
  }

  addPiece(piece) {
    this.composition.push(piece);
    return this.composition;
  }

  clear() {
    this.composition = [];
  }
}
"""


def _music_game_runner_stub() -> str:
    return """export class MusicGameRunner {
  constructor({ gameType = "lesson_mission_game", rules = [], winCondition = "", coreLoop = [] } = {}) {
    this.gameType = gameType;
    this.rules = rules;
    this.winCondition = winCondition;
    this.coreLoop = coreLoop;
    this.sequence = [];
    this.attempts = 0;
  }

  addRule(rule) {
    this.sequence.push(rule);
    return this.sequence;
  }

  reset() {
    this.sequence = [];
  }

  check() {
    this.attempts += 1;
    const hasChoice = this.sequence.length > 0;
    const enoughForLoop = this.sequence.length >= Math.min(3, Math.max(1, this.rules.length));
    const passed = hasChoice && (this.gameType === "lesson_mission_game" || enoughForLoop);
    return {
      passed,
      attempts: this.attempts,
      progress: this.rules.length ? Math.round((this.sequence.length / this.rules.length) * 100) : 0,
      nextStep: this.coreLoop[Math.min(this.sequence.length, this.coreLoop.length - 1)] || "说出音乐理由",
      message: passed ? this.winCondition : "先完成一次游戏操作，再回到音乐理由。",
    };
  }
}
"""
