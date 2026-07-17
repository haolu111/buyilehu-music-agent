<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import SceneHeader from '../components/SceneHeader.vue'
import FeedbackToast from '../components/FeedbackToast.vue'
import * as classroomApi from '../api/studentClassroomApi'
import { useStudentStore } from '../stores/studentStore'
import type { ClassroomSession, StudentSubmission } from '../types'

const router = useRouter()
const store = useStudentStore()
const toast = ref('')
const loading = ref(false)
const expandedSessionId = ref<number | null>(null)
const submissionsBySession = ref<Record<number, StudentSubmission[]>>({})

const sessions = computed(() => store.classroomHistory)

function statusText(status?: string) {
  const map: Record<string, string> = {
    not_started: '未开始',
    running: '进行中',
    paused: '已暂停',
    ended: '已结束',
  }
  return status ? map[status] || status : '-'
}

function formatTime(value?: string) {
  if (!value) return '-'
  return value.replace('T', ' ').slice(0, 16)
}

function completedCount(session: ClassroomSession) {
  const submissions = submissionsBySession.value[session.id] || []
  return submissions.filter((item) => item.progressStatus === 'completed').length
}

function averageScore(session: ClassroomSession) {
  const scored = (submissionsBySession.value[session.id] || []).filter((item) => item.score != null)
  if (!scored.length) return '-'
  const total = scored.reduce((sum, item) => sum + Number(item.score || 0), 0)
  return Math.round(total / scored.length)
}

async function loadHistory() {
  loading.value = true
  toast.value = ''
  try {
    await store.loadClassroomHistory()
  } catch {
    toast.value = store.error || '加载课堂记录失败'
  } finally {
    loading.value = false
  }
}

async function toggleResults(session: ClassroomSession) {
  if (expandedSessionId.value === session.id) {
    expandedSessionId.value = null
    return
  }
  expandedSessionId.value = session.id
  if (!submissionsBySession.value[session.id]) {
    submissionsBySession.value = {
      ...submissionsBySession.value,
      [session.id]: await classroomApi.listMySubmissions(session.id),
    }
  }
}

async function enterSession(session: ClassroomSession) {
  if (session.status === 'ended') return
  await store.enterHistorySession(session)
  await router.push('/classroom')
}

onMounted(loadHistory)
</script>

<template>
  <main class="page-shell">
    <SceneHeader title="课堂记录" subtitle="看看完成过的音乐挑战" status="课堂足迹" />

    <div class="action-row" style="margin-bottom: 18px;">
      <button class="secondary-action" type="button" @click="router.push('/home')">返回首页</button>
      <button class="secondary-action" type="button" @click="loadHistory">刷新记录</button>
    </div>

    <section v-if="loading" class="empty-state">
      <p>加载课堂记录中...</p>
    </section>

    <section v-else-if="!sessions.length" class="empty-state">
      <p>暂无课堂记录。完成课堂活动后会显示在这里。</p>
    </section>

    <section v-else class="history-list">
      <article v-for="session in sessions" :key="session.id" class="history-card">
        <div class="history-main">
          <div>
            <h2>{{ session.courseTitle || `课堂 #${session.id}` }}</h2>
            <p class="muted">班级 #{{ session.classId }} / {{ statusText(session.status) }}</p>
            <p class="muted">开始：{{ formatTime(session.startedAt || session.scheduledStartAt) }} / 结束：{{ formatTime(session.endedAt) }}</p>
          </div>
          <div class="history-stats">
            <span>{{ completedCount(session) }} / {{ session.nodeStates.length }} 环节</span>
            <strong>{{ averageScore(session) }}</strong>
          </div>
        </div>

        <p v-if="session.courseDescription" class="muted">{{ session.courseDescription }}</p>

        <div class="action-row">
          <button class="secondary-action" type="button" @click="toggleResults(session)">
            {{ expandedSessionId === session.id ? '收起结果' : '查看结果' }}
          </button>
          <button
            class="primary-action"
            type="button"
            :disabled="session.status === 'ended'"
            @click="enterSession(session)"
          >
            {{ session.status === 'ended' ? '已结束' : '进入课堂' }}
          </button>
        </div>

        <table v-if="expandedSessionId === session.id" class="result-table">
          <thead>
            <tr>
              <th>环节</th>
              <th>状态</th>
              <th>分数</th>
              <th>提交时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="!(submissionsBySession[session.id] || []).length">
              <td colspan="4">暂无提交记录</td>
            </tr>
            <tr v-for="item in submissionsBySession[session.id] || []" :key="item.progressId">
              <td>{{ item.nodeTitle || `环节 #${item.nodeId}` }}</td>
              <td>{{ statusText(item.progressStatus) }}</td>
              <td>{{ item.score ?? '-' }}</td>
              <td>{{ formatTime(item.lastActiveAt) }}</td>
            </tr>
          </tbody>
        </table>
      </article>
    </section>

    <FeedbackToast :message="toast" tone="warning" />
  </main>
</template>
