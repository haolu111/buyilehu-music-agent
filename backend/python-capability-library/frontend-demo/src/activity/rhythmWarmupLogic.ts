import { formalRhythmLabel, formalRhythmName } from "./rhythmNaming";
import { buildRhythmPatternTimeline, getRhythmPatternDefinition } from "../shared/rhythmPatternCatalog";

export type PrimaryMeter = "2/4" | "3/4" | "4/4";

export type RhythmCardInput = {
  id: string;
  patternId?: string;
  label: string;
  syllable: string;
  beats: number;
  hitRequired?: boolean;
  subdivisions?: number;
  gesture?: string;
  color?: string;
};

export type RhythmCard = Required<Pick<RhythmCardInput, "id" | "label" | "syllable" | "beats" | "hitRequired" | "subdivisions">> & {
  patternId: string;
  durationMs: number;
  gesture: string;
  color: string;
};

export type BeatTimelineEvent = {
  id: string;
  cardId: string;
  patternId: string;
  label: string;
  syllable: string;
  startMs: number;
  durationMs: number;
  bar: number;
  beatInBar: number;
  hitRequired: boolean;
  color: string;
};

export type BeatTimelineOptions = {
  bpm?: number;
  meter?: PrimaryMeter;
  repeatCount?: number;
};

export type TapTimingStatus = "on_time" | "early" | "late" | "rest" | "miss";

export type TapTimingJudgement = {
  status: TapTimingStatus;
  nearestEvent?: BeatTimelineEvent;
  offsetMs?: number;
  accuracy: number;
  message: string;
};

export type GradePreset = "lower_primary" | "middle_primary" | "upper_primary";
export type PracticeMode = "play_along" | "echo";
export type RhythmTapStatus = "correct" | "early" | "late" | "extra" | "rest_error";
export type RhythmAttemptResult = "correct" | "adjust" | "retry";

export type RhythmPerformanceTimelineEvent = {
  id: string;
  kind: "hit" | "rest";
  rhythmId: string;
  repeatIndex: number;
  patternIndex: number;
  hitIndex: number;
  targetMs: number;
  endMs?: number;
};

export type RhythmAudioEvent = {
  patternId: string;
  offset: 0;
  start: number;
  duration: number;
};

export type RhythmTapJudgement = {
  id: string;
  status: RhythmTapStatus;
  tapMs: number;
  targetEventId?: string;
  targetMs?: number;
  offsetMs?: number;
  message: string;
};

export type RhythmPerformanceStability = {
  status: TempoStabilityStatus;
  matchedTapCount: number;
  averageIntervalErrorMs: number;
  averageAbsoluteIntervalErrorMs: number;
  intervalErrorRangeMs: number;
};

export type RhythmAttemptSummary = {
  result: RhythmAttemptResult;
  score: number;
  expectedHitCount: number;
  correctCount: number;
  earlyCount: number;
  lateCount: number;
  missedCount: number;
  extraCount: number;
  restErrorCount: number;
  matchedRate: number;
  correctRate: number;
  stability: RhythmPerformanceStability;
  teacherSuggestion: string;
};

export type RhythmWarmupAttemptRecord = {
  version: "rhythm_warmup_attempt_v2";
  activity_id: "rhythm_warmup";
  grade_preset: GradePreset;
  practice_mode: PracticeMode;
  bpm: number;
  meter: PrimaryMeter;
  repeat_count: number;
  pattern_ids: string[];
  tap_attempts: Array<{
    tap_ms: number;
    status: RhythmTapStatus;
    target_event_id?: string;
    target_ms?: number;
    offset_ms?: number;
  }>;
  summary: {
    result: RhythmAttemptResult;
    score: number;
    expected_hit_count: number;
    correct_count: number;
    early_count: number;
    late_count: number;
    missed_count: number;
    extra_count: number;
    rest_error_count: number;
    matched_rate: number;
    correct_rate: number;
    tempo_stability: TempoStabilityStatus;
    teacher_suggestion: string;
  };
};

