from __future__ import annotations

import html
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.services.runtime_paths import output_url_for_path


_STRUCTURAL_WORDS = [
    "新增",
    "增加",
    "加一个",
    "添加",
    "删除按钮",
    "拖拽",
    "关卡",
    "音频",
    "播放",
    "试听",
    "上传",
    "逻辑",
    "规则",
    "判定",
    "通关",
    "布局",
    "样式",
    "颜色",
    "动画",
    "功能",
]


def try_lightweight_revision(
    *,
    spec_payload: dict[str, Any],
    revision: str,
    index_path: Path,
    generation_mode: str,
    emit: Any = None,
) -> dict[str, Any] | None:
    """Patch tiny text-only edits without rebuilding spec or invoking OpenCode."""

    patch = _parse_text_patch(revision)
    if not patch:
        return None

    old, new = patch
    content = index_path.read_text(encoding="utf-8")
    updated, count = _replace_visible_text(content, old, new)
    if count <= 0 or updated == content:
        return None

    target_dir = index_path.parent
    _snapshot_version(target_dir)
    index_path.write_text(updated, encoding="utf-8")

    if emit:
        emit(f"已启用轻量修改通道：替换 {count} 处页面文案。", "lightweight-revision", "info")

    execution = _write_lightweight_execution_report(target_dir, old, new, count, generation_mode)
    spec = dict(spec_payload)
    spec["generation_mode"] = "strict" if str(generation_mode).strip().lower() == "strict" else "fast"

    return {
        "page_url": output_url_for_path(index_path),
        "file_path": str(index_path),
        "model": {"provider": "local", "model": "lightweight-patch"},
        "spec": spec,
        "brain": _lightweight_brain_report(revision),
        "execution": execution,
        "opencode": {
            "enabled": False,
            "status": "skipped",
            "reason": "命中轻量文案修改，已跳过 OpenCode。",
            "execution_url": execution.get("report_url", ""),
        },
        "opencode_run": {"enabled": False, "status": "skipped", "reason": "lightweight_text_patch"},
        "revision": revision,
        "incremental": True,
        "lightweight": True,
    }


def _parse_text_patch(revision: str) -> tuple[str, str] | None:
    text = revision.strip()
    if not text or len(text) > 180:
        return None
    if any(word in text for word in _STRUCTURAL_WORDS):
        return None

    patterns = [
        r"把[“\"'](?P<old>[^“”\"']{1,60})[”\"']?(?:改成|改为|换成|替换成)[“\"'](?P<new>[^“”\"']{0,80})[”\"']?",
        r"将[“\"'](?P<old>[^“”\"']{1,60})[”\"']?(?:改成|改为|换成|替换成)[“\"'](?P<new>[^“”\"']{0,80})[”\"']?",
        r"[“\"'](?P<old>[^“”\"']{1,60})[”\"']?(?:改成|改为|换成|替换成)[“\"'](?P<new>[^“”\"']{0,80})[”\"']?",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if not match:
            continue
        old = _clean_text(match.group("old"))
        new = _clean_text(match.group("new"))
        if old and old != new:
            return old, new
    return None


def _replace_visible_text(content: str, old: str, new: str) -> tuple[str, int]:
    escaped_old = html.escape(old, quote=False)
    escaped_new = html.escape(new, quote=False)
    chunks = re.split(r"(<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>)", content, flags=re.I | re.S)
    count = 0
    for index, chunk in enumerate(chunks):
        if index % 2 == 1:
            continue
        chunk, direct = _replace_count(chunk, old, new)
        chunk, escaped = _replace_count(chunk, escaped_old, escaped_new)
        chunks[index] = chunk
        count += direct + escaped
    return "".join(chunks), count


def _replace_count(text: str, old: str, new: str) -> tuple[str, int]:
    return text.replace(old, new), text.count(old)


def _snapshot_version(target_dir: Path) -> None:
    versions_dir = target_dir / "versions"
    versions_dir.mkdir(parents=True, exist_ok=True)
    numbers = [
        int(child.name[1:])
        for child in versions_dir.iterdir()
        if child.is_dir() and re.fullmatch(r"v\d{3}", child.name)
    ]
    version_id = f"v{max(numbers, default=0) + 1:03d}"
    snapshot_dir = versions_dir / version_id
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    files = []
    for name in ["index.html", "styles.css", "app.js"]:
        source = target_dir / name
        if source.exists() and source.is_file():
            shutil.copy2(source, snapshot_dir / name)
            files.append(name)
    (snapshot_dir / "version-manifest.json").write_text(
        json.dumps(
            {"version": version_id, "action": "lightweight-revise", "created_at": _now(), "files": files},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def _write_lightweight_execution_report(target_dir: Path, old: str, new: str, count: int, generation_mode: str) -> dict[str, Any]:
    report = {
        "status": "passed",
        "generation_mode": "strict" if str(generation_mode).strip().lower() == "strict" else "fast",
        "summary": f"轻量文案修改完成：已将“{old}”替换为“{new}”，共 {count} 处。",
        "results": {
            "lightweight_revision": {
                "agent_id": "lightweight-revision",
                "status": "passed",
                "checks": [],
                "changed_count": count,
                "finished_at": _now(),
            }
        },
        "validation_layers": [
            {
                "id": "runtime",
                "label": "轻量修改",
                "status": "passed",
                "blocking": True,
                "description": "命中文案级小修改，已跳过完整生成和多智能体验收。",
            }
        ],
        "updated_at": _now(),
    }
    path = target_dir / "config" / "execution-report.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    report["report_url"] = output_url_for_path(path)
    return report


def _lightweight_brain_report(revision: str) -> dict[str, Any]:
    return {
        "self_critique": {
            "score": 100,
            "verdict": "passed",
            "summary": "命中轻量文案修改，已直接更新当前页面。",
        },
        "planning": {"objective": revision},
        "reflection": {"status": "lightweight_patch"},
    }


def _clean_text(value: str) -> str:
    return value.strip().strip("，。；;:： ")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
