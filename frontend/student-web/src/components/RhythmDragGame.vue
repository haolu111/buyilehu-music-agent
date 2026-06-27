<script setup lang="ts">
import { computed, ref } from 'vue'
import RhythmCard from './RhythmCard.vue'

const emit = defineEmits<{
  completed: [payload: { sequence: string[]; score: number }]
}>()

const cards = [
  { name: 'ta', pattern: 'X' },
  { name: 'ti-ti', pattern: 'X X' },
  { name: 'rest', pattern: '-' },
]

const selected = ref<string[]>([])

const score = computed(() => Math.min(100, selected.value.length * 25))

function addCard(name: string) {
  if (selected.value.length >= 4) return
  selected.value.push(name)
}

function removeCard(index: number) {
  selected.value.splice(index, 1)
}

function submit() {
  emit('completed', { sequence: selected.value, score: score.value })
}
</script>

<template>
  <section class="tool-panel rhythm-game">
    <div class="card-row">
      <RhythmCard
        v-for="card in cards"
        :key="card.name"
        :name="card.name"
        :pattern="card.pattern"
        @click="addCard(card.name)"
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
      <span v-for="slot in 4 - selected.length" :key="slot" class="empty-beat"></span>
    </div>

    <button class="primary-action" type="button" :disabled="selected.length === 0" @click="submit">
      提交
    </button>
  </section>
</template>
