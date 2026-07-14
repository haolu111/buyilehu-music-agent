from __future__ import annotations

from typing import Any

from app.services.instrument_audio_registry import get_instrument_audio_pack
from app.services.virtual_instrument_spec import validate_virtual_instrument_spec


_COMMON_INPUTS = ["touch", "mouse", "keyboard"]
_COMMON_GATES = ["sound_plays", "latency_ok", "events_recorded", "teacher_controls_apply"]


def _runtime_contract(
    components: list[str],
    supported_activity_ids: list[str],
    classroom_evidence: list[str],
    *,
    event_schema: list[str] | None = None,
    extra_quality_gates: list[str] | None = None,
    audio_unlock_required: bool = True,
) -> dict[str, Any]:
    schema = ["instrument_id", "timestamp_ms", *(event_schema or ["action", "value"])]
    quality_gates = ["sound_plays", "events_recorded", "reset_clears_events"]
    for gate in extra_quality_gates or []:
        if gate not in quality_gates:
            quality_gates.append(gate)
    return {
        "version": "virtual_instrument_runtime_contract_v1",
        "runtime_components": components,
        "supported_activity_ids": supported_activity_ids,
        "student_event_schema": schema,
        "audio_unlock_required": audio_unlock_required,
        "quality_gates": quality_gates,
        "classroom_evidence": classroom_evidence,
    }


def _with_playable_asset_requirements(spec: dict[str, Any]) -> dict[str, Any]:
    enriched = dict(spec)
    sample_item = _sample_item_for(str(enriched.get("instrument_id") or ""))
    gates = list(enriched.get("quality_gates") or [])
    for gate in ("sampled_playback", "generated_instrument_skin_visible"):
        if gate not in gates:
            gates.append(gate)
    if sample_item.get("playable_status") == "ready_real_sample" and "real_sample_playback" not in gates:
        gates.append("real_sample_playback")
    if sample_item.get("playable_status") == "ready_soundfont_proxy" and "exact_sample_needed" not in gates:
        gates.append("exact_sample_needed")
    enriched["quality_gates"] = gates
    enriched["real_sample_required"] = sample_item.get("playable_status") == "ready_real_sample"
    enriched["sampled_playback_required"] = True
    enriched["sample_pack_required"] = "primary_playable_instrument_sample_pack"
    enriched["sample_status"] = sample_item.get("playable_status", "pending_exact_sample")
    enriched["sample_fidelity"] = sample_item.get("sample_fidelity", "not_real_sample")
    enriched["exact_real_instrument_sample"] = bool(sample_item.get("exact_real_instrument_sample"))
    enriched["playback_instrument"] = sample_item.get("playback_instrument", "")
    enriched["audio_classroom_note"] = sample_item.get("classroom_note", "")
    enriched["local_asset_status"] = sample_item.get("local_asset_status", "")
    enriched["local_asset_url"] = sample_item.get("local_asset_url", "")
    enriched["visual_asset_pack_required"] = "generated_playable_instrument_pack"
    runtime = dict(enriched.get("runtime_contract") or {})
    runtime_gates = list(runtime.get("quality_gates") or [])
    for gate in ("sampled_playback", "generated_instrument_skin_visible"):
        if gate not in runtime_gates:
            runtime_gates.append(gate)
    if sample_item.get("playable_status") == "ready_real_sample" and "real_sample_playback" not in runtime_gates:
        runtime_gates.append("real_sample_playback")
    if sample_item.get("playable_status") == "ready_soundfont_proxy" and "exact_sample_needed" not in runtime_gates:
        runtime_gates.append("exact_sample_needed")
    runtime["quality_gates"] = runtime_gates
    enriched["runtime_contract"] = runtime
    return enriched


def _sample_item_for(instrument_id: str) -> dict[str, Any]:
    pack = get_instrument_audio_pack("primary_playable_instrument_sample_pack")
    for item in pack.get("items", []):
        if item.get("instrument_id") == instrument_id:
            return item
    return {
        "playable_status": "pending_exact_sample",
        "sample_fidelity": "not_real_sample",
        "exact_real_instrument_sample": False,
    }


