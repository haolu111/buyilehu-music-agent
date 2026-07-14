import Phaser from "phaser";
import { TemplateCharacterPresenter } from "./templateCharacterPresenter";
import { templateVisualPackForConfig } from "./templateVisualAssets";
import type { TemplatePoseKey, TemplateVisualPack } from "./types";

export type FormTreasurePlayMode = "map" | "constellation" | "gallery" | "train" | "stage";
export type FormTreasureStatus = "ready" | "listening" | "verified" | "success" | "failed";
export type FormTreasureAudioMode = "internal_form" | "lesson_audio" | "hybrid";

export type FormTimelineSegment = {
  id: string;
  label: string;
  name?: string;
  bars?: number;
  start_bar?: number;
  midi_offsets?: number[];
  hint?: string;
};

export type FormStructureCard = {
  id: string;
  label: string;
  name?: string;
  description?: string;
};

export type FormProgressModel = {
  total_steps?: number;
  reward?: string;
};

export type FormTreasureToolId = "compass" | "scroll" | "key";
export type FormTreasureScenePhase = "idle" | "listening" | "placing" | "hint" | "success" | "failed";

export type FormTreasureSceneConfig = {
  engine?: "phaser_2d";
  scene_id?: "form_treasure_scene";
  runtime_shell?: "form_treasure_shell";
  game_feel?: "form_treasure_hunt";
  skin_id?: string;
  skin_play_mode?: FormTreasurePlayMode;
  mode?: string;
  form_type?: string;
  section_length_bars?: number;
  hint_mode?: "guided" | "partial" | "challenge";
  timeline_segments?: FormTimelineSegment[];
  structure_cards?: FormStructureCard[];
  answer_pattern?: string[];
  progress_model?: FormProgressModel;
  audio_mode?: FormTreasureAudioMode;
  allow_relisten?: boolean;
  form_hud?: boolean;
  show_teacher_text_in_play?: boolean;
  asset_manifest?: TemplateVisualPack;
};

export type FormTreasureSnapshot = {
  status: FormTreasureStatus;
  currentSegment: number;
  totalSegments: number;
  selectedPattern: string[];
  answerPattern: string[];
  routeSlots: string[];
  activeSegment: number;
  activeTool: FormTreasureToolId | null;
  score: number;
  stars: number;
  revealedClues: string[];
  scenePhase: FormTreasureScenePhase;
  fxQueue: string[];
  progress: number;
  attempts: number;
  hintMode: "guided" | "partial" | "challenge";
  formType: string;
  skinObjective: string;
  message: string;
};

export type FormTreasureSceneEvent = {
  type: "listen_segment" | "select_card" | "place_card" | "remove_card" | "use_tool" | "verify" | "mission_success" | "mission_failed" | "reset";
  snapshot: FormTreasureSnapshot;
  message?: string;
};

export type FormTreasureController = {
  listenSegment: (index: number) => void;
  previewPattern: (pattern: string[]) => void;
  placeCard: (slotIndex: number, label: string) => void;
  removeCard: (slotIndex: number) => void;
  useTool: (toolId: FormTreasureToolId) => void;
  setActiveCard: (label: string | null) => void;
  verifyPattern: (pattern: string[], correct: boolean) => void;
  reset: () => void;
  destroy: () => void;
};

const WIDTH = 960;
const HEIGHT = 540;
const BACKGROUND_ASSET_KEY = "form_treasure_template_bg";
const HERO_ASSET_KEYS: Record<TemplatePoseKey, string> = {
  idle: "form_treasure_pose_idle",
  action: "form_treasure_pose_action",
  miss: "form_treasure_pose_miss",
  win: "form_treasure_pose_win"
};
const PROP_ASSET_KEYS = Array.from({ length: 12 }, (_, index) => `form_treasure_prop_${index + 1}`);
const REWARD_ASSET_KEYS = Array.from({ length: 12 }, (_, index) => `form_treasure_reward_${index + 1}`);
const TOOL_PROPS: Record<FormTreasureToolId, number> = { scroll: 0, compass: 1, key: 10 };
const CHEST_PROP_INDEX = 2;

const palettes: Record<FormTreasurePlayMode, { bg: number; land: number; route: number; accent: number; glow: number; ink: string }> = {
  map: { bg: 0xf2d59b, land: 0x6f8b4d, route: 0x8d5524, accent: 0xd9a441, glow: 0xfff0a6, ink: "#3e2a16" },
  constellation: { bg: 0x102543, land: 0x243a78, route: 0x86d9ff, accent: 0xffd166, glow: 0xf8f2ff, ink: "#f8f2ff" },
  gallery: { bg: 0xefe7dc, land: 0xb48d66, route: 0x7a5131, accent: 0xc96f4a, glow: 0xffe0a3, ink: "#3d2f27" },
  train: { bg: 0x8cc7d8, land: 0x4f6b7b, route: 0xd74f35, accent: 0xffca55, glow: 0xfff4b8, ink: "#20323a" },
  stage: { bg: 0x251733, land: 0x6d2d54, route: 0xf0b35a, accent: 0xff6575, glow: 0xffe0a8, ink: "#fff3da" }
};

