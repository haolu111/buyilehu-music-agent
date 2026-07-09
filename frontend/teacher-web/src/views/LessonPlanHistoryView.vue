<script setup lang="ts">
import { onMounted, ref } from 'vue'
import AppShell from '../components/AppShell.vue'
import { lessonPlanApi } from '../api/lessonPlanApi'
import type { LessonPlanSummary } from '../types'

const lessonPlans = ref<LessonPlanSummary[]>([])
const loading = ref(false)
const error = ref('')

function formatTime(value?: string) {
  if (!value) return '-'
  return new Intl.DateTimeFormat('zh-CN', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

async function loadLessonPlans() {
  loading.value = true
  error.value = ''
  try {
    lessonPlans.value = await lessonPlanApi.listMine()
  } catch (exception) {
    error.value = exception instanceof Error ? exception.message : '加载历史教案失败'
  } finally {
    loading.value = false
  }
}

onMounted(loadLessonPlans)
</script>

<template>
  <AppShell>
    <div class="section-header">
      <div>
        <h1>历史教案</h1>
        <p class="muted">这里列出你上传过的教案，包含教案 ID，生成互动包时直接填写这个 ID 即可。</p>
      </div>
      <button class="button" type="button" :disabled="loading" @click="loadLessonPlans">
        {{ loading ? '刷新中...' : '刷新列表' }}
      </button>
    </div>

    <p v-if="error" class="error">{{ error }}</p>

    <div v-if="lessonPlans.length" class="list">
      <article v-for="plan in lessonPlans" :key="plan.id" class="card">
        <div class="list-item">
          <div>
            <h3>{{ plan.title }}</h3>
            <p class="muted">教案 ID：{{ plan.id }} · 状态：{{ plan.status || 'unknown' }} · 解析：{{ plan.parseStatus || 'unknown' }}</p>
          </div>
          <div class="button-row">
            <RouterLink class="button" :to="`/lesson-plans/${plan.id}/parse-result`">查看解析</RouterLink>
            <RouterLink class="button primary" :to="`/packages/generate?lessonPlanId=${plan.id}`">生成互动包</RouterLink>
          </div>
        </div>
        <p class="muted">创建时间：{{ formatTime(plan.createdAt) }} · 更新时间：{{ formatTime(plan.updatedAt) }}</p>
      </article>
    </div>

    <div v-else class="card">
      <p class="muted">{{ loading ? '正在加载教案...' : '还没有上传过教案。' }}</p>
    </div>
  </AppShell>
</template>
