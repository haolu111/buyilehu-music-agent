import {
  Badge,
  Box,
  Button,
  Card,
  Container,
  Flex,
  Grid,
  Heading,
  Select,
  Separator,
  Slider,
  Switch,
  Text,
  TextArea,
  TextField
} from "@radix-ui/themes";
import type { ReactNode } from "react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  Activity,
  Castle,
  CheckCircle2,
  Cloud,
  Crosshair,
  Ear,
  FileSearch,
  Gauge,
  Hand,
  Map,
  Mic2,
  Mountain,
  Music2,
  Play,
  RotateCcw,
  Settings2,
  ShieldCheck,
  Sparkles
} from "lucide-react";
import {
  useConsoleStore,
  type BeatGuardianMode,
  type CompositionPuzzleMode,
  type Difficulty,
  type FormTreasureMode,
  type GameSkin,
  type GameInstance,
  type Meter,
  type PitchLadderMode,
  type RhythmEchoMode,
  type SolfegeTargetMode,
  type TemplateForm,
  type TemplateId,
  type TimbreDetectiveMode
} from "./store";
import { playHybridTimbreProfile, playHybridToneSequence } from "./shared/realAudio";
import { resolvePitchToken } from "./shared/pitchCatalog";

const templateLabels: Record<TemplateId, string> = {
  beat_guardian_core: "充能护盾",
  pitch_ladder_core: "音高爬梯",
  rhythm_echo_core: "节奏复刻",
  solfege_target_core: "唱名打靶",
  timbre_detective_core: "音色侦探",
  form_treasure_core: "曲式寻宝",
  composition_puzzle_core: "拼图创编工坊"
};

const beatGuardianModeLabels: Record<BeatGuardianMode, string> = {
  beat_defense: "护盾充能",
  strong_beat_guard: "强拍充能",
  meter_gate: "拍号护盾"
};

const rhythmModeLabels: Record<RhythmEchoMode, string> = {
  echo_tap: "点按复刻",
  echo_body_percussion: "身体打击",
  echo_chain: "复刻接龙"
};

const pitchModeLabels: Record<PitchLadderMode, string> = {
  high_low_steps: "高低台阶",
  solfege_ladder: "唱名定位",
  melody_climb: "旋律攀爬"
};

const solfegeModeLabels: Record<SolfegeTargetMode, string> = {
  listen_and_hit: "听音打靶",
  aim_and_sing: "瞄准后唱",
  target_chain: "连环靶"
};

const timbreModeLabels: Record<TimbreDetectiveMode, string> = {
  instrument_clue: "乐器线索",
  family_sorting: "家族归档",
  compare_twins: "双声辨影"
};

const formModeLabels: Record<FormTreasureMode, string> = {
  aba_treasure: "ABA 寻宝",
  rondo_treasure: "回旋寻宝",
  repeat_contrast: "重复对比"
};

const compositionModeLabels: Record<CompositionPuzzleMode, string> = {
  rhythm_puzzle_composition: "节奏拼图创编",
  melody_puzzle_creation: "旋律拼图创作",
  melody_rhythm_puzzle: "旋律节奏拼图"
};

const skinLabels: Record<GameSkin, string> = {
  castle_gate: "充能护盾",
  stage_light: "舞台追光",
  dragon_boat: "龙舟鼓点",
  train_conductor: "节拍列车",
  space_orbit: "星球轨道",
  rhythm_radio: "节奏电波传呼机",
  echo_cave: "回声山洞",
  robot_signal: "机器人信号",
  rain_window: "雨点窗台",
  kitchen_band: "厨房乐队",
  mountain_steps: "音高山路",
  cloud_elevator: "云梯升空",
  bamboo_ladder: "竹节爬梯",
  lantern_tower: "灯塔点灯",
  star_target: "唱名星靶场",
  flower_bloom: "花朵绽放",
  lantern_target: "灯笼靶会",
  archery_field: "音乐弓箭场",
  bubble_pop: "泡泡唱名",
  sound_casebook: "声音案卷",
  museum_clues: "乐器博物馆",
  forest_echo: "森林回声",
  studio_mixer: "录音棚调音台",
  shadow_theater: "声影剧场",
  treasure_map: "藏宝图寻宝",
  constellation_path: "星图航线",
  museum_gallery: "音乐展馆",
  train_route: "音乐列车",
  stage_script: "剧场分幕",
  composition_studio: "音乐创编教室",
  rhythm_tile_table: "节奏积木桌",
  melody_garden: "旋律花园"
};

type ConsoleContext = "lesson" | "direct";

type LessonRecommendation = {
  matched: boolean;
  template_id: string;
  template_label: string;
  lesson_focus: string;
  lesson_stage: string;
  fit_summary: string;
  reason: string;
  match_status: string;
  music_element_adjustment_contract?: {
    status?: string;
    lesson_focus?: {
      primary_element?: string;
      element_family?: string;
      evidence?: string;
    };
    template_match?: {
      confidence?: number;
      reason?: string;
    };
    element_adjustments?: Array<{
      teacher_label?: string;
      template_config_key?: string;
    }>;
    unsupported_elements?: string[];
  };
};

const consoleContext: ConsoleContext =
  new URLSearchParams(window.location.search).get("context") === "lesson" ? "lesson" : "direct";
const lessonProposalId = new URLSearchParams(window.location.search).get("proposal_id") || "";

const lessonDifficultyLabels: Record<Difficulty, string> = {
  L1: "入门",
  L2: "基础",
  L3: "标准",
  L4: "进阶",
  L5: "挑战"
};

const lessonSpeedLabels = {
  slower: "慢一些",
  steady: "适中",
  faster: "快一些"
} as const;

type LessonSpeed = keyof typeof lessonSpeedLabels;

export function App() {
  const { form, updateForm, loadForm, switchTemplate, createInstance, instance, loading, error } = useConsoleStore();
  const [lessonRecommendation, setLessonRecommendation] = useState<LessonRecommendation | null>(null);
  const isLessonContext = consoleContext === "lesson";
  const activeInstance = instance?.template_id === form.template_id ? instance : null;
  const activeConfig = activeInstance?.config ?? form;
  const isBeatGuardian = form.template_id === "beat_guardian_core";
  const isPitchLadder = form.template_id === "pitch_ladder_core";
  const isSolfegeTarget = form.template_id === "solfege_target_core";
  const isTimbreDetective = form.template_id === "timbre_detective_core";
  const isFormTreasure = form.template_id === "form_treasure_core";
  const isCompositionPuzzle = form.template_id === "composition_puzzle_core";
  const isPitchGame = isPitchLadder || isSolfegeTarget;
  const canSyncLessonConfig =
    !isLessonContext ||
    Boolean(lessonRecommendation?.matched && lessonRecommendation.template_id === form.template_id);

  useEffect(() => {
    if (!canSyncLessonConfig) return;
    window.parent?.postMessage(
      {
        type: "buyilehu-template-config",
        config: form
      },
      window.location.origin
    );
  }, [canSyncLessonConfig, form]);

  useEffect(() => {
    if (!instance) return;
    window.parent?.postMessage(
      {
        type: "buyilehu-template-instance",
        instance
      },
      window.location.origin
    );
  }, [instance]);

  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      if (event.origin !== window.location.origin) return;
      if (event.data?.type === "buyilehu-load-template-config" && event.data?.config) {
        loadForm(event.data.config as Partial<TemplateForm>);
      }
      if (event.data?.type === "buyilehu-load-lesson-recommendation" && event.data?.recommendation) {
        setLessonRecommendation(event.data.recommendation as LessonRecommendation);
      }
    };
    window.addEventListener("message", handleMessage);
    window.parent?.postMessage(
      {
        type: "buyilehu-template-console-ready",
        context: consoleContext
      },
      window.location.origin
    );
    return () => window.removeEventListener("message", handleMessage);
  }, [loadForm]);

  useEffect(() => {
    if (!isLessonContext || !lessonProposalId) return;
    let cancelled = false;
    const loadLessonWorkflow = async () => {
      try {
        const response = await fetch("/api/workflows/lesson-game/plan", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ proposal_id: lessonProposalId })
        });
        const data = await response.json();
        if (!response.ok || cancelled) return;
        const workflow = data.workflow || {};
        const instance = workflow.instance || {};
        const proposalCard = workflow.proposal_card || {};
        const lessonFit = workflow.source?.lesson_fit || proposalCard.lesson_fit || {};
        const templateHint = lessonFit.template_hint || {};
        const adjustmentContract =
          workflow.source?.music_element_adjustment_contract ||
          lessonFit.music_element_adjustment_contract ||
          {};
        setLessonRecommendation({
          matched: Boolean(instance.template_id),
          template_id: instance.template_id || "",
          template_label: instance.template_label || proposalCard.template_label || "",
          lesson_focus: proposalCard.music_element || lessonFit.lesson_evidence?.music_element || "",
          lesson_stage: lessonFit.lesson_evidence?.target_stage || "",
          fit_summary: proposalCard.fit_summary || lessonFit.fit_summary || "",
          reason: templateHint.reason || "",
          match_status: templateHint.match_status || (instance.template_id ? "exact" : "unmatched"),
          music_element_adjustment_contract: adjustmentContract
        });
        if (instance.config && instance.template_id) {
          loadForm(instance.config as Partial<TemplateForm>);
        }
      } catch {
        // Parent-page sync remains available if this direct recovery path fails.
      }
    };
    void loadLessonWorkflow();
    return () => {
      cancelled = true;
    };
  }, [isLessonContext, loadForm]);

  return (
    <main className="app-shell">
      <Container size="4" px="5">
        <Flex className="topbar" justify="between" align="center" gap="4">
          <Box>
            <Text className="eyebrow">
              {isLessonContext ? "不亦乐乎 · 本课游戏设置" : "不亦乐乎 · 直接生成"}
            </Text>
            <Heading className="page-title">
              {isLessonContext ? "为这节课准备游戏" : "选择游戏和难度"}
            </Heading>
          </Box>
          <Badge size="3" color="teal" variant="soft">
            {isLessonContext
              ? !lessonRecommendation
                ? "正在准备"
                : lessonRecommendation.matched
                  ? "已为本课推荐"
                  : "继续设计中"
              : "教师可自定义"}
          </Badge>
        </Flex>

        {isLessonContext ? <LessonRecommendationCard recommendation={lessonRecommendation} /> : <DirectWorkflowCard />}

        <Grid columns={isLessonContext ? "1" : { initial: "1", lg: "1.05fr 0.95fr" }} gap="5" align="start">
          <section className="control-panel">
            <Flex align="center" gap="3" mb="4">
              <Settings2 size={22} />
              <Heading size="5">{isLessonContext ? "游戏设置" : "游戏配置"}</Heading>
            </Flex>

            {isLessonContext ? (
              <LessonTeacherControls
                form={form}
                updateForm={updateForm}
                recommendation={lessonRecommendation}
                isBeatGuardian={isBeatGuardian}
                isPitchLadder={isPitchLadder}
                isSolfegeTarget={isSolfegeTarget}
                isTimbreDetective={isTimbreDetective}
                isFormTreasure={isFormTreasure}
                isCompositionPuzzle={isCompositionPuzzle}
              />
            ) : (
              <DirectTemplateControls
                form={form}
                updateForm={updateForm}
                switchTemplate={switchTemplate}
                isBeatGuardian={isBeatGuardian}
                isPitchLadder={isPitchLadder}
                isSolfegeTarget={isSolfegeTarget}
                isTimbreDetective={isTimbreDetective}
                isFormTreasure={isFormTreasure}
                isCompositionPuzzle={isCompositionPuzzle}
                isPitchGame={isPitchGame}
                createInstance={createInstance}
                loading={loading}
                error={error}
              />
            )}
          </section>

          {!isLessonContext ? (
            <section className="preview-panel">
              <Flex align="center" gap="3" mb="4">
                {isCompositionPuzzle ? (
                  <Sparkles size={22} />
                ) : isTimbreDetective ? (
                  <FileSearch size={22} />
                ) : isFormTreasure ? (
                  <Map size={22} />
                ) : isSolfegeTarget ? (
                  <Crosshair size={22} />
                ) : isPitchLadder ? (
                  <Mountain size={22} />
                ) : isBeatGuardian ? (
                  <Castle size={22} />
                ) : (
                  <Music2 size={22} />
                )}
                <Heading size="5">模板预览</Heading>
              </Flex>

              {isCompositionPuzzle ? (
                <CompositionPuzzleStage config={activeConfig} instance={activeInstance} />
              ) : isTimbreDetective ? (
                <TimbreDetectiveStage config={activeConfig} instance={activeInstance} />
              ) : isFormTreasure ? (
                <FormTreasureStage config={activeConfig} instance={activeInstance} />
              ) : isSolfegeTarget ? (
                <SolfegeTargetStage config={activeConfig} instance={activeInstance} />
              ) : isPitchLadder ? (
                <PitchLadderStage config={activeConfig} instance={activeInstance} />
              ) : isBeatGuardian ? (
                <BeatGuardianStage config={activeConfig} instance={activeInstance} />
              ) : (
                <RhythmEchoPreview form={form} instance={activeInstance} />
              )}

            </section>
          ) : null}
        </Grid>
      </Container>
    </main>
  );
}

function DirectWorkflowCard() {
  return (
    <Card className="workflow-card workflow-single direct">
      <Text className="stage-kicker">直接生成</Text>
      <Heading size="4">选择玩法和难度即可生成</Heading>
      <Text as="p" color="gray" mt="2">
        细节参数放在更多设置里，需要时再展开。
      </Text>
    </Card>
  );
}

function getLessonSpeed(bpm: number): LessonSpeed {
  if (bpm <= 78) return "slower";
  if (bpm >= 100) return "faster";
  return "steady";
}

