<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import RhythmCard from './RhythmCard.vue'
import { playErrorSound, playRhythmPattern, playRhythmSequence, playSuccessSound } from '../utils/activitySound'

const emit = defineEmits<{ completed: [payload: { sequence: string[] }] }>()
const props = withDefaults(defineProps<{
  cards?: Array<{ name: string; pattern?: string }>
  maxBeats?: number
  targetSequence?: string[]
}>(), {
  cards: () => [
    { name: 'ta', pattern: 'X' },
    { name: 'ti-ti', pattern: 'X X' },
    { name: 'rest', pattern: '-' },
  ],
  maxBeats: 4,
  targetSequence: () => ['ta', 'ti-ti', 'ta', 'rest'],
})

type Result = 'correct' | 'wrong' | null
const selected = ref<string[]>([])
const submitted = ref(false)
const isPlaying = ref(false)
let playbackTimer: number | null = null

const target = computed(() => {
  const source = props.targetSequence?.length ? props.targetSequence : ['ta', 'ti-ti', 'ta', 'rest']
  return source.slice(0, props.maxBeats)
})
const results = computed<Result[]>(() =>
  selected.value.map((item, index) => submitted.value ? (item === target.value[index] ? 'correct' : 'wrong') : null),
)
const allCorrect = computed(() =>
  selected.value.length === target.value.length
  && selected.value.every((item, index) => item === target.value[index]),
)

watch(() => props.targetSequence, reset, { deep: true })

function label(token: string) {
  if (token === 'ta') return '♩ 四分音符（1拍）'
  if (token === 'ti-ti') return '♫ 两个八分音符（1拍）'
  if (token === 'rest') return '𝄽 四分休止（1拍）'
  return token
}
function playTarget() {
  if (isPlaying.value) return
  isPlaying.value = true
  playRhythmSequence(target.value)
  playbackTimer = window.setTimeout(() => { isPlaying.value = false }, target.value.length * 560 + 150)
}
function addCard(name: string, pattern = name) {
  if (selected.value.length >= target.value.length) return
  submitted.value = false
  playRhythmPattern(pattern)
  selected.value.push(name)
}
function removeCard(index: number) {
  submitted.value = false
  selected.value.splice(index, 1)
}
function undo() {
  submitted.value = false
  selected.value.pop()
}
function reset() {
  selected.value = []
  submitted.value = false
  isPlaying.value = false
  if (playbackTimer !== null) window.clearTimeout(playbackTimer)
}
function submit() {
  submitted.value = true
  if (allCorrect.value) {
    playSuccessSound()
    emit('completed', { sequence: [...selected.value] })
  } else {
    playErrorSound()
  }
}
</script>

<template>
  <section class="tool-panel rhythm-game">
    <header class="echo-header">
      <div>
        <span>节奏回声</span>
        <h3>先听目标节奏，再用节奏卡把它还原</h3>
      </div>
      <button class="listen-button" type="button" :disabled="isPlaying" @click="playTarget">
        {{ isPlaying ? '正在播放…' : '▶ 播放目标节奏' }}
      </button>
    </header>

    <p class="instruction">目标共 {{ target.length }} 拍。每张卡占1拍，请按听到的先后顺序点击。</p>
    <div class="card-row">
      <RhythmCard v-for="card in props.cards" :key="card.name"
        :name="label(card.name)" :pattern="card.pattern || card.name"
        @click="addCard(card.name, card.pattern)" />
    </div>

    <div class="progress-line">
      <strong>我的答案</strong>
      <span>已完成 {{ selected.length }} / {{ target.length }} 拍</span>
    </div>
    <div class="drop-lane" aria-label="我的节奏答案">
      <button v-for="(item, index) in selected" :key="`${item}-${index}`" type="button"
        class="beat-token" :class="results[index]" :title="`点击移除第${index + 1}拍`"
        @click="removeCard(index)">
        <small>第{{ index + 1 }}拍</small>{{ label(item) }}
      </button>
      <span v-for="slot in target.length - selected.length" :key="slot" class="empty-beat">
        第{{ selected.length + slot }}拍
      </span>
    </div>

    <p v-if="submitted" class="feedback" :class="{ success: allCorrect }">
      {{ allCorrect ? '完全正确！你准确还原了目标节奏。' : '还不完全正确：红色拍位需要修改。可以再听一次。' }}
    </p>
    <div class="actions">
      <button type="button" :disabled="!selected.length" @click="undo">撤销一拍</button>
      <button type="button" :disabled="!selected.length" @click="reset">清空</button>
      <button class="primary-action" type="button" :disabled="selected.length !== target.length" @click="submit">
        提交并检查
      </button>
    </div>
  </section>
</template>

<style scoped>
.rhythm-game{display:grid;gap:18px}.echo-header,.progress-line,.actions{display:flex;align-items:center;justify-content:space-between;gap:14px}.echo-header span{color:#a85f32;font-size:12px;font-weight:800}.echo-header h3{margin:4px 0 0;font-size:clamp(18px,2.4vw,26px)}.listen-button{padding:12px 18px;border:0;border-radius:12px;background:#147d6c;color:#fff;font-weight:800}.instruction{margin:0;color:#526c66}.drop-lane{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}.beat-token,.empty-beat{min-height:78px;padding:10px;border-radius:12px}.beat-token{border:2px solid #bdd5ce;background:#fff;color:#18302c}.beat-token small{display:block;margin-bottom:6px;color:#71857f}.beat-token.correct{border-color:#28a47e;background:#e9f8f1}.beat-token.wrong{border-color:#df6a5f;background:#fff0ed}.empty-beat{display:grid;place-items:center;border:2px dashed #c9d3d0;color:#8a9995}.feedback{margin:0;padding:12px;border-radius:10px;background:#fff0ed;color:#a33830}.feedback.success{background:#e8f7ef;color:#167458}.actions{justify-content:flex-end}.actions button{padding:10px 16px;border:1px solid #bdcbc7;border-radius:10px;background:#fff;font-weight:700}.actions .primary-action{border:0;background:#15977f;color:#fff}.actions button:disabled,.listen-button:disabled{opacity:.45}@media(max-width:700px){.echo-header{align-items:stretch;flex-direction:column}.drop-lane{grid-template-columns:repeat(2,1fr)}.actions{flex-wrap:wrap}.actions button{flex:1}}
</style>
