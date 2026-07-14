import Phaser from "phaser";
import {
  buildCompositionPuzzleLogicConfig,
  compositionFilledSlots,
  evaluateCompositionPuzzleChecks,
  rhythmAttackCount,
  transposeNoteName,
  type CompositionConstraintCheck,
  type CompositionMeter,
  type CompositionPlacedCard,
  type CompositionPuzzleMode,
  type CompositionRhythmCard,
  type CompositionScaleType
} from "./compositionPuzzleLogic";
import { TemplateCharacterPresenter } from "./templateCharacterPresenter";
import { templateVisualPackForConfig } from "./templateVisualAssets";
import type { TemplatePoseKey, TemplateVisualPack } from "./types";

export type CompositionPuzzleStatus = "ready" | "building" | "auditioning" | "checked" | "success" | "failed";
export type { CompositionConstraintCheck, CompositionPlacedCard, CompositionPuzzleMode, CompositionRhythmCard };

export type CompositionPuzzleSceneConfig = {
  engine?: "phaser_2d";
  scene_id?: "composition_puzzle_scene";
  runtime_shell?: "composition_puzzle_shell";
  skin_id?: string;
  skin_play_mode?: "studio" | "rhythm_table" | "melody_garden";
  mode?: CompositionPuzzleMode;
  phrase_length_bars?: number;
  composition_total_bars?: number;
  composition_segment_bars?: number;
  composition_segments?: number;
  length_clamped?: boolean;
  total_slots?: number;
  segment_slots?: number;
  current_segment_index?: number;
  all_placed?: CompositionPlacedCard[];
  slots_per_bar?: number;
  meter_options?: CompositionMeter[];
  selected_meter?: CompositionMeter;
  tonic_options?: string[];
  selected_tonic?: string;
  scale_options?: CompositionScaleType[];
  selected_scale_type?: CompositionScaleType;
  playback_tonic?: string;
  constraint_profile?: "guided" | "balanced" | "challenge";
  rhythm_cards?: Array<string | CompositionRhythmCard>;
  melody_cards?: string[];
  required_elements?: string[];
  teacher_confirm_required?: boolean;
  constraint_checks?: CompositionConstraintCheck[];
  asset_manifest?: TemplateVisualPack;
};

export type CompositionPuzzleSnapshot = {
  status: CompositionPuzzleStatus;
  placed: CompositionPlacedCard[];
  segmentPlaced: CompositionPlacedCard[];
  checks: CompositionConstraintCheck[];
  progress: number;
  attempts: number;
  score: number;
  message: string;
  teacherConfirmed: boolean;
  auditioned: boolean;
  filledSlots: number;
  slotCount: number;
  segmentFilledSlots: number;
  segmentSlotCount: number;
  currentSegmentIndex: number;
  compositionSegments: number;
  totalBars: number;
  selectedSlotIndex: number;
};

export type CompositionPuzzleSceneEvent = {
  type: "place_card" | "select_slot" | "fill_pitch" | "audition" | "check" | "teacher_confirm" | "mission_success" | "mission_failed" | "reset";
  snapshot: CompositionPuzzleSnapshot;
  message?: string;
};

export type CompositionPuzzleController = {
  placeCard: (card: CompositionPlacedCard) => void;
  selectSlot: (index: number) => void;
  fillPitch: (pitch: string) => void;
  setPlaybackTonic: (tonic: string) => void;
  removeCard: (index: number) => void;
  moveCard: (fromIndex: number, toIndex: number) => void;
  undo: () => void;
  audition: (bpm?: number) => void;
  check: (teacherConfirmed?: boolean) => void;
  teacherConfirm: () => void;
  reset: () => void;
  destroy: () => void;
};

const WIDTH = 960;
const HEIGHT = 540;
const COMPOSITION_BPM_DEFAULT = 90;
const COMPOSITION_BPM_MIN = 40;
const COMPOSITION_BPM_MAX = 180;
const BACKGROUND_ASSET_KEY = "composition_puzzle_bg";
const HERO_ASSET_KEYS: Record<TemplatePoseKey, string> = {
  idle: "composition_pose_idle",
  action: "composition_pose_action",
  miss: "composition_pose_miss",
  win: "composition_pose_win"
};
const PROP_ASSET_KEYS = ["composition_prop_1", "composition_prop_2", "composition_prop_3"];
const REWARD_ASSET_KEY = "composition_reward";

const paletteByMode: Record<string, { bg: number; panel: number; card: number; accent: number; success: number; ink: string }> = {
  studio: { bg: 0xeef6f1, panel: 0xffffff, card: 0xffe2a8, accent: 0x2f6f73, success: 0x4fa66a, ink: "#18302e" },
  rhythm_table: { bg: 0xf6f0e2, panel: 0xfffbef, card: 0xf2c35b, accent: 0x8b5f2b, success: 0x4d9b72, ink: "#2f2514" },
  melody_garden: { bg: 0xf0f8ef, panel: 0xfffff7, card: 0xf2b5c6, accent: 0x376a55, success: 0x58a66b, ink: "#20382b" }
};

