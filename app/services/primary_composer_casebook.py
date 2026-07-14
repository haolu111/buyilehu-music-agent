from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.services.music_game_composer import compose_music_game


CASEBOOK_REPORT_VERSION = "primary_composer_casebook_report_v1"


PRIMARY_CLASSROOM_CASES: list[dict[str, Any]] = [
    {
        "case_id": "lower_rhythm_echo",
        "title": "二年级节奏复刻热身",
        "expected_activity_id": "rhythm_warmup",
        "practice_domain": "表现",
        "request": {
            "teacher_request": "二年级节奏复刻小游戏，练习稳定拍、四分音符、八分音符和休止",
            "lesson_text": "学生先听目标节奏，再用拍手或节奏垫模仿，感受稳定拍和休止。",
            "grade_band": "lower_primary",
            "available_materials": {
                "meter": "2/4",
                "rhythm_pattern": ["quarter", "eighth_pair", "rest", "quarter"],
                "bpm": 88,
            },
        },
    },
    {
        "case_id": "lower_meter_body_movement",
        "title": "一年级二拍子强弱律动",
        "expected_activity_id": "meter_body_movement",
        "practice_domain": "表现",
        "request": {
            "teacher_request": "给一年级做一个学习二拍子强弱的身体律动小游戏",
            "lesson_text": "学生听音乐感受二拍子强弱规律，能在强拍上拍手、弱拍上轻拍腿。",
            "grade_band": "lower_primary",
            "available_materials": {
                "meter": "2/4",
                "rhythm_pattern": ["quarter", "quarter", "quarter", "quarter"],
                "bpm": 84,
            },
            "classroom_constraints": {"no_real_instruments": True},
        },
    },
    {
        "case_id": "lower_steady_beat_walk",
        "title": "一年级稳定拍行走",
        "expected_activity_id": "steady_beat_walk",
        "practice_domain": "表现",
        "request": {
            "teacher_request": "一年级稳定拍行走活动，学生听音乐跟着稳定拍走步，休止时停住",
            "lesson_text": "学生先听稳定拍，再用走、拍、停表现拍点和休止。",
            "grade_band": "lower_primary",
            "available_materials": {
                "meter": "2/4",
                "rhythm_pattern": ["quarter", "quarter", "rest", "quarter"],
                "movement_actions": ["走一步", "拍手", "停住"],
                "bpm": 84,
            },
        },
    },
    {
        "case_id": "middle_phrase_singing",
        "title": "三年级乐句学唱",
        "expected_activity_id": "phrase_loop_singing",
        "practice_domain": "表现",
        "request": {
            "teacher_request": "三年级歌曲分句学唱，做听一句唱一句的乐句学唱活动",
            "lesson_text": "学生先整体听歌曲，再分句模唱，注意乐句、歌词和自然声音。",
            "grade_band": "middle_primary",
            "available_materials": {
                "song_title": "小雨沙沙",
                "lyrics_phrase": ["小雨小雨沙沙沙", "种子种子在说话"],
                "melody_phrase": ["do re mi mi re", "mi sol mi re do"],
                "audio_clip": "song-phrase.mp3",
                "bpm": 86,
            },
        },
    },
    {
        "case_id": "middle_phrase_loop_singing",
        "title": "三年级分句循环学唱",
        "expected_activity_id": "phrase_loop_singing",
        "practice_domain": "表现",
        "request": {
            "teacher_request": "三年级歌曲分句循环学唱，听一句唱一句，教师确认后进入下一句",
            "lesson_text": "学生先完整听歌曲，再按乐句听唱，关注自然声音、乐句记忆和歌词表达。",
            "grade_band": "middle_primary",
            "available_materials": {
                "song_title": "小雨沙沙",
                "lyrics_phrase": ["小雨小雨沙沙沙", "种子种子在说话"],
                "melody_phrase": ["do re mi mi re", "mi sol mi re do"],
                "audio_clip": "song-phrase-loop.mp3",
                "bpm": 86,
            },
        },
    },
    {
        "case_id": "upper_difficult_phrase_loop",
        "title": "五年级难点乐句慢速循环",
        "expected_activity_id": "phrase_singing_practice",
        "practice_domain": "表现",
        "request": {
            "teacher_request": "五年级歌曲难点乐句循环练习，慢速听唱并关注换气和旋律走向",
            "lesson_text": "学生先听难点乐句，再慢速模唱，注意呼吸位置、旋律走向和自然声音。",
            "grade_band": "upper_primary",
            "available_materials": {
                "song_title": "让我们荡起双桨",
                "lyrics_phrase": ["小船儿轻轻飘荡在水中", "迎面吹来了凉爽的风"],
                "melody_phrase": ["mi sol la sol mi re", "re mi sol mi re do"],
                "audio_clip": "difficult-phrase.mp3",
                "difficult_phrase": "迎面吹来了凉爽的风",
                "breath_points": ["吹来了/凉爽的风"],
                "bpm": 72,
            },
        },
    },
    {
        "case_id": "middle_call_response_singing",
        "title": "三年级接唱练习",
        "expected_activity_id": "phrase_loop_singing",
        "practice_domain": "表现",
        "request": {
            "teacher_request": "三年级做师生接唱和小组接唱练习，听一句唱一句",
            "lesson_text": "学生听教师或音频提示后接唱下一句，关注乐句衔接和歌词表达。",
            "grade_band": "middle_primary",
            "available_materials": {
                "lyrics_phrase": ["太阳出来了", "花儿对我笑"],
                "melody_phrase": ["do mi sol sol", "sol mi re do"],
                "audio_clip": "call-response.mp3",
                "classroom_group_task": ["A组唱问句", "B组唱答句"],
                "bpm": 88,
            },
        },
    },
    {
        "case_id": "lower_lyrics_rhythm",
        "title": "二年级歌词节奏朗读",
        "expected_activity_id": "lyrics_rhythm_reading",
        "practice_domain": "表现",
        "request": {
            "teacher_request": "二年级歌曲课，做歌词节奏朗读活动，先按节拍读歌词再拍出来",
            "lesson_text": "学生能按稳定拍朗读歌词，拍出歌词节奏，再回到歌曲演唱。",
            "grade_band": "lower_primary",
            "available_materials": {
                "lyrics_phrase": ["小雨沙沙", "种子发芽"],
                "rhythm_pattern": ["quarter", "eighth_pair", "quarter", "rest"],
                "meter": "2/4",
                "bpm": 84,
            },
        },
    },
    {
        "case_id": "middle_song_expression",
        "title": "四年级歌曲力度情绪处理",
        "expected_activity_id": "phrase_singing_practice",
        "practice_domain": "表现",
        "request": {
            "teacher_request": "四年级歌曲处理，分句学唱后加入力度和情绪处理",
            "lesson_text": "学生听范唱，分句演唱，并尝试用较弱、渐强和优美情绪处理歌曲。",
            "grade_band": "middle_primary",
            "available_materials": {
                "lyrics_phrase": ["月儿明风儿静", "树叶儿遮窗棂"],
                "melody_phrase": ["do re mi sol", "sol mi re do"],
                "audio_clip": "song-expression.mp3",
                "target_expression": ["优美", "轻柔", "渐强"],
                "bpm": 80,
            },
        },
    },
    {
        "case_id": "middle_solfege_sorting",
        "title": "四年级唱名排序",
        "expected_activity_id": "solfege_sorting",
        "practice_domain": "表现",
        "request": {
            "teacher_request": "四年级唱名排序，听 do re mi sol 的音高走向再排列唱名",
            "lesson_text": "学生通过听辨和模唱，理解 do/re/mi/sol/la 的音高方向。",
            "grade_band": "middle_primary",
            "available_materials": {
                "solfege_set": ["do", "re", "mi", "sol", "la"],
                "pitch_motion": ["up", "up", "down", "same"],
                "bpm": 92,
            },
        },
    },
    {
        "case_id": "upper_melody_contour",
        "title": "五年级旋律线手势描画",
        "expected_activity_id": "melody_contour_trace",
        "practice_domain": "表现",
        "request": {
            "teacher_request": "五年级旋律线描一描活动，听辨上行、下行、平稳并用手势画出旋律",
            "lesson_text": "学生先听短句，再跟着旋律线用手势表现音高走向，最后唱回。",
            "grade_band": "upper_primary",
            "available_materials": {
                "pitch_motion": ["up", "up", "down", "same"],
                "melody_phrase": ["do re mi sol mi"],
                "audio_clip": "melody-contour.mp3",
                "bpm": 88,
            },
        },
    },
    {
        "case_id": "lower_listening_mood",
        "title": "二年级听赏情绪选择",
        "expected_activity_id": "picture_listening_intro",
        "practice_domain": "欣赏",
        "request": {
            "teacher_request": "二年级欣赏课，听音乐后选择情绪图片并说依据",
            "lesson_text": "学生初听音乐，感受欢快、安静或优美的情绪，并用速度、力度说理由。",
            "grade_band": "lower_primary",
            "available_materials": {
                "audio_clip": "listening-mood.mp3",
                "expression_trait": ["欢快", "安静", "优美"],
                "evidence_terms": ["速度较快", "力度较强", "旋律流畅"],
            },
        },
    },
    {
        "case_id": "middle_listening_evidence",
        "title": "四年级欣赏复听找证据",
        "expected_activity_id": "listen_choose_explain",
        "practice_domain": "欣赏",
        "request": {
            "teacher_request": "四年级欣赏复听，找速度、力度和旋律证据后选择情绪",
            "lesson_text": "学生复听音乐，用速度较快、力度较强、旋律跳跃等音乐词说明情绪依据。",
            "grade_band": "middle_primary",
            "available_materials": {
                "audio_clip": "relisten-evidence.mp3",
                "expression_trait": ["欢快", "紧张", "优美"],
                "evidence_terms": ["速度较快", "力度较强", "旋律跳跃", "节奏密集"],
            },
        },
    },
    {
        "case_id": "middle_listen_choose_explain",
        "title": "三年级听一听选一选",
        "expected_activity_id": "listen_choose_explain",
        "practice_domain": "欣赏",
        "request": {
            "teacher_request": "三年级欣赏课做听一听选一选活动，学生听完后选择情绪、速度、力度并说音乐依据",
            "lesson_text": "学生先完整听音乐，再选择欢快、优美或安静，并用速度较快、力度较强、旋律流畅说依据。",
            "grade_band": "middle_primary",
            "available_materials": {
                "audio_clip": "listen-choose.mp3",
                "expression_trait": ["欢快", "优美", "安静"],
                "evidence_terms": ["速度较快", "力度较强", "旋律流畅"],
            },
        },
    },
    {
        "case_id": "middle_timbre_match",
        "title": "四年级音色侦探",
        "expected_activity_id": "instrument_timbre_match",
        "practice_domain": "欣赏",
        "request": {
            "teacher_request": "四年级欣赏课，做听辨笛子、二胡和小提琴音色的音色侦探",
            "lesson_text": "学生先听声音，再根据气息感、弦鸣、明亮等音色证据判断乐器。",
            "grade_band": "middle_primary",
            "available_materials": {
                "audio_clip": "timbre.mp3",
                "instrument_pool": ["笛子", "二胡", "小提琴"],
                "timbre_set": ["气息感", "弦鸣", "明亮", "柔和"],
            },
        },
    },
    {
        "case_id": "upper_instrument_family",
        "title": "五年级乐器家族分类",
        "expected_activity_id": "instrument_family_sorting",
        "practice_domain": "联系",
        "request": {
            "teacher_request": "五年级欣赏拓展，听辨乐器家族，按发声方式给乐器分类",
            "lesson_text": "学生先听笛子、二胡、琵琶、小鼓等音色，再按吹奏、拉弦、弹拨、打击分类并说明依据。",
            "grade_band": "upper_primary",
            "available_materials": {
                "audio_clip": "instrument-family.mp3",
                "instrument_pool": ["笛子", "二胡", "琵琶", "小鼓"],
                "instrument_family_set": ["吹奏", "拉弦", "弹拨", "打击"],
                "timbre_set": ["气息感", "弦鸣", "拨弦", "敲击感"],
            },
        },
    },
    {
        "case_id": "upper_form_ordering",
        "title": "五年级 ABA 曲式排序",
        "expected_activity_id": "form_ordering",
        "practice_domain": "欣赏",
        "request": {
            "teacher_request": "五年级欣赏课，做 ABA 曲式排序和主题再现活动",
            "lesson_text": "学生复听三个段落，听辨主题段、对比段和再现段，说出重复与对比依据。",
            "grade_band": "upper_primary",
            "available_materials": {
                "audio_clip": "form.mp3",
                "form_structure": "ABA",
                "section_length_bars": 8,
            },
        },
    },
    {
        "case_id": "lower_rest_freeze",
        "title": "二年级休止停住体验",
        "expected_activity_id": "rhythm_warmup",
        "practice_domain": "表现",
        "request": {
            "teacher_request": "二年级休止冻结小游戏，听到休止要停住，练习稳定拍",
            "lesson_text": "学生先听节奏，在休止处停住，用身体动作表现休止也是音乐。",
            "grade_band": "lower_primary",
            "available_materials": {
                "meter": "2/4",
                "rhythm_pattern": ["quarter", "rest", "eighth_pair", "quarter"],
                "body_action_set": ["拍手", "停住", "拍腿"],
                "bpm": 82,
            },
        },
    },
    {
        "case_id": "middle_body_percussion",
        "title": "三年级身体打击编排",
        "expected_activity_id": "body_percussion_builder",
        "practice_domain": "创造",
        "request": {
            "teacher_request": "三年级身体打击编排，用拍手、拍腿、跺脚组合一个两小节节奏",
            "lesson_text": "学生用身体动作表现节奏和节拍，注意动作力度和小节完整。",
            "grade_band": "middle_primary",
            "available_materials": {
                "rhythm_pattern": ["quarter", "quarter", "eighth_pair", "quarter"],
                "meter": "2/4",
                "body_action_set": ["拍手", "拍腿", "跺脚", "停住"],
                "bpm": 92,
            },
        },
    },
    {
        "case_id": "middle_rhythm_creation",
        "title": "四年级节奏创编",
        "expected_activity_id": "body_percussion_builder",
        "practice_domain": "创造",
        "request": {
            "teacher_request": "四年级节奏创编，用节奏卡和身体动作编一个两小节节奏",
            "lesson_text": "学生在二拍子框架内选择节奏和动作，保证小节完整，回放后修改。",
            "grade_band": "middle_primary",
            "available_materials": {
                "rhythm_pattern": ["quarter", "eighth_pair", "quarter", "rest"],
                "meter": "2/4",
                "body_action_set": ["拍手", "拍腿", "跺脚", "停住"],
                "creation_constraint": "两小节，必须包含一个休止",
                "bpm": 92,
            },
        },
    },
    {
        "case_id": "upper_xylophone_creation",
        "title": "五年级五声短句创编",
        "expected_activity_id": "xylophone_creation",
        "practice_domain": "创造",
        "request": {
            "teacher_request": "五年级没有实体音条琴，做一个五声音阶短句创编小游戏",
            "lesson_text": "学生用 do re mi sol la 创编两小节短句，试听后修改并说明五声风格。",
            "grade_band": "upper_primary",
            "available_materials": {
                "solfege_set": ["do", "re", "mi", "sol", "la"],
                "rhythm_pattern": ["quarter", "quarter", "eighth_pair", "quarter"],
                "meter": "2/4",
                "composition_total_bars": 2,
                "bpm": 88,
            },
            "classroom_constraints": {"no_real_instruments": True},
        },
    },
    {
        "case_id": "middle_orff_ensemble",
        "title": "四年级奥尔夫打击乐合奏",
        "expected_activity_id": "orff_percussion_ensemble",
        "practice_domain": "表现",
        "request": {
            "teacher_request": "四年级没有实体打击乐器，做一个奥尔夫小组合奏活动",
            "lesson_text": "学生分三组负责固定节奏声部，听稳定拍进入并完成合奏展示。",
            "grade_band": "middle_primary",
            "available_materials": {
                "rhythm_pattern": ["quarter", "eighth_pair", "quarter", "rest"],
                "classroom_group_task": ["A组手鼓强拍", "B组木鱼稳定拍", "C组沙锤弱拍"],
                "group_count": 3,
                "meter": "2/4",
                "bpm": 88,
            },
            "classroom_constraints": {"no_real_instruments": True},
        },
    },
    {
        "case_id": "middle_classroom_band_roles",
        "title": "四年级小乐队分声部",
        "expected_activity_id": "classroom_band_roles",
        "practice_domain": "表现",
        "request": {
            "teacher_request": "四年级小乐队分声部活动，给每组分配手鼓、木鱼、沙锤声部并完成合奏",
            "lesson_text": "学生按小组任务卡负责不同打击乐声部，先听稳定拍和同伴声部，再按教师指挥进入。",
            "grade_band": "middle_primary",
            "available_materials": {
                "rhythm_pattern": ["quarter", "eighth_pair", "quarter", "rest"],
                "classroom_group_task": ["A组手鼓强拍", "B组木鱼稳定拍", "C组沙锤弱拍"],
                "instrument_parts": ["hand_drum", "woodblock", "shaker"],
                "group_count": 3,
                "meter": "2/4",
                "bpm": 88,
            },
            "classroom_constraints": {"no_real_instruments": True},
        },
    },
    {
        "case_id": "lower_group_relay",
        "title": "二年级小组节奏接力展示",
        "expected_activity_id": "group_relay_performance",
        "practice_domain": "表现",
        "request": {
            "teacher_request": "二年级小组节奏接力展示，每组轮流拍一个节奏并互相评价",
            "lesson_text": "学生按小组接力完成拍手节奏，听同伴表现，并用一句话评价节奏是否稳定。",
            "grade_band": "lower_primary",
            "available_materials": {
                "classroom_group_task": ["A组拍第一小节", "B组接第二小节", "C组做休止动作"],
                "assessment_criteria": ["节奏稳定", "能听同伴", "休止能停住"],
                "rhythm_pattern": ["quarter", "quarter", "rest", "quarter"],
                "meter": "2/4",
            },
        },
    },
    {
        "case_id": "upper_show_peer_feedback",
        "title": "五年级小组展示与同伴评价",
        "expected_activity_id": "show_and_peer_feedback",
        "practice_domain": "表现",
        "request": {
            "teacher_request": "五年级小组展示与同伴评价活动，学生展示后同伴用音乐依据互评",
            "lesson_text": "各小组展示节奏创编成果，同伴先听展示，再围绕节奏稳定、进入整齐和合作倾听说一句建议。",
            "grade_band": "upper_primary",
            "available_materials": {
                "classroom_group_task": ["A组展示节奏创编", "B组展示身体打击", "C组展示五声短句"],
                "assessment_criteria": ["节奏稳定", "进入整齐", "能听同伴"],
                "music_focus": "节奏创编展示",
                "evidence_terms": ["节奏稳定", "进入整齐", "力度有变化", "能听同伴"],
            },
        },
    },
    {
        "case_id": "upper_exit_ticket",
        "title": "六年级课堂出口票",
        "expected_activity_id": "exit_ticket_review",
        "practice_domain": "联系",
        "request": {
            "teacher_request": "六年级课堂出口票，复习今天听赏中的曲式和音乐依据",
            "lesson_text": "学生用一句话说明本课听到的重复、对比或再现依据。",
            "grade_band": "upper_primary",
            "available_materials": {
                "assessment_criteria": ["能说出本课音乐要素", "能给出听到的依据"],
                "music_focus": "曲式中的重复、对比和再现",
                "objective": "复习曲式听辨证据",
            },
        },
    },
]


