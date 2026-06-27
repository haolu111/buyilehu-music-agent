<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits<{
  submitted: [payload: { title: string; notes: string }]
}>()

const title = ref('我的节奏')
const notes = ref('')
</script>

<template>
  <section class="tool-panel creation-panel">
    <label>
      作品名
      <input v-model="title" maxlength="24" />
    </label>
    <label>
      创作记录
      <textarea v-model="notes" rows="5" maxlength="240"></textarea>
    </label>
    <button
      class="primary-action"
      type="button"
      :disabled="!notes.trim()"
      @click="emit('submitted', { title, notes })"
    >
      完成
    </button>
  </section>
</template>
