import * as graphicScoreLogic from "../src/activity/graphicScoreLogic";

const {
  buildGraphicScoreExport,
  buildGraphicScorePlan,
  buildGraphicScoreSummary,
  evaluateGraphicScore,
  graphicToneOffset,
  placeGraphicSymbol
} = graphicScoreLogic;

function assertEqual<T>(actual: T, expected: T, label: string) {
  if (actual !== expected) {
    throw new Error(`${label}: expected ${String(expected)}, got ${String(actual)}`);
  }
}

function assertDeepEqual<T>(actual: T, expected: T, label: string) {
  const actualText = JSON.stringify(actual);
  const expectedText = JSON.stringify(expected);
  if (actualText !== expectedText) {
    throw new Error(`${label}: expected ${expectedText}, got ${actualText}`);
  }
}

const plan = buildGraphicScorePlan({
  meter: "2/4",
  totalBeats: 4,
  symbolMeanings: [
    { symbol: "dot", label: "点", pitch: "high", duration: "short", dynamics: "soft" },
    { symbol: "line", label: "线", pitch: "middle", duration: "long", dynamics: "medium" },
    { symbol: "block", label: "块", pitch: "low", duration: "long", dynamics: "strong" },
  ],
  requiredElements: ["pitch", "duration", "dynamics"],
});

assertEqual(plan.slots.length, 4, "graphic score has four ordered slots");
assertDeepEqual(plan.requiredElements, ["pitch", "duration", "dynamics"], "plan keeps required music elements");
assertEqual(plan.symbols[0].label, "点", "plan keeps symbol label");
assertEqual(graphicToneOffset("high"), 7, "high graphic maps to higher tone");
assertEqual(graphicToneOffset("low"), -5, "low graphic maps to lower tone");

let slots = plan.slots;
slots = placeGraphicSymbol(slots, 1, plan.symbols[0]);
slots = placeGraphicSymbol(slots, 2, plan.symbols[1]);
slots = placeGraphicSymbol(slots, 3, plan.symbols[2]);

const incomplete = evaluateGraphicScore(plan, slots, false);
assertEqual(incomplete.status, "incomplete", "unfilled score is incomplete");

slots = placeGraphicSymbol(slots, 4, plan.symbols[0]);
const needsPlayback = evaluateGraphicScore(plan, slots, false);
assertEqual(needsPlayback.status, "needs_playback", "filled score must be played before sharing");

const ready = evaluateGraphicScore(plan, slots, true);
assertEqual(ready.status, "ready", "filled and played score is ready");
assertEqual(ready.feedback.includes("高低"), true, "ready feedback names pitch");
assertEqual(ready.feedback.includes("强弱"), true, "ready feedback names dynamics");

const summary = buildGraphicScoreSummary(plan, slots, true);
assertEqual(summary.version, "graphic_score_summary_v1", "summary has stable version");
assertEqual(summary.usedPitchLevels.includes("high"), true, "summary records high pitch");
assertEqual(summary.usedDynamics.includes("strong"), true, "summary records strong dynamics");
assertEqual(summary.readyForPerformance, true, "summary is ready for performance");

const exported = JSON.parse(buildGraphicScoreExport(summary));
assertEqual(exported.version, "graphic_score_record_v1", "export has stable version");
assertEqual(exported.slots.length, 4, "export keeps ordered slots");
assertEqual(exported.ready_for_performance, true, "export keeps performance readiness");

type MixedGraphicScoreApi = {
  placeGraphicRhythmCard: (slots: typeof plan.slots, beatIndex: number, rhythmId: string) => typeof plan.slots;
  placeGraphicPitchCard: (slots: typeof plan.slots, beatIndex: number, pitchId: string) => typeof plan.slots;
  buildGraphicScorePlaybackEvents: (slots: typeof plan.slots, bpm: number, mode: "graphic" | "mixed_cards") => Array<{ offset: number; start: number; duration: number }>;
};

const mixedApi = graphicScoreLogic as unknown as MixedGraphicScoreApi;
assertEqual(typeof mixedApi.placeGraphicRhythmCard, "function", "graphic score exposes rhythm card placement");
assertEqual(typeof mixedApi.placeGraphicPitchCard, "function", "graphic score exposes pitch card placement");
assertEqual(typeof mixedApi.buildGraphicScorePlaybackEvents, "function", "graphic score exposes canonical playback events");

let mixedSlots = plan.slots;
const mixedSymbols = [plan.symbols[0], plan.symbols[1], plan.symbols[2], plan.symbols[0]];
mixedSymbols.forEach((symbol, index) => {
  mixedSlots = placeGraphicSymbol(mixedSlots, index + 1, symbol);
});
mixedSlots = mixedApi.placeGraphicRhythmCard(mixedSlots, 1, "eighth_pair");
mixedSlots = mixedApi.placeGraphicPitchCard(mixedSlots, 1, "mi");
mixedSlots = mixedApi.placeGraphicRhythmCard(mixedSlots, 2, "rest");
mixedSlots = mixedApi.placeGraphicPitchCard(mixedSlots, 2, "do");
mixedSlots = mixedApi.placeGraphicRhythmCard(mixedSlots, 3, "quarter");
mixedSlots = mixedApi.placeGraphicPitchCard(mixedSlots, 3, "sol");
mixedSlots = mixedApi.placeGraphicRhythmCard(mixedSlots, 4, "sixteenth_four");
mixedSlots = mixedApi.placeGraphicPitchCard(mixedSlots, 4, "do");

const mixedEvents = mixedApi.buildGraphicScorePlaybackEvents(mixedSlots, 60, "mixed_cards");
assertEqual(mixedEvents.length, 7, "mixed score expands internal rhythm attacks and keeps rests silent");
assertDeepEqual(mixedEvents.slice(0, 2).map((event) => event.offset), [4, 4], "mi card sets exact pitch for both eighth notes");
assertDeepEqual(mixedEvents.slice(0, 2).map((event) => event.start), [0, 0.5], "eighth pair uses canonical half-beat spacing");
assertEqual(mixedEvents[2].offset, 7, "sol card sets the next sounding pitch");
assertEqual(mixedEvents[2].start, 2, "rest occupies its beat without producing an event");

const mixedEvaluation = evaluateGraphicScore(plan, mixedSlots, true, "mixed_cards");
assertEqual(mixedEvaluation.status, "ready", "complete mixed score can be presented after playback");
const mixedSummary = buildGraphicScoreSummary(plan, mixedSlots, true, "mixed_cards");
assertDeepEqual(mixedSummary.rhythmIds, ["eighth_pair", "rest", "quarter", "sixteenth_four"], "summary records rhythm card ids");
assertDeepEqual(mixedSummary.pitchIds, ["mi", "do", "sol", "do"], "summary records pitch card ids");
