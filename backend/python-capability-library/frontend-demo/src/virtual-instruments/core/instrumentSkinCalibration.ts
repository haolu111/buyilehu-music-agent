import { getInstrumentSkinMetadata } from "./instrumentSkins";
import { INSTRUMENT_TOUCH_REGIONS, pointInTouchShape, validateTouchRegions, type InstrumentTouchRegion, type TouchShape } from "./instrumentTouchMap";
import { getVirtualInstrumentDefinition } from "./virtualInstrumentCatalog";

export type InstrumentSkinCalibration = {
  instrumentId: string;
  assetSha256: string;
  calibrationVersion: number;
  coordinateSpace: "skin_canvas";
  canvas: { width: 1024; height: 1024 };
  contentBounds: { x: number; y: number; width: number; height: number };
  alphaHitPolicy: { enabled: true; alphaThreshold: number; semanticPaddingRatio: 0.08 };
  regions: InstrumentTouchRegion[];
};

export type SkinCanvasRect = { left: number; top: number; width: number; height: number };
export type SkinPoint = { normalizedX: number; normalizedY: number; pixelX: number; pixelY: number };
export type SkinHitOptions = {
  gesture?: InstrumentTouchRegion["gesture"];
  alphaAt: (normalizedX: number, normalizedY: number) => number;
  allowedZoneIds?: string[];
};

const instrumentIds = ["virtual_frame_drum", "virtual_snare_drum", "virtual_woodblock", "virtual_shaker", "virtual_triangle", "virtual_tambourine"];

export const SKIN_CALIBRATION_ASSET_HASHES: Record<string, string> = {
  virtual_frame_drum: "d677d385a85a191f43f0e572cf4a7ce41cb4b6484e2971a7f2db14eb80424a05",
  virtual_snare_drum: "129e22be1c201668de5c098174890ff5ef24ec144b05ac3ff12bbd20109c3757",
  virtual_woodblock: "8e1301937d41464f068d9266ab8bbc153e16c2f7f1eb715f14e354a0a57808f5",
  virtual_shaker: "3d90bc011a382b32fa568fbff75096497d7b79a2f737ebc464048111da7b5025",
  virtual_triangle: "94fc071579e27f7455e46d349fcb05c0364058eeb1ed4ddcb0dfdc6f51ef2458",
  virtual_tambourine: "2e8442bd13fbf3f886262305089260a6785f9273e717d37d4736dff5c086d74c",
};

export const INSTRUMENT_SKIN_CALIBRATIONS: InstrumentSkinCalibration[] = instrumentIds.map((instrumentId) => {
  const asset = getInstrumentSkinMetadata(instrumentId);
  if (!asset) throw new Error(`Missing skin metadata for ${instrumentId}`);
  return {
    instrumentId,
    assetSha256: SKIN_CALIBRATION_ASSET_HASHES[instrumentId],
    calibrationVersion: 2,
    coordinateSpace: "skin_canvas",
    canvas: { width: 1024, height: 1024 },
    contentBounds: { ...asset.contentBounds },
    alphaHitPolicy: { enabled: true, alphaThreshold: 12, semanticPaddingRatio: .08 },
    regions: INSTRUMENT_TOUCH_REGIONS.filter((region) => region.instrumentId === instrumentId),
  };
});

export function getInstrumentSkinCalibration(instrumentId: string): InstrumentSkinCalibration {
  const calibration = INSTRUMENT_SKIN_CALIBRATIONS.find((item) => item.instrumentId === instrumentId);
  if (!calibration) throw new Error(`Missing skin calibration for ${instrumentId}`);
  return calibration;
}

export function clientPointToSkinPoint(clientX: number, clientY: number, rect: SkinCanvasRect): SkinPoint | null {
  if (rect.width <= 0 || rect.height <= 0) return null;
  const normalizedX = (clientX - rect.left) / rect.width;
  const normalizedY = (clientY - rect.top) / rect.height;
  if (normalizedX < 0 || normalizedX > 1 || normalizedY < 0 || normalizedY > 1) return null;
  return { normalizedX, normalizedY, pixelX: Math.round(normalizedX * 1024), pixelY: Math.round(normalizedY * 1024) };
}

function pointInPaddedShape(shape: TouchShape, x: number, y: number, paddingRatio: number): boolean {
  if (shape.type === "rect") {
    const px = shape.width * paddingRatio; const py = shape.height * paddingRatio;
    return pointInTouchShape({ type: "rect", x: Math.max(0, shape.x - px), y: Math.max(0, shape.y - py), width: Math.min(1, shape.width + px * 2), height: Math.min(1, shape.height + py * 2) }, x, y);
  }
  if (shape.type === "circle") return pointInTouchShape({ ...shape, radius: Math.min(1, shape.radius * (1 + paddingRatio)) }, x, y);
  if (shape.type === "ellipse") return pointInTouchShape({ ...shape, rx: Math.min(1, shape.rx * (1 + paddingRatio)), ry: Math.min(1, shape.ry * (1 + paddingRatio)) }, x, y);
  if (shape.type === "ring") return pointInTouchShape({ ...shape, innerRadius: Math.max(0, shape.innerRadius * (1 - paddingRatio)), outerRadius: Math.min(1, shape.outerRadius * (1 + paddingRatio)) }, x, y);
  return pointInTouchShape(shape, x, y);
}

export function hitTestInstrumentSkin(instrumentId: string, normalizedX: number, normalizedY: number, options: SkinHitOptions): InstrumentTouchRegion | null {
  const calibration = getInstrumentSkinCalibration(instrumentId);
  const gesture = options.gesture ?? "tap";
  const allowed = options.allowedZoneIds ? new Set(options.allowedZoneIds) : null;
  return calibration.regions
    .filter((region) => region.gesture === gesture && (!allowed || allowed.has(region.zoneId)))
    .sort((left, right) => right.priority - left.priority)
    .find((region) => {
      if (!pointInPaddedShape(region.shape, normalizedX, normalizedY, calibration.alphaHitPolicy.semanticPaddingRatio)) return false;
      return region.hitSurface !== "skin_alpha" || options.alphaAt(normalizedX, normalizedY) >= calibration.alphaHitPolicy.alphaThreshold;
    }) ?? null;
}

export function validateSkinCalibration(calibration: InstrumentSkinCalibration): true {
  const asset = getInstrumentSkinMetadata(calibration.instrumentId);
  if (!asset || asset.sha256 !== calibration.assetSha256) throw new Error(`Skin asset changed; recalibration required: ${calibration.instrumentId}`);
  if (calibration.coordinateSpace !== "skin_canvas" || calibration.canvas.width !== 1024 || calibration.canvas.height !== 1024) throw new Error(`Invalid skin canvas: ${calibration.instrumentId}`);
  if (calibration.alphaHitPolicy.semanticPaddingRatio !== .08) throw new Error(`Invalid classroom touch padding: ${calibration.instrumentId}`);
  validateTouchRegions(calibration.regions);
  const zones = new Set(getVirtualInstrumentDefinition(calibration.instrumentId).zones.map((zone) => zone.id));
  if (!calibration.regions.every((region) => zones.has(region.zoneId))) throw new Error(`Calibration references an unknown sound zone: ${calibration.instrumentId}`);
  return true;
}

for (const calibration of INSTRUMENT_SKIN_CALIBRATIONS) validateSkinCalibration(calibration);
