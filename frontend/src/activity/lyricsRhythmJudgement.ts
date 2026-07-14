import { RHYTHM_PATTERN_DEFINITIONS } from "../shared/rhythmPatternCatalog";
import {
  buildRhythmPerformanceTimeline,
  evaluateRhythmAttempt,
  judgeRhythmPerformanceTap,
  type GradePreset,
  type RhythmPerformanceTimelineEvent,
  type RhythmTapJudgement,
  type TempoStabilityStatus,
} from "./rhythmWarmupLogic";
import { normalizeLyricsPracticeMode, type LyricsPracticeMode } from "./lyricsTrainingFlow";

export type LyricsRhythmSource = "musicxml" | "midi" | "teacher_manual" | "recognized_draft";

export type LyricsRhythmPhrase = {
  id: string;
  lyrics: string;
  meter: string;
  bpm: number;
  patternIds: string[];
  lyricUnits: Array<{ id: string; text: string; targetHitIds: string[] }>;
  audioClip?: { url: string; startSeconds: number; endSeconds: number };
  source: LyricsRhythmSource;
  teacherConfirmed: boolean;
};

export type LyricsRhythmActivityConfig = {
  version: "lyrics_rhythm_activity_v2";
  gradePreset: GradePreset;
  practiceMode: LyricsPracticeMode;
  phrases: LyricsRhythmPhrase[];
  usingExampleMaterial: boolean;
};

export type LyricsRhythmConfigInput = {
  version?: string;
  grade_preset?: GradePreset;
  gradePreset?: GradePreset;
  practice_mode?: LyricsPracticeMode;
  practiceMode?: LyricsPracticeMode;
  phrases?: LyricsRhythmPhrase[];
  lyrics_phrases?: string[];
  rhythm_pattern?: string[];
  meter?: string;
  bpm?: number;
  example_material?: boolean;
};

export type LyricsRhythmTimelineEvent = RhythmPerformanceTimelineEvent & {
  rhythm: string;
  targetMs: number;
  durationMs: number;
  isRest: boolean;
  restStartMs?: number;
  restEndMs?: number;
};

export type LyricsRhythmTapJudgement = RhythmTapJudgement;
export type LyricsRhythmTeacherChecks = { readingCorrect: boolean; singingMeetsGoal: boolean };

export type LyricsRhythmAttemptEvaluation = {
  phraseIndex: number;
  phrase: string;
  tapSummary: {
    attemptCount: number;
    correctCount: number;
    onTimeCount: number;
    earlyCount: number;
    lateCount: number;
    missedCount: number;
    missCount: number;
    extraCount: number;
    restErrorCount: number;
    expectedHitCount: number;
    score: number;
  };
  tempoStability: TempoStabilityStatus;
  attemptResult: "correct" | "adjust" | "retry";
  retryCount: number;
  webSuggestion: string;
  requiresRepractice: boolean;
  webRecommendedPass: boolean;
  recommendedPass: boolean;
  teacherChecks: LyricsRhythmTeacherChecks;
  finalPassAllowed: boolean;
};

export type LyricsRhythmRecord = {
  version: "lyrics_rhythm_reading_record_v2";
  activity_id: "lyrics_rhythm_reading";
  phrase_id: string;
  phrase_index: number;
  phrase_text: string;
  source: LyricsRhythmSource;
  pattern_ids: string[];
  bpm: number;
  meter: string;
  tap_attempts: Array<{
    tap_ms: number;
    status: LyricsRhythmTapJudgement["status"];
    target_event_id?: string;
    target_ms?: number;
    offset_ms?: number;
  }>;
  timing_result: LyricsRhythmAttemptEvaluation["tapSummary"];
  tempo_stability: TempoStabilityStatus;
  retry_count: number;
  web_suggestion: string;
  requires_repractice: boolean;
  web_judgement: { recommended_pass: boolean };
  teacher_confirmation: { reading_correct: boolean; singing_meets_goal: boolean };
  final_pass_allowed: boolean;
  pass_confirmed: boolean;
};

const DEFAULT_BPM = 84;
const VALID_PATTERN_IDS = new Set(RHYTHM_PATTERN_DEFINITIONS.map((item) => item.id));

