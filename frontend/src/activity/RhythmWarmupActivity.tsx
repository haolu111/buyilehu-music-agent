import { Badge, Box, Button, Container, Flex, Grid, Heading, Text } from "@radix-ui/themes";
import { BookOpenCheck, CheckCircle2, Footprints, GraduationCap, Sparkles } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import { AudioPlayer } from "../music-components/AudioPlayer";
import { MeterTrack } from "../music-components/MeterTrack";
import { RhythmCardBank } from "../music-components/RhythmCardBank";
import { RhythmPad } from "../music-components/RhythmPad";
import { TapFeedback } from "../music-components/TapFeedback";
import { TeacherControlBar } from "../music-components/TeacherControlBar";
import { playHybridToneSequenceAsync, prepareSampledInstrument, stopActiveSampledPlayback } from "../shared/realAudio";
import {
  getRhythmPatternDefinition,
  resolveRhythmExerciseInput,
  type RhythmExerciseInput,
  type ResolvedRhythmExercise,
} from "../shared/rhythmPatternCatalog";
import { formalRhythmLabel, formalRhythmName } from "./rhythmNaming";
import {
  buildBeatTimeline,
  buildDefaultRhythmWarmupToolkit,
  buildRhythmAudioEvents,
  buildRhythmPerformanceTimeline,
  buildRhythmWarmupAttemptRecord,
  evaluateRhythmAttempt,
  judgeRhythmPerformanceTap,
  normalizeRhythmCards,
  resolveGradeTimingWindows,
  rhythmSequenceDurationMs,
  type GradePreset,
  type PracticeMode,
  type PrimaryMeter,
  type RhythmAttemptSummary,
  type RhythmTapJudgement,
} from "./rhythmWarmupLogic";

type AttemptPhase = "idle" | "loading" | "demonstrating" | "count_in" | "recording" | "finished" | "error";

type RhythmWarmupActivityProps = {
  exerciseInput?: RhythmExerciseInput;
};

const TEACHER_EXAMPLE: RhythmExerciseInput = {
  patternIds: ["quarter", "eighth_pair", "rest", "sixteenth_four", "eighth_sixteenth_sixteenth", "sixteenth_sixteenth_eighth", "quarter", "eighth_pair"],
  meter: "2/4",
  gradePreset: "middle_primary",
  bpm: 92,
  mode: "echo",
};

