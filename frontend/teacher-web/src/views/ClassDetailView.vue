<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import AppShell from '../components/AppShell.vue'
import { classApi } from '../api/classApi'
import type { ClassInfo, UserInfo } from '../types'

const route = useRoute()
const students = ref<UserInfo[]>([])
const classInfo = ref<ClassInfo | null>(null)
const loading = ref(true)
const error = ref('')
const classId = Number(route.params.classId)

onMounted(async () => {
  try {
    const [studentData, classData] = await Promise.all([
      classApi.listStudents(classId),
      classApi.listClasses(),
    ])
    students.value = studentData
    classInfo.value = classData.find(item => item.id === classId) || null
  } catch (exception) {
    error.value = exception instanceof Error ? exception.message : '加载学生失败'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <AppShell>
    <div class="page-heading"><div><p class="breadcrumb">班级与学生 / 学生名单</p><h1>{{ classInfo?.className || '班级详情' }}</h1><p>共 {{ students.length }} 人</p></div><RouterLink class="button" to="/classes">返回班级列表</RouterLink></div>
    <p v-if="error" class="error">{{ error }}</p>
    <section class="table-card">
      <table class="data-table student-table"><thead><tr><th>学生</th><th>登录账号</th><th>身份</th><th>状态</th></tr></thead><tbody>
        <tr v-for="student in students" :key="student.id"><td><strong>{{ student.displayName || student.realName || student.username }}</strong></td><td>{{ student.username }}</td><td>学生</td><td><span class="status-pill active">正常</span></td></tr>
        <tr v-if="!students.length"><td colspan="4" class="empty-cell">{{ loading ? '正在加载学生名单…' : '暂无学生加入' }}</td></tr>
      </tbody></table>
    </section>
  </AppShell>
</template>
