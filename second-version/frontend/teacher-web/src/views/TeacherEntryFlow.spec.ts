import { flushPromises, mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const { listClasses, listActiveSessions, listMine, listPackages, upload } = vi.hoisted(() => ({
  listClasses: vi.fn(),
  listActiveSessions: vi.fn(),
  listMine: vi.fn(),
  listPackages: vi.fn(),
  upload: vi.fn(),
}))

vi.mock('../api/classApi', () => ({ classApi: { listClasses } }))
vi.mock('../api/classroomApi', () => ({ classroomApi: { listActiveSessions } }))
vi.mock('../api/lessonPlanApi', () => ({ lessonPlanApi: { listMine, upload } }))
vi.mock('../api/packageApi', () => ({ packageApi: { listPackages } }))

import DashboardView from './DashboardView.vue'
import LessonPlanHistoryView from './LessonPlanHistoryView.vue'
import LessonUploadView from './LessonUploadView.vue'
import { useAuthStore } from '../stores/authStore'

function routerFor(component: object, path: string) {
  return createRouter({ history: createMemoryHistory(), routes: [{ path, component }, { path: '/:pathMatch(.*)*', component: { template: '<div />' } }] })
}

function shellStub() {
  return { AppShell: { template: '<div><slot /></div>' }, LessonWorkspaceNav: { template: '<div />' } }
}

describe('teacher entry flow', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    useAuthStore().user = { id: 1, username: 'teacher', role: 'teacher', displayName: '林老师' }
    listClasses.mockResolvedValue([])
    listPackages.mockResolvedValue([])
    listMine.mockResolvedValue([])
    listActiveSessions.mockResolvedValue([])
  })

  it('keeps exactly two fixed dashboard actions and sends teachers to a live classroom', async () => {
    listActiveSessions.mockResolvedValue([{ id: 24, status: 'running', nodeStates: [], courseTitle: '节奏游戏' }])
    const router = routerFor(DashboardView, '/dashboard')
    await router.push('/dashboard')
    await router.isReady()
    const wrapper = mount(DashboardView, { global: { plugins: [router], stubs: shellStub() } })
    await flushPromises()

    const actions = wrapper.get('[data-testid="dashboard-primary-actions"]')
    expect(actions.findAll('a')).toHaveLength(2)
    expect(actions.text()).toContain('上传教案')
    expect(actions.text()).toContain('进入课堂')
    expect(actions.findAll('a').map((link) => link.attributes('href'))).toEqual(['/lesson-plans/upload', '/classroom/24/control'])
  })

  it('keeps the primary actions clear beside a decorative music-classroom scene', async () => {
    const router = routerFor(DashboardView, '/dashboard')
    await router.push('/dashboard')
    await router.isReady()
    const wrapper = mount(DashboardView, { global: { plugins: [router], stubs: shellStub() } })
    await flushPromises()

    const scene = wrapper.get('[data-testid="dashboard-music-scene"]')
    expect(scene.attributes('aria-hidden')).toBe('true')
    expect(scene.get('img').attributes('alt')).toBe('')
    expect(wrapper.get('[data-testid="dashboard-primary-actions"]').text()).toContain('上传教案')
    expect(wrapper.get('[data-testid="dashboard-primary-actions"]').text()).toContain('进入课堂')
  })

  it('keeps a paused classroom available from the dashboard entry action', async () => {
    listActiveSessions.mockResolvedValue([{ id: 31, status: 'paused', nodeStates: [], courseTitle: '合唱排练' }])
    const router = routerFor(DashboardView, '/dashboard')
    await router.push('/dashboard')
    await router.isReady()
    const wrapper = mount(DashboardView, { global: { plugins: [router], stubs: shellStub() } })
    await flushPromises()

    expect(wrapper.get('[data-testid="dashboard-primary-actions"]').findAll('a')[1].attributes('href')).toBe('/classroom/31/control')
  })

  it('keeps an upcoming classroom available from the dashboard entry action', async () => {
    listActiveSessions.mockResolvedValue([{ id: 32, status: 'not_started', nodeStates: [], courseTitle: '节拍练习' }])
    const router = routerFor(DashboardView, '/dashboard')
    await router.push('/dashboard')
    await router.isReady()
    const wrapper = mount(DashboardView, { global: { plugins: [router], stubs: shellStub() } })
    await flushPromises()

    expect(wrapper.get('[data-testid="dashboard-primary-actions"]').findAll('a')[1].attributes('href')).toBe('/classroom/32/control')
  })

  it('uses the classroom list for the dashboard classroom action and hides zero pending items', async () => {
    const router = routerFor(DashboardView, '/dashboard')
    await router.push('/dashboard')
    await router.isReady()
    const wrapper = mount(DashboardView, { global: { plugins: [router], stubs: shellStub() } })
    await flushPromises()

    expect(wrapper.get('[data-testid="dashboard-primary-actions"]').findAll('a')[1].attributes('href')).toBe('/classrooms')
    expect(wrapper.findAll('[data-testid="continue-item"]')).toHaveLength(0)
    expect(wrapper.get('[data-testid="continue-empty"]').text()).toContain('暂时没有待处理事项')
  })

  it('sends the ready-package task to the counted generated package proposal', async () => {
    listPackages.mockResolvedValue([
      { id: 51, title: '节奏冒险', status: 'generated' },
      { id: 52, title: '旋律接龙', status: 'draft' },
    ])
    const router = routerFor(DashboardView, '/dashboard')
    await router.push('/dashboard')
    await router.isReady()
    const wrapper = mount(DashboardView, { global: { plugins: [router], stubs: shellStub() } })
    await flushPromises()

    const packageAction = wrapper.get('[data-testid="continue-package-item"]')
    expect(packageAction.attributes('href')).toBe('/packages/51/proposal')
    expect(packageAction.text()).toContain('确认互动方案')
  })

  it('sends a modified package to its classroom publishing flow', async () => {
    listPackages.mockResolvedValue([{ id: 53, title: '打击乐合奏', status: 'modified' }])
    const router = routerFor(DashboardView, '/dashboard')
    await router.push('/dashboard')
    await router.isReady()
    const wrapper = mount(DashboardView, { global: { plugins: [router], stubs: shellStub() } })
    await flushPromises()

    const packageAction = wrapper.get('[data-testid="continue-package-item"]')
    expect(packageAction.attributes('href')).toBe('/packages/53/publish')
    expect(packageAction.text()).toContain('发布课堂')
  })

  it('shows a retry state instead of an empty dashboard when a data request fails', async () => {
    listPackages.mockRejectedValueOnce(new Error('network unavailable'))
    const router = routerFor(DashboardView, '/dashboard')
    await router.push('/dashboard')
    await router.isReady()
    const wrapper = mount(DashboardView, { global: { plugins: [router], stubs: shellStub() } })
    await flushPromises()

    expect(wrapper.get('[data-testid="dashboard-load-error"]').text()).toContain('暂时无法加载')
    expect(wrapper.get('[data-testid="dashboard-retry"]').text()).toContain('重试')
    const callsBeforeRetry = listPackages.mock.calls.length
    await wrapper.get('[data-testid="dashboard-retry"]').trigger('click')
    await flushPromises()
    expect(listPackages).toHaveBeenCalledTimes(callsBeforeRetry + 1)
    expect(wrapper.find('[data-testid="dashboard-load-error"]').exists()).toBe(false)
  })

  it('reveals the lesson title after selecting a valid file and labels the primary action 解析教案', async () => {
    const router = routerFor(LessonUploadView, '/lesson-plans/upload')
    await router.push('/lesson-plans/upload')
    await router.isReady()
    const wrapper = mount(LessonUploadView, { global: { plugins: [router], stubs: shellStub() } })

    expect(wrapper.find('input[name="lesson-title"]').exists()).toBe(false)
    expect(wrapper.get('[data-testid="lesson-upload-primary"]').text()).toBe('解析教案')
    expect(wrapper.get('[data-stage="upload-lesson"]').attributes('data-state')).toBe('current')

    const fileInput = wrapper.get('input[type="file"]')
    Object.defineProperty(fileInput.element, 'files', { value: [new File(['lesson'], '小星星.docx', { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' })] })
    await fileInput.trigger('change')

    expect(wrapper.get('input[name="lesson-title"]').element).toHaveProperty('value', '小星星')
  })

  it('rejects unsupported and oversized uploads before exposing a title', async () => {
    const router = routerFor(LessonUploadView, '/lesson-plans/upload')
    await router.push('/lesson-plans/upload')
    await router.isReady()
    const wrapper = mount(LessonUploadView, { global: { plugins: [router], stubs: shellStub() } })
    const fileInput = wrapper.get('input[type="file"]')

    Object.defineProperty(fileInput.element, 'files', { configurable: true, value: [new File(['bad'], '教案.exe', { type: 'application/octet-stream' })] })
    await fileInput.trigger('change')
    expect(wrapper.text()).toContain('请选择 DOCX、PDF 或 TXT 格式的教案')
    expect(wrapper.find('input[name="lesson-title"]').exists()).toBe(false)

    Object.defineProperty(fileInput.element, 'files', { configurable: true, value: [new File([new Uint8Array(20 * 1024 * 1024 + 1)], '太大的教案.pdf', { type: 'application/pdf' })] })
    await fileInput.trigger('change')
    expect(wrapper.text()).toContain('文件不能超过 20MB')
    expect(wrapper.find('input[name="lesson-title"]').exists()).toBe(false)
  })

  it('clears the selected lesson before rejecting an invalid replacement', async () => {
    const router = routerFor(LessonUploadView, '/lesson-plans/upload')
    await router.push('/lesson-plans/upload')
    await router.isReady()
    const wrapper = mount(LessonUploadView, { global: { plugins: [router], stubs: shellStub() } })
    const fileInput = wrapper.get('input[type="file"]')
    Object.defineProperty(fileInput.element, 'files', { configurable: true, value: [new File(['lesson'], '小星星.docx')] })
    await fileInput.trigger('change')
    expect(wrapper.find('input[name="lesson-title"]').exists()).toBe(true)

    Object.defineProperty(fileInput.element, 'value', { configurable: true, writable: true, value: 'C:\\fakepath\\坏文件.exe' })
    Object.defineProperty(fileInput.element, 'files', { configurable: true, value: [new File(['bad'], '坏文件.exe')] })
    await fileInput.trigger('change')
    expect(wrapper.find('input[name="lesson-title"]').exists()).toBe(false)
    expect(wrapper.get('[data-testid="lesson-upload-primary"]').attributes('disabled')).toBeDefined()
    expect((fileInput.element as HTMLInputElement).value).toBe('')
  })

  it('clears the native chooser on removal so the same file can be selected again', async () => {
    const router = routerFor(LessonUploadView, '/lesson-plans/upload')
    await router.push('/lesson-plans/upload')
    await router.isReady()
    const wrapper = mount(LessonUploadView, { global: { plugins: [router], stubs: shellStub() } })
    const fileInput = wrapper.get('input[type="file"]')
    const lesson = new File(['lesson'], '小星星.docx')
    Object.defineProperty(fileInput.element, 'files', { configurable: true, value: [lesson] })
    Object.defineProperty(fileInput.element, 'value', { configurable: true, writable: true, value: 'C:\\fakepath\\小星星.docx' })
    await fileInput.trigger('change')
    await wrapper.get('button.ghost').trigger('click')

    expect((fileInput.element as HTMLInputElement).value).toBe('')
    expect(wrapper.get('[data-testid="lesson-upload-primary"]').attributes('disabled')).toBeDefined()
    Object.defineProperty(fileInput.element, 'files', { configurable: true, value: [lesson] })
    await fileInput.trigger('change')
    expect(wrapper.get('input[name="lesson-title"]').element).toHaveProperty('value', '小星星')
  })

  it('shows retry context but still requires a new lesson file', async () => {
    const router = routerFor(LessonUploadView, '/lesson-plans/upload')
    await router.push('/lesson-plans/upload?retryLessonPlanId=2')
    await router.isReady()
    const wrapper = mount(LessonUploadView, { global: { plugins: [router], stubs: shellStub() } })

    expect(wrapper.text()).toContain('重新上传教案后将开始新的解析')
    expect(wrapper.get('[data-testid="lesson-upload-primary"]').attributes('disabled')).toBeDefined()
  })

  it('maps each lesson plan status to one clear next action', async () => {
    listMine.mockResolvedValue([
      { id: 1, title: '解析中的教案', parseStatus: 'processing', status: 'pending' },
      { id: 2, title: '失败的教案', parseStatus: 'failed', status: 'pending' },
      { id: 3, title: '待确认教案', parseStatus: 'success', status: 'pending' },
      { id: 4, title: '已确认教案', parseStatus: 'success', status: 'confirmed' },
    ])
    const router = routerFor(LessonPlanHistoryView, '/lesson-plans/history')
    await router.push('/lesson-plans/history')
    await router.isReady()
    const wrapper = mount(LessonPlanHistoryView, { global: { plugins: [router], stubs: shellStub() } })
    await flushPromises()

    const actions = wrapper.findAll('[data-testid="lesson-plan-next-action"]')
    expect(actions.map((action) => action.text())).toEqual(['查看解析进度', '重新上传并解析', '确认解析内容', '设置课堂'])
    expect(actions.map((action) => action.attributes('href'))).toEqual([
      '/lesson-plans/1/parse-result',
      '/lesson-plans/upload?retryLessonPlanId=2',
      '/lesson-plans/3/parse-result',
      '/packages/generate?lessonPlanId=4',
    ])
  })
})
