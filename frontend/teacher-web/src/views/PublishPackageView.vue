<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppShell from '../components/AppShell.vue'
import { packageApi } from '../api/packageApi'

const route = useRoute()
const router = useRouter()
const packageId = Number(route.params.packageId)
const classId = ref('')
const loading = ref(false)
const message = ref('当前后端尚未实现发布接口，本页已预留 POST /api/v1/packages/{packageId}/publish 调用。')
const error = ref('')

async function publish() {
  loading.value = true
  error.value = ''
  try {
    await packageApi.publishPackage(packageId, Number(classId.value))
    message.value = '发布成功'
    await router.push('/classroom/1/control')
  } catch (err) {
    error.value = err instanceof Error ? err.message : '发布失败，等待后端发布模块实现'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AppShell>
    <h1>发布到班级</h1>
    <div class="card stack">
      <p class="muted">{{ message }}</p>
      <label>班级 ID<input v-model="classId" placeholder="例如：1" /></label>
      <button class="primary" :disabled="loading" @click="publish">发布</button>
      <p v-if="error" class="error">{{ error }}</p>
      <RouterLink class="button" to="/classroom/1/control">先进入课堂控制占位页</RouterLink>
    </div>
  </AppShell>
</template>
