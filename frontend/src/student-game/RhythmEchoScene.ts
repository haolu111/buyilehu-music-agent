import Phaser from "phaser";
import { getAudioContext, playHybridToneSequence, prepareSampledInstrument, type AudioPlaySource } from "../shared/realAudio";
import {
  resolveRhythmRoundPlan,
  type RhythmRoundPatches,
  type RhythmTimelineItem
} from "./rhythmEchoRoundPlan";
import { TemplateCharacterPresenter } from "./templateCharacterPresenter";
import { templateVisualPackForConfig } from "./templateVisualAssets";
import type { TemplatePoseKey, TemplateVisualPack } from "./types";

export type RhythmEchoPlayMode = "radio" | "cave" | "signal" | "rain" | "kitchen";
export type RhythmEchoStatus = "ready" | "demo" | "blind_demo" | "count_in" | "recording" | "success" | "failed";
export type RhythmEchoJudgement = "perfect" | "good" | "early" | "late" | "short" | "long" | "extra" | "missed" | "too_early";
export type RhythmEchoAudioMode = "internal_pattern" | "lesson_audio" | "hybrid";

type JudgementWindows = {
  perfect_ms: number;
  good_ms: number;
  late_ms: number;
};

type ScoreModel = {
  perfect: number;
  good: number;
  wrong: number;
  missed: number;
};

type LessonAudioSync = {
  audio_url?: string;
  bpm?: number;
  meter?: string;
  offset_ms?: number;
  segment_label?: string;
};

type RhythmPulse = {
  start_ms: number;
  duration_ms: number;
};

type EchoStageNode = {
  x: number;
  y: number;
  width: number;
  duration: number;
  item: RhythmTimelineItem;
  hitIndex: number;
};

export type RhythmEchoSceneConfig = {
  engine?: "phaser_2d";
  scene_id?: "rhythm_echo_scene";
  scene_phase?: "ready";
  game_feel?: "arcade_rhythm_echo";
  runtime_shell?: "rhythm_echo_shell" | "rhythm_echo_arcade";
  skin_id?: string;
  skin_play_mode?: RhythmEchoPlayMode;
  meter?: string;
  bpm?: number;
  active_round?: number;
  round_count?: number;
  pattern_steps?: string[];
  pattern_timeline?: RhythmTimelineItem[];
  round_patches?: RhythmRoundPatches;
  round_length_steps?: number;
  required_accuracy?: number;
  energy_max?: number;
  energy_loss_per_miss?: number;
  combo_milestones?: number[];
  judgement_windows?: Partial<JudgementWindows>;
  input_map?: { primary?: string; pointer?: boolean };
  fx_profile?: { hit?: string; miss?: string; success?: string };
  arcade_hud?: boolean;
  show_teacher_text_in_play?: boolean;
  score_model?: Partial<ScoreModel>;
  count_in_beats?: number;
  audio_mode?: RhythmEchoAudioMode;
  lesson_audio_sync?: LessonAudioSync;
  minimal_hud?: boolean;
  asset_manifest?: TemplateVisualPack;
};

type NormalizedRhythmEchoSceneConfig = Omit<
  Required<RhythmEchoSceneConfig>,
  "combo_milestones" | "fx_profile" | "input_map" | "judgement_windows" | "lesson_audio_sync" | "pattern_steps" | "pattern_timeline" | "score_model"
> & {
  combo_milestones: number[];
  fx_profile: { hit: string; miss: string; success: string };
  input_map: { primary: string; pointer: boolean };
  judgement_windows: JudgementWindows;
  lesson_audio_sync: LessonAudioSync;
  pattern_steps: string[];
  pattern_timeline: RhythmTimelineItem[];
  round_patches: RhythmRoundPatches;
  score_model: ScoreModel;
};

export type RhythmEchoSnapshot = {
  status: RhythmEchoStatus;
  currentIndex: number;
  totalHits: number;
  hits: number;
  misses: number;
  extras: number;
  combo: number;
  maxCombo: number;
  score: number;
  energy: number;
  energyMax: number;
  accuracy: number;
  progress: number;
  audioMode: RhythmEchoAudioMode;
  audioLabel: string;
  audioReady: boolean;
  audioPreparing: boolean;
  audioError?: string;
  audioSource?: Extract<AudioPlaySource, "soundfont" | "lesson_audio" | "oscillator" | "failed">;
  currentRound: number;
  totalRounds: number;
  cleared: number;
  patternLabel: string;
  durationLabel: string;
  lastJudgement?: RhythmEchoJudgement;
  message: string;
};

export type RhythmEchoSceneEvent = {
  type: "audio" | "demo" | "start" | "reset" | "tap" | "press_start" | "press_end" | "judgement" | "mission_success" | "mission_failed";
  judgement?: RhythmEchoJudgement;
  message?: string;
  snapshot: RhythmEchoSnapshot;
};

export type RhythmEchoController = {
  prepareAudio: () => Promise<void>;
  demo: () => void;
  start: () => void;
  tap: () => void;
  pressStart: () => void;
  pressEnd: () => void;
  reset: () => void;
  destroy: () => void;
};

const WIDTH = 960;
const HEIGHT = 520;
const BACKGROUND_ASSET_KEY = "rhythm_echo_template_bg";
const HERO_ASSET_KEYS: Record<TemplatePoseKey, string> = {
  idle: "rhythm_echo_pose_idle",
  action: "rhythm_echo_pose_action",
  miss: "rhythm_echo_pose_miss",
  win: "rhythm_echo_pose_win"
};
const PROP_ASSET_KEYS = ["rhythm_echo_prop_1", "rhythm_echo_prop_2", "rhythm_echo_prop_3"];
const REWARD_ASSET_KEY = "rhythm_echo_reward";
const MIN_PRESS_MS = 90;
const TRACK_Y = 336;
const PLAYER_Y = 428;
const NODE_BASE_X = 260;
const NODE_SPAN = 500;

const palettes: Record<RhythmEchoPlayMode, { bg: number; deep: number; accent: number; target: number; soft: number; danger: number }> = {
  radio: { bg: 0x0f1c24, deep: 0x112a33, accent: 0x65f0a9, target: 0xf6ffb8, soft: 0x4d817b, danger: 0xff5d5d },
  cave: { bg: 0x1c3142, deep: 0x17202f, accent: 0x90d7ff, target: 0xf2e1a0, soft: 0x5e7fa4, danger: 0xf06a4d },
  signal: { bg: 0x152c35, deep: 0x0f1c24, accent: 0x65f0a9, target: 0xf6ffb8, soft: 0x4d817b, danger: 0xff5d5d },
  rain: { bg: 0x20384d, deep: 0x142536, accent: 0x83c7ff, target: 0xf9e8a0, soft: 0x638cac, danger: 0xe65b47 },
  kitchen: { bg: 0x3e392b, deep: 0x5d321f, accent: 0xffbd5c, target: 0xffefbd, soft: 0xb98c62, danger: 0xdf553b }
};

