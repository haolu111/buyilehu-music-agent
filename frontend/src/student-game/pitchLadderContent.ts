import type { PitchDirection } from "./pitchLadderSystem";

export type PitchLadderSkinPlayMode = "mountain" | "cloud" | "bamboo" | "lantern";

export type PitchLadderAnimationKey = "idle" | "run" | "walk" | "jump" | "fall" | "win" | "fail";

export type PitchLadderLevelStep = {
  id: string;
  sequence: string[];
  answer: PitchDirection;
  start: RoutePoint;
  choices: Record<PitchDirection, RoutePoint>;
};

export type RoutePoint = {
  x: number;
  y: number;
};

export type PitchLadderContentManifest = {
  manifestVersion: 1;
  assetProfile: "open_sprite_atlas_v1";
  art?: {
    backgroundKey: string;
    background: string;
    heroSeedKey: string;
    heroSeed: string;
    heroPosesKey: string;
    heroPoses: string;
    propsSheetKey: string;
    propsSheet: string;
  };
  hero: {
    key: string;
    animations: Record<PitchLadderAnimationKey, string>;
    frameSize: { width: number; height: number };
    anchor: { x: number; y: number };
  };
  heroSprite?: {
    sheetKey: string;
    sheet: string;
    frameWidth: number;
    frameHeight: number;
    displayHeight: number;
    footOffsetY?: number;
    anchor: { x: number; y: number };
    animations: Record<PitchLadderAnimationKey, { frames: number[]; frameRate: number; repeat: number }>;
  };
  environment: {
    backgroundLayers: string[];
    platformKey: string;
    goalKey: string;
  };
  mountainRoute?: {
    entry: RoutePoint;
    steps: Array<{
      start: RoutePoint;
      choices: Record<PitchDirection, RoutePoint>;
    }>;
    summit: RoutePoint;
  };
  ui: {
    buttonSkin: string;
    rewardIcon: string;
    energyFrame: string;
  };
  fx: {
    hit: string;
    miss: string;
    reward: string;
    stageClear: string;
    voiceTrail: string;
  };
  audio: {
    targetTone: string;
    hit: string;
    miss: string;
    reward: string;
  };
};

type PitchLadderHeroSprite = NonNullable<PitchLadderContentManifest["heroSprite"]>;

const BASE_HERO = {
  key: "pitch_climber",
  animations: {
    idle: "pitch_climber_idle",
    run: "pitch_climber_run",
    walk: "pitch_climber_walk",
    jump: "pitch_climber_jump",
    fall: "pitch_climber_fall",
    win: "pitch_climber_win",
    fail: "pitch_climber_fail"
  },
  frameSize: { width: 96, height: 112 },
  anchor: { x: 0.5, y: 0.86 }
};

const BASE_HERO_SPRITE_ANIMATIONS: PitchLadderHeroSprite["animations"] = {
  idle: { frames: [0, 1, 2, 3], frameRate: 4, repeat: -1 },
  walk: { frames: [4, 5, 6, 7], frameRate: 8, repeat: -1 },
  run: { frames: [4, 5, 6, 7], frameRate: 8, repeat: -1 },
  jump: { frames: [8, 9], frameRate: 7, repeat: 0 },
  fall: { frames: [10, 11], frameRate: 7, repeat: 0 },
  win: { frames: [12, 13], frameRate: 5, repeat: 2 },
  fail: { frames: [14, 15], frameRate: 5, repeat: 1 }
};

function heroSprite(sheetKey: string, sheet: string, displayHeight: number, footOffsetY: number): PitchLadderHeroSprite {
  return {
    sheetKey,
    sheet,
    frameWidth: 192,
    frameHeight: 224,
    displayHeight,
    footOffsetY,
    anchor: { x: 0.5, y: 1 },
    animations: BASE_HERO_SPRITE_ANIMATIONS
  };
}

const BASE_UI = {
  buttonSkin: "golden_arcade_button",
  rewardIcon: "melody_gem",
  energyFrame: "heart_energy_frame"
};

const BASE_FX = {
  hit: "note_spark",
  miss: "slide_dust",
  reward: "gem_fly",
  stageClear: "summit_flash",
  voiceTrail: "voice_ribbon"
};

const BASE_AUDIO = {
  targetTone: "triangle_pitch_prompt",
  hit: "soft_chime",
  miss: "rubber_slide",
  reward: "gem_collect"
};

