import Phaser from "phaser";
import { rhythmFamilyAssets } from "./rhythmFamilyAssets";

export type RaceTimingStatus = "ready" | "count_in" | "racing" | "success" | "failed";
export type RaceTimingJudgement = "perfect" | "good" | "early" | "late" | "missed" | "too_early";

export type RaceTimingSceneConfig = {
  engine?: "phaser_2d";
  scene_id?: "race_timing_scene";
  runtime_shell?: "race_timing_shell";
  gameplay_variant_id?: "race_timing";
  meter?: string;
  bpm?: number;
  round_count?: number;
  count_in_beats?: number;
  combo_required?: number;
  mistake_limit?: number;
  energy_max?: number;
  asset_manifest?: Record<string, string>;
};

export type RaceTimingSnapshot = {
  status: RaceTimingStatus;
  beat: number;
  totalBeats: number;
  hits: number;
  misses: number;
  combo: number;
  maxCombo: number;
  requiredCombo: number;
  score: number;
  energy: number;
  energyMax: number;
  progress: number;
  message: string;
  lastJudgement?: RaceTimingJudgement;
};

export type RaceTimingSceneEvent = {
  type: "start" | "reset" | "tap" | "beat_tick" | "judgement" | "mission_success" | "mission_failed";
  judgement?: RaceTimingJudgement;
  message?: string;
  snapshot: RaceTimingSnapshot;
};

export type RaceTimingController = {
  start: () => void;
  tap: () => void;
  reset: () => void;
  destroy: () => void;
};

const WIDTH = 960;
const HEIGHT = 520;
const ASSET_KEY = "race_timing_bg";

export function buildRaceTimingSceneConfig(raw: Record<string, unknown>): RaceTimingSceneConfig {
  const nested = isRecord(raw.scene_config) ? raw.scene_config : {};
  const merged = { ...raw, ...nested };
  return {
    engine: "phaser_2d",
    scene_id: "race_timing_scene",
    runtime_shell: "race_timing_shell",
    gameplay_variant_id: "race_timing",
    meter: String(merged.meter || "2/4"),
    bpm: clampNumber(Number(merged.bpm), 60, 140, 96),
    round_count: clampNumber(Number(merged.round_count), 3, 12, 5),
    count_in_beats: clampNumber(Number(merged.count_in_beats), 0, 8, 4),
    combo_required: clampNumber(Number(merged.combo_required), 2, 12, 4),
    mistake_limit: clampNumber(Number(merged.mistake_limit), 1, 8, 3),
    energy_max: clampNumber(Number(merged.energy_max), 50, 150, 100),
    asset_manifest: rhythmFamilyAssets(merged).background ? rhythmFamilyAssets(merged) : undefined
  };
}

export function mountRaceTimingScene(
  parent: HTMLElement,
  config: RaceTimingSceneConfig,
  onEvent: (event: RaceTimingSceneEvent) => void
): RaceTimingController {
  const built = buildRaceTimingSceneConfig(config as Record<string, unknown>);
  const scene = new RaceTimingScene(built, onEvent);
  const game = new Phaser.Game({
    type: Phaser.AUTO,
    parent,
    width: WIDTH,
    height: HEIGHT,
    backgroundColor: "#0f6f73",
    scale: { mode: Phaser.Scale.FIT, autoCenter: Phaser.Scale.CENTER_BOTH },
    scene: [scene]
  });
  return {
    start: () => scene.startRace(),
    tap: () => scene.tapBeat(),
    reset: () => scene.resetRace(),
    destroy: () => game.destroy(true)
  };
}

class RaceTimingScene extends Phaser.Scene {
  private readonly sceneConfig: Required<RaceTimingSceneConfig>;
  private readonly onSceneEvent: (event: RaceTimingSceneEvent) => void;
  private graphics!: Phaser.GameObjects.Graphics;
  private titleText!: Phaser.GameObjects.Text;
  private statusText!: Phaser.GameObjects.Text;
  private scoreText!: Phaser.GameObjects.Text;
  private backgroundImage: Phaser.GameObjects.Image | null = null;
  private status: RaceTimingStatus = "ready";
  private startAt = 0;
  private lastBeat = 0;
  private hits = 0;
  private misses = 0;
  private combo = 0;
  private maxCombo = 0;
  private score = 0;
  private energy = 100;
  private lastJudgement: RaceTimingJudgement | undefined;

