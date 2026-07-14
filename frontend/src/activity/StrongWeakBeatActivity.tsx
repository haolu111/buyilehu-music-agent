import { Badge, Button, Container, Flex, Grid, Heading, Text } from "@radix-ui/themes";
import { CheckCircle2, Footprints, Hand, Play, RotateCcw } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import { playHybridToneSequenceAsync, stopActiveSampledPlayback } from "../shared/realAudio";
import {
  accentInputChoices,
  accentToneOffset,
  buildAccentInputSummary,
  buildAccentRound,
  buildCountInBeats,
  evaluateAccentAttempt,
  judgeAccentInput,
  type AccentBeat,
  type AccentAttemptEvaluation,
  type AccentInputJudgement,
  type AccentStrength,
  type StrongWeakMeter
} from "./strongWeakBeatLogic";
import "./primaryActivity.css";

type PracticeStage = "idle" | "listening" | "ready" | "count_in" | "judging" | "feedback" | "movement" | "complete" | "audio_error";

type StrongWeakBeatState = {
  workflow?: {
    education_alignment?: {
      primary_competency?: string;
      music_elements?: string[];
    };
  };
  config?: {
    meter?: StrongWeakMeter;
    bpm?: number;
    cycle_count?: number;
  };
};

declare global {
  interface Window {
    __STRONG_WEAK_BEAT_STATE__?: StrongWeakBeatState;
  }
}

const defaultState: StrongWeakBeatState = {
  workflow: {
    education_alignment: {
      primary_competency: "艺术表现",
      music_elements: ["节拍", "拍号", "强弱"]
    }
  },
  config: { meter: "2/4", bpm: 88, cycle_count: 2 }
};

const inputLabels: Record<AccentStrength, string> = {
  strong: "强拍",
  secondary: "次强拍",
  weak: "弱拍"
};

