<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { Clock3, FileText, Settings2, Sparkles, UsersRound } from 'lucide-vue-next'
import { useRoute, useRouter } from 'vue-router'
import AppShell from '../components/AppShell.vue'
import LessonWorkspaceNav from '../components/LessonWorkspaceNav.vue'
import WorkflowStepper from '../components/WorkflowStepper.vue'
import { packageApi } from '../api/packageApi'
import { lessonPlanApi } from '../api/lessonPlanApi'
import type { GenerationJob, LessonPlanSummary } from '../types'

const route = useRoute()
const router = useRouter()
const plans = ref<LessonPlanSummary[]>([])
const lessonPlanId = ref(String(route.query.lessonPlanId || ''))
const loading = ref(false)
const error = ref('')
const job = ref<GenerationJob | null>(null)
const duration = ref('40')
const mode = ref('individual')
const density = ref('standard')
const difficulty = ref('grade')
const flow = ref('teacher')
const theme = ref('auto')
let statusSubscription: AbortController | null = null

const generationProgress = computed(() => Math.max(0, Math.min(100, Number(job.value?.progress || 0))))
const generationPhase = computed(() => {
  if (job.value?.message) return job.value.message
  const progress = generationProgress.value
  if (progress < 35) return '教学设计 Agent 正在生成活动结构'
  if (progress < 50) return '正在匹配一一对应的活动组件'
  if (progress < 75) return 'LangGraph 正在构建素材并执行教学质量审计'
  if (progress < 85) return '正在执行结构与业务校验'
  if (progress < 95) return '正在生成正式共享活动组件'
  return '正在保存活动包和审核报告'
})
const generationSteps = computed(() => {
  const progress = generationProgress.value
  return [
    { key: 'design', label: '教学设计', detail: '生成活动结构', start: 10, done: 35 },
    { key: 'matching', label: '组件匹配', detail: '建立活动与组件一一映射', start: 40, done: 50 },
    { key: 'materials', label: '活动构建', detail: '构建音乐素材与运行参数', start: 55, done: 75 },
    { key: 'audit', label: '质量审计', detail: '质量 Agent 与业务规则校验', start: 78, done: 85 },
    { key: 'persist', label: '保存发布', detail: '保存共享配置与审核报告', start: 88, done: 100 },
  ].map((step) => ({
    ...step,
    state: progress >= step.done ? 'done' : progress >= step.start ? 'active' : 'waiting',
  }))
})

async function handleStatus(status: GenerationJob) {
  job.value = status
  if (status.status === 'failed') {
    loading.value = false
    const detail = status.errorMessage || ''
    error.value = detail.includes('timed out')
      ? '教学设计服务响应超时。本次任务已停止，请重新生成；系统会在审计模型超时时自动使用规则审计。'
      : detail || '生成失败，请稍后重试'
    statusSubscription?.abort()
  } else if (status.packageId) {
    loading.value = false
    statusSubscription?.abort()
    await router.push(`/packages/${status.packageId}/proposal`)
  }
}

async function generate() {
  if (!lessonPlanId.value) {
    error.value = '请选择一份已解析的教案'
    return
  }
  statusSubscription?.abort()
  loading.value = true
  error.value = ''
  job.value = null
  try {
    const created = await packageApi.createGenerationJob(Number(lessonPlanId.value), {
      duration: Number(duration.value),
      mode: mode.value,
      density: density.value,
      difficulty: difficulty.value,
      flow: flow.value,
      theme: theme.value,
    })
    await handleStatus(created)
    if (created.status !== 'success' && created.status !== 'failed') {
      statusSubscription = packageApi.watchGenerationJob(created.id, handleStatus, (subscriptionError) => {
        error.value = subscriptionError.message
      })
    }
  } catch (caught) {
    loading.value = false
    error.value = caught instanceof Error ? caught.message : '生成失败，请重试'
  }
}

onMounted(async () => {
  try {
    plans.value = (await lessonPlanApi.listMine()).filter((item) => item.parseStatus === 'success')
  } catch {
    error.value = '无法加载教案列表，请重试'
  }
})

onUnmounted(() => statusSubscription?.abort())
</script>

<template>
  <AppShell>
    <LessonWorkspaceNav />
    <WorkflowStepper current-stage="setup-classroom" :lesson-plan-id="lessonPlanId" />

    <header class="page-heading compact">
      <div>
        <p class="eyebrow">第 3 步 · 设置课堂</p>
        <h1>设置课堂</h1>
        <p>确认这节课如何开展，再生成活动方案。</p>
      </div>
    </header>

    <section class="card generation-form" :aria-busy="loading">
      <label class="full-field field-with-icon">
        <span><FileText :size="18" aria-hidden="true" /> 选用教案</span>
        <select v-model="lessonPlanId" name="lesson-plan">
          <option value="" disabled>请选择已解析的教案</option>
          <option v-for="plan in plans" :key="plan.id" :value="String(plan.id)">{{ plan.title }} · 已解析</option>
        </select>
      </label>

      <div class="settings-grid essentials-grid">
        <label class="field-with-icon"><span><Clock3 :size="18" aria-hidden="true" /> 课堂时长</span><select v-model="duration"><option value="30">30 分钟</option><option value="40">40 分钟</option><option value="45">45 分钟</option></select></label>
        <label class="field-with-icon"><span><UsersRound :size="18" aria-hidden="true" /> 使用方式</span><select v-model="mode"><option value="individual">学生个人设备</option><option value="group">小组共用设备</option><option value="teacher">教师大屏演示</option></select></label>
      </div>

      <details class="generation-advanced" data-testid="advanced-generation-settings">
        <summary><Settings2 :size="18" aria-hidden="true" /> 更多设置</summary>
        <div class="settings-grid">
          <label>活动密度<select v-model="density"><option value="light">精简</option><option value="standard">标准</option><option value="rich">丰富</option></select></label>
          <label>难度<select v-model="difficulty"><option value="grade">按年级默认</option><option value="easy">适当降低</option><option value="hard">增加挑战</option></select></label>
          <label>课堂流程<select v-model="flow"><option value="teacher">教师逐步解锁</option><option value="auto">学生自动进入</option></select></label>
          <label>视觉情境<select v-model="theme"><option value="auto">系统推荐</option><option value="stage">音乐舞台</option><option value="nature">自然乐园</option></select></label>
        </div>
      </details>

      <p v-if="error" class="error" role="alert">{{ error }}</p>
      <section v-if="loading && job" class="generation-progress" aria-live="polite">
        <div><strong>{{ generationPhase }}</strong><span>{{ generationProgress }}%</span></div>
        <progress :value="generationProgress" max="100">{{ generationProgress }}%</progress>
        <ol class="generation-timeline" aria-label="生成步骤">
          <li v-for="step in generationSteps" :key="step.key" :class="`is-${step.state}`">
            <i aria-hidden="true">{{ step.state === 'done' ? '✓' : step.state === 'active' ? '●' : '' }}</i>
            <span><strong>{{ step.label }}</strong><small>{{ step.detail }}</small></span>
            <em>{{ step.state === 'done' ? '已完成' : step.state === 'active' ? '进行中' : '等待中' }}</em>
          </li>
        </ol>
        <small>生成任务已在后台运行，页面状态会实时更新。</small>
      </section>
      <div class="button-row end">
        <button class="button primary" data-testid="generate-package" :disabled="loading || !lessonPlanId" @click="generate">
          <Sparkles :size="18" aria-hidden="true" /> {{ loading ? '正在生成方案…' : '生成活动方案' }}
        </button>
      </div>
    </section>
  </AppShell>
</template>