  constructor(config: RaceTimingSceneConfig, onEvent: (event: RaceTimingSceneEvent) => void) {
    super("race_timing_scene");
    this.sceneConfig = buildRaceTimingSceneConfig(config as Record<string, unknown>) as Required<RaceTimingSceneConfig>;
    this.energy = this.sceneConfig.energy_max;
    this.onSceneEvent = onEvent;
  }

  preload() {
    const background = this.sceneConfig.asset_manifest?.background;
    if (background) this.load.image(ASSET_KEY, background);
  }

  create() {
    if (this.textures.exists(ASSET_KEY)) {
      this.backgroundImage = this.add.image(WIDTH / 2, HEIGHT / 2, ASSET_KEY).setDisplaySize(WIDTH, HEIGHT).setDepth(-10);
    }
    this.graphics = this.add.graphics();
    this.titleText = this.add.text(34, 24, "节拍竞速", textStyle("30px", true));
    this.statusText = this.add.text(34, 64, "按开始，跟稳拍点冲刺。", textStyle("19px"));
    this.scoreText = this.add.text(WIDTH - 36, 28, "0", textStyle("30px", true)).setOrigin(1, 0);
    this.input.on("pointerdown", () => this.tapBeat());
    this.renderScene();
  }

  update() {
    if (this.status !== "count_in" && this.status !== "racing") return;
    if (this.time.now < this.startAt) {
      this.renderScene();
      return;
    }
    if (this.status === "count_in") {
      this.status = "racing";
      this.emitEvent("start", "开始冲刺");
    }
    const beat = Math.floor((this.time.now - this.startAt) / this.beatMs) + 1;
    if (beat !== this.lastBeat && beat <= this.totalBeats) {
      this.lastBeat = beat;
      this.emitEvent("beat_tick", "听稳");
    }
    if (beat > this.totalBeats + 1) this.finish(this.progress >= 0.82 && this.energy > 0, this.progress >= 0.82 ? "冲线" : "再来");
    this.renderScene();
  }

  startRace() {
    this.resetCounters();
    this.status = "count_in";
    this.startAt = this.time.now + this.sceneConfig.count_in_beats * this.beatMs;
    this.emitEvent("start", "预备拍");
    this.renderScene();
  }

  tapBeat() {
    this.emitEvent("tap", "");
    if (this.status === "ready" || this.status === "count_in") {
      this.emitJudgement("too_early", this.status === "ready" ? "先开始" : "等拍点");
      return;
    }
    if (this.status === "success" || this.status === "failed") return;
    const beatFloat = (this.time.now - this.startAt) / this.beatMs;
    const nearestBeat = Math.round(beatFloat) + 1;
    const diffMs = this.time.now - (this.startAt + (nearestBeat - 1) * this.beatMs);
    const abs = Math.abs(diffMs);
    if (nearestBeat < 1 || nearestBeat > this.totalBeats) {
      this.penalty("late", "晚了");
      return;
    }
    if (abs <= 80) this.hit("perfect", "完美");
    else if (abs <= 170) this.hit(diffMs < 0 ? "early" : "good", diffMs < 0 ? "稍早" : "拍准了");
    else this.penalty(diffMs < 0 ? "early" : "late", diffMs < 0 ? "早了" : "晚了");
  }

  resetRace() {
    this.resetCounters();
    this.status = "ready";
    this.emitEvent("reset", "准备");
    this.renderScene();
  }

  private hit(judgement: "perfect" | "good" | "early", message: string) {
    this.hits += 1;
    this.combo += 1;
    this.maxCombo = Math.max(this.maxCombo, this.combo);
    this.score += judgement === "perfect" ? 140 : judgement === "good" ? 95 : 55;
    this.energy = Math.min(this.sceneConfig.energy_max, this.energy + 3);
    this.emitJudgement(judgement, message);
    if (this.combo >= this.sceneConfig.combo_required && this.progress >= 0.9) this.finish(true, "冲线");
  }

  private penalty(judgement: "early" | "late" | "missed", message: string) {
    this.misses += 1;
    this.combo = 0;
    this.score -= 45;
    this.energy = Math.max(0, this.energy - 22);
    this.cameras.main.shake(110, 0.006);
    this.emitJudgement(judgement, message);
    if (this.misses >= this.sceneConfig.mistake_limit || this.energy <= 0) this.finish(false, "再来");
  }

