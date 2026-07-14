from __future__ import annotations

from typing import Any


RHYTHM_MOUNTAIN_TEMPLATE: dict[str, Any] = {
    "id": "immersive_rhythm_mountain",
    "label": "沉浸式节奏闯关",
    "source_folder": "音乐闯关",
    "best_for": ["节奏识读", "稳拍敲击", "打击乐合奏", "力度渐强", "跟随音乐表现"],
    "avoid_for": ["纯演唱", "单纯音色听辨", "旋律接龙", "自由创作"],
    "logic": [
        "地图式关卡路径",
        "按顺序解锁",
        "听辨跟读",
        "稳拍敲击",
        "双乐器合奏跟打",
        "力度渐强表达",
        "通关后回看与重置",
    ],
    "threshold": 50,
}


def list_performance_templates() -> list[dict[str, Any]]:
    return [RHYTHM_MOUNTAIN_TEMPLATE]


def apply_performance_template_if_applicable(spec: dict[str, Any]) -> dict[str, Any]:
    enriched = dict(spec)
    performance = enriched.get("performance") if isinstance(enriched.get("performance"), dict) else {}
    if not performance.get("enabled"):
        return enriched

    score, reasons = _rhythm_mountain_score(enriched)
    selection = {
        "template_id": RHYTHM_MOUNTAIN_TEMPLATE["id"],
        "score": score,
        "threshold": RHYTHM_MOUNTAIN_TEMPLATE["threshold"],
        "matched": score >= RHYTHM_MOUNTAIN_TEMPLATE["threshold"],
        "reasons": reasons,
        "note": "只在节奏、打击乐、跟随音乐、力度渐强等表现目标足够匹配时启用。",
    }
    performance = dict(performance)
    performance["template_selection"] = selection
    if score < RHYTHM_MOUNTAIN_TEMPLATE["threshold"]:
        enriched["performance"] = performance
        return enriched

    target_skill = str(
        enriched.get("target_music_element")
        or performance.get("target_skill")
        or "节奏表现"
    )
    theme = str(performance.get("theme") or enriched.get("song_name") or "音乐闯关")
    levels = _adapt_rhythm_mountain_levels(performance.get("levels", []), target_skill, theme)
    performance.update(
        {
            "template_id": RHYTHM_MOUNTAIN_TEMPLATE["id"],
            "template_variant": RHYTHM_MOUNTAIN_TEMPLATE["id"],
            "template_label": RHYTHM_MOUNTAIN_TEMPLATE["label"],
            "source_logic": RHYTHM_MOUNTAIN_TEMPLATE["logic"],
            "stage_count": len(levels),
            "levels": levels,
            "target_skill": target_skill,
            "teacher_fit_note": "此模板适合把节奏、打击乐、力度或跟随音乐的表现目标做成逐级挑战；若课例重点转向演唱、旋律或音色，应改用其他表现模板。",
        }
    )
    enriched["performance"] = performance
    return enriched


