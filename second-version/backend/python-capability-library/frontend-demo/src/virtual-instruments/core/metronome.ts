export type Meter = "2/4" | "3/4" | "4/4" | "6/8";
export type MetronomeConfig = {
  bpm: number;
  meter: Meter;
  countInBars: 1;
  continueDuringPerformance: boolean;
  subdivision: "beat" | "eighth";
};

export type MetronomeTimelineEvent = {
  id: string;
  phase: "count_in" | "performance";
  beatIndex: number;
  timeMs: number;
  accent: "strong" | "weak";
  midi: 33 | 34;
};

export function normalizeMetronomeConfig(config: MetronomeConfig): MetronomeConfig {
  if (!["2/4", "3/4", "4/4", "6/8"].includes(config.meter)) throw new Error(`Unsupported meter: ${config.meter}`);
  return { ...config, bpm: Math.max(40, Math.min(160, Math.round(config.bpm))), countInBars: 1, subdivision: config.meter === "6/8" ? "eighth" : config.subdivision };
}

export function beatsPerBar(meter: Meter): number { return meter === "2/4" ? 2 : meter === "3/4" ? 3 : meter === "4/4" ? 4 : 6; }
export function metronomeBeatMs(config: MetronomeConfig): number { return 60000 / normalizeMetronomeConfig(config).bpm; }

export function buildMetronomeTimeline(config: MetronomeConfig, performanceBars: number): MetronomeTimelineEvent[] {
  const normalized = normalizeMetronomeConfig(config);
  const perBar = beatsPerBar(normalized.meter);
  const countInCount = perBar * normalized.countInBars;
  const performanceCount = normalized.continueDuringPerformance ? perBar * Math.max(0, Math.floor(performanceBars)) : 0;
  const beatMs = metronomeBeatMs(normalized);
  return Array.from({ length: countInCount + performanceCount }, (_, index) => {
    const phase = index < countInCount ? "count_in" as const : "performance" as const;
    const localIndex = phase === "count_in" ? index : index - countInCount;
    const strong = localIndex % perBar === 0;
    return { id: `${phase}-${localIndex}`, phase, beatIndex: localIndex, timeMs: index * beatMs, accent: strong ? "strong" : "weak", midi: strong ? 34 : 33 };
  });
}
