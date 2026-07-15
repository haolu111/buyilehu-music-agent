<script setup lang="ts">
import CreationPanel from './CreationPanel.vue'
import EnsembleRoles from './EnsembleRoles.vue'
import FormOrdering from './FormOrdering.vue'
import ListeningChoice from './ListeningChoice.vue'
import MelodyTrace from './MelodyTrace.vue'
import MeterCompareTool from './MeterCompareTool.vue'
import RhythmDragGame from './RhythmDragGame.vue'
import SingingPractice from './SingingPractice.vue'
import SolfegeSorting from './SolfegeSorting.vue'
import SummaryPage from './SummaryPage.vue'
import TimbreMatch from './TimbreMatch.vue'
import VirtualInstrument from './VirtualInstrument.vue'
import type { ActivityRuntimeConfig } from '../types'

const props = defineProps<{ runtime?: ActivityRuntimeConfig | null; fallbackRenderer: ActivityRuntimeConfig['renderer']; completedCount: number; totalCount: number }>()
const emit = defineEmits<{ completed: [payload: { result: Record<string, unknown> }] }>()
function runtimeProps(): Record<string, any> { return props.runtime?.props || {} }
</script>

<template>
  <MeterCompareTool v-if="(runtime?.renderer || fallbackRenderer) === 'meter-compare'" :meters="runtimeProps().meters" />
  <RhythmDragGame v-else-if="(runtime?.renderer || fallbackRenderer) === 'rhythm-drag'" :cards="runtimeProps().cards" :max-beats="runtimeProps().maxBeats" @completed="emit('completed', { result: { sequence: $event.sequence } })" />
  <CreationPanel v-else-if="(runtime?.renderer || fallbackRenderer) === 'creation-panel'" :default-title="runtimeProps().defaultTitle" :prompt="runtimeProps().prompt" @submitted="emit('completed', { result: $event })" />
  <SingingPractice v-else-if="(runtime?.renderer || fallbackRenderer) === 'singing-practice'" v-bind="runtimeProps()" @completed="emit('completed', $event)" />
  <ListeningChoice v-else-if="(runtime?.renderer || fallbackRenderer) === 'listening-choice'" v-bind="runtimeProps()" @completed="emit('completed', $event)" />
  <SolfegeSorting v-else-if="(runtime?.renderer || fallbackRenderer) === 'solfege-sort'" v-bind="runtimeProps()" @completed="emit('completed', $event)" />
  <MelodyTrace v-else-if="(runtime?.renderer || fallbackRenderer) === 'melody-trace'" v-bind="runtimeProps()" @completed="emit('completed', $event)" />
  <TimbreMatch v-else-if="(runtime?.renderer || fallbackRenderer) === 'timbre-match'" v-bind="runtimeProps()" @completed="emit('completed', $event)" />
  <FormOrdering v-else-if="(runtime?.renderer || fallbackRenderer) === 'form-order'" v-bind="runtimeProps()" @completed="emit('completed', $event)" />
  <VirtualInstrument v-else-if="(runtime?.renderer || fallbackRenderer) === 'virtual-instrument'" v-bind="runtimeProps()" @completed="emit('completed', $event)" />
  <EnsembleRoles v-else-if="(runtime?.renderer || fallbackRenderer) === 'ensemble-roles'" v-bind="runtimeProps()" @completed="emit('completed', $event)" />
  <SummaryPage v-else-if="(runtime?.renderer || fallbackRenderer) === 'summary'" :completed-count="completedCount" :total-count="totalCount" />
  <section v-else class="tool-panel"><p>当前活动没有可用的学生端交互组件，请返回课堂并联系老师。</p></section>
</template>
