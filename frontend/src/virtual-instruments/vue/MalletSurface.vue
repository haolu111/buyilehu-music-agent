<script setup lang="ts">
import { computed } from "vue";
import {
  buildMalletLayout,
  formatPitchLabel,
  type AccidentalPreference,
  type MalletLayoutMode,
  type PitchLabelMode,
} from "../core/malletLayout";
import type { PlayableZone } from "../core/playableZones";

const props = withDefaults(defineProps<{
  instrumentId: string;
  mode?: MalletLayoutMode;
  registerStartMidi: number;
  labelMode?: PitchLabelMode;
  tonicMidi?: number;
  accidentalPreference?: AccidentalPreference;
  rollEnabled?: boolean;
  activeZoneIds?: Set<string>;
}>(), {
  mode: "diatonic",
  labelMode: "number",
  tonicMidi: 60,
  accidentalPreference: "sharp",
  rollEnabled: false,
  activeZoneIds: () => new Set<string>(),
});

const emit = defineEmits<{
  pointerdown: [event: PointerEvent, zone: PlayableZone];
  pointerup: [event: PointerEvent];
}>();

const bars = computed(() => buildMalletLayout({
  instrumentId: props.instrumentId,
  mode: props.mode,
  registerStartMidi: props.registerStartMidi,
}));

const materialClass = computed(() => props.instrumentId.replace("virtual_", ""));

function zoneFor(bar: (typeof bars.value)[number]): PlayableZone {
  return {
    id: bar.id,
    midi: bar.midi,
    label: formatPitchLabel(bar.midi, {
      mode: props.labelMode,
      tonicMidi: props.tonicMidi,
      accidentalPreference: props.accidentalPreference,
    }),
    action: props.rollEnabled ? "roll" : "note",
    hitArea: { x: bar.leftPercent, y: 0, width: bar.widthPercent, height: bar.heightPercent },
  };
}
</script>

<template>
  <div class="mallet-stage" :class="[`mallet-stage--${materialClass}`, `mode--${mode}`]">
    <div class="resonator-bed" aria-hidden="true">
      <i v-for="index in 12" :key="index" :style="{ height: `${82 - index * 3.7}%` }" />
    </div>
    <button
      v-for="bar in bars"
      :key="bar.id"
      type="button"
      class="mallet-bar"
      :class="[`row--${bar.row}`, { active: activeZoneIds.has(bar.id) }]"
      :style="{
        left: `${bar.leftPercent}%`,
        width: `${bar.widthPercent}%`,
        height: `${bar.heightPercent}%`,
      }"
      :data-zone-id="bar.id"
      :aria-label="`${formatPitchLabel(bar.midi, { mode: 'note', accidentalPreference })} ${formatPitchLabel(bar.midi, { mode: labelMode, tonicMidi, accidentalPreference })}`"
      @pointerdown.prevent="emit('pointerdown', $event, zoneFor(bar))"
      @pointerup.prevent="emit('pointerup', $event)"
      @pointercancel.prevent="emit('pointerup', $event)"
      @lostpointercapture="emit('pointerup', $event)"
    >
      <span>{{ formatPitchLabel(bar.midi, { mode: labelMode, tonicMidi, accidentalPreference }) }}</span>
      <i aria-hidden="true" /><i aria-hidden="true" />
    </button>
    <div class="frame-rail frame-rail--top" aria-hidden="true" />
    <div class="frame-rail frame-rail--bottom" aria-hidden="true" />
  </div>
</template>

<style scoped>
.mallet-stage{position:absolute;inset:0;overflow:hidden;background:radial-gradient(circle at 50% 0,#4b382a 0,#1d1713 45%,#0c0d0c 100%);isolation:isolate}.mallet-stage:before{content:"";position:absolute;inset:3% 2%;border-radius:24px;background:linear-gradient(110deg,#53341f,#221811 45%,#654126);box-shadow:inset 0 0 0 2px #d5a56a22,0 28px 45px #0009;transform:perspective(800px) rotateX(2deg)}.resonator-bed{position:absolute;z-index:0;inset:18% 7% 7%;display:flex;gap:2.8%;align-items:flex-start;justify-content:center;opacity:.32}.resonator-bed i{width:4.2%;border-radius:0 0 50% 50%;background:linear-gradient(90deg,#3d3024,#b58750 40%,#4b3727);box-shadow:inset -3px 0 7px #0007}.mallet-bar{position:absolute;z-index:3;bottom:7%;padding:0;border:1px solid #fff2;border-radius:7px 7px 11px 11px;color:#f7e8c9;background:linear-gradient(90deg,#5e301c,#a45c32 18%,#cd8950 50%,#7a3e24 86%,#3c2015);box-shadow:inset 0 1px 1px #fff5,inset 0 -9px 14px #27130d99,0 10px 13px #0008;touch-action:none}.mallet-bar.row--accidental{z-index:5;bottom:46%;background:linear-gradient(90deg,#241c18,#5a493d 46%,#1a1512);color:#ead7b9}.mallet-bar span{position:absolute;left:50%;top:48%;transform:translate(-50%,-50%);font:700 clamp(10px,1.2vw,15px)/1 "Avenir Next","PingFang SC",sans-serif;text-shadow:0 1px 3px #000}.mallet-bar>i{position:absolute;left:50%;width:7px;height:7px;transform:translateX(-50%);border-radius:50%;background:#dac29a;box-shadow:inset 0 1px 2px #fff8,0 1px 2px #000}.mallet-bar>i:first-of-type{top:7%}.mallet-bar>i:last-of-type{bottom:7%}.mallet-bar.active{filter:brightness(1.32);transform:translateY(3px);box-shadow:inset 0 0 26px #ffd59199,0 4px 7px #0008}.mallet-stage--marimba .mallet-bar{background:linear-gradient(90deg,#402217,#7e4329 22%,#a9683b 52%,#562b1c 87%,#2b1710)}.mallet-stage--glockenspiel{background:radial-gradient(circle at 50% 0,#6b7472,#242b2c 48%,#0d1112)}.mallet-stage--glockenspiel .mallet-bar{color:#29302f;background:linear-gradient(90deg,#6f7b7b,#e5e0d1 22%,#fffdf2 48%,#a6afad 78%,#535d5d);text-shadow:0 1px #fff}.mallet-stage--glockenspiel .resonator-bed{opacity:.12}.frame-rail{position:absolute;z-index:2;left:2%;right:2%;height:3.5%;border-radius:999px;background:linear-gradient(#835436,#362318);box-shadow:0 5px 8px #0008}.frame-rail--top{top:39%}.frame-rail--bottom{bottom:3%}@media(max-width:700px) and (orientation:portrait){.mallet-bar span{font-size:10px}.mallet-stage:before{inset:2% 1%}}
</style>
