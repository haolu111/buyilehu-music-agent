import Phaser from "phaser";
import { rhythmFamilyAssets } from "./rhythmFamilyAssets";

export type PatternBuilderStatus = "ready" | "building" | "success" | "failed";
export type PatternBuilderToken = "quarter" | "eighth_pair" | "rest";

export type PatternBuilderSceneConfig = {
  engine?: "phaser_2d";
  scene_id?: "pattern_builder_scene";
  runtime_shell?: "pattern_builder_shell";
  gameplay_variant_id?: "pattern_builder";
  pattern_steps?: string[];
  round_count?: number;
  asset_manifest?: Record<string, string>;
};

export type PatternBuilderSnapshot = {
  status: PatternBuilderStatus;
  target: PatternBuilderToken[];
  placed: PatternBuilderToken[];
  score: number;
  attempts: number;
  progress: number;
  message: string;
};

export type PatternBuilderSceneEvent = {
  type: "start" | "reset" | "place" | "check" | "mission_success" | "mission_failed";
  message?: string;
  snapshot: PatternBuilderSnapshot;
};

export type PatternBuilderController = {
  start: () => void;
  place: (token: PatternBuilderToken) => void;
  check: () => void;
  reset: () => void;
  destroy: () => void;
};

const WIDTH = 960;
const HEIGHT = 520;
const ASSET_KEY = "pattern_builder_bg";
const TOKENS: PatternBuilderToken[] = ["quarter", "eighth_pair", "rest"];

export function buildPatternBuilderSceneConfig(raw: Record<string, unknown>): PatternBuilderSceneConfig {
  const nested = isRecord(raw.scene_config) ? raw.scene_config : {};
  const merged = { ...raw, ...nested };
  return {
    engine: "phaser_2d",
    scene_id: "pattern_builder_scene",
    runtime_shell: "pattern_builder_shell",
    gameplay_variant_id: "pattern_builder",
    pattern_steps: normalizePattern(merged.pattern_steps),
    round_count: clampNumber(Number(merged.round_count), 1, 8, 3),
    asset_manifest: rhythmFamilyAssets(merged)
  };
}

export function mountPatternBuilderScene(
  parent: HTMLElement,
  config: PatternBuilderSceneConfig,
  onEvent: (event: PatternBuilderSceneEvent) => void
): PatternBuilderController {
  const built = buildPatternBuilderSceneConfig(config as Record<string, unknown>);
  const scene = new PatternBuilderScene(built, onEvent);
  const game = new Phaser.Game({
    type: Phaser.AUTO,
    parent,
    width: WIDTH,
    height: HEIGHT,
    backgroundColor: "#243f38",
    scale: { mode: Phaser.Scale.FIT, autoCenter: Phaser.Scale.CENTER_BOTH },
    scene: [scene]
  });
  return {
    start: () => scene.startBuild(),
    place: (token) => scene.placeToken(token),
    check: () => scene.checkPattern(),
    reset: () => scene.resetBuild(),
    destroy: () => game.destroy(true)
  };
}

class PatternBuilderScene extends Phaser.Scene {
  private readonly sceneConfig: Required<PatternBuilderSceneConfig>;
  private readonly onSceneEvent: (event: PatternBuilderSceneEvent) => void;
  private graphics!: Phaser.GameObjects.Graphics;
  private titleText!: Phaser.GameObjects.Text;
  private statusText!: Phaser.GameObjects.Text;
  private backgroundImage: Phaser.GameObjects.Image | null = null;
  private status: PatternBuilderStatus = "ready";
  private placed: PatternBuilderToken[] = [];
  private attempts = 0;
  private score = 0;

  constructor(config: PatternBuilderSceneConfig, onEvent: (event: PatternBuilderSceneEvent) => void) {
    super("pattern_builder_scene");
    this.sceneConfig = buildPatternBuilderSceneConfig(config as Record<string, unknown>) as Required<PatternBuilderSceneConfig>;
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
    this.titleText = this.add.text(34, 24, "节奏工坊", textStyle("30px", true));
    this.statusText = this.add.text(34, 64, "拖节奏卡，拼出目标。", textStyle("19px"));
    TOKENS.forEach((token, index) => {
      const button = this.add.rectangle(190 + index * 170, 414, 132, 62, 0xfff2bd, 0.96).setStrokeStyle(4, 0xf2b84b, 0.85);
      const label = this.add.text(190 + index * 170, 414, tokenLabel(token), {
        color: "#173028",
        fontFamily: "Noto Sans SC, PingFang SC, sans-serif",
        fontSize: "22px",
        fontStyle: "bold"
      }).setOrigin(0.5);
      button.setInteractive({ useHandCursor: true }).on("pointerdown", () => this.placeToken(token));
      label.setInteractive({ useHandCursor: true }).on("pointerdown", () => this.placeToken(token));
    });
    this.input.keyboard?.on("keydown-ENTER", () => this.checkPattern());
    this.renderScene();
  }

