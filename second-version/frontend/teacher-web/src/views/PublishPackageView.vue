<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppShell from '../components/AppShell.vue'
import WorkflowStepper from '../components/WorkflowStepper.vue'
import { packageApi } from '../api/packageApi'
import { classApi } from '../api/classApi'
import type { PackageInfo, PackageVersion, ClassInfo } from '../types'

const route = useRoute()
const router = useRouter()
const packageId = Number(route.params.packageId)

const packageInfo = ref<PackageInfo | null>(null)
const classes = ref<ClassInfo[]>([])
const versions = ref<PackageVersion[]>([])
const selectedClassIds = ref<number[]>([])
const versionId = ref('')
const courseTitle = ref('')
const courseDescription = ref('')
const scheduledStartAt = ref('')
const reviewEnabled = ref(false)
const loading = ref(false)
const error = ref('')
const message = ref('选择班级和版本后即可创建课堂。创建后课堂默认未开始，需要到课堂管理中点击开始课堂。')

const canPublish = computed(() => selectedClassIds.value.length > 0 && Boolean(versionId.value))

async function loadData() {
  loading.value = true
  error.value = ''
  try {
    const [pkg, mineClasses, versionList] = await Promise.all([
      packageApi.getPackage(packageId),
      classApi.listClasses(),
      packageApi.listVersions(packageId),
    ])
    packageInfo.value = pkg
    classes.value = mineClasses
    versions.value = versionList
    courseTitle.value = courseTitle.value || pkg.title

    if (selectedClassIds.value.length === 0 && mineClasses.length > 0) {
      selectedClassIds.value = [mineClasses[0].id]
    }

    const defaultVersionId = pkg.currentVersionId || versionList[0]?.id
    if (!versionId.value && defaultVersionId) {
      versionId.value = String(defaultVersionId)
    }
  } catch (exception) {
    error.value = exception instanceof Error ? exception.message : '加载创建页面失败'
  } finally {
    loading.value = false
  }
}

async function publish() {
  if (!canPublish.value) {
    error.value = '请先选择班级和版本'
    return
  }
  loading.value = true
  error.value = ''
  try {
    await packageApi.publishPackage(packageId, {
      classIds: selectedClassIds.value,
      versionId: Number(versionId.value),
      courseTitle: courseTitle.value,
      courseDescription: courseDescription.value,
      scheduledStartAt: scheduledStartAt.value || undefined,
      startImmediately: false,
      reviewEnabled: reviewEnabled.value,
    })
    message.value = '课堂已创建，当前未开始。请到课堂管理中点击开始课堂，系统会自动解锁第一个环节。'
    await router.push('/classrooms')
  } catch (exception) {
    error.value = exception instanceof Error ? exception.message : '创建课堂失败'
  } finally {
    loading.value = false
  }
}

function describeVersion(item: PackageVersion) {
  return `版本 ${item.versionNo} / ID ${item.id}`
}

onMounted(loadData)
</script>

<template>
  <AppShell>
    <WorkflowStepper current-stage="publish-classroom" :package-id="packageId" />
    <div class="section-header">
      <div>
        <p class="eyebrow">第 6 步 · 发布课堂</p>
        <h1>创建课堂</h1>
        <p class="muted">选择一个或多个授课班级，设置课堂信息后创建课堂。每个班级会生成独立课堂进度。</p>
      </div>
      <RouterLink class="button" :to="`/packages/${packageId}`">返回互动包详情</RouterLink>
    </div>

    <p v-if="error" class="error">{{ error }}</p>

    <section v-if="packageInfo" class="card stack">
      <div class="list-line">
        <div>
          <strong>{{ packageInfo.title }}</strong>
          <p class="muted">{{ packageInfo.description || '暂无简介' }}</p>
        </div>
        <span class="tag">当前版本 ID：{{ packageInfo.currentVersionId || '-' }}</span>
      </div>

      <p class="muted">{{ message }}</p>

      <div class="grid two">
        <label>
          课堂标题
          <input v-model.trim="courseTitle" placeholder="例如：三拍子律动体验课" />
        </label>
        <label>
          计划开始时间
          <input v-model="scheduledStartAt" type="datetime-local" />
        </label>
      </div>

      <label>
        课程简介
        <textarea v-model.trim="courseDescription" rows="3" placeholder="给学生和教师看的课堂说明"></textarea>
      </label>

      <label>
        版本
        <select v-model="versionId">
          <option value="">请选择版本</option>
          <option v-for="item in versions" :key="item.id" :value="String(item.id)">
            {{ describeVersion(item) }}
          </option>
        </select>
      </label>

      <section class="stack">
        <h3>授课班级</h3>
        <label v-for="item in classes" :key="item.id" class="inline-control">
          <input v-model="selectedClassIds" type="checkbox" :value="item.id" />
          #{{ item.id }} {{ item.className }}
          <span class="muted">{{ item.description }}</span>
        </label>
      </section>

      <label class="inline-control">
        <input v-model="reviewEnabled" type="checkbox" />
        开启发布后复盘
      </label>

      <div class="button-row">
        <button class="primary" :disabled="loading || !canPublish" @click="publish">
          {{ loading ? '创建中...' : '创建课堂' }}
        </button>
        <button class="button" type="button" @click="loadData">刷新数据</button>
      </div>
    </section>
  </AppShell>
</template>
