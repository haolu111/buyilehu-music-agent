import { Badge, Button, Container, Flex, Grid, Heading, Text, TextArea } from "@radix-ui/themes";
import { CheckCircle2, ClipboardCheck, RotateCcw, Send, TicketCheck } from "lucide-react";
import { useMemo, useState } from "react";
import {
  buildExitTicketExport,
  buildEvidenceTerms,
  buildExitTicketSentence,
  judgeExitTicket,
  summarizeExitTickets,
  type ExitTicketSubmission
} from "./exitTicketLogic";
import "./primaryActivity.css";

type ExitTicketState = {
  workflow?: {
    education_alignment?: {
      primary_competency?: string;
      music_elements?: string[];
      student_practices?: string[];
    };
  };
  config?: {
    music_focus?: string;
    assessment_criteria?: string[];
    teacher_export_enabled?: boolean;
  };
};

declare global {
  interface Window {
    __EXIT_TICKET_STATE__?: ExitTicketState;
  }
}

const defaultState: ExitTicketState = {
  workflow: {
    education_alignment: {
      primary_competency: "审美感知",
      music_elements: ["评价"],
      student_practices: ["choose", "explain", "assess"]
    }
  },
  config: {
    music_focus: "曲式中的重复、对比和再现",
    assessment_criteria: ["能说出本课音乐要素", "能给出听到的依据"],
    teacher_export_enabled: true
  }
};

export function ExitTicketActivity({ state = window.__EXIT_TICKET_STATE__ ?? defaultState }: { state?: ExitTicketState }) {
  const config = state.config ?? defaultState.config ?? {};
  const alignment = state.workflow?.education_alignment ?? defaultState.workflow?.education_alignment ?? {};
  const focus = config.music_focus || "本课音乐要素";
  const criteria = config.assessment_criteria?.length ? config.assessment_criteria : defaultState.config?.assessment_criteria ?? [];
  const evidenceTerms = useMemo(() => buildEvidenceTerms(criteria, focus), [criteria, focus]);
  const [selectedEvidence, setSelectedEvidence] = useState("");
  const [reason, setReason] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [submissions, setSubmissions] = useState<ExitTicketSubmission[]>([]);
  const result = judgeExitTicket({ focus, selectedEvidence, reason });
  const sentence = buildExitTicketSentence(focus, selectedEvidence, reason);
  const classSummary = useMemo(() => summarizeExitTickets(submissions), [submissions]);
  const exportJson = useMemo(() => buildExitTicketExport(classSummary), [classSummary]);

  const reset = () => {
    setSelectedEvidence("");
    setReason("");
    setSubmitted(false);
  };

  const submitTicket = () => {
    if (result.status !== "ready") return;
    const nextSubmission = {
      focus,
      selectedEvidence,
      reason,
      submittedAt: new Date().toISOString(),
    };
    setSubmissions((current) => [...current, nextSubmission]);
    setSubmitted(true);
  };

  return (
    <main className="primary-activity-shell exit-ticket-shell">
      <Container size="4" px="4">
        <section className="teacher-control-bar">
          <Flex align="center" justify="between" gap="3" wrap="wrap">
            <Flex align="center" gap="2" wrap="wrap">
              <TicketCheck size={18} />
              <Text weight="bold">课堂出口票</Text>
              <Badge color={result.status === "ready" ? "green" : "amber"} variant="soft">
                {result.status === "ready" ? "可提交" : "补音乐依据"}
              </Badge>
              <Badge color="teal" variant="soft">{alignment.primary_competency ?? "审美感知"}</Badge>
            </Flex>
            <Button variant="soft" color="gray" onClick={reset} aria-label="重置出口票">
              <RotateCcw size={17} />
            </Button>
          </Flex>
        </section>

        <Grid columns={{ initial: "1", md: "1.08fr .92fr" }} gap="4" className="activity-stage">
          <section className="activity-board" aria-label="课堂出口票活动">
            <Flex align="center" gap="2" wrap="wrap">
              {(alignment.music_elements ?? []).map((element) => (
                <Badge key={element} color="amber" variant="soft">{element}</Badge>
              ))}
            </Flex>
            <Heading as="h1" size="8" className="activity-title">课堂出口票</Heading>
            <Text as="p" size="3" color="gray" className="activity-subtitle">
              下课前用一个音乐依据词和一句理由，回到本课学习目标。
            </Text>

            <section className="exit-focus-card" aria-label="本课音乐目标">
              <Text size="1" color="gray">本课音乐目标</Text>
              <strong>{focus}</strong>
            </section>

            <section className="primary-tool evidence-panel">
              <Text weight="bold">选择一个音乐依据</Text>
              <div className="evidence-chip-grid">
                {evidenceTerms.map((term) => (
                  <button
                    key={term}
                    type="button"
                    className={selectedEvidence === term ? "active" : ""}
                    onClick={() => {
                      setSelectedEvidence(term);
                      setSubmitted(false);
                    }}
                  >
                    {term}
                  </button>
                ))}
              </div>
            </section>

            <label className="exit-reason-box">
              <Text weight="bold">写一句音乐理由</Text>
              <TextArea
                value={reason}
                onChange={(event) => {
                  setReason(event.target.value);
                  setSubmitted(false);
                }}
                placeholder="例如：A 段主题在最后又回来了。"
                resize="vertical"
              />
            </label>
          </section>

          <aside className="activity-side" aria-label="出口票反馈区">
            <section className={`primary-tool exit-result ${result.status}`}>
              <Flex align="center" gap="2">
                <CheckCircle2 size={20} />
                <Text weight="bold">音乐反馈</Text>
              </Flex>
              <p>{result.feedback}</p>
              <Button highContrast disabled={result.status !== "ready"} onClick={submitTicket}>
                <Send size={18} />
                提交出口票
              </Button>
            </section>

            <section className="primary-tool exit-sentence">
              <Flex align="center" gap="2">
                <ClipboardCheck size={20} />
                <Text weight="bold">学生出口票</Text>
              </Flex>
              <p>{sentence}</p>
              {submitted ? <Text size="2" color="green">已提交：教师可用于下节课复习判断。</Text> : null}
            </section>

            <section className="primary-tool exit-summary">
              <Text weight="bold">班级汇总</Text>
              <p>已记录 {classSummary.total} 张出口票。</p>
              <p>最多依据：{classSummary.topEvidence || "待提交"}</p>
              <p>{classSummary.reviewSuggestion}</p>
              <Text as="p" size="1" color="gray">导出 JSON</Text>
              <pre aria-label="出口票导出 JSON">{exportJson}</pre>
            </section>

            <section className="primary-tool classroom-prompts">
              <Text weight="bold">教师观察点</Text>
              <p>学生是否说到具体音乐要素，而不是只说喜欢或好听。</p>
              <p>出口票结果可作为下节课复听、复唱或小组展示的依据。</p>
            </section>
          </aside>
        </Grid>
      </Container>
    </main>
  );
}
