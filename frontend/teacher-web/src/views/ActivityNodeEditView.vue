<script setup lang="ts">
import { computed } from 'vue'
import ActivityNodeConfigForm from '../components/ActivityNodeConfigForm.vue'
import ComponentParamEditor from '../components/ComponentParamEditor.vue'
import MusicContentEditor from '../components/MusicContentEditor.vue'
import type { PackageModifyPayload, ProposalCard } from '../types'

const props = defineProps<{
  proposal: ProposalCard | null
  selectedNodeId: number | null
}>()

const emit = defineEmits<{
  save: [payload: PackageModifyPayload]
  change: [payload: PackageModifyPayload]
}>()

let componentParams: Record<string, unknown> = {}
let formPayload: PackageModifyPayload = {}
let musicPayload: PackageModifyPayload = {}

const initialMusicContent = computed(() => {
  const node = props.proposal?.activityNodes.find((item) => item.id === props.selectedNodeId)
  if (!node?.configJson) return {}
  try {
    return JSON.parse(node.configJson).musicContent || {}
  } catch {
    return {}
  }
})

function save(payload: PackageModifyPayload) {
  emit('save', { ...payload, ...musicPayload, componentParams })
}

function preview(payload: PackageModifyPayload) {
  formPayload = { ...formPayload, ...payload }
  emit('change', { ...formPayload, ...musicPayload, componentParams })
}

function updateMusic(payload: PackageModifyPayload) {
  musicPayload = payload
  emit('change', { ...formPayload, ...musicPayload, componentParams })
}
</script>

<template>
  <section class="card stack">
    <template v-if="proposal && selectedNodeId">
      <h2>节点参数</h2>
      <ActivityNodeConfigForm
        :initial-title="proposal.activityNodes.find((node) => node.id === selectedNodeId)?.title"
        @save="save"
        @change="preview"
      />
      <div class="sub-panel">
        <h3>组件参数</h3>
        <ComponentParamEditor @change="componentParams = $event; preview({})" />
      </div>
      <MusicContentEditor :initial="initialMusicContent" @change="updateMusic" />
    </template>
    <p v-else class="muted">请选择左侧活动节点</p>
  </section>
</template>
