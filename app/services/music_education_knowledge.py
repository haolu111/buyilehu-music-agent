from __future__ import annotations

import re
from typing import Any


CURRICULUM_ANCHORS = [
    {
        "id": "core_literacy",
        "title": "艺术核心素养",
        "points": ["审美感知", "艺术表现", "创意实践", "文化理解"],
        "use_in_generation": "每个工具至少覆盖其中 2 个维度，并把评价反馈写成学生能理解的课堂语言。",
        "source": "教育部 2022 年版义务教育艺术课程相关公开信息。",
    },
    {
        "id": "integrated_art",
        "title": "艺术课程综合化",
        "points": ["音乐可与律动、戏剧、视觉图形、故事情境结合", "活动设计应服务育人目标，不只是技能练习"],
        "use_in_generation": "低年级优先唱游、律动和图形谱；高年级可增加风格、文化和创作表达。",
        "source": "教育部 2022 年版义务教育课程方案和艺术课程相关公开信息。",
    },
    {
        "id": "stage_structure",
        "title": "义务教育阶段结构",
        "points": ["1-2 年级偏综合艺术与唱游", "3-7 年级以音乐、美术为主并融入综合艺术", "8-9 年级可拓展舞蹈、戏剧、影视等方向"],
        "use_in_generation": "按照学段控制理论深度、操作复杂度和评价方式。",
        "source": "教育部公开答复和课程标准宣传材料。",
    },
]


GRADE_PROFILES = {
    "lower_primary": {
        "label": "小学低年级",
        "grade_terms": ["一年级", "二年级", "1年级", "2年级", "小学低年级"],
        "abilities": ["稳定拍感", "模仿短节奏", "听辨强弱快慢", "用动作表现音乐情绪", "跟唱短句"],
        "avoid": ["长篇文字说明", "抽象调式理论", "复杂多声部", "过长关卡"],
        "interaction": ["大按钮", "动物或故事角色", "动作模仿", "唱游", "即时鼓励"],
        "assessment": ["能跟随拍点", "能用动作回应", "能说出快慢强弱等直观感受"],
    },
    "middle_primary": {
        "label": "小学中年级",
        "grade_terms": ["三年级", "四年级", "3年级", "4年级", "小学中年级", "四年级"],
        "abilities": ["识别常见节奏型", "听辨主题动机", "模唱或接龙短旋律", "理解五声音阶初步色彩", "小组合作表现"],
        "avoid": ["一次呈现过多音乐概念", "过度依赖文字评价", "没有示范就要求创作"],
        "interaction": ["关卡地图", "节奏模仿", "旋律接龙", "拖拽排序", "图形谱提示"],
        "assessment": ["节奏稳定", "主题辨认", "合作参与", "能用简单音乐词汇解释选择"],
    },
    "upper_primary": {
        "label": "小学高年级",
        "grade_terms": ["五年级", "六年级", "5年级", "6年级", "小学高年级"],
        "abilities": ["比较音乐要素变化", "理解乐句结构", "进行简单变奏", "尝试二声部或声部轮换", "说明创作意图"],
        "avoid": ["只做听辨不迁移", "缺少创作展示", "评价标准过于模糊"],
        "interaction": ["分组创编", "双声部网格", "结构反馈", "作品展示", "同伴评价"],
        "assessment": ["结构完整", "素材使用合理", "表现有层次", "能解释音乐处理理由"],
    },
    "middle_school": {
        "label": "初中",
        "grade_terms": ["初中", "七年级", "八年级", "九年级", "7年级", "8年级", "9年级"],
        "abilities": ["分析风格与文化背景", "比较不同版本", "参与合奏或编创", "使用基本音乐术语", "形成审美判断"],
        "avoid": ["活动幼稚化", "只给游戏不讲音乐依据", "缺少文化理解"],
        "interaction": ["风格实验室", "版本比较", "小组编配", "术语卡片", "展示辩护"],
        "assessment": ["音乐术语准确", "风格判断有依据", "合作编创有效", "文化理解具体"],
    },
    "high_school": {
        "label": "高中",
        "grade_terms": ["高中", "高一", "高二", "高三"],
        "abilities": ["深入赏析", "跨文化比较", "较完整的创编与表演设计", "批判性审美表达"],
        "avoid": ["过度卡通化", "只停留在操作层面", "缺少探究问题"],
        "interaction": ["专题探究", "作品分析", "编创工作坊", "展示评价量规"],
        "assessment": ["观点清晰", "证据充分", "表现与分析结合", "能联系文化语境"],
    },
}


