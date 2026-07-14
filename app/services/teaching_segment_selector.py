from __future__ import annotations

from typing import Any


SELECTED_TEACHING_SEGMENT_VERSION = "selected_teaching_segment_v1"


def select_teaching_segment(lesson_case: dict[str, Any]) -> dict[str, Any]:
    segments = lesson_case.get("segments") if isinstance(lesson_case.get("segments"), list) else []
    scored = [(_score_segment(segment), segment) for segment in segments if isinstance(segment, dict)]
    scored = [item for item in scored if item[0] > 0]
    if not scored:
        raise ValueError("没有找到适合游戏化的教学环节。")
    scored.sort(key=lambda item: item[0], reverse=True)
    segment = scored[0][1]
    behaviors = _string_list(segment.get("student_behaviors"))
    return {
        "version": SELECTED_TEACHING_SEGMENT_VERSION,
        "segment_id": str(segment.get("segment_id") or ""),
        "selection_reason": _selection_reason(segment, behaviors),
        "source_evidence": str(segment.get("source_evidence") or ""),
        "must_preserve": {
            "teaching_goal": str(segment.get("teaching_goal") or ""),
            "music_material": str(segment.get("music_material") or ""),
            "student_behaviors": behaviors,
            "music_focus": _string_list(segment.get("music_focus")),
        },
        "must_not_add": [
            "不得新增教案未出现的曲式学习目标",
            "不得改成无关音色听辨游戏",
            "不得脱离原教学环节另造课堂任务",
        ],
    }


def _score_segment(segment: dict[str, Any]) -> int:
    material = str(segment.get("music_material") or "").strip()
    behaviors = _string_list(segment.get("student_behaviors"))
    focus = _string_list(segment.get("music_focus"))
    potential = str(segment.get("digital_potential") or "")
    if not material or not behaviors:
        return 0
    stage = str(segment.get("stage") or "")
    evidence = str(segment.get("source_evidence") or "")
    if _is_meta_stage(stage, evidence):
        return 0
    score = 20
    score += 24 if focus else 0
    score += 18 if "听" in behaviors else 0
    score += 18 if any(item in behaviors for item in ("拍", "动", "唱", "奏", "编")) else 0
    score += 16 if potential == "high" else 6 if potential == "medium" else 0
    if any(item in focus for item in ("二拍子", "强弱拍", "稳定拍", "节奏")):
        score += 10
    if _is_teaching_process_stage(stage):
        score += 22
    if any(marker in stage for marker in ("游戏化活动", "感受拍点", "节拍体验")):
        score += 18
    if any(marker in stage for marker in ("课堂回扣", "导入")):
        score -= 18
    if "开头乐句" in evidence or "第一乐句" in evidence:
        score += 8
    return score


def _selection_reason(segment: dict[str, Any], behaviors: list[str]) -> str:
    joined_behaviors = "、".join(behaviors) or "学生操作"
    focus = "、".join(_string_list(segment.get("music_focus"))) or "音乐目标"
    return f"该环节已有{joined_behaviors}行为，并聚焦{focus}，适合转译为3-8分钟音乐学习游戏。"


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _is_meta_stage(stage: str, evidence: str) -> bool:
    text = f"{stage} {evidence}"
    markers = (
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
    return any(marker in text for marker in markers)


def _is_teaching_process_stage(stage: str) -> bool:
    return any(
        marker in stage
        for marker in (
            "情境导入",
            "感受拍点",
            "学唱歌曲",
            "游戏化活动",
            "创编伴奏",
            "课堂回扣",
        )
    )
