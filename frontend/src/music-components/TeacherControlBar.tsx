import { Button, Flex, Select, Slider, Text } from "@radix-ui/themes";
import { RotateCcw, SlidersHorizontal } from "lucide-react";
import type { PrimaryMeter } from "../activity/rhythmWarmupLogic";
import type { GradePreset, PracticeMode } from "../activity/rhythmWarmupLogic";

type TeacherControlBarProps = {
  bpm: number;
  meter: PrimaryMeter;
  repeatCount: number;
  gradePreset?: GradePreset;
  practiceMode?: PracticeMode;
  onBpmChange: (bpm: number) => void;
  onMeterChange: (meter: PrimaryMeter) => void;
  onRepeatChange: (repeatCount: number) => void;
  onGradePresetChange?: (gradePreset: GradePreset) => void;
  onPracticeModeChange?: (practiceMode: PracticeMode) => void;
  onReset: () => void;
};

export function TeacherControlBar({
  bpm,
  meter,
  repeatCount,
  gradePreset,
  practiceMode,
  onBpmChange,
  onMeterChange,
  onRepeatChange,
  onGradePresetChange,
  onPracticeModeChange,
  onReset
}: TeacherControlBarProps) {
  return (
    <section className="teacher-control-bar" aria-label="教师控制条">
      <Flex align="center" justify="between" gap="3" wrap="wrap">
        <Flex align="center" gap="2">
          <SlidersHorizontal size={18} />
          <Text size="2" weight="bold">教师控制</Text>
        </Flex>
        <Flex align="center" gap="3" wrap="wrap">
          <label className="compact-control">
            <Text size="1" color="gray">速度</Text>
            <Slider value={[bpm]} min={72} max={124} step={4} onValueChange={(value) => onBpmChange(value[0] ?? bpm)} />
            <Text size="1" weight="bold">{bpm}</Text>
          </label>
          <label className="compact-select">
            <Text size="1" color="gray">拍号</Text>
            <Select.Root value={meter} onValueChange={(value) => onMeterChange(value as PrimaryMeter)}>
              <Select.Trigger aria-label="选择拍号" />
              <Select.Content>
                <Select.Item value="2/4">2/4</Select.Item>
                <Select.Item value="3/4">3/4</Select.Item>
                <Select.Item value="4/4">4/4</Select.Item>
              </Select.Content>
            </Select.Root>
          </label>
          {gradePreset && onGradePresetChange ? (
            <label className="compact-select">
              <Text size="1" color="gray">年级</Text>
              <Select.Root value={gradePreset} onValueChange={(value) => onGradePresetChange(value as GradePreset)}>
                <Select.Trigger aria-label="选择年级判定标准" />
                <Select.Content>
                  <Select.Item value="lower_primary">小学低段</Select.Item>
                  <Select.Item value="middle_primary">小学中段</Select.Item>
                  <Select.Item value="upper_primary">小学高段</Select.Item>
                </Select.Content>
              </Select.Root>
            </label>
          ) : null}
          {practiceMode && onPracticeModeChange ? (
            <label className="compact-select">
              <Text size="1" color="gray">模式</Text>
              <Select.Root value={practiceMode} onValueChange={(value) => onPracticeModeChange(value as PracticeMode)}>
                <Select.Trigger aria-label="选择节奏练习模式" />
                <Select.Content>
                  <Select.Item value="play_along">跟拍</Select.Item>
                  <Select.Item value="echo">听后回拍</Select.Item>
                </Select.Content>
              </Select.Root>
            </label>
          ) : null}
          <label className="compact-select">
            <Text size="1" color="gray">遍数</Text>
            <Select.Root value={String(repeatCount)} onValueChange={(value) => onRepeatChange(Number(value))}>
              <Select.Trigger aria-label="选择重复遍数" />
              <Select.Content>
                <Select.Item value="1">1</Select.Item>
                <Select.Item value="2">2</Select.Item>
                <Select.Item value="3">3</Select.Item>
              </Select.Content>
            </Select.Root>
          </label>
          <Button variant="soft" color="gray" onClick={onReset} aria-label="重置活动">
            <RotateCcw size={17} />
          </Button>
        </Flex>
      </Flex>
    </section>
  );
}
