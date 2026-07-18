import { Badge, Button, Container, Flex, Grid, Heading, Text, TextArea } from "@radix-ui/themes";
import { CheckCircle2, Hand, Music2, Play, RotateCcw, Volume2, VolumeX } from "lucide-react";
import { useMemo, useState } from "react";
import { RhythmNotation } from "../music-components/RhythmNotation";
import { playPlayableInstrumentSequence } from "../shared/realAudio";
import { playableInstrumentAssetFor } from "./playableInstrumentAssets";
import { formalRhythmLabel, formalRhythmName } from "./rhythmNaming";
import {
  buildOrffPlaybackQueue,
  buildDefaultOrffGroupRecords,
  buildOrffEntryPlan,
  buildOrffPerformanceExport,
  buildOrffSessionExport,
  judgeOrffPerformanceRecord,
  judgeOrffEntryTiming,
  recordOrffEnsembleEvent,
  summarizeOrffEntryAttempts,
  summarizeOrffPerformance,
  updateOrffCriterion,
  updateOrffEvidence,
  type OrffEnsembleEvent,
  type OrffEntryTimingResult,
  type OrffCriterionStatus
} from "./orffEnsembleLogic";
import "./primaryActivity.css";
import { ReadableData } from "./ReadableData";

type OrffEnsembleState = {
  workflow?: {
    education_alignment?: {
      primary_competency?: string;
      music_elements?: string[];
      student_practices?: string[];
    };
  };
  config?: {
    group_tasks?: string[];
    rhythm_pattern?: string[];
    instrument_parts?: string[];
    meter?: string;
    bpm?: number;
    mute_solo_enabled?: boolean;
    assessment_criteria?: string[];
    entry_every_bars?: number;
  };
};

declare global {
  interface Window {
    __ORFF_ENSEMBLE_STATE__?: OrffEnsembleState;
  }
}

const defaultState: OrffEnsembleState = {
  workflow: {
    education_alignment: {
      primary_competency: "艺术表现",
      music_elements: ["节奏", "合作", "力度"],
      student_practices: ["play", "listen", "cooperate", "perform"]
    }
  },
  config: {
    group_tasks: ["A组手鼓强拍", "B组木鱼稳定拍", "C组沙锤弱拍", "D组三角铁点缀"],
    rhythm_pattern: ["quarter", "eighth_pair", "quarter", "rest"],
    instrument_parts: ["hand_drum", "woodblock", "shaker", "triangle"],
    meter: "2/4",
    bpm: 88,
    mute_solo_enabled: true,
    assessment_criteria: ["节奏稳定", "按时进入", "能听同伴"],
    entry_every_bars: 1
  }
};

