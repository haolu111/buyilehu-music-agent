from __future__ import annotations

import html
import json
from pathlib import Path
from uuid import uuid4


PRODUCTION_MUSIC_GAME_TEMPLATE_IDS = {
    "beat_guardian_core",
    "pitch_ladder_core",
    "rhythm_echo_core",
    "solfege_target_core",
    "timbre_detective_core",
    "form_treasure_core",
    "composition_puzzle_core",
}

NEW_STUDENT_RUNTIME_MARKERS = [
    "student-game-root",
    "__STUDENT_GAME_STATE__",
    "react_student_runtime",
]


def _short_student_text(value: object, limit: int = 36) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "…"


def render_generated_tool(spec: dict, output_dir: Path) -> tuple[Path, str]:
    _assert_not_production_music_game_legacy_route(spec)
    tool_id = uuid4().hex[:10]
    target_dir = output_dir / "generated_tools" / tool_id
    target_dir.mkdir(parents=True, exist_ok=True)
    index_path = target_dir / "index.html"
    index_path.write_text(_render_html(spec), encoding="utf-8")
    return index_path, f"/output/generated_tools/{tool_id}/index.html"


def ensure_listening_tool_contract(spec: dict, index_path: Path) -> bool:
    """Keep listening artifacts from losing the required audio element controls."""
    if not _is_listening_tool(spec):
        return False
    required_markers = [
        'id="listening-form"',
        'name="audio"',
        'name="tonic"',
        'name="mode"',
        'name="tempo_multiplier"',
        'name="rhythm_density"',
        'name="instrument"',
        'data-component="element_control_panel"',
        'value="preserve" selected',
        'value="1.0"',
        "保持原调式",
        "保持原音色",
        "resolvePlaybackInstrument",
        "/api/listening/upload",
        "/api/listening/transform",
        "uploadPayload.session_id",
        'transformData.append("session_id", sessionId)',
        "generated_midi_url",
        "source_audio_url",
        "transformed_audio_url",
    ]
    html_text = index_path.read_text(encoding="utf-8") if index_path.exists() else ""
    if all(marker in html_text for marker in required_markers):
        return False
    index_path.write_text(_render_html(spec), encoding="utf-8")
    return True


def ensure_music_game_playable_contract(spec: dict, index_path: Path) -> bool:
    """Keep lesson-generated music games from degrading into text-only rule pages."""
    production_template_id = _production_music_game_template_id(spec)
    if production_template_id:
        html_text = index_path.read_text(encoding="utf-8") if index_path.exists() else ""
        if _has_new_student_runtime(html_text):
            return False
        raise RuntimeError(
            f"{production_template_id} 是已升级的成熟音乐游戏模板，必须使用 "
            "render_template_game_artifact() 的 React 学生运行时，禁止回退到旧 Template_MusicGame 页面。"
        )
    if not _is_music_game_playable_tool(spec):
        return False
    if str(spec.get("artifact_generation_mode") or "") == "freeform":
        return False

    playable = spec.get("music_game", {}).get("playable_game", {})
    materials = playable.get("materials", []) if isinstance(playable, dict) else []
    target_sequence = playable.get("target_sequence", []) if isinstance(playable, dict) else []
    html_text = index_path.read_text(encoding="utf-8") if index_path.exists() else ""
    visible_text = _visible_text_for_contract(html_text)
    local_renderer_markers = [
        "function renderMusicGame()",
        "function renderPlayableMusicMission",
        'data-playable-mission="true"',
        'id="play-target-sequence"',
        'id="play-my-sequence"',
        'id="check-playable-sequence"',
        'id="reset-playable-sequence"',
        "class PlayableMusicMission",
        "new PlayableMusicMission(root)",
        'data-lesson-panel="true"',
        "本关任务",
    ]
    visible_control_markers = [
        "试听目标",
        "试听我的排列",
        "检查挑战",
        "重来",
    ]
    material_labels = [
        str(item.get("label", "")).strip()
        for item in materials
        if isinstance(item, dict) and str(item.get("label", "")).strip()
    ]
    forbidden_visible_text = ["是否服务于", "是否真正聚焦", "不是泛泛", "脱离教案单独玩游戏"]
    has_local_renderer = all(marker in html_text for marker in local_renderer_markers)
    has_visible_controls = all(marker in visible_text for marker in visible_control_markers)
    has_contract = has_local_renderer or has_visible_controls
    has_student_brief = "本关任务" in visible_text or 'data-lesson-panel="true"' in html_text
    has_materials = all(label in html_text for label in material_labels[:6])
    has_target = bool(target_sequence) and any(str(item) in html_text for item in target_sequence)
    leaks_meta_text = any(text in visible_text for text in forbidden_visible_text)
    needs_timbre_lab = _is_timbre_game(spec)
    has_timbre_lab = 'data-timbre-lab="true"' in html_text and "试听音色" in visible_text
    if has_contract and has_student_brief and has_materials and has_target and not leaks_meta_text and (not needs_timbre_lab or has_timbre_lab):
        return False

    index_path.write_text(_render_html(spec), encoding="utf-8")
    return True


def _visible_text_for_contract(html_text: str) -> str:
    """Approximate student-visible text so script templates cannot satisfy checks alone."""
    import re

    visible = re.sub(r"<script\b[^>]*>.*?</script>", " ", html_text, flags=re.I | re.S)
    visible = re.sub(r"<style\b[^>]*>.*?</style>", " ", visible, flags=re.I | re.S)
    visible = re.sub(r"<[^>]+>", " ", visible)
    return " ".join(html.unescape(visible).split())


def _is_listening_tool(spec: dict) -> bool:
    return (
        spec.get("activity_type") == "listening"
        or spec.get("template_id") in {"Template_Listen", "Blueprint_Listen"}
        or spec.get("interaction_model", {}).get("primary") == "element_transform_lab"
    )


def _is_music_game_playable_tool(spec: dict) -> bool:
    game = spec.get("music_game", {}) if isinstance(spec.get("music_game"), dict) else {}
    playable = game.get("playable_game", {}) if isinstance(game.get("playable_game"), dict) else {}
    return (
        spec.get("activity_type") == "music_game"
        and bool(game.get("enabled"))
        and bool(playable.get("materials"))
        and bool(playable.get("target_sequence"))
    )


def _is_timbre_game(spec: dict) -> bool:
    game = spec.get("music_game", {}) if isinstance(spec.get("music_game"), dict) else {}
    playable = game.get("playable_game", {}) if isinstance(game.get("playable_game"), dict) else {}
    haystack = " ".join(
        [
            str(game.get("game_type", "")),
            str(game.get("game_name", "")),
            str(game.get("music_concept", "")),
            str(spec.get("target_music_element", "")),
            json.dumps(game.get("rules", []), ensure_ascii=False),
            json.dumps(playable.get("materials", []), ensure_ascii=False),
        ]
    )
    return any(token in haystack for token in ["音色", "乐器", "清脆", "柔和", "打击", "timbre"])


def _assert_not_production_music_game_legacy_route(spec: dict) -> None:
    template_id = _production_music_game_template_id(spec)
    if not template_id:
        return
    raise RuntimeError(
        f"{template_id} 是已升级的成熟音乐游戏模板，必须走 render_template_game_artifact() "
        "并输出 React/Phaser 学生运行时；旧 webpage_generator/Template_MusicGame 链路已禁用。"
    )


def _production_music_game_template_id(spec: dict) -> str:
    if not isinstance(spec, dict):
        return ""
    candidates: list[object] = [
        spec.get("template_id"),
        spec.get("matched_template_id"),
        spec.get("blueprint_id"),
    ]
    music_game = spec.get("music_game", {}) if isinstance(spec.get("music_game"), dict) else {}
    candidates.extend(
        [
            music_game.get("template_id"),
            music_game.get("matched_template_id"),
            music_game.get("blueprint_id"),
        ]
    )
    template_workflow = spec.get("template_workflow", {}) if isinstance(spec.get("template_workflow"), dict) else {}
    instance = template_workflow.get("instance", {}) if isinstance(template_workflow.get("instance"), dict) else {}
    config = instance.get("config", {}) if isinstance(instance.get("config"), dict) else {}
    proposal_card = (
        template_workflow.get("proposal_card", {})
        if isinstance(template_workflow.get("proposal_card"), dict)
        else {}
    )
    template_match = (
        template_workflow.get("template_match", {})
        if isinstance(template_workflow.get("template_match"), dict)
        else {}
    )
    candidates.extend(
        [
            instance.get("template_id"),
            config.get("template_id"),
            proposal_card.get("template_id"),
            template_match.get("template_id"),
        ]
    )
    for candidate in candidates:
        template_id = str(candidate or "").strip()
        if template_id in PRODUCTION_MUSIC_GAME_TEMPLATE_IDS:
            return template_id
    return ""


def _has_new_student_runtime(html_text: str) -> bool:
    return all(marker in html_text for marker in NEW_STUDENT_RUNTIME_MARKERS)