export function buildRhythmEchoSceneConfig(raw: Record<string, unknown>): RhythmEchoSceneConfig {
  const nested = isRecord(raw.scene_config) ? raw.scene_config : {};
  const merged = { ...raw, ...nested };
  const skinId = String(merged.skin_id || "rhythm_radio");
  const roundPlan = resolveRhythmRoundPlan(merged);
  const patternSteps = roundPlan.pattern_steps;
  const timeline = roundPlan.pattern_timeline;
  const totalHits = timeline.filter((item) => item.hit_required).length;
  return {
    engine: "phaser_2d",
    scene_id: "rhythm_echo_scene",
    scene_phase: "ready",
    game_feel: "arcade_rhythm_echo",
    runtime_shell: "rhythm_echo_shell",
    skin_id: skinId,
    skin_play_mode: normalizePlayMode(merged.skin_play_mode, skinId),
    meter: String(merged.meter || "2/4"),
    bpm: clampNumber(Number(merged.bpm), 60, 132, 92),
    active_round: roundPlan.active_round,
    round_count: roundPlan.round_count,
    pattern_steps: patternSteps,
    pattern_timeline: timeline,
    round_patches: roundPlan.round_patches,
    round_length_steps: clampNumber(Number(merged.round_length_steps), 1, 16, totalHits || 2),
    required_accuracy: clampFloat(Number(merged.required_accuracy), 0.5, 1, 0.8),
    energy_max: clampNumber(Number(merged.energy_max), 50, 150, 100),
    energy_loss_per_miss: clampNumber(Number(merged.energy_loss_per_miss), 8, 60, 22),
    combo_milestones: normalizeComboMilestones(merged.combo_milestones),
    judgement_windows: normalizeJudgementWindows(merged.judgement_windows, Number(merged.timing_tolerance_ms || 180)),
    input_map: normalizeInputMap(merged.input_map),
    fx_profile: normalizeFxProfile(merged.fx_profile),
    arcade_hud: true,
    show_teacher_text_in_play: false,
    score_model: normalizeScoreModel(merged.score_model),
    count_in_beats: clampNumber(Number(merged.count_in_beats), 0, 8, 4),
    audio_mode: normalizeAudioMode(merged.audio_mode),
    lesson_audio_sync: normalizeLessonAudioSync(merged.lesson_audio_sync),
    minimal_hud: true,
    asset_manifest: templateVisualPackForConfig(merged, "rhythm_echo_core")
  };
}

export function mountRhythmEchoScene(
  parent: HTMLElement,
  config: RhythmEchoSceneConfig,
  onEvent: (event: RhythmEchoSceneEvent) => void
): RhythmEchoController {
  const built = buildRhythmEchoSceneConfig(config as Record<string, unknown>);
  const scene = new RhythmEchoScene(built, onEvent);
  const game = new Phaser.Game({
    type: Phaser.AUTO,
    parent,
    width: WIDTH,
    height: HEIGHT,
    backgroundColor: palettes[built.skin_play_mode || "radio"].bg,
    scale: {
      mode: Phaser.Scale.FIT,
      autoCenter: Phaser.Scale.CENTER_BOTH
    },
    scene: [scene]
  });

  return {
    prepareAudio: () => scene.prepareAudio(),
    demo: () => scene.playDemo(),
    start: () => scene.startRecording(),
    tap: () => scene.tapRhythm(),
    pressStart: () => scene.pressStart(),
    pressEnd: () => scene.pressEnd(),
    reset: () => scene.resetMission(),
    destroy: () => game.destroy(true)
  };
}

class RhythmEchoScene extends Phaser.Scene {
  private readonly sceneConfig: NormalizedRhythmEchoSceneConfig;
  private readonly onSceneEvent: (event: RhythmEchoSceneEvent) => void;
  private graphics!: Phaser.GameObjects.Graphics;
  private titleText!: Phaser.GameObjects.Text;
  private statusText!: Phaser.GameObjects.Text;
  private scoreText!: Phaser.GameObjects.Text;
  private status: RhythmEchoStatus = "ready";
  private recordStartAt = 0;
  private currentExpected = 0;
  private demoIndex = -1;
  private inputTimes: number[] = [];
  private inputPulses: RhythmPulse[] = [];
  private activePressStart: number | null = null;
  private hitKeys = new Set<number>();
  private demoTimers: Phaser.Time.TimerEvent[] = [];
  private demoTimeouts: number[] = [];
  private hits = 0;
  private misses = 0;
  private extras = 0;
  private combo = 0;
  private maxCombo = 0;
  private score = 0;
  private energy = 100;
  private currentMessage = "准备";
  private lastJudgement: RhythmEchoJudgement | undefined;
  private audioReady = false;
  private audioPreparing = false;
  private audioError = "";
  private audioSource: Extract<AudioPlaySource, "soundfont" | "lesson_audio" | "oscillator" | "failed"> | undefined;
  private celebratedMilestones = new Set<number>();
  private backgroundImage: Phaser.GameObjects.Image | null = null;
  private heroPresenter: TemplateCharacterPresenter | null = null;
  private propImages: Phaser.GameObjects.Image[] = [];
  private rewardImage: Phaser.GameObjects.Image | null = null;
  private receiverDish: Phaser.GameObjects.Container | null = null;
  private activeBeam: Phaser.GameObjects.Line | null = null;
  private nodeLabels = new Map<number, Phaser.GameObjects.Text>();

  constructor(config: RhythmEchoSceneConfig, onEvent: (event: RhythmEchoSceneEvent) => void) {
    super("rhythm_echo_scene");
    this.sceneConfig = buildRhythmEchoSceneConfig(config as Record<string, unknown>) as NormalizedRhythmEchoSceneConfig;
    this.energy = this.sceneConfig.energy_max;
    this.onSceneEvent = onEvent;
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
    const reward = this.sceneConfig.asset_manifest?.rewards?.[0];
    if (reward) this.load.image(REWARD_ASSET_KEY, reward);
  }

  create() {
    if (this.textures.exists(BACKGROUND_ASSET_KEY)) {
      this.backgroundImage = this.add.image(WIDTH / 2, HEIGHT / 2, BACKGROUND_ASSET_KEY).setDisplaySize(WIDTH, HEIGHT).setDepth(-10);
    }
    this.graphics = this.add.graphics();
    this.titleText = this.add.text(34, 24, this.sceneTitle(), {
      color: "#fff8dd",
      fontFamily: "Noto Sans SC, PingFang SC, sans-serif",
      fontSize: "30px",
      fontStyle: "bold"
    });
    this.statusText = this.add.text(34, 64, "先准备采样音色，再听示范。", {
      color: "#ffffff",
      fontFamily: "Noto Sans SC, PingFang SC, sans-serif",
      fontSize: "19px"
    });
    this.scoreText = this.add.text(WIDTH - 36, 28, "0", {
      color: "#fff8dd",
      fontFamily: "Noto Sans SC, PingFang SC, sans-serif",
      fontSize: "30px",
      fontStyle: "bold"
    }).setOrigin(1, 0);
    this.heroPresenter = new TemplateCharacterPresenter(this, {
      poseKeys: HERO_ASSET_KEYS,
      x: 118,
      y: 336,
      displaySize: 188,
      depth: 7,
      preserveAspectRatio: true,
      reducedMotion: prefersReducedMotion()
    });
    this.propImages = PROP_ASSET_KEYS
      .filter((key) => this.textures.exists(key))
      .map((key, index) => {
        const placements = [
          { x: 150, y: 256, size: 84, alpha: 0.86 },
          { x: 804, y: 198, size: 106, alpha: 0.9 },
          { x: 824, y: 396, size: 94, alpha: 0.82 }
        ];
        const placement = placements[index] || placements[0];
        return this.add.image(placement.x, placement.y, key)
          .setDepth(3)
          .setDisplaySize(placement.size, placement.size)
          .setAlpha(placement.alpha);
      });
    if (this.textures.exists(REWARD_ASSET_KEY)) {
      this.rewardImage = this.add.image(834, 134, REWARD_ASSET_KEY).setDepth(6).setDisplaySize(86, 86).setAlpha(0.9);
    }
    this.receiverDish = this.createReceiverDish();
    this.input.on("pointerdown", () => this.pressStart());
    this.input.on("pointerup", () => this.pressEnd());
    this.input.on("pointerupoutside", () => this.pressEnd());
    this.renderScene();
  }

