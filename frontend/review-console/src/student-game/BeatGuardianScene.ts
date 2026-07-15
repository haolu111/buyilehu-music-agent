import Phaser from "phaser";
import { playHybridToneSequence } from "../shared/realAudio";
import { TemplateCharacterPresenter } from "./templateCharacterPresenter";
import { templateVisualPackForConfig } from "./templateVisualAssets";
import type { TemplatePoseKey, TemplateVisualPack } from "./types";

export type BeatGuardianPlayMode = "race" | "gate" | "station" | "spotlight" | "orbit";
export type BeatGuardianStatus = "ready" | "count_in" | "playing" | "success" | "failed";
export type BeatGuardianJudgement = "perfect" | "good" | "early" | "late" | "wrong" | "missed" | "too_early" | "already_hit";
export type BeatGuardianAudioMode = "internal_meter" | "lesson_audio" | "hybrid";

type BeatSoundProfile = {
  wave?: OscillatorType;
  frequency?: number;
  duration_ms?: number;
  gain?: number;
};

type LessonAudioSync = {
  audio_url?: string;
  bpm?: number;
  meter?: string;
  offset_ms?: number;
  segment_label?: string;
};

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

type MonsterSeed = {
  angle: number;
  spawnDistance: number;
  speed: number;
  wobbleMs: number;
  phase: number;
};

type MonsterState = MonsterSeed & {
  distance: number;
  impulse: number;
  cleared: boolean;
  clearAt: number;
  stunUntil: number;
  breachCooldownUntil: number;
  hitFlashUntil: number;
};

type NormalizedBeatGuardianSceneConfig = Omit<
  Required<BeatGuardianSceneConfig>,
  "beat_sound_profile" | "combo_milestones" | "fx_profile" | "input_map" | "judgement_windows" | "lesson_audio_sync" | "score_model" | "target_beats"
> & {
  beat_sound_profile: { strong: BeatSoundProfile; weak: BeatSoundProfile };
  combo_milestones: number[];
  fx_profile: { hit: string; miss: string; success: string };
  input_map: { primary: string; pointer: boolean };
  judgement_windows: JudgementWindows;
  lesson_audio_sync: LessonAudioSync;
  score_model: ScoreModel;
  target_beats: number[];
};

export type BeatGuardianSceneConfig = {
  engine?: "phaser_2d";
  scene_id?: "beat_guardian_scene";
  scene_phase?: "ready";
  game_feel?: "arcade_rhythm";
  runtime_shell?: "beat_guardian_shell" | "beat_guardian_arcade";
  skin_id?: string;
  skin_play_mode?: BeatGuardianPlayMode;
  meter?: string;
  beats_per_bar?: number;
  bpm?: number;
  target_beats?: number[];
  round_length_beats?: number;
  required_combo?: number;
  combo_required?: number;
  max_mistakes?: number;
  mistake_limit?: number;
  energy_max?: number;
  energy_loss_per_miss?: number;
  combo_milestones?: number[];
  judgement_windows?: Partial<JudgementWindows>;
  input_map?: { primary?: string; pointer?: boolean };
  fx_profile?: { hit?: string; miss?: string; success?: string };
  arcade_hud?: boolean;
  show_teacher_text_in_play?: boolean;
  score_model?: Partial<ScoreModel>;
  mission_duration_bars?: number;
  bars_per_round?: number;
  count_in_beats?: number;
  timing_tolerance_ms?: number;
  audio_mode?: BeatGuardianAudioMode;
  strong_beat_sound?: string;
  weak_beat_sound?: string;
  beat_sound_profile?: {
    strong?: BeatSoundProfile;
    weak?: BeatSoundProfile;
  };
  lesson_audio_sync?: LessonAudioSync;
  minimal_hud?: boolean;
  show_beat_track?: boolean;
  show_strong_beat_hint?: boolean;
  show_weak_beat_hint?: boolean;
  visual_beat_hint?: boolean;
  skin_objective?: string;
  reward_animation?: string;
  asset_manifest?: TemplateVisualPack;
};

export type BeatGuardianSnapshot = {
  status: BeatGuardianStatus;
  phase: BeatGuardianStatus;
  currentBeat: number;
  currentBar: number;
  beatsPerBar: number;
  missionBars: number;
  targetBeats: number[];
  hits: number;
  misses: number;
  falseAlarms: number;
  combo: number;
  maxCombo: number;
  requiredCombo: number;
  maxMistakes: number;
  score: number;
  energy: number;
  energyMax: number;
  countInRemaining: number;
  progress: number;
  audioMode: BeatGuardianAudioMode;
  audioLabel: string;
  skinObjective: string;
  shieldCracks?: number;
  pulsePhase?: number;
  monstersRemaining?: number;
  monstersCleared?: number;
  monsterTotal?: number;
  dangerLevel?: number;
  lastJudgement?: BeatGuardianJudgement;
  judgementCounts?: Partial<Record<BeatGuardianJudgement, number>>;
  message: string;
};

export type BeatGuardianSceneEvent = {
  type: "start" | "reset" | "guard" | "beat_tick" | "judgement" | "mission_success" | "mission_failed";
  judgement?: BeatGuardianJudgement;
  message?: string;
  snapshot: BeatGuardianSnapshot;
};

export type BeatGuardianController = {
  start: () => void;
  guard: () => void;
  reset: () => void;
  destroy: () => void;
};

const WIDTH = 960;
const HEIGHT = 520;
const BACKGROUND_ASSET_KEY = "beat_guard_template_bg";
const HERO_ASSET_KEYS: Record<TemplatePoseKey, string> = {
  idle: "beat_guard_pose_idle",
  action: "beat_guard_pose_action",
  miss: "beat_guard_pose_miss",
  win: "beat_guard_pose_win"
};
const PROP_ASSET_KEYS = [
  "beat_guard_prop_1",
  "beat_guard_prop_2",
  "beat_guard_prop_3",
  "beat_guard_prop_4",
  "beat_guard_prop_5",
  "beat_guard_prop_6"
];
const REWARD_ASSET_KEY = "beat_guard_reward";
const WEAK_BEAT_CUE_KEY = "beat_guard_weak_beat_cue";
const SLIME_MONSTER_ASSET_KEY = PROP_ASSET_KEYS[1];
const MONSTER_BASE_DISPLAY_SIZE = 64;
const ARENA_CENTER_X = 480;
const ARENA_CENTER_Y = 262;
const MONSTER_BREACH_DISTANCE = 132;
const MONSTER_WARNING_DISTANCE = 174;
const MAX_SHIELD_CRACKS = 6;
export const BEAT_GUARDIAN_MONSTER_TOTAL = 6;

const palettes: Record<BeatGuardianPlayMode, { bg: number; deep: number; accent: number; target: number; soft: number; danger: number }> = {
  race: { bg: 0x0f6f73, deep: 0x5c2518, accent: 0xf2b84b, target: 0xfff2bd, soft: 0x8ad7d1, danger: 0xe4573d },
  gate: { bg: 0x243f38, deep: 0x6d3f24, accent: 0xe2b35e, target: 0xfff0bd, soft: 0xabc7a4, danger: 0xd6503e },
  station: { bg: 0x18384f, deep: 0x13283a, accent: 0xf3c45b, target: 0xdff4ff, soft: 0x8fb7d6, danger: 0xff6b4a },
  spotlight: { bg: 0x172b44, deep: 0x0c1726, accent: 0xffd36d, target: 0xffffff, soft: 0x5e7895, danger: 0xf25f4c },
  orbit: { bg: 0x101f35, deep: 0x06101f, accent: 0xf2c94c, target: 0x9be7ff, soft: 0x6c79c8, danger: 0xff6b6b }
};

