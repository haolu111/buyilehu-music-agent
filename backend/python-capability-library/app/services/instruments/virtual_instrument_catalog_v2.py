from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any


_CONTRACT_ROOT = Path(__file__).resolve().parents[3] / "contracts" / "music"
_CATALOG = json.loads((_CONTRACT_ROOT / "virtual-instrument-catalog.v2.json").read_text(encoding="utf-8"))
_LICENSE_MANIFEST = json.loads((_CONTRACT_ROOT / "instrument-audio-license-manifest.v1.json").read_text(encoding="utf-8"))

VIRTUAL_INSTRUMENT_CATALOG_VERSION = str(_CATALOG["version"])
AUDIO_LICENSE_MANIFEST_VERSION = str(_LICENSE_MANIFEST["version"])
VIRTUAL_INSTRUMENT_DEFINITIONS: tuple[dict[str, Any], ...] = tuple(deepcopy(_CATALOG["instruments"]))
PERCUSSION_GRID_DEFINITION: dict[str, Any] = deepcopy(_CATALOG["percussionGrid"])

_BY_ID = {str(item["id"]): item for item in VIRTUAL_INSTRUMENT_DEFINITIONS}
_ALIASES = {str(key): str(value) for key, value in _CATALOG.get("legacyAliases", {}).items()}


def resolve_virtual_instrument_v2_id(value: Any) -> str:
    instrument_id = str(value or "").strip()
    resolved = _ALIASES.get(instrument_id, instrument_id)
    if resolved not in _BY_ID:
        raise ValueError(f"unknown virtual instrument v2 id: {value}")
    return resolved


def get_virtual_instrument_v2(instrument_id: Any) -> dict[str, Any]:
    return deepcopy(_BY_ID[resolve_virtual_instrument_v2_id(instrument_id)])


def list_virtual_instruments_v2() -> list[dict[str, Any]]:
    return [deepcopy(item) for item in VIRTUAL_INSTRUMENT_DEFINITIONS]


def list_instrument_audio_assets() -> list[dict[str, Any]]:
    return deepcopy(_LICENSE_MANIFEST.get("assets", []))


def list_audited_instrument_audio_assets() -> list[dict[str, Any]]:
    return [
        item for item in list_instrument_audio_assets()
        if item.get("status") == "audited" and item.get("instrumentId") in _BY_ID
    ]


def get_audited_classroom_audio_asset(instrument_or_utility_id: str) -> dict[str, Any] | None:
    return next(
        (
            item for item in list_instrument_audio_assets()
            if item.get("status") == "audited" and item.get("instrumentId") == instrument_or_utility_id
        ),
        None,
    )
