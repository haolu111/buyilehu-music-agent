export type MusicElementControllerConfig = {
  tonic: string;
  mode: string;
  tempoMultiplier: number;
  rhythmDensity: string;
  instrument: string;
};

export type ListeningPlaybackNote = {
  midi?: number;
  pitch?: number;
  start?: number;
  start_seconds?: number;
  duration?: number;
  duration_seconds?: number;
  velocity?: number;
};

export type ListeningPlayback = {
  notes?: ListeningPlaybackNote[];
  instrument?: string;
};

export type ListeningTransformResponse = {
  session_id: string;
  cache_hit?: boolean;
  source_audio_url?: string;
  transformed_audio_url?: string;
  generated_midi_url?: string;
  transformed_midi_url?: string;
  stem_urls?: Record<string, string>;
  source_playback?: ListeningPlayback;
  transformed_playback?: ListeningPlayback;
  processing_strategy?: string;
  symbolic_available?: boolean;
  summary?: {
    teaching_suggestion?: string;
    tip?: string;
    [key: string]: unknown;
  };
  warning?: string;
  error?: string;
};

export const DEFAULT_MUSIC_ELEMENT_CONFIG: MusicElementControllerConfig = {
  tonic: "C",
  mode: "preserve",
  tempoMultiplier: 1,
  rhythmDensity: "preserve",
  instrument: "preserve"
};

export function listeningFileKey(file: File) {
  return `${file.name}:${file.size}:${file.lastModified}`;
}

export function needsListeningUpload(fileKey: string, sessionId: string, uploadedFileKey: string) {
  return !sessionId || fileKey !== uploadedFileKey;
}

export async function fileFromBoundSource(
  asset: { url: string; label?: string },
  fetcher: typeof fetch = fetch
) {
  try {
    const response = await fetcher(asset.url);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const blob = await response.blob();
    const urlName = decodeURIComponent(asset.url.split("/").pop()?.split("?")[0] || "");
    const label = asset.label?.includes(".") ? asset.label : urlName || asset.label || "bound-classroom-audio";
    return new File([blob], label, {
      type: blob.type || "audio/mpeg",
      lastModified: 0
    });
  } catch {
    throw new Error("无法读取智能体已绑定的歌曲，请重新上传课堂音频。");
  }
}

export async function uploadListeningSource(
  file: File,
  fetcher: typeof fetch = fetch
): Promise<ListeningTransformResponse> {
  const form = new FormData();
  form.append("audio", file);
  return requestListeningTransform("/api/listening/upload", form, fetcher);
}

export async function transformListeningSession(
  sessionId: string,
  config: MusicElementControllerConfig,
  fetcher: typeof fetch = fetch
): Promise<ListeningTransformResponse> {
  const form = new FormData();
  form.append("session_id", sessionId);
  form.append("tonic", config.tonic);
  form.append("mode", config.mode);
  form.append("tempo_multiplier", String(config.tempoMultiplier));
  form.append("rhythm_density", config.rhythmDensity);
  form.append("instrument", config.instrument);
  return requestListeningTransform("/api/listening/transform", form, fetcher);
}

async function requestListeningTransform(
  url: string,
  form: FormData,
  fetcher: typeof fetch
): Promise<ListeningTransformResponse> {
  const response = await fetcher(url, { method: "POST", body: form });
  const payload = await response.json() as ListeningTransformResponse;
  if (!response.ok) throw new Error(payload.error || "音乐要素处理失败");
  if (!payload.session_id) throw new Error("音乐要素处理未返回会话 ID");
  return payload;
}
