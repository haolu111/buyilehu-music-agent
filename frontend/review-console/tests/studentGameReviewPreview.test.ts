import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import {
  createStudentGameReviewState,
  resolveStudentGameReviewTemplate
} from "../src/student-game/studentGameReviewPreview";

assert.equal(resolveStudentGameReviewTemplate("?template=timbre_detective_core&review=1"), "timbre_detective_core");
assert.equal(resolveStudentGameReviewTemplate("?template=not-real&review=1"), "solfege_target_core");
assert.equal(resolveStudentGameReviewTemplate("?template=beat_guardian_core"), "solfege_target_core", "review flag is required");

const gameIds = [
  "beat_guardian_core",
  "pitch_ladder_core",
  "rhythm_echo_core",
  "solfege_target_core",
  "timbre_detective_core",
  "form_treasure_core",
  "composition_puzzle_core"
] as const;

for (const templateId of gameIds) {
  const state = createStudentGameReviewState(templateId);
  assert.equal(state.template_id, templateId);
  assert.equal(state.config?.template_id, templateId);
  assert.equal(state.workflow?.workflow_kind, "music_education_review_example");
  assert.match(state.workflow?.gameplay_blueprint?.prompt || "", /审核示例/);
  assert.ok(state.instance?.student_task?.listen);
  assert.ok(state.instance?.student_task?.do);
  assert.ok(state.instance?.student_task?.pass);
}

const createReviewStateFromFormalTemplate = createStudentGameReviewState as (
  templateId: typeof gameIds[number],
  template?: { label: string; description: string; default_config: Record<string, unknown> }
) => ReturnType<typeof createStudentGameReviewState>;

const formalTemplateState = createReviewStateFromFormalTemplate("beat_guardian_core", {
  label: "最新充能护盾",
  description: "正式注册表中的最新审核模板。",
  default_config: {
    template_id: "beat_guardian_core",
    meter: "3/4",
    bpm: 104,
    runtime_shell: "beat_guardian_shell",
    student_task_copy: {
      listen: "听正式模板的三拍子强拍。",
      do: "在第 1 拍充能。",
      pass: "完成正式模板回合。"
    }
  }
});

assert.equal(formalTemplateState.instance?.template_label, "最新充能护盾");
assert.equal(formalTemplateState.config?.meter, "3/4");
assert.equal(formalTemplateState.config?.bpm, 104);
assert.equal(formalTemplateState.instance?.student_task?.listen, "听什么：听正式模板的三拍子强拍。");

const frontendRoot = dirname(dirname(fileURLToPath(import.meta.url)));
const studentMainSource = readFileSync(join(frontendRoot, "src", "student-main.tsx"), "utf8");
assert.match(studentMainSource, /\/api\/game-templates\//, "审核游戏必须从正式游戏模板接口读取配置");

console.log("student game review preview tests passed");
