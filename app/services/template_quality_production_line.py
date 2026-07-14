from __future__ import annotations

from typing import Any


PRODUCTION_LINE_REPORT_VERSION = "template_quality_production_line_report_v1"


def build_template_quality_production_line_report(
    *,
    lesson_case: dict[str, Any] | None = None,
    selected_segment: dict[str, Any] | None = None,
    segment_game_brief: dict[str, Any] | None = None,
    music_game_production_spec: dict[str, Any],
    runtime_config: dict[str, Any] | None = None,
    teacher_control_config: dict[str, Any] | None = None,
    asset_validation: dict[str, Any] | None = None,
    browser_asset_qa: dict[str, Any] | None = None,
) -> dict[str, Any]:
    lesson_case = lesson_case if isinstance(lesson_case, dict) else {}
    selected_segment = selected_segment if isinstance(selected_segment, dict) else {}
    segment_game_brief = segment_game_brief if isinstance(segment_game_brief, dict) else {}
    runtime_config = runtime_config if isinstance(runtime_config, dict) else {}
    teacher_control_config = teacher_control_config if isinstance(teacher_control_config, dict) else {}
    asset_validation = asset_validation if isinstance(asset_validation, dict) else {}
    browser_asset_qa = browser_asset_qa if isinstance(browser_asset_qa, dict) else {}
    spec = music_game_production_spec

    steps = [
        _step(
            "lesson_segment_lock",
            "教案环节锁定",
            bool(lesson_case and (selected_segment.get("segment_id") or segment_game_brief.get("source_segment_id"))),
            "lesson_case 和 selected_teaching_segment 必须能定位到当前教学环节。",
            artifacts=["lesson-case.json", "selected-segment.json"],
        ),
        _step(
            "music_task_translation",
            "音乐任务转译",
            bool(segment_game_brief.get("music_learning_target") and segment_game_brief.get("student_actions")),
            "segment-game-brief.json 必须把教案语言转成学生音乐行为。",
            artifacts=["segment-game-brief.json"],
        ),
        _step(
            "original_game_concept",
            "原创玩法概念",
            _has_text(spec.get("original_game_concept"), "not_template_skin_reason"),
            "original-game-concept.json 必须说明不是 7 个模板换皮。",
            artifacts=["original-game-concept.json"],
        ),
        _step(
            "reusable_component_assembly",
            "查询可复用组件",
            _component_assembly_ready(spec.get("component_assembly_plan")),
            "component-assembly-plan.json 必须说明哪些能力复用组件库，并把原创需求映射到已登记组件和运行时绑定。",
            artifacts=["component-assembly-plan.json"],
        ),
        _step(
            "music_truth",
            "音乐真值生成",
            _dict(spec.get("music_truth")).get("truth_status") in {"usable", "draft"},
            "music-truth.json 必须给出可判定的音乐真值，低置信 blocked 不能进入运行时。",
            artifacts=["music-truth.json"],
        ),
        _step(
            "level_curve",
            "关卡曲线设计",
            _has_list(spec.get("level_curve"), "levels"),
            "level-curve.json 必须覆盖课堂 3-8 分钟活动曲线。",
            artifacts=["level-curve.json"],
        ),
        _step(
            "scene_bible",
            "课堂情境导演",
            isinstance(spec.get("scene_bible"), str) and "资产需求" in spec.get("scene_bible", ""),
            "scene-bible.md 必须说明课堂情境和资产方向。",
            artifacts=["scene-bible.md"],
        ),
        _step(
            "image_generation_tasks",
            "生图资产任务生成",
            _has_list(spec.get("asset_contract"), "assets") and isinstance(_dict(spec.get("image_generation_tasks")).get("tasks"), list),
            "asset-contract.json 和 image-generation-tasks.json 必须覆盖人物、场景、道具、奖励/反馈缺口。",
            artifacts=["asset-contract.json", "image-generation-tasks.json"],
        ),
        _step(
            "generated_assets_registered",
            "生图执行与资产入库",
            _assets_ready(spec),
            "generated-asset-registry.json 必须有可运行时使用的资产，pending 不能当最终交付。",
            artifacts=["generated-asset-registry.json", "image-generation-execution-report.json"],
            warning=_asset_generation_needs_model_output(spec),
            warning_reason="当前资产可运行但还未由智能体内部 image_gen 输出确认，不能宣传为最终高质量生图资产。",
        ),
        _step(
            "runtime_state_machine",
            "游戏状态机与运行时绑定",
            _state_machine_ready(spec.get("game_state_machine")) and bool(runtime_config.get("generated_asset_registry")),
            "game-state-machine.json 和 runtime-config.json 必须把游戏状态、资产和音乐任务绑定起来。",
            artifacts=["game-state-machine.json", "runtime-config.json"],
        ),
        _step(
            "teacher_control_binding",
            "教师控制端绑定",
            _has_list(teacher_control_config, "editable_controls"),
            "teacher-control-config.json 必须提供开始、暂停、重置、调速、提示等课堂控制能力。",
            artifacts=["teacher-control-config.json"],
        ),
        _step(
            "automatic_qa",
            "自动 QA 与阻断",
            _qa_ready(spec, asset_validation, browser_asset_qa),
            "QA 必须覆盖音乐逻辑、资产可见、移动端/投屏端浏览器检查。",
            artifacts=["qa-report.json", "asset-validation.json", "browser-asset-qa.json", "browser-qa-report.json"],
            warning=browser_asset_qa.get("status") == "ready_for_browser_screenshot",
            warning_reason="等待 Playwright 截图和真实浏览器渲染验证。",
        ),
    ]
    blocking = [step["id"] for step in steps if step["status"] == "blocked"]
    warnings = [step["id"] for step in steps if step["status"] == "warning"]
    delivery_status = final_delivery_status(blocking, warnings)
    return {
        "version": PRODUCTION_LINE_REPORT_VERSION,
        "source_plan": "升级规划/09-模板级原创游戏生产线执行清单.md",
        "status": "blocked" if blocking else "ready_with_warnings" if warnings else "pass",
        "preview_only": delivery_status == "preview_ready_needs_agent_image_gen",
        "final_delivery_status": delivery_status,
        "blocking_steps": blocking,
        "warning_steps": warnings,
        "steps": steps,
    }


