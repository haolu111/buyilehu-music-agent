from __future__ import annotations

import json
from typing import Any, Literal, TypedDict
from uuid import uuid4

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from app.services.orchestration import package_design_agent as design_agent
from app.services.music_content.music_content_registry import validate_and_resolve_music_content


# One targeted retry keeps the total design + audit budget below the
# Java request timeout and still allows malformed structured output repair.
MAX_DESIGN_RETRIES = 1


class PackageDesignState(TypedDict, total=False):
    trace_id: str
    lesson: dict[str, Any]
    preferences: dict[str, Any]
    require_teacher_review: bool
    quality_review_mode: Literal["rules", "hybrid"]
    candidate: dict[str, Any]
    package: dict[str, Any]
    built_nodes: list[dict[str, Any]]
    validation_errors: list[str]
    quality_report: dict[str, Any]
    teacher_review: dict[str, Any]
    node_feedback: list[dict[str, Any]]
    provider: str
    model: str | None
    errors: list[str]
    retry_count: int
    fallback_used: bool


def _design(state: PackageDesignState) -> dict[str, Any]:
    errors = list(state.get("errors", []))
    feedback = _repair_feedback(state)
    lesson = dict(state["lesson"])
    preferences = dict(state.get("preferences", {}))
    if feedback:
        preferences["revision_feedback"] = feedback

    for config in (design_agent._ecnu_config(), design_agent._doubao_config()):
        if not config.get("enabled"):
            errors.append(f"{config['provider']}: not configured")
            continue
        try:
            candidate = design_agent._call_model(
                config, lesson=lesson, preferences=preferences,
            )
            return {
                "candidate": candidate,
                "provider": config["provider"],
                "model": config.get("model"),
                "errors": errors,
                "validation_errors": [],
            }
        except Exception as exc:
            errors.append(f"{config['provider']}: {design_agent._short_error(exc)}")

    return {"errors": errors, "candidate": {}}


def _validate(state: PackageDesignState) -> dict[str, Any]:
    try:
        package = design_agent._validate_design(
            state.get("candidate", {}), lesson=state["lesson"],
        )
        package["design"] = {
            "provider": state.get("provider"),
            "model": state.get("model"),
            "fallback_reason": "; ".join(state.get("errors", [])) or None,
            "trace_id": state["trace_id"],
            "orchestration": "langgraph-stategraph",
        }
        return {"package": package, "validation_errors": []}
    except Exception as exc:
        return {
            "validation_errors": [design_agent._short_error(exc)],
            "retry_count": state.get("retry_count", 0) + 1,
        }


def _route_validation(state: PackageDesignState) -> str:
    if not state.get("validation_errors"):
        return "build"
    if state.get("retry_count", 0) <= MAX_DESIGN_RETRIES and any(
        config.get("enabled")
        for config in (design_agent._ecnu_config(), design_agent._doubao_config())
    ):
        return "retry"
    return "fallback"


def _build_activity_materials(state: PackageDesignState) -> dict[str, Any]:
    nodes = []
    for step in state["package"]["steps"]:
        nodes.append({
            "node_id": step.get("node_id"),
            "entity_id": step.get("entity_id"),
            "activity_id": step["activity_id"],
            "title": step["title"],
            "node_type": step["node_type"],
            "component_keys": list(step.get("component_keys", [])),
            "material_requirements": _material_requirements(step),
            "music_content": step.get("music_content", {}),
            "resolved_music_content": step.get("resolved_music_content", {}),
            "build_status": "ready",
        })
    package = dict(state["package"])
    package["built_nodes"] = nodes
    return {"package": package, "built_nodes": nodes}


