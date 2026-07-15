<script setup lang="ts">
import { LogIn } from 'lucide-vue-next'
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'
import buyilehuLogo from '../assets/buyilehu-logo-sidebar.png'
import musicChildrenBanner from '../assets/music-children-orff-banner.png'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const username = ref('teacher001')
const password = ref('123456')
const loading = ref(false)
const error = ref('')

async function submit() {
  loading.value = true
  error.value = ''
  try {
    await auth.login(username.value, password.value)
    await router.push((route.query.redirect as string) || '/dashboard')
  } catch (err) {
    error.value = err instanceof Error ? err.message : '登录失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <section class="login-visual" aria-hidden="true">
      <img :src="musicChildrenBanner" alt="" />
      <div><strong>让音乐课堂动起来</strong><span>备课 · 游戏 · 互动 · 复盘</span></div>
    </section>
    <form class="login-card" @submit.prevent="submit">
      <div class="login-brand">
        <img :src="buyilehuLogo" alt="不亦乐乎" />
        <strong>教师工作空间</strong>
        <small>音乐课堂游戏生成智能体</small>
      </div>
      <label>账号<input v-model="username" placeholder="teacher001" /></label>
      <label>密码<input v-model="password" type="password" placeholder="123456" /></label>
      <p v-if="error" class="error">{{ error }}</p>
      <button class="primary login-submit" :disabled="loading"><LogIn :size="19" aria-hidden="true" />{{ loading ? '登录中...' : '进入工作空间' }}</button>
      <p class="muted">默认验收账号：teacher001 / 123456</p>
    </form>
  </div>
</template>
