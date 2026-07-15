import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { templateVisualPackForConfig } from "../src/student-game/templateVisualAssets";

function assertEqual(actual: unknown, expected: unknown, label: string) {
  if (actual !== expected) {
    throw new Error(`${label}: expected ${String(expected)}, got ${String(actual)}`);
  }
}

function assert(condition: boolean, label: string) {
  if (!condition) throw new Error(label);
}

const repoRoot = join(dirname(fileURLToPath(import.meta.url)), "..", "..", "..");

const cases: Array<[string, string]> = [
  ["beat_guardian_core", "节拍守卫"],
  ["rhythm_echo_core", "节奏复刻"],
  ["solfege_target_core", "唱名打靶"],
  ["timbre_detective_core", "音色侦探"],
  ["form_treasure_core", "曲式寻宝"],
  ["composition_puzzle_core", "composition-puzzle"]
];

for (const [templateId, sourcePack] of cases) {
  const pack = templateVisualPackForConfig(undefined, templateId);
  assertEqual(pack.sourcePack, sourcePack, `${templateId} source pack`);

  const urls = [
    pack.background,
    pack.poses?.idle,
    pack.poses?.action,
    pack.poses?.miss,
    pack.poses?.win,
    ...(pack.props || []),
    ...(pack.rewards || [])
  ].filter((value): value is string => typeof value === "string" && value.length > 0);

  assert(urls.length >= 29, `${templateId} exposes the full extracted asset set`);
  for (const url of urls) {
    assert(url.startsWith("/static/assets/"), `${templateId} uses static asset URL: ${url}`);
    const localPath = join(repoRoot, "app", url.replace(/^\/static\//, "static/"));
    assert(existsSync(localPath), `${templateId} asset exists on disk: ${url}`);
  }
}