def _quality_review(state: PackageDesignState) -> dict[str, Any]:
    rule_report = _rule_quality_report(state)
    if state.get("quality_review_mode") != "hybrid":
        update: dict[str, Any] = {"quality_report": rule_report}
        if not rule_report["passed"]:
            update["retry_count"] = state.get("retry_count", 0) + 1
        return update

    messages = _quality_messages(state, rule_report)
    errors = []
    for config in (design_agent._ecnu_config(), design_agent._doubao_config()):
        if not config.get("enabled"):
            errors.append(f"{config['provider']}: not configured")
            continue
        try:
            try:
                report = design_agent._call_model_messages(
                    config, messages=messages, max_tokens=900,
                )
            except json.JSONDecodeError:
                # Some OpenAI-compatible providers occasionally ignore the
                # JSON-only instruction. Retry the audit node itself once;
                # the package design and all already-built nodes stay intact.
                repair_messages = messages + [{
                    "role": "user",
                    "content": (
                        "上一条审计结果不是合法 JSON。请重新执行同一审计，只输出一个严格合法的 "
                        "JSON 对象：属性名和字符串必须使用双引号，数组项之间必须有逗号，"
                        "不要使用 Markdown 代码块或补充说明。"
                    ),
                }]
                report = design_agent._call_model_messages(
                    config, messages=repair_messages, max_tokens=900,
                )
            passed = bool(report.get("passed")) and rule_report["passed"]
            issues = report.get("issues") if isinstance(report.get("issues"), list) else []
            quality_report = {
                "passed": passed,
                "score": max(0, min(100, int(report.get("score", 0)))),
                "issues": rule_report["issues"] + issues,
                "provider": config["provider"],
                "model": config.get("model"),
                "rule_checks": rule_report["checks"],
            }
            update = {"quality_report": quality_report}
            if not passed:
                update["retry_count"] = state.get("retry_count", 0) + 1
                update["node_feedback"] = _quality_node_feedback(issues)
            return update
        except Exception as exc:
            errors.append(f"{config['provider']}: {design_agent._short_error(exc)}")

    rule_report["provider"] = "rule_fallback"
    rule_report["fallback_reason"] = "; ".join(errors)
    # A transient model timeout must not discard an otherwise valid package.
    # Keep the deterministic rule audit visible as an explicit degradation.
    update = {"quality_report": rule_report}
    if not rule_report["passed"]:
        update["retry_count"] = state.get("retry_count", 0) + 1
    return update


def _route_quality(state: PackageDesignState) -> str:
    if state["quality_report"].get("passed"):
        return "review"
    if state.get("retry_count", 0) < MAX_DESIGN_RETRIES:
        return "revise_nodes" if state.get("node_feedback") else "retry"
    # Preserve the differentiated Agent design after retries. The failed
    # quality report remains visible for teacher review; replacing the whole
    # package with one fixed rule template would erase lesson-specific work.
    return "review" if state.get("package") else "fallback"


def _rule_fallback(state: PackageDesignState) -> dict[str, Any]:
    package = design_agent._rule_fallback(state["lesson"])
    errors = list(state.get("errors", [])) + list(state.get("validation_errors", []))
    package["design"] = {
        "provider": "rule_fallback",
        "model": None,
        "fallback_reason": "; ".join(errors) or "quality review rejected generated design",
        "trace_id": state["trace_id"],
        "orchestration": "langgraph-stategraph",
    }
    return {
        "package": package,
        "provider": "rule_fallback",
        "model": None,
        "fallback_used": True,
        "validation_errors": [],
    }


def _teacher_review(state: PackageDesignState) -> dict[str, Any]:
    if not state.get("require_teacher_review"):
        return {"teacher_review": {"decision": "auto_approved"}}
    decision = interrupt({
        "type": "package_teacher_review",
        "trace_id": state["trace_id"],
        "package": state["package"],
        "quality_report": state["quality_report"],
        "allowed_decisions": ["approve", "edit", "reject"],
    })
    if not isinstance(decision, dict):
        decision = {"decision": str(decision)}
    update = {"teacher_review": decision}
    update["node_feedback"] = (
        decision.get("node_feedback")
        if isinstance(decision.get("node_feedback"), list)
        else []
    )
    if decision.get("decision") == "edit":
        update["retry_count"] = state.get("retry_count", 0) + 1
    return update


def _route_teacher_review(state: PackageDesignState) -> str:
    decision = str(state.get("teacher_review", {}).get("decision") or "reject")
    if decision == "approve" or decision == "auto_approved":
        return "finish"
    if decision == "edit" and state.get("retry_count", 0) < MAX_DESIGN_RETRIES:
        return "revise_nodes" if state.get("node_feedback") else "retry"
    return "fallback"