  update() {
    if (this.status !== "recording") return;
    const elapsed = this.time.now - this.recordStartAt;
    if (this.activePressStart !== null && elapsed - this.activePressStart > this.totalDurationMs) {
      this.pressEnd();
      return;
    }
    if (elapsed > this.totalDurationMs + this.sceneConfig.judgement_windows.late_ms && this.activePressStart === null) {
      this.finishFromWaveform();
    }
    this.renderScene();
  }

  async prepareAudio() {
    if (this.audioPreparing) return;
    if (this.audioReady) {
      this.emitEvent("audio", "采样已就绪");
      return;
    }
    this.audioPreparing = true;
    this.audioError = "";
    this.audioSource = undefined;
    this.currentMessage = "正在加载采样音色";
    this.statusText.setText("正在加载采样音色");
    this.emitEvent("audio", "正在加载采样音色");
    this.renderScene();

    const result = await prepareSampledInstrument("xylophone");
    this.audioPreparing = false;
    if (result.ok && result.source === "soundfont") {
      this.audioReady = true;
      this.audioSource = "soundfont";
      this.audioError = "";
      this.currentMessage = "采样就绪，听示范";
      this.statusText.setText("采样就绪，听示范");
      this.emitEvent("audio", "采样就绪，听示范");
    } else {
      const fallbackContext = getAudioContext();
      if (fallbackContext) {
        if (fallbackContext.state === "suspended") await fallbackContext.resume();
        this.audioReady = true;
        this.audioSource = "oscillator";
        this.audioError = "";
        this.currentMessage = "合成音就绪，听示范";
        this.statusText.setText("合成音就绪，听示范");
        this.emitEvent("audio", "合成音就绪，听示范");
      } else {
        this.audioReady = false;
        this.audioSource = "failed";
        this.audioError = "音频不可用，请重试";
        this.currentMessage = this.audioError;
        this.statusText.setText(this.audioError);
        this.emitEvent("audio", this.audioError);
      }
    }
    this.renderScene();
  }

  playDemo() {
    if (!this.canUseSampledAudio("先准备采样音色")) return;
    this.clearDemoTimers();
    this.resetCounters();
    this.status = "demo";
    this.currentMessage = "听示范";
    this.statusText.setText("听示范");
    this.scheduleTargetPlayback(260, true, () => {
      this.demoIndex = -1;
      this.status = "ready";
      this.emitEvent("demo", "轮到你");
      this.renderScene();
    });
    this.emitEvent("demo", "听示范");
    this.renderScene();
  }

  startRecording() {
    if (!this.canUseSampledAudio("先准备采样音色")) return;
    this.clearDemoTimers();
    this.resetCounters();
    this.status = "blind_demo";
    this.currentMessage = "盲听复刻";
    this.statusText.setText("盲听复刻");
    this.scheduleTargetPlayback(260, false, () => {
      this.status = "recording";
      this.recordStartAt = this.time.now;
      this.currentMessage = "按住复刻";
      this.statusText.setText("按住复刻");
      this.emitEvent("start", "按住复刻");
      this.renderScene();
    });
    this.emitEvent("start", "盲听复刻");
    this.renderScene();
  }

  tapRhythm() {
    this.emitEvent("tap", "");
    this.pressStart();
    this.time.delayedCall(160, () => this.pressEnd());
  }

  pressStart() {
    this.emitEvent("press_start", "");
    if (!this.canUseSampledAudio("先准备采样音色")) return;
    if (this.status === "ready" || this.status === "demo" || this.status === "blind_demo" || this.status === "count_in") {
      this.emitJudgement("too_early", this.status === "ready" ? "先开始" : "等一下");
      return;
    }
    if (this.status === "success" || this.status === "failed" || this.activePressStart !== null) return;
    this.activePressStart = Math.max(0, this.time.now - this.recordStartAt);
    this.playPatternSound("quarter", true);
    this.currentMessage = "复刻中";
    this.statusText.setText("复刻中");
    this.heroPresenter?.pulse("hit");
    this.renderScene();
  }

  pressEnd() {
    this.emitEvent("press_end", "");
    if (this.status !== "recording" || this.activePressStart === null) return;
    const endMs = Math.max(this.activePressStart + MIN_PRESS_MS, this.time.now - this.recordStartAt);
    this.recordPulse(this.activePressStart, endMs - this.activePressStart);
    this.activePressStart = null;
    this.currentMessage = "继续听拍";
    this.statusText.setText("继续听拍");
    if (this.currentExpected >= this.expectedHits.length) this.finishFromWaveform();
    this.renderScene();
  }

  private recordPulse(startMs: number, durationMs: number) {
    const clampedStart = Math.max(0, Math.min(startMs, this.totalDurationMs + this.sceneConfig.judgement_windows.late_ms));
    const clampedDuration = Math.max(MIN_PRESS_MS, Math.min(durationMs, this.totalDurationMs));
    this.inputTimes.push(clampedStart);
    this.inputPulses.push({ start_ms: clampedStart, duration_ms: clampedDuration });
    const expected = this.expectedHits[this.currentExpected];
    if (!expected) {
      this.registerExtra();
      return;
    }
    const startDiff = clampedStart - expected.time_beats * this.beatMs;
    const durationDiff = clampedDuration - expected.duration_beats * this.beatMs;
    const absStartDiff = Math.abs(startDiff);
    const absDurationDiff = Math.abs(durationDiff);
    if (absStartDiff <= this.sceneConfig.judgement_windows.perfect_ms && absDurationDiff <= this.durationPerfectMs) {
      this.registerHit("perfect", expected);
      return;
    }
    if (absStartDiff <= this.sceneConfig.judgement_windows.good_ms && absDurationDiff <= this.durationGoodMs) {
      this.registerHit("good", expected);
      return;
    }
    if (absStartDiff <= this.sceneConfig.judgement_windows.late_ms && absDurationDiff <= this.durationLateMs) {
      this.registerLooseHit(Math.abs(startDiff) >= Math.abs(durationDiff) ? (startDiff < 0 ? "early" : "late") : (durationDiff < 0 ? "short" : "long"), expected);
      return;
    }
    this.registerLooseHit(Math.abs(startDiff) >= Math.abs(durationDiff) ? (startDiff < 0 ? "early" : "late") : (durationDiff < 0 ? "short" : "long"), expected);
  }

  private scheduleTargetPlayback(delayBase: number, visible: boolean, onComplete: () => void) {
    let completed = false;
    const finishPlayback = () => {
      if (completed) return;
      completed = true;
      onComplete();
    };
    this.expectedHits.forEach((hit, index) => {
      this.demoTimers.push(
        this.time.delayedCall(delayBase + hit.time_beats * this.beatMs, () => {
          this.demoIndex = visible ? index : -1;
          this.playPatternSound(hit.step, true);
          if (visible) this.pulseAt(hit.time_beats, "demo");
          this.renderScene();
        })
      );
    });
    const completeDelay = delayBase + this.totalDurationMs + 520;
    this.demoTimers.push(this.time.delayedCall(completeDelay, finishPlayback));
    this.demoTimeouts.push(window.setTimeout(finishPlayback, completeDelay + 160));
  }

  resetMission() {
    this.clearDemoTimers();
    this.resetCounters();
    this.status = "ready";
    this.currentMessage = "准备";
    this.statusText.setText("准备");
    this.emitEvent("reset", "准备");
    this.renderScene();
  }

  private registerHit(judgement: "perfect" | "good", expected: RhythmTimelineItem) {
    this.hitKeys.add(this.currentExpected);
    this.currentExpected += 1;
    this.hits += 1;
    this.combo += 1;
    this.maxCombo = Math.max(this.maxCombo, this.combo);
    this.score += this.sceneConfig.score_model[judgement];
    this.energy = Math.min(this.sceneConfig.energy_max, this.energy + (judgement === "perfect" ? 4 : 2));
    this.playPatternSound(expected.step, judgement === "perfect");
    this.pulseAt(expected.time_beats, judgement);
    this.playHitFx(expected.time_beats, judgement);
    this.comboBurst(this.combo, judgement);
    this.emitJudgement(judgement, judgement === "perfect" ? "完美" : "拍准了");
    this.checkMilestone();
    this.checkCompletion();
  }

