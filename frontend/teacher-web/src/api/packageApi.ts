import request, { unwrap } from './request'
import type { GenerationJob, PackageInfo, PackageModifyPayload, PackageModifyResult, PackageVersion, ProposalCard } from '../types'

export const packageApi = {
  createGenerationJob(lessonPlanId: number, preferences: Record<string, unknown> = {}) {
    return unwrap<GenerationJob>(request.post('/generation-jobs', { lessonPlanId, preferences }))
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
  publishPackage(packageId: number, classId: number, versionId?: number) {
    return unwrap<unknown>(request.post(`/packages/${packageId}/publish`, { classId, versionId }))
  },
  updateNodeConfig(packageId: number, nodeId: number, payload: PackageModifyPayload) {
    return unwrap<PackageModifyResult>(request.patch(`/packages/${packageId}/nodes/${nodeId}/config`, payload))
  },
  modifyPackage(packageId: number, nodeId: number, payload: PackageModifyPayload) {
    return unwrap<PackageModifyResult>(request.post(`/packages/${packageId}/modify`, { nodeId, config: payload }))
  },
  listVersions(packageId: number) {
    return unwrap<PackageVersion[]>(request.get(`/packages/${packageId}/versions`))
  },
}