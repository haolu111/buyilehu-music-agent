import Phaser from "phaser";
import { resolvePitchToken } from "../shared/pitchCatalog";
import { resolveSolfegeTargetShot } from "./solfegeTargetLogic";
import { TemplateCharacterPresenter } from "./templateCharacterPresenter";
import { templateVisualPackForConfig } from "./templateVisualAssets";
import type { TemplatePoseKey, TemplateVisualPack } from "./types";

export type SolfegeTargetPlayMode = "star" | "flower" | "lantern" | "archery" | "bubble";
export type SolfegeTargetStatus = "ready" | "listening" | "aiming" | "sing_back" | "success" | "failed";
export type SolfegeTargetJudgement = "hit" | "miss" | "combo" | "sing_back_ready" | "sing_back_confirmed";
export type SolfegeTargetMode = "single_target" | "aim_and_sing" | "target_chain";
export type SolfegeTargetAudioMode = "internal_pitch" | "lesson_audio" | "hybrid";
export type SolfegeTargetMistakeReason = "wrong_target" | "chain_wrong";

type TargetLayoutItem = {
  id: string;
  note: string;
  label: string;
  midi_offset: number;
  x: number;
  y: number;
};

type SolfegeRound = {
  id?: string;
  sequence?: string[];
  labels?: string[];
  midi_offsets?: number[];
  answer?: string | string[];
  sing_back_required?: boolean;
  teacher_confirm_required?: boolean;
};

type FxProfile = {
  hit: string;
  miss: string;
  success: string;
};

type ScoreModel = {
  perfect: number;
  good: number;
  wrong: number;
  missed: number;
};

type TargetMotionProfile = {
  float_amplitude: number;
  float_speed: number;
  orbit_jitter: number;
};

type AssetRoleMap = {
  launcher: string;
  projectile: string;
  trail: string;
  target_primary: string;
  target_secondary: string;
  gate: string;
  combo: string;
  miss: string;
  medal: string;
};

export type SolfegeTargetSceneConfig = {
  engine?: "phaser_2d";
  scene_id?: "solfege_target_scene";
  runtime_shell?: "solfege_target_shell";
  game_feel?: "solfege_target_range";
  skin_id?: string;
  skin_play_mode?: SolfegeTargetPlayMode;
  mode?: string;
  current_mode?: SolfegeTargetMode;
  target_solfege?: string[];
  solfege_rounds?: SolfegeRound[];
  target_rounds?: SolfegeRound[];
  target_layout?: TargetLayoutItem[];
  energy_max?: number;
  mistake_limit?: number;
  combo_milestones?: number[];
  sing_back_required?: boolean;
  teacher_confirm_required?: boolean;
  mic_assist_enabled?: boolean;
  audio_mode?: SolfegeTargetAudioMode;
  input_map?: { primary?: string; pointer?: boolean };
  fx_profile?: Partial<FxProfile>;
  score_model?: Partial<ScoreModel>;
  arcade_play_model?: "bubble_target_chain";
  target_motion_profile?: Partial<TargetMotionProfile>;
  asset_role_map?: Partial<AssetRoleMap>;
  target_hud?: boolean;
  show_teacher_text_in_play?: boolean;
  asset_manifest?: TemplateVisualPack;
};

export type SolfegeTargetSnapshot = {
  status: SolfegeTargetStatus;
  currentRound: number;
  totalRounds: number;
  currentMode: SolfegeTargetMode;
  sequence: string[];
  labels: string[];
  answer: string[];
  selected: string[];
  expectedNote?: string;
  lastChosenNote?: string;
  lastShotIndex?: number;
  nextExpectedNote?: string;
  mistakeReason?: SolfegeTargetMistakeReason;
  combo: number;
  maxCombo: number;
  score: number;
  hits: number;
  misses: number;
  cleared: number;
  energy: number;
  energyMax: number;
  mistakeLimit: number;
  progress: number;
  skinObjective: string;
  audioMode: SolfegeTargetAudioMode;
  audioLabel: string;
  singBackRequired: boolean;
  teacherConfirmRequired: boolean;
  singBackConfirmed: boolean;
  micAssistEnabled: boolean;
  lastJudgement?: SolfegeTargetJudgement;
  message: string;
};

export type SolfegeTargetSceneEvent = {
  type:
    | "listen"
    | "aim"
    | "fire"
    | "hit"
    | "miss"
    | "combo"
    | "sing_back_ready"
    | "sing_back_confirmed"
    | "mission_success"
    | "mission_failed"
    | "reset";
  judgement?: SolfegeTargetJudgement;
  message?: string;
  snapshot: SolfegeTargetSnapshot;
};

export type SolfegeTargetController = {
  listen: () => void;
  fire: (note: string) => void;
  confirmSingBack: () => void;
  reset: () => void;
  destroy: () => void;
};

const WIDTH = 960;
const HEIGHT = 540;
const BACKGROUND_ASSET_KEY = "solfege_target_template_bg";
const HERO_ASSET_KEYS: Record<TemplatePoseKey, string> = {
  idle: "solfege_target_pose_idle",
  action: "solfege_target_pose_action",
  miss: "solfege_target_pose_miss",
  win: "solfege_target_pose_win"
};
const PROP_ASSET_KEYS = Array.from({ length: 12 }, (_, index) => `solfege_target_prop_${index + 1}`);
const REWARD_ASSET_KEYS = Array.from({ length: 12 }, (_, index) => `solfege_target_reward_${index + 1}`);
const LAUNCHER_POINT = { x: 210, y: 420 };
const TARGET_ARENA = {
  minX: 316,
  maxX: 704,
  minY: 152,
  maxY: 374
};

type NormalizedSolfegeTargetSceneConfig = Omit<
  Required<SolfegeTargetSceneConfig>,
  "asset_role_map" | "combo_milestones" | "fx_profile" | "input_map" | "score_model" | "target_motion_profile"
> & {
  asset_role_map: AssetRoleMap;
  combo_milestones: number[];
  fx_profile: FxProfile;
  input_map: { primary: string; pointer: boolean };
  score_model: ScoreModel;
  target_motion_profile: TargetMotionProfile;
};

