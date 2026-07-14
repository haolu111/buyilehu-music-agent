import { Badge, Button, Flex, Text } from "@radix-ui/themes";
import { Boxes, FileUp, Gamepad2, Hammer, Library, Music2, PenLine, Repeat2, Sparkles, Users } from "lucide-react";
import type { GenerationMode } from "./activity-store";

type TeacherHomeProps = {
  mode: GenerationMode;
  onModeChange: (mode: GenerationMode) => void;
};

const teacherTasks = [
  { label: "上传教案生成活动", icon: FileUp },
  { label: "直接生成活动/游戏/工具", icon: Sparkles },
  { label: "生成虚拟教具", icon: Hammer },
  { label: "生成虚拟乐器", icon: Music2 },
  { label: "生成课堂小游戏", icon: Gamepad2 },
  { label: "生成欣赏课互动", icon: Library },
  { label: "生成学唱练习", icon: PenLine },
  { label: "生成小组合作活动", icon: Users },
  { label: "修改已有作品", icon: Repeat2 },
];

export function TeacherHome({ mode, onModeChange }: TeacherHomeProps) {
  return (
    <section className="teacher-home" aria-label="教师首页">
      <Flex align="center" justify="between" gap="3" wrap="wrap" className="teacher-home-head">
        <div>
          <Badge color="teal" variant="soft">
            <Boxes size={14} />
            双端活动生成
          </Badge>
          <h1>音乐课堂工作台</h1>
          <Text as="p" color="gray">
            从教案或直接需求出发，先确认方案，再生成学生端和教师端。
          </Text>
        </div>
      </Flex>

      <div className="entry-mode-grid" aria-label="双入口模式">
        <button className={mode === "lesson_upload" ? "active" : ""} type="button" onClick={() => onModeChange("lesson_upload")}>
          <FileUp size={22} />
          <strong>上传教案生成</strong>
          <span>根据你的教案环节和材料生成活动链</span>
        </button>
        <button className={mode === "direct" ? "active" : ""} type="button" onClick={() => onModeChange("direct")}>
          <Sparkles size={22} />
          <strong>直接生成活动/游戏/工具</strong>
          <span>根据你的直接需求快速生成活动、游戏或工具</span>
        </button>
      </div>

      {mode === "direct" ? (
        <p className="direct-mode-note">
          未上传教案时，系统会使用你的直接需求和默认练习材料生成。如果需要贴合具体课例，请上传教案、音频或谱例。
        </p>
      ) : (
        <p className="direct-mode-note">上传教案后，系统会优先选择适合数字化的课堂环节，不会强行改造讲解、示范或讨论。</p>
      )}

      <div className="teacher-task-grid" aria-label="教师能做什么">
        {teacherTasks.map((task) => {
          const Icon = task.icon;
          return (
            <Button key={task.label} type="button" variant="soft" color="gray" className="teacher-task-button">
              <Icon size={17} />
              {task.label}
            </Button>
          );
        })}
      </div>
    </section>
  );
}
