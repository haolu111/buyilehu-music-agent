# 保存正式游戏模板及其默认参数、难度、玩法、计分和反馈规则
# 这是整个目录中体积很大的文件之一。它定义了多个生产级核心模板，例如：

# beat_guardian_core：节拍守卫；
# rhythm_echo_core：节奏回声；
# pitch_ladder_core：音高阶梯；
# solfege_target_core：唱名打靶；
# timbre_detective_core：音色侦探；
# form_treasure_core：曲式寻宝；
# composition_puzzle_core：创编拼图。

# 每个模板通常包含：

# template_id
# 模板名称
# 适用音乐要素
# 学生操作流程
# 核心游戏循环
# 难度维度
# L1～L5 难度预设
# 计分权重
# 反馈文案
# 默认配置
# 前端技术栈
# 支持的皮肤

# 例如 pitch_ladder_core 会定义：

# 可以使用哪些唱名；
# 每关出现几个音；
# 是否显示唱名提示；
# 是否显示方向提示；
# 判断上行、下行、同音的反馈；
# 音高、顺序、唱名映射和演唱迁移的评分权重。
from __future__ import annotations

import math
from copy import deepcopy
from typing import Any
from uuid import uuid4

from app.services.games.experience_variant_registry import (
    apply_experience_variant,
    get_experience_variant,
    list_experience_variants,
)
from app.services.music.pitch_catalog import PITCH_DEFINITIONS, resolve_pitch_token
from app.services.games.template_blueprint_registry import apply_template_blueprint_contract, get_template_blueprint


RHYTHM_ECHO_DEFAULT_CONFIG: dict[str, Any] = {
    "template_id": "rhythm_echo_core",
    "engine": "phaser_2d",
    "scene_id": "rhythm_echo_scene",
    "game_feel": "arcade_rhythm_echo",
    "game_genre": "memory_echo",
    "runtime_shell": "rhythm_echo_shell",
    "camera_profile": "echo_memory_console",
    "hud_model": "demo_record_accuracy",
    "interaction_model": "listen_memorize_replay",
    "cartoon_role": "电波传呼员",
    "distinctiveness_tags": ["记忆回放", "电波传呼", "录制轨道", "准确率复盘"],
    "student_ui_mode": "game_first",
    "audio_mode": "hybrid",
    "mode": "echo_tap",
    "grade_band": "小学低段",
    "music_concept": "四分音符与八分音符",
    "meter": "2/4",
    "bpm": 92,
    "round_count": 6,
    "bars_per_round": 1,
    "count_in_beats": 4,
    "allow_relisten": True,
    "retry_limit": 3,
    "pass_score": 0.8,
    "input_method": "tap",
    "timing_tolerance_ms": 180,
    "round_length_steps": 2,
    "required_accuracy": 0.8,
    "energy_max": 100,
    "energy_loss_per_miss": 22,
    "combo_milestones": [2, 4, 6],
    "judgement_windows": {"perfect_ms": 95, "good_ms": 210, "late_ms": 320},
    "input_map": {"primary": "Space", "pointer": True},
    "fx_profile": {"hit": "echo_burst", "miss": "track_shake", "success": "skin_echo_finish"},
    "score_model": {"perfect": 120, "good": 80, "wrong": -40, "missed": -60},
    "lesson_audio_sync": {},
    "beat_snap": True,
    "visual_beat_hint": True,
    "subdivision_hint": False,
    "show_timeline_feedback": True,
    "show_text_feedback": True,
    "show_badges": True,
    "skin_id": "rhythm_radio",
    "theme": "节奏电波传呼机",
    "reward_style": "飞船对接徽章",
    "teacher_prompt": "先听清楚，再拍出来，说一说这个节奏哪里稳。",
    "age_ui_profile": "lower_primary",
    "student_task_copy": {
        "listen": "听什么：先完整听一遍目标节奏。",
        "do": "做什么：用点击、拍手或身体动作拍回来。",
        "pass": "怎样过关：节奏顺序和拍点都稳定。",
    },
    "music_reason_prompts": {
        "early": "抢拍了：先等到拍点再出手。",
        "late": "拖拍了：心里的稳定拍要往前带一点。",
        "missing": "漏拍了：目标节奏中间少了一下。",
        "wrong_order": "顺序错了：再听长短和休止的位置。",
        "success": "节奏复刻成功：说出它的长短和疏密特点。",
    },
    "result_transfer_prompt": "用口读或身体律动再表现一次节奏型。",
    "pattern_pool": [
        {"id": "r1", "label": "四 四", "steps": ["quarter", "quarter"], "difficulty": 1},
        {"id": "r2", "label": "四 二八", "steps": ["quarter", "eighth_pair"], "difficulty": 1},
        {"id": "r3", "label": "二八 四", "steps": ["eighth_pair", "quarter"], "difficulty": 1},
        {"id": "r4", "label": "四 休止", "steps": ["quarter", "rest"], "difficulty": 2},
        {"id": "r5", "label": "二分 四", "steps": ["half", "quarter"], "difficulty": 3},
        {"id": "r6", "label": "小切分", "steps": ["syncopation"], "difficulty": 4},
    ],
}


RHYTHM_ECHO_SKIN_PLAY_MODES: dict[str, str] = {
    "rhythm_radio": "radio",
    "echo_cave": "cave",
    "robot_signal": "signal",
    "rain_window": "rain",
    "kitchen_band": "kitchen",
}


BEAT_GUARDIAN_DEFAULT_CONFIG: dict[str, Any] = {
    "template_id": "beat_guardian_core",
    "engine": "phaser_2d",
    "scene_id": "beat_guardian_scene",
    "game_genre": "arcade_guardian",
    "mode": "strong_beat_guard",
    "grade_band": "小学低段",
    "music_concept": "强拍与弱拍",
    "meter": "4/4",
    "bpm": 88,
    "round_count": 5,
    "bars_per_round": 4,
    "mission_duration_bars": 4,
    "target_beats": [1],
    "count_in_bars": 1,
    "count_in_beats": 4,
    "student_ui_mode": "game_first",
    "teacher_panel_mode": "collapsed",
    "audio_mode": "hybrid",
    "strong_beat_sound": "low_drum",
    "weak_beat_sound": "wood_tick",
    "beat_sound_profile": {
        "strong": {"wave": "sine", "frequency": 196, "duration_ms": 110, "gain": 0.28},
        "weak": {"wave": "triangle", "frequency": 392, "duration_ms": 72, "gain": 0.12},
    },
    "lesson_audio_sync": {},
    "feedback_style": "short_student_facing",
    "minimal_hud": True,
    "game_feel": "arcade_rhythm",
    "runtime_shell": "beat_guardian_shell",
    "camera_profile": "side_guard_lane",
    "hud_model": "energy_combo_target",
    "interaction_model": "predict_downbeat_charge",
    "cartoon_role": "护盾充能员",
    "distinctiveness_tags": ["护盾充能", "强拍预判", "弱拍蓄势", "周期延伸"],
    "round_length_beats": 24,
    "energy_max": 100,
    "energy_loss_per_miss": 24,
    "combo_milestones": [3, 6, 8],
    "judgement_windows": {"perfect_ms": 70, "good_ms": 150, "late_ms": 260},
    "input_map": {"primary": "Space", "pointer": True},
    "fx_profile": {"hit": "burst", "miss": "shake", "success": "skin_objective_finish"},
    "score_model": {"perfect": 120, "good": 80, "wrong": -40, "missed": -60},
    "input_method": "tap",
    "timing_tolerance_ms": 170,
    "allow_practice_round": True,
    "show_beat_track": True,
    "show_strong_beat_hint": True,
    "show_weak_beat_hint": False,
    "pass_score": 0.82,
    "combo_required": 6,
    "required_combo": 6,
    "mistake_limit": 5,
    "max_mistakes": 5,
    "skin_id": "castle_gate",
    "skin_play_mode": "gate",
    "theme": "充能护盾",
    "reward_style": "护盾徽章",
    "reward_animation": "shield_wave",
    "skin_objective": "维持护盾",
    "teacher_prompt": "观察护盾收缩并预判每小节第 1 拍，动作要和强拍同时发生，不要听到后补按。",
    "age_ui_profile": "lower_primary",
    "student_task_copy": {
        "listen": "听什么：听清稳定拍和第 1 拍重音周期。",
        "do": "做什么：第 1 拍同步充能，用震波弹开靠近的怪物。",
        "pass": "怎样过关：清掉全部弱拍怪物，别让护盾裂开。",
    },
    "music_reason_prompts": {
        "early": "抢拍了：你比拍点早了一点。",
        "late": "拖拍了：你听到后才按，护盾已经开始放大。",
        "wrong_position": "弱拍先蓄住：等护盾缩到最小的强拍瞬间。",
        "missing": "漏充了：第 1 拍过去了，下一小节提前准备。",
        "success": "怪物清场：说出你怎么预判第 1 拍。",
    },
    "result_transfer_prompt": "回到歌曲里，用身体律动预判每小节第 1 拍。",
}


BEAT_GUARDIAN_SKIN_PLAY_MODES: dict[str, str] = {
    "dragon_boat": "race",
    "castle_gate": "gate",
    "train_conductor": "station",
    "stage_light": "spotlight",
    "space_orbit": "orbit",
}


PITCH_LADDER_DEFAULT_CONFIG: dict[str, Any] = {
    "template_id": "pitch_ladder_core",
    "engine": "phaser_2d",
    "scene_id": "pitch_ladder_scene",
    "game_feel": "map_pitch_climb",
    "game_genre": "map_climb",
    "runtime_shell": "pitch_ladder_map_shell",
    "camera_profile": "vertical_route_map",
    "hud_model": "route_position_direction",
    "interaction_model": "listen_choose_route",
    "cartoon_role": "音高探路者",
    "distinctiveness_tags": ["地图攀爬", "高低路线", "节点前进", "唱回确认"],
    "mode": "high_low_steps",
    "student_ui_mode": "game_first",
    "game_experience": "adventure_climb",
    "first_screen_density": "playfield_only",
    "copy_budget": {"objective_max_chars": 18, "feedback_max_chars": 8},
    "audio_mode": "hybrid",
    "audio_assets": {
        "sfx": {
            "step": "/audio/pitch-ladder/sfx-step.ogg",
            "miss": "/audio/pitch-ladder/sfx-miss.ogg",
            "reward": "/audio/pitch-ladder/sfx-reward.ogg",
            "clear": "/audio/pitch-ladder/sfx-clear.ogg",
        },
    },
    "grade_band": "小学低段",
    "music_concept": "高低与级进",
    "tonic": "C",
    "scale_type": "major_pentatonic",
    "pitch_range": ["do", "re", "mi", "sol", "la"],
    "round_count": 6,
    "notes_per_round": 2,
    "music_elements": {
        "tonic": "C",
        "scale_type": "major_pentatonic",
        "pitch_range": ["do", "re", "mi", "sol", "la"],
        "notes_per_round": 2,
        "round_count": 6,
        "direction_mix": {"higher": 0.4, "same": 0.2, "lower": 0.4},
        "step_skip_mix": {"step": 0.75, "skip": 0.25},
        "show_solfege_hint": True,
        "audio_mode": "hybrid",
        "sing_back_required": True,
    },
    "target_pattern_type": "direction_pair",
    "current_mode": "direction_pair",
    "energy_max": 100,
    "mistake_limit": 3,
    "character_profile": {
        "role": "旋律探险家",
        "idle_animation": "bounce_ready",
        "success_animation": "flag_cheer",
        "fail_animation": "slide_back",
    },
    "reward_model": {
        "token_name": "旋律宝石",
        "tokens_required": 6,
        "final_reward_animation": "summit_flag",
    },
    "fail_pressure_model": {
        "energy_loss_animation": "heart_drop",
        "route_damage_animation": "crack_flash",
        "quick_retry": True,
    },
    "sing_back_required": True,
    "input_map": {"primary": "Space", "pointer": True},
    "input_bindings": {
        "listen": ["Space", "KeyL"],
        "choose_higher": ["ArrowUp", "KeyW"],
        "choose_same": ["ArrowRight", "KeyD"],
        "choose_lower": ["ArrowDown", "KeyS"],
        "voice_check": ["Enter", "KeyV"],
        "teacher_confirm": ["KeyT"],
        "reset": ["KeyR"],
    },
    "fx_profile": {"step": "route_glow", "miss": "map_shake", "success": "summit_finish"},
    "content_manifest": {
        "manifestVersion": 1,
        "assetProfile": "open_sprite_atlas_v1",
        "art": {
            "backgroundKey": "pitch_ladder_mountain_bg",
            "background": "/static/assets/game-packs/pitch-ladder/mountain/backgrounds/mountain-pitch-path-bg.png",
            "heroSeedKey": "pitch_ladder_explorer_seed",
            "heroSeed": "/static/assets/game-packs/pitch-ladder/mountain/characters/pitch-explorer-seed.png",
            "heroPosesKey": "pitch_ladder_explorer_poses",
            "heroPoses": "/static/assets/game-packs/pitch-ladder/mountain/characters/pitch-explorer-poses.png",
            "propsSheetKey": "pitch_ladder_mountain_props",
            "propsSheet": "/static/assets/game-packs/pitch-ladder/mountain/props/mountain-props.png",
        },
        "hero": {
            "key": "pitch_climber",
            "animations": {
                "idle": "pitch_climber_idle",
                "run": "pitch_climber_run",
                "jump": "pitch_climber_jump",
                "fall": "pitch_climber_fall",
                "win": "pitch_climber_win",
                "fail": "pitch_climber_fail",
            },
            "frameSize": {"width": 96, "height": 112},
            "anchor": {"x": 0.5, "y": 0.86},
        },
        "environment": {
            "backgroundLayers": ["sky_gradient", "far_mountains", "near_mountains", "cloud_lane"],
            "platformKey": "singing_platform",
            "goalKey": "summit_flag",
        },
        "ui": {"buttonSkin": "golden_arcade_button", "rewardIcon": "melody_gem", "energyFrame": "heart_energy_frame"},
        "fx": {"hit": "note_spark", "miss": "slide_dust", "reward": "gem_fly", "stageClear": "summit_flash", "voiceTrail": "voice_ribbon"},
        "audio": {"targetTone": "triangle_pitch_prompt", "hit": "soft_chime", "miss": "rubber_slide", "reward": "gem_collect"},
    },
    "quality_gate_profile": {
        "target": "publishable_2d_h5",
        "min_canvas": {"desktop": [760, 420], "mobile": [320, 300]},
        "input_modes": ["pointer", "keyboard", "touch_swipe", "voice", "teacher_fallback"],
        "asset_pipeline": "open_sprite_atlas_v1",
    },
    "voice_control_mode": "listen_then_sing",
    "route_style": "map_native",
    "movement_profile": "walk_arc",
    "hint_density": "low",
    "allow_relisten": True,
    "retry_limit": 3,
    "show_staff_hint": False,
    "show_solfege_hint": True,
    "show_direction_hint": False,
    "pass_score": 0.8,
    "skin_id": "mountain_steps",
    "theme": "音高山路",
    "reward_style": "音阶徽章",
    "teacher_prompt": "先听，再判断第二个音是更高还是更低，最后唱出来。",
    "age_ui_profile": "lower_primary",
    "student_task_copy": {
        "listen": "听什么：先听目标音或短旋律。",
        "do": "做什么：判断更高、更低或走出台阶路线。",
        "pass": "怎样过关：找对路线后唱出来。",
    },
    "music_reason_prompts": {
        "higher": "更高：声音往上走。",
        "lower": "更低：声音往下落。",
        "same": "一样高：两个音保持在同一位置。",
        "wrong": "顺序不稳：再听声音往哪里走。",
        "success": "路线找对了：把这组音唱出来。",
    },
    "result_transfer_prompt": "唱回这组音，并说出旋律往哪里走。",
}


PITCH_LADDER_SKIN_PLAY_MODES: dict[str, str] = {
    "mountain_steps": "mountain",
    "cloud_elevator": "cloud",
    "bamboo_ladder": "bamboo",
    "lantern_tower": "lantern",
}


PITCH_LADDER_ROUTE_OBJECTIVES: dict[str, str] = {
    "mountain": "summit",
    "cloud": "cloud_gate",
    "bamboo": "bamboo_crown",
    "lantern": "lantern_beacon",
}


PITCH_LADDER_SKIN_LABELS: dict[str, dict[str, str]] = {
    "mountain": {"theme": "音高山路", "reward_style": "音阶徽章", "token_name": "旋律宝石"},
    "cloud": {"theme": "云梯升空", "reward_style": "云门徽章", "token_name": "云朵宝石"},
    "bamboo": {"theme": "竹节爬梯", "reward_style": "竹冠徽章", "token_name": "竹音宝石"},
    "lantern": {"theme": "灯塔点灯", "reward_style": "灯塔徽章", "token_name": "灯光宝石"},
}


PITCH_LADDER_SKIN_ART: dict[str, dict[str, str]] = {
    "mountain": {
        "backgroundKey": "pitch_ladder_mountain_bg",
        "background": "/static/assets/game-packs/pitch-ladder/mountain/backgrounds/mountain-pitch-path-bg.png",
        "heroSeedKey": "pitch_ladder_explorer_seed",
        "heroSeed": "/static/assets/game-packs/pitch-ladder/mountain/characters/pitch-explorer-seed.png",
        "heroPosesKey": "pitch_ladder_explorer_poses",
        "heroPoses": "/static/assets/game-packs/pitch-ladder/mountain/characters/pitch-explorer-poses.png",
        "propsSheetKey": "pitch_ladder_mountain_props",
        "propsSheet": "/static/assets/game-packs/pitch-ladder/mountain/props/mountain-props.png",
    },
    "cloud": {
        "backgroundKey": "pitch_ladder_cloud_bg",
        "background": "/static/assets/game-packs/pitch-ladder/cloud/backgrounds/cloud-elevator-bg.png",
        "heroSeedKey": "pitch_ladder_cloud_hero",
        "heroSeed": "/static/assets/game-packs/pitch-ladder/cloud/characters/cloud-explorer-poses-transparent.png",
        "heroPosesKey": "pitch_ladder_cloud_poses",
        "heroPoses": "/static/assets/game-packs/pitch-ladder/cloud/characters/cloud-explorer-poses-transparent.png",
        "propsSheetKey": "pitch_ladder_cloud_props",
        "propsSheet": "/static/assets/game-packs/pitch-ladder/cloud/props/cloud-elevator-props.png",
    },
    "bamboo": {
        "backgroundKey": "pitch_ladder_bamboo_bg",
        "background": "/static/assets/game-packs/pitch-ladder/bamboo/backgrounds/bamboo-ladder-bg.png",
        "heroSeedKey": "pitch_ladder_bamboo_hero",
        "heroSeed": "/static/assets/game-packs/pitch-ladder/bamboo/characters/bamboo-climber-poses-transparent.png",
        "heroPosesKey": "pitch_ladder_bamboo_poses",
        "heroPoses": "/static/assets/game-packs/pitch-ladder/bamboo/characters/bamboo-climber-poses-transparent.png",
        "propsSheetKey": "pitch_ladder_bamboo_props",
        "propsSheet": "/static/assets/game-packs/pitch-ladder/bamboo/props/bamboo-ladder-props.png",
    },
}


PITCH_LADDER_HERO_SPRITE_ANIMATIONS: dict[str, dict[str, Any]] = {
    "idle": {"frames": [0, 1, 2, 3], "frameRate": 4, "repeat": -1},
    "walk": {"frames": [4, 5, 6, 7], "frameRate": 8, "repeat": -1},
    "run": {"frames": [4, 5, 6, 7], "frameRate": 8, "repeat": -1},
    "jump": {"frames": [8, 9], "frameRate": 7, "repeat": 0},
    "fall": {"frames": [10, 11], "frameRate": 7, "repeat": 0},
    "win": {"frames": [12, 13], "frameRate": 5, "repeat": 2},
    "fail": {"frames": [14, 15], "frameRate": 5, "repeat": 1},
}


PITCH_LADDER_HERO_SPRITES: dict[str, dict[str, Any]] = {
    "mountain": {
        "sheetKey": "pitch_ladder_mountain_action_strip",
        "sheet": "/static/assets/game-packs/pitch-ladder/mountain/characters/pitch-explorer-action-strip.png",
        "displayHeight": 112,
        "footOffsetY": 12,
    },
    "cloud": {
        "sheetKey": "pitch_ladder_cloud_action_strip",
        "sheet": "/static/assets/game-packs/pitch-ladder/cloud/characters/cloud-explorer-action-strip.png",
        "displayHeight": 132,
        "footOffsetY": 18,
    },
    "bamboo": {
        "sheetKey": "pitch_ladder_bamboo_action_strip",
        "sheet": "/static/assets/game-packs/pitch-ladder/bamboo/characters/bamboo-climber-action-strip.png",
        "displayHeight": 138,
        "footOffsetY": 20,
    },
}