export function RhythmWarmupActivity({ exerciseInput }: RhythmWarmupActivityProps = {}) {
  const toolkit = useMemo(() => buildDefaultRhythmWarmupToolkit(), []);
  const initialInput = exerciseInput ?? TEACHER_EXAMPLE;
  const [bpm, setBpm] = useState(initialInput.bpm);
  const [meter, setMeter] = useState<PrimaryMeter>(initialInput.meter);
  const [repeatCount, setRepeatCount] = useState(toolkit.teacherControls.repeatCount);
  const [gradePreset, setGradePreset] = useState<GradePreset>(initialInput.gradePreset);
  const [practiceMode, setPracticeMode] = useState<PracticeMode>(initialInput.mode);
  const [materialMode, setMaterialMode] = useState<"teacher" | "random">(
    initialInput.patternIds?.length || initialInput.allowedPatternIds?.length ? "teacher" : "random"
  );
  const [question, setQuestion] = useState<ResolvedRhythmExercise>(() => resolveRhythmExerciseInput(initialInput));
  const [phase, setPhase] = useState<AttemptPhase>("idle");
  const [elapsedMs, setElapsedMs] = useState(0);
  const [judgements, setJudgements] = useState<RhythmTapJudgement[]>([]);
  const [lastJudgement, setLastJudgement] = useState<RhythmTapJudgement>();
  const [finalSummary, setFinalSummary] = useState<RhythmAttemptSummary>();
  const [audioError, setAudioError] = useState("");
  const recordStartAtRef = useRef(0);
  const phaseRef = useRef<AttemptPhase>("idle");
  const judgementsRef = useRef<RhythmTapJudgement[]>([]);
  const timersRef = useRef<number[]>([]);
  const rhythmAudioReadyRef = useRef(false);

  const patternIds = question.patternIds;
  const cards = useMemo(() => normalizeRhythmCards(patternIds.map(rhythmCardInput), bpm), [bpm, patternIds]);
  const meterTimeline = useMemo(() => buildBeatTimeline(cards, { bpm, meter, repeatCount }), [bpm, cards, meter, repeatCount]);
  const performanceTimeline = useMemo(
    () => buildRhythmPerformanceTimeline(patternIds, { bpm, repeatCount }),
    [bpm, repeatCount]
  );
  const totalMs = useMemo(() => rhythmSequenceDurationMs(patternIds, { bpm, repeatCount }), [bpm, repeatCount]);
  const activeEvent = meterTimeline.find((event) => elapsedMs >= event.startMs && elapsedMs < event.startMs + event.durationMs);
  const liveSummary = useMemo(
    () => evaluateRhythmAttempt(performanceTimeline, judgements, { bpm, gradePreset }),
    [bpm, gradePreset, judgements, performanceTimeline]
  );
  const summary = finalSummary ?? liveSummary;
  const attemptRecord = phase === "finished"
    ? buildRhythmWarmupAttemptRecord({ gradePreset, practiceMode, bpm, meter, repeatCount, patternIds, timeline: performanceTimeline, judgements })
    : undefined;
  const active = ["loading", "demonstrating", "count_in", "recording"].includes(phase);
  const inputError = question.ok ? "" : question.error || "节奏素材无法使用";

  useEffect(() => {
    if (phase !== "recording") return undefined;
    const ticker = window.setInterval(() => {
      setElapsedMs(Math.max(0, Math.min(totalMs, performance.now() - recordStartAtRef.current)));
    }, 24);
    return () => window.clearInterval(ticker);
  }, [phase, totalMs]);

  useEffect(() => () => {
    clearScheduledTimers(timersRef.current);
    stopActiveSampledPlayback();
  }, []);

  const transitionTo = (nextPhase: AttemptPhase) => {
    phaseRef.current = nextPhase;
    setPhase(nextPhase);
  };

  const clearAttemptState = () => {
    setElapsedMs(0);
    setJudgements([]);
    judgementsRef.current = [];
    setLastJudgement(undefined);
    setFinalSummary(undefined);
    setAudioError("");
  };

  const resetActivity = () => {
    clearScheduledTimers(timersRef.current);
    stopActiveSampledPlayback();
    clearAttemptState();
    transitionTo("idle");
  };

  const prepareRhythmAudio = async () => {
    if (rhythmAudioReadyRef.current) return true;
    const result = await Promise.race([
      Promise.all([
        prepareSampledInstrument("acoustic_grand_piano", { audition: false }),
        prepareSampledInstrument("woodblock", { audition: false }),
      ]),
      new Promise<Awaited<ReturnType<typeof prepareSampledInstrument>>[]>((resolve) => {
        window.setTimeout(() => resolve([{ ok: false, source: "failed", error: "SoundFont preparation timed out" }]), 8000);
      }),
    ]);
    rhythmAudioReadyRef.current = result.every((item) => item.ok);
    return rhythmAudioReadyRef.current;
  };

  const finishAttempt = () => {
    if (phaseRef.current !== "recording") return;
    const nextSummary = evaluateRhythmAttempt(performanceTimeline, judgementsRef.current, { bpm, gradePreset });
    setElapsedMs(totalMs);
    setFinalSummary(nextSummary);
    transitionTo("finished");
  };

  const beginRecording = async (playTarget: boolean) => {
    const beatMs = 60000 / bpm;
    const countInBeats = Number(meter.split("/")[0]) || 2;
    const leadInMs = 160;
    const countInMs = countInBeats * beatMs;
    const recordingDelayMs = Math.round(leadInMs + countInMs);
    const scheduleStartedAt = performance.now();
    transitionTo("count_in");
    const result = await playPracticeAudio({
      timeline: performanceTimeline,
      beatMs,
      countInBeats,
      leadInMs,
      recordingDelayMs,
      playTarget,
    });
    if (!result.ok) {
      setAudioError("真实钢琴采样未加载，练习没有开始。请检查声音资源后重试。");
      transitionTo("error");
      return;
    }
    recordStartAtRef.current = scheduleStartedAt + recordingDelayMs;
    scheduleTimer(timersRef.current, () => transitionTo("recording"), recordingDelayMs);
    const outerMs = resolveGradeTimingWindows(bpm, gradePreset).outerMs;
    scheduleTimer(timersRef.current, finishAttempt, recordingDelayMs + totalMs + outerMs);
  };

  const startPractice = async () => {
    if (!question.ok) return;
    if (active) {
      resetActivity();
      return;
    }
    resetActivity();
    transitionTo("loading");
    const ready = await prepareRhythmAudio();
    if (!ready) {
      setAudioError("真实钢琴采样未加载，练习没有开始。请检查声音资源后重试。");
      transitionTo("error");
      return;
    }
    if (practiceMode === "echo") {
      transitionTo("demonstrating");
      const demoLeadInMs = 160;
      const demoResult = await playTargetAudio(performanceTimeline, demoLeadInMs);
      if (!demoResult.ok) {
        setAudioError("示范音频加载失败，未进入回拍阶段。");
        transitionTo("error");
        return;
      }
      scheduleTimer(timersRef.current, () => void beginRecording(false), demoLeadInMs + totalMs + 520);
      return;
    }
    await beginRecording(true);
  };

  const handleTap = (timestampMs: number) => {
    if (phaseRef.current !== "recording") return;
    const tapMs = Math.round(timestampMs - recordStartAtRef.current);
    const nextJudgement = judgeRhythmPerformanceTap(tapMs, performanceTimeline, judgementsRef.current, { bpm, gradePreset });
    const nextJudgements = [...judgementsRef.current, nextJudgement];
    judgementsRef.current = nextJudgements;
    setJudgements(nextJudgements);
    setLastJudgement(nextJudgement);
    void playRhythmTap();
  };

  const updateAndReset = <T,>(setter: (value: T) => void, value: T) => {
    resetActivity();
    setter(value);
  };

  const updateQuestionContext = (nextGrade: GradePreset, nextMeter: PrimaryMeter) => {
    resetActivity();
    setGradePreset(nextGrade);
    setMeter(nextMeter);
    setMaterialMode("random");
    setQuestion(resolveRhythmExerciseInput({ gradePreset: nextGrade, meter: nextMeter, bpm, mode: practiceMode }));
  };

  const drawNewQuestion = () => {
    resetActivity();
    setMaterialMode("random");
    setQuestion(resolveRhythmExerciseInput({ gradePreset, meter, bpm, mode: practiceMode, previousPatternIds: patternIds }));
  };

  const showTeacherExample = () => {
    resetActivity();
    setBpm(TEACHER_EXAMPLE.bpm);
    setMeter(TEACHER_EXAMPLE.meter);
    setGradePreset(TEACHER_EXAMPLE.gradePreset);
    setPracticeMode(TEACHER_EXAMPLE.mode);
    setMaterialMode("teacher");
    setQuestion(resolveRhythmExerciseInput(TEACHER_EXAMPLE));
  };

  return (
    <main className="primary-activity-shell rhythm-warmup-shell" data-attempt-phase={phase} data-attempt-result={finalSummary?.result || "pending"}>
      <Container size="4" px="4">
        <TeacherControlBar
          bpm={bpm}
          meter={meter}
          repeatCount={repeatCount}
          gradePreset={gradePreset}
          practiceMode={practiceMode}
          onBpmChange={(value) => updateAndReset(setBpm, value)}
          onMeterChange={(value) => updateQuestionContext(gradePreset, value)}
          onRepeatChange={(value) => updateAndReset(setRepeatCount, value)}
          onGradePresetChange={(value) => updateQuestionContext(value, meter)}
          onPracticeModeChange={(value) => updateAndReset(setPracticeMode, value)}
          onReset={resetActivity}
        />

        <Grid columns={{ initial: "1", md: "1.15fr .85fr" }} gap="4" className="activity-stage">
          <section className="activity-board" aria-label="小学节奏热身活动">
            <Flex align="start" justify="between" gap="4" wrap="wrap" className="activity-title-row">
              <Box>
                <Flex align="center" gap="2" wrap="wrap">
                  <Badge color="green" variant="soft">{gradePresetLabel(gradePreset)}</Badge>
                  <Badge color="amber" variant="soft">{practiceMode === "play_along" ? "跟拍模式" : "听后回拍"}</Badge>
                </Flex>
                <Heading as="h1" size="8" className="activity-title">{toolkit.title}</Heading>
                <Text as="p" size="3" color="gray" className="activity-subtitle">
                  每个内部音头独立判定，明确反馈正确、早晚、漏拍、多拍和休止误拍。
                </Text>
              </Box>
              <Flex className="activity-flow" gap="2" wrap="wrap">
                {(practiceMode === "play_along" ? ["听预备拍", "同步跟拍", "查看正误", "调整重练"] : ["听完整示范", "听预备拍", "独立回拍", "查看正误"]).map((step, index) => (
                  <span key={step}>{index + 1}. {step}</span>
                ))}
              </Flex>
            </Flex>

            <Grid columns={{ initial: "1", sm: "1fr 1fr" }} gap="3">
              <AudioPlayer
                playing={active}
                bpm={bpm}
                onToggle={() => void startPractice()}
                onPreviewPulse={() => void playRhythmTap()}
                actionLabel={practiceMode === "play_along" ? "开始跟拍" : "开始听后回拍"}
                activeLabel="取消本轮"
                statusText={phaseLabel(phase, bpm)}
                disabled={phase === "loading" || !question.ok}
              />
              <TapFeedback judgement={lastJudgement} score={summary.score} tapCount={judgements.length} />
            </Grid>

            <MeterTrack events={meterTimeline} elapsedMs={elapsedMs} totalMs={totalMs} />
            <RhythmCardBank cards={cards} activeCardId={activeEvent?.cardId} />
            <Flex gap="2" wrap="wrap" mt="3">
              {!exerciseInput ? (
                <>
                  <Button variant={materialMode === "teacher" ? "solid" : "soft"} color="amber" onClick={showTeacherExample} disabled={active}>教师指定示例</Button>
                  <Button variant={materialMode === "random" ? "solid" : "soft"} color="gray" onClick={drawNewQuestion} disabled={active}>随机兜底</Button>
                </>
              ) : null}
              <Button variant="soft" color="gray" onClick={resetActivity} disabled={active}>重练当前题</Button>
              {materialMode === "random" ? <Button variant="solid" color="green" onClick={drawNewQuestion} disabled={active}>再来一组</Button> : null}
              <Text size="2" color={question.ok ? "gray" : "red"}>
                {question.ok ? `${question.barCount} 小节 · ${materialSourceLabel(question.source)}` : inputError}
              </Text>
            </Flex>
          </section>

          <aside className="activity-side" aria-label="课堂操作区">
            <RhythmPad disabled={phase !== "recording"} onTap={handleTap} />

            <section className={`primary-tool rhythm-attempt-result ${finalSummary?.result || phase}`} aria-label="整轮节奏判定">
              <Flex align="center" justify="between" gap="3" wrap="wrap">
                <div>
                  <Text weight="bold">网页节奏判定</Text>
                  <p className="rhythm-attempt-state">{finalSummary ? resultLabel(finalSummary.result) : attemptInstruction(phase, practiceMode)}</p>
                </div>
                <Badge color={resultColor(finalSummary?.result)} variant="soft" data-score={summary.score}>{summary.score} 分</Badge>
              </Flex>
              <div className="rhythm-result-grid">
                <span>目标音头<strong>{summary.expectedHitCount}</strong></span>
                <span>正确<strong>{summary.correctCount}</strong></span>
                <span>偏早<strong>{summary.earlyCount}</strong></span>
                <span>偏晚<strong>{summary.lateCount}</strong></span>
                <span>漏拍<strong>{finalSummary ? summary.missedCount : "--"}</strong></span>
                <span>多拍<strong>{summary.extraCount}</strong></span>
                <span>休止误拍<strong>{summary.restErrorCount}</strong></span>
              </div>
              {finalSummary ? <p className="rhythm-teacher-suggestion">{finalSummary.teacherSuggestion}</p> : null}
              {audioError ? <p className="rhythm-audio-error">{audioError}</p> : null}
              {attemptRecord ? (
                <details className="rhythm-attempt-record">
                  <summary>查看本轮判定记录</summary>
                  <pre>{JSON.stringify(attemptRecord, null, 2)}</pre>
                </details>
              ) : null}
            </section>

            <section className={`primary-tool steady-beat-check ${summary.stability.status}`}>
              <Text weight="bold">节奏稳定度</Text>
              <div className="steady-beat-grid">
                <span>已匹配音头</span>
                <strong>{summary.stability.matchedTapCount} 次</strong>
                <span>平均间隔误差</span>
                <strong>{summary.stability.matchedTapCount >= 3 ? `${summary.stability.averageAbsoluteIntervalErrorMs} ms` : "--"}</strong>
                <span>间隔误差范围</span>
                <strong>{summary.stability.matchedTapCount >= 3 ? `${summary.stability.intervalErrorRangeMs} ms` : "--"}</strong>
              </div>
              <p>{stabilityLabel(summary.stability.status)}</p>
            </section>

            <section className="primary-tool classroom-kit">
              <Flex align="center" gap="2"><BookOpenCheck size={18} /><Text weight="bold">判定依据</Text></Flex>
              <div className="kit-list">
                <span>内部音头时间线</span><span>一对一匹配</span><span>年级时间窗</span><span>休止保护</span>
              </div>
            </section>

            <section className="primary-tool classroom-prompts">
              <Flex align="center" gap="2"><GraduationCap size={18} /><Text weight="bold">教师提示</Text></Flex>
              <p><Sparkles size={15} />先保持当前速度完成正确，再逐步加速或隐藏节奏卡。</p>
              <p><Footprints size={15} />网页只判断敲击时间；动作质量、力度和音乐表现仍由教师观察。</p>
              {finalSummary?.result === "correct" ? <p><CheckCircle2 size={15} />本轮正确，可换动作或提高难度。</p> : null}
            </section>
          </aside>
        </Grid>
      </Container>
    </main>
  );
}

