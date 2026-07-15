import { Badge, Button, Container, Flex, Grid, Heading, Text } from "@radix-ui/themes";
import { CheckCircle2, Eye, Music2, Play, RotateCcw, Sparkles, Volume2 } from "lucide-react";
import { useMemo, useState } from "react";
import { playPlayableInstrumentSequence } from "../shared/realAudio";
import "./primaryActivity.css";

type ListeningChoiceState = {
  workflow?: {
    education_alignment?: {
      primary_competency?: string;
      music_elements?: string[];
      student_practices?: string[];
    };
  };
  config?: {
    audio_clip?: string;
    expression_traits?: string[];
    evidence_terms?: string[];
    mood_card_pack?: string;
    mood_card_assets?: MoodCardAsset[];
    teacher_reason_required?: boolean;
  };
};

type MoodCardAsset = {
  id: string;
  trait: string;
  src: string;
  alt: string;
  source?: string;
};

declare global {
  interface Window {
    __LISTENING_CHOICE_STATE__?: ListeningChoiceState;
  }
}

const defaultState: ListeningChoiceState = {
  workflow: {
    education_alignment: {
      primary_competency: "审美感知",
      music_elements: ["情绪", "速度", "力度"],
      student_practices: ["listen", "choose", "explain"]
    }
  },
  config: {
    expression_traits: ["欢快", "安静", "优美"],
    evidence_terms: ["速度较快", "力度较强", "旋律流畅"],
    teacher_reason_required: true
  }
};

