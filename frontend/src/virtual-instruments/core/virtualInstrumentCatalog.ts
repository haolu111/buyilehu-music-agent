import catalogData from "../../../../contracts/music/virtual-instrument-catalog.v2.json";
import licenseManifestData from "../../../../contracts/music/instrument-audio-license-manifest.v1.json";

export type VirtualInstrumentFamily = "keyboard" | "mallet" | "percussion";
export type VirtualInstrumentLayout = "piano" | "bars" | "pads";
export type VirtualInstrumentZoneAction = "note" | "one_shot" | "sustain" | "dampen" | "roll";

export type VirtualInstrumentZone = {
  id: string;
  label: string;
  midi: number;
  action: VirtualInstrumentZoneAction;
};

export type VirtualInstrumentDefinition = {
  id: string;
  name: string;
  family: VirtualInstrumentFamily;
  layout: VirtualInstrumentLayout;
  layoutModes: string[];
  soundPackId: string;
  pitchRange?: { minMidi: number; maxMidi: number };
  zones: VirtualInstrumentZone[];
  supportsMultiTouch: true;
  supportsRecording: true;
  skin: { kind: "structured_svg" | "image2_transparent"; assetId: string; chassisAssetId?: string };
  performanceSurface?:
    | { kind: "piano"; visibleOctavesLandscape: 2; visibleOctavesPortrait: 1; supportsGlissando: true; supportsSustain: true }
    | { kind: "mallet"; registerWindowSemitones: 12; defaultLayoutMode: "diatonic"; supportsRoll: true };
};

export type PercussionGridDefinition = {
  id: "virtual_percussion_grid";
  name: string;
  tileCount: { min: 2; max: 6 };
  teacherSelectsInstrumentAndZone: true;
  studentZonesPerTile: 1;
  requiresAuditedAudioAndImage: true;
};

export type InstrumentAudioAsset = {
  instrumentId: string;
  status: "audited" | "needs_review" | "blocked";
  sourceUrl: string;
  licenseId: string;
  commercialUse: boolean;
  redistribution: boolean;
  attribution: string;
  primary: { path: string; format: "sf3" | "sf2"; sha256: string; sizeBytes: number };
  fallback: { path: string; format: "midi-js-mp3" | "legacy-wav-map"; sha256: string; sizeBytes: number };
};

type CatalogData = {
  version: string;
  legacyAliases: Record<string, string>;
  instruments: VirtualInstrumentDefinition[];
  percussionGrid: PercussionGridDefinition;
};

type LicenseManifestData = {
  version: string;
  offlineBudgetBytes: number;
  assets: InstrumentAudioAsset[];
};

const catalog = catalogData as CatalogData;
const licenseManifest = licenseManifestData as LicenseManifestData;
const definitionsById = new Map(catalog.instruments.map((item) => [item.id, item]));

export const VIRTUAL_INSTRUMENT_CATALOG_VERSION = catalog.version;
export const AUDIO_LICENSE_MANIFEST_VERSION = licenseManifest.version;
export const VIRTUAL_INSTRUMENT_DEFINITIONS = catalog.instruments;
export const VIRTUAL_INSTRUMENT_OFFLINE_BUDGET_BYTES = licenseManifest.offlineBudgetBytes;
export const PERCUSSION_GRID_DEFINITION = catalog.percussionGrid;

export function resolveVirtualInstrumentId(value: unknown): string {
  const instrumentId = String(value ?? "").trim();
  const resolved = catalog.legacyAliases[instrumentId] ?? instrumentId;
  if (!definitionsById.has(resolved)) throw new Error(`Unknown virtual instrument v2 id: ${String(value)}`);
  return resolved;
}

export function getVirtualInstrumentDefinition(value: unknown): VirtualInstrumentDefinition {
  return definitionsById.get(resolveVirtualInstrumentId(value))!;
}

export function listInstrumentAudioAssets(): InstrumentAudioAsset[] {
  return licenseManifest.assets.map((item) => ({ ...item, primary: { ...item.primary }, fallback: { ...item.fallback } }));
}

export function listAuditedInstrumentAudioAssets(): InstrumentAudioAsset[] {
  return listInstrumentAudioAssets().filter((item) => item.status === "audited" && definitionsById.has(item.instrumentId));
}

export function getAuditedClassroomAudioAsset(instrumentOrUtilityId: string): InstrumentAudioAsset | null {
  return listInstrumentAudioAssets().find((item) => item.status === "audited" && item.instrumentId === instrumentOrUtilityId) ?? null;
}
