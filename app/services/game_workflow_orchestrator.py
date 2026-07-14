from __future__ import annotations

from copy import deepcopy
import re
from typing import Any

from app.services.experience_variant_registry import get_experience_variant, list_experience_variants
from app.services.activity_chain_planner import plan_activity_chain
from app.services.activity_spec import build_activity_spec_from_lesson, build_activity_spec_from_teacher_request
from app.services.game_template_registry import (
    build_game_instance,
    get_game_skin,
    get_game_template,
    list_game_skins,
)
from app.services.delivery_gate import evaluate_delivery_gate
from app.services.experience_director import build_experience_script
from app.services.frontend_handoff_builder import build_frontend_handoff_contract
from app.services.frontend_presentation_pack_builder import build_frontend_presentation_pack
from app.services.game_variant_spec import build_game_variant_spec
from app.services.gameplay_blueprint_builder import build_gameplay_blueprint
from app.services.lesson_adaptation_director import attach_lesson_adaptation
from app.services.lesson_delivery_gates import (
    evaluate_lesson_alignment_gate,
    evaluate_lesson_slot_coverage,
    evaluate_template_fidelity_gate,
)
from app.services.lesson_template_personalizer import build_template_instance_patch
from app.services.music_element_adjustment_contract import filter_template_config_overrides
from app.services.music_game_skill_orchestrator import build_music_game_production_spec
from app.services.opencode_role_policy import build_opencode_role_policy, opencode_regular_path_is_isolated
from app.services.render_spec_builder import build_render_spec
from app.services.template_mechanism_router import route_lesson_template
from app.services.template_blueprint_registry import build_blueprint_quality_gates
from app.services.template_fidelity_contract import build_template_fidelity_contract
from app.services.theme_pack_builder import build_theme_pack
from app.services.task_portrait import build_task_portrait_from_lesson
from app.services.toolkit_registry import build_toolkit_spec


WORKFLOW_VERSION = "music_game_workflow_v1"

TEMPLATE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "composition_puzzle_core": (
        "拼图创编",
        "节奏拼图",
        "节奏创编",
        "时值拼图",
        "旋律拼图",
        "旋律创作",
        "旋律创编",
        "旋律创造",
        "五声音阶创编",
        "旋律节奏拼图",
        "音符拼图",
        "旋律和节奏",
        "节奏卡",
        "拖拽拼成",
        "素材拼成",
        "创编工坊",
    ),
    "beat_guardian_core": ("节拍", "强拍", "弱拍", "拍号", "稳拍", "律动", "进入", "二拍子", "三拍子", "四拍子"),
    "pitch_ladder_core": ("音高", "高低", "唱名", "do", "re", "mi", "sol", "la", "级进", "跳进", "旋律线"),
    "rhythm_echo_core": ("节奏", "时值", "附点", "切分", "休止", "复刻", "模仿", "拍手", "接龙"),
    "solfege_target_core": ("唱名打靶", "听音打靶", "唱回", "唱名听辨", "内听", "靶"),
    "timbre_detective_core": ("音色", "乐器", "侦探", "笛子", "二胡", "小提琴", "音色证据"),
    "form_treasure_core": ("曲式", "ABA", "回旋", "重复对比", "段落", "结构", "曲式寻宝"),
}

SKIN_KEYWORDS: dict[str, tuple[str, ...]] = {
    "dragon_boat": ("龙舟", "端午", "鼓点", "民俗"),
    "stage_light": ("舞台", "表演", "合奏", "追光"),
    "train_conductor": ("列车", "火车", "车轮", "低年级"),
    "space_orbit": ("太空", "星球", "轨道", "宇宙"),
    "echo_cave": ("回声", "山洞", "记忆"),
    "robot_signal": ("机器人", "信号", "编码", "科技"),
    "rain_window": ("雨", "窗", "轻柔", "雨点"),
    "kitchen_band": ("厨房", "生活", "锅", "杯"),
    "mountain_steps": ("山", "山路", "爬梯", "登山", "音高山路"),
    "cloud_elevator": ("云", "升空", "高低"),
    "bamboo_ladder": ("竹", "中国风", "民歌"),
    "lantern_tower": ("灯", "塔", "点灯", "短旋律"),
    "treasure_map": ("藏宝", "寻宝", "地图", "ABA"),
    "constellation_path": ("星图", "星座", "回旋", "航线"),
    "museum_gallery": ("展馆", "博物馆", "听赏"),
    "train_route": ("列车", "火车", "路线", "重复"),
    "stage_script": ("剧场", "舞台", "分幕", "剧本"),
    "composition_studio": ("创编", "工坊", "教室", "综合"),
    "rhythm_tile_table": ("节奏拼图", "节奏创编", "时值拼图", "积木"),
    "melody_garden": ("旋律拼图", "旋律创作", "音级创编", "花园"),
}

SOFT_DIAGNOSTIC_GATE_IDS = {"lesson_alignment_gate"}


def build_direct_game_workflow(need: str, options: dict[str, Any] | None = None) -> dict[str, Any]:
    """Plan a game from a plain-language request without touching the lesson-analysis chain."""
    options = options or {}
    clean_need = str(need or "").strip()
    template_id = _choose_template(clean_need, preferred=options.get("template_id"))
    config = _config_from_text(
        template_id,
        clean_need,
        options,
        source_kind="direct_game",
    )
    instance = build_game_instance(config)
    instance["skin_selection_source"] = _skin_selection_source_from_config(config)
    proposal_card = _build_proposal_card(
        workflow_kind="direct_game",
        template_id=template_id,
        instance=instance,
        source_text=clean_need,
        source_summary="教师直接描述的游戏目标",
    )
    activity_spec = build_activity_spec_from_teacher_request(
        clean_need,
        options={**options, "activity_shape": "game", "runtime_ref": options.get("runtime_ref") or "teacher_projection"},
    )
    return _workflow_payload(
        workflow_kind="direct_game",
        source={"need": clean_need, "options": deepcopy(options), "activity_spec": activity_spec},
        proposal_card=proposal_card,
        instance=instance,
        entry_contract={
            "input": "自然语言游戏需求",
            "must_not_mix_with": "lesson_game",
            "handoff": "先形成方案卡，再进入模板实例化或人工确认",
        },
    )