export function normalizeLyricsRhythmConfig(input: LyricsRhythmConfigInput = {}): LyricsRhythmActivityConfig {
  const gradePreset = input.grade_preset ?? input.gradePreset ?? "middle_primary";
  if (Array.isArray(input.phrases) && input.phrases.length) {
    return {
      version: "lyrics_rhythm_activity_v2",
      gradePreset,
      practiceMode: normalizeLyricsPracticeMode(input.practice_mode ?? input.practiceMode),
      phrases: input.phrases.map(normalizePhrase),
      usingExampleMaterial: Boolean(input.example_material),
    };
  }

  const legacyLyrics = input.lyrics_phrases?.filter((item) => String(item).trim()) ?? [];
  const legacyPattern = input.rhythm_pattern?.filter(Boolean) ?? [];
  return {
    version: "lyrics_rhythm_activity_v2",
    gradePreset,
    practiceMode: normalizeLyricsPracticeMode(input.practice_mode ?? input.practiceMode),
    phrases: legacyLyrics.map((lyrics, index) => normalizePhrase({
      id: `legacy-phrase-${index + 1}`,
      lyrics,
      meter: input.meter ?? "2/4",
      bpm: input.bpm ?? DEFAULT_BPM,
      patternIds: legacyPattern,
      lyricUnits: [],
      source: "teacher_manual",
      teacherConfirmed: true,
    })),
    usingExampleMaterial: Boolean(input.example_material),
  };
}

export function canStartLyricsRhythmPhrase(phrase: LyricsRhythmPhrase): { ok: boolean; reason?: string } {
  if (!phrase.teacherConfirmed || phrase.source === "recognized_draft") {
    return { ok: false, reason: "该乐句来自识别草稿，需教师核对歌词与谱面后才能开始判定。" };
  }
  if (!phrase.lyrics.trim()) return { ok: false, reason: "缺少歌词文本。" };
  if (!phrase.patternIds.length) return { ok: false, reason: "缺少已确认的节奏型。" };
  const unknown = phrase.patternIds.find((id) => !VALID_PATTERN_IDS.has(id));
  if (unknown) return { ok: false, reason: `无法识别节奏型：${unknown}` };
  const hitIds = new Set(buildRhythmPerformanceTimeline(phrase.patternIds, { bpm: phrase.bpm })
    .filter((event) => event.kind === "hit")
    .map((event) => event.id));
  const invalidBinding = phrase.lyricUnits.flatMap((unit) => unit.targetHitIds).find((id) => !hitIds.has(id));
  if (invalidBinding) return { ok: false, reason: `歌词绑定引用了不存在的音头：${invalidBinding}` };
  return { ok: true };
}

export function buildLyricsRhythmTimeline(
  patternIds: string[],
  options: { bpm?: number } = {}
): LyricsRhythmTimelineEvent[] {
  const bpm = clampNumber(options.bpm, 40, 180, DEFAULT_BPM);
  const beatMs = 60000 / bpm;
  return buildRhythmPerformanceTimeline(patternIds, { bpm }).map((event) => ({
    ...event,
    rhythm: event.rhythmId,
    durationMs: Math.round((event.endMs === undefined ? beatMs : event.endMs - event.targetMs)),
    isRest: event.kind === "rest",
    restStartMs: event.kind === "rest" ? event.targetMs : undefined,
    restEndMs: event.kind === "rest" ? event.endMs : undefined,
  }));
}

export function judgeLyricsRhythmTap(
  tapMs: number,
  timeline: LyricsRhythmTimelineEvent[],
  previousJudgements: LyricsRhythmTapJudgement[] = [],
  options: { bpm?: number; gradePreset?: GradePreset } = {}
): LyricsRhythmTapJudgement {
  return judgeRhythmPerformanceTap(tapMs, timeline, previousJudgements, options);
}