export type TempoStabilityStatus = "collecting" | "stable" | "rushing" | "dragging" | "unstable";

export type TempoStabilitySummary = {
  status: TempoStabilityStatus;
  tapCount: number;
  targetIntervalMs: number;
  averageIntervalMs: number;
  averageDeviationMs: number;
  teacherSuggestion: string;
};

export type RhythmWarmupToolkit = {
  activityId: "rhythm_warmup";
  title: string;
  gradeBands: string[];
  requiredComponents: string[];
  teachingAids: string[];
  virtualInstruments: string[];
  rhythmCards: RhythmCard[];
  teacherControls: {
    bpm: number;
    meter: PrimaryMeter;
    repeatCount: number;
    toleranceMs: number;
    mode: "listen" | "speak" | "tap";
  };
  classroomFlow: string[];
};

const DEFAULT_BPM = 100;
const DEFAULT_CARD_COLORS = ["#f1c36a", "#7fcbb6", "#ef8f6b", "#8db7d8", "#d6b0ef"];

export function normalizeRhythmCards(cards: RhythmCardInput[], bpm = DEFAULT_BPM): RhythmCard[] {
  const beatMs = 60000 / Math.max(40, Math.min(180, bpm));
  return cards.map((card, index) => ({
    id: card.id,
    patternId: card.patternId ?? card.id,
    label: card.label,
    syllable: card.syllable,
    beats: Math.max(0.25, card.beats),
    hitRequired: card.hitRequired ?? true,
    subdivisions: Math.max(1, card.subdivisions ?? 1),
    durationMs: Math.round(Math.max(0.25, card.beats) * beatMs),
    gesture: card.gesture || "拍手",
    color: card.color || DEFAULT_CARD_COLORS[index % DEFAULT_CARD_COLORS.length]
  }));
}

export function buildBeatTimeline(cards: RhythmCard[], options: BeatTimelineOptions = {}): BeatTimelineEvent[] {
  const beatsPerBar = resolveBeatsPerBar(options.meter ?? "2/4");
  const repeatCount = Math.max(1, Math.floor(options.repeatCount ?? 1));
  const events: BeatTimelineEvent[] = [];
  let cursorMs = 0;
  let beatIndex = 0;

  for (let repeat = 0; repeat < repeatCount; repeat += 1) {
    cards.forEach((card) => {
      const bar = Math.floor(beatIndex / beatsPerBar) + 1;
      const beatInBar = (beatIndex % beatsPerBar) + 1;
      events.push({
        id: `${repeat + 1}-${card.id}-${events.length + 1}`,
        cardId: card.id,
        patternId: card.patternId,
        label: card.label,
        syllable: card.syllable,
        startMs: cursorMs,
        durationMs: card.durationMs,
        bar,
        beatInBar,
        hitRequired: card.hitRequired,
        color: card.color
      });
      cursorMs += card.durationMs;
      beatIndex += Math.max(1, Math.round(card.beats));
    });
  }

  return events;
}

export function judgeTapTiming(
  tapMs: number,
  timeline: BeatTimelineEvent[],
  options: { toleranceMs?: number } = {}
): TapTimingJudgement {
  const toleranceMs = Math.max(40, options.toleranceMs ?? 110);
  const nearestEvent = findNearestEvent(tapMs, timeline);
  if (!nearestEvent) {
    return { status: "miss", accuracy: 0, message: "再听一次节拍入口" };
  }

  const offsetMs = Math.round(tapMs - nearestEvent.startMs);
  const absOffset = Math.abs(offsetMs);
  if (!nearestEvent.hitRequired && absOffset <= toleranceMs) {
    return { status: "rest", nearestEvent, offsetMs, accuracy: 0, message: "这里是休止，手要收住" };
  }
  if (nearestEvent.hitRequired && absOffset <= toleranceMs) {
    return {
      status: "on_time",
      nearestEvent,
      offsetMs,
      accuracy: Math.max(0, 1 - absOffset / toleranceMs),
      message: "稳"
    };
  }
  if (absOffset <= toleranceMs * 2.2) {
    return {
      status: offsetMs < 0 ? "early" : "late",
      nearestEvent,
      offsetMs,
      accuracy: Math.max(0, 1 - absOffset / (toleranceMs * 2.2)),
      message: offsetMs < 0 ? "稍早" : "稍晚"
    };
  }
  return { status: "miss", nearestEvent, offsetMs, accuracy: 0, message: "没有对上拍点" };
}

