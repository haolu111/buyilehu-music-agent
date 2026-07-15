from __future__ import annotations

from typing import Any, Literal, TypedDict
from uuid import uuid4

from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph


class PackageDesignState(TypedDict, total=False):
    lesson: dict[str, Any]
    preferences: dict[str, Any]
    trace_id: str
    providers: list[dict[str, Any]]
    provider_index: int
    candidate: dict[str, Any] | None
    design: dict[str, Any]
    selected_provider: dict[str, Any]
    errors: list[str]
    workflow_steps: list[str]
    tool_calls: list[str]
    result: dict[str, Any]


@tool("package_design_model", description="Generate a classroom package design with one configured model provider.")
def package_design_model_tool(
    provider_config: dict[str, Any],
    lesson: dict[str, Any],
    preferences: dict[str, Any],
) -> dict[str, Any]:
    from app.services.orchestration import package_design_agent

    return package_design_agent._call_model(
        provider_config,
        lesson=lesson,
        preferences=preferences,
    )


@tool("validate_package_design", description="Validate and normalize a generated classroom package design.")
def validate_package_design_tool(
    candidate: dict[str, Any],
    lesson: dict[str, Any],
) -> dict[str, Any]:
    from app.services.orchestration import package_design_agent

    return package_design_agent._validate_design(candidate, lesson=lesson)


@tool("rule_package_design", description="Build a deterministic package design when model tools are unavailable.")
def rule_package_design_tool(lesson: dict[str, Any]) -> dict[str, Any]:
    from app.services.orchestration import package_design_agent

    return package_design_agent._rule_fallback(lesson)


def run_package_design_workflow(
    *, lesson: dict[str, Any], preferences: dict[str, Any]
) -> dict[str, Any]:
    final_state = PACKAGE_DESIGN_GRAPH.invoke(
        {
            "lesson": lesson,
            "preferences": preferences,
            "trace_id": str(uuid4()),
            "errors": [],
            "workflow_steps": [],
            "tool_calls": [],
        }
    )
    return final_state["result"]


def _prepare(state: PackageDesignState) -> dict[str, Any]:
    from app.services.orchestration import package_design_agent

    return {
        "providers": [
            package_design_agent._ecnu_config(),
            package_design_agent._doubao_config(),
        ],
        "provider_index": 0,
        "candidate": None,
        "workflow_steps": [*state.get("workflow_steps", []), "prepare"],
    }


def _call_model(state: PackageDesignState) -> dict[str, Any]:
    provider_index = state["provider_index"]
    config = state["providers"][provider_index]
    provider = str(config["provider"])
    next_index = provider_index + 1
    steps = list(state.get("workflow_steps", []))
    errors = list(state.get("errors", []))

    if not config.get("enabled"):
        errors.append(f"{provider}: not configured")
        steps.append(f"provider:{provider}:skipped")
        return {
            "provider_index": next_index,
            "candidate": None,
            "errors": errors,
            "workflow_steps": steps,
        }

    tool_calls = [*state.get("tool_calls", []), package_design_model_tool.name]
    steps.append(f"provider:{provider}:model")
    try:
        candidate = package_design_model_tool.invoke(
            {
                "provider_config": config,
                "lesson": state["lesson"],
                "preferences": state["preferences"],
            }
        )
    except Exception as exc:
        from app.services.orchestration import package_design_agent

        errors.append(f"{provider}: {package_design_agent._short_error(exc)}")
        steps.append(f"provider:{provider}:failed")
        candidate = None

    return {
        "provider_index": next_index,
        "candidate": candidate,
        "selected_provider": {
            "provider": provider,
            "model": config.get("model"),
        },
        "errors": errors,
        "workflow_steps": steps,
        "tool_calls": tool_calls,
    }


def _validate(state: PackageDesignState) -> dict[str, Any]:
    provider = state["selected_provider"]["provider"]
    steps = list(state.get("workflow_steps", []))
    errors = list(state.get("errors", []))
    tool_calls = [*state.get("tool_calls", []), validate_package_design_tool.name]
    try:
        design = validate_package_design_tool.invoke(
            {"candidate": state["candidate"], "lesson": state["lesson"]}
        )
        steps.append(f"provider:{provider}:validated")
        return {
            "design": design,
            "workflow_steps": steps,
            "tool_calls": tool_calls,
        }
    except Exception as exc:
        from app.services.orchestration import package_design_agent

        errors.append(f"{provider}: {package_design_agent._short_error(exc)}")
        steps.append(f"provider:{provider}:invalid")
        return {
            "candidate": None,
            "errors": errors,
            "workflow_steps": steps,
            "tool_calls": tool_calls,
        }


def _fallback(state: PackageDesignState) -> dict[str, Any]:
    design = rule_package_design_tool.invoke({"lesson": state["lesson"]})
    return {
        "design": design,
        "selected_provider": {"provider": "rule_fallback", "model": None},
        "workflow_steps": [*state.get("workflow_steps", []), "fallback:rule"],
        "tool_calls": [*state.get("tool_calls", []), rule_package_design_tool.name],
    }


def _finalize(state: PackageDesignState) -> dict[str, Any]:
    result = dict(state["design"])
    selected_provider = state["selected_provider"]
    errors = state.get("errors", [])
    result["design"] = {
        "provider": selected_provider["provider"],
        "model": selected_provider.get("model"),
        "fallback_reason": "; ".join(errors) or None,
        "trace_id": state["trace_id"],
        "workflow_engine": "langgraph",
        "workflow_steps": [*state.get("workflow_steps", []), "finalize"],
        "tool_calls": list(state.get("tool_calls", [])),
    }
    return {"result": result}


def _route_after_model(state: PackageDesignState) -> Literal["validate", "retry", "fallback"]:
    if state.get("candidate") is not None:
        return "validate"
    if state["provider_index"] < len(state["providers"]):
        return "retry"
    return "fallback"


def _route_after_validation(state: PackageDesignState) -> Literal["finalize", "retry", "fallback"]:
    if state.get("design") is not None:
        return "finalize"
    if state["provider_index"] < len(state["providers"]):
        return "retry"
    return "fallback"


def _build_graph():
    graph = StateGraph(PackageDesignState)
    graph.add_node("prepare", _prepare)
    graph.add_node("call_model", _call_model)
    graph.add_node("validate", _validate)
    graph.add_node("fallback", _fallback)
    graph.add_node("finalize", _finalize)
    graph.add_edge(START, "prepare")
    graph.add_edge("prepare", "call_model")
    graph.add_conditional_edges(
        "call_model",
        _route_after_model,
        {"validate": "validate", "retry": "call_model", "fallback": "fallback"},
    )
    graph.add_conditional_edges(
        "validate",
        _route_after_validation,
        {"finalize": "finalize", "retry": "call_model", "fallback": "fallback"},
    )
    graph.add_edge("fallback", "finalize")
    graph.add_edge("finalize", END)
    return graph.compile()


PACKAGE_DESIGN_GRAPH = _build_graph()
