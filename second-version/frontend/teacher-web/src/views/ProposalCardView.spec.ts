import { flushPromises, mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const { getProposal, confirmProposal } = vi.hoisted(() => ({ getProposal: vi.fn(), confirmProposal: vi.fn() }))
vi.mock('../api/packageApi', () => ({ packageApi: { getProposal, confirmProposal } }))

import ProposalCardView from './ProposalCardView.vue'

const proposal = {
  id: 3, packageId: 34, packageInfo: { id: 34, lessonPlanId: 8, title: '小星星互动方案', status: 'generated' }, title: '小星星互动方案', versionNo: 1, content: '课程：音乐\n时长：40分钟\ntrace：private', status: 'generated', confirmStatus: 'pending',
  teachingObjectives: ['稳定拍点'], sourceLessonSections: ['律动导入'],
  activityNodes: [{ id: 9, title: '听辨旋律', nodeType: 'listening_activity', sortOrder: 1, components: [] }], components: [],
}

function makeRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/packages/:packageId/proposal', component: ProposalCardView },
      { path: '/packages/:packageId/edit', component: { template: '<div>编辑页</div>' } },
      { path: '/packages/generate', component: { template: '<div>设置课堂</div>' } },
      { path: '/lesson-plans/upload', component: { template: '<div>上传教案</div>' } },
    ],
  })
}

describe('ProposalCardView', () => {
  beforeEach(() => {
    getProposal.mockResolvedValue(proposal)
    confirmProposal.mockResolvedValue({ ...proposal, confirmStatus: 'confirmed' })
  })

  it('shows the confirm-proposal workflow stage and collapses supporting details', async () => {
    const router = makeRouter()
    await router.push('/packages/34/proposal')
    await router.isReady()
    const wrapper = mount(ProposalCardView, {
      global: { plugins: [router], stubs: { AppShell: { template: '<div><slot /></div>' }, LessonWorkspaceNav: { template: '<div />' } } },
    })
    await flushPromises()

    expect(wrapper.get('[data-stage="confirm-proposal"]').attributes('data-state')).toBe('current')
    expect(wrapper.get('[data-testid="back-to-classroom-settings"]').text()).toBe('返回调整')
    expect(wrapper.get('[data-testid="confirm-proposal"]').text()).toBe('确认方案，进入编辑')
    expect(wrapper.get('details[data-testid="proposal-objectives"]').attributes('open')).toBeUndefined()
    expect(wrapper.get('details[data-testid="proposal-source"]').attributes('open')).toBeUndefined()
  })

  it('confirms once and goes directly to package editing', async () => {
    const router = makeRouter()
    await router.push('/packages/34/proposal')
    await router.isReady()
    const wrapper = mount(ProposalCardView, {
      global: { plugins: [router], stubs: { AppShell: { template: '<div><slot /></div>' }, LessonWorkspaceNav: { template: '<div />' } } },
    })
    await flushPromises()

    await wrapper.get('[data-testid="confirm-proposal"]').trigger('click')
    await flushPromises()

    expect(confirmProposal).toHaveBeenCalledWith(34)
    expect(router.currentRoute.value.fullPath).toBe('/packages/34/edit')
  })

  it('returns to the original lesson plan settings when the teacher adjusts the proposal', async () => {
    const router = makeRouter()
    await router.push('/packages/34/proposal')
    await router.isReady()
    const wrapper = mount(ProposalCardView, {
      global: { plugins: [router], stubs: { AppShell: { template: '<div><slot /></div>' }, LessonWorkspaceNav: { template: '<div />' } } },
    })
    await flushPromises()

    await wrapper.get('[data-testid="back-to-classroom-settings"]').trigger('click')
    await flushPromises()

    expect(router.currentRoute.value.fullPath).toBe('/packages/generate?lessonPlanId=8')
  })

  it('does not offer confirmation again after the proposal is already confirmed', async () => {
    getProposal.mockResolvedValue({ ...proposal, confirmStatus: 'confirmed' })
    const router = makeRouter()
    await router.push('/packages/34/proposal')
    await router.isReady()
    const wrapper = mount(ProposalCardView, {
      global: { plugins: [router], stubs: { AppShell: { template: '<div><slot /></div>' }, LessonWorkspaceNav: { template: '<div />' } } },
    })
    await flushPromises()

    expect(wrapper.find('[data-testid="confirm-proposal"]').exists()).toBe(false)
    expect(wrapper.get('[data-testid="edit-confirmed-package"]').attributes('href')).toBe('/packages/34/edit')
  })
})
