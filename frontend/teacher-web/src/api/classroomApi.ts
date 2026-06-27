import request, { unwrap } from './request'

export const classroomApi = {
  createSession(packageId: number, classId: number) {
    return unwrap<unknown>(request.post('/classroom-sessions', { packageId, classId }))
  },
  getSession(sessionId: number) {
    return unwrap<unknown>(request.get(`/classroom-sessions/${sessionId}`))
  },
}
