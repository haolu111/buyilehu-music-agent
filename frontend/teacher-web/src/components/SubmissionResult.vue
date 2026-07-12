<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ value?: string; nodeType?: string }>()
const labels: Record<string, string> = {
  observed: '完成内容', sequence: '节奏组合', title: '作品名称', notes: '创作说明',
  answer: '学生答案', choice: '选择结果', difficulty: '活动难度',
}
const observedLabels: Record<string, string> = {
  entry: '已进入课堂', meter_experience: '完成节拍体验', rhythm: '完成节奏活动',
  summary: '已查看课堂小结', creation: '完成音乐创编',
}
const fields = computed(() => {
  if (!props.value) return []
  try {
    const parsed = JSON.parse(props.value)
    if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) return [{ label: '提交内容', value: String(parsed) }]
    return Object.entries(parsed).map(([key, value]) => ({
      label: labels[key] || '活动记录',
      value: key === 'observed' ? (observedLabels[String(value)] || '已完成活动') : Array.isArray(value) ? value.join('、') : typeof value === 'object' ? '已保存活动数据' : String(value),
    }))
  } catch { return [{ label: '提交内容', value: props.value }] }
})
</script>

<template>
  <div v-if="fields.length" class="submission-result">
    <span v-for="field in fields" :key="`${field.label}-${field.value}`"><small>{{ field.label }}</small><strong>{{ field.value }}</strong></span>
  </div>
  <span v-else class="muted">暂无提交内容</span>
</template>