function lessonSpeedToBpm(speed: LessonSpeed) {
  if (speed === "slower") return 72;
  if (speed === "faster") return 108;
  return 88;
}

function beatGuardianDifficultyPatch(difficulty: Difficulty): Partial<TemplateForm> {
  if (difficulty === "L1") {
    return {
      difficulty,
      mode: "beat_defense",
      meter: "2/4",
      bpm: 76,
      timing_tolerance_ms: 240,
      target_beats: [1],
      combo_required: 4,
      mistake_limit: 5,
      show_beat_track: true,
      show_strong_beat_hint: true,
      show_weak_beat_hint: true,
      visual_beat_hint: true
    };
  }
  if (difficulty === "L2") {
    return {
      difficulty,
      mode: "strong_beat_guard",
      meter: "2/4",
      bpm: 86,
      timing_tolerance_ms: 205,
      target_beats: [1],
      combo_required: 4,
      mistake_limit: 5,
      show_beat_track: true,
      show_strong_beat_hint: true,
      show_weak_beat_hint: false,
      visual_beat_hint: true
    };
  }
  if (difficulty === "L3") {
    return {
      difficulty,
      mode: "strong_beat_guard",
      meter: "4/4",
      bpm: 96,
      timing_tolerance_ms: 175,
      target_beats: [1],
      combo_required: 4,
      mistake_limit: 5,
      show_beat_track: true,
      show_strong_beat_hint: true,
      show_weak_beat_hint: false,
      visual_beat_hint: true
    };
  }
  if (difficulty === "L4") {
    return {
      difficulty,
      mode: "meter_gate",
      meter: "3/4",
      bpm: 104,
      timing_tolerance_ms: 155,
      target_beats: [1],
      combo_required: 4,
      mistake_limit: 5,
      show_beat_track: true,
      show_strong_beat_hint: true,
      show_weak_beat_hint: false,
      visual_beat_hint: false
    };
  }
  if (difficulty === "L5") {
    return {
      difficulty,
      mode: "meter_gate",
      meter: "4/4",
      bpm: 112,
      timing_tolerance_ms: 140,
      target_beats: [1],
      combo_required: 4,
      mistake_limit: 5,
      show_beat_track: false,
      show_strong_beat_hint: false,
      show_weak_beat_hint: false,
      visual_beat_hint: false
    };
  }
  return {
    difficulty,
    show_beat_track: true,
    show_strong_beat_hint: true,
    show_weak_beat_hint: false,
    visual_beat_hint: true
  };
}

function difficultyPatchForTemplate(difficulty: Difficulty, isBeatGuardian: boolean): Partial<TemplateForm> {
  return isBeatGuardian ? beatGuardianDifficultyPatch(difficulty) : { difficulty };
}

const beatGuardianSupportSteps = [
  {
    level: "L1",
    title: "看见每拍",
    copy: "强拍、弱拍和同步亮点都打开，先建立稳定拍周期。",
    tags: ["轨道", "强拍", "弱拍", "亮点"]
  },
  {
    level: "L2-L3",
    title: "只强调第 1 拍",
    copy: "弱拍变成蓄势时间，学生开始从小节周期里预判强拍。",
    tags: ["轨道", "强拍", "亮点"]
  },
  {
    level: "L4",
    title: "撤掉同步亮点",
    copy: "保留拍位参照，但不再闪烁答案，观察是否能提前准备动作。",
    tags: ["轨道", "强拍"]
  },
  {
    level: "L5",
    title: "听觉挑战",
    copy: "拍点轨道也撤掉，主要依靠听觉、身体律动和内心稳定拍。",
    tags: ["听觉", "身体"]
  }
];

function beatGuardianSupportProfile(form: TemplateForm): {
  label: string;
  tone: "green" | "blue" | "amber";
  description: string;
  observable: string;
} {
  if (!form.show_beat_track && !form.visual_beat_hint) {
    return {
      label: "听觉挑战",
      tone: "amber",
      description: "拍点轨道和同步亮点都已撤掉。",
      observable: "看学生能否用口数、律动或内心拍提前落在第 1 拍。"
    };
  }
  if (!form.visual_beat_hint || !form.show_weak_beat_hint || !form.show_strong_beat_hint) {
    return {
      label: "半支架",
      tone: "blue",
      description: "保留必要参照，但弱化直接答案。",
      observable: "看学生是否从等画面提示，转为预判下一小节开头。"
    };
  }
  return {
    label: "全支架",
    tone: "green",
    description: "强拍、弱拍、轨道与同步亮点都打开。",
    observable: "适合入门或集体示范，先让学生说出强弱规律。"
  };
}

