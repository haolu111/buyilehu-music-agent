import { Badge, Button, Flex, Text } from "@radix-ui/themes";
import { CheckCircle2, ClipboardCheck, RotateCcw } from "lucide-react";

export type RubricCriterion = {
  id: string;
  label: string;
  evidence: string;
  met?: boolean;
};

type RubricPanelProps = {
  criteria: RubricCriterion[];
  title?: string;
  onToggleCriterion?: (criterionId: string) => void;
  onReset?: () => void;
};

export function RubricPanel({ criteria, title = "音乐表现证据", onToggleCriterion, onReset }: RubricPanelProps) {
  const metCount = criteria.filter((criterion) => criterion.met).length;
  return (
    <section className="primary-tool rubric-panel" aria-label="评价量规">
      <Flex align="center" justify="between" gap="3" className="tool-heading">
        <Flex align="center" gap="2">
          <ClipboardCheck size={18} />
          <div>
            <Text as="p" size="2" weight="bold">{title}</Text>
            <Text as="p" size="1" color="gray">奖励和记录必须绑定音乐表现证据</Text>
          </div>
        </Flex>
        <Badge color={metCount === criteria.length && criteria.length ? "green" : "amber"} variant="soft">
          {metCount}/{criteria.length}
        </Badge>
      </Flex>
      <div className="kit-list">
        {criteria.map((criterion) => (
          <Button
            key={criterion.id}
            variant={criterion.met ? "solid" : "surface"}
            highContrast={criterion.met}
            onClick={() => onToggleCriterion?.(criterion.id)}
            aria-pressed={criterion.met}
          >
            <CheckCircle2 size={16} />
            {criterion.label}: {criterion.evidence}
          </Button>
        ))}
      </div>
      <Flex justify="end" mt="3">
        <Button variant="soft" color="gray" onClick={onReset} aria-label="重置评价">
          <RotateCcw size={17} />
        </Button>
      </Flex>
    </section>
  );
}
