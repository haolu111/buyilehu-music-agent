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
const editing = ref(false)
const nodeId = computed(() => Number(route.params.nodeId))
const node = computed(() =>
  store.currentSession?.nodeStates.find((item) => (item.activityNodeId || item.id) === nodeId.value) || null,
)
const submission = computed(() => store.getSubmission(nodeId.value))
const rawNodeType = computed(() => node.value?.nodeType || '')

const activityKind = computed(() => {
  const type = rawNodeType.value.toLowerCase()
  if (type.includes('summary')) return 'summary'
  if (type.includes('creation')) return 'creation'
  if (type.includes('rhythm')) return 'game'
  if (type.includes('meter') || type === 'entry' || type === 'tool') return 'tool'
  return 'unknown'
})

const showResult = computed(() => Boolean(submission.value) && !editing.value)

const activityStatus = computed(() => {
  switch (activityKind.value) {
    case 'tool':
      return '节拍工具'
    case 'game':
      return '节奏游戏'
    case 'creation':
      return '创编课堂'
    case 'summary':
      return '课堂总结'
    default:
      return '课堂活动'
  }
})

const subtitle = computed(() => {
  if (!node.value) return '正在同步课堂信息'
  return `节点 ${node.value.sortOrder || ''}`.trim()
})

const formattedResult = computed(() => {
  const value = submission.value?.resultJson
  if (!value) return '暂无提交内容'
  try {
    return JSON.stringify(JSON.parse(value), null, 2)
  } catch {
    return value
  }
})

async function ensureSession() {
  try {
    if (!store.currentSession) {
      await store.refreshCurrentClassroom()
    } else {
      await store.loadSubmissions(store.currentSession.id)
    }
    if (!store.currentSession || store.currentSession.status === 'ended') {
      toast.value = '课堂已结束或不可用'
      await router.push('/home')
      return
    }
    if (!node.value) {
      toast.value = '当前没有可用的课堂活动，请先返回课堂入口'
    }
  } catch {
    toast.value = store.error
  }
}

async function submit(payload: Record<string, unknown>, score?: number) {
  try {
    await store.submitCurrentNode(nodeId.value, payload, score)
    editing.value = false
    toast.value = submission.value ? '结果已更新' : '已提交'
  } catch {
    toast.value = store.error
  }
}

function editResult() {
  editing.value = true
}

async function exitClassroom() {
  store.exitCurrentClassroom()
  await router.push('/home')
}

onMounted(ensureSession)
</script>

<template>
  <main class="page-shell activity-shell">
    <SceneHeader :title="node?.title || '课堂活动'" :subtitle="subtitle" :status="activityStatus" />

    <section v-if="node" class="activity-content">
      <section v-if="showResult" class="tool-panel">
        <h2>我的提交结果</h2>
        <p class="muted">状态：{{ submission?.progressStatus }} / 分数：{{ submission?.score ?? '-' }}</p>
        <pre style="white-space: pre-wrap;">{{ formattedResult }}</pre>
        <div class="action-row">
          <button class="secondary-action" type="button" @click="router.push('/classroom')">返回课堂</button>
          <button class="secondary-action" type="button" @click="exitClassroom">退出课堂</button>
          <button class="primary-action" type="button" @click="editResult">修改结果</button>
        </div>
      </section>

      <template v-else>
        <MeterCompareTool v-if="activityKind === 'tool'" />
        <RhythmDragGame
          v-else-if="activityKind === 'game'"
          @completed="submit({ sequence: $event.sequence }, $event.score)"
        />
        <CreationPanel v-else-if="activityKind === 'creation'" @submitted="submit($event, 100)" />
        <SummaryPage
          v-else-if="activityKind === 'summary'"
          :completed-count="store.submissions.filter((item) => item.progressStatus === 'completed').length"
          :total-count="store.currentSession?.nodeStates.length || 0"
        />
        <section v-else class="tool-panel">
          <p>当前活动类型暂未接入专用组件，完成后可以直接提交。</p>
          <button class="primary-action" type="button" @click="submit({ observed: rawNodeType || 'unknown' }, 100)">
            完成并提交
          </button>
        </section>

        <div v-if="activityKind === 'tool' || activityKind === 'summary' || activityKind === 'unknown'" class="action-row">
          <button class="secondary-action" type="button" @click="router.push('/classroom')">返回课堂</button>
          <button
            class="primary-action"
            type="button"
            @click="submit({ observed: rawNodeType || activityKind }, 100)"
          >
            {{ submission ? '重新提交' : '完成' }}
          </button>
        </div>
      </template>
    </section>

    <section v-else class="empty-state">
      <p>当前没有找到对应的课堂活动。</p>
      <button class="secondary-action" type="button" @click="router.push('/classroom')">返回课堂入口</button>
    </section>

    <FeedbackToast :message="toast" />
  </main>
</template>