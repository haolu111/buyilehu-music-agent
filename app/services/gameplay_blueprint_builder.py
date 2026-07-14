from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.services.game_template_registry import get_game_template


def build_gameplay_blueprint(
    *,
    workflow_kind: str,
    proposal_card: dict[str, Any],
    instance: dict[str, Any],
    source: dict[str, Any],
) -> dict[str, Any]:
    """Translate a gameplay template into a student-facing gameplay blueprint."""

    lesson_context = source.get("lesson_context", {}) if isinstance(source.get("lesson_context"), dict) else {}
    playable = lesson_context.get("playable_game", {}) if isinstance(lesson_context.get("playable_game"), dict) else {}
    if workflow_kind == "lesson_game" and playable:
        if _is_production_template_instance(instance):
            blueprint = _lesson_template_patch_blueprint(proposal_card, instance, playable, lesson_context)
        else:
            blueprint = _lesson_blueprint(proposal_card, instance, playable, lesson_context)
        return _attach_game_variant_spec(blueprint, source)
    if workflow_kind == "lesson_game":
        blueprint = _lesson_template_blueprint(proposal_card, instance, lesson_context)
        return _attach_game_variant_spec(blueprint, source)
    return _attach_game_variant_spec(_direct_blueprint(proposal_card, instance), source)


def _is_production_template_instance(instance: dict[str, Any]) -> bool:
    template = get_game_template(str(instance.get("template_id") or "")) or {}
    return template.get("runtime_status") == "production" and instance.get("generation_mode") == "template_config"


def _attach_game_variant_spec(blueprint: dict[str, Any], source: dict[str, Any]) -> dict[str, Any]:
    variant = source.get("game_variant_spec") if isinstance(source.get("game_variant_spec"), dict) else {}
    if not variant:
        return blueprint
    updated = dict(blueprint)
    updated["game_variant_spec"] = deepcopy(variant)
    entity_application = variant.get("entity_application") if isinstance(variant.get("entity_application"), dict) else {}
    if entity_application:
        updated["music_entity_execution"] = {
            "contract_schema_version": deepcopy(variant.get("contract_schema_version", "")),
            "music_entity": deepcopy(variant.get("music_entity", {})),
            "variant_parameters": deepcopy(variant.get("variant_parameters", {})),
            "slot_bindings": deepcopy(variant.get("slot_bindings", {})),
            "entity_application": deepcopy(entity_application),
            "material_entities": deepcopy(variant.get("material_entities", []))
            if isinstance(variant.get("material_entities"), list)
            else [],
            "selected_entity": deepcopy(variant.get("selected_entity", {}))
            if isinstance(variant.get("selected_entity"), dict)
            else {},
            "template_capability_match": deepcopy(variant.get("template_capability_match", {}))
            if isinstance(variant.get("template_capability_match"), dict)
            else {},
            "execution_plan": deepcopy(variant.get("execution_plan", {}))
            if isinstance(variant.get("execution_plan"), dict)
            else {},
            "confirmation_gates": deepcopy(variant.get("confirmation_gates", []))
            if isinstance(variant.get("confirmation_gates"), list)
            else [],
            "teacher_confirmation_cards": deepcopy(variant.get("teacher_confirmation_cards", []))
            if isinstance(variant.get("teacher_confirmation_cards"), list)
            else [],
        }
    return updated


def _lesson_template_patch_blueprint(
    proposal_card: dict[str, Any],
    instance: dict[str, Any],
    playable: dict[str, Any],
    lesson_context: dict[str, Any],
) -> dict[str, Any]:
    blueprint = _lesson_template_blueprint(proposal_card, instance, lesson_context)
    prompt = str(playable.get("prompt") or "").strip()
    if prompt:
        blueprint["prompt"] = prompt
    rounds = _clean_rounds(playable.get("rounds"), playable.get("target_sequence"))
    if rounds:
        blueprint["rounds"] = rounds
    if isinstance(playable.get("materials"), list):
        blueprint["materials"] = deepcopy(playable.get("materials", []))
    if isinstance(playable.get("target_sequence"), list):
        blueprint["target_sequence"] = deepcopy(playable.get("target_sequence", []))
    if isinstance(playable.get("feedback"), dict):
        blueprint["feedback_rules"] = {
            **dict(blueprint.get("feedback_rules", {}) if isinstance(blueprint.get("feedback_rules"), dict) else {}),
            **deepcopy(playable.get("feedback", {})),
        }
    if isinstance(playable.get("learning_transfer"), dict):
        transfer = dict(blueprint.get("learning_transfer", {}) if isinstance(blueprint.get("learning_transfer"), dict) else {})
        transfer.update(deepcopy(playable.get("learning_transfer", {})))
        blueprint["learning_transfer"] = transfer
    blueprint["lesson_adaptation_mode"] = "template_component_patch"
    blueprint["playable_scaffold_operation_type"] = str(playable.get("operation_type") or "")
    return blueprint


