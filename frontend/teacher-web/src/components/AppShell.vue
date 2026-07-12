<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const teacherName = computed(() => auth.user?.displayName || auth.user?.realName || auth.user?.username || '音乐教师')
const navItems = [
  { label: '工作台', icon: '⌂', to: '/dashboard', matches: ['/dashboard'] },
  { label: '班级与学生', icon: '人', to: '/classes', matches: ['/classes'] },
  { label: '教案与互动包', icon: '♫', to: '/lesson-plans/history', matches: ['/lesson-plans', '/packages'] },
  { label: '课堂教学', icon: '▷', to: '/classrooms', matches: ['/classrooms', '/classroom/'] },
  { label: '数据报告', icon: '▥', to: '/reports', matches: ['/reports'] },
]
function isActive(item: typeof navItems[number]) {
  if (item.label === '数据报告' && route.path.endsWith('/report')) return true
  if (item.label === '课堂教学' && route.path.endsWith('/report')) return false
  return item.matches.some(path => route.path === path || route.path.startsWith(`${path}/`) || (path.endsWith('/') && route.path.startsWith(path)))
}
async function logout() { auth.logout(); await router.push('/login') }
onMounted(() => { if (!auth.user && auth.isLoggedIn) auth.fetchMe().catch(() => undefined) })
</script>

<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand"><span class="brand-mark">♫</span><div><strong>不亦乐乎</strong><small>音乐课堂工作台</small></div></div>
      <nav class="nav" aria-label="主导航">
        <RouterLink v-for="item in navItems" :key="item.label" :to="item.to" :class="{ active: isActive(item) }"><span aria-hidden="true">{{ item.icon }}</span>{{ item.label }}</RouterLink>
      </nav>
      <div class="sidebar-foot"><span>●</span> 教学服务正常</div>
    </aside>
    <main class="main">
      <header class="topbar">
        <div class="topbar-title"><strong>教师工作空间</strong><span>备课、上课与复盘</span></div>
        <details class="teacher-menu">
          <summary><span class="teacher-avatar">{{ teacherName.slice(0, 1) }}</span><span><strong>{{ teacherName }}</strong><small>音乐教师</small></span></summary>
          <div class="teacher-menu-panel"><RouterLink to="/profile">个人信息</RouterLink><RouterLink to="/settings">账号设置</RouterLink><RouterLink to="/help">帮助中心</RouterLink><button class="danger-text" type="button" @click="logout">退出登录</button></div>
        </details>
      </header>
      <section class="page"><slot /></section>
    </main>
  </div>
</template>
