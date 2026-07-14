import {
  buildLyricsRhythmRecord,
  buildLyricsRhythmTimeline,
  canStartLyricsRhythmPhrase,
  evaluateLyricsRhythmAttempt,
  judgeLyricsRhythmTap,
  normalizeLyricsRhythmConfig,
  type LyricsRhythmPhrase,
  type LyricsRhythmTapJudgement
} from "../src/activity/lyricsRhythmJudgement";

function assertEqual<T>(actual: T, expected: T, label: string) {
  if (actual !== expected) throw new Error(`${label}: expected ${String(expected)}, got ${String(actual)}`);
}

function assertDeepEqual(actual: unknown, expected: unknown, label: string) {
  const actualText = JSON.stringify(actual);
  const expectedText = JSON.stringify(expected);
  if (actualText !== expectedText) throw new Error(`${label}: expected ${expectedText}, got ${actualText}`);
}

const springPhrase: LyricsRhythmPhrase = {
  id: "spring-1",
  lyrics: "春天来了",
  meter: "2/4",
  bpm: 60,
  patternIds: ["quarter", "eighth_pair", "quarter", "rest"],
  lyricUnits: [
    { id: "word-1", text: "春", targetHitIds: ["1-1-quarter-hit-1"] },
    { id: "word-2", text: "天", targetHitIds: ["1-2-eighth_pair-hit-1", "1-2-eighth_pair-hit-2"] },
    { id: "word-3", text: "来了", targetHitIds: ["1-3-quarter-hit-1"] },
  ],
  source: "musicxml",
  teacherConfirmed: true,
};

const secondPhrase: LyricsRhythmPhrase = {
  id: "spring-2",
  lyrics: "花儿笑了",
  meter: "3/4",
  bpm: 72,
  patternIds: ["eighth_pair", "quarter", "half"],
  lyricUnits: [],
  source: "teacher_manual",
  teacherConfirmed: true,
};

const normalized = normalizeLyricsRhythmConfig({
  version: "lyrics_rhythm_activity_v2",
  grade_preset: "lower_primary",
  phrases: [springPhrase, secondPhrase],
});
assertEqual(normalized.phrases.length, 2, "specific songs keep every supplied phrase");
assertEqual(normalized.phrases[1].meter, "3/4", "phrases keep independent meter");
assertEqual(normalized.phrases[1].bpm, 72, "phrases keep independent bpm");

const draftPhrase = { ...springPhrase, id: "draft-1", source: "recognized_draft" as const, teacherConfirmed: false };
assertEqual(canStartLyricsRhythmPhrase(draftPhrase).ok, false, "unconfirmed recognition draft cannot start judgement");
assertEqual(canStartLyricsRhythmPhrase(springPhrase).ok, true, "confirmed score phrase can start judgement");

const timeline = buildLyricsRhythmTimeline(springPhrase.patternIds, { bpm: springPhrase.bpm });
assertDeepEqual(
  timeline.map((event) => [event.rhythm, event.targetMs, event.isRest]),
  [
    ["quarter", 0, false],
    ["eighth_pair", 1000, false],
    ["eighth_pair", 1500, false],
    ["quarter", 2000, false],
    ["rest", 3000, true],
  ],
  "lyrics rhythm timeline comes from the shared rhythm catalog"
);

const judgements: LyricsRhythmTapJudgement[] = [];
for (const time of [0, 1000, 1500, 2000]) {
  judgements.push(judgeLyricsRhythmTap(time, timeline, judgements, { bpm: 60, gradePreset: "lower_primary" }));
}
const duplicate = judgeLyricsRhythmTap(2010, timeline, judgements, { bpm: 60, gradePreset: "lower_primary" });
assertEqual(duplicate.status, "extra", "one target onset cannot score twice");
assertEqual(judgeLyricsRhythmTap(3060, timeline, judgements, { bpm: 60 }).status, "rest_error", "rest taps are identified");

const ready = evaluateLyricsRhythmAttempt({
  phraseIndex: 0,
  phrase: springPhrase,
  tapJudgements: judgements,
  retryCount: 0,
  teacherChecks: { readingCorrect: false, singingMeetsGoal: false },
});
assertEqual(ready.webRecommendedPass, true, "web can recommend pass from objective timing evidence");
assertEqual(ready.finalPassAllowed, false, "web evidence alone cannot pass reading and singing");

const teacherConfirmed = evaluateLyricsRhythmAttempt({
  phraseIndex: 0,
  phrase: springPhrase,
  tapJudgements: judgements,
  retryCount: 0,
  teacherChecks: { readingCorrect: true, singingMeetsGoal: true },
});
assertEqual(teacherConfirmed.finalPassAllowed, true, "final pass requires both teacher confirmations");
assertEqual(teacherConfirmed.tapSummary.missedCount, 0, "complete attempt has no missed onset");

const record = buildLyricsRhythmRecord({
  phraseIndex: 0,
  phrase: springPhrase,
  tapJudgements: judgements,
  retryCount: 1,
  teacherChecks: { readingCorrect: true, singingMeetsGoal: false },
  passConfirmed: false,
});
assertEqual(record.version, "lyrics_rhythm_reading_record_v2", "record exports v2 evidence boundary");
assertEqual(record.web_judgement.recommended_pass, true, "record includes web timing recommendation");
assertEqual(record.teacher_confirmation.singing_meets_goal, false, "record keeps teacher singing decision separate");
assertEqual(record.final_pass_allowed, false, "record exposes combined final gate");

const legacy = normalizeLyricsRhythmConfig({
  lyrics_phrases: ["旧版第一句", "旧版第二句"],
  rhythm_pattern: ["quarter", "rest"],
  meter: "2/4",
  bpm: 84,
});
assertEqual(legacy.version, "lyrics_rhythm_activity_v2", "legacy input is converted to v2");
assertEqual(legacy.phrases[0].source, "teacher_manual", "legacy supplied material remains teacher material");
assertEqual(legacy.phrases[1].patternIds.join(","), "quarter,rest", "legacy rhythm remains compatible");
