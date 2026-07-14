from __future__ import annotations

import base64
import json
import os
import re
import tempfile
import urllib.error
import urllib.request
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from app.services.llm_config import llm_runtime_config, normalize_chat_ecnu_model_name

SOLFEGE_TO_PITCH = {
    "do": 60,
    "re": 62,
    "mi": 64,
    "fa": 65,
    "sol": 67,
    "so": 67,
    "la": 69,
    "si": 71,
    "ti": 71,
    "1": 60,
    "2": 62,
    "3": 64,
    "4": 65,
    "5": 67,
    "6": 69,
    "7": 71,
    "宫": 60,
    "商": 62,
    "角": 64,
    "徵": 67,
    "徴": 67,
    "羽": 69,
}

PITCH_TO_SOLFEGE = {
    0: "do",
    1: "di",
    2: "re",
    3: "ri",
    4: "mi",
    5: "fa",
    6: "fi",
    7: "sol",
    8: "si",
    9: "la",
    10: "li",
    11: "ti",
}

TEXT_EXTENSIONS = {".txt", ".md", ".markdown", ".csv"}
MIDI_EXTENSIONS = {".mid", ".midi"}
MUSICXML_EXTENSIONS = {".musicxml", ".xml", ".mxl"}
SCORE_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".aac", ".flac"}
SCORE_REVIEW_TEXT_LIMIT = 1200


def _score_vision_model_name() -> str:
    configured = (
        os.getenv("CHAT_ECNU_SCORE_MODEL")
        or os.getenv("SCORE_VISION_MODEL")
        or ""
    ).strip()
    if configured:
        return normalize_chat_ecnu_model_name(configured)
    if llm_runtime_config().get("provider") == "chat_ecnu":
        return "ecnu-vl"
    return normalize_chat_ecnu_model_name(os.getenv("CHAT_ECNU_MODEL") or "ecnu-max")


def score_omr_status() -> dict[str, Any]:
    llm_config = llm_runtime_config()
    model = _score_vision_model_name()
    return {
        "version": "score_multimodal_llm_v1",
        "runtime_network_required": True,
        "score_parser": {
            "engine": model,
            "available": bool(llm_config.get("enabled")),
            "provider": llm_config.get("provider", ""),
            "model": model,
            "source": "远端大模型视觉识谱，仅保留这一路解析链路。",
            "output": "numbered notation text",
        },
    }


def parse_song_material(filename: str, data: bytes | None = None, *, text_hint: str = "") -> dict[str, Any]:
    """Extract a conservative song-material summary for lesson-to-game anchoring."""

    data = data or b""
    suffix = Path(filename or "").suffix.lower()
    text_hint = text_hint.strip()
    if suffix in MIDI_EXTENSIONS and data:
        return _parse_midi_material(filename, data)
    if suffix in MUSICXML_EXTENSIONS and data:
        return _parse_musicxml_material(filename, data)
    if suffix in TEXT_EXTENSIONS and data:
        return _parse_text_material(filename, _decode_text(data))
    if suffix == ".pdf" and data:
        return _parse_score_image_or_pdf_material(filename, data, text_hint=text_hint)
    if suffix in SCORE_IMAGE_EXTENSIONS and data:
        return _parse_score_image_or_pdf_material(filename, data, text_hint=text_hint)
    if text_hint:
        return _parse_text_material(filename or "song-material.txt", text_hint)
    if suffix in AUDIO_EXTENSIONS and data:
        return _metadata_only(filename, "audio_reference", "metadata_only", True, "音频可作为歌曲依据，但需要谱面或文字旋律来精确生成游戏。")
    return {}


def build_song_anchor_contract(
    song_material: dict[str, Any],
    *,
    lesson_context: dict[str, Any] | None = None,
    extra_need: str = "",
) -> dict[str, Any]:
    if not song_material:
        return {}
    lesson_context = lesson_context or {}
    phrases = [item for item in song_material.get("phrases", []) if isinstance(item, dict)]
    selected_phrase = _select_phrase(phrases, lesson_context, extra_need)
    must_anchor_to_song = bool(selected_phrase)
    allowed_templates = [
        "phrase_rebuild_singing",
        "segment_ordering_studio",
        "rhythm_rebuild_challenge",
        "pitch_ladder_game",
        "constrained_composition_lab",
    ]
    material_title = _clean_song_title(song_material.get("song_title"))
    lesson_title = _clean_song_title(lesson_context.get("song_name"))
    return {
        "version": "song_anchor_contract_v1",
        "song_title": material_title or lesson_title or "当前歌曲",
        "must_anchor_to_song": must_anchor_to_song,
        "source": song_material.get("source", {}),
        "required_fragment_source": "song_material.phrases",
        "available_phrase_ids": [phrase.get("id", "") for phrase in phrases if phrase.get("id")],
        "selected_phrase_id": selected_phrase.get("id", ""),
        "selected_phrase": selected_phrase,
        "allowed_game_templates": allowed_templates,
        "requires_manual_confirmation": bool(song_material.get("source", {}).get("requires_manual_confirmation")),
        "non_negotiables": (
            [
                "学唱、演唱、歌曲表现类游戏必须使用 song_material.phrases 中的真实乐句或目标序列。",
                "不能用通用节奏、通用音高方向或模板材料替代当前歌曲片段。",
                "页面显示、播放、判定和通关答案必须来自同一个歌曲片段数据表。",
                "每关通关后必须回到听唱、跟唱、模唱或歌曲表现，不能只停留在拖拽。",
            ]
            if must_anchor_to_song
            else [
                "当前没有锁定具体歌曲片段，可先生成通用音乐概念游戏；如后续上传音频或乐谱，再切换到歌曲锚定模式。",
            ]
        ),
    }


def attach_song_anchor_to_lesson_analysis(
    lesson_analysis: dict[str, Any],
    song_material: dict[str, Any],
    *,
    extra_need: str = "",
) -> dict[str, Any]:
    if not song_material:
        return lesson_analysis
    enriched = dict(lesson_analysis)
    lesson_context = dict(enriched.get("lesson_context") or {})
    phrases = [item for item in song_material.get("phrases", []) if isinstance(item, dict)]
    material_title = _clean_song_title(song_material.get("song_title"))
    if material_title:
        enriched["song_name"] = material_title
        lesson_context["song_name"] = material_title
    contract = build_song_anchor_contract(song_material, lesson_context=lesson_context, extra_need=extra_need)
    selected_phrase = contract.get("selected_phrase", {})
    recommended = dict(enriched.get("recommended_game") or {})
    if selected_phrase:
        recommended["uses_song_material"] = True
        recommended["song_anchor_phrase"] = selected_phrase
        if _is_singing_context(enriched, lesson_context, extra_need):
            recommended.setdefault("name", "歌曲乐句闯关")
            recommended["type"] = "phrase_rebuild_singing"
            recommended["mechanic"] = "用歌曲真实乐句做听辨、排序、跟唱和表现闯关。"
            recommended["music_element"] = lesson_context.get("target_music_element") or "歌曲乐句"
    lesson_context["song_material"] = song_material
    lesson_context["song_anchor_contract"] = contract
    lesson_context["song_anchor_phrase"] = selected_phrase
    lesson_context["song_material_summary"] = {
        "enabled": True,
        "song_title": contract.get("song_title", ""),
        "source_kind": song_material.get("source", {}).get("kind", ""),
        "source_filename": song_material.get("source", {}).get("filename", ""),
        "analysis_quality": song_material.get("source", {}).get("analysis_quality", ""),
        "phrase_count": len(phrases),
        "has_audio": bool(song_material.get("source", {}).get("source_audio_url")),
        "requires_manual_confirmation": bool(song_material.get("source", {}).get("requires_manual_confirmation")),
        "score_review_status": (song_material.get("score_review") or song_material.get("source", {}).get("score_review") or {}).get("status", ""),
        "used_for_generation": True,
    }
    lesson_context["decision_trace"] = [
        *lesson_context.get("decision_trace", []),
        f"已接入歌曲材料：{contract.get('song_title', '当前歌曲')}，优先使用 {selected_phrase.get('label', '真实乐句')} 生成游戏。",
    ]
    enriched["recommended_game"] = recommended
    enriched["lesson_context"] = lesson_context
    enriched["song_material"] = song_material
    enriched["song_anchor_contract"] = contract
    enriched["song_material_summary"] = lesson_context["song_material_summary"]
    return enriched


