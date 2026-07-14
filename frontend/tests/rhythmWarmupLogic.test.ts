import {
  buildBeatTimeline,
  buildDefaultRhythmWarmupToolkit,
  judgeTapTiming,
  summarizeTempoStability,
  normalizeRhythmCards
} from "../src/activity/rhythmWarmupLogic";

function assertEqual<T>(actual: T, expected: T, label: string) {
  if (actual !== expected) {
    throw new Error(`${label}: expected ${String(expected)}, got ${String(actual)}`);
  }
}

function assertDeepEqual(actual: unknown, expected: unknown, label: string) {
  const actualText = JSON.stringify(actual);
  const expectedText = JSON.stringify(expected);
  if (actualText !== expectedText) {
    throw new Error(`${label}: expected ${expectedText}, got ${actualText}`);
  }
}

const cards = normalizeRhythmCards([
  { id: "card-1", patternId: "quarter", label: "四", syllable: "四", beats: 1, hitRequired: true },
  { id: "eighth_pair", label: "二八", syllable: "二八", beats: 1, hitRequired: true, subdivisions: 2 },
  { id: "rest", label: "休止", syllable: "休止", beats: 1, hitRequired: false }
]);

assertDeepEqual(
  cards.map((card) => card.durationMs),
  [600, 600, 600],
  "default BPM converts one-beat primary rhythm cards into 600ms cards"
);
assertEqual(cards[1].subdivisions, 2, "eighth-pair cards preserve the visible subdivision count");
assertEqual(cards[2].hitRequired, false, "rest cards remain visible but do not require a tap");
assertEqual(cards[0].patternId, "quarter", "a repeated UI instance preserves its canonical notation and playback pattern id");

const timeline = buildBeatTimeline(cards, { bpm: 100, meter: "2/4", repeatCount: 2 });
assertDeepEqual(
  timeline.map((event) => [event.cardId, event.patternId, event.startMs, event.bar, event.beatInBar, event.hitRequired]),
  [
    ["card-1", "quarter", 0, 1, 1, true],
    ["eighth_pair", "eighth_pair", 600, 1, 2, true],
    ["rest", "rest", 1200, 2, 1, false],
    ["card-1", "quarter", 1800, 2, 2, true],
    ["eighth_pair", "eighth_pair", 2400, 3, 1, true],
    ["rest", "rest", 3000, 3, 2, false]
  ],
  "beat timeline repeats the rhythm pattern and labels bars/beats for a meter track"
);

assertEqual(judgeTapTiming(595, timeline, { toleranceMs: 95 }).status, "on_time", "near taps are on time");
assertEqual(judgeTapTiming(450, timeline, { toleranceMs: 95 }).status, "early", "early taps are identified");
assertEqual(judgeTapTiming(742, timeline, { toleranceMs: 95 }).status, "late", "late taps are identified");
assertEqual(judgeTapTiming(1220, timeline, { toleranceMs: 95 }).status, "rest", "rests do not reward taps");
assertEqual(judgeTapTiming(4720, timeline, { toleranceMs: 95 }).status, "miss", "unmatched taps are misses");

const toolkit = buildDefaultRhythmWarmupToolkit();
assertEqual(toolkit.activityId, "rhythm_warmup", "default toolkit exposes the rhythm warmup activity id");
assertEqual(toolkit.teacherControls.bpm, 92, "default rhythm warmup keeps a primary-classroom tempo");
assertDeepEqual(
  toolkit.requiredComponents,
  ["audio_player", "rhythm_card_bank", "meter_track", "tap_feedback", "teacher_control_bar", "rhythm_pad"],
  "default rhythm warmup declares the first reusable component set"
);
assertDeepEqual(toolkit.teachingAids, ["rhythm_cards"], "default toolkit binds rhythm cards as the teaching aid");
assertDeepEqual(toolkit.virtualInstruments, ["rhythm_pad"], "default toolkit binds the rhythm pad as the virtual instrument");
assertDeepEqual(
  toolkit.rhythmCards.map((card) => card.syllable),
  ["四个十六", "二八", "八十六", "十六八", "四"],
  "default rhythm cards expose classroom rhythm patterns for visual notation cards"
);

const stable = summarizeTempoStability([0, 652, 1304, 1956], { bpm: 92, toleranceMs: 80 });
assertEqual(stable.status, "stable", "even tap intervals count as stable beat");
assertEqual(stable.tapCount, 4, "tempo stability counts tap records");
assertEqual(stable.targetIntervalMs, 652, "tempo stability derives target interval from BPM");
assertEqual(stable.teacherSuggestion.includes("保持"), true, "stable beat gives a keep-going suggestion");

const rushing = summarizeTempoStability([0, 520, 1010, 1480], { bpm: 92, toleranceMs: 80 });
assertEqual(rushing.status, "rushing", "too-short intervals identify rushing");
assertEqual(rushing.teacherSuggestion.includes("放慢"), true, "rushing beat asks teacher to slow down");

const collecting = summarizeTempoStability([0], { bpm: 92 });
assertEqual(collecting.status, "collecting", "one tap is not enough to judge stability");
