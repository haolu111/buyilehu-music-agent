# 从教案文字和已上传材料中解析节拍、节奏、音高、唱名、音色、曲式等候选参数
from __future__ import annotations

from copy import deepcopy
import re
from typing import Any

from app.services.music.pitch_catalog import PITCH_DEFINITIONS, pitch_tokens_from_text, resolve_pitch_token


MUSIC_ELEMENT_BINDING_VERSION = "music_element_binding_v1"
MUSIC_ELEMENT_RETRIEVAL_VERSION = "music_element_retrieval_v1"
MUSIC_ENTITY_LOOKUP_VERSION = "music_entity_lookup_v1"

TEMPLATE_BY_ENTITY_TYPE = {
    "meter": "beat_guardian_core",
    "rhythm_pattern": "rhythm_echo_core",
    "pitch_motion": "pitch_ladder_core",
    "solfege_set": "solfege_target_core",
    "timbre_set": "timbre_detective_core",
    "form_structure": "form_treasure_core",
    "scale": "composition_puzzle_core",
    "composition_material": "composition_puzzle_core",
}

GAME_SLOTS_BY_TEMPLATE = {
    "beat_guardian_core": ["round_1.answer_sequence", "round_1.score_phrase"],
    "rhythm_echo_core": ["round_1.target_rhythm", "round_1.playback_tokens"],
    "pitch_ladder_core": ["round_1.target_melody", "round_1.playback_tokens"],
    "solfege_target_core": ["round_1.target_solfege", "round_1.playback_tokens"],
    "timbre_detective_core": ["round_1.listen_clip", "round_1.evidence_prompt"],
    "form_treasure_core": ["round_1.form_answer", "section_a.listen_clip"],
    "composition_puzzle_core": ["round_1.material_cards", "round_1.constraint_checks"],
}

ENTITY_TYPE_CANDIDATES = {
    "scale": [
        ("scale", "composition_puzzle_core", "五声音阶素材可作为创编卡和约束检查。"),
        ("pitch_motion", "pitch_ladder_core", "可把音阶音级转成旋律路线，但不负责开放创编。"),
        ("solfege_set", "solfege_target_core", "可听辨或唱回音级集合，但不负责旋律组合。"),
    ],
    "rhythm_pattern": [
        ("rhythm_pattern", "rhythm_echo_core", "节奏型可直接成为复刻目标。"),
        ("composition_material", "composition_puzzle_core", "节奏素材也可进入拼图创编。"),
    ],
    "pitch_motion": [
        ("pitch_motion", "pitch_ladder_core", "旋律走向可直接成为路线/高低判断。"),
        ("solfege_set", "solfege_target_core", "若目标强调唱名，可转为唱名击中。"),
    ],
    "solfege_set": [
        ("solfege_set", "solfege_target_core", "唱名集合可直接成为击中和唱回目标。"),
        ("pitch_motion", "pitch_ladder_core", "可把唱名顺序转成旋律路线。"),
    ],
    "timbre_set": [
        ("timbre_set", "timbre_detective_core", "音色和乐器可成为听辨证据。"),
    ],
    "form_structure": [
        ("form_structure", "form_treasure_core", "曲式结构可成为段落路线答案。"),
    ],
    "meter": [
        ("meter", "beat_guardian_core", "强弱拍和拍号可成为守拍/进入时机。"),
    ],
    "composition_material": [
        ("composition_material", "composition_puzzle_core", "素材卡和约束检查适合创编。"),
    ],
}

RHYTHM_KEYWORD_STEPS: tuple[tuple[str, str], ...] = (
    ("切分", "syncopation"),
    ("休止", "rest"),
    ("空拍", "rest"),
    ("附点", "dotted_quarter"),
    ("八分", "eighth_pair"),
    ("四分", "quarter"),
    ("二分", "half"),
)

SOLFEGE_ORDER = [str(pitch["id"]) for pitch in PITCH_DEFINITIONS]
SOLFEGE_MIDI_OFFSETS = {str(pitch["id"]): int(pitch["semitone"]) for pitch in PITCH_DEFINITIONS}
KNOWN_INSTRUMENTS = ["笛子", "长笛", "二胡", "小提琴", "古筝", "钢琴", "木鱼", "小鼓", "锣", "钹", "人声"]