type TargetView = {
  item: TargetLayoutItem;
  container: Phaser.GameObjects.Container;
  baseX: number;
  baseY: number;
  floatSeed: number;
  shadow: Phaser.GameObjects.Ellipse;
  glow: Phaser.GameObjects.Arc;
  baseDisk: Phaser.GameObjects.Arc;
  outerRing: Phaser.GameObjects.Arc;
  midRing: Phaser.GameObjects.Arc;
  innerRing: Phaser.GameObjects.Arc;
  crosshairH: Phaser.GameObjects.Rectangle;
  crosshairV: Phaser.GameObjects.Rectangle;
  label: Phaser.GameObjects.Text;
  clearedBadge: Phaser.GameObjects.Text | Phaser.GameObjects.Arc;
};

const palettes: Record<SolfegeTargetPlayMode, { bg: number; deep: number; target: number; accent: number; soft: number; danger: number }> = {
  star: { bg: 0x101f35, deep: 0x071120, target: 0xfff2bd, accent: 0xf2c94c, soft: 0x5874c9, danger: 0xff6b6b },
  flower: { bg: 0x7fbf9d, deep: 0x315c46, target: 0xfff1c7, accent: 0xf29ac2, soft: 0xbee8c5, danger: 0xe55d5d },
  lantern: { bg: 0x2f2234, deep: 0x1a1022, target: 0xffdf8a, accent: 0xff8d50, soft: 0x86515b, danger: 0xff5f4a },
  archery: { bg: 0x334d5f, deep: 0x172936, target: 0xfff5cf, accent: 0xf1b14a, soft: 0x7aa8b8, danger: 0xd94f3d },
  bubble: { bg: 0x86d8e8, deep: 0x2e7188, target: 0xffffff, accent: 0xffc85f, soft: 0xb8eef5, danger: 0xe45c7a }
};

export function buildSolfegeTargetSceneConfig(raw: Record<string, unknown>): SolfegeTargetSceneConfig {
  const nested = isRecord(raw.scene_config) ? raw.scene_config : {};
  const merged = { ...raw, ...nested };
  const notes = normalizeNotes(merged.target_solfege);
  const skinId = String(merged.skin_id || "star_target");
  const playMode = normalizePlayMode(merged.skin_play_mode, skinId);
  return {
    engine: "phaser_2d",
    scene_id: "solfege_target_scene",
    runtime_shell: "solfege_target_shell",
    game_feel: "solfege_target_range",
    skin_id: skinId,
    skin_play_mode: playMode,
    mode: String(merged.mode || "listen_and_hit"),
    current_mode: normalizeMode(merged.current_mode, merged.mode),
    target_solfege: notes,
    solfege_rounds: normalizeRounds(merged.solfege_rounds || merged.target_rounds, notes),
    target_rounds: normalizeRounds(merged.target_rounds || merged.solfege_rounds, notes),
    target_layout: normalizeLayout(merged.target_layout, notes, playMode),
    energy_max: clampNumber(Number(merged.energy_max), 50, 150, 100),
    mistake_limit: clampNumber(Number(merged.mistake_limit), 1, 10, 3),
    combo_milestones: normalizeComboMilestones(merged.combo_milestones),
    sing_back_required: merged.sing_back_required !== false,
    teacher_confirm_required: merged.teacher_confirm_required !== false,
    mic_assist_enabled: merged.mic_assist_enabled !== false,
    audio_mode: normalizeAudioMode(merged.audio_mode),
    input_map: normalizeInputMap(merged.input_map),
    fx_profile: normalizeFxProfile(merged.fx_profile),
    score_model: normalizeScoreModel(merged.score_model),
    arcade_play_model: "bubble_target_chain",
    target_motion_profile: normalizeTargetMotionProfile(merged.target_motion_profile),
    asset_role_map: normalizeAssetRoleMap(merged.asset_role_map),
    target_hud: true,
    show_teacher_text_in_play: false,
    asset_manifest: templateVisualPackForConfig(merged, "solfege_target_core")
  };
}

export function mountSolfegeTargetScene(
  parent: HTMLElement,
  config: SolfegeTargetSceneConfig,
  onEvent: (event: SolfegeTargetSceneEvent) => void
): SolfegeTargetController {
  const built = buildSolfegeTargetSceneConfig(config as Record<string, unknown>);
  const scene = new SolfegeTargetScene(built, onEvent);
  const game = new Phaser.Game({
    type: Phaser.AUTO,
    parent,
    width: WIDTH,
    height: HEIGHT,
    backgroundColor: palettes[built.skin_play_mode || "star"].bg,
    scale: {
      mode: Phaser.Scale.FIT,
      autoCenter: Phaser.Scale.CENTER_BOTH
    },
    scene: [scene]
  });

  return {
    listen: () => scene.listenTarget(),
    fire: (note: string) => scene.fireAt(note),
    confirmSingBack: () => scene.confirmSingBack(),
    reset: () => scene.resetMission(),
    destroy: () => game.destroy(true)
  };
}

class SolfegeTargetScene extends Phaser.Scene {
  private readonly sceneConfig: NormalizedSolfegeTargetSceneConfig;
  private readonly onSceneEvent: (event: SolfegeTargetSceneEvent) => void;
  private graphics!: Phaser.GameObjects.Graphics;
  private statusText!: Phaser.GameObjects.Text;
  private scoreText!: Phaser.GameObjects.Text;
  private gateProgress!: Phaser.GameObjects.Graphics;
  private targetViews: TargetView[] = [];
  private activeTweens: Phaser.Tweens.Tween[] = [];
  private starGate: Phaser.GameObjects.Container | null = null;
  private status: SolfegeTargetStatus = "ready";
  private currentRound = 0;
  private selected: string[] = [];
  private combo = 0;
  private maxCombo = 0;
  private score = 0;
  private hits = 0;
  private misses = 0;
  private cleared = 0;
  private energy = 100;
  private message = "听目标音";
  private lastJudgement: SolfegeTargetJudgement | undefined;
  private singBackConfirmedRound: number | null = null;
  private lastChosenNote: string | undefined;
  private lastExpectedNote: string | undefined;
  private lastShotIndex: number | undefined;
  private mistakeReason: SolfegeTargetMistakeReason | undefined;
  private backgroundImage: Phaser.GameObjects.Image | null = null;
  private heroPresenter: TemplateCharacterPresenter | null = null;
  private launcherImage: Phaser.GameObjects.Image | null = null;
  private rewardImages: Phaser.GameObjects.Image[] = [];

  constructor(config: SolfegeTargetSceneConfig, onEvent: (event: SolfegeTargetSceneEvent) => void) {
    super("solfege_target_scene");
    this.sceneConfig = normalizeRequiredConfig(config);
    this.onSceneEvent = onEvent;
    this.energy = this.sceneConfig.energy_max;
  }