MISSING_MATERIAL_DEMO: dict[str, Any] = {
    "case_id": "missing_timbre_material",
    "title": "缺材料音色侦探",
    "expected_activity_id": "instrument_timbre_match",
    "practice_domain": "欣赏",
    "request": {
        "teacher_request": "做一个听辨乐器音色的音色侦探小游戏",
        "lesson_text": "学生能听辨不同乐器音色并说出依据。",
        "grade_band": "middle_primary",
        "available_materials": {},
    },
}


def build_primary_composer_casebook_report(*, include_missing_material_demo: bool = False) -> dict[str, Any]:
    cases = [_case_result(case) for case in PRIMARY_CLASSROOM_CASES]
    blocking_failures = [
        failure
        for case in cases
        for failure in _case_blocking_failures(case)
    ]
    report: dict[str, Any] = {
        "version": CASEBOOK_REPORT_VERSION,
        "scope": "primary_school_music_only",
        "music_education_basis": {
            "curriculum_logic": "按小学音乐课堂的审美感知、艺术表现、创意实践、文化理解组织活动。",
            "learning_sequence": "体验在先，表现跟进，理解生成，迁移或创造收束。",
            "student_practices": ["listen", "sing", "play", "move", "read", "create", "evaluate"],
            "not_generic_game_rule": "先判断音乐目标和学生音乐实践，再选择游戏机制、组件、教具和虚拟乐器。",
        },
        "status": "pass" if not blocking_failures else "fail",
        "coverage_summary": _coverage_summary(cases),
        "cases": cases,
        "blocking_failures": blocking_failures,
        "implementation_status": {
            "composer": "implemented",
            "case_count": len(cases),
            "missing_material_demo": "included" if include_missing_material_demo else "available_on_request",
        },
    }
    if include_missing_material_demo:
        report["missing_material_demo"] = _case_result(MISSING_MATERIAL_DEMO)
    return report


