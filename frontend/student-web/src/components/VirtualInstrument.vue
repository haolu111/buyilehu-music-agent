<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted } from 'vue'

interface InstrumentKey {
  note?: string
  label?: string
  zoneId?: string
  midi?: number
}

interface InstrumentTask {
  id?: string
  kind?: string
  bpm?: number
  instrumentId?: string
}

const props = withDefaults(defineProps<{
  prompt?: string
  keys?: InstrumentKey[]
  task?: InstrumentTask
  instrumentId?: string
  instrument?: { id?: string; instrumentId?: string }
  activityId?: string
}>(), {
  prompt: '直接点击乐器的演奏区域完成任务。',
  keys: () => [],
})

const emit = defineEmits<{
  completed: [payload: { result: Record<string, unknown> }]
}>()

const resolvedInstrumentId = computed(() => {
  if (props.instrumentId) return props.instrumentId
  if (props.task?.instrumentId) return props.task.instrumentId
  if (props.instrument?.id) return props.instrument.id
  if (props.instrument?.instrumentId) return props.instrument.instrumentId
  if (props.activityId === 'xylophone_creation') return 'virtual_xylophone'
  if (props.activityId && /melody|pitch|keyboard|piano/.test(props.activityId)) return 'virtual_piano'
  if (props.keys.some((key) => key.zoneId?.includes('center') || key.zoneId?.includes('edge'))) {
    return 'virtual_frame_drum'
  }
  if (props.keys.some((key) => typeof key.midi === 'number')) return 'virtual_piano'
  return 'virtual_frame_drum'
})

function encodeConfig(value: unknown): string {
  const bytes = new TextEncoder().encode(JSON.stringify(value))
  let binary = ''
  bytes.forEach((byte) => { binary += String.fromCharCode(byte) })
  return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
}

const playerUrl = computed(() => {
  const config = encodeConfig({
    instrumentId: resolvedInstrumentId.value,
    prompt: props.prompt,
    task: props.task,
  })
  return `/template-console/virtual-instrument-player.html?config=${encodeURIComponent(config)}`
})

function receiveMessage(event: MessageEvent) {
  if (event.origin !== location.origin) return
  const message = event.data
  if (!message || (
    message.type !== 'buyilehu:activity-completed'
    && message.type !== 'buyilehu:virtual-instrument-completed'
  )) return
  const result = message.result ?? message.payload?.result
  emit('completed', {
    result: result && typeof result === 'object' ? result : {},
  })
}

onMounted(() => window.addEventListener('message', receiveMessage))
onBeforeUnmount(() => window.removeEventListener('message', receiveMessage))
</script>

<template>
  <section class="instrument-runtime">
    <iframe
      :src="playerUrl"
      title="虚拟乐器演奏"
      allow="autoplay"
    />
  </section>
</template>

<style scoped>
.instrument-runtime{width:100%;min-height:min(760px,calc(100vh - 150px));overflow:hidden;border-radius:22px;background:#f2f6f3}
iframe{display:block;width:100%;height:min(760px,calc(100vh - 150px));min-height:620px;border:0;background:#f2f6f3}
@media(max-width:700px){.instrument-runtime,iframe{height:calc(100vh - 105px);min-height:560px;border-radius:14px}}
</style>