export function OrffEnsembleActivity({ state = window.__ORFF_ENSEMBLE_STATE__ ?? defaultState }: { state?: OrffEnsembleState }) {
  const config = state.config ?? defaultState.config ?? {};
  const tasks = config.group_tasks?.length ? config.group_tasks : defaultState.config?.group_tasks ?? [];
  const parts = config.instrument_parts?.length ? config.instrument_parts : defaultState.config?.instrument_parts ?? [];
  const rhythm = config.rhythm_pattern?.length ? config.rhythm_pattern : defaultState.config?.rhythm_pattern ?? [];
  const alignment = state.workflow?.education_alignment ?? defaultState.workflow?.education_alignment ?? {};
  const criteria = config.assessment_criteria?.length ? config.assessment_criteria : defaultState.config?.assessment_criteria ?? [];
  const entryPlan = useMemo(() => buildOrffEntryPlan(tasks, {
    bpm: config.bpm,
    meter: config.meter,
    entryEveryBars: config.entry_every_bars
  }), [config.bpm, config.entry_every_bars, config.meter, tasks]);
  const [muted, setMuted] = useState<string[]>([]);
  const [solo, setSolo] = useState("");
  const [records, setRecords] = useState(() => buildDefaultOrffGroupRecords(tasks, criteria));
  const [entryStartedAt, setEntryStartedAt] = useState<number | null>(null);
  const [entryResults, setEntryResults] = useState<Record<string, OrffEntryTimingResult>>({});
  const [sessionEvents, setSessionEvents] = useState<OrffEnsembleEvent[]>([]);
  const activeCount = useMemo(() => tasks.filter((_, index) => isAudible(partKey(parts, index), muted, solo)).length, [muted, parts, solo, tasks]);
  const performanceSummary = useMemo(() => summarizeOrffPerformance(records), [records]);
  const performanceExport = useMemo(() => buildOrffPerformanceExport(performanceSummary), [performanceSummary]);
  const playbackQueue = useMemo(() => buildOrffPlaybackQueue(sessionEvents), [sessionEvents]);
  const entryAttemptSummary = useMemo(() => summarizeOrffEntryAttempts(sessionEvents), [sessionEvents]);
  const sessionExport = useMemo(() => buildOrffSessionExport(sessionEvents, entryAttemptSummary), [entryAttemptSummary, sessionEvents]);

  const playPart = (part: string, index: number) => {
    if (!isAudible(part, muted, solo)) return;
    playPlayableInstrumentSequence(partOffsets(part, rhythm, index), {
      instrument: instrumentName(part),
      gap: 60 / Number(config.bpm || 88),
      duration: part === "triangle" ? 0.62 : 0.16,
      gain: part === "triangle" ? 0.42 : 0.58,
      baseMidi: 48 + index * 4,
      oscillatorWave: part === "triangle" ? "sine" : part === "shaker" ? "sawtooth" : "square"
    });
    const now = Date.now();
    setSessionEvents((current) => recordOrffEnsembleEvent(current, {
      eventType: "play",
      groupName: groupNameFromTask(tasks[index], index),
      part,
      timestampMs: entryStartedAt === null ? now : now - entryStartedAt,
      rhythmStep: index,
    }));
  };

  const playAll = () => {
    parts.forEach((part, index) => {
      setTimeout(() => playPart(part, index), index * 80);
    });
  };

  const toggleMute = (part: string) => {
    setMuted((current) => current.includes(part) ? current.filter((item) => item !== part) : [...current, part]);
  };

  const reset = () => {
    setMuted([]);
    setSolo("");
    setRecords(buildDefaultOrffGroupRecords(tasks, criteria));
    setEntryStartedAt(null);
    setEntryResults({});
    setSessionEvents([]);
  };

  const startEntryClock = () => {
    setEntryStartedAt(Date.now());
    setEntryResults({});
  };

  const recordEntry = (cueIndex: number) => {
    const cue = entryPlan[cueIndex];
    if (!cue || entryStartedAt === null) return;
    const elapsed = Date.now() - entryStartedAt;
    const result = judgeOrffEntryTiming(cue, elapsed, Number(config.bpm || 88));
    setEntryResults((current) => ({ ...current, [cue.groupName]: result }));
    setSessionEvents((current) => recordOrffEnsembleEvent(current, {
      eventType: "entry",
      groupName: cue.groupName,
      part: partKey(parts, cueIndex),
      timestampMs: elapsed,
      cue,
      entryResult: result,
    }));
  };

  const markCriterion = (groupIndex: number, label: string, status: OrffCriterionStatus) => {
    setRecords((current) => updateOrffCriterion(current, groupIndex, label, status));
  };

  const setEvidence = (groupIndex: number, evidence: string) => {
    setRecords((current) => updateOrffEvidence(current, groupIndex, evidence));
  };

  return (
    <main className="primary-activity-shell orff-ensemble-shell">
      <Container size="4" px="4">
        <section className="teacher-control-bar">
          <Flex align="center" justify="between" gap="3" wrap="wrap">
            <Flex align="center" gap="2">
              <Music2 size={18} />
              <Text weight="bold">奥尔夫合奏控制</Text>
              <Badge color="green" variant="soft">可听声部 {activeCount}/{tasks.length || 1}</Badge>
              <Badge color="amber" variant="soft">{config.meter ?? "2/4"} · {config.bpm ?? 88} BPM</Badge>
            </Flex>
            <Flex gap="2" wrap="wrap">
              <Button highContrast onClick={playAll} aria-label="播放合奏">
                <Play size={17} />
                合奏
              </Button>
              <Button variant="soft" color="gray" onClick={reset} aria-label="重置">
                <RotateCcw size={17} />
              </Button>
            </Flex>
          </Flex>
        </section>

        <Grid columns={{ initial: "1", md: "1.08fr .92fr" }} gap="4" className="activity-stage">
          <section className="activity-board orff-board" aria-label="奥尔夫合奏活动">
            <Flex align="center" gap="2" wrap="wrap">
              <Badge color="green" variant="soft">{alignment.primary_competency ?? "艺术表现"}</Badge>
              {(alignment.music_elements ?? []).map((element) => <Badge key={element} color="amber" variant="soft">{element}</Badge>)}
            </Flex>
            <Heading as="h1" size="8" className="activity-title">奥尔夫打击乐合奏</Heading>
            <Text as="p" size="3" color="gray" className="activity-subtitle">
              分组负责固定节奏声部，听稳定拍进入，合奏时先听别人再演奏自己。
            </Text>

            <Grid columns={{ initial: "1", sm: "3" }} gap="3" className="ensemble-part-grid">
              {tasks.map((task, index) => {
                const part = partKey(parts, index);
                const audible = isAudible(part, muted, solo);
                return (
                  <section key={`${task}-${index}`} className={`ensemble-part-card ${audible ? "" : "muted"}`}>
                    <Flex align="center" justify="between" gap="2">
                      <Badge color="teal" variant="soft">{instrumentLabel(part)}</Badge>
                      <Badge color={audible ? "green" : "gray"} variant="soft">{audible ? "可听" : "静音"}</Badge>
                    </Flex>
                    <strong>{task}</strong>
                    <button type="button" className="ensemble-play-pad" onClick={() => playPart(part, index)}>
                      <PlayableInstrumentSkin part={part} label={instrumentLabel(part)} />
                      <span className="ensemble-play-label">
                        <Hand size={18} />
                        演奏
                      </span>
                    </button>
                    <Flex gap="2" wrap="wrap">
                      <Button size="2" variant="soft" onClick={() => toggleMute(part)}>
                        <VolumeX size={15} />
                        静音
                      </Button>
                      <Button size="2" variant={solo === part ? "solid" : "soft"} onClick={() => setSolo(solo === part ? "" : part)}>
                        <Volume2 size={15} />
                        独奏
                      </Button>
                    </Flex>
                  </section>
                );
              })}
            </Grid>
          </section>

          <aside className="activity-side" aria-label="合奏提示区">
            <section className="primary-tool ensemble-rhythm-panel">
              <Text weight="bold">共同节奏</Text>
              <div className="lyrics-rhythm-strip ensemble-rhythm-strip">
                {rhythm.map((item, index) => (
                  <span key={`${item}-${index}`} className={item}>
                    <strong><RhythmNotation rhythm={item} /></strong>
                    <small>{rhythmName(item)}</small>
                  </span>
                ))}
              </div>
            </section>

            <section className="primary-tool ensemble-entry-panel">
              <Flex align="center" justify="between" gap="2" wrap="wrap">
                <Text weight="bold">声部进入提示</Text>
                <Button size="2" variant="soft" onClick={startEntryClock} aria-label="开始声部进入计时">
                  <Play size={15} />
                  开始计时
                </Button>
              </Flex>
              <div className="ensemble-entry-list">
                {entryPlan.map((cue, cueIndex) => {
                  const result = entryResults[cue.groupName];
                  return (
                    <article key={`${cue.groupName}-${cue.targetMs}`} className={`ensemble-entry-card ${result?.status ?? "waiting"}`}>
                      <div>
                        <strong>{cue.groupName}</strong>
                        <span>第 {cue.barNumber} 小节第 {cue.beatNumber} 拍进入</span>
                      </div>
                      <Button size="2" variant="soft" disabled={entryStartedAt === null} onClick={() => recordEntry(cueIndex)}>
                        记录进入
                      </Button>
                      {result ? (
                        <small>{entryStatusLabel(result.status)} · {result.teacherSuggestion}</small>
                      ) : (
                        <small>{entryStartedAt === null ? "先点开始计时，再记录各组进入。" : "等待本组进入。"}</small>
                      )}
                    </article>
                  );
                })}
              </div>
            </section>

            <section className="primary-tool ensemble-performance-panel">
              <Flex align="center" justify="between" gap="2" wrap="wrap">
                <Flex align="center" gap="2">
                  <CheckCircle2 size={19} />
                  <Text weight="bold">小组表现记录</Text>
                </Flex>
                <Badge color={performanceSummary.readyGroups === performanceSummary.totalGroups ? "green" : "amber"} variant="soft">
                  {performanceSummary.readyGroups}/{performanceSummary.totalGroups} 组可记录
                </Badge>
              </Flex>
              <div className="ensemble-record-list">
                {records.map((record, groupIndex) => {
                  const judge = judgeOrffPerformanceRecord(record);
                  return (
                    <article key={`${record.groupName}-${record.task}`} className={`ensemble-record-card ${judge.status}`}>
                      <Flex align="center" justify="between" gap="2" wrap="wrap">
                        <strong>{record.groupName}</strong>
                        <Badge color={judge.status === "ready" ? "green" : "amber"} variant="soft">
                          {judge.status === "ready" ? "已记录" : "待补依据"}
                        </Badge>
                      </Flex>
                      <p>{record.task}</p>
                      <div className="ensemble-criteria-grid" aria-label={`${record.groupName}评价维度`}>
                        {record.criteria.map((criterion) => (
                          <Button
                            key={criterion.label}
                            type="button"
                            size="2"
                            variant={criterion.status === "met" ? "solid" : "soft"}
                            color={criterion.status === "met" ? "green" : "gray"}
                            onClick={() => markCriterion(groupIndex, criterion.label, criterion.status === "met" ? "unchecked" : "met")}
                          >
                            {criterion.label}
                          </Button>
                        ))}
                      </div>
                      <TextArea
                        aria-label={`${record.groupName}音乐依据`}
                        value={record.evidence}
                        onChange={(event) => setEvidence(groupIndex, event.target.value)}
                        placeholder="写一句音乐依据，如：节奏稳定，进入整齐，能听同伴声部"
                      />
                      <small>{judge.feedback}</small>
                    </article>
                  );
                })}
              </div>
              <div className="ensemble-summary-box">
                <Text weight="bold">教师下一步</Text>
                <p>{performanceSummary.teacherNextStep}</p>
                <ReadableData value={performanceExport} />
              </div>
            </section>

            <section className="primary-tool ensemble-session-panel">
              <Flex align="center" justify="between" gap="2" wrap="wrap">
                <Text weight="bold">录制回放</Text>
                <Badge color={sessionEvents.length ? "green" : "gray"} variant="soft">
                  已记录 {sessionEvents.length} 个事件
                </Badge>
              </Flex>
              <div className="ensemble-playback-list" aria-label="奥尔夫录制回放队列">
                {playbackQueue.length ? playbackQueue.slice(0, 6).map((item, index) => (
                  <article key={`${item.groupName}-${item.eventType}-${item.timestampMs}-${index}`}>
                    <strong>{item.groupName}</strong>
                    <span>{item.eventType === "entry" ? "进入" : "演奏"} · {instrumentLabel(item.part)} · +{item.delayMs}ms</span>
                  </article>
                )) : (
                  <p>先记录声部进入或演奏，形成可回放的课堂证据。</p>
                )}
              </div>
              <div className="ensemble-entry-summary">
                <Text weight="bold">多次进入汇总</Text>
                <p>{entryAttemptSummary.teacherNextStep}</p>
                {Object.entries(entryAttemptSummary.byGroup).map(([groupName, summary]) => (
                  <span key={groupName}>
                    {groupName}：准时 {summary.on_cue}，偏早 {summary.early}，偏晚 {summary.late}
                  </span>
                ))}
              </div>
              <ReadableData value={sessionExport} />
            </section>

            <section className="primary-tool classroom-prompts">
              <Text weight="bold">教师提示</Text>
              <p>先单独听每个声部，再两组合，最后全组合奏。</p>
              <p>如果合奏散掉，独奏最稳定的一组，再让其他组依次加入。</p>
              <p>展示后请学生说出自己什么时候进入、怎样听其他声部。</p>
            </section>
          </aside>
        </Grid>
      </Container>
    </main>
  );
}

