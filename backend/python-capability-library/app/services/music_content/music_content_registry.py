from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any


def _contract_payload(file_name: str) -> dict[str, Any]:
    source = Path(__file__).resolve()
    search_roots = [Path.cwd(), *source.parents]
    contract_path = next(
        (
            root / "contracts" / "music-content" / file_name
            for root in search_roots
            if (root / "contracts" / "music-content" / file_name).is_file()
        ),
        None,
    )
    if contract_path is None:
        raise RuntimeError(f"shared music-content contract is missing: contracts/music-content/{file_name}")
    return json.loads(contract_path.read_text(encoding="utf-8"))


def _load_meter_catalog() -> dict[str, dict[str, Any]]:
    payload = _contract_payload("meters.json")
    return {
        meter_id: {
            "id": meter_id,
            "signature": item["signature"],
            "beatsPerBar": item["beats_per_bar"],
            "beatUnit": item["beat_unit"],
            "accentPattern": list(item["accent_pattern"]),
        }
        for meter_id, item in payload["meters"].items()
    }


METER_CATALOG = _load_meter_catalog()
ELEMENT_CATALOG = _contract_payload("elements.json")

METER_CAPABLE_ENTITIES: dict[str, dict[str, Any]] = {
    "rhythm_warmup": {"meter_ids": list(METER_CATALOG), "bpm": [50, 120], "bars": [1, 8]},
    "meter_body_movement": {"meter_ids": list(METER_CATALOG), "bpm": [50, 110], "bars": [1, 8]},
    "strong_weak_beat_circle": {"meter_ids": list(METER_CATALOG), "bpm": [50, 110], "bars": [1, 8]},
    "steady_beat_walk": {"meter_ids": list(METER_CATALOG), "bpm": [50, 120], "bars": [1, 8]},
    "rhythm_question_answer": {"meter_ids": list(METER_CATALOG), "bpm": [50, 120], "bars": [1, 8]},
    "body_percussion_builder": {"meter_ids": list(METER_CATALOG), "bpm": [50, 120], "bars": [1, 8]},
    "lyrics_rhythm_reading": {"meter_ids": list(METER_CATALOG), "bpm": [50, 110], "bars": [1, 8]},
    "simple_score_following": {"meter_ids": list(METER_CATALOG), "bpm": [50, 110], "bars": [1, 8]},
    "graphic_score_create": {"meter_ids": list(METER_CATALOG), "bpm": [50, 120], "bars": [1, 8]},
    "xylophone_creation": {"meter_ids": list(METER_CATALOG), "bpm": [50, 120], "bars": [1, 8]},
    "orff_percussion_ensemble": {"meter_ids": list(METER_CATALOG), "bpm": [50, 120], "bars": [1, 8]},
    "group_relay_performance": {"meter_ids": list(METER_CATALOG), "bpm": [50, 120], "bars": [1, 8]},
    "beat_guardian_core": {"meter_ids": list(METER_CATALOG), "bpm": [50, 120], "bars": [1, 8]},
    "rhythm_echo_core": {"meter_ids": list(METER_CATALOG), "bpm": [50, 120], "bars": [1, 8]},
    "virtual_frame_drum": {"meter_ids": list(METER_CATALOG), "bpm": [40, 140], "bars": [1, 16]},
    "instrument_task:steady_beat": {"meter_ids": list(METER_CATALOG), "bpm": [40, 140], "bars": [1, 16]},
    "instrument_task:rhythm_echo": {"meter_ids": list(METER_CATALOG), "bpm": [40, 140], "bars": [1, 16]},
    "instrument_task:melody_sequence": {"meter_ids": list(METER_CATALOG), "bpm": [40, 140], "bars": [1, 16]},
    "instrument_task:ensemble_cue": {"meter_ids": list(METER_CATALOG), "bpm": [40, 140], "bars": [1, 16]},
    "instrument_task:constrained_composition": {"meter_ids": list(METER_CATALOG), "bpm": [40, 140], "bars": [1, 16]},
}

_RHYTHM_ENTITIES = {
    "rhythm_warmup", "meter_body_movement", "strong_weak_beat_circle", "steady_beat_walk",
    "rhythm_question_answer", "body_percussion_builder", "lyrics_rhythm_reading",
    "simple_score_following", "graphic_score_create", "xylophone_creation",
    "orff_percussion_ensemble", "group_relay_performance", "beat_guardian_core",
    "rhythm_echo_core", "virtual_frame_drum",
    "instrument_task:steady_beat", "instrument_task:rhythm_echo",
    "instrument_task:melody_sequence", "instrument_task:ensemble_cue",
    "instrument_task:constrained_composition",
}
_PITCH_ENTITIES = {
    "solfege_sorting", "solfege_echo_singing", "melody_contour_trace",
    "simple_score_following", "xylophone_creation", "pitch_ladder_core",
    "virtual_xylophone", "virtual_piano",
    "instrument_task:free_play", "instrument_task:melody_sequence",
    "instrument_task:constrained_composition",
}
_MELODY_ENTITIES = {
    "phrase_singing_practice", "phrase_loop_singing", "solfege_echo_singing",
    "melody_contour_trace", "simple_score_following", "xylophone_creation",
    "pitch_ladder_core", "virtual_xylophone", "virtual_piano",
    "instrument_task:melody_sequence", "instrument_task:constrained_composition",
}
_FORM_ENTITIES = {
    "theme_return_action", "form_ordering", "form_treasure_core",
    "graphic_score_create", "composition_puzzle_core",
    "instrument_task:constrained_composition",
}
_DYNAMIC_ENTITIES = {
    "listen_choose_explain", "lesson_opening_hook", "graphic_score_create",
    "body_percussion_builder", "orff_percussion_ensemble",
    "group_relay_performance", "ensemble_conductor_rehearsal",
    "virtual_frame_drum", "virtual_xylophone", "virtual_piano",
    "instrument_task:free_play", "instrument_task:steady_beat",
    "instrument_task:rhythm_echo", "instrument_task:melody_sequence",
    "instrument_task:ensemble_cue", "instrument_task:constrained_composition",
}
_TIMBRE_ENTITIES = {
    "listen_choose_explain", "lesson_opening_hook", "instrument_timbre_match",
    "instrument_family_sorting", "orff_percussion_ensemble",
    "classroom_band_roles", "ensemble_conductor_rehearsal",
    "timbre_detective_core", "xylophone_creation",
    "virtual_frame_drum", "virtual_xylophone", "virtual_piano",
    "instrument_task:free_play", "instrument_task:melody_sequence",
    "instrument_task:ensemble_cue", "instrument_task:constrained_composition",
}


