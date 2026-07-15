import { flushPromises, mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const { listMine, createGenerationJob } = vi.hoisted(() => ({
  listMine: vi.fn(),
  createGenerationJob: vi.fn(),
}))

vi.mock('../api/lessonPlanApi', () => ({ lessonPlanApi: { listMine } }))
vi.mock('../api/packageApi', () => ({ packageApi: { createGenerationJob } }))

import PackageGenerateView from './PackageGenerateView.vue'

function makeRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/packages/generate', component: PackageGenerateView },
      { path: '/packages/:packageId/proposal', component: { template: '<div />' } },
    ],
  })
}

describe('PackageGenerateView', () => {
  beforeEach(() => {
    listMine.mockResolvedValue([{ id: 8, title: '小星星', parseStatus: 'success' }])
    createGenerationJob.mockResolvedValue({ id: 2, lessonPlanId: 8, status: 'completed', packageId: 34 })
  })

  it('uses the setup-classroom workflow step and keeps advanced options closed by default', async () => {
    const router = makeRouter()
    await router.push('/packages/generate?lessonPlanId=8')
    await router.isReady()
    const wrapper = mount(PackageGenerateView, {
      global: { plugins: [router], stubs: { AppShell: { template: '<div><slot /></div>' }, LessonWorkspaceNav: { template: '<div />' } } },
    })
    await flushPromises()

    expect(wrapper.get('[data-stage="setup-classroom"]').attributes('data-state')).toBe('current')
    expect((wrapper.get('select[name="lesson-plan"]').element as HTMLSelectElement).value).toBe('8')
    const advanced = wrapper.get('details[data-testid="advanced-generation-settings"]')
    expect(advanced.attributes('open')).toBeUndefined()
    expect(advanced.text()).toContain('活动密度')
    expect(advanced.text()).toContain('视觉情境')
  })

  it('keeps the selected lesson and all existing defaults in the generation request', async () => {
    const router = makeRouter()
    await router.push('/packages/generate?lessonPlanId=8')
    await router.isReady()
    const wrapper = mount(PackageGenerateView, {
      global: { plugins: [router], stubs: { AppShell: { template: '<div><slot /></div>' }, LessonWorkspaceNav: { template: '<div />' } } },
    })
    await flushPromises()

    await wrapper.get('[data-testid="generate-package"]').trigger('click')
    await flushPromises()

    expect(createGenerationJob).toHaveBeenCalledWith(8, {
      duration: 40, mode: 'individual', density: 'standard', difficulty: 'grade', flow: 'teacher', theme: 'auto',
    })
    expect(router.currentRoute.value.fullPath).toBe('/packages/34/proposal')
  })
})