export function buildFormTreasureSceneConfig(raw: Record<string, unknown>): FormTreasureSceneConfig {
  const nested = isRecord(raw.scene_config) ? raw.scene_config : {};
  const merged = { ...raw, ...nested };
  const formType = String(merged.form_type || "ABA");
  const answerPattern = normalizeAnswerPattern(merged.answer_pattern, formType);
  return {
    engine: "phaser_2d",
    scene_id: "form_treasure_scene",
    runtime_shell: "form_treasure_shell",
    game_feel: "form_treasure_hunt",
    skin_id: String(merged.skin_id || "treasure_map"),
    skin_play_mode: normalizePlayMode(merged.skin_play_mode, merged.skin_id),
    mode: String(merged.mode || "aba_treasure"),
    form_type: formType,
    section_length_bars: clampNumber(Number(merged.section_length_bars), 4, 16, 8),
    hint_mode: normalizeHintMode(merged.hint_mode),
    timeline_segments: normalizeSegments(merged.timeline_segments, answerPattern),
    structure_cards: normalizeCards(merged.structure_cards, answerPattern),
    answer_pattern: answerPattern,
    progress_model: isRecord(merged.progress_model) ? merged.progress_model as FormProgressModel : { total_steps: answerPattern.length, reward: "结构宝藏" },
    audio_mode: normalizeAudioMode(merged.audio_mode),
    allow_relisten: merged.allow_relisten !== false,
    form_hud: true,
    show_teacher_text_in_play: false,
    asset_manifest: templateVisualPackForConfig(merged, "form_treasure_core")
  };
}

export function mountFormTreasureScene(
  parent: HTMLElement,
  config: FormTreasureSceneConfig,
  onEvent: (event: FormTreasureSceneEvent) => void
): FormTreasureController {
  const built = buildFormTreasureSceneConfig(config as Record<string, unknown>);
  const scene = new FormTreasureScene(built, onEvent);
  const game = new Phaser.Game({
    type: Phaser.AUTO,
    parent,
    width: WIDTH,
    height: HEIGHT,
    backgroundColor: palettes[built.skin_play_mode || "map"].bg,
    scale: {
      mode: Phaser.Scale.FIT,
      autoCenter: Phaser.Scale.CENTER_BOTH
    },
    scene: [scene]
  });

  return {
    listenSegment: (index) => scene.listenSegment(index),
    previewPattern: (pattern) => scene.previewPattern(pattern),
    placeCard: (slotIndex, label) => scene.placeCard(slotIndex, label),
    removeCard: (slotIndex) => scene.removeCard(slotIndex),
    useTool: (toolId) => scene.useTool(toolId),
    setActiveCard: (label) => scene.setActiveCard(label),
    verifyPattern: (pattern, correct) => scene.verifyPattern(pattern, correct),
    reset: () => scene.resetMission(),
    destroy: () => game.destroy(true)
  };
}

class FormTreasureScene extends Phaser.Scene {
  private readonly sceneConfig: Required<FormTreasureSceneConfig>;
  private readonly onSceneEvent: (event: FormTreasureSceneEvent) => void;
  private graphics!: Phaser.GameObjects.Graphics;
  private titleText!: Phaser.GameObjects.Text;
  private statusText!: Phaser.GameObjects.Text;
  private clueText!: Phaser.GameObjects.Text;
  private cursor!: Phaser.GameObjects.Container;
  private treasure!: Phaser.GameObjects.Container;
  private selectedPattern: string[];
  private routeSlots: string[];
  private currentSegment = 0;
  private status: FormTreasureStatus = "ready";
  private attempts = 0;
  private message = "听段落，排结构";
  private activeTool: FormTreasureToolId | null = null;
  private activeCard: string | null = null;
  private revealedClues: string[] = [];
  private fxQueue: string[] = [];
  private backgroundImage: Phaser.GameObjects.Image | null = null;
  private heroPresenter: TemplateCharacterPresenter | null = null;
  private propImages: Phaser.GameObjects.Image[] = [];
  private rewardImages: Phaser.GameObjects.Image[] = [];

