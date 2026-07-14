from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from urllib.parse import quote


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _app_root() -> Path:
    return _project_root() / "app"


def _legacy_runtime_root() -> Path:
    return _project_root() / ".music-agent-runtime"


def _default_runtime_root() -> Path:
    project_name = _project_root().name or "music-agent"
    if sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support" / "music-agent-runtime"
    else:
        xdg_state_home = os.environ.get("XDG_STATE_HOME", "").strip()
        xdg_data_home = os.environ.get("XDG_DATA_HOME", "").strip()
        if xdg_state_home:
            base = Path(xdg_state_home).expanduser() / "music-agent-runtime"
        elif xdg_data_home:
            base = Path(xdg_data_home).expanduser() / "music-agent-runtime"
        else:
            base = Path.home() / ".local" / "state" / "music-agent-runtime"
    return base / project_name


def _migrate_legacy_runtime_if_needed(target_root: Path) -> None:
    legacy_root = _legacy_runtime_root()
    if target_root == legacy_root or not legacy_root.exists():
        return

    # Dev mode commonly runs with uvicorn --reload. Keeping runtime writes
    # inside the repo causes file watchers to restart the server mid-job.
    # Move stable runtime data out of tree, but leave old job state behind.
    for name in ("output", "uploads", "assets", "opencode-xdg"):
        source = legacy_root / name
        target = target_root / name
        if not source.exists() or target.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            if source.is_dir():
                shutil.copytree(source, target)
            else:
                shutil.copy2(source, target)
        except Exception:
            continue


def runtime_root() -> Path:
    configured = os.environ.get("MUSIC_AGENT_RUNTIME_DIR", "").strip()
    if configured:
        root = Path(configured).expanduser()
    else:
        root = _default_runtime_root()
    root.mkdir(parents=True, exist_ok=True)
    _migrate_legacy_runtime_if_needed(root)
    return root


def get_output_dir() -> Path:
    if os.environ.get("MUSIC_AGENT_OUTPUT_DIR"):
        path = Path(os.environ.get("MUSIC_AGENT_OUTPUT_DIR", "")).expanduser()
    else:
        path = runtime_root() / "output"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_upload_dir() -> Path:
    if os.environ.get("MUSIC_AGENT_UPLOAD_DIR"):
        path = Path(os.environ.get("MUSIC_AGENT_UPLOAD_DIR", "")).expanduser()
    else:
        path = runtime_root() / "uploads"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_job_dir() -> Path:
    if os.environ.get("MUSIC_AGENT_JOB_DIR"):
        path = Path(os.environ.get("MUSIC_AGENT_JOB_DIR", "")).expanduser()
    else:
        path = runtime_root() / "jobs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_lesson_proposal_dir() -> Path:
    if os.environ.get("MUSIC_AGENT_PROPOSAL_DIR"):
        path = Path(os.environ.get("MUSIC_AGENT_PROPOSAL_DIR", "")).expanduser()
    else:
        path = get_output_dir() / "lesson_proposals"
    path.mkdir(parents=True, exist_ok=True)
    return path


def output_url_for_path(path: Path) -> str:
    try:
        relative = path.resolve().relative_to(get_output_dir().resolve()).as_posix()
        encoded = "/".join(quote(part) for part in relative.split("/"))
        return f"/output/{encoded}"
    except ValueError:
        # 非 output_dir 内部路径不能安全映射到静态输出 URL。
        return ""