MUSIC_ENTITY_LIBRARY: tuple[dict[str, Any], ...] = (
    {
        "semantic_term": "力度变化",
        "entity_type": "dynamics",
        "entity_id": "dynamic_contrast",
        "label": "力度强弱变化",
        "synonyms": ("力度变化", "力度强弱", "声音强弱", "渐强", "渐弱", "强弱变化"),
        "executable_fields": {
            "dynamic_levels": ["p", "f"],
            "contrast_pattern": ["soft", "strong"],
            "student_action": "compare_loudness",
        },
        "compatible_template_ids": ["composition_puzzle_core"],
        "confidence": 0.72,
        "needs_confirmation": True,
        "confirmation_gap": "需要教师补充对应谱面力度记号或音频强弱片段，才能把力度变化作为明确游戏答案。",
        "evidence": "本地音乐实体库：dynamic_contrast",
    },
    {
        "semantic_term": "节奏型",
        "entity_type": "rhythm_pattern",
        "entity_id": "basic_rhythm_pattern",
        "label": "基础节奏型",
        "synonyms": ("节奏型", "节奏", "时值组合", "节奏模仿", "听后拍回"),
        "executable_fields": {
            "pattern_steps": ["quarter", "eighth_pair"],
            "duration_beats": [1.0, 1.0],
            "constraint_checks": ["preserve_order", "match_duration_profile"],
        },
        "compatible_template_ids": ["rhythm_echo_core", "composition_puzzle_core"],
        "confidence": 0.78,
        "needs_confirmation": True,
        "confirmation_gap": "需要教师确认实际节奏顺序，或提供文字谱、MIDI、MusicXML 片段。",
        "evidence": "本地音乐实体库：basic_rhythm_pattern",
    },
    {
        "semantic_term": "音色辨别",
        "entity_type": "timbre_set",
        "entity_id": "instrument_timbre",
        "label": "乐器音色辨别",
        "synonyms": ("音色辨别", "音色听辨", "乐器识别", "乐器音色", "声音证据"),
        "executable_fields": {
            "instrument_pool": ["笛子", "二胡"],
            "evidence_traits": ["气息感", "弦鸣"],
            "comparison_pairs": [["笛子", "二胡"]],
        },
        "compatible_template_ids": ["timbre_detective_core"],
        "confidence": 0.84,
        "needs_confirmation": False,
        "confirmation_gap": "",
        "evidence": "本地音乐实体库：instrument_timbre",
    },
    {
        "semantic_term": "曲式结构",
        "entity_type": "form_structure",
        "entity_id": "aba_form",
        "label": "ABA 曲式结构",
        "synonyms": ("曲式结构", "曲式", "ABA", "A-B-A", "重复对比", "重复与对比", "主题再现", "段落结构"),
        "executable_fields": {
            "form_type": "ABA",
            "answer_pattern": ["A", "B", "A"],
            "timeline_segments": [
                {"id": "section_1", "label": "A", "function": "theme"},
                {"id": "section_2", "label": "B", "function": "contrast"},
                {"id": "section_3", "label": "A", "function": "return"},
            ],
        },
        "compatible_template_ids": ["form_treasure_core"],
        "confidence": 0.82,
        "needs_confirmation": True,
        "confirmation_gap": "需要教师确认实际段落边界或音频片段。",
        "evidence": "本地音乐实体库：aba_form",
    },
    {
        "semantic_term": "强弱拍",
        "entity_type": "meter",
        "entity_id": "meter_accent",
        "label": "强弱拍规律",
        "synonyms": ("强弱拍", "强拍", "弱拍", "节拍强弱", "拍号"),
        "executable_fields": {
            "meter": "2/4",
            "beat_count": 2,
            "accent_pattern": ["strong", "weak"],
            "target_beats": [1],
        },
        "compatible_template_ids": ["beat_guardian_core"],
        "confidence": 0.8,
        "needs_confirmation": True,
        "confirmation_gap": "需要教师确认拍号或目标进入拍位。",
        "evidence": "本地音乐实体库：meter_accent",
    },
    {
        "semantic_term": "旋律走向",
        "entity_type": "pitch_motion",
        "entity_id": "melodic_contour",
        "label": "旋律高低走向",
        "synonyms": ("旋律走向", "旋律线", "音高高低", "上行", "下行", "级进", "跳进"),
        "executable_fields": {
            "motions": ["ascending", "descending"],
            "target_melody": ["do", "re", "mi", "sol"],
            "midi_offsets": [0, 2, 4, 7],
        },
        "compatible_template_ids": ["pitch_ladder_core", "solfege_target_core"],
        "confidence": 0.76,
        "needs_confirmation": True,
        "confirmation_gap": "需要教师确认目标旋律或唱名路线。",
        "evidence": "本地音乐实体库：melodic_contour",
    },
    {
        "semantic_term": "五声音阶",
        "entity_type": "scale",
        "entity_id": "chinese_pentatonic",
        "label": "五声音阶素材",
        "synonyms": ("五声音阶", "五声", "宫商角徵羽", "宫", "商", "角", "徵", "羽"),
        "executable_fields": {
            "scale_degrees": ["do", "re", "mi", "sol", "la"],
            "gongche_degrees": ["宫", "商", "角", "徵", "羽"],
            "constraint_checks": ["use_pentatonic_degrees", "end_on_tonic_or_la"],
        },
        "compatible_template_ids": ["composition_puzzle_core", "pitch_ladder_core", "solfege_target_core"],
        "confidence": 0.82,
        "needs_confirmation": True,
        "confirmation_gap": "需要教师确认实际调高、结束音或可用素材卡。",
        "evidence": "本地音乐实体库：chinese_pentatonic",
    },
)


def resolve_music_element_binding(
    *,
    semantic_text: str,
    song_material: dict[str, Any] | None = None,
    template_id: str = "",
) -> dict[str, Any]:
    """Resolve a teacher-facing music-element phrase into a playable entity."""

    material = song_material if isinstance(song_material, dict) else {}
    text = str(semantic_text or "").strip()
    canonical = _canonical_element(text)
    resolved_template_id = template_id or TEMPLATE_BY_ENTITY_TYPE.get(canonical["entity_type"], "")
    entity = _entity_for(canonical, text, material)
    material_ref = _material_reference(material, canonical)
    has_material = bool(material_ref)
    confidence = _confidence(canonical, has_material=has_material)
    requires_confirmation = not has_material
    status = "resolved" if confidence >= 0.75 and not requires_confirmation else "needs_confirmation"
    confirmation_reason = "" if not requires_confirmation else "缺少可绑定的谱面、MIDI、音频片段或教师确认文字谱。"

    return _drop_empty(
        {
            "version": MUSIC_ELEMENT_BINDING_VERSION,
            "status": status,
            "semantic_element": text,
            "canonical_element": canonical,
            "entity": entity,
            "source_material": material_ref,
            "template_match": {
                "template_id": resolved_template_id,
                "match_basis": "music_element_entity",
                "confidence": confidence,
            },
            "game_slots": GAME_SLOTS_BY_TEMPLATE.get(resolved_template_id, []),
            "requires_teacher_confirmation": requires_confirmation,
            "confirmation_reason": confirmation_reason,
        }
    )


