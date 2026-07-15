<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { AudioEngineRouter } from "../core/audioEngine";
import { LegacySoundfontEngine } from "../core/legacySoundfontEngine";
import type { InstrumentTouchRegion } from "../core/instrumentTouchMap";
import { PerformanceRecorder, type PerformanceRecording } from "../core/performanceRecorder";
import { PerformanceRecordingStore } from "../core/performanceRecordingStore";
import { PerformanceReplayer } from "../core/performanceReplayer";
import { buildPlayableZones, type PlayableZone } from "../core/playableZones";
import { SpessaSynthEngine } from "../core/spessaSynthEngine";
import { getVirtualInstrumentDefinition } from "../core/virtualInstrumentCatalog";
import MalletSurface from "./MalletSurface.vue";
import PianoSurface from "./PianoSurface.vue";
import InstrumentSkinCanvas from "./InstrumentSkinCanvas.vue";
import type { VirtualInstrumentPlayerProps } from "./types";

const props = withDefaults(defineProps<VirtualInstrumentPlayerProps>(), {
  disabled: false,
  defaultVelocity: 96,
  autoInitialize: false,
  showControls: true,
  reviewMode: false,
  layoutMode: "diatonic",
  labelMode: "number",
  tonicMidi: 60,
  accidentalPreference: "sharp",
  rollEnabled: false,
  rollIntervalMs: 120,
});
const emit = defineEmits<{
  ready: [engineId: "spessasynth" | "legacy_soundfont"];
  noteon: [zone: PlayableZone, velocity: number];
  noteoff: [zone: PlayableZone];
  recordingstopped: [recording: PerformanceRecording];
  error: [error: Error];
}>();

const instrument = computed(() => getVirtualInstrumentDefinition(props.instrumentId));
const padZones = computed(() => instrument.value.family === "percussion" ? buildPlayableZones(props.instrumentId) : []);
const defaultRegister = computed(() => instrument.value.pitchRange?.minMidi ?? 60);
const effectiveRegister = computed(() => props.registerStartMidi ?? defaultRegister.value);
const pianoOctaveCount = ref<1 | 2>(matchMedia?.("(orientation: portrait)")?.matches ? 1 : 2);
const activeZoneIds = ref(new Set<string>());
const state = ref<"idle" | "loading" | "ready" | "error">("idle");
const engineId = ref<"spessasynth" | "legacy_soundfont" | null>(null);
const fallbackReason = ref<string | null>(null);
const errorMessage = ref("");
const loadingStage = ref("");
const isRecording = ref(false);
const sustainActive = ref(false);
const latestRecording = ref<PerformanceRecording | null>(null);
const store = new PerformanceRecordingStore();
const activePointers = new Map<number, PlayableZone>();
const rollTimers = new Map<number, number>();
let engine: AudioEngineRouter | null = null;
let recorder = new PerformanceRecorder({ instrumentId: props.instrumentId });

const replayer = new PerformanceReplayer({
  noteOn: (midi, velocity) => engine?.noteOn(midi, velocity),
  noteOff: (midi) => engine?.noteOff(midi),
  setSustain: (active) => engine?.setSustain(active),
  allNotesOff: () => engine?.allNotesOff(),
});

async function initialize(): Promise<void> {
  if (state.value === "loading") return;
  state.value = "loading"; errorMessage.value = ""; loadingStage.value = "正在准备音频引擎";
  try {
    const updateStage = (stage: string) => { loadingStage.value = stage; };
    engine ??= new AudioEngineRouter(new SpessaSynthEngine({ onStage: updateStage }), new LegacySoundfontEngine({ onStage: updateStage }));
    await engine.initialize(props.instrumentId);
    engineId.value = engine.activeEngineId; fallbackReason.value = engine.fallbackReason; state.value = "ready";
    emit("ready", engine.activeEngineId!);
  } catch (error) {
    const normalized = error instanceof Error ? error : new Error(String(error));
    state.value = "error"; errorMessage.value = normalized.message; emit("error", normalized);
  }
}

function velocityFromPointer(event: PointerEvent): number {
  return event.pressure > 0 ? Math.round(Math.min(1, event.pressure) * 127) : props.defaultVelocity;
}

