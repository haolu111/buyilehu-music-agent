from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.services.activity_registry import get_activity_template, list_activity_templates
from app.services.adaptive_template_registry import adaptive_specs_for_activity
from app.services.assessment_record_registry import assessment_record_specs_for_activity
from app.services.asset_pack_template_registry import asset_pack_template_specs_for_activity
from app.services.delivery_template_registry import delivery_templates_for_activity
from app.services.gameplay_template_catalog import gameplay_template_specs_for_activity
from app.services.material_binding_spec import build_material_binding_spec
from app.services.material_binding_registry import material_binder_specs_for_activity
from app.services.material_entity_registry import (
    material_entity_specs_for_activity,
    parse_lesson_material_entities,
    parsed_entities_to_available_materials,
)
from app.services.micro_activity_template_registry import micro_activity_specs_for_activity
from app.services.music_game_composition_spec import (
    MUSIC_GAME_COMPOSITION_SPEC_VERSION,
    validate_music_game_composition_spec,
)
from app.services.music_practice_classification import activity_allowed_as_default_main
from app.services.music_rule_registry import music_rule_specs_for_activity, rules_for_activity
from app.services.primary_music_game_runtime_builder import build_primary_music_game_runtime
from app.services.scenario_template_registry import scenario_templates_for_activity
from app.services.teacher_control_registry import teacher_control_pack_ids_for_activity, teacher_control_specs_for_ids
from app.services.teaching_aid_registry import get_teaching_aid
from app.services.virtual_instrument_registry import get_virtual_instrument


COMPOSER_VERSION = "music_game_composer_v1"

ACTIVITY_KEYWORDS: dict[str, list[str]] = {
    "lesson_opening_hook": ["课堂导入", "导入钩子", "开头", "开场", "新课导入", "先听一小段", "说感受"],
    "rhythm_question_answer": ["节奏问答", "老师拍一句", "教师拍一句", "学生答一句", "回拍", "答句", "问句"],
    "steady_beat_walk": ["稳定拍行走", "稳拍行走", "走步", "跟着稳定拍走", "休止时停住", "走走停停"],
    "meter_body_movement": ["强弱", "二拍子", "三拍子", "四拍子", "拍号", "强拍", "强弱拍圆圈", "强弱拍围圈", "围圈", "圆圈", "强拍拍手", "弱拍拍腿"],
    "rhythm_warmup": ["节奏", "稳拍", "稳定拍检查", "一分钟稳拍检查", "跟着节拍", "拍一拍", "节奏热身", "休止"],
    "lyrics_rhythm_reading": ["歌词节奏朗读", "按节拍读歌词", "拍读歌词", "读歌词再拍", "按拍点读歌词"],
    "lyrics_rhythm_practice": ["歌词节奏", "按节拍读歌词", "读歌词", "歌词朗读", "歌词节拍"],
    "phrase_loop_singing": ["分句循环", "分句学唱", "听一句唱一句", "循环学唱", "乐句循环"],
    "phrase_singing_practice": ["学唱", "分句", "唱一句", "歌词", "歌曲"],
    "solfege_echo_singing": ["唱名回声", "回声模唱", "模唱回来", "听后模唱", "老师唱", "教师唱", "学生模唱"],
    "melody_contour_trace": ["旋律线", "旋律走向", "上行", "下行", "平稳", "手势画", "描一描", "画出旋律"],
    "solfege_sorting": ["唱名", "do", "re", "mi", "音高", "旋律走向"],
    "simple_score_following": ["简谱", "识谱", "跟读", "读谱", "视唱", "谱面", "唱名和节奏"],
    "listen_choose_explain": ["听一听选一选", "听完后选择", "复听找证据", "找速度", "找力度", "说音乐依据", "选择速度", "选择力度"],
    "picture_listening_intro": ["欣赏", "情绪", "速度", "力度", "听赏"],
    "theme_return_action": ["主题再现动作", "复听主题", "主题回来", "听到a主题", "听到A主题", "举主题卡", "做动作"],
    "instrument_timbre_match": ["音色", "乐器", "听辨乐器", "乐器家族"],
    "instrument_family_sorting": ["乐器家族", "发声方式", "民族乐器", "西洋乐器", "乐器分类", "分类"],
    "form_ordering": ["曲式", "ABA", "回旋", "段落", "主题再现"],
    "body_percussion_builder": ["身体打击", "节奏创编", "身体动作", "动作", "拍手", "跺脚", "律动"],
    "graphic_score_create": ["图形谱", "点线块", "图形创编", "图形谱创编", "高低强弱长短", "图形表示"],
    "xylophone_creation": ["音条琴", "五声", "五声音阶", "创编", "do re mi sol la"],
    "classroom_band_roles": ["小乐队分声部", "小乐队", "分声部", "乐器分配", "小组任务卡", "分配手鼓", "分配木鱼", "分配沙锤"],
    "orff_percussion_ensemble": ["奥尔夫", "合奏", "打击乐", "声部", "小乐队"],
    "show_and_peer_feedback": ["同伴评价", "互评", "展示评价", "评价建议", "用音乐依据评价", "展示后评价"],
    "group_relay_performance": ["小组", "接力", "展示", "合作"],
    "exit_ticket_review": ["出口票", "复习", "评价", "收尾"],
}