  private finish(success: boolean, message: string) {
    if (this.status === "success" || this.status === "failed") return;
    this.status = success ? "success" : "failed";
    this.emitEvent(success ? "mission_success" : "mission_failed", message);
    this.renderScene();
  }

  private emitJudgement(judgement: RaceTimingJudgement, message: string) {
    this.lastJudgement = judgement;
    this.emitEvent("judgement", message, judgement);
    this.renderScene();
  }

  private emitEvent(type: RaceTimingSceneEvent["type"], message: string, judgement?: RaceTimingJudgement) {
    this.statusText?.setText(message || "听稳");
    this.onSceneEvent({ type, judgement, message, snapshot: this.snapshot(message || "听稳") });
  }

  private snapshot(message: string): RaceTimingSnapshot {
    return {
      status: this.status,
      beat: Math.max(0, this.lastBeat),
      totalBeats: this.totalBeats,
      hits: this.hits,
      misses: this.misses,
      combo: this.combo,
      maxCombo: this.maxCombo,
      requiredCombo: this.sceneConfig.combo_required,
      score: this.score,
      energy: this.energy,
      energyMax: this.sceneConfig.energy_max,
      progress: this.progress,
      lastJudgement: this.lastJudgement,
      message
    };
  }

  private renderScene() {
    if (!this.graphics) return;
    this.graphics.clear();
    if (!this.backgroundImage) this.cameras.main.setBackgroundColor("#0f6f73");
    this.graphics.fillStyle(0x0b2630, 0.44).fillRoundedRect(30, 105, 900, 280, 28);
    this.graphics.lineStyle(5, 0xfff2bd, 0.8).lineBetween(810, 146, 810, 350);
    for (let index = 0; index < 8; index += 1) {
      const x = 100 + index * 90;
      this.graphics.fillStyle(index % 2 ? 0xffffff : 0xf2b84b, 0.24).fillRoundedRect(x, 318, 58, 30, 8);
    }
    const x = 90 + this.progress * 710;
    this.graphics.fillStyle(0xf2b84b, 1).fillRoundedRect(x, 236, 138, 56, 24);
    this.graphics.fillStyle(0x0b2630, 1).fillCircle(x + 34, 302, 16).fillCircle(x + 104, 302, 16);
    this.graphics.fillStyle(0xfff2bd, 0.96).fillCircle(x + 110, 220, 18 + Math.min(this.combo, 8));
    this.graphics.fillStyle(0xffffff, 0.22).fillRoundedRect(34, 478, 316, 18, 9);
    this.graphics.fillStyle(this.energy <= 28 ? 0xe4573d : 0xf2b84b, 0.96).fillRoundedRect(34, 478, Math.max(8, 316 * (this.energy / this.sceneConfig.energy_max)), 18, 9);
    this.graphics.fillStyle(0xffffff, 0.22).fillRoundedRect(610, 478, 316, 18, 9);
    this.graphics.fillStyle(0xfff2bd, 0.95).fillRoundedRect(610, 478, Math.max(8, 316 * this.progress), 18, 9);
    this.titleText.setText("节拍竞速");
    this.scoreText.setText(String(Math.max(0, this.score)));
  }

  private resetCounters() {
    this.lastBeat = 0;
    this.hits = 0;
    this.misses = 0;
    this.combo = 0;
    this.maxCombo = 0;
    this.score = 0;
    this.energy = this.sceneConfig.energy_max;
    this.lastJudgement = undefined;
  }

  private get beatMs() {
    return 60000 / this.sceneConfig.bpm;
  }

  private get totalBeats() {
    return this.sceneConfig.round_count * 4;
  }

  private get progress() {
    return Math.min(1, (this.hits * 1.25 + this.combo * 0.35) / Math.max(1, this.sceneConfig.combo_required * 2.1));
  }
}

function textStyle(fontSize: string, bold = false): Phaser.Types.GameObjects.Text.TextStyle {
  return {
    color: "#fff8dd",
    fontFamily: "Noto Sans SC, PingFang SC, sans-serif",
    fontSize,
    fontStyle: bold ? "bold" : undefined
  };
}

function clampNumber(value: number, min: number, max: number, fallback: number) {
  if (!Number.isFinite(value)) return fallback;
  return Math.max(min, Math.min(max, Math.round(value)));
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value && typeof value === "object" && !Array.isArray(value));
}
