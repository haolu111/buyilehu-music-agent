<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import AppShell from '../components/AppShell.vue'
import { classApi } from '../api/classApi'
import { statusText } from '../utils/display'
import type { ClassInfo } from '../types'

const classes = ref<ClassInfo[]>([])
const className = ref('')
const description = ref('')
const loading = ref(false)
const countsLoading = ref(false)
const error = ref('')
const query = ref('')
const showCreate = ref(false)
const copied = ref('')

const filtered = computed(() => classes.value.filter(item =>
  !query.value || item.className.toLowerCase().includes(query.value.toLowerCase()),
))

async function loadClasses() {
  countsLoading.value = true
  const classList = await classApi.listClasses()
  classes.value = classList

  const studentResults = await Promise.allSettled(
    classList.map(item => classApi.listStudents(item.id)),
  )
  classes.value = classList.map((item, index) => ({
    ...item,
    studentCount: studentResults[index].status === 'fulfilled'
      ? studentResults[index].value.length
      : item.studentCount,
  }))
  countsLoading.value = false
}

async function createClass() {
  if (!className.value.trim()) return
  loading.value = true
  error.value = ''
  try {
    await classApi.createClass(className.value, description.value)
    className.value = ''
    description.value = ''
    showCreate.value = false
    await loadClasses()
  } catch (exception) {
    error.value = exception instanceof Error ? exception.message : '创建班级失败'
  } finally {
    loading.value = false
  }
}

async function copyCode(code?: string) {
  if (!code) return
  await navigator.clipboard.writeText(code)
  copied.value = code
  window.setTimeout(() => copied.value = '', 1500)
}

onMounted(() => loadClasses().catch((exception: unknown) => {
  countsLoading.value = false
  error.value = exception instanceof Error ? exception.message : '加载班级失败'
}))
</script>

<template>
  <AppShell>
    <div class="page-heading">
      <div><p class="eyebrow">班级与学生</p><h1>班级管理</h1><p>查看学生、分享邀请码并管理正在使用的班级。</p></div>
      <button class="button primary" @click="showCreate = true">＋ 创建班级</button>
    </div>
    <div class="filter-bar"><input v-model="query" placeholder="搜索班级名称" aria-label="搜索班级"><select aria-label="按状态筛选"><option>全部状态</option><option>使用中</option></select></div>
    <p v-if="error" class="error">{{ error }}</p>
    <div class="class-grid">
      <article v-for="item in filtered" :key="item.id" class="card class-card-teacher">
        <div class="class-card-head">
          <div><span class="status-pill" :class="item.status">{{ statusText(item.status) }}</span><h2>{{ item.className }}</h2><p>{{ item.description || '暂无班级说明' }}</p></div>
          <span class="student-count-badge"><strong>{{ countsLoading && item.studentCount == null ? '同步中' : `${item.studentCount ?? 0} 人` }}</strong></span>
        </div>
        <div class="class-metrics"><span><small>学生人数</small><strong>{{ countsLoading && item.studentCount == null ? '同步中' : `${item.studentCount ?? 0} 人` }}</strong></span><span><small>邀请码</small><strong>{{ item.inviteCode || '生成中' }}</strong></span></div>
        <div class="class-actions"><button class="button" :disabled="!item.inviteCode" @click="copyCode(item.inviteCode)">{{ copied === item.inviteCode ? '已复制' : '复制邀请码' }}</button><RouterLink class="button primary-soft" :to="`/classes/${item.id}`">学生名单 →</RouterLink></div>
      </article>
      <div v-if="!filtered.length" class="empty-inline">还没有符合条件的班级</div>
    </div>
    <div v-if="showCreate" class="modal-backdrop" @click.self="showCreate = false"><section class="modal-panel" role="dialog" aria-modal="true" aria-labelledby="create-class-title"><div class="section-header"><div><p class="eyebrow">新班级</p><h2 id="create-class-title">创建班级</h2></div><button class="icon-button" aria-label="关闭" @click="showCreate = false">×</button></div><div class="stack"><label>班级名称<input v-model="className" placeholder="例如：一年级一班"></label><label>班级描述<textarea v-model="description" rows="4" placeholder="选填，可填写学年或教学说明"></textarea></label></div><div class="button-row end"><button class="button" @click="showCreate = false">取消</button><button class="button primary" :disabled="loading || !className.trim()" @click="createClass">{{ loading ? '创建中…' : '创建班级' }}</button></div></section></div>
  </AppShell>
</template>
