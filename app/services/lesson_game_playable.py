from __future__ import annotations

from typing import Any

from app.services.music_logic_contract import align_playable_game_to_contract, build_music_logic_contract


def attach_playable_game_to_lesson_analysis(lesson_analysis: dict[str, Any]) -> dict[str, Any]:
    enriched = dict(lesson_analysis)
    lesson_context = dict(enriched.get("lesson_context") or {})
    recommended = dict(enriched.get("recommended_game") or {})
    playable = build_playable_game(lesson_context=lesson_context, recommended_game=recommended)
    playable = ensure_phrase_expression_evidence_playable(
        playable,
        lesson_context=lesson_context,
        recommended_game=recommended,
    )
    contract = build_music_logic_contract(
        music_game={
            "enabled": True,
            "game_type": recommended.get("type") or lesson_context.get("recommended_game_type", ""),
            "music_concept": lesson_context.get("target_music_element") or recommended.get("music_element", ""),
            "rules": recommended.get("rules", []),
            "playable_game": playable,
        },
        playable_game=playable,
        lesson_context=lesson_context,
    )
    playable = align_playable_game_to_contract(playable, contract)
    recommended["playable_game"] = playable
    recommended["music_logic_contract"] = contract
    if recommended.get("name"):
        lesson_context["recommended_game_name"] = recommended["name"]
    if recommended.get("type"):
        lesson_context["recommended_game_type"] = recommended["type"]
    if recommended.get("mechanic"):
        lesson_context["recommended_game_mechanic"] = recommended["mechanic"]
    if recommended.get("rules"):
        lesson_context["recommended_game_rules"] = recommended["rules"]
    if recommended.get("student_actions"):
        lesson_context["recommended_game_actions"] = recommended["student_actions"]
    lesson_context["playable_game"] = playable
    lesson_context["music_logic_contract"] = contract
    lesson_context["musical_game_logic_contract"] = {
        "version": contract.get("version", "music_logic_contract_v1"),
        "non_negotiables": contract.get("non_negotiables", []),
    }
    lesson_context["recommended_game_objects"] = playable["materials"]
    lesson_context["recommended_game_target_sequence"] = playable["target_sequence"]
    lesson_context["recommended_game_feedback"] = playable["feedback"]
    lesson_context["learning_transfer"] = playable.get("learning_transfer", {})
    lesson_context["student_facing_task"] = playable.get("student_facing_task", {})
    enriched["recommended_game"] = recommended
    enriched["lesson_context"] = lesson_context
    return enriched


def build_playable_game(*, lesson_context: dict[str, Any], recommended_game: dict[str, Any] | None = None) -> dict[str, Any]:
    recommended_game = recommended_game or {}
    song_anchor = lesson_context.get("song_anchor_contract") if isinstance(lesson_context, dict) else {}
    if isinstance(song_anchor, dict) and song_anchor.get("selected_phrase"):
        if _is_song_phrase_structure_context(lesson_context, recommended_game):
            playable = _song_phrase_structure_playable(song_anchor, lesson_context, recommended_game)
        else:
            playable = _song_anchor_playable(song_anchor, lesson_context, recommended_game)
        return _finalize_playable_game(playable, lesson_context, recommended_game)

    target = str(
        lesson_context.get("target_music_element")
        or recommended_game.get("music_element")
        or "音乐要素"
    )
    objective = str(lesson_context.get("target_objective") or "")
    stage = str(lesson_context.get("target_stage") or "课堂核心环节")
    mechanism_id = str(
        lesson_context.get("music_element_mechanic", {}).get("mechanism_id")
        or recommended_game.get("mechanism_id")
        or lesson_context.get("recommended_game_type")
        or recommended_game.get("type")
        or ""
    )
    source = " ".join(
        [
            target,
            objective,
            stage,
            mechanism_id,
            str(lesson_context.get("target_segment_task", "")),
            str(lesson_context.get("target_segment_gameable_point", "")),
            str(recommended_game.get("mechanic", "")),
            " ".join(str(item) for item in recommended_game.get("rules", []) if str(item).strip()),
        ]
    )
    domain_hint = _domain_hint_for_game(mechanism_id, recommended_game.get("type", ""), target)

    if _is_melody_path_design(source, recommended_game):
        playable = _melody_path_draw_playable(target, objective, stage)
    elif _is_pitch_action_response(source):
        playable = _pitch_action_response_playable(target, objective, stage)
    elif domain_hint == "timbre":
        playable = _timbre_playable(target, objective, stage)
    elif domain_hint == "pentatonic":
        playable = _pentatonic_playable(target, objective, stage)
    elif domain_hint == "rhythm":
        playable = _rhythm_playable(target, objective, stage, source)
    elif domain_hint == "solmi":
        playable = _solmi_playable(target, objective, stage)
    elif domain_hint == "pitch":
        playable = _melody_playable(target, objective, stage, source)
    elif domain_hint == "phrase_structure":
        playable = _phrase_structure_playable(target, objective, stage, source)
    elif domain_hint == "expression":
        playable = _expression_playable(target, objective, stage, source)
    elif domain_hint == "singing":
        playable = _singing_playable(target, objective, stage)
    else:
        playable = _mission_playable(target, objective, stage)
    return _finalize_playable_game(playable, lesson_context, recommended_game)


