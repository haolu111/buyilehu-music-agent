import request, { unwrap } from './request'
import type { LoginResult, UserInfo } from '../types'

export const authApi = {
  login(username: string, password: string) {
    return unwrap<LoginResult>(request.post('/auth/login', { username, password }))
  },
  me() {
    return unwrap<UserInfo>(request.get('/auth/me'))
  },
}