SOLFEGE_TARGET_DEFAULT_CONFIG: dict[str, Any] = {
    "template_id": "solfege_target_core",
    "engine": "phaser_2d",
    "scene_id": "solfege_target_scene",
    "game_feel": "solfege_target_range",
    "game_genre": "target_range",
    "runtime_shell": "solfege_target_shell",
    "camera_profile": "aiming_target_arena",
    "hud_model": "reticle_hit_singback",
    "interaction_model": "listen_aim_hit_sing",
    "cartoon_role": "唱名小射手",
    "distinctiveness_tags": ["靶场射击", "准星锁定", "唱名命中", "唱回确认"],
    "mode": "listen_and_hit",
    "student_ui_mode": "game_first",
    "audio_mode": "hybrid",
    "grade_band": "小学低段",
    "music_concept": "唱名听辨与模唱",
    "tonic": "C",
    "solfege_system": "movable_do",
    "scale_type": "major_pentatonic",
    "target_solfege": ["do", "mi", "sol"],
    "round_count": 6,
    "notes_per_round": 1,
    "current_mode": "single_target",
    "energy_max": 100,
    "mistake_limit": 3,
    "combo_milestones": [2, 4, 6],
    "input_map": {"primary": "Space", "pointer": True},
    "fx_profile": {"hit": "target_burst", "miss": "reticle_shake", "success": "skin_target_finish"},
    "score_model": {"perfect": 140, "good": 90, "wrong": -45, "missed": -65},
    "arcade_play_model": "bubble_target_chain",
    "target_motion_profile": {"float_amplitude": 8, "float_speed": 0.85, "orbit_jitter": 0.012},
    "asset_role_map": {
        "launcher": "prop-05-cannon-launcher",
        "projectile": "prop-07-note-projectile",
        "trail": "prop-08-orbit-trail",
        "target_primary": "phaser-drawn-solfege-target",
        "target_secondary": "phaser-drawn-solfege-target",
        "gate": "prop-09-singback-gate",
        "combo": "ui-07-hit-comet",
        "miss": "ui-08-miss-crescent",
        "medal": "ui-06-constellation-medal",
    },
    "allow_relisten": True,
    "retry_limit": 3,
    "show_solfege_hint": True,
    "show_pitch_hint": False,
    "require_sing_back": True,
    "sing_back_required": True,
    "teacher_confirm_required": True,
    "mic_assist_enabled": True,
    "pass_score": 0.8,
    "skin_id": "star_target",
    "theme": "唱名星靶场",
    "reward_style": "靶心徽章",
    "teacher_prompt": "先听目标音，在心里唱一遍，再击中对应唱名靶，并开口唱出来。",
    "age_ui_profile": "upper_primary",
    "student_task_copy": {
        "listen": "听什么：听目标音，在心里找到唱名。",
        "do": "做什么：先击中唱名，再唱回确认。",
        "pass": "怎样过关：命中并完成唱回。",
    },
    "music_reason_prompts": {
        "wrong_target": "唱名不对：先在心里唱出目标音。",
        "right_target": "击中唱名：现在把它唱出来。",
        "chain_wrong": "顺序不稳：重新听整组音。",
        "sing_back": "点击不是终点：请用自己的声音唱回。",
        "success": "听辨和唱回完成：说出这个音的位置感。",
    },
    "result_transfer_prompt": "说出这个唱名在旋律里的位置感。",
}


SOLFEGE_TARGET_SKIN_PLAY_MODES: dict[str, str] = {
    "star_target": "star",
    "flower_bloom": "flower",
    "lantern_target": "lantern",
    "archery_field": "archery",
    "bubble_pop": "bubble",
}


TIMBRE_DETECTIVE_SKIN_PLAY_MODES: dict[str, str] = {
    "sound_casebook": "casebook",
    "museum_clues": "museum",
    "forest_echo": "forest",
    "studio_mixer": "studio",
    "shadow_theater": "theater",
}


TIMBRE_DETECTIVE_DEFAULT_CONFIG: dict[str, Any] = {
    "template_id": "timbre_detective_core",
    "engine": "phaser_2d",
    "scene_id": "timbre_detective_scene",
    "game_feel": "animated_detective_caseboard",
    "game_genre": "detective_mystery",
    "runtime_shell": "timbre_detective_shell",
    "camera_profile": "detective_desk_closeup",
    "hud_model": "clue_suspect_evidence",
    "interaction_model": "listen_investigate_drag_evidence_submit",
    "cartoon_role": "声音小侦探",
    "distinctiveness_tags": ["侦探解谜", "声音证物", "嫌疑对象", "证据推理"],
    "mode": "instrument_clue",
    "student_ui_mode": "game_first",
    "audio_mode": "hybrid",
    "grade_band": "小学中段",
    "music_concept": "音色听辨与乐器识别",
    "sound_set": "classroom_instruments",
    "instrument_pool": ["笛子", "二胡", "小提琴", "钢琴", "小鼓", "木鱼"],
    "timbre_traits": ["明亮", "柔和", "短促", "持续", "气息感", "弦鸣", "敲击感"],
    "round_count": 6,
    "choices_per_round": 4,
    "evidence_required": 1,
    "allow_relisten": True,
    "retry_limit": 3,
    "show_wave_hint": True,
    "show_family_hint": False,
    "require_reason": True,
    "ai_clue_enabled": False,
    "ai_clue_policy": "teacher_assist_only",
    "hf_model_id": "MIT/ast-finetuned-audioset-10-10-0.4593",
    "pass_score": 0.8,
    "skin_id": "sound_casebook",
    "theme": "声音案发现场",
    "reward_style": "侦探徽章",
    "teacher_prompt": "先听声音，再找乐器嫌疑人，最后说出你判断的音色证据。",
    "age_ui_profile": "upper_primary",
    "student_task_copy": {
        "listen": "听什么：听声音证物，抓住音色线索。",
        "do": "做什么：选择嫌疑对象，再贴上证据词。",
        "pass": "怎样过关：对象和音色证据都成立。",
    },
    "music_reason_prompts": {
        "wrong_source": "对象错了：复听发声方式和起音。",
        "wrong_family": "家族不对：先判断管、弦、打击或键盘。",
        "weak_evidence": "证据不足：换一个更能说明音色的词。",
        "family_match": "家族判断成立：说出它的发声方式。",
        "success": "证据成立：用音色词解释你的判断。",
    },
    "result_transfer_prompt": "用一个音色词解释为什么是这个乐器/家族。",
}


FORM_TREASURE_SKIN_PLAY_MODES: dict[str, str] = {
    "treasure_map": "map",
    "constellation_path": "constellation",
    "museum_gallery": "gallery",
    "train_route": "train",
    "stage_script": "stage",
}


COMPOSITION_PUZZLE_SKIN_PLAY_MODES: dict[str, str] = {
    "composition_studio": "studio",
    "rhythm_tile_table": "rhythm_table",
    "melody_garden": "melody_garden",
}


FORM_TREASURE_DEFAULT_CONFIG: dict[str, Any] = {
    "template_id": "form_treasure_core",
    "engine": "phaser_2d",
    "scene_id": "form_treasure_scene",
    "game_feel": "form_treasure_hunt",
    "game_genre": "form_treasure_map",
    "runtime_shell": "form_treasure_shell",
    "camera_profile": "timeline_treasure_map",
    "hud_model": "timeline_card_progress",
    "interaction_model": "listen_place_card_use_tool_verify",
    "publish_quality_profile": "arcade_h5",
    "cartoon_role": "曲式寻宝队",
    "distinctiveness_tags": ["曲式寻宝", "段落时间轴", "结构卡排列", "宝藏奖励"],
    "mode": "aba_treasure",
    "student_ui_mode": "game_first",
    "audio_mode": "internal_form",
    "grade_band": "小学高段-初中",
    "music_concept": "曲式结构听辨",
    "form_type": "ABA",
    "section_length_bars": 8,
    "hint_mode": "partial",
    "round_count": 3,
    "allow_relisten": True,
    "retry_limit": 3,
    "pass_score": 0.8,
    "skin_id": "treasure_map",
    "theme": "藏宝图寻宝",
    "reward_style": "结构宝藏",
    "teacher_prompt": "先听段落，再判断相同、重复或对比，最后说出曲式依据。",
    "age_ui_profile": "upper_primary",
    "student_task_copy": {
        "listen": "听什么：听每个段落是否重复、对比或再现。",
        "do": "做什么：放结构卡，排出曲式路线。",
        "pass": "怎样过关：路线正确，并能说出依据。",
    },
    "music_reason_prompts": {
        "wrong_order": "路线还不对：再听主题段有没有回来。",
        "same_section": "重复线索：这一段像前面的主题。",
        "contrast_section": "对比线索：这一段材料变了。",
        "rondo_theme": "回旋主题：主题又回来了。",
        "success": "曲式路线点亮：说出重复、对比或再现依据。",
    },
    "result_transfer_prompt": "指出哪一段像 A 段，哪一段形成对比。",
    "input_actions": ["listen_segment", "select_card", "place_card", "remove_card", "use_tool", "verify", "reset"],
    "fx_profile": {
        "segment_listen": "island_pulse_and_compass",
        "card_place": "card_snap_route_slot",
        "bridge_light": "bridge_and_dotted_path_glow",
        "tool_hint": "scroll_compass_key_reveal",
        "miss": "wrong_route_smoke_shake",
        "treasure_unlock": "chest_open_star_burst",
    },
    "score_model": {
        "perfect": 1000,
        "placed_card": 120,
        "tool_hint": -40,
        "wrong": -120,
    },
}

COMPOSITION_PUZZLE_DEFAULT_CONFIG: dict[str, Any] = {
    "template_id": "composition_puzzle_core",
    "engine": "phaser_2d",
    "scene_id": "composition_puzzle_scene",
    "game_feel": "arcade_composition_studio",
    "game_genre": "constrained_composition_puzzle",
    "runtime_shell": "composition_puzzle_shell",
    "camera_profile": "studio_tile_table",
    "hud_model": "constraint_checklist_progress",
    "interaction_model": "drag_arrange_audition_submit",
    "cartoon_role": "音乐创编师",
    "distinctiveness_tags": ["约束创作", "拖拽拼图", "试听验证", "教师确认"],
    "mode": "melody_rhythm_puzzle",
    "student_ui_mode": "game_first",
    "audio_mode": "internal_composition",
    "grade_band": "小学中段",
    "music_concept": "节奏与旋律创编",
    "meter": "2/4",
    "bpm": 92,
    "tonic": "C",
    "scale_type": "major_pentatonic",
    "phrase_length_bars": 2,
    "composition_total_bars": 2,
    "composition_segment_bars": 2,
    "composition_segments": 1,
    "length_clamped": False,
    "slots_per_bar": 4,
    "round_count": 4,
    "retry_limit": 3,
    "pass_score": 0.8,
    "teacher_confirm_required": True,
    "constraint_profile": "guided",
    "rhythm_cards": [
        {"id": "quarter", "label": "𝅘𝅥", "beats": 1, "kind": "hit", "difficulty": 1},
        {"id": "eighth_pair", "label": "𝅘𝅥𝅮𝅘𝅥𝅮", "beats": 1, "kind": "hit", "difficulty": 1},
        {"id": "sixteenth_four", "label": "𝅘𝅥𝅯𝅘𝅥𝅯𝅘𝅥𝅯𝅘𝅥𝅯", "beats": 1, "kind": "hit", "difficulty": 2},
        {"id": "rest", "label": "𝄽", "beats": 1, "kind": "rest", "difficulty": 2},
    ],
    "melody_cards": ["do", "re", "mi", "sol", "la"],
    "required_elements": ["至少 1 个变化音高", "填满小节", "试听后提交"],
    "skin_id": "composition_studio",
    "skin_play_mode": "studio",
    "theme": "音乐创编教室",
    "reward_style": "创编徽章",
    "teacher_prompt": "先让学生用素材卡拼出短句，试听后检查是否满足节奏或旋律约束，再请学生说明创编理由。",
    "age_ui_profile": "upper_primary",
    "student_task_copy": {
        "listen": "听什么：试听自己拼出的短句，听它是否完整。",
        "do": "做什么：拖拽节奏卡或旋律卡，按要求拼成完整音乐作品。",
        "pass": "怎样过关：自动规则通过后，请教师确认音乐性与创意表达。",
    },
    "music_reason_prompts": {
        "constraint_missing": "还差一个约束：看清规则清单，再调整素材卡。",
        "bar_incomplete": "小节还没有填满：补足节奏时值后再试听。",
        "melody_static": "旋律变化还不够：加入上行、下行或结束音。",
        "teacher_confirm": "规则通过了：请教师听一听并确认创编理由。",
        "success": "创编完成：说出你用了哪些节奏或旋律办法。",
    },
    "result_transfer_prompt": "把作品拍读、唱出或用课堂乐器演一遍，并说明它满足了哪些音乐约束。",
}


CORE_TEMPLATE_ASSET_PACKS: dict[str, str] = {
    "beat_guardian_core": "节拍守卫",
    "rhythm_echo_core": "节奏复刻",
    "solfege_target_core": "唱名打靶",
    "timbre_detective_core": "音色侦探",
    "form_treasure_core": "曲式寻宝",
    "composition_puzzle_core": "composition-puzzle",
}

OPEN_SOURCE_FRONTEND_STACK: dict[str, Any] = {
    "app_framework": "React + Vite",
    "component_library": "Radix Themes",
    "icons": "Lucide React",
    "state": "Zustand",
    "runtime_shell": "react_student_runtime",
    "license_policy": "open_source_only",
    "dependencies": ["React", "Vite", "Radix Themes", "Lucide React", "Zustand", "Phaser"],
    "runtime_boundary": "React/Radix 承载学生端壳、HUD、控件和反馈；Phaser 仅作为游戏画布引擎。",
}

def _template_asset_manifest(template_id: str) -> dict[str, Any] | None:
    pack = CORE_TEMPLATE_ASSET_PACKS.get(template_id)
    if not pack:
        return None
    root = f"/static/assets/game-packs/{pack}"
    extracted = f"{root}/extracted"
    return {
        "background": f"{root}/background.png",
        "poses": {
            "idle": f"{extracted}/pose-01-idle.png",
            "action": f"{extracted}/pose-02-action.png",
            "miss": f"{extracted}/pose-03-miss.png",
            "win": f"{extracted}/pose-04-win.png",
        },
        "props": [f"{extracted}/prop-{index:02d}.png" for index in range(1, 13)],
        "rewards": [f"{extracted}/ui-{index:02d}.png" for index in range(1, 13)],
        "sourcePack": pack,
        "license": "local_generated_assets",
    }


def _attach_template_asset_manifest(config: dict[str, Any], template_id: str) -> None:
    manifest = _template_asset_manifest(template_id)
    if not manifest:
        return
    config["asset_manifest"] = deepcopy(manifest)
    if isinstance(config.get("scene_config"), dict):
        config["scene_config"]["asset_manifest"] = deepcopy(manifest)