export function buildCompositionPuzzleSceneConfig(raw: Record<string, unknown>): CompositionPuzzleSceneConfig {
  const nested = isRecord(raw.scene_config) ? raw.scene_config : {};
  const merged = { ...raw, ...nested };
  const logic = buildCompositionPuzzleLogicConfig(merged);
  return {
    engine: "phaser_2d",
    scene_id: "composition_puzzle_scene",
    runtime_shell: "composition_puzzle_shell",
    skin_id: String(merged.skin_id || "composition_studio"),
    skin_play_mode: normalizePlayMode(merged.skin_play_mode, merged.skin_id),
    mode: logic.mode,
    phrase_length_bars: logic.phrase_length_bars,
    composition_total_bars: logic.composition_total_bars,
    composition_segment_bars: logic.composition_segment_bars,
    composition_segments: logic.composition_segments,
    length_clamped: logic.length_clamped,
    total_slots: logic.total_slots,
    segment_slots: logic.segment_slots,
    current_segment_index: Number(merged.current_segment_index || 0),
    all_placed: Array.isArray(merged.all_placed) ? merged.all_placed as CompositionPlacedCard[] : [],
    slots_per_bar: logic.slots_per_bar,
    meter_options: logic.meter_options,
    selected_meter: logic.selected_meter,
    tonic_options: logic.tonic_options,
    selected_tonic: logic.selected_tonic,
    scale_options: logic.scale_options,
    selected_scale_type: logic.selected_scale_type,
    playback_tonic: logic.playback_tonic,
    constraint_profile: logic.constraint_profile,
    rhythm_cards: logic.rhythm_cards,
    melody_cards: logic.melody_cards,
    required_elements: logic.required_elements,
    teacher_confirm_required: logic.teacher_confirm_required,
    constraint_checks: logic.constraint_checks,
    asset_manifest: templateVisualPackForConfig(merged, "composition_puzzle_core")
  };
}

export function mountCompositionPuzzleScene(
  parent: HTMLElement,
  config: CompositionPuzzleSceneConfig,
  onEvent: (event: CompositionPuzzleSceneEvent) => void
): CompositionPuzzleController {
  const built = buildCompositionPuzzleSceneConfig(config as Record<string, unknown>);
  const scene = new CompositionPuzzleScene(built, onEvent);
  const game = new Phaser.Game({
    type: Phaser.AUTO,
    parent,
    width: WIDTH,
    height: HEIGHT,
    backgroundColor: paletteByMode[built.skin_play_mode || "studio"].bg,
    scale: { mode: Phaser.Scale.FIT, autoCenter: Phaser.Scale.CENTER_BOTH },
    scene: [scene]
  });
  return {
    placeCard: (card) => scene.placeCard(card),
    selectSlot: (index) => scene.selectSlot(index),
    fillPitch: (pitch) => scene.fillPitch(pitch),
    setPlaybackTonic: (tonic) => scene.setPlaybackTonic(tonic),
    removeCard: (index) => scene.removeCard(index),
    moveCard: (fromIndex, toIndex) => scene.moveCard(fromIndex, toIndex),
    undo: () => scene.undo(),
    audition: (bpm) => scene.audition(bpm),
    check: (teacherConfirmed) => scene.check(teacherConfirmed),
    teacherConfirm: () => scene.teacherConfirm(),
    reset: () => scene.resetPuzzle(),
    destroy: () => game.destroy(true)
  };
}

class CompositionPuzzleScene extends Phaser.Scene {
  private readonly sceneConfig: Required<CompositionPuzzleSceneConfig>;
  private readonly onSceneEvent: (event: CompositionPuzzleSceneEvent) => void;
  private graphics!: Phaser.GameObjects.Graphics;
  private statusText!: Phaser.GameObjects.Text;
  private placed: CompositionPlacedCard[] = [];
  private allPlaced: CompositionPlacedCard[] = [];
  private status: CompositionPuzzleStatus = "ready";
  private attempts = 0;
  private score = 0;
  private teacherConfirmed = false;
  private auditioned = false;
  private backgroundImage: Phaser.GameObjects.Image | null = null;
  private heroPresenter: TemplateCharacterPresenter | null = null;
  private propImages: Phaser.GameObjects.Image[] = [];
  private rewardImage: Phaser.GameObjects.Image | null = null;
  private auditionIndex = -1;
  private selectedSlotIndex = -1;
  private dragGhost: Phaser.GameObjects.Container | null = null;
  private interactiveObjects: Phaser.GameObjects.GameObject[] = [];
  private notationObjects: Phaser.GameObjects.GameObject[] = [];
  private successEmitter: Phaser.GameObjects.Particles.ParticleEmitter | null = null;

