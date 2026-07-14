import { Badge, Button, Flex, Text } from "@radix-ui/themes";
import { Ear, Mic2 } from "lucide-react";

export type SolfegeCard = {
  id: string;
  syllable: string;
  handSign?: string;
  heard?: boolean;
  selected?: boolean;
};

type SolfegeCardBankProps = {
  cards: SolfegeCard[];
  mode?: "listen" | "sing_back" | "order";
  onSelect?: (cardId: string) => void;
};

export function SolfegeCardBank({ cards, mode = "listen", onSelect }: SolfegeCardBankProps) {
  return (
    <section className="primary-tool solfege-card-bank" aria-label="唱名卡仓库">
      <Flex align="center" justify="between" gap="3" className="tool-heading">
        <div>
          <Text as="p" size="2" weight="bold">唱名卡</Text>
          <Text as="p" size="1" color="gray">先听辨，再唱回或排序</Text>
        </div>
        <Badge color={mode === "sing_back" ? "green" : "amber"} variant="soft">{mode}</Badge>
      </Flex>
      <div className="rhythm-card-grid">
        {cards.map((card) => (
          <Button
            key={card.id}
            className={`rhythm-card ${card.selected ? "active" : ""}`}
            variant={card.selected ? "solid" : "surface"}
            highContrast={card.selected}
            onClick={() => onSelect?.(card.id)}
            aria-pressed={card.selected}
            aria-label={`${card.syllable} 唱名卡`}
          >
            <span className="rhythm-card-symbol">{card.syllable}</span>
            <span className="rhythm-card-meta">
              {card.heard ? <Mic2 size={15} /> : <Ear size={15} />}
              {card.handSign ?? "听辨"}
            </span>
          </Button>
        ))}
      </div>
    </section>
  );
}
