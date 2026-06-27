import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import * as authApi from '../api/authApi'
import * as classApi from '../api/classApi'
import * as classroomApi from '../api/studentClassroomApi'
import type { ClassroomSession, ClassInfo, LoginResponse } from '../types'

const savedProfile = localStorage.getItem('student_profile')

export const useStudentStore = defineStore('student', () => {
  const token = ref(localStorage.getItem('student_token') || '')
  const profile = ref<LoginResponse | null>(savedProfile ? JSON.parse(savedProfile) : null)
  const currentClass = ref<ClassInfo | null>(null)
  const currentSession = ref<ClassroomSession | null>(null)
  const loading = ref(false)
  const error = ref('')

  const isAuthed = computed(() => Boolean(token.value))
  const currentNode = computed(() => {
    if (!currentSession.value?.currentNodeId) return null
    return currentSession.value.nodeStates.find(
      (node) => (node.activityNodeId || node.id) === currentSession.value?.currentNodeId,
    ) || null
  })
  const firstUnlockedNode = computed(() =>
    currentSession.value?.nodeStates.find((node) => node.status === 'unlocked') || null,
  )

  async function login(username: string, password: string) {
    loading.value = true
    error.value = ''
    try {
      const data = await authApi.login({ username, password })
      token.value = data.token
      profile.value = data
      localStorage.setItem('student_token', data.token)
      localStorage.setItem('student_profile', JSON.stringify(data))
    } catch (exception) {
      error.value = exception instanceof Error ? exception.message : '登录失败'
      throw exception
    } finally {
      loading.value = false
    }
  }

  function logout() {
    token.value = ''
    profile.value = null
    currentClass.value = null
    currentSession.value = null
    localStorage.removeItem('student_token')
    localStorage.removeItem('student_profile')
  }

  async function join(inviteCode: string) {
    loading.value = true
    error.value = ''
    try {
      currentClass.value = await classApi.joinClass(inviteCode)
      return currentClass.value
    } catch (exception) {
      error.value = exception instanceof Error ? exception.message : '加入班级失败'
      throw exception
    } finally {
      loading.value = false
    }
  }

  async function refreshCurrentClassroom() {
    loading.value = true
    error.value = ''
    try {
      const data = await classroomApi.getCurrentClassroom()
      if (data && 'session' in data) {
        currentSession.value = data.session
        currentClass.value = data.classInfo || currentClass.value
      } else {
        currentSession.value = data
      }
      return currentSession.value
    } catch (exception) {
      error.value = exception instanceof Error ? exception.message : '课堂状态同步失败'
      throw exception
    } finally {
      loading.value = false
    }
  }

  async function enterCurrentNode(nodeId: number) {
    if (!currentSession.value) return null
    currentSession.value = await classroomApi.enterNode(currentSession.value.id, nodeId)
    return currentSession.value
  }

  async function submitCurrentNode(nodeId: number, resultJson: Record<string, unknown>, score?: number) {
    if (!currentSession.value) return null
    currentSession.value = await classroomApi.submitNode(currentSession.value.id, nodeId, {
      resultType: 'activity_result',
      score,
      resultJson,
    })
    return currentSession.value
  }

  return {
    token,
    profile,
    currentClass,
    currentSession,
    currentNode,
    firstUnlockedNode,
    loading,
    error,
    isAuthed,
    login,
    logout,
    join,
    refreshCurrentClassroom,
    enterCurrentNode,
    submitCurrentNode,
  }
})
