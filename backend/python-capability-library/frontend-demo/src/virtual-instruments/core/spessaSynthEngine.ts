import type { VirtualInstrumentAudioEngine } from "./audioEngine";
import { getAuditedClassroomAudioAsset } from "./virtualInstrumentCatalog";
import { ALL_CLASSROOM_SOUNDBANK_BUILD_SPECS } from "./soundbankBuildPlan";

export type SpessaSynthDriver = {
  initialize(soundbankUrl: string, program: number, drum: boolean): Promise<void>;
  noteOn(channel: number, midi: number, velocity: number): void;
  noteOff(channel: number, midi: number): void;
  setSustain(channel: number, active: boolean): void;
  allNotesOff(): void;
  destroy(): Promise<void>;
};

type SpessaSynthEngineOptions = {
  createDriver?: () => Promise<SpessaSynthDriver>;
  onStage?: (stage: string) => void;
};

export const SPESSA_SYNTH_CONFIG = { oneOutput: false, eventsEnabled: false } as const;

export function withAudioInitializationTimeout<T>(promise: Promise<T>, timeoutMs: number, stage: string): Promise<T> {
  return new Promise((resolve, reject) => {
    const timeout = globalThis.setTimeout(
      () => reject(new Error(`Audio initialization timed out: ${stage}`)),
      timeoutMs,
    );
    promise.then(
      (value) => { globalThis.clearTimeout(timeout); resolve(value); },
      (error) => { globalThis.clearTimeout(timeout); reject(error); },
    );
  });
}

export class SpessaSynthEngine implements VirtualInstrumentAudioEngine {
  readonly id = "spessasynth" as const;
  private driver: SpessaSynthDriver | null = null;
  private channel = 0;
  private readonly createDriver: () => Promise<SpessaSynthDriver>;
  private readonly onStage: (stage: string) => void;

  constructor(options: SpessaSynthEngineOptions = {}) {
    this.onStage = options.onStage ?? (() => undefined);
    this.createDriver = options.createDriver ?? (() => createBrowserSpessaDriver(this.onStage));
  }

  async initialize(instrumentId: string): Promise<void> {
    await this.destroy();
    const asset = getAuditedClassroomAudioAsset(instrumentId);
    const buildSpec = ALL_CLASSROOM_SOUNDBANK_BUILD_SPECS.find((item) => item.instrumentId === instrumentId);
    if (!asset || !buildSpec) throw new Error(`No audited SpessaSynth pack for ${instrumentId}`);
    const driver = await this.createDriver();
    try {
      this.onStage("正在解码 SoundFont");
      await driver.initialize(asset.primary.path, buildSpec.program, buildSpec.drum);
    } catch (error) {
      await driver.destroy().catch(() => undefined);
      throw error;
    }
    this.driver = driver;
    this.channel = buildSpec.drum ? 9 : 0;
  }

  noteOn(midi: number, velocity: number): void {
    this.requireDriver().noteOn(this.channel, midi, velocity);
  }

  noteOff(midi: number): void {
    this.requireDriver().noteOff(this.channel, midi);
  }

  setSustain(active: boolean): void {
    this.requireDriver().setSustain(this.channel, active);
  }

  allNotesOff(): void {
    this.driver?.allNotesOff();
  }

  async destroy(): Promise<void> {
    if (!this.driver) return;
    const driver = this.driver;
    this.driver = null;
    await driver.destroy();
  }

  private requireDriver(): SpessaSynthDriver {
    if (!this.driver) throw new Error("SpessaSynth engine is not initialized");
    return this.driver;
  }
}

async function createBrowserSpessaDriver(onStage: (stage: string) => void): Promise<SpessaSynthDriver> {
  onStage("正在载入 SpessaSynth");
  const context = new AudioContext({ latencyHint: "interactive" });
  const resumePromise = context.state === "running" ? Promise.resolve() : context.resume();
  let synthesizer: import("spessasynth_lib").WorkletSynthesizer | null = null;
  try {
    const { WorkletSynthesizer } = await import("spessasynth_lib");
    onStage("正在启用设备音频");
    await withAudioInitializationTimeout(resumePromise, 3_000, "audio context resume");
    const processorUrl = new URL(
      "../../../node_modules/spessasynth_lib/dist/spessasynth_processor.min.js",
      import.meta.url,
    );
    await context.audioWorklet.addModule(processorUrl);
    onStage("正在创建音频工作线程");
    synthesizer = new WorkletSynthesizer(context, SPESSA_SYNTH_CONFIG);
    synthesizer.connect(context.destination);
    onStage("正在等待音频工作线程");
    await withAudioInitializationTimeout(synthesizer.isReady, 8_000, "SpessaSynth worklet ready");
  } catch (error) {
    synthesizer?.destroy();
    await context.close().catch(() => undefined);
    throw error;
  }

  return {
    async initialize(soundbankUrl, program, drum) {
      const response = await fetch(soundbankUrl);
      if (!response.ok) throw new Error(`SoundFont load failed (${response.status}): ${soundbankUrl}`);
      await withAudioInitializationTimeout(
        synthesizer!.soundBankManager.addSoundBank(await response.arrayBuffer(), "virtual-instrument-pack"),
        12_000,
        "SoundFont decode",
      );
      if (drum) synthesizer!.midiChannels[9]?.setDrums(true);
      synthesizer!.programChange(drum ? 9 : 0, program);
    },
    noteOn: (channel, midi, velocity) => synthesizer!.noteOn(channel, midi, velocity),
    noteOff: (channel, midi) => synthesizer!.noteOff(channel, midi),
    setSustain: (channel, active) => synthesizer!.controllerChange(channel, 64, active ? 127 : 0),
    allNotesOff: () => synthesizer!.stopAll(true),
    async destroy() {
      synthesizer?.stopAll(true);
      synthesizer?.destroy();
      if (context.state !== "closed") await context.close();
    },
  };
}
