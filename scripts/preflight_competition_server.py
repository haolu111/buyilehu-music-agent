from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from app.main import _competition_readiness, _import_status  # noqa: E402
from app.services.auth_store import smtp_config_status  # noqa: E402
from app.services.opencode_runtime import opencode_status  # noqa: E402
from app.services.runtime_tools import resolve_ffmpeg_command  # noqa: E402
from app.services.song_material_parser import score_omr_status  # noqa: E402


def main() -> int:
    audio_tools = {
        "ffmpeg": resolve_ffmpeg_command(),
        "fluidsynth": _which("fluidsynth"),
    }
    status = _competition_readiness(
        opencode=opencode_status(),
        basic_pitch=_import_status("basic_pitch.inference"),
        score_omr=score_omr_status(),
        audio_tools=audio_tools,
        smtp=smtp_config_status(),
    )
    print(json.dumps(status, ensure_ascii=False, indent=2))
    if status.get("ready"):
        print("\nOK: competition preflight passed. Judges should only need the public URL.")
        return 0
    print("\nFAIL: competition preflight found blocking items. Fix them before submitting the URL.")
    return 1


def _which(command: str) -> str:
    from shutil import which

    return which(command) or ""


if __name__ == "__main__":
    raise SystemExit(main())
