from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from typing import Any

from app.services.auto_template_match_resolver import resolve_auto_template_match
from app.services.game_template_registry import build_game_instance, get_game_template
from app.services.llm_config import llm_env_missing_reason, llm_runtime_config
from app.services.music_game_library import build_music_game_blueprint, canonical_game_type


MAX_LESSON_PROMPT_CHARS = 7000
ALLOWED_GAME_TYPES = {
    "rhythm_race_game",
    "meter_orbit_game",
    "meter_gate_game",
    "dotted_rhythm_bounce",
    "syncopation_flag_game",
    "rest_light_game",
    "note_value_race",
    "pitch_path_game",
    "sol_mi_pitch_game",
    "interval_step_game",
    "melody_path_game",
    "phrase_pair_game",
    "timbre_detective_game",
    "timbre_match_game",
    "dynamic_contrast_game",
    "dynamic_slider_game",
    "expression_control_game",
    "tempo_dashboard_game",
    "pentatonic_grid_game",
    "mode_puzzle_game",
    "scene_expression_game",
    "singing_ladder_game",
    "creation_mission_game",
    "lesson_mission_game",
    "phrase_rebuild_singing",
}

META_RULE_MARKERS = ["是否服务于", "是否真正聚焦", "不是泛泛", "脱离教案", "质量门槛", "生成结果"]


LESSON_BRAIN_SYSTEM_PROMPT = """
你是中小学音乐课堂游戏设计大脑。你的任务不是写网页代码，而是阅读教案后输出稳定的教学设计决策。

你必须遵守：
1. 先理解整节课，不要把一个孤立知识点误当整课。
2. 先锁定教学重点可承载的模板游戏类型，再在该模板能力范围内制定游戏规则。
3. 如果教学重点与模板游戏冲突，以教学重点和模板能力为准，不能把节奏规则套到音高/旋律模板，或把音高规则套到节奏模板。
4. 只选择一个最适合游戏化的主环节。
5. 游戏必须是音乐游戏，学生操作必须回到可听、可唱、可拍、可辨或可创编的音乐行为。
6. 规则必须给学生使用，不能输出“是否服务于……”这类教师检查语。
7. 不要输出 HTML、CSS、JS、代码或技术路线。

只输出合法 JSON：
{
  "target_music_element": "具体音乐要素或音乐能力",
  "target_stage": "适合投放游戏的教学环节",
  "target_objective": "这个游戏要服务的课堂目标",
  "lesson_evidence": "来自教案的一句依据，尽量短",
  "selected_game_segment": {
    "stage_label": "环节名称",
    "task_summary": "环节任务",
    "gameable_point": "为什么能转成游戏，必须具体",
    "student_operation": "学生具体操作",
    "selection_reason": "为什么选这个环节"
  },
  "recommended_game": {
    "name": "游戏名称",
    "type": "从可用游戏机制中选择或给出 lesson_mission_game",
    "mechanic": "一句话描述玩法机制",
    "rules": ["学生可读的简短规则1", "学生可读的简短规则2"],
    "student_actions": ["学生动作1", "学生动作2", "学生动作3"],
    "win_condition": "通关条件"
  },
  "teacher_guidance": ["教师引导语1", "教师引导语2"],
  "assessment_closure": "游戏结束后如何回到课堂学习",
  "confidence": 0.0,
  "rationale": "简短说明为什么这样设计"
}
""".strip()


def lesson_brain_llm_status() -> dict[str, Any]:
    config = llm_runtime_config()
    return {
        "enabled": config["enabled"],
        "provider": config["provider"],
        "model": config["model"],
        "base_url": config["base_url"],
        "role": "lesson_design_brain_only",
    }


