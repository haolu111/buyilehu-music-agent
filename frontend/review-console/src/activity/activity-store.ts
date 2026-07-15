import { create } from "zustand";

export type GenerationMode = "lesson_upload" | "direct";
export type ClassroomGoal = "听辨" | "学唱" | "节奏" | "音高" | "器乐" | "创编" | "欣赏" | "复习";
export type StudentBehavior = "听一听" | "唱一唱" | "拍一拍" | "奏一奏" | "排一排" | "编一编" | "说一说";
export type ActivityForm = "虚拟教具" | "虚拟乐器" | "小游戏" | "小组活动" | "练习页面" | "综合活动";

export type ActivitySpecInput = {
  generation_mode: GenerationMode;
  teacher_request: string;
  structured_fields: {
    classroom_goal: ClassroomGoal;
    student_behavior: StudentBehavior;
    activity_form: ActivityForm;
  };
};

export type TeacherPlanCardModel = {
  mode: "教案生成" | "直接生成";
  source_basis: string;
  understood_goal: string;
  music_materials: string[];
  student_actions: string[];
  recommended_activity_form: string;
  tools_instruments_or_games: string[];
  difficulty_and_hint_strategy: string;
  grade_fit_reason: string;
  teacher_confirmations: string[];
  default_materials: string[];
  music_education_rules: string[];
  non_digital_sections: string[];
  low_confidence_materials: string[];
};

export type LessonSegment = {
  segment_id: string;
  stage: string;
  source_evidence: string;
  teaching_goal: string;
  music_material: string;
  student_behaviors: string[];
  music_focus: string[];
  digital_potential: string;
};

export type SelectedTeachingSegment = {
  version: string;
  segment_id: string;
  selection_reason: string;
  source_evidence: string;
  must_preserve: {
    teaching_goal: string;
    music_material: string;
    student_behaviors: string[];
    music_focus?: string[];
  };
  must_not_add: string[];
};

export type SegmentGameBrief = {
  version: string;
  source_segment_id: string;
  source_evidence: string;
  game_goal: string;
  music_learning_target: string;
  student_actions: string[];
  core_mechanic: string;
  success_condition: string;
  error_feedback: Array<{ error_type: string; feedback: string }>;
  classroom_return: string;
};

export type LessonCase = {
  version: string;
  lesson_title: string;
  grade_band: string;
  segments: LessonSegment[];
};

export type LessonCaseLoopResult = {
  lesson_case: LessonCase;
  selected_segment: SelectedTeachingSegment;
  segment_game_brief: SegmentGameBrief;
  candidate_segments?: LessonSegment[];
};

export type LessonCaseArtifact = {
  artifact_id: string;
  page_url: string;
  teacher_url: string;
  file_path: string;
  files: string[];
};

export type LessonCaseGenerateResult = LessonCaseLoopResult & {
  artifact_id: string;
  page_url: string;
  teacher_url: string;
  artifact: LessonCaseArtifact;
  qa_report: { status: string; blocking_issues?: string[]; warning_issues?: string[] };
  lesson_segment_grounding_result: { status: string; blocking_issues?: string[] };
  teacher_control_state: { tempo: number; show_hint: boolean; focus: string; paused: boolean };
};

export type ClassroomControlAction =
  | "pause"
  | "reset"
  | "tempo"
  | "difficulty_down"
  | "difficulty_up"
  | "hint_visibility"
  | "phrase_focus"
  | "mode_switch"
  | "instrument_voice"
  | "regenerate_plan_card"
  | "continue_editing";

export type WorkManagementAction =
  | "preview"
  | "continue_edit"
  | "duplicate"
  | "download_package"
  | "save_as_template"
  | "last_classroom_config";

export const classroomControlActions: ClassroomControlAction[] = [
  "pause",
  "reset",
  "tempo",
  "difficulty_down",
  "difficulty_up",
  "hint_visibility",
  "phrase_focus",
  "mode_switch",
  "instrument_voice",
  "regenerate_plan_card",
  "continue_editing",
];

export const workManagementActions: WorkManagementAction[] = [
  "preview",
  "continue_edit",
  "duplicate",
  "download_package",
  "save_as_template",
  "last_classroom_config",
];

type ActivityWorkbenchState = {
  mode: GenerationMode;
  classroomGoal: ClassroomGoal;
  studentBehavior: StudentBehavior;
  activityForm: ActivityForm;
  teacherRequest: string;
  bpm: number;
  showHint: boolean;
  paused: boolean;
  focus: string;
  classMode: "个人" | "小组" | "全班";
  lessonText: string;
  lessonLoop: LessonCaseLoopResult | null;
  generatedLessonGame: LessonCaseGenerateResult | null;
  loopStatus: "idle" | "analyzing" | "ready" | "generating" | "generated" | "error";
  loopError: string;
  setMode: (mode: GenerationMode) => void;
  setWizardField: (field: "classroomGoal" | "studentBehavior" | "activityForm", value: string) => void;
  setTeacherRequest: (teacherRequest: string) => void;
  setLessonText: (lessonText: string) => void;
  setLessonLoop: (lessonLoop: LessonCaseLoopResult | null) => void;
  setGeneratedLessonGame: (generatedLessonGame: LessonCaseGenerateResult | null) => void;
  setLoopStatus: (loopStatus: ActivityWorkbenchState["loopStatus"]) => void;
  setLoopError: (loopError: string) => void;
  applyControl: (action: ClassroomControlAction) => void;
};

