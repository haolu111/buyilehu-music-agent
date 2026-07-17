# 把活动组合结果转换成学生端可以直接运行的状态数据
from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.services.assets.asset_pack_file_validator import resolve_static_asset_url
from app.services.assets.asset_pack_registry import get_asset_pack
from app.services.games.game_template_registry import build_game_instance
from app.services.instruments.instrument_audio_registry import get_instrument_audio_pack
from app.services.runtime.music_classroom_suite import build_default_music_media_session


RUNTIME_BUILDER_VERSION = "primary_music_game_runtime_builder_v1"


def build_primary_music_game_runtime(
    *,
    composition: dict[str, Any],
    request: dict[str, Any],
) -> dict[str, Any]:
    if composition.get("status") != "ready":
        return _empty_runtime("missing_material")
    if composition.get("selected_activity_id") in {"picture_listening_intro", "listen_choose_explain"}:
        return _listening_choice_runtime(composition=composition, request=request)
    if composition.get("selected_activity_id") == "lesson_opening_hook":
        return _lesson_opening_runtime(composition=composition, request=request)
    if composition.get("selected_activity_id") == "theme_return_action":
        return _theme_return_action_runtime(composition=composition, request=request)
    if composition.get("selected_activity_id") in {"lyrics_rhythm_practice", "lyrics_rhythm_reading"}:
        return _lyrics_rhythm_runtime(composition=composition, request=request)
    if composition.get("selected_activity_id") == "rhythm_question_answer":
        return _rhythm_question_answer_runtime(composition=composition, request=request)
    if composition.get("selected_activity_id") == "steady_beat_walk":
        return _steady_beat_walk_runtime(composition=composition, request=request)
    if composition.get("selected_activity_id") in {"meter_body_movement", "strong_weak_beat_circle"}:
        return _strong_weak_beat_runtime(composition=composition, request=request)
    if composition.get("selected_activity_id") in {"orff_percussion_ensemble", "classroom_band_roles"}:
        return _orff_ensemble_runtime(composition=composition, request=request)
    if composition.get("selected_activity_id") in {"phrase_singing_practice", "phrase_loop_singing"}:
        return _phrase_singing_runtime(composition=composition, request=request)
    if composition.get("selected_activity_id") == "solfege_echo_singing":
        return _solfege_echo_runtime(composition=composition, request=request)
    if composition.get("selected_activity_id") == "melody_contour_trace":
        return _melody_contour_runtime(composition=composition, request=request)
    if composition.get("selected_activity_id") == "simple_score_following":
        return _simple_score_runtime(composition=composition, request=request)
    if composition.get("selected_activity_id") == "instrument_family_sorting":
        return _instrument_family_runtime(composition=composition, request=request)
    if composition.get("selected_activity_id") == "xylophone_creation":
        return _pentatonic_melody_runtime(composition=composition, request=request)
    if composition.get("selected_activity_id") == "body_percussion_builder":
        return _body_percussion_runtime(composition=composition, request=request)
    if composition.get("selected_activity_id") == "graphic_score_create":
        return _graphic_score_runtime(composition=composition, request=request)
    if composition.get("selected_activity_id") == "group_relay_performance":
        return _group_relay_runtime(composition=composition, request=request)
    if composition.get("selected_activity_id") == "show_and_peer_feedback":
        return _peer_feedback_runtime(composition=composition, request=request)
    if composition.get("selected_activity_id") == "exit_ticket_review":
        return _exit_ticket_runtime(composition=composition, request=request)
    if composition.get("selected_activity_id") in {
        "song_audio_workbench_activity",
        "score_audio_sync_practice",
        "ear_training_practice",
        "vocal_choir_training_activity",
        "ensemble_conductor_rehearsal",
    }:
        return _music_classroom_suite_runtime(composition=composition, request=request)
    template_id = composition.get("selected_game_template")
    if template_id not in {
        "beat_guardian_core",
        "rhythm_echo_core",
        "timbre_detective_core",
        "form_treasure_core",
        "composition_puzzle_core",
        "pitch_ladder_core",
        "solfege_target_core",
    }:
        return _empty_runtime("template_runtime_not_connected")

    available = request.get("available_materials") if isinstance(request.get("available_materials"), dict) else {}
    payload = _template_payload(str(template_id), composition, available)
    instance = build_game_instance(payload)
    config = deepcopy(instance["config"])
    _apply_music_runtime_overrides(config, str(template_id), composition, available)
    instance["config"] = config
    state = {
        "workflow": {
            "workflow_kind": "primary_activity_game",
            "composition_spec": _public_composition_summary(composition),
            "education_alignment": deepcopy(composition["education_alignment"]),
            "gameplay_blueprint": {
                "student_facing_name": instance["template_label"],
                "prompt": composition["teacher_explanation"]["why_this_game"],
                "operation_type": str(template_id).replace("_core", ""),
                "scene_goal": "通过音乐实践完成本课目标。",
                "game_genre": config.get("game_genre", ""),
            },
        },
        "instance": {
            "template_label": instance["template_label"],
            "student_task": instance.get("student_task", {}),
        },
        "template_id": template_id,
        "age_ui_profile": _age_profile(composition.get("difficulty", {}).get("grade_band", "")),
        "config": config,
        "student_task_copy": config.get("student_task_copy") or instance.get("student_task", {}),
        "music_reason_prompts": config.get("music_reason_prompts", {}),
        "result_transfer_prompt": config.get("result_transfer_prompt", "回到教材音乐中再表现一次。"),
    }
    return {
        "runtime_builder_version": RUNTIME_BUILDER_VERSION,
        "student_game_state": state,
        "student_entry": "/template-console/student-game.html",
        "runtime_status": "ready",
    }


def _empty_runtime(reason: str) -> dict[str, Any]:
    return {
        "runtime_builder_version": RUNTIME_BUILDER_VERSION,
        "student_game_state": None,
        "student_entry": "",
        "runtime_status": reason,
    }


