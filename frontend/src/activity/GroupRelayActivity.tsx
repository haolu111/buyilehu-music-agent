import { Badge, Button, Container, Flex, Grid, Heading, Text } from "@radix-ui/themes";
import { CheckCircle2, Ear, Hand, RotateCcw, Send, Users, Volume2 } from "lucide-react";
import { useMemo, useState } from "react";
import { playPlayableInstrumentSequence } from "../shared/realAudio";
import {
  buildGroupRelayRounds,
  judgeGroupRelay,
  markGroupPerformed,
  submitGroupAssessment,
  updateRelayEvidence
} from "./groupRelayLogic";
import "./primaryActivity.css";

type GroupRelayState = {
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
    rhythm_pattern?: string[];
    meter?: string;
  };
};

declare global {
  interface Window {
    __GROUP_RELAY_STATE__?: GroupRelayState;
  }
}

const defaultState: GroupRelayState = {
  workflow: {
    education_alignment: {
      primary_competency: "艺术表现",
      music_elements: ["节奏", "休止", "合作"],
      student_practices: ["tap", "listen", "cooperate", "assess", "perform"]
    }
  },
  config: {
    group_tasks: ["A组拍第一小节", "B组接第二小节", "C组做休止动作"],
    assessment_criteria: ["节奏稳定", "能听同伴", "休止能停住"],
    rhythm_pattern: ["quarter", "quarter", "rest", "quarter"],
    meter: "2/4"
  }
};

