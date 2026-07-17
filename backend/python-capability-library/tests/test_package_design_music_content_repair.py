from app.services.orchestration.package_design_agent import _validate_design


def test_ensemble_cue_removes_only_unsupported_pitch_field() -> None:
    payload = {
        "title": "虚拟乐器合奏课",
        "steps": [
            {"activity_id": "lesson_opening_hook"},
            {
                "node_type": "instrument_task",
                "activity_id": "orff_percussion_ensemble",
                "task_kind": "ensemble_cue",
                "instrument_id": "virtual_piano",
                "title": "颜色指挥合奏",
                "music_content": {
                    "meter_ids": ["meter_4_4"],
                    "bpm": 80,
                    "bars": 8,
                    "pitch_set_ids": ["pitch_do_re_mi_sol_la"],
                    "dynamic_ids": ["dynamic_mf"],
                    "timbre_ids": ["timbre_piano"],
                },
            },
            {"activity_id": "exit_ticket_review"},
        ],
    }

    package = _validate_design(
        payload,
        lesson={
            "course_name": "虚拟乐器任务实验室",
            "grade_band": "middle_primary",
            "objectives": ["根据颜色提示完成合奏进入与停止"],
        },
    )

    node = package["steps"][1]
    assert "pitch_set_ids" not in node["music_content"]
    assert node["music_content"]["dynamic_ids"] == ["dynamic_mf"]
    assert node["music_content"]["timbre_ids"] == ["timbre_piano"]
    assert node["music_content_corrections"] == [{
        "field": "pitch_set_ids",
        "action": "removed",
        "reason": "instrument_task:ensemble_cue does not support pitch_set_ids",
    }]


def test_design_over_seven_steps_is_trimmed_without_rule_fallback() -> None:
    activity_ids = [
        "lesson_opening_hook",
        "rhythm_warmup",
        "strong_weak_beat_circle",
        "steady_beat_walk",
        "rhythm_question_answer",
        "body_percussion_builder",
        "xylophone_creation",
        "orff_percussion_ensemble",
        "exit_ticket_review",
    ]
    package = _validate_design(
        {"title": "音乐闯关嘉年华", "steps": [
            {"activity_id": activity_id} for activity_id in activity_ids
        ]},
        lesson={"course_name": "音乐闯关嘉年华", "grade_band": "middle_primary"},
    )

    assert len(package["steps"]) == 7
    assert package["steps"][0]["activity_id"] == "lesson_opening_hook"
    assert package["steps"][-1]["activity_id"] == "exit_ticket_review"
    assert package["design_corrections"] == [{
        "field": "steps",
        "action": "trimmed",
        "from": 9,
        "to": 7,
        "reason": "interactive package supports at most 7 nodes",
    }]


def test_game_activity_alias_is_normalized_to_game_template() -> None:
    package = _validate_design(
        {"steps": [
            {"activity_id": "lesson_opening_hook"},
            {
                "node_type": "game",
                "activity_id": "rhythm_question_answer",
                "template_id": "rhythm_question_answer",
                "music_content": {"meter_ids": []},
            },
            {"activity_id": "exit_ticket_review"},
        ]},
        lesson={"course_name": "音乐闯关", "grade_band": "middle_primary"},
    )

    node = package["steps"][1]
    assert node["node_type"] == "game"
    assert node["component_keys"] == ["game:rhythm_echo_core"]
    assert node["music_content"]["meter_ids"] == ["meter_2_4"]
