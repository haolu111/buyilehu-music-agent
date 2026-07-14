import { Badge, Button, Container, Flex, Grid, Heading, Text } from "@radix-ui/themes";
import { CheckCircle2, Eye, ListMusic, RotateCcw, Volume2 } from "lucide-react";
import { useMemo, useState } from "react";
import { RhythmNotation } from "../music-components/RhythmNotation";
import { playPlayableInstrumentSequence } from "../shared/realAudio";
import { buildSimpleScorePlan } from "./simpleScoreLogic";
import "./primaryActivity.css";

type SimpleScoreState = {
  workflow?: {
    education_alignment?: {
      primary_competency?: string;
      music_elements?: string[];
      student_practices?: string[];
    };
  };
  config?: {
    numbered_score?: string[];
    solfege_lines?: string[][];
    rhythm_pattern?: string[];
    audio_clip?: string;
    meter?: string;
    bpm?: number;
    teacher_confirm_required?: boolean;
    show_solfege?: boolean;
  };
};

declare global {
  interface Window {
    __SIMPLE_SCORE_STATE__?: SimpleScoreState;
  }
}

const defaultState: SimpleScoreState = {
  workflow: {
    education_alignment: {
      primary_competency: "艺术表现",
      music_elements: ["识谱", "唱名", "节奏", "旋律"],
      student_practices: ["listen", "read", "sing", "explain"]
    }
  },
  config: {
    numbered_score: ["1 2 3", "3 5 6"],
    rhythm_pattern: ["quarter", "quarter", "half"],
    meter: "2/4",
    bpm: 84,
    teacher_confirm_required: true,
    show_solfege: true
  }
};

const SOLFEGE_OFFSETS: Record<string, number> = { do: 0, re: 2, mi: 4, fa: 5, sol: 7, la: 9, ti: 11 };

