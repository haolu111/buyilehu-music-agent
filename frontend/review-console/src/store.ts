import { create } from "zustand";

export type TemplateId =
  | "beat_guardian_core"
  | "pitch_ladder_core"
  | "rhythm_echo_core"
  | "solfege_target_core"
  | "timbre_detective_core"
  | "form_treasure_core"
  | "composition_puzzle_core";
export type RhythmEchoMode = "echo_tap" | "echo_body_percussion" | "echo_chain";
export type BeatGuardianMode = "beat_defense" | "strong_beat_guard" | "meter_gate";
export type PitchLadderMode = "high_low_steps" | "solfege_ladder" | "melody_climb";
export type SolfegeTargetMode = "listen_and_hit" | "aim_and_sing" | "target_chain";
export type TimbreDetectiveMode = "instrument_clue" | "family_sorting" | "compare_twins";
export type FormTreasureMode = "aba_treasure" | "rondo_treasure" | "repeat_contrast";
export type CompositionPuzzleMode = "rhythm_puzzle_composition" | "melody_puzzle_creation" | "melody_rhythm_puzzle";
export type Meter = "2/4" | "3/4" | "4/4";
export type Difficulty = "L1" | "L2" | "L3" | "L4" | "L5";
export type GameSkin =
  | "castle_gate"
  | "stage_light"
  | "dragon_boat"
  | "train_conductor"
  | "space_orbit"
  | "rhythm_radio"
  | "echo_cave"
  | "robot_signal"
  | "rain_window"
  | "kitchen_band"
  | "mountain_steps"
  | "cloud_elevator"
  | "bamboo_ladder"
  | "lantern_tower"
  | "star_target"
  | "flower_bloom"
  | "lantern_target"
  | "archery_field"
  | "bubble_pop"
  | "sound_casebook"
  | "museum_clues"
  | "forest_echo"
  | "studio_mixer"
  | "shadow_theater"
  | "treasure_map"
  | "constellation_path"
  | "museum_gallery"
  | "train_route"
  | "stage_script"
  | "composition_studio"
  | "rhythm_tile_table"
  | "melody_garden";

export type TemplateForm = {
  template_id: TemplateId;
  difficulty: Difficulty;
  mode:
    | RhythmEchoMode
    | BeatGuardianMode
    | PitchLadderMode
    | SolfegeTargetMode
    | TimbreDetectiveMode
    | FormTreasureMode
    | CompositionPuzzleMode;
  grade_band: string;
  music_concept: string;
  meter: Meter;
  tonic: string;
  scale_type: string;
  pitch_range: string[];
  target_solfege: string[];
  solfege_system: string;
  sound_set: string;
  instrument_pool: string[];
  timbre_traits: string[];
  choices_per_round: number;
  evidence_required: number;
  form_type: "ABA" | "回旋" | "重复对比";
  section_length_bars: number;
  hint_mode: "guided" | "partial" | "challenge";
  phrase_length_bars: number;
  composition_total_bars: number;
  composition_segment_bars: number;
  composition_segments: number;
  length_clamped: boolean;
  slots_per_bar: number;
  constraint_profile: "guided" | "balanced" | "challenge";
  rhythm_cards: string[];
  melody_cards: string[];
  notes_per_round: number;
  retry_limit: number;
  bpm: number;
  round_count: number;
  bars_per_round: number;
  count_in_bars: number;
  timing_tolerance_ms: number;
  pass_score: number;
  allow_relisten: boolean;
  visual_beat_hint: boolean;
  allow_practice_round: boolean;
  show_beat_track: boolean;
  show_strong_beat_hint: boolean;
  show_weak_beat_hint: boolean;
  show_staff_hint: boolean;
  show_solfege_hint: boolean;
  show_direction_hint: boolean;
  show_pitch_hint: boolean;
  require_sing_back: boolean;
  sing_back_required: boolean;
  teacher_confirm_required: boolean;
  mic_assist_enabled: boolean;
  show_wave_hint: boolean;
  show_family_hint: boolean;
  require_reason: boolean;
  ai_clue_enabled: boolean;
  hf_model_id: string;
  skin_id: GameSkin;
  target_beats: number[];
  combo_required: number;
  mistake_limit: number;
  teacher_prompt: string;
};