  preload() {
    const background = this.sceneConfig.asset_manifest?.background;
    if (background) this.load.image(BACKGROUND_ASSET_KEY, background);
    (Object.keys(HERO_ASSET_KEYS) as TemplatePoseKey[]).forEach((pose) => {
      const source = this.sceneConfig.asset_manifest?.poses?.[pose];
      if (source) this.load.image(HERO_ASSET_KEYS[pose], source);
    });
    this.sceneConfig.asset_manifest?.props?.slice(0, PROP_ASSET_KEYS.length).forEach((source, index) => {
      if (source) this.load.image(PROP_ASSET_KEYS[index], source);
    });
    this.sceneConfig.asset_manifest?.rewards?.slice(0, REWARD_ASSET_KEYS.length).forEach((source, index) => {
      if (source) this.load.image(REWARD_ASSET_KEYS[index], source);
    });
  }

  create() {
    if (this.textures.exists(BACKGROUND_ASSET_KEY)) {
      this.backgroundImage = this.add.image(WIDTH / 2, HEIGHT / 2, BACKGROUND_ASSET_KEY).setDisplaySize(WIDTH, HEIGHT).setDepth(-10);
    }
    this.graphics = this.add.graphics();
    this.gateProgress = this.add.graphics().setDepth(3);
    this.statusText = this.add.text(34, 32, "听目标音", {
      fontFamily: "Arial, sans-serif",
      fontSize: "20px",
      color: "#fff7d0",
      fontStyle: "bold"
    });
    this.scoreText = this.add.text(WIDTH - 34, 32, "0", {
      fontFamily: "Arial, sans-serif",
      fontSize: "20px",
      color: "#ffffff",
      fontStyle: "bold",
      align: "right"
    }).setOrigin(1, 0);
    this.heroPresenter = new TemplateCharacterPresenter(this, {
      poseKeys: HERO_ASSET_KEYS,
      x: 132,
      y: 394,
      displaySize: 150,
      depth: 4,
      reducedMotion: prefersReducedMotion()
    });
    this.rewardImages = REWARD_ASSET_KEYS
      .filter((key, index) => [0, 1, 2, 5].includes(index) && this.textures.exists(key))
      .map((key, index) => this.add.image(778 + (index % 2) * 42, 444 + Math.floor(index / 2) * 34, key).setDepth(4).setDisplaySize(34, 34).setAlpha(0).setVisible(false));
    this.createLauncher();
    this.createStarGate();
    this.createTargetViews();
    this.drawScene();
    this.input.on("pointerdown", (pointer: Phaser.Input.Pointer) => this.handleStagePointer(pointer.x, pointer.y));
    this.emit("reset", undefined, "听目标音");
  }

  listenTarget() {
    if (this.status === "success" || this.status === "failed") return;
    if (this.status === "sing_back") {
      this.message = "复听唱回";
      this.drawScene();
      this.flashAnswerTargets();
      this.emit("listen", undefined, "复听唱回");
      return;
    }
    this.status = "listening";
    this.message = "听目标";
    this.drawScene();
    this.flashAnswerTargets();
    this.emit("listen", undefined, "听目标");
    this.time.delayedCall(620, () => {
      if (this.status === "listening") {
        this.status = "aiming";
        this.message = "点靶";
        this.drawScene();
        this.emit("aim", undefined, "点靶");
      }
    });
  }

  fireAt(note: string) {
    if (this.status === "failed") return;
    if (this.status === "sing_back") {
      this.message = "先唱回";
      this.emit("sing_back_ready", "sing_back_ready", "先唱回");
      return;
    }
    if (this.status === "ready" || this.status === "listening") {
      this.status = "aiming";
      this.message = "点靶";
      this.drawScene();
    }
    const target = this.pointForNote(note);
    const expected = this.answer();
    const step = Math.min(this.selected.length, Math.max(0, expected.length - 1));
    const expectedPoint = this.pointForNote(expected[step] || note);
    this.lastChosenNote = note;
    this.lastExpectedNote = expected[step] || note;
    this.lastShotIndex = step;
    this.lastJudgement = undefined;
    this.mistakeReason = undefined;
    this.animateProjectile(note === expected[step] ? target : expectedPoint, target, note === expected[step]);
    this.selected = [...this.selected, note].slice(0, this.answer().length);
    this.emit("fire", undefined, "发射");
    this.time.delayedCall(260, () => this.resolveShot(note));
  }

  confirmSingBack() {
    if (this.status !== "sing_back" && this.status !== "success") {
      this.message = "先命中";
      this.emit("sing_back_ready", "sing_back_ready", "先命中");
      return;
    }
    this.lastJudgement = "sing_back_confirmed";
    this.singBackConfirmedRound = this.currentRound;
    if (this.currentRound + 1 >= this.sceneConfig.solfege_rounds.length) {
      this.status = "success";
      this.message = "通关";
      this.drawScene();
      this.emit("mission_success", "sing_back_confirmed", "通关");
      return;
    }
    this.currentRound += 1;
    this.selected = [];
    this.clearShotEvidence();
    this.status = "ready";
    this.message = "听目标音";
    this.drawScene();
    this.emit("sing_back_confirmed", "sing_back_confirmed", "下一关");
  }

  resetMission() {
    this.status = "ready";
    this.currentRound = 0;
    this.selected = [];
    this.combo = 0;
    this.maxCombo = 0;
    this.score = 0;
    this.hits = 0;
    this.misses = 0;
    this.cleared = 0;
    this.energy = this.sceneConfig.energy_max;
    this.message = "听目标音";
    this.lastJudgement = undefined;
    this.singBackConfirmedRound = null;
    this.clearShotEvidence();
    this.drawScene();
    this.emit("reset", undefined, "听目标音");
  }

