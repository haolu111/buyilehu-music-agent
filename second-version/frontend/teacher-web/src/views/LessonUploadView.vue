<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { FileCheck2, FileUp, Sparkles, X } from 'lucide-vue-next'
import AppShell from '../components/AppShell.vue'
import WorkflowStepper from '../components/WorkflowStepper.vue'
import { lessonPlanApi } from '../api/lessonPlanApi'

const router = useRouter()
const route = useRoute()
const title = ref('')
const file = ref<File | null>(null)
const nativeFileInput = ref<HTMLInputElement | null>(null)
const loading = ref(false)
const error = ref('')
const dragging = ref(false)
const acceptedExtensions = ['txt', 'docx', 'pdf']
const fileSize = computed(() => file.value ? `${(file.value.size / 1024 / 1024).toFixed(1)} MB` : '')
const isRetryUpload = computed(() => Boolean(route.query.retryLessonPlanId))

function setFile(value?: File) {
  if (!value) return
  const extension = value.name.split('.').pop()?.toLowerCase()
  if (!extension || !acceptedExtensions.includes(extension)) {
    rejectFile('请选择 DOCX、PDF 或 TXT 格式的教案')
    return
  }
  if (value.size > 20 * 1024 * 1024) {
    rejectFile('文件不能超过 20MB')
    return
  }
  error.value = ''
  file.value = value
  if (!title.value) title.value = value.name.replace(/\.[^.]+$/, '')
}

function clearFile() {
  file.value = null
  title.value = ''
  error.value = ''
  if (nativeFileInput.value) nativeFileInput.value.value = ''
}

function rejectFile(message: string) {
  clearFile()
  error.value = message
}

function onFileChange(event: Event) { setFile((event.target as HTMLInputElement).files?.[0]) }
function onDrop(event: DragEvent) { dragging.value = false; setFile(event.dataTransfer?.files?.[0]) }
async function upload() {
  if (!file.value) {
    error.value = '请先选择教案文件'
    return
  }
  loading.value = true
  error.value = ''
  try {
    const plan = await lessonPlanApi.upload(file.value, title.value)
    await router.push(`/lesson-plans/${plan.id}/parse-result`)
  } catch (e) {
    error.value = e instanceof Error ? e.message : '解析教案失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AppShell>
    <WorkflowStepper current-stage="upload-lesson" />
    <div class="page-heading compact"><div><p class="eyebrow">第一步</p><h1>上传教案</h1><p>上传后，系统会提取课程、目标和教学流程。</p></div></div>
    <div class="upload-layout">
      <section class="card upload-card">
        <p v-if="isRetryUpload" class="retry-upload-context"><Sparkles :size="16" aria-hidden="true" />重新上传教案后将开始新的解析。</p>
        <label class="upload-zone" :class="{ dragging, selected: file }" @dragover.prevent="dragging = true" @dragleave.prevent="dragging = false" @drop.prevent="onDrop">
          <input ref="nativeFileInput" type="file" accept=".txt,.docx,.pdf" @change="onFileChange">
          <FileCheck2 v-if="file" class="upload-icon" :size="27" aria-hidden="true" />
          <FileUp v-else class="upload-icon" :size="27" aria-hidden="true" />
          <template v-if="!file"><strong>选择教案文件</strong><small>也可拖拽到这里 · DOCX、PDF、TXT，最大 20MB</small></template>
          <template v-else><strong>{{ file.name }}</strong><small>{{ fileSize }} · 点击可更换文件</small></template>
        </label>
        <label v-if="file" class="lesson-title-field">教案标题<input v-model="title" name="lesson-title" placeholder="默认使用文件名"></label>
        <div class="button-row upload-actions">
          <button v-if="file" class="button ghost" type="button" @click="clearFile"><X :size="17" aria-hidden="true" />移除文件</button>
          <button class="button primary" type="button" data-testid="lesson-upload-primary" :disabled="loading || !file" @click="upload"><Sparkles :size="17" aria-hidden="true" />{{ loading ? '正在解析…' : '解析教案' }}</button>
        </div>
        <p v-if="error" class="error">{{ error }}</p>
      </section>
      <aside class="card upload-note"><Sparkles :size="23" aria-hidden="true" /><div><strong>解析完成后</strong><p>确认内容，再设置课堂方案。</p></div></aside>
    </div>
  </AppShell>
</template>
