const componentLabels: Record<string, string> = {
  'listening choice': '听辨选择',
  listening_choice: '听辨选择',
  'instrument task:free play': '乐器自由探索',
  'instrument:virtual piano': '虚拟钢琴',
  'instrument task:steady beat': '稳定节拍练习',
  'instrument:virtual frame drum': '虚拟框鼓',
  'instrument task:rhythm echo': '节奏模仿',
  'instrument task:melody sequence': '旋律排序',
  'instrument task:ensemble cue': '合奏提示练习',
  'instrument task:constrained composition': '限定条件创编',
}

const nodeTypeLabels: Record<string, string> = {
  entry: '课堂导入',
  listening_activity: '听辨活动',
  rhythm_game: '节奏活动',
  meter_experience: '节拍体验',
  singing_practice: '演唱练习',
  creation_workshop: '音乐创编',
  melody_activity: '旋律活动',
  timbre_activity: '音色活动',
  form_activity: '曲式活动',
  instrument_activity: '虚拟乐器',
  ensemble_activity: '合奏活动',
  summary: '课堂总结',
}

function normalized(value: string) {
  return value.trim().toLowerCase().replace(/\s*:\s*/g, ':')
}

export function componentDisplayName(name?: string, componentKey?: string) {
  const candidates = [name, componentKey].filter((value): value is string => Boolean(value?.trim()))
  for (const candidate of candidates) {
    const label = componentLabels[normalized(candidate)]
    if (label) return label
  }
  const fallback = candidates[0] || '互动活动'
  return /[\u3400-\u9fff]/.test(fallback) ? fallback : '互动活动'
}

export function nodeTypeDisplayName(type?: string) {
  if (!type) return '课堂活动'
  return nodeTypeLabels[normalized(type)] || '课堂活动'
}