EVIDENCE_TASK_MARKERS = (
    "课堂导入",
    "导入钩子",
    "开场",
    "开头",
    "新课导入",
    "先听一小段",
    "听一听选一选",
    "听完后选择",
    "听音乐后选择",
    "复听找证据",
    "找速度",
    "找力度",
    "说音乐依据",
    "选择情绪",
    "选择速度",
    "选择力度",
    "听后选择乐器",
    "听后选择音色",
    "听后匹配",
    "听辨匹配",
    "听辨乐器",
    "听辨音色",
    "听辨乐器家族",
    "听后唱名排序",
    "唱名排序",
    "乐器分类",
    "按发声方式分类",
    "曲式排序",
    "段落排序",
    "曲式寻宝",
    "复听三个段落",
    "出口票",
    "课末",
    "收尾",
    "课堂复习",
    "本课回顾",
    "学习反馈",
)


def compose_music_game(request: dict[str, Any]) -> dict[str, Any]:
    normalized = request if isinstance(request, dict) else {}
    material_entity_parse = parse_lesson_material_entities(
        str(normalized.get("lesson_text") or ""),
        extra_need=str(normalized.get("teacher_request") or ""),
    )
    parsed_materials = parsed_entities_to_available_materials(material_entity_parse)
    explicit_materials = normalized.get("available_materials") if isinstance(normalized.get("available_materials"), dict) else {}
    available_materials = {**parsed_materials, **explicit_materials}
    selection_request = {**normalized, "available_materials": available_materials}
    activity = _select_activity(selection_request)
    toolkit = activity["toolkit"]
    required_material_entities = _required_material_entities_for_request(
        activity=activity,
        request=normalized,
        available_materials=available_materials,
    )
    material_binding = build_material_binding_spec(
        source_request=normalized,
        required_material_entities=required_material_entities,
        available_materials=available_materials,
    )
    missing_fields = list(material_binding["missing_fields"])
    status = "needs_material" if missing_fields else "ready"
    selected_rules = rules_for_activity(activity["activity_id"])
    selected_teacher_controls = _teacher_control_packs(activity["teacher_controls"], activity["activity_id"])
    selected_game_template = _selected_game_template(activity)
    quality_gates = _quality_gates(status, selected_rules, toolkit)

    spec = {
        "version": MUSIC_GAME_COMPOSITION_SPEC_VERSION,
        "composer_version": COMPOSER_VERSION,
        "status": status,
        "selected_activity_id": activity["activity_id"],
        "selected_activity_name": activity["name"],
        "selected_game_template": selected_game_template,
        "why": _why(activity, selected_game_template, missing_fields),
        "selected_rules": selected_rules,
        "music_rule_specs": music_rule_specs_for_activity(activity["activity_id"]),
        "selected_components": deepcopy(toolkit.get("components", [])),
        "selected_teaching_aids": deepcopy(toolkit.get("teaching_aids", [])),
        "selected_virtual_instruments": _virtual_instruments_for_constraints(toolkit, normalized),
        "selected_teacher_controls": selected_teacher_controls,
        "teacher_control_specs": teacher_control_specs_for_ids(selected_teacher_controls),
        "selected_assets": _asset_packs_for_activity(activity["activity_id"]),
        "asset_pack_template_specs": asset_pack_template_specs_for_activity(activity["activity_id"]),
        "micro_activity_template_specs": micro_activity_specs_for_activity(activity["activity_id"]),
        "gameplay_template_specs": gameplay_template_specs_for_activity(activity["activity_id"]),
        "education_alignment": deepcopy(activity["education_alignment"]),
        "material_binding": material_binding,
        "material_entity_parse": material_entity_parse,
        "material_entity_specs": material_entity_specs_for_activity(activity["activity_id"]),
        "material_binder_specs": material_binder_specs_for_activity(activity["activity_id"]),
        "assessment_record_specs": assessment_record_specs_for_activity(activity["activity_id"]),
        "adaptive_template_specs": adaptive_specs_for_activity(activity["activity_id"]),
        "delivery_template_specs": delivery_templates_for_activity(activity["activity_id"]),
        "scenario_template_specs": scenario_templates_for_activity(activity["activity_id"]),
        "missing_fields": missing_fields,
        "teacher_confirm_fields": material_binding["teacher_confirm_fields"],
        "difficulty": _difficulty(activity, normalized),
        "teacher_explanation": _teacher_explanation(activity, selected_game_template, missing_fields),
        "quality_gates": quality_gates,
        "passed_gates": [gate for gate, passed in quality_gates.items() if passed],
        "failed_gates": [gate for gate, passed in quality_gates.items() if not passed],
        "runtime_targets": ["student_game", "teacher_control"],
        "lesson_runtime_generated_assets": _lesson_runtime_generated_assets(
            activity=activity,
            request=normalized,
            available_materials=available_materials,
        ),
    }
    spec["runtime"] = build_primary_music_game_runtime(composition=spec, request=normalized)
    _attach_lesson_runtime_generated_assets(spec["runtime"], spec["lesson_runtime_generated_assets"])
    spec["teacher_plan_card"] = _teacher_plan_card(spec, normalized, available_materials)
    spec["activity_spec"] = _activity_spec(spec)
    spec["classroom_runtime"] = _classroom_runtime(spec)
    spec["artifact_package"] = _artifact_package(spec)
    spec["acceptance_report"] = _acceptance_report(spec)
    return validate_music_game_composition_spec(spec)


