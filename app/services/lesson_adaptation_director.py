from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.services.lesson_fit_layer import attach_lesson_fit_layer, refresh_lesson_fit_template_hint
from app.services.lesson_game_playable import attach_playable_game_to_lesson_analysis
from app.services.music_element_adjustment_contract import attach_music_element_adjustment_contract


LESSON_ADAPTATION_VERSION = "lesson_adaptation_v1"


def attach_lesson_adaptation(
    lesson_analysis: dict[str, Any],
    *,
    lesson_source: dict[str, Any] | None = None,
    extra_need: str = "",
) -> dict[str, Any]:
    """Build the lesson-only layer before any template or frontend decision."""

    enriched = deepcopy(lesson_analysis)
    lesson_context = enriched.get("lesson_context", {}) if isinstance(enriched.get("lesson_context"), dict) else {}
    playable = lesson_context.get("playable_game") if isinstance(lesson_context.get("playable_game"), dict) else {}
    recommended = enriched.get("recommended_game") if isinstance(enriched.get("recommended_game"), dict) else {}
    if not playable or recommended:
        enriched = attach_playable_game_to_lesson_analysis(enriched)
    lesson_context = enriched.get("lesson_context", {}) if isinstance(enriched.get("lesson_context"), dict) else {}
    existing_fit = lesson_context.get("lesson_fit") if isinstance(lesson_context.get("lesson_fit"), dict) else {}
    if not existing_fit:
        enriched = attach_lesson_fit_layer(enriched, lesson_source=lesson_source, extra_need=extra_need)
    else:
        enriched = refresh_lesson_fit_template_hint(enriched, lesson_source=lesson_source, extra_need=extra_need)
    enriched = attach_music_element_adjustment_contract(enriched)

    lesson_context = enriched.get("lesson_context", {}) if isinstance(enriched.get("lesson_context"), dict) else {}
    lesson_fit = lesson_context.get("lesson_fit", {}) if isinstance(lesson_context.get("lesson_fit"), dict) else {}
    playable = lesson_context.get("playable_game", {}) if isinstance(lesson_context.get("playable_game"), dict) else {}
    music_logic = lesson_context.get("music_logic_contract", {}) if isinstance(lesson_context.get("music_logic_contract"), dict) else {}
    adaptation = build_lesson_adaptation_contract(
        lesson_context=lesson_context,
        lesson_fit=lesson_fit,
        playable_game=playable,
        music_logic_contract=music_logic,
    )
    lesson_context["lesson_adaptation"] = adaptation
    enriched["lesson_context"] = lesson_context
    enriched["lesson_adaptation"] = adaptation
    return enriched


def build_lesson_adaptation_contract(
    *,
    lesson_context: dict[str, Any],
    lesson_fit: dict[str, Any],
    playable_game: dict[str, Any],
    music_logic_contract: dict[str, Any],
) -> dict[str, Any]:
    """Describe what the lesson layer owns, without choosing UI or skins."""

    lesson_evidence = lesson_fit.get("lesson_evidence", {}) if isinstance(lesson_fit.get("lesson_evidence"), dict) else {}
    material_binding = lesson_fit.get("material_binding", {}) if isinstance(lesson_fit.get("material_binding"), dict) else {}
    return {
        "version": LESSON_ADAPTATION_VERSION,
        "owner": "lesson_fit_director",
        "responsibility": "translate_unbounded_lessons_into_bounded_learning_tasks",
        "owns": [
            "教学目标",
            "音乐要素",
            "课堂环节",
            "作品或乐句绑定",
            "学生必须完成的听做说行为",
            "课堂迁移闭环",
        ],
        "must_not_do": [
            "不选择页面皮肤",
            "不设计最终前端布局",
            "不把不匹配模板硬套进教案",
        ],
        "lesson_focus": {
            "target_objective": lesson_evidence.get("target_objective") or lesson_context.get("target_objective") or "",
            "music_element": lesson_evidence.get("music_element") or lesson_context.get("target_music_element") or "",
            "target_stage": lesson_evidence.get("target_stage") or lesson_context.get("target_stage") or "",
            "segment_task": lesson_evidence.get("segment_task") or lesson_context.get("target_segment_task") or "",
        },
        "material_binding": deepcopy(material_binding),
        "student_learning_contract": {
            "operation_type": playable_game.get("operation_type", ""),
            "prompt": playable_game.get("prompt", ""),
            "required_student_actions": deepcopy(playable_game.get("required_student_actions", [])),
            "completion_condition": playable_game.get("completion_condition", ""),
            "learning_transfer": deepcopy(playable_game.get("learning_transfer", {})),
        },
        "template_need": {
            "operation_type": playable_game.get("operation_type", ""),
            "mechanism_id": _mechanism_id_from_context(lesson_context),
            "music_focus": lesson_evidence.get("music_element") or lesson_context.get("target_music_element") or "",
            "fit_score": lesson_fit.get("fit_score", 0),
        },
        "music_logic_ref": {
            "version": music_logic_contract.get("version", ""),
            "token_count": len(music_logic_contract.get("tokens", [])) if isinstance(music_logic_contract.get("tokens"), list) else 0,
            "round_count": len(playable_game.get("rounds", [])) if isinstance(playable_game.get("rounds"), list) else 0,
        },
    }


def _mechanism_id_from_context(lesson_context: dict[str, Any]) -> str:
    mechanism = lesson_context.get("music_element_mechanic", {})
    if isinstance(mechanism, dict) and mechanism.get("mechanism_id"):
        return str(mechanism.get("mechanism_id"))
    return str(lesson_context.get("recommended_game_type") or "")
