<script setup lang="ts">
import { computed, ref } from 'vue'
import { playMeter } from '../utils/activitySound'

const props = withDefaults(defineProps<{ meters?: string[] }>(), { meters: () => ['2/4', '3/4'] })
const selected = ref(props.meters[0] || '2/4')
const beats = computed(() => Array.from({ length: Number(selected.value.split('/')[0]) || 2 }, (_, index) => index + 1))
</script>

<template>
  <section class="tool-panel">
    <div class="segmented" role="tablist" aria-label="选择拍号">
      <button v-for="meter in props.meters" :key="meter" :class="{ active: selected === meter }" type="button" @click="selected = meter">{{ meter }}</button>
    </div>
    <div class="meter-lane" :style="{ gridTemplateColumns: `repeat(${beats.length}, 1fr)` }">
      <span v-for="beat in beats" :key="beat" :class="{ strong: beat === 1 }">{{ beat }}</span>
    </div>
    <p class="tool-note">{{ beats.map((beat) => beat === 1 ? '强' : '弱').join(' · ') }}</p>
    <button class="secondary-action" type="button" @click="playMeter(beats.length)">试听节拍</button>
  </section>
</template>