VIRTUAL_INSTRUMENT_REGISTRY: dict[str, dict[str, Any]] = {
    "rhythm_pad": {
        "version": "virtual_instrument_spec_v1",
        "instrument_id": "rhythm_pad",
        "name": "节奏垫",
        "audience": "primary_school",
        "replace_physical_instrument": "节奏垫",
        "grade_bands": ["lower_primary", "middle_primary", "upper_primary"],
        "runtime": "react_webaudio",
        "input_modes": _COMMON_INPUTS,
        "sound_source": "webaudio_synthetic_drum",
        "pitch_set": [],
        "constraints": {"record_events": True, "challenge_only_records": True},
        "teacher_controls": ["change_tempo", "show_beat", "reset"],
        "quality_gates": _COMMON_GATES,
        "open_source_dependencies": ["react", "webaudio"],
        "image2_required": False,
        "runtime_contract": _runtime_contract(
            ["RhythmPad", "RhythmWarmupActivity"],
            ["rhythm_warmup"],
            ["学生能点击或触摸节奏垫，系统记录拍点事件。"],
            event_schema=["tap_index", "timing_status"],
            extra_quality_gates=["timing_feedback_ready"],
        ),
    },
    "virtual_hand_drum": {
        "version": "virtual_instrument_spec_v1",
        "instrument_id": "virtual_hand_drum",
        "name": "虚拟小鼓",
        "audience": "primary_school",
        "replace_physical_instrument": "小鼓",
        "grade_bands": ["lower_primary", "middle_primary"],
        "runtime": "react_webaudio",
        "input_modes": _COMMON_INPUTS,
        "sound_source": "sample_or_webaudio_drum",
        "pitch_set": [],
        "constraints": {"record_events": True, "supports_accent": True, "supports_rim_hit": True},
        "teacher_controls": ["change_tempo", "enable_rim_hit", "reset"],
        "quality_gates": _COMMON_GATES,
        "open_source_dependencies": ["react", "webaudio"],
        "image2_required": False,
        "runtime_contract": _runtime_contract(
            ["OrffEnsembleActivity"],
            ["meter_body_movement", "orff_percussion_ensemble", "classroom_band_roles"],
            ["学生能用虚拟小鼓表现强拍或固定声部。"],
            event_schema=["hit_type", "beat_index"],
            extra_quality_gates=["accent_controls_apply"],
        ),
    },
    "woodblock_claves": {
        "version": "virtual_instrument_spec_v1",
        "instrument_id": "woodblock_claves",
        "name": "木鱼响板",
        "audience": "primary_school",
        "replace_physical_instrument": "木鱼/响板",
        "grade_bands": ["lower_primary", "middle_primary", "upper_primary"],
        "runtime": "react_webaudio",
        "input_modes": _COMMON_INPUTS,
        "sound_source": "sample_or_webaudio_click",
        "pitch_set": [],
        "constraints": {"record_events": True, "instrument_choices": ["woodblock", "claves"]},
        "teacher_controls": ["choose_sound", "change_tempo", "reset"],
        "quality_gates": _COMMON_GATES,
        "open_source_dependencies": ["react", "webaudio"],
        "image2_required": False,
        "runtime_contract": _runtime_contract(
            ["OrffEnsembleActivity"],
            ["orff_percussion_ensemble", "classroom_band_roles"],
            ["学生能用木鱼/响板保持稳定拍或回应节奏。"],
            event_schema=["sound_variant", "beat_index"],
            extra_quality_gates=["sound_choice_applies"],
        ),
    },
    "shaker": {
        "version": "virtual_instrument_spec_v1",
        "instrument_id": "shaker",
        "name": "虚拟沙锤",
        "audience": "primary_school",
        "replace_physical_instrument": "沙锤",
        "grade_bands": ["lower_primary", "middle_primary"],
        "runtime": "react_webaudio",
        "input_modes": _COMMON_INPUTS,
        "sound_source": "noise_synth_or_sample",
        "pitch_set": [],
        "constraints": {"record_events": True, "supports_sustain": True},
        "teacher_controls": ["change_tempo", "toggle_sustain", "reset"],
        "quality_gates": _COMMON_GATES,
        "open_source_dependencies": ["react", "webaudio"],
        "image2_required": False,
        "runtime_contract": _runtime_contract(
            ["OrffEnsembleActivity"],
            ["orff_percussion_ensemble", "classroom_band_roles"],
            ["学生能用沙锤表现弱拍、持续音或节奏纹理。"],
            event_schema=["shake_mode", "beat_index"],
            extra_quality_gates=["sustain_toggle_applies"],
        ),
    },
    "triangle_bell": {
        "version": "virtual_instrument_spec_v1",
        "instrument_id": "triangle_bell",
        "name": "虚拟三角铁/碰铃",
        "audience": "primary_school",
        "replace_physical_instrument": "三角铁/碰铃",
        "grade_bands": ["middle_primary", "upper_primary"],
        "runtime": "react_webaudio",
        "input_modes": _COMMON_INPUTS,
        "sound_source": "sample_or_webaudio_metal_bell",
        "pitch_set": [],
        "constraints": {"record_events": True, "supports_sustain": True, "supports_dampen": True},
        "teacher_controls": ["change_tempo", "dampen", "reset"],
        "quality_gates": _COMMON_GATES + ["sustain_release_applies"],
        "open_source_dependencies": ["react", "webaudio"],
        "image2_required": False,
        "runtime_contract": _runtime_contract(
            ["OrffEnsembleActivity"],
            ["orff_percussion_ensemble", "classroom_band_roles"],
            ["学生能用三角铁/碰铃在长音点缀处按时进入，并听见延音与止音。"],
            event_schema=["hit_type", "beat_index", "sustain_ms"],
            extra_quality_gates=["sustain_release_applies", "entry_timing_visible"],
        ),
    },
    "tambourine": {
        "version": "virtual_instrument_spec_v1",
        "instrument_id": "tambourine",
        "name": "虚拟铃鼓",
        "audience": "primary_school",
        "replace_physical_instrument": "铃鼓",
        "grade_bands": ["lower_primary", "middle_primary", "upper_primary"],
        "runtime": "react_webaudio",
        "input_modes": _COMMON_INPUTS,
        "sound_source": "sample_or_webaudio_tambourine",
        "pitch_set": [],
        "constraints": {"record_events": True, "supports_accent": True, "supports_roll": True},
        "teacher_controls": ["change_tempo", "toggle_roll", "reset"],
        "quality_gates": _COMMON_GATES + ["roll_mode_applies"],
        "open_source_dependencies": ["react", "webaudio"],
        "image2_required": False,
        "runtime_contract": _runtime_contract(
            ["OrffEnsembleActivity"],
            ["orff_percussion_ensemble", "classroom_band_roles", "body_percussion_builder"],
            ["学生能用铃鼓表现强拍、弱拍或滚奏纹理，并在合奏中按时进入。"],
            event_schema=["hit_type", "roll_mode", "beat_index"],
            extra_quality_gates=["roll_mode_applies", "entry_timing_visible"],
        ),
    },
    "virtual_xylophone": {
        "version": "virtual_instrument_spec_v1",
        "instrument_id": "virtual_xylophone",
        "name": "虚拟音条琴",
        "audience": "primary_school",
        "replace_physical_instrument": "音条琴",
        "grade_bands": ["middle_primary", "upper_primary"],
        "runtime": "react_webaudio",
        "input_modes": _COMMON_INPUTS,
        "sound_source": "webaudio_or_soundfont",
        "pitch_set": ["do", "re", "mi", "sol", "la"],
        "constraints": {
            "only_allow_target_pitches": True,
            "show_solfege": True,
            "record_events": True,
        },
        "teacher_controls": ["change_tempo", "hide_labels", "limit_pitch_count", "reset"],
        "quality_gates": _COMMON_GATES + ["material_bound"],
        "open_source_dependencies": ["react", "tonejs_or_webaudio"],
        "image2_required": True,
        "runtime_contract": _runtime_contract(
            ["CompositionPuzzleScene", "StudentGameApp"],
            ["xylophone_creation", "solfege_sorting", "solfege_echo_singing"],
            ["学生能在限定 do/re/mi/sol/la 内试听、创编、回放短句或获得唱名回声参照。"],
            event_schema=["pitch", "solfege", "slot_index"],
            extra_quality_gates=["pitch_limited_to_material", "playback_ready"],
        ),
    },
    "simple_keyboard": {
        "version": "virtual_instrument_spec_v1",
        "instrument_id": "simple_keyboard",
        "name": "简版键盘",
        "audience": "primary_school",
        "replace_physical_instrument": "键盘/口风琴键盘提示",
        "grade_bands": ["upper_primary"],
        "runtime": "react_webaudio",
        "input_modes": _COMMON_INPUTS,
        "sound_source": "webaudio_or_soundfont",
        "pitch_set": ["do", "re", "mi", "fa", "sol", "la", "ti"],
        "constraints": {"only_allow_target_pitches": True, "show_solfege": True, "record_events": True},
        "teacher_controls": ["transpose", "hide_labels", "limit_pitch_count", "reset"],
        "quality_gates": _COMMON_GATES + ["material_bound"],
        "open_source_dependencies": ["react", "tonejs_or_webaudio"],
        "image2_required": False,
        "runtime_contract": _runtime_contract(
            ["SimpleKeyboardBoard"],
            ["solfege_sorting", "xylophone_creation"],
            ["学生能用简版键盘听辨或演奏目标音级。"],
            event_schema=["pitch", "key_index"],
            extra_quality_gates=["pitch_limited_to_material"],
        ),
    },
    "pentatonic_grid": {
        "version": "virtual_instrument_spec_v1",
        "instrument_id": "pentatonic_grid",
        "name": "五声宫格乐器",
        "audience": "primary_school",
        "replace_physical_instrument": "五声音阶创编板",
        "grade_bands": ["upper_primary"],
        "runtime": "react_webaudio",
        "input_modes": _COMMON_INPUTS,
        "sound_source": "webaudio_or_soundfont",
        "pitch_set": ["宫", "商", "角", "徵", "羽"],
        "constraints": {"only_allow_target_pitches": True, "show_solfege": True, "record_events": True},
        "teacher_controls": ["choose_tonic", "limit_pitch_count", "reset"],
        "quality_gates": _COMMON_GATES + ["material_bound"],
        "open_source_dependencies": ["react", "tonejs_or_webaudio"],
        "image2_required": False,
        "runtime_contract": _runtime_contract(
            ["CompositionPuzzleScene", "PentatonicGrid"],
            ["xylophone_creation"],
            ["学生能在五声音阶限制内创编、试听和修改短句。"],
            event_schema=["degree", "slot_index"],
            extra_quality_gates=["pitch_limited_to_material", "playback_ready"],
        ),
    },
    "recorder_fingering_board": {
        "version": "virtual_instrument_spec_v1",
        "instrument_id": "recorder_fingering_board",
        "name": "竖笛指法板",
        "audience": "primary_school",
        "replace_physical_instrument": "竖笛指法图",
        "grade_bands": ["upper_primary"],
        "runtime": "react_svg",
        "input_modes": _COMMON_INPUTS,
        "sound_source": "webaudio_reference_tone",
        "pitch_set": ["do", "re", "mi", "fa", "sol"],
        "constraints": {"record_events": True, "fingering_hint_only": True},
        "teacher_controls": ["choose_pitch", "hide_labels", "reset"],
        "quality_gates": _COMMON_GATES,
        "open_source_dependencies": ["react", "svg"],
        "image2_required": False,
        "runtime_contract": _runtime_contract(
            ["RecorderFingeringBoard"],
            ["solfege_sorting"],
            ["学生能查看竖笛指法提示并听参考音，不做真实吹奏评分。"],
            event_schema=["pitch", "fingering_id"],
            extra_quality_gates=["hint_only_no_auto_singing_score"],
        ),
    },
    "melodica_keyboard_board": {
        "version": "virtual_instrument_spec_v1",
        "instrument_id": "melodica_keyboard_board",
        "name": "口风琴键盘板",
        "audience": "primary_school",
        "replace_physical_instrument": "口风琴键盘提示板",
        "grade_bands": ["upper_primary"],
        "runtime": "react_webaudio",
        "input_modes": _COMMON_INPUTS,
        "sound_source": "webaudio_or_soundfont",
        "pitch_set": ["do", "re", "mi", "fa", "sol", "la", "ti"],
        "constraints": {"only_allow_target_pitches": True, "show_solfege": True, "record_events": True},
        "teacher_controls": ["transpose", "hide_labels", "reset"],
        "quality_gates": _COMMON_GATES + ["material_bound"],
        "open_source_dependencies": ["react", "tonejs_or_webaudio"],
        "image2_required": False,
        "runtime_contract": _runtime_contract(
            ["MelodicaKeyboardBoard", "SimpleKeyboardBoard"],
            ["solfege_sorting", "xylophone_creation"],
            ["学生能用口风琴键位提示练习目标旋律。"],
            event_schema=["pitch", "key_index"],
            extra_quality_gates=["pitch_limited_to_material"],
        ),
    },
    "dizi_playable_board": {
        "version": "virtual_instrument_spec_v1",
        "instrument_id": "dizi_playable_board",
        "name": "笛子演奏板",
        "audience": "primary_school",
        "replace_physical_instrument": "笛子",
        "grade_bands": ["middle_primary", "upper_primary"],
        "runtime": "react_webaudio",
        "input_modes": _COMMON_INPUTS,
        "sound_source": "soundfont_proxy_flute_until_dizi_sample_ready",
        "pitch_set": ["do", "re", "mi", "sol", "la"],
        "constraints": {"only_allow_target_pitches": True, "show_breath_hint": True, "record_events": True},
        "teacher_controls": ["choose_pitch", "hide_labels", "limit_pitch_count", "reset"],
        "quality_gates": _COMMON_GATES + ["material_bound"],
        "open_source_dependencies": ["react", "soundfont-player", "webaudio"],
        "image2_required": False,
        "runtime_contract": _runtime_contract(
            ["DiziPlayableBoard", "SimpleKeyboardBoard"],
            ["instrument_timbre_match", "xylophone_creation", "classroom_band_roles"],
            ["学生能用笛子演奏板试听和演奏限定音；当前音色为长笛 SoundFont 近似，必须提示待补笛子实录。"],
            event_schema=["pitch", "breath_hint", "key_index"],
            extra_quality_gates=["pitch_limited_to_material", "exact_sample_needed"],
        ),
    },
    "flute_playable_board": {
        "version": "virtual_instrument_spec_v1",
        "instrument_id": "flute_playable_board",
        "name": "长笛演奏板",
        "audience": "primary_school",
        "replace_physical_instrument": "长笛",
        "grade_bands": ["middle_primary", "upper_primary"],
        "runtime": "react_webaudio",
        "input_modes": _COMMON_INPUTS,
        "sound_source": "soundfont_flute_sample",
        "pitch_set": ["do", "re", "mi", "fa", "sol", "la"],
        "constraints": {"only_allow_target_pitches": True, "show_breath_hint": True, "record_events": True},
        "teacher_controls": ["choose_pitch", "hide_labels", "limit_pitch_count", "reset"],
        "quality_gates": _COMMON_GATES + ["material_bound"],
        "open_source_dependencies": ["react", "soundfont-player", "webaudio"],
        "image2_required": False,
        "runtime_contract": _runtime_contract(
            ["FlutePlayableBoard", "SimpleKeyboardBoard"],
            ["instrument_timbre_match", "xylophone_creation", "classroom_band_roles"],
            ["学生能用长笛演奏板试听和演奏限定音，并记录音高、进入时间和教师调节。"],
            event_schema=["pitch", "breath_hint", "key_index"],
            extra_quality_gates=["pitch_limited_to_material", "real_sample_playback"],
        ),
    },
}


def list_virtual_instruments() -> list[dict[str, Any]]:
    return [validate_virtual_instrument_spec(_with_playable_asset_requirements(spec)) for spec in VIRTUAL_INSTRUMENT_REGISTRY.values()]


def get_virtual_instrument(instrument_id: str) -> dict[str, Any]:
    spec = VIRTUAL_INSTRUMENT_REGISTRY.get(str(instrument_id or ""))
    if not spec:
        raise ValueError(f"unknown virtual instrument: {instrument_id}")
    return validate_virtual_instrument_spec(_with_playable_asset_requirements(spec))
