import { Badge, Button, Container, Flex, Grid, Heading, Text } from "@radix-ui/themes";
import {
  AlertTriangle,
  CheckCircle2,
  ChevronRight,
  Ear,
  Hand,
  Headphones,
  ListMusic,
  Mic2,
  Music2,
  Play,
  RotateCcw,
  Settings2,
  Volume2,
} from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import { RhythmNotation } from "../music-components/RhythmNotation";
import {
  playHybridToneSequenceAsync,
  playLessonAudio,
  prepareSampledInstrument,
  stopActiveSampledPlayback,
} from "../shared/realAudio";
import {
  buildRhythmAudioEvents,
  resolveGradeTimingWindows,
  rhythmSequenceDurationMs,
} from "./rhythmWarmupLogic";
import {
  buildLyricsRhythmRecord,
  buildLyricsRhythmTimeline,
  canStartLyricsRhythmPhrase,
  evaluateLyricsRhythmAttempt,
  judgeLyricsRhythmTap,
  normalizeLyricsRhythmConfig,
  type LyricsRhythmConfigInput,
  type LyricsRhythmTapJudgement,
  type LyricsRhythmTeacherChecks,
} from "./lyricsRhythmJudgement";
import {
  classroomResultLabel,
  primaryActionForTrainingStage,
  shouldPlayTargetDuringRecording,
  type LyricsTrainingStage,
} from "./lyricsTrainingFlow";
import { formalRhythmName } from "./rhythmNaming";
import "./primaryActivity.css";
import { ReadableData } from "./ReadableData";

type LyricsRhythmState = {
  workflow?: {
    education_alignment?: {
      primary_competency?: string;
      music_elements?: string[];
      student_practices?: string[];
    };
  };
  config?: LyricsRhythmConfigInput & { teacher_confirm_required?: boolean };
};

declare global {
  interface Window {
    __LYRICS_RHYTHM_STATE__?: LyricsRhythmState;
  }
}

const defaultState: LyricsRhythmState = {
  workflow: {
    education_alignment: {
      primary_competency: "艺术表现",
      music_elements: ["歌词", "节奏", "节拍"],
      student_practices: ["listen", "read", "tap", "sing"],
    },
  },
  config: {
    version: "lyrics_rhythm_activity_v2",
    grade_preset: "lower_primary",
    practice_mode: "echo",
    example_material: true,
    phrases: [
      {
        id: "review-example-1",
        lyrics: "小雨沙沙",
        meter: "2/4",
        bpm: 84,
        patternIds: ["quarter", "eighth_pair", "quarter", "rest"],
        lyricUnits: [],
        source: "teacher_manual",
        teacherConfirmed: true,
      },
      {
        id: "review-example-2",
        lyrics: "种子发芽",
        meter: "2/4",
        bpm: 96,
        patternIds: ["eighth_pair", "quarter", "eighth_pair", "quarter"],
        lyricUnits: [],
        source: "teacher_manual",
        teacherConfirmed: true,
      },
    ],
  },
};

const EMPTY_TEACHER_CHECKS: LyricsRhythmTeacherChecks = { readingCorrect: false, singingMeetsGoal: false };
const SOUNDFONT_PREPARE_TIMEOUT_MS = 8000;

