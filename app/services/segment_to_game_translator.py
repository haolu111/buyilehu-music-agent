from __future__ import annotations

from typing import Any


SEGMENT_GAME_BRIEF_VERSION = "segment_game_brief_v1"


def translate_segment_to_game_brief(
    lesson_case: dict[str, Any],
    selected_segment: dict[str, Any],
) -> dict[str, Any]:
    segment = _find_source_segment(lesson_case, str(selected_segment.get("segment_id") or ""))
    preserve = selected_segment.get("must_preserve") if isinstance(selected_segment.get("must_preserve"), dict) else {}
    music_focus = _string_list(preserve.get("music_focus") or segment.get("music_focus"))
    music_material = str(preserve.get("music_material") or segment.get("music_material") or "教案音乐材料")
    source_evidence = str(segment.get("source_evidence") or selected_segment.get("source_evidence") or "")
    target = _learning_target(music_focus)
    return {
        "version": SEGMENT_GAME_BRIEF_VERSION,
        "source_segment_id": str(selected_segment.get("segment_id") or segment.get("segment_id") or ""),
        "source_evidence": source_evidence,
        "game_goal": _game_goal(target),
        "music_learning_target": target,
        "student_actions": _student_actions(music_material, _string_list(preserve.get("student_behaviors"))),
        "core_mechanic": _core_mechanic(target),
        "success_condition": _success_condition(target),
        "error_feedback": _error_feedback(target),
        "classroom_return": _classroom_return(music_material, target),
        "must_preserve": {
            "teaching_goal": str(preserve.get("teaching_goal") or segment.get("teaching_goal") or ""),
            "music_material": music_material,
            "student_behaviors": _string_list(preserve.get("student_behaviors") or segment.get("student_behaviors")),
        },
    }


def _find_source_segment(lesson_case: dict[str, Any], segment_id: str) -> dict[str, Any]:
    segments = lesson_case.get("segments") if isinstance(lesson_case.get("segments"), list) else []
    for segment in segments:
        if isinstance(segment, dict) and str(segment.get("segment_id") or "") == segment_id:
            return segment
    raise ValueError("没有找到选中的教案环节。")


def _learning_target(music_focus: list[str]) -> str:
    if "二拍子" in music_focus and "强弱拍" in music_focus:
        return "二拍子强弱感知"
    if "强弱拍" in music_focus:
        return "强弱拍感知"
    if "节奏" in music_focus:
        return "节奏听辨与表现"
    if "旋律" in music_focus:
        return "旋律听辨与表现"
    if "音色" in music_focus:
        return "音色听辨"
    return "音乐要素感知"


def _game_goal(target: str) -> str:
    if "二拍子" in target or "强弱拍" in target:
        return "帮助学生在听辨中预判二拍子强拍。"
    return f"帮助学生通过听与做理解{target}。"


def _student_actions(music_material: str, behaviors: list[str]) -> list[str]:
    actions = [f"听{music_material}"]
    if any(item in behaviors for item in ("拍", "动")):
        actions.append("在强拍同步点击/拍手")
        if "动" in behaviors:
            actions.append("用律动表现强弱")
    elif "唱" in behaviors:
        actions.append("听后唱回关键片段")
    else:
        actions.append("根据听到的音乐做出选择")
    actions.append("游戏后边唱边拍")
    return actions


def _core_mechanic(target: str) -> str:
    if "二拍子" in target or "强弱拍" in target:
        return "强拍预判与同步反馈"
    if "节奏" in target:
        return "节奏听辨与复现反馈"
    if "旋律" in target:
        return "旋律方向选择与唱回反馈"
    return "听辨选择与音乐理由反馈"


def _success_condition(target: str) -> str:
    if "二拍子" in target or "强弱拍" in target:
        return "学生能在多个小节中稳定命中强拍。"
    return f"学生能稳定完成{target}任务并说出音乐依据。"


def _error_feedback(target: str) -> list[dict[str, str]]:
    if "二拍子" in target or "强弱拍" in target:
        return [
            {"error_type": "early", "feedback": "抢拍了，等强拍落下再拍。"},
            {"error_type": "late", "feedback": "晚了，下一小节提前预判。"},
            {"error_type": "missing", "feedback": "漏掉强拍，听小节开头。"},
        ]
    return [
        {"error_type": "early", "feedback": "先听完整，再做判断。"},
        {"error_type": "late", "feedback": "跟住音乐线索再回应。"},
        {"error_type": "missing", "feedback": "漏掉了关键音乐线索。"},
    ]


def _classroom_return(music_material: str, target: str) -> str:
    if "二拍子" in target or "强弱拍" in target:
        return f"回到{music_material}，边唱边拍强拍。"
    return f"回到{music_material}，用课堂方式再次表现{target}。"


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]
