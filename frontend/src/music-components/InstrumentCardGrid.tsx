import { Badge, Button, Flex, Text } from "@radix-ui/themes";
import { Ear, ImageOff, Music2 } from "lucide-react";

export type InstrumentCard = {
  id: string;
  name: string;
  family: string;
  audioReady?: boolean;
  photoSource?: "real_photo" | "icon" | "generated_reference";
  selected?: boolean;
};

type InstrumentCardGridProps = {
  instruments: InstrumentCard[];
  onSelect?: (instrumentId: string) => void;
  onPreviewAudio?: (instrumentId: string) => void;
};

export function InstrumentCardGrid({ instruments, onSelect, onPreviewAudio }: InstrumentCardGridProps) {
  return (
    <section className="primary-tool instrument-card-grid" aria-label="乐器卡片网格">
      <Flex align="center" justify="between" gap="3" className="tool-heading">
        <div>
          <Text as="p" size="2" weight="bold">乐器家族</Text>
          <Text as="p" size="1" color="gray">音色判断必须来自音频样本</Text>
        </div>
        <Badge color="blue" variant="soft">instrument_audio_pack</Badge>
      </Flex>
      <div className="rhythm-card-grid">
        {instruments.map((instrument) => (
          <Button
            key={instrument.id}
            className={`rhythm-card ${instrument.selected ? "active" : ""}`}
            variant={instrument.selected ? "solid" : "surface"}
            highContrast={instrument.selected}
            onClick={() => onSelect?.(instrument.id)}
            aria-pressed={instrument.selected}
          >
            <span className="rhythm-card-symbol">{instrument.name}</span>
            <span className="rhythm-card-meta">
              {instrument.audioReady ? <Music2 size={15} /> : <ImageOff size={15} />}
              {instrument.family}
            </span>
            <span className="rhythm-card-meta">
              <Ear size={15} />
              <span onClick={(event) => {
                event.stopPropagation();
                onPreviewAudio?.(instrument.id);
              }}>试听</span>
            </span>
          </Button>
        ))}
      </div>
    </section>
  );
}
