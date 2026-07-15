<script setup lang="ts">
import { useRoute } from 'vue-router'
const route = useRoute()
const items = [
  { label: '我的教案', to: '/lesson-plans/history', match: '/lesson-plans/history' },
  { label: '上传教案', to: '/lesson-plans/upload', match: '/lesson-plans/upload' },
  { label: '生成互动包', to: '/packages/generate', match: '/packages/generate' },
]
</script>

<template>
  <div class="workspace-context">
    <p class="breadcrumb">教案与互动包 / {{ items.find(item => route.path.startsWith(item.match))?.label || '内容详情' }}</p>
    <nav class="workspace-tabs" aria-label="教案与互动包">
      <RouterLink v-for="item in items" :key="item.to" :to="item.to" :class="{ active: route.path.startsWith(item.match) }">{{ item.label }}</RouterLink>
    </nav>
  </div>
</template>
