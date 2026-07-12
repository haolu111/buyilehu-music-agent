from __future__ import annotations

import shutil
from pathlib import Path


def resolve_ffmpeg_command() -> str:
    command = shutil.which("ffmpeg")
    if command:
        return command
    try:
        import imageio_ffmpeg

        candidate = Path(imageio_ffmpeg.get_ffmpeg_exe())
    except Exception:
        return ""
    if candidate.exists() and candidate.is_file():
        return str(candidate)
    return ""


def ensure_ffmpeg_on_path() -> str:
    command = resolve_ffmpeg_command()
    if not command:
        return ""
    import os

    command_dir = str(Path(command).parent)
    paths = os.environ.get("PATH", "").split(os.pathsep)
    if command_dir not in paths:
        os.environ["PATH"] = command_dir + os.pathsep + os.environ.get("PATH", "")
    return command
