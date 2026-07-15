import { useState } from "react";
import { Badge, Button, Container, Flex, Grid, Heading, Text } from "@radix-ui/themes";
import { CheckCircle2, ExternalLink, PencilRuler, Play, XCircle } from "lucide-react";
import { RhythmNotation } from "../music-components/RhythmNotation";
import {
  PITCH_REGISTERS,
  REGISTERED_PITCH_DEFINITIONS,
  registeredPitchToMidi,
  resolvePitchToken,
  sequenceToMidiOffsets,
  type PitchRegisterDefinition
} from "../shared/pitchCatalog";
import {
  EXACT_TIMBRE_DEFINITIONS,
  SAMPLE_LIBRARY,
  type ExactTimbreDefinition
} from "../shared/instrumentTimbreCatalog";
import { playHybridToneSequenceAsync } from "../shared/realAudio";
import { formalRhythmName } from "./rhythmNaming";
import { FIRST_BATCH_COMPONENTS } from "../shared/musicMediaContracts";

type RhythmReviewItem = {
  id: string;
  name: string;
  classroomUse: string;
  events: Array<{ offset: number; start: number; duration: number }>;
};

type MelodyReviewItem = {
  name: string;
  focus: string;
  pitchIds: string[];
};

type TimbreReviewItem = ExactTimbreDefinition;

type ActivityReviewItem = {
  name: string;
  element: string;
  studentAction: string;
  auditFocus: string;
  href: string;
};

const rhythmItems: RhythmReviewItem[] = [
  { id: "quarter", name: "四分音符", classroomUse: "稳定一拍，适合建立基本拍感。", events: [{ offset: 0, start: 0, duration: 0.28 }] },
  { id: "eighth_pair", name: "二八", classroomUse: "一拍两下，适合从稳定拍进入均分。", events: [{ offset: 0, start: 0, duration: 0.16 }, { offset: 0, start: 0.5, duration: 0.16 }] },
  { id: "eighth_sixteenth_sixteenth", name: "八十六", classroomUse: "前长后短，适合听辨疏密变化。", events: [{ offset: 0, start: 0, duration: 0.22 }, { offset: 0, start: 0.5, duration: 0.1 }, { offset: 0, start: 0.75, duration: 0.1 }] },
  { id: "sixteenth_sixteenth_eighth", name: "十六八", classroomUse: "前短后长，适合和八十六对比。", events: [{ offset: 0, start: 0, duration: 0.1 }, { offset: 0, start: 0.25, duration: 0.1 }, { offset: 0, start: 0.5, duration: 0.22 }] },
  { id: "sixteenth_four", name: "四个十六", classroomUse: "一拍四下，适合训练均匀快速分拍。", events: [{ offset: 0, start: 0, duration: 0.08 }, { offset: 0, start: 0.25, duration: 0.08 }, { offset: 0, start: 0.5, duration: 0.08 }, { offset: 0, start: 0.75, duration: 0.08 }] },
  { id: "syncopation", name: "小切分", classroomUse: "十六-八-十六，第二个音跨过半拍位置，形成一拍内的切分重心。", events: [{ offset: 0, start: 0, duration: 0.18 }, { offset: 0, start: 0.25, duration: 0.38 }, { offset: 0, start: 0.75, duration: 0.18 }] },
  { id: "eighth_triplet", name: "三连音", classroomUse: "一拍平均分成三份，三个音时值均等。", events: [{ offset: 0, start: 0, duration: 0.22 }, { offset: 0, start: 1 / 3, duration: 0.22 }, { offset: 0, start: 2 / 3, duration: 0.22 }] },
  { id: "rest", name: "四分休止符", classroomUse: "静默一整拍，保持内心拍但不发声。", events: [] },
  { id: "eighth_rest", name: "八分休止符", classroomUse: "静默半拍，适合练习细分拍中的收住与等待。", events: [] }
];

const melodyItems: MelodyReviewItem[] = [
  { name: "级进上行", focus: "听辨旋律向上走。", pitchIds: ["do", "re", "mi", "sol"] },
  { name: "级进下行", focus: "听辨旋律回落。", pitchIds: ["sol", "mi", "re", "do"] },
  { name: "五声短句", focus: "适合五声音阶创编。", pitchIds: ["do", "mi", "sol", "la", "sol"] }
];