def validate_song_anchor_contract(contract: dict[str, Any]) -> list[str]:
    if not contract:
        return []
    errors: list[str] = []
    must_anchor_to_song = bool(contract.get("must_anchor_to_song"))
    selected = contract.get("selected_phrase", {}) if isinstance(contract.get("selected_phrase"), dict) else {}
    if must_anchor_to_song and not selected:
        errors.append("缺少选中的歌曲片段。")
    if must_anchor_to_song and selected and not selected.get("target_sequence"):
        errors.append("选中歌曲片段缺少目标音序或节奏序列。")
    source = contract.get("source", {}) if isinstance(contract.get("source"), dict) else {}
    if must_anchor_to_song and source.get("analysis_quality") == "metadata_only":
        errors.append("歌曲材料只有元数据，无法精确生成与判定音乐游戏。")
    elif not must_anchor_to_song and source.get("analysis_quality") == "metadata_only":
        errors.append("歌曲材料只有元数据，当前将退回非歌曲锚定模式生成。")
    return errors


def _parse_midi_material(filename: str, data: bytes) -> dict[str, Any]:
    try:
        import pretty_midi
    except ImportError:
        return _metadata_only(filename, "midi", "metadata_only", True, "当前环境缺少 MIDI 解析库，需要教师确认歌曲片段。")
    with tempfile.NamedTemporaryFile(suffix=Path(filename).suffix or ".mid", delete=True) as temp:
        temp.write(data)
        temp.flush()
        midi_data = pretty_midi.PrettyMIDI(temp.name)
    notes = []
    for instrument in midi_data.instruments:
        if instrument.is_drum:
            continue
        for note in instrument.notes:
            notes.append(
                {
                    "pitch": note.pitch,
                    "start": round(note.start, 4),
                    "duration": round(max(0.08, note.end - note.start), 4),
                    "velocity": note.velocity,
                }
            )
    notes = sorted(notes, key=lambda item: (item["start"], item["pitch"]))[:96]
    duration = max((note["start"] + note["duration"] for note in notes), default=0)
    note_events = {"notes": notes, "duration": round(duration, 4)}
    notes = note_events.get("notes", [])
    phrases = _phrases_from_note_events(notes)
    return _material(
        filename,
        kind="midi",
        quality="high" if phrases else "low",
        requires_confirmation=not bool(phrases),
        phrases=phrases,
        extra={"duration": note_events.get("duration", 0), "note_count": len(notes)},
    )


def _parse_musicxml_material(filename: str, data: bytes) -> dict[str, Any]:
    text = _decode_musicxml_payload(filename, data)
    root = ET.fromstring(text)
    divisions = _first_int(root, ".//{*}divisions", 1) or 1
    key_fifths = _first_int(root, ".//{*}fifths", 0)
    beats = _first_text(root, ".//{*}beats") or ""
    beat_type = _first_text(root, ".//{*}beat-type") or ""
    notes: list[dict[str, Any]] = []
    current_time = 0.0
    for note_el in root.findall(".//{*}note"):
        duration = (_first_int(note_el, "{*}duration", divisions) or divisions) / max(divisions, 1)
        is_rest = note_el.find("{*}rest") is not None
        if is_rest:
            notes.append(_note_token("rest", "休止", 0, current_time, duration, rest=True))
        else:
            step = _first_text(note_el, "{*}pitch/{*}step") or "C"
            alter = _first_int(note_el, "{*}pitch/{*}alter", 0) or 0
            octave = _first_int(note_el, "{*}pitch/{*}octave", 4) or 4
            pitch = _musicxml_pitch(step, alter, octave)
            label = _pitch_label(pitch)
            notes.append(_note_token(_token_id(label, len(notes) + 1), label, pitch, current_time, duration))
        current_time += max(duration, 0.25)
    phrases = _phrases_from_note_tokens(notes)
    return _material(
        filename,
        kind="musicxml",
        quality="high" if phrases else "low",
        requires_confirmation=not bool(phrases),
        phrases=phrases,
        extra={"key_fifths": key_fifths, "meter": f"{beats}/{beat_type}" if beats and beat_type else ""},
    )


def _parse_score_image_or_pdf_material(filename: str, data: bytes, *, text_hint: str = "") -> dict[str, Any]:
    suffix = Path(filename or "").suffix.lower()
    if text_hint.strip():
        hinted = _parse_text_material(filename or "score-hint.txt", text_hint)
        if hinted.get("phrases"):
            source = hinted.setdefault("source", {})
            source["kind"] = "teacher_confirmed_score_hint"
            source["filename"] = filename
            source["analysis_quality"] = "medium"
            source["requires_manual_confirmation"] = False
            return _attach_score_review(
                hinted,
                _build_score_review(
                    filename,
                    "teacher_confirmed_score_hint",
                    [],
                    material=hinted,
                    recognized_text=text_hint,
                    status="confirmed",
                    message="已使用老师确认的文字谱作为歌曲材料。",
                    manual_text_required=False,
                ),
            )

    attempts: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="score_omr_") as temp_dir:
        workspace = Path(temp_dir)
        input_path = workspace / Path(filename or f"score{suffix or '.png'}").name
        input_path.write_bytes(data)

        vision_llm_result = _try_multimodal_score_parser(input_path, workspace)
        attempts.append(vision_llm_result["attempt"])
        if vision_llm_result.get("material", {}).get("phrases"):
            material = vision_llm_result["material"]
            return _attach_score_review(
                material,
                _build_score_review(
                    filename,
                    material.get("source", {}).get("kind", "multimodal_llm_score"),
                    attempts,
                    material=material,
                    recognized_text=vision_llm_result["attempt"].get("recognized_text", ""),
                    status="needs_confirmation",
                    message="已通过 ecnu-max 视觉解析出乐谱片段，建议老师在生成前快速核对一次。",
                    manual_text_required=False,
                ),
            )

    kind = "pdf_score" if suffix == ".pdf" else "score_image"
    note = (
        "已尝试 ecnu-max 视觉解析，但没有提取出可靠音符表。"
        "请补充文字谱、MIDI、MusicXML，或在“歌曲材料说明”里直接写核心乐句。"
    )
    material = _metadata_only(
        filename,
        kind,
        "metadata_only",
        True,
        note,
        extra={"omr_attempts": attempts},
    )
    return _attach_score_review(
        material,
        _build_score_review(
            filename,
            kind,
            attempts,
            material=material,
            status="failed",
            message="谱面图片/PDF 没有识别出可靠旋律。请检查识别文字，或补充文字谱后重新分析。",
            manual_text_required=True,
        ),
    )


