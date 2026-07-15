import Phaser from "phaser";
import { resolvePitchToken } from "../shared/pitchCatalog";
import { GameAudioManager, type GameAudioAssetConfig } from "./audio";
import {
  buildPitchLadderLevelSteps,
  buildPitchLadderNativeRoutePoints,
  routePointToCanvas,
  PITCH_LADDER_SKIN_MANIFESTS,
  usesNativePitchLadderMapRoute,
  type PitchLadderAnimationKey,
  type PitchLadderContentManifest,
  type PitchLadderLevelStep,
  type RoutePoint
} from "./pitchLadderContent";
import { PitchLadderGameSystem, isPitchDirection, pitchDirectionLabel, type PitchDirection } from "./pitchLadderSystem";

export type PitchLadderPlayMode = "mountain" | "cloud" | "bamboo" | "lantern";
export type PitchLadderStatus = "ready" | "listening" | "playing" | "round_clear" | "mission_success" | "mission_failed";
export type PitchLadderJudgement = "correct" | "wrong" | "partial" | "sing_back";
export type PitchLadderMode = "direction_pair" | "single_solfege" | "melody_path";
export type PitchLadderAudioMode = "internal_pitch" | "lesson_audio" | "hybrid";

type CharacterProfile = {
  role: string;
  idle_animation: string;
  success_animation: string;
  fail_animation: string;
};

type RewardModel = {
  token_name: string;
  tokens_required: number;
  final_reward_animation: string;
};

type FailPressureModel = {
  energy_loss_animation: string;
  route_damage_animation: string;
  quick_retry: boolean;
};

type CopyBudget = {
  objective_max_chars: number;
  feedback_max_chars: number;
};

type PitchRouteNode = {
  id: string;
  note: string;
  label: string;
  midi_offset: number;
  level: number;
  height: number;
};

type PitchRound = {
  id?: string;
  sequence?: string[];
  labels?: string[];
  midi_offsets?: number[];
  answer?: string | string[];
};

type PitchMusicElements = {
  tonic?: string;
  scale_type?: string;
  pitch_range?: string[];
  notes_per_round?: number;
  round_count?: number;
  direction_mix?: Record<string, number>;
  step_skip_mix?: Record<string, number>;
  show_solfege_hint?: boolean;
  audio_mode?: PitchLadderAudioMode;
  sing_back_required?: boolean;
};

type FxProfile = {
  step: string;
  miss: string;
  success: string;
};

type DirectionChoice = PitchDirection;
export type PitchLadderVoiceDirection = DirectionChoice;

type PlatformPoint = {
  x: number;
  y: number;
  width: number;
  label: string;
  direction?: DirectionChoice;
  active?: boolean;
  correct?: boolean;
};

const DEBUG_NATIVE_ROUTE_POINTS = false;

export type PitchLadderSceneConfig = {
  engine?: "phaser_2d";
  scene_id?: "pitch_ladder_scene";
  runtime_shell?: "pitch_ladder_map_shell";
  game_feel?: "map_pitch_climb";
  skin_id?: string;
  skin_play_mode?: PitchLadderPlayMode;
  mode?: string;
  current_mode?: PitchLadderMode;
  target_pattern_type?: string;
  music_elements?: PitchMusicElements;
  pitch_range?: string[];
  pitch_rounds?: PitchRound[];
  route_nodes?: PitchRouteNode[];
  pitch_path?: Array<Record<string, unknown>>;
  energy_max?: number;
  mistake_limit?: number;
  sing_back_required?: boolean;
  audio_mode?: PitchLadderAudioMode;
  audio_assets?: GameAudioAssetConfig;
  input_map?: { primary?: string; pointer?: boolean };
  fx_profile?: Partial<FxProfile>;
  map_hud?: boolean;
  adventure_hud?: boolean;
  show_mission_ribbon_in_play?: boolean;
  route_objective?: "summit" | "cloud_gate" | "bamboo_crown" | "lantern_beacon";
  copy_budget?: { objective_max_chars?: number; feedback_max_chars?: number };
  character_profile?: Partial<CharacterProfile>;
  reward_model?: Partial<RewardModel>;
  fail_pressure_model?: Partial<FailPressureModel>;
  show_teacher_text_in_play?: boolean;
  content_manifest?: Partial<PitchLadderContentManifest>;
  route_style?: "floating_platforms" | "map_native";
  movement_profile?: "jump_arc" | "walk_arc";
  hint_density?: "low" | "medium";
};

type NormalizedPitchLadderSceneConfig = Omit<
  Required<PitchLadderSceneConfig>,
  "copy_budget" | "character_profile" | "reward_model" | "fail_pressure_model" | "fx_profile" | "content_manifest"
> & {
  copy_budget: CopyBudget;
  character_profile: CharacterProfile;
  reward_model: RewardModel;
  fail_pressure_model: FailPressureModel;
  fx_profile: FxProfile;
  content_manifest?: Partial<PitchLadderContentManifest>;
};

export type PitchLadderSnapshot = {
  status: PitchLadderStatus;
  currentRound: number;
  totalRounds: number;
  currentMode: PitchLadderMode;
  sequence: string[];
  labels: string[];
  answer: string | string[];
  selected: string[];
  progress: number;
  cleared: number;
  rewardsCollected: number;
  rewardTotal: number;
  rewardTokenName: string;
  mistakes: number;
  mistakeLimit: number;
  energy: number;
  energyMax: number;
  skinObjective: string;
  audioMode: PitchLadderAudioMode;
  audioLabel: string;
  lastJudgement?: PitchLadderJudgement;
  message: string;
};

export type PitchLadderSceneEvent = {
  type:
    | "listen"
    | "choose_direction"
    | "preview_direction"
    | "voice_start"
    | "voice_result"
    | "voice_retry"
    | "choose_node"
    | "route_step"
    | "judgement"
    | "round_success"
    | "mission_success"
    | "mission_failed"
    | "reset";
  judgement?: PitchLadderJudgement;
  message?: string;
  snapshot: PitchLadderSnapshot;
};

export type PitchLadderController = {
  listen: () => void;
  previewDirection: (direction: string) => void;
  startVoiceCharge: () => void;
  updateVoiceMeter: (level: number, trace?: number[]) => void;
  resolveVoiceAttempt: (choice: string, voiceDirection: string) => void;
  voiceRetry: (message: string) => void;
  chooseDirection: (direction: string) => void;
  chooseNode: (note: string) => void;
  confirmSingBack: () => void;
  reset: () => void;
  destroy: () => void;
};

const WIDTH = 960;
const HEIGHT = 540;

const palettes: Record<PitchLadderPlayMode, { bg: number; land: number; route: number; accent: number; target: number; danger: number }> = {
  mountain: { bg: 0x9fd4e3, land: 0x466d48, route: 0xf0d798, accent: 0xf0a94a, target: 0xfff3bd, danger: 0xd95d3f },
  cloud: { bg: 0x9ed8ff, land: 0x5f88b8, route: 0xffffff, accent: 0xf6c85f, target: 0xe9fbff, danger: 0xe2644e },
  bamboo: { bg: 0xbfdc9a, land: 0x426c39, route: 0xd8b56d, accent: 0xffd15c, target: 0xfff7c5, danger: 0xcf563c },
  lantern: { bg: 0x23324a, land: 0x7a4935, route: 0xffc76b, accent: 0xff8d50, target: 0xfff1bd, danger: 0xff6650 }
};

export function buildPitchLadderSceneConfig(raw: Record<string, unknown>): PitchLadderSceneConfig {
  const nested = isRecord(raw.scene_config) ? raw.scene_config : {};
  const merged = { ...raw, ...nested };
  const pitchRange = normalizePitchRange(merged.pitch_range);
  const nodes = normalizeRouteNodes(merged.route_nodes, pitchRange);
  const rounds = normalizeRounds(merged.pitch_rounds, pitchRange);
  const skinId = String(merged.skin_id || "mountain_steps");
  const mode = normalizeMode(merged.current_mode, merged.target_pattern_type, merged.mode);
  return {
    engine: "phaser_2d",
    scene_id: "pitch_ladder_scene",
    runtime_shell: "pitch_ladder_map_shell",
    game_feel: "map_pitch_climb",
    skin_id: skinId,
    skin_play_mode: normalizePlayMode(merged.skin_play_mode, skinId),
    mode: String(merged.mode || "high_low_steps"),
    current_mode: mode,
    target_pattern_type: String(merged.target_pattern_type || mode),
    music_elements: normalizeMusicElements(merged.music_elements, pitchRange, mode),
    pitch_range: pitchRange,
    pitch_rounds: rounds,
    route_nodes: nodes,
    pitch_path: Array.isArray(merged.pitch_path) ? merged.pitch_path as Array<Record<string, unknown>> : [],
    energy_max: clampNumber(Number(merged.energy_max), 50, 150, 100),
    mistake_limit: clampNumber(Number(merged.mistake_limit), 1, 10, 3),
    sing_back_required: merged.sing_back_required !== false,
    audio_mode: normalizeAudioMode(merged.audio_mode),
    input_map: normalizeInputMap(merged.input_map),
    fx_profile: normalizeFxProfile(merged.fx_profile),
    adventure_hud: true,
    show_mission_ribbon_in_play: false,
    route_objective: normalizeRouteObjective(merged.route_objective, normalizePlayMode(merged.skin_play_mode, skinId)),
    copy_budget: normalizeCopyBudget(merged.copy_budget),
    character_profile: normalizeCharacterProfile(merged.character_profile),
    reward_model: normalizeRewardModel(merged.reward_model, rounds.length || 1),
    fail_pressure_model: normalizeFailPressureModel(merged.fail_pressure_model),
    content_manifest: isRecord(merged.content_manifest) ? merged.content_manifest as Partial<PitchLadderContentManifest> : undefined,
    map_hud: true,
    route_style: normalizeRouteStyle(merged.route_style),
    movement_profile: String(merged.movement_profile || "walk_arc") as PitchLadderSceneConfig["movement_profile"],
    hint_density: String(merged.hint_density || "low") as PitchLadderSceneConfig["hint_density"],
    show_teacher_text_in_play: false
  };
}