def _finish(state: PackageDesignState) -> dict[str, Any]:
    package = dict(state["package"])
    package["quality_report"] = state.get("quality_report", {})
    package["teacher_review"] = state.get("teacher_review", {})
    return {"package": package}


def _revise_nodes(state: PackageDesignState) -> dict[str, Any]:
    package = dict(state["package"])
    steps = [dict(step) for step in package.get("steps", [])]
    revisions = []
    errors = []
    for item in state.get("node_feedback", []):
        activity_id = str(item.get("activity_id") or "").strip()
        feedback = str(item.get("feedback") or "").strip()
        index = next(
            (i for i, step in enumerate(steps) if step.get("activity_id") == activity_id),
            None,
        )
        if index is None or not feedback:
            errors.append(f"invalid node feedback: {activity_id or 'missing activity_id'}")
            continue
        try:
            revised = revise_package_node(
                lesson=state["lesson"],
                node=steps[index],
                feedback=feedback,
                allow_activity_replacement=True,
            )
            steps[index] = revised["node"]
            revisions.append({
                "activity_id": activity_id,
                "feedback": feedback,
                "provider": revised["provider"],
            })
        except Exception as exc:
            errors.append(f"{activity_id}: {design_agent._short_error(exc)}")

    candidate = {
        "title": package.get("title"),
        "reasoning_summary": package.get("reasoning_summary"),
        "steps": steps,
    }
    try:
        validated = design_agent._validate_design(candidate, lesson=state["lesson"])
    except Exception as exc:
        return {
            "validation_errors": errors + [design_agent._short_error(exc)],
            "retry_count": state.get("retry_count", 0) + 1,
        }
    revised_by_id = {step["activity_id"]: step for step in steps}
    for step in validated["steps"]:
        source = revised_by_id.get(step["activity_id"], {})
        for key in ("description", "difficulty", "rhythmCardCount", "hintEnabled"):
            if key in source:
                step[key] = source[key]
    validated["design"] = dict(package.get("design", {}))
    validated["design"]["node_revisions"] = revisions
    return {
        "package": validated,
        "validation_errors": errors,
        "node_feedback": [],
    }


def _repair_feedback(state: PackageDesignState) -> str:
    parts = list(state.get("validation_errors", []))
    report = state.get("quality_report", {})
    parts.extend(
        str(item.get("message") or item)
        for item in report.get("issues", [])
        if item
    )
    feedback = state.get("teacher_review", {}).get("feedback")
    if feedback:
        parts.append(str(feedback))
    return "; ".join(parts)


def _quality_node_feedback(issues: list[Any]) -> list[dict[str, str]]:
    feedback = []
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        activity_id = str(issue.get("activity_id") or issue.get("step_id") or "").strip()
        message = str(issue.get("message") or issue.get("suggestion") or "").strip()
        if activity_id and message:
            feedback.append({"activity_id": activity_id, "feedback": message})
    return feedback


def _material_requirements(step: dict[str, Any]) -> list[str]:
    requirements = []
    for key in step.get("component_keys", []):
        if str(key).startswith("instrument"):
            requirements.append("instrument_configuration")
        elif str(key).startswith("game"):
            requirements.append("game_materials")
    return requirements or ["activity_materials"]


def _rule_quality_report(state: PackageDesignState) -> dict[str, Any]:
    steps = state["package"].get("steps", [])
    ids = [step.get("activity_id") for step in steps]
    checks = {
        "step_count": 3 <= len(steps) <= 7,
        "unique_activity_ids": len(ids) == len(set(ids)),
        "all_nodes_built": len(state.get("built_nodes", [])) == len(steps),
        "has_opening": bool(steps),
        "has_closure": bool(steps),
        "music_content_resolved": all(
            not step.get("music_content") or bool(step.get("resolved_music_content"))
            for step in steps
        ),
    }
    issues = [
        {"severity": "major", "message": name}
        for name, passed in checks.items() if not passed
    ]
    score = round(100 * sum(checks.values()) / len(checks))
    return {
        "passed": all(checks.values()),
        "score": score,
        "issues": issues,
        "checks": checks,
        "provider": "system",
    }


