import { Badge, Button, Flex, Text } from "@radix-ui/themes";
import { Pause, Play, Repeat, Shuffle } from "lucide-react";

export type ComparePlayerClip = {
  id: string;
  label: string;
  description?: string;
  listened?: boolean;
};

type ComparePlayerProps = {
  clips: ComparePlayerClip[];
  activeClipId?: string;
  playing?: boolean;
  evidencePrompt?: string;
  onSelectClip?: (clipId: string) => void;
  onTogglePlay?: (clipId: string) => void;
  onReplay?: (clipId: string) => void;
};

export function ComparePlayer({
  clips,
  activeClipId,
  playing = false,
  evidencePrompt = "听完 A/B 后，说出速度、力度、旋律或音色依据。",
  onSelectClip,
  onTogglePlay,
  onReplay
}: ComparePlayerProps) {
  const activeClip = clips.find((clip) => clip.id === activeClipId) ?? clips[0];
  return (
    <section className="primary-tool compare-player" aria-label="对比聆听播放器">
      <Flex align="center" justify="between" gap="3" wrap="wrap">
        <div>
          <Text as="p" size="2" weight="bold">对比聆听</Text>
          <Text as="p" size="1" color="gray">{evidencePrompt}</Text>
        </div>
        <Badge color={clips.every((clip) => clip.listened) ? "green" : "amber"} variant="soft">
          {clips.filter((clip) => clip.listened).length}/{clips.length} 已听
        </Badge>
      </Flex>
      <Flex gap="2" wrap="wrap" mt="3">
        {clips.map((clip) => {
          const selected = clip.id === activeClip?.id;
          return (
            <Button
              key={clip.id}
              variant={selected ? "solid" : "surface"}
              highContrast={selected}
              onClick={() => onSelectClip?.(clip.id)}
              aria-pressed={selected}
            >
              <Shuffle size={16} />
              {clip.label}
            </Button>
          );
        })}
      </Flex>
      <Flex align="center" justify="between" gap="3" mt="3" wrap="wrap">
        <Text size="2">{activeClip?.description ?? "选择一个片段开始复听。"}</Text>
        <Flex gap="2">
          <Button
            variant="soft"
            highContrast
            disabled={!activeClip}
            onClick={() => activeClip && onReplay?.(activeClip.id)}
            aria-label="复听当前片段"
          >
            <Repeat size={17} />
          </Button>
          <Button
            highContrast
            disabled={!activeClip}
            onClick={() => activeClip && onTogglePlay?.(activeClip.id)}
            aria-label={playing ? "暂停当前片段" : "播放当前片段"}
          >
            {playing ? <Pause size={17} /> : <Play size={17} />}
            {playing ? "暂停" : "播放"}
          </Button>
        </Flex>
      </Flex>
    </section>
  );
}
