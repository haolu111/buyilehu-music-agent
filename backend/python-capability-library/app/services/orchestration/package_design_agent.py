from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any
from uuid import uuid4

from app.services.core.env_bootstrap import ensure_env_loaded
from app.services.activities.activity_interaction_registry import (
    get_activity_interaction,
    list_agent_activity_specs,
)
from app.services.music_content.music_content_registry import (
    capability_for,
    music_content_catalog,
    validate_and_resolve_music_content,
)


ALLOWED_ACTIVITIES: dict[str, dict[str, Any]] = {
    spec["activity_id"]: spec for spec in list_agent_activity_specs()
}
ALLOWED_GAMES = {
    "rhythm_echo_core": "节奏回声",
    "beat_guardian_core": "节拍守卫",
    "pitch_ladder_core": "音高阶梯",
    "solfege_target_core": "唱名目标",
    "timbre_detective_core": "音色侦探",
    "form_treasure_core": "曲式寻宝",
    "composition_puzzle_core": "创编拼图",
}
GAME_TEMPLATE_ALIASES = {
    "rhythm_question_answer": "rhythm_echo_core",
    "rhythm_warmup": "rhythm_echo_core",
    "strong_weak_beat_circle": "beat_guardian_core",
    "steady_beat_walk": "beat_guardian_core",
    "solfege_sorting": "solfege_target_core",
    "solfege_echo_singing": "solfege_target_core",
    "melody_contour_trace": "pitch_ladder_core",
    "instrument_timbre_match": "timbre_detective_core",
    "instrument_family_sorting": "timbre_detective_core",
    "form_ordering": "form_treasure_core",
    "theme_return_action": "form_treasure_core",
    "graphic_score_create": "composition_puzzle_core",
    "xylophone_creation": "composition_puzzle_core",
}
ALLOWED_INSTRUMENT_TASKS = {
    "free_play", "steady_beat", "rhythm_echo", "melody_sequence",
    "ensemble_cue", "constrained_composition",
}
ALLOWED_INSTRUMENTS = {
    "virtual_piano", "virtual_xylophone", "virtual_frame_drum",
}
INSTRUMENT_ALIASES = {
    "piano": "virtual_piano",
    "xylophone": "virtual_xylophone",
    "drum": "virtual_frame_drum",
    "frame_drum": "virtual_frame_drum",
    "virtual_hand_drum": "virtual_frame_drum",
}