export type GameInstance = {
  instance_id: string;
  template_id: TemplateId;
  template_label: string;
  scaffold_id: string;
  generation_mode: string;
  opencode_required: boolean;
  config: TemplateForm & Record<string, unknown>;
  student_task: Record<string, string>;
  scoring: Record<string, number>;
  feedback_rules: Record<string, string>;
};

type ConsoleState = {
  form: TemplateForm;
  instance: GameInstance | null;
  loading: boolean;
  error: string;
  updateForm: (patch: Partial<TemplateForm>) => void;
  loadForm: (payload: Partial<TemplateForm>) => void;
  switchTemplate: (templateId: TemplateId) => void;
  createInstance: () => Promise<void>;
};

const beatGuardianDefaults: TemplateForm = {
  template_id: "beat_guardian_core",
  difficulty: "L2",
  mode: "strong_beat_guard",
  grade_band: "小学低段",
  music_concept: "强拍与弱拍",
  meter: "2/4",
  tonic: "C",
  scale_type: "major_pentatonic",
  pitch_range: ["do", "re", "mi", "sol", "la"],
  target_solfege: ["do", "mi", "sol"],
  solfege_system: "movable_do",
  sound_set: "classroom_instruments",
  instrument_pool: ["笛子", "二胡", "小提琴", "钢琴", "小鼓", "木鱼"],
  timbre_traits: ["明亮", "柔和", "短促", "持续", "气息感", "弦鸣", "敲击感"],
  choices_per_round: 4,
  evidence_required: 1,
  form_type: "ABA",
  section_length_bars: 8,
  hint_mode: "partial",
  phrase_length_bars: 2,
  composition_total_bars: 2,
  composition_segment_bars: 2,
  composition_segments: 1,
  length_clamped: false,
  slots_per_bar: 4,
  constraint_profile: "guided",
  rhythm_cards: ["quarter", "eighth_pair", "rest", "half"],
  melody_cards: ["do", "re", "mi", "sol", "la"],
  notes_per_round: 2,
  retry_limit: 3,
  bpm: 86,
  round_count: 5,
  bars_per_round: 4,
  count_in_bars: 1,
  timing_tolerance_ms: 205,
  pass_score: 0.82,
  allow_relisten: true,
  visual_beat_hint: true,
  allow_practice_round: true,
  show_beat_track: true,
  show_strong_beat_hint: true,
  show_weak_beat_hint: false,
  show_staff_hint: false,
  show_solfege_hint: true,
  show_direction_hint: false,
  show_pitch_hint: false,
  require_sing_back: true,
  sing_back_required: true,
  teacher_confirm_required: true,
  mic_assist_enabled: false,
  show_wave_hint: false,
  show_family_hint: false,
  require_reason: true,
  ai_clue_enabled: false,
  hf_model_id: "MIT/ast-finetuned-audioset-10-10-0.4593",
  skin_id: "castle_gate",
  target_beats: [1],
  combo_required: 4,
  mistake_limit: 5,
  teacher_prompt: "观察护盾收缩并预判每小节第 1 拍，动作要和强拍同时发生，不要听到后补按。"
};

