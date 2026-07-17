<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { PackageModifyPayload, ProposalCard } from '../types'
import { registerReviewedActivityElement } from '../../../shared-activity-runtime/reviewedActivityFrame'

type PreviewNode = ProposalCard['activityNodes'][number]
type Runtime = {
  nodeType?: string
  family?: string
  variant?: string
  renderer?: string
  legacyRenderer?: string
  componentUrl?: string
  props?: Record<string, any>
}

const props = defineProps<{
  nodes: PreviewNode[]
  selectedNodeId?: number | null
  draft?: PackageModifyPayload
  mode?: 'single' | 'package'
}>()
registerReviewedActivityElement()
const emit = defineEmits<{ select: [nodeId: number] }>()

const previewIndex = ref(0)
const testResult = ref('')
const sequence = ref<string[]>([])
const selectedRole = ref('')
const completedSteps = ref<string[]>([])
const explanation = ref('')
const rhythmSubmitted = ref(false)
const rhythmPlaying = ref(false)

const visibleNodes = computed(() => props.nodes.filter((node) => !parseConfig(node).hidden))
const activeNode = computed(() => {
  if (props.mode === 'single' && props.selectedNodeId) {
    return props.nodes.find((node) => node.id === props.selectedNodeId) || null
  }
  return visibleNodes.value[previewIndex.value] || null
})
const runtime = computed<Runtime>(() => parseConfig(activeNode.value).activityRuntime || {})
const nodeConfig = computed(() => parseConfig(activeNode.value))
const runtimeProps = computed(() => {
  const value = { ...(runtime.value.props || {}) }
  if (activeNode.value?.id !== props.selectedNodeId || !props.draft?.resolvedMusicContent) return value
  const content = props.draft.resolvedMusicContent as Record<string, any>
  value.musicContent = content
  if (content.rhythm_patterns?.length) {
    value.rhythmPatterns = content.rhythm_patterns
    value.targetSequence = content.rhythm_patterns.flatMap((item: any) => item.tokens || [])
  }
  if (content.pitch_sets?.length) {
    value.pitchSets = content.pitch_sets
    value.tokens = content.pitch_sets[0].notes || []
  }
  if (content.melody_phrases?.length) {
    value.melodyPhrases = content.melody_phrases
    value.notes = content.melody_phrases[0].contour || content.melody_phrases[0].notes || []
  }
  if (content.forms?.length) {
    value.forms = content.forms
    value.sections = content.forms[0].sections || []
  }
  if (content.dynamics?.length) value.dynamics = content.dynamics
  if (content.timbres?.length) {
    value.timbres = content.timbres
    value.items = content.timbres.map((item: any) => item.label)
    value.instrument = content.timbres[0].instrument
  }
  return value
})
const renderer = computed(() => runtime.value.renderer || fallbackRenderer(activeNode.value?.nodeType || ''))
const legacyRenderer = computed(() => runtime.value.legacyRenderer || renderer.value)
const displayTitle = computed(() =>
  activeNode.value?.id === props.selectedNodeId && props.draft?.title
    ? props.draft.title
    : activeNode.value?.title || '未选择活动',
)
const displayPrompt = computed(() => translateText(
  activeNode.value?.id === props.selectedNodeId && props.draft?.description
    ? props.draft.description
    : nodeConfig.value.recommendationReason || runtimeProps.value.prompt || defaultPrompt(renderer.value),
))
const rhythmCount = computed(() =>
  activeNode.value?.id === props.selectedNodeId && props.draft?.rhythmCardCount != null
    ? props.draft.rhythmCardCount
    : runtimeProps.value.maxBeats || 4,
)
const rhythmTarget = computed<string[]>(() => {
  const configured = runtimeProps.value.targetSequence
  const source = Array.isArray(configured) && configured.length
    ? configured.map(String)
    : ['ta', 'ti-ti', 'ta', 'rest']
  return source.slice(0, rhythmCount.value)
})
const rhythmCorrect = computed(() =>
  sequence.value.length === rhythmTarget.value.length
  && sequence.value.every((token, index) => token === rhythmTarget.value[index]),
)
const virtualInstrumentUrl = computed(() => {
  const task = runtimeProps.value.task || {}
  const keys = Array.isArray(runtimeProps.value.keys) ? runtimeProps.value.keys : []
  const instrumentId = runtimeProps.value.instrumentId
    || task.instrumentId
    || runtimeProps.value.instrument?.id
    || runtimeProps.value.instrument?.instrumentId
    || (runtimeProps.value.activityId === 'xylophone_creation' ? 'virtual_xylophone' : null)
    || (/melody|pitch|keyboard|piano/.test(String(runtimeProps.value.activityId || '')) ? 'virtual_piano' : null)
    || (keys.some((key: any) => String(key.zoneId || '').match(/center|edge/)) ? 'virtual_frame_drum' : null)
    || (keys.some((key: any) => Number.isFinite(key.midi)) ? 'virtual_piano' : null)
    || 'virtual_frame_drum'
  const bytes = new TextEncoder().encode(JSON.stringify({
    instrumentId,
    prompt: displayPrompt.value,
    task,
  }))
  let binary = ''
  bytes.forEach((byte) => { binary += String.fromCharCode(byte) })
  const encoded = btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
  return `/template-console/virtual-instrument-player.html?config=${encodeURIComponent(encoded)}`
})
const metaLabels = computed(() => [
  nodeTypeLabel(runtime.value.nodeType || activeNode.value?.nodeType || ''),
  runtime.value.family
    ? `${familyLabel(runtime.value.family)} · ${variantLabel(runtime.value.variant || '')}`
    : '',
  rendererLabel(renderer.value),
].filter(Boolean))