  startBuild() {
    this.status = "building";
    this.emitEvent("start", "开始拼节奏");
    this.renderScene();
  }

  placeToken(token: PatternBuilderToken) {
    if (this.status === "ready") this.startBuild();
    if (this.status === "success" || this.status === "failed") return;
    if (this.placed.length >= this.target.length) this.placed = [];
    this.placed.push(token);
    this.emitEvent("place", `${tokenLabel(token)}已放入`);
    if (this.placed.length === this.target.length) this.checkPattern();
    this.renderScene();
  }

  checkPattern() {
    if (this.status === "ready") this.startBuild();
    this.attempts += 1;
    const correct = this.target.every((token, index) => token === this.placed[index]);
    if (correct) {
      this.status = "success";
      this.score = Math.max(100, 520 - this.attempts * 60);
      this.emitEvent("mission_success", "拼成了");
      this.renderScene();
      return;
    }
    this.score = Math.max(0, this.score - 30);
    this.status = this.attempts >= 3 ? "failed" : "building";
    this.cameras.main.shake(120, 0.006);
    this.emitEvent(this.status === "failed" ? "mission_failed" : "check", this.status === "failed" ? "再来" : "顺序不对");
    this.renderScene();
  }

  resetBuild() {
    this.status = "ready";
    this.placed = [];
    this.attempts = 0;
    this.score = 0;
    this.emitEvent("reset", "准备");
    this.renderScene();
  }

  private emitEvent(type: PatternBuilderSceneEvent["type"], message: string) {
    this.statusText?.setText(message);
    this.onSceneEvent({ type, message, snapshot: this.snapshot(message) });
  }

  private snapshot(message: string): PatternBuilderSnapshot {
    return {
      status: this.status,
      target: this.target,
      placed: this.placed,
      score: this.score,
      attempts: this.attempts,
      progress: this.target.length ? this.placed.length / this.target.length : 0,
      message
    };
  }

  private renderScene() {
    if (!this.graphics) return;
    this.graphics.clear();
    if (!this.backgroundImage) this.cameras.main.setBackgroundColor("#243f38");
    this.graphics.fillStyle(0x13283a, 0.48).fillRoundedRect(42, 110, 876, 260, 28);
    this.graphics.fillStyle(0xffffff, 0.22).fillRoundedRect(116, 170, 728, 92, 24);
    this.target.forEach((token, index) => this.drawCard(178 + index * 142, 216, token, 0xfff2bd, 0.44));
    this.graphics.fillStyle(0x07111f, 0.42).fillRoundedRect(116, 286, 728, 76, 22);
    this.placed.forEach((token, index) => this.drawCard(178 + index * 142, 324, token, token === this.target[index] ? 0x8ff0c2 : 0xf2b84b, 0.96));
    this.titleText.setText("节奏工坊");
  }

  private drawCard(x: number, y: number, token: PatternBuilderToken, color: number, alpha: number) {
    this.graphics.fillStyle(color, alpha).fillRoundedRect(x - 54, y - 30, 108, 60, 16);
    this.graphics.lineStyle(3, 0xffffff, 0.52).strokeRoundedRect(x - 54, y - 30, 108, 60, 16);
  }

  private get target(): PatternBuilderToken[] {
    return this.sceneConfig.pattern_steps as PatternBuilderToken[];
  }
}

function normalizePattern(value: unknown): PatternBuilderToken[] {
  if (!Array.isArray(value)) return ["quarter", "eighth_pair", "quarter", "rest"];
  const tokens = value.filter((item): item is PatternBuilderToken => TOKENS.includes(String(item) as PatternBuilderToken));
  return tokens.length ? tokens.slice(0, 5) : ["quarter", "eighth_pair", "quarter", "rest"];
}

function tokenLabel(token: PatternBuilderToken) {
  return {
    quarter: "四分",
    eighth_pair: "二八",
    rest: "休止"
  }[token];
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
