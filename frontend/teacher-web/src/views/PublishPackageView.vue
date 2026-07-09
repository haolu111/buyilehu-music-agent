<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppShell from '../components/AppShell.vue'
import { packageApi } from '../api/packageApi'
import { classApi } from '../api/classApi'
import type { PackageInfo, PackageVersion, ClassInfo } from '../types'

const route = useRoute()
const router = useRouter()
const packageId = Number(route.params.packageId)

const packageInfo = ref<PackageInfo | null>(null)
const classes = ref<ClassInfo[]>([])
const versions = ref<PackageVersion[]>([])
const classId = ref('')
const versionId = ref('')
const reviewEnabled = ref(false)
const loading = ref(false)
const error = ref('')
const message = ref('选择班级和版本后即可发布。')

const canPublish = computed(() => Boolean(classId.value && versionId.value))

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

    if (!classId.value && mineClasses.length > 0) {
      classId.value = String(mineClasses[0].id)
    }

    const defaultVersionId = pkg.currentVersionId || versionList[0]?.id
    if (!versionId.value && defaultVersionId) {
      versionId.value = String(defaultVersionId)
    }
  } catch (exception) {
    error.value = exception instanceof Error ? exception.message : '加载发布页失败'
  } finally {
    loading.value = false
  }
}

async function publish() {
  if (!classId.value) {
    error.value = '请先选择班级'
    return
  }
  loading.value = true
  error.value = ''
  try {
    await packageApi.publishPackage(
      packageId,
      Number(classId.value),
      Number(versionId.value),
      reviewEnabled.value,
    )
    message.value = '发布成功，班级已可使用该互动包。'
    await router.push(`/packages/${packageId}`)
  } catch (exception) {
    error.value = exception instanceof Error ? exception.message : '发布失败'
  } finally {
    loading.value = false
  }
}

function describeClass(item: ClassInfo) {
  return `#${item.id} · ${item.className}`
}

function describeVersion(item: PackageVersion) {
  return `版本 ${item.versionNo} · ID ${item.id}`
}

onMounted(loadData)
</script>

<template>
  <AppShell>
    <div class="section-header">
      <div>
        <h1>发布到班级</h1>
        <p class="muted">这里会把互动包发布到指定班级，并绑定一个具体版本。版本不填时会优先使用当前版本。</p>
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
          班级
          <select v-model="classId">
            <option value="">请选择班级</option>
            <option v-for="item in classes" :key="item.id" :value="String(item.id)">
              {{ describeClass(item) }}
            </option>
          </select>
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
      </div>

      <label class="inline-control">
        <input v-model="reviewEnabled" type="checkbox" />
        开启发布后复盘
      </label>

      <div class="button-row">
        <button class="primary" :disabled="loading || !canPublish" @click="publish">
          {{ loading ? '发布中...' : '发布' }}
        </button>
        <button class="button" type="button" @click="loadData">刷新数据</button>
      </div>
    </section>
  </AppShell>
</template>