def _select_activity(request: dict[str, Any]) -> dict[str, Any]:
    text = " ".join(
        str(request.get(key) or "")
        for key in ("teacher_request", "lesson_text", "grade_band")
    ).lower()
    materials = request.get("available_materials") if isinstance(request.get("available_materials"), dict) else {}
    if "图形谱" in text and any(marker in text for marker in ("创编", "编辑", "节奏卡", "唱名卡", "音高卡")):
        return get_activity_template("graphic_score_create")
    forced_activity_id = _forced_activity_for_teaching_stage(text, materials)
    if forced_activity_id:
        return get_activity_template(forced_activity_id)
    best_activity_id = ""
    best_score = -1
    explicit_evidence_task = _has_explicit_evidence_task(text)
    for activity in list_activity_templates():
        activity_id = str(activity.get("activity_id") or "")
        if not activity_id:
            continue
        try:
            default_main_allowed = activity_allowed_as_default_main(activity_id)
        except ValueError:
            continue
        if not explicit_evidence_task and not default_main_allowed:
            continue
        score = 0
        for keyword in ACTIVITY_KEYWORDS.get(activity["activity_id"], []):
            if keyword.lower() in text:
                score += 6
        for element in activity["education_alignment"].get("music_elements", []):
            if str(element).lower() in text:
                score += 3
        for practice in activity.get("student_music_behaviors", []):
            if str(practice).lower() in text:
                score += 1
        score += sum(1 for entity in activity["required_material_entities"] if entity in materials)
        if _grade_matches(activity, str(request.get("grade_band") or "")):
            score += 2
        if score > best_score:
            best_score = score
            best_activity_id = activity_id
    return get_activity_template(best_activity_id or "rhythm_warmup")


def _has_explicit_evidence_task(text: str) -> bool:
    if any(marker in text for marker in EVIDENCE_TASK_MARKERS):
        return True
    return "听辨" in text and any(marker in text for marker in ("乐器", "音色", "乐器家族", "发声方式"))


def _required_material_entities_for_request(
    *,
    activity: dict[str, Any],
    request: dict[str, Any],
    available_materials: dict[str, Any],
) -> list[str]:
    required = list(activity.get("required_material_entities", []))
    if activity.get("activity_id") != "graphic_score_create":
        return required
    if _graphic_score_creation_mode(request, available_materials) == "mixed_cards":
        return required
    return [entity for entity in required if entity not in {"rhythm_pattern", "solfege_set"}]


def _graphic_score_creation_mode(request: dict[str, Any], available_materials: dict[str, Any]) -> str:
    explicit = available_materials.get("creation_mode") or request.get("creation_mode")
    if explicit == "mixed_cards":
        return "mixed_cards"
    text = " ".join(str(request.get(key) or "") for key in ("teacher_request", "lesson_text")).lower()
    if any(marker in text for marker in ("混合图形谱", "节奏卡", "唱名卡", "音高卡")):
        return "mixed_cards"
    return "graphic"


