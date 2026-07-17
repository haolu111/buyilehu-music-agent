#定义教师端对游戏的控制能力
from __future__ import annotations

from copy import deepcopy
from typing import Any


TEACHER_CONTROL_PACK_VERSION = "teacher_control_pack_v1"

REQUIRED_FIELDS = (
    "version",
    "control_pack_id",
    "label",
    "audience",
    "classroom_problem",
    "controls",
    "teacher_actions",
    "applicable_activity_ids",
    "music_education_use",
    "quality_gates",
    "control_logic",
)


DEFAULT_CONTROL_LOGIC = {
    "reset_behavior": "一键回到本轮初始状态，保留原始音乐材料，按活动需要清空学生临时事件。",
    "teacher_priority_over_auto_adaptive": True,
    "auto_adjustment_requires_visible_reason": True,
    "projector_safe": True,
    "grade_band_policy": {
        "lower_primary": "低段只显示必要控制，优先速度、播放、提示、重置。",
        "middle_primary": "中段可增加小组、难度和结果回看。",
        "upper_primary": "高段可开放更多创编、声部和导出控制。",
    },
}


def _pack(
    control_pack_id: str,
    label: str,
    *,
    classroom_problem: str,
    controls: list[str],
    teacher_actions: list[str],
    applicable_activity_ids: list[str],
    music_education_use: str,
    quality_gates: list[str],
    control_logic: dict[str, Any] | None = None,
) -> dict[str, Any]:
    merged_logic = deepcopy(DEFAULT_CONTROL_LOGIC)
    if control_logic:
        merged_logic.update(control_logic)
    return {
        "version": TEACHER_CONTROL_PACK_VERSION,
        "control_pack_id": control_pack_id,
        "label": label,
        "audience": "primary_school",
        "classroom_problem": classroom_problem,
        "controls": controls,
        "teacher_actions": teacher_actions,
        "applicable_activity_ids": applicable_activity_ids,
        "music_education_use": music_education_use,
        "quality_gates": quality_gates,
        "control_logic": merged_logic,
    }


ALL_ACTIVITY_IDS = ["*"]

