import {
  buildPentatonicCreationExport,
  buildPentatonicCreationSummary,
  buildPentatonicMelodyPlan,
  evaluatePentatonicMelody,
  noteOffsetForSolfege,
  recordPentatonicCreationEvent
} from "../src/activity/pentatonicMelodyLogic";

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

const plan = buildPentatonicMelodyPlan({
  solfegeSet: ["do", "re", "mi", "fa", "sol", "la", "ti"],
  rhythmPattern: ["quarter", "quarter", "eighth_pair", "quarter"],
  meter: "2/4",
  compositionTotalBars: 2,
  bpm: 112
});

assertDeepEqual(plan.allowedSolfege, ["do", "re", "mi", "sol", "la"], "plan keeps classroom pentatonic notes only");
assertEqual(plan.bpm, 104, "plan clamps fast creation tempo");
assertEqual(plan.slots.length, 4, "plan creates one slot for each rhythm card");
assertEqual(plan.capacityBeats, 4, "two bars in 2/4 require four beats");
assertEqual(plan.rhythmCards[2].label, "二八", "eighth pair uses formal classroom rhythm naming");
assertEqual(noteOffsetForSolfege("la"), 9, "la maps to pentatonic tone offset");

const incomplete = evaluatePentatonicMelody(plan, ["do", "re"], false);
assertEqual(incomplete.status, "incomplete", "not enough notes is incomplete");

const notAuditioned = evaluatePentatonicMelody(plan, ["do", "re", "mi", "sol"], false);
assertEqual(notAuditioned.status, "needs_audition", "filled phrase must be listened to before confirmation");

const ready = evaluatePentatonicMelody(plan, ["do", "re", "mi", "sol"], true);
assertEqual(ready.status, "ready", "filled and auditioned pentatonic phrase is ready");
assertEqual(ready.message.includes("五声音级"), true, "ready feedback names pentatonic constraint");

const emptyEvents = [];
const placedEvents = recordPentatonicCreationEvent(emptyEvents, {
  eventType: "place_note",
  note: "do",
  slotIndex: 0,
  timestampMs: 20,
});
const revisedEvents = recordPentatonicCreationEvent(placedEvents, {
  eventType: "undo_note",
  note: "do",
  slotIndex: 0,
  timestampMs: 80,
});
const replayedEvents = recordPentatonicCreationEvent(revisedEvents, {
  eventType: "audition_phrase",
  notes: ["do", "re", "mi", "sol"],
  timestampMs: 140,
});

assertEqual(emptyEvents.length, 0, "recording does not mutate previous pentatonic events");
assertEqual(replayedEvents.length, 3, "pentatonic creation events append");

const summary = buildPentatonicCreationSummary(plan, ["do", "re", "mi", "sol"], replayedEvents, true);
assertEqual(summary.version, "pentatonic_creation_summary_v1", "summary has stable version");
assertEqual(summary.noteSequence, "do re mi sol", "summary keeps note sequence");
assertEqual(summary.revisionCount, 1, "summary counts undo as revision");
assertEqual(summary.auditionCount, 1, "summary counts phrase auditions");
assertEqual(summary.readyForRelay, true, "ready phrase can enter group relay");
assertEqual(summary.teacherNextStep.includes("下一组"), true, "summary suggests group relay");

const exported = JSON.parse(buildPentatonicCreationExport(summary));
assertEqual(exported.version, "pentatonic_creation_record_v1", "export has stable version");
assertEqual(exported.note_sequence, "do re mi sol", "export keeps note sequence");
assertEqual(exported.ready_for_relay, true, "export keeps relay readiness");
assertEqual(exported.events.length, 3, "export keeps creation events");
