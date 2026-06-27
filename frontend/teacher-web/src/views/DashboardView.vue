<script setup lang="ts">
import { onMounted } from 'vue'
import AppShell from '../components/AppShell.vue'
import { useAuthStore } from '../stores/authStore'

const auth = useAuthStore()
onMounted(() => {
  if (!auth.user) auth.fetchMe().catch(() => undefined)
})
</script>

<template>
  <AppShell>
    <h1>教师工作台</h1>
    <p class="lead">按业务流程完成：班级管理 → 上传教案 → 生成互动包 → 确认方案卡 → 发布与课堂控制。</p>
    <div class="grid">
      <RouterLink class="card action-card" to="/classes">1. 班级管理<span>创建班级，查看学生</span></RouterLink>
      <RouterLink class="card action-card" to="/lesson-plans/upload">2. 上传教案<span>上传 docx/txt 并查看解析结果</span></RouterLink>
      <RouterLink class="card action-card" to="/packages/generate">3. 生成互动包<span>基于教案生成固定五段活动链</span></RouterLink>
      <RouterLink class="card action-card" to="/packages/1/proposal">4. 方案卡确认<span>输入真实 packageId 后查看与确认</span></RouterLink>
    </div>
  </AppShell>
</template>
