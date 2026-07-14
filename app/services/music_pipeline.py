from __future__ import annotations

import json
import math
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

import librosa
import numpy as np
import pretty_midi
import soundfile as sf

from app.services.runtime_paths import get_output_dir, runtime_root
from app.services.runtime_tools import ensure_ffmpeg_on_path
from app.services.sf2_renderer import SF2RenderUnavailable, render_pretty_midi_with_sf2


TARGET_SAMPLE_RATE = 32000
DEMUCS_MODEL = os.environ.get("MUSIC_AGENT_DEMUCS_MODEL", "htdemucs")
HF_SOUNDFONT_REPO = os.environ.get("MUSIC_AGENT_SOUNDFONT_REPO", "projectlosangeles/soundfonts4u")
HF_SOUNDFONT_FILE = os.environ.get("MUSIC_AGENT_SOUNDFONT_FILE", "Essential Keys-C-v1.0.sf2")

TONIC_TO_PC = {
    "C": 0,
    "C#": 1,
    "Db": 1,
    "D": 2,
    "D#": 3,
    "Eb": 3,
    "E": 4,
    "F": 5,
    "F#": 6,
    "Gb": 6,
    "G": 7,
    "G#": 8,
    "Ab": 8,
    "A": 9,
    "A#": 10,
    "Bb": 10,
    "B": 11,
}

MODE_INTERVALS = {
    "western_major": [0, 2, 4, 5, 7, 9, 11],
    "western_minor": [0, 2, 3, 5, 7, 8, 10],
    "chinese_pentatonic": [0, 2, 4, 7, 9],
    "chinese_heptatonic": [0, 2, 4, 5, 7, 9, 11],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "blues": [0, 3, 5, 6, 7, 10],
}

MODE_LABELS = {
    "preserve": "保持原调式",
    "western_major": "西洋大调",
    "western_minor": "西洋小调",
    "chinese_pentatonic": "中国五声调式",
    "chinese_heptatonic": "中国七声调式",
    "dorian": "多利亚调式",
    "phrygian": "弗里吉亚调式",
    "blues": "布鲁斯调式",
}

INSTRUMENT_PROGRAMS = {
    "preserve": {
        "program": 0,
        "name": "保持原音色",
        "midi_name": "",
        "waveform": "triangle",
        "partials": [1.0, 0.34, 0.12],
        "attack": 0.012,
        "release": 0.24,
    },
    "piano": {
        "program": 0,
        "name": "钢琴",
        "midi_name": "Piano",
        "waveform": "triangle",
        "partials": [1.0, 0.34, 0.12],
        "attack": 0.012,
        "release": 0.24,
    },
    "violin": {
        "program": 40,
        "name": "小提琴",
        "midi_name": "Violin",
        "waveform": "saw",
        "partials": [0.8, 0.24, 0.08],
        "attack": 0.08,
        "release": 0.22,
    },
    "flute": {
        "program": 73,
        "name": "长笛",
        "midi_name": "Flute",
        "waveform": "sine",
        "partials": [1.0, 0.1, 0.04],
        "attack": 0.04,
        "release": 0.16,
    },
    "guzheng": {
        "program": 107,
        "name": "古筝",
        "midi_name": "Koto",
        "waveform": "triangle",
        "partials": [0.92, 0.38, 0.14],
        "attack": 0.006,
        "release": 0.48,
    },
}


@dataclass
class TransformationConfig:
    tonic: str
    mode: str
    tempo_multiplier: float
    rhythm_density: str
    instrument: str


class BasicPitchUnavailable(RuntimeError):
    pass


class StemSeparationUnavailable(RuntimeError):
    pass


class RenderUnavailable(RuntimeError):
    pass


def _safe_mkdir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _to_output_url(path: Path, output_mount_prefix: str = "/output") -> str:
    relative = path.resolve().relative_to(get_output_dir().resolve())
    return f"{output_mount_prefix}/{relative.as_posix()}"


