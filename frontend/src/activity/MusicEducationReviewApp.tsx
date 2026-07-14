import { useEffect, useMemo, useRef, useState } from "react";
import { Badge, Button, Container, Flex, Grid, Heading, Text } from "@radix-ui/themes";
import { Boxes, Copy, ExternalLink, Filter, LibraryBig, Play, Search, ShieldCheck, Volume2 } from "lucide-react";
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
import {
  REVIEW_CATEGORIES,
  REVIEW_CATEGORY_LABELS,
  buildReviewItemCopy,
  collectMusicElements,
  countMismatchCategories,
  createReviewPreviewRequestGuard,
  defaultActivityTeachingRole,
  filterReviewItems,
  resolveInitialReviewCategory,
  stringArray,
  type ReviewCatalog,
  type ReviewCatalogItem,
  type ReviewCategory,
  type ReviewFilters,
  type ReviewPreview
} from "./musicEducationReviewCatalog";

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

const expectedCatalogSummary = "最新正式库：32 个组件、32 种活动、7 个游戏、17 种教具、11 种虚拟乐器、9 种材料绑定器";
const gradeBandOptions = [
  ["all", "全部学段"],
  ["lower_primary", "小学低段"],
  ["middle_primary", "小学中段"],
  ["upper_primary", "小学高段"]
] as const;