def _try_multimodal_score_parser(input_path: Path, workspace: Path) -> dict[str, Any]:
    attempt = {
        "engine": "multimodal_llm_score_parser",
        "available": False,
        "status": "skipped",
    }
    llm_config = llm_runtime_config()
    if not llm_config["enabled"]:
        attempt["message"] = "未配置可用的大模型视觉解析服务。"
        return {"attempt": attempt}

    image_groups = _score_image_page_candidates(input_path, workspace)
    images = [group[0] for group in image_groups[:3] if group]
    if not images:
        attempt["message"] = "没有可发送给大模型的谱面图片。"
        return {"attempt": attempt}

    attempt["available"] = True
    try:
        payload = _call_multimodal_score_model(images, llm_config)
    except Exception as exc:
        attempt["status"] = "failed"
        attempt["message"] = f"大模型视觉解析失败：{exc}"
        return {"attempt": attempt}

    material = _material_from_multimodal_payload(input_path.name, payload)
    recognized_text = _multimodal_payload_to_text(payload)
    attempt["recognized_text"] = recognized_text[:SCORE_REVIEW_TEXT_LIMIT]
    attempt["ocr_text_preview"] = recognized_text[:240]
    phrase_count = len(material.get("phrases", [])) if isinstance(material.get("phrases"), list) else 0
    attempt["status"] = "parsed" if phrase_count else "empty"
    if phrase_count:
        attempt["message"] = "大模型已解析出可用乐句。"
        return {"attempt": attempt, "material": material}
    attempt["message"] = "大模型没有返回足够可靠的乐句结构。"
    return {"attempt": attempt}


def _call_multimodal_score_model(images: list[Path], llm_config: dict[str, Any]) -> dict[str, Any]:
    if llm_config.get("provider") == "chat_ecnu":
        return _call_chat_ecnu_multimodal_score_model(images, llm_config)

    from openai import OpenAI

    client = OpenAI(api_key=llm_config["api_key"], base_url=llm_config["base_url"])
    score_model = _score_vision_model_name()
    content = _multimodal_score_prompt_content(images)

    response = client.chat.completions.create(
        model=score_model,
        messages=[
            {"role": "system", "content": "你必须只返回 JSON，不要解释。"},
            {"role": "user", "content": content},
        ],
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content or "{}"
    return json.loads(raw)


def _call_chat_ecnu_multimodal_score_model(images: list[Path], llm_config: dict[str, Any]) -> dict[str, Any]:
    score_model = _score_vision_model_name()
    payload = {
        "messages": [
            {"role": "system", "content": "你必须只返回 JSON，不要解释。"},
            {"role": "user", "content": _multimodal_score_prompt_content(images)},
        ],
        "stream": False,
        "model": score_model,
    }
    first_payload = _post_chat_ecnu_multimodal_payload(payload, llm_config)
    if _material_from_multimodal_payload(images[0].name, first_payload).get("phrases"):
        return first_payload

    fallback_model = normalize_chat_ecnu_model_name(str(llm_config.get("model") or ""))
    if fallback_model and fallback_model != score_model:
        fallback_payload = dict(payload)
        fallback_payload["model"] = fallback_model
        try:
            second_payload = _post_chat_ecnu_multimodal_payload(fallback_payload, llm_config)
        except Exception:
            return first_payload
        if _material_from_multimodal_payload(images[0].name, second_payload).get("phrases"):
            return second_payload
    return first_payload


def _post_chat_ecnu_multimodal_payload(payload: dict[str, Any], llm_config: dict[str, Any]) -> dict[str, Any]:
    request = urllib.request.Request(
        llm_config["chat_completions_url"],
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {llm_config['api_key']}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=40) as response:
            raw = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"ChatECNU 视觉识谱调用失败：HTTP {exc.code} {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"ChatECNU 视觉识谱连接失败：{exc.reason}") from exc
    response_payload = json.loads(raw)
    return _json_from_chat_completion_payload(response_payload)


def _multimodal_score_prompt_content(images: list[Path]) -> list[dict[str, Any]]:
    content: list[dict[str, Any]] = [
        {
            "type": "text",
            "text": (
                "你是音乐乐谱解析助手。请识别图片/PDF里的歌曲标题、调号、拍号、速度、歌词和1到4个核心乐句，"
                "只返回 JSON 对象，不要解释，不确定就留空，不要编造。"
                "字段：song_title, key_signature, time_signature, tempo_text, lyrics, phrases。"
                "phrases 每项包含 phrase_label, notation, melody_outline, rhythm_hint, lyrics, confidence。"
                "notation 优先用简谱数字、休止0，或 do re mi fa sol la ti。"
            ),
        }
    ]
    for image_path in images:
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": _path_to_data_url(image_path)},
            }
        )
    return content


def _json_from_chat_completion_payload(payload: dict[str, Any]) -> dict[str, Any]:
    choices = payload.get("choices")
    if isinstance(choices, list) and choices:
        first = choices[0]
        if isinstance(first, dict):
            message = first.get("message")
            if isinstance(message, dict) and message.get("content") is not None:
                return _json_from_text(str(message.get("content") or "{}"))
            if first.get("text") is not None:
                return _json_from_text(str(first.get("text") or "{}"))
    data = payload.get("data")
    if isinstance(data, dict):
        return _json_from_chat_completion_payload(data)
    if payload.get("content") is not None:
        return _json_from_text(str(payload.get("content") or "{}"))
    raise ValueError("ChatECNU response does not contain assistant content")


def _json_from_text(text: str) -> dict[str, Any]:
    candidate = str(text or "").strip()
    if not candidate:
        return {}
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", candidate, re.S)
    if fenced:
        return json.loads(fenced.group(1))
    start = candidate.find("{")
    end = candidate.rfind("}")
    if start >= 0 and end > start:
        return json.loads(candidate[start : end + 1])
    raise ValueError("ChatECNU response content is not valid JSON")


