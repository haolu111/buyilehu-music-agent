from __future__ import annotations

import re
from typing import Any


RHYTHM_NOTE_VALUES: dict[str, dict[str, Any]] = {
    "whole": {
        "label": "全音符",
        "symbol": "𝅝",
        "fallback_symbol": "○",
        "value": "4拍",
        "beats": 4.0,
        "duration_label": "四拍长音",
        "midi": 60,
    },
    "half": {
        "label": "二分音符",
        "symbol": "𝅗𝅥",
        "fallback_symbol": "○|",
        "value": "2拍",
        "beats": 2.0,
        "duration_label": "两拍长音",
        "midi": 60,
    },
    "quarter": {
        "label": "四分音符",
        "symbol": "♩",
        "fallback_symbol": "♩",
        "value": "1拍",
        "beats": 1.0,
        "duration_label": "一拍",
        "midi": 60,
    },
    "eighth": {
        "label": "八分音符",
        "symbol": "♪",
        "fallback_symbol": "♪",
        "value": "半拍",
        "beats": 0.5,
        "duration_label": "半拍",
        "midi": 60,
    },
}

SOLFEGE_PITCHES: dict[str, dict[str, Any]] = {
    "do": {"label": "do", "movable_do": "do", "scale_degree": 1, "midi": 60, "height_index": 0},
    "re": {"label": "re", "movable_do": "re", "scale_degree": 2, "midi": 62, "height_index": 1},
    "mi": {"label": "mi", "movable_do": "mi", "scale_degree": 3, "midi": 64, "height_index": 2},
    "sol": {"label": "sol", "movable_do": "sol", "scale_degree": 5, "midi": 67, "height_index": 4},
    "la": {"label": "la", "movable_do": "la", "scale_degree": 6, "midi": 69, "height_index": 5},
}

PENTATONIC_PITCHES: dict[str, dict[str, Any]] = {
    "gong": {"label": "宫", "movable_do": "do", "scale_degree": 1, "midi": 60, "function": "稳定起点"},
    "shang": {"label": "商", "movable_do": "re", "scale_degree": 2, "midi": 62, "function": "向前发展"},
    "jue": {"label": "角", "movable_do": "mi", "scale_degree": 3, "midi": 64, "function": "柔和色彩"},
    "zhi": {"label": "徵", "movable_do": "sol", "scale_degree": 5, "midi": 67, "function": "明亮支点"},
    "yu": {"label": "羽", "movable_do": "la", "scale_degree": 6, "midi": 69, "function": "收束色彩"},
}


