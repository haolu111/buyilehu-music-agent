import { Badge, Flex, Text } from "@radix-ui/themes";
import { CheckCircle2, TimerReset, XCircle } from "lucide-react";
import type { RhythmTapJudgement, TapTimingJudgement } from "../activity/rhythmWarmupLogic";

type TapFeedbackProps = {
  judgement?: TapTimingJudgement | RhythmTapJudgement;
  score: number;
  tapCount: number;
};

export function TapFeedback({ judgement, score, tapCount }: TapFeedbackProps) {
  const status = judgement?.status ?? "miss";
  const Icon = status === "on_time" || status === "correct"
    ? CheckCircle2
    : status === "early" || status === "late" ? TimerReset : XCircle;
  return (
    <section className={`primary-tool tap-feedback ${status}`} aria-label="敲击反馈">
      <Flex align="center" justify="between" gap="3">
        <Flex align="center" gap="3">
          <span className="feedback-icon"><Icon size={22} /></span>
          <div>
            <Text as="p" size="2" weight="bold">{judgement?.message ?? "等待敲击"}</Text>
            <Text as="p" size="1" color="gray">{tapCount ? `已敲 ${tapCount} 次` : "点击节奏垫开始"}</Text>
          </div>
        </Flex>
        <Badge color={score >= 90 ? "green" : score >= 60 ? "amber" : "gray"} variant="soft">
          {score} 分
        </Badge>
      </Flex>
    </section>
  );
}
