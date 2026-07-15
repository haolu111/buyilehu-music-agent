<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import DynamicActivityHost from '../components/DynamicActivityHost.vue'
import FeedbackToast from '../components/FeedbackToast.vue'
import SceneHeader from '../components/SceneHeader.vue'
import type { ActivityRenderer } from '../types'
import { useStudentStore } from '../stores/studentStore'
import { playErrorSound, playSuccessSound, unlockActivitySound } from '../utils/activitySound'

interface AssessmentResult {
  score?: number | null
  mode?: string
  provider?: string
  model?: string | null
  feedback?: string
  fallbackReason?: string | null
}

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
const runtimeConfig = computed(() => node.value?.runtimeConfig || null)

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

const parsedResult = computed<Record<string, unknown>>(() => {
  const value = submission.value?.resultJson
  if (!value) return {}
  try {
    return JSON.parse(value) as Record<string, unknown>
  } catch {
    return { result: value }
  }
})

function formatResultValue(value: unknown) {
  if (Array.isArray(value)) return value.join('、')
  if (value && typeof value === 'object') {
    return Object.entries(value as Record<string, unknown>).map(([key, item]) => `${key}: ${String(item)}`).join('；')
  }
  return String(value ?? '')
}

const resultFields = computed(() => {
  const labels: Record<string, string> = {
    observed: '完成内容', sequence: '我的顺序', title: '作品名称', notes: '创作内容', choice: '我的选择', evidence: '判断依据',
    explanation: '我的理由', trace: '旋律轨迹', matches: '音色配对', order: '曲式顺序', role: '合奏角色', completedSteps: '排练步骤',
    phrase: '练唱乐句', attempts: '练唱次数', durationSeconds: '录音时长', bpm: '练习速度', result: '活动记录',
  }
  const observed: Record<string, string> = { entry: '课堂准备已完成', meter_experience: '节拍体验已完成', summary: '课堂小结已查看' }
  return Object.entries(parsedResult.value)
    .filter(([key]) => key !== '_assessment')
    .map(([key, item]) => ({
      label: labels[key] || '活动记录',
      value: key === 'observed' ? (observed[String(item)] || '活动已完成') : formatResultValue(item),
    }))
})

const assessment = computed<AssessmentResult | null>(() => {
  const value = parsedResult.value._assessment
  return value && typeof value === 'object' ? value as AssessmentResult : null
})

const assessmentSource = computed(() => {
  const value = assessment.value
  if (!value) return '课堂评分'
  if (value.mode === 'service_fallback' || value.mode === 'ai_fallback') return '临时评分'
  const provider = (value.provider || '').toLowerCase()
  if (provider.includes('ecnu')) return 'ECNU 智能评分'
  if (provider.includes('doubao')) return '豆包智能评分'
  if (value.mode === 'rule') return '系统自动评分'
  if (value.mode === 'completion') return '完成记录'
  if (value.mode === 'ai') return '智能评分'
  return '课堂评分'
})

const fallbackRenderer = computed<ActivityRenderer>(() => {
  if (activityKind.value === 'summary') return 'summary'
  if (activityKind.value === 'creation') return 'creation-panel'
  if (activityKind.value === 'game') return 'rhythm-drag'
  if (activityKind.value === 'tool') return 'meter-compare'
  return 'completion'
})
const activeRenderer = computed(() => runtimeConfig.value?.renderer || fallbackRenderer.value)

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

async function submit(payload: Record<string, unknown>) {
  const wasCompleted = submission.value?.progressStatus === 'completed'
  unlockActivitySound()
  try {
    await store.submitCurrentNode(nodeId.value, payload)
    editing.value = false
    toast.value = wasCompleted ? '结果已更新' : '活动已提交'
    playSuccessSound()
  } catch {
    toast.value = store.error
    playErrorSound()
  }
}

function editResult() {
  editing.value = true
}

async function waitForNextNode() {
  await router.push({
    path: '/classroom/waiting',
    query: { completedNodeId: String(nodeId.value) },
  })
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
        <div class="student-result-grid"><span v-for="field in resultFields" :key="`${field.label}-${field.value}`"><small>{{ field.label }}</small><strong>{{ field.value }}</strong></span></div>
        <div v-if="assessment" class="assessment-panel" :class="{ temporary: assessment.mode === 'service_fallback' || assessment.mode === 'ai_fallback' }">
          <div><small>{{ assessmentSource }}</small><strong v-if="assessment.score != null">{{ assessment.score }} 分</strong><strong v-else>本环节不计分</strong></div>
          <p>{{ assessment.feedback || '结果已记录。' }}</p>
        </div>
        <div v-else-if="submission?.score != null" class="assessment-panel"><div><small>课堂评分</small><strong>{{ submission.score }} 分</strong></div></div>
        <div class="action-row">
          <button class="primary-action" type="button" @click="editResult">修改结果</button>
          <button class="secondary-action" type="button" @click="router.push('/classroom')">返回课堂</button>
          <button class="secondary-action" type="button" @click="waitForNextNode">完成，等待下一环节</button>
        </div>
      </section>

      <template v-else>
        <DynamicActivityHost
          :runtime="runtimeConfig"
          :fallback-renderer="fallbackRenderer"
          :completed-count="completedChallenges"
          :total-count="challengeNodes.length"
          @completed="submit($event.result)"
        />

        <div v-if="activeRenderer === 'meter-compare' || activeRenderer === 'summary' || activeRenderer === 'completion'" class="action-row">
          <button class="secondary-action" type="button" @click="router.push('/classroom')">返回课堂</button>
          <button
            class="primary-action"
            type="button"
            @click="submit({ observed: rawNodeType || activityKind })"
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
