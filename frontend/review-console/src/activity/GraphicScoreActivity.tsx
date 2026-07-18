import { Badge, Button, Container, Flex, Grid, Heading, Text } from "@radix-ui/themes";
import { CheckCircle2, Eraser, Shapes, Volume2 } from "lucide-react";
import { useMemo, useState } from "react";
import { RhythmCardBank, SolfegeCardBank, type SolfegeCard } from "../music-components";
import { resolvePitchToken } from "../shared/pitchCatalog";
import { playHybridToneSequenceAsync } from "../shared/realAudio";
import { getRhythmPatternDefinition } from "../shared/rhythmPatternCatalog";
import { formalRhythmLabel, formalRhythmName } from "./rhythmNaming";
import { normalizeRhythmCards, type RhythmCard } from "./rhythmWarmupLogic";
import {
  buildGraphicScorePlaybackEvents,
  buildGraphicScoreExport,
  buildGraphicScorePlan,
  buildGraphicScoreSummary,
  evaluateGraphicScore,
  placeGraphicPitchCard,
  placeGraphicRhythmCard,
  placeGraphicSymbol,
  type GraphicScoreMode,
  type GraphicScoreSlot,
  type GraphicSymbolMeaning
} from "./graphicScoreLogic";
import "./primaryActivity.css";
import { ReadableData } from "./ReadableData";

type GraphicScoreState = {
  workflow?: {
    education_alignment?: {
      primary_competency?: string;
      music_elements?: string[];
      student_practices?: string[];
    };
  };
  config?: {
    meter?: string;
    total_beats?: number;
    symbol_meanings?: GraphicSymbolMeaning[];
    required_elements?: string[];
    bpm?: number;
    creation_mode?: GraphicScoreMode;
    rhythm_card_ids?: string[];
    pitch_card_ids?: string[];
  };
};

declare global {
  interface Window {
    __GRAPHIC_SCORE_STATE__?: GraphicScoreState;
  }
}

const defaultState: GraphicScoreState = {
  workflow: {
    education_alignment: {
      primary_competency: "创意实践",
      music_elements: ["图形谱", "音高", "力度", "节奏"],
      student_practices: ["create", "listen", "revise", "explain"]
    }
  },
  config: {
    meter: "2/4",
    total_beats: 4,
    bpm: 88,
    creation_mode: "graphic",
    rhythm_card_ids: ["quarter", "eighth_pair", "sixteenth_four", "rest"],
    pitch_card_ids: ["do", "re", "mi", "fa", "sol", "la", "ti"],
    symbol_meanings: [
      { symbol: "dot", label: "点", pitch: "high", duration: "short", dynamics: "soft" },
      { symbol: "line", label: "线", pitch: "middle", duration: "long", dynamics: "medium" },
      { symbol: "block", label: "块", pitch: "low", duration: "long", dynamics: "strong" },
    ],
    required_elements: ["pitch", "duration", "dynamics"],
  }
};

const PITCH_LABELS: Record<string, string> = { high: "高", middle: "中", low: "低" };
const DURATION_LABELS: Record<string, string> = { short: "短", long: "长" };
const DYNAMICS_LABELS: Record<string, string> = { soft: "弱", medium: "中", strong: "强" };
const DEFAULT_RHYTHM_IDS = ["quarter", "eighth_pair", "sixteenth_four", "rest"];
const DEFAULT_PITCH_IDS = ["do", "re", "mi", "fa", "sol", "la", "ti"];
const CARD_COLORS = ["#f1c36a", "#7fcbb6", "#81b6d9", "#dca384"];
const SOLFEGE_HAND_SIGNS: Record<string, string> = {
  do: "拳形",
  re: "斜掌",
  mi: "平掌",
  fa: "拇指向下",
  sol: "掌心向前",
  la: "弯掌",
  ti: "食指向上"
};