def design_interactive_package(*, lesson: dict[str, Any], preferences: dict[str, Any]) -> dict[str, Any]:
    ensure_env_loaded()
    # Local import avoids a module cycle: graph nodes reuse the provider,
    # prompt and validation helpers defined in this module.
    from app.services.orchestration.package_design_graph import run_package_design

    result = run_package_design(
        lesson=lesson,
        preferences=preferences,
        require_teacher_review=False,
        quality_review_mode="hybrid",
    )
    return result["package"]


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
    timeout_seconds = max(5.0, float(os.getenv("PACKAGE_AGENT_MODEL_TIMEOUT_SECONDS") or "120"))
    if config["provider"] == "chat_ecnu":
        request = urllib.request.Request(
            config["url"],
            data=json.dumps({
                "model": config["model"],
                "messages": messages,
                "stream": False,
                "temperature": 0.2,
                "max_tokens": max_tokens,
                "response_format": {"type": "json_object"},
            }, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {config['api_key']}"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
                result = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:300]
            raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc
        return _json_from_text(_completion_content(result))

    from openai import OpenAI

    client = OpenAI(api_key=config["api_key"], base_url=config["base_url"], timeout=timeout_seconds)
    response = client.chat.completions.create(
        model=config["model"], messages=messages, temperature=0.2, max_tokens=max_tokens,
        response_format={"type": "json_object"},
    )
    return _json_from_text(response.choices[0].message.content or "{}")


def _messages(*, lesson: dict[str, Any], preferences: dict[str, Any]) -> list[dict[str, str]]:
    catalog = list(ALLOWED_ACTIVITIES.values())
    instrument_task_capabilities = {
        task_kind: capability_for(f"instrument_task:{task_kind}")
        for task_kind in sorted(ALLOWED_INSTRUMENT_TASKS)
    }
    system = (
        "你是不亦乐乎小学音乐课堂的互动包设计 Agent。只输出 JSON。"
        "根据教案目标、音乐要素、教学过程和时长选择 3 到 7 个活动。"
        "steps 数组绝对不能超过 7 项；目标较多时应合并相近任务，而不是继续增加节点。"
        "必须从 allowed_activities 选择 activity_id，不得创造新 ID。"
        "活动顺序要形成体验、表现、理解、迁移或创编的课堂闭环。"
    )
    user = json.dumps({
        "lesson": lesson,
        "preferences": preferences,
        "allowed_activities": catalog,
        "allowed_games": ALLOWED_GAMES,
        "allowed_instrument_tasks": sorted(ALLOWED_INSTRUMENT_TASKS),
        "instrument_task_music_content_capabilities": instrument_task_capabilities,
        "allowed_instruments": sorted(ALLOWED_INSTRUMENTS),
        "music_content_catalog": music_content_catalog(),
        "music_content_rule": (
            "Only configure music_content for a node with music_content_capability. "
            "For instrument_task nodes, obey instrument_task_music_content_capabilities "
            "for the selected task_kind; do not infer capability from instrument_id. "
            "meter_ids, rhythm_pattern_ids, pitch_set_ids, melody_phrase_ids, "
            "form_ids, dynamic_ids and timbre_ids must come from the catalog. "
            "Only change musical content when the activity template remains suitable. "
            "Activities, games and virtual "
            "instruments are peer package nodes."
        ),
        "step_requirement": "每个步骤必须提供 recommendation_reason，用自然中文结合教案目标说明推荐目的，不能罗列标签。",
        "output_schema": {
            "title": "互动包标题",
            "reasoning_summary": "两三句话说明活动设计依据",
            "steps": [{
                "node_type": "activity|game|instrument_task",
                "activity_id": "活动节点填写",
                "template_id": "游戏节点填写",
                "task_kind": "虚拟乐器节点填写",
                "instrument_id": "虚拟乐器节点填写",
                "title": "学生看到的节点标题",
                "music_content": {
                    "meter_ids": ["meter_2_4"], "bpm": 84, "bars": 4,
                    "rhythm_pattern_ids": ["rhythm_titi_ta"],
                    "pitch_set_ids": ["pitch_do_re_mi_sol_la"],
                    "melody_phrase_ids": ["melody_arch"],
                    "form_ids": ["form_aba"],
                    "dynamic_ids": ["dynamic_p", "dynamic_f"],
                    "timbre_ids": ["timbre_piano"],
                },
            }],
        },
    }, ensure_ascii=False, separators=(",", ":"))
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def _validate_design(payload: dict[str, Any], *, lesson: dict[str, Any]) -> dict[str, Any]:
    raw_steps = payload.get("steps")
    if not isinstance(raw_steps, list) or len(raw_steps) < 3:
        raise ValueError("model must return 3 to 7 steps")
    package_corrections: list[dict[str, Any]] = []
    if len(raw_steps) > 7:
        original_count = len(raw_steps)
        # Preserve the opening and closing tasks, then keep the earliest five
        # teaching tasks. A model exceeding the package-size constraint should
        # not cause its otherwise lesson-specific design to be discarded.
        raw_steps = [raw_steps[0], *raw_steps[1:-1][:5], raw_steps[-1]]
        package_corrections.append({
            "field": "steps",
            "action": "trimmed",
            "from": original_count,
            "to": 7,
            "reason": "interactive package supports at most 7 nodes",
        })
    steps = []
    for index, raw in enumerate(raw_steps):
        if not isinstance(raw, dict):
            raise ValueError("each step must be an object")
        interactive_node_type = str(raw.get("node_type") or "activity").strip()
        activity_id = str(raw.get("activity_id") or "").strip()
        component_keys: list[str] = []
        default_title = ""
        content_entity_id = activity_id
        validation_entity_id = activity_id
        if interactive_node_type == "game":
            template_id = str(raw.get("template_id") or "").strip()
            if not template_id and activity_id in ALLOWED_GAMES:
                template_id = activity_id
            template_id = GAME_TEMPLATE_ALIASES.get(template_id, template_id)
            template_id = GAME_TEMPLATE_ALIASES.get(activity_id, template_id)
            if template_id not in ALLOWED_GAMES:
                # Keep a valid activity selected by the model when it merely
                # mislabeled the node as a game. This repairs only the problem
                # node and avoids replacing the entire lesson-specific package.
                if activity_id in ALLOWED_ACTIVITIES:
                    interactive_node_type = "activity"
                else:
                    raise ValueError(f"game is not allowed: {template_id}")
            else:
                activity_id = (
                    activity_id
                    if activity_id in ALLOWED_ACTIVITIES
                    else "rhythm_question_answer"
                )
                component_keys = [f"game:{template_id}"]
                default_title = ALLOWED_GAMES[template_id]
                content_entity_id = template_id
                validation_entity_id = activity_id
        elif interactive_node_type == "instrument_task":
            task_kind = str(raw.get("task_kind") or "").strip()
            if task_kind not in ALLOWED_INSTRUMENT_TASKS:
                raise ValueError(f"instrument task is not allowed: {task_kind}")
            instrument_id = str(raw.get("instrument_id") or (
                "virtual_piano" if task_kind == "melody_sequence" else "virtual_frame_drum"
            )).strip()
            instrument_id = INSTRUMENT_ALIASES.get(instrument_id, instrument_id)
            if instrument_id not in ALLOWED_INSTRUMENTS:
                raise ValueError(f"instrument is not allowed: {instrument_id}")
            activity_id = activity_id or (
                "xylophone_creation" if task_kind == "melody_sequence" else "rhythm_warmup"
            )
            component_keys = [f"instrument_task:{task_kind}", f"instrument:{instrument_id}"]
            default_title = "虚拟乐器任务"
            content_entity_id = instrument_id
            # Musical content constrains the teaching task, not the skin.
            # A piano can perform rhythm, dynamics and form; validating these
            # fields against the instrument asset caused valid Agent designs
            # to be discarded and replaced by the fixed fallback package.
            validation_entity_id = f"instrument_task:{task_kind}"
        else:
            interactive_node_type = "activity"
        try:
            spec = get_activity_interaction(activity_id)
        except ValueError:
            raise ValueError(f"activity is not allowed: {activity_id}")
        title = str(raw.get("title") or default_title or spec["name"]).strip()[:60] or spec["name"]
        recommendation_reason = str(raw.get("recommendation_reason") or "").strip()
        if not recommendation_reason:
            recommendation_reason = _fallback_recommendation_reason(
                lesson=lesson,
                title=title,
                node_type=interactive_node_type,
                family=str(spec.get("family") or ""),
            )
        if not component_keys:
            component_keys = list(spec["component_keys"])
        raw_music_content, removed_fields = _remove_unsupported_music_content(
            entity_id=validation_entity_id,
            raw=raw.get("music_content"),
        )
        normalized_content, resolved_content = validate_and_resolve_music_content(
            entity_id=validation_entity_id,
            raw=raw_music_content,
            grade_band=str(lesson.get("grade_band") or "middle_primary"),
        )
        steps.append({
            "node_id": str(raw.get("node_id") or f"node-{index + 1}"),
            "entity_id": content_entity_id,
            "activity_id": activity_id,
            "title": title,
            "node_type": interactive_node_type if interactive_node_type != "activity" else spec["node_type"],
            "sort_order": index + 1,
            "component_keys": component_keys,
            "family": spec["family"],
            "variant": spec["variant"],
            "renderer": spec["renderer"],
            "component_url": spec.get("component_url"),
            "music_content": normalized_content,
            "resolved_music_content": resolved_content,
            "music_content_capability": capability_for(content_entity_id),
            "music_content_corrections": [
                {
                    "field": field,
                    "action": "removed",
                    "reason": f"{validation_entity_id} does not support {field}",
                }
                for field in removed_fields
            ],
            "recommendation_reason": recommendation_reason[:240],
        })
    course_name = str(lesson.get("course_name") or "音乐课")
    return {
        "schema_version": "package-design.v1",
        "design_version": "interactive-package-design.v2",
        "title": str(payload.get("title") or f"{course_name}互动课堂").strip()[:100],
        "reasoning_summary": str(payload.get("reasoning_summary") or "根据教案目标组织课堂活动。")[:500],
        "steps": steps,
        "design_corrections": package_corrections,
    }


def _remove_unsupported_music_content(
    *, entity_id: str, raw: Any,
) -> tuple[dict[str, Any], list[str]]:
    """Repair only unsupported music fields instead of rejecting the whole package.

    Unknown catalog IDs and invalid ranges remain hard validation errors. This
    narrowly handles a model attaching a valid musical element to the wrong
    node type, such as pitch_set_ids on an ensemble-cue task.
    """
    content = dict(raw) if isinstance(raw, dict) else {}
    capability = capability_for(entity_id)
    # Empty arrays from structured model output mean "no selection". Retain
    # strict validation for non-empty unknown IDs, but do not discard a whole
    # package because an optional list was emitted as [].
    for field in (
        "meter_ids", "rhythm_pattern_ids", "pitch_set_ids",
        "melody_phrase_ids", "form_ids", "dynamic_ids", "timbre_ids",
    ):
        if content.get(field) == []:
            content.pop(field, None)
    removed = [
        field for field in (
            "meter_ids", "bpm", "bars", "rhythm_pattern_ids",
            "pitch_set_ids", "melody_phrase_ids", "form_ids",
            "dynamic_ids", "timbre_ids",
        )
        if field in content and field not in capability
    ]
    for field in removed:
        content.pop(field, None)
    return content, removed


def _fallback_recommendation_reason(
    *, lesson: dict[str, Any], title: str, node_type: str, family: str,
) -> str:
    objectives = [
        str(item).strip() for item in lesson.get("objectives", [])
        if str(item).strip()
    ]
    focus = objectives[0] if objectives else ""
    if node_type == "game":
        purpose = "用即时挑战和反馈检验学生是否真正掌握，并保持课堂参与度。"
    elif node_type == "instrument_task":
        purpose = "让学生通过可听、可操作的乐器体验，把抽象的音乐概念转化为演奏实践。"
    else:
        purposes = {
            "lyrics_rhythm": "帮助学生把歌词重音、节拍和朗读动作建立联系，为后续演唱做好节奏准备。",
            "singing_phrase": "通过分句模仿和反复练习，降低完整演唱的难度并巩固旋律记忆。",
            "ensemble": "让学生在分工合作中关注声部配合、稳定节拍和整体音响效果。",
            "performance_reflection": "通过展示、观察和反馈，让学生把表演体验转化为可表达、可改进的学习成果。",
        }
        purpose = purposes.get(
            family,
            "通过明确的互动任务帮助学生理解、练习并检验本课的核心音乐能力。",
        )
    if focus:
        return f"推荐“{title}”，用于承接“{focus}”这一教学目标。{purpose}"
    return f"推荐“{title}”。{purpose}"


def _rule_fallback(lesson: dict[str, Any]) -> dict[str, Any]:
    elements = {str(item) for item in lesson.get("music_elements", [])}
    activity_ids = ["lesson_opening_hook"]
    if "节拍" in elements:
        activity_ids.append("strong_weak_beat_circle")
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
