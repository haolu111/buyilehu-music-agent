import { Badge, Button, Flex, Text } from "@radix-ui/themes";
import { CheckCircle2, ExternalLink, Gamepad2, Hammer, RotateCcw, ShieldCheck } from "lucide-react";
import type { LessonCaseGenerateResult, LessonCaseLoopResult, LessonSegment } from "./activity-store";

type ActivityPlanCardProps = {
  lessonLoop: LessonCaseLoopResult | null;
  generated: LessonCaseGenerateResult | null;
  status: "idle" | "analyzing" | "ready" | "generating" | "generated" | "error";
  onGenerate: () => void;
  onReset: () => void;
  onSelectSegment: (segmentId: string) => void;
  onMarkAsTool: () => void;
};

export function ActivityPlanCard({
  lessonLoop,
  generated,
  status,
  onGenerate,
  onReset,
  onSelectSegment,
  onMarkAsTool,
}: ActivityPlanCardProps) {
  if (!lessonLoop) {
    return (
      <section className="activity-board plan-card-panel" aria-label="闭环等待">
        <Badge color="gray" variant="soft">等待教案</Badge>
        <h2>先分析教案</h2>
        <p className="quiet-copy">系统会列出可游戏化环节，并说明游戏设计来自教案哪里。</p>
      </section>
    );
  }

  const selected = lessonLoop.lesson_case.segments.find(
    (segment) => segment.segment_id === lessonLoop.selected_segment.segment_id,
  );
  const brief = lessonLoop.segment_game_brief;
  const qaStatus = generated?.qa_report?.status || "";
  const groundingStatus = generated?.lesson_segment_grounding_result?.status || "";

  return (
    <section className="plan-card-panel" aria-label="教案到游戏闭环卡片">
      <section className="activity-board">
        <Flex align="center" justify="between" gap="3" wrap="wrap">
          <div>
            <Badge color="green" variant="soft">
              <CheckCircle2 size={14} />
              教案环节选择
            </Badge>
            <h2>{selected?.stage || "已选环节"}</h2>
          </div>
          <Button type="button" variant="soft" color="gray" onClick={onReset}>
            <RotateCcw size={16} />
            重选
          </Button>
          <Button type="button" variant="soft" color="gray" onClick={onMarkAsTool}>
            <Hammer size={16} />
            改成课堂工具
          </Button>
        </Flex>
        <PlanSection title="教案依据" value={lessonLoop.selected_segment.source_evidence} />
        <PlanSection title="音乐目标" value={lessonLoop.selected_segment.must_preserve.teaching_goal} />
        <PlanList title="音乐材料" items={[lessonLoop.selected_segment.must_preserve.music_material]} />
        <PlanList title="学生行为" items={lessonLoop.selected_segment.must_preserve.student_behaviors} />
        <PlanSection title="为什么适合游戏化" value={lessonLoop.selected_segment.selection_reason} />
        <CandidateList
          segments={lessonLoop.lesson_case.segments}
          selectedId={lessonLoop.selected_segment.segment_id}
          disabled={status === "analyzing" || status === "generating"}
          onSelectSegment={onSelectSegment}
        />
      </section>

      <section className="activity-board">
        <Badge color="amber" variant="soft">
          <Gamepad2 size={14} />
          游戏设计
        </Badge>
        <h2>{brief.music_learning_target}</h2>
        <PlanSection title="游戏目标" value={brief.game_goal} />
        <PlanList title="学生会做什么" items={brief.student_actions} />
        <PlanSection title="核心玩法" value={brief.core_mechanic} />
        <PlanSection title="成功条件" value={brief.success_condition} />
        <PlanList title="错误反馈" items={brief.error_feedback.map((item) => item.feedback)} />
        <PlanSection title="课堂回扣" value={brief.classroom_return} />
        <Flex gap="2" wrap="wrap" className="plan-actions">
          <Button highContrast type="button" onClick={onGenerate} disabled={status === "generating"}>
            <Gamepad2 size={17} />
            {status === "generating" ? "生成中" : "生成游戏"}
          </Button>
        </Flex>
      </section>

      <section className="activity-board">
        <Badge color={generated ? "green" : "gray"} variant="soft">
          <ShieldCheck size={14} />
          生成结果与 QA
        </Badge>
        <h2>{generated ? "作品已保存" : "等待生成"}</h2>
        {generated ? (
          <>
            <PlanList title="自动验收" items={[`游戏 QA：${qaStatus}`, `教案依据：${groundingStatus}`]} />
            <PlanList title="作品包文件" items={generated.artifact.files.slice(0, 6)} />
            <Flex gap="2" wrap="wrap" className="plan-actions">
              <Button asChild highContrast>
                <a href={generated.page_url} target="_blank" rel="noreferrer">
                  <ExternalLink size={17} />
                  打开学生端
                </a>
              </Button>
              <Button asChild variant="soft" color="gray">
                <a href={generated.teacher_url} target="_blank" rel="noreferrer">
                  <ExternalLink size={17} />
                  打开教师端
                </a>
              </Button>
            </Flex>
          </>
        ) : (
          <p className="quiet-copy">生成后会显示学生端、教师端、QA 结果和作品包。</p>
        )}
      </section>
    </section>
  );
}

function PlanSection({ title, value }: { title: string; value: string }) {
  return (
    <div className="plan-row">
      <Text size="1" color="gray">{title}</Text>
      <p>{value || "待确认"}</p>
    </div>
  );
}

function PlanList({ title, items, empty = "待确认" }: { title: string; items: string[]; empty?: string }) {
  const visibleItems = items.filter(Boolean).length ? items.filter(Boolean) : [empty];
  return (
    <div className="plan-row">
      <Text size="1" color="gray">{title}</Text>
      <div className="plan-chip-list">
        {visibleItems.map((item) => (
          <span key={item}>{item}</span>
        ))}
      </div>
    </div>
  );
}

function CandidateList({
  segments,
  selectedId,
  disabled,
  onSelectSegment,
}: {
  segments: LessonSegment[];
  selectedId: string;
  disabled: boolean;
  onSelectSegment: (segmentId: string) => void;
}) {
  return (
    <div className="lesson-candidate-list" aria-label="可选教案环节">
      {segments.map((segment) => (
        <div key={segment.segment_id} className={segment.segment_id === selectedId ? "selected" : ""}>
          <strong>{segment.stage}</strong>
          <span>{segment.digital_potential === "high" ? "适合游戏化" : "更适合作为课堂辅助"}</span>
          <Button
            type="button"
            size="1"
            variant={segment.segment_id === selectedId ? "solid" : "soft"}
            color={segment.segment_id === selectedId ? "green" : "gray"}
            disabled={disabled || segment.segment_id === selectedId}
            onClick={() => onSelectSegment(segment.segment_id)}
          >
            <CheckCircle2 size={14} />
            {segment.segment_id === selectedId ? "已选环节" : "选择此环节"}
          </Button>
        </div>
      ))}
    </div>
  );
}