export function GraphicScoreActivity({ state = window.__GRAPHIC_SCORE_STATE__ ?? defaultState }: { state?: GraphicScoreState }) {
  const config = state.config ?? defaultState.config ?? {};
  const alignment = state.workflow?.education_alignment ?? defaultState.workflow?.education_alignment ?? {};
  const plan = useMemo(() => buildGraphicScorePlan({
    meter: config.meter,
    totalBeats: config.total_beats,
    symbolMeanings: config.symbol_meanings,
    requiredElements: config.required_elements,
  }), [config.meter, config.required_elements, config.symbol_meanings, config.total_beats]);
  const rhythmCards = useMemo(() => buildGraphicRhythmCards(config.rhythm_card_ids, config.bpm), [config.bpm, config.rhythm_card_ids]);
  const pitchCards = useMemo(() => buildGraphicPitchCards(config.pitch_card_ids), [config.pitch_card_ids]);
  const [slots, setSlots] = useState<GraphicScoreSlot[]>(plan.slots);
  const [activeSymbol, setActiveSymbol] = useState<GraphicSymbolMeaning>(plan.symbols[0]);
  const [activeRhythmId, setActiveRhythmId] = useState(rhythmCards[0]?.id || "quarter");
  const [activePitchId, setActivePitchId] = useState(pitchCards[0]?.id || "do");
  const [mode, setMode] = useState<GraphicScoreMode>(config.creation_mode === "mixed_cards" ? "mixed_cards" : "graphic");
  const [playedBack, setPlayedBack] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [audioStatus, setAudioStatus] = useState("");
  const evaluation = evaluateGraphicScore(plan, slots, playedBack, mode);
  const summary = useMemo(() => buildGraphicScoreSummary(plan, slots, playedBack, mode), [mode, playedBack, plan, slots]);
  const recordExport = useMemo(() => buildGraphicScoreExport(summary), [summary]);

  const placeSymbol = (beatIndex: number) => {
    setSlots((current) => {
      let next = placeGraphicSymbol(current, beatIndex, activeSymbol);
      if (mode === "mixed_cards") {
        next = placeGraphicRhythmCard(next, beatIndex, activeRhythmId);
        next = placeGraphicPitchCard(next, beatIndex, activePitchId);
      }
      return next;
    });
    setPlayedBack(false);
    setSubmitted(false);
    setAudioStatus("");
  };

  const playScore = async () => {
    if (!slots.some((slot) => slot.symbol)) return;
    const events = buildGraphicScorePlaybackEvents(slots, config.bpm ?? 88, mode);
    if (!events.length) {
      setPlayedBack(true);
      setAudioStatus("全休止作品：保持内心拍，不播放声音");
      return;
    }
    setAudioStatus("正在加载真实钢琴采样...");
    const result = await playHybridToneSequenceAsync([], {
      instrument: "acoustic_grand_piano",
      events,
      gain: 0.55,
      baseMidi: 60,
      allowOscillatorFallback: false
    });
    setPlayedBack(result.ok);
    setAudioStatus(result.ok ? "已按节奏卡和音高卡播放" : "钢琴采样未加载，作品未标记为已回放");
  };

  const switchMode = (nextMode: GraphicScoreMode) => {
    setMode(nextMode);
    setSlots(plan.slots);
    setPlayedBack(false);
    setSubmitted(false);
    setAudioStatus("");
  };

  const reset = () => {
    setSlots(plan.slots);
    setActiveSymbol(plan.symbols[0]);
    setPlayedBack(false);
    setSubmitted(false);
    setAudioStatus("");
  };

  return (
    <main className="primary-activity-shell graphic-score-shell">
      <Container size="4" px="4">
        <section className="teacher-control-bar">
          <Flex align="center" justify="between" gap="3" wrap="wrap">
            <Flex align="center" gap="2" wrap="wrap">
              <Shapes size={18} />
              <Text weight="bold">图形谱创编控制</Text>
              <Badge color={evaluation.status === "ready" ? "green" : "amber"} variant="soft">
                {evaluation.status === "ready" ? "可展示" : "先创编并回放"}
              </Badge>
              <Badge color="teal" variant="soft">{plan.meter} · {config.bpm ?? 88} BPM</Badge>
            </Flex>
            <Flex gap="2" wrap="wrap">
              <div className="graphic-score-mode-control" role="group" aria-label="图形谱创编模式">
                <Button type="button" variant={mode === "graphic" ? "solid" : "soft"} highContrast={mode === "graphic"} onClick={() => switchMode("graphic")}>纯图形</Button>
                <Button type="button" variant={mode === "mixed_cards" ? "solid" : "soft"} highContrast={mode === "mixed_cards"} onClick={() => switchMode("mixed_cards")}>图形＋音乐卡</Button>
              </div>
              <Button highContrast onClick={playScore} disabled={!slots.some((slot) => slot.symbol)} aria-label="播放图形谱">
                <Volume2 size={17} />
                播放
              </Button>
              <Button variant="soft" color="gray" onClick={reset} aria-label="清空图形谱">
                <Eraser size={17} />
              </Button>
            </Flex>
          </Flex>
        </section>

        <Grid columns={{ initial: "1", md: "1.08fr .92fr" }} gap="4" className="activity-stage">
          <section className="activity-board graphic-score-board" aria-label="图形谱创编活动">
            <Flex align="center" gap="2" wrap="wrap">
              <Badge color="teal" variant="soft">{alignment.primary_competency ?? "创意实践"}</Badge>
              {(alignment.music_elements ?? []).map((element) => <Badge key={element} color="amber" variant="soft">{element}</Badge>)}
            </Flex>
            <Heading as="h1" size="8" className="activity-title">图形谱创编</Heading>
            <Text as="p" size="3" color="gray" className="activity-subtitle">
              {mode === "graphic"
                ? "用点、线、块表示高低、长短和强弱，按顺序放入拍点，播放后再说明图形含义。"
                : "先选图形、节奏卡和唱名卡，再放入拍点；节奏卡决定时值，唱名卡决定真实音高。"}
            </Text>

            <Text weight="bold" className="tool-label">图形含义卡</Text>
            <div className="graphic-symbol-bank" aria-label="图形含义卡">
              {plan.symbols.map((symbol) => (
                <button
                  key={symbol.symbol}
                  type="button"
                  className={`${activeSymbol.symbol === symbol.symbol ? "active" : ""} shape-${symbol.symbol}`}
                  onClick={() => setActiveSymbol(symbol)}
                >
                  <strong>{symbolGlyph(symbol.symbol)}</strong>
                  <span>{symbol.label}：{PITCH_LABELS[symbol.pitch]} · {DURATION_LABELS[symbol.duration]} · {DYNAMICS_LABELS[symbol.dynamics]}</span>
                </button>
              ))}
            </div>

            {mode === "mixed_cards" ? (
              <section className="graphic-score-card-palettes" aria-label="图形谱音乐卡片材料">
                <RhythmCardBank cards={rhythmCards} activeCardId={activeRhythmId} onSelect={setActiveRhythmId} />
                <SolfegeCardBank
                  cards={pitchCards.map((card) => ({ ...card, selected: card.id === activePitchId }))}
                  mode="order"
                  onSelect={setActivePitchId}
                />
              </section>
            ) : null}

            <Text weight="bold" className="tool-label">图形谱板</Text>
            <div className="graphic-score-slot-grid" aria-label="图形谱板">
              {slots.map((slot) => (
                <button
                  key={slot.beatIndex}
                  type="button"
                  className={`graphic-score-slot ${slot.symbol ? `filled shape-${slot.symbol.symbol}` : ""}`}
                  onClick={() => placeSymbol(slot.beatIndex)}
                >
                  <span>第 {slot.beatIndex} 拍</span>
                  <strong>{slot.symbol ? symbolGlyph(slot.symbol.symbol) : "+"}</strong>
                  <small>{slot.symbol ? slotDescription(slot, mode) : "放入图形"}</small>
                </button>
              ))}
            </div>
          </section>

          <aside className="activity-side" aria-label="图形谱反馈区">
            <section className={`primary-tool graphic-score-feedback ${evaluation.status}`}>
              <Flex align="center" gap="2">
                <CheckCircle2 size={20} />
                <Text weight="bold">音乐反馈</Text>
              </Flex>
              <p>{evaluation.feedback}</p>
              {audioStatus ? <Text size="2" color={playedBack ? "green" : "amber"}>{audioStatus}</Text> : null}
              <Button size="4" highContrast disabled={evaluation.status !== "ready"} onClick={() => setSubmitted(true)}>
                <CheckCircle2 size={18} />
                提交展示
              </Button>
              {submitted ? <Text size="2" color="green">图形谱已保存，可以全班展示。</Text> : null}
            </section>

            <section className="primary-tool graphic-score-record-panel">
              <Text weight="bold">创编记录</Text>
              <div className="graphic-score-stats">
                <span>高低：{summary.usedPitchLevels.map((item) => PITCH_LABELS[item]).join("、") || "待补"}</span>
                <span>长短：{summary.usedDurations.map((item) => DURATION_LABELS[item]).join("、") || "待补"}</span>
                <span>强弱：{summary.usedDynamics.map((item) => DYNAMICS_LABELS[item]).join("、") || "待补"}</span>
                {mode === "mixed_cards" ? <span>节奏：{summary.rhythmIds.map(formalRhythmLabel).join("、") || "待补"}</span> : null}
                {mode === "mixed_cards" ? <span>唱名：{summary.pitchIds.map(pitchCardLabel).join("、") || "待补"}</span> : null}
                <span>{summary.readyForPerformance ? "可表演" : "继续修改"}</span>
              </div>
              <p>{summary.teacherNextStep}</p>
              <ReadableData value={recordExport} />
            </section>
          </aside>
        </Grid>
      </Container>
    </main>
  );
}

