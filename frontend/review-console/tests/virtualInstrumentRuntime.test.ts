import { AudioEngineRouter, type VirtualInstrumentAudioEngine } from "../src/virtual-instruments/core/audioEngine";
import { PerformanceRecorder } from "../src/virtual-instruments/core/performanceRecorder";
import { PerformanceReplayer } from "../src/virtual-instruments/core/performanceReplayer";
import { PointerPerformanceController } from "../src/virtual-instruments/core/pointerPerformanceController";

function assertEqual<T>(actual: T, expected: T, label: string) {
  if (actual !== expected) throw new Error(`${label}: expected ${String(expected)}, got ${String(actual)}`);
}

{
  const scheduled: Array<{ delay: number; run: () => void }> = [];
  const played: string[] = [];
  const replayer = new PerformanceReplayer({
    schedule: (run, delay) => {
      scheduled.push({ delay, run });
      return scheduled.length;
    },
    cancel: () => undefined,
    noteOn: (midi, velocity) => played.push(`on:${midi}:${velocity}`),
    noteOff: (midi) => played.push(`off:${midi}`),
    allNotesOff: () => played.push("all-off"),
  });
  replayer.play({
    version: "virtual_instrument_performance_v1",
    id: "recording-1",
    instrumentId: "virtual_piano",
    createdAt: "2026-07-11T00:00:00.000Z",
    durationMs: 500,
    events: [
      { type: "note_on", timeMs: 120, midi: 60, velocity: 96, zoneId: "C4" },
      { type: "note_off", timeMs: 480, midi: 60, velocity: 0, zoneId: "C4" },
    ],
  });
  assertDeepEqual(scheduled.map((item) => item.delay), [120, 480, 500], "replay uses exact recorded event timing and completion");
  scheduled.forEach((item) => item.run());
  assertDeepEqual(played, ["on:60:96", "off:60", "all-off"], "replay sends recorded note events and cleans up at the end");
}

function assertDeepEqual(actual: unknown, expected: unknown, label: string) {
  const left = JSON.stringify(actual);
  const right = JSON.stringify(expected);
  if (left !== right) throw new Error(`${label}: expected ${right}, got ${left}`);
}

class FakeEngine implements VirtualInstrumentAudioEngine {
  readonly calls: string[] = [];

  constructor(
    readonly id: "spessasynth" | "legacy_soundfont",
    private readonly failInitialize = false,
  ) {}

  async initialize(instrumentId: string) {
    this.calls.push(`initialize:${instrumentId}`);
    if (this.failInitialize) throw new Error("engine unavailable");
  }

  noteOn(midi: number, velocity: number) {
    this.calls.push(`on:${midi}:${velocity}`);
  }

  noteOff(midi: number) {
    this.calls.push(`off:${midi}`);
  }

  setSustain(active: boolean) {
    this.calls.push(`sustain:${active}`);
  }

  allNotesOff() {
    this.calls.push("all-off");
  }

  async destroy() {
    this.calls.push("destroy");
  }
}

{
  const primary = new FakeEngine("spessasynth", true);
  const fallback = new FakeEngine("legacy_soundfont");
  const router = new AudioEngineRouter(primary, fallback);
  await router.initialize("virtual_piano");
  assertEqual(router.activeEngineId, "legacy_soundfont", "fallback becomes active after primary initialization fails");
  assertEqual(router.fallbackReason, "engine unavailable", "fallback exposes the primary failure reason");
  router.noteOn(60, 96);
  router.noteOff(60);
  router.setSustain(true);
  assertDeepEqual(fallback.calls, ["initialize:virtual_piano", "on:60:96", "off:60", "sustain:true"], "router forwards playback and sustain to fallback");
}

{
  let now = 1000;
  const recorder = new PerformanceRecorder({ instrumentId: "virtual_piano", now: () => now });
  recorder.start();
  now = 1120;
  recorder.noteOn(60, 96, "key-c4");
  now = 1480;
  recorder.noteOff(60, "key-c4");
  now = 1600;
  recorder.setSustain(true);
  now = 1900;
  recorder.setSustain(false);
  now = 301_001;
  recorder.noteOn(64, 96, "key-e4");
  const recording = recorder.stop();
  assertEqual(recording.version, "virtual_instrument_performance_v2", "new recordings declare the sustain-capable v2 contract");
  assertEqual(recording.durationMs, 300_000, "recording duration is capped at five minutes");
  assertEqual(recording.events.length, 4, "note and sustain events are recorded while events after five minutes are discarded");
  assertDeepEqual(recording.events.map((event) => event.timeMs), [120, 480, 600, 900], "recording stores relative event timing");
  const midi = recorder.toMidi(recording);
  assertEqual(String.fromCharCode(...midi.slice(0, 4)), "MThd", "MIDI export has a standard header");
  assertEqual([...midi].some((value, index, bytes) => value === 0xb0 && bytes[index + 1] === 64), true, "MIDI export contains sustain CC64");
}

{
  const events: string[] = [];
  const controller = new PointerPerformanceController({
    resolveZone: (target) => String(target),
    getMidiForZone: (zoneId) => (zoneId === "left" ? 60 : 64),
    noteOn: (midi, velocity, zoneId) => events.push(`on:${zoneId}:${midi}:${velocity}`),
    noteOff: (midi, zoneId) => events.push(`off:${zoneId}:${midi}`),
  });
  controller.pointerDown({ pointerId: 1, pressure: 0.5, target: "left" });
  controller.pointerDown({ pointerId: 2, pressure: 0, target: "right" });
  controller.pointerMove({ pointerId: 1, pressure: 0.75, target: "right" });
  controller.pointerUp({ pointerId: 1 });
  controller.cancelAll();
  assertDeepEqual(
    events,
    ["on:left:60:64", "on:right:64:96", "off:left:60", "on:right:64:95", "off:right:64", "off:right:64"],
    "controller supports concurrent pointers, slide transitions, pressure velocity and complete cleanup",
  );
}
