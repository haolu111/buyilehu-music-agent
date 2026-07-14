import { Badge, Button, Flex, Text } from "@radix-ui/themes";
import { Eye, MessageCircleQuestion } from "lucide-react";

export type PicturePromptCard = {
  id: string;
  label: string;
  prompt: string;
  imageUrl?: string;
  selected?: boolean;
};

type PicturePromptCardsProps = {
  cards: PicturePromptCard[];
  listened: boolean;
  onSelect?: (cardId: string) => void;
};

export function PicturePromptCards({ cards, listened, onSelect }: PicturePromptCardsProps) {
  return (
    <section className="primary-tool picture-prompt-cards" aria-label="画面提示卡">
      <Flex align="center" justify="between" gap="3" className="tool-heading">
        <div>
          <Text as="p" size="2" weight="bold">感受/画面卡</Text>
          <Text as="p" size="1" color="gray">课堂导入先听音乐，再选画面或问题</Text>
        </div>
        <Badge color={listened ? "green" : "amber"} variant="soft">{listened ? "已听" : "先听"}</Badge>
      </Flex>
      <div className="rhythm-card-grid">
        {cards.map((card) => (
          <Button
            key={card.id}
            className={`rhythm-card ${card.selected ? "active" : ""}`}
            disabled={!listened}
            variant={card.selected ? "solid" : "surface"}
            highContrast={card.selected}
            onClick={() => onSelect?.(card.id)}
            aria-pressed={card.selected}
          >
            <span className="rhythm-card-symbol">{card.imageUrl ? <img src={card.imageUrl} alt="" /> : <Eye size={24} />}</span>
            <span className="rhythm-card-meta">
              <MessageCircleQuestion size={15} />
              {card.label}
            </span>
            <span className="rhythm-card-meta">{card.prompt}</span>
          </Button>
        ))}
      </div>
    </section>
  );
}