  constructor(config: FormTreasureSceneConfig, onEvent: (event: FormTreasureSceneEvent) => void) {
    super("form_treasure_scene");
    this.sceneConfig = normalizeRequiredConfig(config);
    this.onSceneEvent = onEvent;
    this.selectedPattern = [];
    this.routeSlots = emptyRouteSlots(this.sceneConfig.answer_pattern.length);
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
    const palette = palettes[this.sceneConfig.skin_play_mode];
    this.titleText = this.add.text(34, 24, "曲式藏宝图", {
      fontFamily: "Noto Sans SC, PingFang SC, Arial, sans-serif",
      fontSize: "26px",
      color: palette.ink,
      fontStyle: "bold"
    });
    this.statusText = this.add.text(38, 66, this.message, {
      fontFamily: "Arial, sans-serif",
      fontSize: "18px",
      color: palette.ink
    });
    this.clueText = this.add.text(38, 92, "点段落岛复听，放结构卡连桥。", {
      fontFamily: "Noto Sans SC, PingFang SC, Arial, sans-serif",
      fontSize: "15px",
      color: palette.ink
    }).setAlpha(0.86);
    this.cursor = this.add.container(0, 0);
    this.cursor.add(this.add.circle(0, 0, 18, palette.glow));
    this.cursor.add(this.add.triangle(0, -6, -9, 8, 9, 8, 0, 0, palette.accent));
    this.heroPresenter = new TemplateCharacterPresenter(this, {
      poseKeys: HERO_ASSET_KEYS,
      x: 154,
      y: 394,
      displaySize: 190,
      depth: 12,
      reducedMotion: prefersReducedMotion(),
      preserveAspectRatio: true
    });
    this.treasure = this.add.container(WIDTH - 106, HEIGHT - 112).setDepth(5);
    if (this.textures.exists(PROP_ASSET_KEYS[CHEST_PROP_INDEX])) {
      this.treasure.add(this.add.image(0, 0, PROP_ASSET_KEYS[CHEST_PROP_INDEX]).setDisplaySize(102, 102));
    } else {
      this.treasure.add(this.add.rectangle(0, 0, 72, 48, palette.accent, 0.95).setStrokeStyle(4, palette.route));
      this.treasure.add(this.add.rectangle(0, -24, 78, 16, palette.glow, 0.95).setStrokeStyle(3, palette.route));
    }
    this.treasure
      .setSize(118, 108)
      .setInteractive(new Phaser.Geom.Rectangle(-59, -54, 118, 108), Phaser.Geom.Rectangle.Contains)
      .on("pointerdown", () => this.openTreasure());
    this.propImages = PROP_ASSET_KEYS
      .filter((key) => this.textures.exists(key))
      .map((key, index) => {
        const positions = this.toolPositions();
        const point = positions[index] || { x: 734 + (index % 4) * 56, y: 130 + Math.floor(index / 4) * 54 };
        const size = toolIdForPropIndex(index) ? 72 : index === CHEST_PROP_INDEX ? 64 : 50;
        const image = this.add.image(point.x, point.y, key).setDepth(3).setDisplaySize(size, size).setAlpha(index === CHEST_PROP_INDEX ? 0.38 : 0.72);
        const toolId = toolIdForPropIndex(index);
        image.setInteractive({ useHandCursor: true }).on("pointerdown", () => toolId ? this.useTool(toolId) : this.inspectProp(index));
        return image;
      });
    this.rewardImages = REWARD_ASSET_KEYS
      .filter((key) => this.textures.exists(key))
      .map((key, index) => this.add.image(WIDTH - 118 + (index % 3) * 18, HEIGHT - 126 + Math.floor(index / 3) * 14, key).setDepth(6).setDisplaySize(54, 54).setAlpha(0).setVisible(false));
    this.drawScene();
    this.placeCursor(0, false);
    this.emit("reset");
  }

  listenSegment(index: number) {
    const maxIndex = this.sceneConfig.timeline_segments.length - 1;
    this.currentSegment = clampNumber(index, 0, maxIndex, 0);
    this.status = "listening";
    this.message = `${this.sceneConfig.timeline_segments[this.currentSegment]?.label || "段落"} 正在播放`;
    this.fxQueue = ["segment_listen"];
    this.activeTool = null;
    this.addClue(this.currentSegment);
    this.placeCursor(this.currentSegment, true);
    this.playListenFx(this.currentSegment);
    this.drawScene();
    this.emit("listen_segment");
  }

  previewPattern(pattern: string[]) {
    this.routeSlots = normalizeSlots(pattern, this.sceneConfig.answer_pattern.length);
    this.selectedPattern = filledSlots(this.routeSlots);
    this.status = "ready";
    this.activeTool = null;
    this.message = this.selectedPattern.length ? `路线：${this.selectedPattern.join(" - ")}` : "选择结构卡";
    this.fxQueue = this.selectedPattern.length ? ["card_place"] : [];
    this.drawScene();
    this.emit("select_card");
  }

  placeCard(slotIndex: number, label: string) {
    if (this.status === "success") return;
    const index = clampNumber(slotIndex, 0, this.routeSlots.length - 1, 0);
    this.routeSlots[index] = String(label || "").toUpperCase();
    this.selectedPattern = filledSlots(this.routeSlots);
    this.activeCard = null;
    this.status = "ready";
    this.message = `${this.routeSlots[index]} 卡放到第 ${index + 1} 座岛`;
    this.fxQueue = ["card_place", "bridge_light"];
    this.placeCursor(index, true);
    this.playCardPlaceFx(index);
    this.drawScene();
    this.emit("place_card");
  }

  removeCard(slotIndex: number) {
    const index = clampNumber(slotIndex, 0, this.routeSlots.length - 1, this.routeSlots.length - 1);
    this.routeSlots[index] = "";
    this.selectedPattern = filledSlots(this.routeSlots);
    this.status = "ready";
    this.message = this.selectedPattern.length ? "撤回一张结构卡" : "选择结构卡";
    this.fxQueue = ["card_remove"];
    this.drawScene();
    this.emit("remove_card");
  }

  useTool(toolId: FormTreasureToolId) {
    this.activeTool = toolId;
    this.status = "ready";
    this.addClue(this.currentSegment);
    this.message = toolMessage(toolId, this.sceneConfig.timeline_segments[this.currentSegment]);
    this.fxQueue = ["tool_hint"];
    this.playToolFx(toolId);
    this.drawScene();
    this.emit("use_tool");
  }