export function GroupRelayActivity({ state = window.__GROUP_RELAY_STATE__ ?? defaultState }: { state?: GroupRelayState }) {
  const config = state.config ?? defaultState.config ?? {};
  const alignment = state.workflow?.education_alignment ?? defaultState.workflow?.education_alignment ?? {};
  const tasks = config.group_tasks?.length ? config.group_tasks : defaultState.config?.group_tasks ?? [];
  const criteria = config.assessment_criteria?.length ? config.assessment_criteria : defaultState.config?.assessment_criteria ?? [];
  const rhythm = config.rhythm_pattern?.length ? config.rhythm_pattern : defaultState.config?.rhythm_pattern ?? [];
  const initialRounds = useMemo(() => buildGroupRelayRounds(tasks), [tasks]);
  const [rounds, setRounds] = useState(initialRounds);
  const result = judgeGroupRelay(rounds);
  const activeIndex = rounds.findIndex((round) => round.status === "active" || round.status === "performed");

  const reset = () => setRounds(initialRounds);
  const playCue = () => {
    const offsets = rhythm.map((item, index) => item === "rest" ? -5 : index % 2 === 0 ? 0 : 7);
    playPlayableInstrumentSequence(offsets.length ? offsets : [0, 0, -5, 7], {
      instrument: "woodblock",
      gap: 0.36,
      duration: 0.14,
      gain: 0.54,
      baseMidi: 60,
      oscillatorWave: "square"
    });
  };

  return (
    <main className="primary-activity-shell group-relay-shell">
      <Container size="4" px="4">
        <section className="teacher-control-bar" aria-label="小组接力控制条">
          <Flex align="center" justify="between" gap="3" wrap="wrap">
            <Flex align="center" gap="2" wrap="wrap">
              <Users size={18} />
              <Text weight="bold">小组接力展示</Text>
              <Badge color={result.status === "ready" ? "green" : "amber"} variant="soft">
                {result.status === "ready" ? "接力完成" : "先听同伴"}
              </Badge>
              <Badge color="teal" variant="soft">{config.meter ?? "2/4"}</Badge>
            </Flex>
            <Flex gap="2" wrap="wrap">
              <Button highContrast onClick={playCue} aria-label="播放接力提示节奏">
                <Volume2 size={17} />
                提示节奏
              </Button>
              <Button variant="soft" color="gray" onClick={reset} aria-label="重置小组接力">
                <RotateCcw size={17} />
              </Button>
            </Flex>
          </Flex>
        </section>

        <Grid columns={{ initial: "1", md: "1.08fr .92fr" }} gap="4" className="activity-stage">
          <section className="activity-board" aria-label="小组接力活动">
            <Flex align="center" gap="2" wrap="wrap">
              <Badge color="green" variant="soft">{alignment.primary_competency ?? "艺术表现"}</Badge>
              {(alignment.music_elements ?? []).map((element) => (
                <Badge key={element} color="amber" variant="soft">{element}</Badge>
              ))}
            </Flex>
            <Heading as="h1" size="8" className="activity-title">小组接力展示</Heading>
            <Text as="p" size="3" color="gray" className="activity-subtitle">
              每组先听同伴，再接上自己的节奏、休止或动作任务；评价必须说出音乐依据。
            </Text>

            <Grid columns={{ initial: "1", sm: "3" }} gap="3" className="group-relay-list">
              {rounds.map((round, index) => (
                <section key={`${round.groupName}-${index}`} className={`group-relay-card ${round.status}`}>
                  <Flex align="center" justify="between" gap="2">
                    <Badge color={round.status === "assessed" ? "green" : round.status === "active" ? "amber" : "gray"} variant="soft">
                      {statusLabel(round.status)}
                    </Badge>
                    <span className="relay-step">{index + 1}</span>
                  </Flex>
                  <strong>{round.task}</strong>
                  <p>{round.status === "waiting" ? "先听同伴表现，等轮到本组再进入。" : "听稳定拍，完成本组接力任务。"}</p>
                  <Button
                    highContrast={round.status === "active"}
                    variant={round.status === "active" ? "solid" : "soft"}
                    disabled={round.status !== "active"}
                    onClick={() => setRounds((current) => markGroupPerformed(current, index))}
                  >
                    <Hand size={17} />
                    完成展示
                  </Button>
                </section>
              ))}
            </Grid>
          </section>

          <aside className="activity-side" aria-label="接力评价区">
            <section className="primary-tool relay-evidence-box">
              <Flex align="center" gap="2">
                <Ear size={19} />
                <Text weight="bold">音乐依据</Text>
              </Flex>
              <Text as="p" size="2" color="gray">不能只说好听或喜欢，要说节奏、休止、进入、速度或同伴倾听。</Text>
              <div className="criteria-chip-grid">
                {criteria.map((criterion) => (
                  <button
                    key={criterion}
                    type="button"
                    disabled={activeIndex < 0 || rounds[activeIndex]?.status !== "performed"}
                    onClick={() => setRounds((current) => updateRelayEvidence(current, activeIndex, criterion))}
                  >
                    {criterion}
                  </button>
                ))}
              </div>
              <textarea
                aria-label="填写小组接力音乐依据"
                value={activeIndex >= 0 ? rounds[activeIndex]?.evidence ?? "" : ""}
                disabled={activeIndex < 0 || rounds[activeIndex]?.status !== "performed"}
                placeholder="例如：节奏稳定，休止能停住，进入整齐。"
                onChange={(event) => setRounds((current) => updateRelayEvidence(current, activeIndex, event.target.value))}
              />
              <Button
                highContrast
                disabled={activeIndex < 0 || rounds[activeIndex]?.status !== "performed"}
                onClick={() => setRounds((current) => submitGroupAssessment(current, activeIndex))}
              >
                <Send size={17} />
                提交评价
              </Button>
            </section>

            <section className={`primary-tool relay-result ${result.status}`}>
              <Flex align="center" gap="2">
                <CheckCircle2 size={20} />
                <Text weight="bold">接力反馈</Text>
              </Flex>
              <p>{result.feedback}</p>
            </section>

            <section className="primary-tool classroom-prompts">
              <Text weight="bold">教师观察点</Text>
              <p>学生是否能先听同伴，再按轮次进入。</p>
              <p>评价是否指向节奏稳定、休止停住、进入整齐或合作倾听。</p>
              <p>小组展示结束后，把各组任务连起来回到歌曲或节奏片段中表现。</p>
            </section>
          </aside>
        </Grid>
      </Container>
    </main>
  );
}

function statusLabel(status: string) {
  const labels: Record<string, string> = {
    waiting: "等待",
    active: "本组进入",
    performed: "待评价",
    assessed: "已评价"
  };
  return labels[status] ?? "接力";
}
