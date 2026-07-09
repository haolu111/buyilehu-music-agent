<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import AppShell from '../components/AppShell.vue'
import { classroomApi } from '../api/classroomApi'
import { classApi } from '../api/classApi'
import type { ClassroomSession, StudentSubmission, UserInfo } from '../types'

const route = useRoute()
const sessionId = Number(route.params.sessionId)
const session = ref<ClassroomSession | null>(null)
const submissions = ref<StudentSubmission[]>([])
const classStudents = ref<UserInfo[]>([])
const loading = ref(false)
const error = ref('')

const students = computed(() => {
  const map = new Map<number, string>()
  for (const student of classStudents.value) {
    const id = Number((student as UserInfo & { studentId?: number }).studentId || student.id)
    map.set(id, student.realName || student.displayName || student.username || `学生 #${id}`)
  }
  for (const item of submissions.value) {
    if (!map.has(item.studentId)) {
      map.set(item.studentId, item.studentName || `学生 #${item.studentId}`)
    }
  }
  return Array.from(map.entries())
    .map(([id, name]) => ({ id, name }))
    .sort((left, right) => left.name.localeCompare(right.name))
})

const nodes = computed(() => session.value?.nodeStates || [])
const totalTaskCount = computed(() => students.value.length * nodes.value.length)
const completedSubmissions = computed(() => {
  const keys = new Set<string>()
  for (const item of submissions.value) {
    if (item.progressStatus === 'completed') {
      keys.add(`${item.studentId}-${item.nodeId}`)
    }
  }
  return keys.size
})
const completionRate = computed(() => {
  if (!totalTaskCount.value) return 0
  return Math.round((completedSubmissions.value / totalTaskCount.value) * 100)
})
const averageScore = computed(() => {
  const scored = submissions.value.filter((item) => item.score != null)
  if (!scored.length) return 0
  const total = scored.reduce((sum, item) => sum + Number(item.score || 0), 0)
  return Math.round(total / scored.length)
})
const pieStyle = computed(() => ({
  background: `conic-gradient(#2a9d8f 0 ${completionRate.value}%, #e5e7eb ${completionRate.value}% 100%)`,
}))

const nodeBars = computed(() => nodes.value.map((node) => {
  const nodeId = node.activityNodeId || node.id
  const completed = new Set(
    submissions.value
      .filter((item) => item.nodeId === nodeId && item.progressStatus === 'completed')
      .map((item) => item.studentId),
  ).size
  const rate = students.value.length ? Math.round((completed / students.value.length) * 100) : 0
  return {
    id: nodeId,
    title: node.title,
    sortOrder: node.sortOrder,
    completed,
    rate,
  }
}))

const scoreBuckets = computed(() => {
  const buckets = [
    { label: '0-59', min: 0, max: 59, count: 0 },
    { label: '60-79', min: 60, max: 79, count: 0 },
    { label: '80-89', min: 80, max: 89, count: 0 },
    { label: '90-100', min: 90, max: 100, count: 0 },
  ]
  for (const item of submissions.value) {
    if (item.score == null) continue
    const score = Number(item.score)
    const bucket = buckets.find((part) => score >= part.min && score <= part.max)
    if (bucket) bucket.count += 1
  }
  const max = Math.max(1, ...buckets.map((item) => item.count))
  return buckets.map((item) => ({ ...item, rate: Math.round((item.count / max) * 100) }))
})

const studentRows = computed(() => students.value.map((student) => {
  const studentSubmissions = submissions.value.filter((item) => item.studentId === student.id)
  const completedNodeIds = new Set(
    studentSubmissions
      .filter((item) => item.progressStatus === 'completed')
      .map((item) => item.nodeId),
  )
  const scored = studentSubmissions.filter((item) => item.score != null)
  const score = scored.length
    ? Math.round(scored.reduce((sum, item) => sum + Number(item.score || 0), 0) / scored.length)
    : null
  return {
    id: student.id,
    name: student.name,
    completed: completedNodeIds.size,
    total: nodes.value.length,
    rate: nodes.value.length ? Math.round((completedNodeIds.size / nodes.value.length) * 100) : 0,
    score,
    submissions: studentSubmissions.sort((left, right) => (left.sortOrder || 9999) - (right.sortOrder || 9999)),
  }
}))

