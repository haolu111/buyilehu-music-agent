export type RhythmPatternDefinition = {
  id: string;
  durationBeats: number;
  hitOffsetsBeats: number[];
  restWindowsBeats: Array<[number, number]>;
};

export type RhythmPatternTimelineEvent = {
  id: string;
  kind: "hit" | "rest";
  rhythmId: string;
  repeatIndex: number;
  patternIndex: number;
  hitIndex: number;
  targetBeat: number;
  endBeat?: number;
};

export type RhythmEchoGradePreset = "lower_primary" | "middle_primary" | "upper_primary";
export type RhythmEchoMeter = "2/4" | "3/4" | "4/4";

export type RhythmEchoQuestion = {
  gradePreset: RhythmEchoGradePreset;
  meter: RhythmEchoMeter;
  barCount: number;
  patternIds: string[];
  barPatternIds: string[][];
};

export type RhythmExerciseInput = {
  patternIds?: string[];
  allowedPatternIds?: string[];
  meter: RhythmEchoMeter;
  gradePreset: RhythmEchoGradePreset;
  bpm: number;
  mode: "echo" | "play_along";
};

export type ResolvedRhythmExercise = {
  ok: boolean;
  source: "teacher_sequence" | "teacher_pool" | "random_fallback" | "invalid";
  patternIds: string[];
  barCount: number;
  error?: string;
};

const DEFINITIONS: RhythmPatternDefinition[] = [
  { id: "quarter", durationBeats: 1, hitOffsetsBeats: [0], restWindowsBeats: [] },
  { id: "quarter_2", durationBeats: 1, hitOffsetsBeats: [0], restWindowsBeats: [] },
  { id: "eighth_pair", durationBeats: 1, hitOffsetsBeats: [0, 0.5], restWindowsBeats: [] },
  { id: "eighth_sixteenth", durationBeats: 1, hitOffsetsBeats: [0, 0.5, 0.75], restWindowsBeats: [] },
  { id: "eighth_sixteenth_sixteenth", durationBeats: 1, hitOffsetsBeats: [0, 0.5, 0.75], restWindowsBeats: [] },
  { id: "sixteenth_eighth", durationBeats: 1, hitOffsetsBeats: [0, 0.25, 0.5], restWindowsBeats: [] },
  { id: "sixteenth_sixteenth_eighth", durationBeats: 1, hitOffsetsBeats: [0, 0.25, 0.5], restWindowsBeats: [] },
  { id: "sixteenth_four", durationBeats: 1, hitOffsetsBeats: [0, 0.25, 0.5, 0.75], restWindowsBeats: [] },
  { id: "sixteenth_run", durationBeats: 1, hitOffsetsBeats: [0, 0.25, 0.5, 0.75], restWindowsBeats: [] },
  { id: "syncopation", durationBeats: 1, hitOffsetsBeats: [0, 0.25, 0.75], restWindowsBeats: [] },
  { id: "eighth_triplet", durationBeats: 1, hitOffsetsBeats: [0, 1 / 3, 2 / 3], restWindowsBeats: [] },
  { id: "dotted_quarter", durationBeats: 1.5, hitOffsetsBeats: [0], restWindowsBeats: [] },
  { id: "half", durationBeats: 2, hitOffsetsBeats: [0], restWindowsBeats: [] },
  { id: "dotted_half", durationBeats: 3, hitOffsetsBeats: [0], restWindowsBeats: [] },
  { id: "rest", durationBeats: 1, hitOffsetsBeats: [], restWindowsBeats: [[0, 1]] },
  { id: "eighth_rest", durationBeats: 0.5, hitOffsetsBeats: [], restWindowsBeats: [[0, 0.5]] },
];

const BY_ID = new Map(DEFINITIONS.map((definition) => [definition.id, definition]));

export const RHYTHM_PATTERN_DEFINITIONS = DEFINITIONS;

export const RHYTHM_ECHO_GRADE_POOLS: Record<RhythmEchoGradePreset, string[]> = {
  lower_primary: ["quarter", "eighth_pair", "rest"],
  middle_primary: [
    "quarter",
    "eighth_pair",
    "rest",
    "sixteenth_four",
    "eighth_sixteenth_sixteenth",
    "sixteenth_sixteenth_eighth",
  ],
  upper_primary: [
    "quarter",
    "eighth_pair",
    "rest",
    "sixteenth_four",
    "eighth_sixteenth_sixteenth",
    "sixteenth_sixteenth_eighth",
    "syncopation",
    "eighth_triplet",
  ],
};

export function getRhythmPatternDefinition(id: string): RhythmPatternDefinition {
  return BY_ID.get(id) ?? BY_ID.get("quarter")!;
}