const registeredPitchGroups = PITCH_REGISTERS.map((register) => ({
  ...register,
  pitches: REGISTERED_PITCH_DEFINITIONS.filter((pitch) => pitch.registerId === register.id)
}));

const activityItems: ActivityReviewItem[] = [
  { name: "节奏热身", element: "节奏型、稳定拍", studentAction: "听、看、拍", auditFocus: "节奏型图形是否准确，播放疏密是否对应。", href: "/template-console/primary-activity-preview.html" },
  { name: "歌词节奏", element: "歌词与节奏", studentAction: "读、拍、唱", auditFocus: "教学环节需要歌词节奏时，必须绑定教师上传或系统识别出的歌词；样例歌词只用于预览。", href: "/template-console/lyrics-rhythm-preview.html" },
  { name: "乐器家族分类", element: "音色、发声方式", studentAction: "听、分、说依据", auditFocus: "音色证据词是否适合小学表达。", href: "/template-console/instrument-family-preview.html" },
  { name: "五声音条琴创编", element: "五声旋律、节奏短句", studentAction: "选音、试听、修改", auditFocus: "创编材料是否可唱、可听、可说明。", href: "/template-console/pentatonic-melody-preview.html" },
  { name: "奥尔夫合奏", element: "节奏、声部进入", studentAction: "分组、合奏、评价", auditFocus: "声部任务是否清楚，进入提示是否适合课堂。", href: "/template-console/orff-ensemble-preview.html" }
];