export const useActivityWorkbenchStore = create<ActivityWorkbenchState>((set) => ({
  mode: "lesson_upload",
  classroomGoal: "节奏",
  studentBehavior: "拍一拍",
  activityForm: "小游戏",
  teacherRequest: "二年级二拍子强弱小游戏，先听再拍。",
  bpm: 88,
  showHint: true,
  paused: false,
  focus: "全部",
  classMode: "全班",
  lessonText:
    "课题：《小雨沙沙》\n学段：小学低段\n二、学唱前节拍体验\n听第一乐句，感受二拍子强弱，并用拍手表现。学生跟随音乐做小雨沙沙的律动。",
  lessonLoop: null,
  generatedLessonGame: null,
  loopStatus: "idle",
  loopError: "",
  setMode: (mode) => set({ mode }),
  setWizardField: (field, value) => set({ [field]: value } as Pick<ActivityWorkbenchState, typeof field>),
  setTeacherRequest: (teacherRequest) => set({ teacherRequest }),
  setLessonText: (lessonText) => set({ lessonText }),
  setLessonLoop: (lessonLoop) => set({ lessonLoop }),
  setGeneratedLessonGame: (generatedLessonGame) => set({ generatedLessonGame }),
  setLoopStatus: (loopStatus) => set({ loopStatus }),
  setLoopError: (loopError) => set({ loopError }),
  applyControl: (action) =>
    set((state) => {
      if (action === "pause") return { paused: !state.paused };
      if (action === "reset") return { paused: false, bpm: 88, showHint: true, focus: "全部", classMode: "全班" };
      if (action === "tempo") return { bpm: state.bpm === 88 ? 76 : 88 };
      if (action === "difficulty_down") return { showHint: true, bpm: Math.max(72, state.bpm - 8) };
      if (action === "difficulty_up") return { showHint: false, bpm: Math.min(116, state.bpm + 8) };
      if (action === "hint_visibility") return { showHint: !state.showHint };
      if (action === "phrase_focus") return { focus: state.focus === "全部" ? "第二句" : "全部" };
      if (action === "mode_switch") return { classMode: state.classMode === "全班" ? "小组" : state.classMode === "小组" ? "个人" : "全班" };
      return {};
    }),
}));

export function buildActivitySpecInput(state: {
  mode: GenerationMode;
  classroomGoal: ClassroomGoal;
  studentBehavior: StudentBehavior;
  activityForm: ActivityForm;
  teacherRequest: string;
}): ActivitySpecInput {
  return {
    generation_mode: state.mode,
    teacher_request: state.teacherRequest,
    structured_fields: {
      classroom_goal: state.classroomGoal,
      student_behavior: state.studentBehavior,
      activity_form: state.activityForm,
    },
  };
}

export function buildLocalPlanCard(input: ActivitySpecInput): TeacherPlanCardModel {
  const lessonMode = input.generation_mode === "lesson_upload";
  return {
    mode: lessonMode ? "教案生成" : "直接生成",
    source_basis: lessonMode
      ? "我将基于上传教案中最适合数字化的环节生成活动链。"
      : "当前没有绑定具体教案；我将基于你的直接需求和系统默认练习材料生成。",
    understood_goal: `围绕${input.structured_fields.classroom_goal}目标，让学生${input.structured_fields.student_behavior}并完成课堂回扣。`,
    music_materials: lessonMode ? ["教案识别材料", "教师确认后的片段"] : ["系统默认二拍子练习材料", "可补充音频或谱例"],
    student_actions: [input.structured_fields.student_behavior, "说一说依据"],
    recommended_activity_form: input.structured_fields.activity_form,
    tools_instruments_or_games: ["教师控制台", "学生操作区", input.structured_fields.activity_form],
    difficulty_and_hint_strategy: "默认低段速度 88 BPM，显示提示；课堂中可降速、只练某句或切换小组模式。",
    grade_fit_reason: "少文字、大按钮、先听再做，适合小学课堂投屏和平板触摸。",
    teacher_confirmations: lessonMode
      ? ["请确认教案环节、音乐材料和低置信片段。"]
      : ["当前未上传教案。", "当前未绑定具体歌曲。", "如果要贴合某首歌或某份教案，请补充教案、音频或谱例。"],
    default_materials: lessonMode ? [] : ["系统默认二拍子或节奏练习材料"],
    music_education_rules: ["先听再做", "用音乐要素反馈", "完成后回到教材音乐"],
    non_digital_sections: lessonMode ? ["教师示范、情感交流和完整讨论不强行数字化。"] : [],
    low_confidence_materials: [],
  };
}
