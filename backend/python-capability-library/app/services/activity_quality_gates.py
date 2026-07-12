from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.services.asset_pack_file_validator import list_asset_pack_file_reports
from app.services.activity_registry import get_activity_template, list_activity_templates
from app.services.asset_pack_registry import list_asset_packs
from app.services.doubao_asset_pack_verifier import verify_doubao_asset_pack_outputs
from app.services.doubao_generation_queue import list_pending_doubao_generation_tasks
from app.services.component_library import get_component_spec
from app.services.game_template_registry import get_game_template, list_game_templates
from app.services.image2_generation_queue import list_pending_image2_generation_tasks
from app.services.instrument_audio_registry import list_instrument_audio_packs
from app.services.material_binding_registry import material_binder_specs_for_activity
from app.services.template_game_asset_registry import evaluate_template_game_asset_library
from app.services.toolkit_registry import build_toolkit_spec


ACTIVITY_QUALITY_REPORT_VERSION = "activity_quality_report_v1"
ACTIVITY_LIBRARY_QUALITY_REPORT_VERSION = "activity_library_quality_report_v1"


def evaluate_activity_quality(activity_or_id: str | dict[str, Any]) -> dict[str, Any]:
    activity = _activity_from_input(activity_or_id)
    toolkit = _toolkit_for_activity(activity)
    gates = [
        _music_education_alignment_gate(activity),
        _music_learning_path_gate(activity),
        _music_pedagogy_gate(activity, toolkit),
        _toolkit_components_registered_gate(activity, toolkit),
        _teaching_aids_callable_gate(activity, toolkit),
        _virtual_instruments_callable_gate(activity, toolkit),
        _teacher_control_gate(activity),
        _material_binding_gate(activity),
        _runtime_artifact_gate(activity),
    ]
    blocking_failures = [gate for gate in gates if gate["status"] == "fail"]
    return {
        "version": ACTIVITY_QUALITY_REPORT_VERSION,
        "activity_id": activity.get("activity_id", ""),
        "activity_name": activity.get("name", ""),
        "status": "fail" if blocking_failures else "pass",
        "gates": gates,
        "blocking_failures": blocking_failures,
    }


def evaluate_activity_library_quality() -> dict[str, Any]:
    reports = [evaluate_activity_quality(activity) for activity in list_activity_templates()]
    asset_pack_gates = _asset_pack_gates()
    blocking_failures = [
        {
            "activity_id": report["activity_id"],
            "gate": deepcopy(gate),
        }
        for report in reports
        for gate in report["blocking_failures"]
    ] + [{"activity_id": "asset_library", "gate": deepcopy(gate)} for gate in asset_pack_gates if gate["status"] == "fail"]
    return {
        "version": ACTIVITY_LIBRARY_QUALITY_REPORT_VERSION,
        "status": "fail" if blocking_failures else "pass",
        "activities": reports,
        "asset_pack_gates": asset_pack_gates,
        "pending_image2_generation_tasks": list_pending_image2_generation_tasks(),
        "pending_doubao_generation_tasks": list_pending_doubao_generation_tasks(),
        "doubao_asset_pack_verification": verify_doubao_asset_pack_outputs(),
        "blocking_failures": blocking_failures,
    }


def evaluate_activity_delivery_quality(delivery: dict[str, Any]) -> dict[str, Any]:
    payload = deepcopy(delivery) if isinstance(delivery, dict) else {}
    gates = [
        _source_mode_gate(payload),
        _grounding_gate(payload),
        _music_truth_gate(payload),
        _student_music_behavior_delivery_gate(payload),
        _teacher_control_delivery_gate(payload),
        _runtime_delivery_gate(payload),
        _degraded_delivery_gate(payload),
    ]
    blocking_failures = [gate for gate in gates if gate["status"] == "fail"]
    return {
        "version": "activity_delivery_quality_report_v1",
        "status": "fail" if blocking_failures else "pass",
        "delivery_kind": payload.get("delivery_kind", ""),
        "source_mode": payload.get("source_mode", ""),
        "gates": gates,
        "blocking_failures": blocking_failures,
    }


def evaluate_game_template_music_logic_quality(template_or_id: str | dict[str, Any]) -> dict[str, Any]:
    template = _game_template_from_input(template_or_id)
    gates = [
        _template_music_logic_gate(template),
        _template_student_music_behavior_gate(template),
        _template_runtime_quality_profile_gate(template),
    ]
    blocking_failures = [gate for gate in gates if gate["status"] == "fail"]
    return {
        "version": "game_template_music_logic_report_v1",
        "template_id": template.get("template_id", ""),
        "template_label": template.get("label", ""),
        "status": "fail" if blocking_failures else "pass",
        "gates": gates,
        "blocking_failures": blocking_failures,
    }


def evaluate_game_template_music_logic_library_quality() -> dict[str, Any]:
    reports = [evaluate_game_template_music_logic_quality(template) for template in list_game_templates()]
    blocking_failures = [
        {"template_id": report["template_id"], "gate": deepcopy(gate)}
        for report in reports
        for gate in report["blocking_failures"]
    ]
    return {
        "version": "game_template_music_logic_library_report_v1",
        "status": "fail" if blocking_failures else "pass",
        "template_count": len(reports),
        "templates": reports,
        "blocking_failures": blocking_failures,
    }


