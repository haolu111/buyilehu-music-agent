<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import SceneHeader from '../components/SceneHeader.vue'
import FeedbackToast from '../components/FeedbackToast.vue'
import { useStudentStore } from '../stores/studentStore'
import studentMusicHero from '../assets/student-music-classroom-hero.png'

const store = useStudentStore()
const router = useRouter()
const toast = ref('')
const soundEnabled = ref(localStorage.getItem('student_sound_enabled') !== 'false')
let timer = 0

const studentName = computed(() => store.profile?.user?.realName || store.profile?.user?.username || '小小音乐家')
const avatarText = computed(() => studentName.value.slice(0, 1))
const teacherName = computed(() => store.currentClass?.teacherName || '授课老师')
const classLine = computed(() => [store.currentClass?.schoolName, store.currentClass?.className, teacherName.value].filter(Boolean).join(' · '))
const completedNodeIds = computed(() => new Set(
  store.submissions.filter(item => item.progressStatus === 'completed').map(item => item.nodeId),
))
const completedCount = computed(() => completedNodeIds.value.size)
const totalCount = computed(() => store.currentSession?.nodeStates.length || 0)
const starCount = computed(() => completedCount.value * 3)
const actionableNode = computed(() => {
  const nodes = store.currentSession?.nodeStates || []
  const current = store.currentNode
  if (current && !completedNodeIds.value.has(current.activityNodeId || current.id)) return current
  return nodes.find(node => node.status === 'unlocked' && !completedNodeIds.value.has(node.activityNodeId || node.id)) || null
})

const classroomState = computed(() => {
  const session = store.currentSession
  if (!session) return { key: 'none', label: '暂无进行中的课堂', title: '等待老师发布新课堂', description: '有新课堂时，这里会自动出现，不用反复刷新。', action: '' }
  if (session.status === 'not_started') return { key: 'waiting', label: '等待老师开启', title: session.courseTitle || '今天的音乐课', description: '老师正在准备课堂，开启后页面会自动提醒你。', action: '' }
  if (session.status === 'paused') return { key: 'paused', label: '课堂暂时休息', title: session.courseTitle || '今天的音乐课', description: '先休息一下，老师恢复课堂后会自动提醒你。', action: '' }
  if (session.status === 'ended' || (totalCount.value > 0 && completedCount.value >= totalCount.value)) return { key: 'done', label: '本节课已完成', title: session.courseTitle || '今天的音乐课', description: '今天的音乐挑战全部完成，星星已经放进收藏册！', action: '查看课堂小结' }
  if (!actionableNode.value && completedCount.value > 0) return { key: 'next', label: '等待下一活动', title: '当前活动已完成！', description: '太棒了，等老师开启下一关后会自动提醒你。', action: '' }
  if (actionableNode.value) return { key: 'active', label: '活动进行中', title: actionableNode.value.title, description: `今天共 ${totalCount.value} 个活动，已完成 ${completedCount.value} 个。`, action: completedCount.value ? '继续活动' : '进入活动' }
  return { key: 'open', label: '课堂已开启', title: session.courseTitle || '今天的音乐课', description: '老师已经开启课堂，准备好就出发吧。', action: '进入课堂' }
})

const activityProgress = computed(() => store.currentSession?.nodeStates || [])

async function refresh() {
  try { await Promise.all([store.refreshCurrentClassroom(), store.loadClassroomHistory()]) }
  catch { toast.value = store.error }
}

async function enterClassroom() {
  if (classroomState.value.key === 'done') return router.push('/classroom')
  if (actionableNode.value) {
    const id = actionableNode.value.activityNodeId || actionableNode.value.id
    await store.enterCurrentNode(id)
    return router.push(`/classroom/nodes/${id}`)
  }
  return router.push('/classroom')
}

function toggleSound() {
  soundEnabled.value = !soundEnabled.value
  localStorage.setItem('student_sound_enabled', String(soundEnabled.value))
}

async function logout() {
  store.logout()
  await router.push('/login')
}

onMounted(() => { refresh(); timer = window.setInterval(refresh, 3000) })
onBeforeUnmount(() => window.clearInterval(timer))
</script>