GAME_TEMPLATE_REGISTRY: dict[str, dict[str, Any]] = {
    "beat_guardian_core": {
        "template_id": "beat_guardian_core",
        "label": "充能护盾",
        "family": "rhythm",
        "scaffold_id": "beat_guardian",
        "version": "v1",
        "status": "ready",
        "runtime_status": "production",
        "description": "音乐持续进行时，学生观察护盾按小节呼吸，在第 1 拍收缩到最小、最亮的瞬间同步充能，训练稳定拍、强弱规律和提前预判。",
        "open_source_frontend": {
            "app_framework": "React + Vite",
            "component_library": "Radix Themes",
            "game_engine": "Phaser 2D",
            "icons": "Lucide React",
            "state": "Zustand",
        },
        "supported_modes": ["beat_defense", "strong_beat_guard", "meter_gate"],
        "supported_skins": ["castle_gate", "stage_light", "dragon_boat", "train_conductor", "space_orbit"],
        "learning_targets": ["稳定节拍", "强弱拍", "拍号感", "提前预判", "听觉控制"],
        "student_actions": ["听拍", "观察护盾", "预判第 1 拍", "同步充能", "修正下一次"],
        "core_loop": ["任务提示", "预备拍", "护盾脉冲", "学生充能", "即时反馈", "通关复盘"],
        "difficulty_axes": ["bpm", "meter", "downbeat_only", "visual_hint", "tolerance", "music_backing"],
        "difficulty_presets": {
            "L1": {
                "mode": "beat_defense",
                "meter": "2/4",
                "bpm": 76,
                "target_beats": [1],
                "timing_tolerance_ms": 240,
                "show_strong_beat_hint": True,
                "show_weak_beat_hint": True,
            },
            "L2": {
                "mode": "strong_beat_guard",
                "meter": "2/4",
                "bpm": 86,
                "target_beats": [1],
                "timing_tolerance_ms": 205,
                "show_strong_beat_hint": True,
                "show_weak_beat_hint": False,
            },
            "L3": {
                "mode": "strong_beat_guard",
                "meter": "4/4",
                "bpm": 96,
                "target_beats": [1],
                "timing_tolerance_ms": 175,
                "show_strong_beat_hint": True,
                "show_weak_beat_hint": False,
            },
            "L4": {
                "mode": "meter_gate",
                "meter": "3/4",
                "bpm": 104,
                "target_beats": [1],
                "timing_tolerance_ms": 155,
                "show_beat_track": True,
                "show_strong_beat_hint": True,
                "show_weak_beat_hint": False,
                "visual_beat_hint": False,
            },
            "L5": {
                "mode": "meter_gate",
                "meter": "4/4",
                "bpm": 112,
                "target_beats": [1],
                "timing_tolerance_ms": 140,
                "show_beat_track": False,
                "show_strong_beat_hint": False,
                "show_weak_beat_hint": False,
                "visual_beat_hint": False,
            },
        },
        "scoring": {
            "timing_score": 0.4,
            "beat_position_score": 0.35,
            "steadiness_score": 0.15,
            "restraint_score": 0.1,
        },
        "feedback_rules": {
            "early": "你比拍点早了一点，再多预判一点周期。",
            "late": "这一下有点晚，不能听到后才补按。",
            "wrong_position": "弱拍先蓄住，等护盾缩到最小。",
            "missing": "第 1 拍已经过去了，下一小节提前准备。",
            "success": "怪物清场了，现在说一说这一小节的强弱规律。",
        },
        "default_config": BEAT_GUARDIAN_DEFAULT_CONFIG,
    },
    "pitch_ladder_core": {
        "template_id": "pitch_ladder_core",
        "label": "音高爬梯",
        "family": "melody",
        "scaffold_id": "pitch_ladder",
        "version": "v1",
        "status": "ready",
        "runtime_status": "production",
        "description": "把听到的音高关系映射为空间台阶，让学生先听、判断高低或唱名，再通过模唱完成迁移。",
        "open_source_frontend": {
            "app_framework": "React + Vite",
            "component_library": "Radix Themes",
            "icons": "Lucide React",
            "state": "Zustand",
        },
        "supported_modes": ["high_low_steps", "solfege_ladder", "melody_climb"],
        "supported_skins": ["mountain_steps", "cloud_elevator", "bamboo_ladder", "lantern_tower"],
        "learning_targets": ["音高方向", "级进与跳进", "唱名映射", "音列记忆", "模唱迁移"],
        "student_actions": ["先听", "判断高低", "选择台阶", "修正", "唱出来"],
        "core_loop": ["播放目标音列", "学生判断或定位", "即时反馈", "重新聆听", "模唱复盘"],
        "difficulty_axes": ["pitch_range", "notes_per_round", "direction_mix", "solfege_hint", "memory_span"],
        "difficulty_presets": {
            "L1": {
                "mode": "high_low_steps",
                "pitch_range": ["do", "mi", "sol"],
                "notes_per_round": 2,
                "show_solfege_hint": True,
                "show_direction_hint": True,
            },
            "L2": {
                "mode": "high_low_steps",
                "pitch_range": ["do", "re", "mi", "sol"],
                "notes_per_round": 2,
                "show_solfege_hint": True,
                "show_direction_hint": False,
            },
            "L3": {
                "mode": "solfege_ladder",
                "pitch_range": ["do", "re", "mi", "sol", "la"],
                "notes_per_round": 1,
                "show_solfege_hint": True,
                "show_direction_hint": False,
            },
            "L4": {
                "mode": "melody_climb",
                "pitch_range": ["do", "re", "mi", "fa", "sol", "la"],
                "notes_per_round": 3,
                "show_solfege_hint": True,
                "show_direction_hint": False,
            },
            "L5": {
                "mode": "melody_climb",
                "pitch_range": ["do", "re", "mi", "fa", "sol", "la", "ti", "do_high"],
                "notes_per_round": 4,
                "show_solfege_hint": False,
                "show_direction_hint": False,
            },
        },
        "scoring": {
            "pitch_relation_score": 0.35,
            "sequence_score": 0.3,
            "solfege_mapping_score": 0.2,
            "vocal_transfer_score": 0.15,
        },
        "feedback_rules": {
            "higher": "第二个音更高，声音往上走。",
            "lower": "第二个音更低，声音往下落。",
            "same": "两个音一样高，先稳住再唱。",
            "wrong": "再听一次，注意声音是往上、往下，还是保持不变。",
            "success": "音高路线找对了，现在把这组音唱出来。",
        },
        "default_config": PITCH_LADDER_DEFAULT_CONFIG,
    },
    "solfege_target_core": {
        "template_id": "solfege_target_core",
        "label": "唱名打靶",
        "family": "melody",
        "scaffold_id": "solfege_target",
        "version": "v1",
        "status": "ready",
        "runtime_status": "production",
        "description": "学生听目标音、瞄准唱名靶、击中后唱回确认，训练唱名归属、内听和模唱迁移。",
        "open_source_frontend": {
            "app_framework": "React + Vite",
            "component_library": "Radix Themes",
            "icons": "Lucide React",
            "state": "Zustand",
        },
        "supported_modes": ["listen_and_hit", "aim_and_sing", "target_chain"],
        "supported_skins": ["star_target", "flower_bloom", "lantern_target", "archery_field", "bubble_pop"],
        "learning_targets": ["唱名听辨", "首调归属", "内听", "模唱", "短音组记忆"],
        "student_actions": ["听目标音", "心里唱名", "瞄准靶心", "击中", "唱回确认"],
        "core_loop": ["播放目标音", "学生击中唱名靶", "即时反馈", "唱回确认", "教师复盘"],
        "difficulty_axes": ["target_solfege", "notes_per_round", "solfege_hint", "relisten_limit", "sing_back"],
        "difficulty_presets": {
            "L1": {
                "mode": "listen_and_hit",
                "target_solfege": ["do", "mi", "sol"],
                "notes_per_round": 1,
                "show_solfege_hint": True,
                "show_pitch_hint": True,
            },
            "L2": {
                "mode": "listen_and_hit",
                "target_solfege": ["do", "re", "mi", "sol", "la"],
                "notes_per_round": 1,
                "show_solfege_hint": True,
                "show_pitch_hint": False,
            },
            "L3": {
                "mode": "aim_and_sing",
                "target_solfege": ["do", "re", "mi", "sol", "la"],
                "notes_per_round": 1,
                "show_solfege_hint": True,
                "show_pitch_hint": False,
                "require_sing_back": True,
            },
            "L4": {
                "mode": "target_chain",
                "target_solfege": ["do", "re", "mi", "fa", "sol", "la"],
                "notes_per_round": 2,
                "show_solfege_hint": True,
                "show_pitch_hint": False,
                "require_sing_back": True,
            },
            "L5": {
                "mode": "target_chain",
                "target_solfege": ["do", "re", "mi", "fa", "sol", "la", "ti", "do_high"],
                "notes_per_round": 4,
                "show_solfege_hint": False,
                "show_pitch_hint": False,
                "require_sing_back": True,
            },
        },
        "scoring": {
            "solfege_accuracy": 0.45,
            "listening_focus": 0.15,
            "sequence_memory": 0.2,
            "sing_back_completion": 0.2,
        },
        "feedback_rules": {
            "wrong_target": "再听一次，先在心里唱出唱名，再瞄准靶心。",
            "right_target": "唱名靶击中了，现在把这个音唱出来。",
            "chain_wrong": "靶心顺序还不稳，重新听一遍整组音。",
            "sing_back": "点击不是终点，请用自己的声音完成唱回。",
            "success": "听辨、击中、唱回都完成了，说说这个音在旋律里的位置感。",
        },
        "default_config": SOLFEGE_TARGET_DEFAULT_CONFIG,
    },
    "timbre_detective_core": {
        "template_id": "timbre_detective_core",
        "label": "音色侦探",
        "family": "timbre",
        "scaffold_id": "timbre_detective",
        "version": "v1",
        "status": "ready",
        "runtime_status": "production",
        "description": "学生以侦探身份听声音证物、筛选嫌疑乐器、标记音色证据，并说出判断依据。",
        "open_source_frontend": {
            "app_framework": "React + Vite",
            "component_library": "Radix Themes",
            "icons": "Lucide React",
            "state": "Zustand",
            "optional_ai": "Hugging Face Transformers.js audio classification as a teacher-controlled clue",
        },
        "supported_modes": ["instrument_clue", "family_sorting", "compare_twins"],
        "supported_skins": ["sound_casebook", "museum_clues", "forest_echo", "studio_mixer", "shadow_theater"],
        "learning_targets": ["音色听辨", "乐器识别", "发声方式", "音色描述", "作品聆听迁移"],
        "student_actions": ["听取线索", "搜查证物", "比较嫌疑人", "标记证据", "提交推理", "复听修正"],
        "core_loop": ["播放声音证物", "选择嫌疑乐器或家族", "选择音色证据", "即时反馈", "口头说明理由"],
        "difficulty_axes": ["instrument_pool", "choices_per_round", "evidence_required", "family_hint", "comparison_similarity"],
        "difficulty_presets": {
            "L1": {
                "mode": "instrument_clue",
                "instrument_pool": ["笛子", "钢琴", "小鼓"],
                "choices_per_round": 3,
                "evidence_required": 1,
                "show_family_hint": True,
            },
            "L2": {
                "mode": "instrument_clue",
                "instrument_pool": ["笛子", "二胡", "钢琴", "小鼓", "木鱼"],
                "choices_per_round": 4,
                "evidence_required": 1,
                "show_family_hint": False,
            },
            "L3": {
                "mode": "family_sorting",
                "instrument_pool": ["笛子", "二胡", "小提琴", "钢琴", "小鼓", "木鱼"],
                "choices_per_round": 4,
                "evidence_required": 1,
                "show_family_hint": False,
            },
            "L4": {
                "mode": "compare_twins",
                "instrument_pool": ["笛子", "长笛", "二胡", "小提琴", "小鼓", "木鱼"],
                "choices_per_round": 4,
                "evidence_required": 2,
                "show_family_hint": False,
            },
            "L5": {
                "mode": "compare_twins",
                "instrument_pool": ["笛子", "长笛", "二胡", "小提琴", "钢琴", "古筝", "小鼓", "木鱼"],
                "choices_per_round": 5,
                "evidence_required": 2,
                "show_family_hint": False,
            },
        },
        "scoring": {
            "source_accuracy": 0.4,
            "evidence_score": 0.3,
            "comparison_score": 0.2,
            "listening_focus": 0.1,
        },
        "feedback_rules": {
            "wrong_source": "嫌疑乐器还不对，复听时注意声音是气息、弦鸣还是敲击产生的。",
            "weak_evidence": "证据还不够有力，请找一个更能说明音色特点的词。",
            "family_match": "家族判断成立，现在说出它的发声方式。",
            "compare_success": "你听出了两个相似音色的差异，这就是侦探耳朵。",
            "success": "破案成功：乐器和音色证据都能说清楚。",
        },
        "default_config": TIMBRE_DETECTIVE_DEFAULT_CONFIG,
    },
    "form_treasure_core": {
        "template_id": "form_treasure_core",
        "label": "曲式寻宝",
        "family": "form",
        "scaffold_id": "form_treasure",
        "version": "v1",
        "status": "ready",
        "runtime_status": "production",
        "description": "学生听辨不同段落，把结构卡排列成 ABA、回旋或重复对比路线，训练曲式结构感知和段落命名。",
        "open_source_frontend": {
            "app_framework": "React + Vite",
            "component_library": "Radix Themes",
            "game_engine": "Phaser 2D",
            "icons": "Lucide React",
            "state": "Zustand",
        },
        "supported_modes": ["aba_treasure", "rondo_treasure", "repeat_contrast"],
        "supported_skins": ["treasure_map", "constellation_path", "museum_gallery", "train_route", "stage_script"],
        "learning_targets": ["曲式结构", "ABA", "回旋曲式", "重复与对比", "段落命名"],
        "student_actions": ["听段落", "选择结构卡", "排列曲式", "命名段落", "验证路线", "复盘依据"],
        "core_loop": ["播放段落", "观察时间轴", "排列结构卡", "验证答案", "点亮宝藏", "说出曲式依据"],
        "difficulty_axes": ["form_type", "section_length_bars", "hint_mode", "round_count", "relisten"],
        "difficulty_presets": {
            "L1": {"form_type": "ABA", "mode": "aba_treasure", "section_length_bars": 4, "hint_mode": "guided", "round_count": 2},
            "L2": {"form_type": "ABA", "mode": "aba_treasure", "section_length_bars": 8, "hint_mode": "guided", "round_count": 3},
            "L3": {"form_type": "ABA", "mode": "aba_treasure", "section_length_bars": 8, "hint_mode": "partial", "round_count": 3},
            "L4": {"form_type": "回旋", "mode": "rondo_treasure", "section_length_bars": 12, "hint_mode": "partial", "round_count": 4},
            "L5": {"form_type": "重复对比", "mode": "repeat_contrast", "section_length_bars": 16, "hint_mode": "challenge", "round_count": 4},
        },
        "scoring": {
            "segment_identification": 0.35,
            "structure_order": 0.35,
            "listening_focus": 0.15,
            "verbal_transfer": 0.15,
        },
        "feedback_rules": {
            "wrong_order": "路线还不对，再听主题段有没有回来。",
            "same_section": "你找到了相同段落，这是曲式线索。",
            "contrast_section": "这个段落有对比，请换一张结构卡。",
            "success": "曲式路线点亮了，现在说出你的段落依据。",
        },
        "default_config": FORM_TREASURE_DEFAULT_CONFIG,
    },
    "composition_puzzle_core": {
        "template_id": "composition_puzzle_core",
        "label": "拼图创编工坊",
        "family": "composition",
        "scaffold_id": "composition_puzzle",
        "version": "v1",
        "status": "ready",
        "runtime_status": "production",
        "description": "学生像 4399 小游戏一样拖拽节奏卡、旋律卡或音符组合卡到创编轨道，试听后按音乐约束自动检查，并由教师确认开放创作质量。",
        "open_source_frontend": {
            "app_framework": "React + Vite",
            "component_library": "Radix Themes",
            "game_engine": "Phaser 2D",
            "icons": "Lucide React",
            "state": "Zustand",
        },
        "supported_modes": ["rhythm_puzzle_composition", "melody_puzzle_creation", "melody_rhythm_puzzle"],
        "supported_skins": ["composition_studio", "rhythm_tile_table", "melody_garden"],
        "learning_targets": ["节奏创编", "旋律创作", "音高与时值组合", "试听修正", "创意表达"],
        "student_actions": ["选素材", "拖拽拼接", "试听作品", "检查约束", "修改", "教师确认"],
        "core_loop": ["进入关卡", "选择素材卡", "拼入作品轨道", "试听验证", "规则检查", "教师确认", "通关奖励"],
        "difficulty_axes": ["composition_total_bars", "composition_segment_bars", "slots_per_bar", "constraint_profile", "rhythm_card_density", "melody_card_count"],
        "difficulty_presets": {
            "L1": {"phrase_length_bars": 1, "constraint_profile": "guided", "round_count": 3},
            "L2": {"phrase_length_bars": 2, "constraint_profile": "guided", "round_count": 4},
            "L3": {"phrase_length_bars": 2, "constraint_profile": "balanced", "round_count": 4},
            "L4": {"phrase_length_bars": 3, "constraint_profile": "balanced", "round_count": 5},
            "L5": {"phrase_length_bars": 4, "constraint_profile": "challenge", "round_count": 6},
        },
        "scoring": {
            "constraint_score": 0.45,
            "completion_score": 0.25,
            "audition_revision_score": 0.15,
            "teacher_confirm_score": 0.15,
        },
        "feedback_rules": {
            "constraint_missing": "还有约束没有满足，请调整素材卡。",
            "bar_incomplete": "作品轨道还没有填满，先补足小节。",
            "melody_static": "旋律变化还不够，请加入上行、下行或结束音。",
            "teacher_confirm": "规则通过，请教师听辨并确认创编理由。",
            "success": "创编完成：说出你用了哪些音乐办法。",
        },
        "default_config": COMPOSITION_PUZZLE_DEFAULT_CONFIG,
    },
    "rhythm_echo_core": {
        "template_id": "rhythm_echo_core",
        "label": "节奏复刻",
        "family": "rhythm",
        "scaffold_id": "rhythm_recall",
        "version": "v1",
        "status": "ready",
        "runtime_status": "production",
        "description": "听示范、复刻拍点、查看时间轴反馈，再重试或通关的时间判定型节奏模板。",
        "open_source_frontend": {
            "app_framework": "React + Vite",
            "component_library": "Radix Themes",
            "icons": "Lucide React",
            "state": "Zustand",
        },
        "supported_modes": ["echo_tap", "echo_body_percussion", "echo_chain"],
        "supported_skins": ["rhythm_radio", "echo_cave", "robot_signal", "rain_window", "kitchen_band"],
        "learning_targets": ["稳拍", "时值辨识", "节奏模仿", "节奏记忆", "表现迁移"],
        "student_actions": ["先听", "复刻", "看反馈", "修正", "再表现"],
        "core_loop": ["播放示范", "倒计时准备", "学生输入", "时间判定", "反馈复盘", "重试或过关"],
        "difficulty_axes": [
            "bpm",
            "bars_per_round",
            "pattern_density",
            "rest_usage",
            "dotted_usage",
            "syncopation_usage",
            "memory_span",
        ],
        "difficulty_presets": {
            "L1": {
                "bpm": 84,
                "bars_per_round": 1,
                "allowed_difficulty": 1,
                "timing_tolerance_ms": 220,
                "required_accuracy": 0.65,
                "energy_loss_per_miss": 14,
                "round_length_steps": 2,
                "judgement_windows": {"perfect_ms": 95, "good_ms": 210, "late_ms": 340},
            },
            "L2": {
                "bpm": 92,
                "bars_per_round": 1,
                "allowed_difficulty": 2,
                "timing_tolerance_ms": 190,
                "required_accuracy": 0.75,
                "energy_loss_per_miss": 18,
                "round_length_steps": 3,
                "judgement_windows": {"perfect_ms": 85, "good_ms": 185, "late_ms": 300},
            },
            "L3": {
                "bpm": 100,
                "bars_per_round": 2,
                "allowed_difficulty": 3,
                "timing_tolerance_ms": 170,
                "required_accuracy": 0.8,
                "energy_loss_per_miss": 22,
                "round_length_steps": 4,
                "judgement_windows": {"perfect_ms": 70, "good_ms": 160, "late_ms": 270},
            },
            "L4": {
                "bpm": 108,
                "bars_per_round": 2,
                "allowed_difficulty": 4,
                "timing_tolerance_ms": 150,
                "required_accuracy": 0.85,
                "energy_loss_per_miss": 26,
                "round_length_steps": 5,
                "judgement_windows": {"perfect_ms": 60, "good_ms": 140, "late_ms": 240},
            },
            "L5": {
                "bpm": 112,
                "bars_per_round": 2,
                "allowed_difficulty": 4,
                "timing_tolerance_ms": 140,
                "required_accuracy": 0.9,
                "energy_loss_per_miss": 30,
                "round_length_steps": 6,
                "judgement_windows": {"perfect_ms": 50, "good_ms": 125, "late_ms": 220},
                "mode": "echo_chain",
            },
        },
        "scoring": {
            "pulse_score": 0.45,
            "pattern_score": 0.4,
            "completion_score": 0.15,
        },
        "feedback_rules": {
            "early": "前面有点抢拍，先等住稳定拍点。",
            "late": "后面有点拖拍，跟着心里的拍子走。",
            "missing": "中间少了一拍，再听一次目标节奏。",
            "wrong_order": "节奏顺序和示范还不一致。",
            "success": "节奏复刻成功，现在拍一遍并说出它的特点。",
        },
        "default_config": RHYTHM_ECHO_DEFAULT_CONFIG,
    }
}


GAME_SKIN_REGISTRY: dict[str, dict[str, Any]] = {
    "castle_gate": {
        "skin_id": "castle_gate",
        "template_id": "beat_guardian_core",
        "label": "充能护盾",
        "aesthetic": "发光护盾、呼吸节拍、弱拍怪物、强拍震波",
        "classroom_scene": "适合强拍弱拍、拍号感、稳定进入训练",
    },
    "stage_light": {
        "skin_id": "stage_light",
        "template_id": "beat_guardian_core",
        "label": "舞台追光",
        "aesthetic": "舞台灯光扫过拍位，强拍像主灯亮起",
        "classroom_scene": "适合表演前的进入时机和合奏稳拍",
    },
    "dragon_boat": {
        "skin_id": "dragon_boat",
        "template_id": "beat_guardian_core",
        "label": "龙舟鼓点",
        "aesthetic": "龙舟鼓手、船桨节奏、强拍鼓槌落点",
        "classroom_scene": "适合民俗音乐、二拍子律动、身体参与",
    },
    "train_conductor": {
        "skin_id": "train_conductor",
        "template_id": "beat_guardian_core",
        "label": "节拍列车",
        "aesthetic": "列车进站、车轮稳定滚动、目标站台开门",
        "classroom_scene": "适合低年级稳定拍和速度变化感知",
    },
    "space_orbit": {
        "skin_id": "space_orbit",
        "template_id": "beat_guardian_core",
        "label": "星球轨道",
        "aesthetic": "星球按拍运行，目标拍位出现轨道窗口",
        "classroom_scene": "适合少视觉提示后的内在节拍保持",
    },
    "rhythm_radio": {
        "skin_id": "rhythm_radio",
        "template_id": "rhythm_echo_core",
        "label": "节奏电波传呼机",
        "aesthetic": "电波轨道、传呼机按钮、飞船对接反馈",
        "classroom_scene": "适合长短节奏听辨、记忆复刻和时间轴复盘",
    },
    "echo_cave": {
        "skin_id": "echo_cave",
        "template_id": "rhythm_echo_core",
        "label": "回声山洞",
        "aesthetic": "山洞回声把示范节奏反射回来",
        "classroom_scene": "适合先听后模仿、延迟记忆训练",
    },
    "robot_signal": {
        "skin_id": "robot_signal",
        "template_id": "rhythm_echo_core",
        "label": "机器人信号",
        "aesthetic": "信号灯、脉冲格、机器伙伴解析节奏",
        "classroom_scene": "适合节奏编码、切分和休止辨认",
    },
    "rain_window": {
        "skin_id": "rain_window",
        "template_id": "rhythm_echo_core",
        "label": "雨点窗台",
        "aesthetic": "雨滴按节奏落在窗格上",
        "classroom_scene": "适合轻柔音色、长短时值和疏密变化",
    },
    "kitchen_band": {
        "skin_id": "kitchen_band",
        "template_id": "rhythm_echo_core",
        "label": "厨房乐队",
        "aesthetic": "杯盘锅勺变成节奏声部",
        "classroom_scene": "适合创意实践、身体与生活声音迁移",
    },
    "mountain_steps": {
        "skin_id": "mountain_steps",
        "template_id": "pitch_ladder_core",
        "label": "音高山路",
        "aesthetic": "山路台阶表现音高上行与下行",
        "classroom_scene": "适合高低方向、级进和跳进入门",
    },
    "cloud_elevator": {
        "skin_id": "cloud_elevator",
        "template_id": "pitch_ladder_core",
        "label": "云梯升空",
        "aesthetic": "云梯升降表现音高空间变化",
        "classroom_scene": "适合低年级音高方向判断",
    },
    "bamboo_ladder": {
        "skin_id": "bamboo_ladder",
        "template_id": "pitch_ladder_core",
        "label": "竹节爬梯",
        "aesthetic": "竹节层层向上，唱名落在不同竹节",
        "classroom_scene": "适合中国风音乐材料和唱名定位",
    },
    "lantern_tower": {
        "skin_id": "lantern_tower",
        "template_id": "pitch_ladder_core",
        "label": "灯塔点灯",
        "aesthetic": "灯塔楼层按音高点亮",
        "classroom_scene": "适合短旋律记忆和音列路线复述",
    },
    "star_target": {
        "skin_id": "star_target",
        "template_id": "solfege_target_core",
        "label": "唱名星靶场",
        "aesthetic": "星球靶围绕发声星核，击中后星轨亮起",
        "classroom_scene": "适合低段三音组、五声音阶唱名听辨",
    },
    "flower_bloom": {
        "skin_id": "flower_bloom",
        "template_id": "solfege_target_core",
        "label": "花朵绽放",
        "aesthetic": "唱名花瓣随击中和唱回逐层开放",
        "classroom_scene": "适合低年级温和反馈和集体模唱",
    },
    "lantern_target": {
        "skin_id": "lantern_target",
        "template_id": "solfege_target_core",
        "label": "灯笼靶会",
        "aesthetic": "唱名灯笼悬挂成圆阵，击中后灯火变亮",
        "classroom_scene": "适合中国风音乐材料、民歌唱名训练",
    },
    "archery_field": {
        "skin_id": "archery_field",
        "template_id": "solfege_target_core",
        "label": "音乐弓箭场",
        "aesthetic": "准星、弓弦和靶环强调瞄准与击中动作",
        "classroom_scene": "适合中高年级快速听辨和短音组记忆",
    },
    "bubble_pop": {
        "skin_id": "bubble_pop",
        "template_id": "solfege_target_core",
        "label": "泡泡唱名",
        "aesthetic": "唱名泡泡漂浮，击中后轻盈弹开",
        "classroom_scene": "适合低年级游戏化入门和轻声模唱",
    },
    "sound_casebook": {
        "skin_id": "sound_casebook",
        "template_id": "timbre_detective_core",
        "label": "声音案卷",
        "aesthetic": "侦探案桌、声音证物、嫌疑乐器卡和证据贴纸",
        "classroom_scene": "适合标准音色听辨和乐器识别",
    },
    "museum_clues": {
        "skin_id": "museum_clues",
        "template_id": "timbre_detective_core",
        "label": "乐器博物馆",
        "aesthetic": "展柜、藏品标签和乐器家族归档",
        "classroom_scene": "适合乐器分类、发声方式和文化理解",
    },
    "forest_echo": {
        "skin_id": "forest_echo",
        "template_id": "timbre_detective_core",
        "label": "森林回声",
        "aesthetic": "树影、回声波纹和自然声音线索",
        "classroom_scene": "适合自然声与乐器音色对比",
    },
    "studio_mixer": {
        "skin_id": "studio_mixer",
        "template_id": "timbre_detective_core",
        "label": "录音棚调音台",
        "aesthetic": "推子、波形、频谱和音色参数",
        "classroom_scene": "适合高年级理解明亮度、起音、延音等音色属性",
    },
    "shadow_theater": {
        "skin_id": "shadow_theater",
        "template_id": "timbre_detective_core",
        "label": "声影剧场",
        "aesthetic": "皮影、剪影舞台和民族乐器声影",
        "classroom_scene": "适合民族乐器、故事化听赏和审美表达",
    },
    "treasure_map": {
        "skin_id": "treasure_map",
        "template_id": "form_treasure_core",
        "label": "藏宝图寻宝",
        "aesthetic": "藏宝图、段落岛屿、路线点亮和宝箱奖励",
        "classroom_scene": "适合 ABA、重复对比和段落结构入门",
    },
    "constellation_path": {
        "skin_id": "constellation_path",
        "template_id": "form_treasure_core",
        "label": "星图航线",
        "aesthetic": "星座航线、段落星点和终点星门",
        "classroom_scene": "适合回旋曲式和多段结构记忆",
    },
    "museum_gallery": {
        "skin_id": "museum_gallery",
        "template_id": "form_treasure_core",
        "label": "音乐展馆",
        "aesthetic": "展厅、作品分区、主题展牌和结构导览",
        "classroom_scene": "适合听赏课中的曲式结构归纳",
    },
    "train_route": {
        "skin_id": "train_route",
        "template_id": "form_treasure_core",
        "label": "音乐列车",
        "aesthetic": "列车路线、段落站台和重复返站",
        "classroom_scene": "适合重复、对比和回到主题段的结构感知",
    },
    "stage_script": {
        "skin_id": "stage_script",
        "template_id": "form_treasure_core",
        "label": "剧场分幕",
        "aesthetic": "舞台分幕、灯光段落和剧本结构卡",
        "classroom_scene": "适合戏剧化听赏、段落命名和主题再现",
    },
    "composition_studio": {
        "skin_id": "composition_studio",
        "template_id": "composition_puzzle_core",
        "label": "音乐创编教室",
        "aesthetic": "卡通音乐教室、素材架、作品轨道和通关徽章",
        "classroom_scene": "适合节奏、旋律或综合音乐要素的约束创作",
    },
    "rhythm_tile_table": {
        "skin_id": "rhythm_tile_table",
        "template_id": "composition_puzzle_core",
        "label": "节奏积木桌",
        "aesthetic": "节奏积木、拍点轨道、试听波纹和鼓点奖励",
        "classroom_scene": "适合时值、休止、附点和切分的节奏创编",
    },
    "melody_garden": {
        "skin_id": "melody_garden",
        "template_id": "composition_puzzle_core",
        "label": "旋律花园",
        "aesthetic": "音符花朵、旋律藤蔓、上行下行路径和花章奖励",
        "classroom_scene": "适合唱名、音高走向和旋律短句创作",
    },
}


