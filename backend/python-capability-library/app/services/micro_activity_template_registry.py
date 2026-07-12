from __future__ import annotations

from copy import deepcopy
from typing import Any


REQUIRED_MICRO_ACTIVITY_FIELDS = (
    "version",
    "micro_activity_template_id",
    "label",
    "audience",
    "duration_minutes",
    "classroom_use",
    "component_ids",
    "applicable_activity_ids",
    "music_elements",
    "student_music_practices",
    "teaching_stages",
    "teacher_controls",
    "acceptance",
    "quality_gates",
)


MICRO_ACTIVITY_TEMPLATE_REGISTRY: dict[str, dict[str, Any]] = {
    "one_minute_beat_check": {
        "version": "micro_activity_template_v1",
        "micro_activity_template_id": "one_minute_beat_check",
        "label": "一分钟稳拍检查",
        "audience": "primary_school",
        "duration_minutes": 1,
        "classroom_use": "上课开始或节奏活动前快速检查全班拍点是否稳定。",
        "component_ids": ["meter_track", "tap_feedback", "teacher_control_bar"],
        "applicable_activity_ids": ["rhythm_warmup", "steady_beat_walk", "strong_weak_beat_circle"],
        "music_elements": ["稳定拍", "节奏"],
        "student_music_practices": ["listen", "tap", "move"],
        "teaching_stages": ["导入", "节奏练习"],
        "teacher_controls": ["tempo", "reset", "show_beat"],
        "acceptance": ["能快速开始", "能快速重置", "至少记录 3 次拍点"],
        "quality_gates": ["学生先听稳定拍", "全班拍点记录可见", "教师可一键重置"],
    },
    "listen_once_vote": {
        "version": "micro_activity_template_v1",
        "micro_activity_template_id": "listen_once_vote",
        "label": "听一遍投票",
        "audience": "primary_school",
        "duration_minutes": 2,
        "classroom_use": "欣赏初听后让学生选择听到的情绪、速度或力度，并显示全班投票结果。",
        "component_ids": ["audio_player", "choice_cards", "rubric_panel", "teacher_control_bar"],
        "applicable_activity_ids": ["picture_listening_intro", "listen_choose_explain", "lesson_opening_hook"],
        "music_elements": ["情绪", "速度", "力度"],
        "student_music_practices": ["listen", "choose", "explain"],
        "teaching_stages": ["导入", "初听/感受"],
        "teacher_controls": ["playback", "result_review", "reset"],
        "acceptance": ["全班投票结果可显示", "可复听", "学生能说出至少一个音乐依据"],
        "quality_gates": ["必须先完整听一遍", "选择后追问音乐依据", "不能只按人数排名"],
    },
    "clap_after_me": {
        "version": "micro_activity_template_v1",
        "micro_activity_template_id": "clap_after_me",
        "label": "跟我拍",
        "audience": "primary_school",
        "duration_minutes": 3,
        "classroom_use": "教师示范一条短节奏，学生用拍手、节奏垫或身体动作回应。",
        "component_ids": ["rhythm_card_bank", "rhythm_pad", "meter_track", "teacher_control_bar"],
        "applicable_activity_ids": ["rhythm_warmup", "rhythm_question_answer", "lyrics_rhythm_reading"],
        "music_elements": ["稳定拍", "节奏", "休止"],
        "student_music_practices": ["listen", "tap", "move"],
        "teaching_stages": ["节奏练习", "巩固"],
        "teacher_controls": ["tempo", "show_hint", "reset"],
        "acceptance": ["教师示范清楚", "学生回应有拍点记录", "可换节奏卡"],
        "quality_gates": ["先听教师节奏再回应", "休止要表现为停住", "反馈围绕拍点和节奏顺序"],
    },
    "sing_the_missing_word": {
        "version": "micro_activity_template_v1",
        "micro_activity_template_id": "sing_the_missing_word",
        "label": "缺词接唱",
        "audience": "primary_school",
        "duration_minutes": 3,
        "classroom_use": "歌曲巩固时隐藏关键词，学生在乐句中接唱缺失歌词。",
        "component_ids": ["audio_player", "lyrics_strip", "teacher_control_bar"],
        "applicable_activity_ids": ["phrase_singing_practice", "phrase_loop_singing", "lyrics_rhythm_reading"],
        "music_elements": ["乐句", "歌词", "旋律"],
        "student_music_practices": ["listen", "sing"],
        "teaching_stages": ["学唱", "巩固"],
        "teacher_controls": ["phrase_loop", "hide_hint", "teacher_confirm", "reset"],
        "acceptance": ["可隐藏关键词", "可按乐句循环", "教师确认后进入下一句"],
        "quality_gates": ["不能只看字填空", "学生要在旋律中接唱", "低段保留教师确认"],
    },
    "find_the_strong_beat": {
        "version": "micro_activity_template_v1",
        "micro_activity_template_id": "find_the_strong_beat",
        "label": "找强拍",
        "audience": "primary_school",
        "duration_minutes": 3,
        "classroom_use": "拍号体验时让学生听稳定拍并在强拍上敲击虚拟小鼓或做大动作。",
        "component_ids": ["meter_track", "virtual_hand_drum", "tap_feedback", "teacher_control_bar"],
        "applicable_activity_ids": ["meter_body_movement", "strong_weak_beat_circle", "rhythm_warmup"],
        "music_elements": ["节拍", "拍号", "强弱"],
        "student_music_practices": ["listen", "tap", "move", "play"],
        "teaching_stages": ["导入", "律动", "学唱前体验"],
        "teacher_controls": ["tempo", "show_strong_beat", "hide_hint", "reset"],
        "acceptance": ["强拍点击判定", "弱拍不误判为失败", "教师可开关强拍提示"],
        "quality_gates": ["必须先体验强弱再讲拍号", "低段用大动作表现强拍", "判定围绕拍点而非抢答速度"],
    },
    "choose_the_timbre_word": {
        "version": "micro_activity_template_v1",
        "micro_activity_template_id": "choose_the_timbre_word",
        "label": "选音色词",
        "audience": "primary_school",
        "duration_minutes": 4,
        "classroom_use": "音色听辨时先播放对比音频，再让学生选择明亮、柔和、清脆、低沉等证据词。",
        "component_ids": ["compare_player", "evidence_word_cards", "rubric_panel", "teacher_control_bar"],
        "applicable_activity_ids": ["instrument_timbre_match", "instrument_family_sorting", "listen_choose_explain"],
        "music_elements": ["音色", "乐器", "力度"],
        "student_music_practices": ["listen", "choose", "explain"],
        "teaching_stages": ["复听/探究", "评价"],
        "teacher_controls": ["playback", "result_review", "teacher_confirm", "reset"],
        "acceptance": ["选择后能说依据", "可复听对比", "证据词和音频绑定"],
        "quality_gates": ["必须先听声音再看图", "证据词不能脱离听觉", "真实乐器图卡不能冒充音频证据"],
    },
    "move_when_theme_returns": {
        "version": "micro_activity_template_v1",
        "micro_activity_template_id": "move_when_theme_returns",
        "label": "主题回来就动作",
        "audience": "primary_school",
        "duration_minutes": 5,
        "classroom_use": "欣赏复听时，主题段落回来学生做约定动作或举主题卡。",
        "component_ids": ["audio_player", "body_action_cards", "form_card_timeline", "teacher_control_bar"],
        "applicable_activity_ids": ["theme_return_action", "form_ordering", "picture_listening_intro"],
        "music_elements": ["主题", "重复", "曲式"],
        "student_music_practices": ["listen", "move", "explain"],
        "teaching_stages": ["复听/探究", "欣赏"],
        "teacher_controls": ["playback", "show_hint", "hide_hint", "reset"],
        "acceptance": ["主题段落提示可开关", "学生动作和主题再现绑定", "可复听验证"],
        "quality_gates": ["必须绑定音频段落", "动作服务主题再现听辨", "不能变成普通反应游戏"],
    },
    "two_group_echo": {
        "version": "micro_activity_template_v1",
        "micro_activity_template_id": "two_group_echo",
        "label": "两组回声",
        "audience": "primary_school",
        "duration_minutes": 5,
        "classroom_use": "A/B 两组轮流接唱、接拍或接奏，适合学唱巩固和节奏问答。",
        "component_ids": ["group_task_board", "audio_player", "teacher_control_bar"],
        "applicable_activity_ids": ["rhythm_question_answer", "phrase_loop_singing", "group_relay_performance"],
        "music_elements": ["乐句", "节奏", "问答"],
        "student_music_practices": ["listen", "sing", "tap", "cooperate"],
        "teaching_stages": ["巩固", "展示评价"],
        "teacher_controls": ["group_rotation", "phrase_loop", "teacher_confirm", "reset"],
        "acceptance": ["A/B 组轮次清楚", "教师可切换当前组", "每组结果可记录"],
        "quality_gates": ["先听示范再回声", "回声材料必须保持同拍号或同乐句", "小组轮换不打断音乐流程"],
    },
    "rhythm_swap_one_card": {
        "version": "micro_activity_template_v1",
        "micro_activity_template_id": "rhythm_swap_one_card",
        "label": "换一张节奏卡",
        "audience": "primary_school",
        "duration_minutes": 5,
        "classroom_use": "学生在固定小节内替换一张节奏卡，形成新的可拍节奏。",
        "component_ids": ["rhythm_card_bank", "meter_track", "tap_feedback", "teacher_control_bar"],
        "applicable_activity_ids": ["body_percussion_builder", "rhythm_question_answer", "composition_puzzle_core", "rhythm_warmup"],
        "music_elements": ["节奏", "小节", "休止"],
        "student_music_practices": ["create", "tap", "listen"],
        "teaching_stages": ["节奏练习", "创编"],
        "teacher_controls": ["show_hint", "teacher_confirm", "reset"],
        "acceptance": ["换卡后总拍数正确", "可拍出来验证", "教师可确认保存"],
        "quality_gates": ["总拍数必须符合拍号", "替换后必须回放或拍读", "创编不允许随机超小节"],
    },
    "three_word_music_reason": {
        "version": "micro_activity_template_v1",
        "micro_activity_template_id": "three_word_music_reason",
        "label": "三词说依据",
        "audience": "primary_school",
        "duration_minutes": 5,
        "classroom_use": "欣赏或评价时让学生先选 3 个音乐证据词，再说一句听到的依据。",
        "component_ids": ["evidence_word_cards", "rubric_panel", "teacher_control_bar"],
        "applicable_activity_ids": ["listen_choose_explain", "picture_listening_intro", "show_and_peer_feedback", "exit_ticket_review"],
        "music_elements": ["情绪", "速度", "力度", "音色"],
        "student_music_practices": ["listen", "choose", "evaluate", "explain"],
        "teaching_stages": ["评价", "收尾", "欣赏"],
        "teacher_controls": ["result_review", "teacher_confirm", "reset"],
        "acceptance": ["学生必须选词再表达", "教师可保存表达", "可用于出口票"],
        "quality_gates": ["学生必须先选证据词再表达", "证据词必须来自音乐要素", "不能只写喜欢或不喜欢"],
    },
}


