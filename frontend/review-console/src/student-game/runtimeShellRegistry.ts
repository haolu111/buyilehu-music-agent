import type { StudentGameState } from "./types";
import type { HudPresetKey } from "./hudPresetRegistry";

export type RuntimeShellKey =
  | "beat_guardian_shell"
  | "rhythm_echo_shell"
  | "race_timing_shell"
  | "pattern_builder_shell"
  | "pitch_ladder_map_shell"
  | "solfege_target_shell"
  | "timbre_detective_shell"
  | "form_treasure_shell"
  | "composition_puzzle_shell";

export type RuntimeShellMetadata = {
  key: RuntimeShellKey;
  templateId: string;
  gameGenre: string;
  pageClass: string;
  hudPreset: HudPresetKey;
  allowLessonRuntime: boolean;
  legacyShells?: string[];
};

export const RUNTIME_SHELL_REGISTRY: Record<RuntimeShellKey, RuntimeShellMetadata> = {
  beat_guardian_shell: {
    key: "beat_guardian_shell",
    templateId: "beat_guardian_core",
    gameGenre: "arcade_guardian",
    pageClass: "beat-arcade-page",
    hudPreset: "energy_combo_target",
    allowLessonRuntime: true,
    legacyShells: ["beat_guardian_arcade"]
  },
  rhythm_echo_shell: {
    key: "rhythm_echo_shell",
    templateId: "rhythm_echo_core",
    gameGenre: "memory_echo",
    pageClass: "rhythm-arcade-page",
    hudPreset: "demo_record_accuracy",
    allowLessonRuntime: true,
    legacyShells: ["rhythm_echo_arcade"]
  },
  race_timing_shell: {
    key: "race_timing_shell",
    templateId: "rhythm_family_core",
    gameGenre: "arcade_race",
    pageClass: "race-timing-page",
    hudPreset: "energy_combo_target",
    allowLessonRuntime: true
  },
  pattern_builder_shell: {
    key: "pattern_builder_shell",
    templateId: "rhythm_family_core",
    gameGenre: "rhythm_builder",
    pageClass: "pattern-builder-page",
    hudPreset: "timeline_card_progress",
    allowLessonRuntime: true
  },
  pitch_ladder_map_shell: {
    key: "pitch_ladder_map_shell",
    templateId: "pitch_ladder_core",
    gameGenre: "map_climb",
    pageClass: "pitch-map-page",
    hudPreset: "route_position_direction",
    allowLessonRuntime: true
  },
  solfege_target_shell: {
    key: "solfege_target_shell",
    templateId: "solfege_target_core",
    gameGenre: "target_range",
    pageClass: "solfege-range-page",
    hudPreset: "reticle_hit_singback",
    allowLessonRuntime: true
  },
  timbre_detective_shell: {
    key: "timbre_detective_shell",
    templateId: "timbre_detective_core",
    gameGenre: "detective_mystery",
    pageClass: "timbre-desk-page",
    hudPreset: "clue_suspect_evidence",
    allowLessonRuntime: true
  },
  form_treasure_shell: {
    key: "form_treasure_shell",
    templateId: "form_treasure_core",
    gameGenre: "form_treasure_map",
    pageClass: "form-treasure-page",
    hudPreset: "timeline_card_progress",
    allowLessonRuntime: true
  },
  composition_puzzle_shell: {
    key: "composition_puzzle_shell",
    templateId: "composition_puzzle_core",
    gameGenre: "constrained_composition_puzzle",
    pageClass: "composition-puzzle-page",
    hudPreset: "constraint_checklist_progress",
    allowLessonRuntime: true
  }
};

export function resolveRuntimeShellKey(state: StudentGameState, isLessonRuntime: boolean): RuntimeShellKey | null {
  const configuredShell = String(state.config?.runtime_shell || "");
  const templateId = String(state.template_id || state.config?.template_id || "");
  const match = Object.values(RUNTIME_SHELL_REGISTRY).find((shell) => {
    const shellMatches = shell.key === configuredShell || shell.legacyShells?.includes(configuredShell);
    return shellMatches && shell.templateId === templateId;
  });
  if (!match) return null;
  if (isLessonRuntime && !match.allowLessonRuntime) return null;
  return match.key;
}
