from __future__ import annotations

from pathlib import Path
from typing import Any

from app.services.assets.asset_pack_file_validator import asset_pack_file_report
from app.services.assets.asset_pack_registry import list_asset_packs


DOUBAO_GENERATION_QUEUE_VERSION = "doubao_generation_queue_v1"
DOUBAO_PROVIDER_LABEL = "豆包生图"


def list_pending_doubao_generation_tasks(packs: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Return historical external-generation compatibility tasks for missing PNG packs."""
    source_packs = packs if packs is not None else list_asset_packs()
    tasks: list[dict[str, Any]] = []
    for pack in source_packs:
        if pack.get("source") != "doubao_generated":
            continue
        report = asset_pack_file_report(pack)
        if report["status"] != "pending_doubao_generation":
            continue
        tasks.append(
            {
                "version": DOUBAO_GENERATION_QUEUE_VERSION,
                "provider": DOUBAO_PROVIDER_LABEL,
                "asset_pack_id": pack["asset_pack_id"],
                "label": pack["label"],
                "status": "pending_generation",
                "source_replacement": "历史兼容队列；当前正式生图入口应迁移为 image_gen_generated",
                "save_policy": "优先用 image_gen 生成 PNG 并保存到 listed save_path；未保存到 workspace 前不得标记已入库。",
                "outputs": [_output_entry(pack["asset_pack_id"], entry) for entry in report["missing_files"]],
            }
        )
    return tasks


def _output_entry(pack_id: str, entry: dict[str, str]) -> dict[str, str]:
    path = Path(entry["path"])
    asset_id = entry.get("asset_id") or _preview_asset_id(pack_id)
    return {
        "kind": entry["kind"],
        "asset_id": asset_id,
        "file": entry["file"],
        "save_path": str(path),
        "doubao_prompt": _doubao_prompt(pack_id, asset_id),
        "postprocess": "下载后保持 PNG；如果文件名不同，重命名为 save_path 的文件名；不要压缩到模糊。",
    }


def _preview_asset_id(pack_id: str) -> str:
    if pack_id == "music_mood_picture_pack":
        return "preview"
    if pack_id == "classroom_stage_background_pack":
        return "preview"
    return "preview"


def _doubao_prompt(pack_id: str, asset_id: str) -> str:
    if pack_id == "music_mood_picture_pack":
        return _mood_prompt(asset_id)
    if pack_id == "classroom_stage_background_pack":
        return _background_prompt(asset_id)
    if pack_id == "classroom_character_pack":
        return _character_prompt(asset_id)
    return (
        "生成小学音乐课堂可用的图片素材，明亮清晰，儿童友好，无文字、无logo、无水印。"
        "这是课堂插图，不是真实乐器照片。"
    )


def _mood_prompt(asset_id: str) -> str:
    labels = {
        "preview": "六宫格音乐情绪图卡合集，包含欢快、优美、活泼、安静、庄严、神秘六种情绪",
        "cheerful": "欢快音乐情绪图卡，明亮、跳跃、速度较快的感觉",
        "beautiful": "优美音乐情绪图卡，柔和、流畅、旋律线条舒展的感觉",
        "lively": "活泼音乐情绪图卡，轻快、有动感、适合小学低段听赏选择",
        "quiet": "安静音乐情绪图卡，留白、柔和、力度较弱或速度舒缓的感觉",
        "solemn": "庄严音乐情绪图卡，稳定、厚重、有进行感和较强力度的感觉",
        "mysterious": "神秘音乐情绪图卡，含蓄、探索感、适合表达特殊音色或不确定感",
    }
    target = labels.get(asset_id, labels["preview"])
    return (
        f"请生成一张小学音乐课堂听赏活动使用的{target}。"
        "风格：儿童友好、明亮干净、主体明确、适合投屏。"
        "教学用途：学生先听音乐，再选择情绪图卡，并说明速度、力度、旋律或音色依据。"
        "画面要求：不要文字、不要logo、不要水印、不要五线谱文字、不要真实乐器伪造、不要人物特写。"
        "比例：正方形，PNG，边缘清晰，适合做H5图卡。"
    )


def _background_prompt(asset_id: str) -> str:
    labels = {
        "preview": "小学音乐课堂投屏背景合集预览，包含音乐教室、小舞台、森林音乐路径、星空音乐天空、音乐地图",
        "music_classroom": "小学音乐教室投屏背景，明亮但不干扰操作组件，中间留出活动区域",
        "small_stage": "小舞台投屏背景，适合歌唱表演和小组展示，中间留空",
        "forest_music_path": "森林音乐路径投屏背景，适合节奏行走、强弱拍律动和旋律路线活动",
        "starry_music_sky": "星空音乐天空投屏背景，适合安静听赏、音高想象和乐句学唱",
        "music_map": "音乐地图投屏背景，适合曲式寻宝、主题再现和段落路线活动",
    }
    target = labels.get(asset_id, labels["preview"])
    return (
        f"请生成一张{target}。"
        "风格：儿童友好、明亮干净、层次清楚，适合小学音乐课堂大屏。"
        "教学用途：作为H5音乐活动背景，前景会叠加节奏卡、唱名卡、按钮和学生任务区。"
        "画面要求：中间留出干净操作区域；不要文字、不要logo、不要水印、不要具体真实乐器特写、不要人物特写。"
        "比例：16:9，PNG，背景不能抢走学生对音乐任务的注意力。"
    )


def _character_prompt(asset_id: str) -> str:
    labels = {
        "preview": "小学音乐课堂角色合集预览，包含音乐小助手、节奏队长、音色侦探三个角色",
        "music_helper": "音乐小助手角色，负责提示先听音乐、看任务和举手表达音乐依据",
        "rhythm_captain": "节奏队长角色，负责提示稳定拍、强弱拍和节奏接龙",
        "timbre_detective": "音色侦探角色，负责提示先听音色、再选择乐器、说出听觉证据",
    }
    target = labels.get(asset_id, labels["preview"])
    return (
        f"请生成一张{target}。"
        "风格：儿童友好、明亮干净、主体明确、适合小学音乐课堂 H5 任务引导。"
        "教学用途：作为课堂活动中的任务引导和反馈角色，只帮助学生理解音乐任务，不替代音乐材料。"
        "画面要求：不要文字、不要logo、不要水印、不要真实乐器特写、不要人物照片感、不要危险动作。"
        "真实性要求：这是生成角色插图，不是真实乐器照片，也不能伪装成真实乐器照片。"
        "比例：正方形，PNG，边缘清晰，适合做角色卡或反馈角色。"
    )
