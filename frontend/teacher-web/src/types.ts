export interface ApiResponse<T> {
  code: number
  message: string
  data: T
  requestId: string
}

export interface UserInfo {
  id: number
  username: string
  displayName?: string
  realName?: string
  role: string
  status?: string
}

export interface LoginResult {
  token: string
  user: UserInfo
}

export interface ClassInfo {
  id: number
  className: string
  inviteCode?: string
  teacherId?: number
  studentCount?: number
  description?: string
  status?: string
}

export interface LessonPlan {
  id: number
  teacherId?: number
  title: string
  courseName?: string
  grade?: string
  parseStatus?: string
  status?: string
  sourceFileUrl?: string
  rawText?: string
  parsedJson?: string
  createdAt?: string
  updatedAt?: string
}

export interface LessonPlanSummary {
  id: number
  teacherId?: number
  title: string
  parseStatus?: string
  status?: string
  createdAt?: string
  updatedAt?: string
}

export interface GenerationJob {
  id: number
  lessonPlanId: number
  status: string
  progress?: number
  packageId?: number
  versionId?: number
}

export interface PackageInfo {
  id: number
  lessonPlanId?: number
  generationJobId?: number
  ownerId?: number
  currentVersionId?: number
  title: string
  description?: string
  status: string
}

export interface ProposalCard {
  id: number
  packageId: number
  generationJobId?: number
  versionId?: number
  versionNo?: number
  title: string
  content: string
  status: string
  confirmStatus: string
  packageInfo?: PackageInfo
  teachingObjectives: string[]
  sourceLessonSections: string[]
  activityNodes: Array<{
    id: number
    title: string
    nodeType: string
    sortOrder: number
    components: ComponentView[]
  }>
  components: ComponentView[]
}

export interface ComponentView {
  id: number
  activityNodeId: number
  componentDefinitionId: number
  componentKey: string
  name: string
  category: string
  instanceName: string
  sortOrder: number
}

export interface PackageModifyPayload {
  title?: string
  description?: string
  difficulty?: string
  rhythmCardCount?: number
  hintEnabled?: boolean
  hidden?: boolean
  componentInstanceId?: number
  componentParams?: Record<string, unknown>
}

export interface PackageModifyResult {
  packageId: number
  nodeId: number
  fromVersionId: number
  toVersionId: number
  versionNo: number
  message: string
}

export interface PackageVersion {
  id: number
  packageId: number
  versionNo: number
  createdBy: number
  remark?: string
  status: string
  createdAt?: string
  updatedAt?: string
}

export interface SessionNodeState {
  id: number
  sessionId: number
  activityNodeId: number
  title: string
  nodeType: string
  sortOrder: number
  status: 'locked' | 'unlocked'
  unlockedAt?: string
}

export interface ClassroomSession {
  id: number
  publicationId: number
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
  nodeStates: SessionNodeState[]
}

export interface StudentSubmission {
  progressId: number
  sessionId: number
  studentId: number
  studentName: string
  nodeId: number
  nodeTitle: string
  sortOrder: number
  progressStatus: string
  progress: number
  score?: number
  wrongCount: number
  hintUsedCount: number
  durationSeconds: number
  resultJson?: string
  lastActiveAt?: string
}