def evaluate_browser_acceptance_quality(browser_report: dict[str, Any]) -> dict[str, Any]:
    report = deepcopy(browser_report) if isinstance(browser_report, dict) else {}
    gates = [
        _browser_open_gate(report),
        _browser_viewport_gate(report),
        _browser_interaction_gate(report),
        _browser_canvas_gate(report),
        _browser_layout_gate(report),
        _browser_audio_gate(report),
    ]
    blocking_failures = [gate for gate in gates if gate["status"] == "fail"]
    return {
        "version": "browser_acceptance_quality_report_v1",
        "status": "fail" if blocking_failures else "pass",
        "mode": report.get("mode", ""),
        "screenshot": report.get("screenshot", ""),
        "gates": gates,
        "blocking_failures": blocking_failures,
    }


def _activity_from_input(activity_or_id: str | dict[str, Any]) -> dict[str, Any]:
    if isinstance(activity_or_id, dict):
        return deepcopy(activity_or_id)
    return get_activity_template(str(activity_or_id or ""))


def _game_template_from_input(template_or_id: str | dict[str, Any]) -> dict[str, Any]:
    if isinstance(template_or_id, dict):
        return deepcopy(template_or_id)
    template = get_game_template(str(template_or_id or ""))
    if not template:
        raise ValueError(f"unknown game template: {template_or_id}")
    return template


def _toolkit_for_activity(activity: dict[str, Any]) -> dict[str, Any]:
    activity_id = str(activity.get("activity_id") or "")
    try:
        if activity_id:
            toolkit = build_toolkit_spec(activity_id)
            if activity.get("toolkit") != toolkit.get("selected"):
                toolkit = deepcopy(toolkit)
                toolkit["selected"] = deepcopy(activity.get("toolkit", {}))
            return toolkit
    except ValueError:
        pass
    return {
        "version": "toolkit_spec_v1",
        "activity_id": activity_id,
        "selected": deepcopy(activity.get("toolkit", {})),
        "teaching_aid_specs": [],
        "virtual_instrument_specs": [],
    }


def _music_education_alignment_gate(activity: dict[str, Any]) -> dict[str, str]:
    alignment = activity.get("education_alignment") if isinstance(activity.get("education_alignment"), dict) else {}
    has_alignment = bool(
        alignment.get("primary_competency")
        and alignment.get("student_practices")
        and alignment.get("music_elements")
        and alignment.get("teaching_stages")
        and alignment.get("grade_fit")
        and alignment.get("pedagogy_notes")
    )
    return _gate(
        "music_education_alignment",
        "音乐教育校准",
        "pass" if has_alignment else "fail",
        "活动声明了核心素养、学生音乐实践、音乐要素、学段适配和教学提示。"
        if has_alignment
        else "缺少小学音乐教育校准字段。",
    )


def _music_learning_path_gate(activity: dict[str, Any]) -> dict[str, str]:
    alignment = activity.get("education_alignment") if isinstance(activity.get("education_alignment"), dict) else {}
    path = alignment.get("music_learning_path") if isinstance(alignment.get("music_learning_path"), dict) else {}
    required = ["experience", "performance", "understanding", "transfer_or_creation"]
    ok = all(str(path.get(key) or "").strip() for key in required)
    return _gate(
        "music_learning_path",
        "音乐学习路径",
        "pass" if ok else "fail",
        "活动遵循体验先行、表现跟进、理解生成、迁移或创造。"
        if ok
        else "缺少完整的音乐学习路径。",
    )


