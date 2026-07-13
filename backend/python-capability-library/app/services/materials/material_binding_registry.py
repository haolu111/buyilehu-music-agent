# 定义不同活动如何绑定音乐材料
from __future__ import annotations

from copy import deepcopy
from typing import Any


MATERIAL_BINDER_SPEC_VERSION = "material_binder_spec_v1"

REQUIRED_FIELDS = (
    "version",
    "binder_id",
    "label",
    "audience",
    "primary_material_kind",
    "input_entities",
    "output_entities",
    "applicable_activity_ids",
    "student_music_practices",
    "music_education_use",
    "quality_gates",
)


def _binder(
    binder_id: str,
    label: str,
    *,
    primary_material_kind: str,
    input_entities: list[str],
    output_entities: list[str],
    applicable_activity_ids: list[str],
    student_music_practices: list[str],
    music_education_use: str,
    quality_gates: list[str],
) -> dict[str, Any]:
    return {
        "version": MATERIAL_BINDER_SPEC_VERSION,
        "binder_id": binder_id,
        "label": label,
        "audience": "primary_school",
        "primary_material_kind": primary_material_kind,
        "input_entities": input_entities,
        "output_entities": output_entities,
        "applicable_activity_ids": applicable_activity_ids,
        "student_music_practices": student_music_practices,
        "music_education_use": music_education_use,
        "quality_gates": quality_gates,
    }