def retrieve_music_element_candidates(
    *,
    semantic_text: str,
    song_material: dict[str, Any] | None = None,
    template_id: str = "",
) -> dict[str, Any]:
    """Return ranked candidate entities before committing to one template."""

    material = song_material if isinstance(song_material, dict) else {}
    text = str(semantic_text or "").strip()
    canonical = _canonical_element(text)
    candidates: list[dict[str, Any]] = []
    for rank, (entity_type, candidate_template_id, rationale) in enumerate(_candidate_specs(canonical, template_id), start=1):
        candidate_canonical = _canonical_for_entity_type(entity_type, text, canonical)
        entity = _entity_for(candidate_canonical, text, material)
        material_ref = _material_reference(material, candidate_canonical)
        has_material = bool(material_ref)
        confidence = _candidate_confidence(rank, has_material=has_material, requested=template_id == candidate_template_id)
        requires_confirmation = _candidate_requires_confirmation(entity, has_material=has_material)
        candidate = _drop_empty(
            {
                "rank": rank,
                "status": "resolved" if confidence >= 0.75 and not requires_confirmation else "needs_confirmation",
                "canonical_element": candidate_canonical,
                "entity": entity,
                "source_material": material_ref,
                "template_match": {
                    "template_id": candidate_template_id,
                    "match_basis": "music_element_retrieval",
                    "confidence": confidence,
                },
                "game_slots": GAME_SLOTS_BY_TEMPLATE.get(candidate_template_id, []),
                "rationale": rationale,
                "requires_teacher_confirmation": requires_confirmation,
            }
        )
        candidates.append(candidate)

    return {
        "version": MUSIC_ELEMENT_RETRIEVAL_VERSION,
        "query": {
            "semantic_text": text,
            "requested_template_id": template_id,
        },
        "canonical_query": canonical,
        "candidates": candidates,
        "selected_template_id": candidates[0]["template_match"]["template_id"] if candidates else "",
        "requires_teacher_confirmation": any(candidate.get("requires_teacher_confirmation") for candidate in candidates),
    }


