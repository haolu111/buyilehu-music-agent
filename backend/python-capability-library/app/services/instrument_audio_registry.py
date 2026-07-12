from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from app.services.instrument_timbre_catalog import EXACT_TIMBRE_DEFINITIONS, SAMPLE_LIBRARY


INSTRUMENT_AUDIO_PACK_VERSION = "instrument_audio_pack_v1"
SOUNDFONT_ASSET_URL_PREFIX = "/static/assets/midi-js-soundfonts/FluidR3_GM/"
SOUNDFONT_ASSET_ROOT = Path(__file__).resolve().parents[1] / "static" / "assets" / "midi-js-soundfonts" / "FluidR3_GM"
SOUNDFONT_SOURCE_BASE = "https://gleitz.github.io/midi-js-soundfonts/FluidR3_GM/"

REQUIRED_PACK_FIELDS = (
    "version",
    "audio_pack_id",
    "label",
    "audience",
    "sample_status",
    "allowed_activities",
    "education_alignment",
    "items",
)

REQUIRED_ITEM_FIELDS = (
    "instrument_id",
    "label",
    "audio_source_kind",
    "is_real_sample",
    "sample_fidelity",
    "playable_status",
    "playback_instrument",
    "license",
    "classroom_note",
)


def _alignment() -> dict[str, Any]:
    return {
        "primary_competency": "审美感知",
        "music_elements": ["音色", "乐器家族", "发声方式"],
        "student_practices": ["listen", "classify", "explain"],
        "grade_bands": ["middle_primary", "upper_primary"],
        "pedagogy_notes": [
            "乐器分类必须先听声音，再看真实照片验证。",
            "当前本地可发声来源是 SoundFont 或 WebAudio fallback，不能标记为真实乐器采样。",
            "补入开源真实采样后必须记录 source_url、license 和 attribution。",
        ],
    }


def _audio_item(
    instrument_id: str,
    label: str,
    *,
    kind: str,
    playback_instrument: str,
    license_name: str,
    note: str,
    sample_fidelity: str = "not_real_sample",
    playable_status: str = "pending_exact_sample",
    source_url: str = "",
    attribution: str = "",
) -> dict[str, Any]:
    return {
        "instrument_id": instrument_id,
        "label": label,
        "audio_source_kind": kind,
        "is_real_sample": kind == "open_sample",
        "exact_real_instrument_sample": sample_fidelity == "exact_open_sample",
        "sample_fidelity": sample_fidelity,
        "playable_status": playable_status,
        "playback_instrument": playback_instrument,
        "source_url": source_url,
        "license": license_name,
        "attribution": attribution,
        "classroom_note": note,
    }


FALLBACK_NOTE = "这是课堂可听 fallback，能支持先听再分，但不能标记为真实采样。"
SYNTH_NOTE = "这是 WebAudio 合成打击音，能替代课堂即时操作音，但不能标记为真实采样。"
PLAYABLE_SAMPLE_NOTE = "这是本地 SoundFont 采样音色，用于库乐队式点击演奏；如为近似音色，课堂提示不得宣称为对应实体乐器录音。"


def _playable_sample_item(
    instrument_id: str,
    label: str,
    playback_instrument: str,
    *,
    note: str = PLAYABLE_SAMPLE_NOTE,
    sample_fidelity: str = "close_soundfont_sample",
) -> dict[str, Any]:
    file_name = f"{playback_instrument}-mp3.js"
    playable_status = "ready_real_sample" if sample_fidelity == "exact_open_sample" else "ready_soundfont_proxy"
    return _audio_item(
        instrument_id,
        label,
        kind="open_sample",
        playback_instrument=playback_instrument,
        license_name="FluidR3 GM SoundFont sample",
        source_url=f"{SOUNDFONT_SOURCE_BASE}{file_name}",
        attribution="FluidR3 GM SoundFont, converted for midi-js-soundfonts by gleitz",
        note=note,
        sample_fidelity=sample_fidelity,
        playable_status=playable_status,
    )


