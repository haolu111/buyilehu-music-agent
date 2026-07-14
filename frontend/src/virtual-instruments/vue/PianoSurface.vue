<script setup lang="ts">
import { computed } from "vue";
import { formatPitchLabel, type AccidentalPreference, type PitchLabelMode } from "../core/malletLayout";
import { buildPianoLayout } from "../core/pianoLayout";
import type { PlayableZone } from "../core/playableZones";

const props = withDefaults(defineProps<{
  startMidi: number;
  octaveCount?: 1 | 2;
  labelMode?: PitchLabelMode;
  tonicMidi?: number;
  accidentalPreference?: AccidentalPreference;
  activeZoneIds?: Set<string>;
  sustainActive?: boolean;
}>(), {
  octaveCount: 2,
  labelMode: "hidden",
  tonicMidi: 60,
  accidentalPreference: "sharp",
  activeZoneIds: () => new Set<string>(),
  sustainActive: false,
});

const emit = defineEmits<{
  pointerdown: [event: PointerEvent, zone: PlayableZone];
  pointermove: [event: PointerEvent, zone: PlayableZone];
  pointerup: [event: PointerEvent];
  sustainchange: [active: boolean];
}>();

const keys = computed(() => buildPianoLayout({ startMidi: props.startMidi, octaveCount: props.octaveCount }));

function zoneFor(key: (typeof keys.value)[number]): PlayableZone {
  return {
    id: key.id,
    midi: key.midi,
    label: formatPitchLabel(key.midi, { mode: props.labelMode, tonicMidi: props.tonicMidi, accidentalPreference: props.accidentalPreference }),
    action: "note",
    hitArea: { x: key.leftPercent, y: 0, width: key.widthPercent, height: key.kind === "black" ? 62 : 100 },
  };
}

function handleMove(event: PointerEvent): void {
  if (event.buttons === 0 && event.pressure === 0) return;
  const target = document.elementFromPoint(event.clientX, event.clientY)?.closest<HTMLElement>("[data-piano-midi]");
  if (!target) return;
  const key = keys.value.find((candidate) => candidate.midi === Number(target.dataset.pianoMidi));
  if (key) emit("pointermove", event, zoneFor(key));
}
</script>

<template>
  <div class="piano-stage" @pointermove.prevent="handleMove">
    <div class="fallboard"><span>CLASSROOM GRAND</span><i /></div>
    <button
      v-for="key in keys"
      :key="key.id"
      type="button"
      class="piano-key"
      :class="[`kind--${key.kind}`, { active: activeZoneIds.has(key.id) }]"
      :style="{ left: `${key.leftPercent}%`, width: `${key.widthPercent}%` }"
      :data-zone-id="key.id"
      :data-piano-midi="key.midi"
      :aria-label="formatPitchLabel(key.midi, { mode: 'note', accidentalPreference })"
      @pointerdown.prevent="emit('pointerdown', $event, zoneFor(key))"
      @pointerup.prevent="emit('pointerup', $event)"
      @pointercancel.prevent="emit('pointerup', $event)"
      @lostpointercapture="emit('pointerup', $event)"
    ><span>{{ formatPitchLabel(key.midi, { mode: labelMode, tonicMidi, accidentalPreference }) }}</span></button>
    <button class="sustain-pedal" :class="{ active: sustainActive }" type="button" @pointerdown.prevent="emit('sustainchange', true)" @pointerup.prevent="emit('sustainchange', false)" @pointercancel.prevent="emit('sustainchange', false)">
      <span>延音</span><small>SUSTAIN</small>
    </button>
  </div>
</template>

<style scoped>
.piano-stage{position:absolute;inset:0;padding-top:17%;overflow:hidden;background:linear-gradient(145deg,#16191a,#050606 72%);touch-action:none}.fallboard{position:absolute;z-index:6;left:0;right:0;top:0;height:18%;display:flex;align-items:center;justify-content:center;color:#bda47a;background:linear-gradient(#262a29,#080909);box-shadow:0 12px 23px #000c,inset 0 -1px #c7a76c44;font:600 clamp(9px,1.1vw,13px)/1 Futura,sans-serif;letter-spacing:.22em}.fallboard i{position:absolute;bottom:12%;width:36px;height:3px;border-radius:99px;background:#9a7748}.piano-key{position:absolute;top:17%;bottom:0;padding:0;border:1px solid #8f8a7f;border-radius:0 0 8px 8px;touch-action:none}.piano-key.kind--white{z-index:1;color:#57534a;background:linear-gradient(90deg,#b9b7b0,#fffef5 24%,#ece9df 76%,#aaa8a1);box-shadow:inset 0 -12px 15px #8f8a7f33}.piano-key.kind--black{z-index:3;bottom:38%;color:#d9c9ad;background:linear-gradient(90deg,#050606,#3b3e3c 42%,#090a0a 78%);border-color:#050606;box-shadow:inset 0 -8px 13px #000,4px 8px 8px #0008}.piano-key span{position:absolute;left:50%;bottom:7%;transform:translateX(-50%);font:700 clamp(9px,1vw,12px)/1 "Avenir Next",sans-serif}.piano-key.kind--black span{bottom:10%}.piano-key.active{filter:brightness(1.22);transform:translateY(4px);box-shadow:inset 0 0 28px #d7a76188}.sustain-pedal{position:absolute;z-index:8;right:2%;bottom:3%;min-width:92px;padding:10px 18px;border:1px solid #d5bc8c55;border-radius:14px;color:#cfb889;background:#191c1bdb;box-shadow:0 8px 20px #0009}.sustain-pedal span,.sustain-pedal small{display:block}.sustain-pedal small{margin-top:3px;font-size:8px;letter-spacing:.13em;opacity:.6}.sustain-pedal.active{color:#24190f;background:#d4b579;transform:translateY(2px)}@media(max-width:700px) and (orientation:portrait){.piano-stage{padding-top:23%}.fallboard{height:24%}.piano-key{top:23%}.sustain-pedal{min-width:76px;padding:8px 12px}}
</style>

