from __future__ import annotations

import re
from copy import deepcopy
from typing import Any

from app.services.activity_registry import get_activity_template, list_activity_templates
from app.services.pitch_catalog import pitch_tokens_from_text, resolve_pitch_token


MATERIAL_ENTITY_SPEC_VERSION = "material_entity_spec_v1"
MATERIAL_ENTITY_PARSE_VERSION = "material_entity_parse_v1"

REQUIRED_FIELDS = (
    "version",
    "entity_id",
    "label",
    "audience",
    "source_kinds",
    "structured_result_fields",
    "game_ready_schema",
    "matched_binder_ids",
    "recommended_gameplay_template_ids",
    "quality_gates",
    "teacher_confirm_required",
    "do_not_invent_policy",
)


ENTITY_ALIASES: dict[str, str] = {
    "lyrics_phrase": "lyrics_text",
    "song_phrase": "melody_phrase",
    "numbered_score": "melody_phrase",
    "pitch_motion": "melody_phrase",
    "lesson_topic": "lesson_objective",
    "music_focus": "lesson_objective",
    "expression_trait": "timbre_set",
    "instrument_pool": "timbre_set",
    "instrument_family_set": "timbre_set",
    "theme_windows": "form_structure",
    "graphic_symbol_meanings": "form_structure",
}


def _entity(
    entity_id: str,
    label: str,
    *,
    source_kinds: list[str],
    structured_result_fields: list[str],
    game_ready_schema: dict[str, Any],
    matched_binder_ids: list[str],
    recommended_gameplay_template_ids: list[str],
    quality_gates: list[str],
    teacher_confirm_required: list[str],
    music_education_use: str,
) -> dict[str, Any]:
    gates = list(dict.fromkeys(["do_not_invent", *quality_gates]))
    return {
        "version": MATERIAL_ENTITY_SPEC_VERSION,
        "entity_id": entity_id,
        "label": label,
        "audience": "primary_school",
        "source_kinds": source_kinds,
        "structured_result_fields": structured_result_fields,
        "game_ready_schema": game_ready_schema,
        "matched_binder_ids": matched_binder_ids,
        "recommended_gameplay_template_ids": recommended_gameplay_template_ids,
        "quality_gates": gates,
        "teacher_confirm_required": teacher_confirm_required,
        "do_not_invent_policy": "没有在教案、教师需求或上传材料中出现时，保持 missing，不自动编造。",
        "music_education_use": music_education_use,
    }