def _path_to_data_url(path: Path) -> str:
    suffix = path.suffix.lower()
    mime = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }.get(suffix, "image/png")
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def _material_from_multimodal_payload(filename: str, payload: dict[str, Any]) -> dict[str, Any]:
    song_title = _clean_song_title(payload.get("song_title")) or _title_from_filename(filename) or "当前歌曲"
    key_signature = str(payload.get("key_signature") or "").strip()
    time_signature = str(payload.get("time_signature") or "").strip()
    tempo_text = str(payload.get("tempo_text") or "").strip()
    visible_text = _multimodal_visible_text(payload)
    payload_lyrics = payload.get("lyrics", []) if isinstance(payload.get("lyrics"), list) else []
    recognized_lyrics = [str(item or "").strip() for item in payload_lyrics if str(item or "").strip()][:8]
    phrases_payload = payload.get("phrases", []) if isinstance(payload.get("phrases"), list) else []
    phrases: list[dict[str, Any]] = _phrases_from_multimodal_visible_text(visible_text)
    seen_phrase_notation = {str(phrase.get("source_text") or "").strip() for phrase in phrases}
    phrase_summaries: list[dict[str, Any]] = []
    for index, item in enumerate(phrases_payload[:8], start=1):
        if not isinstance(item, dict):
            continue
        label = str(item.get("phrase_label") or f"第{index}乐句").strip() or f"第{index}乐句"
        notation = str(item.get("notation") or "").strip()
        melody_outline = str(item.get("melody_outline") or "").strip()
        rhythm_hint = str(item.get("rhythm_hint") or "").strip()
        phrase_lyrics = str(item.get("lyrics") or "").strip()
        confidence = str(item.get("confidence") or "").strip()
        inferred_notation = _notation_from_multimodal_phrase_fields(
            label=label,
            notation=notation,
            melody_outline=melody_outline,
            rhythm_hint=rhythm_hint,
            phrase_lyrics=phrase_lyrics,
        )
        phrase_summary = _drop_empty_fields(
            {
                "label": label,
                "notation": notation or inferred_notation,
                "melody_outline": melody_outline,
                "rhythm_hint": rhythm_hint,
                "lyrics": phrase_lyrics,
                "confidence": confidence,
            }
        )
        if phrase_summary:
            phrase_summaries.append(phrase_summary)
        tokens = _tokens_from_text(notation) if notation else []
        if not tokens and melody_outline:
            tokens = _tokens_from_text(melody_outline)
        if not tokens and inferred_notation:
            tokens = _tokens_from_text(inferred_notation)
        if tokens:
            phrase_source_text = notation or melody_outline or inferred_notation
            if phrase_source_text.strip() in seen_phrase_notation:
                continue
            phrase = _phrase_from_tokens(f"phrase_{len(phrases) + 1}", label, tokens, notation or melody_outline or inferred_notation)
            if phrase_lyrics:
                phrase["lyrics"] = phrase_lyrics
            if rhythm_hint:
                phrase["rhythm_hint"] = rhythm_hint
            if confidence:
                phrase["confidence"] = confidence
            phrases.append(phrase)
            seen_phrase_notation.add(phrase_source_text.strip())
            continue
        if phrase_lyrics and phrase_lyrics not in recognized_lyrics:
            recognized_lyrics.append(phrase_lyrics)
    partial_recognition = bool(key_signature or time_signature or tempo_text or recognized_lyrics or phrase_summaries)
    return _material(
        filename,
        kind="multimodal_llm_score",
        quality="medium" if phrases or partial_recognition else "low",
        requires_confirmation=True if phrases or partial_recognition else True,
        phrases=phrases,
        title=song_title,
        extra={
            "llm_multimodal": True,
            "key": key_signature,
            "meter": time_signature,
            "tempo": tempo_text,
            "recognized_lyrics": recognized_lyrics,
            "recognized_phrases": phrase_summaries,
            "partial_recognition": partial_recognition,
        },
    )


def _multimodal_visible_text(payload: dict[str, Any]) -> str:
    fields = [
        payload.get("visible_text"),
        payload.get("recognized_text"),
        payload.get("ocr_text"),
        payload.get("text"),
    ]
    lines: list[str] = []
    for value in fields:
        if isinstance(value, str) and value.strip():
            lines.append(value.strip())
        elif isinstance(value, list):
            lines.extend(str(item).strip() for item in value if str(item).strip())
    return "\n".join(lines)


def _phrases_from_multimodal_visible_text(text: str) -> list[dict[str, Any]]:
    phrases: list[dict[str, Any]] = []
    for label, notation in _phrase_notation_pairs_from_text(text):
        tokens = _tokens_from_text(notation)
        if len(tokens) < 2:
            continue
        phrases.append(_phrase_from_tokens(f"phrase_{len(phrases) + 1}", label, tokens, notation))
        if len(phrases) >= 8:
            break
    return phrases


def _phrase_notation_pairs_from_text(text: str) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for raw_line in str(text or "").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        label_match = re.search(r"((?:第\s*)?[一二三四五六七八九十\d]+\s*(?:乐句|句|段)|phrase\s*\d+)", line, re.I)
        if not label_match:
            continue
        notation = _notation_text_from_line(line)
        if not notation:
            continue
        label = label_match.group(1).strip()
        pairs.append((label, notation))
    if pairs:
        return pairs[:8]
    notation_lines = [line.strip() for line in str(text or "").splitlines() if _looks_like_notation_line(line)]
    return [(f"第{index}乐句", _notation_text_from_line(line) or line) for index, line in enumerate(notation_lines[:8], start=1)]


def _notation_from_multimodal_phrase_fields(
    *,
    label: str,
    notation: str,
    melody_outline: str,
    rhythm_hint: str,
    phrase_lyrics: str,
) -> str:
    for value in [notation, melody_outline, rhythm_hint, phrase_lyrics, label]:
        candidate = _notation_text_from_line(str(value or ""))
        if candidate:
            return candidate
    return ""


def _notation_text_from_line(line: str) -> str:
    text = str(line or "").strip()
    if not text:
        return ""
    compact_match = re.search(r"(?<!\d)([1-7](?:\s*[1-7]){2,})(?!\d)", text)
    if compact_match:
        compact = re.sub(r"\s+", "", compact_match.group(1))
        return " ".join(compact)
    allowed = re.sub(r"(?i)\b(do|re|mi|fa|sol|so|la|si|ti)\b|[0-7]|休止|宫|商|角|徵|徴|羽", lambda match: f" {match.group(0)} ", text)
    tokens = re.findall(r"(?i)\bdo\b|\bre\b|\bmi\b|\bfa\b|\bsol\b|\bso\b|\bla\b|\bsi\b|\bti\b|[0-7]|休止|宫|商|角|徵|徴|羽", allowed)
    if len(tokens) < 3:
        return ""
    return " ".join(tokens)


def _multimodal_payload_to_text(payload: dict[str, Any]) -> str:
    if not isinstance(payload, dict):
        return ""
    lines: list[str] = []
    title = str(payload.get("song_title") or "").strip()
    if title:
        lines.append(f"歌名：{title}")
    key_signature = str(payload.get("key_signature") or "").strip()
    if key_signature:
        lines.append(f"调号：{key_signature}")
    time_signature = str(payload.get("time_signature") or "").strip()
    if time_signature:
        lines.append(f"拍号：{time_signature}")
    tempo_text = str(payload.get("tempo_text") or "").strip()
    if tempo_text:
        lines.append(f"速度：{tempo_text}")
    lyrics = payload.get("lyrics", []) if isinstance(payload.get("lyrics"), list) else []
    if lyrics:
        cleaned_lyrics = [str(item or "").strip() for item in lyrics if str(item or "").strip()]
        if cleaned_lyrics:
            lines.append(f"歌词：{' / '.join(cleaned_lyrics[:4])}")
    phrases = payload.get("phrases", []) if isinstance(payload.get("phrases"), list) else []
    for index, item in enumerate(phrases[:8], start=1):
        if not isinstance(item, dict):
            continue
        label = str(item.get("phrase_label") or f"第{index}乐句").strip() or f"第{index}乐句"
        notation = str(item.get("notation") or "").strip()
        if notation:
            lines.append(f"{label}：{notation}")
            continue
        melody_outline = str(item.get("melody_outline") or "").strip()
        rhythm_hint = str(item.get("rhythm_hint") or "").strip()
        summary_parts = [part for part in [melody_outline, rhythm_hint] if part]
        if summary_parts:
            lines.append(f"{label}：{'；'.join(summary_parts)}")
    return "\n".join(lines)


