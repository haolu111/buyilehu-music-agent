<script setup lang="ts">
import { ref } from 'vue'
import RhythmCard from './RhythmCard.vue'
import { playRhythmPattern } from '../utils/activitySound'

const emit = defineEmits<{
  completed: [payload: { sequence: string[] }]
}>()

const props = withDefaults(defineProps<{
  cards?: Array<{ name: string; pattern: string }>
  maxBeats?: number
}>(), { cards: () => [
  { name: 'ta', pattern: 'X' },
  { name: 'ti-ti', pattern: 'X X' },
  { name: 'rest', pattern: '-' },
], maxBeats: 4 })

const selected = ref<string[]>([])

function addCard(name: string, pattern: string) {
  if (selected.value.length >= props.maxBeats) return
  playRhythmPattern(pattern || name)
  selected.value.push(name)
}

function removeCard(index: number) {
  selected.value.splice(index, 1)
}

function submit() {
  emit('completed', { sequence: selected.value })
}
</script>

<template>
  <section class="tool-panel rhythm-game">
    <div class="card-row">
      <RhythmCard
        v-for="card in props.cards"
        :key="card.name"
        :name="card.name"
        :pattern="card.pattern"
        @click="addCard(card.name, card.pattern)"
      />
    </div>

    <div class="drop-lane">
      <button
        v-for="(item, index) in selected"
        :key="`${item}-${index}`"
        type="button"
        class="beat-token"
        @click="removeCard(index)"
      >
        {{ item }}
      </button>
      <span v-for="slot in props.maxBeats - selected.length" :key="slot" class="empty-beat"></span>
    </div>

    <button class="primary-action" type="button" :disabled="selected.length === 0" @click="submit">
      提交
    </button>
  </section>
</template>