const pitchLadderDefaults: TemplateForm = {
  template_id: "pitch_ladder_core",
  difficulty: "L2",
  mode: "high_low_steps",
  grade_band: "小学低段",
  music_concept: "高低与级进",
  meter: "2/4",
  tonic: "C",
  scale_type: "major_pentatonic",
  pitch_range: ["do", "re", "mi", "sol", "la"],
  target_solfege: ["do", "mi", "sol"],
  solfege_system: "movable_do",
  sound_set: "classroom_instruments",
  instrument_pool: ["笛子", "二胡", "小提琴", "钢琴", "小鼓", "木鱼"],
  timbre_traits: ["明亮", "柔和", "短促", "持续", "气息感", "弦鸣", "敲击感"],
  choices_per_round: 4,
  evidence_required: 1,
  form_type: "ABA",
  section_length_bars: 8,
  hint_mode: "partial",
  phrase_length_bars: 2,
  composition_total_bars: 2,
  composition_segment_bars: 2,
  composition_segments: 1,
  length_clamped: false,
  slots_per_bar: 4,
  constraint_profile: "guided",
  rhythm_cards: ["quarter", "eighth_pair", "rest", "half"],
  melody_cards: ["do", "re", "mi", "sol", "la"],
  notes_per_round: 2,
  retry_limit: 3,
  bpm: 88,
  round_count: 6,
  bars_per_round: 1,
  count_in_bars: 0,
  timing_tolerance_ms: 0,
  pass_score: 0.8,
  allow_relisten: true,
  visual_beat_hint: false,
  allow_practice_round: true,
  show_beat_track: false,
  show_strong_beat_hint: false,
  show_weak_beat_hint: false,
  show_staff_hint: false,
  show_solfege_hint: true,
  show_direction_hint: false,
  show_pitch_hint: false,
  require_sing_back: true,
  sing_back_required: true,
  teacher_confirm_required: true,
  mic_assist_enabled: false,
  show_wave_hint: false,
  show_family_hint: false,
  require_reason: true,
  ai_clue_enabled: false,
  hf_model_id: "MIT/ast-finetuned-audioset-10-10-0.4593",
  skin_id: "mountain_steps",
  target_beats: [1],
  combo_required: 3,
  mistake_limit: 3,
  teacher_prompt: "先听，再判断第二个音是更高还是更低，最后唱出来。"
};

const solfegeTargetDefaults: TemplateForm = {
  template_id: "solfege_target_core",
  difficulty: "L2",
  mode: "listen_and_hit",
  grade_band: "小学低段",
  music_concept: "唱名听辨与模唱",
  meter: "2/4",
  tonic: "C",
  scale_type: "major_pentatonic",
  pitch_range: ["do", "re", "mi", "sol", "la"],
  target_solfege: ["do", "mi", "sol"],
  solfege_system: "movable_do",
  sound_set: "classroom_instruments",
  instrument_pool: ["笛子", "二胡", "小提琴", "钢琴", "小鼓", "木鱼"],
  timbre_traits: ["明亮", "柔和", "短促", "持续", "气息感", "弦鸣", "敲击感"],
  choices_per_round: 4,
  evidence_required: 1,
  form_type: "ABA",
  section_length_bars: 8,
  hint_mode: "partial",
  phrase_length_bars: 2,
  composition_total_bars: 2,
  composition_segment_bars: 2,
  composition_segments: 1,
  length_clamped: false,
  slots_per_bar: 4,
  constraint_profile: "guided",
  rhythm_cards: ["quarter", "eighth_pair", "rest", "half"],
  melody_cards: ["do", "re", "mi", "sol", "la"],
  notes_per_round: 1,
  retry_limit: 3,
  bpm: 84,
  round_count: 6,
  bars_per_round: 1,
  count_in_bars: 0,
  timing_tolerance_ms: 0,
  pass_score: 0.8,
  allow_relisten: true,
  visual_beat_hint: false,
  allow_practice_round: true,
  show_beat_track: false,
  show_strong_beat_hint: false,
  show_weak_beat_hint: false,
  show_staff_hint: false,
  show_solfege_hint: true,
  show_direction_hint: false,
  show_pitch_hint: false,
  require_sing_back: true,
  sing_back_required: true,
  teacher_confirm_required: true,
  mic_assist_enabled: false,
  show_wave_hint: false,
  show_family_hint: false,
  require_reason: true,
  ai_clue_enabled: false,
  hf_model_id: "MIT/ast-finetuned-audioset-10-10-0.4593",
  skin_id: "star_target",
  target_beats: [1],
  combo_required: 3,
  mistake_limit: 3,
  teacher_prompt: "先听目标音，在心里唱一遍，再击中对应唱名靶，并开口唱出来。"
};

