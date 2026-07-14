import { Badge, Button, Container, Flex, Grid, Heading, Text } from "@radix-ui/themes";
import { CheckCircle2, Hand, RotateCcw, Volume2 } from "lucide-react";
import { useMemo, useState } from "react";
import { playPlayableInstrumentSequence } from "../shared/realAudio";
import {
  actionSyllable,
  buildBodyPercussionSlots,
  judgeBodyPercussion,
  updateBodyAction
} from "./bodyPercussionLogic";
import "./primaryActivity.css";

type BodyPercussionState = {
  workflow?: {
    education_alignment?: {
      primary_competency?: string;
      music_elements?: string[];
      student_practices?: string[];
    };
  };
  config?: {
    body_actions?: string[];
    rhythm_pattern?: string[];
    meter?: string;
    bpm?: number;
  };
};

declare global {
  interface Window {
    __BODY_PERCUSSION_STATE__?: BodyPercussionState;
  }
}

const defaultState: BodyPercussionState = {
  workflow: {
    education_alignment: {
      primary_competency: "创意实践",
      music_elements: ["节奏", "节拍", "力度"],
      student_practices: ["move", "tap", "arrange", "create", "perform"]
    }
  },
  config: {
    body_actions: ["拍手", "拍腿", "跺脚", "停住"],
    rhythm_pattern: ["quarter", "eighth_pair", "rest", "quarter"],
    meter: "2/4",
    bpm: 92
  }
};

export function BodyPercussionActivity({ state = window.__BODY_PERCUSSION_STATE__ ?? defaultState }: { state?: BodyPercussionState }) {
  const config = state.config ?? defaultState.config ?? {};
  const alignment = state.workflow?.education_alignment ?? defaultState.workflow?.education_alignment ?? {};
  const actions = config.body_actions?.length ? config.body_actions : defaultState.config?.body_actions ?? [];
  const rhythm = config.rhythm_pattern?.length ? config.rhythm_pattern : defaultState.config?.rhythm_pattern ?? [];
  const initialSlots = useMemo(() => buildBodyPercussionSlots(rhythm, actions), [actions, rhythm]);
  const [slots, setSlots] = useState(initialSlots);
  const result = judgeBodyPercussion(slots);

  const reset = () => setSlots(initialSlots);
  const playPattern = () => {
    playPlayableInstrumentSequence(
      slots.map((slot) => (slot.action === "停住" ? -5 : slot.action.includes("跺") ? 0 : slot.action.includes("腿") ? 4 : 7)),
      {
        instrument: "woodblock",
        gap: 0.24,
        duration: 0.12,
        gain: 0.56,
        baseMidi: 60,
        oscillatorWave: "triangle"
      }
    );
  };

  return (
    <main className="primary-activity-shell body-percussion-shell">
      <Container size="4" px="4">
        <section className="teacher-control-bar">
          <Flex align="center" justify="between" gap="3" wrap="wrap">
            <Flex align="center" gap="2" wrap="wrap">
              <Hand size={18} />
              <Text weight="bold">身体打击编排</Text>
              <Badge color={result.status === "ready" ? "green" : "amber"} variant="soft">
                {result.status === "ready" ? "可展示" : "检查休止"}
              </Badge>
              <Badge color="teal" variant="soft">{config.meter ?? "2/4"} · {config.bpm ?? 92} BPM</Badge>
            </Flex>
            <Flex gap="2" wrap="wrap">
              <Button highContrast onClick={playPattern} aria-label="播放身体打击编排">
                <Volume2 size={17} />
                播放
              </Button>
              <Button variant="soft" color="gray" onClick={reset} aria-label="重置身体打击">
                <RotateCcw size={17} />
              </Button>
            </Flex>
          </Flex>
        </section>

        <Grid columns={{ initial: "1", md: "1.08fr .92fr" }} gap="4" className="activity-stage">
          <section className="activity-board" aria-label="身体打击编排活动">
            <Flex align="center" gap="2" wrap="wrap">
              {(alignment.music_elements ?? []).map((element) => (
                <Badge key={element} color="amber" variant="soft">{element}</Badge>
              ))}
            </Flex>
            <Heading as="h1" size="8" className="activity-title">身体打击编排</Heading>
            <Text as="p" size="3" color="gray" className="activity-subtitle">
              把拍手、拍腿、跺脚和停住放进拍点里，休止也要用身体表现出来。
            </Text>

            <Grid columns={{ initial: "1", sm: "2" }} gap="3" className="body-slot-grid">
              {slots.map((slot) => (
                <section
                  key={slot.beatIndex}
                  className={`body-slot ${slot.rhythm === "rest" ? "rest" : ""}`}
                  data-body-beat={slot.beatIndex}
                  data-body-rhythm={slot.rhythm}
                >
                  <Text size="1" color="gray">第 {slot.beatIndex} 拍 · {rhythmLabel(slot.rhythm)}</Text>
                  <strong>{actionSyllable(slot.action)}</strong>
                  <div className="body-action-row">
                    {actions.map((action) => (
                      <button
                        key={action}
                        type="button"
                        className={slot.action === action ? "active" : ""}
                        data-body-action={action}
                        onClick={() => setSlots((current) => updateBodyAction(current, slot.beatIndex, action))}
                      >
                        {action}
                      </button>
                    ))}
                  </div>
                </section>
              ))}
            </Grid>
          </section>

          <aside className="activity-side" aria-label="身体打击反馈区">
            <section className={`primary-tool body-result ${result.status}`}>
              <Flex align="center" gap="2">
                <CheckCircle2 size={20} />
                <Text weight="bold">音乐反馈</Text>
              </Flex>
              <p>{result.feedback}</p>
              <Button highContrast disabled={result.status !== "ready"}>
                <CheckCircle2 size={18} />
                提交展示
              </Button>
            </section>

            <section className="primary-tool classroom-prompts">
              <Text weight="bold">教师观察点</Text>
              <p>学生是否能让动作落在拍点上，而不是只做舞蹈动作。</p>
              <p>遇到休止时是否真正停住，理解停住也是音乐表现。</p>
            </section>
          </aside>
        </Grid>
      </Container>
    </main>
  );
}

function rhythmLabel(rhythm: string) {
  if (rhythm === "eighth_pair") return "八分音符组";
  if (rhythm === "rest") return "休止";
  if (rhythm === "half") return "二分音符";
  return "四分音符";
}
