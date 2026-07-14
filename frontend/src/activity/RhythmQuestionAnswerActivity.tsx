import { Badge, Button, Container, Flex, Grid, Heading, Text } from "@radix-ui/themes";
import { CheckCircle2, MessageCircleQuestion, Play, RotateCcw, Volume2 } from "lucide-react";
import { useMemo, useState } from "react";
import { RhythmNotation } from "../music-components/RhythmNotation";
import { playPlayableInstrumentSequence } from "../shared/realAudio";
import {
  buildRhythmQuestionAnswerExport,
  buildRhythmQuestionAnswerPlan,
  buildRhythmQuestionAnswerSummary,
  evaluateRhythmAnswer,
  rhythmLabel,
  rhythmPatternBeats
} from "./rhythmQuestionAnswerLogic";
import "./primaryActivity.css";

type RhythmQuestionAnswerState = {
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
    question_pattern?: string[];
    answer_pattern?: string[];
  };
};

declare global {
  interface Window {
    __RHYTHM_QUESTION_STATE__?: RhythmQuestionAnswerState;
  }
}

const defaultState: RhythmQuestionAnswerState = {
  workflow: {
    education_alignment: {
      primary_competency: "艺术表现",
      music_elements: ["节奏", "节拍", "创编结构"],
      student_practices: ["listen", "tap", "create", "perform", "explain"]
    }
  },
  config: {
    meter: "2/4",
    bpm: 92,
    question_pattern: ["quarter", "eighth_pair"],
    answer_pattern: ["eighth_pair", "quarter"],
  }
};

const ANSWER_BANK = ["quarter", "eighth_pair", "eighth_sixteenth_sixteenth", "sixteenth_sixteenth_eighth", "sixteenth_four", "syncopation", "rest"];