def _common_timbre_review_item(definition: dict[str, Any]) -> dict[str, Any]:
    playback_instrument = str(definition["playbackInstrument"])
    return _audio_item(
        str(definition["id"]),
        str(definition["label"]),
        kind="open_sample",
        playback_instrument=playback_instrument,
        license_name=str(SAMPLE_LIBRARY["license"]),
        note=str(definition["classroomNote"]),
        sample_fidelity="exact_open_sample",
        playable_status="ready_real_sample",
        source_url=f"{SAMPLE_LIBRARY['sourceUrl']}{playback_instrument}-mp3.js",
        attribution=str(SAMPLE_LIBRARY["attribution"]),
    ) | {
        "license_url": str(SAMPLE_LIBRARY["licenseUrl"]),
        "family_id": str(definition["familyId"]),
        "family_label": str(definition["familyLabel"]),
        "classroom_family": str(definition["classroomFamily"]),
        "evidence_terms": deepcopy(definition["evidenceTerms"]),
        "preview": deepcopy(definition["preview"]),
    }

INSTRUMENT_AUDIO_PACKS: dict[str, dict[str, Any]] = {
    "common_instrument_timbre_review_pack": {
        "version": INSTRUMENT_AUDIO_PACK_VERSION,
        "audio_pack_id": "common_instrument_timbre_review_pack",
        "label": "基础音乐教育常见乐器真实音色审核包",
        "audience": "primary_school",
        "sample_status": "exact_open_samples_ready",
        "allowed_activities": ["instrument_timbre_review", "instrument_family_sorting", "instrument_timbre_match"],
        "education_alignment": {
            "primary_competency": "审美感知",
            "music_elements": ["音色", "乐器家族", "发声方式"],
            "student_practices": ["listen", "compare", "classify", "explain"],
            "grade_bands": ["lower_primary", "middle_primary", "upper_primary"],
            "pedagogy_notes": [
                "十二件乐器均使用与乐器名称一致的 FluidR3 GM SoundFont 采样预设。",
                "试听短句按乐器代表音域配置，用于专业审核和课堂听辨，不回退到振荡器。",
                "商业分发时必须保留 FluidR3 GM 与 midi-js-soundfonts 的 CC BY 3.0 署名。",
            ],
        },
        "sample_library": deepcopy(SAMPLE_LIBRARY),
        "items": [_common_timbre_review_item(definition) for definition in EXACT_TIMBRE_DEFINITIONS],
    },
    "primary_instrument_audio_pack": {
        "version": INSTRUMENT_AUDIO_PACK_VERSION,
        "audio_pack_id": "primary_instrument_audio_pack",
        "label": "小学乐器听辨音频包",
        "audience": "primary_school",
        "sample_status": "fallback_ready_needs_open_samples",
        "allowed_activities": ["instrument_family_sorting", "instrument_timbre_match", "orff_percussion_ensemble"],
        "education_alignment": _alignment(),
        "items": [
            _audio_item("dizi", "笛子", kind="soundfont_fallback", playback_instrument="flute", license_name="FluidR3 GM SoundFont", note=FALLBACK_NOTE),
            _audio_item("erhu", "二胡", kind="soundfont_fallback", playback_instrument="violin", license_name="FluidR3 GM SoundFont", note=FALLBACK_NOTE),
            _audio_item("pipa", "琵琶", kind="soundfont_fallback", playback_instrument="koto", license_name="FluidR3 GM SoundFont", note=FALLBACK_NOTE),
            _audio_item("hand_drum", "小鼓", kind="webaudio_synthesis", playback_instrument="standard_drum_kit", license_name="project_generated_synthesis", note=SYNTH_NOTE),
            _audio_item("woodblock", "木鱼", kind="webaudio_synthesis", playback_instrument="woodblock", license_name="project_generated_synthesis", note=SYNTH_NOTE),
            _audio_item("shaker", "沙锤", kind="webaudio_synthesis", playback_instrument="shaker", license_name="project_generated_synthesis", note=SYNTH_NOTE),
            _audio_item("triangle", "三角铁", kind="webaudio_synthesis", playback_instrument="triangle_bell", license_name="project_generated_synthesis", note=SYNTH_NOTE),
            _audio_item("tambourine", "铃鼓", kind="webaudio_synthesis", playback_instrument="tambourine", license_name="project_generated_synthesis", note=SYNTH_NOTE),
            _audio_item("xylophone", "音条琴", kind="soundfont_fallback", playback_instrument="xylophone", license_name="FluidR3 GM SoundFont", note=FALLBACK_NOTE),
            _audio_item("recorder", "竖笛", kind="soundfont_fallback", playback_instrument="flute", license_name="FluidR3 GM SoundFont", note=FALLBACK_NOTE),
            _audio_item("melodica", "口风琴", kind="soundfont_fallback", playback_instrument="acoustic_grand_piano", license_name="FluidR3 GM SoundFont", note=FALLBACK_NOTE),
        ],
    },
    "primary_playable_instrument_sample_pack": {
        "version": INSTRUMENT_AUDIO_PACK_VERSION,
        "audio_pack_id": "primary_playable_instrument_sample_pack",
        "label": "小学可演奏乐器采样演奏包",
        "audience": "primary_school",
        "sample_status": "sampled_playback_ready_needs_exact_samples",
        "allowed_activities": [
            "rhythm_warmup",
            "meter_body_movement",
            "steady_beat_walk",
            "strong_weak_beat_circle",
            "rhythm_question_answer",
            "xylophone_creation",
            "solfege_echo_singing",
            "orff_percussion_ensemble",
            "classroom_band_roles",
            "body_percussion_builder",
        ],
        "education_alignment": {
            "primary_competency": "艺术表现",
            "music_elements": ["音色", "节奏", "音高", "合奏"],
            "student_practices": ["listen", "play", "create", "perform"],
            "grade_bands": ["lower_primary", "middle_primary", "upper_primary"],
            "pedagogy_notes": [
                "采样包服务库乐队式可演奏乐器，学生必须先听见音色再演奏或创编。",
                "运行时必须优先播放本地采样文件，不能把 oscillator 或 WebAudio 合成音标记为真实采样。",
                "近似音色必须在课堂提示中说明，不得冒充某个实体乐器的精确录音。",
            ],
        },
        "items": [
            _playable_sample_item("rhythm_pad", "节奏垫", "taiko_drum", note="这是本地 SoundFont 采样音色，可用于节奏垫演奏；不声明为某个实体节奏垫的精确录音。"),
            _playable_sample_item("virtual_hand_drum", "虚拟小鼓", "taiko_drum", note="这是本地 SoundFont 鼓类采样，可用于课堂小鼓替代演奏；补入小鼓实录前标为近似采样。"),
            _playable_sample_item("woodblock_claves", "木鱼响板", "woodblock"),
            _playable_sample_item("shaker", "虚拟沙锤", "agogo", note="这是本地 SoundFont 采样近似音色，用于沙锤节奏纹理占位；补入精确沙锤 one-shot 前不得宣称为沙锤实录。", sample_fidelity="approximate_soundfont_sample"),
            _playable_sample_item("triangle_bell", "三角铁/碰铃", "glockenspiel"),
            _playable_sample_item("tambourine", "虚拟铃鼓", "reverse_cymbal", note="这是本地 SoundFont 金属打击采样近似音色，用于铃鼓滚奏占位；补入精确铃鼓 one-shot 前不得宣称为铃鼓实录。", sample_fidelity="approximate_soundfont_sample"),
            _playable_sample_item("virtual_xylophone", "虚拟音条琴", "xylophone", sample_fidelity="exact_open_sample"),
            _playable_sample_item("simple_keyboard", "简版键盘", "acoustic_grand_piano", sample_fidelity="exact_open_sample"),
            _playable_sample_item("pentatonic_grid", "五声宫格乐器", "xylophone", note="这是本地 SoundFont 音条琴采样，用于五声音阶宫格演奏；五声限制由运行时控制。", sample_fidelity="exact_open_sample"),
            _playable_sample_item("recorder_fingering_board", "竖笛指法板", "flute", note="这是本地 SoundFont 长笛采样近似音色，用于竖笛指法板参考音；补入竖笛实录前不得宣称为竖笛实录。", sample_fidelity="approximate_soundfont_sample"),
            _playable_sample_item("melodica_keyboard_board", "口风琴键盘板", "acoustic_grand_piano", note="这是本地 SoundFont 钢琴采样近似音色，用于口风琴键位演奏占位；补入口风琴实录前不得宣称为口风琴实录。", sample_fidelity="approximate_soundfont_sample"),
            _playable_sample_item("dizi_playable_board", "笛子演奏板", "flute", note="这是本地 SoundFont 长笛采样近似音色，用于笛子演奏板先行可奏；补入笛子实录前不得宣称为笛子实录。", sample_fidelity="approximate_soundfont_sample"),
            _playable_sample_item("flute_playable_board", "长笛演奏板", "flute", sample_fidelity="exact_open_sample"),
        ],
    }
}


