import Phaser from "phaser";
import type { TemplateCharacterPresenterOptions, TemplatePoseKey } from "./types";

export class TemplateCharacterPresenter {
  private readonly scene: Phaser.Scene;
  private readonly poseKeys: Partial<Record<TemplatePoseKey, string>>;
  private readonly reducedMotion: boolean;
  private readonly stableScale: boolean;
  private readonly preserveAspectRatio: boolean;
  private readonly displaySize: number;
  private readonly baseX: number;
  private readonly baseY: number;
  private readonly container: Phaser.GameObjects.Container;
  private currentSprite: Phaser.GameObjects.Image | null = null;
  private nextSprite: Phaser.GameObjects.Image | null = null;
  private currentPose: TemplatePoseKey = "idle";
  private idleTween: Phaser.Tweens.Tween | null = null;

  constructor(scene: Phaser.Scene, options: TemplateCharacterPresenterOptions) {
    this.scene = scene;
    this.poseKeys = options.poseKeys;
    this.reducedMotion = Boolean(options.reducedMotion);
    this.stableScale = Boolean(options.stableScale);
    this.preserveAspectRatio = Boolean(options.preserveAspectRatio);
    this.displaySize = options.displaySize;
    this.baseX = options.x;
    this.baseY = options.y;
    this.container = scene.add.container(options.x, options.y).setDepth(options.depth ?? 4);
    const idleKey = this.resolvePoseKey("idle");
    if (idleKey) {
      this.currentSprite = this.createSprite(idleKey, 1);
      this.container.add(this.currentSprite);
    }
    this.startIdleLoop();
  }

  transitionTo(pose: TemplatePoseKey, reason: "idle" | "hit" | "miss" | "success" | "listen" = "idle") {
    const key = this.resolvePoseKey(pose);
    if (!key || !this.currentSprite) return;
    if (this.currentPose === pose) {
      return;
    }
    this.currentPose = pose;
    if (this.reducedMotion || this.stableScale) {
      this.nextSprite?.destroy();
      this.nextSprite = null;
      this.currentSprite.setTexture(key);
      this.applyDisplaySize(this.currentSprite);
      this.currentSprite.setAlpha(reason === "miss" ? 0.84 : 1);
      this.playAccent(reason);
      this.startIdleLoop();
      return;
    }

    this.nextSprite?.destroy();
    this.nextSprite = this.createSprite(key, 0);
    this.container.add(this.nextSprite);
    const outgoing = this.currentSprite;
    const incoming = this.nextSprite;
    const baseScaleX = incoming.scaleX;
    const baseScaleY = incoming.scaleY;
    if (!this.stableScale) {
      const accentScale = reason === "success" ? 1.08 : reason === "hit" || reason === "listen" ? 1.04 : 0.98;
      incoming.setScale(baseScaleX * accentScale, baseScaleY * accentScale);
    }
    incoming.setY(reason === "success" ? -10 : reason === "miss" ? 7 : -2);
    this.scene.tweens.add({
      targets: outgoing,
      alpha: 0,
      duration: 180,
      ease: "Cubic.Out",
      onComplete: () => outgoing.destroy()
    });
    this.scene.tweens.add({
      targets: incoming,
      alpha: reason === "miss" ? 0.84 : 1,
      y: 0,
      ...(this.stableScale ? {} : { scaleX: baseScaleX, scaleY: baseScaleY }),
      duration: 240,
      ease: "Back.Out",
      onComplete: () => {
        this.currentSprite = incoming;
        this.nextSprite = null;
        this.playAccent(reason);
        this.startIdleLoop();
      }
    });
  }

  setAlpha(alpha: number) {
    this.container.setAlpha(alpha);
  }

  setVisible(visible: boolean) {
    this.container.setVisible(visible);
  }

  pulse(reason: "hit" | "miss" | "success" | "listen" = "hit") {
    this.playAccent(reason);
  }

  destroy() {
    this.idleTween?.stop();
    this.container.destroy(true);
  }

  private createSprite(key: string, alpha: number) {
    const sprite = this.scene.add.image(0, 0, key).setAlpha(alpha);
    this.applyDisplaySize(sprite);
    return sprite;
  }

  private applyDisplaySize(sprite: Phaser.GameObjects.Image) {
    if (!this.preserveAspectRatio) {
      sprite.setDisplaySize(this.displaySize, this.displaySize);
      return;
    }
    const width = sprite.width || this.displaySize;
    const height = sprite.height || this.displaySize;
    const scale = this.displaySize / Math.max(width, height, 1);
    sprite.setScale(scale);
  }

  private resolvePoseKey(pose: TemplatePoseKey) {
    const key = this.poseKeys[pose] || this.poseKeys.idle;
    return key && this.scene.textures.exists(key) ? key : undefined;
  }

  private startIdleLoop() {
    if (this.reducedMotion) return;
    this.scene.tweens.killTweensOf(this.container);
    this.idleTween?.stop();
    this.container.setPosition(this.baseX, this.baseY).setAngle(0).setScale(1);
    this.idleTween = this.scene.tweens.add({
      targets: this.container,
      y: this.baseY - 5,
      ...(this.stableScale ? {} : { scaleY: 1.025 }),
      duration: 960,
      yoyo: true,
      repeat: -1,
      ease: "Sine.inOut"
    });
  }

  private playAccent(reason: "idle" | "hit" | "miss" | "success" | "listen") {
    if (this.reducedMotion || reason === "idle") return;
    this.idleTween?.pause();
    if (reason === "miss") {
      this.scene.tweens.add({
        targets: this.container,
        x: { from: this.baseX - 8, to: this.baseX },
        angle: { from: -4, to: 0 },
        duration: 90,
        yoyo: true,
        repeat: 2,
        ease: "Sine.inOut",
        onComplete: () => {
          this.container.setPosition(this.baseX, this.baseY).setAngle(0);
          this.idleTween?.resume();
        }
      });
      return;
    }
    this.scene.tweens.add({
      targets: this.container,
      y: this.baseY + (reason === "success" ? -24 : -10),
      ...(this.stableScale ? {} : {
        scaleX: reason === "success" ? 1.12 : 1.08,
        scaleY: reason === "success" ? 1.12 : 1.04
      }),
      duration: reason === "success" ? 260 : 150,
      yoyo: true,
      ease: "Back.Out",
      onComplete: () => {
        this.container.setPosition(this.baseX, this.baseY).setAngle(0).setScale(1);
        this.idleTween?.resume();
      }
    });
  }
}
