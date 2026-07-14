from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path
from typing import Any

import httpx

from app.services.env_bootstrap import ensure_env_loaded
from app.services.runtime_paths import get_output_dir, output_url_for_path


DEFAULT_IMAGE_MODEL = "ecnu-image"
DEFAULT_PROVIDER = "chat_ecnu"
DEFAULT_IMAGE_SIZE = "1280x720"
ALLOWED_PROVIDERS = {"chat_ecnu", "local_preset"}
DEFAULT_CHAT_ECNU_IMAGE_GENERATIONS_URL = "https://chat.ecnu.edu.cn/open/api/v1/images/generations"
IMAGE_PURPOSES = ("atmosphere",)
SAFE_USAGE = "cover_or_atmosphere_only"
SAFE_USAGE_POLICY = "AI 生成图仅用于作品封面或课堂氛围参考，不得替换模板主场景、角色、道具、地图、操作区或动画素材。"


def image_generation_status() -> dict[str, Any]:
    ensure_env_loaded()
    provider = _provider()
    token_present = bool(_api_token(provider))
    configured = _setting()
    enabled = _enabled()
    return {
        "id": "ai_image_generation",
        "name": "课堂真实图片生成",
        "provider": provider,
        "enabled": enabled,
        "configured": configured,
        "token_present": token_present,
        "model": _model_name(),
        "size": _image_size(),
        "endpoint": _chat_ecnu_image_url() if provider == "chat_ecnu" else "",
        "output_dir": str(_image_output_dir()),
        "fallback": "preset_visual_asset_library",
        "reason": "" if enabled else _disabled_reason(),
        "description": "根据教案重点和歌曲气质生成课堂氛围图；不可用时自动使用稳定模板场景。",
    }


