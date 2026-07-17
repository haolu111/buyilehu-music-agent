<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { Send } from 'lucide-vue-next'
import { useRoute } from 'vue-router'
import AppShell from '../components/AppShell.vue'
import WorkflowStepper from '../components/WorkflowStepper.vue'
import VersionHistoryPanel from '../components/VersionHistoryPanel.vue'
import ActivityNodeEditView from './ActivityNodeEditView.vue'
import InteractivePackagePreview from '../components/InteractivePackagePreview.vue'
import { packageApi } from '../api/packageApi'
import type { PackageModifyPayload, PackageVersion, ProposalCard } from '../types'
import { componentDisplayName, nodeTypeDisplayName } from '../utils/presentationLabels'

const route = useRoute()
const packageId = Number(route.params.packageId)
const proposal = ref<ProposalCard | null>(null)
const versions = ref<PackageVersion[]>([])
const selectedNodeId = ref<number | null>(null)
const loading = ref(false)
const message = ref('')
const error = ref('')
const draft = ref<PackageModifyPayload>({})
const nodeFeedback = ref('')

const selectedNode = computed(() =>
  proposal.value?.activityNodes.find((node) => node.id === selectedNodeId.value) || null,
)

async function load() {
  loading.value = true
  error.value = ''
  try {
    proposal.value = await packageApi.getProposal(packageId)
    versions.value = await packageApi.listVersions(packageId)
    if (!selectedNodeId.value && proposal.value.activityNodes.length > 0) {
      selectedNodeId.value = proposal.value.activityNodes[0].id
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : '加载互动包失败'
  } finally {
    loading.value = false
  }
}

async function saveNode(payload: PackageModifyPayload) {
  const baseVersionId = proposal.value?.packageInfo?.currentVersionId
  if (!selectedNodeId.value || !baseVersionId) return
  loading.value = true
  message.value = ''
  error.value = ''
  try {
    const result = await packageApi.updateNodeConfig(packageId, selectedNodeId.value, baseVersionId, payload)
    message.value = `已生成 v${result.versionNo}`
    await load()
  } catch (err) {
    error.value = err instanceof Error ? err.message : '保存失败'
  } finally {
    loading.value = false
  }
}

async function reviseSelectedNode() {
  const baseVersionId = proposal.value?.packageInfo?.currentVersionId
  const feedback = nodeFeedback.value.trim()
  if (!selectedNodeId.value || !baseVersionId || !feedback) return
  loading.value = true
  message.value = ''
  error.value = ''
  try {
    const result = await packageApi.reviseNodeWithAgent(
      packageId, selectedNodeId.value, baseVersionId, feedback,
    )
    message.value = `Agent 已只修改当前节点，并生成 v${result.versionNo}`
    nodeFeedback.value = ''
    await load()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Agent 修改节点失败'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <AppShell>
    <WorkflowStepper current-stage="edit-package" :package-id="packageId" />
    <div class="section-header">
      <div>
        <p class="eyebrow">第 5 步 · 编辑互动包</p>
        <h1>互动包编辑</h1>
        <p class="lead">参数级修改会自动生成新版本</p>
      </div>
      <div class="button-row">
        <RouterLink class="button" :to="`/packages/${packageId}`">返回详情</RouterLink>
        <RouterLink class="button primary" data-testid="publish-classroom-next" :to="`/packages/${packageId}/publish`"><Send :size="18" aria-hidden="true" /> 发布到班级</RouterLink>
      </div>
    </div>

    <p v-if="message" class="tag">{{ message }}</p>
    <p v-if="error" class="error">{{ error }}</p>

    <section class="edit-layout">
      <div class="card stack">
        <h2>活动节点</h2>
        <button
          v-for="node in proposal?.activityNodes || []"
          :key="node.id"
          type="button"
          class="node-select"
          :class="{ active: node.id === selectedNodeId }"
          @click="selectedNodeId = node.id"
        >
          <span>{{ node.sortOrder }}</span>
          <strong>{{ node.title }}</strong>
          <small>{{ nodeTypeDisplayName(node.nodeType) }}</small>
        </button>
      </div>

      <ActivityNodeEditView
        :proposal="proposal"
        :selected-node-id="selectedNodeId"
        @save="saveNode"
        @change="draft = $event"
      />

      <VersionHistoryPanel :versions="versions" />
    </section>

    <section v-if="selectedNode" class="card stack">
      <h2>当前节点预览</h2>
      <p><strong>{{ selectedNode.title }}</strong></p>
      <p class="muted">组件数量：{{ selectedNode.components.length }}</p>
      <span v-for="component in selectedNode.components" :key="component.id" class="tag">
        {{ componentDisplayName(component.name, component.componentKey) }}
      </span>
      <div class="agent-node-revision">
        <div>
          <p class="eyebrow">节点修改建议</p>
          <h3>让 Agent 只修改“{{ selectedNode.title }}”</h3>
          <p class="muted">其他活动节点及其顺序保持不变。请具体说明难度、时长、活动方式或提示策略。</p>
        </div>
        <textarea
          v-model="nodeFeedback"
          data-testid="node-agent-feedback"
          maxlength="2000"
          rows="4"
          placeholder="例如：这个活动对三年级偏难，请保留活动目标，把节奏卡数量降到 4，并增加一次教师示范提示。"
        />
        <div class="button-row">
          <small class="muted">{{ nodeFeedback.length }} / 2000</small>
          <button
            class="button primary"
            data-testid="revise-node-with-agent"
            type="button"
            :disabled="loading || !nodeFeedback.trim()"
            @click="reviseSelectedNode"
          >
            {{ loading ? 'Agent 修改中…' : '提交建议并修改当前节点' }}
          </button>
        </div>
      </div>
    </section>
    <section v-if="selectedNode && proposal" class="card stack live-preview-panel">
      <div>
        <p class="eyebrow">实时预览</p>
        <h2>修改后的学生端效果</h2>
        <p class="muted">参数变化会立即显示；点击保存后才会生成新版本。</p>
      </div>
      <InteractivePackagePreview
        :nodes="proposal.activityNodes"
        :selected-node-id="selectedNodeId"
        :draft="draft"
        mode="single"
      />
    </section>
  </AppShell>
</template>
