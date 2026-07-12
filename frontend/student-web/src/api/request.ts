import axios, { type AxiosError } from 'axios'
import type { ApiResponse } from '../types'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
})

function redirectToLogin() {
  const redirect = window.location.pathname + window.location.search
  if (window.location.pathname !== '/login') {
    window.location.assign(`/login?redirect=${encodeURIComponent(redirect)}`)
  }
}

request.interceptors.request.use((config) => {
  const token = localStorage.getItem('student_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

request.interceptors.response.use(
  (response) => {
    const body = response.data as ApiResponse<unknown>
    if (typeof body?.code === 'number' && body.code !== 0) {
      return Promise.reject(new Error(body.message || '请求失败'))
    }
    return response
  },
  (error: AxiosError<ApiResponse<unknown>>) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('student_token')
      localStorage.removeItem('student_profile')
      redirectToLogin()
    }
    return Promise.reject(new Error(error.response?.data?.message || (error.response?.status === 401 ? '登录已过期，请重新登录' : error.message) || '网络错误'))
  },
)

export async function unwrap<T>(promise: Promise<{ data: ApiResponse<T> }>): Promise<T> {
  const response = await promise
  return response.data.data
}

export default request
