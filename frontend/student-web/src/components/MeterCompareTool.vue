<script setup lang="ts">
import { computed, ref } from 'vue'

const selected = ref<'two' | 'three'>('two')

const beats = computed(() => (selected.value === 'two' ? [1, 2] : [1, 2, 3]))
</script>

<template>
  <section class="tool-panel">
    <div class="segmented" role="tablist" aria-label="拍号">
      <button :class="{ active: selected === 'two' }" type="button" @click="selected = 'two'">2/4</button>
      <button :class="{ active: selected === 'three' }" type="button" @click="selected = 'three'">3/4</button>
    </div>
    <div class="meter-lane" :class="selected">
      <span v-for="beat in beats" :key="beat" :class="{ strong: beat === 1 }">{{ beat }}</span>
    </div>
    <p class="tool-note">{{ selected === 'two' ? '强 弱' : '强 弱 弱' }}</p>
  </section>
</template>
