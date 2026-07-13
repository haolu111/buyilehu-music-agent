<script setup lang="ts">
import { computed, onBeforeUnmount, ref } from "vue";
import { LegacySoundfontEngine } from "../core/legacySoundfontEngine";
import { validatePercussionGrid, type PercussionGridTile } from "../core/percussionGrid";
import type { InstrumentTouchRegion } from "../core/instrumentTouchMap";
import { getVirtualInstrumentDefinition } from "../core/virtualInstrumentCatalog";
import InstrumentSkinCanvas from "./InstrumentSkinCanvas.vue";

const props = withDefaults(defineProps<{
  tiles: PercussionGridTile[];
  defaultVelocity?: number;
  showLabels?: boolean;
  reviewMode?: boolean;
}>(), { defaultVelocity: 96, showLabels: true, reviewMode: false });
const emit = defineEmits<{ noteon: [tile: PercussionGridTile, elapsedTimestamp: number]; noteoff: [tile: PercussionGridTile] }>();

const validatedTiles = computed(() => validatePercussionGrid(props.tiles));
const state = ref<"idle" | "loading" | "ready" | "error">("idle");
const errorMessage = ref("");
const activeTiles = ref(new Set<string>());
const engines = new Map<string, LegacySoundfontEngine>();
const activePointers = new Map<number, PercussionGridTile>();
const rollTimers = new Map<number, number>();

async function initialize(): Promise<void> {
  state.value = "loading";
  errorMessage.value = "";
  try {
    const instrumentIds = [...new Set(validatedTiles.value.map((tile) => tile.instrumentId))];
    const initialization = instrumentIds.map((instrumentId) => {
      const engine = new LegacySoundfontEngine();
      engines.set(instrumentId, engine);
      return engine.initialize(instrumentId);
    });
    await Promise.all(initialization);
    state.value = "ready";
  } catch (error) {
    state.value = "error";
    errorMessage.value = error instanceof Error ? error.message : String(error);
    await destroy();
  }
}

function play(event: PointerEvent, tile: PercussionGridTile, region: InstrumentTouchRegion): void {
  if (state.value !== "ready") return;
  const instrument = getVirtualInstrumentDefinition(tile.instrumentId);
  const zone = instrument.zones.find((candidate) => candidate.id === region.zoneId)!;
  const velocity = event.pressure > 0 ? Math.round(event.pressure * 127) : props.defaultVelocity;
  activePointers.set(event.pointerId, tile);
  activeTiles.value = new Set(activeTiles.value).add(tile.id);
  (event.currentTarget as HTMLElement | null)?.setPointerCapture?.(event.pointerId);
  if (zone.action === "dampen") engines.get(tile.instrumentId)?.allNotesOff();
  engines.get(tile.instrumentId)?.noteOn(zone.midi, velocity);
  emit("noteon", tile, performance.now());
  if (zone.action === "roll") {
    rollTimers.set(event.pointerId, window.setInterval(() => {
      engines.get(tile.instrumentId)?.noteOn(zone.midi, velocity);
      window.setTimeout(() => engines.get(tile.instrumentId)?.noteOff(zone.midi), 62);
    }, 120));
  }
}

function stop(event: PointerEvent): void {
  const tile = activePointers.get(event.pointerId);
  if (!tile) return;
  const instrument = getVirtualInstrumentDefinition(tile.instrumentId);
  const zone = instrument.zones.find((candidate) => candidate.id === tile.zoneId)!;
  const rollTimer = rollTimers.get(event.pointerId);
  if (rollTimer !== undefined) window.clearInterval(rollTimer);
  rollTimers.delete(event.pointerId);
  engines.get(tile.instrumentId)?.noteOff(zone.midi);
  emit("noteoff", tile);
  activePointers.delete(event.pointerId);
  const next = new Set(activeTiles.value); next.delete(tile.id); activeTiles.value = next;
}

async function destroy(): Promise<void> {
  for (const timer of rollTimers.values()) window.clearInterval(timer);
  rollTimers.clear();
  activePointers.clear(); activeTiles.value = new Set();
  await Promise.all([...engines.values()].map((engine) => engine.destroy()));
  engines.clear();
}
function triggerTile(tileId: string, durationMs = 120, velocity = props.defaultVelocity): void {
  if (state.value !== "ready") return;
  const tile = validatedTiles.value.find((candidate) => candidate.id === tileId) ?? validatedTiles.value.find((candidate) => candidate.zoneId === tileId);
  if (!tile) return;
  const zone = getVirtualInstrumentDefinition(tile.instrumentId).zones.find((candidate) => candidate.id === tile.zoneId);
  if (!zone) return;
  engines.get(tile.instrumentId)?.noteOn(zone.midi, velocity);
  window.setTimeout(() => engines.get(tile.instrumentId)?.noteOff(zone.midi), Math.max(40, durationMs));
}

