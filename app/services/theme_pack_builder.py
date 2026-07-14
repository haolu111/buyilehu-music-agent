from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.services.game_template_registry import get_game_skin


THEME_LIBRARY: dict[str, dict[str, Any]] = {
    "cloud_elevator": {
        "theme_name": "云梯升空",
        "visual_direction": "明亮、轻快、用云端楼层表现音高升降",
        "palette": {"primary": "#3D78A8", "accent": "#F2C85B", "background": "#EEF7FF", "success": "#55A7A0"},
        "avatar": {"name": "云朵探险家", "role": "驾驶云梯找到音高楼层"},
        "skin_family": "trail_world",
        "layout_variant": "trail_map",
        "reward_token": "云门徽章",
        "scene": {
            "setting": "云端升降台",
            "objective_noun": "云梯楼层",
            "progress_noun": "云台",
            "supporting_prop": "云门",
        },
    },
    "bamboo_ladder": {
        "theme_name": "竹节爬梯",
        "visual_direction": "清雅、舒展、带一点中国风",
        "palette": {"primary": "#2F6B4F", "accent": "#D9A441", "background": "#F4EFE2", "success": "#4D9B72"},
        "avatar": {"name": "小竹灵", "role": "沿旋律路线前进"},
        "skin_family": "trail_world",
        "layout_variant": "trail_map",
        "reward_token": "竹叶徽章",
        "scene": {
            "setting": "竹林山径",
            "objective_noun": "旋律小路",
            "progress_noun": "竹节",
            "supporting_prop": "竹叶风铃",
        },
    },
    "mountain_steps": {
        "theme_name": "山路音阶",
        "visual_direction": "明快、向上、适合音高探索",
        "palette": {"primary": "#315C6E", "accent": "#E0A24C", "background": "#F5F1E7", "success": "#4E8E6D"},
        "avatar": {"name": "探路者", "role": "沿音阶继续攀登"},
        "skin_family": "trail_world",
        "layout_variant": "trail_map",
        "reward_token": "登山旗",
        "scene": {
            "setting": "音阶山路",
            "objective_noun": "旋律路线",
            "progress_noun": "山路节点",
            "supporting_prop": "路标",
        },
    },
    "dragon_boat": {
        "theme_name": "龙舟鼓点",
        "visual_direction": "热烈、民俗、节拍感强",
        "palette": {"primary": "#8D3A2E", "accent": "#D9A441", "background": "#F6EBDD", "success": "#4D8A62"},
        "avatar": {"name": "鼓手", "role": "守住节拍带动龙舟"},
        "skin_family": "race_world",
        "layout_variant": "river_race",
        "reward_token": "船桨徽章",
        "scene": {
            "setting": "龙舟赛道",
            "objective_noun": "目标拍位",
            "progress_noun": "河段",
            "supporting_prop": "鼓槌",
        },
    },
    "castle_gate": {
        "theme_name": "充能护盾",
        "visual_direction": "音乐能量圆阵、透明护盾、弱拍怪物和强拍震波",
        "palette": {"primary": "#1F6F72", "accent": "#E0B94B", "background": "#EAF5EF", "success": "#4DAF7C"},
        "avatar": {"name": "护盾充能员", "role": "预判第 1 拍维持护盾"},
        "skin_family": "race_world",
        "layout_variant": "pulsing_shield",
        "reward_token": "护盾徽章",
        "scene": {
            "setting": "音乐能量圆阵",
            "objective_noun": "中央护盾",
            "progress_noun": "小节周期",
            "supporting_prop": "弱拍怪物",
        },
    },
    "sound_casebook": {
        "theme_name": "声音案发现场",
        "visual_direction": "侦探、清晰、聚焦证据",
        "palette": {"primary": "#324A5F", "accent": "#C98B3A", "background": "#F2EFE8", "success": "#4F8B72"},
        "avatar": {"name": "小侦探", "role": "搜集声音证据"},
        "skin_family": "casebook_world",
        "layout_variant": "detective_desk",
        "reward_token": "证据贴纸",
        "scene": {
            "setting": "侦探案桌",
            "objective_noun": "声音线索",
            "progress_noun": "案件",
            "supporting_prop": "放大镜",
        },
    },
    "rhythm_radio": {
        "theme_name": "节奏电波传呼机",
        "visual_direction": "电波、飞船、长短信号清晰",
        "palette": {"primary": "#0F1C24", "accent": "#65F0A9", "background": "#DDF8F0", "success": "#2AA876"},
        "avatar": {"name": "电波传呼员", "role": "复刻长短节奏信号"},
        "skin_family": "target_world",
        "layout_variant": "signal_console",
        "reward_token": "对接徽章",
        "scene": {
            "setting": "飞船电波控制室",
            "objective_noun": "长短信号",
            "progress_noun": "传呼轨道",
            "supporting_prop": "传呼机",
        },
    },
    "treasure_map": {
        "theme_name": "藏宝图寻宝",
        "visual_direction": "冒险、纸纹、路线清晰",
        "palette": {"primary": "#7A4E2D", "accent": "#D9A441", "background": "#F5E8CB", "success": "#4D8A62"},
        "avatar": {"name": "寻宝队", "role": "沿曲式路线找宝藏"},
        "skin_family": "trail_world",
        "layout_variant": "trail_map",
        "reward_token": "结构宝箱",
        "scene": {
            "setting": "曲式藏宝图",
            "objective_noun": "段落路线",
            "progress_noun": "宝藏节点",
            "supporting_prop": "罗盘",
        },
    },
    "constellation_path": {
        "theme_name": "星图航线",
        "visual_direction": "星空、航线、主题回归",
        "palette": {"primary": "#315C77", "accent": "#E8B84E", "background": "#EEF3F7", "success": "#4A8D73"},
        "avatar": {"name": "星图员", "role": "连接曲式星座"},
        "skin_family": "target_world",
        "layout_variant": "target_arena",
        "reward_token": "星门徽章",
        "scene": {
            "setting": "曲式星图",
            "objective_noun": "主题星",
            "progress_noun": "航线",
            "supporting_prop": "星盘",
        },
    },
    "museum_gallery": {
        "theme_name": "音乐展馆",
        "visual_direction": "展览、导览、结构归档",
        "palette": {"primary": "#324A5F", "accent": "#C98B3A", "background": "#F2EFE8", "success": "#4F8B72"},
        "avatar": {"name": "小策展人", "role": "给段落分区"},
        "skin_family": "casebook_world",
        "layout_variant": "detective_desk",
        "reward_token": "策展印章",
        "scene": {
            "setting": "音乐展馆",
            "objective_noun": "段落展厅",
            "progress_noun": "展线",
            "supporting_prop": "展牌",
        },
    },
    "train_route": {
        "theme_name": "音乐列车",
        "visual_direction": "路线、返站、准点推进",
        "palette": {"primary": "#8D3A2E", "accent": "#D9A441", "background": "#F6EBDD", "success": "#4D8A62"},
        "avatar": {"name": "列车长", "role": "按曲式到站"},
        "skin_family": "race_world",
        "layout_variant": "river_race",
        "reward_token": "终点车票",
        "scene": {
            "setting": "音乐铁路",
            "objective_noun": "段落站台",
            "progress_noun": "站点",
            "supporting_prop": "车票",
        },
    },
    "stage_script": {
        "theme_name": "剧场分幕",
        "visual_direction": "舞台、分幕、灯光结构",
        "palette": {"primary": "#7A4E2D", "accent": "#DFAE53", "background": "#F6F0E6", "success": "#4D8A62"},
        "avatar": {"name": "小导演", "role": "排好音乐分幕"},
        "skin_family": "pulse_world",
        "layout_variant": "pulse_stage",
        "reward_token": "终幕灯光",
        "scene": {
            "setting": "曲式剧场",
            "objective_noun": "音乐分幕",
            "progress_noun": "幕次",
            "supporting_prop": "剧本",
        },
    },
    "composition_studio": {
        "theme_name": "音乐创编教室",
        "visual_direction": "明亮卡通、素材架、作品轨道、通关徽章",
        "palette": {"primary": "#2F6F73", "accent": "#E3B34D", "background": "#F2F7F4", "success": "#4FA66A"},
        "avatar": {"name": "小创编师", "role": "拖拽素材卡完成音乐短句"},
        "skin_family": "pulse_world",
        "layout_variant": "pulse_stage",
        "reward_token": "创编徽章",
        "scene": {
            "setting": "音乐创编教室",
            "objective_noun": "作品轨道",
            "progress_noun": "小节灯",
            "supporting_prop": "教师确认印章",
        },
    },
    "rhythm_tile_table": {
        "theme_name": "节奏积木桌",
        "visual_direction": "节奏积木、拍点槽、试听波纹、清楚的时值反馈",
        "palette": {"primary": "#6B5B2E", "accent": "#E4794F", "background": "#F6F3EA", "success": "#4D9B72"},
        "avatar": {"name": "节奏搭建师", "role": "把时值积木拼成完整小节"},
        "skin_family": "pulse_world",
        "layout_variant": "pulse_stage",
        "reward_token": "节奏星章",
        "scene": {
            "setting": "节奏工坊",
            "objective_noun": "节奏轨道",
            "progress_noun": "拍点槽",
            "supporting_prop": "试听波纹",
        },
    },
    "melody_garden": {
        "theme_name": "旋律花园",
        "visual_direction": "清新花园、唱名花卡、旋律藤蔓、结束音花台",
        "palette": {"primary": "#376A55", "accent": "#D86A88", "background": "#F0F7EF", "success": "#58A66B"},
        "avatar": {"name": "旋律园丁", "role": "让唱名花卡连成短旋律"},
        "skin_family": "target_world",
        "layout_variant": "target_arena",
        "reward_token": "旋律花章",
        "scene": {
            "setting": "旋律花园",
            "objective_noun": "旋律藤蔓",
            "progress_noun": "唱名花台",
            "supporting_prop": "花章",
        },
    },
}


