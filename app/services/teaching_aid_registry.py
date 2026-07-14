from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.services.teaching_aid_spec import validate_teaching_aid_spec


_DEFAULT_ACCEPTANCE = {
    "must_bind_material": True,
    "must_be_operable_without_long_text": True,
    "must_export_as_part_of_activity": True,
}


def _asset_policy(
    *,
    real_photo_required: bool = False,
    doubao_required: bool = False,
    image_gen_required: bool = False,
    asset_pack_required: str = "",
) -> dict[str, Any]:
    if real_photo_required:
        source = "real_open_license_photo"
    elif image_gen_required:
        source = "image_gen_generated_png"
    elif doubao_required:
        source = "doubao_generated_png"
    else:
        source = "vector_or_runtime_component"
    return {
        "source": source,
        "real_photo_required": real_photo_required,
        "doubao_required": doubao_required,
        "image_gen_required": image_gen_required,
        "asset_pack_required": asset_pack_required,
        "note": "可演奏乐器卡使用本地 image2 生成皮肤并绑定真实采样；情绪图卡与课堂角色使用生成 PNG 入库；场景图按教案临时生成。",
    }


def _with_asset_policy(
    spec: dict[str, Any],
    *,
    real_photo_required: bool = False,
    doubao_required: bool = False,
    image_gen_required: bool = False,
    asset_pack_required: str = "",
    extra_quality_gates: list[str] | None = None,
) -> dict[str, Any]:
    quality_gates = list(spec.get("quality_gates", []))
    runtime_gates = spec.get("runtime", {}).get("quality_gates", []) if isinstance(spec.get("runtime"), dict) else []
    for gate in [*runtime_gates, *(extra_quality_gates or [])]:
        if gate not in quality_gates:
            quality_gates.append(gate)
    if real_photo_required and "real_photo_required" not in quality_gates:
        quality_gates.append("real_photo_required")
    if image_gen_required and "image_gen_png_file_verified" not in quality_gates:
        quality_gates.append("image_gen_png_file_verified")
    if doubao_required and "doubao_png_file_verified" not in quality_gates:
        quality_gates.append("doubao_png_file_verified")
    spec["real_photo_required"] = real_photo_required
    spec["doubao_required"] = doubao_required
    spec["image_gen_required"] = image_gen_required
    spec["asset_pack_required"] = asset_pack_required
    spec["asset_policy"] = _asset_policy(
        real_photo_required=real_photo_required,
        doubao_required=doubao_required,
        image_gen_required=image_gen_required,
        asset_pack_required=asset_pack_required,
    )
    spec["quality_gates"] = quality_gates
    return spec


def _runtime(
    components: list[str],
    supported_activity_ids: list[str],
    student_event_schema: list[str],
    classroom_evidence: list[str],
    *,
    extra_quality_gates: list[str] | None = None,
) -> dict[str, Any]:
    quality_gates = ["material_bound", "student_operable", "teacher_reset_ready"]
    for gate in extra_quality_gates or []:
        if gate not in quality_gates:
            quality_gates.append(gate)
    return {
        "version": "teaching_aid_runtime_contract_v1",
        "runtime_components": components,
        "supported_activity_ids": supported_activity_ids,
        "student_event_schema": student_event_schema,
        "quality_gates": quality_gates,
        "classroom_evidence": classroom_evidence,
    }


