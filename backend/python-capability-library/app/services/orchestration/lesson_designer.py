# 使用本地规则快速生成游戏计划、智能体计划和创编拼图
from __future__ import annotations

from dataclasses import dataclass


MODE_TO_SOLFEGE = {
    "western_major": ["do", "re", "mi", "fa", "sol", "la", "ti"],
    "western_minor": ["la", "ti", "do", "re", "mi", "fa", "sol"],
    "chinese_pentatonic": ["宫", "商", "角", "徵", "羽"],
    "chinese_heptatonic": ["宫", "商", "角", "变徵", "徵", "羽", "变宫"],
    "dorian": ["1", "2", "b3", "4", "5", "6", "b7"],
    "phrygian": ["1", "b2", "b3", "4", "5", "b6", "b7"],
    "blues": ["1", "b3", "4", "#4", "5", "b7"],
}

MODE_LABELS = {
    "western_major": "西洋大调",
    "western_minor": "西洋小调",
    "chinese_pentatonic": "中国五声调式",
    "chinese_heptatonic": "中国七声调式",
    "dorian": "多利亚调式",
    "phrygian": "弗里吉亚调式",
    "blues": "布鲁斯调式",
}

MODE_KEYWORDS = {
    "chinese_pentatonic": ["五声", "中国", "民族", "宫商角徵羽"],
    "chinese_heptatonic": ["七声", "雅乐", "燕乐"],
    "dorian": ["多利亚", "dorian"],
    "phrygian": ["弗里吉亚", "phrygian"],
    "blues": ["布鲁斯", "蓝调", "blues"],
    "western_minor": ["小调", "忧伤", "暗淡"],
    "western_major": ["大调", "明亮", "欢快"],
}

INSTRUMENT_KEYWORDS = {
    "guzheng": ["古筝", "民族", "中国"],
    "violin": ["小提琴", "弦乐"],
    "flute": ["长笛", "笛", "清亮"],
    "piano": ["钢琴", "键盘", "基础"],
}


@dataclass
class GameRequest:
    stage_count: int
    grade_band: str
    target_skill: str
    theme: str


@dataclass
class PuzzleRequest:
    tonic: str
    mode: str
    bars: int
    mood: str


def generate_game_plan(request: GameRequest) -> dict:
    levels = []
    skill_ladder = [
        "辨认",
        "比较",
        "模仿",
        "迁移",
        "创造",
    ]

    for index in range(request.stage_count):
        ladder = skill_ladder[min(index, len(skill_ladder) - 1)]
        level_no = index + 1
        levels.append(
            {
                "level": level_no,
                "title": f"第{level_no}关：{request.theme}{ladder}",
                "goal": f"围绕“{request.target_skill}”完成一次{ladder}任务。",
                "student_task": _student_task_for_level(request.target_skill, ladder),
                "teacher_prompt": _teacher_prompt(request.grade_band, ladder),
                "success_rule": _success_rule(level_no),
                "reward": _reward(level_no),
            }
        )

    return {
        "grade_band": request.grade_band,
        "theme": request.theme,
        "target_skill": request.target_skill,
        "levels": levels,
        "final_boss": {
            "title": "终极关卡：综合舞台",
            "goal": "学生需要听辨、表现并再创造同一音乐材料，形成完整课堂闭环。",
            "scoring": ["听辨准确 40 分", "合作表现 30 分", "创意改编 30 分"],
        },
    }


def generate_agent_plan(need: str) -> dict:
    normalized = need.lower()
    mode = _first_keyword_match(normalized, MODE_KEYWORDS, "western_major")
    instrument = _first_keyword_match(normalized, INSTRUMENT_KEYWORDS, "piano")
    rhythm_density = "preserve"
    tempo_multiplier = 1.0
    grade_band = "小学" if "小学" in need else "高中" if "高中" in need else "初中" if "初中" in need else "小学"
    target_skill = _infer_target_skill(need)
    theme = "音乐探险" if grade_band == "小学" else "风格实验室"
    mood = "明亮" if mode == "western_major" else "民族风" if mode.startswith("chinese") else "富有张力"

    return {
        "listening": {
            "tonic": _infer_tonic(need),
            "mode": "preserve",
            "mode_label": "保持原调式",
            "tempo_multiplier": tempo_multiplier,
            "rhythm_density": rhythm_density,
            "instrument": "preserve",
        },
        "performance": {
            "grade_band": grade_band,
            "target_skill": target_skill,
            "theme": theme,
            "stage_count": 4,
        },
        "creation": {
            "tonic": _infer_tonic(need),
            "mode": mode,
            "bars": 4,
            "mood": mood,
        },
        "teaching_flow": [
            "先用聆听层生成对比版本，让学生听出音乐要素变化。",
            "再用表现层闯关任务，把听到的变化转化为动作、演唱或器乐表现。",
            "最后用创造层拼图，让学生把调式、节奏和音色经验迁移到小创作中。",
        ],
    }