export function resolveGradeTimingWindows(
  bpm: number,
  gradePreset: GradePreset
): { correctMs: number; outerMs: number } {
  const beatMs = 60000 / Math.max(40, Math.min(180, bpm));
  const presets: Record<GradePreset, { correctRatio: number; correctMin: number; correctMax: number; outerRatio: number; outerMin: number; outerMax: number }> = {
    lower_primary: { correctRatio: 0.18, correctMin: 100, correctMax: 180, outerRatio: 0.32, outerMin: 180, outerMax: 300 },
    middle_primary: { correctRatio: 0.15, correctMin: 90, correctMax: 150, outerRatio: 0.28, outerMin: 160, outerMax: 260 },
    upper_primary: { correctRatio: 0.12, correctMin: 75, correctMax: 120, outerRatio: 0.24, outerMin: 130, outerMax: 220 },
  };
  const preset = presets[gradePreset];
  return {
    correctMs: Math.round(clamp(beatMs * preset.correctRatio, preset.correctMin, preset.correctMax)),
    outerMs: Math.round(clamp(beatMs * preset.outerRatio, preset.outerMin, preset.outerMax)),
  };
}

export function buildRhythmPerformanceTimeline(
  patternIds: string[],
  options: { bpm?: number; repeatCount?: number } = {}
): RhythmPerformanceTimelineEvent[] {
  const beatMs = 60000 / Math.max(40, Math.min(180, options.bpm ?? DEFAULT_BPM));
  return buildRhythmPatternTimeline(patternIds, { repeatCount: options.repeatCount }).map((event) => ({
    id: event.id,
    kind: event.kind,
    rhythmId: event.rhythmId,
    repeatIndex: event.repeatIndex,
    patternIndex: event.patternIndex,
    hitIndex: event.hitIndex,
    targetMs: Math.round(event.targetBeat * beatMs),
    endMs: event.endBeat === undefined ? undefined : Math.round(event.endBeat * beatMs),
  }));
}

export function buildRhythmAudioEvents(
  timeline: RhythmPerformanceTimelineEvent[],
  options: { startMs?: number; durationSeconds?: number } = {}
): RhythmAudioEvent[] {
  const startMs = Math.max(0, options.startMs ?? 0);
  const duration = Math.max(0.05, options.durationSeconds ?? 0.1);
  return timeline.filter((event) => event.kind === "hit").map((event) => ({
    patternId: event.rhythmId,
    offset: 0,
    start: (startMs + event.targetMs) / 1000,
    duration,
  }));
}

export function rhythmSequenceDurationMs(
  patternIds: string[],
  options: { bpm?: number; repeatCount?: number } = {}
) {
  const beatMs = 60000 / Math.max(40, Math.min(180, options.bpm ?? DEFAULT_BPM));
  const beatsPerSequence = patternIds.reduce((total, id) => total + getRhythmPatternDefinition(id).durationBeats, 0);
  return Math.round(beatsPerSequence * Math.max(1, Math.floor(options.repeatCount ?? 1)) * beatMs);
}

