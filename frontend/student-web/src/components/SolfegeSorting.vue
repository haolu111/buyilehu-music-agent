<script setup lang="ts">
import { ref } from 'vue'
import { playSolfege } from '../utils/activitySound'
const props = withDefaults(defineProps<{ prompt?: string; tokens?: string[]; targetLength?: number }>(), { prompt: '按听到的顺序排列唱名。', tokens: () => ['do', 're', 'mi', 'sol'], targetLength: 4 })
const emit = defineEmits<{ completed: [payload: { result: Record<string, unknown> }] }>()
const sequence = ref<string[]>([])
function add(token: string) { if (sequence.value.length < props.targetLength) { playSolfege(token); sequence.value.push(token) } }
function submit() { emit('completed', { result: { sequence: sequence.value } }) }
</script>
<template><section class="music-activity"><header><span class="activity-kicker">唱名排序</span><h2>把唱名排成旋律</h2><p>{{ prompt }}</p></header><div class="sequence-lane"><span v-for="index in targetLength" :key="index">{{ sequence[index - 1] || index }}</span></div><div class="music-token-grid"><button v-for="token in tokens" :key="token" type="button" @click="add(token)">{{ token }}</button></div><div class="activity-actions"><button class="secondary-action" type="button" :disabled="!sequence.length" @click="sequence.pop()">撤销</button><button class="secondary-action" type="button" :disabled="!sequence.length" @click="sequence = []">重置</button><button class="primary-action" type="button" :disabled="sequence.length !== targetLength" @click="submit">提交顺序</button></div></section></template>