def _music_pedagogy_gate(activity: dict[str, Any], toolkit: dict[str, Any]) -> dict[str, str]:
    alignment = activity.get("education_alignment") if isinstance(activity.get("education_alignment"), dict) else {}
    elements = _string_set(alignment.get("music_elements")) or _string_set(activity.get("required_material_entities"))
    practices = _string_set(alignment.get("student_practices")) or _string_set(activity.get("student_music_behaviors"))
    materials = _string_set(activity.get("required_material_entities"))
    selected = toolkit.get("selected") if isinstance(toolkit.get("selected"), dict) else {}
    components = _string_set(selected.get("components"))
    aids = _string_set(selected.get("teaching_aids"))
    instruments = _string_set(selected.get("virtual_instruments"))
    templates = _string_set(selected.get("game_templates"))
    audio_evidence_components = {"compare_player", "audio_player", "song_audio_workbench"}
    form_evidence_components = {"form_card_timeline", "audio_player", "song_audio_workbench"}
    failures: list[str] = []

    if elements.intersection({"音色", "乐器", "乐器家族", "发声方式"}):
        if "listen" not in practices or not components.intersection(audio_evidence_components):
            failures.append("音色/乐器活动必须先听声音证据，不能套成节奏点击或看图猜。")
        if components.intersection({"rhythm_card_bank", "tap_feedback"}) and not components.intersection(audio_evidence_components):
            failures.append("音色目标不能只使用节奏卡、点击反馈等节奏组件。")

    if elements.intersection({"曲式", "重复", "对比"}):
        if "listen" not in practices or "audio_clip" not in materials or not components.intersection(form_evidence_components):
            failures.append("曲式活动必须绑定音频段落，并通过复听判断重复、对比或再现。")

    if elements.intersection({"唱名", "音高", "旋律", "五声音阶"}):
        if "listen" not in practices:
            failures.append("音高/唱名活动必须从听辨开始。")
        if not materials.intersection({"solfege_set", "pitch_motion", "melody_phrase", "audio_clip", "rhythm_pattern", "graphic_symbol_meanings"}):
            failures.append("音高/唱名活动缺少音级、旋律路线或音频材料依据。")
        if "solfege_target_core" in templates and "sing" not in practices:
            failures.append("唱名打靶不能只点击，必须包含唱回或教师确认。")
        if instruments.intersection({"virtual_keyboard", "virtual_xylophone", "pentatonic_grid"}) and _has_lower_primary(activity):
            if not _quality_names_for_toolkit(toolkit).intersection({"pitch_limited_to_material", "pitch_set_limited"}):
                failures.append("低段虚拟键盘/音条琴必须限制音域和材料音级。")

    if elements.intersection({"稳定拍", "节奏", "休止", "节拍", "拍号", "强弱"}):
        if not practices.intersection({"tap", "move", "play", "read", "arrange", "create"}):
            failures.append("节奏和节拍活动必须落到拍、动、奏、读或创编等音乐实践。")
        if "rhythm_pattern" in materials and not _quality_names_for_toolkit(toolkit).intersection(
            {"rhythm_value_check", "meter_bound", "timing_feedback_ready", "accent_controls_apply"}
        ):
            failures.append("节奏卡或节拍活动必须能检查时值、小节长度、拍号或拍点。")

    if elements.intersection({"创编结构", "五声音阶"}) or practices.intersection({"create", "revise", "arrange"}):
        if not practices.intersection({"listen", "revise", "perform", "play"}):
            failures.append("创编活动必须能试听、修改、演奏或展示，不能只拼完即通过。")
        if not _quality_names_for_toolkit(toolkit).intersection(
            {"playback_ready", "record_ready", "pitch_limited_to_material", "rhythm_value_check", "meter_bound", "sequence_reset_ready", "symbol_meaning_bound"}
        ):
            failures.append("创编活动必须有约束、试听或记录验证。")

    if _reward_is_speed_only(activity) and not _reward_has_music_evidence(activity, toolkit):
        failures.append("奖励和评分必须绑定音乐表现证据，不能只按抢答速度、排行榜或反应时间发放。")

    if failures:
        return _gate("music_pedagogy_gate", "MusicPedagogyGate", "fail", "；".join(failures))
    return _gate(
        "music_pedagogy_gate",
        "MusicPedagogyGate",
        "pass",
        "组件、教具、乐器和模板先满足音乐目标、学生实践、材料依据和课堂迁移，再允许组合。",
    )


def _toolkit_components_registered_gate(activity: dict[str, Any], toolkit: dict[str, Any]) -> dict[str, str]:
    selected = toolkit.get("selected") if isinstance(toolkit.get("selected"), dict) else {}
    components = selected.get("components") if isinstance(selected.get("components"), list) else []
    missing: list[str] = []
    invalid_contracts: list[str] = []
    for component_id in components:
        try:
            spec = get_component_spec(str(component_id))
        except ValueError:
            missing.append(str(component_id))
            continue
        if spec.get("audience") == "primary_school" and (
            not spec.get("student_actions") or not spec.get("music_elements") or not spec.get("quality_gates")
        ):
            invalid_contracts.append(str(component_id))
    ok = bool(components) and "teacher_control_bar" in components and not missing and not invalid_contracts
    return _gate(
        "toolkit_components_registered",
        "组件组合可用",
        "pass" if ok else "fail",
        f"组件：{', '.join(components)}。"
        if ok
        else _component_gate_failure_detail(components, missing, invalid_contracts),
    )


def _teaching_aids_callable_gate(activity: dict[str, Any], toolkit: dict[str, Any]) -> dict[str, str]:
    specs = toolkit.get("teaching_aid_specs") if isinstance(toolkit.get("teaching_aid_specs"), list) else []
    selected = toolkit.get("selected") if isinstance(toolkit.get("selected"), dict) else {}
    expected = selected.get("teaching_aids") if isinstance(selected.get("teaching_aids"), list) else []
    ok = len(specs) == len(expected) and all(spec.get("version") == "teaching_aid_spec_v1" for spec in specs)
    return _gate(
        "teaching_aids_callable",
        "虚拟教具可调用",
        "pass" if ok else "fail",
        "活动所需虚拟教具都能从 registry 取到。"
        if ok
        else "存在无法从 registry 取到的虚拟教具。",
    )


def _virtual_instruments_callable_gate(activity: dict[str, Any], toolkit: dict[str, Any]) -> dict[str, str]:
    specs = toolkit.get("virtual_instrument_specs") if isinstance(toolkit.get("virtual_instrument_specs"), list) else []
    selected = toolkit.get("selected") if isinstance(toolkit.get("selected"), dict) else {}
    expected = selected.get("virtual_instruments") if isinstance(selected.get("virtual_instruments"), list) else []
    ok = len(specs) == len(expected) and all(spec.get("version") == "virtual_instrument_spec_v1" for spec in specs)
    return _gate(
        "virtual_instruments_callable",
        "虚拟乐器可调用",
        "pass" if ok else "fail",
        "活动所需虚拟乐器都能从 registry 取到。"
        if ok
        else "存在无法从 registry 取到的虚拟乐器。",
    )


