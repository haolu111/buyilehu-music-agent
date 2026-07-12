<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import AppShell from '../components/AppShell.vue'
import LessonWorkspaceNav from '../components/LessonWorkspaceNav.vue'
import { lessonPlanApi } from '../api/lessonPlanApi'
import { formatDateTime, statusText } from '../utils/display'
import type { LessonPlanSummary } from '../types'

const lessonPlans = ref<LessonPlanSummary[]>([]), loading = ref(false), error = ref(''), query = ref(''), statusFilter = ref('all')
const filteredPlans = computed(() => lessonPlans.value.filter(plan => (!query.value || plan.title.toLowerCase().includes(query.value.toLowerCase())) && (statusFilter.value === 'all' || plan.parseStatus === statusFilter.value)))
async function loadLessonPlans() { loading.value = true; error.value = ''; try { lessonPlans.value = await lessonPlanApi.listMine() } catch (e) { error.value = e instanceof Error ? e.message : '加载教案失败' } finally { loading.value = false } }
function nextAction(plan: LessonPlanSummary) { if (plan.parseStatus === 'processing') return '查看进度'; if (plan.parseStatus === 'failed') return '重新解析'; if (plan.status === 'confirmed') return '生成互动包'; return '查看并确认方案' }
function nextRoute(plan: LessonPlanSummary) { return plan.status === 'confirmed' ? `/packages/generate?lessonPlanId=${plan.id}` : `/lesson-plans/${plan.id}/parse-result` }
onMounted(loadLessonPlans)
</script>
<template><AppShell><LessonWorkspaceNav />
  <div class="page-heading compact"><div><h1>我的教案</h1><p>查看解析进度，并从系统建议的下一步继续备课。</p></div><RouterLink class="button primary" to="/lesson-plans/upload">＋ 上传教案</RouterLink></div>
  <div class="filter-bar"><input v-model="query" placeholder="搜索教案名称" aria-label="搜索教案名称"><select v-model="statusFilter" aria-label="按解析状态筛选"><option value="all">全部状态</option><option value="success">解析成功</option><option value="processing">解析中</option><option value="failed">解析失败</option></select><button class="button" :disabled="loading" @click="loadLessonPlans">刷新</button></div>
  <p v-if="error" class="error">{{ error }}</p>
  <div class="table-card"><table class="data-table lesson-table"><thead><tr><th>教案名称</th><th>解析状态</th><th>活动方案</th><th>更新时间</th><th>下一步</th></tr></thead><tbody>
    <tr v-for="plan in filteredPlans" :key="plan.id"><td><strong>{{ plan.title }}</strong><small>音乐教案</small></td><td><span class="status-pill" :class="plan.parseStatus">{{ statusText(plan.parseStatus) }}</span></td><td>{{ plan.parseStatus === 'success' ? (plan.status === 'confirmed' ? '方案已确认' : '等待确认') : '尚未生成' }}</td><td>{{ formatDateTime(plan.updatedAt || plan.createdAt) }}</td><td><RouterLink class="text-link" :to="nextRoute(plan)">{{ nextAction(plan) }} →</RouterLink></td></tr>
    <tr v-if="!filteredPlans.length"><td colspan="5" class="empty-cell">{{ loading ? '正在加载教案…' : '没有符合条件的教案' }}</td></tr>
  </tbody></table></div>
</AppShell></template>