function symbolGlyph(symbol: string): string {
  if (symbol === "line") return "━";
  if (symbol === "block") return "■";
  return "●";
}

function buildGraphicRhythmCards(values: unknown, bpm = 88): RhythmCard[] {
  const requested = Array.isArray(values) ? values.map(String).filter(Boolean) : [];
  const ids = requested.length ? requested : DEFAULT_RHYTHM_IDS;
  return normalizeRhythmCards(ids.map((id, index) => {
    const definition = getRhythmPatternDefinition(id);
    return {
      id: definition.id,
      patternId: definition.id,
      label: formalRhythmName(definition.id),
      syllable: formalRhythmLabel(definition.id),
      beats: definition.durationBeats,
      hitRequired: definition.hitOffsetsBeats.length > 0,
      subdivisions: Math.max(1, definition.hitOffsetsBeats.length),
      gesture: definition.hitOffsetsBeats.length ? "决定时值" : "保持休止",
      color: CARD_COLORS[index % CARD_COLORS.length]
    };
  }), bpm);
}

function buildGraphicPitchCards(values: unknown): SolfegeCard[] {
  const requested = Array.isArray(values) ? values.map(String).filter(Boolean) : [];
  const ids = (requested.length ? requested : DEFAULT_PITCH_IDS)
    .map((value) => resolvePitchToken(value)?.id)
    .filter((value): value is string => Boolean(value));
  return Array.from(new Set(ids)).map((id) => ({
    id,
    syllable: pitchCardLabel(id),
    handSign: SOLFEGE_HAND_SIGNS[id] || "唱名",
    heard: false
  }));
}

function pitchCardLabel(pitchId: string): string {
  const pitch = resolvePitchToken(pitchId);
  return pitch?.numberLabels[0] || pitchId;
}

function slotDescription(slot: GraphicScoreSlot, mode: GraphicScoreMode): string {
  const graphic = `${PITCH_LABELS[slot.symbol?.pitch || "middle"]} · ${DURATION_LABELS[slot.symbol?.duration || "long"]} · ${DYNAMICS_LABELS[slot.symbol?.dynamics || "medium"]}`;
  if (mode === "graphic") return graphic;
  const rhythm = slot.rhythmId ? formalRhythmLabel(slot.rhythmId) : "待选节奏";
  const pitch = slot.pitchId ? pitchCardLabel(slot.pitchId) : "待选音高";
  return `${rhythm} · ${pitch} · ${graphic}`;
}
