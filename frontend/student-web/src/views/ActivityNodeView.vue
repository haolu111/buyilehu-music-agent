<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import CreationPanel from '../components/CreationPanel.vue'
import FeedbackToast from '../components/FeedbackToast.vue'
import MeterCompareTool from '../components/MeterCompareTool.vue'
import RhythmDragGame from '../components/RhythmDragGame.vue'
import SceneHeader from '../components/SceneHeader.vue'
import SummaryPage from '../components/SummaryPage.vue'
import { useStudentStore } from '../stores/studentStore'

const route = useRoute()
const router = useRouter()
const store = useStudentStore()
const toast = ref('')
const nodeId = computed(() => Number(route.params.nodeId))
const node = computed(() =>
  store.currentSession?.nodeStates.find((item) => (item.activityNodeId || item.id) === nodeId.value) || null,
)
const nodeType = computed(() => node.value?.nodeType || 'tool')

async function ensureSession() {
  if (!store.currentSession) {
    await store.refreshCurrentClassroom()
  }
}

async function submit(payload: Record<string, unknown>, score?: number) {
  await store.submitCurrentNode(nodeId.value, payload, score)
  toast.value = '已提交'
  await router.push('/classroom/waiting')
}

onMounted(ensureSession)
</script>

<template>
  <main class="page-shell activity-shell">
    <SceneHeader :title="node?.title || '课堂活动'" :subtitle="`节点 ${node?.sortOrder || ''}`" :status="nodeType" />

    <MeterCompareTool v-if="nodeType === 'tool' || nodeType === 'entry'" />
    <RhythmDragGame v-else-if="nodeType === 'game'" @completed="submit({ sequence: $event.sequence }, $event.score)" />
    <CreationPanel v-else-if="nodeType === 'creation'" @submitted="submit($event, 100)" />
    <SummaryPage
      v-else
      :completed-count="store.currentSession?.nodeStates.filter((item) => item.status === 'unlocked').length || 0"
      :total-count="store.currentSession?.nodeStates.length || 0"
    />

    <div v-if="nodeType === 'tool' || nodeType === 'entry'" class="action-row">
      <button class="secondary-action" type="button" @click="router.push('/classroom')">返回</button>
      <button class="primary-action" type="button" @click="submit({ observed: nodeType }, 100)">完成</button>
    </div>

    <FeedbackToast :message="toast" />
  </main>
</template>