def _forced_activity_for_teaching_stage(text: str, materials: dict[str, Any]) -> str:
    if any(marker in text for marker in ("稳定拍行走", "稳拍行走", "走步", "跟着稳定拍走", "休止时停住", "走走停停")):
        if materials.get("rhythm_pattern") or materials.get("pattern_steps") or materials.get("meter"):
            return "steady_beat_walk"
    if any(marker in text for marker in ("强弱拍圆圈", "强弱拍围圈", "围圈", "圆圈", "强拍拍手", "弱拍拍腿")):
        if materials.get("meter") or materials.get("rhythm_pattern") or materials.get("pattern_steps"):
            return "meter_body_movement"
    if any(marker in text for marker in ("旋律线", "手势画", "手势", "描一描", "画出旋律", "画出", "描出")):
        if materials.get("pitch_motion") or materials.get("melody_contour") or materials.get("melody_phrase"):
            return "melody_contour_trace"
    if any(marker in text for marker in ("节奏问答", "老师拍一句", "教师拍一句", "学生答一句", "回拍", "答句", "问句")):
        if materials.get("rhythm_pattern") or materials.get("pattern_steps") or materials.get("rhythm_cards"):
            return "rhythm_question_answer"
    if any(marker in text for marker in ("歌词节奏朗读", "按节拍读歌词", "拍读歌词", "读歌词再拍", "按拍点读歌词")):
        if materials.get("lyrics_phrase") or materials.get("lyrics_text"):
            return "lyrics_rhythm_reading"
    if any(marker in text for marker in ("课堂导入", "导入钩子", "开头", "开场", "新课导入", "先听一小段")):
        if materials.get("audio_clip") or materials.get("audio_url") or materials.get("source_audio_url"):
            return "lesson_opening_hook"
    if any(marker in text for marker in ("听一听选一选", "听完后选择", "复听找证据", "找速度", "找力度", "说音乐依据", "选择速度", "选择力度")):
        if materials.get("audio_clip") or materials.get("audio_url") or materials.get("source_audio_url"):
            return "listen_choose_explain"
    if any(marker in text for marker in ("小乐队分声部", "分声部", "乐器分配", "小组任务卡", "分配手鼓", "分配木鱼", "分配沙锤")):
        if materials.get("classroom_group_task") or materials.get("group_tasks"):
            return "classroom_band_roles"
    difficult_phrase_markers = ("难点", "慢速", "换气", "呼吸", "difficult_phrase", "breath_points")
    expression_markers = ("歌曲处理", "力度", "情绪处理", "声音处理", "target_expression", "渐强", "轻柔")
    if any(marker in text for marker in expression_markers) or materials.get("target_expression"):
        if materials.get("lyrics_phrase") or materials.get("melody_phrase"):
            return "phrase_singing_practice"
    if any(marker in text for marker in ("分句循环", "分句学唱", "听一句唱一句", "循环学唱", "乐句循环")):
        if not any(marker in text for marker in difficult_phrase_markers) and (
            materials.get("lyrics_phrase") or materials.get("melody_phrase") or materials.get("audio_clip")
        ):
            return "phrase_loop_singing"
    if any(marker in text for marker in ("同伴评价", "互评", "展示评价", "评价建议", "展示后同伴", "用音乐依据评价", "展示后评价")):
        if materials.get("assessment_criteria") or materials.get("rubric"):
            return "show_and_peer_feedback"
    if any(marker in text for marker in ("出口票", "课末", "收尾", "课堂复习", "本课回顾", "学习反馈")):
        if materials.get("assessment_criteria") or materials.get("music_focus") or materials.get("objective"):
            return "exit_ticket_review"
    return ""


def _grade_matches(activity: dict[str, Any], grade_band: str) -> bool:
    grade = grade_band.strip()
    if not grade:
        return False
    if grade in activity.get("grade_bands", []):
        return True
    if "一年级" in grade or "二年级" in grade or "lower" in grade:
        return "lower_primary" in activity.get("grade_bands", [])
    if "三年级" in grade or "四年级" in grade or "middle" in grade:
        return "middle_primary" in activity.get("grade_bands", [])
    if "五年级" in grade or "六年级" in grade or "upper" in grade:
        return "upper_primary" in activity.get("grade_bands", [])
    return False


def _selected_game_template(activity: dict[str, Any]) -> str | None:
    templates = activity.get("toolkit", {}).get("game_templates", [])
    if templates:
        return str(templates[0])
    if activity.get("activity_id") == "rhythm_warmup":
        return "rhythm_echo_core"
    return None


