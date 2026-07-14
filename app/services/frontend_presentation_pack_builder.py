from __future__ import annotations

from copy import deepcopy
from typing import Any


PRESENTATION_PACK_VERSION = "frontend_presentation_pack_v1"

FRONTEND_STACK = {
    "app_framework": "React + Vite",
    "component_library": "Radix Themes",
    "icons": "Lucide React",
    "state": "Zustand",
}


def build_frontend_presentation_pack(
    *,
    gameplay_blueprint: dict[str, Any],
    experience_script: dict[str, Any],
    theme_pack: dict[str, Any],
    render_spec: dict[str, Any],
) -> dict[str, Any]:
    """Create the React-consumable art-direction layer for a locked game."""

    palette = theme_pack.get("palette", {}) if isinstance(theme_pack.get("palette"), dict) else {}
    scene = theme_pack.get("scene", {}) if isinstance(theme_pack.get("scene"), dict) else {}
    skin_family = str(theme_pack.get("skin_family") or "")
    layout_variant = str(theme_pack.get("layout_variant") or "")
    motion = theme_pack.get("motion", {}) if isinstance(theme_pack.get("motion"), dict) else {}
    operation_type = str(gameplay_blueprint.get("operation_type") or "")
    template_id = str(gameplay_blueprint.get("based_on_template") or "")
    experience_variant_id = str(gameplay_blueprint.get("experience_variant_id") or theme_pack.get("experience_variant_id") or "")
    play_mode = str(gameplay_blueprint.get("play_mode") or theme_pack.get("play_mode") or "")
    playfield_composition = str(gameplay_blueprint.get("playfield_composition") or theme_pack.get("playfield_composition") or "")
    playfield = render_spec.get("screen_structure", {}).get("playfield", {})
    playfield_type = str(playfield.get("type") or "")
    engine_target = _engine_target(operation_type, playfield)
    primary_action = _primary_action(template_id, operation_type, playfield_type)
    shell = _runtime_shell(template_id, engine_target)
    return {
        "version": PRESENTATION_PACK_VERSION,
        "owner": "frontend_presentation_director",
        "runtime_target": "react_student_runtime",
        "output_kind": "react_presentation_pack",
        "engine_target": engine_target,
        "template_id": template_id,
        "frontend_stack": deepcopy(FRONTEND_STACK),
        "source": "system_baseline",
        "experience_variant_id": experience_variant_id,
        "play_mode": play_mode,
        "game_genre": gameplay_blueprint.get("game_genre", ""),
        "variant_game_genre": gameplay_blueprint.get("variant_game_genre", ""),
        "scene_goal": gameplay_blueprint.get("scene_goal", ""),
        "main_object": gameplay_blueprint.get("main_object", ""),
        "interaction_feedback": gameplay_blueprint.get("interaction_feedback", ""),
        "failure_feedback": gameplay_blueprint.get("failure_feedback", ""),
        "reward_loop": gameplay_blueprint.get("reward_loop", ""),
        "playfield_composition": playfield_composition,
        "skin_family": skin_family,
        "layout_variant": layout_variant,
        "palette": deepcopy(palette),
        "scene": deepcopy(scene),
        "motif": _motif_for_family(skin_family),
        "hud_density": _hud_density_for_family(skin_family),
        "reward_style": {
            "token": theme_pack.get("reward_token", "奖励"),
            "cadence": "每关都有可见推进，通关时给出明确庆祝反馈",
        },
        "motion_profile": {
            "entry": motion.get("entry", "轻缓浮现"),
            "success": motion.get("success", "正确元素点亮"),
            "failure": motion.get("failure", "轻微停顿"),
            "tempo": _motion_tempo(operation_type),
        },
        "animation_profile": {
            "scene_entry": motion.get("entry", "轻缓浮现"),
            "hit": motion.get("success", "目标拍点亮并推进主物件"),
            "miss": motion.get("failure", "轻微停顿并给出可恢复提示"),
            "reward": "通关时触发皮肤专属奖励动画",
        },
        "scene_skin": {
            "skin_id": theme_pack.get("theme_id") or theme_pack.get("skin_id") or layout_variant or skin_family,
            "skin_family": skin_family,
            "play_mode_hint": play_mode or _scene_play_mode_hint(layout_variant, skin_family),
            "experience_variant_id": experience_variant_id,
            "scene_goal": gameplay_blueprint.get("scene_goal", ""),
            "main_object": gameplay_blueprint.get("main_object", ""),
            "interaction_feedback": gameplay_blueprint.get("interaction_feedback", ""),
            "failure_feedback": gameplay_blueprint.get("failure_feedback", ""),
            "reward_loop": gameplay_blueprint.get("reward_loop", ""),
        },
        "hud_layout": {
            "style": _hud_density_for_family(skin_family),
            "shell": shell,
            "persistent_cluster": _persistent_cluster(template_id),
            "primary_action": primary_action,
            "teacher_readable_feedback": True,
            "first_screen_density": "playfield_only" if shell.endswith("_shell") else "balanced",
            "teacher_notes_visibility": "pause_or_result_only" if engine_target == "phaser_2d" else "collapsed",
            "feedback_max_chars": 8 if engine_target == "phaser_2d" else 36,
            "play_mode": play_mode,
            "playfield_composition": playfield_composition,
        },
        "background_layers": _background_layers_for_family(skin_family),
        "css_variables": {
            "--student-primary": palette.get("primary", ""),
            "--student-accent": palette.get("accent", ""),
            "--student-bg": palette.get("background", ""),
            "--student-success": palette.get("success", ""),
        },
        "asset_manifest": {
            "hero_prop": scene.get("supporting_prop", ""),
            "objective_noun": scene.get("objective_noun", ""),
            "playfield_type": playfield.get("type", ""),
            "main_object": gameplay_blueprint.get("main_object", ""),
            "experience_variant_id": experience_variant_id,
        },
        "copy_tone": {
            "opening_hook": experience_script.get("opening_hook", ""),
            "reward_token": theme_pack.get("reward_token", ""),
        },
}


