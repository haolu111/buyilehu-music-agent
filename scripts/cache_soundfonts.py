from __future__ import annotations

import os
import shutil
import sys
import urllib.request
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
APP_DIR = ROOT_DIR / "app"
STATIC_ASSETS_DIR = APP_DIR / "static" / "assets"
RUNTIME_ASSETS_DIR = ROOT_DIR / ".music-agent-runtime" / "assets"

HF_SOUNDFONT_REPO = os.environ.get("MUSIC_AGENT_SOUNDFONT_REPO", "projectlosangeles/soundfonts4u")
HF_SOUNDFONT_FILE = os.environ.get("MUSIC_AGENT_SOUNDFONT_FILE", "Essential Keys-C-v1.0.sf2")

BROWSER_INSTRUMENTS = [
    "acoustic_grand_piano",
    "acoustic_guitar_nylon",
    "violin",
    "cello",
    "flute",
    "clarinet",
    "oboe",
    "trumpet",
    "french_horn",
    "accordion",
    "orchestral_harp",
    "xylophone",
]


def copy_tree(source: Path, target: Path) -> None:
    if not source.exists():
        return
    for source_file in source.rglob("*"):
        if not source_file.is_file():
            continue
        relative = source_file.relative_to(source)
        target_file = target / relative
        target_file.parent.mkdir(parents=True, exist_ok=True)
        if target_file.exists() and target_file.stat().st_size == source_file.stat().st_size:
            continue
        shutil.copy2(source_file, target_file)


def download_file(urls: list[str], target: Path) -> bool:
    if target.exists() and target.stat().st_size > 1024:
        return True
    target.parent.mkdir(parents=True, exist_ok=True)
    last_error = ""
    for url in urls:
        try:
            with urllib.request.urlopen(url, timeout=45) as response:
                data = response.read()
            if len(data) <= 1024:
                raise RuntimeError(f"Downloaded file is too small: {len(data)} bytes")
            tmp = target.with_suffix(target.suffix + ".tmp")
            tmp.write_bytes(data)
            tmp.replace(target)
            print(f"cached {target.relative_to(ROOT_DIR)} from {url}")
            return True
        except Exception as exc:
            last_error = str(exc)
    print(f"warning: could not cache {target.name}: {last_error}", file=sys.stderr)
    return False


def cache_browser_soundfonts() -> None:
    copy_tree(STATIC_ASSETS_DIR / "soundfont-player", RUNTIME_ASSETS_DIR / "soundfont-player")
    copy_tree(STATIC_ASSETS_DIR / "midi-js-soundfonts", RUNTIME_ASSETS_DIR / "midi-js-soundfonts")

    download_file(
        [
            "https://cdn.jsdelivr.net/npm/soundfont-player@0.15.7/dist/soundfont-player.js",
            "https://unpkg.com/soundfont-player@0.15.7/dist/soundfont-player.js",
        ],
        RUNTIME_ASSETS_DIR / "soundfont-player" / "soundfont-player.js",
    )

    for instrument in BROWSER_INSTRUMENTS:
        filename = f"{instrument}-mp3.js"
        static_target = STATIC_ASSETS_DIR / "midi-js-soundfonts" / "FluidR3_GM" / filename
        if download_file(
            [
                f"https://registry.npmmirror.com/midi-js-soundfonts/latest/files/FluidR3_GM/{filename}",
                f"https://cdn.jsdelivr.net/gh/gleitz/midi-js-soundfonts@gh-pages/FluidR3_GM/{filename}",
                f"https://gleitz.github.io/midi-js-soundfonts/FluidR3_GM/{filename}",
            ],
            static_target,
        ):
            runtime_target = RUNTIME_ASSETS_DIR / "midi-js-soundfonts" / "FluidR3_GM" / filename
            runtime_target.parent.mkdir(parents=True, exist_ok=True)
            if not runtime_target.exists() or runtime_target.stat().st_size != static_target.stat().st_size:
                shutil.copy2(static_target, runtime_target)


def cache_server_sf2() -> None:
    soundfont_dir = RUNTIME_ASSETS_DIR / "soundfonts"
    soundfont_dir.mkdir(parents=True, exist_ok=True)

    configured = os.environ.get("MUSIC_AGENT_SOUNDFONT_PATH", "").strip()
    if configured:
        configured_path = Path(configured).expanduser()
        if configured_path.exists():
            print(f"using configured SF2: {configured_path}")
            return

    target = soundfont_dir / HF_SOUNDFONT_FILE
    if target.exists() and target.stat().st_size > 1024:
        print(f"server SF2 already cached: {target.relative_to(ROOT_DIR)}")
        return

    try:
        from huggingface_hub import hf_hub_download

        path = hf_hub_download(
            repo_id=HF_SOUNDFONT_REPO,
            filename=HF_SOUNDFONT_FILE,
            repo_type="dataset",
            local_dir=str(soundfont_dir),
        )
        print(f"cached server SF2 from Hugging Face: {Path(path).relative_to(ROOT_DIR)}")
        return
    except Exception as exc:
        print(f"warning: Hugging Face SF2 cache failed: {exc}", file=sys.stderr)

    try:
        import pretty_midi

        bundled = Path(pretty_midi.__file__).resolve().parent / "TimGM6mb.sf2"
        if bundled.exists():
            fallback_target = soundfont_dir / bundled.name
            shutil.copy2(bundled, fallback_target)
            print(f"cached bundled fallback SF2: {fallback_target.relative_to(ROOT_DIR)}")
            return
    except Exception as exc:
        print(f"warning: bundled fallback SF2 unavailable: {exc}", file=sys.stderr)

    raise SystemExit("No usable server SF2 was cached.")


def main() -> None:
    cache_browser_soundfonts()
    cache_server_sf2()
    print("SoundFont cache is ready.")


if __name__ == "__main__":
    main()
