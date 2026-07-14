import React from "react";
import ReactDOM from "react-dom/client";
import { Button, Flex, Slider, Text, Theme } from "@radix-ui/themes";
import "@radix-ui/themes/styles.css";
import { Eye, FastForward, Gauge, Pause, RotateCcw, Save, StepBack, Users } from "lucide-react";
import { ActivityPlanCard } from "./activity/ActivityPlanCard";
import { ActivityWizard } from "./activity/ActivityWizard";
import { StudentActivityShell } from "./activity/StudentActivityShell";
import { TeacherHome } from "./activity/TeacherHome";
import {
  classroomControlActions,
  useActivityWorkbenchStore,
  workManagementActions,
  type ClassroomControlAction,
} from "./activity/activity-store";
import "./activity/primaryActivity.css";

const controlLabels: Record<ClassroomControlAction, string> = {
  pause: "暂停",
  reset: "重置",
  tempo: "调速",
  difficulty_down: "降低难度",
  difficulty_up: "提高难度",
  hint_visibility: "显示/隐藏提示",
  phrase_focus: "只练某一句或某一关",
  mode_switch: "个人/小组/全班",
  instrument_voice: "换乐器或声部",
  regenerate_plan_card: "重新生成方案卡",
  continue_editing: "继续修改当前作品",
};

const controlIcons: Partial<Record<ClassroomControlAction, typeof Pause>> = {
  pause: Pause,
  reset: RotateCcw,
  tempo: Gauge,
  difficulty_down: StepBack,
  difficulty_up: FastForward,
  mode_switch: Users,
  regenerate_plan_card: Eye,
  continue_editing: Save,
};

const managementLabels: Record<(typeof workManagementActions)[number], string> = {
  preview: "预览",
  continue_edit: "继续修改",
  duplicate: "复制为新作品",
  download_package: "下载作品包",
  save_as_template: "复用为个人模板",
  last_classroom_config: "查看上次课堂配置",
};

