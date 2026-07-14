from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.services.game_template_registry import get_game_template


LOCKED_CORE_FIELDS = ("engine", "scene_id", "runtime_shell")
LOCKED_RUNTIME_COMPONENTS = {
    "beat_guardian_core": "BeatGuardianGame",
    "rhythm_echo_core": "RhythmEchoGame",
    "pitch_ladder_core": "PitchLadderGame",
    "solfege_target_core": "SolfegeTargetGame",
    "timbre_detective_core": "TimbreDetectiveGame",
    "form_treasure_core": "FormTreasureGame",
    "composition_puzzle_core": "CompositionPuzzleGame",
}
ALLOWED_TEMPLATE_ADAPTATION_FIELDS = (
    "skin_id",
    "skin_play_mode",
    "music_concept",
    "teacher_prompt",
    "material_binding_plan",
    "lesson_adaptation",
)


def build_template_fidelity_contract(instance: dict[str, Any], skin_selection_source: str = "") -> dict[str, Any]:
    template_id = str(instance.get("template_id") or "")
    template = get_game_template(template_id) or {}
    config = instance.get("config", {}) if isinstance(instance.get("config"), dict) else {}
    default_config = template.get("default_config", {}) if isinstance(template.get("default_config"), dict) else {}
    allowed_skin_ids = [str(item) for item in template.get("supported_skins", []) if str(item).strip()]
    selected_skin_id = str(config.get("skin_id") or "")
    locked_runtime_component = LOCKED_RUNTIME_COMPONENTS.get(template_id, "")
    actual_runtime_component = str(config.get("runtime_component") or locked_runtime_component)
    locked_core_fields = {
        field: {
            "expected": default_config.get(field, ""),
            "actual": config.get(field, ""),
            "pass": config.get(field, "") == default_config.get(field, ""),
        }
        for field in LOCKED_CORE_FIELDS
    }
    skin_allowed = bool(selected_skin_id and selected_skin_id in allowed_skin_ids)
    runtime_component_pass = bool(locked_runtime_component and actual_runtime_component == locked_runtime_component)
    template_fidelity_pass = bool(
        template_id
        and skin_allowed
        and all(item["pass"] for item in locked_core_fields.values())
        and runtime_component_pass
    )
    return {
        "template_id": template_id,
        "runtime_shell": str(config.get("runtime_shell") or ""),
        "scene_id": str(config.get("scene_id") or ""),
        "engine": str(config.get("engine") or ""),
        "allowed_skin_ids": deepcopy(allowed_skin_ids),
        "selected_skin_id": selected_skin_id,
        "skin_selection_source": _normalize_skin_selection_source(skin_selection_source),
        "locked_runtime_component": locked_runtime_component,
        "actual_runtime_component": actual_runtime_component,
        "lesson_adaptation_mode": "template_component_patch" if locked_runtime_component else "",
        "locked_core_fields": locked_core_fields,
        "runtime_component_pass": runtime_component_pass,
        "allowed_adaptation_fields": list(ALLOWED_TEMPLATE_ADAPTATION_FIELDS),
        "template_fidelity_pass": template_fidelity_pass,
    }


def template_fidelity_passes(workflow: dict[str, Any]) -> bool:
    if not isinstance(workflow, dict):
        return False
    instance = workflow.get("instance", {}) if isinstance(workflow.get("instance"), dict) else {}
    existing = workflow.get("template_fidelity_contract", {})
    source = ""
    if isinstance(existing, dict):
        source = str(existing.get("skin_selection_source") or "")
    current = build_template_fidelity_contract(instance, source)
    return bool(current.get("template_fidelity_pass"))


def _normalize_skin_selection_source(value: str) -> str:
    if value in {"teacher_selected", "lesson_recommended", "template_default"}:
        return value
    return "template_default"
