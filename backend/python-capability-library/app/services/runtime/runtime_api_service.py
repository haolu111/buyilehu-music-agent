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
        template_id = str(
            game_spec.get("templateId")
            or game_spec.get("template_id")
            or composition.get("selected_game_template")
            or "rhythm_echo_core"
        )
        state = runtime.get("student_game_state") if isinstance(runtime, dict) else None
        if isinstance(state, dict):
            return {
                "schemaVersion": "interactive-node-runtime.v2",
                "nodeType": "game",
                "family": "music_game",
                "variant": template_id,
                "renderer": "reviewed-game",
                "legacyRenderer": build_game_node(game_spec)["runtime"]["legacyRenderer"],
                "componentUrl": (
                    f"/template-console/student-game.html?"
                    f"template={template_id}&review=1"
                ),
                "props": {
                    "title": str(composition.get("selected_node_title") or "音乐游戏"),
                    "studentGameState": deepcopy(state),
                },
                "assets": _runtime_assets(runtime),
                "assessment": {
                    "mode": "game_rule",
                    "resultType": template_id,
                    "maxScore": 100,
                },
                "mediaSession": media_session_preview,
            }
        return build_game_node(game_spec)["runtime"]
    if interactive_node_type == "instrument_task":
        task_spec = request.get("instrument_task") if isinstance(request.get("instrument_task"), dict) else {}
        return build_instrument_task(task_spec)["runtime"]

    interaction = get_activity_interaction(activity_id)
    renderer = str(interaction["renderer"])
    legacy_renderer = str(interaction["legacy_renderer"])
    state = runtime.get("student_game_state") if isinstance(runtime, dict) else {}
    state = state if isinstance(state, dict) else {}
    config = state.get("config") if isinstance(state.get("config"), dict) else {}
    workflow = state.get("workflow") if isinstance(state.get("workflow"), dict) else {}
    blueprint = workflow.get("gameplay_blueprint") if isinstance(workflow.get("gameplay_blueprint"), dict) else {}
    available = request.get("available_materials") if isinstance(request.get("available_materials"), dict) else {}
    teacher_explanation = composition.get("teacher_explanation") if isinstance(composition.get("teacher_explanation"), dict) else {}
    prompt = str(
        composition.get("selected_node_reason")
        or blueprint.get("prompt")
        or teacher_explanation.get("why_this_game")
        or "完成这项音乐活动。"
    )
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
    resolved_music_content = (
        request.get("resolved_music_content")
        if isinstance(request.get("resolved_music_content"), dict)
        else composition.get("resolved_music_content")
    )
    if isinstance(resolved_music_content, dict) and resolved_music_content:
        props["musicContent"] = deepcopy(resolved_music_content)
        meters = resolved_music_content.get("meters")
        if isinstance(meters, list) and meters:
            props["meters"] = [
                str(item.get("signature"))
                for item in meters if isinstance(item, dict) and item.get("signature")
            ]
        if resolved_music_content.get("bpm") is not None:
            config["bpm"] = resolved_music_content["bpm"]
        rhythm_patterns = resolved_music_content.get("rhythm_patterns")
        if isinstance(rhythm_patterns, list) and rhythm_patterns:
            props["rhythmPatterns"] = deepcopy(rhythm_patterns)
            props["cards"] = [
                {"name": str(item.get("label") or item.get("id")), "pattern": " ".join(item.get("tokens") or [])}
                for item in rhythm_patterns if isinstance(item, dict)
            ]
            props["targetSequence"] = [
                str(token)
                for item in rhythm_patterns if isinstance(item, dict)
                for token in (item.get("tokens") or [])
            ]
        pitch_sets = resolved_music_content.get("pitch_sets")
        if isinstance(pitch_sets, list) and pitch_sets:
            props["pitchSets"] = deepcopy(pitch_sets)
            props["tokens"] = list(pitch_sets[0].get("notes") or [])
        melody_phrases = resolved_music_content.get("melody_phrases")
        if isinstance(melody_phrases, list) and melody_phrases:
            props["melodyPhrases"] = deepcopy(melody_phrases)
            props["notes"] = list(melody_phrases[0].get("contour") or melody_phrases[0].get("notes") or [])
        forms = resolved_music_content.get("forms")
        if isinstance(forms, list) and forms:
            props["forms"] = deepcopy(forms)
            props["sections"] = list(forms[0].get("sections") or [])
        dynamics = resolved_music_content.get("dynamics")
        if isinstance(dynamics, list) and dynamics:
            props["dynamics"] = deepcopy(dynamics)
            props["dynamicOptions"] = [str(item.get("symbol") or item.get("label")) for item in dynamics]
        timbres = resolved_music_content.get("timbres")
        if isinstance(timbres, list) and timbres:
            props["timbres"] = deepcopy(timbres)
            props["items"] = [str(item.get("label") or item.get("id")) for item in timbres]
            props["instrument"] = str(timbres[0].get("instrument") or "")

    if legacy_renderer == "meter-compare":
        props["meters"] = props.get("meters") or _list_value(
            config.get("meters") or available.get("meters"), ["2/4", "3/4"],
        )
    elif legacy_renderer == "rhythm-drag":
        props["maxBeats"] = _int_value(config.get("max_beats") or available.get("max_beats"), 4)
        props["cards"] = props.get("cards") or [
            {"name": "ta", "pattern": "X"},
            {"name": "ti-ti", "pattern": "X X"},
            {"name": "rest", "pattern": "-"},
        ]
        props["targetSequence"] = props.get("targetSequence") or _list_value(
            config.get("target_sequence") or available.get("rhythm_answer"),
            ["ta", "ti-ti", "ta", "rest"],
        )[:props["maxBeats"]]
    elif legacy_renderer == "creation-panel":
        props["defaultTitle"] = "我的音乐小作品"
    elif legacy_renderer == "singing-practice":
        props.update({
            "phrases": _list_value(config.get("lyrics_phrases") or available.get("lyrics_phrase"), ["第一乐句", "第二乐句"]),
            "lyrics": str(available.get("lyrics_text") or ""),
            "audioUrl": audio_url,
            "bpm": _int_value(config.get("bpm") or available.get("bpm"), 86),
            "recordingEnabled": True,
        })
    elif legacy_renderer == "listening-choice":
        props.update({
            "audioUrl": audio_url,
            "options": _list_value(config.get("expression_traits") or config.get("options") or available.get("mood_options"), ["欢快", "安静", "优美"]),
            "evidenceOptions": _list_value(config.get("evidence_terms"), ["速度", "力度", "旋律", "音色"]),
            "allowExplanation": True,
        })
    elif legacy_renderer == "solfege-sort":
        tokens = props.get("tokens") or _list_value(config.get("solfege_set") or config.get("allowed_solfege") or available.get("target_solfege"), ["do", "re", "mi", "sol"])
        props.update({"tokens": tokens, "targetLength": len(tokens), "audioUrl": audio_url})
    elif legacy_renderer == "melody-trace":
        notes = props.get("notes") or _list_value(config.get("pitch_motion") or config.get("solfege_lines") or available.get("pitch_motion"), ["same", "up", "down", "same"])
        props.update({"notes": notes, "levels": ["high", "middle", "low"], "audioUrl": audio_url})
    elif legacy_renderer == "timbre-match":
        items = props.get("items") or _list_value(config.get("instruments") or config.get("instrument_cards") or available.get("instruments"), ["小提琴", "长笛", "小号", "鼓"])
        options = _list_value(config.get("families") or config.get("family_options"), ["弦乐器", "木管乐器", "铜管乐器", "打击乐器"])
        props.update({"items": items, "options": options, "audioUrl": audio_url})
    elif legacy_renderer == "form-order":
        props["sections"] = props.get("sections") or _list_value(config.get("sections") or config.get("form_sections") or available.get("form_sections"), ["引子", "A段", "B段", "尾声"])
        props["audioUrl"] = audio_url
    elif legacy_renderer == "virtual-instrument":
        instrument_id = _legacy_virtual_instrument_id(
            activity_id=activity_id,
            config=config,
            available=available,
            composition=composition,
        )
        props["instrumentId"] = instrument_id
        solfege = props.get("tokens") or _list_value(config.get("allowed_solfege"), ["do", "re", "mi", "sol", "la"])
        frequency = {"do": 261.63, "re": 293.66, "mi": 329.63, "fa": 349.23, "sol": 392.0, "la": 440.0, "si": 493.88}
        colors = ["#e85d4a", "#ed9b2d", "#e1c542", "#54a96b", "#3285b5", "#7659a8", "#bf5b8a"]
        props["keys"] = [
            {"note": note, "label": note, "frequency": frequency.get(note.lower(), 261.63), "color": colors[index % len(colors)]}
            for index, note in enumerate(solfege)
        ]
    elif legacy_renderer == "ensemble-roles":
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
        "legacyRenderer": legacy_renderer,
        "componentUrl": interaction.get("component_url"),
        "props": props,
        "assets": _runtime_assets(runtime),
        "assessment": _assessment_spec(renderer=legacy_renderer, props=props),
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
    behavior_labels = {
        "listen": "聆听", "choose": "选择", "explain": "说明理由", "assess": "评价",
        "perform": "表演", "cooperate": "合作", "create": "创编", "revise": "修改",
        "tap": "拍击", "move": "律动", "sing": "演唱", "read": "朗读", "play": "演奏",
    }