  private registerLooseHit(judgement: "early" | "late" | "short" | "long", expected: RhythmTimelineItem) {
    this.hitKeys.add(this.currentExpected);
    this.currentExpected += 1;
    this.hits += 1;
    this.combo = 0;
    this.score += Math.round(this.sceneConfig.score_model.good * 0.45);
    this.energy = Math.max(0, this.energy - Math.round(this.sceneConfig.energy_loss_per_miss * 0.45));
    this.playPatternSound(expected.step, false);
    this.pulseAt(expected.time_beats, "loose");
    this.playMissFx(expected.time_beats, judgement);
    this.emitJudgement(judgement, judgement === "early" ? "早了" : judgement === "late" ? "晚了" : judgement === "short" ? "短了" : "长了");
    this.checkFailure();
    this.checkCompletion();
  }

  private registerMissed() {
    this.misses += 1;
    this.combo = 0;
    this.score += this.sceneConfig.score_model.missed;
    this.energy = Math.max(0, this.energy - this.sceneConfig.energy_loss_per_miss);
    this.pulseAt(this.expectedHits[this.currentExpected]?.time_beats || 0, "miss");
    this.playMissFx(this.expectedHits[this.currentExpected]?.time_beats || 0, "missed");
    this.currentExpected += 1;
    this.cameras.main.shake(110, 0.006);
    this.emitJudgement("missed", "漏掉了");
    this.checkFailure();
  }

  private registerExtra() {
    this.extras += 1;
    this.combo = 0;
    this.score += this.sceneConfig.score_model.wrong;
    this.energy = Math.max(0, this.energy - this.sceneConfig.energy_loss_per_miss);
    this.playMissFx((this.time.now - this.recordStartAt) / this.beatMs, "extra");
    this.cameras.main.shake(110, 0.006);
    this.emitJudgement("extra", "多拍了");
    this.checkFailure();
  }

  private checkMilestone() {
    if (this.sceneConfig.combo_milestones.includes(this.combo) && !this.celebratedMilestones.has(this.combo)) {
      this.celebratedMilestones.add(this.combo);
      this.milestoneBurst(this.combo);
    }
  }

  private checkCompletion() {
    if (this.currentExpected >= this.expectedHits.length) {
      this.finishFromWaveform();
    }
  }

  private checkFailure() {
    if (this.energy <= 0) this.finishMission(false, "能量空了");
  }

  private finishMission(success: boolean, message: string) {
    if (this.status === "success" || this.status === "failed") return;
    this.status = success ? "success" : "failed";
    this.statusText.setText(message);
    if (success) this.playStageClearFx();
    else this.playMissFx(this.totalDurationMs / this.beatMs, "missed", true);
    this.emitEvent(success ? "mission_success" : "mission_failed", message);
    this.renderScene();
  }

  private finishFromWaveform() {
    if (this.status === "success" || this.status === "failed") return;
    while (this.currentExpected < this.expectedHits.length) this.registerMissed();
    this.finishMission(this.completionPassed, this.completionPassed ? "对接成功" : "波形错位");
  }

  private emitJudgement(judgement: RhythmEchoJudgement, message: string) {
    const shortMessage = this.shortFeedback(judgement, message);
    this.lastJudgement = judgement;
    this.currentMessage = shortMessage;
    this.statusText.setText(shortMessage);
    this.emitEvent("judgement", shortMessage, judgement);
    this.renderScene();
  }

  private emitEvent(type: RhythmEchoSceneEvent["type"], message: string, judgement?: RhythmEchoJudgement) {
    if (message) this.currentMessage = message;
    this.onSceneEvent({ type, judgement, message, snapshot: this.snapshot(message || this.currentMessage) });
  }

  private snapshot(message: string): RhythmEchoSnapshot {
    return {
      status: this.status,
      currentIndex: this.currentExpected,
      totalHits: this.expectedHits.length,
      hits: this.hits,
      misses: this.misses,
      extras: this.extras,
      combo: this.combo,
      maxCombo: this.maxCombo,
      score: this.score,
      energy: this.energy,
      energyMax: this.sceneConfig.energy_max,
      accuracy: this.accuracy,
      progress: this.progress,
      audioMode: this.effectiveAudioMode,
      audioLabel: this.audioLabel,
      audioReady: this.audioReady,
      audioPreparing: this.audioPreparing,
      audioError: this.audioError || undefined,
      audioSource: this.audioSource,
      currentRound: Math.max(0, this.sceneConfig.active_round - 1),
      totalRounds: this.sceneConfig.round_count,
      cleared: this.status === "success" ? this.sceneConfig.active_round : Math.max(0, this.sceneConfig.active_round - 1),
      patternLabel: this.patternLabel,
      durationLabel: this.durationLabel,
      lastJudgement: this.lastJudgement,
      message
    };
  }

  private shortFeedback(judgement: RhythmEchoJudgement, fallback: string) {
    return {
      perfect: "完美",
      good: "拍准了",
      early: "早了",
      late: "晚了",
      short: "短了",
      long: "长了",
      extra: "多拍了",
      missed: "漏掉了",
      too_early: "等一下"
    }[judgement] || fallback.slice(0, 8);
  }

  private renderScene() {
    if (!this.graphics) return;
    const palette = palettes[this.sceneConfig.skin_play_mode];
    this.graphics.clear();
    this.drawBackground(palette);
    this.drawArcadeSet(palette);
    this.drawRhythmNodes(palette);
    this.drawPlayerTrail(palette);
    this.drawTimingGhosts(palette);
    this.drawMeters(palette);
    this.updateTemplateSprites();
    this.titleText.setText(this.sceneTitle());
    this.scoreText.setText(String(Math.max(0, this.score)));
  }

  private drawBackground(palette: (typeof palettes)[RhythmEchoPlayMode]) {
    if (!this.backgroundImage) this.cameras.main.setBackgroundColor(palette.bg);
    this.graphics.fillStyle(palette.deep, this.backgroundImage ? 0.06 : 0.82).fillRoundedRect(18, 16, WIDTH - 36, HEIGHT - 32, 34);
    this.graphics.fillGradientStyle(0xffffff, 0xffffff, palette.accent, palette.deep, 0.02, 0.01, 0.06, 0.08)
      .fillRoundedRect(42, 96, WIDTH - 84, 350, 30);
    this.graphics.fillStyle(0x061018, this.backgroundImage ? 0.1 : 0.46).fillRoundedRect(60, 118, WIDTH - 120, 302, 28);
    this.graphics.lineStyle(2, 0xffffff, this.backgroundImage ? 0.28 : 0.16).strokeRoundedRect(60, 118, WIDTH - 120, 302, 28);
    this.graphics.fillStyle(0xffffff, this.backgroundImage ? 0.04 : 0.08).fillCircle(782, 118, 126);
    this.graphics.fillStyle(palette.accent, this.backgroundImage ? 0.06 : 0.12).fillCircle(150, 392, 160);
    this.drawParallaxLights(palette);
  }

  private drawParallaxLights(palette: (typeof palettes)[RhythmEchoPlayMode]) {
    const drift = Math.sin(this.time.now / 780) * 8;
    for (let index = 0; index < 7; index += 1) {
      const x = 148 + index * 112 + drift * (index % 2 ? -1 : 1);
      const y = 148 + (index % 3) * 34;
      this.graphics.fillStyle(index % 2 ? palette.target : palette.accent, 0.08 + (index % 3) * 0.03).fillEllipse(x, y, 72, 16);
    }
  }

