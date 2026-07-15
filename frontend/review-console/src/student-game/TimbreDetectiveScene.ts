import Phaser from "phaser";
import { TemplateCharacterPresenter } from "./templateCharacterPresenter";
import { templateVisualPackForConfig } from "./templateVisualAssets";
import type { Round, TemplatePoseKey, TemplateVisualPack, TimbreAudioProfile } from "./types";

export type TimbreCaseState = "open" | "solved" | "wrong" | "evidence_missing";

export type TimbreDetectiveSceneConfig = {
  engine?: "phaser_2d";
  scene_id?: "timbre_detective_scene";
  runtime_shell?: "timbre_detective_shell";
  game_feel?: "animated_detective_caseboard";
  skin_id?: string;
  skin_play_mode?: "casebook" | "museum" | "forest" | "studio" | "theater";
  mode?: string;
  clue_cases?: Round[];
  suspect_cards?: Array<Record<string, string>>;
  evidence_tokens?: Array<Record<string, string>>;
  evidence_required?: number;
  comparison_reason_required?: boolean;
  dynamic_case_scene?: boolean;
  input_actions?: string[];
  fx_profile?: Record<string, string>;
  score_model?: Record<string, number>;
  asset_manifest?: TemplateVisualPack;
};

export type TimbreDetectiveSnapshot = {
  status: TimbreCaseState;
  currentCase: number;
  totalCases: number;
  heard: boolean;
  selectedAnswer: string;
  selectedEvidence: string[];
  solvedCases: number;
  score: number;
  combo: number;
  evidenceNeed: number;
  message: string;
};

export type TimbreDetectiveSceneEvent = {
  type:
    | "scene_ready"
    | "listen_requested"
    | "suspect_selected"
    | "evidence_selected"
    | "submit_requested"
    | "next_requested"
    | "reset_requested";
  snapshot: TimbreDetectiveSnapshot;
  suspect?: string;
  evidence?: string[];
  message?: string;
};

export type TimbreDetectiveController = {
  setSnapshot: (snapshot: TimbreDetectiveSnapshot, round: Round, suspects: Array<Record<string, string>>, evidence: Array<Record<string, string>>) => void;
  playListenFx: (profile?: TimbreAudioProfile | null, compareProfile?: TimbreAudioProfile | null) => void;
  showResult: (state: TimbreCaseState) => void;
  resetBoard: () => void;
  destroy: () => void;
};

const WIDTH = 960;
const HEIGHT = 540;
const BG_KEY = "timbre_detective_bg";
const HERO_KEYS: Record<TemplatePoseKey, string> = {
  idle: "timbre_pose_idle",
  action: "timbre_pose_action",
  miss: "timbre_pose_miss",
  win: "timbre_pose_win"
};
const PROP_KEYS = Array.from({ length: 12 }, (_, index) => `timbre_prop_${index + 1}`);
const REWARD_KEYS = Array.from({ length: 12 }, (_, index) => `timbre_reward_${index + 1}`);

type SceneSuspect = {
  label: string;
  hint: string;
  visual: string;
  x: number;
  y: number;
  container: Phaser.GameObjects.Container;
  frame: Phaser.GameObjects.Rectangle;
};

type SceneEvidence = {
  label: string;
  x: number;
  y: number;
  container: Phaser.GameObjects.Container;
  selected: boolean;
};

export function buildTimbreDetectiveSceneConfig(raw: Record<string, unknown>): TimbreDetectiveSceneConfig {
  const nested = isRecord(raw.scene_config) ? raw.scene_config : {};
  const merged = { ...raw, ...nested };
  return {
    engine: "phaser_2d",
    scene_id: "timbre_detective_scene",
    runtime_shell: "timbre_detective_shell",
    game_feel: "animated_detective_caseboard",
    skin_id: String(merged.skin_id || "sound_casebook"),
    skin_play_mode: normalizePlayMode(merged.skin_play_mode, merged.skin_id),
    mode: String(merged.mode || "instrument_clue"),
    clue_cases: normalizeRounds(merged.clue_cases || merged.timbre_rounds),
    suspect_cards: normalizeCards(merged.suspect_cards),
    evidence_tokens: normalizeCards(merged.evidence_tokens),
    evidence_required: clampNumber(Number(merged.evidence_required), 1, 3, 1),
    comparison_reason_required: Boolean(merged.comparison_reason_required),
    dynamic_case_scene: true,
    input_actions: normalizeInputActions(merged.input_actions),
    fx_profile: isRecord(merged.fx_profile) ? Object.fromEntries(Object.entries(merged.fx_profile).map(([key, value]) => [key, String(value)])) : {},
    score_model: isRecord(merged.score_model) ? Object.fromEntries(Object.entries(merged.score_model).map(([key, value]) => [key, Number(value)])) : {},
    asset_manifest: templateVisualPackForConfig(merged, "timbre_detective_core")
  };
}