  constructor(config: CompositionPuzzleSceneConfig, onEvent: (event: CompositionPuzzleSceneEvent) => void) {
    super("composition_puzzle_scene");
    this.sceneConfig = normalizeRequiredConfig(config);
    this.placed = Array.isArray(this.sceneConfig.all_placed)
      ? this.segmentPlacedFromAll(this.sceneConfig.all_placed, this.currentSegmentIndex)
      : [];
    this.allPlaced = this.composeAllPlaced(this.placed);
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
    const palette = this.palette;
    this.add.text(34, 22, "拼图创编工坊", {
      color: palette.ink,
      fontFamily: "Noto Sans SC, PingFang SC, sans-serif",
      fontSize: "24px",
      fontStyle: "bold"
    });
    this.statusText = this.add.text(36, 54, this.sceneConfig.selected_meter, {
      color: palette.ink,
      fontFamily: "Noto Sans SC, PingFang SC, sans-serif",
      fontSize: "15px",
      fontStyle: "bold"
    });
    this.heroPresenter = new TemplateCharacterPresenter(this, {
      poseKeys: HERO_ASSET_KEYS,
      x: WIDTH - 118,
      y: 170,
      displaySize: 150,
      depth: 6
    });
    this.sceneConfig.asset_manifest?.props?.slice(0, 3).forEach((_, index) => {
      const key = PROP_ASSET_KEYS[index];
      if (this.textures.exists(key)) {
        this.propImages.push(this.add.image(82 + index * 74, HEIGHT - 72, key).setDisplaySize(54, 54).setDepth(4));
      }
    });
    if (this.textures.exists(REWARD_ASSET_KEY)) {
      this.rewardImage = this.add.image(WIDTH - 82, HEIGHT - 68, REWARD_ASSET_KEY).setDisplaySize(68, 68).setDepth(7).setAlpha(0.4);
    }
    this.renderScene();
  }

  placeCard(card: CompositionPlacedCard) {
    if (this.status === "success") return;
    while (compositionFilledSlots(this.placed) + Math.max(1, Number(card.beats || 1)) > this.slotCount && this.placed.length) {
      this.placed.shift();
    }
    this.status = "building";
    this.teacherConfirmed = false;
    this.auditioned = false;
    const rhythm = card.rhythm || card.id;
    const attackCount = rhythmAttackCount(rhythm);
    this.placed.push({
      ...card,
      rhythm,
      attackCount,
      pitches: attackCount ? Array.from({ length: attackCount }, () => "") : [],
      selectedAttackIndex: 0,
      beats: Math.max(1, Number(card.beats || 1))
    });
    this.syncAllPlaced();
    this.selectedSlotIndex = this.placed.length - 1;
    this.heroPresenter?.transitionTo("action", "hit");
    this.popFloatingText("节奏入格!", 500, 244, 0x4fa66a);
    this.emitEvent("place_card", "节奏已放入轨道");
    this.renderScene();
  }

  selectSlot(index: number) {
    if (index < 0 || index >= this.placed.length) return;
    this.selectedSlotIndex = index;
    this.emitEvent("select_slot", "已选择节奏格");
    this.renderScene();
  }

  fillPitch(pitch: string) {
    if (this.status === "success") return;
    const slot = this.placed[this.selectedSlotIndex];
    if (!slot) return;
    const attackCount = rhythmAttackCount(slot.rhythm || slot.id);
    if (!attackCount) {
      this.popFloatingText("休止不用填音", 500, 244, 0xd66b4b);
      return;
    }
    const pitches = Array.from({ length: attackCount }, (_, index) => slot.pitches?.[index] || "");
    const emptyIndex = pitches.findIndex((item) => !item);
    const targetIndex = emptyIndex >= 0 ? emptyIndex : Math.max(0, Math.min(attackCount - 1, slot.selectedAttackIndex || 0));
    pitches[targetIndex] = pitch;
    this.placed[this.selectedSlotIndex] = {
      ...slot,
      pitches,
      pitch: pitches[0],
      selectedAttackIndex: Math.min(targetIndex + 1, attackCount - 1)
    };
    this.syncAllPlaced();
    this.status = "building";
    this.teacherConfirmed = false;
    this.auditioned = false;
    this.heroPresenter?.transitionTo("action", "hit");
    this.emitEvent("fill_pitch", "音名已填入节奏格");
    this.renderScene();
  }

  setPlaybackTonic(tonic: string) {
    this.sceneConfig.playback_tonic = tonic;
    this.renderScene();
  }

  removeCard(index: number) {
    if (this.status === "success") return;
    if (index < 0 || index >= this.placed.length) return;
    this.placed.splice(index, 1);
    this.syncAllPlaced();
    if (this.selectedSlotIndex >= this.placed.length) this.selectedSlotIndex = this.placed.length - 1;
    this.status = this.placed.length ? "building" : "ready";
    this.teacherConfirmed = false;
    this.auditioned = false;
    this.emitEvent("place_card", "已移除素材卡");
    this.renderScene();
  }

