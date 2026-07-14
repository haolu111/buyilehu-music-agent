import assert from "node:assert/strict";
import {
  activeScoreEventIndex,
  audibleTracks,
  buildEarTrainingRounds,
  buildWaveformBars,
  clearScheduledCueHandles,
  normalizeLoopRange,
  vocalSafetyPreset
} from "../src/music-components/musicClassroomLogic";

assert.deepEqual(normalizeLoopRange(8, 3, 10), { startSeconds: 3, endSeconds: 8 });
assert.deepEqual(normalizeLoopRange(-2, 18, 12), { startSeconds: 0, endSeconds: 12 });

const bars = buildWaveformBars("teacher-song.mp3", 24);
assert.equal(bars.length, 24);
assert.ok(bars.every((height) => height >= 18 && height <= 94));
assert.deepEqual(bars, buildWaveformBars("teacher-song.mp3", 24), "waveform placeholder is stable for the same source");

const constrainedRounds = buildEarTrainingRounds({
  questionTypes: ["single_pitch", "interval", "rhythm", "short_melody", "tonal_center"],
  allowedMidi: [60, 62, 64, 65, 67],
  allowRandom: false,
  count: 5
});
assert.deepEqual(constrainedRounds.map((round) => round.type), [
  "single_pitch",
  "interval",
  "rhythm",
  "short_melody",
  "tonal_center"
]);
assert.ok(constrainedRounds.every((round) => round.midi.every((midi) => [60, 62, 64, 65, 67].includes(midi))));

assert.deepEqual(vocalSafetyPreset("lower_primary"), {
  comfortableMidi: [60, 69],
  continuousMinutes: 4,
  cue: "轻声、自然、不过度追求音量"
});
assert.equal(vocalSafetyPreset("upper_primary").continuousMinutes, 8);

const tracks = [
  { id: "a", muted: false, solo: false },
  { id: "b", muted: false, solo: true },
  { id: "c", muted: true, solo: false }
];
assert.deepEqual(audibleTracks(tracks).map((track) => track.id), ["b"]);

const cancelledCueHandles: number[] = [];
const cueHandles = [11, 12, 13];
clearScheduledCueHandles(cueHandles, (handle) => cancelledCueHandles.push(handle));
assert.deepEqual(cancelledCueHandles, [11, 12, 13]);
assert.deepEqual(cueHandles, [], "cleared cue handles cannot fire after the teacher pauses");

const scoreEvents = [
  { startSeconds: 0, rest: false },
  { startSeconds: 0.5, rest: true },
  { startSeconds: 1, rest: false },
  { startSeconds: 1.5, rest: false }
];
assert.equal(activeScoreEventIndex(scoreEvents, -0.1), -1);
assert.equal(activeScoreEventIndex(scoreEvents, 0.75), 0, "rests keep the cursor on the preceding sounded note");
assert.equal(activeScoreEventIndex(scoreEvents, 1.2), 1);
assert.equal(activeScoreEventIndex(scoreEvents, 2), 2);
