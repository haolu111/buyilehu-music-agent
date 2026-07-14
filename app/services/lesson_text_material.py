from __future__ import annotations

import re
from typing import Any

from app.services.song_material_parser import parse_song_material


SOLFEGE_RE = re.compile(r"(?i)\b(?:do|re|mi|fa|sol|so|la|si|ti)\b")
DIGIT_NOTATION_RE = re.compile(r"[1-7][0-7\s,，、;；/\-.]{3,}[0-7]")
RHYTHM_RE = re.compile(r"(?:全音符|二分音符|四分音符|八分音符|十六分音符|附点|切分|休止|强拍|弱拍|节奏型|ta|ti[-\s]?ti)", re.I)
FORM_RE = re.compile(r"(?:ABA|A段|B段|再现|重复|对比|回旋|曲式|乐段|段落)")
TIMBRE_RE = re.compile(r"(?:音色|乐器|笛子|二胡|小提琴|钢琴|长笛|古筝|木鱼|鼓|弦乐|管乐|打击乐)")


def build_text_material_draft(lesson_text: str, *, extra_need: str = "") -> dict[str, Any]:
    """Extract teacher-confirmable music material from plain lesson text."""

    source_text = "\n".join(part for part in [lesson_text, extra_need] if str(part or "").strip())
    candidates = _extract_candidates(source_text)
    if not candidates:
        return {
            "version": "text_material_draft_v1",
            "status": "needs_teacher_confirmation",
            "message": "教案正文里没有自动提取出可用于游戏判定的材料。请补充核心乐句、唱名、简谱、节奏型、段落结构或音色线索后再生成。",
            "items": [],
            "confirmed_text": "",
        }
    confirmed_text = "\n".join(f"{item['label']}：{item['text']}" for item in candidates[:8])
    return {
        "version": "text_material_draft_v1",
        "status": "needs_teacher_confirmation",
        "message": "已从教案正文提取出文字音乐材料，请老师确认或修正后再生成。",
        "items": candidates[:8],
        "confirmed_text": confirmed_text,
    }


def text_material_draft_to_song_material(draft: dict[str, Any], *, filename: str = "lesson-text-material.txt") -> dict[str, Any]:
    if not isinstance(draft, dict):
        return {}
    text = str(draft.get("confirmed_text") or "").strip()
    if not text:
        items = draft.get("items", []) if isinstance(draft.get("items"), list) else []
        text = "\n".join(
            f"{item.get('label') or f'第{index}乐句'}：{item.get('text') or ''}"
            for index, item in enumerate(items[:8], start=1)
            if isinstance(item, dict) and str(item.get("text") or "").strip()
        )
    if not text:
        return {}
    material = parse_song_material(filename, b"", text_hint=text)
    if not material:
        return {}
    source = material.setdefault("source", {})
    source["kind"] = "teacher_confirmed_score_hint"
    source["filename"] = filename
    source["analysis_quality"] = "medium" if material.get("phrases") else "low"
    source["requires_manual_confirmation"] = False
    source["from_text_material_draft"] = True
    material["text_material_draft"] = {**draft, "status": "confirmed", "confirmed_text": text}
    return material


def _extract_candidates(text: str) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for line in _candidate_lines(text):
        kind = _line_kind(line)
        if not kind:
            continue
        label = _label_for_kind(kind, len(candidates) + 1)
        candidates.append(
            {
                "id": f"text_{len(candidates) + 1}",
                "label": label,
                "kind": kind,
                "text": _clean_candidate_text(line),
                "confidence": "medium",
            }
        )
    return _dedupe_candidates(candidates)


def _candidate_lines(text: str) -> list[str]:
    lines = []
    for raw in re.split(r"[\n。；;]", str(text or "")):
        line = re.sub(r"\s+", " ", raw).strip()
        if 4 <= len(line) <= 140:
            lines.append(line)
    return lines


def _line_kind(line: str) -> str:
    solfege_count = len(SOLFEGE_RE.findall(line))
    digit_match = DIGIT_NOTATION_RE.search(line)
    if solfege_count >= 3 or digit_match:
        return "notation"
    if RHYTHM_RE.search(line):
        return "rhythm"
    if FORM_RE.search(line):
        return "form"
    if TIMBRE_RE.search(line):
        return "timbre"
    return ""


def _label_for_kind(kind: str, index: int) -> str:
    return {
        "notation": f"第{index}乐句",
        "rhythm": f"节奏材料{index}",
        "form": f"段落材料{index}",
        "timbre": f"音色材料{index}",
    }.get(kind, f"材料{index}")


def _clean_candidate_text(line: str) -> str:
    cleaned = re.sub(r"^(教师|学生|活动|环节|步骤|提问|板书)[:：]\s*", "", line).strip()
    return cleaned[:120]


def _dedupe_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    seen = set()
    for item in candidates:
        text = item.get("text", "")
        key = re.sub(r"\s+", "", text)
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result