export function mountPitchLadderScene(
  parent: HTMLElement,
  config: PitchLadderSceneConfig,
  onEvent: (event: PitchLadderSceneEvent) => void
): PitchLadderController {
  const built = buildPitchLadderSceneConfig(config as Record<string, unknown>);
  const scene = new PitchLadderScene(built, onEvent);
  const game = new Phaser.Game({
    type: Phaser.AUTO,
    parent,
    width: WIDTH,
    height: HEIGHT,
    backgroundColor: palettes[built.skin_play_mode || "mountain"].bg,
    scale: {
      mode: Phaser.Scale.FIT,
      autoCenter: Phaser.Scale.CENTER_BOTH
    },
    scene: [scene]
  });

  return {
    listen: () => scene.listenTarget(),
    previewDirection: (direction: string) => scene.previewDirection(direction),
    startVoiceCharge: () => scene.startVoiceCharge(),
    updateVoiceMeter: (level: number, trace?: number[]) => scene.updateVoiceMeter(level, trace),
    resolveVoiceAttempt: (choice: string, voiceDirection: string) => scene.resolveVoiceAttempt(choice, voiceDirection),
    voiceRetry: (message: string) => scene.voiceRetry(message),
    chooseDirection: (direction: string) => scene.chooseDirection(direction),
    chooseNode: (note: string) => scene.chooseNode(note),
    confirmSingBack: () => scene.confirmSingBack(),
    reset: () => scene.resetMission(),
    destroy: () => {
      scene.destroyAudio();
      game.destroy(true);
    }
  };
}

class PitchLadderScene extends Phaser.Scene {
  private readonly sceneConfig: NormalizedPitchLadderSceneConfig;
  private readonly onSceneEvent: (event: PitchLadderSceneEvent) => void;
  private graphics!: Phaser.GameObjects.Graphics;
  private backdropImage?: Phaser.GameObjects.Image;
  private titleText!: Phaser.GameObjects.Text;
  private statusText!: Phaser.GameObjects.Text;
  private actor!: Phaser.GameObjects.Container;
  private actorSprite?: Phaser.GameObjects.Sprite;
  private actorShadow?: Phaser.GameObjects.Ellipse;
  private actorAnimationState: PitchLadderAnimationKey | null = null;
  private system: PitchLadderGameSystem;
  private contentManifest: PitchLadderContentManifest;
  private levelSteps: PitchLadderLevelStep[];
  private audioManager: GameAudioManager;
  private nodeTexts: Phaser.GameObjects.Text[] = [];
  private rewardTokens: Phaser.GameObjects.GameObject[] = [];
  private damageFlash = 0;
  private voiceActive = false;
  private voiceLevel = 0;
  private voiceTrace: number[] = [];

  constructor(config: PitchLadderSceneConfig, onEvent: (event: PitchLadderSceneEvent) => void) {
    super("pitch_ladder_scene");
    this.sceneConfig = normalizeRequiredConfig(config);
    this.onSceneEvent = onEvent;
    this.audioManager = new GameAudioManager(this.sceneConfig.audio_assets);
    this.system = new PitchLadderGameSystem({
      rounds: this.sceneConfig.pitch_rounds,
      energyMax: this.sceneConfig.energy_max,
      mistakeLimit: this.sceneConfig.mistake_limit
    });
    this.contentManifest = normalizeContentManifest(this.sceneConfig.content_manifest, this.sceneConfig.skin_play_mode);
    this.levelSteps = buildPitchLadderLevelSteps(this.sceneConfig.pitch_rounds, this.sceneConfig.skin_play_mode);
  }

  preload() {
    const art = this.contentManifest.art;
    if (art) {
      this.load.image(art.backgroundKey, art.background);
      this.load.image(art.heroSeedKey, art.heroSeed);
      this.load.image(art.heroPosesKey, art.heroPoses);
      this.load.image(art.propsSheetKey, art.propsSheet);
    }
    const heroSprite = this.contentManifest.heroSprite;
    if (heroSprite) {
      this.load.spritesheet(heroSprite.sheetKey, heroSprite.sheet, {
        frameWidth: heroSprite.frameWidth,
        frameHeight: heroSprite.frameHeight
      });
    }
  }

  create() {
    this.backdropImage = this.createBackdropImage();
    this.graphics = this.add.graphics();
    this.titleText = this.add.text(32, 24, "音高山路", {
      fontFamily: "Noto Sans SC, PingFang SC, Arial, sans-serif",
      fontSize: "20px",
      color: "#fff7d0",
      fontStyle: "bold"
    });
    this.statusText = this.add.text(32, 52, "听音", {
      fontFamily: "Noto Sans SC, PingFang SC, Arial, sans-serif",
      fontSize: "16px",
      color: "#fffef2"
    });
    this.createActorAnimations();
    this.actor = this.createActor();
    this.drawScene();
    this.moveActorToCurrentStart(false);
    this.startIdleAnimation();
    this.input.on("pointerdown", (pointer: Phaser.Input.Pointer) => this.handleStagePointer(pointer.x, pointer.y));
    this.emit("reset", undefined, "听音");
  }

  listenTarget() {
    const outcome = this.system.listen();
    this.flashSequence();
    this.emit("listen", outcome.judgement, outcome.message);
    this.time.delayedCall(720, () => {
      if (this.system.state.status === "listening") {
        const playing = this.system.enterPlaying(this.sceneConfig.current_mode === "melody_path" ? "路线" : "选");
        this.drawScene();
        this.emit("route_step", playing.judgement, playing.message);
      }
    });
  }

  chooseDirection(direction: string) {
    const round = this.currentPitchRound();
    const expected = String(round.answer || "");
    if (!["higher", "same", "lower"].includes(expected)) {
      this.chooseNode(direction);
      return;
    }
    const outcome = this.system.chooseDirection(direction);
    this.applySystemOutcome(outcome, "choose_direction");
  }

  previewDirection(direction: string) {
    if (!isPitchDirection(direction)) return;
    const expected = String(this.currentPitchRound().answer || "");
    if (!["higher", "same", "lower"].includes(expected)) {
      this.chooseNode(direction);
      return;
    }
    const outcome = this.system.previewDirection(direction);
    this.voiceActive = false;
    this.voiceLevel = 0;
    this.voiceTrace = [];
    this.drawScene();
    this.pulseDirection(direction);
    this.emit("preview_direction", outcome.judgement, outcome.message);
  }

  startVoiceCharge() {
    const outcome = this.system.startVoiceCharge();
    this.voiceActive = true;
    this.voiceLevel = 0.2;
    this.voiceTrace = [];
    this.drawScene();
    this.emit("voice_start", outcome.judgement, outcome.message);
  }

  updateVoiceMeter(level: number, trace: number[] = []) {
    this.voiceActive = true;
    this.voiceLevel = Math.max(0, Math.min(1, level));
    this.voiceTrace = trace.slice(-18);
    this.drawScene();
  }

  resolveVoiceAttempt(choice: string, voiceDirection: string) {
    if (!isPitchDirection(choice) || !isPitchDirection(voiceDirection)) return;
    this.voiceActive = false;
    this.voiceLevel = 0;
    this.voiceTrace = [];
    const outcome = this.system.resolveVoiceAttempt(choice, voiceDirection);
    this.applySystemOutcome(outcome, "voice_result");
  }

  voiceRetry(message: string) {
    const outcome = this.system.voiceRetry(message);
    this.voiceActive = false;
    this.voiceLevel = 0;
    this.voiceTrace = [];
    this.drawScene();
    this.emit("voice_retry", outcome.judgement, outcome.message);
  }

  chooseNode(note: string) {
    const outcome = this.system.chooseNode(note);
    if (outcome.type === "partial") this.tweenActorToNote(note);
    this.applySystemOutcome(outcome, "choose_node");
  }

  confirmSingBack() {
    const outcome = this.system.confirmSingBack();
    this.voiceActive = false;
    this.voiceLevel = 0;
    this.voiceTrace = [];
    this.drawScene();
    if (outcome.type === "mission_success") {
      this.playRewardFx(true);
      this.emit("mission_success", outcome.judgement, outcome.message);
      return;
    }
    if (outcome.type === "playing") {
      this.moveActorToCurrentStart(true);
      this.emit("route_step", outcome.judgement, outcome.message);
      return;
    }
    this.emit("round_success", outcome.judgement, outcome.message);
  }

  resetMission() {
    const outcome = this.system.reset();
    this.voiceActive = false;
    this.voiceLevel = 0;
    this.voiceTrace = [];
    this.drawScene();
    this.moveActorToCurrentStart(false);
    this.emit("reset", outcome.judgement, outcome.message);
  }

  private applySystemOutcome(outcome: ReturnType<PitchLadderGameSystem["chooseDirection"]>, eventType: PitchLadderSceneEvent["type"]) {
    if (outcome.type === "round_clear" || outcome.type === "mission_success") {
      this.audioManager.playSfx(outcome.type === "mission_success" ? "clear" : "reward");
      if (outcome.direction) this.tweenActorToDirection(outcome.direction);
      this.time.delayedCall(this.isNativeSkinRoute() ? 680 : 280, () => this.completeRound(outcome.type === "mission_success"));
      this.emit(eventType, outcome.judgement, outcome.message);
      return;
    }
    if (outcome.type === "partial") {
      this.audioManager.playSfx("step");
      this.drawScene();
      this.emit(eventType, outcome.judgement, outcome.message);
      return;
    }
    if (outcome.type === "mistake" || outcome.type === "mission_failed") {
      this.audioManager.playSfx("miss");
      this.playRegisteredMistake(outcome.message);
      this.emit(this.system.state.status === "mission_failed" ? "mission_failed" : "judgement", "wrong", outcome.message);
      return;
    }
    this.drawScene();
    this.emit(eventType, outcome.judgement, outcome.message);
  }

