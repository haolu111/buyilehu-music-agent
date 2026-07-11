import request, { unwrap } from './request'
import type { ClassroomSession, StudentSubmission } from '../types'

export const classroomApi = {
  createSession(publicationId: number, payload: Record<string, unknown> = {}) {
    return unwrap<ClassroomSession>(request.post('/classroom-sessions', { publicationId, ...payload }))
  },
  listActiveSessions() {
    return unwrap<ClassroomSession[]>(request.get('/classroom-sessions/active'))
  },
  getSession(sessionId: number) {
    return unwrap<ClassroomSession>(request.get(`/classroom-sessions/${sessionId}`))
  },
  listSubmissions(sessionId: number) {
    return unwrap<StudentSubmission[]>(request.get(`/classroom-sessions/${sessionId}/submissions`))
  },
  start(sessionId: number) {
    return unwrap<ClassroomSession>(request.post(`/classroom-sessions/${sessionId}/start`))
  },
  unlockNode(sessionId: number, nodeId: number) {
    return unwrap<ClassroomSession>(request.post(`/classroom-sessions/${sessionId}/nodes/${nodeId}/unlock`))
  },
  pause(sessionId: number) {
    return unwrap<ClassroomSession>(request.post(`/classroom-sessions/${sessionId}/pause`))
  },
  end(sessionId: number) {
    return unwrap<ClassroomSession>(request.post(`/classroom-sessions/${sessionId}/end`))
  },
}