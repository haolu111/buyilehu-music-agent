from __future__ import annotations

from copy import deepcopy
from typing import Any


REQUIRED_RULE_FIELDS = (
    "version",
    "rule_id",
    "name",
    "audience",
    "rule_family",
    "inputs",
    "outputs",
    "music_elements",
    "student_practices",
    "feedback_contract",
    "pedagogy_guardrails",
    "applicable_activity_ids",
)

FEEDBACK_CONTRACT = {
    "status": "规则判定状态，不只使用 correct/wrong。",
    "music_reason": "说明学生表现背后的音乐原因。",
    "student_feedback": "给学生的短反馈，使用小学课堂语言。",
    "teacher_suggestion": "给教师的下一步调节建议。",
    "next_practice": "建议回到听、唱、奏、动、读、创、评中的哪一步。",
    "requires_teacher_confirm": "是否需要教师确认，尤其是歌唱、展示、创编和主观评价。",
}


def _rule(
    rule_id: str,
    name: str,
    *,
    rule_family: str,
    inputs: list[str],
    outputs: list[str],
    music_elements: list[str],
    student_practices: list[str],
    pedagogy_guardrails: list[str],
    applicable_activity_ids: list[str],
    feedback_kind: str = "",
) -> dict[str, Any]:
    return {
        "version": "music_rule_spec_v1",
        "rule_id": rule_id,
        "name": name,
        "audience": "primary_school",
        "rule_family": rule_family,
        "inputs": inputs,
        "outputs": outputs,
        "music_elements": music_elements,
        "student_practices": student_practices,
        "feedback_contract": deepcopy(FEEDBACK_CONTRACT),
        "pedagogy_guardrails": pedagogy_guardrails,
        "applicable_activity_ids": applicable_activity_ids,
        "feedback_kind": feedback_kind or rule_family,
    }


COMMON_RHYTHM_GUARDRAILS = [
    "低段重点反馈稳不稳、早还是晚，不强调复杂时值名称。",
    "休止符练习要提示停住也是音乐表现。",
]

COMMON_LISTENING_GUARDRAILS = [
    "欣赏和音色活动必须先听声音，再选择或分类。",
    "选择后必须鼓励学生说出音乐依据。",
]


