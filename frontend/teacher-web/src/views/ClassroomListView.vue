<script setup lang="ts">
import { onMounted, ref } from 'vue'
import AppShell from '../components/AppShell.vue'
import { classroomApi } from '../api/classroomApi'
import type { ClassroomSession } from '../types'

const sessions = ref<ClassroomSession[]>([])
const loading = ref(false)
const error = ref('')

async function loadSessions() {
  loading.value = true
  error.value = ''
  try {
    sessions.value = await classroomApi.listActiveSessions()
  } catch (exception) {
    error.value = exception instanceof Error ? exception.message : '加载课堂失败'
  } finally {
    loading.value = false
  }
}

function statusText(status: string) {
  const map: Record<string, string> = {
    not_started: '未开始',
    running: '进行中',
    paused: '已暂停',
    ended: '已结束',
  }
  return map[status] || status
}

onMounted(loadSessions)
</script>

<template>
  <AppShell>
    <div class="section-header">
      <div>
        <h1>课堂管理</h1>
        <p class="muted">查看待开始、进行中和已结束课堂。结束后可进入课程分析。</p>
      </div>
      <button class="button" type="button" @click="loadSessions">刷新</button>
    </div>

    <p v-if="error" class="error">{{ error }}</p>

    <section class="card stack">
      <p v-if="loading" class="muted">加载中...</p>
      <p v-else-if="!sessions.length" class="muted">暂无课堂。可以在互动包详情页创建课堂。</p>
      <div v-for="session in sessions" :key="session.id" class="list-line">
        <div>
          <strong>{{ session.courseTitle || `课堂 #${session.id}` }}</strong>
          <p class="muted">
            班级 #{{ session.classId }} / 环节 {{ session.nodeStates.length }} 个
            <span v-if="session.scheduledStartAt"> / 计划 {{ session.scheduledStartAt }}</span>
          </p>
        </div>
        <div class="button-row" style="margin-top: 0;">
          <span class="tag">{{ statusText(session.status) }}</span>
          <RouterLink class="button" :to="`/classroom/${session.id}/control`">控制台</RouterLink>
          <RouterLink class="button primary" :to="`/classroom/${session.id}/report`">课程分析</RouterLink>
        </div>
      </div>
    </section>
  </AppShell>
</template>