  private completeRound(missionSuccess: boolean) {
    this.drawScene();
    this.playRewardFx(missionSuccess);
    if (missionSuccess) {
      this.emit("mission_success", "sing_back", "登顶");
      return;
    }
    this.emit("round_success", "sing_back", "唱回");
    if (this.sceneConfig.current_mode === "direction_pair") {
      this.time.delayedCall(420, () => {
        const next = this.system.advanceRound();
        this.drawScene();
        this.moveActorToCurrentStart(true);
        this.emit("route_step", next.judgement, next.message);
      });
    }
  }

  private playRegisteredMistake(_message: string) {
    this.voiceActive = false;
    this.voiceLevel = 0;
    this.voiceTrace = [];
    this.damageFlash = 1;
    this.playMissFx();
    this.cameras.main.shake(180, 0.01);
    this.drawScene();
    this.time.delayedCall(360, () => {
      this.damageFlash = 0;
      this.drawScene();
    });
  }

  private drawScene() {
    const palette = palettes[this.sceneConfig.skin_play_mode];
    const state = this.system.state;
    this.clearDynamicLabels();
    this.graphics.clear();
    if (!this.hasSkinBackground()) this.graphics.fillStyle(palette.bg, 1).fillRect(0, 0, WIDTH, HEIGHT);
    this.drawBackdrop(palette);
    if (this.sceneConfig.current_mode === "direction_pair") {
      this.drawPlatformChallenge(palette);
      return;
    }
    if (this.isNativeSkinRoute()) {
      this.drawNativeNodeRoute(palette);
      return;
    }
    const points = this.nodePoints();
    this.graphics.lineStyle(10, palette.route, 0.86);
    for (let index = 0; index < points.length - 1; index += 1) {
      this.graphics.lineBetween(points[index].x, points[index].y, points[index + 1].x, points[index + 1].y);
    }
    if (this.damageFlash > 0) {
      this.drawRouteDamage(points, palette);
    }
    points.forEach((point, index) => {
      const node = this.sceneConfig.route_nodes[index];
      const selected = state.selected.includes(node.note) || (state.status === "listening" && this.currentSequence().includes(node.note));
      this.graphics.fillStyle(selected ? palette.target : 0xfffbdf, 1).fillCircle(point.x, point.y, selected ? 24 : 19);
      this.graphics.lineStyle(4, palette.accent, selected ? 1 : 0.45).strokeCircle(point.x, point.y, selected ? 26 : 21);
      this.nodeTexts.push(
        this.add.text(point.x, point.y + 30, node.label, {
          fontFamily: "Arial, sans-serif",
          fontSize: "16px",
          color: this.sceneConfig.skin_play_mode === "lantern" ? "#fff7d0" : "#18342a",
          fontStyle: "bold"
        }).setOrigin(0.5)
      );
    });
    this.drawRewardTrack(palette);
    this.drawObjective(palette);
    this.titleText.setText(this.titleForSkin());
    this.statusText.setText(this.shortStatusText());
  }

  private drawBackdrop(palette: (typeof palettes)[PitchLadderPlayMode]) {
    if (this.hasSkinBackground()) {
      this.graphics.fillGradientStyle(0x102333, 0x102333, 0x102333, 0x102333, 0.24, 0.08, 0, 0.18);
      this.graphics.fillRect(0, 0, WIDTH, HEIGHT);
      this.graphics.fillStyle(0xfff0a8, 0.12).fillEllipse(760, 82, 140, 76);
      return;
    }
    this.graphics.fillGradientStyle(0xffffff, 0xffffff, palette.bg, palette.bg, 0.24, 0.12, 0.08, 0.02);
    this.graphics.fillRect(0, 0, WIDTH, HEIGHT);
    this.graphics.fillStyle(0xffffff, 0.24).fillCircle(760, 82, 46);
    for (let index = 0; index < 5; index += 1) {
      this.graphics.fillStyle(0xffffff, 0.24 + (index % 2) * 0.1).fillEllipse(130 + index * 185, 86 + (index % 2) * 34, 132, 34);
    }
    if (this.sceneConfig.skin_play_mode === "cloud") {
      for (let index = 0; index < 5; index += 1) {
        this.graphics.fillStyle(0xffffff, 0.42).fillEllipse(150 + index * 160, 148 + (index % 2) * 54, 150, 56);
      }
      this.graphics.fillStyle(palette.land, 0.3).fillRoundedRect(70, 438, 820, 72, 28);
      return;
    }
    if (this.sceneConfig.skin_play_mode === "bamboo") {
      for (let index = 0; index < 8; index += 1) {
        this.graphics.fillStyle(0x3f7b3a, 0.34).fillRoundedRect(80 + index * 110, 90, 24, 410, 12);
      }
      return;
    }
    if (this.sceneConfig.skin_play_mode === "lantern") {
      for (let index = 0; index < 5; index += 1) {
        this.graphics.fillStyle(0xffb14e, 0.22).fillCircle(160 + index * 155, 115, 42);
      }
      this.graphics.fillStyle(0x1a2237, 0.45).fillRect(0, 422, WIDTH, 118);
      return;
    }
    this.graphics.fillStyle(0x6fa178, 0.28).fillTriangle(-60, 526, 250, 202, 600, 526);
    this.graphics.fillStyle(0x497557, 0.4).fillTriangle(220, 526, 610, 156, 1030, 526);
    this.graphics.fillStyle(palette.land, 0.22).fillRoundedRect(-30, 482, 1040, 78, 30);
  }

  private drawPlatformChallenge(palette: (typeof palettes)[PitchLadderPlayMode]) {
    if (this.isNativeSkinRoute()) {
      this.drawNativeSkinRoute(palette);
      return;
    }
    const state = this.system.state;
    const start = this.currentStartPoint();
    const choices = this.directionPlatforms();
    const expected = this.expectedDirection();
    const chosen = state.selected[0] as DirectionChoice | undefined;
    this.drawPlatform(start, palette, true);
    choices.forEach((platform) => {
      const isChosen = chosen === platform.direction;
      this.drawPlatform({
        ...platform,
        active: state.status === "playing" || state.status === "listening",
        correct: isChosen || (state.status === "listening" && platform.direction === expected)
      }, palette);
    });
    this.drawRewardTrack(palette);
    this.drawObjective(palette);
    this.drawVoiceMeter(palette);
    this.titleText.setText(this.titleForSkin());
    this.statusText.setText(this.shortStatusText());
  }

  private drawNativeSkinRoute(palette: (typeof palettes)[PitchLadderPlayMode]) {
    const state = this.system.state;
    const start = this.currentStartPoint();
    const choices = this.directionPlatforms();
    const chosen = state.selected[0] as DirectionChoice | undefined;
    const expected = this.expectedDirection();
    this.drawSkinRouteTrail(palette, start, choices);
    this.drawSkinRouteNode(start, palette, "current", true);
    this.debugNativeRoutePoint(start, 0x66fff0);
    choices.forEach((choice) => {
      this.drawSkinRouteNode(choice, palette, choice.direction || "same", chosen === choice.direction || (state.status === "listening" && choice.direction === expected));
      this.debugNativeRoutePoint(choice, choice.direction === expected ? 0xfff36a : 0xffffff);
    });
    this.drawRewardTrack(palette);
    this.drawObjective(palette);
    this.drawVoiceMeter(palette);
    this.titleText.setText(this.titleForSkin());
    this.statusText.setText(this.shortStatusText());
  }

  private drawNativeNodeRoute(palette: (typeof palettes)[PitchLadderPlayMode]) {
    const state = this.system.state;
    const points = this.nodePoints();
    this.drawNativeNodeTrail(palette, points);
    this.drawNativeTargetSequence(palette);
    points.forEach((point, index) => {
      const node = this.sceneConfig.route_nodes[index];
      const selected = state.selected.includes(node.note);
      const previewed = state.status === "listening" && this.currentSequence().includes(node.note);
      this.drawNativeNoteNode(point, palette, node.label, selected || previewed, selected);
    });
    if (this.damageFlash > 0) {
      this.drawRouteDamage(points, palette);
    }
    this.drawRewardTrack(palette);
    this.drawObjective(palette);
    this.titleText.setText(this.titleForSkin());
    this.statusText.setText(this.shortStatusText());
  }

  private drawNativeNodeTrail(palette: (typeof palettes)[PitchLadderPlayMode], points: RoutePoint[]) {
    this.graphics.lineStyle(5, palette.target, 0.22);
    for (let index = 0; index < points.length - 1; index += 1) {
      const start = points[index];
      const end = points[index + 1];
      const controlX = (start.x + end.x) / 2;
      const controlY = Math.min(start.y, end.y) - 18;
      const path = new Phaser.Curves.QuadraticBezier(
        new Phaser.Math.Vector2(start.x, start.y),
        new Phaser.Math.Vector2(controlX, controlY),
        new Phaser.Math.Vector2(end.x, end.y)
      );
      const trailPoints = path.getPoints(14);
      trailPoints.forEach((point, pointIndex) => {
        if (pointIndex === 0) this.graphics.moveTo(point.x, point.y);
        else this.graphics.lineTo(point.x, point.y);
      });
      this.graphics.fillStyle(palette.target, 0.16);
      trailPoints.filter((_, pointIndex) => pointIndex % 5 === 2).forEach((point) => this.graphics.fillCircle(point.x, point.y, 3));
    }
  }