<template>
  <main class="page-shell home-page">
    <SceneHeader brand title="不亦乐乎" :subtitle="`你好，${studentName}！今天想听见什么声音？`" status="音乐课堂" />

    <details class="student-menu">
      <summary aria-label="打开学生菜单">
        <span class="star-total" aria-label="我的星星">★ {{ starCount }}</span>
        <span class="student-avatar" aria-hidden="true">{{ avatarText }}</span>
        <span class="student-menu-name">{{ studentName }}</span>
      </summary>
      <div class="student-menu-panel">
        <div><strong>{{ studentName }}</strong><span>{{ classLine || '还没有加入班级' }}</span></div>
        <button type="button" @click="toggleSound"><span aria-hidden="true">{{ soundEnabled ? '🔊' : '🔇' }}</span>声音提示：{{ soundEnabled ? '开' : '关' }}</button>
        <button type="button" @click="router.push('/join-class')"><span aria-hidden="true">＋</span>加入新班级</button>
        <button type="button" @click="logout"><span aria-hidden="true">↪</span>退出登录</button>
      </div>
    </details>

    <section class="current-classroom" :class="`state-${classroomState.key}`">
      <div class="classroom-main">
        <div class="classroom-status"><span class="status-dot"></span>{{ classroomState.label }}</div>
        <p class="section-label">当前课堂</p>
        <h2>{{ classroomState.title }}</h2>
        <p class="class-meta">{{ classLine || '加入班级后即可参与课堂' }}</p>
        <p class="class-description">{{ classroomState.description }}</p>

        <button v-if="classroomState.action" class="primary-action classroom-action" type="button" @click="enterClassroom">
          {{ classroomState.action }} <span aria-hidden="true">→</span>
        </button>
        <div v-else-if="['waiting', 'paused', 'next'].includes(classroomState.key)" class="waiting-indicator" role="status">
          <span class="waiting-bars" aria-hidden="true"><i></i><i></i><i></i></span>
          {{ classroomState.label }}……
          <small>状态会自动更新，无需刷新</small>
        </div>
      </div>

      <div class="classroom-visual student-hero-art" aria-hidden="true"><img :src="studentMusicHero" alt="" /></div>
    </section>

    <section v-if="activityProgress.length" class="activity-journey" aria-label="今天的课堂活动进度">
      <div class="journey-heading">
        <div><p class="section-label">今天的活动</p><h2>已完成 {{ completedCount }} / {{ totalCount }}</h2></div>
        <div class="journey-progress"><span :style="{ width: `${totalCount ? completedCount / totalCount * 100 : 0}%` }"></span></div>
      </div>
      <ol>
        <li v-for="node in activityProgress" :key="node.activityNodeId || node.id" :class="{
          completed: completedNodeIds.has(node.activityNodeId || node.id),
          current: (node.activityNodeId || node.id) === (actionableNode?.activityNodeId || actionableNode?.id),
          locked: node.status !== 'unlocked',
        }">
          <span class="activity-marker" aria-hidden="true">{{ completedNodeIds.has(node.activityNodeId || node.id) ? '✓' : node.status !== 'unlocked' ? '锁' : node.sortOrder }}</span>
          <span><strong>{{ node.title }}</strong><small>{{ completedNodeIds.has(node.activityNodeId || node.id) ? '已经完成' : node.status !== 'unlocked' ? '等待老师开启' : '现在进行' }}</small></span>
        </li>
      </ol>
    </section>

    <section class="quick-grid">
      <button class="quick-card stars-card" type="button" @click="router.push('/history')">
        <span class="quick-icon" aria-hidden="true">★</span><span><small>我的星星</small><strong>本节获得 {{ starCount }} 颗星</strong><em>已完成 {{ completedCount }} 个课堂活动</em></span><b aria-hidden="true">→</b>
      </button>
      <article class="quick-card class-card">
        <span class="quick-icon" aria-hidden="true">♫</span><span><small>我的班级</small><strong>{{ store.currentClass?.className || '还没有加入班级' }}</strong><em>{{ store.currentClass ? teacherName : '可从头像菜单加入班级' }}</em></span>
      </article>
    </section>

    <FeedbackToast :message="toast" tone="warning" />
  </main>
</template>
