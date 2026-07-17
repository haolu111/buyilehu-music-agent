import request, { unwrap } from './request'
import type { GenerationJob, PackageInfo, PackageModifyPayload, PackageModifyResult, PackageVersion, ProposalCard } from '../types'

const createIdempotencyKey = () => (
  globalThis.crypto?.randomUUID?.()
  ?? `generation-${Date.now()}-${Math.random().toString(36).slice(2)}`
)

export const packageApi = {
  createGenerationJob(lessonPlanId: number, preferences: Record<string, unknown> = {}, idempotencyKey = createIdempotencyKey()) {
    return unwrap<GenerationJob>(request.post('/generation-jobs', { lessonPlanId, preferences }, {
      headers: { 'Idempotency-Key': idempotencyKey },
      // Package generation performs both design and quality-audit model calls.
      timeout: 180000,
    }))
  },
  getGenerationJob(jobId: number) {
    return unwrap<GenerationJob>(request.get(`/generation-jobs/${jobId}`))
  },
  watchGenerationJob(jobId: number, onStatus: (job: GenerationJob) => void, onError: (error: Error) => void) {
    const controller = new AbortController()
    let terminal = false

    const waitToReconnect = () => new Promise<void>((resolve) => window.setTimeout(resolve, 1500))
    const consume = async () => {
      const token = localStorage.getItem('teacher_token')
      const response = await fetch(`/api/v1/generation-jobs/${jobId}/events`, {
        headers: {
          Accept: 'text/event-stream',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        signal: controller.signal,
      })
      if (response.status === 401) {
        localStorage.removeItem('teacher_token')
        window.location.assign(`/login?redirect=${encodeURIComponent(window.location.pathname + window.location.search)}`)
        return
      }
      if (!response.ok || !response.body) {
        throw new Error(`状态订阅失败 (${response.status})`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''
      while (!terminal && !controller.signal.aborted) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true }).replace(/\r\n/g, '\n')
        const events = buffer.split('\n\n')
        buffer = events.pop() || ''
        for (const event of events) {
          const data = event.split('\n')
            .filter((line) => line.startsWith('data:'))
            .map((line) => line.slice(5).trimStart())
            .join('\n')
          if (!data) continue
          const status = JSON.parse(data) as GenerationJob
          terminal = status.status === 'success' || status.status === 'failed'
          onStatus(status)
        }
      }
    }

    void (async () => {
      while (!terminal && !controller.signal.aborted) {
        try {
          await consume()
        } catch (error) {
          if (controller.signal.aborted) return
          try {
            const snapshot = await packageApi.getGenerationJob(jobId)
            terminal = snapshot.status === 'success' || snapshot.status === 'failed'
            onStatus(snapshot)
          } catch {
            onError(error instanceof Error ? error : new Error('生成状态连接已断开'))
          }
        }
        if (!terminal && !controller.signal.aborted) await waitToReconnect()
      }
    })()

    return controller
  },
  getProposal(packageId: number) {
    return unwrap<ProposalCard>(request.get(`/packages/${packageId}/proposal`))
  },
  confirmProposal(packageId: number) {
    return unwrap<ProposalCard>(request.post(`/packages/${packageId}/proposal/confirm`))
  },
  getPackage(packageId: number) {
    return unwrap<PackageInfo>(request.get(`/packages/${packageId}`))
  },
  listPackages() {
    return unwrap<PackageInfo[]>(request.get('/packages'))
  },
  publishPackage(packageId: number, payload: Record<string, unknown>) {
    return unwrap<unknown>(request.post(`/packages/${packageId}/publish`, payload))
  },
  updateNodeConfig(packageId: number, nodeId: number, baseVersionId: number, payload: PackageModifyPayload) {
    return unwrap<PackageModifyResult>(request.patch(`/packages/${packageId}/nodes/${nodeId}/config`, payload, {
      headers: { 'X-Package-Version': String(baseVersionId) },
    }))
  },
  modifyPackage(packageId: number, nodeId: number, baseVersionId: number, payload: PackageModifyPayload) {
    return unwrap<PackageModifyResult>(request.post(`/packages/${packageId}/modify`, { nodeId, baseVersionId, config: payload }))
  },
  reviseNodeWithAgent(packageId: number, nodeId: number, baseVersionId: number, feedback: string) {
    return unwrap<PackageModifyResult>(request.post(`/packages/${packageId}/modify`, {
      nodeId,
      baseVersionId,
      modifyType: 'agent_node_revision',
      feedback,
      config: {},
    }))
  },
  listVersions(packageId: number) {
    return unwrap<PackageVersion[]>(request.get(`/packages/${packageId}/versions`))
  },
}
