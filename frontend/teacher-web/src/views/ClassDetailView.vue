<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import AppShell from '../components/AppShell.vue'
import { classApi } from '../api/classApi'
import type { UserInfo } from '../types'

const route = useRoute()
const students = ref<UserInfo[]>([])
const error = ref('')
const classId = Number(route.params.classId)

onMounted(async () => {
  try {
    students.value = await classApi.listStudents(classId)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载学生失败'
  }
})
</script>

<template>
  <AppShell>
    <h1>班级详情 #{{ classId }}</h1>
    <p v-if="error" class="error">{{ error }}</p>
    <div class="card">
      <h3>学生列表</h3>
      <p v-if="students.length === 0" class="muted">暂无学生加入。</p>
      <ul>
        <li v-for="student in students" :key="student.id">{{ student.username }} / {{ student.role }}</li>
      </ul>
    </div>
  </AppShell>
</template>