def attach_generated_visual_assets(spec: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    ensure_env_loaded()
    enriched = dict(spec)
    report = _base_report()
    if not _enabled():
        report["status"] = "disabled"
        report["reason"] = _disabled_reason()
        enriched["image_generation"] = report
        return enriched, report

    try:
        generated_pack, report = _generate_pack(enriched)
    except Exception as exc:  # pragma: no cover - network/provider failures are environment-specific.
        report = _base_report()
        report["status"] = "failed"
        report["reason"] = f"{type(exc).__name__}: {exc}"
        if "visual_asset_pack" in enriched:
            report["fallback_applied"] = True
        enriched["image_generation"] = report
        return enriched, report

    base_pack = dict(enriched.get("visual_asset_pack") or {})
    merged_pack = {
        **base_pack,
        **generated_pack,
        "source": f"{report.get('provider', _provider())}_text_to_image",
        "fallback_badge": base_pack.get("badge", ""),
    }
    merged_pack.pop("background_image", None)
    if not merged_pack.get("badge"):
        merged_pack["badge"] = base_pack.get("badge") or merged_pack.get("component", "")

    enriched["visual_asset_pack"] = merged_pack
    if isinstance(enriched.get("music_game"), dict):
        enriched["music_game"] = {**enriched["music_game"], "visual_asset_pack": merged_pack}
    visual_theme = dict(enriched.get("visual_theme") or {})
    style = visual_theme.get("illustration_style", "课堂视觉")
    visual_theme["illustration_style"] = f"{style}；已生成课堂氛围图，游戏主场景仍使用稳定模板画面"
    visual_theme["asset_pack_id"] = merged_pack["id"]
    enriched["visual_theme"] = visual_theme
    enriched["image_generation"] = report
    return enriched, report


def build_image_prompts(spec: dict[str, Any]) -> dict[str, str]:
    game = spec.get("music_game") if isinstance(spec.get("music_game"), dict) else {}
    lesson = spec.get("lesson_context") if isinstance(spec.get("lesson_context"), dict) else {}
    music_element = (
        spec.get("target_music_element")
        or game.get("music_concept")
        or lesson.get("target_music_element")
        or "音乐课堂活动"
    )
    song_name = spec.get("song_name") or lesson.get("song_name") or game.get("song_name") or ""
    game_name = game.get("game_name") or spec.get("title") or "音乐游戏"
    mechanism = (
        game.get("mechanism_id")
        or (spec.get("music_element_mechanic") or {}).get("mechanism_id", "")
        or spec.get("target_segment_mechanic", "")
    )
    student_task = lesson.get("student_task") or spec.get("target_segment_task") or game.get("goal", "")
    visual_hint = _visual_hint_for_text(
        " ".join([str(music_element), str(mechanism), str(student_task), str(game_name), str(song_name)])
    )
    common = (
        "中小学音乐课堂氛围图，横版16:9，远景氛围层，画面明亮干净，适合儿童课堂，"
        "无文字、无logo、无水印、无乐谱、无谱子、无五线谱、无音符主体、无人物、"
        "无乐器主体、无按钮、无界面按钮、无可交互道具，不出现畸形乐器或危险动作，"
        "中央留空，中心区域干净，边缘只保留轻量主题装饰"
    )
    song_clause = f"，灵感来自歌曲《{song_name}》" if song_name else ""
    return {
        "atmosphere": (
            f"{common}，游戏名“{game_name}”，音乐重点“{music_element}”{song_clause}，{visual_hint}"
        ),
    }


def _generate_pack(spec: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    provider = _provider()
    token = _api_token(provider)
    if not token:
        raise RuntimeError(f"{_token_name(provider)} is missing")
    if provider != "chat_ecnu":
        raise RuntimeError(f"Unsupported image generation provider: {provider}")

    prompts = build_image_prompts(spec)
    model = _model_name()
    generated: dict[str, str] = {}
    cache_hits: list[str] = []
    for purpose in IMAGE_PURPOSES:
        prompt = prompts[purpose]
        image_path = _cached_image_path(model, provider, purpose, prompt)
        if image_path.exists():
            cache_hits.append(purpose)
        else:
            image_bytes = _call_chat_ecnu_image_generation(prompt=prompt, model=model, token=token)
            image_path.parent.mkdir(parents=True, exist_ok=True)
            image_path.write_bytes(image_bytes)
        generated[purpose] = output_url_for_path(image_path)

    pack_id = "ai_generated_" + _stable_hash({"model": model, "provider": provider, "prompts": prompts})[:10]
    report = _base_report()
    report.update(
        {
            "status": "cached" if len(cache_hits) == len(IMAGE_PURPOSES) else "generated",
            "provider": provider,
            "model": model,
            "endpoint": _chat_ecnu_image_url(),
            "size": _image_size(),
            "prompts": prompts,
            "cache_hits": cache_hits,
            "assets": generated,
            "image_count": len(generated),
            "usage": SAFE_USAGE,
            "safe_usage_policy": SAFE_USAGE_POLICY,
            "user_message": "已生成课堂氛围图，游戏主场景仍使用稳定模板画面。",
        }
    )
    atmosphere_image = generated["atmosphere"]
    return (
        {
            "id": pack_id,
            "label": "ChatECNU 生成课堂氛围图",
            "hero": atmosphere_image,
            "atmosphere_image": atmosphere_image,
            "cover_image": atmosphere_image,
            "component": "",
            "badge": "",
            "provider": provider,
            "model": model,
            "usage": SAFE_USAGE,
        },
        report,
    )


def _visual_hint_for_text(text: str) -> str:
    lowered = text.lower()
    if any(word in lowered for word in ["牧歌", "草原", "蒙古", "蒙古族", "牧民", "辽阔", "民歌"]):
        return "草原、蓝天、远山、牧歌民歌气质，色彩清新辽阔，适合表现旋律起伏"
    if any(word in lowered for word in ["红歌", "革命", "歌唱祖国", "红色", "祖国", "合唱", "队歌"]):
        return "红色舞台、合唱氛围、飘带和暖金灯光，庄重明亮，不出现具体人物、徽章、标语或敏感符号"
    if any(word in lowered for word in ["江南", "茉莉花", "水乡", "小桥", "流水"]):
        return "江南水乡、清雅花朵、柔和水面和音乐课堂气质"
    if any(word in lowered for word in ["节奏", "节拍", "时值", "切分", "附点", "rhythm", "meter"]):
        return "节奏律动感、打击乐、拍点光效、学生跟随稳定拍活动"
    if any(word in lowered for word in ["音高", "旋律", "sol", "mi", "乐句", "pitch", "melody"]):
        return "旋律路线、音高阶梯、上行下行的光带，空间开阔"
    if any(word in lowered for word in ["力度", "强弱", "速度", "tempo", "dynamic"]):
        return "声音能量波、强弱对比、指挥手势和柔和光影"
    if any(word in lowered for word in ["音色", "乐器", "timbre", "古筝", "长笛", "二胡", "小提琴"]):
        return "真实乐器、音色侦探氛围、学生比较不同乐器声音色彩"
    if any(word in lowered for word in ["五声", "宫", "商", "角", "徵", "羽", "民族", "调式", "mode"]):
        return "中国民族音乐课堂气质，古筝、竹笛细节，五声音阶色彩"
    return "课堂任务冒险氛围、音乐卡片、合作学习、学习目标视觉化"


def _call_chat_ecnu_image_generation(*, prompt: str, model: str, token: str) -> bytes:
    response = httpx.post(
        _chat_ecnu_image_url(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={
            "model": model,
            "prompt": prompt,
            "n": 1,
            "size": _image_size(),
            "response_format": _response_format(),
        },
        timeout=float(os.environ.get("IMAGE_GEN_TIMEOUT", "120")),
    )
    response.raise_for_status()
    payload = response.json()
    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, list) or not data:
        raise RuntimeError("ChatECNU image response did not include data")
    item = data[0] if isinstance(data[0], dict) else {}
    if item.get("b64_json"):
        return base64.b64decode(str(item["b64_json"]))
    if item.get("url"):
        return _download_generated_image(str(item["url"]))
    raise RuntimeError("ChatECNU image response did not include b64_json or url")


def _download_generated_image(url: str) -> bytes:
    response = httpx.get(url, timeout=float(os.environ.get("IMAGE_GEN_DOWNLOAD_TIMEOUT", "60")))
    response.raise_for_status()
    return response.content


def _cached_image_path(model: str, provider: str, purpose: str, prompt: str) -> Path:
    digest = _stable_hash({"model": model, "provider": provider, "purpose": purpose, "prompt": prompt})
    return _image_output_dir() / f"{purpose}-{digest[:16]}.{_image_extension()}"


def _image_output_dir() -> Path:
    path = get_output_dir() / "generated_images"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _stable_hash(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return hashlib.sha1(body.encode("utf-8")).hexdigest()


def _base_report() -> dict[str, Any]:
    return {
        "status": "not_run",
        "provider": _provider(),
        "model": _model_name(),
        "assets": {},
        "prompts": {},
        "fallback": "preset_visual_asset_library",
        "image_count": 0,
        "usage": SAFE_USAGE,
        "safe_usage_policy": SAFE_USAGE_POLICY,
        "user_message": "已使用稳定模板场景，保证游戏画面和操作清楚。",
    }


def _enabled() -> bool:
    setting = _setting()
    if setting in {"0", "false", "off", "no", "disabled"}:
        return False
    provider = _provider()
    if provider == "local_preset" or provider not in ALLOWED_PROVIDERS:
        return False
    if setting in {"1", "true", "on", "yes", "enabled"}:
        return bool(_api_token(provider))
    return bool(_api_token(provider))


def _setting() -> str:
    return os.environ.get("IMAGE_GEN_ENABLED", "auto").strip().lower()


def _disabled_reason() -> str:
    if _setting() in {"0", "false", "off", "no", "disabled"}:
        return "IMAGE_GEN_ENABLED is disabled"
    provider = _provider()
    if provider == "local_preset":
        return "使用本地预设素材，不调用远程生图服务"
    if provider not in ALLOWED_PROVIDERS:
        return f"不允许使用非国内生图服务: {provider}"
    if not _api_token(provider):
        return f"{_token_name(provider)} is not configured"
    return "image generation is not enabled"


def _model_name() -> str:
    return os.environ.get("IMAGE_GEN_MODEL", DEFAULT_IMAGE_MODEL).strip() or DEFAULT_IMAGE_MODEL


def _provider() -> str:
    return os.environ.get("IMAGE_GEN_PROVIDER", DEFAULT_PROVIDER).strip().lower() or DEFAULT_PROVIDER


def _api_token(provider: str) -> str:
    if provider == "chat_ecnu":
        return os.environ.get("CHAT_ECNU_API_KEY", "").strip()
    return ""


def _token_name(provider: str) -> str:
    if provider == "chat_ecnu":
        return "CHAT_ECNU_API_KEY"
    return "IMAGE_GEN_API_KEY"


def _chat_ecnu_image_url() -> str:
    return (
        os.environ.get("CHAT_ECNU_IMAGE_GENERATIONS_URL", "").strip()
        or DEFAULT_CHAT_ECNU_IMAGE_GENERATIONS_URL
    )


def _image_size() -> str:
    size = os.environ.get("IMAGE_GEN_SIZE", DEFAULT_IMAGE_SIZE).strip() or DEFAULT_IMAGE_SIZE
    return size if size in {"512x512", "768x768", "720x1280", "1280x720", "1024x1024"} else DEFAULT_IMAGE_SIZE


def _response_format() -> str:
    configured = os.environ.get("IMAGE_GEN_RESPONSE_FORMAT", "b64_json").strip().lower()
    return configured if configured in {"b64_json", "url"} else "b64_json"


def _image_extension() -> str:
    configured = os.environ.get("IMAGE_GEN_FILE_EXTENSION", "png").strip().lower().lstrip(".")
    return configured if configured in {"png", "jpg", "jpeg", "webp"} else "png"
