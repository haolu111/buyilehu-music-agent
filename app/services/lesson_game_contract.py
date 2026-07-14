from __future__ import annotations

import json
import re
from typing import Any


def build_lesson_game_contract(proposal: dict[str, Any]) -> dict[str, Any]:
    """Build the lesson-game contract for lesson-driven scaffold-first generation."""

    lesson_analysis = proposal.get("lesson_analysis", {}) if isinstance(proposal.get("lesson_analysis"), dict) else {}
    lesson_context = proposal.get("lesson_context", {}) if isinstance(proposal.get("lesson_context"), dict) else {}
    if not lesson_context and isinstance(lesson_analysis.get("lesson_context"), dict):
        lesson_context = lesson_analysis.get("lesson_context", {})
    recommended = lesson_analysis.get("recommended_game", {}) if isinstance(lesson_analysis.get("recommended_game"), dict) else {}
    focus = lesson_analysis.get("specific_focus", {}) if isinstance(lesson_analysis.get("specific_focus"), dict) else {}
    playable = lesson_context.get("playable_game") if isinstance(lesson_context.get("playable_game"), dict) else {}
    lesson_adaptation = (
        lesson_context.get("lesson_adaptation")
        if isinstance(lesson_context.get("lesson_adaptation"), dict)
        else lesson_analysis.get("lesson_adaptation")
        if isinstance(lesson_analysis.get("lesson_adaptation"), dict)
        else {}
    )
    if not playable and isinstance(recommended.get("playable_game"), dict):
        playable = recommended.get("playable_game", {})
    song_material = lesson_context.get("song_material") if isinstance(lesson_context.get("song_material"), dict) else {}
    song_anchor = lesson_context.get("song_anchor_contract") if isinstance(lesson_context.get("song_anchor_contract"), dict) else {}
    music_logic = lesson_context.get("music_logic_contract") if isinstance(lesson_context.get("music_logic_contract"), dict) else {}
    if not music_logic and isinstance(recommended.get("music_logic_contract"), dict):
        music_logic = recommended.get("music_logic_contract", {})

    selected_segment = lesson_context.get("selected_game_segment") if isinstance(lesson_context.get("selected_game_segment"), dict) else {}
    rules = _string_list(recommended.get("rules") or lesson_context.get("recommended_game_rules"))
    student_actions = _string_list(
        recommended.get("student_actions")
        or lesson_context.get("recommended_game_actions")
        or playable.get("required_student_actions")
    )

    contract = {
        "version": "lesson_game_contract_v1",
        "generation_mode": "lesson_contract_scaffold_first",
        "template_policy": {
            "allow_template_rendering": False,
            "allow_template_fallback": False,
            "direct_generation_tools_unaffected": True,
            "opencode_failure_strategy": "repair_current_artifact_only",
            "prefer_playable_scaffold": True,
        },
        "lesson_goal": _text(
            lesson_context.get("target_objective")
            or recommended.get("goal")
            or lesson_analysis.get("core_objective")
            or lesson_analysis.get("objective_summary")
        ),
        "selected_stage": _text(
            lesson_context.get("target_stage")
            or lesson_analysis.get("game_stage")
            or selected_segment.get("stage_label")
        ),
        "music_focus": _text(
            lesson_context.get("target_music_element")
            or recommended.get("music_element")
            or focus.get("element")
        ),
        "selected_task": _text(
            lesson_context.get("target_segment_task")
            or selected_segment.get("task_summary")
        ),
        "game_name": _text(recommended.get("name") or lesson_context.get("recommended_game_name")),
        "game_mechanic": _text(
            recommended.get("mechanic")
            or lesson_context.get("target_segment_gameable_point")
            or selected_segment.get("gameable_point")
        ),
        "student_actions": student_actions,
        "rules": rules,
        "win_condition": _text(
            recommended.get("win_condition")
            or playable.get("completion_condition")
            or lesson_context.get("assessment_closure")
        ),
        "playable_game": _compact_playable(playable),
        "music_logic_contract": _compact_music_logic(music_logic),
        "song_anchor_contract": _compact_song_anchor(song_anchor),
        "sound_source_policy": _sound_source_policy(song_material),
        "lesson_adaptation": _compact_lesson_adaptation(lesson_adaptation),
        "uploaded_material_policy": {
            "uploaded_audio_must_render": bool(_sound_source_policy(song_material).get("has_uploaded_audio")),
            "uploaded_score_prefer_when_needed": bool(song_anchor),
            "score_usage_policy": "use_when_it_supports_the_selected_task_or_song_anchor",
        },
        "must_include": _must_include_terms(lesson_analysis, lesson_context, recommended, playable),
        "must_not_include": [
            "模板页",
            "通用规则说明页",
            "教师检查清单",
            "OpenCode",
            "API",
            "模型",
            "Basic Pitch",
            "排行榜",
            "登录",
            "录音",
        ],
        "qa_checks": [
            "不要使用任何本地模板页或活动母版兜底；教案生成应优先复用可玩骨架承载当前课堂任务。",
            "页面必须可玩：开始、试听或播放、学生操作、即时反馈、胜利条件、重新挑战。",
            "页面必须显性呈现本关任务、教案环节和音乐重点。",
            "如果教师上传了音频，页面必须实际接入该音频或它切出的真实片段，至少一个学生可见播放按钮/卡片要能播放上传素材；不能只保留 SoundFont 或空壳试听。",
            "播放必须使用真实音色：上传音频切片、SoundFont/FluidR3_GM 或 SF2 渲染，oscillator 只能作为降级。",
            "如果教师上传了谱子，且当前任务需要具体歌曲片段、乐句或判定材料，应优先使用谱面解析结果；如果当前任务不依赖谱面细节，可以不强制显示整张谱。",
            "音乐符号、片段、答案和判定必须来自 music_logic_contract、song_anchor_contract 或 playable_game。",
        ],
        "responsibility_boundary": {
            "lesson_fit_director": "决定本课真正要学什么、绑定哪段材料、学生必须完成什么学习行为。",
            "template_mechanism_router": "只负责选择能承载该学习行为的成熟玩法底盘。",
            "frontend_presentation_director": "只负责把已锁定玩法做成学生愿意玩的前端体验，不得改写教学与答案。",
        },
    }
    return _drop_empty(contract)