  private drawNativeTargetSequence(palette: (typeof palettes)[PitchLadderPlayMode]) {
    const sequence = this.currentSequence();
    if (sequence.length < 2 || this.system.state.status === "ready") return;
    const points = sequence.map((note) => this.pointForNote(note));
    this.graphics.lineStyle(4, palette.accent, this.system.state.status === "listening" ? 0.78 : 0.48);
    for (let index = 0; index < points.length - 1; index += 1) {
      const start = points[index];
      const end = points[index + 1];
      this.graphics.lineBetween(start.x, start.y, end.x, end.y);
    }
  }

  private drawNativeNoteNode(point: RoutePoint, palette: (typeof palettes)[PitchLadderPlayMode], label: string, active: boolean, selected: boolean) {
    this.graphics.fillStyle(0x102333, 0.24).fillEllipse(point.x, point.y + 9, active ? 58 : 44, active ? 14 : 10);
    this.graphics.fillStyle(active ? palette.target : 0xffffff, active ? 0.24 : 0.12).fillCircle(point.x, point.y, active ? 26 : 20);
    this.graphics.lineStyle(active ? 3 : 2, selected ? palette.accent : 0xffffff, active ? 0.92 : 0.46).strokeCircle(point.x, point.y, active ? 23 : 18);
    this.nodeTexts.push(
      this.add.text(point.x, point.y, label, {
        fontFamily: "Noto Sans SC, PingFang SC, Arial, sans-serif",
        fontSize: "15px",
        color: "#fff8dd",
        fontStyle: "bold",
        stroke: "#173427",
        strokeThickness: 3
      }).setOrigin(0.5)
    );
  }

  private drawSkinRouteTrail(palette: (typeof palettes)[PitchLadderPlayMode], start: PlatformPoint, choices: PlatformPoint[]) {
    choices.forEach((choice) => {
      const controlX = (start.x + choice.x) / 2;
      const controlY = Math.min(start.y, choice.y) - (choice.direction === "same" ? 18 : 34);
      const path = new Phaser.Curves.QuadraticBezier(
        new Phaser.Math.Vector2(start.x, start.y),
        new Phaser.Math.Vector2(controlX, controlY),
        new Phaser.Math.Vector2(choice.x, choice.y)
      );
      const points = path.getPoints(18);
      this.graphics.lineStyle(choice.direction === this.system.state.selected[0] ? 4 : 2, palette.target, choice.direction === this.system.state.selected[0] ? 0.74 : 0.2);
      points.forEach((point, index) => {
        if (index === 0) this.graphics.moveTo(point.x, point.y);
        else this.graphics.lineTo(point.x, point.y);
      });
      this.graphics.fillStyle(palette.target, choice.direction === this.expectedDirection() && this.system.state.status === "listening" ? 0.58 : 0.18);
      points.filter((_, index) => index % 6 === 3).forEach((point) => this.graphics.fillCircle(point.x, point.y, 4));
    });
  }

  private drawSkinRouteNode(platform: PlatformPoint, palette: (typeof palettes)[PitchLadderPlayMode], glyph: string, active: boolean) {
    this.graphics.fillStyle(0x102333, 0.22).fillEllipse(platform.x, platform.y + 9, active ? 56 : 42, active ? 13 : 9);
    this.graphics.fillStyle(active ? palette.target : 0xffffff, active ? 0.2 : 0.1).fillCircle(platform.x, platform.y, active ? 25 : 19);
    this.graphics.lineStyle(active ? 3 : 2, active ? palette.accent : 0xffffff, active ? 0.9 : 0.44).strokeCircle(platform.x, platform.y, active ? 22 : 17);
    if (glyph !== "current") {
      this.nodeTexts.push(
        this.add.text(platform.x, platform.y, pitchDirectionGlyph(glyph as DirectionChoice), {
          fontFamily: "Noto Sans SC, PingFang SC, Arial, sans-serif",
          fontSize: "15px",
          color: "#fff8dd",
          fontStyle: "bold",
          stroke: "#173427",
          strokeThickness: 3
        }).setOrigin(0.5)
      );
    }
  }

  private drawPlatform(platform: PlatformPoint, palette: (typeof palettes)[PitchLadderPlayMode], start = false) {
    const glow = platform.active || platform.correct || start;
    const topColor = platform.correct ? palette.target : start ? 0xfff4c8 : 0xf6e5a3;
    const baseColor = start ? palette.accent : palette.land;
    const accentStripe = this.contentManifest.environment.platformKey === "singing_platform" ? 0xfff7c5 : topColor;
    if (glow) {
      this.graphics.fillStyle(platform.correct ? palette.accent : 0xffffff, platform.correct ? 0.24 : 0.16).fillEllipse(platform.x, platform.y + 8, platform.width + 58, 44);
    }
    this.graphics.fillStyle(0x1b2838, 0.2).fillEllipse(platform.x, platform.y + 36, platform.width + 32, 24);
    this.graphics.fillStyle(baseColor, start ? 0.98 : 0.88).fillRoundedRect(platform.x - platform.width / 2, platform.y, platform.width, 34, 16);
    this.graphics.fillStyle(topColor, 0.98).fillRoundedRect(platform.x - platform.width / 2 + 8, platform.y - 14, platform.width - 16, 30, 15);
    this.graphics.fillStyle(accentStripe, 0.42).fillRoundedRect(platform.x - platform.width / 2 + 20, platform.y - 7, platform.width - 40, 7, 4);
    this.graphics.lineStyle(4, platform.correct ? palette.accent : 0xffffff, platform.correct ? 0.96 : 0.52).strokeRoundedRect(platform.x - platform.width / 2 + 8, platform.y - 14, platform.width - 16, 30, 15);
    if (platform.label) {
      this.nodeTexts.push(
        this.add.text(platform.x, platform.y - 48, platform.label, {
          fontFamily: "Noto Sans SC, PingFang SC, Arial, sans-serif",
          fontSize: start ? "18px" : "20px",
          color: this.sceneConfig.skin_play_mode === "lantern" ? "#fff8dd" : "#173427",
          fontStyle: "bold"
        }).setOrigin(0.5)
      );
    }
  }

  private drawEnergyBar(palette: (typeof palettes)[PitchLadderPlayMode]) {
    const percent = Math.max(0, Math.min(1, this.system.state.energy / Math.max(1, this.sceneConfig.energy_max)));
    this.graphics.fillStyle(0x142330, 0.32).fillRoundedRect(34, HEIGHT - 54, 210, 18, 9);
    this.graphics.fillStyle(percent <= 0.32 ? palette.danger : palette.accent, 0.9).fillRoundedRect(38, HEIGHT - 50, 202 * percent, 10, 5);
    this.nodeTexts.push(
      this.add.text(34, HEIGHT - 82, `能量 ${Math.round(percent * 100)}%`, {
        fontFamily: "Noto Sans SC, PingFang SC, Arial, sans-serif",
        fontSize: "16px",
        color: "#fff8dd",
        fontStyle: "bold"
      })
    );
  }

  private drawVoiceMeter(palette: (typeof palettes)[PitchLadderPlayMode]) {
    const selectedDirection = this.system.state.selected[0] as DirectionChoice | undefined;
    if (!this.voiceActive && !selectedDirection) return;
    const x = 320;
    const y = HEIGHT - 74;
    const width = 300;
    this.graphics.fillStyle(0x102333, 0.46).fillRoundedRect(x, y, width, 38, 18);
    this.graphics.fillStyle(palette.accent, 0.82).fillRoundedRect(x + 10, y + 12, Math.max(8, (width - 20) * this.voiceLevel), 14, 7);
    this.graphics.lineStyle(2, 0xffffff, 0.34).strokeRoundedRect(x, y, width, 38, 18);
    const label = this.voiceActive ? "声音蓄力" : selectedDirection ? `已选${pitchDirectionLabel(selectedDirection)}` : "先选平台";
    this.nodeTexts.push(
      this.add.text(x + width / 2, y - 12, label, {
        fontFamily: "Noto Sans SC, PingFang SC, Arial, sans-serif",
        fontSize: "16px",
        color: "#fff8dd",
        fontStyle: "bold"
      }).setOrigin(0.5)
    );
    if (this.voiceTrace.length < 2) return;
    const minPitch = Math.min(...this.voiceTrace);
    const maxPitch = Math.max(...this.voiceTrace);
    this.graphics.lineStyle(3, palette.target, 0.88);
    this.voiceTrace.forEach((pitch, index) => {
      const px = x + 18 + (index / Math.max(1, this.voiceTrace.length - 1)) * (width - 36);
      const normalized = (pitch - minPitch) / Math.max(1, maxPitch - minPitch);
      const py = y + 28 - normalized * 20;
      if (index === 0) this.graphics.moveTo(px, py);
      else this.graphics.lineTo(px, py);
    });
  }

  private clearDynamicLabels() {
    this.nodeTexts.forEach((text) => text.destroy());
    this.nodeTexts = [];
  }

  private createBackdropImage() {
    const art = this.contentManifest.art;
    if (!art || !this.textures.exists(art.backgroundKey)) return undefined;
    return this.add.image(WIDTH / 2, HEIGHT / 2, art.backgroundKey).setDisplaySize(WIDTH, HEIGHT).setDepth(-2);
  }

  private hasSkinBackground() {
    const art = this.contentManifest.art;
    return Boolean(this.backdropImage && art && this.textures.exists(art.backgroundKey));
  }