def _quality_messages(
    state: PackageDesignState, rule_report: dict[str, Any],
) -> list[dict[str, str]]:
    system = (
        "你是小学音乐课堂教学质量评估 Agent。只输出 JSON。"
        "检查活动是否覆盖教学目标、顺序是否连贯、难度是否适龄。"
        "逐项检查 activity_id、renderer、component_url 是否一一对应；"
        "不允许两个活动复用同一个 renderer 或同一个正式组件页面。"
        "检查相邻活动的学生操作、音乐材料和课堂任务是否实质重复。"
        "活动、游戏、虚拟乐器是同级节点。检查每个节点的 music_content 是否真正服务教学目标，"
        "拍号、速度和小节数是否适龄，并检查相邻节点是否只是重复同一音乐材料。"
        "如果模板选择没有问题，只是音乐内容不合理，必须建议只修改 music_content，不能替换模板。"
        "发现重复时，issues 必须指出具体 activity_id，passed 必须为 false。"
        "不得绕过代码校验；存在代码校验错误时 passed 必须为 false。"
    )
    user = json.dumps({
        "lesson": state["lesson"],
        "package": state["package"],
        "rule_report": rule_report,
        "output_schema": {
            "passed": True,
            "score": 0,
            "issues": [{
                "severity": "major",
                "activity_id": "必须填写发生问题的活动 ID",
                "message": "问题与具体修改建议",
            }],
        },
    }, ensure_ascii=False, separators=(",", ":"))
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def _compile_graph():
    builder = StateGraph(PackageDesignState)
    builder.add_node("design_agent", _design)
    builder.add_node("validate", _validate)
    builder.add_node("build_activity_materials", _build_activity_materials)
    builder.add_node("quality_agent", _quality_review)
    builder.add_node("rule_fallback", _rule_fallback)
    builder.add_node("teacher_review", _teacher_review)
    builder.add_node("revise_nodes", _revise_nodes)
    builder.add_node("finish", _finish)
    builder.add_edge(START, "design_agent")
    builder.add_edge("design_agent", "validate")
    builder.add_conditional_edges("validate", _route_validation, {
        "build": "build_activity_materials",
        "retry": "design_agent",
        "fallback": "rule_fallback",
    })
    builder.add_edge("build_activity_materials", "quality_agent")
    builder.add_conditional_edges("quality_agent", _route_quality, {
        "review": "teacher_review",
        "retry": "design_agent",
        "revise_nodes": "revise_nodes",
        "fallback": "rule_fallback",
    })
    builder.add_edge("rule_fallback", "build_activity_materials")
    builder.add_conditional_edges("teacher_review", _route_teacher_review, {
        "finish": "finish",
        "retry": "design_agent",
        "revise_nodes": "revise_nodes",
        "fallback": "rule_fallback",
    })
    builder.add_edge("revise_nodes", "build_activity_materials")
    builder.add_edge("finish", END)
    return builder.compile(checkpointer=InMemorySaver())


package_design_graph = _compile_graph()


def run_package_design(
    *,
    lesson: dict[str, Any],
    preferences: dict[str, Any],
    thread_id: str | None = None,
    require_teacher_review: bool = False,
    quality_review_mode: Literal["rules", "hybrid"] = "rules",
) -> dict[str, Any]:
    workflow_id = thread_id or str(uuid4())
    state: PackageDesignState = {
        "trace_id": str(uuid4()),
        "lesson": lesson,
        "preferences": preferences,
        "require_teacher_review": require_teacher_review,
        "quality_review_mode": quality_review_mode,
        "retry_count": 0,
        "errors": [],
        "fallback_used": False,
    }
    result = package_design_graph.invoke(
        state, {"configurable": {"thread_id": workflow_id}},
    )
    return _workflow_response(workflow_id, result)