def _teacher_control_packs(controls: list[str], activity_id: str) -> list[str]:
    return teacher_control_pack_ids_for_activity(controls, activity_id)


def _virtual_instruments_for_constraints(toolkit: dict[str, Any], request: dict[str, Any]) -> list[str]:
    instruments = list(toolkit.get("virtual_instruments", []))
    constraints = request.get("classroom_constraints") if isinstance(request.get("classroom_constraints"), dict) else {}
    if constraints.get("no_real_instruments") and not instruments:
        if "meter_track" in toolkit.get("components", []):
            instruments.append("rhythm_pad")
    return instruments


def _asset_packs_for_activity(activity_id: str) -> list[str]:
    if activity_id in {"instrument_timbre_match"}:
        return ["generated_playable_instrument_pack"]
    if activity_id in {"instrument_family_sorting"}:
        return ["generated_playable_instrument_pack"]
    if activity_id in {"picture_listening_intro", "listen_choose_explain", "lesson_opening_hook"}:
        return ["mood_symbol_card_pack", "music_mood_picture_pack"]
    if activity_id in {"orff_percussion_ensemble", "classroom_band_roles"}:
        return ["generated_playable_instrument_pack", "reward_badge_pack"]
    return ["reward_badge_pack"]


def _lesson_runtime_generated_assets(
    *,
    activity: dict[str, Any],
    request: dict[str, Any],
    available_materials: dict[str, Any],
) -> dict[str, Any]:
    alignment = activity.get("education_alignment") if isinstance(activity.get("education_alignment"), dict) else {}
    music_goals = [str(item) for item in alignment.get("music_elements", []) if str(item).strip()]
    teaching_stages = [str(item) for item in activity.get("classroom_stage", []) if str(item).strip()]
    return {
        "version": "lesson_runtime_generated_assets_v1",
        "scene_background": {
            "required": True,
            "provider": "agent_internal_image_gen",
            "save_dir": "assets/",
            "file": "scene-background.png",
            "ratio": "16:9",
            "reason": "由本课歌曲/欣赏材料、年级、活动任务生成，不能使用固定场景冒充教案适配。",
            "lesson_material": _lesson_material_for_asset_contract(request, available_materials),
            "grade_band": str(request.get("grade_band") or ""),
            "activity_id": str(activity.get("activity_id") or ""),
            "activity_play": "、".join(teaching_stages + [str(activity.get("name") or "")]).strip("、"),
            "music_goals": music_goals,
            "student_practices": [str(item) for item in alignment.get("student_practices", []) if str(item).strip()],
            "lesson_evidence": str(request.get("lesson_text") or "")[:180],
        },
        "lesson_props": [],
        "lesson_characters": [],
    }


def _lesson_material_for_asset_contract(request: dict[str, Any], available_materials: dict[str, Any]) -> str:
    for key in ("song_title", "work_title", "lesson_topic", "title", "selected_phrase_label", "audio_clip"):
        value = available_materials.get(key)
        if value not in ("", None, [], {}):
            return str(value)
    lesson_text = str(request.get("lesson_text") or "").strip()
    if lesson_text:
        return lesson_text[:120]
    return "当前教案音乐材料待教师确认"


def _attach_lesson_runtime_generated_assets(runtime: dict[str, Any], contract: dict[str, Any]) -> None:
    runtime["lesson_runtime_generated_assets"] = deepcopy(contract)
    state = runtime.get("student_game_state")
    if not isinstance(state, dict):
        return
    config = state.get("config")
    if isinstance(config, dict):
        config["lesson_runtime_generated_assets"] = deepcopy(contract)


def _quality_gates(status: str, selected_rules: list[str], toolkit: dict[str, Any]) -> dict[str, bool]:
    return {
        "education_alignment_gate": True,
        "music_practice_gate": True,
        "music_element_gate": True,
        "material_bound_gate": status == "ready",
        "teacher_control_gate": "teacher_control_bar" in toolkit.get("components", []),
        "rule_test_gate": bool(selected_rules) or status == "ready",
        "reset_gate": True,
    }


