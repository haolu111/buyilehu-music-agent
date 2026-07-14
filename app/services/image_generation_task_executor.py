from __future__ import annotations

import base64
import hashlib
import struct
import zlib
from pathlib import Path
from typing import Any, Callable, Tuple, Union


ROOT = Path(__file__).resolve().parents[2]
STATIC_ASSET_ROOT = ROOT / "app" / "static" / "assets"
STATIC_ASSET_URL_PREFIX = "/static/assets/"


AgentImageGenerator = Callable[[dict[str, Any]], Union[bytes, Tuple[bytes, dict[str, Any]]]]


def execute_image_generation_tasks(
    *,
    image_generation_tasks: dict[str, Any],
    generated_asset_registry: dict[str, Any],
    overwrite: bool = False,
    image_gen_executor: AgentImageGenerator | None = None,
    allow_local_fallback: bool = True,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Execute image-generation-tasks.json with the agent's internal image_gen executor.

    This production path is for classroom game assets: scene images, character poses,
    props, rewards, and feedback sheets. It is intentionally separate from the existing
    image2/ChatECNU atmosphere or asset-pack queues. Tests may inject an executor; when
    none is available, the local PNG fallback keeps artifacts runnable but is labeled as
    fallback, not model output.
    """

    tasks = image_generation_tasks.get("tasks") if isinstance(image_generation_tasks.get("tasks"), list) else []
    previous_reused = (
        generated_asset_registry.get("reused_assets")
        if isinstance(generated_asset_registry.get("reused_assets"), list)
        else []
    )
    generator = image_gen_executor
    executor = "agent_internal_image_gen" if generator else "local_generated_fallback"
    generated_assets: list[dict[str, str]] = []
    pending_assets: list[dict[str, str]] = []
    results: list[dict[str, Any]] = []
    remote_count = 0
    fallback_count = 0
    cached_count = 0

    for task in tasks:
        if not isinstance(task, dict):
            continue
        output_path = _safe_output_path(str(task.get("output_path") or ""))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        metadata: dict[str, Any] = {}
        source = "cached_generated_asset"
        status = "cached"
        error = ""
        if output_path.exists() and not overwrite:
            cached_count += 1
        else:
            try:
                if not generator:
                    raise RuntimeError("agent internal image_gen executor is not attached")
                generated = generator(task)
                if isinstance(generated, tuple):
                    image_bytes, metadata = generated
                else:
                    image_bytes = generated
                output_path.write_bytes(image_bytes)
                source = "agent_internal_image_gen"
                status = "generated_by_image_gen"
                remote_count += 1
            except Exception as exc:  # pragma: no cover - provider failures vary by environment.
                error = f"{type(exc).__name__}: {exc}"
                if not allow_local_fallback:
                    status = "blocked"
                    source = "not_generated"
                    pending_assets.append(
                        {
                            "asset_id": str(task.get("asset_id") or output_path.stem),
                            "type": str(task.get("type") or "generated_asset"),
                            "reason": error,
                        }
                    )
                    results.append(_result(task, output_path, status=status, source=source, error=error))
                    continue
                output_path.write_bytes(_placeholder_png_bytes(task))
                source = "local_generated_fallback"
                status = "generated_local_fallback"
                fallback_count += 1

        asset = {
            "asset_id": str(task.get("asset_id") or output_path.stem),
            "type": str(task.get("type") or "generated_asset"),
            "url": _static_url_for(output_path),
            "source": source,
            "runtime_usage": str(task.get("runtime_usage") or ""),
        }
        generated_assets.append(asset)
        results.append(
            _result(
                task,
                output_path,
                status=status,
                source=source,
                error=error,
                metadata=metadata,
            )
        )

    if pending_assets:
        registry_status = "pending_generation"
        report_status = "blocked"
    elif fallback_count:
        registry_status = "ready_with_generated_assets"
        report_status = "ready_with_fallback"
    else:
        registry_status = "ready_with_generated_assets" if generated_assets else generated_asset_registry.get("status", "ready")
        report_status = "ready"

    registry = {
        "version": "generated_asset_registry_v1",
        "template_runtime_candidate": generated_asset_registry.get("template_runtime_candidate", ""),
        "reused_assets": [*previous_reused, *generated_assets],
        "pending_generation_assets": pending_assets,
        "task_count": len(tasks),
        "status": registry_status,
    }
    report = {
        "version": "image_generation_execution_report_v1",
        "status": report_status,
        "executor": executor if not fallback_count else f"{executor}_with_local_fallback",
        "image_gen_executor_attached": bool(generator),
        "provider_boundary": "agent_internal_image_gen_only_not_image2_or_chat_ecnu",
        "task_count": len(tasks),
        "generated_count": len(generated_assets),
        "image_gen_generated_count": remote_count,
        "local_fallback_count": fallback_count,
        "cached_count": cached_count,
        "results": results,
    }
    return registry, report


def execute_image_generation_tasks_locally(
    *,
    image_generation_tasks: dict[str, Any],
    generated_asset_registry: dict[str, Any],
    overwrite: bool = False,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Execute image-generation-tasks.json using deterministic local PNG fallback assets."""

    tasks = image_generation_tasks.get("tasks") if isinstance(image_generation_tasks.get("tasks"), list) else []
    previous_reused = (
        generated_asset_registry.get("reused_assets")
        if isinstance(generated_asset_registry.get("reused_assets"), list)
        else []
    )
    generated_assets: list[dict[str, str]] = []
    results: list[dict[str, Any]] = []
    for task in tasks:
        if not isinstance(task, dict):
            continue
        output_path = _safe_output_path(str(task.get("output_path") or ""))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if output_path.exists() and not overwrite:
            status = "cached"
        else:
            output_path.write_bytes(_placeholder_png_bytes(task))
            status = "generated_local_fallback"
        asset = {
            "asset_id": str(task.get("asset_id") or output_path.stem),
            "type": str(task.get("type") or "generated_asset"),
            "url": _static_url_for(output_path),
            "source": "local_generated_fallback",
            "runtime_usage": str(task.get("runtime_usage") or ""),
        }
        generated_assets.append(asset)
        results.append(
            {
                "asset_id": asset["asset_id"],
                "status": status,
                "path": str(output_path),
                "url": asset["url"],
                "prompt_hash": _hash(str(task.get("prompt") or ""))[:12],
            }
        )

    registry = {
        "version": "generated_asset_registry_v1",
        "template_runtime_candidate": generated_asset_registry.get("template_runtime_candidate", ""),
        "reused_assets": [*previous_reused, *generated_assets],
        "pending_generation_assets": [],
        "task_count": len(tasks),
        "status": "ready_with_generated_assets" if generated_assets else generated_asset_registry.get("status", "ready"),
    }
    report = {
        "version": "image_generation_execution_report_v1",
        "status": "ready" if not tasks or generated_assets else "blocked",
        "executor": "local_generated_fallback",
        "task_count": len(tasks),
        "generated_count": len(generated_assets),
        "results": results,
    }
    return registry, report


def apply_agent_image_gen_outputs(
    *,
    image_generation_tasks: dict[str, Any],
    generated_asset_registry: dict[str, Any],
    outputs: list[dict[str, Any]],
    overwrite: bool = True,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Materialize assets already generated by the agent's internal image_gen capability."""

    tasks = image_generation_tasks.get("tasks") if isinstance(image_generation_tasks.get("tasks"), list) else []
    output_by_asset_id = {
        str(item.get("asset_id") or ""): item for item in outputs if isinstance(item, dict) and str(item.get("asset_id") or "")
    }
    previous_reused = [
        item
        for item in generated_asset_registry.get("reused_assets", [])
        if isinstance(item, dict) and str(item.get("source") or "") not in {"local_generated_fallback", "cached_generated_asset"}
    ] if isinstance(generated_asset_registry.get("reused_assets"), list) else []
    generated_assets: list[dict[str, str]] = []
    pending_assets: list[dict[str, str]] = []
    results: list[dict[str, Any]] = []

    for task in tasks:
        if not isinstance(task, dict):
            continue
        asset_id = str(task.get("asset_id") or "")
        output = output_by_asset_id.get(asset_id)
        output_path = _safe_output_path(str(task.get("output_path") or ""))
        if not output:
            pending_assets.append({"asset_id": asset_id, "type": str(task.get("type") or ""), "reason": "missing_image_gen_output"})
            results.append(_result(task, output_path, status="pending_image_gen_output", source="not_generated"))
            continue
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if output_path.exists() and not overwrite:
            status = "cached"
        else:
            output_path.write_bytes(_image_bytes_from_output(output))
            status = "generated_by_image_gen"
        asset = {
            "asset_id": asset_id or output_path.stem,
            "type": str(task.get("type") or "generated_asset"),
            "url": _static_url_for(output_path),
            "source": "agent_internal_image_gen",
            "runtime_usage": str(task.get("runtime_usage") or ""),
        }
        generated_assets.append(asset)
        results.append(
            _result(
                task,
                output_path,
                status=status,
                source="agent_internal_image_gen",
                metadata={"provider": "agent_internal_image_gen"},
            )
        )

    registry = {
        "version": "generated_asset_registry_v1",
        "template_runtime_candidate": generated_asset_registry.get("template_runtime_candidate", ""),
        "reused_assets": [*previous_reused, *generated_assets],
        "pending_generation_assets": pending_assets,
        "task_count": len(tasks),
        "status": "pending_generation" if pending_assets else "ready_with_generated_assets",
    }
    report = {
        "version": "image_generation_execution_report_v1",
        "status": "blocked" if pending_assets else "ready",
        "executor": "agent_internal_image_gen",
        "image_gen_executor_attached": True,
        "provider_boundary": "agent_internal_image_gen_only_not_image2_or_chat_ecnu",
        "task_count": len(tasks),
        "generated_count": len(generated_assets),
        "image_gen_generated_count": len(generated_assets),
        "local_fallback_count": 0,
        "cached_count": sum(1 for result in results if result.get("status") == "cached"),
        "results": results,
    }
    return registry, report


def build_agent_image_gen_prompt(task: dict[str, Any]) -> str:
    prompt = str(task.get("prompt") or "").strip()
    asset_type = str(task.get("type") or "generated_asset")
    runtime_usage = str(task.get("runtime_usage") or "")
    constraints = [
        "用于小学音乐课堂 H5 游戏。",
        "必须服务当前音乐学习行为，不做纯装饰图。",
        "无文字、无 logo、无水印。",
        "主体清晰，儿童友好，适合投屏和移动端。",
    ]
    if task.get("transparent_background"):
        constraints.append("透明背景 PNG，适合叠加在游戏画面中。")
    return "\n".join(
        [
            prompt or f"生成 {asset_type} 游戏素材。",
            f"Asset type: {asset_type}",
            f"Runtime usage: {runtime_usage}",
            *constraints,
        ]
    )


def _image_bytes_from_output(output: dict[str, Any]) -> bytes:
    raw_bytes = output.get("bytes")
    if isinstance(raw_bytes, bytes):
        return raw_bytes
    b64 = str(output.get("b64_png") or output.get("b64_json") or output.get("data_url") or "")
    if "," in b64 and b64.strip().startswith("data:"):
        b64 = b64.split(",", 1)[1]
    if not b64:
        raise ValueError("image_gen output must include b64_png, b64_json, data_url, or bytes")
    return base64.b64decode(b64)


def _result(
    task: dict[str, Any],
    output_path: Path,
    *,
    status: str,
    source: str,
    error: str = "",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result = {
        "asset_id": str(task.get("asset_id") or output_path.stem),
        "status": status,
        "source": source,
        "path": str(output_path),
        "url": _static_url_for(output_path) if output_path.exists() else "",
        "prompt_hash": _hash(str(task.get("prompt") or ""))[:12],
    }
    if error:
        result["error"] = error
    if metadata:
        result["metadata"] = metadata
    return result


def _safe_output_path(value: str) -> Path:
    if not value:
        raise ValueError("image generation task output_path is required")
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / path
    resolved = path.resolve()
    try:
        resolved.relative_to(STATIC_ASSET_ROOT.resolve())
    except ValueError as exc:
        raise ValueError(f"generated asset must be inside app/static/assets: {value}") from exc
    return resolved


def _static_url_for(path: Path) -> str:
    relative = path.resolve().relative_to(STATIC_ASSET_ROOT.resolve())
    return STATIC_ASSET_URL_PREFIX + relative.as_posix()


def _placeholder_png_bytes(task: dict[str, Any]) -> bytes:
    width, height = _size(str(task.get("size") or "512x512"))
    color = _color(task)
    transparent = bool(task.get("transparent_background"))
    if transparent:
        background = (color[0], color[1], color[2], 0)
    else:
        background = (color[0], color[1], color[2], 255)
    rows = []
    for y in range(height):
        row = bytearray([0])
        for x in range(width):
            edge = x < 8 or y < 8 or x >= width - 8 or y >= height - 8
            if edge:
                pixel = (max(color[0] - 45, 0), max(color[1] - 45, 0), max(color[2] - 45, 0), 255)
            elif (x + y) % 37 == 0:
                pixel = (min(color[0] + 35, 255), min(color[1] + 35, 255), min(color[2] + 35, 255), 220)
            else:
                pixel = background
            row.extend(pixel)
        rows.append(bytes(row))
    raw = b"".join(rows)
    return _png(width, height, raw)


def _size(value: str) -> tuple[int, int]:
    try:
        width_text, height_text = value.lower().split("x", 1)
        width = max(96, min(1280, int(width_text)))
        height = max(96, min(1280, int(height_text)))
        return width, height
    except Exception:
        return 512, 512


def _color(task: dict[str, Any]) -> tuple[int, int, int]:
    digest = hashlib.sha1(
        f"{task.get('asset_id','')}|{task.get('type','')}|{task.get('prompt','')}".encode("utf-8")
    ).digest()
    return 90 + digest[0] % 120, 90 + digest[1] % 120, 90 + digest[2] % 120


def _png(width: int, height: int, raw_rgba_rows: bytes) -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    compressed = zlib.compress(raw_rgba_rows, level=6)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", compressed) + chunk(b"IEND", b"")


def _hash(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()
