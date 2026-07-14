from __future__ import annotations

from copy import deepcopy
from typing import Any


ASSESSMENT_RECORD_TEMPLATE_VERSION = "assessment_record_template_v1"

REQUIRED_FIELDS = (
    "version",
    "record_template_id",
    "label",
    "audience",
    "records",
    "output_forms",
    "applicable_activity_ids",
    "student_music_practices",
    "music_education_use",
    "json_schema",
    "quality_gates",
)


def _schema(required: list[str], properties: dict[str, str]) -> dict[str, Any]:
    return {
        "type": "object",
        "required": required,
        "properties": {
            key: {"type": value}
            for key, value in properties.items()
        },
    }


def _record_template(
    record_template_id: str,
    label: str,
    *,
    records: list[str],
    output_forms: list[str],
    applicable_activity_ids: list[str],
    student_music_practices: list[str],
    music_education_use: str,
    json_schema: dict[str, Any],
    quality_gates: list[str],
) -> dict[str, Any]:
    return {
        "version": ASSESSMENT_RECORD_TEMPLATE_VERSION,
        "record_template_id": record_template_id,
        "label": label,
        "audience": "primary_school",
        "records": records,
        "output_forms": output_forms,
        "applicable_activity_ids": applicable_activity_ids,
        "student_music_practices": student_music_practices,
        "music_education_use": music_education_use,
        "json_schema": json_schema,
        "quality_gates": quality_gates,
    }


