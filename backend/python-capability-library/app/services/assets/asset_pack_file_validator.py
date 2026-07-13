# 检查素材清单中登记的文件是否真的存在
from __future__ import annotations

from pathlib import Path
from typing import Any


STATIC_ASSET_URL_PREFIX = "/static/assets/"
STATIC_ASSET_ROOT = Path(__file__).resolve().parents[2] / "static" / "assets"


def resolve_static_asset_url(url: str) -> Path:
    value = str(url or "").strip()
    if not value.startswith(STATIC_ASSET_URL_PREFIX):
        raise ValueError(f"asset URL must start with {STATIC_ASSET_URL_PREFIX}: {value}")
    relative = value.removeprefix(STATIC_ASSET_URL_PREFIX)
    return STATIC_ASSET_ROOT / relative


def asset_pack_file_report(pack: dict[str, Any]) -> dict[str, Any]:
    pack_id = str(pack.get("asset_pack_id") or "")
    entries = _expected_file_entries(pack)
    missing = [entry for entry in entries if not entry["path"].exists()]
    present = [entry for entry in entries if entry["path"].exists()]
    source = str(pack.get("source") or "")
    blocking = source == "project_generated"
    if source == "doubao_generated":
        pending_status = "pending_doubao_generation"
    elif "image2" in source:
        pending_status = "pending_image2_generation"
    else:
        pending_status = "pending_asset_files"
    return {
        "asset_pack_id": pack_id,
        "source": source,
        "status": "ready" if not missing else ("missing_files" if blocking else pending_status),
        "blocking": bool(missing and blocking),
        "present_count": len(present),
        "missing_count": len(missing),
        "present_files": [_public_file_entry(entry) for entry in present],
        "missing_files": [_public_file_entry(entry) for entry in missing],
    }


def list_asset_pack_file_reports(packs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [asset_pack_file_report(pack) for pack in packs]


def _expected_file_entries(pack: dict[str, Any]) -> list[dict[str, Any]]:
    if str(pack.get("source") or "") in {"runtime_generated", "webaudio_synthesis", "soundfont_fallback", "lesson_runtime_generated"}:
        return []
    pack_id = str(pack.get("asset_pack_id") or "")
    entries: list[dict[str, Any]] = []
    preview = str(pack.get("preview") or "").strip()
    if preview:
        entries.append({"kind": "preview", "file": preview, "path": resolve_static_asset_url(preview)})
    for asset in pack.get("assets", []):
        file_name = str(asset.get("file") or "").strip()
        if not file_name:
            continue
        url = f"{STATIC_ASSET_URL_PREFIX}primary-asset-packs/{pack_id}/{file_name}"
        entries.append({"kind": "asset", "asset_id": asset.get("id", ""), "file": url, "path": resolve_static_asset_url(url)})
    return entries


def _public_file_entry(entry: dict[str, Any]) -> dict[str, str]:
    return {
        "kind": str(entry.get("kind") or ""),
        "asset_id": str(entry.get("asset_id") or ""),
        "file": str(entry.get("file") or ""),
        "path": str(entry.get("path") or ""),
    }