TEACHER_CONTROL_PACKS: dict[str, dict[str, Any]] = {
    "tempo_control_pack": _pack(
        "tempo_control_pack",
        "速度控制包",
        classroom_problem="教师需要根据学生拍点、演唱和器乐进入情况现场调速。",
        controls=["BPM", "慢速", "原速", "加速"],
        teacher_actions=["set_bpm", "slow_down", "restore_tempo", "speed_up"],
        applicable_activity_ids=ALL_ACTIVITY_IDS,
        music_education_use="用于节奏、学唱和器乐活动的分层练习，帮助学生先稳再快。",
        quality_gates=["tempo_applies", "student_state_preserved", "reset_restores_default"],
    ),
    "hint_visibility_pack": _pack(
        "hint_visibility_pack",
        "提示开关包",
        classroom_problem="教师需要先给支架，再逐步隐藏答案、歌词、唱名、节拍或图片。",
        controls=["显示提示", "隐藏提示", "隐藏歌词", "隐藏唱名", "隐藏节奏", "隐藏图片"],
        teacher_actions=["show_hint", "hide_hint", "hide_words", "hide_solfege", "hide_picture"],
        applicable_activity_ids=ALL_ACTIVITY_IDS,
        music_education_use="支持从体验到独立表现的递进，避免学生只看答案操作。",
        quality_gates=["hint_toggle_applies", "answer_not_revealed_by_default", "teacher_can_restore_hint"],
    ),
    "phrase_loop_pack": _pack(
        "phrase_loop_pack",
        "分句循环包",
        classroom_problem="歌曲学唱需要反复练当前乐句、上一句和下一句。",
        controls=["上一句", "下一句", "循环当前句", "停止循环"],
        teacher_actions=["previous_phrase", "next_phrase", "loop_current_phrase", "stop_loop"],
        applicable_activity_ids=["phrase_singing_practice", "phrase_loop_singing", "lyrics_rhythm_reading"],
        music_education_use="用于整体听后分句模唱和难点句重练，保留教师确认。",
        quality_gates=["phrase_index_changes", "loop_applies", "teacher_confirm_available"],
    ),
    "group_rotation_pack": _pack(
        "group_rotation_pack",
        "小组轮换包",
        classroom_problem="小组展示、接力和合奏容易出现轮次混乱。",
        controls=["当前组", "下一组", "跳过", "标记完成"],
        teacher_actions=["assign_group", "next_group", "skip_group", "mark_done"],
        applicable_activity_ids=["group_relay_performance", "show_and_peer_feedback", "classroom_band_roles", "orff_percussion_ensemble"],
        music_education_use="让小组合作围绕具体音乐任务轮换，而不是无序抢答。",
        quality_gates=["current_group_visible", "rotation_advances", "completed_state_recorded"],
    ),
    "teacher_confirm_pack": _pack(
        "teacher_confirm_pack",
        "教师确认包",
        classroom_problem="儿童演唱、展示和创编不适合完全自动评分。",
        controls=["通过", "再来一次", "给提示"],
        teacher_actions=["confirm_pass", "retry", "show_prompt"],
        applicable_activity_ids=["phrase_singing_practice", "phrase_loop_singing", "solfege_echo_singing", "show_and_peer_feedback", "exit_ticket_review"],
        music_education_use="把主观表现交还给教师专业判断，同时保留学生记录。",
        quality_gates=["manual_confirm_available", "retry_preserves_material", "feedback_recorded"],
    ),
    "classroom_timer_pack": _pack(
        "classroom_timer_pack",
        "课堂计时包",
        classroom_problem="小组创编、讨论和展示需要清晰时间边界。",
        controls=["30 秒", "1 分钟", "3 分钟", "暂停"],
        teacher_actions=["start_30s", "start_1m", "start_3m", "pause_timer"],
        applicable_activity_ids=["body_percussion_builder", "group_relay_performance", "show_and_peer_feedback", "xylophone_creation"],
        music_education_use="帮助学生在有限时间内完成听、编、改、演的课堂任务。",
        quality_gates=["timer_visible", "pause_resume_applies", "timeout_does_not_submit_automatically"],
    ),
    "difficulty_stepper_pack": _pack(
        "difficulty_stepper_pack",
        "难度阶梯包",
        classroom_problem="教师要在课堂现场根据学生表现升降难度。",
        controls=["简单", "标准", "挑战"],
        teacher_actions=["set_easy", "set_standard", "set_challenge"],
        applicable_activity_ids=ALL_ACTIVITY_IDS,
        music_education_use="低难度减少材料和提示负担，高难度增加隐藏提示、速度或创编要求。",
        quality_gates=["difficulty_changes_constraints", "current_level_visible", "reset_restores_default"],
    ),
    "mute_solo_pack": _pack(
        "mute_solo_pack",
        "合奏控制包",
        classroom_problem="合奏时教师需要让某个声部独奏、静音或全开。",
        controls=["全部", "独奏", "静音", "轮奏"],
        teacher_actions=["all_on", "solo_group", "mute_group", "rotate_parts"],
        applicable_activity_ids=["orff_percussion_ensemble", "classroom_band_roles"],
        music_education_use="用于听清声部、控制音量平衡和练习按时进入。",
        quality_gates=["mute_applies", "solo_applies", "ensemble_state_recorded"],
    ),
    "playback_control_pack": _pack(
        "playback_control_pack",
        "播放控制包",
        classroom_problem="听赏、识谱、音色和曲式活动需要复听、分段听和对比听。",
        controls=["播放", "暂停", "重播", "分段复听"],
        teacher_actions=["play", "pause", "replay", "replay_section"],
        applicable_activity_ids=ALL_ACTIVITY_IDS,
        music_education_use="保证学生先听音乐材料，再进行选择、排序、分类或说明依据。",
        quality_gates=["playback_starts", "replay_resets_position", "section_replay_available_when_needed"],
    ),
    "result_review_pack": _pack(
        "result_review_pack",
        "结果记录包",
        classroom_problem="课堂活动需要保存展示、评价、创编和出口票结果。",
        controls=["保存", "导出", "查看汇总"],
        teacher_actions=["save", "export_json", "view_summary"],
        applicable_activity_ids=ALL_ACTIVITY_IDS,
        music_education_use="把学生听、唱、奏、动、创、评的过程转成课后可复盘证据。",
        quality_gates=["record_export_available", "summary_visible", "student_privacy_safe"],
    ),
    "reset_pack": _pack(
        "reset_pack",
        "重置包",
        classroom_problem="教师需要随时重新开始当前轮次，且不能破坏原始音乐材料。",
        controls=["重置", "清空本轮", "回到开始"],
        teacher_actions=["reset", "clear_round", "restart"],
        applicable_activity_ids=ALL_ACTIVITY_IDS,
        music_education_use="用于课堂控场和重复练习，保证误操作后能快速恢复。",
        quality_gates=["reset_available", "material_preserved", "student_events_cleared_when_expected"],
    ),
}