  moveCard(fromIndex: number, toIndex: number) {
    if (this.status === "success") return;
    if (fromIndex < 0 || fromIndex >= this.placed.length) return;
    const target = Math.min(Math.max(0, toIndex), this.placed.length - 1);
    const [card] = this.placed.splice(fromIndex, 1);
    this.placed.splice(target, 0, card);
    this.syncAllPlaced();
    this.selectedSlotIndex = target;
    this.status = "building";
    this.teacherConfirmed = false;
    this.auditioned = false;
    this.emitEvent("place_card", "素材卡已重排");
    this.renderScene();
  }

  undo() {
    this.removeCard(this.placed.length - 1);
  }

  audition(bpm = COMPOSITION_BPM_DEFAULT) {
    if (!this.placed.length || this.status === "success") return;
    this.status = "auditioning";
    this.auditioned = true;
    this.auditionIndex = -1;
    this.heroPresenter?.transitionTo("action", "listen");
    this.emitEvent("audition", "试听作品");
    this.time.removeAllEvents();
    const beatMs = beatMsForBpm(bpm);
    let cursorMs = 0;
    this.placed.forEach((card, index) => {
      const startMs = cursorMs;
      cursorMs += Math.max(1, Number(card.beats || 1)) * beatMs;
      this.time.delayedCall(startMs, () => {
        this.auditionIndex = index;
        this.renderScene();
      });
    });
    this.time.delayedCall(cursorMs + 180, () => {
      this.auditionIndex = -1;
      this.status = "building";
      this.renderScene();
    });
  }

  check(teacherConfirmed = this.teacherConfirmed) {
    this.attempts += 1;
    this.teacherConfirmed = teacherConfirmed;
    const checks = this.computeChecks();
    const passed = checks.every((item) => item.passed) && (!this.sceneConfig.teacher_confirm_required || this.teacherConfirmed);
    this.status = passed ? "success" : "failed";
    this.score = passed ? Math.max(300, 1000 - this.attempts * 80) : Math.max(0, this.score - 60);
    this.heroPresenter?.transitionTo(passed ? "win" : "miss", passed ? "success" : "miss");
    if (passed) {
      this.rewardImage?.setAlpha(1);
      this.launchSuccessFx();
      this.cameras.main.flash(220, 255, 240, 160);
    } else {
      const missing = checks.find((item) => !item.passed)?.label || "规则";
      this.popFloatingText(`缺少：${missing}`, WIDTH - 250, 310, 0xd66b4b);
      this.cameras.main.shake(140, 0.005);
    }
    this.emitEvent(passed ? "mission_success" : "mission_failed", passed ? "创编通关" : "还要修改");
    this.renderScene();
  }

  teacherConfirm() {
    this.teacherConfirmed = true;
    this.emitEvent("teacher_confirm", "教师已确认");
    this.check(true);
  }

  resetPuzzle() {
    this.placed = [];
    this.syncAllPlaced();
    this.status = "ready";
    this.attempts = 0;
    this.score = 0;
    this.teacherConfirmed = false;
    this.auditioned = false;
    this.auditionIndex = -1;
    this.selectedSlotIndex = -1;
    this.rewardImage?.setAlpha(0.4);
    this.heroPresenter?.transitionTo("idle", "idle");
    this.emitEvent("reset", "重新创编");
    this.renderScene();
  }

  private renderScene() {
    if (!this.graphics) return;
    const palette = this.palette;
    this.graphics.clear();
    this.textObjects.forEach((text) => text.setVisible(false));
    this.clearNotationObjects();
    this.clearInteractiveObjects();
    if (!this.backgroundImage) {
      this.cameras.main.setBackgroundColor(palette.bg);
      this.graphics.fillStyle(0xffffff, 0.52).fillRoundedRect(28, 92, 904, 390, 28);
      this.graphics.fillStyle(palette.accent, 0.1).fillRoundedRect(50, 128, 470, 80, 18);
      this.graphics.fillStyle(palette.success, 0.1).fillRoundedRect(542, 128, 260, 210, 24);
    }
    this.drawTrack();
    this.statusText.setText(this.status === "success" ? "通关" : `${this.sceneConfig.selected_meter} · ${this.modeLabel()}`);
  }

