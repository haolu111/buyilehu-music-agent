<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import AppShell from '../components/AppShell.vue'
import SubmissionResult from '../components/SubmissionResult.vue'
import { classroomApi } from '../api/classroomApi'
import type { ClassroomSession, StudentSubmission } from '../types'

const route = useRoute()
const sessionId = Number(route.params.sessionId)
const session = ref<ClassroomSession | null>(null)
const submissions = ref<StudentSubmission[]>([])
const loading = ref(false)
const error = ref('')
const message = ref('')
const page = ref(1)
const pageSize = ref(8)
let timer = 0

const currentNode = computed(() =>
  session.value?.nodeStates.find((node) => node.activityNodeId === session.value?.currentNodeId) || null,
)
const nextLockedNode = computed(() =>
  session.value?.nodeStates.find((node) => node.status === 'locked') || null,
)

const latestSubmissions = computed(() => {
  const map = new Map<string, StudentSubmission>()
  for (const item of submissions.value) {
    const key = `${item.studentId}-${item.nodeId}`
    const existing = map.get(key)
    if (!existing || String(item.lastActiveAt || '') >= String(existing.lastActiveAt || '')) {
      map.set(key, item)
    }
  }
  return Array.from(map.values()).sort((left, right) => {
    const studentCompare = String(left.studentName || '').localeCompare(String(right.studentName || ''))
    if (studentCompare !== 0) return studentCompare
    return (left.sortOrder || 9999) - (right.sortOrder || 9999)
  })
})

const pageCount = computed(() => Math.max(1, Math.ceil(latestSubmissions.value.length / pageSize.value)))
const pagedSubmissions = computed(() => {
  const start = (page.value - 1) * pageSize.value
  return latestSubmissions.value.slice(start, start + pageSize.value)
})

async function loadData(silent = false) {
  if (!silent) loading.value = true
  error.value = ''
  try {
    const [sessionData, submissionData] = await Promise.all([
      classroomApi.getSession(sessionId),
      classroomApi.listSubmissions(sessionId),
    ])
    session.value = sessionData
    submissions.value = submissionData
    if (page.value > pageCount.value) page.value = pageCount.value
  } catch (exception) {
    error.value = exception instanceof Error ? exception.message : '加载课堂失败'
  } finally {
    loading.value = false
  }
}

async function startSession() {
  try {
    session.value = await classroomApi.start(sessionId)
    message.value = '课堂已开始，第一个环节已解锁'
    await loadData(true)
  } catch (exception) {
    error.value = exception instanceof Error ? exception.message : '开始课堂失败'
  }
}

async function unlock(nodeId?: number) {
  if (!nodeId) return
  try {
    session.value = await classroomApi.unlockNode(sessionId, nodeId)
    message.value = '环节已解锁'
    await loadData(true)
  } catch (exception) {
    error.value = exception instanceof Error ? exception.message : '解锁失败'
  }
}

async function pauseSession() {
  try {
    session.value = await classroomApi.pause(sessionId)
    message.value = '课堂已暂停'
    await loadData(true)
  } catch (exception) {
    error.value = exception instanceof Error ? exception.message : '暂停失败'
  }
}

async function endSession() {
  try {
    session.value = await classroomApi.end(sessionId)
    message.value = '课堂已结束，可查看课程分析'
    await loadData(true)
  } catch (exception) {
    error.value = exception instanceof Error ? exception.message : '结束失败'
  }
}

function statusText(status?: string) {
  const map: Record<string, string> = {
    not_started: '未开始',
    running: '进行中',
    paused: '已暂停',
    ended: '已结束',
    locked: '锁定',
    unlocked: '已解锁',
    completed: '已完成',
    doing: '进行中',
  }
  return status ? map[status] || status : '-'
}

function prevPage() {
  page.value = Math.max(1, page.value - 1)
}

function nextPage() {
  page.value = Math.min(pageCount.value, page.value + 1)
}