def _ids(section: str) -> list[str]:
    return list(ELEMENT_CATALOG[section])


def _element_capability(entity_id: str) -> dict[str, Any]:
    capability = deepcopy(METER_CAPABLE_ENTITIES.get(entity_id, {}))
    if entity_id in _RHYTHM_ENTITIES:
        capability["rhythm_pattern_ids"] = _ids("rhythm_patterns")
    if entity_id in _PITCH_ENTITIES:
        capability["pitch_set_ids"] = _ids("pitch_sets")
    if entity_id in _MELODY_ENTITIES:
        capability["melody_phrase_ids"] = _ids("melody_phrases")
    if entity_id in _FORM_ENTITIES:
        capability["form_ids"] = _ids("forms")
    if entity_id in _DYNAMIC_ENTITIES:
        capability["dynamic_ids"] = _ids("dynamics")
    if entity_id in _TIMBRE_ENTITIES:
        capability["timbre_ids"] = _ids("timbres")
    return capability


def music_content_catalog() -> dict[str, Any]:
    return {
        "meters": deepcopy(METER_CATALOG),
        **deepcopy(ELEMENT_CATALOG),
    }


def capability_for(entity_id: str) -> dict[str, Any]:
    return _element_capability(entity_id)


def validate_and_resolve_music_content(
    *, entity_id: str, raw: Any, grade_band: str = "middle_primary",
) -> tuple[dict[str, Any], dict[str, Any]]:
    content = deepcopy(raw) if isinstance(raw, dict) else {}
    capability = _element_capability(entity_id)
    if not capability:
        if content:
            raise ValueError(f"{entity_id} does not accept music_content")
        return {}, {}

    normalized: dict[str, Any] = {}
    resolved: dict[str, Any] = {}
    if "meter_ids" in capability:
        meter_ids = _validated_ids(
            entity_id, content.get("meter_ids", ["meter_2_4"]),
            "meter_ids", METER_CATALOG, capability["meter_ids"],
        )
        bpm_default = 76 if grade_band == "lower_primary" else 84
        bpm = int(content.get("bpm", bpm_default))
        bpm_min, bpm_max = capability["bpm"]
        if not bpm_min <= bpm <= bpm_max:
            raise ValueError(f"{entity_id}.music_content.bpm must be {bpm_min}..{bpm_max}")
        bars = int(content.get("bars", 4))
        bars_min, bars_max = capability["bars"]
        if not bars_min <= bars <= bars_max:
            raise ValueError(f"{entity_id}.music_content.bars must be {bars_min}..{bars_max}")
        normalized.update({"meter_ids": meter_ids, "bpm": bpm, "bars": bars})
        resolved.update({
            "meters": [deepcopy(METER_CATALOG[item]) for item in meter_ids],
            "bpm": bpm, "bars": bars,
        })

    mappings = (
        ("rhythm_pattern_ids", "rhythm_patterns"),
        ("pitch_set_ids", "pitch_sets"),
        ("melody_phrase_ids", "melody_phrases"),
        ("form_ids", "forms"),
        ("dynamic_ids", "dynamics"),
        ("timbre_ids", "timbres"),
    )
    for field, section in mappings:
        if field not in content:
            continue
        if field not in capability:
            raise ValueError(f"{entity_id} does not support {field}")
        selected = _validated_ids(
            entity_id, content[field], field,
            ELEMENT_CATALOG[section], capability[field],
        )
        normalized[field] = selected
        resolved[section] = [
            {"id": item, **deepcopy(ELEMENT_CATALOG[section][item])}
            for item in selected
        ]
    return normalized, resolved


def _validated_ids(
    entity_id: str,
    value: Any,
    field: str,
    catalog: dict[str, Any],
    supported: list[str],
) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{entity_id}.music_content.{field} must be a non-empty list")
    selected = [str(item) for item in value]
    unknown = [item for item in selected if item not in catalog]
    if unknown:
        raise ValueError(f"{entity_id} references unknown {field}: {unknown[0]}")
    unsupported = [item for item in selected if item not in supported]
    if unsupported:
        raise ValueError(f"{entity_id} does not support {field}: {unsupported[0]}")
    return list(dict.fromkeys(selected))
