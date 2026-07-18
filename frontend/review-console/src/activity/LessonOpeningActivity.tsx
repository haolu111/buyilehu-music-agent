import { Badge, Button, Container, Flex, Grid, Heading, Text } from "@radix-ui/themes";
import { CheckCircle2, Eye, Lightbulb, Play, RotateCcw, Sparkles, Volume2 } from "lucide-react";
import { useMemo, useState } from "react";
import { playPlayableInstrumentSequence } from "../shared/realAudio";
import {
  buildLessonOpeningExport,
  buildLessonOpeningPlan,
  buildLessonOpeningSummary,
  evaluateLessonOpening
} from "./lessonOpeningLogic";
import "./primaryActivity.css";
import { ReadableData } from "./ReadableData";

type LessonOpeningState = {
  workflow?: {
    education_alignment?: {
      primary_competency?: string;
      music_elements?: string[];
      student_practices?: string[];
    };
  };
  config?: {
    lesson_topic?: string;
    audio_clip?: string;
    expression_traits?: string[];
    evidence_terms?: string[];
    opening_questions?: string[];
    next_activity_hint?: string;
  };
};

declare global {
  interface Window {
    __LESSON_OPENING_STATE__?: LessonOpeningState;
  }
}

const defaultState: LessonOpeningState = {
  workflow: {
    education_alignment: {
      primary_competency: "审美感知",
      music_elements: ["情绪", "速度", "力度", "旋律"],
      student_practices: ["listen", "choose", "explain"]
    }
  },
  config: {
    lesson_topic: "小雨沙沙",
    expression_traits: ["欢快", "安静", "优美"],
    evidence_terms: ["速度较快", "力度较弱", "旋律流畅"],
    opening_questions: ["你听到的小雨像在做什么？", "音乐速度给你什么感觉？", "我们接下来怎样唱出小雨？"],
    next_activity_hint: "进入分句学唱或歌词节奏朗读。"
  }
};