export function MusicEducationReviewApp() {
  const [pitchPlayback, setPitchPlayback] = useState<Record<string, string>>({});
  const [timbrePlayback, setTimbrePlayback] = useState<Record<string, string>>({});

  const listenToPitch = async (pitchIds: string[], statusKey: string) => {
    setPitchPlayback((current) => ({ ...current, [statusKey]: "正在加载真实钢琴采样..." }));
    const result = await playPitchPreview(pitchIds);
    setPitchPlayback((current) => ({
      ...current,
      [statusKey]: result.ok ? "已播放真实钢琴采样" : "真实钢琴采样未加载，请检查后端声音资源"
    }));
  };

  const listenToRegisteredPitch = async (pitchId: string) => {
    setPitchPlayback((current) => ({ ...current, [pitchId]: "正在加载真实钢琴采样..." }));
    const result = await playRegisteredPitchPreview(pitchId);
    setPitchPlayback((current) => ({
      ...current,
      [pitchId]: result.ok ? "已播放真实钢琴采样" : "真实钢琴采样未加载，请检查后端声音资源"
    }));
  };

  const listenToTimbre = async (item: TimbreReviewItem) => {
    setTimbrePlayback((current) => ({ ...current, [item.id]: "正在加载采样音色..." }));
    const result = await playTimbre(item);
    setTimbrePlayback((current) => ({
      ...current,
      [item.id]: result.ok ? "已播放真实 SoundFont 采样" : "真实音色未加载，请检查后端声音资源"
    }));
  };

  return (
    <main className="primary-activity-shell music-review-shell">
      <Container size="4" px="4">
        <section className="music-review-hero">
          <Flex align="center" justify="between" gap="4" wrap="wrap">
            <div>
              <Badge color="green" variant="soft">给音乐教育专业审核</Badge>
              <Heading as="h1" size="8" className="activity-title">音乐教育专业审核库</Heading>
              <Text as="p" size="3" color="gray" className="activity-subtitle">
                这里只看课堂材料是否专业：节奏型、旋律、音色、活动任务和学生行为。
              </Text>
            </div>
            <div className="music-review-legend" aria-label="审核按钮说明">
              <span><CheckCircle2 size={16} /> 通过</span>
              <span><PencilRuler size={16} /> 需修改</span>
              <span><XCircle size={16} /> 不适合</span>
            </div>
          </Flex>
        </section>

        <ReviewSection
          kicker="一、节奏型库"
          title="看谱型，点一下听"
          note="你主要判断：谱形与时值是否正确；所有非休止节奏统一使用真实钢琴采样试听。"
        >
          <Grid columns={{ initial: "1", sm: "2", md: "4" }} gap="3">
            {rhythmItems.map((item) => (
              <article className="music-review-card rhythm-review-card" key={item.id}>
                <div className="music-review-notation">
                  <RhythmNotation rhythm={item.id} label={item.name} />
                </div>
                <strong>{item.name}</strong>
                <small>{formalRhythmName(item.id)}</small>
                <p>{item.classroomUse}</p>
                <ReviewActions
                  onListen={() => playRhythm(item)}
                  disabledListen={!item.events.length}
                  listenLabel={!item.events.length ? "休止静默" : "钢琴试听"}
                />
              </article>
            ))}
          </Grid>
        </ReviewSection>

        <ReviewSection
          kicker="二、十二平均律单音库"
          title="三个完整音组，每个音都能独立调用"
          note="小字组、小字一组和小字二组各含 12 个实际音高；同音异名共用同一个声音资源。"
        >
          <div className="pitch-register-list">
            {registeredPitchGroups.map((group) => (
              <section className="pitch-register-group" data-register-id={group.id} key={group.id}>
                <Flex align="end" justify="between" gap="3" wrap="wrap" className="pitch-register-head">
                  <div>
                    <Heading as="h3" size="4">{group.chineseName}</Heading>
                    <Text as="p" size="2" color="gray">{registeredPitchRangeLabel(group.id)}</Text>
                  </div>
                  <Text as="p" size="2" weight="bold">MIDI {group.baseMidi}–{group.baseMidi + 11}</Text>
                </Flex>
                <Grid columns={{ initial: "1", sm: "2", md: "4" }} gap="3">
                  {group.pitches.map((pitch) => (
                    <article className="music-review-card pitch-review-card" key={pitch.id}>
                      <span className="music-review-score pitch-review-score">
                        <NumberNotationPitchLabel
                          labels={pitch.numberLabels}
                          octaveMark={group.octaveMark}
                          registerName={group.chineseName}
                        />
                      </span>
                      <strong>{pitch.scientificLabels.join(" / ")}</strong>
                      <small>{group.chineseName} · MIDI {pitch.midi}</small>
                      <p>相对本组 C +{pitch.semitone} 半音。</p>
                      {pitchPlayback[pitch.id] ? <span className="music-review-audio-status">{pitchPlayback[pitch.id]}</span> : null}
                      <ReviewActions onListen={() => void listenToRegisteredPitch(pitch.id)} listenLabel="钢琴试听" />
                    </article>
                  ))}
                </Grid>
              </section>
            ))}
          </div>
        </ReviewSection>

        <ReviewSection
          kicker="三、旋律组合示例"
          title="单音按 ID 组合成旋律"
          note="这些是组合示例，不是单音能力的上限。"
        >
          <Grid columns={{ initial: "1", md: "3" }} gap="3">
            {melodyItems.map((item) => (
              <article className="music-review-card" key={item.name}>
                <span className="music-review-score">{pitchSequenceNumberLabel(item.pitchIds)}</span>
                <strong>{item.name}</strong>
                <small>{item.pitchIds.join(" ")}</small>
                <p>{item.focus}</p>
                {pitchPlayback[item.name] ? <span className="music-review-audio-status">{pitchPlayback[item.name]}</span> : null}
                <ReviewActions onListen={() => void listenToPitch(item.pitchIds, item.name)} listenLabel="钢琴试听" />
              </article>
            ))}
          </Grid>
        </ReviewSection>

        <ReviewSection
          kicker="四、音色与乐器库"
          title="12 件常见乐器真实音色"
          note="你主要判断：音色是否符合乐器特征、分类是否正确、证据词是否适合学生表达。"
        >
          <section className="timbre-review-group timbre-review-group-ready">
            <div className="timbre-review-group-head">
              <div>
                <Badge color="green" variant="soft">可审核真实采样 · 12 件</Badge>
                <Heading as="h3" size="4">基础音乐教育常见乐器</Heading>
              </div>
              <p>
                采样来源：FluidR3 GM · CC BY 3.0。商业使用可以，但发布时必须保留来源、许可与署名。
              </p>
            </div>
            <Grid columns={{ initial: "1", sm: "2", md: "4" }} gap="3">
              {EXACT_TIMBRE_DEFINITIONS.map((item) => (
                <article
                  className="music-review-card timbre-review-card timbre-review-card-ready"
                  data-timbre-id={item.id}
                  key={item.id}
                >
                  <div className="timbre-review-badges">
                    <span className="instrument-badge">{item.familyLabel}</span>
                    <span className="sample-fidelity-badge">精确 SoundFont 采样</span>
                  </div>
                  <strong>{item.label}</strong>
                  <small>{item.classroomFamily} · 代表音 MIDI {item.preview.baseMidi}</small>
                  <p className="timbre-evidence"><b>听辨证据：</b>{item.evidenceTerms.join("、")}</p>
                  <p>{item.classroomNote}</p>
                  <p className="timbre-license-note">
                    {SAMPLE_LIBRARY.license} · {SAMPLE_LIBRARY.id} · 需保留署名
                  </p>
                  {timbrePlayback[item.id] ? <span className="music-review-audio-status">{timbrePlayback[item.id]}</span> : null}
                  <ReviewActions onListen={() => void listenToTimbre(item)} listenLabel="试听真实采样" />
                </article>
              ))}
            </Grid>
          </section>

        </ReviewSection>

        <ReviewSection
          kicker="五、课堂活动库"
          title="看学生要做什么"
          note="你主要判断：任务是否像真实音乐课，学生是否需要听、唱、拍、创编和说明。"
        >
          <Grid columns={{ initial: "1", md: "2" }} gap="3">
            {activityItems.map((item) => (
              <article className="music-review-card activity-review-card" key={item.name}>
                <Flex align="start" justify="between" gap="3">
                  <div>
                    <strong>{item.name}</strong>
                    <small>{item.element}</small>
                  </div>
                  <Button asChild size="2" variant="soft">
                    <a href={item.href} target="_blank" rel="noreferrer">
                      <ExternalLink size={15} />
                      打开
                    </a>
                  </Button>
                </Flex>
                <p>学生行为：{item.studentAction}</p>
                <p>审核重点：{item.auditFocus}</p>
                <ReviewOnlyActions />
              </article>
            ))}
          </Grid>
        </ReviewSection>

        <ReviewSection
          kicker="六、真实课堂核心组件 · 第一批"
          title="五个独立组件，共用同一音乐媒体底座"
          note="逐项打开真实操作界面，重点审核课堂流程、音乐边界和教师控制是否合理。"
        >
          <Grid columns={{ initial: "1", md: "2" }} gap="3">
            {FIRST_BATCH_COMPONENTS.map((item) => (
              <article className="music-review-card activity-review-card" key={item.id} data-classroom-component-id={item.id}>
                <Flex align="start" justify="between" gap="3">
                  <div><strong>{item.name}</strong><small>第一批 · 0{item.order}</small></div>
                  <Button asChild size="2" highContrast><a href={`/template-console/music-classroom-suite.html?component=${item.id}`} target="_blank" rel="noreferrer"><ExternalLink size={15} />打开训练台</a></Button>
                </Flex>
                <p>{firstBatchReviewCopy[item.id].purpose}</p>
                <p><b>网页负责：</b>{firstBatchReviewCopy[item.id].web}</p>
                <p><b>教师负责：</b>{firstBatchReviewCopy[item.id].teacher}</p>
                <ReviewOnlyActions />
              </article>
            ))}
          </Grid>
        </ReviewSection>
      </Container>
    </main>
  );
}

