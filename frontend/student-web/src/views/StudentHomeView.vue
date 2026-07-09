<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import SceneHeader from '../components/SceneHeader.vue'
import FeedbackToast from '../components/FeedbackToast.vue'
import { useStudentStore } from '../stores/studentStore'

const store = useStudentStore()
const router = useRouter()
const toast = ref('')
const activeClassId = computed(() => store.currentSession?.classId || null)

async function refresh() {
  try {
    await Promise.all([
      store.refreshCurrentClassroom(),
      store.loadClassroomHistory(),
    ])
  } catch {
    toast.value = store.error
  }
}

onMounted(refresh)
</script>

<template>
  <main class="page-shell">
    <SceneHeader
      title="我的课堂"
      :subtitle="store.profile?.displayName || store.profile?.username || '学生'"
      status="Home"
    />

    <section class="home-grid">
      <article class="action-card">
        <h2>已加入班级</h2>
        <p>{{ store.currentClass?.className || '暂无班级' }}</p>
        <button class="secondary-action" type="button" @click="router.push('/join-class')">加入班级</button>
      </article>

      <article class="action-card">
        <h2>当前课堂</h2>
        <p>{{ store.currentSession ? `状态：${store.currentSession.status}` : '暂无进行中的课堂' }}</p>
        <button
          class="primary-action"
          type="button"
          :disabled="!store.currentSession"
          @click="router.push('/classroom')"
        >
          进入课堂
        </button>
      </article>

      <article class="action-card">
        <h2>课堂记录</h2>
        <p>{{ store.classroomHistory.length ? `共 ${store.classroomHistory.length} 节课堂` : '暂无课堂记录' }}</p>
        <button class="secondary-action" type="button" @click="router.push('/history')">查看历史课堂</button>
      </article>
    </section>

    <section class="card" style="margin-top: 18px;">
      <h2>我加入的班级</h2>
      <div v-if="store.joinedClasses.length" class="list">
        <div v-for="item in store.joinedClasses" :key="item.id" class="list-line">
          <div>
            <strong>#{{ item.id }} {{ item.className }}</strong>
            <p class="muted">{{ item.description || '暂无班级简介' }}</p>
          </div>
          <span class="tag" :class="{ active: activeClassId === item.id }">
            {{ activeClassId === item.id ? '当前课堂' : item.status }}
          </span>
        </div>
      </div>
      <p v-else class="muted">登录后会自动从后端同步已加入的班级。</p>
    </section>

    <section class="timeline-strip" aria-label="课堂流程">
      <span>登录</span>
      <span>入班</span>
      <span>进入课堂</span>
      <span>完成活动</span>
      <span>查看结果</span>
    </section>

    <FeedbackToast :message="toast" tone="warning" />
  </main>
</template>