function rhythmCardInput(id: string, index: number) {
  const definition = getRhythmPatternDefinition(id);
  return {
    id: `${index + 1}-${id}`,
    patternId: id,
    label: formalRhythmName(id),
    syllable: formalRhythmLabel(id),
    beats: definition.durationBeats,
    hitRequired: definition.hitOffsetsBeats.length > 0,
    subdivisions: Math.max(1, definition.hitOffsetsBeats.length),
    gesture: definition.hitOffsetsBeats.length ? "拍手" : "停住",
  };
}

function materialSourceLabel(source: ResolvedRhythmExercise["source"]) {
  if (source === "teacher_sequence") return "教师指定序列";
  if (source === "teacher_pool") return "教师限定范围";
  return "已审核节奏型库随机兜底";
}

async function playPracticeAudio(input: {
  timeline: ReturnType<typeof buildRhythmPerformanceTimeline>;
  beatMs: number;
  countInBeats: number;
  leadInMs: number;
  recordingDelayMs: number;
  playTarget: boolean;
}) {
  const countInEvents = Array.from({ length: input.countInBeats }, (_, index) => ({
    offset: 0,
    start: (input.leadInMs + index * input.beatMs) / 1000,
    duration: 0.1,
  }));
  const targetEvents = input.playTarget
    ? buildRhythmAudioEvents(input.timeline, { startMs: input.recordingDelayMs })
    : [];
  const results = await Promise.all([
    playHybridToneSequenceAsync([], {
      instrument: "woodblock",
      baseMidi: 60,
      gain: 0.5,
      allowOscillatorFallback: false,
      events: countInEvents,
    }),
    ...(targetEvents.length ? [playHybridToneSequenceAsync([], {
      instrument: "acoustic_grand_piano",
      baseMidi: 60,
      gain: 0.62,
      allowOscillatorFallback: false,
      events: targetEvents,
    })] : []),
  ]);
  return results.find((result) => !result.ok) ?? results[0];
}

