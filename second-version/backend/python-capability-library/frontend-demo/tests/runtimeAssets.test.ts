import { runtimeAssetUrl } from "../src/shared/runtimeAssets";

function assertEqual(actual: string, expected: string, label: string) {
  if (actual !== expected) throw new Error(`${label}: expected ${expected}, got ${actual}`);
}

assertEqual(
  runtimeAssetUrl("/runtime-assets/virtual-instruments/audio/virtual_piano.sf3", "./"),
  "./runtime-assets/virtual-instruments/audio/virtual_piano.sf3",
  "GitHub Pages loads runtime assets from the deployed project directory",
);
assertEqual(
  runtimeAssetUrl("/runtime-assets/soundfont-player/soundfont-player.js", "/"),
  "/runtime-assets/soundfont-player/soundfont-player.js",
  "the local development server keeps its root runtime-assets route",
);
