<script setup lang="ts">
import type { ClassroomInstrumentActivityConfig } from "../core/classroomInstrumentActivity";
const props = defineProps<{ modelValue: ClassroomInstrumentActivityConfig }>();
const emit = defineEmits<{ "update:modelValue": [value: ClassroomInstrumentActivityConfig] }>();
function patch(value: Partial<ClassroomInstrumentActivityConfig>) { emit("update:modelValue", { ...props.modelValue, ...value }); }
function patchMetronome(value: Partial<ClassroomInstrumentActivityConfig["metronome"]>) { patch({ metronome: { ...props.modelValue.metronome, ...value } }); }
</script>
<template><div class="teacher-bar">
  <label>玩法<select :value="modelValue.mode" @change="patch({mode:($event.target as HTMLSelectElement).value as ClassroomInstrumentActivityConfig['mode']})"><option value="free_play">自由演奏</option><option value="steady_beat">稳定拍</option><option value="echo">听后复刻</option><option value="ensemble_cue">合奏提示</option></select></label>
  <label>年级<select :value="modelValue.gradePreset" @change="patch({gradePreset:($event.target as HTMLSelectElement).value as ClassroomInstrumentActivityConfig['gradePreset']})"><option value="lower_primary">小学低段</option><option value="middle_primary">小学中段</option><option value="upper_primary">小学高段</option></select></label>
  <label>每分钟拍数<input type="number" min="40" max="160" :value="modelValue.metronome.bpm" @change="patchMetronome({bpm:Number(($event.target as HTMLInputElement).value)})"></label>
  <label>拍号<select :value="modelValue.metronome.meter" @change="patchMetronome({meter:($event.target as HTMLSelectElement).value as ClassroomInstrumentActivityConfig['metronome']['meter']})"><option>2/4</option><option>3/4</option><option>4/4</option><option>6/8</option></select></label>
  <label class="check"><input type="checkbox" :checked="modelValue.metronome.continueDuringPerformance" @change="patchMetronome({continueDuringPerformance:($event.target as HTMLInputElement).checked})">演奏时继续节拍器</label>
</div></template>
<style scoped>.teacher-bar{display:flex;flex-wrap:wrap;gap:10px;padding:12px 16px;color:#efe5d3;background:#25312e}.teacher-bar label{display:flex;align-items:center;gap:6px;font-size:11px;font-weight:700}.teacher-bar select,.teacher-bar input{min-height:34px;padding:5px 8px;border:1px solid #fff2;border-radius:8px;color:#f4ead7;background:#111917}.teacher-bar input[type=number]{width:72px}.check{padding:0 10px;border-radius:8px;background:#fff1}</style>