def build_lesson_game_workflow(proposal: dict[str, Any], options: dict[str, Any] | None = None) -> dict[str, Any]:
    """Plan a game from analyzed lesson material. This intentionally stays separate from direct generation."""
    options = options or {}
    lesson_analysis = proposal.get("lesson_analysis") if isinstance(proposal.get("lesson_analysis"), dict) else proposal
    lesson_source = proposal.get("lesson_source", {}) if isinstance(proposal.get("lesson_source"), dict) else {}
    if isinstance(lesson_analysis, dict):
        lesson_analysis = attach_lesson_adaptation(
            lesson_analysis,
            lesson_source=lesson_source,
            extra_need=str(options.get("extra_need") or proposal.get("extra_need") or ""),
        )
    analysis_context = lesson_analysis.get("lesson_context", {}) if isinstance(lesson_analysis, dict) else {}
    proposal_context = proposal.get("lesson_context", {}) if isinstance(proposal.get("lesson_context"), dict) else {}
    lesson_context = {**proposal_context, **analysis_context}
    music_game = lesson_analysis.get("music_game", {}) if isinstance(lesson_analysis, dict) else {}
    lesson_fit = _lesson_fit_from(proposal, lesson_analysis, lesson_context)
    lesson_adaptation = _lesson_adaptation_from(proposal, lesson_analysis, lesson_context)
    music_element_adjustment_contract = _music_element_adjustment_from(proposal, lesson_analysis, lesson_context, lesson_fit)
    template_decision = route_lesson_template(
        lesson_adaptation=lesson_adaptation,
        lesson_fit=lesson_fit,
        preferred_template_id=options.get("template_id"),
    )
    contract_template_id = str(
        (music_element_adjustment_contract.get("template_match") or {}).get("template_id")
        if isinstance(music_element_adjustment_contract.get("template_match"), dict)
        else ""
    ).strip()
    fit_auto_template_id = _high_confidence_fit_template_id(lesson_fit)
    fit_evidence = lesson_fit.get("lesson_evidence", {}) if isinstance(lesson_fit.get("lesson_evidence"), dict) else {}
    material_binding = lesson_fit.get("material_binding", {}) if isinstance(lesson_fit.get("material_binding"), dict) else {}
    source_text = _compact_join(
        [
            lesson_fit.get("fit_summary"),
            fit_evidence.get("music_element"),
            fit_evidence.get("target_objective"),
            fit_evidence.get("target_stage"),
            fit_evidence.get("segment_task"),
            fit_evidence.get("gameable_point"),
            material_binding.get("song_title"),
            material_binding.get("selected_phrase_label"),
            lesson_context.get("target_music_element"),
            lesson_context.get("teaching_objective"),
            music_game.get("recommended_game_name"),
            music_game.get("recommended_game_type"),
            music_game.get("core_mechanic"),
            proposal.get("need"),
            options.get("extra_need"),
        ]
    )
    template_id = _choose_template(
        source_text,
        preferred=contract_template_id or fit_auto_template_id or template_decision.get("template_id"),
        allow_unmatched=template_decision.get("decision") == "unmatched" and not contract_template_id,
    )
    fit_config_overrides = (
        template_decision.get("config_overrides", {})
        if isinstance(template_decision.get("config_overrides"), dict)
        else {}
    )
    contract_config_overrides = (
        filter_template_config_overrides(template_id, music_element_adjustment_contract.get("config_overrides"))
        if isinstance(music_element_adjustment_contract.get("config_overrides"), dict)
        else {}
    )
    workflow_options = {
        **fit_config_overrides,
        **contract_config_overrides,
        **options,
        "grade_band": lesson_context.get("grade_band") or options.get("grade_band"),
        "music_concept": fit_evidence.get("music_element") or lesson_context.get("target_music_element") or options.get("music_concept"),
        "teacher_prompt": (
            options.get("teacher_prompt")
            or contract_config_overrides.get("teacher_prompt")
            or fit_config_overrides.get("teacher_prompt")
            or _lesson_teacher_prompt(lesson_context, music_game)
        ),
    }
    lesson_audio_sync = _lesson_audio_sync_from(
        lesson_source=lesson_source,
        lesson_context=lesson_context,
        material_binding=material_binding,
        options=options,
    )
    if lesson_audio_sync:
        workflow_options.setdefault("lesson_audio_sync", lesson_audio_sync)
        workflow_options.setdefault("audio_mode", "hybrid")
    template_instance_patch: dict[str, Any] = {}
    if template_id:
        template_instance_patch = build_template_instance_patch(
            template_id=template_id,
            lesson_context=lesson_context,
            lesson_fit=lesson_fit,
            lesson_adaptation=lesson_adaptation,
            source_text=source_text,
        )
        patch_options = (
            template_instance_patch.get("patch", {})
            if isinstance(template_instance_patch.get("patch"), dict)
            else {}
        )
        protected_options = options if template_instance_patch.get("source") in {"llm", "music_element_binding"} else {**fit_config_overrides, **contract_config_overrides, **options}
        patch_options = _protect_explicit_lesson_options(patch_options, protected_options)
        if template_instance_patch.get("source") in {"llm", "music_element_binding"}:
            workflow_options = {**workflow_options, **patch_options}
        else:
            workflow_options = {**workflow_options, **patch_options, **contract_config_overrides}
        workflow_options = {**workflow_options, **filter_template_config_overrides(template_id, options)}
        game_variant_spec = build_game_variant_spec(
            lesson_fit=lesson_fit,
            template_id=template_id,
            options=workflow_options,
        )
        config = _config_from_text(
            template_id,
            source_text,
            workflow_options,
            source_kind="lesson_game",
        )
        instance = build_game_instance(config)
        instance["skin_selection_source"] = _skin_selection_source_from_config(config)
    else:
        game_variant_spec = {}
        instance = _unmatched_lesson_instance(workflow_options)
    proposal_card = _build_proposal_card(
        workflow_kind="lesson_game",
        template_id=template_id,
        instance=instance,
        source_text=source_text,
        source_summary="教案与音乐材料分析后的游戏目标",
        lesson_context=lesson_context,
        lesson_source=lesson_source,
        lesson_fit=lesson_fit,
    )
    lesson_payload_for_activity = {
        "lesson_context": lesson_context,
        "lesson_fit": lesson_fit,
        "lesson_source": lesson_source,
        "lesson_analysis": lesson_analysis,
    }
    activity_spec = build_activity_spec_from_lesson(lesson_payload_for_activity, options=options)
    task_portrait = build_task_portrait_from_lesson(lesson_payload_for_activity)
    return _workflow_payload(
        workflow_kind="lesson_game",
        source={
            "lesson_context": deepcopy(lesson_context),
            "lesson_source": deepcopy(lesson_source),
            "lesson_fit": deepcopy(lesson_fit),
            "lesson_adaptation": deepcopy(lesson_adaptation),
            "music_element_adjustment_contract": deepcopy(music_element_adjustment_contract),
            "template_decision": deepcopy(template_decision),
            "game_variant_spec": deepcopy(game_variant_spec),
            "template_instance_patch": deepcopy(template_instance_patch),
            "options": deepcopy(options),
            "activity_spec": deepcopy(activity_spec),
            "task_portrait": deepcopy(task_portrait),
        },
        proposal_card=proposal_card,
        instance=instance,
        entry_contract={
            "input": "教案、谱例、音频或教师补充要求",
            "must_not_mix_with": "direct_game",
            "handoff": "必须先完成教案分析和方案确认，再进入模板实例化或网页生成",
        },
    )


def list_workflow_skins(template_id: str | None = None) -> list[dict[str, Any]]:
    return list_game_skins(template_id)


def _workflow_payload(
    *,
    workflow_kind: str,
    source: dict[str, Any],
    proposal_card: dict[str, Any],
    instance: dict[str, Any],
    entry_contract: dict[str, str],
) -> dict[str, Any]:
    lesson_adaptation = source.get("lesson_adaptation", {}) if isinstance(source.get("lesson_adaptation"), dict) else {}
    template_decision = source.get("template_decision", {}) if isinstance(source.get("template_decision"), dict) else {}
    gameplay_blueprint = build_gameplay_blueprint(
        workflow_kind=workflow_kind,
        proposal_card=proposal_card,
        instance=instance,
        source=source,
    )
    experience_script = build_experience_script(
        gameplay_blueprint=gameplay_blueprint,
        proposal_card=proposal_card,
    )
    theme_pack = build_theme_pack(
        instance=instance,
        gameplay_blueprint=gameplay_blueprint,
        proposal_card=proposal_card,
    )
    render_spec = build_render_spec(
        workflow_kind=workflow_kind,
        gameplay_blueprint=gameplay_blueprint,
        experience_script=experience_script,
        theme_pack=theme_pack,
    )
    delivery_decision = evaluate_delivery_gate(
        workflow_kind=workflow_kind,
        gameplay_blueprint=gameplay_blueprint,
        experience_script=experience_script,
        theme_pack=theme_pack,
        render_spec=render_spec,
    )
    frontend_handoff_contract = build_frontend_handoff_contract(
        workflow_kind=workflow_kind,
        lesson_adaptation=lesson_adaptation,
        template_decision=template_decision or _direct_template_decision(instance),
        gameplay_blueprint=gameplay_blueprint,
        theme_pack=theme_pack,
        render_spec=render_spec,
    )
    presentation_pack = build_frontend_presentation_pack(
        gameplay_blueprint=gameplay_blueprint,
        experience_script=experience_script,
        theme_pack=theme_pack,
        render_spec=render_spec,
    )
    opencode_role_policy = build_opencode_role_policy(
        workflow_kind=workflow_kind,
        instance=instance,
        frontend_handoff_contract=frontend_handoff_contract,
        presentation_pack=presentation_pack,
    )
    template_fidelity_contract = build_template_fidelity_contract(
        instance,
        str(instance.get("skin_selection_source") or "template_default"),
    )
    lesson_alignment_result = (
        evaluate_lesson_alignment_gate(
            template_id=str(instance.get("template_id") or ""),
            lesson_context=source.get("lesson_context", {}) if isinstance(source.get("lesson_context"), dict) else {},
            lesson_fit=source.get("lesson_fit", {}) if isinstance(source.get("lesson_fit"), dict) else {},
            proposal_card=proposal_card,
        )
        if workflow_kind == "lesson_game"
        else {}
    )
    template_fidelity_result = (
        evaluate_template_fidelity_gate(
            template_fidelity_contract=template_fidelity_contract,
            source_options=source.get("options", {}) if isinstance(source.get("options"), dict) else {},
        )
        if workflow_kind == "lesson_game"
        else {}
    )
    lesson_slot_coverage_result = (
        evaluate_lesson_slot_coverage(
            template_id=str(instance.get("template_id") or ""),
            lesson_alignment_result=lesson_alignment_result,
            game_variant_spec=source.get("game_variant_spec", {}) if isinstance(source.get("game_variant_spec"), dict) else {},
        )
        if workflow_kind == "lesson_game"
        else {}
    )
    if workflow_kind == "lesson_game" and isinstance(source.get("game_variant_spec"), dict):
        source["game_variant_spec"] = {
            **deepcopy(source.get("game_variant_spec", {})),
            "lesson_contract_ref": deepcopy(lesson_alignment_result.get("lesson_contract_ref", {})),
            "lesson_alignment_result": deepcopy(lesson_alignment_result),
            "template_fidelity_result": deepcopy(template_fidelity_result),
            "lesson_slot_coverage_result": deepcopy(lesson_slot_coverage_result),
        }
        gameplay_blueprint = _sync_blueprint_variant_contracts(gameplay_blueprint, source["game_variant_spec"])
        render_spec = _sync_render_variant_contracts(render_spec, source["game_variant_spec"])
        frontend_handoff_contract = _sync_handoff_variant_contracts(frontend_handoff_contract, source["game_variant_spec"])
    activity_spec = _activity_spec_for_workflow(workflow_kind, source, proposal_card, instance)
    task_portrait = source.get("task_portrait", {}) if isinstance(source.get("task_portrait"), dict) else {}
    activity_chain = plan_activity_chain(activity_spec, portrait=task_portrait)
    toolkit_spec = _workflow_toolkit_spec(activity_spec)
    music_game_production_spec = build_music_game_production_spec(
        workflow_kind=workflow_kind,
        activity_spec=activity_spec,
        source=source,
        instance=instance,
        game_variant_spec=source.get("game_variant_spec", {}) if isinstance(source.get("game_variant_spec"), dict) else {},
    )
    source["music_game_production_spec"] = deepcopy(music_game_production_spec)
    quality_gates = _quality_gates(
        workflow_kind,
        proposal_card,
        instance,
        source,
        gameplay_blueprint=gameplay_blueprint,
        experience_script=experience_script,
        theme_pack=theme_pack,
        render_spec=render_spec,
        delivery_decision=delivery_decision,
        lesson_adaptation=lesson_adaptation,
        template_decision=template_decision or _direct_template_decision(instance),
        frontend_handoff_contract=frontend_handoff_contract,
        opencode_role_policy=opencode_role_policy,
        template_fidelity_contract=template_fidelity_contract,
        lesson_alignment_result=lesson_alignment_result,
        template_fidelity_result=template_fidelity_result,
        lesson_slot_coverage_result=lesson_slot_coverage_result,
    )
    pass_count = sum(1 for gate in quality_gates if gate["status"] == "pass")
    experience_variant = (
        instance.get("config", {}).get("experience_variant")
        if isinstance(instance.get("config"), dict) and isinstance(instance.get("config", {}).get("experience_variant"), dict)
        else {}
    )
    hard_blocking_failures = hard_blocking_quality_failures(quality_gates)
    student_runtime_config = _student_runtime_config(instance, music_game_production_spec)
    teacher_control_state = _teacher_control_state(instance, activity_spec, music_game_production_spec)
    return {
        "workflow_version": WORKFLOW_VERSION,
        "workflow_kind": workflow_kind,
        "quality_mode": "quality_first",
        "entry_contract": entry_contract,
        "source": deepcopy(source),
        "responsibility_map": _responsibility_map(
            workflow_kind=workflow_kind,
            lesson_adaptation=lesson_adaptation,
            template_decision=template_decision or _direct_template_decision(instance),
            frontend_handoff_contract=frontend_handoff_contract,
        ),
        "proposal_card": proposal_card,
        "instance": instance,
        "template_match": _template_match(instance),
        "activity_spec": activity_spec,
        "toolkit_spec": toolkit_spec,
        "task_portrait": deepcopy(task_portrait),
        "activity_chain": activity_chain,
        "music_game_production_spec": music_game_production_spec,
        "teacher_control_state": teacher_control_state,
        "student_runtime_config": student_runtime_config,
        "revision_history": [],
        "template_fidelity_contract": template_fidelity_contract,
        **(
            {"game_variant_spec": deepcopy(source.get("game_variant_spec", {}))}
            if workflow_kind == "lesson_game"
            else {}
        ),
        "lesson_adaptation": lesson_adaptation,
        "template_decision": template_decision or _direct_template_decision(instance),
        **(
            {"template_instance_patch": deepcopy(source.get("template_instance_patch", {}))}
            if workflow_kind == "lesson_game"
            else {}
        ),
        "experience_variant": deepcopy(experience_variant),
        "gameplay_blueprint": gameplay_blueprint,
        "experience_script": experience_script,
        "theme_pack": theme_pack,
        "presentation_pack": presentation_pack,
        "opencode_role_policy": opencode_role_policy,
        "render_spec": render_spec,
        "frontend_handoff_contract": frontend_handoff_contract,
        "delivery_decision": delivery_decision,
        "quality_gates": quality_gates,
        "quality_summary": {
            "pass_count": pass_count,
            "total": len(quality_gates),
            "blocking_failures": [gate for gate in quality_gates if gate["status"] == "fail"],
            "hard_blocking_failures": hard_blocking_failures,
        },
        "next_actions": [
            "教师确认方案卡是否贴合课堂目标",
            "按班级水平微调难度、提示、皮肤和通关标准",
            "确认后复用模板运行时生成游戏实例",
        ],
    }


