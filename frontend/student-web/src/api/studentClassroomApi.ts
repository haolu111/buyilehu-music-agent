import request, { unwrap } from './request'
import type { ClassroomSession, NodeSubmitPayload, StudentCurrentClassroom } from '../types'

export function getCurrentClassroom() {
  return unwrap<StudentCurrentClassroom | ClassroomSession | null>(
    request.get('/student/classrooms/current'),
  )
}

export function enterNode(sessionId: number, nodeId: number) {
  return unwrap<ClassroomSession>(
    request.post(`/student/classroom-sessions/${sessionId}/nodes/${nodeId}/enter`),
  )
}

export function submitNode(sessionId: number, nodeId: number, payload: NodeSubmitPayload) {
  return unwrap<ClassroomSession>(
    request.post(`/student/classroom-sessions/${sessionId}/nodes/${nodeId}/submit`, payload),
  )
}