export function judgeRhythmPerformanceTap(
  tapMs: number,
  timeline: RhythmPerformanceTimelineEvent[],
  previousJudgements: RhythmTapJudgement[],
  options: { bpm?: number; gradePreset?: GradePreset } = {}
): RhythmTapJudgement {
  const roundedTapMs = Math.round(tapMs);
  const gradePreset = options.gradePreset ?? "middle_primary";
  const windows = resolveGradeTimingWindows(options.bpm ?? DEFAULT_BPM, gradePreset);
  const restEvent = timeline.find((event) => (
    event.kind === "rest"
    && event.endMs !== undefined
    && roundedTapMs >= event.targetMs
    && roundedTapMs < event.endMs
  ));
  if (restEvent) {
    return {
      id: `tap-${previousJudgements.length + 1}`,
      status: "rest_error",
      tapMs: roundedTapMs,
      targetEventId: restEvent.id,
      targetMs: restEvent.targetMs,
      offsetMs: roundedTapMs - restEvent.targetMs,
      message: "错误：休止处要停住",
    };
  }

  const matchedTargetIds = new Set(previousJudgements.map((item) => item.targetEventId).filter(Boolean));
  const previousTap = previousJudgements[previousJudgements.length - 1];
  const duplicateGuardMs = Math.min(75, Math.round(windows.correctMs / 2));
  if (previousTap && roundedTapMs - previousTap.tapMs >= 0 && roundedTapMs - previousTap.tapMs < duplicateGuardMs) {
    return {
      id: `tap-${previousJudgements.length + 1}`,
      status: "extra",
      tapMs: roundedTapMs,
      message: "错误：同一个音头多拍了一下",
    };
  }
  const candidates = timeline
    .filter((event) => event.kind === "hit" && !matchedTargetIds.has(event.id))
    .map((event) => ({ event, distance: Math.abs(roundedTapMs - event.targetMs) }))
    .filter((item) => item.distance <= windows.outerMs)
    .sort((left, right) => left.distance - right.distance || left.event.targetMs - right.event.targetMs);
  const nearest = candidates[0];
  if (!nearest) {
    return {
      id: `tap-${previousJudgements.length + 1}`,
      status: "extra",
      tapMs: roundedTapMs,
      message: "错误：多拍了一下",
    };
  }

  const offsetMs = roundedTapMs - nearest.event.targetMs;
  const status: RhythmTapStatus = Math.abs(offsetMs) <= windows.correctMs
    ? "correct"
    : offsetMs < 0 ? "early" : "late";
  return {
    id: `tap-${previousJudgements.length + 1}`,
    status,
    tapMs: roundedTapMs,
    targetEventId: nearest.event.id,
    targetMs: nearest.event.targetMs,
    offsetMs,
    message: status === "correct" ? "正确" : status === "early" ? "偏早" : "偏晚",
  };
}

export function evaluateRhythmAttempt(
  timeline: RhythmPerformanceTimelineEvent[],
  judgements: RhythmTapJudgement[],
  options: { bpm?: number; gradePreset?: GradePreset } = {}
): RhythmAttemptSummary {
  const hitEvents = timeline.filter((event) => event.kind === "hit");
  const matchedTargetIds = new Set(judgements.map((item) => item.targetEventId).filter((id) => hitEvents.some((event) => event.id === id)));
  const correctCount = countStatus(judgements, "correct");
  const earlyCount = countStatus(judgements, "early");
  const lateCount = countStatus(judgements, "late");
  const extraCount = countStatus(judgements, "extra");
  const restErrorCount = countStatus(judgements, "rest_error");
  const expectedHitCount = hitEvents.length;
  const missedCount = Math.max(0, expectedHitCount - matchedTargetIds.size);
  const matchedCount = correctCount + earlyCount + lateCount;
  const matchedRate = expectedHitCount ? matchedCount / expectedHitCount : 0;
  const correctRate = expectedHitCount ? correctCount / expectedHitCount : 0;
  const weightedPoints = correctCount + (earlyCount + lateCount) * 0.6;
  const score = Math.round(clamp((expectedHitCount ? weightedPoints / expectedHitCount * 100 : 0) - (extraCount + restErrorCount) * 5, 0, 100));
  const result: RhythmAttemptResult = correctCount === expectedHitCount && extraCount === 0 && restErrorCount === 0
    ? "correct"
    : matchedRate >= 0.8 && correctRate >= 0.7 && restErrorCount === 0 && missedCount + extraCount <= 2
      ? "adjust"
      : "retry";
  const stability = summarizeRhythmPerformanceStability(
    timeline,
    judgements,
    options.bpm ?? DEFAULT_BPM,
    options.gradePreset ?? "middle_primary"
  );
  return {
    result,
    score,
    expectedHitCount,
    correctCount,
    earlyCount,
    lateCount,
    missedCount,
    extraCount,
    restErrorCount,
    matchedRate,
    correctRate,
    stability,
    teacherSuggestion: rhythmAttemptSuggestion({ result, earlyCount, lateCount, missedCount, extraCount, restErrorCount, stability }),
  };
}

