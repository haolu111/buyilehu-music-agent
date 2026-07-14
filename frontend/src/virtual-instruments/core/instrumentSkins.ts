import manifestData from "../../../../contracts/music/instrument-skin-manifest.v1.json";

export type InstrumentSkinMetadata = {
  instrumentId: string;
  assetRole?: "chassis";
  path: string;
  canvas: { width: number; height: number };
  contentBounds: { x: number; y: number; width: number; height: number };
  visualCenter: { x: number; y: number };
  safePadding: number;
  sha256: string;
  sizeBytes: number;
};

const allInstrumentAssets = manifestData.assets as InstrumentSkinMetadata[];
export const INSTRUMENT_SKIN_MANIFEST = allInstrumentAssets.filter((asset) => asset.assetRole !== "chassis");
export const INSTRUMENT_CHASSIS_MANIFEST = allInstrumentAssets.filter((asset) => asset.assetRole === "chassis");
export const INSTRUMENT_SKIN_URLS: Record<string, string> = {
  virtual_frame_drum: "/runtime-assets/virtual-instruments/skins/virtual-frame-drum.webp",
  virtual_snare_drum: "/runtime-assets/virtual-instruments/skins/virtual-snare-drum.webp",
  virtual_woodblock: "/runtime-assets/virtual-instruments/skins/virtual-woodblock.webp",
  virtual_shaker: "/runtime-assets/virtual-instruments/skins/virtual-shaker.webp",
  virtual_triangle: "/runtime-assets/virtual-instruments/skins/virtual-triangle.webp",
  virtual_tambourine: "/runtime-assets/virtual-instruments/skins/virtual-tambourine.webp",
};

export const INSTRUMENT_CHASSIS_URLS: Record<string, string> = {
  virtual_xylophone: "/runtime-assets/virtual-instruments/skins/virtual-xylophone-chassis.webp",
  virtual_marimba: "/runtime-assets/virtual-instruments/skins/virtual-marimba-chassis.webp",
  virtual_glockenspiel: "/runtime-assets/virtual-instruments/skins/virtual-glockenspiel-chassis.webp",
};

export function getInstrumentSkinUrl(instrumentId: string): string | null {
  return INSTRUMENT_SKIN_URLS[instrumentId] ?? null;
}

export function getInstrumentSkinMetadata(instrumentId: string): InstrumentSkinMetadata | null {
  return INSTRUMENT_SKIN_MANIFEST.find((asset) => asset.instrumentId === instrumentId && asset.assetRole !== "chassis") ?? null;
}

export function getInstrumentChassisUrl(instrumentId: string): string | null {
  return INSTRUMENT_CHASSIS_URLS[instrumentId] ?? null;
}
