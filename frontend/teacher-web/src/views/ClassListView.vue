<script setup lang="ts">
import { onMounted, ref } from 'vue'
import AppShell from '../components/AppShell.vue'
import { classApi } from '../api/classApi'
import type { ClassInfo } from '../types'

const classes = ref<ClassInfo[]>([])
const className = ref('')
const description = ref('')
const loading = ref(false)
const error = ref('')

async function loadClasses() {
  classes.value = await classApi.listClasses()
}

async function createClass() {
  if (!className.value.trim()) return
  loading.value = true
  error.value = ''
  try {
    await classApi.createClass(className.value, description.value)
    className.value = ''
    description.value = ''
    await loadClasses()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '创建班级失败'
  } finally {
    loading.value = false
  }
}

onMounted(() => loadClasses().catch((err) => (error.value = err.message)))
</script>

<template>
  <AppShell>
    <h1>班级管理</h1>
    <div class="card form-row">
      <input v-model="className" placeholder="班级名称，例如：三年级一班" />
      <input v-model="description" placeholder="班级描述，可选" />
      <button class="primary" :disabled="loading" @click="createClass">创建班级</button>
    </div>
    <p v-if="error" class="error">{{ error }}</p>
    <div class="list">
      <RouterLink v-for="item in classes" :key="item.id" class="card list-item" :to="`/classes/${item.id}`">
        <div>
          <strong>{{ item.className }}</strong>
          <p class="muted">邀请码：{{ item.inviteCode || '生成中' }} / 状态：{{ item.status || '-' }}</p>
        </div>
        <span>查看学生 →</span>
      </RouterLink>
    </div>
  </AppShell>
</template>
