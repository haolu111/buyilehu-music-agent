import { flushPromises, mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const { getProposal, listVersions } = vi.hoisted(() => ({ getProposal: vi.fn(), listVersions: vi.fn() }))
vi.mock('../api/packageApi', () => ({ packageApi: { getProposal, listVersions } }))

import PackageEditView from './PackageEditView.vue'

describe('PackageEditView', () => {
  beforeEach(() => {
    getProposal.mockResolvedValue({ id: 3, packageId: 34, title: '小星星互动包', content: '', status: 'draft', confirmStatus: 'confirmed', teachingObjectives: [], sourceLessonSections: [], activityNodes: [], components: [] })
    listVersions.mockResolvedValue([])
  })

  it('marks editing as the current workflow stage and provides the publishing next action', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/packages/:packageId/edit', component: PackageEditView },
        { path: '/packages/:packageId/proposal', component: { template: '<div>确认方案</div>' } },
        { path: '/packages/:packageId', component: { template: '<div>详情</div>' } },
        { path: '/packages/:packageId/publish', component: { template: '<div>发布</div>' } },
        { path: '/lesson-plans/upload', component: { template: '<div>上传</div>' } },
      ],
    })
    await router.push('/packages/34/edit')
    await router.isReady()
    const wrapper = mount(PackageEditView, {
      global: {
        plugins: [router],
        stubs: {
          AppShell: { template: '<div><slot /></div>' },
          VersionHistoryPanel: { template: '<div />' },
          ActivityNodeEditView: { template: '<div />' },
        },
      },
    })
    await flushPromises()

    expect(wrapper.get('[data-stage="edit-package"]').attributes('data-state')).toBe('current')
    expect(wrapper.get('[data-testid="publish-classroom-next"]').text()).toContain('发布到班级')
    expect(wrapper.get('[data-testid="publish-classroom-next"]').attributes('href')).toBe('/packages/34/publish')
    expect(wrapper.get('a.button:not([data-testid])').attributes('href')).toBe('/packages/34')
  })
})
