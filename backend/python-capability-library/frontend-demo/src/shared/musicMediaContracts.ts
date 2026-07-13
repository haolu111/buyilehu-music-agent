export type GradePreset = "lower_primary" | "middle_primary" | "upper_primary";
export type MusicSourceKind = "teacher_upload" | "platform_authorized" | "soundfont_generated";
export type ScoreSource = "musicxml" | "midi" | "teacher_manual" | "recognized_draft";

export type MusicSourceAsset = {
  id: string;
  kind: MusicSourceKind;
  url: string;
  label: string;
  rightsStatus: "teacher_confirmation_required" | "platform_authorized" | "generated_reference";
};

export type ScoreEvent = {
  id: string;
  partId: string;
  measure: number;
  beat: number;
  startSeconds: number;
  durationSeconds: number;
  midi: number;
  lyric?: string;
  tie?: "start" | "continue" | "stop";
  rest: boolean;
};

export type NormalizedScoreTimeline = {
  version: "normalized_score_timeline_v1";
  source: ScoreSource;
  teacherConfirmed: boolean;
  meterMap: Array<{ measure: number; meter: string }>;
  tempoMap: Array<{ measure: number; bpm: number }>;
  keyMap: Array<{ measure: number; tonic: string; mode: string }>;
  events: ScoreEvent[];
};

export type MusicTrack = {
  id: string;
  label: string;
  sourceKind: "human_voice" | "uploaded_stem" | "soundfont_reference" | "lesson_audio";
  url?: string;
  instrument?: string;
  midiEvents?: ScoreEvent[];
  volume: number;
  muted: boolean;
  solo: boolean;
};

export type MusicMediaSession = {
  version: "music_media_session_v1";
  sessionId: string;
  gradePreset: GradePreset;
  sourceAssets: MusicSourceAsset[];
  scoreTimeline?: NormalizedScoreTimeline;
  tracks: MusicTrack[];
  transport: {
    bpm: number;
    playbackRate: number;
    transposeSemitones: number;
    countInBars: number;
    loop?: { startSeconds: number; endSeconds: number };
  };
  recordingPolicy: "local_session_only";
  networkMode: "single_device_classroom";
};

export const FIRST_BATCH_COMPONENTS = [
  { id: "song_audio_workbench", name: "音乐要素控制器", order: 1 },
  { id: "score_audio_sync_player", name: "谱面与声音同步播放器", order: 2 },
  { id: "ear_training_engine", name: "视唱练耳引擎", order: 3 },
  { id: "vocal_choir_training", name: "合唱与嗓音训练组件", order: 4 },
  { id: "ensemble_conductor", name: "多声部排练与指挥台", order: 5 }
] as const;

export function buildDefaultMusicMediaSession(input: {
  sessionId: string;
  sourceUrl?: string;
  sourceKind?: MusicSourceKind;
  gradePreset?: GradePreset;
}): MusicMediaSession {
  const sourceKind = input.sourceKind ?? "teacher_upload";
  const sourceAssets: MusicSourceAsset[] = input.sourceUrl ? [{
    id: "primary_source",
    kind: sourceKind,
    url: input.sourceUrl,
    label: sourceKind === "teacher_upload" ? "教师课堂音频" : "平台授权资源",
    rightsStatus: sourceKind === "teacher_upload" ? "teacher_confirmation_required" : "platform_authorized"
  }] : [];
  return {
    version: "music_media_session_v1",
    sessionId: input.sessionId,
    gradePreset: input.gradePreset ?? "middle_primary",
    sourceAssets,
    tracks: [],
    transport: {
      bpm: 88,
      playbackRate: 1,
      transposeSemitones: 0,
      countInBars: 1
    },
    recordingPolicy: "local_session_only",
    networkMode: "single_device_classroom"
  };
}

export function canUseScoreForStudentJudgement(timeline?: NormalizedScoreTimeline): boolean {
  if (!timeline?.teacherConfirmed) return false;
  return timeline.source === "musicxml" || timeline.source === "midi" || timeline.source === "teacher_manual";
}

export function scoreDurationSeconds(timeline?: NormalizedScoreTimeline): number {
  return Math.max(0, ...(timeline?.events ?? []).map((event) => event.startSeconds + event.durationSeconds));
}

export function musicMediaSessionFromWire(value: unknown): MusicMediaSession | undefined {
  if (!value || typeof value !== "object") return undefined;
  const raw = value as Record<string, unknown>;
  if (raw.version !== "music_media_session_v1") return undefined;
  const transport = (raw.transport && typeof raw.transport === "object" ? raw.transport : {}) as Record<string, unknown>;
  const sourceAssets = Array.isArray(raw.source_assets) ? raw.source_assets : Array.isArray(raw.sourceAssets) ? raw.sourceAssets : [];
  return {
    version: "music_media_session_v1",
    sessionId: String(raw.session_id ?? raw.sessionId ?? "classroom-session"),
    gradePreset: (raw.grade_preset ?? raw.gradePreset ?? "middle_primary") as GradePreset,
    sourceAssets: sourceAssets.map((item, index) => {
      const asset = (item && typeof item === "object" ? item : {}) as Record<string, unknown>;
      return {
        id: String(asset.id ?? `asset-${index + 1}`),
        kind: String(asset.kind ?? "teacher_upload") as MusicSourceKind,
        url: String(asset.url ?? ""),
        label: String(asset.label ?? "课堂音频"),
        rightsStatus: String(asset.rights_status ?? asset.rightsStatus ?? "teacher_confirmation_required") as MusicSourceAsset["rightsStatus"]
      };
    }),
    tracks: [],
    transport: {
      bpm: Number(transport.bpm ?? 88),
      playbackRate: Number(transport.playback_rate ?? transport.playbackRate ?? 1),
      transposeSemitones: Number(transport.transpose_semitones ?? transport.transposeSemitones ?? 0),
      countInBars: Number(transport.count_in_bars ?? transport.countInBars ?? 1)
    },
    recordingPolicy: "local_session_only",
    networkMode: "single_device_classroom"
  };
}
