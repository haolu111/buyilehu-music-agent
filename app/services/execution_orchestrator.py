from __future__ import annotations

import ast
import hashlib
from html import unescape as html_unescape
from html.parser import HTMLParser
import json
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.services.music_education_knowledge import evaluate_music_education_fit
from app.services.music_logic_contract import validate_music_logic_contract
from app.services.song_material_parser import validate_song_anchor_contract
from app.services.runtime_paths import get_output_dir


EXECUTION_AGENTS = [
    {
        "id": "execution-orchestrator",
        "name": "Execution Orchestrator",
        "responsibility": "拆分执行任务、收集各执行智能体结果、输出最终验收报告。",
    },
    {
        "id": "frontend-artifact-builder",
        "name": "Frontend Artifact Builder",
        "responsibility": "确认网页产物文件、交互入口、资源引用和课堂页面结构。",
    },
    {
        "id": "music-logic-agent",
        "name": "Music Logic Agent",
        "responsibility": "检查调式、节奏、关卡、创作素材和音乐小游戏规则是否符合音乐课堂逻辑。",
    },
    {
        "id": "lesson-fit-agent",
        "name": "Lesson Fit Agent",
        "responsibility": "检查生成结果是否真正贴合课例目标、教学环节、音乐要素和课堂闭环。",
    },
    {
        "id": "browser-qa-agent",
        "name": "Browser QA Agent",
        "responsibility": "用轻量浏览器式静态检查模拟页面打开、按钮、表单和脚本风险。",
    },
    {
        "id": "repair-agent",
        "name": "Repair Agent",
        "responsibility": "对可安全自动修复的问题做最小修复，并记录剩余风险。",
    },
    {
        "id": "versioning-agent",
        "name": "Versioning Agent",
        "responsibility": "为每次生成、修改或修复后的产物建立版本快照和清单。",
    },
    {
        "id": "music-tool-calculator",
        "name": "Music Tool Calculator",
        "responsibility": "计算 BPM、拍数、小节、素材数量、关卡数量和评价权重等可验证指标。",
    },
    {
        "id": "code-interpreter",
        "name": "Code Interpreter",
        "responsibility": "解析 JSON、检查 Python/JavaScript/HTML 结构和执行层配置一致性。",
    },
    {
        "id": "optional-search-agent",
        "name": "Optional Search Agent",
        "responsibility": "为未来备课资料检索预留，默认离线禁用，避免生成流程依赖网络。",
    },
]

ARTIFACT_FILE_ALLOWLIST = {
    "index.html",
    "styles.css",
    "app.js",
    "config/tool-spec.json",
    "config/opencode-spec.json",
    "config/opencode-task.json",
    "config/agent-brain.json",
    "config/opencode-run.json",
    "config/opencode-artifact-request.md",
    "config/opencode-artifact-summary.md",
    "config/selected-components.json",
    "config/levels.json",
    "config/creation-pieces.json",
    "config/music-game.json",
    "config/lesson-adaptation.json",
    "config/template-decision.json",
    "config/frontend-handoff-contract.json",
    "config/frontend-presentation-pack.json",
    "config/song-material.json",
    "config/song-anchor-contract.json",
    "config/lesson-game-contract.json",
    "config/playable-music-game.json",
    "components/LevelController.js",
    "components/CreationBoard.js",
    "components/MusicGameRunner.js",
    "python/transforms/modal_mapper.py",
    "python/transforms/rhythm_density.py",
    "python/transforms/instrument_tempo.py",
}

TECHNICAL_UI_TERMS = ["OpenCode", "Basic Pitch", "API", "backend", "model", "模型", "接口", "技术路线"]
VALID_MODES = {
    "western_major",
    "western_minor",
    "chinese_pentatonic",
    "chinese_heptatonic",
    "dorian",
    "phrygian",
    "blues",
}
VALID_LISTENING_MODES = VALID_MODES | {"preserve"}
VALID_INSTRUMENTS = {"piano", "violin", "flute", "guzheng"}
VALID_LISTENING_INSTRUMENTS = VALID_INSTRUMENTS | {"preserve"}
VALID_RHYTHM_DENSITIES = {"preserve", "dense", "relaxed"}
VALID_GENERATION_MODES = {"fast", "strict"}


def _generation_mode(spec: dict[str, Any]) -> str:
    mode = str(spec.get("generation_mode") or spec.get("lesson_generation_policy", {}).get("mode") or "fast").strip().lower()
    return mode if mode in VALID_GENERATION_MODES else "fast"


def _is_fast_mode(spec: dict[str, Any]) -> bool:
    return _generation_mode(spec) == "fast"


def _is_strict_mode(spec: dict[str, Any]) -> bool:
    return _generation_mode(spec) == "strict"


def initialize_execution(
    spec: dict[str, Any],
    target_dir: Path,
    *,
    action: str,
    revision: str = "",
) -> dict[str, Any]:
    """Create the execution plan before artifact-building starts."""

    report = {
        "version": "execution-orchestrator-v1",
        "action": action,
        "created_at": _now(),
        "updated_at": _now(),
        "report_url": _relative_output_url(target_dir, target_dir / "config" / "execution-report.json"),
        "status": "running",
        "agents": EXECUTION_AGENTS,
        "plan": _execution_plan(spec, action=action, revision=revision),
        "results": {},
        "summary": "执行层多智能体协作已开始。",
    }
    _write_execution_report(target_dir, report)
    return report


