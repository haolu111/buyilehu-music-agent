from __future__ import annotations

from copy import deepcopy
import re
from typing import Any

from app.services.default_music_material_library import choose_default_material_for_focus
from app.services.music_education_alignment import validate_music_education_alignment


ACTIVITY_SPEC_VERSION = "activity_spec_v1"

REQUIRED_ACTIVITY_TEMPLATE_FIELDS = (
    "version",
    "activity_id",
    "name",
    "audience",
    "grade_bands",
    "classroom_stage",
    "student_music_behaviors",
    "required_material_entities",
    "toolkit",
    "teacher_controls",
    "acceptance",
    "education_alignment",
)


def validate_activity_template_spec(spec: dict[str, Any]) -> dict[str, Any]:
    missing = [field for field in REQUIRED_ACTIVITY_TEMPLATE_FIELDS if not spec.get(field)]
    if missing:
        raise ValueError(f"activity template spec missing fields: {', '.join(missing)}")
    if spec.get("version") != "activity_template_spec_v1":
        raise ValueError("activity template spec version must be activity_template_spec_v1")
    if spec.get("audience") != "primary_school":
        raise ValueError("activity template audience must be primary_school")
    toolkit = spec.get("toolkit")
    if not isinstance(toolkit, dict):
        raise ValueError("activity template toolkit must be a dict")
    for key in ("components", "teaching_aids", "virtual_instruments"):
        if key not in toolkit or not isinstance(toolkit.get(key), list):
            raise ValueError(f"activity template toolkit.{key} must be a list")
    validated = deepcopy(spec)
    validated["education_alignment"] = validate_music_education_alignment(
        spec.get("education_alignment"),
        activity_id=str(spec.get("activity_id") or "unknown"),
        allowed_practices=[str(item) for item in spec.get("student_music_behaviors", [])],
        allowed_teaching_stages=[str(item) for item in spec.get("classroom_stage", [])],
        grade_bands=[str(item) for item in spec.get("grade_bands", [])],
    )
    return validated


def build_activity_spec_from_teacher_request(
    teacher_request: str,
    *,
    options: dict[str, Any] | None = None,
) -> dict[str, Any]:
    options = options if isinstance(options, dict) else {}
    text = str(teacher_request or "").strip()
    completeness = _direct_completeness(text, options)
    if completeness["status"] == "needs_clarification":
        return _direct_clarification_spec(text, completeness)

    music_focus = _music_focus(text, options)
    default_material = choose_default_material_for_focus(music_focus)
    activity_shape = _activity_shape(text, options)
    toolkit_ref = _toolkit_ref(activity_shape, music_focus, text)
    spec = {
        "version": ACTIVITY_SPEC_VERSION,
        "source_mode": "direct",
        "grounding_source": "teacher_request",
        "activity_goal": _activity_goal(text, music_focus, activity_shape),
        "grade_band": _grade_band(text, options),
        "classroom_stage": _classroom_stage(text, options),
        "activity_shape": activity_shape,
        "student_music_behaviors": _student_behaviors(text, music_focus),
        "music_focus": {"label": music_focus, "default_material_ref": default_material["material_id"]},
        "material_refs": _material_refs(text, default_material),
        "toolkit_ref": toolkit_ref,
        "difficulty_profile_ref": _difficulty_profile(text, options),
        "runtime_ref": _runtime_ref(text, options),
        "classroom_minutes": _classroom_minutes(text, options),
        "quality_gate_result": {"status": "pass", "checks": ["direct_source_transparent", "registry_toolkit_selected"]},
        "teacher_request": text,
        "assumptions": _direct_assumptions(text, default_material),
        "confirmation_required": [],
        "default_material": default_material,
    }
    return spec