def enhance_lesson_analysis_with_llm(
    lesson_text: str,
    lesson_analysis: dict[str, Any],
    *,
    extra_need: str = "",
) -> dict[str, Any]:
    """Use an optional OpenAI-compatible LLM only to improve lesson design decisions.

    The returned analysis still flows through local playable_game, OpenCode, and QA layers.
    """
    status = lesson_brain_llm_status()
    enriched = _deepcopy(lesson_analysis)
    if not status["enabled"]:
        enriched["design_brain"] = {
            **status,
            "status": "skipped",
            "reason": llm_env_missing_reason(),
        }
        return enriched

    try:
        suggestion = _call_lesson_brain(lesson_text, lesson_analysis, extra_need=extra_need)
        enriched, applied = _apply_suggestion(enriched, suggestion)
        enriched["design_brain"] = {
            **status,
            "status": "applied",
            "confidence": suggestion.get("confidence", 0),
            "rationale": str(suggestion.get("rationale", ""))[:400],
            "applied_fields": applied,
        }
        return enriched
    except Exception as exc:
        enriched["design_brain"] = {
            **status,
            "status": "error",
            "error": str(exc)[:300],
        }
        return enriched


def _call_lesson_brain(lesson_text: str, lesson_analysis: dict[str, Any], *, extra_need: str) -> dict[str, Any]:
    config = llm_runtime_config()
    prompt = "\n".join(
        [
            "请根据本地规则初步分析和原始教案，优化“教案生成音乐游戏”的设计决策。",
            "",
            "本地初步分析 JSON：",
            json.dumps(_analysis_brief(lesson_analysis), ensure_ascii=False, separators=(",", ":")),
            "",
            "用户补充要求：",
            extra_need.strip() or "无",
            "",
            "原始教案：",
            _clip(lesson_text, MAX_LESSON_PROMPT_CHARS),
        ]
    )
    messages = [
        {"role": "system", "content": LESSON_BRAIN_SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]
    if config["provider"] == "chat_ecnu":
        return _call_chat_ecnu_lesson_brain(config, messages)
    return _call_openai_compatible_lesson_brain(config, messages)


def _call_openai_compatible_lesson_brain(config: dict[str, Any], messages: list[dict[str, str]]) -> dict[str, Any]:
    from openai import OpenAI

    client = OpenAI(api_key=config["api_key"], base_url=config["base_url"], timeout=20.0)
    response = client.chat.completions.create(
        model=config["model"],
        messages=messages,
        max_tokens=1800,
        temperature=0.2,
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content or "{}"
    return _json_from_text(content)


def _call_chat_ecnu_lesson_brain(config: dict[str, Any], messages: list[dict[str, str]]) -> dict[str, Any]:
    payload = {
        "messages": messages,
        "stream": False,
        "model": config["model"],
    }
    request = urllib.request.Request(
        config["chat_completions_url"],
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config['api_key']}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"ChatECNU 调用失败：HTTP {exc.code} {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"ChatECNU 连接失败：{exc.reason}") from exc
    payload = json.loads(raw)
    content = _chat_completion_content(payload)
    return _json_from_text(content)


def _chat_completion_content(payload: dict[str, Any]) -> str:
    choices = payload.get("choices")
    if isinstance(choices, list) and choices:
        first = choices[0]
        if isinstance(first, dict):
            message = first.get("message")
            if isinstance(message, dict) and message.get("content") is not None:
                return str(message.get("content") or "{}")
            if first.get("text") is not None:
                return str(first.get("text") or "{}")
    data = payload.get("data")
    if isinstance(data, dict):
        return _chat_completion_content(data)
    if payload.get("content") is not None:
        return str(payload.get("content") or "{}")
    raise ValueError("ChatECNU response does not contain assistant content")


def _apply_suggestion(analysis: dict[str, Any], suggestion: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    applied: list[str] = []
    lesson_context = analysis.setdefault("lesson_context", {})
    recommended = analysis.setdefault("recommended_game", {})
    focus = analysis.setdefault("specific_focus", {})
    selected = analysis.setdefault("selected_game_segment", {})
    context_segment = lesson_context.setdefault("selected_game_segment", selected)

    target_music_element = _clean_text(suggestion.get("target_music_element"))
    if _meaningful(target_music_element):
        focus["element"] = target_music_element
        recommended["music_element"] = target_music_element
        lesson_context["target_music_element"] = target_music_element
        selected["music_focus"] = target_music_element
        context_segment["music_focus"] = target_music_element
        applied.append("target_music_element")

    target_stage = _clean_text(suggestion.get("target_stage"))
    if _meaningful(target_stage):
        analysis["game_stage"] = target_stage
        lesson_context["target_stage"] = target_stage
        selected["stage_label"] = target_stage
        context_segment["stage_label"] = target_stage
        applied.append("target_stage")

    target_objective = _clean_text(suggestion.get("target_objective"))
    if _meaningful(target_objective):
        analysis["objective_summary"] = target_objective
        lesson_context["target_objective"] = target_objective
        applied.append("target_objective")

    evidence = _clean_text(suggestion.get("lesson_evidence"))
    if _meaningful(evidence):
        focus["evidence"] = evidence
        lesson_context["lesson_evidence"] = evidence
        applied.append("lesson_evidence")

    segment = suggestion.get("selected_game_segment") if isinstance(suggestion.get("selected_game_segment"), dict) else {}
    _merge_segment(selected, context_segment, lesson_context, segment, applied)

    game = suggestion.get("recommended_game") if isinstance(suggestion.get("recommended_game"), dict) else {}
    _merge_game(recommended, lesson_context, game, applied)
    _calibrate_recommended_game_to_template(analysis, recommended, lesson_context, applied)

    teacher_guidance = _clean_list(suggestion.get("teacher_guidance"), limit=4)
    if teacher_guidance:
        lesson_context["teacher_guidance"] = teacher_guidance
        applied.append("teacher_guidance")

    assessment_closure = _clean_text(suggestion.get("assessment_closure"))
    if _meaningful(assessment_closure):
        lesson_context["assessment_closure"] = assessment_closure
        applied.append("assessment_closure")

    rationale = _clean_text(suggestion.get("rationale"))
    if rationale:
        lesson_context["why_this_game_fits_this_lesson"] = rationale
        trace = list(lesson_context.get("decision_trace", []))
        trace.append(f"教案设计大脑：{rationale}")
        lesson_context["decision_trace"] = trace[-8:]
        applied.append("rationale")

    analysis["lesson_context"] = lesson_context
    return analysis, applied


def _merge_segment(selected: dict[str, Any], context_segment: dict[str, Any], lesson_context: dict[str, Any], segment: dict[str, Any], applied: list[str]) -> None:
    mapping = {
        "stage_label": "target_stage",
        "task_summary": "target_segment_task",
        "gameable_point": "target_segment_gameable_point",
        "student_operation": "student_task",
        "selection_reason": "stage_reason",
    }
    for field, context_key in mapping.items():
        value = _clean_text(segment.get(field))
        if not _meaningful(value):
            continue
        selected[field] = value
        context_segment[field] = value
        lesson_context[context_key] = value
        applied.append(field)


def _merge_game(recommended: dict[str, Any], lesson_context: dict[str, Any], game: dict[str, Any], applied: list[str]) -> None:
    name = _clean_text(game.get("name"))
    if _meaningful(name):
        recommended["name"] = name
        lesson_context["recommended_game_name"] = name
        applied.append("recommended_game.name")

    game_type = _clean_text(game.get("type"))
    if game_type in ALLOWED_GAME_TYPES:
        current_type = _clean_text(recommended.get("type") or lesson_context.get("recommended_game_type"))
        if not (game_type == "lesson_mission_game" and _is_specific_game_type(current_type)):
            recommended["type"] = game_type
            lesson_context["recommended_game_type"] = game_type
            applied.append("recommended_game.type")

    mechanic = _clean_text(game.get("mechanic"))
    if _meaningful(mechanic):
        recommended["mechanic"] = mechanic
        lesson_context["recommended_game_mechanic"] = mechanic
        applied.append("recommended_game.mechanic")

    rules = [rule for rule in _clean_list(game.get("rules"), limit=5) if not _is_meta_rule(rule)]
    if rules:
        recommended["rules"] = rules
        lesson_context["recommended_game_rules"] = rules
        applied.append("recommended_game.rules")

    actions = _clean_list(game.get("student_actions"), limit=6)
    if actions:
        recommended["student_actions"] = actions
        lesson_context["recommended_game_actions"] = actions
        lesson_context["student_task"] = "，".join(actions[:3]) + "。"
        applied.append("recommended_game.student_actions")

    win_condition = _clean_text(game.get("win_condition"))
    if _meaningful(win_condition):
        recommended["win_condition"] = win_condition
        applied.append("recommended_game.win_condition")

    _restore_specific_game_type_from_focus(recommended, lesson_context, applied)


def _is_specific_game_type(game_type: str) -> bool:
    return bool(game_type and game_type not in {"lesson_mission_game", "music_game", "mixed"})


def _restore_specific_game_type_from_focus(recommended: dict[str, Any], lesson_context: dict[str, Any], applied: list[str]) -> None:
    source = " ".join(
        [
            str(lesson_context.get("target_music_element", "")),
            str(recommended.get("music_element", "")),
            str(recommended.get("mechanic", "")),
            str(lesson_context.get("target_segment_gameable_point", "")),
        ]
    ).lower()
    current = _clean_text(recommended.get("type") or lesson_context.get("recommended_game_type"))
    if current and current != "lesson_mission_game":
        return
    if ("sol" in source and "mi" in source) or "音高" in source:
        recommended["type"] = "sol_mi_pitch_game" if "sol" in source and "mi" in source else "pitch_path_game"
        lesson_context["recommended_game_type"] = recommended["type"]
        applied.append("recommended_game.type.restore_specific")


TEMPLATE_DEFAULT_GAME_TYPES = {
    "beat_guardian_core": "rhythm_race_game",
    "pitch_ladder_core": "melody_path_game",
    "rhythm_echo_core": "rhythm_echo_chain",
    "solfege_target_core": "sol_mi_pitch_game",
    "timbre_detective_core": "timbre_detective_game",
    "form_treasure_core": "lesson_mission_game",
    "composition_puzzle_core": "constrained_composition_lab",
}


def _calibrate_recommended_game_to_template(
    analysis: dict[str, Any],
    recommended: dict[str, Any],
    lesson_context: dict[str, Any],
    applied: list[str],
) -> None:
    template_match = resolve_auto_template_match(
        lesson_analysis=analysis,
        lesson_fit={
            "lesson_evidence": {
                "music_element": lesson_context.get("target_music_element", ""),
                "target_objective": lesson_context.get("target_objective", ""),
                "target_stage": lesson_context.get("target_stage", ""),
                "segment_task": lesson_context.get("target_segment_task", ""),
                "gameable_point": lesson_context.get("target_segment_gameable_point", ""),
            },
            "template_hint": {},
        },
        lesson_context=lesson_context,
    )
    template_id = str(template_match.get("template_id") or "")
    target_type = TEMPLATE_DEFAULT_GAME_TYPES.get(template_id, "")
    if not target_type:
        return

    raw_type = str(recommended.get("type") or lesson_context.get("recommended_game_type") or "")
    current_type = canonical_game_type(raw_type)

    blueprint = build_music_game_blueprint(
        game_type=target_type,
        concept=str(lesson_context.get("target_music_element") or recommended.get("music_element") or ""),
        goal=str(lesson_context.get("target_objective") or ""),
        stage=str(lesson_context.get("target_stage") or ""),
        source_name="",
    )
    grounded_plan = _template_grounded_game_plan(
        template_id=template_id,
        blueprint=blueprint,
        lesson_context=lesson_context,
        template_match=template_match,
    )
    if grounded_plan:
        lesson_context["template_grounded_game_plan"] = grounded_plan
        analysis["template_grounded_game_plan"] = grounded_plan
        applied.append("template_grounded_game_plan")

    if current_type == target_type and raw_type == target_type:
        return

    recommended["type"] = target_type
    recommended["name"] = blueprint["game_name"]
    recommended["mechanic"] = blueprint["mechanic"]
    recommended["rules"] = _rules_from_blueprint(blueprint)
    recommended["student_actions"] = blueprint["student_actions"]
    recommended["win_condition"] = f"学生完成“{blueprint['music_concept']}”挑战，并能说出音乐判断依据。"
    lesson_context["recommended_game_type"] = target_type
    lesson_context["recommended_game_name"] = recommended["name"]
    lesson_context["recommended_game_mechanic"] = recommended["mechanic"]
    lesson_context["recommended_game_rules"] = recommended["rules"]
    lesson_context["recommended_game_actions"] = recommended["student_actions"]
    applied.append("template_first_calibration")


def _template_grounded_game_plan(
    *,
    template_id: str,
    blueprint: dict[str, Any],
    lesson_context: dict[str, Any],
    template_match: dict[str, Any],
) -> dict[str, Any]:
    template = get_game_template(template_id) or {}
    if not template:
        return {}
    try:
        instance = build_game_instance({"template_id": template_id, "difficulty": "L2"})
    except Exception:
        instance = {}
    student_task = instance.get("student_task") if isinstance(instance.get("student_task"), dict) else {}
    config = instance.get("config") if isinstance(instance.get("config"), dict) else {}
    feedback_rules = instance.get("feedback_rules") if isinstance(instance.get("feedback_rules"), dict) else {}
    reason_prompts = config.get("music_reason_prompts") if isinstance(config.get("music_reason_prompts"), dict) else {}

    listen = _clean_text(student_task.get("listen")) or _first_clean(blueprint.get("student_actions"))
    do = _clean_text(student_task.get("do")) or _first_clean((blueprint.get("student_actions") or [])[1:]) or _clean_text(blueprint.get("mechanic"))
    pass_rule = _clean_text(student_task.get("pass")) or _clean_text(blueprint.get("failure_state"))
    student_actions = [item for item in [listen, do, pass_rule] if item]
    music_reason = _clean_text(reason_prompts.get("success") or feedback_rules.get("success") or pass_rule)
    operation_summary = "，".join(student_actions[:3])
    concept = _clean_text(lesson_context.get("target_music_element") or blueprint.get("music_concept")) or "本课音乐要素"
    confidence = template_match.get("confidence")
    confidence_text = f"，置信度 {round(float(confidence) * 100)}%" if isinstance(confidence, (int, float)) else ""
    game_name = _clean_text(template.get("label")) or _clean_text(blueprint.get("game_name"))
    rule_checks = [
        f"操作规则：{do}" if do else "",
        f"通关标准：{pass_rule}" if pass_rule else "",
        f"判断依据：{music_reason}" if music_reason else "",
    ]
    reason_items = [
        f"匹配模板：{game_name}{confidence_text}",
        f"模板操作：{operation_summary}" if operation_summary else "",
        f"音乐依据：围绕“{concept}”完成操作并说出判断依据。",
    ]
    return {
        "version": "template_grounded_game_plan_v1",
        "template_id": template_id,
        "template_label": game_name,
        "game_name": game_name,
        "student_actions": student_actions,
        "rule_checks": [item for item in rule_checks if item],
        "win_condition": f"学生完成“{concept}”挑战，并能说出音乐判断依据。",
        "operation_summary": operation_summary,
        "reason_items": [item for item in reason_items if item],
    }


def _first_clean(values: Any) -> str:
    if not isinstance(values, list):
        return ""
    for value in values:
        text = _clean_text(value)
        if text:
            return text
    return ""


def _rules_from_blueprint(blueprint: dict[str, Any]) -> list[str]:
    actions = [str(action) for action in blueprint.get("student_actions", []) if str(action).strip()]
    rules = actions[:3]
    if blueprint.get("failure_state"):
        rules.append(str(blueprint["failure_state"]))
    return rules[:4]


def _analysis_brief(analysis: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "song_name",
        "grade_band",
        "lesson_type",
        "music_elements",
        "specific_focus",
        "key_objectives",
        "key_difficulties",
        "game_stage",
        "selected_game_segment",
        "recommended_game",
        "objective_summary",
    ]
    return {key: analysis.get(key) for key in keys}


def _clean_text(value: Any) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return text[:500]


def _clean_list(value: Any, *, limit: int) -> list[str]:
    if isinstance(value, list):
        raw = value
    else:
        raw = str(value or "").splitlines()
    result: list[str] = []
    for item in raw:
        text = _clean_text(item).strip("-•、. ")
        if text and not _is_meta_rule(text):
            result.append(text)
    return result[:limit]


def _meaningful(text: str) -> bool:
    return bool(text) and text not in {"无", "未提炼", "不确定", "音乐要素", "综合音乐感知"}


def _is_meta_rule(text: str) -> bool:
    return any(marker in text for marker in META_RULE_MARKERS)


def _json_from_text(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)\s*```", cleaned, re.DOTALL)
    if fenced:
        cleaned = fenced.group(1).strip()
    candidate = _extract_json_object_text(cleaned)
    payload = None
    for attempt in _json_parse_attempts(candidate):
        try:
            payload = json.loads(attempt)
            break
        except json.JSONDecodeError:
            continue
    if payload is None:
        payload = json.loads(candidate)
    if not isinstance(payload, dict):
        raise ValueError("lesson brain response is not an object")
    return payload


def _extract_json_object_text(text: str) -> str:
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        return text[start : end + 1].strip()
    return text.strip()


def _json_parse_attempts(text: str) -> list[str]:
    normalized = (
        text.strip()
        .replace("\ufeff", "")
        .replace("“", '"')
        .replace("”", '"')
        .replace("‘", "'")
        .replace("’", "'")
    )
    attempts = [normalized]
    repaired = _repair_json_like_text(normalized)
    if repaired != normalized:
        attempts.append(repaired)
    return attempts


def _repair_json_like_text(text: str) -> str:
    repaired = text
    repaired = re.sub(r"//.*?$", "", repaired, flags=re.MULTILINE)
    repaired = re.sub(r"/\*[\s\S]*?\*/", "", repaired)
    repaired = re.sub(r",(\s*[}\]])", r"\1", repaired)
    repaired = re.sub(r"([{\[,]\s*)([A-Za-z_][A-Za-z0-9_\-]*)(\s*:)", r'\1"\2"\3', repaired)
    repaired = re.sub(r":\s*'([^'\\]*(?:\\.[^'\\]*)*)'", lambda match: ': ' + json.dumps(match.group(1), ensure_ascii=False), repaired)
    repaired = re.sub(r"\[\s*'([^'\\]*(?:\\.[^'\\]*)*)'", lambda match: "[" + json.dumps(match.group(1), ensure_ascii=False), repaired)
    repaired = re.sub(r",\s*'([^'\\]*(?:\\.[^'\\]*)*)'", lambda match: ", " + json.dumps(match.group(1), ensure_ascii=False), repaired)
    return repaired.strip()


def _clip(text: str, limit: int) -> str:
    text = str(text or "")
    return text if len(text) <= limit else text[:limit] + "\n……"


def _deepcopy(payload: dict[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(payload, ensure_ascii=False))
