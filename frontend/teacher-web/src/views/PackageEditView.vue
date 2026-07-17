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

const route = useRoute()
const packageId = Number(route.params.packageId)
const proposal = ref<ProposalCard | null>(null)
const versions = ref<PackageVersion[]>([])
const selectedNodeId = ref<number | null>(null)
const loading = ref(false)
const message = ref('')
const error = ref('')
const draft = ref<PackageModifyPayload>({})

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
          <small>{{ node.nodeType }}</small>
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
        {{ component.name || component.componentKey }}
      </span>
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
