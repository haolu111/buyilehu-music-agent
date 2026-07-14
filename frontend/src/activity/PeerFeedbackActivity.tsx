import { Badge, Button, Container, Flex, Grid, Heading, Text } from "@radix-ui/themes";
import { CheckCircle2, ClipboardCheck, Ear, RotateCcw, Send, Users } from "lucide-react";
import { useMemo, useState } from "react";
import {
  buildPeerFeedbackRecord,
  buildPeerFeedbackShowcases,
  evaluatePeerFeedback,
  submitPeerFeedback,
  updatePeerFeedbackEvidence,
  updatePeerFeedbackSuggestion
} from "./peerFeedbackLogic";
import "./primaryActivity.css";

type PeerFeedbackState = {
  workflow?: {
    education_alignment?: {
      primary_competency?: string;
      music_elements?: string[];
      student_practices?: string[];
    };
  };
  config?: {
    group_tasks?: string[];
    assessment_criteria?: string[];
    evidence_terms?: string[];
    music_focus?: string;
  };
};

declare global {
  interface Window {
    __PEER_FEEDBACK_STATE__?: PeerFeedbackState;
  }
}

const defaultState: PeerFeedbackState = {
  workflow: {
    education_alignment: {
      primary_competency: "审美感知",
      music_elements: ["评价", "表现", "合作"],
      student_practices: ["listen", "perform", "assess", "explain"]
    }
  },
  config: {
    group_tasks: ["A组展示节奏创编", "B组展示身体打击", "C组展示五声短句"],
    assessment_criteria: ["节奏稳定", "进入整齐", "能听同伴"],
    evidence_terms: ["节奏稳定", "进入整齐", "力度有变化", "能听同伴"],
    music_focus: "小组音乐展示"
  }
};

