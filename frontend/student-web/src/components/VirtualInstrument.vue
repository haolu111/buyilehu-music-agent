<script setup lang="ts">
import { ref } from 'vue'
interface InstrumentKey { note: string; label: string; frequency: number; color: string }
withDefaults(defineProps<{ prompt?: string; keys?: InstrumentKey[] }>(), { prompt: '敲击音条，创作一段短旋律。', keys: () => [] })
const emit = defineEmits<{ completed: [payload: { result: Record<string, unknown> }] }>()
const sequence = ref<string[]>([])
let context: AudioContext | null = null
function play(key: InstrumentKey) { context ||= new AudioContext(); const oscillator = context.createOscillator(); const gain = context.createGain(); oscillator.frequency.value = key.frequency; oscillator.type = 'sine'; gain.gain.setValueAtTime(.24, context.currentTime); gain.gain.exponentialRampToValueAtTime(.001, context.currentTime + .55); oscillator.connect(gain).connect(context.destination); oscillator.start(); oscillator.stop(context.currentTime + .55); sequence.value.push(key.note) }
function submit() { emit('completed', { result: { notes: sequence.value } }) }
</script>
<template><section class="music-activity"><header><span class="activity-kicker">虚拟乐器</span><h2>我的音条琴</h2><p>{{ prompt }}</p></header><div class="instrument-keys"><button v-for="key in keys" :key="key.note" type="button" :style="{ background: key.color }" @click="play(key)"><strong>{{ key.label }}</strong><small>{{ Math.round(key.frequency) }} Hz</small></button></div><div class="played-notes"><span v-if="!sequence.length">敲击上面的音条开始创作</span><b v-for="(note, index) in sequence" :key="`${note}-${index}`">{{ note }}</b></div><div class="activity-actions"><button class="secondary-action" type="button" :disabled="!sequence.length" @click="sequence = []">清空</button><button class="primary-action" type="button" :disabled="sequence.length < 3" @click="submit">提交旋律</button></div></section></template>
