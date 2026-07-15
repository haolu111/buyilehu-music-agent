<script setup lang="ts">
import { computed, ref } from 'vue'
import { playMelodyLevel } from '../utils/activitySound'
const props = withDefaults(defineProps<{ prompt?: string; notes?: string[]; levels?: string[]; audioUrl?: string }>(), { prompt: '选择每一拍的高低，画出旋律线。', notes: () => ['same', 'up', 'down', 'same'], levels: () => ['high', 'middle', 'low'], audioUrl: '' })
const emit = defineEmits<{ completed: [payload: { result: Record<string, unknown> }] }>()
const trace = ref<string[]>([])
const labels: Record<string, string> = { high: '高', middle: '中', low: '低', up: '高', same: '中', down: '低' }
const points = computed(() => trace.value.map((level, index) => `${25 + index * (250 / Math.max(props.notes.length - 1, 1))},${level === 'high' ? 25 : level === 'low' ? 125 : 75}`).join(' '))
function choose(level: string) { if (trace.value.length < props.notes.length) { playMelodyLevel(level); trace.value.push(level) } }
function submit() { emit('completed', { result: { trace: trace.value } }) }
</script>
<template><section class="music-activity"><header><span class="activity-kicker">旋律轨迹</span><h2>画出声音的高低</h2><p>{{ prompt }}</p></header><audio v-if="audioUrl" class="activity-audio" :src="audioUrl" controls /><svg class="melody-canvas" viewBox="0 0 300 150" role="img" aria-label="旋律轨迹"><line v-for="y in [25,75,125]" :key="y" x1="10" :y1="y" x2="290" :y2="y" /><polyline :points="points" /><circle v-for="point in points.split(' ').filter(Boolean)" :key="point" :cx="point.split(',')[0]" :cy="point.split(',')[1]" r="6" /></svg><div class="choice-grid compact"><button v-for="level in levels" :key="level" type="button" @click="choose(level)">{{ labels[level] || level }}</button></div><div class="activity-actions"><button class="secondary-action" type="button" :disabled="!trace.length" @click="trace.pop()">撤销</button><button class="primary-action" type="button" :disabled="trace.length !== notes.length" @click="submit">提交旋律线</button></div></section></template>