  private shortStatusText() {
    const state = this.system.state;
    if (state.status === "mission_success") return "登顶";
    if (state.status === "mission_failed") return "再听";
    if (state.status === "round_clear") return "唱回";
    if (state.status === "listening") return "听音";
    return state.message.length > 6 ? state.message.slice(0, 6) : state.message;
  }

  private createActor() {
    const palette = palettes[this.sceneConfig.skin_play_mode];
    const actor = this.add.container(0, 0);
    actor.setName(this.contentManifest.hero.key);
    const heroSprite = this.contentManifest.heroSprite;
    if (heroSprite && this.textures.exists(heroSprite.sheetKey)) {
      this.actorShadow = this.add.ellipse(0, -6, 42, 16, 0x264653, 0.24);
      actor.add(this.actorShadow);
      this.actorSprite = this.add.sprite(0, 0, heroSprite.sheetKey, 0)
        .setOrigin(heroSprite.anchor.x, heroSprite.anchor.y)
        .setDisplaySize(
          Math.round(heroSprite.displayHeight * (heroSprite.frameWidth / heroSprite.frameHeight)),
          heroSprite.displayHeight
        );
      actor.add(this.actorSprite);
      this.playActorAnim("idle", true);
      return actor;
    }
    const art = this.contentManifest.art;
    if (art && this.textures.exists(art.heroSeedKey)) {
      this.actorShadow = this.add.ellipse(0, -6, 42, 16, 0x264653, 0.24);
      actor.add(this.actorShadow);
      const sprite = this.add.image(0, 0, art.heroSeedKey).setOrigin(0.5, 1);
      if (this.sceneConfig.skin_play_mode === "cloud") {
        sprite.setCrop(120, 30, 280, 430).setDisplaySize(84, 129);
      } else if (this.sceneConfig.skin_play_mode === "bamboo") {
        sprite.setCrop(128, 28, 250, 442).setDisplaySize(78, 138);
      } else {
        sprite.setDisplaySize(82, 96);
      }
      actor.add(sprite);
      return actor;
    }
    actor.add(this.add.ellipse(0, 18, 34, 20, 0x264653, 0.28));
    actor.add(this.add.circle(0, 0, 20, 0xfff0c2));
    actor.add(this.add.rectangle(0, 26, 32, 34, palette.accent));
    actor.add(this.add.rectangle(-15, 28, 8, 26, 0x365c7d).setAngle(12));
    actor.add(this.add.rectangle(15, 28, 8, 26, 0x365c7d).setAngle(-12));
    actor.add(this.add.rectangle(-9, 50, 8, 22, 0x2b4a64).setAngle(8));
    actor.add(this.add.rectangle(9, 50, 8, 22, 0x2b4a64).setAngle(-8));
    actor.add(this.add.ellipse(0, -20, 52, 18, 0x365c7d));
    actor.add(this.add.triangle(0, -38, -20, -20, 20, -20, 0, -52, 0x365c7d));
    actor.add(this.add.rectangle(-24, 22, 10, 26, 0xd76b3f));
    actor.add(this.add.circle(-7, -5, 3.5, 0x273238));
    actor.add(this.add.circle(7, -5, 3.5, 0x273238));
    actor.add(this.add.arc(0, 4, 9, 15, 165, false, 0x273238, 1.8));
    return actor;
  }

  private createActorAnimations() {
    const heroSprite = this.contentManifest.heroSprite;
    if (!heroSprite || !this.textures.exists(heroSprite.sheetKey)) return;
    (Object.entries(heroSprite.animations) as Array<[PitchLadderAnimationKey, { frames: number[]; frameRate: number; repeat: number }]>).forEach(([key, config]) => {
      const animationKey = this.actorAnimationKey(key);
      if (this.anims.exists(animationKey)) return;
      this.anims.create({
        key: animationKey,
        frames: config.frames.map((frame) => ({ key: heroSprite.sheetKey, frame })),
        frameRate: config.frameRate,
        repeat: config.repeat
      });
    });
  }

  private actorAnimationKey(key: PitchLadderAnimationKey) {
    const heroSprite = this.contentManifest.heroSprite;
    return `${heroSprite?.sheetKey || this.contentManifest.hero.key}_${key}`;
  }

  private playActorAnim(key: PitchLadderAnimationKey, force = false) {
    if (!this.actorSprite || (!force && this.actorAnimationState === key)) return;
    const animationKey = this.actorAnimationKey(key);
    if (!this.anims.exists(animationKey)) return;
    this.actorAnimationState = key;
    this.actorSprite.play(animationKey, true);
  }

  private startIdleAnimation() {
    if (this.actorSprite) {
      this.playActorAnim("idle", true);
      this.tweens.add({
        targets: this.actorSprite,
        y: -6,
        duration: 720,
        yoyo: true,
        repeat: -1,
        ease: "Sine.easeInOut"
      });
      if (this.actorShadow) {
        this.tweens.add({
          targets: this.actorShadow,
          scaleX: 0.88,
          scaleY: 0.82,
          duration: 720,
          yoyo: true,
          repeat: -1,
          ease: "Sine.easeInOut"
        });
      }
      return;
    }
    this.tweens.add({
      targets: this.actor,
      y: this.actor.y - 6,
      duration: 720,
      yoyo: true,
      repeat: -1,
      ease: "Sine.easeInOut"
    });
  }

  private drawRouteDamage(points: Array<{ x: number; y: number }>, palette: (typeof palettes)[PitchLadderPlayMode]) {
    this.graphics.lineStyle(5, palette.danger, 0.86);
    const startIndex = Math.max(0, Math.min(this.system.state.selected.length, points.length - 2));
    const start = points[startIndex];
    const end = points[startIndex + 1] || start;
    const midX = (start.x + end.x) / 2;
    const midY = (start.y + end.y) / 2;
    this.graphics.lineBetween(midX - 28, midY - 16, midX - 8, midY + 12);
    this.graphics.lineBetween(midX - 8, midY + 12, midX + 20, midY - 12);
    this.graphics.fillStyle(palette.danger, 0.18).fillCircle(midX, midY, 46);
  }

  private drawRewardTrack(palette: (typeof palettes)[PitchLadderPlayMode]) {
    this.rewardTokens.forEach((token) => token.destroy());
    this.rewardTokens = [];
    const total = Math.max(1, this.sceneConfig.reward_model.tokens_required);
    const shown = Math.min(total, 6);
    for (let index = 0; index < shown; index += 1) {
      const filled = index < this.system.state.cleared;
      const x = WIDTH - 52 - index * 34;
      const y = 42;
      this.graphics.fillStyle(filled ? palette.accent : 0xffffff, filled ? 1 : 0.42).fillCircle(x, y, 12);
      this.graphics.lineStyle(2, filled ? 0xffffff : palette.accent, filled ? 0.88 : 0.38).strokeCircle(x, y, 13);
    }
  }

  private drawObjective(palette: (typeof palettes)[PitchLadderPlayMode]) {
    const end = this.routeGoalPoint();
    if (!end) return;
    this.graphics.fillStyle(0xffffff, 0.18).fillRoundedRect(end.x - 42, end.y - 116, 84, 18, 9);
    if (this.sceneConfig.route_objective === "cloud_gate") {
      this.graphics.fillStyle(0xffffff, 0.7).fillRoundedRect(end.x - 48, end.y - 92, 96, 54, 24);
      this.graphics.lineStyle(5, palette.accent, this.system.state.status === "mission_success" ? 1 : 0.4).strokeRoundedRect(end.x - 52, end.y - 96, 104, 62, 26);
      return;
    }
    if (this.sceneConfig.route_objective === "bamboo_crown") {
      this.graphics.fillStyle(0xffd15c, this.system.state.status === "mission_success" ? 0.95 : 0.45).fillCircle(end.x, end.y - 72, 28);
      this.graphics.fillStyle(0xfff7c5, 0.78).fillCircle(end.x, end.y - 72, 12);
      return;
    }
    if (this.sceneConfig.route_objective === "lantern_beacon") {
      this.graphics.fillStyle(0xff8d50, this.system.state.status === "mission_success" ? 0.95 : 0.42).fillCircle(end.x, end.y - 70, 30);
      this.graphics.lineStyle(3, 0xfff1bd, 0.9).strokeCircle(end.x, end.y - 70, 36);
      return;
    }
    this.graphics.fillStyle(0x365c7d, 1).fillRect(end.x - 4, end.y - 90, 8, 70);
    this.graphics.fillStyle(this.system.state.status === "mission_success" ? palette.accent : 0xfff3bd, 0.95).fillTriangle(end.x + 4, end.y - 90, end.x + 62, end.y - 72, end.x + 4, end.y - 54);
    this.graphics.fillStyle(0xfffbdf, this.system.state.status === "mission_success" ? 0.98 : 0.52).fillCircle(end.x, end.y - 10, 30);
    this.graphics.lineStyle(5, palette.accent, this.system.state.status === "mission_success" ? 1 : 0.42).strokeCircle(end.x, end.y - 10, 33);
  }

  private animateRoundClear(missionDone: boolean) {
    this.playActorAnim(missionDone ? "win" : "idle", true);
    const palette = palettes[this.sceneConfig.skin_play_mode];
    const end = this.sceneConfig.current_mode === "direction_pair" ? this.currentStartPoint() : this.routeGoalPoint();
    const token = this.add.star(this.actor.x, this.actor.y - 42, 5, 10, 22, palette.accent, 0.96);
    token.setName(this.contentManifest.fx.reward);
    this.tweens.add({
      targets: token,
      x: WIDTH - 52 - Math.min(this.system.state.cleared - 1, 5) * 34,
      y: 42,
      scale: 0.7,
      duration: 520,
      ease: "Back.easeIn",
      onComplete: () => token.destroy()
    });
    if (missionDone) {
      this.graphics.fillStyle(palette.target, 0.88).fillCircle(end.x, end.y - 46, 24);
      this.cameras.main.flash(380, 255, 240, 170);
    }
    this.tweens.add({ targets: this.actor, scale: 1.2, yoyo: true, duration: 180, repeat: missionDone ? 4 : 2 });
  }

