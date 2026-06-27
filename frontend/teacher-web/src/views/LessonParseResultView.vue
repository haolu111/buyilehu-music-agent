<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import AppShell from '../components/AppShell.vue'
import { lessonPlanApi } from '../api/lessonPlanApi'
import type { LessonPlan } from '../types'

const route = useRoute()
const lessonPlanId = Number(route.params.lessonPlanId)
const lessonPlan = ref<LessonPlan | null>(null)
const error = ref('')

const parsed = computed(() => {
  if (!lessonPlan.value?.parsedJson) return null
  try {
    return JSON.parse(lessonPlan.value.parsedJson)
  } catch {
    return null
  }
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
    <h1>教案解析结果</h1>
    <p v-if="error" class="error">{{ error }}</p>
    <div v-if="lessonPlan" class="grid two">
      <section class="card">
        <h3>{{ lessonPlan.title }}</h3>
        <p class="muted">解析状态：{{ lessonPlan.parseStatus }}</p>
        <pre>{{ parsed || lessonPlan.parsedJson }}</pre>
      </section>
      <section class="card">
        <h3>原文预览</h3>
        <pre>{{ lessonPlan.rawText }}</pre>
      </section>
    </div>
    <RouterLink class="button primary" :to="`/packages/generate?lessonPlanId=${lessonPlanId}`">创建生成任务</RouterLink>
  </AppShell>
</template>
