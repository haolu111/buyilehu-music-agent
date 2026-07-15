import { describe, expect, it, vi } from 'vitest'
import type { LessonPlan } from '../types'
import { presentLessonPlan } from './lessonPlanPresentation'

describe('presentLessonPlan', () => {
  it('maps parsed lesson data into a bounded teacher-facing summary', () => {
    const lessonPlan: LessonPlan = {
      id: 8,
      title: '小星星',
      parsedJson: JSON.stringify({
        courseName: '闪烁的小星',
        grade: '一年级',
        objectives: ['能跟唱旋律', '感受四分音符'],
        keyPoints: ['稳定节拍'],
        process: [{ title: '律动导入', duration: '5分钟' }],
        musicElements: ['旋律', '节拍'],
      }),
    }

    expect(presentLessonPlan(lessonPlan)).toEqual({
      courseName: '闪烁的小星',
      grade: '一年级',
      objectives: ['能跟唱旋律', '感受四分音符'],
      keyPoints: ['稳定节拍'],
      process: [{ title: '律动导入', duration: '5分钟' }],
      musicElements: ['旋律', '节拍'],
    })
  })

  it('falls back to safe empty fields when parsed JSON is absent or invalid', () => {
    const lessonPlan: LessonPlan = { id: 8, title: '春天在哪里', parsedJson: '{not json' }

    expect(presentLessonPlan(lessonPlan)).toEqual({
      courseName: '春天在哪里',
      grade: '',
      objectives: [],
      keyPoints: [],
      process: [],
      musicElements: [],
    })
  })

  it('bounds every summary field and list while preserving readable values', () => {
    const longText = '节'.repeat(160)
    const lessonPlan: LessonPlan = {
      id: 9,
      title: '边界教案',
      parsedJson: JSON.stringify({
        courseName: longText,
        grade: longText,
        objectives: Array.from({ length: 8 }, () => longText),
        keyPoints: Array.from({ length: 8 }, () => longText),
        musicElements: Array.from({ length: 8 }, () => longText),
        process: Array.from({ length: 8 }, () => ({ title: longText, duration: longText })),
      }),
    }

    const summary = presentLessonPlan(lessonPlan)
    expect(summary.courseName).toHaveLength(120)
    expect(summary.grade).toHaveLength(120)
    expect(summary.objectives).toHaveLength(6)
    expect(summary.keyPoints).toHaveLength(6)
    expect(summary.musicElements).toHaveLength(6)
    expect(summary.process).toHaveLength(6)
    expect(summary.objectives[0]).toHaveLength(120)
    expect(summary.process[0]).toEqual({ title: longText.slice(0, 120), duration: longText.slice(0, 120) })
  })

  it('does not parse oversized raw JSON', () => {
    const parse = vi.spyOn(JSON, 'parse')
    const lessonPlan: LessonPlan = { id: 10, title: '安全教案', parsedJson: `{"courseName":"${'节'.repeat(100_000)}"}` }

    expect(presentLessonPlan(lessonPlan)).toMatchObject({ courseName: '安全教案' })
    expect(parse).not.toHaveBeenCalled()
  })
})