export function mountTimbreDetectiveScene(
  parent: HTMLElement,
  config: TimbreDetectiveSceneConfig,
  initialSnapshot: TimbreDetectiveSnapshot,
  initialRound: Round,
  suspects: Array<Record<string, string>>,
  evidence: Array<Record<string, string>>,
  onEvent: (event: TimbreDetectiveSceneEvent) => void
): TimbreDetectiveController {
  const built = buildTimbreDetectiveSceneConfig(config as Record<string, unknown>);
  const scene = new TimbreDetectiveScene(built, initialSnapshot, initialRound, suspects, evidence, onEvent);
  const game = new Phaser.Game({
    type: Phaser.AUTO,
    parent,
    width: WIDTH,
    height: HEIGHT,
    backgroundColor: "#271a17",
    scale: { mode: Phaser.Scale.FIT, autoCenter: Phaser.Scale.CENTER_BOTH },
    scene: [scene]
  });
  return {
    setSnapshot: (snapshot, round, nextSuspects, nextEvidence) => scene.setSnapshot(snapshot, round, nextSuspects, nextEvidence),
    playListenFx: (profile, compareProfile) => scene.playListenFx(profile, compareProfile),
    showResult: (state) => scene.showResult(state),
    resetBoard: () => scene.resetBoard(),
    destroy: () => game.destroy(true)
  };
}

class TimbreDetectiveScene extends Phaser.Scene {
  private readonly sceneConfig: Required<TimbreDetectiveSceneConfig>;
  private readonly onSceneEvent: (event: TimbreDetectiveSceneEvent) => void;
  private snapshot: TimbreDetectiveSnapshot;
  private round: Round;
  private suspects: Array<Record<string, string>>;
  private evidence: Array<Record<string, string>>;
  private hero: TemplateCharacterPresenter | null = null;
  private evidenceOrb!: Phaser.GameObjects.Container;
  private waveGraphics!: Phaser.GameObjects.Graphics;
  private threadGraphics!: Phaser.GameObjects.Graphics;
  private caseTitle!: Phaser.GameObjects.Text;
  private feedbackText!: Phaser.GameObjects.Text;
  private stampText!: Phaser.GameObjects.Text;
  private rewardImage: Phaser.GameObjects.Image | null = null;
  private heroBackdrop: Phaser.GameObjects.Container | null = null;
  private suspectViews: SceneSuspect[] = [];
  private evidenceViews: SceneEvidence[] = [];
  private evidenceSlots: Phaser.GameObjects.Rectangle[] = [];
  private lampBeam!: Phaser.GameObjects.Triangle;
  private tableGroup!: Phaser.GameObjects.Container;
  private sceneReady = false;
  private draggingEvidence: { view: SceneEvidence; pointerId: number; moved: boolean; startX: number; startY: number } | null = null;

  constructor(
    config: TimbreDetectiveSceneConfig,
    snapshot: TimbreDetectiveSnapshot,
    round: Round,
    suspects: Array<Record<string, string>>,
    evidence: Array<Record<string, string>>,
    onEvent: (event: TimbreDetectiveSceneEvent) => void
  ) {
    super("timbre_detective_scene");
    this.sceneConfig = normalizeRequiredConfig(config);
    this.snapshot = snapshot;
    this.round = round;
    this.suspects = suspects;
    this.evidence = evidence;
    this.onSceneEvent = onEvent;
  }

