<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import FeedbackToast from '../components/FeedbackToast.vue'
import SceneHeader from '../components/SceneHeader.vue'
import { useStudentStore } from '../stores/studentStore'

const store = useStudentStore()
const router = useRouter()
const inviteCode = ref('')
const toast = ref('')

async function join() {
  try {
    const classInfo = await store.join(inviteCode.value)
    toast.value = `已加入班级：${classInfo.className}（#${classInfo.id}）`
    await router.push('/home')
  } catch {
    toast.value = store.error
  }
}
</script>

<template>
  <main class="page-shell narrow">
    <SceneHeader title="加入班级" subtitle="输入老师提供的邀请码" status="Class" />
    <form class="form-stack" @submit.prevent="join">
      <label>
        邀请码
        <input v-model.trim="inviteCode" maxlength="16" required />
      </label>
      <button class="primary-action" type="submit" :disabled="store.loading">
        {{ store.loading ? '加入中...' : '加入班级' }}
      </button>
    </form>
    <FeedbackToast :message="toast" :tone="store.error ? 'error' : 'success'" />
  </main>
</template>