def list_game_templates() -> list[dict[str, Any]]:
    return [
        _public_template(template)
        for template in sorted(GAME_TEMPLATE_REGISTRY.values(), key=lambda item: str(item.get("label", "")))
    ]


def list_game_skins(template_id: str | None = None) -> list[dict[str, Any]]:
    skins = [
        _public_skin(skin)
        for skin in GAME_SKIN_REGISTRY.values()
        if template_id is None or skin.get("template_id") == template_id
    ]
    return sorted(skins, key=lambda item: (str(item.get("template_id", "")), str(item.get("label", ""))))


def get_game_skin(skin_id: str) -> dict[str, Any] | None:
    skin = GAME_SKIN_REGISTRY.get(str(skin_id))
    return _public_skin(skin) if skin else None


def get_game_template(template_id: str) -> dict[str, Any] | None:
    template = GAME_TEMPLATE_REGISTRY.get(template_id)
    return _with_frontend_policy(template) if template else None


def build_game_instance(payload: dict[str, Any]) -> dict[str, Any]:
    template_id = str(payload.get("template_id") or "rhythm_echo_core").strip()
    template = get_game_template(template_id)
    if not template:
        raise ValueError(f"未知游戏模板：{template_id}")

    config = deepcopy(template["default_config"])
    difficulty = str(payload.get("difficulty") or payload.get("difficulty_preset") or "L2").strip().upper()
    preset = template.get("difficulty_presets", {}).get(difficulty, {})
    config.update(preset)
    overrides = _allowed_overrides(payload)
    teacher_config_fields = set(overrides)
    config.update(overrides)
    config["_content_manifest_explicit"] = "content_manifest" in payload
    config["_teacher_config_fields"] = teacher_config_fields
    config["template_id"] = template_id
    config["frontend_policy"] = template["frontend_policy"]
    config["forbid_standalone_web_trio"] = template["forbid_standalone_web_trio"]
    config["open_source_frontend"] = deepcopy(template["open_source_frontend"])
    config["difficulty"] = difficulty if preset else "custom"
    if template_id == "rhythm_echo_core":
        config["pattern_pool"] = _filter_pattern_pool(config, int(config.get("allowed_difficulty") or 5))
        config = _normalize_rhythm_echo_config(config)
    elif template_id == "beat_guardian_core":
        config = _normalize_beat_guardian_config(config)
    elif template_id == "pitch_ladder_core":
        config = _normalize_pitch_ladder_config(config)
    elif template_id == "solfege_target_core":
        config = _normalize_solfege_target_config(config)
    elif template_id == "timbre_detective_core":
        config = _normalize_timbre_detective_config(config)
    elif template_id == "form_treasure_core":
        config = _normalize_form_treasure_config(config)
    elif template_id == "composition_puzzle_core":
        config = _normalize_composition_puzzle_config(config)
    config["skin_id"] = _normalize_skin_id(template_id, config.get("skin_id"))
    if template_id == "beat_guardian_core" and isinstance(config.get("scene_config"), dict):
        config["skin_play_mode"] = _normalize_beat_guardian_skin_play_mode(config.get("skin_play_mode"), config["skin_id"])
        config["scene_config"]["skin_id"] = config["skin_id"]
        config["scene_config"]["skin_play_mode"] = config["skin_play_mode"]
        config["scene_config"]["reward_animation"] = config.get("reward_animation") or _reward_animation_for_skin(config["skin_id"])
    if template_id == "rhythm_echo_core" and isinstance(config.get("scene_config"), dict):
        config["skin_play_mode"] = _normalize_rhythm_echo_skin_play_mode(config.get("skin_play_mode"), config["skin_id"])
        config["scene_config"]["skin_id"] = config["skin_id"]
        config["scene_config"]["skin_play_mode"] = config["skin_play_mode"]
    if template_id == "pitch_ladder_core" and isinstance(config.get("scene_config"), dict):
        config["skin_play_mode"] = _normalize_pitch_ladder_skin_play_mode(config.get("skin_play_mode"), config["skin_id"])
        config["scene_config"]["skin_id"] = config["skin_id"]
        config["scene_config"]["skin_play_mode"] = config["skin_play_mode"]
    if template_id == "solfege_target_core" and isinstance(config.get("scene_config"), dict):
        config["skin_play_mode"] = _normalize_solfege_target_skin_play_mode(config.get("skin_play_mode"), config["skin_id"])
        config["scene_config"]["skin_id"] = config["skin_id"]
        config["scene_config"]["skin_play_mode"] = config["skin_play_mode"]
    if template_id == "timbre_detective_core" and isinstance(config.get("scene_config"), dict):
        config["skin_play_mode"] = _normalize_timbre_detective_skin_play_mode(config.get("skin_play_mode"), config["skin_id"])
        config["scene_config"]["skin_id"] = config["skin_id"]
        config["scene_config"]["skin_play_mode"] = config["skin_play_mode"]
    if template_id == "form_treasure_core" and isinstance(config.get("scene_config"), dict):
        config["skin_play_mode"] = _normalize_form_treasure_skin_play_mode(config.get("skin_play_mode"), config["skin_id"])
        config["scene_config"]["skin_id"] = config["skin_id"]
        config["scene_config"]["skin_play_mode"] = config["skin_play_mode"]
    if template_id == "composition_puzzle_core" and isinstance(config.get("scene_config"), dict):
        config["skin_play_mode"] = _normalize_composition_puzzle_skin_play_mode(config.get("skin_play_mode"), config["skin_id"])
        config["scene_config"]["skin_id"] = config["skin_id"]
        config["scene_config"]["skin_play_mode"] = config["skin_play_mode"]
    _attach_template_asset_manifest(config, template_id)
    config.pop("_content_manifest_explicit", None)
    config.pop("_strict_teacher_config", None)
    config.pop("_teacher_config_fields", None)
    config = apply_experience_variant(config, template_id)
    blueprint = get_template_blueprint(template_id) or {}
    if blueprint:
        config["template_blueprint"] = deepcopy(blueprint)
        if isinstance(config.get("scene_config"), dict):
            config["scene_config"]["runtime_shell"] = config.get("runtime_shell")
            config["scene_config"]["hud_model"] = config.get("hud_model")
            config["scene_config"]["game_genre"] = config.get("game_genre")
            config["scene_config"]["quality_gate_profile"] = config.get("quality_gate_profile")

    return {
        "instance_id": uuid4().hex[:12],
        "template_id": template_id,
        "template_label": template["label"],
        "scaffold_id": template["scaffold_id"],
        "version": template["version"],
        "status": "ready",
        "generation_mode": "template_config",
        "opencode_required": False,
        "template_blueprint": blueprint,
        "config": config,
        "skin": get_game_skin(config["skin_id"]) or {},
        "student_task": _student_task_for_config(template_id, config),
        "scoring": template["scoring"],
        "feedback_rules": template["feedback_rules"],
    }


def _public_template(template: dict[str, Any]) -> dict[str, Any]:
    public = _with_frontend_policy(template)
    public["default_config"] = deepcopy(template["default_config"])
    public["experience_variants"] = list_experience_variants(str(template.get("template_id") or ""))
    blueprint = get_template_blueprint(str(template.get("template_id") or ""))
    if blueprint:
        public["template_blueprint"] = blueprint
        public["default_config"]["template_blueprint"] = deepcopy(blueprint)
    return public


def _with_frontend_policy(template: dict[str, Any]) -> dict[str, Any]:
    public = deepcopy(template)
    configured_frontend = public.get("open_source_frontend", {})
    frontend = {
        **OPEN_SOURCE_FRONTEND_STACK,
        **(configured_frontend if isinstance(configured_frontend, dict) else {}),
    }
    frontend["app_framework"] = OPEN_SOURCE_FRONTEND_STACK["app_framework"]
    frontend["component_library"] = OPEN_SOURCE_FRONTEND_STACK["component_library"]
    frontend["icons"] = OPEN_SOURCE_FRONTEND_STACK["icons"]
    frontend.setdefault("state", OPEN_SOURCE_FRONTEND_STACK["state"])
    frontend["runtime_shell"] = OPEN_SOURCE_FRONTEND_STACK["runtime_shell"]
    frontend["license_policy"] = OPEN_SOURCE_FRONTEND_STACK["license_policy"]
    frontend["dependencies"] = deepcopy(OPEN_SOURCE_FRONTEND_STACK["dependencies"])
    frontend["runtime_boundary"] = OPEN_SOURCE_FRONTEND_STACK["runtime_boundary"]
    public["open_source_frontend"] = frontend
    public["frontend_policy"] = "react_component_library"
    public["forbid_standalone_web_trio"] = True
    return public


def _public_skin(skin: dict[str, Any]) -> dict[str, Any]:
    public = deepcopy(skin)
    variant = get_experience_variant(str(public.get("skin_id") or ""), str(public.get("template_id") or ""))
    if variant:
        public["play_mode"] = variant.get("play_mode", "")
        public["experience_variant_id"] = variant.get("experience_variant_id", "")
        public["scene_goal"] = variant.get("scene_goal", "")
        public["student_mission"] = variant.get("student_mission", "")
        public["interaction_feedback"] = variant.get("interaction_feedback", "")
        public["failure_feedback"] = variant.get("failure_feedback", "")
        public["reward_loop"] = variant.get("reward_loop", "")
        public["skin_family"] = variant.get("skin_family", "")
        public["layout_variant"] = variant.get("layout_variant", "")
    return public


def _allowed_overrides(payload: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "mode",
        "grade_band",
        "music_concept",
        "meter",
        "bpm",
        "round_count",
        "bars_per_round",
        "count_in_beats",
        "mission_duration_bars",
        "allow_relisten",
        "retry_limit",
        "pass_score",
        "engine",
        "scene_id",
        "skin_play_mode",
        "student_ui_mode",
        "teacher_panel_mode",
        "audio_mode",
        "strong_beat_sound",
        "weak_beat_sound",
        "beat_sound_profile",
        "lesson_audio_sync",
        "feedback_style",
        "minimal_hud",
        "game_feel",
        "game_genre",
        "game_experience",
        "first_screen_density",
        "copy_budget",
        "character_profile",
        "reward_model",
        "fail_pressure_model",
        "runtime_shell",
        "experience_variant_id",
        "experience_variant",
        "variant_game_genre",
        "variant_camera_profile",
        "variant_hud_model",
        "playfield_composition",
        "scene_goal",
        "main_object",
        "interaction_feedback",
        "failure_feedback",
        "reward_loop",
        "student_mission",
        "template_match_reason",
        "camera_profile",
        "hud_model",
        "interaction_model",
        "cartoon_role",
        "distinctiveness_tags",
        "round_length_beats",
        "round_length_steps",
        "required_accuracy",
        "energy_max",
        "energy_loss_per_miss",
        "combo_milestones",
        "judgement_windows",
        "input_map",
        "fx_profile",
        "score_model",
        "arcade_play_model",
        "target_motion_profile",
        "asset_role_map",
        "skin_objective",
        "required_combo",
        "max_mistakes",
        "reward_animation",
        "input_method",
        "timing_tolerance_ms",
        "beat_snap",
        "visual_beat_hint",
        "show_beat_track",
        "show_strong_beat_hint",
        "show_weak_beat_hint",
        "allow_practice_round",
        "subdivision_hint",
        "show_timeline_feedback",
        "show_text_feedback",
        "show_badges",
        "target_beats",
        "pattern_steps",
        "pattern_timeline",
        "allowed_difficulty",
        "tonic",
        "scale_type",
        "pitch_range",
        "route_nodes",
        "pitch_path",
        "adventure_hud",
        "show_mission_ribbon_in_play",
        "route_objective",
        "current_mode",
        "sing_back_required",
        "scene_config",
        "map_hud",
        "notes_per_round",
        "target_pattern_type",
        "target_solfege",
        "target_layout",
        "target_rounds",
        "target_hud",
        "solfege_system",
        "show_pitch_hint",
        "require_sing_back",
        "teacher_confirm_required",
        "mic_assist_enabled",
        "sound_set",
        "instrument_pool",
        "timbre_traits",
        "choices_per_round",
        "evidence_required",
        "show_wave_hint",
        "show_family_hint",
        "require_reason",
        "ai_clue_enabled",
        "ai_clue_policy",
        "clue_cases",
        "suspect_cards",
        "evidence_tokens",
        "case_progress",
        "detective_hud",
        "hf_model_id",
        "retry_limit",
        "show_staff_hint",
        "show_solfege_hint",
        "show_direction_hint",
        "skin_id",
        "form_type",
        "section_length_bars",
        "hint_mode",
        "phrase_length_bars",
        "composition_total_bars",
        "composition_segment_bars",
        "composition_segments",
        "length_clamped",
        "slots_per_bar",
        "constraint_profile",
        "rhythm_cards",
        "melody_cards",
        "required_elements",
        "composition_rounds",
        "constraint_checks",
        "composition_hud",
        "timeline_segments",
        "structure_cards",
        "answer_pattern",
        "progress_model",
        "count_in_bars",
        "combo_required",
        "mistake_limit",
        "theme",
        "lesson_specific_assets_required",
        "lesson_title",
        "lesson_asset_pack_id",
        "lesson_role_visual",
        "lesson_scene_context",
        "lesson_prop_visual",
        "lesson_material",
        "reward_style",
        "teacher_prompt",
        "age_ui_profile",
        "student_task_copy",
        "music_reason_prompts",
        "result_transfer_prompt",
        "_strict_teacher_config",
    }
    return {key: payload[key] for key in allowed if key in payload}


def _normalize_rhythm_echo_config(config: dict[str, Any]) -> dict[str, Any]:
    config["engine"] = "phaser_2d"
    config["scene_id"] = "rhythm_echo_scene"
    config["game_feel"] = "arcade_rhythm_echo"
    _apply_distinctiveness_contract(config, "rhythm_echo_core")
    config["student_ui_mode"] = "game_first"
    config["audio_mode"] = _normalize_rhythm_echo_audio_mode(config.get("audio_mode"))
    config["bpm"] = _clamp_int(config.get("bpm"), 60, 132, 92)
    config["round_count"] = _clamp_int(config.get("round_count"), 1, 12, 6)
    config["bars_per_round"] = _clamp_int(config.get("bars_per_round"), 1, 4, 1)
    config["count_in_beats"] = _clamp_int(config.get("count_in_beats"), 0, 8, 4)
    config["retry_limit"] = _clamp_int(config.get("retry_limit"), 0, 6, 3)
    config["timing_tolerance_ms"] = _clamp_int(config.get("timing_tolerance_ms"), 80, 320, 180)
    config["pass_score"] = _clamp_float(config.get("pass_score"), 0.5, 1.0, 0.8)
    config["required_accuracy"] = _clamp_float(config.get("required_accuracy") or config["pass_score"], 0.5, 1.0, 0.8)
    config["energy_max"] = _clamp_int(config.get("energy_max"), 50, 150, 100)
    config["energy_loss_per_miss"] = _clamp_int(config.get("energy_loss_per_miss"), 8, 60, 22)
    config["combo_milestones"] = _normalize_combo_milestones(config.get("combo_milestones"), 4)
    config["judgement_windows"] = _normalize_judgement_windows(config.get("judgement_windows"), config["timing_tolerance_ms"])
    config["input_map"] = _normalize_input_map(config.get("input_map"))
    config["fx_profile"] = _normalize_fx_profile(config.get("fx_profile"))
    config["score_model"] = _normalize_score_model(config.get("score_model"))
    config["lesson_audio_sync"] = _normalize_lesson_audio_sync(config.get("lesson_audio_sync"))
    if config.get("mode") not in {"echo_tap", "echo_body_percussion", "echo_chain"}:
        config["mode"] = "echo_tap"
    if config.get("input_method") not in {"tap", "keyboard", "body_percussion"}:
        config["input_method"] = "tap"
    if config.get("meter") not in {"2/4", "3/4", "4/4"}:
        config["meter"] = "2/4"
    skin_id = str(config.get("skin_id") or "rhythm_radio")
    config["skin_play_mode"] = _normalize_rhythm_echo_skin_play_mode(config.get("skin_play_mode"), skin_id)
    config["pattern_steps"] = _normalize_rhythm_pattern_steps(config.get("pattern_steps"), config.get("pattern_pool"))
    config["pattern_timeline"] = _build_rhythm_pattern_timeline(config["pattern_steps"])
    hit_count = sum(1 for item in config["pattern_timeline"] if item.get("hit_required"))
    config["round_length_steps"] = _clamp_int(config.get("round_length_steps") or hit_count, 1, 16, hit_count or 2)
    config["scene_config"] = {
        "engine": config["engine"],
        "scene_id": config["scene_id"],
        "scene_phase": "ready",
        "game_feel": config["game_feel"],
        "game_genre": config["game_genre"],
        "runtime_shell": config["runtime_shell"],
        "camera_profile": config["camera_profile"],
        "hud_model": config["hud_model"],
        "interaction_model": config["interaction_model"],
        "cartoon_role": config["cartoon_role"],
        "distinctiveness_tags": deepcopy(config["distinctiveness_tags"]),
        "skin_id": skin_id,
        "skin_play_mode": config["skin_play_mode"],
        "meter": config["meter"],
        "bpm": config["bpm"],
        "pattern_steps": deepcopy(config["pattern_steps"]),
        "pattern_timeline": deepcopy(config["pattern_timeline"]),
        "round_length_steps": config["round_length_steps"],
        "required_accuracy": config["required_accuracy"],
        "energy_max": config["energy_max"],
        "energy_loss_per_miss": config["energy_loss_per_miss"],
        "combo_milestones": deepcopy(config["combo_milestones"]),
        "judgement_windows": deepcopy(config["judgement_windows"]),
        "input_map": deepcopy(config["input_map"]),
        "fx_profile": deepcopy(config["fx_profile"]),
        "arcade_hud": True,
        "show_teacher_text_in_play": False,
        "score_model": deepcopy(config["score_model"]),
        "count_in_beats": config["count_in_beats"],
        "audio_mode": config["audio_mode"],
        "lesson_audio_sync": deepcopy(config["lesson_audio_sync"]),
        "minimal_hud": True,
    }
    return config


