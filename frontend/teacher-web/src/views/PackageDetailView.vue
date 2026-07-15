<script setup lang="ts">
import { ArrowLeft, Eye, Pencil, Send } from 'lucide-vue-next'
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import AppShell from '../components/AppShell.vue'
import LessonWorkspaceNav from '../components/LessonWorkspaceNav.vue'
import { packageApi } from '../api/packageApi'
import type { PackageInfo } from '../types'
import { statusText } from '../utils/display'

const route = useRoute()
const packageId = Number(route.params.packageId)
const packageInfo = ref<PackageInfo | null>(null)
const packages = ref<PackageInfo[]>([])
const error = ref('')

onMounted(async () => {
  try {
    packageInfo.value = await packageApi.getPackage(packageId)
    packages.value = await packageApi.listPackages()
  } catch (exception) {
    error.value = exception instanceof Error ? exception.message : '加载互动包失败'
  }
})
</script>

<template>
  <AppShell>
    <LessonWorkspaceNav />
    <div class="page-heading compact">
      <div><p class="eyebrow">教案与互动包</p><h1>互动包详情</h1><p>查看当前版本，并继续确认、编辑或发布课堂。</p></div>
      <RouterLink class="button" to="/lesson-plans/history"><ArrowLeft :size="17" aria-hidden="true" />返回内容列表</RouterLink>
    </div>
    <p v-if="error" class="error">{{ error }}</p>
    <section v-if="packageInfo" class="card package-detail-summary">
      <div class="section-header compact">
        <div><span class="status-pill" :class="packageInfo.status">{{ statusText(packageInfo.status) }}</span><h2>{{ packageInfo.title }}</h2><p class="muted">{{ packageInfo.description || '课堂互动活动包' }}</p></div>
        <span class="tag">版本 {{ packageInfo.currentVersionId || '—' }}</span>
      </div>
      <div class="package-detail-actions">
        <RouterLink class="button" :to="`/packages/${packageId}/proposal`"><Eye :size="17" aria-hidden="true" />查看方案</RouterLink>
        <RouterLink class="button primary-soft" :to="`/packages/${packageId}/edit`"><Pencil :size="17" aria-hidden="true" />编辑互动包</RouterLink>
        <RouterLink class="button primary" :to="`/packages/${packageId}/publish`"><Send :size="17" aria-hidden="true" />发布到班级</RouterLink>
      </div>
    </section>

    <section class="card package-library-panel" style="margin-top: 18px;">
      <div class="section-header compact"><div><h3>最近互动包</h3><p class="muted">快速切换到其他已生成内容</p></div></div>
      <RouterLink v-for="item in packages" :key="item.id" class="list-line" :to="`/packages/${item.id}`">
        <span><strong>{{ item.title }}</strong><small class="muted">{{ item.description || '课堂互动活动包' }}</small></span><span class="status-pill" :class="item.status">{{ statusText(item.status) }}</span>
      </RouterLink>
    </section>
  </AppShell>
</template>