export function buildBeatGuardianSceneConfig(raw: Record<string, unknown>): BeatGuardianSceneConfig {
  const nested = isRecord(raw.scene_config) ? raw.scene_config : {};
  const merged = { ...raw, ...nested };
  const skinId = String(merged.skin_id || "castle_gate");
  const mode = normalizePlayMode(merged.skin_play_mode, skinId);
  const meter = String(merged.meter || "4/4");
  const beatsPerBar = clampNumber(Number(merged.beats_per_bar || meter.split("/")[0]), 2, 4, 4);
  const targetBeats = normalizeTargetBeats(merged.target_beats, beatsPerBar);
  const missionBars = clampNumber(Number(merged.mission_duration_bars || merged.bars_per_round), 1, 8, 4);
  const roundLength = clampNumber(Number(merged.round_length_beats), beatsPerBar, beatsPerBar * 8, beatsPerBar * missionBars);

  return {
    engine: "phaser_2d",
    scene_id: "beat_guardian_scene",
    scene_phase: "ready",
    game_feel: "arcade_rhythm",
    runtime_shell: "beat_guardian_shell",
    skin_id: skinId,
    skin_play_mode: mode,
    meter,
    beats_per_bar: beatsPerBar,
    bpm: clampNumber(Number(merged.bpm), 60, 132, 88),
    target_beats: targetBeats,
    round_length_beats: roundLength,
    required_combo: clampNumber(Number(merged.required_combo || merged.combo_required), 1, 24, 4),
    max_mistakes: clampNumber(Number(merged.max_mistakes || merged.mistake_limit), 0, 12, 5),
    energy_max: clampNumber(Number(merged.energy_max), 50, 150, 100),
    energy_loss_per_miss: clampNumber(Number(merged.energy_loss_per_miss), 8, 60, 24),
    combo_milestones: normalizeComboMilestones(merged.combo_milestones, Number(merged.required_combo || merged.combo_required || 4)),
    judgement_windows: normalizeJudgementWindows(merged.judgement_windows, Number(merged.timing_tolerance_ms || 170)),
    input_map: normalizeInputMap(merged.input_map),
    fx_profile: normalizeFxProfile(merged.fx_profile),
    arcade_hud: true,
    show_teacher_text_in_play: false,
    score_model: normalizeScoreModel(merged.score_model),
    mission_duration_bars: Math.ceil(roundLength / beatsPerBar),
    count_in_beats: clampNumber(Number(merged.count_in_beats), 0, 8, beatsPerBar),
    timing_tolerance_ms: clampNumber(Number(merged.timing_tolerance_ms), 80, 320, 170),
    audio_mode: normalizeAudioMode(merged.audio_mode),
    strong_beat_sound: String(merged.strong_beat_sound || "low_drum"),
    weak_beat_sound: String(merged.weak_beat_sound || "wood_tick"),
    beat_sound_profile: normalizeBeatSoundProfile(merged.beat_sound_profile),
    lesson_audio_sync: normalizeLessonAudioSync(merged.lesson_audio_sync),
    minimal_hud: true,
    show_beat_track: Boolean(merged.show_beat_track ?? true),
    show_strong_beat_hint: Boolean(merged.show_strong_beat_hint ?? true),
    show_weak_beat_hint: Boolean(merged.show_weak_beat_hint ?? false),
    visual_beat_hint: Boolean(merged.visual_beat_hint ?? true),
    skin_objective: String(merged.skin_objective || skinObjectiveForSkin(skinId)),
    reward_animation: String(merged.reward_animation || ""),
    asset_manifest: templateVisualPackForConfig(merged, "beat_guardian_core")
  };
}

export function mountBeatGuardianScene(
  parent: HTMLElement,
  config: BeatGuardianSceneConfig,
  onEvent: (event: BeatGuardianSceneEvent) => void
): BeatGuardianController {
  const built = buildBeatGuardianSceneConfig(config as Record<string, unknown>);
  const scene = new BeatGuardianScene(built, onEvent);
  const game = new Phaser.Game({
    type: Phaser.AUTO,
    parent,
    width: WIDTH,
    height: HEIGHT,
    backgroundColor: palettes[built.skin_play_mode || "gate"].bg,
    fps: {
      target: 60,
      min: 30
    },
    scale: {
      mode: Phaser.Scale.FIT,
      autoCenter: Phaser.Scale.CENTER_BOTH
    },
    scene: [scene]
  });

  return {
    start: () => scene.startMission(),
    guard: () => scene.guardBeat(),
    reset: () => scene.resetMission(),
    destroy: () => game.destroy(true)
  };
}

class BeatGuardianScene extends Phaser.Scene {
  private readonly sceneConfig: NormalizedBeatGuardianSceneConfig;
  private readonly onSceneEvent: (event: BeatGuardianSceneEvent) => void;
  private readonly monsterSeeds = createMonsterSeeds();
  private monsterStates: MonsterState[] = [];
  private graphics!: Phaser.GameObjects.Graphics;
  private titleText!: Phaser.GameObjects.Text;
  private statusText!: Phaser.GameObjects.Text;
  private scoreText!: Phaser.GameObjects.Text;
  private beatLabels: Phaser.GameObjects.Text[] = [];
  private status: BeatGuardianStatus = "ready";
  private startAt = 0;
  private lastBeatIndex = 0;
  private hits = 0;
  private misses = 0;
  private falseAlarms = 0;
  private combo = 0;
  private maxCombo = 0;
  private score = 0;
  private energy = 100;
  private shieldCracks = 0;
  private countInRemaining = 0;
  private lastCountInRemaining = 0;
  private currentMessage = "准备";
  private lastJudgement: BeatGuardianJudgement | undefined;
  private lastJudgementAt = 0;
  private shockwaveUntil = 0;
  private lastMonsterBreachAt = 0;
  private hitStopUntil = 0;
  private hitBeatKeys = new Set<string>();
  private missedBeatKeys = new Set<string>();
  private celebratedMilestones = new Set<number>();
  private lessonAudio: HTMLAudioElement | null = null;
  private lessonAudioFailed = false;
  private judgementCounts: Partial<Record<BeatGuardianJudgement, number>> = {};
  private backgroundImage: Phaser.GameObjects.Image | null = null;
  private heroPresenter: TemplateCharacterPresenter | null = null;
  private monsterImages: Array<Phaser.GameObjects.Image | null> = [];
  private focusProp: Phaser.GameObjects.Image | null = null;
  private rewardImage: Phaser.GameObjects.Image | null = null;

  constructor(config: BeatGuardianSceneConfig, onEvent: (event: BeatGuardianSceneEvent) => void) {
    super("beat_guardian_scene");
    this.sceneConfig = buildBeatGuardianSceneConfig(config as Record<string, unknown>) as NormalizedBeatGuardianSceneConfig;
    this.energy = Number(this.sceneConfig.energy_max);
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
    this.createWeakBeatCueTexture();
    this.monsterStates = this.createMonsterStates();
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
    this.statusText = this.add.text(34, 64, "按开始，看怪物靠近。", {
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
      x: 480,
      y: 274,
      displaySize: 142,
      depth: 7,
      reducedMotion: prefersReducedMotion(),
      stableScale: true
    });
    this.monsterImages = this.monsterSeeds.map(() => {
      const textureKey = this.textures.exists(SLIME_MONSTER_ASSET_KEY) ? SLIME_MONSTER_ASSET_KEY : WEAK_BEAT_CUE_KEY;
      if (!this.textures.exists(textureKey)) return null;
      return this.add.image(480, 260, textureKey).setDepth(5).setDisplaySize(MONSTER_BASE_DISPLAY_SIZE, MONSTER_BASE_DISPLAY_SIZE).setAlpha(0.82);
    });
    if (this.textures.exists(PROP_ASSET_KEYS[0])) {
      this.focusProp = this.add.image(480, 268, PROP_ASSET_KEYS[0]).setDepth(6).setDisplaySize(100, 100).setAlpha(0.34);
    }
    if (this.textures.exists(REWARD_ASSET_KEY)) {
      this.rewardImage = this.add.image(838, 128, REWARD_ASSET_KEY).setDepth(8).setDisplaySize(76, 76).setAlpha(0.9);
    }
    this.beatLabels = Array.from({ length: this.beatsPerBar }, (_, index) =>
      this.add.text(0, 0, String(index + 1), {
        color: index === 0 ? "#5c3516" : "#173028",
        fontFamily: "Noto Sans SC, PingFang SC, sans-serif",
        fontSize: "30px",
        fontStyle: "bold"
      }).setOrigin(0.5).setDepth(9)
    );
    this.input.on("pointerdown", () => this.guardBeat());
    this.renderScene();
  }

