<script setup lang="ts">
import { reactive, watch } from 'vue'

type Option = { id: string; label: string; resolved: Record<string, unknown> }
const props = defineProps<{ initial?: Record<string, any> }>()
const emit = defineEmits<{
  change: [payload: { musicContent: Record<string, unknown>; resolvedMusicContent: Record<string, unknown> }]
}>()

const catalog: Record<string, Option[]> = {
  rhythm_pattern_ids: [
    { id: 'rhythm_ta_ta', label: '四分音符 × 2', resolved: { tokens: ['ta', 'ta'], beats: 2 } },
    { id: 'rhythm_titi_ta', label: '八分音符组 + 四分音符', resolved: { tokens: ['ti-ti', 'ta'], beats: 2 } },
    { id: 'rhythm_ta_rest', label: '四分音符 + 四分休止', resolved: { tokens: ['ta', 'rest'], beats: 2 } },
    { id: 'rhythm_syncopation', label: '切分节奏', resolved: { tokens: ['ti', 'ta-a', 'ti'], beats: 2 } },
  ],
  pitch_set_ids: [
    { id: 'pitch_do_re_mi', label: 'do re mi', resolved: { notes: ['do', 're', 'mi'] } },
    { id: 'pitch_do_re_mi_sol_la', label: '五声音阶 do re mi sol la', resolved: { notes: ['do', 're', 'mi', 'sol', 'la'] } },
    { id: 'pitch_diatonic', label: '七声音阶', resolved: { notes: ['do', 're', 'mi', 'fa', 'sol', 'la', 'ti'] } },
  ],
  melody_phrase_ids: [
    { id: 'melody_step_up', label: '级进上行', resolved: { notes: ['do', 're', 'mi', 'sol'], contour: ['same', 'up', 'up', 'up'] } },
    { id: 'melody_step_down', label: '级进下行', resolved: { notes: ['sol', 'mi', 're', 'do'], contour: ['same', 'down', 'down', 'down'] } },
    { id: 'melody_arch', label: '拱形旋律', resolved: { notes: ['do', 'mi', 'sol', 'mi', 'do'], contour: ['same', 'up', 'up', 'down', 'down'] } },
  ],
  form_ids: [
    { id: 'form_ab', label: '二段体 AB', resolved: { sections: ['A', 'B'] } },
    { id: 'form_aba', label: '三段体 ABA', resolved: { sections: ['A', 'B', 'A'] } },
    { id: 'form_aaba', label: 'AABA', resolved: { sections: ['A', 'A', 'B', 'A'] } },
    { id: 'form_rondo', label: '回旋曲式 ABACA', resolved: { sections: ['A', 'B', 'A', 'C', 'A'] } },
  ],
  dynamic_ids: [
    { id: 'dynamic_p', label: '弱 p', resolved: { symbol: 'p', gain: .35 } },
    { id: 'dynamic_mp', label: '中弱 mp', resolved: { symbol: 'mp', gain: .5 } },
    { id: 'dynamic_mf', label: '中强 mf', resolved: { symbol: 'mf', gain: .68 } },
    { id: 'dynamic_f', label: '强 f', resolved: { symbol: 'f', gain: .86 } },
    { id: 'dynamic_crescendo', label: '渐强', resolved: { symbol: '<', curve: 'crescendo' } },
    { id: 'dynamic_diminuendo', label: '渐弱', resolved: { symbol: '>', curve: 'diminuendo' } },
  ],
  timbre_ids: [
    { id: 'timbre_piano', label: '钢琴', resolved: { instrument: 'acoustic_grand_piano', family: '键盘乐器' } },
    { id: 'timbre_xylophone', label: '木琴', resolved: { instrument: 'xylophone', family: '打击乐器' } },
    { id: 'timbre_flute', label: '长笛', resolved: { instrument: 'flute', family: '木管乐器' } },
    { id: 'timbre_violin', label: '小提琴', resolved: { instrument: 'violin', family: '弦乐器' } },
    { id: 'timbre_drum', label: '鼓', resolved: { instrument: 'taiko_drum', family: '打击乐器' } },
  ],
}
const selection = reactive<Record<string, string[]>>(
  Object.fromEntries(Object.keys(catalog).map((key) => [key, []])),
)
const resolvedKeys: Record<string, string> = {
  rhythm_pattern_ids: 'rhythm_patterns', pitch_set_ids: 'pitch_sets',
  melody_phrase_ids: 'melody_phrases', form_ids: 'forms',
  dynamic_ids: 'dynamics', timbre_ids: 'timbres',
}

watch(() => props.initial, (initial) => {
  for (const key of Object.keys(catalog)) {
    selection[key] = Array.isArray(initial?.[key]) ? [...initial![key]] : []
  }
}, { immediate: true, deep: true })

watch(selection, () => {
  const musicContent: Record<string, unknown> = {}
  const resolvedMusicContent: Record<string, unknown> = {}
  for (const [key, ids] of Object.entries(selection)) {
    if (!ids.length) continue
    musicContent[key] = [...ids]
    resolvedMusicContent[resolvedKeys[key]] = ids.map((id) => {
      const option = catalog[key].find((item) => item.id === id)!
      return { id, label: option.label, ...option.resolved }
    })
  }
  emit('change', { musicContent, resolvedMusicContent })
}, { deep: true, immediate: true })
</script>

<template>
  <section class="music-content-editor">
    <div>
      <h3>音乐要素替换</h3>
      <p class="muted">只替换活动中的音乐内容，不改变活动编号和正式活动组件。</p>
    </div>
    <label>节奏型<select v-model="selection.rhythm_pattern_ids" multiple><option v-for="item in catalog.rhythm_pattern_ids" :key="item.id" :value="item.id">{{ item.label }}</option></select></label>
    <label>音高集合<select v-model="selection.pitch_set_ids" multiple><option v-for="item in catalog.pitch_set_ids" :key="item.id" :value="item.id">{{ item.label }}</option></select></label>
    <label>旋律片段<select v-model="selection.melody_phrase_ids" multiple><option v-for="item in catalog.melody_phrase_ids" :key="item.id" :value="item.id">{{ item.label }}</option></select></label>
    <label>曲式<select v-model="selection.form_ids" multiple><option v-for="item in catalog.form_ids" :key="item.id" :value="item.id">{{ item.label }}</option></select></label>
    <label>力度<select v-model="selection.dynamic_ids" multiple><option v-for="item in catalog.dynamic_ids" :key="item.id" :value="item.id">{{ item.label }}</option></select></label>
    <label>音色<select v-model="selection.timbre_ids" multiple><option v-for="item in catalog.timbre_ids" :key="item.id" :value="item.id">{{ item.label }}</option></select></label>
  </section>
</template>
