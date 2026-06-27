import request, { unwrap } from './request'

export const reportApi = {
  getClassroomReport(sessionId: number) {
    return unwrap<unknown>(request.get(`/reports/classroom-sessions/${sessionId}`))
  },
}