  private drawArcadeSet(palette: (typeof palettes)[RhythmEchoPlayMode]) {
    const progress = this.progress;
    this.graphics.fillStyle(0x03070d, 0.45).fillEllipse(136, 416, 150, 26);
    this.graphics.fillStyle(0x03070d, 0.42).fillEllipse(798, 394, 184, 28);
    this.graphics.lineStyle(8, palette.accent, 0.2 + progress * 0.22).strokeCircle(136, 300, 54 + progress * 24);
    this.graphics.lineStyle(7, palette.target, 0.2 + progress * 0.26).strokeCircle(800, 288, 48 + progress * 30);
    this.drawReceiverEnergy(palette);

    if (this.sceneConfig.skin_play_mode === "radio") {
      for (let index = 0; index < 8; index += 1) {
        const active = index / 10 < progress;
        this.graphics.fillStyle(active ? palette.accent : 0xffffff, active ? 0.88 : 0.2)
          .fillRoundedRect(334 + index * 38, 156 + (index % 2) * 20, 26, active ? 34 : 18, 8);
      }
      return;
    }
    if (this.sceneConfig.skin_play_mode === "cave") {
      for (let index = 0; index < 4; index += 1) {
        this.graphics.lineStyle(4, palette.accent, 0.14 + progress * 0.18).strokeCircle(520, 270, 46 + index * 44 + progress * 30);
      }
      return;
    }
    if (this.sceneConfig.skin_play_mode === "signal") {
      for (let index = 0; index < 8; index += 1) {
        this.graphics.fillStyle(index / 8 < progress ? palette.accent : 0xffffff, index / 8 < progress ? 0.9 : 0.18)
          .fillRoundedRect(318 + index * 48, 160 + (index % 2) * 38, 36, 28, 8);
      }
      return;
    }
    if (this.sceneConfig.skin_play_mode === "rain") {
      for (let index = 0; index < 18; index += 1) {
        const active = index / 18 < progress;
        this.graphics.fillStyle(active ? palette.accent : palette.soft, active ? 0.86 : 0.28).fillEllipse(196 + index * 34, 150 + (index % 3) * 34, 12, 28);
      }
      return;
    }
    for (let index = 0; index < 5; index += 1) {
      const active = index / 5 < progress;
      this.graphics.fillStyle(active ? palette.accent : palette.soft, active ? 0.9 : 0.34).fillRoundedRect(320 + index * 82, 168, 52, 52, 14);
      this.graphics.fillStyle(palette.target, active ? 0.95 : 0.34).fillCircle(346 + index * 82, 194, 14);
    }
  }

  private drawReceiverEnergy(palette: (typeof palettes)[RhythmEchoPlayMode]) {
    const energy = this.status === "success" ? 1 : this.progress;
    this.graphics.fillStyle(0xffffff, this.backgroundImage ? 0.04 : 0.1).fillRoundedRect(714, 182, 172, 188, 28);
    this.graphics.lineStyle(5, palette.target, 0.2 + energy * 0.46).strokeRoundedRect(724, 192, 152, 168, 24);
    this.graphics.fillStyle(palette.target, 0.18 + energy * 0.28).fillCircle(800, 276, 36 + energy * 22);
    this.graphics.fillStyle(palette.deep, this.backgroundImage ? 0.46 : 0.88).fillCircle(800, 276, 36);
    this.graphics.fillStyle(palette.target, 0.28 + energy * 0.58).fillCircle(800, 276, 20 + energy * 10);
    this.graphics.lineStyle(4, palette.accent, 0.18 + energy * 0.28).lineBetween(740, 354, 860, 354);
  }

  private drawRhythmNodes(palette: (typeof palettes)[RhythmEchoPlayMode]) {
    const hideTarget = this.status === "blind_demo" || this.status === "recording";
    this.addOrUpdateLaneLabel(900, 176, TRACK_Y - 78, hideTarget ? "盲听中" : "目标节奏");
    this.addOrUpdateLaneLabel(901, 176, PLAYER_Y - 48, "复刻轨道");
    this.graphics.lineStyle(8, 0xffffff, 0.14).lineBetween(196, TRACK_Y, 760, TRACK_Y);
    this.graphics.lineStyle(5, palette.accent, 0.22 + this.progress * 0.44).lineBetween(196, TRACK_Y, 196 + 564 * this.progress, TRACK_Y);
    this.echoNodes.forEach((node, index) => {
      const { item, x, y, width, hitIndex } = node;
      if (!item.hit_required) {
        if (!hideTarget) this.drawRestNode(x, y, palette);
        this.addOrUpdateLaneLabel(index, x, y + 22, hideTarget ? "" : "休");
        return;
      }
      const hit = this.hitKeys.has(hitIndex);
      const demo = this.demoIndex === hitIndex;
      if (!hideTarget) this.drawEchoNode(node, palette, hit, demo);
      this.addOrUpdateLaneLabel(index, x, y + 24, hideTarget ? "" : item.label);
      if (demo) this.drawSignalBeam(136, 300, x, y, palette.target, 0.72);
      if (hit) this.drawSignalBeam(x, y, 800, 276, palette.accent, 0.26);
    });
  }

  private drawRestNode(x: number, y: number, palette: (typeof palettes)[RhythmEchoPlayMode]) {
    this.graphics.fillStyle(0x071017, 0.78).fillRoundedRect(x - 22, y - 18, 44, 36, 12);
    this.graphics.lineStyle(2, palette.soft, 0.45).strokeRoundedRect(x - 22, y - 18, 44, 36, 12);
    this.graphics.fillStyle(0xffffff, 0.34).fillRect(x - 9, y - 8, 18, 16);
  }

  private drawEchoNode(node: EchoStageNode, palette: (typeof palettes)[RhythmEchoPlayMode], hit: boolean, demo: boolean) {
    const phase = Math.sin((this.time.now + node.hitIndex * 140) / 240);
    const glow = hit || demo ? 0.34 + phase * 0.08 : 0.12;
    const color = hit ? palette.accent : demo ? palette.target : palette.soft;
    this.graphics.fillStyle(color, glow).fillCircle(node.x, node.y, node.width * 0.62);
    this.graphics.fillStyle(0x071017, 0.86).fillRoundedRect(node.x - node.width / 2, node.y - 26, node.width, 52, 16);
    this.graphics.lineStyle(hit || demo ? 5 : 3, color, hit || demo ? 0.92 : 0.42).strokeRoundedRect(node.x - node.width / 2, node.y - 26, node.width, 52, 16);
    this.graphics.fillStyle(color, hit || demo ? 0.95 : 0.58).fillRoundedRect(node.x - node.width * 0.34, node.y - 8, node.width * 0.68, 16, 8);
    if (node.duration >= 1.5) {
      this.graphics.fillStyle(palette.target, hit || demo ? 0.86 : 0.28).fillCircle(node.x + node.width / 2 - 14, node.y, 8);
    }
  }

