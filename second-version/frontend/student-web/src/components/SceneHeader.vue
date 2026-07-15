<script setup lang="ts">
import buyilehuLogo from '../assets/buyilehu-logo-transparent.png'

defineProps<{
  title: string
  subtitle?: string
  status?: string
  brand?: boolean
}>()
</script>

<template>
  <header class="scene-header" :class="{ 'brand-scene-header': brand }">
    <template v-if="brand">
      <div class="scene-brand-lockup">
        <img class="scene-brand-logo" :src="buyilehuLogo" alt="不亦乐乎" />
        <p v-if="subtitle" class="scene-subtitle">{{ subtitle }}</p>
      </div>
    </template>
    <template v-else>
      <div class="scene-mark" aria-hidden="true"><span>♫</span></div>
      <div>
        <p v-if="status" class="scene-status">{{ status }}</p>
        <h1>{{ title }}</h1>
        <p v-if="subtitle" class="scene-subtitle">{{ subtitle }}</p>
      </div>
      <div class="header-notes" aria-hidden="true"><span>♪</span><span>♬</span></div>
    </template>
  </header>
</template>
