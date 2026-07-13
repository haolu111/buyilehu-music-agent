<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppShell from '../components/AppShell.vue'
import LessonWorkspaceNav from '../components/LessonWorkspaceNav.vue'
import { packageApi } from '../api/packageApi'
import type { ProposalCard } from '../types'

const route = useRoute()
const router = useRouter()
const packageId = Number(route.params.packageId)
const proposal = ref<ProposalCard | null>(null)
const loading = ref(false)
const error = ref('')

const contentEntries = computed(() => {
  const lines = proposal.value?.content?.split(/\r?\n/).map(line => line.trim()).filter(Boolean) || []
  return lines.map((line) => {
    const separator = line.search(/[：:]/)
    return separator > 0
      ? { label: line.slice(0, separator).trim(), value: line.slice(separator + 1).trim() }
      : { label: '方案说明', value: line }
  })
})
const summaryEntries = computed(() => contentEntries.value.filter(entry => !/追踪|评分|request|trace/i.test(entry.label)).slice(0, 4))
const technicalEntries = computed(() => contentEntries.value.filter(entry => !summaryEntries.value.includes(entry)))
const statusText = computed(() => proposal.value?.confirmStatus === 'confirmed' ? '已确认' : '待确认')

function nodeTypeLabel(type: string) {
  const labels: Record<string, string> = {
    entry: '课堂导入', listening_activity: '听辨活动', rhythm_game: '节奏活动',
    meter_experience: '节拍体验', singing_practice: '演唱练习', creation_workshop: '音乐创编',
    melody_activity: '旋律活动', timbre_activity: '音色活动', form_activity: '曲式活动',
    instrument_activity: '虚拟乐器', ensemble_activity: '合奏活动', summary: '课堂总结',
  }
  return labels[type] || type.replace(/_/g, ' ')
}

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

onMounted(() => loadProposal().catch((err) => (error.value = err instanceof Error ? err.message : '方案加载失败')))
</script>

<template>
  <AppShell>
    <LessonWorkspaceNav />

    <header class="page-heading proposal-page-heading">
      <div>
        <p class="eyebrow">互动包生成 · 方案审核</p>
        <h1>确认课堂互动方案</h1>
        <p>检查活动顺序和教学依据，确认后即可进入互动包编辑。</p>
      </div>
      <button class="ghost" type="button" @click="router.push('/lesson-plans/history')">返回教案</button>
    </header>

    <p v-if="error" class="proposal-alert" role="alert">{{ error }}</p>
    <div v-if="!proposal && !error" class="proposal-loading" aria-label="正在加载方案">
      <span /><span /><span />
    </div>

    <div v-if="proposal" class="proposal-layout">
      <section class="proposal-decision">
        <div class="proposal-title-block">
          <div class="proposal-title-row">
            <span class="proposal-mark" aria-hidden="true">✓</span>
            <div>
              <span class="status-pill" :class="proposal.confirmStatus">{{ statusText }}</span>
              <h2>{{ proposal.title }}</h2>
            </div>
          </div>
          <p>版本 v{{ proposal.versionNo || 1 }} · {{ proposal.activityNodes.length }} 个课堂活动 · {{ proposal.components.length }} 个互动组件</p>
        </div>
        <div class="proposal-confirm-area">
          <span v-if="proposal.confirmStatus !== 'confirmed'">确认后仍可继续调整活动参数</span>
          <button class="primary proposal-confirm" :disabled="loading || proposal.confirmStatus === 'confirmed'" @click="confirm">
            {{ loading ? '正在确认…' : proposal.confirmStatus === 'confirmed' ? '方案已确认' : '确认并进入编辑' }}
          </button>
        </div>
      </section>

      <section class="proposal-brief" aria-labelledby="proposal-summary-title">
        <div class="proposal-section-heading">
          <div><span>01</span><div><h2 id="proposal-summary-title">方案摘要</h2><p>Agent 根据教案整理出的课堂设计结论</p></div></div>
          <span class="agent-badge">AI 生成建议</span>
        </div>
        <dl class="proposal-summary-list">
          <div v-for="entry in summaryEntries" :key="`${entry.label}-${entry.value}`">
            <dt>{{ entry.label }}</dt>
            <dd>{{ entry.value }}</dd>
          </div>
        </dl>
        <details v-if="technicalEntries.length" class="proposal-technical">
          <summary>查看生成详情</summary>
          <dl><div v-for="entry in technicalEntries" :key="`${entry.label}-${entry.value}`"><dt>{{ entry.label }}</dt><dd>{{ entry.value }}</dd></div></dl>
        </details>
      </section>

      <section class="proposal-flow" aria-labelledby="proposal-flow-title">
        <div class="proposal-section-heading">
          <div><span>02</span><div><h2 id="proposal-flow-title">课堂活动流程</h2><p>按课堂执行顺序检查每个互动环节</p></div></div>
          <strong>{{ proposal.activityNodes.length }} 个环节</strong>
        </div>
        <ol class="proposal-node-list">
          <li v-for="(node, index) in proposal.activityNodes" :key="node.id">
            <div class="proposal-node-index"><span>{{ String(index + 1).padStart(2, '0') }}</span></div>
            <div class="proposal-node-copy">
              <span>{{ nodeTypeLabel(node.nodeType) }}</span>
              <h3>{{ node.title }}</h3>
              <div v-if="node.components.length" class="proposal-component-tags">
                <span v-for="component in node.components" :key="component.id">{{ component.name || component.componentKey }}</span>
              </div>
            </div>
          </li>
        </ol>
      </section>

      <section class="proposal-evidence-grid">
        <article class="proposal-evidence" aria-labelledby="objectives-title">
          <div class="proposal-section-heading compact">
            <div><span>03</span><div><h2 id="objectives-title">教学目标</h2><p>本方案需要达成的学习结果</p></div></div>
          </div>
          <ol class="objective-list">
            <li v-for="(item, index) in proposal.teachingObjectives" :key="item"><span>{{ index + 1 }}</span><p>{{ item }}</p></li>
          </ol>
        </article>

        <article class="proposal-evidence" aria-labelledby="source-title">
          <div class="proposal-section-heading compact">
            <div><span>04</span><div><h2 id="source-title">教案依据</h2><p>生成活动时采用的原教案内容</p></div></div>
          </div>
          <ul class="source-section-list">
            <li v-for="item in proposal.sourceLessonSections" :key="item">{{ item }}</li>
          </ul>
        </article>
      </section>

      <section v-if="proposal.components.length" class="proposal-components">
        <div><h2>互动组件</h2><p>本方案将使用以下学生端能力</p></div>
        <div class="proposal-component-tags large"><span v-for="component in proposal.components" :key="component.id">{{ component.name || component.componentKey }}</span></div>
      </section>
    </div>
  </AppShell>
</template>