export function StrongWeakBeatActivity({ state = window.__STRONG_WEAK_BEAT_STATE__ ?? defaultState }: { state?: StrongWeakBeatState }) {
  const config = state.config ?? defaultState.config ?? {};
  const [meter, setMeter] = useState<StrongWeakMeter>(config.meter ?? "2/4");
  const [bpm, setBpm] = useState(() => normalizeBpm(config.bpm ?? 88));
  const [bpmDraft, setBpmDraft] = useState(() => String(normalizeBpm(config.bpm ?? 88)));
  const cycleCount = config.cycle_count ?? 2;
  const round = useMemo(() => buildAccentRound({ meter, bpm, cycleCount }), [bpm, cycleCount, meter]);
  const beatMs = Math.round(60000 / Math.max(40, Math.min(180, bpm)));
  const alignment = state.workflow?.education_alignment ?? defaultState.workflow?.education_alignment ?? {};
  const inputChoices = accentInputChoices(meter);

  const [stage, setStage] = useState<PracticeStage>("idle");
  const [activeIndex, setActiveIndex] = useState(0);
  const [judgements, setJudgements] = useState<AccentInputJudgement[]>([]);
  const [feedback, setFeedback] = useState("先听示范，感受每一小节的强弱规律。");
  const [movementFinished, setMovementFinished] = useState(false);
  const [countInBeat, setCountInBeat] = useState(0);
  const [attemptEvaluation, setAttemptEvaluation] = useState<AccentAttemptEvaluation | null>(null);
  const showAccentChoices = stage === "count_in" || stage === "judging";
  const timersRef = useRef<number[]>([]);
  const playbackRunRef = useRef(0);
  const stageRef = useRef<PracticeStage>("idle");
  const activeIndexRef = useRef(0);
  const scheduledBeatStartRef = useRef(0);
  const matchedBeatIdsRef = useRef(new Set<string>());
  const judgementsRef = useRef<AccentInputJudgement[]>([]);

  const activeBeat = round[activeIndex] ?? round[0];
  const summary = useMemo(() => buildAccentInputSummary(judgements), [judgements]);

  const clearTimers = () => {
    timersRef.current.forEach((timer) => window.clearTimeout(timer));
    timersRef.current = [];
  };

  const cancelPlayback = () => {
    playbackRunRef.current += 1;
    clearTimers();
    stopActiveSampledPlayback();
  };

  const appendJudgement = (judgement: AccentInputJudgement) => {
    judgementsRef.current = [...judgementsRef.current, judgement];
    setJudgements(judgementsRef.current);
    setFeedback(judgement.feedback);
  };

  const reset = () => {
    cancelPlayback();
    matchedBeatIdsRef.current = new Set();
    judgementsRef.current = [];
    activeIndexRef.current = 0;
    scheduledBeatStartRef.current = 0;
    stageRef.current = "idle";
    setStage("idle");
    setActiveIndex(0);
    setJudgements([]);
    setMovementFinished(false);
    setCountInBeat(0);
    setAttemptEvaluation(null);
    setFeedback("先听示范，感受每一小节的强弱规律。");
  };

  const handlePracticeSettingChange = (nextMeter: StrongWeakMeter, nextBpm: number) => {
    reset();
    setMeter(nextMeter);
    setBpm(normalizeBpm(nextBpm));
    setBpmDraft(String(normalizeBpm(nextBpm)));
  };

  const applyBpmDraft = () => {
    const nextBpm = normalizeBpm(Number(bpmDraft));
    if (nextBpm === bpm) {
      setBpmDraft(String(nextBpm));
      return;
    }
    handlePracticeSettingChange(meter, nextBpm);
  };

  const playAccentSequence = async (beats: AccentBeat[]) => {
    const result = await playHybridToneSequenceAsync([], {
      instrument: "woodblock",
      baseMidi: 60,
      gain: 0.62,
      allowOscillatorFallback: false,
      events: beats.map((beat) => ({
        offset: accentToneOffset(beat.strength),
        start: beat.startMs / 1000,
        duration: 0.13
      }))
    });
    return result.ok;
  };

  const playCountInSequence = async (beats: AccentBeat[]) => {
    const result = await playHybridToneSequenceAsync([], {
      instrument: "glockenspiel",
      baseMidi: 74,
      gain: 0.5,
      allowOscillatorFallback: false,
      events: beats.map((beat) => ({
        offset: beat.beatInBar === 1 ? 7 : 0,
        start: beat.startMs / 1000,
        duration: 0.1
      }))
    });
    return result.ok;
  };

  const scheduleTimeline = (beats: AccentBeat[], mode: "display" | "count_in" | "judge", onFinish: () => void) => {
    clearTimers();
    const run = playbackRunRef.current;
    const startAt = performance.now();
    beats.forEach((beat, index) => {
      const timer = window.setTimeout(() => {
        if (playbackRunRef.current !== run) return;
        if (mode === "judge" && index > 0) {
          const previous = beats[index - 1];
          if (!matchedBeatIdsRef.current.has(previous.id)) {
            appendJudgement({ status: "missing", beat: previous, feedback: `漏拍：第 ${previous.beatInBar} 拍是${previous.label}。` });
          }
        }
        if (mode === "count_in") {
          setCountInBeat(index + 1);
        } else {
          activeIndexRef.current = index % round.length;
          scheduledBeatStartRef.current = startAt + beat.startMs;
          setActiveIndex(activeIndexRef.current);
        }
      }, Math.max(0, startAt + beat.startMs - performance.now()));
      timersRef.current.push(timer);
    });
    const finalBeat = beats[beats.length - 1];
    const finalTimer = window.setTimeout(() => {
      if (playbackRunRef.current !== run) return;
      if (mode === "judge" && !matchedBeatIdsRef.current.has(finalBeat.id)) {
        appendJudgement({ status: "missing", beat: finalBeat, feedback: `漏拍：第 ${finalBeat.beatInBar} 拍是${finalBeat.label}。` });
      }
      onFinish();
    }, Math.max(0, startAt + finalBeat.startMs + beatMs - performance.now()));
    timersRef.current.push(finalTimer);
  };

  const startListening = async () => {
    reset();
    const run = playbackRunRef.current;
    stageRef.current = "listening";
    setStage("listening");
    setFeedback("正在播放示范：先听，不需要按按钮。\n");
    const demonstration = [...round, ...round].map((beat, index) => ({ ...beat, id: `demo-${index}`, startMs: index * beatMs }));
    if (!await playAccentSequence(demonstration)) {
      if (playbackRunRef.current !== run) return;
      stageRef.current = "audio_error";
      setStage("audio_error");
      setFeedback("真实音色未能加载，请重新加载后再开始。");
      return;
    }
    scheduleTimeline(demonstration, "display", () => {
      if (playbackRunRef.current !== run) return;
      stageRef.current = "ready";
      setStage("ready");
      setFeedback("示范结束。现在只需用网页判断强拍、次强拍和弱拍。");
    });
  };

  const startJudging = async () => {
    cancelPlayback();
    const run = playbackRunRef.current;
    matchedBeatIdsRef.current = new Set();
    judgementsRef.current = [];
    setJudgements([]);
    setCountInBeat(0);
    setAttemptEvaluation(null);
    setActiveIndex(-1);
    stageRef.current = "count_in";
    setStage("count_in");
    setFeedback("预备拍：只听节拍器，不要按网页按钮。\n");
    const countIn = buildCountInBeats(meter, bpm);
    if (!await playCountInSequence(countIn)) {
      if (playbackRunRef.current !== run) return;
      stageRef.current = "audio_error";
      setStage("audio_error");
      setFeedback("真实音色未能加载，请重新加载后再开始。");
      return;
    }
    scheduleTimeline(countIn, "count_in", () => {
      if (playbackRunRef.current !== run) return;
      stageRef.current = "judging";
      setStage("judging");
      setFeedback("现在开始网页判断：在当前拍按强拍、次强拍或弱拍。此时不做身体动作。\n");
      void playAccentSequence(round).then((audioOk) => {
        if (playbackRunRef.current !== run) return;
        if (!audioOk) {
          stageRef.current = "audio_error";
          setStage("audio_error");
          setFeedback("真实音色未能加载，请重新加载后再开始。");
          return;
        }
        scheduleTimeline(round, "judge", () => {
          if (playbackRunRef.current !== run) return;
          const evaluation = evaluateAccentAttempt(buildAccentInputSummary(judgementsRef.current));
          setAttemptEvaluation(evaluation);
          stageRef.current = "feedback";
          setStage("feedback");
          setFeedback(evaluation.feedback);
        });
      });
    });
  };

  const chooseAccent = (strength: AccentStrength) => {
    if (stageRef.current !== "judging") return;
    const beat = round[activeIndexRef.current];
    if (!beat) return;
    if (matchedBeatIdsRef.current.has(beat.id)) {
      appendJudgement({ status: "extra", beat, selectedStrength: strength, feedback: "多按：这一拍已经判断过了，等待下一拍。" });
      return;
    }
    matchedBeatIdsRef.current.add(beat.id);
    appendJudgement(judgeAccentInput(beat, strength, performance.now() - scheduledBeatStartRef.current));
  };

  const startMovement = async () => {
    cancelPlayback();
    const run = playbackRunRef.current;
    setMovementFinished(false);
    stageRef.current = "movement";
    setStage("movement");
    setFeedback("现在离开按钮，只做身体动作：强拍拍手，弱拍拍腿。\n");
    if (!await playAccentSequence(round)) {
      if (playbackRunRef.current !== run) return;
      stageRef.current = "audio_error";
      setStage("audio_error");
      setFeedback("真实音色未能加载，请重新加载后再开始。");
      return;
    }
    scheduleTimeline(round, "display", () => {
      if (playbackRunRef.current !== run) return;
      setMovementFinished(true);
      setFeedback("身体律动播放结束。确认自己已完成后，再结束练习。\n");
    });
  };

  useEffect(() => {
    const keyMap: Record<string, AccentStrength> = { f: "strong", g: "secondary", h: "weak" };
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.repeat || stageRef.current !== "judging") return;
      const strength = keyMap[event.key.toLowerCase()];
      if (strength && inputChoices.includes(strength)) {
        event.preventDefault();
        chooseAccent(strength);
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [inputChoices, round]);

  useEffect(() => () => {
    cancelPlayback();
  }, []);

  const primaryAction = stage === "idle" || stage === "complete" || stage === "audio_error"
    ? startListening
    : stage === "ready"
      ? startJudging
      : stage === "feedback"
        ? attemptEvaluation?.passed ? startMovement : startListening
        : stage === "movement" && movementFinished
          ? () => { stageRef.current = "complete"; setStage("complete"); setFeedback("练习完成：网页分数来自强弱拍判断；身体动作由你自己确认。\n"); }
          : undefined;
  const primaryLabel = stage === "idle" ? "开始练习：先听示范"
    : stage === "ready" ? "开始网页判断"
      : stage === "feedback" ? attemptEvaluation?.passed ? "开始身体律动" : "再听一次并重练"
        : stage === "movement" && movementFinished ? "我已完成身体律动"
          : stage === "complete" ? "再听一次并重练"
            : stage === "audio_error" ? "重新加载音色"
              : stage === "listening" ? "正在播放"
                : "正在判断";

  return (
    <main className="primary-activity-shell strong-weak-shell">
      <Container size="4" px="4">
        <section className="teacher-control-bar">
          <Flex align="center" justify="between" gap="3" wrap="wrap">
            <Flex align="center" gap="2" wrap="wrap">
              <Footprints size={18} />
              <Text weight="bold">强弱拍律动独立练习</Text>
              <Badge color="green" variant="soft">{meter}</Badge>
              <Badge color="amber" variant="soft">{bpm} BPM</Badge>
              <Badge color="blue" variant="soft">{stageLabel(stage)}</Badge>
            </Flex>
            <Flex align="end" gap="2" wrap="wrap">
              <label className="strong-weak-setting">
                <span>拍号</span>
                <select value={meter} onChange={(event) => handlePracticeSettingChange(event.currentTarget.value as StrongWeakMeter, bpm)} aria-label="选择拍号">
                  <option value="2/4">2/4</option>
                  <option value="3/4">3/4</option>
                  <option value="4/4">4/4</option>
                </select>
              </label>
              <label className="strong-weak-setting">
                <span>速度 BPM</span>
                <input
                  type="number"
                  min="50"
                  max="160"
                  step="1"
                  value={bpmDraft}
                  onChange={(event) => setBpmDraft(event.currentTarget.value)}
                  onBlur={applyBpmDraft}
                  onKeyDown={(event) => {
                    if (event.key === "Enter") event.currentTarget.blur();
                  }}
                  aria-label="设置速度 BPM"
                />
              </label>
              <Button variant="soft" color="gray" onClick={reset} aria-label="重置练习"><RotateCcw size={17} /></Button>
            </Flex>
          </Flex>
        </section>

        <Grid columns={{ initial: "1", md: "1.08fr .92fr" }} gap="4" className="activity-stage">
          <section className="activity-board strong-weak-board" aria-label="强弱拍独立练习">
            <Flex align="center" gap="2" wrap="wrap">
              <Badge color="green" variant="soft">{alignment.primary_competency ?? "艺术表现"}</Badge>
              {(alignment.music_elements ?? []).map((element) => <Badge key={element} color="amber" variant="soft">{element}</Badge>)}
            </Flex>
            <Heading as="h1" size="8" className="activity-title">强弱拍律动</Heading>
            <Text as="p" size="3" color="gray" className="activity-subtitle">先用网页判断强弱拍，再离开按钮做拍手、拍腿的身体律动。</Text>

            <div className="accent-circle-grid" aria-label="当前强弱拍">
              {round.map((beat, index) => (
                <div key={beat.id} className={`accent-orb ${beat.strength} ${index === activeIndex ? "active" : ""}`}>
                  <span>{beat.bar}-{beat.beatInBar}</span>
                  <strong>{beat.label}</strong>
                  <small>{stage === "movement" ? `身体：${beat.action}` : "网页判断拍位"}</small>
                </div>
              ))}
            </div>
            {stage === "count_in" && <p className="accent-count-in" role="status">预备拍 {countInBeat || 1}／{meter.slice(0, 1)}：只听节拍器，下一小节再开始判断。</p>}
          </section>

          <aside className="activity-side" aria-label="强弱拍练习操作区">
            <section className="primary-tool accent-action-panel">
              <Flex align="center" gap="2"><Hand size={20} /><Text weight="bold">{stage === "judging" ? "网页判断" : stage === "movement" ? "身体律动" : "当前步骤"}</Text></Flex>
              {showAccentChoices ? <>
                <p>{stage === "count_in" ? "预备拍：先看清下面按钮的位置；听到下一小节开始后再按。" : `当前是 ${activeBeat?.label ?? "强拍"}。只选择强弱拍，不需要拍手或拍腿。`}</p>
                <Grid columns={inputChoices.length === 3 ? "3" : "2"} gap="2">
                  {inputChoices.map((strength) => <button key={strength} type="button" disabled={stage !== "judging"} onClick={() => chooseAccent(strength)}>{inputLabels[strength]} <small>({strength === "strong" ? "F" : strength === "secondary" ? "G" : "H"})</small></button>)}
                </Grid>
              </> : stage === "movement" ? <p>{movementFinished ? "身体律动已播放完。确认自己完成后，点击下方主按钮结束。" : "现在离开按钮，只做身体动作：强拍拍手，弱拍拍腿，次强拍轻拍手。"}</p> : <p>{stage === "feedback" ? attemptEvaluation?.passed ? "网页判断已达到要求。现在再做身体动作。" : "本轮未达到要求，重新听示范后再练一次。" : "先听示范，再进入网页判断。"}</p>}
            </section>

            <section className="primary-tool accent-feedback">
              <Flex align="center" gap="2"><CheckCircle2 size={20} /><Text weight="bold">网页反馈</Text></Flex>
              <p>{feedback}</p>
              <div className="accent-summary-grid">
                <span>正确</span><strong>{summary.correct} 次</strong>
                <span>稍早／稍晚</span><strong>{summary.early + summary.late} 次</strong>
                <span>强弱选错</span><strong>{summary.wrongAccent} 次</strong>
                <span>漏拍／多按</span><strong>{summary.missing + summary.extra} 次</strong>
                <span>网页正确率</span><strong>{summary.accuracy} 分</strong>
              </div>
            </section>

            <section className="primary-tool classroom-prompts">
              <Text weight="bold">练习主操作</Text>
              <Button size="4" highContrast onClick={() => void primaryAction?.()} disabled={!primaryAction}><Play size={18} fill="currentColor" />{primaryLabel}</Button>
              <p>身体动作不由网页自动评分；网页只记录你对强弱拍和拍点时间的判断。</p>
            </section>
          </aside>
        </Grid>
      </Container>
    </main>
  );
}

function normalizeBpm(value: number) {
  return Math.max(50, Math.min(160, Math.round(Number(value) || 88)));
}

function stageLabel(stage: PracticeStage) {
  return ({ idle: "听示范", listening: "听示范", ready: "准备判断", count_in: "预备拍", judging: "网页判断", feedback: "查看反馈", movement: "身体律动", complete: "完成", audio_error: "音色异常" } as Record<PracticeStage, string>)[stage];
}