  preload() {
    const manifest = this.sceneConfig.asset_manifest;
    if (manifest.background) this.load.image(BG_KEY, manifest.background);
    (Object.keys(HERO_KEYS) as TemplatePoseKey[]).forEach((pose) => {
      const source = manifest.poses?.[pose];
      if (source) this.load.image(HERO_KEYS[pose], source);
    });
    manifest.props?.slice(0, PROP_KEYS.length).forEach((source, index) => this.load.image(PROP_KEYS[index], source));
    manifest.rewards?.slice(0, REWARD_KEYS.length).forEach((source, index) => this.load.image(REWARD_KEYS[index], source));
  }

  create() {
    this.cameras.main.setRoundPixels(true);
    this.buildBackdrop();
    this.buildDesk();
    this.buildCaseBoard();
    this.buildEvidenceOrb();
    this.heroBackdrop = this.add.container(846, 346).setDepth(12);
    this.heroBackdrop.add(this.add.ellipse(0, 72, 130, 34, 0x120c0a, 0.34));
    this.heroBackdrop.add(this.add.ellipse(0, 0, 150, 236, 0xffe3a1, 0.16).setStrokeStyle(3, 0xffd88f, 0.22));
    this.heroBackdrop.add(this.add.rectangle(0, 92, 118, 36, 0x2c1b18, 0.48).setStrokeStyle(2, 0xf1b64d, 0.22));
    this.heroBackdrop.add(this.add.text(-42, 82, "声音侦探", labelStyle("#ffe7ba", 15, 84)));
    this.hero = new TemplateCharacterPresenter(this, {
      poseKeys: HERO_KEYS,
      x: 846,
      y: 334,
      displaySize: 238,
      depth: 13,
      preserveAspectRatio: true,
      stableScale: true
    });
    this.rebuildInteractivePieces();
    this.registerStageInput();
    this.sceneReady = true;
    this.updateSceneText();
    this.updateSelectionState();
    this.onSceneEvent({ type: "scene_ready", snapshot: this.snapshot, message: "声音案卷已打开" });
  }

  setSnapshot(
    snapshot: TimbreDetectiveSnapshot,
    round: Round,
    suspects: Array<Record<string, string>>,
    evidence: Array<Record<string, string>>
  ) {
    const caseChanged = snapshot.currentCase !== this.snapshot.currentCase;
    this.snapshot = snapshot;
    this.round = round;
    this.suspects = suspects;
    this.evidence = evidence;
    if (!this.sceneReady) return;
    if (caseChanged) {
      this.resetBoard();
      this.rebuildInteractivePieces();
    }
    this.updateSceneText();
    this.updateSelectionState();
    if (snapshot.status === "solved" || snapshot.status === "wrong" || snapshot.status === "evidence_missing") {
      this.showResult(snapshot.status);
    }
  }

  playListenFx(profile?: TimbreAudioProfile | null, compareProfile?: TimbreAudioProfile | null) {
    if (!this.sceneReady) return;
    const brightness = clampNumber(Number(profile?.brightness ?? 0.55), 0.1, 1, 0.55);
    const release = clampNumber(Number(profile?.release ?? 0.34), 0.08, 0.9, 0.34);
    this.snapshot = { ...this.snapshot, heard: true, message: compareProfile ? "比较两声" : "声纹扫描中" };
    this.hero?.transitionTo("action", "listen");
    this.feedbackText.setText(compareProfile ? "比较两声，寻找差异" : "声纹正在扫描");
    this.lampSweep();
    this.cameras.main.zoomTo(1.035, 260, "Sine.easeOut", true);
    this.time.delayedCall(420, () => this.cameras.main.zoomTo(1, 340, "Sine.easeInOut", true));
    this.animateWave(brightness, release, false);
    if (compareProfile) {
      this.time.delayedCall(680, () => this.animateWave(clampNumber(Number(compareProfile.brightness ?? 0.45), 0.1, 1, 0.45), release, true));
    }
    this.emitParticles(236, 244, 0x61d6ba, 18);
  }

