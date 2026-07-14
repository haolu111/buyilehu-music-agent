import { Button, Flex, Text } from "@radix-ui/themes";
import { CheckCircle2, HelpCircle, Play, RotateCcw, Volume2 } from "lucide-react";

type StudentActivityShellProps = {
  title: string;
  currentTask: string;
  bpm: number;
  showHint: boolean;
  paused: boolean;
  focus: string;
};

export function StudentActivityShell({ title, currentTask, bpm, showHint, paused, focus }: StudentActivityShellProps) {
  return (
    <section className="student-shell-preview" aria-label="学生活动外壳">
      <div className="student-shell-header">
        <Text size="1" color="gray">活动标题</Text>
        <h2>{title}</h2>
      </div>

      <div className="student-current-task">
        <Text size="1" color="gray">当前任务</Text>
        <strong>{currentTask}</strong>
      </div>

      <Flex gap="2" wrap="wrap" className="student-playback-row">
        <Button size="3" highContrast disabled={paused}>
          <Play size={18} />
          播放
        </Button>
        <Button size="3" variant="soft" color="gray">
          <Volume2 size={18} />
          重听
        </Button>
        <Button size="3" variant="soft" color="gray">
          <RotateCcw size={18} />
          再来一次
        </Button>
      </Flex>

      <div className="student-operation-zone" aria-label="操作区">
        <button type="button">强</button>
        <button type="button">弱</button>
        <button type="button">拍</button>
      </div>

      <div className="student-feedback-zone">
        <CheckCircle2 size={22} />
        <span>即时反馈：{paused ? "教师已暂停" : showHint ? `跟着提示，速度 ${bpm} BPM` : `隐藏提示，练习 ${focus}`}</span>
      </div>

      <div className="student-complete-zone">
        <Text size="1" color="gray">完成状态</Text>
        <span>{paused ? "等待教师继续" : "进行中"}</span>
      </div>

      <div className="student-return-question">
        <HelpCircle size={19} />
        <span>课堂回扣问题：刚才的强弱在歌曲哪一句里最明显？</span>
      </div>
    </section>
  );
}
