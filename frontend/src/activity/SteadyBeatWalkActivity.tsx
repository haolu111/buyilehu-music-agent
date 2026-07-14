import { Badge, Button, Container, Flex, Grid, Heading, Text } from "@radix-ui/themes";
import { CheckCircle2, Footprints, RotateCcw, Volume2 } from "lucide-react";
import { useMemo, useState } from "react";
import { playPlayableInstrumentSequence } from "../shared/realAudio";
import {
  buildSteadyBeatWalkPlan,
  buildSteadyBeatWalkRecord,
  evaluateSteadyBeatWalk,
  judgeSteadyBeatAction,
  steadyBeatToneOffset,
  type SteadyBeatWalkJudgement
} from "./steadyBeatWalkLogic";
import "./primaryActivity.css";

type SteadyBeatWalkState = {
  workflow?: {
    education_alignment?: {
      primary_competency?: string;
      music_elements?: string[];
      student_practices?: string[];
    };
  };
  config?: {
    meter?: string;
    bpm?: number;
    rhythm_pattern?: string[];
    movement_actions?: string[];
  };
};

declare global {
  interface Window {
    __STEADY_BEAT_WALK_STATE__?: SteadyBeatWalkState;
  }
}

const defaultState: SteadyBeatWalkState = {
  workflow: {
    education_alignment: {
      primary_competency: "艺术表现",
      music_elements: ["稳定拍", "节奏", "休止"],
      student_practices: ["listen", "move", "tap", "perform"]
    }
  },
  config: {
    meter: "2/4",
    bpm: 84,
    rhythm_pattern: ["quarter", "quarter", "rest", "quarter"],
    movement_actions: ["走一步", "拍手", "停住"],
  }
};

