<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import SceneHeader from '../components/SceneHeader.vue'
import FeedbackToast from '../components/FeedbackToast.vue'
import SummaryPage from '../components/SummaryPage.vue'
import { useStudentStore } from '../stores/studentStore'

const router = useRouter()
const store = useStudentStore()
const toast = ref('')
let timer = 0

const unlockedNode = computed(() => store.currentNode || store.firstUnlockedNode)
const completedCount = computed(() =>
  store.currentSession?.nodeStates.filter((node) => node.status === 'unlocked').length || 0,
)
const totalCount = computed(() => store.currentSession?.nodeStates.length || 0)

async function poll() {
  try {
    await store.refreshCurrentClassroom()
  } catch {
    toast.value = store.error
  }
}

async function enterNode() {
  const node = unlockedNode.value
  if (!node) return
  const nodeId = node.activityNodeId || node.id
  await store.enterCurrentNode(nodeId)
  await router.push(`/classroom/nodes/${nodeId}`)
}

onMounted(() => {
  poll()
  timer = window.setInterval(poll, 3000)
})

onBeforeUnmount(() => window.clearInterval(timer))
</script>

<template>
  <main class="page-shell">
    <SceneHeader title="课堂入口" subtitle="跟随老师解锁活动" :status="store.currentSession?.status || 'Session'" />

    <section v-if="store.currentSession" class="classroom-board">
      <div class="node-map">
        <button
          v-for="node in store.currentSession.nodeStates"
          :key="node.activityNodeId || node.id"
          type="button"
          class="node-pill"
          :class="{ unlocked: node.status === 'unlocked', current: (node.activityNodeId || node.id) === store.currentSession.currentNodeId }"
          :disabled="node.status !== 'unlocked'"
          @click="router.push(`/classroom/nodes/${node.activityNodeId || node.id}`)"
        >
          <span>{{ node.sortOrder }}</span>
          {{ node.title }}
        </button>
      </div>

      <button class="primary-action wide" type="button" :disabled="!unlockedNode" @click="enterNode">
        {{ unlockedNode ? '进入当前活动' : '等待解锁' }}
      </button>

      <SummaryPage :completed-count="completedCount" :total-count="totalCount" />
    </section>

    <section v-else class="empty-state">
      <p>暂无课堂</p>
      <button class="secondary-action" type="button" @click="router.push('/home')">返回首页</button>
    </section>

    <FeedbackToast :message="toast" tone="warning" />
  </main>
</template>
