<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppShell from '../components/AppShell.vue'
import { packageApi } from '../api/packageApi'
import type { ProposalCard } from '../types'

const route = useRoute()
const router = useRouter()
const packageId = Number(route.params.packageId)
const proposal = ref<ProposalCard | null>(null)
const loading = ref(false)
const error = ref('')

async function loadProposal() {
  proposal.value = await packageApi.getProposal(packageId)
}

async function confirm() {
  loading.value = true
  error.value = ''
  try {
    proposal.value = await packageApi.confirmProposal(packageId)
    await router.push(`/packages/${packageId}`)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '确认方案卡失败'
  } finally {
    loading.value = false
  }
}

onMounted(() => loadProposal().catch((err) => (error.value = err.message)))
</script>

<template>
  <AppShell>
    <h1>方案卡确认</h1>
    <p v-if="error" class="error">{{ error }}</p>
    <div v-if="proposal" class="stack">
      <section class="card">
        <div class="section-header">
          <div>
            <h2>{{ proposal.title }}</h2>
            <p class="muted">确认状态：{{ proposal.confirmStatus }} / 版本：v{{ proposal.versionNo }}</p>
          </div>
          <button class="primary" :disabled="loading || proposal.confirmStatus === 'confirmed'" @click="confirm">
            {{ proposal.confirmStatus === 'confirmed' ? '已确认' : '确认方案卡' }}
          </button>
        </div>
        <pre>{{ proposal.content }}</pre>
      </section>

      <section class="grid two">
        <div class="card">
          <h3>教学目标</h3>
          <ul>
            <li v-for="item in proposal.teachingObjectives" :key="item">{{ item }}</li>
          </ul>
        </div>
        <div class="card">
          <h3>来源教案环节</h3>
          <ul>
            <li v-for="item in proposal.sourceLessonSections" :key="item">{{ item }}</li>
          </ul>
        </div>
      </section>

      <section class="card">
        <h3>活动节点</h3>
        <div class="timeline">
          <article v-for="node in proposal.activityNodes" :key="node.id" class="node">
            <strong>{{ node.sortOrder }}. {{ node.title }}</strong>
            <p class="muted">{{ node.nodeType }}</p>
            <span v-for="component in node.components" :key="component.id" class="tag">{{ component.componentKey }}</span>
          </article>
        </div>
      </section>

      <section class="card">
        <h3>组件清单</h3>
        <span v-for="component in proposal.components" :key="component.id" class="tag">{{ component.componentKey }}</span>
      </section>
    </div>
  </AppShell>
</template>