def finalize_execution(
    spec: dict[str, Any],
    target_dir: Path,
    *,
    action: str,
    opencode_run: dict[str, Any],
    brain_report: dict[str, Any] | None = None,
    existing_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run execution agents after OpenCode/local rendering and persist a report."""

    report = existing_report or initialize_execution(spec, target_dir, action=action)
    report["updated_at"] = _now()
    report["opencode_status"] = opencode_run.get("status", "unknown")
    report["generation_mode"] = _generation_mode(spec)
    strict_opencode_generation = bool(opencode_run.get("enabled")) and action == "generate"
    fast_mode = _is_fast_mode(spec)
    revise_mode = action == "revise"

    frontend_result = frontend_artifact_builder_agent(spec, target_dir, opencode_run)
    music_result = music_logic_agent(spec)
    lesson_fit_result = lesson_fit_agent(spec)
    calculator_result = music_tool_calculator_agent(spec)
    code_result = code_interpreter_agent(target_dir)
    browser_result = browser_qa_agent(spec, target_dir)

    preliminary_results = {
        "frontend_artifact_builder": frontend_result,
        "music_logic_agent": music_result,
        "lesson_fit_agent": lesson_fit_result,
        "music_tool_calculator": calculator_result,
        "code_interpreter": code_result,
        "browser_qa_agent": browser_result,
        "optional_search_agent": optional_search_agent(spec),
    }
    if fast_mode and _is_playable_scaffold_artifact(spec):
        preliminary_results = _relax_fast_scaffold_validation(preliminary_results)
    if revise_mode and fast_mode:
        preliminary_results = _relax_incremental_validation(preliminary_results)
    if _should_deliver_first_page(spec, opencode_run, preliminary_results):
        preliminary_results = _relax_first_page_delivery_validation(preliminary_results)

    repair_result = repair_agent(spec, target_dir, preliminary_results, allow_page_repairs=not strict_opencode_generation)
    max_rounds = 1 if fast_mode or revise_mode else _repair_max_rounds()
    repair_attempts = [repair_result]
    for _round in range(1, max_rounds):
        if not repair_result["repairs"]:
            break
        frontend_result = frontend_artifact_builder_agent(spec, target_dir, opencode_run)
        code_result = code_interpreter_agent(target_dir)
        browser_result = browser_qa_agent(spec, target_dir)
        preliminary_results.update(
            {
                "frontend_artifact_builder": frontend_result,
                "code_interpreter": code_result,
                "browser_qa_agent": browser_result,
            }
        )
        repair_result = repair_agent(
            spec,
            target_dir,
            preliminary_results,
            round_no=_round + 1,
            allow_page_repairs=not strict_opencode_generation,
        )
        repair_attempts.append(repair_result)

    repair_result = _merge_repair_attempts(repair_attempts)

    report["results"] = {
        **preliminary_results,
        "repair_agent": repair_result,
    }
    report["brain_alignment"] = _brain_alignment(brain_report)
    report["validation_layers"] = _validation_layers(preliminary_results, repair_result, fast_mode=fast_mode)
    report["status"] = _overall_status(report["results"])
    report["summary"] = _summary_for_status(report["status"], report["results"])
    _write_execution_report(target_dir, report)

    version_result = versioning_agent(target_dir, action=action)
    report["results"] = {
        **preliminary_results,
        "repair_agent": repair_result,
        "versioning_agent": version_result,
    }
    report["status"] = _overall_status(report["results"])
    report["validation_layers"] = _validation_layers(report["results"], repair_result, fast_mode=fast_mode)
    report["summary"] = _summary_for_status(report["status"], report["results"])
    _write_execution_report(target_dir, report)
    return report


def frontend_artifact_builder_agent(
    spec: dict[str, Any],
    target_dir: Path,
    opencode_run: dict[str, Any],
) -> dict[str, Any]:
    index_path = target_dir / "index.html"
    checks: list[dict[str, Any]] = []
    content = _read_text(index_path)
    fast_mode = _is_fast_mode(spec)

    if fast_mode and _page_uses_audio_playback(content) and not _has_audio_playback_guard(content):
        audio_hardened = _repair_audio_playback_resilience(content)
        if audio_hardened != content:
            index_path.write_text(audio_hardened, encoding="utf-8")
            content = audio_hardened

    _add_check(checks, "index_exists", "index.html 存在", index_path.exists(), "生成页面文件不存在。")
    _add_check(checks, "html_complete", "HTML 结构完整", "</html>" in content.lower(), "index.html 缺少结束标签。")
    _add_check(checks, "has_title", "页面标题存在", bool(re.search(r"<title>.+?</title>", content, re.S | re.I)), "页面缺少 title。")
    _add_check(checks, "has_student_ui", "有学生可操作入口", _has_interaction(content), "页面没有发现按钮、表单、选择器或拖拽入口。")
    if _page_uses_audio_playback(content):
        _add_check(
            checks,
            "audio_guard_present",
            "页面内置音频守卫",
            _has_audio_playback_guard(content),
            "页面包含播放能力，但没有注入统一音频守卫；切后台或再次点击后可能失声。",
        )
    missing_prompt_terms, unrequested_features = _prompt_contract_alignment(content, spec)
    if missing_prompt_terms or unrequested_features:
        _add_check(
            checks,
            "prompt_contract_must_include",
            "页面保留用户原始需求",
            not missing_prompt_terms,
            "页面缺少用户提示词中的关键要素：" + "、".join(missing_prompt_terms[:8]),
            warn_only=fast_mode,
        )
        _add_check(
            checks,
            "prompt_contract_no_unrequested_features",
            "页面未加入无关大功能",
            not unrequested_features,
            "页面加入了用户未要求的大功能：" + "、".join(unrequested_features[:8]),
            warn_only=fast_mode,
        )
    music_contract = spec.get("music_logic_contract") or (
        spec.get("music_game", {}).get("music_logic_contract") if isinstance(spec.get("music_game"), dict) else {}
    )
    if isinstance(music_contract, dict) and music_contract:
        missing_music_labels, extra_music_ids = _music_contract_render_alignment(content, music_contract, spec)
        _add_check(
            checks,
            "music_contract_visible",
            "页面呈现统一音乐材料",
            not missing_music_labels,
            "页面缺少音乐材料表中的关键标签或符号：" + "、".join(missing_music_labels[:6]),
            warn_only=fast_mode,
        )
        _add_check(
            checks,
            "music_contract_no_extra_ids",
            "页面未新增契约外答案材料",
            not extra_music_ids,
            "页面疑似新增了契约外音乐材料或答案 id：" + "、".join(extra_music_ids[:8]),
            warn_only=fast_mode,
        )
    song_anchor_contract = spec.get("song_anchor_contract") if isinstance(spec.get("song_anchor_contract"), dict) else {}
    if song_anchor_contract:
        missing_song_terms = _song_anchor_render_alignment(content, song_anchor_contract)
        _add_check(
            checks,
            "song_anchor_visible",
            "页面贴合歌曲片段",
            not missing_song_terms,
            "页面没有呈现歌曲锚定材料：" + "、".join(missing_song_terms[:6]),
            warn_only=fast_mode,
        )
    template_marker_count = len(re.findall(r'data-template=["\']', content, flags=re.IGNORECASE))
    single_primary_render = _has_single_primary_activity(content, spec, template_marker_count)
    lesson_context = spec.get("lesson_context", {}) if isinstance(spec.get("lesson_context"), dict) else {}
    strict_generated_page = (
        bool(opencode_run.get("enabled"))
        and opencode_run.get("action") == "generate"
        and (bool(lesson_context) or spec.get("activity_type") == "music_game")
    )
    local_playable_ready = False
    if lesson_context:
        target_stage = str(spec.get("target_stage") or lesson_context.get("target_stage") or "")
        target_music_element = str(spec.get("target_music_element") or lesson_context.get("target_music_element") or "")
        target_objective = str(spec.get("target_objective") or lesson_context.get("target_objective") or "")
        target_segment_task = str(spec.get("target_segment_task") or lesson_context.get("target_segment_task") or "")
        playable_game = spec.get("music_game", {}).get("playable_game", {}) if isinstance(spec.get("music_game"), dict) else {}
        has_lesson_anchor = _has_lesson_anchor(content, target_stage, target_music_element, target_objective)
        _add_check(
            checks,
            "lesson_panel_visible",
            "页面显性展示课例定位",
            has_lesson_anchor,
            "页面没有显性展示课例定位，用户难以理解这个游戏为何服务该教案。",
            warn_only=fast_mode,
        )
        _add_check(
            checks,
            "lesson_constraints_visible",
            "页面可见课例约束",
            any(_text_aligns(content, token) for token in [target_stage, target_music_element, target_objective] if token),
            "页面没有把目标环节、音乐要素或课堂目标展示出来。",
            warn_only=True,
        )
        _add_check(
            checks,
            "selected_segment_visible",
            "页面呈现选中的环节任务",
            _segment_task_rendered(content, target_segment_task, target_stage, target_music_element, target_objective),
            "页面没有呈现从教案中选出的目标环节任务，可能又退化成泛化游戏。",
            warn_only=fast_mode,
        )
        _add_check(
            checks,
            "single_primary_activity",
            "课例页面只保留一个主活动",
            single_primary_render,
            "页面没有呈现为单一音乐游戏流程，可能继续堆叠多个无关模块。",
            warn_only=fast_mode,
        )
        if playable_game:
            local_playable_ready = (
                _has_playable_controls(content)
                and _has_playable_materials(content, playable_game)
                and not _has_meta_lesson_checks(content)
            )
            _add_check(
                checks,
                "playable_game_controls_present",
                "可玩任务按钮完整",
                _has_playable_controls(content),
                "教案小游戏缺少试听目标、试听我的排列、检查挑战或重来按钮。",
                warn_only=fast_mode,
            )
            _add_check(
                checks,
                "playable_game_materials_present",
                "可操作音乐材料存在",
                _has_playable_materials(content, playable_game),
                "页面没有呈现 playable_game 中的音乐材料，可能只是文字说明。",
                warn_only=fast_mode,
            )
            _add_check(
                checks,
                "playable_game_no_meta_rules",
                "学生界面不显示教师检查语",
                not _has_meta_lesson_checks(content),
                "页面把教师检查项展示给学生了，游戏规则会变得难懂。",
            )
            _add_check(
                checks,
                "student_task_brief_operational",
                "本关任务说明清楚",
                _has_operational_student_task_brief(content, playable_game),
                "页面没有清楚回答学生“听什么、做什么、怎样过关”，容易看不懂怎么玩。",
                warn_only=fast_mode,
            )
            _add_check(
                checks,
                "learning_transfer_rendered",
                "页面呈现学习迁移动作",
                _has_learning_transfer_rendered(content, playable_game),
                "页面没有呈现通关后的拍、唱、演、说、创编或演奏任务，游戏容易停留在纯玩。",
                warn_only=fast_mode,
            )
            _add_check(
                checks,
                "opencode_playable_output_applied",
                "OpenCode 真正落地了可玩产物",
                _delivery_produced_valid_page(content, spec, opencode_run),
                "OpenCode 本次没有真正写出最终页面，回退到了本地兜底页。",
                warn_only=fast_mode or not strict_generated_page,
            )
    _add_check(
        checks,
        "opencode_or_local_output",
        "生成器产生了可追踪结果",
        _delivery_produced_valid_page(content, spec, opencode_run),
        "没有检测到生成器产物变化，或已回退到本地基础页。",
        warn_only=fast_mode or not strict_generated_page,
    )
    _add_check(
        checks,
        "opencode_no_timeout_restore",
        "OpenCode 没有超时回退",
        not _is_restored_local_fallback(opencode_run) or _delivery_produced_valid_page(content, spec, opencode_run),
        "OpenCode 本次超时或无改动后回退到了本地基础页，教案小游戏不能把本地模板当作成功结果。",
        warn_only=fast_mode or not strict_generated_page,
    )
    if str(spec.get("direct_generation_route") or "") in {"template_seed_then_opencode_refine", "template_reference_then_opencode_generate"}:
        _add_check(
            checks,
            "direct_template_reference_realized",
            "直接生成已在模板参考约束下完成实际生成",
            bool(opencode_run.get("index_changed")) and not _is_restored_local_fallback(opencode_run),
            "当前结果仍停留在模板参考层或已回退到模板页；直接生成必须产出针对当前需求的实际页面，模板不能作为成功兜底结果。",
        )

    return _agent_result(
        "frontend-artifact-builder",
        checks,
        details={
            "index_path": str(index_path),
            "bytes": index_path.stat().st_size if index_path.exists() else 0,
            "activity_type": spec.get("activity_type", "mixed"),
            "template_marker_count": template_marker_count,
            "single_primary_render": single_primary_render,
            "changed_files": opencode_run.get("changed_files", []),
            "index_changed": opencode_run.get("index_changed"),
            "restored_fallback": opencode_run.get("restored_fallback"),
            "missing_required_artifact": opencode_run.get("missing_required_artifact"),
        },
    )


def _has_single_primary_activity(content: str, spec: dict[str, Any], template_marker_count: int) -> bool:
    """Accept both our template renderer and OpenCode-authored one-game pages."""

    if "renderMainActivity()" in content and "renderLessonBrief() + renderMainActivity()" in content:
        return True

    activity_type = str(spec.get("activity_type") or "")
    if activity_type != "music_game":
        return template_marker_count <= 1

    lowered = content.lower()
    generated_template_markers = [
        "data-template=\"template_listen\"",
        "data-template='template_listen'",
        "data-template=\"template_performance\"",
        "data-template='template_performance'",
        "data-template=\"template_creation\"",
        "data-template='template_creation'",
    ]
    if sum(1 for marker in generated_template_markers if marker in lowered) > 1:
        return False

    unrelated_module_signals = [
        ("listening", ["name=\"audio\"", "element_control_panel", "生成对比版本"]),
        ("performance", ["level-progress", "data-level-index", "通关进度"]),
        ("creation", ["creation-grid", "puzzle-palette", "旋律线"]),
    ]
    active_unrelated_modules = 0
    for _module_name, signals in unrelated_module_signals:
        if any(signal.lower() in lowered for signal in signals):
            active_unrelated_modules += 1

    if active_unrelated_modules >= 2:
        return False

    game_signals = [
        "开始挑战",
        "播放验证",
        "重新挑战",
        "再玩一次",
        "游戏规则",
        "挑战结果",
        "试听目标",
        "试听我的排列",
        "检查挑战",
        "重来",
    ]
    lesson_context = spec.get("lesson_context", {}) if isinstance(spec.get("lesson_context"), dict) else {}
    has_lesson_panel = _has_lesson_anchor(
        content,
        str(spec.get("target_stage") or lesson_context.get("target_stage") or ""),
        str(spec.get("target_music_element") or lesson_context.get("target_music_element") or ""),
        str(spec.get("target_objective") or lesson_context.get("target_objective") or ""),
    )
    if _has_playable_controls(content):
        return has_lesson_panel

    has_game_flow = sum(1 for signal in game_signals if signal in content) >= 2
    return has_game_flow and has_lesson_panel


def _has_lesson_anchor(content: str, target_stage: str, target_music_element: str, target_objective: str) -> bool:
    if 'data-lesson-panel="true"' in content or "课例定位" in content or "本关任务" in content:
        return True
    tokens = [token for token in [target_stage, target_music_element, target_objective] if token]
    return sum(1 for token in tokens if _text_aligns(content, token)) >= 2


def _segment_task_rendered(
    content: str,
    target_segment_task: str,
    target_stage: str,
    target_music_element: str,
    target_objective: str,
) -> bool:
    if not target_segment_task:
        return False
    if _text_aligns(content, target_segment_task):
        return True

    visible = _student_visible_text(content)
    key_terms = [
        term
        for term in re.split(r"[，。、；：:、“”\"'\s]+", target_segment_task)
        if len(term) >= 2 and term not in {"重点解决", "学生", "能够", "可以"}
    ]
    if sum(1 for term in key_terms if _text_aligns(visible, term)) >= 2:
        return True

    action_pairs = [
        ("听辨", ["听辨", "听：", "试听", "聆听"]),
        ("排序", ["排序", "顺序", "排回"]),
        ("理由", ["理由", "说出", "说一说", "为什么"]),
        ("重复", ["重复"]),
        ("对比", ["对比"]),
    ]
    action_hits = 0
    for source, rendered_options in action_pairs:
        if source in target_segment_task or source in target_objective:
            action_hits += int(any(option in visible for option in rendered_options))

    anchors = [token for token in [target_stage, target_music_element] if token]
    anchor_hits = sum(1 for token in anchors if _text_aligns(visible, token))
    return anchor_hits >= 1 and action_hits >= 2


def _has_playable_controls(content: str) -> bool:
    required = ["试听目标", "试听我的排列", "检查挑战", "重来"]
    return all(text in content for text in required) and any(token in content.lower() for token in ["addeventlistener", "onclick"])


def _is_restored_local_fallback(opencode_run: dict[str, Any]) -> bool:
    status = str(opencode_run.get("status") or "")
    return status.endswith("_restored") and not bool(opencode_run.get("artifact_changed"))


def _opencode_produced_artifact(opencode_run: dict[str, Any]) -> bool:
    if not bool(opencode_run.get("enabled")):
        return opencode_run.get("status") == "skipped"
    if _is_restored_local_fallback(opencode_run):
        return False
    if opencode_run.get("action") == "generate" and not bool(opencode_run.get("index_changed")):
        return False
    status = str(opencode_run.get("status") or "")
    return bool(opencode_run.get("artifact_changed")) and status in {
        "completed",
        "failed_with_artifact",
        "timeout_with_artifact",
    }


def _delivery_produced_valid_page(content: str, spec: dict[str, Any], opencode_run: dict[str, Any]) -> bool:
    if _opencode_produced_artifact(opencode_run):
        return True
    if str(spec.get("direct_generation_route") or "") in {"template_seed_then_opencode_refine", "template_reference_then_opencode_generate"}:
        return False
    lesson_context = spec.get("lesson_context", {}) if isinstance(spec.get("lesson_context"), dict) else {}
    if (
        bool(opencode_run.get("enabled"))
        and opencode_run.get("action") == "generate"
        and (bool(lesson_context) or spec.get("activity_type") == "music_game")
    ):
        return False
    if not _is_restored_local_fallback(opencode_run):
        return False
    if not _has_interaction(content):
        return False
    if spec.get("activity_type") == "music_game":
        return _has_lesson_anchor(
            content,
            str(spec.get("target_stage") or lesson_context.get("target_stage") or ""),
            str(spec.get("target_music_element") or lesson_context.get("target_music_element") or ""),
            str(spec.get("target_objective") or lesson_context.get("target_objective") or ""),
        )
    return True


def _has_playable_materials(content: str, playable_game: dict[str, Any]) -> bool:
    materials = playable_game.get("materials", []) if isinstance(playable_game, dict) else []
    labels = [
        str(item.get("label", "")).strip()
        for item in materials
        if isinstance(item, dict) and str(item.get("label", "")).strip()
    ]
    return bool(labels) and all(label in content for label in labels[:6])


def _html_tag_balance(content: str, tag_name: str) -> bool:
    if not content.strip():
        return True

    class _BalanceParser(HTMLParser):
        def __init__(self, tracked_tag: str) -> None:
            super().__init__()
            self.tracked_tag = tracked_tag
            self.opens = 0
            self.closes = 0

        def handle_starttag(self, tag: str, attrs) -> None:  # type: ignore[override]
            if tag.lower() == self.tracked_tag:
                self.opens += 1

        def handle_endtag(self, tag: str) -> None:  # type: ignore[override]
            if tag.lower() == self.tracked_tag:
                self.closes += 1

    parser = _BalanceParser(tag_name.lower())
    try:
        parser.feed(content)
        parser.close()
    except Exception:
        lowered = content.lower()
        return lowered.count(f"<{tag_name.lower()}") == lowered.count(f"</{tag_name.lower()}>")
    return parser.opens == parser.closes


def _has_meta_lesson_checks(content: str) -> bool:
    visible = re.sub(r"<script\b[^>]*>.*?</script>", "", content, flags=re.I | re.S)
    visible = re.sub(r"<style\b[^>]*>.*?</style>", "", visible, flags=re.I | re.S)
    return any(marker in visible for marker in ["是否服务于", "是否真正聚焦", "不是泛泛", "脱离教案单独玩游戏"])


def _has_operational_student_task_brief(content: str, playable_game: dict[str, Any]) -> bool:
    if "本关任务" not in content:
        return False
    visible = _student_visible_text(content)
    structural_signals = ["我听什么", "我做什么", "怎样算过关", "听：", "做：", "过关：", "试听目标", "检查挑战"]
    signal_count = sum(1 for signal in structural_signals if signal in visible)
    raw_signal_count = sum(1 for signal in ["本关任务", "听：", "做：", "过关：", "试听目标", "检查挑战"] if signal in content)
    task = playable_game.get("student_facing_task", {}) if isinstance(playable_game.get("student_facing_task"), dict) else {}
    task_terms = [
        str(value).strip("。")
        for value in task.values()
        if isinstance(value, str) and len(str(value).strip()) >= 3
    ]
    term_count = sum(1 for term in task_terms if _text_aligns(visible, term))
    renderer_has_brief = all(
        marker in content
        for marker in ["renderStudentGameBrief", "本关任务", "听：", "做：", "过关："]
    )
    return signal_count >= 3 or term_count >= 2 or raw_signal_count >= 4 or renderer_has_brief


def _has_learning_transfer_rendered(content: str, playable_game: dict[str, Any]) -> bool:
    visible = _student_visible_text(content)
    transfer = playable_game.get("learning_transfer", {}) if isinstance(playable_game.get("learning_transfer"), dict) else {}
    transfer_text = str(transfer.get("classroom_transfer") or "")
    if transfer_text and _text_aligns(visible, transfer_text):
        return True
    return any(keyword in visible for keyword in ["拍", "唱", "演", "说", "动作", "表现", "创编", "模唱", "跟唱", "律动", "演奏"])


def _playable_has_learning_loop(playable_game: dict[str, Any]) -> bool:
    if not isinstance(playable_game, dict) or not playable_game:
        return False
    transfer = playable_game.get("learning_transfer", {})
    if not isinstance(transfer, dict):
        return False
    required = ["listen_target", "music_evidence", "student_operation", "classroom_transfer"]
    if not all(transfer.get(key) for key in required):
        return False
    evidence = transfer.get("music_evidence")
    return isinstance(evidence, list) and any(str(item).strip() for item in evidence)


def _playable_has_music_evidence(playable_game: dict[str, Any], target_music_element: str, lesson_evidence: str) -> bool:
    if not isinstance(playable_game, dict) or not playable_game:
        return False
    transfer = playable_game.get("learning_transfer", {})
    evidence_text = ""
    if isinstance(transfer, dict):
        evidence_text = " ".join(str(item) for item in transfer.get("music_evidence", []) if str(item).strip())
    materials = playable_game.get("materials", []) if isinstance(playable_game.get("materials"), list) else []
    material_text = " ".join(
        " ".join(
            [
                str(item.get("label", "")),
                str(item.get("music_value", "")),
                str(item.get("feedback", "")),
                str(item.get("evidence_role", "")),
                str(item.get("teaching_role", "")),
            ]
        )
        for item in materials
        if isinstance(item, dict)
    )
    combined = " ".join([evidence_text, material_text, str(target_music_element), str(lesson_evidence)])
    music_keywords = [
        "音",
        "唱名",
        "音高",
        "旋律",
        "节奏",
        "拍",
        "时值",
        "重音",
        "休止",
        "乐句",
        "乐段",
        "重复",
        "对比",
        "呼应",
        "力度",
        "速度",
        "音色",
        "演唱",
        "情绪",
        "动作",
        "调式",
        "五声",
        "证据",
    ]
    has_evidence_text = any(keyword in combined for keyword in music_keywords)
    has_playable_sound = any(
        isinstance(item, dict)
        and (
            bool(item.get("audio_clip_url"))
            or bool(item.get("playback_tokens"))
            or isinstance(item.get("pitch"), int)
            or isinstance(item.get("duration"), (int, float))
        )
        for item in materials
    )
    return has_evidence_text and has_playable_sound


def _playable_has_classroom_transfer(playable_game: dict[str, Any]) -> bool:
    if not isinstance(playable_game, dict) or not playable_game:
        return False
    transfer = playable_game.get("learning_transfer", {})
    text = ""
    if isinstance(transfer, dict):
        text += " " + str(transfer.get("classroom_transfer", ""))
    text += " " + " ".join(str(item) for item in playable_game.get("required_student_actions", []) if str(item).strip())
    feedback = playable_game.get("feedback", {})
    if isinstance(feedback, dict):
        text += " " + " ".join(str(item) for item in feedback.values())
    return any(keyword in text for keyword in ["拍", "唱", "演", "说", "动作", "表现", "创编", "模唱", "跟唱", "律动", "演奏"])


def _prompt_contract_alignment(content: str, spec: dict[str, Any]) -> tuple[list[str], list[str]]:
    contract = spec.get("user_prompt_contract", {}) if isinstance(spec.get("user_prompt_contract"), dict) else {}
    if not contract:
        return [], []
    must_include = _clean_contract_terms(contract.get("must_include", []))
    must_not_include = _clean_contract_terms(contract.get("must_not_include", []))
    if not must_include and not must_not_include:
        return [], []

    visible = _student_visible_text(content)
    hard_terms = [term for term in must_include if _is_hard_prompt_term(term, spec)]
    missing = [term for term in hard_terms if not _contract_term_satisfied(content, term, spec)]
    unrequested = [term for term in must_not_include if _text_aligns(visible, term)]
    return missing, unrequested


def _is_hard_prompt_term(term: str, spec: dict[str, Any]) -> bool:
    """Only block on terms that define the current generated artifact.

    The prompt contract often contains background words copied from the full lesson
    plan. Those should guide the page, but they should not fail a playable artifact
    when the selected lesson focus is narrower.
    """

    term = str(term or "").strip()
    if not term:
        return False
    lesson_context = spec.get("lesson_context", {}) if isinstance(spec.get("lesson_context"), dict) else {}
    anchors = [
        spec.get("song_name", ""),
        spec.get("title", ""),
        spec.get("target_music_element", ""),
        spec.get("target_stage", ""),
        lesson_context.get("song_name", ""),
        lesson_context.get("target_music_element", ""),
        lesson_context.get("target_stage", ""),
    ]
    if any(_text_aligns(str(anchor), term) or _text_aligns(term, str(anchor)) for anchor in anchors if anchor):
        return True
    gameplay_terms = {"拖拽", "点击", "播放", "试听", "排序", "排列", "匹配", "配对", "重来", "反馈", "挑战"}
    if term in gameplay_terms:
        return True
    return False


def _contract_term_satisfied(content: str, term: str, spec: dict[str, Any]) -> bool:
    if _text_aligns(content, term):
        return True
    target_music_element = str(spec.get("target_music_element", "") or "").strip()
    if target_music_element and target_music_element in term and _text_aligns(content, target_music_element):
        return True
    if term.startswith("围绕") and target_music_element and _text_aligns(content, target_music_element):
        return True
    context = " ".join(
        [
            str(spec.get("grade_band", "")),
            str(spec.get("original_user_need", "")),
            str(spec.get("visual_theme", {})),
        ]
    )
    if term in {"小学", "初中", "高中", "一年级", "二年级", "三年级", "四年级", "五年级", "六年级"}:
        return _text_aligns(context, term)
    if term == "时值":
        return any(token in content for token in ["全音符", "二分音符", "四分音符", "八分音符", "拍"])
    if term == "星级":
        return any(token in content for token in ["星级", "星星", "⭐", "★", "stars", "star"])
    if term == "匹配":
        return any(token in content for token in ["匹配", "配对", "拼回", "成组", "连线", "对应"])
    if term == "配对":
        return any(token in content for token in ["匹配", "配对", "成组", "连线", "对应"])
    if term == "旋律":
        return any(token in content for token in ["旋律", "乐句", "唱", "音高", "歌声"])
    if term == "音高":
        return any(token in content for token in ["音高", "唱名", "旋律", "乐句", "高低"])
    if term == "拖拽":
        return any(token in content for token in ["拖拽", "拖动", "拖卡片", "拖唱名", "拖到", "拖进", "拖回"])
    if term == "点击":
        lower = content.lower()
        return any(token in content for token in ["点击", "点按", "按下", "轻触"]) or any(
            token in lower
            for token in ["addeventlistener('click'", 'addeventlistener("click"', ".onclick", "onclick="]
        )
    return False


def _clean_contract_terms(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    cleaned: list[str] = []
    for item in value:
        text = str(item or "").strip()
        if text and text not in cleaned:
            cleaned.append(text)
    return cleaned


def _student_visible_text(content: str) -> str:
    visible = re.sub(r"<script\b[^>]*>.*?</script>", "", content, flags=re.I | re.S)
    visible = re.sub(r"<style\b[^>]*>.*?</style>", "", visible, flags=re.I | re.S)
    visible = re.sub(r"<[^>]+>", " ", visible)
    return re.sub(r"\s+", " ", visible).strip()


def _long_student_text_blocks(content: str, *, limit: int = 86) -> list[str]:
    visible_html = re.sub(r"<script\b[^>]*>.*?</script>", "", content, flags=re.I | re.S)
    visible_html = re.sub(r"<style\b[^>]*>.*?</style>", "", visible_html, flags=re.I | re.S)
    blocks: list[str] = []
    tag_limits = {
        "h1": 34,
        "h2": 38,
        "h3": 42,
        "h4": 42,
        "button": 30,
        "label": 34,
        "summary": 44,
        "p": limit,
        "li": 72,
        "small": 58,
        "em": 58,
    }
    for tag, tag_limit in tag_limits.items():
        pattern = rf"<{tag}\b[^>]*>(.*?)</{tag}>"
        for raw in re.findall(pattern, visible_html, flags=re.I | re.S):
            text = re.sub(r"<[^>]+>", " ", raw)
            text = re.sub(r"\s+", " ", html_unescape(text)).strip()
            if len(text) > tag_limit and not _looks_like_control_option_dump(text):
                blocks.append(f"{tag}: {short_text(text, 54)}")
    return blocks[:6]


def _student_copy_density(content: str) -> int:
    visible = _student_visible_text(content)
    return len(re.sub(r"\s+", "", visible))


def _student_copy_density_limit(spec: dict[str, Any]) -> int:
    activity_type = str(spec.get("activity_type") or "mixed")
    if activity_type == "listening":
        return 2200
    if activity_type == "mixed":
        return 1900
    return 1550


def _looks_like_control_option_dump(text: str) -> bool:
    option_tokens = ["调式", "音色", "小节", "声部", "保持", "选择"]
    return len(text) > 120 and sum(1 for token in option_tokens if token in text) >= 3


def _has_large_student_modules(content: str, browser_details: dict[str, Any]) -> bool:
    if browser_details.get("mode") == "playwright":
        if int(browser_details.get("large_interactive_count") or 0) >= 2:
            return True
        if int(browser_details.get("largest_interactive_area") or 0) >= 28000:
            return True

    lower = content.lower()
    has_large_css = any(
        marker in lower
        for marker in [
            "min-height: 138px",
            "min-height: 170px",
            "min-height: 260px",
            "min-height:138px",
            "min-height:170px",
            "min-height:260px",
            "height: 420px",
            "min-height: 56px",
            "min-height: 100px",
            "min-height:56px",
            "min-height:100px",
            "width: 80px",
            "height: 80px",
            "min-width: 120px",
            "min-width:120px",
        ]
    )
    has_primary_module = any(
        marker in lower
        for marker in [
            "playable-mission",
            "playable-target",
            "drop-zone",
            "game-lane",
            "quest-panel",
            "melody-canvas",
            "data-playable-mission",
            "cardpool",
            "card-pool",
            "challengezone",
            "challenge-zone",
            "class=\"zone\"",
            "class='zone'",
            ".card",
            ".note-card",
            ".slot",
            ".drop-slot",
            "touch-action: none",
        ]
    )
    return has_large_css and has_primary_module


def _has_above_fold_student_action(content: str, browser_details: dict[str, Any]) -> bool:
    if browser_details.get("mode") == "playwright" and browser_details.get("opened"):
        if int(browser_details.get("above_fold_interactive_count") or 0) >= 1:
            return True
        if int(browser_details.get("largest_above_fold_interactive_area") or 0) >= 18000:
            return True

    lower = content.lower()
    return any(
        marker in lower
        for marker in [
            "hero-actions",
            "play-panel",
            "game-board",
            "main-stage",
            "student-stage",
            "quest-panel",
            "controls",
            "start-overlay",
            "start-box",
            "btn-start",
            "game-area",
            "challenge-zone",
            "card-pool",
            "btn-play",
            "action-row",
            "note-card",
            "drop-slot",
        ]
    ) and any(token in content for token in ["开始", "播放", "试听", "重来", "挑战"])


def _requires_student_controls(spec: dict[str, Any]) -> bool:
    activity_type = str(spec.get("activity_type") or "")
    if activity_type in {"listening", "performance", "creation", "music_game", "mixed"}:
        return True
    return any(
        isinstance(spec.get(module), dict) and spec[module].get("enabled")
        for module in ["listening", "performance", "creation", "music_game"]
    )


def _reset_warn_only(spec: dict[str, Any]) -> bool:
    return str(spec.get("activity_type") or "") == "listening"


def _music_contract_render_alignment(content: str, contract: dict[str, Any], spec: dict[str, Any] | None = None) -> tuple[list[str], list[str]]:
    tokens = contract.get("tokens", []) if isinstance(contract.get("tokens"), list) else []
    if not tokens:
        return ["音乐材料表"], []
    visible = _student_visible_text(content)
    missing: list[str] = []
    allowed_ids: set[str] = set()

    def add_allowed(value: Any) -> None:
        text = str(value or "").strip()
        if text:
            allowed_ids.add(text)

    for token in tokens:
        if not isinstance(token, dict):
            continue
        token_id = str(token.get("id", "")).strip()
        add_allowed(token_id)
        label = str(token.get("label", "")).strip()
        add_allowed(label)
        symbol = str(token.get("symbol", "")).strip()
        add_allowed(symbol)
        fallback = str(token.get("fallback_symbol", "")).strip()
        add_allowed(fallback)
        music_value = str(token.get("music_value", "")).strip()
        add_allowed(music_value)
        if label and (_text_aligns(visible, label) or _text_aligns(content, label)):
            continue
        if symbol and (symbol in visible or symbol in content):
            continue
        if fallback and (fallback in visible or fallback in content):
            continue
        if music_value and (_text_aligns(visible, music_value) or _text_aligns(content, music_value)):
            continue
        if label:
            missing.append(label)
    spec = spec or {}
    for token_id in _song_material_ids_from_spec(spec):
        allowed_ids.add(token_id)

    known_generated_ids = {
        "whole",
        "half",
        "quarter",
        "eighth",
        "turtle",
        "bear",
        "deer",
        "rabbit",
        "cat",
        "dog",
        "up",
        "down",
        "same",
        "sol",
        "mi",
        "do",
        "re",
        "gong",
        "shang",
        "jue",
        "zhi",
        "yu",
    }
    explicit_material_patterns = [
        r"""data-(?:id|note|note-id|material|material-id)=["']([A-Za-z][A-Za-z0-9_-]{1,30})["']""",
        r"""["'](?:id|noteId|materialId)["']\s*:\s*["']([A-Za-z][A-Za-z0-9_-]{1,30})["']""",
        r"""\b(?:id|noteId|materialId)\s*:\s*["']([A-Za-z][A-Za-z0-9_-]{1,30})["']""",
    ]
    quoted_ids: set[str] = set()
    for pattern in explicit_material_patterns:
        quoted_ids.update(re.findall(pattern, content, flags=re.IGNORECASE))
    extra = sorted(item for item in quoted_ids if item in known_generated_ids and item not in allowed_ids)
    return missing, extra


def _song_material_ids_from_spec(spec: dict[str, Any]) -> set[str]:
    ids: set[str] = set()

    def add(value: Any) -> None:
        text = str(value or "").strip()
        if text:
            ids.add(text)

    music_game = spec.get("music_game", {}) if isinstance(spec.get("music_game"), dict) else {}
    playable = music_game.get("playable_game", {}) if isinstance(music_game.get("playable_game"), dict) else {}
    phrase_table = playable.get("song_phrase_table", {}) if isinstance(playable.get("song_phrase_table"), dict) else {}
    for value in phrase_table.get("target_sequence", []) if isinstance(phrase_table.get("target_sequence"), list) else []:
        add(value)
    for token in phrase_table.get("playback_tokens", []) if isinstance(phrase_table.get("playback_tokens"), list) else []:
        if isinstance(token, dict):
            add(token.get("id"))

    song_anchor = spec.get("song_anchor_contract", {}) if isinstance(spec.get("song_anchor_contract"), dict) else {}
    selected_phrase = song_anchor.get("selected_phrase", {}) if isinstance(song_anchor.get("selected_phrase"), dict) else {}
    for value in selected_phrase.get("target_sequence", []) if isinstance(selected_phrase.get("target_sequence"), list) else []:
        add(value)
    for token in selected_phrase.get("main_melody", []) if isinstance(selected_phrase.get("main_melody"), list) else []:
        if isinstance(token, dict):
            add(token.get("id"))
    return ids


def _song_anchor_render_alignment(content: str, contract: dict[str, Any]) -> list[str]:
    visible = _student_visible_text(content)
    phrase = contract.get("selected_phrase", {}) if isinstance(contract.get("selected_phrase"), dict) else {}
    required_terms = [
        str(contract.get("song_title", "")).strip(),
        str(phrase.get("label", "")).strip(),
    ]
    missing = []
    for term in [item for item in required_terms if item]:
        if _text_aligns(visible, term) or _text_aligns(content, term):
            continue
        missing.append(term)
    return missing


def music_logic_agent(spec: dict[str, Any]) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    activity_type = spec.get("activity_type", "mixed")
    listening = spec.get("listening", {})
    performance = spec.get("performance", {})
    creation = spec.get("creation", {})
    music_game = spec.get("music_game", {})
    activity_type_lock = spec.get("activity_type_lock", {}) if isinstance(spec.get("activity_type_lock"), dict) else {}

    if activity_type_lock.get("enabled"):
        expected_type = str(activity_type_lock.get("activity_type") or "")
        actual_modules = [
            module
            for module, payload in [
                ("listening", listening),
                ("performance", performance),
                ("creation", creation),
                ("music_game", music_game),
            ]
            if isinstance(payload, dict) and payload.get("enabled")
        ]
        expected_modules = activity_type_lock.get("active_modules", [])
        _add_check(
            checks,
            "activity_type_lock_respected",
            "生成目标锁未被改写",
            activity_type == expected_type and actual_modules == expected_modules,
            f"生成目标锁要求 {expected_type}/{expected_modules}，实际为 {activity_type}/{actual_modules}。",
        )

    if listening.get("enabled"):
        _add_check(checks, "mode_valid", "聆听调式有效", listening.get("mode") in VALID_LISTENING_MODES, "聆听调式不在支持列表中。")
        _add_check(
            checks,
            "tempo_range",
            "速度倍率合理",
            0.5 <= float(listening.get("tempo_multiplier", 1.0)) <= 2.0,
            "速度倍率应在 0.5 到 2.0 之间。",
        )
        _add_check(
            checks,
            "instrument_valid",
            "音色有效",
            listening.get("instrument") in VALID_LISTENING_INSTRUMENTS,
            "音色不在支持列表中。",
            warn_only=True,
        )
        _add_check(
            checks,
            "rhythm_density_valid",
            "节奏控制有效",
            listening.get("rhythm_density", "preserve") in VALID_RHYTHM_DENSITIES,
            "节奏控制应为保持原节奏、更密集或更舒缓。",
        )

    if performance.get("enabled"):
        levels = performance.get("levels", [])
        _add_check(checks, "levels_present", "表现关卡足够", isinstance(levels, list) and len(levels) >= 3, "表现活动至少需要 3 个关卡。")
        _add_check(
            checks,
            "levels_have_rules",
            "关卡有任务和规则",
            all(level.get("student_task") and level.get("success_rule") for level in levels if isinstance(level, dict)),
            "至少有一个关卡缺少学生任务或通关规则。",
        )

    if creation.get("enabled"):
        pieces = creation.get("pieces", [])
        _add_check(checks, "creation_mode_valid", "创造调式有效", creation.get("mode") in VALID_MODES, "创造调式不在支持列表中。")
        _add_check(checks, "pieces_present", "创作素材足够", isinstance(pieces, list) and len(pieces) >= 4, "创造活动至少需要 4 个素材。")
        _add_check(
            checks,
            "bars_range",
            "小节数适合课堂",
            2 <= int(creation.get("bars", 4)) <= 8,
            "创造活动小节数建议在 2 到 8 之间。",
            warn_only=True,
        )

    if music_game.get("enabled"):
        _add_check(checks, "game_rules_present", "小游戏规则完整", bool(music_game.get("rules")), "小游戏缺少音乐规则。")
        _add_check(checks, "game_actions_present", "小游戏动作明确", bool(music_game.get("student_actions")), "小游戏缺少学生操作。")
        _add_check(checks, "game_win_condition", "小游戏有胜利条件", bool(music_game.get("win_condition")), "小游戏缺少胜利条件。")
        playable_game = music_game.get("playable_game", {}) if isinstance(music_game.get("playable_game"), dict) else {}
        music_contract = spec.get("music_logic_contract") or music_game.get("music_logic_contract") or {}
        contract_errors = validate_music_logic_contract(music_contract, playable_game)
        song_anchor_contract = spec.get("song_anchor_contract") or music_game.get("song_anchor_contract") or {}
        song_anchor_errors = validate_song_anchor_contract(song_anchor_contract) if isinstance(song_anchor_contract, dict) else []
        _add_check(
            checks,
            "music_logic_contract_present",
            "存在统一音乐逻辑表",
            bool(music_contract) and not contract_errors,
            "音乐逻辑契约无效：" + "；".join(contract_errors[:4]),
        )
        if song_anchor_contract:
            _add_check(
                checks,
                "song_anchor_contract_valid",
                "歌曲片段锚定有效",
                not song_anchor_errors,
                "歌曲锚定契约需要确认：" + "；".join(song_anchor_errors[:4]),
                warn_only=all("元数据" in item for item in song_anchor_errors),
            )
        if spec.get("lesson_context"):
            _add_check(
                checks,
                "lesson_game_playable_spec_present",
                "教案游戏有可执行规格",
                bool(playable_game.get("materials")) and bool(playable_game.get("target_sequence")),
                "上传教案生成的音乐游戏不能只给文字规则，必须包含可操作材料和目标序列。",
            )

    if activity_type in {"performance", "creation", "music_game"}:
        runtime = spec.get("runtime_behaviors", {})
        _add_check(
            checks,
            "no_forced_audio_upload",
            "非聆听活动不强制上传音频",
            not bool(runtime.get("requires_audio_upload")),
            "非聆听活动不应强制上传音频。",
        )

    education_fit = evaluate_music_education_fit(spec)
    _add_check(
        checks,
        "grade_ability_fit",
        "符合年级能力分层",
        education_fit["score"] >= 76,
        f"音乐教育知识库适配得分 {education_fit['score']}，需要补充学段支架、曲目重点或课程素养。",
        warn_only=True,
    )
    _add_check(
        checks,
        "curriculum_anchor_present",
        "关联课程标准锚点",
        bool(education_fit.get("curriculum_anchors")),
        "没有可用课程标准锚点。",
        warn_only=True,
    )

    return _agent_result(
        "music-logic-agent",
        checks,
        details={
            "activity_type": activity_type,
            "education_fit": education_fit,
        },
    )


def lesson_fit_agent(spec: dict[str, Any]) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    fast_mode = _is_fast_mode(spec)
    lesson_context = spec.get("lesson_context", {}) if isinstance(spec.get("lesson_context"), dict) else {}
    music_game = spec.get("music_game", {}) if isinstance(spec.get("music_game"), dict) else {}
    teacher_notes = " ".join(str(note) for note in spec.get("teacher_notes", []))
    subtitle = str(spec.get("subtitle", ""))
    has_lesson_contract = bool(
        lesson_context
        or spec.get("lesson_middle_layer")
        or spec.get("target_stage")
        or spec.get("target_objective")
        or spec.get("target_music_element")
        or spec.get("selected_game_segment")
        or spec.get("goal_task_game_mapping")
    )

    if not has_lesson_contract:
        _add_check(
            checks,
            "lesson_fit_not_required",
            "非教案生成任务不强制课例贴合检查",
            True,
            "当前不是上传教案生成游戏链路，不需要课例中间层。",
        )
        return _agent_result(
            "lesson-fit-agent",
            checks,
            details={
                "lesson_fit_score": 100,
                "skipped_reason": "no_lesson_context",
                "activity_type": spec.get("activity_type", "mixed"),
            },
        )

    target_stage = str(spec.get("target_stage") or lesson_context.get("target_stage") or "")
    target_objective = str(spec.get("target_objective") or lesson_context.get("target_objective") or "")
    target_music_element = str(spec.get("target_music_element") or lesson_context.get("target_music_element") or "")
    lesson_evidence = str(spec.get("lesson_evidence") or lesson_context.get("lesson_evidence") or "")
    selected_segment = spec.get("selected_game_segment") or lesson_context.get("selected_game_segment") or {}
    goal_mapping = spec.get("goal_task_game_mapping") or lesson_context.get("goal_task_game_mapping") or []
    quality_gates = spec.get("lesson_quality_gates") or lesson_context.get("quality_gates") or {}
    mechanic_rule = spec.get("music_element_mechanic") or lesson_context.get("music_element_mechanic") or {}
    prompt_chain = spec.get("lesson_prompt_chain") or lesson_context.get("prompt_chain") or []
    musical_contract = spec.get("musical_game_logic_contract") or lesson_context.get("musical_game_logic_contract") or {}
    song_anchor_contract = spec.get("song_anchor_contract") or lesson_context.get("song_anchor_contract") or {}
    target_segment_task = str(spec.get("target_segment_task") or lesson_context.get("target_segment_task") or "")
    target_segment_gameable_point = str(
        spec.get("target_segment_gameable_point") or lesson_context.get("target_segment_gameable_point") or ""
    )
    teacher_guidance = spec.get("teacher_guidance") or lesson_context.get("teacher_guidance") or []
    assessment_closure = str(spec.get("assessment_closure") or lesson_context.get("assessment_closure") or "")
    fit_reason = str(spec.get("why_this_game_fits_this_lesson") or lesson_context.get("why_this_game_fits_this_lesson") or "")
    playable_game = music_game.get("playable_game", {}) if isinstance(music_game.get("playable_game"), dict) else {}
    singing_like = any(
        keyword in " ".join([target_objective, target_segment_task, target_music_element, fit_reason])
        for keyword in ["学唱", "演唱", "唱会", "跟唱", "模唱", "乐句", "歌曲表现"]
    )
    phrase_expression_source = " ".join([target_objective, target_segment_task, target_music_element, lesson_evidence])
    operation_type = str(playable_game.get("operation_type", "")) if isinstance(playable_game, dict) else ""
    phrase_expression_like = operation_type in {
        "song_phrase_expression_match",
        "phrase_call_response_match",
        "section_contrast_order",
        "phrase_structure_order",
    } or any(
        keyword in phrase_expression_source
        for keyword in ["A段", "B段", "乐段", "情绪", "断连", "温馨", "欢快", "跳跃", "连贯", "演唱方法", "声音表现"]
    )

    _add_check(checks, "lesson_context_present", "存在课例中间层", bool(lesson_context), "缺少课例中间层，页面可能退化成通用小游戏。")
    _add_check(checks, "target_stage_present", "目标环节明确", bool(target_stage), "没有指定游戏要落在哪个教学环节。")
    _add_check(checks, "target_objective_present", "目标任务明确", bool(target_objective), "没有指定该环节要解决的课堂目标。")
    _add_check(checks, "target_music_element_present", "具体音乐要素明确", bool(target_music_element), "没有锁定具体音乐要素，容易生成泛化网页。")
    _add_check(checks, "lesson_evidence_present", "有教案依据", bool(lesson_evidence), "没有保留来自教案的依据句。")
    _add_check(checks, "selected_segment_present", "选中主游戏环节", bool(selected_segment), "没有选中一个主游戏环节，下游容易把多个预设模块堆在一起。")
    _add_check(checks, "target_segment_task_present", "环节任务明确", bool(target_segment_task), "没有把教案中的环节任务传给生成器。")
    _add_check(
        checks,
        "target_segment_gameable_point_present",
        "游戏化切入点明确",
        bool(target_segment_gameable_point),
        "没有说明这个教学环节为什么适合转成小游戏。",
    )
    _add_check(checks, "goal_task_mapping_present", "存在目标-环节映射", bool(goal_mapping), "缺少整课目标与环节任务的映射。")
    _add_check(checks, "prompt_chain_present", "存在设计提示链", bool(prompt_chain), "缺少规则化提示链，后续修改可能重新变成随意生成。")
    _add_check(
        checks,
        "music_mechanic_mapping_present",
        "存在音乐要素到游戏机制映射",
        bool(mechanic_rule.get("mechanism_id")),
        "缺少音乐要素到游戏机制的映射，玩法可能与学习内容脱节。",
    )
    _add_check(
        checks,
        "musical_logic_contract_present",
        "存在音乐性闭环约束",
        bool(musical_contract.get("non_negotiables")),
        "缺少音乐性闭环约束，容易生成只有拖拽外壳、没有音乐学习逻辑的游戏。",
        warn_only=True,
    )
    _add_check(
        checks,
        "playable_learning_loop_present",
        "游戏具备学习闭环",
        _playable_has_learning_loop(playable_game),
        "playable_game 缺少“听什么、根据什么音乐证据判断、操作后迁移到什么课堂表现”的通用学习闭环。",
        warn_only=fast_mode,
    )
    _add_check(
        checks,
        "playable_music_evidence_present",
        "游戏判定依赖音乐证据",
        _playable_has_music_evidence(playable_game, target_music_element, lesson_evidence),
        "游戏材料或学习闭环没有明确音乐证据，容易变成普通拖拽或文字规则页面。",
        warn_only=fast_mode,
    )
    _add_check(
        checks,
        "playable_classroom_transfer_present",
        "通关后回到课堂学习任务",
        _playable_has_classroom_transfer(playable_game),
        "游戏通关后没有迁移到拍、唱、演、说、创编或演奏等课堂音乐行为。",
        warn_only=fast_mode,
    )
    if singing_like:
        _add_check(
            checks,
            "singing_lesson_has_song_anchor",
            "学唱类课例锚定歌曲材料",
            bool(song_anchor_contract.get("selected_phrase")) if isinstance(song_anchor_contract, dict) else False,
            "学唱或演唱类课例最好上传谱面、MIDI 或文字旋律，否则游戏容易脱离具体歌曲。",
            warn_only=True,
        )
    if phrase_expression_like:
        materials = playable_game.get("materials", []) if isinstance(playable_game.get("materials"), list) else []
        evidence_cards = [
            item
            for item in materials
            if isinstance(item, dict)
            and not str(item.get("id", "")).startswith("phrase_")
            and any(
                keyword in " ".join([str(item.get("label", "")), str(item.get("music_value", "")), str(item.get("feedback", ""))])
                for keyword in ["唱", "情绪", "动作", "连贯", "跳跃", "温馨", "欢快", "对比", "重复"]
            )
        ]
        _add_check(
            checks,
            "phrase_expression_has_evidence_cards",
            "乐段表现有音乐证据卡",
            bool(evidence_cards),
            "该课例要求比较乐段、情绪、声音或动作表现，游戏不能只排列片段，必须包含演唱方法、情绪或动作依据。",
            warn_only=fast_mode,
        )
    if quality_gates:
        _add_check(
            checks,
            "middle_layer_quality_gates_passed",
            "中间层质量门槛通过",
            all(bool(value) for value in quality_gates.values()),
            "中间层仍有关键字段不足，生成结果可能和课例关联不够紧。",
            warn_only=True,
        )
    _add_check(
        checks,
        "music_game_concept_aligned",
        "游戏概念对齐音乐要素",
        _text_aligns(str(music_game.get("music_concept", "")), target_music_element),
        "小游戏概念没有对准教案中的具体音乐要素。",
        warn_only=fast_mode,
    )
    _add_check(
        checks,
        "game_goal_aligned",
        "游戏目标对齐课堂目标",
        _text_aligns(str(music_game.get("goal", "")), target_objective),
        "小游戏目标没有明显对齐课堂目标。",
        warn_only=fast_mode,
    )
    _add_check(
        checks,
        "subtitle_mentions_lesson_fit",
        "页面摘要体现课例约束",
        _text_aligns(subtitle, target_stage) or _text_aligns(subtitle, target_music_element),
        "页面摘要没有体现课例环节或具体音乐要素。",
        warn_only=True,
    )
    _add_check(
        checks,
        "teacher_guidance_present",
        "教师引导语完整",
        isinstance(teacher_guidance, list) and len(teacher_guidance) >= 2,
        "缺少教师引导语，课堂落地性不够。",
        warn_only=True,
    )
    _add_check(
        checks,
        "assessment_closure_present",
        "课堂收束存在",
        bool(assessment_closure),
        "缺少课堂收束与评价闭环。",
        warn_only=True,
    )
    _add_check(
        checks,
        "fit_reason_present",
        "说明为何适合这个课例",
        bool(fit_reason),
        "没有说明为什么这个游戏适合该课例。",
        warn_only=True,
    )
    _add_check(
        checks,
        "teacher_notes_include_constraints",
        "教师提示保留课例约束",
        any(_text_aligns(teacher_notes, token) for token in [target_stage, target_music_element, target_objective] if token),
        "教师提示没有保留课例环节或音乐要素约束。",
        warn_only=True,
    )

    passed = sum(1 for check in checks if check["status"] == "pass")
    score = round(passed / max(len(checks), 1) * 100)
    result = _agent_result(
        "lesson-fit-agent",
        checks,
        details={
            "lesson_fit_score": score,
            "target_stage": target_stage,
            "target_objective": target_objective,
            "target_music_element": target_music_element,
            "target_segment_task": target_segment_task,
            "mechanism_id": mechanic_rule.get("mechanism_id", ""),
            "quality_gates": quality_gates,
        },
    )
    min_score = 55 if fast_mode else 70
    if score < min_score and result["status"] == "warning":
        result["status"] = "failed"
    return result


def music_tool_calculator_agent(spec: dict[str, Any]) -> dict[str, Any]:
    scoring = spec.get("scoring", {})
    metrics = scoring.get("metrics", []) if isinstance(scoring.get("metrics"), list) else []
    weights = [float(metric.get("weight", 0)) for metric in metrics if isinstance(metric, dict)]
    creation = spec.get("creation", {})
    performance = spec.get("performance", {})
    listening = spec.get("listening", {})

    calculations = {
        "score_weight_total": round(sum(weights), 4),
        "performance_level_count": len(performance.get("levels", [])) if performance.get("enabled") else 0,
        "creation_bars": int(creation.get("bars", 0)) if creation.get("enabled") else 0,
        "creation_sixteenth_slots": int(creation.get("bars", 0)) * 16 if creation.get("enabled") else 0,
        "creation_piece_count": len(creation.get("pieces", [])) if creation.get("enabled") else 0,
        "tempo_multiplier": float(listening.get("tempo_multiplier", 1.0)) if listening.get("enabled") else 1.0,
    }

    checks: list[dict[str, Any]] = []
    if weights:
        _add_check(
            checks,
            "weights_sum",
            "评价权重合计合理",
            0.85 <= calculations["score_weight_total"] <= 1.15,
            f"评价权重合计为 {calculations['score_weight_total']}，建议接近 1。",
            warn_only=True,
        )
    if creation.get("enabled"):
        _add_check(
            checks,
            "grid_slots_enough",
            "旋律网格容量充足",
            calculations["creation_sixteenth_slots"] >= calculations["creation_piece_count"],
            "素材数量超过网格基础容量，可能不利于课堂操作。",
            warn_only=True,
        )

    return _agent_result("music-tool-calculator", checks, details=calculations)


def code_interpreter_agent(target_dir: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    config_dir = target_dir / "config"
    json_files = sorted(config_dir.glob("*.json")) if config_dir.exists() else []
    json_errors: list[str] = []
    for path in json_files:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            json_errors.append(f"{path.name}: {exc}")

    python_errors: list[str] = []
    for path in sorted((target_dir / "python").rglob("*.py")) if (target_dir / "python").exists() else []:
        try:
            ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError as exc:
            python_errors.append(f"{path.relative_to(target_dir)}: {exc}")

    index_content = _read_text(target_dir / "index.html")
    script_balance = _html_tag_balance(index_content, "script")
    style_balance = _html_tag_balance(index_content, "style")

    _add_check(checks, "json_parse", "配置 JSON 可解析", not json_errors, "存在无法解析的 JSON 配置。")
    _add_check(checks, "python_parse", "Python 插件语法正确", not python_errors, "存在 Python 语法错误。")
    _add_check(checks, "script_balance", "脚本标签闭合", script_balance, "script 标签数量不匹配。")
    _add_check(checks, "style_balance", "样式标签闭合", style_balance, "style 标签数量不匹配。")

    return _agent_result(
        "code-interpreter",
        checks,
        details={
            "json_files": [path.name for path in json_files],
            "json_errors": json_errors,
            "python_errors": python_errors,
        },
    )


def browser_qa_agent(spec: dict[str, Any], target_dir: Path) -> dict[str, Any]:
    content = _read_text(target_dir / "index.html")
    lower = content.lower()
    checks: list[dict[str, Any]] = []
    components = set(spec.get("interaction_model", {}).get("components", []))
    browser_details = _run_playwright_browser_qa(target_dir)
    requires_student_controls = _requires_student_controls(spec)
    fast_mode = _is_fast_mode(spec)

    _add_check(checks, "viewport", "移动端视口存在", "viewport" in lower, "页面缺少 viewport 设置。", warn_only=True)
    _add_check(checks, "no_broken_local_assets", "本地资源引用完整", not _missing_local_assets(content, target_dir), "存在缺失的本地 CSS 或 JS 资源。")
    _add_check(checks, "no_teacher_technical_terms", "学生界面不暴露技术词", not _technical_terms_in_ui(content), "页面可见文案疑似暴露技术词。")
    _add_check(
        checks,
        "has_reset",
        "有重置/重玩入口",
        "重置" in content or "重新" in content or "重来" in content or "retry" in lower,
        "页面缺少重置或重新挑战入口。",
        warn_only=_reset_warn_only(spec),
    )
    long_text_blocks = _long_student_text_blocks(content)
    copy_density = _student_copy_density(content)
    copy_density_limit = _student_copy_density_limit(spec)
    _add_check(
        checks,
        "student_copy_concise",
        "学生页文案精简",
        not long_text_blocks and copy_density <= copy_density_limit,
        (
            f"学生页面文案过多或存在过长说明：{' / '.join(long_text_blocks[:3])}；"
            f"可见文字 {copy_density}/{copy_density_limit} 字。"
        ),
        warn_only=fast_mode,
    )
    _add_check(
        checks,
        "large_student_modules",
        "学生操作模块足够大",
        _has_large_student_modules(content, browser_details),
        "页面交互控件或主操作区偏小，可能不适合学生触控或闯关使用。",
        warn_only=fast_mode,
    )
    _add_check(
        checks,
        "above_fold_student_action",
        "首屏就有学生可操作区",
        (not requires_student_controls) or _has_above_fold_student_action(content, browser_details),
        "首屏没有检测到足够大的开始、播放、闯关或操作区域，学生打开后容易只看到说明文字。",
        warn_only=fast_mode,
    )
    requires_playback = (
        "playback_controls" in components
        or spec.get("creation", {}).get("enabled")
        or spec.get("music_game", {}).get("enabled")
        or spec.get("listening", {}).get("enabled")
    )
    lesson_real_sound_required = bool(
        spec.get("lesson_generation_policy", {}).get("real_sound_required")
        if isinstance(spec.get("lesson_generation_policy"), dict)
        else False
    )
    lesson_game_contract = spec.get("lesson_game_contract", {}) if isinstance(spec.get("lesson_game_contract"), dict) else {}
    sound_source_policy = lesson_game_contract.get("sound_source_policy", {}) if isinstance(lesson_game_contract.get("sound_source_policy"), dict) else {}
    uploaded_audio_must_render = bool(sound_source_policy.get("has_uploaded_audio"))
    if requires_playback:
        has_sampled_playback = _uses_sampled_instrument_playback(content)
        _add_check(
            checks,
            "sampled_instrument_playback",
            "乐器试听使用真实采样音色",
            has_sampled_playback,
            "页面有播放需求，但没有发现 SoundFont 或采样音色播放实现，可能仍是纯电子合成音。",
            warn_only=fast_mode,
        )
        _add_check(
            checks,
            "not_oscillator_only_audio",
            "不是仅靠电子合成音播放",
            has_sampled_playback or not _uses_oscillator_synthesis(content),
            "页面主要使用 Web Audio oscillator 合成音色，听感会偏电子。",
            warn_only=fast_mode,
        )
    if lesson_real_sound_required:
        has_real_sound = _uses_real_lesson_sound_source(content)
        _add_check(
            checks,
            "lesson_game_real_sound",
            "教案转游戏必须使用真实音色",
            has_real_sound,
            "教案转游戏未检测到真实音色来源，不能只靠 oscillator 或空壳播放。",
            warn_only=fast_mode,
        )
        _add_check(
            checks,
            "lesson_game_real_sound_not_oscillator_only",
            "教案转游戏不是纯 oscillator",
            has_real_sound or not _uses_oscillator_synthesis(content),
            "教案转游戏主要依赖 oscillator 合成音色，未达真实音色要求。",
            warn_only=fast_mode,
        )
    if uploaded_audio_must_render:
        has_uploaded_audio_render = _uses_uploaded_lesson_audio(content, sound_source_policy)
        _add_check(
            checks,
            "lesson_uploaded_audio_rendered",
            "上传音频已落实到网页播放",
            has_uploaded_audio_render,
            "教师已上传课堂音频，但页面没有检测到这份音频或它切片的真实播放入口。",
        )
    if browser_details["mode"] == "playwright":
        _add_check(checks, "browser_open", "真实浏览器可打开", browser_details["opened"], browser_details.get("error") or "真实浏览器打开失败。", warn_only=fast_mode)
        _add_check(
            checks,
            "browser_console_clean",
            "真实浏览器无脚本错误",
            not _blocking_browser_console_errors(content, browser_details),
            "真实浏览器运行时发现脚本错误。",
            warn_only=fast_mode,
        )
        _add_check(
            checks,
            "browser_has_controls",
            "真实浏览器检测到交互控件",
            browser_details["button_count"] + browser_details["input_count"] + browser_details["select_count"] > 0,
            "真实浏览器没有检测到可操作控件。",
            warn_only=True if fast_mode else not requires_student_controls,
        )
    else:
        _add_check(
            checks,
            "browser_runtime",
            "真实浏览器 QA",
            True,
            browser_details["reason"],
        )

    if requires_playback:
        _add_check(checks, "has_play_control", "有播放/试听入口", any(word in content for word in ["播放", "试听", "开始"]), "页面缺少播放、试听或开始入口。")
    if "drag_drop_puzzle" in components:
        _add_check(
            checks,
            "drag_or_click_interaction",
            "拖拽或点击添加可用",
            any(token in lower for token in ["draggable", "dragstart", "drop", "点击", "添加"]),
            "需要拖拽或点击添加交互，但页面未发现相关实现。",
            warn_only=True,
        )
    if spec.get("listening", {}).get("enabled"):
        _add_check(checks, "audio_upload_form", "聆听活动有上传入口", 'type="file"' in lower or "上传" in content, "聆听活动缺少音频上传入口。")

    return _agent_result(
        "browser-qa-agent",
        checks,
        details={
            "mode": browser_details["mode"],
            "browser": browser_details,
            "html_bytes": len(content.encode("utf-8")),
        },
    )


def repair_agent(
    spec: dict[str, Any],
    target_dir: Path,
    agent_results: dict[str, Any],
    *,
    round_no: int = 1,
    allow_page_repairs: bool = True,
) -> dict[str, Any]:
    repairs: list[str] = []
    skipped: list[str] = []
    index_path = target_dir / "index.html"
    content = _read_text(index_path)

    audio_hardened = _repair_audio_playback_resilience(content)
    if audio_hardened != content:
        index_path.write_text(audio_hardened, encoding="utf-8")
        repairs.append("加固网页音频恢复逻辑，确保页面切后台或再次点击后仍可恢复播放。")
        content = audio_hardened

    if not allow_page_repairs:
        return {
            "agent_id": "repair-agent",
            "status": "repaired" if repairs else "skipped",
            "round": round_no,
            "repairs": repairs,
            "skipped": ["OpenCode 首次生成模式下已禁用本地结构性页面修补；仅保留安全的音频守卫注入。"] if repairs else ["OpenCode 首次生成模式下已禁用本地页面修补；未通过时应由 OpenCode 重新生成。"],
            "finished_at": _now(),
        }

    if content and "</html>" not in content.lower():
        index_path.write_text(content.rstrip() + "\n</html>\n", encoding="utf-8")
        repairs.append("补齐 index.html 结束标签。")
        content = _read_text(index_path)

    if content and "viewport" not in content.lower() and "<head" in content.lower():
        content = re.sub(
            r"(<head[^>]*>)",
            r'\1\n    <meta name="viewport" content="width=device-width, initial-scale=1.0" />',
            content,
            count=1,
            flags=re.IGNORECASE,
        )
        index_path.write_text(content, encoding="utf-8")
        repairs.append("补齐移动端 viewport。")
        content = _read_text(index_path)

    fixed_loader = _repair_legacy_soundfont_loader(content)
    if fixed_loader != content:
        index_path.write_text(fixed_loader, encoding="utf-8")
        repairs.append("修复旧版 soundfont 回退脚本，避免 script 标签失衡。")
        content = fixed_loader

    summary_path = target_dir / "config" / "opencode-artifact-summary.md"
    if not summary_path.exists():
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text(_default_artifact_summary(spec, agent_results), encoding="utf-8")
        repairs.append("补写 config/opencode-artifact-summary.md。")

    missing_assets = _missing_local_assets(_read_text(index_path), target_dir)
    for missing_asset in missing_assets:
        if missing_asset in {"styles.css", "app.js"}:
            target = target_dir / missing_asset
            target.write_text("/* Auto-created by Repair Agent to satisfy local asset reference. */\n" if missing_asset.endswith(".css") else "// Auto-created by Repair Agent to satisfy local asset reference.\n", encoding="utf-8")
            repairs.append(f"补齐缺失本地资源 {missing_asset}。")
        else:
            skipped.append(f"检测到缺失本地资源 {missing_asset}，未自动创建。")

    if _should_add_fallback_controls(spec, _read_text(index_path)):
        _inject_fallback_controls(index_path, spec)
        repairs.append("补充基础开始/重置/反馈控件，避免产物只有文字说明。")

    if _should_add_lesson_summary(spec, _read_text(index_path)):
        _inject_lesson_summary(index_path, spec)
        repairs.append("补充课例定位摘要，避免页面退化成通用小游戏。")

    if _should_add_student_game_brief(spec, _read_text(index_path)):
        _inject_student_game_brief(index_path, spec)
        repairs.append("补充学生可读的本关任务提示，说明听什么、拖什么、如何验证。")

    return {
        "agent_id": "repair-agent",
        "status": "repaired" if repairs else "passed",
        "round": round_no,
        "repairs": repairs,
        "skipped": skipped,
        "finished_at": _now(),
    }


def versioning_agent(target_dir: Path, *, action: str) -> dict[str, Any]:
    versions_dir = target_dir / "versions"
    versions_dir.mkdir(parents=True, exist_ok=True)
    version_number = _next_version_number(versions_dir)
    version_id = f"v{version_number:03d}"
    snapshot_dir = versions_dir / version_id
    snapshot_dir.mkdir(parents=True, exist_ok=True)

    files = []
    for relative in sorted(ARTIFACT_FILE_ALLOWLIST):
        source = target_dir / relative
        if not source.exists() or not source.is_file():
            continue
        destination = snapshot_dir / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        files.append(
            {
                "path": relative,
                "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                "bytes": source.stat().st_size,
            }
        )

    manifest = {
        "version": version_id,
        "action": action,
        "created_at": _now(),
        "file_count": len(files),
        "files": files,
    }
    (snapshot_dir / "version-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "agent_id": "versioning-agent",
        "status": "passed" if files else "warning",
        "version": version_id,
        "snapshot_path": str(snapshot_dir),
        "file_count": len(files),
        "manifest": f"versions/{version_id}/version-manifest.json",
        "finished_at": _now(),
    }


def optional_search_agent(spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "agent_id": "optional-search-agent",
        "status": "skipped",
        "reason": "默认离线禁用。后续可接入受控资料检索，用于歌曲背景、教材信息和课堂拓展引用。",
        "query_hint": f"{spec.get('song_name', '音乐课堂')} {spec.get('grade_band', '')} 教学活动",
        "finished_at": _now(),
    }


def _execution_plan(spec: dict[str, Any], *, action: str, revision: str) -> list[dict[str, str]]:
    steps = [
        ("frontend-artifact-builder", "生成/确认网页产物结构和交互入口。"),
        ("music-logic-agent", "检查音乐教学逻辑、调式、关卡、创作和游戏规则。"),
        ("lesson-fit-agent", "检查生成结果是否贴合具体课例、目标环节和音乐要素。"),
        ("music-tool-calculator", "计算权重、关卡数、小节容量和节奏相关指标。"),
        ("code-interpreter", "解析配置与代码结构，发现格式和语法问题。"),
        ("browser-qa-agent", "进行轻量浏览器式静态验收。"),
        ("repair-agent", "执行安全的最小自动修复。"),
        ("versioning-agent", "保存产物版本快照。"),
        ("optional-search-agent", "保留受控搜索能力，默认跳过。"),
    ]
    return [
        {
            "agent_id": agent_id,
            "goal": goal,
            "status": "pending",
            "action": action,
            "revision": revision if agent_id == "frontend-artifact-builder" and revision else "",
        }
        for agent_id, goal in steps
    ]


def _agent_result(agent_id: str, checks: list[dict[str, Any]], *, details: dict[str, Any] | None = None) -> dict[str, Any]:
    failures = [check for check in checks if check["status"] == "fail"]
    warnings = [check for check in checks if check["status"] == "warning"]
    status = "failed" if failures else "warning" if warnings else "passed"
    return {
        "agent_id": agent_id,
        "status": status,
        "checks": checks,
        "details": details or {},
        "finished_at": _now(),
    }


def _add_check(
    checks: list[dict[str, Any]],
    check_id: str,
    label: str,
    passed: bool,
    message: str,
    *,
    warn_only: bool = False,
) -> None:
    checks.append(
        {
            "id": check_id,
            "label": label,
            "status": "pass" if passed else "warning" if warn_only else "fail",
            "message": "通过。" if passed else message,
        }
    )


def _overall_status(results: dict[str, Any]) -> str:
    statuses = [result.get("status") for result in results.values() if isinstance(result, dict)]
    if any(status == "failed" for status in statuses):
        return "failed"
    if any(status == "warning" for status in statuses):
        return "passed_with_warnings"
    return "passed"


def _validation_layers(results: dict[str, Any], repair_result: dict[str, Any], *, fast_mode: bool) -> list[dict[str, Any]]:
    return [
        {
            "id": "runability",
            "label": "第一层：能不能跑",
            "status": _layer_status(results, ["frontend_artifact_builder", "browser_qa_agent", "code_interpreter"]),
            "blocking": True,
            "description": "检查页面文件、HTML/JS 结构、学生可操作入口和预览打开风险。",
        },
        {
            "id": "music_logic",
            "label": "第二层：音乐是否成立",
            "status": _layer_status(results, ["music_logic_agent", "music_tool_calculator"]),
            "blocking": True,
            "description": "检查音乐材料、节奏/旋律/音色和判定规则是否基本成立。",
        },
        {
            "id": "lesson_fit",
            "label": "第三层：是否贴合教案",
            "status": _layer_status(results, ["lesson_fit_agent"]),
            "blocking": not fast_mode,
            "description": "快速模式下多作为提醒；严格模式下用于拦截明显跑偏。",
        },
        {
            "id": "repair_versioning",
            "label": "修复层：自动优化和版本保存",
            "status": _layer_status({**results, "repair_agent": repair_result}, ["repair_agent", "versioning_agent"]),
            "blocking": False,
            "description": "记录自动修复、剩余风险和版本快照。",
        },
    ]


def _layer_status(results: dict[str, Any], keys: list[str]) -> str:
    statuses = [
        str(results.get(key, {}).get("status") or "")
        for key in keys
        if isinstance(results.get(key), dict) and results.get(key, {}).get("status")
    ]
    if not statuses:
        return "skipped"
    if "failed" in statuses:
        return "failed"
    if "warning" in statuses or "passed_with_warnings" in statuses:
        return "warning"
    if "repaired" in statuses:
        return "repaired"
    if "running" in statuses:
        return "running"
    return "passed"


def _relax_incremental_validation(results: dict[str, Any]) -> dict[str, Any]:
    relaxed: dict[str, Any] = {}
    blocking_agents = {"frontend_artifact_builder", "browser_qa_agent", "code_interpreter"}
    for agent_id, result in results.items():
        if not isinstance(result, dict):
            relaxed[agent_id] = result
            continue
        if agent_id in blocking_agents:
            relaxed[agent_id] = result
            continue
        updated = dict(result)
        checks = updated.get("checks")
        if isinstance(checks, list):
            new_checks: list[dict[str, Any]] = []
            for check in checks:
                if isinstance(check, dict) and check.get("status") == "fail":
                    softened = dict(check)
                    softened["status"] = "warning"
                    new_checks.append(softened)
                else:
                    new_checks.append(check)
            updated["checks"] = new_checks
        if updated.get("status") == "failed":
            updated["status"] = "warning"
        relaxed[agent_id] = updated
    return relaxed


def _should_deliver_first_page(spec: dict[str, Any], opencode_run: dict[str, Any], results: dict[str, Any]) -> bool:
    if spec.get("activity_type") != "music_game":
        return False
    if not bool(opencode_run.get("enabled")) or opencode_run.get("action") != "generate":
        return False
    if not _opencode_produced_artifact(opencode_run):
        return False
    status = str(opencode_run.get("status") or "")
    if status not in {"completed", "failed_with_artifact", "timeout_with_artifact"}:
        return False
    frontend = results.get("frontend_artifact_builder", {})
    browser = results.get("browser_qa_agent", {})
    code = results.get("code_interpreter", {})
    if not isinstance(frontend, dict) or not isinstance(browser, dict) or not isinstance(code, dict):
        return False
    if frontend.get("status") == "failed":
        return False
    if code.get("status") == "failed":
        return False
    return True


def _relax_first_page_delivery_validation(results: dict[str, Any]) -> dict[str, Any]:
    relaxed: dict[str, Any] = {}
    blocking_agents = {"frontend_artifact_builder", "browser_qa_agent", "code_interpreter"}
    for agent_id, result in results.items():
        if not isinstance(result, dict):
            relaxed[agent_id] = result
            continue
        if agent_id in blocking_agents:
            relaxed[agent_id] = result
            continue
        updated = dict(result)
        checks = updated.get("checks")
        if isinstance(checks, list):
            new_checks: list[dict[str, Any]] = []
            for check in checks:
                if isinstance(check, dict) and check.get("status") == "fail":
                    softened = dict(check)
                    softened["status"] = "warning"
                    new_checks.append(softened)
                else:
                    new_checks.append(check)
            updated["checks"] = new_checks
        if updated.get("status") == "failed":
            updated["status"] = "warning"
        relaxed[agent_id] = updated
    return relaxed


def _is_playable_scaffold_artifact(spec: dict[str, Any]) -> bool:
    scaffold = spec.get("playable_scaffold", {}) if isinstance(spec.get("playable_scaffold"), dict) else {}
    generation_strategy = spec.get("generation_strategy", {}) if isinstance(spec.get("generation_strategy"), dict) else {}
    return (
        spec.get("activity_type") == "music_game"
        and bool(scaffold.get("enabled"))
        and str(generation_strategy.get("mode") or "") == "fast_playable_scaffold"
    )


def _relax_fast_scaffold_validation(results: dict[str, Any]) -> dict[str, Any]:
    """Fast scaffold artifacts should be blocked only by runtime usability.

    Music/lesson completeness remains visible as warnings so strict mode or a
    later upgrade can refine it without making the first usable version crawl.
    """

    relaxed: dict[str, Any] = {}
    blocking_agents = {"frontend_artifact_builder", "browser_qa_agent", "code_interpreter"}
    hard_music_checks = {
        "lesson_game_playable_spec_present",
        "no_forced_audio_upload",
        "activity_type_lock_respected",
    }
    for agent_id, result in results.items():
        if not isinstance(result, dict):
            relaxed[agent_id] = result
            continue
        if agent_id in blocking_agents:
            relaxed[agent_id] = result
            continue
        updated = dict(result)
        checks = updated.get("checks")
        has_failures = False
        if isinstance(checks, list):
            new_checks: list[dict[str, Any]] = []
            for check in checks:
                if not isinstance(check, dict) or check.get("status") != "fail":
                    new_checks.append(check)
                    continue
                if agent_id == "music_logic_agent" and check.get("id") in hard_music_checks:
                    has_failures = True
                    new_checks.append(check)
                    continue
                softened = dict(check)
                softened["status"] = "warning"
                new_checks.append(softened)
            updated["checks"] = new_checks
        if updated.get("status") == "failed" and not has_failures:
            updated["status"] = "warning"
        relaxed[agent_id] = updated
    return relaxed


def _run_playwright_browser_qa(target_dir: Path) -> dict[str, Any]:
    index_path = target_dir / "index.html"
    if not index_path.exists():
        return {"mode": "static-browser-qa", "reason": "index.html 不存在，无法启动真实浏览器。"}

    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        return {
            "mode": "static-browser-qa",
            "reason": f"未安装 Playwright，已降级为静态 QA：{exc}",
        }

    console_errors: list[str] = []
    page_errors: list[str] = []
    click_error = ""
    screenshot_path = target_dir / "config" / "browser-qa.png"
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1366, "height": 900})
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
            page.on("pageerror", lambda exc: page_errors.append(str(exc)))
            page.goto(index_path.resolve().as_uri(), wait_until="load", timeout=8000)
            page.wait_for_timeout(350)
            button_count = page.locator("button").count()
            input_count = page.locator("input, textarea").count()
            select_count = page.locator("select").count()
            if button_count:
                try:
                    start_buttons = page.locator("#start-overlay button, .start-overlay button, .start-screen button")
                    if start_buttons.count():
                        start_buttons.first.click(timeout=1600)
                    else:
                        page.locator("button:visible").first.click(timeout=1600)
                    page.wait_for_timeout(150)
                except Exception as exc:
                    click_error = str(exc)
            interactive_metrics = page.evaluate(
                """() => {
                  const selectors = "button,input,textarea,select,canvas,[draggable='true'],.drop-zone,.playable-target,.playable-bank,.game-lane,.quest-panel,.melody-canvas,#game-area,#challenge-zone,#card-pool,.note-card,.drop-slot,.game-board,.main-stage,.student-stage";
                  const nodes = Array.from(document.querySelectorAll(selectors));
                  const viewportHeight = window.innerHeight || 900;
                  const boxes = nodes.map((node) => {
                    const rect = node.getBoundingClientRect();
                    return { width: rect.width, height: rect.height, top: rect.top, area: rect.width * rect.height };
                  }).filter((box) => box.width > 0 && box.height > 0);
                  const aboveFold = boxes.filter((box) => box.top < viewportHeight && box.top + box.height > 0);
                  return {
                    largeInteractiveCount: boxes.filter((box) => box.height >= 56 && box.area >= 6000).length,
                    largestInteractiveArea: boxes.reduce((max, box) => Math.max(max, box.area), 0),
                    aboveFoldInteractiveCount: aboveFold.filter((box) => box.height >= 56 && box.area >= 6000).length,
                    largestAboveFoldInteractiveArea: aboveFold.reduce((max, box) => Math.max(max, box.area), 0),
                  };
                }"""
            )
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(screenshot_path), full_page=True)
            browser.close()
    except Exception as exc:
        return {
            "mode": "playwright",
            "opened": False,
            "error": str(exc),
            "console_errors": console_errors[-8:],
            "page_errors": page_errors[-8:],
            "click_error": click_error,
            "button_count": 0,
            "input_count": 0,
            "select_count": 0,
            "screenshot": "",
            "large_interactive_count": 0,
            "largest_interactive_area": 0,
            "above_fold_interactive_count": 0,
            "largest_above_fold_interactive_area": 0,
        }

    return {
        "mode": "playwright",
        "opened": True,
        "error": "",
        "console_errors": console_errors[-8:],
        "page_errors": page_errors[-8:],
        "click_error": click_error,
        "button_count": button_count,
        "input_count": input_count,
        "select_count": select_count,
        "screenshot": _relative_output_url(target_dir, screenshot_path),
        "large_interactive_count": int(interactive_metrics.get("largeInteractiveCount", 0)),
        "largest_interactive_area": int(interactive_metrics.get("largestInteractiveArea", 0)),
        "above_fold_interactive_count": int(interactive_metrics.get("aboveFoldInteractiveCount", 0)),
        "largest_above_fold_interactive_area": int(interactive_metrics.get("largestAboveFoldInteractiveArea", 0)),
    }