watch(activeNode, resetTest)

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
  if (type.includes('ensemble')) return 'ensemble-roles'
  return 'completion'
}
function resetTest() {
  testResult.value = ''
  sequence.value = []
  selectedRole.value = ''
  completedSteps.value = []
  explanation.value = ''
  rhythmSubmitted.value = false
  rhythmPlaying.value = false
}
function choose(value: unknown) { testResult.value = `已选择：${translateText(String(value))}` }
function add(value: unknown) {
  if (renderer.value === 'rhythm-drag' && sequence.value.length >= rhythmTarget.value.length) return
  rhythmSubmitted.value = false
  sequence.value.push(String(value))
  testResult.value = `当前结果：${sequence.value.map(translateText).join(' · ')}`
}
function rhythmLabel(value: string) {
  if (value === 'ta') return '♩ 四分音符（1拍）'
  if (value === 'ti-ti') return '♫ 两个八分音符（1拍）'
  if (value === 'rest') return '𝄽 四分休止（1拍）'
  return translateText(value)
}
function playRhythmTarget() {
  if (rhythmPlaying.value) return
  const AudioContextClass = window.AudioContext
  if (!AudioContextClass) return
  const context = new AudioContextClass()
  void context.resume()
  rhythmPlaying.value = true
  rhythmTarget.value.forEach((token, beatIndex) => {
    if (token === 'rest') return
    const hits = token === 'ti-ti' ? 2 : 1
    for (let hit = 0; hit < hits; hit += 1) {
      const start = context.currentTime + .05 + beatIndex * .56 + hit * .56 / hits
      const oscillator = context.createOscillator()
      const gain = context.createGain()
      oscillator.type = 'square'; oscillator.frequency.value = 196
      gain.gain.setValueAtTime(.14, start); gain.gain.exponentialRampToValueAtTime(.001, start + .09)
      oscillator.connect(gain).connect(context.destination); oscillator.start(start); oscillator.stop(start + .1)
    }
  })
  window.setTimeout(() => { rhythmPlaying.value = false; void context.close() }, rhythmTarget.value.length * 560 + 200)
}
function undoRhythm() { rhythmSubmitted.value = false; sequence.value.pop(); testResult.value = '' }
function clearRhythm() { rhythmSubmitted.value = false; sequence.value = []; testResult.value = '' }
function submitRhythm() {
  rhythmSubmitted.value = true
  testResult.value = rhythmCorrect.value
    ? '完全正确！已准确还原目标节奏。'
    : '还不完全正确：红色拍位需要修改，可以重新播放目标节奏。'
}
function toggleStep(step: string) {
  completedSteps.value = completedSteps.value.includes(step)
    ? completedSteps.value.filter((item) => item !== step)
    : [...completedSteps.value, step]
  testResult.value = `已完成 ${completedSteps.value.length} 个排练步骤`
}
function previous() { previewIndex.value = Math.max(0, previewIndex.value - 1) }
function next() { previewIndex.value = Math.min(visibleNodes.value.length - 1, previewIndex.value + 1) }
function finish(message = '试玩操作正常，实际课堂中将记录学生提交。') { testResult.value = message }

