<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
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
let timer = 0
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

const showResult = computed(() => submission.value?.progressStatus === 'completed' && !editing.value)

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

const resultFields = computed(() => {
  const value = submission.value?.resultJson
  if (!value) return []
  try {
    const parsed = JSON.parse(value) as Record<string, unknown>
    const labels: Record<string, string> = { observed: '完成内容', sequence: '我的节奏', title: '作品名称', notes: '创作灵感' }
    const observed: Record<string, string> = { entry: '课堂准备已完成', meter_experience: '节拍体验已完成', summary: '课堂小结已查看' }
    return Object.entries(parsed).map(([key, item]) => ({ label: labels[key] || '活动记录', value: key === 'observed' ? (observed[String(item)] || '活动已完成') : Array.isArray(item) ? item.join('、') : String(item) }))
  } catch {
    return [{ label: '活动记录', value }]
  }
})

const challengeNodes = computed(() => store.currentSession?.nodeStates.filter(item => {
  const type = item.nodeType.toLowerCase()
  return !type.includes('entry') && type !== 'entry' && !type.includes('summary')
}) || [])
const completedChallenges = computed(() => challengeNodes.value.filter(item => store.getSubmission(item.activityNodeId || item.id)?.progressStatus === 'completed').length)

async function ensureSession() {
  try {
    if (!store.currentSession) {
      await store.refreshCurrentClassroom()
    } else {
      await store.loadSubmissions(store.currentSession.id)
    }
    if (!store.currentSession || store.currentSession.status === 'ended') {
      toast.value = '课堂已结束或不可用'
      await router.push('/classroom')
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
  const wasCompleted = submission.value?.progressStatus === 'completed'
  try {
    await store.submitCurrentNode(nodeId.value, payload, score)
    editing.value = false
    toast.value = wasCompleted ? '结果已更新' : '活动已提交'
  } catch {
    toast.value = store.error
  }
}

function editResult() {
  editing.value = true
}

async function syncClassroom() {
  try {
    await store.refreshCurrentClassroom()
    if (store.currentSession?.status === 'ended') await router.push('/classroom')
  } catch {
    toast.value = '课堂连接中断，正在自动重连…'
  }
}

onMounted(() => { ensureSession(); timer = window.setInterval(syncClassroom, 3000) })
onBeforeUnmount(() => window.clearInterval(timer))
</script>

<template>
  <main class="page-shell activity-shell">
    <SceneHeader :title="node?.title || '课堂活动'" :subtitle="subtitle" :status="store.currentSession?.status === 'paused' ? '老师已暂停' : activityStatus" />

    <section v-if="node" class="activity-content">
      <section v-if="showResult" class="tool-panel">
        <div class="submission-success"><span>✓</span><div><h2>活动已提交</h2><p>做得很好！结果已经保存，等待老师开启下一环节。</p></div></div>
        <div class="student-result-grid"><span v-for="field in resultFields" :key="`${field.label}-${field.value}`"><small>{{ field.label }}</small><strong>{{ field.value }}</strong></span><span v-if="submission?.score != null"><small>本次得分</small><strong>{{ submission.score }} 分</strong></span></div>
        <div class="action-row">
          <button class="primary-action" type="button" @click="editResult">修改结果</button>
          <button class="secondary-action" type="button" @click="router.push('/classroom/waiting')">完成，等待下一环节</button>
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
          :completed-count="completedChallenges"
          :total-count="challengeNodes.length"
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
    <div v-if="store.currentSession?.status === 'paused'" class="activity-paused-overlay"><div><span>Ⅱ</span><h2>老师暂停了当前活动</h2><p>请先停下来，课堂恢复后页面会自动更新。</p></div></div>
  </main>
</template>
