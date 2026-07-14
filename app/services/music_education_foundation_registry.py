from __future__ import annotations

from copy import deepcopy
from typing import Any


CORE_COMPETENCY_SPECS: list[dict[str, Any]] = [
    {
        "competency_id": "aesthetic_perception",
        "label": "审美感知",
        "classroom_meaning": "听辨音乐情绪、速度、力度、音色、旋律特点，形成感受和判断。",
        "candidate_activities": ["听赏选择", "音色侦探", "主题再现", "情绪图卡"],
        "avoid": "只让学生抢答，不要求聆听依据。",
    },
    {
        "competency_id": "artistic_performance",
        "label": "艺术表现",
        "classroom_meaning": "用歌唱、演奏、律动、身体动作表现音乐。",
        "candidate_activities": ["分句跟唱", "节奏复刻", "强弱拍律动", "虚拟乐器演奏"],
        "avoid": "只点按钮得分，没有唱、奏、动。",
    },
    {
        "competency_id": "creative_practice",
        "label": "创意实践",
        "classroom_meaning": "用节奏、旋律、动作、图形谱进行简单创编。",
        "candidate_activities": ["节奏拼图", "五声创编", "身体打击编排", "问答句创作"],
        "avoid": "随机拼图但不校验音乐结构。",
    },
    {
        "competency_id": "cultural_understanding",
        "label": "文化理解",
        "classroom_meaning": "感受作品背景、民族音乐、乐器文化、生活情境。",
        "candidate_activities": ["乐器家族", "节日音乐", "民族乐器音色", "场景化欣赏"],
        "avoid": "做成百科问答，脱离音乐听觉体验。",
    },
]


STUDENT_PRACTICE_SPECS: list[dict[str, Any]] = [
    {
        "practice_id": "listen",
        "label": "听",
        "primary_classroom_meaning": "听情绪、速度、力度、音色、主题、段落。",
        "candidate_activities": ["听赏选择", "音色侦探", "主题再现"],
    },
    {
        "practice_id": "sing",
        "label": "唱",
        "primary_classroom_meaning": "模唱、接唱、分句唱、唱名唱。",
        "candidate_activities": ["分句跟唱", "缺词接唱", "唱名回声"],
    },
    {
        "practice_id": "play",
        "label": "奏",
        "primary_classroom_meaning": "用虚拟或实体乐器敲击或演奏。",
        "candidate_activities": ["音条琴挑战", "奥尔夫合奏", "强拍小鼓"],
    },
    {
        "practice_id": "move",
        "label": "动",
        "primary_classroom_meaning": "身体律动、拍手、跺脚、动作表现。",
        "candidate_activities": ["强弱拍律动", "身体打击编排"],
    },
    {
        "practice_id": "read_notation",
        "label": "读谱",
        "primary_classroom_meaning": "简谱、节奏谱、图形谱、简单五线谱。",
        "candidate_activities": ["简谱跟读", "节奏卡排序", "图形谱寻路"],
    },
    {
        "practice_id": "create",
        "label": "创编",
        "primary_classroom_meaning": "编节奏、编旋律、编动作、编伴奏。",
        "candidate_activities": ["节奏拼图", "五声造句", "问答句创作"],
    },
    {
        "practice_id": "evaluate",
        "label": "评价",
        "primary_classroom_meaning": "说依据、自评互评、听辨后表达。",
        "candidate_activities": ["三词说依据", "展示评价", "出口票"],
    },
    {
        "practice_id": "connect_culture",
        "label": "联系文化",
        "primary_classroom_meaning": "乐器、民歌、节日、地域风格。",
        "candidate_activities": ["乐器分类", "节日音乐包", "民族音色游戏"],
    },
]


MUSIC_ELEMENT_SPECS: list[dict[str, Any]] = [
    {"element_id": "steady_beat", "label": "稳定拍", "primary_range": "感受均匀拍点", "game_methods": ["跟拍", "行走", "敲击"], "grade_hint": "低段优先"},
    {"element_id": "rhythm", "label": "节奏", "primary_range": "四分、八分、休止、简单组合", "game_methods": ["节奏卡", "复刻", "接龙"], "grade_hint": "全学段"},
    {"element_id": "meter", "label": "节拍/拍号", "primary_range": "二拍子、三拍子、四拍子强弱", "game_methods": ["强拍点击", "律动圆圈"], "grade_hint": "低/中段"},
    {"element_id": "tempo", "label": "速度", "primary_range": "快、慢、渐快、渐慢", "game_methods": ["听赏选择", "动作变化"], "grade_hint": "全学段"},
    {"element_id": "dynamics", "label": "力度", "primary_range": "强、弱、渐强、渐弱", "game_methods": ["力度条", "动作幅度"], "grade_hint": "全学段"},
    {"element_id": "pitch", "label": "音高", "primary_range": "高低、级进、跳进", "game_methods": ["音高阶梯", "唱名打靶"], "grade_hint": "中/高段"},
    {"element_id": "melody", "label": "旋律", "primary_range": "上行、下行、重复、问答", "game_methods": ["旋律线", "唱名排序"], "grade_hint": "中/高段"},
    {"element_id": "timbre", "label": "音色", "primary_range": "人声/乐器、打击/吹奏/弹拨/拉弦", "game_methods": ["音色侦探", "乐器分类"], "grade_hint": "中/高段"},
    {"element_id": "form", "label": "曲式", "primary_range": "重复、对比、ABA、回旋", "game_methods": ["曲式寻宝", "段落排序"], "grade_hint": "高段优先"},
    {"element_id": "mood_image", "label": "情绪/形象", "primary_range": "欢快、优美、安静、活泼等", "game_methods": ["情绪图卡", "听赏投票"], "grade_hint": "低/中段"},
    {"element_id": "style_culture", "label": "风格/文化", "primary_range": "民族乐器、节日、地域音乐", "game_methods": ["场景化欣赏", "乐器文化"], "grade_hint": "中/高段"},
]


