<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits<{ submitted: [payload: { title: string; notes: string }] }>()
const props = withDefaults(defineProps<{ defaultTitle?: string; prompt?: string }>(), {
  defaultTitle: '我的音乐小作品',
  prompt: '写下你听见的节奏、想到的画面……',
})
const title = ref(props.defaultTitle)
const notes = ref('')
</script>

<template>
  <section class="tool-panel creation-panel">
    <label>作品名称<input v-model="title" maxlength="24" /></label>
    <label>创作灵感<textarea v-model="notes" rows="5" maxlength="240" :placeholder="props.prompt"></textarea></label>
    <button class="primary-action" type="button" :disabled="!notes.trim()" @click="emit('submitted', { title, notes })">保存我的作品</button>
  </section>
</template>
