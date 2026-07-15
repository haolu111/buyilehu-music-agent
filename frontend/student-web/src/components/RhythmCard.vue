<script setup lang="ts">
defineProps<{
  name: string
  pattern: string
  active?: boolean
}>()
</script>

<template>
  <button class="rhythm-card" :class="{ active }" type="button">
    <span class="rhythm-name">{{ name }}</span>
    <span class="rhythm-pattern">{{ pattern }}</span>
  </button>
</template>