export function ListeningChoiceActivity({ state = window.__LISTENING_CHOICE_STATE__ ?? defaultState }: { state?: ListeningChoiceState }) {
  const config = state.config ?? defaultState.config ?? {};
  const alignment = state.workflow?.education_alignment ?? defaultState.workflow?.education_alignment ?? {};
  const traits = config.expression_traits?.length ? config.expression_traits : defaultState.config?.expression_traits ?? [];
  const evidenceTerms = config.evidence_terms?.length ? config.evidence_terms : defaultState.config?.evidence_terms ?? [];
  const moodCards = moodCardAssetsForTraits(traits, config.mood_card_assets);
  const [hasListened, setHasListened] = useState(false);
  const [selectedTrait, setSelectedTrait] = useState("");
  const [selectedEvidence, setSelectedEvidence] = useState<string[]>([]);
  const [submitted, setSubmitted] = useState(false);
  const canSubmit = hasListened && selectedTrait && (!config.teacher_reason_required || selectedEvidence.length > 0);

  const statusText = useMemo(() => {
    if (!hasListened) return "先完整听一遍";
    if (!selectedTrait) return "选择你的情绪感受";
    if (!selectedEvidence.length) return "选择听到的音乐依据";
    return "可以提交给教师观察";
  }, [hasListened, selectedEvidence.length, selectedTrait]);

  const previewAudio = () => {
    setHasListened(true);
    if (config.audio_clip) {
      const audio = new Audio(config.audio_clip);
      audio.play().catch(() => playFallbackListeningCue());
      return;
    }
    playFallbackListeningCue();
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
    setSubmitted(false);
  };

  return (
    <main className="primary-activity-shell listening-choice-shell">
      <Container size="4" px="4">
        <section className="teacher-control-bar">
          <Flex align="center" justify="between" gap="3" wrap="wrap">
            <Flex align="center" gap="2">
              <Eye size={18} />
              <Text weight="bold">听赏导入控制</Text>
              <Badge color={hasListened ? "green" : "amber"} variant="soft">{statusText}</Badge>
            </Flex>
            <Flex gap="2" wrap="wrap">
              <Button highContrast onClick={previewAudio} aria-label="播放音乐">
                <Volume2 size={17} />
                播放
              </Button>
              <Button variant="soft" color="gray" onClick={reset} aria-label="重置">
                <RotateCcw size={17} />
              </Button>
            </Flex>
          </Flex>
        </section>

        <Grid columns={{ initial: "1", md: "1.08fr .92fr" }} gap="4" className="activity-stage">
          <section className="activity-board listening-board" aria-label="听赏情绪选择活动">
            <Flex align="center" gap="2" wrap="wrap">
              <Badge color="teal" variant="soft">{alignment.primary_competency ?? "审美感知"}</Badge>
              {(alignment.music_elements ?? []).map((element) => <Badge key={element} color="amber" variant="soft">{element}</Badge>)}
            </Flex>
            <Heading as="h1" size="8" className="activity-title">听赏情绪选择</Heading>
            <Text as="p" size="3" color="gray" className="activity-subtitle">
              先听音乐，再选择感受到的情绪，并用音乐要素说出依据。
            </Text>

            <section className={`listening-player ${hasListened ? "played" : ""}`} aria-label="音乐播放区">
              <button type="button" onClick={previewAudio}>
                <Play size={34} fill="currentColor" />
              </button>
              <div>
                <Text weight="bold">{hasListened ? "已经听过一遍" : "先完整听一遍"}</Text>
                <Text size="2" color="gray">低年级先表达感受，中年级再补速度、力度等依据。</Text>
              </div>
            </section>

            <Grid columns={{ initial: "1", sm: "3" }} gap="3" className="mood-card-grid">
              {traits.map((trait) => (
                <button
                  key={trait}
                  type="button"
                  className={`mood-card ${selectedTrait === trait ? "active" : ""}`}
                  onClick={() => {
                    setSelectedTrait(trait);
                    setSubmitted(false);
                  }}
                >
                  {moodCards[trait] ? (
                    <img src={moodCards[trait].src} alt={moodCards[trait].alt || `${trait}情绪图卡`} />
                  ) : (
                    <Sparkles size={24} />
                  )}
                  <strong>{trait}</strong>
                  <span>{moodCards[trait] ? "项目生成图卡" : "我听到的情绪"}</span>
                </button>
              ))}
            </Grid>
          </section>

          <aside className="activity-side" aria-label="音乐依据选择区">
            <section className="primary-tool evidence-panel">
              <Flex align="center" gap="2">
                <Music2 size={20} />
                <Text weight="bold">选择音乐依据</Text>
              </Flex>
              <Text as="p" size="2" color="gray">至少选择一个你真正听到的依据。</Text>
              <div className="evidence-chip-grid">
                {evidenceTerms.map((term) => (
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

            <section className="primary-tool listening-summary">
              <Flex align="center" gap="2">
                <CheckCircle2 size={20} />
                <Text weight="bold">学生表达</Text>
              </Flex>
              <p>
                我觉得这段音乐是
                <strong>{selectedTrait || "____"}</strong>
                的，因为我听到了
                <strong>{selectedEvidence.length ? selectedEvidence.join("、") : "____"}</strong>
                。
              </p>
              <Button size="4" highContrast disabled={!canSubmit} onClick={() => setSubmitted(true)}>
                <CheckCircle2 size={18} />
                提交依据
              </Button>
              {submitted ? <Text size="2" color="green">已提交：请复听并验证这个依据。</Text> : null}
            </section>

            <section className="primary-tool classroom-prompts">
              <Text weight="bold">教师观察点</Text>
              <p>学生是否先听完整音乐，而不是先看选项猜答案。</p>
              <p>学生能否把情绪选择和速度、力度、旋律等听觉证据连接起来。</p>
            </section>
          </aside>
        </Grid>
      </Container>
    </main>
  );
}

function playFallbackListeningCue() {
  playPlayableInstrumentSequence([0, 4, 7, 9, 7, 4], {
    instrument: "simple_keyboard",
    gap: 0.36,
    duration: 0.28,
    gain: 0.58,
    baseMidi: 60,
    oscillatorWave: "sine"
  });
}

function moodCardAssetsForTraits(traits: string[], assets?: MoodCardAsset[]) {
  const byTrait: Record<string, MoodCardAsset> = {};
  for (const asset of assets ?? []) {
    if (asset.trait) byTrait[asset.trait] = asset;
  }
  const fallbackIds: Record<string, string> = {
    欢快: "cheerful",
    优美: "beautiful",
    活泼: "lively",
    安静: "quiet",
    庄严: "solemn",
    神秘: "mysterious",
  };
  for (const trait of traits) {
    if (byTrait[trait] || !fallbackIds[trait]) continue;
    const id = fallbackIds[trait];
    byTrait[trait] = {
      id,
      trait,
      src: `/static/assets/primary-asset-packs/mood_symbol_card_pack/images/${id}.svg`,
      alt: `${trait}情绪符号图卡`,
      source: "project_generated_svg_fallback",
    };
  }
  return byTrait;
}
