<script setup lang="ts">
defineProps<{
  message: string
  tone?: 'success' | 'warning' | 'error'
}>()
</script>

<template>
  <Transition name="toast">
    <div v-if="message" class="feedback-toast" :class="tone || 'success'" role="status">
      {{ message }}
    </div>
  </Transition>
</template>
