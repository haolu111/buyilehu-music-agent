<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ArrowRight, CalendarClock, CheckCircle2, CircleAlert, ClipboardCheck, FileMusic, FileUp, PlayCircle, RefreshCw, Send, Settings2, UsersRound } from 'lucide-vue-next'
import AppShell from '../components/AppShell.vue'
import { useAuthStore } from '../stores/authStore'
import { classApi } from '../api/classApi'
import { classroomApi } from '../api/classroomApi'
import { lessonPlanApi } from '../api/lessonPlanApi'
import { packageApi } from '../api/packageApi'
import { formatDateTime, statusText } from '../utils/display'
import type { ClassInfo, ClassroomSession, LessonPlanSummary, PackageInfo } from '../types'
import musicClassroomHero from '../assets/music-children-orff-banner.png'
import musicDashboardDecorations from '../assets/music-dashboard-decorations.png'
import musicWorkspaceStickers from '../assets/music-workspace-stickers.png'

const auth = useAuthStore()
const sessions = ref<ClassroomSession[]>([])
const classes = ref<ClassInfo[]>([])
const plans = ref<LessonPlanSummary[]>([])
const packages = ref<PackageInfo[]>([])
const loading = ref(true)
const loadError = ref('')
const teacherName = computed(() => auth.user?.displayName || auth.user?.realName || '老师')
const liveSession = computed(() => sessions.value.find((item) => ['running', 'paused'].includes(item.status)) || sessions.value.find((item) => item.status === 'not_started'))
const pendingPlans = computed(() => plans.value.filter((item) => item.parseStatus === 'success' && item.status !== 'confirmed').length)
const readyPackageStatuses = ['generated', 'confirmed', 'draft', 'modified']
const readyPackages = computed(() => packages.value.filter((item) => readyPackageStatuses.includes(item.status)).length)
const firstReadyPackage = computed(() => packages.value.find((item) => readyPackageStatuses.includes(item.status)))
const upcomingCount = computed(() => sessions.value.filter((item) => item.status === 'not_started').length)
const recentPackages = computed(() => packages.value.slice(0, 2))
const recentClasses = computed(() => classes.value.slice(0, 2))
const visibleContinueItems = computed(() => continueItems.value.slice(0, 2))
const classroomEntryRoute = computed(() => liveSession.value ? `/classroom/${liveSession.value.id}/control` : '/classrooms')
const currentClassNode = computed(() => liveSession.value?.nodeStates.find((node) => node.activityNodeId === liveSession.value?.currentNodeId) || liveSession.value?.nodeStates.find((node) => node.status === 'unlocked'))
const unlockedNodeCount = computed(() => liveSession.value?.nodeStates.filter((node) => node.status === 'unlocked').length || 0)
const classroomProgress = computed(() => {
  const total = liveSession.value?.nodeStates.length || 0
  return total ? Math.round((unlockedNodeCount.value / total) * 100) : 0
})
const classroomActionLabel = computed(() => {
  if (liveSession.value?.status === 'not_started') return '开始课堂'
  if (liveSession.value?.status === 'paused') return '继续课堂'
  return '进入课堂'
})
const preparationStages = [
  { label: '上传', icon: FileUp },
  { label: '确认', icon: CheckCircle2 },
  { label: '设置', icon: Settings2 },
  { label: '发布', icon: Send },
]
const packageTodo = computed(() => {
  const item = firstReadyPackage.value
  if (!item) return undefined
  if (item.status === 'generated') return { id: 'packages', count: readyPackages.value, label: '个互动包待继续', action: '确认互动方案', to: `/packages/${item.id}/proposal`, icon: FileMusic, testId: 'continue-package-item' }
  if (item.status === 'modified') return { id: 'packages', count: readyPackages.value, label: '个互动包待发布', action: '发布课堂', to: `/packages/${item.id}/publish`, icon: FileMusic, testId: 'continue-package-item' }
  return { id: 'packages', count: readyPackages.value, label: '个互动包待继续', action: item.status === 'draft' ? '继续编辑互动包' : '编辑互动包', to: `/packages/${item.id}/edit`, icon: FileMusic, testId: 'continue-package-item' }
})
const continueItems = computed(() => [
  pendingPlans.value > 0 ? { id: 'plans', count: pendingPlans.value, label: '份教案待确认', action: '确认解析内容', to: '/lesson-plans/history', icon: ClipboardCheck, testId: 'continue-plan-item' } : undefined,
  packageTodo.value,
  upcomingCount.value > 0 ? { id: 'classrooms', count: upcomingCount.value, label: '节课堂待开始', action: '查看课堂', to: '/classrooms', icon: CalendarClock, testId: 'continue-classroom-item' } : undefined,
].filter(Boolean) as Array<{ id: string; count: number; label: string; action: string; to: string; icon: typeof ClipboardCheck; testId: string }>)

function packageDestination(item: PackageInfo) {
  if (item.status === 'generated') return `/packages/${item.id}/proposal`
  if (item.status === 'modified') return `/packages/${item.id}/publish`
  if (['draft', 'confirmed'].includes(item.status)) return `/packages/${item.id}/edit`
  return `/packages/${item.id}`
}