def _teacher_control_gate(activity: dict[str, Any]) -> dict[str, str]:
    toolkit = activity.get("toolkit") if isinstance(activity.get("toolkit"), dict) else {}
    components = toolkit.get("components") if isinstance(toolkit.get("components"), list) else []
    controls = activity.get("teacher_controls") if isinstance(activity.get("teacher_controls"), list) else []
    ok = "teacher_control_bar" in components and bool(controls)
    return _gate(
        "teacher_control_ready",
        "教师控制可用",
        "pass" if ok else "fail",
        f"教师可控制：{', '.join(controls)}。" if ok else "缺少教师控制条或教师控制项。",
    )


def _material_binding_gate(activity: dict[str, Any]) -> dict[str, str]:
    entities = activity.get("required_material_entities") if isinstance(activity.get("required_material_entities"), list) else []
    acceptance = activity.get("acceptance") if isinstance(activity.get("acceptance"), list) else []
    activity_id = str(activity.get("activity_id") or "")
    binders = material_binder_specs_for_activity(activity_id) if activity_id else []
    binder_ids = [binder["binder_id"] for binder in binders]
    ok = bool(entities) and "material_bound" in acceptance and bool(binders)
    return _gate(
        "material_binding_ready",
        "材料绑定可验收",
        "pass" if ok else "fail",
        f"需要绑定：{', '.join(entities)}；可用绑定模板：{', '.join(binder_ids)}。"
        if ok
        else "缺少必需音乐材料、material_bound 验收项，或没有可用材料绑定模板。",
    )


def _runtime_artifact_gate(activity: dict[str, Any]) -> dict[str, str]:
    toolkit = activity.get("toolkit") if isinstance(activity.get("toolkit"), dict) else {}
    components = toolkit.get("components") if isinstance(toolkit.get("components"), list) else []
    ok = bool(components) and "student_can_operate" in activity.get("acceptance", []) and "teacher_can_adjust" in activity.get("acceptance", [])
    return _gate(
        "runtime_artifact_ready",
        "运行产物可交付",
        "pass" if ok else "fail",
        "活动声明了学生可操作、教师可调整，并有可渲染组件。"
        if ok
        else "缺少学生可操作、教师可调整或可渲染组件合同。",
    )


def _source_mode_gate(delivery: dict[str, Any]) -> dict[str, str]:
    source_mode = str(delivery.get("source_mode") or "")
    ok = source_mode in {"lesson_based", "direct"}
    return _gate(
        "source_mode_gate",
        "来源模式",
        "pass" if ok else "fail",
        f"当前来源模式：{source_mode}。" if ok else "交付产物必须声明 lesson_based 或 direct。",
    )


def _grounding_gate(delivery: dict[str, Any]) -> dict[str, str]:
    source_mode = str(delivery.get("source_mode") or "")
    grounding = delivery.get("grounding") if isinstance(delivery.get("grounding"), dict) else {}
    if source_mode == "lesson_based":
        evidence = grounding.get("lesson_evidence") if isinstance(grounding.get("lesson_evidence"), dict) else {}
        required = ("stage", "objective", "material_ref", "student_behavior", "digital_reason")
        missing = [field for field in required if not evidence.get(field)]
        return _gate(
            "lesson_grounding_gate",
            "教案链路依据",
            "pass" if not missing else "fail",
            "活动节点有教案环节、目标、材料、学生行为和数字化理由。"
            if not missing
            else f"lesson_based 缺少教案依据字段：{', '.join(missing)}。",
        )
    if source_mode == "direct":
        assumptions = _string_set(grounding.get("assumptions"))
        has_request = bool(str(grounding.get("teacher_request") or "").strip())
        transparent_default = (
            bool(str(grounding.get("default_material_label") or "").strip())
            or any("默认" in item or "未上传教案" in item for item in assumptions)
        )
        false_lesson_claim = bool(grounding.get("claims_lesson_fit") or grounding.get("lesson_evidence"))
        ok = has_request and transparent_default and not false_lesson_claim
        return _gate(
            "direct_grounding_gate",
            "直接生成依据",
            "pass" if ok else "fail",
            "直接生成保留教师需求、默认假设和未绑定教案说明。"
            if ok
            else "direct 产物必须基于教师需求，透明标注默认材料，且不能声称贴合具体教案。",
        )
    return _gate("grounding_gate", "Grounding", "fail", "无法在未知来源模式下验证依据。")


def _music_truth_gate(delivery: dict[str, Any]) -> dict[str, str]:
    music_logic = delivery.get("music_logic") if isinstance(delivery.get("music_logic"), dict) else {}
    answer_source = str(music_logic.get("answer_source") or "")
    confidence = str(music_logic.get("confidence") or "")
    allowed_sources = {"lesson", "score", "audio", "midi", "teacher_confirm", "system_default_practice_material"}
    ok = answer_source in allowed_sources and confidence != "low"
    return _gate(
        "music_truth_gate",
        "音乐真值",
        "pass" if ok else "fail",
        f"正式判定来源：{answer_source}。" if ok else "音乐答案不能来自模型临时猜测或低置信推断。",
    )


