<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AppShell from '../components/AppShell.vue'
import { lessonPlanApi } from '../api/lessonPlanApi'

const router = useRouter()
const title = ref('')
const file = ref<File | null>(null)
const loading = ref(false)
const error = ref('')

function onFileChange(event: Event) {
  file.value = (event.target as HTMLInputElement).files?.[0] || null
}

async function upload() {
  if (!file.value) {
    error.value = '请先选择 docx 或 txt 文件'
    return
  }
  loading.value = true
  error.value = ''
  try {
    const lessonPlan = await lessonPlanApi.upload(file.value, title.value)
    await router.push(`/lesson-plans/${lessonPlan.id}/parse-result`)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '上传失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AppShell>
    <h1>上传教案</h1>
    <div class="card stack">
      <label>教案标题<input v-model="title" placeholder="可选，默认使用文件名" /></label>
      <label>教案文件<input type="file" accept=".txt,.docx" @change="onFileChange" /></label>
      <button class="primary" :disabled="loading" @click="upload">{{ loading ? '上传解析中...' : '上传并解析' }}</button>
      <p v-if="error" class="error">{{ error }}</p>
    </div>
  </AppShell>
</template>