  private playRewardFx(missionDone: boolean) {
    this.animateRoundClear(missionDone);
    if (missionDone) this.playStageClearFx();
  }

  destroyAudio() {
    this.audioManager.destroy();
  }

  private playMissFx() {
    this.animateSlip();
    const point = this.sceneConfig.current_mode === "direction_pair"
      ? this.currentStartPoint()
      : this.pointForNote(this.system.state.selected[this.system.state.selected.length - 1] || this.currentSequence()[0] || this.sceneConfig.route_nodes[0]?.note);
    const dust = this.add.circle(point.x, point.y - 20, 22, palettes[this.sceneConfig.skin_play_mode].danger, 0.35);
    dust.setName(this.contentManifest.fx.miss);
    const label = this.add.text(point.x, point.y - 82, "再听", {
      color: "#fff2bd",
      fontFamily: "Noto Sans SC, PingFang SC, sans-serif",
      fontSize: "26px",
      fontStyle: "bold"
    }).setOrigin(0.5);
    this.tweens.add({ targets: dust, scale: 2.2, alpha: 0, duration: 420, ease: "Cubic.Out", onComplete: () => dust.destroy() });
    this.tweens.add({ targets: label, y: point.y - 116, alpha: 0, duration: 460, ease: "Cubic.Out", onComplete: () => label.destroy() });
  }

  private playStageClearFx() {
    this.playActorAnim("win", true);
    const end = this.routeGoalPoint();
    const flag = this.add.triangle(end.x + 44, end.y - 120, 0, 0, 0, 52, 54, 18, palettes[this.sceneConfig.skin_play_mode].accent, 0.96);
    const label = this.add.text(end.x, end.y - 150, "登顶", {
      color: "#fff8dd",
      fontFamily: "Noto Sans SC, PingFang SC, sans-serif",
      fontSize: "42px",
      fontStyle: "bold"
    }).setOrigin(0.5);
    this.tweens.add({ targets: flag, y: flag.y - 20, angle: 8, yoyo: true, repeat: 2, duration: 180 });
    this.tweens.add({ targets: label, scale: 1.18, alpha: 0, duration: 760, ease: "Back.Out", onComplete: () => label.destroy() });
  }

  private animateSlip() {
    this.playActorAnim("fall", true);
    if (this.sceneConfig.current_mode === "direction_pair") {
      const start = this.currentStartPoint();
      if (this.isNativeSkinRoute()) {
        const wrong = this.system.state.selected[0] as DirectionChoice | undefined;
        const target = wrong ? this.directionPlatforms().find((platform) => platform.direction === wrong) : undefined;
        const footY = this.actorFootY(start);
        if (target) {
          const partial = {
            x: start.x + (target.x - start.x) * 0.36,
            y: footY + (this.actorFootY(target) - footY) * 0.36
          };
          this.tweens.add({ targets: this.actor, x: partial.x, y: partial.y, angle: wrong === "higher" ? -4 : 4, duration: 190, ease: "Sine.easeOut" });
          this.time.delayedCall(190, () => this.playActorAnim("fail", true));
          this.tweens.add({
            targets: this.actor,
            x: start.x,
            y: footY,
            angle: 0,
            duration: 300,
            delay: 210,
            ease: "Back.easeOut",
            onComplete: () => this.playActorAnim("idle", true)
          });
          return;
        }
      }
      this.tweens.add({ targets: this.actor, x: start.x - 28, y: start.y - 26, angle: -12, duration: 120, yoyo: true, repeat: 1 });
      this.tweens.add({ targets: this.actor, x: start.x, y: this.actorFootY(start), angle: 0, duration: 260, delay: 240, ease: "Sine.easeOut", onComplete: () => this.playActorAnim("idle", true) });
      return;
    }
    const fallbackNote = this.system.state.selected[this.system.state.selected.length - 1] || this.currentSequence()[0] || this.sceneConfig.route_nodes[0]?.note;
    const point = this.pointForNote(fallbackNote);
    const actorY = this.actorYForRoutePoint(point);
    this.tweens.add({ targets: this.actor, x: point.x - 18, y: actorY - 18, angle: -8, duration: 120, yoyo: true, repeat: 1 });
    this.tweens.add({ targets: this.actor, x: point.x, y: actorY, angle: 0, duration: 260, delay: 240, ease: "Sine.easeOut", onComplete: () => this.playActorAnim("idle", true) });
  }

  private flashSequence() {
    if (this.sceneConfig.current_mode === "direction_pair") {
      const expected = this.expectedDirection();
      this.directionPlatforms().forEach((platform, index) => {
        this.time.delayedCall(index * 120, () => {
          const marker = this.add.circle(platform.x, platform.y - 6, platform.direction === expected ? 36 : 26, platform.direction === expected ? palettes[this.sceneConfig.skin_play_mode].target : 0xffffff, platform.direction === expected ? 0.42 : 0.16);
          this.tweens.add({ targets: marker, scale: platform.direction === expected ? 1.9 : 1.35, alpha: 0, duration: 460, onComplete: () => marker.destroy() });
        });
      });
      return;
    }
    this.currentSequence().forEach((note, index) => {
      const point = this.pointForNote(note);
      this.time.delayedCall(index * 240, () => {
        const marker = this.add.circle(point.x, point.y, 34, palettes[this.sceneConfig.skin_play_mode].target, 0.35);
        this.tweens.add({ targets: marker, scale: 1.7, alpha: 0, duration: 420, onComplete: () => marker.destroy() });
      });
    });
  }

  private moveActorToCurrentStart(animate: boolean) {
    if (this.sceneConfig.current_mode === "direction_pair") {
      const point = this.currentStartPoint();
      const y = this.actorFootY(point);
      if (animate) {
        this.playActorAnim("walk", true);
        this.tweens.add({ targets: this.actor, x: point.x, y, duration: 360, ease: "Sine.easeInOut", onComplete: () => this.playActorAnim("idle", true) });
      } else {
        this.actor.setPosition(point.x, y);
        this.playActorAnim("idle", true);
      }
      return;
    }
    const first = this.currentSequence()[0] || this.sceneConfig.route_nodes[0]?.note;
    const point = this.pointForNote(first);
    const actorY = this.actorYForRoutePoint(point);
    if (animate) {
      this.playActorAnim("walk", true);
      this.tweens.add({ targets: this.actor, x: point.x, y: actorY, duration: 360, ease: "Sine.easeInOut", onComplete: () => this.playActorAnim("idle", true) });
    } else {
      this.actor.setPosition(point.x, actorY);
      this.playActorAnim("idle", true);
    }
  }

  private tweenActorToNote(note: string) {
    const point = this.pointForNote(note);
    this.playActorAnim("walk", true);
    if (this.isNativeSkinRoute()) {
      const start = new Phaser.Math.Vector2(this.actor.x, this.actor.y);
      const end = new Phaser.Math.Vector2(point.x, this.actorYForRoutePoint(point));
      const curve = new Phaser.Curves.QuadraticBezier(
        start,
        new Phaser.Math.Vector2((start.x + end.x) / 2, Math.min(start.y, end.y) - 22),
        end
      );
      const marker = { t: 0 };
      this.tweens.add({
        targets: marker,
        t: 1,
        duration: 360,
        ease: "Sine.easeInOut",
        onUpdate: () => {
          const routePoint = curve.getPoint(marker.t);
          this.actor.setPosition(routePoint.x, routePoint.y);
        },
        onComplete: () => this.playActorAnim("idle", true)
      });
      return;
    }
    this.tweens.add({ targets: this.actor, x: point.x, y: this.actorYForRoutePoint(point), duration: 260, ease: "Back.easeOut", onComplete: () => this.playActorAnim("idle", true) });
  }

  private tweenActorToDirection(direction: DirectionChoice) {
    const point = this.directionPlatforms().find((platform) => platform.direction === direction) || this.directionPlatforms()[1];
    if (this.isNativeSkinRoute()) {
      this.tweenActorAlongRoute(point, direction);
      return;
    }
    this.playActorAnim(direction === "higher" ? "jump" : "walk", true);
    this.tweens.add({
      targets: this.actor,
      x: point.x,
      y: point.y - 52,
      duration: 360,
      ease: "Cubic.easeOut",
      onComplete: () => this.playActorAnim("idle", true)
    });
    this.tweens.add({ targets: this.actor, scale: 1.12, yoyo: true, duration: 170, ease: "Back.easeOut" });
  }

  private tweenActorAlongRoute(target: PlatformPoint, direction: DirectionChoice) {
    const start = new Phaser.Math.Vector2(this.actor.x, this.actor.y);
    const end = new Phaser.Math.Vector2(target.x, this.actorFootY(target));
    const sameStep = direction === "same";
    const verticalDelta = Math.abs(start.y - end.y);
    const arcLift = sameStep ? 8 : Math.max(18, Math.min(38, verticalDelta * 0.38));
    const control = new Phaser.Math.Vector2((start.x + end.x) / 2, Math.min(start.y, end.y) - arcLift);
    const curve = new Phaser.Curves.QuadraticBezier(start, control, end);
    const marker = { t: 0 };
    this.actor.setScale(1, 1);
    this.playActorAnim(direction === "higher" ? "jump" : "walk", true);
    if (direction === "higher") {
      this.time.delayedCall(180, () => this.playActorAnim("walk", true));
    }
    this.tweens.add({
      targets: marker,
      t: 1,
      duration: sameStep ? 420 : 620,
      ease: "Sine.easeInOut",
      onUpdate: () => {
        const point = curve.getPoint(marker.t);
        this.actor.setPosition(point.x, point.y + Math.sin(marker.t * Math.PI * (sameStep ? 2 : 4)) * (sameStep ? 1.5 : 2.5));
        if (Math.round(marker.t * 10) % 3 === 0) this.spawnNoteTrail(point.x, point.y - 46);
      },
      onComplete: () => {
        this.actor.setPosition(end.x, end.y);
        this.playActorAnim("idle", true);
      }
    });
    this.tweens.add({ targets: this.actor, scaleX: direction === "lower" ? 0.96 : 1.04, scaleY: direction === "higher" ? 1.06 : 0.98, yoyo: true, duration: 180, repeat: 2 });
  }