def _first_keyword_match(text: str, mapping: dict[str, list[str]], fallback: str) -> str:
    for value, keywords in mapping.items():
        if any(keyword.lower() in text for keyword in keywords):
            return value
    return fallback


def _infer_tonic(need: str) -> str:
    for tonic in ["C#", "D#", "F#", "G#", "A#", "C", "D", "E", "F", "G", "A", "B"]:
        if f"{tonic}调" in need or f"{tonic} " in need:
            return tonic
    return "C"


def _infer_target_skill(need: str) -> str:
    if "节奏" in need:
        return "节奏听辨"
    if "调式" in need or "调性" in need:
        return "调式色彩辨认"
    if "音色" in need or "乐器" in need:
        return "音色辨认"
    if "速度" in need:
        return "速度变化表现"
    return "音乐要素综合感知"


def _student_task_for_level(target_skill: str, ladder: str) -> str:
    mapping = {
        "辨认": f"从 3 个音频片段中找出最符合“{target_skill}”的版本。",
        "比较": f"比较两个版本在“{target_skill}”上的差别，并说出理由。",
        "模仿": f"用身体律动、打击乐或哼唱模仿“{target_skill}”的特点。",
        "迁移": f"把学到的“{target_skill}”迁移到一段新旋律中。",
        "创造": f"围绕“{target_skill}”重新设计一段 2 小节音乐挑战。",
    }
    return mapping[ladder]


def _teacher_prompt(grade_band: str, ladder: str) -> str:
    if grade_band == "小学":
        return f"采用图形谱、动作提示和颜色卡片，帮助学生完成“{ladder}”任务。"
    return f"增加音乐术语、风格判断和小组讨论，支撑学生完成“{ladder}”任务。"


def _success_rule(level_no: int) -> str:
    if level_no <= 2:
        return "答对即可通关，重在建立信心。"
    if level_no <= 4:
        return "需给出判断依据，并与同伴合作完成。"
    return "需在限时内完成任务，并展示创造性解决方案。"


def _reward(level_no: int) -> str:
    rewards = [
        "获得 1 枚节奏徽章",
        "解锁新的音色卡牌",
        "获得调式变形钥匙",
        "解锁自由创编道具",
        "登上班级音乐排行榜",
    ]
    return rewards[min(level_no - 1, len(rewards) - 1)]


def generate_creation_puzzle(request: PuzzleRequest) -> dict:
    pitch_material = MODE_TO_SOLFEGE[request.mode]
    total_pieces = max(6, request.bars * 3)
    rhythm_templates = ["四", "二八", "二分", "休止", "小切分", "三连音"]

    pieces = []
    for index in range(total_pieces):
        pieces.append(
            {
                "id": f"piece-{index + 1}",
                "pitch": pitch_material[index % len(pitch_material)],
                "rhythm": rhythm_templates[index % len(rhythm_templates)],
                "function": ["起始", "发展", "过渡", "收束"][index % 4],
            }
        )

    prompt = (
        f"请使用 {request.tonic} 为主音的{MODE_LABELS[request.mode]}材料，"
        f"在 {request.bars} 小节内拼出一首“{request.mood}”气质的小曲。"
    )

    return {
        "prompt": prompt,
        "pieces": pieces,
        "teacher_hint": "可以先固定起始音与结束音，再逐步补足中间节奏和骨干旋律。",
        "assessment": [
            "是否保持统一调式色彩",
            "是否形成起承转合",
            "是否体现指定情绪",
        ],
    }
