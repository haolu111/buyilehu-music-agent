import { buildMetronomeTimeline, normalizeMetronomeConfig } from "../src/virtual-instruments/core/metronome";
import { createClassroomActivitySession, recordClassroomActivityTap, finishClassroomActivity } from "../src/virtual-instruments/core/classroomInstrumentActivity";
import { METRONOME_SOUNDBANK_BUILD_SPEC } from "../src/virtual-instruments/core/soundbankBuildPlan";
import { getAuditedClassroomAudioAsset } from "../src/virtual-instruments/core/virtualInstrumentCatalog";

function equal<T>(actual: T, expected: T, label: string) {
  if (actual !== expected) throw new Error(`${label}: expected ${String(expected)}, got ${String(actual)}`);
}

const config = normalizeMetronomeConfig({ bpm: 120, meter: "6/8", countInBars: 1, continueDuringPerformance: false, subdivision: "eighth" });
const timeline = buildMetronomeTimeline(config, 1);
equal(timeline.filter((event) => event.phase === "count_in").length, 6, "6/8 count-in has six eighth-note clicks");
equal(timeline[0].midi, 34, "bar starts use the real metronome bell");
equal(timeline[1].midi, 33, "weak beats use the real metronome click");
equal(timeline.some((event) => event.phase === "performance"), false, "muted performance has no metronome overlap");
equal(JSON.stringify(METRONOME_SOUNDBANK_BUILD_SPEC.midiNotes), JSON.stringify([33, 34]), "metronome pack contains click and bell only");
equal(getAuditedClassroomAudioAsset("virtual_metronome")?.fallback.format, "legacy-wav-map", "metronome has a real WAV fallback");

const steady = createClassroomActivitySession({
  mode: "steady_beat",
  target: { type: "instrument", instrumentId: "virtual_snare_drum" },
  gradePreset: "middle_primary",
  metronome: { bpm: 120, meter: "4/4", countInBars: 1, continueDuringPerformance: true, subdivision: "beat" },
  demoSequence: [
    { zoneId: "center", beatOffset: 0, durationBeats: 0.25 },
    { zoneId: "center", beatOffset: 1, durationBeats: 0.25 },
  ],
});
recordClassroomActivityTap(steady, { zoneId: "center", elapsedMs: 0 });
recordClassroomActivityTap(steady, { zoneId: "center", elapsedMs: 500 });
const evidence = finishClassroomActivity(steady);
equal(evidence.correctCount, 2, "steady beat records objective correct taps");
equal(evidence.completed, true, "matched sequence completes");
equal(evidence.taskVersion, "teacher_constrained_instrument_task_v1", "legacy activity adapts its task to the shared contract");
equal(evidence.evidenceStatus, "evidence_pass", "legacy activity receives shared objective evidence");
equal(evidence.restErrorCount, 0, "standard timed activities never report composition rest errors");

const instrumentIdentity = createClassroomActivitySession({ ...steady.config, mode: "free_play" });
recordClassroomActivityTap(instrumentIdentity, { zoneId: "midi-60", midi: 60, elapsedMs: 10 });
equal(instrumentIdentity.performanceEvents[0].midi, 60, "virtual instrument MIDI is preserved in task events");

const gridIdentity = createClassroomActivitySession({
  ...steady.config,
  mode: "free_play",
  target: {
    type: "percussion_grid",
    tiles: [
      { id: "snare-tile", instrumentId: "virtual_snare_drum", zoneId: "center", colorToken: "slate" },
      { id: "frame-tile", instrumentId: "virtual_frame_drum", zoneId: "center", colorToken: "oak" },
    ],
  },
});
recordClassroomActivityTap(gridIdentity, { zoneId: "center", instrumentId: "virtual_frame_drum", elapsedMs: 10 });
equal(gridIdentity.performanceEvents[0].zoneId, "center", "grid zone identity is preserved");
equal(gridIdentity.performanceEvents[0].instrumentId, "virtual_frame_drum", "grid instrument identity is preserved");
equal(gridIdentity.performanceEvents[0].midi, undefined, "grid events do not invent MIDI when the tile did not provide it");

const free = createClassroomActivitySession({ ...steady.config, mode: "free_play" });
recordClassroomActivityTap(free, { zoneId: "rim", elapsedMs: 120 });
equal(finishClassroomActivity(free).correctCount, 0, "free play is never auto-scored");
equal(finishClassroomActivity(free).completed, true, "free play records participation only");
