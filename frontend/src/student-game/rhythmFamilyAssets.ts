import type { LooseRecord } from "./types";

export type RhythmFamilyAssetManifest = {
  background: string;
  hero_poses: string;
  props: string;
  ui_rewards: string;
  prompt?: string;
};

const ROOT = "/static/assets/game-packs/rhythm-family";

const DEFAULT_VARIANT = "echo_replay";

const FALLBACKS: Record<string, RhythmFamilyAssetManifest> = {
  echo_replay: manifestFor("echo_replay", "节奏复刻素材包"),
  beat_guard: manifestFor("beat_guard", "节拍守卫素材包"),
  race_timing: manifestFor("race_timing", "节拍竞速素材包"),
  pattern_builder: manifestFor("pattern_builder", "节奏工坊素材包")
};

function manifestFor(variant: string, prompt: string): RhythmFamilyAssetManifest {
  return {
    background: `${ROOT}/${variant}/background.png`,
    hero_poses: `${ROOT}/${variant}/hero-poses.png`,
    props: `${ROOT}/${variant}/props.png`,
    ui_rewards: `${ROOT}/${variant}/ui-rewards.png`,
    prompt
  };
}

export function rhythmFamilyVariantId(config: LooseRecord | undefined): string {
  const nested: LooseRecord = config?.scene_config && typeof config.scene_config === "object" ? (config.scene_config as LooseRecord) : {};
  const raw = String(config?.gameplay_variant_id || nested.gameplay_variant_id || DEFAULT_VARIANT);
  return raw in FALLBACKS ? raw : DEFAULT_VARIANT;
}

export function rhythmFamilyAssets(config: LooseRecord | undefined): RhythmFamilyAssetManifest {
  const variant = rhythmFamilyVariantId(config);
  const nested: LooseRecord = config?.scene_config && typeof config.scene_config === "object" ? (config.scene_config as LooseRecord) : {};
  const raw = (config?.asset_manifest || nested.asset_manifest || {}) as Partial<RhythmFamilyAssetManifest>;
  const fallback = FALLBACKS[variant] || FALLBACKS[DEFAULT_VARIANT];
  return {
    background: String(raw.background || fallback.background),
    hero_poses: String(raw.hero_poses || fallback.hero_poses),
    props: String(raw.props || fallback.props),
    ui_rewards: String(raw.ui_rewards || fallback.ui_rewards),
    prompt: String(raw.prompt || fallback.prompt || "")
  };
}
