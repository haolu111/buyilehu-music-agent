from __future__ import annotations

import re
from typing import Any


LESSON_CASE_VERSION = "lesson_case_v1"
STAGE_HEADING_RE = re.compile(r"^\s*(?:[一二三四五六七八九十]+[、.．]|(?:\d+)[、.．])\s*(.+?)\s*$")

BEHAVIOR_KEYWORDS = {
    "听": ("听", "聆听", "欣赏", "播放"),
    "拍": ("拍", "拍手", "拍击", "击拍", "强拍"),
    "动": ("动", "律动", "身体", "动作"),
    "唱": ("唱", "学唱", "模唱", "演唱", "跟唱"),
    "说": ("说", "说明", "交流", "回答"),
    "奏": ("演奏", "乐器", "伴奏", "打击乐器", "小乐器"),
    "编": ("创编", "编创", "编"),
}

FOCUS_KEYWORDS = {
    "二拍子": ("二拍子", "2/4", "两拍子"),
    "三拍子": ("三拍子", "3/4"),
    "强弱拍": ("强弱", "强拍", "弱拍", "重音"),
    "稳定拍": ("稳定拍", "节拍"),
    "节奏": ("节奏", "时值", "四分", "八分", "休止"),
    "旋律": ("旋律", "乐句", "上行", "下行", "音高"),
    "音色": ("音色", "乐器"),
}


def analyze_lesson_case(lesson_text: str) -> dict[str, Any]:
    text = str(lesson_text or "").strip()
    if not text:
        raise ValueError("请提供教案文本。")

    segments = [
        _segment_payload(index, heading, body)
        for index, (heading, body) in enumerate(_split_segments(text), start=1)
        if body.strip() or heading.strip()
    ]
    if not segments:
        segments = [_segment_payload(1, "课堂核心环节", text)]
    return {
        "version": LESSON_CASE_VERSION,
        "lesson_title": _extract_title(text),
        "grade_band": _extract_grade_band(text),
        "segments": segments,
        "source_summary": {
            "text_length": len(text),
            "input_mode": "pasted_text",
        },
    }


def _split_segments(text: str) -> list[tuple[str, str]]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    segments: list[tuple[str, list[str]]] = []
    current_heading = ""
    current_body: list[str] = []

    for line in lines:
        heading = _heading_from_line(line)
        if heading:
            if current_heading or current_body:
                segments.append((current_heading or "课堂环节", current_body))
            current_heading = heading
            current_body = []
        else:
            current_body.append(line)

    if current_heading or current_body:
        segments.append((current_heading or "课堂环节", current_body))

    if len(segments) <= 1:
        sentence_chunks = [chunk.strip() for chunk in re.split(r"[。！？]\s*", text) if chunk.strip()]
        return [(f"环节{idx}", chunk) for idx, chunk in enumerate(sentence_chunks, start=1)]
    return [(heading, "\n".join(body)) for heading, body in segments]


def _heading_from_line(line: str) -> str:
    match = STAGE_HEADING_RE.match(line)
    if not match:
        return ""
    heading = match.group(1).strip(" ：:")
    if len(heading) > 24:
        return ""
    if any(marker in heading for marker in ("课题", "学段", "教学目标", "目标")):
        return ""
    return heading


def _segment_payload(index: int, heading: str, body: str) -> dict[str, Any]:
    evidence = _clean_evidence(body or heading)
    behaviors = _keywords_present(evidence, BEHAVIOR_KEYWORDS)
    focus = _keywords_present(evidence, FOCUS_KEYWORDS)
    material = _extract_music_material(evidence)
    teaching_goal = _teaching_goal(evidence, focus)
    return {
        "segment_id": f"seg-{index:03d}",
        "stage": heading.strip() or f"环节{index}",
        "source_evidence": evidence,
        "teaching_goal": teaching_goal,
        "music_material": material,
        "student_behaviors": behaviors,
        "music_focus": focus,
        "digital_potential": _digital_potential(material=material, behaviors=behaviors, focus=focus, text=evidence),
    }


