<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'

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
    <form class="login-card" @submit.prevent="submit">
      <div class="brand center">
        <span class="brand-mark">♪</span>
        <div>
          <strong>不亦乐乎音乐课堂</strong>
          <small>教师端登录</small>
        </div>
      </div>
      <label>账号<input v-model="username" placeholder="teacher001" /></label>
      <label>密码<input v-model="password" type="password" placeholder="123456" /></label>
      <p v-if="error" class="error">{{ error }}</p>
      <button class="primary" :disabled="loading">{{ loading ? '登录中...' : '登录' }}</button>
      <p class="muted">默认验收账号：teacher001 / 123456</p>
    </form>
  </div>
</template>
