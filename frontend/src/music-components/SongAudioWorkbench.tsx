import { Badge, Button, Flex, Select, Text } from "@radix-ui/themes";
import { Download, FileAudio, RotateCcw, SlidersHorizontal, Upload, WandSparkles, Waves } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import type { MusicMediaSession, MusicSourceAsset } from "../shared/musicMediaContracts";
import { buildDefaultMusicMediaSession } from "../shared/musicMediaContracts";
import { playHybridToneSequenceAsync } from "../shared/realAudio";
import {
  DEFAULT_MUSIC_ELEMENT_CONFIG,
  fileFromBoundSource,
  listeningFileKey,
  needsListeningUpload,
  transformListeningSession,
  uploadListeningSource,
  type ListeningPlayback,
  type ListeningTransformResponse,
  type MusicElementControllerConfig
} from "./musicElementController";
import { MusicClassroomFrame } from "./MusicClassroomFrame";

const TONIC_OPTIONS = ["C", "D", "E", "F", "G", "A", "B"];
const MODE_OPTIONS = [
  ["preserve", "保持原调式"],
  ["western_major", "西洋大调"],
  ["western_minor", "西洋小调"],
  ["chinese_pentatonic", "中国五声调式"],
  ["chinese_heptatonic", "中国七声调式"],
  ["dorian", "多利亚"],
  ["phrygian", "弗里吉亚"],
  ["blues", "布鲁斯"]
] as const;
const RHYTHM_OPTIONS = [
  ["preserve", "保持原节奏"],
  ["dense", "更密集"],
  ["relaxed", "更舒缓"]
] as const;
const INSTRUMENT_OPTIONS = [
  ["preserve", "保持原音色"],
  ["piano", "钢琴"],
  ["violin", "小提琴"],
  ["guzheng", "古筝"],
  ["flute", "长笛"]
] as const;