def _parse_text_material(filename: str, text: str) -> dict[str, Any]:
    title = _extract_title(text) or _title_from_filename(filename) or "当前歌曲"
    meter = _extract_by_label(text, ["拍号", "节拍"])
    key = _extract_by_label(text, ["调性", "调号"])
    tempo = _extract_by_label(text, ["速度", "BPM", "bpm"])
    phrase_lines = _extract_phrase_lines(text)
    if not phrase_lines:
        if _looks_like_compact_notation_text(text):
            notation_lines = [line.strip() for line in text.splitlines() if _looks_like_notation_line(line)]
            if len(notation_lines) >= 2:
                phrase_lines = [
                    (f"line_{index}", f"第{index}乐句", line)
                    for index, line in enumerate(notation_lines[:8], start=1)
                ]
            else:
                phrase_lines = [("phrase_1", "歌曲片段", text)]
        else:
            return _metadata_only(
                filename or "song-material.txt",
                "text_score",
                "low",
                True,
                "文本里没有可靠的乐句、简谱或唱名序列，不能直接作为游戏播放和判定材料。",
                extra={"meter": meter, "key": key, "tempo": tempo, "song_title": title},
            )
    phrases = []
    for _index, (_raw_id, label, phrase_text) in enumerate(phrase_lines[:8], start=1):
        tokens = _tokens_from_text(phrase_text)
        if tokens:
            phrase_index = len(phrases) + 1
            phrases.append(_phrase_from_tokens(f"phrase_{phrase_index}", label or f"第{phrase_index}乐句", tokens, phrase_text))
    return _material(
        filename or "song-material.txt",
        kind="text_score",
        quality="medium" if phrases else "low",
        requires_confirmation=not bool(phrases),
        phrases=phrases,
        title=title,
        extra={"meter": meter, "key": key, "tempo": tempo},
    )


def _looks_like_compact_notation_text(text: str) -> bool:
    lines = [line.strip() for line in str(text or "").splitlines() if line.strip()]
    if not lines:
        return False
    return any(_looks_like_notation_line(line) for line in lines[:12])


def _looks_like_notation_line(line: str) -> bool:
    text = str(line or "").strip()
    if not text or len(text) > 120:
        return False
    prose_markers = [
        "你能",
        "是否",
        "怎样",
        "什么",
        "目标",
        "重点",
        "难点",
        "环节",
        "活动",
        "教学",
        "感知",
        "认识",
        "区别",
        "找到",
        "演唱",
        "表现",
        "问题",
        "吗",
        "？",
        "?",
    ]
    if any(marker in text for marker in prose_markers):
        return False
    solfege_tokens = re.findall(r"(?i)\bdo\b|\bre\b|\bmi\b|\bfa\b|\bsol\b|\bla\b|\bsi\b|\bti\b", text)
    digit_tokens = re.findall(r"[1-7]", text)
    rest_tokens = re.findall(r"0|休止", text)
    has_digit_run = bool(re.search(r"[1-7][0-7\s,，、;；/\-.]{3,}[0-7]", text))
    has_solfege_run = len(solfege_tokens) >= 3
    notation_count = len(solfege_tokens) + len(digit_tokens) + len(rest_tokens)
    if notation_count < 3 and not has_digit_run:
        return False
    residue = re.sub(
        r"(?i)\bdo\b|\bre\b|\bmi\b|\bfa\b|\bsol\b|\bla\b|\bsi\b|\bti\b|[0-7]|休止|小节|拍|第|一|二|三|四|五|六|七|八|九|十|句|乐句|[:：,，、;；/\-\.\s]",
        "",
        text,
    )
    return (has_digit_run or has_solfege_run or notation_count >= 4) and len(residue) <= 8