  update(_time: number, _delta: number) {
    if (this.status !== "count_in" && this.status !== "playing") return;
    const now = this.time.now;
    if (this.status === "count_in" && now < this.startAt) {
      this.countInRemaining = Math.max(1, Math.ceil((this.startAt - now) / this.beatMs));
      if (this.countInRemaining !== this.lastCountInRemaining) {
        this.lastCountInRemaining = this.countInRemaining;
        this.playBeatSound(false);
        this.pulseCountdown(this.countInRemaining);
      }
      this.renderScene();
      return;
    }

    if (this.status === "count_in") {
      this.status = "playing";
      this.countInRemaining = 0;
      this.emitEvent("beat_tick", "开始预判");
    }

    const beatIndex = Math.floor((now - this.startAt) / this.beatMs) + 1;
    if (beatIndex !== this.lastBeatIndex) this.registerBeatTick(beatIndex);
    this.markOverdueDownbeats(now);
    this.updateMonsterPressure(now, _delta);
    this.renderScene();
  }

  startMission() {
    this.resetCounters();
    this.status = "count_in";
    this.startAt = this.time.now + this.sceneConfig.count_in_beats * this.beatMs;
    this.countInRemaining = this.sceneConfig.count_in_beats;
    this.lastCountInRemaining = 0;
    this.currentMessage = "预备";
    this.statusText.setText("预备：怪物会靠近，强拍充能把它们弹开。");
    this.startAudio();
    this.emitEvent("start", "预备");
    this.renderScene();
  }

  guardBeat() {
    this.emitEvent("guard", "");
    if (this.status === "ready") {
      this.emitJudgement("too_early", "先开始");
      return;
    }
    const now = this.time.now;
    if (this.status === "count_in" && now >= this.startAt - this.sceneConfig.judgement_windows.good_ms) {
      this.status = "playing";
      this.countInRemaining = 0;
      this.lastBeatIndex = 0;
    } else if (this.status === "count_in" || now < this.startAt) {
      this.emitJudgement("too_early", "等护盾收缩");
      return;
    }
    if (this.status === "success" || this.status === "failed") return;

    const nearestBar = this.nearestChargeBar(now);
    const nearestBeatIndex = nearestBar * this.beatsPerBar + 1;
    if (nearestBeatIndex < 1 || nearestBeatIndex > this.totalBeats) {
      this.applyPenalty("late", this.sceneConfig.energy_loss_per_miss, "晚了");
      this.checkFailure();
      return;
    }

    const expectedAt = this.startAt + nearestBar * this.barMs;
    const diff = now - expectedAt;
    const absDiff = Math.abs(diff);
    const beatKey = this.beatKey(nearestBeatIndex);
    const beatPosition = this.currentBeat || 1;

    if (this.hitBeatKeys.has(beatKey)) {
      this.emitJudgement("already_hit", "已充能");
      return;
    }

    if (absDiff <= this.sceneConfig.judgement_windows.perfect_ms) {
      this.registerHit("perfect", beatKey);
      return;
    }
    if (absDiff <= this.sceneConfig.judgement_windows.good_ms) {
      this.registerHit("good", beatKey);
      return;
    }
    if (absDiff <= this.sceneConfig.judgement_windows.late_ms) {
      if (diff > 0) this.missedBeatKeys.add(beatKey);
      this.applyPenalty(diff < 0 ? "early" : "late", Math.round(this.sceneConfig.energy_loss_per_miss * 0.7), diff < 0 ? "早了" : "晚了");
      this.flashAtBeat(beatPosition, "miss");
      this.checkFailure();
      return;
    }

    const weakBeatPress = this.currentBeat > 1;
    if (!weakBeatPress && diff > 0) this.missedBeatKeys.add(beatKey);
    this.applyPenalty(weakBeatPress ? "wrong" : diff < 0 ? "early" : "late", this.sceneConfig.energy_loss_per_miss, weakBeatPress ? "弱拍先蓄住" : diff < 0 ? "早了" : "晚了");
    this.flashAtBeat(beatPosition, "miss");
    this.checkFailure();
  }

  resetMission() {
    this.stopAudio();
    this.resetCounters();
    this.status = "ready";
    this.currentMessage = "准备";
    this.statusText.setText("准备");
    this.emitEvent("reset", "准备");
    this.renderScene();
  }

  private registerBeatTick(beatIndex: number) {
    if (beatIndex > this.totalBeats + 1) {
      this.finishMission(this.monstersRemaining <= 0, this.monstersRemaining <= 0 ? "怪物清场" : "怪物突破");
      return;
    }

    this.lastBeatIndex = beatIndex;
    if (beatIndex <= this.totalBeats) {
      const beatPosition = this.beatPosition(beatIndex);
      const strong = beatPosition === 1;
      this.playBeatSound(strong);
      this.emitEvent("beat_tick", strong ? "充能点" : "听弱拍");
    }
  }

  private registerHit(judgement: "perfect" | "good", beatKey: string) {
    this.hitBeatKeys.add(beatKey);
    this.hits += 1;
    this.combo += 1;
    this.maxCombo = Math.max(this.maxCombo, this.combo);
    this.score += this.sceneConfig.score_model[judgement];
    this.energy = Math.min(this.sceneConfig.energy_max, this.energy + (judgement === "perfect" ? 6 : 3));
    if (judgement === "perfect") this.shieldCracks = Math.max(0, this.shieldCracks - 1);
    this.flashAtBeat(1, judgement);
    this.applyShieldShockwave(judgement);
    this.playHitFx(judgement);
    this.playJudgementSound(judgement);
    this.comboBurst(this.combo, judgement);
    const cleared = this.monstersCleared;
    this.emitJudgement(judgement, judgement === "perfect" ? `完美震波 ${cleared}/${this.monsterTotal}` : `震波击退 ${cleared}/${this.monsterTotal}`);
    if (this.sceneConfig.combo_milestones.includes(this.combo) && !this.celebratedMilestones.has(this.combo)) {
      this.celebratedMilestones.add(this.combo);
      this.milestoneBurst(this.combo);
    }
    if (this.monstersRemaining <= 0) this.finishMission(true, "怪物清场");
  }

  private markOverdueDownbeats(now: number) {
    if (this.status !== "playing") return;
    const lateWindow = this.sceneConfig.judgement_windows.late_ms;
    const maxBar = Math.min(
      this.sceneConfig.mission_duration_bars - 1,
      Math.floor(Math.max(0, now - this.startAt - lateWindow) / this.barMs)
    );
    for (let bar = 0; bar <= maxBar; bar += 1) {
      const beatIndex = bar * this.beatsPerBar + 1;
      if (beatIndex < 1 || beatIndex > this.totalBeats) continue;
      const beatKey = this.beatKey(beatIndex);
      if (this.hitBeatKeys.has(beatKey) || this.missedBeatKeys.has(beatKey)) continue;
      this.missedBeatKeys.add(beatKey);
      this.misses += 1;
      this.combo = 0;
      this.shieldCracks = Math.min(MAX_SHIELD_CRACKS, this.shieldCracks + 1);
      this.score += this.sceneConfig.score_model.missed;
      this.energy = Math.max(0, this.energy - Math.round(this.sceneConfig.energy_loss_per_miss * 0.58));
      this.flashAtBeat(1, "missed");
      this.cameras.main.shake(130, 0.006);
      this.emitJudgement("missed", "强拍漏充");
      this.checkFailure();
      if (this.status !== "playing") return;
    }
  }

