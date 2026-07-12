from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any


_CATALOG_PATH = Path(__file__).resolve().parents[3] / "contracts" / "music" / "instrument-timbre-catalog.v1.json"
_CATALOG: dict[str, Any] = json.loads(_CATALOG_PATH.read_text(encoding="utf-8"))

INSTRUMENT_TIMBRE_CATALOG_VERSION = str(_CATALOG["version"])
SAMPLE_LIBRARY: dict[str, Any] = deepcopy(_CATALOG["sampleLibrary"])
EXACT_TIMBRE_DEFINITIONS: tuple[dict[str, Any], ...] = tuple(deepcopy(_CATALOG["exactTimbres"]))
PENDING_EXACT_TIMBRE_DEFINITIONS: tuple[dict[str, Any], ...] = tuple(
    deepcopy(_CATALOG["pendingExactTimbres"])
)


def list_exact_timbres() -> list[dict[str, Any]]:
    return deepcopy(list(EXACT_TIMBRE_DEFINITIONS))


def list_pending_exact_timbres() -> list[dict[str, Any]]:
    return deepcopy(list(PENDING_EXACT_TIMBRE_DEFINITIONS))
