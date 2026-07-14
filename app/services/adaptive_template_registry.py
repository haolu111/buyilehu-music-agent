from __future__ import annotations

from copy import deepcopy
from typing import Any


ADAPTIVE_TEMPLATE_SPEC_VERSION = "adaptive_template_spec_v1"

REQUIRED_FIELDS = (
    "version",
    "adaptive_template_id",
    "label",
    "audience",
    "trigger_condition",
    "adjustment",
    "teacher_visible_reason",
    "undo_action",
    "applicable_activity_ids",
    "student_music_practices",
    "music_education_guardrails",
    "quality_gates",
)

COMMON_GUARDRAILS = [
    "不能改变课堂目标",
    "调整原因必须让教师看见",
    "教师必须能一键撤回",
    "小学低段优先调速度、提示和选项数量，不做复杂评分",
]


def _adaptive_template(
    adaptive_template_id: str,
    label: str,
    *,
    trigger_condition: str,
    adjustment: str,
    teacher_visible_reason: str,
    undo_action: str,
    applicable_activity_ids: list[str],
    student_music_practices: list[str],
    quality_gates: list[str],
    extra_guardrails: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "version": ADAPTIVE_TEMPLATE_SPEC_VERSION,
        "adaptive_template_id": adaptive_template_id,
        "label": label,
        "audience": "primary_school",
        "trigger_condition": trigger_condition,
        "adjustment": adjustment,
        "teacher_visible_reason": teacher_visible_reason,
        "undo_action": undo_action,
        "applicable_activity_ids": applicable_activity_ids,
        "student_music_practices": student_music_practices,
        "music_education_guardrails": COMMON_GUARDRAILS + (extra_guardrails or []),
        "quality_gates": quality_gates,
    }