  setActiveCard(label: string | null) {
    this.activeCard = label ? label.toUpperCase() : null;
    this.drawScene();
  }

  verifyPattern(pattern: string[], correct: boolean) {
    this.routeSlots = normalizeSlots(pattern, this.sceneConfig.answer_pattern.length);
    this.selectedPattern = filledSlots(this.routeSlots);
    this.attempts += 1;
    this.status = correct ? "success" : "failed";
    this.message = correct ? "宝藏路线点亮" : "路线还不对";
    this.fxQueue = correct ? ["treasure_unlock"] : ["wrong_route_smoke"];
    this.drawScene();
    if (correct) {
      this.playStageClearFx();
      this.emit("mission_success");
    } else {
      this.playMissFx();
      this.emit("mission_failed");
    }
  }

  openTreasure() {
    const complete = this.routeSlots.every(Boolean);
    if (!complete) {
      this.activeTool = "key";
      this.message = "宝箱还缺完整路线";
      this.fxQueue = ["tool_hint"];
      this.playToolFx("key");
      this.drawScene();
      this.emit("use_tool");
      return;
    }
    const correct = this.routeSlots.every((item, index) => item === this.sceneConfig.answer_pattern[index]);
    this.verifyPattern(this.routeSlots, correct);
  }

  resetMission() {
    this.status = "ready";
    this.currentSegment = 0;
    this.selectedPattern = [];
    this.routeSlots = emptyRouteSlots(this.sceneConfig.answer_pattern.length);
    this.attempts = 0;
    this.message = "听段落，排结构";
    this.activeTool = null;
    this.activeCard = null;
    this.revealedClues = [];
    this.fxQueue = [];
    this.placeCursor(0, true);
    this.drawScene();
    this.emit("reset");
  }

  private playStageClearFx() {
    this.tweens.add({ targets: this.treasure, y: this.treasure.y - 28, scale: 1.18, yoyo: true, duration: 360 });
    this.cameras.main.flash(360, 255, 230, 150);
    const label = this.add.text(480, 164, "宝箱开启", {
      color: "#5b3716",
      fontFamily: "Noto Sans SC, PingFang SC, sans-serif",
      fontSize: "44px",
      fontStyle: "bold"
    }).setOrigin(0.5);
    for (let index = 0; index < 12; index += 1) {
      const dot = this.add.circle(this.treasure.x, this.treasure.y, 7, index % 2 ? 0xffd15c : 0x4e8066, 0.92);
      this.tweens.add({
        targets: dot,
        x: this.treasure.x + Math.cos((index / 12) * Math.PI * 2) * 170,
        y: this.treasure.y + Math.sin((index / 12) * Math.PI * 2) * 96,
        alpha: 0,
        duration: 640,
        ease: "Cubic.Out",
        onComplete: () => dot.destroy()
      });
    }
    this.rewardImages.forEach((image, index) => {
      image.setVisible(true).setAlpha(0).setScale(0.64);
      this.tweens.add({
        targets: image,
        alpha: { from: 0, to: 0.95 },
        x: WIDTH - 118 + Math.cos(index) * (42 + index * 6),
        y: HEIGHT - 126 + Math.sin(index * 1.7) * (34 + index * 4),
        scale: 0.86,
        yoyo: true,
        duration: 720,
        delay: index * 24,
        ease: "Back.Out"
      });
    });
    this.tweens.add({ targets: label, scale: 1.16, alpha: 0, duration: 760, ease: "Back.Out", onComplete: () => label.destroy() });
  }

  private playMissFx() {
    this.cameras.main.shake(180, 0.01);
    const label = this.add.text(480, 164, "路线再查", {
      color: "#8d3428",
      fontFamily: "Noto Sans SC, PingFang SC, sans-serif",
      fontSize: "34px",
      fontStyle: "bold"
    }).setOrigin(0.5);
    this.tweens.add({ targets: label, y: 130, alpha: 0, duration: 540, ease: "Cubic.Out", onComplete: () => label.destroy() });
  }