export function buildRhythmWarmupAttemptRecord(input: {
  gradePreset: GradePreset;
  practiceMode: PracticeMode;
  bpm: number;
  meter: PrimaryMeter;
  repeatCount: number;
  patternIds: string[];
  timeline: RhythmPerformanceTimelineEvent[];
  judgements: RhythmTapJudgement[];
}): RhythmWarmupAttemptRecord {
  const summary = evaluateRhythmAttempt(input.timeline, input.judgements, {
    bpm: input.bpm,
    gradePreset: input.gradePreset,
  });
  return {
    version: "rhythm_warmup_attempt_v2",
    activity_id: "rhythm_warmup",
    grade_preset: input.gradePreset,
    practice_mode: input.practiceMode,
    bpm: input.bpm,
    meter: input.meter,
    repeat_count: input.repeatCount,
    pattern_ids: [...input.patternIds],
    tap_attempts: input.judgements.map((item) => ({
      tap_ms: item.tapMs,
      status: item.status,
      target_event_id: item.targetEventId,
      target_ms: item.targetMs,
      offset_ms: item.offsetMs,
    })),
    summary: {
      result: summary.result,
      score: summary.score,
      expected_hit_count: summary.expectedHitCount,
      correct_count: summary.correctCount,
      early_count: summary.earlyCount,
      late_count: summary.lateCount,
      missed_count: summary.missedCount,
      extra_count: summary.extraCount,
      rest_error_count: summary.restErrorCount,
      matched_rate: summary.matchedRate,
      correct_rate: summary.correctRate,
      tempo_stability: summary.stability.status,
      teacher_suggestion: summary.teacherSuggestion,
    },
  };
}

export function summarizeTempoStability(
  tapTimesMs: number[],
  options: { bpm?: number; toleranceMs?: number } = {}
): TempoStabilitySummary {
  const tapCount = tapTimesMs.length;
  const targetIntervalMs = Math.round(60000 / Math.max(40, Math.min(180, options.bpm ?? DEFAULT_BPM)));
  const toleranceMs = Math.max(40, options.toleranceMs ?? 90);
  if (tapCount < 3) {
    return {
      status: "collecting",
      tapCount,
      targetIntervalMs,
      averageIntervalMs: 0,
      averageDeviationMs: 0,
      teacherSuggestion: "至少记录 3 次拍点，再判断稳定拍。",
    };
  }
  const sorted = [...tapTimesMs].sort((left, right) => left - right);
  const intervals = sorted.slice(1).map((time, index) => time - sorted[index]);
  const averageIntervalMs = Math.round(intervals.reduce((total, item) => total + item, 0) / intervals.length);
  const deviations = intervals.map((interval) => Math.abs(interval - targetIntervalMs));
  const averageDeviationMs = Math.round(deviations.reduce((total, item) => total + item, 0) / deviations.length);
  const variance = Math.max(...intervals) - Math.min(...intervals);
  const status = resolveTempoStabilityStatus(averageIntervalMs, targetIntervalMs, averageDeviationMs, variance, toleranceMs);
  return {
    status,
    tapCount,
    targetIntervalMs,
    averageIntervalMs,
    averageDeviationMs,
    teacherSuggestion: tempoStabilitySuggestion(status),
  };
}

