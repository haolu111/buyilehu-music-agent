from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.services.activities.activity_interaction_registry import get_activity_interaction
from app.services.activities.activity_family_registry import get_activity_family
from app.services.activities.activity_registry import get_activity_template, list_activity_templates
from app.services.orchestration.toolkit_registry import build_toolkit_spec
from app.services.runtime.music_classroom_suite import build_default_music_media_session
from app.services.runtime.primary_music_game_runtime_builder import build_primary_music_game_runtime
from app.services.games.interactive_game_service import build_game_node
from app.services.instruments.instrument_task_service import build_instrument_task


_MEDIA_SESSION_ACTIVITY_IDS = {
    "song_audio_workbench_activity",
    "score_audio_sync_practice",
    "ear_training_practice",
    "vocal_choir_training_activity",
    "ensemble_conductor_rehearsal",
}


def list_available_toolkits() -> list[dict[str, Any]]:
    activity_ids = [str(activity["activity_id"]) for activity in list_activity_templates()]
    return [build_toolkit_spec(activity_id) for activity_id in activity_ids]


def build_runtime_bundle(
    *,
    activity_id: str | None,
    composition: dict[str, Any] | None,
    request: dict[str, Any] | None,
) -> dict[str, Any]:
    resolved_activity_id = _resolve_activity_id(activity_id=activity_id, composition=composition)
    activity = get_activity_template(resolved_activity_id)
    toolkit = build_toolkit_spec(resolved_activity_id)
    resolved_composition = _resolve_composition(activity=activity, toolkit=toolkit, composition=composition)
    resolved_request = deepcopy(request) if isinstance(request, dict) else {}
    media_session_preview = _maybe_build_media_session_preview(
        activity_id=resolved_activity_id,
        composition=resolved_composition,
        request=resolved_request,
    )
    runtime = build_primary_music_game_runtime(composition=resolved_composition, request=resolved_request)
    activity_runtime = _build_activity_runtime(
        activity_id=resolved_activity_id,
        activity=activity,
        composition=resolved_composition,
        runtime=runtime,
        media_session_preview=media_session_preview,
        request=resolved_request,
    )
    return {
        "activity_id": resolved_activity_id,
        "toolkit": toolkit,
        "composition": resolved_composition,
        "runtime": runtime,
        "media_session_preview": media_session_preview,
        "activity_runtime": activity_runtime,
    }