export function LyricsRhythmActivity({ state = window.__LYRICS_RHYTHM_STATE__ ?? defaultState }: { state?: LyricsRhythmState }) {
  const resolved = useMemo(() => normalizeLyricsRhythmConfig(state.config ?? {}), [state.config]);
  const phrases = resolved.phrases;
  const alignment = state.workflow?.education_alignment ?? defaultState.workflow?.education_alignment ?? {};
  const [activeIndex, setActiveIndex] = useState(0);
  const [stage, setStage] = useState<LyricsTrainingStage>("idle");
  const [passed, setPassed] = useState<boolean[]>(() => phrases.map(() => false));
  const [teacherChecks, setTeacherChecks] = useState<LyricsRhythmTeacherChecks[]>(() => phrases.map(() => ({ ...EMPTY_TEACHER_CHECKS })));
  const [tapJudgements, setTapJudgements] = useState<LyricsRhythmTapJudgement[][]>(() => phrases.map(() => []));
  const [retryCounts, setRetryCounts] = useState<number[]>(() => phrases.map(() => 0));
  const [audioError, setAudioError] = useState("");
  const recordStartAtRef = useRef<number | null>(null);
  const timersRef = useRef<number[]>([]);
  const runIdRef = useRef(0);

  const activePhrase = phrases[activeIndex];
  const activeTeacherChecks = teacherChecks[activeIndex] ?? EMPTY_TEACHER_CHECKS;
  const activeTapJudgements = tapJudgements[activeIndex] ?? [];
  const phraseGate = activePhrase ? canStartLyricsRhythmPhrase(activePhrase) : { ok: false, reason: "缺少已确认谱面。" };
  const timeline = useMemo(
    () => activePhrase ? buildLyricsRhythmTimeline(activePhrase.patternIds, { bpm: activePhrase.bpm }) : [],
    [activePhrase]
  );
  const activeEvaluation = useMemo(() => activePhrase ? evaluateLyricsRhythmAttempt({
    phraseIndex: activeIndex,
    phrase: activePhrase,
    tapJudgements: activeTapJudgements,
    retryCount: retryCounts[activeIndex] ?? 0,
    teacherChecks: activeTeacherChecks,
    gradePreset: resolved.gradePreset,
  }) : null, [activeIndex, activePhrase, activeTapJudgements, activeTeacherChecks, resolved.gradePreset, retryCounts]);
  const activeRecord = useMemo(() => activePhrase ? buildLyricsRhythmRecord({
    phraseIndex: activeIndex,
    phrase: activePhrase,
    tapJudgements: activeTapJudgements,
    retryCount: retryCounts[activeIndex] ?? 0,
    teacherChecks: activeTeacherChecks,
    passConfirmed: passed[activeIndex] ?? false,
    gradePreset: resolved.gradePreset,
  }) : null, [activeIndex, activePhrase, activeTapJudgements, activeTeacherChecks, retryCounts, passed, resolved.gradePreset]);
  const completedCount = passed.filter(Boolean).length;
  const lastTap = activeTapJudgements[activeTapJudgements.length - 1];
  const isBusy = stage === "listening" || stage === "count_in" || stage === "recording";

  useEffect(() => () => {
    runIdRef.current += 1;
    cancelPractice(timersRef.current);
  }, []);
  useEffect(() => {
    runIdRef.current += 1;
    cancelPractice(timersRef.current);
    setStage(phraseGate.ok ? "idle" : "blocked");
    setAudioError("");
    recordStartAtRef.current = null;
  }, [activeIndex, phraseGate.ok]);

  const recordTap = () => {
    if (stage !== "recording" || recordStartAtRef.current === null || !activePhrase) return;
    const tapMs = performance.now() - recordStartAtRef.current;
    const judgement = judgeLyricsRhythmTap(tapMs, timeline, activeTapJudgements, {
      bpm: activePhrase.bpm,
      gradePreset: resolved.gradePreset,
    });
    setTapJudgements((current) => current.map((items, index) => index === activeIndex ? [...items, judgement] : items));
    void playHybridToneSequenceAsync([0], {
      instrument: "acoustic_grand_piano",
      baseMidi: 60,
      duration: 0.09,
      gain: 0.34,
      allowOscillatorFallback: false,
    });
  };

  useEffect(() => {
    if (stage !== "recording") return;
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.repeat || (event.code !== "Space" && event.code !== "Enter")) return;
      const target = event.target as HTMLElement | null;
      if (target?.closest("button, input, textarea, select, [contenteditable='true']")) return;
      event.preventDefault();
      recordTap();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [stage, activePhrase, activeTapJudgements, timeline, resolved.gradePreset]);

  const startListening = async () => {
    if (!activePhrase || !phraseGate.ok || isBusy) return;
    cancelPractice(timersRef.current);
    const runId = ++runIdRef.current;
    setAudioError("");
    setStage("listening");
    recordStartAtRef.current = null;
    if (activeTapJudgements.length || stage === "feedback") {
      setRetryCounts((current) => current.map((count, index) => index === activeIndex ? count + 1 : count));
    }
    setTapJudgements((current) => current.map((items, index) => index === activeIndex ? [] : items));

    const prepared = await prepareLyricsRhythmAudio();
    if (runIdRef.current !== runId) return;
    if (prepared.some((result) => !result.ok)) {
      setStage("audio_error");
      setAudioError("真实钢琴或节拍器音色加载失败，请重新加载音色。 ");
      return;
    }
    const result = await playHybridToneSequenceAsync([], {
      instrument: "acoustic_grand_piano",
      baseMidi: 60,
      gain: 0.62,
      allowOscillatorFallback: false,
      events: buildRhythmAudioEvents(timeline),
    });
    if (runIdRef.current !== runId) return;
    if (!result.ok) {
      setStage("audio_error");
      setAudioError("真实钢琴示范播放失败，请重新加载音色。 ");
      return;
    }
    const totalMs = rhythmSequenceDurationMs(activePhrase.patternIds, { bpm: activePhrase.bpm });
    scheduleTimer(timersRef.current, () => {
      if (runIdRef.current === runId) setStage("ready");
    }, totalMs + 180);
  };

  const startRecording = () => {
    if (!activePhrase || stage !== "ready") return;
    cancelPractice(timersRef.current);
    const runId = ++runIdRef.current;
    setStage("count_in");
    const beatMs = 60000 / activePhrase.bpm;
    const countInBeats = Math.max(1, Number(activePhrase.meter.split("/")[0]) || 2);
    const leadInMs = 100;
    const recordingDelayMs = leadInMs + countInBeats * beatMs + 160;
    const totalMs = rhythmSequenceDurationMs(activePhrase.patternIds, { bpm: activePhrase.bpm });
    const outerMs = resolveGradeTimingWindows(activePhrase.bpm, resolved.gradePreset).outerMs;
    recordStartAtRef.current = performance.now() + recordingDelayMs;

    const countInEvents = Array.from({ length: countInBeats }, (_, index) => ({
      offset: 0,
      start: (leadInMs + index * beatMs) / 1000,
      duration: 0.1,
    }));
    const playbackTasks = [playHybridToneSequenceAsync([], {
      instrument: "woodblock",
      baseMidi: 60,
      gain: 0.5,
      allowOscillatorFallback: false,
      events: countInEvents,
    })];
    if (shouldPlayTargetDuringRecording(resolved.practiceMode)) {
      playbackTasks.push(playHybridToneSequenceAsync([], {
        instrument: "acoustic_grand_piano",
        baseMidi: 60,
        gain: 0.62,
        allowOscillatorFallback: false,
        events: buildRhythmAudioEvents(timeline, { startMs: recordingDelayMs }),
      }));
    }
    void Promise.all(playbackTasks).then((results) => {
      if (runIdRef.current !== runId) return;
      if (results.some((result) => !result.ok)) {
        cancelPractice(timersRef.current);
        setStage("audio_error");
        setAudioError("课堂音色播放失败，本轮已取消，请重新加载音色。 ");
      }
    });
    scheduleTimer(timersRef.current, () => {
      if (runIdRef.current === runId) setStage("recording");
    }, recordingDelayMs);
    scheduleTimer(timersRef.current, () => {
      if (runIdRef.current === runId) setStage("feedback");
    }, recordingDelayMs + totalMs + outerMs);
  };

  const toggleTeacherCheck = (key: keyof LyricsRhythmTeacherChecks) => {
    setTeacherChecks((current) => current.map((checks, index) => (
      index === activeIndex ? { ...checks, [key]: !checks[key] } : checks
    )));
  };

  const advancePhrase = () => {
    if (stage !== "feedback" || !activeEvaluation?.finalPassAllowed) return;
    setPassed((current) => current.map((value, index) => index === activeIndex ? true : value));
    if (activeIndex < phrases.length - 1) setActiveIndex((index) => index + 1);
  };

  const reset = () => {
    runIdRef.current += 1;
    cancelPractice(timersRef.current);
    setActiveIndex(0);
    setStage(phrases[0] && canStartLyricsRhythmPhrase(phrases[0]).ok ? "idle" : "blocked");
    setPassed(phrases.map(() => false));
    setTeacherChecks(phrases.map(() => ({ ...EMPTY_TEACHER_CHECKS })));
    setTapJudgements(phrases.map(() => []));
    setRetryCounts(phrases.map(() => 0));
    setAudioError("");
    recordStartAtRef.current = null;
  };

  if (!activePhrase) return <MissingMaterial />;

  return (
    <main className="primary-activity-shell lyrics-rhythm-shell lyrics-classroom-shell">
      <Container size="4" px="4">
        <header className="teacher-control-bar lyrics-classroom-toolbar">
          <Flex align="center" justify="between" gap="3" wrap="wrap">
            <Flex align="center" gap="2" wrap="wrap">
              <ListMusic size={18} />
              <Heading as="h1" size="4">歌词节奏训练</Heading>
              <Badge color="green" variant="soft">乐句 {activeIndex + 1}/{phrases.length}</Badge>
              <Badge color="amber" variant="soft">{activePhrase.meter} · {activePhrase.bpm} BPM</Badge>
              <Badge color="teal" variant="soft">{resolved.practiceMode === "echo" ? "听后拍回" : "同步跟拍"}</Badge>
            </Flex>
            <Button variant="soft" color="gray" onClick={reset} aria-label="重置训练"><RotateCcw size={17} /> 重置</Button>
          </Flex>
        </header>

        <Grid columns={{ initial: "1", lg: "minmax(0, 1fr) 290px" }} gap="4" className="lyrics-classroom-layout">
          <section className="lyrics-training-console" aria-label="歌词节奏课堂训练台">
            <div className="lyrics-training-stepper" aria-label="训练步骤">
              <TrainingStep number="1" label="听示范" icon={<Ear size={20} />} active={stage === "idle" || stage === "listening" || stage === "audio_error"} done={!['idle', 'listening', 'audio_error', 'blocked'].includes(stage)} />
              <span className="lyrics-step-line" />
              <TrainingStep number="2" label="拍回来" icon={<Hand size={20} />} active={stage === "ready" || stage === "count_in" || stage === "recording"} done={stage === "feedback"} />
              <span className="lyrics-step-line" />
              <TrainingStep number="3" label="看反馈" icon={<CheckCircle2 size={20} />} active={stage === "feedback"} done={passed[activeIndex]} />
            </div>

            <div className="lyrics-classroom-phrase">
              <span>当前歌词</span>
              <strong>{activePhrase.lyrics}</strong>
              <small>{primaryActionForTrainingStage(stage)}</small>
            </div>

            <div className={`lyrics-classroom-stage stage-${stage} tap-${lastTap?.status ?? "idle"}`}>
              {stage === "idle" ? (
                <ClassroomAction icon={<Headphones size={34} />} label="开始训练：先听示范" hint="钢琴会完整示范本句节奏" onClick={() => void startListening()} />
              ) : null}
              {stage === "listening" ? <ListeningState /> : null}
              {stage === "ready" ? (
                <ClassroomAction icon={<Play size={34} />} label={resolved.practiceMode === "echo" ? "我准备好了，开始拍回" : "我准备好了，开始同步跟拍"} hint="先听一小节木鱼预备拍，再开始敲击" onClick={startRecording} />
              ) : null}
              {stage === "count_in" ? <CountInState meter={activePhrase.meter} /> : null}
              {stage === "recording" ? <RhythmPad lastTap={lastTap} onTap={recordTap} /> : null}
              {stage === "feedback" && activeEvaluation ? (
                <FeedbackPanel
                  evaluation={activeEvaluation}
                  teacherChecks={activeTeacherChecks}
                  onTeacherCheck={toggleTeacherCheck}
                  onRetry={() => void startListening()}
                  onAdvance={advancePhrase}
                  isLastPhrase={activeIndex === phrases.length - 1}
                />
              ) : null}
              {stage === "audio_error" ? (
                <div className="lyrics-audio-error-state">
                  <AlertTriangle size={38} />
                  <strong>音色没有准备好</strong>
                  <p>{audioError}</p>
                  <Button size="4" highContrast onClick={() => void startListening()}>重新加载音色</Button>
                </div>
              ) : null}
              {stage === "blocked" ? (
                <div className="lyrics-audio-error-state">
                  <AlertTriangle size={38} />
                  <strong>暂时不能开始训练</strong>
                  <p>{phraseGate.reason}</p>
                </div>
              ) : null}
            </div>

            <div className="lyrics-score-ribbon">
              <Flex align="center" justify="between" gap="2" wrap="wrap">
                <Text weight="bold">本句节奏谱</Text>
                {activePhrase.audioClip ? (
                  <Button variant="ghost" disabled={isBusy} onClick={() => void playLessonAudio(activePhrase.audioClip!.url, activePhrase.audioClip!.startSeconds * 1000)}>
                    <Music2 size={16} /> 听歌曲原句
                  </Button>
                ) : <Text size="1" color="gray">未绑定歌曲原音频</Text>}
              </Flex>
              <div className="lyrics-rhythm-strip lyrics-classroom-rhythm-strip" aria-label="本句节奏型">
                {activePhrase.patternIds.map((item, index) => (
                  <span key={`${item}-${index}`} className={item}>
                    <strong><RhythmNotation rhythm={item} /></strong>
                    <small>{formalRhythmName(item)}</small>
                  </span>
                ))}
              </div>
            </div>
          </section>

          <aside className="lyrics-classroom-side" aria-label="教师控制区">
            <section className="primary-tool phrase-list lyrics-list">
              <Flex align="center" gap="2"><Music2 size={18} /><Text weight="bold">歌曲乐句</Text></Flex>
              <div>
                {phrases.map((phrase, index) => (
                  <button key={phrase.id} type="button" disabled={isBusy} className={`${index === activeIndex ? "active" : ""} ${passed[index] ? "passed" : ""}`} onClick={() => setActiveIndex(index)}>
                    <span>{passed[index] ? "✓" : index + 1}</span><strong>{phrase.lyrics}</strong><small>{phrase.meter} · {phrase.bpm} BPM</small>
                  </button>
                ))}
              </div>
            </section>

            <details className="primary-tool lyrics-teacher-drawer">
              <summary><Settings2 size={18} /> 教师信息与审核记录</summary>
              <div className="lyrics-teacher-drawer-body">
                <p><strong>网页判断：</strong>点击时间、早晚、漏拍、多拍、休止和稳定度。</p>
                <p><strong>教师判断：</strong>歌词、咬字、音准、气息、乐句和表现。</p>
                <p><strong>材料：</strong>{resolved.usingExampleMaterial ? "组件审核示例" : sourceLabel(activePhrase.source)}</p>
                <p><strong>素养：</strong>{alignment.primary_competency ?? "艺术表现"}</p>
                {activeRecord ? <details className="lyrics-record-detail"><summary>本句活动记录</summary><ReadableData value={activeRecord} /></details> : null}
              </div>
            </details>
          </aside>
        </Grid>
      </Container>
    </main>
  );
}