function packageNextAction(item: PackageInfo) {
  if (item.status === 'generated') return '确认方案'
  if (item.status === 'modified') return '发布课堂'
  if (['draft', 'confirmed'].includes(item.status)) return '继续编辑'
  return '查看详情'
}

function packageLessonPlanLabel(item: PackageInfo) {
  const sourcePlanName = item.description?.match(/《([^》]+)》/)?.[1]?.trim()
  if (sourcePlanName) return `《${sourcePlanName}》教案`

  const packageName = item.title.replace(/互动包$/, '').trim()
  return packageName ? `${packageName}教案` : '音乐教案'
}

async function listDashboardClasses() {
  const classList = await classApi.listClasses()
  const visibleClasses = classList.slice(0, 2)
  const studentResults = await Promise.allSettled(
    visibleClasses.map((item) => classApi.listStudents(item.id)),
  )

  return classList.map((item, index) => {
    const studentResult = studentResults[index]
    return studentResult?.status === 'fulfilled'
      ? { ...item, studentCount: studentResult.value.length }
      : item
  })
}

async function loadDashboard() {
  loading.value = true
  loadError.value = ''
  const results = await Promise.allSettled([classroomApi.listActiveSessions(), lessonPlanApi.listMine(), packageApi.listPackages(), listDashboardClasses()])
  if (results[0].status === 'fulfilled') sessions.value = results[0].value
  if (results[1].status === 'fulfilled') plans.value = results[1].value
  if (results[2].status === 'fulfilled') packages.value = results[2].value
  if (results[3].status === 'fulfilled') classes.value = results[3].value
  if (results.some((result) => result.status === 'rejected')) loadError.value = '部分教学数据暂时无法加载，请重试。'
  loading.value = false
}

onMounted(() => {
  if (!auth.user) auth.fetchMe().catch(() => undefined)
  loadDashboard()
})
</script>