MUSIC_RULE_REGISTRY: dict[str, dict[str, Any]] = {
    "rhythm_timing_judgement": _rule(
        "rhythm_timing_judgement",
        "拍点早晚判定",
        rule_family="rhythm",
        inputs=["tap_time_ms", "target_time_ms", "target_event_id", "target_consumed", "rest_error", "tolerance_ms", "bpm"],
        outputs=["correct", "on_time", "early", "late", "missed", "miss", "extra", "rest_error"],
        music_elements=["稳定拍", "节奏"],
        student_practices=["listen", "tap", "move"],
        pedagogy_guardrails=COMMON_RHYTHM_GUARDRAILS,
        applicable_activity_ids=["rhythm_warmup", "steady_beat_walk", "rhythm_question_answer", "lyrics_rhythm_reading"],
        feedback_kind="early_on_time_late",
    ),
    "rhythm_performance_result_rule": _rule(
        "rhythm_performance_result_rule",
        "完整节奏表现结果",
        rule_family="rhythm_performance",
        inputs=[
            "expected_hit_count",
            "correct_count",
            "early_count",
            "late_count",
            "missed_count",
            "extra_count",
            "rest_error_count",
            "matched_rate",
            "correct_rate",
        ],
        outputs=["correct", "adjust", "retry"],
        music_elements=["节奏", "稳定拍", "休止"],
        student_practices=["listen", "tap", "revise"],
        pedagogy_guardrails=[
            "整轮结果必须来自每个内部音头的一对一匹配，不能只比较节奏卡起点。",
            "网页只判断可测的敲击时间，不替代教师对动作质量、力度和音乐表现力的观察。",
            "反馈必须指出漏拍、多拍、早晚或休止误拍，并给出可执行的重练建议。",
        ],
        applicable_activity_ids=["rhythm_warmup"],
        feedback_kind="complete_rhythm_result",
    ),
    "rest_guard_rule": _rule(
        "rest_guard_rule",
        "休止符守住判定",
        rule_family="rhythm",
        inputs=["tap_events_ms", "rest_start_ms", "rest_end_ms"],
        outputs=["correct_rest", "tapped_rest"],
        music_elements=["休止", "节奏"],
        student_practices=["listen", "tap", "move"],
        pedagogy_guardrails=COMMON_RHYTHM_GUARDRAILS,
        applicable_activity_ids=["rhythm_warmup", "steady_beat_walk", "lyrics_rhythm_reading", "lyrics_rhythm_practice"],
        feedback_kind="silence_as_music",
    ),
    "lyrics_beat_alignment_rule": _rule(
        "lyrics_beat_alignment_rule",
        "歌词落拍判定",
        rule_family="lyrics_rhythm",
        inputs=["lyric_syllable_index", "tap_time_ms", "target_time_ms", "tolerance_ms", "phrase_index"],
        outputs=["aligned", "early", "late", "miss"],
        music_elements=["歌词", "节奏", "稳定拍"],
        student_practices=["read", "tap", "sing"],
        pedagogy_guardrails=[
            "网页只判断可测的点读或敲击时间，不声称自动判断儿童朗读质量。",
            "歌词落拍反馈要回到按稳定拍读歌词，再回到歌曲演唱。",
        ],
        applicable_activity_ids=["lyrics_rhythm_reading", "lyrics_rhythm_practice"],
        feedback_kind="lyrics_on_beat",
    ),
    "read_tap_sing_sequence_rule": _rule(
        "read_tap_sing_sequence_rule",
        "读拍唱流程判定",
        rule_family="lyrics_rhythm",
        inputs=["read_step_completed", "tap_step_completed", "sing_step_completed", "step_sequence"],
        outputs=["complete", "missing_read", "missing_tap", "missing_sing", "out_of_order"],
        music_elements=["歌词", "节奏", "乐句"],
        student_practices=["read", "tap", "sing"],
        pedagogy_guardrails=[
            "歌词节奏页不能跳过按拍读歌词直接通过。",
            "回唱质量不由网页自动评分，网页只记录回唱步骤是否完成。",
        ],
        applicable_activity_ids=["lyrics_rhythm_reading", "lyrics_rhythm_practice"],
        feedback_kind="read_tap_sing_flow",
    ),
    "meter_accent_rule": _rule(
        "meter_accent_rule",
        "强弱拍判定",
        rule_family="rhythm",
        inputs=["meter", "beat_index", "tap"],
        outputs=["strong_hit", "weak_hit", "miss"],
        music_elements=["节拍", "拍号", "强弱"],
        student_practices=["listen", "tap", "move", "play"],
        pedagogy_guardrails=["必须先体验强弱，再讲拍号。", "强拍反馈围绕拍点同步，不按抢答速度给分。"],
        applicable_activity_ids=["meter_body_movement", "strong_weak_beat_circle", "rhythm_warmup"],
        feedback_kind="strong_weak_beat",
    ),
    "rhythm_pattern_order_rule": _rule(
        "rhythm_pattern_order_rule",
        "节奏顺序判定",
        rule_family="rhythm",
        inputs=["target_pattern", "student_pattern"],
        outputs=["correct", "wrong_order", "partial"],
        music_elements=["节奏", "乐句"],
        student_practices=["listen", "tap", "create"],
        pedagogy_guardrails=["先听或读目标节奏，再比较顺序。", "反馈要指出长短和休止位置。"],
        applicable_activity_ids=["rhythm_question_answer", "lyrics_rhythm_reading"],
    ),
    "bar_length_rule": _rule(
        "bar_length_rule",
        "小节总时值校验",
        rule_family="rhythm",
        inputs=["card_beats", "meter_beats"],
        outputs=["valid", "overflow", "underfill"],
        music_elements=["节奏", "小节"],
        student_practices=["create", "tap"],
        pedagogy_guardrails=["创编不是随便拖卡，必须符合拍号总时值。", "替换后必须回放或拍读。"],
        applicable_activity_ids=["body_percussion_builder", "rhythm_question_answer", "xylophone_creation"],
        feedback_kind="bar_fit",
    ),
    "tempo_stability_rule": _rule(
        "tempo_stability_rule",
        "速度稳定度",
        rule_family="rhythm",
        inputs=["tap_intervals_ms", "bpm", "tolerance_ratio"],
        outputs=["stable", "unstable"],
        music_elements=["稳定拍", "速度"],
        student_practices=["listen", "tap", "move"],
        pedagogy_guardrails=["低段反馈稳定或不稳定，不做复杂统计解释。", "不稳定时建议降速和复听。"],
        applicable_activity_ids=["rhythm_warmup", "steady_beat_walk", "lyrics_rhythm_reading", "lyrics_rhythm_practice"],
    ),
    "steady_beat_movement_rule": _rule(
        "steady_beat_movement_rule",
        "稳定拍行走判定",
        rule_family="rhythm",
        inputs=["movement_events", "target_beats", "rest_windows"],
        outputs=["on_beat_walk", "late_walk", "rest_moved"],
        music_elements=["稳定拍", "节奏", "休止"],
        student_practices=["listen", "move", "tap"],
        pedagogy_guardrails=COMMON_RHYTHM_GUARDRAILS,
        applicable_activity_ids=["steady_beat_walk"],
        feedback_kind="walk_freeze_on_beat",
    ),
    "rhythm_call_response_rule": _rule(
        "rhythm_call_response_rule",
        "节奏问答结构判定",
        rule_family="rhythm_creation",
        inputs=["question_pattern", "answer_pattern", "meter"],
        outputs=["balanced", "too_long", "too_short", "wrong_meter"],
        music_elements=["节奏", "节拍", "创编结构"],
        student_practices=["listen", "tap", "create"],
        pedagogy_guardrails=["答句必须保持同拍号或同乐句长度。", "问答句要能被学生拍读。"],
        applicable_activity_ids=["rhythm_question_answer"],
        feedback_kind="call_response_bar_fit",
    ),
    "solfege_match_rule": _rule(
        "solfege_match_rule",
        "唱名匹配",
        rule_family="pitch",
        inputs=["target_solfege", "selected_solfege"],
        outputs=["correct", "wrong"],
        music_elements=["唱名", "音高"],
        student_practices=["listen", "sing", "read"],
        pedagogy_guardrails=["唱名活动要从听和唱开始。", "低段不急于读复杂谱。"],
        applicable_activity_ids=["solfege_echo_singing", "solfege_sorting", "simple_score_following", "xylophone_creation"],
        feedback_kind="listen_and_sing",
    ),
    "pitch_direction_rule": _rule(
        "pitch_direction_rule",
        "音高走向判定",
        rule_family="pitch",
        inputs=["pitch_sequence"],
        outputs=["up", "down", "same", "leap", "mixed"],
        music_elements=["音高", "旋律"],
        student_practices=["listen", "sing", "read"],
        pedagogy_guardrails=["低段优先高低感和上行下行。", "先听旋律走向，再用手势或路线表达。"],
        applicable_activity_ids=["solfege_echo_singing", "solfege_sorting", "melody_contour_trace"],
        feedback_kind="up_down_same",
    ),
    "melody_sequence_rule": _rule(
        "melody_sequence_rule",
        "旋律序列判定",
        rule_family="pitch",
        inputs=["target_notes", "played_notes"],
        outputs=["correct", "partial", "wrong"],
        music_elements=["音高", "旋律"],
        student_practices=["play", "listen", "sing"],
        pedagogy_guardrails=["音条琴演奏要限制音级。", "演奏后要听回并修正。"],
        applicable_activity_ids=["xylophone_creation", "solfege_sorting"],
    ),
    "pentatonic_constraint_rule": _rule(
        "pentatonic_constraint_rule",
        "五声音阶限制",
        rule_family="pitch_creation",
        inputs=["selected_notes", "allowed_set"],
        outputs=["valid", "invalid"],
        music_elements=["五声音阶", "旋律"],
        student_practices=["create", "play", "listen"],
        pedagogy_guardrails=["五声创编要限制音级，避免乱敲。", "必须能回放、修改和说明意图。"],
        applicable_activity_ids=["xylophone_creation"],
    ),
    "singback_teacher_confirm_rule": _rule(
        "singback_teacher_confirm_rule",
        "跟唱教师确认",
        rule_family="singing",
        inputs=["teacher_action", "round_state"],
        outputs=["pass", "retry", "hint"],
        music_elements=["乐句", "旋律", "歌词"],
        student_practices=["listen", "sing", "evaluate"],
        pedagogy_guardrails=["第一阶段不做高风险自动人声评分。", "儿童歌唱优先教师确认。"],
        applicable_activity_ids=["phrase_singing_practice", "phrase_loop_singing", "solfege_echo_singing"],
        feedback_kind="teacher_confirm",
    ),
    "melody_contour_rule": _rule(
        "melody_contour_rule",
        "旋律线跟踪判定",
        rule_family="pitch",
        inputs=["target_contour", "student_contour"],
        outputs=["matched", "partial", "mismatch"],
        music_elements=["旋律", "音高"],
        student_practices=["listen", "move", "explain"],
        pedagogy_guardrails=["旋律线要绑定真实听到的乐句。", "手势或线条要回到听觉依据。"],
        applicable_activity_ids=["melody_contour_trace"],
        feedback_kind="contour_gesture_feedback",
    ),
    "score_following_rule": _rule(
        "score_following_rule",
        "简谱跟读判定",
        rule_family="pitch_notation",
        inputs=["score_notes", "student_reading"],
        outputs=["correct", "partial", "wrong"],
        music_elements=["识谱", "唱名", "节奏"],
        student_practices=["listen", "read", "sing"],
        pedagogy_guardrails=["识谱要联系声音，不只看符号。", "小学高段再增加复杂读谱要求。"],
        applicable_activity_ids=["simple_score_following"],
        feedback_kind="score_to_sound_mapping",
    ),
    "timbre_match_rule": _rule(
        "timbre_match_rule",
        "音色匹配",
        rule_family="listening_timbre",
        inputs=["target_instrument", "selected_instrument"],
        outputs=["correct", "wrong"],
        music_elements=["音色", "乐器"],
        student_practices=["listen", "match", "explain"],
        pedagogy_guardrails=COMMON_LISTENING_GUARDRAILS,
        applicable_activity_ids=["instrument_timbre_match", "instrument_family_sorting"],
        feedback_kind="evidence_required",
    ),
    "timbre_evidence_rule": _rule(
        "timbre_evidence_rule",
        "音色证据判定",
        rule_family="listening_timbre",
        inputs=["selected_traits", "answer_traits"],
        outputs=["enough", "missing", "wrong"],
        music_elements=["音色", "乐器"],
        student_practices=["listen", "choose", "explain"],
        pedagogy_guardrails=COMMON_LISTENING_GUARDRAILS,
        applicable_activity_ids=["instrument_timbre_match", "instrument_family_sorting"],
        feedback_kind="music_reason",
    ),
    "instrument_family_rule": _rule(
        "instrument_family_rule",
        "乐器家族分类",
        rule_family="listening_timbre",
        inputs=["instrument", "family"],
        outputs=["correct", "wrong"],
        music_elements=["乐器家族", "音色", "发声方式"],
        student_practices=["listen", "classify", "explain"],
        pedagogy_guardrails=["分类前必须先听声音。", "真实照片服务听辨，不做百科问答。"],
        applicable_activity_ids=["instrument_family_sorting"],
        feedback_kind="family_and_timbre_evidence",
    ),
    "mood_choice_rule": _rule(
        "mood_choice_rule",
        "情绪选择判定",
        rule_family="listening",
        inputs=["selected_mood", "accepted_moods"],
        outputs=["accepted", "not_accepted"],
        music_elements=["情绪", "速度", "力度"],
        student_practices=["listen", "choose", "explain"],
        pedagogy_guardrails=COMMON_LISTENING_GUARDRAILS,
        applicable_activity_ids=["picture_listening_intro", "listen_choose_explain", "lesson_opening_hook"],
        feedback_kind="listen_choose_explain",
    ),
    "tempo_dynamic_choice_rule": _rule(
        "tempo_dynamic_choice_rule",
        "速度力度判断",
        rule_family="listening",
        inputs=["selected_term", "target_terms"],
        outputs=["correct", "wrong"],
        music_elements=["速度", "力度"],
        student_practices=["listen", "choose", "explain"],
        pedagogy_guardrails=COMMON_LISTENING_GUARDRAILS,
        applicable_activity_ids=["picture_listening_intro", "listen_choose_explain"],
    ),
    "listening_choice_rule": _rule(
        "listening_choice_rule",
        "听赏先听后选规则",
        rule_family="listening",
        inputs=["listened_once", "choice"],
        outputs=["can_choose", "must_listen_first"],
        music_elements=["情绪", "速度", "力度"],
        student_practices=["listen", "choose", "explain"],
        pedagogy_guardrails=COMMON_LISTENING_GUARDRAILS,
        applicable_activity_ids=["listen_choose_explain"],
        feedback_kind="listen_choose_explain",
    ),
    "opening_listen_before_choice_rule": _rule(
        "opening_listen_before_choice_rule",
        "导入先听后选规则",
        rule_family="listening",
        inputs=["listened_seconds", "choice"],
        outputs=["can_choose", "must_listen_first"],
        music_elements=["情绪", "速度", "力度", "旋律"],
        student_practices=["listen", "choose", "explain"],
        pedagogy_guardrails=COMMON_LISTENING_GUARDRAILS,
        applicable_activity_ids=["picture_listening_intro", "lesson_opening_hook"],
        feedback_kind="listen_before_opening_choice",
    ),
    "evidence_required_rule": _rule(
        "evidence_required_rule",
        "听赏依据表达规则",
        rule_family="listening",
        inputs=["selected_evidence_terms", "student_reason"],
        outputs=["enough", "missing"],
        music_elements=["情绪", "速度", "力度", "音色"],
        student_practices=["listen", "choose", "explain"],
        pedagogy_guardrails=["不能只写喜欢或不喜欢。", "证据词必须来自音乐要素。"],
        applicable_activity_ids=["picture_listening_intro", "listen_choose_explain", "lesson_opening_hook", "exit_ticket_review"],
        feedback_kind="music_reason_required",
    ),
    "theme_return_window_rule": _rule(
        "theme_return_window_rule",
        "主题再现时间窗判定",
        rule_family="listening_form",
        inputs=["click_time_ms", "theme_windows"],
        outputs=["hit", "miss"],
        music_elements=["主题", "重复", "再现"],
        student_practices=["listen", "move", "explain"],
        pedagogy_guardrails=["主题再现必须基于音频时间段或教师标注。", "动作服务主题听辨，不是普通反应游戏。"],
        applicable_activity_ids=["theme_return_action"],
        feedback_kind="theme_return_action",
    ),
    "form_order_rule": _rule(
        "form_order_rule",
        "曲式排序判定",
        rule_family="listening_form",
        inputs=["target_order", "student_order"],
        outputs=["correct", "partial", "wrong"],
        music_elements=["曲式", "重复", "对比"],
        student_practices=["listen", "order", "explain"],
        pedagogy_guardrails=["曲式必须绑定音频段落复听。", "图形排序最终要回到重复和对比的听觉依据。"],
        applicable_activity_ids=["form_ordering"],
        feedback_kind="section_order",
    ),
    "creation_bar_fit_rule": _rule(
        "creation_bar_fit_rule",
        "创编小节适配",
        rule_family="composition",
        inputs=["card_beats", "meter_beats"],
        outputs=["valid", "overflow", "underfill"],
        music_elements=["节奏", "创编结构"],
        student_practices=["create", "revise", "play"],
        pedagogy_guardrails=["创编必须有小节、节拍或问答等最低结构。", "必须能回放、修改和说明。"],
        applicable_activity_ids=["body_percussion_builder", "xylophone_creation"],
        feedback_kind="bar_fit",
    ),
    "call_response_balance_rule": _rule(
        "call_response_balance_rule",
        "问答句平衡",
        rule_family="composition",
        inputs=["question_phrase_beats", "answer_phrase_beats"],
        outputs=["balanced", "too_long", "too_short"],
        music_elements=["问答", "乐句", "节奏"],
        student_practices=["create", "tap", "listen"],
        pedagogy_guardrails=["问答句要能听出呼应。", "低段只做短问短答。"],
        applicable_activity_ids=["rhythm_question_answer", "body_percussion_builder"],
    ),
    "graphic_score_symbol_rule": _rule(
        "graphic_score_symbol_rule",
        "图形谱含义判定",
        rule_family="composition",
        inputs=["symbol_set", "student_explanation"],
        outputs=["clear", "unclear", "missing_playback"],
        music_elements=["图形谱", "音高", "力度", "节奏"],
        student_practices=["create", "explain", "listen"],
        pedagogy_guardrails=["图形谱必须能被声音或动作验证。", "符号含义要和音乐要素绑定。"],
        applicable_activity_ids=["graphic_score_create"],
        feedback_kind="symbol_meaning_and_playback",
    ),
    "ensemble_entry_rule": _rule(
        "ensemble_entry_rule",
        "声部进入判定",
        rule_family="ensemble_group",
        inputs=["entry_cue_ms", "play_event_ms", "tolerance_ms"],
        outputs=["on_cue", "early", "late"],
        music_elements=["节奏", "声部", "合作"],
        student_practices=["listen", "play", "cooperate"],
        pedagogy_guardrails=["合奏重点是倾听、进入和声部配合。", "不能变成多人同时乱敲。"],
        applicable_activity_ids=["classroom_band_roles", "orff_percussion_ensemble"],
        feedback_kind="entry_timing",
    ),
    "group_turn_rule": _rule(
        "group_turn_rule",
        "小组轮次判定",
        rule_family="ensemble_group",
        inputs=["current_group", "action_group"],
        outputs=["allowed", "blocked"],
        music_elements=["合作", "展示"],
        student_practices=["cooperate", "perform"],
        pedagogy_guardrails=["轮换服务音乐任务，不是课堂管理本身。", "小组轮换不能打断音乐流程。"],
        applicable_activity_ids=["group_relay_performance", "rhythm_question_answer"],
    ),
    "rubric_score_rule": _rule(
        "rubric_score_rule",
        "评价量规计算",
        rule_family="assessment",
        inputs=["rubric_selections"],
        outputs=["summary_score", "teacher_review_summary"],
        music_elements=["评价", "合作"],
        student_practices=["evaluate", "explain"],
        pedagogy_guardrails=["评价不以排名为主。", "要反馈节奏、声音、倾听或创编修改等音乐证据。"],
        applicable_activity_ids=["group_relay_performance", "show_and_peer_feedback", "exit_ticket_review"],
        feedback_kind="rubric",
    ),
    "peer_feedback_rule": _rule(
        "peer_feedback_rule",
        "同伴评价音乐依据规则",
        rule_family="assessment",
        inputs=["feedback_text", "evidence_terms"],
        outputs=["specific", "too_general"],
        music_elements=["评价", "合作"],
        student_practices=["evaluate", "explain"],
        pedagogy_guardrails=["同伴评价必须说具体音乐依据。", "不能只说很好或不好。"],
        applicable_activity_ids=["show_and_peer_feedback"],
        feedback_kind="specific_music_evidence_required",
    ),
}


