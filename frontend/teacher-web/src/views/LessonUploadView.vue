<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { CheckCircle2, FileCheck2, FileUp, Sparkles, X, XCircle } from 'lucide-vue-next'
import AppShell from '../components/AppShell.vue'
import WorkflowStepper from '../components/WorkflowStepper.vue'
import { lessonPlanApi } from '../api/lessonPlanApi'

type UploadStatus = 'pending' | 'uploading' | 'success' | 'failed'
type UploadItem = {
  key: string
  file: File
  title: string
  status: UploadStatus
  lessonPlanId?: number
  error?: string
}

const router = useRouter()
const route = useRoute()
const items = ref<UploadItem[]>([])
const nativeFileInput = ref<HTMLInputElement | null>(null)
const loading = ref(false)
const error = ref('')
const dragging = ref(false)
const acceptedExtensions = ['txt', 'docx', 'pdf']
const isRetryUpload = computed(() => Boolean(route.query.retryLessonPlanId))
const isBatch = computed(() => items.value.length > 1)
const successCount = computed(() => items.value.filter((item) => item.status === 'success').length)
const failedCount = computed(() => items.value.filter((item) => item.status === 'failed').length)
const totalSize = computed(() => {
  const bytes = items.value.reduce((sum, item) => sum + item.file.size, 0)
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
})

function validateFile(file: File) {
  const extension = file.name.split('.').pop()?.toLowerCase()
  if (!extension || !acceptedExtensions.includes(extension)) return '请选择 DOCX、PDF 或 TXT 格式的教案'
  if (file.size > 20 * 1024 * 1024) return '文件不能超过 20MB'
  return ''
}

function addFiles(files?: FileList | File[]) {
  if (!files?.length) return
  error.value = ''
  const additions: UploadItem[] = []
  const errors: string[] = []
  Array.from(files).forEach((file) => {
    const validation = validateFile(file)
    if (validation) {
      errors.push(`${file.name}：${validation}`)
      return
    }
    const key = `${file.name}-${file.size}-${file.lastModified}`
    if (items.value.some((item) => item.key === key) || additions.some((item) => item.key === key)) return
    additions.push({
      key,
      file,
      title: file.name.replace(/\.[^.]+$/, ''),
      status: 'pending',
    })
  })
  items.value.push(...additions)
  if (errors.length) error.value = errors.join('；')
  if (nativeFileInput.value) nativeFileInput.value.value = ''
}

function removeItem(key: string) {
  if (loading.value) return
  items.value = items.value.filter((item) => item.key !== key)
  error.value = ''
}

function clearFiles() {
  if (loading.value) return
  items.value = []
  error.value = ''
  if (nativeFileInput.value) nativeFileInput.value.value = ''
}

function onFileChange(event: Event) {
  addFiles((event.target as HTMLInputElement).files || undefined)
}

function onDrop(event: DragEvent) {
  dragging.value = false
  addFiles(event.dataTransfer?.files)
}

async function upload() {
  if (!items.value.length) {
    error.value = '请先选择教案文件'
    return
  }
  loading.value = true
  error.value = ''
  for (const item of items.value) {
    if (item.status === 'success') continue
    item.status = 'uploading'
    item.error = ''
    try {
      const plan = await lessonPlanApi.upload(item.file, item.title)
      item.status = 'success'
      item.lessonPlanId = plan.id
    } catch (e) {
      item.status = 'failed'
      item.error = e instanceof Error ? e.message : '解析教案失败'
    }
  }
  loading.value = false
  if (items.value.length === 1 && successCount.value === 1) {
    await router.push(`/lesson-plans/${items.value[0].lessonPlanId}/parse-result`)
  }
}

function statusText(status: UploadStatus) {
  return { pending: '等待上传', uploading: '正在解析', success: '解析成功', failed: '解析失败' }[status]
}
</script>

<template>
  <AppShell>
    <WorkflowStepper current-stage="upload-lesson" />
    <div class="page-heading compact">
      <div>
        <p class="eyebrow">第一步</p>
        <h1>上传教案</h1>
        <p>可以一次选择多份教案，系统会逐份提取课程、目标和教学流程。</p>
      </div>
    </div>
    <div class="upload-layout">
      <section class="card upload-card">
        <p v-if="isRetryUpload" class="retry-upload-context">
          <Sparkles :size="16" aria-hidden="true" />重新上传教案后将开始新的解析。
        </p>
        <label class="upload-zone" :class="{ dragging, selected: items.length }"
          @dragover.prevent="dragging = true" @dragleave.prevent="dragging = false" @drop.prevent="onDrop">
          <input ref="nativeFileInput" type="file" accept=".txt,.docx,.pdf" multiple @change="onFileChange">
          <FileCheck2 v-if="items.length" class="upload-icon" :size="27" aria-hidden="true" />
          <FileUp v-else class="upload-icon" :size="27" aria-hidden="true" />
          <template v-if="!items.length">
            <strong>选择一份或多份教案</strong>
            <small>也可将多个文件拖到这里 · DOCX、PDF、TXT · 单个文件最大 20MB</small>
          </template>
          <template v-else>
            <strong>已选择 {{ items.length }} 份教案</strong>
            <small>共 {{ totalSize }} · 点击可继续添加文件</small>
          </template>
        </label>

        <div v-if="items.length" class="upload-file-list">
          <article v-for="item in items" :key="item.key" class="upload-file-item" :data-status="item.status">
            <FileCheck2 :size="20" aria-hidden="true" />
            <div class="upload-file-main">
              <strong>{{ item.file.name }}</strong>
              <input v-model="item.title" :name="items.length === 1 ? 'lesson-title' : undefined"
                aria-label="教案标题" :disabled="loading" placeholder="教案标题">
              <small v-if="item.error" class="error">{{ item.error }}</small>
            </div>
            <span class="upload-file-status">
              <CheckCircle2 v-if="item.status === 'success'" :size="17" />
              <XCircle v-else-if="item.status === 'failed'" :size="17" />
              {{ statusText(item.status) }}
            </span>
            <button class="icon-button" type="button" aria-label="移除文件"
              :disabled="loading" @click="removeItem(item.key)"><X :size="17" /></button>
          </article>
        </div>

        <div class="button-row upload-actions">
          <button v-if="items.length" class="button ghost" type="button" :disabled="loading" @click="clearFiles">
            <X :size="17" aria-hidden="true" />移除全部
          </button>
          <button class="button primary" type="button" data-testid="lesson-upload-primary"
            :disabled="loading || !items.length" @click="upload">
            <Sparkles :size="17" aria-hidden="true" />
            {{ loading ? `正在解析 ${successCount + failedCount + 1}/${items.length}…` : (isBatch ? `批量解析 ${items.length} 份教案` : '解析教案') }}
          </button>
          <RouterLink v-if="isBatch && successCount" class="button" to="/lesson-plans/history">
            查看已上传教案（{{ successCount }}）
          </RouterLink>
        </div>
        <p v-if="error" class="error">{{ error }}</p>
        <p v-if="isBatch && !loading && (successCount || failedCount)" class="upload-summary">
          批量处理完成：成功 {{ successCount }} 份，失败 {{ failedCount }} 份。
          <span v-if="failedCount">修正失败项后可再次点击批量解析。</span>
        </p>
      </section>
      <aside class="card upload-note">
        <Sparkles :size="23" aria-hidden="true" />
        <div><strong>批量上传说明</strong><p>文件将按列表顺序逐份解析。完成后可到“我的教案”统一确认内容。</p></div>
      </aside>
    </div>
  </AppShell>
</template>