  private applyPenalty(judgement: "early" | "late" | "wrong", energyLoss: number, message: string) {
    this.falseAlarms += 1;
    this.combo = 0;
    this.shieldCracks = Math.min(MAX_SHIELD_CRACKS, this.shieldCracks + 1);
    this.score += this.sceneConfig.score_model.wrong;
    const easedLoss = Math.round(energyLoss * (judgement === "wrong" ? 0.62 : 0.78));
    this.energy = Math.max(0, this.energy - easedLoss);
    this.playJudgementSound(judgement);
    this.playMissFx(judgement);
    if (judgement === "wrong") this.cameras.main.shake(140, 0.007);
    this.emitJudgement(judgement, message);
  }

  private finishMission(success: boolean, message: string) {
    if (this.status === "success" || this.status === "failed") return;
    this.status = success ? "success" : "failed";
    this.stopAudio();
    this.statusText.setText(message);
    if (success) this.playStageClearFx();
    else this.playMissFx("wrong", true);
    this.emitEvent(success ? "mission_success" : "mission_failed", message);
    this.renderScene();
  }

  private checkFailure() {
    if (this.energy <= 0) this.finishMission(false, "能量空了");
    if (this.shieldCracks >= MAX_SHIELD_CRACKS) this.finishMission(false, "裂缝满格");
    if (this.lastBeatIndex > this.totalBeats && this.monstersRemaining > 0) this.finishMission(false, "怪物突破");
  }

  private emitJudgement(judgement: BeatGuardianJudgement, message: string) {
    const shortMessage = this.shortFeedback(judgement, message);
    this.lastJudgement = judgement;
    this.lastJudgementAt = this.time.now;
    this.judgementCounts[judgement] = (this.judgementCounts[judgement] || 0) + 1;
    this.statusText.setText(shortMessage);
    this.emitEvent("judgement", shortMessage, judgement);
    this.renderScene();
  }

  private emitEvent(type: BeatGuardianSceneEvent["type"], message: string, judgement?: BeatGuardianJudgement) {
    if (message) this.currentMessage = message;
    this.onSceneEvent({ type, judgement, message, snapshot: this.snapshot(message || this.currentMessage) });
  }

  private snapshot(message: string): BeatGuardianSnapshot {
    return {
      status: this.status,
      phase: this.status,
      currentBeat: this.currentBeat,
      currentBar: this.currentBar,
      beatsPerBar: this.beatsPerBar,
      missionBars: this.sceneConfig.mission_duration_bars,
      targetBeats: [1],
      hits: this.hits,
      misses: this.misses,
      falseAlarms: this.falseAlarms,
      combo: this.combo,
      maxCombo: this.maxCombo,
      requiredCombo: this.sceneConfig.required_combo,
      maxMistakes: this.sceneConfig.max_mistakes,
      score: this.score,
      energy: this.energy,
      energyMax: this.sceneConfig.energy_max,
      countInRemaining: this.countInRemaining,
      progress: this.progress,
      audioMode: this.effectiveAudioMode,
      audioLabel: this.audioLabel,
      skinObjective: this.sceneConfig.skin_objective,
      shieldCracks: this.shieldCracks,
      pulsePhase: this.pulsePhase(this.time.now),
      monstersRemaining: this.monstersRemaining,
      monstersCleared: this.monstersCleared,
      monsterTotal: this.monsterTotal,
      dangerLevel: this.dangerLevel,
      lastJudgement: this.lastJudgement,
      judgementCounts: { ...this.judgementCounts },
      message
    };
  }

  private shortFeedback(judgement: BeatGuardianJudgement, fallback: string) {
    return {
      perfect: "完美充能",
      good: "合上了",
      missed: "强拍漏充",
      wrong: fallback === "怪物撞盾" ? "怪物撞盾" : "弱拍先蓄住",
      early: "早了",
      late: "晚了",
      too_early: "等护盾收缩",
      already_hit: "已充能"
    }[judgement] || fallback.slice(0, 8);
  }

  private renderScene() {
    if (!this.graphics) return;
    const palette = palettes[this.sceneConfig.skin_play_mode];
    this.graphics.clear();
    this.drawBackground(palette);
    this.drawPulseArena(palette);
    this.drawMonsterRing(palette);
    this.drawShield(palette);
    this.drawBeatGuide(palette);
    this.drawArcadeMeters(palette);
    this.updateTemplateSprites();
    this.titleText.setText(this.sceneTitle());
    this.scoreText.setText(String(Math.max(0, this.score)));
  }

  private drawBackground(palette: (typeof palettes)[BeatGuardianPlayMode]) {
    if (!this.backgroundImage) this.cameras.main.setBackgroundColor(palette.bg);
    this.graphics.fillStyle(palette.deep, this.backgroundImage ? 0.34 : 0.72).fillRoundedRect(18, 16, WIDTH - 36, HEIGHT - 32, 34);
    this.graphics.fillStyle(0xffffff, 0.08).fillCircle(480, 258, 238);
    this.graphics.fillStyle(palette.accent, 0.16).fillCircle(132, 414, 148);
    this.graphics.fillStyle(palette.target, 0.12).fillCircle(820, 98, 132);
    this.graphics.lineStyle(2, 0xffffff, 0.13).strokeRoundedRect(36, 96, WIDTH - 72, 274, 28);
  }

  private drawPulseArena(palette: (typeof palettes)[BeatGuardianPlayMode]) {
    const phase = this.pulsePhase(this.time.now);
    const focus = 1 - phase;
    const radius = this.shieldRadius(this.time.now);
    for (let index = 0; index < 5; index += 1) {
      const ringRadius = radius + 46 + index * 38 + Math.sin(this.time.now / 360 + index) * 5;
      this.graphics.lineStyle(index === 0 ? 4 : 2, index % 2 ? palette.soft : palette.accent, 0.12 + focus * 0.12).strokeCircle(480, 262, ringRadius);
    }
    for (let beat = 0; beat < this.beatsPerBar; beat += 1) {
      const angle = -Math.PI / 2 + (beat / this.beatsPerBar) * Math.PI * 2;
      const active = this.sceneConfig.visual_beat_hint && this.status === "playing" && this.currentBeat === beat + 1;
      const x = 480 + Math.cos(angle) * 188;
      const y = 262 + Math.sin(angle) * 126;
      const target = beat === 0;
      const showStrong = !target || this.sceneConfig.show_strong_beat_hint;
      const showWeak = target || this.sceneConfig.show_weak_beat_hint;
      const idleAlpha = target ? (showStrong ? 0.72 : 0.24) : (showWeak ? 0.38 : 0.12);
      const dotRadius = target ? (showStrong ? 14 : 8) : (showWeak ? 10 : 5);
      this.graphics.fillStyle(target ? palette.target : palette.soft, active ? 0.96 : idleAlpha).fillCircle(x, y, active ? 18 : dotRadius);
      this.graphics.lineStyle(active ? 5 : 2, active ? palette.accent : 0xffffff, active ? 0.95 : showStrong || showWeak ? 0.28 : 0.08).strokeCircle(x, y, active ? 30 : target ? 22 : 16);
    }
  }

