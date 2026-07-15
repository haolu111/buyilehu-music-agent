<script setup lang="ts">
import { ChartNoAxesCombined, ChevronDown, FileMusic, LayoutDashboard, Presentation, Users } from 'lucide-vue-next'
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/authStore'
import buyilehuLogo from '../assets/buyilehu-logo-sidebar.png'
import sidebarMusicNotes from '../assets/sidebar-music-notes.png'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const teacherName = computed(() => auth.user?.displayName || auth.user?.realName || auth.user?.username || '音乐教师')
const workspacePageClass = computed(() => {
  const path = route.path
  if (path.startsWith('/lesson-plans') || path.startsWith('/packages')) return 'workspace-page prep-workspace-page'
  if (path.startsWith('/classes')) return 'workspace-page class-workspace-page'
  if (path.startsWith('/classrooms') || path.startsWith('/classroom/')) return 'workspace-page classroom-workspace-page'
  if (path.startsWith('/reports')) return 'workspace-page report-workspace-page'
  if (path.startsWith('/profile') || path.startsWith('/settings') || path.startsWith('/help')) return 'workspace-page account-workspace-page'
  return ''
})
const navItems = [
  { label: '工作台', compactLabel: '首页', icon: LayoutDashboard, to: '/dashboard', matches: ['/dashboard'] },
  { label: '教案与互动包', compactLabel: '备课', icon: FileMusic, to: '/lesson-plans/history', matches: ['/lesson-plans', '/packages'] },
  { label: '班级与学生', compactLabel: '班级', icon: Users, to: '/classes', matches: ['/classes'] },
  { label: '课堂教学', compactLabel: '上课', icon: Presentation, to: '/classrooms', matches: ['/classrooms', '/classroom/'] },
  { label: '数据报告', compactLabel: '报告', icon: ChartNoAxesCombined, to: '/reports', matches: ['/reports'] },
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
      <div class="brand brand-logo-lockup"><img class="brand-logo-image" :src="buyilehuLogo" alt="不亦乐乎" /><strong>教师工作空间</strong></div>
      <nav class="nav" aria-label="主导航">
        <RouterLink v-for="item in navItems" :key="item.label" :to="item.to" :aria-label="item.label" :class="{ active: isActive(item) }"><component :is="item.icon" :size="18" stroke-width="2" aria-hidden="true" /><span class="nav-label-desktop" aria-hidden="true">{{ item.label }}</span><span class="nav-label-mobile" aria-hidden="true">{{ item.compactLabel }}</span></RouterLink>
      </nav>
      <div class="sidebar-art" aria-hidden="true"><img :src="sidebarMusicNotes" alt="" /></div>
    </aside>
    <main class="main" :class="{ 'dashboard-main': route.path === '/dashboard' }">
      <header class="topbar">
        <details class="teacher-menu">
          <summary><span class="teacher-avatar">👩🏻‍🏫</span><span><strong>{{ teacherName }}</strong><small>音乐教师</small></span><ChevronDown :size="18" aria-hidden="true" /></summary>
          <div class="teacher-menu-panel"><RouterLink to="/profile">个人信息</RouterLink><RouterLink to="/settings">账号设置</RouterLink><RouterLink to="/help">帮助中心</RouterLink><button class="danger-text" type="button" @click="logout">退出登录</button></div>
        </details>
      </header>
      <section class="page" :class="[{ 'dashboard-page': route.path === '/dashboard' }, workspacePageClass]"><slot /></section>
    </main>
  </div>
</template>
