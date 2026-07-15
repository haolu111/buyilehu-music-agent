import {
  classroomResultLabel,
  normalizeLyricsPracticeMode,
  primaryActionForTrainingStage,
  shouldPlayTargetDuringRecording,
} from "../src/activity/lyricsTrainingFlow";

function assertEqual<T>(actual: T, expected: T, label: string) {
  if (actual !== expected) throw new Error(`${label}: expected ${String(expected)}, got ${String(actual)}`);
}

assertEqual(normalizeLyricsPracticeMode(undefined), "echo", "missing practice mode defaults to echo");
assertEqual(normalizeLyricsPracticeMode("play_along"), "play_along", "teacher can explicitly request play along");
assertEqual(normalizeLyricsPracticeMode("random"), "echo", "unknown mode never randomly changes classroom behavior");

assertEqual(primaryActionForTrainingStage("idle"), "开始训练：先听示范", "idle stage exposes a visible training action");
assertEqual(primaryActionForTrainingStage("ready"), "我准备好了，开始拍回", "ready stage exposes the perform action");
assertEqual(primaryActionForTrainingStage("recording"), "拍一下", "recording stage exposes the rhythm pad");
assertEqual(primaryActionForTrainingStage("feedback"), "再听一次并重练", "feedback stage exposes repractice");
assertEqual(primaryActionForTrainingStage("audio_error"), "重新加载音色", "audio error exposes recovery");

assertEqual(shouldPlayTargetDuringRecording("echo"), false, "echo recording is silent after count in");
assertEqual(shouldPlayTargetDuringRecording("play_along"), true, "play along schedules the target during recording");

assertEqual(classroomResultLabel("correct"), "节奏准确，可以进入教师确认", "correct result uses classroom language");
assertEqual(classroomResultLabel("adjust"), "基本正确，再调整一次", "adjust result uses classroom language");
assertEqual(classroomResultLabel("retry"), "需要重新听示范", "retry result uses classroom language");
