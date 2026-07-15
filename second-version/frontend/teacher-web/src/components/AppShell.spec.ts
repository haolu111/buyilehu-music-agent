import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import { describe, expect, it } from 'vitest'
import AppShell from './AppShell.vue'

describe('AppShell mobile navigation', () => {
  it('provides compact labels for every bottom navigation destination', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/dashboard', component: { template: '<div />' } },
        { path: '/classes', component: { template: '<div />' } },
        { path: '/lesson-plans/history', component: { template: '<div />' } },
        { path: '/classrooms', component: { template: '<div />' } },
        { path: '/reports', component: { template: '<div />' } },
      ],
    })
    await router.push('/dashboard')
    await router.isReady()

    const wrapper = mount(AppShell, { global: { plugins: [createPinia(), router] } })

    expect(wrapper.findAll('.nav-label-mobile').map((label) => label.text())).toEqual(['首页', '备课', '班级', '上课', '报告'])
    expect(wrapper.findAll('.nav-label-desktop').map((label) => label.text())).toEqual(['工作台', '教案与互动包', '班级与学生', '课堂教学', '数据报告'])
  })
})