function TrainingStep({ number, label, icon, active, done }: { number: string; label: string; icon: React.ReactNode; active: boolean; done: boolean }) {
  return <div className={`lyrics-training-step ${active ? "active" : ""} ${done ? "done" : ""}`}><span>{done ? <CheckCircle2 size={20} /> : number}</span>{icon}<strong>{label}</strong></div>;
}

function ClassroomAction({ icon, label, hint, onClick }: { icon: React.ReactNode; label: string; hint: string; onClick: () => void }) {
  return (
    <div className="lyrics-classroom-primary-action">
      <Button size="4" highContrast onClick={onClick}>{icon}<span>{label}<small>{hint}</small></span><ChevronRight size={30} /></Button>
    </div>
  );
}

function ListeningState() {
  return <div className="lyrics-listening-state"><span className="lyrics-listening-pulse"><Volume2 size={42} /></span><strong>安静听完整示范</strong><p>先把节奏听进心里，播放结束后再拍。</p></div>;
}

function CountInState({ meter }: { meter: string }) {
  return <div className="lyrics-count-in-state"><span>{Number(meter.split("/")[0]) || 2}</span><strong>听木鱼预备拍</strong><p>预备拍结束后，大节奏垫会自动亮起。</p></div>;
}

function RhythmPad({ lastTap, onTap }: { lastTap?: LyricsRhythmTapJudgement; onTap: () => void }) {
  return (
    <button type="button" className={`lyrics-giant-rhythm-pad ${lastTap?.status ?? "idle"}`} onClick={onTap} aria-label="按当前乐句实际音头敲击">
      <Hand size={58} />
      <strong>拍一下</strong>
      <span>{tapMessage(lastTap)}</span>
      <small>触屏点击，也可以按空格键</small>
    </button>
  );
}