function startRoll(pointerId: number, zone: PlayableZone, velocity: number): void {
  if (zone.action !== "roll") return;
  rollTimers.set(pointerId, window.setInterval(() => {
    engine?.noteOn(zone.midi, velocity); recorder.noteOn(zone.midi, velocity, zone.id);
    window.setTimeout(() => { engine?.noteOff(zone.midi); recorder.noteOff(zone.midi, zone.id); }, 62);
  }, Math.max(80, props.rollIntervalMs)));
}

function stopRoll(pointerId: number): void {
  const timer = rollTimers.get(pointerId);
  if (timer !== undefined) window.clearInterval(timer);
  rollTimers.delete(pointerId);
}

function noteOn(event: PointerEvent, zone: PlayableZone): void {
  if (props.disabled || state.value !== "ready" || activePointers.has(event.pointerId)) return;
  (event.currentTarget as HTMLElement | null)?.setPointerCapture?.(event.pointerId);
  const velocity = velocityFromPointer(event);
  activePointers.set(event.pointerId, zone); activeZoneIds.value = new Set(activeZoneIds.value).add(zone.id);
  if (zone.action === "dampen") engine?.allNotesOff();
  engine?.noteOn(zone.midi, velocity); recorder.noteOn(zone.midi, velocity, zone.id); emit("noteon", zone, velocity);
  startRoll(event.pointerId, zone, velocity);
}

function noteMove(event: PointerEvent, zone: PlayableZone): void {
  const previous = activePointers.get(event.pointerId);
  if (!previous || previous.id === zone.id || state.value !== "ready") return;
  stopRoll(event.pointerId); engine?.noteOff(previous.midi); recorder.noteOff(previous.midi, previous.id); emit("noteoff", previous);
  const velocity = velocityFromPointer(event);
  activePointers.set(event.pointerId, zone);
  const next = new Set(activeZoneIds.value); next.delete(previous.id); next.add(zone.id); activeZoneIds.value = next;
  engine?.noteOn(zone.midi, velocity); recorder.noteOn(zone.midi, velocity, zone.id); emit("noteon", zone, velocity);
  startRoll(event.pointerId, zone, velocity);
}

function noteOff(event: PointerEvent): void {
  const zone = activePointers.get(event.pointerId);
  if (!zone) return;
  stopRoll(event.pointerId); activePointers.delete(event.pointerId);
  engine?.noteOff(zone.midi); recorder.noteOff(zone.midi, zone.id); emit("noteoff", zone);
  const next = new Set(activeZoneIds.value); next.delete(zone.id); activeZoneIds.value = next;
}

function setSustain(active: boolean): void {
  if (state.value !== "ready" || sustainActive.value === active) return;
  sustainActive.value = active; engine?.setSustain(active); recorder.setSustain(active);
}

function stopAll(): void {
  for (const timer of rollTimers.values()) window.clearInterval(timer);
  rollTimers.clear(); activePointers.clear(); activeZoneIds.value = new Set(); replayer.stop();
  if (sustainActive.value) engine?.setSustain(false);
  sustainActive.value = false; engine?.allNotesOff();
}

function startRecording(): void {
  if (state.value !== "ready" || isRecording.value) return;
  recorder = new PerformanceRecorder({ instrumentId: props.instrumentId }); recorder.start(); isRecording.value = true;
}

async function stopRecording(): Promise<PerformanceRecording | null> {
  if (!isRecording.value) return latestRecording.value;
  isRecording.value = false; latestRecording.value = recorder.stop(); await store.save(latestRecording.value);
  emit("recordingstopped", latestRecording.value); return latestRecording.value;
}

