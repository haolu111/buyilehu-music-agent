# 检查活动是否符合音乐教育目标和年级要求
from __future__ import annotations

from copy import deepcopy
from typing import Any


CORE_COMPETENCIES = ("审美感知", "艺术表现", "创意实践", "文化理解")

MUSIC_PRACTICES = (
    "listen",
    "sing",
    "read",
    "tap",
    "move",
    "play",
    "arrange",
    "choose",
    "match",
    "classify",
    "order",
    "create",
    "revise",
    "cooperate",
    "perform",
    "assess",
    "explain",
)

MUSIC_ELEMENTS = (
    "稳定拍",
    "节奏",
    "休止",
    "节拍",
    "拍号",
    "强弱",
    "速度",
    "力度",
    "音高",
    "唱名",
    "识谱",
    "图形谱",
    "旋律",
    "乐句",
    "歌词",
    "音色",
    "乐器",
    "声部",
    "乐器家族",
    "发声方式",
    "曲式",
    "主题",
    "重复",
    "对比",
    "再现",
    "情绪",
    "五声音阶",
    "创编结构",
    "合作",
    "评价",
)

GRADE_BANDS = ("lower_primary", "middle_primary", "upper_primary")

REQUIRED_ALIGNMENT_FIELDS = (
    "primary_competency",
    "student_practices",
    "music_elements",
    "teaching_stages",
    "grade_fit",
    "pedagogy_notes",
)
MUSIC_LEARNING_PATH_KEYS = ("experience", "performance", "understanding", "transfer_or_creation")


def validate_music_education_alignment(
    alignment: dict[str, Any],
    *,
    activity_id: str,
    allowed_practices: list[str],
    allowed_teaching_stages: list[str],
    grade_bands: list[str],
) -> dict[str, Any]:
    if not isinstance(alignment, dict):
        raise ValueError(f"{activity_id} education_alignment must be a dict")
    missing = [field for field in REQUIRED_ALIGNMENT_FIELDS if not alignment.get(field)]
    if missing:
        raise ValueError(f"{activity_id} education_alignment missing fields: {', '.join(missing)}")

    primary = alignment.get("primary_competency")
    if primary not in CORE_COMPETENCIES:
        raise ValueError(f"{activity_id} primary_competency must be one of {', '.join(CORE_COMPETENCIES)}")

    secondary = alignment.get("secondary_competency")
    if secondary and secondary not in CORE_COMPETENCIES:
        raise ValueError(f"{activity_id} secondary_competency must be one of {', '.join(CORE_COMPETENCIES)}")

    practices = _string_list(alignment.get("student_practices"), f"{activity_id} student_practices")
    unknown_practices = [practice for practice in practices if practice not in MUSIC_PRACTICES]
    if unknown_practices:
        raise ValueError(f"{activity_id} has unknown music practices: {', '.join(unknown_practices)}")
    not_declared = [practice for practice in practices if practice not in allowed_practices]
    if not_declared:
        raise ValueError(f"{activity_id} education practices not declared on activity: {', '.join(not_declared)}")

    elements = _string_list(alignment.get("music_elements"), f"{activity_id} music_elements")
    unknown_elements = [element for element in elements if element not in MUSIC_ELEMENTS]
    if unknown_elements:
        raise ValueError(f"{activity_id} has unknown music elements: {', '.join(unknown_elements)}")

    stages = _string_list(alignment.get("teaching_stages"), f"{activity_id} teaching_stages")
    not_declared_stages = [stage for stage in stages if stage not in allowed_teaching_stages]
    if not_declared_stages:
        raise ValueError(f"{activity_id} education stages not declared on activity: {', '.join(not_declared_stages)}")

    fit = alignment.get("grade_fit")
    if not isinstance(fit, dict):
        raise ValueError(f"{activity_id} grade_fit must be a dict")
    missing_grade_fit = [grade for grade in grade_bands if grade not in fit or not str(fit.get(grade) or "").strip()]
    if missing_grade_fit:
        raise ValueError(f"{activity_id} grade_fit missing declared grade bands: {', '.join(missing_grade_fit)}")
    unknown_grade_fit = [grade for grade in fit if grade not in GRADE_BANDS]
    if unknown_grade_fit:
        raise ValueError(f"{activity_id} grade_fit has unknown grade bands: {', '.join(unknown_grade_fit)}")

    notes = _string_list(alignment.get("pedagogy_notes"), f"{activity_id} pedagogy_notes")
    if len(notes) < 2:
        raise ValueError(f"{activity_id} pedagogy_notes must include at least two music teaching notes")
    _validate_music_pedagogy_relationships(
        activity_id=activity_id,
        primary=primary,
        practices=practices,
        elements=elements,
        stages=stages,
    )

    validated = deepcopy(alignment)
    validated["music_learning_path"] = _music_learning_path(validated)
    validated["pedagogy_guardrails"] = _pedagogy_guardrails(validated)
    return validated


