<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import SceneHeader from '../components/SceneHeader.vue'
import FeedbackToast from '../components/FeedbackToast.vue'
import { useStudentStore } from '../stores/studentStore'

const router = useRouter()
const store = useStudentStore()
const toast = ref('')
const connected = ref(navigator.onLine)
const lastNodeId = ref<number | null>(store.currentSession?.currentNodeId || null)
let timer = 0

const nextNode = computed(() => {
  const nodes = store.currentSession?.nodeStates || []
  return nodes.find((node) => node.status === 'unlocked' && (node.activityNodeId || node.id) !== lastNodeId.value)
})

async function poll() {
  try {
    await store.refreshCurrentClassroom()
    connected.value = true
    if (store.currentSession?.status === 'ended') {
      await router.push('/classroom')
      return
    }
    if (nextNode.value) {
      const id = nextNode.value.activityNodeId || nextNode.value.id
      await router.push(`/classroom/nodes/${id}`)
    }
  } catch {
    connected.value = false
    toast.value = '课堂连接中断，正在自动重连…'
  }
}

onMounted(() => {
  poll()
  timer = window.setInterval(poll, 3000)
})

onBeforeUnmount(() => window.clearInterval(timer))
</script>

<template>
  <main class="page-shell waiting-shell">
    <SceneHeader title="等待下一环节" subtitle="老师解锁后会自动进入，无需刷新" :status="connected ? '已连接课堂' : '正在重新连接'" />
    <section class="pulse-stage" aria-live="polite">
      <div class="pulse-bars" aria-hidden="true">
        <span></span><span></span><span></span><span></span>
      </div>
      <h2>{{ store.currentSession?.status === 'paused' ? '老师暂停了课堂' : '当前活动已完成！' }}</h2>
      <p>{{ store.currentSession?.status === 'paused' ? '请先休息一下，恢复后会自动更新。' : '老师正在准备下一环节，开启后将自动进入。' }}</p>
    </section>
    <button class="secondary-action" type="button" @click="router.push('/classroom')">查看课堂</button>
    <FeedbackToast :message="toast" tone="warning" />
  </main>
</template>