  private drawScene() {
    const palette = palettes[this.sceneConfig.skin_play_mode];
    const hasSceneArt = Boolean(this.backgroundImage);
    this.graphics.clear();
    this.drawWorld(palette);
    const nodes = this.nodePositions();
    if (!hasSceneArt) {
      this.graphics.lineStyle(14, palette.route, 0.18);
      for (let index = 0; index < nodes.length - 1; index += 1) {
        this.graphics.lineBetween(nodes[index].x, nodes[index].y, nodes[index + 1].x, nodes[index + 1].y);
      }
      this.graphics.lineStyle(7, palette.route, 0.72);
    }
    for (let index = 0; index < nodes.length - 1; index += 1) {
      const lit = this.status === "success" || Boolean(this.routeSlots[index] && this.routeSlots[index + 1]);
      if (hasSceneArt && !lit) continue;
      this.graphics.lineStyle(lit ? (hasSceneArt ? 5 : 9) : 5, lit ? palette.glow : palette.route, lit ? 0.86 : 0.5);
      this.graphics.lineBetween(nodes[index].x, nodes[index].y, nodes[index + 1].x, nodes[index + 1].y);
    }
    nodes.forEach((point, index) => {
      const expected = this.sceneConfig.answer_pattern[index] || "?";
      const selected = this.routeSlots[index];
      const solved = this.status === "success";
      const active = index === this.currentSegment;
      const hoverReady = Boolean(this.activeCard && !selected);
      const nodePropIndex = 4 + (index % 4);
      if (hasSceneArt) {
        const radius = active ? 28 : 23;
        this.graphics.fillStyle(0x1f1308, active ? 0.2 : 0.12);
        this.graphics.fillCircle(point.x + 4, point.y + 8, radius + 7);
        this.graphics.fillStyle(solved || selected ? palette.glow : 0xfff4bf, solved || selected ? 0.9 : 0.7);
        this.graphics.lineStyle(active ? 5 : hoverReady ? 4 : 2, active ? palette.accent : hoverReady ? palette.glow : 0x6a4320, active || hoverReady ? 0.92 : 0.42);
        this.graphics.fillCircle(point.x, point.y, radius);
        this.graphics.strokeCircle(point.x, point.y, radius);
        this.graphics.fillStyle(palette.accent, selected ? 0.42 : 0.18);
        this.graphics.fillCircle(point.x + radius - 7, point.y - radius + 8, 7);
        this.positionNodeProp(nodePropIndex, point.x - 32, point.y - 54, active || Boolean(selected));
      } else {
        this.graphics.fillStyle(solved || selected ? palette.glow : palette.land, solved || selected ? 0.96 : 0.84);
        this.graphics.lineStyle(active ? 7 : hoverReady ? 5 : 3, active ? palette.accent : hoverReady ? palette.glow : palette.route, 1);
        this.graphics.fillEllipse(point.x, point.y, active ? 94 : 82, active ? 68 : 58);
        this.graphics.strokeEllipse(point.x, point.y, active ? 94 : 82, active ? 68 : 58);
        this.graphics.fillStyle(palette.accent, selected ? 0.28 : 0.12);
        this.graphics.fillCircle(point.x + 28, point.y - 18, 9);
        this.positionNodeProp(nodePropIndex, point.x - 34, point.y - 34, active || Boolean(selected));
      }
      this.addOrUpdateNodeHitArea(index, point.x, point.y);
      this.addOrUpdateNodeLabel(index, point.x, point.y, solved ? expected : selected || `${index + 1}`);
    });
    this.updateTemplateSprites();
    this.statusText.setText(this.message);
    this.clueText.setText(lastItem(this.revealedClues) || "点段落岛复听，放结构卡连桥。");
  }

  private drawWorld(palette: typeof palettes[FormTreasurePlayMode]) {
    if (!this.backgroundImage) {
      this.graphics.fillStyle(palette.bg, 1);
      this.graphics.fillRect(0, 0, WIDTH, HEIGHT);
    }
    this.graphics.fillStyle(palette.bg, this.backgroundImage ? 0 : 0.08).fillRoundedRect(20, 18, WIDTH - 40, HEIGHT - 36, 32);
    if (this.backgroundImage) {
      this.graphics.fillStyle(0x1b1006, 0.18).fillRoundedRect(26, 20, WIDTH - 52, 74, 18);
      this.graphics.fillStyle(0xfff3c8, 0.76).fillRoundedRect(34, 28, 386, 58, 16);
      this.graphics.lineStyle(2, 0x6f4320, 0.2).strokeRoundedRect(34, 28, 386, 58, 16);
      return;
    }
    if (this.sceneConfig.skin_play_mode === "constellation") {
      for (let index = 0; index < 42; index += 1) {
        this.graphics.fillStyle(index % 3 === 0 ? palette.glow : palette.route, 0.7);
        this.graphics.fillCircle(40 + (index * 83) % 880, 110 + (index * 47) % 320, 2 + (index % 3));
      }
    } else if (this.sceneConfig.skin_play_mode === "gallery") {
      for (let index = 0; index < 5; index += 1) {
        this.graphics.lineStyle(5, palette.land, 0.45);
        this.graphics.strokeRect(70 + index * 170, 130 + (index % 2) * 28, 112, 90);
      }
    } else if (this.sceneConfig.skin_play_mode === "train") {
      this.graphics.fillStyle(palette.land, 0.45);
      this.graphics.fillRect(0, 368, WIDTH, 64);
      this.graphics.lineStyle(5, palette.route, 0.65);
      this.graphics.lineBetween(0, 400, WIDTH, 400);
    } else if (this.sceneConfig.skin_play_mode === "stage") {
      this.graphics.fillStyle(palette.land, 0.5);
      this.graphics.fillRect(0, 0, 118, HEIGHT);
      this.graphics.fillRect(WIDTH - 118, 0, 118, HEIGHT);
      this.graphics.fillStyle(palette.accent, 0.22);
      this.graphics.fillTriangle(180, 0, 470, 420, 760, 0);
    } else {
      this.graphics.fillStyle(palette.land, 0.18);
      this.graphics.fillEllipse(490, 292, 820, 290);
      this.graphics.lineStyle(3, palette.route, 0.18);
      for (let index = 0; index < 7; index += 1) {
        this.graphics.lineBetween(80 + index * 120, 120, 40 + index * 130, 470);
      }
    }
  }