def _repair_max_rounds() -> int:
    try:
        return max(1, min(int(os.getenv("EXECUTION_REPAIR_MAX_ROUNDS", "3")), 5))
    except ValueError:
        return 3


def _merge_repair_attempts(attempts: list[dict[str, Any]]) -> dict[str, Any]:
    repairs = []
    skipped = []
    for attempt in attempts:
        repairs.extend(attempt.get("repairs", []))
        skipped.extend(attempt.get("skipped", []))
    return {
        "agent_id": "repair-agent",
        "status": "repaired" if repairs else "passed",
        "rounds": len(attempts),
        "attempts": attempts,
        "repairs": repairs,
        "skipped": skipped,
        "finished_at": _now(),
    }


def _should_add_fallback_controls(spec: dict[str, Any], content: str) -> bool:
    if not content:
        return False
    if _has_interaction(content):
        return False
    return spec.get("activity_type") in {"performance", "creation", "music_game", "mixed"}


def _should_add_lesson_summary(spec: dict[str, Any], content: str) -> bool:
    lesson_context = spec.get("lesson_context", {}) if isinstance(spec.get("lesson_context"), dict) else {}
    if not lesson_context or not content:
        return False
    if spec.get("activity_type") == "music_game" or _has_playable_controls(content):
        return False
    return 'data-lesson-panel="true"' not in content and "课例定位" not in content