onBeforeUnmount(() => { void destroy(); });
defineExpose({ initialize, destroy, triggerTile });
</script>

<template>
  <section class="percussion-grid-shell">
    <button v-if="state !== 'ready'" class="grid-gate" type="button" :disabled="state === 'loading'" @click="initialize">
      {{ state === 'loading' ? '正在载入六件真实采样…' : '启用真实打击乐' }}
      <small v-if="errorMessage">{{ errorMessage }}</small>
    </button>
    <div class="percussion-grid" :class="`count--${validatedTiles.length}`">
      <div
        v-for="tile in validatedTiles"
        :key="tile.id"
        role="button"
        tabindex="0"
        class="percussion-tile"
        :class="[{ active: activeTiles.has(tile.id) }, `tone--${tile.colorToken}`]"
        :data-zone-id="tile.id"
      >
        <InstrumentSkinCanvas :instrument-id="tile.instrumentId" :allowed-zone-ids="[tile.zoneId]" :review-mode="reviewMode" :disabled="state !== 'ready'" @regiondown="(event, region) => play(event, tile, region)" @regionhold="(event, region) => play(event, tile, region)" @regionup="stop" />
        <span v-if="showLabels">{{ getVirtualInstrumentDefinition(tile.instrumentId).name }}</span>
        <small v-if="showLabels">{{ getVirtualInstrumentDefinition(tile.instrumentId).zones.find(zone => zone.id === tile.zoneId)?.label }}</small>
        <em v-if="reviewMode">仅图片主体热区发声</em>
      </div>
    </div>
  </section>
</template>

<style scoped>
.percussion-grid-shell{position:relative;min-height:520px;padding:18px;border-radius:28px;background:radial-gradient(circle at 50% 0,#39413d,#121716 72%);box-shadow:inset 0 0 0 1px #fff1,0 28px 60px #0005}.percussion-grid{height:484px;display:grid;grid-template-columns:repeat(3,1fr);grid-auto-rows:1fr;gap:12px}.percussion-grid.count--2{grid-template-columns:repeat(2,1fr)}.percussion-grid.count--3{grid-template-columns:repeat(3,1fr)}.percussion-grid.count--4{grid-template-columns:repeat(2,1fr)}.percussion-tile{position:relative;overflow:hidden;border:1px solid #fff2;border-radius:22px;color:#f8ead6;background:linear-gradient(145deg,#72452f,#3e261c);box-shadow:inset 0 0 45px #0004,0 10px 20px #0005;touch-action:none}.percussion-tile img{position:absolute;inset:5%;width:90%;height:78%;object-fit:contain;filter:drop-shadow(0 13px 16px #0008);pointer-events:none}.percussion-tile span,.percussion-tile small{position:absolute;z-index:2;left:14px;bottom:12px}.percussion-tile span{font:700 14px/1 "Avenir Next","PingFang SC",sans-serif}.percussion-tile small{left:auto;right:14px;color:#f5dfbd99}.percussion-tile.active{filter:brightness(1.3);transform:translateY(3px);box-shadow:inset 0 0 55px #ffd59b88}.tone--slate{background:linear-gradient(145deg,#49677b,#263943)}.tone--oak{background:linear-gradient(145deg,#8b6936,#4b361d)}.tone--sage{background:linear-gradient(145deg,#5d815b,#30472f)}.tone--violet{background:linear-gradient(145deg,#6e5b8b,#382d4b)}.tone--brass{background:linear-gradient(145deg,#9b7935,#4b3818)}.grid-gate{position:absolute;z-index:10;left:50%;top:50%;transform:translate(-50%,-50%);padding:16px 24px;border:0;border-radius:16px;color:#24170f;background:#e2bd83;box-shadow:0 18px 35px #0009;font-weight:800}.grid-gate small{display:block;margin-top:5px;color:#8d4339}@media(max-width:700px) and (orientation:portrait){.percussion-grid-shell{min-height:650px}.percussion-grid{height:614px;grid-template-columns:repeat(2,1fr)!important}}
</style>
