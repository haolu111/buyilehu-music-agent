import manifestData from "../../../../contracts/music/instrument-skin-manifest.v1.json";
import { runtimeAssetUrl } from "../../shared/runtimeAssets";

export type InstrumentSkinMetadata = {
  instrumentId: string;
  path: string;
  canvas: { width: number; height: number };
  contentBounds: { x: number; y: number; width: number; height: number };
  visualCenter: { x: number; y: number };
  safePadding: number;
  sha256: string;
  sizeBytes: number;
};

export const INSTRUMENT_SKIN_MANIFEST = manifestData.assets as InstrumentSkinMetadata[];
export const INSTRUMENT_SKIN_URLS: Record<string, string> = {
  virtual_frame_drum: runtimeAssetUrl("/runtime-assets/virtual-instruments/skins/virtual-frame-drum.webp"),
  virtual_snare_drum: runtimeAssetUrl("/runtime-assets/virtual-instruments/skins/virtual-snare-drum.webp"),
  virtual_woodblock: runtimeAssetUrl("/runtime-assets/virtual-instruments/skins/virtual-woodblock.webp"),
  virtual_shaker: runtimeAssetUrl("/runtime-assets/virtual-instruments/skins/virtual-shaker.webp"),
  virtual_triangle: runtimeAssetUrl("/runtime-assets/virtual-instruments/skins/virtual-triangle.webp"),
  virtual_tambourine: runtimeAssetUrl("/runtime-assets/virtual-instruments/skins/virtual-tambourine.webp"),
};

export function getInstrumentSkinUrl(instrumentId: string): string | null {
  return INSTRUMENT_SKIN_URLS[instrumentId] ?? null;
}

export function getInstrumentSkinMetadata(instrumentId: string): InstrumentSkinMetadata | null {
  return INSTRUMENT_SKIN_MANIFEST.find((asset) => asset.instrumentId === instrumentId) ?? null;
}
