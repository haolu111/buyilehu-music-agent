import { defineStore } from 'pinia'
import { authApi } from '../api/authApi'
import type { UserInfo } from '../types'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('teacher_token') || '',
    user: null as UserInfo | null,
  }),
  getters: {
    isLoggedIn: (state) => Boolean(state.token),
  },
  actions: {
    async login(username: string, password: string) {
      const result = await authApi.login(username, password)
      this.token = result.token
      this.user = result.user
      localStorage.setItem('teacher_token', result.token)
    },
    async fetchMe() {
      this.user = await authApi.me()
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('teacher_token')
    },
  },
})
