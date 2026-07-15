<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ArrowLeft, CheckCircle2, Pencil, Sparkles } from 'lucide-vue-next'
import { useRoute, useRouter } from 'vue-router'
import AppShell from '../components/AppShell.vue'
import LessonWorkspaceNav from '../components/LessonWorkspaceNav.vue'
import WorkflowStepper from '../components/WorkflowStepper.vue'
import { packageApi } from '../api/packageApi'
import type { ProposalCard } from '../types'

const route = useRoute()
const router = useRouter()
const packageId = Number(route.params.packageId)
const proposal = ref<ProposalCard | null>(null)
const loading = ref(false)
const error = ref('')
const contentEntries = computed(() => (proposal.value?.content?.split(/\r?\n/).map((line) => line.trim()).filter(Boolean) || []).map((line) => {
  const separator = line.search(/[：:]/)
  return separator > 0 ? { label: line.slice(0, separator).trim(), value: line.slice(separator + 1).trim() } : { label: '方案说明', value: line }
}))
const summaryEntries = computed(() => contentEntries.value.filter((entry) => !/追踪|评分|request|trace/i.test(entry.label)).slice(0, 4))
const technicalEntries = computed(() => contentEntries.value.filter((entry) => !summaryEntries.value.includes(entry)))
const isConfirmed = computed(() => proposal.value?.confirmStatus === 'confirmed')
const statusText = computed(() => isConfirmed.value ? '已确认' : '待确认')

function nodeTypeLabel(type: string) {
  const labels: Record<string, string> = { entry: '课堂导入', listening_activity: '听辨活动', rhythm_game: '节奏活动', meter_experience: '节拍体验', singing_practice: '演唱练习', creation_workshop: '音乐创编', melody_activity: '旋律活动', timbre_activity: '音色活动', form_activity: '曲式活动', instrument_activity: '虚拟乐器', ensemble_activity: '合奏活动', summary: '课堂总结' }
  return labels[type] || type.replace(/_/g, ' ')
}
async function loadProposal() { proposal.value = await packageApi.getProposal(packageId) }
async function confirm() {
  if (isConfirmed.value) return
  loading.value = true
  error.value = ''
  try {
    proposal.value = await packageApi.confirmProposal(packageId)
    await router.push(`/packages/${packageId}/edit`)
  } catch (err) {
    error.value = err instanceof Error ? err.message : '确认方案失败，请重试'
  } finally { loading.value = false }
}
function returnToSettings() {
  const lessonPlanId = proposal.value?.packageInfo?.lessonPlanId
  router.push(lessonPlanId ? `/packages/generate?lessonPlanId=${lessonPlanId}` : '/packages/generate')
}
onMounted(() => loadProposal().catch((err) => (error.value = err instanceof Error ? err.message : '方案加载失败')))
</script>

<template>
  <AppShell>
    <LessonWorkspaceNav />
    <WorkflowStepper current-stage="confirm-proposal" :package-id="packageId" />
    <header class="page-heading proposal-page-heading"><div><p class="eyebrow">第 4 步 · 确认方案</p><h1>确认课堂活动方案</h1><p>查看活动顺序，确认后进入编辑。</p></div></header>
    <p v-if="error" class="proposal-alert" role="alert">{{ error }}</p>
    <div v-if="!proposal && !error" class="proposal-loading" aria-label="正在加载方案"><span /><span /><span /></div>

    <div v-if="proposal" class="proposal-layout">
      <section class="proposal-decision">
        <div class="proposal-title-block"><div class="proposal-title-row"><CheckCircle2 class="proposal-mark" :size="24" aria-hidden="true" /><div><span class="status-pill" :class="proposal.confirmStatus">{{ statusText }}</span><h2>{{ proposal.title }}</h2></div></div><p>版本 v{{ proposal.versionNo || 1 }} · {{ proposal.activityNodes.length }} 个课堂活动 · {{ proposal.components.length }} 个互动组件</p></div>
        <div class="proposal-confirm-area">
          <RouterLink v-if="isConfirmed" class="button primary" :to="`/packages/${packageId}/edit`" data-testid="edit-confirmed-package"><Pencil :size="18" aria-hidden="true" /> 进入互动包编辑</RouterLink>
          <template v-else>
            <button class="button ghost" data-testid="back-to-classroom-settings" type="button" @click="returnToSettings"><ArrowLeft :size="18" aria-hidden="true" /> 返回调整</button>
            <button class="button primary proposal-confirm" data-testid="confirm-proposal" :disabled="loading" @click="confirm"><Sparkles :size="18" aria-hidden="true" /> {{ loading ? '正在确认…' : '确认方案，进入编辑' }}</button>
          </template>
        </div>
      </section>

      <section class="proposal-brief" aria-labelledby="proposal-summary-title"><div class="proposal-section-heading"><div><span>01</span><div><h2 id="proposal-summary-title">方案摘要</h2></div></div><span class="agent-badge">AI 生成建议</span></div><dl class="proposal-summary-list"><div v-for="entry in summaryEntries" :key="`${entry.label}-${entry.value}`"><dt>{{ entry.label }}</dt><dd>{{ entry.value }}</dd></div></dl><details v-if="technicalEntries.length" class="proposal-technical"><summary>查看技术详情</summary><dl><div v-for="entry in technicalEntries" :key="`${entry.label}-${entry.value}`"><dt>{{ entry.label }}</dt><dd>{{ entry.value }}</dd></div></dl></details></section>

      <section class="proposal-flow" aria-labelledby="proposal-flow-title"><div class="proposal-section-heading"><div><span>02</span><div><h2 id="proposal-flow-title">课堂活动顺序</h2></div></div><strong>{{ proposal.activityNodes.length }} 个环节</strong></div><ol class="proposal-node-list"><li v-for="(node, index) in proposal.activityNodes" :key="node.id"><div class="proposal-node-index"><span>{{ String(index + 1).padStart(2, '0') }}</span></div><div class="proposal-node-copy"><span>{{ nodeTypeLabel(node.nodeType) }}</span><h3>{{ node.title }}</h3><div v-if="node.components.length" class="proposal-component-tags"><span v-for="component in node.components" :key="component.id">{{ component.name || component.componentKey }}</span></div></div></li></ol></section>

      <section class="proposal-evidence-grid">
        <details class="proposal-evidence" data-testid="proposal-objectives"><summary><span>03</span> 教学目标</summary><ol class="objective-list"><li v-for="(item, index) in proposal.teachingObjectives" :key="item"><span>{{ index + 1 }}</span><p>{{ item }}</p></li></ol></details>
        <details class="proposal-evidence" data-testid="proposal-source"><summary><span>04</span> 教案依据</summary><ul class="source-section-list"><li v-for="item in proposal.sourceLessonSections" :key="item">{{ item }}</li></ul></details>
      </section>
      <section v-if="proposal.components.length" class="proposal-components"><div><h2>互动组件</h2></div><div class="proposal-component-tags large"><span v-for="component in proposal.components" :key="component.id">{{ component.name || component.componentKey }}</span></div></section>
    </div>
  </AppShell>
</template>
