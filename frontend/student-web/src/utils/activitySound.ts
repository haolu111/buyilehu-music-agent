let audioContext: AudioContext | null = null

function context(): AudioContext | null {
  if (typeof window === 'undefined' || !window.AudioContext) return null
  audioContext ||= new AudioContext()
  if (audioContext.state === 'suspended') void audioContext.resume()
  return audioContext
}

function tone(frequency: number, duration = 0.12, delay = 0, gainValue = 0.13, type: OscillatorType = 'sine') {
  const ctx = context()
  if (!ctx) return
  const start = ctx.currentTime + delay
  const oscillator = ctx.createOscillator()
  const gain = ctx.createGain()
  oscillator.type = type
  oscillator.frequency.setValueAtTime(frequency, start)
  gain.gain.setValueAtTime(gainValue, start)
  gain.gain.exponentialRampToValueAtTime(0.001, start + duration)
  oscillator.connect(gain).connect(ctx.destination)
  oscillator.start(start)
  oscillator.stop(start + duration)
}

export function unlockActivitySound() {
  context()
}

export function playTapSound() {
  tone(660, 0.07, 0, 0.07)
}

export function playSuccessSound() {
  tone(523.25, 0.14, 0, 0.12)
  tone(659.25, 0.14, 0.11, 0.12)
  tone(783.99, 0.24, 0.22, 0.12)
}

export function playErrorSound() {
  tone(220, 0.15, 0, 0.1, 'triangle')
  tone(174.61, 0.22, 0.13, 0.1, 'triangle')
}

const solfegeFrequencies: Record<string, number> = {
  do: 261.63,
  re: 293.66,
  mi: 329.63,
  fa: 349.23,
  sol: 392,
  so: 392,
  la: 440,
  ti: 493.88,
  si: 493.88,
}

export function playSolfege(token: string) {
  tone(solfegeFrequencies[token.toLowerCase()] || 349.23, 0.3, 0, 0.13)
}

export function playMelodyLevel(level: string) {
  const frequencies: Record<string, number> = { high: 523.25, up: 523.25, middle: 392, same: 392, low: 261.63, down: 261.63 }
  tone(frequencies[level] || 392, 0.25, 0, 0.12)
}

export function playRhythmPattern(pattern: string) {
  const normalized = pattern.toLowerCase()
  if (normalized === 'rest' || pattern.trim() === '-') {
    playTapSound()
    return
  }
  const hits = normalized.includes('ti-ti') || pattern.trim().split(/\s+/).length > 1 ? 2 : 1
  for (let index = 0; index < hits; index += 1) tone(196, 0.08, index * 0.12, 0.12, 'square')
}

export function playRhythmSequence(sequence: string[], beatSeconds = 0.56) {
  sequence.forEach((token, beatIndex) => {
    const normalized = token.toLowerCase()
    if (normalized === 'rest' || token.trim() === '-') return
    const hits = normalized.includes('ti-ti') ? 2 : 1
    for (let hit = 0; hit < hits; hit += 1) {
      tone(196, 0.09, beatIndex * beatSeconds + hit * beatSeconds / hits, hit === 0 ? 0.16 : 0.12, 'square')
    }
  })
}

export function playMeter(beats: number) {
  for (let index = 0; index < beats; index += 1) {
    tone(index === 0 ? 880 : 587.33, 0.09, index * 0.32, index === 0 ? 0.13 : 0.09, 'triangle')
  }
}