export const PITCH_LADDER_SKIN_MANIFESTS: Record<"mountain" | "cloud" | "bamboo", PitchLadderContentManifest> = {
  mountain: {
  manifestVersion: 1,
  assetProfile: "open_sprite_atlas_v1",
  art: {
    backgroundKey: "pitch_ladder_mountain_bg",
    background: "/static/assets/game-packs/pitch-ladder/mountain/backgrounds/mountain-pitch-path-bg.png",
    heroSeedKey: "pitch_ladder_explorer_seed",
    heroSeed: "/static/assets/game-packs/pitch-ladder/mountain/characters/pitch-explorer-seed.png",
    heroPosesKey: "pitch_ladder_explorer_poses",
    heroPoses: "/static/assets/game-packs/pitch-ladder/mountain/characters/pitch-explorer-poses.png",
    propsSheetKey: "pitch_ladder_mountain_props",
    propsSheet: "/static/assets/game-packs/pitch-ladder/mountain/props/mountain-props.png"
  },
  hero: BASE_HERO,
  heroSprite: heroSprite(
    "pitch_ladder_mountain_action_strip",
    "/static/assets/game-packs/pitch-ladder/mountain/characters/pitch-explorer-action-strip.png",
    112,
    12
  ),
  environment: {
    backgroundLayers: ["sky_gradient", "far_mountains", "near_mountains", "cloud_lane"],
    platformKey: "singing_platform",
    goalKey: "summit_flag"
  },
  ui: BASE_UI,
  fx: BASE_FX,
  audio: BASE_AUDIO
  },
  cloud: {
  manifestVersion: 1,
  assetProfile: "open_sprite_atlas_v1",
  art: {
    backgroundKey: "pitch_ladder_cloud_bg",
    background: "/static/assets/game-packs/pitch-ladder/cloud/backgrounds/cloud-elevator-bg.png",
    heroSeedKey: "pitch_ladder_cloud_hero",
    heroSeed: "/static/assets/game-packs/pitch-ladder/cloud/characters/cloud-explorer-poses-transparent.png",
    heroPosesKey: "pitch_ladder_cloud_poses",
    heroPoses: "/static/assets/game-packs/pitch-ladder/cloud/characters/cloud-explorer-poses-transparent.png",
    propsSheetKey: "pitch_ladder_cloud_props",
    propsSheet: "/static/assets/game-packs/pitch-ladder/cloud/props/cloud-elevator-props.png"
  },
  hero: BASE_HERO,
  heroSprite: heroSprite(
    "pitch_ladder_cloud_action_strip",
    "/static/assets/game-packs/pitch-ladder/cloud/characters/cloud-explorer-action-strip.png",
    132,
    18
  ),
  environment: {
    backgroundLayers: ["sky_gradient", "cloud_lane", "floating_islands"],
    platformKey: "cloud_platform",
    goalKey: "cloud_gate"
  },
  ui: BASE_UI,
  fx: BASE_FX,
  audio: BASE_AUDIO
  },
  bamboo: {
  manifestVersion: 1,
  assetProfile: "open_sprite_atlas_v1",
  art: {
    backgroundKey: "pitch_ladder_bamboo_bg",
    background: "/static/assets/game-packs/pitch-ladder/bamboo/backgrounds/bamboo-ladder-bg.png",
    heroSeedKey: "pitch_ladder_bamboo_hero",
    heroSeed: "/static/assets/game-packs/pitch-ladder/bamboo/characters/bamboo-climber-poses-transparent.png",
    heroPosesKey: "pitch_ladder_bamboo_poses",
    heroPoses: "/static/assets/game-packs/pitch-ladder/bamboo/characters/bamboo-climber-poses-transparent.png",
    propsSheetKey: "pitch_ladder_bamboo_props",
    propsSheet: "/static/assets/game-packs/pitch-ladder/bamboo/props/bamboo-ladder-props.png"
  },
  hero: BASE_HERO,
  heroSprite: heroSprite(
    "pitch_ladder_bamboo_action_strip",
    "/static/assets/game-packs/pitch-ladder/bamboo/characters/bamboo-climber-action-strip.png",
    138,
    20
  ),
  environment: {
    backgroundLayers: ["bamboo_forest", "waterfall", "leaf_platforms"],
    platformKey: "bamboo_platform",
    goalKey: "bamboo_crown"
  },
  ui: BASE_UI,
  fx: BASE_FX,
  audio: BASE_AUDIO
  }
};

