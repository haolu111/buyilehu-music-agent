import type { LooseRecord, TemplatePoseKey, TemplateVisualPack } from "./types";

const TEMPLATE_PACKS: Record<string, string> = {
  beat_guardian_core: "节拍守卫",
  rhythm_echo_core: "节奏复刻",
  solfege_target_core: "唱名打靶",
  timbre_detective_core: "音色侦探",
  form_treasure_core: "曲式寻宝",
  composition_puzzle_core: "composition-puzzle"
};

export function templateVisualPackForConfig(config: LooseRecord | undefined, templateId?: string): TemplateVisualPack {
  const nested = isRecord(config?.scene_config) ? config?.scene_config : {};
  const manifest = readManifest(config?.asset_manifest) || readManifest(nested?.asset_manifest);
  if (manifest) return manifest;

  const resolvedTemplateId = String(templateId || config?.template_id || nested?.template_id || "");
  const pack = TEMPLATE_PACKS[resolvedTemplateId];
  return pack ? packManifest(pack) : {};
}

export function templatePose(pack: TemplateVisualPack | undefined, pose: TemplatePoseKey): string | undefined {
  return pack?.poses?.[pose] || pack?.poses?.idle;
}

export function templateProp(pack: TemplateVisualPack | undefined, index: number): string | undefined {
  return pack?.props?.[Math.max(0, index)];
}

export function templateReward(pack: TemplateVisualPack | undefined, index: number): string | undefined {
  return pack?.rewards?.[Math.max(0, index)];
}

function packManifest(pack: string): TemplateVisualPack {
  const root = `/static/assets/game-packs/${pack}`;
  const extracted = `${root}/extracted`;
  return {
    background: `${root}/background.png`,
    mission_board: "/static/assets/game-packs/mission-board.svg",
    mission_badge: "/static/assets/game-packs/mission-badge.svg",
    poses: {
      idle: `${extracted}/pose-01-idle.png`,
      action: `${extracted}/pose-02-action.png`,
      miss: `${extracted}/pose-03-miss.png`,
      win: `${extracted}/pose-04-win.png`
    },
    props: Array.from({ length: 12 }, (_, index) => `${extracted}/prop-${String(index + 1).padStart(2, "0")}.png`),
    rewards: Array.from({ length: 12 }, (_, index) => `${extracted}/ui-${String(index + 1).padStart(2, "0")}.png`),
    sourcePack: pack,
    license: "local_generated_assets"
  };
}

function readManifest(value: unknown): TemplateVisualPack | null {
  if (!isRecord(value)) return null;
  return {
    background: typeof value.background === "string" ? value.background : undefined,
    mission_board: typeof value.mission_board === "string" ? value.mission_board : undefined,
    mission_badge: typeof value.mission_badge === "string" ? value.mission_badge : undefined,
    poses: isRecord(value.poses) ? {
      idle: stringValue(value.poses.idle),
      action: stringValue(value.poses.action),
      miss: stringValue(value.poses.miss),
      win: stringValue(value.poses.win)
    } : undefined,
    props: Array.isArray(value.props) ? value.props.map(String).filter(Boolean) : undefined,
    rewards: Array.isArray(value.rewards) ? value.rewards.map(String).filter(Boolean) : undefined,
    sourcePack: typeof value.sourcePack === "string" ? value.sourcePack : undefined,
    license: typeof value.license === "string" ? value.license : undefined
  };
}

function stringValue(value: unknown): string | undefined {
  return typeof value === "string" && value ? value : undefined;
}

function isRecord(value: unknown): value is LooseRecord {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
