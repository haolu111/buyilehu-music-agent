<script setup lang="ts">
import { onMounted, ref } from 'vue'
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

async function generate() {
  if (!lessonPlanId.value) {
    error.value = '请选择一份已解析的教案'
    return
  }
  loading.value = true
  error.value = ''
  try {
    job.value = await packageApi.createGenerationJob(Number(lessonPlanId.value), {
      duration: Number(duration.value), mode: mode.value, density: density.value,
      difficulty: difficulty.value, flow: flow.value, theme: theme.value,
    })
    if (job.value.packageId) await router.push(`/packages/${job.value.packageId}/proposal`)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '生成失败，请重试'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    plans.value = (await lessonPlanApi.listMine()).filter((item) => item.parseStatus === 'success')
  } catch {
    error.value = '无法加载教案列表，请重试'
  }
})
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
      <div class="button-row end">
        <button class="button primary" data-testid="generate-package" :disabled="loading || !lessonPlanId" @click="generate">
          <Sparkles :size="18" aria-hidden="true" /> {{ loading ? '正在生成方案…' : '生成活动方案' }}
        </button>
      </div>
    </section>
  </AppShell>
</template>
