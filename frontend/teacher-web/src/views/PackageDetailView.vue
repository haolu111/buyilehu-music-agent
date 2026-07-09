<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import AppShell from '../components/AppShell.vue'
import { packageApi } from '../api/packageApi'
import type { PackageInfo } from '../types'

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
    <h1>互动包详情</h1>
    <p v-if="error" class="error">{{ error }}</p>
    <section v-if="packageInfo" class="card">
      <h2>{{ packageInfo.title }}</h2>
      <p>{{ packageInfo.description }}</p>
      <p class="muted">状态：{{ packageInfo.status }} / 当前版本 ID：{{ packageInfo.currentVersionId || '-' }}</p>
      <div class="button-row">
        <RouterLink class="button" :to="`/packages/${packageId}/proposal`">查看方案卡</RouterLink>
        <RouterLink class="button" :to="`/packages/${packageId}/edit`">编辑互动包</RouterLink>
        <RouterLink class="button primary" :to="`/packages/${packageId}/publish`">发布到班级</RouterLink>
      </div>
    </section>

    <section class="card" style="margin-top: 18px;">
      <h3>我的互动包</h3>
      <RouterLink v-for="item in packages" :key="item.id" class="list-line" :to="`/packages/${item.id}`">
        {{ item.title }} <span class="muted">{{ item.status }}</span>
      </RouterLink>
    </section>
  </AppShell>
</template>