def _validate_music_pedagogy_relationships(
    *,
    activity_id: str,
    primary: str,
    practices: list[str],
    elements: list[str],
    stages: list[str],
) -> None:
    practice_set = set(practices)
    element_set = set(elements)
    stage_set = set(stages)

    if primary == "艺术表现" and not practice_set.intersection({"sing", "play", "tap", "move", "perform", "read"}):
        raise ValueError(f"{activity_id} 艺术表现 must include singing, playing, tapping, movement, reading, or performance")
    if primary == "审美感知" and not practice_set.intersection({"listen", "choose", "explain", "assess"}):
        raise ValueError(f"{activity_id} 审美感知 must include listening, choosing, explaining, or assessing")
    if primary == "创意实践" and not practice_set.intersection({"create", "revise", "arrange"}):
        raise ValueError(f"{activity_id} 创意实践 must include create, revise, or arrange")
    if primary == "文化理解" and not practice_set.intersection({"listen", "classify", "explain"}):
        raise ValueError(f"{activity_id} 文化理解 must include listening, classifying, or explaining")

    listening_elements = {"情绪", "音色", "乐器", "乐器家族", "发声方式", "曲式", "重复", "对比"}
    listening_stages = {"欣赏", "初听", "复听", "文化理解"}
    if (element_set.intersection(listening_elements) or stage_set.intersection(listening_stages)) and "listen" not in practice_set:
        raise ValueError(f"{activity_id} listening, timbre, form, or culture activities must start from listen")

    if element_set.intersection({"乐句", "旋律", "歌词"}) and "学唱" in stage_set:
        if "listen" not in practice_set or not practice_set.intersection({"sing", "read"}):
            raise ValueError(f"{activity_id} singing activities must combine listening with singing or lyrics reading")

    if element_set.intersection({"稳定拍", "节奏", "休止", "节拍", "拍号", "强弱"}) and not practice_set.intersection(
        {"tap", "move", "play", "read", "create", "arrange"}
    ):
        raise ValueError(f"{activity_id} rhythm and meter activities must include embodied or performed music practice")

    if element_set.intersection({"乐器家族", "发声方式"}) and "classify" not in practice_set:
        raise ValueError(f"{activity_id} instrument family activities must include classify")


def _music_learning_path(alignment: dict[str, Any]) -> dict[str, str]:
    path = alignment.get("music_learning_path") if isinstance(alignment.get("music_learning_path"), dict) else {}
    if path:
        missing_steps = [key for key in MUSIC_LEARNING_PATH_KEYS if not str(path.get(key) or "").strip()]
        if missing_steps:
            raise ValueError(f"music_learning_path missing steps: {', '.join(missing_steps)}")
        return {key: str(path[key]).strip() for key in MUSIC_LEARNING_PATH_KEYS}

    practices = _string_list(alignment.get("student_practices"), "student_practices")
    elements = _string_list(alignment.get("music_elements"), "music_elements")
    focus = "、".join(elements[:3])
    if "稳定拍" in elements:
        experience = "学生先听稳定拍和强弱变化，用身体感受音乐脉动。"
    elif "情绪" in elements or "音色" in elements or "曲式" in elements:
        experience = f"学生先完整聆听音乐，感受{focus}。"
    elif "乐句" in elements or "歌词" in elements:
        experience = f"学生先听范唱或片段，感受{focus}。"
    else:
        experience = f"学生先通过听觉体验{focus}。"

    performance = _performance_step(practices, focus)
    understanding = f"学生用音乐词或动作说明自己听到、唱到、奏到的{focus}。"
    transfer = _transfer_step(practices, focus)
    return {
        "experience": experience,
        "performance": performance,
        "understanding": understanding,
        "transfer_or_creation": transfer,
    }


def _pedagogy_guardrails(alignment: dict[str, Any]) -> dict[str, str]:
    practices = _string_list(alignment.get("student_practices"), "student_practices")
    elements = _string_list(alignment.get("music_elements"), "music_elements")
    primary = str(alignment.get("primary_competency") or "")
    focus = "、".join(elements[:3])
    return {
        "curriculum_basis": "小学音乐活动必须服务审美感知、艺术表现、创意实践或文化理解，且通过听、唱、奏、动、读、创、评等音乐实践达成。",
        "not_generic_game": f"本活动必须围绕{focus}设计反馈，不能只用点击、得分、闯关替代音乐学习。",
        "teacher_role": "教师保留调速、提示、重置和确认权；儿童歌唱、展示、创编等高噪声或主观任务优先教师确认。",
        "practice_requirement": f"{primary}必须落到学生实际音乐行为：{', '.join(practices)}。",
    }


def _performance_step(practices: list[str], focus: str) -> str:
    if "sing" in practices:
        return f"学生用模唱、分句演唱或歌词朗读表现{focus}。"
    if "play" in practices:
        return f"学生用虚拟乐器或课堂打击乐表现{focus}。"
    if "tap" in practices or "move" in practices:
        return f"学生用拍击、律动或身体动作表现{focus}。"
    if "match" in practices or "order" in practices or "choose" in practices:
        return f"学生通过选择、匹配或排序表达对{focus}的听辨结果。"
    return f"学生完成与{focus}对应的音乐实践任务。"


def _transfer_step(practices: list[str], focus: str) -> str:
    if "create" in practices or "revise" in practices:
        return f"学生在规则限制内创编、回放并修改自己的{focus}材料。"
    if "cooperate" in practices or "perform" in practices:
        return f"学生把{focus}迁移到小组合作、展示或同伴评价中。"
    if "assess" in practices or "explain" in practices:
        return f"学生用一句音乐依据完成自评、互评或课堂出口表达。"
    return f"学生把{focus}带回歌曲演唱、欣赏复听或下一步课堂任务。"


def _string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{label} must be a non-empty list")
    items = [str(item or "").strip() for item in value]
    if not all(items):
        raise ValueError(f"{label} must not contain empty values")
    return items
