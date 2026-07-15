<script setup lang="ts">
import ActivityNodeConfigForm from '../components/ActivityNodeConfigForm.vue'
import ComponentParamEditor from '../components/ComponentParamEditor.vue'
import type { PackageModifyPayload, ProposalCard } from '../types'

defineProps<{
  proposal: ProposalCard | null
  selectedNodeId: number | null
}>()

const emit = defineEmits<{
  save: [payload: PackageModifyPayload]
}>()

let componentParams: Record<string, unknown> = {}

function save(payload: PackageModifyPayload) {
  emit('save', { ...payload, componentParams })
}
</script>

<template>
  <section class="card stack">
    <template v-if="proposal && selectedNodeId">
      <h2>节点参数</h2>
      <ActivityNodeConfigForm
        :initial-title="proposal.activityNodes.find((node) => node.id === selectedNodeId)?.title"
        @save="save"
      />
      <div class="sub-panel">
        <h3>组件参数</h3>
        <ComponentParamEditor @change="componentParams = $event" />
      </div>
    </template>
    <p v-else class="muted">请选择左侧活动节点</p>
  </section>
</template>