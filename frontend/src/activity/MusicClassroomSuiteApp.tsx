import { Badge, Button, Container, Flex, Heading, Text } from "@radix-ui/themes";
import { AudioLines, BookOpenCheck, Ear, Mic2, Music4 } from "lucide-react";
import { useMemo, useState } from "react";
import {
  EarTrainingEngine,
  EnsembleConductor,
  ScoreAudioSyncPlayer,
  SongAudioWorkbench,
  VocalChoirTraining
} from "../music-components";
import { FIRST_BATCH_COMPONENTS, musicMediaSessionFromWire } from "../shared/musicMediaContracts";
import "./primaryActivity.css";
import "./musicClassroomSuite.css";

const iconById = {
  song_audio_workbench: AudioLines,
  score_audio_sync_player: BookOpenCheck,
  ear_training_engine: Ear,
  vocal_choir_training: Mic2,
  ensemble_conductor: Music4
};

type MusicClassroomSuiteRuntimeState = {
  config?: {
    runtime_component_id?: string;
    media_session?: unknown;
  };
};

declare global {
  interface Window {
    __MUSIC_CLASSROOM_SUITE_STATE__?: MusicClassroomSuiteRuntimeState;
  }
}

export function MusicClassroomSuiteApp() {
  const runtimeState = window.__MUSIC_CLASSROOM_SUITE_STATE__;
  const mediaSession = useMemo(() => musicMediaSessionFromWire(runtimeState?.config?.media_session), [runtimeState?.config?.media_session]);
  const requested = useMemo(() => new URLSearchParams(window.location.search).get("component") ?? runtimeState?.config?.runtime_component_id ?? "song_audio_workbench", [runtimeState?.config?.runtime_component_id]);
  const [active, setActive] = useState(FIRST_BATCH_COMPONENTS.some((item) => item.id === requested) ? requested : "song_audio_workbench");
  return (
    <main className="music-classroom-suite-shell">
      <Container size="4" px="4">
        <header className="classroom-suite-hero">
          <div><Badge color="green" variant="soft">真实课堂组件 · 第一批</Badge><Heading as="h1" size="8">音乐课堂工作站</Heading><Text as="p" size="3" color="gray">统一声音、谱面和课堂时间轴；教师掌握音乐专业判断。</Text></div>
          <div className="classroom-suite-principles"><span>先听</span><i /><span>再做</span><i /><span>反馈</span><i /><span>教师确认</span></div>
        </header>
        <nav className="classroom-suite-nav" aria-label="第一批音乐课堂组件">
          {FIRST_BATCH_COMPONENTS.map((item) => { const Icon = iconById[item.id]; return <button key={item.id} data-component-id={item.id} className={active === item.id ? "active" : ""} onClick={() => setActive(item.id)}><Icon size={20} /><span>0{item.order}</span><strong>{item.name}</strong></button>; })}
        </nav>
        <Flex className="classroom-suite-context" align="center" justify="between" gap="3" wrap="wrap"><Text size="2">当前为单机课堂模式，适合教师电脑、触屏、平板和投屏。</Text><Button variant="soft" asChild><a href="/template-console/music-education-review.html">返回专业审核库</a></Button></Flex>
        {active === "song_audio_workbench" ? <SongAudioWorkbench initialSession={mediaSession} /> : null}
        {active === "score_audio_sync_player" ? <ScoreAudioSyncPlayer /> : null}
        {active === "ear_training_engine" ? <EarTrainingEngine /> : null}
        {active === "vocal_choir_training" ? <VocalChoirTraining /> : null}
        {active === "ensemble_conductor" ? <EnsembleConductor /> : null}
      </Container>
    </main>
  );
}