def list_instrument_audio_packs() -> list[dict[str, Any]]:
    return [validate_instrument_audio_pack(pack) for pack in INSTRUMENT_AUDIO_PACKS.values()]


def get_instrument_audio_pack(audio_pack_id: str) -> dict[str, Any]:
    pack = INSTRUMENT_AUDIO_PACKS.get(str(audio_pack_id or ""))
    if not pack:
        raise ValueError(f"unknown instrument audio pack: {audio_pack_id}")
    return validate_instrument_audio_pack(pack)


def validate_instrument_audio_pack(pack: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(pack, dict):
        raise ValueError("instrument audio pack must be a dict")
    missing = [field for field in REQUIRED_PACK_FIELDS if not pack.get(field)]
    if missing:
        raise ValueError(f"instrument audio pack missing fields: {', '.join(missing)}")
    if pack.get("version") != INSTRUMENT_AUDIO_PACK_VERSION:
        raise ValueError("instrument audio pack version must be instrument_audio_pack_v1")
    if pack.get("audience") != "primary_school":
        raise ValueError("instrument audio pack audience must be primary_school")
    items = pack.get("items")
    if not isinstance(items, list) or not items:
        raise ValueError("instrument audio pack items must be a non-empty list")
    for item in items:
        _validate_item(item)
    validated = deepcopy(pack)
    _attach_local_file_report(validated)
    return validated


def _validate_item(item: dict[str, Any]) -> None:
    if not isinstance(item, dict):
        raise ValueError("instrument audio item must be a dict")
    missing = [field for field in REQUIRED_ITEM_FIELDS if item.get(field) in (None, "")]
    if missing:
        raise ValueError(f"instrument audio item missing fields: {', '.join(missing)}")
    kind = item.get("audio_source_kind")
    if kind not in {"open_sample", "soundfont_fallback", "webaudio_synthesis"}:
        raise ValueError("instrument audio source kind is not supported")
    if item.get("sample_fidelity") not in {
        "exact_open_sample",
        "close_soundfont_sample",
        "approximate_soundfont_sample",
        "not_real_sample",
    }:
        raise ValueError("instrument audio sample_fidelity is not supported")
    if item.get("playable_status") not in {"ready_real_sample", "ready_soundfont_proxy", "pending_exact_sample"}:
        raise ValueError("instrument audio playable_status is not supported")
    if kind == "open_sample":
        missing = [field for field in ("source_url", "attribution") if not item.get(field)]
        if missing:
            raise ValueError(f"open sample audio item missing fields: {', '.join(missing)}")
        if item.get("is_real_sample") is not True:
            raise ValueError("open sample audio item must set is_real_sample=true")
        if item.get("sample_fidelity") == "not_real_sample":
            raise ValueError("open sample audio item must declare sample_fidelity")
    elif item.get("is_real_sample"):
        raise ValueError("fallback audio item cannot be marked as a real sample")
    if item.get("exact_real_instrument_sample") and item.get("sample_fidelity") != "exact_open_sample":
        raise ValueError("exact_real_instrument_sample requires exact_open_sample fidelity")


def _attach_local_file_report(pack: dict[str, Any]) -> None:
    missing_files: list[dict[str, str]] = []
    ready_files: list[dict[str, str]] = []
    for item in pack.get("items", []):
        if item.get("audio_source_kind") not in {"soundfont_fallback", "open_sample"}:
            item["local_asset_status"] = "not_required"
            item["local_asset_url"] = ""
            continue
        file_name = f"{item.get('playback_instrument')}-mp3.js"
        local_path = SOUNDFONT_ASSET_ROOT / file_name
        local_url = f"{SOUNDFONT_ASSET_URL_PREFIX}{file_name}"
        item["local_asset_url"] = local_url
        if local_path.exists():
            item["local_asset_status"] = "ready"
            ready_files.append({"instrument_id": str(item.get("instrument_id") or ""), "file": str(local_path)})
        else:
            item["local_asset_status"] = "missing"
            missing_files.append({"instrument_id": str(item.get("instrument_id") or ""), "file": str(local_path)})
    pack["local_file_report"] = {
        "status": "ready" if not missing_files else "missing_files",
        "ready_count": len(ready_files),
        "missing_count": len(missing_files),
        "ready_files": ready_files,
        "missing_files": missing_files,
    }
