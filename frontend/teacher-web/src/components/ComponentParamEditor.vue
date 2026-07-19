<script setup lang="ts">
import { reactive } from 'vue'

const emit = defineEmits<{
  change: [payload: Record<string, unknown>]
}>()

const params = reactive({
  tempo: 90,
  allowRetry: true,
})
</script>

<template>
  <div class="stack">
    <label>
      速度 BPM
      <input v-model.number="params.tempo" min="40" max="180" type="number" @change="emit('change', { ...params })" />
    </label>
    <label class="inline-control">
      <input v-model="params.allowRetry" type="checkbox" @change="emit('change', { ...params })" />
      允许重试
    </label>
  </div>
</template>