MATERIAL_ENTITIES: dict[str, dict[str, Any]] = {
    "lesson_objective": _entity(
        "lesson_objective",
        "教学目标 / 音乐学习重点",
        source_kinds=["lesson_text", "teacher_request", "manual_input"],
        structured_result_fields=["objective_text", "music_elements", "student_practices", "grade_hint"],
        game_ready_schema={"value": "string", "music_elements": "list[str]", "student_practices": "list[str]"},
        matched_binder_ids=["listening_evidence_binder", "group_task_binder"],
        recommended_gameplay_template_ids=["listen_choose_explain", "exit_ticket_review", "lesson_opening_hook"],
        quality_gates=["objective_mentions_music_element", "primary_grade_fit"],
        teacher_confirm_required=["music_element_focus"],
        music_education_use="把教案目标转成活动选择依据，确保游戏练的是节奏、旋律、音色、曲式等音乐内容。",
    ),
    "lyrics_text": _entity(
        "lyrics_text",
        "歌词文本 / 歌词乐句",
        source_kinds=["lesson_text", "uploaded_doc", "manual_input"],
        structured_result_fields=["phrases", "line_count", "song_title"],
        game_ready_schema={"phrases": "list[str]", "value": "list[str]"},
        matched_binder_ids=["song_phrase_binder", "lyrics_rhythm_binder"],
        recommended_gameplay_template_ids=["lyrics_rhythm_reading", "lyrics_rhythm_practice", "phrase_loop_singing"],
        quality_gates=["lyrics_not_empty", "phrase_count_confirmable"],
        teacher_confirm_required=["phrase_split"],
        music_education_use="支撑按拍读歌词、歌词节奏、分句学唱和歌词提示隐藏。",
    ),
    "audio_clip": _entity(
        "audio_clip",
        "音频片段",
        source_kinds=["uploaded_audio", "audio_url", "manual_input"],
        structured_result_fields=["url", "filename", "start_seconds", "end_seconds", "source_kind"],
        game_ready_schema={"url": "string", "start_seconds": "number|null", "end_seconds": "number|null"},
        matched_binder_ids=["song_phrase_binder", "listening_evidence_binder", "form_segment_binder", "timbre_pool_binder"],
        recommended_gameplay_template_ids=["phrase_loop_singing", "listen_choose_explain", "theme_return_action", "instrument_timbre_match"],
        quality_gates=["audio_source_present", "boundary_teacher_confirmable"],
        teacher_confirm_required=["audio_clip_boundary"],
        music_education_use="支撑先听后唱、复听找证据、主题再现和音色听辨，不能用无声游戏替代聆听。",
    ),
    "rhythm_pattern": _entity(
        "rhythm_pattern",
        "节奏型",
        source_kinds=["lesson_text", "score_hint", "manual_input"],
        structured_result_fields=["tokens", "notation_text", "duration_policy"],
        game_ready_schema={"tokens": "list[str]", "value": "list[str]"},
        matched_binder_ids=["rhythm_pattern_binder", "lyrics_rhythm_binder"],
        recommended_gameplay_template_ids=["rhythm_warmup", "lyrics_rhythm_reading", "rhythm_question_answer", "body_percussion_builder"],
        quality_gates=["rhythm_tokens_present", "bar_length_teacher_confirmable"],
        teacher_confirm_required=["rhythm_value_check"],
        music_education_use="把四分、八分、休止等节奏材料转为节奏卡、拍击目标和小节长度检查。",
    ),
    "meter": _entity(
        "meter",
        "拍号",
        source_kinds=["lesson_text", "score_hint", "manual_input"],
        structured_result_fields=["value", "strong_weak_pattern"],
        game_ready_schema={"value": "string", "strong_weak_pattern": "list[str]"},
        matched_binder_ids=["rhythm_pattern_binder", "lyrics_rhythm_binder", "graphic_score_binder"],
        recommended_gameplay_template_ids=["meter_body_movement", "strong_weak_beat_circle", "steady_beat_walk"],
        quality_gates=["meter_present", "strong_weak_pattern_ready"],
        teacher_confirm_required=["tempo_or_meter"],
        music_education_use="用于强弱拍律动、节奏小节容量、稳定拍轨和图形谱格数。",
    ),
    "melody_phrase": _entity(
        "melody_phrase",
        "旋律短句 / 唱名材料",
        source_kinds=["lesson_text", "score_hint", "manual_input"],
        structured_result_fields=["solfege", "numbered_notation", "pitch_motion"],
        game_ready_schema={"solfege": "list[str]", "pitch_motion": "list[str]"},
        matched_binder_ids=["song_phrase_binder", "solfege_set_binder"],
        recommended_gameplay_template_ids=["solfege_echo_singing", "melody_contour_trace", "simple_score_following", "xylophone_creation"],
        quality_gates=["pitch_material_present", "singback_teacher_confirmable"],
        teacher_confirm_required=["singback_teacher_confirmation"],
        music_education_use="支撑唱名回声、旋律线描画、识谱跟唱和音条琴限制音级。",
    ),
    "solfege_set": _entity(
        "solfege_set",
        "唱名集合",
        source_kinds=["lesson_text", "score_hint", "manual_input"],
        structured_result_fields=["solfege", "limited_pitch_set"],
        game_ready_schema={"value": "list[str]"},
        matched_binder_ids=["solfege_set_binder"],
        recommended_gameplay_template_ids=["solfege_sorting", "solfege_echo_singing", "xylophone_creation"],
        quality_gates=["pitch_set_limited", "primary_range_fit"],
        teacher_confirm_required=["pitch_set"],
        music_education_use="限制学生可用音级，避免创编游戏脱离歌曲或本课音高材料。",
    ),
    "timbre_set": _entity(
        "timbre_set",
        "音色 / 乐器集合",
        source_kinds=["lesson_text", "uploaded_audio", "manual_input"],
        structured_result_fields=["instruments", "families", "timbre_words", "evidence_terms"],
        game_ready_schema={"instruments": "list[str]", "timbre_words": "list[str]"},
        matched_binder_ids=["timbre_pool_binder", "listening_evidence_binder"],
        recommended_gameplay_template_ids=["instrument_timbre_match", "instrument_family_sorting", "listen_choose_explain"],
        quality_gates=["instrument_or_timbre_present", "generated_playable_skin_required_for_instrument_cards"],
        teacher_confirm_required=["instrument_audio_match"],
        music_education_use="支撑听辨音色、乐器家族分类和用音乐证据描述听感。",
    ),
    "form_structure": _entity(
        "form_structure",
        "曲式 / 段落结构",
        source_kinds=["lesson_text", "score_hint", "manual_input"],
        structured_result_fields=["sections", "form_type", "theme_return"],
        game_ready_schema={"sections": "list[str]", "form_type": "string"},
        matched_binder_ids=["form_segment_binder", "graphic_score_binder"],
        recommended_gameplay_template_ids=["form_ordering", "theme_return_action", "graphic_score_create"],
        quality_gates=["section_labels_present", "audio_window_confirmable_when_needed"],
        teacher_confirm_required=["section_boundaries"],
        music_education_use="支撑 A/B 段排序、主题再现动作和图形谱结构表达。",
    ),
    "classroom_group_task": _entity(
        "classroom_group_task",
        "小组任务 / 声部分工",
        source_kinds=["lesson_text", "teacher_request", "manual_input"],
        structured_result_fields=["groups", "roles", "turn_policy", "ensemble_parts"],
        game_ready_schema={"groups": "list[str]", "roles": "list[str]"},
        matched_binder_ids=["group_task_binder"],
        recommended_gameplay_template_ids=["classroom_band_roles", "orff_percussion_ensemble", "group_relay_performance", "show_and_peer_feedback"],
        quality_gates=["group_task_present", "role_assignment_clear"],
        teacher_confirm_required=["group_count"],
        music_education_use="把班级组织转成可执行的小组任务卡、轮换规则、声部分工和展示流程。",
    ),
    "assessment_criteria": _entity(
        "assessment_criteria",
        "评价标准",
        source_kinds=["lesson_text", "teacher_request", "manual_input"],
        structured_result_fields=["criteria", "observable_evidence", "record_form"],
        game_ready_schema={"criteria": "list[str]", "observable_evidence": "list[str]"},
        matched_binder_ids=["group_task_binder", "listening_evidence_binder"],
        recommended_gameplay_template_ids=["show_and_peer_feedback", "exit_ticket_review", "group_relay_performance"],
        quality_gates=["criteria_observable", "music_evidence_required"],
        teacher_confirm_required=["rubric_weight"],
        music_education_use="让游戏结果留下拍点、演唱、听辨依据、合奏进入和创编说明等音乐学习证据。",
    ),
}