def _student_music_behavior_delivery_gate(delivery: dict[str, Any]) -> dict[str, str]:
    behaviors = _string_set(delivery.get("student_music_behaviors"))
    ok = bool(behaviors.intersection({"listen", "sing", "read", "tap", "move", "play", "create", "revise", "perform", "assess", "explain"}))
    return _gate(
        "student_music_behavior_gate",
        "学生音乐行为",
        "pass" if ok else "fail",
        f"学生实际音乐行为：{', '.join(sorted(behaviors))}。" if ok else "产物必须让学生真实听、唱、奏、动、创或评。",
    )


def _teacher_control_delivery_gate(delivery: dict[str, Any]) -> dict[str, str]:
    controls = _string_set(delivery.get("teacher_controls"))
    ok = bool(controls.intersection({"pause", "tempo", "reset", "difficulty", "show_answer", "hide_hint", "replay"}))
    return _gate(
        "teacher_control_gate",
        "课堂可控",
        "pass" if ok else "fail",
        f"教师控制：{', '.join(sorted(controls))}。" if ok else "产物必须保留暂停、调速、重置、降难度或提示控制。",
    )


def _runtime_delivery_gate(delivery: dict[str, Any]) -> dict[str, str]:
    checks = delivery.get("runtime_checks") if isinstance(delivery.get("runtime_checks"), dict) else {}
    delivery_kind = str(delivery.get("delivery_kind") or "")
    page_ready = checks.get("page_open") is True
    operable = checks.get("student_operable") is True
    reset_or_card = checks.get("reset_ready") is True or delivery_kind in {"teacher_plan_card", "question_card", "confirmation_card"}
    ok = page_ready and operable and reset_or_card
    return _gate(
        "runtime_playable_gate",
        "页面可玩",
        "pass" if ok else "fail",
        "页面可打开、可操作，并有重置或卡片式下一步。"
        if ok
        else "页面验收必须证明可打开、可操作，并具备重置或明确下一步。",
    )


def _degraded_delivery_gate(delivery: dict[str, Any]) -> dict[str, str]:
    if not delivery.get("degraded_from"):
        return _gate("degraded_delivery_gate", "降级交付", "pass", "当前不是降级产物。")
    required_kind = str(delivery.get("delivery_kind") or "") in {
        "interactive_practice",
        "virtual_teaching_aid",
        "teacher_plan_card",
        "question_card",
        "confirmation_card",
    }
    ok = (
        required_kind
        and bool(str(delivery.get("degrade_reason") or "").strip())
        and bool(str(delivery.get("teacher_next_action") or "").strip())
        and isinstance(delivery.get("upgrade_path"), list)
        and bool(delivery.get("upgrade_path"))
        and delivery.get("claims_full_game") is not True
    )
    return _gate(
        "degraded_delivery_gate",
        "降级交付",
        "pass" if ok else "fail",
        "降级产物解释原因、保留教师下一步、不冒充完整游戏，并给出升级路径。"
        if ok
        else "降级不是失败，但必须说明原因、下一步和升级路径，且不能冒充完整游戏。",
    )


def _template_music_logic_gate(template: dict[str, Any]) -> dict[str, str]:
    template_id = str(template.get("template_id") or "")
    config = template.get("default_config") if isinstance(template.get("default_config"), dict) else {}
    targets = _string_set(template.get("learning_targets"))
    actions = _string_set(template.get("student_actions"))
    core_loop = _string_set(template.get("core_loop"))
    scoring = template.get("scoring") if isinstance(template.get("scoring"), dict) else {}
    feedback = template.get("feedback_rules") if isinstance(template.get("feedback_rules"), dict) else {}
    text = " ".join(str(item) for item in [template.get("description", ""), *targets, *actions, *core_loop, *feedback.values()])
    failures: list[str] = []

    if template_id in {"rhythm_echo_core", "beat_guardian_core"}:
        if not (config.get("meter") or config.get("target_beats") or config.get("pattern_pool")):
            failures.append("节奏/节拍模板必须声明拍号、目标拍点或节奏型。")
        if not any(
            key in scoring
            for key in ("timing_score", "beat_position_score", "steadiness_score", "pulse_score", "pattern_score")
        ):
            failures.append("节奏/节拍模板必须把拍点、时值或稳定拍纳入评分。")
    elif template_id == "pitch_ladder_core":
        if not (config.get("pitch_range") and config.get("notes_per_round")):
            failures.append("音高模板必须声明音域、音级数量或旋律路线。")
        if "唱" not in text and not config.get("sing_back_required"):
            failures.append("音高模板必须把判断迁移到唱回或模唱。")
    elif template_id == "solfege_target_core":
        if not (config.get("target_solfege") or config.get("music_elements", {}).get("target_solfege")):
            failures.append("唱名模板必须声明目标唱名集合。")
        if "唱回" not in text and "模唱" not in text and not config.get("require_sing_back") and not config.get("sing_back_required"):
            failures.append("唱名打靶不能只点击，必须包含唱回或教师确认。")
    elif template_id == "timbre_detective_core":
        if "听" not in text or "证据" not in text:
            failures.append("音色模板必须以声音证据和复听为依据。")
        if not any(key in scoring for key in ("source_accuracy", "evidence_score", "listening_focus")):
            failures.append("音色模板必须评分或记录音色证据。")
    elif template_id == "form_treasure_core":
        if "听" not in text or not targets.intersection({"曲式结构", "ABA", "回旋曲式", "重复与对比"}):
            failures.append("曲式模板必须听辨段落重复、对比或再现。")
        if not any(key in scoring for key in ("segment_identification", "structure_order")):
            failures.append("曲式模板必须检查段落识别和结构顺序。")
    elif template_id == "composition_puzzle_core":
        if "试听" not in text or "约束" not in text:
            failures.append("创编模板必须有约束和试听验证。")
        if not any(key in scoring for key in ("constraint_score", "audition_revision_score", "teacher_confirm_score")):
            failures.append("创编模板必须检查约束、试听修改或教师确认。")
    else:
        failures.append("未知模板没有可执行的音乐逻辑门禁画像。")

    if failures:
        return _gate("template_music_logic_gate", "模板音乐逻辑", "fail", "；".join(failures))
    return _gate("template_music_logic_gate", "模板音乐逻辑", "pass", f"{template_id} 已覆盖对应品类的音乐真值和反馈规则。")


