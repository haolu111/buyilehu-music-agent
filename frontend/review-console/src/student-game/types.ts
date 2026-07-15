export type Primitive = string | number | boolean | null;
export type LooseRecord = Record<string, unknown>;

export type StudentTaskCopy = {
  listen?: string;
  do?: string;
  pass?: string;
};

export type Round = {
  id?: string;
  label?: string;
  prompt?: string;
  target_sequence?: string[];
  sequence?: string[];
  answer?: string | string[];
  compare_with?: string | null;
  compare_prompt?: string;
  midi_offsets?: number[];
  stars?: number;
  sing_back_required?: boolean;
  mode?: string;
  target?: string;
  candidates?: string[];
  evidence_options?: string[];
  evidence_answer?: string[];
  contrast_evidence_options?: string[];
  contrast_evidence_answer?: string[];
  comparison_reason_required?: boolean;
  reason_frame?: {
    target?: string;
    contrast?: string;
    sentence?: string;
  };
  audio_profile?: TimbreAudioProfile | null;
  compare_audio_profile?: TimbreAudioProfile | null;
  playback_url?: string;
  audio_clip_url?: string;
  source_audio_url?: string;
  audio_url?: string;
  compare_playback_url?: string;
  compare_audio_clip_url?: string;
  compare_source_audio_url?: string;
  compare_audio_url?: string;
  family?: string;
  ai_teacher_clue?: string;
};

export type Material = {
  id: string;
  label?: string;
  pitch?: number;
  audio_clip_url?: string;
  source_audio_url?: string;
  audio_url?: string;
};

export type TimbreAudioProfile = {
  wave?: OscillatorType;
  frequency?: number;
  attack?: number;
  release?: number;
  brightness?: number;
  audio_url?: string;
  audio_clip_url?: string;
  source_audio_url?: string;
};

export type LessonPlayable = {
  operation_type?: string;
  prompt?: string;
  materials?: Material[];
  target_sequence?: string[];
  rounds?: Round[];
  feedback?: Record<string, string>;
};

export type MusicLogicToken = {
  id: string;
  height_index?: number;
  playback?: {
    midi?: number;
  };
};

export type MusicLogicContract = {
  tokens?: MusicLogicToken[];
  rounds?: Round[];
};

export type GameplayBlueprint = {
  student_facing_name?: string;
  player_verb?: string;
  prompt?: string;
  win_condition?: string;
  operation_type?: string;
  lesson_fit_applied?: boolean;
  experience_variant_id?: string;
  play_mode?: string;
  game_genre?: string;
  variant_game_genre?: string;
  scene_goal?: string;
  main_object?: string;
  interaction_feedback?: string;
  failure_feedback?: string;
  reward_loop?: string;
  playfield_composition?: string;
  game_variant_spec?: GameVariantSpec;
  music_entity_execution?: MusicEntityExecution;
};

export type ExperienceScript = {
  opening_hook?: string;
  tutorial?: {
    first_action_hint?: string;
  };
  progression?: Array<{
    round_id?: string;
    emotion?: string;
    reward?: string;
  }>;
  replay_hook?: string;
  closure_prompt?: string;
};

export type ThemePack = {
  theme_name?: string;
  skin_family?: "trail_world" | "race_world" | "casebook_world" | "pulse_world" | "target_world";
  layout_variant?: "trail_map" | "river_race" | "detective_desk" | "pulse_stage" | "target_arena";
  reward_token?: string;
  css_variables?: Record<string, string>;
  palette?: {
    primary?: string;
    accent?: string;
    background?: string;
    success?: string;
  };
  avatar?: {
    name?: string;
    role?: string;
  };
  scene?: {
    setting?: string;
    objective_noun?: string;
    progress_noun?: string;
    supporting_prop?: string;
  };
  experience_variant_id?: string;
  play_mode?: string;
  playfield_composition?: string;
  scene_goal?: string;
  main_object?: string;
  interaction_feedback?: string;
  failure_feedback?: string;
  reward_loop?: string;
};

