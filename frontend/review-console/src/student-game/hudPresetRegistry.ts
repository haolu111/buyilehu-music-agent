export type HudPresetKey =
  | "energy_combo_target"
  | "demo_record_accuracy"
  | "speed_combo_finish"
  | "route_position_direction"
  | "reticle_hit_singback"
  | "clue_suspect_evidence"
  | "timeline_card_progress"
  | "constraint_checklist_progress";

export type HudPreset = {
  key: HudPresetKey;
  primaryMetric: string;
  secondaryMetric: string;
  feedbackStyle: "short_judgement" | "memory_trace" | "route_hint" | "target_hit" | "evidence_reasoning" | "form_route" | "constraint_checklist";
  playfieldProtection: "top_edge" | "side_panel" | "corner_badges" | "desk_overlay" | "bottom_cards";
};

export const HUD_PRESET_REGISTRY: Record<HudPresetKey, HudPreset> = {
  energy_combo_target: {
    key: "energy_combo_target",
    primaryMetric: "energy",
    secondaryMetric: "combo",
    feedbackStyle: "short_judgement",
    playfieldProtection: "top_edge"
  },
  demo_record_accuracy: {
    key: "demo_record_accuracy",
    primaryMetric: "accuracy",
    secondaryMetric: "memory_progress",
    feedbackStyle: "memory_trace",
    playfieldProtection: "side_panel"
  },
  speed_combo_finish: {
    key: "speed_combo_finish",
    primaryMetric: "speed",
    secondaryMetric: "combo",
    feedbackStyle: "short_judgement",
    playfieldProtection: "top_edge"
  },
  route_position_direction: {
    key: "route_position_direction",
    primaryMetric: "route_position",
    secondaryMetric: "pitch_direction",
    feedbackStyle: "route_hint",
    playfieldProtection: "corner_badges"
  },
  reticle_hit_singback: {
    key: "reticle_hit_singback",
    primaryMetric: "target_lock",
    secondaryMetric: "sing_back",
    feedbackStyle: "target_hit",
    playfieldProtection: "corner_badges"
  },
  clue_suspect_evidence: {
    key: "clue_suspect_evidence",
    primaryMetric: "evidence_count",
    secondaryMetric: "suspect_choice",
    feedbackStyle: "evidence_reasoning",
    playfieldProtection: "desk_overlay"
  },
  timeline_card_progress: {
    key: "timeline_card_progress",
    primaryMetric: "timeline_progress",
    secondaryMetric: "structure_cards",
    feedbackStyle: "form_route",
    playfieldProtection: "bottom_cards"
  },
  constraint_checklist_progress: {
    key: "constraint_checklist_progress",
    primaryMetric: "constraint_progress",
    secondaryMetric: "teacher_confirm",
    feedbackStyle: "constraint_checklist",
    playfieldProtection: "bottom_cards"
  }
};

export function getHudPreset(key: string | undefined): HudPreset | null {
  if (!key || !(key in HUD_PRESET_REGISTRY)) return null;
  return HUD_PRESET_REGISTRY[key as HudPresetKey];
}
