import { Badge, Button, Flex, Grid, SegmentedControl, Text } from "@radix-ui/themes";
import { AlertTriangle, Pause, Play, Repeat2, RotateCcw } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import type { OpenSheetMusicDisplay as OpenSheetMusicDisplayInstance } from "opensheetmusicdisplay";
import type { NormalizedScoreTimeline } from "../shared/musicMediaContracts";
import { canUseScoreForStudentJudgement, scoreDurationSeconds } from "../shared/musicMediaContracts";
import { playHybridToneSequenceAsync, stopActiveSampledPlayback } from "../shared/realAudio";
import { activeScoreEventIndex, midiToSolfege } from "./musicClassroomLogic";
import { MusicClassroomFrame } from "./MusicClassroomFrame";

const demoTimeline: NormalizedScoreTimeline = {
  version: "normalized_score_timeline_v1",
  source: "teacher_manual",
  teacherConfirmed: true,
  meterMap: [{ measure: 1, meter: "2/4" }, { measure: 2, meter: "2/4" }],
  tempoMap: [{ measure: 1, bpm: 88 }],
  keyMap: [{ measure: 1, tonic: "C", mode: "major" }],
  events: [60, 62, 64, 67, 67, 64, 62, 60].map((midi, index) => ({
    id: `demo-${index + 1}`, partId: "melody", measure: Math.floor(index / 4) + 1, beat: index % 4 / 2 + 1,
    startSeconds: index * 0.42, durationSeconds: 0.34, midi, lyric: ["听", "见", "旋", "律", "跟", "着", "谱", "唱"][index], rest: false
  }))
};