def _should_add_student_game_brief(spec: dict[str, Any], content: str) -> bool:
    if not content or spec.get("activity_type") != "music_game":
        return False
    if 'data-lesson-panel="true"' in content or "本关任务" in content:
        return False
    music_game = spec.get("music_game", {}) if isinstance(spec.get("music_game"), dict) else {}
    return bool(music_game.get("enabled")) and _has_playable_controls(content)


def _inject_student_game_brief(index_path: Path, spec: dict[str, Any]) -> None:
    content = _read_text(index_path)
    if not content:
        return
    lesson_context = spec.get("lesson_context", {}) if isinstance(spec.get("lesson_context"), dict) else {}
    music_game = spec.get("music_game", {}) if isinstance(spec.get("music_game"), dict) else {}
    playable = music_game.get("playable_game", {}) if isinstance(music_game.get("playable_game"), dict) else {}
    song_title = (
        spec.get("song_name")
        or lesson_context.get("song_name")
        or playable.get("song_title")
        or "这首歌"
    )
    target_stage = spec.get("target_stage") or lesson_context.get("target_stage") or playable.get("target_stage") or "课堂活动"
    target_music_element = (
        spec.get("target_music_element")
        or lesson_context.get("target_music_element")
        or playable.get("music_goal")
        or music_game.get("music_concept")
        or "音乐线索"
    )
    prompt = playable.get("prompt") or music_game.get("mechanic") or "先听目标，再完成挑战。"
    student_task = playable.get("student_facing_task", {}) if isinstance(playable.get("student_facing_task"), dict) else {}
    listen_task = str(student_task.get("listen") or f"听《{song_title}》片段")
    do_task = str(student_task.get("do") or "拖卡片完成挑战")
    pass_task = str(student_task.get("pass") or f"完成后回到“{target_stage}”")
    target_segment_task = str(spec.get("target_segment_task") or lesson_context.get("target_segment_task") or "")
    selected_phrase = (
        spec.get("song_anchor_contract", {}).get("selected_phrase", {})
        if isinstance(spec.get("song_anchor_contract"), dict)
        else {}
    )
    phrase_label = str(selected_phrase.get("label", "")) if isinstance(selected_phrase, dict) else ""
    brief = f"""
    <section class="agent-game-brief" data-lesson-panel="true" style="margin:14px 0 18px;padding:14px 16px;border-radius:18px;background:rgba(255,255,255,.11);border:1px solid rgba(255,255,255,.18);color:inherit;">
      <strong>本关任务</strong>
      <span style="display:inline-block;margin-left:10px;">{html_escape(listen_task)}，抓住“{html_escape(str(target_music_element))}”。</span>
      {f'<div style="margin-top:6px;font-size:.9em;opacity:.82;">环节任务：{html_escape(target_segment_task)}</div>' if target_segment_task else ''}
      {f'<div style="margin-top:4px;font-size:.9em;opacity:.78;">歌曲片段：{html_escape(phrase_label)}</div>' if phrase_label else ''}
      <div style="margin-top:8px;font-size:.94em;opacity:.86;">听：{html_escape(listen_task)} ｜ 做：{html_escape(do_task)} ｜ 过关：{html_escape(pass_task)}</div>
      <div style="margin-top:6px;font-size:.88em;opacity:.72;">{html_escape(short_text(str(prompt), 54))}</div>
    </section>
"""
    if re.search(r"<main\b", content, flags=re.IGNORECASE):
        content = re.sub(
            r"(<main[^>]*>\s*)",
            lambda match: match.group(1) + brief,
            content,
            count=1,
            flags=re.IGNORECASE,
        )
    elif "<body" in content.lower():
        content = re.sub(
            r"(<body[^>]*>\s*)",
            lambda match: match.group(1) + brief,
            content,
            count=1,
            flags=re.IGNORECASE,
        )
    else:
        content = brief + content
    index_path.write_text(content, encoding="utf-8")