  showResult(state: TimbreCaseState) {
    if (!this.sceneReady) return;
    this.stampText.setVisible(true);
    if (state === "solved") {
      this.hero?.transitionTo("win", "success");
      this.stampText.setText("破案").setColor("#15523d").setAngle(-10).setAlpha(0).setScale(1.9);
      this.tweens.add({ targets: this.stampText, alpha: 1, scale: 1, duration: 320, ease: "Bounce.Out" });
      this.emitParticles(493, 178, 0xf1b64d, 34);
      this.flashReward();
      this.cameras.main.zoomTo(1.04, 200, "Sine.easeOut", true);
      this.time.delayedCall(360, () => this.cameras.main.zoomTo(1, 280, "Sine.easeInOut", true));
      return;
    }
    this.hero?.transitionTo("miss", "miss");
    this.stampText.setText(state === "evidence_missing" ? "补证据" : "再侦查").setColor("#8f2c24").setAngle(8).setAlpha(0).setScale(1.5);
    this.tweens.add({ targets: this.stampText, alpha: 1, scale: 1, duration: 220, ease: "Back.Out" });
    this.cameras.main.shake(190, 0.007);
    this.emitParticles(493, 178, 0xd65f48, 16);
  }

  resetBoard() {
    if (!this.sceneReady) return;
    this.waveGraphics.clear();
    this.threadGraphics.clear();
    this.stampText.setVisible(false);
    this.rewardImage?.setVisible(false);
    this.hero?.transitionTo("idle", "idle");
    this.heroBackdrop?.setAlpha(1);
    this.cameras.main.setZoom(1);
  }

  private buildBackdrop() {
    if (this.textures.exists(BG_KEY)) {
      this.add.image(WIDTH / 2, HEIGHT / 2, BG_KEY).setDisplaySize(WIDTH, HEIGHT).setDepth(-20).setAlpha(0.92);
    }
    this.add.rectangle(WIDTH / 2, HEIGHT / 2, WIDTH, HEIGHT, 0x2a1815, 0.34).setDepth(-19);
    this.add.rectangle(WIDTH / 2, HEIGHT - 54, WIDTH, 132, 0x3f231b, 0.9).setDepth(-2);
    this.add.rectangle(WIDTH / 2, HEIGHT - 118, WIDTH, 18, 0xf0b66b, 0.22).setDepth(-1);
    this.lampBeam = this.add.triangle(716, 94, 0, 0, 172, 0, 92, 332, 0xffdca3, 0.16).setDepth(-3).setAlpha(0.45);
    this.tweens.add({ targets: this.lampBeam, alpha: 0.24, duration: 1350, yoyo: true, repeat: -1, ease: "Sine.inOut" });
  }

  private buildDesk() {
    this.tableGroup = this.add.container(0, 0).setDepth(2);
    this.tableGroup.add(this.add.rectangle(480, 369, 770, 250, 0x6b3e24, 0.94).setStrokeStyle(5, 0xf1b64d, 0.34));
    this.tableGroup.add(this.add.rectangle(480, 258, 706, 32, 0x9b6638, 0.86));
    this.tableGroup.add(this.add.ellipse(236, 244, 132, 90, 0x152d2a, 0.72).setStrokeStyle(4, 0x61d6ba, 0.68));
    this.tableGroup.add(this.add.text(182, 200, "声音证物", labelStyle("#dff8e9", 18)));
    this.tableGroup.add(this.add.rectangle(502, 274, 260, 34, 0x2c1b18, 0.28));
    this.tableGroup.add(this.add.text(395, 257, "线索会连到这里", labelStyle("#ffe7ba", 15)));
    this.waveGraphics = this.add.graphics().setDepth(12);
    this.threadGraphics = this.add.graphics().setDepth(11);
  }

