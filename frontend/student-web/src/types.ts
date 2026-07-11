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
  score?: number
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