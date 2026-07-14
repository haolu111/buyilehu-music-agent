import { Badge, Button, Container, Flex, Grid, Heading, Text } from "@radix-ui/themes";
import { CheckCircle2, Ear, RotateCcw, Volume2 } from "lucide-react";
import { useMemo, useState } from "react";
import { playPlayableInstrumentSequence } from "../shared/realAudio";
import {
  buildDefaultInstrumentCards,
  evidenceForFamily,
  judgeInstrumentFamilySort,
  type InstrumentFamilyCard
} from "./instrumentFamilyLogic";
import "./primaryActivity.css";

type InstrumentFamilyState = {
  workflow?: {
    education_alignment?: {
      primary_competency?: string;
      music_elements?: string[];
      student_practices?: string[];
    };
  };
  config?: {
    audio_clip?: string;
    instrument_pool?: string[];
    family_set?: string[];
    instrument_card_assets?: Array<{
      id: string;
      label: string;
      src: string;
      alt?: string;
      visual_authenticity?: "generated_illustration" | string;
      source_pack?: string;
    }>;
    teacher_reason_required?: boolean;
  };
};

declare global {
  interface Window {
    __INSTRUMENT_FAMILY_STATE__?: InstrumentFamilyState;
  }
}

const defaultState: InstrumentFamilyState = {
  workflow: {
    education_alignment: {
      primary_competency: "文化理解",
      music_elements: ["乐器家族", "音色", "发声方式"],
      student_practices: ["listen", "classify", "explain"]
    }
  },
  config: {
    instrument_pool: ["笛子", "二胡", "琵琶", "小鼓"],
    family_set: ["吹奏", "拉弦", "弹拨", "打击"],
    teacher_reason_required: true
  }
};

export function InstrumentFamilySortingActivity({
  state = window.__INSTRUMENT_FAMILY_STATE__ ?? defaultState
}: {
  state?: InstrumentFamilyState;
}) {
  const config = state.config ?? defaultState.config ?? {};
  const alignment = state.workflow?.education_alignment ?? defaultState.workflow?.education_alignment ?? {};
  const families = config.family_set?.length ? config.family_set : defaultState.config?.family_set ?? [];
  const cards = useMemo(
    () => withRuntimeInstrumentPhotos(buildDefaultInstrumentCards(config.instrument_pool ?? [], families), config.instrument_card_assets ?? []),
    [config.instrument_pool, config.instrument_card_assets, families]
  );
  const [hasListened, setHasListened] = useState(false);
  const [selectedCardId, setSelectedCardId] = useState(cards[0]?.id ?? "");
  const [selectedFamily, setSelectedFamily] = useState("");
  const [selectedEvidence, setSelectedEvidence] = useState<string[]>([]);

  const selectedCard = cards.find((card) => card.id === selectedCardId) ?? cards[0];
  const evidenceTerms = useMemo(() => {
    const terms = new Set<string>();
    families.forEach((family) => evidenceForFamily(family).forEach((term) => terms.add(term)));
    return Array.from(terms);
  }, [families]);
  const result = selectedCard
    ? judgeInstrumentFamilySort({ card: selectedCard, selectedFamily, selectedEvidence, hasListened })
    : undefined;

  const previewAudio = () => {
    setHasListened(true);
    if (config.audio_clip) {
      const audio = new Audio(config.audio_clip);
      audio.play().catch(() => playInstrumentCue(selectedCard));
      return;
    }
    playInstrumentCue(selectedCard);
  };

  const reset = () => {
    setHasListened(false);
    setSelectedCardId(cards[0]?.id ?? "");
    setSelectedFamily("");
    setSelectedEvidence([]);
  };

  const chooseCard = (card: InstrumentFamilyCard) => {
    setSelectedCardId(card.id);
    setSelectedFamily("");
    setSelectedEvidence([]);
  };

  const toggleEvidence = (term: string) => {
    setSelectedEvidence((current) =>
      current.includes(term) ? current.filter((item) => item !== term) : [...current, term]
    );
  };

  return (
    <main className="primary-activity-shell instrument-family-shell">
      <Container size="4" px="4">
        <section className="teacher-control-bar">
          <Flex align="center" justify="between" gap="3" wrap="wrap">
            <Flex align="center" gap="2" wrap="wrap">
              <Ear size={18} />
              <Text weight="bold">乐器家族分类控制</Text>
              <Badge color={hasListened ? "green" : "amber"} variant="soft">
                {hasListened ? "已听声音" : "先听再分"}
              </Badge>
              <Badge color="teal" variant="soft">{alignment.primary_competency ?? "文化理解"}</Badge>
            </Flex>
            <Flex gap="2" wrap="wrap">
              <Button highContrast onClick={previewAudio} aria-label="播放乐器声音">
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
          <section className="activity-board" aria-label="乐器家族分类活动">
            <Flex align="center" gap="2" wrap="wrap">
              {(alignment.music_elements ?? []).map((element) => (
                <Badge key={element} color="amber" variant="soft">{element}</Badge>
              ))}
            </Flex>
            <Heading as="h1" size="8" className="activity-title">乐器家族分类</Heading>
            <Text as="p" size="3" color="gray" className="activity-subtitle">
              先听乐器声音，再按发声方式分类，并选出听到的音色依据。
            </Text>

            <section className={`listening-player ${hasListened ? "played" : ""}`} aria-label="乐器声音播放区">
              <button type="button" onClick={previewAudio}>
                <Volume2 size={32} />
              </button>
              <div>
                <Text weight="bold">{selectedCard ? `听：${selectedCard.label}` : "听乐器声音"}</Text>
                <Text size="2" color="gray">图片和名称只做验证，分类依据要回到声音。</Text>
              </div>
            </section>

            <Grid columns={{ initial: "1", sm: "2" }} gap="3" className="instrument-card-grid">
              {cards.map((card) => (
                <button
                  key={card.id}
                  className={`instrument-card ${card.id === selectedCard?.id ? "active" : ""}`}
                  type="button"
                  onClick={() => chooseCard(card)}
                >
                  {card.imageUrl ? (
                    <img src={card.imageUrl} alt={`${card.label}生成乐器皮肤`} />
                  ) : (
                    <span className="instrument-photo-pending">{card.visualSourceStatus === "generated_illustration" ? "生成乐器皮肤" : "待生成乐器皮肤"}</span>
                  )}
                  <strong>{card.label}</strong>
                  <span>{card.visualSourceStatus === "generated_illustration" ? "生成乐器皮肤" : "待生成/待接入"}</span>
                  <span>{audioSourceLabel(card.audioSourceKind)}</span>
                  <span>{sampleFidelityLabel(card)}</span>
                  <span>{card.id === selectedCard?.id && hasListened ? "正在分类" : "先听后分"}</span>
                </button>
              ))}
            </Grid>
          </section>

          <aside className="activity-side" aria-label="分类与依据选择区">
            <section className="primary-tool evidence-panel">
              <Text weight="bold">选择乐器家族</Text>
              <div className="family-choice-grid">
                {families.map((family) => (
                  <button
                    key={family}
                    type="button"
                    className={selectedFamily === family ? "active" : ""}
                    onClick={() => setSelectedFamily(family)}
                    disabled={!hasListened}
                  >
                    {family}
                  </button>
                ))}
              </div>
            </section>

            <section className="primary-tool evidence-panel">
              <Text weight="bold">选择听到的依据</Text>
              <Text as="p" size="2" color="gray">至少选择一个音色或发声方式依据。</Text>
              {selectedCard ? (
                <Text as="p" size="1" color="gray">
                  声音来源：{audioSourceLabel(selectedCard.audioSourceKind)}，{sampleFidelityLabel(selectedCard)}，{selectedCard.audioClassroomNote}
                </Text>
              ) : null}
              <div className="evidence-chip-grid">
                {evidenceTerms.map((term) => (
                  <button
                    key={term}
                    type="button"
                    className={selectedEvidence.includes(term) ? "active" : ""}
                    onClick={() => toggleEvidence(term)}
                    disabled={!hasListened}
                  >
                    {term}
                  </button>
                ))}
              </div>
            </section>

            <section className={`primary-tool family-result ${result?.status ?? ""}`}>
              <Flex align="center" gap="2">
                <CheckCircle2 size={20} />
                <Text weight="bold">音乐反馈</Text>
              </Flex>
              <p>{result?.musicReason ?? "请选择乐器。"}</p>
              <Button highContrast disabled={result?.status !== "correct"}>
                <CheckCircle2 size={18} />
                提交分类
              </Button>
            </section>

            <section className="primary-tool classroom-prompts">
              <Text weight="bold">教师观察点</Text>
              <p>学生是否先听声音，而不是只看乐器名称或图片。</p>
              <p>学生能否用气息感、弦鸣、拨弦、敲击感等词说明分类依据。</p>
            </section>
          </aside>
        </Grid>
      </Container>
    </main>
  );
}

