<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import AppShell from '../components/AppShell.vue'
import VersionHistoryPanel from '../components/VersionHistoryPanel.vue'
import ActivityNodeEditView from './ActivityNodeEditView.vue'
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
  if (!selectedNodeId.value) return
  loading.value = true
  message.value = ''
  error.value = ''
  try {
    const result = await packageApi.updateNodeConfig(packageId, selectedNodeId.value, payload)
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
    <div class="section-header">
      <div>
        <h1>互动包编辑</h1>
        <p class="lead">参数级修改会自动生成新版本</p>
      </div>
      <RouterLink class="button" :to="`/packages/${packageId}`">返回详情</RouterLink>
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

      <ActivityNodeEditView :proposal="proposal" :selected-node-id="selectedNodeId" @save="saveNode" />

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
  </AppShell>
</template>