def _render_html(spec: dict) -> str:
    _assert_not_production_music_game_legacy_route(spec)
    safe_spec = json.dumps(spec, ensure_ascii=False).replace("</", "<\\/")
    title = html.escape(spec["title"])
    subtitle = html.escape(_short_student_text(spec.get("subtitle", ""), 42))
    template_id = html.escape(spec.get("template_id", "Music-Gen Creator"))
    template_role = html.escape(spec.get("template_role", "activity_blueprint"))

    template = """<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>__TITLE__</title>
    <style>
      :root {
        --paper: #fff8df;
        --ink: #26324f;
        --muted: #637092;
        --mint: #23bf9f;
        --coral: #ff8f6a;
        --sun: #ffd45f;
        --rose: #ff8fbd;
        --sky: #88d8ff;
        --violet: #6d6af6;
        --line: rgba(35, 48, 79, 0.14);
        --shadow: 0 24px 70px rgba(56, 76, 118, 0.16);
      }

      * {
        box-sizing: border-box;
      }

      body {
        margin: 0;
        min-height: 100vh;
        font-family: "Comic Sans MS", "Marker Felt", "PingFang SC", "Noto Sans SC", sans-serif;
        color: var(--ink);
        background:
          radial-gradient(circle at 8% 14%, rgba(255, 143, 189, 0.38), transparent 24%),
          radial-gradient(circle at 86% 10%, rgba(136, 216, 255, 0.52), transparent 24%),
          radial-gradient(circle at 82% 88%, rgba(255, 212, 95, 0.42), transparent 28%),
          linear-gradient(135deg, #fff8df, #dff8ff 58%, #fff0da);
      }

      body::before,
      body::after {
        content: "";
        position: fixed;
        z-index: -1;
        border-radius: 45% 55% 64% 36%;
        background: rgba(255, 255, 255, 0.34);
        animation: drift 8s ease-in-out infinite;
      }

      body::before {
        width: 180px;
        height: 180px;
        left: 4vw;
        bottom: 8vh;
      }

      body::after {
        width: 230px;
        height: 230px;
        right: 7vw;
        top: 9vh;
        animation-delay: -3s;
      }

      .shell {
        width: min(1280px, calc(100% - 20px));
        margin: 0 auto;
        padding: 18px 0 36px;
      }

      .hero,
      .panel {
        border: 2px solid rgba(255, 255, 255, 0.76);
        border-radius: 34px;
        background: rgba(255, 252, 244, 0.84);
        box-shadow: var(--shadow);
        backdrop-filter: blur(16px);
      }

      .hero {
        display: grid;
        grid-template-columns: minmax(0, 1fr) auto;
        gap: 16px;
        align-items: center;
        padding: 22px;
        margin-bottom: 14px;
        overflow: hidden;
      }

      .orbit {
        width: 132px;
        height: 132px;
        border-radius: 44% 56% 50% 50%;
        background: linear-gradient(145deg, #ffffff, #dff5ff);
        box-shadow: inset -12px -14px rgba(136, 216, 255, 0.35), 0 18px 38px rgba(56, 76, 118, 0.14);
        display: grid;
        place-items: center;
        font-size: 3rem;
        font-weight: 900;
        color: var(--violet);
        animation: bob 3.4s ease-in-out infinite;
      }

      .eyebrow {
        margin: 0 0 10px;
        color: var(--violet);
        font-weight: 900;
        letter-spacing: 0.1em;
        text-transform: uppercase;
      }

      h1 {
        max-width: 13ch;
        margin: 0;
        font-size: clamp(2rem, 5vw, 4rem);
        line-height: 0.98;
      }

      h2,
      h3 {
        margin: 0 0 12px;
      }

      p,
      li {
        color: var(--muted);
        line-height: 1.48;
      }

      button,
      input,
      select {
        font: inherit;
      }

      button,
      .pill {
        border: 0;
        border-radius: 999px;
        font-weight: 900;
      }

      button {
        min-height: 56px;
        padding: 14px 20px;
        color: white;
        background: linear-gradient(135deg, var(--rose), var(--violet));
        cursor: pointer;
        font-size: 1.02rem;
        transition: transform 0.18s ease, box-shadow 0.18s ease;
        box-shadow: 0 12px 24px rgba(109, 106, 246, 0.22);
      }

      button:hover {
        transform: translateY(-2px) rotate(-1deg);
      }

      button:disabled {
        cursor: not-allowed;
        opacity: 0.5;
        transform: none;
      }

      input,
      select {
        width: 100%;
        border: 2px solid rgba(109, 106, 246, 0.14);
        border-radius: 999px;
        padding: 12px 14px;
        color: var(--ink);
        background: white;
      }

      label {
        display: grid;
        gap: 8px;
        color: var(--muted);
        font-weight: 800;
      }

      .panel {
        padding: 26px;
        margin-top: 14px;
      }

      .tag-row,
      .button-row {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        align-items: center;
      }

      .pill {
        display: inline-flex;
        padding: 8px 12px;
        color: var(--violet);
        background: rgba(109, 106, 246, 0.1);
      }

      .form-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 14px;
        align-items: end;
      }

      .status-card,
      .drop-zone,
      .composition-card {
        min-height: 138px;
        border: 2px dashed rgba(109, 106, 246, 0.24);
        border-radius: 24px;
        padding: 20px;
        background: rgba(255, 255, 255, 0.62);
      }

      .result-actions {
        margin-top: 12px;
      }

      .lesson-brief {
        display: grid;
        gap: 14px;
      }

      .lesson-brief-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 12px;
      }

      .lesson-brief-card {
        min-height: 112px;
        padding: 18px;
        border: 2px solid rgba(35, 48, 79, 0.08);
        border-radius: 22px;
        background: linear-gradient(145deg, rgba(255, 255, 255, 0.88), rgba(245, 250, 255, 0.88));
      }

      .lesson-brief-card strong {
        display: block;
        margin-bottom: 8px;
        color: var(--ink);
      }

      .lesson-brief-card p,
      .lesson-brief-card li {
        margin: 0;
      }

      .lesson-brief-list {
        margin: 0;
        padding-left: 18px;
      }

      .levels {
        display: grid;
        gap: 14px;
      }

      .level {
        position: relative;
        display: grid;
        gap: 8px;
        min-height: 132px;
        padding: 18px;
        border: 2px solid rgba(35, 48, 79, 0.08);
        border-radius: 24px;
        background: rgba(255, 255, 255, 0.78);
        transition: transform 0.18s ease, opacity 0.18s ease;
      }

      .level.locked {
        opacity: 0.54;
      }

      .level.complete {
        border-color: rgba(35, 191, 159, 0.45);
        background: linear-gradient(145deg, rgba(236, 255, 249, 0.92), rgba(255, 255, 255, 0.82));
      }

      .level-top {
        display: flex;
        justify-content: space-between;
        gap: 12px;
        align-items: center;
      }

      .badge {
        flex: 0 0 auto;
        padding: 7px 11px;
        border-radius: 999px;
        color: white;
        background: var(--mint);
        font-weight: 900;
      }

      .progress-shell {
        height: 18px;
        overflow: hidden;
        border-radius: 999px;
        background: rgba(109, 106, 246, 0.12);
      }

      .progress-bar {
        height: 100%;
        width: 0%;
        border-radius: inherit;
        background: linear-gradient(90deg, var(--mint), var(--sun), var(--coral));
        transition: width 0.24s ease;
      }

      .quest-shell {
        background:
          radial-gradient(circle at 14% 18%, rgba(255, 212, 95, 0.38), transparent 24%),
          linear-gradient(135deg, rgba(20, 39, 22, 0.96), rgba(49, 79, 56, 0.92));
        color: #fff9e8;
      }

      .quest-shell h2,
      .quest-shell h3,
      .quest-shell p {
        color: inherit;
      }

      .quest-layout {
        display: grid;
        grid-template-columns: minmax(240px, 0.72fr) minmax(0, 1.28fr);
        gap: 16px;
        align-items: start;
      }

      .quest-map {
        display: grid;
        gap: 12px;
      }

      .quest-level-card {
        display: grid;
        gap: 8px;
        padding: 16px;
        border: 1px solid rgba(255, 255, 255, 0.22);
        border-radius: 24px;
        color: #fff9e8;
        background: rgba(255, 255, 255, 0.11);
        text-align: left;
        cursor: pointer;
      }

      .quest-level-card.locked {
        opacity: 0.46;
        cursor: not-allowed;
      }

      .quest-level-card.active {
        border-color: rgba(255, 212, 95, 0.78);
        box-shadow: 0 18px 36px rgba(0, 0, 0, 0.16);
      }

      .quest-level-card.done {
        background: rgba(35, 191, 159, 0.2);
      }

      .quest-panel {
        min-height: 440px;
        padding: 22px;
        border: 1px solid rgba(255, 255, 255, 0.24);
        border-radius: 28px;
        background: rgba(255, 249, 232, 0.13);
        backdrop-filter: blur(12px);
      }

      .quest-pattern,
      .quest-pads,
      .dynamic-ladder {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin: 14px 0;
      }

      .quest-token,
      .quest-pad,
      .dynamic-step {
        min-height: 64px;
        padding: 0 20px;
        border: 0;
        border-radius: 18px;
        color: var(--ink);
        background: #fff9e8;
        font-weight: 900;
        box-shadow: 0 14px 24px rgba(0, 0, 0, 0.16);
      }

      .quest-token {
        display: inline-flex;
        align-items: center;
        box-shadow: none;
      }

      .quest-token.active,
      .quest-pad.hit,
      .dynamic-step.hit {
        background: linear-gradient(135deg, #ffe19a, #f0b84f);
        transform: translateY(-2px);
      }

      .quest-feedback {
        margin-top: 12px;
        padding: 14px;
        border-radius: 20px;
        background: rgba(255, 255, 255, 0.14);
        line-height: 1.7;
      }

      .grid {
        display: grid;
        grid-template-columns: minmax(0, 1fr) minmax(320px, 0.8fr);
        gap: 18px;
      }

      .pieces {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(168px, 1fr));
        gap: 14px;
      }

      .piece {
        min-height: 128px;
        padding: 18px;
        border: 2px solid rgba(35, 48, 79, 0.08);
        border-radius: 20px;
        background: white;
        cursor: grab;
        user-select: none;
      }

      .piece:active {
        cursor: grabbing;
      }

      .drop-zone {
        display: flex;
        align-content: flex-start;
        align-items: flex-start;
        flex-wrap: wrap;
        gap: 10px;
      }

      .drop-zone .piece {
        cursor: pointer;
        background: linear-gradient(145deg, #fffdf4, #effaff);
      }

      .timbre-lab {
        display: grid;
        gap: 12px;
        margin: 14px 0;
        padding: 14px;
        border: 1px solid rgba(35, 48, 79, 0.12);
        border-radius: 18px;
        background: rgba(255, 255, 255, 0.62);
      }

      .timbre-lab h3 {
        margin: 0;
      }

      .timbre-lab p {
        margin: 0;
      }

      .timbre-sample-button {
        min-width: 116px;
      }

      .game-rules {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
        gap: 14px;
      }

      .game-hero {
        display: grid;
        grid-template-columns: minmax(0, 1.15fr) minmax(160px, 0.5fr);
        gap: 16px;
        align-items: center;
        margin-bottom: 12px;
        padding: 20px;
        border-radius: 30px;
        background:
          linear-gradient(110deg, rgba(255, 253, 244, 0.92), rgba(255, 253, 244, 0.7)),
          var(--asset-hero, linear-gradient(145deg, #fffdf4, #effaff));
        background-size: cover;
        background-position: center;
        overflow: hidden;
      }

      .game-hero-copy {
        display: grid;
        gap: 12px;
      }

      .game-subcopy {
        margin: 0;
        font-size: 1.02rem;
      }

      .student-game-brief {
        display: grid;
        grid-template-columns: auto 1fr;
        gap: 12px;
        align-items: start;
        margin: 0 0 14px;
        padding: 14px 16px;
        border-radius: 22px;
        background: linear-gradient(135deg, rgba(255, 248, 222, 0.96), rgba(232, 248, 255, 0.94));
        border: 2px solid rgba(35, 48, 79, 0.08);
        box-shadow: 0 16px 34px rgba(35, 48, 79, 0.08);
      }

      .student-game-brief .brief-orb {
        width: 42px;
        height: 42px;
        display: grid;
        place-items: center;
        border-radius: 16px;
        background: #23304f;
        color: #fff;
        box-shadow: inset 0 -8px 18px rgba(255, 255, 255, 0.16);
      }

      .student-game-brief strong {
        display: block;
        margin-bottom: 3px;
        color: var(--violet);
        font-size: 1rem;
      }

      .student-game-brief p,
      .student-game-brief small,
      .student-game-brief em {
        display: block;
        margin: 0;
      }

      .student-game-brief small {
        margin-top: 4px;
        color: var(--muted);
        font-weight: 800;
      }

      .student-game-brief em {
        margin-top: 4px;
        color: rgba(35, 48, 79, 0.66);
        font-style: normal;
        font-size: 0.9rem;
      }

      .game-steps {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(154px, 1fr));
        gap: 12px;
      }

      .game-step {
        min-height: 92px;
        padding: 14px;
        border-radius: 18px;
        background: rgba(255, 255, 255, 0.86);
        border: 2px solid rgba(35, 48, 79, 0.08);
      }

      .game-step strong {
        display: block;
        margin-bottom: 4px;
        color: var(--violet);
      }

      .game-step p {
        margin: 0;
        font-size: 0.95rem;
      }

      .game-mascot {
        position: relative;
        min-height: 190px;
        border-radius: 28px;
        background:
          radial-gradient(circle at 26% 28%, rgba(255, 255, 255, 0.95), transparent 12%),
          radial-gradient(circle at 74% 26%, rgba(255, 255, 255, 0.85), transparent 10%),
          linear-gradient(160deg, rgba(255, 245, 208, 0.9), rgba(214, 244, 255, 0.95));
        border: 2px solid rgba(255, 255, 255, 0.76);
        overflow: hidden;
      }

      .game-asset-figure {
        display: grid;
        gap: 8px;
        justify-items: center;
        padding: 10px;
        border-radius: 26px;
        background: var(--asset-bg, rgba(255, 255, 255, 0.7));
        border: 2px solid rgba(255, 255, 255, 0.72);
        box-shadow: 0 18px 36px rgba(35, 48, 79, 0.1);
      }

      .game-asset-figure img {
        width: min(100%, 260px);
        aspect-ratio: 16 / 11;
        object-fit: cover;
        border-radius: 20px;
        display: block;
      }

      .game-asset-figure figcaption {
        font-size: 0.85rem;
        font-weight: 900;
        color: var(--asset-accent, var(--violet));
      }

      .game-mascot::before,
      .game-mascot::after {
        content: "";
        position: absolute;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.78);
      }

      .game-mascot::before {
        width: 118px;
        height: 118px;
        left: 50%;
        top: 42px;
        transform: translateX(-50%);
      }

      .game-mascot::after {
        width: 76px;
        height: 76px;
        right: 20px;
        top: 18px;
        background: rgba(255, 212, 95, 0.62);
      }

      .mascot-eye {
        position: absolute;
        top: 92px;
        width: 12px;
        height: 18px;
        border-radius: 999px;
        background: var(--ink);
      }

      .mascot-eye.left {
        left: calc(50% - 22px);
      }

      .mascot-eye.right {
        left: calc(50% + 10px);
      }

      .mascot-smile {
        position: absolute;
        left: 50%;
        top: 116px;
        width: 42px;
        height: 20px;
        border: 4px solid var(--coral);
        border-top: 0;
        border-left-color: transparent;
        border-right-color: transparent;
        border-bottom-left-radius: 26px;
        border-bottom-right-radius: 26px;
        transform: translateX(-50%);
      }

      .mascot-spark {
        position: absolute;
        padding: 6px 10px;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.88);
        color: var(--violet);
        font-weight: 900;
        font-size: 0.9rem;
        box-shadow: 0 10px 20px rgba(35, 48, 79, 0.1);
      }

      .mascot-spark.one {
        left: 14px;
        top: 18px;
      }

      .mascot-spark.two {
        right: 16px;
        bottom: 18px;
      }

      .game-rule-card {
        display: grid;
        gap: 8px;
        min-height: 122px;
        padding: 16px;
        border: 2px solid rgba(35, 48, 79, 0.08);
        border-radius: 22px;
        background: linear-gradient(145deg, #fffdf4, #effaff);
        cursor: grab;
      }

      .game-rule-visual {
        width: 42px;
        height: 42px;
        border-radius: 14px;
        object-fit: cover;
        flex: 0 0 auto;
      }

      .game-rule-card:active {
        cursor: grabbing;
      }

      .playable-mission {
        display: grid;
        gap: 14px;
        margin-top: 14px;
        padding: 20px;
        border-radius: 28px;
        background: linear-gradient(145deg, rgba(255, 253, 244, 0.95), rgba(238, 250, 255, 0.92));
        border: 2px solid rgba(35, 48, 79, 0.08);
      }

      .playable-mission.lower-primary {
        background:
          radial-gradient(circle at 12% 18%, rgba(255, 220, 120, 0.26), transparent 18%),
          radial-gradient(circle at 86% 20%, rgba(120, 208, 255, 0.24), transparent 18%),
          linear-gradient(145deg, rgba(255, 250, 236, 0.98), rgba(234, 248, 255, 0.95));
      }

      .playable-mission[data-playable-variant="pitch"] {
        background: linear-gradient(145deg, rgba(255, 247, 214, 0.96), rgba(233, 247, 255, 0.94));
      }

      .playable-mission[data-playable-variant="rhythm"] {
        background: linear-gradient(145deg, rgba(255, 243, 229, 0.96), rgba(245, 255, 240, 0.94));
      }

      .playable-mission[data-playable-variant="phrase"] {
        background: linear-gradient(145deg, rgba(245, 240, 255, 0.96), rgba(235, 250, 255, 0.94));
      }

      .playable-mission[data-playable-variant="expression"] {
        background: linear-gradient(145deg, rgba(255, 239, 234, 0.96), rgba(255, 251, 233, 0.94));
      }

      .playable-mission[data-playable-variant="timbre"] {
        background: linear-gradient(145deg, rgba(236, 255, 247, 0.96), rgba(240, 247, 255, 0.94));
      }

      .playable-mission[data-playable-variant="pentatonic"] {
        background: linear-gradient(145deg, rgba(255, 249, 231, 0.96), rgba(239, 255, 245, 0.94));
      }

      .playable-variant-head {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        align-items: center;
      }

      .playable-variant-tag,
      .playable-variant-tip {
        display: inline-flex;
        align-items: center;
        padding: 7px 12px;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.82);
        color: var(--ink);
        font-size: 0.9rem;
        font-weight: 900;
      }

      .playable-variant-tip {
        color: var(--muted);
        font-weight: 800;
      }

      .playable-hud {
        display: flex;
        flex-wrap: wrap;
        justify-content: space-between;
        gap: 12px;
        align-items: center;
      }

      .playable-round-badge,
      .playable-hearts,
      .playable-stars {
        display: inline-flex;
        gap: 8px;
        align-items: center;
        padding: 8px 12px;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.84);
        color: var(--ink);
        font-weight: 900;
      }

      .playable-subcopy {
        margin: 0;
        color: var(--muted);
        font-weight: 700;
      }

      .playable-grid {
        display: grid;
        grid-template-columns: minmax(0, 0.86fr) minmax(0, 1.14fr);
        gap: 14px;
      }

      .playable-bank,
      .playable-target {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        min-height: 170px;
        padding: 16px;
        border-radius: 22px;
        background: rgba(255, 255, 255, 0.72);
      }

      .playable-target[data-target-kind="pitch"] {
        background:
          linear-gradient(180deg, rgba(255, 255, 255, 0.82), rgba(255, 236, 198, 0.74)),
          repeating-linear-gradient(180deg, transparent 0 44px, rgba(255, 179, 71, 0.16) 44px 46px);
      }

      .playable-target[data-target-kind="rhythm"] {
        background:
          linear-gradient(180deg, rgba(255, 255, 255, 0.82), rgba(232, 255, 233, 0.74)),
          repeating-linear-gradient(90deg, transparent 0 58px, rgba(89, 193, 139, 0.18) 58px 60px);
      }

      .playable-target[data-target-kind="phrase"] {
        background:
          linear-gradient(180deg, rgba(255, 255, 255, 0.82), rgba(239, 232, 255, 0.74)),
          radial-gradient(circle at 12% 24%, rgba(109, 106, 246, 0.12), transparent 18%);
      }

      .playable-target[data-target-kind="expression"] {
        background:
          linear-gradient(180deg, rgba(255, 255, 255, 0.82), rgba(255, 235, 222, 0.74)),
          repeating-linear-gradient(90deg, transparent 0 66px, rgba(255, 127, 80, 0.15) 66px 68px);
      }

      .playable-target[data-target-kind="timbre"] {
        background:
          linear-gradient(180deg, rgba(255, 255, 255, 0.82), rgba(225, 255, 244, 0.74)),
          radial-gradient(circle at 88% 18%, rgba(74, 182, 255, 0.14), transparent 18%);
      }

      .playable-target[data-target-kind="pentatonic"] {
        background:
          linear-gradient(180deg, rgba(255, 255, 255, 0.82), rgba(248, 252, 216, 0.74)),
          repeating-linear-gradient(90deg, transparent 0 52px, rgba(255, 179, 71, 0.14) 52px 54px);
      }

      .playable-card {
        min-width: 150px;
        min-height: 108px;
        padding: 16px;
        border: 0;
        border-radius: 18px;
        color: var(--ink);
        background: linear-gradient(145deg, #fff8df, #eafff8);
        box-shadow: 0 12px 24px rgba(35, 48, 79, 0.1);
        text-align: left;
        cursor: grab;
      }

      .playable-card.playable-card--sol,
      .playable-card.playable-card--mi {
        min-width: 142px;
        min-height: 118px;
        display: grid;
        gap: 6px;
        align-content: start;
      }

      .playable-card-figure {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 48px;
        height: 48px;
        border-radius: 16px;
        font-size: 0.92rem;
        font-weight: 900;
        color: white;
      }

      .playable-card--sol .playable-card-figure {
        background: linear-gradient(145deg, #ffb347, #ff7f50);
      }

      .playable-card--mi .playable-card-figure {
        background: linear-gradient(145deg, #59c18b, #2f8f68);
      }

      .playable-note-name {
        font-size: 1.2rem;
        letter-spacing: 0.04em;
      }

      .playable-card strong {
        display: block;
      }

      .playable-card small {
        color: var(--muted);
        font-weight: 800;
      }

      .playable-card.active {
        outline: 3px solid rgba(255, 143, 106, 0.55);
      }

      .playable-feedback {
        min-height: 88px;
        padding: 18px;
        border-radius: 20px;
        background: rgba(255, 255, 255, 0.78);
        font-weight: 800;
      }

      .playable-progress {
        width: 100%;
        height: 12px;
        border-radius: 999px;
        background: rgba(109, 106, 246, 0.12);
        overflow: hidden;
      }

      .playable-progress-bar {
        height: 100%;
        width: 0%;
        border-radius: inherit;
        background: linear-gradient(90deg, #ffb347, #59c18b, #4ab6ff);
        transition: width 0.2s ease;
      }

      .game-rule-top {
        display: flex;
        justify-content: space-between;
        gap: 8px;
        align-items: center;
      }

      .game-rule-title {
        font-size: 1rem;
        color: var(--ink);
      }

      .game-rule-badge {
        padding: 6px 10px;
        border-radius: 999px;
        background: rgba(109, 106, 246, 0.12);
        color: var(--violet);
        font-weight: 900;
        font-size: 0.85rem;
        white-space: nowrap;
      }

      .game-rule-tip {
        margin: 0;
        font-size: 0.95rem;
        line-height: 1.5;
      }

      .game-lane {
        display: grid;
        gap: 12px;
        min-height: 260px;
        margin-top: 16px;
        padding: 16px;
        border-radius: 26px;
        background: linear-gradient(90deg, rgba(35, 191, 159, 0.12), rgba(255, 209, 102, 0.2));
      }

      .game-lane-top {
        display: flex;
        justify-content: space-between;
        gap: 12px;
        align-items: center;
        flex-wrap: wrap;
      }

      .game-lane-title {
        margin: 0;
      }

      .game-lane-tip {
        margin: 0;
        padding: 8px 12px;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.82);
        color: var(--muted);
        font-weight: 800;
      }

      .runner-strip {
        position: relative;
        min-height: 110px;
        overflow: hidden;
        border-radius: 20px;
        background: rgba(255, 255, 255, 0.64);
      }

      .runner-token {
        position: absolute;
        left: 8px;
        top: 16px;
        min-width: 92px;
        padding: 10px 12px;
        border-radius: 999px;
        background: white;
        box-shadow: 0 12px 24px rgba(35, 48, 79, 0.12);
        transition: transform var(--race-duration, 1.2s) linear;
      }

      .runner-token.running {
        transform: translateX(min(680px, 64vw));
      }

      .compact-note {
        margin: 0;
        font-size: 0.95rem;
      }

      .happy-note {
        color: var(--violet);
        font-weight: 900;
      }

      .melody-board {
        margin-top: 18px;
        display: grid;
        gap: 12px;
      }

      .melody-toolbar {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 12px;
        align-items: end;
      }

      .melody-toolbar p {
        margin: 0;
        padding: 12px 14px;
        border-radius: 18px;
        background: rgba(109, 106, 246, 0.08);
      }

      .melody-canvas {
        width: 100%;
        height: 420px;
        border: 2px solid rgba(35, 48, 79, 0.1);
        border-radius: 24px;
        background: linear-gradient(145deg, #fffdf6, #effaff);
        cursor: crosshair;
        touch-action: none;
      }

      @keyframes bob {
        0%,
        100% {
          transform: translateY(0) rotate(-2deg);
        }
        50% {
          transform: translateY(-10px) rotate(2deg);
        }
      }

      @keyframes drift {
        0%,
        100% {
          transform: translate3d(0, 0, 0) rotate(0);
        }
        50% {
          transform: translate3d(0, -18px, 0) rotate(9deg);
        }
      }

      @media (max-width: 880px) {
        .hero,
        .grid,
        .form-grid,
        .game-hero,
        .quest-layout,
        .playable-grid,
        .melody-toolbar {
          grid-template-columns: 1fr;
        }

        .orbit {
          width: 120px;
          height: 120px;
          font-size: 2.2rem;
        }
      }
    </style>
  </head>
  <body>
    <main class="shell">
      <section class="hero">
        <div>
          <p class="eyebrow">__TEMPLATE_ID__ · __TEMPLATE_ROLE__</p>
          <h1>__TITLE__</h1>
          <p>__SUBTITLE__</p>
          <div id="skill-tags" class="tag-row"></div>
        </div>
        <div class="orbit" aria-hidden="true">♪</div>
      </section>

      <div id="app"></div>

      <section class="panel" id="teacher-panel">
        <h2>教师提示</h2>
        <ul id="teacher-notes"></ul>
      </section>
    </main>

    <script src="/runtime-assets/soundfont-player/soundfont-player.js"></script>
    <script>
      (() => {
        if (window.__musicAgentAudioGuardVersion >= 2) return;
        window.__musicAgentAudioGuardInstalled = true;
        window.__musicAgentAudioGuardVersion = 2;

        const NativeAudioContext = window.AudioContext || window.webkitAudioContext;
        const trackedContexts = new Set();
        const resetCallbacks = new Set();
        let wakeInFlight = null;

        function trackContext(context) {
          if (!context || trackedContexts.has(context)) return context;
          trackedContexts.add(context);
          context.addEventListener?.("statechange", () => {
            if (context.state === "closed") {
              trackedContexts.delete(context);
              resetCallbacks.forEach((callback) => {
                try {
                  callback(context);
                } catch (error) {
                  console.warn("Audio reset callback failed.", error);
                }
              });
            }
          });
          return context;
        }

        async function wakeTrackedContexts(reason = "playback") {
          if (!trackedContexts.size) return;
          const tasks = [];
          trackedContexts.forEach((context) => {
            if (!context) return;
            if (context.state === "closed") {
              trackedContexts.delete(context);
              resetCallbacks.forEach((callback) => {
                try {
                  callback(context);
                } catch (error) {
                  console.warn("Audio reset callback failed.", error);
                }
              });
              return;
            }
            if (context.state === "suspended") {
              tasks.push(
                context.resume().catch((error) => {
                  console.warn(`AudioContext resume failed during ${reason}.`, error);
                })
              );
            }
          });
          if (tasks.length) {
            await Promise.all(tasks);
          }
        }

        function scheduleWake(reason) {
          if (!wakeInFlight) {
            wakeInFlight = wakeTrackedContexts(reason).finally(() => {
              wakeInFlight = null;
            });
          }
          return wakeInFlight;
        }

        window.__musicAgentAudioGuard = window.__musicAgentAudioGuard || {};
        window.__musicAgentAudioGuard.wake = scheduleWake;
        window.__musicAgentAudioGuard.trackContext = trackContext;
        window.__musicAgentAudioGuard.onReset = (callback) => {
          if (typeof callback === "function") {
            resetCallbacks.add(callback);
          }
        };

        if (NativeAudioContext && !window.__musicAgentAudioContextWrapped) {
          window.__musicAgentAudioContextWrapped = true;
          const WrappedAudioContext = new Proxy(NativeAudioContext, {
            construct(target, args, newTarget) {
              const context = Reflect.construct(target, args, newTarget || target);
              return trackContext(context);
            },
          });
          WrappedAudioContext.prototype = NativeAudioContext.prototype;
          try {
            Object.defineProperty(WrappedAudioContext, "name", { value: NativeAudioContext.name });
          } catch (_error) {}
          window.AudioContext = WrappedAudioContext;
          if (window.webkitAudioContext) {
            window.webkitAudioContext = WrappedAudioContext;
          }
        }

        if (!window.__musicAgentMediaPlayWrapped && window.HTMLMediaElement?.prototype?.play) {
          window.__musicAgentMediaPlayWrapped = true;
          const nativePlay = window.HTMLMediaElement.prototype.play;
          window.HTMLMediaElement.prototype.play = function playWithWake(...args) {
            return Promise.resolve(scheduleWake("media-play")).catch(() => {}).then(() => nativePlay.apply(this, args));
          };
        }

        const wake = () => {
          scheduleWake("gesture").catch(() => {});
        };
        ["pointerdown", "pointerup", "touchstart", "touchend", "mousedown", "keydown", "click"].forEach((eventName) => {
          document.addEventListener(eventName, wake, { passive: true, capture: true });
        });
        document.addEventListener("visibilitychange", () => {
          if (document.visibilityState === "visible") {
            scheduleWake("visibilitychange").catch(() => {});
          }
        });
        window.addEventListener("focus", () => {
          scheduleWake("window-focus").catch(() => {});
        });
        window.addEventListener("pageshow", () => {
          scheduleWake("pageshow").catch(() => {});
        });

        function wrapSoundfontPlayer(player, context) {
          if (!player || player.__musicAgentWrapped) return player;
          player.__musicAgentWrapped = true;
          player.__musicAgentAudioContext = context || null;
          if (typeof player.play === "function") {
            const nativePlay = player.play.bind(player);
            player.play = function playWithAudioWake(...args) {
              const activeContext = player.__musicAgentAudioContext || context;
              if (activeContext?.state === "closed") {
                throw new Error("SoundFont player is bound to a closed AudioContext");
              }
              scheduleWake("soundfont-play").catch(() => {});
              if (activeContext?.state === "suspended") {
                try {
                  activeContext.resume?.();
                } catch (_error) {}
              }
              return nativePlay(...args);
            };
          }
          return player;
        }

        function installSoundfontInstrumentGuard() {
          if (!window.Soundfont || window.Soundfont.__musicAgentInstrumentWrapped) return;
          const nativeInstrument = window.Soundfont.instrument;
          if (typeof nativeInstrument !== "function") return;
          window.Soundfont.__musicAgentInstrumentWrapped = true;
          window.Soundfont.instrument = function instrumentWithAudioWake(context, name, options) {
            if (context) trackContext(context);
            return Promise.resolve(scheduleWake("soundfont-load"))
              .catch(() => {})
              .then(() => nativeInstrument.call(this, context, name, options))
              .then((player) => wrapSoundfontPlayer(player, context));
          };
        }

        installSoundfontInstrumentGuard();
        document.addEventListener("DOMContentLoaded", installSoundfontInstrumentGuard);
        window.addEventListener("load", installSoundfontInstrumentGuard);
        const soundfontGuardTimer = window.setInterval(() => {
          installSoundfontInstrumentGuard();
          if (window.Soundfont?.__musicAgentInstrumentWrapped) {
            window.clearInterval(soundfontGuardTimer);
          }
        }, 250);
        window.setTimeout(() => window.clearInterval(soundfontGuardTimer), 8000);
      })();
    </script>
    <script>
      if (!window.Soundfont) {
        const fallbackScript = document.createElement("script");
        fallbackScript.src = "/static/assets/soundfont-player/soundfont-player.js";
        document.head.appendChild(fallbackScript);
      }
    </script>
    <script>
      const spec = __SPEC__;
      const app = document.querySelector("#app");
      const skillTags = document.querySelector("#skill-tags");
      const teacherNotes = document.querySelector("#teacher-notes");
      const teacherPanel = document.querySelector("#teacher-panel");

      const modeOptions = [
        ["preserve", "保持原调式"],
        ["western_major", "西洋大调"],
        ["western_minor", "西洋小调"],
        ["chinese_pentatonic", "中国五声调式"],
        ["chinese_heptatonic", "中国七声调式"],
        ["dorian", "多利亚"],
        ["phrygian", "弗里吉亚"],
        ["blues", "布鲁斯"],
      ];

      const instrumentOptions = [
        ["preserve", "保持原音色"],
        ["piano", "钢琴"],
        ["violin", "小提琴"],
        ["guzheng", "古筝"],
        ["flute", "长笛"],
      ];

      const pitchToMidi = {
        "do": 60,
        "re": 62,
        "mi": 64,
        "fa": 65,
        "sol": 67,
        "la": 69,
        "ti": 71,
        "宫": 60,
        "商": 62,
        "角": 64,
        "徵": 67,
        "羽": 69,
        "1": 60,
        "2": 62,
        "b3": 63,
        "3": 64,
        "4": 65,
        "#4": 66,
        "5": 67,
        "6": 69,
        "b7": 70,
        "7": 71,
      };

      let audioContext = null;
      let activeClipAudio = null;
      let latestPlayback = null;
      let latestInstrument = spec.listening?.instrument || "preserve";
      let audioActivationInstalled = false;
      let audioResumeInFlight = null;

      function escapeText(value) {
        return String(value ?? "")
          .replaceAll("&", "&amp;")
          .replaceAll("<", "&lt;")
          .replaceAll(">", "&gt;")
          .replaceAll('"', "&quot;")
          .replaceAll("'", "&#039;");
      }

      function getOrCreateAudioContext() {
        if (!audioContext) {
          const AudioContextCtor = window.AudioContext || window.webkitAudioContext;
          if (!AudioContextCtor) {
            throw new Error("AudioContext unavailable");
          }
          audioContext = new AudioContextCtor();
          window.__musicAgentAudioGuard?.trackContext?.(audioContext);
          window.__musicAgentAudioGuard?.onReset?.(() => {
            soundfontCache.clear();
          });
        }
        return audioContext;
      }

      async function resumeAudioContext(reason = "playback") {
        const context = getOrCreateAudioContext();
        if (context.state === "closed") {
          audioContext = null;
          soundfontCache.clear();
          return resumeAudioContext(reason);
        }
        if (context.state !== "suspended") {
          return context;
        }
        if (!audioResumeInFlight) {
          audioResumeInFlight = context.resume()
            .catch((error) => {
              console.warn(`AudioContext resume failed during ${reason}.`, error);
              throw error;
            })
            .finally(() => {
              audioResumeInFlight = null;
            });
        }
        await audioResumeInFlight;
        return getOrCreateAudioContext();
      }

      async function ensureAudioReady(reason = "playback") {
        const context = getOrCreateAudioContext();
        if (context.state === "running") {
          return context;
        }
        return resumeAudioContext(reason);
      }

      async function primeMediaElementPlayback(audio, reason = "media") {
        try {
          await ensureAudioReady(reason);
        } catch (_error) {}
        audio.muted = false;
        audio.autoplay = false;
        audio.playsInline = true;
        const started = audio.play();
        if (started && typeof started.then === "function") {
          await started;
        }
      }

      async function playManagedAudioElement(audio, reason = "media") {
        if (!audio) return false;
        if (activeClipAudio && activeClipAudio !== audio) {
          try {
            activeClipAudio.pause();
            activeClipAudio.currentTime = 0;
          } catch (_error) {}
        }
        activeClipAudio = audio;
        try {
          audio.pause();
          audio.currentTime = 0;
        } catch (_error) {}
        try {
          await primeMediaElementPlayback(audio, reason);
          return true;
        } catch (error) {
          console.warn(`Managed audio playback failed during ${reason}.`, error);
          return false;
        }
      }

      function installAudioActivationHooks() {
        if (audioActivationInstalled) return;
        audioActivationInstalled = true;
        const wakeAudio = () => {
          resumeAudioContext("gesture").catch(() => {});
        };
        ["pointerdown", "pointerup", "touchstart", "touchend", "mousedown", "keydown", "click"].forEach((eventName) => {
          document.addEventListener(eventName, wakeAudio, { passive: true, capture: true });
        });
        document.addEventListener("visibilitychange", () => {
          if (document.visibilityState === "visible") {
            resumeAudioContext("visibilitychange").catch(() => {});
          }
        });
        window.addEventListener("focus", () => {
          resumeAudioContext("window-focus").catch(() => {});
        });
        window.addEventListener("pageshow", () => {
          resumeAudioContext("pageshow").catch(() => {});
        });
      }

      function optionList(options, selected) {
        return options
          .map(([value, label]) => `<option value="${escapeText(value)}" ${value === selected ? "selected" : ""}>${escapeText(label)}</option>`)
          .join("");
      }

      function renderChrome() {
        skillTags.innerHTML = friendlyTagList().map((item) => `<span class="pill">${escapeText(item)}</span>`).join("");
        const notes = compactTeacherNotes();
        teacherNotes.innerHTML = notes.map((note) => `<li>${escapeText(note)}</li>`).join("");
        if (teacherPanel) {
          const hideTeacherPanel = Boolean(spec.lesson_context) && Boolean(spec.music_game?.enabled);
          teacherPanel.style.display = hideTeacherPanel || !notes.length ? "none" : "";
        }
      }

      function renderLessonBrief() {
        if (!spec.lesson_context) return "";
        const context = spec.lesson_context;
        const assessmentClosure = spec.assessment_closure || context.assessment_closure || "";
        const segmentTask = spec.target_segment_task || context.target_segment_task || "";
        const gameablePoint = spec.target_segment_gameable_point || context.target_segment_gameable_point || "";
        return `
          <section class="panel lesson-brief" data-lesson-panel="true">
            <h2>本关任务</h2>
            <div class="lesson-brief-grid">
              <article class="lesson-brief-card">
                <strong>练习什么</strong>
                <p>${escapeText(spec.target_music_element || context.target_music_element || "综合音乐感知")}</p>
              </article>
              <article class="lesson-brief-card">
                <strong>怎么做</strong>
                <p>${escapeText(shortText(segmentTask || gameablePoint || "看规则卡，排好顺序，再点开始。", 32))}</p>
              </article>
              <article class="lesson-brief-card">
                <strong>完成后</strong>
                <p>${escapeText(shortText(assessmentClosure || "说一说你听到了什么音乐变化。", 28))}</p>
              </article>
            </div>
          </section>
        `;
      }

      function renderListening() {
        if (!spec.listening?.enabled) return "";
        return `
          <section class="panel" data-template="Template_Listen">
            <h2>聆听调音台</h2>
            <p>${escapeText(shortText(spec.listening.task || "上传后马上对比。", 28))}</p>
            <form id="listening-form" class="form-grid" data-component="element_control_panel">
              <label>上传课堂音频<input type="file" name="audio" accept="audio/*" required /></label>
              <label>同主音<select name="tonic">${["C","D","E","F","G","A","B"].map((tonic) => `<option ${tonic === spec.listening.tonic ? "selected" : ""}>${tonic}</option>`).join("")}</select></label>
              <label>大小调 / 调式转换<select name="mode"><option value="preserve" selected>保持原调式</option>${modeOptions.filter(([value]) => value !== "preserve").map(([value, label]) => `<option value="${escapeText(value)}">${escapeText(label)}</option>`).join("")}</select></label>
              <label>BPM / 速度倍率<input type="number" name="tempo_multiplier" min="0.5" max="2" step="0.1" value="1.0" /></label>
              <label>节奏密度<select name="rhythm_density"><option value="preserve" selected>保持原节奏</option><option value="dense">更密集</option><option value="relaxed">更舒缓</option></select></label>
              <label>音色切换<select name="instrument"><option value="preserve" selected>保持原音色</option>${instrumentOptions.filter(([value]) => value !== "preserve").map(([value, label]) => `<option value="${escapeText(value)}">${escapeText(label)}</option>`).join("")}</select></label>
              <button type="submit">生成对比版本</button>
            </form>
            <div id="listening-result" class="status-card">上传音频，马上对比。</div>
          </section>
        `;
      }

      function renderPerformance() {
        if (!spec.performance?.enabled) return "";
        if (spec.performance.template_variant === "immersive_rhythm_mountain") return renderImmersivePerformance();
        return `
          <section class="panel" data-template="Template_Performance">
            <h2>表现训练：${escapeText(spec.performance.theme)}</h2>
            <p>${escapeText(shortText(spec.performance.target_skill || "完成逐关表现挑战。", 28))}</p>
            <div class="progress-shell" aria-label="通关进度"><div id="level-progress" class="progress-bar"></div></div>
            <p id="level-status" class="happy-note"></p>
            <div id="levels" class="levels">
              ${(spec.performance.levels || []).map((level, index) => `
                <article class="level" data-level-index="${index}">
                  <div class="level-top">
                    <h3>${index + 1}. ${escapeText(level.title)}</h3>
                    <span class="badge">未解锁</span>
                  </div>
                  <p><strong>目标：</strong>${escapeText(shortText(level.goal, 22))}</p>
                  <p><strong>任务：</strong>${escapeText(shortText(level.student_task, 26))}</p>
                  <p><strong>通关：</strong>${escapeText(shortText(level.success_rule, 24))}</p>
                  <button type="button" class="complete-level">完成本关</button>
                </article>
              `).join("")}
            </div>
          </section>
        `;
      }

      function renderImmersivePerformance() {
        const perf = spec.performance;
        const levels = perf.levels || [];
        return `
          <section class="panel quest-shell" data-template="Template_Performance" data-performance-template="immersive_rhythm_mountain">
            <h2>${escapeText(perf.template_label || "沉浸式节奏闯关")}</h2>
            <p>${escapeText(shortText(perf.target_skill || "完成逐关表现挑战。", 28))}</p>
            <div class="progress-shell" aria-label="通关进度"><div id="level-progress" class="progress-bar"></div></div>
            <p id="level-status" class="happy-note"></p>
            <div class="quest-layout">
              <div class="quest-map" id="quest-map">
                ${levels.map((level, index) => renderQuestLevelCard(level, index)).join("")}
              </div>
              <div class="quest-panel" id="quest-panel"></div>
            </div>
          </section>
        `;
      }

      function renderQuestLevelCard(level, index) {
        return `
          <button class="quest-level-card" type="button" data-level-index="${index}">
            <span class="badge">第 ${index + 1} 关</span>
            <strong>${escapeText(level.title || `第 ${index + 1} 关`)}</strong>
            <span>${escapeText(shortText(level.goal || level.student_task || "完成表现挑战。", 38))}</span>
          </button>
        `;
      }

	      function renderCreation() {
	        if (!spec.creation?.enabled) return "";
	        return `
	          <section class="panel" data-template="Template_Creation">
	            <h2>创意活动：${creationModeLabel(spec.creation.creation_mode)}</h2>
	              <p>${escapeText(spec.creation.bars)} 小节，把素材拼成音乐。</p>
	              ${renderMusicContractChips()}
	            <div class="grid">
              <div>
                <h3>素材仓库</h3>
                <div id="pieces" class="pieces">
                  ${(spec.creation.pieces || []).map((piece, index) => renderPiece(piece, index)).join("")}
                </div>
              </div>
              <div>
                <h3>作品区</h3>
                  <div id="drop-zone" class="drop-zone">拖进来，拼作品。</div>
                <div class="button-row result-actions">
                  <label>拼图音色
                    <select id="composition-instrument">${soundfontInstrumentOptions("acoustic_grand_piano")}</select>
                  </label>
                  <label>演奏方式
                    <select id="composition-articulation">${articulationOptions("natural")}</select>
                  </label>
                  <button id="play-composition" type="button">试听作品雏形</button>
                  <button id="clear-composition" type="button">清空作品区</button>
                </div>
                <div id="composition-feedback" class="composition-card">拼好后，说一个亮点。</div>
              </div>
            </div>
            <div class="melody-board">
              <h3>网格旋律线</h3>
              <p>点格子画旋律，再试听。</p>
              <div class="melody-toolbar">
                <label>选择调性
                  <select id="melody-key">
                    ${keyOptions(spec.creation?.tonic || "C")}
                  </select>
                </label>
                <label>小节数
                  <select id="melody-bars">
                    ${[2, 4, 6, 8].map((bars) => `<option value="${bars}" ${Number(spec.creation?.bars || 4) === bars ? "selected" : ""}>${bars} 小节</option>`).join("")}
                  </select>
                </label>
                <label>当前声部
                  <select id="melody-voice">
                    <option value="voice1">声部一</option>
                    <option value="voice2">声部二</option>
                  </select>
                </label>
                <label>声部一音色
                  <select id="voice1-instrument">${soundfontInstrumentOptions("acoustic_grand_piano")}</select>
                </label>
                <label>声部二音色
                  <select id="voice2-instrument">${soundfontInstrumentOptions("violin")}</select>
                </label>
                <label>演奏方式
                  <select id="melody-articulation">${articulationOptions("auto")}</select>
                </label>
                <p>选声部，画旋律。</p>
              </div>
              <canvas id="melody-canvas" class="melody-canvas" width="1040" height="420" aria-label="网格旋律线作曲区"></canvas>
              <div class="button-row">
                <button id="play-melody-line" type="button">试听旋律线</button>
                <button id="clear-melody-line" type="button">重画旋律线</button>
              </div>
              <div id="melody-feedback" class="composition-card">画完后，听听像不像乐句。</div>
            </div>
          </section>
	        `;
	      }

	      function renderMusicContractChips() {
	        const tokens = spec.music_logic_contract?.tokens || spec.music_game?.music_logic_contract?.tokens || [];
	        if (!tokens.length) return "";
	        return `
	          <div class="button-row" aria-label="音乐材料表">
	            ${tokens.slice(0, 8).map((token) => {
	              const label = token.label || token.symbol || token.fallback_symbol || token.music_value || token.id || "音乐材料";
	              return `<span class="quest-token" data-material-id="${escapeText(token.id || "")}">${escapeText(label)}</span>`;
	            }).join("")}
	          </div>
	        `;
	      }

      function renderMusicGame() {
        if (!spec.music_game?.enabled) return "";
        const game = spec.music_game;
        const assetPack = game.visual_asset_pack || spec.visual_asset_pack || {};
        const shortGoal = shortText(game.goal || "通过操作和反馈理解音乐规则。", 36);
        const loopSteps = (Array.isArray(game.core_loop) && game.core_loop.length ? game.core_loop : ["选卡片", "排顺序", "点开始"]).slice(0, 5);
        return `
          <section class="panel" data-template="Template_MusicGame" data-game-type="${escapeText(game.game_type || "lesson_mission_game")}" data-game-family="${escapeText(game.game_family || "mission")}" style="--asset-bg:${escapeText(assetPack.background || "#fffdf4")};--asset-accent:${escapeText(assetPack.accent || "#6a4bc3")};--asset-hero:url('${escapeText(assetPack.background_image || assetPack.hero || "")}')">
            <div class="game-hero">
              <div class="game-hero-copy">
                <h2>${escapeText(game.game_name || "音乐挑战")}</h2>
                <p class="game-subcopy">${escapeText(shortGoal)}</p>
                <div class="game-steps">
                  ${loopSteps.map((step, index) => renderGameLoopStep(step, index)).join("")}
                </div>
              </div>
              ${renderGameAssetFigure(assetPack, game)}
            </div>
            ${renderStudentGameBrief(game, game.playable_game || {})}
            ${renderTimbreLab(game, game.playable_game || {})}
            ${game.playable_game ? renderPlayableMusicMission(game.playable_game) : `
            <div class="game-lane">
              <div class="game-lane-top">
                <h3 class="game-lane-title">挑战区</h3>
                <p class="game-lane-tip">把卡片放进这里</p>
              </div>
              <div id="game-drop-zone" class="drop-zone">点卡片或拖卡片到这里</div>
              <div class="button-row">
                <button id="start-game" type="button">开始挑战</button>
                <button id="reset-game" type="button">重新排列</button>
              </div>
              <div class="runner-strip" id="runner-strip" aria-label="角色动画跑道"></div>
              ${game.progression?.length ? `<div class="tag-row game-progression">${game.progression.map((item) => `<span class="pill">${escapeText(item)}</span>`).join("")}</div>` : ""}
              <div id="game-feedback" class="composition-card">${escapeText(game.win_condition || "完成后说出你的音乐理由。")}</div>
            </div>
            `}
            ${renderGameRulesPanel(game)}
          </section>
        `;
      }

      function renderTimbreLab(game, playable) {
        const conceptText = `${game.game_type || ""} ${game.music_concept || ""} ${game.game_name || ""} ${game.goal || ""} ${(game.rules || []).map((rule) => `${rule.music_element || ""} ${rule.value || ""} ${rule.character || ""}`).join(" ")} ${(playable.materials || []).map((item) => `${item.label || ""} ${item.music_value || ""}`).join(" ")}`;
        if (!/音色|乐器|清脆|柔和|短促|打击|timbre|instrument|detective/.test(conceptText)) return "";
        const samples = [
          ["acoustic_grand_piano", "钢琴", "颗粒清楚，起音干净"],
          ["violin", "小提琴", "线条连贯，声音有拉弦感"],
          ["flute", "长笛", "明亮轻盈，气息感明显"],
          ["koto", "古筝", "拨弦清亮，余音较长"],
          ["xylophone", "木琴", "短促明亮，颗粒感强"],
        ];
        return `
          <div class="timbre-lab" data-timbre-lab="true">
            <h3>试听音色</h3>
            <p>先听，再拖卡片。</p>
            <div class="button-row">
              ${samples.map(([instrument, label, hint]) => `<button class="timbre-sample-button" type="button" data-timbre-sample="${instrument}" data-timbre-hint="${escapeText(hint)}">${escapeText(label)}</button>`).join("")}
            </div>
            <div class="composition-card" id="timbre-feedback">选择一个音色试听。</div>
          </div>
        `;
      }

      function renderStudentGameBrief(game, playable) {
        const songTitle = spec.song_name || spec.lesson_context?.song_name || playable.song_title || "这首歌";
        const targetStage = spec.target_stage || spec.lesson_context?.target_stage || playable.target_stage || "课堂活动";
        const concept = spec.target_music_element || spec.lesson_context?.target_music_element || playable.music_goal || game.music_concept || "音乐线索";
        const segmentTask = spec.target_segment_task || spec.lesson_context?.target_segment_task || game.target_segment_task || "";
        const phraseLabel = spec.song_anchor_contract?.selected_phrase?.label || game.song_anchor_contract?.selected_phrase?.label || "";
        const prompt = playable.prompt || game.mechanic || "先听目标，再完成挑战。";
        const task = playable.student_facing_task || spec.student_facing_task || {};
        const listen = task.listen || `听《${songTitle}》片段`;
        const action = task.do || "拖卡片完成挑战";
        const pass = task.pass || `过关后回到${targetStage}`;
        return `
          <div class="student-game-brief" data-lesson-panel="true">
            <div class="brief-orb">🎧</div>
            <div>
              <strong>本关任务</strong>
              <p>${escapeText(shortText(listen, 18))}，抓“${escapeText(shortText(concept, 10))}”。</p>
              ${segmentTask ? `<small>${escapeText(shortText(segmentTask, 22))}</small>` : ""}
              ${phraseLabel ? `<small>${escapeText(shortText(phraseLabel, 18))}</small>` : ""}
              <small>听：${escapeText(shortText(listen, 12))} ｜ 做：${escapeText(shortText(action, 12))} ｜ 过关：${escapeText(shortText(pass, 12))}</small>
              <em>${escapeText(shortText(prompt, 24))}</em>
            </div>
          </div>
        `;
      }

      function renderGameRulesPanel(game) {
        const rules = (game.rules || []).filter(Boolean).slice(0, game.playable_game ? 2 : 8);
        if (!rules.length) return "";
        if (game.playable_game) {
          const tags = rules.map((rule) => `<span class="pill">${escapeText(shortText(rule.music_element || rule.value || "规则提示", 14))}</span>`).join("");
          return `<div class="tag-row game-rule-strip" id="game-rules">${tags}</div>`;
        }
        const body = rules.map((rule, index) => renderGameRule(rule, index)).join("");
        return `
          <details class="game-rules game-rules-compact" id="game-rules" open>
            <summary>游戏规则</summary>
            <div class="game-rules-body">${body}</div>
          </details>
        `;
      }

      function resolvePlayableVariant(playable, game = spec.music_game || {}) {
        const source = [
          playable?.operation_type || "",
          playable?.music_goal || "",
          game?.game_type || "",
          game?.music_concept || "",
          game?.mechanic || "",
        ].join(" ");
        if (/solmi|pitch|melody|singing_ladder/.test(source)) return "pitch";
        if (/rhythm|note_value|meter|syncopation|dotted|rest/.test(source)) return "rhythm";
        if (/phrase|section|song_phrase|contrast|call_response/.test(source)) return "phrase";
        if (/expression|dynamic|tempo/.test(source)) return "expression";
        if (/timbre|instrument/.test(source)) return "timbre";
        if (/pentatonic|gong|shang|jue|zhi|yu/.test(source)) return "pentatonic";
        return "mission";
      }

      function playableVariantConfig(playable, game = spec.music_game || {}) {
        const variant = resolvePlayableVariant(playable, game);
        const map = {
          pitch: {
            label: "音高闯关",
            tip: "先听音列，再把唱名摆上台阶",
            title: "开始音高挑战",
            bankTitle: "唱名卡",
            targetTitle: "音高台阶",
            placeholder: "把唱名卡拖到音高台阶",
            targetKind: "pitch",
          },
          rhythm: {
            label: "节奏工坊",
            tip: "按拍点把材料排成节奏线",
            title: "开始节奏挑战",
            bankTitle: "节奏材料",
            targetTitle: "节拍跑道",
            placeholder: "按拍点把节奏卡放进跑道",
            targetKind: "rhythm",
          },
          phrase: {
            label: "乐句拼图",
            tip: "重听片段关系，再拼回歌曲结构",
            title: "开始乐句挑战",
            bankTitle: "片段与证据卡",
            targetTitle: "乐句故事板",
            placeholder: "先放片段，再补上对应关系或结构顺序",
            targetKind: "phrase",
          },
          expression: {
            label: "表现变化线",
            tip: "把强弱或快慢排成一条变化线",
            title: "开始表现挑战",
            bankTitle: "表现卡",
            targetTitle: "表现变化线",
            placeholder: "把力度或速度卡排成变化线",
            targetKind: "expression",
          },
          timbre: {
            label: "音色侦探",
            tip: "先试听音色，再连接证据",
            title: "开始音色挑战",
            bankTitle: "音色证据卡",
            targetTitle: "音色证据链",
            placeholder: "把音色线索按听到的顺序连起来",
            targetKind: "timbre",
          },
          pentatonic: {
            label: "五声拼句台",
            tip: "只用五声音级拼出短句",
            title: "开始五声挑战",
            bankTitle: "五声音级卡",
            targetTitle: "五声拼句台",
            placeholder: "把宫商角徵羽拖进拼句台",
            targetKind: "pentatonic",
          },
          mission: {
            label: "课堂任务链",
            tip: "先听线索，再完成任务",
            title: "开始音乐挑战",
            bankTitle: "音乐卡片",
            targetTitle: "挑战区",
            placeholder: "把音乐卡片放到这里",
            targetKind: "mission",
          },
        };
        return { variant, ...(map[variant] || map.mission) };
      }

      function renderPlayableMusicMission(playable) {
        const materials = Array.isArray(playable.materials) ? playable.materials : [];
        const isLowerPrimary = String(playable.age_style || "") === "lower_primary_cartoon";
        const variant = playableVariantConfig(playable);
        const sourcePhraseLabel = playable.source_phrase_label || playable.song_phrase_table?.label || "当前乐句";
        const sourcePhraseAudio = playable.source_phrase_audio_url || "";
        return `
          <div class="playable-mission ${isLowerPrimary ? "lower-primary" : ""}" data-playable-mission="true" data-playable-variant="${escapeText(variant.variant)}">
            <div>
              <div class="playable-variant-head">
                <span class="playable-variant-tag">${escapeText(variant.label)}</span>
                <span class="playable-variant-tip">${escapeText(variant.tip)}</span>
              </div>
              <div class="playable-hud">
                <div class="playable-round-badge" id="playable-round-badge">第 1 关</div>
                <div class="playable-hearts" id="playable-hearts">❤ ❤ ❤</div>
                <div class="playable-stars" id="playable-stars">★ ☆ ☆</div>
              </div>
              <h3>${escapeText(isLowerPrimary ? "唱名闯关" : variant.title)}</h3>
              <p class="playable-subcopy" id="playable-round-prompt">${escapeText(shortText(playable.prompt || "先听，再拖，再检查。", 24))}</p>
            </div>
            <div class="playable-progress" aria-label="闯关进度"><div id="playable-progress-bar" class="playable-progress-bar"></div></div>
            <div class="button-row">
              <button id="play-target-sequence" type="button">试听目标</button>
              <button id="play-my-sequence" type="button">试听我的排列</button>
              <button id="check-playable-sequence" type="button">检查挑战</button>
              <button id="reset-playable-sequence" type="button">重来</button>
            </div>
            ${sourcePhraseAudio ? `
              <div class="playable-source-audio">
                <p>真实片段：${escapeText(sourcePhraseLabel)}</p>
                <audio controls preload="metadata" src="${escapeText(sourcePhraseAudio)}"></audio>
                <p><a href="${escapeText(sourcePhraseAudio)}" download target="_blank" rel="noreferrer">下载这句原音</a></p>
              </div>
            ` : ""}
            <div class="playable-grid">
              <div>
                <h3>${escapeText(isLowerPrimary ? "唱名精灵" : variant.bankTitle)}</h3>
                <div class="playable-bank">
                  ${materials.map((item) => renderPlayableCard(item)).join("")}
                </div>
              </div>
              <div>
                <h3>${escapeText(isLowerPrimary ? "音高台阶" : variant.targetTitle)}</h3>
                <div id="playable-target" class="playable-target" data-target-kind="${escapeText(variant.targetKind)}" data-placeholder="${escapeText(isLowerPrimary ? "拖到台阶上" : variant.placeholder)}">${escapeText(isLowerPrimary ? "拖到台阶上" : variant.placeholder)}</div>
              </div>
            </div>
            <div id="playable-feedback" class="playable-feedback">${escapeText(playable.feedback?.empty || "先把音乐卡片放进挑战区。")}</div>
          </div>
        `;
      }

      function renderPlayableCard(item) {
        const payload = escapeText(JSON.stringify(item || {}));
        const hasAudio = item.audio_clip_url;
        return `
          <button class="playable-card playable-card--${escapeText(item.id || "card")}" type="button" draggable="true" data-playable-card="${payload}">
            ${item.avatar ? `<span class="playable-card-figure">${escapeText(item.avatar)}</span>` : ""}
            <strong class="playable-note-name">${escapeText(item.label || "音乐卡片")}</strong>
                  <small>${escapeText(shortText(item.music_value || "音乐任务", 12))}</small>
            ${hasAudio ? `<span class="audio-badge" title="真实音频">🎵</span>` : ""}
          </button>
        `;
      }

      function renderGameAssetFigure(assetPack, game) {
        const imageSource = assetPack?.component || assetPack?.hero;
        if (imageSource) {
          return `
            <figure class="game-asset-figure">
              <img src="${escapeText(imageSource)}" alt="${escapeText(assetPack.label || game.game_name || "音乐游戏插图")}" />
              <figcaption>${escapeText(assetPack.label || "课堂素材包")}</figcaption>
            </figure>
          `;
        }
        return `
          <div class="game-mascot" aria-hidden="true">
            <span class="mascot-spark one">开始玩</span>
            <span class="mascot-eye left"></span>
            <span class="mascot-eye right"></span>
            <span class="mascot-smile"></span>
            <span class="mascot-spark two">跟着听</span>
          </div>
        `;
      }

      function renderGameLoopStep(step, index) {
        const text = String(step || "完成挑战");
        return `
          <article class="game-step">
            <strong>${index + 1} ${escapeText(shortText(text, 10))}</strong>
            <p>${escapeText(shortText(text, 18))}</p>
          </article>
        `;
      }

      function inferPrimaryActivityFromInteraction() {
        const primary = String(spec.interaction_model?.primary || "");
        if (["element_transform_lab", "listening_quiz_challenge"].includes(primary)) return "listening";
        if (["two_voice_melody_grid", "melody_grid_composer", "melody_continuation_board", "note_fill_blank_puzzle", "drag_drop_music_puzzle"].includes(primary)) {
          return "creation";
        }
        if (["rhythm_tap_challenge", "body_percussion_challenge", "call_response_singing", "level_map_challenge"].includes(primary)) {
          return "performance";
        }
        if (["rhythm_race_game", "rhythm_animal_race", "pitch_flying_game", "melody_path_game", "music_match_game", "timbre_detective_game", "pentatonic_grid_game", "group_relay_game", "expression_control_game", "lesson_mission_game", "custom_music_game"].includes(primary)) {
          return "music_game";
        }
        return "";
      }

      function resolvePrimaryActivityType() {
        const explicitType = String(spec.activity_type || "");
        const enabledMap = {
          listening: Boolean(spec.listening?.enabled),
          performance: Boolean(spec.performance?.enabled),
          creation: Boolean(spec.creation?.enabled),
          music_game: Boolean(spec.music_game?.enabled),
        };

        if (spec.lesson_context) {
          if (enabledMap.music_game) return "music_game";
          if (enabledMap.performance) return "performance";
          if (enabledMap.creation) return "creation";
          if (enabledMap.listening) return "listening";
        }

        if (explicitType && explicitType !== "mixed" && enabledMap[explicitType]) {
          return explicitType;
        }

        const inferred = inferPrimaryActivityFromInteraction();
        if (inferred && enabledMap[inferred]) {
          return inferred;
        }

        for (const key of ["music_game", "performance", "creation", "listening"]) {
          if (enabledMap[key]) return key;
        }
        return explicitType === "mixed" ? "music_game" : explicitType || "music_game";
      }

      function renderMainActivity() {
        const primaryType = resolvePrimaryActivityType();
        if (primaryType === "listening") return renderListening();
        if (primaryType === "performance") return renderPerformance();
        if (primaryType === "creation") return renderCreation();
        return renderMusicGame();
      }

      function renderGameRule(rule, index) {
        const payload = escapeText(JSON.stringify(rule));
        const assetPack = spec.music_game?.visual_asset_pack || spec.visual_asset_pack || {};
        return `
          <article class="game-rule-card" draggable="true" data-rule-index="${index}" data-rule="${payload}">
            <div class="game-rule-top">
              ${assetPack.component || assetPack.badge ? `<img class="game-rule-visual" src="${escapeText(assetPack.component || assetPack.badge)}" alt="" aria-hidden="true" />` : ""}
              <strong class="game-rule-title">${escapeText(rule.character || `角色-${index + 1}`)}</strong>
              <span class="game-rule-badge">${escapeText(rule.value || "规则")}</span>
            </div>
            <p class="compact-note">${escapeText(rule.music_element || "音乐规则")}</p>
            <p class="game-rule-tip">${escapeText(shortText(rule.feedback || rule.motion || "跟着规则完成挑战。", 24))}</p>
          </article>
        `;
      }

      function shortText(value, limit = 24) {
        const text = String(value || "").replace(/\s+/g, " ").trim();
        if (text.length <= limit) return text;
        return `${text.slice(0, limit)}...`;
      }

      function friendlyTagList() {
        if (spec.music_game?.enabled) {
          return [
            spec.target_music_element || spec.music_game.music_concept || "本关练习",
            "可拖拽",
            "可播放",
          ];
        }
        if (spec.creation?.enabled) return ["自己创作", "可试听", "可重画"];
        if (spec.performance?.enabled) return ["逐关挑战", "即时反馈", "继续下一关"];
        if (spec.listening?.enabled) return ["先听一听", "再选答案", "马上对比"];
        return ["音乐课堂", "互动活动", "可操作"];
      }

      function compactTeacherNotes() {
        const notes = (spec.teacher_notes || []).filter((note) => {
          return !/智能体|自检|生成前|曲目重点|学段能力/.test(String(note || ""));
        });
        return notes.slice(0, 2).map((note) => shortText(note, 30));
      }

      function renderPiece(piece, index) {
        const payload = escapeText(JSON.stringify(piece));
        return `
          <article class="piece" draggable="true" data-piece-index="${index}" data-piece="${payload}">
            <strong>${escapeText(piece.id || `素材-${index + 1}`)}</strong>
            <p>音高：${escapeText(shortText(piece.pitch, 10))}</p>
            <p>节奏：${escapeText(shortText(piece.rhythm, 10))}</p>
            <p>功能：${escapeText(shortText(piece.function, 12))}</p>
          </article>
        `;
      }

      function modeLabel(mode) {
        const match = modeOptions.find(([value]) => value === mode);
        return match ? match[1] : mode;
      }

      function keyOptions(selectedKey) {
        return ["C", "D", "E", "F", "G", "A", "B", "Bb", "Eb", "F#", "C#"].map(
          (key) => `<option value="${key}" ${key === selectedKey ? "selected" : ""}>${key} 调</option>`
        ).join("");
      }

      function soundfontInstrumentOptions(selectedInstrument) {
        return [
          ["acoustic_grand_piano", "钢琴"],
          ["violin", "小提琴"],
          ["flute", "长笛"],
          ["koto", "古筝"],
          ["acoustic_guitar_nylon", "尼龙吉他"],
          ["clarinet", "单簧管"],
          ["cello", "大提琴"],
          ["xylophone", "木琴"],
        ].map(([value, label]) => `<option value="${value}" ${value === selectedInstrument ? "selected" : ""}>${label}</option>`).join("");
      }

      function articulationOptions(selectedArticulation) {
        return [
          ["auto", "自动"],
          ["natural", "自然"],
          ["legato", "连奏"],
          ["staccato", "断奏"],
          ["pluck", "拨弦"],
        ].map(([value, label]) => `<option value="${value}" ${value === selectedArticulation ? "selected" : ""}>${label}</option>`).join("");
      }

      function creationModeLabel(mode) {
        return {
          free_assembly: "自由拼装",
          note_fill_blank: "音符填空",
          melody_continuation: "旋律续写",
          rhythm_puzzle: "节奏拼图",
          style_remix: "风格重组",
          melody_grid: "网格旋律线",
        }[mode] || "自由拼装";
      }

      class LevelController {
        constructor(root) {
          this.root = root;
          this.levels = Array.from(root.querySelectorAll(".level"));
          this.progress = root.querySelector("#level-progress");
          this.status = root.querySelector("#level-status");
          this.completed = new Set();
          this.bind();
          this.render();
        }

        bind() {
          this.levels.forEach((level, index) => {
            level.querySelector(".complete-level").addEventListener("click", () => {
              if (!this.isUnlocked(index)) return;
              this.completed.add(index);
              this.render();
            });
          });
        }

        isUnlocked(index) {
          return index === 0 || this.completed.has(index - 1);
        }

        render() {
          this.levels.forEach((level, index) => {
            const done = this.completed.has(index);
            const unlocked = this.isUnlocked(index);
            level.classList.toggle("locked", !unlocked);
            level.classList.toggle("complete", done);
            level.querySelector(".badge").textContent = done ? "已通关" : unlocked ? "挑战中" : "未解锁";
            level.querySelector(".complete-level").disabled = !unlocked || done;
          });

          const percent = this.levels.length ? Math.round((this.completed.size / this.levels.length) * 100) : 0;
          this.progress.style.width = `${percent}%`;
          this.status.textContent = percent === 100 ? "全部通关，可以进入班级展示。" : `已完成 ${this.completed.size}/${this.levels.length} 关。`;
        }
      }

      class PerformanceQuestController {
        constructor(root) {
          this.root = root;
          this.levels = spec.performance?.levels || [];
          this.cards = Array.from(root.querySelectorAll(".quest-level-card"));
          this.panel = root.querySelector("#quest-panel");
          this.progress = root.querySelector("#level-progress");
          this.status = root.querySelector("#level-status");
          this.storageKey = `performanceQuest:${spec.title || "music"}:${spec.performance?.template_id || "default"}`;
          this.completed = new Set(this.readProgress().completed || []);
          this.activeIndex = Math.min(this.levels.length - 1, this.readProgress().unlockedLevel || 0);
          this.inputSequence = [];
          this.expectedSequence = [];
          this.bind();
          this.render();
        }

        readProgress() {
          try {
            const saved = JSON.parse(localStorage.getItem(this.storageKey) || "{}");
            return {
              unlockedLevel: Number(saved.unlockedLevel || 0),
              completed: Array.isArray(saved.completed) ? saved.completed.map(Number) : [],
            };
          } catch (_error) {
            return { unlockedLevel: 0, completed: [] };
          }
        }

        saveProgress() {
          const highestCompleted = Math.max(-1, ...Array.from(this.completed));
          const unlockedLevel = Math.min(this.levels.length - 1, highestCompleted + 1);
          localStorage.setItem(this.storageKey, JSON.stringify({
            unlockedLevel,
            completed: Array.from(this.completed).sort((a, b) => a - b),
          }));
        }

        bind() {
          this.cards.forEach((card, index) => {
            card.addEventListener("click", () => {
              if (!this.isUnlocked(index)) return;
              this.activeIndex = index;
              this.inputSequence = [];
              this.render();
            });
          });

          this.root.addEventListener("click", (event) => {
            const actionTarget = event.target.closest("[data-quest-action]");
            if (!actionTarget) return;
            const action = actionTarget.dataset.questAction;
            if (action === "start") this.startCurrentChallenge();
            if (action === "reset") {
              this.inputSequence = [];
              this.renderPanel("已重置本关，准备好再开始。");
            }
            if (action === "teacher-pass") this.completeLevel(this.activeIndex, "教师已确认本关表现达标。");
            if (action === "input") this.recordInput(actionTarget.dataset.value || "");
          });
        }

        isUnlocked(index) {
          return index === 0 || this.completed.has(index - 1);
        }

        render() {
          this.cards.forEach((card, index) => {
            const done = this.completed.has(index);
            const unlocked = this.isUnlocked(index);
            card.classList.toggle("locked", !unlocked);
            card.classList.toggle("done", done);
            card.classList.toggle("active", index === this.activeIndex);
            const badge = card.querySelector(".badge");
            badge.textContent = done ? "已通关" : unlocked ? `第 ${index + 1} 关` : "未解锁";
          });
          const percent = this.levels.length ? Math.round((this.completed.size / this.levels.length) * 100) : 0;
          this.progress.style.width = `${percent}%`;
          this.status.textContent = percent === 100 ? "全部通关，可以回看任意关卡或进行班级展示。" : `已完成 ${this.completed.size}/${this.levels.length} 关。`;
          this.renderPanel();
        }

        renderPanel(feedback = "") {
          const level = this.levels[this.activeIndex] || {};
          const pattern = this.patternForLevel(level);
          this.expectedSequence = pattern;
          const kind = level.challenge_kind || "steady_tap";
          this.panel.innerHTML = `
            <h3>${escapeText(level.title || "表现挑战")}</h3>
            <p><strong>目标：</strong>${escapeText(level.goal || spec.performance?.target_skill || "完成表现任务")}</p>
            <p><strong>玩法：</strong>${escapeText(level.student_task || "点击开始挑战，再根据提示完成表现。")}</p>
            <div class="quest-pattern" aria-label="目标序列">
              ${pattern.map((item, index) => `<span class="quest-token" data-token-index="${index}">${escapeText(this.labelForValue(item, kind))}</span>`).join("")}
            </div>
            <div class="quest-pads">
              ${this.controlsForKind(kind)}
            </div>
            <div class="button-row">
              <button type="button" data-quest-action="start">开始挑战</button>
              <button type="button" data-quest-action="reset">重来</button>
              <button type="button" data-quest-action="teacher-pass">教师确认通关</button>
            </div>
            <div class="quest-feedback" id="quest-feedback">${escapeText(feedback || level.success_rule || "完成后说出你用了哪个音乐要素。")}</div>
          `;
        }

        controlsForKind(kind) {
          if (kind === "ensemble_follow") {
            return [
              `<button class="quest-pad" type="button" data-quest-action="input" data-value="drum">鼓</button>`,
              `<button class="quest-pad" type="button" data-quest-action="input" data-value="cymbal">镲</button>`,
            ].join("");
          }
          if (kind === "dynamic_expression") {
            return ["p", "mp", "mf", "f"].map((value) => (
              `<button class="dynamic-step" type="button" data-quest-action="input" data-value="${value}">${value}</button>`
            )).join("");
          }
          if (kind === "chant_readback") {
            return `<button class="quest-pad" type="button" data-quest-action="input" data-value="chant">我已跟读一遍</button>`;
          }
          return `<button class="quest-pad" type="button" data-quest-action="input" data-value="tap">敲击</button>`;
        }

        startCurrentChallenge() {
          const level = this.levels[this.activeIndex] || {};
          const kind = level.challenge_kind || "steady_tap";
          const pattern = this.patternForLevel(level);
          this.inputSequence = [];
          this.flashPattern(pattern, kind);
          this.playPattern(pattern, kind);
          this.feedback(`先听/看目标序列，再完成：${pattern.map((item) => this.labelForValue(item, kind)).join(" - ")}。`);
        }

        recordInput(value) {
          const level = this.levels[this.activeIndex] || {};
          const kind = level.challenge_kind || "steady_tap";
          if (kind === "chant_readback") {
            this.completeLevel(this.activeIndex, "跟读完成。请说一句：这个节奏最明显的特点是什么？");
            return;
          }
          this.inputSequence.push(value);
          this.flashInput(value);
          const expected = this.expectedSequence[this.inputSequence.length - 1];
          if (value !== expected) {
            this.feedback(`这里应该是“${this.labelForValue(expected, kind)}”，再听一次目标序列后重来。`);
            this.inputSequence = [];
            return;
          }
          if (this.inputSequence.length >= this.expectedSequence.length) {
            this.completeLevel(this.activeIndex, "顺序正确，表现达标。进入下一关前，请说出你的音乐理由。");
            return;
          }
          this.feedback(`正确，继续第 ${this.inputSequence.length + 1} 个。`);
        }

        completeLevel(index, message) {
          this.completed.add(index);
          this.saveProgress();
          this.feedback(message);
          if (index < this.levels.length - 1) this.activeIndex = index + 1;
          window.setTimeout(() => this.render(), 650);
        }

        patternForLevel(level) {
          if (Array.isArray(level.pattern) && level.pattern.length) return level.pattern.map(String);
          if (level.challenge_kind === "ensemble_follow") return ["drum", "drum", "cymbal", "drum", "cymbal", "drum"];
          if (level.challenge_kind === "dynamic_expression") return ["p", "mp", "mf", "f"];
          if (level.challenge_kind === "chant_readback") return ["咚", "哒", "哒", "咚"];
          return ["tap", "tap", "tap", "tap", "tap", "tap", "tap", "tap"];
        }

        labelForValue(value, kind) {
          const labels = {
            tap: "拍",
            drum: "鼓",
            cymbal: "镲",
            chant: "跟读",
            p: "弱 p",
            mp: "中弱 mp",
            mf: "中强 mf",
            f: "强 f",
          };
          if (kind === "chant_readback" && !labels[value]) return value;
          return labels[value] || value;
        }

        flashPattern(pattern, kind) {
          this.panel.querySelectorAll(".quest-token").forEach((token) => token.classList.remove("active"));
          pattern.forEach((_item, index) => {
            window.setTimeout(() => {
              const token = this.panel.querySelector(`[data-token-index="${index}"]`);
              if (!token) return;
              token.classList.add("active");
              window.setTimeout(() => token.classList.remove("active"), 280);
            }, index * 430);
          });
        }

        flashInput(value) {
          const target = this.panel.querySelector(`[data-value="${value}"]`);
          if (!target) return;
          target.classList.add("hit");
          window.setTimeout(() => target.classList.remove("hit"), 220);
        }

        playPattern(pattern, kind) {
          const notes = pattern.map((item, index) => ({
            pitch: item === "cymbal" ? 76 : item === "drum" ? 48 : item === "f" ? 72 : item === "mf" ? 67 : item === "mp" ? 64 : item === "p" ? 60 : 55 + (index % 3) * 4,
            start: index * 0.42,
            duration: kind === "dynamic_expression" ? 0.38 : 0.16,
            velocity: item === "f" ? 112 : item === "mf" ? 96 : item === "mp" ? 78 : item === "p" ? 58 : 88,
          }));
          playSoundfontNotes(notes, "acoustic_grand_piano", kind === "dynamic_expression" ? "legato" : "staccato");
        }

        feedback(message) {
          const node = this.panel.querySelector("#quest-feedback");
          if (node) node.textContent = message;
        }
      }

      class CreationAssetLoader {
        constructor(root) {
          this.root = root;
          this.dropZone = root.querySelector("#drop-zone");
          this.feedback = root.querySelector("#composition-feedback");
          this.instrumentSelect = root.querySelector("#composition-instrument");
          this.articulationSelect = root.querySelector("#composition-articulation");
          this.draggedPiece = null;
          this.bindPieces();
          this.bindButtons();
        }

        bindPieces() {
          this.root.querySelectorAll(".piece").forEach((piece) => {
            piece.addEventListener("dragstart", () => {
              this.draggedPiece = this.clonePiece(piece);
            });
            piece.addEventListener("click", () => this.addPiece(this.clonePiece(piece)));
          });
          this.dropZone.addEventListener("dragover", (event) => event.preventDefault());
          this.dropZone.addEventListener("drop", (event) => {
            event.preventDefault();
            if (this.draggedPiece) this.addPiece(this.draggedPiece);
            this.draggedPiece = null;
          });
        }

        bindButtons() {
          this.root.querySelector("#clear-composition").addEventListener("click", () => {
            this.dropZone.textContent = "把素材拖到这里，或直接点击素材加入作品。";
            this.feedback.textContent = "完成后说一说：哪里像开始，哪里像发展，哪里像收束？";
          });
          this.root.querySelector("#play-composition").addEventListener("click", () => this.playComposition());
        }

        clonePiece(piece) {
          const clone = piece.cloneNode(true);
          clone.setAttribute("draggable", "false");
          clone.addEventListener("click", () => {
            clone.remove();
            this.updateFeedback();
          });
          return clone;
        }

        addPiece(piece) {
          if (this.dropZone.childElementCount === 0) this.dropZone.textContent = "";
          this.dropZone.appendChild(piece);
          this.updateFeedback();
        }

        updateFeedback() {
          const pieces = this.currentPieces();
          if (!pieces.length) {
            this.dropZone.textContent = "把素材拖到这里，或直接点击素材加入作品。";
            this.feedback.textContent = "完成后说一说：哪里像开始，哪里像发展，哪里像收束？";
            return;
          }
          const functions = pieces.map((piece) => piece.function).filter(Boolean).join("、");
          this.feedback.textContent = `作品已有 ${pieces.length} 个素材，结构功能包含：${functions || "待说明"}。`;
        }

        currentPieces() {
          return Array.from(this.dropZone.querySelectorAll(".piece")).map((node) => {
            try {
              return JSON.parse(node.dataset.piece || "{}");
            } catch {
              return {};
            }
          });
        }

        playComposition() {
          const pieces = this.currentPieces();
          if (!pieces.length) {
            this.feedback.textContent = "先放入几个素材，再试听作品雏形。";
            return;
          }
          const notes = pieces.map((piece, index) => ({
            pitch: pitchToMidi[piece.pitch] || 60 + (index % 5) * 2,
            start: index * 0.52,
            duration: rhythmDuration(piece.rhythm),
            velocity: 82,
          }));
          playSoundfontNotes(notes, this.instrumentSelect.value, this.articulationSelect.value);
        }
      }

      function rhythmDuration(rhythm) {
        return {
          "四": 0.45,
          "二八": 0.28,
          "八十六": 0.28,
          "十六八": 0.28,
          "四个十六": 0.24,
          "二分": 0.86,
          "休止": 0.18,
          "小切分": 0.38,
          "三连音": 0.24,
        }[rhythm] || 0.42;
      }

      class MusicGameRunner {
        constructor(root) {
          this.root = root;
          this.dropZone = root.querySelector("#game-drop-zone");
          this.feedback = root.querySelector("#game-feedback");
          this.runnerStrip = root.querySelector("#runner-strip");
          this.sequence = [];
          this.draggedRule = null;
          this.secondsPerBeat = 0.52;
          this.gameType = root.dataset.gameType || spec.music_game?.game_type || "lesson_mission_game";
          this.gameFamily = root.dataset.gameFamily || spec.music_game?.game_family || "mission";
          this.bind();
        }

        bind() {
          this.root.querySelectorAll(".game-rule-card").forEach((card) => {
            card.addEventListener("dragstart", () => {
              this.draggedRule = this.parseRule(card);
            });
            card.addEventListener("click", () => this.addRule(this.parseRule(card)));
          });

          this.dropZone.addEventListener("dragover", (event) => event.preventDefault());
          this.dropZone.addEventListener("drop", (event) => {
            event.preventDefault();
            if (this.draggedRule) this.addRule(this.draggedRule);
          });

          this.root.querySelector("#start-game").addEventListener("click", () => this.start());
          this.root.querySelector("#reset-game").addEventListener("click", () => this.reset());
        }

        parseRule(card) {
          try {
            return JSON.parse(card.dataset.rule || "{}");
          } catch (_error) {
            return {};
          }
        }

        addRule(rule) {
          this.sequence.push(rule);
          const chip = document.createElement("article");
          chip.className = "piece";
          chip.innerHTML = `<strong>${escapeText(rule.character || "角色")}</strong><p>${escapeText(rule.music_element || "规则")} ${escapeText(rule.value || "")}</p>`;
          chip.addEventListener("click", () => {
            const index = Array.from(this.dropZone.children).indexOf(chip);
            if (index >= 0) this.sequence.splice(index, 1);
            chip.remove();
            this.updateFeedback();
          });
          this.dropZone.appendChild(chip);
          this.updateFeedback();
        }

        reset() {
          this.sequence = [];
          this.dropZone.innerHTML = "把角色拖到这里，或直接点击角色加入挑战顺序。";
          this.runnerStrip.innerHTML = "";
          this.feedback.textContent = spec.music_game?.win_condition || "重新排列后再挑战一次。";
        }

        updateFeedback() {
          if (this.dropZone.textContent.includes("把角色拖到这里")) this.dropZone.innerHTML = "";
          this.feedback.textContent = this.sequence.length
            ? `已经放入 ${this.sequence.length} 个角色。点击开始，看看它们能不能按音乐规则完成挑战。`
            : "先选择至少一个角色。";
        }

        start() {
          if (!this.sequence.length) {
            this.feedback.textContent = "先拖入一个角色，再开始挑战。";
            return;
          }
          this.runnerStrip.innerHTML = "";
          const playback = this.buildPlayback(this.sequence);
          let startTime = 0;
          playback.segments.forEach((segment, index) => {
            const rule = segment.rule || {};
            const beats = Math.max(0.5, segment.duration / this.secondsPerBeat);
            const token = document.createElement("span");
            token.className = "runner-token";
            token.style.top = `${12 + index * 4}px`;
            token.style.setProperty("--race-duration", `${Math.max(0.75, beats * 0.55)}s`);
            token.textContent = `${rule.character || "角色"} ${rule.value || ""}`;
            this.runnerStrip.appendChild(token);
            window.setTimeout(() => token.classList.add("running"), startTime * 1000 + 80);
            startTime += Math.max(0.5, segment.duration);
          });
          playSoundfontNotes(playback.notes, playback.instrument || "acoustic_grand_piano", playback.articulation);
          this.feedback.textContent = playback.feedback || spec.music_game?.win_condition || "挑战完成，说一说每个角色为什么这样跑。";
        }

        beatsFromValue(value) {
          const numeric = Number(String(value || "").match(/\\d+(\\.\\d+)?/)?.[0] || 1);
          return Math.max(0.5, numeric);
        }

        buildPlayback(sequence) {
          const concept = String(spec.music_game?.music_concept || "");
          const notes = [];
          const segments = [];
          let cursor = 0;

          sequence.forEach((rule, index) => {
            const segment = this.buildRuleSegment(rule, cursor, index, concept);
            segment.notes.forEach((note) => notes.push(note));
            segments.push({
              rule,
              duration: segment.duration,
            });
            cursor += segment.duration;
          });

          return {
            notes,
            segments,
            articulation: this.articulationForConcept(concept),
            instrument: this.instrumentForSequence(sequence, concept),
            feedback: this.feedbackForPlayback(concept),
          };
        }

        buildRuleSegment(rule, cursor, index, concept) {
          if (this.isSyncopationConcept(concept, rule)) return this.buildSyncopationSegment(rule, cursor, index);
          if (this.isTripleMeterConcept(concept, rule)) return this.buildTripleMeterSegment(rule, cursor, index);
          if (this.isDottedConcept(concept, rule)) return this.buildDottedSegment(rule, cursor, index);
          if (this.isRestConcept(concept, rule)) return this.buildRestSegment(rule, cursor, index);
          if (this.isPitchConcept(concept, rule)) return this.buildPitchSegment(rule, cursor, index);
          if (this.isPentatonicConcept(concept, rule)) return this.buildPentatonicSegment(rule, cursor, index);
          if (this.isExpressionConcept(concept, rule)) return this.buildExpressionSegment(rule, cursor, index);
          if (this.isRelayConcept(concept, rule)) return this.buildRelaySegment(rule, cursor, index);
          if (this.isTimbreConcept(concept, rule)) return this.buildTimbreSegment(rule, cursor, index);
          return this.buildDurationSegment(rule, cursor, index);
        }

        buildDurationSegment(rule, cursor, index) {
          const beats = this.beatsFromValue(rule.value);
          const duration = Math.max(this.secondsPerBeat * 0.75, beats * this.secondsPerBeat);
          return {
            duration,
            notes: [
              {
                pitch: 60 + (index % 4) * 2,
                start: cursor,
                duration: Math.max(0.18, duration * 0.82),
                velocity: 86,
              },
            ],
          };
        }

        buildTripleMeterSegment(rule, cursor, index) {
          const label = `${rule.music_element || ""} ${rule.value || ""}`;
          const isStrong = /强|第1拍/.test(label);
          const duration = this.secondsPerBeat;
          return {
            duration,
            notes: [
              {
                pitch: isStrong ? 67 : 64,
                start: cursor,
                duration: duration * (isStrong ? 0.9 : 0.72),
                velocity: isStrong ? 108 : 76,
              },
            ],
          };
        }

        buildSyncopationSegment(rule, cursor, index) {
          const label = `${rule.music_element || ""} ${rule.value || ""} ${rule.motion || ""}`;
          const barDuration = this.secondsPerBeat * 2;
          const notes = [
            { pitch: 48, start: cursor, duration: 0.12, velocity: 48 },
            { pitch: 48, start: cursor + this.secondsPerBeat, duration: 0.12, velocity: 48 },
          ];
          if (/重音转移|切分|非强拍/.test(label)) {
            notes.push({
              pitch: 69,
              start: cursor + this.secondsPerBeat * 0.5,
              duration: this.secondsPerBeat * 1.15,
              velocity: 112,
            });
          } else if (/稳定拍|底层节拍/.test(label)) {
            notes.push({
              pitch: 55,
              start: cursor,
              duration: this.secondsPerBeat * 0.45,
              velocity: 74,
            });
            notes.push({
              pitch: 55,
              start: cursor + this.secondsPerBeat,
              duration: this.secondsPerBeat * 0.45,
              velocity: 74,
            });
          } else {
            notes.push({
              pitch: 64 + (index % 2) * 2,
              start: cursor + this.secondsPerBeat * 0.5,
              duration: this.secondsPerBeat * 0.95,
              velocity: 96,
            });
          }
          return { duration: barDuration, notes };
        }

        buildDottedSegment(rule, cursor, index) {
          const basePitch = 62 + (index % 3) * 2;
          return {
            duration: this.secondsPerBeat,
            notes: [
              {
                pitch: basePitch,
                start: cursor,
                duration: this.secondsPerBeat * 0.72,
                velocity: 96,
              },
              {
                pitch: basePitch + 3,
                start: cursor + this.secondsPerBeat * 0.75,
                duration: this.secondsPerBeat * 0.22,
                velocity: 88,
              },
            ],
          };
        }

        buildRestSegment(rule, cursor, index) {
          const label = `${rule.music_element || ""} ${rule.value || ""}`;
          if (/休止|停顿|无声/.test(label)) {
            return {
              duration: this.secondsPerBeat,
              notes: [
                { pitch: 48, start: cursor, duration: 0.08, velocity: 42 },
              ],
            };
          }
          return {
            duration: this.secondsPerBeat,
            notes: [
              { pitch: 60 + index, start: cursor, duration: this.secondsPerBeat * 0.62, velocity: 86 },
            ],
          };
        }

        buildPitchSegment(rule, cursor, index) {
          const label = `${rule.music_element || ""} ${rule.value || ""}`;
          const duration = this.secondsPerBeat;
          if (/上行|升高|向上|高音/.test(label)) {
            return {
              duration,
              notes: [
                { pitch: 60, start: cursor, duration: duration * 0.42, velocity: 78 },
                { pitch: 64, start: cursor + duration * 0.48, duration: duration * 0.42, velocity: 92 },
              ],
            };
          }
          if (/下行|降低|向下|低音/.test(label)) {
            return {
              duration,
              notes: [
                { pitch: 67, start: cursor, duration: duration * 0.42, velocity: 92 },
                { pitch: 62, start: cursor + duration * 0.48, duration: duration * 0.42, velocity: 78 },
              ],
            };
          }
          return {
            duration,
            notes: [
              { pitch: 64, start: cursor, duration: duration * 0.42, velocity: 84 },
              { pitch: 64, start: cursor + duration * 0.48, duration: duration * 0.42, velocity: 84 },
            ],
          };
        }

        buildPentatonicSegment(rule, cursor, index) {
          const label = `${rule.music_element || ""} ${rule.value || ""}`;
          const pitchMap = { "宫": 60, "商": 62, "角": 64, "徵": 67, "羽": 69 };
          const key = Object.keys(pitchMap).find((name) => label.includes(name));
          const pitch = key ? pitchMap[key] : [60, 62, 64, 67, 69][index % 5];
          const duration = this.secondsPerBeat * 0.92;
          return {
            duration,
            notes: [
              { pitch, start: cursor, duration: duration * 0.74, velocity: 86 },
            ],
          };
        }

        buildExpressionSegment(rule, cursor, index) {
          const label = `${rule.music_element || ""} ${rule.value || ""}`;
          const isStrong = /强|有力|力度/.test(label);
          const isFast = /快|速度|加速/.test(label);
          const duration = this.secondsPerBeat * (isFast ? 0.68 : 1.12);
          return {
            duration,
            notes: [
              { pitch: 60 + (index % 4) * 3, start: cursor, duration: duration * 0.72, velocity: isStrong ? 112 : 70 },
            ],
          };
        }

        buildRelaySegment(rule, cursor, index) {
          const duration = this.secondsPerBeat * 0.88;
          return {
            duration,
            notes: [
              { pitch: 55 + (index % 5) * 2, start: cursor, duration: duration * 0.36, velocity: 78 },
              { pitch: 60 + (index % 5) * 2, start: cursor + duration * 0.46, duration: duration * 0.36, velocity: 92 },
            ],
          };
        }

        buildTimbreSegment(rule, cursor, index) {
          const duration = this.secondsPerBeat;
          const label = `${rule.music_element || ""} ${rule.value || ""}`;
          const pitch = /打击|短促/.test(label) ? 48 : /柔和|圆润/.test(label) ? 64 : 72;
          const velocity = /明亮|清脆/.test(label) ? 100 : 78;
          const instrument = this.instrumentForRule(rule);
          return {
            duration,
            notes: [
              { pitch, start: cursor, duration: /打击|短促/.test(label) ? 0.16 : duration * 0.66, velocity, instrument },
            ],
          };
        }

        instrumentForSequence(sequence, concept) {
          if (!/(音色|乐器)/.test(concept)) return "acoustic_grand_piano";
          return this.instrumentForRule(sequence[0] || {});
        }

        instrumentForRule(rule) {
          const label = `${rule.music_element || ""} ${rule.value || ""} ${rule.character || ""} ${rule.feedback || ""}`;
          if (/小提琴|拉弦|柔和|圆润|连贯/.test(label)) return "violin";
          if (/长笛|清亮|轻盈|明亮|清脆/.test(label)) return "flute";
          if (/古筝|拨弦|民族|筝/.test(label)) return "koto";
          if (/木琴|打击|短促|颗粒/.test(label)) return "xylophone";
          return "acoustic_grand_piano";
        }

        articulationForConcept(concept) {
          if (/(旋律|音高|上行|下行)/.test(concept)) return "legato";
          if (/[切分|附点|节奏|拍|时值]/.test(concept)) return "staccato";
          return "natural";
        }

        feedbackForPlayback(concept) {
          if (concept.includes("切分")) return "播放里已经把稳定拍和弱拍重音做出来了。边听边拍，感受重音是不是转移到了非强拍位置。";
          if (concept.includes("三拍子")) return "播放里第一拍会更重，后两拍更轻。边听边做强弱弱，检查摇荡感是否出来。";
          if (concept.includes("附点")) return "播放里已经体现先长后短的附点关系。听一听是不是有明显的长短对比。";
          if (concept.includes("休止")) return "播放里已经把有声和停顿分开了。注意休止处虽然没声音，但时值还在。";
          if (/(旋律|音高|上行|下行)/.test(concept)) return "播放里已经体现高低变化。听的时候注意路线是不是和你的判断一致。";
          if (/(五声|宫|商|角|徵|羽|调式)/.test(concept)) return "播放里使用了五声音级。听一听短句有没有稳定的民族风格，再说出你用了哪些音。";
          if (/(音色|乐器)/.test(concept)) return "现在请把声音特点讲出来：是清亮、柔和、短促，还是有明显的发声线索？";
          if (/(力度|速度|情绪|形象)/.test(concept)) return "观察你选择的表现变化，再说出它和音乐情绪或形象的关系。";
          if (/(合作|接力|展示)/.test(concept)) return "接力挑战完成。请每组说一句自己接住了前一组的哪个音乐线索。";
          return spec.music_game?.win_condition || "挑战完成，说一说你听到的音乐规则。";
        }

        isTripleMeterConcept(concept, rule) {
          return concept.includes("三拍子") || /强弱弱|第1拍|第2拍|第3拍/.test(`${rule.music_element || ""} ${rule.value || ""}`);
        }

        isSyncopationConcept(concept, rule) {
          return concept.includes("切分") || /重音转移|非强拍|稳定拍|底层节拍/.test(`${rule.music_element || ""} ${rule.value || ""} ${rule.motion || ""}`);
        }

        isDottedConcept(concept, rule) {
          return concept.includes("附点") || /长短关系|附点/.test(`${rule.music_element || ""} ${rule.value || ""}`);
        }

        isRestConcept(concept, rule) {
          return concept.includes("休止") || /休止|停顿|无声/.test(`${rule.music_element || ""} ${rule.value || ""}`);
        }

        isPitchConcept(concept, rule) {
          return /旋律|音高|上行|下行|级进|跳进/.test(concept) || /向上|向下|高音|低音|保持/.test(`${rule.music_element || ""} ${rule.value || ""}`);
        }

        isPentatonicConcept(concept, rule) {
          return this.gameType === "pentatonic_grid_game" || /五声|调式|宫|商|角|徵|羽/.test(`${concept} ${rule.music_element || ""} ${rule.value || ""}`);
        }

        isExpressionConcept(concept, rule) {
          return this.gameType === "expression_control_game" || /力度|速度|情绪|形象|强弱|快慢/.test(`${concept} ${rule.music_element || ""} ${rule.value || ""}`);
        }

        isRelayConcept(concept, rule) {
          return this.gameType === "group_relay_game" || /合作|接力|小组|展示|轮次/.test(`${concept} ${rule.music_element || ""} ${rule.value || ""}`);
        }

        isTimbreConcept(concept, rule) {
          return this.gameType === "timbre_detective_game" || /音色|乐器|清脆|柔和|打击/.test(`${concept} ${rule.music_element || ""} ${rule.value || ""}`);
        }
      }

      class PlayableMusicMission {
        constructor(root) {
          this.root = root;
          this.playable = spec.music_game?.playable_game || {};
          this.variant = root.dataset.playableVariant || resolvePlayableVariant(this.playable, spec.music_game || {});
          this.materials = Array.isArray(this.playable.materials) ? this.playable.materials : [];
          this.rounds = Array.isArray(this.playable.rounds) && this.playable.rounds.length
            ? this.playable.rounds
            : [{ label: "第 1 关", prompt: this.playable.prompt || "", target_sequence: this.playable.target_sequence || [] }];
          this.currentRoundIndex = 0;
          this.maxLives = Math.max(1, Number(this.playable.lives || 3));
          this.lives = this.maxLives;
          this.target = root.querySelector("#playable-target");
          this.feedback = root.querySelector("#playable-feedback");
          this.roundBadge = root.querySelector("#playable-round-badge");
          this.roundPrompt = root.querySelector("#playable-round-prompt");
          this.hearts = root.querySelector("#playable-hearts");
          this.stars = root.querySelector("#playable-stars");
          this.progressBar = root.querySelector("#playable-progress-bar");
          this.emptyTargetText = this.target?.dataset.placeholder || (String(this.playable.age_style || "") === "lower_primary_cartoon" ? "拖到台阶上" : "把音乐卡片放到这里");
          this.sequence = [];
          this.dragged = null;
          this.bind();
          this.updateRoundUi();
        }

        bind() {
          this.root.querySelectorAll(".playable-card").forEach((card) => {
            card.addEventListener("dragstart", () => {
              this.dragged = this.parseCard(card);
            });
            card.addEventListener("click", () => this.addMaterial(this.parseCard(card)));
          });
          this.target.addEventListener("dragover", (event) => event.preventDefault());
          this.target.addEventListener("drop", (event) => {
            event.preventDefault();
            if (this.dragged) this.addMaterial(this.dragged);
            this.dragged = null;
          });
          this.root.querySelector("#play-target-sequence").addEventListener("click", () => this.playTarget());
          this.root.querySelector("#play-my-sequence").addEventListener("click", () => this.playMine());
          this.root.querySelector("#check-playable-sequence").addEventListener("click", () => this.check());
          this.root.querySelector("#reset-playable-sequence").addEventListener("click", () => this.reset());
        }

        parseCard(card) {
          try {
            return JSON.parse(card.dataset.playableCard || "{}");
          } catch (_error) {
            return {};
          }
        }

        addMaterial(material) {
          if (!material?.id) return;
          if ((this.target.textContent || "").trim() === this.emptyTargetText) this.target.innerHTML = "";
          this.sequence.push(material);
          const node = document.createElement("button");
          node.type = "button";
          node.className = `playable-card playable-card--${escapeText(material.id || "card")}`;
          const hasAudio = material.audio_clip_url;
          node.innerHTML = `${material.avatar ? `<span class="playable-card-figure">${escapeText(material.avatar)}</span>` : ""}<strong class="playable-note-name">${escapeText(material.label || "音乐卡片")}</strong><small>${escapeText(material.music_value || "")}</small>${hasAudio ? `<span class="audio-badge" title="真实音频">🎵</span>` : ""}`;
          node.addEventListener("click", () => {
            const index = Array.from(this.target.children).indexOf(node);
            if (index >= 0) this.sequence.splice(index, 1);
            node.remove();
            this.updateFeedback();
          });
          this.target.appendChild(node);
          this.updateFeedback(material.feedback);
        }

        reset() {
          this.sequence = [];
          this.lives = this.maxLives;
          this.target.innerHTML = this.emptyTargetText;
          this.feedback.textContent = this.playable.feedback?.empty || "先把音乐卡片放进挑战区。";
          this.updateRoundUi();
        }

        currentRound() {
          return this.rounds[this.currentRoundIndex] || this.rounds[0] || { target_sequence: this.playable.target_sequence || [] };
        }

        updateRoundUi() {
          const round = this.currentRound();
          if (this.roundBadge) this.roundBadge.textContent = round.label || `第 ${this.currentRoundIndex + 1} 关`;
          if (this.roundPrompt) this.roundPrompt.textContent = round.prompt || this.playable.prompt || "先试听目标，再完成操作并检查。";
          if (this.hearts) this.hearts.textContent = Array.from({ length: this.maxLives }, (_value, index) => index < this.lives ? "❤" : "♡").join(" ");
          if (this.stars) this.stars.textContent = this.rounds.map((_round, index) => index <= this.currentRoundIndex ? "★" : "☆").join(" ");
          if (this.progressBar) {
            const width = `${((this.currentRoundIndex) / Math.max(1, this.rounds.length)) * 100}%`;
            this.progressBar.style.width = width;
          }
        }

        updateFeedback(extra = "") {
          if (!this.sequence.length) {
            this.feedback.textContent = this.playable.feedback?.empty || "先把音乐卡片放进挑战区。";
            return;
          }
          this.feedback.textContent = extra || `已放入 ${this.sequence.length} 张卡片。`;
        }

        playTarget() {
          const targetSequence = this.currentRound().target_sequence || this.playable.target_sequence || [];
          this.flashBank(targetSequence);
          this.playSequence(this.materialsForIds(targetSequence));
          const hint = this.previewHint();
          this.feedback.textContent = hint;
        }

        playMine() {
          if (!this.sequence.length) {
            this.feedback.textContent = this.playable.feedback?.empty || "先放入卡片再试听。";
            return;
          }
          this.playSequence(this.sequence);
          this.feedback.textContent = "正在播放你的排列。";
        }

        check() {
          const expected = this.currentRound().target_sequence || this.playable.target_sequence || [];
          const actual = this.sequence.map((item) => item.id);
          if (!actual.length) {
            this.feedback.textContent = this.playable.feedback?.empty || "先把音乐卡片放进挑战区。";
            return;
          }
          const isPrefix = actual.every((id, index) => id === expected[index]);
          if (actual.length < expected.length && isPrefix) {
            this.feedback.textContent = this.playable.feedback?.partial || "方向对了，继续补完整。";
            return;
          }
          const correct = expected.length === actual.length && expected.every((id, index) => id === actual[index]);
          if (correct) {
            this.playMine();
            if (this.currentRoundIndex < this.rounds.length - 1) {
              this.currentRoundIndex += 1;
              this.lives = this.maxLives;
              this.sequence = [];
              this.target.innerHTML = this.emptyTargetText;
              this.feedback.textContent = `这一关通过了，进入${this.currentRound().label || "下一关"}。`;
              this.updateRoundUi();
              return;
            }
            if (this.progressBar) this.progressBar.style.width = "100%";
            this.feedback.textContent = `${this.playable.feedback?.success || "挑战成功。"} ${this.playable.feedback?.closure || ""}`.trim();
            return;
          }
          this.lives = Math.max(0, this.lives - 1);
          if (this.lives <= 0) {
            this.lives = this.maxLives;
            this.sequence = [];
            this.target.innerHTML = this.emptyTargetText;
            this.feedback.textContent = "三次机会用完了，这一关重新开始。";
          } else {
            this.feedback.textContent = `${this.playable.feedback?.wrong || "顺序还没有体现音乐关系，先试听目标再调整。"} 还剩 ${this.lives} 次机会。`;
          }
          this.updateRoundUi();
        }

        materialsForIds(ids) {
          return ids.map((id) => this.materials.find((item) => item.id === id)).filter(Boolean);
        }

        playSequence(sequence) {
          const hasAudioClips = sequence.some((item) => item && item.audio_clip_url);
          if (hasAudioClips) {
            playAudioClipSequence(sequence);
            return;
          }
          let cursor = 0;
          const secondsPerStep = Number(this.playable.playback?.seconds_per_step || 0.52);
          const notes = [];
          sequence.forEach((item, index) => {
            const itemInstrument = this.instrumentForMaterial(item);
            const phraseTokens = Array.isArray(item.playback_tokens) && item.playback_tokens.length
              ? item.playback_tokens
              : (Array.isArray(item.phrase_tokens) ? item.phrase_tokens : []);
            if (phraseTokens.length) {
              phraseTokens.forEach((token, tokenIndex) => {
                const duration = Math.max(0.08, Number(token.duration || secondsPerStep));
                if (!token.rest) {
                  notes.push({
                    pitch: Number(token.pitch || item.pitch || 60 + ((index + tokenIndex) % 5) * 2),
                    start: cursor,
                    duration,
                    velocity: Number(token.velocity || item.velocity || 86),
                    instrument: token.instrument || itemInstrument,
                  });
                }
                cursor += Math.max(secondsPerStep * 0.65, duration);
              });
              cursor += secondsPerStep * 0.35;
              return;
            }
            const duration = Math.max(0.08, Number(item.duration || secondsPerStep));
            if (!item.rest) {
              notes.push({
                pitch: Number(item.pitch || 60 + (index % 5) * 2),
                start: cursor,
                duration,
                velocity: Number(item.velocity || 86),
                instrument: itemInstrument,
              });
            }
            cursor += Math.max(secondsPerStep, duration);
          });
          playSoundfontNotes(notes, this.playable.playback?.instrument || notes[0]?.instrument || "acoustic_grand_piano", this.articulation());
        }

        instrumentForMaterial(item) {
          const label = `${item?.label || ""} ${item?.music_value || ""} ${item?.feedback || ""} ${item?.instrument || ""}`;
          if (/violin|小提琴|拉弦|柔和|圆润|连贯/.test(label)) return "violin";
          if (/flute|长笛|清亮|轻盈|明亮|清脆/.test(label)) return "flute";
          if (/koto|guzheng|古筝|拨弦|民族|筝/.test(label)) return "koto";
          if (/xylophone|木琴|打击|短促|颗粒/.test(label)) return "xylophone";
          if (/cello|大提琴|低沉/.test(label)) return "cello";
          return this.playable.playback?.instrument || "acoustic_grand_piano";
        }

        articulation() {
          const type = String(this.playable.operation_type || "");
          if (/melody|singing|expression/.test(type)) return "legato";
          if (/rhythm|timbre/.test(type)) return "staccato";
          return "natural";
        }

        previewHint() {
          if (this.variant === "phrase") return "听清乐句关系，再把片段和证据排进故事板。";
          if (this.variant === "rhythm") return "边听边数拍点，再把节奏材料放进跑道。";
          if (this.variant === "expression") return "先听声音大小或快慢变化，再排出表现线。";
          if (this.variant === "timbre") return "先抓住音色特征，再连接对应证据。";
          if (this.variant === "pentatonic") return "先听民族风格，再把五声音级拼成短句。";
          return "听清音列，再开始摆卡。";
        }

        flashBank(ids) {
          this.root.querySelectorAll(".playable-card").forEach((card) => card.classList.remove("active"));
          ids.forEach((id, index) => {
            window.setTimeout(() => {
              const card = Array.from(this.root.querySelectorAll(".playable-bank .playable-card")).find((node) => {
                try {
                  return JSON.parse(node.dataset.playableCard || "{}").id === id;
                } catch (_error) {
                  return false;
                }
              });
              if (!card) return;
              card.classList.add("active");
              window.setTimeout(() => card.classList.remove("active"), 280);
            }, index * 420);
          });
        }
      }

      function bindListening() {
        const form = document.querySelector("#listening-form");
        if (!form) return;
        let sessionId = "";
        let uploadedFileKey = "";

        form.addEventListener("submit", async (event) => {
          event.preventDefault();
          const result = document.querySelector("#listening-result");
          const submitButton = form.querySelector('button[type="submit"]');
          const file = form.elements.audio.files[0];
          if (!file) {
            result.innerHTML = "请先上传一段课堂音频。";
            return;
          }

          const fileKey = `${file.name}:${file.size}:${file.lastModified}`;
          const originalButtonText = submitButton.textContent;
          submitButton.disabled = true;
          submitButton.textContent = sessionId && fileKey === uploadedFileKey ? "正在变换要素..." : "正在首次解析音频...";
          result.innerHTML = sessionId && fileKey === uploadedFileKey
            ? "正在根据新的音乐要素生成对比版本，这次不会重复解析整首歌。"
            : "第一次上传需要整理旋律、伴奏和谱面，后续改参数会快很多。";

          try {
            if (!sessionId || fileKey !== uploadedFileKey) {
              const uploadData = new FormData();
              uploadData.append("audio", file);
              const uploadResponse = await fetch("/api/listening/upload", {
                method: "POST",
                body: uploadData,
              });
              const uploadPayload = await uploadResponse.json();
              if (!uploadResponse.ok) {
                throw new Error(uploadPayload.error || "这段音频暂时没有听清楚。");
              }
              sessionId = uploadPayload.session_id;
              uploadedFileKey = fileKey;
            }

            const transformData = new FormData();
            transformData.append("session_id", sessionId);
            transformData.append("tonic", form.elements.tonic.value);
            transformData.append("mode", form.elements.mode.value);
            transformData.append("tempo_multiplier", form.elements.tempo_multiplier.value);
            transformData.append("rhythm_density", form.elements.rhythm_density.value);
            transformData.append("instrument", form.elements.instrument.value);

            const response = await fetch("/api/listening/transform", {
              method: "POST",
              body: transformData,
            });
            const data = await response.json();
            if (!response.ok) {
              throw new Error(data.error || "这段音频暂时没有听清楚。");
            }
            renderListeningResult(data, result, form);
          } catch (error) {
            result.innerHTML = `处理失败：${escapeText(error.message || "这段音频暂时没有听清楚。")}`;
          } finally {
            submitButton.disabled = false;
            submitButton.textContent = originalButtonText;
          }
        });
      }

      function renderListeningResult(data, result, form) {
        const transformedPlayback = data.transformed_playback || data.playback || { notes: [] };
        latestPlayback = transformedPlayback;
        latestInstrument = form.elements.instrument.value;
        const stemLinks = Object.entries(data.stem_urls || {})
          .map(([name, url]) => `<a href="${escapeText(url)}" target="_blank" rel="noreferrer">${escapeText(name)}</a>`)
          .join(" · ");
        const downloadLinks = [
          data.generated_midi_url ? `<a href="${escapeText(data.generated_midi_url)}" target="_blank" rel="noreferrer">识别旋律 MIDI</a>` : "",
          data.transformed_midi_url ? `<a href="${escapeText(data.transformed_midi_url)}" target="_blank" rel="noreferrer">改写后 MIDI</a>` : "",
          data.transformed_audio_url ? `<a href="${escapeText(data.transformed_audio_url)}" target="_blank" rel="noreferrer">改写后音频</a>` : "",
        ].filter(Boolean).join(" · ");
        result.innerHTML = `
          <p class="happy-note">${data.cache_hit ? "已从缓存取回这个版本。" : "对比版本已经生成。"}</p>
          <p>${escapeText(data.summary?.teaching_suggestion || data.summary?.tip || "现在可以让学生对比听辨音乐要素变化。")}</p>
          ${data.source_audio_url ? `<label>原音频<audio id="listening-source-audio" controls preload="metadata" src="${escapeText(data.source_audio_url)}"></audio></label>` : ""}
          ${data.transformed_audio_url ? `<label>改写后音频<audio id="listening-transformed-audio" controls preload="metadata" src="${escapeText(data.transformed_audio_url)}"></audio></label>` : ""}
          <div class="button-row">
            <button id="play-source" type="button">试听识别旋律</button>
            <button id="play-transformed" type="button">试听变换版本</button>
          </div>
          ${downloadLinks ? `<p>下载：${downloadLinks}</p>` : ""}
          ${stemLinks ? `<p>课堂分轨：${stemLinks}</p>` : ""}
          ${data.warning ? `<p>${escapeText(data.warning)}</p>` : ""}
        `;
        result.querySelector("#play-source").addEventListener("click", async () => {
          const sourceAudio = result.querySelector("#listening-source-audio");
          const sourcePlayback = data.source_playback || { notes: [] };
          const played = await playManagedAudioElement(sourceAudio, "listening-source");
          if (played) return;
          playSoundfontNotes(sourcePlayback.notes || [], resolvePlaybackInstrument(sourcePlayback, "preserve"));
        });
        result.querySelector("#play-transformed").addEventListener("click", async () => {
          const transformedAudio = result.querySelector("#listening-transformed-audio");
          const played = await playManagedAudioElement(transformedAudio, "listening-transformed");
          if (played) return;
          playSoundfontNotes(transformedPlayback.notes || [], resolvePlaybackInstrument(transformedPlayback, latestInstrument));
        });
      }

      function bindPerformance() {
        const root = document.querySelector('[data-template="Template_Performance"]');
        if (!root) return;
        if (root.dataset.performanceTemplate === "immersive_rhythm_mountain") {
          new PerformanceQuestController(root);
          return;
        }
        new LevelController(root);
      }

      function bindCreation() {
        const root = document.querySelector('[data-template="Template_Creation"]');
        if (root) {
          new CreationAssetLoader(root);
          new MelodyLineBoard(root);
        }
      }

      function bindMusicGame() {
        const root = document.querySelector('[data-template="Template_MusicGame"]');
        if (!root) return;
        bindTimbreLab(root);
        if (root.querySelector('[data-playable-mission="true"]')) {
          new PlayableMusicMission(root);
          return;
        }
        new MusicGameRunner(root);
      }

      function bindTimbreLab(root) {
        const feedback = root.querySelector("#timbre-feedback");
        root.querySelectorAll("[data-timbre-sample]").forEach((button) => {
          button.addEventListener("click", async () => {
            const instrumentName = button.dataset.timbreSample || "acoustic_grand_piano";
            const notes = [
              { pitch: 60, start: 0, duration: 0.42, velocity: 86, instrument: instrumentName },
              { pitch: 64, start: 0.48, duration: 0.42, velocity: 88, instrument: instrumentName },
              { pitch: 67, start: 0.96, duration: 0.64, velocity: 90, instrument: instrumentName },
            ];
            const originalText = button.textContent;
            button.disabled = true;
            button.textContent = "加载中...";
            if (feedback) feedback.textContent = `正在加载${originalText}真实采样音色...`;
            const ok = await playSoundfontNotes(notes, instrumentName, "auto");
            button.disabled = false;
            button.textContent = originalText;
            if (ok && feedback) {
              feedback.textContent = `${originalText}：${button.dataset.timbreHint || "听一听它的发声特点。"} 说出一个你听到的证据。`;
            }
          });
        });
      }

      class MelodyLineBoard {
        constructor(root) {
          this.root = root;
          this.canvas = root.querySelector("#melody-canvas");
          this.keySelect = root.querySelector("#melody-key");
          this.barsSelect = root.querySelector("#melody-bars");
          this.voiceSelect = root.querySelector("#melody-voice");
          this.voiceInstrumentSelects = {
            voice1: root.querySelector("#voice1-instrument"),
            voice2: root.querySelector("#voice2-instrument"),
          };
          this.articulationSelect = root.querySelector("#melody-articulation");
          this.feedback = root.querySelector("#melody-feedback");
          this.voices = {
            voice1: new Map(),
            voice2: new Map(),
          };
          this.isDrawing = false;
          this.ctx = this.canvas.getContext("2d");
          this.cellWidth = 24;
          this.cellHeight = 18;
          this.labelWidth = 72;
          this.topPadding = 18;
          this.pitchRows = 20;
          this.mode = spec.creation?.mode || "western_major";
          this.tonic = this.keySelect?.value || spec.creation?.tonic || "C";
          this.voiceColors = {
            voice1: "#6d6af6",
            voice2: "#ff8f6a",
          };
          this.bind();
          this.draw();
        }

        bind() {
          this.canvas.addEventListener("pointerdown", (event) => {
            this.isDrawing = true;
            this.addPointFromEvent(event);
          });
          this.canvas.addEventListener("pointermove", (event) => {
            if (!this.isDrawing) return;
            this.addPointFromEvent(event);
          });
          window.addEventListener("pointerup", () => {
            if (!this.isDrawing) return;
            this.isDrawing = false;
            this.updateFeedback();
          });
          this.keySelect.addEventListener("change", () => {
            this.tonic = this.keySelect.value;
            this.draw();
            this.updateFeedback();
          });
          this.barsSelect.addEventListener("change", () => {
            this.clearVoices();
            this.draw();
            this.feedback.textContent = "小节数已更新，请重新画旋律线。";
          });
          this.voiceSelect.addEventListener("change", () => {
            this.draw();
            this.updateFeedback();
          });
          Object.values(this.voiceInstrumentSelects).forEach((select) => {
            select.addEventListener("change", () => this.updateFeedback());
          });
          this.articulationSelect.addEventListener("change", () => this.updateFeedback());
          this.root.querySelector("#play-melody-line").addEventListener("click", () => this.play());
          this.root.querySelector("#clear-melody-line").addEventListener("click", () => {
            this.clearActiveVoice();
            this.feedback.textContent = `${this.voiceLabel(this.activeVoice())}已清空，可以重新画这一条线。`;
            this.draw();
          });
        }

        addPointFromEvent(event) {
          const rect = this.canvas.getBoundingClientRect();
          const rawX = ((event.clientX - rect.left) / rect.width) * this.canvas.width;
          const rawY = ((event.clientY - rect.top) / rect.height) * this.canvas.height;
          const totalSteps = this.totalSteps();
          const step = Math.max(0, Math.min(totalSteps - 1, Math.round((rawX - this.labelWidth) / this.cellWidth)));
          const row = Math.max(0, Math.min(this.pitchRows - 1, Math.round((rawY - this.topPadding) / this.cellHeight)));
          this.voices[this.activeVoice()].set(step, row);
          this.draw();
        }

        draw() {
          this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
          this.drawGrid();
          this.drawVoice("voice1");
          this.drawVoice("voice2");
        }

        drawVoice(voice) {
          const points = this.gridPoints(voice);
          if (!points.length) return;
          const isActive = voice === this.activeVoice();
          this.ctx.lineWidth = isActive ? 5 : 3;
          this.ctx.lineCap = "round";
          this.ctx.lineJoin = "round";
          this.ctx.globalAlpha = isActive ? 1 : 0.56;
          this.ctx.strokeStyle = this.voiceColors[voice];
          if (points.length > 1) {
            this.ctx.beginPath();
            points.forEach((point, index) => {
              if (index === 0) this.ctx.moveTo(point.x, point.y);
              else this.ctx.lineTo(point.x, point.y);
            });
            this.ctx.stroke();
          }
          points.forEach((point) => {
            this.ctx.beginPath();
            this.ctx.fillStyle = this.voiceColors[voice];
            this.ctx.arc(point.x, point.y, isActive ? 7 : 5, 0, Math.PI * 2);
            this.ctx.fill();
          });
          this.ctx.globalAlpha = 1;
        }

        drawGrid() {
          const totalSteps = this.totalSteps();
          const gridWidth = totalSteps * this.cellWidth;
          const gridHeight = (this.pitchRows - 1) * this.cellHeight;
          this.canvas.width = this.labelWidth + gridWidth + 24;
          this.canvas.height = this.topPadding * 2 + gridHeight;
          this.ctx.fillStyle = "#fffdf6";
          this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

          for (let row = 0; row < this.pitchRows; row += 1) {
            const y = this.topPadding + row * this.cellHeight;
            this.ctx.strokeStyle = row % 2 === 0 ? "rgba(35, 48, 79, 0.15)" : "rgba(35, 48, 79, 0.08)";
            this.ctx.lineWidth = 1;
            this.ctx.beginPath();
            this.ctx.moveTo(this.labelWidth, y);
            this.ctx.lineTo(this.labelWidth + gridWidth, y);
            this.ctx.stroke();

            const midi = this.rowToMidi(row);
            this.ctx.fillStyle = this.isScaleTone(midi) ? "#26324f" : "rgba(99, 112, 146, 0.55)";
            this.ctx.font = this.isScaleTone(midi) ? "700 12px sans-serif" : "12px sans-serif";
            this.ctx.textAlign = "right";
            this.ctx.textBaseline = "middle";
            this.ctx.fillText(this.solfegeForMidi(midi), this.labelWidth - 10, y);
          }

          for (let step = 0; step <= totalSteps; step += 1) {
            const x = this.labelWidth + step * this.cellWidth;
            this.ctx.strokeStyle = step % 16 === 0 ? "rgba(109, 106, 246, 0.35)" : step % 4 === 0 ? "rgba(109, 106, 246, 0.2)" : "rgba(109, 106, 246, 0.1)";
            this.ctx.lineWidth = step % 16 === 0 ? 2 : 1;
            this.ctx.beginPath();
            this.ctx.moveTo(x, this.topPadding);
            this.ctx.lineTo(x, this.topPadding + gridHeight);
            this.ctx.stroke();

            if (step % 16 === 0) {
              this.ctx.fillStyle = "rgba(99, 112, 146, 0.8)";
              this.ctx.font = "700 11px sans-serif";
              this.ctx.textAlign = "center";
              this.ctx.textBaseline = "top";
              this.ctx.fillText(`第${step / 16 + 1}小节`, x + 24, this.topPadding + gridHeight + 8);
            }
          }
        }

        notes() {
          return this.notesForVoice(this.activeVoice());
        }

        notesForVoice(voice) {
          const entries = Array.from(this.voices[voice].entries()).sort(([a], [b]) => a - b);
          return entries.map(([step, row]) => {
            return {
              pitch: this.rowToMidi(row),
              start: step * 0.25,
              duration: 0.25,
              velocity: 84,
            };
          });
        }

        preparedNotesForVoice(voice) {
          return prepareMelodyNotes(
            this.notesForVoice(voice),
            this.voiceInstrumentSelects[voice].value,
            this.articulationSelect.value
          );
        }

        updateFeedback() {
          const activeVoice = this.activeVoice();
          const activeNotes = this.preparedNotesForVoice(activeVoice);
          const voice1Count = this.voices.voice1.size;
          const voice2Count = this.voices.voice2.size;
          if (!activeNotes.length) {
            this.feedback.textContent = `${this.voiceLabel(activeVoice)}还没有旋律线。声部一 ${voice1Count} 个音，声部二 ${voice2Count} 个音。`;
            return;
          }
          const first = activeNotes[0].pitch;
          const last = activeNotes[activeNotes.length - 1].pitch;
          const stable = last % 12 === tonicPc(this.tonic);
          this.feedback.textContent = `${this.voiceLabel(activeVoice)}已生成 ${activeNotes.length} 个音，音色为 ${this.selectedInstrumentLabel(activeVoice)}；开始是 ${this.solfegeForMidi(first)}，结束是 ${this.solfegeForMidi(last)}。${stable ? "结尾落在 do，稳定感很好。" : "结尾可以尝试落回 do，让乐句更完整。"} 声部一 ${voice1Count} 个音，声部二 ${voice2Count} 个音。`;
        }

        play() {
          const voice1Notes = this.preparedNotesForVoice("voice1");
          const voice2Notes = this.preparedNotesForVoice("voice2");
          if (!voice1Notes.length && !voice2Notes.length) {
            this.feedback.textContent = "先选择声部并画旋律线，再试听。";
            return;
          }
          if (voice1Notes.length) playSoundfontNotes(voice1Notes, this.voiceInstrumentSelects.voice1.value, this.articulationSelect.value);
          if (voice2Notes.length) playSoundfontNotes(voice2Notes, this.voiceInstrumentSelects.voice2.value, this.articulationSelect.value);
        }

        totalSteps() {
          return Number(this.barsSelect.value || 4) * 16;
        }

        rowToMidi(row) {
          const center = 60 + tonicPc(this.tonic);
          return center + 9 - row;
        }

        gridPoints(voice) {
          return Array.from(this.voices[voice].entries())
            .sort(([a], [b]) => a - b)
            .map(([step, row]) => ({
              x: this.labelWidth + step * this.cellWidth,
              y: this.topPadding + row * this.cellHeight,
            }));
        }

        activeVoice() {
          return this.voiceSelect.value || "voice1";
        }

        clearActiveVoice() {
          this.voices[this.activeVoice()].clear();
        }

        clearVoices() {
          this.voices.voice1.clear();
          this.voices.voice2.clear();
        }

        voiceLabel(voice) {
          return voice === "voice2" ? "声部二" : "声部一";
        }

        selectedInstrumentLabel(voice) {
          const select = this.voiceInstrumentSelects[voice];
          return select.options[select.selectedIndex]?.textContent || "当前音色";
        }

        isScaleTone(midi) {
          return modeIntervals(this.mode).includes((midi - tonicPc(this.tonic) + 120) % 12);
        }

        solfegeForMidi(midi) {
          const degree = (midi - tonicPc(this.tonic) + 120) % 12;
          return {
            0: "do",
            1: "#do",
            2: "re",
            3: "♭mi",
            4: "mi",
            5: "fa",
            6: "#fa",
            7: "sol",
            8: "♭la",
            9: "la",
            10: "♭ti",
            11: "ti",
          }[degree] || "";
        }
      }

      function tonicPc(key) {
        return {
          C: 0,
          "C#": 1,
          Db: 1,
          D: 2,
          "D#": 3,
          Eb: 3,
          E: 4,
          F: 5,
          "F#": 6,
          Gb: 6,
          G: 7,
          "G#": 8,
          Ab: 8,
          A: 9,
          "A#": 10,
          Bb: 10,
          B: 11,
        }[key] ?? 0;
      }

      function modeIntervals(mode) {
        return {
          western_major: [0, 2, 4, 5, 7, 9, 11],
          western_minor: [0, 2, 3, 5, 7, 8, 10],
          chinese_pentatonic: [0, 2, 4, 7, 9],
          chinese_heptatonic: [0, 2, 4, 5, 7, 9, 11],
          dorian: [0, 2, 3, 5, 7, 9, 10],
          phrygian: [0, 1, 3, 5, 7, 8, 10],
          blues: [0, 3, 5, 6, 7, 10],
        }[mode] || [0, 2, 4, 5, 7, 9, 11];
      }

      async function playNotes(notes, oscillatorTypeValue) {
        if (!notes.length) return;
        await ensureAudioReady("oscillator-sequence");
        const startOffset = audioContext.currentTime + 0.08;
        notes.slice(0, 220).forEach((note) => playNote(note, startOffset, oscillatorTypeValue));
      }

      function prepareMelodyNotes(notes) {
        return mergeSustainedNotes(interpolateMelodyNotes(notes));
      }

      function interpolateMelodyNotes(notes) {
        const sorted = notes.slice().sort((a, b) => Number(a.start || 0) - Number(b.start || 0));
        if (sorted.length <= 1) return sorted;
        const result = [];
        for (let index = 0; index < sorted.length - 1; index += 1) {
          const current = sorted[index];
          const next = sorted[index + 1];
          result.push(current);
          const currentStep = Math.round(Number(current.start || 0) / 0.25);
          const nextStep = Math.round(Number(next.start || 0) / 0.25);
          const gap = nextStep - currentStep;
          if (gap > 1 && gap <= 8) {
            for (let stepOffset = 1; stepOffset < gap; stepOffset += 1) {
              const ratio = stepOffset / gap;
              result.push({
                pitch: Math.round(Number(current.pitch) + (Number(next.pitch) - Number(current.pitch)) * ratio),
                start: (currentStep + stepOffset) * 0.25,
                duration: 0.25,
                velocity: Math.round((Number(current.velocity || 84) + Number(next.velocity || 84)) / 2),
              });
            }
          }
        }
        result.push(sorted[sorted.length - 1]);
        return result;
      }

      function mergeSustainedNotes(notes) {
        const sorted = notes.slice().sort((a, b) => Number(a.start || 0) - Number(b.start || 0));
        const merged = [];
        sorted.forEach((note) => {
          const start = Number(note.start || 0);
          const duration = Number(note.duration || 0.25);
          const last = merged[merged.length - 1];
          if (last && Number(last.pitch) === Number(note.pitch) && Math.abs(Number(last.start) + Number(last.duration) - start) < 0.03) {
            last.duration = Number(last.duration) + duration;
            last.velocity = Math.max(Number(last.velocity || 80), Number(note.velocity || 80));
            return;
          }
          merged.push({ ...note, start, duration });
        });
        return merged;
      }

      function resolveArticulation(instrumentName, articulation) {
        if (articulation && articulation !== "auto") return articulation;
        if (["flute", "violin", "cello", "clarinet"].includes(instrumentName)) return "legato";
        if (["koto", "acoustic_guitar_nylon"].includes(instrumentName)) return "pluck";
        if (instrumentName === "xylophone") return "staccato";
        return "natural";
      }

      function applyPlaybackStyle(notes, instrumentName, articulation) {
        const sampledInstrument = normalizeSoundfontInstrument(instrumentName);
        const resolved = resolveArticulation(sampledInstrument || "acoustic_grand_piano", articulation || "auto");
        const durationScale = {
          legato: 1.12,
          natural: 0.96,
          staccato: 0.52,
          pluck: 0.86,
        }[resolved] || 0.96;
        return notes.map((note) => ({
          ...note,
          duration: Math.max(0.08, Number(note.duration || 0.4) * durationScale),
          velocity: Number(note.velocity || 82),
        }));
      }

      const soundfontCache = new Map();
      const soundfontHosts = [
        "/runtime-assets/midi-js-soundfonts/",
        "/static/assets/midi-js-soundfonts/",
        "https://registry.npmmirror.com/midi-js-soundfonts/latest/files/",
        "https://gleitz.github.io/midi-js-soundfonts/",
        "https://cdn.jsdelivr.net/gh/gleitz/midi-js-soundfonts@gh-pages/",
      ];

      function normalizeSoundfontInstrument(instrumentName) {
        return {
          preserve: "acoustic_grand_piano",
          piano: "acoustic_grand_piano",
          guzheng: "koto",
          zheng: "koto",
          guitar: "acoustic_guitar_nylon",
        }[instrumentName] || instrumentName || "acoustic_grand_piano";
      }

      function resolvePlaybackInstrument(playback, selectedInstrument, fallback = "acoustic_grand_piano") {
        if (selectedInstrument && selectedInstrument !== "preserve") {
          return normalizeSoundfontInstrument(selectedInstrument);
        }
        return normalizeSoundfontInstrument(playback?.instrument || playback?.notes?.[0]?.instrument || fallback);
      }

      function withSoundfontTimeout(promise, label, timeoutMs = 6500) {
        let timeoutId = null;
        const timeout = new Promise((_resolve, reject) => {
          timeoutId = window.setTimeout(() => reject(new Error(`${label} timed out`)), timeoutMs);
        });
        return Promise.race([promise, timeout]).finally(() => {
          if (timeoutId) window.clearTimeout(timeoutId);
        });
      }

      async function loadSoundfontInstrument(instrumentName) {
        await ensureAudioReady(`load-soundfont:${instrumentName}`);
        if (!window.Soundfont) throw new Error("SoundFont loader unavailable");
        const sampledInstrument = normalizeSoundfontInstrument(instrumentName);
        if (!soundfontCache.has(sampledInstrument)) {
          soundfontCache.set(sampledInstrument, (async () => {
            let lastError = null;
            for (const host of soundfontHosts) {
              try {
                return await withSoundfontTimeout(Soundfont.instrument(audioContext, sampledInstrument, {
                  soundfont: "FluidR3_GM",
                  format: "mp3",
                  nameToUrl: (name, soundfont, format) => `${host}${soundfont}/${name}-${format}.js`,
                }), `${sampledInstrument} from ${host}`);
              } catch (error) {
                lastError = error;
              }
            }
            throw lastError || new Error("SoundFont load failed");
          })());
        }
        try {
          return await soundfontCache.get(sampledInstrument);
        } catch (error) {
          soundfontCache.delete(sampledInstrument);
          throw error;
        }
      }

      async function playSoundfontNotes(notes, instrumentName, articulation = "auto") {
        if (!notes.length) return false;
        if (activeClipAudio) {
          try {
            activeClipAudio.pause();
            activeClipAudio.currentTime = 0;
          } catch (_error) {}
          activeClipAudio = null;
        }
        await ensureAudioReady(`soundfont-playback:${instrumentName || "default"}`);
        const startOffset = audioContext.currentTime + 0.08;
        const shapedNotes = applyPlaybackStyle(notes, instrumentName, articulation);
        try {
          const grouped = groupNotesByInstrument(shapedNotes, instrumentName || "acoustic_grand_piano");
          await Promise.all(Array.from(grouped.keys()).map((name) => loadSoundfontInstrument(name)));
          for (const [name, groupNotes] of grouped.entries()) {
            const instrument = await loadSoundfontInstrument(name);
            groupNotes.slice(0, 220).forEach((note) => {
              instrument.play(Number(note.pitch || 60), startOffset + Number(note.start || 0), {
                duration: Math.max(0.08, Number(note.duration || 0.4)),
                gain: Math.max(0.08, Number(note.velocity || 82) / 150),
              });
            });
          }
          return true;
        } catch (error) {
          showSoundfontUnavailable(error);
          return false;
        }
      }

      function showSoundfontUnavailable(error) {
        const message = "真实采样音色资源没有加载成功。请先在服务器预缓存 soundfont-player 和 FluidR3_GM 乐器音色，再试听。";
        const targets = [
          document.querySelector("#timbre-feedback"),
          document.querySelector("#game-feedback"),
          document.querySelector("#playable-feedback"),
          document.querySelector("#composition-feedback"),
          document.querySelector("#melody-feedback"),
          document.querySelector("#listening-result"),
        ].filter(Boolean);
        targets.forEach((node) => {
          node.textContent = message;
        });
        console.warn(message, error);
      }

      function groupNotesByInstrument(notes, fallbackInstrument) {
        const groups = new Map();
        notes.slice(0, 220).forEach((note) => {
          const name = normalizeSoundfontInstrument(note.instrument || fallbackInstrument || "acoustic_grand_piano");
          if (!groups.has(name)) groups.set(name, []);
          groups.get(name).push(note);
        });
        return groups;
      }

      async function playAudioClipSequence(sequence) {
        const clips = sequence
          .map((item) => item && item.audio_clip_url ? String(item.audio_clip_url) : "")
          .filter(Boolean);
        if (!clips.length) return false;
        if (activeClipAudio) {
          try {
            activeClipAudio.pause();
            activeClipAudio.currentTime = 0;
          } catch (_error) {}
          activeClipAudio = null;
        }
        for (const clip of clips) {
          const audio = new Audio(clip);
          activeClipAudio = audio;
          audio.preload = "auto";
          await new Promise((resolve) => {
            const cleanup = () => {
              audio.onended = null;
              audio.onerror = null;
              resolve();
            };
            audio.onended = cleanup;
            audio.onerror = cleanup;
            primeMediaElementPlayback(audio, `audio-clip:${clip}`).catch((error) => {
              console.warn("Audio clip playback failed.", error);
              resolve();
            });
          });
        }
        activeClipAudio = null;
        return true;
      }

      async function playFallbackInstrumentNotes(notes, instrumentName, articulation = "auto") {
        if (!notes.length) return;
        await ensureAudioReady(`fallback-playback:${instrumentName || "default"}`);
        const startOffset = audioContext.currentTime + 0.08;
        notes.slice(0, 220).forEach((note) => playFallbackInstrumentNote(note, startOffset, instrumentName, articulation));
      }

      function instrumentProfile(instrumentName, articulation) {
        const sampledInstrument = normalizeSoundfontInstrument(instrumentName);
        const resolved = resolveArticulation(sampledInstrument || "acoustic_grand_piano", articulation || "auto");
        const profiles = {
          acoustic_grand_piano: { type: "triangle", attack: 0.012, release: 0.28, filter: 2300, vibrato: 0, partials: [1, 0.32, 0.1] },
          violin: { type: "sawtooth", attack: 0.12, release: 0.22, filter: 1700, vibrato: 5, partials: [0.75, 0.22, 0.08] },
          cello: { type: "sawtooth", attack: 0.14, release: 0.28, filter: 1200, vibrato: 4, partials: [0.82, 0.18, 0.06] },
          flute: { type: "sine", attack: 0.08, release: 0.18, filter: 1800, vibrato: 3.5, partials: [1, 0.08, 0.02] },
          clarinet: { type: "square", attack: 0.06, release: 0.2, filter: 1350, vibrato: 2.5, partials: [0.68, 0.18, 0.05] },
          koto: { type: "triangle", attack: 0.006, release: 0.7, filter: 3000, vibrato: 0, partials: [0.95, 0.42, 0.18] },
          acoustic_guitar_nylon: { type: "triangle", attack: 0.01, release: 0.55, filter: 2100, vibrato: 0, partials: [0.82, 0.34, 0.12] },
          xylophone: { type: "sine", attack: 0.004, release: 0.18, filter: 4200, vibrato: 0, partials: [1, 0.55, 0.24] },
        };
        const profile = profiles[sampledInstrument] || profiles.acoustic_grand_piano;
        if (resolved === "staccato") return { ...profile, release: Math.min(profile.release, 0.16) };
        if (resolved === "legato") return { ...profile, attack: Math.max(profile.attack, 0.06), release: Math.max(profile.release, 0.24) };
        if (resolved === "pluck") return { ...profile, attack: 0.006, release: Math.max(profile.release, 0.45) };
        return profile;
      }

      function playFallbackInstrumentNote(note, startOffset, instrumentName, articulation) {
        const profile = instrumentProfile(instrumentName, articulation);
        const start = startOffset + Number(note.start || 0);
        const duration = Math.min(Number(note.duration || 0.45), 3.2);
        const baseFrequency = 440 * Math.pow(2, (Number(note.pitch || 60) - 69) / 12);
        const output = audioContext.createGain();
        const filter = audioContext.createBiquadFilter();
        const velocityGain = Math.max(0.035, Number(note.velocity || 80) / 820);

        filter.type = "lowpass";
        filter.frequency.setValueAtTime(profile.filter, start);
        filter.frequency.exponentialRampToValueAtTime(Math.max(500, profile.filter * 0.55), start + duration + profile.release);

        output.gain.setValueAtTime(0.0001, start);
        output.gain.linearRampToValueAtTime(velocityGain, start + profile.attack);
        output.gain.setValueAtTime(velocityGain * 0.74, start + Math.min(duration, 0.22));
        output.gain.exponentialRampToValueAtTime(0.0001, start + duration + profile.release);

        profile.partials.forEach((gainValue, index) => {
          const oscillator = audioContext.createOscillator();
          const partialGain = audioContext.createGain();
          oscillator.frequency.value = baseFrequency * (index + 1);
          oscillator.type = index === 0 ? profile.type : "sine";
          partialGain.gain.value = gainValue;
          if (profile.vibrato) {
            const vibrato = audioContext.createOscillator();
            const vibratoGain = audioContext.createGain();
            vibrato.frequency.value = profile.vibrato;
            vibratoGain.gain.value = 5;
            vibrato.connect(vibratoGain);
            vibratoGain.connect(oscillator.detune);
            vibrato.start(start);
            vibrato.stop(start + duration + profile.release);
          }
          oscillator.connect(partialGain);
          partialGain.connect(filter);
          oscillator.start(start);
          oscillator.stop(start + duration + profile.release + 0.04);
        });

        filter.connect(output);
        output.connect(audioContext.destination);
      }

      async function playPianoNotes(notes) {
        if (!notes.length) return;
        await ensureAudioReady("piano-playback");
        const startOffset = audioContext.currentTime + 0.08;
        notes.slice(0, 220).forEach((note) => playPianoNote(note, startOffset));
      }

      function playPianoNote(note, startOffset) {
        const start = startOffset + Number(note.start || 0);
        const duration = Math.min(Number(note.duration || 0.45), 2.4);
        const baseFrequency = 440 * Math.pow(2, (Number(note.pitch || 60) - 69) / 12);
        const output = audioContext.createGain();
        const filter = audioContext.createBiquadFilter();
        const velocityGain = Math.max(0.045, Number(note.velocity || 80) / 760);

        filter.type = "lowpass";
        filter.frequency.setValueAtTime(2600, start);
        filter.frequency.exponentialRampToValueAtTime(900, start + duration + 0.18);

        output.gain.setValueAtTime(0.0001, start);
        output.gain.exponentialRampToValueAtTime(velocityGain, start + 0.012);
        output.gain.exponentialRampToValueAtTime(Math.max(0.012, velocityGain * 0.28), start + 0.12);
        output.gain.exponentialRampToValueAtTime(0.0001, start + duration + 0.24);

        [
          { ratio: 1, gain: 1, detune: -4, type: "triangle" },
          { ratio: 2, gain: 0.34, detune: 3, type: "sine" },
          { ratio: 3, gain: 0.12, detune: 0, type: "sine" },
        ].forEach((partial) => {
          const oscillator = audioContext.createOscillator();
          const partialGain = audioContext.createGain();
          oscillator.frequency.value = baseFrequency * partial.ratio;
          oscillator.detune.value = partial.detune;
          oscillator.type = partial.type;
          partialGain.gain.value = partial.gain;
          oscillator.connect(partialGain);
          partialGain.connect(filter);
          oscillator.start(start);
          oscillator.stop(start + duration + 0.28);
        });

        filter.connect(output);
        output.connect(audioContext.destination);
      }

      function playNote(note, startOffset, oscillatorTypeValue) {
        const oscillator = audioContext.createOscillator();
        const gain = audioContext.createGain();
        const start = startOffset + Number(note.start || 0);
        const duration = Math.min(Number(note.duration || 0.4), 2.2);

        oscillator.frequency.value = 440 * Math.pow(2, (Number(note.pitch || 60) - 69) / 12);
        oscillator.type = oscillatorTypeValue || "triangle";
        gain.gain.setValueAtTime(0.0001, start);
        gain.gain.exponentialRampToValueAtTime(Math.max(0.04, Number(note.velocity || 80) / 780), start + 0.03);
        gain.gain.exponentialRampToValueAtTime(0.0001, start + duration);
        oscillator.connect(gain);
        gain.connect(audioContext.destination);
        oscillator.start(start);
        oscillator.stop(start + duration + 0.04);
      }

      function oscillatorType(instrument) {
        return {
          piano: "triangle",
          violin: "sawtooth",
          guzheng: "triangle",
          flute: "sine",
        }[instrument] || "triangle";
      }

      installAudioActivationHooks();
      renderChrome();
      app.innerHTML = renderLessonBrief() + renderMainActivity();
      bindListening();
      bindPerformance();
      bindCreation();
      bindMusicGame();
    </script>
  </body>
</html>
"""

    return (
        template.replace("__TITLE__", title)
        .replace("__SUBTITLE__", subtitle)
        .replace("__TEMPLATE_ID__", template_id)
        .replace("__TEMPLATE_ROLE__", template_role)
        .replace("__SPEC__", safe_spec)
    )
