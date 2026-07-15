import { Badge, Button, Flex, Text } from "@radix-ui/themes";
import { RotateCcw, Volume2 } from "lucide-react";

export type FormSectionCard = {
  id: string;
  label: string;
  section: "A" | "B" | "C" | string;
  listened?: boolean;
  placed?: boolean;
};

type FormCardTimelineProps = {
  sections: FormSectionCard[];
  answerPattern?: string[];
  onReplaySection?: (sectionId: string) => void;
  onReset?: () => void;
};

export function FormCardTimeline({ sections, answerPattern = [], onReplaySection, onReset }: FormCardTimelineProps) {
  return (
    <section className="primary-tool form-card-timeline" aria-label="曲式卡时间线">
      <Flex align="center" justify="between" gap="3" className="tool-heading">
        <div>
          <Text as="p" size="2" weight="bold">曲式时间线</Text>
          <Text as="p" size="1" color="gray">每个段落都要能复听再排序</Text>
        </div>
        <Flex gap="2" align="center">
          <Badge color="green" variant="soft">{answerPattern.join("-") || "pattern"}</Badge>
          <Button variant="soft" color="gray" onClick={onReset} aria-label="重置曲式排序">
            <RotateCcw size={16} />
          </Button>
        </Flex>
      </Flex>
      <div className="beat-event-grid">
        {sections.map((section, index) => (
          <div key={section.id} className={`beat-event ${section.placed ? "passed" : ""}`}>
            <span>{index + 1}</span>
            <strong>{section.section}</strong>
            <Button variant="ghost" size="1" onClick={() => onReplaySection?.(section.id)} aria-label={`复听${section.label}`}>
              <Volume2 size={14} />
              {section.label}
            </Button>
          </div>
        ))}
      </div>
    </section>
  );
}
