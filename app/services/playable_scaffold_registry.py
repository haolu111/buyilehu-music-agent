from __future__ import annotations

import json
import re
from typing import Any


SCAFFOLD_LABELS = {
    "drag_puzzle": "拖拽拼图骨架",
    "level_runner": "闯关表现骨架",
    "match_quiz": "证据匹配骨架",
}


def classify_playable_scaffold(spec: dict[str, Any], *, generation_mode: str = "fast") -> dict[str, Any]:
    """Conservatively route common playable mechanics to stable local scaffolds.

    This is not a visual template selector. It only decides whether the existing
    reusable playable runtime can satisfy the mechanics quickly; unclear or novel
    games keep the freeform OpenCode path.
    """

    if _mode(generation_mode or spec.get("generation_mode")) != "fast":
        return _no_match("严格模式保留自由生成和完整验收。")
    if spec.get("activity_type") != "music_game":
        return _no_match("当前不是音乐小游戏。")

    game = spec.get("music_game", {}) if isinstance(spec.get("music_game"), dict) else {}
    playable = game.get("playable_game", {}) if isinstance(game.get("playable_game"), dict) else {}
    if not game.get("enabled") or not isinstance(playable, dict):
        return _no_match("没有可玩音乐游戏规格。")
    if not playable.get("materials") or not playable.get("target_sequence"):
        return _no_match("缺少可操作材料或目标序列。")

    text = _spec_text(spec, game, playable)
    operation_type = str(playable.get("operation_type") or game.get("operation_type") or "")
    scaffold_scores = {
        "drag_puzzle": _score_drag_puzzle(text, operation_type),
        "level_runner": _score_level_runner(text, operation_type, playable),
        "match_quiz": _score_match_quiz(text, operation_type),
    }
    scaffold_id, score = max(scaffold_scores.items(), key=lambda item: item[1])
    if score < 3:
        return _no_match("玩法意图不够明确，继续走开放生成。", scores=scaffold_scores)

    enriched = _normalize_spec_for_scaffold(spec, scaffold_id)
    return {
        "enabled": True,
        "scaffold_id": scaffold_id,
        "label": SCAFFOLD_LABELS.get(scaffold_id, scaffold_id),
        "confidence": min(0.96, 0.55 + score * 0.09),
        "reason": _reason_for(scaffold_id),
        "scores": scaffold_scores,
        "spec": enriched,
    }


def _normalize_spec_for_scaffold(spec: dict[str, Any], scaffold_id: str) -> dict[str, Any]:
    enriched = dict(spec)
    game = dict(enriched.get("music_game", {}) if isinstance(enriched.get("music_game"), dict) else {})
    playable = dict(game.get("playable_game", {}) if isinstance(game.get("playable_game"), dict) else {})
    playable.setdefault("prompt", _prompt_for(scaffold_id, enriched, game))
    playable.setdefault("student_facing_task", _student_task_for(scaffold_id, enriched, game))
    playable.setdefault("feedback", _feedback_for(scaffold_id))
    playable.setdefault("learning_transfer", _learning_transfer_for(enriched, scaffold_id))
    playable.setdefault("playback", {})
    playable["playback"] = {
        "instrument": _playback_instrument_for(enriched, scaffold_id),
        "seconds_per_step": 0.5,
        **dict(playable.get("playback", {}) if isinstance(playable.get("playback"), dict) else {}),
    }
    playable["scaffold_id"] = scaffold_id
    game["playable_game"] = playable
    game["enabled"] = True
    enriched["music_game"] = game
    enriched["playable_scaffold"] = {
        "enabled": True,
        "scaffold_id": scaffold_id,
        "label": SCAFFOLD_LABELS.get(scaffold_id, scaffold_id),
        "render_strategy": "local_reusable_playable_runtime",
    }
    enriched["artifact_generation_mode"] = "scaffold"
    generation_strategy = dict(enriched.get("generation_strategy", {}) if isinstance(enriched.get("generation_strategy"), dict) else {})
    generation_strategy["mode"] = "fast_playable_scaffold"
    generation_strategy["template_policy"] = "reuse_runtime_primitives_not_fixed_visual_template"
    generation_strategy["freeform_fallback"] = True
    enriched["generation_strategy"] = generation_strategy
    return enriched


def _spec_text(spec: dict[str, Any], game: dict[str, Any], playable: dict[str, Any]) -> str:
    parts = [
        spec.get("title", ""),
        spec.get("subtitle", ""),
        spec.get("original_user_need", ""),
        spec.get("target_stage", ""),
        spec.get("target_objective", ""),
        spec.get("target_music_element", ""),
        spec.get("target_segment_task", ""),
        game.get("game_type", ""),
        game.get("game_name", ""),
        game.get("music_concept", ""),
        game.get("mechanic", ""),
        playable.get("operation_type", ""),
        playable.get("music_goal", ""),
    ]
    compact_payload = {
        "rules": game.get("rules", []),
        "student_actions": game.get("student_actions", []),
        "materials": playable.get("materials", []),
        "target_sequence": playable.get("target_sequence", []),
    }
    parts.append(json.dumps(compact_payload, ensure_ascii=False))
    return " ".join(str(part or "") for part in parts).lower()