def _activity_spec_for_workflow(
    workflow_kind: str,
    source: dict[str, Any],
    proposal_card: dict[str, Any],
    instance: dict[str, Any],
) -> dict[str, Any]:
    if isinstance(source.get("activity_spec"), dict) and source["activity_spec"]:
        spec = deepcopy(source["activity_spec"])
    elif workflow_kind == "direct_game":
        need = str(source.get("need") or proposal_card.get("evidence", {}).get("source_text") or "")
        spec = build_activity_spec_from_teacher_request(
            need,
            options={"activity_shape": "game", "runtime_ref": "teacher_projection"},
        )
    else:
        spec = {}
    if spec:
        spec.setdefault("runtime_ref", "teacher_projection")
        spec.setdefault("quality_gate_result", {"status": "pass"})
        if not spec.get("toolkit_ref"):
            template_id = str(instance.get("template_id") or "")
            spec["toolkit_ref"] = _activity_ref_from_template(template_id)
    return spec


def _workflow_toolkit_spec(activity_spec: dict[str, Any]) -> dict[str, Any]:
    activity_id = str(activity_spec.get("toolkit_ref") or "")
    if not activity_id:
        return {"version": "toolkit_spec_v1", "tools": []}
    try:
        return build_toolkit_spec(activity_id)
    except ValueError:
        return {
            "version": "toolkit_spec_v1",
            "activity_id": activity_id,
            "tools": [],
            "why": "当前活动形态还没有匹配到 registry 条目。",
        }


def _activity_ref_from_template(template_id: str) -> str:
    return {
        "beat_guardian_core": "meter_body_movement",
        "rhythm_echo_core": "rhythm_warmup",
        "pitch_ladder_core": "solfege_sorting",
        "solfege_target_core": "solfege_sorting",
        "timbre_detective_core": "instrument_timbre_match",
        "form_treasure_core": "form_ordering",
        "composition_puzzle_core": "xylophone_creation",
    }.get(template_id, "rhythm_warmup")


def _student_runtime_config(instance: dict[str, Any], music_game_production_spec: dict[str, Any]) -> dict[str, Any]:
    package_runtime = (
        music_game_production_spec.get("runtime_config")
        if isinstance(music_game_production_spec.get("runtime_config"), dict)
        else {}
    )
    if package_runtime:
        return deepcopy(package_runtime)
    config = deepcopy(instance.get("config", {})) if isinstance(instance.get("config"), dict) else {}
    if music_game_production_spec.get("package_id"):
        config["production_package_ref"] = music_game_production_spec["package_id"]
    return config


def _teacher_control_state(
    instance: dict[str, Any],
    activity_spec: dict[str, Any],
    music_game_production_spec: dict[str, Any] | None = None,
) -> dict[str, Any]:
    config = instance.get("config") if isinstance(instance.get("config"), dict) else {}
    production = music_game_production_spec if isinstance(music_game_production_spec, dict) else {}
    teacher_control_config = (
        production.get("teacher_control_config")
        if isinstance(production.get("teacher_control_config"), dict)
        else {}
    )
    state = {
        "version": "teacher_control_state_v1",
        "tempo": config.get("bpm"),
        "show_answer": config.get("show_answer", True),
        "show_solfege": config.get("show_solfege", False),
        "group_mode": config.get("group_mode", activity_spec.get("runtime_ref") == "group_shared_tablet"),
        "allow_relisten": config.get("allow_relisten", True),
    }
    if production.get("package_id"):
        state["production_package_ref"] = production["package_id"]
    if teacher_control_config.get("editable_controls"):
        state["editable_controls"] = deepcopy(teacher_control_config["editable_controls"])
    return state


def hard_blocking_quality_failures(quality_gates: list[dict[str, Any]] | Any) -> list[dict[str, Any]]:
    if not isinstance(quality_gates, list):
        return []
    return [
        gate
        for gate in quality_gates
        if isinstance(gate, dict)
        and gate.get("status") == "fail"
        and gate.get("id") not in SOFT_DIAGNOSTIC_GATE_IDS
    ]


def _lesson_fit_from(
    proposal: dict[str, Any],
    lesson_analysis: dict[str, Any],
    lesson_context: dict[str, Any],
) -> dict[str, Any]:
    for value in (
        proposal.get("lesson_fit"),
        lesson_analysis.get("lesson_fit"),
        lesson_context.get("lesson_fit"),
    ):
        if isinstance(value, dict) and value:
            return value
    return {}


def _sync_blueprint_variant_contracts(blueprint: dict[str, Any], variant: dict[str, Any]) -> dict[str, Any]:
    updated = dict(blueprint)
    updated["game_variant_spec"] = deepcopy(variant)
    updated["music_entity_execution"] = _music_entity_execution_from_variant(variant)
    return updated


def _sync_render_variant_contracts(render_spec: dict[str, Any], variant: dict[str, Any]) -> dict[str, Any]:
    updated = dict(render_spec)
    updated["music_entity_execution"] = _music_entity_execution_from_variant(variant)
    return updated


def _sync_handoff_variant_contracts(handoff: dict[str, Any], variant: dict[str, Any]) -> dict[str, Any]:
    updated = deepcopy(handoff)
    inputs = updated.setdefault("presentation_inputs", {})
    if isinstance(inputs, dict):
        execution = _music_entity_execution_from_variant(variant)
        inputs["music_entity_execution"] = execution
        inputs["template_capability_match"] = deepcopy(execution.get("template_capability_match", {}))
        inputs["lesson_alignment_result"] = deepcopy(variant.get("lesson_alignment_result", {}))
        inputs["template_fidelity_result"] = deepcopy(variant.get("template_fidelity_result", {}))
        inputs["lesson_slot_coverage_result"] = deepcopy(variant.get("lesson_slot_coverage_result", {}))
    return updated