async function loadReport() {
  loading.value = true
  error.value = ''
  try {
    const sessionData = await classroomApi.getSession(sessionId)
    const [submissionData, studentData] = await Promise.all([
      classroomApi.listSubmissions(sessionId),
      classApi.listStudents(sessionData.classId),
    ])
    session.value = sessionData
    submissions.value = submissionData
    classStudents.value = studentData
  } catch (exception) {
    error.value = exception instanceof Error ? exception.message : '加载课程分析失败'
  } finally {
    loading.value = false
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

function formatResult(value?: string) {
  if (!value) return '暂无提交内容'
  try {
    return JSON.stringify(JSON.parse(value), null, 2)
  } catch {
    return value
  }
}

onMounted(loadReport)
</script>

<template>
  <AppShell>
    <div class="section-header">
      <div>
        <h1>{{ session?.courseTitle || `课堂分析 #${sessionId}` }}</h1>
        <p class="muted">班级 #{{ session?.classId || '-' }} / {{ statusText(session?.status) }}</p>
      </div>
      <button class="button" type="button" @click="loadReport">刷新分析</button>
    </div>

    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="loading" class="muted">加载分析中...</p>

    <template v-if="session && !loading">
      <section class="grid">
        <div class="stat"><strong>{{ students.length }}</strong><span>参与学生</span></div>
        <div class="stat"><strong>{{ completedSubmissions }}/{{ totalTaskCount }}</strong><span>完成任务</span></div>
        <div class="stat"><strong>{{ completionRate }}%</strong><span>总体完成率</span></div>
        <div class="stat"><strong>{{ averageScore || '-' }}</strong><span>平均分</span></div>
      </section>

      <section class="analysis-grid">
        <article class="card stack">
          <h2>总体完成分析</h2>
          <div class="pie-row">
            <div class="pie-chart" :style="pieStyle"><span>{{ completionRate }}%</span></div>
            <div>
              <p class="muted">已完成 {{ completedSubmissions }} 个学生任务</p>
              <p class="muted">未完成 {{ Math.max(0, totalTaskCount - completedSubmissions) }} 个学生任务</p>
            </div>
          </div>
        </article>

        <article class="card stack">
          <h2>分数分布</h2>
          <div class="bar-list">
            <div v-for="bucket in scoreBuckets" :key="bucket.label" class="bar-row">
              <span>{{ bucket.label }}</span>
              <div class="bar-track"><i :style="{ width: `${bucket.rate}%` }"></i></div>
              <strong>{{ bucket.count }}</strong>
            </div>
          </div>
        </article>
      </section>

      <section class="card stack" style="margin-top: 18px;">
        <h2>各环节完成情况</h2>
        <div class="bar-list">
          <div v-for="node in nodeBars" :key="node.id" class="bar-row wide-bar">
            <span>{{ node.sortOrder }}. {{ node.title }}</span>
            <div class="bar-track"><i :style="{ width: `${node.rate}%` }"></i></div>
            <strong>{{ node.completed }}/{{ students.length }}</strong>
          </div>
        </div>
      </section>

      <section class="card stack" style="margin-top: 18px;">
        <h2>学生作答明细</h2>
        <table class="data-table">
          <thead>
            <tr>
              <th>学生</th>
              <th>完成情况</th>
              <th>平均分</th>
              <th>具体作答</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!studentRows.length">
              <td colspan="4">暂无学生提交数据</td>
            </tr>
            <tr v-for="row in studentRows" :key="row.id">
              <td>{{ row.name }}</td>
              <td>{{ row.completed }}/{{ row.total }}（{{ row.rate }}%）</td>
              <td>{{ row.score ?? '-' }}</td>
              <td>
                <div class="answer-list">
                  <div v-for="item in row.submissions" :key="item.progressId" class="answer-item">
                    <strong>{{ item.nodeTitle || `环节 #${item.nodeId}` }}</strong>
                    <span>{{ statusText(item.progressStatus) }} / {{ item.score ?? '-' }} 分</span>
                    <pre>{{ formatResult(item.resultJson) }}</pre>
                  </div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </section>
    </template>
  </AppShell>
</template>