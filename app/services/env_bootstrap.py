from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv


_ENV_LOADED = False


def ensure_env_loaded() -> None:
    global _ENV_LOADED
    if _ENV_LOADED:
        return

    current_file = Path(__file__).resolve()
    app_dir = current_file.parent.parent
    project_dir = app_dir.parent
    workspace_dir = project_dir.parent

    # 优先加载工作区根目录的共享配置，再加载第一版自己的覆盖配置。
    # .env.server 让本地 uvicorn 启动也能复用 Docker 部署所需的服务端配置。
    for candidate in [workspace_dir / ".env", project_dir / ".env", project_dir / ".env.server"]:
        if candidate.exists():
            load_dotenv(candidate, override=False)

    _ENV_LOADED = True
