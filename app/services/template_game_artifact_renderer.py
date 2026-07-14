from __future__ import annotations

import html
import json
import shutil
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.services.image_generation_skill import attach_generated_visual_assets
from app.services.runtime_paths import output_url_for_path
from app.services.template_fidelity_contract import build_template_fidelity_contract


FRONTEND_DIST_DIR = Path(__file__).resolve().parents[2] / "frontend" / "dist"
FRONTEND_SRC_DIR = Path(__file__).resolve().parents[2] / "frontend" / "src"
RUNTIME_SOURCE = "react_student_runtime"
RUNTIME_VERSION = "react_student_runtime_v2"
FRONTEND_DIST_STALE_GRACE_SECONDS = 24 * 60 * 60.0


def render_template_game_artifact(
    workflow: dict[str, Any],
    output_dir: Path,
    *,
    lesson_game_contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Publish a React-rendered student game powered by reusable gameplay templates."""
    workflow, visual_asset_pack, image_generation_report = _prepare_template_visual_assets(workflow)
    instance = workflow.get("instance", {}) if isinstance(workflow.get("instance"), dict) else {}
    proposal_card = workflow.get("proposal_card", {}) if isinstance(workflow.get("proposal_card"), dict) else {}
    config = instance.get("config", {}) if isinstance(instance.get("config"), dict) else {}
    template_id = str(instance.get("template_id") or config.get("template_id") or "")
    tool_id = uuid4().hex[:10]
    target_dir = output_dir / "generated_tools" / tool_id
    target_dir.mkdir(parents=True, exist_ok=True)
    index_path = target_dir / "index.html"
    spec = _artifact_spec(workflow)
    runtime_marker = _runtime_marker(workflow)
    template_fidelity_contract = _template_fidelity_contract(workflow)
    spec["runtime_marker"] = runtime_marker
    spec["template_fidelity_contract"] = template_fidelity_contract
    spec["visual_asset_pack"] = visual_asset_pack
    spec["image_generation"] = image_generation_report
    page_state = {
        "workflow": workflow,
        "instance": instance,
        "proposal_card": proposal_card,
        "config": config,
        "template_id": template_id,
        "lesson_game_contract": lesson_game_contract or {},
        "material_binding_plan": workflow.get("material_binding_plan", {}),
        "template_fidelity_contract": template_fidelity_contract,
        "runtime_marker": runtime_marker,
        "visual_asset_pack": visual_asset_pack,
        "image_generation": image_generation_report,
    }
    runtime_assets = _student_runtime_assets(target_dir)
    index_path.write_text(_html_document(page_state, runtime_assets=runtime_assets), encoding="utf-8")
    return {
        "action": "DELIVER",
        "generation_mode": "composed_template_game",
        "template_first": True,
        "runtime_marker": runtime_marker,
        "template_fidelity_contract": template_fidelity_contract,
        "page_url": output_url_for_path(index_path),
        "file_path": str(index_path),
        "spec": spec,
        "template_workflow": workflow,
        "execution": {
            "generation_mode": RUNTIME_SOURCE,
            "runtime_marker": runtime_marker,
            "status": "ready",
            "summary": (
                "已按教案契约完成学生成品游戏合成，并由 React 学生运行时承载。"
                if lesson_game_contract
                else "已用成熟玩法模板合成学生成品游戏，并由 React 学生运行时承载。"
            ),
            "quality_gates": workflow.get("quality_gates", []),
        },
    }


def _prepare_template_visual_assets(workflow: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    spec = _artifact_spec(workflow)
    visual_asset_pack = _base_template_asset_pack(workflow)
    spec["visual_asset_pack"] = visual_asset_pack
    music_game = spec.get("music_game", {}) if isinstance(spec.get("music_game"), dict) else {}
    spec["music_game"] = {**music_game, "visual_asset_pack": visual_asset_pack}
    enriched, report = attach_generated_visual_assets(spec)
    pack = enriched.get("visual_asset_pack", visual_asset_pack)
    if not isinstance(pack, dict):
        pack = visual_asset_pack
    updated = _inject_visual_pack_into_workflow(workflow, pack, report)
    return updated, pack, report


def _base_template_asset_pack(workflow: dict[str, Any]) -> dict[str, Any]:
    theme_pack = workflow.get("theme_pack", {}) if isinstance(workflow.get("theme_pack"), dict) else {}
    palette = theme_pack.get("palette", {}) if isinstance(theme_pack.get("palette"), dict) else {}
    scene = theme_pack.get("scene", {}) if isinstance(theme_pack.get("scene"), dict) else {}
    return {
        "id": str(theme_pack.get("theme_id") or "template_theme"),
        "label": str(theme_pack.get("theme_name") or scene.get("setting") or "模板主题背景"),
        "hero": "",
        "badge": "",
        "component": "",
        "accent": palette.get("accent", ""),
        "background": palette.get("background", ""),
        "source": "template_theme_pack",
    }


def _inject_visual_pack_into_workflow(
    workflow: dict[str, Any],
    visual_asset_pack: dict[str, Any],
    image_generation_report: dict[str, Any],
) -> dict[str, Any]:
    updated = dict(workflow)
    updated["visual_asset_pack"] = visual_asset_pack
    updated["image_generation"] = image_generation_report
    atmosphere = str(visual_asset_pack.get("atmosphere_image") or visual_asset_pack.get("cover_image") or "")
    for key in ("theme_pack", "presentation_pack"):
        pack = dict(updated.get(key, {})) if isinstance(updated.get(key), dict) else {}
        asset_manifest = dict(pack.get("asset_manifest", {})) if isinstance(pack.get("asset_manifest"), dict) else {}
        if atmosphere:
            asset_manifest["generated_atmosphere_image"] = atmosphere
            asset_manifest["cover_image"] = atmosphere
        asset_manifest["image_generation_provider"] = image_generation_report.get("provider", "")
        asset_manifest["image_generation_status"] = image_generation_report.get("status", "")
        asset_manifest["image_generation_usage"] = image_generation_report.get("usage", "")
        pack["asset_manifest"] = asset_manifest
        pack["visual_asset_pack"] = visual_asset_pack
        pack["image_generation"] = image_generation_report
        updated[key] = pack
    return updated


def _artifact_spec(workflow: dict[str, Any]) -> dict[str, Any]:
    instance = workflow.get("instance", {}) if isinstance(workflow.get("instance"), dict) else {}
    proposal_card = workflow.get("proposal_card", {}) if isinstance(workflow.get("proposal_card"), dict) else {}
    config = instance.get("config", {}) if isinstance(instance.get("config"), dict) else {}
    material = proposal_card.get("material_binding", {}) if isinstance(proposal_card.get("material_binding"), dict) else {}
    title = proposal_card.get("fit_summary") or proposal_card.get("title") or instance.get("template_label") or "课堂音乐游戏"
    song_name = material.get("song_title") or "自选歌曲"
    return {
        "activity_type": "music_game",
        "title": title,
        "subtitle": proposal_card.get("transfer_task") or "围绕课例目标生成的学生成品音乐游戏。",
        "song_name": song_name,
        "grade_band": config.get("grade_band") or proposal_card.get("grade_band") or "小学",
        "generation_mode": "composed_template_game",
        "music_game": {
            "enabled": True,
            "template_id": instance.get("template_id"),
            "game_name": instance.get("template_label"),
            "music_concept": config.get("music_concept"),
            "student_task": instance.get("student_task", {}),
            "skin": instance.get("skin", {}),
        },
        "template_match": workflow.get("template_match", {}),
        "template_workflow": workflow,
        "lesson_adaptation": workflow.get("lesson_adaptation", {}),
        "template_decision": workflow.get("template_decision", {}),
        "gameplay_blueprint": workflow.get("gameplay_blueprint", {}),
        "experience_script": workflow.get("experience_script", {}),
        "theme_pack": workflow.get("theme_pack", {}),
        "presentation_pack": workflow.get("presentation_pack", {}),
        "opencode_role_policy": workflow.get("opencode_role_policy", {}),
        "render_spec": workflow.get("render_spec", {}),
        "frontend_handoff_contract": workflow.get("frontend_handoff_contract", {}),
        "intervention_trace": workflow.get("intervention_trace", []),
        "responsibility_map": workflow.get("responsibility_map", {}),
        "delivery_decision": workflow.get("delivery_decision", {}),
        "lesson_fit": proposal_card.get("lesson_fit", {}),
        "material_binding_plan": workflow.get("material_binding_plan", {}),
        "template_fidelity_contract": workflow.get("template_fidelity_contract", {}),
        "visual_asset_pack": workflow.get("visual_asset_pack", {}),
        "image_generation": workflow.get("image_generation", {}),
        "template_workflow_version": workflow.get("workflow_version", ""),
    }


def _template_fidelity_contract(workflow: dict[str, Any]) -> dict[str, Any]:
    existing = workflow.get("template_fidelity_contract", {}) if isinstance(workflow.get("template_fidelity_contract"), dict) else {}
    instance = workflow.get("instance", {}) if isinstance(workflow.get("instance"), dict) else {}
    return build_template_fidelity_contract(instance, str(existing.get("skin_selection_source") or ""))


def _runtime_marker(workflow: dict[str, Any]) -> dict[str, str]:
    instance = workflow.get("instance", {}) if isinstance(workflow.get("instance"), dict) else {}
    config = instance.get("config", {}) if isinstance(instance.get("config"), dict) else {}
    gameplay_blueprint = workflow.get("gameplay_blueprint", {}) if isinstance(workflow.get("gameplay_blueprint"), dict) else {}
    presentation_pack = workflow.get("presentation_pack", {}) if isinstance(workflow.get("presentation_pack"), dict) else {}
    theme_pack = workflow.get("theme_pack", {}) if isinstance(workflow.get("theme_pack"), dict) else {}
    experience_variant = workflow.get("experience_variant", {}) if isinstance(workflow.get("experience_variant"), dict) else {}

    experience_variant_id = _first_text(
        gameplay_blueprint.get("experience_variant_id"),
        presentation_pack.get("experience_variant_id"),
        theme_pack.get("experience_variant_id"),
        experience_variant.get("experience_variant_id"),
        experience_variant.get("skin_id"),
        config.get("experience_variant_id"),
    )
    play_mode = _first_text(
        gameplay_blueprint.get("play_mode"),
        presentation_pack.get("play_mode"),
        theme_pack.get("play_mode"),
        experience_variant.get("play_mode"),
        config.get("play_mode"),
    )
    return {
        "runtime_source": RUNTIME_SOURCE,
        "runtime_version": RUNTIME_VERSION,
        "generated_with": "render_template_game_artifact",
        "runtime_target": "react_student_runtime",
        "output_kind": "react_presentation_pack",
        "template_id": str(instance.get("template_id") or config.get("template_id") or ""),
        "template_label": str(instance.get("template_label") or ""),
        "experience_variant_id": experience_variant_id,
        "play_mode": play_mode,
    }


def _first_text(*values: Any) -> str:
    for value in values:
        text = str(value or "").strip()
        if text:
            return text
    return ""


def _student_runtime_assets(target_dir: Path) -> tuple[list[str], str]:
    manifest_path = FRONTEND_DIST_DIR / ".vite" / "manifest.json"
    if not manifest_path.exists():
        raise RuntimeError("缺少学生端 React 运行时构建产物，请先执行 frontend 的 npm run build。")
    _assert_frontend_dist_current(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entry_key, entry = _student_runtime_manifest_entry(manifest)
    if not isinstance(entry, dict) or not entry.get("file"):
        raise RuntimeError("学生端 React 运行时构建产物不完整，请重新执行 frontend 的 npm run build。")
    asset_paths: list[str] = []
    css_assets: list[str] = []

    def remember_asset(asset_path: str) -> None:
        if asset_path and asset_path not in asset_paths:
            asset_paths.append(asset_path)

    def collect_assets(manifest_key: str) -> None:
        item = manifest.get(manifest_key)
        if not isinstance(item, dict):
            return
        if isinstance(item.get("file"), str):
            remember_asset(item["file"])
        for imported_key in item.get("imports", []):
            if isinstance(imported_key, str):
                collect_assets(imported_key)
        for css_file in item.get("css", []):
            if isinstance(css_file, str) and css_file not in css_assets:
                css_assets.append(css_file)
                remember_asset(css_file)

    collect_assets(entry_key)
    _copy_runtime_assets(asset_paths, target_dir)
    css_files = [item for item in css_assets]
    script_file = str(entry["file"])
    if not (script_file.startswith("assets/student-game-") or script_file.startswith("assets/student-main-")):
        raise RuntimeError("学生端 React 运行时入口不是最新 student-game bundle，请重新执行 frontend 的 npm run build。")
    return css_files, script_file


def _student_runtime_manifest_entry(manifest: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    direct = manifest.get("student-game.html")
    if isinstance(direct, dict):
        return "student-game.html", direct
    for key, item in manifest.items():
        if not isinstance(item, dict):
            continue
        file_path = str(item.get("file") or "")
        name = str(item.get("name") or "")
        if file_path.endswith(".js") and (name == "student-main" or file_path.startswith("assets/student-main-")):
            return str(key), item
    return "student-game.html", {}


def _assert_frontend_dist_current(manifest_path: Path) -> None:
    source_paths = _student_runtime_source_paths()
    if not source_paths:
        return
    manifest_mtime = manifest_path.stat().st_mtime
    newest_source = max(path.stat().st_mtime for path in source_paths if path.exists())
    if newest_source > manifest_mtime + FRONTEND_DIST_STALE_GRACE_SECONDS:
        raise RuntimeError("学生端 React 运行时构建产物已过期，请在 frontend 目录执行 npm run build 后重新生成。")


def _student_runtime_source_paths() -> list[Path]:
    paths = [
        FRONTEND_SRC_DIR / "student-main.tsx",
        FRONTEND_SRC_DIR / "student-game" / "StudentGameApp.tsx",
        FRONTEND_SRC_DIR / "student-game" / "styles.css",
        FRONTEND_SRC_DIR / "student-game" / "types.ts",
    ]
    student_game_dir = FRONTEND_SRC_DIR / "student-game"
    if student_game_dir.exists():
        paths.extend(student_game_dir.rglob("*.ts"))
        paths.extend(student_game_dir.rglob("*.tsx"))
        paths.extend(student_game_dir.rglob("*.css"))
    unique: list[Path] = []
    seen: set[Path] = set()
    for path in paths:
        if path.exists() and path.is_file() and path not in seen:
            unique.append(path)
            seen.add(path)
    return unique


def _copy_runtime_assets(asset_paths: list[str], target_dir: Path) -> None:
    for asset_path in asset_paths:
        source = FRONTEND_DIST_DIR / asset_path
        if not source.exists() or not source.is_file():
            raise RuntimeError(f"学生端 React 运行时资源缺失：{asset_path}。请重新执行 frontend 的 npm run build。")
        target = target_dir / asset_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def _html_document(page_state: dict[str, Any], *, runtime_assets: tuple[list[str], str]) -> str:
    state_json = json.dumps(page_state, ensure_ascii=False).replace("</", "<\\/")
    runtime_marker = page_state.get("runtime_marker", {}) if isinstance(page_state.get("runtime_marker"), dict) else {}
    fidelity = page_state.get("template_fidelity_contract", {}) if isinstance(page_state.get("template_fidelity_contract"), dict) else {}
    marker_json = json.dumps(runtime_marker, ensure_ascii=False).replace("</", "<\\/")
    title = html.escape(str(_artifact_spec(page_state.get("workflow", {})).get("title", "课堂音乐游戏")))
    css_files, script_file = runtime_assets
    css_tags = "\n".join(f'  <link rel="stylesheet" crossorigin href="{html.escape(item)}" />' for item in css_files)
    script_src = html.escape(script_file)
    audio_policy = {
        "policy_id": "soundfont_first_hybrid_audio",
        "lesson_audio_priority": True,
        "soundfont_player_paths": [
            "/runtime-assets/soundfont-player/soundfont-player.js",
            "/static/assets/soundfont-player/soundfont-player.js",
        ],
        "soundfont_sample_bases": [
            "/runtime-assets/midi-js-soundfonts/FluidR3_GM/",
            "/static/assets/midi-js-soundfonts/FluidR3_GM/",
        ],
        "fallback": "oscillator_only_after_soundfont_failure",
    }
    audio_policy_json = json.dumps(audio_policy, ensure_ascii=False).replace("</", "<\\/")
    runtime_source = html.escape(str(runtime_marker.get("runtime_source") or RUNTIME_SOURCE))
    runtime_version = html.escape(str(runtime_marker.get("runtime_version") or RUNTIME_VERSION))
    template_id = html.escape(str(fidelity.get("template_id") or runtime_marker.get("template_id") or ""))
    selected_skin_id = html.escape(str(fidelity.get("selected_skin_id") or ""))
    runtime_shell = html.escape(str(fidelity.get("runtime_shell") or ""))
    runtime_component = html.escape(str(fidelity.get("actual_runtime_component") or ""))
    template_fidelity_pass = "true" if fidelity.get("template_fidelity_pass") else "false"
    experience_variant_id = html.escape(str(runtime_marker.get("experience_variant_id") or ""))
    play_mode = html.escape(str(runtime_marker.get("play_mode") or ""))
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="buyilehu-runtime-source" content="{runtime_source}" />
  <meta name="buyilehu-runtime-version" content="{runtime_version}" />
  <meta name="buyilehu-template-id" content="{template_id}" />
  <meta name="buyilehu-selected-skin-id" content="{selected_skin_id}" />
  <meta name="buyilehu-runtime-shell" content="{runtime_shell}" />
  <meta name="buyilehu-runtime-component" content="{runtime_component}" />
  <meta name="buyilehu-template-fidelity-pass" content="{template_fidelity_pass}" />
  <meta name="buyilehu-experience-variant-id" content="{experience_variant_id}" />
  <meta name="buyilehu-play-mode" content="{play_mode}" />
  <meta name="buyilehu-audio-policy" content="soundfont_first_hybrid_audio" />
  <title>{title}</title>
{css_tags}
</head>
<body data-buyilehu-runtime-source="{runtime_source}" data-buyilehu-runtime-version="{runtime_version}" data-experience-variant-id="{experience_variant_id}" data-play-mode="{play_mode}">
  <div id="student-game-root"></div>
  <script>
    window.__BUYILEHU_RUNTIME_MARKER__ = {marker_json};
    window.__BUYILEHU_AUDIO_POLICY__ = {audio_policy_json};
    window.__STUDENT_GAME_STATE__ = {state_json};
  </script>
  <script type="module" crossorigin src="{script_src}"></script>
</body>
</html>"""