REPERTOIRE_LIBRARY = {
    "茉莉花": {
        "title": "茉莉花",
        "tags": ["中国民歌", "五声音阶", "江南民歌", "旋律优美"],
        "teaching_points": ["五声音阶色彩", "级进旋律", "民歌流传与地域版本", "柔美连贯的演唱气息"],
        "activity_suggestions": ["主题听辨", "五声音阶旋律接龙", "不同音色对比", "民歌风格小组展示"],
        "cautions": ["避免只讲背景不让学生听辨主题", "低年级活动要把五声音阶转成可操作素材"],
    },
    "小小虫": {
        "title": "小小虫",
        "tags": ["儿童歌曲", "节奏模仿", "律动"],
        "teaching_points": ["稳定拍感", "短句模唱", "动作与节奏对应", "轻快情绪"],
        "activity_suggestions": ["昆虫角色节奏卡", "问答模唱", "动作接龙", "节奏密度变化聆听"],
        "cautions": ["任务时长要短", "反馈要直观"],
    },
    "彼得与狼": {
        "title": "彼得与狼",
        "tags": ["管弦乐", "音色", "角色主题"],
        "teaching_points": ["乐器音色辨认", "角色主题", "叙事音乐", "管弦乐队"],
        "activity_suggestions": ["角色音色匹配", "主题卡牌排序", "故事段落听辨"],
        "cautions": ["避免一次介绍过多乐器", "先听角色主题再讲乐器名称"],
    },
    "在山魔王的宫殿里": {
        "title": "在山魔王的宫殿里",
        "tags": ["速度渐快", "力度渐强", "重复动机", "管弦乐"],
        "teaching_points": ["速度与力度变化", "重复动机", "紧张情绪", "渐强渐快的结构"],
        "activity_suggestions": ["速度力度曲线", "身体律动渐强", "动机叠加小游戏"],
        "cautions": ["引导学生说出变化依据，而不只说可怕或刺激"],
    },
}


def knowledge_context_for_need(need: str, spec: dict[str, Any] | None = None) -> dict[str, Any]:
    grade_profile = grade_profile_for_text(_grade_text(need, spec))
    repertoire = repertoire_for_text(need, spec)
    return {
        "grade_profile": grade_profile,
        "curriculum_anchors": CURRICULUM_ANCHORS,
        "repertoire": repertoire,
        "generation_guidance": build_generation_guidance(grade_profile, repertoire, spec),
    }


def compact_prompt_context(need: str, spec: dict[str, Any] | None = None) -> dict[str, Any]:
    context = knowledge_context_for_need(need, spec)
    profile = context["grade_profile"]
    repertoire = context["repertoire"]
    return {
        "grade": {
            "label": profile["label"],
            "abilities": profile["abilities"][:5],
            "avoid": profile["avoid"][:4],
            "interaction": profile["interaction"][:5],
            "assessment": profile["assessment"][:4],
        },
        "curriculum": [
            {
                "title": anchor["title"],
                "points": anchor["points"],
                "use": anchor["use_in_generation"],
            }
            for anchor in CURRICULUM_ANCHORS
        ],
        "repertoire": repertoire,
        "guidance": context["generation_guidance"],
    }


def evaluate_music_education_fit(spec: dict[str, Any]) -> dict[str, Any]:
    context = knowledge_context_for_need(spec.get("title", "") + spec.get("subtitle", ""), spec)
    profile = context["grade_profile"]
    repertoire = context["repertoire"]
    activity_type = spec.get("activity_type", "mixed")
    checks: list[dict[str, Any]] = []

    _add_fit_check(
        checks,
        "grade_interaction_fit",
        "交互复杂度匹配学段",
        _interaction_fits_grade(spec, profile),
        f"{profile['label']}需要更直观、分步的操作，当前交互可能偏复杂或偏抽象。",
        "减少同时出现的概念，加入示范、图形谱、大按钮或分关卡引导。",
        warn_only=True,
    )
    _add_fit_check(
        checks,
        "core_literacy_coverage",
        "覆盖艺术核心素养",
        _core_literacy_coverage(spec) >= 2,
        "当前设计对审美感知、艺术表现、创意实践、文化理解的覆盖不足。",
        "至少补充听辨/表现/创作/文化说明中的两个维度。",
        warn_only=True,
    )
    if repertoire:
        _add_fit_check(
            checks,
            "repertoire_teaching_points",
            "体现曲目教学重点",
            _mentions_any(spec, repertoire.get("teaching_points", []) + repertoire.get("tags", [])),
            f"未明显体现《{repertoire['title']}》的曲目特点。",
            f"加入 {repertoire['teaching_points'][0]} 或 {repertoire['activity_suggestions'][0]}。",
            warn_only=True,
        )
    if activity_type == "performance":
        levels = spec.get("performance", {}).get("levels", [])
        _add_fit_check(
            checks,
            "performance_progression",
            "表现任务递进",
            _levels_progress(levels),
            "表现关卡没有体现从感知到模仿再到展示/创造的递进。",
            "按听辨、模仿、迁移、展示或创造重排关卡。",
            warn_only=True,
        )
    if activity_type == "creation":
        _add_fit_check(
            checks,
            "creation_scaffold",
            "创造活动有支架",
            bool(spec.get("creation", {}).get("pieces")) and bool(spec.get("interaction_model", {}).get("student_actions")),
            "创造活动缺少素材或学生操作支架。",
            "提供素材卡、结构提示和试听反馈。",
            warn_only=True,
        )

    score = 100 - sum(8 if check["status"] == "warn" else 14 for check in checks if check["status"] != "pass")
    score = max(0, min(100, score))
    return {
        "score": score,
        "grade_profile": profile,
        "repertoire": repertoire,
        "curriculum_anchors": CURRICULUM_ANCHORS,
        "checks": checks,
        "recommendations": [check["fix"] for check in checks if check["status"] != "pass"],
    }


