import { Badge, Button, Container, Flex, Grid, Heading, Text } from "@radix-ui/themes";
import { CheckCircle2, ListMusic, Mic2, Play, RotateCcw, SkipBack, SkipForward, Volume2 } from "lucide-react";
import { useMemo, useState } from "react";
import { playPlayableInstrumentSequence } from "../shared/realAudio";
import { buildPhraseRepairPlan, type PhrasePracticeVariant } from "./phraseSingingLogic";
import "./primaryActivity.css";

type PhraseSingingState = {
  workflow?: {
    education_alignment?: {
      primary_competency?: string;
      music_elements?: string[];
      student_practices?: string[];
    };
  };
  config?: {
    lyrics_phrases?: string[];
    melody_phrases?: string[];
    audio_clip?: string;
    bpm?: number;
    practice_variant?: PhrasePracticeVariant;
    difficult_phrase?: string;
    breath_points?: string[];
    slow_loop_enabled?: boolean;
    show_breath_hint?: boolean;
    teacher_confirm_required?: boolean;
    show_pitch_hint?: boolean;
  };
};

declare global {
  interface Window {
    __PHRASE_SINGING_STATE__?: PhraseSingingState;
  }
}

const defaultState: PhraseSingingState = {
  workflow: {
    education_alignment: {
      primary_competency: "艺术表现",
      music_elements: ["乐句", "旋律", "歌词"],
      student_practices: ["listen", "sing", "explain"]
    }
  },
  config: {
    lyrics_phrases: ["春天来了", "小鸟歌唱"],
    melody_phrases: ["do re mi", "mi sol mi"],
    teacher_confirm_required: true,
    show_pitch_hint: true
  }
};

