<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import AppShell from '../components/AppShell.vue'
import LessonWorkspaceNav from '../components/LessonWorkspaceNav.vue'
import { lessonPlanApi } from '../api/lessonPlanApi'
const router = useRouter(), title = ref(''), file = ref<File|null>(null), loading = ref(false), error = ref(''), dragging = ref(false)
const fileSize = computed(() => file.value ? `${(file.value.size / 1024 / 1024).toFixed(1)} MB` : '')
function setFile(value?: File) { if (!value) return; if (value.size > 20 * 1024 * 1024) { error.value = '文件不能超过 20MB'; return } file.value = value; if (!title.value) title.value = value.name.replace(/\.[^.]+$/, '') }
function onFileChange(event: Event) { setFile((event.target as HTMLInputElement).files?.[0]) }
function onDrop(event: DragEvent) { dragging.value = false; setFile(event.dataTransfer?.files?.[0]) }
async function upload() { if (!file.value) return error.value = '请先选择教案文件'; loading.value = true; error.value=''; try { const plan = await lessonPlanApi.upload(file.value,title.value); await router.push(`/lesson-plans/${plan.id}/parse-result`) } catch(e) { error.value=e instanceof Error?e.message:'上传失败' } finally { loading.value=false } }
</script>
<template><AppShell><LessonWorkspaceNav /><div class="page-heading compact"><div><h1>上传教案</h1><p>系统将识别课程信息、教学目标和流程，并生成可确认的活动方案。</p></div></div>
  <div class="upload-layout"><section class="card upload-card"><label>教案标题<input v-model="title" placeholder="默认使用文件名"></label>
    <label class="upload-zone" :class="{ dragging, selected:file }" @dragover.prevent="dragging=true" @dragleave.prevent="dragging=false" @drop.prevent="onDrop"><input type="file" accept=".txt,.docx,.pdf" @change="onFileChange"><span class="upload-icon">↑</span><template v-if="!file"><strong>拖拽教案到这里，或点击选择文件</strong><small>支持 DOCX、PDF、TXT，单个文件不超过 20MB</small></template><template v-else><strong>{{ file.name }}</strong><small>{{ fileSize }} · 点击可更换文件</small></template></label>
    <div class="button-row"><button v-if="file" class="button" type="button" @click="file=null">移除文件</button><button class="button primary" :disabled="loading||!file" @click="upload">{{ loading?'正在上传并解析…':'上传并开始解析' }}</button></div><p v-if="error" class="error">{{ error }}</p></section>
    <aside class="card result-preview"><p class="eyebrow">解析后你将获得</p><ol><li><span>1</span><div><strong>课程信息</strong><small>年级、课题与课堂时长</small></div></li><li><span>2</span><div><strong>教学流程</strong><small>自动拆分导入、体验与总结</small></div></li><li><span>3</span><div><strong>活动方案卡</strong><small>确认后再生成正式互动包</small></div></li></ol></aside>
  </div>
</AppShell></template>