export function PeerFeedbackActivity({ state = window.__PEER_FEEDBACK_STATE__ ?? defaultState }: { state?: PeerFeedbackState }) {
  const config = state.config ?? defaultState.config ?? {};
  const alignment = state.workflow?.education_alignment ?? defaultState.workflow?.education_alignment ?? {};
  const groupTasks = config.group_tasks?.length ? config.group_tasks : defaultState.config?.group_tasks ?? [];
  const criteria = config.assessment_criteria?.length ? config.assessment_criteria : defaultState.config?.assessment_criteria ?? [];
  const evidenceTerms = config.evidence_terms?.length ? config.evidence_terms : criteria;
  const initialShowcases = useMemo(() => buildPeerFeedbackShowcases(groupTasks, criteria), [criteria, groupTasks]);
  const [showcases, setShowcases] = useState(initialShowcases);
  const activeIndex = showcases.findIndex((showcase) => showcase.status === "active");
  const activeShowcase = activeIndex >= 0 ? showcases[activeIndex] : undefined;
  const evaluation = evaluatePeerFeedback(showcases);
  const record = buildPeerFeedbackRecord(showcases);

  const reset = () => setShowcases(initialShowcases);

  return (
    <main className="primary-activity-shell peer-feedback-shell">
      <Container size="4" px="4">
        <section className="teacher-control-bar" aria-label="展示评价控制条">
          <Flex align="center" justify="between" gap="3" wrap="wrap">
            <Flex align="center" gap="2" wrap="wrap">
              <ClipboardCheck size={18} />
              <Text weight="bold">展示与同伴评价</Text>
              <Badge color={evaluation.status === "ready" ? "green" : "amber"} variant="soft">
                {evaluation.status === "ready" ? "可汇总" : "先听展示"}
              </Badge>
              <Badge color="teal" variant="soft">{config.music_focus ?? "小组音乐展示"}</Badge>
            </Flex>
            <Button variant="soft" color="gray" onClick={reset} aria-label="重置展示评价">
              <RotateCcw size={17} />
            </Button>
          </Flex>
        </section>

        <Grid columns={{ initial: "1", md: "1.08fr .92fr" }} gap="4" className="activity-stage">
          <section className="activity-board peer-feedback-board" aria-label="展示与同伴评价活动">
            <Flex align="center" gap="2" wrap="wrap">
              <Badge color="green" variant="soft">{alignment.primary_competency ?? "审美感知"}</Badge>
              {(alignment.music_elements ?? []).map((element) => (
                <Badge key={element} color="amber" variant="soft">{element}</Badge>
              ))}
            </Flex>
            <Heading as="h1" size="8" className="activity-title">展示与同伴评价</Heading>
            <Text as="p" size="3" color="gray" className="activity-subtitle">
              先听完整展示，再选择音乐依据，最后写一句能帮助下一轮改进的建议。
            </Text>

            <Grid columns={{ initial: "1", sm: "3" }} gap="3" className="peer-showcase-list">
              {showcases.map((showcase, index) => (
                <section key={showcase.id} className={`peer-showcase-card ${showcase.status}`}>
                  <Flex align="center" justify="between" gap="2">
                    <Badge color={showcase.status === "reviewed" ? "green" : showcase.status === "active" ? "amber" : "gray"} variant="soft">
                      {statusLabel(showcase.status)}
                    </Badge>
                    <span className="relay-step">{index + 1}</span>
                  </Flex>
                  <strong>{showcase.task}</strong>
                  <p>{showcase.status === "waiting" ? "先听前面小组展示，准备评价。" : "请同伴先听完整展示，再评价。"}</p>
                  {showcase.evidenceTerms.length > 0 && <small>依据：{showcase.evidenceTerms.join("、")}</small>}
                </section>
              ))}
            </Grid>
          </section>

          <aside className="activity-side" aria-label="同伴评价区">
            <section className="primary-tool peer-feedback-panel">
              <Flex align="center" gap="2">
                <Ear size={19} />
                <Text weight="bold">同伴建议</Text>
              </Flex>
              <p>{activeShowcase ? `正在评价：${activeShowcase.task}` : "所有小组都已完成评价。"}</p>
              <div className="criteria-chip-grid">
                {evidenceTerms.map((term) => (
                  <button
                    key={term}
                    type="button"
                    disabled={!activeShowcase}
                    className={activeShowcase?.evidenceTerms.includes(term) ? "selected" : ""}
                    onClick={() => setShowcases((current) => updatePeerFeedbackEvidence(current, activeIndex, term))}
                  >
                    {term}
                  </button>
                ))}
              </div>
              <textarea
                aria-label="填写同伴评价建议"
                value={activeShowcase?.suggestion ?? ""}
                disabled={!activeShowcase}
                placeholder="例如：节奏稳定，如果休止处停得更整齐会更好。"
                onChange={(event) => setShowcases((current) => updatePeerFeedbackSuggestion(current, activeIndex, event.target.value))}
              />
              <Button
                highContrast
                disabled={!activeShowcase}
                onClick={() => setShowcases((current) => submitPeerFeedback(current, activeIndex))}
              >
                <Send size={17} />
                提交同伴评价
              </Button>
            </section>

            <section className={`primary-tool peer-feedback-result ${evaluation.status}`}>
              <Flex align="center" gap="2">
                <CheckCircle2 size={20} />
                <Text weight="bold">评价反馈</Text>
              </Flex>
              <p>{evaluation.feedback}</p>
              <p>{evaluation.teacherSuggestion}</p>
            </section>

            <section className="primary-tool peer-feedback-record">
              <Text weight="bold">展示评价记录</Text>
              <pre aria-label="展示评价记录导出 JSON">{JSON.stringify(record, null, 2)}</pre>
            </section>

            <section className="primary-tool classroom-prompts">
              <Flex align="center" gap="2">
                <Users size={18} />
                <Text weight="bold">教师观察点</Text>
              </Flex>
              <p>学生是否先听完整展示，再评价。</p>
              <p>不能只说好听或喜欢，要说出一个音乐依据。</p>
              <p>建议是否具体指向节奏、进入、力度、声音或合作倾听。</p>
              <p>下一轮展示能否根据同伴建议修改一个音乐点。</p>
            </section>
          </aside>
        </Grid>
      </Container>
    </main>
  );
}

function statusLabel(status: string) {
  const labels: Record<string, string> = {
    waiting: "等待展示",
    active: "正在评价",
    reviewed: "已评价"
  };
  return labels[status] ?? "展示";
}
