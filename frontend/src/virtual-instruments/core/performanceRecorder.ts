export type PerformanceNoteEvent = {
  type: "note_on" | "note_off";
  timeMs: number;
  midi: number;
  velocity: number;
  zoneId: string;
};

export type PerformanceControlEvent = {
  type: "control_change";
  timeMs: number;
  controller: 64;
  value: 0 | 127;
};

export type PerformanceEvent = PerformanceNoteEvent | PerformanceControlEvent;

export type PerformanceRecording = {
  version: "virtual_instrument_performance_v1" | "virtual_instrument_performance_v2";
  id: string;
  instrumentId: string;
  createdAt: string;
  durationMs: number;
  events: PerformanceEvent[];
};

type PerformanceRecorderOptions = {
  instrumentId: string;
  now?: () => number;
  maxDurationMs?: number;
};

const DEFAULT_MAX_DURATION_MS = 300_000;

export class PerformanceRecorder {
  private readonly now: () => number;
  private readonly maxDurationMs: number;
  private startedAt: number | null = null;
  private events: PerformanceEvent[] = [];

  constructor(private readonly options: PerformanceRecorderOptions) {
    this.now = options.now ?? (() => performance.now());
    this.maxDurationMs = options.maxDurationMs ?? DEFAULT_MAX_DURATION_MS;
  }

  start(): void {
    this.startedAt = this.now();
    this.events = [];
  }

  noteOn(midi: number, velocity: number, zoneId: string): void {
    this.record("note_on", midi, velocity, zoneId);
  }

  noteOff(midi: number, zoneId: string): void {
    this.record("note_off", midi, 0, zoneId);
  }

  setSustain(active: boolean): void {
    if (this.startedAt === null) return;
    const timeMs = Math.max(0, this.now() - this.startedAt);
    if (timeMs > this.maxDurationMs) return;
    this.events.push({ type: "control_change", timeMs, controller: 64, value: active ? 127 : 0 });
  }

  stop(): PerformanceRecording {
    if (this.startedAt === null) throw new Error("Performance recording has not started");
    const durationMs = Math.min(Math.max(0, this.now() - this.startedAt), this.maxDurationMs);
    const recording: PerformanceRecording = {
      version: "virtual_instrument_performance_v2",
      id: globalThis.crypto?.randomUUID?.() ?? `performance-${Date.now()}`,
      instrumentId: this.options.instrumentId,
      createdAt: new Date().toISOString(),
      durationMs,
      events: this.events.map((event) => ({ ...event })),
    };
    this.startedAt = null;
    return recording;
  }

  toMidi(recording: PerformanceRecording, ticksPerQuarter = 480, bpm = 120): Uint8Array {
    const ticksPerMs = (ticksPerQuarter * bpm) / 60_000;
    const ordered = [...recording.events].sort((left, right) => left.timeMs - right.timeMs || eventOrder(left) - eventOrder(right));
    let previousTick = 0;
    const track: number[] = [0x00, 0xff, 0x51, 0x03, 0x07, 0xa1, 0x20];
    for (const event of ordered) {
      const tick = Math.round(event.timeMs * ticksPerMs);
      track.push(...encodeVariableLength(Math.max(0, tick - previousTick)));
      if (event.type === "control_change") track.push(0xb0, event.controller, event.value);
      else track.push(event.type === "note_on" ? 0x90 : 0x80, clampMidi(event.midi), clampMidi(event.velocity));
      previousTick = tick;
    }
    track.push(0x00, 0xff, 0x2f, 0x00);
    return new Uint8Array([
      ...ascii("MThd"), ...uint32(6), 0x00, 0x00, 0x00, 0x01, ...uint16(ticksPerQuarter),
      ...ascii("MTrk"), ...uint32(track.length), ...track,
    ]);
  }

  private record(type: PerformanceNoteEvent["type"], midi: number, velocity: number, zoneId: string): void {
    if (this.startedAt === null) return;
    const timeMs = Math.max(0, this.now() - this.startedAt);
    if (timeMs > this.maxDurationMs) return;
    this.events.push({ type, timeMs, midi: clampMidi(midi), velocity: clampMidi(velocity), zoneId });
  }
}

function eventOrder(event: PerformanceEvent): number {
  if (event.type === "control_change") return 1;
  return event.type === "note_off" ? 0 : 1;
}

function clampMidi(value: number): number {
  return Math.max(0, Math.min(127, Math.round(value)));
}

function ascii(value: string): number[] {
  return [...value].map((character) => character.charCodeAt(0));
}

function uint16(value: number): number[] {
  return [(value >>> 8) & 0xff, value & 0xff];
}

function uint32(value: number): number[] {
  return [(value >>> 24) & 0xff, (value >>> 16) & 0xff, (value >>> 8) & 0xff, value & 0xff];
}

function encodeVariableLength(value: number): number[] {
  const bytes = [value & 0x7f];
  for (let remaining = value >>> 7; remaining > 0; remaining >>>= 7) bytes.unshift((remaining & 0x7f) | 0x80);
  return bytes;
}