export function RhythmQuestionAnswerActivity({ state = window.__RHYTHM_QUESTION_STATE__ ?? defaultState }: { state?: RhythmQuestionAnswerState }) {
  const config = state.config ?? defaultState.config ?? {};
  const alignment = state.workflow?.education_alignment ?? defaultState.workflow?.education_alignment ?? {};
  const plan = useMemo(() => buildRhythmQuestionAnswerPlan({
    meter: config.meter,
    bpm: config.bpm,
    questionPattern: config.question_pattern,
    answerPattern: config.answer_pattern,
  }), [config.answer_pattern, config.bpm, config.meter, config.question_pattern]);
  const [hasListenedQuestion, setHasListenedQuestion] = useState(false);
  const [answerPattern, setAnswerPattern] = useState(plan.answerPattern);
  const [tappedAnswerCount, setTappedAnswerCount] = useState(0);
  const [submitted, setSubmitted] = useState(false);
  const selection = { hasListenedQuestion, answerPattern, tappedAnswerCount };
  const evaluation = evaluateRhythmAnswer(plan, selection);
  const summary = buildRhythmQuestionAnswerSummary(plan, selection);
  const recordExport = buildRhythmQuestionAnswerExport(summary);

  const playQuestion = () => {
    setHasListenedQuestion(true);
    playPattern(plan.questionPattern, plan.bpm);
  };

  const tapAnswer = () => {
    setTappedAnswerCount((count) => Math.min(answerPattern.length, count + 1));
    playPattern([answerPattern[Math.min(answerPattern.length - 1, tappedAnswerCount)] || "quarter"], plan.bpm);
  };

  const appendAnswer = (step: string) => {
    setAnswerPattern((current) => [...current, step]);
    setTappedAnswerCount(0);
    setSubmitted(false);
  };

  const removeLast = () => {
    setAnswerPattern((current) => current.slice(0, -1));
    setTappedAnswerCount(0);
    setSubmitted(false);
  };

  const reset = () => {
    setHasListenedQuestion(false);
    setAnswerPattern(plan.answerPattern);
    setTappedAnswerCount(0);
    setSubmitted(false);
  };

  return (
    <main className="primary-activity-shell rhythm-question-shell">
      <Container size="4" px="4">
        <section className="teacher-control-bar">
          <Flex align="center" justify="between" gap="3" wrap="wrap">
            <Flex align="center" gap="2" wrap="wrap">
              <MessageCircleQuestion size={18} />
              <Text weight="bold">节奏问答控制</Text>
              <Badge color={evaluation.status === "ready" ? "green" : "amber"} variant="soft">
                {evaluation.status === "ready" ? "可小组接答" : "先听问句再答"}
              </Badge>
              <Badge color="teal" variant="soft">{plan.meter} · {plan.bpm} BPM</Badge>
            </Flex>
            <Flex gap="2" wrap="wrap">
              <Button highContrast onClick={playQuestion} aria-label="播放节奏问句">
                <Volume2 size={17} />
                播放问句
              </Button>
              <Button variant="soft" color="gray" onClick={reset} aria-label="重置节奏问答">
                <RotateCcw size={17} />
              </Button>
            </Flex>
          </Flex>
        </section>

        <Grid columns={{ initial: "1", md: "1.02fr .98fr" }} gap="4" className="activity-stage">
          <section className="activity-board rhythm-question-board" aria-label="节奏问答活动">
            <Flex align="center" gap="2" wrap="wrap">
              <Badge color="teal" variant="soft">{alignment.primary_competency ?? "艺术表现"}</Badge>
              {(alignment.music_elements ?? []).map((element) => <Badge key={element} color="amber" variant="soft">{element}</Badge>)}
            </Flex>
            <Heading as="h1" size="8" className="activity-title">节奏问答</Heading>
            <Text as="p" size="3" color="gray" className="activity-subtitle">
              先听教师节奏问句，再用同拍号答句回拍，像音乐里的对话。
            </Text>

            <Grid columns={{ initial: "1", sm: "2" }} gap="3" className="rhythm-question-columns">
              <section className="rhythm-qa-panel question">
                <Text weight="bold">问句</Text>
                <RhythmPatternCards pattern={plan.questionPattern} activeCount={hasListenedQuestion ? plan.questionPattern.length : 0} />
                <Button highContrast onClick={playQuestion} aria-label="播放节奏问句">
                  <Play size={17} />
                  听问句
                </Button>
              </section>

              <section className="rhythm-qa-panel answer">
                <Flex align="center" justify="between" gap="2">
                  <Text weight="bold">答句</Text>
                  <Badge color={rhythmPatternBeats(answerPattern) === plan.beatsPerBar ? "green" : "amber"} variant="soft">
                    {rhythmPatternBeats(answerPattern)}/{plan.beatsPerBar} 拍
                  </Badge>
                </Flex>
                <RhythmPatternCards pattern={answerPattern} activeCount={tappedAnswerCount} />
                <Flex gap="2" wrap="wrap">
                  <Button highContrast onClick={tapAnswer} disabled={!answerPattern.length} aria-label="回拍节奏答句">
                    <Volume2 size={17} />
                    回拍
                  </Button>
                  <Button variant="soft" color="gray" onClick={removeLast} disabled={!answerPattern.length}>
                    撤回一张
                  </Button>
                </Flex>
              </section>
            </Grid>

            <section className="primary-tool rhythm-answer-bank">
              <Text weight="bold">换一张节奏卡</Text>
              <div className="rhythm-answer-card-bank">
                {ANSWER_BANK.map((step) => (
                  <button key={step} type="button" onClick={() => appendAnswer(step)}>
                    <strong><RhythmNotation rhythm={step} /></strong>
                    <span>{step === "rest" ? "休止" : "1 拍"}</span>
                  </button>
                ))}
              </div>
            </section>
          </section>

          <aside className="activity-side" aria-label="节奏问答反馈区">
            <section className={`primary-tool rhythm-question-feedback ${evaluation.status}`}>
              <Flex align="center" gap="2">
                <CheckCircle2 size={20} />
                <Text weight="bold">音乐反馈</Text>
              </Flex>
              <p>{evaluation.feedback}</p>
              <Button size="4" highContrast disabled={evaluation.status !== "ready"} onClick={() => setSubmitted(true)}>
                <CheckCircle2 size={18} />
                保存问答
              </Button>
              {submitted ? <Text size="2" color="green">节奏问答已保存，可以小组接答。</Text> : null}
            </section>

            <section className="primary-tool rhythm-question-record">
              <Text weight="bold">问答记录</Text>
              <p>{summary.teacherNextStep}</p>
              <pre aria-label="节奏问答记录导出 JSON">{recordExport}</pre>
            </section>
          </aside>
        </Grid>
      </Container>
    </main>
  );
}

function RhythmPatternCards({ pattern, activeCount }: { pattern: string[]; activeCount: number }) {
  return (
    <div className="rhythm-qa-card-row">
      {pattern.map((step, index) => (
        <div key={`${step}-${index}`} className={`rhythm-qa-card ${index < activeCount ? "active" : ""} step-${step}`}>
          <strong><RhythmNotation rhythm={step} /></strong>
          <span>第 {index + 1} 张</span>
        </div>
      ))}
    </div>
  );
}

function playPattern(pattern: string[], bpm: number) {
  const gap = 60 / Math.max(60, Math.min(132, bpm));
  const offsets = pattern.map((step) => step === "rest" ? -12 : step === "eighth_pair" ? 4 : 0);
  playPlayableInstrumentSequence(offsets, {
    instrument: "woodblock",
    gap,
    duration: 0.12,
    gain: 0.62,
    baseMidi: 60,
    oscillatorWave: "triangle"
  });
}