const teachingRoleOptions = [
  ["all", "全部课堂角色"],
  ["core_practice", "核心音乐实践"],
  ["practice_with_evidence", "实践主导＋网页证据"],
  ["listening_evidence", "听赏证据／选择整理"],
  ["closure_assessment", "课末反馈／教师再教学依据"]
] as const;

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
  const initialParams = useMemo(() => new URLSearchParams(window.location.search), []);
  const initialCategory = resolveInitialReviewCategory(initialParams.get("category"));
  const [activeView, setActiveView] = useState<"professional" | ReviewCategory>(
    initialCategory
  );
  const [catalog, setCatalog] = useState<ReviewCatalog | null>(null);
  const [catalogLoading, setCatalogLoading] = useState(true);
  const [catalogError, setCatalogError] = useState("");
  const [selectedItem, setSelectedItem] = useState<ReviewCatalogItem | null>(null);
  const [preview, setPreview] = useState<ReviewPreview | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [copyStatus, setCopyStatus] = useState("");
  const previewRequestGuard = useRef(createReviewPreviewRequestGuard()).current;
  const [filters, setFilters] = useState<ReviewFilters>({
    search: "",
    gradeBand: "all",
    musicElement: "all",
    implementationStatus: "all",
    runnableOnly: false,
    teachingRole: "all"
  });

  useEffect(() => {
    let active = true;
    fetch("/api/music-education-review/catalog")
      .then((response) => response.ok ? response.json() : Promise.reject(new Error(`HTTP ${response.status}`)))
      .then((payload: ReviewCatalog) => {
        if (!active) return;
        setCatalog(payload);
        setCatalogError("");
        const requestedId = initialParams.get("item");
        if (requestedId) {
          const requested = payload.categories[initialCategory].find((item) => item.id === requestedId);
          if (requested) void openCatalogItem(requested);
        }
      })
      .catch(() => {
        if (active) setCatalogError("无法读取正式能力库，已禁止使用本地假目录。请检查后端服务。");
      })
      .finally(() => {
        if (active) setCatalogLoading(false);
      });
    return () => { active = false; };
  }, [initialCategory, initialParams]);

  useEffect(() => {
    const teachingRole = activeView === "activity"
      ? defaultActivityTeachingRole(catalog?.categories.activity || [])
      : "all";
    setFilters((current) => current.teachingRole === teachingRole ? current : { ...current, teachingRole });
  }, [activeView, catalog]);

  const musicElementOptions = useMemo(() => collectMusicElements(catalog), [catalog]);
  const activeItems = activeView === "professional" || !catalog ? [] : catalog.categories[activeView];
  const filteredItems = useMemo(() => filterReviewItems(activeItems, filters), [activeItems, filters]);
  const countMismatches = catalog ? countMismatchCategories(catalog.actual_counts, catalog.expected_counts) : [];

  async function openCatalogItem(item: ReviewCatalogItem) {
    const requestId = previewRequestGuard.start();
    setSelectedItem(item);
    setPreview(null);
    setPreviewLoading(true);
    setCopyStatus("");
    try {
      const response = await fetch(`/api/music-education-review/previews/${item.category}/${encodeURIComponent(item.id)}`);
      if (!response.ok) throw new Error(String(response.status));
      const payload = await response.json() as ReviewPreview;
      previewRequestGuard.commit(requestId, () => setPreview(payload));
    } catch {
      previewRequestGuard.commit(requestId, () => setPreview(null));
    } finally {
      previewRequestGuard.commit(requestId, () => setPreviewLoading(false));
    }
  }

  async function copySelectedItem() {
    if (!selectedItem) return;
    await navigator.clipboard.writeText(buildReviewItemCopy(selectedItem));
    setCopyStatus("已复制项目名称、ID 和审核重点");
  }


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
              <Heading as="h1" size="8" className="activity-title">音乐教育组件总审核台</Heading>
              <Text as="p" size="3" color="gray" className="activity-subtitle">
                专业材料和智能体可调用的六大能力库集中在一个页面审核。
              </Text>
              <Text as="p" size="2" color="gray">{expectedCatalogSummary}</Text>
            </div>
            <div className="music-review-health" data-status={catalogError || countMismatches.length ? "error" : "ready"}>
              <ShieldCheck size={20} />
              <div>
                <strong>{catalogLoading ? "正在读取正式库" : catalogError ? "后端库未连接" : "正式库已连接"}</strong>
                <span>{catalogError || (countMismatches.length ? `数量异常：${countMismatches.map((category) => REVIEW_CATEGORY_LABELS[category]).join("、")}` : "数量和质量门禁实时读取")}</span>
              </div>
            </div>
          </Flex>
        </section>

        {catalog ? (
          <section className="music-review-dashboard" aria-label="六大组件库数量">
            {REVIEW_CATEGORIES.map((category) => (
            <button type="button" key={category} data-status={catalog.actual_counts[category] === catalog.expected_counts[category] ? "pass" : "fail"} onClick={() => { setActiveView(category); setSelectedItem(null); setPreview(null); }}>
                <strong>{catalog.actual_counts[category]}</strong>
                <span>{REVIEW_CATEGORY_LABELS[category]}</span>
                <small>预期 {catalog.expected_counts[category]}</small>
              </button>
            ))}
            <div className="music-review-quality-summary">
              <span>活动门禁：<b>{catalog.activity_quality_report.status === "pass" ? "通过" : "失败"}</b></span>
              <span>游戏门禁：<b>{catalog.game_quality_report.status === "pass" ? "通过" : "失败"}</b></span>
            </div>
          </section>
        ) : null}

        <nav className="music-review-navigation" aria-label="审核分类">
          <button type="button" className={activeView === "professional" ? "active" : ""} onClick={() => { setActiveView("professional"); setSelectedItem(null); setPreview(null); }}><LibraryBig size={17} />专业材料</button>
          {REVIEW_CATEGORIES.map((category) => (
            <button type="button" key={category} className={activeView === category ? "active" : ""} onClick={() => { setActiveView(category); setSelectedItem(null); setPreview(null); }}>
              <Boxes size={16} />{REVIEW_CATEGORY_LABELS[category]}
            </button>
          ))}
        </nav>

        {catalogError ? <section className="music-review-catalog-error">{catalogError}</section> : null}

        {activeView !== "professional" ? (
          <CatalogReviewConsole
            category={activeView}
            items={filteredItems}
            totalCount={activeItems.length}
            filters={filters}
            setFilters={setFilters}
            musicElementOptions={musicElementOptions}
            selectedItem={selectedItem}
            preview={preview}
            previewLoading={previewLoading}
            copyStatus={copyStatus}
            onSelect={(item) => void openCatalogItem(item)}
            onCopy={() => void copySelectedItem()}
          />
        ) : null}

        {activeView === "professional" ? <>

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
              </article>
            ))}
          </Grid>
        </ReviewSection>
        </> : null}
      </Container>
    </main>
  );
}

