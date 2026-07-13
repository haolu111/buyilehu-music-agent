<script setup lang="ts">
import { ref } from 'vue'
withDefaults(defineProps<{ prompt?: string; roles?: string[]; steps?: string[]; audioUrl?: string }>(), { prompt: '选择你的合奏角色，按步骤完成排练。', roles: () => ['节奏组', '旋律组', '音色组', '指挥'], steps: () => ['确认声部', '分组练习', '合奏排练', '完成展示'], audioUrl: '' })
const emit = defineEmits<{ completed: [payload: { result: Record<string, unknown> }] }>()
const role = ref(''); const completedSteps = ref<string[]>([])
function submit() { emit('completed', { result: { role: role.value, completedSteps: completedSteps.value } }) }
</script>
<template><section class="music-activity"><header><span class="activity-kicker">合奏任务</span><h2>找到我的合奏位置</h2><p>{{ prompt }}</p></header><audio v-if="audioUrl" class="activity-audio" :src="audioUrl" controls /><div class="choice-grid"><button v-for="item in roles" :key="String(item)" type="button" :class="{ selected: role === String(item) }" @click="role = String(item)">{{ item }}</button></div><div class="rehearsal-steps"><label v-for="step in steps" :key="String(step)"><input v-model="completedSteps" type="checkbox" :value="String(step)" /><span>{{ step }}</span></label></div><div class="activity-actions"><button class="primary-action" type="button" :disabled="!role || completedSteps.length !== steps.length" @click="submit">完成合奏任务</button></div></section></template>
