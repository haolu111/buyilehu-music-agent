<script setup lang="ts">
defineProps<{
  title: string
  subtitle?: string
  status?: string
}>()
</script>

<template>
  <header class="scene-header">
    <div class="scene-mark" aria-hidden="true">
      <span>♫</span>
    </div>
    <div>
      <p v-if="status" class="scene-status">{{ status }}</p>
      <h1>{{ title }}</h1>
      <p v-if="subtitle" class="scene-subtitle">{{ subtitle }}</p>
    </div>
    <div class="header-notes" aria-hidden="true"><span>♪</span><span>♬</span></div>
  </header>
</template>