<template>
  <AppShell>
    <section class="dashboard-hero">
      <div class="dashboard-hero-copy">
        <h1>教学工作台</h1>
        <h2>{{ teacherName }}，今天准备上什么课？</h2>
        <p>轻松备课，高效互动，让音乐课堂更有趣。</p>
      </div>
      <div class="hero-preparation-flow" aria-label="备课顺序">
        <strong>备课顺序</strong>
        <ol>
          <li v-for="(stage, index) in preparationStages" :key="stage.label">
            <i :class="`hero-flow-${index}`"><component :is="stage.icon" :size="15" aria-hidden="true" /></i>
            <span>{{ stage.label }}</span>
            <ArrowRight v-if="index < preparationStages.length - 1" :size="14" aria-hidden="true" />
          </li>
        </ol>
      </div>
      <div class="dashboard-primary-actions" data-testid="dashboard-primary-actions">
        <RouterLink class="button primary" to="/lesson-plans/upload"><span class="hero-action-icon"><FileUp :size="22" aria-hidden="true" /></span>上传教案</RouterLink>
        <RouterLink class="button teaching" :to="classroomEntryRoute"><span class="hero-action-icon"><PlayCircle :size="24" aria-hidden="true" /></span>进入课堂</RouterLink>
      </div>
      <div class="dashboard-hero-scene" data-testid="dashboard-music-scene" aria-hidden="true"><img :src="musicClassroomHero" alt="" /></div>
    </section>

    <section class="dashboard-overview-grid">
      <article class="card dashboard-panel current-class-panel">
        <div class="dashboard-panel-heading"><span class="panel-art-icon decoration-chalkboard" :style="{ backgroundImage: `url(${musicDashboardDecorations})` }" aria-hidden="true"></span><h2>当前课堂</h2></div>
        <div v-if="liveSession" class="current-class-body">
          <div class="current-class-summary">
            <span class="classroom-avatar" :style="{ backgroundImage: `url(${musicWorkspaceStickers})` }" aria-hidden="true"></span>
            <span><strong>{{ liveSession.courseTitle || '音乐互动课堂' }}</strong><small>{{ formatDateTime(liveSession.scheduledStartAt || liveSession.startedAt) }}</small></span>
            <span class="status-pill" :class="liveSession.status">{{ statusText(liveSession.status) }}</span>
          </div>
          <div class="current-class-progress">
            <div class="current-class-metric"><small>当前环节</small><strong>{{ currentClassNode?.title || (liveSession.status === 'not_started' ? '等待开始' : '课堂进行中') }}</strong></div>
            <div class="current-class-metric progress-metric"><small>课堂进度</small><strong>{{ unlockedNodeCount }} / {{ liveSession.nodeStates.length }} 环节</strong><span class="class-progress-track"><i :style="{ width: `${classroomProgress}%` }"></i></span></div>
            <RouterLink class="button primary current-class-action" :to="classroomEntryRoute"><PlayCircle :size="17" aria-hidden="true" />{{ classroomActionLabel }}</RouterLink>
          </div>
        </div>
        <RouterLink v-else class="current-class-summary empty" to="/classrooms"><span class="classroom-avatar" :style="{ backgroundImage: `url(${musicWorkspaceStickers})` }" aria-hidden="true"></span><span><strong>还没有进行中的课堂</strong><small>查看课堂安排</small></span><ArrowRight :size="17" aria-hidden="true" /></RouterLink>
      </article>

      <article class="card dashboard-panel continue-panel">
        <div class="dashboard-panel-heading"><span class="panel-art-icon decoration-cards" :style="{ backgroundImage: `url(${musicDashboardDecorations})` }" aria-hidden="true"></span><h2>待办事项</h2><span v-if="continueItems.length">{{ continueItems.length }} 项</span></div>
        <div v-if="loadError" class="dashboard-load-error" data-testid="dashboard-load-error">
          <CircleAlert :size="20" aria-hidden="true" />
          <span>{{ loadError }}</span>
          <button class="button ghost" type="button" data-testid="dashboard-retry" :disabled="loading" @click="loadDashboard"><RefreshCw :size="16" aria-hidden="true" />重试</button>
        </div>
        <div v-else-if="visibleContinueItems.length" class="continue-list">
          <RouterLink v-for="item in visibleContinueItems" :key="item.id" :to="item.to" :data-testid="item.testId">
            <span class="continue-icon"><component :is="item.icon" :size="18" aria-hidden="true" /></span>
            <span><strong>{{ item.count }} {{ item.label }}</strong><small>{{ item.action }}</small></span>
            <ArrowRight :size="18" aria-hidden="true" />
          </RouterLink>
        </div>
        <div v-else class="continue-empty" data-testid="continue-empty"><ClipboardCheck :size="20" aria-hidden="true" /><span>{{ loading ? '正在同步待办…' : '暂时没有待处理事项' }}</span></div>
      </article>

    </section>

    <section class="dashboard-bottom-grid">
      <section class="recent-section card">
        <div class="section-header"><div class="dashboard-panel-heading"><span class="panel-art-icon decoration-tambourine" :style="{ backgroundImage: `url(${musicDashboardDecorations})` }" aria-hidden="true"></span><h2>最近生成</h2><span v-if="packages.length" class="recent-package-count">共 {{ packages.length }} 个</span></div><RouterLink class="text-link" to="/lesson-plans/history">查看全部 <ArrowRight :size="16" aria-hidden="true" /></RouterLink></div>
        <div v-if="recentPackages.length" class="package-list">
          <article v-for="(item, index) in recentPackages" :key="item.id" class="package-list-item">
            <RouterLink class="package-card-content" :to="`/packages/${item.id}`"><span class="package-art" :class="`package-art-${index % 4}`" :style="{ backgroundImage: `url(${musicWorkspaceStickers})` }" aria-hidden="true"></span><span class="package-card-copy"><strong>{{ item.title }}</strong><small>{{ packageLessonPlanLabel(item) }}</small></span></RouterLink>
            <div class="package-card-footer"><span><span class="status-pill">{{ statusText(item.status) }}</span></span><span class="package-card-actions"><RouterLink class="package-detail-action" :to="`/packages/${item.id}`">查看</RouterLink><RouterLink class="package-next-action" :to="packageDestination(item)">{{ packageNextAction(item) }} <ArrowRight :size="15" aria-hidden="true" /></RouterLink></span></div>
          </article>
        </div>
        <div v-else class="empty-inline">{{ loadError ? '暂时无法同步互动包，请重试。' : loading ? '正在同步教学内容…' : '还没有互动包，上传教案后即可开始生成。' }}</div>
      </section>

      <section class="class-management-panel card">
        <div class="section-header"><div class="dashboard-panel-heading"><span class="class-panel-icon"><UsersRound :size="18" aria-hidden="true" /></span><h2>班级管理</h2><span v-if="classes.length" class="recent-package-count">共 {{ classes.length }} 个</span></div><RouterLink class="text-link" to="/classes">查看全部 <ArrowRight :size="16" aria-hidden="true" /></RouterLink></div>
        <div v-if="recentClasses.length" class="dashboard-class-list">
          <RouterLink v-for="item in recentClasses" :key="item.id" :to="`/classes/${item.id}`"><span class="dashboard-class-icon"><UsersRound :size="19" aria-hidden="true" /></span><span><strong>{{ item.className }}</strong><small>{{ item.description || '音乐课堂班级' }}</small></span><span class="dashboard-student-count" data-testid="dashboard-class-student-count">{{ item.studentCount ?? 0 }} 人</span><ArrowRight :size="17" aria-hidden="true" /></RouterLink>
        </div>
        <RouterLink v-else class="class-management-empty" to="/classes"><UsersRound :size="21" aria-hidden="true" /><span>{{ loading ? '正在同步班级…' : '还没有班级，前往创建' }}</span><ArrowRight :size="17" aria-hidden="true" /></RouterLink>
      </section>
    </section>
  </AppShell>
</template>