  private updateTemplateSprites() {
    const pose = this.status === "success" ? "win" : this.status === "failed" ? "miss" : this.selectedPattern.length > 0 || this.status === "listening" ? "action" : "idle";
    this.heroPresenter?.transitionTo(pose, this.status === "success" ? "success" : this.status === "failed" ? "miss" : this.status === "listening" ? "listen" : this.selectedPattern.length > 0 ? "hit" : "idle");
    this.propImages.forEach((image, index) => {
      const toolId = toolIdForPropIndex(index);
      const isRouteProp = index >= 4 && index <= 9;
      if (!isRouteProp) {
        image.setDisplaySize(this.propDisplaySize(index, toolId === this.activeTool), this.propDisplaySize(index, toolId === this.activeTool));
      }
      image.setAlpha(this.status === "success" ? 0.96 : toolId ? 0.92 : isRouteProp ? image.alpha : 0.56);
      image.setAngle(this.status === "listening" || toolId === this.activeTool ? Math.sin((this.time.now + index * 180) / 240) * 4 : 0);
    });
    this.rewardImages.forEach((image) => image.setVisible(this.status === "success" || image.alpha > 0));
  }

  private addOrUpdateNodeLabel(index: number, x: number, y: number, label: string) {
    const palette = palettes[this.sceneConfig.skin_play_mode];
    const text = this.children.getByName(`node_label_${index}`) as Phaser.GameObjects.Text | null;
    const display = label.length > 3 ? label.slice(0, 3) : label;
    if (text) {
      text.setText(display);
      text.setPosition(x, y);
      text.setStyle({
        fontFamily: "Noto Sans SC, PingFang SC, Arial, sans-serif",
        fontSize: this.backgroundImage ? "19px" : "24px",
        color: this.backgroundImage ? "#3f260f" : palette.ink,
        fontStyle: "bold",
        stroke: this.backgroundImage ? "#fff4c9" : undefined,
        strokeThickness: this.backgroundImage ? 4 : 0
      });
      return;
    }
    this.add.text(x, y, display, {
      fontFamily: "Noto Sans SC, PingFang SC, Arial, sans-serif",
      fontSize: this.backgroundImage ? "19px" : "24px",
      color: this.backgroundImage ? "#3f260f" : palette.ink,
      fontStyle: "bold",
      stroke: this.backgroundImage ? "#fff4c9" : undefined,
      strokeThickness: this.backgroundImage ? 4 : 0
    }).setName(`node_label_${index}`).setOrigin(0.5).setDepth(8);
  }

  private addOrUpdateNodeHitArea(index: number, x: number, y: number) {
    const name = `node_hit_${index}`;
    const hit = this.children.getByName(name) as Phaser.GameObjects.Zone | null;
    if (hit) {
      hit.setPosition(x, y);
      return;
    }
    this.add.zone(x, y, this.backgroundImage ? 76 : 98, this.backgroundImage ? 76 : 78)
      .setName(name)
      .setInteractive({ useHandCursor: true })
      .on("pointerdown", () => {
        if (this.activeCard) {
          this.placeCard(index, this.activeCard);
          return;
        }
        this.listenSegment(index);
      });
  }

  private nodePositions() {
    const total = Math.max(1, this.sceneConfig.timeline_segments.length);
    if (this.backgroundImage && total === 5) {
      return [
        { x: 154, y: 224 },
        { x: 350, y: 150 },
        { x: 638, y: 238 },
        { x: 774, y: 360 },
        { x: 600, y: 112 }
      ];
    }
    return this.sceneConfig.timeline_segments.map((_, index) => {
      const x = 110 + index * (740 / Math.max(total - 1, 1));
      const y = this.sceneConfig.skin_play_mode === "train"
        ? 380
        : 285 + Math.sin(index * 1.35) * 58;
      return { x, y };
    });
  }

  private placeCursor(index: number, animated: boolean) {
    const point = this.nodePositions()[index] || { x: 110, y: 285 };
    const offset = this.backgroundImage ? 38 : 58;
    if (animated) {
      this.tweens.add({ targets: this.cursor, x: point.x, y: point.y - offset, duration: 360, ease: "Back.easeOut" });
    } else {
      this.cursor.setPosition(point.x, point.y - offset);
    }
  }

  private playListenFx(index: number) {
    const point = this.nodePositions()[index] || { x: 110, y: 285 };
    const ring = this.add.circle(point.x, point.y, 44, palettes[this.sceneConfig.skin_play_mode].glow, 0).setStrokeStyle(4, palettes[this.sceneConfig.skin_play_mode].accent, 0.9).setDepth(2);
    this.tweens.add({ targets: ring, scale: 1.8, alpha: 0, duration: 620, ease: "Cubic.Out", onComplete: () => ring.destroy() });
  }

  private playCardPlaceFx(index: number) {
    const point = this.nodePositions()[index] || { x: 110, y: 285 };
    const marker = this.add.star(point.x, point.y - 44, 5, 10, 22, palettes[this.sceneConfig.skin_play_mode].accent, 0.95).setDepth(6);
    this.tweens.add({ targets: marker, y: point.y - 78, alpha: 0, scale: 1.35, duration: 560, ease: "Back.Out", onComplete: () => marker.destroy() });
  }

