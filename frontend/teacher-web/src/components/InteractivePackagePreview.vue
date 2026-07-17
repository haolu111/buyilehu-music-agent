<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { PackageModifyPayload, ProposalCard } from '../types'

type PreviewNode = ProposalCard['activityNodes'][number]
type Runtime = {
  schemaVersion?: string
  nodeType?: string
  family?: string
  variant?: string
  renderer?: string
  props?: Record<string, any>
}

const props = defineProps<{
  nodes: PreviewNode[]
  selectedNodeId?: number | null
  draft?: PackageModifyPayload
  mode?: 'single' | 'package'
}>()

const emit = defineEmits<{ select: [nodeId: number] }>()
const previewIndex = ref(0)
const testResult = ref('')
const sequence = ref<string[]>([])

const visibleNodes = computed(() => props.nodes.filter((node) => !parseConfig(node).hidden))
const activeNode = computed(() => {
  if (props.mode === 'single' && props.selectedNodeId) {
    return props.nodes.find((node) => node.id === props.selectedNodeId) || null
  }
  return visibleNodes.value[previewIndex.value] || null
})
const runtime = computed<Runtime>(() => parseConfig(activeNode.value).activityRuntime || {})
const runtimeProps = computed(() => runtime.value.props || {})
const displayTitle = computed(() =>
  activeNode.value?.id === props.selectedNodeId && props.draft?.title
    ? props.draft.title
    : activeNode.value?.title || '未选择节点',
)
const displayPrompt = computed(() =>
  activeNode.value?.id === props.selectedNodeId && props.draft?.description
    ? props.draft.description
    : runtimeProps.value.prompt || '按要求完成当前音乐活动。',
)
const renderer = computed(() => runtime.value.renderer || fallbackRenderer(activeNode.value?.nodeType || ''))
const rhythmCount = computed(() =>
  activeNode.value?.id === props.selectedNodeId && props.draft?.rhythmCardCount != null
    ? props.draft.rhythmCardCount
    : runtimeProps.value.maxBeats || 4,
)

watch(activeNode, () => resetTest())

function parseConfig(node?: PreviewNode | null): Record<string, any> {
  if (!node?.configJson) return {}
  try { return JSON.parse(node.configJson) } catch { return {} }
}
function fallbackRenderer(type: string) {
  if (type.includes('summary')) return 'summary'
  if (type.includes('creation')) return 'creation-panel'
  if (type === 'instrument_task' || type.includes('instrument')) return 'virtual-instrument'
  if (type === 'game' || type.includes('rhythm')) return 'rhythm-drag'
  if (type.includes('singing')) return 'singing-practice'
  return 'completion'
}
function resetTest() { testResult.value = ''; sequence.value = [] }
function choose(value: string) { testResult.value = `已选择：${value}` }
function add(value: string) { sequence.value.push(value); testResult.value = `当前序列：${sequence.value.join(' · ')}` }
function previous() { previewIndex.value = Math.max(0, previewIndex.value - 1) }
function next() { previewIndex.value = Math.min(visibleNodes.value.length - 1, previewIndex.value + 1) }
</script>

<template>
  <section class="package-preview">
    <header class="preview-toolbar">
      <div>
        <span class="tag">教师测试模式 · 不记录学生成绩</span>
        <h2>{{ displayTitle }}</h2>
        <p>{{ displayPrompt }}</p>
      </div>
      <button class="button" type="button" @click="resetTest">重置试玩</button>
    </header>

    <div v-if="mode === 'package'" class="preview-flow">
      <button
        v-for="(node, index) in visibleNodes"
        :key="node.id"
        type="button"
        :class="{ active: index === previewIndex }"
        @click="previewIndex = index; emit('select', node.id)"
      >
        <span>{{ index + 1 }}</span>{{ node.title }}
      </button>
    </div>

    <div v-if="activeNode" class="preview-device">
      <div class="preview-meta">
        <span>{{ runtime.nodeType || activeNode.nodeType }}</span>
        <span v-if="runtime.family">{{ runtime.family }} / {{ runtime.variant }}</span>
        <span>{{ renderer }}</span>
      </div>

      <div v-if="renderer === 'rhythm-drag'" class="preview-interaction">
        <p>点击节奏卡，模拟学生完成节奏任务：</p>
        <div class="preview-buttons">
          <button v-for="card in ['ta', 'ti-ti', 'rest']" :key="card" type="button" @click="add(card)">{{ card }}</button>
        </div>
        <small>目标长度：{{ rhythmCount }} 拍</small>
      </div>

      <div v-else-if="renderer === 'virtual-instrument'" class="preview-interaction">
        <p>点击演奏区测试虚拟乐器任务：</p>
        <div class="preview-piano">
          <button v-for="key in runtimeProps.keys || [{ label: 'do' }, { label: 're' }, { label: 'mi' }, { label: 'sol' }]" :key="key.label" type="button" @click="add(key.label)">{{ key.label }}</button>
        </div>
      </div>

      <div v-else-if="renderer === 'listening-choice' || renderer === 'timbre-match'" class="preview-interaction">
        <p>模拟聆听后选择：</p>
        <div class="preview-buttons">
          <button v-for="option in runtimeProps.options || ['欢快', '安静', '优美']" :key="option" type="button" @click="choose(option)">{{ option }}</button>
        </div>
      </div>

      <div v-else-if="renderer === 'singing-practice'" class="preview-interaction">
        <p v-for="phrase in runtimeProps.phrases || ['第一乐句', '第二乐句']" :key="phrase">♪ {{ phrase }}</p>
        <button class="button primary" type="button" @click="testResult = '已模拟完成一次跟唱录音'">模拟录音</button>
      </div>

      <div v-else-if="renderer === 'creation-panel'" class="preview-interaction">
        <textarea :placeholder="runtimeProps.defaultTitle || '输入学生创编内容'"></textarea>
        <button class="button primary" type="button" @click="testResult = '创编内容可正常提交'">测试提交</button>
      </div>

      <div v-else class="preview-interaction">
        <p>该节点将以“{{ renderer }}”形式呈现。</p>
        <button class="button primary" type="button" @click="testResult = '节点完成操作正常'">模拟完成</button>
      </div>

      <p v-if="testResult" class="preview-result">{{ testResult }}</p>
    </div>

    <footer v-if="mode === 'package'" class="preview-navigation">
      <button class="button" type="button" :disabled="previewIndex === 0" @click="previous">上一个环节</button>
      <span>{{ previewIndex + 1 }} / {{ visibleNodes.length }}</span>
      <button class="button primary" type="button" :disabled="previewIndex >= visibleNodes.length - 1" @click="next">下一个环节</button>
    </footer>
  </section>
</template>