def _normalize_beat_guardian_config(config: dict[str, Any]) -> dict[str, Any]:
    config["engine"] = "phaser_2d"
    config["scene_id"] = "beat_guardian_scene"
    config["student_ui_mode"] = "game_first"
    config["game_feel"] = "arcade_rhythm"
    _apply_distinctiveness_contract(config, "beat_guardian_core")
    config["teacher_panel_mode"] = str(config.get("teacher_panel_mode") or "collapsed")
    if config["teacher_panel_mode"] not in {"collapsed", "end_screen"}:
        config["teacher_panel_mode"] = "collapsed"
    config["audio_mode"] = _normalize_beat_guardian_audio_mode(config.get("audio_mode"))
    config["feedback_style"] = "short_student_facing"
    config["minimal_hud"] = True
    config["bpm"] = _clamp_int(config.get("bpm"), 60, 132, 88)
    config["round_count"] = _clamp_int(config.get("round_count"), 1, 12, 5)
    config["bars_per_round"] = _clamp_int(config.get("bars_per_round"), 1, 8, 4)
    config["mission_duration_bars"] = _clamp_int(config.get("mission_duration_bars") or config.get("bars_per_round"), 1, 8, 4)
    config["count_in_bars"] = _clamp_int(config.get("count_in_bars"), 0, 2, 1)
    required_combo = _clamp_int(config.get("required_combo") or config.get("combo_required"), 1, 12, 4)
    max_mistakes = _clamp_int(config.get("max_mistakes") or config.get("mistake_limit"), 0, 8, 5)
    config["combo_required"] = required_combo
    config["required_combo"] = required_combo
    config["mistake_limit"] = max_mistakes
    config["max_mistakes"] = max_mistakes
    config["timing_tolerance_ms"] = _clamp_int(config.get("timing_tolerance_ms"), 80, 320, 170)
    config["pass_score"] = _clamp_float(config.get("pass_score"), 0.5, 1.0, 0.82)
    if config.get("mode") not in {"beat_defense", "strong_beat_guard", "meter_gate"}:
        config["mode"] = "strong_beat_guard"
    if config.get("input_method") not in {"tap", "keyboard", "body_percussion"}:
        config["input_method"] = "tap"
    if config.get("meter") not in {"2/4", "3/4", "4/4"}:
        config["meter"] = "4/4"
    beats_per_bar = int(str(config["meter"]).split("/", 1)[0])
    config["count_in_beats"] = _clamp_int(config.get("count_in_beats") or config["count_in_bars"] * beats_per_bar, 0, 8, beats_per_bar)
    config["target_beats"] = _normalize_target_beats(config.get("target_beats"), beats_per_bar)
    round_length_beats = _clamp_int(
        config.get("round_length_beats") or config["mission_duration_bars"] * beats_per_bar,
        beats_per_bar,
        beats_per_bar * 8,
        config["mission_duration_bars"] * beats_per_bar,
    )
    config["round_length_beats"] = round_length_beats
    config["mission_duration_bars"] = max(1, min(8, (round_length_beats + beats_per_bar - 1) // beats_per_bar))
    config["energy_max"] = _clamp_int(config.get("energy_max"), 50, 150, 100)
    config["energy_loss_per_miss"] = _clamp_int(config.get("energy_loss_per_miss"), 8, 60, 24)
    config["combo_milestones"] = _normalize_combo_milestones(config.get("combo_milestones"), required_combo)
    config["judgement_windows"] = _normalize_judgement_windows(config.get("judgement_windows"), config["timing_tolerance_ms"])
    config["input_map"] = _normalize_input_map(config.get("input_map"))
    config["fx_profile"] = _normalize_fx_profile(config.get("fx_profile"))
    config["score_model"] = _normalize_score_model(config.get("score_model"))
    config["show_beat_track"] = bool(config.get("show_beat_track", True))
    config["show_strong_beat_hint"] = bool(config.get("show_strong_beat_hint", True))
    config["show_weak_beat_hint"] = bool(config.get("show_weak_beat_hint", False))
    config["visual_beat_hint"] = bool(config.get("visual_beat_hint", True))
    skin_id = str(config.get("skin_id") or "castle_gate")
    config["skin_play_mode"] = _normalize_beat_guardian_skin_play_mode(config.get("skin_play_mode"), skin_id)
    config["skin_objective"] = _skin_objective_for_skin(skin_id)
    config["beat_sound_profile"] = _normalize_beat_sound_profile(config.get("beat_sound_profile"))
    config["lesson_audio_sync"] = _normalize_lesson_audio_sync(config.get("lesson_audio_sync"))
    config["scene_config"] = {
        "engine": config["engine"],
        "scene_id": config["scene_id"],
        "scene_phase": "ready",
        "game_feel": config["game_feel"],
        "game_genre": config["game_genre"],
        "runtime_shell": config["runtime_shell"],
        "camera_profile": config["camera_profile"],
        "hud_model": config["hud_model"],
        "interaction_model": config["interaction_model"],
        "cartoon_role": config["cartoon_role"],
        "distinctiveness_tags": deepcopy(config["distinctiveness_tags"]),
        "skin_id": skin_id,
        "skin_play_mode": config["skin_play_mode"],
        "meter": config["meter"],
        "beats_per_bar": beats_per_bar,
        "bpm": config["bpm"],
        "target_beats": deepcopy(config["target_beats"]),
        "round_length_beats": config["round_length_beats"],
        "required_combo": config["required_combo"],
        "max_mistakes": config["max_mistakes"],
        "energy_max": config["energy_max"],
        "energy_loss_per_miss": config["energy_loss_per_miss"],
        "combo_milestones": deepcopy(config["combo_milestones"]),
        "judgement_windows": deepcopy(config["judgement_windows"]),
        "input_map": deepcopy(config["input_map"]),
        "fx_profile": deepcopy(config["fx_profile"]),
        "arcade_hud": True,
        "show_teacher_text_in_play": False,
        "score_model": deepcopy(config["score_model"]),
        "show_beat_track": config["show_beat_track"],
        "show_strong_beat_hint": config["show_strong_beat_hint"],
        "show_weak_beat_hint": config["show_weak_beat_hint"],
        "visual_beat_hint": config["visual_beat_hint"],
        "mission_duration_bars": config["mission_duration_bars"],
        "count_in_beats": config["count_in_beats"],
        "timing_tolerance_ms": config["timing_tolerance_ms"],
        "audio_mode": config["audio_mode"],
        "strong_beat_sound": config.get("strong_beat_sound") or "low_drum",
        "weak_beat_sound": config.get("weak_beat_sound") or "wood_tick",
        "beat_sound_profile": deepcopy(config["beat_sound_profile"]),
        "lesson_audio_sync": deepcopy(config["lesson_audio_sync"]),
        "minimal_hud": True,
        "skin_objective": config["skin_objective"],
        "reward_animation": config.get("reward_animation") or _reward_animation_for_skin(skin_id),
    }
    return config


def _normalize_beat_guardian_audio_mode(value: Any) -> str:
    mode = str(value or "hybrid").strip()
    if mode in {"internal_meter", "lesson_audio", "hybrid"}:
        return mode
    return "hybrid"


def _apply_distinctiveness_contract(config: dict[str, Any], template_id: str) -> None:
    apply_template_blueprint_contract(config, template_id)


def _normalize_rhythm_echo_audio_mode(value: Any) -> str:
    mode = str(value or "hybrid").strip()
    if mode in {"internal_pattern", "lesson_audio", "hybrid"}:
        return mode
    return "hybrid"


def _normalize_pitch_ladder_audio_mode(value: Any) -> str:
    mode = str(value or "hybrid").strip()
    if mode in {"internal_pitch", "lesson_audio", "hybrid"}:
        return mode
    return "hybrid"


def _normalize_solfege_target_audio_mode(value: Any) -> str:
    mode = str(value or "hybrid").strip()
    if mode in {"internal_pitch", "lesson_audio", "hybrid"}:
        return mode
    return "hybrid"


def _normalize_timbre_detective_audio_mode(value: Any) -> str:
    mode = str(value or "hybrid").strip()
    if mode in {"internal_timbre", "lesson_audio", "hybrid"}:
        return mode
    return "hybrid"


def _normalize_form_treasure_audio_mode(value: Any) -> str:
    mode = str(value or "internal_form").strip()
    if mode in {"internal_form", "lesson_audio", "hybrid"}:
        return mode
    return "internal_form"


def _normalize_composition_audio_mode(value: Any) -> str:
    mode = str(value or "internal_composition").strip()
    if mode in {"internal_composition", "lesson_audio", "hybrid"}:
        return mode
    return "internal_composition"


def _normalize_composition_mode(value: Any) -> str:
    mode = str(value or "").strip()
    if mode in {"rhythm_puzzle_composition", "melody_puzzle_creation", "melody_rhythm_puzzle"}:
        return mode
    if mode in {"节奏拼图创编", "rhythm"}:
        return "rhythm_puzzle_composition"
    if mode in {"旋律拼图创作", "melody"}:
        return "melody_puzzle_creation"
    if mode in {"旋律节奏拼图", "mixed"}:
        return "melody_rhythm_puzzle"
    return "rhythm_puzzle_composition"


def _normalize_constraint_profile(value: Any) -> str:
    profile = str(value or "").strip()
    if profile in {"guided", "balanced", "challenge"}:
        return profile
    return "guided"


def _normalize_composition_rhythm_cards(value: Any) -> list[dict[str, Any]]:
    source = value if isinstance(value, list) else COMPOSITION_PUZZLE_DEFAULT_CONFIG["rhythm_cards"]
    cards: list[dict[str, Any]] = []
    for item in source:
        if not isinstance(item, dict):
            continue
        card_id = str(item.get("id") or "").strip()
        label = str(item.get("label") or card_id).strip()
        if not card_id or not label:
            continue
        cards.append(
            {
                "id": card_id,
                "label": label,
                "beats": _clamp_float(item.get("beats"), 0.5, 4.0, 1.0),
                "kind": str(item.get("kind") or "hit"),
                "difficulty": _clamp_int(item.get("difficulty"), 1, 5, 1),
            }
        )
    return cards[:8] if len(cards) >= 2 else deepcopy(COMPOSITION_PUZZLE_DEFAULT_CONFIG["rhythm_cards"])


def _normalize_composition_melody_cards(value: Any) -> list[str]:
    source = value if isinstance(value, list) else COMPOSITION_PUZZLE_DEFAULT_CONFIG["melody_cards"]
    ordered = [pitch for pitch in PITCH_ORDER if pitch in {str(item) for item in source}]
    return ordered if len(ordered) >= 2 else deepcopy(COMPOSITION_PUZZLE_DEFAULT_CONFIG["melody_cards"])


def _composition_required_elements(config: dict[str, Any]) -> list[str]:
    explicit = _normalize_composition_required_elements(config.get("required_elements"))
    if explicit:
        return explicit
    mode = str(config.get("mode") or "")
    profile = str(config.get("constraint_profile") or "guided")
    checks = ["填满小节", "试听后提交"]
    if mode in {"rhythm_puzzle_composition", "melody_rhythm_puzzle"}:
        checks.append("至少使用 2 种节奏材料")
    if mode in {"melody_puzzle_creation", "melody_rhythm_puzzle"}:
        checks.append("至少出现 3 个音高")
        checks.append("结束音回到 do 或 la")
    if profile == "challenge":
        checks.append("说明创编理由")
    return checks


def _normalize_composition_required_elements(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    normalized: list[str] = []
    for item in value:
        label = str(item or "").strip()
        if label and label not in normalized:
            normalized.append(label)
    return normalized[:8]


def _build_composition_rounds(config: dict[str, Any]) -> list[dict[str, Any]]:
    total_slots = int(config["composition_total_bars"]) * int(config["slots_per_bar"])
    segment_slots = int(config["composition_segment_bars"]) * int(config["slots_per_bar"])
    rhythm_cards = config["rhythm_cards"]
    melody_cards = config["melody_cards"]
    rounds = []
    for index in range(int(config["composition_segments"])):
        rhythm = rhythm_cards[index % len(rhythm_cards)]
        melody = melody_cards[index % len(melody_cards)]
        start_bar = index * int(config["composition_segment_bars"]) + 1
        end_bar = min(int(config["composition_total_bars"]), start_bar + int(config["composition_segment_bars"]) - 1)
        rounds.append(
            {
                "id": f"composition-segment-{index + 1}",
                "label": f"第 {index + 1} 段",
                "prompt": _composition_prompt_for_mode(config["mode"]),
                "target_slots": total_slots,
                "segment_slots": segment_slots,
                "start_bar": start_bar,
                "end_bar": end_bar,
                "bars": max(1, end_bar - start_bar + 1),
                "starter_rhythm": rhythm["id"],
                "starter_pitch": melody,
                "stars": min(index + 1, 3),
            }
        )
    return rounds


def _build_composition_constraint_checks(config: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        _composition_constraint_check(label, index)
        for index, label in enumerate(config["required_elements"])
    ]


def _composition_constraint_check(label: str, index: int) -> dict[str, Any]:
    check = {"id": f"check-{index + 1}", "label": label, "required": True, "status": "pending"}
    if label in PITCH_ORDER:
        check.update({"id": f"pitch_token_{label}", "kind": "pitch_token", "target": label, "label": f"必须使用 {PITCH_LABELS.get(label, label)}"})
    return check


def _composition_prompt_for_mode(mode: str) -> str:
    if mode == "melody_puzzle_creation":
        return "用唱名卡拼出有起伏的旋律短句。"
    if mode == "melody_rhythm_puzzle":
        return "把音高和节奏组合成完整音乐短句。"
    return "用节奏卡拼出完整小节，再试听修正。"


def _normalize_combo_milestones(value: Any, required_combo: int) -> list[int]:
    if not isinstance(value, list):
        value = [4, 8, 12]
    milestones: list[int] = []
    for item in value:
        combo = _clamp_int(item, 1, 24, 4)
        if combo not in milestones:
            milestones.append(combo)
    if required_combo not in milestones:
        milestones.append(required_combo)
    return sorted(milestones)


def _normalize_judgement_windows(value: Any, fallback_tolerance: int) -> dict[str, int]:
    raw = value if isinstance(value, dict) else {}
    perfect = max(95, _clamp_int(raw.get("perfect_ms"), 35, 140, 95))
    good = max(210, _clamp_int(raw.get("good_ms"), perfect, 260, min(max(fallback_tolerance, 160), 220)))
    late = max(320, _clamp_int(raw.get("late_ms"), good, 420, max(fallback_tolerance, 320)))
    return {"perfect_ms": perfect, "good_ms": good, "late_ms": late}


def _normalize_input_map(value: Any) -> dict[str, Any]:
    raw = value if isinstance(value, dict) else {}
    primary = str(raw.get("primary") or "Space").strip() or "Space"
    return {"primary": primary, "pointer": bool(raw.get("pointer", True))}


def _normalize_fx_profile(value: Any) -> dict[str, str]:
    raw = value if isinstance(value, dict) else {}
    return {
        "hit": str(raw.get("hit") or "burst"),
        "miss": str(raw.get("miss") or "shake"),
        "success": str(raw.get("success") or "skin_objective_finish"),
    }


def _normalize_copy_budget(value: Any) -> dict[str, int]:
    raw = value if isinstance(value, dict) else {}
    return {
        "objective_max_chars": _clamp_int(raw.get("objective_max_chars"), 8, 36, 18),
        "feedback_max_chars": _clamp_int(raw.get("feedback_max_chars"), 4, 16, 8),
    }


def _normalize_pitch_character_profile(value: Any) -> dict[str, str]:
    raw = value if isinstance(value, dict) else {}
    return {
        "role": str(raw.get("role") or "旋律探险家"),
        "idle_animation": str(raw.get("idle_animation") or "bounce_ready"),
        "success_animation": str(raw.get("success_animation") or "flag_cheer"),
        "fail_animation": str(raw.get("fail_animation") or "slide_back"),
    }


def _normalize_pitch_reward_model(value: Any, tokens_required: int) -> dict[str, Any]:
    raw = value if isinstance(value, dict) else {}
    return {
        "token_name": str(raw.get("token_name") or "旋律宝石"),
        "tokens_required": _clamp_int(raw.get("tokens_required"), 1, 12, tokens_required),
        "final_reward_animation": str(raw.get("final_reward_animation") or "summit_flag"),
    }


def _normalize_pitch_fail_pressure_model(value: Any) -> dict[str, Any]:
    raw = value if isinstance(value, dict) else {}
    return {
        "energy_loss_animation": str(raw.get("energy_loss_animation") or "heart_drop"),
        "route_damage_animation": str(raw.get("route_damage_animation") or "crack_flash"),
        "quick_retry": bool(raw.get("quick_retry", True)),
    }


def _normalize_pitch_music_elements(config: dict[str, Any]) -> dict[str, Any]:
    raw = config.get("music_elements") if isinstance(config.get("music_elements"), dict) else {}
    solfege_hint = config["show_solfege_hint"] if "show_solfege_hint" in config else raw.get("show_solfege_hint", True)
    sing_back_required = config["sing_back_required"] if "sing_back_required" in config else raw.get("sing_back_required", True)
    return {
        "tonic": str(config.get("tonic") or raw.get("tonic") or "C"),
        "scale_type": str(config.get("scale_type") or raw.get("scale_type") or "major_pentatonic"),
        "pitch_range": deepcopy(config.get("pitch_range") or PITCH_LADDER_DEFAULT_CONFIG["pitch_range"]),
        "notes_per_round": int(config.get("notes_per_round") or PITCH_LADDER_DEFAULT_CONFIG["notes_per_round"]),
        "round_count": int(config.get("round_count") or PITCH_LADDER_DEFAULT_CONFIG["round_count"]),
        "direction_mix": _normalize_ratio_mix(raw.get("direction_mix"), {"higher": 0.4, "same": 0.2, "lower": 0.4}),
        "step_skip_mix": _normalize_ratio_mix(raw.get("step_skip_mix"), {"step": 0.75, "skip": 0.25}),
        "show_solfege_hint": bool(solfege_hint),
        "audio_mode": str(config.get("audio_mode") or raw.get("audio_mode") or "hybrid"),
        "sing_back_required": bool(sing_back_required),
    }


def _normalize_ratio_mix(value: Any, fallback: dict[str, float]) -> dict[str, float]:
    raw = value if isinstance(value, dict) else {}
    normalized: dict[str, float] = {}
    for key, default in fallback.items():
        normalized[key] = _clamp_float(raw.get(key), 0.0, 1.0, default)
    total = sum(normalized.values())
    if total <= 0:
        return deepcopy(fallback)
    return {key: round(weight / total, 3) for key, weight in normalized.items()}


def _normalize_solfege_fx_profile(value: Any) -> dict[str, str]:
    raw = value if isinstance(value, dict) else {}
    return {
        "hit": str(raw.get("hit") or "target_burst"),
        "miss": str(raw.get("miss") or "reticle_shake"),
        "success": str(raw.get("success") or "skin_target_finish"),
    }


def _normalize_score_model(value: Any) -> dict[str, int]:
    raw = value if isinstance(value, dict) else {}
    return {
        "perfect": _clamp_int(raw.get("perfect"), 20, 500, 120),
        "good": _clamp_int(raw.get("good"), 10, 300, 80),
        "wrong": -abs(_clamp_int(raw.get("wrong"), -200, 200, -40)),
        "missed": -abs(_clamp_int(raw.get("missed"), -240, 240, -60)),
    }


def _normalize_solfege_target_motion_profile(value: Any) -> dict[str, float]:
    raw = value if isinstance(value, dict) else {}
    return {
        "float_amplitude": _clamp_float(raw.get("float_amplitude"), 0, 10, 8),
        "float_speed": _clamp_float(raw.get("float_speed"), 0.2, 2.4, 0.85),
        "orbit_jitter": _clamp_float(raw.get("orbit_jitter"), 0, 0.017, 0.012),
    }


def _normalize_solfege_asset_role_map(value: Any) -> dict[str, str]:
    default = deepcopy(SOLFEGE_TARGET_DEFAULT_CONFIG["asset_role_map"])
    if not isinstance(value, dict):
        return default
    for key in default:
        text = str(value.get(key) or "").strip()
        if text:
            default[key] = text
    return default


def _normalize_beat_sound_profile(value: Any) -> dict[str, dict[str, Any]]:
    default = deepcopy(BEAT_GUARDIAN_DEFAULT_CONFIG["beat_sound_profile"])
    if not isinstance(value, dict):
        return default
    for key in ("strong", "weak"):
        candidate = value.get(key)
        if not isinstance(candidate, dict):
            continue
        merged = {**default[key], **candidate}
        merged["frequency"] = _clamp_int(merged.get("frequency"), 80, 1200, default[key]["frequency"])
        merged["duration_ms"] = _clamp_int(merged.get("duration_ms"), 35, 260, default[key]["duration_ms"])
        merged["gain"] = _clamp_float(merged.get("gain"), 0.03, 0.5, default[key]["gain"])
        if merged.get("wave") not in {"sine", "square", "sawtooth", "triangle"}:
            merged["wave"] = default[key]["wave"]
        default[key] = merged
    return default


def _normalize_lesson_audio_sync(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}
    audio_url = str(value.get("audio_url") or value.get("source_audio_url") or value.get("audio_clip_url") or "").strip()
    if not audio_url:
        return {}
    return {
        "audio_url": audio_url,
        "bpm": _clamp_int(value.get("bpm"), 40, 180, 88),
        "meter": str(value.get("meter") or "4/4") if str(value.get("meter") or "4/4") in {"2/4", "3/4", "4/4"} else "4/4",
        "offset_ms": _clamp_int(value.get("offset_ms"), 0, 10000, 0),
        "segment_label": str(value.get("segment_label") or value.get("selected_phrase_label") or "作品片段"),
    }


def _normalize_beat_guardian_skin_play_mode(value: Any, skin_id: str) -> str:
    if skin_id in BEAT_GUARDIAN_SKIN_PLAY_MODES:
        return BEAT_GUARDIAN_SKIN_PLAY_MODES[skin_id]
    mode = str(value or "").strip()
    if mode in {"race", "gate", "station", "spotlight", "orbit"}:
        return mode
    return "gate"


def _reward_animation_for_skin(skin_id: str) -> str:
    return {
        "dragon_boat": "finish_surge",
        "castle_gate": "gate_open",
        "train_conductor": "platform_arrival",
        "stage_light": "main_spotlight",
        "space_orbit": "orbit_lock",
    }.get(skin_id, "badge_spark")


def _skin_objective_for_skin(skin_id: str) -> str:
    return {
        "dragon_boat": "跟鼓点预判强拍",
        "castle_gate": "维持护盾",
        "train_conductor": "准点充能",
        "stage_light": "强拍点亮",
        "space_orbit": "轨道同步",
    }.get(skin_id, "维持护盾")


def _normalize_target_beats(value: Any, beats_per_bar: int) -> list[int]:
    if beats_per_bar >= 1:
        return [1]
    if not isinstance(value, list):
        value = [1]
    beats: list[int] = []
    for item in value:
        try:
            beat = int(item)
        except (TypeError, ValueError):
            continue
        if 1 <= beat <= beats_per_bar and beat not in beats:
            beats.append(beat)
    return beats or [1]


def _normalize_rhythm_echo_skin_play_mode(value: Any, skin_id: str) -> str:
    if skin_id in RHYTHM_ECHO_SKIN_PLAY_MODES:
        return RHYTHM_ECHO_SKIN_PLAY_MODES[skin_id]
    mode = str(value or "").strip()
    if mode == "drum":
        return "radio"
    if mode in {"radio", "cave", "signal", "rain", "kitchen"}:
        return mode
    return "radio"


def _normalize_pitch_ladder_skin_play_mode(value: Any, skin_id: str) -> str:
    if skin_id in PITCH_LADDER_SKIN_PLAY_MODES:
        return PITCH_LADDER_SKIN_PLAY_MODES[skin_id]
    mode = str(value or "").strip()
    if mode in {"mountain", "cloud", "bamboo", "lantern"}:
        return mode
    return "mountain"


def _pitch_ladder_content_manifest_for_skin(skin_play_mode: str) -> dict[str, Any]:
    manifest = deepcopy(PITCH_LADDER_DEFAULT_CONFIG["content_manifest"])
    art = PITCH_LADDER_SKIN_ART.get(skin_play_mode)
    if art:
        manifest["art"] = deepcopy(art)
        hero_sprite = PITCH_LADDER_HERO_SPRITES.get(skin_play_mode)
        if hero_sprite:
            manifest["heroSprite"] = {
                **deepcopy(hero_sprite),
                "frameWidth": 192,
                "frameHeight": 224,
                "anchor": {"x": 0.5, "y": 1},
                "animations": deepcopy(PITCH_LADDER_HERO_SPRITE_ANIMATIONS),
            }
        if skin_play_mode == "cloud":
            manifest["environment"] = {
                "backgroundLayers": ["sky_gradient", "cloud_lane", "floating_islands"],
                "platformKey": "cloud_platform",
                "goalKey": "cloud_gate",
            }
        elif skin_play_mode == "bamboo":
            manifest["environment"] = {
                "backgroundLayers": ["bamboo_forest", "waterfall", "leaf_platforms"],
                "platformKey": "bamboo_platform",
                "goalKey": "bamboo_crown",
            }
    return manifest


def _normalize_solfege_target_skin_play_mode(value: Any, skin_id: str) -> str:
    if skin_id in SOLFEGE_TARGET_SKIN_PLAY_MODES:
        return SOLFEGE_TARGET_SKIN_PLAY_MODES[skin_id]
    mode = str(value or "").strip()
    if mode in {"star", "flower", "lantern", "archery", "bubble"}:
        return mode
    return "star"


def _normalize_timbre_detective_skin_play_mode(value: Any, skin_id: str) -> str:
    if skin_id in TIMBRE_DETECTIVE_SKIN_PLAY_MODES:
        return TIMBRE_DETECTIVE_SKIN_PLAY_MODES[skin_id]
    mode = str(value or "").strip()
    if mode in {"casebook", "museum", "forest", "studio", "theater"}:
        return mode
    return "casebook"


def _normalize_form_treasure_skin_play_mode(value: Any, skin_id: str) -> str:
    if skin_id in FORM_TREASURE_SKIN_PLAY_MODES:
        return FORM_TREASURE_SKIN_PLAY_MODES[skin_id]
    mode = str(value or "").strip()
    if mode in {"map", "constellation", "gallery", "train", "stage"}:
        return mode
    return "map"


def _normalize_composition_puzzle_skin_play_mode(value: Any, skin_id: str) -> str:
    if skin_id in COMPOSITION_PUZZLE_SKIN_PLAY_MODES:
        return COMPOSITION_PUZZLE_SKIN_PLAY_MODES[skin_id]
    mode = str(value or "").strip()
    if mode in {"studio", "rhythm_table", "melody_garden"}:
        return mode
    return "studio"


def _normalize_rhythm_pattern_steps(value: Any, pattern_pool: Any) -> list[str]:
    allowed = {"quarter", "eighth_pair", "eighth", "half", "rest", "syncopation", "dotted_quarter"}
    if isinstance(value, list):
        steps = [str(item) for item in value if str(item) in allowed]
        if steps:
            return steps[:12]
    if isinstance(pattern_pool, list) and pattern_pool:
        first = pattern_pool[0]
        if isinstance(first, dict) and isinstance(first.get("steps"), list):
            steps = [str(item) for item in first["steps"] if str(item) in allowed]
            if steps:
                return steps[:12]
    return ["quarter", "quarter"]


def _build_rhythm_pattern_timeline(steps: list[str]) -> list[dict[str, Any]]:
    timeline: list[dict[str, Any]] = []
    current = 0.0
    for step in steps:
        for atomic in _expand_rhythm_step(step):
            duration = float(atomic["duration_beats"])
            timeline.append(
                {
                    "step": atomic["step"],
                    "label": atomic["label"],
                    "time_beats": round(current, 3),
                    "duration_beats": duration,
                    "hit_required": bool(atomic["hit_required"]),
                }
            )
            current += duration
    return timeline


def _expand_rhythm_step(step: str) -> list[dict[str, Any]]:
    if step == "eighth_pair":
        return [
            {"step": "eighth", "label": "八分", "duration_beats": 0.5, "hit_required": True},
            {"step": "eighth", "label": "八分", "duration_beats": 0.5, "hit_required": True},
        ]
    if step == "half":
        return [{"step": "half", "label": "二分", "duration_beats": 2.0, "hit_required": True}]
    if step == "dotted_quarter":
        return [{"step": "dotted_quarter", "label": "附点四分", "duration_beats": 1.5, "hit_required": True}]
    if step == "rest":
        return [{"step": "rest", "label": "休止", "duration_beats": 1.0, "hit_required": False}]
    if step == "syncopation":
        return [
            {"step": "sixteenth", "label": "切分前十六", "duration_beats": 0.25, "hit_required": True},
            {"step": "eighth", "label": "切分中八分", "duration_beats": 0.5, "hit_required": True},
            {"step": "sixteenth", "label": "切分后十六", "duration_beats": 0.25, "hit_required": True},
        ]
    if step == "eighth":
        return [{"step": "eighth", "label": "八分", "duration_beats": 0.5, "hit_required": True}]
    return [{"step": "quarter", "label": "四", "duration_beats": 1.0, "hit_required": True}]


PITCH_ORDER = [str(pitch["id"]) for pitch in PITCH_DEFINITIONS]
PITCH_LADDER_ALLOWED_MODES = {"high_low_steps", "solfege_ladder", "melody_climb"}
PITCH_LADDER_ALLOWED_SCALE_TYPES = {"major_pentatonic", "major", "minor_pentatonic"}
PITCH_LADDER_ALLOWED_SKINS = {"mountain_steps", "cloud_elevator", "bamboo_ladder", "lantern_tower"}
PITCH_LABELS = {
    str(pitch["id"]): str((pitch["solfegeAliases"] or [" / ".join(pitch["numberLabels"])])[0])
    for pitch in PITCH_DEFINITIONS
}
PITCH_SEMITONES = {str(pitch["id"]): int(pitch["semitone"]) for pitch in PITCH_DEFINITIONS}


def _strict_pitch_ladder_teacher_config_fields(config: dict[str, Any]) -> set[str]:
    if not config.get("_strict_teacher_config"):
        return set()
    fields = config.get("_teacher_config_fields")
    return {str(field) for field in fields} if isinstance(fields, set) else set()


def _require_pitch_ladder_teacher_config(
    condition: bool,
    field: str,
    message: str,
) -> None:
    if not condition:
        raise ValueError(f"音高游戏配置无效：{field} {message}")


def _strict_int_value(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value)
    return None


def _strict_float_value(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _validate_pitch_ladder_teacher_config(config: dict[str, Any]) -> None:
    fields = _strict_pitch_ladder_teacher_config_fields(config)
    if not fields:
        return
    if "mode" in fields:
        _require_pitch_ladder_teacher_config(
            config.get("mode") in PITCH_LADDER_ALLOWED_MODES,
            "mode",
            "必须是 high_low_steps、solfege_ladder 或 melody_climb。",
        )
    if "skin_id" in fields:
        _require_pitch_ladder_teacher_config(
            config.get("skin_id") in PITCH_LADDER_ALLOWED_SKINS,
            "skin_id",
            "必须是 mountain_steps、cloud_elevator、bamboo_ladder 或 lantern_tower。",
        )
    if "scale_type" in fields:
        _require_pitch_ladder_teacher_config(
            config.get("scale_type") in PITCH_LADDER_ALLOWED_SCALE_TYPES,
            "scale_type",
            "必须是 major_pentatonic、major 或 minor_pentatonic。",
        )
    if "pitch_range" in fields:
        value = config.get("pitch_range")
        valid_notes = [str(item) for item in value] if isinstance(value, list) else []
        unique_notes = []
        for note in valid_notes:
            resolved = resolve_pitch_token(note)
            if resolved and resolved["id"] not in unique_notes:
                unique_notes.append(resolved["id"])
        _require_pitch_ladder_teacher_config(isinstance(value, list), "pitch_range", "必须是音名列表。")
        _require_pitch_ladder_teacher_config(
            len(unique_notes) == len({str(item) for item in valid_notes}) and len(unique_notes) >= 2,
            "pitch_range",
            "至少包含 2 个有效唱名或简谱音级。",
        )
    if "round_count" in fields:
        round_count = _strict_int_value(config.get("round_count"))
        _require_pitch_ladder_teacher_config(round_count is not None and 1 <= round_count <= 12, "round_count", "必须在 1 到 12 之间。")
    if "notes_per_round" in fields:
        notes_per_round = _strict_int_value(config.get("notes_per_round"))
        _require_pitch_ladder_teacher_config(notes_per_round is not None and 1 <= notes_per_round <= 5, "notes_per_round", "必须在 1 到 5 之间。")
        mode = str(config.get("mode") or PITCH_LADDER_DEFAULT_CONFIG["mode"])
        if mode == "high_low_steps":
            _require_pitch_ladder_teacher_config(notes_per_round == 2, "notes_per_round", "在 high_low_steps 模式下必须等于 2。")
        elif mode == "solfege_ladder":
            _require_pitch_ladder_teacher_config(notes_per_round == 1, "notes_per_round", "在 solfege_ladder 模式下必须等于 1。")
        elif mode == "melody_climb":
            _require_pitch_ladder_teacher_config(3 <= notes_per_round <= 5, "notes_per_round", "在 melody_climb 模式下必须在 3 到 5 之间。")
    if "retry_limit" in fields:
        retry_limit = _strict_int_value(config.get("retry_limit"))
        _require_pitch_ladder_teacher_config(retry_limit is not None and 0 <= retry_limit <= 6, "retry_limit", "必须在 0 到 6 之间。")
    if "pass_score" in fields:
        pass_score = _strict_float_value(config.get("pass_score"))
        _require_pitch_ladder_teacher_config(pass_score is not None and 0.5 <= pass_score <= 1.0, "pass_score", "必须在 0.5 到 1.0 之间。")
    if "mistake_limit" in fields:
        mistake_limit = _strict_int_value(config.get("mistake_limit"))
        _require_pitch_ladder_teacher_config(mistake_limit is not None and 1 <= mistake_limit <= 10, "mistake_limit", "必须在 1 到 10 之间。")


def _normalize_pitch_ladder_config(config: dict[str, Any]) -> dict[str, Any]:
    _validate_pitch_ladder_teacher_config(config)
    config["engine"] = "phaser_2d"
    config["scene_id"] = "pitch_ladder_scene"
    config["game_feel"] = "map_pitch_climb"
    _apply_distinctiveness_contract(config, "pitch_ladder_core")
    config["student_ui_mode"] = "game_first"
    config["game_experience"] = "adventure_climb"
    config["first_screen_density"] = "playfield_only"
    config["copy_budget"] = _normalize_copy_budget(config.get("copy_budget"))
    config["audio_mode"] = _normalize_pitch_ladder_audio_mode(config.get("audio_mode"))
    config["round_count"] = _clamp_int(config.get("round_count"), 1, 12, 6)
    config["notes_per_round"] = _clamp_int(config.get("notes_per_round"), 1, 5, 2)
    config["retry_limit"] = _clamp_int(config.get("retry_limit"), 0, 6, 3)
    config["pass_score"] = _clamp_float(config.get("pass_score"), 0.5, 1.0, 0.8)
    config["energy_max"] = _clamp_int(config.get("energy_max"), 50, 150, 100)
    config["mistake_limit"] = _clamp_int(config.get("mistake_limit"), 1, 10, 3)
    config["character_profile"] = _normalize_pitch_character_profile(config.get("character_profile"))
    config["reward_model"] = _normalize_pitch_reward_model(config.get("reward_model"), config["round_count"])
    config["fail_pressure_model"] = _normalize_pitch_fail_pressure_model(config.get("fail_pressure_model"))
    config["sing_back_required"] = bool(config.get("sing_back_required", True))
    config["input_map"] = _normalize_input_map(config.get("input_map"))
    config["input_bindings"] = deepcopy(config.get("input_bindings") or PITCH_LADDER_DEFAULT_CONFIG["input_bindings"])
    config["fx_profile"] = _normalize_fx_profile(config.get("fx_profile"))
    custom_content_manifest = deepcopy(config["content_manifest"]) if config.get("_content_manifest_explicit") and isinstance(config.get("content_manifest"), dict) else None
    config["quality_gate_profile"] = deepcopy(config.get("quality_gate_profile") or PITCH_LADDER_DEFAULT_CONFIG["quality_gate_profile"])
    config["voice_control_mode"] = str(config.get("voice_control_mode") or "listen_then_sing")
    config["route_style"] = str(config.get("route_style") or "map_native")
    config["movement_profile"] = str(config.get("movement_profile") or "walk_arc")
    config["hint_density"] = str(config.get("hint_density") or "low")
    if config.get("mode") not in PITCH_LADDER_ALLOWED_MODES:
        config["mode"] = "high_low_steps"
    if config.get("scale_type") not in PITCH_LADDER_ALLOWED_SCALE_TYPES:
        config["scale_type"] = "major_pentatonic"
    if config.get("skin_id") not in PITCH_LADDER_ALLOWED_SKINS:
        config["skin_id"] = "mountain_steps"
    config["pitch_range"] = _normalize_pitch_range(config.get("pitch_range"))
    if config["mode"] == "high_low_steps":
        config["notes_per_round"] = 2
        config["target_pattern_type"] = "direction_pair"
        config["current_mode"] = "direction_pair"
    elif config["mode"] == "solfege_ladder":
        config["notes_per_round"] = 1
        config["target_pattern_type"] = "single_solfege"
        config["current_mode"] = "single_solfege"
    else:
        config["notes_per_round"] = max(3, config["notes_per_round"])
        config["target_pattern_type"] = "melody_path"
        config["current_mode"] = "melody_path"
    config["pitch_rounds"] = _build_pitch_rounds(config)
    config["skin_play_mode"] = _normalize_pitch_ladder_skin_play_mode(config.get("skin_play_mode"), config["skin_id"])
    config["content_manifest"] = custom_content_manifest or _pitch_ladder_content_manifest_for_skin(config["skin_play_mode"])
    config["route_objective"] = PITCH_LADDER_ROUTE_OBJECTIVES.get(config["skin_play_mode"], "summit")
    skin_labels = PITCH_LADDER_SKIN_LABELS.get(config["skin_play_mode"], PITCH_LADDER_SKIN_LABELS["mountain"])
    config["theme"] = skin_labels["theme"]
    config["reward_style"] = skin_labels["reward_style"]
    config["reward_model"]["token_name"] = skin_labels["token_name"]
    config["route_nodes"] = _build_pitch_route_nodes(config["pitch_range"])
    config["pitch_path"] = _build_pitch_path(config["pitch_rounds"], config["route_nodes"])
    config["music_elements"] = _normalize_pitch_music_elements(config)
    config["scene_config"] = {
        "engine": "phaser_2d",
        "scene_id": "pitch_ladder_scene",
        "runtime_shell": config["runtime_shell"],
        "hud_model": config["hud_model"],
        "game_genre": config["game_genre"],
        "quality_gate_profile": config.get("quality_gate_profile"),
        "game_feel": config["game_feel"],
        "student_ui_mode": "game_first",
        "game_experience": "adventure_climb",
        "first_screen_density": "playfield_only",
        "copy_budget": deepcopy(config["copy_budget"]),
        "skin_id": config["skin_id"],
        "skin_play_mode": config["skin_play_mode"],
        "route_objective": config["route_objective"],
        "character_profile": deepcopy(config["character_profile"]),
        "reward_model": deepcopy(config["reward_model"]),
        "fail_pressure_model": deepcopy(config["fail_pressure_model"]),
        "mode": config["mode"],
        "current_mode": config["current_mode"],
        "target_pattern_type": config["target_pattern_type"],
        "round_count": config["round_count"],
        "notes_per_round": config["notes_per_round"],
        "pitch_range": deepcopy(config["pitch_range"]),
        "music_elements": deepcopy(config["music_elements"]),
        "pitch_rounds": deepcopy(config["pitch_rounds"]),
        "route_nodes": deepcopy(config["route_nodes"]),
        "pitch_path": deepcopy(config["pitch_path"]),
        "energy_max": config["energy_max"],
        "mistake_limit": config["mistake_limit"],
        "retry_limit": config["retry_limit"],
        "pass_score": config["pass_score"],
        "allow_relisten": config["allow_relisten"],
        "show_staff_hint": config["show_staff_hint"],
        "show_solfege_hint": config["show_solfege_hint"],
        "show_direction_hint": config["show_direction_hint"],
        "sing_back_required": config["sing_back_required"],
        "teacher_prompt": config["teacher_prompt"],
        "tonic": config["tonic"],
        "scale_type": config["scale_type"],
        "audio_mode": config["audio_mode"],
        "audio_assets": deepcopy(config.get("audio_assets") or {}),
        "input_map": deepcopy(config["input_map"]),
        "input_bindings": deepcopy(config["input_bindings"]),
        "fx_profile": deepcopy(config["fx_profile"]),
        "content_manifest": deepcopy(config["content_manifest"]),
        "quality_gate_profile": deepcopy(config["quality_gate_profile"]),
        "voice_control_mode": config["voice_control_mode"],
        "route_style": config["route_style"],
        "movement_profile": config["movement_profile"],
        "hint_density": config["hint_density"],
        "show_teacher_text_in_play": False,
        "map_hud": True,
        "adventure_hud": True,
        "show_mission_ribbon_in_play": False,
    }
    return config


def _normalize_solfege_target_config(config: dict[str, Any]) -> dict[str, Any]:
    config["engine"] = "phaser_2d"
    config["scene_id"] = "solfege_target_scene"
    config["game_feel"] = "solfege_target_range"
    _apply_distinctiveness_contract(config, "solfege_target_core")
    config["student_ui_mode"] = "game_first"
    config["audio_mode"] = _normalize_solfege_target_audio_mode(config.get("audio_mode"))
    config["round_count"] = _clamp_int(config.get("round_count"), 1, 12, 6)
    config["notes_per_round"] = _clamp_int(config.get("notes_per_round"), 1, 4, 1)
    config["retry_limit"] = _clamp_int(config.get("retry_limit"), 0, 6, 3)
    config["pass_score"] = _clamp_float(config.get("pass_score"), 0.5, 1.0, 0.8)
    config["energy_max"] = _clamp_int(config.get("energy_max"), 50, 150, 100)
    config["mistake_limit"] = _clamp_int(config.get("mistake_limit"), 1, 10, 3)
    config["combo_milestones"] = _normalize_combo_milestones(config.get("combo_milestones"), 4)
    config["input_map"] = _normalize_input_map(config.get("input_map"))
    config["fx_profile"] = _normalize_solfege_fx_profile(config.get("fx_profile"))
    config["score_model"] = _normalize_score_model(config.get("score_model"))
    config["arcade_play_model"] = "bubble_target_chain"
    config["target_motion_profile"] = _normalize_solfege_target_motion_profile(config.get("target_motion_profile"))
    config["asset_role_map"] = _normalize_solfege_asset_role_map(config.get("asset_role_map"))
    config["mic_assist_enabled"] = bool(config.get("mic_assist_enabled", True))
    config["sing_back_required"] = bool(config.get("sing_back_required", config.get("require_sing_back", True)))
    config["teacher_confirm_required"] = bool(config.get("teacher_confirm_required", True))
    config["require_sing_back"] = config["sing_back_required"]
    if config.get("mode") not in {"listen_and_hit", "aim_and_sing", "target_chain"}:
        config["mode"] = "listen_and_hit"
    if config.get("scale_type") not in {"major_pentatonic", "major", "minor_pentatonic"}:
        config["scale_type"] = "major_pentatonic"
    if config.get("solfege_system") not in {"movable_do", "fixed_do"}:
        config["solfege_system"] = "movable_do"
    config["target_solfege"] = _normalize_target_solfege(config.get("target_solfege"))
    if config["mode"] in {"listen_and_hit", "aim_and_sing"}:
        config["notes_per_round"] = 1
        config["current_mode"] = "aim_and_sing" if config["mode"] == "aim_and_sing" else "single_target"
    else:
        config["notes_per_round"] = max(2, config["notes_per_round"])
        config["current_mode"] = "target_chain"
    config["solfege_rounds"] = _build_solfege_rounds(config)
    config["target_rounds"] = deepcopy(config["solfege_rounds"])
    config["skin_play_mode"] = _normalize_solfege_target_skin_play_mode(config.get("skin_play_mode"), config.get("skin_id"))
    config["target_layout"] = _build_solfege_target_layout(config["target_solfege"], config["skin_play_mode"])
    config["scene_config"] = {
        "engine": "phaser_2d",
        "scene_id": "solfege_target_scene",
        "runtime_shell": config["runtime_shell"],
        "hud_model": config["hud_model"],
        "game_genre": config["game_genre"],
        "quality_gate_profile": config.get("quality_gate_profile"),
        "game_feel": config["game_feel"],
        "student_ui_mode": "game_first",
        "skin_id": config["skin_id"],
        "skin_play_mode": config["skin_play_mode"],
        "mode": config["mode"],
        "current_mode": config["current_mode"],
        "target_solfege": deepcopy(config["target_solfege"]),
        "solfege_rounds": deepcopy(config["solfege_rounds"]),
        "target_rounds": deepcopy(config["target_rounds"]),
        "target_layout": deepcopy(config["target_layout"]),
        "energy_max": config["energy_max"],
        "mistake_limit": config["mistake_limit"],
        "combo_milestones": deepcopy(config["combo_milestones"]),
        "sing_back_required": config["sing_back_required"],
        "teacher_confirm_required": config["teacher_confirm_required"],
        "mic_assist_enabled": config["mic_assist_enabled"],
        "audio_mode": config["audio_mode"],
        "input_map": deepcopy(config["input_map"]),
        "fx_profile": deepcopy(config["fx_profile"]),
        "score_model": deepcopy(config["score_model"]),
        "arcade_play_model": config["arcade_play_model"],
        "target_motion_profile": deepcopy(config["target_motion_profile"]),
        "asset_role_map": deepcopy(config["asset_role_map"]),
        "show_teacher_text_in_play": False,
        "target_hud": True,
    }
    return config


TIMBRE_INSTRUMENT_CATALOG: dict[str, dict[str, Any]] = {
    "笛子": {
        "family": "管乐",
        "traits": ["明亮", "气息感", "持续"],
        "wave": "sine",
        "frequency": 740,
        "attack": 0.04,
        "release": 0.34,
        "brightness": 0.82,
    },
    "长笛": {
        "family": "管乐",
        "traits": ["明亮", "柔和", "气息感"],
        "wave": "sine",
        "frequency": 660,
        "attack": 0.05,
        "release": 0.42,
        "brightness": 0.72,
    },
    "二胡": {
        "family": "弦乐",
        "traits": ["柔和", "持续", "弦鸣"],
        "wave": "sawtooth",
        "frequency": 392,
        "attack": 0.08,
        "release": 0.5,
        "brightness": 0.5,
    },
    "小提琴": {
        "family": "弦乐",
        "traits": ["明亮", "持续", "弦鸣"],
        "wave": "sawtooth",
        "frequency": 520,
        "attack": 0.06,
        "release": 0.46,
        "brightness": 0.68,
    },
    "古筝": {
        "family": "弹拨乐",
        "traits": ["明亮", "短促", "弦鸣"],
        "wave": "triangle",
        "frequency": 494,
        "attack": 0.02,
        "release": 0.7,
        "brightness": 0.78,
    },
    "钢琴": {
        "family": "键盘乐",
        "traits": ["明亮", "短促", "敲击感"],
        "wave": "triangle",
        "frequency": 440,
        "attack": 0.01,
        "release": 0.62,
        "brightness": 0.64,
    },
    "小鼓": {
        "family": "打击乐",
        "traits": ["短促", "敲击感", "明亮"],
        "wave": "square",
        "frequency": 180,
        "attack": 0.005,
        "release": 0.18,
        "brightness": 0.7,
    },
    "木鱼": {
        "family": "打击乐",
        "traits": ["短促", "敲击感", "木质感"],
        "wave": "square",
        "frequency": 520,
        "attack": 0.004,
        "release": 0.12,
        "brightness": 0.58,
    },
    "人声": {
        "family": "人声",
        "traits": ["柔和", "持续", "气息感"],
        "wave": "sine",
        "frequency": 330,
        "attack": 0.05,
        "release": 0.45,
        "brightness": 0.45,
    },
}


TIMBRE_COMPARISON_CUES: dict[tuple[str, str], dict[str, list[str]]] = {
    ("二胡", "小提琴"): {
        "target": ["滑音起伏比第二声更明显", "音头更像擦弦进入", "共鸣更窄更贴近民族拉弦"],
        "contrast": ["第二声更稳定明亮", "第二声线条更均匀", "第二声共鸣更宽更亮"],
    },
    ("小提琴", "二胡"): {
        "target": ["音高线条比第二声更稳定", "高频亮度更突出", "共鸣更宽更均匀"],
        "contrast": ["第二声滑音起伏更明显", "第二声音头更像擦弦进入", "第二声共鸣更窄更贴近民族拉弦"],
    },
    ("笛子", "二胡"): {
        "target": ["气流边缘比第二声更明显", "音头更像吹奏进入", "声音线条更清透"],
        "contrast": ["第二声弓弦摩擦更明显", "第二声滑音起伏更明显", "第二声拉弦共鸣更突出"],
    },
    ("二胡", "笛子"): {
        "target": ["弓弦摩擦比第二声更明显", "滑音起伏更明显", "拉弦共鸣更突出"],
        "contrast": ["第二声气流边缘更明显", "第二声音头更像吹奏进入", "第二声线条更清透"],
    },
    ("小提琴", "笛子"): {
        "target": ["弓弦持续感比第二声更明显", "声音线条更连贯", "共鸣更像拉弦发声"],
        "contrast": ["第二声气流边缘更明显", "第二声音头更像吹奏进入", "第二声更清透"],
    },
    ("笛子", "小提琴"): {
        "target": ["气流边缘比第二声更明显", "音头更像吹奏进入", "声音线条更清透"],
        "contrast": ["第二声弓弦持续感更明显", "第二声线条更连贯", "第二声共鸣更像拉弦发声"],
    },
}


def _normalize_timbre_detective_config(config: dict[str, Any]) -> dict[str, Any]:
    config["engine"] = "phaser_2d"
    config["scene_id"] = "timbre_detective_scene"
    config["game_feel"] = "animated_detective_caseboard"
    config["interaction_model"] = "listen_investigate_drag_evidence_submit"
    _apply_distinctiveness_contract(config, "timbre_detective_core")
    config["student_ui_mode"] = "game_first"
    config["audio_mode"] = _normalize_timbre_detective_audio_mode(config.get("audio_mode"))
    config["round_count"] = _clamp_int(config.get("round_count"), 1, 12, 6)
    config["choices_per_round"] = _clamp_int(config.get("choices_per_round"), 2, 6, 4)
    config["evidence_required"] = _clamp_int(config.get("evidence_required"), 1, 3, 1)
    config["retry_limit"] = _clamp_int(config.get("retry_limit"), 0, 6, 3)
    config["pass_score"] = _clamp_float(config.get("pass_score"), 0.5, 1.0, 0.8)
    config["ai_clue_policy"] = "teacher_assist_only"
    config["ai_clue_enabled"] = bool(config.get("ai_clue_enabled", False))
    if config.get("mode") not in {"instrument_clue", "family_sorting", "compare_twins"}:
        config["mode"] = "instrument_clue"
    if config.get("sound_set") not in {"classroom_instruments", "chinese_instruments", "orchestra", "found_sounds"}:
        config["sound_set"] = "classroom_instruments"
    config["instrument_pool"] = _normalize_instrument_pool(config.get("instrument_pool"))
    config["timbre_traits"] = _normalize_timbre_traits(config.get("timbre_traits"))
    if config["mode"] == "family_sorting":
        config["evidence_required"] = max(1, config["evidence_required"])
    if config["mode"] == "compare_twins":
        config["choices_per_round"] = max(3, config["choices_per_round"])
        config["evidence_required"] = max(2, config["evidence_required"])
    config["comparison_reason_required"] = config["mode"] == "compare_twins"
    config["skin_play_mode"] = _normalize_timbre_detective_skin_play_mode(config.get("skin_play_mode"), config.get("skin_id"))
    config["timbre_rounds"] = _build_timbre_rounds(config)
    config["clue_cases"] = _build_timbre_clue_cases(config)
    config["suspect_cards"] = _build_timbre_suspect_cards(config)
    config["evidence_tokens"] = _build_timbre_evidence_tokens(config)
    config["case_progress"] = {
        "total_cases": len(config["clue_cases"]),
        "solved_cases": 0,
        "evidence_required": config["evidence_required"],
    }
    config["scene_config"] = {
        "engine": "phaser_2d",
        "scene_id": "timbre_detective_scene",
        "runtime_shell": config["runtime_shell"],
        "hud_model": config["hud_model"],
        "interaction_model": config["interaction_model"],
        "game_genre": config["game_genre"],
        "quality_gate_profile": config.get("quality_gate_profile"),
        "game_feel": config["game_feel"],
        "student_ui_mode": "game_first",
        "skin_id": config["skin_id"],
        "skin_play_mode": config["skin_play_mode"],
        "mode": config["mode"],
        "instrument_pool": deepcopy(config["instrument_pool"]),
        "timbre_traits": deepcopy(config["timbre_traits"]),
        "choices_per_round": config["choices_per_round"],
        "evidence_required": config["evidence_required"],
        "comparison_reason_required": config["comparison_reason_required"],
        "clue_cases": deepcopy(config["clue_cases"]),
        "suspect_cards": deepcopy(config["suspect_cards"]),
        "evidence_tokens": deepcopy(config["evidence_tokens"]),
        "case_progress": deepcopy(config["case_progress"]),
        "audio_mode": config["audio_mode"],
        "ai_clue_enabled": config["ai_clue_enabled"],
        "ai_clue_policy": config["ai_clue_policy"],
        "hf_model_id": config.get("hf_model_id"),
        "detective_hud": True,
        "dynamic_case_scene": True,
        "input_actions": ["listen", "select_suspect", "toggle_evidence", "select_contrast_evidence", "submit_case", "next_case", "reset"],
        "fx_profile": {
            "wave_scan": "frequency_rings",
            "clue_line": "caseboard_thread",
            "stamp_drop": "case_solved_stamp",
            "miss": "desk_shake_red_stamp",
            "reward": "badge_burst",
        },
        "score_model": {
            "perfect": 520,
            "evidence": 90,
            "solved": 280,
            "wrong": -80,
        },
        "show_teacher_text_in_play": False,
        "teacher_assist_only": True,
    }
    return config


def _normalize_form_treasure_config(config: dict[str, Any]) -> dict[str, Any]:
    config["engine"] = "phaser_2d"
    config["scene_id"] = "form_treasure_scene"
    config["game_feel"] = "form_treasure_hunt"
    config["interaction_model"] = "listen_place_card_use_tool_verify"
    config["publish_quality_profile"] = "arcade_h5"
    _apply_distinctiveness_contract(config, "form_treasure_core")
    config["student_ui_mode"] = "game_first"
    config["audio_mode"] = _normalize_form_treasure_audio_mode(config.get("audio_mode"))
    config["round_count"] = _clamp_int(config.get("round_count"), 1, 6, 3)
    config["retry_limit"] = _clamp_int(config.get("retry_limit"), 0, 6, 3)
    config["pass_score"] = _clamp_float(config.get("pass_score"), 0.5, 1.0, 0.8)
    config["section_length_bars"] = _normalize_section_length_bars(config.get("section_length_bars"))
    config["hint_mode"] = _normalize_form_hint_mode(config.get("hint_mode"))
    config["form_type"] = _normalize_form_type(config.get("form_type"), config.get("mode"))
    config["mode"] = _mode_for_form_type(config["form_type"], config.get("mode"))
    config["allow_relisten"] = bool(config.get("allow_relisten", True))
    config["skin_play_mode"] = _normalize_form_treasure_skin_play_mode(config.get("skin_play_mode"), config.get("skin_id"))
    config["answer_pattern"] = _answer_pattern_for_form_type(config["form_type"])
    config["timeline_segments"] = _build_form_timeline_segments(config)
    config["structure_cards"] = _build_form_structure_cards(config)
    config["progress_model"] = {
        "total_segments": len(config["timeline_segments"]),
        "required_correct": max(1, math.ceil(len(config["timeline_segments"]) * config["pass_score"])),
        "treasure_label": _form_treasure_reward_for_skin(config["skin_play_mode"]),
    }
    config["scene_config"] = {
        "engine": "phaser_2d",
        "scene_id": "form_treasure_scene",
        "runtime_shell": config["runtime_shell"],
        "hud_model": config["hud_model"],
        "interaction_model": config["interaction_model"],
        "game_genre": config["game_genre"],
        "quality_gate_profile": config.get("quality_gate_profile"),
        "publish_quality_profile": config["publish_quality_profile"],
        "game_feel": config["game_feel"],
        "student_ui_mode": "game_first",
        "dynamic_map_scene": True,
        "skin_id": config["skin_id"],
        "skin_play_mode": config["skin_play_mode"],
        "mode": config["mode"],
        "form_type": config["form_type"],
        "section_length_bars": config["section_length_bars"],
        "hint_mode": config["hint_mode"],
        "timeline_segments": deepcopy(config["timeline_segments"]),
        "structure_cards": deepcopy(config["structure_cards"]),
        "answer_pattern": deepcopy(config["answer_pattern"]),
        "progress_model": deepcopy(config["progress_model"]),
        "audio_mode": config["audio_mode"],
        "allow_relisten": config["allow_relisten"],
        "show_teacher_text_in_play": False,
        "form_hud": True,
        "input_actions": deepcopy(config["input_actions"]),
        "fx_profile": deepcopy(config["fx_profile"]),
        "score_model": deepcopy(config["score_model"]),
    }
    return config


def _normalize_composition_puzzle_config(config: dict[str, Any]) -> dict[str, Any]:
    config["engine"] = "phaser_2d"
    config["scene_id"] = "composition_puzzle_scene"
    config["game_feel"] = "arcade_composition_studio"
    _apply_distinctiveness_contract(config, "composition_puzzle_core")
    config["student_ui_mode"] = "game_first"
    config["audio_mode"] = _normalize_composition_audio_mode(config.get("audio_mode"))
    config["mode"] = _normalize_composition_mode(config.get("mode"))
    config["bpm"] = _clamp_int(config.get("bpm"), 60, 132, 92)
    config["round_count"] = _clamp_int(config.get("round_count"), 1, 8, 4)
    config["retry_limit"] = _clamp_int(config.get("retry_limit"), 0, 6, 3)
    config["pass_score"] = _clamp_float(config.get("pass_score"), 0.5, 1.0, 0.8)
    raw_total_bars = config.get("composition_total_bars")
    if raw_total_bars is None:
        raw_total_bars = config.get("phrase_length_bars")
    total_bars = _clamp_int(raw_total_bars, 1, 32, 2)
    try:
        config["length_clamped"] = int(raw_total_bars) != total_bars
    except (TypeError, ValueError):
        config["length_clamped"] = False
    raw_segment_bars = config.get("composition_segment_bars")
    if raw_segment_bars is None:
        raw_segment_bars = min(4, total_bars)
    segment_bars = _clamp_int(raw_segment_bars, 1, min(4, total_bars), min(4, total_bars))
    config["composition_total_bars"] = total_bars
    config["composition_segment_bars"] = segment_bars
    config["composition_segments"] = max(1, math.ceil(total_bars / segment_bars))
    config["phrase_length_bars"] = segment_bars
    meter = str(config.get("meter") or "2/4")
    if meter not in {"2/4", "3/4", "4/4"}:
        meter = "2/4"
    config["meter"] = meter
    config["slots_per_bar"] = int(meter.split("/", 1)[0])
    config["constraint_profile"] = _normalize_constraint_profile(config.get("constraint_profile"))
    config["teacher_confirm_required"] = bool(config.get("teacher_confirm_required", True))
    config["rhythm_cards"] = _normalize_composition_rhythm_cards(config.get("rhythm_cards"))
    config["melody_cards"] = _normalize_composition_melody_cards(config.get("melody_cards"))
    config["required_elements"] = _composition_required_elements(config)
    config["skin_play_mode"] = _normalize_composition_puzzle_skin_play_mode(config.get("skin_play_mode"), config.get("skin_id"))
    config["composition_rounds"] = _build_composition_rounds(config)
    config["constraint_checks"] = _build_composition_constraint_checks(config)
    config["scene_config"] = {
        "engine": "phaser_2d",
        "scene_id": "composition_puzzle_scene",
        "runtime_shell": config["runtime_shell"],
        "hud_model": config["hud_model"],
        "game_genre": config["game_genre"],
        "quality_gate_profile": config.get("quality_gate_profile"),
        "game_feel": config["game_feel"],
        "student_ui_mode": "game_first",
        "skin_id": config["skin_id"],
        "skin_play_mode": config["skin_play_mode"],
        "mode": config["mode"],
        "meter": config.get("meter", "2/4"),
        "bpm": config["bpm"],
        "phrase_length_bars": config["phrase_length_bars"],
        "composition_total_bars": config["composition_total_bars"],
        "composition_segment_bars": config["composition_segment_bars"],
        "composition_segments": config["composition_segments"],
        "length_clamped": config["length_clamped"],
        "slots_per_bar": config["slots_per_bar"],
        "constraint_profile": config["constraint_profile"],
        "rhythm_cards": deepcopy(config["rhythm_cards"]),
        "melody_cards": deepcopy(config["melody_cards"]),
        "composition_rounds": deepcopy(config["composition_rounds"]),
        "constraint_checks": deepcopy(config["constraint_checks"]),
        "teacher_confirm_required": config["teacher_confirm_required"],
        "audio_mode": config["audio_mode"],
        "composition_hud": True,
        "phaser_drag_scene": True,
        "show_teacher_text_in_play": False,
    }
    return config


def _normalize_form_type(value: Any, mode: Any = None) -> str:
    raw = str(value or "").strip().upper()
    mode_raw = str(mode or "").strip()
    if raw in {"ABA", "A-B-A"}:
        return "ABA"
    if raw in {"回旋", "RONDO"}:
        return "回旋"
    if raw in {"重复对比", "REPEAT_CONTRAST"}:
        return "重复对比"
    if mode_raw == "rondo_treasure":
        return "回旋"
    if mode_raw == "repeat_contrast":
        return "重复对比"
    if mode_raw == "aba_treasure":
        return "ABA"
    return "ABA"


def _mode_for_form_type(form_type: str, current: Any = None) -> str:
    candidate = str(current or "").strip()
    expected = {"ABA": "aba_treasure", "回旋": "rondo_treasure", "重复对比": "repeat_contrast"}.get(form_type, "aba_treasure")
    if expected:
        return expected
    if candidate in {"aba_treasure", "rondo_treasure", "repeat_contrast"}:
        return candidate
    return "aba_treasure"


def _normalize_section_length_bars(value: Any) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = 8
    return min((4, 8, 12, 16), key=lambda item: abs(item - number))


def _normalize_form_hint_mode(value: Any) -> str:
    mode = str(value or "partial").strip()
    if mode in {"guided", "partial", "challenge"}:
        return mode
    aliases = {"引导": "guided", "半提示": "partial", "挑战": "challenge"}
    return aliases.get(mode, "partial")


def _answer_pattern_for_form_type(form_type: str) -> list[str]:
    if form_type == "回旋":
        return ["A", "B", "A", "C", "A"]
    if form_type == "重复对比":
        return ["A", "A", "B", "B"]
    return ["A", "B", "A"]


def _build_form_timeline_segments(config: dict[str, Any]) -> list[dict[str, Any]]:
    pattern = config["answer_pattern"]
    segments: list[dict[str, Any]] = []
    for index, label in enumerate(pattern):
        segments.append(
            {
                "id": f"seg-{index + 1}",
                "label": label,
                "name": _form_segment_name(label),
                "bars": config["section_length_bars"],
                "start_bar": index * config["section_length_bars"] + 1,
                "midi_offsets": _form_segment_offsets(label),
                "hint": _form_segment_hint(label, config["hint_mode"]),
            }
        )
    return segments


def _build_form_structure_cards(config: dict[str, Any]) -> list[dict[str, Any]]:
    labels = []
    for label in config["answer_pattern"]:
        if label not in labels:
            labels.append(label)
    if config["hint_mode"] != "guided" and "C" not in labels and config["form_type"] != "ABA":
        labels.append("C")
    return [
        {
            "id": f"card-{label}",
            "label": label,
            "name": _form_segment_name(label),
            "description": _form_segment_hint(label, config["hint_mode"]),
        }
        for label in labels
    ]


def _form_segment_name(label: str) -> str:
    return {"A": "主题段", "B": "对比段", "C": "新材料段"}.get(label, "段落")


def _form_segment_hint(label: str, hint_mode: str) -> str:
    if hint_mode == "challenge":
        return "只听音乐判断段落关系。"
    hints = {
        "A": "主题旋律会再次出现。",
        "B": "这里和主题形成对比。",
        "C": "这里出现新的材料。",
    }
    if hint_mode == "guided":
        return hints.get(label, "听它和前面是否相同。")
    return {"A": "像主题", "B": "有对比", "C": "新材料"}.get(label, "听关系")


def _form_segment_offsets(label: str) -> list[int]:
    return {
        "A": [0, 2, 4, 2],
        "B": [5, 4, 2, 0],
        "C": [7, 5, 4, 7],
    }.get(label, [0, 2, 4, 2])


def _form_treasure_reward_for_skin(skin_play_mode: str) -> str:
    return {
        "map": "宝箱开启",
        "constellation": "星门点亮",
        "gallery": "展馆盖章",
        "train": "列车到站",
        "stage": "终幕亮灯",
    }.get(skin_play_mode, "宝藏点亮")


def _normalize_skin_id(template_id: str, skin_id: Any) -> str:
    template = GAME_TEMPLATE_REGISTRY.get(template_id) or {}
    supported = template.get("supported_skins") or []
    candidate = str(skin_id or "").strip()
    if candidate in supported:
        return candidate
    default_config = template.get("default_config") or {}
    fallback = str(default_config.get("skin_id") or "")
    return fallback if fallback in supported else str(supported[0] if supported else "")


def _normalize_pitch_range(value: Any) -> list[str]:
    if not isinstance(value, list):
        value = PITCH_LADDER_DEFAULT_CONFIG["pitch_range"]
    allowed = _resolved_pitch_ids(value)
    ordered = [pitch for pitch in PITCH_ORDER if pitch in allowed]
    return ordered if len(ordered) >= 2 else deepcopy(PITCH_LADDER_DEFAULT_CONFIG["pitch_range"])


def _normalize_target_solfege(value: Any) -> list[str]:
    if not isinstance(value, list):
        value = SOLFEGE_TARGET_DEFAULT_CONFIG["target_solfege"]
    allowed = _resolved_pitch_ids(value)
    ordered = [pitch for pitch in PITCH_ORDER if pitch in allowed]
    return ordered if len(ordered) >= 2 else deepcopy(SOLFEGE_TARGET_DEFAULT_CONFIG["target_solfege"])


def _resolved_pitch_ids(values: list[Any]) -> list[str]:
    resolved_ids: list[str] = []
    for value in values:
        pitch = resolve_pitch_token(value)
        if pitch and pitch["id"] not in resolved_ids:
            resolved_ids.append(str(pitch["id"]))
    return resolved_ids


def _normalize_instrument_pool(value: Any) -> list[str]:
    if not isinstance(value, list):
        value = TIMBRE_DETECTIVE_DEFAULT_CONFIG["instrument_pool"]
    allowed = [str(item) for item in value if str(item) in TIMBRE_INSTRUMENT_CATALOG]
    unique = []
    for instrument in allowed:
        if instrument not in unique:
            unique.append(instrument)
    return unique if len(unique) >= 2 else deepcopy(TIMBRE_DETECTIVE_DEFAULT_CONFIG["instrument_pool"])


def _normalize_timbre_traits(value: Any) -> list[str]:
    fallback = TIMBRE_DETECTIVE_DEFAULT_CONFIG["timbre_traits"]
    if not isinstance(value, list):
        value = fallback
    traits = []
    for item in value:
        trait = str(item)
        if trait and trait not in traits:
            traits.append(trait)
    return traits if len(traits) >= 3 else deepcopy(fallback)


def _build_pitch_rounds(config: dict[str, Any]) -> list[dict[str, Any]]:
    pitch_range = config["pitch_range"]
    rounds: list[dict[str, Any]] = []
    for index in range(config["round_count"]):
        if config["mode"] == "solfege_ladder":
            note = pitch_range[index % len(pitch_range)]
            sequence = [note]
            answer = note
        elif config["mode"] == "melody_climb":
            start = index % len(pitch_range)
            sequence = [pitch_range[(start + step) % len(pitch_range)] for step in range(config["notes_per_round"])]
            if index % 2:
                sequence = list(reversed(sequence))
            answer = sequence
        else:
            first = pitch_range[index % len(pitch_range)]
            offset = (index % 3) - 1
            if offset == 0:
                second = first
            else:
                first_index = pitch_range.index(first)
                second_index = max(0, min(len(pitch_range) - 1, first_index + offset))
                second = pitch_range[second_index]
                if second == first and len(pitch_range) > 1:
                    second = pitch_range[min(len(pitch_range) - 1, first_index + 1)]
            sequence = [first, second]
            answer = _pitch_direction(first, second)
        rounds.append(
            {
                "id": f"p{index + 1}",
                "sequence": sequence,
                "labels": [PITCH_LABELS.get(note, note) for note in sequence],
                "midi_offsets": [PITCH_SEMITONES.get(note, 0) for note in sequence],
                "answer": answer,
            }
        )
    return rounds


def _build_pitch_route_nodes(pitch_range: list[str]) -> list[dict[str, Any]]:
    if not pitch_range:
        pitch_range = deepcopy(PITCH_LADDER_DEFAULT_CONFIG["pitch_range"])
    total = max(1, len(pitch_range) - 1)
    nodes: list[dict[str, Any]] = []
    for index, note in enumerate(pitch_range):
        height = round(index / total, 3)
        nodes.append(
            {
                "id": note,
                "note": note,
                "label": PITCH_LABELS.get(note, note),
                "midi_offset": PITCH_SEMITONES.get(note, 0),
                "level": index,
                "height": height,
            }
        )
    return nodes


def _build_pitch_path(rounds: list[dict[str, Any]], route_nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    levels = {node["note"]: node["level"] for node in route_nodes}
    path: list[dict[str, Any]] = []
    for round_item in rounds:
        sequence = [str(note) for note in round_item.get("sequence", []) if str(note) in levels]
        if not sequence:
            continue
        path.append(
            {
                "round_id": round_item.get("id"),
                "sequence": sequence,
                "levels": [levels[note] for note in sequence],
                "answer": deepcopy(round_item.get("answer")),
            }
        )
    return path


def _build_solfege_target_layout(targets: list[str], skin_play_mode: str) -> list[dict[str, Any]]:
    if not targets:
        targets = deepcopy(SOLFEGE_TARGET_DEFAULT_CONFIG["target_solfege"])
    count = len(targets)
    layout: list[dict[str, Any]] = []
    points = _solfege_target_arena_points(count, skin_play_mode)
    for index, note in enumerate(targets):
        point = points[index % len(points)]
        layout.append(
            {
                "id": note,
                "note": note,
                "label": PITCH_LABELS.get(note, note),
                "midi_offset": PITCH_SEMITONES.get(note, 0),
                "x": round(point["x"], 3),
                "y": round(point["y"], 3),
            }
        )
    return layout


def _solfege_target_arena_points(count: int, skin_play_mode: str) -> list[dict[str, float]]:
    if skin_play_mode == "archery":
        return [
            {
                "x": 0.34 + (index / max(1, count - 1)) * 0.34,
                "y": 0.34 + (index % 2) * 0.22,
            }
            for index in range(max(1, count))
        ]
    if skin_play_mode == "bubble":
        return [
            {
                "x": 0.32 + (index / max(1, count - 1)) * 0.36,
                "y": 0.32 + ((index * 29) % 28) / 100,
            }
            for index in range(max(1, count))
        ]
    presets: dict[int, list[dict[str, float]]] = {
        1: [{"x": 0.5, "y": 0.44}],
        2: [{"x": 0.42, "y": 0.42}, {"x": 0.58, "y": 0.42}],
        3: [{"x": 0.5, "y": 0.32}, {"x": 0.39, "y": 0.54}, {"x": 0.61, "y": 0.54}],
        4: [{"x": 0.39, "y": 0.34}, {"x": 0.61, "y": 0.34}, {"x": 0.41, "y": 0.57}, {"x": 0.59, "y": 0.57}],
        5: [{"x": 0.5, "y": 0.29}, {"x": 0.36, "y": 0.43}, {"x": 0.64, "y": 0.43}, {"x": 0.42, "y": 0.62}, {"x": 0.58, "y": 0.62}],
    }
    if count <= 5:
        return presets[max(1, count)]
    return [
        {
            "x": 0.34 + (index % 3) * 0.16,
            "y": 0.3 + (index // 3) * 0.17,
        }
        for index in range(count)
    ]


def _build_timbre_rounds(config: dict[str, Any]) -> list[dict[str, Any]]:
    pool = config["instrument_pool"]
    trait_pool = config["timbre_traits"]
    families = sorted({TIMBRE_INSTRUMENT_CATALOG[item]["family"] for item in pool})
    rounds: list[dict[str, Any]] = []
    for index in range(config["round_count"]):
        target = pool[index % len(pool)]
        target_info = TIMBRE_INSTRUMENT_CATALOG[target]
        compare_with = None
        answer: str | list[str] = target
        prompt = "找出声音证物对应的嫌疑乐器，并标记音色证据。"
        if config["mode"] == "family_sorting":
            answer = str(target_info["family"])
            prompt = "先不急着猜乐器，把声音证物归入正确的乐器家族。"
        elif config["mode"] == "compare_twins":
            compare_with = _pick_compare_instrument(target, pool)
            prompt = f"比较两个相似声音，找出第一个声音更像哪位嫌疑人：{target} 还是 {compare_with}。"
        candidates = _build_timbre_candidates(config, target, families)
        evidence_answer = [trait for trait in target_info["traits"] if trait in trait_pool]
        if not evidence_answer:
            evidence_answer = list(target_info["traits"][: config["evidence_required"]])
        evidence_options = _build_evidence_options(trait_pool, evidence_answer, config["evidence_required"] + 4)
        contrast_evidence_answer: list[str] = []
        contrast_evidence_options: list[str] = []
        if compare_with:
            comparison_cues = _comparison_cues_for_timbre(target, compare_with)
            evidence_answer = comparison_cues["target"]
            evidence_options = comparison_cues["options"]
            contrast_evidence_answer = comparison_cues["contrast"]
            contrast_evidence_options = comparison_cues["options"]
        rounds.append(
            {
                "id": f"t{index + 1}",
                "mode": config["mode"],
                "prompt": prompt,
                "compare_prompt": _timbre_compare_prompt(target, compare_with, contrast_evidence_answer),
                "target": target,
                "family": target_info["family"],
                "traits": target_info["traits"],
                "candidates": candidates,
                "evidence_options": evidence_options,
                "evidence_answer": evidence_answer if compare_with else evidence_answer[: config["evidence_required"]],
                "answer": answer,
                "compare_with": compare_with,
                "audio_profile": _audio_profile_for_instrument(target),
                "compare_audio_profile": _audio_profile_for_instrument(compare_with) if compare_with else None,
                "comparison_reason_required": bool(compare_with),
                "contrast_evidence_options": contrast_evidence_options,
                "contrast_evidence_answer": contrast_evidence_answer,
                "reason_frame": {
                    "target": target,
                    "contrast": compare_with or "",
                    "sentence": f"第一声相对第二声{{evidence}}，所以更像{target}；对照线索是{{contrast_evidence}}。",
                },
            }
        )
    return rounds


def _build_timbre_clue_cases(config: dict[str, Any]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for index, round_item in enumerate(config.get("timbre_rounds", [])):
        if not isinstance(round_item, dict):
            continue
        answer = round_item.get("answer")
        answer_label = " / ".join(str(item) for item in answer) if isinstance(answer, list) else str(answer or "")
        cases.append(
            {
                "id": round_item.get("id") or f"case-{index + 1}",
                "case_number": index + 1,
                "title": _timbre_case_title(config.get("skin_play_mode"), index),
                "prompt": round_item.get("prompt") or "听声音证物，找出嫌疑对象和证据。",
                "target": round_item.get("target", ""),
                "answer": answer,
                "answer_label": answer_label,
                "family": round_item.get("family", ""),
                "candidates": deepcopy(round_item.get("candidates", [])),
                "evidence_options": deepcopy(round_item.get("evidence_options", [])),
                "evidence_answer": deepcopy(round_item.get("evidence_answer", [])),
                "audio_profile": deepcopy(round_item.get("audio_profile")),
                "playback_url": round_item.get("playback_url", ""),
                "audio_clip_url": round_item.get("audio_clip_url", ""),
                "source_audio_url": round_item.get("source_audio_url", ""),
                "audio_url": round_item.get("audio_url", ""),
                "compare_with": round_item.get("compare_with"),
                "compare_prompt": round_item.get("compare_prompt", ""),
                "compare_audio_profile": deepcopy(round_item.get("compare_audio_profile")),
                "compare_playback_url": round_item.get("compare_playback_url", ""),
                "compare_audio_clip_url": round_item.get("compare_audio_clip_url", ""),
                "compare_source_audio_url": round_item.get("compare_source_audio_url", ""),
                "compare_audio_url": round_item.get("compare_audio_url", ""),
                "comparison_reason_required": bool(round_item.get("comparison_reason_required")),
                "contrast_evidence_options": deepcopy(round_item.get("contrast_evidence_options", [])),
                "contrast_evidence_answer": deepcopy(round_item.get("contrast_evidence_answer", [])),
                "reason_frame": deepcopy(round_item.get("reason_frame", {})),
                "ai_teacher_clue": _timbre_teacher_clue(round_item),
            }
        )
    return cases


def _build_timbre_suspect_cards(config: dict[str, Any]) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    if config.get("mode") == "family_sorting":
        values = sorted({TIMBRE_INSTRUMENT_CATALOG[item]["family"] for item in config["instrument_pool"]})
        for family in ["管乐", "弦乐", "打击乐", "键盘乐", "弹拨乐", "人声"]:
            if family not in values:
                values.append(family)
        for index, family in enumerate(values[: config["choices_per_round"] + 2]):
            cards.append(
                {
                    "id": f"family-{index + 1}",
                    "label": family,
                    "type": "family",
                    "hint": "根据发声方式归档。",
                    "visual": _timbre_suspect_visual(family),
                }
            )
        return cards

    for instrument in config["instrument_pool"]:
        info = TIMBRE_INSTRUMENT_CATALOG[instrument]
        cards.append(
            {
                "id": instrument,
                "label": instrument,
                "type": "instrument",
                "family": info["family"],
                "hint": " / ".join(info["traits"][:2]),
                "visual": _timbre_suspect_visual(info["family"]),
            }
        )
    return cards


def _build_timbre_evidence_tokens(config: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "id": trait,
            "label": trait,
            "type": _timbre_trait_type(trait),
            "teacher_prompt": _timbre_trait_prompt(trait),
        }
        for trait in config["timbre_traits"]
    ]


def _timbre_case_title(skin_play_mode: Any, index: int) -> str:
    prefix = {
        "casebook": "案卷",
        "museum": "展柜",
        "forest": "回声足迹",
        "studio": "音轨",
        "theater": "声影",
    }.get(str(skin_play_mode or ""), "案卷")
    return f"{prefix} {index + 1}"


def _timbre_teacher_clue(round_item: dict[str, Any]) -> str:
    traits = round_item.get("evidence_answer") if isinstance(round_item.get("evidence_answer"), list) else []
    family = str(round_item.get("family") or "声音家族")
    clue = "、".join(str(item) for item in traits[:2]) or "起音和延音"
    return f"教师辅助：可提醒学生关注{family}的{clue}，但不直接公布答案。"


def _timbre_suspect_visual(value: str) -> str:
    return {
        "管乐": "气流",
        "弦乐": "弓弦",
        "打击乐": "鼓点",
        "键盘乐": "琴键",
        "弹拨乐": "拨弦",
        "人声": "声波",
    }.get(value, "声纹")


def _timbre_trait_type(trait: str) -> str:
    if trait in {"短促", "持续"}:
        return "duration"
    if trait in {"明亮", "柔和", "木质感"}:
        return "color"
    if trait in {"气息感", "弦鸣", "敲击感"}:
        return "source"
    return "texture"


def _timbre_trait_prompt(trait: str) -> str:
    return {
        "明亮": "声音是否有清晰、发亮的边缘？",
        "柔和": "声音是否圆润、不刺耳？",
        "短促": "声音是否很快结束？",
        "持续": "声音是否能拉长保持？",
        "气息感": "能不能听到吹奏或呼吸的感觉？",
        "弦鸣": "是否像弦被拉动或振动？",
        "敲击感": "起音是不是像敲出来的？",
        "木质感": "声音是否有木头共鸣的质地？",
    }.get(trait, "这个词能否说明你听到的声音？")


def _build_timbre_candidates(config: dict[str, Any], target: str, families: list[str]) -> list[str]:
    if config["mode"] == "family_sorting":
        candidates = [TIMBRE_INSTRUMENT_CATALOG[target]["family"]]
        for family in families:
            if family not in candidates:
                candidates.append(family)
        for family in ["管乐", "弦乐", "打击乐", "键盘乐", "弹拨乐", "人声"]:
            if family not in candidates:
                candidates.append(family)
        return candidates[: config["choices_per_round"]]
    pool = config["instrument_pool"]
    candidates = [target]
    start = pool.index(target) if target in pool else 0
    for step in range(1, len(pool) + 1):
        candidate = pool[(start + step) % len(pool)]
        if candidate not in candidates:
            candidates.append(candidate)
        if len(candidates) >= config["choices_per_round"]:
            break
    return candidates


def _build_evidence_options(trait_pool: list[str], answers: list[str], limit: int) -> list[str]:
    options = list(answers)
    for trait in trait_pool:
        if trait not in options:
            options.append(trait)
        if len(options) >= limit:
            break
    return options


def _comparison_cues_for_timbre(target: str, compare_with: str) -> dict[str, list[str]]:
    pair = TIMBRE_COMPARISON_CUES.get((target, compare_with))
    if pair:
        target_cues = list(pair["target"])
        contrast_cues = list(pair["contrast"])
    else:
        target_info = TIMBRE_INSTRUMENT_CATALOG[target]
        compare_info = TIMBRE_INSTRUMENT_CATALOG[compare_with]
        target_cues = _generic_comparison_cues(target_info, compare_info, "第一声")
        contrast_cues = _generic_comparison_cues(compare_info, target_info, "第二声")
    options = []
    for cue in [*target_cues, *contrast_cues]:
        if cue not in options:
            options.append(cue)
    return {"target": target_cues, "contrast": contrast_cues, "options": options[:6]}


def _generic_comparison_cues(primary: dict[str, Any], other: dict[str, Any], label: str) -> list[str]:
    cues: list[str] = []
    if float(primary.get("attack", 0.05)) < float(other.get("attack", 0.05)):
        cues.append(f"{label}音头更直接")
    else:
        cues.append(f"{label}音头进入更柔和")
    if float(primary.get("release", 0.4)) > float(other.get("release", 0.4)):
        cues.append(f"{label}尾音保持更久")
    else:
        cues.append(f"{label}收音更干脆")
    if float(primary.get("brightness", 0.5)) > float(other.get("brightness", 0.5)):
        cues.append(f"{label}高频亮度更突出")
    else:
        cues.append(f"{label}亮度更收敛")
    return cues


def _contrast_traits_for_timbre(target_traits: list[str], compare_traits: list[str], trait_pool: list[str]) -> list[str]:
    contrasts = [trait for trait in compare_traits if trait not in target_traits and trait in trait_pool]
    if contrasts:
        return contrasts
    contrasts = [trait for trait in target_traits if trait in trait_pool]
    if contrasts:
        return contrasts[:1]
    return [trait_pool[0]] if trait_pool else []


def _timbre_compare_prompt(target: str, compare_with: str | None, contrast_traits: list[str]) -> str:
    if not compare_with:
        return ""
    return f"比较第一声和第二声的相对差异：哪条线索能说明第一声更像{target}，而不是{compare_with}？"


def _pick_compare_instrument(target: str, pool: list[str]) -> str:
    target_family = TIMBRE_INSTRUMENT_CATALOG[target]["family"]
    for instrument in pool:
        if instrument != target and TIMBRE_INSTRUMENT_CATALOG[instrument]["family"] == target_family:
            return instrument
    for instrument in pool:
        if instrument != target:
            return instrument
    return target


def _audio_profile_for_instrument(instrument: str | None) -> dict[str, Any] | None:
    if not instrument:
        return None
    info = TIMBRE_INSTRUMENT_CATALOG[instrument]
    return {
        "wave": info["wave"],
        "frequency": info["frequency"],
        "attack": info["attack"],
        "release": info["release"],
        "brightness": info["brightness"],
    }


def _build_solfege_rounds(config: dict[str, Any]) -> list[dict[str, Any]]:
    targets = config["target_solfege"]
    rounds: list[dict[str, Any]] = []
    for index in range(config["round_count"]):
        if config["mode"] == "target_chain":
            start = index % len(targets)
            sequence = [targets[(start + step) % len(targets)] for step in range(config["notes_per_round"])]
            if index % 2:
                sequence = list(reversed(sequence))
            answer: str | list[str] = sequence
        else:
            note = targets[index % len(targets)]
            sequence = [note]
            answer = note
        rounds.append(
            {
                "id": f"s{index + 1}",
                "sequence": sequence,
                "labels": [PITCH_LABELS.get(note, note) for note in sequence],
                "midi_offsets": [PITCH_SEMITONES.get(note, 0) for note in sequence],
                "answer": answer,
                "sing_back_required": bool(config.get("require_sing_back")),
                "teacher_confirm_required": bool(config.get("teacher_confirm_required")),
            }
        )
    return rounds


def _pitch_direction(first: str, second: str) -> str:
    first_index = PITCH_ORDER.index(first)
    second_index = PITCH_ORDER.index(second)
    if second_index > first_index:
        return "higher"
    if second_index < first_index:
        return "lower"
    return "same"


def _filter_pattern_pool(config: dict[str, Any], allowed_difficulty: int) -> list[dict[str, Any]]:
    pool = config.get("pattern_pool")
    if not isinstance(pool, list):
        pool = RHYTHM_ECHO_DEFAULT_CONFIG["pattern_pool"]
    filtered = [
        deepcopy(item)
        for item in pool
        if isinstance(item, dict) and int(item.get("difficulty") or 1) <= allowed_difficulty
    ]
    return filtered or deepcopy(RHYTHM_ECHO_DEFAULT_CONFIG["pattern_pool"][:3])


def _student_task_for_config(template_id: str, config: dict[str, Any]) -> dict[str, str]:
    if template_id == "beat_guardian_core":
        return {
            "listen": "听清稳定拍和第 1 拍重音周期",
            "do": _student_action_for_beat_guardian_mode(config["mode"]),
            "pass": "清掉全部弱拍怪物后，说出本轮强弱规律",
        }
    if template_id == "pitch_ladder_core":
        return {
            "listen": "先听目标音或音列",
            "do": _student_action_for_pitch_ladder_mode(config["mode"]),
            "pass": "找对音高路线后，把这组音唱出来",
        }
    if template_id == "solfege_target_core":
        return {
            "listen": "先听目标音，在心里找到唱名",
            "do": _student_action_for_solfege_target_mode(config["mode"]),
            "pass": "击中唱名靶后，把目标音或音组唱回出来",
        }
    if template_id == "timbre_detective_core":
        return {
            "listen": "先听声音证物，抓住音色线索",
            "do": _student_action_for_timbre_detective_mode(config["mode"]),
            "pass": "乐器或家族判断成立后，说出至少一个音色证据",
        }
    if template_id == "form_treasure_core":
        return {
            "listen": "先听每个段落，判断主题是否重复或对比",
            "do": _student_action_for_form_treasure_mode(config["mode"]),
            "pass": "曲式路线点亮后，说出 ABA、回旋或重复对比的依据",
        }
    if template_id == "composition_puzzle_core":
        return {
            "listen": "试听自己拼出的音乐短句，检查小节是否完整",
            "do": _student_action_for_composition_mode(config["mode"]),
            "pass": "规则清单通过后，请教师确认创编理由和音乐性",
        }
    return {
        "listen": "先听目标节奏",
        "do": _student_action_for_rhythm_echo_mode(config["mode"]),
        "pass": "达到通关分后，用拍手或口读再表现一次",
    }


def _student_action_for_rhythm_echo_mode(mode: str) -> str:
    if mode == "echo_body_percussion":
        return "用拍手、拍腿或跺脚复刻节奏"
    if mode == "echo_chain":
        return "先复刻，再接一小节自己的回应"
    return "用点击或键盘复刻拍点"


def _student_action_for_beat_guardian_mode(mode: str) -> str:
    if mode == "beat_defense":
        return "观察护盾呼吸，先把身体里的拍子立住"
    if mode == "meter_gate":
        return "根据拍号感受护盾周期，在第 1 拍同步充能"
    return "只在第 1 拍同步充能，弱拍先蓄住"


def _student_action_for_pitch_ladder_mode(mode: str) -> str:
    if mode == "solfege_ladder":
        return "听目标音，把唱名放到对应台阶"
    if mode == "melody_climb":
        return "听短旋律，按顺序走出台阶路线"
    return "听两个音，判断第二个音更高、更低还是相同"


def _student_action_for_solfege_target_mode(mode: str) -> str:
    if mode == "aim_and_sing":
        return "瞄准目标唱名后，先唱出来再由教师确认"
    if mode == "target_chain":
        return "听一组音，按顺序击中唱名靶并唱回整组"
    return "听单个目标音，击中对应唱名靶"


def _student_action_for_timbre_detective_mode(mode: str) -> str:
    if mode == "family_sorting":
        return "把声音证物归入正确的乐器家族，并说明发声方式"
    if mode == "compare_twins":
        return "比较两个相似声音，找出差异并标记证据"
    return "选择嫌疑乐器，再选择支持判断的音色证据"


def _student_action_for_form_treasure_mode(mode: str) -> str:
    if mode == "rondo_treasure":
        return "听出主题段多次返回，把结构卡排成回旋路线"
    if mode == "repeat_contrast":
        return "听出重复和对比，把相同段落与变化段落配对"
    return "听出主题段、对比段和再现段，把结构卡排成 ABA"


def _student_action_for_composition_mode(mode: str) -> str:
    if mode == "melody_puzzle_creation":
        return "拖拽唱名卡，拼出有起伏和结束音的旋律短句"
    if mode == "melody_rhythm_puzzle":
        return "把音高和节奏卡成对放入轨道，拼成完整乐句"
    return "拖拽节奏卡填满小节，试听后调整长短、休止和疏密"


def _clamp_int(value: Any, minimum: int, maximum: int, fallback: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = fallback
    return max(minimum, min(maximum, number))


def _clamp_float(value: Any, minimum: float, maximum: float, fallback: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = fallback
    return max(minimum, min(maximum, number))