  private buildCaseBoard() {
    this.add.rectangle(493, 166, 294, 178, 0xf2d9a8, 0.94).setDepth(4).setStrokeStyle(5, 0x5c3220, 0.56);
    this.add.rectangle(493, 99, 246, 22, 0x5c3220, 0.82).setDepth(5);
    this.caseTitle = this.add.text(370, 113, "", {
      color: "#352218",
      fontFamily: "PingFang SC, Noto Sans SC, sans-serif",
      fontSize: "20px",
      fontStyle: "bold",
      fixedWidth: 246
    }).setDepth(6);
    this.feedbackText = this.add.text(374, 144, "", {
      color: "#68452c",
      fontFamily: "PingFang SC, Noto Sans SC, sans-serif",
      fontSize: "15px",
      wordWrap: { width: 236 }
    }).setDepth(6);
    for (let index = 0; index < 3; index += 1) {
      const slot = this.add.rectangle(404 + index * 88, 220, 72, 38, 0xfff5d6, 0.82).setStrokeStyle(2, 0x9b6638, 0.38).setDepth(6);
      this.evidenceSlots.push(slot);
    }
    this.stampText = this.add.text(462, 170, "", {
      color: "#15523d",
      fontFamily: "PingFang SC, Noto Sans SC, sans-serif",
      fontSize: "34px",
      fontStyle: "bold"
    }).setDepth(30).setVisible(false);
    if (this.textures.exists(REWARD_KEYS[0])) {
      this.rewardImage = this.add.image(635, 162, REWARD_KEYS[0]).setDisplaySize(72, 72).setDepth(26).setVisible(false);
    }
  }

  private buildEvidenceOrb() {
    this.evidenceOrb = this.add.container(236, 244).setDepth(14);
    this.evidenceOrb.add(this.add.circle(0, 0, 42, 0x61d6ba, 0.22).setStrokeStyle(4, 0xbff4df, 0.7));
    this.evidenceOrb.add(this.add.circle(0, 0, 17, 0xffe3a1, 0.8));
    const iconKey = PROP_KEYS[0];
    if (this.textures.exists(iconKey)) this.evidenceOrb.add(this.add.image(0, -6, iconKey).setDisplaySize(54, 54));
    this.tweens.add({ targets: this.evidenceOrb, y: 236, duration: 980, yoyo: true, repeat: -1, ease: "Sine.inOut" });
  }

  private rebuildInteractivePieces() {
    this.suspectViews.forEach((view) => view.container.destroy(true));
    this.evidenceViews.forEach((view) => view.container.destroy(true));
    this.suspectViews = [];
    this.evidenceViews = [];
    this.suspects.slice(0, 6).forEach((item, index) => this.suspectViews.push(this.createSuspect(item, index)));
    this.evidence.slice(0, 6).forEach((item, index) => this.evidenceViews.push(this.createEvidence(item, index)));
  }

  private createSuspect(item: Record<string, string>, index: number): SceneSuspect {
    const positions = [
      [116, 340],
      [255, 386],
      [392, 382],
      [560, 382],
      [690, 386],
      [808, 306]
    ];
    const [x, y] = positions[index] || [128 + index * 120, 394];
    const label = String(item.label || item.id || "嫌疑");
    const container = this.add.container(x, y).setDepth(17);
    const frame = this.add.rectangle(0, 0, 112, 88, 0xfff3d6, 0.94).setStrokeStyle(3, 0x7a4a2a, 0.48);
    const propKey = PROP_KEYS[(index + 2) % PROP_KEYS.length];
    container.add(frame);
    if (this.textures.exists(propKey)) container.add(this.add.image(0, -15, propKey).setDisplaySize(50, 50));
    container.add(this.add.text(-45, 18, label, labelStyle("#2c1b18", 18, 90)));
    container.add(this.add.text(-45, 42, String(item.hint || item.visual || "听证物"), labelStyle("#6f4d34", 12, 92)));
    return { label, hint: String(item.hint || ""), visual: String(item.visual || ""), x, y, container, frame };
  }

  private createEvidence(item: Record<string, string>, index: number): SceneEvidence {
    const x = 662 + (index % 3) * 84;
    const y = 78 + Math.floor(index / 3) * 58;
    const label = String(item.label || item.id || "证据");
    const container = this.add.container(x, y).setDepth(16);
    const bg = this.add.rectangle(0, 0, 74, 42, 0xfff8dd, 0.96).setStrokeStyle(2, 0x2f766c, 0.38);
    container.add(bg);
    const propKey = PROP_KEYS[(index + 6) % PROP_KEYS.length];
    if (this.textures.exists(propKey)) container.add(this.add.image(-22, 0, propKey).setDisplaySize(26, 26));
    container.add(this.add.text(-22, -9, shortEvidenceLabel(label), labelStyle("#2c1b18", 13, 66)));
    return { label, x, y, container, selected: false };
  }