def _build_activity_runtime(
    *,
    activity_id: str,
    activity: dict[str, Any],
    composition: dict[str, Any],
    runtime: dict[str, Any],
    media_session_preview: dict[str, Any] | None,
    request: dict[str, Any],
) -> dict[str, Any]:
    interactive_node_type = str(
        composition.get("interactive_node_type")
        or request.get("interactive_node_type")
        or "activity"
    )
    if interactive_node_type == "game":
        game_spec = request.get("game") if isinstance(request.get("game"), dict) else {}
        if not game_spec:
            explanation = composition.get("teacher_explanation")
            explanation = explanation if isinstance(explanation, dict) else {}
            game_spec = {
                "templateId": composition.get("selected_game_template") or "rhythm_echo_core",
                "prompt": explanation.get("why_this_game"),
            }
        return build_game_node(game_spec)["runtime"]
    if interactive_node_type == "instrument_task":
        task_spec = request.get("instrument_task") if isinstance(request.get("instrument_task"), dict) else {}
        return build_instrument_task(task_spec)["runtime"]

    renderer = str(get_activity_interaction(activity_id)["renderer"])
    state = runtime.get("student_game_state") if isinstance(runtime, dict) else {}
    state = state if isinstance(state, dict) else {}
    config = state.get("config") if isinstance(state.get("config"), dict) else {}
    workflow = state.get("workflow") if isinstance(state.get("workflow"), dict) else {}
    blueprint = workflow.get("gameplay_blueprint") if isinstance(workflow.get("gameplay_blueprint"), dict) else {}
    available = request.get("available_materials") if isinstance(request.get("available_materials"), dict) else {}
    teacher_explanation = composition.get("teacher_explanation") if isinstance(composition.get("teacher_explanation"), dict) else {}
    prompt = str(blueprint.get("prompt") or teacher_explanation.get("why_this_game") or "完成这项音乐活动。")
    audio_url = str(
        config.get("audio_clip")
        or available.get("audio_clip")
        or available.get("audio_url")
        or available.get("source_audio_url")
        or ""
    )
    props: dict[str, Any] = {
        "activityId": activity_id,
        "title": str(composition.get("selected_node_title") or activity.get("name") or "音乐活动"),
        "prompt": prompt,
    }

    if renderer == "meter-compare":
        props["meters"] = _list_value(config.get("meters") or available.get("meters"), ["2/4", "3/4"])
    elif renderer == "rhythm-drag":
        props["maxBeats"] = _int_value(config.get("max_beats") or available.get("max_beats"), 4)
        props["cards"] = [
            {"name": "ta", "pattern": "X"},
            {"name": "ti-ti", "pattern": "X X"},
            {"name": "rest", "pattern": "-"},
        ]
        props["targetSequence"] = _list_value(
            config.get("target_sequence") or available.get("rhythm_answer"),
            ["ta", "ti-ti", "ta", "rest"],
        )[:props["maxBeats"]]
    elif renderer == "creation-panel":
        props["defaultTitle"] = "我的音乐小作品"
    elif renderer == "singing-practice":
        props.update({
            "phrases": _list_value(config.get("lyrics_phrases") or available.get("lyrics_phrase"), ["第一乐句", "第二乐句"]),
            "lyrics": str(available.get("lyrics_text") or ""),
            "audioUrl": audio_url,
            "bpm": _int_value(config.get("bpm") or available.get("bpm"), 86),
            "recordingEnabled": True,
        })
    elif renderer == "listening-choice":
        props.update({
            "audioUrl": audio_url,
            "options": _list_value(config.get("expression_traits") or config.get("options") or available.get("mood_options"), ["欢快", "安静", "优美"]),
            "evidenceOptions": _list_value(config.get("evidence_terms"), ["速度", "力度", "旋律", "音色"]),
            "allowExplanation": True,
        })
    elif renderer == "solfege-sort":
        tokens = _list_value(config.get("solfege_set") or config.get("allowed_solfege") or available.get("target_solfege"), ["do", "re", "mi", "sol"])
        props.update({"tokens": tokens, "targetLength": len(tokens), "audioUrl": audio_url})
    elif renderer == "melody-trace":
        notes = _list_value(config.get("pitch_motion") or config.get("solfege_lines") or available.get("pitch_motion"), ["same", "up", "down", "same"])
        props.update({"notes": notes, "levels": ["high", "middle", "low"], "audioUrl": audio_url})
    elif renderer == "timbre-match":
        items = _list_value(config.get("instruments") or config.get("instrument_cards") or available.get("instruments"), ["小提琴", "长笛", "小号", "鼓"])
        options = _list_value(config.get("families") or config.get("family_options"), ["弦乐器", "木管乐器", "铜管乐器", "打击乐器"])
        props.update({"items": items, "options": options, "audioUrl": audio_url})
    elif renderer == "form-order":
        props["sections"] = _list_value(config.get("sections") or config.get("form_sections") or available.get("form_sections"), ["引子", "A段", "B段", "尾声"])
        props["audioUrl"] = audio_url
    elif renderer == "virtual-instrument":
        solfege = _list_value(config.get("allowed_solfege"), ["do", "re", "mi", "sol", "la"])
        frequency = {"do": 261.63, "re": 293.66, "mi": 329.63, "fa": 349.23, "sol": 392.0, "la": 440.0, "si": 493.88}
        colors = ["#e85d4a", "#ed9b2d", "#e1c542", "#54a96b", "#3285b5", "#7659a8", "#bf5b8a"]
        props["keys"] = [
            {"note": note, "label": note, "frequency": frequency.get(note.lower(), 261.63), "color": colors[index % len(colors)]}
            for index, note in enumerate(solfege)
        ]
    elif renderer == "ensemble-roles":
        props.update({
            "roles": _list_value(config.get("roles") or config.get("role_cards") or available.get("ensemble_roles"), ["节奏组", "旋律组", "音色组", "指挥"]),
            "steps": _list_value(config.get("rehearsal_steps") or config.get("steps"), ["确认声部", "分组练习", "合奏排练", "完成展示"]),
            "audioUrl": audio_url,
        })

    classification = get_activity_family(activity_id)
    return {
        "schemaVersion": "interactive-node-runtime.v2",
        "nodeType": "activity",
        "family": classification["family"],
        "variant": classification["variant"],
        "renderer": renderer,
        "legacyRenderer": renderer,
        "props": props,
        "assets": _runtime_assets(runtime),
        "assessment": _assessment_spec(renderer=renderer, props=props),
        "mediaSession": media_session_preview,
    }


def _runtime_assets(runtime: dict[str, Any]) -> list[dict[str, Any]]:
    assets = runtime.get("assets") if isinstance(runtime, dict) else None
    return deepcopy(assets) if isinstance(assets, list) else []