  private resolveShot(note: string) {
    const expected = this.answer();
    const shotResult = resolveSolfegeTargetShot(expected, this.selected, note);
    const expectedNote = shotResult.expectedNote;
    const ok = shotResult.ok;
    this.lastChosenNote = note;
    this.lastExpectedNote = expectedNote;
    this.lastShotIndex = shotResult.shotIndex;
    if (!ok) {
      this.combo = 0;
      this.misses += 1;
      this.score = Math.max(0, this.score + this.sceneConfig.score_model.wrong);
      this.energy = Math.max(0, this.energy - Math.ceil(this.sceneConfig.energy_max / this.sceneConfig.mistake_limit));
      this.selected = [];
      this.status = this.energy <= 0 || this.misses >= this.sceneConfig.mistake_limit ? "failed" : "aiming";
      this.message = this.status === "failed" ? "复盘" : "错靶";
      this.lastJudgement = "miss";
      this.mistakeReason = shotResult.mistakeReason;
      this.playMissFx();
      this.cameras.main.shake(160, 0.01);
      this.drawScene();
      this.emit(this.status === "failed" ? "mission_failed" : "miss", "miss", this.message);
      return;
    }
    this.combo += 1;
    this.maxCombo = Math.max(this.maxCombo, this.combo);
    this.hits += 1;
    this.score += this.sceneConfig.score_model.good + (this.sceneConfig.combo_milestones.includes(this.combo) ? this.sceneConfig.score_model.perfect : 0);
    this.message = this.selected.length < expected.length ? "继续" : "唱回";
    this.lastJudgement = this.sceneConfig.combo_milestones.includes(this.combo) ? "combo" : "hit";
    this.mistakeReason = undefined;
    this.playHitFx(note);
    if (shotResult.completed) {
      this.status = "sing_back";
      this.cleared = Math.max(this.cleared, this.currentRound + 1);
      this.score += this.sceneConfig.score_model.perfect;
      this.drawScene();
      this.emit("sing_back_ready", "sing_back_ready", "唱回");
      return;
    }
    this.status = "aiming";
    this.drawScene();
    this.emit(this.lastJudgement === "combo" ? "combo" : "hit", this.lastJudgement, this.message);
  }

  private drawScene() {
    const palette = palettes[this.sceneConfig.skin_play_mode];
    this.graphics.clear();
    this.gateProgress.clear();
    if (!this.backgroundImage) this.graphics.fillStyle(palette.bg, 1).fillRect(0, 0, WIDTH, HEIGHT);
    this.graphics.fillStyle(palette.deep, this.backgroundImage ? 0.22 : 0.55).fillRoundedRect(20, 18, WIDTH - 40, HEIGHT - 36, 32);
    this.drawBackdrop(palette);
    this.drawClearedPath(palette);
    this.drawReticle(palette);
    this.updateTargetViews();
    this.updateTemplateSprites();
    this.updateStarGate();
    this.statusText.setText(`${this.message}  连击 ${this.combo}  能量 ${Math.round((this.energy / this.sceneConfig.energy_max) * 100)}%`);
    this.scoreText.setText(`得分 ${this.score}`);
  }

  private updateTemplateSprites() {
    const pose = this.status === "success" ? "win" : this.status === "failed" ? "miss" : this.status === "aiming" || this.status === "sing_back" ? "action" : "idle";
    this.heroPresenter?.transitionTo(pose, this.status === "success" ? "success" : this.status === "failed" ? "miss" : this.status === "listening" ? "listen" : this.status === "aiming" || this.status === "sing_back" ? "hit" : "idle");
    this.launcherImage?.setAngle(this.status === "aiming" || this.status === "listening" ? -10 : -4);
    this.rewardImages.forEach((image, index) => {
      const visible = index < Math.max(this.cleared, this.status === "sing_back" ? this.cleared + 1 : 0) || this.status === "success";
      image.setVisible(visible);
      image.setAlpha(visible ? (this.status === "success" ? 0.95 : 0.72) : 0);
      image.setScale(this.status === "success" ? 1.12 : 1);
    });
  }

  update() {
    if (!this.targetViews.length) return;
    this.updateTargetPositions();
    this.drawDynamicLinks();
  }

  private drawBackdrop(palette: (typeof palettes)[SolfegeTargetPlayMode]) {
    if (this.sceneConfig.skin_play_mode === "flower") {
      this.graphics.fillStyle(0xffffff, 0.2).fillCircle(160, 130, 90);
      this.graphics.fillStyle(0xffb7d8, 0.26).fillCircle(760, 150, 110);
      return;
    }
    if (this.sceneConfig.skin_play_mode === "lantern") {
      for (let index = 0; index < 5; index += 1) {
        this.graphics.fillStyle(0xff9d50, 0.2).fillCircle(150 + index * 160, 95, 44);
      }
      return;
    }
    if (this.sceneConfig.skin_play_mode === "archery") {
      this.graphics.fillStyle(0x21384a, 0.58).fillRoundedRect(70, 420, 820, 58, 20);
      return;
    }
    if (this.sceneConfig.skin_play_mode === "bubble") {
      for (let index = 0; index < 10; index += 1) {
        this.graphics.fillStyle(0xffffff, 0.22).fillCircle(80 + index * 95, 90 + (index % 4) * 70, 26);
      }
      return;
    }
    this.graphics.lineStyle(2, palette.soft, 0.28);
    for (let index = 0; index < 8; index += 1) {
      this.graphics.strokeCircle(WIDTH / 2, HEIGHT / 2, 80 + index * 42);
    }
  }

  private drawReticle(palette: (typeof palettes)[SolfegeTargetPlayMode]) {
    this.graphics.lineStyle(3, palette.accent, 0.72);
    this.graphics.strokeCircle(WIDTH / 2, HEIGHT / 2, 72);
    this.graphics.lineBetween(WIDTH / 2 - 96, HEIGHT / 2, WIDTH / 2 - 42, HEIGHT / 2);
    this.graphics.lineBetween(WIDTH / 2 + 42, HEIGHT / 2, WIDTH / 2 + 96, HEIGHT / 2);
    this.graphics.lineBetween(WIDTH / 2, HEIGHT / 2 - 96, WIDTH / 2, HEIGHT / 2 - 42);
    this.graphics.lineBetween(WIDTH / 2, HEIGHT / 2 + 42, WIDTH / 2, HEIGHT / 2 + 96);
  }

  private createLauncher() {
    const launcherKey = PROP_ASSET_KEYS[4];
    if (this.textures.exists(launcherKey)) {
      this.launcherImage = this.add.image(LAUNCHER_POINT.x - 34, LAUNCHER_POINT.y - 12, launcherKey).setDepth(5).setDisplaySize(86, 86).setAngle(-4);
    }
    this.add.circle(LAUNCHER_POINT.x, LAUNCHER_POINT.y, 18, palettes[this.sceneConfig.skin_play_mode].accent, 0.22).setDepth(3)
      .setStrokeStyle(3, 0xffffff, 0.34);
  }

