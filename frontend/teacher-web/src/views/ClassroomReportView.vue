<script setup lang="ts">
import { useRoute } from 'vue-router'
import AppShell from '../components/AppShell.vue'

const route = useRoute()
const sessionId = route.params.sessionId
</script>

<template>
  <AppShell>
    <h1>课堂报告</h1>
    <section class="card">
      <p class="muted">课堂 Session：{{ sessionId }}</p>
      <div class="grid">
        <div class="stat"><strong>--</strong><span>参与学生</span></div>
        <div class="stat"><strong>--</strong><span>完成率</span></div>
        <div class="stat"><strong>--</strong><span>互动次数</span></div>
      </div>
      <p class="muted">等待后端课堂数据与报告接口实现后接入。</p>
    </section>
  </AppShell>
</template>
