import {
  INSTRUMENT_SKIN_CALIBRATIONS,
  SKIN_CALIBRATION_ASSET_HASHES,
  clientPointToSkinPoint,
  hitTestInstrumentSkin,
  validateSkinCalibration,
} from "../src/virtual-instruments/core/instrumentSkinCalibration";

function equal<T>(actual: T, expected: T, label: string) {
  if (actual !== expected) throw new Error(`${label}: expected ${String(expected)}, got ${String(actual)}`);
}

const mapped = clientPointToSkinPoint(300, 250, { left: 100, top: 50, width: 400, height: 400 });
equal(mapped?.pixelX, 512, "client x maps to the 1024 skin canvas");
equal(mapped?.pixelY, 512, "client y maps to the 1024 skin canvas");
equal(clientPointToSkinPoint(90, 250, { left: 100, top: 50, width: 400, height: 400 }), null, "points outside the skin canvas are rejected");

equal(INSTRUMENT_SKIN_CALIBRATIONS.length, 6, "all six percussion skins are calibrated");
equal(SKIN_CALIBRATION_ASSET_HASHES.virtual_frame_drum, "d677d385a85a191f43f0e572cf4a7ce41cb4b6484e2971a7f2db14eb80424a05", "calibration locks the reviewed frame-drum image hash");
for (const calibration of INSTRUMENT_SKIN_CALIBRATIONS) validateSkinCalibration(calibration);

const opaque = () => 255;
const transparent = () => 0;
equal(hitTestInstrumentSkin("virtual_frame_drum", .5, .51, { alphaAt: opaque })?.zoneId, "center", "frame drum center maps to center sound");
equal(hitTestInstrumentSkin("virtual_frame_drum", .5, .51, { alphaAt: transparent }), null, "transparent pixels stay silent");
equal(hitTestInstrumentSkin("virtual_frame_drum", .03, .03, { alphaAt: opaque }), null, "semantic blank corners stay silent");

equal(hitTestInstrumentSkin("virtual_woodblock", .3, .49, { alphaAt: opaque })?.zoneId, "low", "large left woodblock maps to low MIDI 77 zone");
equal(hitTestInstrumentSkin("virtual_woodblock", .82, .5, { alphaAt: opaque })?.zoneId, "high", "small right woodblock maps to high MIDI 76 zone");

equal(hitTestInstrumentSkin("virtual_triangle", .33, .6, { alphaAt: opaque })?.zoneId, "open", "triangle body maps to open sound");
equal(hitTestInstrumentSkin("virtual_triangle", .5, .5, { alphaAt: transparent })?.zoneId, "open", "triangle visible interior uses the same open-sound region shown to students");
equal(hitTestInstrumentSkin("virtual_triangle", .86, .12, { alphaAt: transparent, gesture: "choke" })?.zoneId, "dampen", "visible choke control works independently of image alpha");

equal(hitTestInstrumentSkin("virtual_shaker", .52, .3, { alphaAt: opaque })?.zoneId, "short", "shaker body supports a tap");
equal(hitTestInstrumentSkin("virtual_shaker", .52, .3, { alphaAt: opaque, gesture: "hold_roll" })?.zoneId, "sustain", "same shaker body supports hold roll");
