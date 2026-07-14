from __future__ import annotations

from typing import Any

from app.services.component_library import get_component_spec


def build_component_capability_plan(
    *,
    game_design: dict[str, Any],
    original_game_concept: dict[str, Any],
    config: dict[str, Any],
) -> dict[str, Any]:
    """Map original game requirements to already registered classroom components."""

    mechanic = game_design.get("mechanic_contract") if isinstance(game_design.get("mechanic_contract"), dict) else {}
    requirement_text = _requirement_text(mechanic, original_game_concept, config)
    requirements = [
        {
            "capability_id": "audio_playback",
            "requirement": "学生必须先听到教案音乐材料，并能重听。",
            "component_id": "audio_player",
            "runtime_binding": ["audio-manifest.json", "runtime-config.audio_policy"],
        },
        {
            "capability_id": "game_status_hud",
            "requirement": "投屏和学生端必须显示关卡、进度、当前音乐目标。",
            "component_id": "game_hud",
            "runtime_binding": ["level-curve.json", "runtime-config.level_count"],
        },
        {
            "capability_id": "teacher_control",
            "requirement": "教师必须能开始、暂停、重置、调速、重听和显隐提示。",
            "component_id": "teacher_control_bar",
            "runtime_binding": ["teacher-control-config.json", "lesson-case-teacher-control"],
        },
        {
            "capability_id": "reward_progress",
            "requirement": "奖励必须回到音乐原因和下一步课堂练习。",
            "component_id": "reward_panel",
            "runtime_binding": ["game-state-machine.json.reward", "runtime-config.classroom_return"],
        },
    ]
    if _needs_meter_or_tap(requirement_text):
        requirements.extend(
            [
                {
                    "capability_id": "meter_visualization",
                    "requirement": "二拍子、强弱拍和拍点轨道必须走已登记节拍组件。",
                    "component_id": "meter_track",
                    "runtime_binding": ["music-truth.json.material", "runtime-config.bpm"],
                },
                {
                    "capability_id": "timing_feedback",
                    "requirement": "抢拍、拖拍、漏拍必须走统一敲击反馈和误差窗口。",
                    "component_id": "tap_feedback",
                    "runtime_binding": ["music_truth.judgement_windows", "music_truth.error_categories"],
                },
            ]
        )
    if _needs_choice_or_drag(requirement_text):
        requirements.extend(
            [
                {
                    "capability_id": "choice_input",
                    "requirement": "听辨选择必须先听后选并保留音乐依据。",
                    "component_id": "answer_choice_grid",
                    "runtime_binding": ["music-truth.json.answers", "runtime-config.student_actions"],
                },
                {
                    "capability_id": "drag_or_order_input",
                    "requirement": "拖拽、排序、拼接类任务必须走已登记操作板。",
                    "component_id": "drag_sort_board",
                    "runtime_binding": ["level-curve.json.levels", "game-state-machine.json.student_action"],
                },
            ]
        )

    matches: list[dict[str, Any]] = []
    missing: list[dict[str, str]] = []
    runtime_bindings: dict[str, list[str]] = {}
    quality_gates: set[str] = set()
    for requirement in requirements:
        component_id = str(requirement["component_id"])
        try:
            spec = get_component_spec(component_id)
        except ValueError:
            missing.append(
                {
                    "capability_id": str(requirement["capability_id"]),
                    "component_id": component_id,
                    "reason": "component_not_registered",
                }
            )
            continue
        bindings = [str(item) for item in requirement.get("runtime_binding", [])]
        runtime_bindings[component_id] = bindings
        quality_gates.update(str(gate) for gate in spec.get("quality_gates", []) if gate)
        matches.append(
            {
                "capability_id": str(requirement["capability_id"]),
                "requirement": str(requirement["requirement"]),
                "registered_component_id": component_id,
                "registered_component": True,
                "component_role": str(spec.get("role") or ""),
                "runtime": str(spec.get("runtime") or ""),
                "student_actions": [str(action) for action in spec.get("student_actions", [])],
                "music_elements": [str(element) for element in spec.get("music_elements", [])],
                "teacher_controls": [str(control) for control in spec.get("teacher_controls", [])],
                "quality_gates": [str(gate) for gate in spec.get("quality_gates", [])],
                "runtime_binding": bindings,
                "called_by_template_ids": [str(template_id) for template_id in spec.get("called_by_template_ids", [])],
            }
        )
    return {
        "component_registry_ref": "app/services/component_library.py",
        "required_capabilities": [str(item["capability_id"]) for item in requirements],
        "capability_matches": matches,
        "missing_required_capabilities": missing,
        "runtime_bindings": runtime_bindings,
        "component_quality_gates": sorted(quality_gates),
    }


def _requirement_text(
    mechanic: dict[str, Any],
    original_game_concept: dict[str, Any],
    config: dict[str, Any],
) -> str:
    pieces: list[str] = []
    for value in (
        mechanic.get("operation"),
        mechanic.get("student_action"),
        mechanic.get("mechanic_id"),
        original_game_concept.get("music_learning_target"),
        original_game_concept.get("core_metaphor"),
        config.get("interaction_model"),
        config.get("music_concept"),
    ):
        if value:
            pieces.append(str(value))
    loop = original_game_concept.get("student_loop")
    if isinstance(loop, list):
        pieces.extend(str(item) for item in loop)
    return " ".join(pieces).lower()


def _needs_meter_or_tap(requirement_text: str) -> bool:
    tokens = ["tap", "beat", "meter", "rhythm", "拍", "节拍", "强弱", "二拍子", "强拍", "弱拍", "节奏"]
    return any(token in requirement_text for token in tokens)


def _needs_choice_or_drag(requirement_text: str) -> bool:
    tokens = ["choice", "choose", "drag", "order", "match", "select", "选择", "拖拽", "排序", "匹配", "听辨"]
    return any(token in requirement_text for token in tokens)