  private drawMonsterRing(palette: (typeof palettes)[BeatGuardianPlayMode]) {
    const now = this.time.now;
    const shock = Math.max(0, (this.shockwaveUntil - now) / 460);
    this.monsterStates.forEach((monster, index) => {
      if (monster.cleared && now - monster.clearAt > 620) {
        this.monsterImages[index]?.setVisible(false);
        return;
      }
      const clearFade = monster.cleared ? Math.max(0, 1 - (now - monster.clearAt) / 620) : 1;
      const danger = monster.distance <= MONSTER_WARNING_DISTANCE && !monster.cleared;
      const wobble = Math.sin(now / monster.wobbleMs + monster.phase) * (danger ? 10 : 6);
      const distance = monster.distance + wobble + shock * 28;
      const x = ARENA_CENTER_X + Math.cos(monster.angle) * distance;
      const y = ARENA_CENTER_Y + Math.sin(monster.angle) * distance * 0.66;
      const proximity = 1 - Math.max(0, Math.min(1, (monster.distance - MONSTER_BREACH_DISTANCE) / 180));
      const scale = (0.74 + proximity * 0.24 + (danger ? Math.sin(now / 100 + index) * 0.035 : 0)) * clearFade;
      const alpha = this.status === "success" ? 0.08 : (monster.cleared ? 0.52 * clearFade : 0.74 + proximity * 0.2);
      const image = this.monsterImages[index];
      this.graphics.lineStyle(5, 0xfff0bd, (0.28 + proximity * 0.3) * clearFade).strokeCircle(x, y, 23 * scale);
      this.graphics.lineStyle(2, 0x24385f, (0.48 + proximity * 0.24) * clearFade).strokeCircle(x, y, 18 * scale);
      if (danger) {
        this.graphics.lineStyle(4, palette.danger, 0.46 + Math.sin(now / 100) * 0.12).strokeCircle(x, y, 28 + proximity * 13);
      }
      if (image) {
        this.sizeMonsterImage(image, MONSTER_BASE_DISPLAY_SIZE * scale);
        image.setVisible(true).setPosition(x, y).setAngle(Math.sin(now / 220 + index) * (danger ? 10 : 5)).setAlpha(alpha);
      } else {
        this.graphics.fillStyle(monster.cleared ? palette.target : danger ? palette.danger : 0x7fb7e8, alpha * 0.72).fillCircle(x, y, 12 * scale);
        this.graphics.fillStyle(0xffffff, alpha * 0.82).fillCircle(x - 3.6 * scale, y - 2.8 * scale, 2 * scale).fillCircle(x + 3.6 * scale, y - 2.8 * scale, 2 * scale);
      }
      if (monster.hitFlashUntil > now) {
        const flash = (monster.hitFlashUntil - now) / 260;
        this.graphics.lineStyle(4, palette.target, flash).strokeCircle(x, y, 34 + (1 - flash) * 34);
      }
    });
  }

  private sizeMonsterImage(image: Phaser.GameObjects.Image, maxDisplaySize: number) {
    const frame = image.texture.getSourceImage() as HTMLImageElement | HTMLCanvasElement | undefined;
    const sourceWidth = Number(frame?.width || image.width || MONSTER_BASE_DISPLAY_SIZE);
    const sourceHeight = Number(frame?.height || image.height || MONSTER_BASE_DISPLAY_SIZE);
    if (sourceWidth >= sourceHeight) {
      image.setDisplaySize(maxDisplaySize, maxDisplaySize * (sourceHeight / sourceWidth));
    } else {
      image.setDisplaySize(maxDisplaySize * (sourceWidth / sourceHeight), maxDisplaySize);
    }
  }

  private createWeakBeatCueTexture() {
    if (this.textures.exists(WEAK_BEAT_CUE_KEY)) return;
    const cue = this.make.graphics({ x: 0, y: 0 }, false);
    cue.fillStyle(0xfff0bd, 0.28).fillCircle(32, 34, 30);
    cue.fillStyle(0x6ea8ff, 0.96).fillRoundedRect(12, 14, 40, 40, 16);
    cue.fillStyle(0x4658ba, 0.92).fillRoundedRect(18, 10, 28, 18, 9);
    cue.fillStyle(0xeaf7ff, 0.98).fillCircle(24, 30, 5.8).fillCircle(40, 30, 5.8);
    cue.fillStyle(0x1e2859, 0.88).fillCircle(24, 31, 2.1).fillCircle(40, 31, 2.1);
    cue.lineStyle(5, 0xfff0bd, 0.9).strokeRoundedRect(10, 12, 44, 44, 17);
    cue.lineStyle(3, 0xffffff, 0.55).beginPath().arc(32, 36, 14, 0.2, Math.PI - 0.2).strokePath();
    cue.lineStyle(4, 0xffd36d, 0.78).lineBetween(46, 17, 46, 39).lineBetween(46, 17, 54, 17);
    cue.fillStyle(0xffd36d, 0.9).fillCircle(43, 40, 4);
    cue.generateTexture(WEAK_BEAT_CUE_KEY, 64, 64);
    cue.destroy();
  }

  private drawShield(palette: (typeof palettes)[BeatGuardianPlayMode]) {
    const now = this.time.now;
    const phase = this.pulsePhase(now);
    const focus = 1 - phase;
    const radius = this.shieldRadius(now);
    const alpha = 0.26 + focus * 0.3;
    this.graphics.fillStyle(palette.target, alpha).fillCircle(480, 262, radius);
    this.graphics.lineStyle(8 + focus * 8, palette.target, 0.68 + focus * 0.28).strokeCircle(480, 262, radius);
    this.graphics.lineStyle(3, 0xffffff, 0.54 + focus * 0.28).strokeCircle(480, 262, radius - 18);
    this.graphics.fillStyle(0xffffff, 0.08 + focus * 0.16).fillCircle(480, 262, 28 + focus * 7);
    if (this.focusProp) {
      this.focusProp.setDisplaySize(radius * 1.25, radius * 1.25).setAlpha(0.16 + focus * 0.22).setAngle(now / 80);
    }
    const shock = Math.max(0, (this.shockwaveUntil - now) / 460);
    if (shock > 0) {
      this.graphics.lineStyle(8 * shock, palette.target, 0.85 * shock).strokeCircle(480, 262, radius + (1 - shock) * 196);
      this.graphics.lineStyle(3, 0xffffff, 0.72 * shock).strokeCircle(480, 262, radius + (1 - shock) * 260);
    }
    for (let index = 0; index < this.shieldCracks; index += 1) {
      const angle = -Math.PI / 2 + (index / Math.max(1, this.shieldCracks)) * Math.PI * 1.6 + 0.2;
      const sx = 480 + Math.cos(angle) * (radius - 22);
      const sy = 262 + Math.sin(angle) * (radius - 22);
      const ex = 480 + Math.cos(angle + 0.22) * (radius + 10);
      const ey = 262 + Math.sin(angle + 0.22) * (radius + 10);
      this.graphics.lineStyle(4, palette.danger, 0.72).lineBetween(sx, sy, ex, ey);
      this.graphics.lineStyle(1, 0xffffff, 0.5).lineBetween(sx + 4, sy - 3, ex - 5, ey + 3);
    }
  }

  private drawBeatGuide(palette: (typeof palettes)[BeatGuardianPlayMode]) {
    if (!this.sceneConfig.show_beat_track) {
      this.beatLabels.forEach((label) => label.setVisible(false));
      return;
    }
    const left = 236;
    const spacing = 488 / Math.max(1, this.beatsPerBar - 1);
    for (let beat = 1; beat <= this.beatsPerBar; beat += 1) {
      const x = left + (beat - 1) * spacing;
      const target = beat === 1;
      const active = this.sceneConfig.visual_beat_hint && this.status === "playing" && this.currentBeat === beat;
      const showStrong = !target || this.sceneConfig.show_strong_beat_hint;
      const showWeak = target || this.sceneConfig.show_weak_beat_hint;
      const alpha = target ? (showStrong ? 0.94 : 0.38) : (showWeak ? 0.56 : 0.18);
      this.graphics.fillStyle(target ? palette.target : 0xffffff, alpha).fillRoundedRect(x - 38, 405, 76, 48, 20);
      this.graphics.lineStyle(active ? 6 : 2, active ? palette.accent : palette.soft, active ? 1 : showStrong || showWeak ? 0.58 : 0.16).strokeRoundedRect(x - 38, 405, 76, 48, 20);
      if (target && this.sceneConfig.show_strong_beat_hint) this.graphics.lineStyle(3, palette.accent, 0.7).strokeCircle(x, 429, 31);
      this.beatLabels[beat - 1]?.setVisible(showStrong || showWeak).setPosition(x, 429);
      this.beatLabels[beat - 1]?.setColor(target ? "#6a351b" : "#173028");
    }
  }

