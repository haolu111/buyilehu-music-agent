from __future__ import annotations

import argparse
import shutil
from pathlib import Path


NEW_RUNTIME_MARKERS = (
    "student-game-root",
    "react_student_runtime",
    "__STUDENT_GAME_STATE__",
)

LEGACY_GAME_MARKERS = (
    "Template_MusicGame",
    ".game-hero",
    "__TEMPLATE_GAME_STATE__",
    "renderPlayableMusicMission",
    "student-game-brief",
)

PRODUCTION_TEMPLATE_IDS = (
    "beat_guardian_core",
    "pitch_ladder_core",
    "rhythm_echo_core",
    "solfege_target_core",
    "timbre_detective_core",
)


def is_legacy_game_output(tool_dir: Path) -> bool:
    index_path = tool_dir / "index.html"
    if not index_path.is_file():
        return False
    html_text = index_path.read_text(encoding="utf-8", errors="ignore")
    has_new_runtime = any(marker in html_text for marker in NEW_RUNTIME_MARKERS)
    if has_new_runtime:
        return False
    has_legacy_marker = any(marker in html_text for marker in LEGACY_GAME_MARKERS)
    has_production_template_id = any(template_id in html_text for template_id in PRODUCTION_TEMPLATE_IDS)
    return has_legacy_marker or has_production_template_id


def find_legacy_game_outputs(generated_tools_dir: Path) -> list[Path]:
    if not generated_tools_dir.exists():
        return []
    return sorted(
        path
        for path in generated_tools_dir.iterdir()
        if path.is_dir() and is_legacy_game_output(path)
    )


def cleanup_legacy_game_outputs(generated_tools_dir: Path, *, delete: bool = False) -> list[Path]:
    matches = find_legacy_game_outputs(generated_tools_dir)
    if delete:
        for path in matches:
            shutil.rmtree(path)
    return matches


def main() -> int:
    parser = argparse.ArgumentParser(description="Find or delete legacy low-quality music game outputs.")
    parser.add_argument(
        "generated_tools_dir",
        nargs="?",
        default=str(Path(__file__).resolve().parents[1] / "app" / "output" / "generated_tools"),
        help="Directory containing generated tool output folders.",
    )
    parser.add_argument("--delete", action="store_true", help="Delete matching legacy output directories.")
    args = parser.parse_args()

    root = Path(args.generated_tools_dir)
    matches = cleanup_legacy_game_outputs(root, delete=args.delete)
    action = "deleted" if args.delete else "would_delete"
    for path in matches:
        print(f"{action}\t{path}")
    print(f"{action}_count\t{len(matches)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