FAMILY_DEFAULTS: dict[str, dict[str, Any]] = {
    "trail_world": THEME_LIBRARY["mountain_steps"],
    "race_world": THEME_LIBRARY["dragon_boat"],
    "casebook_world": THEME_LIBRARY["sound_casebook"],
    "pulse_world": THEME_LIBRARY["rhythm_radio"],
    "target_world": {
        "theme_name": "唱名星靶场",
        "visual_direction": "清亮、聚焦、带一点宇宙童话感",
        "palette": {"primary": "#315C77", "accent": "#E8B84E", "background": "#EEF3F7", "success": "#4A8D73"},
        "avatar": {"name": "小射手", "role": "听准唱名再击中靶心"},
        "skin_family": "target_world",
        "layout_variant": "target_arena",
        "reward_token": "星轨徽章",
        "scene": {
            "setting": "唱名靶场",
            "objective_noun": "唱名靶心",
            "progress_noun": "星环",
            "supporting_prop": "准星",
        },
    },
}


def build_theme_pack(
    *,
    instance: dict[str, Any],
    gameplay_blueprint: dict[str, Any],
    proposal_card: dict[str, Any],
) -> dict[str, Any]:
    """Choose a theme shell without changing the gameplay itself."""

    skin = instance.get("skin", {}) if isinstance(instance.get("skin"), dict) else {}
    config = instance.get("config", {}) if isinstance(instance.get("config"), dict) else {}
    variant = config.get("experience_variant") if isinstance(config.get("experience_variant"), dict) else {}
    skin_id = str(skin.get("skin_id") or instance.get("config", {}).get("skin_id") or "")
    base = _resolve_theme(skin_id, gameplay_blueprint, variant)
    return {
        "version": "theme_pack_v1",
        "theme_id": skin_id or base["theme_name"],
        "theme_name": base["theme_name"],
        "visual_direction": base["visual_direction"],
        "palette": dict(base["palette"]),
        "typography": {
            "headline": "Noto Serif SC",
            "body": "Noto Sans SC",
        },
        "avatar": dict(base["avatar"]),
        "skin_family": variant.get("skin_family") or base["skin_family"],
        "layout_variant": variant.get("layout_variant") or base["layout_variant"],
        "reward_token": base["reward_token"],
        "scene": deepcopy(base["scene"]),
        "experience_variant_id": config.get("experience_variant_id", ""),
        "play_mode": config.get("skin_play_mode", ""),
        "playfield_composition": config.get("playfield_composition", ""),
        "scene_goal": config.get("scene_goal", ""),
        "main_object": config.get("main_object", ""),
        "interaction_feedback": config.get("interaction_feedback", ""),
        "failure_feedback": config.get("failure_feedback", ""),
        "reward_loop": config.get("reward_loop", ""),
        "motion": {
            "entry": "轻缓浮现",
            "success": _success_motion(gameplay_blueprint),
            "failure": "轻微停顿，不做惩罚性抖动",
        },
        "sound_design": {
            "ui_click": "soft_tick",
            "success": "warm_chime",
            "failure": "gentle_hint",
        },
        "layout_style": "playfield_first",
        "source_skin_label": skin.get("label") or proposal_card.get("skin_label") or "",
    }


