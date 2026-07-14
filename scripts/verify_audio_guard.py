from __future__ import annotations

import os
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _generated_tools_roots() -> list[Path]:
    roots: list[Path] = []
    configured = os.environ.get("MUSIC_AGENT_OUTPUT_DIR", "").strip()
    if configured:
        roots.append(Path(configured).expanduser() / "generated_tools")
    try:
        from app.services.runtime_paths import get_output_dir

        roots.append(get_output_dir() / "generated_tools")
    except Exception:
        pass
    roots.append(PROJECT_ROOT / "app" / "output" / "generated_tools")

    unique: list[Path] = []
    seen: set[Path] = set()
    for root in roots:
        resolved = root.resolve()
        if resolved not in seen:
            unique.append(resolved)
            seen.add(resolved)
    return unique


def main() -> int:
    audio_pages = []
    missing_guard = []
    missing_soundfont_policy = []

    roots = _generated_tools_roots()
    for path in sorted({page for root in roots if root.exists() for page in root.rglob("index.html")}):
        text = path.read_text(encoding="utf-8")
        has_audio = (
            "buyilehu-audio-policy" in text
            or "__BUYILEHU_AUDIO_POLICY__" in text
            or "AudioContext" in text
            or ".play(" in text
            or "Soundfont.instrument" in text
        )
        if not has_audio:
            continue
        audio_pages.append(path)
        has_policy = (
            "soundfont_first_hybrid_audio" in text
            and "/runtime-assets/soundfont-player/soundfont-player.js" in text
            and "/runtime-assets/midi-js-soundfonts/FluidR3_GM/" in text
        )
        if not has_policy:
            missing_soundfont_policy.append(path)
        if "__musicAgentAudioGuardInstalled" not in text and not has_policy:
            missing_guard.append(path)

    print(f"audio_pages={len(audio_pages)}")
    print("roots=" + ",".join(str(root) for root in roots))
    print(f"missing_guard={len(missing_guard)}")
    print(f"missing_soundfont_policy={len(missing_soundfont_policy)}")
    for path in missing_soundfont_policy:
        print(path)
    for path in missing_guard:
        print(path)

    return 1 if missing_guard or missing_soundfont_policy else 0


if __name__ == "__main__":
    raise SystemExit(main())
