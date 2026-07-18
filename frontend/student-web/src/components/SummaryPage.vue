<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  completedCount: number
  totalCount: number
}>()

const percentage = computed(() => props.totalCount ? Math.round((props.completedCount / props.totalCount) * 100) : 0)
const stars = computed(() => percentage.value >= 100 ? 3 : percentage.value >= 60 ? 2 : percentage.value > 0 ? 1 : 0)
const earnedStars = computed(() => props.completedCount * 3)
const encouragement = computed(() => percentage.value >= 100
  ? '太棒啦！你完成了今天所有的音乐挑战！'
  : percentage.value > 0 ? '每一次练习都让耳朵更灵敏，继续加油！' : '准备好了吗？一起开启今天的音乐冒险吧！')
</script>

<template>
  <section class="summary-page">
    <div class="summary-celebration" aria-hidden="true">
      <span v-for="index in 3" :key="index" :class="{ earned: index <= stars }">★</span>
    </div>
    <div class="summary-copy">
      <p class="summary-kicker">今日音乐课堂</p>
      <h2>课堂小结</h2>
      <p>{{ encouragement }}</p>
      <div class="summary-progress" aria-label="课堂完成进度">
        <div class="summary-progress-label"><span>闯关进度</span><strong>{{ completedCount }} / {{ totalCount }}</strong></div>
        <div class="progress-track"><span :style="{ width: `${percentage}%` }"></span></div>
      </div>
    </div>
    <div class="summary-score"><strong>{{ earnedStars }}</strong><span>本节星星</span></div>
  </section>
</template>