export function ScoreAudioSyncPlayer({ timeline = demoTimeline, musicXmlUrl }: { timeline?: NormalizedScoreTimeline; musicXmlUrl?: string }) {
  const [view, setView] = useState<"numbered" | "staff">("numbered");
  const [playing, setPlaying] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const [loopMeasure, setLoopMeasure] = useState<number | null>(null);
  const startedAt = useRef(0);
  const timer = useRef<number | null>(null);
  const scoreHostRef = useRef<HTMLDivElement | null>(null);
  const osmdRef = useRef<OpenSheetMusicDisplayInstance | null>(null);
  const [scoreRenderStatus, setScoreRenderStatus] = useState("");
  const duration = scoreDurationSeconds(timeline);
  const ready = canUseScoreForStudentJudgement(timeline);
  const events = useMemo(() => loopMeasure ? timeline.events.filter((event) => event.measure === loopMeasure) : timeline.events, [loopMeasure, timeline.events]);
  const activeId = [...events].reverse().find((event) => elapsed >= event.startSeconds)?.id;
  const activeMusicXmlEventIndex = useMemo(() => activeScoreEventIndex(timeline.events, elapsed), [elapsed, timeline.events]);

  useEffect(() => () => { if (timer.current) cancelAnimationFrame(timer.current); stopActiveSampledPlayback(); }, []);
  useEffect(() => {
    if (!musicXmlUrl || !scoreHostRef.current || !ready) return;
    setScoreRenderStatus("正在加载已确认 MusicXML…");
    let cancelled = false;
    void import("opensheetmusicdisplay").then(({ OpenSheetMusicDisplay }) => {
      if (cancelled || !scoreHostRef.current) return;
      const osmd = new OpenSheetMusicDisplay(scoreHostRef.current, { autoResize: true, drawTitle: false, followCursor: true });
      osmdRef.current = osmd;
      return osmd.load(musicXmlUrl).then(() => {
        if (cancelled) return;
        osmd.render();
        osmd.cursor.show();
        setScoreRenderStatus("MusicXML 五线谱已加载");
      });
    }).catch(() => setScoreRenderStatus("MusicXML 渲染失败，请教师检查谱面文件"));
    return () => { cancelled = true; osmdRef.current = null; if (scoreHostRef.current) scoreHostRef.current.innerHTML = ""; };
  }, [musicXmlUrl, ready]);
  useEffect(() => {
    if (view !== "staff" || !musicXmlUrl || !scoreRenderStatus.includes("已加载") || activeMusicXmlEventIndex < 0) return;
    const cursor = osmdRef.current?.cursor;
    if (!cursor) return;
    cursor.reset();
    for (let index = 0; index < activeMusicXmlEventIndex; index += 1) cursor.next();
    cursor.show();
  }, [activeMusicXmlEventIndex, musicXmlUrl, scoreRenderStatus, view]);

  const play = async () => {
    if (!ready || !events.length) return;
    stopActiveSampledPlayback();
    const baseStart = events[0].startSeconds;
    setElapsed(baseStart);
    startedAt.current = performance.now() - baseStart * 1000;
    setPlaying(true);
    const result = await playHybridToneSequenceAsync([], {
      instrument: "acoustic_grand_piano", baseMidi: 0, allowOscillatorFallback: false,
      events: events.filter((event) => !event.rest).map((event) => ({ offset: event.midi, start: event.startSeconds - baseStart, duration: event.durationSeconds }))
    });
    if (!result.ok) { setPlaying(false); return; }
    const tick = () => {
      const next = (performance.now() - startedAt.current) / 1000;
      setElapsed(next);
      const lastEvent = events[events.length - 1];
      if (next < (lastEvent?.startSeconds ?? 0) + (lastEvent?.durationSeconds ?? 0)) timer.current = requestAnimationFrame(tick);
      else setPlaying(false);
    };
    timer.current = requestAnimationFrame(tick);
  };

  const stop = () => { if (timer.current) cancelAnimationFrame(timer.current); stopActiveSampledPlayback(); setPlaying(false); };

  return (
    <MusicClassroomFrame
      kicker="第一批 · 02" title="谱面与声音同步播放器"
      summary="五线谱、简谱、歌词和钢琴示范共用同一条音符时间轴。"
      status={ready ? "谱面已由教师确认" : "等待教师确认"}
      teacherBoundary="教师确认谱面版本、歌词对应、乐句划分及学生实际识谱和演唱表现。"
    >
      {!ready ? <section className="classroom-blocked"><AlertTriangle size={24} /><div><strong>识别草稿不能直接训练</strong><p>请教师确认 MusicXML、MIDI 或手工谱面后再开始。</p></div></section> : null}
      <Grid columns={{ initial: "1", md: "1fr .32fr" }} gap="4">
        <section className="classroom-console-panel score-sync-stage">
          <Flex align="center" justify="between" gap="3" wrap="wrap">
            <SegmentedControl.Root value={view} onValueChange={(value) => setView(value as "numbered" | "staff")}><SegmentedControl.Item value="numbered">简谱</SegmentedControl.Item><SegmentedControl.Item value="staff">五线谱</SegmentedControl.Item></SegmentedControl.Root>
            <Badge color="amber" variant="soft">{timeline.meterMap[0]?.meter ?? "2/4"} · {timeline.tempoMap[0]?.bpm ?? 88} BPM</Badge>
          </Flex>
          {view === "staff" && musicXmlUrl ? <div ref={scoreHostRef} className="osmd-score-host" aria-label="MusicXML五线谱同步视图" /> : <div className={`score-sync-surface ${view}`} aria-label={view === "staff" ? "五线谱同步视图" : "简谱同步视图"}>
            {view === "staff" ? <div className="staff-lines" aria-hidden="true">{Array.from({ length: 5 }, (_, index) => <i key={index} />)}</div> : null}
            {timeline.events.map((event) => <button key={event.id} className={event.id === activeId && playing ? "active" : ""} onClick={() => setElapsed(event.startSeconds)} title={`第${event.measure}小节 第${event.beat}拍`}><strong>{view === "numbered" ? numberForMidi(event.midi) : "●"}</strong><small>{event.lyric ?? midiToSolfege(event.midi)}</small></button>)}
          </div>}
          {scoreRenderStatus ? <Text size="2" color={scoreRenderStatus.includes("失败") ? "ruby" : "green"}>{scoreRenderStatus}</Text> : null}
          <div className="score-progress"><span style={{ width: `${Math.min(100, elapsed / Math.max(.1, duration) * 100)}%` }} /></div>
          <Flex gap="2" wrap="wrap"><Button size="3" highContrast onClick={() => void play()} disabled={!ready}>{playing ? <Pause size={18} /> : <Play size={18} />}{playing ? "重新播放" : "播放并跟谱"}</Button><Button size="3" variant="soft" onClick={stop}>停止</Button><Badge color="teal" variant="soft">{elapsed.toFixed(1)} 秒</Badge></Flex>
        </section>
        <aside className="classroom-console-panel classroom-control-stack">
          <Text weight="bold">乐句与小节循环</Text>
          {[...new Set(timeline.events.map((event) => event.measure))].map((measure) => <Button key={measure} variant={loopMeasure === measure ? "solid" : "soft"} onClick={() => setLoopMeasure(loopMeasure === measure ? null : measure)}><Repeat2 size={16} />第 {measure} 小节</Button>)}
          <Button color="gray" variant="soft" onClick={() => { stop(); setElapsed(0); setLoopMeasure(null); }}><RotateCcw size={16} />重置</Button>
          <Text size="1" color="gray">点击任一音符可定位；正式接入 MusicXML 后由同一事件 ID 驱动谱面光标和声音。</Text>
        </aside>
      </Grid>
    </MusicClassroomFrame>
  );
}

function numberForMidi(midi: number) { return ({ 0: "1", 2: "2", 4: "3", 5: "4", 7: "5", 9: "6", 11: "7" } as Record<number, string>)[midi % 12] ?? "♯"; }
