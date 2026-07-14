from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import time
import sys
from pathlib import Path
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.image2_generation_queue import list_pending_image2_generation_tasks  # noqa: E402


DEFAULT_BASE_URL = "https://www.codex2api.com"
DEFAULT_MODEL = "gpt-image-2"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate pending image2 asset-pack PNG outputs.")
    parser.add_argument("--packs", nargs="*", help="Only generate these asset_pack_id values.")
    parser.add_argument("--model", default=os.environ.get("IMAGE2_MODEL", DEFAULT_MODEL))
    parser.add_argument("--base-url", default=os.environ.get("IMAGE2_BASE_URL", DEFAULT_BASE_URL))
    parser.add_argument("--api-key-env", default="IMAGE2_API_KEY")
    parser.add_argument("--quality", default=os.environ.get("IMAGE2_QUALITY", "low"))
    parser.add_argument("--size", default=os.environ.get("IMAGE2_SIZE", "1024x1024"))
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--retries", type=int, default=int(os.environ.get("IMAGE2_RETRIES", "3")))
    parser.add_argument("--transport", choices=["httpx", "curl"], default=os.environ.get("IMAGE2_TRANSPORT", "httpx"))
    parser.add_argument("--prompt-mode", choices=["full", "concise"], default=os.environ.get("IMAGE2_PROMPT_MODE", "full"))
    args = parser.parse_args()

    api_key = os.environ.get(args.api_key_env, "").strip()
    if not api_key:
        raise SystemExit(f"{args.api_key_env} is required")

    pack_filter = set(args.packs or [])
    tasks = [
        task
        for task in list_pending_image2_generation_tasks()
        if not pack_filter or task["asset_pack_id"] in pack_filter
    ]
    outputs = [(task, output) for task in tasks for output in task["outputs"]]
    if args.limit:
        outputs = outputs[: args.limit]

    results: list[dict[str, Any]] = []
    for index, (task, output) in enumerate(outputs, start=1):
        save_path = Path(output["save_path"])
        if save_path.exists() and not args.overwrite:
            results.append({"status": "skipped_existing", "path": str(save_path)})
            continue

        prompt = build_prompt(task, output, mode=args.prompt_mode)
        print(f"[{index}/{len(outputs)}] generating {task['asset_pack_id']}::{output['asset_id'] or output['kind']}", flush=True)
        image_bytes, revised_prompt = generate_image(
            base_url=args.base_url,
            api_key=api_key,
            model=args.model,
            prompt=prompt,
            quality=args.quality,
            size=args.size,
            retries=args.retries,
            transport=args.transport,
        )
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_bytes(image_bytes)
        results.append(
            {
                "status": "generated",
                "asset_pack_id": task["asset_pack_id"],
                "asset_id": output["asset_id"],
                "path": str(save_path),
                "bytes": len(image_bytes),
                "revised_prompt": revised_prompt,
            }
        )

    report_path = ROOT / "app" / "static" / "assets" / "primary-asset-packs" / "image2-generation-report.json"
    report_path.write_text(json.dumps({"results": results}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote report: {report_path}")
    return 0


def build_prompt(task: dict[str, Any], output: dict[str, Any], *, mode: str = "full") -> str:
    suffix = output.get("suggested_prompt_suffix") or ""
    asset_id = output.get("asset_id") or output.get("kind") or "preview"
    single_asset_prompt = str(output.get("asset_image2_prompt") or "").strip()
    if single_asset_prompt:
        return single_asset_prompt
    if mode == "concise":
        return concise_prompt(task["asset_pack_id"], asset_id)
    return (
        f"{task['image2_prompt']}\n"
        f"{suffix}\n"
        f"Asset id: {asset_id}\n"
        "Music education requirement: 用于小学音乐课堂投屏活动，必须服务听、唱、拍、奏、动、选、说依据等音乐学习行为。\n"
        "Visual requirement: 明亮清晰，儿童友好，主体明确，不能出现文字、logo、水印、五线谱文字化内容或畸形乐器。\n"
        "Authenticity note: 这是 image2 生成的课堂插图/背景，不得冒充真实乐器照片。"
    )


def concise_prompt(asset_pack_id: str, asset_id: str) -> str:
    mood_labels = {
        "preview": "六宫格小学音乐情绪图卡合集，欢快、优美、活泼、安静、庄严、神秘",
        "cheerful": "小学音乐听赏情绪图卡：欢快，明亮跳跃",
        "beautiful": "小学音乐听赏情绪图卡：优美，柔和流动",
        "lively": "小学音乐听赏情绪图卡：活泼，轻快动感",
        "quiet": "小学音乐听赏情绪图卡：安静，留白柔和",
        "solemn": "小学音乐听赏情绪图卡：庄严，稳定厚重",
        "mysterious": "小学音乐听赏情绪图卡：神秘，含蓄探索感",
    }
    background_labels = {
        "preview": "小学音乐课堂投屏背景合集预览，教室、舞台、森林音乐路径、星空、音乐地图",
        "music_classroom": "小学音乐教室投屏背景，明亮干净，中间留出活动区域",
        "small_stage": "小学音乐小舞台投屏背景，适合歌唱和小组展示",
        "forest_music_path": "森林音乐路径投屏背景，适合节奏行走和旋律路线活动",
        "starry_music_sky": "星空音乐投屏背景，适合安静听赏和音高想象",
        "music_map": "音乐地图投屏背景，适合曲式路线和寻宝活动",
    }
    label = mood_labels.get(asset_id, asset_id) if asset_pack_id == "music_mood_picture_pack" else background_labels.get(asset_id, asset_id)
    return (
        f"{label}。儿童友好插图，明亮清晰，无文字、无logo、无水印、无真实乐器伪造，"
        "适合小学音乐课堂H5活动，主体明确，边缘整洁。"
    )


def generate_image(
    *,
    base_url: str,
    api_key: str,
    model: str,
    prompt: str,
    quality: str,
    size: str,
    retries: int,
    transport: str,
) -> tuple[bytes, str]:
    if transport == "curl":
        return generate_image_with_curl(
            base_url=base_url,
            api_key=api_key,
            model=model,
            prompt=prompt,
            quality=quality,
            size=size,
            retries=retries,
        )

    endpoint = base_url.rstrip("/") + "/v1/images/generations"
    request = {
        "model": model,
        "prompt": prompt,
        "size": size,
        "quality": quality,
        "output_format": "png",
        "n": 1,
        "response_format": "b64_json",
    }
    last_error: Exception | None = None
    for attempt in range(1, max(1, retries) + 1):
        try:
            with httpx.Client(trust_env=False, timeout=float(os.environ.get("IMAGE2_TIMEOUT", "180"))) as client:
                response = client.post(
                    endpoint,
                    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                    json=request,
                )
            response.raise_for_status()
            break
        except (httpx.HTTPError, RuntimeError) as exc:
            last_error = exc
            if attempt >= max(1, retries):
                raise
            time.sleep(min(8, attempt * 2))
    else:
        raise RuntimeError(f"image2 request failed: {last_error}")
    payload = response.json()
    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, list) or not data:
        raise RuntimeError("image2 response missing data")
    first = data[0] if isinstance(data[0], dict) else {}
    revised_prompt = str(first.get("revised_prompt") or "")
    if first.get("b64_json"):
        return base64.b64decode(str(first["b64_json"])), revised_prompt
    if first.get("url"):
        with httpx.Client(trust_env=False, timeout=float(os.environ.get("IMAGE2_DOWNLOAD_TIMEOUT", "90"))) as client:
            image = client.get(str(first["url"]))
            image.raise_for_status()
        return image.content, revised_prompt
    raise RuntimeError("image2 response missing b64_json or url")


def generate_image_with_curl(
    *,
    base_url: str,
    api_key: str,
    model: str,
    prompt: str,
    quality: str,
    size: str,
    retries: int,
) -> tuple[bytes, str]:
    endpoint = base_url.rstrip("/") + "/v1/images/generations"
    request = {
        "model": model,
        "prompt": prompt,
        "size": size,
        "quality": quality,
        "output_format": "png",
        "n": 1,
        "response_format": "b64_json",
    }
    last_error = ""
    for attempt in range(1, max(1, retries) + 1):
        completed = subprocess.run(
            [
                "curl",
                "-sS",
                "--fail-with-body",
                "--max-time",
                os.environ.get("IMAGE2_CURL_MAX_TIME", "240"),
                "-X",
                "POST",
                endpoint,
                "-H",
                f"Authorization: Bearer {api_key}",
                "-H",
                "Content-Type: application/json",
                "-d",
                json.dumps(request, ensure_ascii=False),
            ],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if completed.returncode == 0:
            payload = json.loads(completed.stdout.decode("utf-8"))
            data = payload.get("data") if isinstance(payload, dict) else None
            if not isinstance(data, list) or not data:
                raise RuntimeError("image2 curl response missing data")
            first = data[0] if isinstance(data[0], dict) else {}
            revised_prompt = str(first.get("revised_prompt") or "")
            if first.get("b64_json"):
                return base64.b64decode(str(first["b64_json"])), revised_prompt
            if first.get("url"):
                image = subprocess.run(
                    ["curl", "-sS", "--fail", "--max-time", os.environ.get("IMAGE2_CURL_DOWNLOAD_MAX_TIME", "120"), str(first["url"])],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                return image.stdout, revised_prompt
            raise RuntimeError("image2 curl response missing b64_json or url")
        last_error = completed.stderr.decode("utf-8", errors="replace") or completed.stdout.decode("utf-8", errors="replace")
        if attempt < max(1, retries):
            time.sleep(min(8, attempt * 2))
    raise RuntimeError(f"image2 curl request failed: {last_error}")


if __name__ == "__main__":
    raise SystemExit(main())