def _inject_lesson_summary(index_path: Path, spec: dict[str, Any]) -> None:
    content = _read_text(index_path)
    lesson_context = spec.get("lesson_context", {}) if isinstance(spec.get("lesson_context"), dict) else {}
    if not content or not lesson_context:
        return

    teacher_guidance = "".join(
        f"<li>{html_escape(str(item))}</li>"
        for item in (spec.get("teacher_guidance") or lesson_context.get("teacher_guidance") or [])[:3]
        if str(item).strip()
    ) or "<li>先说明课堂任务，再引导学生进入互动挑战。</li>"
    summary = f"""
    <section class="agent-lesson-summary" data-lesson-panel="true" style="margin:24px 0;padding:20px;border-radius:20px;background:rgba(255,255,255,.88);border:1px solid rgba(0,0,0,.08);">
      <h2>课例定位</h2>
      <p><strong>投放环节：</strong>{html_escape(str(spec.get("target_stage") or lesson_context.get("target_stage") or "课堂核心环节"))}</p>
      <p><strong>目标任务：</strong>{html_escape(str(spec.get("target_objective") or lesson_context.get("target_objective") or "围绕本课核心目标展开"))}</p>
      <p><strong>音乐要素：</strong>{html_escape(str(spec.get("target_music_element") or lesson_context.get("target_music_element") or "综合音乐感知"))}</p>
      <p><strong>教案依据：</strong>{html_escape(str(spec.get("lesson_evidence") or lesson_context.get("lesson_evidence") or "根据教案内容提炼"))}</p>
      <p><strong>设计原因：</strong>{html_escape(str(spec.get("why_this_game_fits_this_lesson") or lesson_context.get("why_this_game_fits_this_lesson") or "把教案里的核心任务转成可操作活动。"))}</p>
      <ul>{teacher_guidance}</ul>
      <p><strong>课堂收束：</strong>{html_escape(str(spec.get("assessment_closure") or lesson_context.get("assessment_closure") or "完成互动后回到课堂表达与评价。"))}</p>
    </section>
"""
    if "<body" in content.lower():
        content = re.sub(
            r"(<body[^>]*>\s*)",
            lambda match: match.group(1) + summary,
            content,
            count=1,
            flags=re.IGNORECASE,
        )
    else:
        content = summary + content
    index_path.write_text(content, encoding="utf-8")