  private registerStageInput() {
    this.input.on("pointerdown", this.handleStagePointerDown, this);
    this.input.on("pointermove", this.handleStagePointerMove, this);
    this.input.on("pointerup", this.handleStagePointerUp, this);
  }

  private handleStagePointerDown(pointer: Phaser.Input.Pointer) {
    const point = this.pointerToWorld(pointer);
    const evidence = this.findEvidenceAt(point.x, point.y);
    if (evidence) {
      this.draggingEvidence = { view: evidence, pointerId: pointer.id, moved: false, startX: point.x, startY: point.y };
      evidence.container.setDepth(28).setScale(1.08);
      return;
    }
    const suspect = this.findSuspectAt(point.x, point.y);
    if (suspect) {
      this.snapshot = { ...this.snapshot, selectedAnswer: suspect.label, status: "open" };
      this.updateSelectionState();
      this.onSceneEvent({ type: "suspect_selected", snapshot: this.snapshot, suspect: suspect.label, message: "已锁定嫌疑" });
      return;
    }
    if (this.isInside(point.x, point.y, this.evidenceOrb.x, this.evidenceOrb.y, 58, 50)) {
      this.onSceneEvent({ type: "listen_requested", snapshot: this.snapshot, message: "听声音证物" });
    }
  }

  private handleStagePointerMove(pointer: Phaser.Input.Pointer) {
    if (!this.draggingEvidence || this.draggingEvidence.pointerId !== pointer.id || !pointer.isDown) return;
    const point = this.pointerToWorld(pointer);
    this.draggingEvidence.moved = this.draggingEvidence.moved || Phaser.Math.Distance.Between(point.x, point.y, this.draggingEvidence.startX, this.draggingEvidence.startY) > 8;
    this.draggingEvidence.view.container.setPosition(point.x, point.y);
  }

  private handleStagePointerUp(pointer: Phaser.Input.Pointer) {
    if (!this.draggingEvidence || this.draggingEvidence.pointerId !== pointer.id) return;
    const view = this.draggingEvidence.view;
    view.container.setScale(1).setDepth(16);
    this.draggingEvidence = null;
    this.toggleEvidence(view.label);
  }

  private pointerToWorld(pointer: Phaser.Input.Pointer) {
    return this.cameras.main.getWorldPoint(pointer.x, pointer.y);
  }

  private findEvidenceAt(x: number, y: number) {
    return [...this.evidenceViews].reverse().find((view) => this.isInside(x, y, view.container.x, view.container.y, 46, 30));
  }

  private findSuspectAt(x: number, y: number) {
    return [...this.suspectViews].reverse().find((view) => this.isInside(x, y, view.x, view.y, 62, 50));
  }

  private isInside(x: number, y: number, centerX: number, centerY: number, halfWidth: number, halfHeight: number) {
    return Math.abs(x - centerX) <= halfWidth && Math.abs(y - centerY) <= halfHeight;
  }

  private toggleEvidence(label: string) {
    const current = new Set(this.snapshot.selectedEvidence);
    if (current.has(label)) current.delete(label);
    else if (current.size < this.snapshot.evidenceNeed) current.add(label);
    const evidence = Array.from(current);
    if (!current.has(label) && evidence.length >= this.snapshot.evidenceNeed) {
      evidence[evidence.length - 1] = label;
    }
    this.snapshot = { ...this.snapshot, selectedEvidence: evidence, status: "open" };
    this.updateSelectionState();
    this.onSceneEvent({ type: "evidence_selected", snapshot: this.snapshot, evidence, message: "证据已贴上" });
    this.flyEvidenceLabel(label, evidence.indexOf(label));
  }

  private updateSceneText() {
    this.caseTitle.setText(`案件 ${Math.min(this.snapshot.currentCase + 1, this.snapshot.totalCases)}：${String(this.round.label || this.round.id || "声音证物")}`);
    this.feedbackText.setText(this.snapshot.message || String(this.round.prompt || "听证物，找线索"));
  }