TEACHING_AID_REGISTRY: dict[str, dict[str, Any]] = {
    "rhythm_cards": _with_asset_policy({
        "version": "teaching_aid_spec_v1",
        "aid_id": "rhythm_cards",
        "name": "可播放节奏卡",
        "audience": "primary_school",
        "replace_physical_aid": "实体节奏卡",
        "grade_bands": ["lower_primary", "middle_primary", "upper_primary"],
        "material_entities": ["rhythm_pattern", "meter"],
        "components": ["rhythm_card_bank", "audio_player"],
        "student_actions": ["drag", "listen", "arrange", "tap"],
        "teacher_controls": ["shuffle", "show_answer", "slow_down", "reset"],
        "open_source_dependencies": ["react", "webaudio"],
        "image2_required": False,
        "acceptance": deepcopy(_DEFAULT_ACCEPTANCE),
        "runtime": _runtime(
            ["RhythmCardBank", "AudioPlayer"],
            ["rhythm_warmup", "lyrics_rhythm_practice", "lyrics_rhythm_reading", "xylophone_creation"],
            ["card_id", "action", "timestamp_ms", "beats"],
            ["学生能试听、排列和拍读节奏卡。"],
            extra_quality_gates=["rhythm_value_check"],
        ),
    }),
    "note_value_cards": _with_asset_policy({
        "version": "teaching_aid_spec_v1",
        "aid_id": "note_value_cards",
        "name": "音符休止符时值卡",
        "audience": "primary_school",
        "replace_physical_aid": "实体音符卡和休止符卡",
        "grade_bands": ["middle_primary", "upper_primary"],
        "material_entities": ["rhythm_pattern", "note_value"],
        "components": ["rhythm_card_bank", "tap_feedback"],
        "student_actions": ["match", "classify", "tap", "explain"],
        "teacher_controls": ["show_name", "hide_value", "reset"],
        "open_source_dependencies": ["react"],
        "image2_required": False,
        "acceptance": deepcopy(_DEFAULT_ACCEPTANCE),
        "runtime": _runtime(
            ["RhythmCardBank", "TapFeedback"],
            ["rhythm_warmup"],
            ["card_id", "matched_value", "timestamp_ms"],
            ["学生能把音符/休止符与时值或拍击结果配对。"],
            extra_quality_gates=["rhythm_value_check"],
        ),
    }),
    "solfege_cards": _with_asset_policy({
        "version": "teaching_aid_spec_v1",
        "aid_id": "solfege_cards",
        "name": "唱名排序卡",
        "audience": "primary_school",
        "replace_physical_aid": "实体唱名卡",
        "grade_bands": ["middle_primary", "upper_primary"],
        "material_entities": ["solfege_set", "pitch_motion"],
        "components": ["solfege_card_bank", "audio_player"],
        "student_actions": ["listen", "arrange", "sing_back"],
        "teacher_controls": ["show_solfege", "hide_solfege", "limit_pitch_count", "reset"],
        "open_source_dependencies": ["react", "webaudio"],
        "image2_required": False,
        "acceptance": deepcopy(_DEFAULT_ACCEPTANCE),
        "runtime": _runtime(
            ["SolfegeCardBank", "AudioPlayer"],
            ["solfege_sorting", "solfege_echo_singing", "xylophone_creation"],
            ["solfege", "order_index", "timestamp_ms"],
            ["学生能听音、排序并用唱名模唱。"],
            extra_quality_gates=["pitch_set_limited"],
        ),
    }),
    "pitch_ladder_board": _with_asset_policy({
        "version": "teaching_aid_spec_v1",
        "aid_id": "pitch_ladder_board",
        "name": "音高阶梯板",
        "audience": "primary_school",
        "replace_physical_aid": "实体音高阶梯",
        "grade_bands": ["lower_primary", "middle_primary", "upper_primary"],
        "material_entities": ["pitch_motion", "solfege_set"],
        "components": ["solfege_card_bank", "audio_player"],
        "student_actions": ["listen", "place", "trace", "sing_back"],
        "teacher_controls": ["show_direction", "show_solfege", "reset"],
        "open_source_dependencies": ["react", "svg"],
        "image2_required": False,
        "acceptance": deepcopy(_DEFAULT_ACCEPTANCE),
        "runtime": _runtime(
            ["SolfegeCardBank", "PitchLadderScene"],
            ["solfege_sorting", "solfege_echo_singing"],
            ["pitch_label", "direction", "timestamp_ms"],
            ["学生能把音高方向和唱名位置联系起来。"],
            extra_quality_gates=["pitch_direction_visible"],
        ),
    }),
    "simple_score_board": _with_asset_policy({
        "version": "teaching_aid_spec_v1",
        "aid_id": "simple_score_board",
        "name": "简谱跟读板",
        "audience": "primary_school",
        "replace_physical_aid": "黑板简谱和投影片",
        "grade_bands": ["upper_primary"],
        "material_entities": ["numbered_score", "rhythm_pattern", "audio_clip"],
        "components": ["score_following_board", "audio_player"],
        "student_actions": ["listen", "read", "sing_back", "explain"],
        "teacher_controls": ["replay", "show_solfege", "hide_solfege", "reset"],
        "open_source_dependencies": ["react", "svg", "webaudio"],
        "image2_required": False,
        "acceptance": deepcopy(_DEFAULT_ACCEPTANCE),
        "runtime": _runtime(
            ["SimpleScoreFollowingActivity", "AudioPlayer"],
            ["simple_score_following"],
            ["score_line_index", "symbol_index", "action", "timestamp_ms"],
            ["学生能把简谱数字、唱名、节奏和听觉材料对应起来。"],
            extra_quality_gates=["listen_before_read", "score_to_sound_mapping", "rhythm_value_check", "meter_bound"],
        ),
    }),
    "melody_contour_board": _with_asset_policy({
        "version": "teaching_aid_spec_v1",
        "aid_id": "melody_contour_board",
        "name": "旋律线跟踪板",
        "audience": "primary_school",
        "replace_physical_aid": "黑板旋律线和手势提示",
        "grade_bands": ["middle_primary", "upper_primary"],
        "material_entities": ["pitch_motion", "melody_phrase", "audio_clip"],
        "components": ["melody_contour_line", "audio_player"],
        "student_actions": ["listen", "move", "sing_back", "explain"],
        "teacher_controls": ["replay", "show_hint", "hide_hint", "reset"],
        "open_source_dependencies": ["react", "svg", "webaudio"],
        "image2_required": False,
        "acceptance": deepcopy(_DEFAULT_ACCEPTANCE),
        "runtime": _runtime(
            ["MelodyContourTraceActivity", "MelodyContourLine", "AudioPlayer"],
            ["melody_contour_trace"],
            ["drawing_points", "timestamp_ms", "drawing_complete"],
            ["学生能先听旋律，再自由描画高低走向，并回到唱回。"],
            extra_quality_gates=["listen_before_trace", "pitch_direction_visible", "singing_transfer_ready"],
        ),
    }),
    "lyrics_rhythm_strip": _with_asset_policy({
        "version": "teaching_aid_spec_v1",
        "aid_id": "lyrics_rhythm_strip",
        "name": "歌词节奏条",
        "audience": "primary_school",
        "replace_physical_aid": "实体歌词条和节奏卡",
        "grade_bands": ["lower_primary", "middle_primary", "upper_primary"],
        "material_entities": ["lyrics_phrase", "rhythm_pattern", "meter"],
        "components": ["lyrics_strip", "meter_track", "audio_player"],
        "student_actions": ["read", "tap", "arrange", "explain"],
        "teacher_controls": ["show_stress", "hide_rhythm", "slow_down", "reset"],
        "open_source_dependencies": ["react", "svg"],
        "image2_required": False,
        "acceptance": deepcopy(_DEFAULT_ACCEPTANCE),
        "runtime": _runtime(
            ["LyricsRhythmActivity", "LyricsStrip", "MeterTrack"],
            ["phrase_singing_practice", "lyrics_rhythm_practice", "lyrics_rhythm_reading"],
            ["phrase_index", "action", "timestamp_ms"],
            ["学生能按稳定拍读歌词并回到歌曲演唱。"],
            extra_quality_gates=["phrase_loop_ready"],
        ),
    }),
    "form_cards": _with_asset_policy({
        "version": "teaching_aid_spec_v1",
        "aid_id": "form_cards",
        "name": "曲式结构卡",
        "audience": "primary_school",
        "replace_physical_aid": "实体曲式卡",
        "grade_bands": ["upper_primary"],
        "material_entities": ["form_structure", "audio_clip"],
        "components": ["form_card_timeline", "audio_player"],
        "student_actions": ["listen", "order", "compare", "explain"],
        "teacher_controls": ["replay_section", "show_hint", "reset"],
        "open_source_dependencies": ["react", "svg"],
        "image2_required": False,
        "acceptance": deepcopy(_DEFAULT_ACCEPTANCE),
        "runtime": _runtime(
            ["FormTreasureScene", "FormCardTimeline", "AudioPlayer"],
            ["form_ordering"],
            ["section_id", "placed_index", "timestamp_ms"],
            ["学生能复听段落并排列曲式结构。"],
            extra_quality_gates=["section_relisten_ready"],
        ),
    }),
    "theme_cards": _with_asset_policy({
        "version": "teaching_aid_spec_v1",
        "aid_id": "theme_cards",
        "name": "主题再现动作卡",
        "audience": "primary_school",
        "replace_physical_aid": "实体主题卡和动作提示卡",
        "grade_bands": ["middle_primary", "upper_primary"],
        "material_entities": ["audio_clip", "theme_windows"],
        "components": ["theme_return_timeline", "movement_action_cards", "audio_player"],
        "student_actions": ["listen", "move", "explain"],
        "teacher_controls": ["replay", "replay_section", "show_hint", "reset"],
        "open_source_dependencies": ["react", "webaudio"],
        "image2_required": False,
        "acceptance": deepcopy(_DEFAULT_ACCEPTANCE),
        "runtime": _runtime(
            ["ThemeReturnActionActivity", "ThemeReturnTimeline", "MovementActionCards"],
            ["theme_return_action"],
            ["action", "evidence_terms", "timestamp_sec", "status"],
            ["学生能在主题再现时间窗内做动作，并用旋律或节奏依据说明。"],
            extra_quality_gates=["listen_before_action", "theme_window_bound", "evidence_required"],
        ),
    }),
    "instrument_cards": _with_asset_policy({
        "version": "teaching_aid_spec_v1",
        "aid_id": "instrument_cards",
        "name": "乐器音色证据卡",
        "audience": "primary_school",
        "replace_physical_aid": "实体乐器卡和音色词卡",
        "grade_bands": ["middle_primary", "upper_primary"],
        "material_entities": ["timbre_set", "instrument_pool", "audio_clip"],
        "components": ["instrument_card_grid", "compare_player"],
        "student_actions": ["listen", "match", "compare", "explain"],
        "teacher_controls": ["replay", "show_family", "reset"],
        "open_source_dependencies": ["react"],
        "image2_required": False,
        "acceptance": deepcopy(_DEFAULT_ACCEPTANCE),
        "runtime": _runtime(
            ["TimbreDetectiveScene", "InstrumentCardGrid", "ComparePlayer"],
            ["instrument_timbre_match", "instrument_family_sorting"],
            ["instrument_id", "timbre_trait", "choice", "timestamp_ms"],
            ["学生能先听声音，再选择乐器和音色证据。"],
            extra_quality_gates=["listen_before_choice", "evidence_required"],
        ),
    }, image_gen_required=True, asset_pack_required="generated_playable_instrument_pack", extra_quality_gates=["generated_instrument_skin_visible", "real_sample_playback"]),
    "timbre_evidence_cards": _with_asset_policy({
        "version": "teaching_aid_spec_v1",
        "aid_id": "timbre_evidence_cards",
        "name": "音色证据词卡",
        "audience": "primary_school",
        "replace_physical_aid": "实体音色词卡",
        "grade_bands": ["middle_primary", "upper_primary"],
        "material_entities": ["timbre_set", "audio_clip"],
        "components": ["answer_choice_grid", "compare_player"],
        "student_actions": ["listen", "choose", "explain"],
        "teacher_controls": ["replay", "show_answer", "reset"],
        "open_source_dependencies": ["react", "radix"],
        "image2_required": False,
        "acceptance": deepcopy(_DEFAULT_ACCEPTANCE),
        "runtime": _runtime(
            ["AnswerChoiceGrid", "ComparePlayer"],
            ["instrument_timbre_match", "listen_choose_explain"],
            ["evidence_term", "choice", "timestamp_ms"],
            ["学生能用清脆、柔和、明亮等音色词说明听辨依据。"],
            extra_quality_gates=["listen_before_choice", "evidence_required"],
        ),
    }),
    "tempo_dynamic_word_cards": _with_asset_policy({
        "version": "teaching_aid_spec_v1",
        "aid_id": "tempo_dynamic_word_cards",
        "name": "速度力度词卡",
        "audience": "primary_school",
        "replace_physical_aid": "实体速度力度词卡",
        "grade_bands": ["lower_primary", "middle_primary", "upper_primary"],
        "material_entities": ["audio_clip", "expression_trait"],
        "components": ["answer_choice_grid", "rubric_panel"],
        "student_actions": ["listen", "choose", "explain"],
        "teacher_controls": ["replay", "hide_words", "reset"],
        "open_source_dependencies": ["react", "radix"],
        "image2_required": False,
        "acceptance": deepcopy(_DEFAULT_ACCEPTANCE),
        "runtime": _runtime(
            ["AnswerChoiceGrid", "RubricPanel"],
            ["picture_listening_intro", "listen_choose_explain", "exit_ticket_review"],
            ["term_id", "choice", "timestamp_ms"],
            ["学生能听辨快慢、强弱并用词卡表达依据。"],
            extra_quality_gates=["listen_before_choice", "music_evidence_required"],
        ),
    }),
    "body_percussion_cards": _with_asset_policy({
        "version": "teaching_aid_spec_v1",
        "aid_id": "body_percussion_cards",
        "name": "身体打击动作卡",
        "audience": "primary_school",
        "replace_physical_aid": "实体身体律动动作卡",
        "grade_bands": ["lower_primary", "middle_primary"],
        "material_entities": ["rhythm_pattern", "meter"],
        "components": ["body_action_cards", "meter_track"],
        "student_actions": ["arrange", "move", "tap", "perform"],
        "teacher_controls": ["show_beat", "slow_down", "reset"],
        "open_source_dependencies": ["react"],
        "image2_required": False,
        "acceptance": deepcopy(_DEFAULT_ACCEPTANCE),
        "runtime": _runtime(
            ["BodyActionCards", "MeterTrack"],
            ["meter_body_movement", "body_percussion_builder"],
            ["action_id", "beat_index", "timestamp_ms"],
            ["学生能用身体动作表现节拍、强弱和休止。"],
            extra_quality_gates=["meter_bound"],
        ),
    }),
    "mood_picture_cards": _with_asset_policy({
        "version": "teaching_aid_spec_v1",
        "aid_id": "mood_picture_cards",
        "name": "听赏情绪图卡",
        "audience": "primary_school",
        "replace_physical_aid": "实体情绪图卡",
        "grade_bands": ["lower_primary", "middle_primary"],
        "material_entities": ["audio_clip", "expression_trait"],
        "components": ["picture_prompt_cards", "compare_player"],
        "student_actions": ["listen", "choose", "explain"],
        "teacher_controls": ["replay", "hide_words", "reset"],
        "open_source_dependencies": ["react"],
        "image2_required": False,
        "image_gen_required": True,
        "acceptance": deepcopy(_DEFAULT_ACCEPTANCE),
        "runtime": _runtime(
            ["ListeningChoiceActivity", "PicturePromptCards", "ComparePlayer"],
            ["picture_listening_intro", "listen_choose_explain"],
            ["card_id", "evidence_term", "timestamp_ms"],
            ["学生能初听后选择情绪图卡并说音乐依据。"],
            extra_quality_gates=["listen_before_choice", "evidence_required"],
        ),
    }, image_gen_required=True, asset_pack_required="music_mood_picture_pack"),
    "graphic_score_cards": _with_asset_policy({
        "version": "teaching_aid_spec_v1",
        "aid_id": "graphic_score_cards",
        "name": "图形谱编辑板",
        "audience": "primary_school",
        "replace_physical_aid": "实体图形谱板",
        "grade_bands": ["middle_primary", "upper_primary"],
        "material_entities": ["graphic_symbol_meanings", "meter", "rhythm_pattern", "solfege_set"],
        "components": ["graphic_score_canvas", "rhythm_card_bank", "solfege_card_bank", "audio_player"],
        "student_actions": ["draw", "listen", "revise", "explain"],
        "teacher_controls": ["clear", "play", "reset"],
        "open_source_dependencies": ["react", "svg"],
        "image2_required": False,
        "acceptance": deepcopy(_DEFAULT_ACCEPTANCE),
        "runtime": _runtime(
            ["GraphicScoreActivity", "GraphicScoreBoard", "RhythmCardBank", "SolfegeCardBank", "AudioPlayer"],
            ["graphic_score_create", "xylophone_creation"],
            ["shape_id", "music_meaning", "timestamp_ms"],
            ["学生能用图形表示节奏、力度或旋律线并说明。"],
            extra_quality_gates=[
                "symbol_meaning_bound",
                "rhythm_value_check",
                "pitch_playback_mapping",
                "playback_ready",
            ],
        ),
    }),
    "group_mission_cards": _with_asset_policy({
        "version": "teaching_aid_spec_v1",
        "aid_id": "group_mission_cards",
        "name": "小组任务卡",
        "audience": "primary_school",
        "replace_physical_aid": "实体小组任务卡",
        "grade_bands": ["lower_primary", "middle_primary", "upper_primary"],
        "material_entities": ["classroom_group_task"],
        "components": ["group_task_board"],
        "student_actions": ["receive", "practice", "relay", "perform"],
        "teacher_controls": ["assign_group", "mark_done", "reset"],
        "open_source_dependencies": ["react", "radix"],
        "image2_required": False,
        "acceptance": deepcopy(_DEFAULT_ACCEPTANCE),
        "runtime": _runtime(
            ["GroupTaskBoard", "OrffEnsembleActivity"],
            ["orff_percussion_ensemble", "classroom_band_roles", "group_relay_performance", "show_and_peer_feedback"],
            ["group_id", "task_status", "timestamp_ms"],
            ["学生能按小组任务进入、轮奏或展示。"],
            extra_quality_gates=["group_state_ready"],
        ),
    }),
    "performance_rubric": _with_asset_policy({
        "version": "teaching_aid_spec_v1",
        "aid_id": "performance_rubric",
        "name": "课堂表现评价量规",
        "audience": "primary_school",
        "replace_physical_aid": "实体评价表",
        "grade_bands": ["middle_primary", "upper_primary"],
        "material_entities": ["assessment_criteria"],
        "components": ["rubric_panel"],
        "student_actions": ["self_assess", "peer_assess", "explain"],
        "teacher_controls": ["edit_criteria", "save", "reset"],
        "open_source_dependencies": ["react", "radix"],
        "image2_required": False,
        "acceptance": deepcopy(_DEFAULT_ACCEPTANCE),
        "runtime": _runtime(
            ["RubricPanel", "PeerFeedbackActivity"],
            ["group_relay_performance", "show_and_peer_feedback", "exit_ticket_review", "orff_percussion_ensemble", "classroom_band_roles"],
            ["criterion_id", "rating", "timestamp_ms"],
            ["评价维度能对应本课音乐目标并记录结果。"],
            extra_quality_gates=["record_ready"],
        ),
    }),
}


TEACHING_AID_ALIASES = {
    "instrument_evidence_cards": "instrument_cards",
    "theme_action_cards": "theme_cards",
    "graphic_score_board": "graphic_score_cards",
}


def list_teaching_aids() -> list[dict[str, Any]]:
    specs = [validate_teaching_aid_spec(spec) for spec in TEACHING_AID_REGISTRY.values()]
    for alias_id, canonical_id in TEACHING_AID_ALIASES.items():
        alias_spec = validate_teaching_aid_spec(TEACHING_AID_REGISTRY[canonical_id])
        alias_spec["aid_id"] = alias_id
        alias_spec["canonical_aid_id"] = canonical_id
        alias_spec["legacy_alias"] = True
        specs.append(alias_spec)
    return specs


def get_teaching_aid(aid_id: str) -> dict[str, Any]:
    raw_id = str(aid_id or "")
    canonical = raw_id if raw_id in TEACHING_AID_REGISTRY else TEACHING_AID_ALIASES.get(raw_id, raw_id)
    spec = TEACHING_AID_REGISTRY.get(canonical)
    if not spec:
        raise ValueError(f"unknown teaching aid: {aid_id}")
    return validate_teaching_aid_spec(spec)
