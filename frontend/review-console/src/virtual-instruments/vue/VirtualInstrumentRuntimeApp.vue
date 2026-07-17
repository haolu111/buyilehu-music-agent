<script setup lang="ts">
import { computed, onBeforeUnmount, ref } from "vue";
import type { PlayableZone } from "../core/playableZones";
import VirtualInstrumentPlayer from "./VirtualInstrumentPlayer.vue";

type RuntimeConfig = {
  instrumentId?: string;
  prompt?: string;
  task?: {
    id?: string;
    kind?: string;
    bpm?: number;
    instrumentId?: string;
    targetEvents?: Array<{ offsetBeats?: number; zoneId?: string; midi?: number }>;
  };
};

function readConfig(): RuntimeConfig {
  const encoded = new URLSearchParams(location.search).get("config");
  if (!encoded) return {};
  try {
    const binary = atob(encoded.replace(/-/g, "+").replace(/_/g, "/"));
    const bytes = Uint8Array.from(binary, (character) => character.charCodeAt(0));
    return JSON.parse(new TextDecoder().decode(bytes)) as RuntimeConfig;
  } catch {
    return {};
  }
}

const config = readConfig();
const instrumentId = computed(() => config.instrumentId || config.task?.instrumentId || "virtual_frame_drum");
const events = ref<Array<{ timeMs: number; zoneId: string; midi: number; velocity: number }>>([]);
const startedAt = ref(0);
const player = ref<InstanceType<typeof VirtualInstrumentPlayer> | null>(null);
const isPlayingDemo = ref(false);
const isPreparingAudio = ref(false);
const currentDemoBeat = ref<number | null>(null);
const demoTimers: number[] = [];

type PlaybackMode = "sequence" | "metronome" | "none";

const playbackMode = computed<PlaybackMode>(() => {
  switch (config.task?.kind) {
    case "rhythm_echo":
    case "melody_sequence":
      return "sequence";
    case "steady_beat":
      return "metronome";
    default:
      return "none";
  }
});
const demoHeading = computed(() =>
  playbackMode.value === "metronome" ? "跟随节拍练习" : "先听，再演奏",
);
const demoIdleText = computed(() =>
  playbackMode.value === "metronome" ? "启动任务节拍" : "听一遍任务示范",
);
const demoButtonText = computed(() => {
  if (isPlayingDemo.value) return "重新播放";
  return playbackMode.value === "metronome" ? "▶ 启动节拍" : "▶ 播放示范";
});

const demoEvents = computed(() => {
  if (config.task?.targetEvents?.length) return config.task.targetEvents;
  if (instrumentId.value === "virtual_frame_drum") {
    return [
      { offsetBeats: 0, zoneId: "center" },
      { offsetBeats: 1, zoneId: "edge" },
      { offsetBeats: 2, zoneId: "center" },
      { offsetBeats: 3, zoneId: "edge" },
    ];
  }
  return [60, 64, 67, 72].map((midi, index) => ({ offsetBeats: index, midi }));
});

function stopDemo() {
  demoTimers.splice(0).forEach((timer) => window.clearTimeout(timer));
  player.value?.stopAll();
  isPlayingDemo.value = false;
  isPreparingAudio.value = false;
  currentDemoBeat.value = null;
}

async function playDemo() {
  if (playbackMode.value === "none") return;
  stopDemo();
  isPreparingAudio.value = true;
  try {
    await player.value?.initialize();
    isPreparingAudio.value = false;
    isPlayingDemo.value = true;
    const beatMs = 60000 / Math.max(40, Math.min(180, config.task?.bpm || 88));
    demoEvents.value.forEach((event, index) => {
      const offset = Math.max(0, event.offsetBeats ?? index);
      demoTimers.push(window.setTimeout(() => {
        currentDemoBeat.value = index + 1;
        const zoneId = event.zoneId || (typeof event.midi === "number" ? `midi-${event.midi}` : "center");
        player.value?.triggerZone(zoneId, Math.min(420, beatMs * 0.7), index === 0 ? 112 : 92);
      }, offset * beatMs));
    });
    const last = demoEvents.value.reduce(
      (maximum, event, index) => Math.max(maximum, event.offsetBeats ?? index),
      0,
    );
    demoTimers.push(window.setTimeout(stopDemo, (last + 1) * beatMs));
  } catch {
    stopDemo();
  }
}

function onNoteOn(zone: PlayableZone, velocity: number) {
  if (!startedAt.value) startedAt.value = performance.now();
  events.value.push({
    timeMs: Math.round(performance.now() - startedAt.value),
    zoneId: zone.id,
    midi: zone.midi,
    velocity,
  });
}