  private createStarGate() {
    const palette = palettes[this.sceneConfig.skin_play_mode];
    const gate = this.add.container(832, 410).setDepth(3);
    const gateKey = PROP_ASSET_KEYS[8];
    if (this.textures.exists(gateKey)) {
      gate.add(this.add.image(0, 0, gateKey).setDisplaySize(112, 86).setAlpha(0.88));
    } else {
      gate.add(this.add.circle(0, 0, 48, palette.soft, 0.28).setStrokeStyle(4, palette.accent, 0.7));
    }
    gate.add(this.add.text(0, 52, "唱回星门", {
      fontFamily: "Noto Sans SC, PingFang SC, sans-serif",
      fontSize: "16px",
      color: "#fff8dd",
      fontStyle: "bold"
    }).setOrigin(0.5));
    this.starGate = gate;
  }

  private createTargetViews() {
    const palette = palettes[this.sceneConfig.skin_play_mode];
    this.targetViews.forEach((view) => view.container.destroy(true));
    const layout = this.composedTargetLayout();
    this.targetViews = layout.map((item, index) => {
      const point = this.layoutPoint(item);
      const container = this.add.container(point.x, point.y).setDepth(4);
      const shadow = this.add.ellipse(0, 54, 96, 22, 0x000000, 0.24);
      const glow = this.add.circle(0, 0, 58, palette.accent, 0.12).setStrokeStyle(4, palette.accent, 0.32);
      const baseDisk = this.add.circle(0, 0, 48, palette.target, 0.96).setStrokeStyle(6, 0xfff7d0, 0.92);
      const outerRing = this.add.circle(0, 0, 36, palette.soft, 0.28).setStrokeStyle(4, palette.soft, 0.78);
      const midRing = this.add.circle(0, 0, 25, 0xffffff, 0.18).setStrokeStyle(3, 0xffffff, 0.72);
      const innerRing = this.add.circle(0, 0, 13, palette.accent, 0.92).setStrokeStyle(3, 0x6a3f1d, 0.28);
      const crosshairH = this.add.rectangle(0, 0, 82, 4, 0xffffff, 0.24);
      const crosshairV = this.add.rectangle(0, 0, 4, 82, 0xffffff, 0.24);
      const label = this.add.text(0, 0, item.label, {
        fontFamily: "Arial, Noto Sans SC, sans-serif",
        fontSize: "26px",
        color: "#2d1a19",
        fontStyle: "bold",
        align: "center",
        stroke: "#fff7d0",
        strokeThickness: 4
      }).setOrigin(0.5);
      const clearedBadge = this.add.text(36, -38, "✓", {
        fontFamily: "Arial, sans-serif",
        fontSize: "23px",
        color: "#173024",
        fontStyle: "bold",
        backgroundColor: "#ffe070",
        padding: { x: 6, y: 2 }
      }).setOrigin(0.5).setVisible(false);
      container.add([shadow, glow, baseDisk, crosshairH, crosshairV, outerRing, midRing, innerRing, label, clearedBadge]);
      container.setSize(120, 120);
      return {
        item,
        container,
        baseX: point.x,
        baseY: point.y,
        floatSeed: index * 0.9,
        shadow,
        glow,
        baseDisk,
        outerRing,
        midRing,
        innerRing,
        crosshairH,
        crosshairV,
        label,
        clearedBadge
      };
    });
  }

  private updateTargetPositions() {
    const palette = palettes[this.sceneConfig.skin_play_mode];
    const motion = this.sceneConfig.target_motion_profile;
    const time = this.time.now / 1000;
    this.targetViews.forEach((view, index) => {
      const selected = this.selected.includes(view.item.note);
      const answer = this.answer().includes(view.item.note);
      const drift = Math.sin(time * motion.float_speed + view.floatSeed) * Math.min(10, motion.float_amplitude);
      const jitter = Math.cos(time * (motion.float_speed + 0.35) + index) * Math.min(3, motion.orbit_jitter * 180);
      view.container.setPosition(
        clampFloat(view.baseX + jitter, TARGET_ARENA.minX, TARGET_ARENA.maxX, view.baseX),
        clampFloat(view.baseY + drift, TARGET_ARENA.minY, TARGET_ARENA.maxY, view.baseY)
      );
      view.shadow.setScale(1 + Math.abs(drift) / 80, 1);
      view.glow.setAlpha(answer || selected ? 0.34 : 0.12);
      view.glow.setScale(answer || selected ? 1.16 : 1);
      view.outerRing.setStrokeStyle(answer || selected ? 5 : 4, answer ? palette.accent : palette.soft, answer || selected ? 0.95 : 0.78);
      view.innerRing.setFillStyle(selected ? 0x7ee081 : palette.accent, selected ? 0.96 : 0.92);
      view.baseDisk.setFillStyle(selected ? 0xf7ffd0 : palette.target, 0.96);
      view.label.setAlpha(selected ? 0.58 : 1);
      view.clearedBadge.setVisible(selected || (this.status === "sing_back" && answer));
    });
  }

  private updateTargetViews() {
    this.updateTargetPositions();
  }

  private drawClearedPath(palette: (typeof palettes)[SolfegeTargetPlayMode]) {
    const selectedPoints = this.selected.map((note) => this.pointForNote(note));
    if (selectedPoints.length < 1) return;
    this.graphics.lineStyle(6, palette.accent, 0.55);
    let previous = LAUNCHER_POINT;
    selectedPoints.forEach((point) => {
      this.graphics.lineBetween(previous.x, previous.y, point.x, point.y);
      previous = point;
    });
  }

  private drawDynamicLinks() {
    if (!this.gateProgress) return;
    const palette = palettes[this.sceneConfig.skin_play_mode];
    this.gateProgress.clear();
    const progress = this.cleared / Math.max(1, this.sceneConfig.solfege_rounds.length);
    this.gateProgress.lineStyle(7, palette.accent, 0.74);
    this.gateProgress.beginPath();
    this.gateProgress.arc(832, 410, 62, Phaser.Math.DegToRad(-90), Phaser.Math.DegToRad(-90 + progress * 360), false);
    this.gateProgress.strokePath();
    const selectedPoints = this.selected.map((note) => this.pointForNote(note));
    if (selectedPoints.length) {
      this.gateProgress.lineStyle(4, 0xffffff, 0.42);
      let previous = LAUNCHER_POINT;
      selectedPoints.forEach((point) => {
        this.gateProgress.lineBetween(previous.x, previous.y, point.x, point.y);
        previous = point;
      });
    }
  }

