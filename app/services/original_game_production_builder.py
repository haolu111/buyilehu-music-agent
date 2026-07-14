from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.services.component_capability_registry import build_component_capability_plan


def build_original_game_concept(
    instance: dict[str, Any],
    *,
    game_concept: dict[str, Any] | None = None,
    segment_game_brief: dict[str, Any] | None = None,
) -> dict[str, Any]:
    config = instance.get("config") if isinstance(instance.get("config"), dict) else {}
    template_id = str(instance.get("template_id") or config.get("template_id") or "").strip()
    concept = game_concept if isinstance(game_concept, dict) else {}
    brief = segment_game_brief if isinstance(segment_game_brief, dict) else {}
    student_loop = _student_loop(concept, config)
    music_target = str(
        concept.get("music_learning_target")
        or brief.get("music_learning_target")
        or config.get("music_concept")
        or "音乐要素感知与表达"
    )
    core_metaphor = str(
        concept.get("core_mechanic")
        or brief.get("core_mechanic")
        or config.get("theme")
        or config.get("game_feel")
        or "课堂音乐任务闯关"
    )
    title = str(config.get("theme") or config.get("skin_objective") or "原创课堂音乐游戏")
    if brief.get("source_segment_id"):
        title = f"{title}：{music_target}"
    return {
        "version": "original_game_concept_v1",
        "source": "segment_game_brief" if brief else "runtime_request",
        "game_title": title,
        "template_runtime_candidate": template_id,
        "music_learning_target": music_target,
        "core_metaphor": core_metaphor,
        "student_loop": student_loop,
        "success_condition": str(concept.get("success_condition") or brief.get("success_condition") or ""),
        "classroom_return": str(concept.get("classroom_return") or brief.get("classroom_return") or config.get("result_transfer_prompt") or ""),
        "originality_policy": {
            "seven_templates_are_quality_reference": True,
            "template_runtime_is_not_final_design": True,
            "final_output_policy": "original_lesson_game_not_template_skin",
        },
        "not_template_skin_reason": _not_template_skin_reason(
            template_id=template_id,
            music_target=music_target,
            core_metaphor=core_metaphor,
            source_segment_id=str(brief.get("source_segment_id") or concept.get("source_segment_id") or ""),
            source_evidence=str(brief.get("source_evidence") or concept.get("source_evidence") or ""),
        ),
    }


def build_component_assembly_plan(
    instance: dict[str, Any],
    *,
    game_design: dict[str, Any],
    original_game_concept: dict[str, Any],
) -> dict[str, Any]:
    config = instance.get("config") if isinstance(instance.get("config"), dict) else {}
    template_id = str(instance.get("template_id") or config.get("template_id") or "").strip()
    mechanic = game_design.get("mechanic_contract") if isinstance(game_design.get("mechanic_contract"), dict) else {}
    operation = str(mechanic.get("operation") or config.get("interaction_model") or "")
    reusable = [
        {
            "component_id": "audio_unlock_and_playback",
            "reason": "真实声音、重听和课堂投屏播放是重复底层能力。",
            "quality_gates": ["audio_playable", "relisten_ready"],
        },
        {
            "component_id": "teacher_control_protocol",
            "reason": "开始、暂停、重置、调速、提示量应走统一教师控制协议。",
            "quality_gates": ["teacher_can_adjust", "reset_ready"],
        },
        {
            "component_id": "asset_loader_registry",
            "reason": "背景、角色、道具和奖励资产必须从登记表进入运行时。",
            "quality_gates": ["asset_visible", "fallback_registered"],
        },
    ]
    if any(token in operation for token in ("tap", "beat", "replay", "predict")):
        reusable.append(
            {
                "component_id": "beat_timeline_judge",
                "reason": "拍点、早晚漏和同步判定属于可复用音乐游戏能力。",
                "quality_gates": ["meter_bound", "timing_feedback_ready"],
            }
        )
    if any(token in operation for token in ("drag", "choice", "match", "order")):
        reusable.append(
            {
                "component_id": "choice_drag_order_input",
                "reason": "选择、拖拽和排序输入由组件库统一处理。",
                "quality_gates": ["student_operable", "sequence_reset_ready"],
            }
        )
    capability_plan = build_component_capability_plan(
        game_design=game_design,
        original_game_concept=original_game_concept,
        config=config,
    )
    return {
        "version": "component_assembly_plan_v1",
        "template_runtime_candidate": template_id,
        "mechanic_id": str(mechanic.get("mechanic_id") or ""),
        "reuse_policy": "reuse_stable_components_generate_only_lesson_specific_parts",
        "assembly_mode": "registered_components_plus_lesson_specific_generation",
        "reusable_components": reusable,
        **capability_plan,
        "generated_parts": [
            "lesson_specific_music_truth",
            "original_game_rules",
            "level_content",
            "lesson_specific_scene_bible",
            "lesson_specific_asset_tasks",
            "scene_bible",
            "image_generation_tasks",
            "student_feedback_copy",
            "classroom_return",
        ],
        "original_game_concept_ref": "original-game-concept.json" if original_game_concept else "",
    }


