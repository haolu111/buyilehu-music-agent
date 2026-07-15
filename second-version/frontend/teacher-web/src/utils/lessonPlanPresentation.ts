import type { LessonPlan } from '../types'

export interface LessonProcessItem {
  title: string
  duration: string
}

export interface LessonPlanPresentation {
  courseName: string
  grade: string
  objectives: string[]
  keyPoints: string[]
  process: LessonProcessItem[]
  musicElements: string[]
}

const MAX_ITEMS = 6
const MAX_TEXT_LENGTH = 120
const MAX_PARSED_JSON_LENGTH = 50_000

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function asText(value: unknown): string {
  return typeof value === 'string' ? value.replace(/\s+/g, ' ').trim().slice(0, MAX_TEXT_LENGTH) : ''
}

function asTextList(value: unknown): string[] {
  const values = Array.isArray(value) ? value : typeof value === 'string' ? value.split(/[、,，；;]/) : []
  return values.map(asText).filter(Boolean).slice(0, MAX_ITEMS)
}

function firstText(record: Record<string, unknown>, keys: string[]): string {
  for (const key of keys) {
    const text = asText(record[key])
    if (text) return text
  }
  return ''
}

function asProcess(value: unknown): LessonProcessItem[] {
  if (!Array.isArray(value)) return []

  return value.slice(0, MAX_ITEMS).flatMap((item) => {
    if (!isRecord(item)) return []
    const title = firstText(item, ['title', 'name', 'step', 'content'])
    if (!title) return []
    return [{ title, duration: firstText(item, ['duration', 'time', 'minutes']) }]
  })
}

function emptyPresentation(lessonPlan: LessonPlan): LessonPlanPresentation {
  return {
    courseName: lessonPlan.courseName || lessonPlan.title,
    grade: lessonPlan.grade || '',
    objectives: [],
    keyPoints: [],
    process: [],
    musicElements: [],
  }
}

export function presentLessonPlan(lessonPlan: LessonPlan): LessonPlanPresentation {
  const fallback = emptyPresentation(lessonPlan)
  if (!lessonPlan.parsedJson || lessonPlan.parsedJson.length > MAX_PARSED_JSON_LENGTH) return fallback

  try {
    const parsed: unknown = JSON.parse(lessonPlan.parsedJson)
    if (!isRecord(parsed)) return fallback

    return {
      courseName: firstText(parsed, ['courseName', 'course_name', 'lessonName', 'title']) || fallback.courseName,
      grade: firstText(parsed, ['grade', 'gradeName', 'grade_name']) || fallback.grade,
      objectives: asTextList(parsed.objectives ?? parsed.teachingObjectives ?? parsed.goals),
      keyPoints: asTextList(parsed.keyPoints ?? parsed.keyPointsAndDifficulties ?? parsed.importantPoints),
      process: asProcess(parsed.process ?? parsed.teachingProcess ?? parsed.steps),
      musicElements: asTextList(parsed.musicElements ?? parsed.musicElement ?? parsed.elements),
    }
  } catch {
    return fallback
  }
}
