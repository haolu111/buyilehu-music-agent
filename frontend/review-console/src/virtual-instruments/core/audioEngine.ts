export type VirtualInstrumentAudioEngineId = "spessasynth" | "legacy_soundfont";

export interface VirtualInstrumentAudioEngine {
  readonly id: VirtualInstrumentAudioEngineId;
  initialize(instrumentId: string): Promise<void>;
  noteOn(midi: number, velocity: number): void;
  noteOff(midi: number): void;
  setSustain(active: boolean): void;
  allNotesOff(): void;
  destroy(): Promise<void>;
}

export class AudioEngineRouter implements VirtualInstrumentAudioEngine {
  readonly id = "spessasynth" as const;
  activeEngineId: VirtualInstrumentAudioEngineId | null = null;
  fallbackReason: string | null = null;
  private activeEngine: VirtualInstrumentAudioEngine | null = null;

  constructor(
    private readonly primary: VirtualInstrumentAudioEngine,
    private readonly fallback: VirtualInstrumentAudioEngine,
  ) {}

  async initialize(instrumentId: string): Promise<void> {
    await this.activeEngine?.destroy();
    this.activeEngine = null;
    this.activeEngineId = null;
    this.fallbackReason = null;
    // The VCSL frame-drum fallback contains the exact audited center/edge
    // recordings. Its custom SF2 can be parsed without exposing a playable
    // preset in every SpessaSynth/browser combination, which looks "ready"
    // while producing silence. Prefer the deterministic recordings here.
    if (instrumentId === "virtual_frame_drum") {
      this.fallbackReason = "手鼓使用经审计的 VCSL 鼓心/鼓边真实采样";
      await this.fallback.initialize(instrumentId);
      this.activeEngine = this.fallback;
      this.activeEngineId = this.activeEngine.id;
      return;
    }
    try {
      await this.primary.initialize(instrumentId);
      this.activeEngine = this.primary;
    } catch (error) {
      this.fallbackReason = error instanceof Error ? error.message : String(error);
      await this.primary.destroy().catch(() => undefined);
      await this.fallback.initialize(instrumentId);
      this.activeEngine = this.fallback;
    }
    this.activeEngineId = this.activeEngine.id;
  }

  noteOn(midi: number, velocity: number): void {
    this.requireActiveEngine().noteOn(midi, velocity);
  }

  noteOff(midi: number): void {
    this.requireActiveEngine().noteOff(midi);
  }

  setSustain(active: boolean): void {
    this.requireActiveEngine().setSustain(active);
  }

  allNotesOff(): void {
    this.activeEngine?.allNotesOff();
  }

  async destroy(): Promise<void> {
    await this.activeEngine?.destroy();
    this.activeEngine = null;
    this.activeEngineId = null;
  }

  private requireActiveEngine(): VirtualInstrumentAudioEngine {
    if (!this.activeEngine) throw new Error("Virtual instrument audio engine is not initialized");
    return this.activeEngine;
  }
}
