from __future__ import annotations

import importlib.util
import sys
import types
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pretty_midi


class SF2RenderUnavailable(RuntimeError):
    pass


@dataclass
class RenderResult:
    audio: np.ndarray
    sample_rate: int
    backend: str


def _load_tinysoundfont_extension() -> Any:
    try:
        import tinysoundfont._tinysoundfont as extension  # type: ignore[attr-defined]

        return extension
    except Exception:
        pass

    site_packages = Path(sys.prefix) / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
    extension_path = site_packages / "tinysoundfont" / f"_tinysoundfont.cpython-{sys.version_info.major}{sys.version_info.minor}-darwin.so"
    if not extension_path.exists():
        raise SF2RenderUnavailable("找不到 tinysoundfont 的二进制扩展，请先执行 .venv/bin/python -m pip install tinysoundfont --no-deps。")

    package = types.ModuleType("tinysoundfont")
    package.__path__ = [str(extension_path.parent)]
    sys.modules.setdefault("tinysoundfont", package)

    module_name = "tinysoundfont._tinysoundfont"
    spec = importlib.util.spec_from_file_location(module_name, extension_path)
    if spec is None or spec.loader is None:
        raise SF2RenderUnavailable("无法装载 tinysoundfont 扩展。")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class TinySoundFontSynth:
    def __init__(self, sample_rate: int = 44100, gain: float = -2.0):
        self.sample_rate = sample_rate
        self.gain = gain
        self.extension = _load_tinysoundfont_extension()
        self.soundfonts: dict[int, Any] = {}
        self.channel_soundfont: dict[int, int] = {}
        self.next_sfid = 0

    def sfload(self, filename: str, gain: float = 0.0, max_voices: int = 256) -> int:
        soundfont = self.extension.SoundFont(filename)
        soundfont.set_output(
            self.extension.OutputMode.StereoInterleaved,
            self.sample_rate,
            self.gain + gain,
        )
        soundfont.set_max_voices(max_voices)
        sfid = self.next_sfid
        self.next_sfid += 1
        self.soundfonts[sfid] = soundfont
        return sfid

    def resolve_preset(self, sfid: int, bank: int, preset: int) -> tuple[int, int]:
        soundfont = self.soundfonts[sfid]
        fallback_presets = {
            40: 20,
            73: 29,
            107: 35,
        }
        candidates = [preset]
        if preset in fallback_presets:
            candidates.append(fallback_presets[preset])
        available = [index for index in range(128) if soundfont.get_preset_index(bank, index) >= 0]
        candidates.extend(available)

        for candidate in candidates:
            index = soundfont.get_preset_index(bank, candidate)
            if index >= 0:
                return bank, candidate
        raise SF2RenderUnavailable("当前 SF2 里找不到可用的预设。")

    def program_select(self, channel: int, sfid: int, bank: int, preset: int, is_drums: bool = False) -> None:
        if sfid not in self.soundfonts:
            raise SF2RenderUnavailable("无效的 SoundFont ID。")
        soundfont = self.soundfonts[sfid]
        self.channel_soundfont[channel] = sfid
        resolved_bank, resolved_preset = self.resolve_preset(sfid, bank, preset)
        soundfont.channel_set_bank(channel, resolved_bank)
        soundfont.channel_set_preset_number(channel, resolved_preset, is_drums)

    def note_on(self, channel: int, pitch: int, velocity: int) -> None:
        sfid = self.channel_soundfont[channel]
        self.soundfonts[sfid].channel_note_on(channel, int(pitch), max(0.0, min(1.0, velocity / 127.0)))

    def note_off(self, channel: int, pitch: int) -> None:
        sfid = self.channel_soundfont[channel]
        self.soundfonts[sfid].channel_note_off(channel, int(pitch))

    def pitch_bend(self, channel: int, value: int) -> None:
        sfid = self.channel_soundfont[channel]
        self.soundfonts[sfid].channel_set_pitch_wheel(channel, int(value))

    def sounds_off(self) -> None:
        for soundfont in self.soundfonts.values():
            soundfont.reset()

    def generate(self, frame_count: int) -> np.ndarray:
        if frame_count <= 0:
            return np.zeros((2, 0), dtype=np.float32)
        buffer = memoryview(bytearray(frame_count * 2 * 4))
        mix = False
        for soundfont in self.soundfonts.values():
            soundfont.render(buffer, mix)
            mix = True
        interleaved = np.frombuffer(buffer, dtype=np.float32)
        if interleaved.size != frame_count * 2:
            raise SF2RenderUnavailable("SF2 渲染返回了异常长度的音频缓冲。")
        return interleaved.reshape(frame_count, 2).T.copy()


def render_pretty_midi_with_sf2(
    midi_data: pretty_midi.PrettyMIDI,
    soundfont_path: str | Path,
    sample_rate: int = 44100,
) -> RenderResult:
    synth = TinySoundFontSynth(sample_rate=sample_rate)
    sfid = synth.sfload(str(soundfont_path))

    active_instruments = [instrument for instrument in midi_data.instruments if instrument.notes]
    if not active_instruments:
        raise SF2RenderUnavailable("MIDI 里没有可渲染的轨道。")

    for index, instrument in enumerate(active_instruments[:15]):
        channel = 9 if instrument.is_drum else index if index < 9 else index + 1
        program = 0 if instrument.is_drum else int(max(0, min(127, instrument.program)))
        synth.program_select(channel, sfid, 128 if instrument.is_drum else 0, program, instrument.is_drum)
        instrument._sf2_channel = channel  # type: ignore[attr-defined]

    events: list[tuple[float, int, int, int, int]] = []
    for instrument in active_instruments[:15]:
        channel = getattr(instrument, "_sf2_channel")
        for note in instrument.notes:
            events.append((float(note.start), 1, channel, int(note.pitch), int(note.velocity)))
            events.append((float(note.end), 0, channel, int(note.pitch), 0))
        for bend in instrument.pitch_bends:
            events.append((float(bend.time), 2, channel, int(bend.pitch), 0))

    if not events:
        raise SF2RenderUnavailable("MIDI 里没有可渲染的事件。")

    events.sort(key=lambda item: (item[0], item[1]))
    rendered_segments: list[np.ndarray] = []
    current_time = 0.0
    for event_time, event_type, channel, value, velocity in events:
        if event_time > current_time:
            frame_count = int(round((event_time - current_time) * sample_rate))
            rendered_segments.append(synth.generate(frame_count))
            current_time = event_time

        if event_type == 0:
            synth.note_off(channel, value)
        elif event_type == 1:
            synth.note_on(channel, value, velocity)
        else:
            synth.pitch_bend(channel, int(max(0, min(16383, value + 8192))))

    rendered_segments.append(synth.generate(int(sample_rate * 1.2)))
    synth.sounds_off()

    audio = np.concatenate(rendered_segments, axis=1) if rendered_segments else np.zeros((2, 0), dtype=np.float32)
    return RenderResult(audio=audio, sample_rate=sample_rate, backend="tinysoundfont_sf2")