SOLFEGE_TOKENS = ("do", "re", "mi", "fa", "sol", "so", "la", "si", "ti")
RHYTHM_WORDS = ("ta", "ti-ti", "titi", "四分音符", "八分音符", "二分音符", "全音符", "十六分音符", "附点", "切分", "休止")
INSTRUMENT_WORDS = (
    "手鼓",
    "三角铁",
    "木鱼",
    "沙锤",
    "铃鼓",
    "碰铃",
    "钢琴",
    "小提琴",
    "长笛",
    "单簧管",
    "二胡",
    "古筝",
    "笛子",
    "鼓",
)
TIMBRE_WORDS = ("明亮", "柔和", "轻快", "活泼", "优美", "安静", "庄严", "神秘", "低沉", "清脆")

METER_RE = re.compile(r"(?<!\d)([23468]\s*/\s*[248]|[二三四2-4]\s*[拍]\s*子|四二拍|四三拍|四四拍)")
SOLFEGE_RE = re.compile(r"(?i)\b(do|re|mi|fa|sol|so|la|si|ti)\b")
DIGIT_NOTATION_RE = re.compile(r"[1-7][0-7\s,，、;；/\-.]{3,}[0-7]")
PITCH_CONTEXT_RE = re.compile(r"(?:唱名|简谱|旋律(?:短句|材料|音型)?)\s*[:：]\s*(.+)", re.IGNORECASE)