def apply_lesson_game_contract_to_spec(spec: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    updated = json.loads(json.dumps(spec, ensure_ascii=False))
    lesson_context = updated.setdefault("lesson_context", {})
    music_game = updated.setdefault("music_game", {})
    updated["activity_type"] = "music_game"
    updated["lesson_game_contract"] = contract
    if contract.get("lesson_adaptation"):
        updated["lesson_adaptation"] = contract["lesson_adaptation"]
    updated["lesson_generation_policy"] = {
        "mode": "fast",
        "template_fallback": False,
        "template_rendering": False,
        "real_sound_required": True,
        "repair_strategy": "opencode_repair_current_artifact_only",
        "scaffold_policy": "prefer_playable_scaffold",
        "freeform_fallback": True,
    }
    updated["artifact_generation_mode"] = "prefer_scaffold"
    updated["template_id"] = "lesson_game_contract_playable_scaffold"
    updated["blueprint_plan"] = {
        "blueprint_id": "Reusable_Playable_Scaffold",
        "blueprint_label": "可复用玩法骨架",
        "selection_reason": "教案生成优先复用稳定可玩骨架承载课堂任务，不使用模板页；未命中时再进入 OpenCode 自由生成。",
        "primary_interaction": contract.get("playable_game", {}).get("operation_type", "lesson_mission_game")
        if isinstance(contract.get("playable_game"), dict)
        else "lesson_mission_game",
    }
    updated["generation_strategy"] = {
        "mode": "prefer_playable_scaffold_then_freeform",
        "artifact_goal": "先锁定教案适配和成熟玩法底盘，再由 OpenCode 负责学生端表现层深化；不适合骨架时再自由生成。",
        "opencode_execution_target": "命中模板时 OpenCode 只做表现层深化；未命中时按教案契约自由生成；可玩骨架只作为结构参考，不作为本地页面兜底。",
        "prefer_incremental_revision": True,
        "scaffold_policy": "prefer_playable_scaffold",
        "freeform_fallback": True,
        "render_priority": [
            "lesson_game_contract",
            "music_logic_contract",
            "playable_game",
            "real_sound_playback",
            "student_game_loop",
        ],
    }
    components = updated.setdefault("interaction_model", {}).setdefault("components", [])
    if isinstance(components, list):
        for component in ["playback_controls", "drag_drop_puzzle", "reflection_panel"]:
            if component not in components:
                components.append(component)
    music_game["enabled"] = True
    if contract.get("playable_game"):
        music_game["playable_game"] = contract["playable_game"]
    if contract.get("music_logic_contract"):
        updated["music_logic_contract"] = contract["music_logic_contract"]
        music_game["music_logic_contract"] = contract["music_logic_contract"]
    if contract.get("song_anchor_contract"):
        updated["song_anchor_contract"] = contract["song_anchor_contract"]
    lesson_context["lesson_game_contract"] = contract
    return updated


def _sound_source_policy(song_material: dict[str, Any]) -> dict[str, Any]:
    source = song_material.get("source", {}) if isinstance(song_material.get("source"), dict) else {}
    has_audio_clips = False
    for phrase in song_material.get("phrases", []) if isinstance(song_material.get("phrases"), list) else []:
        if isinstance(phrase, dict) and phrase.get("audio_clip_url"):
            has_audio_clips = True
            break
    return {
        "real_sound_required": True,
        "priority": [
            "uploaded_audio_phrase_clips",
            "local_soundfont_player_fluidr3_gm",
            "sf2_offline_render",
        ],
        "oscillator_policy": "fallback_only_not_primary",
        "has_uploaded_audio": bool(source.get("source_audio_url")),
        "has_audio_clips": has_audio_clips,
        "source_audio_url": source.get("source_audio_url", ""),
    }


def _compact_playable(playable: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(playable, dict):
        return {}
    return {
        "operation_type": playable.get("operation_type", ""),
        "prompt": playable.get("prompt", ""),
        "materials": [
            {
                "id": item.get("id", ""),
                "label": item.get("label", ""),
                "music_value": item.get("music_value", ""),
                "feedback": item.get("feedback", ""),
                "audio_clip_url": item.get("audio_clip_url", ""),
                "playback_tokens": item.get("playback_tokens", [])[:8] if isinstance(item.get("playback_tokens"), list) else [],
            }
            for item in playable.get("materials", [])[:10]
            if isinstance(item, dict)
        ],
        "target_sequence": playable.get("target_sequence", [])[:16] if isinstance(playable.get("target_sequence"), list) else [],
        "rounds": [
            {
                "id": item.get("id", ""),
                "label": item.get("label", ""),
                "prompt": item.get("prompt", ""),
                "target_sequence": item.get("target_sequence", [])[:16]
                if isinstance(item.get("target_sequence"), list)
                else [],
                "stars": item.get("stars", 0),
            }
            for item in playable.get("rounds", [])[:8]
            if isinstance(item, dict)
        ],
        "check_rule": playable.get("check_rule", ""),
        "completion_condition": playable.get("completion_condition", ""),
        "required_student_actions": _string_list(playable.get("required_student_actions"), limit=6),
        "feedback": playable.get("feedback", {}) if isinstance(playable.get("feedback"), dict) else {},
        "learning_transfer": playable.get("learning_transfer", {}) if isinstance(playable.get("learning_transfer"), dict) else {},
    }


def _compact_music_logic(contract: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(contract, dict):
        return {}
    compact = dict(contract)
    if isinstance(compact.get("tokens"), list):
        compact["tokens"] = compact["tokens"][:16]
    if isinstance(compact.get("answer_sequences"), list):
        compact["answer_sequences"] = compact["answer_sequences"][:8]
    return compact


def _compact_song_anchor(contract: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(contract, dict):
        return {}
    selected = contract.get("selected_phrase") if isinstance(contract.get("selected_phrase"), dict) else {}
    return {
        "required": bool(contract),
        "song_title": contract.get("song_title", ""),
        "selected_phrase_id": contract.get("selected_phrase_id", ""),
        "selected_phrase": {
            "id": selected.get("id", ""),
            "label": selected.get("label", ""),
            "target_sequence": selected.get("target_sequence", [])[:16] if isinstance(selected.get("target_sequence"), list) else [],
            "playback_tokens": selected.get("playback_tokens", [])[:12] if isinstance(selected.get("playback_tokens"), list) else [],
            "audio_clip_url": selected.get("audio_clip_url", ""),
        },
    }


def _compact_lesson_adaptation(contract: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(contract, dict):
        return {}
    lesson_focus = contract.get("lesson_focus", {}) if isinstance(contract.get("lesson_focus"), dict) else {}
    student_learning = (
        contract.get("student_learning_contract", {})
        if isinstance(contract.get("student_learning_contract"), dict)
        else {}
    )
    template_need = contract.get("template_need", {}) if isinstance(contract.get("template_need"), dict) else {}
    return {
        "version": contract.get("version", ""),
        "owner": contract.get("owner", ""),
        "lesson_focus": lesson_focus,
        "student_learning_contract": {
            "operation_type": student_learning.get("operation_type", ""),
            "prompt": student_learning.get("prompt", ""),
            "required_student_actions": _string_list(student_learning.get("required_student_actions"), limit=6),
            "completion_condition": student_learning.get("completion_condition", ""),
        },
        "template_need": {
            "operation_type": template_need.get("operation_type", ""),
            "mechanism_id": template_need.get("mechanism_id", ""),
            "music_focus": template_need.get("music_focus", ""),
        },
    }


def _must_include_terms(
    lesson_analysis: dict[str, Any],
    lesson_context: dict[str, Any],
    recommended: dict[str, Any],
    playable: dict[str, Any],
) -> list[str]:
    values = [
        lesson_analysis.get("song_name"),
        lesson_analysis.get("grade_band"),
        lesson_context.get("target_stage"),
        lesson_context.get("target_music_element"),
        lesson_context.get("target_segment_task"),
        recommended.get("name"),
        recommended.get("music_element"),
        playable.get("operation_type") if isinstance(playable, dict) else "",
    ]
    result: list[str] = []
    for value in values:
        text = _text(value, 80)
        if text and text not in result:
            result.append(text)
    return result


def _string_list(value: Any, limit: int = 8) -> list[str]:
    if not isinstance(value, list):
        return []
    result = []
    for item in value[:limit]:
        if isinstance(item, dict):
            item = item.get("value") or item.get("label") or item.get("feedback") or item.get("music_element")
        text = _text(item, 120)
        if text:
            result.append(text)
    return result


def _text(value: Any, limit: int = 220) -> str:
    cleaned = re.sub(r"\s+", " ", str(value or "")).strip()
    return cleaned if len(cleaned) <= limit else cleaned[:limit].rstrip() + "..."


def _drop_empty(value: Any) -> Any:
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            cleaned = _drop_empty(item)
            if cleaned in ({}, [], ""):
                continue
            result[key] = cleaned
        return result
    if isinstance(value, list):
        return [_drop_empty(item) for item in value if _drop_empty(item) not in ({}, [], "")]
    return value
