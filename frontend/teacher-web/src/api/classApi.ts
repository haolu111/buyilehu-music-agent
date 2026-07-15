import request, { unwrap } from './request'
import type { ClassInfo, UserInfo } from '../types'

export const classApi = {
  createClass(className: string, description = '') {
    return unwrap<ClassInfo>(request.post('/classes', { className, description }))
  },
  listClasses() {
    return unwrap<ClassInfo[]>(request.get('/classes'))
  },
  joinClass(inviteCode: string) {
    return unwrap<ClassInfo>(request.post('/classes/join', { inviteCode }))
  },
  listStudents(classId: number) {
    return unwrap<UserInfo[]>(request.get(`/classes/${classId}/students`))
  },
}