export function SimpleScoreFollowingActivity({ state = window.__SIMPLE_SCORE_STATE__ ?? defaultState }: { state?: SimpleScoreState }) {
  const config = state.config ?? defaultState.config ?? {};
  const plan = useMemo(() => buildSimpleScorePlan({
    numberedScore: config.numbered_score,
    rhythmPattern: config.rhythm_pattern,
    bpm: config.bpm
  }), [config.bpm, config.numbered_score, config.rhythm_pattern]);
  const alignment = state.workflow?.education_alignment ?? defaultState.workflow?.education_alignment ?? {};
  const [activeIndex, setActiveIndex] = useState(0);
  const [hasListened, setHasListened] = useState(false);
  const [confirmed, setConfirmed] = useState<boolean[]>(() => plan.lines.map(() => false));
  const activeLine = plan.lines[activeIndex] ?? plan.lines[0];
  const completedCount = confirmed.filter(Boolean).length;
  const progressText = `${completedCount}/${plan.lines.length || 1}`;
  const allConfirmed = completedCount === plan.lines.length;

  const listenLine = () => {
    setHasListened(true);
    const solfege = config.solfege_lines?.[activeIndex]?.length ? config.solfege_lines[activeIndex] : activeLine.solfege;
    playPlayableInstrumentSequence(solfege.map((token) => SOLFEGE_OFFSETS[token] ?? 0), {
      instrument: "xylophone",
      audioUrl: config.audio_clip,
      gap: 60 / plan.bpm,
      duration: 0.34,
      gain: 0.6,
      baseMidi: 60,
      oscillatorWave: "triangle"
    });
  };

  const markPassed = () => {
    setConfirmed((current) => current.map((value, index) => (index === activeIndex ? true : value)));
    setHasListened(false);
    if (activeIndex < plan.lines.length - 1) setActiveIndex((index) => index + 1);
  };

  const reset = () => {
    setActiveIndex(0);
    setHasListened(false);
    setConfirmed(plan.lines.map(() => false));
  };

  return (
    <main className="primary-activity-shell simple-score-shell">
      <Container size="4" px="4">
        <section className="teacher-control-bar">
          <Flex align="center" justify="between" gap="3" wrap="wrap">
            <Flex align="center" gap="2" wrap="wrap">
              <ListMusic size={18} />
              <Text weight="bold">简谱跟读控制</Text>
              <Badge color="green" variant="soft">{progressText}</Badge>
              <Badge color="amber" variant="soft">{config.meter ?? "2/4"} · {plan.bpm} BPM</Badge>
            </Flex>
            <Flex gap="2" wrap="wrap">
              <Button highContrast onClick={listenLine} aria-label="试听当前简谱">
                <Volume2 size={17} />
                先听
              </Button>
              <Button variant="soft" color="gray" onClick={reset} aria-label="重置">
                <RotateCcw size={17} />
              </Button>
            </Flex>
          </Flex>
        </section>

        <Grid columns={{ initial: "1", md: "1.05fr .95fr" }} gap="4" className="activity-stage">
          <section className="activity-board simple-score-board" aria-label="简谱跟读活动">
            <Flex align="center" gap="2" wrap="wrap">
              <Badge color="green" variant="soft">{alignment.primary_competency ?? "艺术表现"}</Badge>
              {(alignment.music_elements ?? []).map((element) => <Badge key={element} color="amber" variant="soft">{element}</Badge>)}
            </Flex>
            <Heading as="h1" size="8" className="activity-title">简谱跟读</Heading>
            <Text as="p" size="3" color="gray" className="activity-subtitle">
              先听示范，再看简谱跟读唱名和节奏，把谱面和声音对应起来。
            </Text>

            <div className={`simple-score-focus ${hasListened ? "listened" : ""}`}>
              <Text as="p" size="2" color="gray">当前简谱 {activeIndex + 1}</Text>
              <strong>{activeLine.score}</strong>
              <span>{activeLine.studentCue}</span>
            </div>

            <div className="simple-score-lines" aria-label="简谱行">
              {plan.lines.map((line, index) => (
                <button
                  key={line.id}
                  type="button"
                  className={`${index === activeIndex ? "active" : ""} ${confirmed[index] ? "passed" : ""}`}
                  onClick={() => {
                    setActiveIndex(index);
                    setHasListened(false);
                  }}
                >
                  <span>{index + 1}</span>
                  <strong>{line.score}</strong>
                  <small>{line.solfege.join(" ")}</small>
                </button>
              ))}
            </div>
          </section>

          <aside className="activity-side" aria-label="简谱跟读确认区">
            <section className="primary-tool teacher-confirm-card">
              <Flex align="center" gap="2">
                <CheckCircle2 size={20} />
                <Text weight="bold">教师确认</Text>
              </Flex>
              <Text as="p" size="2" color="gray">确认学生已经先听，再跟读唱名和节奏。</Text>
              <Button size="4" highContrast onClick={markPassed} disabled={!hasListened}>
                <CheckCircle2 size={18} />
                跟读通过
              </Button>
            </section>

            <section className="primary-tool simple-score-rhythm-panel">
              <Text weight="bold">节奏卡</Text>
              <div>
                {plan.rhythmCards.map((card) => (
                  <span key={card.id} className={card.rhythm}>
                    <strong><RhythmNotation rhythm={card.rhythm} label={card.name} /></strong>
                    <small>{card.name}</small>
                  </span>
                ))}
              </div>
            </section>

            <section className="primary-tool classroom-prompts">
              <Flex align="center" gap="2">
                <Eye size={18} />
                <Text weight="bold">教师提示</Text>
              </Flex>
              <p>{activeLine.teacherCue}</p>
              <p>{allConfirmed ? "可以回到歌曲或旋律短句，边看简谱边唱一次。" : "读谱时先说数字对应唱名，再按节奏跟读。"}</p>
            </section>
          </aside>
        </Grid>
      </Container>
    </main>
  );
}