export function PhraseSingingActivity({ state = window.__PHRASE_SINGING_STATE__ ?? defaultState }: { state?: PhraseSingingState }) {
  const phrases = state.config?.lyrics_phrases?.length ? state.config.lyrics_phrases : defaultState.config?.lyrics_phrases ?? [];
  const melodies = state.config?.melody_phrases ?? [];
  const alignment = state.workflow?.education_alignment ?? defaultState.workflow?.education_alignment ?? {};
  const repairPlan = useMemo(() => buildPhraseRepairPlan({
    lyricsPhrases: phrases,
    melodyPhrases: melodies,
    difficultPhrase: state.config?.difficult_phrase,
    breathPoints: state.config?.breath_points,
    bpm: state.config?.bpm,
  }), [melodies, phrases, state.config?.bpm, state.config?.breath_points, state.config?.difficult_phrase]);
  const isDifficultRepair = (state.config?.practice_variant ?? repairPlan.variant) === "difficult_phrase_repair";
  const [activeIndex, setActiveIndex] = useState(repairPlan.activeIndex);
  const [passed, setPassed] = useState<boolean[]>(() => phrases.map(() => false));
  const [looping, setLooping] = useState(false);
  const activePhrase = phrases[activeIndex] ?? "";
  const activeMelody = melodies[activeIndex] ?? "";
  const completedCount = passed.filter(Boolean).length;
  const allPassed = completedCount === phrases.length;

  const progressText = useMemo(() => `${completedCount}/${phrases.length || 1}`, [completedCount, phrases.length]);

  const previewPhrase = () => {
    const offsets = melodyOffsets(activeMelody, activeIndex);
    playPlayableInstrumentSequence(offsets, {
      instrument: "simple_keyboard",
      gap: 60 / repairPlan.bpm,
      duration: 0.3,
      gain: 0.62,
      baseMidi: 60,
      oscillatorWave: "triangle"
    });
  };

  const markPassed = () => {
    setPassed((current) => current.map((value, index) => (index === activeIndex ? true : value)));
    if (activeIndex < phrases.length - 1) setActiveIndex((index) => index + 1);
  };

  const reset = () => {
    setActiveIndex(repairPlan.activeIndex);
    setPassed(phrases.map(() => false));
    setLooping(false);
  };

  return (
    <main className="primary-activity-shell phrase-singing-shell">
      <Container size="4" px="4">
        <section className="teacher-control-bar">
          <Flex align="center" justify="between" gap="3" wrap="wrap">
            <Flex align="center" gap="2">
              <ListMusic size={18} />
              <Text weight="bold">分句学唱控制</Text>
              <Badge color="green" variant="soft">{progressText}</Badge>
              <Badge color={isDifficultRepair ? "amber" : "teal"} variant="soft">{repairPlan.slowLoopLabel}</Badge>
            </Flex>
            <Flex gap="2" wrap="wrap">
              <Button variant="soft" onClick={() => setActiveIndex((index) => Math.max(0, index - 1))} aria-label="上一句">
                <SkipBack size={17} />
              </Button>
              <Button highContrast onClick={previewPhrase} aria-label="试听当前乐句">
                <Volume2 size={17} />
                试听
              </Button>
              <Button variant={looping ? "solid" : "soft"} onClick={() => setLooping((value) => !value)} aria-label="循环当前乐句">
                <Play size={17} />
                {isDifficultRepair ? "慢速循环" : "循环"}
              </Button>
              <Button variant="soft" onClick={() => setActiveIndex((index) => Math.min(phrases.length - 1, index + 1))} aria-label="下一句">
                <SkipForward size={17} />
              </Button>
              <Button variant="soft" color="gray" onClick={reset} aria-label="重置">
                <RotateCcw size={17} />
              </Button>
            </Flex>
          </Flex>
        </section>

        <Grid columns={{ initial: "1", md: "1.05fr .95fr" }} gap="4" className="activity-stage">
          <section className="activity-board phrase-board" aria-label="乐句学唱活动">
            <Flex align="center" gap="2" wrap="wrap">
              <Badge color="green" variant="soft">{alignment.primary_competency ?? "艺术表现"}</Badge>
              {(alignment.music_elements ?? []).map((element) => <Badge key={element} color="amber" variant="soft">{element}</Badge>)}
            </Flex>
            <Heading as="h1" size="8" className="activity-title">乐句学唱</Heading>
            <Text as="p" size="3" color="gray" className="activity-subtitle">
              {isDifficultRepair ? "慢速听唱难点乐句，先找换气点和旋律走向，再由教师确认。" : "听一句、唱一句，由教师确认后进入下一句。"}
            </Text>

            <div className={`phrase-focus ${isDifficultRepair ? "difficult" : ""}`}>
              <Text as="p" size="2" color="gray">当前乐句 {activeIndex + 1}</Text>
              <strong>{activePhrase}</strong>
              {activeMelody ? <span>{activeMelody}</span> : null}
            </div>

            {isDifficultRepair ? (
              <section className="phrase-repair-panel" aria-label="难点乐句重练提示">
                <Text weight="bold">难点乐句重练</Text>
                <div>
                  <span>目标句</span>
                  <strong>{repairPlan.difficultPhrase}</strong>
                </div>
                {repairPlan.breathHints.length ? (
                  <div>
                    <span>换气点</span>
                    <strong>{repairPlan.breathHints.join("；")}</strong>
                  </div>
                ) : null}
                <div>
                  <span>旋律走向</span>
                  <strong>{repairPlan.melodyHint || activeMelody || "听后用手势画出高低走向"}</strong>
                </div>
              </section>
            ) : null}

            <Grid columns={{ initial: "1", sm: "2" }} gap="3">
              <section className="primary-tool phrase-step">
                <Volume2 size={22} />
                <Text weight="bold">先听</Text>
                <Text size="2" color="gray">听清歌词、旋律走向和呼吸位置。</Text>
              </section>
              <section className="primary-tool phrase-step">
                <Mic2 size={22} />
                <Text weight="bold">再唱</Text>
                <Text size="2" color="gray">用自然声音唱回，不追求机器评分。</Text>
              </section>
            </Grid>
          </section>

          <aside className="activity-side" aria-label="教师确认区">
            <section className="primary-tool teacher-confirm-card">
              <Flex align="center" gap="2">
                <CheckCircle2 size={20} />
                <Text weight="bold">教师确认</Text>
              </Flex>
              <Text as="p" size="2" color="gray">确认学生这一句是否自然、完整、稳定。</Text>
              <Button size="4" highContrast onClick={markPassed}>
                <CheckCircle2 size={18} />
                通过这一句
              </Button>
            </section>

            <section className="primary-tool phrase-list">
              <Text weight="bold">乐句列表</Text>
              <div>
                {phrases.map((phrase, index) => (
                  <button
                    key={`${phrase}-${index}`}
                    type="button"
                    className={`${index === activeIndex ? "active" : ""} ${passed[index] ? "passed" : ""}`}
                    onClick={() => setActiveIndex(index)}
                  >
                    <span>{index + 1}</span>
                    <strong>{phrase}</strong>
                  </button>
                ))}
              </div>
            </section>

            <section className="primary-tool classroom-prompts">
              <Text weight="bold">教师提示</Text>
              <p>{isDifficultRepair ? "难点句先慢速循环，学生用手势画旋律走向，再处理换气。" : "先整体听，再分句模唱；不要用机器音准分数替代教师判断。"}</p>
              <p>{allPassed ? "可以把所有乐句连起来完整演唱。" : "如果不稳定，循环当前句并放慢速度。"}</p>
            </section>
          </aside>
        </Grid>
      </Container>
    </main>
  );
}

function melodyOffsets(melody: string, index: number) {
  const map: Record<string, number> = { do: 0, re: 2, mi: 4, fa: 5, sol: 7, la: 9, ti: 11 };
  const tokens = melody.toLowerCase().split(/\s+/).filter(Boolean);
  const offsets = tokens.map((token) => map[token]).filter((value): value is number => typeof value === "number");
  return offsets.length ? offsets : [0, 2 + index, 4 + index];
}