def list_material_entity_specs() -> list[dict[str, Any]]:
    return [validate_material_entity_spec(spec) for spec in MATERIAL_ENTITIES.values()]


def get_material_entity_spec(entity_id: str) -> dict[str, Any]:
    normalized = normalize_material_entity_id(entity_id)
    spec = MATERIAL_ENTITIES.get(normalized)
    if not spec:
        raise ValueError(f"unknown material entity: {entity_id}")
    return validate_material_entity_spec(spec)


def material_entity_specs_for_activity(activity_id: str) -> list[dict[str, Any]]:
    activity = get_activity_template(activity_id)
    seen: set[str] = set()
    specs: list[dict[str, Any]] = []
    for entity_id in activity.get("required_material_entities", []):
        normalized = normalize_material_entity_id(entity_id)
        if normalized in seen or normalized not in MATERIAL_ENTITIES:
            continue
        seen.add(normalized)
        specs.append(get_material_entity_spec(normalized))
    return specs


def validate_material_entity_spec(spec: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(spec, dict):
        raise ValueError("material entity spec must be a dict")
    missing = [field for field in REQUIRED_FIELDS if not spec.get(field)]
    if missing:
        raise ValueError(f"material entity spec missing fields: {', '.join(missing)}")
    if spec.get("version") != MATERIAL_ENTITY_SPEC_VERSION:
        raise ValueError("material entity spec version must be material_entity_spec_v1")
    if spec.get("audience") != "primary_school":
        raise ValueError("material entity spec audience must be primary_school")
    return deepcopy(spec)


def normalize_material_entity_id(entity_id: str) -> str:
    value = str(entity_id or "").strip()
    return ENTITY_ALIASES.get(value, value)


def parse_lesson_material_entities(lesson_text: str, *, extra_need: str = "") -> dict[str, Any]:
    source_text = "\n".join(part for part in [lesson_text, extra_need] if str(part or "").strip())
    game_ready_entities: dict[str, Any] = {}
    detected_entities: list[dict[str, Any]] = []

    for entity_id, detector in (
        ("lesson_objective", _detect_lesson_objective),
        ("lyrics_text", _detect_lyrics_text),
        ("audio_clip", _detect_audio_clip),
        ("rhythm_pattern", _detect_rhythm_pattern),
        ("meter", _detect_meter),
        ("melody_phrase", _detect_melody_phrase),
        ("solfege_set", _detect_solfege_set),
        ("timbre_set", _detect_timbre_set),
        ("form_structure", _detect_form_structure),
        ("classroom_group_task", _detect_group_task),
        ("assessment_criteria", _detect_assessment_criteria),
    ):
        result = detector(source_text)
        if not result:
            continue
        game_ready_entities[entity_id] = result
        detected_entities.append(
            {
                "entity_id": entity_id,
                "label": MATERIAL_ENTITIES[entity_id]["label"],
                "confidence": result.get("confidence", "medium"),
                "source": result.get("source", "lesson_text"),
            }
        )

    missing_entities = [entity_id for entity_id in MATERIAL_ENTITIES if entity_id not in game_ready_entities]
    binding_recommendations = _binding_recommendations(game_ready_entities)
    teacher_confirm_fields = _teacher_confirm_fields(game_ready_entities, missing_entities)
    return {
        "version": MATERIAL_ENTITY_PARSE_VERSION,
        "audience": "primary_school",
        "status": "ready_for_binding" if binding_recommendations else "needs_teacher_material",
        "detected_entities": detected_entities,
        "game_ready_entities": game_ready_entities,
        "missing_entities": missing_entities,
        "teacher_confirm_fields": teacher_confirm_fields,
        "binding_recommendations": binding_recommendations,
        "do_not_invent_policy": {
            "missing_values_must_stay_missing": True,
            "message": "没有从教案、教师需求或上传材料中识别到的内容不会自动补写；需要教师确认或补充。",
        },
    }


def material_entity_catalog() -> dict[str, Any]:
    return {
        "version": "material_entity_catalog_v1",
        "audience": "primary_school",
        "entities": list_material_entity_specs(),
        "aliases": deepcopy(ENTITY_ALIASES),
        "activity_coverage": {
            activity["activity_id"]: [
                normalize_material_entity_id(entity_id)
                for entity_id in activity.get("required_material_entities", [])
                if normalize_material_entity_id(entity_id) in MATERIAL_ENTITIES
            ]
            for activity in list_activity_templates()
        },
        "parser_contract": {
            "version": MATERIAL_ENTITY_PARSE_VERSION,
            "input": ["lesson_text", "extra_need"],
            "output": ["game_ready_entities", "missing_entities", "teacher_confirm_fields", "binding_recommendations"],
            "policy": "只提取可追溯到教案或教师需求的材料，缺失项保持 missing。",
        },
    }


def parsed_entities_to_available_materials(parsed: dict[str, Any]) -> dict[str, Any]:
    entities = parsed.get("game_ready_entities", {}) if isinstance(parsed, dict) else {}
    if not isinstance(entities, dict):
        return {}
    materials: dict[str, Any] = {}
    if "lyrics_text" in entities:
        phrases = entities["lyrics_text"].get("phrases") if isinstance(entities["lyrics_text"], dict) else None
        if phrases:
            materials["lyrics_text"] = phrases
            materials["lyrics_phrase"] = phrases
    if "audio_clip" in entities:
        materials["audio_clip"] = deepcopy(entities["audio_clip"])
    if "rhythm_pattern" in entities:
        tokens = entities["rhythm_pattern"].get("tokens") if isinstance(entities["rhythm_pattern"], dict) else None
        if tokens:
            materials["rhythm_pattern"] = tokens
    if "meter" in entities:
        value = entities["meter"].get("value") if isinstance(entities["meter"], dict) else None
        if value:
            materials["meter"] = value
    if "melody_phrase" in entities:
        materials["melody_phrase"] = deepcopy(entities["melody_phrase"])
        motion = entities["melody_phrase"].get("pitch_motion") if isinstance(entities["melody_phrase"], dict) else None
        if motion:
            materials["pitch_motion"] = motion
    if "solfege_set" in entities:
        value = entities["solfege_set"].get("value") if isinstance(entities["solfege_set"], dict) else None
        if value:
            materials["solfege_set"] = value
    if "timbre_set" in entities:
        timbre = entities["timbre_set"]
        materials["timbre_set"] = deepcopy(timbre)
        if isinstance(timbre, dict) and timbre.get("instruments"):
            materials["instrument_pool"] = timbre["instruments"]
    if "form_structure" in entities:
        materials["form_structure"] = deepcopy(entities["form_structure"])
    if "classroom_group_task" in entities:
        materials["classroom_group_task"] = deepcopy(entities["classroom_group_task"])
    if "assessment_criteria" in entities:
        criteria = entities["assessment_criteria"].get("criteria") if isinstance(entities["assessment_criteria"], dict) else None
        if criteria:
            materials["assessment_criteria"] = criteria
    if "lesson_objective" in entities:
        objective = entities["lesson_objective"].get("value") if isinstance(entities["lesson_objective"], dict) else None
        if objective:
            materials["music_focus"] = objective
            materials["lesson_topic"] = objective
    return materials


def _detect_lesson_objective(text: str) -> dict[str, Any] | None:
    line = _first_matching_line(text, ("教学目标", "学习目标", "本课目标", "目标：", "能"))
    if not line:
        return None
    return {
        "value": _after_colon(line),
        "music_elements": _music_elements(text),
        "student_practices": _student_practices(text),
        "confidence": "medium",
        "source": "lesson_text",
    }


def _detect_lyrics_text(text: str) -> dict[str, Any] | None:
    line = _first_matching_line(text, ("歌词", "唱词"))
    if not line:
        return None
    content = _after_colon(line)
    phrases = [part.strip(" ，,。") for part in re.split(r"[，,。；;、/]", content) if 1 < len(part.strip()) <= 30]
    if not phrases:
        return None
    return {"value": phrases, "phrases": phrases, "line_count": len(phrases), "confidence": "medium", "source": "lesson_text"}


def _detect_audio_clip(text: str) -> dict[str, Any] | None:
    match = re.search(r"(https?://\S+\.(?:mp3|wav|m4a|ogg)|[\w\-.一-龥]+?\.(?:mp3|wav|m4a|ogg))", text, re.I)
    if not match:
        return None
    return {
        "url": match.group(1).rstrip("。；;，,"),
        "start_seconds": None,
        "end_seconds": None,
        "source_kind": "lesson_text",
        "confidence": "medium",
        "source": "lesson_text",
    }


def _detect_rhythm_pattern(text: str) -> dict[str, Any] | None:
    tokens: list[str] = []
    lower = text.lower()
    for token in RHYTHM_WORDS:
        if token.lower() in lower:
            tokens.append(token)
    if not tokens:
        return None
    return {
        "value": tokens,
        "tokens": tokens,
        "notation_text": _first_matching_line(text, ("节奏型", "节奏", "休止")) or " ".join(tokens),
        "confidence": "medium",
        "source": "lesson_text",
    }


def _detect_meter(text: str) -> dict[str, Any] | None:
    match = METER_RE.search(text)
    if not match:
        return None
    value = _normalize_meter(match.group(1))
    return {
        "value": value,
        "strong_weak_pattern": _strong_weak_pattern(value),
        "confidence": "medium",
        "source": "lesson_text",
    }


def _detect_melody_phrase(text: str) -> dict[str, Any] | None:
    contextual_tokens, numbered_notation = _contextual_pitch_tokens(text)
    solfege = contextual_tokens or _natural_solfege_tokens(text)
    if len(solfege) < 3:
        return None
    return {
        "solfege": solfege,
        "numbered_notation": numbered_notation,
        "pitch_motion": _pitch_motion(solfege),
        "confidence": "medium",
        "source": "lesson_text",
    }


def _detect_solfege_set(text: str) -> dict[str, Any] | None:
    contextual_tokens, _ = _contextual_pitch_tokens(text)
    source_tokens = contextual_tokens or _natural_solfege_tokens(text)
    solfege = []
    for token in source_tokens:
        if token not in solfege:
            solfege.append(token)
    if not solfege:
        return None
    return {"value": solfege, "limited_pitch_set": solfege, "confidence": "medium", "source": "lesson_text"}


def _detect_timbre_set(text: str) -> dict[str, Any] | None:
    instruments = [word for word in INSTRUMENT_WORDS if word in text]
    timbre_words = [word for word in TIMBRE_WORDS if word in text]
    if not instruments and not timbre_words:
        return None
    return {
        "instruments": instruments,
        "families": _instrument_families(instruments),
        "timbre_words": timbre_words,
        "evidence_terms": timbre_words or ["音色"],
        "confidence": "medium",
        "source": "lesson_text",
    }


def _detect_form_structure(text: str) -> dict[str, Any] | None:
    upper_text = text.upper()
    sections = []
    for label in ("A", "B", "C"):
        if f"{label}段" in upper_text or f"{label}主题" in upper_text:
            sections.append(label)
    if "ABA" in upper_text:
        sections = ["A", "B", "A"]
    if not sections and not any(word in text for word in ("曲式", "段落", "再现", "重复", "对比", "回旋")):
        return None
    return {
        "sections": sections or ["A", "B"],
        "form_type": "ABA" if sections == ["A", "B", "A"] or "ABA" in upper_text else "contrast_or_repeat",
        "theme_return": "再现" in text or "回到A段" in text or "回到 A 段" in text,
        "confidence": "medium",
        "source": "lesson_text",
    }


def _detect_group_task(text: str) -> dict[str, Any] | None:
    if not any(word in text for word in ("小组", "声部", "分组", "合奏", "轮流", "轮换", "接力")):
        return None
    groups = re.findall(r"([\u4e00-\u9fa5A-Za-z0-9]+组)", text)
    return {
        "groups": list(dict.fromkeys(groups)) or ["第1组", "第2组"],
        "roles": _group_roles(text),
        "turn_policy": "轮流" if "轮流" in text or "轮换" in text else "同时或接力",
        "confidence": "medium",
        "source": "lesson_text",
    }


def _detect_assessment_criteria(text: str) -> dict[str, Any] | None:
    line = _first_matching_line(text, ("评价标准", "评价", "互评", "出口票", "量规"))
    if not line:
        return None
    content = _after_colon(line)
    criteria = [part.strip(" ，,。") for part in re.split(r"[、，,；;]", content) if len(part.strip()) > 1]
    return {
        "criteria": criteria or [content],
        "observable_evidence": [item for item in criteria if any(word in item for word in ("能", "说出", "跟", "进入", "表现"))] or criteria,
        "record_form": "rubric",
        "confidence": "medium",
        "source": "lesson_text",
    }


def _binding_recommendations(game_ready_entities: dict[str, Any]) -> list[dict[str, Any]]:
    recommendations: list[dict[str, Any]] = []
    entity_ids = set(game_ready_entities)
    priority = {
        "lyrics_text": 0,
        "rhythm_pattern": 1,
        "meter": 2,
        "melody_phrase": 3,
        "solfege_set": 4,
        "audio_clip": 5,
        "timbre_set": 6,
        "form_structure": 7,
        "classroom_group_task": 8,
        "assessment_criteria": 9,
        "lesson_objective": 10,
    }
    sorted_specs = sorted(MATERIAL_ENTITIES.values(), key=lambda spec: priority.get(spec["entity_id"], 99))
    for spec in sorted_specs:
        if spec["entity_id"] not in entity_ids:
            continue
        recommendations.append(
            {
                "entity_id": spec["entity_id"],
                "binder_ids": deepcopy(spec["matched_binder_ids"]),
                "activity_ids": deepcopy(spec["recommended_gameplay_template_ids"]),
                "reason": spec["music_education_use"],
            }
        )
    return recommendations


def _teacher_confirm_fields(game_ready_entities: dict[str, Any], missing_entities: list[str]) -> list[str]:
    fields: list[str] = []
    for entity_id in game_ready_entities:
        fields.extend(MATERIAL_ENTITIES[entity_id]["teacher_confirm_required"])
    for entity_id in missing_entities:
        if entity_id in {"audio_clip", "meter", "assessment_criteria"}:
            fields.append(entity_id)
    return list(dict.fromkeys(fields))


def _first_matching_line(text: str, markers: tuple[str, ...]) -> str:
    for line in _lines(text):
        if any(marker in line for marker in markers):
            return line
    return ""


def _lines(text: str) -> list[str]:
    return [re.sub(r"\s+", " ", line).strip() for line in re.split(r"[\n。；;]", str(text or "")) if line.strip()]


def _after_colon(line: str) -> str:
    parts = re.split(r"[:：]", line, maxsplit=1)
    return (parts[1] if len(parts) > 1 else line).strip()


def _normalize_meter(value: str) -> str:
    compact = re.sub(r"\s+", "", value)
    if compact in {"四二拍", "二拍子", "2拍子"}:
        return "2/4"
    if compact in {"四三拍", "三拍子", "3拍子"}:
        return "3/4"
    if compact in {"四四拍", "四拍子", "4拍子"}:
        return "4/4"
    return compact


def _strong_weak_pattern(meter: str) -> list[str]:
    if meter.startswith("2/"):
        return ["强", "弱"]
    if meter.startswith("3/"):
        return ["强", "弱", "弱"]
    if meter.startswith("4/"):
        return ["强", "弱", "次强", "弱"]
    return ["强", "弱"]


def _pitch_motion(solfege: list[str]) -> list[str]:
    motion = []
    for current, next_item in zip(solfege, solfege[1:]):
        current_pitch = resolve_pitch_token(current)
        next_pitch = resolve_pitch_token(next_item)
        current_semitone = int(current_pitch["semitone"]) if current_pitch else 0
        next_semitone = int(next_pitch["semitone"]) if next_pitch else 0
        delta = next_semitone - current_semitone
        motion.append("up" if delta > 0 else "down" if delta < 0 else "same")
    return motion


def _natural_solfege_tokens(text: str) -> list[str]:
    tokens: list[str] = []
    for item in SOLFEGE_RE.findall(text):
        pitch = resolve_pitch_token(item)
        if pitch:
            tokens.append(str(pitch["id"]))
    return tokens


def _contextual_pitch_tokens(text: str) -> tuple[list[str], str]:
    tokens: list[str] = []
    notation_parts: list[str] = []
    for line in _lines(text):
        match = PITCH_CONTEXT_RE.search(line)
        if not match:
            continue
        notation = match.group(1).strip()
        line_tokens = pitch_tokens_from_text(notation, unique=False)
        if line_tokens:
            tokens.extend(line_tokens)
            notation_parts.append(notation)
    return tokens, " ".join(notation_parts)


def _music_elements(text: str) -> list[str]:
    mapping = {
        "节奏": ("节奏", "节拍", "稳定拍", "休止"),
        "旋律": ("旋律", "唱名", "音高", "do", "re", "mi"),
        "音色": ("音色", "乐器", "手鼓", "三角铁"),
        "曲式": ("曲式", "段落", "A段", "B段", "再现"),
        "力度": ("力度", "强", "弱", "渐强"),
        "速度": ("速度", "快", "慢"),
    }
    return [label for label, markers in mapping.items() if any(marker in text for marker in markers)] or ["音乐要素"]


def _student_practices(text: str) -> list[str]:
    practices = []
    for marker, practice in (
        ("听", "listen"),
        ("唱", "sing"),
        ("朗读", "read"),
        ("拍", "tap"),
        ("律动", "move"),
        ("创编", "create"),
        ("评价", "assess"),
        ("合奏", "perform"),
    ):
        if marker in text and practice not in practices:
            practices.append(practice)
    return practices or ["listen"]


def _instrument_families(instruments: list[str]) -> list[str]:
    families = []
    if any(item in instruments for item in ("手鼓", "三角铁", "木鱼", "沙锤", "铃鼓", "碰铃", "鼓")):
        families.append("打击乐器")
    if any(item in instruments for item in ("小提琴", "二胡", "古筝")):
        families.append("弦乐器")
    if any(item in instruments for item in ("长笛", "单簧管", "笛子")):
        families.append("管乐器")
    if "钢琴" in instruments:
        families.append("键盘乐器")
    return families


def _group_roles(text: str) -> list[str]:
    roles = []
    for marker in ("拍手", "手鼓", "三角铁", "木鱼", "沙锤", "演唱", "律动"):
        if marker in text:
            roles.append(marker)
    return roles or ["节奏声部", "旋律声部"]