export function SongAudioWorkbench({
  initialSession = buildDefaultMusicMediaSession({ sessionId: "audio-workbench" }),
  onSessionChange
}: {
  initialSession?: MusicMediaSession;
  onSessionChange?: (session: MusicMediaSession) => void;
}) {
  const initialAsset = initialSession.sourceAssets[0];
  const [session, setSession] = useState(initialSession);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [boundSourceFile, setBoundSourceFile] = useState<File | null>(null);
  const [localPreviewUrl, setLocalPreviewUrl] = useState("");
  const [sessionId, setSessionId] = useState("");
  const [uploadedFileKey, setUploadedFileKey] = useState("");
  const [config, setConfig] = useState<MusicElementControllerConfig>({
    ...DEFAULT_MUSIC_ELEMENT_CONFIG,
    tempoMultiplier: initialSession.transport.playbackRate
  });
  const [result, setResult] = useState<ListeningTransformResponse | null>(null);
  const [status, setStatus] = useState(initialAsset?.url ? "已绑定课堂歌曲，可以开始解析和变化音乐要素。" : "请选择课堂歌曲后开始。" );
  const [processing, setProcessing] = useState(false);

  useEffect(() => onSessionChange?.(session), [onSessionChange, session]);
  useEffect(() => {
    if (!selectedFile) { setLocalPreviewUrl(""); return; }
    const url = URL.createObjectURL(selectedFile);
    setLocalPreviewUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [selectedFile]);

  const sourceUrl = result?.source_audio_url || localPreviewUrl || initialAsset?.url || "";
  const sourceLabel = selectedFile?.name || initialAsset?.label || "等待教师选择歌曲";
  const transformedUrl = result?.transformed_audio_url || "";
  const downloadItems = useMemo(() => [
    ["识别旋律 MIDI", result?.generated_midi_url],
    ["变化后 MIDI", result?.transformed_midi_url],
    ["变化后音频", result?.transformed_audio_url]
  ].filter((item): item is [string, string] => Boolean(item[1])), [result]);

  const updateConfig = <Key extends keyof MusicElementControllerConfig>(key: Key, value: MusicElementControllerConfig[Key]) => {
    setConfig((current) => ({ ...current, [key]: value }));
  };

  const chooseFile = (file?: File) => {
    if (!file) return;
    setSelectedFile(file);
    setBoundSourceFile(null);
    setSessionId("");
    setUploadedFileKey("");
    setResult(null);
    setStatus(`已选择“${file.name}”，点击生成后首次解析。`);
  };

  const resolveSourceFile = async () => {
    if (selectedFile) return selectedFile;
    if (boundSourceFile) return boundSourceFile;
    if (!initialAsset?.url) throw new Error("请先上传一段课堂歌曲或片段。");
    setStatus("正在读取智能体已绑定的课堂歌曲…");
    const file = await fileFromBoundSource(initialAsset);
    setBoundSourceFile(file);
    return file;
  };

  const generateComparison = async () => {
    setProcessing(true);
    try {
      const file = await resolveSourceFile();
      const fileKey = listeningFileKey(file);
      let activeSessionId = sessionId;
      if (needsListeningUpload(fileKey, activeSessionId, uploadedFileKey)) {
        setStatus("正在首次解析歌曲；后续修改参数将复用本次结果…");
        const uploaded = await uploadListeningSource(file);
        activeSessionId = uploaded.session_id;
        setSessionId(activeSessionId);
        setUploadedFileKey(fileKey);
      } else {
        setStatus("正在复用歌曲解析结果，变化音乐要素…");
      }

      const transformed = await transformListeningSession(activeSessionId, config);
      setResult(transformed);
      setStatus(transformed.cache_hit ? "已从缓存取回这个对比版本。" : "音乐要素对比版本已生成。" );
      syncMediaSession(transformed);
    } catch (error) {
      setStatus(`处理失败：${error instanceof Error ? error.message : "这段音频暂时没有听清楚。"}`);
    } finally {
      setProcessing(false);
    }
  };

  const syncMediaSession = (transformed: ListeningTransformResponse) => {
    const sourceAssets: MusicSourceAsset[] = [];
    if (transformed.source_audio_url) {
      sourceAssets.push({
        id: "primary_source",
        kind: initialAsset?.kind || "teacher_upload",
        url: transformed.source_audio_url,
        label: sourceLabel,
        rightsStatus: initialAsset?.rightsStatus || "teacher_confirmation_required"
      });
    }
    if (transformed.transformed_audio_url) {
      sourceAssets.push({
        id: "music_element_variant",
        kind: "soundfont_generated",
        url: transformed.transformed_audio_url,
        label: `${sourceLabel} · 音乐要素变化版`,
        rightsStatus: "generated_reference"
      });
    }
    setSession((current) => ({
      ...current,
      sourceAssets: sourceAssets.length ? sourceAssets : current.sourceAssets,
      transport: { ...current.transport, playbackRate: config.tempoMultiplier }
    }));
  };

  const resetElements = () => {
    setConfig(DEFAULT_MUSIC_ELEMENT_CONFIG);
    setResult(null);
    setStatus(sessionId ? "音乐要素已重置；歌曲解析缓存仍然保留。" : "音乐要素已重置。" );
  };

  const playPlayback = async (playback: ListeningPlayback | undefined, instrument: string) => {
    const notes = playback?.notes || [];
    if (!notes.length) { setStatus("当前没有可试听的识别旋律。"); return; }
    const playbackResult = await playHybridToneSequenceAsync([], {
      instrument: instrument === "preserve" ? playback?.instrument || "acoustic_grand_piano" : instrument,
      baseMidi: 0,
      allowOscillatorFallback: false,
      events: notes.map((note) => ({
        offset: Number(note.pitch ?? note.midi ?? 60),
        start: Number(note.start ?? note.start_seconds ?? 0),
        duration: Number(note.duration ?? note.duration_seconds ?? .3)
      }))
    });
    if (!playbackResult.ok) setStatus("真实乐器音色加载失败，请教师检查声音资源。");
  };

  return (
    <MusicClassroomFrame
      kicker="第一批 · 01"
      title="音乐要素控制器"
      summary="直接复用现成聆听调音台：上传歌曲后改变主音、调式、速度、节奏密度或音色，并对比真实处理结果。"
      status={sessionId ? "歌曲已解析，可快速调整" : "等待首次解析"}
      teacherBoundary="教师确认素材版权、变化目标、学生音域和作品风格；网页只提供音频处理与客观对比证据。"
    >
      <section className="classroom-console-panel music-element-source-panel">
        <Flex align="center" justify="between" gap="3" wrap="wrap">
          <div>
            <Text weight="bold">课堂歌曲</Text>
            <Text as="p" size="2" color="gray">{sourceLabel}</Text>
          </div>
          <label className="classroom-upload-button"><Upload size={17} />上传或更换歌曲<input type="file" accept="audio/*" onChange={(event) => chooseFile(event.target.files?.[0])} /></label>
        </Flex>
        {sourceUrl ? <audio controls preload="metadata" src={sourceUrl} className="music-element-source-audio" aria-label="当前课堂歌曲" /> : <div className="music-element-empty"><FileAudio size={28} /><span>尚未绑定歌曲</span></div>}
      </section>

      <section className="classroom-console-panel">
        <Flex align="center" gap="2"><SlidersHorizontal size={19} /><Text weight="bold">音乐要素控制</Text></Flex>
        <div className="music-element-control-grid">
          <ControllerSelect label="同主音" value={config.tonic} options={TONIC_OPTIONS.map((value) => [value, value] as const)} onChange={(value) => updateConfig("tonic", value)} />
          <ControllerSelect label="大小调／调式转换" value={config.mode} options={MODE_OPTIONS} onChange={(value) => updateConfig("mode", value)} />
          <label className="music-element-field">
            <span>BPM／速度倍率</span>
            <input type="number" min="0.5" max="2" step="0.1" value={config.tempoMultiplier} onChange={(event) => updateConfig("tempoMultiplier", Math.max(.5, Math.min(2, Number(event.target.value) || 1)))} />
            <small>{config.tempoMultiplier.toFixed(1)} ×</small>
          </label>
          <ControllerSelect label="节奏密度" value={config.rhythmDensity} options={RHYTHM_OPTIONS} onChange={(value) => updateConfig("rhythmDensity", value)} />
          <ControllerSelect label="音色切换" value={config.instrument} options={INSTRUMENT_OPTIONS} onChange={(value) => updateConfig("instrument", value)} />
        </div>
        <Flex gap="2" wrap="wrap">
          <Button size="3" highContrast disabled={processing || (!selectedFile && !initialAsset?.url)} onClick={() => void generateComparison()}><WandSparkles size={18} />{processing ? "正在处理…" : "生成对比版本"}</Button>
          <Button size="3" variant="soft" color="gray" onClick={resetElements}><RotateCcw size={17} />重置音乐要素</Button>
        </Flex>
        <div className={`music-element-status ${status.startsWith("处理失败") ? "error" : ""}`}><Waves size={17} /><span>{status}</span></div>
      </section>

      {result ? (
        <section className="classroom-console-panel music-element-result-panel">
          <Flex align="center" justify="between" gap="2" wrap="wrap">
            <Text weight="bold">原版与变化版对比</Text>
            <Flex gap="2" wrap="wrap">
              <Badge color={result.cache_hit ? "amber" : "green"} variant="soft">{result.cache_hit ? "缓存版本" : "新生成"}</Badge>
              <Badge color="teal" variant="soft">{result.processing_strategy === "original_audio_dsp" ? "原声音频处理" : "旋律与音色重构"}</Badge>
            </Flex>
          </Flex>
          <Text as="p" size="2" color="gray">{result.summary?.teaching_suggestion || result.summary?.tip || "请让学生比较两个版本中的音乐要素变化。"}</Text>
          <div className="music-element-compare-grid">
            <ComparisonAudio title="原版歌曲" url={result.source_audio_url} emptyText="原版音频不可用，可试听识别旋律。" />
            <ComparisonAudio title="变化后版本" url={result.transformed_audio_url} emptyText="没有生成音频文件，可试听真实乐器重构版本。" />
          </div>
          <Flex gap="2" wrap="wrap">
            <Button variant="soft" onClick={() => void playPlayback(result.source_playback, result.source_playback?.instrument || "acoustic_grand_piano")}>试听识别旋律</Button>
            <Button variant="soft" onClick={() => void playPlayback(result.transformed_playback, config.instrument)}>试听变换版本</Button>
          </Flex>
          {downloadItems.length ? <ResultLinks title="下载结果" items={downloadItems} /> : null}
          {Object.keys(result.stem_urls || {}).length ? <ResultLinks title="课堂分轨" items={Object.entries(result.stem_urls || {})} /> : null}
          {result.warning ? <div className="music-element-warning">{result.warning}</div> : null}
        </section>
      ) : null}
    </MusicClassroomFrame>
  );
}

function ControllerSelect({ label, value, options, onChange }: { label: string; value: string; options: ReadonlyArray<readonly [string, string]>; onChange: (value: string) => void }) {
  return <label className="music-element-field"><span>{label}</span><Select.Root value={value} onValueChange={onChange}><Select.Trigger aria-label={label} /><Select.Content>{options.map(([id, name]) => <Select.Item key={id} value={id}>{name}</Select.Item>)}</Select.Content></Select.Root></label>;
}

function ComparisonAudio({ title, url, emptyText }: { title: string; url?: string; emptyText: string }) {
  return <article className="music-element-audio-card"><strong>{title}</strong>{url ? <audio controls preload="metadata" src={url} /> : <Text size="2" color="gray">{emptyText}</Text>}</article>;
}

function ResultLinks({ title, items }: { title: string; items: Array<[string, string]> }) {
  return <div className="music-element-link-group"><strong>{title}</strong><Flex gap="2" wrap="wrap">{items.map(([label, url]) => <Button key={`${label}-${url}`} variant="soft" asChild><a href={url} target="_blank" rel="noreferrer"><Download size={15} />{label}</a></Button>)}</Flex></div>;
}
