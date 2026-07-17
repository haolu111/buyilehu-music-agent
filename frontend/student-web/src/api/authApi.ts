import request, { unwrap } from './request'
import type { LoginRequest, LoginResponse } from '../types'

export function login(payload: LoginRequest) {
  return unwrap<LoginResponse>(request.post('/auth/login', payload))
}

export function me() {
  return unwrap<LoginResponse['user']>(request.get('/auth/me'))
}
