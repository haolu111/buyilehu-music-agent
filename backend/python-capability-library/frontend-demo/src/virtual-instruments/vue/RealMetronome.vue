<script setup lang="ts">
import { onBeforeUnmount, ref } from "vue";
import { AudioEngineRouter } from "../core/audioEngine";
import { LegacySoundfontEngine } from "../core/legacySoundfontEngine";
import { buildMetronomeTimeline, type MetronomeConfig } from "../core/metronome";
import { SpessaSynthEngine } from "../core/spessaSynthEngine";

const emit = defineEmits<{
  (event: "ready"): void;
  (event: "beat", accent: "strong" | "weak", phase: "count_in" | "performance"): void;
  (event: "error", error: Error): void;
}>();
const state = ref<"idle" | "loading" | "ready" | "error">("idle");
let engine: AudioEngineRouter | null = null;
let timers: number[] = [];

async function initialize() {
  if (state.value === "ready") return;
  state.value = "loading";
  try {
    engine ??= new AudioEngineRouter(new SpessaSynthEngine(), new LegacySoundfontEngine());
    await engine.initialize("virtual_metronome");
    state.value = "ready";
    emit("ready");
  } catch (error) {
    state.value = "error";
    const normalized = error instanceof Error ? error : new Error(String(error));
    emit("error", normalized);
    throw normalized;
  }
}
function stop() { timers.forEach(window.clearTimeout); timers = []; engine?.allNotesOff(); }
async function play(config: MetronomeConfig, performanceBars = 0) {
  await initialize(); stop();
  for (const event of buildMetronomeTimeline(config, performanceBars)) {
    timers.push(window.setTimeout(() => {
      engine?.noteOn(event.midi, event.accent === "strong" ? 112 : 88);
      window.setTimeout(() => engine?.noteOff(event.midi), 80);
      emit("beat", event.accent, event.phase);
    }, event.timeMs));
  }
}
onBeforeUnmount(() => { stop(); void engine?.destroy(); });
defineExpose({ initialize, play, stop, state });
</script>
<template><span class="metronome-status" :data-state="state">节拍器：{{ state === 'ready' ? '真实采样就绪' : state === 'loading' ? '载入中' : state === 'error' ? '载入失败' : '待启用' }}</span></template>
<style scoped>.metronome-status{padding:5px 8px;border-radius:999px;color:#ada492;background:#fff1;font-size:9px}.metronome-status[data-state=ready]{color:#b9dda9}.metronome-status[data-state=error]{color:#ff9f8c}</style>