  private spawnNoteTrail(x: number, y: number) {
    const note = this.add.text(x, y, "♪", {
      fontFamily: "Arial, sans-serif",
      fontSize: "18px",
      color: "#fff6a8",
      fontStyle: "bold"
    }).setOrigin(0.5);
    this.tweens.add({ targets: note, y: y - 28, alpha: 0, scale: 0.5, duration: 420, ease: "Cubic.Out", onComplete: () => note.destroy() });
  }

  private pulseDirection(direction: DirectionChoice) {
    const point = this.directionPlatforms().find((platform) => platform.direction === direction);
    if (!point) return;
    const ring = this.add.circle(point.x, point.y - 6, 38, palettes[this.sceneConfig.skin_play_mode].target, 0.28);
    this.tweens.add({ targets: ring, scale: 1.75, alpha: 0, duration: 420, ease: "Cubic.Out", onComplete: () => ring.destroy() });
    this.tweens.add({ targets: this.actor, scale: 1.08, yoyo: true, duration: 150, ease: "Back.easeOut" });
  }

  private pointForNote(note: string) {
    const index = Math.max(0, this.sceneConfig.route_nodes.findIndex((node) => node.note === note));
    return this.nodePoints()[index] || this.nodePoints()[0];
  }

  private handleStagePointer(x: number, y: number) {
    if (this.system.state.status === "ready" || this.system.state.status === "listening") return;
    if (this.sceneConfig.current_mode === "direction_pair") {
      const platform = this.directionPlatforms().find((item) => (
        Math.abs(x - item.x) <= item.width / 2 + 34 && Math.abs(y - item.y) <= 74
      ));
      if (platform?.direction) this.previewDirection(platform.direction);
      return;
    }
    const nearest = this.sceneConfig.route_nodes
      .map((node) => ({ node, point: this.pointForNote(node.note) }))
      .sort((a, b) => Phaser.Math.Distance.Between(x, y, a.point.x, a.point.y) - Phaser.Math.Distance.Between(x, y, b.point.x, b.point.y))[0];
    if (nearest && Phaser.Math.Distance.Between(x, y, nearest.point.x, nearest.point.y) <= 78) this.chooseNode(nearest.node.note);
  }

  private nodePoints() {
    if (this.isNativeSkinRoute()) {
      return buildPitchLadderNativeRoutePoints(this.sceneConfig.route_nodes.length, this.sceneConfig.skin_play_mode, WIDTH, HEIGHT);
    }
    const count = Math.max(1, this.sceneConfig.route_nodes.length);
    return this.sceneConfig.route_nodes.map((_, index) => ({
      x: 120 + (index / Math.max(1, count - 1)) * 720,
      y: 420 - (index / Math.max(1, count - 1)) * 270 + Math.sin(index * 1.2) * 22
    }));
  }

  private routeGoalPoint() {
    if (this.isNativeSkinRoute()) {
      const route = this.contentManifest.mountainRoute;
      if (route?.summit) return routePointToCanvas(route.summit, WIDTH, HEIGHT);
    }
    if (this.sceneConfig.current_mode === "direction_pair") return { x: 858, y: 248 };
    return this.nodePoints()[this.nodePoints().length - 1];
  }

  private actorYForRoutePoint(point: RoutePoint) {
    if (!this.isNativeSkinRoute()) return point.y - 40;
    return point.y + (this.contentManifest.heroSprite?.footOffsetY || 0);
  }

  private currentStartPoint(): PlatformPoint {
    if (this.isNativeSkinRoute()) {
      const step = this.levelSteps[this.system.state.currentRound % this.levelSteps.length];
      const point = routePointToCanvas(step?.start || { x: 0.2, y: 0.74 }, WIDTH, HEIGHT);
      return { x: point.x, y: point.y, width: 86, label: "", direction: this.system.state.actorLane };
    }
    const progress = this.system.state.currentRound / Math.max(1, this.sceneConfig.pitch_rounds.length);
    const x = 112 + progress * 548;
    const y = this.laneY(this.system.state.actorLane);
    return { x, y, width: 128, label: "", direction: this.system.state.actorLane };
  }

  private directionPlatforms(): PlatformPoint[] {
    const start = this.currentStartPoint();
    const currentStep = this.levelSteps[this.system.state.currentRound % this.levelSteps.length];
    if (this.isNativeSkinRoute() && currentStep) {
      return (["higher", "same", "lower"] as DirectionChoice[]).map((direction) => {
        const point = routePointToCanvas(currentStep.choices[direction], WIDTH, HEIGHT);
        return { x: point.x, y: point.y, width: 92, label: "", direction };
      });
    }
    const nextX = Math.min(810, start.x + 210);
    const lanes = { higher: 196, same: 312, lower: 424 };
    return (["higher", "same", "lower"] as DirectionChoice[]).map((direction) => ({
      x: nextX,
      y: lanes[direction],
      width: 138,
      label: pitchDirectionGlyph(direction),
      direction
    }));
  }

  private actorFootY(point: PlatformPoint) {
    if (!this.isNativeSkinRoute()) return point.y - 52;
    return point.y + (this.contentManifest.heroSprite?.footOffsetY || 0);
  }

  private debugNativeRoutePoint(point: PlatformPoint, color: number) {
    if (!DEBUG_NATIVE_ROUTE_POINTS) return;
    const y = this.actorFootY(point);
    this.graphics.lineStyle(2, color, 0.9);
    this.graphics.lineBetween(point.x - 10, y, point.x + 10, y);
    this.graphics.lineBetween(point.x, y - 10, point.x, y + 10);
    this.graphics.strokeCircle(point.x, y, 8);
  }

  private isNativeSkinRoute() {
    return usesNativePitchLadderMapRoute(this.sceneConfig.skin_play_mode, this.sceneConfig.route_style);
  }

  private laneY(direction: DirectionChoice) {
    return { higher: 196, same: 312, lower: 424 }[direction];
  }

  private expectedDirection(): DirectionChoice {
    const answer = String(this.currentPitchRound().answer || "higher");
    return isPitchDirection(answer) ? answer : "higher";
  }

  private currentPitchRound() {
    return this.system.currentRound();
  }

  private currentSequence() {
    return (this.currentPitchRound().sequence || []).map(String);
  }

  private titleForSkin() {
    return {
      mountain: "音高山路",
      cloud: "云梯升空",
      bamboo: "竹节爬梯",
      lantern: "灯塔点灯"
    }[this.sceneConfig.skin_play_mode];
  }

  private snapshot(): PitchLadderSnapshot {
    const round = this.currentPitchRound();
    const state = this.system.state;
    return {
      status: state.status,
      currentRound: state.currentRound,
      totalRounds: this.sceneConfig.pitch_rounds.length,
      currentMode: this.sceneConfig.current_mode,
      sequence: (round.sequence || []).map(String),
      labels: (round.labels || round.sequence || []).map(String),
      answer: Array.isArray(round.answer) ? round.answer.map(String) : String(round.answer || ""),
      selected: [...state.selected],
      progress: state.cleared / Math.max(1, this.sceneConfig.pitch_rounds.length),
      cleared: state.cleared,
      rewardsCollected: state.cleared,
      rewardTotal: this.sceneConfig.reward_model.tokens_required,
      rewardTokenName: this.sceneConfig.reward_model.token_name,
      mistakes: state.mistakes,
      mistakeLimit: this.sceneConfig.mistake_limit,
      energy: state.energy,
      energyMax: this.sceneConfig.energy_max,
      skinObjective: this.titleForSkin(),
      audioMode: this.sceneConfig.audio_mode,
      audioLabel: this.sceneConfig.audio_mode === "lesson_audio" ? "作品片段" : "内置音高",
      lastJudgement: state.lastJudgement,
      message: state.message
    };
  }

  private emit(type: PitchLadderSceneEvent["type"], judgement?: PitchLadderJudgement, message?: string) {
    this.onSceneEvent({ type, judgement, message, snapshot: this.snapshot() });
  }
}

function normalizeRequiredConfig(config: PitchLadderSceneConfig): NormalizedPitchLadderSceneConfig {
  const built = buildPitchLadderSceneConfig(config as Record<string, unknown>);
  return {
    engine: "phaser_2d",
    scene_id: "pitch_ladder_scene",
    runtime_shell: "pitch_ladder_map_shell",
    game_feel: "map_pitch_climb",
    skin_id: built.skin_id || "mountain_steps",
    skin_play_mode: built.skin_play_mode || "mountain",
    mode: built.mode || "high_low_steps",
    current_mode: built.current_mode || "direction_pair",
    target_pattern_type: built.target_pattern_type || "direction_pair",
    music_elements: built.music_elements || normalizeMusicElements(undefined, built.pitch_range || ["do", "re", "mi", "sol", "la"], built.current_mode || "direction_pair"),
    pitch_range: built.pitch_range || ["do", "re", "mi", "sol", "la"],
    pitch_rounds: built.pitch_rounds || [],
    route_nodes: built.route_nodes || [],
    pitch_path: built.pitch_path || [],
    energy_max: built.energy_max || 100,
    mistake_limit: built.mistake_limit || 3,
    sing_back_required: built.sing_back_required !== false,
    audio_mode: built.audio_mode || "hybrid",
    audio_assets: normalizeAudioAssets(built.audio_assets),
    input_map: built.input_map || { primary: "Space", pointer: true },
    fx_profile: normalizeFxProfile(built.fx_profile),
    map_hud: true,
    adventure_hud: true,
    show_mission_ribbon_in_play: false,
    route_objective: built.route_objective || "summit",
    copy_budget: normalizeCopyBudget(built.copy_budget),
    character_profile: normalizeCharacterProfile(built.character_profile),
    reward_model: normalizeRewardModel(built.reward_model, built.pitch_rounds?.length || 1),
    fail_pressure_model: normalizeFailPressureModel(built.fail_pressure_model),
    content_manifest: built.content_manifest || undefined,
    route_style: built.route_style || "map_native",
    movement_profile: built.movement_profile || "walk_arc",
    hint_density: built.hint_density || "low",
    show_teacher_text_in_play: false
  };
}