function BeatGuardianSupportPanel({ form }: { form: TemplateForm }) {
  const profile = beatGuardianSupportProfile(form);
  return (
    <Box className="beat-support-panel">
      <Flex align="center" justify="between" gap="3" wrap="wrap">
        <Box>
          <Text className="stage-kicker">节拍守卫 · 支架阶梯</Text>
          <Heading size="3">从看见拍点，过渡到听觉预判</Heading>
          <Text as="p" className="beat-support-copy">
            {profile.description} {profile.observable}
          </Text>
        </Box>
        <Badge color={profile.tone} variant="solid">
          当前：{profile.label}
        </Badge>
      </Flex>
      <div className="beat-support-steps" aria-label="节拍守卫支架阶梯">
        {beatGuardianSupportSteps.map((step) => {
          const active = step.level === "L2-L3" ? form.difficulty === "L2" || form.difficulty === "L3" : step.level === form.difficulty;
          return (
            <div key={step.level} className={`beat-support-step${active ? " active" : ""}`}>
              <strong>{step.level}</strong>
              <span>{step.title}</span>
              <p>{step.copy}</p>
              <div className="beat-support-tags">
                {step.tags.map((tag) => (
                  <em key={tag}>{tag}</em>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </Box>
  );
}

function getLessonSupportEnabled(
  form: TemplateForm,
  {
    isBeatGuardian,
    isPitchLadder,
    isSolfegeTarget,
    isTimbreDetective,
    isCompositionPuzzle
  }: {
    isBeatGuardian: boolean;
    isPitchLadder: boolean;
    isSolfegeTarget: boolean;
    isTimbreDetective: boolean;
    isCompositionPuzzle?: boolean;
  }
) {
  if (isCompositionPuzzle) return form.show_beat_track || form.show_solfege_hint;
  if (isTimbreDetective) return form.show_wave_hint || form.show_family_hint;
  if (isSolfegeTarget) return form.show_solfege_hint;
  if (isPitchLadder) return form.show_solfege_hint || form.show_direction_hint || form.show_staff_hint;
  if (isBeatGuardian) return form.show_beat_track || form.show_strong_beat_hint || form.show_weak_beat_hint || form.visual_beat_hint;
  return form.visual_beat_hint;
}

function getLessonSupportPatch(
  enabled: boolean,
  {
    isBeatGuardian,
    isPitchLadder,
    isSolfegeTarget,
    isTimbreDetective,
    isCompositionPuzzle
  }: {
    isBeatGuardian: boolean;
    isPitchLadder: boolean;
    isSolfegeTarget: boolean;
    isTimbreDetective: boolean;
    isCompositionPuzzle?: boolean;
  }
): Partial<TemplateForm> {
  if (isCompositionPuzzle) {
    return { show_beat_track: enabled, show_solfege_hint: enabled };
  }
  if (isTimbreDetective) {
    return { show_wave_hint: enabled, show_family_hint: enabled };
  }
  if (isSolfegeTarget) {
    return { show_solfege_hint: enabled };
  }
  if (isPitchLadder) {
    return {
      show_solfege_hint: enabled,
      show_direction_hint: enabled,
      show_staff_hint: enabled
    };
  }
  if (isBeatGuardian) {
    return {
      show_beat_track: enabled,
      show_strong_beat_hint: enabled,
      show_weak_beat_hint: enabled,
      visual_beat_hint: enabled
    };
  }
  return { visual_beat_hint: enabled };
}

function LessonRecommendationCard({ recommendation }: { recommendation: LessonRecommendation | null }) {
  if (!recommendation) {
    return (
      <Card className="lesson-recommendation pending">
        <Text className="stage-kicker">正在分析教案</Text>
        <Heading size="4">正在为这节课挑选合适的游戏</Heading>
        <Text as="p" color="gray" mt="2">
          先看看学生这节课要学什么，再为他们准备合适的玩法。
        </Text>
      </Card>
    );
  }

  if (!recommendation.matched) {
    return (
      <Card className="lesson-recommendation unmatched">
        <Text className="stage-kicker">更适合专属设计</Text>
        <Heading size="4">这节课需要更贴合的游戏</Heading>
        <Text as="p" color="gray" mt="2">
          {recommendation.lesson_focus
            ? `本课重点是“${recommendation.lesson_focus}”。`
            : "已经看清这节课的学习重点。"}
          为了让游戏真正服务学习，这次会继续围绕本课目标设计更合适的玩法。
        </Text>
      </Card>
    );
  }

  return (
    <Card className="lesson-recommendation matched compact">
      <Flex justify="between" align="center" gap="3" wrap="wrap">
        <Text weight="bold">已为本课选好游戏</Text>
        <Flex gap="2" wrap="wrap" align="center">
          <Badge color="teal" variant="soft">
            {recommendation.template_label || "成熟玩法"}
          </Badge>
          {recommendation.lesson_focus ? <Badge color="gray" variant="soft">{recommendation.lesson_focus}</Badge> : null}
          {recommendation.lesson_stage ? <Badge color="gray" variant="soft">{recommendation.lesson_stage}</Badge> : null}
        </Flex>
      </Flex>
    </Card>
  );
}

function LessonAdjustmentSummary({ recommendation }: { recommendation: LessonRecommendation }) {
  const contract = recommendation.music_element_adjustment_contract;
  const adjustments = contract?.element_adjustments?.filter((item) => item.teacher_label).slice(0, 4) || [];
  const confidence = contract?.template_match?.confidence;
  if (!contract && !adjustments.length) return null;

  return (
    <Box className="lesson-adjustment-summary" mt="4">
      <Flex gap="2" wrap="wrap" align="center">
        <Badge color="teal" variant="soft">
          {contract?.lesson_focus?.primary_element || recommendation.lesson_focus || "音乐要素"}
        </Badge>
        {typeof confidence === "number" ? (
          <Badge color="amber" variant="soft">
            置信度 {Math.round(confidence * 100)}%
          </Badge>
        ) : null}
      </Flex>
      {adjustments.length ? (
        <Grid columns={{ initial: "1", sm: "2" }} gap="2" mt="3">
          {adjustments.map((item) => (
            <Text key={`${item.template_config_key}-${item.teacher_label}`} as="p" size="2" className="lesson-adjustment-chip">
              {item.teacher_label}
            </Text>
          ))}
        </Grid>
      ) : null}
    </Box>
  );
}

function LessonTeacherControls({
  form,
  updateForm,
  recommendation,
  isBeatGuardian,
  isPitchLadder,
  isSolfegeTarget,
  isTimbreDetective,
  isFormTreasure,
  isCompositionPuzzle
}: {
  form: TemplateForm;
  updateForm: (patch: Partial<TemplateForm>) => void;
  recommendation: LessonRecommendation | null;
  isBeatGuardian: boolean;
  isPitchLadder: boolean;
  isSolfegeTarget: boolean;
  isTimbreDetective: boolean;
  isFormTreasure: boolean;
  isCompositionPuzzle: boolean;
}) {
  const [advancedOpen, setAdvancedOpen] = useState(false);

  if (!recommendation) {
    return (
      <Text as="p" color="gray">
        教案分析完成后，这里会出现适合这节课的游戏设置。
      </Text>
    );
  }

  if (!recommendation.matched) {
    return (
      <Box className="lesson-note-card">
        <Heading size="4">这节课先不使用现成玩法</Heading>
        <Text as="p" color="gray" mt="2">
          目前还没有与本课重点足够贴合的成熟玩法。为了让学生学得更准，这次会继续按本课目标设计游戏。
        </Text>
      </Box>
    );
  }

  const lessonSupportEnabled = getLessonSupportEnabled(form, {
    isBeatGuardian,
    isPitchLadder,
    isSolfegeTarget,
    isTimbreDetective,
    isCompositionPuzzle
  });
  const lessonSpeed = getLessonSpeed(form.bpm);
  const summary =
    recommendation.fit_summary ||
    recommendation.reason ||
    `已选用${recommendation.template_label || templateLabels[form.template_id]}，老师只需要确认难度和练习轮数。`;

  return (
    <>
      <Card className="lesson-simple-summary" mb="4">
        <Flex align="center" justify="between" gap="3" wrap="wrap">
          <Box>
            <Text className="stage-kicker">本课游戏</Text>
            <Heading size="4">{recommendation.template_label || templateLabels[form.template_id]}</Heading>
            <Text as="p" color="gray" mt="1">
              {summary}
            </Text>
          </Box>
        </Flex>
      </Card>

      <Grid className="lesson-primary-controls" columns={{ initial: "1", sm: "2" }} gap="4">
        <LabeledControl label="练习难度">
          <Select.Root
            value={form.difficulty}
            onValueChange={(value) => updateForm(difficultyPatchForTemplate(value as Difficulty, isBeatGuardian))}
          >
            <Select.Trigger />
            <Select.Content>
              {Object.entries(lessonDifficultyLabels).map(([value, label]) => (
                <Select.Item key={value} value={value}>
                  {label}
                </Select.Item>
              ))}
            </Select.Content>
          </Select.Root>
        </LabeledControl>

        <LabeledControl label="练习轮数">
          <Select.Root value={String(form.round_count)} onValueChange={(value) => updateForm({ round_count: Number(value) })}>
            <Select.Trigger />
            <Select.Content>
              {[3, 4, 5, 6, 8, 10].map((count) => (
                <Select.Item key={count} value={String(count)}>
                  {count} 轮
                </Select.Item>
              ))}
            </Select.Content>
          </Select.Root>
        </LabeledControl>
      </Grid>

      <Box className="lesson-advanced">
        <Button type="button" variant="soft" color="gray" onClick={() => setAdvancedOpen((open) => !open)}>
          <Settings2 size={16} />
          {advancedOpen ? "收起更多设置" : "更多设置"}
        </Button>

        {advancedOpen ? (
          <Box className="lesson-advanced-panel" mt="3">
            <Text as="p" className="lesson-inline-help">
              图片会按教案和歌曲氛围自动生成。
            </Text>

            <Grid columns={{ initial: "1", sm: "2" }} gap="4" mt="3">
              {isPitchLadder ? (
                <LabeledControl label="玩法模式">
                  <Select.Root value={form.mode} onValueChange={(value) => updateForm({ mode: value as TemplateForm["mode"] })}>
                    <Select.Trigger />
                    <Select.Content>
                      <Select.Item value="high_low_steps">高低台阶</Select.Item>
                      <Select.Item value="solfege_ladder">唱名定位</Select.Item>
                      <Select.Item value="melody_climb">旋律攀爬</Select.Item>
                    </Select.Content>
                  </Select.Root>
                </LabeledControl>
              ) : null}

              {!isPitchLadder && !isSolfegeTarget && !isTimbreDetective && !isFormTreasure && !isCompositionPuzzle ? (
                <LabeledControl label="练习速度">
                  <Select.Root
                    value={lessonSpeed}
                    onValueChange={(value) => updateForm({ bpm: lessonSpeedToBpm(value as LessonSpeed) })}
                  >
                    <Select.Trigger />
                    <Select.Content>
                      {Object.entries(lessonSpeedLabels).map(([value, label]) => (
                        <Select.Item key={value} value={value}>
                          {label}
                        </Select.Item>
                      ))}
                    </Select.Content>
                  </Select.Root>
                </LabeledControl>
              ) : null}
            </Grid>

            {isBeatGuardian ? <BeatGuardianSupportPanel form={form} /> : null}

            {isPitchLadder ? <PitchControls form={form} updateForm={updateForm} compact /> : null}

            {isFormTreasure ? <FormTreasureControls form={form} updateForm={updateForm} compact /> : null}

            {isCompositionPuzzle ? <CompositionPuzzleControls form={form} updateForm={updateForm} compact /> : null}

            <Flex gap="5" wrap="wrap" mt="4">
              <ToggleRow
                label="允许学生重听"
                checked={form.allow_relisten}
                onCheckedChange={(value) => updateForm({ allow_relisten: value })}
              />
              <ToggleRow
                label="先给一轮练习"
                checked={form.allow_practice_round}
                onCheckedChange={(value) => updateForm({ allow_practice_round: value })}
              />
              <ToggleRow
                label="给学生更多提示"
                checked={lessonSupportEnabled}
                onCheckedChange={(value) =>
                  updateForm(
                    getLessonSupportPatch(value, {
                      isBeatGuardian,
                      isPitchLadder,
                      isSolfegeTarget,
                      isTimbreDetective,
                      isCompositionPuzzle
                    })
                  )
                }
              />
              {isPitchLadder || isSolfegeTarget ? (
                <ToggleRow
                  label="要求学生唱回"
                  checked={form.sing_back_required ?? form.require_sing_back}
                  onCheckedChange={(value) => updateForm({ require_sing_back: value, sing_back_required: value })}
                />
              ) : null}
              {isTimbreDetective ? (
                <ToggleRow
                  label="要求说出判断依据"
                  checked={form.require_reason}
                  onCheckedChange={(value) => updateForm({ require_reason: value })}
                />
              ) : null}
            </Flex>

            <Box mt="4">
              <LabeledControl label="教师引导语">
                <TextArea
                  value={form.teacher_prompt}
                  onChange={(event) => updateForm({ teacher_prompt: event.target.value })}
                  rows={3}
                />
              </LabeledControl>
            </Box>

            <TemplateVisualBase form={form} compact />
            <LessonAdjustmentSummary recommendation={recommendation} />
          </Box>
        ) : null}
      </Box>
    </>
  );
}

function DirectTemplateControls({
  form,
  updateForm,
  switchTemplate,
  isBeatGuardian,
  isPitchLadder,
  isSolfegeTarget,
  isTimbreDetective,
  isFormTreasure,
  isCompositionPuzzle,
  isPitchGame,
  createInstance,
  loading,
  error
}: {
  form: TemplateForm;
  updateForm: (patch: Partial<TemplateForm>) => void;
  switchTemplate: (templateId: TemplateId) => void;
  isBeatGuardian: boolean;
  isPitchLadder: boolean;
  isSolfegeTarget: boolean;
  isTimbreDetective: boolean;
  isFormTreasure: boolean;
  isCompositionPuzzle: boolean;
  isPitchGame: boolean;
  createInstance: () => Promise<void>;
  loading: boolean;
  error: string;
}) {
  const [advancedOpen, setAdvancedOpen] = useState(false);

  return (
    <>
      <Grid className="direct-primary-controls" columns={{ initial: "1", sm: "2" }} gap="4">
        <LabeledControl label="游戏模板">
          <Select.Root value={form.template_id} onValueChange={(value) => switchTemplate(value as TemplateId)}>
            <Select.Trigger />
            <Select.Content>
              <Select.Item value="beat_guardian_core">充能护盾</Select.Item>
              <Select.Item value="pitch_ladder_core">音高爬梯</Select.Item>
              <Select.Item value="rhythm_echo_core">节奏复刻</Select.Item>
              <Select.Item value="solfege_target_core">唱名打靶</Select.Item>
              <Select.Item value="timbre_detective_core">音色侦探</Select.Item>
              <Select.Item value="form_treasure_core">曲式寻宝</Select.Item>
              <Select.Item value="composition_puzzle_core">拼图创编工坊</Select.Item>
            </Select.Content>
          </Select.Root>
        </LabeledControl>

        <LabeledControl label="难度档位">
          <Select.Root
            value={form.difficulty}
            onValueChange={(value) => updateForm(difficultyPatchForTemplate(value as Difficulty, isBeatGuardian))}
          >
            <Select.Trigger />
            <Select.Content>
              {isCompositionPuzzle ? (
                <>
                  <Select.Item value="L1">L1 · 1 小节引导</Select.Item>
                  <Select.Item value="L2">L2 · 2 小节创编</Select.Item>
                  <Select.Item value="L3">L3 · 约束检查</Select.Item>
                  <Select.Item value="L4">L4 · 3 小节变化</Select.Item>
                  <Select.Item value="L5">L5 · 开放挑战</Select.Item>
                </>
              ) : isFormTreasure ? (
                <>
                  <Select.Item value="aba_treasure">ABA 寻宝</Select.Item>
                  <Select.Item value="rondo_treasure">回旋寻宝</Select.Item>
                  <Select.Item value="repeat_contrast">重复对比</Select.Item>
                </>
              ) : isTimbreDetective ? (
                <>
                  <Select.Item value="L1">L1 · 找声音朋友</Select.Item>
                  <Select.Item value="L2">L2 · 乐器嫌疑人</Select.Item>
                  <Select.Item value="L3">L3 · 家族归档</Select.Item>
                  <Select.Item value="L4">L4 · 双声辨影</Select.Item>
                  <Select.Item value="L5">L5 · 相似音色推理</Select.Item>
                </>
              ) : isSolfegeTarget ? (
                <>
                  <Select.Item value="L1">L1 · 三音靶</Select.Item>
                  <Select.Item value="L2">L2 · 五声靶</Select.Item>
                  <Select.Item value="L3">L3 · 瞄准后唱</Select.Item>
                  <Select.Item value="L4">L4 · 连环双靶</Select.Item>
                  <Select.Item value="L5">L5 · 短句靶阵</Select.Item>
                </>
              ) : isPitchLadder ? (
                <>
                  <Select.Item value="L1">L1 · 高低方向</Select.Item>
                  <Select.Item value="L2">L2 · 加入相同音</Select.Item>
                  <Select.Item value="L3">L3 · 唱名定位</Select.Item>
                  <Select.Item value="L4">L4 · 三音路线</Select.Item>
                  <Select.Item value="L5">L5 · 短句记忆</Select.Item>
                </>
              ) : isBeatGuardian ? (
                <>
                  <Select.Item value="L1">L1 · 每拍稳定</Select.Item>
                  <Select.Item value="L2">L2 · 第 1 拍充能</Select.Item>
                  <Select.Item value="L3">L3 · 四拍子护盾</Select.Item>
                  <Select.Item value="L4">L4 · 三拍子护盾</Select.Item>
                  <Select.Item value="L5">L5 · 少视觉提示</Select.Item>
                </>
              ) : (
                <>
                  <Select.Item value="L1">L1 · 单一节奏</Select.Item>
                  <Select.Item value="L2">L2 · 加入休止</Select.Item>
                  <Select.Item value="L3">L3 · 两小节记忆</Select.Item>
                  <Select.Item value="L4">L4 · 附点或切分</Select.Item>
                  <Select.Item value="L5">L5 · 复刻后接龙</Select.Item>
                </>
              )}
            </Select.Content>
          </Select.Root>
        </LabeledControl>
      </Grid>

      <Flex gap="3" mt="4" wrap="wrap">
        <Button size="3" onClick={createInstance} disabled={loading}>
          <Play size={18} />
          生成游戏实例
        </Button>
        <Button size="3" variant="soft" color="gray" onClick={() => window.location.reload()}>
          <RotateCcw size={18} />
          重置
        </Button>
      </Flex>
      {error ? (
        <Text as="p" color="red" mt="3">
          {error}
        </Text>
      ) : null}

      <Box className="direct-advanced">
        <Button type="button" variant="soft" color="gray" onClick={() => setAdvancedOpen((open) => !open)}>
          <Settings2 size={16} />
          {advancedOpen ? "收起更多设置" : "更多设置"}
        </Button>

        {advancedOpen ? (
          <Box className="direct-advanced-panel" mt="3">
            <Text as="p" className="lesson-inline-help">
              图片会按课堂主题和生成内容自动决定视觉氛围。
            </Text>

            <Grid columns={{ initial: "1", sm: "2" }} gap="4" mt="3">
              <LabeledControl label="玩法模式">
                <Select.Root value={form.mode} onValueChange={(value) => updateForm({ mode: value as TemplateForm["mode"] })}>
                  <Select.Trigger />
                  <Select.Content>
                    {isCompositionPuzzle ? (
                      <>
                        <Select.Item value="rhythm_puzzle_composition">节奏拼图创编</Select.Item>
                        <Select.Item value="melody_puzzle_creation">旋律拼图创作</Select.Item>
                        <Select.Item value="melody_rhythm_puzzle">旋律节奏拼图</Select.Item>
                      </>
                    ) : isTimbreDetective ? (
                      <>
                        <Select.Item value="instrument_clue">乐器线索</Select.Item>
                        <Select.Item value="family_sorting">家族归档</Select.Item>
                        <Select.Item value="compare_twins">双声辨影</Select.Item>
                      </>
                    ) : isSolfegeTarget ? (
                      <>
                        <Select.Item value="listen_and_hit">听音打靶</Select.Item>
                        <Select.Item value="aim_and_sing">瞄准后唱</Select.Item>
                        <Select.Item value="target_chain">连环靶</Select.Item>
                      </>
                    ) : isPitchLadder ? (
                      <>
                        <Select.Item value="high_low_steps">高低台阶</Select.Item>
                        <Select.Item value="solfege_ladder">唱名定位</Select.Item>
                        <Select.Item value="melody_climb">旋律攀爬</Select.Item>
                      </>
                    ) : isBeatGuardian ? (
                      <>
                        <Select.Item value="beat_defense">护盾呼吸</Select.Item>
                        <Select.Item value="strong_beat_guard">第一拍充能</Select.Item>
                        <Select.Item value="meter_gate">拍号护盾</Select.Item>
                      </>
                    ) : (
                      <>
                        <Select.Item value="echo_tap">点按复刻</Select.Item>
                        <Select.Item value="echo_body_percussion">身体打击</Select.Item>
                        <Select.Item value="echo_chain">复刻接龙</Select.Item>
                      </>
                    )}
                  </Select.Content>
                </Select.Root>
              </LabeledControl>

              <LabeledControl label={isPitchGame ? "课堂脉搏" : "拍号"}>
                <Select.Root value={form.meter} onValueChange={(value) => updateForm({ meter: value as Meter })}>
                  <Select.Trigger />
                  <Select.Content>
                    <Select.Item value="2/4">2/4</Select.Item>
                    <Select.Item value="3/4">3/4</Select.Item>
                    <Select.Item value="4/4">4/4</Select.Item>
                  </Select.Content>
                </Select.Root>
              </LabeledControl>
            </Grid>

            <Grid columns={{ initial: "1", sm: "2" }} gap="4" mt="4">
              <LabeledControl label="学段">
                <TextField.Root value={form.grade_band} onChange={(event) => updateForm({ grade_band: event.target.value })} />
              </LabeledControl>
              <LabeledControl label="音乐要素">
                <TextField.Root value={form.music_concept} onChange={(event) => updateForm({ music_concept: event.target.value })} />
              </LabeledControl>
            </Grid>

            <Box mt="4">
              <TemplateVisualBase form={form} compact />
            </Box>

            {isTimbreDetective ? (
              <TimbreControls form={form} updateForm={updateForm} />
            ) : isCompositionPuzzle ? (
              <CompositionPuzzleControls form={form} updateForm={updateForm} />
            ) : isFormTreasure ? (
              <FormTreasureControls form={form} updateForm={updateForm} />
            ) : isSolfegeTarget ? (
              <SolfegeControls form={form} updateForm={updateForm} />
            ) : isPitchLadder ? (
              <PitchControls form={form} updateForm={updateForm} />
            ) : isBeatGuardian ? (
              <Box mt="4">
                <DownbeatChargePicker form={form} updateForm={updateForm} />
              </Box>
            ) : null}

            {isBeatGuardian ? <BeatGuardianSupportPanel form={form} /> : null}

            {isPitchGame || isTimbreDetective || isFormTreasure || isCompositionPuzzle ? (
              <Grid columns={{ initial: "1", sm: "2" }} gap="4" mt="4">
                <SliderControl
                  icon={<Activity size={18} />}
                  label="回合"
                  value={form.round_count}
                  min={1}
                  max={12}
                  suffix="轮"
                  onChange={(value) => updateForm({ round_count: value })}
                />
                <SliderControl
                  icon={<Sparkles size={18} />}
                  label="通关"
                  value={Math.round(form.pass_score * 100)}
                  min={50}
                  max={100}
                  suffix="%"
                  onChange={(value) => updateForm({ pass_score: value / 100 })}
                />
              </Grid>
            ) : (
              <Grid columns={{ initial: "1", sm: "3" }} gap="4" mt="4">
                <SliderControl
                  icon={<Gauge size={18} />}
                  label="速度"
                  value={form.bpm}
                  min={60}
                  max={132}
                  suffix="BPM"
                  onChange={(value) => updateForm({ bpm: value })}
                />
                <SliderControl
                  icon={<Activity size={18} />}
                  label="回合"
                  value={form.round_count}
                  min={1}
                  max={12}
                  suffix="轮"
                  onChange={(value) => updateForm({ round_count: value })}
                />
                <SliderControl
                  icon={<Sparkles size={18} />}
                  label="容错"
                  value={form.timing_tolerance_ms}
                  min={80}
                  max={320}
                  suffix="ms"
                  onChange={(value) => updateForm({ timing_tolerance_ms: value })}
                />
              </Grid>
            )}

            {isTimbreDetective ? (
              <Grid columns={{ initial: "1", sm: "2" }} gap="4" mt="4">
                <SliderControl
                  icon={<FileSearch size={18} />}
                  label="嫌疑选项"
                  value={form.choices_per_round}
                  min={2}
                  max={6}
                  suffix="个"
                  onChange={(value) => updateForm({ choices_per_round: value })}
                />
                <SliderControl
                  icon={<Sparkles size={18} />}
                  label="证据"
                  value={form.evidence_required}
                  min={1}
                  max={3}
                  suffix="条"
                  onChange={(value) => updateForm({ evidence_required: value })}
                />
              </Grid>
            ) : isCompositionPuzzle ? (
              <Grid columns={{ initial: "1", sm: "2" }} gap="4" mt="4">
                <SliderControl
                  icon={<Music2 size={18} />}
                  label="短句长度"
                  value={form.phrase_length_bars}
                  min={1}
                  max={4}
                  suffix="小节"
                  onChange={(value) => updateForm({ phrase_length_bars: value, bars_per_round: value })}
                />
                <SliderControl
                  icon={<Hand size={18} />}
                  label="每小节格"
                  value={form.slots_per_bar}
                  min={2}
                  max={8}
                  suffix="格"
                  onChange={(value) => updateForm({ slots_per_bar: value })}
                />
              </Grid>
            ) : isPitchGame ? (
              <Grid columns={{ initial: "1", sm: "2" }} gap="4" mt="4">
                <SliderControl
                  icon={<Music2 size={18} />}
                  label="音数"
                  value={form.notes_per_round}
                  min={1}
                  max={isSolfegeTarget ? 4 : 5}
                  suffix="个"
                  onChange={(value) => updateForm({ notes_per_round: value })}
                />
                <SliderControl
                  icon={<Hand size={18} />}
                  label="重试"
                  value={form.retry_limit}
                  min={0}
                  max={6}
                  suffix="次"
                  onChange={(value) => updateForm({ retry_limit: value })}
                />
              </Grid>
            ) : isBeatGuardian ? (
              <Grid columns={{ initial: "1", sm: "2" }} gap="4" mt="4">
                <SliderControl
                  icon={<ShieldCheck size={18} />}
                  label="连续目标"
                  value={form.combo_required}
                  min={1}
                  max={12}
                  suffix="次"
                  onChange={(value) => updateForm({ combo_required: value })}
                />
                <SliderControl
                  icon={<Hand size={18} />}
                  label="错误上限"
                  value={form.mistake_limit}
                  min={0}
                  max={8}
                  suffix="次"
                  onChange={(value) => updateForm({ mistake_limit: value })}
                />
              </Grid>
            ) : null}

            <Flex gap="5" wrap="wrap" mt="5">
              {isTimbreDetective ? (
                <>
                  <ToggleRow
                    label="波形线索"
                    checked={form.show_wave_hint}
                    onCheckedChange={(value) => updateForm({ show_wave_hint: value })}
                  />
                  <ToggleRow
                    label="家族提示"
                    checked={form.show_family_hint}
                    onCheckedChange={(value) => updateForm({ show_family_hint: value })}
                  />
                  <ToggleRow
                    label="辅助提示"
                    checked={form.ai_clue_enabled}
                    onCheckedChange={(value) => updateForm({ ai_clue_enabled: value })}
                  />
                </>
              ) : isCompositionPuzzle ? (
                <>
                  <ToggleRow
                    label="教师确认"
                    checked={form.teacher_confirm_required}
                    onCheckedChange={(value) => updateForm({ teacher_confirm_required: value })}
                  />
                  <ToggleRow
                    label="显示拍点"
                    checked={form.show_beat_track}
                    onCheckedChange={(value) => updateForm({ show_beat_track: value })}
                  />
                  <ToggleRow
                    label="唱名提示"
                    checked={form.show_solfege_hint}
                    onCheckedChange={(value) => updateForm({ show_solfege_hint: value })}
                  />
                </>
              ) : isSolfegeTarget ? (
                <>
                  <ToggleRow
                    label="唱名提示"
                    checked={form.show_solfege_hint}
                    onCheckedChange={(value) => updateForm({ show_solfege_hint: value })}
                  />
                  <ToggleRow
                    label="唱回确认"
                    checked={form.sing_back_required ?? form.require_sing_back}
                    onCheckedChange={(value) => updateForm({ require_sing_back: value, sing_back_required: value })}
                  />
                  <ToggleRow
                    label="教师确认"
                    checked={form.teacher_confirm_required}
                    onCheckedChange={(value) => updateForm({ teacher_confirm_required: value })}
                  />
                </>
              ) : isPitchLadder ? (
                <>
                  <ToggleRow
                    label="唱名提示"
                    checked={form.show_solfege_hint}
                    onCheckedChange={(value) => updateForm({ show_solfege_hint: value })}
                  />
                  <ToggleRow
                    label="方向提示"
                    checked={form.show_direction_hint}
                    onCheckedChange={(value) => updateForm({ show_direction_hint: value })}
                  />
                  <ToggleRow
                    label="谱面提示"
                    checked={form.show_staff_hint}
                    onCheckedChange={(value) => updateForm({ show_staff_hint: value })}
                  />
                </>
              ) : isBeatGuardian ? (
                <>
                  <ToggleRow
                    label="节拍轨道"
                    checked={form.show_beat_track}
                    onCheckedChange={(value) => updateForm({ show_beat_track: value })}
                  />
                  <ToggleRow
                    label="强拍提示"
                    checked={form.show_strong_beat_hint}
                    onCheckedChange={(value) => updateForm({ show_strong_beat_hint: value })}
                  />
                  <ToggleRow
                    label="弱拍提示"
                    checked={form.show_weak_beat_hint}
                    onCheckedChange={(value) => updateForm({ show_weak_beat_hint: value })}
                  />
                  <ToggleRow
                    label="同步亮点"
                    checked={form.visual_beat_hint}
                    onCheckedChange={(value) => updateForm({ visual_beat_hint: value })}
                  />
                </>
              ) : (
                <>
                  <ToggleRow
                    label="允许重听"
                    checked={form.allow_relisten}
                    onCheckedChange={(value) => updateForm({ allow_relisten: value })}
                  />
                  <ToggleRow
                    label="显示拍点提示"
                    checked={form.visual_beat_hint}
                    onCheckedChange={(value) => updateForm({ visual_beat_hint: value })}
                  />
                </>
              )}
            </Flex>

            <Box mt="5">
              <LabeledControl label="教师提示">
                <TextArea
                  value={form.teacher_prompt}
                  onChange={(event) => updateForm({ teacher_prompt: event.target.value })}
                  rows={3}
                />
              </LabeledControl>
            </Box>
          </Box>
        ) : null}
      </Box>
    </>
  );
}

function TemplateVisualBase({
  form,
  compact = false
}: {
  form: TemplateForm;
  compact?: boolean;
}) {
  return (
    <Box className={compact ? "skin-library visual-base compact" : "skin-library visual-base"}>
      <Flex align="center" justify="between" gap="3" mb="3">
        <Box>
          <Text className="stage-kicker">默认视觉</Text>
          <Heading size={compact ? "3" : "4"}>{templateLabels[form.template_id]}</Heading>
        </Box>
        <Badge color="teal" variant="soft">
          内部固定
        </Badge>
      </Flex>
      <div className="visual-base-card">
        <span className={`skin-swatch ${form.skin_id}`} aria-hidden="true" />
        <div>
          <strong>{skinLabels[form.skin_id]}</strong>
          <Text as="p" size="2" color="gray" mt="1">
            当前模板使用这个默认骨架来保证玩法、布局和判定稳定。
          </Text>
        </div>
      </div>
      <Text as="p" className="skin-helper">
        教师无需手动选择皮肤。生成图片会优先根据教案语义、歌曲氛围和课堂场景自动决定视觉环境。
      </Text>
    </Box>
  );
}

function DownbeatChargePicker({
  form,
  updateForm
}: {
  form: TemplateForm;
  updateForm: (patch: Partial<TemplateForm>) => void;
}) {
  const beatsPerBar = Number(form.meter.split("/")[0]);

  return (
    <Box>
      <Text size="2" weight="bold">
        充能拍位
      </Text>
      <Text as="p" size="2" color="gray" mt="1">
        护盾只在每小节第 1 拍收缩到最小；弱拍用于蓄势，不作为目标拍。
      </Text>
      <Flex gap="2" mt="2" wrap="wrap">
        {Array.from({ length: beatsPerBar }).map((_, index) => {
          const beat = index + 1;
          const selected = beat === 1;
          return (
            <Button
              key={beat}
              type="button"
              variant={selected ? "solid" : "soft"}
              color={selected ? "teal" : "gray"}
              disabled={!selected}
              onClick={() => updateForm({ target_beats: [1] })}
            >
              {selected ? "第 1 拍充能" : `第 ${beat} 拍蓄势`}
            </Button>
          );
        })}
      </Flex>
    </Box>
  );
}

function FormTreasureControls({
  form,
  updateForm,
  compact = false
}: {
  form: TemplateForm;
  updateForm: (patch: Partial<TemplateForm>) => void;
  compact?: boolean;
}) {
  return (
    <Box mt={compact ? "4" : "4"} className="form-treasure-controls">
      <Grid columns={{ initial: "1", sm: "3" }} gap="4">
        <LabeledControl label="曲式类型">
          <Select.Root
            value={form.form_type}
            onValueChange={(value) =>
              updateForm({
                form_type: value as TemplateForm["form_type"],
                mode: value === "回旋" ? "rondo_treasure" : value === "重复对比" ? "repeat_contrast" : "aba_treasure"
              })
            }
          >
            <Select.Trigger />
            <Select.Content>
              <Select.Item value="ABA">ABA</Select.Item>
              <Select.Item value="回旋">回旋</Select.Item>
              <Select.Item value="重复对比">重复对比</Select.Item>
            </Select.Content>
          </Select.Root>
        </LabeledControl>
        <LabeledControl label="段落长度">
          <Select.Root value={String(form.section_length_bars)} onValueChange={(value) => updateForm({ section_length_bars: Number(value), bars_per_round: Number(value) })}>
            <Select.Trigger />
            <Select.Content>
              {[4, 8, 12, 16].map((bars) => (
                <Select.Item key={bars} value={String(bars)}>{bars} 小节</Select.Item>
              ))}
            </Select.Content>
          </Select.Root>
        </LabeledControl>
        <LabeledControl label="提示模式">
          <Select.Root value={form.hint_mode} onValueChange={(value) => updateForm({ hint_mode: value as TemplateForm["hint_mode"] })}>
            <Select.Trigger />
            <Select.Content>
              <Select.Item value="guided">引导</Select.Item>
              <Select.Item value="partial">半提示</Select.Item>
              <Select.Item value="challenge">挑战</Select.Item>
            </Select.Content>
          </Select.Root>
        </LabeledControl>
      </Grid>
      <Text as="p" className="skin-helper" mt="3">
        学生端会先听段落，再排列结构卡。这里配置的是课堂可理解参数，不暴露代码字段。
      </Text>
    </Box>
  );
}

function CompositionPuzzleControls({
  form,
  updateForm,
  compact = false
}: {
  form: TemplateForm;
  updateForm: (patch: Partial<TemplateForm>) => void;
  compact?: boolean;
}) {
  const rhythmOptions = [
    ["quarter", "四分"],
    ["eighth_pair", "二八"],
    ["sixteenth_four", "四个十六"],
    ["eighth_sixteenth_sixteenth", "前八后十六"],
    ["sixteenth_sixteenth_eighth", "前十六后八"],
    ["rest", "休止"]
  ] as const;
  const melodyOptions = ["C", "D", "E", "F", "G", "A", "B", "C'"];
  const toggleList = (key: "rhythm_cards" | "melody_cards", value: string, minimum: number) => {
    const current = new Set(form[key]);
    if (current.has(value)) {
      current.delete(value);
    } else {
      current.add(value);
    }
    const ordered = (key === "rhythm_cards" ? rhythmOptions.map(([id]) => id) : melodyOptions).filter((item) => current.has(item));
    if (ordered.length >= minimum) updateForm({ [key]: ordered } as Partial<TemplateForm>);
  };

  return (
    <Box mt={compact ? "4" : "4"} className="composition-puzzle-controls">
      <Grid columns={{ initial: "1", sm: "3" }} gap="4">
        <LabeledControl label="创编侧重点">
          <Select.Root
            value={form.mode}
            onValueChange={(value) => {
              const mode = value as CompositionPuzzleMode;
              updateForm({ mode });
            }}
          >
            <Select.Trigger />
            <Select.Content>
              <Select.Item value="rhythm_puzzle_composition">节奏拼图创编</Select.Item>
              <Select.Item value="melody_puzzle_creation">旋律拼图创作</Select.Item>
              <Select.Item value="melody_rhythm_puzzle">旋律节奏拼图</Select.Item>
            </Select.Content>
          </Select.Root>
        </LabeledControl>
        <LabeledControl label="作品长度">
          <Select.Root
            value={String(form.composition_total_bars || form.phrase_length_bars)}
            onValueChange={(value) => {
              const totalBars = Number(value);
              const segmentBars = Math.min(4, totalBars);
              updateForm({
                composition_total_bars: totalBars,
                composition_segment_bars: segmentBars,
                composition_segments: Math.ceil(totalBars / segmentBars),
                phrase_length_bars: segmentBars,
                bars_per_round: segmentBars
              });
            }}
          >
            <Select.Trigger />
            <Select.Content>
              {[2, 4, 8, 12, 16, 32].map((bars) => (
                <Select.Item key={bars} value={String(bars)}>{bars} 小节</Select.Item>
              ))}
            </Select.Content>
          </Select.Root>
        </LabeledControl>
        <LabeledControl label="约束强度">
          <Select.Root value={form.constraint_profile} onValueChange={(value) => updateForm({ constraint_profile: value as TemplateForm["constraint_profile"] })}>
            <Select.Trigger />
            <Select.Content>
              <Select.Item value="guided">引导</Select.Item>
              <Select.Item value="balanced">标准</Select.Item>
              <Select.Item value="challenge">挑战</Select.Item>
            </Select.Content>
          </Select.Root>
        </LabeledControl>
      </Grid>

      <Grid columns={{ initial: "1", sm: "2" }} gap="4" mt="4">
        <Box>
          <Text size="2" weight="bold">节奏素材卡</Text>
          <Flex gap="2" mt="2" wrap="wrap">
            {rhythmOptions.map(([id, label]) => (
              <Button
                key={id}
                type="button"
                size="2"
                variant={form.rhythm_cards.includes(id) ? "solid" : "soft"}
                color={form.rhythm_cards.includes(id) ? "amber" : "gray"}
                onClick={() => toggleList("rhythm_cards", id, 2)}
              >
                {label}
              </Button>
            ))}
          </Flex>
        </Box>
        <Box>
          <Text size="2" weight="bold">旋律素材卡</Text>
          <Flex gap="2" mt="2" wrap="wrap">
            {melodyOptions.map((note) => (
              <Button
                key={note}
                type="button"
                size="2"
                variant={form.melody_cards.includes(note) ? "solid" : "soft"}
                color={form.melody_cards.includes(note) ? "teal" : "gray"}
                onClick={() => toggleList("melody_cards", note, 2)}
              >
                {note}
              </Button>
            ))}
          </Flex>
        </Box>
      </Grid>
      <Text as="p" className="skin-helper" mt="3">
        学生端用 Phaser 拖拽卡片到作品轨道，试听时依次高亮，再按约束清单和教师确认通关。
      </Text>
    </Box>
  );
}

function SolfegeControls({
  form,
  updateForm
}: {
  form: TemplateForm;
  updateForm: (patch: Partial<TemplateForm>) => void;
}) {
  const allSolfege = ["do", "re", "mi", "fa", "sol", "la", "ti", "do_high"];
  const toggleSolfege = (note: string) => {
    const current = new Set(form.target_solfege);
    if (current.has(note)) {
      current.delete(note);
    } else {
      current.add(note);
    }
    const next = allSolfege.filter((item) => current.has(item));
    updateForm({ target_solfege: next.length >= 2 ? next : form.target_solfege });
  };

  return (
    <Box mt="4">
      <Grid columns={{ initial: "1", sm: "2" }} gap="4">
        <LabeledControl label="唱名体系">
          <Select.Root value={form.solfege_system} onValueChange={(value) => updateForm({ solfege_system: value })}>
            <Select.Trigger />
            <Select.Content>
              <Select.Item value="movable_do">首调唱名</Select.Item>
              <Select.Item value="fixed_do">固定唱名</Select.Item>
            </Select.Content>
          </Select.Root>
        </LabeledControl>
        <LabeledControl label="靶场任务提示">
          <Text as="p" color="gray" size="2">
            击中靶心只是中间动作，学生还需要把目标音唱回出来。
          </Text>
        </LabeledControl>
      </Grid>

      <Box mt="4">
        <Text size="2" weight="bold">
          唱名靶
        </Text>
        <Flex gap="2" mt="2" wrap="wrap">
          {allSolfege.map((note) => {
            const selected = form.target_solfege.includes(note);
            return (
              <Button
                key={note}
                type="button"
                variant={selected ? "solid" : "soft"}
                color={selected ? "teal" : "gray"}
                onClick={() => toggleSolfege(note)}
              >
                {note === "do_high" ? "do'" : note}
              </Button>
            );
          })}
        </Flex>
      </Box>
    </Box>
  );
}

function TimbreControls({
  form,
  updateForm
}: {
  form: TemplateForm;
  updateForm: (patch: Partial<TemplateForm>) => void;
}) {
  const instruments = ["笛子", "长笛", "二胡", "小提琴", "古筝", "钢琴", "小鼓", "木鱼", "人声"];
  const traits = ["明亮", "柔和", "短促", "持续", "气息感", "弦鸣", "敲击感", "木质感", "金属感"];
  const toggleItem = (key: "instrument_pool" | "timbre_traits", item: string, minimum: number) => {
    const current = new Set(form[key]);
    if (current.has(item)) {
      current.delete(item);
    } else {
      current.add(item);
    }
    const source = key === "instrument_pool" ? instruments : traits;
    const next = source.filter((value) => current.has(value));
    updateForm({ [key]: next.length >= minimum ? next : form[key] } as Partial<TemplateForm>);
  };

  return (
    <Box mt="4">
      <Grid columns={{ initial: "1", sm: "2" }} gap="4">
        <LabeledControl label="声音素材集">
          <Select.Root value={form.sound_set} onValueChange={(value) => updateForm({ sound_set: value })}>
            <Select.Trigger />
            <Select.Content>
              <Select.Item value="classroom_instruments">课堂常见乐器</Select.Item>
              <Select.Item value="chinese_instruments">民族乐器</Select.Item>
              <Select.Item value="orchestra">管弦乐器</Select.Item>
              <Select.Item value="found_sounds">生活声音</Select.Item>
            </Select.Content>
          </Select.Root>
        </LabeledControl>
        <LabeledControl label="辅助提示说明">
          <Text as="p" color="gray" size="2">
            默认关闭。开启后只给教师增加判断线索，不替学生完成听辨。
          </Text>
        </LabeledControl>
      </Grid>

      <Box mt="4">
        <Text size="2" weight="bold">
          嫌疑乐器
        </Text>
        <Flex gap="2" mt="2" wrap="wrap">
          {instruments.map((instrument) => {
            const selected = form.instrument_pool.includes(instrument);
            return (
              <Button
                key={instrument}
                type="button"
                variant={selected ? "solid" : "soft"}
                color={selected ? "teal" : "gray"}
                onClick={() => toggleItem("instrument_pool", instrument, 2)}
              >
                {instrument}
              </Button>
            );
          })}
        </Flex>
      </Box>

      <Box mt="4">
        <Text size="2" weight="bold">
          音色证据词
        </Text>
        <Flex gap="2" mt="2" wrap="wrap">
          {traits.map((trait) => {
            const selected = form.timbre_traits.includes(trait);
            return (
              <Button
                key={trait}
                type="button"
                variant={selected ? "solid" : "soft"}
                color={selected ? "teal" : "gray"}
                onClick={() => toggleItem("timbre_traits", trait, 3)}
              >
                {trait}
              </Button>
            );
          })}
        </Flex>
      </Box>
    </Box>
  );
}

function PitchControls({
  form,
  updateForm,
  compact = false
}: {
  form: TemplateForm;
  updateForm: (patch: Partial<TemplateForm>) => void;
  compact?: boolean;
}) {
  const allPitches = ["do", "re", "mi", "fa", "sol", "la", "ti", "do_high"];
  const togglePitch = (pitch: string) => {
    const current = new Set(form.pitch_range);
    if (current.has(pitch)) {
      current.delete(pitch);
    } else {
      current.add(pitch);
    }
    const next = allPitches.filter((item) => current.has(item));
    updateForm({ pitch_range: next.length >= 2 ? next : form.pitch_range });
  };

  return (
    <Box mt="4">
      <Grid columns={{ initial: "1", sm: "2" }} gap="4">
        <LabeledControl label={compact ? "音阶类型" : "调式范围"}>
          <Select.Root value={form.scale_type} onValueChange={(value) => updateForm({ scale_type: value })}>
            <Select.Trigger />
            <Select.Content>
              <Select.Item value="major_pentatonic">大调五声音阶</Select.Item>
              <Select.Item value="major">自然大调</Select.Item>
              <Select.Item value="minor_pentatonic">小调五声音阶</Select.Item>
            </Select.Content>
          </Select.Root>
        </LabeledControl>
        {compact ? (
          <LabeledControl label="每轮音数">
            <Select.Root value={String(form.notes_per_round)} onValueChange={(value) => updateForm({ notes_per_round: Number(value) })}>
              <Select.Trigger />
              <Select.Content>
                {[2, 3, 4, 5].map((count) => (
                  <Select.Item key={count} value={String(count)}>
                    {count} 个音
                  </Select.Item>
                ))}
              </Select.Content>
            </Select.Root>
          </LabeledControl>
        ) : null}
        <LabeledControl label="音高任务提示">
          <Text as="p" color="gray" size="2">
            当前默认视觉：{skinLabels[form.skin_id]}。确认生成后，新学生游戏会按这些音级和模式重建关卡，图片氛围由教案语义自动生成。
          </Text>
        </LabeledControl>
      </Grid>

      <Box mt="4">
        <Text size="2" weight="bold">
          台阶音级
        </Text>
        <Flex gap="2" mt="2" wrap="wrap">
          {allPitches.map((pitch) => {
            const selected = form.pitch_range.includes(pitch);
            return (
              <Button
                key={pitch}
                type="button"
                variant={selected ? "solid" : "soft"}
                color={selected ? "teal" : "gray"}
                onClick={() => togglePitch(pitch)}
              >
                {pitch === "do_high" ? "do'" : pitch}
              </Button>
            );
          })}
        </Flex>
      </Box>
    </Box>
  );
}

function RhythmEchoPreview({ form, instance }: { form: TemplateForm; instance: GameInstance | null }) {
  const mode = form.mode as RhythmEchoMode;
  return (
    <Card className="stage-card">
      <Flex justify="between" align="start" gap="4">
        <Box>
          <Text className="stage-kicker">当前模式</Text>
          <Heading size="6">{rhythmModeLabels[mode] || "点按复刻"}</Heading>
          <Text as="p" color="gray" mt="2">
            听完示范后复刻节奏，系统根据拍点稳定度和节奏完整度反馈。
          </Text>
        </Box>
        <Badge color="amber" variant="solid">
          {form.difficulty}
        </Badge>
      </Flex>
      <div className="beat-lane" aria-hidden="true">
        {Array.from({ length: 8 }).map((_, index) => (
          <span key={index} className={index % 2 === 0 ? "beat strong" : "beat"} />
        ))}
      </div>
      <Grid columns="3" gap="3" mt="4">
        <Metric label="速度" value={`${form.bpm} BPM`} />
        <Metric label="拍号" value={form.meter} />
        <Metric label="状态" value={instance ? "已生成" : "待生成"} />
      </Grid>
    </Card>
  );
}

function FormTreasureStage({
  config,
  instance
}: {
  config: TemplateForm & Record<string, unknown>;
  instance: GameInstance | null;
}) {
  const mode = config.mode as FormTreasureMode;
  const pattern =
    Array.isArray(config.answer_pattern)
      ? config.answer_pattern.map(String)
      : config.form_type === "回旋"
        ? ["A", "B", "A", "C", "A"]
        : config.form_type === "重复对比"
          ? ["A", "A", "B", "A"]
          : ["A", "B", "A"];
  return (
    <Card className="stage-card form-treasure-preview-card">
      <Flex justify="between" align="start" gap="4">
        <Box>
          <Text className="stage-kicker">当前模式</Text>
          <Heading size="6">{formModeLabels[mode] || "ABA 寻宝"}</Heading>
          <Text as="p" color="gray" mt="2">
            学生听段落、排列结构卡、验证曲式路线，最后说出重复与对比依据。
          </Text>
        </Box>
        <Badge color="amber" variant="solid">
          {config.difficulty}
        </Badge>
      </Flex>
      <div className="form-preview-map" aria-hidden="true">
        {pattern.map((label, index) => (
          <span key={`${label}_${index}`} className={`form-preview-node node-${label.toLowerCase()}`}>
            {label}
          </span>
        ))}
      </div>
      <Grid columns="3" gap="3" mt="4">
        <Metric label="曲式" value={config.form_type} />
        <Metric label="段落" value={`${config.section_length_bars} 小节`} />
        <Metric label="状态" value={instance ? "已生成" : "待生成"} />
      </Grid>
    </Card>
  );
}

function CompositionPuzzleStage({
  config,
  instance
}: {
  config: TemplateForm & Record<string, unknown>;
  instance: GameInstance | null;
}) {
  const mode = config.mode as CompositionPuzzleMode;
  const totalBars = Number(config.composition_total_bars || config.phrase_length_bars || 2);
  const segmentBars = Number(config.composition_segment_bars || Math.min(4, totalBars));
  const segments = Number(config.composition_segments || Math.ceil(totalBars / Math.max(1, segmentBars)));
  const slots = Math.max(2, segmentBars * Number(config.slots_per_bar || 4));
  const rhythmCards = Array.isArray(config.rhythm_cards) ? config.rhythm_cards.map(String).slice(0, 5) : [];
  const melodyCards = Array.isArray(config.melody_cards) ? config.melody_cards.map(String).slice(0, 5) : [];
  return (
    <Card className="stage-card composition-preview-card">
      <Flex justify="between" align="start" gap="4">
        <Box>
          <Text className="stage-kicker">当前模式</Text>
          <Heading size="6">{compositionModeLabels[mode] || "节奏拼图创编"}</Heading>
          <Text as="p" color="gray" mt="2">
            学生拖拽素材卡到作品轨道，试听高亮后检查约束，开放创作由教师确认。
          </Text>
        </Box>
        <Badge color="amber" variant="solid">
          {config.difficulty}
        </Badge>
      </Flex>
      <div className="composition-preview-track" aria-hidden="true">
        {Array.from({ length: Math.min(slots, 16) }).map((_, index) => (
          <span key={index} className={index % Number(config.slots_per_bar || 4) === 0 ? "slot bar-start" : "slot"} />
        ))}
      </div>
      <Flex gap="2" wrap="wrap" mt="4">
        {rhythmCards.map((card) => (
          <Badge key={card} color="amber" variant="soft">{card}</Badge>
        ))}
        {melodyCards.map((card) => (
          <Badge key={card} color="teal" variant="soft">{card === "do_high" ? "do'" : card}</Badge>
        ))}
      </Flex>
      <Grid columns="3" gap="3" mt="4">
        <Metric label="作品" value={`${totalBars} 小节`} />
        <Metric label="分段" value={`${segments} 段`} />
        <Metric label="约束" value={String(config.constraint_profile || "guided")} />
      </Grid>
    </Card>
  );
}

type PitchRound = {
  id: string;
  sequence: string[];
  labels: string[];
  midi_offsets: number[];
  answer: string | string[];
};

type SolfegeRound = PitchRound & {
  sing_back_required?: boolean;
  teacher_confirm_required?: boolean;
};

type TimbreAudioProfile = {
  wave: OscillatorType;
  frequency: number;
  attack: number;
  release: number;
  brightness: number;
};

type TimbreRound = {
  id: string;
  mode: string;
  prompt: string;
  target: string;
  family: string;
  traits: string[];
  candidates: string[];
  evidence_options: string[];
  evidence_answer: string[];
  answer: string | string[];
  compare_with?: string | null;
  audio_profile: TimbreAudioProfile;
  compare_audio_profile?: TimbreAudioProfile | null;
};

const pitchLabelMap: Record<string, string> = {
  do: "do",
  re: "re",
  mi: "mi",
  fa: "fa",
  sol: "sol",
  la: "la",
  ti: "ti",
  do_high: "do'"
};

const fallbackTimbreProfiles: Record<string, { family: string; traits: string[]; audio_profile: TimbreAudioProfile }> = {
  笛子: { family: "管乐", traits: ["明亮", "气息感", "持续"], audio_profile: { wave: "sine", frequency: 740, attack: 0.04, release: 0.34, brightness: 0.82 } },
  长笛: { family: "管乐", traits: ["明亮", "柔和", "气息感"], audio_profile: { wave: "sine", frequency: 660, attack: 0.05, release: 0.42, brightness: 0.72 } },
  二胡: { family: "弦乐", traits: ["柔和", "持续", "弦鸣"], audio_profile: { wave: "sawtooth", frequency: 392, attack: 0.08, release: 0.5, brightness: 0.5 } },
  小提琴: { family: "弦乐", traits: ["明亮", "持续", "弦鸣"], audio_profile: { wave: "sawtooth", frequency: 520, attack: 0.06, release: 0.46, brightness: 0.68 } },
  古筝: { family: "弹拨乐", traits: ["明亮", "短促", "弦鸣"], audio_profile: { wave: "triangle", frequency: 494, attack: 0.02, release: 0.7, brightness: 0.78 } },
  钢琴: { family: "键盘乐", traits: ["明亮", "短促", "敲击感"], audio_profile: { wave: "triangle", frequency: 440, attack: 0.01, release: 0.62, brightness: 0.64 } },
  小鼓: { family: "打击乐", traits: ["短促", "敲击感", "明亮"], audio_profile: { wave: "square", frequency: 180, attack: 0.005, release: 0.18, brightness: 0.7 } },
  木鱼: { family: "打击乐", traits: ["短促", "敲击感", "木质感"], audio_profile: { wave: "square", frequency: 520, attack: 0.004, release: 0.12, brightness: 0.58 } },
  人声: { family: "人声", traits: ["柔和", "持续", "气息感"], audio_profile: { wave: "sine", frequency: 330, attack: 0.05, release: 0.45, brightness: 0.45 } }
};

function TimbreDetectiveStage({
  config,
  instance
}: {
  config: TemplateForm & Record<string, unknown>;
  instance: GameInstance | null;
}) {
  const rounds = useMemo(() => normalizeTimbreRounds(config), [config]);
  const [roundIndex, setRoundIndex] = useState(0);
  const [correct, setCorrect] = useState(0);
  const [attempts, setAttempts] = useState(0);
  const [relistens, setRelistens] = useState(0);
  const [selectedSource, setSelectedSource] = useState("");
  const [selectedEvidence, setSelectedEvidence] = useState<string[]>([]);
  const [feedback, setFeedback] = useState("先播放声音证物，再选择嫌疑对象和音色证据。");
  const current = rounds[Math.min(roundIndex, rounds.length - 1)];
  const mode = config.mode as TimbreDetectiveMode;
  const score = attempts ? correct / attempts : 0;

  useEffect(() => {
    setRoundIndex(0);
    setCorrect(0);
    setAttempts(0);
    setRelistens(0);
    setSelectedSource("");
    setSelectedEvidence([]);
    setFeedback("先播放声音证物，再选择嫌疑对象和音色证据。");
  }, [config.template_id, config.mode, config.difficulty, config.round_count, config.instrument_pool, config.timbre_traits]);

  const playProfile = useCallback((profile: TimbreAudioProfile, label: string, delay = 0) => {
    window.setTimeout(() => {
      void playHybridTimbreProfile(profile, { instrument: label, label, duration: Math.max(0.5, profile.attack + profile.release + 0.34) });
    }, delay * 1000);
  }, []);

  const playEvidence = useCallback(() => {
    if (!current) {
      return;
    }
    playProfile(current.audio_profile, current.target || current.family || "", 0);
    if (mode === "compare_twins" && current.compare_audio_profile) {
      playProfile(current.compare_audio_profile, current.compare_with || "", 0.82);
    }
    setRelistens((value) => value + 1);
    setFeedback(mode === "compare_twins" ? "第一声和第二声有什么不同？找证据，不急着猜。" : "听完后找嫌疑对象，再选择能说明判断的证据。");
  }, [current, mode, playProfile]);

  const toggleEvidence = (trait: string) => {
    setSelectedEvidence((value) => {
      if (value.includes(trait)) {
        return value.filter((item) => item !== trait);
      }
      return [...value, trait].slice(0, Math.max(1, config.evidence_required));
    });
  };

  const nextRound = useCallback(() => {
    setSelectedSource("");
    setSelectedEvidence([]);
    window.setTimeout(() => {
      setRoundIndex((value) => (value + 1) % rounds.length);
    }, 900);
  }, [rounds.length]);

  const submitReasoning = () => {
    if (!selectedSource) {
      setFeedback("还没有选择嫌疑对象。先听，再决定声音来自哪里。");
      return;
    }
    if (selectedEvidence.length < Math.max(1, config.evidence_required)) {
      setFeedback("还需要选择音色证据。侦探不能只猜，要说出理由。");
      return;
    }
    setAttempts((value) => value + 1);
    const sourceCorrect = selectedSource === current.answer;
    const evidenceCorrect = current.evidence_answer.every((trait) => selectedEvidence.includes(trait));
    if (sourceCorrect && evidenceCorrect) {
      setCorrect((value) => value + 1);
      setFeedback(`破案成功：${selectedSource} 的判断有证据支撑，可以请学生口头描述这个音色。`);
      nextRound();
    } else if (sourceCorrect) {
      setFeedback("嫌疑对象找对了，但证据还不够准确。再听起音、延音和材质感。");
    } else {
      setFeedback("嫌疑对象还不对。复听时注意它更像管乐、弦乐还是打击乐。");
    }
  };

  return (
    <Card className={`timbre-stage ${config.skin_id || "sound_casebook"}`}>
      <Flex justify="between" align="start" gap="4" wrap="wrap">
        <Box>
          <Text className="stage-kicker">音色案件</Text>
          <Heading size="6">{timbreModeLabels[mode] || "乐器线索"}</Heading>
          <Text as="p" color="gray" mt="2">
            {skinLabels[config.skin_id as GameSkin] || "声音案卷"} · 第 {roundIndex + 1}/{rounds.length} 轮
          </Text>
        </Box>
        <Badge color={instance ? "teal" : "amber"} variant="solid">
          {instance ? "已生成" : "待生成"}
        </Badge>
      </Flex>

      <div className="timbre-case-board">
        <div className="timbre-evidence-player">
          <Ear size={42} />
          <Text size="2" weight="bold">
            声音证物
          </Text>
          <Text size="1" color="gray">
            {current.prompt}
          </Text>
          {config.show_wave_hint ? <TimbreWave profile={current.audio_profile} /> : null}
          {config.ai_clue_enabled ? (
            <Badge color="amber" variant="soft">
              辅助提示仅供教师参考
            </Badge>
          ) : null}
        </div>

        <div className="timbre-suspects">
          <Text size="2" weight="bold">
            {mode === "family_sorting" ? "家族档案" : "嫌疑对象"}
          </Text>
          <Grid columns={{ initial: "2", sm: "2" }} gap="2" mt="2">
            {current.candidates.map((candidate) => (
              <button
                key={candidate}
                type="button"
                className={`suspect-card ${selectedSource === candidate ? "selected" : ""}`}
                onClick={() => setSelectedSource(candidate)}
              >
                <span>{candidate}</span>
                {config.show_family_hint && fallbackTimbreProfiles[candidate] ? (
                  <small>{fallbackTimbreProfiles[candidate].family}</small>
                ) : null}
              </button>
            ))}
          </Grid>
        </div>
      </div>

      <Flex gap="3" mt="4" wrap="wrap">
        <Button size="3" onClick={playEvidence}>
          <Play size={18} />
          播放声音证物
        </Button>
        <Button size="3" color="teal" onClick={submitReasoning}>
          <FileSearch size={18} />
          提交推理
        </Button>
      </Flex>

      <Box mt="4">
        <Text size="2" weight="bold">
          音色证据板
        </Text>
        <Flex gap="2" mt="2" wrap="wrap">
          {current.evidence_options.map((trait) => {
            const selected = selectedEvidence.includes(trait);
            return (
              <Button
                key={trait}
                type="button"
                variant={selected ? "solid" : "soft"}
                color={selected ? "amber" : "gray"}
                onClick={() => toggleEvidence(trait)}
              >
                {trait}
              </Button>
            );
          })}
        </Flex>
      </Box>

      <Text as="p" className="guardian-feedback timbre-feedback">
        {feedback}
      </Text>

      <Grid columns={{ initial: "2", sm: "4" }} gap="3" mt="4">
        <Metric label="破案" value={`${correct}/${attempts || 0}`} />
        <Metric label="重听" value={`${Math.max(0, relistens - 1)} 次`} />
        <Metric label="证据" value={`${selectedEvidence.length}/${config.evidence_required}`} />
        <Metric label="得分" value={`${Math.round(score * 100)}%`} />
      </Grid>
    </Card>
  );
}

function TimbreWave({ profile }: { profile: TimbreAudioProfile }) {
  return (
    <div className="timbre-wave" aria-hidden="true">
      {Array.from({ length: 18 }).map((_, index) => {
        const height = 18 + Math.abs(Math.sin(index * profile.brightness + profile.frequency / 180)) * 44;
        return <span key={index} style={{ height: `${height}px` }} />;
      })}
    </div>
  );
}

function normalizeTimbreRounds(config: TemplateForm & Record<string, unknown>): TimbreRound[] {
  if (Array.isArray(config.timbre_rounds) && config.timbre_rounds.length) {
    return config.timbre_rounds as TimbreRound[];
  }
  const pool = config.instrument_pool.length ? config.instrument_pool : ["笛子", "二胡", "钢琴", "小鼓"];
  const traits = config.timbre_traits.length ? config.timbre_traits : ["明亮", "柔和", "短促", "持续", "气息感", "弦鸣", "敲击感"];
  return Array.from({ length: config.round_count }).map((_, index) => {
    const target = pool[index % pool.length];
    const record = fallbackTimbreProfiles[target] || fallbackTimbreProfiles["钢琴"];
    const answer = config.mode === "family_sorting" ? record.family : target;
    const candidates =
      config.mode === "family_sorting"
        ? Array.from(new Set(pool.map((item) => fallbackTimbreProfiles[item]?.family).filter(Boolean) as string[])).slice(0, config.choices_per_round)
        : [target, ...pool.filter((item) => item !== target)].slice(0, config.choices_per_round);
    const evidenceAnswer = record.traits.filter((trait) => traits.includes(trait)).slice(0, Math.max(1, config.evidence_required));
    const compareWith = config.mode === "compare_twins" ? pool.find((item) => item !== target) || null : null;
    return {
      id: `fallback-timbre-${index + 1}`,
      mode: String(config.mode),
      prompt: config.mode === "compare_twins" ? "比较两个相似声音，找出差异证据。" : "找出声音证物对应的嫌疑对象。",
      target,
      family: record.family,
      traits: record.traits,
      candidates: candidates.length ? candidates : [answer],
      evidence_options: Array.from(new Set([...evidenceAnswer, ...traits])).slice(0, Math.max(5, config.evidence_required + 3)),
      evidence_answer: evidenceAnswer.length ? evidenceAnswer : record.traits.slice(0, 1),
      answer,
      compare_with: compareWith,
      audio_profile: record.audio_profile,
      compare_audio_profile: compareWith ? fallbackTimbreProfiles[compareWith]?.audio_profile : null
    };
  });
}

function SolfegeTargetStage({
  config,
  instance
}: {
  config: TemplateForm & Record<string, unknown>;
  instance: GameInstance | null;
}) {
  const rounds = useMemo(() => normalizeSolfegeRounds(config), [config]);
  const [roundIndex, setRoundIndex] = useState(0);
  const [correct, setCorrect] = useState(0);
  const [attempts, setAttempts] = useState(0);
  const [relistens, setRelistens] = useState(0);
  const [selectedPath, setSelectedPath] = useState<string[]>([]);
  const [singBackPending, setSingBackPending] = useState(false);
  const [feedback, setFeedback] = useState("先听目标音，在心里唱出唱名，再瞄准靶心。");
  const current = rounds[Math.min(roundIndex, rounds.length - 1)];
  const mode = config.mode as SolfegeTargetMode;
  const targets = config.target_solfege?.length ? config.target_solfege : ["do", "mi", "sol"];
  const score = attempts ? correct / attempts : 0;

  useEffect(() => {
    setRoundIndex(0);
    setCorrect(0);
    setAttempts(0);
    setRelistens(0);
    setSelectedPath([]);
    setSingBackPending(false);
    setFeedback("先听目标音，在心里唱出唱名，再瞄准靶心。");
  }, [config.template_id, config.mode, config.difficulty, config.round_count, config.target_solfege]);

  const playSequence = useCallback(() => {
    if (!current) {
      return;
    }
    playHybridToneSequence(current.midi_offsets, {
      instrument: config.skin_id === "bubble_pop" ? "xylophone" : "acoustic_grand_piano",
      gap: 0.46,
      duration: 0.38,
      oscillatorWave: config.skin_id === "bubble_pop" ? "sine" : "triangle"
    });
    setRelistens((value) => value + 1);
    setFeedback("听完先别急，心里唱一遍，再击中靶心。");
  }, [config.skin_id, current]);

  const advanceRound = useCallback(() => {
    setSelectedPath([]);
    setSingBackPending(false);
    window.setTimeout(() => {
      setRoundIndex((value) => (value + 1) % rounds.length);
    }, 680);
  }, [rounds.length]);

  const completeRound = useCallback(
    (isCorrect: boolean) => {
      if (isCorrect) {
        setCorrect((value) => value + 1);
        setFeedback("唱回完成，这个唱名已经进到耳朵和声音里了。");
      } else {
        setFeedback("唱回还可以再稳一点，教师可以让学生轻声跟唱一次。");
      }
      advanceRound();
    },
    [advanceRound]
  );

  const handleCorrectTarget = () => {
    if (current.sing_back_required ?? config.require_sing_back) {
      setSingBackPending(true);
      setFeedback("靶心击中了。现在请学生唱回这个音，再由教师确认。");
    } else {
      completeRound(true);
    }
  };

  const answerTarget = (note: string) => {
    if (singBackPending) {
      return;
    }
    setAttempts((value) => value + 1);
    if (current.answer === note) {
      handleCorrectTarget();
    } else {
      setFeedback("这个靶心还不对。再听一次，先在心里唱出目标唱名。");
    }
  };

  const chooseChainNote = (note: string) => {
    if (singBackPending) {
      return;
    }
    setSelectedPath((value) => [...value, note].slice(0, current.sequence.length));
  };

  const submitChain = () => {
    setAttempts((value) => value + 1);
    if (JSON.stringify(selectedPath) === JSON.stringify(current.answer)) {
      handleCorrectTarget();
    } else {
      setFeedback("连环靶顺序还没对。重新听一遍，再按顺序击中唱名。");
      setSelectedPath([]);
    }
  };

  return (
    <Card className={`solfege-stage ${config.skin_id || "star_target"}`}>
      <Flex justify="between" align="start" gap="4" wrap="wrap">
        <Box>
          <Text className="stage-kicker">唱名任务</Text>
          <Heading size="6">{solfegeModeLabels[mode] || "听音打靶"}</Heading>
          <Text as="p" color="gray" mt="2">
            {skinLabels[config.skin_id as GameSkin] || "唱名星靶场"} · 第 {roundIndex + 1}/{rounds.length} 轮
          </Text>
        </Box>
        <Badge color={instance ? "teal" : "amber"} variant="solid">
          {instance ? "已生成" : "待生成"}
        </Badge>
      </Flex>

      <div className="solfege-arena">
        <div className="solfege-core">
          <Crosshair size={38} />
          <Text size="2" weight="bold">
            {config.show_solfege_hint ? current.labels.join("  ") : "听目标音"}
          </Text>
          <Text size="1" color="gray">
            {mode === "target_chain" ? `${current.sequence.length} 音连环靶` : "击中后要唱回"}
          </Text>
        </div>
        {targets.map((note, index) => {
          const angle = -90 + (360 / targets.length) * index;
          const radians = (angle * Math.PI) / 180;
          const x = 50 + 40 * Math.cos(radians);
          const y = 50 + 40 * Math.sin(radians);
          const active = current.sequence.includes(note);
          const selected = selectedPath.includes(note);
          return (
            <button
              key={note}
              type="button"
              className={`solfege-target ${active ? "active" : ""} ${selected ? "selected" : ""}`}
              style={{ left: `${x}%`, top: `${y}%` }}
              onClick={() => (mode === "target_chain" ? chooseChainNote(note) : answerTarget(note))}
            >
              <span>{pitchLabelMap[note] || note}</span>
            </button>
          );
        })}
      </div>

      <Flex gap="3" mt="4" wrap="wrap">
        <Button size="3" onClick={playSequence}>
          <Play size={18} />
          听目标音
        </Button>
        {mode === "target_chain" ? (
          <>
            <Button size="3" color="teal" onClick={submitChain} disabled={selectedPath.length !== current.sequence.length}>
              <Crosshair size={18} />
              提交连环靶
            </Button>
            <Button size="3" variant="soft" color="gray" onClick={() => setSelectedPath([])}>
              清空
            </Button>
          </>
        ) : null}
        {singBackPending ? (
          <>
            <Button size="3" color="green" onClick={() => completeRound(true)}>
              <CheckCircle2 size={18} />
              唱回完成
            </Button>
            <Button size="3" variant="soft" color="amber" onClick={() => completeRound(false)}>
              <Mic2 size={18} />
              再唱一次
            </Button>
          </>
        ) : null}
      </Flex>

      {mode === "target_chain" ? (
        <Text as="p" className="solfege-path">
          当前靶序：{selectedPath.map((note) => pitchLabelMap[note] || note).join(" → ") || "还没有击中靶心"}
        </Text>
      ) : null}

      <Text as="p" className="guardian-feedback solfege-feedback">
        {feedback}
      </Text>

      <Grid columns={{ initial: "2", sm: "4" }} gap="3" mt="4">
        <Metric label="完成" value={`${correct}/${attempts || 0}`} />
        <Metric label="重听" value={`${Math.max(0, relistens - 1)} 次`} />
        <Metric label="靶心" value={`${targets.length} 个`} />
        <Metric label="得分" value={`${Math.round(score * 100)}%`} />
      </Grid>
    </Card>
  );
}

function normalizeSolfegeRounds(config: TemplateForm & Record<string, unknown>): SolfegeRound[] {
  if (Array.isArray(config.solfege_rounds) && config.solfege_rounds.length) {
    return config.solfege_rounds as SolfegeRound[];
  }
  const targets = config.target_solfege.length ? config.target_solfege : ["do", "mi", "sol"];
  return Array.from({ length: config.round_count }).map((_, index) => {
    const sequence =
      config.mode === "target_chain"
        ? Array.from({ length: Math.max(2, config.notes_per_round) }).map((__, step) => targets[(index + step) % targets.length])
        : [targets[index % targets.length]];
    return {
      id: `fallback-solfege-${index + 1}`,
      sequence,
      labels: sequence.map((note) => pitchLabelMap[note] || note),
      midi_offsets: sequence.map((note) => resolvePitchToken(note)?.semitone ?? 0),
      answer: config.mode === "target_chain" ? sequence : sequence[0],
      sing_back_required: config.require_sing_back,
      teacher_confirm_required: config.teacher_confirm_required
    };
  });
}

function PitchLadderStage({
  config,
  instance
}: {
  config: TemplateForm & Record<string, unknown>;
  instance: GameInstance | null;
}) {
  const rounds = useMemo(() => normalizePitchRounds(config), [config]);
  const [roundIndex, setRoundIndex] = useState(0);
  const [correct, setCorrect] = useState(0);
  const [attempts, setAttempts] = useState(0);
  const [selectedPath, setSelectedPath] = useState<string[]>([]);
  const [feedback, setFeedback] = useState("先听目标音，再让角色走上正确台阶。");
  const current = rounds[Math.min(roundIndex, rounds.length - 1)];
  const mode = config.mode as PitchLadderMode;
  const pitchRange = config.pitch_range ?? [];
  const score = attempts ? correct / attempts : 0;

  useEffect(() => {
    setRoundIndex(0);
    setCorrect(0);
    setAttempts(0);
    setSelectedPath([]);
    setFeedback("先听目标音，再让角色走上正确台阶。");
  }, [config.template_id, config.mode, config.difficulty, config.round_count, config.pitch_range]);

  const playSequence = useCallback(() => {
    if (!current) {
      return;
    }
    playHybridToneSequence(current.midi_offsets, {
      instrument: "acoustic_grand_piano",
      gap: 0.48,
      duration: 0.4,
      oscillatorWave: "triangle"
    });
    setFeedback("听完后再判断，不急着点。");
  }, [current]);

  const nextRound = useCallback(
    (isCorrect: boolean) => {
      setAttempts((value) => value + 1);
      if (isCorrect) {
        setCorrect((value) => value + 1);
        setFeedback("音高路线找对了，现在把这组音唱出来。");
      } else {
        setFeedback("再听一次，注意声音是往上、往下，还是保持不变。");
      }
      setSelectedPath([]);
      window.setTimeout(() => {
        setRoundIndex((value) => (value + 1) % rounds.length);
      }, isCorrect ? 760 : 1100);
    },
    [rounds.length]
  );

  const answerDirection = (answer: string) => nextRound(current.answer === answer);
  const answerSolfege = (note: string) => nextRound(current.answer === note);
  const choosePathNote = (note: string) => {
    setSelectedPath((value) => [...value, note].slice(0, current.sequence.length));
  };
  const submitPath = () => {
    nextRound(JSON.stringify(selectedPath) === JSON.stringify(current.answer));
  };

  return (
    <Card className={`pitch-stage ${config.skin_id || "mountain_steps"}`}>
      <Flex justify="between" align="start" gap="4" wrap="wrap">
        <Box>
          <Text className="stage-kicker">音高任务</Text>
          <Heading size="6">{pitchModeLabels[mode] || "高低台阶"}</Heading>
          <Text as="p" color="gray" mt="2">
            {skinLabels[config.skin_id as GameSkin] || "音高山路"} · 第 {roundIndex + 1}/{rounds.length} 轮
          </Text>
        </Box>
        <Badge color={instance ? "teal" : "amber"} variant="solid">
          {instance ? "已生成" : "待生成"}
        </Badge>
      </Flex>

      <div className="pitch-ladder-board">
        <div className="pitch-ladder-rail">
          {pitchRange.map((note, index) => {
            const active = current.sequence.includes(note);
            return (
              <button
                key={note}
                type="button"
                className={`pitch-step ${active ? "active" : ""}`}
                onClick={() => (mode === "solfege_ladder" ? answerSolfege(note) : choosePathNote(note))}
                style={{ transform: `translateY(${(pitchRange.length - index - 1) * -4}px)` }}
              >
                <span>{config.show_solfege_hint ? pitchLabelMap[note] || note : index + 1}</span>
              </button>
            );
          })}
        </div>
        <div className="pitch-cloud">
          {config.skin_id === "cloud_elevator" ? <Cloud size={34} /> : <Mountain size={34} />}
          <Text size="2" weight="bold">
            {current.labels.join("  ")}
          </Text>
        </div>
      </div>

      <Flex gap="3" mt="4" wrap="wrap">
        <Button size="3" onClick={playSequence}>
          <Play size={18} />
          听目标音
        </Button>
        {mode === "high_low_steps" ? (
          <>
            <Button size="3" variant="soft" onClick={() => answerDirection("higher")}>
              更高
            </Button>
            <Button size="3" variant="soft" onClick={() => answerDirection("same")}>
              相同
            </Button>
            <Button size="3" variant="soft" onClick={() => answerDirection("lower")}>
              更低
            </Button>
          </>
        ) : mode === "melody_climb" ? (
          <>
            <Button size="3" color="teal" onClick={submitPath} disabled={selectedPath.length !== current.sequence.length}>
              提交路线
            </Button>
            <Button size="3" variant="soft" color="gray" onClick={() => setSelectedPath([])}>
              清空
            </Button>
          </>
        ) : null}
      </Flex>

      {mode === "melody_climb" ? (
        <Text as="p" className="pitch-path">
          当前路线：{selectedPath.map((note) => pitchLabelMap[note] || note).join(" → ") || "还没有选择"}
        </Text>
      ) : null}

      <Text as="p" className="guardian-feedback pitch-feedback">
        {feedback}
      </Text>

      <Grid columns={{ initial: "2", sm: "4" }} gap="3" mt="4">
        <Metric label="正确" value={`${correct}/${attempts || 0}`} />
        <Metric label="音数" value={`${config.notes_per_round}`} />
        <Metric label="范围" value={`${pitchRange.length} 级`} />
        <Metric label="得分" value={`${Math.round(score * 100)}%`} />
      </Grid>
    </Card>
  );
}

function normalizePitchRounds(config: TemplateForm & Record<string, unknown>): PitchRound[] {
  if (Array.isArray(config.pitch_rounds) && config.pitch_rounds.length) {
    return config.pitch_rounds as PitchRound[];
  }
  const range = config.pitch_range.length ? config.pitch_range : ["do", "re", "mi", "sol", "la"];
  return Array.from({ length: config.round_count }).map((_, index) => {
    const first = range[index % range.length];
    const second = range[Math.min(range.length - 1, (index + 1) % range.length)];
    const sequence =
      config.mode === "solfege_ladder"
        ? [first]
        : config.mode === "melody_climb"
          ? Array.from({ length: Math.max(2, config.notes_per_round) }).map((__, step) => range[(index + step) % range.length])
          : [first, second];
    return {
      id: `fallback-${index + 1}`,
      sequence,
      labels: sequence.map((note) => pitchLabelMap[note] || note),
      midi_offsets: sequence.map((note) => resolvePitchToken(note)?.semitone ?? 0),
      answer:
        config.mode === "solfege_ladder"
          ? first
          : config.mode === "melody_climb"
            ? sequence
            : pitchDirection(first, second)
    };
  });
}

function pitchDirection(first: string, second: string) {
  const order = ["do", "re", "mi", "fa", "sol", "la", "ti", "do_high"];
  const diff = order.indexOf(second) - order.indexOf(first);
  if (diff > 0) {
    return "higher";
  }
  if (diff < 0) {
    return "lower";
  }
  return "same";
}

function BeatGuardianStage({ config, instance }: { config: TemplateForm; instance: GameInstance | null }) {
  const beatsPerBar = Number(config.meter.split("/")[0]);
  const intervalMs = 60000 / config.bpm;
  const totalBeats = beatsPerBar * config.bars_per_round;
  const targetBeatSet = useMemo(() => new Set([1]), []);
  const targetTotal = config.bars_per_round;
  const [running, setRunning] = useState(false);
  const [finished, setFinished] = useState(false);
  const [currentBeat, setCurrentBeat] = useState(1);
  const [hits, setHits] = useState(0);
  const [misses, setMisses] = useState(0);
  const [falseAlarms, setFalseAlarms] = useState(0);
  const [combo, setCombo] = useState(0);
  const [maxCombo, setMaxCombo] = useState(0);
  const [feedback, setFeedback] = useState("生成实例后，按开始充能进入课堂试玩。");
  const startAtRef = useRef(0);
  const lastBeatRef = useRef(0);
  const hitBeatsRef = useRef(new Set<number>());
  const rafRef = useRef<number | null>(null);

  const resetMission = useCallback(() => {
    if (rafRef.current) {
      cancelAnimationFrame(rafRef.current);
      rafRef.current = null;
    }
    setRunning(false);
    setFinished(false);
    setCurrentBeat(1);
    setHits(0);
    setMisses(0);
    setFalseAlarms(0);
    setCombo(0);
    setMaxCombo(0);
    setFeedback("看清护盾收缩节奏，准备在第 1 拍同步充能。");
    hitBeatsRef.current = new Set();
    lastBeatRef.current = 0;
  }, []);

  const playClick = useCallback((strong: boolean) => {
    playHybridToneSequence([strong ? 12 : 5], {
      instrument: "xylophone",
      gap: 0.12,
      duration: 0.1,
      oscillatorWave: "sine",
      gain: strong ? 0.9 : 0.65
    });
  }, []);

  const startMission = useCallback(() => {
    resetMission();
    const countInMs = beatsPerBar * config.count_in_bars * intervalMs;
    startAtRef.current = performance.now() + 600 + countInMs;
    setFeedback(config.count_in_bars ? "预备拍开始，先把身体里的拍子立住。" : "任务开始，预判第 1 拍同步充能。");
    setRunning(true);
  }, [beatsPerBar, config.count_in_bars, intervalMs, resetMission]);

  const guardBeat = useCallback(() => {
    if (!running || finished) {
      return;
    }
    const now = performance.now();
    const rawIndex = (now - startAtRef.current) / intervalMs;
    const nearestBeat = Math.round(rawIndex) + 1;
    if (nearestBeat < 1 || nearestBeat > totalBeats) {
      setFeedback("还没到任务拍，先听预备拍。");
      return;
    }
    const expectedAt = startAtRef.current + (nearestBeat - 1) * intervalMs;
    const diff = now - expectedAt;
    const beatPosition = ((nearestBeat - 1) % beatsPerBar) + 1;
    const isTarget = targetBeatSet.has(beatPosition);
    const isInTime = Math.abs(diff) <= config.timing_tolerance_ms;

    if (isTarget && isInTime && !hitBeatsRef.current.has(nearestBeat)) {
      hitBeatsRef.current.add(nearestBeat);
      setHits((value) => value + 1);
      setCombo((value) => {
        const next = value + 1;
        setMaxCombo((previous) => Math.max(previous, next));
        return next;
      });
      setFeedback(`第 ${beatPosition} 拍同步充能。继续保持稳定。`);
      return;
    }

    setCombo(0);
    if (!isTarget) {
      setFalseAlarms((value) => value + 1);
      setFeedback("弱拍先蓄住，等护盾缩到最小。");
    } else if (diff < 0) {
      setFeedback("你比拍点早了一点，再多预判一点周期。");
    } else {
      setFeedback("这一下有点晚，不能听到后才补按。");
    }
  }, [beatsPerBar, config.timing_tolerance_ms, finished, intervalMs, running, targetBeatSet, totalBeats]);

  useEffect(() => {
    if (!running) {
      return;
    }
    const tick = () => {
      const now = performance.now();
      const rawIndex = (now - startAtRef.current) / intervalMs;
      const beatIndex = Math.floor(rawIndex) + 1;

      if (beatIndex >= 1 && beatIndex <= totalBeats && beatIndex !== lastBeatRef.current) {
        const previousBeat = lastBeatRef.current;
        if (previousBeat >= 1) {
          const previousPosition = ((previousBeat - 1) % beatsPerBar) + 1;
          if (targetBeatSet.has(previousPosition) && !hitBeatsRef.current.has(previousBeat)) {
            setMisses((value) => value + 1);
            setCombo(0);
            setFeedback("第 1 拍已经过去了，下一小节提前准备。");
          }
        }
        lastBeatRef.current = beatIndex;
        setCurrentBeat(((beatIndex - 1) % beatsPerBar) + 1);
        playClick(targetBeatSet.has(((beatIndex - 1) % beatsPerBar) + 1));
      }

      if (beatIndex > totalBeats + 1) {
        setRunning(false);
        setFinished(true);
        setFeedback("本轮结束，看看充能、裂缝和稳定度。");
        return;
      }
      rafRef.current = requestAnimationFrame(tick);
    };
    rafRef.current = requestAnimationFrame(tick);
    return () => {
      if (rafRef.current) {
        cancelAnimationFrame(rafRef.current);
      }
    };
  }, [beatsPerBar, intervalMs, playClick, running, targetBeatSet, totalBeats]);

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.code === "Space") {
        event.preventDefault();
        guardBeat();
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [guardBeat]);

  const score = computeGuardianScore({
    hits,
    misses,
    falseAlarms,
    maxCombo,
    targetTotal,
    comboRequired: config.combo_required,
    mistakeLimit: config.mistake_limit
  });

  return (
    <Card className="guardian-stage">
      <Flex justify="between" align="start" gap="4" wrap="wrap">
        <Box>
          <Text className="stage-kicker">节拍任务</Text>
          <Heading size="6">{beatGuardianModeLabels[config.mode as BeatGuardianMode] || "强拍充能"}</Heading>
          <Text as="p" color="gray" mt="2">
            {config.meter} · 充能拍位：第 1 拍
          </Text>
        </Box>
        <Badge color={instance ? "teal" : "amber"} variant="solid">
          {instance ? "已生成" : "待生成"}
        </Badge>
      </Flex>

      <div className="guardian-board">
        {Array.from({ length: beatsPerBar }).map((_, index) => {
          const beat = index + 1;
          const isTarget = targetBeatSet.has(beat);
          const isActive = running && currentBeat === beat;
          const isStrong = beat === 1;
          return (
            <div
              key={beat}
              className={[
                "guardian-gate",
                isTarget ? "target" : "",
                isActive ? "active" : "",
                isStrong ? "strong-gate" : ""
              ].join(" ")}
            >
              <span className="gate-number">{beat}</span>
              <span className="gate-label">{isTarget ? "充" : isStrong ? "强" : "听"}</span>
            </div>
          );
        })}
      </div>

      <Flex className="guardian-actions" gap="3" wrap="wrap">
        <Button size="3" onClick={startMission}>
          <Play size={18} />
          开始充能
        </Button>
        <Button size="3" color="teal" variant="solid" onClick={guardBeat} disabled={!running}>
          <ShieldCheck size={18} />
          同步充能
        </Button>
        <Button size="3" variant="soft" color="gray" onClick={resetMission}>
          <RotateCcw size={18} />
          重来
        </Button>
      </Flex>

      <Text as="p" className="guardian-feedback">
        {feedback}
      </Text>

      <Grid columns={{ initial: "2", sm: "4" }} gap="3" mt="4">
        <Metric label="命中" value={`${hits}/${targetTotal}`} />
        <Metric label="误击" value={`${falseAlarms}`} />
        <Metric label="漏拍" value={`${misses}`} />
        <Metric label="得分" value={`${Math.round(score * 100)}%`} />
      </Grid>
    </Card>
  );
}

function computeGuardianScore({
  hits,
  misses,
  falseAlarms,
  maxCombo,
  targetTotal,
  comboRequired,
  mistakeLimit
}: {
  hits: number;
  misses: number;
  falseAlarms: number;
  maxCombo: number;
  targetTotal: number;
  comboRequired: number;
  mistakeLimit: number;
}) {
  if (hits + misses + falseAlarms === 0) {
    return 0;
  }
  const timingScore = targetTotal ? hits / targetTotal : 0;
  const beatPositionScore = targetTotal ? Math.max(0, (targetTotal - misses) / targetTotal) : 0;
  const steadinessScore = Math.min(1, maxCombo / Math.max(1, comboRequired));
  const restraintScore = 1 - Math.min(1, falseAlarms / Math.max(1, mistakeLimit + 1));
  return 0.4 * timingScore + 0.35 * beatPositionScore + 0.15 * steadinessScore + 0.1 * restraintScore;
}

function LabeledControl({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="field">
      <Text size="2" weight="bold">
        {label}
      </Text>
      {children}
    </label>
  );
}

function SliderControl({
  icon,
  label,
  value,
  min,
  max,
  suffix,
  onChange
}: {
  icon: ReactNode;
  label: string;
  value: number;
  min: number;
  max: number;
  suffix: string;
  onChange: (value: number) => void;
}) {
  return (
    <Box className="slider-card">
      <Flex justify="between" align="center" mb="3">
        <Flex gap="2" align="center">
          {icon}
          <Text size="2" weight="bold">
            {label}
          </Text>
        </Flex>
        <Text size="2">
          {value} {suffix}
        </Text>
      </Flex>
      <Slider value={[value]} min={min} max={max} step={1} onValueChange={([next]) => onChange(next)} />
    </Box>
  );
}

function ToggleRow({
  label,
  checked,
  onCheckedChange
}: {
  label: string;
  checked: boolean;
  onCheckedChange: (checked: boolean) => void;
}) {
  return (
    <Flex align="center" gap="2">
      <Switch checked={checked} onCheckedChange={onCheckedChange} />
      <Text size="2" weight="bold">
        {label}
      </Text>
    </Flex>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <Box className="metric">
      <Text size="1" color="gray">
        {label}
      </Text>
      <Separator size="4" my="2" />
      <Text size="3" weight="bold">
        {value}
      </Text>
    </Box>
  );
}
