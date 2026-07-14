from __future__ import annotations

import re
from dataclasses import dataclass


ACTIVITY_LABELS = {
    "listening": "聆听体验",
    "performance": "表现训练",
    "creation": "创意活动",
    "music_game": "音乐小游戏",
    "mixed": "综合活动",
    "unknown": "待确认",
}


@dataclass(frozen=True)
class GuidanceResult:
    activity_type: str
    ready: bool
    question: str
    missing_fields: list[str]
    normalized_need: str

    def to_dict(self) -> dict:
        return {
            "activity_type": self.activity_type,
            "activity_label": ACTIVITY_LABELS[self.activity_type],
            "ready": self.ready,
            "question": self.question,
            "missing_fields": self.missing_fields,
            "normalized_need": self.normalized_need,
        }


def build_guidance(need: str) -> GuidanceResult:
    normalized_need = _normalize_need(need)
    activity_type = infer_activity_type(normalized_need)
    missing_fields = _missing_fields(normalized_need, activity_type)

    return GuidanceResult(
        activity_type=activity_type,
        ready=not missing_fields,
        question=_build_question(activity_type, missing_fields, normalized_need),
        missing_fields=missing_fields,
        normalized_need=normalized_need,
    )


def infer_activity_type(need: str) -> str:
    strong_listening = any(
        word in need
        for word in [
            "聆听",
            "听觉",
            "体验",
            "音频",
            "听辨",
            "对比试听",
            "要素修改",
            "音乐要素修改",
            "切换音乐要素",
            "对比听",
            "转midi",
            "转 midi",
            "midi",
            "改音",
            "改节奏",
        ]
    )
    strong_performance = any(word in need for word in ["表现", "闯关", "关卡", "演唱", "唱歌", "律动", "节奏训练", "打击乐"])
    strong_creation = any(word in need for word in ["创造", "创意", "创作", "写歌", "续写", "拼图", "拖拽", "重组", "填空", "网格", "旋律线"])
    explicit_music_game = any(
        word in need
        for word in [
            "音乐小游戏",
            "小游戏",
            "赛跑",
            "跑过屏幕",
            "动物",
            "角色",
            "卡牌",
            "翻牌",
            "消消乐",
            "找朋友",
            "跑酷",
            "飞行",
            "拖拽动物",
            "节奏句子",
            "音符游戏",
        ]
    )
    generic_game = "游戏" in need
    listening_only = any(word in need for word in ["听辨", "聆听工具", "听辨工具"]) and not strong_performance and not strong_creation

    element_only_listening = any(word in need for word in ["调式", "调性", "音色", "速度", "主音", "节奏", "音乐要素"])
    if explicit_music_game and not strong_performance:
        return "music_game"
    if generic_game and not (strong_performance or strong_creation or strong_listening):
        return "music_game"

    has_listening = strong_listening or listening_only or (element_only_listening and not strong_performance and not strong_creation)
    has_performance = strong_performance
    has_creation = strong_creation

    matched_count = sum([has_listening, has_performance, has_creation])
    if matched_count == 0:
        return "unknown"
    if matched_count > 1:
        return "mixed"
    if has_listening:
        return "listening"
    if has_performance:
        return "performance"
    return "creation"


def _missing_fields(need: str, activity_type: str) -> list[str]:
    if activity_type == "unknown":
        return ["activity_type"]

    missing_fields: list[str] = []
    if activity_type in ("listening", "mixed"):
        if not _has_music_material(need):
            missing_fields.append("listening_material")
        if not any(word in need for word in ["调式", "调性", "节奏", "速度", "音色", "主音", "力度", "对比"]):
            missing_fields.append("listening_element")

    if activity_type in ("performance", "mixed"):
        if not _has_music_material(need):
            missing_fields.append("performance_material")
        if not any(word in need for word in ["第一关", "第1关", "关卡", "长音", "切分", "音高", "节奏", "完整演唱", "律动"]):
            missing_fields.append("performance_levels")

    if activity_type in ("creation", "mixed"):
        if not any(word in need for word in ["拼装", "拼图", "填空", "续写", "重组", "自由", "节奏", "旋律", "歌词", "网格", "旋律线"]):
            missing_fields.append("creation_method")
        if not any(word in need for word in ["规则", "素材", "小节", "主音", "调式", "节奏型", "情绪", "风格"]):
            missing_fields.append("creation_rule")

    if activity_type == "music_game":
        if not any(word in need for word in ["音符", "节奏", "音高", "强弱", "速度", "音色", "调式", "拍", "时值", "旋律"]):
            missing_fields.append("game_music_rule")
        if not any(word in need for word in ["拖拽", "点击", "排列", "匹配", "赛跑", "飞行", "翻牌", "消消乐", "找朋友", "跑酷", "跑过屏幕"]):
            missing_fields.append("game_mechanic")

    return missing_fields


def _build_question(activity_type: str, missing_fields: list[str], need: str) -> str:
    if not missing_fields:
        return "信息已经够用了，我可以开始生成课堂网页。"

    if "activity_type" in missing_fields:
        return "欢迎！今天要进行哪类教学活动？请从聆听体验、表现训练、创意活动、音乐小游戏中选一个，并告诉我歌曲或素材。"

    prompts = []
    if "listening_material" in missing_fields or "listening_element" in missing_fields:
        prompts.append("聆听体验需要确认：是哪首曲子或哪段音频？希望学生对比哪些要素，比如调式、速度、节奏、音色或主音？")
    if "performance_material" in missing_fields or "performance_levels" in missing_fields:
        prompts.append("表现训练需要确认：使用哪首歌或节奏型？请给出关卡划分，例如第一关长音、第二关切分音、第三关完整演唱。")
    if "creation_method" in missing_fields or "creation_rule" in missing_fields:
        prompts.append("创意活动需要确认：希望学生自由拼装、音符填空、旋律续写、风格重组还是网格画旋律线？请补充素材或规则，比如主音、调式、小节数、节奏型。")
    if "game_music_rule" in missing_fields or "game_mechanic" in missing_fields:
        prompts.append("音乐小游戏需要确认：要练习哪个音乐概念，比如音符时值、节奏、音高或强弱？学生通过什么玩法完成，比如拖拽排列、点击匹配、赛跑、翻牌或角色闯关？")

    if activity_type == "mixed":
        return "这是一个综合活动，我还需要把每个环节补齐：" + " ".join(prompts)
    return prompts[0]


def _has_music_material(need: str) -> bool:
    return bool(re.search(r"《[^》]{1,40}》", need)) or any(
        word in need for word in ["歌曲", "曲子", "音频", "民歌", "节奏型", "旋律", "作品", "小小虫", "茉莉花"]
    )


def _normalize_need(need: str) -> str:
    return re.sub(r"\s+", " ", need).strip()