  private updateStarGate() {
    if (!this.starGate) return;
    const scale = this.status === "success" ? 1.16 : this.status === "sing_back" ? 1.08 : 1;
    this.starGate.setScale(scale);
    this.starGate.setAlpha(this.status === "failed" ? 0.68 : 1);
  }

  private animateProjectile(flyTo: { x: number; y: number }, impactAt: { x: number; y: number }, accurate: boolean) {
    const palette = palettes[this.sceneConfig.skin_play_mode];
    const projectileKey = PROP_ASSET_KEYS[6];
    const trailKey = PROP_ASSET_KEYS[7];
    const shot = this.textures.exists(projectileKey)
      ? this.add.image(LAUNCHER_POINT.x, LAUNCHER_POINT.y, projectileKey).setDepth(8).setDisplaySize(42, 42)
      : this.add.circle(LAUNCHER_POINT.x, LAUNCHER_POINT.y, 9, palette.accent, 1).setDepth(8);
    const trail = this.textures.exists(trailKey)
      ? this.add.image(LAUNCHER_POINT.x, LAUNCHER_POINT.y, trailKey).setDepth(7).setDisplaySize(68, 42).setAlpha(0.7)
      : this.add.circle(LAUNCHER_POINT.x, LAUNCHER_POINT.y, 18, palette.accent, 0.26).setDepth(7);
    this.tweens.add({
      targets: [shot, trail],
      x: accurate ? flyTo.x : impactAt.x,
      y: accurate ? flyTo.y : impactAt.y,
      angle: accurate ? 22 : -36,
      duration: 260,
      ease: accurate ? "Cubic.easeOut" : "Sine.easeInOut",
      onComplete: () => {
        shot.destroy();
        trail.destroy();
      }
    });
    this.heroPresenter?.pulse("hit");
  }

  private burstAt(note: string) {
    const point = this.currentPointForNote(note);
    const palette = palettes[this.sceneConfig.skin_play_mode];
    const rewardKey = REWARD_ASSET_KEYS[6];
    const burst = this.textures.exists(rewardKey)
      ? this.add.image(point.x, point.y, rewardKey).setDepth(9).setDisplaySize(92, 92).setAlpha(0.86)
      : this.add.circle(point.x, point.y, 18, palette.accent, 0.5).setDepth(9);
    this.tweens.add({ targets: burst, scale: 1.8, alpha: 0, duration: 440, ease: "Cubic.Out", onComplete: () => burst.destroy() });
  }

  private playHitFx(note: string) {
    this.burstAt(note);
    const point = this.currentPointForNote(note);
    const view = this.targetViews.find((item) => item.item.note === note);
    if (view) {
      this.tweens.add({ targets: view.container, scaleX: 1.16, scaleY: 1.16, duration: 90, yoyo: true, ease: "Back.Out" });
    }
    const text = this.lastJudgement === "combo" ? `连击 ${this.combo}` : "命中";
    const label = this.add.text(point.x, point.y - 76, text, {
      color: "#fff2bd",
      fontFamily: "Noto Sans SC, PingFang SC, sans-serif",
      fontSize: "28px",
      fontStyle: "bold",
      stroke: "#10213a",
      strokeThickness: 5
    }).setOrigin(0.5);
    this.tweens.add({ targets: label, y: point.y - 104, alpha: 0, duration: 460, ease: "Cubic.Out", onComplete: () => label.destroy() });
    this.cameras.main.flash(90, 255, 232, 166, false);
  }

  private playMissFx() {
    const point = { x: WIDTH / 2, y: HEIGHT / 2 };
    const missKey = REWARD_ASSET_KEYS[7];
    const ring = this.textures.exists(missKey)
      ? this.add.image(point.x, point.y, missKey).setDepth(9).setDisplaySize(120, 120).setAlpha(0.78)
      : this.add.circle(point.x, point.y, 58, palettes[this.sceneConfig.skin_play_mode].danger, 0.18)
        .setStrokeStyle(5, palettes[this.sceneConfig.skin_play_mode].danger, 0.7).setDepth(9);
    const label = this.add.text(point.x, point.y - 84, "错靶", {
      color: "#ffd6c4",
      fontFamily: "Noto Sans SC, PingFang SC, sans-serif",
      fontSize: "28px",
      fontStyle: "bold"
    }).setOrigin(0.5);
    this.tweens.add({ targets: ring, scale: 1.5, alpha: 0, duration: 420, ease: "Cubic.Out", onComplete: () => ring.destroy() });
    this.tweens.add({ targets: label, y: point.y - 118, alpha: 0, duration: 460, ease: "Cubic.Out", onComplete: () => label.destroy() });
    this.heroPresenter?.pulse("miss");
  }

  private flashAnswerTargets() {
    this.answer().forEach((note, index) => {
      this.time.delayedCall(index * 220, () => this.burstAt(note));
    });
  }

  private pointForNote(note: string) {
    const target = this.targetViews.find((item) => item.item.note === note)?.item
      || this.composedTargetLayout().find((item) => item.note === note)
      || this.composedTargetLayout()[0];
    return this.layoutPoint(target);
  }

  private currentPointForNote(note: string) {
    const view = this.targetViews.find((item) => item.item.note === note);
    return view ? { x: view.container.x, y: view.container.y } : this.pointForNote(note);
  }

  private composedTargetLayout() {
    return normalizeLayout(undefined, this.sceneConfig.target_solfege, this.sceneConfig.skin_play_mode);
  }

  private layoutPoint(item: TargetLayoutItem) {
    return {
      x: clampFloat(item.x * WIDTH, TARGET_ARENA.minX, TARGET_ARENA.maxX, WIDTH / 2),
      y: clampFloat(item.y * HEIGHT, TARGET_ARENA.minY, TARGET_ARENA.maxY, HEIGHT / 2)
    };
  }

  private handleStagePointer(x: number, y: number) {
    const nearest = this.targetViews
      .map((view) => ({ target: view.item, point: { x: view.container.x, y: view.container.y } }))
      .sort((a, b) => Phaser.Math.Distance.Between(x, y, a.point.x, a.point.y) - Phaser.Math.Distance.Between(x, y, b.point.x, b.point.y))[0];
      if (nearest && Phaser.Math.Distance.Between(x, y, nearest.point.x, nearest.point.y) <= 74) this.fireAt(nearest.target.note);
  }

