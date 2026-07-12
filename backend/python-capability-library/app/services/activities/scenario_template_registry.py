# 定义课堂情景包装，例如场景图、角色、任务背景和素材策略
from __future__ import annotations

from copy import deepcopy
from typing import Any


SCENARIO_TEMPLATE_SPEC_VERSION = "scenario_template_spec_v1"

REQUIRED_FIELDS = (
    "version",
    "scenario_template_id",
    "label",
    "audience",
    "classroom_scenario",
    "composition",
    "image_generation",
    "recommended_activity_ids",
    "teacher_controls",
    "music_education_guardrails",
    "quality_gates",
)

COMMON_GUARDRAILS = [
    "不能脱离音乐学习目标",
    "不能只做课堂管理或普通游戏",
    "必须保留听、唱、拍、奏、创、评中的至少一种学生音乐实践",
]


def _scenario_template(
    scenario_template_id: str,
    label: str,
    *,
    classroom_scenario: str,
    composition: str,
    image_generation: str,
    recommended_activity_ids: list[str],
    teacher_controls: list[str],
    quality_gates: list[str],
    extra_guardrails: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "version": SCENARIO_TEMPLATE_SPEC_VERSION,
        "scenario_template_id": scenario_template_id,
        "label": label,
        "audience": "primary_school",
        "classroom_scenario": classroom_scenario,
        "composition": composition,
        "image_generation": image_generation,
        "recommended_activity_ids": recommended_activity_ids,
        "teacher_controls": teacher_controls,
        "music_education_guardrails": COMMON_GUARDRAILS + (extra_guardrails or []),
        "quality_gates": quality_gates,
    }


SCENARIO_TEMPLATES: dict[str, dict[str, Any]] = {
    "substitute_teacher_mode": _scenario_template(
        "substitute_teacher_mode",
        "代课模式",
        classroom_scenario="临时代课、教师不熟悉教材或需要低风险流程。",
        composition="低风险听辨/节奏热身 + 清晰投屏步骤 + 自动提示 + 教师一键重置。",
        image_generation="optional_image_gen",
        recommended_activity_ids=[
            "rhythm_warmup",
            "lesson_opening_hook",
            "listen_choose_explain",
            "steady_beat_walk",
            "exit_ticket_review",
        ],
        teacher_controls=["playback", "tempo", "show_hint", "reset", "result_review"],
        quality_gates=["low_risk_flow", "teacher_prompt_visible", "reset_available"],
    ),
    "no_instrument_class_mode": _scenario_template(
        "no_instrument_class_mode",
        "无乐器教室模式",
        classroom_scenario="没有打击乐器、音条琴或乐器数量不足。",
        composition="虚拟乐器 + 身体打击 + 节奏卡 + 小组轮换，优先用拍手、拍腿、跺脚和停住替代实体乐器。",
        image_generation="none",
        recommended_activity_ids=[
            "body_percussion_builder",
            "rhythm_warmup",
            "strong_weak_beat_circle",
            "steady_beat_walk",
            "xylophone_creation",
            "orff_percussion_ensemble",
            "classroom_band_roles",
            "group_relay_performance",
        ],
        teacher_controls=["tempo", "mute_solo", "group_rotation", "reset", "result_review"],
        quality_gates=["virtual_or_body_substitute_ready", "sound_fallback_marked", "group_task_clear"],
    ),
    "large_class_quick_response": _scenario_template(
        "large_class_quick_response",
        "大班快速响应",
        classroom_scenario="学生多、无法逐个检查，需要快速收集全班反应。",
        composition="全班投屏选择 + 小组举牌/手势反馈 + 教师抽样追问音乐依据。",
        image_generation="none",
        recommended_activity_ids=[
            "listen_choose_explain",
            "instrument_timbre_match",
            "instrument_family_sorting",
            "theme_return_action",
            "rhythm_warmup",
            "exit_ticket_review",
        ],
        teacher_controls=["show_hint", "classroom_timer", "result_review", "reset"],
        quality_gates=["whole_class_response_visible", "evidence_prompt_required", "teacher_summary_ready"],
    ),
    "low_noise_music_activity": _scenario_template(
        "low_noise_music_activity",
        "低噪音活动",
        classroom_scenario="教室隔音差、临近考试或不能太吵。",
        composition="听辨、手势、静默节奏、旋律线和出口票，减少大声唱奏。",
        image_generation="optional_image_gen",
        recommended_activity_ids=[
            "melody_contour_trace",
            "theme_return_action",
            "listen_choose_explain",
            "picture_listening_intro",
            "simple_score_following",
            "exit_ticket_review",
        ],
        teacher_controls=["playback", "show_hint", "classroom_timer", "reset"],
        quality_gates=["low_noise_actions_only", "listen_first_preserved", "no_loud_performance_required"],
    ),
    "performance_day_pack": _scenario_template(
        "performance_day_pack",
        "展示课套装",
        classroom_scenario="汇报演出、展示课或公开课前排练。",
        composition="小组任务 + 计时 + 合奏控制 + 表现评价 + 展示记录。",
        image_generation="requires_image_gen",
        recommended_activity_ids=[
            "orff_percussion_ensemble",
            "classroom_band_roles",
            "group_relay_performance",
            "show_and_peer_feedback",
            "xylophone_creation",
        ],
        teacher_controls=["group_rotation", "mute_solo", "classroom_timer", "result_review", "reset"],
        quality_gates=["group_roles_clear", "performance_rubric_ready", "record_export_available"],
    ),
    "review_before_exam": _scenario_template(
        "review_before_exam",
        "复习课套装",
        classroom_scenario="单元复习、期末复习或课前回顾。",
        composition="出口票 + 听辨 + 节奏 + 唱名混合，快速看出薄弱点。",
        image_generation="none",
        recommended_activity_ids=[
            "exit_ticket_review",
            "rhythm_warmup",
            "listen_choose_explain",
            "solfege_sorting",
            "simple_score_following",
            "instrument_timbre_match",
        ],
        teacher_controls=["difficulty", "show_hint", "result_review", "reset"],
        quality_gates=["review_targets_visible", "result_summary_ready", "next_lesson_suggestion_available"],
    ),
    "festival_music_pack": _scenario_template(
        "festival_music_pack",
        "节日音乐活动",
        classroom_scenario="六一、春节、校园活动或主题音乐周。",
        composition="节奏、动作、合奏、展示和祝福语创编，围绕节日音乐素材完成。",
        image_generation="requires_image_gen",
        recommended_activity_ids=[
            "lesson_opening_hook",
            "body_percussion_builder",
            "orff_percussion_ensemble",
            "group_relay_performance",
            "show_and_peer_feedback",
            "graphic_score_create",
        ],
        teacher_controls=["tempo", "group_rotation", "classroom_timer", "result_review", "reset"],
        quality_gates=["festival_music_material_bound", "performance_or_creation_ready", "visual_assets_marked_if_missing"],
    ),
}