function CatalogReviewConsole({
  category,
  items,
  totalCount,
  filters,
  setFilters,
  musicElementOptions,
  selectedItem,
  preview,
  previewLoading,
  copyStatus,
  onSelect,
  onCopy
}: {
  category: ReviewCategory;
  items: ReviewCatalogItem[];
  totalCount: number;
  filters: ReviewFilters;
  setFilters: React.Dispatch<React.SetStateAction<ReviewFilters>>;
  musicElementOptions: string[];
  selectedItem: ReviewCatalogItem | null;
  preview: ReviewPreview | null;
  previewLoading: boolean;
  copyStatus: string;
  onSelect: (item: ReviewCatalogItem) => void;
  onCopy: () => void;
}) {
  return (
    <section className="music-review-catalog-section" data-review-category={category}>
      <div className="music-review-catalog-heading">
        <div>
          <Text as="p" size="2" weight="bold" color="teal">组件总库·只读审核</Text>
          <Heading as="h2" size="6">{REVIEW_CATEGORY_LABELS[category]}</Heading>
          <Text as="p" size="2" color="gray">显示 {items.length} / {totalCount} 项，没有截断目录。</Text>
        </div>
        <Badge color="teal" variant="soft">实时正式注册表</Badge>
      </div>

      <div className="music-review-filter-bar">
        <label className="music-review-search"><Search size={17} /><input aria-label="搜索审核项目" value={filters.search} placeholder="搜索名称、ID、音乐要素或审核重点" onChange={(event) => setFilters((current) => ({ ...current, search: event.target.value }))} /></label>
        <label><span>学段</span><select value={filters.gradeBand} onChange={(event) => setFilters((current) => ({ ...current, gradeBand: event.target.value }))}>{gradeBandOptions.map(([value, label]) => <option value={value} key={value}>{label}</option>)}</select></label>
        <label><span>音乐要素</span><select value={filters.musicElement} onChange={(event) => setFilters((current) => ({ ...current, musicElement: event.target.value }))}><option value="all">全部要素</option>{musicElementOptions.map((element) => <option value={element} key={element}>{element}</option>)}</select></label>
        {category === "activity" ? <label><span>课堂角色</span><select value={filters.teachingRole} onChange={(event) => setFilters((current) => ({ ...current, teachingRole: event.target.value }))}>{teachingRoleOptions.map(([value, label]) => <option value={value} key={value}>{label}</option>)}</select></label> : null}
        <label><span>实现状态</span><select value={filters.implementationStatus} onChange={(event) => setFilters((current) => ({ ...current, implementationStatus: event.target.value as ReviewFilters["implementationStatus"] }))}><option value="all">全部状态</option><option value="live">可运行</option><option value="preview_ready">审核预览</option><option value="contract_only">合同审核</option></select></label>
        <label className="music-review-toggle"><input type="checkbox" checked={filters.runnableOnly} onChange={(event) => setFilters((current) => ({ ...current, runnableOnly: event.target.checked }))} /><Filter size={15} />只看可试玩／可试听</label>
      </div>

      <div className="music-review-console-layout">
        <div className="music-review-catalog-grid" aria-label={`${REVIEW_CATEGORY_LABELS[category]}完整目录`}>
          {items.map((item) => (
            <button type="button" key={item.id} className={`music-review-catalog-card ${selectedItem?.id === item.id ? "active" : ""}`} onClick={() => onSelect(item)}>
              <span className="music-review-card-status-row">
                <small>{item.id}</small>
                <i data-status={item.implementation_status}>{implementationLabel(item.implementation_status)}</i>
              </span>
              <strong>{item.name}</strong>
              <p>{item.purpose}</p>
              {item.teaching_role_label ? <span className="music-review-role-badge" data-role={item.teaching_role}>{item.teaching_role_label}</span> : item.category === "activity" ? <span className="music-review-role-badge" data-role="unclassified">待补角色</span> : null}
              <span className="music-review-chip-row">{item.music_elements.slice(0, 4).map((element) => <em key={element}>{element}</em>)}</span>
              {isEvidenceOnlyRole(item) ? <p className="music-review-main-activity-warning"><strong>使用边界：</strong>不能作为课堂主活动；只能用于导入、复听证据或课末反馈。</p> : null}
              {item.lifecycle_status === "compatibility" ? <b className="music-review-compatibility">旧版兼容·禁止优先调用</b> : null}
            </button>
          ))}
          {!items.length ? <div className="music-review-empty-filter">没有符合当前筛选条件的项目。</div> : null}
        </div>

        <ReviewPreviewPanel
          item={selectedItem}
          preview={preview}
          loading={previewLoading}
          copyStatus={copyStatus}
          onCopy={onCopy}
        />
      </div>
    </section>
  );
}

