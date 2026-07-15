<script setup lang="ts">
import { reactive, watch } from 'vue'
import type { PackageModifyPayload } from '../types'

const props = defineProps<{
  initialTitle?: string
}>()

const emit = defineEmits<{
  save: [payload: PackageModifyPayload]
}>()

const form = reactive<PackageModifyPayload>({
  title: props.initialTitle || '',
  description: '',
  difficulty: 'normal',
  rhythmCardCount: 4,
  hintEnabled: true,
  hidden: false,
})

watch(
  () => props.initialTitle,
  (title) => {
    if (title) form.title = title
  },
)
</script>

<template>
  <form class="stack" @submit.prevent="emit('save', { ...form })">
    <label>
      活动标题
      <input v-model="form.title" maxlength="120" />
    </label>
    <label>
      活动说明
      <input v-model="form.description" maxlength="500" placeholder="给学生看的简短说明" />
    </label>
    <label>
      难度
      <select v-model="form.difficulty">
        <option value="easy">简单</option>
        <option value="normal">标准</option>
        <option value="hard">挑战</option>
      </select>
    </label>
    <label>
      节奏卡数量
      <input v-model.number="form.rhythmCardCount" min="0" type="number" />
    </label>
    <label class="inline-control">
      <input v-model="form.hintEnabled" type="checkbox" />
      开启提示
    </label>
    <label class="inline-control">
      <input v-model="form.hidden" type="checkbox" />
      隐藏该节点
    </label>
    <button class="primary" type="submit">保存并生成新版本</button>
  </form>
</template>