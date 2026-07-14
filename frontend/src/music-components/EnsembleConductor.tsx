import { Badge, Button, Flex, Grid, Slider, Text } from "@radix-ui/themes";
import { Maximize2, Pause, Play, RotateCcw, Volume2, VolumeX } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import type { MusicTrack } from "../shared/musicMediaContracts";
import { playHybridToneSequenceAsync, stopActiveSampledPlayback } from "../shared/realAudio";
import { audibleTracks, clearScheduledCueHandles } from "./musicClassroomLogic";
import { MusicClassroomFrame } from "./MusicClassroomFrame";

const initialTracks: MusicTrack[] = [
  { id: "voice-one", label: "儿童声部一", sourceKind: "soundfont_reference", instrument: "flute", volume: .8, muted: false, solo: false },
  { id: "voice-two", label: "儿童声部二", sourceKind: "soundfont_reference", instrument: "clarinet", volume: .72, muted: false, solo: false },
  { id: "orff", label: "奥尔夫伴奏", sourceKind: "soundfont_reference", instrument: "xylophone", volume: .62, muted: false, solo: false }
];

export function EnsembleConductor() {
  const [tracks, setTracks] = useState(initialTracks);
  const [playing, setPlaying] = useState(false);
  const [cue, setCue] = useState("等待教师预备");
  const stageRef = useRef<HTMLDivElement | null>(null);
  const scheduledCueHandles = useRef<number[]>([]);
  const playbackRun = useRef(0);
  const audible = useMemo(() => audibleTracks(tracks), [tracks]);
  const updateTrack = (id: string, patch: Partial<MusicTrack>) => setTracks((current) => current.map((track) => track.id === id ? { ...track, ...patch } : track));

  const cancelScheduledCues = () => {
    playbackRun.current += 1;
    clearScheduledCueHandles(scheduledCueHandles.current, (handle) => window.clearTimeout(handle));
  };

  useEffect(() => () => { cancelScheduledCues(); stopActiveSampledPlayback(); }, []);

  const playEnsemble = async () => {
    cancelScheduledCues(); stopActiveSampledPlayback();
    const run = playbackRun.current;
    setPlaying(true); setCue("预备拍：听节拍器，不演奏");
    const countIn = await playHybridToneSequenceAsync([0, 0, 0, 0], { instrument: "woodblock", baseMidi: 76, gap: .45, duration: .12, gain: .55, allowOscillatorFallback: false });
    if (playbackRun.current !== run) return;
    if (!countIn.ok) { setPlaying(false); setCue("真实节拍器音色加载失败，请教师检查声音资源"); return; }
    const entranceHandle = window.setTimeout(() => {
      if (playbackRun.current !== run) return;
      setCue("第 1 小节：全部进入");
      audible.forEach((track, index) => void playHybridToneSequenceAsync(index === 1 ? [7, 5, 4, 2, 0] : [0, 2, 4, 5, 7], { instrument: track.instrument, baseMidi: 60 - index * 5, gap: .45, duration: .36, gain: track.volume, allowOscillatorFallback: false }));
      const finishHandle = window.setTimeout(() => {
        if (playbackRun.current !== run) return;
        setPlaying(false); setCue("结束：看教师收拍");
      }, 2700);
      scheduledCueHandles.current.push(finishHandle);
    }, 1800);
    scheduledCueHandles.current.push(entranceHandle);
  };
  const stop = () => { cancelScheduledCues(); stopActiveSampledPlayback(); setPlaying(false); setCue("已暂停，等待教师指挥"); };

  return (
    <MusicClassroomFrame kicker="第一批 · 05" title="多声部排练与指挥台" summary="儿童二声部、轮唱和课堂乐队共用分轨控制、预备拍与小节进入提示。" teacherBoundary="网页记录进入和节奏证据；音准、声部平衡、合作聆听与音乐表现由教师判断。">
      <section ref={stageRef} className={`conductor-cue-stage ${playing ? "playing" : ""}`}><span>指挥提示</span><strong>{cue}</strong><Flex className="conductor-actions" gap="2"><Button size="3" highContrast onClick={() => void playEnsemble()} disabled={playing}><Play size={18} />预备拍后合奏</Button><Button size="3" variant="soft" onClick={stop}><Pause size={18} />暂停</Button><Button size="3" variant="soft" onClick={() => void stageRef.current?.requestFullscreen()}><Maximize2 size={17} />全屏指挥</Button></Flex></section>
      <Grid columns={{ initial: "1", md: "3" }} gap="3" className="ensemble-track-grid">
        {tracks.map((track) => <article key={track.id} className={`ensemble-track-console ${track.muted ? "muted" : ""}`}>
          <Flex align="center" justify="between" gap="2"><div><strong>{track.label}</strong><small>{track.sourceKind === "soundfont_reference" ? "真实乐器 SoundFont 代奏" : "教师上传分轨"}</small></div><Badge color={track.solo ? "amber" : track.muted ? "gray" : "green"} variant="soft">{track.solo ? "独奏" : track.muted ? "静音" : "合奏"}</Badge></Flex>
          <label className="classroom-field"><span>音量 <b>{Math.round(track.volume * 100)}%</b></span><Slider value={[track.volume]} min={0} max={1} step={.05} onValueChange={([value]) => updateTrack(track.id, { volume: value })} /></label>
          <Flex gap="2"><Button size="2" variant="soft" onClick={() => updateTrack(track.id, { muted: !track.muted })}>{track.muted ? <Volume2 size={15} /> : <VolumeX size={15} />}{track.muted ? "恢复" : "静音"}</Button><Button size="2" variant={track.solo ? "solid" : "soft"} onClick={() => updateTrack(track.id, { solo: !track.solo })}>独奏</Button></Flex>
        </article>)}
      </Grid>
      <Flex justify="between" gap="3" wrap="wrap" className="ensemble-footer"><Text size="2" color="gray">人声声部与乐器代奏必须明确标注；当前示例为乐器参考音，不冒充真人合唱。</Text><Button variant="soft" color="gray" onClick={() => { stop(); setTracks(initialTracks); setCue("等待教师预备"); }}><RotateCcw size={16} />重置声部</Button></Flex>
    </MusicClassroomFrame>
  );
}
