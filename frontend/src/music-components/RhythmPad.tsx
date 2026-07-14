import { Button, Text } from "@radix-ui/themes";
import { Drum } from "lucide-react";

type RhythmPadProps = {
  disabled?: boolean;
  onTap: (timestampMs: number) => void;
};

export function RhythmPad({ disabled, onTap }: RhythmPadProps) {
  const triggerTap = () => {
    if (!disabled) onTap(performance.now());
  };

  return (
    <section className="rhythm-pad-wrap" aria-label="虚拟节奏垫">
      <Button
        className="rhythm-pad"
        disabled={disabled}
        onPointerDown={(event) => {
          if (event.button !== 0) return;
          event.preventDefault();
          triggerTap();
        }}
        onKeyDown={(event) => {
          if (event.repeat || (event.key !== " " && event.key !== "Enter")) return;
          event.preventDefault();
          triggerTap();
        }}
        aria-label="敲击节奏垫"
      >
        <Drum size={34} />
        <span>敲击</span>
      </Button>
      <Text as="p" size="1" color="gray">录入阶段可用 · 支持触屏、鼠标、空格和回车</Text>
    </section>
  );
}