function replay(recording = latestRecording.value): void { if (recording && state.value === "ready") replayer.play(recording); }
function exportMidi(recording = latestRecording.value): Uint8Array | null {
  if (!recording) return null;
  const bytes = recorder.toMidi(recording); const url = URL.createObjectURL(new Blob([bytes], { type: "audio/midi" }));
  const link = document.createElement("a"); link.href = url; link.download = `${recording.instrumentId}-${recording.id}.mid`; link.click(); URL.revokeObjectURL(url); return bytes;
}
function triggerZone(zoneId: string, durationMs = 120, velocity = props.defaultVelocity): void {
  if (state.value !== "ready") return;
  const zone = [...padZones.value, ...buildPlayableZones(props.instrumentId)].find((candidate) => candidate.id === zoneId)
    ?? (/^midi-\d+$/.test(zoneId) ? { id: zoneId, label: zoneId, midi: Number(zoneId.slice(5)), action: "note" as const, hitArea: { x: 0, y: 0, width: 0, height: 0 } } : null);
  if (!zone) return;
  engine?.noteOn(zone.midi, velocity);
  window.setTimeout(() => engine?.noteOff(zone.midi), Math.max(40, durationMs));
}
function playableZoneForRegion(region: InstrumentTouchRegion): PlayableZone {
  const zone = padZones.value.find((candidate) => candidate.id === region.zoneId);
  if (!zone) throw new Error(`Missing playable zone ${region.zoneId} for ${props.instrumentId}`);
  return zone;
}
function regionDown(event: PointerEvent, region: InstrumentTouchRegion) { noteOn(event, playableZoneForRegion(region)); }
function regionHold(event: PointerEvent, region: InstrumentTouchRegion) { noteOff(event); noteOn(event, playableZoneForRegion(region)); }
function updateOrientation() { pianoOctaveCount.value = matchMedia("(orientation: portrait)").matches ? 1 : 2; }

watch(() => props.instrumentId, async () => { stopAll(); if (isRecording.value) await stopRecording(); state.value = "idle"; recorder = new PerformanceRecorder({ instrumentId: props.instrumentId }); if (props.autoInitialize) await initialize(); });
onMounted(() => { window.addEventListener("blur", stopAll); window.addEventListener("resize", updateOrientation); if (props.autoInitialize) void initialize(); });
onBeforeUnmount(() => { stopAll(); window.removeEventListener("blur", stopAll); window.removeEventListener("resize", updateOrientation); store.close(); void engine?.destroy(); });
defineExpose({ initialize, startRecording, stopRecording, replay, stopAll, exportMidi, triggerZone, getActiveEngine: () => engineId.value });
</script>

<template>
  <section class="instrument" :class="[`instrument--${instrument.layout}`, { 'is-disabled': disabled }]">
    <header>
      <div><p>CLASSROOM INSTRUMENT / {{ instrument.family }}</p><h2>{{ instrument.name }}</h2></div>
      <span class="engine" :data-state="state">{{ state === 'ready' ? (engineId === 'spessasynth' ? 'SpessaSynth 主引擎' : '真实采样后备') : state === 'loading' ? loadingStage : state === 'error' ? '音色加载失败' : '等待启用' }}</span>
    </header>

    <div v-if="state !== 'ready'" class="sound-gate">
      <button type="button" :disabled="state === 'loading'" @click="initialize">{{ state === 'loading' ? '正在加载…' : '启用真实音色' }}<small>无振荡器替代</small></button>
      <p v-if="errorMessage">{{ errorMessage }}</p>
    </div>

    <div class="play-surface" :data-layout="instrument.layout">
      <PianoSurface
        v-if="instrument.family === 'keyboard'"
        :start-midi="effectiveRegister"
        :octave-count="pianoOctaveCount"
        :label-mode="labelMode"
        :tonic-midi="tonicMidi"
        :accidental-preference="accidentalPreference"
        :active-zone-ids="activeZoneIds"
        :sustain-active="sustainActive"
        @pointerdown="noteOn"
        @pointermove="noteMove"
        @pointerup="noteOff"
        @sustainchange="setSustain"
      />
      <MalletSurface
        v-else-if="instrument.family === 'mallet'"
        :instrument-id="instrument.id"
        :mode="layoutMode"
        :register-start-midi="effectiveRegister"
        :label-mode="labelMode"
        :tonic-midi="tonicMidi"
        :accidental-preference="accidentalPreference"
        :roll-enabled="rollEnabled"
        :active-zone-ids="activeZoneIds"
        @pointerdown="noteOn"
        @pointerup="noteOff"
      />
      <template v-else>
        <InstrumentSkinCanvas :instrument-id="instrument.id" :review-mode="reviewMode" :disabled="disabled || state !== 'ready'" @regiondown="regionDown" @regionhold="regionHold" @regionup="noteOff" @error="emit('error', $event)" />
        <span v-for="zone in padZones" :key="zone.id" class="zone-status" :data-zone-id="zone.id" :class="{ active: activeZoneIds.has(zone.id) }">{{ zone.label }}</span>
      </template>
    </div>

    <footer v-if="showControls">
      <div><button class="record" :class="{ active: isRecording }" @click="isRecording ? stopRecording() : startRecording()">● {{ isRecording ? '停止录制' : '录制演奏' }}</button><button :disabled="!latestRecording" @click="replay()">回放</button><button :disabled="!latestRecording" @click="exportMidi()">导出 MIDI</button></div>
      <p>最多10点触控 · 压感优先 / 默认力度{{ defaultVelocity }} · 最长5分钟</p>
    </footer>
    <aside v-if="reviewMode">音色：离线真实采样　引擎：{{ engineId ?? '未启用' }}　后备原因：{{ fallbackReason ?? '无' }}</aside>
  </section>