def _legacy_virtual_instrument_id(
    *,
    activity_id: str,
    config: dict[str, Any],
    available: dict[str, Any],
    composition: dict[str, Any],
) -> str:
    """Upgrade legacy virtual-instrument activities to an explicit audited skin."""
    candidates = [
        config.get("instrumentId"),
        config.get("instrument_id"),
        available.get("instrumentId"),
        available.get("instrument_id"),
        composition.get("instrumentId"),
        composition.get("instrument_id"),
    ]
    aliases = {
        "piano": "virtual_piano",
        "钢琴": "virtual_piano",
        "xylophone": "virtual_xylophone",
        "木琴": "virtual_xylophone",
        "drum": "virtual_frame_drum",
        "鼓": "virtual_frame_drum",
        "rhythm_pad": "virtual_frame_drum",
    }
    for candidate in candidates:
        normalized = aliases.get(str(candidate or "").strip(), str(candidate or "").strip())
        if normalized.startswith("virtual_"):
            return normalized
    if activity_id == "xylophone_creation":
        return "virtual_xylophone"
    if any(token in activity_id for token in ("melody", "pitch", "keyboard", "piano")):
        return "virtual_piano"
    return "virtual_frame_drum"
    behaviors = "、".join(
        behavior_labels.get(str(item), str(item))
        for item in activity.get("student_music_behaviors", [])
        if str(item).strip()
    )
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