def _lesson_blueprint(
    proposal_card: dict[str, Any],
    instance: dict[str, Any],
    playable: dict[str, Any],
    lesson_context: dict[str, Any],
) -> dict[str, Any]:
    operation_type = str(playable.get("operation_type") or "lesson_mission")
    rounds = _clean_rounds(playable.get("rounds"), playable.get("target_sequence"))
    feedback = dict(playable.get("feedback", {}) if isinstance(playable.get("feedback"), dict) else {})
    config = instance.get("config", {}) if isinstance(instance.get("config"), dict) else {}
    variant = config.get("experience_variant") if isinstance(config.get("experience_variant"), dict) else {}
    return {
        "version": "gameplay_blueprint_v1",
        "source_kind": "lesson_game",
        "based_on_template": instance.get("template_id", ""),
        "experience_variant_id": config.get("experience_variant_id", ""),
        "play_mode": config.get("skin_play_mode", ""),
        "game_genre": config.get("game_genre", ""),
        "variant_game_genre": config.get("variant_game_genre", ""),
        "scene_goal": variant.get("scene_goal", ""),
        "main_object": variant.get("main_object", ""),
        "interaction_feedback": variant.get("interaction_feedback", ""),
        "failure_feedback": variant.get("failure_feedback", ""),
        "reward_loop": variant.get("reward_loop", ""),
        "playfield_composition": config.get("playfield_composition", ""),
        "student_facing_name": lesson_context.get("recommended_game_name")
        or proposal_card.get("template_label")
        or "课堂音乐游戏",
        "player_verb": _player_verb(operation_type),
        "operation_type": operation_type,
        "music_focus": playable.get("music_goal") or proposal_card.get("music_element") or "",
        "lesson_goal": playable.get("lesson_objective") or "",
        "selected_stage": playable.get("target_stage") or "",
        "prompt": playable.get("prompt") or "",
        "core_loop": _lesson_core_loop(playable),
        "student_actions": deepcopy(playable.get("required_student_actions", [])),
        "win_condition": playable.get("completion_condition") or "",
        "fail_condition": _fail_condition(operation_type),
        "retry_rule": _retry_rule(operation_type),
        "rounds": rounds,
        "materials": deepcopy(playable.get("materials", [])),
        "target_sequence": deepcopy(playable.get("target_sequence", [])),
        "feedback_rules": feedback,
        "learning_transfer": deepcopy(playable.get("learning_transfer", {})),
        "ui_contract": deepcopy(playable.get("ui_contract", {})),
    }


def _direct_blueprint(proposal_card: dict[str, Any], instance: dict[str, Any]) -> dict[str, Any]:
    template_id = str(instance.get("template_id") or "")
    template = get_game_template(template_id) or {}
    config = instance.get("config", {}) if isinstance(instance.get("config"), dict) else {}
    variant = config.get("experience_variant") if isinstance(config.get("experience_variant"), dict) else {}
    operation_type = _direct_operation_type(template_id, config)
    rounds = _direct_rounds(template_id, config)
    return {
        "version": "gameplay_blueprint_v1",
        "source_kind": "direct_game",
        "based_on_template": template_id,
        "experience_variant_id": config.get("experience_variant_id", ""),
        "play_mode": config.get("skin_play_mode", ""),
        "game_genre": config.get("game_genre", ""),
        "variant_game_genre": config.get("variant_game_genre", ""),
        "scene_goal": variant.get("scene_goal", ""),
        "main_object": variant.get("main_object", ""),
        "interaction_feedback": variant.get("interaction_feedback", ""),
        "failure_feedback": variant.get("failure_feedback", ""),
        "reward_loop": variant.get("reward_loop", ""),
        "playfield_composition": config.get("playfield_composition", ""),
        "student_facing_name": variant.get("student_mission") or proposal_card.get("template_label") or template.get("label") or "音乐游戏",
        "player_verb": _player_verb(operation_type),
        "operation_type": operation_type,
        "music_focus": proposal_card.get("music_element") or config.get("music_concept") or "",
        "lesson_goal": proposal_card.get("learning_goal") or "",
        "selected_stage": "",
        "prompt": variant.get("student_mission") or _direct_prompt(template_id, config),
        "core_loop": deepcopy(template.get("core_loop", [])),
        "student_actions": deepcopy(template.get("student_actions", [])),
        "win_condition": variant.get("scene_goal") or _direct_win_condition(template_id, config),
        "fail_condition": variant.get("failure_feedback") or _fail_condition(operation_type),
        "retry_rule": _retry_rule(operation_type),
        "rounds": rounds,
        "materials": [],
        "target_sequence": [],
        "feedback_rules": deepcopy(instance.get("feedback_rules", {})),
        "learning_transfer": {},
        "ui_contract": {
            "must_have_controls": _direct_controls(template_id),
            "must_have_regions": ["本关任务", "操作区", "即时反馈"],
        },
    }


