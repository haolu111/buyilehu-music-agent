<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import FeedbackToast from '../components/FeedbackToast.vue'
import SummaryPage from '../components/SummaryPage.vue'
import { useStudentStore } from '../stores/studentStore'
import type { ActivityNode } from '../types'

const router = useRouter()
const store = useStudentStore()
const toast = ref('')
const connected = ref(navigator.onLine)
const soundReady = ref(false)
const microphoneState = ref<'idle' | 'checking' | 'ready' | 'denied'>('idle')
const showExitConfirm = ref(false)
let timer = 0

const studentName = computed(() => store.profile?.user?.realName || store.profile?.user?.username || '小小音乐家')
const className = computed(() => store.currentClass?.className || '我的班级')
const allNodes = computed(() => store.currentSession?.nodeStates || [])
const isFlowNode = (node?: ActivityNode | null) => {
  if (!node) return false
  const type = node.nodeType.toLowerCase()
  return type === 'entry' || type.includes('entry') || type.includes('summary')
}
const challengeNodes = computed(() => allNodes.value.filter(node => !isFlowNode(node)))
const completedNodeIds = computed(() => new Set(store.submissions.filter(item => item.progressStatus === 'completed').map(item => item.nodeId)))
const completedChallenges = computed(() => challengeNodes.value.filter(node => completedNodeIds.value.has(node.activityNodeId || node.id)).length)
const starCount = computed(() => completedChallenges.value * 3)
const currentTask = computed(() => {
  const current = store.currentNode
  if (current && current.status === 'unlocked' && !completedNodeIds.value.has(current.activityNodeId || current.id)) return current
  return allNodes.value.find(node => node.status === 'unlocked' && !completedNodeIds.value.has(node.activityNodeId || node.id)) || null
})
const classroomFinished = computed(() => store.currentSession?.status === 'ended' || (challengeNodes.value.length > 0 && completedChallenges.value === challengeNodes.value.length))

function activityDescription(node?: ActivityNode | null) {
  const type = node?.nodeType.toLowerCase() || ''
  if (type.includes('entry')) return '检查声音与设备，准备进入今天的音乐课堂。'
  if (type.includes('meter')) return '听一听、拍一拍，感受不同拍号的强弱规律。'
  if (type.includes('rhythm')) return '组合节奏卡片，完成属于你的节奏挑战。'
  if (type.includes('creation')) return '把灵感变成音乐，创作自己的节奏作品。'
  if (type.includes('summary')) return '回顾今天的课堂，看看收获了哪些音乐能力。'
  return '跟随老师完成这一环节的音乐任务。'
}
function activityMinutes(node?: ActivityNode | null) { return isFlowNode(node) ? 1 : node?.nodeType.toLowerCase().includes('creation') ? 8 : 5 }
function nodeStatus(node: ActivityNode) {
  const id = node.activityNodeId || node.id
  const submission = store.getSubmission(id)
  if (completedNodeIds.value.has(id)) return 'completed'
  if (store.currentSession?.status === 'paused' && node.status === 'unlocked') return 'paused'
  if (currentTask.value && id === (currentTask.value.activityNodeId || currentTask.value.id)) return 'current'
  if (submission) return 'submitted'
  return node.status === 'unlocked' ? 'available' : 'locked'
}
function statusLabel(node: ActivityNode) {
  const labels = { completed: '已完成', submitted: '已提交，等待老师', paused: '老师已暂停', current: '现在进行', available: '可以开始', locked: '尚未开启' }
  return labels[nodeStatus(node)]
}

async function poll() {
  try { await store.refreshCurrentClassroom(); connected.value = true }
  catch { connected.value = false; toast.value = '课堂连接中断，正在自动重连…' }
}
async function enterNode(node = currentTask.value) {
  if (!node || store.currentSession?.status === 'paused' || store.currentSession?.status === 'ended') return
  const id = node.activityNodeId || node.id
  await store.enterCurrentNode(id)
  await router.push(`/classroom/nodes/${id}`)
}
function playTestTone() {
  const context = new AudioContext()
  const oscillator = context.createOscillator()
  const gain = context.createGain()
  oscillator.frequency.value = 523.25
  gain.gain.setValueAtTime(0.12, context.currentTime)
  gain.gain.exponentialRampToValueAtTime(0.001, context.currentTime + 0.7)
  oscillator.connect(gain); gain.connect(context.destination); oscillator.start(); oscillator.stop(context.currentTime + 0.7)
  oscillator.onended = () => context.close()
  soundReady.value = true
}
async function checkMicrophone() {
  microphoneState.value = 'checking'
  try { const stream = await navigator.mediaDevices.getUserMedia({ audio: true }); stream.getTracks().forEach(track => track.stop()); microphoneState.value = 'ready' }
  catch { microphoneState.value = 'denied' }
}
function updateOnline() { connected.value = navigator.onLine }
async function exitClassroom() { store.exitCurrentClassroom(); showExitConfirm.value = false; await router.push('/home') }

onMounted(() => { poll(); timer = window.setInterval(poll, 3000); window.addEventListener('online', updateOnline); window.addEventListener('offline', updateOnline) })
onBeforeUnmount(() => { window.clearInterval(timer); window.removeEventListener('online', updateOnline); window.removeEventListener('offline', updateOnline) })
</script>