export function SteadyBeatWalkActivity({ state = window.__STEADY_BEAT_WALK_STATE__ ?? defaultState }: { state?: SteadyBeatWalkState }) {
  const config = state.config ?? defaultState.config ?? {};
  const alignment = state.workflow?.education_alignment ?? defaultState.workflow?.education_alignment ?? {};
  const plan = useMemo(() => buildSteadyBeatWalkPlan({
    meter: config.meter,
    bpm: config.bpm,
    rhythmPattern: config.rhythm_pattern,
    movementActions: config.movement_actions,
  }), [config.bpm, config.meter, config.movement_actions, config.rhythm_pattern]);
  const [hasListenedBeat, setHasListenedBeat] = useState(false);
  const [activeIndex, setActiveIndex] = useState(0);
  const [judgements, setJudgements] = useState<SteadyBeatWalkJudgement[]>([]);
  const activeStep = plan.beats[activeIndex] ?? plan.beats[0];
  const evaluation = evaluateSteadyBeatWalk(plan, { hasListenedBeat, judgements });
  const record = buildSteadyBeatWalkRecord(plan, { hasListenedBeat, judgements });
  const latest = judgements[judgements.length - 1];

  const playBeat = () => {
    setHasListenedBeat(true);
    playPlayableInstrumentSequence(plan.beats.map((step) => steadyBeatToneOffset(step)), {
      instrument: "woodblock",
      gap: 60 / plan.bpm,
      duration: 0.14,
      gain: 0.58,
      baseMidi: 60,
      oscillatorWave: "square"
    });
  };

  const chooseAction = (action: string) => {
    const judgement = judgeSteadyBeatAction(activeStep, action);
    setJudgements((current) => [...current, judgement]);
    setActiveIndex((index) => (index + 1) % plan.beats.length);
    if (!activeStep.isRest) {
      playPlayableInstrumentSequence([steadyBeatToneOffset(activeStep)], {
        instrument: action.includes("拍") ? "woodblock" : "xylophone",
        gap: 0.16,
        duration: 0.12,
        gain: 0.56,
        baseMidi: 60,
        oscillatorWave: "triangle"
      });
    }
  };

  const reset = () => {
    setHasListenedBeat(false);
    setActiveIndex(0);
    setJudgements([]);
  };

  return (
    <main className="primary-activity-shell steady-walk-shell">
      <Container size="4" px="4">
        <section className="teacher-control-bar">
          <Flex align="center" justify="between" gap="3" wrap="wrap">
            <Flex align="center" gap="2" wrap="wrap">
              <Footprints size={18} />
              <Text weight="bold">稳定拍行走控制</Text>
              <Badge color={evaluation.status === "ready" ? "green" : "amber"} variant="soft">
                {evaluation.status === "ready" ? "可围圈行走" : "先听稳定拍"}
              </Badge>
              <Badge color="teal" variant="soft">{plan.meter} · {plan.bpm} BPM</Badge>
            </Flex>
            <Flex gap="2" wrap="wrap">
              <Button highContrast onClick={playBeat} aria-label="播放稳定拍行走">
                <Volume2 size={17} />
                播放稳定拍
              </Button>
              <Button variant="soft" color="gray" onClick={reset} aria-label="重置稳定拍行走">
                <RotateCcw size={17} />
              </Button>
            </Flex>
          </Flex>
        </section>

        <Grid columns={{ initial: "1", md: "1.08fr .92fr" }} gap="4" className="activity-stage">
          <section className="activity-board steady-walk-board" aria-label="稳定拍行走活动">
            <Flex align="center" gap="2" wrap="wrap">
              <Badge color="green" variant="soft">{alignment.primary_competency ?? "艺术表现"}</Badge>
              {(alignment.music_elements ?? []).map((element) => <Badge key={element} color="amber" variant="soft">{element}</Badge>)}
            </Flex>
            <Heading as="h1" size="8" className="activity-title">稳定拍行走</Heading>
            <Text as="p" size="3" color="gray" className="activity-subtitle">
              先听稳定拍，再用走一步、拍手、停住把拍点和休止表现出来。
            </Text>

            <div className="steady-walk-track" aria-label="稳定拍行走轨道">
              {plan.beats.map((step, index) => (
                <div key={step.id} className={`steady-walk-step ${step.isRest ? "rest" : "move"} ${index === activeIndex ? "active" : ""}`}>
                  <span>第 {index + 1} 拍</span>
                  <strong>{step.label}</strong>
                  <small>{step.expectedAction}</small>
                </div>
              ))}
            </div>
          </section>

          <aside className="activity-side" aria-label="稳定拍行走操作区">
            <section className="primary-tool steady-walk-action-panel">
              <Flex align="center" gap="2">
                <Footprints size={20} />
                <Text weight="bold">当前动作</Text>
              </Flex>
              <p>当前是第 {activeStep.index + 1} 拍：{activeStep.isRest ? "休止，请停住" : "跟稳定拍动起来"}。</p>
              <Grid columns="1" gap="2">
                {plan.movementActions.map((action) => (
                  <button key={action} type="button" onClick={() => chooseAction(action)}>
                    {action}
                  </button>
                ))}
              </Grid>
            </section>

            <section className={`primary-tool steady-walk-feedback ${evaluation.status}`}>
              <Flex align="center" gap="2">
                <CheckCircle2 size={20} />
                <Text weight="bold">稳定拍检查</Text>
              </Flex>
              <p>{latest?.feedback ?? "先听稳定拍，再记录走、拍、停。"}</p>
              <div className="steady-walk-summary-grid">
                <span>已记录</span>
                <strong>{judgements.length} 次</strong>
                <span>正确</span>
                <strong>{evaluation.correctCount} 次</strong>
                <span>稳定度</span>
                <strong>{evaluation.accuracy} 分</strong>
              </div>
              <p>{evaluation.teacherSuggestion}</p>
            </section>

            <section className="primary-tool steady-walk-record">
              <Text weight="bold">行走记录</Text>
              <pre aria-label="稳定拍行走记录导出 JSON">{JSON.stringify(record, null, 2)}</pre>
            </section>
          </aside>
        </Grid>
      </Container>
    </main>
  );
}