  private currentRoundData() {
    return this.sceneConfig.solfege_rounds[this.currentRound % this.sceneConfig.solfege_rounds.length];
  }

  private answer() {
    const answer = this.currentRoundData().answer;
    return (Array.isArray(answer) ? answer : [answer]).map(String).filter(Boolean);
  }

  private sequence() {
    return (this.currentRoundData().sequence || this.answer()).map(String);
  }

  private objective() {
    return {
      star: "音名星靶场",
      flower: "花朵绽放",
      lantern: "灯笼靶会",
      archery: "音乐弓箭场",
      bubble: "泡泡音名"
    }[this.sceneConfig.skin_play_mode];
  }

  private clearShotEvidence() {
    this.lastChosenNote = undefined;
    this.lastExpectedNote = undefined;
    this.lastShotIndex = undefined;
    this.mistakeReason = undefined;
  }

  private snapshot(): SolfegeTargetSnapshot {
    const round = this.currentRoundData();
    const answer = this.answer();
    const nextExpectedNote = answer[Math.min(this.selected.length, Math.max(0, answer.length - 1))];
    return {
      status: this.status,
      currentRound: this.currentRound,
      totalRounds: this.sceneConfig.solfege_rounds.length,
      currentMode: this.sceneConfig.current_mode,
      sequence: this.sequence(),
      labels: (round.labels || this.sequence()).map(String),
      answer,
      selected: [...this.selected],
      expectedNote: this.lastExpectedNote || nextExpectedNote,
      lastChosenNote: this.lastChosenNote,
      lastShotIndex: this.lastShotIndex,
      nextExpectedNote,
      mistakeReason: this.mistakeReason,
      combo: this.combo,
      maxCombo: this.maxCombo,
      score: this.score,
      hits: this.hits,
      misses: this.misses,
      cleared: this.cleared,
      energy: this.energy,
      energyMax: this.sceneConfig.energy_max,
      mistakeLimit: this.sceneConfig.mistake_limit,
      progress: this.cleared / Math.max(1, this.sceneConfig.solfege_rounds.length),
      skinObjective: this.objective(),
      audioMode: this.sceneConfig.audio_mode,
      audioLabel: this.sceneConfig.audio_mode === "lesson_audio" ? "作品片段" : "内置音高",
      singBackRequired: this.sceneConfig.sing_back_required,
      teacherConfirmRequired: this.sceneConfig.teacher_confirm_required,
      singBackConfirmed: this.singBackConfirmedRound === this.currentRound || this.status === "success",
      micAssistEnabled: this.sceneConfig.mic_assist_enabled,
      lastJudgement: this.lastJudgement,
      message: this.message
    };
  }

  private emit(type: SolfegeTargetSceneEvent["type"], judgement?: SolfegeTargetJudgement, message?: string) {
    if (judgement) this.lastJudgement = judgement;
    if (message) this.message = message;
    this.onSceneEvent({ type, judgement, message, snapshot: this.snapshot() });
  }
}

function normalizeRequiredConfig(config: SolfegeTargetSceneConfig): NormalizedSolfegeTargetSceneConfig {
  const built = buildSolfegeTargetSceneConfig(config as Record<string, unknown>);
  return {
    engine: "phaser_2d",
    scene_id: "solfege_target_scene",
    runtime_shell: "solfege_target_shell",
    game_feel: "solfege_target_range",
    skin_id: built.skin_id || "star_target",
    skin_play_mode: built.skin_play_mode || "star",
    mode: built.mode || "listen_and_hit",
    current_mode: built.current_mode || "single_target",
    target_solfege: built.target_solfege || ["do", "mi", "sol"],
    solfege_rounds: built.solfege_rounds || [],
    target_rounds: built.target_rounds || [],
    target_layout: built.target_layout || [],
    energy_max: built.energy_max || 100,
    mistake_limit: built.mistake_limit || 3,
    combo_milestones: built.combo_milestones || [2, 4, 6],
    sing_back_required: built.sing_back_required !== false,
    teacher_confirm_required: built.teacher_confirm_required !== false,
    mic_assist_enabled: built.mic_assist_enabled !== false,
    audio_mode: built.audio_mode || "hybrid",
    input_map: normalizeInputMap(built.input_map),
    fx_profile: normalizeFxProfile(built.fx_profile),
    score_model: normalizeScoreModel(built.score_model),
    arcade_play_model: "bubble_target_chain",
    target_motion_profile: normalizeTargetMotionProfile(built.target_motion_profile),
    asset_role_map: normalizeAssetRoleMap(built.asset_role_map),
    target_hud: true,
    show_teacher_text_in_play: false,
    asset_manifest: built.asset_manifest || {}
  };
}

function normalizeNotes(value: unknown) {
  const fallback = ["do", "mi", "sol"];
  if (!Array.isArray(value)) return fallback;
  const notes = value.map(String).filter(Boolean);
  return notes.length >= 2 ? notes : fallback;
}

function normalizeRounds(value: unknown, notes: string[]): SolfegeRound[] {
  if (Array.isArray(value) && value.length) {
    return value.map((item, index) => {
      const record = isRecord(item) ? item : {};
      const sequence = Array.isArray(record.sequence) ? record.sequence.map(String) : [notes[index % notes.length]];
      return {
        id: String(record.id || `s${index + 1}`),
        sequence,
        labels: Array.isArray(record.labels) ? record.labels.map(String) : sequence.map(noteLabel),
        midi_offsets: Array.isArray(record.midi_offsets) ? record.midi_offsets.map(Number) : sequence.map(pitchMidiOffset),
        answer: Array.isArray(record.answer) ? record.answer.map(String) : String(record.answer || sequence[0]),
        sing_back_required: record.sing_back_required !== false,
        teacher_confirm_required: record.teacher_confirm_required !== false
      };
    });
  }
  return [{ id: "s1", sequence: [notes[0]], labels: [noteLabel(notes[0])], midi_offsets: [0], answer: notes[0], sing_back_required: true, teacher_confirm_required: true }];
}