  private playToolFx(toolId: FormTreasureToolId) {
    const index = TOOL_PROPS[toolId];
    const image = this.propImages[index];
    if (!image) return;
    this.tweens.add({ targets: image, scale: 1.18, angle: toolId === "key" ? 12 : -12, yoyo: true, duration: 180, repeat: 1, ease: "Sine.inOut" });
  }

  private positionNodeProp(index: number, x: number, y: number, active: boolean) {
    const image = this.propImages[index];
    if (!image) return;
    image
      .setPosition(x, y)
      .setDisplaySize(active ? (this.backgroundImage ? 42 : 54) : (this.backgroundImage ? 34 : 44), active ? (this.backgroundImage ? 42 : 54) : (this.backgroundImage ? 34 : 44))
      .setAlpha(active ? 0.9 : this.backgroundImage ? 0.34 : 0.48)
      .setDepth(active ? 7 : 4);
  }

  private propDisplaySize(index: number, active: boolean) {
    if (toolIdForPropIndex(index)) return active ? 82 : 72;
    if (index === CHEST_PROP_INDEX) return 64;
    return 50;
  }

  private inspectProp(index: number) {
    if (index === CHEST_PROP_INDEX) {
      this.openTreasure();
      return;
    }
    const messages = [
      "卷轴记录主题线索",
      "指南针跟随当前段落",
      "宝箱等待完整路线",
      "路径砖会随卡片点亮",
      "段落岛记录当前位置",
      "封蜡表示一次确认",
      "珊瑚标记对比材料",
      "叶片标记主题再现",
      "桥板连接相邻段落",
      "水纹提示继续聆听",
      "钥匙检查完整路线",
      "音乐遗物是通关奖励"
    ];
    this.message = messages[index] || "这个道具会跟随寻宝状态变化";
    this.fxQueue = ["prop_touch"];
    const image = this.propImages[index];
    if (image) {
      this.tweens.add({ targets: image, scale: 1.14, yoyo: true, duration: 160, repeat: 1, ease: "Back.Out" });
    }
    this.drawScene();
    this.emit("use_tool");
  }

  private addClue(index: number) {
    const segment = this.sceneConfig.timeline_segments[index];
    const text = segment?.hint || `${segment?.label || "这一"} 段需要和前后材料比较。`;
    if (!this.revealedClues.includes(text)) {
      this.revealedClues = [...this.revealedClues, text].slice(-4);
    }
  }

  private toolPositions() {
    return [
      { x: 778, y: 84 },
      { x: 842, y: 84 },
      { x: WIDTH - 106, y: HEIGHT - 112 },
      { x: 702, y: 456 },
      { x: 162, y: 252 },
      { x: 326, y: 322 },
      { x: 488, y: 232 },
      { x: 652, y: 326 },
      { x: 812, y: 250 },
      { x: 738, y: 396 },
      { x: 882, y: 108 },
      { x: 872, y: 394 }
    ];
  }

  private emit(type: FormTreasureSceneEvent["type"]) {
    this.onSceneEvent({ type, snapshot: this.snapshot(), message: this.message });
  }

  private snapshot(): FormTreasureSnapshot {
    return {
      status: this.status,
      currentSegment: this.currentSegment,
      totalSegments: this.sceneConfig.timeline_segments.length,
      selectedPattern: [...this.selectedPattern],
      answerPattern: [...this.sceneConfig.answer_pattern],
      routeSlots: [...this.routeSlots],
      activeSegment: this.currentSegment,
      activeTool: this.activeTool,
      score: this.score(),
      stars: starsForScore(this.score(), this.status === "success"),
      revealedClues: [...this.revealedClues],
      scenePhase: this.scenePhase(),
      fxQueue: [...this.fxQueue],
      progress: this.status === "success" ? 1 : this.selectedPattern.length / Math.max(this.sceneConfig.answer_pattern.length, 1),
      attempts: this.attempts,
      hintMode: this.sceneConfig.hint_mode,
      formType: this.sceneConfig.form_type,
      skinObjective: skinObjective(this.sceneConfig.skin_play_mode),
      message: this.message
    };
  }

  private score() {
    const base = this.status === "success" ? 1000 : this.selectedPattern.length * 140;
    const penalty = this.attempts * 120 + this.revealedClues.length * 30;
    return Math.max(0, base - penalty);
  }

  private scenePhase(): FormTreasureScenePhase {
    if (this.status === "success") return "success";
    if (this.status === "failed") return "failed";
    if (this.status === "listening") return "listening";
    if (this.activeTool) return "hint";
    if (this.selectedPattern.length > 0 || this.activeCard) return "placing";
    return "idle";
  }
}

function normalizeRequiredConfig(config: FormTreasureSceneConfig): Required<FormTreasureSceneConfig> {
  const built = buildFormTreasureSceneConfig(config as Record<string, unknown>);
  return {
    ...built,
    engine: "phaser_2d",
    scene_id: "form_treasure_scene",
    runtime_shell: "form_treasure_shell",
    game_feel: "form_treasure_hunt",
    skin_id: built.skin_id || "treasure_map",
    skin_play_mode: built.skin_play_mode || "map",
    mode: built.mode || "aba_treasure",
    form_type: built.form_type || "ABA",
    section_length_bars: built.section_length_bars || 8,
    hint_mode: built.hint_mode || "partial",
    timeline_segments: built.timeline_segments || [],
    structure_cards: built.structure_cards || [],
    answer_pattern: built.answer_pattern || ["A", "B", "A"],
    progress_model: built.progress_model || { total_steps: 3, reward: "结构宝藏" },
    audio_mode: built.audio_mode || "internal_form",
    allow_relisten: built.allow_relisten !== false,
    form_hud: true,
    show_teacher_text_in_play: false,
    asset_manifest: built.asset_manifest || {}
  };
}