def _extract_title(text: str) -> str:
    first_lines = "\n".join(line for line in text.splitlines()[:12])
    patterns = [
        r"课题[：:]\s*《?([^》\n]+)》?",
        r"教案[：:]\s*《([^》]+)》",
        r"歌曲[：:]\s*《?([^》\n]+)》?",
        r"《([^》]+)》",
    ]
    for pattern in patterns:
        match = re.search(pattern, first_lines)
        if match:
            return match.group(1).strip()
    return "未命名课例"


def _extract_grade_band(text: str) -> str:
    primary_grade_match = re.search(r"小学\s*([一二三四五六])年级", text)
    if primary_grade_match:
        grade = f"{primary_grade_match.group(1)}年级"
        if grade in {"一年级", "二年级"}:
            return "小学低段"
        if grade in {"三年级", "四年级"}:
            return "小学中段"
        return "小学高段"
    match = re.search(r"(小学低段|小学中段|小学高段|一年级|二年级|三年级|四年级|五年级|六年级|小学|初中|高中)", text)
    if not match:
        return "小学"
    grade = match.group(1)
    if grade in {"一年级", "二年级"}:
        return "小学低段"
    if grade in {"三年级", "四年级"}:
        return "小学中段"
    if grade in {"五年级", "六年级"}:
        return "小学高段"
    return grade


def _clean_evidence(text: str) -> str:
    compact = re.sub(r"\s+", " ", str(text or "")).strip()
    return compact[:220]


def _keywords_present(text: str, keyword_map: dict[str, tuple[str, ...]]) -> list[str]:
    found: list[str] = []
    for label, keywords in keyword_map.items():
        if any(keyword in text for keyword in keywords):
            found.append(label)
    return found


def _extract_music_material(text: str) -> str:
    phrase_match = re.search(r"第\s*([一二三四五六七八九十\d]+)\s*乐句", text)
    if phrase_match:
        value = phrase_match.group(1)
        normalized = {"1": "一", "2": "二", "3": "三", "4": "四"}.get(value, value)
        return f"第{normalized}乐句"
    if "第一乐句" in text:
        return "第一乐句"
    if "开头乐句" in text:
        return "第一乐句"
    if "歌曲" in text:
        return "歌曲"
    if "音乐" in text:
        return "音乐片段"
    if any(marker in text for marker in ("雨声", "播放")):
        return "声音材料"
    return ""


def _teaching_goal(text: str, focus: list[str]) -> str:
    if "二拍子" in focus and "强弱拍" in focus:
        return "学生能感受二拍子强弱。"
    if "强弱拍" in focus:
        return "学生能听辨并表现强弱拍。"
    if "节奏" in focus:
        return "学生能听辨并表现节奏。"
    if "旋律" in focus:
        return "学生能感受并表现旋律。"
    if "音色" in focus:
        return "学生能听辨音色。"
    if "唱" in _keywords_present(text, BEHAVIOR_KEYWORDS):
        return "学生能参与学唱并表现歌曲。"
    return "学生能参与该教学环节。"


def _digital_potential(*, material: str, behaviors: list[str], focus: list[str], text: str) -> str:
    if _is_meta_or_preparation_section(text):
        return "low"
    if material and focus and any(behavior in behaviors for behavior in ("听", "拍", "动", "唱", "编", "奏")):
        return "high"
    if any(marker in text for marker in ("导入", "说一说", "交流")) and not material:
        return "low"
    if behaviors and (focus or material):
        return "medium"
    return "low"


def _is_meta_or_preparation_section(text: str) -> bool:
    meta_markers = (
        "教材依据",
        "教材与学情分析",
        "教学目标",
        "教学重点",
        "教学难点",
        "教学准备",
        "课堂观察",
        "生成约束",
        "板书设计",
        "课后延伸",
    )
    return any(marker in text for marker in meta_markers)
