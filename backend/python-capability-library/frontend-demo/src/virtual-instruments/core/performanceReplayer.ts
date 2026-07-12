import type { PerformanceRecording } from "./performanceRecorder";

type PerformanceReplayerOptions = {
  schedule?: (run: () => void, delayMs: number) => unknown;
  cancel?: (handle: unknown) => void;
  noteOn: (midi: number, velocity: number) => void;
  noteOff: (midi: number) => void;
  setSustain?: (active: boolean) => void;
  allNotesOff: () => void;
  onComplete?: () => void;
};

export class PerformanceReplayer {
  private readonly scheduled = new Set<unknown>();
  private readonly schedule: (run: () => void, delayMs: number) => unknown;
  private readonly cancelScheduled: (handle: unknown) => void;

  constructor(private readonly options: PerformanceReplayerOptions) {
    this.schedule = options.schedule ?? ((run, delayMs) => globalThis.setTimeout(run, delayMs));
    this.cancelScheduled = options.cancel ?? ((handle) => globalThis.clearTimeout(handle as number));
  }

  play(recording: PerformanceRecording): void {
    this.stop();
    for (const event of recording.events) {
      this.scheduled.add(this.schedule(() => {
        if (event.type === "note_on") this.options.noteOn(event.midi, event.velocity);
        else if (event.type === "note_off") this.options.noteOff(event.midi);
        else if (event.type === "control_change") this.options.setSustain?.(event.value === 127);
      }, event.timeMs));
    }
    this.scheduled.add(this.schedule(() => {
      this.scheduled.clear();
      this.options.allNotesOff();
      this.options.onComplete?.();
    }, recording.durationMs));
  }

  stop(): void {
    for (const handle of this.scheduled) this.cancelScheduled(handle);
    if (this.scheduled.size > 0) this.options.allNotesOff();
    this.scheduled.clear();
  }
}
