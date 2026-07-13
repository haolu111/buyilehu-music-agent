# 统一音高、唱名和 MIDI 编号之间的转换
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import re
from typing import Any, Optional


_CATALOG_PATH = Path(__file__).resolve().parents[3] / "contracts" / "music" / "pitch-catalog.v1.json"
_CATALOG: dict[str, Any] = json.loads(_CATALOG_PATH.read_text(encoding="utf-8"))

PITCH_CATALOG_VERSION = str(_CATALOG["version"])
DEFAULT_TONIC_MIDI = int(_CATALOG["defaultTonicMidi"])
PITCH_DEFINITIONS: tuple[dict[str, Any], ...] = tuple(deepcopy(_CATALOG["pitches"]))
PITCH_CLASS_DEFINITIONS: tuple[dict[str, Any], ...] = tuple(
    pitch for pitch in PITCH_DEFINITIONS if pitch["role"] == "pitch_class"
)
PITCH_REGISTERS: tuple[dict[str, Any], ...] = tuple(deepcopy(_CATALOG["registers"]))
REGISTERED_PITCH_DEFINITIONS: tuple[dict[str, Any], ...] = tuple(
    {
        "id": f'{register["id"]}:{pitch["id"]}',
        "pitchId": str(pitch["id"]),
        "registerId": str(register["id"]),
        "midi": int(register["baseMidi"]) + int(pitch["semitone"]),
        "semitone": int(pitch["semitone"]),
        "numberLabels": deepcopy(pitch["numberLabels"]),
        "scientificLabels": [
            f'{name}{register["scientificOctave"]}' for name in pitch["letterNames"]
        ],
    }
    for register in PITCH_REGISTERS
    for pitch in PITCH_CLASS_DEFINITIONS
)

_PITCH_BY_ALIAS: dict[str, dict[str, Any]] = {}
for _pitch in PITCH_DEFINITIONS:
    for _alias in (
        _pitch["id"],
        *_pitch["numberLabels"],
        *_pitch["solfegeAliases"],
        *_pitch["inputAliases"],
    ):
        _PITCH_BY_ALIAS[str(_alias).strip().casefold()] = _pitch


def _normalize_registered_pitch_token(token: Any) -> str:
    normalized = str(token or "").strip().casefold()
    normalized = re.sub(r"([a-g])#", r"\1♯", normalized)
    return re.sub(r"([a-g])b", r"\1♭", normalized)


_REGISTERED_PITCH_BY_ALIAS: dict[str, dict[str, Any]] = {}
for _registered_pitch in REGISTERED_PITCH_DEFINITIONS:
    for _alias in (_registered_pitch["id"], *_registered_pitch["scientificLabels"]):
        _REGISTERED_PITCH_BY_ALIAS[_normalize_registered_pitch_token(_alias)] = _registered_pitch

_PITCH_TEXT_TOKEN_RE = re.compile(
    r"(?i)(?:[#♯升b♭降]\s*[1-7]|(?<!\d)[1-7](?:['’])?(?!\d)|\b(?:do_high|do['’]?|re|mi|fa|sol|so|la|si|ti)\b)"
)


def resolve_pitch_token(token: Any) -> Optional[dict[str, Any]]:
    return _PITCH_BY_ALIAS.get(str(token or "").strip().casefold())


def resolve_registered_pitch_token(token: Any) -> Optional[dict[str, Any]]:
    return _REGISTERED_PITCH_BY_ALIAS.get(_normalize_registered_pitch_token(token))


def pitch_to_midi(token: Any, tonic_midi: int = DEFAULT_TONIC_MIDI) -> int:
    pitch = resolve_pitch_token(token)
    if pitch is None:
        raise ValueError(f"Unknown pitch token: {token}")
    return round(float(tonic_midi)) + int(pitch["semitone"])


def registered_pitch_to_midi(token: Any) -> int:
    pitch = resolve_registered_pitch_token(token)
    if pitch is None:
        raise ValueError(f"Unknown registered pitch token: {token}")
    return int(pitch["midi"])


def sequence_to_midi_offsets(tokens: list[Any]) -> list[int]:
    offsets: list[int] = []
    for token in tokens:
        pitch = resolve_pitch_token(token)
        if pitch is None:
            raise ValueError(f"Unknown pitch token: {token}")
        offsets.append(int(pitch["semitone"]))
    return offsets


def pitch_tokens_from_text(text: str, *, unique: bool = True) -> list[str]:
    tokens: list[str] = []
    for match in _PITCH_TEXT_TOKEN_RE.finditer(str(text or "")):
        pitch = resolve_pitch_token(re.sub(r"\s+", "", match.group(0)))
        if pitch is None:
            continue
        pitch_id = str(pitch["id"])
        if not unique or pitch_id not in tokens:
            tokens.append(pitch_id)
    return tokens