export type PresentationPack = {
  output_kind?: "react_presentation_pack";
  engine_target?: "phaser_2d" | "react_dom";
  experience_variant_id?: string;
  play_mode?: string;
  game_genre?: string;
  variant_game_genre?: string;
  scene_goal?: string;
  main_object?: string;
  interaction_feedback?: string;
  failure_feedback?: string;
  reward_loop?: string;
  playfield_composition?: string;
  skin_family?: ThemePack["skin_family"];
  layout_variant?: ThemePack["layout_variant"];
  palette?: ThemePack["palette"];
  scene?: ThemePack["scene"];
  scene_skin?: {
    skin_id?: string;
    skin_family?: string;
    play_mode_hint?: string;
    experience_variant_id?: string;
    scene_goal?: string;
    main_object?: string;
    interaction_feedback?: string;
    failure_feedback?: string;
    reward_loop?: string;
  };
  animation_profile?: Record<string, string>;
  hud_layout?: {
    style?: string;
    shell?:
      | "arcade_game"
      | "standard_game"
      | "beat_guardian_shell"
      | "rhythm_echo_shell"
      | "pitch_ladder_map_shell"
      | "solfege_target_shell"
      | "timbre_detective_shell"
      | "form_treasure_shell"
      | "composition_puzzle_shell";
    persistent_cluster?: string;
    primary_action?: string;
    teacher_readable_feedback?: boolean;
    first_screen_density?: "playfield_only" | "minimal" | "balanced";
    teacher_notes_visibility?: "pause_or_result_only" | "collapsed" | "visible";
    feedback_max_chars?: number;
    play_mode?: string;
    playfield_composition?: string;
  };
  reward_style?: {
    token?: string;
  };
  motion_profile?: {
    tempo?: "gentle" | "snappy" | "measured";
  };
  css_variables?: Record<string, string>;
};

export type MusicEntityApplication = {
  template_id?: string;
  canonical_id?: string;
  entity_type?: string;
  label?: string;
  game_parameters?: LooseRecord;
  slot_bindings?: LooseRecord;
  requires_teacher_confirmation?: boolean;
  confirmation_reason?: string;
};

export type MusicEntityConfirmationGate = {
  gate_type?: string;
  entity_type?: string;
  canonical_id?: string;
  label?: string;
  status?: string;
  confidence?: number;
  extraction_basis?: string;
  source_span?: LooseRecord;
  proposed_value?: unknown;
  confirmed_value?: unknown;
  confirmation_error?: string;
  reason?: string;
};

export type MusicEntityExecution = {
  contract_schema_version?: string;
  music_entity?: {
    canonical_id?: string;
    label?: string;
    entity_type?: string;
  };
  variant_parameters?: LooseRecord;
  slot_bindings?: LooseRecord;
  entity_application?: MusicEntityApplication;
  execution_plan?: {
    version?: string;
    template_id?: string;
    status?: string;
    blocked_reasons?: string[];
    entity_type?: string;
    canonical_id?: string;
    parameter_writes?: Array<{ path?: string; value?: unknown }>;
    slot_writes?: Array<{ path?: string; value?: unknown }>;
    entity_application_writes?: {
      game_parameters?: LooseRecord;
      slot_bindings?: LooseRecord;
    };
    requires_teacher_confirmation?: boolean;
    template_capability_status?: string;
  };
  confirmation_gates?: MusicEntityConfirmationGate[];
  requires_teacher_confirmation?: boolean;
  confirmation_reason?: string;
};

export type GameVariantSpec = MusicEntityExecution & {
  version?: string;
  template_id?: string;
  source_of_truth?: string;
  entity_candidates?: LooseRecord[];
};

export type TemplatePoseKey = "idle" | "action" | "miss" | "win";
export type TemplatePropKey = `prop-${string}`;
export type TemplateRewardKey = `ui-${string}`;
export type TemplateInteractionState = "idle" | "listening" | "aiming" | "hit" | "miss" | "success";
export type TemplateMusicMechanicKind = "beat" | "rhythm" | "solfege" | "timbre" | "form";

export type TemplateVisualPack = {
  background?: string;
  mission_board?: string;
  mission_badge?: string;
  poses?: Partial<Record<TemplatePoseKey, string>>;
  props?: string[];
  rewards?: string[];
  sourcePack?: string;
  license?: string;
};

export type TemplateCharacterPresenterOptions = {
  poseKeys: Partial<Record<TemplatePoseKey, string>>;
  x: number;
  y: number;
  displaySize: number;
  preserveAspectRatio?: boolean;
  depth?: number;
  reducedMotion?: boolean;
  stableScale?: boolean;
};

export type StudentGameState = {
  workflow?: {
    workflow_kind?: string;
    game_variant_spec?: GameVariantSpec;
    gameplay_blueprint?: GameplayBlueprint;
    experience_script?: ExperienceScript;
    theme_pack?: ThemePack;
    presentation_pack?: PresentationPack;
    render_spec?: {
      music_entity_execution?: MusicEntityExecution;
      [key: string]: unknown;
    };
    intervention_trace?: Array<Record<string, string>>;
  };
  instance?: {
    template_label?: string;
    student_task?: Record<string, string>;
  };
  proposal_card?: {
    title?: string;
    transfer_task?: string;
  };
  config?: LooseRecord;
  student_task_copy?: StudentTaskCopy;
  music_reason_prompts?: Record<string, string>;
  result_transfer_prompt?: string;
  age_ui_profile?: "lower_primary" | "upper_primary" | "junior_middle";
  template_id?: string;
  lesson_game_contract?: {
    game_name?: string;
    game_mechanic?: string;
    playable_game?: LessonPlayable;
    music_logic_contract?: MusicLogicContract;
  };
};