def _lesson_template_blueprint(
    proposal_card: dict[str, Any],
    instance: dict[str, Any],
    lesson_context: dict[str, Any],
) -> dict[str, Any]:
    blueprint = _direct_blueprint(proposal_card, instance)
    transfer_task = (
        proposal_card.get("transfer_task")
        or lesson_context.get("transfer_task")
        or "通关后回到课堂任务，用唱、拍、说或动作说明音乐依据。"
    )
    blueprint.update(
        {
            "source_kind": "lesson_game",
            "student_facing_name": lesson_context.get("recommended_game_name")
            or proposal_card.get("student_mission")
            or blueprint.get("student_facing_name")
            or "课堂音乐游戏",
            "lesson_goal": lesson_context.get("target_objective")
            or lesson_context.get("teaching_objective")
            or blueprint.get("lesson_goal", ""),
            "selected_stage": lesson_context.get("target_stage") or "",
            "learning_transfer": {"classroom_transfer": transfer_task},
        }
    )
    return blueprint


def _clean_rounds(raw_rounds: Any, fallback_sequence: Any) -> list[dict[str, Any]]:
    rounds = [dict(item) for item in raw_rounds or [] if isinstance(item, dict)]
    if rounds:
        return rounds
    sequence = list(fallback_sequence) if isinstance(fallback_sequence, list) else []
    return [
        {
            "id": "round_1",
            "label": "第 1 关",
            "prompt": "先听，再完成挑战。",
            "target_sequence": sequence,
            "stars": 1,
        }
    ]


def _lesson_core_loop(playable: dict[str, Any]) -> list[str]:
    actions = [str(item) for item in playable.get("required_student_actions", []) if str(item).strip()]
    if actions:
        return actions[:5]
    return ["试听目标", "学生操作", "即时反馈", "重新尝试", "课堂迁移"]


def _direct_operation_type(template_id: str, config: dict[str, Any]) -> str:
    if template_id == "beat_guardian_core":
        return "beat_guardian_tap"
    if template_id == "pitch_ladder_core":
        return "pitch_ladder_sequence" if config.get("mode") == "melody_climb" else "pitch_direction_choice"
    if template_id == "solfege_target_core":
        return "solfege_target_hit"
    if template_id == "timbre_detective_core":
        return "timbre_evidence_match"
    if template_id == "form_treasure_core":
        return "form_treasure_map"
    if template_id == "composition_puzzle_core":
        mode = str(config.get("mode") or "")
        if mode == "melody_puzzle_creation":
            return "composition_puzzle_melody"
        if mode == "melody_rhythm_puzzle":
            return "composition_puzzle_melody_rhythm"
        return "composition_puzzle_rhythm"
    return "rhythm_echo_tap"


def _direct_rounds(template_id: str, config: dict[str, Any]) -> list[dict[str, Any]]:
    if template_id == "composition_puzzle_core" and isinstance(config.get("composition_rounds"), list):
        return [
            {
                "id": item.get("id", f"round_{index + 1}"),
                "label": item.get("label", f"第 {index + 1} 关"),
                "prompt": item.get("prompt") or _direct_prompt(template_id, config),
                "target_sequence": item.get("target_sequence", []),
                "stars": item.get("stars", min(index + 1, 3)),
                "constraints": deepcopy(item.get("constraints", [])),
            }
            for index, item in enumerate(config.get("composition_rounds", []))
            if isinstance(item, dict)
        ]
    if template_id == "pitch_ladder_core" and isinstance(config.get("pitch_rounds"), list):
        return [
            {
                "id": item.get("id", f"round_{index + 1}"),
                "label": f"第 {index + 1} 关",
                "prompt": "先听，再判断音高路线。",
                "target_sequence": item.get("answer", []),
                "stars": index + 1,
            }
            for index, item in enumerate(config.get("pitch_rounds", []))
            if isinstance(item, dict)
        ]
    round_count = max(1, int(config.get("round_count") or 1))
    return [
        {
            "id": f"round_{index + 1}",
            "label": f"第 {index + 1} 关",
            "prompt": _direct_prompt(template_id, config),
            "target_sequence": [],
            "stars": min(index + 1, 3),
        }
        for index in range(min(round_count, 6))
    ]