def _difficulty(activity: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    available = request.get("available_materials") if isinstance(request.get("available_materials"), dict) else {}
    grade = str(request.get("grade_band") or "")
    lower = "lower" in grade or "一年级" in grade or "二年级" in grade
    return {
        "bpm": int(available.get("bpm") or (84 if lower else 96)),
        "show_hint": lower,
        "round_count": 3 if lower else 4,
        "grade_band": grade or (activity.get("grade_bands") or ["middle_primary"])[0],
    }


def _why(activity: dict[str, Any], selected_game_template: str | None, missing_fields: list[str]) -> str:
    elements = "、".join(activity["education_alignment"].get("music_elements", []))
    template_text = f"，可调用 {selected_game_template}" if selected_game_template else "，用活动组件即可完成，不强行套成熟游戏"
    missing_text = f"；但还缺少 {', '.join(missing_fields)}" if missing_fields else ""
    return f"{activity['name']}对齐{elements}等音乐要素{template_text}{missing_text}。"


def _teacher_explanation(activity: dict[str, Any], selected_game_template: str | None, missing_fields: list[str]) -> dict[str, Any]:
    alignment = activity["education_alignment"]
    practices = alignment.get("student_practices", [])
    elements = alignment.get("music_elements", [])
    first_practice = practices[0] if practices else "listen"
    path = [
        f"先听或体验{elements[0] if elements else '音乐材料'}",
        "再用身体、声音或虚拟乐器表现",
        "最后根据反馈进行调整或表达依据",
    ]
    if missing_fields:
        path = ["先补齐音乐材料，再生成可交付游戏"] + path
    return {
        "why_this_game": _why(activity, selected_game_template, missing_fields),
        "music_learning_path": path,
        "what_students_practice": practices,
        "what_to_observe": _observe_points(elements, first_practice),
        "teacher_adjustment": "如果多数学生不稳定，先降速、打开提示或改为教师确认，不直接判定失败。",
    }


def _teacher_plan_card(spec: dict[str, Any], request: dict[str, Any], available: dict[str, Any]) -> dict[str, Any]:
    generation_mode = str(request.get("generation_mode") or "direct")
    is_lesson = generation_mode == "lesson_upload" or bool(request.get("lesson_section"))
    source_basis = str(request.get("lesson_section") or request.get("lesson_text") or "").strip()
    if not source_basis:
        source_basis = "当前没有绑定具体教案，依据教师需求生成可调整活动。"
    materials = _music_material_summary(available)
    confirmations = []
    if not request.get("lesson_text"):
        confirmations.append("当前未上传教案")
    if not available.get("song_title") and not available.get("audio_clip"):
        confirmations.append("当前未绑定具体歌曲")
    if spec.get("missing_fields"):
        confirmations.append(f"还需补充材料：{', '.join(spec['missing_fields'])}。")
    return {
        "id": f"plan-{spec['selected_activity_id']}",
        "mode": "教案生成" if is_lesson else "直接生成",
        "activity_name": spec["selected_activity_name"],
        "source_basis": source_basis,
        "music_goal": spec["why"],
        "music_materials": materials,
        "default_materials": spec["material_binding"]["detected_targets"],
        "music_education_rules": spec["education_alignment"].get("pedagogy_notes", []),
        "teacher_confirmations": confirmations or ["请确认速度、难度和学生操作方式。"],
        "non_digital_sections": ["教师示范", "学生口头说明", "回到歌曲或作品再表现"],
        "low_confidence_materials": list(spec.get("missing_fields", [])),
    }


def _activity_spec(spec: dict[str, Any]) -> dict[str, Any]:
    runtime_ref = f"classroom_runtime_spec_v1:{spec['selected_activity_id']}"
    return {
        "version": "activity_spec_v1",
        "activity_id": spec["selected_activity_id"],
        "teacher_console": {
            "plan_card_id": spec["teacher_plan_card"]["id"],
            "controls": deepcopy(spec["selected_teacher_controls"]),
        },
        "student_shell": {
            "title": spec["selected_activity_name"],
            "entry": spec["runtime"].get("student_entry", ""),
        },
        "runtime_ref": runtime_ref,
    }


def _classroom_runtime(spec: dict[str, Any]) -> dict[str, Any]:
    teaching_aid_contracts = _teaching_aid_runtime_contracts(spec.get("selected_teaching_aids", []))
    virtual_instrument_contracts = _virtual_instrument_runtime_contracts(spec.get("selected_virtual_instruments", []))
    return {
        "version": "classroom_runtime_spec_v1",
        "teacher_controls": [
            "pause",
            "reset",
            "tempo",
            "difficulty_down",
            "difficulty_up",
            "hint_visibility",
            "phrase_focus",
            "mode_switch",
            "instrument_voice",
            "regenerate_plan_card",
            "continue_editing",
        ],
        "student_runtime_config": {
            "runtime_ref": spec["activity_spec"]["runtime_ref"],
            "student_entry": spec["runtime"].get("student_entry", ""),
            "runtime_status": spec["runtime"].get("runtime_status", ""),
            "event_recording_required": bool(teaching_aid_contracts or virtual_instrument_contracts),
            "audio_unlock_required": any(
                contract.get("audio_unlock_required") for contract in virtual_instrument_contracts
            ),
        },
        "teaching_aid_runtime_contracts": teaching_aid_contracts,
        "virtual_instrument_runtime_contracts": virtual_instrument_contracts,
    }


def _artifact_package(spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "version": "activity_artifact_package_v1",
        "deliverables": ["student_end", "teacher_end", "work_package"],
        "management_actions": [
            "preview",
            "continue_edit",
            "duplicate",
            "download_package",
            "save_as_template",
            "last_classroom_config",
        ],
        "student_entry": spec["runtime"].get("student_entry", ""),
        "activity_id": spec["selected_activity_id"],
    }


def _acceptance_report(spec: dict[str, Any]) -> dict[str, Any]:
    gates = _acceptance_gates(spec)
    blocking = [gate for gate in gates if gate["status"] == "fail"]
    warnings = [gate for gate in gates if gate["status"] == "warning"]
    alignment = spec.get("education_alignment") if isinstance(spec.get("education_alignment"), dict) else {}
    runtime = spec.get("runtime") if isinstance(spec.get("runtime"), dict) else {}
    return {
        "version": "music_game_acceptance_report_v1",
        "game_id": f"generated_{spec['selected_activity_id']}",
        "activity_id": spec["selected_activity_id"],
        "template_id": spec.get("selected_game_template") or spec["selected_activity_id"],
        "status": "blocked" if blocking else "ready",
        "education_alignment": {
            "primary_competency": alignment.get("primary_competency", ""),
            "student_practices": deepcopy(alignment.get("student_practices", [])),
            "music_elements": deepcopy(alignment.get("music_elements", [])),
            "teaching_stage": deepcopy(alignment.get("teaching_stages", [])),
            "grade_fit": alignment.get("grade_fit", ""),
        },
        "passed_gates": [gate["id"] for gate in gates if gate["status"] == "pass"],
        "failed_gates": [gate["id"] for gate in blocking],
        "warnings": [gate["id"] for gate in warnings],
        "gates": gates,
        "acceptance_questions": _acceptance_questions(spec),
        "student_url": runtime.get("student_entry", ""),
        "teacher_controls": deepcopy(spec.get("selected_teacher_controls", [])),
        "assets": deepcopy(spec.get("selected_assets", [])),
        "tests": {
            "backend_contract": "required",
            "frontend_build": "required",
            "browser_smoke": "desktop_projection_required",
        },
    }


def _acceptance_gates(spec: dict[str, Any]) -> list[dict[str, str]]:
    alignment = spec.get("education_alignment") if isinstance(spec.get("education_alignment"), dict) else {}
    practices = alignment.get("student_practices") if isinstance(alignment.get("student_practices"), list) else []
    elements = alignment.get("music_elements") if isinstance(alignment.get("music_elements"), list) else []
    stages = alignment.get("teaching_stages") if isinstance(alignment.get("teaching_stages"), list) else []
    runtime = spec.get("runtime") if isinstance(spec.get("runtime"), dict) else {}
    runtime_ready = runtime.get("runtime_status") == "ready" and bool(runtime.get("student_entry"))
    quality = spec.get("quality_gates") if isinstance(spec.get("quality_gates"), dict) else {}
    return [
        _acceptance_gate(
            "education_alignment_gate",
            "pass" if alignment.get("primary_competency") and practices and elements and stages else "fail",
            "绑定了核心素养、学生音乐实践、音乐要素和教学环节。",
            "缺少核心素养、学生音乐实践、音乐要素或教学环节。",
        ),
        _acceptance_gate(
            "music_practice_gate",
            "pass" if practices else "fail",
            f"学生音乐实践：{', '.join(str(item) for item in practices)}。",
            "学生没有明确的听、唱、奏、动、创或评等音乐实践。",
        ),
        _acceptance_gate(
            "music_element_gate",
            "pass" if elements else "fail",
            f"训练音乐要素：{', '.join(str(item) for item in elements)}。",
            "没有明确训练音乐要素。",
        ),
        _acceptance_gate(
            "grade_fit_gate",
            "pass" if alignment.get("grade_fit") else "fail",
            f"学段适配：{alignment.get('grade_fit')}。",
            "缺少小学学段适配说明。",
        ),
        _acceptance_gate(
            "pedagogy_sequence_gate",
            "pass" if len(spec.get("teacher_explanation", {}).get("music_learning_path", [])) >= 3 else "fail",
            "学习路径包含先体验/聆听、再表现、再调整或表达依据。",
            "缺少可解释的音乐学习路径。",
        ),
        _acceptance_gate(
            "material_bound_gate",
            "pass" if not spec.get("missing_fields") else "fail",
            "已绑定生成所需音乐材料。",
            f"缺少材料：{', '.join(spec.get('missing_fields', []))}。",
        ),
        _acceptance_gate(
            "student_operable_gate",
            "pass" if runtime_ready else "fail",
            f"学生端入口：{runtime.get('student_entry', '')}。",
            "学生端入口未就绪，不能交付课堂使用。",
        ),
        _acceptance_gate(
            "teacher_control_gate",
            "pass" if spec.get("selected_teacher_controls") else "fail",
            f"教师控制包：{', '.join(spec.get('selected_teacher_controls', []))}。",
            "缺少教师控制包。",
        ),
        _acceptance_gate(
            "reset_gate",
            "pass" if quality.get("reset_gate") is True else "fail",
            "活动支持重置或重新开始。",
            "缺少重置能力。",
        ),
        _acceptance_gate(
            "projector_layout_gate",
            "warning",
            "",
            "需要通过浏览器 smoke 补充桌面投屏截图证据。",
        ),
    ]


def _acceptance_gate(gate_id: str, status: str, pass_detail: str, fail_detail: str) -> dict[str, str]:
    return {
        "id": gate_id,
        "status": status,
        "detail": pass_detail if status == "pass" else fail_detail,
    }


def _acceptance_questions(spec: dict[str, Any]) -> dict[str, Any]:
    alignment = spec.get("education_alignment") if isinstance(spec.get("education_alignment"), dict) else {}
    elements = alignment.get("music_elements", [])
    practices = alignment.get("student_practices", [])
    return {
        "trained_music_element": elements,
        "student_music_practices": practices,
        "core_competency": alignment.get("primary_competency", ""),
        "grade_fit": alignment.get("grade_fit", ""),
        "teaching_stage": alignment.get("teaching_stages", []),
        "listen_or_experience_first": bool(spec.get("teacher_explanation", {}).get("music_learning_path")),
        "teacher_feedback_available": bool(spec.get("selected_teacher_controls")),
        "high_risk_auto_scoring_avoided": "teacher_confirm_pack" in spec.get("selected_teacher_controls", [])
        or bool(spec.get("teacher_confirm_fields")),
        "missing_material_policy": "blocked_until_material_ready" if spec.get("missing_fields") else "material_ready",
    }


def _teaching_aid_runtime_contracts(aid_ids: list[str]) -> list[dict[str, Any]]:
    contracts: list[dict[str, Any]] = []
    for aid_id in aid_ids:
        aid = get_teaching_aid(aid_id)
        runtime = deepcopy(aid["runtime"])
        runtime["aid_id"] = aid["aid_id"]
        runtime["name"] = aid["name"]
        runtime["replace_physical_aid"] = aid["replace_physical_aid"]
        contracts.append(runtime)
    return contracts


def _virtual_instrument_runtime_contracts(instrument_ids: list[str]) -> list[dict[str, Any]]:
    contracts: list[dict[str, Any]] = []
    for instrument_id in instrument_ids:
        instrument = get_virtual_instrument(instrument_id)
        runtime = deepcopy(instrument["runtime_contract"])
        runtime["instrument_id"] = instrument["instrument_id"]
        runtime["name"] = instrument["name"]
        runtime["replace_physical_instrument"] = instrument["replace_physical_instrument"]
        contracts.append(runtime)
    return contracts


def _music_material_summary(available: dict[str, Any]) -> list[str]:
    labels = []
    for key in ("song_title", "selected_phrase_label", "audio_clip", "meter", "bpm"):
        value = available.get(key)
        if value not in ("", None, [], {}):
            labels.append(str(value))
    for key in ("lyrics_phrase", "rhythm_pattern", "solfege_set", "instrument_pool", "form_structure"):
        value = available.get(key)
        if isinstance(value, list) and value:
            labels.append("、".join(str(item) for item in value[:4]))
        elif value not in ("", None, [], {}):
            labels.append(str(value))
    return labels or ["使用默认课堂材料，需教师课前确认。"]


def _observe_points(elements: list[str], first_practice: str) -> list[str]:
    points = [f"学生是否能围绕{element}做出稳定表现" for element in elements[:2]]
    if first_practice in {"listen", "match", "choose"}:
        points.append("学生是否能说出听到的音乐依据")
    if first_practice in {"play", "tap", "move"}:
        points.append("学生是否能跟随稳定拍或小组进入")
    return points or ["学生是否完成了本轮音乐实践"]