const rhythmEchoDefaults: TemplateForm = {
  template_id: "rhythm_echo_core",
  difficulty: "L2",
  mode: "echo_tap",
  grade_band: "小学低段",
  music_concept: "四分音符与八分音符",
  meter: "2/4",
  tonic: "C",
  scale_type: "major_pentatonic",
  pitch_range: ["do", "re", "mi", "sol", "la"],
  target_solfege: ["do", "mi", "sol"],
  solfege_system: "movable_do",
  sound_set: "classroom_instruments",
  instrument_pool: ["笛子", "二胡", "小提琴", "钢琴", "小鼓", "木鱼"],
  timbre_traits: ["明亮", "柔和", "短促", "持续", "气息感", "弦鸣", "敲击感"],
  choices_per_round: 4,
  evidence_required: 1,
  form_type: "ABA",
  section_length_bars: 8,
  hint_mode: "partial",
  phrase_length_bars: 2,
  composition_total_bars: 2,
  composition_segment_bars: 2,
  composition_segments: 1,
  length_clamped: false,
  slots_per_bar: 4,
  constraint_profile: "guided",
  rhythm_cards: ["quarter", "eighth_pair", "rest", "half"],
  melody_cards: ["do", "re", "mi", "sol", "la"],
  notes_per_round: 2,
  retry_limit: 3,
  bpm: 92,
  round_count: 6,
  bars_per_round: 1,
  count_in_bars: 0,
  timing_tolerance_ms: 180,
  pass_score: 0.8,
  allow_relisten: true,
  visual_beat_hint: true,
  allow_practice_round: false,
  show_beat_track: true,
  show_strong_beat_hint: true,
  show_weak_beat_hint: false,
  show_staff_hint: false,
  show_solfege_hint: true,
  show_direction_hint: false,
  show_pitch_hint: false,
  require_sing_back: true,
  sing_back_required: true,
  teacher_confirm_required: true,
  mic_assist_enabled: false,
  show_wave_hint: false,
  show_family_hint: false,
  require_reason: true,
  ai_clue_enabled: false,
  hf_model_id: "MIT/ast-finetuned-audioset-10-10-0.4593",
  skin_id: "rhythm_radio",
  target_beats: [1],
  combo_required: 3,
  mistake_limit: 3,
  teacher_prompt: "先听清楚，再拍出来，说一说这个节奏哪里稳。"
};

