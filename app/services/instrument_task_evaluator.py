from __future__ import annotations

from copy import deepcopy
from math import isfinite
from typing import Any

from app.services.instrument_task_contract import load_instrument_task_contract
_TIMED_KINDS = {"steady_beat", "rhythm_echo", "melody_sequence", "ensemble_cue"}
_TIMING_PRESETS = {
    "lower_primary": (0.18, 100, 180, 0.32, 180, 300),
    "middle_primary": (0.15, 90, 150, 0.28, 160, 260),
    "upper_primary": (0.12, 75, 120, 0.24, 130, 220),
}


def validate_instrument_task(task: dict[str, Any]) -> None:
    contract = load_instrument_task_contract()
    if task.get("version") != contract["version"]:
        raise ValueError("unsupported instrument task version")
    if task.get("kind") not in contract["taskKinds"]:
        raise ValueError("unsupported instrument task kind")
    if not str(task.get("id") or "").strip() or not str(task.get("instrumentId") or "").strip():
        raise ValueError("instrument task id and instrumentId are required")
    if task.get("gradePreset") not in contract["gradePresets"]:
        raise ValueError("instrument task gradePreset must be lower_primary, middle_primary, or upper_primary")
    bpm = task.get("bpm")
    if bpm is not None and (not _is_finite_number(bpm) or bpm < 40 or bpm > 240):
        raise ValueError("instrument task BPM must be between 40 and 240")
    targets = task.get("targetEvents") or []
    if task.get("kind") in _TIMED_KINDS and not targets:
        raise ValueError(f"{task['kind']} requires targetEvents")
    for target in targets:
        if not str(target.get("id") or "") or not _is_finite_number(target.get("offsetBeats")) or target["offsetBeats"] < 0:
            raise ValueError("every target event requires a non-negative beat offset")
        if target.get("zoneId") is None and target.get("midi") is None:
            raise ValueError("every target event requires zoneId or midi")
        if target.get("midi") is not None and not _is_finite_number(target["midi"]):
            raise ValueError("every target event MIDI must be finite")
    _validate_composition_midi_rules(task.get("compositionRules"))
    _validate_composition_rest_rules(task.get("kind"), task.get("compositionRules"))


def evaluate_instrument_task(task: dict[str, Any], performance_events: list[dict[str, Any]]) -> dict[str, Any]:
    validate_instrument_task(task)
    _validate_performance_events(performance_events)
    events = []
    for original_index, event in enumerate(performance_events):
        copied = deepcopy(event)
        copied["_event_index"] = original_index
        events.append(copied)
    events.sort(key=lambda item: (float(item.get("timeMs", 0)), item["_event_index"]))
    if task["kind"] == "free_play":
        return _participation_evidence(task, len(events))
    if task["kind"] == "constrained_composition":
        return evaluate_composition_constraints(task, events)
    return evaluate_timed_instrument_sequence(task, events)


def evaluate_timed_instrument_sequence(task: dict[str, Any], performance_events: list[dict[str, Any]]) -> dict[str, Any]:
    bpm = float(task.get("bpm") or 100)
    beat_ms = 60000 / bpm
    windows = _resolve_grade_timing_windows(bpm, str(task.get("gradePreset") or "middle_primary"))
    targets = list(task.get("targetEvents") or [])
    matched: set[int] = set()
    results: list[dict[str, Any]] = []
    correct_count = early_count = late_count = extra_count = 0
    for fallback_index, event in enumerate(performance_events):
        event_index = int(event.get("_event_index", fallback_index))
        candidates = []
        for target_index, target in enumerate(targets):
            offset = float(event.get("timeMs", 0)) - float(target["offsetBeats"]) * beat_ms
            if target_index not in matched and _matches_target(event, target) and abs(offset) <= windows["outer_ms"]:
                candidates.append((abs(offset), target_index, target, offset))
        if not candidates:
            extra_count += 1
            results.append({"event_index": event_index, "status": "extra"})
            continue
        _, target_index, target, offset = min(candidates, key=lambda item: item[0])
        matched.add(target_index)
        if abs(offset) <= windows["correct_ms"]:
            status = "correct"; correct_count += 1
        elif offset < 0:
            status = "early"; early_count += 1
        else:
            status = "late"; late_count += 1
        results.append({"event_index": event_index, "status": status, "target_id": target["id"], "offset_ms": offset})
    missed_target_ids = [target["id"] for index, target in enumerate(targets) if index not in matched]
    return build_instrument_performance_evidence(task, {
        "correct_count": correct_count, "early_count": early_count, "late_count": late_count, "extra_count": extra_count, "rest_error_count": 0,
        "missed_count": len(missed_target_ids), "participation_count": len(performance_events), "matched_target_count": len(matched),
        "missed_target_ids": missed_target_ids, "violations": [], "event_results": results,
    })


