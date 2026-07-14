import { Button, Flex, Text } from "@radix-ui/themes";
import { Pause, Play, Volume2 } from "lucide-react";

type AudioPlayerProps = {
  playing: boolean;
  bpm: number;
  onToggle: () => void;
  onPreviewPulse: () => void;
  actionLabel?: string;
  activeLabel?: string;
  statusText?: string;
  disabled?: boolean;
};

export function AudioPlayer({
  playing,
  bpm,
  onToggle,
  onPreviewPulse,
  actionLabel = "播放",
  activeLabel = "取消",
  statusText,
  disabled = false
}: AudioPlayerProps) {
  return (
    <section className="primary-tool audio-player" aria-label="节拍播放器">
      <Flex align="center" justify="between" gap="3">
        <div>
          <Text as="p" size="2" weight="bold">节拍播放器</Text>
          <Text as="p" size="1" color="gray">{statusText || `${bpm} BPM`}</Text>
        </div>
        <Flex gap="2">
          <Button size="3" variant="soft" highContrast onClick={onPreviewPulse} aria-label="试听一拍" disabled={disabled}>
            <Volume2 size={18} />
          </Button>
          <Button size="3" highContrast onClick={onToggle} aria-label={playing ? activeLabel : actionLabel} disabled={disabled}>
            {playing ? <Pause size={18} /> : <Play size={18} />}
            {playing ? activeLabel : actionLabel}
          </Button>
        </Flex>
      </Flex>
    </section>
  );
}