const translations: Record<string, string> = {
  listen: '聆听', choose: '选择', explain: '说明理由', assess: '评价',
  perform: '表演', cooperate: '合作', create: '创编', revise: '修改',
  tap: '拍击', move: '律动', sing: '演唱', read: '朗读', play: '演奏',
  activity: '教学活动', game: '音乐游戏', instrument_task: '虚拟乐器任务',
  beat_rhythm: '节拍与节奏', lyrics_rhythm: '歌词节奏', phrase_singing: '乐句学唱',
  pitch_score: '音高与谱面', guided_listening: '引导聆听', music_structure: '音乐结构',
  music_creation: '音乐创编', ensemble: '合奏与排练',
  performance_reflection: '展示与反思', virtual_instrument: '虚拟乐器',
  peer_feedback: '同伴评价', exit_ticket: '课堂回顾', phrase_loop: '分句循环',
  whole_phrase: '完整乐句', steady_beat: '稳定拍', melody_sequence: '旋律序列',
  rhythm_echo: '节奏模仿', orff_percussion: '奥尔夫打击乐', band_roles: '小乐队分声部',
  relay_performance: '小组接力展示', conductor_rehearsal: '多声部排练与指挥',
}
function translateText(value: string) {
  let result = value
  Object.entries(translations).forEach(([key, label]) => {
    result = result.replace(new RegExp(`\\b${key}\\b`, 'gi'), label)
  })
  return result.replace(/_/g, ' ')
}
function nodeTypeLabel(value: string) {
  const map: Record<string, string> = {
    activity: '教学活动', game: '音乐游戏', instrument_task: '虚拟乐器任务',
    entry: '课堂导入', listening_activity: '聆听活动', rhythm_game: '节奏活动',
    meter_experience: '节拍体验', singing_practice: '演唱练习',
    creation_workshop: '音乐创编', melody_activity: '旋律活动',
    timbre_activity: '音色活动', form_activity: '曲式活动',
    instrument_activity: '虚拟乐器', ensemble_activity: '合奏活动', summary: '课堂总结',
  }
  return map[value] || translateText(value)
}
function familyLabel(value: string) { return translations[value] || translateText(value) }
function variantLabel(value: string) { return translations[value] || translateText(value) }
function rendererLabel(value: string) {
  const map: Record<string, string> = {
    'meter-compare': '节拍比较', 'rhythm-drag': '节奏卡编排',
    'creation-panel': '音乐创编', summary: '课堂总结',
    'singing-practice': '乐句跟唱', 'listening-choice': '聆听选择',
    'solfege-sort': '唱名排序', 'melody-trace': '旋律线描画',
    'timbre-match': '音色配对', 'form-order': '曲式排序',
    'virtual-instrument': '虚拟乐器演奏', 'ensemble-roles': '分声部排练',
    completion: '活动完成',
  }
  return map[value] || translateText(value)
}
function defaultPrompt(value: string) {
  const map: Record<string, string> = {
    'meter-compare': '聆听并比较不同拍号的强弱规律。',
    'rhythm-drag': '选择节奏卡，完成目标节奏。',
    'creation-panel': '根据课堂要求完成一段音乐创编。',
    summary: '回顾本课学习内容，并说明自己的音乐发现。',
    'singing-practice': '先听示范，再逐句跟唱。',
    'listening-choice': '聆听音乐，选择感受并说明音乐依据。',
    'solfege-sort': '聆听并按正确顺序排列唱名。',
    'melody-trace': '聆听旋律，描画音高走向。',
    'timbre-match': '聆听音色，将乐器与类别配对。',
    'form-order': '聆听段落，排列曲式结构。',
    'virtual-instrument': '使用虚拟乐器完成指定演奏任务。',
    'ensemble-roles': '选择声部并完成分组排练。',
  }
  return map[value] || '按要求完成当前音乐活动。'
}
</script>

