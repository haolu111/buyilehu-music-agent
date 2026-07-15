import type { RhythmAttemptResult } from "./rhythmWarmupLogic";

export type LyricsPracticeMode = "echo" | "play_along";

export type LyricsTrainingStage =
  | "idle"
  | "listening"
  | "ready"
  | "count_in"
  | "recording"
  | "feedback"
  | "audio_error"
  | "blocked";

export function normalizeLyricsPracticeMode(value: unknown): LyricsPracticeMode {
  return value === "play_along" ? "play_along" : "echo";
}

export function shouldPlayTargetDuringRecording(mode: LyricsPracticeMode): boolean {
  return mode === "play_along";
}

export function primaryActionForTrainingStage(stage: LyricsTrainingStage): string {
  if (stage === "idle") return "开始训练：先听示范";
  if (stage === "listening") return "正在播放示范";
  if (stage === "ready") return "我准备好了，开始拍回";
  if (stage === "count_in") return "听预备拍";
  if (stage === "recording") return "拍一下";
  if (stage === "feedback") return "再听一次并重练";
  if (stage === "audio_error") return "重新加载音色";
  return "等待教师确认材料";
}

export function classroomResultLabel(result: RhythmAttemptResult): string {
  if (result === "correct") return "节奏准确，可以进入教师确认";
  if (result === "adjust") return "基本正确，再调整一次";
  return "需要重新听示范";
}
