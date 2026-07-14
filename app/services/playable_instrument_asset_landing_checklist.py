from __future__ import annotations

from pathlib import Path
from typing import Any

from app.services.asset_pack_file_validator import asset_pack_file_report
from app.services.asset_pack_registry import get_asset_pack
from app.services.instrument_audio_registry import get_instrument_audio_pack


CHECKLIST_VERSION = "playable_instrument_asset_landing_checklist_v1"
DEFAULT_CHECKLIST_PATH = Path(__file__).resolve().parents[2] / "升级规划" / "可演奏乐器资产落地清单.md"


def build_playable_instrument_asset_landing_checklist() -> dict[str, Any]:
    generated_pack = get_asset_pack("generated_playable_instrument_pack")
    generated_file_report = asset_pack_file_report(generated_pack)
    sample_pack = get_instrument_audio_pack("primary_playable_instrument_sample_pack")
    missing_skin_ids = [entry["asset_id"] for entry in generated_file_report.get("missing_files", []) if entry.get("asset_id")]

    return {
        "version": CHECKLIST_VERSION,
        "title": "可演奏乐器资产落地清单",
        "summary": "用于把可演奏乐器相关资产拆成已落地、可生图、运行时临时生成和采样补齐四类施工队列；已入 manifest 但文件未生成的乐器不得算已落地。",
        "groups": [
            {
                "status": "已直接落地",
                "items": [
                    _item(
                        "generated_playable_instrument_pack",
                        "已直接落地",
                        "生成式可演奏乐器皮肤包",
                        f"已在 asset_pack_registry 落地；当前本地文件 {generated_file_report['present_count']} 个已存在，{generated_file_report['missing_count']} 个待生成。",
                        "继续补齐新增单件皮肤时，先生成独立 PNG，再补进 assets 列表并重新验收；缺文件条目不得显示成 ready。",
                        "asset_pack_registry / asset_pack_template_registry / 现有静态 PNG",
                    ),
                    _item(
                        "primary_playable_instrument_sample_pack",
                        "已直接落地",
                        "小学可演奏乐器采样演奏包",
                        "已在 instrument_audio_registry 落地，提供可点击演奏的本地 SoundFont 采样；精确实录和近似采样用 sample_fidelity 分开验收。",
                        "后续逐个补齐真正可追溯的精确开源采样，不把近似 SoundFont 或 WebAudio 合成音冒充实体乐器实录。",
                        "instrument_audio_registry / 本地 SoundFont 文件 / open_sample 条目",
                    ),
                ],
            },
            {
                "status": "本地 image2 待生成",
                "items": [
                    *[
                        _item(
                            missing_skin_id,
                            "本地 image2 待生成",
                            "待生成单件可演奏乐器皮肤",
                            "已进入 generated_playable_instrument_pack manifest，但本地 PNG 文件尚未存在。",
                            "使用本地生图器 image2 模型逐个生成独立 PNG，不能复用竖笛、套装图或网络照片。",
                            "asset_pack_registry / image2_generation_queue / generated_playable_instrument_pack / PNG 文件验收",
                        )
                        for missing_skin_id in missing_skin_ids
                    ],
                    _item(
                        "classroom_character_pack",
                        "本地 image2 可扩展",
                        "课堂角色包",
                        "已支持生成 PNG 入库，适合任务引导、反馈角色和投屏课堂陪伴。",
                        "若要扩展角色表情或动作，继续走本地 image2 PNG 产线，不回退到前端硬编码。",
                        "asset_pack_registry / 本地 image2 生成管线 / PNG 验收",
                    ),
                    _item(
                        "music_mood_picture_pack",
                        "本地 image2 可扩展",
                        "音乐情绪图卡包",
                        "已支持生成 PNG 入库，适合听赏导入后的情绪选择与表达。",
                        "新增情绪图时继续使用本地 image2 PNG，保持无文字、无水印、可追溯。",
                        "asset_pack_registry / 本地 image2 生成管线 / PNG 验收",
                    ),
                ],
            },
            {
                "status": "运行时临时生成",
                "items": [
                    _item(
                        "classroom_percussion_kit",
                        "运行时临时生成",
                        "奥尔夫打击乐套装总控",
                        "当前只作为 runtime ensemble controller，不作为单件可演奏乐器皮肤。",
                        "如果需要新的操作界面，只做运行时控制器，不新增单件乐器冒充套装。",
                        "virtual_instrument_registry / runtime controller / 合奏总览",
                    ),
                    _item(
                        "ui_token_pack",
                        "运行时临时生成",
                        "课堂 HUD / 进度 token",
                        "由前端运行时生成，用于课堂反馈、进度展示和大字号投屏。",
                        "保持纯运行时生成，不引入磁盘图片队列。",
                        "asset_pack_registry / runtime_generated / React SVG",
                    ),
                ],
            },
            {
                "status": "需要开源音色/采样补齐",
                "items": [
                    _item(
                        "instrument_audio_registry",
                        "需要开源音色/采样补齐",
                        "可演奏乐器音色注册表",
                        "现有注册表已把可演奏音色分成精确采样、SoundFont 接近音色、近似采样和待补真实采样。",
                        "补齐时优先把 dizi / shaker / tambourine / recorder / melodica 等近似采样逐个替换成精确可追溯 open_sample。",
                        "instrument_audio_registry / open_sample 补录 / source_url / license / attribution",
                    ),
                    _item(
                        "instrument_audio_registry:dizi-erhu-pipa",
                        "需要开源音色/采样补齐",
                        "民族管乐真实采样缺口",
                        "当前仍以 SoundFont fallback 承担课堂可听性，不等于真实采样已齐。",
                        "优先补开源真实录音与许可信息，再回填到 sample pack。",
                        "open source 音频检索 / 采样整理 / 版权记录",
                    ),
                ],
            },
        ],
        "evidence": {
            "generated_playable_instrument_pack": {
                "source": generated_pack["source"],
                "provider": generated_pack.get("provider"),
                "asset_count": len(generated_pack.get("assets", [])),
                "file_status": generated_file_report["status"],
                "present_count": generated_file_report["present_count"],
                "missing_count": generated_file_report["missing_count"],
                "missing_asset_ids": missing_skin_ids,
            },
            "primary_playable_instrument_sample_pack": {
                "sample_status": sample_pack["sample_status"],
                "item_count": len(sample_pack.get("items", [])),
            },
        },
    }