<template>
  <section class="package-preview">
    <header class="preview-toolbar">
      <div>
        <span class="tag">教师测试模式 · 不记录学生成绩</span>
        <h2>{{ displayTitle }}</h2>
        <p><strong>推荐目的：</strong>{{ displayPrompt }}</p>
      </div>
      <button class="button" type="button" @click="resetTest">重置试玩</button>
    </header>

    <div v-if="mode === 'package'" class="preview-flow">
      <button v-for="(node, index) in visibleNodes" :key="node.id" type="button"
        :class="{ active: index === previewIndex }"
        @click="previewIndex = index; emit('select', node.id)">
        <span>{{ index + 1 }}</span>{{ node.title }}
      </button>
    </div>

    <div v-if="activeNode" class="preview-device">
      <div class="preview-meta"><span v-for="label in metaLabels" :key="label">{{ label }}</span></div>

      <buyilehu-reviewed-activity
        v-if="runtime.componentUrl"
        :url="runtime.componentUrl"
        :title="displayTitle"
        :config="runtimeProps"
      />

      <div v-else-if="legacyRenderer === 'meter-compare'" class="preview-interaction">
        <p>请选择拍号并点击拍点，感受强拍与弱拍。</p>
        <div class="preview-buttons">
          <button v-for="meter in runtimeProps.meters || ['2/4', '3/4']" :key="meter" type="button" @click="choose(`${meter} 拍`)">{{ meter }}</button>
          <button type="button" @click="add('强拍')">● 强拍</button><button type="button" @click="add('弱拍')">○ 弱拍</button>
        </div>
      </div>

      <div v-else-if="legacyRenderer === 'rhythm-drag'" class="preview-interaction">
        <div class="rhythm-heading">
          <div><strong>节奏回声</strong><p>先听目标节奏，再用节奏卡按顺序还原。</p></div>
          <button class="button primary" type="button" :disabled="rhythmPlaying" @click="playRhythmTarget">
            {{ rhythmPlaying ? '正在播放…' : '▶ 播放目标节奏' }}
          </button>
        </div>
        <div class="preview-buttons">
          <button v-for="card in runtimeProps.cards || [{ name: 'ta' }, { name: 'ti-ti' }, { name: 'rest' }]"
            :key="card.name" type="button" @click="add(card.name)">{{ rhythmLabel(card.name) }}</button>
        </div>
        <div class="rhythm-progress"><strong>我的答案</strong><span>已完成 {{ sequence.length }} / {{ rhythmTarget.length }} 拍</span></div>
        <div class="rhythm-answer">
          <button v-for="(token, index) in sequence" :key="`${token}-${index}`" type="button"
            :class="{ correct: rhythmSubmitted && token === rhythmTarget[index], wrong: rhythmSubmitted && token !== rhythmTarget[index] }"
            @click="sequence.splice(index, 1); rhythmSubmitted = false">
            <small>第{{ index + 1 }}拍</small>{{ rhythmLabel(token) }}
          </button>
          <span v-for="slot in rhythmTarget.length - sequence.length" :key="slot">第{{ sequence.length + slot }}拍</span>
        </div>
        <div class="rhythm-actions">
          <button class="button" type="button" :disabled="!sequence.length" @click="undoRhythm">撤销一拍</button>
          <button class="button" type="button" :disabled="!sequence.length" @click="clearRhythm">清空</button>
          <button class="button primary" type="button" :disabled="sequence.length !== rhythmTarget.length" @click="submitRhythm">提交并检查</button>
        </div>
      </div>

      <div v-else-if="legacyRenderer === 'virtual-instrument'" class="preview-interaction virtual-instrument-preview">
        <iframe :src="virtualInstrumentUrl" title="虚拟乐器课堂预览" allow="autoplay" />
      </div>

      <div v-else-if="legacyRenderer === 'listening-choice'" class="preview-interaction">
        <p>模拟聆听后选择音乐感受和判断依据：</p>
        <div class="preview-buttons">
          <button v-for="option in runtimeProps.options || ['欢快', '安静', '优美']" :key="option" type="button" @click="choose(option)">{{ translateText(option) }}</button>
        </div>
        <textarea v-model="explanation" placeholder="写一句音乐依据，例如：速度较快、力度较强"></textarea>
        <button class="button primary" type="button" @click="finish('聆听选择和理由可以正常提交。')">提交判断</button>
      </div>

      <div v-else-if="legacyRenderer === 'singing-practice'" class="preview-interaction">
        <p v-for="phrase in runtimeProps.phrases || ['第一乐句', '第二乐句']" :key="phrase">♪ {{ translateText(phrase) }}</p>
        <div class="preview-buttons"><button type="button" @click="finish('示范乐句已播放。')">播放示范</button><button type="button" @click="finish('已模拟完成一次跟唱录音。')">模拟录音</button></div>
      </div>

      <div v-else-if="legacyRenderer === 'solfege-sort'" class="preview-interaction">
        <p>按听到的顺序点击唱名：</p>
        <div class="preview-buttons"><button v-for="token in runtimeProps.tokens || ['do','re','mi','sol']" :key="token" type="button" @click="add(token)">{{ token }}</button></div>
        <button class="button primary" type="button" @click="finish('唱名顺序可以正常提交。')">提交顺序</button>
      </div>

      <div v-else-if="legacyRenderer === 'melody-trace'" class="preview-interaction">
        <p>按旋律走向依次选择：</p>
        <div class="preview-buttons"><button type="button" @click="add('上行')">↗ 上行</button><button type="button" @click="add('平行')">→ 平行</button><button type="button" @click="add('下行')">↘ 下行</button></div>
      </div>

      <div v-else-if="legacyRenderer === 'timbre-match'" class="preview-interaction">
        <p>选择乐器，再选择对应类别进行配对：</p>
        <div class="preview-match-grid">
          <button v-for="item in runtimeProps.items || ['小提琴','长笛','小号','鼓']" :key="item" type="button" @click="add(item)">{{ translateText(item) }}</button>
          <button v-for="option in runtimeProps.options || ['弦乐器','木管乐器','铜管乐器','打击乐器']" :key="option" type="button" @click="choose(option)">{{ translateText(option) }}</button>
        </div>
      </div>

      <div v-else-if="legacyRenderer === 'form-order'" class="preview-interaction">
        <p>按听到的顺序点击曲式段落：</p>
        <div class="preview-buttons"><button v-for="section in runtimeProps.sections || ['引子','A段','B段','尾声']" :key="section" type="button" @click="add(section)">{{ translateText(section) }}</button></div>
        <button class="button primary" type="button" @click="finish('曲式顺序可以正常提交。')">验证顺序</button>
      </div>

      <div v-else-if="legacyRenderer === 'creation-panel'" class="preview-interaction">
        <textarea :placeholder="runtimeProps.defaultTitle || '输入学生创编内容'"></textarea>
        <button class="button primary" type="button" @click="finish('创编内容可以正常提交。')">测试提交</button>
      </div>

      <div v-else-if="legacyRenderer === 'ensemble-roles'" class="preview-interaction">
        <p>选择小组声部，并依次完成排练步骤：</p>
        <div class="preview-buttons">
          <button v-for="role in runtimeProps.roles || ['节奏组','旋律组','音色组','指挥']" :key="role" type="button"
            :class="{ selected: selectedRole === role }" @click="selectedRole = role; choose(role)">{{ translateText(role) }}</button>
        </div>
        <div class="preview-checklist">
          <label v-for="step in runtimeProps.steps || ['确认声部','分组练习','合奏排练','完成展示']" :key="step">
            <input type="checkbox" :checked="completedSteps.includes(step)" @change="toggleStep(step)" /> {{ translateText(step) }}
          </label>
        </div>
        <button class="button primary" type="button" :disabled="!selectedRole" @click="finish('声部选择和排练记录可以正常提交。')">提交排练记录</button>
      </div>

      <div v-else-if="legacyRenderer === 'summary'" class="preview-interaction">
        <h3>课堂学习回顾</h3>
        <p>请选择本课最有收获的音乐内容，并写出一个依据。</p>
        <div class="preview-buttons"><button type="button" @click="choose('节拍与节奏')">节拍与节奏</button><button type="button" @click="choose('旋律与音高')">旋律与音高</button><button type="button" @click="choose('合作与表现')">合作与表现</button></div>
        <textarea v-model="explanation" placeholder="我的音乐发现是……"></textarea>
        <button class="button primary" type="button" @click="finish('课堂回顾可以正常提交。')">完成课堂回顾</button>
      </div>

      <div v-else class="preview-interaction">
        <p>当前活动支持完成记录。点击下方按钮测试提交流程。</p>
        <button class="button primary" type="button" @click="finish()">模拟完成</button>
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

<style scoped>
.virtual-instrument-preview{padding:0;overflow:hidden}
.virtual-instrument-preview iframe{display:block;width:100%;height:min(760px,calc(100vh - 190px));min-height:620px;border:0;background:#f2f6f3}
.rhythm-heading,.rhythm-progress,.rhythm-actions{display:flex;align-items:center;justify-content:space-between;gap:12px}.rhythm-heading p{margin:4px 0 0}.rhythm-progress{margin-top:18px}.rhythm-answer{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin-top:10px}.rhythm-answer button,.rhythm-answer span{display:grid;place-items:center;min-height:76px;padding:9px;border-radius:12px}.rhythm-answer button{border:2px solid #c7d6d1;background:#fff}.rhythm-answer button small{color:#71857f}.rhythm-answer button.correct{border-color:#28a47e;background:#e9f8f1}.rhythm-answer button.wrong{border-color:#df6a5f;background:#fff0ed}.rhythm-answer span{border:2px dashed #ccd5d2;color:#899793}.rhythm-actions{justify-content:flex-end;margin-top:14px}
@media(max-width:700px){.virtual-instrument-preview iframe{height:calc(100vh - 130px);min-height:560px}}
</style>
