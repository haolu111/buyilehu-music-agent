import { FIXED_TABLET_STAGE, calculateTabletStageLayout, classifyStageDevice } from "../src/virtual-instruments/core/fixedTabletStage";
import { INSTRUMENT_TOUCH_REGIONS, hitTestInstrumentTouchRegions, validateTouchRegions } from "../src/virtual-instruments/core/instrumentTouchMap";
import { INSTRUMENT_SKIN_MANIFEST } from "../src/virtual-instruments/core/instrumentSkins";

function equal<T>(actual: T, expected: T, label: string) {
  if (actual !== expected) throw new Error(`${label}: expected ${String(expected)}, got ${String(actual)}`);
}

equal(FIXED_TABLET_STAGE.logicalWidth, 1024, "stage width is fixed");
equal(FIXED_TABLET_STAGE.logicalHeight, 768, "stage height is fixed");
const layout = calculateTabletStageLayout(1200, 800);
equal(layout.scale, 800 / 768, "stage uses contain scaling");
equal(Math.round(layout.renderedWidth), 1067, "stage keeps its aspect ratio");
equal(classifyStageDevice(390, 844), "phone_unsupported", "phones are rejected");
equal(classifyStageDevice(768, 1024), "tablet_portrait", "portrait tablet asks for rotation");
equal(classifyStageDevice(1024, 768), "supported", "landscape tablet is supported");

validateTouchRegions(INSTRUMENT_TOUCH_REGIONS);
equal(INSTRUMENT_TOUCH_REGIONS.some((region) => region.gesture === "hold_roll"), true, "roll regions are present");
equal(INSTRUMENT_TOUCH_REGIONS.some((region) => region.gesture === "choke"), true, "triangle choke region is present");
equal(hitTestInstrumentTouchRegions("virtual_frame_drum", 0.5, 0.5)?.zoneId, "center", "drum center wins nested hit test");
equal(hitTestInstrumentTouchRegions("virtual_frame_drum", 0.5, 0.2)?.zoneId, "edge", "drum rim is independently playable");
equal(hitTestInstrumentTouchRegions("virtual_frame_drum", 0.03, 0.03), null, "transparent image margin stays silent");
equal(INSTRUMENT_SKIN_MANIFEST.length, 6, "six image2 skins have normalized metadata");
equal(INSTRUMENT_SKIN_MANIFEST.every((asset) => asset.canvas.width === 1024 && asset.canvas.height === 1024), true, "all skins share one audited canvas");
equal(INSTRUMENT_SKIN_MANIFEST.every((asset) => asset.contentBounds.width > 0 && asset.sha256.length === 64), true, "skin bounds and hashes are recorded");
