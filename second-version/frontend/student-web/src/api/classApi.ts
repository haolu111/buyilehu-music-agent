import request, { unwrap } from './request'
import type { ClassInfo } from '../types'

export function joinClass(inviteCode: string) {
  return unwrap<ClassInfo>(request.post('/classes/join', { inviteCode }))
}

export function listMine() {
  return unwrap<ClassInfo[]>(request.get('/classes'))
}
