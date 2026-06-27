<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import SceneHeader from '../components/SceneHeader.vue'
import FeedbackToast from '../components/FeedbackToast.vue'
import { useStudentStore } from '../stores/studentStore'

const router = useRouter()
const store = useStudentStore()
const toast = ref('')
const lastNodeId = ref<number | null>(store.currentSession?.currentNodeId || null)
let timer = 0

const nextNode = computed(() => {
  const nodes = store.currentSession?.nodeStates || []
  return nodes.find((node) => node.status === 'unlocked' && (node.activityNodeId || node.id) !== lastNodeId.value)
})

async function poll() {
  try {
    await store.refreshCurrentClassroom()
    if (nextNode.value) {
      const id = nextNode.value.activityNodeId || nextNode.value.id
      await router.push(`/classroom/nodes/${id}`)
    }
  } catch {
    toast.value = store.error
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
    <SceneHeader title="等待下一环节" subtitle="老师解锁后会自动进入" status="Waiting" />
    <section class="pulse-stage" aria-live="polite">
      <div class="pulse-bars" aria-hidden="true">
        <span></span><span></span><span></span><span></span>
      </div>
      <p>{{ store.currentSession?.status === 'paused' ? '课堂暂停' : '同步课堂中' }}</p>
    </section>
    <button class="secondary-action" type="button" @click="router.push('/classroom')">查看课堂</button>
    <FeedbackToast :message="toast" tone="warning" />
  </main>
</template>
