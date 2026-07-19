<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import AppShell from '../components/AppShell.vue'
import WorkflowStepper from '../components/WorkflowStepper.vue'
import { lessonPlanApi } from '../api/lessonPlanApi'
import type { LessonPlan } from '../types'
import { presentLessonPlan } from '../utils/lessonPlanPresentation'
import { RAW_PREVIEW_MAX_LENGTH, createTextPreview } from '../utils/textPreview'

const route = useRoute()
const lessonPlanId = Number(route.params.lessonPlanId)
const lessonPlan = ref<LessonPlan | null>(null)
const error = ref('')

const presentation = computed(() => lessonPlan.value ? presentLessonPlan(lessonPlan.value) : null)
const parsedJsonPreview = computed(() => createTextPreview(lessonPlan.value?.parsedJson))
const rawTextPreview = computed(() => createTextPreview(lessonPlan.value?.rawText))
const hasRecognizedDetails = computed(() => {
  const summary = presentation.value
  return Boolean(summary && (summary.grade || summary.objectives.length || summary.keyPoints.length || summary.process.length || summary.musicElements.length))
})

onMounted(async () => {
  try {
    lessonPlan.value = await lessonPlanApi.getLessonPlan(lessonPlanId)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载解析结果失败'
  }
})
</script>

<template>
  <AppShell>
    <WorkflowStepper current-stage="confirm-content" :lesson-plan-id="lessonPlanId" />
    <div class="page-heading compact">
      <div><h1>确认教案内容</h1><p>核对系统识别出的教学重点，再进入课堂设置。</p></div>
    </div>
    <p v-if="error" class="error">{{ error }}</p>
    <template v-if="lessonPlan && presentation">
      <div class="grid two parse-summary-grid">
        <section class="card">
          <p class="eyebrow">已识别的课程信息</p>
          <h2>{{ presentation.courseName }}</h2>
          <dl class="lesson-summary-list">
            <div><dt>年级</dt><dd>{{ presentation.grade || '未识别' }}</dd></div>
            <div><dt>音乐要素</dt><dd><span v-if="presentation.musicElements.length">{{ presentation.musicElements.join('、') }}</span><span v-else>未识别</span></dd></div>
          </dl>
          <p v-if="!hasRecognizedDetails" class="muted">暂未识别出可确认的细节，可直接设置课堂后补充调整。</p>
        </section>
        <section class="card">
          <h2>教学目标与重点</h2>
          <div class="lesson-summary-section"><h3>教学目标</h3><ul v-if="presentation.objectives.length"><li v-for="objective in presentation.objectives" :key="objective">{{ objective }}</li></ul><p v-else class="muted">未识别</p></div>
          <div class="lesson-summary-section"><h3>教学重点</h3><ul v-if="presentation.keyPoints.length"><li v-for="point in presentation.keyPoints" :key="point">{{ point }}</li></ul><p v-else class="muted">未识别</p></div>
        </section>
      </div>
      <section class="card">
        <h2>课堂流程</h2>
        <ol v-if="presentation.process.length" class="lesson-process-list"><li v-for="item in presentation.process" :key="`${item.title}-${item.duration}`"><strong>{{ item.title }}</strong><span>{{ item.duration }}</span></li></ol>
        <p v-else class="muted">未识别课堂流程。</p>
      </section>
      <div class="stack parse-raw-details">
        <details v-if="lessonPlan.parsedJson" class="card"><summary>查看原始解析数据</summary><pre>{{ parsedJsonPreview.content }}</pre><p v-if="parsedJsonPreview.truncated" class="muted parse-preview-truncated">内容已截断，仅显示前 {{ RAW_PREVIEW_MAX_LENGTH }} 个字符。</p></details>
        <details v-if="lessonPlan.rawText" class="card"><summary>查看教案原文</summary><pre>{{ rawTextPreview.content }}</pre><p v-if="rawTextPreview.truncated" class="muted parse-preview-truncated">内容已截断，仅显示前 {{ RAW_PREVIEW_MAX_LENGTH }} 个字符。</p></details>
      </div>
      <div class="button-row"><RouterLink class="button primary" :to="`/packages/generate?lessonPlanId=${lessonPlanId}`">内容无误，设置课堂</RouterLink></div>
    </template>
  </AppShell>
</template>