def build_primary_composer_casebook_summary() -> dict[str, Any]:
    report = build_primary_composer_casebook_report()
    return {
        "version": report["version"],
        "status": report["status"],
        "case_count": len(report["cases"]),
        "activity_coverage": report["coverage_summary"]["activity_ids"],
        "practice_domain_coverage": report["coverage_summary"]["practice_domains"],
        "endpoint": "/api/primary-activity-library/composer-casebook",
    }


def _case_result(case: dict[str, Any]) -> dict[str, Any]:
    composition = compose_music_game(deepcopy(case["request"]))
    alignment = composition["education_alignment"]
    learning_path = alignment.get("music_learning_path", {})
    missing_fields = list(composition.get("missing_fields", []))
    runtime = composition.get("runtime", {})
    result = {
        "case_id": case["case_id"],
        "title": case["title"],
        "grade_band": case["request"].get("grade_band", ""),
        "expected_activity_id": case["expected_activity_id"],
        "composition_status": composition["status"],
        "selected_activity_id": composition["selected_activity_id"],
        "selected_activity_name": composition.get("selected_activity_name", ""),
        "selected_game_template": composition.get("selected_game_template"),
        "selected_components": deepcopy(composition.get("selected_components", [])),
        "selected_teaching_aids": deepcopy(composition.get("selected_teaching_aids", [])),
        "selected_virtual_instruments": deepcopy(composition.get("selected_virtual_instruments", [])),
        "selected_assets": deepcopy(composition.get("selected_assets", [])),
        "selected_rules": deepcopy(composition.get("selected_rules", [])),
        "teacher_confirm_fields": deepcopy(composition.get("teacher_confirm_fields", [])),
        "material_binding": deepcopy(composition.get("material_binding", {})),
        "missing_fields": missing_fields,
        "failed_gates": deepcopy(composition.get("failed_gates", [])),
        "quality_gates": deepcopy(composition.get("quality_gates", {})),
        "runtime_status": runtime.get("runtime_status", ""),
        "student_entry": runtime.get("student_entry", ""),
        "classroom_runtime": deepcopy(composition.get("classroom_runtime", {})),
        "why": composition.get("why", ""),
        "teacher_explanation": deepcopy(composition.get("teacher_explanation", {})),
        "music_education_basis": {
            "core_competency": alignment.get("primary_competency", ""),
            "secondary_competency": alignment.get("secondary_competency", ""),
            "student_practices": deepcopy(alignment.get("student_practices", [])),
            "music_elements": deepcopy(alignment.get("music_elements", [])),
            "teaching_stages": deepcopy(alignment.get("teaching_stages", [])),
            "grade_fit": deepcopy(alignment.get("grade_fit", {})),
            "practice_domain": case["practice_domain"],
        },
        "music_learning_path": {
            "experience": learning_path.get("experience", ""),
            "performance": learning_path.get("performance", ""),
            "understanding": learning_path.get("understanding", ""),
            "transfer_or_creation": learning_path.get("transfer_or_creation", ""),
        },
        "acceptance_questions": _acceptance_questions(composition),
        "missing_library_or_material_explanation": _missing_explanation(missing_fields),
    }
    return result


