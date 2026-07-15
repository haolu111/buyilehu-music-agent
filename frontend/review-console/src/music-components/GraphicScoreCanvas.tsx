import { Badge, Button, Flex, Text } from "@radix-ui/themes";
import { Eraser, Play, Save } from "lucide-react";

export type GraphicScoreSymbol = {
  id: string;
  shape: "dot" | "line" | "wave" | "block" | string;
  meaning: string;
  x: number;
  y: number;
};

type GraphicScoreCanvasProps = {
  symbols: GraphicScoreSymbol[];
  playbackReady?: boolean;
  onPlay?: () => void;
  onClear?: () => void;
  onSave?: () => void;
};

export function GraphicScoreCanvas({ symbols, playbackReady = false, onPlay, onClear, onSave }: GraphicScoreCanvasProps) {
  return (
    <section className="primary-tool graphic-score-canvas" aria-label="图形谱画布">
      <Flex align="center" justify="between" gap="3" className="tool-heading">
        <div>
          <Text as="p" size="2" weight="bold">图形谱</Text>
          <Text as="p" size="1" color="gray">图形必须有声音意义，并可回放修改</Text>
        </div>
        <Badge color={playbackReady ? "green" : "amber"} variant="soft">{playbackReady ? "可回放" : "待绑定声音"}</Badge>
      </Flex>
      <div className="graphic-score-surface" role="img" aria-label="学生图形谱">
        {symbols.map((symbol) => (
          <span
            key={symbol.id}
            className={`score-symbol ${symbol.shape}`}
            style={{ left: `${symbol.x}%`, top: `${symbol.y}%` }}
            title={symbol.meaning}
          />
        ))}
      </div>
      <Flex gap="2" mt="3" wrap="wrap">
        <Button highContrast disabled={!playbackReady} onClick={onPlay} aria-label="回放图形谱">
          <Play size={17} />
          回放
        </Button>
        <Button variant="soft" color="gray" onClick={onClear} aria-label="清空图形谱">
          <Eraser size={17} />
        </Button>
        <Button variant="soft" color="green" onClick={onSave} aria-label="保存图形谱记录">
          <Save size={17} />
        </Button>
      </Flex>
    </section>
  );
}