def render_playable_instrument_asset_landing_markdown(checklist: dict[str, Any]) -> str:
    lines = [
        "# 可演奏乐器资产落地清单",
        "",
        str(checklist.get("summary") or ""),
        "",
    ]
    evidence = checklist.get("evidence") if isinstance(checklist.get("evidence"), dict) else {}
    if evidence:
        lines.append("## 现状证据")
        lines.append("")
        lines.append(
            f"- `generated_playable_instrument_pack`: {evidence['generated_playable_instrument_pack']['source']} / "
            f"{evidence['generated_playable_instrument_pack']['provider']} / {evidence['generated_playable_instrument_pack']['asset_count']} manifest assets / "
            f"{evidence['generated_playable_instrument_pack']['file_status']} / "
            f"{evidence['generated_playable_instrument_pack']['present_count']} present / "
            f"{evidence['generated_playable_instrument_pack']['missing_count']} missing"
        )
        lines.append(
            f"- `primary_playable_instrument_sample_pack`: {evidence['primary_playable_instrument_sample_pack']['sample_status']} / "
            f"{evidence['primary_playable_instrument_sample_pack']['item_count']} items"
        )
        lines.append("")

    for group in checklist.get("groups", []):
        lines.extend(
            [
                f"## {group['status']}",
                "",
                "| ID | 状态 | 资产/清单范围 | 校验口径 | 后续施工动作 | 依赖项 |",
                "| --- | --- | --- | --- | --- | --- |",
            ]
        )
        for item in group.get("items", []):
            lines.append(
                "| `{id}` | {status} | {scope} | {validation} | {next_action} | {dependencies} |".format(
                    id=item["id"],
                    status=item["status"],
                    scope=item["asset_scope"],
                    validation=item["validation"],
                    next_action=item["next_action"],
                    dependencies=item["dependencies"],
                )
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_playable_instrument_asset_landing_markdown(path: Path | str = DEFAULT_CHECKLIST_PATH) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    checklist = build_playable_instrument_asset_landing_checklist()
    target.write_text(render_playable_instrument_asset_landing_markdown(checklist), encoding="utf-8")
    return target


def _item(item_id: str, status: str, asset_scope: str, validation: str, next_action: str, dependencies: str) -> dict[str, str]:
    return {
        "id": item_id,
        "status": status,
        "asset_scope": asset_scope,
        "validation": validation,
        "next_action": next_action,
        "dependencies": dependencies,
    }


if __name__ == "__main__":
    write_playable_instrument_asset_landing_markdown()
