from __future__ import annotations

import json
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from typing import Any


_CONTRACT_PATH = Path(__file__).resolve().parents[2] / "contracts" / "music" / "teacher-constrained-instrument-task.v1.json"


@lru_cache(maxsize=1)
def _read_contract() -> dict[str, Any]:
    return json.loads(_CONTRACT_PATH.read_text(encoding="utf-8"))


def load_instrument_task_contract() -> dict[str, Any]:
    return deepcopy(_read_contract())
