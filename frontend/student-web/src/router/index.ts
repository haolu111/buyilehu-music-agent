import { createRouter, createWebHistory } from 'vue-router'
import { useStudentStore } from '../stores/studentStore'
import LoginView from '../views/LoginView.vue'
import JoinClassView from '../views/JoinClassView.vue'
import StudentHomeView from '../views/StudentHomeView.vue'
import ClassroomEntryView from '../views/ClassroomEntryView.vue'
import ActivityNodeView from '../views/ActivityNodeView.vue'
import WaitingNextNodeView from '../views/WaitingNextNodeView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/home' },
    { path: '/login', name: 'login', component: LoginView, meta: { public: true } },
    { path: '/join-class', name: 'join-class', component: JoinClassView },
    { path: '/home', name: 'home', component: StudentHomeView },
    { path: '/classroom', name: 'classroom-entry', component: ClassroomEntryView },
    { path: '/classroom/nodes/:nodeId', name: 'activity-node', component: ActivityNodeView },
    { path: '/classroom/waiting', name: 'waiting-next-node', component: WaitingNextNodeView },
  ],
})

router.beforeEach(async (to) => {
  const authed = Boolean(localStorage.getItem('student_token'))
  if (!to.meta.public && !authed) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (authed) {
    const store = useStudentStore()
    await store.ensureJoinedClassesLoaded().catch((error: unknown) => {
      console.error('[student-web] failed to load joined classes', error)
    })
  }
  if (to.name === 'login' && authed) {
    return { name: 'home' }
  }
  return true
})

export default router
