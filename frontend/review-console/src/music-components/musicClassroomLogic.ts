import type { GradePreset, MusicTrack } from "../shared/musicMediaContracts";

export type EarTrainingQuestionType = "single_pitch" | "interval" | "rhythm" | "short_melody" | "tonal_center";

export type EarTrainingRound = {
  id: string;
  type: EarTrainingQuestionType;
  midi: number[];
  prompt: string;
  answer: string;
  choices: string[];
};

export function normalizeLoopRange(start: number, end: number, duration: number) {
  const max = Math.max(0, Number(duration) || 0);
  const first = Math.max(0, Math.min(max, Number(start) || 0));
  const second = Math.max(0, Math.min(max, Number(end) || 0));
  return { startSeconds: Math.min(first, second), endSeconds: Math.max(first, second) };
}

export function buildWaveformBars(seed: string, count = 64): number[] {
  let hash = 2166136261;
  for (const char of seed || "music") hash = Math.imul(hash ^ char.charCodeAt(0), 16777619);
  return Array.from({ length: count }, (_, index) => {
    hash = Math.imul(hash ^ (index + 1), 16777619);
    return 18 + (Math.abs(hash) % 77);
  });
}

const NOTE_LABELS: Record<number, string> = { 0: "do", 2: "re", 4: "mi", 5: "fa", 7: "sol", 9: "la", 11: "ti" };

export function buildEarTrainingRounds(input: {
  questionTypes: EarTrainingQuestionType[];
  allowedMidi: number[];
  allowRandom: boolean;
  count: number;
}): EarTrainingRound[] {
  const allowed = input.allowedMidi.length ? [...input.allowedMidi] : [60, 62, 64, 65, 67];
  const types: EarTrainingQuestionType[] = input.questionTypes.length ? input.questionTypes : ["single_pitch"];
  return Array.from({ length: Math.max(1, input.count) }, (_, index) => {
    const questionType: EarTrainingQuestionType = types[index % types.length];
    const start = input.allowRandom ? Math.floor(Math.random() * allowed.length) : index % allowed.length;
    const first = allowed[start % allowed.length];
    const second = allowed[(start + 1 + (questionType === "interval" ? 1 : 0)) % allowed.length];
    const midi = questionType === "single_pitch" || questionType === "tonal_center" ? [first] : questionType === "interval" ? [first, second] : [first, second, allowed[(start + 2) % allowed.length]];
    const answer = questionType === "rhythm" ? "均匀" : noteLabel(midi[midi.length - 1]);
    return {
      id: `ear-${index + 1}`,
      type: questionType,
      midi,
      prompt: promptForQuestion(questionType),
      answer,
      choices: questionType === "rhythm" ? ["均匀", "前紧后松", "有休止"] : ["do", "re", "mi", "fa", "sol", "la", "ti"]
    };
  });
}

export function vocalSafetyPreset(grade: GradePreset) {
  if (grade === "lower_primary") return { comfortableMidi: [60, 69] as [number, number], continuousMinutes: 4, cue: "轻声、自然、不过度追求音量" };
  if (grade === "upper_primary") return { comfortableMidi: [57, 74] as [number, number], continuousMinutes: 8, cue: "保持自然共鸣，不挤压高音" };
  return { comfortableMidi: [59, 72] as [number, number], continuousMinutes: 6, cue: "自然起音，连贯呼吸，不喊唱" };
}

export function audibleTracks<T extends Pick<MusicTrack, "muted" | "solo"> | { muted: boolean; solo: boolean }>(tracks: T[]): T[] {
  const hasSolo = tracks.some((track) => track.solo);
  return tracks.filter((track) => !track.muted && (!hasSolo || track.solo));
}

export function clearScheduledCueHandles(handles: number[], cancel: (handle: number) => void) {
  handles.splice(0).forEach(cancel);
}

export function activeScoreEventIndex(
  events: Array<{ startSeconds: number; rest?: boolean }>,
  elapsedSeconds: number
) {
  let activeIndex = -1;
  for (const event of events) {
    if (event.rest) continue;
    if (elapsedSeconds < event.startSeconds) break;
    activeIndex += 1;
  }
  return activeIndex;
}

export function midiToSolfege(midi: number) {
  return noteLabel(midi);
}

function noteLabel(midi: number) {
  return NOTE_LABELS[((Math.round(midi) % 12) + 12) % 12] ?? "变化音";
}

function promptForQuestion(type: EarTrainingQuestionType) {
  return {
    single_pitch: "听一个音，选择对应唱名。",
    interval: "听两个音，判断第二个音的唱名。",
    rhythm: "听节奏，判断它的组织特点。",
    short_melody: "听短旋律，判断结束音。",
    tonal_center: "听主音感，找出稳定的中心音。"
  }[type];
}
