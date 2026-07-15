import { Badge, Button, Container, Flex, Grid, Heading, Text } from "@radix-ui/themes";
import { Boxes, ExternalLink, GraduationCap, Image, LibraryBig, Music2, Play, School, Wand2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import "./primaryActivity.css";

type ToolkitSelection = {
  components: string[];
  teaching_aids: string[];
  virtual_instruments: string[];
  game_templates: string[];
};

type EducationAlignment = {
  primary_competency: string;
  secondary_competency?: string;
  student_practices: string[];
  music_elements: string[];
  teaching_stages: string[];
  grade_fit: Record<string, string>;
  pedagogy_notes: string[];
};

type ToolkitCatalogItem = {
  activity_id: string;
  activity_name: string;
  grade_bands: string[];
  student_music_behaviors: string[];
  education_alignment: EducationAlignment;
  selected: ToolkitSelection;
  why: string;
};

type TeachingAidSummary = {
  aid_id: string;
  name: string;
  replace_physical_aid: string;
  material_entities?: string[];
  components?: string[];
  student_actions?: string[];
  teacher_controls?: string[];
  real_photo_required?: boolean;
  doubao_required?: boolean;
  image_gen_required?: boolean;
  asset_pack_required?: string;
  asset_policy?: {
    source: string;
    note: string;
  };
  quality_gates?: string[];
};

type VirtualInstrumentSummary = {
  instrument_id: string;
  name: string;
  replace_physical_instrument: string;
  input_modes?: string[];
  sound_source?: string;
  pitch_set?: string[];
  constraints?: Record<string, unknown>;
  teacher_controls?: string[];
  quality_gates?: string[];
  runtime_contract?: {
    audio_unlock_required: boolean;
    student_event_schema: string[];
    quality_gates: string[];
  };
};

type GeneratedOutputTask = {
  kind: string;
  asset_id: string;
  file: string;
  save_path: string;
  suggested_prompt_suffix?: string;
  doubao_prompt?: string;
  image_gen_prompt?: string;
  postprocess?: string;
};

type GeneratedAssetTask = {
  asset_pack_id: string;
  label: string;
  status: "pending_generation" | string;
  provider?: string;
  image2_url?: string;
  image2_prompt?: string;
  image_gen_prompt?: string;
  save_policy: string;
  outputs: GeneratedOutputTask[];
};

type LibraryQualityReport = {
  status: "pass" | "fail" | string;
  pending_image2_generation_tasks?: GeneratedAssetTask[];
  pending_doubao_generation_tasks?: GeneratedAssetTask[];
};

type InstrumentAudioItem = {
  instrument_id: string;
  label: string;
  audio_source_kind: "open_sample" | "soundfont_fallback" | "webaudio_synthesis" | string;
  playback_instrument: string;
  is_real_sample: boolean;
  exact_real_instrument_sample?: boolean;
  sample_fidelity?: "exact_open_sample" | "close_soundfont_sample" | "approximate_soundfont_sample" | "not_real_sample" | string;
  playable_status?: "ready_real_sample" | "ready_soundfont_proxy" | "pending_exact_sample" | string;
  classroom_note: string;
};

type InstrumentAudioPack = {
  audio_pack_id: string;
  label: string;
  sample_status: string;
  local_file_report?: {
    status: "ready" | "missing_files" | string;
    ready_count: number;
    missing_count: number;
  };
  items: InstrumentAudioItem[];
};

type TeacherControlPack = {
  control_pack_id: string;
  label: string;
  classroom_problem: string;
  controls: string[];
  music_education_use: string;
  teacher_actions?: string[];
  quality_gates?: string[];
  control_logic?: {
    reset_behavior: string;
    teacher_priority_over_auto_adaptive: boolean;
    auto_adjustment_requires_visible_reason: boolean;
    projector_safe: boolean;
    grade_band_policy: Record<string, string>;
  };
};

type MaterialBinder = {
  binder_id: string;
  label: string;
  primary_material_kind: string;
  input_entities: string[];
  output_entities: string[];
  applicable_activity_ids: string[];
  student_music_practices: string[];
  music_education_use: string;
  quality_gates: string[];
};

type MaterialEntitySpec = {
  entity_id: string;
  label: string;
  source_kinds: string[];
  structured_result_fields: string[];
  game_ready_schema: Record<string, string>;
  matched_binder_ids: string[];
  recommended_gameplay_template_ids: string[];
  quality_gates: string[];
  teacher_confirm_required: string[];
  do_not_invent_policy: string;
  music_education_use: string;
};

type AssessmentRecordTemplate = {
  record_template_id: string;
  label: string;
  records: string[];
  output_forms: string[];
  applicable_activity_ids: string[];
  student_music_practices: string[];
  music_education_use: string;
  quality_gates: string[];
};

type AdaptiveTemplate = {
  adaptive_template_id: string;
  label: string;
  trigger_condition: string;
  adjustment: string;
  teacher_visible_reason: string;
  undo_action: string;
  applicable_activity_ids: string[];
  student_music_practices: string[];
  music_education_guardrails: string[];
  quality_gates: string[];
};

type DeliveryTemplate = {
  delivery_template_id: string;
  label: string;
  form: string;
  purpose: string;
  priority: "P0" | "P1" | string;
  output_formats: string[];
  applicable_activity_ids: string[];
  classroom_use: string;
  quality_gates: string[];
};

type ScenarioTemplate = {
  scenario_template_id: string;
  label: string;
  classroom_scenario: string;
  composition: string;
  image_generation: "none" | "optional_image_gen" | "requires_image_gen" | string;
  recommended_activity_ids: string[];
  teacher_controls: string[];
  music_education_guardrails: string[];
  quality_gates: string[];
};

type AssetPackTemplate = {
  asset_pack_template_id: string;
  label: string;
  source_kind: string;
  included_assets: Array<{
    asset_id: string;
    file: string;
    music_element: string;
    student_action: string;
    accessibility_label: string;
  }>;
  usage: string[];
  generation_requirement: {
    status: string;
    provider: string;
    save_policy: string;
  };
  authenticity_policy: string;
  applicable_activity_ids: string[];
  supports_teaching_aids: string[];
  supports_virtual_instruments: string[];
  music_elements: string[];
  student_music_practices: string[];
  classroom_role: string;
  quality_gates: string[];
};

type MicroActivityTemplate = {
  micro_activity_template_id: string;
  label: string;
  duration_minutes: number;
  classroom_use: string;
  component_ids: string[];
  applicable_activity_ids: string[];
  music_elements: string[];
  student_music_practices: string[];
  teaching_stages: string[];
  teacher_controls: string[];
  acceptance: string[];
  quality_gates: string[];
};

type MusicEducationFoundation = {
  core_competencies: Array<{
    competency_id: string;
    label: string;
    classroom_meaning: string;
    candidate_activities: string[];
    avoid: string;
  }>;
  student_practices: Array<{
    practice_id: string;
    label: string;
    primary_classroom_meaning: string;
    candidate_activities: string[];
  }>;
  music_elements: Array<{
    element_id: string;
    label: string;
    primary_range: string;
    game_methods: string[];
    grade_hint: string;
  }>;
  grade_boundaries: Array<{
    grade_band: string;
    label: string;
    learning_traits: string;
    design_requirements: string;
    avoid: string;
  }>;
  teaching_stages: Array<{
    stage_id: string;
    label: string;
    music_purpose: string;
    candidate_activities: string[];
    avoid: string;
  }>;
};

type GameplayTemplateSpec = {
  template_id: string;
  label: string;
  primary_competency: string;
  secondary_competency?: string;
  music_elements: string[];
  student_practices: string[];
  teaching_stages: string[];
  supported_materials: string[];
  core_loop: string[];
  required_components: string[];
  required_rules: string[];
  required_teacher_controls: string[];
  optional_assets: string[];
  difficulty_controls: string[];
  implementation_status: "runtime_ready" | "activity_ready" | "spec_ready" | string;
  evidence: string[];
  applicable_activity_ids: string[];
};

type ComponentLibrarySpec = {
  component_id: string;
  name: string;
  role: string;
  runtime: string;
  purpose: string;
  student_actions: string[];
  music_elements: string[];
  required_material_entities: string[];
  teacher_controls: string[];
  required_elements: string[];
  behaviors: string[];
  interaction_modes?: string[];
  empty_state?: string;
  error_state?: string;
  called_by_template_ids?: string[];
  open_source_dependencies: string[];
  quality_gates: string[];
  education_notes: string[];
};

type MusicRuleSpec = {
  rule_id: string;
  name: string;
  rule_family: string;
  inputs: string[];
  outputs: string[];
  music_elements: string[];
  student_practices: string[];
  feedback_contract: Record<string, string>;
  pedagogy_guardrails: string[];
  applicable_activity_ids: string[];
};

type PrimaryActivityLibraryPayload = {
  toolkit_catalog: ToolkitCatalogItem[];
  music_education_foundation?: MusicEducationFoundation;
  gameplay_templates?: GameplayTemplateSpec[];
  component_library?: ComponentLibrarySpec[];
  teaching_aids: TeachingAidSummary[];
  virtual_instruments: VirtualInstrumentSummary[];
  asset_pack_templates?: AssetPackTemplate[];
  micro_activity_templates?: MicroActivityTemplate[];
  material_entities?: MaterialEntitySpec[];
  material_binders?: MaterialBinder[];
  assessment_record_templates?: AssessmentRecordTemplate[];
  adaptive_templates?: AdaptiveTemplate[];
  delivery_templates?: DeliveryTemplate[];
  scenario_templates?: ScenarioTemplate[];
  teacher_control_packs?: TeacherControlPack[];
  music_rules?: MusicRuleSpec[];
  instrument_audio_packs?: InstrumentAudioPack[];
  quality_report?: LibraryQualityReport;
};

const fallbackLibrary: PrimaryActivityLibraryPayload = {
  music_education_foundation: {
    core_competencies: [
      {
        competency_id: "aesthetic_perception",
        label: "审美感知",
        classroom_meaning: "听辨音乐情绪、速度、力度、音色、旋律特点，形成感受和判断。",
        candidate_activities: ["听赏选择", "音色侦探"],
        avoid: "只让学生抢答，不要求聆听依据。"
      },
      {
        competency_id: "artistic_performance",
        label: "艺术表现",
        classroom_meaning: "用歌唱、演奏、律动、身体动作表现音乐。",
        candidate_activities: ["分句跟唱", "节奏复刻"],
        avoid: "只点按钮得分，没有唱、奏、动。"
      }
    ],
    student_practices: [
      {
        practice_id: "listen",
        label: "听",
        primary_classroom_meaning: "听情绪、速度、力度、音色、主题、段落。",
        candidate_activities: ["听赏选择", "音色侦探"]
      },
      {
        practice_id: "sing",
        label: "唱",
        primary_classroom_meaning: "模唱、接唱、分句唱、唱名唱。",
        candidate_activities: ["分句跟唱", "缺词接唱"]
      }
    ],
    music_elements: [
      {
        element_id: "steady_beat",
        label: "稳定拍",
        primary_range: "感受均匀拍点",
        game_methods: ["跟拍", "行走", "敲击"],
        grade_hint: "低段优先"
      }
    ],
    grade_boundaries: [
      {
        grade_band: "lower_primary",
        label: "小学低段",
        learning_traits: "以感受、模仿、动作、图像为主。",
        design_requirements: "少文字、大按钮、多听多动、即时反馈。",
        avoid: "长说明、复杂规则、抽象术语。"
      }
    ],
    teaching_stages: [
      {
        stage_id: "lesson_opening",
        label: "导入",
        music_purpose: "激发兴趣、唤起经验、初步感受。",
        candidate_activities: ["听一遍投票", "情绪图卡"],
        avoid: "复杂闯关。"
      }
    ]
  },
  gameplay_templates: [
    {
      template_id: "rhythm_echo_core",
      label: "节奏复刻",
      primary_competency: "艺术表现",
      secondary_competency: "审美感知",
      music_elements: ["稳定拍", "节奏", "休止"],
      student_practices: ["listen", "tap", "move"],
      teaching_stages: ["律动/节奏", "复习巩固"],
      supported_materials: ["rhythm_pattern", "meter"],
      core_loop: ["listen", "remember", "tap", "feedback"],
      required_components: ["audio_player", "meter_track", "rhythm_pad"],
      required_rules: ["rhythm_timing_judgement"],
      required_teacher_controls: ["tempo_control_pack", "reset_pack"],
      optional_assets: ["reward_badge_pack"],
      difficulty_controls: ["bpm", "show_hint"],
      implementation_status: "runtime_ready",
      evidence: ["game_template_registry", "browser smoke"],
      applicable_activity_ids: ["rhythm_warmup"]
    },
    {
      template_id: "body_percussion_core",
      label: "身体打击工坊",
      primary_competency: "创意实践",
      music_elements: ["节奏", "节拍", "力度"],
      student_practices: ["move", "tap", "create"],
      teaching_stages: ["律动", "创编"],
      supported_materials: ["meter", "body_action_set"],
      core_loop: ["choose_action", "arrange", "perform", "revise"],
      required_components: ["body_action_cards", "meter_track"],
      required_rules: ["bar_length_rule"],
      required_teacher_controls: ["teacher_confirm_pack"],
      optional_assets: ["body_action_card_pack"],
      difficulty_controls: ["bar_count", "action_count"],
      implementation_status: "activity_ready",
      evidence: ["独立 React 学生活动页"],
      applicable_activity_ids: ["body_percussion_builder"]
    }
  ],
  component_library: [
    {
      component_id: "game_hud",
      name: "游戏状态 HUD",
      role: "game_shell",
      runtime: "react_radix_lucide",
      purpose: "显示本轮音乐任务的得分、星级、回合、剩余时间和当前音乐目标。",
      student_actions: ["observe", "revise"],
      music_elements: ["课堂进度", "音乐目标"],
      required_material_entities: [],
      teacher_controls: ["reset", "pause", "show_hint"],
      required_elements: ["分数", "回合", "音乐目标", "状态徽章"],
      behaviors: ["不遮挡音乐操作区", "只显示和当前音乐任务有关的信息", "投屏可读"],
      interaction_modes: ["desktop_mouse", "projector_large_text"],
      empty_state: "未开始时显示本轮音乐任务和开始状态，不显示空分数。",
      error_state: "缺少活动状态时提示教师重置或重新生成活动。",
      called_by_template_ids: ["rhythm_echo_core", "timbre_detective_core"],
      open_source_dependencies: ["react", "radix", "lucide-react"],
      quality_gates: ["not_standalone_game", "readable_on_projector", "reset_ready"],
      education_notes: ["HUD 只能辅助课堂节奏，不能把音乐学习简化成抢分。"]
    },
    {
      component_id: "answer_choice_grid",
      name: "音乐选择网格",
      role: "music_operation",
      runtime: "react_radix",
      purpose: "用于情绪、速度、力度、音色、唱名等听后选择。",
      student_actions: ["listen", "choose", "explain"],
      music_elements: ["情绪", "速度", "力度", "音色", "唱名"],
      required_material_entities: ["audio_clip"],
      teacher_controls: ["reset", "show_answer", "hide_hint"],
      required_elements: ["选项卡", "禁用态", "选择反馈", "依据提示"],
      behaviors: ["必须先听后选", "选项数量可调", "选择后要求音乐依据"],
      interaction_modes: ["desktop_mouse", "touch_screen", "projector_large_text"],
      empty_state: "没有选项时提示补充可听辨目标或证据词。",
      error_state: "音频未绑定时禁止选择并提示先绑定音频。",
      called_by_template_ids: ["listening_choice_core", "timbre_detective_core"],
      open_source_dependencies: ["react", "radix"],
      quality_gates: ["not_standalone_game", "listen_before_choice", "evidence_required"],
      education_notes: ["选择网格用于表达听觉判断，不能变成看图或猜词。"]
    },
    {
      component_id: "drag_sort_board",
      name: "拖拽排序板",
      role: "music_operation",
      runtime: "react_dnd_kit",
      purpose: "用于节奏顺序、曲式段落、乐器分类和创编素材排列。",
      student_actions: ["listen", "arrange", "classify", "create", "explain"],
      music_elements: ["节奏", "曲式", "音色", "创编"],
      required_material_entities: ["rhythm_pattern"],
      teacher_controls: ["reset", "show_answer", "undo"],
      required_elements: ["素材区", "排序区", "撤回", "检查"],
      behaviors: ["支持点击添加的无拖拽替代", "排序后可试听或复听", "总拍数或结构可检查"],
      interaction_modes: ["desktop_mouse", "touch_screen", "projector_large_text"],
      empty_state: "无素材时提示补充节奏、段落或乐器材料。",
      error_state: "素材与目标格不匹配时提示教师调整材料数量。",
      called_by_template_ids: ["form_treasure_core", "rhythm_question_core"],
      open_source_dependencies: ["react", "dnd-kit", "radix"],
      quality_gates: ["not_standalone_game", "student_operable", "undo_ready"],
      education_notes: ["拖拽只是操作方式，排序依据必须来自听觉、节奏时值或音乐结构。"]
    }
  ],
  toolkit_catalog: [
    {
      activity_id: "rhythm_warmup",
      activity_name: "节奏热身",
      grade_bands: ["lower_primary", "middle_primary", "upper_primary"],
      student_music_behaviors: ["listen", "tap", "move"],
      education_alignment: {
        primary_competency: "艺术表现",
        secondary_competency: "审美感知",
        student_practices: ["listen", "tap", "move"],
        music_elements: ["稳定拍", "节奏", "休止"],
        teaching_stages: ["导入", "节奏练习", "巩固"],
        grade_fit: {
          lower_primary: "以听、拍、动建立稳定拍，少文字，强图形提示。",
          middle_primary: "加入四分、八分、休止的节奏卡识别和模仿。",
          upper_primary: "可隐藏提示，要求学生说出节奏疏密和休止位置。"
        },
        pedagogy_notes: ["先听到稳定拍，再用身体和节奏垫表现。", "休止不是空白，要作为停住的音乐表现来反馈。"]
      },
      selected: {
        components: ["audio_player", "rhythm_card_bank", "meter_track", "tap_feedback", "teacher_control_bar"],
        teaching_aids: ["rhythm_cards"],
        virtual_instruments: ["rhythm_pad"],
        game_templates: []
      },
      why: "小学节奏热身优先让学生完成 listen、tap、move，组合实体节奏卡替代件和虚拟节奏垫。"
    },
    {
      activity_id: "solfege_sorting",
      activity_name: "唱名排序",
      grade_bands: ["middle_primary", "upper_primary"],
      student_music_behaviors: ["listen", "arrange", "sing"],
      education_alignment: {
        primary_competency: "艺术表现",
        secondary_competency: "审美感知",
        student_practices: ["listen", "arrange", "sing"],
        music_elements: ["音高", "唱名", "旋律"],
        teaching_stages: ["音高练习", "识谱前准备"],
        grade_fit: {
          middle_primary: "用 do/re/mi/sol/la 建立唱名和音高方向感。",
          upper_primary: "可加入简谱或旋律短句排序。"
        },
        pedagogy_notes: ["唱名排序要从听辨和模唱出发。", "音高活动要限制音级数量。"]
      },
      selected: {
        components: ["audio_player", "solfege_card_bank", "teacher_control_bar"],
        teaching_aids: ["solfege_cards", "pitch_ladder_board"],
        virtual_instruments: ["virtual_xylophone"],
        game_templates: ["pitch_ladder_core", "solfege_target_core"]
      },
      why: "用唱名卡和虚拟音条琴替代磁贴、音条琴等实体教具。"
    },
    {
      activity_id: "orff_percussion_ensemble",
      activity_name: "奥尔夫打击乐合奏",
      grade_bands: ["middle_primary", "upper_primary"],
      student_music_behaviors: ["play", "listen", "cooperate", "perform"],
      education_alignment: {
        primary_competency: "艺术表现",
        secondary_competency: "创意实践",
        student_practices: ["play", "listen", "cooperate", "perform"],
        music_elements: ["节奏", "合作", "力度"],
        teaching_stages: ["器乐", "合作", "展示"],
        grade_fit: {
          middle_primary: "用固定节奏声部进行轮奏和合奏。",
          upper_primary: "加入声部进入、独奏/合奏对比和小组评价。"
        },
        pedagogy_notes: ["合奏重点是倾听、进入和声部配合。", "教师必须能静音、独奏和降速。"]
      },
      selected: {
        components: ["group_task_board", "meter_track", "teacher_control_bar"],
        teaching_aids: ["group_mission_cards", "performance_rubric"],
        virtual_instruments: ["virtual_hand_drum", "woodblock_claves", "shaker", "triangle_bell", "tambourine"],
        game_templates: []
      },
      why: "把小组任务卡、评价表和常用课堂打击乐器数字化。"
    }
  ],
  teaching_aids: [
    {
      aid_id: "rhythm_cards",
      name: "节奏卡",
      replace_physical_aid: "实体节奏卡",
      material_entities: ["rhythm_pattern", "meter"],
      components: ["rhythm_card_bank", "audio_player"],
      student_actions: ["listen", "arrange", "tap"],
      teacher_controls: ["shuffle", "show_answer", "reset"],
      real_photo_required: false,
      doubao_required: false,
      image_gen_required: false,
      asset_pack_required: "",
      asset_policy: { source: "vector_or_runtime_component", note: "运行时组件生成，不需要独立图片。" },
      quality_gates: ["material_bound", "student_operable", "teacher_reset_ready"]
    },
    {
      aid_id: "instrument_cards",
      name: "可演奏乐器皮肤卡",
      replace_physical_aid: "实体乐器图片卡和课堂乐器",
      material_entities: ["timbre_set", "instrument_pool", "audio_clip"],
      components: ["instrument_card_grid", "compare_player"],
      student_actions: ["listen", "match", "play", "explain"],
      teacher_controls: ["replay", "show_family", "reset"],
      real_photo_required: false,
      doubao_required: false,
      image_gen_required: true,
      asset_pack_required: "generated_playable_instrument_pack",
      asset_policy: { source: "image_gen_generated_png", note: "乐器卡使用本地生图器 image2 模型生成皮肤，并绑定本地采样播放；缺图必须标为待生成。" },
      quality_gates: ["listen_before_choice", "generated_instrument_skin_visible", "real_sample_playback", "evidence_required"]
    },
    {
      aid_id: "mood_picture_cards",
      name: "听赏情绪图卡",
      replace_physical_aid: "实体情绪图卡",
      material_entities: ["audio_clip", "expression_trait"],
      components: ["picture_prompt_cards", "compare_player"],
      student_actions: ["listen", "choose", "explain"],
      teacher_controls: ["replay", "hide_words", "reset"],
      real_photo_required: false,
      doubao_required: false,
      image_gen_required: true,
      asset_pack_required: "music_mood_picture_pack",
      asset_policy: { source: "image_gen_generated_png", note: "情绪图卡使用生成 PNG，已按 manifest 入库并通过文件校验；字段名保留旧 manifest 兼容。" },
      quality_gates: ["listen_before_choice", "image_gen_png_file_verified", "evidence_required"]
    },
    { aid_id: "performance_rubric", name: "表现评价表", replace_physical_aid: "纸质评价表" }
  ],
  virtual_instruments: [
    {
      instrument_id: "rhythm_pad",
      name: "虚拟节奏垫",
      replace_physical_instrument: "拍手/小鼓",
      input_modes: ["touch", "mouse", "keyboard"],
      sound_source: "webaudio_synthetic_drum",
      pitch_set: [],
      constraints: { record_events: true },
      teacher_controls: ["change_tempo", "show_beat", "reset"],
      quality_gates: ["sound_plays", "events_recorded", "teacher_controls_apply"],
      runtime_contract: {
        audio_unlock_required: true,
        student_event_schema: ["instrument_id", "timestamp_ms", "tap_index", "timing_status"],
        quality_gates: ["sound_plays", "events_recorded", "reset_clears_events"]
      }
    },
    {
      instrument_id: "tambourine",
      name: "虚拟铃鼓",
      replace_physical_instrument: "铃鼓",
      input_modes: ["touch", "mouse", "keyboard"],
      sound_source: "sample_or_webaudio_tambourine",
      pitch_set: [],
      constraints: { record_events: true, supports_roll: true },
      teacher_controls: ["change_tempo", "toggle_roll", "reset"],
      quality_gates: ["sound_plays", "events_recorded", "roll_mode_applies"],
      runtime_contract: {
        audio_unlock_required: true,
        student_event_schema: ["instrument_id", "timestamp_ms", "hit_type", "roll_mode", "beat_index"],
        quality_gates: ["sound_plays", "events_recorded", "reset_clears_events"]
      }
    },
    {
      instrument_id: "virtual_xylophone",
      name: "虚拟音条琴",
      replace_physical_instrument: "音条琴",
      input_modes: ["touch", "mouse", "keyboard"],
      sound_source: "webaudio_or_soundfont",
      pitch_set: ["do", "re", "mi", "sol", "la"],
      constraints: { only_allow_target_pitches: true, record_events: true },
      teacher_controls: ["change_tempo", "hide_labels", "limit_pitch_count", "reset"],
      quality_gates: ["sound_plays", "events_recorded", "material_bound"],
      runtime_contract: {
        audio_unlock_required: true,
        student_event_schema: ["instrument_id", "timestamp_ms", "pitch", "solfege", "slot_index"],
        quality_gates: ["sound_plays", "events_recorded", "pitch_limited_to_material", "reset_clears_events"]
      }
    },
    {
      instrument_id: "woodblock_claves",
      name: "木鱼响板",
      replace_physical_instrument: "木鱼/响板",
      input_modes: ["touch", "mouse", "keyboard"],
      sound_source: "sample_woodblock",
      pitch_set: [],
      constraints: { record_events: true, instrument_choices: ["woodblock", "claves"] },
      teacher_controls: ["choose_sound", "change_tempo", "reset"],
      quality_gates: ["sound_plays", "events_recorded", "sound_choice_applies"],
      runtime_contract: {
        audio_unlock_required: true,
        student_event_schema: ["instrument_id", "timestamp_ms", "sound_variant", "beat_index"],
        quality_gates: ["sound_plays", "events_recorded", "reset_clears_events"]
      }
    }
  ],
  asset_pack_templates: [
    {
      asset_pack_template_id: "generated_playable_instrument_pack",
      label: "生成式可演奏乐器皮肤包",
      source_kind: "image2",
      included_assets: [
        {
          asset_id: "virtual_hand_drum",
          file: "images/virtual_hand_drum.png",
          music_element: "音色",
          student_action: "play",
          accessibility_label: "虚拟小鼓生成插图"
        }
      ],
      usage: ["virtual_instrument_skin", "playable_instrument_card"],
      generation_requirement: {
        status: "ready_from_manifest",
        provider: "image2",
        save_policy: "每个单件乐器皮肤由本地生图器 image2 模型逐个生成 PNG；新增乐器必须先生成独立 PNG 再进入 ready 列表。"
      },
      authenticity_policy: "生成图只作为库乐队式演奏界面皮肤，不声明为真实照片；真实感由采样音频合同保证。",
      applicable_activity_ids: ["instrument_timbre_match", "instrument_family_sorting"],
      supports_teaching_aids: ["instrument_evidence_cards"],
      supports_virtual_instruments: ["virtual_hand_drum", "woodblock_claves", "shaker", "triangle_bell", "tambourine"],
      music_elements: ["音色", "乐器"],
      student_music_practices: ["listen", "play", "match"],
      classroom_role: "替代小学课堂可演奏乐器皮肤和实体乐器操作界面。",
      quality_gates: ["generated_instrument_skin_visible", "real_sample_playback", "no_web_photo_fallback"]
    },
    {
      asset_pack_template_id: "music_mood_picture_pack",
      label: "音乐情绪图卡包",
      source_kind: "image_gen_generated",
      included_assets: [
        {
          asset_id: "cheerful",
          file: "images/cheerful.png",
          music_element: "情绪",
          student_action: "choose",
          accessibility_label: "欢快情绪图卡"
        }
      ],
      usage: ["mood_card", "listening_intro"],
      generation_requirement: {
        status: "ready_from_manifest",
        provider: "image_gen",
        save_policy: "生成 PNG 已保存到 manifest 指定路径；这是模板库资产建设记录，不改变智能体核心逻辑。"
      },
      authenticity_policy: "使用 image_gen 生成的非写实情绪图，但不能代替真实乐器照片。",
      applicable_activity_ids: ["picture_listening_intro", "listen_choose_explain"],
      supports_teaching_aids: ["mood_picture_cards"],
      supports_virtual_instruments: [],
      music_elements: ["情绪", "速度", "力度"],
      student_music_practices: ["listen", "choose", "explain"],
      classroom_role: "替代实体情绪图卡，用于听赏初听后的情绪选择和音乐依据表达。",
      quality_gates: ["生成 PNG 文件验收通过", "学生必须说出音乐依据"]
    },
    {
      asset_pack_template_id: "classroom_character_pack",
      label: "课堂角色包",
      source_kind: "image_gen_generated",
      included_assets: [
        {
          asset_id: "music_helper",
          file: "images/music_helper.png",
          music_element: "任务引导",
          student_action: "follow",
          accessibility_label: "音乐小助手生成角色"
        }
      ],
      usage: ["classroom_role", "feedback_character"],
      generation_requirement: {
        status: "ready_from_manifest",
        provider: "image2",
        save_policy: "通用课堂角色 PNG 已保存到 manifest 指定路径；后续新增角色再逐张生成。"
      },
      authenticity_policy: "角色图只用于任务引导和反馈，不替代真实乐器照片或音乐材料。",
      applicable_activity_ids: ["rhythm_warmup", "listen_choose_explain"],
      supports_teaching_aids: ["picture_prompt_cards"],
      supports_virtual_instruments: [],
      music_elements: ["任务引导", "反馈"],
      student_music_practices: ["listen", "respond", "explain"],
      classroom_role: "作为低段课堂任务引导和反馈角色。",
      quality_gates: ["生成 PNG 文件验收通过", "角色只用于任务引导和反馈"]
    }
  ],
  micro_activity_templates: [
    {
      micro_activity_template_id: "one_minute_beat_check",
      label: "一分钟稳拍检查",
      duration_minutes: 1,
      classroom_use: "上课开始或节奏活动前快速检查全班拍点是否稳定。",
      component_ids: ["meter_track", "tap_feedback"],
      applicable_activity_ids: ["rhythm_warmup"],
      music_elements: ["稳定拍", "节奏"],
      student_music_practices: ["listen", "tap", "move"],
      teaching_stages: ["导入", "节奏练习"],
      teacher_controls: ["tempo", "reset"],
      acceptance: ["能快速开始", "能快速重置"],
      quality_gates: ["学生先听稳定拍", "全班拍点记录可见"]
    },
    {
      micro_activity_template_id: "listen_once_vote",
      label: "听一遍投票",
      duration_minutes: 2,
      classroom_use: "欣赏初听后让学生选择听到的情绪、速度或力度，并显示全班投票结果。",
      component_ids: ["audio_player", "choice_cards"],
      applicable_activity_ids: ["picture_listening_intro"],
      music_elements: ["情绪", "速度", "力度"],
      student_music_practices: ["listen", "choose", "explain"],
      teaching_stages: ["导入", "初听/感受"],
      teacher_controls: ["playback", "result_review"],
      acceptance: ["全班投票结果可显示"],
      quality_gates: ["必须先完整听一遍", "选择后追问音乐依据"]
    }
  ],
  teacher_control_packs: [
    {
      control_pack_id: "tempo_control_pack",
      label: "速度控制包",
      classroom_problem: "教师需要根据学生表现现场调速。",
      controls: ["BPM", "慢速", "原速", "加速"],
      teacher_actions: ["set_bpm", "slow_down", "restore_tempo", "speed_up"],
      music_education_use: "用于节奏、学唱和器乐活动的分层练习。",
      quality_gates: ["tempo_applies", "student_state_preserved", "reset_restores_default"],
      control_logic: {
        reset_behavior: "一键回到本轮初始状态，保留原始音乐材料。",
        teacher_priority_over_auto_adaptive: true,
        auto_adjustment_requires_visible_reason: true,
        projector_safe: true,
        grade_band_policy: {
          lower_primary: "低段只显示必要控制。",
          middle_primary: "中段可增加难度和结果回看。",
          upper_primary: "高段可开放更多创编和导出控制。"
        }
      }
    },
    {
      control_pack_id: "hint_visibility_pack",
      label: "提示开关包",
      classroom_problem: "教师需要逐步隐藏歌词、唱名、节奏或图片。",
      controls: ["显示提示", "隐藏提示"],
      teacher_actions: ["show_hint", "hide_hint"],
      music_education_use: "支持从支架到独立表现的递进。",
      quality_gates: ["hint_toggle_applies", "answer_not_revealed_by_default", "teacher_can_restore_hint"],
      control_logic: {
        reset_behavior: "重置后恢复默认提示状态，保留音乐材料。",
        teacher_priority_over_auto_adaptive: true,
        auto_adjustment_requires_visible_reason: true,
        projector_safe: true,
        grade_band_policy: {
          lower_primary: "低段少隐藏，先给支架。",
          middle_primary: "中段逐步隐藏答案。",
          upper_primary: "高段可隐藏更多提示并要求说明依据。"
        }
      }
    }
  ],
  material_binders: [
    {
      binder_id: "lyrics_rhythm_binder",
      label: "歌词节奏绑定",
      primary_material_kind: "lyrics_rhythm",
      input_entities: ["lyrics_phrase", "meter", "rhythm_pattern"],
      output_entities: ["lyrics_rhythm_strip", "stress_marks", "read_tap_sequence"],
      applicable_activity_ids: ["lyrics_rhythm_reading"],
      student_music_practices: ["listen", "read", "tap", "sing"],
      music_education_use: "把歌词、拍号和节奏型绑定成先按拍读、再拍出歌词节奏、最后回到演唱的材料。",
      quality_gates: ["lyrics_phrase_present", "meter_bound", "rhythm_value_check"]
    },
    {
      binder_id: "timbre_pool_binder",
      label: "音色池绑定",
      primary_material_kind: "instrument_pool",
      input_entities: ["instrument_pool", "instrument_family_set", "timbre_set", "audio_clip"],
      output_entities: ["instrument_cards", "timbre_word_cards", "compare_player_items"],
      applicable_activity_ids: ["instrument_timbre_match", "instrument_family_sorting"],
      student_music_practices: ["listen", "classify", "match", "explain"],
      music_education_use: "把乐器池、家族、音色词和听辨音频绑定成先听声音、再看真实照片和说依据的材料。",
      quality_gates: ["instrument_pool_present", "real_photo_gate", "audio_or_fallback_ready"]
    }
  ],
  material_entities: [
    {
      entity_id: "lyrics_text",
      label: "歌词文本 / 歌词乐句",
      source_kinds: ["lesson_text", "uploaded_doc", "manual_input"],
      structured_result_fields: ["phrases", "line_count", "song_title"],
      game_ready_schema: { phrases: "list[str]", value: "list[str]" },
      matched_binder_ids: ["song_phrase_binder", "lyrics_rhythm_binder"],
      recommended_gameplay_template_ids: ["lyrics_rhythm_reading", "lyrics_rhythm_practice", "phrase_loop_singing"],
      quality_gates: ["do_not_invent", "lyrics_not_empty", "phrase_count_confirmable"],
      teacher_confirm_required: ["phrase_split"],
      do_not_invent_policy: "没有在教案、教师需求或上传材料中出现时，保持 missing，不自动编造。",
      music_education_use: "支撑按拍读歌词、歌词节奏、分句学唱和歌词提示隐藏。"
    },
    {
      entity_id: "audio_clip",
      label: "音频片段",
      source_kinds: ["uploaded_audio", "audio_url", "manual_input"],
      structured_result_fields: ["url", "filename", "start_seconds", "end_seconds", "source_kind"],
      game_ready_schema: { url: "string", start_seconds: "number|null", end_seconds: "number|null" },
      matched_binder_ids: ["song_phrase_binder", "listening_evidence_binder", "form_segment_binder", "timbre_pool_binder"],
      recommended_gameplay_template_ids: ["phrase_loop_singing", "listen_choose_explain", "theme_return_action", "instrument_timbre_match"],
      quality_gates: ["do_not_invent", "audio_source_present", "boundary_teacher_confirmable"],
      teacher_confirm_required: ["audio_clip_boundary"],
      do_not_invent_policy: "没有在教案、教师需求或上传材料中出现时，保持 missing，不自动编造。",
      music_education_use: "支撑先听后唱、复听找证据、主题再现和音色听辨，不能用无声游戏替代聆听。"
    },
    {
      entity_id: "rhythm_pattern",
      label: "节奏型",
      source_kinds: ["lesson_text", "score_hint", "manual_input"],
      structured_result_fields: ["tokens", "notation_text", "duration_policy"],
      game_ready_schema: { tokens: "list[str]", value: "list[str]" },
      matched_binder_ids: ["rhythm_pattern_binder", "lyrics_rhythm_binder"],
      recommended_gameplay_template_ids: ["rhythm_warmup", "lyrics_rhythm_reading", "rhythm_question_answer", "body_percussion_builder"],
      quality_gates: ["do_not_invent", "rhythm_tokens_present", "bar_length_teacher_confirmable"],
      teacher_confirm_required: ["rhythm_value_check"],
      do_not_invent_policy: "没有在教案、教师需求或上传材料中出现时，保持 missing，不自动编造。",
      music_education_use: "把四分、八分、休止等节奏材料转为节奏卡、拍击目标和小节长度检查。"
    }
  ],
  assessment_record_templates: [
    {
      record_template_id: "tap_accuracy_record",
      label: "完整节奏表现记录",
      records: ["grade_preset", "practice_mode", "tap_attempts", "correct_count", "missed_count", "extra_count", "rest_error_count", "round_result"],
      output_forms: ["complete_rhythm_result", "score", "summary_text", "json_export"],
      applicable_activity_ids: ["rhythm_warmup", "steady_beat_walk"],
      student_music_practices: ["listen", "tap", "move"],
      music_education_use: "记录完整内部音头的正确、早晚、漏拍、多拍和休止误拍，帮助教师做针对性重练。",
      quality_gates: ["records_timing_evidence", "internal_attacks_matched_once", "complete_rhythm_result_visible", "json_export_available"]
    },
    {
      record_template_id: "exit_ticket_record",
      label: "课堂出口票记录",
      records: ["music_focus", "evidence_terms", "student_reason", "next_lesson_suggestion"],
      output_forms: ["class_list", "teacher_review_summary", "json_export"],
      applicable_activity_ids: ["exit_ticket_review"],
      student_music_practices: ["choose", "explain", "assess"],
      music_education_use: "在课堂收尾记录学生能否说出本课音乐要素和一个具体依据，供教师下节课复盘。",
      quality_gates: ["music_focus_present", "evidence_required", "teacher_review_ready"]
    }
  ],
  adaptive_templates: [
    {
      adaptive_template_id: "slow_down_when_many_late",
      label: "多数学生晚拍则降速",
      trigger_condition: "连续 2 轮晚拍或偏慢反馈较多，且活动目标仍是稳定拍、节奏或律动。",
      adjustment: "BPM 降低 8 到 12，并保留当前节奏/拍号材料。",
      teacher_visible_reason: "多数学生落在拍点后面，建议先降速复听，再回到原速。",
      undo_action: "恢复上一轮 BPM。",
      applicable_activity_ids: ["rhythm_warmup", "steady_beat_walk"],
      student_music_practices: ["listen", "tap", "move"],
      music_education_guardrails: ["不能改变课堂目标", "调整原因必须让教师看见", "教师必须能一键撤回"],
      quality_gates: ["teacher_reason_visible", "bpm_change_bounded", "undo_restores_previous_bpm"]
    },
    {
      adaptive_template_id: "suggest_next_activity",
      label: "活动后推荐下一步",
      trigger_condition: "当前活动完成，且已有记录模板或教师确认结果。",
      adjustment: "推荐一个巩固、挑战、展示或收尾活动，不自动跳转。",
      teacher_visible_reason: "根据刚才的课堂结果，给教师一个下一步建议，由教师决定是否采用。",
      undo_action: "关闭建议卡，不改变当前活动。",
      applicable_activity_ids: ["*"],
      student_music_practices: ["listen", "tap", "sing", "move", "play", "create", "perform", "assess"],
      music_education_guardrails: ["不能改变课堂目标", "调整原因必须让教师看见", "教师必须能一键撤回"],
      quality_gates: ["teacher_decides_next_step", "current_activity_preserved", "recommendation_uses_record_evidence"]
    }
  ],
  delivery_templates: [
    {
      delivery_template_id: "projector_activity_view",
      label: "投屏活动视图",
      form: "大字、大按钮、少文字、教师控制明显",
      purpose: "全班一起看、听、做，适合电子白板或教室大屏。",
      priority: "P0",
      output_formats: ["HTML", "React view"],
      applicable_activity_ids: ["*"],
      classroom_use: "用于课堂主屏，保证学生能在远处看清音乐材料、当前任务和教师控制。",
      quality_gates: ["large_text_readable", "teacher_controls_visible", "no_horizontal_overflow"]
    },
    {
      delivery_template_id: "classroom_result_export",
      label: "课堂结果导出",
      form: "JSON/CSV/截图",
      purpose: "课后复盘学生表现、出口票、小组评价和创编记录。",
      priority: "P1",
      output_formats: ["JSON", "CSV", "PNG"],
      applicable_activity_ids: ["rhythm_warmup", "exit_ticket_review"],
      classroom_use: "用于课后整理学生音乐学习证据，服务复盘、下节课调整和教研分享。",
      quality_gates: ["record_schema_bound", "student_privacy_safe", "teacher_summary_available"]
    }
  ],
  scenario_templates: [
    {
      scenario_template_id: "substitute_teacher_mode",
      label: "代课模式",
      classroom_scenario: "临时代课、教师不熟悉教材或需要低风险流程。",
      composition: "低风险听辨/节奏热身 + 清晰投屏步骤 + 自动提示 + 教师一键重置。",
      image_generation: "optional_image_gen",
      recommended_activity_ids: ["rhythm_warmup", "lesson_opening_hook", "listen_choose_explain"],
      teacher_controls: ["playback", "tempo", "show_hint", "reset", "result_review"],
      music_education_guardrails: ["不能脱离音乐学习目标", "不能只做课堂管理或普通游戏"],
      quality_gates: ["low_risk_flow", "teacher_prompt_visible", "reset_available"]
    },
    {
      scenario_template_id: "festival_music_pack",
      label: "节日音乐活动",
      classroom_scenario: "六一、春节、校园活动或主题音乐周。",
      composition: "节奏、动作、合奏、展示和祝福语创编，围绕节日音乐素材完成。",
      image_generation: "requires_image_gen",
      recommended_activity_ids: ["lesson_opening_hook", "body_percussion_builder", "orff_percussion_ensemble"],
      teacher_controls: ["tempo", "group_rotation", "classroom_timer", "result_review", "reset"],
      music_education_guardrails: ["不能脱离音乐学习目标", "必须绑定节日音乐材料"],
      quality_gates: ["festival_music_material_bound", "performance_or_creation_ready", "visual_assets_marked_if_missing"]
    }
  ],
  music_rules: [
    {
      rule_id: "rhythm_timing_judgement",
      name: "拍点早晚判定",
      rule_family: "rhythm",
      inputs: ["tap_time_ms", "target_time_ms", "tolerance_ms"],
      outputs: ["early", "on_time", "late", "miss"],
      music_elements: ["稳定拍", "节奏"],
      student_practices: ["listen", "tap", "move"],
      feedback_contract: {
        status: "规则判定状态",
        music_reason: "说明学生表现背后的音乐原因",
        student_feedback: "给学生的短反馈",
        teacher_suggestion: "给教师的下一步调节建议",
        next_practice: "建议回到哪一步音乐实践",
        requires_teacher_confirm: "是否需要教师确认"
      },
      pedagogy_guardrails: ["低段重点反馈稳不稳、早还是晚"],
      applicable_activity_ids: ["rhythm_warmup"]
    }
  ],
  instrument_audio_packs: [
    {
      audio_pack_id: "primary_instrument_audio_pack",
      label: "小学乐器听辨音频包",
      sample_status: "fallback_ready_needs_open_samples",
      local_file_report: {
        status: "ready",
        ready_count: 1,
        missing_count: 0
      },
      items: [
        {
          instrument_id: "dizi",
          label: "笛子",
          audio_source_kind: "soundfont_fallback",
          playback_instrument: "flute",
          is_real_sample: false,
          exact_real_instrument_sample: false,
          sample_fidelity: "not_real_sample",
          playable_status: "pending_exact_sample",
          classroom_note: "这是课堂可听 fallback，能支持先听再分，但不能标记为真实采样。"
        }
      ]
    },
    {
      audio_pack_id: "primary_playable_instrument_sample_pack",
      label: "小学可演奏乐器采样演奏包",
      sample_status: "sampled_playback_ready_needs_exact_samples",
      local_file_report: {
        status: "ready",
        ready_count: 13,
        missing_count: 0
      },
      items: [
        {
          instrument_id: "flute_playable_board",
          label: "长笛演奏板",
          audio_source_kind: "open_sample",
          playback_instrument: "flute",
          is_real_sample: true,
          exact_real_instrument_sample: true,
          sample_fidelity: "exact_open_sample",
          playable_status: "ready_real_sample",
          classroom_note: "这是本地 SoundFont 长笛采样音色，可用于长笛演奏板。"
        },
        {
          instrument_id: "dizi_playable_board",
          label: "笛子演奏板",
          audio_source_kind: "open_sample",
          playback_instrument: "flute",
          is_real_sample: true,
          exact_real_instrument_sample: false,
          sample_fidelity: "approximate_soundfont_sample",
          playable_status: "ready_soundfont_proxy",
          classroom_note: "这是本地 SoundFont 长笛采样近似音色，用于笛子演奏板先行可奏；待补笛子实录。"
        },
        {
          instrument_id: "shaker",
          label: "虚拟沙锤",
          audio_source_kind: "open_sample",
          playback_instrument: "agogo",
          is_real_sample: true,
          exact_real_instrument_sample: false,
          sample_fidelity: "approximate_soundfont_sample",
          playable_status: "ready_soundfont_proxy",
          classroom_note: "这是本地 SoundFont 近似采样，待补沙锤实录。"
        }
      ]
    }
  ],
  quality_report: {
    status: "pass",
    pending_image2_generation_tasks: []
  }
};

export function PrimaryActivityLibraryApp() {
  const [library, setLibrary] = useState<PrimaryActivityLibraryPayload>(fallbackLibrary);
  const [selectedId, setSelectedId] = useState("rhythm_warmup");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    fetch("/api/primary-activity-library")
      .then((response) => (response.ok ? response.json() : Promise.reject(new Error(String(response.status)))))
      .then((payload: PrimaryActivityLibraryPayload) => {
        if (!active) return;
        setLibrary(payload);
        if (payload.toolkit_catalog[0]) setSelectedId(payload.toolkit_catalog[0].activity_id);
      })
      .catch(() => undefined)
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  const selected = useMemo(
    () => library.toolkit_catalog.find((item) => item.activity_id === selectedId) || library.toolkit_catalog[0],
    [library.toolkit_catalog, selectedId]
  );
  const generatedTasks = [
    ...(library.quality_report?.pending_doubao_generation_tasks ?? []),
    ...(library.quality_report?.pending_image2_generation_tasks ?? [])
  ];
  const pendingImageCount = generatedTasks.reduce((count, task) => count + task.outputs.length, 0);

  return (
    <main className="primary-activity-shell library-shell">
      <Container size="4" px="4">
        <section className="library-hero" aria-label="小学音乐课堂活动库">
          <Flex align="center" justify="between" gap="4" wrap="wrap">
            <div>
              <Flex align="center" gap="2" wrap="wrap">
                <Badge color="green" variant="soft"><School size={14} />小学专版</Badge>
                <Badge color={loading ? "gray" : "amber"} variant="soft">{loading ? "读取后端库" : "库已连接"}</Badge>
              </Flex>
              <Heading as="h1" size="8" className="activity-title">音乐课堂活动库</Heading>
              <Text as="p" size="3" color="gray" className="activity-subtitle">
                先对齐小学音乐教育目标，再组合教具、虚拟乐器和游戏模板。
              </Text>
            </div>
            <Button size="3" highContrast asChild>
              <a href="/template-console/primary-activity-preview.html">
                <Play size={18} />
                打开节奏热身
              </a>
            </Button>
          </Flex>
        </section>

        <Grid columns={{ initial: "1", md: ".9fr 1.1fr" }} gap="4">
          <section className="activity-board library-list" aria-label="活动模板">
            <Flex align="center" gap="2" className="tool-heading">
              <LibraryBig size={20} />
              <Text weight="bold">小学活动模板</Text>
            </Flex>
            <div className="library-card-list">
              {library.toolkit_catalog.map((item) => (
                <button
                  key={item.activity_id}
                  className={`library-activity-card ${item.activity_id === selected?.activity_id ? "active" : ""}`}
                  type="button"
                  onClick={() => setSelectedId(item.activity_id)}
                >
                  <strong>{item.activity_name}</strong>
                  <span>{item.grade_bands.map(gradeBandLabel).join(" / ")}</span>
                </button>
              ))}
            </div>
          </section>

          <section className="activity-board library-detail" aria-label="活动组合详情">
            {selected ? (
              <>
                <Flex align="center" justify="between" gap="3" wrap="wrap">
                  <div>
                    <Text as="p" size="1" color="gray">{selected.activity_id}</Text>
                    <Heading as="h2" size="6">{selected.activity_name}</Heading>
                  </div>
                  {selected.activity_id === "rhythm_warmup" ? (
                    <Button asChild highContrast>
                      <a href="/template-console/primary-activity-preview.html">
                        <Play size={17} />
                        运行
                      </a>
                    </Button>
                  ) : (
                    <Badge color="gray" variant="soft">待接活动页</Badge>
                  )}
                </Flex>
                <Text as="p" size="2" color="gray" className="library-why">{selected.why}</Text>
                <section className="education-panel" aria-label="音乐教育依据">
                  <Flex align="center" gap="2">
                    <GraduationCap size={18} />
                    <Text weight="bold">音乐教育依据</Text>
                  </Flex>
                  <Grid columns={{ initial: "1", sm: "2" }} gap="3" className="education-grid">
                    <EducationBucket title="核心素养" items={[competencyLabel(selected.education_alignment)]} />
                    <EducationBucket title="学生实践" items={selected.education_alignment.student_practices.map(practiceLabel)} />
                    <EducationBucket title="音乐要素" items={selected.education_alignment.music_elements} />
                    <EducationBucket title="教学环节" items={selected.education_alignment.teaching_stages} />
                  </Grid>
                  <div className="pedagogy-notes">
                    {selected.education_alignment.pedagogy_notes.map((note) => <p key={note}>{note}</p>)}
                  </div>
                </section>
                <Grid columns={{ initial: "1", sm: "2" }} gap="3">
                  <LibraryBucket icon={<Boxes size={18} />} title="组件" items={selected.selected.components} />
                  <LibraryBucket icon={<Wand2 size={18} />} title="教具" items={selected.selected.teaching_aids} />
                  <LibraryBucket icon={<Music2 size={18} />} title="虚拟乐器" items={selected.selected.virtual_instruments} />
                  <LibraryBucket icon={<Play size={18} />} title="游戏模板" items={selected.selected.game_templates} empty="无需游戏模板" />
                </Grid>
              </>
            ) : null}
          </section>
        </Grid>

        <Grid columns={{ initial: "1", md: "1fr 1fr" }} gap="4" className="library-inventory">
          <section className="primary-tool teaching-aid-panel" aria-label="虚拟教具库">
            <Flex align="center" justify="between" gap="3" wrap="wrap">
              <Flex align="center" gap="2">
                <Wand2 size={19} />
                <Text weight="bold">虚拟教具库</Text>
              </Flex>
              <Badge color="green" variant="soft">替代实体教具</Badge>
            </Flex>
            <Text as="p" size="2" color="gray" className="doubao-queue-note">
              教具库覆盖节奏卡、唱名卡、歌词条、情绪图卡、速度力度词卡、真实乐器卡、音色证据卡、曲式卡、主题卡、身体动作卡、小组任务卡、评价表和图形谱卡。
            </Text>
            <div className="audio-pack-grid">
              {library.teaching_aids.slice(0, 18).map((aid) => (
                <article className="audio-pack-card" key={aid.aid_id}>
                  <Flex align="center" justify="between" gap="2" wrap="wrap">
                    <Text as="p" size="1" color="gray">{aid.aid_id}</Text>
                    <Badge color={teachingAidAssetColor(aid)} variant="soft">
                      {teachingAidAssetLabel(aid)}
                    </Badge>
                  </Flex>
                  <Text weight="bold">{aid.name}</Text>
                  <Text as="p" size="1" color="gray">替代：{aid.replace_physical_aid}</Text>
                  <div className="audio-source-list">
                    <span>材料：{(aid.material_entities ?? []).slice(0, 4).join(" / ") || "按活动绑定"}</span>
                    <span>组件：{(aid.components ?? []).slice(0, 4).join(" / ") || "runtime component"}</span>
                    <span>学生：{(aid.student_actions ?? []).slice(0, 4).map(practiceLabel).join(" / ") || "课堂操作"}</span>
                    <span>素材包：{aid.asset_pack_required || "不需要独立素材包"}</span>
                    <span>验收：{(aid.quality_gates ?? []).slice(0, 4).join(" / ") || "material_bound / student_operable"}</span>
                  </div>
                </article>
              ))}
            </div>
          </section>
          <section className="primary-tool virtual-instrument-panel" aria-label="虚拟乐器库">
            <Flex align="center" justify="between" gap="3" wrap="wrap">
              <Flex align="center" gap="2">
                <Music2 size={19} />
                <Text weight="bold">虚拟乐器库</Text>
              </Flex>
              <Badge color="purple" variant="soft">音频解锁 / 事件记录 / 教师控制</Badge>
            </Flex>
            <Text as="p" size="2" color="gray" className="doubao-queue-note">
              虚拟乐器覆盖节奏垫、小鼓、木鱼/响板、沙锤、三角铁/碰铃、铃鼓、音条琴、五声宫格、简版键盘、竖笛指法、口风琴键盘和课堂打击乐套组。
            </Text>
            <div className="audio-pack-grid">
              {library.virtual_instruments.slice(0, 16).map((instrument) => (
                <article className="audio-pack-card" key={instrument.instrument_id}>
                  <Flex align="center" justify="between" gap="2" wrap="wrap">
                    <Text as="p" size="1" color="gray">{instrument.instrument_id}</Text>
                    <Badge color="purple" variant="soft">{instrument.sound_source ?? "webaudio"}</Badge>
                  </Flex>
                  <Text weight="bold">{instrument.name}</Text>
                  <Text as="p" size="1" color="gray">替代：{instrument.replace_physical_instrument}</Text>
                  <div className="audio-source-list">
                    <span>输入：{(instrument.input_modes ?? []).join(" / ") || "mouse / keyboard"}</span>
                    <span>音域：{(instrument.pitch_set ?? []).join(" / ") || "无固定音高"}</span>
                    <span>教师：{(instrument.teacher_controls ?? []).slice(0, 4).join(" / ") || "reset"}</span>
                    <span>解锁：{instrument.runtime_contract?.audio_unlock_required ? "first_user_click_required" : "not_required"}</span>
                    <span>事件：{(instrument.runtime_contract?.student_event_schema ?? []).slice(0, 5).join(" / ")}</span>
                    <span>
                      验收：{[
                        ...(instrument.quality_gates ?? []),
                        ...(instrument.runtime_contract?.quality_gates ?? [])
                      ].slice(0, 6).join(" / ")}
                    </span>
                  </div>
                </article>
              ))}
            </div>
          </section>
        </Grid>

        <section className="primary-tool foundation-panel" aria-label="音乐教育基础库">
          <Flex align="center" justify="between" gap="3" wrap="wrap">
            <Flex align="center" gap="2">
              <GraduationCap size={19} />
              <Text weight="bold">音乐教育基础库</Text>
            </Flex>
            <Badge color="green" variant="soft">先判定教学目标，再组合游戏</Badge>
          </Flex>
          <Text as="p" size="2" color="gray" className="doubao-queue-note">
            这里把核心素养、学生音乐实践、音乐要素、小学学段边界和教学环节做成智能体可检索的依据库，避免把普通游戏换皮成音乐主题。
          </Text>
          <div className="audio-pack-grid">
            {(library.music_education_foundation?.core_competencies ?? []).map((item) => (
              <article className="audio-pack-card" key={item.competency_id}>
                <Text as="p" size="1" color="gray">{item.competency_id}</Text>
                <Text weight="bold">{item.label}</Text>
                <Text as="p" size="1" color="gray">{item.classroom_meaning}</Text>
                <div className="audio-source-list">
                  <span>可生成：{item.candidate_activities.join(" / ")}</span>
                  <span>避免：{item.avoid}</span>
                </div>
              </article>
            ))}
          </div>
          <div className="foundation-strip" aria-label="音乐实践和教学边界">
            <span>学生音乐实践：{(library.music_education_foundation?.student_practices ?? []).slice(0, 8).map((item) => item.label).join(" / ")}</span>
            <span>音乐要素：{(library.music_education_foundation?.music_elements ?? []).slice(0, 8).map((item) => item.label).join(" / ")}</span>
            <span>小学学段：{(library.music_education_foundation?.grade_boundaries ?? []).map((item) => item.label).join(" / ")}</span>
            <span>教学环节：{(library.music_education_foundation?.teaching_stages ?? []).slice(0, 6).map((item) => item.label).join(" / ")}</span>
          </div>
        </section>

        <section className="primary-tool gameplay-template-panel" aria-label="玩法模板目录">
          <Flex align="center" justify="between" gap="3" wrap="wrap">
            <Flex align="center" gap="2">
              <Play size={19} />
              <Text weight="bold">玩法模板目录</Text>
            </Flex>
            <Badge color="amber" variant="soft">区分成熟运行、活动页就绪、仅 spec 就绪</Badge>
          </Flex>
          <Text as="p" size="2" color="gray" className="doubao-queue-note">
            玩法模板回答“这个音乐教学目标适合玩什么”。成熟模板可以直接进入学生端运行时，活动页就绪模板可直接上课，spec 就绪模板只作为后续开发骨架。
          </Text>
          <div className="audio-pack-grid">
            {(library.gameplay_templates ?? []).map((template) => (
              <article className="audio-pack-card" key={template.template_id}>
                <Flex align="center" justify="between" gap="2" wrap="wrap">
                  <Text as="p" size="1" color="gray">{template.template_id}</Text>
                  <Badge color={gameplayStatusColor(template.implementation_status)} variant="soft">
                    {gameplayStatusLabel(template.implementation_status)}
                  </Badge>
                </Flex>
                <Text weight="bold">{template.label}</Text>
                <Text as="p" size="1" color="gray">
                  {template.primary_competency} · {template.teaching_stages.join(" / ")}
                </Text>
                <div className="audio-source-list">
                  <span>核心循环：{template.core_loop.join(" -> ")}</span>
                  <span>音乐要素：{template.music_elements.join(" / ")}</span>
                  <span>学生实践：{template.student_practices.map(practiceLabel).join(" / ")}</span>
                  <span>规则：{template.required_rules.slice(0, 3).join(" / ")}</span>
                  <span>证据：{template.evidence.slice(0, 3).join(" / ")}</span>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="primary-tool component-library-panel" aria-label="交互组件库">
          <Flex align="center" justify="between" gap="3" wrap="wrap">
            <Flex align="center" gap="2">
              <Boxes size={19} />
              <Text weight="bold">交互组件库</Text>
            </Flex>
            <Badge color="blue" variant="soft">React / Radix / dnd-kit / WebAudio</Badge>
          </Flex>
          <Text as="p" size="2" color="gray" className="doubao-queue-note">
            组件库把游戏 HUD、回合提示、奖励反馈、进度路径、选择网格、拖拽排序、教师确认和班级计分，与音乐播放器、节奏卡、歌词条、节拍轨、乐器卡等音乐组件组合起来。
          </Text>
          <div className="audio-pack-grid">
            {(library.component_library ?? []).slice(0, 16).map((component) => (
              <article className="audio-pack-card" key={component.component_id}>
                <Flex align="center" justify="between" gap="2" wrap="wrap">
                  <Text as="p" size="1" color="gray">{component.component_id}</Text>
                  <Badge color="blue" variant="soft">{component.role}</Badge>
                </Flex>
                <Text weight="bold">{component.name}</Text>
                <Text as="p" size="1" color="gray">{component.purpose}</Text>
                <div className="audio-source-list">
                  <span>运行：{component.runtime}</span>
                  <span>交互：{(component.interaction_modes ?? ["desktop_mouse"]).slice(0, 3).join(" / ")}</span>
                  <span>学生：{component.student_actions.map(practiceLabel).join(" / ")}</span>
                  <span>音乐要素：{component.music_elements.join(" / ")}</span>
                  <span>开源：{component.open_source_dependencies.slice(0, 4).join(" / ")}</span>
                  <span>空状态：{component.empty_state ?? "已定义默认空状态"}</span>
                  <span>验收：{component.quality_gates.slice(0, 4).join(" / ")}</span>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="primary-tool music-rule-panel" aria-label="音乐规则与判定库">
          <Flex align="center" justify="between" gap="3" wrap="wrap">
            <Flex align="center" gap="2">
              <GraduationCap size={19} />
              <Text weight="bold">音乐规则与判定库</Text>
            </Flex>
            <Badge color="purple" variant="soft">形成性反馈，不只 correct/wrong</Badge>
          </Flex>
          <Text as="p" size="2" color="gray" className="doubao-queue-note">
            规则库按音乐规律判断早晚拍、休止、强弱拍、唱名、音高走向、音色证据、曲式、创编小节和合奏进入，并输出音乐原因、学生反馈和教师建议。
          </Text>
          <div className="audio-pack-grid">
            {(library.music_rules ?? []).slice(0, 12).map((rule) => (
              <article className="audio-pack-card" key={rule.rule_id}>
                <Flex align="center" justify="between" gap="2" wrap="wrap">
                  <Text as="p" size="1" color="gray">{rule.rule_id}</Text>
                  <Badge color="purple" variant="soft">{rule.rule_family}</Badge>
                </Flex>
                <Text weight="bold">{rule.name}</Text>
                <div className="audio-source-list">
                  <span>输入：{rule.inputs.slice(0, 4).join(" / ")}</span>
                  <span>输出：{rule.outputs.slice(0, 5).join(" / ")}</span>
                  <span>音乐要素：{rule.music_elements.join(" / ")}</span>
                  <span>学生实践：{rule.student_practices.map(practiceLabel).join(" / ")}</span>
                  <span>反馈：music_reason / student_feedback / teacher_suggestion / next_practice</span>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="primary-tool asset-pack-template-panel" aria-label="素材包模板">
          <Flex align="center" justify="between" gap="3" wrap="wrap">
            <Flex align="center" gap="2">
              <Image size={19} />
              <Text weight="bold">素材包模板</Text>
            </Flex>
            <Badge color="green" variant="soft">生成乐器皮肤 / 真实采样 / runtime 场景可区分</Badge>
          </Flex>
          <Text as="p" size="2" color="gray" className="doubao-queue-note">
            这里展示模板库已经登记的生成式可演奏乐器皮肤、采样音频、情绪图卡、身体动作卡、奖励徽章、曲式图形和课堂背景合同；本轮建库用本地 codex2api/image2 逐个生成固定资产并通过 PNG 入库校验，不能回退到旧照片包；场景图仍按具体教案和情景临时生成。
          </Text>
          <div className="audio-pack-grid">
            {(library.asset_pack_templates ?? []).map((template) => (
              <article className="audio-pack-card" key={template.asset_pack_template_id}>
                <Flex align="center" justify="between" gap="2" wrap="wrap">
                  <Text as="p" size="1" color="gray">{template.asset_pack_template_id}</Text>
                  <Badge color={assetTemplateStatusColor(template.generation_requirement.status)} variant="soft">
                    {assetTemplateStatusLabel(template.generation_requirement.status)}
                  </Badge>
                </Flex>
                <Text weight="bold">{template.label}</Text>
                <Text as="p" size="1" color="gray">{template.classroom_role}</Text>
                <div className="audio-source-list">
                  <span>来源：{assetSourceLabel(template.source_kind)} · {template.generation_requirement.provider}</span>
                  <span>真实性：{template.authenticity_policy}</span>
                  <span>音乐要素：{template.music_elements.join(" / ")}</span>
                  <span>学生实践：{template.student_music_practices.map(practiceLabel).join(" / ")}</span>
                  <span>素材：{template.included_assets.slice(0, 5).map((asset) => asset.accessibility_label).join(" / ")}</span>
                  <span>保存：{template.generation_requirement.save_policy}</span>
                  <span>验收：{template.quality_gates.slice(0, 4).join(" / ")}</span>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="primary-tool micro-activity-panel" aria-label="微活动模板">
          <Flex align="center" justify="between" gap="3" wrap="wrap">
            <Flex align="center" gap="2">
              <Play size={19} />
              <Text weight="bold">微活动模板</Text>
            </Flex>
            <Badge color="teal" variant="soft">1 到 8 分钟快速插入课堂</Badge>
          </Flex>
          <Text as="p" size="2" color="gray" className="doubao-queue-note">
            微活动用于导入、初听、节奏小练习、复听追问、分组回声和出口表达；智能体可以只生成一个短环节，而不是每次都生成完整大游戏。
          </Text>
          <div className="audio-pack-grid">
            {(library.micro_activity_templates ?? []).map((template) => (
              <article className="audio-pack-card" key={template.micro_activity_template_id}>
                <Flex align="center" justify="between" gap="2" wrap="wrap">
                  <Text as="p" size="1" color="gray">{template.micro_activity_template_id}</Text>
                  <Badge color="teal" variant="soft">{template.duration_minutes} 分钟</Badge>
                </Flex>
                <Text weight="bold">{template.label}</Text>
                <Text as="p" size="1" color="gray">{template.classroom_use}</Text>
                <div className="audio-source-list">
                  <span>组件：{template.component_ids.slice(0, 4).join(" / ")}</span>
                  <span>音乐要素：{template.music_elements.join(" / ")}</span>
                  <span>学生实践：{template.student_music_practices.map(practiceLabel).join(" / ")}</span>
                  <span>验收：{template.acceptance.slice(0, 3).join(" / ")}</span>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="primary-tool material-binder-panel" aria-label="材料绑定模板">
          <Flex align="center" justify="between" gap="3" wrap="wrap">
            <Flex align="center" gap="2">
              <Boxes size={19} />
              <Text weight="bold">材料实体解析库</Text>
            </Flex>
            <Badge color="teal" variant="soft">教案先解析，缺项不编造</Badge>
          </Flex>
          <Text as="p" size="2" color="gray" className="doubao-queue-note">
            解析库把教案里的教学目标、歌词、音频、节奏型、拍号、旋律、唱名、音色、曲式、小组任务和评价标准转成游戏可用 JSON；没有出现的材料保持 missing，交给教师补充确认。
          </Text>
          <div className="audio-pack-grid">
            {(library.material_entities ?? []).map((entity) => (
              <article className="audio-pack-card" key={entity.entity_id}>
                <Flex align="center" justify="between" gap="2" wrap="wrap">
                  <Text as="p" size="1" color="gray">{entity.entity_id}</Text>
                  <Badge color="teal" variant="soft">{entity.source_kinds.slice(0, 2).join(" / ")}</Badge>
                </Flex>
                <Text weight="bold">{entity.label}</Text>
                <Text as="p" size="1" color="gray">{entity.music_education_use}</Text>
                <div className="audio-source-list">
                  <span>结构：{entity.structured_result_fields.slice(0, 4).join(" / ")}</span>
                  <span>绑定：{entity.matched_binder_ids.slice(0, 3).join(" / ")}</span>
                  <span>可生成：{entity.recommended_gameplay_template_ids.slice(0, 4).join(" / ")}</span>
                  <span>确认：{entity.teacher_confirm_required.slice(0, 3).join(" / ")}</span>
                  <span>策略：do_not_invent / missing_values_must_stay_missing</span>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="primary-tool material-binder-panel" aria-label="材料绑定模板">
          <Flex align="center" justify="between" gap="3" wrap="wrap">
            <Flex align="center" gap="2">
              <Boxes size={19} />
              <Text weight="bold">材料绑定模板</Text>
            </Flex>
            <Badge color="green" variant="soft">教案材料到游戏组件</Badge>
          </Flex>
          <Text as="p" size="2" color="gray" className="doubao-queue-note">
            智能体收到教案后，先识别歌曲乐句、歌词节奏、唱名、音色、曲式和小组任务，再按这些模板绑定到可运行活动。
          </Text>
          <div className="audio-pack-grid">
            {(library.material_binders ?? []).map((binder) => (
              <article className="audio-pack-card" key={binder.binder_id}>
                <Text as="p" size="1" color="gray">{binder.binder_id}</Text>
                <Text weight="bold">{binder.label}</Text>
                <Badge color="teal" variant="soft">{binder.primary_material_kind}</Badge>
                <Text as="p" size="1" color="gray">{binder.music_education_use}</Text>
                <div className="audio-source-list">
                  <span>输入：{binder.input_entities.slice(0, 4).join(" / ")}</span>
                  <span>输出：{binder.output_entities.slice(0, 4).join(" / ")}</span>
                  <span>学生实践：{binder.student_music_practices.map(practiceLabel).join(" / ")}</span>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="primary-tool assessment-record-panel" aria-label="评价与记录模板">
          <Flex align="center" justify="between" gap="3" wrap="wrap">
            <Flex align="center" gap="2">
              <GraduationCap size={19} />
              <Text weight="bold">评价与记录模板</Text>
            </Flex>
            <Badge color="purple" variant="soft">课堂结果可导出</Badge>
          </Flex>
          <Text as="p" size="2" color="gray" className="doubao-queue-note">
            每个活动结束后要留下音乐学习证据：拍点、跟唱、欣赏依据、小组表现、创编回放或出口票，而不是只有得分。
          </Text>
          <div className="audio-pack-grid">
            {(library.assessment_record_templates ?? []).map((template) => (
              <article className="audio-pack-card" key={template.record_template_id}>
                <Text as="p" size="1" color="gray">{template.record_template_id}</Text>
                <Text weight="bold">{template.label}</Text>
                <Text as="p" size="1" color="gray">{template.music_education_use}</Text>
                <div className="audio-source-list">
                  <span>记录：{template.records.slice(0, 4).join(" / ")}</span>
                  <span>输出：{template.output_forms.join(" / ")}</span>
                  <span>学生实践：{template.student_music_practices.map(practiceLabel).join(" / ")}</span>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="primary-tool adaptive-template-panel" aria-label="自适应模板">
          <Flex align="center" justify="between" gap="3" wrap="wrap">
            <Flex align="center" gap="2">
              <Wand2 size={19} />
              <Text weight="bold">自适应模板</Text>
            </Flex>
            <Badge color="amber" variant="soft">教师可见，可撤回</Badge>
          </Flex>
          <Text as="p" size="2" color="gray" className="doubao-queue-note">
            系统只给教师看得见的调整建议：降速、隐藏提示、减少选项、重复乐句、增加挑战、切教师确认或推荐下一步，不偷偷改变课堂目标。
          </Text>
          <div className="audio-pack-grid">
            {(library.adaptive_templates ?? []).map((template) => (
              <article className="audio-pack-card" key={template.adaptive_template_id}>
                <Text as="p" size="1" color="gray">{template.adaptive_template_id}</Text>
                <Text weight="bold">{template.label}</Text>
                <Text as="p" size="1" color="gray">{template.teacher_visible_reason}</Text>
                <div className="audio-source-list">
                  <span>触发：{template.trigger_condition}</span>
                  <span>调整：{template.adjustment}</span>
                  <span>撤回：{template.undo_action}</span>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="primary-tool delivery-template-panel" aria-label="投屏与导出模板">
          <Flex align="center" justify="between" gap="3" wrap="wrap">
            <Flex align="center" gap="2">
              <ExternalLink size={19} />
              <Text weight="bold">投屏与导出模板</Text>
            </Flex>
            <Badge color="green" variant="soft">课堂交付产物</Badge>
          </Flex>
          <Text as="p" size="2" color="gray" className="doubao-queue-note">
            活动库要能直接服务上课：投屏、学生触摸、教师备课、打印卡片、活动包导出和课堂结果导出都作为可调用模板。
          </Text>
          <div className="audio-pack-grid">
            {(library.delivery_templates ?? []).map((template) => (
              <article className="audio-pack-card" key={template.delivery_template_id}>
                <Flex align="center" justify="between" gap="2" wrap="wrap">
                  <Text as="p" size="1" color="gray">{template.delivery_template_id}</Text>
                  <Badge color={template.priority === "P0" ? "green" : "gray"} variant="soft">{template.priority}</Badge>
                </Flex>
                <Text weight="bold">{template.label}</Text>
                <Text as="p" size="1" color="gray">{template.classroom_use}</Text>
                <div className="audio-source-list">
                  <span>形式：{template.form}</span>
                  <span>输出：{template.output_formats.join(" / ")}</span>
                  <span>用途：{template.purpose}</span>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="primary-tool scenario-template-panel" aria-label="特殊课堂场景模板">
          <Flex align="center" justify="between" gap="3" wrap="wrap">
            <Flex align="center" gap="2">
              <School size={19} />
              <Text weight="bold">特殊课堂场景模板</Text>
            </Flex>
            <Badge color="orange" variant="soft">真实课堂模式</Badge>
          </Flex>
          <Text as="p" size="2" color="gray" className="doubao-queue-note">
            面向代课、无乐器、大班、低噪音、展示课、复习课和节日活动，把活动库组合成能直接上课的场景包。
          </Text>
          <div className="audio-pack-grid">
            {(library.scenario_templates ?? []).map((template) => (
              <article className="audio-pack-card" key={template.scenario_template_id}>
                <Flex align="center" justify="between" gap="2" wrap="wrap">
                  <Text as="p" size="1" color="gray">{template.scenario_template_id}</Text>
                  <Badge color={scenarioImageColor(template.image_generation)} variant="soft">
                    {scenarioImageLabel(template.image_generation)}
                  </Badge>
                </Flex>
                <Text weight="bold">{template.label}</Text>
                <Text as="p" size="1" color="gray">{template.classroom_scenario}</Text>
                <div className="audio-source-list">
                  <span>组合：{template.composition}</span>
                  <span>推荐活动：{template.recommended_activity_ids.slice(0, 4).join(" / ")}</span>
                  <span>教师控制：{template.teacher_controls.slice(0, 5).join(" / ")}</span>
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="primary-tool teacher-control-pack-panel" aria-label="教师控制包">
          <Flex align="center" justify="between" gap="3" wrap="wrap">
            <Flex align="center" gap="2">
              <Wand2 size={19} />
              <Text weight="bold">教师控制包</Text>
            </Flex>
            <Badge color="teal" variant="soft">教师优先于自动自适应</Badge>
          </Flex>
          <Text as="p" size="2" color="gray" className="doubao-queue-note">
            教师控制包统一处理调速、播放、提示、难度、乐句循环、小组轮换、教师确认、计时、静音独奏、结果回看和重置；自动调整必须显示原因，投屏时不能遮挡主要音乐操作。
          </Text>
          <div className="audio-pack-grid">
            {(library.teacher_control_packs ?? []).slice(0, 12).map((pack) => (
              <article className="audio-pack-card" key={pack.control_pack_id}>
                <Text as="p" size="1" color="gray">{pack.control_pack_id}</Text>
                <Text weight="bold">{pack.label}</Text>
                <Text as="p" size="1" color="gray">{pack.classroom_problem}</Text>
                <div className="audio-source-list">
                  {pack.controls.slice(0, 5).map((control) => <span key={control}>{control}</span>)}
                  <span>动作：{(pack.teacher_actions ?? []).slice(0, 4).join(" / ") || "teacher_action"}</span>
                  <span>重置：{pack.control_logic?.reset_behavior ?? "reset_behavior"}</span>
                  <span>优先级：{pack.control_logic?.teacher_priority_over_auto_adaptive ? "teacher_priority_over_auto_adaptive" : "teacher_control"}</span>
                  <span>自动调整：{pack.control_logic?.auto_adjustment_requires_visible_reason ? "visible_reason_required" : "manual_only"}</span>
                  <span>投屏：{pack.control_logic?.projector_safe ? "projector_safe" : "projector_check_required"}</span>
                  <span>验收：{(pack.quality_gates ?? []).slice(0, 3).join(" / ")}</span>
                </div>
                <Text as="p" size="1" color="gray">{pack.music_education_use}</Text>
              </article>
            ))}
          </div>
        </section>

        <section className="primary-tool audio-pack-panel" aria-label="乐器听辨音频包">
          <Flex align="center" justify="between" gap="3" wrap="wrap">
            <Flex align="center" gap="2">
              <Music2 size={19} />
              <Text weight="bold">乐器听辨音频包</Text>
            </Flex>
            <Badge color="amber" variant="soft">采样优先演奏，近似音色必须标注</Badge>
          </Flex>
          <div className="audio-pack-grid">
            {(library.instrument_audio_packs ?? []).map((pack) => (
              <article className="audio-pack-card" key={pack.audio_pack_id}>
                <Text as="p" size="1" color="gray">{pack.audio_pack_id}</Text>
                <Text weight="bold">{pack.label}</Text>
                <Badge color={audioPackStatusColor(pack.sample_status)} variant="soft">{pack.sample_status}</Badge>
                <Text as="p" size="1" color="gray">
                  {audioFileReportLabel(pack.local_file_report)}
                </Text>
                <div className="audio-source-list">
                  {pack.items.slice(0, 6).map((item) => (
                    <span key={item.instrument_id}>
                      {item.label} · {audioSourceLabel(item.audio_source_kind)} · {sampleFidelityLabel(item)}
                    </span>
                  ))}
                </div>
              </article>
            ))}
          </div>
        </section>

        <section className="primary-tool doubao-queue-panel" aria-label="外部生图兼容队列">
          <Flex align="center" justify="between" gap="3" wrap="wrap">
            <Flex align="center" gap="2">
              <Image size={19} />
              <Text weight="bold">外部生图兼容队列</Text>
              <Badge color={pendingImageCount ? "amber" : "green"} variant="soft">
                {pendingImageCount ? `${pendingImageCount} 张历史任务` : "无历史任务"}
              </Badge>
            </Flex>
            <Button asChild size="2" variant="soft" disabled={!generatedTasks.length}>
              <a href="#external-image-generation-queue" aria-disabled={!generatedTasks.length}>
                <ExternalLink size={15} />
                查看任务
              </a>
            </Button>
          </Flex>
          <Text as="p" size="2" color="gray" className="doubao-queue-note">
            这里兼容读取历史外部生图任务；本轮模板库固定图片资产用本地 image2 生成并入库，项目生成组件直接运行，场景图按教案和情景临时生成。
          </Text>
          {generatedTasks.length ? (
            <div className="doubao-task-grid" id="external-image-generation-queue">
              {generatedTasks.map((task) => (
                <article className="doubao-task-card" key={task.asset_pack_id}>
                  <Flex align="center" justify="between" gap="2" wrap="wrap">
                    <div>
                      <Text as="p" size="1" color="gray">{task.asset_pack_id}</Text>
                      <Text weight="bold">{task.label}</Text>
                    </div>
                    <Badge color="amber" variant="soft">{task.provider || "待生成"}</Badge>
                  </Flex>
                  <div className="doubao-output-list">
                    {task.outputs.slice(0, 5).map((output) => (
                      <div className="doubao-output-row" key={`${task.asset_pack_id}-${output.file}`}>
                        <strong>{output.asset_id}</strong>
                        <span>{output.image_gen_prompt || output.doubao_prompt || output.suggested_prompt_suffix || task.image_gen_prompt || task.image2_prompt}</span>
                        <code>{output.save_path}</code>
                      </div>
                    ))}
                  </div>
                  {task.outputs.length > 5 ? (
                    <Text as="p" size="1" color="gray">另有 {task.outputs.length - 5} 张按同一素材包规则生成。</Text>
                  ) : null}
                </article>
              ))}
            </div>
          ) : (
            <Text as="p" size="2" color="gray" className="doubao-queue-empty">
              当前没有外部生图任务；场景图由智能体按教案临时生成。
            </Text>
          )}
        </section>
      </Container>
    </main>
  );
}

function EducationBucket({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="education-bucket">
      <Text as="p" size="1" color="gray">{title}</Text>
      <div>
        {items.map((item) => <span key={item}>{item}</span>)}
      </div>
    </div>
  );
}

function LibraryBucket({ icon, title, items, empty = "暂无" }: { icon: React.ReactNode; title: string; items: string[]; empty?: string }) {
  return (
    <div className="library-bucket">
      <Flex align="center" gap="2">
        {icon}
        <Text weight="bold">{title}</Text>
      </Flex>
      <div className="kit-list">
        {(items.length ? items : [empty]).map((item) => <span key={item}>{item}</span>)}
      </div>
    </div>
  );
}

function InventoryPanel({ title, items }: { title: string; items: string[] }) {
  return (
    <section className="primary-tool inventory-panel">
      <Text weight="bold">{title}</Text>
      <div className="inventory-list">
        {items.map((item) => <span key={item}>{item}</span>)}
      </div>
    </section>
  );
}

function audioSourceLabel(kind: string) {
  if (kind === "open_sample") return "本地采样播放";
  if (kind === "soundfont_fallback") return "SoundFont";
  if (kind === "webaudio_synthesis") return "WebAudio";
  return kind;
}

function sampleFidelityLabel(item: InstrumentAudioItem) {
  if (item.exact_real_instrument_sample || item.sample_fidelity === "exact_open_sample") return "精确真实采样";
  if (item.sample_fidelity === "close_soundfont_sample") return "SoundFont 接近音色";
  if (item.sample_fidelity === "approximate_soundfont_sample") return "近似采样待补";
  return item.is_real_sample ? "采样播放" : "非真实采样";
}

function audioPackStatusColor(status: string) {
  if (status === "ready" || status === "real_samples_ready") return "green";
  if (status === "sampled_playback_ready_needs_exact_samples") return "amber";
  return "amber";
}

function audioFileReportLabel(report?: InstrumentAudioPack["local_file_report"]) {
  if (!report) return "本地音频文件状态待读取";
  if (report.status === "ready") return `本地 SoundFont 文件已就绪：${report.ready_count} 个`;
  return `本地音频缺文件：${report.missing_count} 个`;
}

function assetSourceLabel(sourceKind: string) {
  if (sourceKind === "open_license_real_photos") return "开源真实照片";
  if (sourceKind === "doubao_generated") return "历史外部生图";
  if (sourceKind === "image2") return "本地 image2 生成";
  if (sourceKind === "image_gen_generated") return "生成 PNG 入库";
  if (sourceKind === "lesson_runtime_generated") return "教案临时生成";
  if (sourceKind === "project_generated") return "项目生成";
  return sourceKind;
}

function assetTemplateStatusLabel(status: string) {
  if (status === "ready_from_manifest") return "manifest 就绪";
  if (status === "pending_until_all_generated_skins_verified") return "乐器皮肤待补齐";
  if (status === "pending_until_png_verified") return "PNG 待入库";
  if (status === "pending_generation_until_png_verified") return "外部 PNG 待验收";
  if (status === "lesson_runtime_generation_required") return "按教案生成";
  return status;
}

function assetTemplateStatusColor(status: string) {
  if (status === "ready_from_manifest") return "green";
  if (status === "pending_until_all_generated_skins_verified") return "amber";
  if (status === "pending_until_png_verified") return "amber";
  if (status === "pending_generation_until_png_verified") return "amber";
  if (status === "lesson_runtime_generation_required") return "blue";
  return "gray";
}

function gameplayStatusLabel(status: string) {
  if (status === "runtime_ready") return "成熟运行";
  if (status === "activity_ready") return "活动页就绪";
  if (status === "spec_ready") return "spec 就绪";
  return status;
}

function gameplayStatusColor(status: string) {
  if (status === "runtime_ready") return "green";
  if (status === "activity_ready") return "teal";
  if (status === "spec_ready") return "gray";
  return "gray";
}

function scenarioImageLabel(kind: string) {
  if (kind === "none") return "无需生图";
  if (kind === "optional_image_gen") return "可临时生图";
  if (kind === "requires_image_gen") return "需要临时生图";
  return kind;
}

function scenarioImageColor(kind: string) {
  if (kind === "requires_image_gen") return "amber";
  if (kind === "optional_image_gen") return "blue";
  return "gray";
}

function teachingAidAssetLabel(aid: TeachingAidSummary) {
  if (aid.real_photo_required) return "真实照片";
  if (aid.asset_pack_required === "generated_playable_instrument_pack") return "生成乐器皮肤";
  if (aid.image_gen_required || aid.asset_policy?.source === "image_gen_generated_png") return "本地 image2 PNG";
  if (aid.doubao_required) return "历史外部 PNG";
  return "组件生成";
}

function teachingAidAssetColor(aid: TeachingAidSummary) {
  if (aid.real_photo_required) return "blue";
  if (aid.image_gen_required || aid.asset_policy?.source === "image_gen_generated_png") return "green";
  if (aid.doubao_required) return "amber";
  return "green";
}

function gradeBandLabel(value: string) {
  return {
    lower_primary: "低段",
    middle_primary: "中段",
    upper_primary: "高段"
  }[value] || value;
}

function competencyLabel(alignment: EducationAlignment) {
  return alignment.secondary_competency
    ? `${alignment.primary_competency} + ${alignment.secondary_competency}`
    : alignment.primary_competency;
}

function practiceLabel(value: string) {
  return {
    listen: "听",
    sing: "唱",
    tap: "拍",
    move: "动",
    play: "奏",
    arrange: "排",
    choose: "选",
    match: "辨",
    order: "排序",
    create: "创",
    revise: "改",
    cooperate: "合作",
    perform: "表现",
    assess: "评",
    explain: "说依据"
  }[value] || value;
}
