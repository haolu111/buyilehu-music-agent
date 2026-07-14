<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { calculateTabletStageLayout, classifyStageDevice } from "../core/fixedTabletStage";

const props = withDefaults(defineProps<{ reviewMode?: boolean; forceDeviceState?: "supported" | "tablet_portrait" | "phone_unsupported" }>(), { reviewMode: false });
const emit = defineEmits<{ blocked: [reason: "tablet_portrait" | "phone_unsupported"]; layoutchange: [scale: number] }>();
const host = ref<HTMLElement | null>(null);
const size = ref({ width: 1024, height: 768 });
const viewport = ref({ width: 1024, height: 768 });
let observer: ResizeObserver | null = null;

const layout = computed(() => calculateTabletStageLayout(size.value.width, size.value.height));
const deviceState = computed(() => props.forceDeviceState ?? classifyStageDevice(viewport.value.width, viewport.value.height));
const stageStyle = computed(() => ({ width: "1024px", height: "768px", transform: `translate(${layout.value.offsetX}px, ${layout.value.offsetY}px) scale(${layout.value.scale})` }));

function measure() {
  if (host.value) size.value = { width: host.value.clientWidth, height: host.value.clientHeight };
  viewport.value = { width: window.innerWidth, height: window.innerHeight };
  emit("layoutchange", layout.value.scale);
  if (deviceState.value !== "supported" && !props.reviewMode) emit("blocked", deviceState.value);
}
onMounted(() => { observer = new ResizeObserver(measure); if (host.value) observer.observe(host.value); window.addEventListener("resize", measure); measure(); });
onBeforeUnmount(() => { observer?.disconnect(); window.removeEventListener("resize", measure); });
</script>

<template>
  <section ref="host" class="tablet-host" :data-device-state="deviceState">
    <div v-if="deviceState === 'phone_unsupported' && !reviewMode" class="device-gate"><strong>不支持手机演奏</strong><span>请使用横屏平板或桌面审核页面。</span></div>
    <div v-else-if="deviceState === 'tablet_portrait' && !reviewMode" class="device-gate"><strong>请旋转设备</strong><span>虚拟乐器使用固定 1024 × 768 横屏舞台。</span></div>
    <div v-else class="tablet-stage" :style="stageStyle"><slot /></div>
  </section>
</template>

<style scoped>
.tablet-host{position:relative;width:100%;height:100%;min-height:480px;overflow:hidden;background:radial-gradient(circle at 50% 25%,#33403c,#111715 70%);border-radius:24px}.tablet-stage{position:absolute;left:0;top:0;transform-origin:top left;overflow:hidden;background:#17201e}.device-gate{position:absolute;inset:0;display:grid;place-content:center;gap:10px;padding:30px;color:#f4ead7;text-align:center;background:#17201e}.device-gate strong{font:600 34px/1.1 "Songti SC",serif}.device-gate span{color:#bcb29f;font-size:14px}
</style>

