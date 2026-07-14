from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.doubao_generation_queue import list_pending_doubao_generation_tasks  # noqa: E402


def main() -> int:
    tasks = list_pending_doubao_generation_tasks()
    out_dir = ROOT / "app" / "static" / "assets" / "primary-asset-packs"
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "doubao-generation-tasks.json"
    md_path = ROOT / "豆包生图素材任务清单.md"

    json_path.write_text(json.dumps({"tasks": tasks}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(tasks), encoding="utf-8")
    print(json_path)
    print(md_path)
    return 0


def render_markdown(tasks: list[dict]) -> str:
    lines = [
        "# 历史外部生图兼容任务清单",
        "",
        "当前正式生图入口是 Codex 内置 `image_gen` / 智能体内置生图能力。本文件名保留为历史兼容，不代表还要使用豆包。",
        "",
        "如果这里出现任务，表示仍有旧 `doubao_generated` 素材包缺 PNG；优先迁移为 `image_gen_generated` 并保存到每条任务的 `save_path`。",
        "",
        "规则：不要文字、不要 logo、不要水印；乐器素材不得用生成图冒充真实照片。",
        "",
    ]
    if not tasks:
        lines.extend(
            [
                "## 当前状态",
                "",
                "当前没有历史外部生图任务。全局情绪图卡与课堂角色已由 `image_gen` 入库；课堂场景图按教案临时生成，不进入固定素材包。",
                "",
            ]
        )
    for task in tasks:
        lines.extend([f"## {task['label']}（{task['asset_pack_id']}）", "", f"- 历史 provider：{task['provider']}", f"- 入库规则：{task['save_policy']}", ""])
        for output in task["outputs"]:
            lines.extend(
                [
                    f"### {output['asset_id']}",
                    "",
                    "历史提示词：",
                    "",
                    "```text",
                    output["doubao_prompt"],
                    "```",
                    "",
                    f"保存路径：`{output['save_path']}`",
                    "",
                ]
            )
    return "\n".join(lines).rstrip() + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