def evaluate_composition_constraints(task: dict[str, Any], performance_events: list[dict[str, Any]]) -> dict[str, Any]:
    rules = task.get("compositionRules") or {}
    violations: list[str] = []
    event_results: list[dict[str, Any]] = []
    rest_error_count = 0
    beat_ms = 60000 / float(task.get("bpm") or 100)
    for fallback_index, event in enumerate(performance_events):
        if rules.get("allowedZoneIds") and event.get("zoneId") not in rules["allowedZoneIds"]:
            violations.append(f"zone_not_allowed:{event.get('zoneId', 'none')}")
        if rules.get("allowedMidi") and event.get("midi") not in rules["allowedMidi"]:
            violations.append(f"midi_not_allowed:{event.get('midi', 'none')}")
        event_beat = float(event.get("timeMs", 0)) / beat_ms
        rest_window_index = next((index for index, window in enumerate(rules.get("restWindowsBeats") or []) if window[0] <= event_beat < window[1]), None)
        if rest_window_index is not None:
            rest_error_count += 1
            violations.append(f"rest_window_played:{rest_window_index}")
            event_results.append({"event_index": int(event.get("_event_index", fallback_index)), "status": "rest_error"})
    event_count = rules.get("requiredEventCount") or {}
    if event_count and not (event_count.get("min", 0) <= len(performance_events) <= event_count.get("max", len(performance_events))):
        violations.append(f"event_count_required:{event_count.get('min', 0)}-{event_count.get('max', len(performance_events))}")
    if rules.get("endingMidi") is not None and (not performance_events or performance_events[-1].get("midi") != rules["endingMidi"]):
        violations.append(f"ending_midi_required:{rules['endingMidi']}")
    if rules.get("requiredBeats") is not None and performance_events:
        last_beat = float(performance_events[-1].get("timeMs", 0)) / (60000 / float(task.get("bpm") or 100))
        if last_beat > rules["requiredBeats"]:
            violations.append(f"duration_beats_exceeded:{rules['requiredBeats']}")
    return build_instrument_performance_evidence(task, {
        "correct_count": 0, "early_count": 0, "late_count": 0, "extra_count": 0, "missed_count": 0, "rest_error_count": rest_error_count,
        "participation_count": len(performance_events), "matched_target_count": 0, "missed_target_ids": [], "violations": violations,
        "event_results": event_results,
    })


def build_instrument_performance_evidence(task: dict[str, Any], counts: dict[str, Any]) -> dict[str, Any]:
    needs_adjustment = bool(counts["violations"] or counts["early_count"] or counts["late_count"] or counts["extra_count"] or counts["missed_count"] or counts["rest_error_count"])
    return {"version": "virtual_instrument_task_attempt_v1", "task_id": task["id"], "kind": task["kind"], "evidence_status": "adjust" if needs_adjustment else "evidence_pass", **counts}


def _participation_evidence(task: dict[str, Any], participation_count: int) -> dict[str, Any]:
    return {"version": "virtual_instrument_task_attempt_v1", "task_id": task["id"], "kind": task["kind"], "evidence_status": "participation_only", "correct_count": 0, "early_count": 0, "late_count": 0, "extra_count": 0, "missed_count": 0, "rest_error_count": 0, "participation_count": participation_count, "matched_target_count": 0, "missed_target_ids": [], "violations": [], "event_results": []}


def _matches_target(event: dict[str, Any], target: dict[str, Any]) -> bool:
    return (target.get("zoneId") is None or target.get("zoneId") == event.get("zoneId")) and (target.get("midi") is None or target.get("midi") == event.get("midi"))


def _validate_composition_rest_rules(kind: Any, rules: Any) -> None:
    if isinstance(rules, dict) and ({"restWindowsBeats", "requiredRestCount"} & rules.keys()) and kind != "constrained_composition":
        raise ValueError("restWindowsBeats and requiredRestCount are only supported by constrained_composition tasks")
    if not isinstance(rules, dict) or "restWindowsBeats" not in rules:
        return
    rest_windows = rules["restWindowsBeats"]
    if not isinstance(rest_windows, list):
        raise ValueError("restWindowsBeats must be a list of [startBeat, endBeat) ranges")
    for window in rest_windows:
        if not isinstance(window, list) or len(window) != 2 or not all(isinstance(value, (int, float)) and isfinite(value) for value in window) or window[0] < 0 or window[1] <= window[0]:
            raise ValueError("every rest window must be [startBeat, endBeat) with a non-negative start and later end")
    required_rest_count = rules.get("requiredRestCount")
    if required_rest_count is None:
        return
    if not isinstance(required_rest_count, dict):
        raise ValueError("requiredRestCount must be a { min, max } range")
    minimum, maximum = required_rest_count.get("min"), required_rest_count.get("max")
    if not isinstance(minimum, int) or not isinstance(maximum, int) or minimum < 0 or maximum < minimum or not minimum <= len(rest_windows) <= maximum:
        raise ValueError("requiredRestCount must contain the supplied restWindowsBeats count")


def _validate_composition_midi_rules(rules: Any) -> None:
    if not isinstance(rules, dict):
        return
    if any(not _is_finite_number(midi) for midi in rules.get("allowedMidi") or []):
        raise ValueError("allowedMidi values must be finite")
    if rules.get("endingMidi") is not None and not _is_finite_number(rules["endingMidi"]):
        raise ValueError("endingMidi must be finite")


def _validate_performance_events(events: list[dict[str, Any]]) -> None:
    for event in events:
        if not isinstance(event, dict) or not _is_finite_number(event.get("timeMs")) or event["timeMs"] < 0:
            raise ValueError("every student event requires a finite, non-negative timeMs")
        if event.get("midi") is not None and not _is_finite_number(event["midi"]):
            raise ValueError("every student event MIDI must be finite")


def _is_finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and isfinite(value)


def _resolve_grade_timing_windows(bpm: float, grade_preset: str) -> dict[str, int]:
    correct_ratio, correct_min, correct_max, outer_ratio, outer_min, outer_max = _TIMING_PRESETS.get(grade_preset, _TIMING_PRESETS["middle_primary"])
    beat_ms = 60000 / max(40, min(180, bpm))
    return {
        "correct_ms": _round_nonnegative_like_javascript(max(correct_min, min(correct_max, beat_ms * correct_ratio))),
        "outer_ms": _round_nonnegative_like_javascript(max(outer_min, min(outer_max, beat_ms * outer_ratio))),
    }


def _round_nonnegative_like_javascript(value: float) -> int:
    """Match Math.round for the non-negative timing windows used by this evaluator."""
    return int(value + 0.5)