def _music_classroom_suite_runtime(*, composition: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    activity_id = str(composition.get("selected_activity_id") or "")
    component_by_activity = {
        "song_audio_workbench_activity": "song_audio_workbench",
        "score_audio_sync_practice": "score_audio_sync_player",
        "ear_training_practice": "ear_training_engine",
        "vocal_choir_training_activity": "vocal_choir_training",
        "ensemble_conductor_rehearsal": "ensemble_conductor",
    }
    component_id = component_by_activity[activity_id]
    available = request.get("available_materials") if isinstance(request.get("available_materials"), dict) else {}
    source_url = str(available.get("audio_clip") or available.get("audio_url") or available.get("source_audio_url") or "")
    grade_band = str((composition.get("difficulty") or {}).get("grade_band") or "middle_primary")
    grade_preset = _age_profile(grade_band)
    session = build_default_music_media_session(
        session_id=str(available.get("session_id") or f"{activity_id}-session"),
        source_url=source_url,
        source_kind="teacher_upload",
        grade_preset=grade_preset,
    )
    state = {
        "workflow": {
            "workflow_kind": "primary_activity_game",
            "education_alignment": deepcopy(composition.get("education_alignment") or {}),
            "teacher_explanation": deepcopy(composition.get("teacher_explanation") or {}),
        },
        "config": {
            "activity_id": activity_id,
            "runtime_component_id": component_id,
            "media_session": session,
            "available_materials": deepcopy(available),
            "teacher_confirm_required": True,
        },
    }
    return {
        "runtime_builder_version": RUNTIME_BUILDER_VERSION,
        "student_game_state": state,
        "student_entry": f"/template-console/music-classroom-suite.html?component={component_id}",
        "runtime_status": "ready",
    }


def _phrase_singing_runtime(*, composition: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    available = request.get("available_materials") if isinstance(request.get("available_materials"), dict) else {}
    lyrics = _phrase_list(available.get("lyrics_phrase") or available.get("lyrics_text"), ["第一乐句", "第二乐句"])
    melody = _phrase_list(available.get("melody_phrase") or available.get("target_solfege"), [])
    audio_clip = str(available.get("audio_clip") or available.get("audio_url") or "")
    difficult_phrase = str(available.get("difficult_phrase") or "").strip()
    breath_points = _phrase_list(available.get("breath_points"), [])
    bpm = int(available.get("bpm") or composition.get("difficulty", {}).get("bpm") or 86)
    activity_id = str(composition.get("selected_activity_id") or "phrase_singing_practice")
    practice_variant = (
        "phrase_loop"
        if activity_id == "phrase_loop_singing"
        else "difficult_phrase_repair"
        if difficult_phrase or breath_points
        else "whole_phrase"
    )
    is_formal_phrase_loop = activity_id == "phrase_loop_singing"
    state = {
        "workflow": {
            "workflow_kind": "primary_activity_game",
            "composition_spec": _public_composition_summary(composition),
            "education_alignment": deepcopy(composition["education_alignment"]),
            "gameplay_blueprint": {
                "student_facing_name": "分句循环学唱" if is_formal_phrase_loop else "乐句学唱",
                "prompt": composition["teacher_explanation"]["why_this_game"],
                "operation_type": "phrase_singing",
                "scene_goal": "通过听一句、唱一句和教师确认完成分句学唱。",
                "game_genre": "guided_singing_practice",
            },
        },
        "instance": {
            "template_label": "分句循环学唱" if is_formal_phrase_loop else "乐句学唱",
            "student_task": {
                "listen": "听什么：先听清当前乐句。",
                "do": "做什么：跟着提示唱回这一句。",
                "pass": "怎样过关：教师确认自然、完整、稳定后进入下一句。",
            },
        },
        "template_id": "primary_phrase_loop_singing" if is_formal_phrase_loop else "primary_phrase_singing",
        "age_ui_profile": _age_profile(composition.get("difficulty", {}).get("grade_band", "")),
        "config": {
            "activity_id": activity_id,
            "runtime_component": "PhraseSingingActivity",
            "lyrics_phrases": lyrics,
            "melody_phrases": melody,
            "audio_clip": audio_clip,
            "bpm": bpm,
            "practice_variant": practice_variant,
            "difficult_phrase": difficult_phrase,
            "breath_points": breath_points,
            "slow_loop_enabled": True,
            "show_breath_hint": bool(difficult_phrase or breath_points),
            "teacher_confirm_required": True,
            "phrase_loop_enabled": True,
            "show_pitch_hint": True,
            "record_export": "phrase_loop_singing_record_v1" if is_formal_phrase_loop else "phrase_singing_record_v1",
            "education_alignment": deepcopy(composition["education_alignment"]),
            "teacher_explanation": deepcopy(composition["teacher_explanation"]),
        },
        "student_task_copy": {
            "listen": "听什么：先听清当前乐句。",
            "do": "做什么：跟着提示唱回这一句。",
            "pass": "怎样过关：教师确认后进入下一句。",
        },
        "music_reason_prompts": {
            "retry": "再听一次这一句，注意歌词、换气和旋律走向。" if practice_variant == "difficult_phrase_repair" else "再听一次这一句，注意歌词和旋律走向。",
            "passed": "难点句稳定了，再回到前后乐句连唱。" if practice_variant == "difficult_phrase_repair" else "这一句稳定了，换下一句。",
        },
        "result_transfer_prompt": "把每个乐句连起来完整演唱。"
    }
    return {
        "runtime_builder_version": RUNTIME_BUILDER_VERSION,
        "student_game_state": state,
        "student_entry": "/template-console/phrase-singing-preview.html",
        "runtime_status": "ready",
    }


def _solfege_echo_runtime(*, composition: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    available = request.get("available_materials") if isinstance(request.get("available_materials"), dict) else {}
    solfege_set = _solfege_cards(available)
    echo_phrases = _echo_phrases(available, solfege_set)
    audio_clip = str(available.get("audio_clip") or available.get("audio_url") or available.get("source_audio_url") or "")
    bpm = int(available.get("bpm") or composition.get("difficulty", {}).get("bpm") or 88)
    state = {
        "workflow": {
            "workflow_kind": "primary_activity_game",
            "composition_spec": _public_composition_summary(composition),
            "education_alignment": deepcopy(composition["education_alignment"]),
            "gameplay_blueprint": {
                "student_facing_name": "唱名回声",
                "prompt": composition["teacher_explanation"]["why_this_game"],
                "operation_type": "solfege_echo_singing",
                "scene_goal": "先听教师或示范音唱名短句，再用自然声音回声模唱，并说出音高走向。",
                "game_genre": "guided_solfege_echo_singing",
            },
        },
        "instance": {
            "template_label": "唱名回声",
            "student_task": {
                "listen": "听什么：先听教师唱名短句和音高走向。",
                "do": "做什么：用自然声音回声模唱同一组唱名。",
                "pass": "怎样完成：唱名顺序正确，音高走向稳定，并由教师确认。",
            },
        },
        "template_id": "primary_solfege_echo",
        "age_ui_profile": _age_profile(composition.get("difficulty", {}).get("grade_band", "")),
        "config": {
            "activity_id": "solfege_echo_singing",
            "runtime_component": "SolfegeEchoActivity",
            "solfege_set": solfege_set,
            "pitch_motion": deepcopy(available.get("pitch_motion") or echo_phrases),
            "echo_phrases": echo_phrases,
            "audio_clip": audio_clip,
            "bpm": bpm,
            "teacher_confirm_required": True,
            "show_solfege": True,
            "show_pitch_motion": True,
            "education_alignment": deepcopy(composition["education_alignment"]),
            "teacher_explanation": deepcopy(composition["teacher_explanation"]),
        },
        "student_task_copy": {
            "listen": "听什么：教师先唱，学生先听不抢唱。",
            "do": "做什么：按同样唱名和音高走向模唱回来。",
            "pass": "怎样完成：教师确认唱名、音高走向和自然声音。",
        },
        "music_reason_prompts": {
            "listen_first": "先听教师唱名短句，再模唱。",
            "direction": "模唱后用手势或语言说出上行、下行或有上有下。",
            "teacher_confirm": "儿童歌唱声音由教师确认，不用机器分数替代判断。",
        },
        "result_transfer_prompt": "把这组唱名回到教材旋律或音条琴上再唱一次。",
    }
    return {
        "runtime_builder_version": RUNTIME_BUILDER_VERSION,
        "student_game_state": state,
        "student_entry": "/template-console/solfege-echo-preview.html",
        "runtime_status": "ready",
    }


def _melody_contour_runtime(*, composition: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    available = request.get("available_materials") if isinstance(request.get("available_materials"), dict) else {}
    pitch_motion = _phrase_list(
        available.get("pitch_motion") or available.get("melody_contour") or available.get("contour_steps") or available.get("direction_steps"),
        ["up", "down", "same"],
    )
    melody_phrases = _phrase_list(available.get("melody_phrase") or available.get("target_solfege"), ["do re mi sol mi"])
    audio_clip = str(available.get("audio_clip") or available.get("audio_url") or available.get("source_audio_url") or "")
    bpm = int(available.get("bpm") or composition.get("difficulty", {}).get("bpm") or 86)
    state = {
        "workflow": {
            "workflow_kind": "primary_activity_game",
            "composition_spec": _public_composition_summary(composition),
            "education_alignment": deepcopy(composition["education_alignment"]),
            "gameplay_blueprint": {
                "student_facing_name": "旋律线描一描",
                "prompt": composition["teacher_explanation"]["why_this_game"],
                "operation_type": "melody_contour_trace",
                "scene_goal": "先听短旋律，再用手势和线条跟踪上行、下行和平稳。",
                "game_genre": "guided_melody_contour_trace",
            },
        },
        "instance": {
            "template_label": "旋律线描一描",
            "student_task": {
                "listen": "听什么：先听短旋律的高低走向。",
                "do": "做什么：用手势向上、向下或平稳跟着旋律线走。",
                "pass": "怎样完成：方向判断稳定后，把旋律唱回或哼回。",
            },
        },
        "template_id": "primary_melody_contour_trace",
        "age_ui_profile": _age_profile(composition.get("difficulty", {}).get("grade_band", "")),
        "config": {
            "activity_id": "melody_contour_trace",
            "runtime_component": "MelodyContourTraceActivity",
            "pitch_motion": pitch_motion,
            "melody_phrases": melody_phrases,
            "audio_clip": audio_clip,
            "bpm": bpm,
            "teacher_confirm_required": True,
            "show_contour_hint": True,
            "record_export": "melody_contour_trace_record_v1",
            "education_alignment": deepcopy(composition["education_alignment"]),
            "teacher_explanation": deepcopy(composition["teacher_explanation"]),
        },
        "student_task_copy": {
            "listen": "听什么：先听旋律高低走向。",
            "do": "做什么：用手势跟踪旋律线。",
            "pass": "怎样完成：能说出上行、下行或平稳，并唱回短句。",
        },
        "music_reason_prompts": {
            "listen_first": "旋律线要先听到声音，再看线条和做手势。",
            "direction": "用上行、下行、平稳说明你听到的音高变化。",
            "success": "旋律线跟踪稳定了，请回到歌曲短句唱回。",
        },
        "result_transfer_prompt": "把刚才描出的旋律线回到教材歌曲或欣赏主题中唱一唱、听一听。",
    }
    return {
        "runtime_builder_version": RUNTIME_BUILDER_VERSION,
        "student_game_state": state,
        "student_entry": "/template-console/melody-contour-preview.html",
        "runtime_status": "ready",
    }


def _simple_score_runtime(*, composition: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    available = request.get("available_materials") if isinstance(request.get("available_materials"), dict) else {}
    numbered_score = _numbered_score_lines(available)
    solfege_lines = [_score_line_to_solfege(line) for line in numbered_score]
    rhythm_pattern = _pattern_steps(available)
    audio_clip = str(available.get("audio_clip") or available.get("audio_url") or available.get("source_audio_url") or "")
    meter = str(available.get("meter") or "2/4")
    bpm = int(available.get("bpm") or composition.get("difficulty", {}).get("bpm") or 84)
    state = {
        "workflow": {
            "workflow_kind": "primary_activity_game",
            "composition_spec": _public_composition_summary(composition),
            "education_alignment": deepcopy(composition["education_alignment"]),
            "gameplay_blueprint": {
                "student_facing_name": "简谱跟读",
                "prompt": composition["teacher_explanation"]["why_this_game"],
                "operation_type": "simple_score_following",
                "scene_goal": "先听音乐，再跟着简谱读唱名和节奏，建立谱面与声音的对应。",
                "game_genre": "guided_score_following",
            },
        },
        "instance": {
            "template_label": "简谱跟读",
            "student_task": {
                "listen": "听什么：先听旋律短句，不急着读谱。",
                "do": "做什么：看简谱数字，跟读唱名和节奏。",
                "pass": "怎样完成：能把谱面、唱名、节奏和听觉对应起来，由教师确认。",
            },
        },
        "template_id": "primary_simple_score_following",
        "age_ui_profile": _age_profile(composition.get("difficulty", {}).get("grade_band", "")),
        "config": {
            "activity_id": "simple_score_following",
            "runtime_component": "SimpleScoreFollowingActivity",
            "numbered_score": numbered_score,
            "solfege_lines": solfege_lines,
            "rhythm_pattern": rhythm_pattern,
            "audio_clip": audio_clip,
            "meter": meter,
            "bpm": bpm,
            "teacher_confirm_required": True,
            "show_solfege": True,
            "listen_before_read_required": True,
            "education_alignment": deepcopy(composition["education_alignment"]),
            "teacher_explanation": deepcopy(composition["teacher_explanation"]),
        },
        "student_task_copy": {
            "listen": "听什么：先听示范音频或教师弹唱。",
            "do": "做什么：按当前高亮的简谱短句读唱名和节奏。",
            "pass": "怎样完成：能说出数字对应唱名，并跟上节奏。",
        },
        "music_reason_prompts": {
            "listen_first": "先听再读谱，避免把识谱变成只认数字。",
            "score_mapping": "把 1/2/3/5/6 对应到 do/re/mi/sol/la，再跟节奏读出来。",
            "teacher_confirm": "简谱跟读表现由教师确认，不用机器视唱分数替代。",
        },
        "result_transfer_prompt": "回到歌曲或旋律短句，边看简谱边唱一次。",
    }
    return {
        "runtime_builder_version": RUNTIME_BUILDER_VERSION,
        "student_game_state": state,
        "student_entry": "/template-console/simple-score-preview.html",
        "runtime_status": "ready",
    }


def _pentatonic_melody_runtime(*, composition: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    available = request.get("available_materials") if isinstance(request.get("available_materials"), dict) else {}
    allowed_solfege = _solfege_cards(available)
    rhythm_pattern = _pattern_steps(available)
    meter = _meter_value(available.get("meter") or "2/4")
    total_bars = _bounded_int(available.get("composition_total_bars") or available.get("phrase_length_bars"), 1, 4, 2)
    bpm = int(available.get("bpm") or composition.get("difficulty", {}).get("bpm") or 88)
    state = {
        "workflow": {
            "workflow_kind": "primary_activity_game",
            "composition_spec": _public_composition_summary(composition),
            "education_alignment": deepcopy(composition["education_alignment"]),
            "gameplay_blueprint": {
                "student_facing_name": "五声音条琴创编",
                "prompt": composition["teacher_explanation"]["why_this_game"],
                "operation_type": "pentatonic_melody_creation",
                "scene_goal": "只用 do/re/mi/sol/la 和节奏框架创编短句，试听后修改并说明五声特点。",
                "game_genre": "guided_pentatonic_xylophone_creation",
            },
        },
        "instance": {
            "template_label": "五声音条琴创编",
            "student_task": {
                "listen": "听什么：试听自己放入的五声音级短句。",
                "do": "做什么：在节奏框架里选择 do/re/mi/sol/la，像演奏音条琴一样组成短句。",
                "pass": "怎样完成：短句填满、回放试听、修改后由教师确认创编理由。",
            },
        },
        "template_id": "primary_pentatonic_melody",
        "age_ui_profile": _age_profile(composition.get("difficulty", {}).get("grade_band", "")),
        "config": {
            "activity_id": "xylophone_creation",
            "runtime_component": "PentatonicMelodyActivity",
            "scale_type": "major_pentatonic",
            "allowed_solfege": allowed_solfege,
            "rhythm_pattern": rhythm_pattern,
            "meter": meter,
            "composition_total_bars": total_bars,
            "bpm": bpm,
            "virtual_instrument": "virtual_xylophone",
            "teacher_confirm_required": True,
            "audition_required": True,
            "min_unique_notes": 3,
            "creation_record_export": "pentatonic_creation_record_v1",
            "creation_summary_export": "pentatonic_creation_summary_v1",
            "relay_review_enabled": True,
            "relay_review_rule": "保留上一组结尾音，只改变一个节奏或一个音级后接龙。",
            "music_reason_prompts": {
                "constraint_missing": "只能使用 do、re、mi、sol、la，先把每个节奏格填满。",
                "needs_audition": "创编不是摆完就结束，请先回放听一遍再修改。",
                "success": "创编完成：回放短句，并说出你用了哪些五声音级和节奏办法。",
            },
            "education_alignment": deepcopy(composition["education_alignment"]),
            "teacher_explanation": deepcopy(composition["teacher_explanation"]),
        },
        "student_task_copy": {
            "listen": "听什么：每次创编后都要回放。",
            "do": "做什么：只用五声音级填入节奏格，像敲音条琴一样试听。",
            "pass": "怎样完成：至少使用 3 个不同音，回放后能说明创编办法。",
        },
        "music_reason_prompts": {
            "constraint_missing": "只能使用 do、re、mi、sol、la，先把每个节奏格填满。",
            "needs_audition": "创编不是摆完就结束，请先回放听一遍再修改。",
            "success": "创编完成：回放短句，并说出你用了哪些五声音级和节奏办法。",
        },
        "result_transfer_prompt": "把创编短句用虚拟音条琴播放，再唱一遍或请小组接龙改编。",
    }
    return {
        "runtime_builder_version": RUNTIME_BUILDER_VERSION,
        "student_game_state": state,
        "student_entry": "/template-console/pentatonic-melody-preview.html",
        "runtime_status": "ready",
    }


def _listening_choice_runtime(*, composition: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    available = request.get("available_materials") if isinstance(request.get("available_materials"), dict) else {}
    activity_id = str(composition.get("selected_activity_id") or "picture_listening_intro")
    dedicated_choice = activity_id == "listen_choose_explain"
    audio_clip = str(available.get("audio_clip") or available.get("audio_url") or available.get("source_audio_url") or "")
    expression_traits = _phrase_list(
        available.get("expression_trait")
        or available.get("expression_traits")
        or available.get("mood_options")
        or available.get("listening_traits"),
        ["欢快", "安静", "优美"],
    )
    evidence_terms = _phrase_list(
        available.get("evidence_terms")
        or available.get("music_evidence_terms")
        or available.get("reason_terms"),
        ["速度较快", "力度较强", "旋律流畅"],
    )
    required_evidence_dimensions = _required_listening_evidence_dimensions(evidence_terms)
    state = {
        "workflow": {
            "workflow_kind": "primary_activity_game",
            "composition_spec": _public_composition_summary(composition),
            "education_alignment": deepcopy(composition["education_alignment"]),
            "gameplay_blueprint": {
                "student_facing_name": "听一听选一选" if dedicated_choice else "听赏情绪选择",
                "prompt": composition["teacher_explanation"]["why_this_game"],
                "operation_type": "listen_choose_explain" if dedicated_choice else "listening_choice",
                "scene_goal": "先初听音乐，再选择情绪，并用音乐要素词说出依据。",
                "game_genre": "guided_listening_response",
            },
        },
        "instance": {
            "template_label": "听一听选一选" if dedicated_choice else "听赏情绪选择",
            "student_task": {
                "listen": "听什么：先完整听音乐，不急着选择。",
                "do": "做什么：选择最符合音乐感受的情绪卡。",
                "pass": "怎样完成：至少说出一个速度、力度或旋律方面的依据。",
            },
        },
        "template_id": "primary_listen_choose_explain" if dedicated_choice else "primary_listening_choice",
        "age_ui_profile": _age_profile(composition.get("difficulty", {}).get("grade_band", "")),
        "config": {
            "activity_id": activity_id,
            "runtime_component": "ListeningChoiceActivity",
            "audio_clip": audio_clip,
            "expression_traits": expression_traits,
            "evidence_terms": evidence_terms,
            "required_evidence_dimensions": required_evidence_dimensions,
            "generic_like_reason_allowed": False,
            "blocked_generic_reasons": ["喜欢", "好听", "不好听", "有趣"],
            "mood_card_pack": "mood_symbol_card_pack",
            "mood_card_assets": _mood_card_assets(expression_traits),
            "teacher_reason_required": True,
            "replay_enabled": True,
            "hide_words_supported": True,
            "record_export": "listening_reason_record_v1" if dedicated_choice else "listening_choice_record_v1",
            "summary_export": "listening_reason_summary_v1" if dedicated_choice else "listening_choice_summary_v1",
            "education_alignment": deepcopy(composition["education_alignment"]),
            "teacher_explanation": deepcopy(composition["teacher_explanation"]),
        },
        "student_task_copy": {
            "listen": "听什么：先完整听音乐，不急着选择。",
            "do": "做什么：选择情绪卡，再选择听到的音乐依据。",
            "pass": "怎样完成：能用速度、力度或旋律词说明理由。",
        },
        "music_reason_prompts": {
            "before_choice": "先听完整音乐，再选情绪。",
            "need_evidence": "请选择一个你听到的音乐依据，例如速度、力度、旋律或音色。",
            "transfer": "复听时检查你的依据是否还能听出来。",
        },
        "result_transfer_prompt": "带着选择的情绪和依据复听音乐，再用动作或表情表现一次。",
    }
    return {
        "runtime_builder_version": RUNTIME_BUILDER_VERSION,
        "student_game_state": state,
        "student_entry": "/template-console/listening-choice-preview.html",
        "runtime_status": "ready",
    }


def _opening_next_activity_hint(request: dict[str, Any]) -> str:
    text = f"{request.get('teacher_request') or ''} {request.get('lesson_text') or ''}"
    if any(marker in text for marker in ("学唱", "歌曲", "唱歌", "歌词")):
        return "进入分句学唱或歌词节奏朗读。"
    if any(marker in text for marker in ("欣赏", "听赏", "主题", "曲式")):
        return "进入复听证据、主题再现或曲式活动。"
    if any(marker in text for marker in ("节奏", "律动", "拍")):
        return "进入稳定拍、强弱拍或节奏模仿活动。"
    return "根据学生回答进入听赏、学唱或节奏实践。"


def _lesson_opening_runtime(*, composition: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    available = request.get("available_materials") if isinstance(request.get("available_materials"), dict) else {}
    lesson_topic = str(
        available.get("lesson_topic")
        or available.get("song_title")
        or available.get("work_title")
        or available.get("title")
        or "本课音乐"
    )
    expression_traits = _phrase_list(
        available.get("expression_trait")
        or available.get("expression_traits")
        or available.get("mood_options")
        or available.get("accepted_moods"),
        ["欢快", "安静", "优美"],
    )
    evidence_terms = _phrase_list(
        available.get("evidence_terms")
        or available.get("music_evidence_terms")
        or available.get("tempo_dynamic_terms"),
        ["速度较快", "力度较弱", "旋律流畅"],
    )
    opening_questions = _phrase_list(
        available.get("opening_questions")
        or available.get("hook_questions")
        or available.get("teacher_questions"),
        [
            f"你听到的{lesson_topic}像在发生什么？",
            "音乐的速度或力度给你什么感觉？",
            "你想带着哪个问题继续听或学唱？",
        ],
    )
    audio_clip = str(available.get("audio_clip") or available.get("audio_url") or available.get("source_audio_url") or "")
    state = {
        "workflow": {
            "workflow_kind": "primary_activity_game",
            "composition_spec": _public_composition_summary(composition),
            "education_alignment": deepcopy(composition["education_alignment"]),
            "gameplay_blueprint": {
                "student_facing_name": "课堂导入钩子",
                "prompt": composition["teacher_explanation"]["why_this_game"],
                "operation_type": "lesson_opening_hook",
                "scene_goal": "先听音乐片段，再用感受、图卡和音乐依据进入新课。",
                "game_genre": "guided_lesson_opening",
            },
        },
        "instance": {
            "template_label": "课堂导入钩子",
            "student_task": {
                "listen": "听什么：先听本课音乐片段，不先看答案。",
                "do": "做什么：选择一个感受或画面，再选一个听到的音乐依据。",
                "pass": "怎样进入下一步：用一句话回答导入问题，教师据此进入学唱或欣赏。",
            },
        },
        "template_id": "primary_lesson_opening",
        "age_ui_profile": _age_profile(composition.get("difficulty", {}).get("grade_band", "")),
        "config": {
            "activity_id": "lesson_opening_hook",
            "runtime_component": "LessonOpeningActivity",
            "lesson_topic": lesson_topic,
            "audio_clip": audio_clip,
            "expression_traits": expression_traits,
            "evidence_terms": evidence_terms,
            "opening_questions": opening_questions,
            "mood_card_pack": "music_mood_picture_pack",
            "mood_card_assets": _mood_card_assets(expression_traits, pack_id="music_mood_picture_pack"),
            "listen_before_picture_prompt_required": True,
            "generated_or_selected_asset_packs": ["music_mood_picture_pack"],
            "toolkit_bindings": {
                "components": ["audio_player", "picture_prompt_cards", "teacher_control_bar"],
                "teaching_aids": ["mood_picture_cards"],
            },
            "teacher_reason_required": True,
            "opening_record_export": "lesson_opening_record_v1",
            "summary_export": "lesson_opening_summary_v1",
            "next_activity_hint": _opening_next_activity_hint(request),
            "education_alignment": deepcopy(composition["education_alignment"]),
            "teacher_explanation": deepcopy(composition["teacher_explanation"]),
        },
        "student_task_copy": {
            "listen": "听什么：先听一小段本课音乐。",
            "do": "做什么：选感受、选音乐依据、选一个想继续探究的问题。",
            "pass": "怎样完成：能说出一句和音乐有关的开场回答。",
        },
        "music_reason_prompts": {
            "listen_first": "导入必须先听音乐，再看图片或问题。",
            "needs_evidence": "只说喜欢还不够，请补一个速度、力度、旋律或音色依据。",
            "success": "导入完成：带着这个问题进入下一段听赏、学唱或节奏活动。",
        },
        "result_transfer_prompt": "把学生选择最多的感受和依据作为下一环节的听赏或学唱关注点。",
    }
    return {
        "runtime_builder_version": RUNTIME_BUILDER_VERSION,
        "student_game_state": state,
        "student_entry": "/template-console/lesson-opening-preview.html",
        "runtime_status": "ready",
    }


def _theme_return_action_runtime(*, composition: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    available = request.get("available_materials") if isinstance(request.get("available_materials"), dict) else {}
    audio_clip = str(available.get("audio_clip") or available.get("audio_url") or available.get("source_audio_url") or "")
    action_choices = _phrase_list(available.get("action_choices") or available.get("theme_actions"), ["举主题卡", "画圆", "拍肩"])
    evidence_terms = _phrase_list(
        available.get("evidence_terms")
        or available.get("music_evidence_terms")
        or available.get("theme_evidence_terms"),
        ["旋律相同", "节奏相似", "力度变化"],
    )
    correct_action = str(available.get("correct_action") or action_choices[0]).strip()
    state = {
        "workflow": {
            "workflow_kind": "primary_activity_game",
            "composition_spec": _public_composition_summary(composition),
            "education_alignment": deepcopy(composition["education_alignment"]),
            "gameplay_blueprint": {
                "student_facing_name": "主题再现动作",
                "prompt": composition["teacher_explanation"]["why_this_game"],
                "operation_type": "theme_return_action",
                "scene_goal": "先听主题，复听时在主题再现时间窗做动作，并说出音乐依据。",
                "game_genre": "guided_theme_return_relistening",
            },
        },
        "instance": {
            "template_label": "主题再现动作",
            "student_task": {
                "listen": "听什么：先听清主题旋律，再复听主题什么时候回来。",
                "do": "做什么：主题回来时做约定动作。",
                "pass": "怎样完成：动作落在主题时间窗内，并能说出旋律或节奏依据。",
            },
        },
        "template_id": "primary_theme_return_action",
        "age_ui_profile": _age_profile(composition.get("difficulty", {}).get("grade_band", "")),
        "config": {
            "activity_id": "theme_return_action",
            "runtime_component": "ThemeReturnActionActivity",
            "audio_clip": audio_clip,
            "theme_label": str(available.get("theme_label") or available.get("theme_name") or "A 主题").strip(),
            "theme_windows": _theme_return_windows(available),
            "action_choices": action_choices,
            "correct_action": correct_action,
            "evidence_terms": evidence_terms,
            "replay_required": True,
            "record_export": "theme_return_action_record_v1",
            "summary_export": "theme_return_action_summary_v1",
            "education_alignment": deepcopy(composition["education_alignment"]),
            "teacher_explanation": deepcopy(composition["teacher_explanation"]),
        },
        "student_task_copy": {
            "listen": "听什么：先听主题，再复听主题是否回来。",
            "do": "做什么：主题回来时做动作卡上的动作。",
            "pass": "怎样完成：动作、时间窗和音乐依据都成立。",
        },
        "music_reason_prompts": {
            "before_action": "先听主题，不要只看时间提示猜答案。",
            "need_evidence": "请说出旋律相同、节奏相似或力度变化等音乐依据。",
            "success": "主题再现听辨成立：回到完整音乐中再听一次。",
        },
        "result_transfer_prompt": "完整复听作品，在每次主题回来时做动作并说出依据。",
    }
    return {
        "runtime_builder_version": RUNTIME_BUILDER_VERSION,
        "student_game_state": state,
        "student_entry": "/template-console/theme-return-action-preview.html",
        "runtime_status": "ready",
    }


def _lyrics_rhythm_runtime(*, composition: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    available = request.get("available_materials") if isinstance(request.get("available_materials"), dict) else {}
    lyrics = _phrase_list(available.get("lyrics_phrase") or available.get("lyrics_text"), ["第一句歌词", "第二句歌词"])
    rhythm_pattern = _pattern_steps(available)
    meter = str(available.get("meter") or "2/4")
    bpm = int(available.get("bpm") or composition.get("difficulty", {}).get("bpm") or 84)
    phrases = _lyrics_rhythm_phrases(
        available=available,
        legacy_lyrics=lyrics,
        legacy_pattern=rhythm_pattern,
        legacy_meter=meter,
        legacy_bpm=bpm,
    )
    material_status = "teacher_confirmation_required" if any(
        phrase.get("source") == "recognized_draft" or not phrase.get("teacherConfirmed")
        for phrase in phrases
    ) else "confirmed"
    practice_mode = "play_along" if available.get("practice_mode") == "play_along" else "echo"
    activity_id = str(composition.get("selected_activity_id") or "lyrics_rhythm_practice")
    is_reading = activity_id == "lyrics_rhythm_reading"
    state = {
        "workflow": {
            "workflow_kind": "primary_activity_game",
            "composition_spec": _public_composition_summary(composition),
            "education_alignment": deepcopy(composition["education_alignment"]),
            "gameplay_blueprint": {
                "student_facing_name": "歌词节奏朗读" if is_reading else "歌词节奏",
                "prompt": composition["teacher_explanation"]["why_this_game"],
                "operation_type": "lyrics_rhythm_reading" if is_reading else "lyrics_rhythm",
                "scene_goal": "先按稳定拍读歌词，再拍出歌词节奏，最后回到歌曲演唱。",
                "game_genre": "guided_lyrics_rhythm_practice",
            },
        },
        "instance": {
            "template_label": "歌词节奏朗读" if is_reading else "歌词节奏",
            "student_task": {
                "listen": "听什么：听稳定拍和歌词重音。",
                "do": "做什么：先读歌词，再按节奏拍出来。",
                "pass": "怎样完成：歌词能落在拍点上，节奏顺序稳定后再唱。",
            },
        },
        "template_id": "primary_lyrics_rhythm_reading" if is_reading else "primary_lyrics_rhythm",
        "age_ui_profile": _age_profile(composition.get("difficulty", {}).get("grade_band", "")),
        "config": {
            "version": "lyrics_rhythm_activity_v2",
            "activity_id": activity_id,
            "runtime_component": "LyricsRhythmActivity",
            "grade_preset": str(composition.get("difficulty", {}).get("grade_band") or "middle_primary"),
            "practice_mode": practice_mode,
            "phrases": phrases,
            "material_status": material_status,
            "lyrics_phrases": lyrics,
            "rhythm_pattern": rhythm_pattern,
            "meter": meter,
            "bpm": bpm,
            "teacher_confirm_required": True,
            "show_beat_track": True,
            "record_export": "lyrics_rhythm_reading_record_v2" if is_reading else "lyrics_rhythm_practice_record_v2",
            "education_alignment": deepcopy(composition["education_alignment"]),
            "teacher_explanation": deepcopy(composition["teacher_explanation"]),
        },
        "student_task_copy": {
            "listen": "听什么：先听稳定拍。",
            "do": "做什么：按拍点读歌词，再把歌词节奏拍出来。",
            "pass": "怎样完成：节奏稳定后回到歌曲演唱。",
        },
        "music_reason_prompts": {
            "read_first": "先按稳定拍读歌词，不急着唱。",
            "tap_again": "再拍一次，注意歌词字和拍点是否对齐。",
            "success": "歌词节奏稳定了，现在回到歌曲中唱出来。",
        },
        "result_transfer_prompt": "把刚才读准、拍稳的歌词放回歌曲中演唱。",
    }
    return {
        "runtime_builder_version": RUNTIME_BUILDER_VERSION,
        "student_game_state": state,
        "student_entry": "/template-console/lyrics-rhythm-preview.html",
        "runtime_status": "ready",
    }


def _lyrics_rhythm_phrases(
    *,
    available: dict[str, Any],
    legacy_lyrics: list[str],
    legacy_pattern: list[str],
    legacy_meter: str,
    legacy_bpm: int,
) -> list[dict[str, Any]]:
    supplied = available.get("lyrics_rhythm_phrases")
    if isinstance(supplied, list) and supplied:
        return [deepcopy(item) for item in supplied if isinstance(item, dict)]
    return [
        {
            "id": f"legacy-phrase-{index + 1}",
            "lyrics": text,
            "meter": legacy_meter,
            "bpm": legacy_bpm,
            "patternIds": list(legacy_pattern),
            "lyricUnits": [],
            "source": "teacher_manual",
            "teacherConfirmed": True,
        }
        for index, text in enumerate(legacy_lyrics)
    ]


def _rhythm_question_answer_runtime(*, composition: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    available = request.get("available_materials") if isinstance(request.get("available_materials"), dict) else {}
    question_pattern = _pattern_steps(available)
    answer_value = available.get("answer_pattern") or available.get("response_pattern") or available.get("student_answer_pattern")
    answer_pattern = [str(item) for item in answer_value] if isinstance(answer_value, list) and answer_value else list(reversed(question_pattern))
    meter = _meter_value(available.get("meter") or "2/4")
    bpm = int(available.get("bpm") or composition.get("difficulty", {}).get("bpm") or 92)
    state = {
        "workflow": {
            "workflow_kind": "primary_activity_game",
            "composition_spec": _public_composition_summary(composition),
            "education_alignment": deepcopy(composition["education_alignment"]),
            "gameplay_blueprint": {
                "student_facing_name": "节奏问答",
                "prompt": composition["teacher_explanation"]["why_this_game"],
                "operation_type": "rhythm_question_answer",
                "scene_goal": "先听教师节奏问句，再用同拍号答句回拍，形成节奏对话。",
                "game_genre": "guided_rhythm_call_response",
            },
        },
        "instance": {
            "template_label": "节奏问答",
            "student_task": {
                "listen": "听什么：先听教师或系统拍出的节奏问句。",
                "do": "做什么：用节奏垫回拍一个同拍号答句。",
                "pass": "怎样完成：答句小节完整，拍点稳定，并能说出和问句的关系。",
            },
        },
        "template_id": "primary_rhythm_question_answer",
        "age_ui_profile": _age_profile(composition.get("difficulty", {}).get("grade_band", "")),
        "config": {
            "activity_id": "rhythm_question_answer",
            "runtime_component": "RhythmQuestionAnswerActivity",
            "question_pattern": question_pattern,
            "answer_pattern": answer_pattern,
            "meter": meter,
            "bpm": bpm,
            "teacher_confirm_required": True,
            "show_beat_track": True,
            "record_export": "rhythm_question_answer_record_v1",
            "summary_export": "rhythm_question_answer_summary_v1",
            "education_alignment": deepcopy(composition["education_alignment"]),
            "teacher_explanation": deepcopy(composition["teacher_explanation"]),
        },
        "student_task_copy": {
            "listen": "听什么：先听问句。",
            "do": "做什么：回拍答句。",
            "pass": "怎样完成：答句小节完整，节奏稳定。",
        },
        "music_reason_prompts": {
            "listen_first": "节奏问答要先听问句，再回拍答句。",
            "bar_fit": "答句要符合拍号，小节不能多也不能少。",
            "success": "问答成立：请小组轮流接答，听听答句是否稳定。",
        },
        "result_transfer_prompt": "把节奏问答接到歌曲伴奏、身体打击或小组接龙里。",
    }
    return {
        "runtime_builder_version": RUNTIME_BUILDER_VERSION,
        "student_game_state": state,
        "student_entry": "/template-console/rhythm-question-preview.html",
        "runtime_status": "ready",
    }


def _steady_beat_walk_runtime(*, composition: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    available = request.get("available_materials") if isinstance(request.get("available_materials"), dict) else {}
    rhythm_pattern = _pattern_steps(available)
    meter = _meter_value(available.get("meter") or "2/4")
    bpm = int(available.get("bpm") or composition.get("difficulty", {}).get("bpm") or 84)
    movement_actions = _phrase_list(available.get("movement_actions") or available.get("body_action_set"), ["走一步", "拍手", "停住"])
    state = {
        "workflow": {
            "workflow_kind": "primary_activity_game",
            "composition_spec": _public_composition_summary(composition),
            "education_alignment": deepcopy(composition["education_alignment"]),
            "gameplay_blueprint": {
                "student_facing_name": "稳定拍行走",
                "prompt": composition["teacher_explanation"]["why_this_game"],
                "operation_type": "steady_beat_walk",
                "scene_goal": "先听稳定拍，再用走、拍、停把稳定拍和休止表现出来。",
                "game_genre": "guided_steady_beat_movement",
            },
        },
        "instance": {
            "template_label": "稳定拍行走",
            "student_task": {
                "listen": "听什么：先听稳定拍和休止位置。",
                "do": "做什么：跟着拍点走一步或拍手，休止时停住。",
                "pass": "怎样完成：动作落在稳定拍上，休止不移动。",
            },
        },
        "template_id": "primary_steady_beat_walk",
        "age_ui_profile": _age_profile(composition.get("difficulty", {}).get("grade_band", "")),
        "config": {
            "activity_id": "steady_beat_walk",
            "runtime_component": "SteadyBeatWalkActivity",
            "rhythm_pattern": rhythm_pattern,
            "meter": meter,
            "bpm": bpm,
            "movement_actions": movement_actions,
            "teacher_confirm_required": True,
            "show_beat_track": True,
            "record_export": "steady_beat_walk_record_v1",
            "education_alignment": deepcopy(composition["education_alignment"]),
            "teacher_explanation": deepcopy(composition["teacher_explanation"]),
        },
        "student_task_copy": {
            "listen": "听什么：先听稳定拍。",
            "do": "做什么：走一步、拍手或停住。",
            "pass": "怎样完成：能跟稳定拍一起走，休止时真的停住。",
        },
        "music_reason_prompts": {
            "listen_first": "低段律动先听稳定拍，再让身体跟上。",
            "rest_freeze": "休止不是空白，要停住让安静也成为音乐。",
            "success": "稳定拍已经能走出来，可以围圈或小组接力走。",
        },
        "result_transfer_prompt": "回到教材歌曲或律动片段，全班围圈跟稳定拍走一次。",
    }
    return {
        "runtime_builder_version": RUNTIME_BUILDER_VERSION,
        "student_game_state": state,
        "student_entry": "/template-console/steady-beat-walk-preview.html",
        "runtime_status": "ready",
    }


def _strong_weak_beat_runtime(*, composition: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    available = request.get("available_materials") if isinstance(request.get("available_materials"), dict) else {}
    meter = _meter_value(available.get("meter") or "2/4")
    bpm = int(available.get("bpm") or composition.get("difficulty", {}).get("bpm") or 88)
    activity_id = str(composition.get("selected_activity_id") or "meter_body_movement")
    is_circle = activity_id == "strong_weak_beat_circle"
    movement_actions = _phrase_list(available.get("movement_actions"), ["拍手", "拍腿", "轻拍肩", "轻拍手"])
    state = {
        "workflow": {
            "workflow_kind": "primary_activity_game",
            "composition_spec": _public_composition_summary(composition),
            "education_alignment": deepcopy(composition["education_alignment"]),
            "gameplay_blueprint": {
                "student_facing_name": "强弱拍圆圈" if is_circle else "强弱拍律动",
                "prompt": composition["teacher_explanation"]["why_this_game"],
                "operation_type": "strong_weak_beat_circle" if is_circle else "strong_weak_beat_body_movement",
                "scene_goal": "先听稳定拍和强弱关系，再用大动作、小动作表现拍号强弱规律。",
                "game_genre": "guided_meter_body_movement",
            },
        },
        "instance": {
            "template_label": "强弱拍圆圈" if is_circle else "强弱拍律动",
            "student_task": {
                "listen": "听什么：听每小节第 1 拍和后续弱拍。",
                "do": "做什么：用拍手、拍腿、轻拍等身体动作表现强弱。",
                "pass": "怎样完成：动作能和拍号强弱对应，并保持稳定拍。",
            },
        },
        "template_id": "primary_strong_weak_beat_circle" if is_circle else "primary_strong_weak_beat",
        "age_ui_profile": _age_profile(composition.get("difficulty", {}).get("grade_band", "")),
        "config": {
            "activity_id": activity_id,
            "runtime_component": "StrongWeakBeatActivity",
            "meter": meter,
            "bpm": bpm,
            "cycle_count": 2,
            "teacher_confirm_required": True,
            "show_beat_track": True,
            "body_action_set": movement_actions,
            "movement_actions": movement_actions,
            "record_export": "strong_weak_beat_circle_record_v1" if is_circle else "meter_body_movement_record_v1",
            "education_alignment": deepcopy(composition["education_alignment"]),
            "teacher_explanation": deepcopy(composition["teacher_explanation"]),
        },
        "student_task_copy": {
            "listen": "听什么：先听强拍和弱拍。",
            "do": "做什么：强拍用明显动作，弱拍用较小动作。",
            "pass": "怎样完成：能说出第 1 拍强，后面弱，并稳定做动作。",
        },
        "music_reason_prompts": {
            "strong": "强拍动作要更清楚，通常在每小节第 1 拍。",
            "weak": "弱拍动作要轻一点，但仍要落在稳定拍上。",
            "success": "强弱拍稳定：回到歌曲或律动片段中围圈表现。",
        },
        "result_transfer_prompt": "回到教材音乐片段，用围圈律动表现二拍子或三拍子的强弱规律。",
    }
    return {
        "runtime_builder_version": RUNTIME_BUILDER_VERSION,
        "student_game_state": state,
        "student_entry": "/template-console/strong-weak-beat-preview.html",
        "runtime_status": "ready",
    }


def _orff_ensemble_runtime(*, composition: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    available = request.get("available_materials") if isinstance(request.get("available_materials"), dict) else {}
    group_tasks = _group_tasks(available)
    rhythm_pattern = _pattern_steps(available)
    instrument_parts = _instrument_parts(available, len(group_tasks))
    meter = str(available.get("meter") or "2/4")
    bpm = int(available.get("bpm") or composition.get("difficulty", {}).get("bpm") or 88)
    activity_id = str(composition.get("selected_activity_id") or "orff_percussion_ensemble")
    is_band_roles = activity_id == "classroom_band_roles"
    assessment_criteria = _phrase_list(
        available.get("assessment_criteria") or available.get("rubric"),
        ["节奏稳定", "按时进入", "能听同伴"],
    )
    state = {
        "workflow": {
            "workflow_kind": "primary_activity_game",
            "composition_spec": _public_composition_summary(composition),
            "education_alignment": deepcopy(composition["education_alignment"]),
            "gameplay_blueprint": {
                "student_facing_name": "小乐队分声部" if is_band_roles else "奥尔夫打击乐合奏",
                "prompt": composition["teacher_explanation"]["why_this_game"],
                "operation_type": "classroom_band_roles" if is_band_roles else "orff_ensemble",
                "scene_goal": "按小组任务分配乐器声部，先听稳定拍和同伴，再按教师指挥进入。" if is_band_roles else "分组负责固定节奏声部，听稳定拍进入，完成可控合奏展示。",
                "game_genre": "guided_group_percussion_ensemble",
            },
        },
        "instance": {
            "template_label": "小乐队分声部" if is_band_roles else "奥尔夫打击乐合奏",
            "student_task": {
                "listen": "听什么：听稳定拍和其他声部。",
                "do": "做什么：按本组任务演奏虚拟打击乐声部。",
                "pass": "怎样完成：能按指挥进入、保持节奏，并与其他组配合。",
            },
        },
        "template_id": "primary_classroom_band_roles" if is_band_roles else "primary_orff_ensemble",
        "age_ui_profile": _age_profile(composition.get("difficulty", {}).get("grade_band", "")),
        "config": {
            "activity_id": activity_id,
            "runtime_component": "OrffEnsembleActivity",
            "group_tasks": group_tasks,
            "rhythm_pattern": rhythm_pattern,
            "instrument_parts": instrument_parts,
            "meter": meter,
            "bpm": bpm,
            "assessment_criteria": assessment_criteria,
            "entry_every_bars": 1,
            "entry_timing_rule": "ensemble_entry_rule",
            "entry_attempt_summary": "orff_entry_attempt_summary_v1",
            "session_record_export": "classroom_band_session_record_v1" if is_band_roles else "orff_ensemble_session_record_v1",
            "role_assignment_export": "classroom_band_role_assignment_v1" if is_band_roles else "",
            "recording_playback_enabled": True,
            "mute_solo_enabled": True,
            "teacher_confirm_required": True,
            "performance_record_export": "orff_group_performance_record_v1",
            "education_alignment": deepcopy(composition["education_alignment"]),
            "teacher_explanation": deepcopy(composition["teacher_explanation"]),
        },
        "student_task_copy": {
            "listen": "听什么：先听稳定拍，再听其他小组声部。",
            "do": "做什么：本组按固定节奏演奏虚拟打击乐。",
            "pass": "怎样完成：按时进入、保持节奏、能合上其他声部。",
        },
        "music_reason_prompts": {
            "entry": "等教师指挥和稳定拍，再进入。",
            "too_loud": "声音太突出：降低力度，听其他声部。",
            "success": "合奏稳定：说出本组什么时候进入、怎样听其他声部。",
        },
        "result_transfer_prompt": "用同样声部分工回到歌曲或律动片段中合奏展示。",
    }
    return {
        "runtime_builder_version": RUNTIME_BUILDER_VERSION,
        "student_game_state": state,
        "student_entry": "/template-console/orff-ensemble-preview.html",
        "runtime_status": "ready",
    }


def _body_percussion_runtime(*, composition: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    available = request.get("available_materials") if isinstance(request.get("available_materials"), dict) else {}
    rhythm_pattern = _pattern_steps(available)
    body_actions = _phrase_list(available.get("body_action_set") or available.get("body_actions"), ["拍手", "拍腿", "跺脚", "停住"])
    meter = str(available.get("meter") or "2/4")
    bpm = int(available.get("bpm") or composition.get("difficulty", {}).get("bpm") or 92)
    state = {
        "workflow": {
            "workflow_kind": "primary_activity_game",
            "composition_spec": _public_composition_summary(composition),
            "education_alignment": deepcopy(composition["education_alignment"]),
            "gameplay_blueprint": {
                "student_facing_name": "身体打击编排",
                "prompt": composition["teacher_explanation"]["why_this_game"],
                "operation_type": "body_percussion",
                "scene_goal": "用拍手、拍腿、跺脚和停住编排能落在节拍里的身体节奏。",
                "game_genre": "guided_body_percussion_builder",
            },
        },
        "instance": {
            "template_label": "身体打击编排",
            "student_task": {
                "listen": "听什么：先听稳定拍和目标节奏。",
                "do": "做什么：把身体动作放进每个拍点。",
                "pass": "怎样完成：动作顺序、总拍数和力度变化都能合上音乐。",
            },
        },
        "template_id": "primary_body_percussion",
        "age_ui_profile": _age_profile(composition.get("difficulty", {}).get("grade_band", "")),
        "config": {
            "activity_id": "body_percussion_builder",
            "runtime_component": "BodyPercussionActivity",
            "body_actions": body_actions,
            "rhythm_pattern": rhythm_pattern,
            "meter": meter,
            "bpm": bpm,
            "teacher_confirm_required": True,
            "show_beat_track": True,
            "education_alignment": deepcopy(composition["education_alignment"]),
            "teacher_explanation": deepcopy(composition["teacher_explanation"]),
        },
        "student_task_copy": {
            "listen": "听什么：先跟稳定拍。",
            "do": "做什么：用动作卡组合身体节奏。",
            "pass": "怎样完成：小节完整，休止时停住，动作力度有变化。",
        },
        "music_reason_prompts": {
            "bar_incomplete": "小节还没填满：检查每个动作是否落在拍点上。",
            "rest_needed": "有休止时动作要停住，停住也是音乐表现。",
            "success": "身体打击稳定：回到音乐中和小组一起表现。",
        },
        "result_transfer_prompt": "把编排好的身体打击放到歌曲伴奏或律动段落里展示。",
    }
    return {
        "runtime_builder_version": RUNTIME_BUILDER_VERSION,
        "student_game_state": state,
        "student_entry": "/template-console/body-percussion-preview.html",
        "runtime_status": "ready",
    }


def _graphic_score_runtime(*, composition: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    available = request.get("available_materials") if isinstance(request.get("available_materials"), dict) else {}
    meter = str(available.get("meter") or "2/4")
    total_beats = _bounded_int(available.get("total_beats") or available.get("totalBeats"), 2, 8, 4)
    bpm = int(available.get("bpm") or composition.get("difficulty", {}).get("bpm") or 88)
    state = {
        "workflow": {
            "workflow_kind": "primary_activity_game",
            "composition_spec": _public_composition_summary(composition),
            "education_alignment": deepcopy(composition["education_alignment"]),
            "gameplay_blueprint": {
                "student_facing_name": "图形谱创编",
                "prompt": composition["teacher_explanation"]["why_this_game"],
                "operation_type": "graphic_score_create",
                "scene_goal": "用点、线、块表达高低、长短、强弱和播放顺序，回放后说明图形含义。",
                "game_genre": "guided_graphic_score_creation",
            },
        },
        "instance": {
            "template_label": "图形谱创编",
            "student_task": {
                "listen": "听什么：播放自己排好的图形谱，听高低、长短和强弱是否清楚。",
                "do": "做什么：把点、线、块按顺序放进拍点。",
                "pass": "怎样完成：放满顺序、回放试听，并说明图形表示的音乐要素。",
            },
        },
        "template_id": "primary_graphic_score",
        "age_ui_profile": _age_profile(composition.get("difficulty", {}).get("grade_band", "")),
        "config": {
            "activity_id": "graphic_score_create",
            "runtime_component": "GraphicScoreActivity",
            "meter": meter,
            "total_beats": total_beats,
            "bpm": bpm,
            "symbol_meanings": _graphic_symbol_meanings(available),
            "required_elements": ["pitch", "duration", "dynamics"],
            "record_export": "graphic_score_record_v1",
            "summary_export": "graphic_score_summary_v1",
            "teacher_confirm_required": True,
            "education_alignment": deepcopy(composition["education_alignment"]),
            "teacher_explanation": deepcopy(composition["teacher_explanation"]),
        },
        "student_task_copy": {
            "listen": "听什么：先播放图形谱。",
            "do": "做什么：用图形表示高低、长短和强弱。",
            "pass": "怎样完成：能解释每个图形的音乐含义。",
        },
        "music_reason_prompts": {
            "incomplete": "图形谱还没放满，请按顺序补齐。",
            "needs_playback": "先播放听一遍，再决定是否修改。",
            "success": "图形谱创编完成：请说明哪些图形表示高低、长短和强弱。",
        },
        "result_transfer_prompt": "把图形谱播放后，用声音、身体动作或小乐器表现一次。",
    }
    return {
        "runtime_builder_version": RUNTIME_BUILDER_VERSION,
        "student_game_state": state,
        "student_entry": "/template-console/graphic-score-preview.html",
        "runtime_status": "ready",
    }


def _instrument_family_runtime(*, composition: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    available = request.get("available_materials") if isinstance(request.get("available_materials"), dict) else {}
    instrument_pool = _instrument_pool(available)
    family_set = _phrase_list(
        available.get("instrument_family_set")
        or available.get("instrument_families")
        or available.get("family_targets")
        or available.get("families"),
        ["吹奏", "拉弦", "弹拨", "打击"],
    )
    audio_clip = str(available.get("audio_clip") or available.get("audio_url") or available.get("source_audio_url") or "")
    instrument_audio_pack = get_instrument_audio_pack("primary_playable_instrument_sample_pack")
    instrument_card_pack_id = "generated_playable_instrument_pack"
    instrument_card_assets, pending_instrument_card_assets = _instrument_card_assets(
        instrument_pool,
        pack_id=instrument_card_pack_id,
    )
    state = {
        "workflow": {
            "workflow_kind": "primary_activity_game",
            "composition_spec": _public_composition_summary(composition),
            "education_alignment": deepcopy(composition["education_alignment"]),
            "gameplay_blueprint": {
                "student_facing_name": "乐器家族分类",
                "prompt": composition["teacher_explanation"]["why_this_game"],
                "operation_type": "instrument_family_sorting",
                "scene_goal": "先听音色，再按发声方式或乐器家族归类，并说出听到的依据。",
                "game_genre": "guided_instrument_family_sort",
            },
        },
        "instance": {
            "template_label": "乐器家族分类",
            "student_task": {
                "listen": "听什么：先听乐器声音，抓住发声方式和音色特点。",
                "do": "做什么：把乐器卡放入对应家族。",
                "pass": "怎样完成：分类正确，并能说出音色或发声方式依据。",
            },
        },
        "template_id": "primary_instrument_family_sorting",
        "age_ui_profile": _age_profile(composition.get("difficulty", {}).get("grade_band", "")),
        "config": {
            "activity_id": "instrument_family_sorting",
            "runtime_component": "InstrumentFamilySortingActivity",
            "audio_clip": audio_clip,
            "instrument_pool": instrument_pool,
            "family_set": family_set,
            "instrument_audio_pack": instrument_audio_pack["audio_pack_id"],
            "instrument_audio_items": [
                item
                for item in instrument_audio_pack.get("items", [])
                if str(item.get("label") or "") in instrument_pool or str(item.get("instrument_id") or "") in {card.get("id") for card in [*instrument_card_assets, *pending_instrument_card_assets]}
            ],
            "instrument_card_pack": instrument_card_pack_id,
            "instrument_card_assets": instrument_card_assets,
            "pending_instrument_card_assets": pending_instrument_card_assets,
            "audio_source_contract": {
                "registry_ref": "instrument_audio_registry.primary_playable_instrument_sample_pack",
                "sample_status": instrument_audio_pack.get("sample_status", ""),
                "allowed_source_kinds": ["open_sample"],
                "fallback_must_be_labeled": False,
            },
            "listen_before_classify_required": True,
            "generated_images_may_claim_real_instrument_photo": False,
            "visual_source_policy": "generated_playable_skin_only_no_web_photos",
            "teacher_reason_required": True,
            "hide_picture_supported": True,
            "education_alignment": deepcopy(composition["education_alignment"]),
            "teacher_explanation": deepcopy(composition["teacher_explanation"]),
        },
        "student_task_copy": {
            "listen": "听什么：先听采样声音，不先猜图片。",
            "do": "做什么：按吹奏、拉弦、弹拨、打击等家族分类。",
            "pass": "怎样完成：能说出发声方式或音色依据。",
        },
        "music_reason_prompts": {
            "listen_first": "先听采样声音，再看生成乐器皮肤验证。",
            "weak_evidence": "请补一个音色或发声方式依据。",
            "success": "分类成立：把这个乐器放回作品片段里复听。",
        },
        "result_transfer_prompt": "回到欣赏作品，听一听这个家族的乐器在哪里出现。",
    }
    return {
        "runtime_builder_version": RUNTIME_BUILDER_VERSION,
        "student_game_state": state,
        "student_entry": "/template-console/instrument-family-preview.html",
        "runtime_status": "ready",
    }


def _group_relay_runtime(*, composition: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    available = request.get("available_materials") if isinstance(request.get("available_materials"), dict) else {}
    group_tasks = _group_tasks(available)
    criteria = _phrase_list(available.get("assessment_criteria") or available.get("rubric"), ["节奏稳定", "能倾听同伴", "大胆表现"])
    state = {
        "workflow": {
            "workflow_kind": "primary_activity_game",
            "composition_spec": _public_composition_summary(composition),
            "education_alignment": deepcopy(composition["education_alignment"]),
            "gameplay_blueprint": {
                "student_facing_name": "小组接力展示",
                "prompt": composition["teacher_explanation"]["why_this_game"],
                "operation_type": "group_relay",
                "scene_goal": "小组轮流完成唱、奏、动或节奏任务，并用音乐依据进行评价。",
                "game_genre": "guided_group_relay_performance",
            },
        },
        "instance": {
            "template_label": "小组接力展示",
            "student_task": {
                "listen": "听什么：听前一组的节奏、声音或动作。",
                "do": "做什么：本组接上任务并完成展示。",
                "pass": "怎样完成：按轮次进入，表现稳定，并能给出同伴评价。",
            },
        },
        "template_id": "primary_group_relay",
        "age_ui_profile": _age_profile(composition.get("difficulty", {}).get("grade_band", "")),
        "config": {
            "activity_id": "group_relay_performance",
            "runtime_component": "GroupRelayActivity",
            "group_tasks": group_tasks,
            "assessment_criteria": criteria,
            "teacher_confirm_required": True,
            "group_rotation_enabled": True,
            "education_alignment": deepcopy(composition["education_alignment"]),
            "teacher_explanation": deepcopy(composition["teacher_explanation"]),
        },
        "student_task_copy": {
            "listen": "听什么：听上一组表现。",
            "do": "做什么：本组接力完成音乐任务。",
            "pass": "怎样完成：稳定表现，并按评价维度说一句依据。",
        },
        "music_reason_prompts": {
            "wait_turn": "先听同伴，等轮到本组再进入。",
            "too_generic": "评价要说音乐依据，例如节奏稳、声音自然或动作合拍。",
            "success": "接力完成：把各组表现连起来展示一次。",
        },
        "result_transfer_prompt": "把小组接力结果用于全班展示或教师课后观察记录。",
    }
    return {
        "runtime_builder_version": RUNTIME_BUILDER_VERSION,
        "student_game_state": state,
        "student_entry": "/template-console/group-relay-preview.html",
        "runtime_status": "ready",
    }


def _peer_feedback_runtime(*, composition: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    available = request.get("available_materials") if isinstance(request.get("available_materials"), dict) else {}
    group_tasks = _group_tasks(available)
    criteria = _phrase_list(available.get("assessment_criteria") or available.get("rubric"), ["节奏稳定", "进入整齐", "能听同伴"])
    evidence_terms = _phrase_list(
        available.get("evidence_terms")
        or available.get("music_evidence_terms")
        or available.get("assessment_criteria")
        or available.get("rubric"),
        criteria,
    )
    focus = str(available.get("music_focus") or available.get("focus") or available.get("objective") or "小组音乐展示")
    state = {
        "workflow": {
            "workflow_kind": "primary_activity_game",
            "composition_spec": _public_composition_summary(composition),
            "education_alignment": deepcopy(composition["education_alignment"]),
            "gameplay_blueprint": {
                "student_facing_name": "展示与同伴评价",
                "prompt": composition["teacher_explanation"]["why_this_game"],
                "operation_type": "show_and_peer_feedback",
                "scene_goal": "小组展示后，同伴先听表现，再用音乐依据给出具体建议。",
                "game_genre": "guided_peer_feedback_showcase",
            },
        },
        "instance": {
            "template_label": "展示与同伴评价",
            "student_task": {
                "listen": "听什么：先听或观看同伴展示的节奏、声音、进入和合作。",
                "do": "做什么：选择一个音乐依据，并写一句具体建议。",
                "pass": "怎样完成：建议必须指向节奏、进入、力度、声音或合作倾听。",
            },
        },
        "template_id": "primary_peer_feedback",
        "age_ui_profile": _age_profile(composition.get("difficulty", {}).get("grade_band", "")),
        "config": {
            "activity_id": "show_and_peer_feedback",
            "runtime_component": "PeerFeedbackActivity",
            "group_tasks": group_tasks,
            "assessment_criteria": criteria,
            "evidence_terms": evidence_terms,
            "music_focus": focus,
            "teacher_confirm_required": True,
            "peer_feedback_required": True,
            "record_export": "peer_feedback_record_v1",
            "summary_export": "peer_feedback_summary_v1",
            "education_alignment": deepcopy(composition["education_alignment"]),
            "teacher_explanation": deepcopy(composition["teacher_explanation"]),
        },
        "student_task_copy": {
            "listen": "听什么：先听同伴展示，不马上打分。",
            "do": "做什么：选音乐依据，写一句可改进建议。",
            "pass": "怎样完成：每组至少收到一条具体音乐建议。",
        },
        "music_reason_prompts": {
            "listen_first": "先听完整展示，再开始评价。",
            "too_generic": "不要只说好听或喜欢，请说节奏、进入、力度、声音或合作倾听。",
            "success": "同伴评价完成：教师可汇总全班最常见的优点和下一步练习点。",
        },
        "result_transfer_prompt": "把同伴建议带回下一次展示，选择一个音乐点修改后再演一次。",
    }
    return {
        "runtime_builder_version": RUNTIME_BUILDER_VERSION,
        "student_game_state": state,
        "student_entry": "/template-console/peer-feedback-preview.html",
        "runtime_status": "ready",
    }


def _exit_ticket_runtime(*, composition: dict[str, Any], request: dict[str, Any]) -> dict[str, Any]:
    available = request.get("available_materials") if isinstance(request.get("available_materials"), dict) else {}
    criteria = _phrase_list(available.get("assessment_criteria") or available.get("rubric"), ["能说出本课音乐要素", "能给出听到或表现到的依据"])
    focus = str(available.get("music_focus") or available.get("focus") or available.get("objective") or "本课音乐要素")
    state = {
        "workflow": {
            "workflow_kind": "primary_activity_game",
            "composition_spec": _public_composition_summary(composition),
            "education_alignment": deepcopy(composition["education_alignment"]),
            "gameplay_blueprint": {
                "student_facing_name": "课堂出口票",
                "prompt": composition["teacher_explanation"]["why_this_game"],
                "operation_type": "exit_ticket",
                "scene_goal": "用选择和一句话依据回顾本课音乐目标，帮助教师判断是否需要复习。",
                "game_genre": "music_evidence_exit_ticket",
            },
        },
        "instance": {
            "template_label": "课堂出口票",
            "student_task": {
                "listen": "想什么：回忆本课听到、唱到或演奏到的音乐要素。",
                "do": "做什么：选择一个依据词，并说一句理由。",
                "pass": "怎样完成：理由必须指向本课音乐目标，而不是泛泛说喜欢。",
            },
        },
        "template_id": "primary_exit_ticket",
        "age_ui_profile": _age_profile(composition.get("difficulty", {}).get("grade_band", "")),
        "config": {
            "activity_id": "exit_ticket_review",
            "runtime_component": "ExitTicketActivity",
            "music_focus": focus,
            "assessment_criteria": criteria,
            "teacher_export_enabled": True,
            "teacher_confirm_required": True,
            "education_alignment": deepcopy(composition["education_alignment"]),
            "teacher_explanation": deepcopy(composition["teacher_explanation"]),
        },
        "student_task_copy": {
            "listen": "想什么：本课学到哪个音乐要素。",
            "do": "做什么：选一个依据词，说一句理由。",
            "pass": "怎样完成：理由具体，能回到音乐。",
        },
        "music_reason_prompts": {
            "too_generic": "不要只说好听，请说速度、力度、音色、节奏、曲式等音乐依据。",
            "success": "依据清楚：教师可据此决定下一节是否复习。",
        },
        "result_transfer_prompt": "把出口票结果作为下节课复习或小组展示的依据。",
    }
    return {
        "runtime_builder_version": RUNTIME_BUILDER_VERSION,
        "student_game_state": state,
        "student_entry": "/template-console/exit-ticket-preview.html",
        "runtime_status": "ready",
    }


def _template_payload(template_id: str, composition: dict[str, Any], available: dict[str, Any]) -> dict[str, Any]:
    difficulty = composition.get("difficulty", {})
    payload: dict[str, Any] = {
        "template_id": template_id,
        "difficulty": "L1" if _is_lower_primary(difficulty.get("grade_band", "")) else "L2",
        "bpm": difficulty.get("bpm") or available.get("bpm") or 92,
        "round_count": difficulty.get("round_count") or 3,
    }
    if template_id == "beat_guardian_core":
        payload.update(
            {
                "meter": available.get("meter") or "2/4",
                "target_beats": [1],
                "mode": "strong_beat_guard",
                "skin_id": "castle_gate",
                "show_strong_beat_hint": bool(difficulty.get("show_hint", True)),
            }
        )
    if template_id == "rhythm_echo_core":
        payload.update(
            {
                "pattern_steps": _pattern_steps(available),
                "bars_per_round": 2,
                "skin_id": "rhythm_radio",
            }
        )
    if template_id == "timbre_detective_core":
        payload.update(
            {
                "mode": "compare_twins" if len(_instrument_pool(available)) <= 3 else "instrument_clue",
                "instrument_pool": _instrument_pool(available),
                "timbre_traits": _timbre_traits(available),
                "choices_per_round": min(4, max(2, len(_instrument_pool(available)))),
                "evidence_required": 2 if "compare" in str(available.get("mode") or "") else 1,
                "sound_set": str(available.get("sound_set") or "classroom_instruments"),
                "skin_id": "sound_casebook",
            }
        )
    if template_id == "form_treasure_core":
        form_type = _form_type(available)
        payload.update(
            {
                "form_type": form_type,
                "mode": _form_mode(form_type),
                "section_length_bars": available.get("section_length_bars") or available.get("bars_per_section") or 8,
                "hint_mode": "partial",
                "allow_relisten": True,
                "skin_id": "treasure_map" if form_type == "ABA" else "constellation_path",
            }
        )
    if template_id == "composition_puzzle_core":
        payload.update(
            {
                "mode": "melody_rhythm_puzzle",
                "meter": str(available.get("meter") or "2/4"),
                "scale_type": "major_pentatonic",
                "melody_cards": _solfege_cards(available),
                "rhythm_cards": _pattern_steps(available),
                "composition_total_bars": available.get("composition_total_bars") or available.get("phrase_length_bars") or 2,
                "composition_segment_bars": available.get("composition_segment_bars") or 2,
                "constraint_profile": "guided",
                "teacher_confirm_required": True,
                "skin_id": "composition_studio",
            }
        )
    if template_id == "pitch_ladder_core":
        payload.update(
            {
                "mode": "high_low_steps",
                "pitch_range": _solfege_cards(available),
                "target_pattern_type": "direction_pair",
                "round_count": 4,
                "skin_id": "mountain_path",
            }
        )
    if template_id == "solfege_target_core":
        payload.update(
            {
                "mode": "listen_choose_solfege",
                "pitch_range": _solfege_cards(available),
                "target_solfege": _solfege_cards(available),
                "round_count": 4,
                "skin_id": "note_targets",
            }
        )
    return payload


def _apply_music_runtime_overrides(
    config: dict[str, Any],
    template_id: str,
    composition: dict[str, Any],
    available: dict[str, Any],
) -> None:
    config["primary_activity_id"] = composition["selected_activity_id"]
    config["education_alignment"] = deepcopy(composition["education_alignment"])
    config["teacher_explanation"] = deepcopy(composition["teacher_explanation"])
    config["music_concept"] = "、".join(composition["education_alignment"].get("music_elements", []))
    config["bpm"] = int(available.get("bpm") or config.get("bpm") or 92)
    if template_id == "beat_guardian_core":
        config["meter"] = str(available.get("meter") or config.get("meter") or "2/4")
        config["target_beats"] = [1]
        config["student_task_copy"] = {
            "listen": "听什么：听清稳定拍和每小节第 1 拍。",
            "do": "做什么：在强拍上点击或敲虚拟小鼓。",
            "pass": "怎样过关：能稳定预判强拍，不抢拍不拖拍。",
        }
        config["music_reason_prompts"] = {
            "early": "抢拍了：先跟着身体点头，再等强拍。",
            "late": "稍晚：提前听小节循环。",
            "success": "强拍稳定：说出你怎样听到第 1 拍。",
        }
        config["result_transfer_prompt"] = "回到歌曲中，用身体律动表现二拍子强弱。"
    if template_id == "rhythm_echo_core":
        config["pattern_steps"] = _pattern_steps(available)
        config["student_task_copy"] = {
            "listen": "听什么：先完整听一遍目标节奏。",
            "do": "做什么：用点击、拍手或身体动作拍回来。",
            "pass": "怎样过关：节奏顺序、拍点和休止都稳定。",
        }
        config["music_reason_prompts"] = {
            "success": "节奏复刻成功：说出长短和休止位置。",
            "wrong_order": "顺序错了：再听长短和休止的位置。",
        }
        config["result_transfer_prompt"] = "用口读或身体律动再表现一次节奏型。"
    if template_id == "timbre_detective_core":
        config["audio_clip"] = str(available.get("audio_clip") or available.get("audio_url") or available.get("source_audio_url") or "")
        config["instrument_pool"] = _instrument_pool(available)
        config["timbre_traits"] = _timbre_traits(available)
        config["music_concept"] = "听辨乐器音色，并用音色证据说明判断。"
        config["comparison_reason_required"] = True
        config["student_task_copy"] = {
            "listen": "听什么：先听声音证物，抓住音色特点。",
            "do": "做什么：选择乐器或家族，再选择音色证据词。",
            "pass": "怎样过关：判断对象和音色证据都成立，并能口头说明理由。",
        }
        config["music_reason_prompts"] = {
            "success": "证据成立：用音色词解释为什么是这个乐器。",
            "wrong_instrument": "先不要看图片，复听声音的发声方式和音色质感。",
            "weak_evidence": "证据不足：换一个更能说明音色的词。",
        }
        config["result_transfer_prompt"] = "回到作品片段中复听，说出这个乐器的音色证据。"
    if template_id == "form_treasure_core":
        config["audio_clip"] = str(available.get("audio_clip") or available.get("audio_url") or available.get("source_audio_url") or "")
        config["music_concept"] = "听辨段落重复、对比与再现，排列曲式路线。"
        config["allow_relisten"] = True
        config["student_task_copy"] = {
            "listen": "听什么：先听每个段落，判断主题是否重复、对比或再现。",
            "do": "做什么：把 A、B、C 等结构卡放到正确段落路线上。",
            "pass": "怎样过关：曲式路线正确，并能说出重复、对比或再现依据。",
        }
        config["music_reason_prompts"] = {
            "success": "曲式路线点亮：说出重复、对比或再现依据。",
            "wrong_order": "路线还不对：复听每段开头，比较主题是否相同。",
            "need_relisten": "先复听段落，再移动结构卡。",
        }
        config["result_transfer_prompt"] = "回到作品中复听完整段落，用语言说出 ABA、回旋或重复对比依据。"
    if template_id == "composition_puzzle_core":
        config["meter"] = str(available.get("meter") or config.get("meter") or "2/4")
        config["scale_type"] = "major_pentatonic"
        config["melody_cards"] = _solfege_cards(available)
        config["rhythm_cards"] = _pattern_steps(available)
        config["music_concept"] = "只用五声音级和节奏素材创编短句，试听后修改。"
        config["teacher_confirm_required"] = True
        config["virtual_instrument"] = "virtual_xylophone"
        config["student_task_copy"] = {
            "listen": "听什么：回放自己拼出的短句，听它是否完整、稳定、有五声风格。",
            "do": "做什么：用 do、re、mi、sol、la 和节奏卡拼出两小节短句。",
            "pass": "怎样过关：规则检查通过后，试听并修改，再请教师确认创编理由。",
        }
        config["music_reason_prompts"] = {
            "constraint_missing": "还差一个约束：只使用五声音级，并把小节填完整。",
            "bar_incomplete": "小节还没有填满：补足节奏时值后再试听。",
            "melody_static": "旋律变化还不够：尝试上行、下行或稳定结束音。",
            "success": "创编完成：回放作品，并说出你用了哪些五声音级和节奏办法。",
        }
        config["result_transfer_prompt"] = "把创编短句用虚拟音条琴播放，再唱一遍或请小组接龙改编。"
    if template_id == "pitch_ladder_core":
        config["pitch_range"] = _solfege_cards(available)
        config["music_concept"] = "先听音高走向，再用 do/re/mi/sol/la 唱名表达高低、级进或跳进。"
        config["sing_back_required"] = True
        config["student_task_copy"] = {
            "listen": "听什么：先听两个音或短句的高低方向。",
            "do": "做什么：选择上行、下行或保持，再唱回唱名。",
            "pass": "怎样过关：方向判断正确，并能用 do/re/mi 等唱名模唱。",
        }
        config["music_reason_prompts"] = {
            "success": "音高路线正确：唱出这组 do/re/mi 的走向。",
            "wrong_direction": "再听一次，比较后一个音比前一个音高还是低。",
            "teacher_confirm": "唱回环节由教师确认，不自动评分儿童声音。",
        }
        config["result_transfer_prompt"] = "把听到的音高走向画成旋律线，再唱回短句。"
    if template_id == "solfege_target_core":
        config["pitch_range"] = _solfege_cards(available)
        config["target_solfege"] = _solfege_cards(available)
        config["music_concept"] = "听辨唱名并模唱，建立音级与声音高低的联系。"
        config["teacher_confirm_required"] = True
        config["student_task_copy"] = {
            "listen": "听什么：听目标音或短句。",
            "do": "做什么：点选对应唱名，再跟唱。",
            "pass": "怎样过关：唱名选择正确，教师确认模唱稳定。",
        }
        config["music_reason_prompts"] = {
            "success": "唱名匹配：用自然声音再唱一遍。",
            "wrong_solfege": "先听高低位置，再看 do/re/mi 的顺序。",
            "teacher_confirm": "唱回环节由教师确认。",
        }
        config["result_transfer_prompt"] = "把选中的唱名放回歌曲或旋律短句中唱一唱。"


def _pattern_steps(available: dict[str, Any]) -> list[str]:
    value = available.get("rhythm_pattern") or available.get("pattern_steps")
    if isinstance(value, list) and value:
        return [str(item) for item in value]
    return ["quarter", "eighth_pair", "rest", "quarter"]


def _solfege_cards(available: dict[str, Any]) -> list[str]:
    value = available.get("solfege_set") or available.get("melody_cards") or available.get("pitch_range")
    items = _phrase_list(value, ["do", "re", "mi", "sol", "la"])
    allowed = {"do", "re", "mi", "sol", "la"}
    normalized = [item.strip().lower() for item in items]
    filtered = [item for item in normalized if item in allowed]
    return _dedupe(filtered) or ["do", "re", "mi", "sol", "la"]


def _echo_phrases(available: dict[str, Any], solfege_set: list[str]) -> list[list[str]]:
    value = available.get("echo_phrases") or available.get("pitch_motion") or available.get("target_solfege")
    source = value if isinstance(value, list) and value else [solfege_set[:3], solfege_set[2:5]]
    phrases: list[list[str]] = []
    allowed = set(solfege_set)
    for item in source:
        if isinstance(item, list):
            tokens = [str(token).strip().lower() for token in item]
        else:
            text = str(item or "").strip().lower()
            for separator in ["-", "，", "、", "/", ","]:
                text = text.replace(separator, " ")
            tokens = [token.strip() for token in text.split() if token.strip()]
        phrase = [token for token in tokens if token in allowed]
        if len(phrase) >= 2:
            phrases.append(phrase[:5])
    return phrases[:6] or [solfege_set[:3], solfege_set[-3:]]


def _numbered_score_lines(available: dict[str, Any]) -> list[str]:
    value = available.get("numbered_score") or available.get("simple_score") or available.get("score_lines")
    lines = _phrase_list(value, ["1 2 3", "3 5 6"])
    return [line.strip() for line in lines if line.strip()][:6] or ["1 2 3"]


def _score_line_to_solfege(line: str) -> list[str]:
    mapping = {"1": "do", "2": "re", "3": "mi", "4": "fa", "5": "sol", "6": "la", "7": "ti"}
    cleaned = str(line or "")
    for separator in ["-", "，", "、", "/", "|"]:
        cleaned = cleaned.replace(separator, " ")
    return [mapping[token] for token in cleaned.split() if token in mapping]


def _group_tasks(available: dict[str, Any]) -> list[str]:
    value = (
        available.get("classroom_group_task")
        or available.get("group_tasks")
        or available.get("part_assignments")
        or available.get("ensemble_parts")
    )
    if isinstance(value, list) and value:
        return [str(item).strip() for item in value if str(item).strip()]
    try:
        count = int(available.get("group_count") or 4)
    except (TypeError, ValueError):
        count = 4
    defaults = ["A组手鼓强拍", "B组木鱼稳定拍", "C组沙锤弱拍", "D组三角铁点缀"]
    return defaults[: max(1, min(count, len(defaults)))]


def _instrument_parts(available: dict[str, Any], count: int) -> list[str]:
    provided = _phrase_list(available.get("instrument_parts") or available.get("role_instruments"), [])
    if provided:
        return provided[: max(1, min(len(provided), count or len(provided)))]
    parts = ["hand_drum", "woodblock", "shaker", "triangle"]
    return parts[: max(1, min(count, len(parts)))]


def _theme_return_windows(available: dict[str, Any]) -> list[dict[str, Any]]:
    value = (
        available.get("theme_windows")
        or available.get("theme_return_windows")
        or available.get("theme_time_windows")
        or available.get("return_windows")
    )
    source = value if isinstance(value, list) and value else [
        {"startSec": 8, "endSec": 14, "label": "第一次出现"},
        {"startSec": 32, "endSec": 40, "label": "主题再现"},
    ]
    windows: list[dict[str, Any]] = []
    for index, item in enumerate(source[:6]):
        raw = item if isinstance(item, dict) else {}
        start = _bounded_int(raw.get("startSec") or raw.get("start_sec") or raw.get("start") or index * 16, 0, 600, index * 16)
        end = _bounded_int(raw.get("endSec") or raw.get("end_sec") or raw.get("end") or start + 6, start + 1, 600, start + 6)
        windows.append({
            "startSec": start,
            "endSec": end,
            "label": str(raw.get("label") or raw.get("name") or f"主题第 {index + 1} 次出现").strip(),
        })
    return windows


def _graphic_symbol_meanings(available: dict[str, Any]) -> list[dict[str, str]]:
    value = (
        available.get("graphic_symbol_meanings")
        or available.get("symbol_meanings")
        or available.get("graphic_symbols")
        or available.get("shape_meanings")
    )
    source = value if isinstance(value, list) and value else [
        {"symbol": "dot", "label": "点", "pitch": "high", "duration": "short", "dynamics": "soft"},
        {"symbol": "line", "label": "线", "pitch": "middle", "duration": "long", "dynamics": "medium"},
        {"symbol": "block", "label": "块", "pitch": "low", "duration": "long", "dynamics": "strong"},
    ]
    meanings: list[dict[str, str]] = []
    defaults = ["dot", "line", "block"]
    labels = ["点", "线", "块"]
    for index, item in enumerate(source[:6]):
        raw = item if isinstance(item, dict) else {}
        meanings.append({
            "symbol": str(raw.get("symbol") or defaults[index % len(defaults)]).strip(),
            "label": str(raw.get("label") or labels[index % len(labels)]).strip(),
            "pitch": _allowed_value(raw.get("pitch"), {"high", "middle", "low"}, "middle"),
            "duration": _allowed_value(raw.get("duration"), {"short", "long"}, "long"),
            "dynamics": _allowed_value(raw.get("dynamics"), {"soft", "medium", "strong"}, "medium"),
        })
    return meanings


def _required_listening_evidence_dimensions(evidence_terms: list[str]) -> list[str]:
    dimensions = ["速度", "力度", "旋律", "音色"]
    selected = [dimension for dimension in dimensions if any(dimension in str(term) for term in evidence_terms)]
    for dimension in dimensions:
        if dimension not in selected:
            selected.append(dimension)
    return selected


def _mood_card_assets(expression_traits: list[str], *, pack_id: str = "mood_symbol_card_pack") -> list[dict[str, str]]:
    mapping = {
        "欢快": ("cheerful", "欢快情绪符号图卡"),
        "优美": ("beautiful", "优美情绪符号图卡"),
        "活泼": ("lively", "活泼情绪符号图卡"),
        "安静": ("quiet", "安静情绪符号图卡"),
        "庄严": ("solemn", "庄严情绪符号图卡"),
        "神秘": ("mysterious", "神秘情绪符号图卡"),
    }
    cards: list[dict[str, str]] = []
    seen: set[str] = set()
    for trait in expression_traits:
        asset_id, label = mapping.get(str(trait), ("cheerful", f"{trait}情绪符号图卡"))
        if asset_id in seen:
            continue
        seen.add(asset_id)
        extension = "png" if pack_id == "music_mood_picture_pack" else "svg"
        source = "primary_asset_pack_generated_picture" if pack_id == "music_mood_picture_pack" else "project_generated_svg_fallback"
        cards.append(
            {
                "id": asset_id,
                "trait": str(trait),
                "src": f"/static/assets/primary-asset-packs/{pack_id}/images/{asset_id}.{extension}",
                "alt": label,
                "source": source,
            }
        )
    return cards


def _instrument_card_assets(instrument_pool: list[str], *, pack_id: str = "generated_playable_instrument_pack") -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    pack = get_asset_pack(pack_id)
    assets_by_id = {str(asset.get("id") or ""): asset for asset in pack.get("assets", [])}
    cards: list[dict[str, str]] = []
    pending: list[dict[str, str]] = []
    seen: set[str] = set()
    for label in instrument_pool:
        asset_id = _instrument_asset_id(str(label))
        if not asset_id or asset_id in seen:
            continue
        asset = assets_by_id.get(asset_id)
        if not asset:
            pending.append(
                {
                    "id": asset_id or _slug(str(label)),
                    "label": str(label),
                    "source_pack": pack_id,
                    "visual_authenticity": "pending_generated_skin",
                    "asset_status": "missing_manifest_asset",
                }
            )
            continue
        seen.add(asset_id)
        src = f"/static/assets/primary-asset-packs/{pack_id}/{asset['file']}"
        local_path = resolve_static_asset_url(src)
        if not local_path.exists():
            pending.append(
                {
                    "id": asset_id,
                    "label": str(label),
                    "src": src,
                    "alt": str(asset.get("accessibility_label") or f"{label}生成乐器皮肤"),
                    "source_pack": pack_id,
                    "visual_authenticity": "pending_generated_skin",
                    "asset_status": "missing_file",
                }
            )
            continue
        cards.append(
            {
                "id": asset_id,
                "label": str(label),
                "src": src,
                "alt": str(asset.get("accessibility_label") or f"{label}生成乐器皮肤"),
                "source_pack": pack_id,
                "visual_authenticity": str(asset.get("visual_authenticity") or ""),
                "license": str(asset.get("license") or pack.get("license") or ""),
                "attribution": str(asset.get("attribution") or ""),
                "source_url": str(asset.get("source_url") or ""),
                "music_element": str(asset.get("music_element") or ""),
                "student_action": str(asset.get("student_action") or ""),
            }
        )
    return cards, pending


def _instrument_asset_id(label: str) -> str:
    name = label.lower()
    mapping = [
        (("节奏垫", "rhythm_pad", "pad"), "rhythm_pad"),
        (("竖笛", "recorder"), "recorder_fingering_board"),
        (("长笛", "flute"), "flute_playable_board"),
        (("笛子", "dizi"), "dizi_playable_board"),
        (("二胡", "erhu"), "erhu_generated_pending"),
        (("琵琶", "pipa"), "pipa_generated_pending"),
        (("小鼓", "手鼓", "hand_drum", "drum"), "virtual_hand_drum"),
        (("木鱼", "响板", "woodblock", "claves"), "woodblock_claves"),
        (("沙锤", "shaker", "maraca"), "shaker"),
        (("三角铁", "碰铃", "triangle"), "triangle_bell"),
        (("铃鼓", "tambourine"), "tambourine"),
        (("音条琴", "木琴", "xylophone"), "virtual_xylophone"),
        (("钢琴", "键盘", "keyboard", "piano"), "simple_keyboard"),
        (("五声", "pentatonic"), "pentatonic_grid"),
        (("奥尔夫", "打击乐套装", "percussion_kit"), "ensemble_controller"),
        (("口风琴", "melodica"), "melodica_keyboard_board"),
    ]
    for keywords, asset_id in mapping:
        if any(keyword.lower() in name for keyword in keywords):
            return asset_id
    return ""


def _slug(value: str) -> str:
    return value.strip().lower().replace(" ", "_") or "unknown_instrument"


def _instrument_pool(available: dict[str, Any]) -> list[str]:
    value = available.get("instrument_pool") or available.get("instruments") or available.get("instrument_cards")
    items = _phrase_list(value, ["笛子", "二胡", "钢琴", "小鼓"])
    return _dedupe(items)[:6]


def _timbre_traits(available: dict[str, Any]) -> list[str]:
    value = available.get("timbre_set") or available.get("timbre_traits") or available.get("evidence_terms")
    items = _phrase_list(value, ["明亮", "柔和", "短促", "持续", "气息感", "弦鸣", "敲击感"])
    return _dedupe(items)[:8]


def _form_type(available: dict[str, Any]) -> str:
    raw = str(available.get("form_structure") or available.get("form_type") or available.get("structure") or "ABA").strip()
    upper = raw.upper().replace("-", "")
    if "回旋" in raw or "RONDO" in upper:
        return "回旋"
    if "重复对比" in raw or "REPEAT" in upper:
        return "重复对比"
    if "ABA" in upper:
        return "ABA"
    return raw or "ABA"


def _form_mode(form_type: str) -> str:
    if form_type == "回旋":
        return "rondo_treasure"
    if form_type == "重复对比":
        return "repeat_contrast"
    return "aba_treasure"


def _meter_value(value: Any) -> str:
    text = str(value or "").strip()
    if text in {"2/4", "3/4", "4/4"}:
        return text
    if "三" in text or "3" in text:
        return "3/4"
    if "四" in text or "4" in text:
        return "4/4"
    return "2/4"


def _bounded_int(value: Any, minimum: int, maximum: int, fallback: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return fallback
    return max(minimum, min(maximum, parsed))


def _allowed_value(value: Any, allowed: set[str], fallback: str) -> str:
    text = str(value or "").strip()
    return text if text in allowed else fallback


def _dedupe(items: list[str]) -> list[str]:
    result: list[str] = []
    for item in items:
        normalized = str(item).strip()
        if normalized and normalized not in result:
            result.append(normalized)
    return result


def _phrase_list(value: Any, fallback: list[str]) -> list[str]:
    if isinstance(value, list) and value:
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        parts = [part.strip() for part in value.replace("。", "\n").replace("，", "\n").splitlines()]
        return [part for part in parts if part]
    return list(fallback)


def _public_composition_summary(composition: dict[str, Any]) -> dict[str, Any]:
    return {
        "version": composition["version"],
        "status": composition["status"],
        "selected_activity_id": composition["selected_activity_id"],
        "selected_game_template": composition.get("selected_game_template"),
        "selected_rules": deepcopy(composition.get("selected_rules", [])),
    }


def _age_profile(grade_band: str) -> str:
    if _is_lower_primary(grade_band):
        return "lower_primary"
    if "middle" in str(grade_band) or "三年级" in str(grade_band) or "四年级" in str(grade_band):
        return "middle_primary"
    return "upper_primary"


def _is_lower_primary(grade_band: Any) -> bool:
    text = str(grade_band or "")
    return "lower" in text or "一年级" in text or "二年级" in text