export const PITCH_LADDER_CONTENT_MANIFEST: PitchLadderContentManifest = PITCH_LADDER_SKIN_MANIFESTS.mountain;

const PITCH_LADDER_NATIVE_ROUTE_SKINS = ["mountain", "cloud", "bamboo"] as const;

export const PITCH_LADDER_SKIN_ROUTES: Record<"mountain" | "cloud" | "bamboo", NonNullable<PitchLadderContentManifest["mountainRoute"]>> = {
  mountain: {
    entry: { x: 0.49, y: 0.82 },
    steps: [
      {
        start: { x: 0.49, y: 0.82 },
        choices: {
          higher: { x: 0.66, y: 0.74 },
          same: { x: 0.56, y: 0.82 },
          lower: { x: 0.31, y: 0.82 }
        }
      },
      {
        start: { x: 0.66, y: 0.74 },
        choices: {
          higher: { x: 0.72, y: 0.62 },
          same: { x: 0.72, y: 0.73 },
          lower: { x: 0.56, y: 0.82 }
        }
      },
      {
        start: { x: 0.72, y: 0.62 },
        choices: {
          higher: { x: 0.76, y: 0.51 },
          same: { x: 0.79, y: 0.62 },
          lower: { x: 0.66, y: 0.74 }
        }
      },
      {
        start: { x: 0.76, y: 0.51 },
        choices: {
          higher: { x: 0.80, y: 0.40 },
          same: { x: 0.83, y: 0.51 },
          lower: { x: 0.72, y: 0.62 }
        }
      },
      {
        start: { x: 0.80, y: 0.40 },
        choices: {
          higher: { x: 0.77, y: 0.13 },
          same: { x: 0.84, y: 0.40 },
          lower: { x: 0.76, y: 0.51 }
        }
      }
    ],
    summit: { x: 0.77, y: 0.13 }
  },
  cloud: {
    entry: { x: 0.22, y: 0.80 },
    steps: [
      { start: { x: 0.22, y: 0.80 }, choices: { higher: { x: 0.39, y: 0.70 }, same: { x: 0.37, y: 0.80 }, lower: { x: 0.18, y: 0.84 } } },
      { start: { x: 0.39, y: 0.70 }, choices: { higher: { x: 0.48, y: 0.60 }, same: { x: 0.51, y: 0.70 }, lower: { x: 0.31, y: 0.80 } } },
      { start: { x: 0.48, y: 0.60 }, choices: { higher: { x: 0.59, y: 0.51 }, same: { x: 0.62, y: 0.60 }, lower: { x: 0.39, y: 0.70 } } },
      { start: { x: 0.59, y: 0.51 }, choices: { higher: { x: 0.68, y: 0.43 }, same: { x: 0.72, y: 0.52 }, lower: { x: 0.48, y: 0.60 } } },
      { start: { x: 0.68, y: 0.43 }, choices: { higher: { x: 0.82, y: 0.20 }, same: { x: 0.76, y: 0.38 }, lower: { x: 0.59, y: 0.51 } } }
    ],
    summit: { x: 0.82, y: 0.20 }
  },
  bamboo: {
    entry: { x: 0.24, y: 0.80 },
    steps: [
      { start: { x: 0.24, y: 0.80 }, choices: { higher: { x: 0.49, y: 0.59 }, same: { x: 0.40, y: 0.73 }, lower: { x: 0.29, y: 0.82 } } },
      { start: { x: 0.49, y: 0.59 }, choices: { higher: { x: 0.60, y: 0.55 }, same: { x: 0.54, y: 0.63 }, lower: { x: 0.40, y: 0.73 } } },
      { start: { x: 0.60, y: 0.55 }, choices: { higher: { x: 0.68, y: 0.48 }, same: { x: 0.68, y: 0.56 }, lower: { x: 0.50, y: 0.65 } } },
      { start: { x: 0.68, y: 0.48 }, choices: { higher: { x: 0.75, y: 0.37 }, same: { x: 0.77, y: 0.47 }, lower: { x: 0.60, y: 0.55 } } },
      { start: { x: 0.75, y: 0.37 }, choices: { higher: { x: 0.82, y: 0.18 }, same: { x: 0.79, y: 0.29 }, lower: { x: 0.68, y: 0.48 } } }
    ],
    summit: { x: 0.82, y: 0.18 }
  }
};

