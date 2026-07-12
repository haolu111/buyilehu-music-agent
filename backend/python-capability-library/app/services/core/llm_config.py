from __future__ import annotations

import os
from typing import Any

from app.services.core.env_bootstrap import ensure_env_loaded


CHAT_ECNU_MODEL_ALIASES = {
    "ecnumax": "ecnu-max",
    "ecnu_max": "ecnu-max",
    "ecnuplus": "ecnu-plus",
    "ecnu_plus": "ecnu-plus",
}


def normalize_chat_ecnu_model_name(model: str) -> str:
    normalized = str(model or "").strip()
    return CHAT_ECNU_MODEL_ALIASES.get(normalized.lower(), normalized)


def llm_runtime_config() -> dict[str, Any]:
    ensure_env_loaded()
    api_key = (
        os.getenv("CHAT_ECNU_API_KEY")
        or os.getenv("DEEPSEEK_API_KEY")
        or ""
    )
    chat_completions_url = (
        os.getenv("CHAT_ECNU_CHAT_COMPLETIONS_URL")
        or "https://chat.ecnu.edu.cn/open/api/v1/chat/completions"
    )
    base_url = (
        os.getenv("CHAT_ECNU_BASE_URL")
        or os.getenv("DEEPSEEK_BASE_URL")
        or ""
    )
    model = (
        os.getenv("CHAT_ECNU_MODEL")
        or os.getenv("DEEPSEEK_MODEL")
        or ""
    )
    model = normalize_chat_ecnu_model_name(model)
    if any(
        [
            os.getenv("CHAT_ECNU_API_KEY"),
            os.getenv("CHAT_ECNU_BASE_URL"),
            os.getenv("CHAT_ECNU_CHAT_COMPLETIONS_URL"),
            os.getenv("CHAT_ECNU_MODEL"),
        ]
    ):
        provider = "chat_ecnu"
        base_url = base_url or "https://chat.ecnu.edu.cn/open/api/v1"
        model = model or "ecnu-max"
    elif any(
        [
            os.getenv("DEEPSEEK_API_KEY"),
            os.getenv("DEEPSEEK_BASE_URL"),
            os.getenv("DEEPSEEK_MODEL"),
        ]
    ):
        provider = "deepseek"
    else:
        provider = "none"
    return {
        "enabled": bool(api_key and base_url and model),
        "api_key": api_key,
        "base_url": base_url,
        "chat_completions_url": chat_completions_url,
        "model": model,
        "provider": provider,
    }


def llm_env_missing_reason() -> str:
    return (
        "missing CHAT_ECNU_API_KEY/CHAT_ECNU_MODEL or "
        "DEEPSEEK_API_KEY/DEEPSEEK_BASE_URL/DEEPSEEK_MODEL"
    )