def _inject_fallback_controls(index_path: Path, spec: dict[str, Any]) -> None:
    content = _read_text(index_path)
    widget = f"""
    <section class="agent-repair-controls" style="margin:24px 0;padding:18px;border-radius:18px;background:#fff8df;border:1px solid rgba(0,0,0,.12);">
      <h2>课堂互动控制</h2>
      <p id="agent-repair-feedback">点击开始后，学生可以按提示完成一次课堂挑战。</p>
      <button type="button" id="agent-repair-start">开始挑战</button>
      <button type="button" id="agent-repair-reset">重置</button>
    </section>
    <script>
      (() => {{
        const title = {json.dumps(str(spec.get("title", "音乐课堂工具")), ensure_ascii=False)};
        const feedback = document.querySelector("#agent-repair-feedback");
        document.querySelector("#agent-repair-start")?.addEventListener("click", () => {{
          feedback.textContent = `已经开始：${{title}}。请完成本页提示的音乐任务，并说出你的音乐理由。`;
        }});
        document.querySelector("#agent-repair-reset")?.addEventListener("click", () => {{
          feedback.textContent = "已经重置，可以重新挑战。";
        }});
      }})();
    </script>
"""
    if "</body>" in content.lower():
        content = re.sub(r"</body>", widget + "\n  </body>", content, count=1, flags=re.IGNORECASE)
    else:
        content += widget
    index_path.write_text(content, encoding="utf-8")


