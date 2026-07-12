from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from app.services.assets.asset_pack_file_validator import STATIC_ASSET_ROOT, STATIC_ASSET_URL_PREFIX, resolve_static_asset_url


CORE_TEMPLATE_GAME_ASSET_PACKS: dict[str, dict[str, str]] = {
    "beat_guardian_core": {"pack_id": "节拍守卫", "label": "节拍守卫模板游戏素材包"},
    "rhythm_echo_core": {"pack_id": "节奏复刻", "label": "节奏复刻模板游戏素材包"},
    "solfege_target_core": {"pack_id": "唱名打靶", "label": "唱名打靶模板游戏素材包"},
    "timbre_detective_core": {"pack_id": "音色侦探", "label": "音色侦探模板游戏素材包"},
    "form_treasure_core": {"pack_id": "曲式寻宝", "label": "曲式寻宝模板游戏素材包"},
    "composition_puzzle_core": {"pack_id": "composition-puzzle", "label": "拼图创编工坊模板游戏素材包"},
}

RHYTHM_FAMILY_ASSET_VARIANTS: dict[str, str] = {
    "echo_replay": "节奏复刻家族变体素材包",
    "beat_guard": "节拍守卫家族变体素材包",
    "race_timing": "节拍竞速家族变体素材包",
    "pattern_builder": "节奏工坊家族变体素材包",
}

PITCH_LADDER_ASSET_VARIANTS: dict[str, dict[str, str]] = {
    "mountain": {
        "label": "音高爬梯山路素材包",
        "background": "backgrounds/mountain-pitch-path-bg.png",
        "hero_seed": "characters/pitch-explorer-seed.png",
        "hero_poses": "characters/pitch-explorer-poses.png",
        "hero_action_strip": "characters/pitch-explorer-action-strip.png",
        "props_sheet": "props/mountain-props.png",
    },
    "cloud": {
        "label": "音高爬梯云梯素材包",
        "background": "backgrounds/cloud-elevator-bg.png",
        "hero_seed": "characters/cloud-explorer-poses-transparent.png",
        "hero_poses": "characters/cloud-explorer-poses-transparent.png",
        "hero_action_strip": "characters/cloud-explorer-action-strip.png",
        "props_sheet": "props/cloud-elevator-props.png",
    },
    "bamboo": {
        "label": "音高爬梯竹节素材包",
        "background": "backgrounds/bamboo-ladder-bg.png",
        "hero_seed": "characters/bamboo-climber-poses-transparent.png",
        "hero_poses": "characters/bamboo-climber-poses-transparent.png",
        "hero_action_strip": "characters/bamboo-climber-action-strip.png",
        "props_sheet": "props/bamboo-ladder-props.png",
    },
}


def list_template_game_asset_packs() -> list[dict[str, Any]]:
    packs: list[dict[str, Any]] = []
    packs.extend(_core_template_pack(template_id, spec) for template_id, spec in CORE_TEMPLATE_GAME_ASSET_PACKS.items())
    packs.extend(_rhythm_family_pack(variant_id, label) for variant_id, label in RHYTHM_FAMILY_ASSET_VARIANTS.items())
    packs.extend(_pitch_ladder_pack(variant_id, spec) for variant_id, spec in PITCH_LADDER_ASSET_VARIANTS.items())
    return [validate_template_game_asset_pack(pack) for pack in packs]


def get_template_game_asset_pack(pack_id: str) -> dict[str, Any]:
    for pack in list_template_game_asset_packs():
        if pack["asset_pack_id"] == pack_id:
            return pack
    raise ValueError(f"unknown template game asset pack: {pack_id}")


def validate_template_game_asset_pack(pack: dict[str, Any]) -> dict[str, Any]:
    required = ("version", "asset_pack_id", "label", "scope", "source", "license", "assets", "music_usage")
    missing = [field for field in required if not pack.get(field)]
    if missing:
        raise ValueError(f"template game asset pack missing fields: {', '.join(missing)}")
    if pack["version"] != "template_game_asset_pack_v1":
        raise ValueError("template game asset pack version must be template_game_asset_pack_v1")
    for asset in pack["assets"]:
        if not isinstance(asset, dict):
            raise ValueError("template game asset entry must be a dict")
        for field in ("id", "file", "usage", "music_element", "student_action"):
            if not asset.get(field):
                raise ValueError(f"template game asset entry missing field: {field}")
        if not str(asset["file"]).startswith(STATIC_ASSET_URL_PREFIX):
            raise ValueError("template game asset file must be a /static/assets/ URL")
    return deepcopy(pack)


def template_game_asset_file_report(pack: dict[str, Any]) -> dict[str, Any]:
    entries = _expected_entries(pack)
    present = [entry for entry in entries if entry["path"].exists()]
    missing = [entry for entry in entries if not entry["path"].exists()]
    return {
        "asset_pack_id": pack["asset_pack_id"],
        "scope": pack["scope"],
        "status": "ready" if not missing else "missing_files",
        "blocking": bool(missing),
        "present_count": len(present),
        "missing_count": len(missing),
        "present_files": [_public_entry(entry) for entry in present],
        "missing_files": [_public_entry(entry) for entry in missing],
    }


