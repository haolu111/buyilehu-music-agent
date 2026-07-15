import { flushPromises, mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import { nextTick } from 'vue'
import { describe, expect, it } from 'vitest'
import WorkflowStepper from './WorkflowStepper.vue'

describe('WorkflowStepper', () => {
  it('uses the approved six-stage teaching workflow and maps proposal review separately', () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/:pathMatch(.*)*', component: { template: '<div />' } }],
    })
    const wrapper = mount(WorkflowStepper, {
      props: {
        currentStage: 'confirm-proposal',
        lessonPlanId: 8,
        packageId: 13,
      },
      global: { plugins: [router] },
    })

    expect(wrapper.text()).toContain('上传教案')
    expect(wrapper.text()).toContain('确认内容')
    expect(wrapper.text()).toContain('设置课堂')
    expect(wrapper.text()).toContain('确认方案')
    expect(wrapper.text()).toContain('编辑互动包')
    expect(wrapper.text()).toContain('发布课堂')
    expect(wrapper.text()).not.toContain('课堂控制')
    expect(wrapper.get('[data-stage="upload-lesson"]').attributes('data-state')).toBe('completed')
    expect(wrapper.get('[data-stage="upload-lesson"] a').attributes('href')).toBe('/lesson-plans/upload')
    expect(wrapper.get('[data-stage="setup-classroom"] a').attributes('href')).toBe('/packages/generate?lessonPlanId=8')
    expect(wrapper.get('[data-stage="confirm-proposal"]').attributes('data-state')).toBe('current')
    expect(wrapper.get('[data-stage="confirm-proposal"]').attributes('aria-current')).toBe('step')
    expect(wrapper.get('[data-stage="edit-package"]').attributes('data-state')).toBe('upcoming')
    expect(wrapper.get('[data-stage="edit-package"] [aria-disabled="true"]').text()).toContain('编辑互动包')
  })

  it('uses router links for available internal workflow routes', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/current', component: { template: '<div />' } },
        { path: '/lesson-plans/upload', component: { template: '<div />' } },
      ],
    })
    await router.push('/current')
    await router.isReady()

    const wrapper = mount(WorkflowStepper, {
      props: { currentStage: 'confirm-content', lessonPlanId: 8 },
      global: { plugins: [router] },
    })

    await wrapper.get('[data-stage="upload-lesson"] a').trigger('click')
    await nextTick()
    await flushPromises()
    expect(router.currentRoute.value.path).toBe('/lesson-plans/upload')
  })
})