export function buildDefaultRhythmWarmupToolkit(): RhythmWarmupToolkit {
  return {
    activityId: "rhythm_warmup",
    title: "小学节奏热身",
    gradeBands: ["小学低段", "小学中段"],
    requiredComponents: [
      "audio_player",
      "rhythm_card_bank",
      "meter_track",
      "tap_feedback",
      "teacher_control_bar",
      "rhythm_pad"
    ],
    teachingAids: ["rhythm_cards"],
    virtualInstruments: ["rhythm_pad"],
    rhythmCards: normalizeRhythmCards(
      [
        { id: "sixteenth_four", label: formalRhythmName("sixteenth_four"), syllable: formalRhythmLabel("sixteenth_four"), beats: 1, subdivisions: 4, gesture: "拍手", color: "#f1c36a" },
        { id: "eighth_pair", label: formalRhythmName("eighth_pair"), syllable: formalRhythmLabel("eighth_pair"), beats: 1, subdivisions: 2, gesture: "拍腿", color: "#7fcbb6" },
        { id: "eighth_sixteenth_sixteenth", label: formalRhythmName("eighth_sixteenth_sixteenth"), syllable: formalRhythmLabel("eighth_sixteenth_sixteenth"), beats: 1, subdivisions: 3, gesture: "拍手", color: "#f1c36a" },
        { id: "sixteenth_sixteenth_eighth", label: formalRhythmName("sixteenth_sixteenth_eighth"), syllable: formalRhythmLabel("sixteenth_sixteenth_eighth"), beats: 1, subdivisions: 3, gesture: "拍腿", color: "#7fcbb6" },
        { id: "quarter", label: formalRhythmName("quarter"), syllable: formalRhythmLabel("quarter"), beats: 1, gesture: "拍手", color: "#f1c36a" }
      ],
      92
    ),
    teacherControls: {
      bpm: 92,
      meter: "2/4",
      repeatCount: 2,
      toleranceMs: 120,
      mode: "tap"
    },
    classroomFlow: ["听节拍", "读节奏", "拍回来", "换动作"]
  };
}

function resolveBeatsPerBar(meter: PrimaryMeter) {
  return Number(meter.split("/")[0]) || 2;
}

function resolveTempoStabilityStatus(
  averageIntervalMs: number,
  targetIntervalMs: number,
  averageDeviationMs: number,
  intervalRangeMs: number,
  toleranceMs: number
): TempoStabilityStatus {
  if (averageDeviationMs <= toleranceMs && intervalRangeMs <= toleranceMs * 1.5) return "stable";
  if (averageIntervalMs < targetIntervalMs - toleranceMs) return "rushing";
  if (averageIntervalMs > targetIntervalMs + toleranceMs) return "dragging";
  return "unstable";
}

function tempoStabilitySuggestion(status: TempoStabilityStatus) {
  if (status === "stable") return "保持稳定拍，可以换动作或隐藏提示。";
  if (status === "rushing") return "拍点偏快，教师可先放慢速度，再让学生跟拍。";
  if (status === "dragging") return "拍点偏慢，先听强拍提示，再缩短动作幅度。";
  if (status === "unstable") return "拍点间隔不均，先只拍稳定拍，不急着读节奏。";
  return "至少记录 3 次拍点，再判断稳定拍。";
}

