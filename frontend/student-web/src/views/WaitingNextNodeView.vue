<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SceneHeader from '../components/SceneHeader.vue'
import FeedbackToast from '../components/FeedbackToast.vue'
import { useStudentStore } from '../stores/studentStore'

const router = useRouter()
const route = useRoute()
const store = useStudentStore()
const toast = ref('')
const connected = ref(navigator.onLine)
const completedNodeId = computed(() => {
  const value = Number(route.query.completedNodeId)
  return Number.isFinite(value) && value > 0 ? value : null
})
let timer = 0

const completedNodeIds = computed(() => new Set(
  store.submissions
    .filter((item) => item.progressStatus === 'completed')
    .map((item) => item.nodeId),
))
const completedCount = computed(() => completedNodeIds.value.size)
const totalCount = computed(() => store.currentSession?.nodeStates.length || 0)
const teacherCurrentNode = computed(() => {
  const session = store.currentSession
  if (!session?.currentNodeId) return null
  return session.nodeStates.find((node) => (node.activityNodeId || node.id) === session.currentNodeId) || null
})
const nextNode = computed(() => {
  const nodes = store.currentSession?.nodeStates || []
  const isAvailable = (node: typeof nodes[number]) => {
    const id = node.activityNodeId || node.id
    return node.status === 'unlocked'
      && id !== completedNodeId.value
      && !completedNodeIds.value.has(id)
  }
  if (teacherCurrentNode.value && isAvailable(teacherCurrentNode.value)) {
    return teacherCurrentNode.value
  }
  return nodes.find(isAvailable) || null
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
      <div class="waiting-progress">
        <span>课堂进度</span>
        <strong>{{ completedCount }} / {{ totalCount }}</strong>
        <div><i :style="{ width: `${totalCount ? completedCount / totalCount * 100 : 0}%` }"></i></div>
      </div>
      <p class="teacher-current-node">
        老师当前开启：<strong>{{ teacherCurrentNode?.title || '等待老师开启下一环节' }}</strong>
      </p>
    </section>
    <button class="secondary-action" type="button" @click="router.push('/classroom')">返回课堂</button>
    <FeedbackToast :message="toast" tone="warning" />
  </main>
</template>