function clear() {
  events.value = [];
  startedAt.value = 0;
}

function submit() {
  const performedEvents = events.value.map((event) => ({
    timeMs: event.timeMs,
    zoneId: event.zoneId,
    midi: event.midi,
    velocity: event.velocity,
  }));
  window.parent.postMessage({
    type: "buyilehu:activity-completed",
    result: {
      events: performedEvents,
      notes: performedEvents.map((event) => event.midi),
      zones: performedEvents.map((event) => event.zoneId),
      taskId: config.task?.id,
      taskKind: config.task?.kind,
      instrumentId: instrumentId.value,
    },
  }, location.origin);
}

onBeforeUnmount(stopDemo);
</script>

<template>
  <main>
    <section class="task">
      <div>
        <span>虚拟乐器任务</span>
        <h1>{{ config.task?.kind || "乐器演奏" }}</h1>
        <p>{{ config.prompt || "直接点击乐器的演奏区域完成任务。" }}</p>
      </div>
      <strong v-if="config.task?.bpm">{{ config.task.bpm }} BPM</strong>
    </section>

    <section v-if="playbackMode !== 'none'" class="demo-toolbar" aria-label="任务音频播放控制">
      <div>
        <span class="listen-first">{{ demoHeading }}</span>
        <strong>
          {{ isPreparingAudio ? "正在准备真实音色…" : isPlayingDemo ? `正在播放第 ${currentDemoBeat || 1} 拍` : demoIdleText }}
        </strong>
      </div>
      <div class="demo-actions">
        <button type="button" class="listen" :disabled="isPreparingAudio" @click="playDemo">
          {{ demoButtonText }}
        </button>
        <button type="button" class="stop" :disabled="!isPlayingDemo && !isPreparingAudio" @click="stopDemo">■ 停止</button>
      </div>
    </section>

    <VirtualInstrumentPlayer
      ref="player"
      :instrument-id="instrumentId"
      :auto-initialize="false"
      :show-controls="false"
      @noteon="onNoteOn"
    />

    <footer>
      <p>已演奏 {{ events.length }} 次</p>
      <div>
        <button type="button" class="secondary" :disabled="!events.length" @click="clear">清空</button>
        <button type="button" class="primary" :disabled="!events.length" @click="submit">提交演奏</button>
      </div>
    </footer>
  </main>
</template>

<style>
*{box-sizing:border-box}html,body,#virtual-instrument-player-app{min-height:100%;margin:0}body{background:#f2f6f3;color:#18302c;font-family:"PingFang SC","Microsoft YaHei",sans-serif}main{width:100%;padding:18px}.task{display:flex;align-items:center;justify-content:space-between;gap:20px;margin:0 auto 14px;padding:4px 8px}.task span{color:#a76135;font-size:12px;font-weight:800;letter-spacing:.12em}.task h1{margin:4px 0;font-size:clamp(20px,3vw,30px)}.task p{margin:0;color:#5b706b}.task strong{white-space:nowrap;color:#b0683d}.demo-toolbar{display:flex;align-items:center;justify-content:space-between;gap:16px;margin:0 0 14px;padding:14px 16px;border:1px solid #cbd9d4;border-radius:16px;background:#fff;box-shadow:0 8px 24px #193d3420}.demo-toolbar>div:first-child{display:grid;gap:3px}.listen-first{color:#b56131;font-size:11px;font-weight:900;letter-spacing:.12em}.demo-toolbar strong{font-size:16px}.demo-actions{display:flex;gap:9px}.demo-actions button{min-width:112px;padding:11px 15px;border-radius:12px;font-weight:900;cursor:pointer}.listen{border:0;color:#fff;background:#147d6c;box-shadow:0 3px 0 #0a5b4e}.stop{border:1px solid #bccbc6;color:#405b55;background:#f5f8f6}.demo-actions button:disabled{cursor:not-allowed;opacity:.4}footer{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:15px 8px 0}footer p{margin:0;color:#5b706b}footer div{display:flex;gap:10px}footer button{min-width:100px;padding:11px 18px;border-radius:12px;font-weight:800;cursor:pointer}.secondary{border:1px solid #b9c8c3;background:#fff;color:#38534d}.primary{border:0;background:#15977f;color:#fff;box-shadow:0 4px 0 #0c6c5b}.primary:disabled,.secondary:disabled{cursor:not-allowed;opacity:.4}@media(max-width:700px){main{padding:10px}.task{align-items:flex-start}.task strong{font-size:12px}.demo-toolbar{align-items:stretch;flex-direction:column}.demo-actions button{flex:1}footer{position:sticky;bottom:0;padding:12px;background:#f2f6f3ee}}
</style>
