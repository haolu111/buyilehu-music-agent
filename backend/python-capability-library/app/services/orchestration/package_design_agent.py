from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

from app.services.core.env_bootstrap import ensure_env_loaded
from app.services.activities.activity_interaction_registry import (
    get_activity_interaction,
    list_agent_activity_specs,
)


ALLOWED_ACTIVITIES: dict[str, dict[str, Any]] = {
    spec["activity_id"]: spec for spec in list_agent_activity_specs()
}


def design_interactive_package(*, lesson: dict[str, Any], preferences: dict[str, Any]) -> dict[str, Any]:
    ensure_env_loaded()
    from app.services.orchestration.package_design_workflow import run_package_design_workflow

    return run_package_design_workflow(lesson=lesson, preferences=preferences)


def _ecnu_config() -> dict[str, Any]:
    key = os.getenv("CHAT_ECNU_API_KEY") or ""
    model = os.getenv("CHAT_ECNU_MODEL") or "ecnu-max"
    return {
        "provider": "chat_ecnu",
        "enabled": bool(key and model),
        "api_key": key,
        "model": model,
        "url": os.getenv("CHAT_ECNU_CHAT_COMPLETIONS_URL") or "https://chat.ecnu.edu.cn/open/api/v1/chat/completions",
    }


def _doubao_config() -> dict[str, Any]:
    key = os.getenv("DOUBAO_API_KEY") or os.getenv("ARK_API_KEY") or ""
    model = os.getenv("DOUBAO_MODEL") or os.getenv("ARK_MODEL") or ""
    return {
        "provider": "doubao",
        "enabled": bool(key and model),
        "api_key": key,
        "model": model,
        "base_url": os.getenv("DOUBAO_BASE_URL") or os.getenv("ARK_BASE_URL") or "https://ark.cn-beijing.volces.com/api/v3",
    }


def _call_model(config: dict[str, Any], *, lesson: dict[str, Any], preferences: dict[str, Any]) -> dict[str, Any]:
    messages = _messages(lesson=lesson, preferences=preferences)
    return _call_model_messages(config, messages=messages, max_tokens=1800)


def _call_model_messages(
    config: dict[str, Any], *, messages: list[dict[str, str]], max_tokens: int,
) -> dict[str, Any]:
    if config["provider"] == "chat_ecnu":
        request = urllib.request.Request(
            config["url"],
            data=json.dumps({"model": config["model"], "messages": messages, "stream": False}, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {config['api_key']}"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                result = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:300]
            raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc
        return _json_from_text(_completion_content(result))

    from openai import OpenAI

    client = OpenAI(api_key=config["api_key"], base_url=config["base_url"], timeout=45.0)
    response = client.chat.completions.create(
        model=config["model"], messages=messages, temperature=0.2, max_tokens=max_tokens,
        response_format={"type": "json_object"},
    )
    return _json_from_text(response.choices[0].message.content or "{}")


def _messages(*, lesson: dict[str, Any], preferences: dict[str, Any]) -> list[dict[str, str]]:
    catalog = list(ALLOWED_ACTIVITIES.values())
    system = (
        "你是不亦乐乎小学音乐课堂的互动包设计 Agent。只输出 JSON。"
        "根据教案目标、音乐要素、教学过程和时长选择 3 到 7 个活动。"
        "必须从 allowed_activities 选择 activity_id，不得创造新 ID。"
        "活动顺序要形成体验、表现、理解、迁移或创编的课堂闭环。"
    )
    user = json.dumps({
        "lesson": lesson,
        "preferences": preferences,
        "allowed_activities": catalog,
        "output_schema": {
            "title": "互动包标题",
            "reasoning_summary": "两三句话说明活动设计依据",
            "steps": [{"activity_id": "白名单 ID", "title": "学生看到的活动标题"}],
        },
    }, ensure_ascii=False, separators=(",", ":"))
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def _validate_design(payload: dict[str, Any], *, lesson: dict[str, Any]) -> dict[str, Any]:
    raw_steps = payload.get("steps")
    if not isinstance(raw_steps, list) or not 3 <= len(raw_steps) <= 7:
        raise ValueError("model must return 3 to 7 steps")
    steps = []
    for index, raw in enumerate(raw_steps):
        if not isinstance(raw, dict):
            raise ValueError("each step must be an object")
        activity_id = str(raw.get("activity_id") or "").strip()
        try:
            spec = get_activity_interaction(activity_id)
        except ValueError:
            raise ValueError(f"activity is not allowed: {activity_id}")
        title = str(raw.get("title") or spec["name"]).strip()[:60] or spec["name"]
        steps.append({
            "activity_id": activity_id,
            "title": title,
            "node_type": spec["node_type"],
            "sort_order": index + 1,
            "component_keys": list(spec["component_keys"]),
        })
    course_name = str(lesson.get("course_name") or "音乐课")
    return {
        "schema_version": "package-design.v1",
        "title": str(payload.get("title") or f"{course_name}互动课堂").strip()[:100],
        "reasoning_summary": str(payload.get("reasoning_summary") or "根据教案目标组织课堂活动。")[:500],
        "steps": steps,
    }


def _rule_fallback(lesson: dict[str, Any]) -> dict[str, Any]:
    elements = {str(item) for item in lesson.get("music_elements", [])}
    activity_ids = ["lesson_opening_hook"]
    if "节拍" in elements:
        activity_ids.append("meter_body_movement")
    activity_ids.append("rhythm_question_answer")
    if "旋律" in elements or "节奏" in elements:
        activity_ids.append("xylophone_creation")
    activity_ids.append("exit_ticket_review")
    payload = {"steps": [{"activity_id": item} for item in activity_ids]}
    return _validate_design(payload, lesson=lesson)


def _completion_content(payload: dict[str, Any]) -> str:
    choices = payload.get("choices")
    if isinstance(choices, list) and choices and isinstance(choices[0], dict):
        message = choices[0].get("message")
        if isinstance(message, dict):
            return str(message.get("content") or "{}")
    data = payload.get("data")
    return _completion_content(data) if isinstance(data, dict) else "{}"


def _json_from_text(text: str) -> dict[str, Any]:
    raw = str(text or "").strip()
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        start, end = raw.find("{"), raw.rfind("}")
        value = json.loads(raw[start : end + 1]) if start >= 0 and end > start else {}
    if not isinstance(value, dict):
        raise ValueError("model response is not a JSON object")
    return value


def _short_error(exc: Exception) -> str:
    message = str(exc).replace("\n", " ").strip()
    return message[:180] or exc.__class__.__name__