def _template_student_music_behavior_gate(template: dict[str, Any]) -> dict[str, str]:
    text = " ".join(
        str(item)
        for item in [
            template.get("description", ""),
            *_string_set(template.get("student_actions")),
            *_string_set(template.get("core_loop")),
            *(
                template.get("default_config", {}).get("student_task_copy", {}).values()
                if isinstance(template.get("default_config", {}).get("student_task_copy"), dict)
                else []
            ),
        ]
    )
    ok = any(word in text for word in ("听", "唱", "拍", "奏", "动", "创", "评", "读", "复听", "试听"))
    return _gate(
        "template_student_music_behavior_gate",
        "模板学生音乐行为",
        "pass" if ok else "fail",
        "模板核心循环包含学生真实音乐实践。"
        if ok
        else "模板不能只提供点击、得分或颜色匹配，必须包含听、唱、奏、动、创或评。",
    )


def _template_runtime_quality_profile_gate(template: dict[str, Any]) -> dict[str, str]:
    config = template.get("default_config") if isinstance(template.get("default_config"), dict) else {}
    ok = bool(config.get("quality_gate_profile") or config.get("template_blueprint", {}).get("quality_gate_profile"))
    return _gate(
        "template_quality_profile_gate",
        "模板门禁画像",
        "pass" if ok else "fail",
        f"品类门禁画像：{config.get('quality_gate_profile') or config.get('template_blueprint', {}).get('quality_gate_profile')}。"
        if ok
        else "模板必须声明 quality_gate_profile，便于生成工作流继承品类门禁。",
    )


def _browser_open_gate(report: dict[str, Any]) -> dict[str, str]:
    opened = report.get("opened") is True
    screenshot = bool(str(report.get("screenshot") or "").strip())
    return _gate(
        "browser_open_gate",
        "浏览器打开与截图",
        "pass" if opened and screenshot else "fail",
        "浏览器可打开页面并留下截图证据。" if opened and screenshot else "浏览器验收必须证明页面能打开并产出截图或可检查结果。",
    )


def _browser_viewport_gate(report: dict[str, Any]) -> dict[str, str]:
    viewports = report.get("viewports") if isinstance(report.get("viewports"), dict) else {}
    desktop = _viewport_passed(viewports, "desktop_projection") or _viewport_passed(viewports, "desktop")
    optional_touch = _viewport_passed(viewports, "mobile_touch") or _viewport_passed(viewports, "mobile") or _viewport_passed(viewports, "tablet")
    return _gate(
        "browser_viewport_gate",
        "桌面投屏视口",
        "pass" if desktop else "fail",
        "已覆盖桌面投屏视口；移动/平板触摸视口按当前小学课堂目标作为可选记录。"
        if desktop and optional_touch
        else "已覆盖桌面投屏视口；当前阶段不要求移动端验收。"
        if desktop
        else "浏览器验收必须覆盖桌面投屏视口。",
    )


def _browser_interaction_gate(report: dict[str, Any]) -> dict[str, str]:
    interactions = report.get("interactions") if isinstance(report.get("interactions"), dict) else {}
    required = ("button_click", "play", "reset")
    missing = [key for key in required if interactions.get(key) is not True]
    drag_required = interactions.get("drag_required") is True
    if drag_required and interactions.get("drag") is not True:
        missing.append("drag")
    return _gate(
        "browser_interaction_gate",
        "按钮拖拽播放重置",
        "pass" if not missing else "fail",
        "按钮、播放、重置和必要拖拽均有操作证据。" if not missing else f"缺少浏览器交互证据：{', '.join(missing)}。",
    )


def _browser_canvas_gate(report: dict[str, Any]) -> dict[str, str]:
    canvas = report.get("canvas") if isinstance(report.get("canvas"), dict) else {}
    required = canvas.get("required") is True
    ok = not required or canvas.get("nonblank") is True
    return _gate(
        "browser_canvas_gate",
        "Canvas 非空",
        "pass" if ok else "fail",
        "Phaser/canvas 产物已验证非空。" if required else "当前产物不要求 canvas 非空验收。",
    )