def build_music_logic_contract(
    *,
    spec: dict[str, Any] | None = None,
    need: str = "",
    music_game: dict[str, Any] | None = None,
    playable_game: dict[str, Any] | None = None,
    lesson_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create one canonical music table that UI, playback and scoring must share."""

    spec = spec or {}
    music_game = dict(music_game or spec.get("music_game") or {})
    playable_game = dict(playable_game or music_game.get("playable_game") or {})
    lesson_context = dict(lesson_context or spec.get("lesson_context") or {})
    source = " ".join(
        [
            need,
            str(spec.get("title", "")),
            str(spec.get("subtitle", "")),
            str(spec.get("target_music_element", "")),
            str(lesson_context.get("target_music_element", "")),
            str(music_game.get("music_concept", "")),
            str(music_game.get("game_type", "")),
            str(playable_game.get("operation_type", "")),
        ]
    )
    concept = str(
        spec.get("target_music_element")
        or lesson_context.get("target_music_element")
        or music_game.get("music_concept")
        or "音乐要素"
    )

    if _has_song_phrase_expression_table(playable_game):
        return _song_phrase_expression_contract(concept, playable_game)
    if _has_song_phrase_structure_table(playable_game):
        return _song_phrase_structure_contract(concept, playable_game)
    if _has_song_phrase_table(playable_game):
        return _song_phrase_contract(concept, playable_game)
    if _is_explicit_pitch_game(source, playable_game):
        return _pitch_contract(concept, source, playable_game)
    if _contains(source, ["音色", "乐器", "管弦", "民族乐器", "清脆", "柔和", "打击", "timbre", "instrument"]):
        return _timbre_contract(concept, music_game, playable_game)
    if _contains(
        source,
        ["meter_gate", "时值", "节奏", "节拍", "拍子", "强拍", "弱拍", "全音符", "二分音符", "四分音符", "八分音符", "附点", "切分", "休止"],
    ):
        return _rhythm_contract(concept, source, music_game, playable_game)
    if _contains(source, ["乐句", "乐段", "片段", "曲式", "结构", "段落"]):
        return _structure_contract(concept, playable_game)
    if _contains(source, ["五声", "宫", "商", "角", "徵", "羽", "调式", "民族"]):
        return _pentatonic_contract(concept, playable_game)
    if _contains(source, ["力度", "强弱", "渐强", "渐弱", "速度", "快慢"]):
        return _expression_contract(concept, source, playable_game)
    if _contains(source, ["sol", "mi", "do", "re", "唱名", "高低音", "音高", "旋律", "上行", "下行", "级进", "跳进"]):
        return _pitch_contract(concept, source, playable_game)
    return _generic_contract(concept, music_game, playable_game)


def attach_music_logic_contract(spec: dict[str, Any], *, need: str = "") -> dict[str, Any]:
    enriched = dict(spec)
    music_game = dict(enriched.get("music_game") or {})
    if not music_game.get("enabled") and enriched.get("activity_type") != "music_game":
        return enriched
    lesson_context = dict(enriched.get("lesson_context") or {})
    playable_game = dict(music_game.get("playable_game") or lesson_context.get("playable_game") or {})
    contract = build_music_logic_contract(
        spec=enriched,
        need=need,
        music_game=music_game,
        playable_game=playable_game,
        lesson_context=lesson_context,
    )
    music_game["music_logic_contract"] = contract
    if playable_game:
        playable_game = _align_playable_to_contract(playable_game, contract)
    else:
        playable_game = _playable_from_contract(contract)
    music_game["playable_game"] = playable_game
    if lesson_context:
        lesson_context["playable_game"] = playable_game
    enriched["music_game"] = music_game
    enriched["music_logic_contract"] = contract
    if lesson_context:
        lesson_context["music_logic_contract"] = contract
        lesson_context["musical_game_logic_contract"] = _legacy_non_negotiables(contract)
        enriched["lesson_context"] = lesson_context
    return enriched


def align_playable_game_to_contract(playable_game: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    """Expose the canonical contract -> playable alignment for upstream lesson flows."""

    return _align_playable_to_contract(playable_game, contract)


def validate_music_logic_contract(contract: dict[str, Any], playable_game: dict[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    if not isinstance(contract, dict) or not contract:
        return ["缺少 music_logic_contract。"]
    token_table = contract.get("tokens")
    if not isinstance(token_table, list) or not token_table:
        errors.append("music_logic_contract.tokens 不能为空。")
        return errors
    token_ids = [str(item.get("id", "")).strip() for item in token_table if isinstance(item, dict)]
    if len(token_ids) != len(set(token_ids)):
        errors.append("music_logic_contract.tokens 存在重复 id。")
    for token in token_table:
        if not isinstance(token, dict):
            errors.append("音乐材料必须是对象。")
            continue
        token_id = str(token.get("id", "")).strip()
        if not token_id:
            errors.append("音乐材料缺少 id。")
        if not str(token.get("label", "")).strip():
            errors.append(f"音乐材料 {token_id or '?'} 缺少标准名称。")
        if "playback" not in token or not isinstance(token.get("playback"), dict):
            errors.append(f"音乐材料 {token_id or '?'} 缺少 playback。")
            continue
        playback = token["playback"]
        if not bool(playback.get("rest")):
            midi = playback.get("midi")
            if not isinstance(midi, int) or not 0 <= midi <= 127:
                errors.append(f"音乐材料 {token_id or '?'} 的 midi 音高无效。")
        beats = playback.get("duration_beats")
        if not isinstance(beats, (int, float)) or float(beats) <= 0:
            errors.append(f"音乐材料 {token_id or '?'} 的 duration_beats 必须为正数。")
    for round_item in contract.get("rounds", []):
        if not isinstance(round_item, dict):
            continue
        for token_id in round_item.get("target_sequence", []):
            if token_id not in token_ids:
                errors.append(f"关卡 {round_item.get('id', '?')} 引用了不存在的音乐材料：{token_id}。")
    if isinstance(playable_game, dict) and playable_game:
        playable_ids = [
            str(item.get("id", "")).strip()
            for item in playable_game.get("materials", [])
            if isinstance(item, dict) and str(item.get("id", "")).strip()
        ]
        for token_id in playable_game.get("target_sequence", []):
            if token_id not in token_ids:
                errors.append(f"playable_game.target_sequence 引用了契约外材料：{token_id}。")
            if playable_ids and token_id not in playable_ids:
                errors.append(f"playable_game.target_sequence 引用了素材池外材料：{token_id}。")
    return errors


def _rhythm_contract(
    concept: str,
    source: str,
    music_game: dict[str, Any],
    playable_game: dict[str, Any],
) -> dict[str, Any]:
    requested = ["whole", "half", "quarter"]
    if _contains(source, ["八分", "半拍"]):
        requested.append("eighth")
    rules = music_game.get("rules") if isinstance(music_game.get("rules"), list) else []
    characters = _characters_by_label(rules)
    tokens = []
    for token_id in requested:
        value = RHYTHM_NOTE_VALUES[token_id]
        tokens.append(
            {
                "id": token_id,
                "label": value["label"],
                "symbol": value["symbol"],
                "fallback_symbol": value["fallback_symbol"],
                "display": f"{value['label']} {value['symbol']} {value['value']}",
                "music_value": value["value"],
                "duration_beats": value["beats"],
                "character": characters.get(value["label"], _default_character(token_id)),
                "playback": {
                    "midi": value["midi"],
                    "duration_beats": value["beats"],
                    "velocity": 88,
                    "rest": False,
                    "pedagogical_role": "同一音高，不同时值，避免把节奏游戏误导成音高游戏。",
                },
            }
        )
    token_ids = [item["id"] for item in tokens]
    target_sequence = _safe_sequence(playable_game.get("target_sequence"), token_ids) or _default_rhythm_sequence(token_ids)
    return _contract(
        concept=concept or "节奏时值",
        focus="rhythm_duration",
        tokens=tokens,
        rounds=_rounds_from_sequence(target_sequence, token_ids, labels=["第 1 关", "第 2 关", "第 3 关"]),
        non_negotiables=[
            "节奏时值游戏必须用同一音高或同一打击音色播放，只改变时长。",
            "符号、名称、拍数、动画时长、判定答案必须来自 tokens 同一张表。",
            "target_sequence 只能引用 tokens 中存在的 id，不能出现素材池里没有的答案。",
        ],
    )


def _is_explicit_pitch_game(source: str, playable_game: dict[str, Any]) -> bool:
    operation_type = str(playable_game.get("operation_type", ""))
    if operation_type in {"pitch_action_response", "solmi_pitch_ladder"}:
        return True
    return _contains(source, ["sol", "mi", "唱名", "高低音", "音高"]) and not _contains(
        operation_type,
        ["phrase_structure", "song_phrase", "section"],
    )


def _pitch_contract(concept: str, source: str, playable_game: dict[str, Any]) -> dict[str, Any]:
    explicit_solmi = _contains(source, ["sol-mi", "sol/mi", "sol 和 mi", "sol与mi"]) or (
        _contains(source, ["sol"]) and _contains(source, ["mi"])
    )
    keys = ["sol", "mi"] if explicit_solmi and not _has_explicit_dore(source) else ["do", "re", "mi", "sol"]
    if _contains(source, ["la", "五声"]):
        keys.append("la")
    tokens = []
    for key in keys:
        value = SOLFEGE_PITCHES[key]
        tokens.append(
            {
                "id": key,
                "label": value["label"],
                "symbol": value["label"],
                "display": f"{value['label']}（首调第{value['scale_degree']}级）",
                "music_value": f"首调第{value['scale_degree']}级",
                "scale_degree": value["scale_degree"],
                "movable_do": value["movable_do"],
                "height_index": value["height_index"],
                "playback": {
                    "midi": value["midi"],
                    "duration_beats": 1,
                    "velocity": 86,
                    "rest": False,
                    "pedagogical_role": "音高游戏必须播放具体唱名，不用抽象上下方向替代固定唱名。",
                },
            }
        )
    token_ids = [item["id"] for item in tokens]
    target_sequence = _safe_sequence(playable_game.get("target_sequence"), token_ids) or token_ids[:3]
    return _contract(
        concept=concept or "音高关系",
        focus="pitch_solfege",
        tokens=tokens,
        rounds=_rounds_from_sequence(target_sequence, token_ids),
        non_negotiables=[
            "音高游戏必须使用具体唱名或音级，不能把 sol/mi/do/re 改成向上、向下、保持。",
            "页面位置高度、播放音高、判定答案必须来自 tokens 同一张表。",
        ],
    )


def _has_explicit_dore(source: str) -> bool:
    return bool(re.search(r"(?<![A-Za-z])(?:do|re)(?![A-Za-z])|do\s*[/和与-]\s*re|do\s*re", str(source), re.I))


def _timbre_contract(concept: str, music_game: dict[str, Any], playable_game: dict[str, Any]) -> dict[str, Any]:
    raw = [
        ("bright", "明亮音色", "清脆 / 有穿透感", 72, "flute"),
        ("soft", "柔和音色", "圆润 / 连贯", 64, "violin"),
        ("percussive", "打击音色", "短促 / 颗粒感", 48, "xylophone"),
        ("plucked", "拨弦音色", "清亮 / 有余音", 67, "koto"),
    ]
    rules = music_game.get("rules") if isinstance(music_game.get("rules"), list) else []
    characters = _characters_by_label(rules)
    tokens = []
    for token_id, label, value, midi, instrument in raw:
        tokens.append(
            {
                "id": token_id,
                "label": label,
                "symbol": label[:2],
                "display": f"{label}：{value}",
                "music_value": value,
                "character": characters.get(label, label),
                "instrument": instrument,
                "playback": {
                    "midi": midi,
                    "duration_beats": 0.75 if token_id == "percussive" else 1.1,
                    "velocity": 92,
                    "rest": False,
                    "instrument": instrument,
                },
            }
        )
    token_ids = [item["id"] for item in tokens]
    target_sequence = _safe_sequence(playable_game.get("target_sequence"), token_ids) or ["percussive", "bright", "soft"]
    return _contract(
        concept=concept or "乐器音色",
        focus="timbre_evidence",
        tokens=tokens,
        rounds=_rounds_from_sequence(target_sequence, token_ids, labels=["听辨音色", "比较音色", "说明证据"]),
        non_negotiables=[
            "音色游戏必须使用音色证据卡或乐器卡，不能改成 do/re/mi/sol 唱名卡。",
            "页面必须提供可听的音色样本，并让学生根据听觉证据拖拽或匹配。",
            "如果没有真实采样资源，页面必须明确提示音色资源缺失，不能用电子合成音假装真实乐器。",
        ],
    )


def _structure_contract(concept: str, playable_game: dict[str, Any]) -> dict[str, Any]:
    raw = [
        ("opening", "开头乐句", "起始材料", 60, 1.0),
        ("development", "发展乐句", "展开材料", 64, 1.0),
        ("contrast", "对比乐句", "变化材料", 67, 1.0),
        ("closing", "收束乐句", "结束材料", 60, 1.25),
    ]
    tokens = [
        {
            "id": token_id,
            "label": label,
            "symbol": str(index),
            "display": f"{label}：{value}",
            "music_value": value,
            "playback": {"midi": midi, "duration_beats": beats, "velocity": 84, "rest": False},
        }
        for index, (token_id, label, value, midi, beats) in enumerate(raw, start=1)
    ]
    token_ids = [item["id"] for item in tokens]
    target_sequence = _safe_sequence(playable_game.get("target_sequence"), token_ids) or ["opening", "development", "contrast", "closing"]
    return _contract(
        concept=concept or "乐句与曲式结构",
        focus="phrase_structure",
        tokens=tokens,
        rounds=_rounds_from_sequence(target_sequence, token_ids),
        non_negotiables=[
            "结构重建游戏必须围绕乐句或乐段的开头、发展、对比、收束关系。",
            "片段显示、播放顺序、判定答案必须来自 tokens 同一张表。",
            "反馈必须指出结构依据，不能只说排序对错。",
        ],
    )


def _has_song_phrase_table(playable_game: dict[str, Any]) -> bool:
    table = playable_game.get("song_phrase_table") if isinstance(playable_game, dict) else {}
    return isinstance(table, dict) and bool(table.get("target_sequence")) and bool(table.get("playback_tokens"))


def _has_song_phrase_expression_table(playable_game: dict[str, Any]) -> bool:
    if not isinstance(playable_game, dict):
        return False
    if str(playable_game.get("operation_type", "")).strip() != "song_phrase_expression_match":
        return False
    materials = playable_game.get("materials", [])
    if isinstance(materials, list) and any(isinstance(item, dict) for item in materials):
        return True
    table = playable_game.get("song_phrase_table") if isinstance(playable_game.get("song_phrase_table"), dict) else {}
    return isinstance(table, dict) and bool(table.get("target_sequence"))


def _has_song_phrase_structure_table(playable_game: dict[str, Any]) -> bool:
    table = playable_game.get("song_phrase_table") if isinstance(playable_game, dict) else {}
    cards = table.get("phrase_cards") if isinstance(table, dict) else []
    return (
        isinstance(table, dict)
        and table.get("mode") == "phrase_structure"
        and bool(table.get("target_sequence"))
        and isinstance(cards, list)
        and bool(cards)
    )


def _song_phrase_contract(concept: str, playable_game: dict[str, Any]) -> dict[str, Any]:
    table = playable_game.get("song_phrase_table", {}) if isinstance(playable_game.get("song_phrase_table"), dict) else {}
    playback_tokens = [item for item in table.get("playback_tokens", []) if isinstance(item, dict)]
    sequence = [str(item).strip() for item in table.get("target_sequence", []) if str(item).strip()]
    if not sequence:
        sequence = [str(item.get("id", "")).strip() for item in playback_tokens if str(item.get("id", "")).strip()]

    material_by_id: dict[str, dict[str, Any]] = {}
    for token in playback_tokens:
        token_id = str(token.get("id", "")).strip()
        if not token_id or token_id in material_by_id:
            continue
        label = str(token.get("label") or token_id)
        material_by_id[token_id] = {
            "id": token_id,
            "label": label,
            "symbol": label,
            "display": f"{label}：歌曲真实音",
            "music_value": str(token.get("music_value") or f"{label} 音"),
            "playback": {
                "midi": int(token.get("pitch", 60) or 60),
                "duration_beats": float(token.get("duration", 1.0) or 1.0),
                "velocity": int(token.get("velocity", 86) or 86),
                "rest": bool(token.get("rest", False)),
            },
        }

    if not material_by_id:
        return _structure_contract(concept, playable_game)

    token_ids = list(material_by_id.keys())
    capped_sequence = [item for item in sequence if item in material_by_id][:8]
    if len(capped_sequence) < 2:
        capped_sequence = token_ids[: min(4, len(token_ids))]
    return _contract(
        concept=concept or "歌曲真实乐句",
        focus="song_phrase_rebuild",
        tokens=[material_by_id[token_id] for token_id in token_ids],
        rounds=_song_phrase_rounds(capped_sequence, token_ids),
        non_negotiables=[
            "歌曲类游戏必须使用歌曲材料表中的真实唱名、音高和时值。",
            "页面显示、播放和判定必须来自同一个 song_phrase_table，不允许用开头/发展等抽象卡片替代真实唱名。",
            "每关只截取适合课堂操作的短乐句，通关后必须回到模唱或听唱。",
        ],
    )


def _material_token_from_playable(material: dict[str, Any]) -> dict[str, Any]:
    playback_tokens = material.get("playback_tokens", []) if isinstance(material.get("playback_tokens"), list) else []
    return {
        "id": str(material.get("id", "")).strip(),
        "label": str(material.get("label") or material.get("id") or ""),
        "symbol": str(material.get("symbol") or material.get("label") or ""),
        "display": str(material.get("display") or material.get("music_value") or material.get("label") or ""),
        "music_value": str(material.get("music_value") or material.get("label") or ""),
        "phrase_role": str(material.get("phrase_role") or ""),
        "audio_clip_url": str(material.get("audio_clip_url") or ""),
        "playback_tokens": playback_tokens,
        "playback": {
            "midi": int(material.get("pitch", 60) or 60),
            "duration_beats": float(material.get("duration", 1.0) or 1.0),
            "velocity": int(material.get("velocity", 86) or 86),
            "rest": bool(material.get("rest", False)),
        },
    }


def _is_expression_evidence_material(material: dict[str, Any]) -> bool:
    source = " ".join(
        [
            str(material.get("id", "")),
            str(material.get("label", "")),
            str(material.get("music_value", "")),
            str(material.get("display", "")),
            str(material.get("feedback", "")),
        ]
    )
    return _contains(source, ["情绪", "动作", "演唱", "唱法", "跳跃", "连贯", "温馨", "欢快", "对比", "重复", "表现"])


def _song_phrase_expression_contract(concept: str, playable_game: dict[str, Any]) -> dict[str, Any]:
    materials = playable_game.get("materials", []) if isinstance(playable_game.get("materials"), list) else []
    material_by_id = {
        str(item.get("id", "")).strip(): dict(item)
        for item in materials
        if isinstance(item, dict) and str(item.get("id", "")).strip()
    }
    table = playable_game.get("song_phrase_table", {}) if isinstance(playable_game.get("song_phrase_table"), dict) else {}
    sequence = _safe_sequence(
        playable_game.get("target_sequence") or table.get("target_sequence"),
        list(material_by_id.keys()),
    )

    phrase_ids: list[str] = []
    evidence_ids: list[str] = []
    ordered_ids = sequence or list(material_by_id.keys())
    for token_id in ordered_ids:
        material = material_by_id.get(token_id)
        if not material:
            continue
        if _is_expression_evidence_material(material):
            evidence_ids.append(token_id)
        else:
            phrase_ids.append(token_id)

    if not phrase_ids or not evidence_ids:
        for token_id, material in material_by_id.items():
            if token_id in phrase_ids or token_id in evidence_ids:
                continue
            if _is_expression_evidence_material(material):
                evidence_ids.append(token_id)
            else:
                phrase_ids.append(token_id)

    if not phrase_ids:
        return _song_phrase_structure_contract(concept, playable_game)

    if not evidence_ids:
        return _song_phrase_contract(concept, playable_game)

    full_sequence = _safe_sequence(sequence, phrase_ids + evidence_ids)
    if len(full_sequence) < 4:
        full_sequence = _song_phrase_expression_sequence(phrase_ids, evidence_ids)

    ordered_token_ids: list[str] = []
    for token_id in [*full_sequence, *phrase_ids, *evidence_ids]:
        if token_id and token_id in material_by_id and token_id not in ordered_token_ids:
            ordered_token_ids.append(token_id)

    return _contract(
        concept=concept or "歌曲片段与表现依据",
        focus="song_phrase_expression_match",
        tokens=[_material_token_from_playable(material_by_id[token_id]) for token_id in ordered_token_ids],
        rounds=_song_phrase_expression_rounds(phrase_ids, evidence_ids, full_sequence),
        non_negotiables=[
            "该类游戏必须同时保留真实歌曲片段卡和表现证据卡，不能退化成纯唱名排序。",
            "页面中的点击、拖拽、播放与判定都必须共用同一张 tokens 材料表。",
            "通关后必须让学生用情绪、声音或动作说明依据，而不是只返回排序结果。",
        ],
    )


def _song_phrase_structure_contract(concept: str, playable_game: dict[str, Any]) -> dict[str, Any]:
    table = playable_game.get("song_phrase_table", {}) if isinstance(playable_game.get("song_phrase_table"), dict) else {}
    cards = [item for item in table.get("phrase_cards", []) if isinstance(item, dict)]
    materials = playable_game.get("materials", []) if isinstance(playable_game.get("materials"), list) else []
    material_by_id = {
        str(item.get("id", "")).strip(): item
        for item in materials
        if isinstance(item, dict) and str(item.get("id", "")).strip()
    }
    tokens: list[dict[str, Any]] = []
    for index, card in enumerate(cards, start=1):
        token_id = str(card.get("id", "")).strip()
        if not token_id:
            continue
        playable_material = material_by_id.get(token_id, {})
        playback_tokens = [
            {
                "id": str(item.get("id", "")),
                "label": str(item.get("label", "")),
                "pitch": int(item.get("pitch", 60) or 60),
                "duration": float(item.get("duration", 0.5) or 0.5),
                "velocity": int(item.get("velocity", 86) or 86),
                "rest": bool(item.get("rest", False)),
            }
            for item in card.get("playback_tokens", [])
            if isinstance(item, dict)
        ]
        preview_pitch = int(playable_material.get("pitch", playback_tokens[0].get("pitch", 60) if playback_tokens else 60))
        preview_duration = float(
            playable_material.get("duration")
            or sum(float(item.get("duration", 0.5) or 0.5) for item in playback_tokens[:8])
            or 1.0
        )
        tokens.append(
            {
                "id": token_id,
                "label": str(card.get("label") or playable_material.get("label") or f"乐句片段{index}"),
                "symbol": str(index),
                "display": str(card.get("music_value") or playable_material.get("music_value") or f"真实片段 {index}"),
                "music_value": str(card.get("music_value") or playable_material.get("music_value") or f"真实片段 {index}"),
                "phrase_role": str(playable_material.get("phrase_role") or ""),
                "audio_clip_url": str(playable_material.get("audio_clip_url") or card.get("audio_clip_url") or ""),
                "playback_tokens": playback_tokens,
                "playback": {
                    "midi": preview_pitch,
                    "duration_beats": max(0.5, round(preview_duration, 3)),
                    "velocity": int(playable_material.get("velocity", 86) or 86),
                    "rest": False,
                },
            }
        )
    token_ids = [item["id"] for item in tokens]
    target_sequence = _safe_sequence(table.get("target_sequence"), token_ids) or token_ids
    return _contract(
        concept=concept or "歌曲乐句结构",
        focus="song_phrase_structure_match",
        tokens=tokens,
        rounds=_song_phrase_structure_rounds(target_sequence, token_ids),
        non_negotiables=[
            "乐句结构游戏必须使用当前歌曲的真实片段卡，而不是通用开头/发展占位卡。",
            "页面显示、播放和判定必须共用同一张 phrase_cards 数据表。",
            "点击片段卡时应播放整段片段，帮助学生判断相似、对比和收束关系。",
        ],
    )


def _song_phrase_rounds(sequence: list[str], token_ids: list[str]) -> list[dict[str, Any]]:
    sequence = _safe_sequence(sequence, token_ids) or token_ids[: min(4, len(token_ids))]
    lengths = [2, 4, min(6, len(sequence))]
    rounds: list[dict[str, Any]] = []
    seen_lengths: set[int] = set()
    for length in lengths:
        length = min(length, len(sequence))
        if length < 2 or length in seen_lengths:
            continue
        seen_lengths.add(length)
        rounds.append(
            {
                "id": f"round_{len(rounds) + 1}",
                "label": f"第 {len(rounds) + 1} 关",
                "target_sequence": sequence[:length],
                "prompt": "听这一小句，把唱名卡排回歌曲里的顺序。",
                "stars": len(rounds) + 1,
            }
        )
    return rounds or _rounds_from_sequence(sequence, token_ids)


def _song_phrase_expression_rounds(
    phrase_ids: list[str],
    evidence_ids: list[str],
    sequence: list[str],
) -> list[dict[str, Any]]:
    if not phrase_ids or not evidence_ids:
        return _song_phrase_rounds(sequence, sequence)
    rounds = [
        {
            "id": "round_1",
            "label": "第 1 关",
            "target_sequence": [phrase_ids[0], evidence_ids[0]],
            "prompt": "先听第一个真实片段，点击或拖拽一张表现证据卡完成配对。",
            "stars": 1,
        }
    ]
    if len(phrase_ids) >= 2:
        rounds.append(
            {
                "id": "round_2",
                "label": "第 2 关",
                "target_sequence": [phrase_ids[1], evidence_ids[min(1, len(evidence_ids) - 1)]],
                "prompt": "再比较第二个片段，判断它更适合哪种声音、情绪或动作表现。",
                "stars": 2,
            }
        )
    rounds.append(
        {
            "id": f"round_{len(rounds) + 1}",
            "label": f"第 {len(rounds) + 1} 关",
            "target_sequence": sequence,
            "prompt": "把片段卡和表现证据卡完整配对，再说出你的判断依据。",
            "stars": 3,
        }
    )
    return rounds


def _song_phrase_structure_rounds(sequence: list[str], token_ids: list[str]) -> list[dict[str, Any]]:
    sequence = _safe_sequence(sequence, token_ids) or token_ids[: min(4, len(token_ids))]
    rounds: list[dict[str, Any]] = []
    if len(sequence) >= 2:
        rounds.append(
            {
                "id": "round_1",
                "label": "第 1 关",
                "target_sequence": sequence[:2],
                "prompt": "先听两个真实片段，找出它们的对应关系。",
                "stars": 1,
            }
        )
    if len(sequence) >= 3:
        rounds.append(
            {
                "id": "round_2",
                "label": "第 2 关",
                "target_sequence": sequence[:3],
                "prompt": "加入变化片段，再判断结构是否成立。",
                "stars": 2,
            }
        )
    rounds.append(
        {
            "id": f"round_{len(rounds) + 1}",
            "label": f"第 {len(rounds) + 1} 关",
            "target_sequence": sequence,
            "prompt": "把整组真实乐句片段排完整。",
            "stars": 3,
        }
    )
    return rounds


def _song_phrase_expression_sequence(phrase_ids: list[str], evidence_ids: list[str]) -> list[str]:
    sequence: list[str] = []
    for index, phrase_id in enumerate(phrase_ids[:2]):
        sequence.append(phrase_id)
        if evidence_ids:
            sequence.append(evidence_ids[min(index, len(evidence_ids) - 1)])
    if len(sequence) >= 4:
        return sequence
    for phrase_id in phrase_ids:
        if phrase_id not in sequence:
            sequence.append(phrase_id)
    for evidence_id in evidence_ids:
        if evidence_id not in sequence:
            sequence.append(evidence_id)
    return sequence


def _pentatonic_contract(concept: str, playable_game: dict[str, Any]) -> dict[str, Any]:
    tokens = []
    for key, value in PENTATONIC_PITCHES.items():
        tokens.append(
            {
                "id": key,
                "label": value["label"],
                "symbol": value["label"],
                "display": f"{value['label']}（首调 {value['movable_do']}）",
                "music_value": value["function"],
                "scale_degree": value["scale_degree"],
                "movable_do": value["movable_do"],
                "playback": {"midi": value["midi"], "duration_beats": 1, "velocity": 84, "rest": False},
            }
        )
    token_ids = [item["id"] for item in tokens]
    target_sequence = _safe_sequence(playable_game.get("target_sequence"), token_ids) or ["gong", "shang", "jue", "zhi", "gong"]
    return _contract(
        concept=concept or "五声音阶",
        focus="pentatonic_mode",
        tokens=tokens,
        rounds=_rounds_from_sequence(target_sequence, token_ids),
        non_negotiables=[
            "五声调式游戏只能使用宫、商、角、徵、羽五个材料，不能混入七声音阶材料。",
            "显示唱名、播放音高、拼句判定必须来自 tokens 同一张表。",
        ],
    )


def _expression_contract(concept: str, source: str, playable_game: dict[str, Any]) -> dict[str, Any]:
    if _contains(source, ["速度", "快慢"]):
        raw = [
            ("slow", "慢速", "慢", 60, 1.4, 78),
            ("medium", "中速", "中", 60, 1.0, 84),
            ("fast", "快速", "快", 60, 0.65, 90),
        ]
        focus = "tempo_change"
    else:
        raw = [
            ("p", "弱 p", "轻", 60, 1.0, 52),
            ("mp", "中弱 mp", "稍轻", 60, 1.0, 68),
            ("mf", "中强 mf", "较强", 60, 1.0, 88),
            ("f", "强 f", "强", 60, 1.0, 112),
        ]
        focus = "dynamics_change"
    tokens = [
        {
            "id": token_id,
            "label": label,
            "symbol": label.split(" ")[-1] if " " in label else label,
            "display": label,
            "music_value": value,
            "playback": {"midi": midi, "duration_beats": beats, "velocity": velocity, "rest": False},
        }
        for token_id, label, value, midi, beats, velocity in raw
    ]
    token_ids = [item["id"] for item in tokens]
    target_sequence = _safe_sequence(playable_game.get("target_sequence"), token_ids) or token_ids
    return _contract(
        concept=concept or "音乐表现变化",
        focus=focus,
        tokens=tokens,
        rounds=_rounds_from_sequence(target_sequence, token_ids),
        non_negotiables=[
            "表现变化游戏必须只改变当前教学目标相关参数：力度改变 velocity，速度改变 duration。",
            "显示标签、播放参数和判定答案必须来自 tokens 同一张表。",
        ],
    )


def _generic_contract(concept: str, music_game: dict[str, Any], playable_game: dict[str, Any]) -> dict[str, Any]:
    rules = music_game.get("rules") if isinstance(music_game.get("rules"), list) else []
    tokens = []
    for index, rule in enumerate(rules[:5], start=1):
        if not isinstance(rule, dict):
            continue
        token_id = _slug(str(rule.get("music_element") or f"item_{index}")) or f"item_{index}"
        tokens.append(
            {
                "id": token_id,
                "label": str(rule.get("music_element") or f"音乐材料{index}"),
                "symbol": str(rule.get("value") or index),
                "display": f"{rule.get('music_element', f'音乐材料{index}')} {rule.get('value', '')}".strip(),
                "music_value": str(rule.get("value") or ""),
                "playback": {"midi": 60 + (index - 1) * 2, "duration_beats": 1, "velocity": 84, "rest": False},
            }
        )
    if not tokens:
        tokens = [
            {
                "id": "listen",
                "label": "先听",
                "symbol": "1",
                "display": "先听",
                "music_value": "听辨线索",
                "playback": {"midi": 60, "duration_beats": 1, "velocity": 84, "rest": False},
            },
            {
                "id": "act",
                "label": "再做",
                "symbol": "2",
                "display": "再做",
                "music_value": "操作表达",
                "playback": {"midi": 64, "duration_beats": 1, "velocity": 84, "rest": False},
            },
            {
                "id": "explain",
                "label": "说理由",
                "symbol": "3",
                "display": "说理由",
                "music_value": "音乐依据",
                "playback": {"midi": 67, "duration_beats": 1, "velocity": 84, "rest": False},
            },
        ]
    token_ids = [item["id"] for item in tokens]
    target_sequence = _safe_sequence(playable_game.get("target_sequence"), token_ids) or token_ids[:3]
    return _contract(
        concept=concept or "音乐要素",
        focus="general_music_logic",
        tokens=tokens,
        rounds=_rounds_from_sequence(target_sequence, token_ids),
        non_negotiables=[
            "页面显示、播放和判定必须共用 tokens 同一张音乐材料表。",
            "不能新增 tokens 之外的答案、角色或播放材料。",
        ],
    )


def _contract(
    *,
    concept: str,
    focus: str,
    tokens: list[dict[str, Any]],
    rounds: list[dict[str, Any]],
    non_negotiables: list[str],
) -> dict[str, Any]:
    return {
        "version": "music_logic_contract_v1",
        "knowledge_basis": [
            "note_values_and_rests",
            "meter_and_duration",
            "scale_degrees_and_movable_do",
            "pentatonic_collection",
        ],
        "concept": concept,
        "focus": focus,
        "base_unit": "quarter_note_beat",
        "meter": "4/4",
        "instrument": "acoustic_grand_piano",
        "tokens": tokens,
        "rounds": rounds,
        "validation": {
            "single_source_of_truth": True,
            "target_sequence_ids_must_exist_in_tokens": True,
            "ui_playback_scoring_must_use_tokens": True,
            "forbid_unmapped_symbols": True,
            "forbid_extra_answer_ids": True,
        },
        "non_negotiables": non_negotiables,
    }


def _align_playable_to_contract(playable_game: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    aligned = dict(playable_game)
    tokens = contract.get("tokens", []) if isinstance(contract.get("tokens"), list) else []
    token_ids = [str(item.get("id", "")).strip() for item in tokens if isinstance(item, dict)]
    material_by_id = {str(item.get("id")): item for item in aligned.get("materials", []) if isinstance(item, dict)}
    materials = []
    for token in tokens:
        token_id = str(token.get("id", "")).strip()
        existing = dict(material_by_id.get(token_id, {}))
        playback = token.get("playback", {}) if isinstance(token.get("playback"), dict) else {}
        materials.append(
            {
                **existing,
                "id": token_id,
                "label": str(token.get("label", existing.get("label", token_id))),
                "music_value": str(token.get("music_value", existing.get("music_value", ""))),
                "symbol": str(token.get("symbol", existing.get("symbol", ""))),
                "display": str(token.get("display", existing.get("display", token.get("label", token_id)))),
                "phrase_role": str(token.get("phrase_role", existing.get("phrase_role", ""))),
                "audio_clip_url": str(token.get("audio_clip_url", existing.get("audio_clip_url", ""))),
                "playback_tokens": token.get("playback_tokens", existing.get("playback_tokens", [])),
                "phrase_tokens": token.get("playback_tokens", existing.get("phrase_tokens", [])),
                "instrument": str(playback.get("instrument", token.get("instrument", existing.get("instrument", "")))),
                "pitch": int(playback.get("midi", existing.get("pitch", 60))),
                "duration": float(playback.get("duration_beats", existing.get("duration", 1))),
                "velocity": int(playback.get("velocity", existing.get("velocity", 86))),
                "rest": bool(playback.get("rest", existing.get("rest", False))),
                "feedback": str(existing.get("feedback") or token.get("display") or token.get("label") or ""),
            }
        )
    aligned["materials"] = materials
    rounds = contract.get("rounds", []) if isinstance(contract.get("rounds"), list) else []
    preserve_authored_rounds = str(aligned.get("operation_type", "")) == "melody_path_draw" and _rounds_use_known_tokens(
        aligned.get("rounds", []),
        token_ids,
    )
    if preserve_authored_rounds:
        authored_rounds = aligned.get("rounds", [])
        aligned["target_sequence"] = list(authored_rounds[0].get("target_sequence") or aligned.get("target_sequence") or [])
    elif rounds:
        aligned["target_sequence"] = list(rounds[0].get("target_sequence") or [])
        aligned["rounds"] = [
            {
                "id": item.get("id", f"round_{index + 1}"),
                "label": item.get("label", f"第 {index + 1} 关"),
                "prompt": item.get("prompt", "按音乐材料完成挑战。"),
                "target_sequence": item.get("target_sequence", []),
                "stars": item.get("stars", index + 1),
            }
            for index, item in enumerate(rounds)
        ]
    aligned["music_logic_contract_ref"] = "music_logic_contract_v1"
    aligned["allowed_material_ids"] = token_ids
    return _ensure_learning_transfer(aligned, contract)


def _rounds_use_known_tokens(rounds: Any, token_ids: list[str]) -> bool:
    if not isinstance(rounds, list) or not rounds:
        return False
    allowed = {str(item) for item in token_ids}
    for item in rounds:
        if not isinstance(item, dict):
            return False
        target_sequence = item.get("target_sequence")
        if not isinstance(target_sequence, list) or not target_sequence:
            return False
        if any(str(token_id) not in allowed for token_id in target_sequence):
            return False
    return True


def _playable_from_contract(contract: dict[str, Any]) -> dict[str, Any]:
    tokens = contract.get("tokens", []) if isinstance(contract.get("tokens"), list) else []
    rounds = contract.get("rounds", []) if isinstance(contract.get("rounds"), list) else []
    materials = []
    for token in tokens:
        if not isinstance(token, dict):
            continue
        playback = token.get("playback", {}) if isinstance(token.get("playback"), dict) else {}
        materials.append(
            {
                "id": str(token.get("id", "")),
                "label": str(token.get("label", "")),
                "music_value": str(token.get("music_value", "")),
                "symbol": str(token.get("symbol", "")),
                "display": str(token.get("display", token.get("label", ""))),
                "avatar": str(token.get("character", "")),
                "phrase_role": str(token.get("phrase_role", "")),
                "audio_clip_url": str(token.get("audio_clip_url", "")),
                "playback_tokens": token.get("playback_tokens", []),
                "phrase_tokens": token.get("playback_tokens", []),
                "instrument": str(playback.get("instrument", token.get("instrument", ""))),
                "pitch": int(playback.get("midi", 60)),
                "duration": float(playback.get("duration_beats", 1)),
                "velocity": int(playback.get("velocity", 86)),
                "rest": bool(playback.get("rest", False)),
                "feedback": str(token.get("display") or token.get("label") or ""),
            }
        )
    first_round = rounds[0] if rounds else {}
    playable = {
        "version": "playable_music_game_v1",
        "operation_type": contract.get("focus", "music_logic_game"),
        "music_goal": contract.get("concept", "音乐要素"),
        "prompt": "先试听目标，再用同一张音乐材料表完成挑战。",
        "materials": materials,
        "target_sequence": list(first_round.get("target_sequence") or []),
        "rounds": [
            {
                "id": item.get("id", f"round_{index + 1}"),
                "label": item.get("label", f"第 {index + 1} 关"),
                "prompt": item.get("prompt", "先试听目标，再完成挑战。"),
                "target_sequence": item.get("target_sequence", []),
                "stars": item.get("stars", index + 1),
            }
            for index, item in enumerate(rounds)
            if isinstance(item, dict)
        ],
        "check_rule": "exact_sequence",
        "allowed_material_ids": [str(item.get("id", "")) for item in tokens if isinstance(item, dict)],
        "playback": {
            "instrument": contract.get("instrument", "acoustic_grand_piano"),
            "seconds_per_step": 0.52,
        },
        "required_student_actions": [
            "点击“试听目标”听清目标材料。",
            "把音乐卡片拖到挑战区。",
            "点击“试听我的排列”检查声音。",
            "点击“检查挑战”获得反馈。",
        ],
        "feedback": {
            "empty": "先把音乐卡片放进挑战区。",
            "wrong": "顺序还没有体现目标音乐关系，先试听目标再调整。",
            "partial": "方向对了，继续补完整。",
            "success": "挑战成功。再说一说你的音乐判断依据。",
            "closure": "回到课堂任务：用拍、唱、说或动作再表现一次。",
        },
        "music_logic_contract_ref": contract.get("version", "music_logic_contract_v1"),
    }
    return _ensure_learning_transfer(playable, contract)


def _ensure_learning_transfer(playable_game: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    playable = dict(playable_game)
    if isinstance(playable.get("learning_transfer"), dict) and playable["learning_transfer"].get("music_evidence"):
        return playable
    concept = str(contract.get("concept") or playable.get("music_goal") or "音乐要素")
    focus = str(contract.get("focus") or playable.get("operation_type") or "")
    domain = _learning_domain_from_focus(focus, concept)
    listen_target, evidence, operation, transfer = _learning_transfer_parts(domain, concept)
    playable["learning_transfer"] = {
        "version": "learning_transfer_v1",
        "domain": domain,
        "lesson_focus": concept,
        "listen_target": listen_target,
        "music_evidence": evidence,
        "student_operation": operation,
        "classroom_transfer": transfer,
        "teacher_check": f"学生能否用音乐证据说明“{concept}”。",
        "anti_patterns": [
            "不能只显示规则文字，必须有可听、可操作、可判定的音乐材料。",
            "页面、播放和判定必须共用 music_logic_contract.tokens。",
            "通关后必须回到拍、唱、演、说或创编等课堂音乐行为。",
        ],
    }
    playable["student_facing_task"] = {
        "listen": _short_task(f"听{concept}"),
        "do": _short_task(operation),
        "pass": _short_task(transfer),
    }
    actions = [str(item) for item in playable.get("required_student_actions", []) if str(item).strip()]
    if not any(keyword in " ".join(actions) for keyword in ["拍", "唱", "演", "说", "动作", "表现", "创编", "模唱", "跟唱"]):
        actions.append(transfer)
    playable["required_student_actions"] = actions[:5]
    return playable


def _learning_domain_from_focus(focus: str, concept: str) -> str:
    source = f"{focus} {concept}"
    if _contains(source, ["rhythm", "duration", "节奏", "时值", "节拍", "切分", "附点", "休止"]):
        return "rhythm"
    if _contains(source, ["timbre", "instrument", "音色", "乐器", "管弦", "清脆", "柔和", "打击"]):
        return "timbre"
    if _contains(source, ["pitch", "melody", "sol", "mi", "唱名", "音高", "旋律", "五声", "宫", "商", "角", "徵", "羽"]):
        return "pitch"
    if _contains(source, ["phrase", "structure", "乐句", "乐段", "结构", "重复", "对比"]):
        return "phrase_structure"
    if _contains(source, ["dynamics", "tempo", "力度", "强弱", "速度", "情绪"]):
        return "expression"
    return "integrated_music"


def _learning_transfer_parts(domain: str, concept: str) -> tuple[str, list[str], str, str]:
    if domain == "rhythm":
        return (
            "目标节奏，重点听拍点、时值、重音和停顿。",
            ["答案必须体现拍点、时值、重音或休止关系。", "播放、动画时长、判定顺序必须来自同一节奏材料表。"],
            "把节奏或时值卡按听到的拍点关系摆成节奏句。",
            "通关后用拍手、踏步或念读复现这个节奏。",
        )
    if domain == "pitch":
        return (
            "目标音列，重点听具体唱名、音高顺序和旋律走向。",
            ["答案必须使用具体唱名、音级或音高材料。", "播放、卡片标签和判定答案必须来自同一音高材料表。"],
            "把具体唱名、音级或音高卡按听到的顺序摆好。",
            "通关后把音列模唱出来，并指出关键唱名。",
        )
    if domain == "phrase_structure":
        return (
            "真实乐句或乐段片段，重点听重复、对比、呼应或表现差别。",
            ["片段卡必须对应真实歌曲片段或统一旋律表。", "判断依据必须落在重复、对比、呼应、情绪或表现方式上。"],
            "把片段卡与音乐证据卡配对或排序。",
            "通关后用演唱、动作或语言表现乐句/乐段关系。",
        )
    if domain == "expression":
        return (
            "表现片段，重点听力度、速度、连断和情绪变化。",
            ["答案必须关联力度、速度、连断、情绪或音乐形象。", "学生需要通过播放比较变化前后。"],
            "根据播放中的表现变化选择并排列音乐卡。",
            "通关后用声音或动作表现音乐变化。",
        )
    if domain == "timbre":
        return (
            "音色样本，重点听明亮、柔和、短促、拨弦等发声证据。",
            ["答案必须根据音色听感判断，不能只看文字或图片。", "播放、卡片和判定必须使用同一组音色证据材料。"],
            "先听音色样本，再把音色证据卡按听到的顺序摆好。",
            "通关后说出每个判断的音色证据，并模仿或选择合适乐器表现。",
        )
    return (
        f"目标音乐材料，重点听“{concept}”。",
        [f"答案必须说得出与“{concept}”有关的音乐依据。", "游戏结果必须能迁移到课堂中的拍、唱、演、说或创编。"],
        "完成音乐材料排列、配对或选择，并说出依据。",
        "通关后用拍、唱、演、说或创编说明音乐判断。",
    )


def _short_task(text: str, limit: int = 24) -> str:
    text = str(text).strip().replace("。", "")
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _legacy_non_negotiables(contract: dict[str, Any]) -> dict[str, Any]:
    return {
        "version": contract.get("version", "music_logic_contract_v1"),
        "non_negotiables": contract.get("non_negotiables", []),
    }


def _rounds_from_sequence(sequence: list[str], token_ids: list[str], labels: list[str] | None = None) -> list[dict[str, Any]]:
    sequence = _safe_sequence(sequence, token_ids) or token_ids[: min(3, len(token_ids))]
    rounds: list[dict[str, Any]] = []
    max_rounds = 3 if len(sequence) >= 3 else 1
    for index in range(max_rounds):
        length = min(len(sequence), max(2, index + 2))
        if index == max_rounds - 1:
            length = len(sequence)
        target = sequence[:length]
        rounds.append(
            {
                "id": f"round_{index + 1}",
                "label": labels[index] if labels and index < len(labels) else f"第 {index + 1} 关",
                "target_sequence": target,
                "prompt": "先试听目标，再用同一张音乐材料表完成排列。",
                "stars": index + 1,
            }
        )
    return rounds


def _safe_sequence(value: Any, allowed_ids: list[str]) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item) in allowed_ids]


def _default_rhythm_sequence(token_ids: list[str]) -> list[str]:
    preferred = ["whole", "half", "quarter", "quarter"]
    sequence = [item for item in preferred if item in token_ids]
    return sequence or token_ids


def _characters_by_label(rules: list[Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    for rule in rules:
        if not isinstance(rule, dict):
            continue
        label = str(rule.get("music_element", "")).strip()
        character = str(rule.get("character", "")).strip()
        if label and character:
            result[label] = character
    return result


def _default_character(token_id: str) -> str:
    return {
        "whole": "慢吞吞的树懒",
        "half": "散步的大象",
        "quarter": "跳跃的兔子",
        "eighth": "敏捷的小松鼠",
    }.get(token_id, "音乐伙伴")


def _contains(text: str, keywords: list[str]) -> bool:
    normalized = str(text)
    for keyword in keywords:
        if keyword.isascii() and keyword.isalpha():
            if re.search(rf"(?<![A-Za-z]){re.escape(keyword)}(?![A-Za-z])", normalized, re.I):
                return True
            continue
        if keyword in normalized:
            return True
    return False


def _slug(text: str) -> str:
    mapping = {
        "全音符": "whole",
        "二分音符": "half",
        "四分音符": "quarter",
        "八分音符": "eighth",
        "强拍": "strong",
        "弱拍": "weak",
        "宫": "gong",
        "商": "shang",
        "角": "jue",
        "徵": "zhi",
        "羽": "yu",
    }
    if text in mapping:
        return mapping[text]
    lowered = text.strip().lower().replace(" ", "_").replace("/", "_")
    return "".join(ch for ch in lowered if ch.isalnum() or ch == "_")[:32]