def _summary_for_status(status: str, results: dict[str, Any]) -> str:
    failed = [key for key, result in results.items() if isinstance(result, dict) and result.get("status") == "failed"]
    warnings = [key for key, result in results.items() if isinstance(result, dict) and result.get("status") == "warning"]
    if status == "failed":
        return f"执行层发现阻断问题：{'、'.join(failed)}。"
    if warnings:
        return f"执行层通过，但仍有需要关注的项目：{'、'.join(warnings)}。"
    return "执行层多智能体验收通过。"


def _repair_legacy_soundfont_loader(content: str) -> str:
    pattern = re.compile(
        r"""if\s*\(!window\.Soundfont\)\s*\{\s*document\.write\('<script src="/static/assets/soundfont-player/soundfont-player\.js"><\\\\/script>'\);\s*\}""",
        re.S,
    )
    replacement = """if (!window.Soundfont) {
        const fallbackScript = document.createElement("script");
        fallbackScript.src = "/static/assets/soundfont-player/soundfont-player.js";
        document.head.appendChild(fallbackScript);
      }"""
    return pattern.sub(replacement, content)


def _repair_audio_playback_resilience(content: str) -> str:
    if not content or "AudioContext" not in content and "audio.play(" not in content:
        return content

    updated = content

    global_guard = """
    <script>
      (() => {
        if (window.__musicAgentAudioGuardVersion >= 2) return;
        window.__musicAgentAudioGuardInstalled = true;
        window.__musicAgentAudioGuardVersion = 2;

        const NativeAudioContext = window.AudioContext || window.webkitAudioContext;
        const trackedContexts = new Set();
        const resetCallbacks = new Set();
        let wakeInFlight = null;

        function trackContext(context) {
          if (!context || trackedContexts.has(context)) return context;
          trackedContexts.add(context);
          context.addEventListener?.("statechange", () => {
            if (context.state === "closed") {
              trackedContexts.delete(context);
              resetCallbacks.forEach((callback) => {
                try {
                  callback(context);
                } catch (error) {
                  console.warn("Audio reset callback failed.", error);
                }
              });
            }
          });
          return context;
        }

        async function wakeTrackedContexts(reason = "playback") {
          if (!trackedContexts.size) return;
          const tasks = [];
          trackedContexts.forEach((context) => {
            if (!context) return;
            if (context.state === "closed") {
              trackedContexts.delete(context);
              resetCallbacks.forEach((callback) => {
                try {
                  callback(context);
                } catch (error) {
                  console.warn("Audio reset callback failed.", error);
                }
              });
              return;
            }
            if (context.state === "suspended") {
              tasks.push(
                context.resume().catch((error) => {
                  console.warn(`AudioContext resume failed during ${reason}.`, error);
                })
              );
            }
          });
          if (tasks.length) {
            await Promise.all(tasks);
          }
        }

        function scheduleWake(reason) {
          if (!wakeInFlight) {
            wakeInFlight = wakeTrackedContexts(reason).finally(() => {
              wakeInFlight = null;
            });
          }
          return wakeInFlight;
        }

        window.__musicAgentAudioGuard = window.__musicAgentAudioGuard || {};
        window.__musicAgentAudioGuard.wake = scheduleWake;
        window.__musicAgentAudioGuard.trackContext = trackContext;
        window.__musicAgentAudioGuard.onReset = (callback) => {
          if (typeof callback === "function") {
            resetCallbacks.add(callback);
          }
        };

        if (NativeAudioContext && !window.__musicAgentAudioContextWrapped) {
          window.__musicAgentAudioContextWrapped = true;
          const WrappedAudioContext = new Proxy(NativeAudioContext, {
            construct(target, args, newTarget) {
              const context = Reflect.construct(target, args, newTarget || target);
              return trackContext(context);
            },
          });
          WrappedAudioContext.prototype = NativeAudioContext.prototype;
          try {
            Object.defineProperty(WrappedAudioContext, "name", { value: NativeAudioContext.name });
          } catch (_error) {}
          window.AudioContext = WrappedAudioContext;
          if (window.webkitAudioContext) {
            window.webkitAudioContext = WrappedAudioContext;
          }
        }

        if (!window.__musicAgentMediaPlayWrapped && window.HTMLMediaElement?.prototype?.play) {
          window.__musicAgentMediaPlayWrapped = true;
          const nativePlay = window.HTMLMediaElement.prototype.play;
          window.HTMLMediaElement.prototype.play = function playWithWake(...args) {
            return Promise.resolve(scheduleWake("media-play")).catch(() => {}).then(() => nativePlay.apply(this, args));
          };
        }

        const wake = () => {
          scheduleWake("gesture").catch(() => {});
        };
        ["pointerdown", "pointerup", "touchstart", "touchend", "mousedown", "keydown", "click"].forEach((eventName) => {
          document.addEventListener(eventName, wake, { passive: true, capture: true });
        });
        document.addEventListener("visibilitychange", () => {
          if (document.visibilityState === "visible") {
            scheduleWake("visibilitychange").catch(() => {});
          }
        });
        window.addEventListener("focus", () => {
          scheduleWake("window-focus").catch(() => {});
        });
          window.addEventListener("pageshow", () => {
            scheduleWake("pageshow").catch(() => {});
          });

        function wrapSoundfontPlayer(player, context) {
          if (!player || player.__musicAgentWrapped) return player;
          player.__musicAgentWrapped = true;
          player.__musicAgentAudioContext = context || null;
          if (typeof player.play === "function") {
            const nativePlay = player.play.bind(player);
            player.play = function playWithAudioWake(...args) {
              const activeContext = player.__musicAgentAudioContext || context;
              if (activeContext?.state === "closed") {
                throw new Error("SoundFont player is bound to a closed AudioContext");
              }
              if (activeContext?.state === "suspended") {
                return Promise.resolve(scheduleWake("soundfont-play"))
                  .catch(() => {})
                  .then(() => activeContext.resume?.())
                  .catch(() => {})
                  .then(() => nativePlay(...args));
              }
              return nativePlay(...args);
            };
          }
          return player;
        }

        function installSoundfontInstrumentGuard() {
          if (!window.Soundfont || window.Soundfont.__musicAgentInstrumentWrapped) return;
          const nativeInstrument = window.Soundfont.instrument;
          if (typeof nativeInstrument !== "function") return;
          window.Soundfont.__musicAgentInstrumentWrapped = true;
          window.Soundfont.instrument = function instrumentWithAudioWake(context, name, options) {
            if (context) trackContext(context);
            return Promise.resolve(scheduleWake("soundfont-load"))
              .catch(() => {})
              .then(() => nativeInstrument.call(this, context, name, options))
              .then((player) => wrapSoundfontPlayer(player, context));
          };
        }

        installSoundfontInstrumentGuard();
        document.addEventListener("DOMContentLoaded", installSoundfontInstrumentGuard);
        window.addEventListener("load", installSoundfontInstrumentGuard);
        const soundfontGuardTimer = window.setInterval(() => {
          installSoundfontInstrumentGuard();
          if (window.Soundfont?.__musicAgentInstrumentWrapped) {
            window.clearInterval(soundfontGuardTimer);
          }
        }, 250);
        window.setTimeout(() => window.clearInterval(soundfontGuardTimer), 8000);
      })();
    </script>
"""
    if "window.__musicAgentAudioGuardVersion >= 2" not in updated and "<script" in updated:
        old_guard_pattern = re.compile(
            r"\s*<script>\s*\(\(\)\s*=>\s*\{\s*if\s*\(window\.__musicAgentAudioGuardInstalled\)\s*return;\s*window\.__musicAgentAudioGuardInstalled\s*=\s*true;.*?window\.addEventListener\(\"pageshow\",\s*\(\)\s*=>\s*\{\s*scheduleWake\(\"pageshow\"\)\.catch\(\(\)\s*=>\s*\{\}\);\s*\}\);\s*\}\)\(\);\s*</script>",
            re.S,
        )
        if old_guard_pattern.search(updated):
            updated = old_guard_pattern.sub("\n" + global_guard, updated, count=1)
        elif "</head>" in updated.lower():
            updated = re.sub(r"</head>", global_guard + "\n  </head>", updated, count=1, flags=re.IGNORECASE)
        else:
            updated = global_guard + updated

    if "function getAudioContext()" in updated and "async function ensureAudioReady(" not in updated:
        helper = """
function resetSoundfontStateForAudioContext() {
  if (typeof soundfontPlayer !== 'undefined') soundfontPlayer = null;
  if (typeof isSoundfontLoaded !== 'undefined') isSoundfontLoaded = false;
  if (typeof soundfontReady !== 'undefined') soundfontReady = false;
  if (typeof currentInstrument !== 'undefined') currentInstrument = null;
  if (typeof piano !== 'undefined') piano = null;
  if (typeof soundfontCache !== 'undefined' && soundfontCache?.clear) soundfontCache.clear();
}

async function ensureAudioReady(reason = 'playback') {
  if (!audioCtx) {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    window.__musicAgentAudioGuard?.trackContext?.(audioCtx);
    window.__musicAgentAudioGuard?.onReset?.(() => {
      resetSoundfontStateForAudioContext();
    });
  }
  if (audioCtx.state === 'closed') {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    window.__musicAgentAudioGuard?.trackContext?.(audioCtx);
    resetSoundfontStateForAudioContext();
  }
  if (audioCtx.state === 'suspended') {
    try {
      await audioCtx.resume();
    } catch (error) {
      console.warn('AudioContext resume failed during ' + reason, error);
    }
  }
  return audioCtx;
}

function installAudioWakeHooks() {
  if (window.__audioWakeHooksInstalled) return;
  window.__audioWakeHooksInstalled = true;
  const wake = () => { ensureAudioReady('gesture').catch(() => {}); };
  ['pointerdown', 'pointerup', 'touchstart', 'touchend', 'mousedown', 'keydown', 'click'].forEach((eventName) => {
    document.addEventListener(eventName, wake, { passive: true, capture: true });
  });
  document.addEventListener('visibilitychange', function() {
    if (document.visibilityState === 'visible') {
      ensureAudioReady('visibilitychange').catch(() => {});
    }
  });
  window.addEventListener('focus', function() {
    ensureAudioReady('window-focus').catch(() => {});
  });
  window.addEventListener('pageshow', function() {
    ensureAudioReady('pageshow').catch(() => {});
  });
}

"""
        updated = updated.replace("async function initSoundfont() {", helper + "async function initSoundfont() {", 1)

    if "function getAudioContext()" in updated:
        updated = updated.replace(
            "function getAudioContext() {\n  if (!audioCtx) {\n    audioCtx = new (window.AudioContext || window.webkitAudioContext)();\n  }\n  return audioCtx;\n}",
            "function getAudioContext() {\n  if (!audioCtx || audioCtx.state === 'closed') {\n    audioCtx = new (window.AudioContext || window.webkitAudioContext)();\n  }\n  return audioCtx;\n}",
        )

    if "const ctx = getAudioContext();" in updated:
        updated = updated.replace("const ctx = getAudioContext();", "const ctx = audioCtx || getAudioContext();")

    if "let audioCtx = null;" in updated and "async function ensureAudioReady(reason = 'playback')" not in updated:
        helper = """
    function resetSoundfontStateForAudioContext() {
      if (typeof soundfontPlayer !== 'undefined') soundfontPlayer = null;
      if (typeof isSoundfontLoaded !== 'undefined') isSoundfontLoaded = false;
      if (typeof soundfontReady !== 'undefined') soundfontReady = false;
      if (typeof currentInstrument !== 'undefined') currentInstrument = null;
      if (typeof piano !== 'undefined') piano = null;
      if (typeof soundfontCache !== 'undefined' && soundfontCache?.clear) soundfontCache.clear();
    }

    async function ensureAudioReady(reason = 'playback') {
      const AudioContextCtor = window.AudioContext || window.webkitAudioContext;
      if (!AudioContextCtor) {
        throw new Error('AudioContext unavailable');
      }
      if (!audioCtx || audioCtx.state === 'closed') {
        audioCtx = new AudioContextCtor();
        window.__musicAgentAudioGuard?.trackContext?.(audioCtx);
        window.__musicAgentAudioGuard?.onReset?.(() => {
          resetSoundfontStateForAudioContext();
        });
        resetSoundfontStateForAudioContext();
      }
      await window.__musicAgentAudioGuard?.wake?.(reason).catch(() => {});
      if (audioCtx.state === 'suspended') {
        try {
          await audioCtx.resume();
        } catch (error) {
          console.warn('AudioContext resume failed during ' + reason, error);
        }
      }
      return audioCtx;
    }

"""
        updated = updated.replace("    let audioCtx = null;\n", "    let audioCtx = null;\n" + helper, 1)

    if "function initAudio() {" in updated and "ensureAudioReady('init-audio').catch(() => {});" not in updated:
        updated = re.sub(
            r"(function\s+initAudio\s*\(\)\s*\{\s*if\s*\(!audioCtx\)\s*\{\s*audioCtx\s*=\s*new\s*\(window\.AudioContext\s*\|\|\s*window\.webkitAudioContext\)\s*\(\);\s*\}\s*\})",
            "function initAudio() {\n      ensureAudioReady('init-audio').catch(() => {});\n    }",
            updated,
            count=1,
            flags=re.S,
        )

    load_soundfont_start = "    function loadSoundfont() {\n      return new Promise((resolve) => {"
    load_soundfont_end = "      });\n    }\n\n    // Play a note using Web Audio oscillator"
    if (
        "function loadSoundfont() {" in updated
        and "return ensureAudioReady('soundfont-load')" not in updated
        and load_soundfont_start in updated
        and load_soundfont_end in updated
    ):
        updated = updated.replace(
            load_soundfont_start,
            "    function loadSoundfont() {\n      return ensureAudioReady('soundfont-load').then(() => new Promise((resolve) => {",
            1,
        )
        updated = updated.replace(
            load_soundfont_end,
            "      }));\n    }\n\n    // Play a note using Web Audio oscillator",
            1,
        )

    play_note_start = "    function playNote(midiNote, duration, velocity) {\n      initAudio();"
    play_note_end = "      playOscillatorNote(midiNote, dur, vel);\n    }\n\n    // Initialize on first interaction"
    if (
        "function playNote(midiNote, duration, velocity) {" in updated
        and "ensureAudioReady('note-play')" not in updated
        and play_note_start in updated
        and play_note_end in updated
    ):
        updated = updated.replace(
            play_note_start,
            "    function playNote(midiNote, duration, velocity) {\n      return ensureAudioReady('note-play').catch(() => {}).then(() => {",
            1,
        )
        updated = updated.replace(
            play_note_end,
            "      playOscillatorNote(midiNote, dur, vel);\n      });\n    }\n\n    // Initialize on first interaction",
            1,
        )

    if "if (isSoundfontLoaded && soundfontPlayer) {" in updated and "audioCtx.state !== 'running'" not in updated:
        updated = updated.replace(
            "      if (isSoundfontLoaded && soundfontPlayer) {",
            "      if (isSoundfontLoaded && soundfontPlayer && audioCtx && audioCtx.state !== 'closed') {",
            1,
        )

    if "async function playSequence(sequenceIds) {" in updated and "await ensureAudioReady('sequence');" not in updated:
        updated = updated.replace(
            "async function playSequence(sequenceIds) {\n  if (isPlaying) return;\n  isPlaying = true;",
            "async function playSequence(sequenceIds) {\n  if (isPlaying) return;\n  await ensureAudioReady('sequence');\n  isPlaying = true;",
            1,
        )

    if "await initSoundfont();" in updated and "await ensureAudioReady('target-play');" not in updated:
        updated = updated.replace("async function playTarget() {\n  await initSoundfont();", "async function playTarget() {\n  await ensureAudioReady('target-play');\n  await initSoundfont();", 1)
        updated = updated.replace("async function playStudent() {\n  await initSoundfont();", "async function playStudent() {\n  await ensureAudioReady('student-play');\n  await initSoundfont();", 1)

    if "window.onload = function() {" in updated and "installAudioWakeHooks();" not in updated:
        updated = updated.replace(
            "window.onload = function() {\n  // Pre-init audio context on first user interaction",
            "window.onload = function() {\n  installAudioWakeHooks();\n  // Pre-init audio context on first user interaction",
            1,
        )
        updated = updated.replace("if (!audioCtx) getAudioContext();", "ensureAudioReady('initial-click').catch(() => {});")

    if "const started = audio.play();" in updated and "await ensureAudioReady(`audio-clip:${clip}`);" not in updated:
        updated = updated.replace(
            "            const started = audio.play();\n            if (started && typeof started.catch === \"function\") {\n              started.catch(() => resolve());\n            }\n",
            "            ensureAudioReady(`audio-clip:${clip}`).catch(() => {}).finally(() => {\n              const started = audio.play();\n              if (started && typeof started.catch === \"function\") {\n                started.catch(() => resolve());\n              }\n            });\n",
        )

    if "let audioContext = null;" in updated and "async function ensureAudioReady(reason = \"playback\")" not in updated:
        helper = """
      let audioActivationInstalled = false;
      let audioResumeInFlight = null;

      function getOrCreateAudioContext() {
        if (!audioContext) {
          const AudioContextCtor = window.AudioContext || window.webkitAudioContext;
          if (!AudioContextCtor) {
            throw new Error("AudioContext unavailable");
          }
          audioContext = new AudioContextCtor();
          window.__musicAgentAudioGuard?.trackContext?.(audioContext);
        }
        return audioContext;
      }

      async function resumeAudioContext(reason = "playback") {
        const context = getOrCreateAudioContext();
        if (context.state === "closed") {
          audioContext = null;
          if (typeof soundfontCache !== "undefined") soundfontCache.clear();
          return resumeAudioContext(reason);
        }
        if (context.state !== "suspended") {
          return context;
        }
        if (!audioResumeInFlight) {
          audioResumeInFlight = context.resume()
            .catch((error) => {
              console.warn(`AudioContext resume failed during ${reason}.`, error);
              throw error;
            })
            .finally(() => {
              audioResumeInFlight = null;
            });
        }
        await audioResumeInFlight;
        return getOrCreateAudioContext();
      }

      async function ensureAudioReady(reason = "playback") {
        const context = getOrCreateAudioContext();
        if (context.state === "running") {
          return context;
        }
        return resumeAudioContext(reason);
      }

      function installAudioActivationHooks() {
        if (audioActivationInstalled) return;
        audioActivationInstalled = true;
        const wakeAudio = () => {
          resumeAudioContext("gesture").catch(() => {});
        };
        ["pointerdown", "pointerup", "touchstart", "touchend", "mousedown", "keydown", "click"].forEach((eventName) => {
          document.addEventListener(eventName, wakeAudio, { passive: true, capture: true });
        });
        document.addEventListener("visibilitychange", () => {
          if (document.visibilityState === "visible") {
            resumeAudioContext("visibilitychange").catch(() => {});
          }
        });
        window.addEventListener("focus", () => {
          resumeAudioContext("window-focus").catch(() => {});
        });
        window.addEventListener("pageshow", () => {
          resumeAudioContext("pageshow").catch(() => {});
        });
      }
"""
        updated = updated.replace(
            "      let audioContext = null;\n      let activeClipAudio = null;\n      let latestPlayback = null;\n      let latestInstrument = spec.listening?.instrument || \"preserve\";\n",
            "      let audioContext = null;\n      let activeClipAudio = null;\n      let latestPlayback = null;\n      let latestInstrument = spec.listening?.instrument || \"preserve\";\n" + helper + "\n",
            1,
        )

    if "audioContext = audioContext || new AudioContext();" in updated:
        updated = updated.replace("audioContext = audioContext || new AudioContext();", "await ensureAudioReady(\"playback\");")

    if "renderChrome();" in updated and "installAudioActivationHooks();" not in updated:
        updated = updated.replace("      renderChrome();", "      installAudioActivationHooks();\n      renderChrome();", 1)

    return updated