ADAPTIVE_TEMPLATES: dict[str, dict[str, Any]] = {
    "slow_down_when_many_late": _adaptive_template(
        "slow_down_when_many_late",
        "多数学生晚拍则降速",
        trigger_condition="连续 2 轮晚拍或偏慢反馈较多，且活动目标仍是稳定拍、节奏或律动。",
        adjustment="BPM 降低 8 到 12，并保留当前节奏/拍号材料。",
        teacher_visible_reason="多数学生落在拍点后面，建议先降速复听，再回到原速。",
        undo_action="恢复上一轮 BPM。",
        applicable_activity_ids=[
            "rhythm_warmup",
            "meter_body_movement",
            "steady_beat_walk",
            "rhythm_question_answer",
            "lyrics_rhythm_reading",
            "lyrics_rhythm_practice",
            "body_percussion_builder",
            "orff_percussion_ensemble",
        ],
        student_music_practices=["listen", "tap", "move", "play"],
        quality_gates=["teacher_reason_visible", "bpm_change_bounded", "undo_restores_previous_bpm"],
    ),
    "hide_hint_after_success": _adaptive_template(
        "hide_hint_after_success",
        "成功后隐藏提示",
        trigger_condition="同一乐句、节奏或唱名连续 2 次通过，且教师未锁定提示。",
        adjustment="隐藏歌词、唱名、节奏或图片提示中的一个支架。",
        teacher_visible_reason="学生已经能借助提示完成，可尝试隐藏部分提示，检查是否真正听会或唱会。",
        undo_action="重新显示刚隐藏的提示。",
        applicable_activity_ids=[
            "phrase_singing_practice",
            "phrase_loop_singing",
            "lyrics_rhythm_reading",
            "lyrics_rhythm_practice",
            "solfege_echo_singing",
            "simple_score_following",
            "melody_contour_trace",
            "solfege_sorting",
        ],
        student_music_practices=["listen", "sing", "read", "tap"],
        quality_gates=["hint_change_visible", "teacher_can_restore_hint", "same_material_preserved"],
    ),
    "reduce_choices_when_wrong": _adaptive_template(
        "reduce_choices_when_wrong",
        "错多则减少选项",
        trigger_condition="连续 2 轮听辨或选择错误，且错误集中在同一音乐要素。",
        adjustment="选项从 5 个降到 3 个，并保留正确答案和一个近似干扰项。",
        teacher_visible_reason="学生还没有分清目标音乐要素，先减少选项，聚焦听辨依据。",
        undo_action="恢复上一组选项数量。",
        applicable_activity_ids=[
            "picture_listening_intro",
            "listen_choose_explain",
            "instrument_timbre_match",
            "instrument_family_sorting",
            "solfege_sorting",
            "form_ordering",
        ],
        student_music_practices=["listen", "choose", "match", "classify"],
        quality_gates=["choice_count_bounded", "target_answer_preserved", "teacher_reason_visible"],
    ),
    "repeat_phrase_when_uncertain": _adaptive_template(
        "repeat_phrase_when_uncertain",
        "不稳定则重复乐句",
        trigger_condition="教师点再练，或同一乐句/唱名/节奏准确率低于教师设定阈值。",
        adjustment="循环当前乐句或当前节奏，不进入下一句。",
        teacher_visible_reason="当前材料还不稳定，建议先重复这一句，再连接下一句。",
        undo_action="取消循环并进入下一句。",
        applicable_activity_ids=[
            "phrase_singing_practice",
            "phrase_loop_singing",
            "solfege_echo_singing",
            "simple_score_following",
            "lyrics_rhythm_reading",
            "rhythm_question_answer",
        ],
        student_music_practices=["listen", "sing", "read", "tap"],
        quality_gates=["current_phrase_preserved", "teacher_confirm_available", "loop_cancel_available"],
    ),
    "raise_challenge_after_stable": _adaptive_template(
        "raise_challenge_after_stable",
        "稳定后增加挑战",
        trigger_condition="连续 2 轮稳定完成，且教师允许挑战。",
        adjustment="小幅加快、增加一张卡片、隐藏一个提示或加入小组接龙。",
        teacher_visible_reason="学生已稳定完成当前材料，可以提高一点挑战，但仍围绕原音乐目标。",
        undo_action="回到上一难度。",
        applicable_activity_ids=[
            "rhythm_warmup",
            "steady_beat_walk",
            "body_percussion_builder",
            "xylophone_creation",
            "graphic_score_create",
            "group_relay_performance",
        ],
        student_music_practices=["tap", "move", "create", "play", "perform"],
        quality_gates=["challenge_step_small", "teacher_reason_visible", "undo_restores_previous_level"],
    ),
    "switch_to_teacher_confirm": _adaptive_template(
        "switch_to_teacher_confirm",
        "自动判定不可靠时切教师确认",
        trigger_condition="麦克风、音频输入或自动判定不可用，或课堂噪声导致结果不可信。",
        adjustment="改为教师确认模式，保留学生操作记录和材料进度。",
        teacher_visible_reason="当前自动判定不可靠，改由教师确认，避免系统误判学生表现。",
        undo_action="恢复自动判定模式。",
        applicable_activity_ids=[
            "phrase_singing_practice",
            "phrase_loop_singing",
            "solfege_echo_singing",
            "simple_score_following",
            "show_and_peer_feedback",
            "orff_percussion_ensemble",
            "classroom_band_roles",
        ],
        student_music_practices=["sing", "perform", "play", "assess"],
        quality_gates=["fallback_reason_visible", "teacher_confirm_available", "student_progress_preserved"],
    ),
    "suggest_next_activity": _adaptive_template(
        "suggest_next_activity",
        "活动后推荐下一步",
        trigger_condition="当前活动完成，且已有记录模板或教师确认结果。",
        adjustment="推荐一个巩固、挑战、展示或收尾活动，不自动跳转。",
        teacher_visible_reason="根据刚才的课堂结果，给教师一个下一步建议，由教师决定是否采用。",
        undo_action="关闭建议卡，不改变当前活动。",
        applicable_activity_ids=["*"],
        student_music_practices=["listen", "tap", "sing", "move", "play", "create", "perform", "assess"],
        quality_gates=["teacher_decides_next_step", "current_activity_preserved", "recommendation_uses_record_evidence"],
    ),
}


def list_adaptive_templates() -> list[dict[str, Any]]:
    return [validate_adaptive_template(template) for template in ADAPTIVE_TEMPLATES.values()]


def get_adaptive_template(adaptive_template_id: str) -> dict[str, Any]:
    template = ADAPTIVE_TEMPLATES.get(str(adaptive_template_id or ""))
    if not template:
        raise ValueError(f"unknown adaptive template: {adaptive_template_id}")
    return validate_adaptive_template(template)


def adaptive_specs_for_activity(activity_id: str) -> list[dict[str, Any]]:
    normalized = str(activity_id or "")
    return [
        validate_adaptive_template(template)
        for template in ADAPTIVE_TEMPLATES.values()
        if "*" in template.get("applicable_activity_ids", []) or normalized in template.get("applicable_activity_ids", [])
    ]


def validate_adaptive_template(template: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(template, dict):
        raise ValueError("adaptive template spec must be a dict")
    missing = [field for field in REQUIRED_FIELDS if not template.get(field)]
    if missing:
        raise ValueError(f"adaptive template spec missing fields: {', '.join(missing)}")
    if template.get("version") != ADAPTIVE_TEMPLATE_SPEC_VERSION:
        raise ValueError("adaptive template spec version must be adaptive_template_spec_v1")
    if template.get("audience") != "primary_school":
        raise ValueError("adaptive template spec audience must be primary_school")
    guardrails = template.get("music_education_guardrails") if isinstance(template.get("music_education_guardrails"), list) else []
    if "不能改变课堂目标" not in guardrails:
        raise ValueError("adaptive template must preserve classroom goal")
    return deepcopy(template)
