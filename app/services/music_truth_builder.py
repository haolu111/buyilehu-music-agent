from __future__ import annotations

from copy import deepcopy
from typing import Any


RHYTHM_STEP_BEATS = {
    "whole": 4.0,
    "half": 2.0,
    "quarter": 1.0,
    "eighth": 0.5,
    "eighth_pair": 1.0,
    "rest": 1.0,
    "dotted_quarter": 1.5,
    "syncopation": 2.0,
    "sixteenth_four": 1.0,
}


def build_music_truth(
    instance: dict[str, Any],
    *,
    source: dict[str, Any] | None = None,
    game_variant_spec: dict[str, Any] | None = None,
    segment_game_brief: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source = source if isinstance(source, dict) else {}
    game_variant_spec = game_variant_spec if isinstance(game_variant_spec, dict) else {}
    segment_game_brief = segment_game_brief if isinstance(segment_game_brief, dict) else {}
    config = instance.get("config") if isinstance(instance.get("config"), dict) else {}
    template_id = str(instance.get("template_id") or config.get("template_id") or "").strip()
    if _requires_confirmation(game_variant_spec, source=source):
        return {
            "version": "music_truth_v1",
            "template_id": template_id,
            "truth_status": "blocked",
            "blocked_reason": "teacher_confirmation_required",
            "answers": [],
            "source_policy": "low_confidence_answers_must_not_enter_runtime",
        }
    if template_id == "rhythm_echo_core":
        truth = _rhythm_truth(config, source=source, game_variant_spec=game_variant_spec)
        return _attach_segment_truth(truth, segment_game_brief)
    return _attach_segment_truth({
        "version": "music_truth_v1",
        "template_id": template_id,
        "truth_status": "draft",
        "answers": [],
        "source_policy": "runtime_must_read_truth_file",
    }, segment_game_brief)


def _rhythm_truth(
    config: dict[str, Any],
    *,
    source: dict[str, Any],
    game_variant_spec: dict[str, Any],
) -> dict[str, Any]:
    steps = _rhythm_steps(config, game_variant_spec)
    answer_source = _answer_source(source, game_variant_spec)
    answers = [
        {
            "answer_id": "round_1.target_rhythm",
            "pattern_steps": deepcopy(steps),
            "duration_beats": [_step_beats(step) for step in steps],
            "meter": config.get("meter", "2/4"),
            "bpm": config.get("bpm", 92),
            "source": answer_source,
            "confidence": answer_source.get("confidence", 1.0),
        }
    ]
    return {
        "version": "music_truth_v1",
        "template_id": "rhythm_echo_core",
        "truth_status": "draft" if _needs_teacher_review(game_variant_spec) else "usable",
        "source_policy": "every_answer_has_traceable_source",
        "answers": answers,
        "validation": {
            "duration_values_known": all(step in RHYTHM_STEP_BEATS for step in steps),
            "runtime_may_guess_answers": False,
        },
    }


def _rhythm_steps(config: dict[str, Any], game_variant_spec: dict[str, Any]) -> list[str]:
    variant_parameters = (
        game_variant_spec.get("variant_parameters")
        if isinstance(game_variant_spec.get("variant_parameters"), dict)
        else {}
    )
    for value in (variant_parameters.get("pattern_steps"), config.get("pattern_steps")):
        if isinstance(value, list) and value:
            return [str(step) for step in value if str(step).strip()]
    return ["quarter", "quarter"]


def _step_beats(step: str) -> float:
    return float(RHYTHM_STEP_BEATS.get(str(step), 1.0))


def _answer_source(source: dict[str, Any], game_variant_spec: dict[str, Any]) -> dict[str, Any]:
    selected_entity = (
        game_variant_spec.get("selected_entity")
        if isinstance(game_variant_spec.get("selected_entity"), dict)
        else {}
    )
    if selected_entity:
        return {
            "kind": selected_entity.get("source_kind") or "music_material_entity",
            "label": selected_entity.get("label") or selected_entity.get("canonical_id") or "音乐材料实体",
            "confidence": selected_entity.get("confidence", 0.9),
        }
    if source.get("lesson_source") or source.get("lesson_fit"):
        return {"kind": "lesson_material", "label": "教案或谱例材料", "confidence": 0.86}
    return {"kind": "teacher_confirmation", "label": "教师直接需求确认", "confidence": 1.0}


def _requires_confirmation(game_variant_spec: dict[str, Any], *, source: dict[str, Any]) -> bool:
    gates = game_variant_spec.get("confirmation_gates") if isinstance(game_variant_spec.get("confirmation_gates"), list) else []
    source_confidence = _source_music_entity_confidence(source)
    for gate in gates:
        if not isinstance(gate, dict) or gate.get("status") == "confirmed":
            continue
        if gate.get("gate_type") != "low_confidence_music_entity":
            continue
        gate_confidence = gate.get("confidence")
        if isinstance(source_confidence, (int, float)) and float(source_confidence) < 0.6:
            return True
        if not isinstance(gate_confidence, (int, float)):
            return True
        if float(gate_confidence) < 0.6:
            return True
    return False


def _needs_teacher_review(game_variant_spec: dict[str, Any]) -> bool:
    gates = game_variant_spec.get("confirmation_gates") if isinstance(game_variant_spec.get("confirmation_gates"), list) else []
    return any(
        isinstance(gate, dict)
        and gate.get("status") != "confirmed"
        and gate.get("gate_type") in {"teacher_confirmation_required", "low_confidence_music_entity"}
        for gate in gates
    )


def _source_music_entity_confidence(source: dict[str, Any]) -> float | None:
    lesson_fit = source.get("lesson_fit") if isinstance(source.get("lesson_fit"), dict) else {}
    binding = lesson_fit.get("music_element_binding") if isinstance(lesson_fit.get("music_element_binding"), dict) else {}
    entity = binding.get("entity") if isinstance(binding.get("entity"), dict) else {}
    confidence = entity.get("confidence")
    return float(confidence) if isinstance(confidence, (int, float)) else None


def _attach_segment_truth(truth: dict[str, Any], segment_game_brief: dict[str, Any]) -> dict[str, Any]:
    if not segment_game_brief:
        return truth
    updated = deepcopy(truth)
    updated["source_segment_id"] = str(segment_game_brief.get("source_segment_id") or "")
    updated["source_evidence"] = str(segment_game_brief.get("source_evidence") or "")
    updated["music_learning_target"] = str(segment_game_brief.get("music_learning_target") or "")
    updated["material"] = _material_from_brief(segment_game_brief)
    updated["error_categories"] = _error_categories_from_brief(segment_game_brief)
    if "judgement_windows" not in updated:
        updated["judgement_windows"] = _default_judgement_windows()
    updated["source_policy"] = "every_answer_has_traceable_lesson_segment_source"
    return updated


def _error_categories_from_brief(segment_game_brief: dict[str, Any]) -> list[dict[str, str]]:
    items = segment_game_brief.get("error_feedback") if isinstance(segment_game_brief.get("error_feedback"), list) else []
    categories = []
    for item in items:
        if not isinstance(item, dict):
            continue
        error_type = str(item.get("error_type") or item.get("type") or "").strip()
        if not error_type:
            continue
        categories.append(
            {
                "error_type": error_type,
                "feedback": str(item.get("feedback") or item.get("message") or "").strip(),
            }
        )
    existing = {item["error_type"] for item in categories}
    defaults = {
        "early": "抢拍了，等强拍落下再拍。",
        "late": "晚了，下一小节提前预判。",
        "missing": "漏掉强拍，听小节开头。",
    }
    for error_type, feedback in defaults.items():
        if error_type not in existing:
            categories.append({"error_type": error_type, "feedback": feedback})
    return categories


def _default_judgement_windows() -> dict[str, int]:
    return {
        "perfect_ms": 95,
        "good_ms": 210,
        "late_ms": 320,
    }


def _material_from_brief(segment_game_brief: dict[str, Any]) -> str:
    preserve = segment_game_brief.get("must_preserve") if isinstance(segment_game_brief.get("must_preserve"), dict) else {}
    material = str(preserve.get("music_material") or "").strip()
    if material:
        return material
    for action in segment_game_brief.get("student_actions", []):
        text = str(action or "")
        if text.startswith("听"):
            return text.removeprefix("听").strip() or "教案音乐材料"
    evidence = str(segment_game_brief.get("source_evidence") or "")
    if "第一乐句" in evidence:
        return "第一乐句"
    return "教案音乐材料"
