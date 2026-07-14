from __future__ import annotations

import re
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: export_standalone_html.py <source_html> <target_html>", file=sys.stderr)
        return 2

    source = Path(sys.argv[1]).expanduser().resolve()
    target = Path(sys.argv[2]).expanduser().resolve()

    if not source.exists():
        print(f"source not found: {source}", file=sys.stderr)
        return 1

    html = source.read_text(encoding="utf-8")
    html = remove_runtime_script_tag(html)
    html = relax_soundfont_loading(html)
    html = inject_offline_notice(html)

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding="utf-8")
    print(target)
    return 0


def remove_runtime_script_tag(html: str) -> str:
    return re.sub(
        r"""\n?\s*<script\s+src="/runtime-assets/soundfont-player/soundfont-player\.js"[^>]*></script>\s*""",
        "\n",
        html,
        flags=re.IGNORECASE,
    )


def relax_soundfont_loading(html: str) -> str:
    start = "function loadSoundfont() {"
    end = "    // Play a note using Web Audio oscillator (fallback)"
    start_index = html.find(start)
    end_index = html.find(end)
    if start_index != -1 and end_index != -1 and end_index > start_index:
        replacement = (
            "function loadSoundfont() {\n"
            "      return new Promise((resolve) => {\n"
            "        console.warn('Offline standalone mode: external SoundFont assets are not bundled, using oscillator fallback');\n"
            "        resolve(false);\n"
            "      });\n"
            "    }\n\n"
        )
        html = html[:start_index] + replacement + html[end_index:]
    html = html.replace(
        "console.warn('Soundfont not available, will use oscillator fallback');",
        "console.warn('Offline standalone mode: Soundfont script is not bundled, using oscillator fallback');",
    )
    return html


def inject_offline_notice(html: str) -> str:
    marker = '<div class="game-subtitle">'
    insert = (
        '<div class="game-subtitle">'
        '离线分享版：双击即可打开，若没有本地音色资源会自动使用内置基础音色。'
        '</div>'
    )
    if "离线分享版" in html:
        return html
    return html.replace(marker, insert + "\n    " + marker, 1)


if __name__ == "__main__":
    raise SystemExit(main())
