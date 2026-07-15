<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SceneHeader from '../components/SceneHeader.vue'
import FeedbackToast from '../components/FeedbackToast.vue'
import { useStudentStore } from '../stores/studentStore'
import studentMusicHero from '../assets/student-music-classroom-hero.png'

const router = useRouter()
const route = useRoute()
const store = useStudentStore()
const username = ref('')
const password = ref('')
const toast = ref('')
const studentRoutePaths = new Set(['/home', '/join-class', '/classroom', '/classroom/waiting', '/history'])

function getSafeRedirect(value: unknown) {
  if (typeof value !== 'string') return '/home'
  if (studentRoutePaths.has(value) || value.startsWith('/classroom/nodes/')) return value
  return '/home'
}

async function submit() {
  try {
    await store.login(username.value, password.value)
    toast.value = '登录成功'
    await router.push(getSafeRedirect(route.query.redirect))
  } catch {
    toast.value = store.error
  }
}
</script>

<template>
  <main class="auth-screen">
    <section class="auth-visual" aria-hidden="true">
      <img class="auth-hero-image" :src="studentMusicHero" alt="" />
      <div class="auth-visual-copy"><strong>今天也来玩音乐吧！</strong><span>听一听 · 拍一拍 · 创作一下</span></div>
    </section>

    <section class="auth-panel">
      <SceneHeader title="学生登录" subtitle="进入你的音乐课堂" status="学生空间" />
      <form class="form-stack" @submit.prevent="submit">
        <label>
          账号
          <input v-model.trim="username" autocomplete="username" required />
        </label>
        <label>
          密码
          <input v-model="password" type="password" autocomplete="current-password" required />
        </label>
        <button class="primary-action" type="submit" :disabled="store.loading">
          {{ store.loading ? '登录中...' : '登录' }}
        </button>
      </form>
    </section>

    <FeedbackToast :message="toast" :tone="store.error ? 'error' : 'success'" />
  </main>
</template>
