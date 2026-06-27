import request, { unwrap } from './request'
import type { LessonPlan } from '../types'

export const lessonPlanApi = {
  upload(file: File, title?: string) {
    const formData = new FormData()
    formData.append('file', file)
    if (title) {
      formData.append('title', title)
    }
    return unwrap<LessonPlan>(request.post('/lesson-plans', formData))
  },
  getLessonPlan(lessonPlanId: number) {
    return unwrap<LessonPlan>(request.get(`/lesson-plans/${lessonPlanId}`))
  },
}