function playTargetAudio(timeline: ReturnType<typeof buildRhythmPerformanceTimeline>, leadInMs: number) {
  return playHybridToneSequenceAsync([], {
    instrument: "acoustic_grand_piano",
    baseMidi: 60,
    gain: 0.62,
    allowOscillatorFallback: false,
    events: buildRhythmAudioEvents(timeline, { startMs: leadInMs }),
  });
}

function playRhythmTap() {
  return playHybridToneSequenceAsync([0], {
    instrument: "acoustic_grand_piano",
    baseMidi: 60,
    duration: 0.08,
    gain: 0.46,
    allowOscillatorFallback: false,
  });
}

function scheduleTimer(timers: number[], callback: () => void, delayMs: number) {
  const timer = window.setTimeout(callback, Math.max(0, delayMs));
  timers.push(timer);
}

function clearScheduledTimers(timers: number[]) {
  timers.splice(0).forEach((timer) => window.clearTimeout(timer));
}

function gradePresetLabel(preset: GradePreset) {
  if (preset === "lower_primary") return "小学低段";
  if (preset === "upper_primary") return "小学高段";
  return "小学中段";
}

function phaseLabel(phase: AttemptPhase, bpm: number) {
  if (phase === "loading") return "正在加载真实钢琴采样";
  if (phase === "demonstrating") return "正在播放完整示范";
  if (phase === "count_in") return "听预备拍，暂时不要敲击";
  if (phase === "recording") return "正在录入并判定";
  if (phase === "finished") return "本轮已经完成";
  if (phase === "error") return "声音资源加载失败";
  return `${bpm} BPM · 点击开始练习`;
}