  private drawArcadeMeters(palette: (typeof palettes)[BeatGuardianPlayMode]) {
    this.graphics.fillStyle(0xffffff, 0.2).fillRoundedRect(34, 478, 316, 18, 9);
    this.graphics.fillStyle(this.energy <= this.sceneConfig.energy_max * 0.28 ? palette.danger : palette.accent, 0.96)
      .fillRoundedRect(34, 478, Math.max(8, 316 * (this.energy / this.sceneConfig.energy_max)), 18, 9);
    this.graphics.fillStyle(0xffffff, 0.2).fillRoundedRect(610, 478, 316, 18, 9);
    this.graphics.fillStyle(palette.target, 0.95).fillRoundedRect(610, 478, Math.max(8, 316 * this.progress), 18, 9);
    this.graphics.fillStyle(0xffffff, 0.92).fillRoundedRect(414, 466, 132, 42, 18);
    this.graphics.fillStyle(this.shieldCracks ? palette.danger : palette.deep, 1).fillCircle(436, 487, 10 + Math.min(this.combo, 8));
    this.graphics.lineStyle(3, palette.accent, 0.8).strokeCircle(436, 487, 18 + Math.max(0, 4 - this.shieldCracks));
  }

  private updateMonsterPressure(now: number, delta: number) {
    if (this.status !== "playing" || now < this.startAt || now < this.hitStopUntil) return;
    const dt = Math.min(0.05, Math.max(0, delta / 1000));
    this.monsterStates.forEach((monster) => {
      if (monster.cleared) return;
      if (monster.impulse > 0) {
        monster.distance = Math.min(monster.spawnDistance + 88, monster.distance + monster.impulse * dt);
        monster.impulse = Math.max(0, monster.impulse - 640 * dt);
        return;
      }
      if (now < monster.stunUntil) return;
      const dangerBoost = monster.distance < MONSTER_WARNING_DISTANCE ? 1.22 : 1;
      const beatSurge = this.currentBeat > 1 ? 1.04 : 0.76;
      monster.distance = Math.max(MONSTER_BREACH_DISTANCE - 8, monster.distance - monster.speed * dangerBoost * beatSurge * dt);
      if (monster.distance <= MONSTER_BREACH_DISTANCE && now > monster.breachCooldownUntil) {
        this.registerMonsterBreach(monster, now);
      }
    });
  }

  private registerMonsterBreach(monster: MonsterState, now: number) {
    monster.distance = MONSTER_WARNING_DISTANCE + 28;
    monster.impulse = 210;
    monster.stunUntil = now + 620;
    monster.breachCooldownUntil = now + 1700;
    monster.hitFlashUntil = now + 420;
    if (now - this.lastMonsterBreachAt < 320) return;
    this.lastMonsterBreachAt = now;
    this.combo = 0;
    this.shieldCracks = Math.min(MAX_SHIELD_CRACKS, this.shieldCracks + 1);
    this.energy = Math.max(0, this.energy - Math.round(this.sceneConfig.energy_loss_per_miss * 0.3));
    this.score += Math.round(this.sceneConfig.score_model.wrong * 0.45);
    this.playMissFx("wrong");
    this.emitJudgement("wrong", "怪物撞盾");
    this.checkFailure();
  }

  private applyShieldShockwave(judgement: "perfect" | "good") {
    const now = this.time.now;
    const clearCount = 1;
    const active = this.monsterStates
      .filter((monster) => !monster.cleared)
      .sort((a, b) => a.distance - b.distance);
    active.forEach((monster, index) => {
      monster.distance = Math.min(monster.spawnDistance + 96, monster.distance + (judgement === "perfect" ? 136 : 96) + index * 12);
      monster.impulse = judgement === "perfect" ? 430 : 310;
      monster.stunUntil = now + (judgement === "perfect" ? 1040 : 720);
      monster.hitFlashUntil = now + 500;
    });
    active.slice(0, clearCount).forEach((monster) => {
      monster.cleared = true;
      monster.clearAt = now;
      monster.distance = Math.min(monster.spawnDistance + 132, monster.distance + 166);
      monster.impulse = 500;
      monster.hitFlashUntil = now + 620;
    });
    this.hitStopUntil = now + (judgement === "perfect" && !prefersReducedMotion() ? 90 : 36);
  }

  private updateTemplateSprites() {
    const freshJudgement = this.time.now - this.lastJudgementAt < 520;
    const pose = this.status === "success"
      ? "win"
      : this.status === "failed"
        ? "miss"
        : freshJudgement && (this.lastJudgement === "perfect" || this.lastJudgement === "good")
          ? "action"
          : freshJudgement && (this.lastJudgement === "early" || this.lastJudgement === "late" || this.lastJudgement === "wrong" || this.lastJudgement === "missed")
            ? "miss"
            : "idle";
    this.heroPresenter?.transitionTo(pose, this.status === "success" ? "success" : this.status === "failed" ? "miss" : pose === "action" ? "hit" : "idle");
    if (this.rewardImage) {
      this.rewardImage.setVisible(this.status === "success" || this.combo >= Math.min(2, this.sceneConfig.required_combo));
      this.rewardImage.setScale(this.status === "success" ? 1.18 : 0.92 + this.combo * 0.03);
      this.rewardImage.setAngle(this.status === "playing" ? Math.sin(this.time.now / 260) * 4 : 0);
    }
  }

  private createMonsterStates(): MonsterState[] {
    return this.monsterSeeds.map((seed) => ({
      ...seed,
      distance: seed.spawnDistance,
      impulse: 0,
      cleared: false,
      clearAt: 0,
      stunUntil: 0,
      breachCooldownUntil: 0,
      hitFlashUntil: 0
    }));
  }

  private startAudio() {
    this.ensureAudioContext();
    if (this.effectiveAudioMode === "lesson_audio") this.startLessonAudio();
  }

  private stopAudio() {
    if (this.lessonAudio) {
      this.lessonAudio.pause();
      this.lessonAudio.currentTime = 0;
    }
  }

  private ensureAudioContext() {
    playHybridToneSequence([], { instrument: "xylophone", duration: 0.01, gain: 0.01 });
  }

  private startLessonAudio() {
    const audioUrl = this.sceneConfig.lesson_audio_sync?.audio_url;
    if (!audioUrl) return;
    if (!this.lessonAudio) {
      this.lessonAudio = new Audio(audioUrl);
      this.lessonAudio.preload = "auto";
    }
    const offsetSeconds = Math.max(0, Number(this.sceneConfig.lesson_audio_sync.offset_ms || 0) / 1000);
    this.lessonAudio.currentTime = offsetSeconds;
    void this.lessonAudio.play().catch(() => {
      this.lessonAudioFailed = true;
      this.playBeatSound(true);
    });
  }

  private playBeatSound(strong: boolean) {
    if (this.effectiveAudioMode === "lesson_audio") return;
    this.ensureAudioContext();
    const fallback = strong
      ? { wave: "sine" as OscillatorType, frequency: 196, duration_ms: 120, gain: 0.28 }
      : { wave: "triangle" as OscillatorType, frequency: 392, duration_ms: 72, gain: 0.12 };
    const profile = (strong ? this.sceneConfig.beat_sound_profile.strong : this.sceneConfig.beat_sound_profile.weak) || fallback;
    this.playTone(profile.wave || fallback.wave, Number(profile.frequency || fallback.frequency), Number(profile.duration_ms || fallback.duration_ms), Number(profile.gain || fallback.gain));
  }

  private playJudgementSound(judgement: BeatGuardianJudgement) {
    this.ensureAudioContext();
    if (this.effectiveAudioMode === "lesson_audio") return;
    const tones: Record<string, [OscillatorType, number, number, number]> = {
      perfect: ["triangle", 720, 110, 0.16],
      good: ["sine", 540, 82, 0.1],
      early: ["sawtooth", 180, 70, 0.08],
      late: ["sawtooth", 150, 70, 0.08],
      wrong: ["square", 120, 90, 0.07],
      missed: ["square", 100, 110, 0.07]
    };
    const tone = tones[judgement];
    if (tone) this.playTone(...tone);
  }