def resume_package_design(
    *,
    thread_id: str,
    decision: str,
    feedback: str = "",
    node_feedback: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    result = package_design_graph.invoke(
        Command(resume={
            "decision": decision,
            "feedback": feedback,
            "node_feedback": node_feedback or [],
        }),
        {"configurable": {"thread_id": thread_id}},
    )
    return _workflow_response(thread_id, result)


def revise_package_node(
    *,
    lesson: dict[str, Any],
    node: dict[str, Any],
    feedback: str,
    allow_activity_replacement: bool = False,
) -> dict[str, Any]:
    messages = _node_revision_messages(
        lesson=lesson,
        node=node,
        feedback=feedback,
        allow_activity_replacement=allow_activity_replacement,
    )
    errors = []
    for config in (design_agent._ecnu_config(), design_agent._doubao_config()):
        if not config.get("enabled"):
            errors.append(f"{config['provider']}: not configured")
            continue
        try:
            payload = design_agent._call_model_messages(
                config, messages=messages, max_tokens=800,
            )
            revised = _validated_revised_node(
                original=node,
                payload=payload,
                allow_activity_replacement=allow_activity_replacement,
            )
            return {
                "node": revised,
                "provider": config["provider"],
                "model": config.get("model"),
                "fallback_reason": "; ".join(errors) or None,
            }
        except Exception as exc:
            errors.append(f"{config['provider']}: {design_agent._short_error(exc)}")
    raise RuntimeError("; ".join(errors) or "no revision model is available")


def _node_revision_messages(
    *,
    lesson: dict[str, Any],
    node: dict[str, Any],
    feedback: str,
    allow_activity_replacement: bool,
) -> list[dict[str, str]]:
    system = (
        "你是小学音乐课堂活动节点修订 Agent。只修改给定的一个节点并只输出 JSON。"
        "不得增加、删除或修改其他节点。activity_id 必须保持不变。"
        "输出可包含 title、description、difficulty、rhythmCardCount、hintEnabled、music_content。"
    )
    if allow_activity_replacement:
        system = (
            "你是小学音乐课堂活动节点修订 Agent。只替换或修改给定的一个问题节点并只输出 JSON。"
            "不得增加、删除或修改其他节点。可从 allowed_activities 选择新的 activity_id，"
            "用于修复重复组件或教学任务重复；不得创造新 ID。"
        )
    user = json.dumps({
        "lesson": lesson,
        "current_node": node,
        "teacher_feedback": feedback,
        "allowed_activities": (
            list(design_agent.ALLOWED_ACTIVITIES.values())
            if allow_activity_replacement else None
        ),
        "output_schema": {
            "activity_id": node.get("activity_id"),
            "title": "修改后的标题",
            "description": "修改后的活动说明",
            "difficulty": "easy|medium|hard",
            "rhythmCardCount": 4,
            "hintEnabled": True,
            "music_content": node.get("music_content", {}),
            "music_content_fields": [
                "meter_ids", "rhythm_pattern_ids", "pitch_set_ids",
                "melody_phrase_ids", "form_ids", "dynamic_ids", "timbre_ids",
            ],
        },
    }, ensure_ascii=False, separators=(",", ":"))
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def _validated_revised_node(
    *,
    original: dict[str, Any],
    payload: dict[str, Any],
    allow_activity_replacement: bool,
) -> dict[str, Any]:
    original_id = str(original.get("activity_id") or "")
    returned_id = str(payload.get("activity_id") or original_id)
    if returned_id != original_id and not allow_activity_replacement:
        raise ValueError("node revision cannot change activity_id")
    if returned_id not in design_agent.ALLOWED_ACTIVITIES:
        raise ValueError(f"node revision returned unknown activity_id: {returned_id}")
    revised = dict(original)
    for key in (
        "title", "description", "difficulty", "rhythmCardCount", "hintEnabled",
        "music_content",
    ):
        if key in payload:
            revised[key] = payload[key]
    revised["activity_id"] = returned_id
    if returned_id != original_id:
        revised["entity_id"] = returned_id
    entity_id = str(revised.get("entity_id") or returned_id)
    normalized, resolved = validate_and_resolve_music_content(
        entity_id=entity_id,
        raw=revised.get("music_content"),
    )
    revised["music_content"] = normalized
    revised["resolved_music_content"] = resolved
    return revised


def _workflow_response(thread_id: str, result: dict[str, Any]) -> dict[str, Any]:
    interruptions = result.get("__interrupt__", [])
    if interruptions:
        value = getattr(interruptions[0], "value", interruptions[0])
        return {"workflow_id": thread_id, "status": "awaiting_teacher_review", "review": value}
    return {
        "workflow_id": thread_id,
        "status": "completed",
        "package": result["package"],
    }