def final_delivery_status(blocking_steps: list[str], warning_steps: list[str]) -> str:
    if blocking_steps:
        return "blocked"
    if "generated_assets_registered" in warning_steps:
        return "preview_ready_needs_agent_image_gen"
    if "automatic_qa" in warning_steps:
        return "final_assets_ready_pending_browser_qa"
    if warning_steps:
        return "ready_with_warnings"
    return "final_ready"


def _step(
    step_id: str,
    label: str,
    passed: bool,
    requirement: str,
    *,
    artifacts: list[str],
    warning: bool = False,
    warning_reason: str = "",
) -> dict[str, Any]:
    if passed:
        status = "warning" if warning else "pass"
    else:
        status = "blocked"
    item = {
        "id": step_id,
        "label": label,
        "status": status,
        "requirement": requirement,
        "artifacts": artifacts,
    }
    if warning and warning_reason:
        item["warning_reason"] = warning_reason
    return item


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _has_text(value: Any, key: str) -> bool:
    return bool(str(_dict(value).get(key) or "").strip())


def _has_list(value: Any, key: str) -> bool:
    return isinstance(_dict(value).get(key), list) and bool(_dict(value).get(key))


def _component_assembly_ready(value: Any) -> bool:
    plan = _dict(value)
    if not _has_list(plan, "reusable_components"):
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
        bindings = runtime_bindings.get(component_id)
        if not isinstance(bindings, list) or not bindings:
            return False
    return True


def _assets_ready(spec: dict[str, Any]) -> bool:
    registry = _dict(spec.get("generated_asset_registry"))
    reused = registry.get("reused_assets")
    pending = registry.get("pending_generation_assets")
    return isinstance(reused, list) and bool(reused) and not pending and registry.get("status") != "pending_generation"


def _asset_generation_needs_model_output(spec: dict[str, Any]) -> bool:
    tasks = _dict(spec.get("image_generation_tasks")).get("tasks")
    if not isinstance(tasks, list) or not tasks:
        return False
    report = _dict(spec.get("image_generation_execution_report"))
    registry = _dict(spec.get("generated_asset_registry"))
    sources = {
        str(asset.get("source") or "")
        for asset in registry.get("reused_assets", [])
        if isinstance(asset, dict)
    }
    if any(source == "agent_internal_image_gen" for source in sources):
        return False
    if report.get("image_gen_generated_count"):
        return False
    if report.get("status") in {"ready_with_fallback", "not_executed"}:
        return True
    return bool({"local_generated_fallback", "cached_generated_asset"} & sources)


def _state_machine_ready(value: Any) -> bool:
    machine = _dict(value)
    states = machine.get("states")
    if not isinstance(states, list):
        return False
    state_ids = {str(state.get("id")) for state in states if isinstance(state, dict)}
    required_states = {"start", "listen", "student_action", "judge", "feedback", "retry", "reward", "classroom_return"}
    bindings = machine.get("state_asset_bindings")
    if not isinstance(bindings, dict):
        return False
    required_bindings = {"start", "listen", "student_action", "feedback", "retry", "reward", "classroom_return"}
    bound_states = {
        str(state_id)
        for state_id, binding in bindings.items()
        if isinstance(binding, dict) and any(str(value or "").strip() for value in binding.values())
    }
    return required_states.issubset(state_ids) and required_bindings.issubset(bound_states)


def _qa_ready(spec: dict[str, Any], asset_validation: dict[str, Any], browser_asset_qa: dict[str, Any]) -> bool:
    qa_report = _dict(spec.get("qa_report"))
    if qa_report.get("status") == "blocked" or asset_validation.get("status") == "blocked":
        return False
    if browser_asset_qa.get("status") not in {"ready_for_browser_screenshot", "pass"}:
        return False
    return True
