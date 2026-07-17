export interface ApiResponse<T> {
  code: number
  message: string
  data: T
  requestId: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  token: string
  userId: number
  username: string
  displayName?: string
  role: 'teacher' | 'student'
}

export interface ClassInfo {
  id: number
  className: string
  teacherId: number
  teacherName?: string
  schoolName?: string
  inviteCode?: string
  description?: string
  status: string
}

export interface ActivityNode {
  id: number
  sessionId?: number
  activityNodeId?: number
  title: string
  nodeType: string
  sortOrder: number
  status?: 'locked' | 'unlocked'
  unlockedAt?: string
  configJson?: string
  runtimeConfig?: ActivityRuntimeConfig
}

export type ActivityRenderer =
  | 'meter-compare'
  | 'rhythm-drag'
  | 'creation-panel'
  | 'summary'
  | 'singing-practice'
  | 'listening-choice'
  | 'solfege-sort'
  | 'melody-trace'
  | 'timbre-match'
  | 'form-order'
  | 'virtual-instrument'
  | 'ensemble-roles'
  | 'completion'

export interface ActivityRuntimeConfig {
  schemaVersion: 'activity-runtime.v1' | 'interactive-node-runtime.v2'
  nodeType?: 'activity' | 'game' | 'instrument_task'
  family?: string
  variant?: string
  renderer: ActivityRenderer
  legacyRenderer?: ActivityRenderer
  props?: Record<string, unknown>
  assets?: Array<Record<string, unknown>>
  assessment?: { resultType?: string; maxScore?: number }
  mediaSession?: Record<string, unknown> | null
}

export interface ClassroomSession {
  id: number
  publicationId?: number
  classId: number
  packageId: number
  teacherId: number
  currentNodeId?: number | null
  status: 'not_started' | 'running' | 'paused' | 'ended'
  courseTitle?: string
  courseDescription?: string
  scheduledStartAt?: string
  startedAt?: string
  endedAt?: string
  nodeStates: ActivityNode[]
}

export interface StudentCurrentClassroom {
  session: ClassroomSession | null
  classInfo?: ClassInfo
}

export interface NodeSubmitPayload {
  resultType: string
  durationSeconds?: number
  resultJson?: Record<string, unknown>
}

export interface StudentSubmission {
  progressId: number
  sessionId: number
  studentId: number
  studentName?: string
  nodeId: number
  nodeTitle?: string
  sortOrder?: number
  progressStatus: string
  progress: number
  score?: number
  wrongCount: number
  hintUsedCount: number
  durationSeconds: number
  resultJson?: string
  lastActiveAt?: string
}