MATERIAL_BINDERS: dict[str, dict[str, Any]] = {
    "song_phrase_binder": _binder(
        "song_phrase_binder",
        "歌曲乐句绑定",
        primary_material_kind="song_phrase",
        input_entities=["lyrics_phrase", "melody_phrase", "audio_clip", "song_title"],
        output_entities=["phrase_player_segments", "lyrics_strip_phrases", "difficult_phrase"],
        applicable_activity_ids=["phrase_singing_practice", "phrase_loop_singing", "solfege_echo_singing", "song_audio_workbench_activity", "score_audio_sync_practice", "vocal_choir_training_activity"],
        student_music_practices=["listen", "sing", "explain"],
        music_education_use="把歌曲歌词、旋律和音频切成可听一句、唱一句、教师确认的学唱材料。",
        quality_gates=["phrase_count_matches", "audio_boundary_confirmable", "teacher_confirm_required"],
    ),
    "lyrics_rhythm_binder": _binder(
        "lyrics_rhythm_binder",
        "歌词节奏绑定",
        primary_material_kind="lyrics_rhythm",
        input_entities=["lyrics_phrase", "meter", "rhythm_pattern"],
        output_entities=["lyrics_rhythm_strip", "stress_marks", "read_tap_sequence"],
        applicable_activity_ids=["lyrics_rhythm_practice", "lyrics_rhythm_reading"],
        student_music_practices=["listen", "read", "tap", "sing"],
        music_education_use="把歌词、拍号和节奏型绑定成先按拍读、再拍出歌词节奏、最后回到演唱的材料。",
        quality_gates=["lyrics_phrase_present", "meter_bound", "rhythm_value_check"],
    ),
    "rhythm_pattern_binder": _binder(
        "rhythm_pattern_binder",
        "节奏型绑定",
        primary_material_kind="rhythm_pattern",
        input_entities=["rhythm_pattern", "meter", "bpm"],
        output_entities=["rhythm_cards", "meter_track", "tap_judgement_targets"],
        applicable_activity_ids=["rhythm_warmup", "lyrics_rhythm_practice", "lyrics_rhythm_reading", "meter_body_movement", "steady_beat_walk", "strong_weak_beat_circle", "rhythm_question_answer", "body_percussion_builder", "ear_training_practice"],
        student_music_practices=["listen", "tap", "move", "create"],
        music_education_use="把节奏文本或教师输入转成可试听、可拍击、可校验小节长度的节奏卡和节拍轨。",
        quality_gates=["rhythm_value_check", "meter_bound", "timing_feedback_ready"],
    ),
    "solfege_set_binder": _binder(
        "solfege_set_binder",
        "唱名集合绑定",
        primary_material_kind="solfege_set",
        input_entities=["solfege_set", "pitch_motion", "melody_phrase"],
        output_entities=["solfege_cards", "pitch_ladder_steps", "limited_pitch_set"],
        applicable_activity_ids=["solfege_sorting", "solfege_echo_singing", "melody_contour_trace", "simple_score_following", "xylophone_creation", "score_audio_sync_practice", "ear_training_practice", "vocal_choir_training_activity"],
        student_music_practices=["listen", "sing", "arrange", "play"],
        music_education_use="把唱名、音高走向和旋律短句绑定到唱名卡、音高阶梯和虚拟音条琴限制音级。",
        quality_gates=["pitch_set_limited", "singback_confirmable", "pitch_motion_present"],
    ),
    "listening_evidence_binder": _binder(
        "listening_evidence_binder",
        "欣赏证据绑定",
        primary_material_kind="listening_evidence",
        input_entities=["audio_clip", "expression_trait", "evidence_terms"],
        output_entities=["mood_choices", "evidence_word_cards", "relisten_prompts"],
        applicable_activity_ids=["picture_listening_intro", "listen_choose_explain", "lesson_opening_hook", "exit_ticket_review"],
        student_music_practices=["listen", "choose", "explain", "assess"],
        music_education_use="把欣赏音频、情绪/速度/力度目标和证据词绑定成先听、选择、说依据和复听验证。",
        quality_gates=["audio_bound", "evidence_required", "relisten_available"],
    ),
    "timbre_pool_binder": _binder(
        "timbre_pool_binder",
        "音色池绑定",
        primary_material_kind="instrument_pool",
        input_entities=["instrument_pool", "instrument_family_set", "timbre_set", "audio_clip"],
        output_entities=["instrument_cards", "timbre_word_cards", "compare_player_items"],
        applicable_activity_ids=["instrument_timbre_match", "instrument_family_sorting"],
        student_music_practices=["listen", "classify", "match", "explain"],
        music_education_use="把乐器池、家族、音色词、生成乐器皮肤和采样音频绑定成先听声音、再操作乐器卡和说依据的材料。",
        quality_gates=["instrument_pool_present", "generated_skin_gate", "real_sample_or_labeled_approximation_ready"],
    ),
    "form_segment_binder": _binder(
        "form_segment_binder",
        "曲式段落绑定",
        primary_material_kind="form_structure",
        input_entities=["form_structure", "theme_windows", "audio_clip"],
        output_entities=["form_cards", "section_timeline", "theme_return_windows"],
        applicable_activity_ids=["form_ordering", "theme_return_action"],
        student_music_practices=["listen", "order", "move", "explain"],
        music_education_use="把 A/B/C 段、主题再现时间窗和音频段落绑定成复听排序或主题回来就动作的活动材料。",
        quality_gates=["section_windows_present", "audio_bound", "relisten_available"],
    ),
    "graphic_score_binder": _binder(
        "graphic_score_binder",
        "图形谱材料绑定",
        primary_material_kind="graphic_score_material",
        input_entities=["graphic_symbol_meanings", "meter", "music_element_focus"],
        output_entities=["graphic_symbol_bank", "graphic_score_slots", "playback_mapping"],
        applicable_activity_ids=["graphic_score_create"],
        student_music_practices=["listen", "create", "revise", "explain"],
        music_education_use="把点、线、块等图形含义和节拍格绑定成可摆放、可回放、可修改并能说明高低长短强弱的图形谱材料。",
        quality_gates=["symbol_meaning_present", "meter_bound", "playback_mapping_ready"],
    ),
    "group_task_binder": _binder(
        "group_task_binder",
        "小组任务绑定",
        primary_material_kind="classroom_group_task",
        input_entities=["classroom_group_task", "group_count", "part_assignments", "assessment_criteria"],
        output_entities=["group_task_board", "role_assignment_cards", "performance_rubric"],
        applicable_activity_ids=["classroom_band_roles", "orff_percussion_ensemble", "group_relay_performance", "show_and_peer_feedback", "ensemble_conductor_rehearsal"],
        student_music_practices=["listen", "cooperate", "perform", "assess"],
        music_education_use="把班级分组、声部任务和评价维度绑定成小组任务卡、角色分配和展示评价材料。",
        quality_gates=["group_task_present", "role_assignment_clear", "rubric_available"],
    ),
}


def list_material_binders() -> list[dict[str, Any]]:
    return [validate_material_binder_spec(binder) for binder in MATERIAL_BINDERS.values()]


def get_material_binder(binder_id: str) -> dict[str, Any]:
    binder = MATERIAL_BINDERS.get(str(binder_id or ""))
    if not binder:
        raise ValueError(f"unknown material binder: {binder_id}")
    return validate_material_binder_spec(binder)


def material_binder_specs_for_activity(activity_id: str) -> list[dict[str, Any]]:
    return [
        validate_material_binder_spec(binder)
        for binder in MATERIAL_BINDERS.values()
        if activity_id in binder.get("applicable_activity_ids", [])
    ]


def validate_material_binder_spec(binder: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(binder, dict):
        raise ValueError("material binder spec must be a dict")
    missing = [field for field in REQUIRED_FIELDS if not binder.get(field)]
    if missing:
        raise ValueError(f"material binder spec missing fields: {', '.join(missing)}")
    if binder.get("version") != MATERIAL_BINDER_SPEC_VERSION:
        raise ValueError("material binder spec version must be material_binder_spec_v1")
    if binder.get("audience") != "primary_school":
        raise ValueError("material binder spec audience must be primary_school")
    return deepcopy(binder)