def build_game_state_machine(
    instance: dict[str, Any],
    *,
    game_design: dict[str, Any],
    level_curve: dict[str, Any],
    asset_contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    config = instance.get("config") if isinstance(instance.get("config"), dict) else {}
    template_id = str(instance.get("template_id") or config.get("template_id") or "").strip()
    mechanic = game_design.get("mechanic_contract") if isinstance(game_design.get("mechanic_contract"), dict) else {}
    loop = mechanic.get("runtime_loop") if isinstance(mechanic.get("runtime_loop"), list) else []
    states = _ordered_states(loop)
    state_asset_bindings = _state_asset_bindings(asset_contract if isinstance(asset_contract, dict) else {})
    return {
        "version": "game_state_machine_v1",
        "template_runtime_candidate": template_id,
        "states": states,
        "state_asset_bindings": state_asset_bindings,
        "initial_state": "start",
        "terminal_states": ["classroom_return"],
        "required_runtime_states": ["start", "listen", "student_action", "judge", "feedback", "retry", "reward", "classroom_return"],
        "transitions": [
            {"from": "start", "to": "listen", "trigger": "teacher_or_student_start"},
            {"from": "listen", "to": "student_action", "trigger": "audio_or_count_in_finished"},
            {"from": "student_action", "to": "judge", "trigger": "student_input_submitted_or_window_closed"},
            {"from": "judge", "to": "feedback", "trigger": "music_truth_checked"},
            {"from": "feedback", "to": "retry", "trigger": "accuracy_below_threshold"},
            {"from": "feedback", "to": "reward", "trigger": "accuracy_passed"},
            {"from": "retry", "to": "listen", "trigger": "retry_selected"},
            {"from": "reward", "to": "listen", "trigger": "next_level_available"},
            {"from": "reward", "to": "classroom_return", "trigger": "all_levels_completed"},
        ],
        "level_count": len(level_curve.get("levels", [])) if isinstance(level_curve.get("levels"), list) else 0,
        "static_exercise_blocker": "state_machine_requires_failure_retry_reward_and_level_progression",
    }


def build_image_generation_tasks(
    instance: dict[str, Any],
    *,
    asset_contract: dict[str, Any],
    scene_bible: str,
    lesson_runtime_generated_assets: dict[str, Any] | None = None,
) -> dict[str, Any]:
    config = instance.get("config") if isinstance(instance.get("config"), dict) else {}
    template_id = str(instance.get("template_id") or config.get("template_id") or "").strip()
    tasks = []
    assets = asset_contract.get("assets") if isinstance(asset_contract.get("assets"), list) else []
    runtime_assets = lesson_runtime_generated_assets if isinstance(lesson_runtime_generated_assets, dict) else {}
    for asset in assets:
        if not isinstance(asset, dict) or not asset.get("generation_required"):
            continue
        runtime_asset = runtime_assets.get(str(asset.get("asset_id") or ""))
        runtime_asset = runtime_asset if isinstance(runtime_asset, dict) else {}
        tasks.append(
            {
                "asset_id": asset.get("asset_id", ""),
                "type": asset.get("type", ""),
                "output_path": asset.get("output_path", ""),
                "size": asset.get("size", "1280x720"),
                "transparent_background": bool(asset.get("transparent_background")),
                "prompt": asset.get("prompt", ""),
                "negative_prompt": "文字，logo，水印，版权角色，复杂杂乱，遮挡操作区",
                "runtime_usage": asset.get("runtime_usage", ""),
                "artifact_save_dir": runtime_asset.get("save_dir", "assets/"),
                "artifact_file": runtime_asset.get("file", _artifact_file_for(asset)),
                "ratio": runtime_asset.get("ratio", _ratio_for_size(str(asset.get("size") or ""))),
                "lesson_grounding": {
                    "source_segment_id": runtime_asset.get("source_segment_id", ""),
                    "lesson_material": runtime_asset.get("lesson_material", ""),
                    "music_goals": runtime_asset.get("music_goals", []),
                    "activity_play": runtime_asset.get("activity_play", ""),
                },
            }
        )
    return {
        "version": "image_generation_tasks_v1",
        "template_runtime_candidate": template_id,
        "scene_bible_ref": "scene-bible.md" if scene_bible else "",
        "provider_policy": {
            "preferred": "agent_internal_image_gen",
            "fallback": "local_preset",
            "must_not_use": ["image2_asset_pack_queue", "chat_ecnu_atmosphere_generation"],
            "notes": "课堂游戏资产图必须由智能体内部 image_gen 能力生成；image2/ChatECNU 只属于既有素材包或氛围图通道。",
        },
        "tasks": tasks,
    }


def build_lesson_runtime_generated_assets(
    instance: dict[str, Any],
    *,
    asset_contract: dict[str, Any],
    segment_game_brief: dict[str, Any] | None = None,
    original_game_concept: dict[str, Any] | None = None,
) -> dict[str, Any]:
    config = instance.get("config") if isinstance(instance.get("config"), dict) else {}
    brief = segment_game_brief if isinstance(segment_game_brief, dict) else {}
    concept = original_game_concept if isinstance(original_game_concept, dict) else {}
    music_goal = str(
        brief.get("music_learning_target")
        or concept.get("music_learning_target")
        or config.get("music_concept")
        or ""
    ).strip()
    lesson_material = str(
        brief.get("source_evidence")
        or config.get("lesson_material")
        or config.get("song_title")
        or config.get("lesson_title")
        or ""
    ).strip()
    source_segment_id = str(brief.get("source_segment_id") or concept.get("source_segment_id") or "").strip()
    activity_play = str(brief.get("core_mechanic") or concept.get("core_metaphor") or config.get("theme") or "").strip()
    assets = asset_contract.get("assets") if isinstance(asset_contract.get("assets"), list) else []
    contract: dict[str, Any] = {}
    for asset in assets:
        if not isinstance(asset, dict):
            continue
        asset_id = str(asset.get("asset_id") or "").strip()
        if not asset_id:
            continue
        generation_required = bool(asset.get("generation_required"))
        contract[asset_id] = {
            "required": generation_required,
            "provider": "agent_internal_image_gen" if generation_required else str(asset.get("source") or "reused_asset"),
            "save_dir": "assets/",
            "file": _artifact_file_for(asset),
            "ratio": _ratio_for_size(str(asset.get("size") or "")),
            "type": str(asset.get("type") or ""),
            "runtime_usage": str(asset.get("runtime_usage") or ""),
            "source_segment_id": source_segment_id,
            "lesson_material": lesson_material,
            "music_goals": [music_goal] if music_goal else [],
            "activity_play": activity_play,
            "reason": "由本课教案环节、音乐目标、游戏状态和课堂情境生成或复用。",
        }
    return contract


def build_generated_asset_registry(
    instance: dict[str, Any],
    *,
    asset_contract: dict[str, Any],
    image_generation_tasks: dict[str, Any],
) -> dict[str, Any]:
    config = instance.get("config") if isinstance(instance.get("config"), dict) else {}
    template_id = str(instance.get("template_id") or config.get("template_id") or "").strip()
    assets = asset_contract.get("assets") if isinstance(asset_contract.get("assets"), list) else []
    reused = []
    pending = []
    for asset in assets:
        if not isinstance(asset, dict):
            continue
        if asset.get("source_url"):
            reused.append(
                {
                    "asset_id": asset.get("asset_id", ""),
                    "type": asset.get("type", ""),
                    "url": asset.get("source_url", ""),
                    "source": asset.get("source", "template_asset_manifest"),
                    "runtime_usage": asset.get("runtime_usage", ""),
                }
            )
        elif asset.get("generation_required"):
            pending.append(
                {
                    "asset_id": asset.get("asset_id", ""),
                    "type": asset.get("type", ""),
                    "task_ref": "image-generation-tasks.json",
                }
            )
    return {
        "version": "generated_asset_registry_v1",
        "template_runtime_candidate": template_id,
        "reused_assets": reused,
        "pending_generation_assets": pending,
        "task_count": len(image_generation_tasks.get("tasks", [])) if isinstance(image_generation_tasks.get("tasks"), list) else 0,
        "status": "ready_with_reused_assets" if reused and not pending else "pending_generation" if pending else "blocked_missing_assets",
    }


def _student_loop(concept: dict[str, Any], config: dict[str, Any]) -> list[str]:
    actions = concept.get("student_actions") if isinstance(concept.get("student_actions"), list) else []
    if actions:
        return [str(action) for action in actions]
    task_copy = config.get("student_task_copy") if isinstance(config.get("student_task_copy"), dict) else {}
    values = [task_copy.get("listen"), task_copy.get("do"), task_copy.get("pass")]
    compact = [str(value) for value in values if value]
    return compact or ["听音乐材料", "完成音乐操作", "根据反馈修正", "回到课堂表现"]


def _not_template_skin_reason(
    *,
    template_id: str,
    music_target: str,
    core_metaphor: str,
    source_segment_id: str,
    source_evidence: str,
) -> str:
    segment_prefix = f"教案环节 {source_segment_id}，" if source_segment_id else ""
    if source_evidence:
        return f"以{segment_prefix}教案证据“{source_evidence}”为来源，围绕“{music_target}”生成“{core_metaphor}”任务；{template_id} 只作为运行时能力候选。"
    return f"围绕“{music_target}”和“{core_metaphor}”生成课堂任务；{template_id} 只作为质量参考和运行时能力候选。"


def _ordered_states(loop: list[Any]) -> list[dict[str, str]]:
    labels = {
        "start": "开始",
        "listen": "听辨",
        "ready": "准备",
        "replay": "学生操作",
        "student_action": "学生操作",
        "judge": "音乐判定",
        "feedback": "反馈",
        "retry": "重试",
        "reward": "奖励",
        "next": "下一关",
        "classroom_return": "课堂回扣",
    }
    ordered = ["start"]
    for item in loop:
        value = str(item)
        if value == "replay":
            value = "student_action"
        if value == "retry_or_next":
            for extra in ("retry", "reward"):
                if extra not in ordered:
                    ordered.append(extra)
            continue
        if value not in ordered:
            ordered.append(value)
    for required in ("listen", "student_action", "judge", "feedback", "retry", "reward", "classroom_return"):
        if required not in ordered:
            ordered.append(required)
    return [{"id": state, "label": labels.get(state, state)} for state in ordered]


def _state_asset_bindings(asset_contract: dict[str, Any]) -> dict[str, dict[str, str]]:
    assets = asset_contract.get("assets") if isinstance(asset_contract.get("assets"), list) else []
    index = _asset_index(assets)
    background = index.get("background") or index.get("scene_background")
    character_default = (
        index.get("character_states") or index.get("character_pose_sheet") or index.get("character_pose") or index.get("character")
    )
    prop = index.get("music_task_prop") or index.get("music_task_props") or index.get("prop") or index.get("prop_sheet")
    feedback = index.get("reward_or_feedback") or index.get("reward_feedback")
    return {
        "start": _compact_binding(
            background=background,
            character=index.get("character_idle") or character_default,
            prop=prop,
        ),
        "listen": _compact_binding(
            background=background,
            character=index.get("character_listen") or character_default,
            prop=prop,
        ),
        "ready": _compact_binding(
            background=background,
            character=index.get("character_ready") or character_default,
            prop=prop,
        ),
        "student_action": _compact_binding(
            background=background,
            character=index.get("character_action") or character_default,
            prop=prop,
        ),
        "judge": _compact_binding(
            background=background,
            prop=prop,
            feedback=feedback,
        ),
        "feedback": _compact_binding(
            background=background,
            character=index.get("character_fail") or index.get("character_success") or character_default,
            feedback=feedback,
        ),
        "retry": _compact_binding(
            background=background,
            character=index.get("character_retry") or index.get("character_fail") or character_default,
            feedback=feedback,
            prop=prop,
        ),
        "reward": _compact_binding(
            background=background,
            character=index.get("character_reward") or index.get("character_success") or character_default,
            reward=feedback,
        ),
        "classroom_return": _compact_binding(
            background=background,
            character=index.get("character_reward") or index.get("character_success") or character_default,
            reward=feedback,
        ),
    }


def _asset_index(assets: list[Any]) -> dict[str, str]:
    index: dict[str, str] = {}
    for asset in assets:
        if not isinstance(asset, dict):
            continue
        asset_id = str(asset.get("asset_id") or "").strip()
        if not asset_id:
            continue
        asset_type = str(asset.get("type") or "").strip()
        runtime_usage = str(asset.get("runtime_usage") or "").strip()
        for key in (runtime_usage, asset_type, asset_id):
            if key and key not in index:
                index[key] = asset_id
        for alias in _runtime_usage_aliases(runtime_usage):
            if alias not in index:
                index[alias] = asset_id
    return index


def _compact_binding(**items: str | None) -> dict[str, str]:
    return {key: value for key, value in items.items() if value}


def _runtime_usage_aliases(runtime_usage: str) -> list[str]:
    aliases = {
        "character_idle": ["character_listen", "character_ready"],
        "character_miss": ["character_fail", "character_retry"],
        "character_win": ["character_success", "character_reward"],
    }
    return aliases.get(runtime_usage, [])


def _artifact_file_for(asset: dict[str, Any]) -> str:
    asset_id = str(asset.get("asset_id") or "generated_asset").strip() or "generated_asset"
    explicit = {
        "scene_background": "scene-background.png",
        "character_pose_sheet": "character-pose-sheet.png",
        "game_props_sheet": "game-props-sheet.png",
        "reward_feedback_sheet": "reward-feedback-sheet.png",
    }
    return explicit.get(asset_id, f"{asset_id.replace('_', '-')}.png")


def _ratio_for_size(size: str) -> str:
    try:
        width_text, height_text = size.lower().split("x", 1)
        width = int(width_text)
        height = int(height_text)
        if width > height:
            return "16:9"
        if width == height:
            return "1:1"
        return "9:16"
    except Exception:
        return "1:1"