def _resolve_theme(skin_id: str, blueprint: dict[str, Any], variant: dict[str, Any] | None = None) -> dict[str, Any]:
    if skin_id in THEME_LIBRARY:
        base = deepcopy(THEME_LIBRARY[skin_id])
        _apply_variant_theme(base, variant or {})
        return base
    family = _fallback_family(blueprint)
    base = deepcopy(FAMILY_DEFAULTS[family])
    registered_skin = get_game_skin(skin_id) if skin_id else None
    if registered_skin:
        base["theme_name"] = registered_skin.get("label") or base["theme_name"]
        base["visual_direction"] = registered_skin.get("aesthetic") or base["visual_direction"]
    _apply_variant_theme(base, variant or {})
    return base


def _apply_variant_theme(base: dict[str, Any], variant: dict[str, Any]) -> None:
    if not variant:
        return
    base["skin_family"] = variant.get("skin_family") or base.get("skin_family")
    base["layout_variant"] = variant.get("layout_variant") or base.get("layout_variant")
    scene = base.get("scene") if isinstance(base.get("scene"), dict) else {}
    scene["objective_noun"] = scene.get("objective_noun") or variant.get("main_object") or "游戏目标"
    scene["progress_noun"] = variant.get("play_mode") or scene.get("progress_noun") or "进度"
    scene["supporting_prop"] = scene.get("supporting_prop") or variant.get("main_object") or "音乐道具"
    base["scene"] = scene


def _fallback_theme(blueprint: dict[str, Any]) -> dict[str, Any]:
    return FAMILY_DEFAULTS[_fallback_family(blueprint)]


def _fallback_family(blueprint: dict[str, Any]) -> str:
    operation_type = str(blueprint.get("operation_type") or "")
    if "timbre" in operation_type:
        return "casebook_world"
    if "beat" in operation_type:
        return "race_world"
    if "rhythm" in operation_type:
        return "pulse_world"
    if "solfege" in operation_type or "target" in operation_type:
        return "target_world"
    return "trail_world"


def _success_motion(blueprint: dict[str, Any]) -> str:
    if blueprint.get("operation_type") == "melody_path_draw":
        return "路线点亮，角色沿路线前进"
    if "beat" in str(blueprint.get("operation_type") or ""):
        return "护盾震波推开弱拍怪物，充能徽章点亮"
    return "正确元素点亮，并给出柔和奖励反馈"