ASSESSMENT_RECORD_TEMPLATES: dict[str, dict[str, Any]] = {
    "tap_accuracy_record": _record_template(
        "tap_accuracy_record",
        "完整节奏表现记录",
        records=[
            "grade_preset",
            "practice_mode",
            "bpm",
            "meter",
            "pattern_ids",
            "tap_attempts",
            "expected_hit_count",
            "correct_count",
            "early_count",
            "late_count",
            "missed_count",
            "extra_count",
            "rest_error_count",
            "steady_beat_accuracy",
            "round_result",
            "score",
            "teacher_suggestion",
        ],
        output_forms=["complete_rhythm_result", "score", "summary_text", "json_export"],
        applicable_activity_ids=[
            "rhythm_warmup",
            "meter_body_movement",
            "steady_beat_walk",
            "rhythm_question_answer",
            "body_percussion_builder",
        ],
        student_music_practices=["listen", "tap", "move"],
        music_education_use="记录学生是否按完整内部音头表现节奏，区分正确、早晚、漏拍、多拍和休止误拍，帮助教师决定针对性重练或增加挑战。",
        json_schema=_schema(
            ["version", "activity_id", "grade_preset", "practice_mode", "expected_hit_count", "correct_count", "round_result", "teacher_suggestion"],
            {
                "version": "string",
                "activity_id": "string",
                "attempt_count": "number",
                "grade_preset": "string",
                "practice_mode": "string",
                "bpm": "number",
                "meter": "string",
                "pattern_ids": "array",
                "tap_attempts": "array",
                "expected_hit_count": "number",
                "correct_count": "number",
                "early_count": "number",
                "on_time_count": "number",
                "late_count": "number",
                "missed_count": "number",
                "extra_count": "number",
                "rest_error_count": "number",
                "steady_beat_accuracy": "number",
                "round_result": "string",
                "score": "number",
                "teacher_suggestion": "string",
            },
        ),
        quality_gates=[
            "records_timing_evidence",
            "internal_attacks_matched_once",
            "missed_extra_rest_errors_visible",
            "complete_rhythm_result_visible",
            "summary_visible",
            "json_export_available",
        ],
    ),
    "lyrics_rhythm_student_judgement_record": _record_template(
        "lyrics_rhythm_student_judgement_record",
        "歌词节奏网页学生判断记录",
        records=[
            "step_sequence",
            "read_step_completed",
            "tap_attempts",
            "timing_result",
            "rest_result",
            "rhythm_order_result",
            "lyric_beat_alignment",
            "tempo_stability",
            "retry_count",
            "web_suggestion",
            "requires_repractice",
            "pass_confirmed",
        ],
        output_forms=["web_judgement_summary", "pass_confirm_record", "json_export"],
        applicable_activity_ids=["lyrics_rhythm_reading", "lyrics_rhythm_practice"],
        student_music_practices=["read", "tap", "sing"],
        music_education_use="记录网页可判断的读拍唱步骤、敲击早晚、休止误拍和歌词落拍情况；网页只给出可测结果和重练提示。",
        json_schema=_schema(
            [
                "version",
                "activity_id",
                "phrase_index",
                "step_sequence",
                "timing_result",
                "web_suggestion",
                "requires_repractice",
                "pass_confirmed",
            ],
            {
                "version": "string",
                "activity_id": "string",
                "phrase_index": "number",
                "phrase_text": "string",
                "step_sequence": "string",
                "read_step_completed": "boolean",
                "tap_attempts": "array",
                "timing_result": "object",
                "rest_result": "object",
                "rhythm_order_result": "string",
                "lyric_beat_alignment": "string",
                "tempo_stability": "string",
                "retry_count": "number",
                "web_suggestion": "string",
                "requires_repractice": "boolean",
                "pass_confirmed": "boolean",
            },
        ),
        quality_gates=[
            "web_judgement_does_not_score_singing",
            "tap_timing_evidence_recorded",
            "read_tap_sing_sequence_recorded",
            "rest_errors_visible",
            "pass_confirm_recorded",
        ],
    ),
    "singing_teacher_check_record": _record_template(
        "singing_teacher_check_record",
        "跟唱教师确认记录",
        records=["phrase_index", "teacher_decision", "retry_count", "singing_note", "next_phrase_ready"],
        output_forms=["teacher_click_record", "phrase_progress", "json_export"],
        applicable_activity_ids=[
            "phrase_singing_practice",
            "phrase_loop_singing",
            "solfege_echo_singing",
            "simple_score_following",
        ],
        student_music_practices=["listen", "sing", "read"],
        music_education_use="把听一句、唱一句、教师确认和再练次数记录下来，避免用自动分数替代小学学唱中的教师判断。",
        json_schema=_schema(
            ["version", "activity_id", "phrase_index", "teacher_decision", "next_phrase_ready"],
            {
                "version": "string",
                "activity_id": "string",
                "phrase_index": "number",
                "teacher_decision": "string",
                "retry_count": "number",
                "singing_note": "string",
                "next_phrase_ready": "boolean",
            },
        ),
        quality_gates=["teacher_confirm_recorded", "retry_preserves_phrase", "progress_export_available"],
    ),
    "listening_reason_record": _record_template(
        "listening_reason_record",
        "欣赏依据记录",
        records=["selected_mood", "evidence_terms", "student_reason", "relisten_prompt"],
        output_forms=["choice_result", "reason_text", "json_export"],
        applicable_activity_ids=[
            "picture_listening_intro",
            "listen_choose_explain",
            "lesson_opening_hook",
            "theme_return_action",
        ],
        student_music_practices=["listen", "choose", "explain"],
        music_education_use="记录学生选择了什么感受、用了哪些速度/力度/旋律证据，并提醒复听验证，避免只看图片猜答案。",
        json_schema=_schema(
            ["version", "activity_id", "selected_mood", "evidence_terms", "relisten_prompt"],
            {
                "version": "string",
                "activity_id": "string",
                "selected_mood": "string",
                "evidence_terms": "array",
                "student_reason": "string",
                "relisten_prompt": "string",
            },
        ),
        quality_gates=["evidence_required", "relisten_prompt_available", "generic_reason_rejected"],
    ),
    "group_performance_record": _record_template(
        "group_performance_record",
        "小组表现记录",
        records=["group_name", "criteria_checks", "music_evidence", "teacher_summary"],
        output_forms=["rubric", "class_summary", "json_export"],
        applicable_activity_ids=[
            "orff_percussion_ensemble",
            "classroom_band_roles",
            "group_relay_performance",
            "show_and_peer_feedback",
        ],
        student_music_practices=["listen", "cooperate", "perform", "assess"],
        music_education_use="把小组合奏、展示和互评绑定到节奏稳定、按时进入、能听同伴等音乐评价维度。",
        json_schema=_schema(
            ["version", "activity_id", "groups", "criteria"],
            {
                "version": "string",
                "activity_id": "string",
                "groups": "array",
                "criteria": "array",
                "teacher_summary": "string",
            },
        ),
        quality_gates=["criteria_bound_to_music_goal", "evidence_text_required", "class_summary_ready"],
    ),
    "creation_replay_record": _record_template(
        "creation_replay_record",
        "创编回放记录",
        records=["created_sequence", "audition_count", "revision_count", "constraint_checks", "student_explanation"],
        output_forms=["replay_data", "creation_summary", "json_export"],
        applicable_activity_ids=["xylophone_creation", "graphic_score_create"],
        student_music_practices=["create", "listen", "revise", "explain", "play"],
        music_education_use="记录学生用了哪些音、节奏或图形，是否回放修改，并能说明创编和音乐要素之间的关系。",
        json_schema=_schema(
            ["version", "activity_id", "created_sequence", "audition_count", "revision_count"],
            {
                "version": "string",
                "activity_id": "string",
                "created_sequence": "array",
                "audition_count": "number",
                "revision_count": "number",
                "constraint_checks": "array",
                "student_explanation": "string",
            },
        ),
        quality_gates=["replay_available", "revision_recorded", "music_constraint_checked"],
    ),
    "exit_ticket_record": _record_template(
        "exit_ticket_record",
        "课堂出口票记录",
        records=["music_focus", "evidence_terms", "student_reason", "next_lesson_suggestion"],
        output_forms=["class_list", "teacher_review_summary", "json_export"],
        applicable_activity_ids=["exit_ticket_review"],
        student_music_practices=["choose", "explain", "assess"],
        music_education_use="在课堂收尾记录每个学生或小组能否说出本课音乐要素和一个具体依据，供教师下节课复盘。",
        json_schema=_schema(
            ["version", "activity_id", "music_focus", "evidence_terms", "student_reason"],
            {
                "version": "string",
                "activity_id": "string",
                "music_focus": "string",
                "evidence_terms": "array",
                "student_reason": "string",
                "next_lesson_suggestion": "string",
            },
        ),
        quality_gates=["music_focus_present", "evidence_required", "teacher_review_ready"],
    ),
}


