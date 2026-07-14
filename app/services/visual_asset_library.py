from __future__ import annotations

from typing import Any


ASSET_PACKS: list[dict[str, Any]] = [
    {
        "id": "rhythm_stage",
        "label": "节奏行动舞台",
        "hero": "/static/assets/game-packs/节奏复刻/background.png",
        "badge": "/static/assets/game-packs/rhythm-badge.svg",
        "keywords": ["节奏", "节拍", "拍", "切分", "附点", "休止符", "时值", "强弱规律"],
        "game_types": ["rhythm_race_game", "rhythm_animal_race", "note_value_race", "syncopation_flag_game", "meter_gate_game", "meter_orbit_game", "rest_light_game", "dotted_rhythm_bounce"],
        "mechanisms": ["rhythm_drag_playback", "syncopation_flag_game", "meter_gate_game", "meter_orbit_game"],
        "accent": "#ff7b54",
        "background": "#fff3c7",
    },
    {
        "id": "pitch_path",
        "label": "音高路线",
        "hero": "/static/assets/game-packs/pitch-path.svg",
        "badge": "/static/assets/game-packs/pitch-badge.svg",
        "keywords": ["音高", "旋律", "sol", "mi", "级进", "跳进", "上行", "下行", "乐句"],
        "game_types": ["pitch_path_game", "melody_path_game", "sol_mi_pitch_game", "interval_step_game", "phrase_pair_game"],
        "mechanisms": ["melody_path_builder", "sol_mi_pitch_game", "phrase_pair_game"],
        "accent": "#2a6fbb",
        "background": "#eaf4ff",
    },
    {
        "id": "dynamics_panel",
        "label": "强弱声音调色盘",
        "hero": "/static/assets/game-packs/dynamics-panel.svg",
        "badge": "/static/assets/game-packs/dynamics-badge.svg",
        "keywords": ["力度", "强弱", "f/p", "f和p", "p和f", "强音", "弱音", "速度"],
        "game_types": ["dynamic_contrast_game", "dynamic_slider_game", "tempo_dashboard_game", "expression_control_game"],
        "mechanisms": ["expression_control_panel", "dynamic_contrast_game"],
        "accent": "#7a58c4",
        "background": "#f4ecff",
    },
    {
        "id": "timbre_detective",
        "label": "音色侦探",
        "hero": "/static/assets/game-packs/音色侦探/background.png",
        "badge": "/static/assets/game-packs/timbre-badge.svg",
        "keywords": ["音色", "乐器", "小提琴", "长笛", "古筝", "二胡", "打击乐"],
        "game_types": ["timbre_match_game", "timbre_detective_game", "music_match_game"],
        "mechanisms": ["timbre_detective_match"],
        "accent": "#2f8f83",
        "background": "#eef7f0",
    },
    {
        "id": "pentatonic_grid",
        "label": "五声宫格",
        "hero": "/static/assets/game-packs/唱名打靶/background.png",
        "badge": "/static/assets/game-packs/pentatonic-badge.svg",
        "keywords": ["五声", "宫", "商", "角", "徵", "羽", "民族", "调式"],
        "game_types": ["mode_puzzle_game", "pentatonic_grid_game"],
        "mechanisms": ["mode_phrase_puzzle"],
        "accent": "#d95d39",
        "background": "#fff1ec",
    },
    {
        "id": "mission_board",
        "label": "课堂任务板",
        "hero": "/static/assets/game-packs/曲式寻宝/background.png",
        "badge": "/static/assets/game-packs/mission-badge.svg",
        "keywords": ["综合", "任务", "合作", "表现", "创编"],
        "game_types": ["lesson_mission_game", "custom_music_game", "creation_mission_game", "scene_expression_game", "singing_ladder_game"],
        "mechanisms": ["lesson_mission_loop", "music_scene_choice", "singing_response_ladder", "music_construction_mission"],
        "accent": "#2f8f83",
        "background": "#f2f6ea",
    },
]


def select_visual_asset_pack(spec: dict[str, Any]) -> dict[str, Any]:
    music_game = spec.get("music_game") if isinstance(spec.get("music_game"), dict) else {}
    mechanic = spec.get("music_element_mechanic") if isinstance(spec.get("music_element_mechanic"), dict) else {}
    text_parts = [
        str(spec.get("target_music_element", "")),
        str(spec.get("target_segment_task", "")),
        str(music_game.get("music_concept", "")),
        str(music_game.get("game_type", "")),
        str(music_game.get("mechanism_id", "")),
        str(mechanic.get("mechanism_id", "")),
    ]
    haystack = " ".join(text_parts).lower()
    game_type = str(music_game.get("game_type", ""))
    mechanism_id = str(music_game.get("mechanism_id") or mechanic.get("mechanism_id") or "")

    ranked = sorted(
        ASSET_PACKS,
        key=lambda pack: _asset_score(pack, haystack, game_type, mechanism_id),
        reverse=True,
    )
    selected = ranked[0] if ranked and _asset_score(ranked[0], haystack, game_type, mechanism_id) > 0 else ASSET_PACKS[-1]
    return {
        "id": selected["id"],
        "label": selected["label"],
        "hero": selected["hero"],
        "badge": selected["badge"],
        "accent": selected["accent"],
        "background": selected["background"],
        "source": "preset_visual_asset_library",
    }


def list_visual_asset_packs() -> list[dict[str, Any]]:
    return ASSET_PACKS


def _asset_score(pack: dict[str, Any], haystack: str, game_type: str, mechanism_id: str) -> int:
    score = 0
    if game_type and game_type in pack.get("game_types", []):
        score += 80
    if mechanism_id and mechanism_id in pack.get("mechanisms", []):
        score += 90
    score += sum(12 for keyword in pack.get("keywords", []) if keyword.lower() in haystack)
    return score