def _assessment_spec(*, renderer: str, props: dict[str, Any]) -> dict[str, Any]:
    spec: dict[str, Any] = {"resultType": renderer, "maxScore": 100}
    if renderer == "rhythm-drag":
        spec.update({"mode": "rule", "answerKey": {"sequence": deepcopy(props.get("targetSequence") or [])}})
    elif renderer == "solfege-sort":
        spec.update({"mode": "rule", "answerKey": {"sequence": deepcopy(props.get("tokens") or [])}})
    elif renderer == "melody-trace":
        raw_notes = _list_value(props.get("notes"), [])
        normalized = [{"up": "high", "same": "middle", "down": "low"}.get(str(note), str(note)) for note in raw_notes]
        spec.update({"mode": "rule", "answerKey": {"trace": normalized}})
    elif renderer == "timbre-match":
        items = [str(item) for item in _list_value(props.get("items"), [])]
        options = [str(item) for item in _list_value(props.get("options"), [])]
        spec.update({"mode": "rule", "answerKey": {"matches": {item: options[index] for index, item in enumerate(items) if index < len(options)}}})
    elif renderer == "form-order":
        spec.update({"mode": "rule", "answerKey": {"order": deepcopy(props.get("sections") or [])}})
    elif renderer in {"listening-choice", "singing-practice"}:
        spec.update({"mode": "rule", "criteria": "completeness_and_practice_evidence"})
    elif renderer in {"creation-panel", "virtual-instrument", "ensemble-roles"}:
        spec.update({
            "mode": "ai",
            "rubric": [
                {"dimension": "任务完成度", "weight": 40},
                {"dimension": "音乐要素运用", "weight": 35},
                {"dimension": "表达与创意", "weight": 25},
            ],
        })
    elif renderer in {"meter-compare", "summary"}:
        spec.update({"mode": "completion", "scoreOnComplete": 80 if renderer == "meter-compare" else None})
    else:
        spec.update({"mode": "completion", "scoreOnComplete": 70})
    return spec


def _list_value(value: Any, fallback: list[Any]) -> list[Any]:
    if isinstance(value, list):
        result = [deepcopy(item) for item in value if str(item).strip()]
        return result or deepcopy(fallback)
    if isinstance(value, str):
        normalized = value.replace("，", ",").replace("；", ",").replace(";", ",")
        result = [item.strip() for item in normalized.split(",") if item.strip()]
        return result or deepcopy(fallback)
    return deepcopy(fallback)


def _int_value(value: Any, fallback: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _resolve_activity_id(*, activity_id: str | None, composition: dict[str, Any] | None) -> str:
    resolved = str(activity_id or "").strip()
    if resolved:
        return resolved
    if isinstance(composition, dict):
        resolved = str(composition.get("selected_activity_id") or "").strip()
    if not resolved:
        raise ValueError("activity_id is required when composition.selected_activity_id is missing")
    return resolved


def _resolve_composition(
    *,
    activity: dict[str, Any],
    toolkit: dict[str, Any],
    composition: dict[str, Any] | None,
) -> dict[str, Any]:
    resolved = deepcopy(composition) if isinstance(composition, dict) else {}
    resolved.setdefault("version", "service_runtime_composition_v1")
    resolved["status"] = str(resolved.get("status") or "ready")
    resolved["selected_activity_id"] = str(resolved.get("selected_activity_id") or activity["activity_id"])
    resolved.setdefault("selected_rules", [])
    resolved.setdefault("education_alignment", deepcopy(activity["education_alignment"]))

    teacher_explanation = resolved.get("teacher_explanation")
    if not isinstance(teacher_explanation, dict):
        teacher_explanation = {}
        resolved["teacher_explanation"] = teacher_explanation
    teacher_explanation.setdefault("why_this_game", _default_why_this_game(activity))

    difficulty = resolved.get("difficulty")
    if not isinstance(difficulty, dict):
        difficulty = {}
        resolved["difficulty"] = difficulty
    difficulty.setdefault("grade_band", _preferred_grade_band(activity.get("grade_bands")))

    if not resolved.get("selected_game_template"):
        game_templates = toolkit.get("selected", {}).get("game_templates", [])
        if isinstance(game_templates, list) and game_templates:
            resolved["selected_game_template"] = str(game_templates[0])
    return resolved


def _default_why_this_game(activity: dict[str, Any]) -> str:
    elements = "、".join(str(item) for item in activity.get("education_alignment", {}).get("music_elements", []) if str(item).strip())
    behaviors = "、".join(str(item) for item in activity.get("student_music_behaviors", []) if str(item).strip())
    if elements and behaviors:
        return f"围绕{elements}组织学生进行{behaviors}。"
    if elements:
        return f"围绕{elements}组织音乐学习活动。"
    if behaviors:
        return f"组织学生进行{behaviors}。"
    return f"组织学生完成{activity.get('name', '音乐活动')}。"


def _preferred_grade_band(value: Any) -> str:
    bands = value if isinstance(value, list) else []
    for band in ("middle_primary", "lower_primary", "upper_primary"):
        if band in bands:
            return band
    return "middle_primary"


def _maybe_build_media_session_preview(
    *,
    activity_id: str,
    composition: dict[str, Any],
    request: dict[str, Any],
) -> dict[str, Any] | None:
    if activity_id not in _MEDIA_SESSION_ACTIVITY_IDS:
        return None
    available = request.get("available_materials") if isinstance(request.get("available_materials"), dict) else {}
    source_url = str(available.get("audio_clip") or available.get("audio_url") or available.get("source_audio_url") or "")
    return build_default_music_media_session(
        session_id=str(available.get("session_id") or f"{activity_id}-session"),
        source_url=source_url,
        source_kind="teacher_upload",
        grade_preset=str(composition.get("difficulty", {}).get("grade_band") or "middle_primary"),
    )