onMounted(() => {
  loadData()
  timer = window.setInterval(() => loadData(true), 3000)
})

onBeforeUnmount(() => window.clearInterval(timer))
</script>

<template>
  <AppShell>
    <div class="section-header">
      <div>
        <h1>{{ session?.courseTitle || `课堂 #${sessionId}` }}</h1>
        <p class="muted">
          班级 #{{ session?.classId || '-' }} / {{ statusText(session?.status) }}
          <span v-if="session?.scheduledStartAt"> / 计划 {{ session.scheduledStartAt }}</span>
        </p>
      </div>
      <div class="button-row" style="margin-top: 0;">
        <RouterLink class="button primary" :to="`/classroom/${sessionId}/report`">课程分析</RouterLink>
        <button class="button" type="button" @click="loadData()">刷新</button>
      </div>
    </div>

    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="message" class="success">{{ message }}</p>

    <section v-if="session" class="card stack">
      <p class="muted">{{ session.courseDescription || '暂无课程简介' }}</p>
      <div class="button-row">
        <button class="primary" type="button" :disabled="session.status === 'running' || session.status === 'ended'" @click="startSession">
          开始课堂
        </button>
        <button class="button" type="button" :disabled="session.status !== 'running' || !nextLockedNode" @click="unlock(nextLockedNode?.activityNodeId)">
          解锁下一环节
        </button>
        <button class="button" type="button" :disabled="session.status !== 'running'" @click="pauseSession">暂停</button>
        <button class="button" type="button" :disabled="session.status === 'ended'" @click="endSession">结束课堂</button>
      </div>
    </section>

    <section v-if="session" class="card stack" style="margin-top: 18px;">
      <h2>课堂流程</h2>
      <div class="list">
        <div v-for="node in session.nodeStates" :key="node.id" class="list-line">
          <div>
            <strong>{{ node.sortOrder }}. {{ node.title }}</strong>
            <p class="muted">{{ node.nodeType }} / {{ statusText(node.status) }}</p>
          </div>
          <button class="button" type="button" :disabled="session.status !== 'running' || node.status === 'unlocked'" @click="unlock(node.activityNodeId)">
            解锁
          </button>
        </div>
      </div>
      <p class="muted">当前环节：{{ currentNode?.title || '尚未选择' }}</p>
    </section>

    <section class="card stack" style="margin-top: 18px;">
      <div class="section-header compact">
        <div>
          <h2>学生提交</h2>
          <p class="muted">自动刷新中，每个学生每个环节显示一条最新结果。</p>
        </div>
        <span class="tag">{{ latestSubmissions.length }} 条</span>
      </div>

      <p v-if="loading" class="muted">加载中...</p>
      <p v-else-if="!latestSubmissions.length" class="muted">暂无学生提交。学生完成或修改环节后会显示在这里。</p>

      <table v-else class="data-table">
        <thead>
          <tr>
            <th>学生</th>
            <th>环节</th>
            <th>状态</th>
            <th>分数</th>
            <th>提交结果</th>
            <th>更新时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in pagedSubmissions" :key="`${item.studentId}-${item.nodeId}`">
            <td>{{ item.studentName || `学生 #${item.studentId}` }}</td>
            <td>{{ item.nodeTitle || `环节 #${item.nodeId}` }}</td>
            <td>{{ statusText(item.progressStatus) }}</td>
            <td>{{ item.score ?? '-' }}</td>
            <td><SubmissionResult :value="item.resultJson" /></td>
            <td>{{ item.lastActiveAt || '-' }}</td>
          </tr>
        </tbody>
      </table>

      <div v-if="latestSubmissions.length" class="button-row">
        <button class="button" type="button" :disabled="page <= 1" @click="prevPage">上一页</button>
        <span class="muted">第 {{ page }} / {{ pageCount }} 页</span>
        <button class="button" type="button" :disabled="page >= pageCount" @click="nextPage">下一页</button>
      </div>
    </section>
  </AppShell>
</template>