def build_generation_guidance(
    profile: dict[str, Any],
    repertoire: dict[str, Any] | None,
    spec: dict[str, Any] | None = None,
) -> list[str]:
    guidance = [
        f"学段定位：{profile['label']}，优先能力：{'、'.join(profile['abilities'][:3])}。",
        f"交互建议：{'、'.join(profile['interaction'][:4])}。",
        f"评价建议：{'、'.join(profile['assessment'][:3])}。",
    ]
    if repertoire:
        guidance.append(f"曲目重点：《{repertoire['title']}》适合突出 {'、'.join(repertoire['teaching_points'][:3])}。")
        guidance.append(f"活动建议：{'、'.join(repertoire['activity_suggestions'][:3])}。")
    if spec and spec.get("activity_type") == "music_game":
        guidance.append("小游戏必须把音乐概念转成明确规则，避免只做泛娱乐操作。")
    return guidance


def grade_profile_for_text(text: str) -> dict[str, Any]:
    normalized = text or ""
    for profile in GRADE_PROFILES.values():
        if any(term in normalized for term in profile["grade_terms"]):
            return profile
    if "小学" in normalized:
        return GRADE_PROFILES["middle_primary"]
    if "初中" in normalized:
        return GRADE_PROFILES["middle_school"]
    if "高中" in normalized:
        return GRADE_PROFILES["high_school"]
    return GRADE_PROFILES["middle_primary"]


def repertoire_for_text(need: str, spec: dict[str, Any] | None = None) -> dict[str, Any] | None:
    candidates = []
    if spec:
        candidates.append(str(spec.get("song_name", "")))
        candidates.append(str(spec.get("title", "")))
    candidates.append(need)
    text = " ".join(candidates)
    bracket_match = re.search(r"《([^》]{1,40})》", text)
    if bracket_match and bracket_match.group(1) in REPERTOIRE_LIBRARY:
        return REPERTOIRE_LIBRARY[bracket_match.group(1)]
    for title, payload in REPERTOIRE_LIBRARY.items():
        if title in text:
            return payload
    return None


def _grade_text(need: str, spec: dict[str, Any] | None) -> str:
    parts = [need]
    if spec:
        parts.append(str(spec.get("grade_band", "")))
        parts.append(str(spec.get("title", "")))
        parts.append(str(spec.get("subtitle", "")))
    return " ".join(parts)


def _interaction_fits_grade(spec: dict[str, Any], profile: dict[str, Any]) -> bool:
    text = _spec_text(spec)
    if profile["label"] == "小学低年级":
        return not any(term in text for term in ["复杂", "多声部", "曲式分析", "和声"]) and any(
            term in text for term in ["动作", "模仿", "图形", "角色", "按钮", "唱游", "鼓励"]
        )
    if profile["label"] == "初中":
        return any(term in text for term in ["风格", "理由", "术语", "比较", "文化", "合作", "创编"])
    return True


def _core_literacy_coverage(spec: dict[str, Any]) -> int:
    text = _spec_text(spec)
    coverage = 0
    if any(term in text for term in ["听辨", "感受", "对比", "审美", "音色", "速度", "力度"]):
        coverage += 1
    if any(term in text for term in ["演唱", "表现", "律动", "敲击", "模仿", "展示"]):
        coverage += 1
    if any(term in text for term in ["创作", "创造", "创编", "续写", "拼图", "网格"]):
        coverage += 1
    if any(term in text for term in ["文化", "民歌", "民族", "风格", "戏曲", "背景"]):
        coverage += 1
    return coverage


def _levels_progress(levels: list[Any]) -> bool:
    text = " ".join(str(level) for level in levels)
    ladder_hits = sum(1 for term in ["听辨", "模仿", "迁移", "展示", "创造", "合作", "完整"] if term in text)
    return ladder_hits >= 3


def _mentions_any(spec: dict[str, Any], terms: list[str]) -> bool:
    text = _spec_text(spec)
    return any(term in text for term in terms)


def _spec_text(spec: dict[str, Any]) -> str:
    return str(spec)


def _add_fit_check(
    checks: list[dict[str, Any]],
    check_id: str,
    label: str,
    passed: bool,
    message: str,
    fix: str,
    *,
    warn_only: bool = False,
) -> None:
    checks.append(
        {
            "id": check_id,
            "label": label,
            "status": "pass" if passed else "warn" if warn_only else "fail",
            "message": "通过。" if passed else message,
            "fix": "" if passed else fix,
        }
    )