</template>

<style scoped>
.instrument{position:relative;overflow:hidden;padding:clamp(18px,2.4vw,30px);color:#f2ead9;background:radial-gradient(circle at 10% 0,#d3844b33,transparent 30%),linear-gradient(145deg,#1c2422,#0b1011 70%);border:1px solid #fff2;border-radius:28px;box-shadow:0 28px 70px #1c19144d;font-family:"Avenir Next","PingFang SC",sans-serif;user-select:none;touch-action:none}header{display:flex;justify-content:space-between;gap:20px;align-items:flex-start;margin-bottom:18px}header p{margin:0 0 5px;color:#d88b54;font:700 10px/1.2 Futura,sans-serif;letter-spacing:.18em}h2{margin:0;font:500 clamp(30px,4vw,50px)/1 "Songti SC",serif}.engine{padding:8px 12px;border:1px solid #fff2;border-radius:999px;color:#a9a193;background:#0003;font-size:11px}.engine[data-state=ready]{color:#b9dda9}.sound-gate{position:absolute;z-index:20;left:50%;top:50%;transform:translate(-50%,-50%);width:min(340px,75%);text-align:center}.sound-gate button{width:100%;padding:14px;border:0;border-radius:16px;color:#21160e;background:linear-gradient(135deg,#f0d5a8,#ce8150);box-shadow:0 18px 40px #0008;font-weight:800}.sound-gate small{display:block;margin-top:4px;opacity:.6}.sound-gate p{color:#f2a08d;font-size:11px}.play-surface{position:relative;min-height:clamp(330px,42vw,520px);overflow:hidden;border-radius:20px;background:radial-gradient(circle,#29332f,#101615 70%);box-shadow:inset 0 0 0 1px #fff1,inset 0 20px 35px #0005}.sound-gate+.play-surface{filter:grayscale(.4) blur(1px);opacity:.42}.zone-status{position:relative;z-index:7;display:inline-block;margin:12px 0 0 12px;padding:5px 8px;border-radius:999px;color:#bdb4a3;background:#10151399;font-size:10px;pointer-events:none}.zone-status.active{color:#25170e;background:#efbd7a;box-shadow:0 0 20px #efbd7a88}footer{display:flex;justify-content:space-between;align-items:center;gap:15px;margin-top:16px}footer div{display:flex;gap:7px}footer button{padding:9px 13px;border:1px solid #fff2;border-radius:10px;color:#f2ead9;background:#fff1}footer button:disabled{opacity:.3}.record.active{color:#ffc1b5;border-color:#dc6b58}footer p,aside{color:#a9a193;font-size:10px}aside{margin-top:12px;padding-top:10px;border-top:1px solid #fff1}.is-disabled{opacity:.55;pointer-events:none}@media(max-width:700px){header,footer{flex-direction:column}.engine{align-self:flex-start}.play-surface{min-height:520px}footer p{margin:0}}
</style>