export function buildPitchLadderLevelSteps(rounds: Array<{ sequence?: string[]; answer?: string | string[] }>, skinPlayMode: PitchLadderSkinPlayMode = "mountain"): PitchLadderLevelStep[] {
  const safeRounds = rounds.length ? rounds : [{ sequence: ["do", "re"], answer: "higher" }];
  const route = PITCH_LADDER_SKIN_ROUTES[skinPlayMode as keyof typeof PITCH_LADDER_SKIN_ROUTES] || PITCH_LADDER_SKIN_ROUTES.mountain;
  return safeRounds.map((round, index) => {
    const answer = normalizeDirection(round.answer);
    const progress = index / Math.max(1, safeRounds.length - 1);
    const routeStep = route?.steps[Math.min(index, route.steps.length - 1)];
    const start = routeStep?.start || { x: 0.18 + progress * 0.55, y: 0.74 - progress * 0.32 };
    const choices = routeStep?.choices;
    return {
      id: `pitch-step-${index + 1}`,
      sequence: (round.sequence || []).map(String),
      answer,
      start,
      choices: {
        higher: clampPoint(choices?.higher || { x: start.x + 0.16, y: start.y - 0.12 }),
        same: clampPoint(choices?.same || { x: start.x + 0.16, y: start.y }),
        lower: clampPoint(choices?.lower || { x: start.x + 0.16, y: start.y + 0.12 })
      }
    };
  });
}

export function usesNativePitchLadderMapRoute(skinPlayMode: PitchLadderSkinPlayMode | undefined, routeStyle: string | undefined): boolean {
  return PITCH_LADDER_NATIVE_ROUTE_SKINS.includes(skinPlayMode as (typeof PITCH_LADDER_NATIVE_ROUTE_SKINS)[number])
    && (routeStyle || "map_native") === "map_native";
}

export function buildPitchLadderNativeRoutePoints(
  count: number,
  skinPlayMode: PitchLadderSkinPlayMode = "mountain",
  width = 1,
  height = 1
): RoutePoint[] {
  const route = PITCH_LADDER_SKIN_ROUTES[skinPlayMode as keyof typeof PITCH_LADDER_SKIN_ROUTES];
  if (!route || count <= 0) return [];
  const anchors = dedupeRoutePoints([
    route.entry,
    ...route.steps.map((step) => step.choices.higher),
    route.summit
  ]);
  if (anchors.length === 1) return Array.from({ length: count }, () => routePointToCanvas(anchors[0], width, height));
  return Array.from({ length: count }, (_, index) => {
    const progress = count === 1 ? 0 : index / (count - 1);
    return routePointToCanvas(pointAlongRoute(anchors, progress), width, height);
  });
}

export function routePointToCanvas(point: RoutePoint, width: number, height: number): RoutePoint {
  return { x: point.x * width, y: point.y * height };
}

function dedupeRoutePoints(points: RoutePoint[]): RoutePoint[] {
  return points.filter((point, index) => {
    const previous = points[index - 1];
    return !previous || Math.abs(previous.x - point.x) > 0.001 || Math.abs(previous.y - point.y) > 0.001;
  });
}

function pointAlongRoute(points: RoutePoint[], progress: number): RoutePoint {
  const segments = points.slice(0, -1).map((start, index) => {
    const end = points[index + 1];
    const length = Math.hypot(end.x - start.x, end.y - start.y);
    return { start, end, length };
  });
  const total = segments.reduce((sum, segment) => sum + segment.length, 0);
  let remaining = Math.max(0, Math.min(1, progress)) * total;
  for (const segment of segments) {
    if (remaining <= segment.length || segment === segments[segments.length - 1]) {
      const t = segment.length === 0 ? 0 : remaining / segment.length;
      return {
        x: segment.start.x + (segment.end.x - segment.start.x) * t,
        y: segment.start.y + (segment.end.y - segment.start.y) * t
      };
    }
    remaining -= segment.length;
  }
  return points[points.length - 1];
}

function clampPoint(point: RoutePoint): RoutePoint {
  return {
    x: Math.max(0.08, Math.min(0.9, point.x)),
    y: Math.max(0.24, Math.min(0.84, point.y))
  };
}

function normalizeDirection(answer: string | string[] | undefined): PitchDirection {
  const value = Array.isArray(answer) ? String(answer[0] || "") : String(answer || "");
  if (value === "same" || value === "lower") return value;
  return "higher";
}
