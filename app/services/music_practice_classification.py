from __future__ import annotations

from copy import deepcopy
from typing import Any, Iterable


ROLE_PROFILES: dict[str, dict[str, Any]] = {
    "core_practice": {
        "label": "核心音乐实践",
        "web_boundary": "网页提供音乐材料、重复练习和必要过程记录；学生必须拍、动、唱、画、奏、创或合作表现。",
        "teacher_boundary": "教师示范、倾听学生真实表现，并判断音准、音色、力度、合作和音乐表达。",
        "agent_default_allowed": True,
    },
    "practice_with_evidence": {
        "label": "实践主导＋网页证据",
        "web_boundary": "网页可记录排序、点击、拍击或对比证据，但这些证据不能替代后续唱、奏、说或实践。",
        "teacher_boundary": "教师确认学生是否真正把听辨结果迁移到声音、身体或乐器表现。",
        "agent_default_allowed": True,
    },
    "listening_evidence": {
        "label": "听赏证据／选择整理",
        "web_boundary": "网页只用于复听后的选择、匹配、分类或排序，并保留学生说出音乐依据的机会。",
        "teacher_boundary": "教师追问听觉依据，并把结果带回动作、歌唱、演奏或后续实践；不得将其作为整节课主活动。",
        "agent_default_allowed": False,
    },
    "closure_assessment": {
        "label": "课末反馈／教师再教学依据",
        "web_boundary": "网页只收集简短回顾证据，不能自动判定整节课的音乐学习已经完成。",
        "teacher_boundary": "教师依据反馈决定补练、调整教学或追问，不以一次答题替代课堂评价。",
        "agent_default_allowed": False,
    },
    "practice_material": {
        "label": "实践材料",
        "web_boundary": "提供可听、可看、可操作的音乐材料，服务学生实践而非代替教师讲解。",
        "teacher_boundary": "教师选择材料、控制难度，并把操作带回实际音乐表现。",
        "agent_default_allowed": True,
    },
    "web_practice_support": {
        "label": "网页特有实践支撑",
        "web_boundary": "提供同步、循环、变速、分轨、时间证据或可听对比等网页特有能力。",
        "teacher_boundary": "教师决定何时使用、听什么和如何把结果迁移到真实表现。",
        "agent_default_allowed": True,
    },
    "evidence_capture": {
        "label": "网页证据采集",
        "web_boundary": "采集选择、匹配、排序或点击等有限证据，不构成完整音乐能力评价。",
        "teacher_boundary": "教师补充追问、示范和对学生音乐表现的最终判断。",
        "agent_default_allowed": False,
    },
    "teacher_orchestration": {
        "label": "教师组织与确认",
        "web_boundary": "协助分组、节奏控制、记录和提示，不自动替代教师决策。",
        "teacher_boundary": "教师拥有确认、撤回、评价和教学调整的最终权力。",
        "agent_default_allowed": False,
    },
    "backend_only": {
        "label": "后台材料处理",
        "web_boundary": "把教师确认的材料转换为结构化数据，不能作为学生页面或自动教师。",
        "teacher_boundary": "教师确认歌曲、谱面、歌词、音频和教学目标后才允许调用。",
        "agent_default_allowed": False,
    },
}


ACTIVITY_ROLE_BY_ID = {
    "rhythm_warmup": "core_practice",
    "meter_body_movement": "core_practice",
    "steady_beat_walk": "core_practice",
    "phrase_singing_practice": "core_practice",
    "phrase_loop_singing": "core_practice",
    "lyrics_rhythm_practice": "core_practice",
    "lyrics_rhythm_reading": "core_practice",
    "rhythm_question_answer": "core_practice",
    "solfege_echo_singing": "core_practice",
    "melody_contour_trace": "core_practice",
    "simple_score_following": "core_practice",
    "theme_return_action": "core_practice",
    "graphic_score_create": "core_practice",
    "body_percussion_builder": "core_practice",
    "xylophone_creation": "core_practice",
    "orff_percussion_ensemble": "core_practice",
    "classroom_band_roles": "core_practice",
    "group_relay_performance": "core_practice",
    "show_and_peer_feedback": "core_practice",
    "score_audio_sync_practice": "core_practice",
    "vocal_choir_training_activity": "core_practice",
    "ensemble_conductor_rehearsal": "core_practice",
    "solfege_sorting": "listening_evidence",
    "song_audio_workbench_activity": "practice_with_evidence",
    "ear_training_practice": "practice_with_evidence",
    "picture_listening_intro": "listening_evidence",
    "listen_choose_explain": "listening_evidence",
    "lesson_opening_hook": "listening_evidence",
    "instrument_timbre_match": "listening_evidence",
    "form_ordering": "listening_evidence",
    "instrument_family_sorting": "listening_evidence",
    "exit_ticket_review": "closure_assessment",
}