def _acceptance_questions(composition: dict[str, Any]) -> dict[str, bool]:
    alignment = composition["education_alignment"]
    practices = set(alignment.get("student_practices", []))
    has_real_music_practice = bool(practices & {"listen", "sing", "play", "tap", "move", "read", "arrange", "create", "perform", "choose", "match", "classify", "order", "assess"})
    runtime = composition.get("runtime", {})
    return {
        "trains_specific_music_element": bool(alignment.get("music_elements")),
        "has_real_music_practice": has_real_music_practice,
        "has_core_competency": bool(alignment.get("primary_competency")),
        "has_grade_fit": bool(alignment.get("grade_fit")),
        "follows_experience_performance_understanding_path": bool(alignment.get("music_learning_path")),
        "has_teacher_control": "teacher_control_bar" in composition.get("selected_components", []),
        "reports_missing_materials": composition["status"] == "ready" or bool(composition.get("missing_fields")),
        "runtime_artifact_ready": runtime.get("runtime_status") == "ready",
    }


def _case_blocking_failures(case: dict[str, Any]) -> list[dict[str, Any]]:
    failures: list[dict[str, Any]] = []
    if case["composition_status"] != "ready":
        failures.append({"case_id": case["case_id"], "reason": "composition_not_ready", "missing_fields": case["missing_fields"]})
    if case["selected_activity_id"] != case["expected_activity_id"]:
        failures.append(
            {
                "case_id": case["case_id"],
                "reason": "unexpected_activity_selection",
                "expected": case["expected_activity_id"],
                "actual": case["selected_activity_id"],
            }
        )
    if case["runtime_status"] != "ready":
        failures.append({"case_id": case["case_id"], "reason": "runtime_not_ready", "runtime_status": case["runtime_status"]})
    for question_id, passed in case["acceptance_questions"].items():
        if not passed:
            failures.append({"case_id": case["case_id"], "reason": f"acceptance_failed:{question_id}"})
    return failures


