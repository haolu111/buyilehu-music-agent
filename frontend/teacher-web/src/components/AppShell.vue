<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'

const router = useRouter()
const auth = useAuthStore()

function logout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand">
        <span class="brand-mark">教</span>
        <div>
          <strong>教师端</strong>
          <small>Buyilehu Music Agent</small>
        </div>
      </div>
      <nav class="nav">
        <RouterLink to="/dashboard">工作台</RouterLink>
        <RouterLink to="/classes">班级管理</RouterLink>
        <RouterLink to="/lesson-plans/upload">上传教案</RouterLink>
        <RouterLink to="/lesson-plans/history">教案历史</RouterLink>
        <RouterLink to="/packages/generate">生成互动包</RouterLink>
      </nav>
    </aside>

    <main class="main">
      <header class="topbar">
        <div>
          <strong>{{ auth.user?.displayName || auth.user?.realName || auth.user?.username || 'teacher001' }}</strong>
          <span class="muted"> / {{ auth.user?.role || 'teacher' }}</span>
        </div>
        <button class="ghost" @click="logout">退出登录</button>
      </header>
      <section class="page">
        <slot />
      </section>
    </main>
  </div>
</template>