  private drawPlayerTrail(palette: (typeof palettes)[RhythmEchoPlayMode]) {
    this.graphics.lineStyle(7, 0xffffff, 0.12).lineBetween(196, PLAYER_Y, 760, PLAYER_Y);
    this.inputPulses.forEach((pulse, index) => {
      const hit = this.hitKeys.has(index);
      const x = this.nodeX(pulse.start_ms / this.beatMs);
      const width = this.durationWidth(pulse.duration_ms / this.beatMs);
      this.graphics.fillStyle(hit ? palette.accent : palette.danger, hit ? 0.92 : 0.78).fillRoundedRect(x - width / 2, PLAYER_Y - 17, width, 34, 14);
      this.graphics.lineStyle(3, hit ? palette.target : palette.danger, hit ? 0.62 : 0.8).strokeRoundedRect(x - width / 2, PLAYER_Y - 17, width, 34, 14);
      if (hit) this.drawSignalBeam(136, 326, x, PLAYER_Y, palette.accent, 0.28);
    });
    if (this.status === "recording" && this.activePressStart !== null) {
      const elapsed = Math.max(this.activePressStart + MIN_PRESS_MS, this.time.now - this.recordStartAt);
      const x = this.nodeX(this.activePressStart / this.beatMs);
      const width = this.durationWidth((elapsed - this.activePressStart) / this.beatMs);
      this.graphics.fillStyle(palette.target, 0.9).fillRoundedRect(x - width / 2, PLAYER_Y - 18, width, 36, 14);
      this.drawSignalBeam(136, 326, Math.min(800, x + width / 2), PLAYER_Y, palette.target, 0.66);
    }
    if (!this.inputPulses.length && this.activePressStart === null) {
      this.graphics.fillStyle(0xffffff, 0.22).fillRoundedRect(226, PLAYER_Y - 8, 96, 16, 8);
    }
  }

  private drawTimingGhosts(palette: (typeof palettes)[RhythmEchoPlayMode]) {
    if (this.status === "success" || this.status === "failed") {
      this.expectedHits.forEach((item, index) => {
        const pulse = this.inputPulses[index];
        if (!pulse) return;
        const expectedX = this.nodeX(item.time_beats);
        const inputX = this.nodeX(pulse.start_ms / this.beatMs);
        const aligned = Math.abs(inputX - expectedX) <= 18 && Math.abs(this.durationWidth(item.duration_beats) - this.durationWidth(pulse.duration_ms / this.beatMs)) <= 22;
        this.graphics.lineStyle(3, aligned ? palette.accent : palette.danger, aligned ? 0.4 : 0.74).lineBetween(expectedX, TRACK_Y + 18, inputX, PLAYER_Y - 18);
      });
    }
    this.drawScanLine(palette);
  }

  private drawScanLine(palette: (typeof palettes)[RhythmEchoPlayMode]) {
    if (this.status !== "demo" && this.status !== "blind_demo" && this.status !== "recording") return;
    const elapsed = this.status === "recording" ? this.time.now - this.recordStartAt : this.time.now % this.totalDurationMs;
    const x = this.nodeX((elapsed / this.beatMs) % Math.max(0.1, this.totalDurationBeats));
    this.graphics.lineStyle(3, palette.target, 0.82).lineBetween(x, TRACK_Y - 58, x, PLAYER_Y + 36);
    this.graphics.fillStyle(palette.target, 0.9).fillCircle(x, TRACK_Y - 58, 7);
  }

  private durationWidth(durationBeats: number) {
    return Math.max(34, Math.min(116, 30 + Math.max(0.18, durationBeats) * 34));
  }

  private drawMeters(palette: (typeof palettes)[RhythmEchoPlayMode]) {
    this.graphics.fillStyle(0xffffff, 0.2).fillRoundedRect(34, 478, 316, 18, 9);
    this.graphics.fillStyle(this.energy <= this.sceneConfig.energy_max * 0.28 ? palette.danger : palette.accent, 0.96)
      .fillRoundedRect(34, 478, Math.max(8, 316 * (this.energy / this.sceneConfig.energy_max)), 18, 9);
    this.graphics.fillStyle(0xffffff, 0.2).fillRoundedRect(610, 478, 316, 18, 9);
    this.graphics.fillStyle(palette.target, 0.95).fillRoundedRect(610, 478, Math.max(8, 316 * this.progress), 18, 9);
  }

  private updateTemplateSprites() {
    const pose = this.status === "success" ? "win" : this.status === "failed" ? "miss" : this.status === "recording" || this.status === "demo" ? "action" : "idle";
    this.heroPresenter?.transitionTo(pose, this.status === "success" ? "success" : this.status === "failed" ? "miss" : this.status === "demo" ? "listen" : this.status === "recording" ? "hit" : "idle");
    this.propImages.forEach((image, index) => {
      const active = index < Math.max(1, Math.ceil(this.progress * this.propImages.length));
      image.setAlpha(this.status === "success" || active ? 0.96 : 0.52);
      image.setScale((this.status === "success" ? 1.08 : 1) + (active ? Math.sin((this.time.now + index * 140) / 240) * 0.04 : 0));
      image.setAngle(this.status === "demo" || this.status === "recording" || active ? Math.sin((this.time.now + index * 170) / 210) * 5 : 0);
    });
    this.updateReceiverDish();
    this.updateActiveBeam();
    if (this.rewardImage) {
      this.rewardImage.setVisible(this.status === "success" || this.combo >= 2);
      this.rewardImage.setScale(this.status === "success" ? 1.18 : 1);
    }
  }

  private pulseAt(timeBeats: number, judgement: "perfect" | "good" | "loose" | "miss" | "demo") {
    const color = judgement === "perfect" || judgement === "demo" ? 0xfff2bd : judgement === "good" ? 0x8ff0c2 : 0xe4573d;
    const ring = this.add.circle(this.nodeX(timeBeats), TRACK_Y, 18, color, 0.55).setDepth(8);
    this.tweens.add({
      targets: ring,
      scale: judgement === "demo" ? 2.2 : 2.6,
      alpha: 0,
      duration: 360,
      ease: "Cubic.Out",
      onComplete: () => ring.destroy()
    });
  }

  private playHitFx(timeBeats: number, judgement: "perfect" | "good") {
    const x = this.nodeX(timeBeats);
    const color = judgement === "perfect" ? 0xfff2bd : 0x8ff0c2;
    const link = this.add.line(0, 0, 136, 326, x, TRACK_Y, color, 0.86).setOrigin(0).setDepth(7);
    const note = this.add.star(x, TRACK_Y - 28, 5, 7, 18, color, 0.95).setDepth(9);
    this.tweens.add({ targets: link, alpha: 0, duration: 340, ease: "Cubic.Out", onComplete: () => link.destroy() });
    this.tweens.add({ targets: note, y: TRACK_Y - 70, angle: 120, alpha: 0, duration: 420, ease: "Back.Out", onComplete: () => note.destroy() });
    this.burstPropRelay(color);
    this.heroPresenter?.pulse("hit");
  }

  private playMissFx(timeBeats: number, judgement: "early" | "late" | "short" | "long" | "extra" | "missed", final = false) {
    const x = this.nodeX(Math.max(0, timeBeats));
    const label = this.add.text(x, TRACK_Y - 42, judgement === "extra" ? "多拍" : judgement === "early" ? "抢拍" : judgement === "late" ? "拖拍" : judgement === "short" ? "太短" : judgement === "long" ? "太长" : "断链", {
      color: "#ffd6c4",
      fontFamily: "Noto Sans SC, PingFang SC, sans-serif",
      fontSize: final ? "32px" : "24px",
      fontStyle: "bold"
    }).setOrigin(0.5).setDepth(10);
    this.cameras.main.shake(final ? 180 : 90, final ? 0.008 : 0.004);
    this.tweens.add({ targets: label, y: TRACK_Y - 78, alpha: 0, duration: 420, ease: "Cubic.Out", onComplete: () => label.destroy() });
    this.heroPresenter?.pulse("miss");
  }

  private addOrUpdateLaneLabel(index: number, x: number, y: number, label: string) {
    const text = this.children.getByName(`rhythm_lane_label_${index}`) as Phaser.GameObjects.Text | null;
    const display = label.length > 4 ? label.slice(0, 4) : label;
    if (text) {
      text.setText(display);
      text.setPosition(x, y + 46);
      return;
    }
    this.add.text(x, y + 46, display, {
      color: "#fff8dd",
      fontFamily: "Noto Sans SC, PingFang SC, sans-serif",
      fontSize: "15px",
      fontStyle: "bold"
    }).setOrigin(0.5).setName(`rhythm_lane_label_${index}`);
  }

