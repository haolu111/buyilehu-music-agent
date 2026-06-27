<script setup lang="ts">
import { useRoute } from 'vue-router'
import AppShell from '../components/AppShell.vue'

const route = useRoute()
const sessionId = route.params.sessionId
</script>

<template>
  <AppShell>
    <h1>课堂控制</h1>
    <section class="card stack">
      <p class="muted">课堂 Session：{{ sessionId }}</p>
      <p>这里预留教师上课控制台：开始节点、切换活动、查看学生进度、结束课堂。</p>
      <div class="button-row">
        <button>开始课堂</button>
        <button>下一活动</button>
        <RouterLink class="button primary" :to="`/classroom/${sessionId}/report`">查看报告</RouterLink>
      </div>
    </section>
  </AppShell>
</template>