  private updateSelectionState() {
    this.threadGraphics.clear();
    this.suspectViews.forEach((view) => {
      const selected = view.label === this.snapshot.selectedAnswer;
      view.frame.setFillStyle(selected ? 0xffdc8a : 0xfff3d6, selected ? 1 : 0.94);
      view.frame.setStrokeStyle(selected ? 5 : 3, selected ? 0xf1b64d : 0x7a4a2a, selected ? 0.95 : 0.48);
      view.container.setScale(selected ? 1.08 : 1);
      if (selected) this.drawThread(236, 244, view.x, view.y - 20, 0xf1b64d, 0.75);
    });
    this.evidenceViews.forEach((view) => {
      const selectedIndex = this.snapshot.selectedEvidence.indexOf(view.label);
      view.selected = selectedIndex >= 0;
      const target = selectedIndex >= 0 && this.evidenceSlots[selectedIndex]
        ? { x: this.evidenceSlots[selectedIndex].x, y: this.evidenceSlots[selectedIndex].y }
        : { x: view.x, y: view.y };
      this.tweens.add({ targets: view.container, x: target.x, y: target.y, scale: selectedIndex >= 0 ? 1.05 : 1, duration: 210, ease: "Cubic.Out" });
      if (selectedIndex >= 0) this.drawThread(493, 220, target.x, target.y, 0x61d6ba, 0.58);
    });
  }

  private animateWave(brightness: number, release: number, compare: boolean) {
    const color = compare ? 0xf1b64d : 0x61d6ba;
    const bars = 18;
    this.tweens.killTweensOf(this.waveGraphics);
    this.waveGraphics.clear();
    for (let step = 0; step < 6; step += 1) {
      this.time.delayedCall(step * 90, () => {
        this.waveGraphics.clear();
        this.waveGraphics.lineStyle(3, color, 0.72 - step * 0.08);
        this.waveGraphics.strokeCircle(236, 244, 50 + step * 19 + release * 15);
        for (let i = 0; i < bars; i += 1) {
          const height = 18 + ((i * 13 + step * 11) % 58) * brightness;
          const x = 302 + i * 9;
          this.waveGraphics.fillStyle(color, 0.42 + brightness * 0.35);
          this.waveGraphics.fillRoundedRect(x, 240 - height / 2, 5, height, 3);
        }
      });
    }
    this.time.delayedCall(680, () => this.waveGraphics.clear());
  }

  private drawThread(fromX: number, fromY: number, toX: number, toY: number, color: number, alpha: number) {
    this.threadGraphics.lineStyle(3, color, alpha);
    this.threadGraphics.beginPath();
    this.threadGraphics.moveTo(fromX, fromY);
    const midX = (fromX + toX) / 2;
    this.threadGraphics.lineTo(midX, fromY - 42);
    this.threadGraphics.lineTo(toX, toY);
    this.threadGraphics.strokePath();
    this.threadGraphics.fillStyle(color, alpha);
    this.threadGraphics.fillCircle(toX, toY, 5);
  }

  private flyEvidenceLabel(label: string, selectedIndex: number) {
    if (selectedIndex < 0 || !this.evidenceSlots[selectedIndex]) return;
    const slot = this.evidenceSlots[selectedIndex];
    const flyer = this.add.text(730, 318, label, labelStyle("#fff8dd", 16)).setDepth(32).setBackgroundColor("#2f766c").setPadding(9, 5, 9, 5);
    this.tweens.add({
      targets: flyer,
      x: slot.x - 26,
      y: slot.y - 12,
      angle: -8,
      duration: 360,
      ease: "Cubic.Out",
      onComplete: () => flyer.destroy()
    });
  }

  private lampSweep() {
    this.tweens.add({ targets: this.lampBeam, x: { from: 650, to: 750 }, alpha: { from: 0.18, to: 0.52 }, duration: 360, yoyo: true, ease: "Sine.inOut" });
  }

  private flashReward() {
    if (!this.rewardImage) return;
    this.rewardImage.setVisible(true).setAlpha(0).setScale(0.4);
    this.tweens.add({ targets: this.rewardImage, alpha: 1, scale: 1, angle: 12, duration: 420, ease: "Back.Out" });
  }

