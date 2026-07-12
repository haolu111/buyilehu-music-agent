from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess
import tempfile
from typing import Any

from app.services.core.runtime_tools import resolve_ffmpeg_command


MIN_PLAYBACK_RATE = 0.5
MAX_PLAYBACK_RATE = 1.25
MIN_TRANSPOSE_SEMITONES = -6
MAX_TRANSPOSE_SEMITONES = 6


def normalize_media_transform(*, playback_rate: float, transpose_semitones: int) -> dict[str, Any]:
    return {
        "playback_rate": max(MIN_PLAYBACK_RATE, min(MAX_PLAYBACK_RATE, float(playback_rate))),
        "transpose_semitones": max(MIN_TRANSPOSE_SEMITONES, min(MAX_TRANSPOSE_SEMITONES, int(transpose_semitones))),
    }


def build_ffmpeg_audio_filter(*, playback_rate: float, transpose_semitones: int) -> str:
    transform = normalize_media_transform(
        playback_rate=playback_rate,
        transpose_semitones=transpose_semitones,
    )
    rate = float(transform["playback_rate"])
    semitones = int(transform["transpose_semitones"])
    filters: list[str] = []
    if semitones:
        factor = 2 ** (semitones / 12)
        filters.extend(
            [
                f"asetrate=44100*{factor:.6f}",
                "aresample=44100",
                f"atempo={1 / factor:.6f}",
            ]
        )
    filters.append(f"atempo={rate:.6f}")
    return ",".join(filters)


def build_media_variant_cache_key(
    source_bytes: bytes,
    *,
    playback_rate: float,
    transpose_semitones: int,
) -> str:
    transform = normalize_media_transform(
        playback_rate=playback_rate,
        transpose_semitones=transpose_semitones,
    )
    digest = hashlib.sha256()
    digest.update(source_bytes)
    digest.update(f"|{transform['playback_rate']:.4f}|{transform['transpose_semitones']}".encode("utf-8"))
    return digest.hexdigest()[:24]


def render_media_variant(
    source_bytes: bytes,
    *,
    source_suffix: str,
    output_dir: Path,
    playback_rate: float,
    transpose_semitones: int,
) -> dict[str, Any]:
    ffmpeg = resolve_ffmpeg_command()
    if not ffmpeg:
        raise RuntimeError("ffmpeg_unavailable")
    suffix = source_suffix.lower() if source_suffix.lower() in {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac"} else ".audio"
    cache_key = build_media_variant_cache_key(
        source_bytes,
        playback_rate=playback_rate,
        transpose_semitones=transpose_semitones,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{cache_key}.mp3"
    if output_path.exists() and output_path.stat().st_size > 0:
        return {"path": output_path, "cache_key": cache_key, "cached": True}
    audio_filter = build_ffmpeg_audio_filter(
        playback_rate=playback_rate,
        transpose_semitones=transpose_semitones,
    )
    with tempfile.TemporaryDirectory(prefix="music-media-") as directory:
        input_path = Path(directory) / f"source{suffix}"
        input_path.write_bytes(source_bytes)
        command = [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-i",
            str(input_path),
            "-vn",
            "-af",
            audio_filter,
            "-codec:a",
            "libmp3lame",
            "-q:a",
            "3",
            str(output_path),
        ]
        completed = subprocess.run(command, capture_output=True, text=True, timeout=90, check=False)
        if completed.returncode != 0 or not output_path.exists():
            output_path.unlink(missing_ok=True)
            raise RuntimeError(f"ffmpeg_failed:{completed.stderr.strip()[:300]}")
    return {"path": output_path, "cache_key": cache_key, "cached": False}
