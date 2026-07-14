from __future__ import annotations

from copy import deepcopy
from typing import Any


def build_asset_contract(instance: dict[str, Any], *, scene_bible: str = "") -> dict[str, Any]:
    config = instance.get("config") if isinstance(instance.get("config"), dict) else {}
    template_id = str(instance.get("template_id") or config.get("template_id") or "").strip()
    force_lesson_assets = bool(config.get("lesson_specific_assets_required"))
    assets = [] if force_lesson_assets else _assets_from_manifest(config, template_id=template_id)
    if not assets:
        assets = _generation_assets_for(config, template_id=template_id)
    return {
        "version": "asset_contract_v1",
        "template_id": template_id,
        "status": "ready_with_reused_assets" if all(asset.get("source_url") for asset in assets) else "needs_generation",
        "scene_bible_required_before_generation": True,
        "asset_roots": ["app/static/assets/", "frontend/public/static/assets/"],
        "scene_bible_ref": "scene-bible.md" if scene_bible else "",
        "assets": assets,
    }


def _assets_from_manifest(config: dict[str, Any], *, template_id: str) -> list[dict[str, Any]]:
    manifest = config.get("asset_manifest") if isinstance(config.get("asset_manifest"), dict) else {}
    if not manifest and isinstance(config.get("scene_config"), dict):
        scene_config = config["scene_config"]
        manifest = scene_config.get("asset_manifest") if isinstance(scene_config.get("asset_manifest"), dict) else {}
    if not manifest:
        return []
    assets: list[dict[str, Any]] = []
    background = str(manifest.get("background") or "")
    if background:
        assets.append(
            _reused_asset(
                asset_id="scene_background",
                asset_type="background",
                source_url=background,
                runtime_usage="scene_background",
                size="1280x720",
                transparent_background=False,
                template_id=template_id,
            )
        )
    poses = manifest.get("poses") if isinstance(manifest.get("poses"), dict) else {}
    for pose_state, url in poses.items():
        assets.append(
            _reused_asset(
                asset_id=f"character_pose_{pose_state}",
                asset_type="character_pose",
                source_url=str(url),
                runtime_usage=f"character_{pose_state}",
                size="512x512",
                transparent_background=True,
                template_id=template_id,
            )
        )
    props = manifest.get("props") if isinstance(manifest.get("props"), list) else []
    for index, url in enumerate(props[:4], start=1):
        assets.append(
            _reused_asset(
                asset_id=f"game_prop_{index:02d}",
                asset_type="prop",
                source_url=str(url),
                runtime_usage="music_task_prop",
                size="512x512",
                transparent_background=True,
                template_id=template_id,
            )
        )
    rewards = manifest.get("rewards") if isinstance(manifest.get("rewards"), list) else []
    for index, url in enumerate(rewards[:3], start=1):
        assets.append(
            _reused_asset(
                asset_id=f"reward_feedback_{index:02d}",
                asset_type="reward_feedback",
                source_url=str(url),
                runtime_usage="reward_or_feedback",
                size="512x512",
                transparent_background=True,
                template_id=template_id,
            )
        )
    return assets


def _generation_assets_for(config: dict[str, Any], *, template_id: str) -> list[dict[str, Any]]:
    theme = str(config.get("theme") or config.get("skin_objective") or config.get("music_concept") or "课堂音乐游戏")
    lesson_title = str(config.get("lesson_title") or "")
    role = str(config.get("lesson_role_visual") or config.get("cartoon_role") or "音乐引导角色")
    prop_visual = str(config.get("lesson_prop_visual") or "音乐任务道具")
    scene_context = str(config.get("lesson_scene_context") or "")
    pack_id = str(config.get("lesson_asset_pack_id") or template_id or "original-game")
    pack_root = f"app/static/assets/game-packs/{pack_id}"
    lesson_prefix = f"《{lesson_title}》" if lesson_title else ""
    common_prompt = f"{lesson_prefix}{theme}，小学音乐课堂游戏视觉，儿童友好，明亮清晰，无文字、无logo、无水印"
    return [
        {
            "asset_id": "scene_background",
            "type": "background",
            "runtime_usage": "scene_background",
            "size": "1280x720",
            "transparent_background": False,
            "generation_required": True,
            "output_path": f"{pack_root}/images/background.png",
            "prompt": f"{common_prompt}，{scene_context}，横版16:9，中央留出学生操作区域",
        },
        {
            "asset_id": "character_pose_sheet",
            "type": "character_pose_sheet",
            "runtime_usage": "character_states",
            "size": "1024x1024",
            "transparent_background": True,
            "generation_required": True,
            "output_path": f"{pack_root}/images/character_pose_sheet.png",
            "prompt": f"{role}，idle、listen、action、success、fail、retry 六个姿势，透明背景，{common_prompt}",
        },
        {
            "asset_id": "game_props_sheet",
            "type": "prop_sheet",
            "runtime_usage": "music_task_props",
            "size": "1024x1024",
            "transparent_background": True,
            "generation_required": True,
            "output_path": f"{pack_root}/images/props_sheet.png",
            "prompt": f"{theme} 的{prop_visual}，单体图集合，透明背景，大轮廓，{common_prompt}",
        },
        {
            "asset_id": "reward_feedback_sheet",
            "type": "reward_feedback",
            "runtime_usage": "reward_or_feedback",
            "size": "1024x1024",
            "transparent_background": True,
            "generation_required": True,
            "output_path": f"{pack_root}/images/reward_feedback_sheet.png",
            "prompt": f"{theme} 的奖励、正确、错误、重试反馈图标，透明背景，无文字，{common_prompt}",
        },
    ]


def _reused_asset(
    *,
    asset_id: str,
    asset_type: str,
    source_url: str,
    runtime_usage: str,
    size: str,
    transparent_background: bool,
    template_id: str,
) -> dict[str, Any]:
    return {
        "asset_id": asset_id,
        "type": asset_type,
        "runtime_usage": runtime_usage,
        "size": size,
        "transparent_background": transparent_background,
        "generation_required": False,
        "source": "template_asset_manifest",
        "source_url": source_url,
        "output_path": "",
        "template_id": template_id,
    }