  private emitParticles(x: number, y: number, color: number, count: number) {
    for (let index = 0; index < count; index += 1) {
      const dot = this.add.circle(x, y, Phaser.Math.Between(3, 7), color, 0.82).setDepth(29);
      this.tweens.add({
        targets: dot,
        x: x + Phaser.Math.Between(-80, 80),
        y: y + Phaser.Math.Between(-68, 42),
        alpha: 0,
        scale: 0.25,
        duration: Phaser.Math.Between(360, 760),
        ease: "Cubic.Out",
        onComplete: () => dot.destroy()
      });
    }
  }
}

function normalizeRequiredConfig(config: TimbreDetectiveSceneConfig): Required<TimbreDetectiveSceneConfig> {
  return {
    engine: "phaser_2d",
    scene_id: "timbre_detective_scene",
    runtime_shell: "timbre_detective_shell",
    game_feel: "animated_detective_caseboard",
    skin_id: config.skin_id || "sound_casebook",
    skin_play_mode: config.skin_play_mode || "casebook",
    mode: config.mode || "instrument_clue",
    clue_cases: config.clue_cases || [],
    suspect_cards: config.suspect_cards || [],
    evidence_tokens: config.evidence_tokens || [],
    evidence_required: config.evidence_required || 1,
    comparison_reason_required: Boolean(config.comparison_reason_required),
    dynamic_case_scene: true,
    input_actions: normalizeInputActions(config.input_actions),
    fx_profile: config.fx_profile || {},
    score_model: config.score_model || {},
    asset_manifest: config.asset_manifest || {}
  };
}

function normalizeRounds(value: unknown): Round[] {
  return Array.isArray(value) ? value.filter(isRecord).map((item) => ({ ...item })) : [];
}

function normalizeCards(value: unknown): Array<Record<string, string>> {
  return Array.isArray(value)
    ? value.filter(isRecord).map((item) => Object.fromEntries(Object.entries(item).map(([key, nextValue]) => [key, String(nextValue ?? "")])))
    : [];
}

function normalizeInputActions(value: unknown): string[] {
  const defaults = ["listen", "select_suspect", "toggle_evidence", "select_contrast_evidence", "submit_case", "next_case", "reset"];
  const provided = Array.isArray(value) ? value.map(String).filter(Boolean) : [];
  return Array.from(new Set([...provided, ...defaults]));
}

function normalizePlayMode(value: unknown, skinId: unknown): Required<TimbreDetectiveSceneConfig>["skin_play_mode"] {
  const text = String(value || "");
  if (["casebook", "museum", "forest", "studio", "theater"].includes(text)) return text as Required<TimbreDetectiveSceneConfig>["skin_play_mode"];
  return {
    sound_casebook: "casebook",
    museum_clues: "museum",
    forest_echo: "forest",
    studio_mixer: "studio",
    shadow_theater: "theater"
  }[String(skinId || "")] as Required<TimbreDetectiveSceneConfig>["skin_play_mode"] || "casebook";
}

function clampNumber(value: number, min: number, max: number, fallback: number) {
  if (!Number.isFinite(value)) return fallback;
  return Math.max(min, Math.min(max, value));
}

function labelStyle(color: string, fontSize: number, fixedWidth?: number): Phaser.Types.GameObjects.Text.TextStyle {
  return {
    color,
    fontFamily: "PingFang SC, Noto Sans SC, sans-serif",
    fontSize: `${fontSize}px`,
    fontStyle: "bold",
    ...(fixedWidth ? { fixedWidth, align: "center" } : {})
  };
}

function shortEvidenceLabel(label: string) {
  if (label.includes("滑音")) return "滑音";
  if (label.includes("擦弦")) return "擦弦";
  if (label.includes("稳定")) return "稳定";
  if (label.includes("明亮") || label.includes("亮度") || label.includes("高频")) return "亮度";
  if (label.includes("气流") || label.includes("吹奏")) return "气流";
  if (label.includes("共鸣") && label.includes("窄")) return "窄共鸣";
  if (label.includes("共鸣") && label.includes("宽")) return "宽共鸣";
  if (label.includes("连贯")) return "连贯";
  return label.length > 4 ? `${label.slice(0, 4)}…` : label;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