def _metadata_only(
    filename: str,
    kind: str,
    quality: str,
    requires_confirmation: bool,
    note: str,
    *,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _material(
        filename,
        kind=kind,
        quality=quality,
        requires_confirmation=requires_confirmation,
        phrases=[],
        extra={"note": note, **(extra or {})},
    )


def _material(
    filename: str,
    *,
    kind: str,
    quality: str,
    requires_confirmation: bool,
    phrases: list[dict[str, Any]],
    title: str = "",
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    extra = extra or {}
    resolved_title = _clean_song_title(title) or _title_from_filename(filename) or "当前歌曲"
    return {
        "version": "song_material_v1",
        "source": {
            "filename": filename,
            "kind": kind,
            "analysis_quality": quality,
            "requires_manual_confirmation": requires_confirmation,
            **{key: value for key, value in extra.items() if value not in ("", None, [])},
        },
        "song_title": resolved_title,
        "meter": extra.get("meter", ""),
        "key": extra.get("key", ""),
        "tempo_bpm": extra.get("tempo", ""),
        "lyrics": extra.get("recognized_lyrics", []),
        "recognized_phrases": extra.get("recognized_phrases", []),
        "phrases": phrases,
        "teaching_game_points": _teaching_points_from_phrases(phrases),
    }


def _attach_score_review(material: dict[str, Any], review: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(material, dict):
        return material
    if review:
        material["score_review"] = review
        source = material.setdefault("source", {})
        if isinstance(source, dict):
            source["score_review"] = review
    return material


def _build_score_review(
    filename: str,
    kind: str,
    attempts: list[dict[str, Any]],
    *,
    material: dict[str, Any] | None = None,
    recognized_text: str = "",
    status: str = "",
    message: str = "",
    manual_text_required: bool = False,
) -> dict[str, Any]:
    material = material or {}
    source = material.get("source", {}) if isinstance(material.get("source"), dict) else {}
    phrases = material.get("phrases", []) if isinstance(material.get("phrases"), list) else []
    recognized_phrases = material.get("recognized_phrases", []) if isinstance(material.get("recognized_phrases"), list) else []
    lyrics = material.get("lyrics", []) if isinstance(material.get("lyrics"), list) else []
    has_partial_recognition = bool(
        source.get("partial_recognition")
        or material.get("key")
        or material.get("meter")
        or material.get("tempo_bpm")
        or lyrics
        or recognized_phrases
    )
    recognized_text = (recognized_text or _recognized_text_from_attempts(attempts)).strip()
    suggested_text = _material_to_text_hint(material)
    if not status:
        if phrases:
            status = "needs_confirmation" if source.get("requires_manual_confirmation") else "parsed"
        elif has_partial_recognition:
            status = "needs_confirmation"
        else:
            status = "failed"
    return {
        "enabled": True,
        "version": "score_review_v1",
        "source_filename": filename,
        "source_kind": kind,
        "status": status,
        "message": message or _score_review_message(status),
        "manual_text_required": bool(manual_text_required),
        "requires_manual_confirmation": bool(source.get("requires_manual_confirmation")) or status in {"needs_confirmation", "failed"},
        "recognized_text": recognized_text[:SCORE_REVIEW_TEXT_LIMIT],
        "recognized_text_preview": recognized_text[:360],
        "suggested_text_hint": suggested_text[:SCORE_REVIEW_TEXT_LIMIT],
        "phrase_count": len(phrases),
        "recognized_phrase_count": len(recognized_phrases),
        "lyrics_count": len([item for item in lyrics if str(item or "").strip()]),
        "key_signature": material.get("key", ""),
        "time_signature": material.get("meter", ""),
        "tempo_text": material.get("tempo_bpm", ""),
        "attempts": _public_omr_attempts(attempts),
    }


def _score_review_message(status: str) -> str:
    if status == "confirmed":
        return "已使用老师确认的文字谱。"
    if status == "parsed":
        return "已识别出可用于播放和判定的乐谱数据。"
    if status == "needs_confirmation":
        return "已识别出部分乐谱信息，建议老师确认后再生成。"
    return "没有识别出可靠乐谱数据，请补充或修正文字谱。"


def _recognized_text_from_attempts(attempts: list[dict[str, Any]]) -> str:
    for attempt in reversed(attempts or []):
        if not isinstance(attempt, dict):
            continue
        text = str(attempt.get("recognized_text") or attempt.get("ocr_text_preview") or "").strip()
        if text:
            return text
    return ""


def _public_omr_attempts(attempts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    public: list[dict[str, Any]] = []
    for attempt in attempts or []:
        if not isinstance(attempt, dict):
            continue
        public.append(
            {
                "engine": attempt.get("engine", ""),
                "available": bool(attempt.get("available")),
                "status": attempt.get("status", ""),
                "message": attempt.get("message", ""),
                "confidence": attempt.get("ocr_confidence_score", ""),
                "preview": str(attempt.get("recognized_text") or attempt.get("ocr_text_preview") or "")[:180],
            }
        )
    return public


def _material_to_text_hint(material: dict[str, Any]) -> str:
    lines: list[str] = []
    if material.get("song_title"):
        lines.append(f"歌名：{material.get('song_title')}")
    if material.get("key"):
        lines.append(f"调号：{material.get('key')}")
    if material.get("meter"):
        lines.append(f"拍号：{material.get('meter')}")
    if material.get("tempo_bpm"):
        lines.append(f"速度：{material.get('tempo_bpm')}")
    lyrics = material.get("lyrics", []) if isinstance(material.get("lyrics"), list) else []
    if lyrics:
        lines.append(f"歌词：{' / '.join(str(item).strip() for item in lyrics[:4] if str(item).strip())}")
    phrases = material.get("phrases", []) if isinstance(material.get("phrases"), list) else []
    for index, phrase in enumerate(phrases[:8], start=1):
        if not isinstance(phrase, dict):
            continue
        label = phrase.get("label") or f"第{index}乐句"
        source_text = str(phrase.get("source_text") or "").strip()
        if source_text:
            lines.append(f"{label}：{source_text}")
            continue
        tokens = phrase.get("playback_tokens") or phrase.get("main_melody") or []
        token_text = " ".join(str(item.get("label", "")) for item in tokens if isinstance(item, dict) and item.get("label"))
        if token_text:
            lines.append(f"{label}：{token_text}")
    if not phrases:
        recognized_phrases = material.get("recognized_phrases", []) if isinstance(material.get("recognized_phrases"), list) else []
        for index, phrase in enumerate(recognized_phrases[:6], start=1):
            if not isinstance(phrase, dict):
                continue
            label = phrase.get("label") or f"第{index}乐句"
            summary = "；".join(
                str(part).strip()
                for part in [phrase.get("notation", ""), phrase.get("melody_outline", ""), phrase.get("rhythm_hint", ""), phrase.get("lyrics", "")]
                if str(part).strip()
            )
            if summary:
                lines.append(f"{label}：{summary}")
    return "\n".join(lines)


def _drop_empty_fields(payload: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if value not in ("", None, [], {})}


def _phrases_from_note_events(notes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    tokens = []
    for index, note in enumerate(notes[:24], start=1):
        pitch = int(note.get("pitch", 60))
        duration = float(note.get("duration", 0.5))
        label = _pitch_label(pitch)
        tokens.append(
            {
                "id": f"n{index}",
                "label": label,
                "music_value": f"{label} 音",
                "pitch": pitch,
                "start": round(float(note.get("start", 0.0) or 0.0), 3),
                "duration": round(max(duration, 0.12), 3),
                "velocity": int(note.get("velocity", 86) or 86),
                "rest": False,
                "feedback": f"这是歌曲片段中的“{label}”。",
            }
        )
    return _phrases_from_note_tokens(tokens)


def _phrases_from_note_tokens(tokens: list[dict[str, Any]]) -> list[dict[str, Any]]:
    tokens = [item for item in tokens[:32] if isinstance(item, dict)]
    if len(tokens) < 2:
        return []

    chunks = _split_phrase_chunks(tokens)
    phrases = []
    for chunk in chunks:
        if len(chunk) < 2:
            continue
        phrase_id = f"phrase_{len(phrases) + 1}"
        start = float(chunk[0].get("start", 0.0) or 0.0)
        end = float(chunk[-1].get("start", 0.0) or 0.0) + float(chunk[-1].get("duration", 0.5) or 0.5)
        phrases.append(
            {
                "id": phrase_id,
                "label": f"第{len(phrases) + 1}乐句",
                "measure_range": f"{round(start, 2)}-{round(end, 2)}",
                "target_sequence": [item["id"] for item in chunk],
                "main_melody": chunk,
                "playback_tokens": chunk,
                "rhythm_features": _rhythm_features(chunk),
                "singing_difficulty": _singing_difficulty(chunk),
            }
        )
    return phrases


def _split_phrase_chunks(tokens: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    chunks: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = []
    limit = min(len(tokens), 32)
    source = tokens[:limit]

    for index, token in enumerate(source):
        current.append(token)
        next_token = source[index + 1] if index + 1 < len(source) else None
        if not next_token:
            break

        duration = float(token.get("duration", 0.5) or 0.5)
        next_start = float(next_token.get("start", 0.0) or 0.0)
        current_end = float(token.get("start", 0.0) or 0.0) + duration
        gap = max(0.0, next_start - current_end)
        current_len = len(current)

        break_after = False
        if bool(token.get("rest")) and current_len >= 2:
            break_after = True
        elif gap >= max(0.35, duration * 0.8):
            break_after = True
        elif duration >= 0.95 and current_len >= 4:
            break_after = True
        elif current_len >= 8 and gap >= 0.15:
            break_after = True
        elif current_len >= 10:
            break_after = True

        if break_after:
            chunks.append(current)
            current = []

    if current:
        chunks.append(current)

    merged: list[list[dict[str, Any]]] = []
    for chunk in chunks:
        if merged and len(chunk) < 2:
            merged[-1].extend(chunk)
            continue
        merged.append(chunk)

    if len(merged) == 1 and len(merged[0]) >= 8:
        return _fallback_even_phrase_chunks(merged[0])
    return merged


def _fallback_even_phrase_chunks(tokens: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    chunk_size = 6 if len(tokens) >= 12 else max(3, len(tokens) // 2)
    chunks: list[list[dict[str, Any]]] = []
    for index in range(0, len(tokens), chunk_size):
        chunk = tokens[index : index + chunk_size]
        if len(chunk) < 2:
            if chunks:
                chunks[-1].extend(chunk)
            continue
        chunks.append(chunk)
    return chunks


def _phrase_from_tokens(phrase_id: str, label: str, tokens: list[dict[str, Any]], raw_text: str) -> dict[str, Any]:
    scoped_tokens: list[dict[str, Any]] = []
    for token in tokens:
        if not isinstance(token, dict):
            continue
        scoped = dict(token)
        scoped["id"] = f"{phrase_id}_{scoped.get('id') or len(scoped_tokens) + 1}"
        scoped_tokens.append(scoped)
    unique = []
    seen = set()
    for token in scoped_tokens:
        token_id = token["id"]
        if token_id in seen:
            continue
        seen.add(token_id)
        unique.append(token)
    return {
        "id": phrase_id,
        "label": label,
        "source_text": raw_text.strip()[:240],
        "target_sequence": [token["id"] for token in scoped_tokens],
        "main_melody": unique,
        "playback_tokens": scoped_tokens,
        "rhythm_features": _rhythm_features(scoped_tokens),
        "singing_difficulty": _singing_difficulty(scoped_tokens),
    }


def _tokens_from_text(text: str) -> list[dict[str, Any]]:
    durations = _durations_from_text(text)
    raw_tokens = re.findall(r"(?i)\bdo\b|\bre\b|\bmi\b|\bfa\b|\bsol\b|\bso\b|\bla\b|\bsi\b|\bti\b|[0-7]|宫|商|角|徵|徴|羽|休止", text)
    tokens: list[dict[str, Any]] = []
    for index, raw in enumerate(raw_tokens[:32], start=1):
        key = raw.lower()
        if raw in {"0", "休止"}:
            tokens.append(_note_token("rest", "休止", 0, index - 1, durations[index - 1] if index - 1 < len(durations) else 1.0, rest=True))
            continue
        pitch = SOLFEGE_TO_PITCH.get(key) or SOLFEGE_TO_PITCH.get(raw) or 60
        label = _normalize_solfege_label(raw)
        duration = durations[index - 1] if index - 1 < len(durations) else 1.0
        tokens.append(_note_token(_token_id(label, index), label, pitch, index - 1, duration))
    return tokens


def _durations_from_text(text: str) -> list[float]:
    mapping = [
        ("全音符", 4.0),
        ("二分音符", 2.0),
        ("四分音符", 1.0),
        ("八分音符", 0.5),
        ("十六分音符", 0.25),
        ("全音", 4.0),
        ("二分", 2.0),
        ("四分", 1.0),
        ("八分", 0.5),
        ("十六分", 0.25),
    ]
    durations: list[float] = []
    for token in re.split(r"[\s,，;；/、]+", text):
        for keyword, value in mapping:
            if keyword in token:
                durations.append(value)
                break
    return durations


def _note_token(token_id: str, label: str, pitch: int, start: float, duration: float, *, rest: bool = False) -> dict[str, Any]:
    return {
        "id": token_id,
        "label": label,
        "music_value": "休止" if rest else f"{label} 音",
        "pitch": pitch,
        "start": round(float(start), 3),
        "duration": round(max(float(duration), 0.12), 3),
        "velocity": 86,
        "rest": rest,
        "feedback": f"这是歌曲片段中的“{label}”。",
    }


def _select_phrase(phrases: list[dict[str, Any]], lesson_context: dict[str, Any], extra_need: str) -> dict[str, Any]:
    if not phrases:
        return {}
    source = " ".join(
        [
            str(lesson_context.get("target_music_element", "")),
            str(lesson_context.get("target_segment_task", "")),
            str(extra_need or ""),
        ]
    )
    if any(word in source for word in ["开头", "主题", "第一", "主旋律"]):
        return phrases[0]
    ranked = sorted(phrases, key=lambda item: (len(item.get("target_sequence", [])), item.get("singing_difficulty", 3)))
    return ranked[0] if ranked else phrases[0]


def _teaching_points_from_phrases(phrases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    points = []
    for phrase in phrases[:4]:
        points.append(
            {
                "phrase_id": phrase.get("id", ""),
                "label": phrase.get("label", ""),
                "recommended_activity": "先听辨真实乐句，再排序、跟唱或改编。",
                "features": phrase.get("rhythm_features", []),
            }
        )
    return points


def _rhythm_features(tokens: list[dict[str, Any]]) -> list[str]:
    durations = [float(item.get("duration", 1.0)) for item in tokens]
    features = []
    if any(duration >= 2 for duration in durations):
        features.append("长音保持")
    if any(duration <= 0.5 for duration in durations):
        features.append("短音密集")
    if any(item.get("rest") for item in tokens):
        features.append("休止停顿")
    if not features:
        features.append("稳定节奏")
    return features


def _singing_difficulty(tokens: list[dict[str, Any]]) -> int:
    pitches = [int(item.get("pitch", 60)) for item in tokens if not item.get("rest")]
    if len(pitches) < 2:
        return 1
    span = max(pitches) - min(pitches)
    if span <= 5 and len(tokens) <= 6:
        return 1
    if span <= 12 and len(tokens) <= 10:
        return 2
    return 3


def _is_singing_context(lesson_analysis: dict[str, Any], lesson_context: dict[str, Any], extra_need: str) -> bool:
    source = " ".join(
        str(item)
        for item in [
            lesson_analysis.get("objective_summary", ""),
            lesson_analysis.get("game_stage", ""),
            lesson_context.get("target_objective", ""),
            lesson_context.get("target_segment_task", ""),
            extra_need,
        ]
    )
    return any(keyword in source for keyword in ["学唱", "演唱", "唱会", "跟唱", "模唱", "歌曲表现", "乐句"])


def _extract_phrase_lines(text: str) -> list[tuple[str, str, str]]:
    results: list[tuple[str, str, str]] = []
    normalized = re.sub(r"[；;。]+", "\n", text)
    normalized = re.sub(
        r"(?<!\n)\s*(第(?:[一二三四五六七八九十\d]+)(?:乐句|句))\s*(?=[0-7doresmifalati宫商角徵徴羽])",
        r"\n\1：",
        normalized,
        flags=re.IGNORECASE,
    )
    normalized = re.sub(
        r"(?<!\n)\s*(第(?:[一二三四五六七八九十\d]+)(?:乐句|句))\s*[是为]",
        r"\n\1：",
        normalized,
        flags=re.IGNORECASE,
    )

    pattern = re.compile(
        r"(第(?:[一二三四五六七八九十\d]+)(?:乐句|句)|(?:乐句|旋律|主题|片段)\s*\d*)\s*[:：]?\s*(.+?)(?=(?:\n\s*(?:第(?:[一二三四五六七八九十\d]+)(?:乐句|句)|(?:乐句|旋律|主题|片段)\s*\d*)\s*[:：]?)|\Z)",
        flags=re.IGNORECASE | re.S,
    )
    for index, match in enumerate(pattern.finditer(normalized), start=1):
        label = match.group(1).strip()
        body = " ".join(match.group(2).strip().split())
        if not body:
            continue
        results.append((f"phrase_{index}", label, body))

    if results:
        return results

    compact_notation_lines: list[tuple[str, str, str]] = []
    for index, line in enumerate(normalized.splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        digits = re.findall(r"[0-7]|休止", stripped)
        if len(digits) < 3:
            continue
        # 允许行首存在少量歌名/脏字，只要主体仍是简谱数字串，就提取为乐句。
        notation_body = " ".join(digits)
        compact_notation_lines.append((f"phrase_{index}", f"第{len(compact_notation_lines) + 1}乐句", notation_body))
    if compact_notation_lines:
        return compact_notation_lines[:8]

    for index, line in enumerate(normalized.splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        if re.search(r"乐句|旋律|主题|片段", stripped) and re.search(r"[:：]", stripped):
            label, body = re.split(r"[:：]", stripped, maxsplit=1)
            results.append((f"line_{index}", label.strip(), body.strip()))
    return results


def _extract_title(text: str) -> str:
    for raw in re.findall(r"《([^》]{1,36})》", text):
        cleaned = _clean_song_title(raw)
        if cleaned:
            return f"《{cleaned}》"
    return _extract_by_label(text, ["歌名", "曲名", "歌曲", "Title", "title"])


def _extract_by_label(text: str, labels: list[str]) -> str:
    for label in labels:
        match = re.search(rf"{re.escape(label)}\s*[:：]\s*([^\n\r]+)", text)
        if match:
            return match.group(1).strip()[:80]
    return ""


def _title_from_filename(filename: str) -> str:
    stem = Path(filename or "").stem.strip()
    return _clean_song_title(stem)


def _clean_song_title(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text).strip(" _-")
    lower = text.lower()
    if lower in {
        "lesson-embedded-score",
        "lesson_embedded_score",
        "embedded-score",
        "embedded_score",
        "song-material",
        "song_material",
        "score-material",
        "score_material",
        "当前歌曲",
        "当前课例",
        "current-song",
        "uploaded-song",
        "uploaded_score",
    }:
        return ""
    if any(token in lower for token in ["embedded-score", "song-material", "score-material"]):
        return ""
    return text


def _first_text(root: ET.Element, path: str) -> str:
    node = root.find(path)
    return (node.text or "").strip() if node is not None and node.text else ""


def _first_int(root: ET.Element, path: str, default: int = 0) -> int:
    try:
        return int(float(_first_text(root, path) or default))
    except (TypeError, ValueError):
        return default


def _musicxml_pitch(step: str, alter: int, octave: int) -> int:
    pcs = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
    return 12 * (octave + 1) + pcs.get(step.upper(), 0) + alter


def _pitch_label(pitch: int) -> str:
    return PITCH_TO_SOLFEGE.get(pitch % 12, f"MIDI {pitch}")


def _normalize_solfege_label(raw: str) -> str:
    label = raw.lower()
    if label == "so":
        return "sol"
    if label in {"si", "ti"}:
        return "ti"
    number_labels = {"1": "do", "2": "re", "3": "mi", "4": "fa", "5": "sol", "6": "la", "7": "ti"}
    chinese_labels = {"宫": "宫", "商": "商", "角": "角", "徵": "徵", "徴": "徵", "羽": "羽"}
    return number_labels.get(raw, chinese_labels.get(raw, label))


def _token_id(label: str, index: int) -> str:
    normalized = re.sub(r"[^A-Za-z0-9_\u4e00-\u9fff]+", "_", label).strip("_").lower()
    base = normalized or "note"
    return f"{base}_{index}"


def _decode_text(data: bytes) -> str:
    for encoding in ("utf-8", "utf-8-sig", "gb18030", "gbk"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="ignore")


def _decode_musicxml_payload(filename: str, data: bytes) -> str:
    suffix = Path(filename or "").suffix.lower()
    if suffix == ".mxl":
        with tempfile.NamedTemporaryFile(suffix=".mxl", delete=True) as temp:
            temp.write(data)
            temp.flush()
            with zipfile.ZipFile(temp.name) as archive:
                candidates = [
                    name
                    for name in archive.namelist()
                    if name.lower().endswith((".xml", ".musicxml"))
                    and "container.xml" not in name.lower()
                    and not name.startswith("__MACOSX/")
                ]
                if not candidates:
                    raise ValueError("MXL 文件里没有找到 MusicXML 主文件。")
                return archive.read(candidates[0]).decode("utf-8", errors="ignore")
    return _decode_text(data)


def _score_image_page_candidates(input_path: Path, workspace: Path) -> list[list[Path]]:
    pages = _score_image_pages(input_path, workspace)
    groups: list[list[Path]] = []
    for page in pages:
        candidates = []
        candidates.extend(_preprocess_score_page(page, workspace))
        candidates.append(page)
        groups.append(_unique_paths(candidates))
    return groups


def _score_image_pages(input_path: Path, workspace: Path) -> list[Path]:
    suffix = input_path.suffix.lower()
    if suffix != ".pdf":
        return [input_path]
    try:
        import fitz
    except ImportError:
        return []
    page_dir = workspace / "pdf-pages"
    page_dir.mkdir(parents=True, exist_ok=True)
    pages: list[Path] = []
    document = fitz.open(str(input_path))
    for index in range(min(document.page_count, 3)):
        page = document.load_page(index)
        pixmap = page.get_pixmap(matrix=fitz.Matrix(3, 3), alpha=False)
        page_path = page_dir / f"page_{index + 1}.png"
        pixmap.save(str(page_path))
        pages.append(page_path)
    return pages


def _preprocess_score_page(image_path: Path, workspace: Path) -> list[Path]:
    try:
        from PIL import Image, ImageEnhance, ImageFilter, ImageOps
    except Exception:
        return []

    output_dir = workspace / "ocr-preprocessed"
    output_dir.mkdir(parents=True, exist_ok=True)
    try:
        original = Image.open(image_path)
        image = original.convert("L")
        width, height = image.size
        if max(width, height) < 1800:
            scale = min(3.0, 1800 / max(width, height))
            image = image.resize((int(width * scale), int(height * scale)))
        enhanced = ImageOps.autocontrast(image)
        enhanced = ImageEnhance.Contrast(enhanced).enhance(1.55)
        enhanced = enhanced.filter(ImageFilter.SHARPEN)
        clean_path = output_dir / f"{image_path.stem}_clean.png"
        enhanced.save(clean_path)

        threshold = int(os.getenv("JIANPU_OCR_THRESHOLD", "185"))
        binary = enhanced.point(lambda pixel: 255 if pixel > threshold else 0)
        binary_path = output_dir / f"{image_path.stem}_binary.png"
        binary.save(binary_path)
        return [clean_path, binary_path]
    except Exception:
        return []


def _unique_paths(paths: list[Path]) -> list[Path]:
    result: list[Path] = []
    seen: set[str] = set()
    for path in paths:
        key = str(path)
        if key in seen:
            continue
        seen.add(key)
        result.append(path)
    return result