def _adapt_rhythm_mountain_levels(raw_levels: Any, target_skill: str, theme: str) -> list[dict[str, Any]]:
    provided = [level for level in raw_levels if isinstance(level, dict)] if isinstance(raw_levels, list) else []
    defaults = [
        {
            "title": "第一关：听辨跟读",
            "goal": f"听出“{target_skill}”的基本节奏线索，并用拟声词稳定跟读。",
            "student_task": "先听示范，再用“咚、哒”等声音跟读节奏型。",
            "success_rule": "能连续跟读一遍目标节奏，并说出最明显的节奏特征。",
            "challenge_kind": "chant_readback",
            "pattern": ["咚", "哒", "哒", "咚"],
            "component": "节奏跟读卡",
            "unlock_reward": "解锁虚拟敲击垫",
        },
        {
            "title": "第二关：稳拍敲击",
            "goal": f"把听到的“{target_skill}”转化为稳定拍点。",
            "student_task": "跟随亮起的拍点敲击，保持速度稳定。",
            "success_rule": "在 8 个拍点中完成至少 6 次稳定敲击。",
            "challenge_kind": "steady_tap",
            "pattern": ["tap", "tap", "tap", "tap", "tap", "tap", "tap", "tap"],
            "component": "稳拍鼓垫",
            "unlock_reward": "解锁双乐器合奏",
        },
        {
            "title": "第三关：合奏跟打",
            "goal": f"听辨“{target_skill}”中的先后关系，并用两件乐器模仿。",
            "student_task": "观察鼓和镲的顺序，按提示完成合奏跟打。",
            "success_rule": "按正确顺序完成 6 次乐器回应。",
            "challenge_kind": "ensemble_follow",
            "pattern": ["drum", "drum", "cymbal", "drum", "cymbal", "drum"],
            "component": "鼓镲合奏垫",
            "unlock_reward": "解锁力度表现关",
        },
        {
            "title": "第四关：渐强表达",
            "goal": f"把“{target_skill}”进一步表现为有层次的音乐表达。",
            "student_task": "按弱到强的顺序完成力度路线，并说明这样处理的理由。",
            "success_rule": "能完成 p-mp-mf-f 的力度路线，并说出它怎样推动音乐情绪。",
            "challenge_kind": "dynamic_expression",
            "pattern": ["p", "mp", "mf", "f"],
            "component": "力度能量阶梯",
            "unlock_reward": "完成完整表现挑战",
        },
    ]

    adapted = []
    for index, default in enumerate(defaults):
        provided_level = provided[index] if index < len(provided) else {}
        adapted.append(
            {
                **default,
                "title": str(provided_level.get("title") or default["title"]),
                "goal": str(provided_level.get("goal") or default["goal"]),
                "student_task": str(provided_level.get("student_task") or default["student_task"]),
                "success_rule": str(provided_level.get("success_rule") or default["success_rule"]),
                "theme": theme,
                "level": index + 1,
            }
        )
    return adapted


def _rhythm_mountain_score(spec: dict[str, Any]) -> tuple[int, list[str]]:
    performance = spec.get("performance") if isinstance(spec.get("performance"), dict) else {}
    lesson_context = spec.get("lesson_context") if isinstance(spec.get("lesson_context"), dict) else {}
    levels = performance.get("levels") if isinstance(performance.get("levels"), list) else []
    haystack = " ".join(
        [
            str(spec.get("activity_type", "")),
            str(spec.get("title", "")),
            str(spec.get("subtitle", "")),
            str(spec.get("song_name", "")),
            str(spec.get("target_music_element", "")),
            str(spec.get("target_segment_task", "")),
            str(spec.get("target_segment_gameable_point", "")),
            str(performance.get("theme", "")),
            str(performance.get("target_skill", "")),
            str(lesson_context.get("target_music_element", "")),
            str(lesson_context.get("target_segment_task", "")),
            " ".join(str(level.get(key, "")) for level in levels for key in ("title", "goal", "student_task", "success_rule") if isinstance(level, dict)),
        ]
    )
    score = 0
    reasons: list[str] = []

    def add(points: int, reason: str) -> None:
        nonlocal score
        score += points
        reasons.append(reason)

    if spec.get("activity_type") in {"performance", "mixed"}:
        add(10, "活动类型是表现性活动。")
    if any(word in haystack for word in ["闯关", "关卡", "逐关", "通关"]):
        add(8, "存在逐关挑战需求。")
    if any(word in haystack for word in ["节奏", "节拍", "拍点", "稳拍", "时值"]):
        add(18, "目标包含节奏或拍点。")
    if any(word in haystack for word in ["打击", "敲击", "跟打", "拍手", "鼓", "镲"]):
        add(25, "任务需要打击乐或敲击表现。")
    if any(word in haystack for word in ["合奏", "声部", "先后关系", "配合"]):
        add(14, "任务包含合奏或声部配合。")
    if any(word in haystack for word in ["力度", "渐强", "渐弱", "强弱"]):
        add(14, "任务包含力度层次。")
    if any(word in haystack for word in ["山魔", "在山魔宫中", "魔宫"]):
        add(30, "曲目或情境与原模板高度相近。")

    if any(word in haystack for word in ["纯演唱", "合唱", "接唱", "模唱"]) and not any(word in haystack for word in ["节奏", "打击", "敲击"]):
        score -= 35
        reasons.append("主要是演唱任务，未体现节奏/打击乐闯关逻辑。")
    if any(word in haystack for word in ["音色听辨", "乐器音色", "旋律接龙", "音高飞行"]) and not any(word in haystack for word in ["节奏", "打击", "力度"]):
        score -= 25
        reasons.append("重点更适合其他模板，不强行套用节奏闯关。")

    return max(0, score), reasons
