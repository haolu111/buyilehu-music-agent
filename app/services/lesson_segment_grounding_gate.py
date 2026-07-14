from __future__ import annotations

from typing import Any


GROUNDING_RESULT_VERSION = "lesson_segment_grounding_result_v1"

UNRELATED_GOAL_MARKERS = {
    "音色听辨": ("二拍子", "强弱", "节拍", "节奏", "旋律"),
    "曲式": ("二拍子", "强弱", "节拍", "节奏", "音色", "旋律"),
}


def evaluate_lesson_segment_grounding(
    *,
    lesson_case: dict[str, Any],
    selected_segment: dict[str, Any],
    segment_game_brief: dict[str, Any],
    production_spec: dict[str, Any] | None = None,
) -> dict[str, Any]:
    production_spec = production_spec if isinstance(production_spec, dict) else {}
    segment_id = str(selected_segment.get("segment_id") or "")
    preserve = selected_segment.get("must_preserve") if isinstance(selected_segment.get("must_preserve"), dict) else {}
    blocking_issues: list[str] = []
    warnings: list[str] = []

    if str(segment_game_brief.get("source_segment_id") or "") != segment_id:
        blocking_issues.append("source_segment_mismatch")
    concept = production_spec.get("game_concept") if isinstance(production_spec.get("game_concept"), dict) else {}
    if concept and str(concept.get("source_segment_id") or "") != segment_id:
        blocking_issues.append("production_source_segment_mismatch")

    material = str(preserve.get("music_material") or "")
    if material and material not in _combined_text(segment_game_brief, production_spec):
        blocking_issues.append("missing_preserved_music_material")

    teaching_goal = str(preserve.get("teaching_goal") or "")
    if teaching_goal and not _goal_preserved(teaching_goal, segment_game_brief):
        warnings.append("teaching_goal_only_partially_preserved")

    if _has_unrelated_goal(segment_game_brief, preserve):
        blocking_issues.append("unrelated_music_goal_added")

    missing_behaviors = _missing_behaviors(preserve, segment_game_brief)
    if missing_behaviors:
        blocking_issues.append("missing_preserved_student_behavior")

    runtime_config = production_spec.get("runtime_config") if isinstance(production_spec.get("runtime_config"), dict) else {}
    classroom_return = str(segment_game_brief.get("classroom_return") or runtime_config.get("classroom_return") or "").strip()
    if not classroom_return:
        blocking_issues.append("missing_classroom_return")

    return {
        "version": GROUNDING_RESULT_VERSION,
        "status": "blocked" if blocking_issues else "pass",
        "source_segment_id": segment_id,
        "blocking_issues": blocking_issues,
        "warning_issues": warnings,
        "checked_items": [
            "source_segment_id",
            "teaching_goal",
            "music_material",
            "student_behaviors",
            "unrelated_music_goal",
            "classroom_return",
        ],
        "evidence": {
            "lesson_title": lesson_case.get("lesson_title", ""),
            "source_evidence": segment_game_brief.get("source_evidence", ""),
        },
    }


def _combined_text(*payloads: Any) -> str:
    chunks: list[str] = []

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)
        elif value is not None:
            chunks.append(str(value))

    for payload in payloads:
        visit(payload)
    return " ".join(chunks)


def _goal_preserved(teaching_goal: str, brief: dict[str, Any]) -> bool:
    text = _combined_text(brief)
    markers = [marker for marker in ("二拍子", "强弱", "强拍", "节奏", "旋律", "音色") if marker in teaching_goal]
    return not markers or any(marker in text for marker in markers)


def _has_unrelated_goal(brief: dict[str, Any], preserve: dict[str, Any]) -> bool:
    target = str(brief.get("music_learning_target") or brief.get("game_goal") or "")
    original_text = _combined_text(preserve)
    for added_goal, compatible_markers in UNRELATED_GOAL_MARKERS.items():
        if added_goal in target and not any(marker in original_text for marker in compatible_markers if marker in added_goal):
            return True
    if "音色" in target and "音色" not in original_text:
        return True
    if "曲式" in target and "曲式" not in original_text:
        return True
    return False


def _missing_behaviors(preserve: dict[str, Any], brief: dict[str, Any]) -> list[str]:
    expected = [str(item) for item in preserve.get("student_behaviors", []) if str(item).strip()]
    executable_brief = {
        "student_actions": brief.get("student_actions", []),
        "core_mechanic": brief.get("core_mechanic", ""),
        "success_condition": brief.get("success_condition", ""),
        "error_feedback": brief.get("error_feedback", []),
        "classroom_return": brief.get("classroom_return", ""),
    }
    text = _combined_text(executable_brief)
    return [behavior for behavior in expected if behavior not in text and not _behavior_synonym_present(behavior, text)]


def _behavior_synonym_present(behavior: str, text: str) -> bool:
    synonyms = {
        "听": ("听", "聆听"),
        "拍": ("拍", "点击", "强拍"),
        "动": ("动", "律动", "身体"),
        "唱": ("唱", "模唱", "唱回"),
    }
    return any(marker in text for marker in synonyms.get(behavior, (behavior,)))