function normalizeLayout(value: unknown, notes: string[], playMode: SolfegeTargetPlayMode): TargetLayoutItem[] {
  const safePoints = targetArenaLayout(notes.length, playMode);
  if (Array.isArray(value) && value.length) {
    return value.map((item, index) => {
      const record = isRecord(item) ? item : {};
      const note = String(record.note || record.id || notes[index % notes.length]);
      const point = safePoints[index % safePoints.length] || { x: 0.5, y: 0.5 };
      return {
        id: String(record.id || note),
        note,
        label: String(record.label || noteLabel(note)),
        midi_offset: Number(record.midi_offset || pitchMidiOffset(note)),
        x: point.x,
        y: point.y
      };
    });
  }
  return notes.map((note, index) => {
    const point = safePoints[index % safePoints.length] || { x: 0.5, y: 0.5 };
    return {
      id: note,
      note,
      label: noteLabel(note),
      midi_offset: pitchMidiOffset(note),
      x: point.x,
      y: point.y
    };
  });
}

function targetArenaLayout(count: number, playMode: SolfegeTargetPlayMode) {
  if (playMode === "archery") {
    return Array.from({ length: Math.max(1, count) }, (_, index) => ({
      x: 0.34 + (index / Math.max(1, count - 1)) * 0.34,
      y: 0.34 + (index % 2) * 0.22
    }));
  }
  if (playMode === "bubble") {
    return Array.from({ length: Math.max(1, count) }, (_, index) => ({
      x: 0.32 + (index / Math.max(1, count - 1)) * 0.36,
      y: 0.32 + ((index * 29) % 28) / 100
    }));
  }
  const presets: Record<number, { x: number; y: number }[]> = {
    1: [{ x: 0.5, y: 0.44 }],
    2: [{ x: 0.42, y: 0.42 }, { x: 0.58, y: 0.42 }],
    3: [{ x: 0.5, y: 0.32 }, { x: 0.39, y: 0.54 }, { x: 0.61, y: 0.54 }],
    4: [{ x: 0.39, y: 0.34 }, { x: 0.61, y: 0.34 }, { x: 0.41, y: 0.57 }, { x: 0.59, y: 0.57 }],
    5: [{ x: 0.5, y: 0.29 }, { x: 0.36, y: 0.43 }, { x: 0.64, y: 0.43 }, { x: 0.42, y: 0.62 }, { x: 0.58, y: 0.62 }]
  };
  if (count <= 5) return presets[Math.max(1, count)];
  return Array.from({ length: count }, (_, index) => ({
    x: 0.34 + (index % 3) * 0.16,
    y: 0.3 + Math.floor(index / 3) * 0.17
  }));
}

function normalizeMode(value: unknown, mode: unknown): SolfegeTargetMode {
  const candidate = String(value || mode || "");
  if (candidate === "aim_and_sing") return "aim_and_sing";
  if (candidate === "target_chain") return "target_chain";
  return "single_target";
}

function normalizePlayMode(value: unknown, skinId: string): SolfegeTargetPlayMode {
  const candidate = String(value || "");
  if (candidate === "star" || candidate === "flower" || candidate === "lantern" || candidate === "archery" || candidate === "bubble") return candidate;
  if (skinId === "flower_bloom") return "flower";
  if (skinId === "lantern_target") return "lantern";
  if (skinId === "archery_field") return "archery";
  if (skinId === "bubble_pop") return "bubble";
  return "star";
}

function normalizeAudioMode(value: unknown): SolfegeTargetAudioMode {
  const candidate = String(value || "hybrid");
  if (candidate === "internal_pitch" || candidate === "lesson_audio" || candidate === "hybrid") return candidate;
  return "hybrid";
}

function normalizeComboMilestones(value: unknown) {
  if (!Array.isArray(value)) return [2, 4, 6];
  const combos = value.map(Number).filter((item) => Number.isFinite(item) && item > 0);
  return combos.length ? combos : [2, 4, 6];
}

function normalizeInputMap(value: unknown) {
  const record = isRecord(value) ? value : {};
  return { primary: String(record.primary || "Space"), pointer: record.pointer !== false };
}

function normalizeFxProfile(value: unknown): FxProfile {
  const record = isRecord(value) ? value : {};
  return {
    hit: String(record.hit || "target_burst"),
    miss: String(record.miss || "reticle_shake"),
    success: String(record.success || "skin_target_finish")
  };
}

function normalizeScoreModel(value: unknown): ScoreModel {
  const record = isRecord(value) ? value : {};
  return {
    perfect: clampNumber(Number(record.perfect), 20, 500, 140),
    good: clampNumber(Number(record.good), 10, 300, 90),
    wrong: -Math.abs(clampNumber(Number(record.wrong), -200, 200, -45)),
    missed: -Math.abs(clampNumber(Number(record.missed), -240, 240, -65))
  };
}

function normalizeTargetMotionProfile(value: unknown): TargetMotionProfile {
  const record = isRecord(value) ? value : {};
  return {
    float_amplitude: clampFloat(Number(record.float_amplitude), 0, 10, 8),
    float_speed: clampFloat(Number(record.float_speed), 0.2, 2.4, 0.85),
    orbit_jitter: clampFloat(Number(record.orbit_jitter), 0, 0.017, 0.012)
  };
}

function normalizeAssetRoleMap(value: unknown): AssetRoleMap {
  const record = isRecord(value) ? value : {};
  return {
    launcher: String(record.launcher || "prop-05-cannon-launcher"),
    projectile: String(record.projectile || "prop-07-note-projectile"),
    trail: String(record.trail || "prop-08-orbit-trail"),
    target_primary: String(record.target_primary || "phaser-drawn-solfege-target"),
    target_secondary: String(record.target_secondary || "phaser-drawn-solfege-target"),
    gate: String(record.gate || "prop-09-singback-gate"),
    combo: String(record.combo || "ui-07-hit-comet"),
    miss: String(record.miss || "ui-08-miss-crescent"),
    medal: String(record.medal || "ui-06-constellation-medal")
  };
}

function pitchMidiOffset(note: string) {
  return resolvePitchToken(note)?.semitone ?? 0;
}

function noteLabel(note: string) {
  return {
    do: "C",
    re: "D",
    mi: "E",
    fa: "F",
    sol: "G",
    la: "A",
    ti: "B",
    do_high: "C'"
  }[note] || note;
}

function clampNumber(value: number, min: number, max: number, fallback: number) {
  if (!Number.isFinite(value)) return fallback;
  return Math.max(min, Math.min(max, Math.round(value)));
}

function clampFloat(value: number, min: number, max: number, fallback: number) {
  if (!Number.isFinite(value)) return fallback;
  return Math.max(min, Math.min(max, value));
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value && typeof value === "object" && !Array.isArray(value));
}

function prefersReducedMotion() {
  return typeof window !== "undefined" && window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
}