def list_template_game_asset_file_reports(packs: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    source = packs if packs is not None else list_template_game_asset_packs()
    return [template_game_asset_file_report(pack) for pack in source]


def evaluate_template_game_asset_library() -> dict[str, Any]:
    packs = list_template_game_asset_packs()
    reports = list_template_game_asset_file_reports(packs)
    return {
        "version": "template_game_asset_library_report_v1",
        "status": "ready" if all(report["status"] == "ready" for report in reports) else "missing_files",
        "asset_pack_count": len(packs),
        "present_file_count": sum(report["present_count"] for report in reports),
        "missing_file_count": sum(report["missing_count"] for report in reports),
        "reports": reports,
    }


def _core_template_pack(template_id: str, spec: dict[str, str]) -> dict[str, Any]:
    pack_id = spec["pack_id"]
    root = f"{STATIC_ASSET_URL_PREFIX}game-packs/{pack_id}"
    extracted = f"{root}/extracted"
    assets = [
        _asset("background", f"{root}/background.png", "game_background", "课堂情境", "listen"),
        _asset("character_pose_sheet", f"{root}/character-poses.png", "source_pose_sheet", "反馈角色", "perform"),
        _asset("props_sheet", f"{root}/props-sheet.png", "source_props_sheet", "音乐任务道具", "interact"),
        _asset("ui_rewards_sheet", f"{root}/ui-rewards.png", "source_ui_reward_sheet", "音乐表现反馈", "revise"),
        _asset("pose_idle", f"{extracted}/pose-01-idle.png", "character_pose", "任务准备", "listen"),
        _asset("pose_action", f"{extracted}/pose-02-action.png", "character_pose", "音乐操作", "perform"),
        _asset("pose_miss", f"{extracted}/pose-03-miss.png", "character_pose", "修正反馈", "revise"),
        _asset("pose_win", f"{extracted}/pose-04-win.png", "character_pose", "完成反馈", "assess"),
    ]
    assets.extend(
        _asset(f"prop_{index:02d}", f"{extracted}/prop-{index:02d}.png", "extracted_prop", "音乐任务道具", "interact")
        for index in range(1, 13)
    )
    assets.extend(
        _asset(f"ui_{index:02d}", f"{extracted}/ui-{index:02d}.png", "extracted_reward_ui", "音乐表现反馈", "revise")
        for index in range(1, 13)
    )
    return _pack(
        asset_pack_id=pack_id,
        label=spec["label"],
        scope="core_template_game",
        assets=assets,
        template_id=template_id,
        music_usage=[
            "背景服务课堂情境，不替代听音乐。",
            "角色、道具和奖励图必须绑定听辨、表现、修正或说明证据。",
        ],
    )


def _rhythm_family_pack(variant_id: str, label: str) -> dict[str, Any]:
    root = f"{STATIC_ASSET_URL_PREFIX}game-packs/rhythm-family/{variant_id}"
    return _pack(
        asset_pack_id=f"rhythm-family/{variant_id}",
        label=label,
        scope="rhythm_family_variant",
        assets=[
            _asset("background", f"{root}/background.png", "game_background", "节奏情境", "listen"),
            _asset("hero_poses", f"{root}/hero-poses.png", "character_pose_sheet", "节奏表现", "tap"),
            _asset("props", f"{root}/props.png", "props_sheet", "节奏任务道具", "perform"),
            _asset("ui_rewards", f"{root}/ui-rewards.png", "ui_reward_sheet", "节奏反馈", "revise"),
        ],
        variant_id=variant_id,
        music_usage=["节奏家族变体必须服务稳拍、复刻、竞速或节奏创编，不作为纯装饰皮肤。"],
    )


def _pitch_ladder_pack(variant_id: str, spec: dict[str, str]) -> dict[str, Any]:
    root = f"{STATIC_ASSET_URL_PREFIX}game-packs/pitch-ladder/{variant_id}"
    return _pack(
        asset_pack_id=f"pitch-ladder/{variant_id}",
        label=spec["label"],
        scope="pitch_ladder_variant",
        assets=[
            _asset("background", f"{root}/{spec['background']}", "game_background", "音高路线", "listen"),
            _asset("hero_seed", f"{root}/{spec['hero_seed']}", "character_seed", "音高路线", "choose"),
            _asset("hero_poses", f"{root}/{spec['hero_poses']}", "character_pose_sheet", "音高行动", "choose"),
            _asset("hero_action_strip", f"{root}/{spec['hero_action_strip']}", "character_action_strip", "音高行动", "perform"),
            _asset("props_sheet", f"{root}/{spec['props_sheet']}", "props_sheet", "音高路线道具", "sing"),
        ],
        variant_id=variant_id,
        music_usage=["音高爬梯素材必须绑定先听、判断高低、路线移动和唱回确认。"],
    )


def _pack(
    *,
    asset_pack_id: str,
    label: str,
    scope: str,
    assets: list[dict[str, str]],
    music_usage: list[str],
    template_id: str = "",
    variant_id: str = "",
) -> dict[str, Any]:
    pack = {
        "version": "template_game_asset_pack_v1",
        "asset_pack_id": asset_pack_id,
        "label": label,
        "scope": scope,
        "source": "local_generated_raster_assets",
        "license": "project_generated",
        "assets": assets,
        "music_usage": music_usage,
    }
    if template_id:
        pack["template_id"] = template_id
    if variant_id:
        pack["variant_id"] = variant_id
    return pack


def _asset(asset_id: str, file: str, usage: str, music_element: str, student_action: str) -> dict[str, str]:
    return {
        "id": asset_id,
        "file": file,
        "usage": usage,
        "music_element": music_element,
        "student_action": student_action,
    }


def _expected_entries(pack: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "asset_id": str(asset["id"]),
            "file": str(asset["file"]),
            "path": resolve_static_asset_url(str(asset["file"])),
        }
        for asset in pack.get("assets", [])
    ]


def _public_entry(entry: dict[str, Any]) -> dict[str, str]:
    path = Path(entry["path"])
    return {
        "asset_id": str(entry["asset_id"]),
        "file": str(entry["file"]),
        "path": str(path),
        "relative_path": str(path.relative_to(STATIC_ASSET_ROOT)),
    }