  private playTone(wave: OscillatorType, frequency: number, durationMs: number, gainValue: number) {
    const midi = Math.max(24, Math.min(96, Math.round(69 + 12 * Math.log2(frequency / 440))));
    playHybridToneSequence([midi - 60], {
      instrument: "xylophone",
      duration: Math.max(0.06, durationMs / 1000),
      gap: Math.max(0.08, durationMs / 1000 + 0.04),
      gain: Math.max(0.1, Math.min(1, gainValue * 3)),
      oscillatorWave: wave
    });
  }

  private flashAtBeat(beat: number, judgement: "perfect" | "good" | "miss" | "missed") {
    const x = this.beatGuideX(beat);
    const color = judgement === "perfect" ? 0xfff2bd : judgement === "good" ? 0x8ff0c2 : 0xe4573d;
    const ring = this.add.circle(x, 429, 22, color, 0.55).setDepth(10);
    this.tweens.add({
      targets: ring,
      scale: judgement === "perfect" ? 2.8 : 2.1,
      alpha: 0,
      duration: 380,
      ease: "Cubic.Out",
      onComplete: () => ring.destroy()
    });
  }

  private playHitFx(judgement: "perfect" | "good") {
    const palette = palettes[this.sceneConfig.skin_play_mode];
    const color = judgement === "perfect" ? palette.target : 0x8ff0c2;
    this.shockwaveUntil = this.time.now + (judgement === "perfect" ? 540 : 360);
    this.cameras.main.pan(480, 262, 42, "Sine.easeOut", true);
    const spark = this.add.star(480, 196, 7, 10, 34, color, 0.95).setDepth(12);
    this.tweens.add({ targets: spark, y: 154, angle: 160, scale: 1.35, alpha: 0, duration: 430, ease: "Back.Out", onComplete: () => spark.destroy() });
    this.heroPresenter?.pulse("hit");
    const clearedLabel = this.add.text(480, 322, judgement === "perfect" ? "-2" : "-1", {
      color: "#fff8dd",
      fontFamily: "Noto Sans SC, PingFang SC, sans-serif",
      fontSize: "34px",
      fontStyle: "bold"
    }).setOrigin(0.5).setDepth(12);
    this.tweens.add({ targets: clearedLabel, y: 284, alpha: 0, duration: 520, ease: "Cubic.Out", onComplete: () => clearedLabel.destroy() });
  }

  private playMissFx(_judgement: "early" | "late" | "wrong", final = false) {
    const crack = this.add.text(480, 196, final ? "护盾失稳" : "裂缝", {
      color: "#ffdfb8",
      fontFamily: "Noto Sans SC, PingFang SC, sans-serif",
      fontSize: final ? "36px" : "28px",
      fontStyle: "bold"
    }).setOrigin(0.5).setDepth(12);
    this.cameras.main.shake(final ? 220 : 120, final ? 0.011 : 0.006);
    this.tweens.add({ targets: crack, y: 156, alpha: 0, duration: 480, ease: "Cubic.Out", onComplete: () => crack.destroy() });
    this.heroPresenter?.pulse("miss");
  }

  private playStageClearFx() {
    this.successBurst();
    this.cameras.main.flash(420, 255, 240, 184);
    const label = this.add.text(480, 178, "护盾稳定", {
      color: "#fff2bd",
      fontFamily: "Noto Sans SC, PingFang SC, sans-serif",
      fontSize: "48px",
      fontStyle: "bold"
    }).setOrigin(0.5).setDepth(12);
    this.tweens.add({ targets: label, scale: 1.18, alpha: 0, duration: 760, ease: "Back.Out", onComplete: () => label.destroy() });
  }

  private comboBurst(combo: number, judgement: "perfect" | "good") {
    const label = this.add.text(480, 118, judgement === "perfect" ? "同时按下" : `${combo} 次充能`, {
      color: judgement === "perfect" ? "#fff2bd" : "#c9ffe3",
      fontFamily: "Noto Sans SC, PingFang SC, sans-serif",
      fontSize: judgement === "perfect" ? "38px" : "30px",
      fontStyle: "bold"
    }).setOrigin(0.5).setDepth(12);
    this.tweens.add({
      targets: label,
      y: 86,
      alpha: 0,
      duration: 520,
      ease: "Cubic.Out",
      onComplete: () => label.destroy()
    });
  }

  private milestoneBurst(combo: number) {
    const label = this.add.text(480, 256, `${combo} 次稳定`, {
      color: "#fff8dd",
      fontFamily: "Noto Sans SC, PingFang SC, sans-serif",
      fontSize: "42px",
      fontStyle: "bold"
    }).setOrigin(0.5).setDepth(12);
    this.tweens.add({
      targets: label,
      scale: 1.35,
      alpha: 0,
      duration: 700,
      ease: "Back.Out",
      onComplete: () => label.destroy()
    });
  }

  private successBurst() {
    const palette = palettes[this.sceneConfig.skin_play_mode];
    for (let index = 0; index < 18; index += 1) {
      const dot = this.add.circle(480, 262, 8, index % 2 ? palette.target : palette.accent, 0.95).setDepth(12);
      this.tweens.add({
        targets: dot,
        x: 480 + Math.cos((index / 18) * Math.PI * 2) * 300,
        y: 262 + Math.sin((index / 18) * Math.PI * 2) * 172,
        alpha: 0,
        duration: 760,
        ease: "Cubic.Out",
        onComplete: () => dot.destroy()
      });
    }
  }

  private pulseCountdown(value: number) {
    if (!value) return;
    const text = this.add.text(480, 246, String(value), {
      color: "#fff8dd",
      fontFamily: "Noto Sans SC, PingFang SC, sans-serif",
      fontSize: "92px",
      fontStyle: "bold"
    }).setOrigin(0.5).setDepth(12);
    this.tweens.add({
      targets: text,
      scale: 1.3,
      alpha: 0,
      duration: 520,
      ease: "Cubic.Out",
      onComplete: () => text.destroy()
    });
  }

  private resetCounters() {
    this.lastBeatIndex = 0;
    this.hits = 0;
    this.misses = 0;
    this.falseAlarms = 0;
    this.combo = 0;
    this.maxCombo = 0;
    this.score = 0;
    this.energy = this.sceneConfig.energy_max;
    this.shieldCracks = 0;
    this.countInRemaining = 0;
    this.lastJudgement = undefined;
    this.lastJudgementAt = 0;
    this.shockwaveUntil = 0;
    this.lastMonsterBreachAt = 0;
    this.hitStopUntil = 0;
    this.monsterStates = this.createMonsterStates();
    this.hitBeatKeys = new Set();
    this.missedBeatKeys = new Set();
    this.celebratedMilestones = new Set();
    this.judgementCounts = {};
  }

  private sceneTitle() {
    return "充能护盾";
  }

  private beatKey(beatIndex: number) {
    return `${Math.floor((beatIndex - 1) / this.beatsPerBar) + 1}:downbeat`;
  }

  private beatPosition(beatIndex: number) {
    return ((beatIndex - 1) % this.beatsPerBar) + 1;
  }

  private nearestChargeBar(now: number) {
    const elapsed = now - this.startAt;
    const centerBar = Math.max(0, Math.floor(elapsed / this.barMs));
    const candidates = [centerBar - 1, centerBar, centerBar + 1]
      .filter((bar) => bar >= 0 && bar * this.beatsPerBar + 1 <= this.totalBeats)
      .map((bar) => ({ bar, distance: Math.abs(now - (this.startAt + bar * this.barMs)) }))
      .sort((left, right) => left.distance - right.distance);
    return candidates[0]?.bar ?? centerBar;
  }

  private beatGuideX(beat: number) {
    const usable = 488;
    return 236 + ((beat - 1) * usable) / Math.max(1, this.beatsPerBar - 1);
  }