  private drawTrack() {
    const palette = this.palette;
    const startX = 68;
    const y = 316;
    const slotWidth = Math.min(88, 800 / this.slotCount);
    this.graphics.fillStyle(0x0f211e, 0.2).fillRoundedRect(startX - 18, y - 68, slotWidth * this.slotCount + 36, 142, 28);
    this.graphics.fillStyle(0xffffff, 0.2).fillRoundedRect(startX - 2, y - 50, slotWidth * this.slotCount - 4, 104, 20);
    for (let index = 0; index < this.slotCount; index += 1) {
      const x = startX + index * slotWidth;
      this.graphics.fillStyle(index === this.auditionIndex ? palette.success : palette.panel, index === this.auditionIndex ? 0.92 : 0.68);
      this.graphics.fillRoundedRect(x, y - 44, slotWidth - 8, 88, 16);
      if (index % this.sceneConfig.slots_per_bar === 0) {
        this.graphics.lineStyle(4, palette.accent, 0.72).lineBetween(x - 5, y - 62, x - 5, y + 62);
      }
    }
    let cursor = 0;
    this.placed.forEach((card, index) => {
      const beats = Math.min(Math.max(1, Math.round(Number(card.beats || 1))), Math.max(1, this.slotCount - cursor));
      const cardWidth = Math.max(58, slotWidth * beats - 10);
      const x = startX + cursor * slotWidth + cardWidth / 2;
      const isSelected = index === this.selectedSlotIndex;
      this.graphics.fillStyle(isSelected ? 0x9ee7d8 : palette.card, isSelected ? 0.98 : 0.96).fillRoundedRect(x - cardWidth / 2, y - 38, cardWidth, 76, 18);
      this.graphics.lineStyle(3, index === this.auditionIndex || isSelected ? palette.success : 0xffffff, 0.78).strokeRoundedRect(x - cardWidth / 2, y - 38, cardWidth, 76, 18);
      const scale = Math.min(1.08, cardWidth / 108);
      this.drawRhythmNotation(card.rhythm || card.id || card.label, x, y - 8, scale, palette.ink);
      this.drawPitchTokens(card, index, x, y + 24, scale, palette.ink);
      this.addPlacedZone(index, x, y, cardWidth, 64);
      cursor += beats;
    });
  }

  private drawShelf() {
    const palette = this.palette;
    this.graphics.fillStyle(palette.panel, 0.74).fillRoundedRect(54, 426, 660, 82, 22);
    const labels = this.availableShelfLabels();
    labels.slice(0, 7).forEach((label, index) => {
      const x = 104 + index * 86;
      const card = this.shelfCardAt(index);
      const isPitch = Boolean(card?.pitch);
      this.graphics.fillStyle(isPitch ? 0x9ee7d8 : palette.card, 0.9).fillRoundedRect(x - 34, 466 - 26, 68, 52, 14);
      this.graphics.lineStyle(2, palette.accent, 0.45).strokeRoundedRect(x - 34, 466 - 26, 68, 52, 14);
      if (isPitch) {
        this.addOrUpdateText(`shelf_${index}`, x, 466, label, "20px", palette.ink);
      } else {
        this.drawRhythmNotation(card?.rhythm || card?.id || label, x, 466, 0.52, palette.ink);
      }
      this.addShelfZone(index, x, 466, label);
    });
  }

  private drawChecks() {
    const palette = this.palette;
    const checks = this.computeChecks();
    checks.forEach((check, index) => {
      const y = 336 + index * 32;
      this.graphics.fillStyle(check.passed ? palette.success : 0xffffff, check.passed ? 0.24 : 0.5).fillRoundedRect(WIDTH - 330, y - 14, 240, 26, 12);
      this.addOrUpdateText(`check_${index}`, WIDTH - 210, y, `${check.passed ? "✓" : "○"} ${check.label}`, "15px", palette.ink);
    });
  }

  private computeChecks(): CompositionConstraintCheck[] {
    return evaluateCompositionPuzzleChecks(this.sceneConfig, this.allPlaced, this.teacherConfirmed, this.auditioned);
  }

  private emitEvent(type: CompositionPuzzleSceneEvent["type"], message: string) {
    this.onSceneEvent({ type, message, snapshot: this.snapshot(message) });
  }

  private snapshot(message: string): CompositionPuzzleSnapshot {
    return {
      status: this.status,
      placed: this.allPlaced,
      segmentPlaced: this.placed,
      checks: this.computeChecks(),
      progress: Math.min(1, compositionFilledSlots(this.allPlaced) / Math.max(1, this.totalSlotCount)),
      attempts: this.attempts,
      score: this.score,
      message,
      teacherConfirmed: this.teacherConfirmed,
      auditioned: this.auditioned,
      filledSlots: compositionFilledSlots(this.allPlaced),
      slotCount: this.totalSlotCount,
      segmentFilledSlots: compositionFilledSlots(this.placed),
      segmentSlotCount: this.slotCount,
      currentSegmentIndex: this.currentSegmentIndex,
      compositionSegments: this.sceneConfig.composition_segments,
      totalBars: this.sceneConfig.composition_total_bars,
      selectedSlotIndex: this.selectedSlotIndex
    };
  }

  private get slotCount() {
    return this.sceneConfig.segment_slots;
  }

  private get totalSlotCount() {
    return this.sceneConfig.total_slots;
  }

  private get currentSegmentIndex() {
    const index = Math.floor(Number(this.sceneConfig.current_segment_index || 0));
    return Math.max(0, Math.min(this.sceneConfig.composition_segments - 1, index));
  }

  private get segmentStartSlot() {
    return this.currentSegmentIndex * this.slotCount;
  }

  private syncAllPlaced() {
    this.allPlaced = this.composeAllPlaced(this.placed);
  }