def _browser_layout_gate(report: dict[str, Any]) -> dict[str, str]:
    layout = report.get("layout") if isinstance(report.get("layout"), dict) else {}
    ok = layout.get("text_overlap") is not True and layout.get("controls_blocked") is not True
    return _gate(
        "browser_layout_gate",
        "布局无遮挡",
        "pass" if ok else "fail",
        "文本不遮挡操作区，控件可用。" if ok else "页面存在文字遮挡或控件被遮挡。",
    )


def _browser_audio_gate(report: dict[str, Any]) -> dict[str, str]:
    audio = report.get("audio") if isinstance(report.get("audio"), dict) else {}
    ok = audio.get("button_error") is not True and audio.get("playback_checked") is True
    return _gate(
        "browser_audio_gate",
        "音频按钮",
        "pass" if ok else "fail",
        "音频按钮已检查且无播放报错。" if ok else "音频按钮必须检查播放路径，并且不能报错。",
    )


def _viewport_passed(viewports: dict[str, Any], key: str) -> bool:
    viewport = viewports.get(key)
    if viewport is True:
        return True
    if isinstance(viewport, dict):
        return viewport.get("passed") is True or viewport.get("status") == "pass"
    return False


def _asset_pack_gates() -> list[dict[str, str]]:
    try:
        packs = list_asset_packs()
    except ValueError as exc:
        return [
            _gate(
                "asset_pack_manifest_ready",
                "素材包清单可用",
                "fail",
                f"素材包 manifest 无法校验：{exc}",
            )
        ]
    image_gen_packs = [pack for pack in packs if pack.get("source") == "image_gen_generated"]
    legacy_external_packs = [pack for pack in packs if pack.get("source") == "doubao_generated"]
    file_reports = list_asset_pack_file_reports(packs)
    template_game_asset_report = evaluate_template_game_asset_library()
    audio_packs = list_instrument_audio_packs()
    audio_missing_files = [
        pack
        for pack in audio_packs
        if isinstance(pack.get("local_file_report"), dict) and pack["local_file_report"].get("status") != "ready"
    ]
    audio_needs_open_samples = [pack for pack in audio_packs if pack.get("sample_status") != "ready"]
    blocking_file_reports = [report for report in file_reports if report.get("blocking")]
    pending_doubao_reports = [report for report in file_reports if report.get("status") == "pending_doubao_generation"]
    pack_activity_ids = {
        activity_id
        for pack in packs
        for activity_id in pack.get("allowed_activities", [])
        if isinstance(activity_id, str) and activity_id
    }
    required_activity_ids = {activity["activity_id"] for activity in list_activity_templates()}
    covered_required_ids = required_activity_ids.intersection(pack_activity_ids)
    return [
        _gate(
            "asset_pack_manifest_ready",
            "素材包清单可用",
            "pass" if packs else "fail",
            f"已登记 {len(packs)} 个小学音乐课堂素材包，包含 {len(image_gen_packs)} 个生成 PNG 素材包、{len(legacy_external_packs)} 个历史外部生图兼容素材包；当前模板库固定图片优先使用本地 image2、项目生成和运行时生成。"
            if packs
            else "没有可调用的素材包。",
        ),
        _gate(
            "asset_pack_music_education_ready",
            "素材包音乐教育校准",
            "pass" if _all_asset_packs_have_music_alignment(packs) else "fail",
            "素材包声明了音乐要素、学生实践、学段和教学提示。"
            if _all_asset_packs_have_music_alignment(packs)
            else "存在缺少音乐教育校准的素材包。",
        ),
        _gate(
            "asset_pack_activity_binding_ready",
            "素材包活动绑定",
            "pass" if covered_required_ids else "fail",
            f"素材包已绑定 {len(covered_required_ids)} 个小学活动模板。"
            if covered_required_ids
            else "素材包没有绑定任何小学活动模板。",
        ),
        _gate(
            "project_generated_asset_files_ready",
            "项目生成素材文件就绪",
            "pass" if not blocking_file_reports else "fail",
            "项目生成 SVG/CSS 素材包的 preview 和 assets 文件均已存在。"
            if not blocking_file_reports
            else f"存在 {len(blocking_file_reports)} 个项目生成素材包缺文件。",
        ),
        _gate(
            "doubao_generated_asset_files_status",
            "历史外部生图素材补齐状态",
            "warning" if pending_doubao_reports else "pass",
            f"{len(pending_doubao_reports)} 个历史外部生图兼容素材包仍缺 PNG，需迁移到 image_gen 或补齐文件后再验收。"
            if pending_doubao_reports
            else "无需历史外部生图补齐；image_gen、项目生成和运行时素材按各自文件/合同验收。",
        ),
        _gate(
            "template_game_raster_assets_ready",
            "模板游戏图片素材就绪",
            "pass" if template_game_asset_report["status"] == "ready" else "fail",
            f"模板游戏素材库已登记 {template_game_asset_report['asset_pack_count']} 个素材包，{template_game_asset_report['present_file_count']} 个图片文件可用。"
            if template_game_asset_report["status"] == "ready"
            else f"模板游戏素材库缺 {template_game_asset_report['missing_file_count']} 个图片文件。",
        ),
        _gate(
            "instrument_audio_pack_status",
            "乐器听辨音频状态",
            "fail" if audio_missing_files else "warning" if audio_needs_open_samples else "pass",
            f"{len(audio_missing_files)} 个乐器听辨音频包缺本地 SoundFont 文件。"
            if audio_missing_files
            else "本地 SoundFont 文件已就绪，WebAudio 合成音可用；真实开源采样仍需补齐，不能标记为真实采样。"
            if audio_needs_open_samples
            else "乐器听辨音频包真实采样已就绪。",
        ),
    ]