def _music_entity_execution_from_variant(variant: dict[str, Any]) -> dict[str, Any]:
    return {
        "contract_schema_version": deepcopy(variant.get("contract_schema_version", "")),
        "music_entity": deepcopy(variant.get("music_entity", {})) if isinstance(variant.get("music_entity"), dict) else {},
        "variant_parameters": deepcopy(variant.get("variant_parameters", {}))
        if isinstance(variant.get("variant_parameters"), dict)
        else {},
        "slot_bindings": deepcopy(variant.get("slot_bindings", {})) if isinstance(variant.get("slot_bindings"), dict) else {},
        "entity_application": deepcopy(variant.get("entity_application", {}))
        if isinstance(variant.get("entity_application"), dict)
        else {},
        "material_entities": deepcopy(variant.get("material_entities", [])) if isinstance(variant.get("material_entities"), list) else [],
        "selected_entity": deepcopy(variant.get("selected_entity", {})) if isinstance(variant.get("selected_entity"), dict) else {},
        "template_capability_match": deepcopy(variant.get("template_capability_match", {}))
        if isinstance(variant.get("template_capability_match"), dict)
        else {},
        "execution_plan": deepcopy(variant.get("execution_plan", {})) if isinstance(variant.get("execution_plan"), dict) else {},
        "confirmation_gates": deepcopy(variant.get("confirmation_gates", []))
        if isinstance(variant.get("confirmation_gates"), list)
        else [],
        "teacher_confirmation_cards": deepcopy(variant.get("teacher_confirmation_cards", []))
        if isinstance(variant.get("teacher_confirmation_cards"), list)
        else [],
        "revision_history": deepcopy(variant.get("revision_history", [])) if isinstance(variant.get("revision_history"), list) else [],
        "lesson_contract_ref": deepcopy(variant.get("lesson_contract_ref", {}))
        if isinstance(variant.get("lesson_contract_ref"), dict)
        else {},
        "lesson_alignment_result": deepcopy(variant.get("lesson_alignment_result", {}))
        if isinstance(variant.get("lesson_alignment_result"), dict)
        else {},
        "template_fidelity_result": deepcopy(variant.get("template_fidelity_result", {}))
        if isinstance(variant.get("template_fidelity_result"), dict)
        else {},
        "lesson_slot_coverage_result": deepcopy(variant.get("lesson_slot_coverage_result", {}))
        if isinstance(variant.get("lesson_slot_coverage_result"), dict)
        else {},
    }


def _lesson_adaptation_from(
    proposal: dict[str, Any],
    lesson_analysis: dict[str, Any],
    lesson_context: dict[str, Any],
) -> dict[str, Any]:
    for value in (
        proposal.get("lesson_adaptation"),
        lesson_analysis.get("lesson_adaptation"),
        lesson_context.get("lesson_adaptation"),
    ):
        if isinstance(value, dict) and value:
            return value
    return {}


def _music_element_adjustment_from(
    proposal: dict[str, Any],
    lesson_analysis: dict[str, Any],
    lesson_context: dict[str, Any],
    lesson_fit: dict[str, Any],
) -> dict[str, Any]:
    for value in (
        proposal.get("music_element_adjustment_contract"),
        lesson_analysis.get("music_element_adjustment_contract"),
        lesson_context.get("music_element_adjustment_contract"),
        lesson_fit.get("music_element_adjustment_contract") if isinstance(lesson_fit, dict) else {},
    ):
        if isinstance(value, dict) and value:
            return value
    return {}


def _high_confidence_fit_template_id(lesson_fit: dict[str, Any]) -> str:
    template_hint = lesson_fit.get("template_hint", {}) if isinstance(lesson_fit.get("template_hint"), dict) else {}
    auto_match = template_hint.get("auto_template_match", {}) if isinstance(template_hint.get("auto_template_match"), dict) else {}
    template_id = str(auto_match.get("template_id") or "").strip()
    confidence = float(auto_match.get("confidence") or 0.0)
    if get_game_template(template_id) and confidence >= 0.75:
        return template_id
    return ""


def _choose_template(text: str, preferred: Any = None, *, allow_unmatched: bool = False) -> str:
    preferred_id = str(preferred or "").strip()
    if get_game_template(preferred_id):
        return preferred_id
    if any(
        keyword in text
        for keyword in (
            "拼图创编",
            "拼图创作",
            "节奏拼图",
            "节奏创编",
            "时值拼图",
            "旋律拼图",
            "旋律创作",
            "旋律创编",
            "旋律创造",
            "音级创编",
            "五声音阶创编",
            "旋律节奏拼图",
            "音符拼图",
            "旋律和节奏",
            "节奏卡",
            "拖拽拼成",
            "素材拼成",
            "创编工坊",
        )
    ):
        return "composition_puzzle_core"
    if "创编" in text and any(keyword in text for keyword in ("小节", "乐句", "旋律", "节奏", "作品", "AABA", "aaba")):
        return "composition_puzzle_core"
    if any(keyword in text for keyword in ("唱名打靶", "听音打靶", "击中", "靶心", "唱名靶")):
        return "solfege_target_core"
    scores = {
        template_id: sum(1 for keyword in keywords if keyword.lower() in text.lower())
        for template_id, keywords in TEMPLATE_KEYWORDS.items()
    }
    best_template, best_score = max(scores.items(), key=lambda item: item[1])
    if best_score > 0:
        return best_template
    return "" if allow_unmatched else "rhythm_echo_core"


def _config_from_text(
    template_id: str,
    text: str,
    options: dict[str, Any],
    *,
    source_kind: str,
) -> dict[str, Any]:
    difficulty = _choose_difficulty(text, options.get("difficulty") or options.get("difficulty_preset"))
    skin_id, skin_selection_source = _choose_skin_with_source(template_id, text, options.get("skin_id"))
    if skin_selection_source != "teacher_selected":
        skin_id = _choose_non_repeated_skin(template_id, skin_id, options)
    config: dict[str, Any] = {
        "template_id": template_id,
        "difficulty": difficulty,
        "skin_id": skin_id,
        "_skin_selection_source": skin_selection_source,
    }
    for key in ("grade_band", "music_concept", "meter", "mode", "teacher_prompt"):
        if options.get(key):
            config[key] = options[key]
    if source_kind == "lesson_game":
        config.setdefault("teacher_prompt", "先回到作品材料中听辨，再进入游戏操作，最后用演唱或演奏复盘。")
    if template_id == "beat_guardian_core":
        config.update(_beat_guardian_overrides(text, options))
    elif template_id == "pitch_ladder_core":
        config.update(_pitch_ladder_overrides(text, options))
    elif template_id == "solfege_target_core":
        config.update(_solfege_target_overrides(text, options))
    elif template_id == "timbre_detective_core":
        config.update(_timbre_detective_overrides(text, options))
    elif template_id == "form_treasure_core":
        config.update(_form_treasure_overrides(text, options))
    elif template_id == "composition_puzzle_core":
        config.update(_composition_puzzle_overrides(text, options))
    else:
        config.update(_rhythm_echo_overrides(text, options))
    config.update(_confirmed_music_element_overrides(template_id, options))
    config.update(_template_instance_copy_overrides(options))
    config["template_id"] = template_id
    config["difficulty"] = difficulty
    config["skin_id"] = skin_id
    config["_skin_selection_source"] = skin_selection_source
    return config


def _confirmed_music_element_overrides(template_id: str, options: dict[str, Any]) -> dict[str, Any]:
    overrides = filter_template_config_overrides(template_id, options)
    for routing_key in ("template_id", "difficulty", "skin_id"):
        overrides.pop(routing_key, None)
    return overrides


def _template_instance_copy_overrides(options: dict[str, Any]) -> dict[str, Any]:
    allowed = ("student_task_copy", "music_reason_prompts", "result_transfer_prompt")
    return {key: deepcopy(options[key]) for key in allowed if key in options}


def _protect_explicit_lesson_options(patch_options: dict[str, Any], options: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(patch_options, dict):
        return {}
    explicit = {key for key, value in options.items() if _has_explicit_option_value(value)}
    if "difficulty" in patch_options and "difficulty_preset" in explicit:
        explicit.add("difficulty")
    return {key: value for key, value in patch_options.items() if key not in explicit}


def _has_explicit_option_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict, set, tuple)):
        return bool(value)
    return True


def _choose_difficulty(text: str, preferred: Any = None) -> str:
    candidate = str(preferred or "").strip().upper()
    if candidate in {"L1", "L2", "L3", "L4", "L5"}:
        return candidate
    if any(word in text for word in ("一年级", "低年级", "入门", "简单", "初学")):
        return "L1"
    if any(word in text for word in ("五年级", "六年级", "高年级", "挑战", "较难")):
        return "L4"
    if any(word in text for word in ("三年级", "四年级", "中段")):
        return "L3"
    return "L2"


def _choose_skin(template_id: str, text: str, preferred: Any = None) -> str:
    return _choose_skin_with_source(template_id, text, preferred)[0]


def _choose_skin_with_source(template_id: str, text: str, preferred: Any = None) -> tuple[str, str]:
    preferred_id = str(preferred or "").strip()
    preferred_skin = get_game_skin(preferred_id)
    if preferred_skin and preferred_skin.get("template_id") == template_id:
        return preferred_id, "teacher_selected"
    recommended: list[tuple[int, str]] = []
    for skin_id, keywords in SKIN_KEYWORDS.items():
        skin = get_game_skin(skin_id)
        if skin and skin.get("template_id") == template_id:
            score = sum(1 for keyword in keywords if keyword in text)
            if score:
                recommended.append((score, skin_id))
    if recommended:
        recommended.sort(key=lambda item: (-item[0], item[1]))
        return recommended[0][1], "lesson_recommended"
    template = get_game_template(template_id) or {}
    default_skin = str((template.get("default_config") or {}).get("skin_id") or "")
    if get_game_skin(default_skin):
        return default_skin, "template_default"
    skins = list_game_skins(template_id)
    return (str(skins[0]["skin_id"]), "template_default") if skins else ("", "template_default")