def list_micro_activity_templates() -> list[dict[str, Any]]:
    return [validate_micro_activity_template(template) for template in MICRO_ACTIVITY_TEMPLATE_REGISTRY.values()]


def get_micro_activity_template(micro_activity_template_id: str) -> dict[str, Any]:
    template = MICRO_ACTIVITY_TEMPLATE_REGISTRY.get(str(micro_activity_template_id or ""))
    if not template:
        raise ValueError(f"unknown micro activity template: {micro_activity_template_id}")
    return validate_micro_activity_template(template)


def micro_activity_specs_for_activity(activity_id: str) -> list[dict[str, Any]]:
    normalized = str(activity_id or "")
    return [
        template
        for template in list_micro_activity_templates()
        if normalized in template.get("applicable_activity_ids", [])
    ]


def validate_micro_activity_template(template: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(template, dict):
        raise ValueError("micro activity template must be a dict")
    missing = [
        field
        for field in REQUIRED_MICRO_ACTIVITY_FIELDS
        if field not in template or template.get(field) is None or template.get(field) == ""
    ]
    if missing:
        raise ValueError(f"micro activity template missing fields: {', '.join(missing)}")
    if template.get("version") != "micro_activity_template_v1":
        raise ValueError("micro activity template version must be micro_activity_template_v1")
    if template.get("audience") != "primary_school":
        raise ValueError("micro activity template audience must be primary_school")
    duration = template.get("duration_minutes")
    if not isinstance(duration, int) or duration < 1 or duration > 8:
        raise ValueError("micro activity duration must be 1-8 minutes")
    for field in (
        "component_ids",
        "applicable_activity_ids",
        "music_elements",
        "student_music_practices",
        "teaching_stages",
        "teacher_controls",
        "acceptance",
        "quality_gates",
    ):
        if not isinstance(template.get(field), list) or not template[field]:
            raise ValueError(f"micro activity template {field} must be a non-empty list")
    if not set(template["student_music_practices"]).intersection({"listen", "sing", "tap", "move", "play", "create", "evaluate", "choose", "explain"}):
        raise ValueError("micro activity template must include a music practice")
    return deepcopy(template)