function partKey(parts: string[], index: number) {
  return parts[index] ?? ["hand_drum", "woodblock", "shaker", "triangle"][index] ?? "claves";
}

function groupNameFromTask(task: string | undefined, index: number) {
  return task?.match(/^[A-ZＡ-Ｚ一二三四五六七八九十\d]+组/)?.[0] || `${index + 1}组`;
}

function isAudible(part: string, muted: string[], solo: string) {
  if (solo) return solo === part;
  return !muted.includes(part);
}

function partOffsets(part: string, rhythm: string[], index: number) {
  const base = part === "triangle" ? [12, -7, 12, -7] : part === "shaker" ? [0, 2, 0, 2] : part === "woodblock" ? [7, 7, 7, 7] : [0, 0, 5, 0];
  return rhythm.map((item, step) => item === "rest" ? -7 : base[step % base.length] + index);
}

function instrumentName(part: string) {
  if (part === "triangle") return "glockenspiel";
  if (part === "shaker") return "agogo";
  if (part === "woodblock") return "woodblock";
  return "taiko_drum";
}

function PlayableInstrumentSkin({ part, label }: { part: string; label: string }) {
  const skin = playableInstrumentAssetFor(part || label);
  if (!skin.url) return <span className="ensemble-skin-pending">待生成/待接入 {label}</span>;
  return <img className="ensemble-instrument-skin" src={skin.url} alt={`${label}生成乐器皮肤`} />;
}

function instrumentLabel(part: string) {
  const labels: Record<string, string> = {
    hand_drum: "手鼓",
    woodblock: "木鱼",
    shaker: "沙锤",
    claves: "响板",
    triangle: "三角铁"
  };
  return labels[part] ?? "打击乐";
}

function rhythmLabel(item: string) {
  return formalRhythmLabel(item);
}

function rhythmName(item: string) {
  return formalRhythmName(item);
}

function entryStatusLabel(status: string) {
  if (status === "on_cue") return "准时进入";
  if (status === "early") return "偏早";
  if (status === "late") return "偏晚";
  return "待记录";
}
