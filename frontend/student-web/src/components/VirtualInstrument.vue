<script setup lang="ts">
import { ref } from 'vue'

interface InstrumentKey {
  note: string
  label: string
  frequency: number
  color: string
  zoneId?: string
  midi?: number
}

interface InstrumentTask {
  id?: string
  kind?: string
  bpm?: number
}

const props = withDefaults(defineProps<{
  prompt?: string
  keys?: InstrumentKey[]
  task?: InstrumentTask
}>(), {
  prompt: '敲击乐器，完成音乐任务。',
  keys: () => [],
})

const emit = defineEmits<{
  completed: [payload: { result: Record<string, unknown> }]
}>()

const sequence = ref<string[]>([])
const events = ref<Array<{ timeMs: number; zoneId?: string; midi?: number }>>([])
let context: AudioContext | null = null
let startedAt = 0

function play(key: InstrumentKey) {
  context ||= new AudioContext()
  if (!startedAt) startedAt = performance.now()
  const oscillator = context.createOscillator()
  const gain = context.createGain()
  oscillator.frequency.value = key.frequency
  oscillator.type = 'sine'
  gain.gain.setValueAtTime(.24, context.currentTime)
  gain.gain.exponentialRampToValueAtTime(.001, context.currentTime + .55)
  oscillator.connect(gain).connect(context.destination)
  oscillator.start()
  oscillator.stop(context.currentTime + .55)
  sequence.value.push(key.note)
  events.value.push({
    timeMs: performance.now() - startedAt,
    zoneId: key.zoneId,
    midi: key.midi,
  })
}

function clear() {
  sequence.value = []
  events.value = []
  startedAt = 0
}

function submit() {
  emit('completed', {
    result: {
      notes: sequence.value,
      events: events.value,
      taskId: props.task?.id,
      taskKind: props.task?.kind,
    },
  })
}
</script>

<template>
  <section class="music-activity">
    <header>
      <span class="activity-kicker">虚拟乐器任务</span>
      <h2>{{ task?.kind || '乐器探索' }}</h2>
      <p>{{ prompt }}</p>
      <small v-if="task?.bpm">速度：{{ task.bpm }} BPM</small>
    </header>
    <div class="instrument-keys">
      <button
        v-for="key in keys"
        :key="key.note"
        type="button"
        :style="{ background: key.color }"
        @click="play(key)"
      >
        <strong>{{ key.label }}</strong>
        <small>{{ Math.round(key.frequency) }} Hz</small>
      </button>
    </div>
    <div class="played-notes">
      <span v-if="!sequence.length">点击上面的演奏区开始</span>
      <b v-for="(note, index) in sequence" :key="`${note}-${index}`">{{ note }}</b>
    </div>
    <div class="activity-actions">
      <button class="secondary-action" type="button" :disabled="!sequence.length" @click="clear">清空</button>
      <button class="primary-action" type="button" :disabled="!sequence.length" @click="submit">提交演奏记录</button>
    </div>
  </section>
</template>