def list_assessment_record_templates() -> list[dict[str, Any]]:
    return [validate_assessment_record_template(template) for template in ASSESSMENT_RECORD_TEMPLATES.values()]


def get_assessment_record_template(record_template_id: str) -> dict[str, Any]:
    template = ASSESSMENT_RECORD_TEMPLATES.get(str(record_template_id or ""))
    if not template:
        raise ValueError(f"unknown assessment record template: {record_template_id}")
    return validate_assessment_record_template(template)


def assessment_record_specs_for_activity(activity_id: str) -> list[dict[str, Any]]:
    return [
        validate_assessment_record_template(template)
        for template in ASSESSMENT_RECORD_TEMPLATES.values()
        if activity_id in template.get("applicable_activity_ids", [])
    ]


def validate_assessment_record_template(template: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(template, dict):
        raise ValueError("assessment record template must be a dict")
    missing = [field for field in REQUIRED_FIELDS if not template.get(field)]
    if missing:
        raise ValueError(f"assessment record template missing fields: {', '.join(missing)}")
    if template.get("version") != ASSESSMENT_RECORD_TEMPLATE_VERSION:
        raise ValueError("assessment record template version must be assessment_record_template_v1")
    if template.get("audience") != "primary_school":
        raise ValueError("assessment record template audience must be primary_school")
    schema = template.get("json_schema") if isinstance(template.get("json_schema"), dict) else {}
    if "version" not in schema.get("required", []):
        raise ValueError("assessment record json_schema must require version")
    return deepcopy(template)