  private composeAllPlaced(segmentPlaced: CompositionPlacedCard[]) {
    const source = Array.isArray(this.sceneConfig.all_placed) ? this.sceneConfig.all_placed : [];
    const before = source.slice(0, this.segmentStartSlot);
    const after = source.slice(this.segmentStartSlot + this.slotCount);
    const merged = before.concat(segmentPlaced, after);
    return merged.slice(0, this.totalSlotCount);
  }

  private segmentPlacedFromAll(allPlaced: CompositionPlacedCard[], segmentIndex: number) {
    const start = segmentIndex * this.slotCount;
    return allPlaced.slice(start, start + this.slotCount);
  }

  private get palette() {
    return paletteByMode[this.sceneConfig.skin_play_mode] || paletteByMode.studio;
  }

  private modeLabel() {
    return {
      rhythm_puzzle_composition: "节奏拼图",
      melody_puzzle_creation: "旋律拼图",
      melody_rhythm_puzzle: "音名 + 节奏"
    }[this.sceneConfig.mode];
  }

  private availableShelfLabels() {
    const rhythm = this.sceneConfig.rhythm_cards.map((card) => typeof card === "string" ? rhythmLabel(card) : card.label);
    const melody = this.sceneConfig.melody_cards.map((note) => noteNameLabel(note));
    if (this.sceneConfig.mode === "rhythm_puzzle_composition") return rhythm;
    if (this.sceneConfig.mode === "melody_puzzle_creation") return melody;
    return rhythm.slice(0, 4).concat(melody.slice(0, 4));
  }

  private textObjects = new Map<string, Phaser.GameObjects.Text>();

  private addOrUpdateText(key: string, x: number, y: number, text: string, fontSize: string, color: string) {
    const existing = this.textObjects.get(key);
    if (existing) {
      existing.setPosition(x, y).setText(text).setStyle({ fontSize, color }).setVisible(true);
      return;
    }
    this.textObjects.set(key, this.add.text(x, y, text, {
      color,
      fontFamily: "Noto Sans SC, PingFang SC, sans-serif",
      fontSize,
      fontStyle: "bold"
    }).setOrigin(0.5).setDepth(8));
  }

  private addShelfZone(index: number, x: number, y: number, label: string) {
    const card = this.shelfCardAt(index);
    if (!card) return;
    const zone = this.add.zone(x, y, 72, 56).setInteractive({ cursor: "grab", draggable: true });
    zone.setDepth(20);
    zone.on("pointerup", () => {
      if (!zone.getData("dragging")) this.placeCard(card);
    });
    zone.on("dragstart", () => {
      zone.setData("dragging", true);
      this.dragGhost = this.createDragGhost(cardLabel(card), x, y, Boolean(card.pitch));
    });
    zone.on("drag", (_pointer: Phaser.Input.Pointer, dragX: number, dragY: number) => {
      this.dragGhost?.setPosition(dragX, dragY);
    });
    zone.on("dragend", (_pointer: Phaser.Input.Pointer, dragX: number, dragY: number) => {
      if (this.isTrackPoint(dragX, dragY)) this.placeCard(card);
      this.dragGhost?.destroy();
      this.dragGhost = null;
      this.time.delayedCall(0, () => zone.setData("dragging", false));
    });
    this.input.setDraggable(zone);
    this.interactiveObjects.push(zone);
    this.addOrUpdateText(`shelf_hint_${index}`, x, y + 38, card.pitch ? "音名" : "节奏", "10px", this.palette.ink);
  }

  private addPlacedZone(index: number, x: number, y: number, width: number, height: number) {
    const zone = this.add.zone(x, y, width, height).setInteractive({ cursor: "grab", draggable: true });
    zone.setDepth(21);
    zone.on("pointerup", (pointer: Phaser.Input.Pointer) => {
      if (pointer.downTime && pointer.upTime - pointer.downTime < 220) this.selectSlot(index);
    });
    zone.on("dragstart", () => {
      this.dragGhost = this.createDragGhost(cardLabel(this.placed[index]), x, y, Boolean(this.placed[index]?.pitch));
    });
    zone.on("drag", (_pointer: Phaser.Input.Pointer, dragX: number, dragY: number) => {
      this.dragGhost?.setPosition(dragX, dragY);
    });
    zone.on("dragend", (_pointer: Phaser.Input.Pointer, dragX: number, dragY: number) => {
      if (this.isTrackPoint(dragX, dragY)) this.moveCard(index, this.slotIndexForPoint(dragX));
      this.dragGhost?.destroy();
      this.dragGhost = null;
    });
    this.input.setDraggable(zone);
    this.interactiveObjects.push(zone);
  }

  private createDragGhost(label: string, x: number, y: number, melody: boolean) {
    const palette = this.palette;
    const rect = this.add.rectangle(0, 0, 78, 58, melody ? 0x9ee7d8 : palette.card, 0.9).setStrokeStyle(3, 0xffffff, 0.8);
    const text = this.add.text(0, 0, label, {
      color: palette.ink,
      fontFamily: "Noto Sans SC, PingFang SC, sans-serif",
      fontSize: "17px",
      fontStyle: "bold"
    }).setOrigin(0.5);
    return this.add.container(x, y, [rect, text]).setDepth(60).setAlpha(0.86);
  }