def build_activity_spec_from_lesson(lesson_payload: dict[str, Any], *, options: dict[str, Any] | None = None) -> dict[str, Any]:
    options = options if isinstance(options, dict) else {}
    context = _lesson_context(lesson_payload)
    lesson_fit = _lesson_fit(lesson_payload, context)
    evidence = lesson_fit.get("lesson_evidence") if isinstance(lesson_fit.get("lesson_evidence"), dict) else {}
    if not evidence:
        raise ValueError("lesson_based activity requires lesson evidence")
    material = lesson_fit.get("material_binding") if isinstance(lesson_fit.get("material_binding"), dict) else {}
    stage = str(evidence.get("target_stage") or context.get("target_stage") or "").strip()
    music_focus = str(evidence.get("music_element") or context.get("target_music_element") or "").strip()
    source_summary = str(
        evidence.get("segment_task")
        or evidence.get("source_quote_or_summary")
        or evidence.get("target_objective")
        or context.get("teaching_objective")
        or evidence.get("music_element")
        or context.get("target_music_element")
        or ""
    ).strip()
    spec = {
        "version": ACTIVITY_SPEC_VERSION,
        "source_mode": "lesson_based",
        "grounding_source": "uploaded_lesson",
        "activity_goal": str(evidence.get("target_objective") or context.get("teaching_objective") or f"{stage}{music_focus}").strip(),
        "grade_band": str(context.get("grade_band") or options.get("grade_band") or "").strip(),
        "classroom_stage": stage,
        "activity_shape": _lesson_activity_shape(music_focus, source_summary),
        "student_music_behaviors": _lesson_student_behaviors(evidence, source_summary),
        "music_focus": {"label": music_focus},
        "material_refs": [material.get("selected_phrase_label")] if material.get("selected_phrase_label") else [],
        "toolkit_ref": _toolkit_ref(_lesson_activity_shape(music_focus, source_summary), music_focus, source_summary),
        "difficulty_profile_ref": _difficulty_profile(str(context.get("grade_band") or ""), options),
        "runtime_ref": _runtime_ref(source_summary, options),
        "classroom_minutes": _classroom_minutes(source_summary, options),
        "quality_gate_result": {"status": "pass", "checks": ["lesson_evidence_present", "no_free_lesson_flow_expansion"]},
        "lesson_evidence": {
            "stage": stage,
            "source_quote_or_summary": source_summary,
            "material_ref": material.get("selected_phrase_label", ""),
            "student_behavior": _lesson_student_behaviors(evidence, source_summary),
        },
    }
    return spec


def _direct_completeness(text: str, options: dict[str, Any]) -> dict[str, Any]:
    missing: list[str] = []
    if not _grade_band(text, options):
        missing.append("年级/学段")
    if not _music_focus(text, options):
        missing.append("音乐目标")
    if not _activity_shape(text, options):
        missing.append("活动形态")
    if not _has_material_or_default(text):
        missing.append("音乐材料或默认材料")
    if not _classroom_minutes(text, options):
        missing.append("课堂时间")
    if not _runtime_ref(text, options):
        missing.append("设备条件")
    too_vague = len(text) < 12 or text in {"做个音乐游戏", "做一个音乐游戏", "音乐游戏"}
    if too_vague or len(missing) >= 4:
        return {"status": "needs_clarification", "missing": missing[:3]}
    return {"status": "ready", "missing": missing}


def _direct_clarification_spec(text: str, completeness: dict[str, Any]) -> dict[str, Any]:
    questions = [
        "年级/学段是什么？",
        "想练节奏、音高还是音色？",
        "课堂时间几分钟？",
    ][:3]
    return {
        "version": ACTIVITY_SPEC_VERSION,
        "source_mode": "direct",
        "grounding_source": "teacher_request",
        "activity_goal": "",
        "grade_band": "",
        "classroom_stage": "",
        "activity_shape": "unknown",
        "student_music_behaviors": [],
        "music_focus": {},
        "material_refs": [],
        "toolkit_ref": "",
        "difficulty_profile_ref": "",
        "runtime_ref": "",
        "quality_gate_result": {"status": "needs_clarification", "missing": deepcopy(completeness.get("missing", []))},
        "teacher_request": text,
        "assumptions": ["未上传教案"],
        "confirmation_required": questions,
        "clarification_card": {
            "teacher_message": "可以，我先帮你选方向：你想练哪一个？",
            "choices": [
                {"label": "节奏闯关", "music_focus": "节奏", "activity_shape": "game"},
                {"label": "音高听辨", "music_focus": "音高", "activity_shape": "game"},
                {"label": "音色侦探", "music_focus": "音色", "activity_shape": "game"},
            ],
        },
    }


