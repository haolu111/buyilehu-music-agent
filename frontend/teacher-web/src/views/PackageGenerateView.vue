<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppShell from '../components/AppShell.vue'
import LessonWorkspaceNav from '../components/LessonWorkspaceNav.vue'
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

async function handleStatus(status: GenerationJob) {
  job.value = status
  if (status.status === 'failed') {
    loading.value = false
    error.value = status.errorMessage || '生成失败，请稍后重试'
    statusSubscription?.abort()
  } else if (status.status === 'success' && status.packageId) {
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
    error.value = caught instanceof Error ? caught.message : '生成失败'
  }
}

onMounted(async () => {
  try {
    plans.value = (await lessonPlanApi.listMine()).filter((item) => item.parseStatus === 'success')
  } catch {
    error.value = '无法加载教案列表'
  }
})

onUnmounted(() => statusSubscription?.abort())
</script>
<template><AppShell><LessonWorkspaceNav /><div class="page-heading compact"><div><h1>生成互动包</h1><p>选择教案并微调课堂参数，系统将先生成活动方案供你确认。</p></div></div>
  <section class="card generation-form"><label class="full-field">选择教案<select v-model="lessonPlanId"><option value="" disabled>请选择已解析的教案</option><option v-for="plan in plans" :key="plan.id" :value="String(plan.id)">{{ plan.title }} · 解析成功</option></select></label>
    <div class="settings-grid"><label>课堂时长<select v-model="duration"><option value="30">30 分钟</option><option value="40">40 分钟</option><option value="45">45 分钟</option></select></label><label>使用方式<select v-model="mode"><option value="individual">学生个人设备</option><option value="group">小组共用设备</option><option value="teacher">教师大屏演示</option></select></label><label>活动密度<select v-model="density"><option value="light">精简</option><option value="standard">标准</option><option value="rich">丰富</option></select></label><label>难度<select v-model="difficulty"><option value="grade">按年级默认</option><option value="easy">适当降低</option><option value="hard">增加挑战</option></select></label><label>课堂流程<select v-model="flow"><option value="teacher">教师逐步解锁</option><option value="auto">学生自动进入</option></select></label><label>视觉情境<select v-model="theme"><option value="auto">系统推荐</option><option value="stage">音乐舞台</option><option value="nature">自然乐园</option></select></label></div>
    <div class="generation-note"><span>♫</span><p><strong>先确认方案，再生成互动包</strong><br>你可以在方案卡中调整顺序、活动类型和难度。</p></div>
    <div v-if="job && loading" class="generation-progress" role="status" aria-live="polite">
      <div><strong>{{ job.message || '任务正在处理中' }}</strong><span>{{ job.progress || 0 }}%</span></div>
      <div class="generation-progress-track"><i :style="{ width: `${job.progress || 0}%` }"></i></div>
    </div>
    <div class="button-row end"><button class="button primary" :disabled="loading||!lessonPlanId" @click="generate">{{ loading?'正在生成方案…':'生成活动方案' }}</button></div><p v-if="error" class="error">{{ error }}</p>
  </section>
</AppShell></template>