const firstBatchReviewCopy: Record<(typeof FIRST_BATCH_COMPONENTS)[number]["id"], { purpose: string; web: string; teacher: string }> = {
  song_audio_workbench: { purpose: "上传歌曲并对比主音、调式、速度、节奏密度和音色变化。", web: "音频解析、参数变化、缓存及原版与变化版对比。", teacher: "素材版权、变化目标、学生音域与作品风格。" },
  score_audio_sync_player: { purpose: "五线谱、简谱、歌词和声音同步跟随。", web: "同一时间轴、光标、定位和循环。", teacher: "谱面版本、歌词对应和学生识谱表现。" },
  ear_training_engine: { purpose: "单音、音程、节奏、短旋律和主音感训练。", web: "客观选择、键盘和节奏点击。", teacher: "真实视唱、模唱和音乐表达。" },
  vocal_choir_training: { purpose: "儿童安全发声、乐句练习、录音回听与合唱准备。", web: "流程、时长、录音和音高趋势证据。", teacher: "音色、气息、咬字、融合和表现。" },
  ensemble_conductor: { purpose: "儿童二声部、轮唱和课堂乐队分轨排练。", web: "静音、独奏、音量、预备拍和进入证据。", teacher: "音准、平衡、合作聆听和音乐表现。" }
};

