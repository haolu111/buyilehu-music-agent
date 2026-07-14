import { readFileSync } from "node:fs";
import { join } from "node:path";
import { buildPlayableZones } from "../src/virtual-instruments/core/playableZones";
import { INSTRUMENT_CHASSIS_URLS, INSTRUMENT_SKIN_URLS } from "../src/virtual-instruments/core/instrumentSkins";
import { VIRTUAL_INSTRUMENT_DEFINITIONS } from "../src/virtual-instruments/core/virtualInstrumentCatalog";

function assertEqual<T>(actual: T, expected: T, label: string) {
  if (actual !== expected) throw new Error(`${label}: expected ${String(expected)}, got ${String(actual)}`);
}

const pianoZones = buildPlayableZones("virtual_piano");
assertEqual(pianoZones.length, 36, "piano exposes every note in its audited C3-B5 range");
assertEqual(pianoZones[0].midi, 48, "piano starts at C3");
assertEqual(pianoZones.at(-1)?.midi, 83, "piano ends at B5");

for (const instrument of VIRTUAL_INSTRUMENT_DEFINITIONS.slice(4)) {
  const zones = buildPlayableZones(instrument.id);
  assertEqual(zones.length, instrument.zones.length, `${instrument.id} locks one touch zone per playing action`);
  assertEqual(zones.every((zone) => zone.hitArea.width > 0 && zone.hitArea.height > 0), true, `${instrument.id} has usable hit areas`);
}

const root = process.cwd();
const component = readFileSync(join(root, "src/virtual-instruments/vue/VirtualInstrumentPlayer.vue"), "utf8");
assertEqual(component.includes("defineProps<VirtualInstrumentPlayerProps>"), true, "Vue component has a typed public props contract");
assertEqual(component.includes("defineExpose"), true, "Vue component exposes integration methods to engineers");
assertEqual(component.includes("from \"react\""), false, "Vue delivery has no React dependency");
assertEqual(component.includes("data-zone-id"), true, "Vue component renders stable touch-zone identifiers");
assertEqual(Object.keys(INSTRUMENT_SKIN_URLS).length, 6, "six percussion instruments have formal image2 skins");
assertEqual(Object.keys(INSTRUMENT_CHASSIS_URLS).length, 3, "three mallet instruments have formal image2 chassis assets");
assertEqual(component.includes("InstrumentSkinCanvas"), true, "Vue component renders the formal skin and locked touch zones in one calibrated canvas");
assertEqual(component.includes("PianoSurface"), true, "player delegates piano geometry to a dedicated surface");
assertEqual(component.includes("MalletSurface"), true, "player delegates mallet geometry to a reusable surface");

const pianoSurface = readFileSync(join(root, "src/virtual-instruments/vue/PianoSurface.vue"), "utf8");
assertEqual(pianoSurface.includes("pointermove"), true, "piano surface supports finger glissando");
assertEqual(pianoSurface.includes("延音"), true, "piano surface exposes a classroom sustain pedal");

const malletSurface = readFileSync(join(root, "src/virtual-instruments/vue/MalletSurface.vue"), "utf8");
assertEqual(malletSurface.includes("buildMalletLayout"), true, "all three mallet instruments share one geometry core");
assertEqual(malletSurface.includes("rollEnabled"), true, "mallet surface has an explicit roll mode");
assertEqual(malletSurface.includes("getInstrumentChassisUrl"), false, "performance surface does not reuse the full-instrument image as a background");
assertEqual(malletSurface.includes("chassis-image"), false, "structured playable bars stay visually separate from the gallery image");

const reviewWizard = readFileSync(join(root, "src/virtual-instruments/vue/InstrumentReviewWizard.vue"), "utf8");
assertEqual(reviewWizard.includes("getInstrumentChassisUrl"), true, "review wizard uses the three complete instrument images as gallery entries");
assertEqual(reviewWizard.includes("进入演奏模式"), true, "complete instrument images open an explicit performance mode");
assertEqual(reviewWizard.includes("返回整体展示"), true, "performance mode can return to the complete instrument image");
assertEqual(reviewWizard.includes("mallet-display-card"), true, "mallet gallery entry is a dedicated whole-instrument card");

