from __future__ import annotations

from copy import deepcopy
from typing import Any


def build_level_curve(
    instance: dict[str, Any],
    *,
    music_truth: dict[str, Any] | None = None,
) -> dict[str, Any]:
    config = instance.get("config") if isinstance(instance.get("config"), dict) else {}
    template_id = str(instance.get("template_id") or config.get("template_id") or "").strip()
    if template_id != "rhythm_echo_core":
        return _generic_template_level_curve(template_id, config, music_truth or {})
    round_count = int(config.get("round_count") or 6)
    bpm = int(config.get("bpm") or 92)
    steps = _truth_steps(music_truth or {}, config)
    levels = []
    for index in range(round_count):
        level_no = index + 1
        levels.append(
            {
                "level": level_no,
                "music_focus": "稳定拍点" if level_no == 1 else "节奏顺序与时值",
                "bpm": min(bpm + index * 2, 132),
                "pattern_steps": deepcopy(steps),
                "hint_amount": "high" if level_no == 1 else "medium" if level_no <= 3 else "low",
                "relisten_limit": 2 if level_no <= 2 else 1,
                "teaching_reason": "先保证低年级能模仿成功，再逐步减少提示并提高反应要求。",
            }
        )
    return {
        "version": "level_curve_v1",
        "template_id": "rhythm_echo_core",
        "difficulty_axes": ["BPM", "节奏密度", "提示量", "重听次数"],
        "levels": levels,
    }


def _truth_steps(music_truth: dict[str, Any], config: dict[str, Any]) -> list[str]:
    answers = music_truth.get("answers") if isinstance(music_truth.get("answers"), list) else []
    first = answers[0] if answers and isinstance(answers[0], dict) else {}
    steps = first.get("pattern_steps") if isinstance(first.get("pattern_steps"), list) else []
    if steps:
        return [str(step) for step in steps]
    return [str(step) for step in config.get("pattern_steps", ["quarter", "quarter"])]


def _generic_template_level_curve(template_id: str, config: dict[str, Any], music_truth: dict[str, Any]) -> dict[str, Any]:
    bpm = int(config.get("bpm") or 88)
    material = str(music_truth.get("material") or config.get("music_material") or "教案音乐材料")
    focus = str(music_truth.get("music_learning_target") or config.get("music_concept") or _focus_for_template(template_id))
    levels = [
        {
            "level": 1,
            "music_focus": focus,
            "bpm": bpm,
            "hint_amount": "high",
            "student_task": "先理解游戏规则，只处理最清楚的一次音乐目标。",
            "music_material": "规则示范片段",
            "teaching_reason": "低年级先建立听辨和操作对应关系，避免一开始被速度和画面干扰。",
        },
        {
            "level": 2,
            "music_focus": focus,
            "bpm": bpm,
            "hint_amount": "medium",
            "student_task": f"进入{material}，按游戏目标完成听辨和操作。",
            "music_material": material,
            "teaching_reason": "把游戏行为绑定回教案音乐材料，防止只玩规则不听音乐。",
        },
        {
            "level": 3,
            "music_focus": focus,
            "bpm": min(bpm + 4, 132),
            "hint_amount": "low",
            "student_task": "减少提示，连续完成多个音乐目标并根据错误反馈调整。",
            "music_material": material,
            "teaching_reason": "通过提示递减和连续判断形成稳定音乐感知。",
        },
        {
            "level": 4,
            "music_focus": "课堂迁移与回扣",
            "bpm": bpm,
            "hint_amount": "teacher_led",
            "student_task": "离开游戏提示，回到唱、拍、动或小组合作表现。",
            "music_material": material,
            "teaching_reason": "把游戏中的成功经验迁移回真实音乐课堂行为。",
        },
    ]
    return {
        "version": "level_curve_v1",
        "template_id": template_id,
        "difficulty_axes": ["提示量", "连续判断次数", "速度", "课堂迁移"],
        "levels": levels,
    }


def _focus_for_template(template_id: str) -> str:
    labels = {
        "beat_guardian_core": "强弱拍和稳定拍感",
        "pitch_ladder_core": "音高方向和旋律走向",
        "solfege_target_core": "唱名听辨和目标音定位",
        "timbre_detective_core": "音色听辨和声音证据",
        "form_treasure_core": "乐句结构和曲式段落",
        "composition_puzzle_core": "节奏/旋律材料组合",
    }
    return labels.get(template_id, "当前音乐学习目标")