def _choose_non_repeated_skin(template_id: str, preferred_skin_id: str, options: dict[str, Any]) -> str:
    """Rotate the skin-backed experience when callers provide recent generation history."""

    recent_variant_ids = {str(item) for item in options.get("recent_experience_variant_ids", []) if str(item).strip()}
    recent_skin_ids = {str(item) for item in options.get("recent_skin_ids", []) if str(item).strip()}
    recent_play_modes = {str(item) for item in options.get("recent_play_modes", []) if str(item).strip()}
    recent_skin_families = {str(item) for item in options.get("recent_skin_families", []) if str(item).strip()}
    if not (recent_variant_ids or recent_skin_ids or recent_play_modes or recent_skin_families):
        return preferred_skin_id
    preferred_variant = get_experience_variant(preferred_skin_id, template_id) or {}
    if (
        preferred_skin_id
        and preferred_skin_id not in recent_skin_ids
        and preferred_variant.get("experience_variant_id") not in recent_variant_ids
        and preferred_variant.get("play_mode") not in recent_play_modes
        and preferred_variant.get("skin_family") not in recent_skin_families
    ):
        return preferred_skin_id
    skins_by_variant = {
        skin.get("experience_variant_id"): skin.get("skin_id")
        for skin in list_game_skins(template_id)
        if skin.get("experience_variant_id") and skin.get("skin_id")
    }
    for variant in list_experience_variants(template_id):
        skin_id = str(skins_by_variant.get(variant.get("experience_variant_id")) or "")
        if not skin_id:
            continue
        if skin_id in recent_skin_ids:
            continue
        if variant.get("experience_variant_id") in recent_variant_ids:
            continue
        if variant.get("play_mode") in recent_play_modes:
            continue
        if variant.get("skin_family") in recent_skin_families:
            continue
        return skin_id
    return preferred_skin_id


def _skin_selection_source_from_config(config: dict[str, Any]) -> str:
    source = str(config.get("_skin_selection_source") or "")
    if source in {"teacher_selected", "lesson_recommended", "template_default"}:
        return source
    return "template_default"


def _beat_guardian_overrides(text: str, options: dict[str, Any]) -> dict[str, Any]:
    overrides: dict[str, Any] = {}
    if "三拍" in text or "3/4" in text:
        overrides["meter"] = "3/4"
    elif "二拍" in text or "2/4" in text or "龙舟" in text:
        overrides["meter"] = "2/4"
    if "每拍" in text:
        overrides["mode"] = "beat_defense"
        overrides["target_beats"] = [1, 2]
    elif "拍号" in text:
        overrides["mode"] = "meter_gate"
    if options.get("target_beats"):
        overrides["target_beats"] = options["target_beats"]
    for key in (
        "audio_mode",
        "lesson_audio_sync",
        "student_ui_mode",
        "teacher_panel_mode",
        "feedback_style",
        "strong_beat_sound",
        "weak_beat_sound",
    ):
        if options.get(key):
            overrides[key] = options[key]
    return overrides


def _lesson_audio_sync_from(
    *,
    lesson_source: dict[str, Any],
    lesson_context: dict[str, Any],
    material_binding: dict[str, Any],
    options: dict[str, Any],
) -> dict[str, Any]:
    explicit = options.get("lesson_audio_sync")
    if isinstance(explicit, dict) and explicit.get("audio_url"):
        return deepcopy(explicit)
    audio_url = (
        material_binding.get("audio_clip_url")
        or material_binding.get("source_audio_url")
        or lesson_context.get("audio_clip_url")
        or lesson_context.get("source_audio_url")
        or lesson_source.get("audio_clip_url")
        or lesson_source.get("source_audio_url")
        or lesson_source.get("audio_url")
    )
    if not audio_url:
        return {}
    return {
        "audio_url": audio_url,
        "bpm": material_binding.get("bpm") or lesson_context.get("bpm") or options.get("bpm"),
        "meter": material_binding.get("meter") or lesson_context.get("meter") or options.get("meter"),
        "offset_ms": material_binding.get("offset_ms") or lesson_context.get("offset_ms") or 0,
        "segment_label": material_binding.get("selected_phrase_label") or lesson_context.get("target_stage") or "作品片段",
    }


def _pitch_ladder_overrides(text: str, options: dict[str, Any]) -> dict[str, Any]:
    overrides: dict[str, Any] = {}
    if not options.get("mode"):
        if any(word in text for word in ("唱名", "do", "re", "mi")):
            overrides["mode"] = "solfege_ladder"
        if any(word in text for word in ("旋律", "短句", "音列")):
            overrides["mode"] = "melody_climb"
    if options.get("pitch_range"):
        overrides["pitch_range"] = options["pitch_range"]
    return overrides


def _rhythm_echo_overrides(text: str, options: dict[str, Any]) -> dict[str, Any]:
    overrides: dict[str, Any] = {}
    if any(word in text for word in ("身体", "拍腿", "跺脚")):
        overrides["mode"] = "echo_body_percussion"
        overrides["input_method"] = "body_percussion"
    if "接龙" in text or "创编" in text:
        overrides["mode"] = "echo_chain"
    for key in ("bpm", "bars_per_round", "timing_tolerance_ms"):
        if options.get(key) is not None:
            overrides[key] = options[key]
    return overrides


def _solfege_target_overrides(text: str, options: dict[str, Any]) -> dict[str, Any]:
    overrides: dict[str, Any] = {}
    if any(word in text for word in ("唱回", "模唱", "内听")):
        overrides["require_sing_back"] = True
    if options.get("target_solfege"):
        overrides["target_solfege"] = options["target_solfege"]
    return overrides


def _timbre_detective_overrides(text: str, options: dict[str, Any]) -> dict[str, Any]:
    overrides: dict[str, Any] = {}
    if any(word in text for word in ("家族", "管乐", "弦乐", "打击乐")):
        overrides["mode"] = "family_sorting"
    for key in ("instrument_pool", "timbre_traits", "choices_per_round", "evidence_required", "ai_clue_enabled", "audio_mode"):
        if options.get(key) is not None:
            overrides[key] = options[key]
    return overrides


def _form_treasure_overrides(text: str, options: dict[str, Any]) -> dict[str, Any]:
    overrides: dict[str, Any] = {}
    if "回旋" in text:
        overrides["form_type"] = "回旋"
        overrides["mode"] = "rondo_treasure"
    elif "重复对比" in text or "重复与对比" in text:
        overrides["form_type"] = "重复对比"
        overrides["mode"] = "repeat_contrast"
    elif "ABA" in text.upper():
        overrides["form_type"] = "ABA"
        overrides["mode"] = "aba_treasure"
    for key in ("form_type", "section_length_bars", "hint_mode", "round_count", "audio_mode"):
        if options.get(key) is not None:
            overrides[key] = options[key]
    return overrides


def _composition_puzzle_overrides(text: str, options: dict[str, Any]) -> dict[str, Any]:
    overrides: dict[str, Any] = {}
    if any(word in text for word in ("旋律节奏拼图", "音符拼图", "旋律和节奏", "综合", "节奏卡", "节奏素材", "时值卡")):
        overrides["mode"] = "melody_rhythm_puzzle"
    elif any(word in text for word in ("旋律拼图", "旋律创作", "旋律创编", "旋律创造", "五声音阶创编", "音级创编", "唱名创作")):
        overrides["mode"] = "melody_puzzle_creation"
    elif any(word in text for word in ("节奏拼图", "节奏创编", "时值拼图", "休止", "切分", "附点")):
        overrides["mode"] = "rhythm_puzzle_composition"
    length_intent = _extract_composition_length_intent(text)
    meter_intent = _extract_composition_meter_intent(text)
    for key in (
        "mode",
        "phrase_length_bars",
        "composition_total_bars",
        "composition_segment_bars",
        "slots_per_bar",
        "constraint_profile",
        "rhythm_cards",
        "melody_cards",
        "teacher_confirm_required",
        "audio_mode",
    ):
        if options.get(key) is not None:
            overrides[key] = options[key]
    if length_intent:
        overrides.update(length_intent)
    if meter_intent:
        overrides.update(meter_intent)
    return overrides


def _extract_composition_length_intent(text: str) -> dict[str, Any]:
    compact = re.sub(r"\s+", "", str(text or ""))
    if not compact:
        return {}
    pair_patterns = (
        r"(?P<count>[0-9一二两三四五六七八九十百]+)(?:句|个乐句|个段落|段)各(?P<bars>[0-9一二两三四五六七八九十百]+)小节",
        r"(?P<count>[0-9一二两三四五六七八九十百]+)(?:个)?乐句每句(?P<bars>[0-9一二两三四五六七八九十百]+)小节",
        r"(?P<count>[0-9一二两三四五六七八九十百]+)(?:个)?段(?:落)?每段(?P<bars>[0-9一二两三四五六七八九十百]+)小节",
    )
    for pattern in pair_patterns:
        match = re.search(pattern, compact)
        if not match:
            continue
        count = _parse_chinese_or_arabic_int(match.group("count"))
        bars = _parse_chinese_or_arabic_int(match.group("bars"))
        if count and bars:
            return _composition_length_contract(count * bars, preferred_segment_bars=bars)
    form_match = re.search(r"每段(?P<bars>[0-9一二两三四五六七八九十百]+)小节.*?(?P<form>[A-G]{2,})", compact, re.IGNORECASE)
    if form_match:
        bars = _parse_chinese_or_arabic_int(form_match.group("bars"))
        form = form_match.group("form")
        if bars and form:
            return _composition_length_contract(bars * len(form), preferred_segment_bars=bars)
    single_match = re.search(r"(?P<bars>[0-9一二两三四五六七八九十百]+)小节", compact)
    if single_match:
        bars = _parse_chinese_or_arabic_int(single_match.group("bars"))
        if bars:
            return _composition_length_contract(bars)
    return {}


