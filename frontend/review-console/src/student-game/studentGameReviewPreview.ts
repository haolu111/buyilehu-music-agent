import { templateDefaults, type TemplateId } from "../store";
import type { LooseRecord, StudentGameState, StudentTaskCopy } from "./types";

const REVIEW_TEMPLATE_IDS = Object.keys(templateDefaults) as TemplateId[];

const reviewCopy: Record<TemplateId, { name: string; listen: string; do: string; pass: string; operation: string }> = {
  beat_guardian_core: { name: "充能护盾", listen: "听稳定拍和每小节第1拍。", do: "在强拍同步充能。", pass: "连续命中目标拍并说出强弱规律。", operation: "beat_guard" },
  pitch_ladder_core: { name: "音高爬梯", listen: "听旋律音高走向。", do: "选择正确的高低位置或唱名。", pass: "连续完成旋律路径并唱回。", operation: "pitch_ladder" },
  rhythm_echo_core: { name: "节奏复刻", listen: "听完整目标节奏。", do: "预备拍后独立拍回。", pass: "拍点、休止和音头数量符合目标。", operation: "rhythm_echo" },
  solfege_target_core: { name: "唱名打靶", listen: "听目标音并在心里唱一遍。", do: "击中对应唱名靶。", pass: "命中并由教师确认唱回。", operation: "solfege_target" },
  timbre_detective_core: { name: "音色侦探", listen: "听真实采样与对照声音。", do: "选择乐器或家族并贴上可听证据。", pass: "答案和音色证据同时正确。", operation: "timbre_detective" },
  form_treasure_core: { name: "曲式寻宝", listen: "复听已确认的音频段落。", do: "按重复、对比和再现排列曲式卡。", pass: "结构顺序与声音证据一致。", operation: "form_treasure" },
  composition_puzzle_core: { name: "拼图创编工坊", listen: "听教师给定的音高和节奏材料。", do: "拖拽材料创编、试听并修改。", pass: "作品符合音高和小节约束并能说明理由。", operation: "composition_puzzle" }
};

export function resolveStudentGameReviewTemplate(search: string): TemplateId {
  const params = new URLSearchParams(search);
  const requested = params.get("review") === "1" ? params.get("template") : "";
  return REVIEW_TEMPLATE_IDS.includes(requested as TemplateId) ? requested as TemplateId : "solfege_target_core";
}

export type FormalGameTemplate = {
  label?: string;
  description?: string;
  default_config?: LooseRecord;
};

export function createStudentGameReviewState(templateId: TemplateId, formalTemplate?: FormalGameTemplate): StudentGameState {
  const copy = reviewCopy[templateId];
  const formalConfig = isRecord(formalTemplate?.default_config) ? formalTemplate.default_config : {};
  const config = { ...templateDefaults[templateId], ...formalConfig, template_id: templateId } as LooseRecord;
  const taskCopy = reviewTaskCopy(config.student_task_copy, copy);
  const templateLabel = formalTemplate?.label?.trim() || copy.name;
  const prompt = formalTemplate?.description?.trim() || `审核示例：${copy.listen}${copy.do}`;
  return {
    workflow: {
      workflow_kind: "music_education_review_example",
      gameplay_blueprint: {
        student_facing_name: templateLabel,
        prompt,
        scene_goal: taskCopy.pass || copy.pass,
        operation_type: copy.operation
      }
    },
    instance: {
      template_label: templateLabel,
      student_task: {
        listen: `听什么：${taskCopy.listen || copy.listen}`,
        do: `做什么：${taskCopy.do || copy.do}`,
        pass: `怎样过关：${taskCopy.pass || copy.pass}`
      }
    },
    template_id: templateId,
    age_ui_profile: "lower_primary",
    config,
    student_task_copy: taskCopy,
    result_transfer_prompt: "审核这个游戏是否真正回到课堂音乐目标。"
  };
}

function reviewTaskCopy(value: unknown, fallback: StudentTaskCopy): StudentTaskCopy {
  if (!isRecord(value)) return { listen: fallback.listen, do: fallback.do, pass: fallback.pass };
  return {
    listen: stringValue(value.listen) || fallback.listen,
    do: stringValue(value.do) || fallback.do,
    pass: stringValue(value.pass) || fallback.pass
  };
}

function isRecord(value: unknown): value is LooseRecord {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function stringValue(value: unknown): string | undefined {
  return typeof value === "string" && value.trim() ? value.trim() : undefined;
}