def _all_asset_packs_have_music_alignment(packs: list[dict[str, Any]]) -> bool:
    for pack in packs:
        alignment = pack.get("education_alignment") if isinstance(pack.get("education_alignment"), dict) else {}
        if not (
            alignment.get("primary_competency")
            and alignment.get("music_elements")
            and alignment.get("student_practices")
            and alignment.get("grade_bands")
            and alignment.get("pedagogy_notes")
        ):
            return False
    return True


def _gate(gate_id: str, label: str, status: str, detail: str) -> dict[str, str]:
    return {"id": gate_id, "label": label, "status": status, "detail": detail}


def _string_set(value: Any) -> set[str]:
    if isinstance(value, list) or isinstance(value, tuple) or isinstance(value, set):
        return {str(item).strip() for item in value if str(item).strip()}
    if isinstance(value, dict):
        return {str(item).strip() for item in value.values() if str(item).strip()}
    if str(value or "").strip():
        return {str(value).strip()}
    return set()


def _has_lower_primary(activity: dict[str, Any]) -> bool:
    grade_bands = _string_set(activity.get("grade_bands"))
    return "lower_primary" in grade_bands or "小学低段" in grade_bands


def _quality_names_for_toolkit(toolkit: dict[str, Any]) -> set[str]:
    names: set[str] = set()
    selected = toolkit.get("selected") if isinstance(toolkit.get("selected"), dict) else {}
    for group in ("components", "teaching_aids", "virtual_instruments", "game_templates"):
        names.update(_string_set(selected.get(group)))
    for component_id in _string_set(selected.get("components")):
        try:
            names.update(_string_set(get_component_spec(component_id).get("quality_gates")))
        except ValueError:
            pass
    for specs_key in ("teaching_aid_specs", "virtual_instrument_specs"):
        specs = toolkit.get(specs_key) if isinstance(toolkit.get(specs_key), list) else []
        for spec in specs:
            if isinstance(spec, dict):
                names.update(_string_set(spec.get("quality_gates")))
                runtime = spec.get("runtime_contract") if isinstance(spec.get("runtime_contract"), dict) else {}
                names.update(_string_set(runtime.get("quality_gates")))
    return names


def _reward_is_speed_only(activity: dict[str, Any]) -> bool:
    reward_policy = activity.get("reward_policy") if isinstance(activity.get("reward_policy"), dict) else {}
    acceptance = activity.get("acceptance") if isinstance(activity.get("acceptance"), list) else []
    text_parts = [
        activity.get("name", ""),
        activity.get("description", ""),
        *acceptance,
        reward_policy.get("reward_basis", ""),
        reward_policy.get("basis", ""),
        reward_policy.get("ranking", ""),
    ]
    score_fields = reward_policy.get("score_fields") if isinstance(reward_policy.get("score_fields"), list) else []
    text = " ".join(str(item) for item in [*text_parts, *score_fields])
    speed_markers = ("抢答", "速度", "最快", "排行榜", "排名", "leaderboard", "response_speed", "reaction_time", "fastest")
    return any(marker in text for marker in speed_markers)


def _reward_has_music_evidence(activity: dict[str, Any], toolkit: dict[str, Any]) -> bool:
    reward_policy = activity.get("reward_policy") if isinstance(activity.get("reward_policy"), dict) else {}
    if reward_policy.get("music_evidence_required") is False:
        return False
    if reward_policy.get("music_evidence_required") is True:
        return True
    selected = toolkit.get("selected") if isinstance(toolkit.get("selected"), dict) else {}
    components = _string_set(selected.get("components"))
    quality_names = _quality_names_for_toolkit(toolkit)
    evidence_components = {"rubric_panel", "tap_feedback", "meter_track", "compare_player", "graphic_score_canvas", "form_card_timeline"}
    evidence_gates = {
        "music_reason_required",
        "music_evidence_required",
        "music_structure_check",
        "timing_feedback_ready",
        "rhythm_value_check",
        "symbol_meaning_bound",
        "playback_ready",
    }
    return bool(components.intersection(evidence_components) and quality_names.intersection(evidence_gates))


def _component_gate_failure_detail(components: list[str], missing: list[str], invalid_contracts: list[str]) -> str:
    if not components:
        return "活动没有可组合组件。"
    if "teacher_control_bar" not in components:
        return "活动缺少教师控制条。"
    if missing:
        return f"活动引用了未注册组件：{', '.join(missing)}。"
    if invalid_contracts:
        return f"组件缺少小学音乐教育合同字段：{', '.join(invalid_contracts)}。"
    return "组件组合合同不完整。"
