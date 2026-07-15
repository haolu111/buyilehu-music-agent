<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ArrowRight, FileUp, RefreshCw, Search } from 'lucide-vue-next'
import AppShell from '../components/AppShell.vue'
import LessonWorkspaceNav from '../components/LessonWorkspaceNav.vue'
import { lessonPlanApi } from '../api/lessonPlanApi'
import { formatDateTime, statusText } from '../utils/display'
import type { LessonPlanSummary } from '../types'

const lessonPlans = ref<LessonPlanSummary[]>([])
const loading = ref(false)
const error = ref('')
const query = ref('')
const statusFilter = ref('all')
const filteredPlans = computed(() => lessonPlans.value.filter((plan) => (!query.value || plan.title.toLowerCase().includes(query.value.toLowerCase())) && (statusFilter.value === 'all' || plan.parseStatus === statusFilter.value)))

async function loadLessonPlans() {
  loading.value = true
  error.value = ''
  try {
    lessonPlans.value = await lessonPlanApi.listMine()
  } catch (e) {
    error.value = e instanceof Error ? e.message : '加载教案失败'
  } finally {
    loading.value = false
  }
}

function nextAction(plan: LessonPlanSummary) {
  if (plan.parseStatus === 'processing') return '查看解析进度'
  if (plan.parseStatus === 'failed') return '重新上传并解析'
  if (plan.status === 'confirmed') return '设置课堂'
  return '确认解析内容'
}

function nextRoute(plan: LessonPlanSummary) {
  if (plan.parseStatus === 'failed') return `/lesson-plans/upload?retryLessonPlanId=${plan.id}`
  return plan.status === 'confirmed' ? `/packages/generate?lessonPlanId=${plan.id}` : `/lesson-plans/${plan.id}/parse-result`
}

onMounted(loadLessonPlans)
</script>

<template>
  <AppShell>
    <LessonWorkspaceNav />
    <div class="page-heading compact"><div><p class="eyebrow">教案库</p><h1>我的教案</h1><p>选择一份教案，完成下一步。</p></div><RouterLink class="button primary" to="/lesson-plans/upload"><FileUp :size="18" aria-hidden="true" />上传教案</RouterLink></div>
    <div class="filter-bar">
      <label class="search-field"><Search :size="18" aria-hidden="true" /><input v-model="query" placeholder="搜索教案名称" aria-label="搜索教案名称"></label>
      <select v-model="statusFilter" aria-label="按解析状态筛选"><option value="all">全部状态</option><option value="success">解析成功</option><option value="processing">解析中</option><option value="failed">解析失败</option></select>
      <button class="button ghost" type="button" :disabled="loading" @click="loadLessonPlans"><RefreshCw :size="17" aria-hidden="true" />刷新</button>
    </div>
    <p v-if="error" class="error">{{ error }}</p>
    <section class="lesson-plan-list" aria-label="教案列表">
      <article v-for="plan in filteredPlans" :key="plan.id" class="lesson-plan-row">
        <div class="lesson-plan-title"><strong>{{ plan.title }}</strong><small>{{ formatDateTime(plan.updatedAt || plan.createdAt) }}</small></div>
        <span class="status-pill" :class="plan.parseStatus">{{ statusText(plan.parseStatus) }}</span>
        <span class="lesson-plan-status">{{ plan.parseStatus === 'success' ? (plan.status === 'confirmed' ? '已确认' : '待确认') : '等待解析' }}</span>
        <RouterLink class="button lesson-plan-action" data-testid="lesson-plan-next-action" :to="nextRoute(plan)">{{ nextAction(plan) }} <ArrowRight :size="16" aria-hidden="true" /></RouterLink>
      </article>
      <div v-if="!filteredPlans.length" class="empty-inline">{{ loading ? '正在加载教案…' : '没有符合条件的教案' }}</div>
    </section>
  </AppShell>
</template>
