from __future__ import annotations

from copy import deepcopy
from math import isfinite
from typing import Any
from uuid import uuid4

from app.services.instruments.virtual_instrument_catalog_v2 import (
    get_virtual_instrument_v2,
    resolve_virtual_instrument_v2_id,
)


TASK_KINDS = {
    "free_play",
    "steady_beat",
    "rhythm_echo",
    "melody_sequence",
    "ensemble_cue",
    "constrained_composition",
}


def build_instrument_task(spec: dict[str, Any]) -> dict[str, Any]:
    kind = str(spec.get("kind") or "free_play")
    if kind not in TASK_KINDS:
        raise ValueError(f"unsupported instrument task kind: {kind}")
    instrument_id = resolve_virtual_instrument_v2_id(
        spec.get("instrumentId") or _default_instrument(kind)
    )
    grade = str(spec.get("gradePreset") or "middle_primary")
    if grade not in {"lower_primary", "middle_primary", "upper_primary"}:
        raise ValueError("invalid instrument task gradePreset")
    bpm = max(40, min(180, _number(spec.get("bpm"), 88)))
    task = {
        "version": "teacher_constrained_instrument_task_v1",
        "id": str(spec.get("id") or f"instrument-task-{uuid4().hex[:10]}"),
        "kind": kind,
        "instrumentId": instrument_id,
        "gradePreset": grade,
        "bpm": bpm,
        "prompt": str(spec.get("prompt") or _default_prompt(kind)),
        "targetEvents": deepcopy(spec.get("targetEvents") or _default_targets(kind)),
        "compositionRules": deepcopy(spec.get("compositionRules") or {}),
        "teacherJudgements": [
            "musical_expression",
            "technique",
            "ensemble_balance",
            "creation_reason",
        ],
    }
    instrument = get_virtual_instrument_v2(instrument_id)
    return {
        "task": task,
        "instrument": instrument,
        "runtime": {
            "schemaVersion": "interactive-node-runtime.v2",
            "nodeType": "instrument_task",
            "family": "virtual_instrument",
            "variant": kind,
            "renderer": "virtual-instrument",
            "legacyRenderer": "virtual-instrument",
            "props": {
                "prompt": task["prompt"],
                "task": task,
                "instrument": instrument,
                "keys": _keys(instrument),
            },
            "assets": [],
            "assessment": {
                "mode": "instrument_evidence",
                "resultType": "instrument_task",
                "maxScore": 100,
                "task": task,
                "teacherConfirmationRequired": kind in {
                    "free_play", "ensemble_cue", "constrained_composition"
                },
            },
            "mediaSession": None,
        },
    }


def evaluate_instrument_task(task: dict[str, Any], events: list[dict[str, Any]]) -> dict[str, Any]:
    kind = str(task.get("kind") or "")
    if kind == "free_play":
        return _evidence(task, events, len(events), 0, "participation_only")
    targets = task.get("targetEvents") if isinstance(task.get("targetEvents"), list) else []
    if not targets:
        return _evidence(task, events, 0, len(events), "adjust")
    bpm = _number(task.get("bpm"), 88)
    beat_ms = 60000 / bpm
    tolerance = 220 if task.get("gradePreset") == "lower_primary" else 170
    matched: set[int] = set()
    correct = 0
    for event in events:
        time_ms = _number(event.get("timeMs"), -1)
        if time_ms < 0:
            continue
        candidates = [
            (abs(time_ms - _number(target.get("offsetBeats"), 0) * beat_ms), index)
            for index, target in enumerate(targets)
            if index not in matched and _same_key(event, target)
        ]
        if candidates:
            distance, index = min(candidates)
            if distance <= tolerance:
                matched.add(index)
                correct += 1
    errors = max(0, len(targets) - correct) + max(0, len(events) - correct)
    return _evidence(task, events, correct, errors, "evidence_pass" if errors == 0 else "adjust")


def _evidence(
    task: dict[str, Any], events: list[dict[str, Any]], correct: int, errors: int, status: str
) -> dict[str, Any]:
    total = max(1, correct + errors)
    return {
        "version": "virtual_instrument_task_attempt_v1",
        "task_id": task.get("id"),
        "kind": task.get("kind"),
        "evidence_status": status,
        "correct_count": correct,
        "error_count": errors,
        "participation_count": len(events),
        "objective_score": round(100 * correct / total) if status != "participation_only" else None,
        "teacher_judgement_required": status == "participation_only"
        or task.get("kind") in {"ensemble_cue", "constrained_composition"},
    }


def _same_key(event: dict[str, Any], target: dict[str, Any]) -> bool:
    return (
        target.get("zoneId") is None or event.get("zoneId") == target.get("zoneId")
    ) and (target.get("midi") is None or event.get("midi") == target.get("midi"))


def _default_instrument(kind: str) -> str:
    return "virtual_piano" if kind == "melody_sequence" else "virtual_frame_drum"


def _default_prompt(kind: str) -> str:
    return {
        "free_play": "自由探索乐器音色，并说说你听到的特点。",
        "steady_beat": "跟随稳定拍，在每个拍点敲击一次。",
        "rhythm_echo": "先听节奏，再用乐器完整模仿。",
        "melody_sequence": "按照给出的音高顺序弹奏旋律。",
        "ensemble_cue": "观察指挥提示，在指定拍点进入。",
        "constrained_composition": "在教师给定的音和节拍范围内完成创编。",
    }[kind]


def _default_targets(kind: str) -> list[dict[str, Any]]:
    if kind == "melody_sequence":
        return [
            {"id": "n1", "offsetBeats": 0, "midi": 60},
            {"id": "n2", "offsetBeats": 1, "midi": 62},
            {"id": "n3", "offsetBeats": 2, "midi": 64},
            {"id": "n4", "offsetBeats": 3, "midi": 67},
        ]
    if kind in {"steady_beat", "rhythm_echo", "ensemble_cue"}:
        return [
            {"id": f"b{index + 1}", "offsetBeats": index, "zoneId": "center"}
            for index in range(4)
        ]
    return []


def _keys(instrument: dict[str, Any]) -> list[dict[str, Any]]:
    zones = instrument.get("zones") if isinstance(instrument.get("zones"), list) else []
    keys = []
    for index, zone in enumerate(zones[:12]):
        midi = zone.get("midi")
        keys.append({
            "note": str(zone.get("id") or midi or index),
            "label": str(zone.get("label") or zone.get("name") or zone.get("id") or index + 1),
            "frequency": 440 * (2 ** ((_number(midi, 69) - 69) / 12)),
            "color": ["#e85d4a", "#ed9b2d", "#54a96b", "#3285b5", "#7659a8"][index % 5],
            "zoneId": zone.get("id"),
            "midi": midi,
        })
    if keys:
        return keys
    return [
        {"note": note, "label": note, "frequency": frequency, "color": color, "midi": midi}
        for note, frequency, color, midi in [
            ("do", 261.63, "#e85d4a", 60),
            ("re", 293.66, "#ed9b2d", 62),
            ("mi", 329.63, "#54a96b", 64),
            ("sol", 392.0, "#3285b5", 67),
        ]
    ]


def _number(value: Any, fallback: float) -> float:
    try:
        result = float(value)
        return result if isfinite(result) else fallback
    except (TypeError, ValueError):
        return fallback