const timbreDetectiveDefaults: TemplateForm = {
  template_id: "timbre_detective_core",
  difficulty: "L2",
  mode: "instrument_clue",
  grade_band: "小学中段",
  music_concept: "音色听辨与乐器识别",
  meter: "2/4",
  tonic: "C",
  scale_type: "major_pentatonic",
  pitch_range: ["do", "re", "mi", "sol", "la"],
  target_solfege: ["do", "mi", "sol"],
  solfege_system: "movable_do",
  sound_set: "classroom_instruments",
  instrument_pool: ["笛子", "二胡", "小提琴", "钢琴", "小鼓", "木鱼"],
  timbre_traits: ["明亮", "柔和", "短促", "持续", "气息感", "弦鸣", "敲击感"],
  choices_per_round: 4,
  evidence_required: 1,
  form_type: "ABA",
  section_length_bars: 8,
  hint_mode: "partial",
  phrase_length_bars: 2,
  composition_total_bars: 2,
  composition_segment_bars: 2,
  composition_segments: 1,
  length_clamped: false,
  slots_per_bar: 4,
  constraint_profile: "guided",
  rhythm_cards: ["quarter", "eighth_pair", "rest", "half"],
  melody_cards: ["do", "re", "mi", "sol", "la"],
  notes_per_round: 1,
  retry_limit: 3,
  bpm: 84,
  round_count: 6,
  bars_per_round: 1,
  count_in_bars: 0,
  timing_tolerance_ms: 0,
  pass_score: 0.8,
  allow_relisten: true,
  visual_beat_hint: false,
  allow_practice_round: true,
  show_beat_track: false,
  show_strong_beat_hint: false,
  show_weak_beat_hint: false,
  show_staff_hint: false,
  show_solfege_hint: true,
  show_direction_hint: false,
  show_pitch_hint: false,
  require_sing_back: false,
  sing_back_required: false,
  teacher_confirm_required: true,
  mic_assist_enabled: false,
  show_wave_hint: true,
  show_family_hint: false,
  require_reason: true,
  ai_clue_enabled: false,
  hf_model_id: "MIT/ast-finetuned-audioset-10-10-0.4593",
  skin_id: "sound_casebook",
  target_beats: [1],
  combo_required: 3,
  mistake_limit: 3,
  teacher_prompt: "先听声音，再找乐器嫌疑人，最后说出你判断的音色证据。"
};

const formTreasureDefaults: TemplateForm = {
  template_id: "form_treasure_core",
  difficulty: "L3",
  mode: "aba_treasure",
  grade_band: "小学高段-初中",
  music_concept: "曲式结构听辨",
  meter: "4/4",
  tonic: "C",
  scale_type: "major",
  pitch_range: ["do", "re", "mi", "fa", "sol", "la"],
  target_solfege: ["do", "mi", "sol"],
  solfege_system: "movable_do",
  sound_set: "form_segments",
  instrument_pool: ["钢琴", "木琴", "弦乐", "长笛"],
  timbre_traits: ["重复", "对比", "再现", "结束感"],
  choices_per_round: 3,
  evidence_required: 1,
  form_type: "ABA",
  section_length_bars: 8,
  hint_mode: "partial",
  phrase_length_bars: 2,
  composition_total_bars: 2,
  composition_segment_bars: 2,
  composition_segments: 1,
  length_clamped: false,
  slots_per_bar: 4,
  constraint_profile: "balanced",
  rhythm_cards: ["quarter", "eighth_pair", "rest", "half"],
  melody_cards: ["do", "re", "mi", "fa", "sol", "la"],
  notes_per_round: 3,
  retry_limit: 3,
  bpm: 88,
  round_count: 3,
  bars_per_round: 8,
  count_in_bars: 0,
  timing_tolerance_ms: 0,
  pass_score: 0.8,
  allow_relisten: true,
  visual_beat_hint: true,
  allow_practice_round: true,
  show_beat_track: false,
  show_strong_beat_hint: false,
  show_weak_beat_hint: false,
  show_staff_hint: false,
  show_solfege_hint: false,
  show_direction_hint: false,
  show_pitch_hint: false,
  require_sing_back: false,
  sing_back_required: false,
  teacher_confirm_required: true,
  mic_assist_enabled: false,
  show_wave_hint: false,
  show_family_hint: false,
  require_reason: true,
  ai_clue_enabled: false,
  hf_model_id: "MIT/ast-finetuned-audioset-10-10-0.4593",
  skin_id: "treasure_map",
  target_beats: [1],
  combo_required: 3,
  mistake_limit: 3,
  teacher_prompt: "听每个段落的主题是否重复、变化或对比，再把结构卡排成曲式路线。"
};

