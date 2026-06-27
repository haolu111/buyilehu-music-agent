<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppShell from '../components/AppShell.vue'
import { packageApi } from '../api/packageApi'
import type { GenerationJob } from '../types'

const route = useRoute()
const router = useRouter()
const lessonPlanId = ref(String(route.query.lessonPlanId || ''))
const loading = ref(false)
const error = ref('')
const job = ref<GenerationJob | null>(null)

async function generate() {
  loading.value = true
  error.value = ''
  try {
    job.value = await packageApi.createGenerationJob(Number(lessonPlanId.value), { template: 'standard-five-step' })
    if (job.value.packageId) {
      await router.push(`/packages/${job.value.packageId}/proposal`)
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : '生成失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AppShell>
    <h1>生成互动包</h1>
    <div class="card stack">
      <label>教案 ID<input v-model="lessonPlanId" placeholder="例如：1" /></label>
      <p class="muted">第一阶段使用固定模板：课堂入口页 → 节拍体验工具 → 节奏拖拽游戏 → 创编工作坊 → 展示总结页。</p>
      <button class="primary" :disabled="loading" @click="generate">{{ loading ? '生成中...' : '创建生成任务' }}</button>
      <p v-if="error" class="error">{{ error }}</p>
    </div>
  </AppShell>
</template>
