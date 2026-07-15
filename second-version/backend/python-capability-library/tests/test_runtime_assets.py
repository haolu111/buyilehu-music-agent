from __future__ import annotations

import unittest
from pathlib import Path


class RuntimeAssetsTests(unittest.TestCase):
    def test_required_audio_assets_are_packaged_and_served(self) -> None:
        root = Path(__file__).resolve().parents[1]
        expected_files = [
            "virtual-instruments/audio/virtual_piano.sf3",
            "virtual-instruments/audio/virtual_piano-mp3-map.js",
            "virtual-instruments/audio/virtual_frame_drum.sf2",
            "midi-js-soundfonts/FluidR3_GM/acoustic_grand_piano-mp3.js",
            "soundfont-player/soundfont-player.js",
        ]

        for relative_path in expected_files:
            self.assertTrue((root / "app" / "static" / "assets" / relative_path).is_file())

        main_module = (root / "app" / "main.py").read_text(encoding="utf-8")
        self.assertIn('"/runtime-assets"', main_module)


if __name__ == "__main__":
    unittest.main()