function ReviewPreviewPanel({ item, preview, loading, copyStatus, onCopy }: {
  item: ReviewCatalogItem | null;
  preview: ReviewPreview | null;
  loading: boolean;
  copyStatus: string;
  onCopy: () => void;
}) {
  if (!item) return <aside className="music-review-preview-panel empty"><Boxes size={30} /><strong>选择一项开始审核</strong><p>这里会显示真实运行入口、教师审核重点和技术合同。</p></aside>;
  return (
    <aside className="music-review-preview-panel" aria-live="polite">
      <div className="music-review-preview-head">
        <div><small>{item.id}</small><Heading as="h3" size="5">{item.name}</Heading></div>
        <Badge color={item.implementation_status === "live" ? "green" : item.implementation_status === "preview_ready" ? "amber" : "gray"} variant="soft">{implementationLabel(item.implementation_status)}</Badge>
      </div>
      {loading ? <div className="music-review-preview-loading">正在读取固定审核示例…</div> : null}
      {!loading && !preview ? <div className="music-review-preview-error">该项预览暂时无法读取，不使用假数据替代。</div> : null}
      {preview ? <>
        <Badge color="teal" variant="solid">{preview.example_label}</Badge>
        <p className="music-review-preview-purpose">{preview.professional_summary.purpose}</p>
        <PreviewList title="音乐要素" values={preview.professional_summary.music_elements} />
        {item.teaching_role_label ? <section className="music-review-practice-boundaries">
          <span className="music-review-role-badge" data-role={item.teaching_role}>{item.teaching_role_label}</span>
          <PreviewList title="学生主体实践" values={item.category === "material_binder" ? ["后台材料处理，不面向学生"] : preview.professional_summary.student_actions} />
          <div className="music-review-boundary-block"><strong>网页只做什么</strong><p>{item.web_boundary}</p></div>
          <div className="music-review-boundary-block"><strong>必须由教师判断什么</strong><p>{item.teacher_boundary}</p></div>
          {isEvidenceOnlyRole(item) ? <p className="music-review-main-activity-warning"><strong>使用边界：</strong>不能作为课堂主活动；只能用于导入、复听证据或课末反馈。</p> : null}
        </section> : item.category === "activity" ? <section className="music-review-practice-boundaries"><span className="music-review-role-badge" data-role="unclassified">待补角色</span><p className="music-review-role-pending">该活动尚未补充课堂角色，因此审核台不会用“核心音乐实践”筛选隐藏它。</p><PreviewList title="学生主体实践" values={preview.professional_summary.student_actions} /></section> : <PreviewList title="学生主体实践" values={preview.professional_summary.student_actions} />}
        <PreviewList title="教师审核重点" values={preview.professional_summary.teacher_focus} ordered />
        {preview.flow?.length ? <div className="music-review-flow">{preview.flow.map((step, index) => <article key={step.id}><span>{index + 1}</span><div><strong>{step.label}</strong><p>{step.description}</p></div></article>)}</div> : null}
        {preview.classroom_preview ? <div className="music-review-demo-block"><strong>教具审核示例</strong><p>替代：{preview.classroom_preview.replaces}</p><p>调用组件：{preview.classroom_preview.components.join(" / ") || "按活动运行时组合"}</p><p>审核时请在下方进入实际课堂活动，确认学生确实能操作该教具。</p></div> : null}
        {preview.fixture && Object.keys(preview.fixture).length ? <KeyValuePreview title="组件固定审核状态" value={preview.fixture} /> : null}
        {preview.binding_example ? <><div className="music-review-demo-block"><strong>后台智能体调用器 · 后台材料处理，不面向学生</strong><p>智能体接收教师确认的歌曲或课堂材料后，才调用它生成结构化结果并交给下游活动。</p></div><div className="music-review-binding-flow"><KeyValuePreview title="1·教师原始材料" value={preview.binding_example.source} /><KeyValuePreview title="2·结构化结果" value={preview.binding_example.structured_result} /><KeyValuePreview title="3·最终活动／组件" value={preview.binding_example.component_targets} /></div></> : null}
        {preview.audio_preview ? <div className="music-review-audio-preview"><div><strong>{preview.audio_preview.audited ? "已审核音频资源" : "组合调用已审核音频资源"}</strong><p>{preview.audio_preview.license || (preview.audio_preview.requires_combined_audio ? "教师选择的每件打击乐器均须使用已审核音频" : "请在完整演奏界面中验证音频")}</p>{preview.audio_preview.attribution ? <small>{preview.audio_preview.attribution}</small> : null}</div><Button highContrast asChild><a href={preview.full_screen_url} target="_blank" rel="noreferrer"><Volume2 size={16} />打开真实演奏界面</a></Button></div> : null}
        <Flex gap="2" wrap="wrap" className="music-review-preview-actions">
          <Button variant="soft" onClick={onCopy}><Copy size={16} />复制项目信息</Button>
          {preview.full_screen_url ? <Button highContrast asChild><a href={preview.full_screen_url} target="_blank" rel="noreferrer"><ExternalLink size={16} />{item.category === "teaching_aid" ? "打开调用该教具的课堂活动" : "全屏打开"}</a></Button> : null}
        </Flex>
        {copyStatus ? <span className="music-review-copy-status">{copyStatus}</span> : null}
        <details className="music-review-technical-details"><summary>技术信息与质量门禁</summary><pre>{JSON.stringify(preview.technical_details, null, 2)}</pre></details>
      </> : null}
    </aside>
  );
}

function PreviewList({ title, values, ordered = false }: { title: string; values: string[]; ordered?: boolean }) {
  const Tag = ordered ? "ol" : "ul";
  return <div className="music-review-preview-list"><strong>{title}</strong><Tag>{values.length ? values.map((value) => <li key={value}>{value}</li>) : <li>待绑定具体教学材料</li>}</Tag></div>;
}

function isEvidenceOnlyRole(item: ReviewCatalogItem) {
  return item.teaching_role === "listening_evidence" || item.teaching_role === "closure_assessment";
}

function KeyValuePreview({ title, value }: { title: string; value: unknown }) {
  return <div className="music-review-demo-block"><strong>{title}</strong><pre>{JSON.stringify(value, null, 2)}</pre></div>;
}

function implementationLabel(status: ReviewCatalogItem["implementation_status"]) {
  return status === "live" ? "可运行" : status === "preview_ready" ? "审核预览" : "合同审核";
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