function summarizeRhythmPerformanceStability(
  timeline: RhythmPerformanceTimelineEvent[],
  judgements: RhythmTapJudgement[],
  bpm: number,
  gradePreset: GradePreset
): RhythmPerformanceStability {
  const hitsById = new Map(timeline.filter((event) => event.kind === "hit").map((event) => [event.id, event]));
  const matched = judgements
    .filter((item) => item.targetEventId && item.status !== "extra" && item.status !== "rest_error")
    .map((item) => ({ judgement: item, target: hitsById.get(item.targetEventId!) }))
    .filter((item): item is { judgement: RhythmTapJudgement; target: RhythmPerformanceTimelineEvent } => Boolean(item.target))
    .sort((left, right) => left.target.targetMs - right.target.targetMs);
  if (matched.length < 3) {
    return {
      status: "collecting",
      matchedTapCount: matched.length,
      averageIntervalErrorMs: 0,
      averageAbsoluteIntervalErrorMs: 0,
      intervalErrorRangeMs: 0,
    };
  }
  const intervalErrors = matched.slice(1).map((item, index) => {
    const previous = matched[index];
    const studentInterval = item.judgement.tapMs - previous.judgement.tapMs;
    const targetInterval = item.target.targetMs - previous.target.targetMs;
    return studentInterval - targetInterval;
  });
  const averageIntervalErrorMs = Math.round(intervalErrors.reduce((total, value) => total + value, 0) / intervalErrors.length);
  const averageAbsoluteIntervalErrorMs = Math.round(intervalErrors.reduce((total, value) => total + Math.abs(value), 0) / intervalErrors.length);
  const intervalErrorRangeMs = Math.round(Math.max(...intervalErrors) - Math.min(...intervalErrors));
  const windows = resolveGradeTimingWindows(bpm, gradePreset);
  const status: TempoStabilityStatus = averageAbsoluteIntervalErrorMs <= windows.correctMs && intervalErrorRangeMs <= windows.outerMs
    ? "stable"
    : averageIntervalErrorMs < -windows.correctMs / 2
      ? "rushing"
      : averageIntervalErrorMs > windows.correctMs / 2
        ? "dragging"
        : "unstable";
  return {
    status,
    matchedTapCount: matched.length,
    averageIntervalErrorMs,
    averageAbsoluteIntervalErrorMs,
    intervalErrorRangeMs,
  };
}

function rhythmAttemptSuggestion(input: {
  result: RhythmAttemptResult;
  earlyCount: number;
  lateCount: number;
  missedCount: number;
  extraCount: number;
  restErrorCount: number;
  stability: RhythmPerformanceStability;
}) {
  if (input.restErrorCount > 0) return "休止处要停住：先只练有休止的节奏卡，再回到完整组合。";
  if (input.missedCount > 0) return `漏拍 ${input.missedCount} 次：建议放慢速度，分卡练习后再连起来。`;
  if (input.extraCount > 0) return `多拍 ${input.extraCount} 次：先听清每张卡有几个音头，再重新跟拍。`;
  if (input.earlyCount > input.lateCount) return "整体有些偏早：先听稳拍，不要抢在声音前面。";
  if (input.lateCount > 0) return "整体有些偏晚：缩小动作，提前准备下一个音头。";
  if (input.stability.status === "rushing") return "节奏逐渐加快：降低速度并保持动作幅度一致。";
  if (input.stability.status === "dragging") return "节奏逐渐变慢：先跟着稳定拍，再加入完整节奏。";
  if (input.stability.status === "unstable") return "音头间隔还不均匀：拆成一拍一拍练习。";
  if (input.result === "correct") return "本轮节奏正确，可以换动作、提高速度或隐藏提示。";
  return "基本正确，再调整早晚位置后重拍一次。";
}

function countStatus(judgements: RhythmTapJudgement[], status: RhythmTapStatus) {
  return judgements.filter((item) => item.status === status).length;
}

function clamp(value: number, min: number, max: number) {
  return Math.max(min, Math.min(max, value));
}

function findNearestEvent(tapMs: number, timeline: BeatTimelineEvent[]) {
  let nearest: BeatTimelineEvent | undefined;
  let nearestDistance = Number.POSITIVE_INFINITY;
  timeline.forEach((event) => {
    const distance = Math.abs(tapMs - event.startMs);
    if (distance < nearestDistance) {
      nearest = event;
      nearestDistance = distance;
    }
  });
  return nearest;
}