const compositionPuzzleDefaults: TemplateForm = {
  template_id: "composition_puzzle_core",
  difficulty: "L2",
  mode: "melody_rhythm_puzzle",
  grade_band: "小学中段",
  music_concept: "节奏与旋律创编",
  meter: "2/4",
  tonic: "C",
  scale_type: "major_pentatonic",
  pitch_range: ["do", "re", "mi", "sol", "la"],
  target_solfege: ["do", "mi", "sol"],
  solfege_system: "movable_do",
  sound_set: "composition_cards",
  instrument_pool: ["钢琴", "木琴", "小鼓", "木鱼"],
  timbre_traits: ["稳定", "变化", "休止", "结束感"],
  choices_per_round: 4,
  evidence_required: 1,
  form_type: "ABA",
  section_length_bars: 8,
  hint_mode: "partial",
  phrase_length_bars: 2,
  composition_total_bars: 2,
  composition_segment_bars: 2,
  composition_segments: 1,
  length_clamped: false,
  slots_per_bar: 4,
  constraint_profile: "guided",
  rhythm_cards: ["quarter", "eighth_pair", "sixteenth_four", "rest"],
  melody_cards: ["do", "re", "mi", "sol", "la"],
  notes_per_round: 3,
  retry_limit: 3,
  bpm: 92,
  round_count: 4,
  bars_per_round: 2,
  count_in_bars: 0,
  timing_tolerance_ms: 0,
  pass_score: 0.8,
  allow_relisten: true,
  visual_beat_hint: true,
  allow_practice_round: true,
  show_beat_track: true,
  show_strong_beat_hint: true,
  show_weak_beat_hint: false,
  show_staff_hint: false,
  show_solfege_hint: true,
  show_direction_hint: true,
  show_pitch_hint: false,
  require_sing_back: false,
  sing_back_required: false,
  teacher_confirm_required: true,
  mic_assist_enabled: false,
  show_wave_hint: false,
  show_family_hint: false,
  require_reason: true,
  ai_clue_enabled: false,
  hf_model_id: "MIT/ast-finetuned-audioset-10-10-0.4593",
  skin_id: "composition_studio",
  target_beats: [1],
  combo_required: 3,
  mistake_limit: 3,
  teacher_prompt: "先让学生用素材卡拼出短句，试听后检查是否满足节奏或旋律约束，再请学生说明创编理由。"
};

export const templateDefaults: Record<TemplateId, TemplateForm> = {
  beat_guardian_core: beatGuardianDefaults,
  pitch_ladder_core: pitchLadderDefaults,
  rhythm_echo_core: rhythmEchoDefaults,
  solfege_target_core: solfegeTargetDefaults,
  timbre_detective_core: timbreDetectiveDefaults,
  form_treasure_core: formTreasureDefaults,
  composition_puzzle_core: compositionPuzzleDefaults
};

function defaultSkinForTemplate(templateId: TemplateId): GameSkin {
  return templateDefaults[templateId].skin_id;
}

function normalizeTemplateForm(form: TemplateForm): TemplateForm {
  return {
    ...form,
    skin_id: defaultSkinForTemplate(form.template_id)
  };
}

export const useConsoleStore = create<ConsoleState>((set, get) => ({
  form: beatGuardianDefaults,
  instance: null,
  loading: false,
  error: "",
  updateForm: (patch) => set((state) => ({ form: normalizeTemplateForm({ ...state.form, ...patch }) })),
  loadForm: (payload) =>
    set((state) => {
      const templateId = payload.template_id && templateDefaults[payload.template_id] ? payload.template_id : state.form.template_id;
      return {
        form: normalizeTemplateForm({
          ...templateDefaults[templateId],
          ...payload,
          template_id: templateId
        }),
        instance: null,
        error: ""
      };
    }),
  switchTemplate: (templateId) =>
    set({
      form: templateDefaults[templateId],
      instance: null,
      error: ""
    }),
  createInstance: async () => {
    set({ loading: true, error: "" });
    try {
      const response = await fetch("/api/game-instances", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(get().form)
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.error || "生成失败");
      }
      set({ instance: payload.instance, loading: false });
    } catch (error) {
      set({ error: error instanceof Error ? error.message : "生成失败", loading: false });
    }
  }
}));
