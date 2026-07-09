<script setup lang="ts">
defineProps<{
  completedCount: number
  totalCount: number
}>()
</script>

<template>
  <section class="summary-page">
    <div class="summary-ring">
      <strong>{{ completedCount }}</strong>
      <span>/ {{ totalCount }}</span>
    </div>
    <div>
      <h2>课堂小结</h2>
      <p>已完成的活动会同步到课堂记录中。</p>
    </div>
  </section>
</template>