  private shelfCardAt(index: number): CompositionPlacedCard | null {
    const labels = this.availableShelfLabels();
    const rhythm: CompositionPlacedCard[] = this.sceneConfig.rhythm_cards.map((card) => typeof card === "string"
      ? { id: card, label: rhythmLabel(card), rhythm: card, beats: rhythmBeats(card) }
      : { id: card.id, label: rhythmLabel(card.id || card.label), rhythm: card.id, beats: Number(card.beats || rhythmBeats(card.id)) });
    const melody: CompositionPlacedCard[] = this.sceneConfig.melody_cards.map((pitch) => ({ id: `pitch_${pitch}`, label: noteNameLabel(pitch), pitch, beats: 1 }));
    const cards = this.sceneConfig.mode === "rhythm_puzzle_composition"
      ? rhythm
      : this.sceneConfig.mode === "melody_puzzle_creation"
        ? melody
        : rhythm.slice(0, 6).concat(melody.slice(0, 4));
    return cards[index] || (labels[index] ? { id: labels[index], label: labels[index], beats: 1 } : null);
  }

  private isTrackPoint(_x: number, y: number) {
    return y >= 236 && y <= 398;
  }

  private slotIndexForPoint(x: number) {
    const slotWidth = Math.min(88, 800 / this.slotCount);
    return Math.round((x - 68) / slotWidth);
  }

  private clearInteractiveObjects() {
    this.interactiveObjects.forEach((object) => object.destroy());
    this.interactiveObjects = [];
  }

  private clearNotationObjects() {
    this.notationObjects.forEach((object) => object.destroy());
    this.notationObjects = [];
  }

  private drawRhythmNotation(id: string, x: number, y: number, scale: number, color: string) {
    const graphics = this.add.graphics().setDepth(9);
    const strokeColor = Phaser.Display.Color.HexStringToColor(color).color;
    if (id === "rest") {
      graphics.lineStyle(5 * scale, strokeColor, 1);
      graphics.beginPath();
      graphics.moveTo(x - 14 * scale, y - 14 * scale);
      graphics.lineTo(x + 12 * scale, y - 14 * scale);
      graphics.lineTo(x - 2 * scale, y + 2 * scale);
      graphics.lineTo(x + 14 * scale, y + 2 * scale);
      graphics.strokePath();
      graphics.fillStyle(strokeColor, 1);
      graphics.fillCircle(x + 3 * scale, y + 18 * scale, 4 * scale);
      this.notationObjects.push(graphics);
      return;
    }
    graphics.fillStyle(strokeColor, 1);
    graphics.lineStyle(4 * scale, strokeColor, 1);
    const pattern = rhythmPattern(id);
    const startX = x - ((pattern.length - 1) * 24 * scale) / 2;
    const stemTop = y - 24 * scale;
    const noteY = y + 12 * scale;
    const stemXs: number[] = [];

    pattern.forEach((duration, index) => {
      const noteX = startX + index * 24 * scale;
      stemXs.push(noteX + 8 * scale);
      graphics.save();
      graphics.translateCanvas(noteX, noteY);
      graphics.rotateCanvas(-0.28);
      graphics.fillEllipse(0, 0, 18 * scale, 13 * scale);
      graphics.restore();
      graphics.lineBetween(noteX + 8 * scale, noteY - 1 * scale, noteX + 8 * scale, stemTop);
      if (duration === "quarter") {
        stemXs.pop();
      }
    });

    if (stemXs.length >= 2) {
      graphics.lineStyle(7 * scale, strokeColor, 1);
      graphics.lineBetween(stemXs[0], stemTop, stemXs[stemXs.length - 1], stemTop);
      const sixteenthXs = pattern
        .map((duration, index) => duration === "sixteenth" ? startX + index * 24 * scale + 8 * scale : null)
        .filter((value): value is number => value !== null);
      if (sixteenthXs.length >= 2) {
        graphics.lineBetween(sixteenthXs[0], stemTop + 11 * scale, sixteenthXs[sixteenthXs.length - 1], stemTop + 11 * scale);
      }
    }

    this.notationObjects.push(graphics);
  }