GRADE_BOUNDARY_SPECS: list[dict[str, Any]] = [
    {
        "grade_band": "lower_primary",
        "label": "小学低段",
        "learning_traits": "以感受、模仿、动作、图像为主。",
        "design_requirements": "少文字、大按钮、多听多动、即时反馈。",
        "avoid": "长说明、复杂规则、抽象术语。",
    },
    {
        "grade_band": "middle_primary",
        "label": "小学中段",
        "learning_traits": "可以进行简单听辨、唱名、节奏组合、小组合作。",
        "design_requirements": "可加入卡片排序、分类、简短理由。",
        "avoid": "过度竞技、过长关卡。",
    },
    {
        "grade_band": "upper_primary",
        "label": "小学高段",
        "learning_traits": "可以读简单谱、理解结构、进行创编和评价。",
        "design_requirements": "可加入曲式、简谱、五声创编、评价量规。",
        "avoid": "高中化乐理、复杂和声。",
    },
]


TEACHING_STAGE_SPECS: list[dict[str, Any]] = [
    {"stage_id": "lesson_opening", "label": "导入", "music_purpose": "激发兴趣、唤起经验、初步感受。", "candidate_activities": ["听一遍投票", "情绪图卡", "导入钩子"], "avoid": "复杂闯关。"},
    {"stage_id": "first_listening", "label": "初听/感受", "music_purpose": "建立整体印象。", "candidate_activities": ["听赏选择", "主题动作"], "avoid": "立即讲知识点。"},
    {"stage_id": "relisten_inquiry", "label": "复听/探究", "music_purpose": "抓音乐要素和证据。", "candidate_activities": ["音色侦探", "主题再现", "曲式排序"], "avoid": "无依据抢答。"},
    {"stage_id": "singing_learning", "label": "学唱", "music_purpose": "分句、模唱、难点解决。", "candidate_activities": ["分句循环", "缺词接唱", "唱名回声"], "avoid": "只看歌词不听唱。"},
    {"stage_id": "rhythm_movement", "label": "律动/节奏", "music_purpose": "稳拍、强弱、节奏型。", "candidate_activities": ["节奏复刻", "强拍守卫", "身体打击"], "avoid": "只点屏不动身体。"},
    {"stage_id": "instrumental", "label": "器乐", "music_purpose": "伴奏、合奏、声部配合。", "candidate_activities": ["虚拟乐器", "奥尔夫合奏"], "avoid": "无节拍约束地乱敲。"},
    {"stage_id": "creation", "label": "创编", "music_purpose": "节奏、旋律、动作创造。", "candidate_activities": ["节奏拼图", "五声造句", "图形谱"], "avoid": "完全随机无音乐规则。"},
    {"stage_id": "showcase_assessment", "label": "展示评价", "music_purpose": "表现、倾听、表达依据。", "candidate_activities": ["小组展示", "同伴评价", "出口票"], "avoid": "只排名不反馈。"},
]


def list_core_competency_specs() -> list[dict[str, Any]]:
    return deepcopy(CORE_COMPETENCY_SPECS)


def list_student_practice_specs() -> list[dict[str, Any]]:
    return deepcopy(STUDENT_PRACTICE_SPECS)


def list_music_element_specs() -> list[dict[str, Any]]:
    return deepcopy(MUSIC_ELEMENT_SPECS)


def list_grade_boundary_specs() -> list[dict[str, Any]]:
    return deepcopy(GRADE_BOUNDARY_SPECS)


def list_teaching_stage_specs() -> list[dict[str, Any]]:
    return deepcopy(TEACHING_STAGE_SPECS)


def music_education_foundation_catalog() -> dict[str, Any]:
    return validate_foundation_catalog(
        {
            "version": "music_education_foundation_catalog_v1",
            "audience": "primary_school",
            "core_competencies": list_core_competency_specs(),
            "student_practices": list_student_practice_specs(),
            "music_elements": list_music_element_specs(),
            "grade_boundaries": list_grade_boundary_specs(),
            "teaching_stages": list_teaching_stage_specs(),
        }
    )


def validate_foundation_catalog(catalog: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(catalog, dict):
        raise ValueError("music education foundation catalog must be a dict")
    if catalog.get("version") != "music_education_foundation_catalog_v1":
        raise ValueError("music education foundation catalog version must be music_education_foundation_catalog_v1")
    if catalog.get("audience") != "primary_school":
        raise ValueError("music education foundation catalog audience must be primary_school")
    for field in ("core_competencies", "student_practices", "music_elements", "grade_boundaries", "teaching_stages"):
        if not isinstance(catalog.get(field), list) or not catalog[field]:
            raise ValueError(f"music education foundation catalog {field} must be a non-empty list")
    _validate_unique(catalog["core_competencies"], "competency_id")
    _validate_unique(catalog["student_practices"], "practice_id")
    _validate_unique(catalog["music_elements"], "element_id")
    _validate_unique(catalog["grade_boundaries"], "grade_band")
    _validate_unique(catalog["teaching_stages"], "stage_id")
    return deepcopy(catalog)


def _validate_unique(items: list[dict[str, Any]], key: str) -> None:
    seen: set[str] = set()
    for item in items:
        value = str(item.get(key) or "")
        if not value:
            raise ValueError(f"foundation item missing {key}")
        if value in seen:
            raise ValueError(f"duplicate foundation item {key}: {value}")
        seen.add(value)