def _direct_prompt(template_id: str, config: dict[str, Any]) -> str:
    if template_id == "beat_guardian_core":
        return "看怪物靠近，预判每小节第 1 拍并同步充能清怪。"
    if template_id == "pitch_ladder_core":
        return "先听目标音，再判断或走出音高路线。"
    if template_id == "solfege_target_core":
        return "先听目标音，在心里唱名，再击中靶心。"
    if template_id == "timbre_detective_core":
        return "先听声音证据，再找出最有力的音色判断。"
    if template_id == "form_treasure_core":
        return "先听段落，再把结构卡排成正确曲式路线。"
    if template_id == "composition_puzzle_core":
        mode = str(config.get("mode") or "")
        if mode == "melody_puzzle_creation":
            return "选择唱名卡，拖入轨道，拼出有走向和结束感的短旋律。"
        if mode == "melody_rhythm_puzzle":
            return "把音高和时值组合成完整音乐短句，试听后检查规则。"
        return "选择节奏卡，填满小节，创编一个稳定又有变化的节奏短句。"
    return "先听节奏示范，再把它稳稳复刻出来。"


def _direct_win_condition(template_id: str, config: dict[str, Any]) -> str:
    if template_id == "beat_guardian_core":
        return "连续在第 1 拍同步充能，让护盾保持稳定。"
    if template_id == "pitch_ladder_core":
        return "正确判断音高关系或完成目标音列。"
    if template_id == "solfege_target_core":
        return "听准唱名并完成唱回。"
    if template_id == "timbre_detective_core":
        return "找对音色来源，并说出听觉证据。"
    if template_id == "composition_puzzle_core":
        return "作品轨道填满并满足约束，试听后完成教师确认。"
    return "复刻目标节奏并保持稳定拍。"


def _direct_controls(template_id: str) -> list[str]:
    return {
        "beat_guardian_core": ["开始节拍", "充能", "重新开始"],
        "pitch_ladder_core": ["听目标音", "下一轮"],
        "solfege_target_core": ["听目标音", "唱回完成", "下一轮"],
        "timbre_detective_core": ["听声音证物", "提交推理", "下一案"],
        "composition_puzzle_core": ["选择素材", "试听作品", "检查约束", "教师确认", "重来"],
        "rhythm_echo_core": ["听示范", "拍一下", "下一轮", "重来"],
    }.get(template_id, ["开始", "重试"])


def _player_verb(operation_type: str) -> str:
    return {
        "melody_path_draw": "画路线",
        "melody_path": "判断路线",
        "beat_guardian_tap": "充能",
        "pitch_direction_choice": "判断高低",
        "pitch_ladder_sequence": "走音阶",
        "solfege_target_hit": "击中唱名",
        "timbre_evidence_match": "找证据",
        "composition_puzzle_rhythm": "拼节奏",
        "composition_puzzle_melody": "拼旋律",
        "composition_puzzle_melody_rhythm": "拼音符短句",
        "rhythm_echo_tap": "复刻节奏",
    }.get(operation_type, "完成挑战")


def _fail_condition(operation_type: str) -> str:
    if operation_type.startswith("composition_puzzle"):
        return "作品轨道未填满，或没有满足本关节奏、旋律与教师确认要求。"
    if operation_type == "melody_path_draw":
        return "学生画出的路线与目标旋律高低变化不一致。"
    if "rhythm" in operation_type or "beat" in operation_type:
        return "学生没有在正确拍点完成动作。"
    if "timbre" in operation_type:
        return "学生没有选出正确音色或证据。"
    return "学生答案与目标音乐材料不一致。"


def _retry_rule(operation_type: str) -> str:
    if operation_type.startswith("composition_puzzle"):
        return "允许保留素材卡并重新排列，试听后再次检查。"
    if operation_type == "melody_path_draw":
        return "允许重听并重画，保留错误后给予方向提示。"
    if "rhythm" in operation_type or "beat" in operation_type:
        return "允许重新听示范并重新尝试。"
    return "允许重听、修改答案并再次提交。"
