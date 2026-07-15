<script setup lang="ts">
import { reactive } from 'vue'
withDefaults(defineProps<{ prompt?: string; items?: string[]; options?: string[]; audioUrl?: string }>(), { prompt: '为每件乐器选择对应的音色家族。', items: () => ['小提琴', '长笛', '小号', '鼓'], options: () => ['弦乐器', '木管乐器', '铜管乐器', '打击乐器'], audioUrl: '' })
const emit = defineEmits<{ completed: [payload: { result: Record<string, unknown> }] }>()
const matches = reactive<Record<string, string>>({})
function submit() { emit('completed', { result: { matches: { ...matches } } }) }
</script>
<template><section class="music-activity"><header><span class="activity-kicker">音色配对</span><h2>听音色，找家族</h2><p>{{ prompt }}</p></header><audio v-if="audioUrl" class="activity-audio" :src="audioUrl" controls /><div class="match-list"><label v-for="item in items" :key="item"><strong>{{ typeof item === 'string' ? item : String(item) }}</strong><select v-model="matches[String(item)]"><option value="">选择家族</option><option v-for="option in options" :key="String(option)" :value="String(option)">{{ option }}</option></select></label></div><div class="activity-actions"><button class="primary-action" type="button" :disabled="Object.keys(matches).length !== items.length" @click="submit">提交配对</button></div></section></template>