<template>
  <main class="classroom-page">
    <header class="classroom-topbar">
      <div><p>{{ className }} · 授课老师</p><h1>{{ store.currentSession?.courseTitle || '音乐闯关岛' }}</h1></div>
      <div class="live-status" :class="{ offline: !connected }"><span></span>{{ connected ? '已连接课堂' : '正在重新连接' }}</div>
      <details class="classroom-student-menu"><summary><span>{{ studentName.slice(0, 1) }}</span><strong>{{ studentName }}</strong></summary><div><button @click="router.push('/home')">个人信息</button><button @click="playTestTone">声音测试</button><button class="exit-link" @click="showExitConfirm = true">退出课堂</button></div></details>
    </header>

    <section v-if="store.currentSession" class="classroom-main-content">
      <div class="classroom-overview">
        <div><span>课堂流程 {{ allNodes.length }} 个环节</span><strong>互动挑战 {{ completedChallenges }} / {{ challengeNodes.length }}</strong></div>
        <div class="lesson-stars"><span>★</span><strong>{{ starCount }}</strong><small>本节星星</small></div>
      </div>

      <section v-if="classroomFinished" class="class-complete-panel">
        <SummaryPage :completed-count="completedChallenges" :total-count="challengeNodes.length" />
      </section>
      <template v-else>
        <section class="current-task-card" :class="{ paused: store.currentSession.status === 'paused' }">
          <div class="task-copy"><p class="task-label">{{ store.currentSession.status === 'paused' ? '课堂暂停' : '当前任务' }}</p><h2>{{ currentTask?.title || '等待老师开启下一环节' }}</h2><p>{{ currentTask ? activityDescription(currentTask) : '老师开启后页面会自动更新，无需刷新。' }}</p><div v-if="currentTask" class="task-meta"><span>约 {{ activityMinutes(currentTask) }} 分钟</span><span v-if="!isFlowNode(currentTask)">完成可得 3 颗星</span></div></div>
          <div class="task-action"><button v-if="currentTask && store.currentSession.status !== 'paused'" class="primary-action" @click="enterNode()">{{ store.getSubmission(currentTask.activityNodeId || currentTask.id) ? '继续挑战' : (isFlowNode(currentTask) ? '进入课堂' : '开始挑战') }} →</button><div v-else class="waiting-badge"><i></i>{{ store.currentSession.status === 'paused' ? '老师已暂停活动' : '等待老师开启…' }}</div></div>
        </section>

        <section v-if="currentTask && isFlowNode(currentTask)" class="device-check-card">
          <div><p class="task-label">课堂准备</p><h2>设备检查</h2></div><div class="device-items"><span class="ready">✓ 网络连接{{ connected ? '正常' : '重连中' }}</span><span :class="{ ready: soundReady }">{{ soundReady ? '✓' : '○' }} 声音{{ soundReady ? '播放正常' : '尚未测试' }}</span><span :class="{ ready: microphoneState === 'ready' }">{{ microphoneState === 'ready' ? '✓' : '○' }} 麦克风{{ microphoneState === 'ready' ? '可用' : microphoneState === 'denied' ? '未授权' : '尚未检测' }}</span></div><div class="device-actions"><button class="secondary-action" @click="playTestTone">播放测试音</button><button class="secondary-action" :disabled="microphoneState === 'checking'" @click="checkMicrophone">{{ microphoneState === 'checking' ? '检测中…' : '检测麦克风' }}</button></div>
        </section>

        <section class="lesson-path"><div class="section-title"><div><p class="task-label">课堂路线</p><h2>今天的音乐环节</h2></div><span>教师逐步开启</span></div><ol><li v-for="node in allNodes" :key="node.activityNodeId || node.id" :class="nodeStatus(node)"><span class="path-marker">{{ nodeStatus(node) === 'completed' ? '✓' : nodeStatus(node) === 'locked' ? '锁' : node.sortOrder }}</span><div><small>{{ isFlowNode(node) ? '课堂环节' : `互动挑战 · 约 ${activityMinutes(node)} 分钟` }}</small><strong>{{ node.title }}</strong><p>{{ nodeStatus(node) === 'locked' ? '完成前面的环节后，由老师开启' : statusLabel(node) }}<template v-if="nodeStatus(node) === 'completed' && !isFlowNode(node)"> · 获得 3 颗星</template></p></div><button v-if="['current','available'].includes(nodeStatus(node))" @click="enterNode(node)">进入</button><button v-else-if="nodeStatus(node) === 'completed'" @click="router.push(`/classroom/nodes/${node.activityNodeId || node.id}`)">查看</button></li></ol></section>
      </template>
    </section>

    <section v-else class="empty-state classroom-empty"><div class="empty-note">♪</div><h2>课堂还在准备中</h2><p>老师开课后会自动显示今天的音乐任务。</p><button class="secondary-action" @click="router.push('/home')">返回音乐岛</button></section>

    <footer v-if="store.currentSession && !classroomFinished" class="classroom-action-dock"><span><i :class="{ offline: !connected }"></i>{{ currentTask ? `当前：${currentTask.title}` : '等待老师开启下一环节' }}</span><button v-if="currentTask && store.currentSession.status !== 'paused'" class="primary-action" @click="enterNode()">{{ store.getSubmission(currentTask.activityNodeId || currentTask.id) ? '继续挑战' : '进入挑战' }}</button><strong v-else>{{ store.currentSession.status === 'paused' ? '课堂已暂停' : '自动同步中…' }}</strong></footer>

    <div v-if="showExitConfirm" class="student-modal" @click.self="showExitConfirm = false"><section role="dialog" aria-modal="true"><h2>确定退出课堂吗？</h2><p>退出后本节课堂将从首页隐藏，未提交的活动内容可能会丢失。</p><div><button class="secondary-action" @click="showExitConfirm = false">继续上课</button><button class="danger-action" @click="exitClassroom">确认退出</button></div></section></div>
    <FeedbackToast :message="toast" tone="warning" />
  </main>
</template>
