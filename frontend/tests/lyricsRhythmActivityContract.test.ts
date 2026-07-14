import { readFileSync } from "node:fs";

function assertIncludes(source: string, expected: string, label: string) {
  if (!source.includes(expected)) throw new Error(`${label}: missing ${expected}`);
}

const source = readFileSync(new URL("../src/activity/LyricsRhythmActivity.tsx", import.meta.url), "utf8");

assertIncludes(source, "SOUNDFONT_PREPARE_TIMEOUT_MS", "lyrics rhythm has a bounded real-audio preparation window");
assertIncludes(source, "allowOscillatorFallback: false", "lyrics rhythm never substitutes an oscillator");
assertIncludes(source, "stage !== \"feedback\"", "final pass waits for the complete rhythm round");
assertIncludes(source, "教师确认：歌词朗读正确", "reading remains a teacher decision");
assertIncludes(source, "教师确认：回唱达到要求", "singing remains a teacher decision");
assertIncludes(source, "lyrics-training-stepper", "classroom flow has a visible listen perform feedback stepper");
assertIncludes(source, "lyrics-classroom-primary-action", "classroom flow has a prominent primary action");
assertIncludes(source, "听歌曲原句", "song audio remains an optional secondary listening action");
assertIncludes(source, "event.repeat", "keyboard hold cannot create repeated taps");
assertIncludes(source, "runIdRef.current !== runId", "stale audio promises cannot reopen a cancelled classroom round");