def _ascii_slug(value: object, fallback: str) -> str:
    text = str(value or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = text.strip("._")
    return text or fallback


def _safe_extension(name: object, fallback: str = ".bin") -> str:
    suffix = Path(str(name or "")).suffix.lower()
    return suffix if suffix else fallback


def _copy_audio_into_workspace(audio_path: Path, workspace: Path) -> Path:
    target = workspace / f"source_audio{_safe_extension(audio_path.name, '.wav')}"
    if not target.exists():
        shutil.copy2(audio_path, target)
    return target


def _write_empty_reference_midi(workspace: Path, reason: str) -> tuple[Path, dict[str, Any]]:
    _safe_mkdir(workspace)
    midi_path = workspace / "source_audio_reference_only.mid"
    if not midi_path.exists():
        pretty_midi.PrettyMIDI().write(str(midi_path))
    return midi_path, {
        "note_events": 0,
        "analysis_quality": "unavailable",
        "symbolic_available": False,
        "requires_manual_confirmation": True,
        "warning": reason,
    }


def _ensure_reference_soundfont() -> dict[str, Any]:
    soundfont_dir = runtime_root() / "assets" / "soundfonts"
    _safe_mkdir(soundfont_dir)
    configured_soundfont = os.environ.get("MUSIC_AGENT_SOUNDFONT_PATH", "").strip()
    configured_path = Path(configured_soundfont).expanduser() if configured_soundfont else None
    if configured_path and configured_path.exists():
        return {
            "available": True,
            "backend": "local_env_path",
            "repo_id": "",
            "filename": configured_path.name,
            "path": str(configured_path),
        }

    cached_path = soundfont_dir / HF_SOUNDFONT_FILE
    cached_path.parent.mkdir(parents=True, exist_ok=True)
    if cached_path.exists():
        return {
            "available": True,
            "backend": "huggingface_hub_cache",
            "repo_id": HF_SOUNDFONT_REPO,
            "filename": HF_SOUNDFONT_FILE,
            "path": str(cached_path),
        }

    local_candidates = sorted(path for path in soundfont_dir.glob("*.sf2") if path.is_file())
    if local_candidates:
        local_path = local_candidates[0]
        return {
            "available": True,
            "backend": "runtime_local_sf2",
            "repo_id": "",
            "filename": local_path.name,
            "path": str(local_path),
        }

    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        hf_hub_download = None

    download_error = ""
    if hf_hub_download is not None:
        try:
            path = hf_hub_download(
                repo_id=HF_SOUNDFONT_REPO,
                filename=HF_SOUNDFONT_FILE,
                repo_type="dataset",
                local_dir=str(soundfont_dir),
            )
            return {
                "available": True,
                "backend": "huggingface_hub",
                "repo_id": HF_SOUNDFONT_REPO,
                "filename": HF_SOUNDFONT_FILE,
                "path": path,
            }
        except Exception as exc:
            download_error = str(exc)

    bundled_sf2 = Path(pretty_midi.__file__).resolve().parent / "TimGM6mb.sf2"
    if bundled_sf2.exists():
        return {
            "available": True,
            "backend": "bundled_pretty_midi_sf2",
            "repo_id": HF_SOUNDFONT_REPO,
            "filename": bundled_sf2.name,
            "path": str(bundled_sf2),
            "warning": download_error,
        }

    return {
        "available": False,
        "backend": "huggingface_hub_error" if download_error else "missing_huggingface_hub",
        "repo_id": HF_SOUNDFONT_REPO,
        "filename": HF_SOUNDFONT_FILE,
        "path": "",
        "error": download_error,
    }


def _note_score(note: pretty_midi.Note) -> float:
    duration = max(0.08, note.end - note.start)
    return duration * (0.8 + note.velocity / 127)


def _estimate_polyphony(notes: list[pretty_midi.Note]) -> float:
    if len(notes) < 2:
        return 0.0
    overlaps = 0
    for left, right in zip(notes, notes[1:]):
        if right.start < left.end - 0.03:
            overlaps += 1
    return overlaps / max(1, len(notes) - 1)


def _melody_focus_score(midi_path: Path) -> float:
    midi_data = pretty_midi.PrettyMIDI(str(midi_path))
    notes = sorted(
        [note for instrument in midi_data.instruments for note in instrument.notes if not instrument.is_drum],
        key=lambda item: (item.start, item.pitch),
    )
    if not notes:
        return float("-inf")

    total_weight = sum(_note_score(note) for note in notes)
    average_pitch = sum(note.pitch for note in notes) / len(notes)
    pitch_span = max(note.pitch for note in notes) - min(note.pitch for note in notes)
    polyphony = _estimate_polyphony(notes)
    return total_weight + average_pitch * 0.08 - polyphony * 45 - max(0, pitch_span - 28) * 0.25


def _run_demucs(audio_path: Path, workspace: Path) -> dict[str, Path]:
    demucs_root = workspace / "demucs"
    expected_dir = demucs_root / DEMUCS_MODEL / audio_path.stem
    expected_files = {
        name: expected_dir / f"{name}.wav" for name in ("vocals", "drums", "bass", "other")
    }
    if all(path.exists() for path in expected_files.values()):
        return expected_files

    try:
        import demucs  # noqa: F401
    except ImportError as exc:
        raise StemSeparationUnavailable("Demucs 还没有安装到当前环境。") from exc

    _safe_mkdir(demucs_root)
    command = [
        sys.executable,
        "-m",
        "demucs.separate",
        "-n",
        DEMUCS_MODEL,
        "--out",
        str(demucs_root),
        str(audio_path),
    ]
    env = dict(os.environ)
    env.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
    completed = subprocess.run(command, cwd=str(workspace), text=True, capture_output=True, check=False, env=env)
    if completed.returncode != 0:
        message = completed.stderr.strip() or completed.stdout.strip() or "Demucs 分轨失败。"
        raise StemSeparationUnavailable(message)

    if not all(path.exists() for path in expected_files.values()):
        raise StemSeparationUnavailable("Demucs 运行结束，但没有产出完整的 stems 文件。")
    return expected_files


def _mix_background_stems(stem_paths: dict[str, Path], excluded_stem: str, workspace: Path) -> Path | None:
    remaining = [path for stem_name, path in stem_paths.items() if stem_name != excluded_stem and path.exists()]
    if not remaining:
        return None

    background_path = workspace / f"background_without_{excluded_stem}.wav"
    if background_path.exists():
        return background_path

    mixed: np.ndarray | None = None
    for stem_path in remaining:
        audio, _ = librosa.load(str(stem_path), sr=TARGET_SAMPLE_RATE, mono=False)
        audio = _to_stereo(audio)
        if mixed is None:
            mixed = audio
            continue
        target_length = max(mixed.shape[-1], audio.shape[-1])
        mixed = _match_audio_length(mixed, target_length) + _match_audio_length(audio, target_length)

    if mixed is None:
        return None

    mixed *= 0.78
    mixed = _normalize_audio(mixed)
    sf.write(str(background_path), mixed.T, TARGET_SAMPLE_RATE)
    return background_path


def prepare_listening_workspace(audio_path: Path, workspace: Path) -> tuple[Path, Path, dict[str, Any]]:
    _safe_mkdir(workspace)
    workspace_audio = _copy_audio_into_workspace(audio_path, workspace)

    separation_info: dict[str, Any] = {
        "available": False,
        "strategy": "original_audio_only",
        "melody_source": "original",
        "background_audio": "",
        "stem_paths": {},
        "source_audio": str(workspace_audio),
        "reference_soundfont": _ensure_reference_soundfont(),
        "symbolic_available": False,
        "recommended_workflow": "original_audio_first",
    }

    try:
        stem_paths = _run_demucs(workspace_audio, workspace)
    except StemSeparationUnavailable as exc:
        try:
            source_midi, transcription_info = transcribe_audio_to_midi(workspace_audio, workspace)
            transcription_info["symbolic_available"] = True
        except BasicPitchUnavailable as midi_exc:
            source_midi, transcription_info = _write_empty_reference_midi(
                workspace,
                f"已保留原音频试听；旋律识别暂不可用：{midi_exc}",
            )
        separation_info["warning"] = str(exc)
        separation_info["transcription"] = transcription_info
        separation_info["symbolic_available"] = bool(transcription_info.get("symbolic_available"))
        return workspace_audio, source_midi, separation_info

    candidates: list[tuple[str, Path, Path, dict[str, Any]]] = []
    for stem_name in ("vocals", "other"):
        stem_path = stem_paths.get(stem_name)
        if stem_path is None or not stem_path.exists():
            continue
        try:
            midi_path, transcription_info = transcribe_audio_to_midi(stem_path, workspace)
        except BasicPitchUnavailable:
            continue
        transcription_info["symbolic_available"] = True
        score = _melody_focus_score(midi_path)
        if math.isfinite(score):
            info = dict(transcription_info)
            info["melody_score"] = round(score, 3)
            candidates.append((stem_name, stem_path, midi_path, info))

    if not candidates:
        try:
            source_midi, transcription_info = transcribe_audio_to_midi(workspace_audio, workspace)
            transcription_info["symbolic_available"] = True
        except BasicPitchUnavailable as midi_exc:
            source_midi, transcription_info = _write_empty_reference_midi(
                workspace,
                f"已保留原音频试听；旋律识别暂不可用：{midi_exc}",
            )
        separation_info["warning"] = "分轨完成，但没有找到足够清晰的旋律 stem，已回退到原音频转写。"
        separation_info["stem_paths"] = {name: str(path) for name, path in stem_paths.items()}
        separation_info["transcription"] = transcription_info
        separation_info["symbolic_available"] = bool(transcription_info.get("symbolic_available"))
        return workspace_audio, source_midi, separation_info

    chosen_stem, melody_audio, source_midi, transcription_info = max(candidates, key=lambda item: item[3]["melody_score"])
    background_audio = _mix_background_stems(stem_paths, chosen_stem, workspace)

    separation_info.update(
        {
            "available": True,
            "strategy": "demucs_stem_selection",
            "melody_source": chosen_stem,
            "background_audio": str(background_audio) if background_audio else "",
            "stem_paths": {name: str(path) for name, path in stem_paths.items()},
            "source_audio": str(workspace_audio),
            "melody_audio": str(melody_audio),
            "transcription": transcription_info,
            "symbolic_available": True,
        }
    )
    return workspace_audio, source_midi, separation_info


def _scale_pitch_candidates(pitch: int, root_pc: int, intervals: list[int]) -> list[int]:
    target_pcs = {(root_pc + interval) % 12 for interval in intervals}
    octave = pitch // 12
    candidates: list[int] = []
    for octave_offset in (-1, 0, 1):
        base = (octave + octave_offset) * 12
        for pc in target_pcs:
            candidate = base + pc
            if 0 <= candidate <= 127:
                candidates.append(candidate)
    return sorted(set(candidates))


def _choose_melodic_target(
    note: pretty_midi.Note,
    candidates: list[int],
    previous_pitch: int | None,
    next_pitch: int | None,
) -> int:
    if not candidates:
        return note.pitch

    best_pitch = note.pitch
    best_cost = float("inf")
    for candidate in candidates:
        shift_cost = abs(candidate - note.pitch)
        leap_cost = 0.0
        if previous_pitch is not None:
            leap_cost += max(0, abs(candidate - previous_pitch) - 7) * 0.55
            original_direction = np.sign(note.pitch - previous_pitch)
            transformed_direction = np.sign(candidate - previous_pitch)
            if original_direction and transformed_direction and original_direction != transformed_direction:
                leap_cost += 0.45
        if next_pitch is not None:
            leap_cost += max(0, abs(next_pitch - candidate) - 9) * 0.18
        register_cost = 0.22 if candidate < 45 or candidate > 92 else 0.0
        cost = shift_cost + leap_cost + register_cost
        if cost < best_cost:
            best_cost = cost
            best_pitch = candidate
    return best_pitch


def _quantize_notes(notes: list[pretty_midi.Note], step: float = 0.125) -> None:
    for note in notes:
        start = round(note.start / step) * step
        end = round(note.end / step) * step
        note.start = max(0.0, start)
        note.end = max(note.start + 0.08, end)


def _pitch_shift_to_nearest_octave(source_pc: int, target_pc: int) -> int:
    shift = target_pc - source_pc
    while shift > 6:
        shift -= 12
    while shift < -6:
        shift += 12
    return shift


def _estimate_tonic_pc(notes: list[pretty_midi.Note], fallback_tonic: str) -> int:
    if not notes:
        return TONIC_TO_PC.get(fallback_tonic, 0)
    weights = {pc: 0.0 for pc in range(12)}
    for note in notes:
        duration = max(0.08, note.end - note.start)
        weights[note.pitch % 12] += duration * (0.75 + note.velocity / 180)
    first_note_pc = min(notes, key=lambda item: item.start).pitch % 12
    last_note_pc = max(notes, key=lambda item: item.end).pitch % 12
    weights[first_note_pc] += 1.4
    weights[last_note_pc] += 1.1
    return max(weights.items(), key=lambda item: item[1])[0]


def _clamp_midi_pitch(pitch: int) -> int:
    return max(0, min(127, int(pitch)))


def _apply_mode_and_tonic(notes: list[pretty_midi.Note], tonic: str, mode: str) -> int:
    if mode == "preserve":
        return 0
    root_pc = TONIC_TO_PC[tonic]
    source_root_pc = _estimate_tonic_pc(notes, tonic)
    tonic_shift = _pitch_shift_to_nearest_octave(source_root_pc, root_pc)
    intervals = MODE_INTERVALS[mode]
    sorted_notes = sorted(notes, key=lambda item: (item.start, item.pitch))
    transformed_line: list[int] = []
    changed = 0

    for index, note in enumerate(sorted_notes):
        original_pitch = note.pitch
        shifted_pitch = _clamp_midi_pitch(note.pitch + tonic_shift)
        next_pitch = (
            _clamp_midi_pitch(sorted_notes[index + 1].pitch + tonic_shift)
            if index + 1 < len(sorted_notes)
            else None
        )
        if (shifted_pitch - root_pc) % 12 in intervals:
            transformed = shifted_pitch
        else:
            candidates = _scale_pitch_candidates(shifted_pitch, root_pc, intervals)
            transformed = _choose_melodic_target(
                pretty_midi.Note(
                    velocity=note.velocity,
                    pitch=shifted_pitch,
                    start=note.start,
                    end=note.end,
                ),
                candidates,
                transformed_line[-1] if transformed_line else None,
                next_pitch,
            )
            if abs(transformed - shifted_pitch) > 4 and max(0.08, note.end - note.start) < 0.22:
                transformed = shifted_pitch
        note.pitch = _clamp_midi_pitch(transformed)
        if note.pitch != original_pitch:
            changed += 1
        transformed_line.append(transformed)
    return changed


def _apply_tempo(midi_data: pretty_midi.PrettyMIDI, tempo_multiplier: float) -> None:
    if tempo_multiplier <= 0:
        return

    scale = 1.0 / tempo_multiplier
    for instrument in midi_data.instruments:
        for note in instrument.notes:
            note.start *= scale
            note.end *= scale


def _apply_rhythm_density(notes: list[pretty_midi.Note], rhythm_density: str, tonic: str, mode: str) -> list[pretty_midi.Note]:
    if not notes:
        return []
    if rhythm_density == "preserve":
        return [
            pretty_midi.Note(
                velocity=note.velocity,
                pitch=note.pitch,
                start=note.start,
                end=note.end,
            )
            for note in sorted(notes, key=lambda item: item.start)
        ]

    ordered_notes = sorted(notes, key=lambda item: item.start)
    transformed_notes: list[pretty_midi.Note] = []
    for index, note in enumerate(ordered_notes):
        duration = max(0.08, note.end - note.start)
        next_start = ordered_notes[index + 1].start if index + 1 < len(ordered_notes) else note.end + duration

        if rhythm_density == "dense" and duration >= 0.32:
            midpoint = note.start + duration / 2
            first = pretty_midi.Note(
                velocity=note.velocity,
                pitch=note.pitch,
                start=note.start,
                end=midpoint,
            )
            second = pretty_midi.Note(
                velocity=max(42, note.velocity - 10),
                pitch=note.pitch,
                start=midpoint,
                end=note.end,
            )
            transformed_notes.extend([first, second])
            continue

        if rhythm_density == "relaxed" and duration <= 0.18 and index % 2 == 1:
            continue

        cloned = pretty_midi.Note(
            velocity=note.velocity,
            pitch=note.pitch,
            start=note.start,
            end=note.end,
        )
        if rhythm_density == "relaxed":
            extension = max(0.08, duration * 0.35)
            cloned.end = min(cloned.end + extension, max(cloned.start + 0.08, next_start - 0.035))
        transformed_notes.append(cloned)

    _quantize_notes(transformed_notes)
    return transformed_notes


def _apply_instrument(midi_data: pretty_midi.PrettyMIDI, instrument_key: str) -> None:
    if instrument_key == "preserve":
        return
    mapping = INSTRUMENT_PROGRAMS[instrument_key]
    for instrument in midi_data.instruments:
        instrument.program = mapping["program"]
        instrument.is_drum = False
        instrument.name = mapping["midi_name"]


def _melody_instruments(midi_data: pretty_midi.PrettyMIDI) -> list[pretty_midi.Instrument]:
    instruments = [instrument for instrument in midi_data.instruments if instrument.notes and not instrument.is_drum]
    if not instruments:
        return []
    ranked = sorted(
        instruments,
        key=lambda instrument: (
            _estimate_polyphony(sorted(instrument.notes, key=lambda item: item.start)),
            -np.mean([note.pitch for note in instrument.notes]),
        ),
    )
    return [ranked[0]]


def _build_teaching_suggestion(config: TransformationConfig) -> str:
    if config.mode == "chinese_pentatonic":
        return "这版会更突出五声骨干音，适合引导学生听辨旋律线条和民族色彩。"
    if config.mode == "blues":
        return "这版会保留旋律主线，同时把蓝调音的味道拉出来，适合比较风格差异。"
    if config.rhythm_density == "dense":
        return "这版主要拉高节奏颗粒感，适合做节奏密度与旋律保持的对比。"
    if config.rhythm_density == "relaxed":
        return "这版只在节奏密度上做舒缓处理，适合对比旋律不变时节奏疏密带来的感受差异。"
    if config.instrument != "preserve":
        return "这版只切换音色，适合让学生对比同一旋律材料在不同乐器上的听觉差异。"
    if config.tempo_multiplier != 1.0:
        return "这版只调整速度，适合让学生对比同一音乐材料在快慢变化中的情绪差异。"
    return "这版默认保持其他音乐要素不动，适合做控制变量式对比聆听。"


def _collect_summary(
    midi_data: pretty_midi.PrettyMIDI,
    config: TransformationConfig,
    pipeline_info: dict[str, Any] | None = None,
    render_info: dict[str, Any] | None = None,
) -> dict[str, Any]:
    note_count = sum(len(instrument.notes) for instrument in midi_data.instruments)
    unique_pitches = sorted(
        {
            note.pitch % 12
            for instrument in midi_data.instruments
            for note in instrument.notes
        }
    )
    payload = {
        "tonic": "保持原主音" if config.mode == "preserve" else config.tonic,
        "mode": MODE_LABELS[config.mode],
        "tempo_multiplier": config.tempo_multiplier,
        "rhythm_density": _rhythm_density_label(config.rhythm_density),
        "instrument": INSTRUMENT_PROGRAMS.get(config.instrument, INSTRUMENT_PROGRAMS["preserve"])["name"],
        "note_count": note_count,
        "pitch_classes": unique_pitches,
        "teaching_suggestion": _build_teaching_suggestion(config),
    }
    if pipeline_info:
        payload["pipeline"] = pipeline_info
    if render_info:
        payload["render"] = render_info
    return payload


def transcribe_audio_to_midi(audio_path: Path, workspace: Path) -> tuple[Path, dict[str, Any]]:
    _safe_mkdir(workspace)
    ensure_ffmpeg_on_path()
    midi_path = workspace / f"transcription_{uuid4().hex[:8]}_basic_pitch.mid"

    try:
        from basic_pitch.inference import predict
    except ImportError as exc:
        raise BasicPitchUnavailable(
            "当前环境未安装 Basic Pitch，请先执行 pip install -r requirements.txt。"
        ) from exc

    try:
        model_output, midi_data, note_events = predict(str(audio_path))
        midi_data.write(str(midi_path))
        return midi_path, {
            "note_events": len(note_events),
            "model_output_keys": sorted(model_output.keys()) if isinstance(model_output, dict) else [],
            "source_audio": str(audio_path),
        }
    except Exception as exc:  # pragma: no cover
        raise BasicPitchUnavailable(f"Basic Pitch 转写失败：{exc}") from exc


def transform_midi_file(source_midi: Path, workspace: Path, config: TransformationConfig) -> tuple[Path, dict[str, Any]]:
    _safe_mkdir(workspace)
    transformed_path = workspace / f"transformed_{uuid4().hex[:8]}.mid"
    midi_data = pretty_midi.PrettyMIDI(str(source_midi))

    targets = _melody_instruments(midi_data)
    if not targets:
        fallback_program = INSTRUMENT_PROGRAMS.get(config.instrument, INSTRUMENT_PROGRAMS["piano"])["program"]
        midi_data.instruments.append(pretty_midi.Instrument(program=fallback_program))
        targets = _melody_instruments(midi_data)

    original_note_count = sum(len(instrument.notes) for instrument in midi_data.instruments)
    transformed_notes = 0
    pitch_changes = 0
    rhythm_changes = 0
    for instrument in targets:
        sorted_notes = sorted(instrument.notes, key=lambda item: (item.start, item.pitch))
        original_target_count = len(sorted_notes)
        pitch_changes += _apply_mode_and_tonic(sorted_notes, config.tonic, config.mode)
        transformed_target_notes = _apply_rhythm_density(sorted_notes, config.rhythm_density, config.tonic, config.mode)
        rhythm_changes += abs(len(transformed_target_notes) - original_target_count)
        if any(
            abs((new.end - new.start) - (old.end - old.start)) > 0.03
            for old, new in zip(sorted_notes, transformed_target_notes)
        ):
            rhythm_changes += 1
        instrument.notes = transformed_target_notes
        transformed_notes += len(instrument.notes)

    _apply_tempo(midi_data, config.tempo_multiplier)
    _apply_instrument(midi_data, config.instrument)
    midi_data.write(str(transformed_path))

    pipeline_info = {
        "original_note_count": original_note_count,
        "transformed_note_count": transformed_notes,
        "pitch_changes": pitch_changes,
        "rhythm_changes": rhythm_changes,
        "tempo_multiplier": config.tempo_multiplier,
        "instrument_changed": config.instrument != "preserve",
        "strategy": "symbolic_midi_element_transform",
    }
    return transformed_path, _collect_summary(midi_data, config, pipeline_info=pipeline_info)


def _rhythm_density_label(rhythm_density: str) -> str:
    if rhythm_density == "dense":
        return "节奏更密集"
    if rhythm_density == "relaxed":
        return "节奏更舒缓"
    return "保持原节奏"


def midi_to_note_events(midi_path: Path, max_notes: int = 220) -> dict[str, Any]:
    midi_data = pretty_midi.PrettyMIDI(str(midi_path))
    notes = []
    instrument_counts: dict[str, int] = {}

    for instrument in midi_data.instruments:
        program = int(instrument.program)
        soundfont_instrument = _program_to_soundfont_instrument(program, instrument.name)
        instrument_counts[soundfont_instrument] = instrument_counts.get(soundfont_instrument, 0) + len(instrument.notes)
        for note in instrument.notes:
            notes.append(
                {
                    "pitch": int(note.pitch),
                    "start": float(round(note.start, 4)),
                    "duration": float(round(max(0.08, note.end - note.start), 4)),
                    "velocity": int(note.velocity),
                    "program": program,
                    "instrument": soundfont_instrument,
                }
            )

    notes = sorted(notes, key=lambda item: (item["start"], item["pitch"]))[:max_notes]
    duration = max((note["start"] + note["duration"] for note in notes), default=0)
    primary_instrument = max(instrument_counts.items(), key=lambda item: item[1])[0] if instrument_counts else "acoustic_grand_piano"
    return {"notes": notes, "duration": float(round(duration, 4)), "instrument": primary_instrument}


def _program_to_soundfont_instrument(program: int, name: str = "") -> str:
    normalized_name = str(name or "").strip().lower().replace(" ", "_")
    if "koto" in normalized_name or "guzheng" in normalized_name or "zheng" in normalized_name:
        return "koto"
    if "violin" in normalized_name:
        return "violin"
    if "flute" in normalized_name:
        return "flute"
    if "xylophone" in normalized_name:
        return "xylophone"
    if program == 107:
        return "koto"
    if program == 73:
        return "flute"
    if program == 13:
        return "xylophone"
    if 40 <= program <= 48:
        return "violin"
    return "acoustic_grand_piano"


def _to_stereo(audio: np.ndarray) -> np.ndarray:
    if audio.ndim == 1:
        return np.stack([audio, audio], axis=0)
    return audio


def _match_audio_length(audio: np.ndarray, length: int) -> np.ndarray:
    if audio.shape[-1] == length:
        return audio
    if audio.shape[-1] > length:
        return audio[..., :length]
    padding = np.zeros((audio.shape[0], length - audio.shape[-1]), dtype=np.float32)
    return np.concatenate([audio, padding], axis=-1)


def _normalize_audio(audio: np.ndarray) -> np.ndarray:
    peak = float(np.max(np.abs(audio))) if audio.size else 0.0
    if peak <= 1e-6:
        return audio.astype(np.float32)
    return (audio / max(peak, 1.0) * 0.95).astype(np.float32)


def _waveform(kind: str, phase: np.ndarray) -> np.ndarray:
    if kind == "sine":
        return np.sin(phase)
    if kind == "triangle":
        return (2 / np.pi) * np.arcsin(np.sin(phase))
    if kind == "square":
        return np.sign(np.sin(phase))
    return 2 * (phase / (2 * np.pi) - np.floor(phase / (2 * np.pi) + 0.5))


def _synthesize_note(note: pretty_midi.Note, profile: dict[str, Any], sample_rate: int) -> np.ndarray:
    duration = max(0.08, note.end - note.start)
    release = profile["release"]
    total_duration = duration + release
    sample_count = max(1, int(total_duration * sample_rate))
    timeline = np.arange(sample_count, dtype=np.float32) / sample_rate
    frequency = 440.0 * (2.0 ** ((note.pitch - 69) / 12.0))
    waveform = np.zeros(sample_count, dtype=np.float32)
    for index, weight in enumerate(profile["partials"], start=1):
        phase = 2 * np.pi * frequency * index * timeline
        component_kind = profile["waveform"] if index == 1 else "sine"
        waveform += weight * _waveform(component_kind, phase)

    attack_samples = max(1, int(profile["attack"] * sample_rate))
    sustain_samples = max(1, int(duration * sample_rate))
    envelope = np.ones(sample_count, dtype=np.float32)
    envelope[:attack_samples] = np.linspace(0.0, 1.0, attack_samples, dtype=np.float32)
    decay_start = min(sample_count, sustain_samples)
    if decay_start < sample_count:
        envelope[decay_start:] = np.linspace(1.0, 0.0, sample_count - decay_start, dtype=np.float32)

    gain = max(0.06, note.velocity / 150.0)
    audio = waveform * envelope * gain * 0.3
    return np.stack([audio, audio], axis=0)


def render_midi_to_wave(
    transformed_midi: Path,
    workspace: Path,
    config: TransformationConfig,
    *,
    background_audio: Path | None = None,
    require_sampled_audio: bool = False,
) -> tuple[Path, dict[str, Any]]:
    _safe_mkdir(workspace)
    output_path = workspace / f"{transformed_midi.stem}.wav"
    midi_data = pretty_midi.PrettyMIDI(str(transformed_midi))
    profile = INSTRUMENT_PROGRAMS[config.instrument]
    notes = sorted(
        [note for instrument in midi_data.instruments for note in instrument.notes if not instrument.is_drum],
        key=lambda item: item.start,
    )
    if not notes:
        raise RenderUnavailable("MIDI 里没有可渲染的音符。")

    soundfont_info = _ensure_reference_soundfont()
    rendered = np.zeros((2, 0), dtype=np.float32)
    backend = "additive_renderer"
    if soundfont_info.get("available") and soundfont_info.get("path"):
        try:
            result = render_pretty_midi_with_sf2(
                midi_data,
                soundfont_info["path"],
                sample_rate=TARGET_SAMPLE_RATE,
            )
            rendered = result.audio
            backend = result.backend
        except SF2RenderUnavailable:
            rendered = np.zeros((2, 0), dtype=np.float32)

    if rendered.shape[-1] == 0:
        if require_sampled_audio:
            detail = soundfont_info.get("error") or soundfont_info.get("warning") or "当前服务器没有可用的 SoundFont / SF2 渲染能力。"
            raise RenderUnavailable(f"改写后音频需要真实采样音色，但本次未能取得可用采样音色。{detail}")
        tail = profile["release"] + 0.6
        total_duration = max(note.end for note in notes) + tail
        total_samples = max(1, int(total_duration * TARGET_SAMPLE_RATE))
        rendered = np.zeros((2, total_samples), dtype=np.float32)

        for note in notes:
            clip = _synthesize_note(note, profile, TARGET_SAMPLE_RATE)
            start_index = max(0, int(note.start * TARGET_SAMPLE_RATE))
            end_index = min(total_samples, start_index + clip.shape[-1])
            rendered[:, start_index:end_index] += clip[:, : end_index - start_index]

    if background_audio and background_audio.exists():
        backing, _ = librosa.load(str(background_audio), sr=TARGET_SAMPLE_RATE, mono=False)
        backing = _to_stereo(backing)
        rendered = _match_audio_length(rendered, max(rendered.shape[-1], backing.shape[-1]))
        backing = _match_audio_length(backing, rendered.shape[-1])
        rendered = backing * 0.82 + rendered * 0.9
        backend = f"stem_mix_{backend}"

    rendered = _normalize_audio(rendered)
    sf.write(str(output_path), rendered.T, TARGET_SAMPLE_RATE)
    return output_path, {
        "backend": backend,
        "sample_rate": TARGET_SAMPLE_RATE,
        "background_mix": bool(background_audio and background_audio.exists()),
        "reference_soundfont": soundfont_info,
    }


def render_original_audio_transform(
    source_audio: Path,
    workspace: Path,
    config: TransformationConfig,
) -> tuple[Path, dict[str, Any]]:
    _safe_mkdir(workspace)
    output_path = workspace / f"original_audio_tempo_{str(config.tempo_multiplier).replace('.', '_')}.wav"
    if output_path.exists():
        return output_path, {
            "backend": "librosa_original_audio",
            "sample_rate": TARGET_SAMPLE_RATE,
            "original_timbre": True,
            "tempo_multiplier": config.tempo_multiplier,
            "cache_hit": True,
        }

    audio, _ = librosa.load(str(source_audio), sr=TARGET_SAMPLE_RATE, mono=False)
    audio = _to_stereo(audio)
    tempo = max(0.5, min(float(config.tempo_multiplier), 2.0))
    if abs(tempo - 1.0) > 0.001:
        stretched_channels = [
            librosa.effects.time_stretch(channel.astype(np.float32), rate=tempo)
            for channel in audio
        ]
        target_length = max(channel.shape[-1] for channel in stretched_channels)
        audio = np.stack(
            [_match_audio_length(channel[np.newaxis, :], target_length)[0] for channel in stretched_channels],
            axis=0,
        )

    audio = _normalize_audio(audio)
    sf.write(str(output_path), audio.T, TARGET_SAMPLE_RATE)
    return output_path, {
        "backend": "librosa_original_audio",
        "sample_rate": TARGET_SAMPLE_RATE,
        "original_timbre": True,
        "tempo_multiplier": tempo,
        "strategy": "original_audio_dsp",
    }


def persist_uploaded_file(file_obj: Any, destination_dir: Path) -> Path:
    _safe_mkdir(destination_dir)
    suffix = _safe_extension(getattr(file_obj, "filename", ""), ".bin")
    stem = _ascii_slug(Path(getattr(file_obj, "filename", "")).stem, "upload")
    target_path = destination_dir / f"{stem}_{uuid4().hex[:8]}{suffix}"
    with target_path.open("wb") as buffer:
        shutil.copyfileobj(file_obj.file, buffer)
    return target_path


def write_metadata(workspace: Path, payload: dict[str, Any]) -> Path:
    metadata_path = workspace / "metadata.json"
    metadata_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return metadata_path


def build_listening_response(
    source_audio: Path,
    source_midi: Path,
    transformed_midi: Path,
    transcription_info: dict[str, Any],
    summary: dict[str, Any],
    output_mount_prefix: str = "/output",
    *,
    transformed_audio: Path | None = None,
    source_audio_public: Path | None = None,
    stem_paths: dict[str, str] | None = None,
    background_audio: Path | None = None,
    pipeline_info: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "audio_name": source_audio.name,
        "generated_midi_url": _to_output_url(source_midi, output_mount_prefix),
        "transformed_midi_url": _to_output_url(transformed_midi, output_mount_prefix),
        "transcription": transcription_info,
        "summary": summary,
    }
    public_source = source_audio_public or source_audio
    if public_source.exists() and public_source.resolve().is_relative_to(get_output_dir().resolve()):
        payload["source_audio_url"] = _to_output_url(public_source, output_mount_prefix)
    if transformed_audio and transformed_audio.exists():
        payload["transformed_audio_url"] = _to_output_url(transformed_audio, output_mount_prefix)
    if background_audio and background_audio.exists():
        payload["background_audio_url"] = _to_output_url(background_audio, output_mount_prefix)
    if stem_paths:
        payload["stem_urls"] = {
            name: _to_output_url(Path(path), output_mount_prefix)
            for name, path in stem_paths.items()
            if Path(path).exists()
        }
    if pipeline_info:
        payload["pipeline"] = pipeline_info
    return payload