def retrieve_music_element_entities(
    *,
    semantic_text: str,
    song_material: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Look up teacher semantic terms in the controlled music-entity library."""

    text = str(semantic_text or "").strip()
    material = song_material if isinstance(song_material, dict) else {}
    entities = _material_entity_lookup_items(material, text)
    entities.extend(_entity_lookup_item(entry, text, material) for entry in MUSIC_ENTITY_LIBRARY if _entry_matches_text(entry, text))
    entities = _dedupe_lookup_entities(entities)
    if not entities:
        entities = [_unknown_entity_lookup_item(text)]
    return {
        "version": MUSIC_ENTITY_LOOKUP_VERSION,
        "status": "resolved" if entities and all(not item.get("needs_confirmation") for item in entities) else "needs_confirmation",
        "query": {"semantic_text": text},
        "entities": entities,
        "requires_teacher_confirmation": any(item.get("needs_confirmation") for item in entities),
    }


def _canonical_element(text: str) -> dict[str, str]:
    lowered = text.lower()
    if any(keyword in text for keyword in ("切分", "附点", "休止", "空拍", "节奏", "时值")):
        if "切分" in text:
            element_id = "syncopation"
            label = "切分节奏"
        elif "休止" in text or "空拍" in text:
            element_id = "rest_rhythm"
            label = "休止节奏"
        elif "附点" in text:
            element_id = "dotted_rhythm"
            label = "附点节奏"
        else:
            element_id = "rhythm_pattern"
            label = "节奏型"
        return {"id": element_id, "label": label, "entity_type": "rhythm_pattern", "domain": "rhythm"}
    if any(keyword in text for keyword in ("五声", "宫", "商", "角", "徵", "羽", "民族调式")):
        return {"id": "chinese_pentatonic", "label": "五声音阶", "entity_type": "scale", "domain": "pitch"}
    if any(keyword in text for keyword in ("唱名", "听音击中", "do", "re", "mi", "sol", "la")):
        return {"id": "movable_do_solfege", "label": "首调唱名", "entity_type": "solfege_set", "domain": "pitch"}
    if any(keyword in text for keyword in ("音高", "旋律走向", "旋律线", "上行", "下行", "级进", "跳进")):
        return {"id": "melodic_contour", "label": "旋律高低走向", "entity_type": "pitch_motion", "domain": "pitch"}
    if any(keyword in text for keyword in ("音色", "乐器", "笛子", "二胡", "小提琴", "钢琴", "古筝")):
        return {"id": "instrument_timbre", "label": "乐器音色", "entity_type": "timbre_set", "domain": "timbre"}
    if any(keyword in text for keyword in ("曲式", "aba", "a-b-a", "回旋", "段落", "重复对比")) or "ABA" in text.upper():
        return {"id": "aba_form" if "ABA" in text.upper() else "form_structure", "label": "曲式结构", "entity_type": "form_structure", "domain": "form"}
    if any(keyword in text for keyword in ("强拍", "弱拍", "拍号", "节拍", "二拍子", "三拍子", "四拍子")):
        if "三拍" in text or "3/4" in text:
            return {"id": "triple_meter_accent", "label": "三拍子强弱拍", "entity_type": "meter", "domain": "meter"}
        if "四拍" in text or "4/4" in text:
            return {"id": "quadruple_meter_accent", "label": "四拍子强弱拍", "entity_type": "meter", "domain": "meter"}
        if "二拍" in text or "2/4" in text:
            return {"id": "duple_meter_accent", "label": "二拍子强弱拍", "entity_type": "meter", "domain": "meter"}
        return {"id": "meter_accent", "label": "强弱拍", "entity_type": "meter", "domain": "meter"}
    if any(keyword in lowered for keyword in ("compose", "composition")) or any(keyword in text for keyword in ("创编", "拼图", "素材卡")):
        return {"id": "composition_material", "label": "创编素材", "entity_type": "composition_material", "domain": "composition"}
    return {"id": "generic_music_element", "label": "综合音乐要素", "entity_type": "composition_material", "domain": "general"}


def _entry_matches_text(entry: dict[str, Any], text: str) -> bool:
    synonyms = entry.get("synonyms") if isinstance(entry.get("synonyms"), tuple) else ()
    return any(str(term or "").strip() and str(term) in text for term in synonyms)


def _entity_lookup_item(entry: dict[str, Any], text: str, material: dict[str, Any]) -> dict[str, Any]:
    semantic_term = str(entry.get("semantic_term") or "").strip()
    executable_fields = deepcopy(entry.get("executable_fields") or {})
    if entry.get("entity_type") == "rhythm_pattern":
        material_pattern = _pattern_steps_with_source_from_material(material)
        if material_pattern["steps"]:
            executable_fields["pattern_steps"] = material_pattern["steps"]
            executable_fields["duration_beats"] = [_duration_for_rhythm_step(step) for step in material_pattern["steps"]]
            executable_fields["source_span"] = material_pattern["source_span"]
            executable_fields["extraction_basis"] = _rhythm_extraction_basis(material_pattern["source_span"])
    if entry.get("entity_type") == "timbre_set":
        instruments = [item for item in KNOWN_INSTRUMENTS if item in text]
        if instruments:
            traits = _timbre_traits(text)
            executable_fields["instrument_pool"] = instruments
            executable_fields["evidence_traits"] = traits
            executable_fields["comparison_pairs"] = _comparison_pairs(instruments)
            executable_fields["trait_targets"] = _trait_targets(instruments, traits)
    return _drop_empty(
        {
            "semantic_term": semantic_term,
            "entity_type": entry.get("entity_type", ""),
            "entity_id": entry.get("entity_id", ""),
            "label": entry.get("label", ""),
            "executable_fields": executable_fields,
            "compatible_template_ids": deepcopy(entry.get("compatible_template_ids") or []),
            "confidence": entry.get("confidence"),
            "needs_confirmation": bool(entry.get("needs_confirmation")),
            "confirmation_gap": entry.get("confirmation_gap", ""),
            "evidence": entry.get("evidence", ""),
        }
    )


def _material_entity_lookup_items(material: dict[str, Any], text: str) -> list[dict[str, Any]]:
    if not isinstance(material, dict) or not material:
        return []
    entities: list[dict[str, Any]] = []
    rhythm = _pattern_steps_with_source_from_material(material)
    if rhythm["steps"] and _material_text_requests(text, ("节奏", "拍回", "时值", "复刻", "休止", "切分", "附点")):
        phrase_id = str(rhythm["source_span"].get("phrase_id") or "phrase")
        entities.append(
            {
                "semantic_term": "节奏型",
                "entity_type": "rhythm_pattern",
                "entity_id": f"material_rhythm_{phrase_id}",
                "label": "材料节奏型",
                "executable_fields": {
                    "pattern_steps": deepcopy(rhythm["steps"]),
                    "duration_beats": [_duration_for_rhythm_step(step) for step in rhythm["steps"]],
                    "constraint_checks": ["preserve_order", "match_duration_profile"],
                },
                "source_span": deepcopy(rhythm["source_span"]),
                "compatible_template_ids": ["rhythm_echo_core", "composition_puzzle_core"],
                "confidence": 0.94,
                "needs_confirmation": False,
                "confirmation_gap": "",
                "evidence": _rhythm_extraction_basis(rhythm["source_span"]),
            }
        )

    pitch = _pitch_tokens_with_source_from_material(material)
    if pitch["tokens"] and _material_text_requests(text, ("旋律", "音高", "唱名", "听音", "路线", "上行", "下行")):
        phrase_id = str(pitch["source_span"].get("phrase_id") or "phrase")
        offsets = [SOLFEGE_MIDI_OFFSETS[token] for token in pitch["tokens"] if token in SOLFEGE_MIDI_OFFSETS]
        if _material_text_requests(text, ("旋律", "音高", "路线", "上行", "下行")):
            entities.append(
                {
                    "semantic_term": "旋律走向",
                    "entity_type": "pitch_motion",
                    "entity_id": f"material_pitch_{phrase_id}",
                    "label": "材料旋律路线",
                    "executable_fields": {
                        "target_melody": deepcopy(pitch["tokens"]),
                        "target_solfege": deepcopy(pitch["tokens"]),
                        "midi_offsets": offsets,
                        "motions": _motions_from_pitch_tokens(pitch["tokens"]),
                    },
                    "source_span": deepcopy(pitch["source_span"]),
                    "compatible_template_ids": ["pitch_ladder_core", "solfege_target_core"],
                    "confidence": 0.94,
                    "needs_confirmation": False,
                    "confirmation_gap": "",
                    "evidence": _pitch_extraction_basis(pitch["source_span"]),
                }
            )
        if _material_text_requests(text, ("唱名", "听音", "do", "re", "mi", "sol", "la")):
            entities.append(
                {
                    "semantic_term": "唱名",
                    "entity_type": "solfege_set",
                    "entity_id": f"material_solfege_{phrase_id}",
                    "label": "材料唱名集合",
                    "executable_fields": {
                        "target_solfege": deepcopy(pitch["tokens"]),
                        "target_melody": deepcopy(pitch["tokens"]),
                        "midi_offsets": offsets,
                    },
                    "source_span": deepcopy(pitch["source_span"]),
                    "compatible_template_ids": ["solfege_target_core", "pitch_ladder_core"],
                    "confidence": 0.94,
                    "needs_confirmation": False,
                    "confirmation_gap": "",
                    "evidence": _pitch_extraction_basis(pitch["source_span"]),
                }
            )

    clip = _source_clip_from_material(material)
    if clip:
        entities.append(clip)
    return entities


def _dedupe_lookup_entities(entities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for entity in entities:
        if not isinstance(entity, dict):
            continue
        key = str(entity.get("entity_id") or entity.get("entity_type") or "")
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(entity)
    return deduped


def _unknown_entity_lookup_item(text: str) -> dict[str, Any]:
    return {
        "semantic_term": text,
        "entity_type": "unknown_music_element",
        "entity_id": "unknown_music_element",
        "label": "待确认音乐要素",
        "executable_fields": {},
        "compatible_template_ids": [],
        "confidence": 0.0,
        "needs_confirmation": True,
        "confirmation_gap": "需要教师补充这个音乐要素对应的谱面、音频片段、课堂例子或可操作判断标准。",
        "evidence": "未命中本地音乐实体库，系统不生成专业音乐答案。",
    }


def _candidate_specs(canonical: dict[str, str], template_id: str) -> list[tuple[str, str, str]]:
    entity_type = canonical.get("entity_type", "")
    specs = list(ENTITY_TYPE_CANDIDATES.get(entity_type, []))
    if not specs:
        resolved_template = template_id or TEMPLATE_BY_ENTITY_TYPE.get(entity_type, "composition_puzzle_core")
        specs = [(entity_type or "composition_material", resolved_template, "使用默认音乐实体候选。")]
    if template_id:
        requested = [item for item in specs if item[1] == template_id]
        others = [item for item in specs if item[1] != template_id]
        specs = requested + others if requested else [(entity_type, template_id, "教师指定模板候选。")] + specs
    return specs


def _canonical_for_entity_type(entity_type: str, text: str, base: dict[str, str]) -> dict[str, str]:
    if entity_type == base.get("entity_type"):
        return deepcopy(base)
    labels = {
        "meter": ("meter_accent", "强弱拍", "meter"),
        "rhythm_pattern": ("rhythm_pattern", "节奏型", "rhythm"),
        "pitch_motion": ("melodic_contour", "旋律高低走向", "pitch"),
        "solfege_set": ("movable_do_solfege", "首调唱名", "pitch"),
        "timbre_set": ("instrument_timbre", "乐器音色", "timbre"),
        "form_structure": ("form_structure", "曲式结构", "form"),
        "scale": ("chinese_pentatonic", "五声音阶", "pitch"),
        "composition_material": ("composition_material", "创编素材", "composition"),
    }
    element_id, label, domain = labels.get(entity_type, ("generic_music_element", "综合音乐要素", "general"))
    if entity_type == "scale" and any(keyword in text for keyword in ("五声", "宫", "商", "角", "徵", "羽")):
        element_id = "chinese_pentatonic"
        label = "五声音阶"
    return {"id": element_id, "label": label, "entity_type": entity_type, "domain": domain}


def _entity_for(canonical: dict[str, str], text: str, material: dict[str, Any]) -> dict[str, Any]:
    entity_type = canonical.get("entity_type")
    if entity_type == "rhythm_pattern":
        material_pattern = _pattern_steps_with_source_from_material(material)
        steps = material_pattern["steps"] or _pattern_steps_from_text(text)
        source_span = material_pattern["source_span"] or _semantic_text_source_span(text)
        return {
            "kind": "rhythm_pattern",
            "playback": {"pattern_steps": steps},
            "answer_tokens": steps,
            "duration_beats": [_duration_for_rhythm_step(step) for step in steps],
            "constraint_checks": ["preserve_order", "match_duration_profile"],
            "source_span": source_span,
            "confidence": _rhythm_entity_confidence(source_span),
            "extraction_basis": _rhythm_extraction_basis(source_span),
        }
    if entity_type == "scale":
        return {
            "kind": "scale",
            "scale_type": "chinese_pentatonic",
            "scale_degrees": ["do", "re", "mi", "sol", "la"],
            "gongche_degrees": ["宫", "商", "角", "徵", "羽"],
            "candidate_pitch_sets": ["C-D-E-G-A", "D-E-F#-A-B"],
            "constraint_checks": ["use_pentatonic_degrees", "end_on_tonic_or_la"],
        }
    if entity_type == "solfege_set":
        pitches = _solfege_tokens(text) or _solfege_tokens(" ".join(_pattern_steps_from_material(material)))
        return {"kind": "solfege_set", "target_solfege": pitches or ["do", "mi", "sol"]}
    if entity_type == "pitch_motion":
        target_melody = _solfege_route_from_text(text) or _pattern_steps_from_material(material)
        return _drop_empty(
            {
                "kind": "pitch_motion",
                "motions": _motions_from_text(text),
                "target_melody": target_melody,
                "midi_offsets": [SOLFEGE_MIDI_OFFSETS[token] for token in target_melody if token in SOLFEGE_MIDI_OFFSETS],
            }
        )
    if entity_type == "timbre_set":
        instruments = [item for item in KNOWN_INSTRUMENTS if item in text]
        pool = instruments or ["笛子", "二胡"]
        traits = _timbre_traits(text)
        return {
            "kind": "timbre_set",
            "instrument_pool": pool,
            "evidence_traits": traits,
            "comparison_pairs": _comparison_pairs(pool),
            "trait_targets": _trait_targets(pool, traits),
        }
    if entity_type == "form_structure":
        pattern = _answer_pattern_from_text(text)
        return {
            "kind": "form_structure",
            "form_type": "ABA" if pattern == ["A", "B", "A"] else "重复对比",
            "answer_pattern": pattern,
            "timeline_segments": _form_timeline_segments(pattern),
        }
    if entity_type == "meter":
        meter = _meter_from_text(text)
        beat_count = _beat_count_for_meter(meter)
        return {
            "kind": "meter",
            "meter": meter,
            "beat_count": beat_count,
            "accent_pattern": _accent_pattern_for_meter(meter),
            "target_beats": _target_beats_from_text(text, beat_count),
        }
    if entity_type == "composition_material":
        return {
            "kind": "composition_material",
            "melody_cards": ["do", "re", "mi", "sol", "la"] if any(keyword in text for keyword in ("五声", "宫", "商", "角", "徵", "羽")) else [],
            "rhythm_cards": _pattern_steps_from_text(text) if any(keyword in text for keyword in ("节奏", "时值", "休止", "切分", "附点")) else [],
            "constraint_checks": ["teacher_confirm_material_fit"],
        }
    return {"kind": entity_type or "music_element"}


def _material_reference(material: dict[str, Any], canonical: dict[str, str]) -> dict[str, Any]:
    source = material.get("source", {}) if isinstance(material.get("source"), dict) else {}
    phrases = material.get("phrases", []) if isinstance(material.get("phrases"), list) else []
    phrase = next((item for item in phrases if isinstance(item, dict)), {})
    if not source and not phrase:
        return {}
    return _drop_empty(
        {
            "song_title": material.get("song_title") or source.get("song_title") or "",
            "source_kind": source.get("kind", ""),
            "source_filename": source.get("filename", ""),
            "phrase_id": phrase.get("id", ""),
            "phrase_label": phrase.get("label", ""),
            "entity_basis": canonical.get("id", ""),
        }
    )


def _pattern_steps_from_material(material: dict[str, Any]) -> list[str]:
    return _pattern_steps_with_source_from_material(material)["steps"]


def _pattern_steps_with_source_from_material(material: dict[str, Any]) -> dict[str, Any]:
    phrases = material.get("phrases", []) if isinstance(material.get("phrases"), list) else []
    for phrase in phrases:
        if not isinstance(phrase, dict):
            continue
        for key in ("target_sequence", "playback_tokens", "main_melody"):
            value = phrase.get(key)
            if isinstance(value, list):
                steps = [str(item).strip() for item in value if str(item or "").strip()]
                if steps:
                    return {
                        "steps": steps,
                        "source_span": _drop_empty(
                            {
                                "kind": "material_phrase",
                                "phrase_id": phrase.get("id", ""),
                                "phrase_label": phrase.get("label", ""),
                                "field": key,
                            }
                        ),
                    }
    return {"steps": [], "source_span": {}}


def _pitch_tokens_with_source_from_material(material: dict[str, Any]) -> dict[str, Any]:
    phrases = material.get("phrases", []) if isinstance(material.get("phrases"), list) else []
    for phrase in phrases:
        if not isinstance(phrase, dict):
            continue
        for key in ("target_sequence", "main_melody"):
            tokens = _solfege_list_from_value(phrase.get(key))
            if tokens:
                return {
                    "tokens": tokens,
                    "source_span": _drop_empty(
                        {
                            "kind": "material_phrase",
                            "phrase_id": phrase.get("id", ""),
                            "phrase_label": phrase.get("label", ""),
                            "field": key,
                        }
                    ),
                }
        playback_tokens = _solfege_list_from_playback_tokens(phrase.get("playback_tokens"))
        if playback_tokens:
            return {
                "tokens": playback_tokens,
                "source_span": _drop_empty(
                    {
                        "kind": "material_phrase",
                        "phrase_id": phrase.get("id", ""),
                        "phrase_label": phrase.get("label", ""),
                        "field": "playback_tokens",
                    }
                ),
            }
    return {"tokens": [], "source_span": {}}


def _solfege_list_from_value(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    tokens: list[str] = []
    for item in value:
        pitch = resolve_pitch_token(item)
        if pitch:
            tokens.append(str(pitch["id"]))
    return tokens


def _solfege_list_from_playback_tokens(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    tokens: list[str] = []
    for item in value:
        if isinstance(item, dict):
            pitch = resolve_pitch_token(item.get("solfege") or item.get("pitch") or "")
            if pitch:
                tokens.append(str(pitch["id"]))
                continue
            midi = item.get("midi")
            if isinstance(midi, (int, float)):
                tokens.append(_solfege_from_midi(int(midi)))
        else:
            pitch = resolve_pitch_token(item)
            if pitch:
                tokens.append(str(pitch["id"]))
    return tokens


def _solfege_from_midi(midi: int) -> str:
    pitch_class = midi % 12
    by_pitch_class = {
        int(pitch["semitone"]): str(pitch["id"])
        for pitch in PITCH_DEFINITIONS
        if pitch["role"] == "pitch_class"
    }
    return by_pitch_class.get(pitch_class, "do")


def _motions_from_pitch_tokens(tokens: list[str]) -> list[str]:
    offsets = [SOLFEGE_MIDI_OFFSETS[token] for token in tokens if token in SOLFEGE_MIDI_OFFSETS]
    motions: list[str] = []
    if any(later > earlier for earlier, later in zip(offsets, offsets[1:])):
        motions.append("ascending")
    if any(later < earlier for earlier, later in zip(offsets, offsets[1:])):
        motions.append("descending")
    return motions or ["stepwise"]


def _pitch_extraction_basis(source_span: dict[str, Any]) -> str:
    field = str(source_span.get("field") or "phrase")
    return f"material_phrase.{field}"


def _source_clip_from_material(material: dict[str, Any]) -> dict[str, Any]:
    source = material.get("source") if isinstance(material.get("source"), dict) else {}
    phrases = material.get("phrases", []) if isinstance(material.get("phrases"), list) else []
    phrase = next((item for item in phrases if isinstance(item, dict) and item.get("audio_clip_url")), {})
    audio_url = str(phrase.get("audio_clip_url") or source.get("source_audio_url") or "").strip()
    if not audio_url:
        return {}
    phrase_id = str(phrase.get("id") or "source").strip() or "source"
    return {
        "semantic_term": "音频材料",
        "entity_type": "source_clip",
        "entity_id": f"source_clip_{phrase_id}",
        "label": str(phrase.get("label") or material.get("song_title") or "音频片段"),
        "executable_fields": _drop_empty(
            {
                "audio_clip_url": audio_url,
                "source_audio_url": source.get("source_audio_url", ""),
                "requires_teacher_confirmation": True,
            }
        ),
        "source_span": _drop_empty(
            {
                "kind": "audio_clip",
                "phrase_id": phrase.get("id", ""),
                "phrase_label": phrase.get("label", ""),
                "field": "audio_clip_url" if phrase.get("audio_clip_url") else "source_audio_url",
            }
        ),
        "compatible_template_ids": ["timbre_detective_core", "form_treasure_core"],
        "confidence": 0.58,
        "needs_confirmation": True,
        "confirmation_gap": "音频材料只能作为低置信候选，需要教师确认听辨目标、答案或片段边界。",
        "evidence": "audio_material.low_confidence_source_clip",
    }


def _material_text_requests(text: str, terms: tuple[str, ...]) -> bool:
    if not text.strip():
        return True
    lowered = text.lower()
    return any(term in text or term in lowered for term in terms)


def _semantic_text_source_span(text: str) -> dict[str, Any]:
    return _drop_empty({"kind": "semantic_text", "text": text})


def _rhythm_entity_confidence(source_span: dict[str, Any]) -> float:
    return 0.94 if source_span.get("kind") == "material_phrase" else 0.68


def _rhythm_extraction_basis(source_span: dict[str, Any]) -> str:
    if source_span.get("kind") == "material_phrase":
        field = str(source_span.get("field") or "phrase")
        return f"material_phrase.{field}"
    return "semantic_text.rhythm_keywords"


def _pattern_steps_from_text(text: str) -> list[str]:
    ordered = _ordered_rhythm_steps_from_text(text)
    if ordered:
        return ordered
    steps = ["quarter"]
    for keyword, step in RHYTHM_KEYWORD_STEPS:
        if keyword in text and step not in steps:
            steps.append(step)
    if len(steps) == 1:
        steps.append("eighth_pair")
    return steps


def _ordered_rhythm_steps_from_text(text: str) -> list[str]:
    token_specs: tuple[tuple[str, tuple[str, ...]], ...] = (
        ("dotted_quarter", ("附点", "ta.")),
        ("syncopation", ("切分", "syncopation")),
        ("eighth_pair", ("八分八分", "八分", "ti-ti", "titi")),
        ("rest", ("休止", "空拍", "休")),
        ("half", ("二分", "ta-a")),
        ("quarter", ("四分", "ta")),
    )
    normalized = text.replace("，", " ").replace("。", " ").replace(",", " ").replace("、", " ")
    chunks = [chunk for chunk in normalized.split() if chunk]
    pattern: list[str] = []
    for chunk in chunks:
        for step, keywords in token_specs:
            if any(keyword in chunk for keyword in keywords):
                pattern.append(step)
                break
    return pattern if len(pattern) >= 2 else []


def _duration_for_rhythm_step(step: str) -> float:
    return {
        "quarter": 1.0,
        "eighth_pair": 1.0,
        "rest": 1.0,
        "half": 2.0,
        "dotted_quarter": 1.5,
        "syncopation": 2.0,
    }.get(step, 1.0)


def _solfege_tokens(text: str) -> list[str]:
    found = _pitch_tokens_from_text(text)
    return [pitch for pitch in SOLFEGE_ORDER if pitch in found]


def _solfege_route_from_text(text: str) -> list[str]:
    return _pitch_tokens_from_text(text)


def _pitch_tokens_from_text(text: str) -> list[str]:
    return pitch_tokens_from_text(text)


def _motions_from_text(text: str) -> list[str]:
    motions: list[str] = []
    if "上行" in text:
        motions.append("ascending")
    if "下行" in text:
        motions.append("descending")
    if "级进" in text:
        motions.append("stepwise")
    if "跳进" in text:
        motions.append("leap")
    return motions or ["ascending", "descending"]


def _timbre_traits(text: str) -> list[str]:
    traits = [trait for trait in ["明亮", "柔和", "气息感", "弦鸣", "敲击感", "持续", "短促"] if trait in text]
    return traits or ["音色证据"]


def _comparison_pairs(pool: list[str]) -> list[list[str]]:
    if len(pool) < 2:
        return []
    return [[pool[index], pool[index + 1]] for index in range(len(pool) - 1)]


def _trait_targets(pool: list[str], traits: list[str]) -> dict[str, list[str]]:
    catalog = {
        "笛子": ["气息感", "明亮"],
        "长笛": ["气息感", "明亮"],
        "二胡": ["弦鸣", "柔和"],
        "小提琴": ["弦鸣", "明亮"],
        "古筝": ["弦鸣", "短促"],
        "钢琴": ["敲击感", "明亮"],
        "木鱼": ["敲击感", "短促"],
        "小鼓": ["敲击感", "短促"],
        "人声": ["气息感", "柔和"],
    }
    targets: dict[str, list[str]] = {}
    for instrument in pool:
        matched = [trait for trait in traits if trait in catalog.get(instrument, [])]
        targets[instrument] = matched or traits[:1]
    return targets


def _answer_pattern_from_text(text: str) -> list[str]:
    normalized = text.upper().replace("-", "")
    if "ABA" in normalized or "再现" in text:
        return ["A", "B", "A"]
    if "回旋" in text:
        return ["A", "B", "A", "C", "A"]
    if "重复对比" in text or "重复与对比" in text:
        return ["A", "A", "B"]
    return ["A", "B", "A"]


def _form_timeline_segments(pattern: list[str]) -> list[dict[str, Any]]:
    function_by_label = {"A": "theme", "B": "contrast", "C": "new_material"}
    counts: dict[str, int] = {}
    segments = []
    for index, label in enumerate(pattern, start=1):
        counts[label] = counts.get(label, 0) + 1
        function = "return" if label == "A" and counts[label] > 1 else function_by_label.get(label, "section")
        segments.append({"id": f"section_{index}", "label": label, "function": function})
    return segments


def _meter_from_text(text: str) -> str:
    if "三拍" in text or "3/4" in text:
        return "3/4"
    if "四拍" in text or "4/4" in text:
        return "4/4"
    return "2/4" if "二拍" in text or "2/4" in text else ""


def _beat_count_for_meter(meter: str) -> int:
    return {"2/4": 2, "3/4": 3, "4/4": 4}.get(meter, 0)


def _accent_pattern_for_meter(meter: str) -> list[str]:
    if meter == "3/4":
        return ["strong", "weak", "weak"]
    if meter == "4/4":
        return ["strong", "weak", "secondary", "weak"]
    if meter == "2/4":
        return ["strong", "weak"]
    return ["strong"]


def _target_beats_from_text(text: str, beat_count: int) -> list[int]:
    if "每拍" in text or "全部拍" in text:
        return list(range(1, beat_count + 1)) if beat_count else [1]
    if "第1拍" in text or "第一拍" in text:
        return [1]
    if "第2拍" in text or "第二拍" in text:
        return [2]
    if "第3拍" in text or "第三拍" in text:
        return [3]
    if "第4拍" in text or "第四拍" in text:
        return [4]
    if "次强拍" in text and beat_count >= 4:
        return [3]
    if "强拍进入" in text or "强拍做动作" in text or "强拍回应" in text:
        return [1]
    if ("强弱拍" in text or "强弱弱" in text) and not any(keyword in text for keyword in ("弱拍进入", "弱拍做动作", "弱拍回应")):
        return [1]
    if "弱拍" in text:
        return list(range(2, beat_count + 1)) if beat_count >= 2 else [1]
    if "强拍" in text or "重拍" in text:
        return [1]
    return [1]


def _confidence(canonical: dict[str, str], *, has_material: bool) -> float:
    if canonical.get("id") == "generic_music_element":
        return 0.42
    return 0.9 if has_material else 0.68


def _candidate_confidence(rank: int, *, has_material: bool, requested: bool) -> float:
    base = 0.9 if has_material else 0.72
    if requested:
        base += 0.06
    base -= max(0, rank - 1) * 0.08
    return round(max(0.45, min(0.96, base)), 2)


def _candidate_requires_confirmation(entity: dict[str, Any], *, has_material: bool) -> bool:
    confidence = entity.get("confidence")
    if isinstance(confidence, (int, float)):
        return float(confidence) < 0.75
    return not has_material


def _drop_empty(payload: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in payload.items():
        if value in ("", None, [], {}):
            continue
        result[key] = deepcopy(value)
    return result
