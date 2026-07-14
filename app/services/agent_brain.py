from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

from app.services.activity_guidance import ACTIVITY_LABELS, infer_activity_type
from app.services.component_library import normalize_component_ids
from app.services.music_education_knowledge import evaluate_music_education_fit, knowledge_context_for_need


VALID_ACTIVITY_TYPES = {"listening", "performance", "creation", "music_game", "mixed"}
TECHNICAL_UI_TERMS = ["OpenCode", "API", "Basic Pitch", "MIDI", "backend", "模型", "接口"]


def prepare_brain_report(
    need: str,
    spec: dict[str, Any],
    *,
    action: str = "generate",
    revision: str = "",
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Run the pre-render brain loop and return a hardened spec plus report."""

    original_critique = critique_spec(need, spec)
    hardened_spec = harden_spec(need, spec, original_critique)
    final_critique = critique_spec(need, hardened_spec)
    report = {
        "version": "brain-loop-v1",
        "action": action,
        "safe_reasoning_note": "为保护稳定性，这里展示可复核的规划摘要、检查项和改进建议，不展示模型原始隐藏思维链。",
        "music_education": knowledge_context_for_need(need, hardened_spec),
        "planning": build_planning_summary(need, hardened_spec, action=action, revision=revision),
        "subgoals": decompose_subgoals(hardened_spec, action=action),
        "self_critique": final_critique,
        "auto_hardening": {
            "applied": hardened_spec != spec,
            "changes": summarize_hardening_changes(spec, hardened_spec),
            "before_score": original_critique["score"],
            "after_score": final_critique["score"],
        },
        "reflection": {},
    }
    return hardened_spec, report


def complete_brain_report(
    brain_report: dict[str, Any],
    spec: dict[str, Any],
    *,
    opencode_run: dict[str, Any] | None = None,
    artifact_path: str | Path | None = None,
) -> dict[str, Any]:
    """Attach post-generation reflection to an existing brain report."""

    completed = copy.deepcopy(brain_report)
    completed["reflection"] = reflect_on_generation(spec, opencode_run=opencode_run, artifact_path=artifact_path)
    return completed


def build_planning_summary(need: str, spec: dict[str, Any], *, action: str, revision: str = "") -> dict[str, Any]:
    activity_type = spec.get("activity_type", "mixed")
    inferred_type = infer_activity_type(need)
    interaction = spec.get("interaction_model", {})
    runtime = spec.get("runtime_behaviors", {})
    selected_components = interaction.get("components", [])

    decisions = [
        f"活动类型定位为：{ACTIVITY_LABELS.get(activity_type, '综合活动')}。",
        f"面向学段：{spec.get('grade_band', '小学')}；曲目/素材：{spec.get('song_name', '自选歌曲')}。",
        f"主要交互：{interaction.get('primary', '课堂互动工具')}。",
        f"运行策略：{'需要上传音频' if runtime.get('requires_audio_upload') else '不强制上传音频'}，支持重置和继续修改。",
    ]
    if inferred_type != "unknown" and inferred_type != activity_type and activity_type != "mixed":
        decisions.append(f"需求关键词也可能指向 {ACTIVITY_LABELS.get(inferred_type, inferred_type)}，因此后续自检会重点检查活动匹配度。")
    if revision.strip():
        decisions.append("这是一次增量修改，规划会优先保留原有课堂目标，只调整用户明确要求的部分。")

    return {
        "objective": _objective_for_spec(spec, action),
        "activity_type": activity_type,
        "decisions": decisions,
        "constraints": [
            "生成结果必须是独立课堂工具页面，而不是智能体主界面的一部分。",
            "页面文案面向教师和学生，避免暴露底层模型、接口和工程术语。",
            "每个活动至少要有可操作任务、反馈方式、重置入口和课堂讨论提示。",
            "只有聆听或综合活动才应该要求上传音频。",
        ],
        "selected_components": selected_components,
    }


def decompose_subgoals(spec: dict[str, Any], *, action: str) -> list[dict[str, str]]:
    subgoals = [
        {
            "id": "understand_need",
            "title": "理解课堂需求",
            "deliverable": "确认活动类型、学段、曲目和核心教学目标。",
            "status": "done",
        },
        {
            "id": "design_interaction",
            "title": "设计交互结构",
            "deliverable": "选择组件、学生动作、教师控制和产出方式。",
            "status": "done",
        },
        {
            "id": "critic_check",
            "title": "自检教学可用性",
            "deliverable": "检查目标匹配、互动闭环、评价规则和技术边界。",
            "status": "done",
        },
        {
            "id": "build_artifact",
            "title": "生成或修改网页产物",
            "deliverable": "写出可打开、可继续修改的课堂工具页面。",
            "status": "pending" if action == "generate" else "active",
        },
    ]

    if spec.get("performance", {}).get("enabled"):
        subgoals.insert(
            2,
            {
                "id": "level_decomposition",
                "title": "拆分表现关卡",
                "deliverable": "把表现训练拆成逐步升级的关卡、任务和通关规则。",
                "status": "done",
            },
        )
    if spec.get("creation", {}).get("enabled"):
        subgoals.insert(
            2,
            {
                "id": "creation_materials",
                "title": "准备创作素材",
                "deliverable": "生成可拖拽、可试听、可说明理由的创作素材。",
                "status": "done",
            },
        )
    if spec.get("music_game", {}).get("enabled"):
        subgoals.insert(
            2,
            {
                "id": "game_loop",
                "title": "定义游戏循环",
                "deliverable": "明确角色、操作、即时反馈、胜利条件和重玩方式。",
                "status": "done",
            },
        )
    return subgoals


def critique_spec(need: str, spec: dict[str, Any]) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    activity_type = spec.get("activity_type", "")
    _add_check(
        checks,
        "activity_type",
        "活动类型明确",
        activity_type in VALID_ACTIVITY_TYPES,
        f"当前活动类型是 {activity_type or '未设置'}。",
        "把活动类型限制为 listening、performance、creation、music_game 或 mixed。",
        priority=3,
    )
    _check_need_preservation(checks, need, spec)
    _check_interaction(checks, spec)
    _check_activity_rules(checks, spec)
    _check_runtime_rules(checks, spec)
    _check_scoring(checks, spec)
    _check_visual_and_language(checks, spec)
    _check_music_education_fit(checks, spec)

    score = 100
    for check in checks:
        if check["status"] == "fail":
            score -= 12 + check["priority"] * 2
        elif check["status"] == "warn":
            score -= 5 + check["priority"]
    score = max(0, min(100, score))
    failed = [check for check in checks if check["status"] == "fail"]
    warned = [check for check in checks if check["status"] == "warn"]
    verdict = "ready" if score >= 85 and not failed else "needs_revision" if score >= 70 else "blocked"

    return {
        "score": score,
        "verdict": verdict,
        "summary": _critique_summary(score, failed, warned),
        "checks": checks,
        "strengths": _strengths_for_spec(spec),
        "risks": [check["message"] for check in failed + warned][:5],
        "recommended_fixes": [check["fix"] for check in failed + warned if check.get("fix")][:6],
    }


def harden_spec(need: str, spec: dict[str, Any], critique: dict[str, Any]) -> dict[str, Any]:
    hardened = copy.deepcopy(spec)
    activity_type = hardened.get("activity_type", "mixed")
    if activity_type not in VALID_ACTIVITY_TYPES:
        activity_type = infer_activity_type(need)
        hardened["activity_type"] = "mixed" if activity_type == "unknown" else activity_type

    interaction = hardened.setdefault("interaction_model", {})
    components = normalize_component_ids(_string_list(interaction.get("components")))
    components = _merge_unique(components, _required_components_for_spec(need, hardened))
    interaction["components"] = components
    interaction.setdefault("primary", _fallback_primary_interaction(hardened))
    interaction["student_actions"] = _string_list(
        interaction.get("student_actions"),
        ["观察任务提示", "完成操作挑战", "听辨或试听结果", "说出音乐理由"],
    )
    interaction["teacher_controls"] = _string_list(
        interaction.get("teacher_controls"),
        ["开始活动", "重置进度", "查看反馈", "组织课堂讨论"],
    )
    interaction["artifact_outputs"] = _string_list(
        interaction.get("artifact_outputs"),
        ["课堂作品或挑战记录", "学生反思", "教师评价线索"],
    )

    runtime = hardened.setdefault("runtime_behaviors", {})
    runtime["resettable"] = True
    runtime["allow_continue_revision"] = True
    runtime.setdefault("save_progress", activity_type in {"performance", "music_game", "mixed"})
    runtime.setdefault("unlock_next_step", activity_type in {"performance", "mixed"})
    runtime.setdefault("countdown", activity_type in {"performance", "music_game"})
    runtime.setdefault("auto_play_after_start", activity_type == "music_game")
    runtime.setdefault("allow_teacher_override", activity_type in {"performance", "music_game", "mixed"})
    runtime["playback"] = (
        "sampled_soundfont_first"
        if activity_type in {"performance", "creation", "music_game", "mixed"}
        else runtime.get("playback", "audio_compare_with_sampled_soundfont_preview")
    )
    if activity_type in {"performance", "creation", "music_game"}:
        runtime["requires_audio_upload"] = False
    else:
        runtime.setdefault("requires_audio_upload", activity_type in {"listening", "mixed"})

    scoring = hardened.setdefault("scoring", {})
    scoring.setdefault("enabled", True)
    scoring.setdefault("feedback_mode", "guided_summary")
    scoring.setdefault("pass_score", 75 if activity_type != "listening" else 0)
    if isinstance(scoring.get("metrics"), list):
        scoring["metrics"] = _normalize_metric_weights(scoring["metrics"])

    notes = _string_list(hardened.get("teacher_notes"))
    if not any("自检" in note for note in notes):
        notes.append("智能体已完成生成前自检：确认活动目标、交互组件、评价反馈和课堂讨论闭环。")
    education_fit = evaluate_music_education_fit(hardened)
    profile = education_fit.get("grade_profile", {})
    if profile and not any("学段能力" in note for note in notes):
        notes.append(f"学段能力提示：{profile.get('label', '当前学段')}适合关注{'、'.join(profile.get('abilities', [])[:3])}。")
    repertoire = education_fit.get("repertoire")
    if repertoire and not any("曲目重点" in note for note in notes):
        notes.append(f"曲目重点提示：《{repertoire['title']}》适合突出{'、'.join(repertoire.get('teaching_points', [])[:3])}。")
    hardened["teacher_notes"] = notes
    return hardened


def summarize_hardening_changes(before: dict[str, Any], after: dict[str, Any]) -> list[str]:
    changes: list[str] = []
    before_components = before.get("interaction_model", {}).get("components", [])
    after_components = after.get("interaction_model", {}).get("components", [])
    added_components = [component for component in after_components if component not in before_components]
    if added_components:
        changes.append(f"补齐交互组件：{'、'.join(added_components)}。")
    before_runtime = before.get("runtime_behaviors", {})
    after_runtime = after.get("runtime_behaviors", {})
    if before_runtime != after_runtime:
        changes.append("加固运行行为：确保可重置、可继续修改，并校正音频上传边界。")
    before_notes = before.get("teacher_notes", [])
    after_notes = after.get("teacher_notes", [])
    if len(after_notes) > len(before_notes):
        changes.append("加入生成前自检说明，方便教师理解产物质量。")
    if not changes:
        changes.append("规格已通过自检，无需额外自动修正。")
    return changes


def reflect_on_generation(
    spec: dict[str, Any],
    *,
    opencode_run: dict[str, Any] | None,
    artifact_path: str | Path | None,
) -> dict[str, Any]:
    run = opencode_run or {}
    validation_errors = run.get("validation_errors") or []
    changed = bool(run.get("artifact_changed"))
    status = run.get("status", "unknown")
    artifact_exists = False
    if artifact_path:
        try:
            artifact_exists = Path(artifact_path).exists()
        except OSError:
            artifact_exists = False

    observations = [
        f"产物生成状态：{status}。",
        f"网页文件：{'已找到' if artifact_exists else '未确认'}。",
        f"产物文件变化：{'有更新' if changed else '未检测到明显变化'}。",
    ]
    if validation_errors:
        observations.append(f"页面校验发现问题：{'；'.join(str(error) for error in validation_errors[:3])}。")
    else:
        observations.append("页面基础校验通过：没有发现缺失 index.html 或本地资源引用错误。")

    next_steps = []
    if validation_errors:
        next_steps.append("优先修复页面完整性或缺失资源，再进行教学细节优化。")
    if not changed and run.get("enabled"):
        next_steps.append("OpenCode 执行后未检测到文件变化，建议重新生成或查看执行日志。")
    if spec.get("performance", {}).get("enabled"):
        next_steps.append("课堂试用时重点观察关卡难度是否逐级上升。")
    if spec.get("creation", {}).get("enabled"):
        next_steps.append("课堂试用时重点观察学生能否听见自己的创作结果并说明理由。")
    if spec.get("music_game", {}).get("enabled"):
        next_steps.append("课堂试用时重点观察游戏规则是否能让学生练到指定音乐概念。")
    if spec.get("listening", {}).get("enabled"):
        next_steps.append("课堂试用时重点观察学生是否能用音乐词汇描述听觉差异。")

    return {
        "status": "passed" if not validation_errors else "needs_follow_up",
        "observations": observations,
        "next_steps": _merge_unique(next_steps, ["如果老师提出修改要求，优先做小步增量修改而不是重做整页。"]),
    }


def _check_need_preservation(checks: list[dict[str, Any]], need: str, spec: dict[str, Any]) -> None:
    song_in_need = ""
    if "《" in need and "》" in need:
        song_in_need = need.split("《", 1)[1].split("》", 1)[0].strip()
    if song_in_need:
        _add_check(
            checks,
            "song_preserved",
            "保留指定曲目",
            song_in_need in str(spec.get("song_name", "")) or song_in_need in str(spec.get("title", "")),
            f"需求指定《{song_in_need}》，当前曲目是 {spec.get('song_name', '未设置')}。",
            f"把曲目设置为《{song_in_need}》，并在标题或任务里体现。",
            priority=3,
        )

    if any(grade in need for grade in ["小学", "初中", "高中"]):
        requested_grade = next(grade for grade in ["小学", "初中", "高中"] if grade in need)
        _add_check(
            checks,
            "grade_preserved",
            "保留指定学段",
            requested_grade in str(spec.get("grade_band", "")),
            f"需求指定{requested_grade}，当前学段是 {spec.get('grade_band', '未设置')}。",
            f"把学段设置为{requested_grade}。",
            priority=2,
        )


def _check_interaction(checks: list[dict[str, Any]], spec: dict[str, Any]) -> None:
    interaction = spec.get("interaction_model", {})
    components = interaction.get("components", [])
    _add_check(
        checks,
        "components_present",
        "交互组件完整",
        isinstance(components, list) and len(components) >= 3,
        f"当前组件数量为 {len(components) if isinstance(components, list) else 0}。",
        "至少配置核心操作组件、反馈组件和反思组件。",
        priority=3,
        warn_only=True,
    )
    _add_check(
        checks,
        "reflection_present",
        "包含课堂反思闭环",
        "reflection_panel" in components,
        "当前组件中缺少 reflection_panel。",
        "加入 reflection_panel，让学生把操作转化为音乐语言。",
        priority=2,
        warn_only=True,
    )
    _add_check(
        checks,
        "student_actions_present",
        "学生动作明确",
        bool(interaction.get("student_actions")),
        "学生动作没有明确列出。",
        "补充学生需要点击、拖拽、听辨、演唱或说明理由的具体动作。",
        priority=2,
        warn_only=True,
    )


def _check_activity_rules(checks: list[dict[str, Any]], spec: dict[str, Any]) -> None:
    if spec.get("performance", {}).get("enabled"):
        levels = spec["performance"].get("levels", [])
        _add_check(
            checks,
            "performance_levels",
            "表现关卡可执行",
            isinstance(levels, list) and len(levels) >= 3,
            f"表现关卡数量为 {len(levels) if isinstance(levels, list) else 0}。",
            "生成至少 3 个递进关卡，并写清任务与通关规则。",
            priority=3,
        )
    if spec.get("creation", {}).get("enabled"):
        pieces = spec["creation"].get("pieces", [])
        components = spec.get("interaction_model", {}).get("components", [])
        _add_check(
            checks,
            "creation_materials",
            "创造素材可操作",
            isinstance(pieces, list) and len(pieces) >= 4,
            f"创造素材数量为 {len(pieces) if isinstance(pieces, list) else 0}。",
            "补充足够的音高、节奏或乐句素材。",
            priority=2,
            warn_only=True,
        )
        _add_check(
            checks,
            "creation_playback",
            "创造活动可试听",
            "playback_controls" in components,
            "创造活动缺少试听/停止/重置控件。",
            "加入 playback_controls，让学生能听见自己的作品。",
            priority=3,
        )
    if spec.get("music_game", {}).get("enabled"):
        game = spec.get("music_game", {})
        _add_check(
            checks,
            "game_loop",
            "小游戏循环完整",
            bool(game.get("rules")) and bool(game.get("student_actions")) and bool(game.get("win_condition")),
            "小游戏缺少规则、学生动作或胜利条件。",
            "补齐规则、操作、即时反馈、胜利条件和重新挑战。",
            priority=3,
        )


def _check_runtime_rules(checks: list[dict[str, Any]], spec: dict[str, Any]) -> None:
    runtime = spec.get("runtime_behaviors", {})
    activity_type = spec.get("activity_type", "mixed")
    _add_check(
        checks,
        "resettable",
        "支持重置",
        bool(runtime.get("resettable")),
        "当前运行行为没有确认支持重置。",
        "设置 resettable=true，避免课堂试错后无法重新开始。",
        priority=2,
        warn_only=True,
    )
    if activity_type in {"performance", "creation", "music_game"}:
        _add_check(
            checks,
            "audio_boundary",
            "音频上传边界正确",
            not bool(runtime.get("requires_audio_upload")),
            f"{activity_type} 类型不应强制上传音频。",
            "只在聆听或综合活动中要求上传音频。",
            priority=3,
        )


def _check_scoring(checks: list[dict[str, Any]], spec: dict[str, Any]) -> None:
    scoring = spec.get("scoring", {})
    metrics = scoring.get("metrics", [])
    _add_check(
        checks,
        "scoring_metrics",
        "评价维度明确",
        isinstance(metrics, list) and len(metrics) >= 2,
        f"当前评价维度数量为 {len(metrics) if isinstance(metrics, list) else 0}。",
        "至少提供两个评价维度，并说明反馈方式。",
        priority=2,
        warn_only=True,
    )
    if isinstance(metrics, list) and metrics:
        total_weight = sum(float(metric.get("weight", 0)) for metric in metrics if isinstance(metric, dict))
        _add_check(
            checks,
            "scoring_weights",
            "评价权重合理",
            0.85 <= total_weight <= 1.15,
            f"当前评价权重合计为 {total_weight:.2f}。",
            "把评价权重归一到约 1.0。",
            priority=1,
            warn_only=True,
        )


def _check_visual_and_language(checks: list[dict[str, Any]], spec: dict[str, Any]) -> None:
    theme = spec.get("visual_theme", {})
    palette = theme.get("palette", [])
    _add_check(
        checks,
        "visual_theme",
        "视觉方向明确",
        bool(theme.get("name")) and isinstance(palette, list) and len(palette) >= 3,
        "视觉主题或配色不完整。",
        "补充主题名称、版式、配色、插图和动效方向。",
        priority=1,
        warn_only=True,
    )
    title_text = f"{spec.get('title', '')} {spec.get('subtitle', '')}"
    leaked_terms = [term for term in TECHNICAL_UI_TERMS if term.lower() in title_text.lower()]
    _add_check(
        checks,
        "student_facing_language",
        "学生界面不暴露技术词",
        not leaked_terms,
        f"标题或副标题包含技术词：{'、'.join(leaked_terms)}。",
        "把工程术语改成课堂语言，例如试听、创作、挑战、反馈。",
        priority=2,
    )


def _check_music_education_fit(checks: list[dict[str, Any]], spec: dict[str, Any]) -> None:
    fit = evaluate_music_education_fit(spec)
    _add_check(
        checks,
        "music_education_fit",
        "符合音乐教育知识库",
        fit["score"] >= 76,
        f"音乐教育适配得分 {fit['score']}，建议结合学段能力、课程素养和曲目特点再优化。",
        "根据知识库建议补充学段支架、核心素养覆盖或曲目教学重点。",
        priority=2,
        warn_only=True,
    )
    for recommendation in fit.get("recommendations", [])[:2]:
        _add_check(
            checks,
            f"music_education_recommendation_{len(checks)}",
            "音乐教育优化建议",
            False,
            recommendation,
            recommendation,
            priority=1,
            warn_only=True,
        )


def _add_check(
    checks: list[dict[str, Any]],
    check_id: str,
    label: str,
    passed: bool,
    message: str,
    fix: str,
    *,
    priority: int,
    warn_only: bool = False,
) -> None:
    checks.append(
        {
            "id": check_id,
            "label": label,
            "status": "pass" if passed else "warn" if warn_only else "fail",
            "priority": priority,
            "message": "通过。" if passed else message,
            "fix": "" if passed else fix,
        }
    )


def _required_components_for_spec(need: str, spec: dict[str, Any]) -> list[str]:
    components: list[str] = []
    if spec.get("listening", {}).get("enabled"):
        components.extend(["audio_upload_compare", "element_control_panel", "playback_controls", "reflection_panel"])
    if spec.get("performance", {}).get("enabled"):
        components.extend(["level_map", "countdown_start", "timing_feedback", "badge_progress", "reflection_panel"])
        if any(word in need for word in ["节奏", "敲击", "拍点", "打击"]):
            components.append("rhythm_tap_pads")
    if spec.get("creation", {}).get("enabled"):
        components.extend(["drag_drop_puzzle", "playback_controls", "reflection_panel"])
        creation_mode = str(spec.get("creation", {}).get("creation_mode", ""))
        if any(word in need for word in ["网格", "旋律线", "画线"]) or "grid" in creation_mode:
            components.append("melody_grid")
        if "双声部" in need or "two_voice" in creation_mode:
            components.append("voice_instrument_mixer")
    if spec.get("music_game", {}).get("enabled"):
        components.extend(["playback_controls", "timing_feedback", "badge_progress", "reflection_panel"])
        if any(word in need for word in ["拖拽", "排列", "拼", "角色", "动物"]):
            components.append("drag_drop_puzzle")
        if any(word in need for word in ["倒计时", "赛跑", "闯关"]):
            components.append("countdown_start")
    return normalize_component_ids(components)


def _normalize_metric_weights(metrics: list[Any]) -> list[dict[str, Any]]:
    clean_metrics = [metric for metric in metrics if isinstance(metric, dict)]
    total = sum(float(metric.get("weight", 0)) for metric in clean_metrics)
    if not clean_metrics or total <= 0:
        return clean_metrics
    if 0.85 <= total <= 1.15:
        return clean_metrics
    normalized = []
    for metric in clean_metrics:
        item = copy.deepcopy(metric)
        item["weight"] = round(float(metric.get("weight", 0)) / total, 2)
        normalized.append(item)
    return normalized


def _objective_for_spec(spec: dict[str, Any], action: str) -> str:
    verb = "修改" if action == "revise" else "生成"
    return f"{verb}一个适合{spec.get('grade_band', '小学')}使用的《{spec.get('song_name', '自选歌曲')}》{ACTIVITY_LABELS.get(spec.get('activity_type', 'mixed'), '音乐课堂')}工具。"


def _fallback_primary_interaction(spec: dict[str, Any]) -> str:
    activity_type = spec.get("activity_type", "mixed")
    return {
        "listening": "听辨对比与音乐要素调节",
        "performance": "逐关解锁的表现挑战",
        "creation": "拖拽拼图与试听创作",
        "music_game": "可重玩的音乐概念小游戏",
        "mixed": "聆听、表现、创造三阶段课堂工作台",
    }.get(activity_type, "音乐课堂互动")


def _critique_summary(score: int, failed: list[dict[str, Any]], warned: list[dict[str, Any]]) -> str:
    if not failed and not warned:
        return f"自检得分 {score}，规格完整，可以进入产物生成。"
    if failed:
        return f"自检得分 {score}，发现 {len(failed)} 个必须修复项和 {len(warned)} 个建议优化项。"
    return f"自检得分 {score}，没有阻断问题，但有 {len(warned)} 个可优化项。"


def _strengths_for_spec(spec: dict[str, Any]) -> list[str]:
    strengths = [
        "已形成结构化产物规格，便于继续修改和生成网页。",
        "已包含交互模型、评价方式、运行行为和视觉方向。",
    ]
    if spec.get("performance", {}).get("enabled"):
        strengths.append("表现训练已有分关卡设计，适合课堂递进。")
    if spec.get("creation", {}).get("enabled"):
        strengths.append("创造活动已有素材和试听方向，利于学生表达想法。")
    if spec.get("music_game", {}).get("enabled"):
        strengths.append("小游戏已有规则和胜利条件，利于把概念转成操作。")
    if spec.get("listening", {}).get("enabled"):
        strengths.append("聆听活动已区分音乐要素，利于对比讨论。")
    return strengths


def _string_list(value: Any, fallback: list[str] | None = None) -> list[str]:
    if isinstance(value, list):
        result = [str(item).strip() for item in value if str(item).strip()]
    elif isinstance(value, str) and value.strip():
        result = [value.strip()]
    else:
        result = []
    return result or list(fallback or [])


def _merge_unique(values: list[str], additions: list[str]) -> list[str]:
    merged = list(values)
    for item in additions:
        if item not in merged:
            merged.append(item)
    return merged