  private shieldRadius(now: number) {
    const phase = this.pulsePhase(now);
    return 92 + easeInOutSine(phase) * 48;
  }

  private pulsePhase(now: number) {
    if (this.status !== "playing" && this.status !== "success" && this.status !== "failed") return 0.72;
    const bar = this.barProgress(now);
    return Math.abs(((bar + 0.5) % 1) - 0.5) * 2;
  }

  private barProgress(now: number) {
    if (this.status !== "playing" || now < this.startAt) return 0;
    return positiveModulo((now - this.startAt) / this.barMs, 1);
  }

  private get beatMs() {
    return 60000 / this.sceneConfig.bpm;
  }

  private get barMs() {
    return this.beatMs * this.beatsPerBar;
  }

  private get beatsPerBar() {
    return this.sceneConfig.beats_per_bar;
  }

  private get totalBeats() {
    return this.sceneConfig.round_length_beats;
  }

  private get currentBeat() {
    if (this.lastBeatIndex < 1) return 0;
    return this.beatPosition(Math.min(this.lastBeatIndex, this.totalBeats));
  }

  private get currentBar() {
    if (this.lastBeatIndex < 1) return 0;
    return Math.min(this.sceneConfig.mission_duration_bars, Math.floor((Math.min(this.lastBeatIndex, this.totalBeats) - 1) / this.beatsPerBar) + 1);
  }

  private get progress() {
    if (this.status === "ready") return 0;
    if (this.status === "success") return 1;
    return Math.max(0, Math.min(1, this.monstersCleared / Math.max(1, this.monsterTotal)));
  }

  private get monsterTotal() {
    return this.monsterSeeds.length;
  }

  private get monstersCleared() {
    return this.monsterStates.filter((monster) => monster.cleared).length;
  }

  private get monstersRemaining() {
    return Math.max(0, this.monsterTotal - this.monstersCleared);
  }

  private get dangerLevel() {
    const active = this.monsterStates.filter((monster) => !monster.cleared);
    if (!active.length) return 0;
    const nearest = Math.min(...active.map((monster) => monster.distance));
    return Math.max(0, Math.min(1, 1 - (nearest - MONSTER_BREACH_DISTANCE) / (MONSTER_WARNING_DISTANCE - MONSTER_BREACH_DISTANCE + 72)));
  }

  private get effectiveAudioMode(): BeatGuardianAudioMode {
    if (this.lessonAudioFailed) return "internal_meter";
    if (this.sceneConfig.audio_mode === "lesson_audio" && this.sceneConfig.lesson_audio_sync?.audio_url) return "lesson_audio";
    if (this.sceneConfig.audio_mode === "hybrid" && this.sceneConfig.lesson_audio_sync?.audio_url) return "lesson_audio";
    return "internal_meter";
  }

  private get audioLabel() {
    if (this.effectiveAudioMode === "lesson_audio") return this.sceneConfig.lesson_audio_sync?.segment_label || "作品片段";
    return "强弱拍鼓点";
  }
}

function createMonsterSeeds(): MonsterSeed[] {
  return [-0.84, -0.5, -0.18, 0.18, 0.5, 0.84].slice(0, BEAT_GUARDIAN_MONSTER_TOTAL).map((turn, index) => ({
    angle: -Math.PI / 2 + turn * Math.PI,
    spawnDistance: 312 + (index % 2) * 28,
    speed: 18 + index * 1.35,
    wobbleMs: 760 + index * 70,
    phase: index * 1.73
  }));
}

function easeInOutSine(value: number) {
  return -(Math.cos(Math.PI * Math.max(0, Math.min(1, value))) - 1) / 2;
}

function positiveModulo(value: number, divisor: number) {
  return ((value % divisor) + divisor) % divisor;
}

function normalizePlayMode(value: unknown, skinId: string): BeatGuardianPlayMode {
  if (value === "race" || value === "gate" || value === "station" || value === "spotlight" || value === "orbit") return value;
  return (
    {
      dragon_boat: "race",
      castle_gate: "gate",
      train_conductor: "station",
      stage_light: "spotlight",
      space_orbit: "orbit"
    }[skinId] || "gate"
  ) as BeatGuardianPlayMode;
}

function normalizeAudioMode(value: unknown): BeatGuardianAudioMode {
  if (value === "internal_meter" || value === "lesson_audio" || value === "hybrid") return value;
  return "hybrid";
}

function normalizeTargetBeats(value: unknown, beatsPerBar: number) {
  if (!Array.isArray(value)) return [1];
  const seen = new Set<number>();
  const beats = value
    .map(Number)
    .filter((beat) => Number.isFinite(beat))
    .map((beat) => Math.round(beat))
    .filter((beat) => beat >= 1 && beat <= beatsPerBar)
    .filter((beat) => {
      if (seen.has(beat)) return false;
      seen.add(beat);
      return true;
    });
  return beats.length ? beats : [1];
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

function normalizeComboMilestones(value: unknown, requiredCombo: number) {
  const raw = Array.isArray(value) ? value : [4, 8, 12];
  const milestones = raw.map(Number).filter((item) => Number.isFinite(item) && item > 0).map((item) => clampNumber(item, 1, 24, 4));
  const required = clampNumber(requiredCombo, 1, 24, 4);
  if (!milestones.includes(required)) milestones.push(required);
  return Array.from(new Set(milestones)).sort((a, b) => a - b);
}

function normalizeJudgementWindows(value: unknown, fallbackTolerance: number): JudgementWindows {
  const raw = isRecord(value) ? value : {};
  const perfect = Math.max(95, clampNumber(Number(raw.perfect_ms), 35, 140, 95));
  const good = Math.max(210, clampNumber(Number(raw.good_ms), perfect, 260, Math.max(perfect, Math.min(fallbackTolerance, 210))));
  const late = Math.max(320, clampNumber(Number(raw.late_ms), good, 420, Math.max(good, 320)));
  return { perfect_ms: perfect, good_ms: good, late_ms: late };
}

function normalizeInputMap(value: unknown) {
  const raw = isRecord(value) ? value : {};
  return { primary: String(raw.primary || "Space"), pointer: raw.pointer !== false };
}

function normalizeFxProfile(value: unknown) {
  const raw = isRecord(value) ? value : {};
  return {
    hit: String(raw.hit || "burst"),
    miss: String(raw.miss || "shake"),
    success: String(raw.success || "skin_objective_finish")
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

function normalizeBeatSoundProfile(value: unknown): { strong: BeatSoundProfile; weak: BeatSoundProfile } {
  const fallback = {
    strong: { wave: "sine" as OscillatorType, frequency: 196, duration_ms: 110, gain: 0.28 },
    weak: { wave: "triangle" as OscillatorType, frequency: 392, duration_ms: 72, gain: 0.12 }
  };
  if (!isRecord(value)) return fallback;
  return {
    strong: normalizeBeatSound(value.strong, fallback.strong),
    weak: normalizeBeatSound(value.weak, fallback.weak)
  };
}

function normalizeBeatSound(value: unknown, fallback: BeatSoundProfile): BeatSoundProfile {
  if (!isRecord(value)) return fallback;
  const wave = value.wave === "sine" || value.wave === "square" || value.wave === "sawtooth" || value.wave === "triangle" ? value.wave : fallback.wave;
  return {
    wave,
    frequency: clampNumber(Number(value.frequency), 80, 1200, Number(fallback.frequency)),
    duration_ms: clampNumber(Number(value.duration_ms), 35, 260, Number(fallback.duration_ms)),
    gain: clampFloat(Number(value.gain), 0.03, 0.5, Number(fallback.gain))
  };
}

function skinObjectiveForSkin(skinId: string) {
  return {
    dragon_boat: "跟鼓点预判强拍",
    castle_gate: "维持护盾",
    train_conductor: "准点充能",
    stage_light: "强拍点亮",
    space_orbit: "轨道同步"
  }[skinId] || "维持护盾";
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
