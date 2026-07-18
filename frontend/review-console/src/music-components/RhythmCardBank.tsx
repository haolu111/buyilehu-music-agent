import { Badge, Button, Flex, Text } from "@radix-ui/themes";
import { Hand } from "lucide-react";
import type { RhythmCard } from "../activity/rhythmWarmupLogic";
import { RhythmNotation } from "./RhythmNotation";

type RhythmCardBankProps = {
  cards: RhythmCard[];
  activeCardId?: string;
  onSelect?: (cardId: string) => void;
};

export function RhythmCardBank({ cards, activeCardId, onSelect }: RhythmCardBankProps) {
  return (
    <section className="primary-tool rhythm-card-bank" aria-label="节奏卡片">
      <Flex align="center" justify="between" gap="3" className="tool-heading">
        <div>
          <Text as="p" size="2" weight="bold">节奏卡片</Text>
          <Text as="p" size="1" color="gray">可投屏，可替代实体节奏卡</Text>
        </div>
        <Badge color="amber" variant="soft">节奏卡片</Badge>
      </Flex>
      <div className="rhythm-card-grid">
        {cards.map((card, index) => (
          <Button
            key={`${card.id}-${index}`}
            className={`rhythm-card ${activeCardId === card.id ? "active" : ""}`}
            style={{ "--card-color": card.color } as React.CSSProperties}
            variant={activeCardId === card.id ? "solid" : "surface"}
            highContrast={activeCardId === card.id}
            onClick={() => onSelect?.(card.id)}
            aria-pressed={onSelect ? activeCardId === card.id : undefined}
            aria-label={`${card.label} ${card.syllable}`}
          >
            <span className="rhythm-card-symbol">
              <RhythmNotation rhythm={card.patternId} label={card.label} />
            </span>
            <span className="rhythm-card-meta">
              <Hand size={15} />
              {card.gesture}
            </span>
          </Button>
        ))}
      </div>
    </section>
  );
}