RULES_BY_ACTIVITY: dict[str, list[str]] = {
    "rhythm_warmup": ["rhythm_timing_judgement", "tempo_stability_rule", "rest_guard_rule"],
    "steady_beat_walk": ["steady_beat_movement_rule", "rhythm_timing_judgement", "rest_guard_rule", "tempo_stability_rule"],
    "rhythm_question_answer": ["rhythm_call_response_rule", "rhythm_pattern_order_rule", "rhythm_timing_judgement", "call_response_balance_rule"],
    "meter_body_movement": ["meter_accent_rule", "rhythm_timing_judgement"],
    "strong_weak_beat_circle": ["meter_accent_rule", "rhythm_timing_judgement"],
    "phrase_singing_practice": ["singback_teacher_confirm_rule"],
    "phrase_loop_singing": ["singback_teacher_confirm_rule"],
    "lyrics_rhythm_practice": [
        "rhythm_timing_judgement",
        "rhythm_pattern_order_rule",
        "rest_guard_rule",
        "tempo_stability_rule",
        "lyrics_beat_alignment_rule",
        "read_tap_sing_sequence_rule",
    ],
    "lyrics_rhythm_reading": [
        "rhythm_timing_judgement",
        "rhythm_pattern_order_rule",
        "rest_guard_rule",
        "tempo_stability_rule",
        "lyrics_beat_alignment_rule",
        "read_tap_sing_sequence_rule",
    ],
    "solfege_echo_singing": ["solfege_match_rule", "pitch_direction_rule", "singback_teacher_confirm_rule"],
    "solfege_sorting": ["solfege_match_rule", "pitch_direction_rule"],
    "melody_contour_trace": ["melody_contour_rule", "pitch_direction_rule"],
    "simple_score_following": ["score_following_rule", "solfege_match_rule"],
    "picture_listening_intro": ["opening_listen_before_choice_rule", "mood_choice_rule", "evidence_required_rule"],
    "listen_choose_explain": ["listening_choice_rule", "mood_choice_rule", "tempo_dynamic_choice_rule", "evidence_required_rule"],
    "lesson_opening_hook": ["opening_listen_before_choice_rule", "mood_choice_rule", "evidence_required_rule"],
    "theme_return_action": ["theme_return_window_rule"],
    "instrument_timbre_match": ["timbre_match_rule", "timbre_evidence_rule"],
    "instrument_family_sorting": ["instrument_family_rule", "timbre_evidence_rule", "timbre_match_rule"],
    "form_ordering": ["form_order_rule", "theme_return_window_rule"],
    "body_percussion_builder": ["creation_bar_fit_rule", "bar_length_rule", "rhythm_timing_judgement"],
    "graphic_score_create": ["graphic_score_symbol_rule"],
    "xylophone_creation": ["creation_bar_fit_rule", "bar_length_rule", "melody_sequence_rule", "pentatonic_constraint_rule", "solfege_match_rule"],
    "classroom_band_roles": ["ensemble_entry_rule", "group_turn_rule", "rhythm_timing_judgement"],
    "orff_percussion_ensemble": ["ensemble_entry_rule", "group_turn_rule", "rhythm_timing_judgement"],
    "group_relay_performance": ["group_turn_rule", "rubric_score_rule"],
    "show_and_peer_feedback": ["peer_feedback_rule", "rubric_score_rule"],
    "exit_ticket_review": ["rubric_score_rule", "evidence_required_rule"],
}


