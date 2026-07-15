import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/authStore'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/dashboard' },
    { path: '/login', component: () => import('../views/LoginView.vue'), meta: { public: true } },
    { path: '/dashboard', component: () => import('../views/DashboardView.vue') },
    { path: '/profile', component: () => import('../views/TeacherProfileView.vue') },
    { path: '/settings', component: () => import('../views/AccountSettingsView.vue') },
    { path: '/help', component: () => import('../views/HelpCenterView.vue') },
    { path: '/classes', component: () => import('../views/ClassListView.vue') },
    { path: '/classes/:classId', component: () => import('../views/ClassDetailView.vue') },
    { path: '/lesson-plans/upload', component: () => import('../views/LessonUploadView.vue') },
    { path: '/lesson-plans/history', component: () => import('../views/LessonPlanHistoryView.vue') },
    { path: '/lesson-plans/:lessonPlanId/parse-result', component: () => import('../views/LessonParseResultView.vue') },
    { path: '/packages/generate', component: () => import('../views/PackageGenerateView.vue') },
    { path: '/packages/:packageId/proposal', component: () => import('../views/ProposalCardView.vue') },
    { path: '/packages/:packageId', component: () => import('../views/PackageDetailView.vue') },
    { path: '/packages/:packageId/publish', component: () => import('../views/PublishPackageView.vue') },
    { path: '/classrooms', component: () => import('../views/ClassroomListView.vue') },
    { path: '/reports', component: () => import('../views/ReportCenterView.vue') },
    { path: '/classroom/:sessionId/control', component: () => import('../views/ClassroomControlView.vue') },
    { path: '/classroom/:sessionId/report', component: () => import('../views/ClassroomReportView.vue') },
    { path: '/packages/:packageId/edit', component: () => import('../views/PackageEditView.vue') },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  if (!to.meta.public && !auth.isLoggedIn) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
})

export default router