export function evaluateLyricsRhythmAttempt(input: {
  phraseIndex: number;
  phrase: LyricsRhythmPhrase;
  tapJudgements: LyricsRhythmTapJudgement[];
  retryCount: number;
  teacherChecks: LyricsRhythmTeacherChecks;
  gradePreset?: GradePreset;
}): LyricsRhythmAttemptEvaluation {
  const timeline = buildLyricsRhythmTimeline(input.phrase.patternIds, { bpm: input.phrase.bpm });
  const summary = evaluateRhythmAttempt(timeline, input.tapJudgements, {
    bpm: input.phrase.bpm,
    gradePreset: input.gradePreset ?? "middle_primary",
  });
  const webRecommendedPass = summary.result === "correct";
  const finalPassAllowed = webRecommendedPass
    && input.teacherChecks.readingCorrect
    && input.teacherChecks.singingMeetsGoal;
  return {
    phraseIndex: input.phraseIndex,
    phrase: input.phrase.lyrics,
    tapSummary: {
      attemptCount: input.tapJudgements.length,
      correctCount: summary.correctCount,
      onTimeCount: summary.correctCount,
      earlyCount: summary.earlyCount,
      lateCount: summary.lateCount,
      missedCount: summary.missedCount,
      missCount: summary.missedCount,
      extraCount: summary.extraCount,
      restErrorCount: summary.restErrorCount,
      expectedHitCount: summary.expectedHitCount,
      score: summary.score,
    },
    tempoStability: summary.stability.status,
    attemptResult: summary.result,
    retryCount: input.retryCount,
    webSuggestion: webRecommendedPass
      ? "节奏点击证据合格，请教师确认歌词朗读和回唱表现。"
      : summary.teacherSuggestion,
    requiresRepractice: summary.result === "retry" || input.retryCount >= 3,
    webRecommendedPass,
    recommendedPass: webRecommendedPass,
    teacherChecks: input.teacherChecks,
    finalPassAllowed,
  };
}

export function buildLyricsRhythmRecord(input: {
  phraseIndex: number;
  phrase: LyricsRhythmPhrase;
  tapJudgements: LyricsRhythmTapJudgement[];
  retryCount: number;
  teacherChecks: LyricsRhythmTeacherChecks;
  passConfirmed: boolean;
  gradePreset?: GradePreset;
}): LyricsRhythmRecord {
  const evaluation = evaluateLyricsRhythmAttempt(input);
  return {
    version: "lyrics_rhythm_reading_record_v2",
    activity_id: "lyrics_rhythm_reading",
    phrase_id: input.phrase.id,
    phrase_index: input.phraseIndex,
    phrase_text: input.phrase.lyrics,
    source: input.phrase.source,
    pattern_ids: [...input.phrase.patternIds],
    bpm: input.phrase.bpm,
    meter: input.phrase.meter,
    tap_attempts: input.tapJudgements.map((item) => ({
      tap_ms: item.tapMs,
      status: item.status,
      target_event_id: item.targetEventId,
      target_ms: item.targetMs,
      offset_ms: item.offsetMs,
    })),
    timing_result: evaluation.tapSummary,
    tempo_stability: evaluation.tempoStability,
    retry_count: evaluation.retryCount,
    web_suggestion: evaluation.webSuggestion,
    requires_repractice: evaluation.requiresRepractice,
    web_judgement: { recommended_pass: evaluation.webRecommendedPass },
    teacher_confirmation: {
      reading_correct: input.teacherChecks.readingCorrect,
      singing_meets_goal: input.teacherChecks.singingMeetsGoal,
    },
    final_pass_allowed: evaluation.finalPassAllowed,
    pass_confirmed: input.passConfirmed,
  };
}

function normalizePhrase(phrase: LyricsRhythmPhrase): LyricsRhythmPhrase {
  return {
    ...phrase,
    id: String(phrase.id || "phrase"),
    lyrics: String(phrase.lyrics || ""),
    meter: String(phrase.meter || "2/4"),
    bpm: clampNumber(phrase.bpm, 40, 180, DEFAULT_BPM),
    patternIds: Array.isArray(phrase.patternIds) ? phrase.patternIds.map(String) : [],
    lyricUnits: Array.isArray(phrase.lyricUnits) ? phrase.lyricUnits.map((unit) => ({
      id: String(unit.id || "unit"),
      text: String(unit.text || ""),
      targetHitIds: Array.isArray(unit.targetHitIds) ? unit.targetHitIds.map(String) : [],
    })) : [],
    source: phrase.source ?? "recognized_draft",
    teacherConfirmed: Boolean(phrase.teacherConfirmed),
  };
}

function clampNumber(value: unknown, min: number, max: number, fallback: number): number {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? Math.max(min, Math.min(max, parsed)) : fallback;
}