TEACHER_CONTROL_ACTION_TO_PACK = {
    "tempo": "tempo_control_pack",
    "show_beat": "hint_visibility_pack",
    "hide_hint": "hint_visibility_pack",
    "show_strong_beat": "hint_visibility_pack",
    "hide_words": "hint_visibility_pack",
    "phrase_loop": "phrase_loop_pack",
    "replay": "playback_control_pack",
    "replay_section": "playback_control_pack",
    "show_reason_prompt": "hint_visibility_pack",
    "show_hint": "hint_visibility_pack",
    "show_solfege": "hint_visibility_pack",
    "hide_solfege": "hint_visibility_pack",
    "hide_picture": "hint_visibility_pack",
    "limit_pitch_count": "difficulty_stepper_pack",
    "record": "result_review_pack",
    "mute_group": "mute_solo_pack",
    "solo_group": "mute_solo_pack",
    "assign_group": "group_rotation_pack",
    "mark_done": "group_rotation_pack",
    "show_answer": "hint_visibility_pack",
    "save": "result_review_pack",
    "reset": "reset",
}

TEACHER_CONFIRM_ACTIVITY_IDS = {
    "phrase_singing_practice",
    "phrase_loop_singing",
    "solfege_echo_singing",
    "simple_score_following",
    "group_relay_performance",
    "show_and_peer_feedback",
    "body_percussion_builder",
    "exit_ticket_review",
}


def list_teacher_control_packs() -> list[dict[str, Any]]:
    return [validate_teacher_control_pack(pack) for pack in TEACHER_CONTROL_PACKS.values()]


def get_teacher_control_pack(control_pack_id: str) -> dict[str, Any]:
    pack = TEACHER_CONTROL_PACKS.get(str(control_pack_id or ""))
    if not pack:
        raise ValueError(f"unknown teacher control pack: {control_pack_id}")
    return validate_teacher_control_pack(pack)


def teacher_control_specs_for_ids(control_pack_ids: list[str]) -> list[dict[str, Any]]:
    specs: list[dict[str, Any]] = []
    for control_pack_id in control_pack_ids:
        if control_pack_id not in {spec["control_pack_id"] for spec in specs}:
            specs.append(get_teacher_control_pack(control_pack_id))
    return specs


def teacher_control_pack_ids_for_activity(controls: list[str], activity_id: str) -> list[str]:
    packs: list[str] = []
    for control in controls:
        pack = TEACHER_CONTROL_ACTION_TO_PACK.get(control)
        if pack and pack not in packs:
            packs.append(pack)
    if "teacher_confirm_pack" not in packs and activity_id in TEACHER_CONFIRM_ACTIVITY_IDS:
        packs.append("teacher_confirm_pack")
    if "reset" in packs:
        packs.remove("reset")
    if "reset_pack" not in packs:
        packs.append("reset_pack")
    return packs


def validate_teacher_control_pack(pack: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(pack, dict):
        raise ValueError("teacher control pack must be a dict")
    missing = [field for field in REQUIRED_FIELDS if not pack.get(field)]
    if missing:
        raise ValueError(f"teacher control pack missing fields: {', '.join(missing)}")
    if pack.get("version") != TEACHER_CONTROL_PACK_VERSION:
        raise ValueError("teacher control pack version must be teacher_control_pack_v1")
    if pack.get("audience") != "primary_school":
        raise ValueError("teacher control pack audience must be primary_school")
    logic = pack.get("control_logic")
    if not isinstance(logic, dict):
        raise ValueError("teacher control pack control_logic must be a dict")
    for field in (
        "reset_behavior",
        "teacher_priority_over_auto_adaptive",
        "auto_adjustment_requires_visible_reason",
        "projector_safe",
        "grade_band_policy",
    ):
        if field not in logic:
            raise ValueError(f"teacher control pack control_logic.{field} must be provided")
    return deepcopy(pack)