COMPONENT_ROLE_BY_ID = {
    "game_hud": "web_practice_support",
    "round_prompt_panel": "web_practice_support",
    "reward_panel": "web_practice_support",
    "progress_path": "web_practice_support",
    "answer_choice_grid": "evidence_capture",
    "drag_sort_board": "evidence_capture",
    "teacher_confirm_overlay": "teacher_orchestration",
    "classroom_scoreboard": "teacher_orchestration",
    "audio_player": "practice_material",
    "compare_player": "practice_material",
    "rhythm_card_bank": "practice_material",
    "solfege_card_bank": "practice_material",
    "score_following_board": "practice_material",
    "melody_contour_line": "practice_material",
    "graphic_score_canvas": "practice_material",
    "lyrics_strip": "practice_material",
    "form_card_timeline": "practice_material",
    "theme_return_timeline": "practice_material",
    "movement_action_cards": "practice_material",
    "instrument_card_grid": "practice_material",
    "meter_track": "practice_material",
    "tap_feedback": "web_practice_support",
    "body_action_cards": "practice_material",
    "picture_prompt_cards": "evidence_capture",
    "teacher_control_bar": "teacher_orchestration",
    "group_task_board": "teacher_orchestration",
    "rubric_panel": "teacher_orchestration",
    "song_audio_workbench": "web_practice_support",
    "score_audio_sync_player": "web_practice_support",
    "ear_training_engine": "web_practice_support",
    "vocal_choir_training": "web_practice_support",
    "ensemble_conductor": "web_practice_support",
}

TEACHING_AID_ROLE_BY_ID = {
    "rhythm_cards": "practice_material",
    "note_value_cards": "practice_material",
    "solfege_cards": "practice_material",
    "pitch_ladder_board": "practice_material",
    "simple_score_board": "practice_material",
    "melody_contour_board": "practice_material",
    "lyrics_rhythm_strip": "practice_material",
    "theme_cards": "practice_material",
    "body_percussion_cards": "practice_material",
    "graphic_score_cards": "practice_material",
    "form_cards": "evidence_capture",
    "instrument_cards": "evidence_capture",
    "timbre_evidence_cards": "evidence_capture",
    "tempo_dynamic_word_cards": "evidence_capture",
    "mood_picture_cards": "evidence_capture",
    "group_mission_cards": "teacher_orchestration",
    "performance_rubric": "teacher_orchestration",
}

MATERIAL_BINDER_ROLE_BY_ID = {
    "song_phrase_binder": "backend_only",
    "lyrics_rhythm_binder": "backend_only",
    "rhythm_pattern_binder": "backend_only",
    "solfege_set_binder": "backend_only",
    "listening_evidence_binder": "backend_only",
    "timbre_pool_binder": "backend_only",
    "form_segment_binder": "backend_only",
    "graphic_score_binder": "backend_only",
    "group_task_binder": "backend_only",
}


def role_profile(role: str) -> dict[str, Any]:
    try:
        return deepcopy(ROLE_PROFILES[role]) | {"role": role}
    except KeyError as exc:
        raise ValueError(f"unknown music practice role: {role}") from exc


def activity_practice_profile(activity_id: str) -> dict[str, Any]:
    return role_profile(_role_for(ACTIVITY_ROLE_BY_ID, activity_id, "activity"))


def component_practice_profile(component_id: str) -> dict[str, Any]:
    return role_profile(_role_for(COMPONENT_ROLE_BY_ID, component_id, "component"))


def teaching_aid_practice_profile(aid_id: str) -> dict[str, Any]:
    return role_profile(_role_for(TEACHING_AID_ROLE_BY_ID, aid_id, "teaching aid"))


def material_binder_practice_profile(binder_id: str) -> dict[str, Any]:
    return role_profile(_role_for(MATERIAL_BINDER_ROLE_BY_ID, binder_id, "material binder"))


def activity_allowed_as_default_main(activity_id: str) -> bool:
    return bool(activity_practice_profile(activity_id)["agent_default_allowed"])


def uncovered_activity_ids(activity_ids: Iterable[str]) -> list[str]:
    return _uncovered(ACTIVITY_ROLE_BY_ID, activity_ids)


def uncovered_component_ids(component_ids: Iterable[str]) -> list[str]:
    return _uncovered(COMPONENT_ROLE_BY_ID, component_ids)


def uncovered_teaching_aid_ids(aid_ids: Iterable[str]) -> list[str]:
    return _uncovered(TEACHING_AID_ROLE_BY_ID, aid_ids)


def uncovered_material_binder_ids(binder_ids: Iterable[str]) -> list[str]:
    return _uncovered(MATERIAL_BINDER_ROLE_BY_ID, binder_ids)


def _role_for(mapping: dict[str, str], item_id: str, item_kind: str) -> str:
    try:
        return mapping[item_id]
    except KeyError as exc:
        raise ValueError(f"unclassified {item_kind}: {item_id}") from exc


def _uncovered(mapping: dict[str, str], item_ids: Iterable[str]) -> list[str]:
    return sorted(item_id for item_id in item_ids if item_id not in mapping)