def list_scenario_templates() -> list[dict[str, Any]]:
    return [validate_scenario_template(template) for template in SCENARIO_TEMPLATES.values()]


def get_scenario_template(scenario_template_id: str) -> dict[str, Any]:
    template = SCENARIO_TEMPLATES.get(str(scenario_template_id or ""))
    if not template:
        raise ValueError(f"unknown scenario template: {scenario_template_id}")
    return validate_scenario_template(template)


def scenario_templates_for_activity(activity_id: str) -> list[dict[str, Any]]:
    normalized = str(activity_id or "")
    return [
        validate_scenario_template(template)
        for template in SCENARIO_TEMPLATES.values()
        if normalized in template.get("recommended_activity_ids", [])
    ]


def validate_scenario_template(template: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(template, dict):
        raise ValueError("scenario template spec must be a dict")
    missing = [field for field in REQUIRED_FIELDS if not template.get(field)]
    if missing:
        raise ValueError(f"scenario template spec missing fields: {', '.join(missing)}")
    if template.get("version") != SCENARIO_TEMPLATE_SPEC_VERSION:
        raise ValueError("scenario template spec version must be scenario_template_spec_v1")
    if template.get("audience") != "primary_school":
        raise ValueError("scenario template spec audience must be primary_school")
    if template.get("image_generation") not in {"none", "optional_image_gen", "requires_image_gen"}:
        raise ValueError("scenario template image_generation must be none, optional_image_gen, or requires_image_gen")
    guardrails = template.get("music_education_guardrails") if isinstance(template.get("music_education_guardrails"), list) else []
    if "不能脱离音乐学习目标" not in guardrails:
        raise ValueError("scenario template must preserve music learning goal")
    return deepcopy(template)