def _coverage_summary(cases: list[dict[str, Any]]) -> dict[str, Any]:
    activity_ids = _dedupe([case["selected_activity_id"] for case in cases])
    competencies = _dedupe([case["music_education_basis"]["core_competency"] for case in cases])
    practices = _dedupe(
        [
            practice
            for case in cases
            for practice in case["music_education_basis"]["student_practices"]
        ]
    )
    elements = _dedupe(
        [
            element
            for case in cases
            for element in case["music_education_basis"]["music_elements"]
        ]
    )
    domains = _dedupe([case["music_education_basis"]["practice_domain"] for case in cases])
    grade_bands = _dedupe([case["grade_band"] for case in cases])
    return {
        "activity_ids": activity_ids,
        "core_competencies": competencies,
        "student_practices": practices,
        "music_elements": elements,
        "practice_domains": domains,
        "grade_bands": grade_bands,
        "daily_classroom_tasks": [
            "唱歌分句学唱",
            "歌词节奏",
            "稳定拍与强弱拍",
            "欣赏初听与复听证据",
            "音色听辨",
            "曲式感知",
            "唱名与音高",
            "身体打击",
            "五声创编",
            "奥尔夫合奏",
            "课堂评价",
        ],
    }


def _missing_explanation(missing_fields: list[str]) -> str:
    if not missing_fields:
        return "材料完整，当前库条目、组件、教具或虚拟乐器足以生成学生端与教师控制端。"
    return f"缺少 {', '.join(missing_fields)}，不能交付学生端；请先补齐对应音乐材料或更换不依赖这些材料的活动。"


def _dedupe(items: list[Any]) -> list[Any]:
    result: list[Any] = []
    for item in items:
        if item not in ("", None, [], {}) and item not in result:
            result.append(item)
    return result
