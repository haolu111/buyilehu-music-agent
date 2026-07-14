import { Badge, Button, Container, Flex, Grid, Heading, Text } from "@radix-ui/themes";
import { CheckCircle2, Mic2, Music2, RotateCcw, SkipForward, Volume2 } from "lucide-react";
import { useMemo, useState } from "react";
import { playPlayableInstrumentSequence } from "../shared/realAudio";
import { buildSolfegeEchoPlan } from "./solfegeEchoLogic";
import "./primaryActivity.css";

type SolfegeEchoState = {
  workflow?: {
    education_alignment?: {
      primary_competency?: string;
      music_elements?: string[];
      student_practices?: string[];
    };
  };
  config?: {
    solfege_set?: string[];
    pitch_motion?: unknown;
    echo_phrases?: string[][];
    audio_clip?: string;
    bpm?: number;
    teacher_confirm_required?: boolean;
    show_solfege?: boolean;
    show_pitch_motion?: boolean;
  };
};

declare global {
  interface Window {
    __SOLFEGE_ECHO_STATE__?: SolfegeEchoState;
  }
}

const defaultState: SolfegeEchoState = {
  workflow: {
    education_alignment: {
      primary_competency: "艺术表现",
      music_elements: ["音高", "唱名", "旋律"],
      student_practices: ["listen", "sing", "explain"]
    }
  },
  config: {
    solfege_set: ["do", "re", "mi", "sol", "la"],
    echo_phrases: [["do", "re", "mi"], ["mi", "sol", "la"]],
    bpm: 88,
    teacher_confirm_required: true,
    show_solfege: true,
    show_pitch_motion: true
  }
};

const SOLFEGE_OFFSETS: Record<string, number> = { do: 0, re: 2, mi: 4, fa: 5, sol: 7, la: 9, ti: 11 };

export function SolfegeEchoActivity({ state = window.__SOLFEGE_ECHO_STATE__ ?? defaultState }: { state?: SolfegeEchoState }) {
  const config = state.config ?? defaultState.config ?? {};
  const plan = useMemo(() => buildSolfegeEchoPlan({
    solfegeSet: config.solfege_set,
    pitchMotion: config.echo_phrases?.length ? config.echo_phrases : config.pitch_motion,
    bpm: config.bpm
  }), [config.bpm, config.echo_phrases, config.pitch_motion, config.solfege_set]);
  const alignment = state.workflow?.education_alignment ?? defaultState.workflow?.education_alignment ?? {};
  const [activeIndex, setActiveIndex] = useState(0);
  const [confirmed, setConfirmed] = useState<boolean[]>(() => plan.rounds.map(() => false));
  const activeRound = plan.rounds[activeIndex] ?? plan.rounds[0];
  const completedCount = confirmed.filter(Boolean).length;
  const progressText = `${completedCount}/${plan.rounds.length || 1}`;
  const allConfirmed = completedCount === plan.rounds.length;

  const playTeacherDemo = () => {
    playPlayableInstrumentSequence(activeRound.phrase.map((token) => SOLFEGE_OFFSETS[token] ?? 0), {
      instrument: "xylophone",
      audioUrl: config.audio_clip,
      gap: 60 / plan.bpm,
      duration: 0.32,
      gain: 0.62,
      baseMidi: 60,
      oscillatorWave: "triangle"
    });
  };

  const markEchoed = () => {
    setConfirmed((current) => current.map((value, index) => (index === activeIndex ? true : value)));
    if (activeIndex < plan.rounds.length - 1) setActiveIndex((index) => index + 1);
  };

  const goNext = () => setActiveIndex((index) => (index + 1) % plan.rounds.length);

  const reset = () => {
    setActiveIndex(0);
    setConfirmed(plan.rounds.map(() => false));
  };

  return (
    <main className="primary-activity-shell solfege-echo-shell">
      <Container size="4" px="4">
        <section className="teacher-control-bar">
          <Flex align="center" justify="between" gap="3" wrap="wrap">
            <Flex align="center" gap="2" wrap="wrap">
              <Music2 size={18} />
              <Text weight="bold">唱名回声控制</Text>
              <Badge color="green" variant="soft">{progressText}</Badge>
              <Badge color="amber" variant="soft">{plan.bpm} BPM</Badge>
            </Flex>
            <Flex gap="2" wrap="wrap">
              <Button highContrast onClick={playTeacherDemo} aria-label="试听示范">
                <Volume2 size={17} />
                试听示范
              </Button>
              <Button variant="soft" onClick={goNext} aria-label="下一组">
                <SkipForward size={17} />
                下一组
              </Button>
              <Button variant="soft" color="gray" onClick={reset} aria-label="重置">
                <RotateCcw size={17} />
              </Button>
            </Flex>
          </Flex>
        </section>

        <Grid columns={{ initial: "1", md: "1.05fr .95fr" }} gap="4" className="activity-stage">
          <section className="activity-board solfege-echo-board" aria-label="唱名回声活动">
            <Flex align="center" gap="2" wrap="wrap">
              <Badge color="green" variant="soft">{alignment.primary_competency ?? "艺术表现"}</Badge>
              {(alignment.music_elements ?? []).map((element) => <Badge key={element} color="amber" variant="soft">{element}</Badge>)}
            </Flex>
            <Heading as="h1" size="8" className="activity-title">唱名回声</Heading>
            <Text as="p" size="3" color="gray" className="activity-subtitle">
              教师先唱，学生听后用自然声音模唱回来，再说出音高走向。
            </Text>

            <div className="solfege-echo-focus">
              <Text as="p" size="2" color="gray">当前回声 {activeIndex + 1}</Text>
              <strong>{activeRound.phrase.join(" ")}</strong>
              <span>{activeRound.teacherCue}</span>
              <span>{activeRound.studentCue}</span>
            </div>

            <Grid columns={{ initial: "1", sm: "2" }} gap="3">
              <section className="primary-tool solfege-echo-step">
                <Volume2 size={22} />
                <Text weight="bold">教师唱</Text>
                <Text size="2" color="gray">学生先听清唱名顺序和高低变化。</Text>
              </section>
              <section className="primary-tool solfege-echo-step">
                <Mic2 size={22} />
                <Text weight="bold">学生回声模唱</Text>
                <Text size="2" color="gray">不抢唱，用自然声音唱回同一组唱名。</Text>
              </section>
            </Grid>
          </section>

          <aside className="activity-side" aria-label="唱名回声确认区">
            <section className="primary-tool teacher-confirm-card">
              <Flex align="center" gap="2">
                <CheckCircle2 size={20} />
                <Text weight="bold">教师确认</Text>
              </Flex>
              <Text as="p" size="2" color="gray">确认唱名顺序、音高走向和自然声音，而不是交给机器打分。</Text>
              <Button size="4" highContrast onClick={markEchoed}>
                <CheckCircle2 size={18} />
                学生已模唱
              </Button>
            </section>

            <section className="primary-tool solfege-card-bank">
              <Text weight="bold">唱名卡</Text>
              <div>
                {plan.allowedSolfege.map((token) => (
                  <span key={token} className={activeRound.phrase.includes(token) ? "active" : ""}>{token}</span>
                ))}
              </div>
            </section>

            <section className="primary-tool solfege-motion-card">
              <Text weight="bold">音高走向</Text>
              <strong>{activeRound.motionHint}</strong>
              <p>{allConfirmed ? "全部回声已确认，可以回到教材旋律中唱一唱。" : "模唱后请学生用手势画出上行、下行或有上有下。"}</p>
            </section>
          </aside>
        </Grid>
      </Container>
    </main>
  );
}