function TeacherActivityWorkbench() {
  const state = useActivityWorkbenchStore();
  const generated = state.generatedLessonGame;
  const currentTitle = generated?.segment_game_brief?.music_learning_target || state.lessonLoop?.segment_game_brief?.music_learning_target || "教案闭环游戏";

  const analyzeLesson = async () => {
    state.setLoopStatus("analyzing");
    state.setLoopError("");
    state.setGeneratedLessonGame(null);
    try {
      const response = await fetch("/api/lesson/case/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ lesson_text: state.lessonText })
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || "教案分析失败");
      state.setLessonLoop(payload);
      state.setLoopStatus("ready");
    } catch (error) {
      state.setLoopError(error instanceof Error ? error.message : "教案分析失败");
      state.setLoopStatus("error");
    }
  };

  const generateGame = async () => {
    if (!state.lessonLoop) return;
    state.setLoopStatus("generating");
    state.setLoopError("");
    try {
      const response = await fetch("/api/lesson/case/generate-game", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lesson_case: state.lessonLoop.lesson_case,
          selected_segment: state.lessonLoop.selected_segment,
          segment_game_brief: state.lessonLoop.segment_game_brief
        })
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || "游戏生成失败");
      state.setGeneratedLessonGame(payload);
      state.setLoopStatus("generated");
    } catch (error) {
      state.setLoopError(error instanceof Error ? error.message : "游戏生成失败");
      state.setLoopStatus("error");
    }
  };

  const selectSegment = async (segmentId: string) => {
    if (!state.lessonLoop || segmentId === state.lessonLoop.selected_segment.segment_id) return;
    state.setLoopStatus("analyzing");
    state.setLoopError("");
    state.setGeneratedLessonGame(null);
    try {
      const selectResponse = await fetch("/api/lesson/case/select-segment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lesson_case: state.lessonLoop.lesson_case,
          segment_id: segmentId
        })
      });
      const selectedPayload = await selectResponse.json();
      if (!selectResponse.ok) throw new Error(selectedPayload.error || "环节选择失败");

      const translateResponse = await fetch("/api/lesson/case/translate-segment-game", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          lesson_case: state.lessonLoop.lesson_case,
          selected_segment: selectedPayload.selected_segment
        })
      });
      const translatedPayload = await translateResponse.json();
      if (!translateResponse.ok) throw new Error(translatedPayload.error || "游戏设计生成失败");

      state.setLessonLoop({
        lesson_case: state.lessonLoop.lesson_case,
        selected_segment: selectedPayload.selected_segment,
        segment_game_brief: translatedPayload.segment_game_brief,
        candidate_segments: state.lessonLoop.candidate_segments || state.lessonLoop.lesson_case.segments
      });
      state.setLoopStatus("ready");
    } catch (error) {
      state.setLoopError(error instanceof Error ? error.message : "环节选择失败");
      state.setLoopStatus("error");
    }
  };

  const markAsTool = () => {
    state.setMode("direct");
    state.setGeneratedLessonGame(null);
    state.setLoopStatus("ready");
  };

  const resetLoop = () => {
    state.setLessonLoop(null);
    state.setGeneratedLessonGame(null);
    state.setLoopStatus("idle");
    state.setLoopError("");
  };

  return (
    <main className="primary-activity-shell teacher-workbench-shell">
      <div className="teacher-workbench-layout">
        <TeacherHome mode={state.mode} onModeChange={state.setMode} />

        <div className="teacher-workbench-main">
          <ActivityWizard
            mode={state.mode}
            lessonText={state.lessonText}
            status={state.loopStatus}
            error={state.loopError}
            lessonLoop={state.lessonLoop}
            onLessonTextChange={state.setLessonText}
            onAnalyze={analyzeLesson}
          />
          <ActivityPlanCard
            lessonLoop={state.lessonLoop}
            generated={generated}
            status={state.loopStatus}
            onGenerate={generateGame}
            onReset={resetLoop}
            onSelectSegment={selectSegment}
            onMarkAsTool={markAsTool}
          />
        </div>

        <aside className="teacher-live-console" aria-label="教师控制台">
          <section className="activity-board">
            <div className="panel-heading">
              <Text size="2" weight="bold">教师控制台</Text>
              <Text size="1" color="gray">课堂中可调速、重置、只练选中环节，并隐藏或显示提示。</Text>
            </div>
            <label className="tempo-control">
              <Text size="1" color="gray">速度 {state.bpm} BPM</Text>
              <Slider value={[state.bpm]} min={72} max={124} step={4} onValueChange={() => state.applyControl("tempo")} />
            </label>
            <div className="console-state-grid">
              <span>提示：{state.showHint ? "显示" : "隐藏"}</span>
              <span>练习：{state.focus}</span>
              <span>模式：{state.classMode}</span>
              <span>状态：{state.paused ? "暂停" : "进行"}</span>
            </div>
            <div className="console-action-grid">
              {classroomControlActions.map((action) => {
                const Icon = controlIcons[action] || Gauge;
                return (
                  <Button key={action} type="button" variant="soft" color="gray" onClick={() => state.applyControl(action)}>
                    <Icon size={15} />
                    {controlLabels[action]}
                  </Button>
                );
              })}
            </div>
          </section>

          <StudentActivityShell
            title={currentTitle}
            currentTask={generated?.segment_game_brief?.game_goal || state.lessonLoop?.selected_segment?.source_evidence || "等待教案分析"}
            bpm={state.bpm}
            showHint={state.showHint}
            paused={state.paused}
            focus={state.focus}
          />

          <section className="activity-board work-management-panel" aria-label="作品管理">
            <Text size="2" weight="bold">作品管理</Text>
            <Flex gap="2" wrap="wrap">
              {workManagementActions.map((action) => (
                <Button key={action} variant="soft" color="gray">
                  {managementLabels[action]}
                </Button>
              ))}
            </Flex>
          </section>
        </aside>
      </div>
    </main>
  );
}

ReactDOM.createRoot(document.getElementById("teacher-activity-root") as HTMLElement).render(
  <React.StrictMode>
    <Theme accentColor="teal" grayColor="sage" radius="medium" scaling="100%">
      <TeacherActivityWorkbench />
    </Theme>
  </React.StrictMode>,
);
