from __future__ import annotations

import json
import struct
from pathlib import Path
from typing import Any

from app.services.assets.doubao_generation_queue import list_pending_doubao_generation_tasks


DOUBAO_ASSET_PACK_VERIFICATION_VERSION = "doubao_asset_pack_verification_v1"
TASKS_PATH = Path(__file__).resolve().parents[2] / "static" / "assets" / "primary-asset-packs" / "doubao-generation-tasks.json"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def verify_doubao_asset_pack_outputs(tasks_path: Path | None = None) -> dict[str, Any]:
    tasks_payload = _load_tasks(tasks_path) if tasks_path else _live_tasks_payload()
    pack_reports = [_verify_task(task) for task in tasks_payload.get("tasks", [])]
    output_reports = [output for pack in pack_reports for output in pack["outputs"]]
    ready_count = sum(1 for output in output_reports if output["status"] == "ready")
    missing_count = sum(1 for output in output_reports if output["status"] == "missing")
    invalid_count = sum(1 for output in output_reports if output["status"] == "invalid")
    return {
        "version": DOUBAO_ASSET_PACK_VERIFICATION_VERSION,
        "status": "ready" if ready_count == len(output_reports) else "pending_generation",
        "ready_count": ready_count,
        "missing_count": missing_count,
        "invalid_count": invalid_count,
        "packs": pack_reports,
    }


def read_png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as file:
        header = file.read(24)
    if len(header) < 24 or not header.startswith(PNG_SIGNATURE) or header[12:16] != b"IHDR":
        raise ValueError(f"not a PNG file: {path}")
    width, height = struct.unpack(">II", header[16:24])
    if width <= 0 or height <= 0:
        raise ValueError(f"invalid PNG dimensions: {path}")
    return width, height


def _load_tasks(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"tasks": []}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {"tasks": []}


def _live_tasks_payload() -> dict[str, Any]:
    return {"tasks": list_pending_doubao_generation_tasks()}


def _verify_task(task: dict[str, Any]) -> dict[str, Any]:
    outputs = [_verify_output(task, output) for output in task.get("outputs", [])]
    ready_count = sum(1 for output in outputs if output["status"] == "ready")
    return {
        "asset_pack_id": str(task.get("asset_pack_id") or ""),
        "label": str(task.get("label") or ""),
        "provider": str(task.get("provider") or ""),
        "status": "ready" if outputs and ready_count == len(outputs) else "pending_generation",
        "ready_count": ready_count,
        "total_count": len(outputs),
        "outputs": outputs,
    }


def _verify_output(task: dict[str, Any], output: dict[str, Any]) -> dict[str, Any]:
    save_path = Path(str(output.get("save_path") or ""))
    base = {
        "asset_pack_id": str(task.get("asset_pack_id") or ""),
        "asset_id": str(output.get("asset_id") or ""),
        "kind": str(output.get("kind") or ""),
        "save_path": str(save_path),
    }
    if not save_path.exists():
        return {**base, "status": "missing", "reason": "file_not_found"}
    try:
        width, height = read_png_dimensions(save_path)
    except ValueError as exc:
        return {**base, "status": "invalid", "reason": str(exc)}
    ratio_ok = _ratio_ok(str(task.get("asset_pack_id") or ""), width, height)
    if not ratio_ok:
        return {**base, "status": "invalid", "reason": "unexpected_png_ratio", "width": width, "height": height}
    return {**base, "status": "ready", "width": width, "height": height}


def _ratio_ok(asset_pack_id: str, width: int, height: int) -> bool:
    if asset_pack_id in {"music_mood_picture_pack", "classroom_character_pack"}:
        return abs(width - height) <= max(2, int(max(width, height) * 0.02))
    if asset_pack_id == "classroom_stage_background_pack":
        return abs((width / height) - (16 / 9)) <= 0.06
    return True
