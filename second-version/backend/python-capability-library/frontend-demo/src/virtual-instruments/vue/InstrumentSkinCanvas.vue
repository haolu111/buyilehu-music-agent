<script setup lang="ts">
import { computed, onBeforeUnmount, ref } from "vue";
import { clientPointToSkinPoint, getInstrumentSkinCalibration, hitTestInstrumentSkin } from "../core/instrumentSkinCalibration";
import { getInstrumentSkinUrl } from "../core/instrumentSkins";
import type { InstrumentTouchRegion } from "../core/instrumentTouchMap";
import InstrumentTouchOverlay from "./InstrumentTouchOverlay.vue";

const props = withDefaults(defineProps<{
  instrumentId: string;
  disabled?: boolean;
  reviewMode?: boolean;
  allowedZoneIds?: string[];
  holdDelayMs?: number;
}>(), { disabled: false, reviewMode: false, holdDelayMs: 360 });
const emit = defineEmits<{
  regiondown: [event: PointerEvent, region: InstrumentTouchRegion];
  regionhold: [event: PointerEvent, region: InstrumentTouchRegion];
  regionup: [event: PointerEvent, region: InstrumentTouchRegion];
  maskready: [];
  error: [error: Error];
}>();
const canvasElement = ref<HTMLElement | null>(null);
const maskCanvas = document.createElement("canvas");
maskCanvas.width = 1024; maskCanvas.height = 1024;
let alphaMask: Uint8ClampedArray | null = null;
const active = new Map<number, InstrumentTouchRegion>();
const holdTimers = new Map<number, number>();
const latestTap = ref<{ x: number; y: number; hitRegionId: string | null } | null>(null);
const skinUrl = computed(() => getInstrumentSkinUrl(props.instrumentId));
const calibration = computed(() => getInstrumentSkinCalibration(props.instrumentId));
const chokeRegion = computed(() => calibration.value.regions.find((region) => region.gesture === "choke" && (!props.allowedZoneIds || props.allowedZoneIds.includes(region.zoneId))) ?? null);

function buildAlphaMask(event: Event): void {
  try {
    const image = event.currentTarget as HTMLImageElement;
    const context = maskCanvas.getContext("2d", { willReadFrequently: true });
    if (!context) throw new Error("Instrument skin alpha canvas is unavailable");
    context.clearRect(0, 0, 1024, 1024); context.drawImage(image, 0, 0, 1024, 1024);
    alphaMask = context.getImageData(0, 0, 1024, 1024).data; emit("maskready");
  } catch (error) { emit("error", error instanceof Error ? error : new Error(String(error))); }
}
function alphaAt(x: number, y: number): number {
  if (!alphaMask) return 0;
  const px = Math.max(0, Math.min(1023, Math.floor(x * 1024))); const py = Math.max(0, Math.min(1023, Math.floor(y * 1024)));
  return alphaMask[(py * 1024 + px) * 4 + 3];
}
function point(event: PointerEvent) {
  const rect = canvasElement.value?.getBoundingClientRect();
  return rect ? clientPointToSkinPoint(event.clientX, event.clientY, rect) : null;
}
function begin(event: PointerEvent, forcedRegion?: InstrumentTouchRegion): void {
  if (props.disabled || active.has(event.pointerId)) return;
  const skinPoint = point(event); if (!skinPoint) return;
  const hold = hitTestInstrumentSkin(props.instrumentId, skinPoint.normalizedX, skinPoint.normalizedY, { alphaAt, gesture: "hold_roll", allowedZoneIds: props.allowedZoneIds });
  const region = forcedRegion ?? hitTestInstrumentSkin(props.instrumentId, skinPoint.normalizedX, skinPoint.normalizedY, { alphaAt, gesture: "tap", allowedZoneIds: props.allowedZoneIds });
  latestTap.value = { x: skinPoint.normalizedX, y: skinPoint.normalizedY, hitRegionId: region?.id ?? hold?.id ?? null };
  if (!region && !hold) return;
  (event.currentTarget as HTMLElement).setPointerCapture?.(event.pointerId);
  if (region) { active.set(event.pointerId, region); emit("regiondown", event, region); }
  if (hold) holdTimers.set(event.pointerId, window.setTimeout(() => { active.set(event.pointerId, hold); latestTap.value = { ...latestTap.value!, hitRegionId: hold.id }; emit("regionhold", event, hold); }, props.holdDelayMs));
}
function end(event: PointerEvent): void {
  const timer = holdTimers.get(event.pointerId); if (timer !== undefined) window.clearTimeout(timer); holdTimers.delete(event.pointerId);
  const region = active.get(event.pointerId); if (region) emit("regionup", event, region); active.delete(event.pointerId);
}
function chokeDown(event: PointerEvent): void { if (chokeRegion.value) begin(event, chokeRegion.value); }
function stopAll(): void { for (const timer of holdTimers.values()) window.clearTimeout(timer); holdTimers.clear(); active.clear(); }
onBeforeUnmount(stopAll);
defineExpose({ alphaAt, stopAll, isMaskReady: () => alphaMask !== null });
</script>

<template>
  <div class="skin-canvas-shell">
    <div ref="canvasElement" class="skin-canvas" :data-instrument="instrumentId" @pointerdown.prevent="begin" @pointerup.prevent="end" @pointercancel.prevent="end" @lostpointercapture="end">
      <img v-if="skinUrl" class="skin-image" :src="skinUrl" :alt="`${instrumentId}完整写实乐器图片`" draggable="false" @load="buildAlphaMask">
      <button v-if="chokeRegion" type="button" class="choke-control" :aria-label="chokeRegion.accessibleLabel" :disabled="disabled" @pointerdown.stop.prevent="chokeDown" @pointerup.stop.prevent="end" @pointercancel.stop.prevent="end">按住止音<small>MIDI 80</small></button>
      <InstrumentTouchOverlay v-if="reviewMode" :instrument-id="instrumentId" :allowed-zone-ids="allowedZoneIds" :latest-tap="latestTap" />
    </div>
  </div>
</template>

<style scoped>
.skin-canvas-shell{position:absolute;inset:3%;display:grid;place-items:center;overflow:visible}.skin-canvas{position:relative;width:auto;height:100%;max-width:100%;aspect-ratio:1/1;overflow:visible;touch-action:none}.skin-image{position:absolute;inset:0;display:block;width:100%;height:100%;object-fit:contain;pointer-events:none;filter:drop-shadow(0 18px 24px #0008)}.choke-control{position:absolute;z-index:8;left:78%;top:4%;width:18%;height:14%;display:grid;place-content:center;border:2px solid #f1c994;border-radius:14px;color:#fff3dd;background:#8f493be8;box-shadow:0 8px 20px #0007;font-weight:900;touch-action:none}.choke-control small{display:block;margin-top:3px;color:#f3c98d;font-size:8px}.choke-control:active{transform:translateY(2px);background:#67342c}.choke-control:disabled{opacity:.5}
</style>
