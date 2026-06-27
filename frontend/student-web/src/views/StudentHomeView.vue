<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import SceneHeader from '../components/SceneHeader.vue'
import FeedbackToast from '../components/FeedbackToast.vue'
import { useStudentStore } from '../stores/studentStore'

const store = useStudentStore()
const router = useRouter()
const toast = ref('')

async function refresh() {
  try {
    await store.refreshCurrentClassroom()
  } catch {
    toast.value = store.error
  }
}

onMounted(refresh)
</script>

<template>
  <main class="page-shell">
    <SceneHeader
      title="我的课堂"
      :subtitle="store.profile?.displayName || store.profile?.username || '学生'"
      status="Home"
    />

    <section class="home-grid">
      <article class="action-card">
        <h2>班级</h2>
        <p>{{ store.currentClass?.className || '暂无班级' }}</p>
        <button class="secondary-action" type="button" @click="router.push('/join-class')">加入班级</button>
      </article>

      <article class="action-card">
        <h2>当前课堂</h2>
        <p>{{ store.currentSession ? `状态：${store.currentSession.status}` : '暂无进行中的课堂' }}</p>
        <button
          class="primary-action"
          type="button"
          :disabled="!store.currentSession"
          @click="router.push('/classroom')"
        >
          进入课堂
        </button>
      </article>
    </section>

    <section class="timeline-strip" aria-label="课堂流程">
      <span>登录</span>
      <span>入班</span>
      <span>进课堂</span>
      <span>做活动</span>
      <span>等解锁</span>
    </section>

    <FeedbackToast :message="toast" tone="warning" />
  </main>
</template>