function normalizePlayMode(value: unknown, skinId: unknown): FormTreasurePlayMode {
  const raw = String(value || skinId || "treasure_map");
  if (raw.includes("constellation")) return "constellation";
  if (raw.includes("museum") || raw.includes("gallery")) return "gallery";
  if (raw.includes("train")) return "train";
  if (raw.includes("stage")) return "stage";
  return "map";
}

function normalizeHintMode(value: unknown): "guided" | "partial" | "challenge" {
  return value === "guided" || value === "challenge" || value === "partial" ? value : "partial";
}

function normalizeAudioMode(value: unknown): FormTreasureAudioMode {
  return value === "lesson_audio" || value === "hybrid" || value === "internal_form" ? value : "internal_form";
}

function normalizeAnswerPattern(value: unknown, formType: string) {
  if (Array.isArray(value) && value.length >= 3) return value.map((item) => String(item).toUpperCase());
  if (formType.includes("回旋")) return ["A", "B", "A", "C", "A"];
  if (formType.includes("重复")) return ["A", "A", "B", "A"];
  return ["A", "B", "A"];
}

function normalizeSegments(value: unknown, answerPattern: string[]): FormTimelineSegment[] {
  if (Array.isArray(value) && value.length) {
    return value.map((item, index) => {
      const record = isRecord(item) ? item : {};
      return {
        id: String(record.id || `segment_${index + 1}`),
        label: String(record.label || answerPattern[index] || "?"),
        name: String(record.name || `段落 ${index + 1}`),
        bars: Number(record.bars || 8),
        start_bar: Number(record.start_bar || index * 8 + 1),
        midi_offsets: Array.isArray(record.midi_offsets) ? record.midi_offsets.map(Number) : [0, 4, 7],
        hint: typeof record.hint === "string" ? record.hint : undefined
      };
    });
  }
  return answerPattern.map((label, index) => ({
    id: `segment_${index + 1}`,
    label,
    name: `${label} 段`,
    bars: 8,
    start_bar: index * 8 + 1,
    midi_offsets: label === "B" ? [2, 5, 9] : label === "C" ? [4, 7, 11] : [0, 4, 7],
    hint: label === "A" ? "主题再现" : "对比材料"
  }));
}

function normalizeCards(value: unknown, answerPattern: string[]): FormStructureCard[] {
  const unique = Array.from(new Set(answerPattern));
  if (Array.isArray(value) && value.length) {
    return value.map((item, index) => {
      const record = isRecord(item) ? item : {};
      return {
        id: String(record.id || `card_${index + 1}`),
        label: String(record.label || unique[index] || "A"),
        name: String(record.name || `${unique[index] || "A"} 段`),
        description: String(record.description || "听辨段落材料")
      };
    });
  }
  return unique.map((label) => ({
    id: `card_${label}`,
    label,
    name: `${label} 段`,
    description: label === "A" ? "熟悉主题" : "新的对比材料"
  }));
}

function skinObjective(mode: FormTreasurePlayMode) {
  if (mode === "constellation") return "点亮星图航线";
  if (mode === "gallery") return "归档音乐展品";
  if (mode === "train") return "驶过段落站台";
  if (mode === "stage") return "完成剧场分幕";
  return "找到结构宝藏";
}

function clampNumber(value: number, min: number, max: number, fallback: number) {
  if (!Number.isFinite(value)) return fallback;
  return Math.min(Math.max(value, min), max);
}

function emptyRouteSlots(total: number) {
  return Array.from({ length: Math.max(1, total) }, () => "");
}

function normalizeSlots(pattern: string[], total: number) {
  const slots = emptyRouteSlots(total);
  pattern.slice(0, total).forEach((item, index) => {
    slots[index] = String(item || "").toUpperCase();
  });
  return slots;
}

function filledSlots(slots: string[]) {
  return slots.filter(Boolean);
}

function toolIdForPropIndex(index: number): FormTreasureToolId | null {
  if (index === TOOL_PROPS.compass) return "compass";
  if (index === TOOL_PROPS.scroll) return "scroll";
  if (index === TOOL_PROPS.key) return "key";
  return null;
}

function toolMessage(toolId: FormTreasureToolId, segment?: FormTimelineSegment) {
  if (toolId === "compass") return `指南针指向：${segment?.name || "当前段落"}`;
  if (toolId === "key") return "钥匙只在路线完整时打开宝箱";
  return segment?.hint || "卷轴提示：听主题有没有回来";
}

function starsForScore(score: number, success: boolean) {
  if (!success) return score >= 300 ? 2 : 1;
  if (score >= 900) return 3;
  if (score >= 650) return 2;
  return 1;
}

function lastItem<T>(items: T[]) {
  return items.length ? items[items.length - 1] : undefined;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function prefersReducedMotion() {
  return typeof window !== "undefined" && window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
}
