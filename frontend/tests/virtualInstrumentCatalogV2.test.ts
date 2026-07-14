import {
  AUDIO_LICENSE_MANIFEST_VERSION,
  VIRTUAL_INSTRUMENT_CATALOG_VERSION,
  VIRTUAL_INSTRUMENT_DEFINITIONS,
  getVirtualInstrumentDefinition,
  listAuditedInstrumentAudioAssets,
  resolveVirtualInstrumentId,
  PERCUSSION_GRID_DEFINITION,
} from "../src/virtual-instruments/core/virtualInstrumentCatalog";

function assertEqual<T>(actual: T, expected: T, label: string) {
  if (actual !== expected) throw new Error(`${label}: expected ${String(expected)}, got ${String(actual)}`);
}

function assertDeepEqual(actual: unknown, expected: unknown, label: string) {
  const left = JSON.stringify(actual);
  const right = JSON.stringify(expected);
  if (left !== right) throw new Error(`${label}: expected ${right}, got ${left}`);
}

const ids = [
  "virtual_piano",
  "virtual_xylophone",
  "virtual_marimba",
  "virtual_glockenspiel",
  "virtual_frame_drum",
  "virtual_snare_drum",
  "virtual_woodblock",
  "virtual_shaker",
  "virtual_triangle",
  "virtual_tambourine",
];

assertEqual(VIRTUAL_INSTRUMENT_CATALOG_VERSION, "virtual_instrument_catalog_v2", "catalog version");
assertDeepEqual(VIRTUAL_INSTRUMENT_DEFINITIONS.map((item) => item.id), ids, "catalog has the locked ten instruments");
assertDeepEqual(getVirtualInstrumentDefinition("virtual_piano").pitchRange, { minMidi: 48, maxMidi: 83 }, "piano range");
assertDeepEqual(getVirtualInstrumentDefinition("virtual_xylophone").layoutModes, ["chromatic", "diatonic", "pentatonic"], "xylophone layouts");
assertEqual(resolveVirtualInstrumentId("simple_keyboard"), "virtual_piano", "legacy keyboard alias");
assertEqual(resolveVirtualInstrumentId("virtual_hand_drum"), "virtual_snare_drum", "legacy drum alias");
assertDeepEqual(
  getVirtualInstrumentDefinition("virtual_snare_drum").zones.map((zone) => zone.midi),
  [38, 37],
  "snare uses GM acoustic snare and side-stick notes",
);
assertDeepEqual(
  getVirtualInstrumentDefinition("virtual_triangle").zones.map((zone) => zone.midi),
  [81, 80],
  "triangle uses GM open and muted triangle notes",
);
assertDeepEqual(PERCUSSION_GRID_DEFINITION.tileCount, { min: 2, max: 6 }, "shared contract locks the classroom grid to two through six instruments");
assertEqual(getVirtualInstrumentDefinition("virtual_piano").performanceSurface?.supportsGlissando, true, "piano contract exposes glissando capability");
assertEqual(getVirtualInstrumentDefinition("virtual_xylophone").performanceSurface?.defaultLayoutMode, "diatonic", "mallet contract defaults to classroom diatonic mode");
assertEqual(getVirtualInstrumentDefinition("virtual_xylophone").skin.chassisAssetId, "virtual_xylophone_chassis_v1", "xylophone contract references its image2 chassis");

assertEqual(AUDIO_LICENSE_MANIFEST_VERSION, "instrument_audio_license_manifest_v1", "audio manifest version");
const assets = listAuditedInstrumentAudioAssets();
assertEqual(assets.length, 10, "every instrument has one audited audio bundle");
assertEqual(assets.every((asset) => asset.status === "audited"), true, "all audio is audited");
assertEqual(assets.find((asset) => asset.instrumentId === "virtual_frame_drum")?.primary.format, "sf2", "frame drum uses its exact custom CC0 bank");
assertEqual(assets.filter((asset) => asset.instrumentId !== "virtual_frame_drum").every((asset) => asset.primary.format === "sf3"), true, "other primary audio uses trimmed sf3");
assertEqual(
  assets.slice(0, 4).every((asset) => asset.fallback.format === "midi-js-mp3"),
  true,
  "pitched fallback packs use compressed MIDI-JS samples",
);
assertEqual(
  assets.slice(4).every((asset) => asset.fallback.format === "legacy-wav-map"),
  true,
  "percussion fallback packs honestly declare their rendered WAV sample maps",
);