function attemptInstruction(phase: AttemptPhase, mode: PracticeMode) {
  if (phase === "loading") return "正在准备真实采样……";
  if (phase === "demonstrating") return "先听完整节奏，示范结束后再回拍。";
  if (phase === "count_in") return "听预备拍，进入录入后节奏垫才会启用。";
  if (phase === "recording") return mode === "play_along" ? "现在跟着目标节奏敲击。" : "现在把刚才听到的节奏拍回来。";
  if (phase === "error") return "本轮没有开始，请检查声音资源。";
  return "点击开始后，网页会给出每次敲击和整轮正误反馈。";
}

function resultLabel(result: RhythmAttemptSummary["result"]) {
  if (result === "correct") return "正确通过";
  if (result === "adjust") return "基本正确需调整";
  return "错误需重练";
}

function resultColor(result?: RhythmAttemptSummary["result"]): "green" | "amber" | "red" | "gray" {
  if (result === "correct") return "green";
  if (result === "adjust") return "amber";
  if (result === "retry") return "red";
  return "gray";
}

function stabilityLabel(status: RhythmAttemptSummary["stability"]["status"]) {
  if (status === "stable") return "音头之间的实际间隔与目标节奏基本一致。";
  if (status === "rushing") return "节奏间隔逐渐缩短，整体有加快倾向。";
  if (status === "dragging") return "节奏间隔逐渐拉长，整体有放慢倾向。";
  if (status === "unstable") return "音头间隔不均，建议降低速度并拆分练习。";
  return "至少匹配 3 个音头后，再判断节奏稳定度。";
}