function ReviewSection({
  kicker,
  title,
  note,
  children
}: {
  kicker: string;
  title: string;
  note: string;
  children: React.ReactNode;
}) {
  return (
    <section className="music-review-section">
      <Flex align="end" justify="between" gap="3" wrap="wrap" className="music-review-section-head">
        <div>
          <Text as="p" size="2" weight="bold" color="teal">{kicker}</Text>
          <Heading as="h2" size="6">{title}</Heading>
        </div>
        <Text as="p" size="2" color="gray">{note}</Text>
      </Flex>
      {children}
    </section>
  );
}

function NumberNotationPitchLabel({
  labels,
  octaveMark,
  registerName
}: {
  labels: string[];
  octaveMark: PitchRegisterDefinition["octaveMark"];
  registerName: string;
}) {
  const dotPosition = octaveMark === "upper_dot" ? "top" : octaveMark === "lower_dot" ? "bottom" : null;

  return (
    <span className="numbered-pitch-label" aria-label={`${registerName}简谱${labels.join("或")}`}>
      {labels.map((label, index) => {
        const degree = label.slice(-1);
        const accidental = label.slice(0, -1);
        return (
          <span className="numbered-pitch-label-part" key={label}>
            {index > 0 ? <span className="numbered-pitch-separator" aria-hidden="true">/</span> : null}
            <span className="numbered-pitch-token" aria-hidden="true">
              {accidental ? <span className="numbered-pitch-accidental">{accidental}</span> : null}
              <span className="numbered-pitch-degree">
                {degree}
                {dotPosition ? <span className={`pitch-octave-dot pitch-octave-dot-${dotPosition}`} /> : null}
              </span>
            </span>
          </span>
        );
      })}
    </span>
  );
}

function ReviewActions({
  onListen,
  disabledListen = false,
  listenLabel = "试听"
}: {
  onListen: () => void;
  disabledListen?: boolean;
  listenLabel?: string;
}) {
  return (
    <div className="music-review-actions">
      <Button size="2" highContrast onClick={onListen} disabled={disabledListen}>
        <Play size={15} />
        {listenLabel}
      </Button>
      <ReviewOnlyActions />
    </div>
  );
}

function ReviewOnlyActions() {
  return (
    <div className="music-review-mark-buttons" aria-label="专业审核">
      <button type="button" data-status="pass"><CheckCircle2 size={14} />通过</button>
      <button type="button" data-status="revise"><PencilRuler size={14} />需修改</button>
      <button type="button" data-status="reject"><XCircle size={14} />不适合</button>
    </div>
  );
}

function playRhythm(item: RhythmReviewItem) {
  if (!item.events.length) return;
  void playHybridToneSequenceAsync([], {
    instrument: "acoustic_grand_piano",
    baseMidi: 60,
    gain: 0.82,
    events: item.events,
    allowOscillatorFallback: false
  });
}

async function playPitchPreview(pitchIds: string[], tonicMidi = 60) {
  return playHybridToneSequenceAsync(sequenceToMidiOffsets(pitchIds), {
    instrument: "acoustic_grand_piano",
    baseMidi: tonicMidi,
    gap: 0.42,
    duration: 0.36,
    gain: 0.68,
    allowOscillatorFallback: false
  });
}

async function playRegisteredPitchPreview(pitchId: string) {
  return playHybridToneSequenceAsync([registeredPitchToMidi(pitchId)], {
    instrument: "acoustic_grand_piano",
    baseMidi: 0,
    duration: 0.46,
    gain: 0.68,
    allowOscillatorFallback: false
  });
}

async function playTimbre(item: TimbreReviewItem) {
  return playHybridToneSequenceAsync(item.preview.offsets, {
    instrument: item.playbackInstrument,
    baseMidi: item.preview.baseMidi,
    gap: item.preview.gap,
    duration: item.preview.duration,
    gain: item.preview.gain,
    allowOscillatorFallback: false
  });
}

function pitchSequenceNumberLabel(pitchIds: string[]) {
  return pitchIds
    .map((pitchId) => resolvePitchToken(pitchId)?.numberLabels[0] || pitchId)
    .join(" ");
}

function registeredPitchRangeLabel(registerId: PitchRegisterDefinition["id"]) {
  const pitches = REGISTERED_PITCH_DEFINITIONS.filter((pitch) => pitch.registerId === registerId);
  return `${pitches[0]?.scientificLabels[0]}–${pitches[pitches.length - 1]?.scientificLabels[0]} · 十二平均律`;
}