function playInstrumentCue(card?: InstrumentFamilyCard) {
  const family = card?.family ?? "";
  const notes = family.includes("打") ? [0, 0, 0] : family.includes("弹") ? [0, 4, 7] : family.includes("拉") ? [0, 2, 5, 7] : [7, 9, 11];
  playPlayableInstrumentSequence(notes, {
    instrument: card?.playbackInstrument || (family.includes("打") ? "woodblock" : family.includes("弹") ? "xylophone" : family.includes("拉") ? "violin" : "flute"),
    gap: family.includes("打") ? 0.16 : 0.28,
    duration: family.includes("打") ? 0.1 : 0.24,
    gain: 0.58,
    baseMidi: 60,
    oscillatorWave: family.includes("打") ? "square" : "sine"
  });
}

function audioSourceLabel(kind: InstrumentFamilyCard["audioSourceKind"]) {
  if (kind === "open_sample") return "采样播放";
  if (kind === "soundfont_fallback") return "SoundFont fallback";
  return "WebAudio 合成音";
}

function sampleFidelityLabel(card: InstrumentFamilyCard) {
  if (card.exactRealInstrumentSample) return "精确真实采样";
  if (card.sampleFidelity === "close_soundfont_sample") return "SoundFont 接近音色";
  if (card.sampleFidelity === "approximate_soundfont_sample") return "近似采样待补";
  return "待补真实采样";
}

function withRuntimeInstrumentPhotos(
  cards: InstrumentFamilyCard[],
  assets: NonNullable<InstrumentFamilyState["config"]>["instrument_card_assets"]
): InstrumentFamilyCard[] {
  if (!assets?.length) return cards;
  const byLabel = new Map(assets.map((asset) => [asset.label, asset]));
  const byId = new Map(assets.map((asset) => [asset.id, asset]));
  return cards.map((card) => {
    const asset = byLabel.get(card.label) || byId.get(card.id);
    if (!asset || asset.visual_authenticity !== "generated_illustration") return card;
    return {
      ...card,
      imageUrl: asset.src,
      visualSourceStatus: "generated_illustration"
    };
  });
}
