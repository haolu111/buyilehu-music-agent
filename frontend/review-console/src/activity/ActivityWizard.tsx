import { Button, Text, TextArea } from "@radix-ui/themes";
import { FileSearch, Wand2 } from "lucide-react";
import type { GenerationMode, LessonCaseLoopResult } from "./activity-store";

type ActivityWizardProps = {
  mode: GenerationMode;
  lessonText: string;
  status: "idle" | "analyzing" | "ready" | "generating" | "generated" | "error";
  error: string;
  onLessonTextChange: (value: string) => void;
  onAnalyze: () => void;
  lessonLoop: LessonCaseLoopResult | null;
};

export function ActivityWizard({
  mode,
  lessonText,
  status,
  error,
  onLessonTextChange,
  onAnalyze,
  lessonLoop,
}: ActivityWizardProps) {
  return (
    <section className="activity-board wizard-panel" aria-label="教案闭环向导">
      <div className="panel-heading">
        <Text size="2" weight="bold">教案输入</Text>
        <Text size="1" color="gray">粘贴教案后，系统先找适合游戏化的课堂环节，再给出游戏设计。</Text>
      </div>

      <label className="teacher-request-box">
        <Text size="2" weight="bold">教案正文</Text>
        <TextArea
          value={lessonText}
          onChange={(event) => onLessonTextChange(event.target.value)}
          resize="vertical"
          rows={9}
          disabled={mode !== "lesson_upload"}
        />
      </label>

      <div className="lesson-action-row">
        <Button type="button" highContrast onClick={onAnalyze} disabled={status === "analyzing" || mode !== "lesson_upload"}>
          <FileSearch size={17} />
          {status === "analyzing" ? "分析中" : "分析教案"}
        </Button>
        {lessonLoop ? (
          <span>
            <Wand2 size={15} />
            已找到 {lessonLoop.lesson_case.segments.length} 个课堂环节
          </span>
        ) : null}
      </div>

      {error ? <p className="loop-error">{error}</p> : null}
    </section>
  );
}