def _composition_length_contract(total_bars: int, *, preferred_segment_bars: int | None = None) -> dict[str, Any]:
    total = max(1, min(32, int(total_bars)))
    segment = preferred_segment_bars if preferred_segment_bars else min(4, total)
    segment = max(1, min(4, total, int(segment)))
    return {
        "composition_total_bars": total,
        "composition_segment_bars": segment,
        "phrase_length_bars": segment,
        "length_clamped": total != int(total_bars),
    }


def _extract_composition_meter_intent(text: str) -> dict[str, Any]:
    compact = re.sub(r"\s+", "", str(text or ""))
    match = re.search(r"每小节(?P<beats>[0-9一二两三四五六七八九十]+)拍", compact)
    if not match:
        return {}
    beats = _parse_chinese_or_arabic_int(match.group("beats"))
    if beats in {2, 3, 4}:
        return {"meter": f"{beats}/4", "slots_per_bar": beats}
    return {}


def _parse_chinese_or_arabic_int(value: str) -> int | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    if raw.isdigit():
        return int(raw)
    digits = {"零": 0, "〇": 0, "一": 1, "二": 2, "两": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
    if raw in digits:
        return digits[raw]
    if "百" in raw:
        left, _, right = raw.partition("百")
        hundred = digits.get(left, 1 if not left else 0)
        remainder = _parse_chinese_or_arabic_int(right) if right else 0
        return hundred * 100 + (remainder or 0)
    if "十" in raw:
        left, _, right = raw.partition("十")
        tens = digits.get(left, 1 if not left else 0)
        ones = digits.get(right, 0) if right else 0
        return tens * 10 + ones
    if all(char in digits for char in raw):
        number = 0
        for char in raw:
            number = number * 10 + digits[char]
        return number
    return None


def _unmatched_lesson_instance(options: dict[str, Any]) -> dict[str, Any]:
    return {
        "instance_id": "",
        "template_id": "",
        "template_label": "",
        "scaffold_id": "",
        "version": "",
        "status": "unmatched",
        "generation_mode": "lesson_specific_generation",
        "opencode_required": True,
        "config": {
            "grade_band": options.get("grade_band") or "小学",
            "music_concept": options.get("music_concept") or "综合音乐感知",
            "teacher_prompt": options.get("teacher_prompt") or "先回到作品材料中听辨，再围绕本课重点生成专属玩法。",
            "pass_score": 0.8,
        },
        "skin": {},
        "student_task": {
            "listen": "先回到作品材料中听辨本课重点",
            "do": "完成与教案目标一致的专属操作",
            "pass": "说出音乐依据，并回到课堂任务",
        },
        "scoring": {},
        "feedback_rules": {},
    }


def _build_proposal_card(
    *,
    workflow_kind: str,
    template_id: str,
    instance: dict[str, Any],
    source_text: str,
    source_summary: str,
    lesson_context: dict[str, Any] | None = None,
    lesson_source: dict[str, Any] | None = None,
    lesson_fit: dict[str, Any] | None = None,
) -> dict[str, Any]:
    template = get_game_template(template_id) or {}
    config = instance["config"]
    skin = instance.get("skin") or {}
    fit = lesson_fit if isinstance(lesson_fit, dict) else {}
    fit_evidence = fit.get("lesson_evidence", {}) if isinstance(fit.get("lesson_evidence"), dict) else {}
    material_binding = fit.get("material_binding", {}) if isinstance(fit.get("material_binding"), dict) else {}
    music_concept = config.get("music_concept") or _infer_music_concept(template_id)
    experience_variant = (
        config.get("experience_variant")
        if isinstance(config.get("experience_variant"), dict)
        else get_experience_variant(str(config.get("skin_id") or ""), template_id) or {}
    )
    return {
        "title": (
            f"{skin.get('label') or template.get('label')} · {template.get('label')}"
            if template_id
            else "教案专属玩法 · 待生成"
        ),
        "workflow_kind": workflow_kind,
        "source_summary": source_summary,
        "learning_goal": _learning_goal(template_id, str(music_concept)),
        "music_element": music_concept,
        "template_id": template_id,
        "template_label": template.get("label"),
        "skin_id": config.get("skin_id"),
        "skin_label": skin.get("label"),
        "experience_variant_id": config.get("experience_variant_id") or experience_variant.get("experience_variant_id", ""),
        "play_mode": config.get("skin_play_mode") or experience_variant.get("play_mode", ""),
        "scene_goal": experience_variant.get("scene_goal", ""),
        "student_mission": experience_variant.get("student_mission", ""),
        "why_this_variant": experience_variant.get("teacher_reason", ""),
        "difficulty": config.get("difficulty"),
        "grade_band": config.get("grade_band"),
        "student_actions": template.get("student_actions", []),
        "core_loop": template.get("core_loop", []),
        "teacher_review_points": _teacher_review_points(workflow_kind),
        "lesson_fit": deepcopy(fit),
        "material_binding": deepcopy(material_binding),
        "transfer_task": fit.get("transfer_task", ""),
        "fit_summary": fit.get("fit_summary", ""),
        "evidence": {
            "source_text": source_text[:500],
            "target_objective": fit_evidence.get("target_objective", ""),
            "target_stage": fit_evidence.get("target_stage", ""),
            "segment_task": fit_evidence.get("segment_task", ""),
            "lesson_context": deepcopy(lesson_context or {}),
            "lesson_source": deepcopy(lesson_source or {}),
        },
    }


def _quality_gates(
    workflow_kind: str,
    proposal_card: dict[str, Any],
    instance: dict[str, Any],
    source: dict[str, Any],
    *,
    gameplay_blueprint: dict[str, Any],
    experience_script: dict[str, Any],
    theme_pack: dict[str, Any],
    render_spec: dict[str, Any],
    delivery_decision: dict[str, Any],
    lesson_adaptation: dict[str, Any],
    template_decision: dict[str, Any],
    frontend_handoff_contract: dict[str, Any],
    opencode_role_policy: dict[str, Any],
    template_fidelity_contract: dict[str, Any],
    lesson_alignment_result: dict[str, Any],
    template_fidelity_result: dict[str, Any],
    lesson_slot_coverage_result: dict[str, Any],
) -> list[dict[str, str]]:
    config = instance.get("config", {})
    student_task = instance.get("student_task", {})
    template = get_game_template(str(instance.get("template_id") or "")) or {}
    gates = [
        _gate(
            "chain_separation",
            "链路隔离",
            "pass" if proposal_card.get("workflow_kind") == workflow_kind else "fail",
            f"当前只走 {workflow_kind}，不会混用另一条入口。",
        ),
        _gate(
            "template_reuse",
            "模板复用",
            "pass"
            if instance.get("generation_mode") == "template_config" and not instance.get("opencode_required")
            else "warning",
            "主链路使用模板配置生成，OpenCode 仅作为未来兜底。"
            if instance.get("generation_mode") == "template_config"
            else "当前教学重点暂无成熟模板，改走教案专属生成以避免误配。",
        ),
        _gate(
            "student_learning_behavior",
            "学生真实学习行为",
            "pass" if student_task.get("listen") and student_task.get("do") and student_task.get("pass") else "fail",
            "任务包含先听、操作判断、复盘表达，不替代学生学习。",
        ),
        _gate(
            "music_element_grounding",
            "音乐要素锚定",
            "pass" if config.get("music_concept") else "fail",
            f"锚定音乐要素：{config.get('music_concept') or '缺失'}。",
        ),
        _gate(
            "skin_variation",
            "审美皮肤差异",
            "pass" if instance.get("skin", {}).get("skin_id") else "warning",
            f"已选择皮肤：{instance.get('skin', {}).get('label') or '未选择'}。",
        ),
        _gate(
            "template_fidelity_contract",
            "模板骨架保真",
            "pass"
            if template_fidelity_contract.get("template_fidelity_pass")
            else "warning"
            if not instance.get("template_id")
            else "fail",
            (
                f"{template_fidelity_contract.get('template_id') or '未知模板'} / "
                f"{template_fidelity_contract.get('runtime_shell') or '缺少运行壳'} / "
                f"皮肤 {template_fidelity_contract.get('selected_skin_id') or '未选择'}。"
            ),
        ),
        *(
            [
                _gate(
                    "lesson_alignment_gate",
                    "教案贴合门禁",
                    "pass" if lesson_alignment_result.get("status") == "pass" else "fail" if lesson_alignment_result.get("status") == "fail" else "warning",
                    lesson_alignment_result.get("teacher_message", "教案贴合门禁未生成。"),
                ),
                _gate(
                    "template_fidelity_gate",
                    "模板保真门禁",
                    "pass" if template_fidelity_result.get("status") == "pass" else "fail",
                    template_fidelity_result.get("teacher_message", "模板保真门禁未生成。"),
                ),
                _gate(
                    "lesson_slot_coverage_gate",
                    "玩法覆盖门禁",
                    "pass"
                    if lesson_slot_coverage_result.get("status") == "pass"
                    else "fail"
                    if lesson_slot_coverage_result.get("status") == "fail"
                    else "warning",
                    lesson_slot_coverage_result.get("teacher_message", "玩法覆盖门禁未生成。"),
                ),
            ]
            if workflow_kind == "lesson_game"
            else []
        ),
        _gate(
            "anti_homogeneity_variant",
            "反同质化体验变体",
            "pass"
            if config.get("experience_variant_id")
            and config.get("scene_goal")
            and config.get("interaction_feedback")
            and config.get("failure_feedback")
            and config.get("reward_loop")
            and config.get("playfield_composition")
            else "fail",
            f"变体：{config.get('experience_variant_id') or '缺失'}；玩法结构：{config.get('playfield_composition') or '缺失'}。",
        ),
        _gate(
            "runtime_maturity",
            "运行时成熟度",
            "pass" if template.get("runtime_status") == "production" else "warning",
            "当前模板运行时可直接交付。" if template.get("runtime_status") == "production" else "当前仅为模板骨架，需经高质量生成后才能交付学生。",
        ),
        _music_game_skill_gate(source),
        _gate(
            "classroom_ready",
            "课堂可用参数",
            "pass"
            if config.get("grade_band") and config.get("teacher_prompt") and config.get("pass_score")
            else "warning",
            "包含学段、教师提示和通关标准，可进入课堂试教。",
        ),
        _gate(
            "gameplay_blueprint_ready",
            "玩法蓝图完整",
            "pass" if gameplay_blueprint.get("player_verb") and gameplay_blueprint.get("rounds") else "fail",
            f"学生动作为：{gameplay_blueprint.get('player_verb') or '缺失'}。",
        ),
        _gate(
            "experience_directed",
            "体验导演完成",
            "pass" if experience_script.get("opening_hook") and experience_script.get("closure_prompt") else "fail",
            experience_script.get("opening_hook") or "缺少开场钩子。",
        ),
        _gate(
            "theme_pack_ready",
            "主题包装完成",
            "pass" if theme_pack.get("theme_name") and theme_pack.get("palette") else "fail",
            f"主题：{theme_pack.get('theme_name') or '缺失'}。",
        ),
        _gate(
            "render_spec_student_ready",
            "学生页渲染规格",
            "pass"
            if render_spec.get("artifact_type") == "student_game"
            and render_spec.get("screen_structure", {}).get("playfield", {}).get("priority") == "primary"
            else "fail",
            "学生模式以主游戏舞台为中心。",
        ),
        _gate(
            "delivery_gate",
            "交付门禁",
            "pass" if delivery_decision.get("status") == "approved" else "fail",
            "；".join(delivery_decision.get("reasons", [])) or "交付门禁未通过。",
        ),
        _gate(
            "template_decision_explicit",
            "模板职责明确",
            "pass" if template_decision.get("owner") == "template_mechanism_router" else "fail",
            f"模板决策：{template_decision.get('decision') or '缺失'}。",
        ),
        _gate(
            "frontend_handoff_scoped",
            "前端交接边界",
            "pass" if frontend_handoff_contract.get("locked_inputs") and frontend_handoff_contract.get("allowed_changes") else "fail",
            f"前端模式：{frontend_handoff_contract.get('mode') or '缺失'}。",
        ),
        _gate(
            "opencode_runtime_isolation",
            "OpenCode 角色隔离",
            "pass" if opencode_regular_path_is_isolated(opencode_role_policy) else "fail",
            opencode_role_policy.get("realtime_opencode", {}).get("reason", ""),
        ),
    ]
    gates.extend(build_blueprint_quality_gates(str(instance.get("template_id") or ""), config))
    if instance.get("template_id") == "beat_guardian_core":
        scene_config = config.get("scene_config", {}) if isinstance(config.get("scene_config"), dict) else {}
        gates.append(
            _gate(
                "beat_guardian_game_first_runtime",
                "节拍守卫学生端门禁",
                "pass"
                if config.get("student_ui_mode") == "game_first"
                and config.get("game_feel") == "arcade_rhythm"
                and config.get("runtime_shell") == "beat_guardian_shell"
                and scene_config.get("minimal_hud") is True
                and scene_config.get("arcade_hud") is True
                and scene_config.get("show_teacher_text_in_play") is False
                and isinstance(scene_config.get("score_model"), dict)
                and config.get("feedback_style") == "short_student_facing"
                and scene_config.get("audio_mode") in {"internal_meter", "lesson_audio", "hybrid"}
                else "fail",
                "节拍守卫必须走专属街机壳、短反馈、能量判定和节拍音频配置。",
            )
        )
    if instance.get("template_id") == "rhythm_echo_core":
        scene_config = config.get("scene_config", {}) if isinstance(config.get("scene_config"), dict) else {}
        gates.append(
            _gate(
                "rhythm_echo_arcade_runtime",
                "节奏复刻学生端门禁",
                "pass"
                if config.get("student_ui_mode") == "game_first"
                and config.get("game_feel") == "arcade_rhythm_echo"
                and config.get("runtime_shell") == "rhythm_echo_shell"
                and scene_config.get("arcade_hud") is True
                and scene_config.get("show_teacher_text_in_play") is False
                and isinstance(scene_config.get("pattern_timeline"), list)
                and isinstance(scene_config.get("score_model"), dict)
                and scene_config.get("audio_mode") in {"internal_pattern", "lesson_audio", "hybrid"}
                else "fail",
                "节奏复刻必须走专属街机壳、节奏时间轴、短反馈、能量判定和节奏音频配置。",
            )
        )
    if instance.get("template_id") == "pitch_ladder_core":
        scene_config = config.get("scene_config", {}) if isinstance(config.get("scene_config"), dict) else {}
        gates.append(
            _gate(
                "pitch_ladder_map_runtime",
                "音高爬梯学生端门禁",
                "pass"
                if config.get("student_ui_mode") == "game_first"
                and config.get("engine") == "phaser_2d"
                and config.get("scene_id") == "pitch_ladder_scene"
                and config.get("game_feel") == "map_pitch_climb"
                and config.get("game_experience") == "adventure_climb"
                and config.get("first_screen_density") == "playfield_only"
                and config.get("runtime_shell") == "pitch_ladder_map_shell"
                and scene_config.get("map_hud") is True
                and scene_config.get("adventure_hud") is True
                and scene_config.get("show_mission_ribbon_in_play") is False
                and scene_config.get("show_teacher_text_in_play") is False
                and isinstance(scene_config.get("character_profile"), dict)
                and isinstance(scene_config.get("reward_model"), dict)
                and isinstance(scene_config.get("fail_pressure_model"), dict)
                and scene_config.get("route_objective") in {"summit", "cloud_gate", "bamboo_crown", "lantern_beacon"}
                and isinstance(scene_config.get("route_nodes"), list)
                and isinstance(scene_config.get("pitch_rounds"), list)
                and scene_config.get("audio_mode") in {"internal_pitch", "lesson_audio", "hybrid"}
                else "fail",
                "音高爬梯必须走 Phaser 冒险地图壳、低文字首屏、角色、奖励和失败压力配置。",
            )
        )
    if instance.get("template_id") == "solfege_target_core":
        scene_config = config.get("scene_config", {}) if isinstance(config.get("scene_config"), dict) else {}
        gates.append(
            _gate(
                "solfege_target_range_runtime",
                "唱名打靶学生端门禁",
                "pass"
                if config.get("student_ui_mode") == "game_first"
                and config.get("engine") == "phaser_2d"
                and config.get("scene_id") == "solfege_target_scene"
                and config.get("game_feel") == "solfege_target_range"
                and config.get("runtime_shell") == "solfege_target_shell"
                and scene_config.get("target_hud") is True
                and scene_config.get("show_teacher_text_in_play") is False
                and scene_config.get("mic_assist_enabled") is True
                and scene_config.get("sing_back_required") is True
                and isinstance(scene_config.get("target_layout"), list)
                and isinstance(scene_config.get("solfege_rounds"), list)
                and scene_config.get("arcade_play_model") == "bubble_target_chain"
                and isinstance(scene_config.get("asset_role_map"), dict)
                and isinstance(scene_config.get("target_motion_profile"), dict)
                and isinstance(scene_config.get("score_model"), dict)
                and scene_config.get("audio_mode") in {"internal_pitch", "lesson_audio", "hybrid"}
                else "fail",
                "唱名打靶必须走 Phaser 泡泡靶场壳、点靶发射、资产角色链、麦克风辅助和唱回复盘配置。",
            )
        )
    if instance.get("template_id") == "timbre_detective_core":
        scene_config = config.get("scene_config", {}) if isinstance(config.get("scene_config"), dict) else {}
        gates.append(
            _gate(
                "timbre_detective_scene_runtime",
                "音色侦探学生端门禁",
                "pass"
                if config.get("student_ui_mode") == "game_first"
                and config.get("engine") == "phaser_2d"
                and config.get("scene_id") == "timbre_detective_scene"
                and config.get("game_feel") == "animated_detective_caseboard"
                and config.get("runtime_shell") == "timbre_detective_shell"
                and config.get("interaction_model") == "listen_investigate_drag_evidence_submit"
                and scene_config.get("detective_hud") is True
                and scene_config.get("dynamic_case_scene") is True
                and scene_config.get("show_teacher_text_in_play") is False
                and scene_config.get("ai_clue_policy") == "teacher_assist_only"
                and scene_config.get("teacher_assist_only") is True
                and isinstance(scene_config.get("input_actions"), list)
                and isinstance(scene_config.get("fx_profile"), dict)
                and isinstance(scene_config.get("score_model"), dict)
                and isinstance(scene_config.get("clue_cases"), list)
                and isinstance(scene_config.get("suspect_cards"), list)
                and isinstance(scene_config.get("evidence_tokens"), list)
                and scene_config.get("audio_mode") in {"internal_timbre", "lesson_audio", "hybrid"}
                else "fail",
                "音色侦探必须走 Phaser 动态侦探桌、程序化声纹、嫌疑卡、证据飞贴、破案印章和教师辅助 AI 兜底。",
            )
        )
    if instance.get("template_id") == "form_treasure_core":
        scene_config = config.get("scene_config", {}) if isinstance(config.get("scene_config"), dict) else {}
        gates.append(
            _gate(
                "form_treasure_runtime",
                "曲式寻宝学生端门禁",
                "pass"
                if config.get("student_ui_mode") == "game_first"
                and config.get("engine") == "phaser_2d"
                and config.get("scene_id") == "form_treasure_scene"
                and config.get("game_feel") == "form_treasure_hunt"
                and config.get("runtime_shell") == "form_treasure_shell"
                and config.get("interaction_model") == "listen_place_card_use_tool_verify"
                and config.get("publish_quality_profile") == "arcade_h5"
                and scene_config.get("form_hud") is True
                and scene_config.get("dynamic_map_scene") is True
                and scene_config.get("publish_quality_profile") == "arcade_h5"
                and scene_config.get("show_teacher_text_in_play") is False
                and isinstance(scene_config.get("input_actions"), list)
                and "place_card" in scene_config.get("input_actions", [])
                and "use_tool" in scene_config.get("input_actions", [])
                and isinstance(scene_config.get("fx_profile"), dict)
                and "treasure_unlock" in scene_config.get("fx_profile", {})
                and isinstance(scene_config.get("score_model"), dict)
                and isinstance(scene_config.get("asset_manifest"), dict)
                and isinstance(scene_config.get("timeline_segments"), list)
                and isinstance(scene_config.get("structure_cards"), list)
                and isinstance(scene_config.get("answer_pattern"), list)
                and isinstance(scene_config.get("progress_model"), dict)
                and scene_config.get("hint_mode") in {"guided", "partial", "challenge"}
                else "fail",
                "曲式寻宝必须走 Phaser 动态藏宝地图、可放置结构卡、工具提示、奖励特效和发布级 H5 门禁。",
            )
        )
    if workflow_kind == "lesson_game":
        lesson_context = source.get("lesson_context", {})
        lesson_fit = source.get("lesson_fit", {}) if isinstance(source.get("lesson_fit"), dict) else {}
        material_binding = lesson_fit.get("material_binding", {}) if isinstance(lesson_fit.get("material_binding"), dict) else {}
        gates.append(
            _gate(
                "lesson_adaptation_ready",
                "教案适配完成",
                "pass" if lesson_adaptation.get("owner") == "lesson_fit_director" else "fail",
                lesson_adaptation.get("responsibility") or "缺少教案适配层。",
            )
        )
        gates.append(
            _gate(
                "lesson_material_trace",
                "教案材料追溯",
                "pass" if lesson_fit or lesson_context or source.get("lesson_source") else "warning",
                "方案保留教案贴合层、教案上下文和材料依据。",
            )
        )
        gates.append(
            _gate(
                "song_or_phrase_binding",
                "作品片段绑定",
                "pass" if material_binding.get("selected_phrase_label") or material_binding.get("target_sequence") else "warning",
                lesson_fit.get("fit_summary") or "尚未绑定到具体乐句，建议教师补充谱例、音频或文字谱。",
            )
        )
        gates.append(
            _gate(
                "transfer_closure",
                "游戏后回到课堂",
                "pass" if lesson_fit.get("transfer_task") else "warning",
                lesson_fit.get("transfer_task") or "需要补充唱一唱、拍一拍、说一说或创编展示。",
            )
        )
    return gates


def _music_game_skill_gate(source: dict[str, Any]) -> dict[str, str]:
    production = (
        source.get("music_game_production_spec")
        if isinstance(source.get("music_game_production_spec"), dict)
        else {}
    )
    runtime_config = production.get("runtime_config") if isinstance(production.get("runtime_config"), dict) else {}
    qa_report = production.get("qa_report") if isinstance(production.get("qa_report"), dict) else {}
    audio_manifest = production.get("audio_manifest") if isinstance(production.get("audio_manifest"), dict) else {}
    music_truth = production.get("music_truth") if isinstance(production.get("music_truth"), dict) else {}
    has_audio = isinstance(audio_manifest.get("sounds"), list) and bool(audio_manifest.get("sounds"))
    status = (
        "pass"
        if production.get("version") == "music_game_production_spec_v1"
        and production.get("production_status") == "ready_for_runtime"
        and music_truth.get("truth_status") in {"usable", "draft"}
        and has_audio
        and runtime_config.get("production_package_ref") == production.get("package_id")
        and qa_report.get("status") == "pass"
        else "fail"
    )
    return _gate(
        "music_game_skill_production_package",
        "游戏生产包合同",
        status,
        "MusicGameSkill 已输出玩法、音乐真值、声音、运行时、教师控制和 QA 合同。"
        if status == "pass"
        else "MusicGameSkill 生产包缺失或仍被音乐真值/QA 阻断。",
    )


def _template_match(instance: dict[str, Any]) -> dict[str, Any]:
    template_id = str(instance.get("template_id") or "")
    template = get_game_template(template_id) or {}
    return {
        "template_id": template_id,
        "template_label": template.get("label", ""),
        "family": template.get("family", ""),
        "match_status": "exact" if template_id else "unmatched",
        "match_reason": "已根据教学重点或直接需求选择最合适的玩法内核。"
        if template_id
        else "当前重点暂无可精确复用的成熟玩法内核。",
        "core_mechanic": template.get("description", ""),
        "experience_variant_id": instance.get("config", {}).get("experience_variant_id", ""),
        "play_mode": instance.get("config", {}).get("skin_play_mode", ""),
        "variant_reason": instance.get("config", {}).get("template_match_reason", ""),
        "supported_operations": template.get("supported_modes", []),
        "default_parameters": deepcopy(template.get("default_config", {})),
    }


def _direct_template_decision(instance: dict[str, Any]) -> dict[str, Any]:
    template_id = str(instance.get("template_id") or "")
    template = get_game_template(template_id) or {}
    return {
        "version": "template_decision_v1",
        "owner": "template_mechanism_router",
        "responsibility": "choose_reusable_gameplay_carrier_only",
        "decision": "exact_match" if template_id else "unmatched",
        "template_id": template_id,
        "template_label": template.get("label", ""),
        "match_status": "exact" if template_id else "unmatched",
        "config_overrides": {},
        "owns": ["模板选择", "模板参数覆盖建议", "模板命中状态"],
        "must_not_do": ["不改写教学目标", "不改写音乐答案", "不决定最终前端表现"],
    }


def _responsibility_map(
    *,
    workflow_kind: str,
    lesson_adaptation: dict[str, Any],
    template_decision: dict[str, Any],
    frontend_handoff_contract: dict[str, Any],
) -> dict[str, Any]:
    return {
        "workflow_kind": workflow_kind,
        "lesson_fit_director": {
            "active": workflow_kind == "lesson_game",
            "owns": lesson_adaptation.get("owns", []),
            "must_not_do": lesson_adaptation.get("must_not_do", []),
        },
        "template_mechanism_router": {
            "active": True,
            "owns": template_decision.get("owns", []),
            "must_not_do": template_decision.get("must_not_do", []),
        },
        "frontend_presentation_director": {
            "active": True,
            "allowed_changes": frontend_handoff_contract.get("allowed_changes", []),
            "locked_inputs": frontend_handoff_contract.get("locked_inputs", []),
        },
    }


def _gate(gate_id: str, label: str, status: str, detail: str) -> dict[str, str]:
    return {"id": gate_id, "label": label, "status": status, "detail": detail}


def _learning_goal(template_id: str, music_concept: str) -> str:
    if template_id == "beat_guardian_core":
        return f"学生通过身体律动和提前预判掌握{music_concept}，形成稳定拍感。"
    if template_id == "pitch_ladder_core":
        return f"学生通过听、选、唱掌握{music_concept}，把音高关系迁移到演唱。"
    if template_id == "solfege_target_core":
        return f"学生通过听辨、击中和唱回掌握{music_concept}，把内听转化为声音。"
    if template_id == "timbre_detective_core":
        return f"学生通过听证据、作判断和说理由掌握{music_concept}。"
    if template_id == "composition_puzzle_core":
        return f"学生通过选材、拼接、试听和修正完成{music_concept}的约束创编，并能说明创作理由。"
    if not template_id:
        return f"学生围绕{music_concept}完成教案专属任务，并把判断迁移回课堂作品。"
    return f"学生通过聆听、复刻和修正掌握{music_concept}，提升节奏记忆与表现。"


def _teacher_review_points(workflow_kind: str) -> list[str]:
    if workflow_kind == "lesson_game":
        return ["是否贴合本课教学目标", "是否能使用上传乐谱或音频材料", "游戏结束是否回到演唱、演奏或欣赏表达"]
    return ["音乐要素是否明确", "难度是否适合目标学段", "皮肤是否带来新鲜感但不干扰学习"]


def _lesson_teacher_prompt(lesson_context: dict[str, Any], music_game: dict[str, Any]) -> str:
    objective = lesson_context.get("teaching_objective") or lesson_context.get("target_music_element") or ""
    mechanic = music_game.get("core_mechanic") or ""
    prompt = _compact_join([objective, mechanic])
    if prompt:
        return f"先带学生回到作品片段中听辨：{prompt}。游戏后请学生用唱、拍或说进行复盘。"
    return "先回到作品材料中听辨，再进入游戏操作，最后用演唱、演奏或语言复盘。"


def _infer_music_concept(template_id: str) -> str:
    if template_id == "beat_guardian_core":
        return "强拍与弱拍"
    if template_id == "pitch_ladder_core":
        return "音高高低与唱名"
    if template_id == "solfege_target_core":
        return "唱名听辨与模唱"
    if template_id == "timbre_detective_core":
        return "音色听辨与乐器识别"
    if template_id == "composition_puzzle_core":
        return "节奏与旋律创编"
    return "节奏型与时值"


def _compact_join(parts: list[Any]) -> str:
    return " ".join(str(part).strip() for part in parts if str(part or "").strip())
