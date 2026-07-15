# 生成另一套缺失图片、SVG 素材的任务队列
from __future__ import annotations

from pathlib import Path
from typing import Any

from app.services.assets.asset_pack_file_validator import asset_pack_file_report
from app.services.assets.asset_pack_registry import IMAGE2_URL, list_asset_packs


IMAGE2_GENERATION_QUEUE_VERSION = "image2_generation_queue_v1"


def list_pending_image2_generation_tasks(packs: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Return concrete image2 generation tasks for packs with missing PNG/SVG outputs."""
    source_packs = packs if packs is not None else list_asset_packs()
    tasks: list[dict[str, Any]] = []
    for pack in source_packs:
        if pack.get("source") != "image2":
            continue
        report = asset_pack_file_report(pack)
        if report["status"] != "pending_image2_generation":
            continue
        tasks.append(
            {
                "version": IMAGE2_GENERATION_QUEUE_VERSION,
                "asset_pack_id": pack["asset_pack_id"],
                "label": pack["label"],
                "status": "pending_generation",
                "image2_url": IMAGE2_URL,
                "image2_prompt": pack["image2_prompt"],
                "save_policy": "生成后必须保存到 workspace 中的 listed save_path，不得只停留在 image2 网站或临时目录。",
                "outputs": [_output_entry(entry) for entry in report["missing_files"]],
            }
        )
    return tasks


def _output_entry(entry: dict[str, str]) -> dict[str, str]:
    path = Path(entry["path"])
    return {
        "kind": entry["kind"],
        "asset_id": entry["asset_id"],
        "file": entry["file"],
        "save_path": str(path),
        "suggested_prompt_suffix": _prompt_suffix(entry["asset_id"]),
        "asset_image2_prompt": _asset_image2_prompt(entry),
    }


def _asset_image2_prompt(entry: dict[str, str]) -> str:
    asset_id = str(entry.get("asset_id") or "")
    labels = {
        "dizi_playable_board": "小学音乐课堂笛子可演奏皮肤，横吹竹笛独立演奏板，清晰孔位和竹质纹理，适合触摸试听，不含文字、logo、水印；不能复用竖笛或长笛图片。",
        "flute_playable_board": "小学音乐课堂长笛可演奏皮肤，西洋长笛独立演奏板，银色金属质感和按键清晰，适合触摸试听，不含文字、logo、水印；不能复用竖笛或笛子图片。",
    }
    primary_request = labels.get(asset_id, "")
    if not primary_request:
        return ""
    asset_type = "single playable instrument skin for a primary school music classroom H5 activity"
    composition = "exactly one instrument or one explicit single performance board, centered, large, isolated, no contact sheet, no collage, no multiple tiles, no other instruments."
    return (
        "Use case: stylized-concept\n"
        f"Asset type: {asset_type}\n"
        f"Primary request: {primary_request}\n"
        f"Composition: {composition}\n"
        "Style: bright, clean, child-friendly, realistic classroom illustration asset, crisp edges, generous whitespace, suitable for projection and later click-zone mapping.\n"
        "Constraints: no text, no logo, no watermark, no complex background, no malformed instrument parts.\n"
    )


def _prompt_suffix(asset_id: str) -> str:
    labels = {
        "cheerful": "单张：欢快情绪图卡，明亮、跳跃、适合小学低段听赏初听后选择。",
        "beautiful": "单张：优美情绪图卡，流畅线条、柔和、适合表达旋律优美。",
        "lively": "单张：活泼情绪图卡，轻快动感、适合表达速度较快。",
        "quiet": "单张：安静情绪图卡，留白、柔和、适合表达力度较弱或速度舒缓。",
        "solemn": "单张：庄严情绪图卡，稳定、厚重、适合表达力度较强和进行感。",
        "mysterious": "单张：神秘情绪图卡，含蓄、探索感、适合表达特殊音色或不确定感。",
        "music_classroom": "单张：小学音乐教室投屏背景，明亮但不干扰操作组件。",
        "small_stage": "单张：小舞台投屏背景，适合小组展示和歌唱表演。",
        "forest_music_path": "单张：森林音乐路径背景，适合节奏行走或旋律路线活动。",
        "starry_music_sky": "单张：星空音乐背景，适合安静听赏和音高想象。",
        "music_map": "单张：音乐地图背景，适合曲式路线或寻宝活动。",
    }
    return labels.get(asset_id, "按素材包 image2_prompt 生成对应预览或素材图。")
