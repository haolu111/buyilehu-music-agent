<script setup lang="ts">
import { onBeforeUnmount, ref } from 'vue'

const props = withDefaults(defineProps<{ phrases?: string[]; lyrics?: string; audioUrl?: string; bpm?: number; recordingEnabled?: boolean }>(), {
  phrases: () => ['第一乐句', '第二乐句'], lyrics: '', audioUrl: '', bpm: 86, recordingEnabled: true,
})
const emit = defineEmits<{ completed: [payload: { result: Record<string, unknown> }] }>()
const activePhrase = ref(0)
const recording = ref(false)
const seconds = ref(0)
const attempts = ref(0)
const error = ref('')
let recorder: MediaRecorder | null = null
let stream: MediaStream | null = null
let timer = 0

async function toggleRecording() {
  if (recording.value) {
    recorder?.stop()
    recording.value = false
    window.clearInterval(timer)
    attempts.value += 1
    return
  }
  try {
    stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    recorder = new MediaRecorder(stream)
    recorder.start()
    seconds.value = 0
    recording.value = true
    timer = window.setInterval(() => { seconds.value += 1 }, 1000)
    error.value = ''
  } catch {
    error.value = '无法使用麦克风，请检查浏览器权限。'
  }
}
function submit() {
  emit('completed', { result: { phrase: props.phrases[activePhrase.value], attempts: attempts.value, durationSeconds: seconds.value, bpm: props.bpm } })
}
onBeforeUnmount(() => { window.clearInterval(timer); stream?.getTracks().forEach(track => track.stop()) })
</script>

<template>
  <section class="music-activity">
    <header><span class="activity-kicker">演唱练习 · 每分钟 {{ bpm }} 拍</span><h2>听一句，唱一句</h2><p>{{ lyrics || '选择乐句，听清旋律后录下你的演唱。' }}</p></header>
    <audio v-if="audioUrl" class="activity-audio" :src="audioUrl" controls />
    <div class="choice-grid"><button v-for="(phrase, index) in phrases" :key="phrase" type="button" :class="{ selected: activePhrase === index }" @click="activePhrase = index">{{ phrase }}</button></div>
    <div class="recording-strip" :class="{ active: recording }"><span class="record-dot" /><strong>{{ recording ? `录音中 ${seconds} 秒` : attempts ? `已完成 ${attempts} 次录音` : '准备录音' }}</strong></div>
    <p v-if="error" class="activity-error">{{ error }}</p>
    <div class="activity-actions"><button v-if="recordingEnabled" class="secondary-action" type="button" @click="toggleRecording">{{ recording ? '停止录音' : '开始录音' }}</button><button class="primary-action" type="button" :disabled="recordingEnabled && !attempts" @click="submit">提交演唱记录</button></div>
  </section>
</template>