def _page_uses_audio_playback(content: str) -> bool:
    return any(token in content for token in ["AudioContext", ".play(", "Soundfont.instrument", "soundfont-player"])


def _has_audio_playback_guard(content: str) -> bool:
    return "__musicAgentAudioGuardInstalled" in content


def _brain_alignment(brain_report: dict[str, Any] | None) -> dict[str, Any]:
    if not brain_report:
        return {"available": False}
    critique = brain_report.get("self_critique", {})
    return {
        "available": True,
        "brain_score": critique.get("score"),
        "brain_verdict": critique.get("verdict"),
        "brain_summary": critique.get("summary", ""),
    }


def _write_execution_report(target_dir: Path, report: dict[str, Any]) -> str:
    path = target_dir / "config" / "execution-report.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return _relative_output_url(target_dir, path)


def _next_version_number(versions_dir: Path) -> int:
    numbers = []
    for child in versions_dir.iterdir():
        if child.is_dir() and re.fullmatch(r"v\d{3}", child.name):
            numbers.append(int(child.name[1:]))
    return max(numbers, default=0) + 1


def _missing_local_assets(content: str, target_dir: Path) -> list[str]:
    missing = []
    for reference in _local_asset_references(content):
        if not (target_dir / reference).exists():
            missing.append(reference)
    return missing


def _local_asset_references(content: str) -> list[str]:
    references: list[str] = []
    for pattern in (r"""<link[^>]+href=["']([^"']+)["']""", r"""<script[^>]+src=["']([^"']+)["']"""):
        for match in re.findall(pattern, content, flags=re.IGNORECASE):
            reference = match.strip()
            if not reference or reference.startswith(("#", "/", "http://", "https://", "data:", "mailto:")):
                continue
            references.append(reference.split("?", 1)[0].split("#", 1)[0])
    return references


def _technical_terms_in_ui(content: str) -> list[str]:
    visible = re.sub(r"<script\b[^>]*>.*?</script>", "", content, flags=re.I | re.S)
    visible = re.sub(r"<style\b[^>]*>.*?</style>", "", visible, flags=re.I | re.S)
    visible = re.sub(r"<[^>]+>", " ", visible)
    return [term for term in TECHNICAL_UI_TERMS if term.lower() in visible.lower()]


def _uses_sampled_instrument_playback(content: str) -> bool:
    lower = content.lower()
    return any(
        token in lower
        for token in [
            "soundfont-player",
            "soundfont.instrument",
            "fluidr3_gm",
            "tone.sampler",
            "new tone.sampler",
            "<audio",
            "decodeaudiodata",
        ]
    )


def _uses_real_lesson_sound_source(content: str) -> bool:
    lower = content.lower()
    return any(
        token in lower
        for token in [
            "soundfont.instrument",
            "fluidr3_gm",
            "tone.sampler",
            "<audio",
            "decodeaudiodata",
            "audio_clip_url",
            "source_audio_url",
            "playback_tokens",
        ]
    )


def _uses_uploaded_lesson_audio(content: str, sound_source_policy: dict[str, Any]) -> bool:
    source_audio_url = str(sound_source_policy.get("source_audio_url") or "").strip()
    if not source_audio_url:
        return False
    if source_audio_url in content:
        return True
    return "audio_clip_url" in content or "<audio" in content.lower()


def _uses_oscillator_synthesis(content: str) -> bool:
    lower = content.lower()
    return "createoscillator" in lower or ".type = 'sine'" in lower or '.type = "sine"' in lower


def _blocking_browser_console_errors(content: str, browser_details: dict[str, Any]) -> list[str]:
    errors = list(browser_details.get("console_errors") or []) + list(browser_details.get("page_errors") or [])
    if not errors:
        return []
    lower = content.lower()
    filtered: list[str] = []
    for error in errors:
        text = str(error or "")
        if (
            "failed to load resource: net::err_file_not_found" in text.lower()
            and "/runtime-assets/" in lower
        ):
            # Playwright opens local artifacts through file:// during QA, while the app serves
            # runtime assets over HTTP in production preview. Keep real JS errors blocking.
            continue
        filtered.append(text)
    return filtered


def _has_interaction(content: str) -> bool:
    lower = content.lower()
    return any(token in lower for token in ["<button", "<form", "<select", "draggable", "addEventListener".lower(), "onclick"])


def _default_artifact_summary(spec: dict[str, Any], agent_results: dict[str, Any]) -> str:
    status_lines = [
        f"- {agent_id}: {result.get('status', 'unknown')}"
        for agent_id, result in agent_results.items()
        if isinstance(result, dict)
    ]
    return "\n".join(
        [
            "# 产物执行摘要",
            "",
            f"- 标题：{spec.get('title', '音乐课堂工具')}",
            f"- 活动类型：{spec.get('activity_type', 'mixed')}",
            "- 自动摘要：Repair Agent 补写该文件，用于记录本次执行层验收状态。",
            "",
            "## 执行智能体状态",
            "",
            *status_lines,
            "",
        ]
    )


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def html_escape(value: str) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#039;")
    )


def short_text(value: str, limit: int) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "…"


def _text_aligns(source: str, target: str) -> bool:
    source_text = str(source or "").strip()
    target_text = str(target or "").strip()
    if not source_text or not target_text:
        return False
    if target_text in source_text or source_text in target_text:
        return True
    level_match = re.search(r"([一二三四五六七八九十0-9]+)\s*关", target_text)
    if level_match:
        level_number = _chinese_level_number(level_match.group(1))
        if level_number and re.search(rf"(第\s*)?{level_number}\s*关|关卡\s*{level_number}", source_text):
            return True
    tokens = [token for token in re.split(r"[，,、；;：:\s（）()]+", target_text) if len(token) >= 2]
    return any(token in source_text for token in tokens)


def _chinese_level_number(value: str) -> str:
    text = str(value or "").strip()
    if text.isdigit():
        return text
    numbers = {
        "一": "1",
        "二": "2",
        "三": "3",
        "四": "4",
        "五": "5",
        "六": "6",
        "七": "7",
        "八": "8",
        "九": "9",
        "十": "10",
    }
    return numbers.get(text, "")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _relative_output_url(target_dir: Path, path: Path) -> str:
    output_root = get_output_dir()
    try:
        return f"/output/{path.resolve().relative_to(output_root.resolve()).as_posix()}"
    except ValueError:
        return str(path.relative_to(target_dir))
