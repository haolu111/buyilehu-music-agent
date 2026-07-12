<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import AppShell from '../components/AppShell.vue'
import { useAuthStore } from '../stores/authStore'
import { classApi } from '../api/classApi'
import { classroomApi } from '../api/classroomApi'
import { lessonPlanApi } from '../api/lessonPlanApi'
import { packageApi } from '../api/packageApi'
import { formatDateTime, statusText } from '../utils/display'
import type { ClassInfo, ClassroomSession, LessonPlanSummary, PackageInfo } from '../types'

const auth = useAuthStore()
const classes = ref<ClassInfo[]>([]), sessions = ref<ClassroomSession[]>([]), plans = ref<LessonPlanSummary[]>([]), packages = ref<PackageInfo[]>([])
const loading = ref(true)
const teacherName = computed(() => auth.user?.displayName || auth.user?.realName || '老师')
const liveSession = computed(() => sessions.value.find(item => item.status === 'running') || sessions.value.find(item => item.status === 'not_started'))
const pendingPlans = computed(() => plans.value.filter(item => item.parseStatus === 'success' && item.status !== 'confirmed').length)
const readyPackages = computed(() => packages.value.filter(item => ['generated', 'confirmed', 'draft'].includes(item.status)).length)
const upcomingCount = computed(() => sessions.value.filter(item => item.status === 'not_started').length)
const recentPackages = computed(() => packages.value.slice(0, 3))

async function loadDashboard() {
  loading.value = true
  const results = await Promise.allSettled([classApi.listClasses(), classroomApi.listActiveSessions(), lessonPlanApi.listMine(), packageApi.listPackages()])
  if (results[0].status === 'fulfilled') classes.value = results[0].value
  if (results[1].status === 'fulfilled') sessions.value = results[1].value
  if (results[2].status === 'fulfilled') plans.value = results[2].value
  if (results[3].status === 'fulfilled') packages.value = results[3].value
  loading.value = false
}
onMounted(() => { if (!auth.user) auth.fetchMe().catch(() => undefined); loadDashboard() })
</script>

<template>
  <AppShell>
    <div class="page-heading"><div><p class="eyebrow">教学工作台</p><h1>{{ teacherName }}，今天准备上什么课？</h1><p>集中处理待办、进入课堂，或继续最近的备课工作。</p></div><RouterLink class="button primary" to="/lesson-plans/upload">＋ 上传新教案</RouterLink></div>
    <section class="today-class card" :class="{ empty: !liveSession }">
      <div><span class="status-pill" :class="liveSession?.status">{{ liveSession ? statusText(liveSession.status) : '今日暂无课堂' }}</span><p class="eyebrow">今日课堂</p><h2>{{ liveSession?.courseTitle || (liveSession ? '音乐互动课堂' : '安排一节新的音乐课堂') }}</h2><p v-if="liveSession">{{ formatDateTime(liveSession.scheduledStartAt || liveSession.startedAt) }} · {{ liveSession.nodeStates.length }} 个课堂环节</p><p v-else>从已经发布的互动包创建课堂后，会显示在这里。</p></div>
      <RouterLink v-if="liveSession" class="button teaching" :to="`/classroom/${liveSession.id}/control`">进入课堂控制台 →</RouterLink><RouterLink v-else class="button" to="/classrooms">查看课堂安排</RouterLink>
    </section>
    <section class="dashboard-grid">
      <div class="card task-panel"><div class="panel-heading"><div><p class="eyebrow">待处理事项</p><h2>接下来要做</h2></div><span>{{ pendingPlans + readyPackages + upcomingCount }} 项</span></div>
        <RouterLink to="/lesson-plans/history"><b>{{ pendingPlans }}</b><span><strong>教案等待确认活动方案</strong><small>查看分析结果并确认下一步</small></span><i>→</i></RouterLink>
        <RouterLink to="/packages/generate"><b>{{ readyPackages }}</b><span><strong>互动包可继续处理</strong><small>确认、预览或发布到班级</small></span><i>→</i></RouterLink>
        <RouterLink to="/classrooms"><b>{{ upcomingCount }}</b><span><strong>课堂等待开始</strong><small>检查课堂环节与班级状态</small></span><i>→</i></RouterLink>
      </div>
      <div class="card quick-panel"><div class="panel-heading"><div><p class="eyebrow">快捷创建</p><h2>开始新的工作</h2></div></div>
        <RouterLink to="/lesson-plans/upload"><span>文</span><div><strong>上传新教案</strong><small>自动识别目标与教学流程</small></div></RouterLink>
        <RouterLink to="/classes"><span>人</span><div><strong>创建班级</strong><small>生成邀请码并管理学生</small></div></RouterLink>
        <RouterLink to="/lesson-plans/history"><span>♫</span><div><strong>从历史教案继续</strong><small>查看方案并生成互动包</small></div></RouterLink>
      </div>
    </section>
    <section class="recent-section"><div class="section-header"><div><p class="eyebrow">最近内容</p><h2>互动包作品</h2></div><RouterLink class="text-link" to="/lesson-plans/history">查看全部 →</RouterLink></div>
      <div v-if="recentPackages.length" class="package-grid"><RouterLink v-for="(item,index) in recentPackages" :key="item.id" class="package-card" :to="`/packages/${item.id}`"><div class="package-cover" :class="`cover-${index % 3}`"><span>♫</span></div><div><span class="status-pill">{{ statusText(item.status) }}</span><h3>{{ item.title }}</h3><p>{{ item.description || '课堂互动活动包' }}</p></div></RouterLink></div>
      <div v-else class="empty-inline">{{ loading ? '正在同步教学内容…' : '还没有互动包，从上传一份教案开始。' }}</div>
    </section>
  </AppShell>
</template>
