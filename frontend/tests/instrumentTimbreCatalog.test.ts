import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import {
  EXACT_TIMBRE_DEFINITIONS,
  INSTRUMENT_TIMBRE_CATALOG_VERSION,
  PENDING_EXACT_TIMBRE_DEFINITIONS,
  SAMPLE_LIBRARY
} from "../src/shared/instrumentTimbreCatalog";

assert.equal(INSTRUMENT_TIMBRE_CATALOG_VERSION, "instrument_timbre_catalog_v1");
assert.deepEqual(
  EXACT_TIMBRE_DEFINITIONS.map((item) => item.id),
  ["piano", "acoustic_guitar", "violin", "cello", "flute", "clarinet", "oboe", "trumpet", "french_horn", "accordion", "harp", "xylophone"]
);
assert.equal(new Set(EXACT_TIMBRE_DEFINITIONS.map((item) => item.playbackInstrument)).size, 12);
assert.equal(EXACT_TIMBRE_DEFINITIONS.every((item) => item.sampleFidelity === "exact_open_sample"), true);
assert.deepEqual(
  new Set(EXACT_TIMBRE_DEFINITIONS.map((item) => item.familyId)),
  new Set(["keyboard", "plucked_string", "bowed_string", "woodwind", "brass", "free_reed", "percussion"])
);

assert.equal(SAMPLE_LIBRARY.license, "CC BY 3.0");
assert.match(SAMPLE_LIBRARY.licenseUrl, /^https:\/\/creativecommons\.org\/licenses\/by\/3\.0/);
assert.ok(SAMPLE_LIBRARY.attribution);
assert.deepEqual(PENDING_EXACT_TIMBRE_DEFINITIONS, []);

const root = dirname(dirname(fileURLToPath(import.meta.url)));
for (const item of EXACT_TIMBRE_DEFINITIONS) {
  assert.equal(item.preview.offsets.length >= 4, true, `${item.label} 应有完整试听短句`);
  assert.equal(
    existsSync(join(root, "..", "app", "static", "assets", "midi-js-soundfonts", "FluidR3_GM", `${item.playbackInstrument}-mp3.js`)),
    true,
    `${item.label} 的本地 SoundFont 文件应存在`
  );
}
const attribution = readFileSync(join(root, "..", "app", "static", "assets", "midi-js-soundfonts", "FluidR3_GM", "ATTRIBUTION.md"), "utf8");
assert.match(attribution, /CC BY 3\.0/);