function FeedbackPanel({ evaluation, teacherChecks, onTeacherCheck, onRetry, onAdvance, isLastPhrase }: {
  evaluation: NonNullable<ReturnType<typeof evaluateLyricsRhythmAttempt>>;
  teacherChecks: LyricsRhythmTeacherChecks;
  onTeacherCheck: (key: keyof LyricsRhythmTeacherChecks) => void;
  onRetry: () => void;
  onAdvance: () => void;
  isLastPhrase: boolean;
}) {
  const correct = evaluation.attemptResult === "correct";
  return (
    <div className={`lyrics-feedback-panel result-${evaluation.attemptResult}`}>
      <div className="lyrics-feedback-hero"><CheckCircle2 size={34} /><div><span>本轮反馈</span><strong>{classroomResultLabel(evaluation.attemptResult)}</strong><p>{evaluation.webSuggestion}</p></div><em>{evaluation.tapSummary.score}</em></div>
      <div className="lyrics-feedback-stats">
        <span><strong>{evaluation.tapSummary.correctCount}</strong>正确</span>
        <span><strong>{evaluation.tapSummary.earlyCount}</strong>偏早</span>
        <span><strong>{evaluation.tapSummary.lateCount}</strong>偏晚</span>
        <span><strong>{evaluation.tapSummary.missedCount}</strong>漏拍</span>
        <span><strong>{evaluation.tapSummary.extraCount}</strong>多拍</span>
        <span><strong>{evaluation.tapSummary.restErrorCount}</strong>休止误拍</span>
      </div>
      {correct ? (
        <div className="lyrics-feedback-teacher-gate">
          <Text weight="bold">请教师完成音乐表现确认</Text>
          <div className="lyrics-teacher-checks">
            <Button variant={teacherChecks.readingCorrect ? "solid" : "soft"} color={teacherChecks.readingCorrect ? "green" : "gray"} onClick={() => onTeacherCheck("readingCorrect")}><CheckCircle2 size={17} /> 教师确认：歌词朗读正确</Button>
            <Button variant={teacherChecks.singingMeetsGoal ? "solid" : "soft"} color={teacherChecks.singingMeetsGoal ? "green" : "gray"} onClick={() => onTeacherCheck("singingMeetsGoal")}><Mic2 size={17} /> 教师确认：回唱达到要求</Button>
          </div>
          <Flex gap="2" wrap="wrap">
            <Button variant="soft" onClick={onRetry}><Headphones size={17} /> 再练一次</Button>
            <Button highContrast onClick={onAdvance} disabled={!evaluation.finalPassAllowed}>{isLastPhrase ? "完成当前乐句" : "进入下一句"}<ChevronRight size={18} /></Button>
          </Flex>
        </div>
      ) : (
        <div className="lyrics-feedback-actions"><Button size="4" highContrast onClick={onRetry}><Headphones size={20} /> 再听一次并重练</Button></div>
      )}
    </div>
  );
}