def _lesson_context(payload: dict[str, Any]) -> dict[str, Any]:
    analysis = payload.get("lesson_analysis") if isinstance(payload.get("lesson_analysis"), dict) else {}
    context: dict[str, Any] = {}
    if isinstance(payload.get("lesson_context"), dict):
        context.update(payload["lesson_context"])
    if isinstance(analysis.get("lesson_context"), dict):
        context.update(analysis["lesson_context"])
    return context


def _lesson_fit(payload: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    for value in (
        payload.get("lesson_fit") if isinstance(payload.get("lesson_fit"), dict) else {},
        context.get("lesson_fit") if isinstance(context.get("lesson_fit"), dict) else {},
        payload.get("lesson_analysis", {}).get("lesson_fit") if isinstance(payload.get("lesson_analysis"), dict) and isinstance(payload.get("lesson_analysis", {}).get("lesson_fit"), dict) else {},
    ):
        if value:
            return value
    return {}


def _grade_band(text: str, options: dict[str, Any]) -> str:
    if options.get("grade_band"):
        return str(options["grade_band"])
    if "一年级" in text or "二年级" in text or "低年级" in text:
        return "小学低段"
    if "三年级" in text or "四年级" in text or "中年级" in text or "中段" in text:
        return "小学中段"
    if "五年级" in text or "六年级" in text or "高年级" in text:
        return "小学高段"
    return ""


def _classroom_stage(text: str, options: dict[str, Any]) -> str:
    if options.get("classroom_stage"):
        return str(options["classroom_stage"])
    for stage in ("导入", "学唱前准备", "学唱", "节奏练习", "律动", "欣赏", "复听", "巩固", "创编", "展示", "评价"):
        if stage in text:
            return stage
    return "练习"


def _activity_shape(text: str, options: dict[str, Any]) -> str:
    if options.get("activity_shape"):
        return str(options["activity_shape"])
    if "教具" in text or "卡" in text or "节奏条" in text:
        return "teaching_aid"
    if "乐器" in text or "音条琴" in text or "打击乐" in text:
        return "virtual_instrument"
    if "小组" in text:
        return "group_activity"
    if "游戏" in text or "闯关" in text or "守卫" in text or "侦探" in text:
        return "game"
    if "练习" in text:
        return "practice"
    return ""


def _lesson_activity_shape(music_focus: str, source_summary: str) -> str:
    text = f"{music_focus} {source_summary}"
    if "游戏" in text or "闯关" in text:
        return "game"
    if "演奏" in text or "乐器" in text or "音条琴" in text or "打击乐器" in text:
        return "virtual_instrument"
    if "读" in text or "拍" in text or "歌词" in text or "节奏" in text:
        return "teaching_aid"
    return "practice"


def _music_focus(text: str, options: dict[str, Any]) -> str:
    if options.get("music_focus"):
        return str(options["music_focus"])
    if "歌词节奏" in text or "节奏条" in text:
        return "歌词节奏"
    if "二拍" in text or "三拍" in text or "强拍" in text or "弱拍" in text or "节拍" in text:
        return "二拍子强弱" if "二拍" in text else "强弱拍"
    if "节奏" in text or "拍读" in text:
        return "节奏"
    if "音高" in text or "唱名" in text or any(token in text.lower() for token in ("do", "re", "mi", "sol")):
        return "音高"
    if "音色" in text or "乐器" in text:
        return "音色"
    if "曲式" in text or "ABA" in text.upper():
        return "曲式"
    if "律动" in text:
        return "律动"
    return ""


def _student_behaviors(text: str, music_focus: str) -> list[str]:
    result: list[str] = []
    for zh, code in (("听", "listen"), ("读", "read"), ("拍", "tap"), ("唱", "sing"), ("奏", "play"), ("动", "move"), ("创", "create"), ("评", "assess")):
        if zh in text and code not in result:
            result.append(code)
    if not result:
        if "音色" in music_focus or "音高" in music_focus:
            result.append("listen")
        if "节奏" in music_focus or "强弱" in music_focus:
            result.extend(["listen", "tap"])
    return result


def _lesson_student_behaviors(evidence: dict[str, Any], source_summary: str) -> list[str]:
    raw = evidence.get("student_behavior") or evidence.get("student_music_behaviors") or []
    if isinstance(raw, str):
        raw = [raw]
    mapped = []
    for item in raw if isinstance(raw, list) else []:
        text_item = str(item or "").strip()
        mapped.append({"听": "listen", "读": "read", "拍": "tap", "唱": "sing", "奏": "play", "动": "move", "创": "create", "评": "assess"}.get(text_item, text_item))
    normalized = [item for item in mapped if item]
    if normalized:
        return list(dict.fromkeys(normalized))
    text = source_summary + " " + " ".join(str(item) for item in raw if isinstance(raw, list))
    return _student_behaviors(text, str(evidence.get("music_element") or ""))


def _toolkit_ref(activity_shape: str, music_focus: str, text: str) -> str:
    if "歌词节奏" in music_focus or "拍读" in text:
        return "lyrics_rhythm_practice"
    if "强弱" in music_focus or "节拍" in music_focus:
        return "meter_body_movement"
    if "音高" in music_focus or "唱名" in music_focus:
        return "solfege_sorting"
    if "音色" in music_focus:
        return "instrument_timbre_match"
    if "曲式" in music_focus:
        return "form_ordering"
    if activity_shape == "group_activity":
        return "group_relay_performance"
    if activity_shape == "virtual_instrument":
        return "xylophone_creation"
    return "rhythm_warmup"


def _runtime_ref(text: str, options: dict[str, Any]) -> str:
    if options.get("runtime_ref"):
        return str(options["runtime_ref"])
    if "投屏" in text:
        return "teacher_projection"
    if "小组" in text:
        return "group_shared_tablet"
    if "平板" in text:
        return "student_tablet"
    if "低设备" in text or "离线" in text:
        return "low_device"
    return "teacher_projection" if text else ""


def _classroom_minutes(text: str, options: dict[str, Any]) -> int:
    if options.get("classroom_minutes"):
        return int(options["classroom_minutes"])
    match = re.search(r"([0-9一二三四五六七八九十]+)\s*分钟", text)
    if match:
        return _parse_int(match.group(1)) or 5
    return 5 if text else 0


def _difficulty_profile(text: str, options: dict[str, Any]) -> str:
    if options.get("difficulty_profile_ref"):
        return str(options["difficulty_profile_ref"])
    if "简单" in text or "低年级" in text:
        return "easy"
    if "难" in text or "挑战" in text:
        return "hard"
    return "standard"


def _material_refs(text: str, default_material: dict[str, Any]) -> list[str]:
    refs: list[str] = []
    if "第一句" in text or "第一乐句" in text:
        refs.append("第一句" if "第一句" in text else "第一乐句")
    refs.append(default_material["material_id"])
    return refs


def _direct_assumptions(text: str, default_material: dict[str, Any]) -> list[str]:
    assumptions = ["未上传教案"]
    if not any(token in text for token in ("第一句", "第一乐句", "歌曲", "音频", "节奏条")):
        assumptions.append(f"使用{default_material['teacher_visible_label']}")
    return assumptions


def _activity_goal(text: str, music_focus: str, activity_shape: str) -> str:
    shape_label = {
        "game": "游戏",
        "teaching_aid": "虚拟教具",
        "virtual_instrument": "虚拟乐器",
        "practice": "练习",
        "group_activity": "小组活动",
    }.get(activity_shape, "活动")
    return f"{music_focus}{shape_label}" if music_focus else text[:40]


def _has_material_or_default(text: str) -> bool:
    return bool(_music_focus(text, {}) or any(token in text for token in ("歌曲", "音频", "节奏", "音高", "音色", "曲式")))


def _parse_int(value: str) -> int | None:
    if value.isdigit():
        return int(value)
    mapping = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}
    return mapping.get(value)