def ensure_phrase_expression_evidence_playable(
    playable_game: dict[str, Any],
    *,
    lesson_context: dict[str, Any],
    recommended_game: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Ensure expression/gesture lessons do not degrade into pure note ordering."""

    recommended_game = recommended_game or {}
    if str(playable_game.get("operation_type", "")) in {
        "melody_path_draw",
        "melody_path",
        "pitch_action_response",
        "solmi_pitch_ladder",
    }:
        return playable_game
    source = " ".join(
        [
            str(playable_game.get("operation_type", "")),
            str(playable_game.get("music_goal", "")),
            str(playable_game.get("prompt", "")),
            str(lesson_context.get("target_objective", "")),
            str(lesson_context.get("lesson_evidence", "")),
            str(lesson_context.get("target_segment_task", "")),
            str(lesson_context.get("target_segment_gameable_point", "")),
            str(recommended_game.get("mechanic", "")),
            " ".join(str(item) for item in recommended_game.get("rules", []) if not isinstance(item, dict)),
        ]
    )
    if not _matches(
        source,
        ["A段", "B段", "乐段", "情绪", "声音变化", "断连", "动作", "演唱", "唱法", "温馨", "欢快", "跳跃", "连贯"],
    ):
        return playable_game

    enriched = dict(playable_game)
    materials = [dict(item) for item in enriched.get("materials", []) if isinstance(item, dict)]
    evidence_cards = [
        item
        for item in materials
        if any(
            keyword in " ".join([str(item.get("label", "")), str(item.get("music_value", "")), str(item.get("feedback", ""))])
            for keyword in ["唱", "情绪", "动作", "连贯", "跳跃", "温馨", "欢快", "对比", "重复"]
        )
    ]
    if evidence_cards:
        return enriched

    evidence_materials = _phrase_expression_evidence_materials(lesson_context, recommended_game)
    existing_ids = {str(item.get("id", "")).strip() for item in materials}
    for item in evidence_materials:
        item_id = str(item.get("id", "")).strip()
        if item_id and item_id not in existing_ids:
            materials.append(item)
            existing_ids.add(item_id)

    target_sequence = [str(item) for item in enriched.get("target_sequence", []) if str(item)]
    evidence_ids = [str(item.get("id", "")).strip() for item in evidence_materials if str(item.get("id", "")).strip()]
    if evidence_ids and not any(item in target_sequence for item in evidence_ids):
        target_sequence = [*target_sequence[: max(1, min(2, len(target_sequence)))], evidence_ids[0]]

    enriched["operation_type"] = "song_phrase_expression_match"
    enriched["materials"] = materials
    enriched["target_sequence"] = target_sequence
    enriched["check_rule"] = "exact_sequence_reusable"
    enriched["prompt"] = "先听歌曲片段，再选择能说明情绪、声音或动作表现的证据卡。"
    enriched["completion_condition"] = "学生能把歌曲片段与演唱方法、情绪或动作依据对应起来，并完成一次表现。"
    actions = [
        "点击“试听目标”听歌曲片段的情绪和声音线索。",
        "点击或拖拽片段卡与表现证据卡，组成你的判断。",
        "点击“试听我的排列”，检查听感和表现依据是否一致。",
        "点击“检查挑战”后，用声音或动作表现依据。",
    ]
    existing_actions = [str(item) for item in enriched.get("required_student_actions", []) if str(item).strip()]
    enriched["required_student_actions"] = _merge_unique_strings(actions, existing_actions)[:5]
    feedback = dict(enriched.get("feedback", {}))
    feedback.update(
        {
            "empty": "先放入歌曲片段，再选择表现证据卡。",
            "wrong": "重听片段，想一想它更连贯、跳跃、温馨还是欢快。",
            "partial": "已经找到一部分依据，继续补上表现卡。",
            "success": "配对正确。现在用声音或动作表现你的依据。",
        }
    )
    enriched["feedback"] = feedback
    enriched["rounds"] = [
        {
            "id": "round_expression",
            "label": "表现依据关",
            "prompt": "听片段，点击或拖拽一张表现证据卡。",
            "target_sequence": target_sequence,
            "stars": 2,
        }
    ]
    return enriched


def _song_anchor_playable(
    song_anchor: dict[str, Any],
    lesson_context: dict[str, Any],
    recommended_game: dict[str, Any],
) -> dict[str, Any]:
    phrase = song_anchor.get("selected_phrase", {}) if isinstance(song_anchor.get("selected_phrase"), dict) else {}
    target = str(
        lesson_context.get("target_music_element")
        or recommended_game.get("music_element")
        or "歌曲乐句"
    )
    objective = str(lesson_context.get("target_objective") or "")
    stage = str(lesson_context.get("target_stage") or "学唱环节")
    song_title = str(song_anchor.get("song_title") or lesson_context.get("song_name") or "当前歌曲")
    source_phrase_audio_url = str(phrase.get("audio_clip_url") or "")
    playback_tokens = [
        item
        for item in (phrase.get("playback_tokens") or phrase.get("main_melody") or [])
        if isinstance(item, dict)
    ]
    if source_phrase_audio_url:
        phrase_label = str(phrase.get("label") or "当前乐句")
        materials = [
            {
                **_material(
                    str(phrase.get("id") or "source_phrase"),
                    phrase_label,
                    f"{phrase_label}原音片段",
                    60,
                    max(
                        0.5,
                        round(
                            float(((phrase.get("audio_clip_range") or {}).get("end", 0.0) or 0.0))
                            - float(((phrase.get("audio_clip_range") or {}).get("start", 0.0) or 0.0)),
                            3,
                        ),
                    ),
                    f"这是《{song_title}》中的{phrase_label}真实原音。",
                    audio_clip_url=source_phrase_audio_url,
                    audio_clip_range=(phrase.get("audio_clip_range", {}) if isinstance(phrase.get("audio_clip_range"), dict) else {}),
                ),
                "source_phrase_id": phrase.get("id", ""),
                "phrase_role": "source_audio_phrase",
            }
        ]
        playable = _playable(
            "song_phrase_audio_focus",
            target,
            objective,
            stage,
            f"先听《{song_title}》{phrase_label}的真实原音，再围绕这句歌完成模唱、跟唱或课堂表达。",
            materials,
            [materials[0]["id"]],
        )
        playable["check_rule"] = "audio_reference_only"
        playable["required_student_actions"] = [
            f"点击“试听目标”听《{song_title}》{phrase_label}的真实原音。",
            "点击“试听我的排列”再次回放这句原音，确认已经记住旋律感觉。",
            "根据老师要求完成跟唱、模唱、动作表现或情绪表达。",
            "完成后回到课堂任务，说出这句歌的听感特点。",
        ]
        playable["completion_condition"] = "学生能围绕真实原音片段完成跟唱、模唱或音乐表达，不再依赖 MIDI 还原。"
        playable["feedback"] = {
            "empty": "先试听这句歌曲原音。",
            "wrong": f"先反复听《{song_title}》这句原音，再尝试完成课堂表现。",
            "partial": "已经听到这句原音了，继续完成老师要求的表现任务。",
            "success": f"这句原音已准备好。现在请直接跟唱或表现《{song_title}》这一句。",
            "closure": f"回到“{stage}”：请用这句真实原音完成“{objective or target}”。",
        }
        playable["audio_events"] = {
            "target_preview": "播放这句真实原音。",
            "student_preview": "再次播放这句真实原音。",
            "success": "保留真实原音，进入课堂表达。",
            "wrong": "提示学生重听真实原音。",
        }
        playable["playback"] = {
            "mode": "source_audio_only",
        }
    else:
        target_sequence = [
            str(item).strip()
            for item in phrase.get("target_sequence", [])
            if str(item).strip()
        ]
        if not target_sequence and playback_tokens:
            target_sequence = [str(item.get("id", "")).strip() for item in playback_tokens if str(item.get("id", "")).strip()]
        materials_by_id: dict[str, dict[str, Any]] = {}
        for token in playback_tokens:
            token_id = str(token.get("id") or "").strip()
            if not token_id or token_id in materials_by_id:
                continue
            materials_by_id[token_id] = _material(
                token_id,
                str(token.get("label") or token_id),
                str(token.get("music_value") or "歌曲真实音"),
                int(token.get("pitch", 60) or 60),
                float(token.get("duration", 0.52) or 0.52),
                str(token.get("feedback") or f"这是《{song_title}》中的真实音。"),
                velocity=int(token.get("velocity", 86) or 86),
                rest=bool(token.get("rest")),
            )
        materials = list(materials_by_id.values())
        playable = _playable(
            "song_phrase_rebuild",
            target,
            objective,
            stage,
            f"听《{song_title}》{phrase.get('label', '真实乐句')}，把唱名卡排回歌曲顺序，再跟着钢琴模唱。",
            materials,
            target_sequence,
        )
    playable["song_anchor_contract_ref"] = song_anchor.get("version", "song_anchor_contract_v1")
    playable["song_title"] = song_title
    playable["source_phrase_id"] = phrase.get("id", "")
    playable["source_phrase_label"] = phrase.get("label", "")
    playable["source_phrase_audio_url"] = source_phrase_audio_url
    playable["max_slots"] = max(len(playable.get("target_sequence", [])), 1)
    playable["song_phrase_table"] = {
        "phrase_id": phrase.get("id", ""),
        "label": phrase.get("label", ""),
        "target_sequence": playable.get("target_sequence", []),
        "playback_tokens": playback_tokens,
    }
    return playable


def _song_phrase_structure_playable(
    song_anchor: dict[str, Any],
    lesson_context: dict[str, Any],
    recommended_game: dict[str, Any],
) -> dict[str, Any]:
    target = str(
        lesson_context.get("target_music_element")
        or recommended_game.get("music_element")
        or "乐句结构"
    )
    objective = str(lesson_context.get("target_objective") or "")
    stage = str(lesson_context.get("target_stage") or "聆听与表现环节")
    song_title = str(song_anchor.get("song_title") or lesson_context.get("song_name") or "当前歌曲")
    phrases = _available_song_phrases(lesson_context, song_anchor)
    phrase_materials = _phrase_materials_from_song(phrases, song_title)
    if len(phrase_materials) < 2:
        return _song_anchor_playable(song_anchor, lesson_context, recommended_game)

    evidence_materials = _phrase_expression_evidence_materials(lesson_context, recommended_game)
    materials = [*phrase_materials, *evidence_materials]
    sequence = _song_phrase_expression_sequence(phrase_materials, evidence_materials)
    playable = _playable(
        "song_phrase_expression_match",
        target,
        objective,
        stage,
        f"先听《{song_title}》的真实片段，再把每个片段和合适的演唱、情绪或动作表现配起来。",
        materials,
        sequence,
    )
    playable["song_anchor_contract_ref"] = song_anchor.get("version", "song_anchor_contract_v1")
    playable["song_title"] = song_title
    playable["check_rule"] = "exact_sequence_reusable"
    playable["required_student_actions"] = [
        f"点击“试听目标”，听《{song_title}》两个片段的情绪和声音线索。",
        "把片段卡和表现证据卡配成一组。",
        "点击“试听我的排列”，检查先听片段、再说表现是否顺。",
        "通关后用声音或动作分别表现两个乐段，并说出依据。",
    ]
    playable["completion_condition"] = "学生能把真实歌曲片段与演唱方法、情绪或动作表现对应起来，并在通关后完成一次课堂表现。"
    playable["feedback"] = {
        "empty": "先放入一个真实片段，再选择它的表现证据。",
        "wrong": f"这个配对还没有体现《{song_title}》的听感。重听片段，判断它更跳跃还是更连贯。",
        "partial": "已经找到一部分依据，继续补上对应的表现卡。",
        "success": f"配对正确。现在请用两种声音或动作表现《{song_title}》的不同乐段。",
        "closure": f"回到“{stage}”：学生要能说明每个片段为什么这样唱或这样动。",
    }
    playable["rounds"] = _song_phrase_expression_rounds(phrase_materials, evidence_materials, sequence)
    playable["song_phrase_table"] = {
        "mode": "phrase_structure",
        "song_title": song_title,
        "target_sequence": sequence,
        "phrase_cards": [
            {
                "id": item["id"],
                "label": item["label"],
                "music_value": item["music_value"],
                "audio_clip_url": item.get("audio_clip_url", ""),
                "playback_tokens": item.get("playback_tokens", []),
            }
            for item in materials
        ],
    }
    return playable


def _rhythm_playable(target: str, objective: str, stage: str, source: str) -> dict[str, Any]:
    if "切分" in source:
        materials = [
            _material("pulse", "稳定拍", "底层节拍", 55, 0.46, "先把稳定拍找出来，切分才不会散。"),
            _material("syncopation", "切分重音", "非强拍延长", 69, 0.78, "切分的关键是重音转移到非强拍。"),
            _material("resolve", "回到强拍", "重新落稳", 60, 0.46, "回到强拍后，节奏句才完整。"),
        ]
        sequence = ["pulse", "syncopation", "resolve"]
        prompt = "先试听目标节奏，再把“稳定拍-切分重音-回到强拍”排出来。"
    elif "附点" in source:
        materials = [
            _material("long", "长音值", "附点前半", 62, 0.78, "附点节奏先长，不能抢。"),
            _material("short", "短音值", "后接短音", 67, 0.22, "短音要紧接出现，形成弹性。"),
            _material("steady", "稳定落点", "回到拍点", 60, 0.42, "最后要落稳拍点。"),
        ]
        sequence = ["long", "short", "steady"]
        prompt = "把附点节奏的“先长后短”排清楚，再播放验证。"
    elif "休止" in source:
        materials = [
            _material("sound", "有声拍", "发声", 64, 0.38, "有声处要准确发出。"),
            _material("rest", "休止拍", "停顿", 48, 0.08, "休止不是空白，也有时值。", rest=True),
            _material("sound2", "再发声", "继续节奏", 67, 0.38, "停顿后要能重新接上。"),
        ]
        sequence = ["sound", "rest", "sound2"]
        prompt = "把有声和休止放到正确位置，听一听停顿是否还保留时值。"
    elif any(keyword in source for keyword in ["时值", "全音符", "二分音符", "四分音符", "八分音符", "十六分音符"]):
        materials = [
            _material("whole", "全音符", "4 拍", 48, 1.6, "全音符要保持 4 拍，角色跑得最慢。"),
            _material("half", "二分音符", "2 拍", 55, 0.9, "二分音符保持 2 拍，速度居中。"),
            _material("quarter", "四分音符", "1 拍", 60, 0.46, "四分音符 1 拍一下，像稳定脚步。"),
            _material("eighth", "八分音符", "半拍", 67, 0.24, "八分音符更短，像轻快小跑。"),
        ]
        sequence = ["quarter", "quarter", "half", "whole"]
        prompt = "拖拽不同时值角色组成节奏句，播放时听它们跑过屏幕的长短。"
    else:
        materials = [
            _material("strong", "强拍", "重一点", 60, 0.46, "强拍要稳，给节奏句支点。"),
            _material("weak", "弱拍", "轻一点", 64, 0.36, "弱拍要轻，不能盖过强拍。"),
            _material("move", "动作拍", "接着走", 67, 0.36, "动作拍帮助学生保持律动。"),
        ]
        sequence = ["strong", "weak", "weak", "strong"]
        prompt = "按强弱关系排列节奏卡，播放后跟着拍一遍。"
    return _playable("rhythm_sequence", target, objective, stage, prompt, materials, sequence)


def _melody_playable(target: str, objective: str, stage: str, source: str) -> dict[str, Any]:
    materials = [
        _material("up", "上行", "音高升高", 64, 0.42, "听到旋律往高处走，就选上行。"),
        _material("down", "下行", "音高降低", 60, 0.42, "听到旋律往低处走，就选下行。"),
        _material("same", "保持", "重复音", 62, 0.42, "重复音要停在同一层。"),
    ]
    if "跳进" in source:
        materials.append(_material("leap", "跳进", "跨得更远", 72, 0.42, "跳进跨度更大，听感更明显。"))
        sequence = ["same", "leap", "down"]
    elif "级进" in source:
        materials.append(_material("step", "级进", "相邻移动", 67, 0.42, "级进像一步一步走。"))
        sequence = ["step", "step", "down"]
    else:
        sequence = ["up", "same", "down"]
    return _playable("melody_path", target, objective, stage, "听目标旋律，选择它的走向，再播放检查路线是否一致。", materials, sequence)


def _melody_path_draw_playable(target: str, objective: str, stage: str) -> dict[str, Any]:
    materials = [
        _material("do", "do", "首调第1级", 60, 1.0, "起点音，先把耳朵安稳下来。"),
        _material("re", "re", "首调第2级", 62, 1.0, "音高向上移动一级。"),
        _material("mi", "mi", "首调第3级", 64, 1.0, "旋律继续抬高。"),
        _material("sol", "sol", "首调第5级", 67, 1.0, "较高音，注意听它和前面音的距离。"),
    ]
    playable = _playable(
        "melody_path_draw",
        target,
        objective,
        stage,
        "先听目标旋律，再在格子图里画出它的高低路线，让小角色沿着你的路线前进。",
        materials,
        ["do", "re", "mi", "re"],
    )
    playable["check_rule"] = "exact_path"
    playable["required_student_actions"] = [
        "点击“听乐句”听清旋律是怎样起伏的。",
        "在每一列格子里点出一个位置，画出你听到的高低路线。",
        "点击“播放我的路线”核对自己的旋律线。",
        "点击“检查路线”获得反馈，必要时重听并重画。",
        f"通关后回到“{stage}”，把旋律线用手势或模唱表现出来。",
    ]
    playable["completion_condition"] = "学生画出的旋律路线与目标音高走向一致，并能回到课堂任务用手势或模唱表现旋律线。"
    playable["ui_contract"]["must_have_controls"] = ["听乐句", "播放我的路线", "检查路线", "重画"]
    playable["ui_contract"]["must_have_regions"] = ["路线格子", "本关任务", "即时反馈", "音乐依据"]
    playable["feedback"] = {
        "empty": "先在每一列点出一个格子，画出你听到的路线。",
        "wrong": "这条路线还没有贴合旋律起伏。再听一遍，注意哪里上行、哪里回落。",
        "partial": "前半段已经对了，继续把后面的走向补完整。",
        "success": f"路线找对了。现在请回到“{stage}”，用手势或模唱表现“{target}”。",
        "closure": f"这条旋律线怎样帮助你理解“{objective or target}”？",
    }
    playable["rounds"] = [
        {
            "id": "round_1",
            "label": "第 1 关",
            "prompt": "先听四个音，再画出上行后回落的路线。",
            "target_sequence": ["do", "re", "mi", "re"],
            "stars": 1,
        },
        {
            "id": "round_2",
            "label": "第 2 关",
            "prompt": "这一次听更远的高点，路线会抬得更高。",
            "target_sequence": ["do", "mi", "sol", "mi"],
            "stars": 2,
        },
        {
            "id": "round_3",
            "label": "第 3 关",
            "prompt": "辨认先高后低再回升的旋律线。",
            "target_sequence": ["sol", "mi", "re", "mi"],
            "stars": 3,
        },
    ]
    return playable


def _solmi_playable(target: str, objective: str, stage: str) -> dict[str, Any]:
    materials = [
        _material("sol", "sol", "较高的唱名", 67, 0.58, "sol 是较高的唱名卡。", avatar="小太阳", icon="sun"),
        _material("mi", "mi", "较低的唱名", 64, 0.58, "mi 是较低的唱名卡。", avatar="小叶子", icon="leaf"),
    ]
    rounds = [
        {
            "id": "round_1",
            "label": "第 1 关",
            "prompt": "先听 2 个音，把它们摆成正确的 sol / mi 顺序。",
            "target_sequence": ["sol", "mi"],
            "stars": 1,
        },
        {
            "id": "round_2",
            "label": "第 2 关",
            "prompt": "这次有 3 个音，别急着拖，先完整听一遍。",
            "target_sequence": ["mi", "sol", "mi"],
            "stars": 2,
        },
        {
            "id": "round_3",
            "label": "第 3 关",
            "prompt": "第 3 关更长了，听完再一次摆满全部台阶。",
            "target_sequence": ["sol", "mi", "sol", "sol"],
            "stars": 3,
        },
        {
            "id": "round_4",
            "label": "第 4 关",
            "prompt": "终极关有 5 个音，摆对后马上模唱。",
            "target_sequence": ["mi", "sol", "sol", "mi", "sol"],
            "stars": 4,
        },
    ]
    playable = _playable(
        "solmi_pitch_ladder",
        target,
        objective,
        stage,
        "听目标音列，把具体的 sol / mi 唱名卡拖到台阶上。",
        materials,
        rounds[0]["target_sequence"],
    )
    playable["rounds"] = rounds
    playable["lives"] = 3
    playable["age_style"] = "lower_primary_cartoon"
    playable["max_slots"] = 5
    playable["required_student_actions"] = [
        "点击“试听目标”听清这一关的具体音列。",
        "把 sol 和 mi 唱名卡拖到台阶上，还原顺序。",
        "点击“试听我的排列”听一听自己摆出的音列。",
        "点击“检查挑战”闯关，通过后立刻模唱。",
    ]
    playable["audio_events"] = {
        "target_preview": "按当前关卡 target_sequence 播放目标音列。",
        "student_preview": "按学生当前排列播放音列。",
        "success": "播放明亮奖励音型，并进入下一关。",
        "wrong": "播放提示音，扣除 1 颗心，保留本关继续挑战。",
    }
    playable["playback"] = {
        "instrument": "acoustic_grand_piano",
        "seconds_per_step": 0.48,
    }
    playable["feedback"] = {
        "empty": "先把 sol / mi 唱名卡放到台阶上。",
        "wrong": "顺序不对，再听一遍目标音列。",
        "partial": "还没摆满全部台阶。",
        "success": "过关，进入下一关。",
        "closure": f"全部通关。回到“{stage}”：现在把这条 sol-mi 音列模唱出来。",
    }
    return playable


def _pitch_action_response_playable(target: str, objective: str, stage: str) -> dict[str, Any]:
    materials = [
        _material("sol", "sol", "举高 / 站起", 67, 0.58, "听到 sol，做高位动作并模唱 sol。", avatar="高位动作", icon="up"),
        _material("mi", "mi", "放低 / 蹲下", 64, 0.58, "听到 mi，做低位动作并模唱 mi。", avatar="低位动作", icon="down"),
    ]
    rounds = [
        {
            "id": "round_1",
            "label": "第 1 轮",
            "prompt": "听到 sol 举高，听到 mi 放低。",
            "target_sequence": ["sol", "mi"],
            "stars": 1,
        },
        {
            "id": "round_2",
            "label": "第 2 轮",
            "prompt": "跟着音高快速切换动作。",
            "target_sequence": ["mi", "sol", "mi"],
            "stars": 2,
        },
        {
            "id": "round_3",
            "label": "第 3 轮",
            "prompt": "边听边做动作，最后把音列模唱出来。",
            "target_sequence": ["sol", "mi", "sol"],
            "stars": 3,
        },
    ]
    playable = _playable(
        "pitch_action_response",
        target,
        objective,
        stage,
        "听 sol / mi，点击对应动作按钮，再跟着模唱。",
        materials,
        rounds[0]["target_sequence"],
    )
    playable["rounds"] = rounds
    playable["check_rule"] = "action_sequence"
    playable["required_student_actions"] = [
        "点击“试听目标”听清 sol / mi。",
        "听到 sol 就点击高位动作，听到 mi 就点击低位动作。",
        "跟随反馈调整动作速度。",
        "通关后边做动作边模唱这一组 sol / mi。",
    ]
    playable["audio_events"] = {
        "target_preview": "按当前轮次播放 sol / mi 目标音列。",
        "student_preview": "播放学生点击出的动作音列。",
        "success": "播放奖励音，并提示学生模唱。",
        "wrong": "播放提示音，保留本轮继续练。",
    }
    playable["feedback"] = {
        "empty": "先听目标，再点击高位或低位动作。",
        "wrong": "动作和音高还没对上，再听一次。",
        "partial": "已经跟上了一部分，继续听下一个音。",
        "success": "动作对上了。现在边做动作边模唱。",
        "closure": f"回到“{stage}”：不用看按钮，也能听准 sol / mi 并唱出来。",
    }
    playable["ui_contract"] = {
        **dict(playable.get("ui_contract", {})),
        "must_have_controls": ["试听目标", "高位动作", "低位动作", "重来"],
        "must_have_regions": ["动作按钮", "目标音列", "即时反馈", "本关任务"],
    }
    return playable


def _timbre_playable(target: str, objective: str, stage: str) -> dict[str, Any]:
    materials = [
        _material("bright", "明亮音色", "清脆/穿透", 76, 0.38, "明亮音色通常更清脆、有穿透感。"),
        _material("soft", "柔和音色", "圆润/连贯", 64, 0.68, "柔和音色更圆润，线条更连贯。"),
        _material("percussive", "打击音色", "短促/颗粒", 48, 0.14, "打击音色短促，有颗粒感。"),
    ]
    return _playable("timbre_match", target, objective, stage, "先试听三种声音线索，再把音色证据按听到的顺序排好。", materials, ["percussive", "bright", "soft"])


def _pentatonic_playable(target: str, objective: str, stage: str) -> dict[str, Any]:
    materials = [
        _material("gong", "宫", "稳定起点", 60, 0.42, "宫音常带来稳定感。"),
        _material("shang", "商", "向前发展", 62, 0.42, "商音让旋律继续向前。"),
        _material("jue", "角", "柔和色彩", 64, 0.42, "角音让短句更有民族色彩。"),
        _material("zhi", "徵", "明亮支点", 67, 0.42, "徵音听起来明亮、有支撑。"),
        _material("yu", "羽", "收束色彩", 69, 0.42, "羽音可以形成不同的收束感。"),
    ]
    return _playable("pentatonic_phrase", target, objective, stage, "只用五声音级拼出短句，播放后判断民族风格是否清楚。", materials, ["gong", "shang", "jue", "zhi", "gong"])


def _phrase_structure_playable(target: str, objective: str, stage: str, source: str) -> dict[str, Any]:
    materials = [
        _material(
            "a_phrase",
            "A乐段",
            "快乐、轻巧的乐句",
            64,
            0.56,
            "A乐段通常先呈现主要情绪或主题，要听它的起始特点。",
            avatar="月亮船",
            icon="moon",
        ),
        _material(
            "a_repeat",
            "A乐段重复",
            "相似乐句再次出现",
            64,
            0.56,
            "重复或相似乐句会让学生听到熟悉感。",
            avatar="小月饼",
            icon="cake",
        ),
        _material(
            "b_phrase",
            "B乐段",
            "温馨、连贯的对比乐句",
            69,
            0.72,
            "B乐段要和A乐段比较，听它的情绪、旋律线或表现方式是否变化。",
            avatar="兔儿爷",
            icon="rabbit",
        ),
        _material(
            "closure",
            "收束乐句",
            "回到完整歌曲",
            60,
            0.64,
            "收束乐句帮助歌曲落稳，最后要回到演唱或动作表现。",
            avatar="团圆灯",
            icon="lantern",
        ),
    ]
    if "问答" in source or "呼应" in source:
        operation = "phrase_call_response_match"
        prompt = "先听乐句线索，把呼应或相似的乐句配成一组，再拼回歌曲结构。"
        sequence = ["a_phrase", "a_repeat", "b_phrase", "closure"]
    elif "对比" in source or "A" in source or "B" in source or "乐段" in source:
        operation = "section_contrast_order"
        prompt = "听A、B两个乐段的情绪和表现差别，把歌曲结构按顺序排出来。"
        sequence = ["a_phrase", "a_repeat", "b_phrase", "closure"]
    else:
        operation = "phrase_structure_order"
        prompt = "听乐句之间的重复、对比和收束关系，把歌曲结构排完整。"
        sequence = ["a_phrase", "a_repeat", "b_phrase", "closure"]
    playable = _playable(operation, target, objective, stage, prompt, materials, sequence)
    playable["check_rule"] = "exact_sequence_reusable"
    playable["rounds"] = [
        {
            "id": "round_1",
            "label": "第 1 关",
            "prompt": "找出两个相似或重复的乐句。",
            "target_sequence": ["a_phrase", "a_repeat"],
            "stars": 1,
        },
        {
            "id": "round_2",
            "label": "第 2 关",
            "prompt": "比较A、B乐段的情绪和表现差别。",
            "target_sequence": ["a_phrase", "b_phrase"],
            "stars": 2,
        },
        {
            "id": "round_3",
            "label": "第 3 关",
            "prompt": "把歌曲结构完整拼回去，完成后用动作或演唱表现。",
            "target_sequence": sequence,
            "stars": 3,
        },
    ]
    playable["required_student_actions"] = [
        "点击“试听目标”听乐句线索。",
        "把A乐段、重复乐句、B乐段和收束乐句拖到挑战区。",
        "点击“试听我的排列”检查结构是否顺。",
        "通关后说出A、B乐段哪里不同，并用演唱或动作表现。",
    ]
    playable["completion_condition"] = "学生能按乐句重复、对比和收束关系拼出歌曲结构，并说明音乐依据。"
    playable["feedback"] = {
        "empty": "先把乐句卡片放进挑战区。",
        "wrong": "结构还不顺。先找相似乐句，再比较A、B乐段。",
        "partial": "已经找到一部分关系，继续补完整。",
        "success": f"结构拼对了。现在请回到“{stage}”，用唱或动作表现两个乐段的不同。",
        "closure": f"这个排列怎样帮助你理解“{objective or target}”？",
    }
    playable["playback"] = {
        "instrument": "acoustic_grand_piano",
        "seconds_per_step": 0.58,
    }
    return playable


def _expression_playable(target: str, objective: str, stage: str, source: str) -> dict[str, Any]:
    if "速度" in source:
        materials = [
            _material("slow", "慢速", "沉稳", 55, 0.78, "慢速要稳，不是散。"),
            _material("medium", "中速", "行进", 62, 0.48, "中速适合稳定表现。"),
            _material("fast", "快速", "紧张/活泼", 72, 0.25, "快速要清楚，不要乱。"),
        ]
        sequence = ["slow", "medium", "fast"]
        prompt = "按音乐形象选择速度变化，听听情绪是否被推动。"
    elif _is_binary_dynamic_contrast(source):
        materials = [
            _material("f", "强 f", "声音有力", 67, 0.48, "强要有支撑，可以用大动作表现。", velocity=112),
            _material("p", "弱 p", "声音轻柔", 60, 0.48, "弱要轻柔，但节拍不能散。", velocity=54),
        ]
        sequence = ["f", "p", "f", "p"]
        prompt = "听四次声音，判断每次是强 f 还是弱 p，再用动作表现强弱对比。"
    else:
        materials = [
            _material("p", "弱 p", "轻柔", 60, 0.48, "弱要轻，但节拍不能丢。", velocity=54),
            _material("mp", "中弱 mp", "稍增强", 62, 0.48, "中弱让声音慢慢靠近。", velocity=68),
            _material("mf", "中强 mf", "更饱满", 64, 0.48, "中强开始有推动力。", velocity=88),
            _material("f", "强 f", "有力", 67, 0.58, "强要有力，但不喊叫。", velocity=112),
        ]
        sequence = ["p", "mp", "mf", "f"]
        prompt = "把力度从弱到强排成变化线，播放后说出音乐形象怎样变化。"
    operation = "dynamic_contrast_choice" if _is_binary_dynamic_contrast(source) else "expression_control"
    playable = _playable(operation, target, objective, stage, prompt, materials, sequence)
    if operation == "dynamic_contrast_choice":
        playable["check_rule"] = "exact_sequence_reusable"
        playable["feedback"]["wrong"] = "这里只判断强 f 和弱 p，不需要加入 mp、mf。先听声音大小，再调整顺序。"
        playable["feedback"]["success"] = f"强弱听辨成功。现在请用大动作/小动作表现“{target}”。"
    return playable


def _singing_playable(target: str, objective: str, stage: str) -> dict[str, Any]:
    materials = [
        _material("breath", "换气点", "先吸气", 60, 0.3, "先找换气点，乐句才连贯。"),
        _material("phrase", "连贯乐句", "唱完整", 64, 0.78, "乐句要连起来，不要一个字一个字断开。"),
        _material("expression", "情绪提示", "带表情", 67, 0.58, "演唱要回到歌曲情绪。"),
    ]
    return _playable("singing_ladder", target, objective, stage, "把演唱表现步骤排成顺序，再跟着提示唱一遍。", materials, ["breath", "phrase", "expression"])


def _mission_playable(target: str, objective: str, stage: str) -> dict[str, Any]:
    materials = [
        _material("listen", "先听", "抓住线索", 60, 0.38, f"先听出“{target}”。"),
        _material("act", "再操作", "完成挑战", 64, 0.38, "操作必须对应音乐行为。"),
        _material("explain", "说理由", "课堂表达", 67, 0.5, "最后说出音乐依据。"),
    ]
    return _playable("lesson_mission", target, objective, stage, "按“先听-操作-说理由”的顺序完成任务。", materials, ["listen", "act", "explain"])


def _playable(
    operation_type: str,
    target: str,
    objective: str,
    stage: str,
    prompt: str,
    materials: list[dict[str, Any]],
    target_sequence: list[str],
) -> dict[str, Any]:
    return {
        "version": "playable_music_game_v1",
        "operation_type": operation_type,
        "music_goal": target,
        "lesson_objective": objective,
        "target_stage": stage,
        "prompt": prompt,
        "materials": materials,
        "target_sequence": target_sequence,
        "check_rule": "exact_sequence",
        "required_student_actions": [
            "点击“试听目标”听清本课音乐要素。",
            "点击或拖拽音乐卡片到挑战区完成排列。",
            "点击“试听我的排列”进行听觉验证。",
            "点击“检查挑战”获得即时反馈，再用拍、唱、说或动作完成课堂表达。",
        ],
        "completion_condition": "目标序列与学生排列完全一致，并能说出与本课音乐要素相关的理由。",
        "playback": {
            "instrument": "acoustic_grand_piano",
            "seconds_per_step": 0.52,
        },
        "audio_events": {
            "target_preview": "按 target_sequence 播放目标声音。",
            "student_preview": "按学生挑战区顺序播放声音。",
            "success": "播放上行奖励音型，并高亮正确序列。",
            "wrong": "播放温和提示音，并保留学生答案方便修改。",
        },
        "ui_contract": {
            "must_have_controls": ["试听目标", "试听我的排列", "检查挑战", "重来"],
            "must_have_regions": ["音乐卡片", "挑战区", "即时反馈"],
            "forbidden_student_text": ["是否服务于", "是否真正聚焦", "不是泛泛", "脱离教案"],
        },
        "feedback": {
            "empty": "先把音乐卡片放进挑战区。",
            "wrong": f"顺序还没有体现“{target}”的音乐关系，先试听目标再调整。",
            "partial": "方向对了，继续补完整。",
            "success": f"挑战成功。现在请用拍、唱、说或动作再表现一次“{target}”。",
            "closure": f"回到“{stage}”：这个游戏结果怎样帮助你完成“{objective or target}”？",
        },
    }


def _finalize_playable_game(
    playable: dict[str, Any],
    lesson_context: dict[str, Any],
    recommended_game: dict[str, Any],
) -> dict[str, Any]:
    """Attach a general learning loop so games stay educational across lesson types."""

    target = str(
        playable.get("music_goal")
        or lesson_context.get("target_music_element")
        or recommended_game.get("music_element")
        or "音乐要素"
    )
    objective = str(playable.get("lesson_objective") or lesson_context.get("target_objective") or "")
    stage = str(playable.get("target_stage") or lesson_context.get("target_stage") or "课堂活动")
    domain = _learning_domain(playable, lesson_context, recommended_game)
    listen_target = _listen_target_for_domain(domain, playable, lesson_context)
    evidence_rules = _evidence_rules_for_domain(domain, target, playable, lesson_context)
    operation = _student_operation_for_domain(domain, playable)
    transfer_action = _transfer_action_for_domain(domain, target, objective, stage, lesson_context)
    teacher_check = _teacher_check_for_domain(domain, target)

    learning_transfer = {
        "version": "learning_transfer_v1",
        "domain": domain,
        "lesson_focus": target,
        "source_stage": stage,
        "listen_target": listen_target,
        "music_evidence": evidence_rules,
        "student_operation": operation,
        "classroom_transfer": transfer_action,
        "teacher_check": teacher_check,
        "anti_patterns": [
            "不能只把规则文字放到网页上，必须让学生真实听、拖、选、判定或创编。",
            "不能用和本课无关的卡片、音符、动物或答案替代教案中的音乐材料。",
            "不能让游戏通关停在得分，必须回到拍、唱、演、说或创编的课堂任务。",
        ],
    }
    playable["learning_transfer"] = learning_transfer
    playable["pedagogical_contract"] = {
        "version": "pedagogical_game_contract_v1",
        "must_answer": ["学生听什么", "学生根据什么音乐证据判断", "学生操作后迁移到什么课堂表现"],
        "learning_loop": [
            f"听：{listen_target}",
            f"辨：{evidence_rules[0] if evidence_rules else target}",
            f"做：{operation}",
            f"用：{transfer_action}",
        ],
    }
    playable["student_facing_task"] = {
        "listen": _student_task_listen(domain, playable, lesson_context),
        "do": _short_task_text(operation),
        "pass": _short_task_text(transfer_action),
    }

    existing_actions = [
        str(item)
        for item in playable.get("required_student_actions", [])
        if str(item).strip()
    ]
    if not existing_actions:
        existing_actions = [
            f"试听目标，听清“{target}”。",
            operation,
            "试听自己的答案并检查挑战。",
        ]
    if not any(_contains_learning_transfer_word(item) for item in existing_actions):
        existing_actions.append(transfer_action)
    playable["required_student_actions"] = existing_actions[:5]

    completion = str(playable.get("completion_condition") or "")
    if not _contains_learning_transfer_word(completion):
        playable["completion_condition"] = (
            f"{completion.rstrip('。')}，并完成课堂迁移：{transfer_action}"
            if completion
            else f"学生完成音乐判断后，能完成课堂迁移：{transfer_action}"
        )

    ui_contract = playable.setdefault("ui_contract", {})
    regions = list(ui_contract.get("must_have_regions", [])) if isinstance(ui_contract.get("must_have_regions"), list) else []
    for region in ["本关任务", "音乐依据", "即时反馈"]:
        if region not in regions:
            regions.append(region)
    ui_contract["must_have_regions"] = regions[:6]

    for material in playable.get("materials", []):
        if not isinstance(material, dict):
            continue
        material.setdefault("evidence_role", _material_evidence_role(material, domain))
        material.setdefault("teaching_role", _material_teaching_role(material, domain))
    return playable


def _learning_domain(
    playable: dict[str, Any],
    lesson_context: dict[str, Any],
    recommended_game: dict[str, Any],
) -> str:
    domain_hint = _domain_hint_for_game(
        str(
            lesson_context.get("music_element_mechanic", {}).get("mechanism_id")
            or recommended_game.get("mechanism_id")
            or lesson_context.get("recommended_game_type")
            or recommended_game.get("type")
            or playable.get("operation_type")
            or ""
        ),
        str(recommended_game.get("type", "")),
        str(playable.get("music_goal") or lesson_context.get("target_music_element") or recommended_game.get("music_element") or ""),
    )
    if domain_hint == "solmi":
        return "pitch"
    if domain_hint in {"timbre", "pentatonic", "rhythm", "pitch", "phrase_structure", "expression", "singing", "creation"}:
        return domain_hint

    source = " ".join(
        [
            str(playable.get("operation_type", "")),
            str(playable.get("music_goal", "")),
            str(playable.get("prompt", "")),
            str(lesson_context.get("target_music_element", "")),
            str(lesson_context.get("target_objective", "")),
            str(lesson_context.get("target_segment_task", "")),
            str(lesson_context.get("target_segment_gameable_point", "")),
            str(recommended_game.get("mechanic", "")),
            str(recommended_game.get("type", "")),
        ]
    )
    if _matches(source, ["音色", "乐器", "管弦", "民族乐器", "timbre"]):
        return "timbre"
    if _matches(source, ["五声", "宫", "商", "角", "徵", "羽", "调式", "民族"]):
        return "pentatonic"
    if _matches(source, ["song_phrase", "乐句", "乐段", "段落", "结构", "重复", "对比", "呼应", "问答", "phrase", "section"]):
        return "phrase_structure"
    if _matches(source, ["切分", "附点", "休止", "节奏", "节拍", "拍点", "时值", "rhythm"]):
        return "rhythm"
    if _matches(source, ["sol", "mi", "do", "re", "la", "唱名", "音高", "旋律", "级进", "跳进", "pitch", "melody"]):
        return "pitch"
    if _matches(source, ["力度", "强弱", "渐强", "渐弱", "速度", "快慢", "情绪", "形象"]):
        return "expression"
    if _matches(source, ["演唱", "歌唱", "咬字", "气息", "跟唱", "模唱"]):
        return "singing"
    if _matches(source, ["创作", "创编", "作曲", "拼图", "旋律线", "creation"]):
        return "creation"
    return "integrated_music"


def _domain_hint_for_game(mechanism_id: str, game_type: str, target: str) -> str:
    source = " ".join([str(mechanism_id or ""), str(game_type or ""), str(target or "")])
    if _matches(source, ["timbre", "音色", "乐器", "管弦", "民族乐器"]):
        return "timbre"
    if _matches(source, ["pentatonic", "mode", "五声", "宫", "商", "角", "徵", "羽", "调式", "民族"]):
        return "pentatonic"
    if _matches(source, ["rhythm", "meter_gate", "节奏", "节拍", "拍子", "强拍", "弱拍", "拍点", "时值", "切分", "附点", "休止"]):
        return "rhythm"
    if _matches(source, ["solmi", "sol", "mi", "唱名", "5音", "3音"]):
        return "solmi"
    if _matches(source, ["pitch", "melody", "旋律", "音高", "上行", "下行", "级进", "跳进"]):
        return "pitch"
    if _matches(source, ["phrase", "section", "乐句", "乐段", "段落", "重复", "对比", "呼应", "问答", "结构"]):
        return "phrase_structure"
    if _matches(source, ["expression", "dynamic", "tempo", "力度", "强弱", "渐强", "渐弱", "速度", "快慢", "情绪", "形象"]):
        return "expression"
    if _matches(source, ["sing", "singing", "演唱", "歌唱", "咬字", "气息", "跟唱", "模唱"]):
        return "singing"
    if _matches(source, ["creation", "creative", "创作", "创编", "作曲", "拼图"]):
        return "creation"
    return ""


def _is_pitch_action_response(source: str) -> bool:
    return _matches(source, ["sol", "mi", "唱名", "音高"]) and _matches(
        source,
        ["举手", "举高", "站起", "站立", "蹲下", "手放低", "放低", "身体动作", "肢体动作", "动作响应", "实时响应"],
    )


def _is_melody_path_design(source: str, recommended_game: dict[str, Any]) -> bool:
    combined = " ".join(
        [
            source,
            str(recommended_game.get("type", "")),
            str(recommended_game.get("mechanic", "")),
            " ".join(str(item) for item in recommended_game.get("rules", []) if str(item).strip()),
            " ".join(str(item) for item in recommended_game.get("student_actions", []) if str(item).strip()),
        ]
    )
    return _matches(
        combined,
        [
            "melody_path_game",
            "melody_path_builder",
            "旋律爬坡",
            "旋律路线",
            "旋律线",
            "格子图",
            "画出",
            "路线",
            "连线",
        ],
    ) and _matches(combined, ["旋律", "上行", "下行", "高低"])


def _listen_target_for_domain(domain: str, playable: dict[str, Any], lesson_context: dict[str, Any]) -> str:
    song_title = str(
        playable.get("song_title")
        or lesson_context.get("song_name")
        or (lesson_context.get("song_anchor_contract") or {}).get("song_title", "")
    )
    song_prefix = f"《{song_title}》的" if song_title else ""
    if domain == "phrase_structure":
        return f"{song_prefix}真实乐句或乐段片段，重点听重复、对比、呼应、情绪或表现差别。"
    if domain == "rhythm":
        return f"{song_prefix}目标节奏，重点听拍点、时值、重音和停顿位置。"
    if domain == "pitch":
        return f"{song_prefix}目标音列，重点听具体唱名、音高顺序和旋律走向。"
    if domain == "pentatonic":
        return f"{song_prefix}五声音级短句，重点听宫、商、角、徵、羽的稳定感和民族风格。"
    if domain == "timbre":
        return f"{song_prefix}声音样本，重点听明亮、柔和、颗粒、延展等音色证据。"
    if domain == "expression":
        return f"{song_prefix}表现片段，重点听力度、速度、连断和情绪变化。"
    if domain == "singing":
        return f"{song_prefix}演唱示范，重点听换气、连贯、咬字和情绪表达。"
    if domain == "creation":
        return "本课已学的音乐材料，重点听它们怎样组成一个有目标的短句。"
    return f"{song_prefix}音乐线索，先听清楚再操作。"


def _evidence_rules_for_domain(
    domain: str,
    target: str,
    playable: dict[str, Any],
    lesson_context: dict[str, Any],
) -> list[str]:
    lesson_evidence = str(lesson_context.get("lesson_evidence") or "").strip()
    evidence_suffix = f" 教案依据：{lesson_evidence}" if lesson_evidence else ""
    if domain == "phrase_structure":
        return [
            f"每张片段卡必须对应真实歌曲片段或统一旋律表，不能只用文字代替音乐。{evidence_suffix}".strip(),
            "判断依据必须落在重复、对比、呼应、乐段情绪、演唱方法或动作表现上。",
        ]
    if domain == "rhythm":
        return [
            f"答案必须体现拍点、时值、重音或休止关系，而不是只按角色好看排序。{evidence_suffix}".strip(),
            "播放、动画时长、判定顺序必须来自同一节奏材料表。",
        ]
    if domain == "pitch":
        return [
            f"答案必须使用具体唱名、音级或音高材料，不能只用“上行、下行、保持”代替具体音。{evidence_suffix}".strip(),
            "播放、卡片标签和判定答案必须来自同一音高材料表。",
        ]
    if domain == "pentatonic":
        return [
            f"答案必须围绕五声音级或民族调式风格判断，不能退回通用上行/下行旋律卡。{evidence_suffix}".strip(),
            "播放、卡片标签和判定答案必须使用同一组宫、商、角、徵、羽材料。",
        ]
    if domain == "timbre":
        return [
            f"答案必须让学生根据音色听感判断，如明亮、柔和、颗粒、延展或乐器家族。{evidence_suffix}".strip(),
            "图像只能辅助，判定必须以可听声音样本为核心。",
        ]
    if domain == "expression":
        return [
            f"答案必须关联力度、速度、连断、情绪或音乐形象的变化。{evidence_suffix}".strip(),
            "学生需要通过播放比较变化前后，而不是只看文字选择。",
        ]
    if domain == "singing":
        return [
            f"答案必须服务演唱任务，如换气、连贯、咬字、音准或情绪表达。{evidence_suffix}".strip(),
            "通关后必须回到模唱、跟唱或分句演唱。",
        ]
    if domain == "creation":
        return [
            f"创作限制必须来自本课音乐要素“{target}”，不能只做自由拼贴。",
            "作品播放和评价必须检查是否使用了本课已学材料。",
        ]
    return [
        f"答案必须说得出与“{target}”有关的音乐依据。{evidence_suffix}".strip(),
        "游戏结果必须能迁移到课堂中的拍、唱、演、说或创编。",
    ]


def _student_operation_for_domain(domain: str, playable: dict[str, Any]) -> str:
    if domain == "phrase_structure":
        return "把真实片段卡与音乐证据卡配对或排序，说明它们的重复、对比或表现关系。"
    if domain == "rhythm":
        return "把节奏、时值、重音或休止卡按听到的拍点关系摆成节奏句。"
    if domain == "pitch":
        return "把具体唱名、音级或音高卡按听到的顺序摆好，再播放核对。"
    if domain == "pentatonic":
        return "把宫、商、角、徵、羽音级卡拼成短句，再播放判断民族风格。"
    if domain == "timbre":
        return "先听声音样本，再把音色证据或乐器卡配到正确位置。"
    if domain == "expression":
        return "根据播放中的力度、速度、连断或情绪变化选择并排列表现卡。"
    if domain == "singing":
        return "把演唱提示按歌曲进行顺序排好，再用声音完成模唱或跟唱。"
    if domain == "creation":
        return "用本课音乐材料拼接、绘制或组合短句，并播放检查是否符合限制。"
    operation_name = str(playable.get("operation_type") or "课堂挑战")
    return f"完成“{operation_name}”操作，并说出选择的音乐依据。"


def _transfer_action_for_domain(
    domain: str,
    target: str,
    objective: str,
    stage: str,
    lesson_context: dict[str, Any],
) -> str:
    closure = str(lesson_context.get("assessment_closure") or "").strip()
    if closure and len(closure) <= 90:
        return closure
    if domain == "phrase_structure":
        return f"通关后回到“{stage}”，用演唱、动作或语言表现乐句/乐段关系。"
    if domain == "rhythm":
        return f"通关后回到“{stage}”，用拍手、踏步或念读复现这个节奏。"
    if domain == "pitch":
        return f"通关后回到“{stage}”，把音列模唱出来，并指出关键唱名。"
    if domain == "pentatonic":
        return f"通关后回到“{stage}”，唱或播放这条五声音级短句，并说出民族风格依据。"
    if domain == "timbre":
        return f"通关后回到“{stage}”，说出音色证据并模仿或选择合适乐器表现。"
    if domain == "expression":
        return f"通关后回到“{stage}”，用声音或动作表现力度、速度或情绪变化。"
    if domain == "singing":
        return f"通关后回到“{stage}”，完成分句模唱或跟唱。"
    if domain == "creation":
        return f"通关后回到“{stage}”，展示作品并说明用了哪些“{target}”。"
    return f"通关后回到“{stage}”，用拍、唱、演、说或创编说明“{objective or target}”。"


def _teacher_check_for_domain(domain: str, target: str) -> str:
    if domain == "phrase_structure":
        return "学生能否先听片段，再说出重复、对比、呼应或表现差别。"
    if domain == "rhythm":
        return "学生能否稳定拍点，并把时值、重音或休止听准、做准。"
    if domain == "pitch":
        return "学生能否把具体唱名或音高顺序听准、摆准、唱准。"
    if domain == "pentatonic":
        return "学生能否使用宫、商、角、徵、羽材料，并说出五声风格依据。"
    if domain == "timbre":
        return "学生能否用听觉证据区分音色，而不是只看图片。"
    if domain == "expression":
        return "学生能否把力度、速度、连断或情绪变化转化为声音/动作表现。"
    if domain == "creation":
        return "学生作品是否使用了本课音乐材料，并能播放、修改和说明。"
    return f"学生能否说出与“{target}”有关的音乐依据。"


def _student_task_listen(domain: str, playable: dict[str, Any], lesson_context: dict[str, Any]) -> str:
    song_title = str(playable.get("song_title") or lesson_context.get("song_name") or "")
    if song_title:
        return f"听《{song_title}》片段"
    if domain == "rhythm":
        return "听目标节奏"
    if domain == "pitch":
        return "听目标音列"
    if domain == "pentatonic":
        return "听五声音级短句"
    if domain == "timbre":
        return "听音色样本"
    if domain == "expression":
        return "听表现变化"
    return "听目标音乐"


def _short_task_text(text: str, limit: int = 24) -> str:
    text = str(text).strip().replace("。", "")
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _contains_learning_transfer_word(text: str) -> bool:
    return any(keyword in str(text) for keyword in ["拍", "唱", "演", "说", "动作", "表现", "创编", "模唱", "跟唱", "律动", "演奏"])


def _material_evidence_role(material: dict[str, Any], domain: str) -> str:
    text = " ".join([str(material.get("label", "")), str(material.get("music_value", "")), str(material.get("feedback", ""))])
    if domain == "phrase_structure" and str(material.get("id", "")).startswith("phrase_"):
        return "song_fragment"
    if any(keyword in text for keyword in ["证据", "情绪", "动作", "唱", "连贯", "跳跃", "对比", "重复"]):
        return "music_evidence"
    if domain in {"rhythm", "pitch", "pentatonic", "timbre", "expression"}:
        return f"{domain}_token"
    return "music_token"


def _material_teaching_role(material: dict[str, Any], domain: str) -> str:
    if domain == "rhythm":
        return "帮助学生听准拍点、时值或重音。"
    if domain == "pitch":
        return "帮助学生听准具体唱名、音高或旋律顺序。"
    if domain == "pentatonic":
        return "帮助学生使用五声音级材料形成民族风格短句。"
    if domain == "phrase_structure":
        return "帮助学生比较真实片段和音乐表现证据。"
    if domain == "timbre":
        return "帮助学生用听觉证据区分音色。"
    if domain == "expression":
        return "帮助学生把音乐变化转化为声音或动作表现。"
    return "帮助学生完成本课音乐判断。"


def _material(
    material_id: str,
    label: str,
    music_value: str,
    pitch: int,
    duration: float,
    feedback: str,
    *,
    velocity: int = 86,
    rest: bool = False,
    avatar: str = "",
    icon: str = "",
    audio_clip_url: str = "",
    audio_clip_range: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "id": material_id,
        "label": label,
        "music_value": music_value,
        "pitch": pitch,
        "duration": duration,
        "velocity": velocity,
        "rest": rest,
        "feedback": feedback,
        "avatar": avatar,
        "icon": icon,
        "audio_clip_url": audio_clip_url,
        "audio_clip_range": audio_clip_range or {},
        "source_type": "real_audio" if audio_clip_url else "synthesized",
    }


def _matches(text: str, keywords: list[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def _merge_unique_strings(*groups: list[str]) -> list[str]:
    merged: list[str] = []
    for group in groups:
        for item in group:
            text = str(item or "").strip()
            if text and text not in merged:
                merged.append(text)
    return merged


def _is_song_phrase_structure_context(lesson_context: dict[str, Any], recommended_game: dict[str, Any]) -> bool:
    """Only treat as phrase-structure game when the recommended game type is explicitly about phrase/section manipulation."""
    # 1. Check recommended game type — strong signal
    game_type = str(recommended_game.get("type", ""))
    phrase_structure_types = {
        "segment_ordering_studio",
        "phrase_pair_game",
    }
    if game_type in phrase_structure_types:
        return True

    # 2. Check mechanism_id
    mechanic_id = str(
        lesson_context.get("music_element_mechanic", {}).get("mechanism_id", "")
        if isinstance(lesson_context.get("music_element_mechanic"), dict)
        else ""
    ) or str(recommended_game.get("mechanism_id", ""))
    if mechanic_id == "segment_ordering_studio":
        return True

    # 3. Only fall back to keyword matching when BOTH target task and recommended mechanic are strongly about phrase structure.
    # Do NOT trigger just because the lesson mentions "乐句" (that happens in almost every singing lesson).
    source = " ".join(
        [
            str(lesson_context.get("target_music_element", "")),
            str(lesson_context.get("target_segment_task", "")),
            str(lesson_context.get("lesson_evidence", "")),
            str(lesson_context.get("target_segment_gameable_point", "")),
            str(recommended_game.get("mechanic", "")),
            str(recommended_game.get("type", "")),
        ]
    )
    phrases = _available_song_phrases(lesson_context, lesson_context.get("song_anchor_contract", {}) or {})
    if len(phrases) >= 2 and _matches(source, ["乐句结构", "A段", "B段", "乐段", "情绪", "动作", "演唱", "唱法", "断连", "连贯", "对比"]):
        return True
    return _matches(source, ["乐句配对", "乐段重组", "乐句拼图", "曲式", "乐段结构"])


def _available_song_phrases(lesson_context: dict[str, Any], song_anchor: dict[str, Any]) -> list[dict[str, Any]]:
    song_material = lesson_context.get("song_material", {}) if isinstance(lesson_context, dict) else {}
    phrases = [item for item in song_material.get("phrases", []) if isinstance(item, dict)] if isinstance(song_material, dict) else []
    if phrases:
        return phrases[:4]
    selected = song_anchor.get("selected_phrase", {}) if isinstance(song_anchor.get("selected_phrase"), dict) else {}
    if selected:
        return [selected]
    return []


def _phrase_materials_from_song(phrases: list[dict[str, Any]], song_title: str) -> list[dict[str, Any]]:
    materials: list[dict[str, Any]] = []
    for index, phrase in enumerate(phrases[:4], start=1):
        playback_tokens = [item for item in (phrase.get("playback_tokens") or phrase.get("main_melody") or []) if isinstance(item, dict)]
        audio_clip_url = str(phrase.get("audio_clip_url") or "")
        clip_range = phrase.get("audio_clip_range", {}) if isinstance(phrase.get("audio_clip_range"), dict) else {}
        clip_duration = max(
            0.5,
            round(float(clip_range.get("end", 0.0) or 0.0) - float(clip_range.get("start", 0.0) or 0.0), 3),
        )
        if len(playback_tokens) < 2 and not audio_clip_url:
            continue
        pitch = int(playback_tokens[0].get("pitch", 60) or 60) if playback_tokens else 60 + (index - 1) * 3
        duration = (
            float(sum(float(item.get("duration", 0.5) or 0.5) for item in playback_tokens[:8]))
            if playback_tokens
            else clip_duration
        )
        label = str(phrase.get("label") or f"第{index}乐句")
        materials.append(
            {
                **_material(
                    f"phrase_{index}",
                    label,
                    f"{label}片段",
                    pitch,
                    max(0.5, round(duration, 3)),
                    f"这是《{song_title}》里的{label}，请听它和其他片段的关系。",
                ),
                "playback_tokens": playback_tokens[:12],
                "phrase_tokens": playback_tokens[:12],
                "audio_clip_url": audio_clip_url,
                "audio_clip_range": clip_range,
                "source_phrase_id": phrase.get("id", ""),
                "phrase_role": _phrase_role(index, len(phrases)),
            }
        )
    if len(materials) >= 2:
        return materials
    if phrases:
        return _chunk_single_phrase_materials(phrases[0], song_title)
    return []


def _chunk_single_phrase_materials(phrase: dict[str, Any], song_title: str) -> list[dict[str, Any]]:
    playback_tokens = [item for item in (phrase.get("playback_tokens") or phrase.get("main_melody") or []) if isinstance(item, dict)]
    if len(playback_tokens) < 4:
        return []
    materials: list[dict[str, Any]] = []
    chunk_size = max(3, min(6, len(playback_tokens) // 3 or 3))
    for index in range(0, len(playback_tokens), chunk_size):
        chunk = playback_tokens[index : index + chunk_size]
        if len(chunk) < 2:
            continue
        card_index = len(materials) + 1
        pitch = int(chunk[0].get("pitch", 60) or 60)
        duration = float(sum(float(item.get("duration", 0.5) or 0.5) for item in chunk))
        materials.append(
            {
                **_material(
                    f"phrase_{card_index}",
                    f"片段 {card_index}",
                    f"第{card_index}个乐句片段",
                    pitch,
                    max(0.4, round(duration, 3)),
                    f"这是《{song_title}》中的真实片段 {card_index}。",
                ),
                "playback_tokens": chunk,
                "phrase_tokens": chunk,
                "audio_clip_url": phrase.get("audio_clip_url", ""),
                "audio_clip_range": phrase.get("audio_clip_range", {}),
                "source_phrase_id": phrase.get("id", ""),
                "phrase_role": _phrase_role(card_index, 4),
            }
        )
        if len(materials) >= 4:
            break
    return materials


def _phrase_role(index: int, total: int) -> str:
    if index == 1:
        return "opening"
    if index == total:
        return "closing"
    if index == 2:
        return "repeat_or_answer"
    return "contrast_or_development"


def _phrase_expression_evidence_materials(
    lesson_context: dict[str, Any],
    recommended_game: dict[str, Any],
) -> list[dict[str, Any]]:
    source = " ".join(
        [
            str(lesson_context.get("target_objective", "")),
            str(lesson_context.get("lesson_evidence", "")),
            str(lesson_context.get("target_segment_task", "")),
            str(lesson_context.get("target_segment_gameable_point", "")),
            str(recommended_game.get("mechanic", "")),
            " ".join(str(item) for item in recommended_game.get("rules", []) if not isinstance(item, dict)),
        ]
    )
    if _matches(source, ["A段", "B段", "乐段", "情绪", "声音", "断连", "动作", "温馨", "快乐", "愉快"]):
        return [
            _material(
                "a_bright_jump",
                "欢快跳跃唱",
                "A段：轻巧、有弹性",
                72,
                0.42,
                "A段通常更活泼，可以用跳跃感声音或轻快动作表现。",
                avatar="A",
                icon="spark",
            ),
            _material(
                "b_warm_legato",
                "温馨连贯唱",
                "B段：柔和、连贯",
                64,
                0.78,
                "B段通常更温馨，可以用连贯声音或舒展动作表现。",
                avatar="B",
                icon="line",
            ),
        ]
    return [
        _material(
            "similar_repeat",
            "相似重复",
            "听起来熟悉",
            67,
            0.46,
            "相似乐句会让人听到熟悉感。",
            avatar="同",
            icon="repeat",
        ),
        _material(
            "contrast_change",
            "对比变化",
            "情绪或线条变化",
            72,
            0.58,
            "对比乐句通常在情绪、节奏或旋律线条上发生变化。",
            avatar="变",
            icon="contrast",
        ),
    ]


def _song_phrase_expression_sequence(
    phrase_materials: list[dict[str, Any]],
    evidence_materials: list[dict[str, Any]],
) -> list[str]:
    if len(phrase_materials) >= 2 and len(evidence_materials) >= 2:
        return [
            phrase_materials[0]["id"],
            evidence_materials[0]["id"],
            phrase_materials[1]["id"],
            evidence_materials[1]["id"],
        ]
    sequence: list[str] = []
    for index, phrase in enumerate(phrase_materials):
        sequence.append(phrase["id"])
        if evidence_materials:
            sequence.append(evidence_materials[min(index, len(evidence_materials) - 1)]["id"])
    return sequence


def _song_phrase_expression_rounds(
    phrase_materials: list[dict[str, Any]],
    evidence_materials: list[dict[str, Any]],
    sequence: list[str],
) -> list[dict[str, Any]]:
    if len(phrase_materials) < 2 or len(evidence_materials) < 2:
        return _song_phrase_structure_rounds(phrase_materials)
    return [
        {
            "id": "round_1",
            "label": "第 1 关",
            "prompt": f"听{phrase_materials[0]['label']}，给它配上合适的声音或动作证据。",
            "target_sequence": [phrase_materials[0]["id"], evidence_materials[0]["id"]],
            "stars": 1,
        },
        {
            "id": "round_2",
            "label": "第 2 关",
            "prompt": f"听{phrase_materials[1]['label']}，判断它和前一段的表现差别。",
            "target_sequence": [phrase_materials[1]["id"], evidence_materials[1]["id"]],
            "stars": 2,
        },
        {
            "id": "round_3",
            "label": "第 3 关",
            "prompt": "把两个片段和两种表现完整配对，再用声音或动作表现一次。",
            "target_sequence": sequence,
            "stars": 3,
        },
    ]


def _song_phrase_structure_rounds(materials: list[dict[str, Any]]) -> list[dict[str, Any]]:
    sequence = [item["id"] for item in materials]
    if len(sequence) < 2:
        return []
    rounds = [
        {
            "id": "round_1",
            "label": "第 1 关",
            "prompt": "先找出前两个真实片段，听它们是否属于同一组乐句关系。",
            "target_sequence": sequence[:2],
            "stars": 1,
        }
    ]
    if len(sequence) >= 3:
        rounds.append(
            {
                "id": "round_2",
                "label": "第 2 关",
                "prompt": "加入变化片段，判断哪一个和前面形成对比或回答。",
                "target_sequence": sequence[:3],
                "stars": 2,
            }
        )
    rounds.append(
        {
            "id": f"round_{len(rounds) + 1}",
            "label": f"第 {len(rounds) + 1} 关",
            "prompt": "把整首歌需要的真实片段排完整，完成结构配对。",
            "target_sequence": sequence,
            "stars": 3,
        }
    )
    return rounds


def _is_binary_dynamic_contrast(source: str) -> bool:
    has_binary_signal = any(keyword in source for keyword in ["f/p", "f 和 p", "f和p", "强弱", "强 弱"])
    has_gradual_signal = any(keyword in source for keyword in ["渐强", "渐弱", "从弱到强", "力度线", "力度变化线", "层次", "mp", "mf"])
    return has_binary_signal and not has_gradual_signal
