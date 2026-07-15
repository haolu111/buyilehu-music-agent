<script setup lang="ts">
import { ref } from 'vue'
const props = withDefaults(defineProps<{ prompt?: string; sections?: string[]; audioUrl?: string }>(), { prompt: '按音乐出现的顺序排列各段。', sections: () => ['引子', 'A段', 'B段', '尾声'], audioUrl: '' })
const emit = defineEmits<{ completed: [payload: { result: Record<string, unknown> }] }>()
function shuffledSections() {
  const shuffled = [...props.sections]
  for (let index = shuffled.length - 1; index > 0; index -= 1) {
    const target = Math.floor(Math.random() * (index + 1))
    ;[shuffled[index], shuffled[target]] = [shuffled[target], shuffled[index]]
  }
  if (shuffled.length > 1 && shuffled.every((item, index) => item === props.sections[index])) shuffled.push(shuffled.shift()!)
  return shuffled
}
const order = ref(shuffledSections())
function move(index: number, offset: number) { const target = index + offset; if (target < 0 || target >= order.value.length) return; [order.value[index], order.value[target]] = [order.value[target], order.value[index]] }
function submit() { emit('completed', { result: { order: order.value } }) }
</script>
<template><section class="music-activity"><header><span class="activity-kicker">曲式排序</span><h2>排出音乐结构</h2><p>{{ prompt }}</p></header><audio v-if="audioUrl" class="activity-audio" :src="audioUrl" controls /><ol class="order-list"><li v-for="(section, index) in order" :key="`${section}-${index}`"><span>{{ index + 1 }}</span><strong>{{ section }}</strong><button type="button" title="上移" :disabled="index === 0" @click="move(index, -1)">↑</button><button type="button" title="下移" :disabled="index === order.length - 1" @click="move(index, 1)">↓</button></li></ol><div class="activity-actions"><button class="primary-action" type="button" @click="submit">提交曲式顺序</button></div></section></template>