  private playStageClearFx() {
    this.successBurst();
    this.cameras.main.flash(360, 210, 235, 255);
    const label = this.add.text(480, 228, "光链完成", {
      color: "#fff2bd",
      fontFamily: "Noto Sans SC, PingFang SC, sans-serif",
      fontSize: "48px",
      fontStyle: "bold"
    }).setOrigin(0.5);
    this.tweens.add({ targets: label, scale: 1.16, alpha: 0, duration: 760, ease: "Back.Out", onComplete: () => label.destroy() });
  }

  private comboBurst(combo: number, judgement: "perfect" | "good") {
    const label = this.add.text(480, 128, judgement === "perfect" ? "完全踩准" : `${combo} 连击`, {
      color: judgement === "perfect" ? "#fff2bd" : "#c9ffe3",
      fontFamily: "Noto Sans SC, PingFang SC, sans-serif",
      fontSize: judgement === "perfect" ? "38px" : "30px",
      fontStyle: "bold"
    }).setOrigin(0.5);
    this.tweens.add({ targets: label, y: 92, alpha: 0, duration: 520, ease: "Cubic.Out", onComplete: () => label.destroy() });
  }

  private milestoneBurst(combo: number) {
    const label = this.add.text(480, 246, `${combo} 连击`, {
      color: "#fff8dd",
      fontFamily: "Noto Sans SC, PingFang SC, sans-serif",
      fontSize: "42px",
      fontStyle: "bold"
    }).setOrigin(0.5);
    this.tweens.add({ targets: label, scale: 1.35, alpha: 0, duration: 700, ease: "Back.Out", onComplete: () => label.destroy() });
  }

  private successBurst() {
    const palette = palettes[this.sceneConfig.skin_play_mode];
    for (let index = 0; index < 14; index += 1) {
      const dot = this.add.circle(480, 256, 8, index % 2 ? palette.target : palette.accent, 0.95);
      this.tweens.add({
        targets: dot,
        x: 480 + Math.cos((index / 14) * Math.PI * 2) * 280,
        y: 256 + Math.sin((index / 14) * Math.PI * 2) * 150,
        alpha: 0,
        duration: 720,
        ease: "Cubic.Out",
        onComplete: () => dot.destroy()
      });
    }
  }

  private createReceiverDish() {
    const dish = this.add.container(800, 276).setDepth(5);
    dish.add(this.add.circle(0, 0, 44, 0x061018, 0.78));
    dish.add(this.add.circle(0, 0, 28, 0xffffff, 0.12));
    dish.add(this.add.rectangle(0, 0, 72, 12, 0xffffff, 0.18));
    dish.add(this.add.rectangle(0, 0, 12, 72, 0xffffff, 0.18));
    dish.add(this.add.circle(0, 0, 14, 0xfff2bd, 0.5));
    return dish;
  }

  private updateReceiverDish() {
    if (!this.receiverDish) return;
    const active = this.status === "demo" || this.status === "recording" || this.status === "success";
    const pulse = active ? 1 + Math.sin(this.time.now / 150) * 0.06 + this.progress * 0.08 : 1;
    this.receiverDish.setScale(this.status === "success" ? 1.22 : pulse);
    this.receiverDish.setAngle(active ? Math.sin(this.time.now / 300) * 2 : 0);
    this.receiverDish.setAlpha(this.status === "failed" ? 0.58 : 1);
  }

  private updateActiveBeam() {
    if (this.status === "recording" && this.activePressStart !== null) {
      if (!this.activeBeam) {
        this.activeBeam = this.add.line(0, 0, 136, 326, 720, PLAYER_Y, palettes[this.sceneConfig.skin_play_mode].target, 0.72).setOrigin(0).setDepth(8);
      }
      const elapsed = Math.max(this.activePressStart + MIN_PRESS_MS, this.time.now - this.recordStartAt);
      const x = this.nodeX((elapsed - this.activePressStart) / this.beatMs + this.activePressStart / this.beatMs);
      this.activeBeam.setTo(136, 326, Math.min(800, x), PLAYER_Y);
      this.activeBeam.setAlpha(0.42 + Math.sin(this.time.now / 90) * 0.18);
      return;
    }
    this.activeBeam?.destroy();
    this.activeBeam = null;
  }

  private drawSignalBeam(fromX: number, fromY: number, toX: number, toY: number, color: number, alpha: number) {
    this.graphics.lineStyle(9, color, alpha * 0.28).lineBetween(fromX, fromY, toX, toY);
    this.graphics.lineStyle(3, color, alpha).lineBetween(fromX, fromY, toX, toY);
  }

  private burstPropRelay(color: number) {
    const prop = this.propImages[Math.min(this.propImages.length - 1, Math.max(0, this.hits % Math.max(1, this.propImages.length)))];
    if (!prop) return;
    const flare = this.add.circle(prop.x, prop.y, 18, color, 0.6).setDepth(9);
    this.tweens.add({ targets: flare, scale: 2.5, alpha: 0, duration: 420, ease: "Cubic.Out", onComplete: () => flare.destroy() });
    this.tweens.add({ targets: prop, scale: 1.18, y: prop.y - 10, duration: 160, yoyo: true, ease: "Back.Out" });
  }

  private pulseCountdown(value: number) {
    const text = this.add.text(480, 246, String(value || "GO"), {
      color: "#fff8dd",
      fontFamily: "Noto Sans SC, PingFang SC, sans-serif",
      fontSize: "84px",
      fontStyle: "bold"
    }).setOrigin(0.5);
    this.tweens.add({ targets: text, scale: 1.25, alpha: 0, duration: 520, ease: "Cubic.Out", onComplete: () => text.destroy() });
  }

  private canUseSampledAudio(message: string) {
    if (this.audioReady) return true;
    const prompt = this.audioError || message;
    this.currentMessage = prompt;
    this.statusText.setText(prompt);
    this.emitEvent("audio", prompt);
    this.renderScene();
    return false;
  }

  private playPatternSound(step: string, strong: boolean) {
    if (this.effectiveAudioMode === "lesson_audio") return;
    const frequency = step === "eighth" ? 520 : step === "half" ? 180 : step === "syncopation" ? 620 : 260;
    this.playTone(step === "rest" ? "triangle" : strong ? "square" : "triangle", frequency, step === "half" ? 150 : 90, strong ? 0.18 : 0.11);
  }

  private playTone(_wave: OscillatorType, frequency: number, durationMs: number, gainValue: number) {
    if (!this.audioReady) return;
    const midi = Math.max(24, Math.min(96, Math.round(69 + 12 * Math.log2(frequency / 440))));
    playHybridToneSequence([midi - 60], {
      instrument: "xylophone",
      duration: Math.max(0.06, durationMs / 1000),
      gap: Math.max(0.08, durationMs / 1000 + 0.04),
      gain: Math.max(0.1, Math.min(1, gainValue * 4)),
      oscillatorWave: _wave,
      allowOscillatorFallback: true
    });
  }

  private resetCounters() {
    this.currentExpected = 0;
    this.demoIndex = -1;
    this.inputTimes = [];
    this.inputPulses = [];
    this.activePressStart = null;
    this.hitKeys = new Set();
    this.hits = 0;
    this.misses = 0;
    this.extras = 0;
    this.combo = 0;
    this.maxCombo = 0;
    this.score = 0;
    this.energy = this.sceneConfig.energy_max;
    this.lastJudgement = undefined;
    this.celebratedMilestones = new Set();
  }

  private clearDemoTimers() {
    this.demoTimers.forEach((timer) => timer.remove(false));
    this.demoTimers = [];
    this.demoTimeouts.forEach((timer) => window.clearTimeout(timer));
    this.demoTimeouts = [];
  }

