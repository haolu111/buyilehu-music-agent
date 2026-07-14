from __future__ import annotations

from typing import Any


def build_experience_script(
    *,
    gameplay_blueprint: dict[str, Any],
    proposal_card: dict[str, Any],
) -> dict[str, Any]:
    """Shape the player journey around a gameplay blueprint."""

    operation_type = str(gameplay_blueprint.get("operation_type") or "")
    rounds = gameplay_blueprint.get("rounds", []) if isinstance(gameplay_blueprint.get("rounds"), list) else []
    return {
        "version": "experience_script_v1",
        "opening_hook": _opening_hook(operation_type, gameplay_blueprint, proposal_card),
        "tutorial": {
            "enabled": True,
            "first_action_hint": _first_action_hint(operation_type),
            "assist_mode": _assist_mode(operation_type),
        },
        "progression": [
            {
                "round_id": item.get("id", f"round_{index + 1}"),
                "emotion": _round_emotion(index, len(rounds)),
                "reward": _round_reward(operation_type, index, len(rounds), gameplay_blueprint),
            }
            for index, item in enumerate(rounds)
            if isinstance(item, dict)
        ],
        "feedback_style": {
            "tone": "鼓励型",
            "failure_behavior": "保留学生当前答案，提示重听和修正，不做惩罚性否定。",
            "success_behavior": _success_behavior(operation_type),
        },
        "replay_hook": _replay_hook(operation_type),
        "closure_prompt": _closure_prompt(gameplay_blueprint),
    }


def _opening_hook(operation_type: str, blueprint: dict[str, Any], proposal_card: dict[str, Any]) -> str:
    if blueprint.get("scene_goal") and blueprint.get("main_object"):
        return f"{blueprint.get('scene_goal')}先听清音乐，再完成这次操作。"
    if operation_type == "melody_path_draw":
        return "旋律小路还没被画出来，先用耳朵找到它的方向。"
    if "beat" in operation_type:
        return "护盾正在呼吸，只有提前预判第 1 拍才能稳定充能。"
    if "rhythm" in operation_type:
        return "节奏回声来了，听清它，再把它完整还回来。"
    if "timbre" in operation_type:
        return "声音留下了线索，请用耳朵把真相找出来。"
    if "solfege" in operation_type:
        return "唱名靶已经亮起，先在心里唱准，再出手。"
    return proposal_card.get("learning_goal") or blueprint.get("prompt") or "先听，再开始挑战。"


def _first_action_hint(operation_type: str) -> str:
    if operation_type == "melody_path_draw":
        return "先听一遍，再在每一列点出一个格子。"
    if "beat" in operation_type:
        return "先让身体跟上稳定拍，再寻找目标拍位。"
    if "rhythm" in operation_type:
        return "先完整听一遍，不急着抢先拍。"
    return "先试听目标，再开始第一步操作。"


def _assist_mode(operation_type: str) -> str:
    if operation_type == "melody_path_draw":
        return "首关显示低干扰提示，帮助学生理解高低坐标。"
    if "beat" in operation_type:
        return "首关显示护盾收缩到最小的第 1 拍提示。"
    return "首关保留更多视觉提示，后续逐步减少。"


def _round_emotion(index: int, total: int) -> str:
    if index == 0:
        return "轻松上手"
    if index + 1 >= total:
        return "完成掌握"
    return "开始挑战"


def _round_reward(operation_type: str, index: int, total: int, blueprint: dict[str, Any] | None = None) -> str:
    if blueprint and blueprint.get("reward_loop") and index + 1 >= max(1, total):
        return str(blueprint.get("reward_loop"))
    if operation_type == "melody_path_draw":
        return ["小角色迈出第一步", "路线被点亮", "整条旋律小路完成"][min(index, 2)]
    if "beat" in operation_type:
        return ["护盾亮起", "震波连击", "护盾稳定"][min(index, 2)]
    if "rhythm" in operation_type:
        return ["第一段回声成功", "时间轴点亮", "节奏徽章完成"][min(index, 2)]
    return ["第一枚徽章", "进度升级", "挑战通关"][min(index, 2)]


def _success_behavior(operation_type: str) -> str:
    if operation_type == "melody_path_draw":
        return "点亮正确路线，并让角色沿路线前进。"
    if "beat" in operation_type:
        return "在第 1 拍同步充能，触发护盾震波并累计稳定连击。"
    return "给出清晰成功反馈，并立刻引向下一轮或课堂迁移。"


def _replay_hook(operation_type: str) -> str:
    if operation_type == "melody_path_draw":
        return "换一条旋律线，再来一次。"
    if "beat" in operation_type:
        return "换一种拍号，再充能一次。"
    return "换一组材料，再挑战一次。"


def _closure_prompt(blueprint: dict[str, Any]) -> str:
    transfer = blueprint.get("learning_transfer", {}) if isinstance(blueprint.get("learning_transfer"), dict) else {}
    return transfer.get("classroom_transfer") or blueprint.get("win_condition") or "说出你刚才听到的音乐依据。"
