import type { ReactNode } from "react";

const labels: Record<string, string> = {
  answer: "回答",
  assessment: "评价",
  attempts: "尝试次数",
  bpm: "速度",
  choice: "选择结果",
  completed: "是否完成",
  completedSteps: "已完成步骤",
  confidence: "可信度",
  createdAt: "创建时间",
  duration: "时长",
  durationSeconds: "时长（秒）",
  evidence: "判断依据",
  explanation: "说明",
  feedback: "反馈",
  focus: "学习重点",
  matches: "配对结果",
  notes: "说明",
  order: "排列顺序",
  reason: "理由",
  result: "活动结果",
  role: "角色",
  score: "得分",
  selectedEvidence: "所选依据",
  sequence: "排列结果",
  status: "状态",
  studentName: "学生姓名",
  submissions: "提交记录",
  submittedAt: "提交时间",
  summary: "汇总",
  title: "名称",
  total: "总数",
  trace: "旋律轨迹",
}

const values: Record<string, string> = {
  true: "是",
  false: "否",
  completed: "已完成",
  correct: "正确",
  incorrect: "需要调整",
  pending: "等待处理",
  ready: "可以提交",
}

function labelFor(key: string) {
  return labels[key] || (/[\u3400-\u9fff]/.test(key) ? key : "活动信息")
}

function scalar(value: unknown) {
  if (value == null || value === "") return "暂无";
  const text = String(value);
  return values[text.toLowerCase()] || text;
}

function renderValue(value: unknown, path: string): ReactNode {
  if (Array.isArray(value)) {
    if (!value.length) return <span>暂无</span>;
    return <ol>{value.map((item, index) => <li key={`${path}-${index}`}>{renderValue(item, `${path}-${index}`)}</li>)}</ol>;
  }
  if (value && typeof value === "object") {
    return (
      <dl className="readable-data-list">
        {Object.entries(value as Record<string, unknown>).map(([key, item]) => (
          <div key={`${path}-${key}`}>
            <dt>{labelFor(key)}</dt>
            <dd>{renderValue(item, `${path}-${key}`)}</dd>
          </div>
        ))}
      </dl>
    );
  }
  return <span>{scalar(value)}</span>;
}

export function ReadableData({ value }: { value: unknown }) {
  let parsed = value;
  if (typeof value === "string") {
    try {
      parsed = JSON.parse(value);
    } catch {
      parsed = value;
    }
  }
  return <div className="readable-data">{renderValue(parsed, "root")}</div>;
}