def _score_drag_puzzle(text: str, operation_type: str) -> int:
    score = _keyword_score(text, ["拖拽", "拖动", "拼图", "排序", "还原", "重建", "排列", "唱名卡", "音高卡", "乐句拼图"])
    if re.search(r"sequence|ordering|puzzle|rebuild|solmi|pitch|melody|phrase", operation_type, re.I):
        score += 2
    return score


def _score_level_runner(text: str, operation_type: str, playable: dict[str, Any]) -> int:
    score = _keyword_score(text, ["关卡", "闯关", "第 1 关", "第一关", "三关", "通关", "模仿", "表现", "跟唱", "节奏提示"])
    if re.search(r"level|runner|performance|echo|sing", operation_type, re.I):
        score += 2
    if isinstance(playable.get("rounds"), list) and len(playable.get("rounds", [])) >= 2:
        score += 2
    return score


def _score_match_quiz(text: str, operation_type: str) -> int:
    score = _keyword_score(text, ["匹配", "配对", "找朋友", "证据卡", "音色侦探", "音色", "乐器", "试听乐器", "timbre"])
    if re.search(r"match|quiz|timbre|instrument|evidence", operation_type, re.I):
        score += 2
    return score


def _keyword_score(text: str, keywords: list[str]) -> int:
    return sum(1 for keyword in keywords if keyword.lower() in text)


def _prompt_for(scaffold_id: str, spec: dict[str, Any], game: dict[str, Any]) -> str:
    concept = spec.get("target_music_element") or game.get("music_concept") or "音乐线索"
    if scaffold_id == "match_quiz":
        return f"先试听，再把证据卡匹配到“{concept}”。"
    if scaffold_id == "level_runner":
        return f"跟着提示完成每一关，抓住“{concept}”。"
    return f"先听目标，再拖卡片还原“{concept}”。"


def _student_task_for(scaffold_id: str, spec: dict[str, Any], game: dict[str, Any]) -> dict[str, str]:
    lesson_context = spec.get("lesson_context", {}) if isinstance(spec.get("lesson_context"), dict) else {}
    song = spec.get("song_name") or lesson_context.get("song_name") or ""
    song = song or "目标音乐"
    concept = spec.get("target_music_element") or game.get("music_concept") or "音乐线索"
    if scaffold_id == "match_quiz":
        return {"listen": f"听{song}里的音色", "do": "拖证据卡完成匹配", "pass": "说出一条音色证据"}
    if scaffold_id == "level_runner":
        return {"listen": f"听{song}的提示", "do": "按关卡完成模仿", "pass": "回到课堂表现一次"}
    return {"listen": f"听{song}目标片段", "do": "拖卡片排出正确顺序", "pass": f"唱或拍出{concept}"}


def _feedback_for(scaffold_id: str) -> dict[str, str]:
    if scaffold_id == "match_quiz":
        return {
            "empty": "先试听，再放入证据卡。",
            "partial": "这条证据方向对了，继续补全。",
            "wrong": "证据还没对上音色，再听一次。",
            "success": "匹配成功。",
            "closure": "现在说出你听到的音色证据。",
        }
    return {
        "empty": "先把音乐卡片放进挑战区。",
        "partial": "前面顺序对了，继续补完整。",
        "wrong": "顺序还没有体现音乐关系，先试听目标再调整。",
        "success": "挑战成功。",
        "closure": "现在回到课堂任务，拍、唱或说出你的音乐理由。",
    }


def _learning_transfer_for(spec: dict[str, Any], scaffold_id: str) -> dict[str, Any]:
    concept = spec.get("target_music_element") or "音乐线索"
    if scaffold_id == "match_quiz":
        return {
            "listen_target": f"听辨{concept}",
            "music_evidence": [f"用{concept}作为判断证据"],
            "student_operation": "匹配证据卡",
            "classroom_transfer": "说出一条听辨理由，再让同伴复核。",
        }
    return {
        "listen_target": f"听清{concept}",
        "music_evidence": [f"根据{concept}判断顺序"],
        "student_operation": "拖拽音乐卡片完成挑战",
        "classroom_transfer": "通关后跟琴模唱、拍击或说出音乐理由。",
    }


def _playback_instrument_for(spec: dict[str, Any], scaffold_id: str) -> str:
    text = json.dumps(spec, ensure_ascii=False).lower()
    if "古筝" in text or "guzheng" in text or "koto" in text:
        return "koto"
    if "小提琴" in text or "violin" in text:
        return "violin"
    if "长笛" in text or "flute" in text:
        return "flute"
    if scaffold_id == "match_quiz" and ("木琴" in text or "打击" in text):
        return "xylophone"
    return "acoustic_grand_piano"


def _reason_for(scaffold_id: str) -> str:
    return {
        "drag_puzzle": "命中常见的拖拽排序/还原类音乐任务，可复用稳定可玩任务板。",
        "level_runner": "命中常见的分关表现任务，可复用稳定关卡状态和通关反馈。",
        "match_quiz": "命中常见的音色/证据匹配任务，可复用稳定试听与证据卡交互。",
    }.get(scaffold_id, "命中可复用玩法骨架。")


def _mode(value: Any) -> str:
    mode = str(value or "").strip().lower()
    return mode if mode in {"fast", "strict"} else "fast"


def _no_match(reason: str, *, scores: dict[str, int] | None = None) -> dict[str, Any]:
    return {
        "enabled": False,
        "scaffold_id": "",
        "label": "",
        "confidence": 0,
        "reason": reason,
        "scores": scores or {},
    }