def _runtime_shell(template_id: str, engine_target: str) -> str:
    return {
        "beat_guardian_core": "beat_guardian_shell",
        "rhythm_echo_core": "rhythm_echo_shell",
        "pitch_ladder_core": "pitch_ladder_map_shell",
        "solfege_target_core": "solfege_target_shell",
        "timbre_detective_core": "timbre_detective_shell",
        "form_treasure_core": "form_treasure_shell",
        "composition_puzzle_core": "composition_puzzle_shell",
    }.get(template_id, "arcade_game" if engine_target == "phaser_2d" else "standard_game")


def _primary_action(template_id: str, operation_type: str, playfield_type: str) -> str:
    if template_id == "beat_guardian_core":
        return "guard_button"
    if template_id == "rhythm_echo_core" or "rhythm_echo" in operation_type or playfield_type == "rhythm_timeline":
        return "record_tap_button"
    if template_id == "pitch_ladder_core":
        return "route_step_button"
    if template_id == "solfege_target_core":
        return "aim_hit_button"
    if template_id == "timbre_detective_core":
        return "submit_evidence_button"
    if template_id == "form_treasure_core":
        return "verify_form_route_button"
    if template_id == "composition_puzzle_core":
        return "audition_submit_button"
    return "primary_action"


def _persistent_cluster(template_id: str) -> str:
    return {
        "beat_guardian_core": "edge_energy_combo",
        "rhythm_echo_core": "memory_console_status",
        "pitch_ladder_core": "map_route_compass",
        "solfege_target_core": "target_reticle_status",
        "timbre_detective_core": "casefile_clue_status",
        "form_treasure_core": "timeline_card_progress",
        "composition_puzzle_core": "constraint_checklist_progress",
    }.get(template_id, "top_compact_status")


def _engine_target(operation_type: str, playfield: dict[str, Any]) -> str:
    playfield_type = str(playfield.get("type") or "")
    if "beat_guardian" in operation_type or playfield_type in {"beat_lane", "beat_guardian_scene"}:
        return "phaser_2d"
    if "rhythm_echo" in operation_type or playfield_type in {"rhythm_timeline", "rhythm_echo_scene"}:
        return "phaser_2d"
    if "form_treasure" in operation_type or playfield_type in {"form_timeline", "form_treasure_scene"}:
        return "phaser_2d"
    if "composition_puzzle" in operation_type or playfield_type == "composition_puzzle_scene":
        return "phaser_2d"
    return "react_dom"


def _scene_play_mode_hint(layout_variant: str, skin_family: str) -> str:
    if layout_variant == "river_race":
        return "race"
    if skin_family == "pulse_world":
        return "spotlight"
    if skin_family == "target_world":
        return "orbit"
    return "gate"


def _motif_for_family(skin_family: str) -> str:
    return {
        "trail_world": "路线、节点、沿途点亮",
        "race_world": "赛道、推进、冲线",
        "casebook_world": "案卷、线索、证据贴",
        "pulse_world": "舞台、脉冲、节拍光环",
        "target_world": "靶场、准星、星轨",
    }.get(skin_family, "课堂冒险")


def _hud_density_for_family(skin_family: str) -> str:
    return {
        "trail_world": "balanced",
        "race_world": "compact",
        "casebook_world": "split",
        "pulse_world": "stage_focused",
        "target_world": "shelf",
    }.get(skin_family, "balanced")


def _motion_tempo(operation_type: str) -> str:
    if "beat" in operation_type or "rhythm" in operation_type:
        return "snappy"
    if "timbre" in operation_type:
        return "measured"
    return "gentle"


def _background_layers_for_family(skin_family: str) -> list[str]:
    return {
        "trail_world": ["soft_glow", "route_texture"],
        "race_world": ["river_band", "finish_glow"],
        "casebook_world": ["paper_grain", "evidence_grid"],
        "pulse_world": ["stage_halo", "sound_rings"],
        "target_world": ["orbit_field", "focus_rings"],
    }.get(skin_family, ["soft_glow"])