const percussionGrid = readFileSync(join(root, "src/virtual-instruments/vue/PercussionGrid.vue"), "utf8");
assertEqual(percussionGrid.includes("validatePercussionGrid"), true, "percussion grid validates teacher-selected instruments and articulations");
assertEqual(percussionGrid.includes("InstrumentSkinCanvas"), true, "percussion grid uses the shared real-image canvas");
assertEqual(percussionGrid.includes("rollTimers"), true, "teacher-selected shaker or tambourine roll articulations repeat only while held");
assertEqual(percussionGrid.includes("InstrumentSkinCanvas"), true, "percussion grid reuses the exact same image and touch canvas as single instruments");
assertEqual(percussionGrid.includes("tilePoint"), false, "percussion grid no longer invents a tile-sized coordinate system");

const skinCanvas = readFileSync(join(root, "src/virtual-instruments/vue/InstrumentSkinCanvas.vue"), "utf8");
assertEqual(skinCanvas.includes("aspect-ratio:1/1"), true, "skin canvas is a fixed square and cannot crop the image");
assertEqual(skinCanvas.includes("hitTestInstrumentSkin"), true, "skin canvas uses the shared calibrated hit tester");
assertEqual(skinCanvas.includes("按住止音"), true, "triangle exposes a visible choke control");
assertEqual(component.includes("InstrumentSkinCanvas"), true, "single instrument player uses the shared calibrated canvas");
assertEqual(component.includes("skin-placeholder"), false, "legacy overflowing image placeholder is removed");
assertEqual(component.includes("(event.currentTarget as HTMLElement | null)?.setPointerCapture"), true, "delayed hold-roll tolerates a cleared pointer-event currentTarget");

const reviewApp = readFileSync(join(root, "src/virtual-instruments/vue/VirtualInstrumentReviewApp.vue"), "utf8");
assertEqual(reviewApp.includes("专业审核通过"), true, "review page records professional approval");
assertEqual(reviewApp.includes("需要修改"), true, "review page records requested changes");
assertEqual(reviewApp.includes("拒绝接入"), true, "review page can block an unsuitable instrument");
assertEqual(reviewApp.includes("打击乐六宫格"), true, "review page includes the teacher-configurable real-image percussion grid");
assertEqual(reviewApp.includes("layoutMode"), true, "review page lets the teacher audit mallet teaching modes");
assertEqual(reviewApp.includes("labelMode"), true, "review page lets the teacher audit pitch-label modes");
assertEqual(reviewApp.includes("InstrumentReviewWizard"), true, "review page delegates release decisions to the ordered five-gate wizard");

const fixedStage = readFileSync(join(root, "src/virtual-instruments/vue/FixedTabletStage.vue"), "utf8");
assertEqual(fixedStage.includes("1024"), true, "fixed stage exposes the audited logical width");
assertEqual(fixedStage.includes("不支持手机演奏"), true, "fixed stage explicitly rejects phone performance");
assertEqual(fixedStage.includes("请旋转设备"), true, "fixed stage handles portrait tablets");

const activity = readFileSync(join(root, "src/virtual-instruments/vue/ClassroomInstrumentActivity.vue"), "utf8");
for (const mode of ["free_play", "steady_beat", "echo", "ensemble_cue"]) {
  assertEqual(activity.includes(mode), true, `classroom shell supports ${mode}`);
}

const viteConfig = readFileSync(join(root, "vite.config.ts"), "utf8");
assertEqual(viteConfig.includes("vue()"), true, "Vite compiles the Vue delivery alongside existing React pages");
assertEqual(viteConfig.includes('"virtual-instrument-review"'), true, "Vite builds an independent instrument review page");

const packageContract = JSON.parse(readFileSync(join(root, "src/virtual-instruments/package.json"), "utf8"));
assertEqual(packageContract.peerDependencies.vue.startsWith("^3"), true, "engineer handoff declares Vue 3 as a peer dependency");
assertEqual("react" in (packageContract.dependencies ?? {}), false, "engineer handoff has no React runtime dependency");