def rules_for_activity(activity_id: str) -> list[str]:
    return list(RULES_BY_ACTIVITY.get(str(activity_id or ""), []))


def music_rule_specs_for_activity(activity_id: str) -> list[dict[str, Any]]:
    return [get_music_rule(rule_id) for rule_id in rules_for_activity(activity_id)]


def get_music_rule(rule_id: str) -> dict[str, Any]:
    rule = MUSIC_RULE_REGISTRY.get(str(rule_id or ""))
    if not rule:
        raise ValueError(f"unknown music rule: {rule_id}")
    return validate_music_rule_spec(rule)


def list_music_rules() -> list[dict[str, Any]]:
    return [validate_music_rule_spec(rule) for rule in MUSIC_RULE_REGISTRY.values()]


def validate_music_rule_spec(rule: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(rule, dict):
        raise ValueError("music rule spec must be a dict")
    missing = [
        field
        for field in REQUIRED_RULE_FIELDS
        if field not in rule or rule.get(field) is None or rule.get(field) == ""
    ]
    if missing:
        raise ValueError(f"music rule spec missing fields: {', '.join(missing)}")
    if rule.get("version") != "music_rule_spec_v1":
        raise ValueError("music rule spec version must be music_rule_spec_v1")
    if rule.get("audience") != "primary_school":
        raise ValueError("music rule audience must be primary_school")
    for field in ("inputs", "outputs", "music_elements", "student_practices", "pedagogy_guardrails", "applicable_activity_ids"):
        if not isinstance(rule.get(field), list) or not rule[field]:
            raise ValueError(f"music rule {field} must be a non-empty list")
    feedback = rule.get("feedback_contract")
    if not isinstance(feedback, dict):
        raise ValueError("music rule feedback_contract must be a dict")
    for field in ("status", "music_reason", "student_feedback", "teacher_suggestion", "next_practice", "requires_teacher_confirm"):
        if not feedback.get(field):
            raise ValueError(f"music rule feedback_contract missing {field}")
    return deepcopy(rule)


def evaluate_music_rule(rule_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    normalized = payload if isinstance(payload, dict) else {}
    if rule_id == "rhythm_timing_judgement":
        return _rhythm_timing(normalized)
    if rule_id == "rhythm_performance_result_rule":
        return _rhythm_performance_result(normalized)
    if rule_id == "rest_guard_rule":
        return _rest_guard(normalized)
    if rule_id == "pitch_direction_rule":
        return _pitch_direction(normalized)
    if rule_id in {"bar_length_rule", "creation_bar_fit_rule"}:
        return _bar_length(normalized)
    if rule_id == "mood_choice_rule":
        return _mood_choice(normalized)
    if rule_id == "timbre_match_rule":
        return _simple_match(
            "correct" if str(normalized.get("target_instrument")) == str(normalized.get("selected_instrument")) else "wrong",
            "学生能把听到的音色和乐器对应起来。" if str(normalized.get("target_instrument")) == str(normalized.get("selected_instrument")) else "学生选择的乐器和目标音色不一致。",
            "先听声音，再看乐器照片，说一说音色证据。",
            "请复听对比两个乐器的发声特点。",
            "listen_then_explain",
        )
    if rule_id == "timbre_evidence_rule":
        selected = set(_string_list(normalized.get("selected_traits")))
        answer = set(_string_list(normalized.get("answer_traits")))
        status = "enough" if selected and selected.intersection(answer) else "missing"
        return _simple_match(
            status,
            "学生选择了能支持音色判断的证据词。" if status == "enough" else "学生还没有选出能支持判断的音色证据。",
            "说出你听到的是清脆、柔和、短促还是持续。",
            "引导学生复听音头、延音和发声方式。",
            "listen_then_choose_evidence",
        )
    return _simple_match(
        "not_evaluated",
        f"{rule_id} 当前提供结构化规则合同，具体判定由对应前端活动或教师确认执行。",
        "请先完成音乐实践，再根据教师提示确认。",
        "使用规则合同中的输入输出字段接入具体活动判定。",
        "teacher_confirm",
        requires_teacher_confirm=True,
    )


def _rhythm_timing(payload: dict[str, Any]) -> dict[str, Any]:
    if bool(payload.get("rest_error")):
        return _simple_match("rest_error", "学生在休止窗口中完成了拍击。", "错误：这里是休止，要停住。", "单独练习休止位置，再回到完整节奏。", "listen_then_freeze")
    if bool(payload.get("target_consumed")):
        return _simple_match("extra", "当前拍击没有可匹配的未使用目标音头。", "错误：多拍了一下。", "先数清每张节奏卡有几个音头，再重新跟拍。", "listen_then_count")
    tap = _number(payload.get("tap_time_ms"), None)
    target = _number(payload.get("target_time_ms"), None)
    tolerance = _number(payload.get("tolerance_ms"), 120.0)
    bpm = int(_number(payload.get("bpm"), 84.0))
    if tap is None or target is None:
        return _simple_match("missed", "学生没有在目标拍附近完成拍击。", "错误：这里漏拍了。", f"降速到 {max(60, bpm - 8)} BPM，并打开拍点提示。", "listen_then_tap")
    delta = tap - target
    if abs(delta) <= tolerance:
        status = "correct" if str(payload.get("target_event_id") or "").strip() else "on_time"
        return _simple_match(status, "学生拍击落在对应目标音头的正确时间窗内。", "正确。", "可以逐步隐藏拍点提示或回到原速。", "tap_then_transfer")
    if delta < 0:
        return _simple_match("early", "学生拍点落在目标拍之前，出现抢拍。", "稍早，先等到拍点再拍手。", f"保持 {bpm} BPM，提醒学生先点头感受强拍。", "listen_then_tap")
    return _simple_match("late", "学生拍点之后才拍击，稳定拍尚未建立。", "稍晚，先跟着强拍点头，再拍手。", f"降速到 {max(60, bpm - 8)} BPM，打开强拍提示。", "listen_then_tap")


def _rhythm_performance_result(payload: dict[str, Any]) -> dict[str, Any]:
    expected = max(0, int(_number(payload.get("expected_hit_count"), 0.0) or 0))
    correct = max(0, int(_number(payload.get("correct_count"), 0.0) or 0))
    early = max(0, int(_number(payload.get("early_count"), 0.0) or 0))
    late = max(0, int(_number(payload.get("late_count"), 0.0) or 0))
    missed = max(0, int(_number(payload.get("missed_count"), max(0, expected - correct - early - late)) or 0))
    extra = max(0, int(_number(payload.get("extra_count"), 0.0) or 0))
    rest_error = max(0, int(_number(payload.get("rest_error_count"), 0.0) or 0))
    matched_rate = _number(payload.get("matched_rate"), (correct + early + late) / expected if expected else 0.0) or 0.0
    correct_rate = _number(payload.get("correct_rate"), correct / expected if expected else 0.0) or 0.0
    if expected > 0 and correct == expected and not any((early, late, missed, extra, rest_error)):
        return _simple_match("correct", "所有目标音头均在正确时间窗内完成，且没有漏拍、多拍或休止误拍。", "本轮节奏正确。", "可以换动作、提高速度或隐藏提示。", "transfer_or_challenge")
    if matched_rate >= 0.8 and correct_rate >= 0.7 and rest_error == 0 and missed + extra <= 2:
        return _simple_match("adjust", "大部分目标音头已经匹配，但仍有早晚位置或少量漏拍、多拍需要调整。", "基本正确，再调整一下。", "根据统计中最多的一类问题做一次针对性重练。", "targeted_repractice")
    if rest_error:
        suggestion = "先单独练习休止，确认停住也是音乐表现。"
    elif missed:
        suggestion = "降低速度并拆分节奏卡，先解决漏拍。"
    elif extra:
        suggestion = "先数清目标音头数量，再重新跟拍。"
    else:
        suggestion = "降低速度，先听预备拍再完成整轮。"
    return _simple_match("retry", "本轮未达到完整节奏表现要求，需要根据可见错误重新练习。", "错误，需要重练。", suggestion, "listen_then_repractice")


def _rest_guard(payload: dict[str, Any]) -> dict[str, Any]:
    start = _number(payload.get("rest_start_ms"), 0.0)
    end = _number(payload.get("rest_end_ms"), 0.0)
    taps = [_number(item, None) for item in (payload.get("tap_events_ms") or [])]
    tapped = any(item is not None and start <= item <= end for item in taps)
    if tapped:
        return _simple_match("tapped_rest", "学生在休止窗口中拍击，休止还没有守住。", "这里要停住，停住也是音乐表现。", "请先识读四、四、休止，再让全班做停住动作。", "listen_then_freeze")
    return _simple_match("correct_rest", "学生在休止窗口保持安静，能把休止作为音乐表现。", "休止守住了，停住也很有音乐感。", "可以把休止放回歌曲或节奏卡中复练。", "freeze_then_tap")


def _pitch_direction(payload: dict[str, Any]) -> dict[str, Any]:
    sequence = [_number(item, None) for item in (payload.get("pitch_sequence") or [])]
    pitches = [item for item in sequence if item is not None]
    if len(pitches) < 2:
        return _simple_match("same", "音高材料不足，先按保持音处理。", "先听一个音，再听下一个音。", "补充至少两个音高再判断走向。", "listen_then_sing")
    intervals = [pitches[index + 1] - pitches[index] for index in range(len(pitches) - 1)]
    if all(interval > 0 for interval in intervals):
        status = "up"
        reason = "旋律音高逐步向上，学生可以用上行动作或音高阶梯表示。"
        feedback = "听到旋律往上走了。"
    elif all(interval < 0 for interval in intervals):
        status = "down"
        reason = "旋律音高逐步向下，学生可以用下行动作或音高阶梯表示。"
        feedback = "听到旋律往下走了。"
    elif all(interval == 0 for interval in intervals):
        status = "same"
        reason = "旋律音高保持不变。"
        feedback = "这几个音保持在同一高度。"
    elif any(abs(interval) > 2 for interval in intervals):
        status = "leap"
        reason = "旋律中出现跳进，需要学生听出不是一步一步移动。"
        feedback = "这里有跳进，手势可以跨大一点。"
    else:
        status = "mixed"
        reason = "旋律同时包含上行和下行。"
        feedback = "旋律方向有变化，边听边画线。"
    return _simple_match(status, reason, feedback, "让学生用手势或音高阶梯复听验证。", "listen_then_trace")


def _bar_length(payload: dict[str, Any]) -> dict[str, Any]:
    beats = sum(_number(item, 0.0) for item in (payload.get("card_beats") or []))
    meter = _number(payload.get("meter_beats"), 4.0)
    if abs(beats - meter) < 0.0001:
        return _simple_match("valid", "节奏卡总时值正好填满当前小节。", "这一小节拍数正好，可以拍出来听听。", "请学生回放或拍读，确认创编能被听见。", "playback_then_revise")
    if beats > meter:
        return _simple_match("overflow", "节奏卡总时值超过当前小节。", "这一小节太满了，需要换短一点的节奏卡。", "提示学生先数拍，再替换一张卡。", "revise_bar")
    return _simple_match("underfill", "节奏卡总时值没有填满当前小节。", "这一小节还少拍，需要补一张节奏卡或延长音。", "提示学生补齐拍数后再回放。", "revise_bar")


def _mood_choice(payload: dict[str, Any]) -> dict[str, Any]:
    selected = str(payload.get("selected_mood") or "").strip()
    accepted = {str(item).strip() for item in (payload.get("accepted_moods") or []) if str(item).strip()}
    if selected and selected in accepted:
        return _simple_match("accepted", "学生选择的情绪与当前音乐材料可接受感受一致。", "你的感受可以成立，请再说一个速度、力度或音色依据。", "追问学生为什么这样选，并组织一次复听验证。", "listen_then_explain")
    return _simple_match("not_accepted", "学生选择的情绪暂时缺少音乐依据支持。", "再听一遍，找找速度、力度或旋律有什么特点。", "引导学生从速度、力度、音色中选择证据词。", "relisten_then_choose")


def _simple_match(
    status: str,
    music_reason: str,
    student_feedback: str,
    teacher_suggestion: str,
    next_practice: str,
    *,
    requires_teacher_confirm: bool = False,
) -> dict[str, Any]:
    return {
        "version": "music_rule_result_v1",
        "status": status,
        "music_reason": music_reason,
        "student_feedback": student_feedback,
        "teacher_suggestion": teacher_suggestion,
        "next_practice": next_practice,
        "requires_teacher_confirm": requires_teacher_confirm,
    }


def _number(value: Any, default: float | None) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]
