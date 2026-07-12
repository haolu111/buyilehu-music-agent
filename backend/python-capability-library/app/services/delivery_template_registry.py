from __future__ import annotations

from copy import deepcopy
from typing import Any


DELIVERY_TEMPLATE_SPEC_VERSION = "delivery_template_spec_v1"

REQUIRED_FIELDS = (
    "version",
    "delivery_template_id",
    "label",
    "audience",
    "form",
    "purpose",
    "priority",
    "output_formats",
    "applicable_activity_ids",
    "classroom_use",
    "quality_gates",
)


def _delivery_template(
    delivery_template_id: str,
    label: str,
    *,
    form: str,
    purpose: str,
    priority: str,
    output_formats: list[str],
    applicable_activity_ids: list[str],
    classroom_use: str,
    quality_gates: list[str],
) -> dict[str, Any]:
    return {
        "version": DELIVERY_TEMPLATE_SPEC_VERSION,
        "delivery_template_id": delivery_template_id,
        "label": label,
        "audience": "primary_school",
        "form": form,
        "purpose": purpose,
        "priority": priority,
        "output_formats": output_formats,
        "applicable_activity_ids": applicable_activity_ids,
        "classroom_use": classroom_use,
        "quality_gates": quality_gates,
    }


P0_ACTIVITY_IDS = ["*"]

CARD_ACTIVITY_IDS = [
    "rhythm_warmup",
    "lyrics_rhythm_reading",
    "lyrics_rhythm_practice",
    "solfege_sorting",
    "simple_score_following",
    "instrument_timbre_match",
    "instrument_family_sorting",
    "form_ordering",
    "theme_return_action",
    "body_percussion_builder",
    "graphic_score_create",
]

RESULT_EXPORT_ACTIVITY_IDS = [
    "rhythm_warmup",
    "steady_beat_walk",
    "strong_weak_beat_circle",
    "rhythm_question_answer",
    "lesson_opening_hook",
    "listen_choose_explain",
    "theme_return_action",
    "graphic_score_create",
    "xylophone_creation",
    "orff_percussion_ensemble",
    "classroom_band_roles",
    "group_relay_performance",
    "show_and_peer_feedback",
    "exit_ticket_review",
]


DELIVERY_TEMPLATES: dict[str, dict[str, Any]] = {
    "projector_activity_view": _delivery_template(
        "projector_activity_view",
        "投屏活动视图",
        form="大字、大按钮、少文字、教师控制明显",
        purpose="全班一起看、听、做，适合电子白板或教室大屏。",
        priority="P0",
        output_formats=["HTML", "React view"],
        applicable_activity_ids=P0_ACTIVITY_IDS,
        classroom_use="用于课堂主屏，保证学生能在远处看清音乐材料、当前任务和教师控制。",
        quality_gates=["large_text_readable", "teacher_controls_visible", "no_horizontal_overflow"],
    ),
    "student_touch_view": _delivery_template(
        "student_touch_view",
        "学生触摸视图",
        form="大触控区域、少菜单、固定任务焦点",
        purpose="触摸屏、平板或一体机上让学生直接操作。",
        priority="P0",
        output_formats=["HTML", "React view"],
        applicable_activity_ids=P0_ACTIVITY_IDS,
        classroom_use="用于学生上台或小组触摸操作，减少长说明，保留清晰反馈和重置。",
        quality_gates=["touch_targets_large", "task_focus_visible", "reset_available"],
    ),
    "teacher_setup_view": _delivery_template(
        "teacher_setup_view",
        "教师备课视图",
        form="参数、材料、预览、质量门禁",
        purpose="上课前配置歌曲、节奏、音色、学段和教师控制。",
        priority="P0",
        output_formats=["JSON", "HTML", "React view"],
        applicable_activity_ids=P0_ACTIVITY_IDS,
        classroom_use="用于课前确认材料绑定、自适应策略、记录模板和缺失素材，避免上课才发现不可用。",
        quality_gates=["material_status_visible", "quality_gates_visible", "preview_available"],
    ),
    "printable_card_sheet": _delivery_template(
        "printable_card_sheet",
        "可打印卡片页",
        form="PDF/HTML 打印卡片",
        purpose="需要实体备份时打印节奏卡、唱名卡、歌词条、图形谱卡或乐器卡。",
        priority="P1",
        output_formats=["HTML", "PDF"],
        applicable_activity_ids=CARD_ACTIVITY_IDS,
        classroom_use="用于没有足够设备、需要贴黑板或分组发卡的场景，仍和数字活动使用同一材料。",
        quality_gates=["print_layout_stable", "card_text_readable", "same_material_as_runtime"],
    ),
    "lesson_activity_pack_export": _delivery_template(
        "lesson_activity_pack_export",
        "活动包导出",
        form="JSON + HTML + assets",
        purpose="把一次课堂活动打包给其他老师或复制到另一台电脑。",
        priority="P1",
        output_formats=["JSON", "HTML", "assets"],
        applicable_activity_ids=P0_ACTIVITY_IDS,
        classroom_use="用于分享完整活动，不只分享截图；包含活动 spec、材料绑定、素材包和运行入口。",
        quality_gates=["spec_included", "assets_included", "runtime_entry_included"],
    ),
    "classroom_result_export": _delivery_template(
        "classroom_result_export",
        "课堂结果导出",
        form="JSON/CSV/截图",
        purpose="课后复盘学生表现、出口票、小组评价和创编记录。",
        priority="P1",
        output_formats=["JSON", "CSV", "PNG"],
        applicable_activity_ids=RESULT_EXPORT_ACTIVITY_IDS,
        classroom_use="用于课后整理学生音乐学习证据，服务复盘、下节课调整和教研分享。",
        quality_gates=["record_schema_bound", "student_privacy_safe", "teacher_summary_available"],
    ),
}


def list_delivery_templates() -> list[dict[str, Any]]:
    return [validate_delivery_template(template) for template in DELIVERY_TEMPLATES.values()]


def get_delivery_template(delivery_template_id: str) -> dict[str, Any]:
    template = DELIVERY_TEMPLATES.get(str(delivery_template_id or ""))
    if not template:
        raise ValueError(f"unknown delivery template: {delivery_template_id}")
    return validate_delivery_template(template)


def delivery_templates_for_activity(activity_id: str) -> list[dict[str, Any]]:
    normalized = str(activity_id or "")
    return [
        validate_delivery_template(template)
        for template in DELIVERY_TEMPLATES.values()
        if "*" in template.get("applicable_activity_ids", []) or normalized in template.get("applicable_activity_ids", [])
    ]


def validate_delivery_template(template: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(template, dict):
        raise ValueError("delivery template spec must be a dict")
    missing = [field for field in REQUIRED_FIELDS if not template.get(field)]
    if missing:
        raise ValueError(f"delivery template spec missing fields: {', '.join(missing)}")
    if template.get("version") != DELIVERY_TEMPLATE_SPEC_VERSION:
        raise ValueError("delivery template spec version must be delivery_template_spec_v1")
    if template.get("audience") != "primary_school":
        raise ValueError("delivery template spec audience must be primary_school")
    if template.get("priority") not in {"P0", "P1"}:
        raise ValueError("delivery template priority must be P0 or P1")
    return deepcopy(template)
