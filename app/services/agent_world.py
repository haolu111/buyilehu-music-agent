from __future__ import annotations

import json
import os
import http.client
import urllib.error
import urllib.request
from typing import Any


def agent_world_status() -> dict[str, Any]:
    base_url = os.getenv("AGENT_WORLD_BASE_URL", "https://world.coze.site").rstrip("/")
    username = os.getenv("AGENT_WORLD_USERNAME", "")
    api_key = os.getenv("AGENT_WORLD_API_KEY", "")

    status: dict[str, Any] = {
        "enabled": bool(username and api_key),
        "base_url": base_url,
        "username": username,
        "authenticated": bool(api_key),
    }
    if not username:
        return status

    try:
        request = urllib.request.Request(f"{base_url}/api/agents/profile/{username}", method="GET")
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
        status["profile"] = payload.get("data", {})
        status["reachable"] = bool(payload.get("success"))
    except (
        urllib.error.URLError,
        TimeoutError,
        json.JSONDecodeError,
        http.client.IncompleteRead,
        http.client.RemoteDisconnected,
    ) as exc:
        status["reachable"] = False
        status["error"] = str(exc)

    return status


def update_agent_world_profile(nickname: str | None = None, bio: str | None = None) -> dict[str, Any]:
    base_url = os.getenv("AGENT_WORLD_BASE_URL", "https://world.coze.site").rstrip("/")
    api_key = os.getenv("AGENT_WORLD_API_KEY", "")
    if not api_key:
        return {"success": False, "message": "Agent World API Key is not configured."}

    body = {key: value for key, value in {"nickname": nickname, "bio": bio}.items() if value}
    request = urllib.request.Request(
        f"{base_url}/api/agents/profile",
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "agent-auth-api-key": api_key,
        },
        method="PUT",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return {"success": False, "message": exc.read().decode("utf-8")}
    except (urllib.error.URLError, TimeoutError) as exc:
        return {"success": False, "message": str(exc)}