function MissingMaterial() {
  return <main className="primary-activity-shell lyrics-rhythm-shell"><Container size="3" px="4"><section className="primary-tool teacher-confirm-card lyrics-material-blocked"><AlertTriangle size={24} /><Heading as="h1" size="6">缺少已确认谱面</Heading><Text color="gray">请由智能体绑定教师提供的歌词与 MusicXML、MIDI 或教师确认节奏。系统不会用示例歌词替代正式歌曲。</Text></section></Container></main>;
}

function scheduleTimer(timers: number[], callback: () => void, delayMs: number) {
  timers.push(window.setTimeout(callback, Math.max(0, delayMs)));
}

async function prepareLyricsRhythmAudio(): Promise<Array<{ ok: boolean; error?: string }>> {
  let timeoutId = 0;
  const timeout = new Promise<Array<{ ok: boolean; error?: string }>>((resolve) => {
    timeoutId = window.setTimeout(() => resolve([{ ok: false, error: "SoundFont preparation timed out" }]), SOUNDFONT_PREPARE_TIMEOUT_MS);
  });
  try {
    return await Promise.race([
      Promise.all([
        prepareSampledInstrument("woodblock", { audition: false }),
        prepareSampledInstrument("acoustic_grand_piano", { audition: false }),
      ]),
      timeout,
    ]);
  } finally {
    window.clearTimeout(timeoutId);
  }
}

function cancelPractice(timers: number[]) {
  timers.splice(0).forEach((timer) => window.clearTimeout(timer));
  stopActiveSampledPlayback();
}

function sourceLabel(source: string) {
  if (source === "musicxml") return "MusicXML 谱面";
  if (source === "midi") return "MIDI 谱面";
  if (source === "teacher_manual") return "教师确认材料";
  return "待教师确认草稿";
}

function tapMessage(lastTap?: LyricsRhythmTapJudgement) {
  if (!lastTap) return "跟着心里的节奏连续拍";
  if (lastTap.status === "correct") return "准";
  if (lastTap.status === "early") return "稍早";
  if (lastTap.status === "late") return "稍晚";
  if (lastTap.status === "rest_error") return "休止处要停";
  return "多拍了一下";
}