  private drawPitchTokens(card: CompositionPlacedCard, cardIndex: number, x: number, y: number, scale: number, color: string) {
    const pattern = rhythmPattern(card.rhythm || card.id);
    const noteIndexes = pattern.map((duration, index) => duration === "rest" ? null : index).filter((value): value is number => value !== null);
    const pitches = card.pitches || [];
    const startX = x - ((pattern.length - 1) * 24 * scale) / 2;
    noteIndexes.forEach((patternIndex, pitchIndex) => {
      const noteX = startX + patternIndex * 24 * scale;
      const basePitch = pitches[pitchIndex] || "";
      const pitch = basePitch ? transposeNoteName(basePitch, this.sceneConfig.selected_tonic, this.sceneConfig.playback_tonic) || basePitch : "·";
      const selected = cardIndex === this.selectedSlotIndex && pitchIndex === (card.selectedAttackIndex || 0);
      if (selected) {
        this.graphics.fillStyle(0xffffff, 0.76).fillRoundedRect(noteX - 13 * scale, y - 10 * scale, 26 * scale, 19 * scale, 8 * scale);
      }
      this.addOrUpdateText(`pitch_${cardIndex}_${pitchIndex}`, noteX, y, pitch, "13px", color);
    });
  }

  private popFloatingText(message: string, x: number, y: number, color: number) {
    const text = this.add.text(x, y, message, {
      color: `#${color.toString(16).padStart(6, "0")}`,
      fontFamily: "Noto Sans SC, PingFang SC, sans-serif",
      fontSize: "20px",
      fontStyle: "bold"
    }).setOrigin(0.5).setDepth(80);
    this.tweens.add({
      targets: text,
      y: y - 38,
      alpha: 0,
      duration: 820,
      ease: "Cubic.easeOut",
      onComplete: () => text.destroy()
    });
  }

  private launchSuccessFx() {
    if (!this.textures.exists(REWARD_ASSET_KEY)) {
      this.popFloatingText("三星通关!", WIDTH - 130, HEIGHT - 86, 0xf0b83e);
      return;
    }
    if (!this.successEmitter) {
      this.successEmitter = this.add.particles(WIDTH - 84, HEIGHT - 70, REWARD_ASSET_KEY, {
        lifespan: 720,
        speed: { min: 80, max: 220 },
        scale: { start: 0.18, end: 0 },
        alpha: { start: 0.9, end: 0 },
        quantity: 18,
        emitting: false
      });
      this.successEmitter.setDepth(70);
    }
    this.successEmitter.explode(24, WIDTH - 84, HEIGHT - 70);
  }
}

function beatMsForBpm(bpm: number) {
  const normalizedBpm = Math.min(COMPOSITION_BPM_MAX, Math.max(COMPOSITION_BPM_MIN, Number.isFinite(bpm) ? bpm : COMPOSITION_BPM_DEFAULT));
  return (60 / normalizedBpm) * 1000;
}

function normalizeRequiredConfig(config: CompositionPuzzleSceneConfig): Required<CompositionPuzzleSceneConfig> {
  return buildCompositionPuzzleSceneConfig(config as Record<string, unknown>) as Required<CompositionPuzzleSceneConfig>;
}

function normalizePlayMode(value: unknown, skinId: unknown): "studio" | "rhythm_table" | "melody_garden" {
  if (skinId === "rhythm_tile_table") return "rhythm_table";
  if (skinId === "melody_garden") return "melody_garden";
  const mode = String(value || "");
  return mode === "rhythm_table" || mode === "melody_garden" ? mode : "studio";
}

function cardLabel(card: CompositionPlacedCard) {
  return card.pitch ? noteNameLabel(card.pitch) : rhythmLabel(card.rhythm || card.id || card.label);
}

function rhythmLabel(id: string) {
  return {
    quarter: "四分",
    eighth_pair: "二八",
    rest: "休止",
    half: "二分",
    dotted_quarter: "附点四分",
    syncopation: "小切分",
    sixteenth_four: "四个十六",
    eighth_sixteenth: "八十六",
    eighth_sixteenth_sixteenth: "八十六",
    sixteenth_eighth: "十六八",
    sixteenth_sixteenth_eighth: "十六八",
    eighth_sixteenth_sixteenth_eighth: "前八后十六 + 八"
  }[id] || id;
}

function rhythmPattern(id: string): Array<"quarter" | "eighth" | "sixteenth" | "rest"> {
  if (id === "rest") return ["rest"];
  if (id === "eighth_pair") return ["eighth", "eighth"];
  if (id === "sixteenth_four") return ["sixteenth", "sixteenth", "sixteenth", "sixteenth"];
  if (id === "eighth_sixteenth" || id === "eighth_sixteenth_sixteenth") return ["eighth", "sixteenth", "sixteenth"];
  if (id === "sixteenth_eighth" || id === "sixteenth_sixteenth_eighth") return ["sixteenth", "sixteenth", "eighth"];
  if (id === "syncopation") return ["sixteenth", "eighth", "sixteenth"];
  if (id === "eighth_sixteenth_sixteenth_eighth") return ["eighth", "sixteenth", "sixteenth", "eighth"];
  return ["quarter"];
}

function rhythmBeats(id: string) {
  return id === "half" || id === "syncopation" || id === "eighth_sixteenth_sixteenth_eighth" ? 2 : 1;
}

function noteNameLabel(note: string) {
  return {
    C: "C",
    D: "D",
    E: "E",
    F: "F",
    G: "G",
    A: "A",
    B: "B",
    "C'": "C'",
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

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
