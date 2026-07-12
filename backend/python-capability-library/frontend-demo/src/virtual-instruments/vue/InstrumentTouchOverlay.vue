<script setup lang="ts">
import { computed } from "vue";
import { getInstrumentSkinCalibration } from "../core/instrumentSkinCalibration";
import type { InstrumentTouchRegion, TouchShape } from "../core/instrumentTouchMap";
import { getVirtualInstrumentDefinition } from "../core/virtualInstrumentCatalog";

const props = defineProps<{
  instrumentId: string;
  latestTap?: { x: number; y: number; hitRegionId: string | null } | null;
  allowedZoneIds?: string[];
}>();
const regions = computed(() => {
  const allowed = props.allowedZoneIds ? new Set(props.allowedZoneIds) : null;
  return getInstrumentSkinCalibration(props.instrumentId).regions.filter((region) => !allowed || allowed.has(region.zoneId));
});

function shapeStyle(shape: TouchShape): Record<string, string> {
  if (shape.type === "rect") return { left:`${shape.x*100}%`,top:`${shape.y*100}%`,width:`${shape.width*100}%`,height:`${shape.height*100}%`,borderRadius:"8px" };
  const cx = shape.cx, cy = shape.cy;
  const rx = shape.type === "ellipse" ? shape.rx : shape.type === "circle" ? shape.radius : shape.type === "ring" ? shape.outerRadius : 0;
  const ry = shape.type === "ellipse" ? shape.ry : rx;
  if (shape.type !== "polygon") return { left:`${(cx-rx)*100}%`,top:`${(cy-ry)*100}%`,width:`${rx*200}%`,height:`${ry*200}%`,borderRadius:"50%" };
  const xs=shape.points.map(point=>point[0]), ys=shape.points.map(point=>point[1]);
  const left=Math.min(...xs), top=Math.min(...ys), right=Math.max(...xs), bottom=Math.max(...ys);
  return { left:`${left*100}%`,top:`${top*100}%`,width:`${(right-left)*100}%`,height:`${(bottom-top)*100}%`,clipPath:`polygon(${shape.points.map(([x,y])=>`${(x-left)/(right-left)*100}% ${(y-top)/(bottom-top)*100}%`).join(",")})` };
}
function details(region: InstrumentTouchRegion): string {
  const zone = getVirtualInstrumentDefinition(region.instrumentId).zones.find((item) => item.id === region.zoneId);
  return `${region.gesture} · MIDI ${zone?.midi ?? "—"}`;
}
</script>

<template>
  <div class="touch-overlay" aria-hidden="true">
    <span v-for="region in regions" :key="region.id" class="touch-region" :data-region-id="region.id" :data-hit-surface="region.hitSurface" :style="shapeStyle(region.shape)">
      <b>{{ region.accessibleLabel }}<small>{{ details(region) }}</small></b>
    </span>
    <i v-if="latestTap" class="tap-point" :class="{ miss: !latestTap.hitRegionId }" :style="{left:`${latestTap.x*100}%`,top:`${latestTap.y*100}%`}" />
  </div>
</template>

<style scoped>
.touch-overlay{position:absolute;inset:0;z-index:6;pointer-events:none}.touch-region{position:absolute;border:2px dashed #ffe1a8;background:#e38b4930;box-shadow:0 0 0 1px #1118}.touch-region[data-hit-surface=visible_control]{border-style:solid;background:#8f493bbb}.touch-region b{position:absolute;left:50%;top:0;transform:translate(-50%,-115%);min-width:0;padding:3px 5px;border-radius:6px;color:#fff;background:#17201ee8;font-size:8px;line-height:1.1;text-align:center;white-space:nowrap}.touch-region[data-hit-surface=visible_control] b{display:none}.touch-region small{display:block;margin-top:2px;color:#efbf7f;font-size:7px}.tap-point{position:absolute;width:18px;height:18px;transform:translate(-50%,-50%);border:3px solid white;border-radius:50%;background:#4ba66c;box-shadow:0 0 0 5px #4ba66c44}.tap-point.miss{background:#d85545;box-shadow:0 0 0 5px #d8554544}
</style>
