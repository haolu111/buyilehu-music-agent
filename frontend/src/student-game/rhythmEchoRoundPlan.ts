export type RhythmTimelineItem = {
  step: string;
  label: string;
  time_beats: number;
  duration_beats: number;
  hit_required: boolean;
};

export type RhythmRoundPatch = {
  pattern_steps?: string[];
  pattern_timeline?: RhythmTimelineItem[];
};

export type RhythmRoundPatches = Record<string, RhythmRoundPatch>;

export type RhythmRoundPlan = {
  active_round: number;
  round_count: number;
  round_patches: RhythmRoundPatches;
  pattern_steps: string[];
  pattern_timeline: RhythmTimelineItem[];
};

const ALLOWED_PATTERN_STEPS = new Set(["quarter", "eighth_pair", "eighth", "half", "rest", "syncopation", "dotted_quarter"]);
const STEP_LABELS: Record<string, string> = {
  quarter: "四分",
  eighth_pair: "二八",
  eighth: "八分",
  half: "二分",
  rest: "休止",
  syncopation: "切分",
  dotted_quarter: "附点四分"
};

export function resolveRhythmRoundPlan(raw: Record<string, unknown>): RhythmRoundPlan {
  const roundPatches = normalizeRoundPatches(raw.round_patches);
  const highestPatchedRound = Object.keys(roundPatches).reduce((highest, key) => {
    const match = /^round_(\d+)$/.exec(key);
    return match ? Math.max(highest, Number(match[1])) : highest;
  }, 1);
  const roundCount = clampNumber(Number(raw.round_count), 1, 12, highestPatchedRound);
  const activeRound = clampNumber(Number(raw.active_round ?? raw.current_round), 1, roundCount, 1);
  const basePatternSteps = normalizePatternSteps(raw.pattern_steps);
  const baseTimeline = normalizeTimeline(raw.pattern_timeline, basePatternSteps);
  const activePatch = roundPatches[`round_${activeRound}`];
  const patchedPatternSteps = activePatch?.pattern_steps?.length ? activePatch.pattern_steps : [];
  const patternSteps = patchedPatternSteps.length ? patchedPatternSteps : basePatternSteps;
  const patchedTimeline = activePatch?.pattern_timeline?.length ? activePatch.pattern_timeline : [];
  const patternTimeline = patchedTimeline.length
    ? patchedTimeline
    : patchedPatternSteps.length
      ? normalizeTimeline(undefined, patternSteps)
      : baseTimeline;
  return {
    active_round: activeRound,
    round_count: roundCount,
    round_patches: roundPatches,
    pattern_steps: patternSteps,
    pattern_timeline: patternTimeline
  };
}

export function normalizePatternSteps(value: unknown) {
  const steps = normalizePatternStepsOrEmpty(value);
  return steps.length ? steps : ["quarter", "quarter"];
}

export function normalizeTimeline(value: unknown, patternSteps: string[]): RhythmTimelineItem[] {
  const timeline = normalizeTimelineOrEmpty(value);
  if (timeline.length && timeline.some((item) => item.hit_required)) return timeline;
  let current = 0;
  const generated: RhythmTimelineItem[] = [];
  patternSteps.forEach((step) => {
    expandStep(step).forEach((item) => {
      generated.push({ ...item, time_beats: current });
      current += item.duration_beats;
    });
  });
  return generated;
}

function normalizeRoundPatches(value: unknown): RhythmRoundPatches {
  if (!isRecord(value)) return {};
  return Object.entries(value).reduce<RhythmRoundPatches>((patches, [key, patchValue]) => {
    if (!/^round_\d+$/.test(key) || !isRecord(patchValue)) return patches;
    const patch: RhythmRoundPatch = {};
    const patternSteps = normalizePatternStepsOrEmpty(patchValue.pattern_steps);
    if (patternSteps.length) patch.pattern_steps = patternSteps;
    const timeline = normalizeTimelineOrEmpty(patchValue.pattern_timeline);
    if (timeline.length) patch.pattern_timeline = timeline;
    if (patch.pattern_steps || patch.pattern_timeline) patches[key] = patch;
    return patches;
  }, {});
}

function normalizePatternStepsOrEmpty(value: unknown) {
  return Array.isArray(value) ? value.map(String).filter((step) => ALLOWED_PATTERN_STEPS.has(step)) : [];
}

function normalizeTimelineOrEmpty(value: unknown): RhythmTimelineItem[] {
  if (!Array.isArray(value) || !value.length) return [];
  return value.filter(isRecord).map((item) => ({
    step: String(item.step || "quarter"),
    label: labelForStep(String(item.step || "quarter"), item.label),
    time_beats: clampFloat(Number(item.time_beats), 0, 64, 0),
    duration_beats: clampFloat(Number(item.duration_beats), 0.25, 4, 1),
    hit_required: item.hit_required !== false
  }));
}

function expandStep(step: string): Omit<RhythmTimelineItem, "time_beats">[] {
  if (step === "eighth_pair") {
    return [
      { step: "eighth", label: "八分", duration_beats: 0.5, hit_required: true },
      { step: "eighth", label: "八分", duration_beats: 0.5, hit_required: true }
    ];
  }
  if (step === "half") return [{ step: "half", label: "二分", duration_beats: 2, hit_required: true }];
  if (step === "dotted_quarter") return [{ step: "dotted_quarter", label: "附点四分", duration_beats: 1.5, hit_required: true }];
  if (step === "rest") return [{ step: "rest", label: "休", duration_beats: 1, hit_required: false }];
  if (step === "syncopation") {
    return [
      { step: "sixteenth", label: "切分前十六", duration_beats: 0.25, hit_required: true },
      { step: "eighth", label: "切分中八分", duration_beats: 0.5, hit_required: true },
      { step: "sixteenth", label: "切分后十六", duration_beats: 0.25, hit_required: true }
    ];
  }
  if (step === "eighth") return [{ step: "eighth", label: "八分", duration_beats: 0.5, hit_required: true }];
  return [{ step: "quarter", label: "四分", duration_beats: 1, hit_required: true }];
}

function labelForStep(step: string, label: unknown) {
  const text = String(label || "").trim();
  if (!text || text === "ta" || text === "ti" || text === "ta-a" || text === "ta." || text === "syn" || text === "co" || text === "pa") {
    return STEP_LABELS[step] ?? "四分";
  }
  return text;
}

function clampNumber(value: number, min: number, max: number, fallback: number) {
  if (!Number.isFinite(value)) return fallback;
  return Math.max(min, Math.min(max, Math.round(value)));
}

function clampFloat(value: number, min: number, max: number, fallback: number) {
  if (!Number.isFinite(value)) return fallback;
  return Math.max(min, Math.min(max, value));
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
