import { flushPromises, mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import { describe, expect, it, vi } from 'vitest'
import { RAW_PREVIEW_MAX_LENGTH } from '../utils/textPreview'

const { getLessonPlan, presentLessonPlan } = vi.hoisted(() => ({ getLessonPlan: vi.fn(), presentLessonPlan: vi.fn() }))

vi.mock('../api/lessonPlanApi', () => ({
  lessonPlanApi: { getLessonPlan },
}))

vi.mock('../utils/lessonPlanPresentation', () => ({ presentLessonPlan }))

import LessonParseResultView from './LessonParseResultView.vue'

describe('LessonParseResultView', () => {
  it('renders the bounded presentation summary and keeps raw content collapsed', async () => {
    presentLessonPlan.mockReturnValue({
      courseName: '闪烁的小星',
      grade: '一年级',
      objectives: ['能跟唱旋律'],
      keyPoints: ['稳定节拍'],
      process: [{ title: '律动导入', duration: '5分钟' }],
      musicElements: ['旋律'],
    })
    getLessonPlan.mockResolvedValue({
      id: 8,
      title: '小星星',
      rawText: '这是教案原文',
      parsedJson: JSON.stringify({
        courseName: '闪烁的小星',
        grade: '一年级',
        objectives: ['能跟唱旋律'],
        keyPoints: ['稳定节拍'],
        process: [{ title: '律动导入', duration: '5分钟' }],
        musicElements: ['旋律'],
      }),
    })
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/lesson-plans/:lessonPlanId/parse-result', component: LessonParseResultView }],
    })
    await router.push('/lesson-plans/8/parse-result')
    await router.isReady()

    const wrapper = mount(LessonParseResultView, {
      global: {
        plugins: [router],
        stubs: { AppShell: { template: '<div><slot /></div>' } },
      },
    })
    await flushPromises()

    expect(presentLessonPlan).toHaveBeenCalledWith(expect.objectContaining({ id: 8 }))
    expect(wrapper.text()).toContain('闪烁的小星')
    expect(wrapper.text()).toContain('一年级')
    expect(wrapper.text()).toContain('音乐要素')
    expect(wrapper.text()).toContain('能跟唱旋律')
    expect(wrapper.text()).toContain('稳定节拍')
    expect(wrapper.text()).toContain('律动导入')
    expect(wrapper.findAll('details')).toHaveLength(2)
    expect(wrapper.findAll('details').every((details) => details.attributes('open') === undefined)).toBe(true)
    expect(wrapper.get('a.button.primary').text()).toBe('内容无误，设置课堂')
    expect(wrapper.get('a.button.primary').attributes('href')).toBe('/packages/generate?lessonPlanId=8')
  })

  it('caps both collapsed raw previews and explains when content is truncated', async () => {
    presentLessonPlan.mockReturnValue({ courseName: '安全教案', grade: '', objectives: [], keyPoints: [], process: [], musicElements: [] })
    getLessonPlan.mockResolvedValue({
      id: 9,
      title: '安全教案',
      parsedJson: 'J'.repeat(RAW_PREVIEW_MAX_LENGTH + 120),
      rawText: 'R'.repeat(RAW_PREVIEW_MAX_LENGTH + 120),
    })
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/lesson-plans/:lessonPlanId/parse-result', component: LessonParseResultView }],
    })
    await router.push('/lesson-plans/9/parse-result')
    await router.isReady()

    const wrapper = mount(LessonParseResultView, {
      global: { plugins: [router], stubs: { AppShell: { template: '<div><slot /></div>' } } },
    })
    await flushPromises()

    expect(wrapper.findAll('.parse-raw-details pre').map((preview) => preview.text().length)).toEqual([RAW_PREVIEW_MAX_LENGTH, RAW_PREVIEW_MAX_LENGTH])
    expect(wrapper.findAll('.parse-preview-truncated')).toHaveLength(2)
    expect(wrapper.findAll('.parse-preview-truncated').every((notice) => notice.text().includes('内容已截断'))).toBe(true)
  })
})