  private hitIndexForTimelineIndex(timelineIndex: number) {
    let hitIndex = -1;
    for (let index = 0; index <= timelineIndex; index += 1) {
      if (this.sceneConfig.pattern_timeline[index]?.hit_required) hitIndex += 1;
    }
    return this.sceneConfig.pattern_timeline[timelineIndex]?.hit_required ? hitIndex : -1;
  }

  private timelineX(timeBeats: number) {
    const usable = 720;
    return 120 + (Math.max(0, timeBeats) / Math.max(1, this.totalDurationBeats)) * usable;
  }

  private nodeX(timeBeats: number) {
    return NODE_BASE_X + (Math.max(0, timeBeats) / Math.max(1, this.totalDurationBeats)) * NODE_SPAN;
  }

  private get echoNodes(): EchoStageNode[] {
    return this.sceneConfig.pattern_timeline.map((item, index) => {
      const hitIndex = this.hitIndexForTimelineIndex(index);
      return {
        item,
        hitIndex,
        x: this.nodeX(item.time_beats),
        y: TRACK_Y + (index % 2 === 0 ? -22 : 22),
        width: this.durationWidth(item.duration_beats),
        duration: item.duration_beats
      };
    });
  }

  private sceneTitle() {
    return {
      radio: "节奏复刻舞台",
      cave: "山洞回声",
      signal: "节奏信号",
      rain: "雨点窗台",
      kitchen: "厨房乐队"
    }[this.sceneConfig.skin_play_mode];
  }

  private get beatMs() {
    return 60000 / this.sceneConfig.bpm;
  }

  private get expectedHits() {
    return this.sceneConfig.pattern_timeline.filter((item) => item.hit_required);
  }

  private get totalDurationBeats() {
    const last = this.sceneConfig.pattern_timeline[this.sceneConfig.pattern_timeline.length - 1];
    return last ? last.time_beats + last.duration_beats : 2;
  }

  private get totalDurationMs() {
    return this.totalDurationBeats * this.beatMs;
  }

  private get accuracy() {
    const total = Math.max(1, this.expectedHits.length + this.extras);
    return this.hits / total;
  }

  private get waveformAccuracy() {
    const expected = this.targetPulses;
    if (!expected.length) return 1;
    const totalPenalty = expected.reduce((sum, target, index) => {
      const pulse = this.inputPulses[index];
      if (!pulse) return sum + 1;
      const startPenalty = Math.min(1, Math.abs(pulse.start_ms - target.start_ms) / Math.max(1, this.sceneConfig.judgement_windows.late_ms));
      const durationPenalty = Math.min(1, Math.abs(pulse.duration_ms - target.duration_ms) / Math.max(1, this.durationLateMs));
      return sum + (startPenalty + durationPenalty) / 2;
    }, Math.max(0, this.inputPulses.length - expected.length));
    return Math.max(0, Math.min(1, 1 - totalPenalty / Math.max(1, expected.length)));
  }

  private get completionPassed() {
    return Math.min(this.accuracy, this.waveformAccuracy) >= this.sceneConfig.required_accuracy && this.inputPulses.length === this.expectedHits.length && this.energy > 0;
  }

  private get progress() {
    if (this.status === "success") return 1;
    return Math.max(0, Math.min(1, this.hits / Math.max(1, this.expectedHits.length)));
  }

  private get patternLabel() {
    return this.sceneConfig.pattern_timeline.map((item) => item.label).join(" ");
  }

  private get durationLabel() {
    return this.expectedHits
      .map((item) => (item.duration_beats >= 1.5 ? "长" : item.duration_beats <= 0.5 ? "短" : "中"))
      .join("-");
  }

  private get targetPulses(): RhythmPulse[] {
    return this.expectedHits.map((item) => ({
      start_ms: item.time_beats * this.beatMs,
      duration_ms: item.duration_beats * this.beatMs
    }));
  }

  private get durationPerfectMs() {
    return Math.max(90, this.beatMs * 0.18);
  }

  private get durationGoodMs() {
    return Math.max(150, this.beatMs * 0.28);
  }

  private get durationLateMs() {
    return Math.max(240, this.beatMs * 0.45);
  }

  private get effectiveAudioMode(): RhythmEchoAudioMode {
    if (this.sceneConfig.audio_mode === "lesson_audio" && this.sceneConfig.lesson_audio_sync?.audio_url) return "lesson_audio";
    if (this.sceneConfig.audio_mode === "hybrid" && this.sceneConfig.lesson_audio_sync?.audio_url) return "lesson_audio";
    return "internal_pattern";
  }

  private get audioLabel() {
    if (this.effectiveAudioMode === "lesson_audio") return this.sceneConfig.lesson_audio_sync?.segment_label || "作品片段";
    return "内置节奏";
  }
}

function normalizePlayMode(value: unknown, skinId: string): RhythmEchoPlayMode {
  if (value === "radio" || value === "cave" || value === "signal" || value === "rain" || value === "kitchen") return value;
  return (
    {
      rhythm_radio: "radio",
      echo_cave: "cave",
      robot_signal: "signal",
      rain_window: "rain",
      kitchen_band: "kitchen"
    }[skinId] || "radio"
  ) as RhythmEchoPlayMode;
}

function normalizeAudioMode(value: unknown): RhythmEchoAudioMode {
  if (value === "internal_pattern" || value === "lesson_audio" || value === "hybrid") return value;
  return "hybrid";
}

function normalizeComboMilestones(value: unknown) {
  const raw = Array.isArray(value) ? value : [2, 4, 6];
  return Array.from(new Set(raw.map(Number).filter((item) => Number.isFinite(item) && item > 0).map((item) => clampNumber(item, 1, 24, 2)))).sort((a, b) => a - b);
}

function normalizeJudgementWindows(value: unknown, fallbackTolerance: number): JudgementWindows {
  const raw = isRecord(value) ? value : {};
  const perfect = clampNumber(Number(raw.perfect_ms), 35, 120, 70);
  const good = clampNumber(Number(raw.good_ms), perfect, 240, Math.max(perfect, Math.min(fallbackTolerance, 180)));
  const late = clampNumber(Number(raw.late_ms), good, 380, Math.max(good, 260));
  return { perfect_ms: perfect, good_ms: good, late_ms: late };
}

function normalizeInputMap(value: unknown) {
  const raw = isRecord(value) ? value : {};
  return { primary: String(raw.primary || "Space"), pointer: raw.pointer !== false };
}

function normalizeFxProfile(value: unknown) {
  const raw = isRecord(value) ? value : {};
  return {
    hit: String(raw.hit || "echo_burst"),
    miss: String(raw.miss || "track_shake"),
    success: String(raw.success || "skin_echo_finish")
  };
}

function normalizeScoreModel(value: unknown): ScoreModel {
  const raw = isRecord(value) ? value : {};
  return {
    perfect: clampNumber(Number(raw.perfect), 20, 500, 120),
    good: clampNumber(Number(raw.good), 10, 300, 80),
    wrong: -Math.abs(clampNumber(Number(raw.wrong), -200, 200, -40)),
    missed: -Math.abs(clampNumber(Number(raw.missed), -240, 240, -60))
  };
}

function normalizeLessonAudioSync(value: unknown): LessonAudioSync {
  if (!isRecord(value)) return {};
  const audioUrl = String(value.audio_url || value.source_audio_url || value.audio_clip_url || "");
  if (!audioUrl) return {};
  return {
    audio_url: audioUrl,
    bpm: clampNumber(Number(value.bpm), 40, 180, 88),
    meter: String(value.meter || "4/4"),
    offset_ms: clampNumber(Number(value.offset_ms), 0, 10000, 0),
    segment_label: String(value.segment_label || value.selected_phrase_label || "作品片段")
  };
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
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function prefersReducedMotion() {
  return typeof window !== "undefined" && window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
}