export function buildRhythmPatternTimeline(
  patternIds: string[],
  options: { repeatCount?: number } = {}
): RhythmPatternTimelineEvent[] {
  const repeatCount = Math.max(1, Math.floor(options.repeatCount ?? 1));
  const events: RhythmPatternTimelineEvent[] = [];
  let cursorBeat = 0;

  for (let repeatIndex = 0; repeatIndex < repeatCount; repeatIndex += 1) {
    patternIds.forEach((rhythmId, patternIndex) => {
      const definition = getRhythmPatternDefinition(rhythmId);
      definition.hitOffsetsBeats.forEach((offset, hitIndex) => {
        events.push({
          id: `${repeatIndex + 1}-${patternIndex + 1}-${rhythmId}-hit-${hitIndex + 1}`,
          kind: "hit",
          rhythmId,
          repeatIndex,
          patternIndex,
          hitIndex,
          targetBeat: cursorBeat + offset,
        });
      });
      definition.restWindowsBeats.forEach(([startBeat, endBeat], hitIndex) => {
        events.push({
          id: `${repeatIndex + 1}-${patternIndex + 1}-${rhythmId}-rest-${hitIndex + 1}`,
          kind: "rest",
          rhythmId,
          repeatIndex,
          patternIndex,
          hitIndex,
          targetBeat: cursorBeat + startBeat,
          endBeat: cursorBeat + endBeat,
        });
      });
      cursorBeat += definition.durationBeats;
    });
  }

  return events.sort((left, right) => left.targetBeat - right.targetBeat || left.id.localeCompare(right.id));
}

export function generateRhythmEchoQuestion(options: {
  gradePreset: RhythmEchoGradePreset;
  meter: RhythmEchoMeter;
  previousPatternIds?: string[];
  random?: () => number;
}): RhythmEchoQuestion {
  const beatsPerBar = Number(options.meter.split("/")[0]) || 2;
  const barCount = options.gradePreset === "lower_primary" ? 2 : 4;
  const pool = RHYTHM_ECHO_GRADE_POOLS[options.gradePreset];
  const random = options.random ?? Math.random;
  const patternIds = Array.from({ length: beatsPerBar * barCount }, () => {
    const index = Math.min(pool.length - 1, Math.floor(Math.max(0, random()) * pool.length));
    return pool[index];
  });

  if (sameSequence(patternIds, options.previousPatternIds) && pool.length > 1) {
    const lastIndex = patternIds.length - 1;
    const currentPoolIndex = Math.max(0, pool.indexOf(patternIds[lastIndex]));
    patternIds[lastIndex] = pool[(currentPoolIndex + 1) % pool.length];
  }

  return {
    gradePreset: options.gradePreset,
    meter: options.meter,
    barCount,
    patternIds,
    barPatternIds: Array.from({ length: barCount }, (_, index) => (
      patternIds.slice(index * beatsPerBar, (index + 1) * beatsPerBar)
    )),
  };
}

export function resolveRhythmExerciseInput(
  input: RhythmExerciseInput & { random?: () => number; previousPatternIds?: string[] }
): ResolvedRhythmExercise {
  const explicit = input.patternIds?.filter(Boolean) ?? [];
  if (explicit.length) {
    const unknown = explicit.find((id) => !BY_ID.has(id));
    if (unknown) return invalidExercise(`未知节奏型：${unknown}`);
    const beatsPerBar = Number(input.meter.split("/")[0]) || 2;
    const totalBeats = explicit.reduce((sum, id) => sum + getRhythmPatternDefinition(id).durationBeats, 0);
    if (totalBeats <= 0 || Math.abs(totalBeats / beatsPerBar - Math.round(totalBeats / beatsPerBar)) > 1e-6) {
      return invalidExercise(`教师指定节奏共 ${totalBeats} 拍，不能构成完整 ${input.meter} 小节`);
    }
    return { ok: true, source: "teacher_sequence", patternIds: [...explicit], barCount: Math.round(totalBeats / beatsPerBar) };
  }

  const requestedPool = input.allowedPatternIds?.filter(Boolean) ?? [];
  if (requestedPool.length) {
    const unknown = requestedPool.find((id) => !BY_ID.has(id));
    if (unknown) return invalidExercise(`未知节奏型：${unknown}`);
    const eligiblePool = requestedPool.filter((id) => getRhythmPatternDefinition(id).durationBeats === 1);
    if (!eligiblePool.length) return invalidExercise("教师限定范围无法按拍号组成完整小节");
    const question = generateFromPool(input, eligiblePool);
    return { ok: true, source: "teacher_pool", patternIds: question.patternIds, barCount: question.barCount };
  }

  const question = generateRhythmEchoQuestion(input);
  return { ok: true, source: "random_fallback", patternIds: question.patternIds, barCount: question.barCount };
}

function generateFromPool(
  input: Pick<RhythmExerciseInput, "gradePreset" | "meter"> & { random?: () => number; previousPatternIds?: string[] },
  pool: string[]
) {
  const beatsPerBar = Number(input.meter.split("/")[0]) || 2;
  const barCount = input.gradePreset === "lower_primary" ? 2 : 4;
  const random = input.random ?? Math.random;
  const patternIds = Array.from({ length: beatsPerBar * barCount }, () => {
    const index = Math.min(pool.length - 1, Math.floor(Math.max(0, random()) * pool.length));
    return pool[index];
  });
  if (sameSequence(patternIds, input.previousPatternIds) && pool.length > 1) {
    const last = patternIds.length - 1;
    patternIds[last] = pool[(pool.indexOf(patternIds[last]) + 1) % pool.length];
  }
  return { patternIds, barCount };
}

function invalidExercise(error: string): ResolvedRhythmExercise {
  return { ok: false, source: "invalid", patternIds: [], barCount: 0, error };
}

function sameSequence(left: string[], right?: string[]) {
  return Boolean(right && left.length === right.length && left.every((item, index) => item === right[index]));
}