function normalizeContentManifest(value: Partial<PitchLadderContentManifest> | undefined, playMode: PitchLadderPlayMode): PitchLadderContentManifest {
  const fallback = PITCH_LADDER_SKIN_MANIFESTS[playMode === "lantern" ? "mountain" : playMode];
  const manifest = isRecord(value) ? value as Partial<PitchLadderContentManifest> : {};
  return {
    ...fallback,
    ...manifest,
    art: { ...(fallback.art || {}), ...(manifest.art || {}) } as PitchLadderContentManifest["art"],
    hero: { ...fallback.hero, ...(manifest.hero || {}), animations: { ...fallback.hero.animations, ...(manifest.hero?.animations || {}) } },
    environment: { ...fallback.environment, ...(manifest.environment || {}) },
    ui: { ...fallback.ui, ...(manifest.ui || {}) },
    fx: { ...fallback.fx, ...(manifest.fx || {}) },
    audio: { ...fallback.audio, ...(manifest.audio || {}) }
  };
}

function normalizeMusicElements(value: unknown, pitchRange: string[], mode: PitchLadderMode): PitchMusicElements {
  const record = isRecord(value) ? value : {};
  return {
    tonic: String(record.tonic || "C"),
    scale_type: String(record.scale_type || "major_pentatonic"),
    pitch_range: Array.isArray(record.pitch_range) ? record.pitch_range.map(String) : pitchRange,
    notes_per_round: clampNumber(Number(record.notes_per_round), 1, 5, mode === "melody_path" ? 3 : 2),
    round_count: clampNumber(Number(record.round_count), 1, 12, 6),
    direction_mix: isRecord(record.direction_mix) ? record.direction_mix as Record<string, number> : { higher: 0.4, same: 0.2, lower: 0.4 },
    step_skip_mix: isRecord(record.step_skip_mix) ? record.step_skip_mix as Record<string, number> : { step: 0.75, skip: 0.25 },
    show_solfege_hint: record.show_solfege_hint !== false,
    audio_mode: normalizeAudioMode(record.audio_mode),
    sing_back_required: record.sing_back_required !== false
  };
}

function normalizePitchRange(value: unknown): string[] {
  const fallback = ["do", "re", "mi", "sol", "la"];
  if (!Array.isArray(value)) return fallback;
  const notes = value.map(String).filter(Boolean);
  return notes.length >= 2 ? notes : fallback;
}

function normalizeRouteNodes(value: unknown, pitchRange: string[]): PitchRouteNode[] {
  if (Array.isArray(value) && value.length) {
    return value.map((item, index) => {
      const record = isRecord(item) ? item : {};
      const note = String(record.note || record.id || pitchRange[index] || `n${index}`);
      return {
        id: String(record.id || note),
        note,
        label: String(record.label || noteLabel(note)),
        midi_offset: Number(record.midi_offset ?? pitchMidiOffset(note)),
        level: Number(record.level || index),
        height: Number(record.height ?? index / Math.max(1, pitchRange.length - 1))
      };
    });
  }
  return pitchRange.map((note, index) => ({
    id: note,
    note,
    label: noteLabel(note),
    midi_offset: pitchMidiOffset(note),
    level: index,
    height: index / Math.max(1, pitchRange.length - 1)
  }));
}

function normalizeRounds(value: unknown, pitchRange: string[]): PitchRound[] {
  if (Array.isArray(value) && value.length) {
    return value.map((item, index) => {
      const record = isRecord(item) ? item : {};
      const sequence = Array.isArray(record.sequence) ? record.sequence.map(String) : pitchRange.slice(0, 2);
      return {
        id: String(record.id || `p${index + 1}`),
        sequence,
        labels: Array.isArray(record.labels) ? record.labels.map(String) : sequence.map(noteLabel),
        midi_offsets: Array.isArray(record.midi_offsets) ? record.midi_offsets.map(Number) : sequence.map(pitchMidiOffset),
        answer: Array.isArray(record.answer) ? record.answer.map(String) : String(record.answer || "higher")
      };
    });
  }
  return [{ id: "p1", sequence: pitchRange.slice(0, 2), labels: pitchRange.slice(0, 2).map(noteLabel), midi_offsets: [0, 2], answer: "higher" }];
}

function normalizeMode(value: unknown, pattern: unknown, mode: unknown): PitchLadderMode {
  const candidate = String(value || pattern || mode || "");
  if (candidate === "single_solfege" || candidate === "solfege_ladder") return "single_solfege";
  if (candidate === "melody_path" || candidate === "melody_climb") return "melody_path";
  return "direction_pair";
}

function pitchDirectionGlyph(direction: PitchDirection) {
  return {
    higher: "↑",
    same: "平",
    lower: "↓"
  }[direction];
}

function normalizePlayMode(value: unknown, skinId: string): PitchLadderPlayMode {
  const candidate = String(value || "");
  if (candidate === "mountain" || candidate === "cloud" || candidate === "bamboo" || candidate === "lantern") return candidate;
  if (skinId === "cloud_elevator") return "cloud";
  if (skinId === "bamboo_ladder") return "bamboo";
  if (skinId === "lantern_tower") return "lantern";
  return "mountain";
}

function normalizeRouteObjective(value: unknown, playMode: PitchLadderPlayMode) {
  const candidate = String(value || "");
  if (candidate === "summit" || candidate === "cloud_gate" || candidate === "bamboo_crown" || candidate === "lantern_beacon") return candidate;
  return {
    mountain: "summit",
    cloud: "cloud_gate",
    bamboo: "bamboo_crown",
    lantern: "lantern_beacon"
  }[playMode] as Required<PitchLadderSceneConfig>["route_objective"];
}

function normalizeRouteStyle(value: unknown): Required<PitchLadderSceneConfig>["route_style"] {
  return value === "floating_platforms" ? "floating_platforms" : "map_native";
}

function normalizeAudioMode(value: unknown): PitchLadderAudioMode {
  const candidate = String(value || "hybrid");
  if (candidate === "internal_pitch" || candidate === "lesson_audio" || candidate === "hybrid") return candidate;
  return "hybrid";
}

function normalizeAudioAssets(value: unknown): GameAudioAssetConfig {
  const record = isRecord(value) ? value : {};
  const sfx = isRecord(record.sfx) ? record.sfx : {};
  const audioAssets: GameAudioAssetConfig = {
    sfx: {}
  };
  Object.entries(sfx).forEach(([key, source]) => {
    if (typeof source === "string" && source) audioAssets.sfx![key] = source;
  });
  return audioAssets;
}

function normalizeCopyBudget(value: unknown) {
  const record = isRecord(value) ? value : {};
  return {
    objective_max_chars: clampNumber(Number(record.objective_max_chars), 8, 36, 18),
    feedback_max_chars: clampNumber(Number(record.feedback_max_chars), 4, 16, 8)
  };
}

function normalizeCharacterProfile(value: unknown): CharacterProfile {
  const record = isRecord(value) ? value : {};
  return {
    role: String(record.role || "旋律探险家"),
    idle_animation: String(record.idle_animation || "bounce_ready"),
    success_animation: String(record.success_animation || "flag_cheer"),
    fail_animation: String(record.fail_animation || "slide_back")
  };
}

function normalizeRewardModel(value: unknown, totalRounds: number): RewardModel {
  const record = isRecord(value) ? value : {};
  return {
    token_name: String(record.token_name || "旋律宝石"),
    tokens_required: clampNumber(Number(record.tokens_required), 1, 12, totalRounds),
    final_reward_animation: String(record.final_reward_animation || "summit_flag")
  };
}

function normalizeFailPressureModel(value: unknown): FailPressureModel {
  const record = isRecord(value) ? value : {};
  return {
    energy_loss_animation: String(record.energy_loss_animation || "heart_drop"),
    route_damage_animation: String(record.route_damage_animation || "crack_flash"),
    quick_retry: record.quick_retry !== false
  };
}

function normalizeInputMap(value: unknown) {
  const record = isRecord(value) ? value : {};
  return { primary: String(record.primary || "Space"), pointer: record.pointer !== false };
}

function normalizeFxProfile(value: unknown): FxProfile {
  const record = isRecord(value) ? value : {};
  return {
    step: String(record.step || "route_glow"),
    miss: String(record.miss || "map_shake"),
    success: String(record.success || "summit_finish")
  };
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

function pitchMidiOffset(note: string) {
  return resolvePitchToken(note)?.semitone ?? 0;
}

function clampNumber(value: number, min: number, max: number, fallback: number) {
  if (!Number.isFinite(value)) return fallback;
  return Math.max(min, Math.min(max, Math.round(value)));
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return Boolean(value && typeof value === "object" && !Array.isArray(value));
}