export function LessonOpeningActivity({ state = window.__LESSON_OPENING_STATE__ ?? defaultState }: { state?: LessonOpeningState }) {
  const config = state.config ?? defaultState.config ?? {};
  const alignment = state.workflow?.education_alignment ?? defaultState.workflow?.education_alignment ?? {};
  const plan = useMemo(() => buildLessonOpeningPlan({
    lessonTopic: config.lesson_topic,
    expressionTraits: config.expression_traits,
    evidenceTerms: config.evidence_terms,
    openingQuestions: config.opening_questions,
  }), [config.evidence_terms, config.expression_traits, config.lesson_topic, config.opening_questions]);
  const [hasListened, setHasListened] = useState(false);
  const [selectedTrait, setSelectedTrait] = useState("");
  const [selectedEvidence, setSelectedEvidence] = useState<string[]>([]);
  const [selectedQuestion, setSelectedQuestion] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const selection = { hasListened, selectedTrait, selectedEvidence, selectedQuestion };
  const evaluation = evaluateLessonOpening(plan, selection);
  const summary = buildLessonOpeningSummary(plan, selection);
  const recordExport = buildLessonOpeningExport(summary);

  const playOpening = () => {
    setHasListened(true);
    if (config.audio_clip) {
      const audio = new Audio(config.audio_clip);
      audio.play().catch(() => playOpeningCue());
      return;
    }
    playOpeningCue();
  };

  const toggleEvidence = (term: string) => {
    setSubmitted(false);
    setSelectedEvidence((current) =>
      current.includes(term) ? current.filter((item) => item !== term) : [...current, term]
    );
  };

  const reset = () => {
    setHasListened(false);
    setSelectedTrait("");
    setSelectedEvidence([]);
    setSelectedQuestion("");
    setSubmitted(false);
  };

  return (
    <main className="primary-activity-shell lesson-opening-shell">
      <Container size="4" px="4">
        <section className="teacher-control-bar">
          <Flex align="center" justify="between" gap="3" wrap="wrap">
            <Flex align="center" gap="2" wrap="wrap">
              <Lightbulb size={18} />
              <Text weight="bold">课堂导入控制</Text>
              <Badge color={evaluation.status === "ready" ? "green" : "amber"} variant="soft">
                {evaluation.status === "ready" ? "可进入下一环节" : "先听、选、说依据"}
              </Badge>
            </Flex>
            <Flex gap="2" wrap="wrap">
              <Button highContrast onClick={playOpening} aria-label="播放导入音乐">
                <Volume2 size={17} />
                播放
              </Button>
              <Button variant="soft" color="gray" onClick={reset} aria-label="重置导入">
                <RotateCcw size={17} />
              </Button>
            </Flex>
          </Flex>
        </section>

        <Grid columns={{ initial: "1", md: "1.05fr .95fr" }} gap="4" className="activity-stage">
          <section className="activity-board lesson-opening-board" aria-label="课堂导入钩子活动">
            <Flex align="center" gap="2" wrap="wrap">
              <Badge color="teal" variant="soft">{alignment.primary_competency ?? "审美感知"}</Badge>
              {(alignment.music_elements ?? []).map((element) => <Badge key={element} color="amber" variant="soft">{element}</Badge>)}
            </Flex>
            <Heading as="h1" size="8" className="activity-title">课堂导入钩子</Heading>
            <Text as="p" size="3" color="gray" className="activity-subtitle">
              先听 {plan.lessonTopic} 的音乐片段，再用感受、依据和一个问题进入新课。
            </Text>

            <section className={`listening-player ${hasListened ? "played" : ""}`} aria-label="导入音乐播放区">
              <button type="button" onClick={playOpening}>
                <Play size={34} fill="currentColor" />
              </button>
              <div>
                <Text weight="bold">{hasListened ? "已经听过导入片段" : "先听 20 到 40 秒"}</Text>
                <Text size="2" color="gray">低段先说感受，中段再补音乐依据。</Text>
              </div>
            </section>

            <Text weight="bold" className="tool-label">选择听到的感受或画面</Text>
            <Grid columns={{ initial: "1", sm: "3" }} gap="3" className="mood-card-grid opening-card-grid">
              {plan.expressionTraits.map((trait) => (
                <button
                  key={trait}
                  type="button"
                  className={`mood-card ${selectedTrait === trait ? "active" : ""}`}
                  onClick={() => {
                    setSelectedTrait(trait);
                    setSubmitted(false);
                  }}
                >
                  <img src={moodSymbolSrc(trait)} alt={`${trait}情绪符号图卡`} />
                  <strong>{trait}</strong>
                  <span>听后选择</span>
                </button>
              ))}
            </Grid>
          </section>

          <aside className="activity-side" aria-label="导入问题与依据区">
            <section className="primary-tool evidence-panel">
              <Flex align="center" gap="2">
                <Eye size={20} />
                <Text weight="bold">选择音乐依据</Text>
              </Flex>
              <Text as="p" size="2" color="gray">不要只说喜欢，要说出听到的音乐线索。</Text>
              <div className="evidence-chip-grid">
                {plan.evidenceTerms.map((term) => (
                  <button
                    key={term}
                    type="button"
                    className={selectedEvidence.includes(term) ? "active" : ""}
                    onClick={() => toggleEvidence(term)}
                  >
                    {term}
                  </button>
                ))}
              </div>
            </section>

            <section className="primary-tool opening-question-panel">
              <Flex align="center" gap="2">
                <Sparkles size={20} />
                <Text weight="bold">带着问题进入新课</Text>
              </Flex>
              <div className="opening-question-list">
                {plan.openingQuestions.map((question) => (
                  <button
                    key={question}
                    type="button"
                    className={selectedQuestion === question ? "active" : ""}
                    onClick={() => {
                      setSelectedQuestion(question);
                      setSubmitted(false);
                    }}
                  >
                    {question}
                  </button>
                ))}
              </div>
            </section>

            <section className={`primary-tool lesson-opening-summary ${evaluation.status}`}>
              <Flex align="center" gap="2">
                <CheckCircle2 size={20} />
                <Text weight="bold">教师开场卡</Text>
              </Flex>
              <p>{evaluation.feedback}</p>
              <p>{evaluation.teacherPrompt}</p>
              <Button size="4" highContrast disabled={evaluation.status !== "ready"} onClick={() => setSubmitted(true)}>
                <CheckCircle2 size={18} />
                生成开场卡
              </Button>
              {submitted ? <Text size="2" color="green">开场卡已保存。{config.next_activity_hint}</Text> : null}
              <ReadableData value={recordExport} />
            </section>
          </aside>
        </Grid>
      </Container>
    </main>
  );
}

function playOpeningCue() {
  playPlayableInstrumentSequence([0, 2, 4, 7, 4, 2], {
    instrument: "simple_keyboard",
    gap: 0.34,
    duration: 0.25,
    gain: 0.55,
    baseMidi: 62,
    oscillatorWave: "sine"
  });
}

function moodSymbolSrc(trait: string): string {
  const ids: Record<string, string> = {
    欢快: "cheerful",
    优美: "beautiful",
    活泼: "lively",
    安静: "quiet",
    庄严: "solemn",
    神秘: "mysterious",
  };
  return `/static/assets/primary-asset-packs/mood_symbol_card_pack/images/${ids[trait] || "cheerful"}.svg`;
}
