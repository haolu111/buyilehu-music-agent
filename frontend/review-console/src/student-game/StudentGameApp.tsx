import { Badge, Box, Button, Card, Flex, Heading, Select, Text } from "@radix-ui/themes";
import { Check, ClipboardCheck, Compass, Flag, KeyRound, Music2, Play, RotateCcw, Route, ScrollText, Search, Sparkles, Star, Trophy, Undo2, Volume2 } from "lucide-react";
import type { ComponentType, CSSProperties, ReactNode } from "react";
import { useEffect, useMemo, useRef, useState } from "react";
import { resolvePitchToken } from "../shared/pitchCatalog";
import {
  BEAT_GUARDIAN_MONSTER_TOTAL,
  buildBeatGuardianSceneConfig,
  mountBeatGuardianScene,
  type BeatGuardianController,
  type BeatGuardianSceneEvent,
  type BeatGuardianSnapshot
} from "./BeatGuardianScene";
import {
  buildRhythmEchoSceneConfig,
  mountRhythmEchoScene,
  type RhythmEchoController,
  type RhythmEchoSceneEvent,
  type RhythmEchoSnapshot
} from "./RhythmEchoScene";
import {
  buildRaceTimingSceneConfig,
  mountRaceTimingScene,
  type RaceTimingController,
  type RaceTimingSceneEvent,
  type RaceTimingSnapshot
} from "./RaceTimingScene";
import {
  buildPatternBuilderSceneConfig,
  mountPatternBuilderScene,
  type PatternBuilderController,
  type PatternBuilderSceneEvent,
  type PatternBuilderSnapshot,
  type PatternBuilderToken
} from "./PatternBuilderScene";
import {
  buildPitchLadderSceneConfig,
  mountPitchLadderScene,
  type PitchLadderController,
  type PitchLadderSceneEvent,
  type PitchLadderSnapshot
} from "./PitchLadderScene";
import {
  buildSolfegeTargetSceneConfig,
  mountSolfegeTargetScene,
  type SolfegeTargetController,
  type SolfegeTargetSceneEvent,
  type SolfegeTargetSnapshot
} from "./SolfegeTargetScene";
import {
  buildFormTreasureSceneConfig,
  mountFormTreasureScene,
  type FormStructureCard,
  type FormTimelineSegment,
  type FormTreasureController,
  type FormTreasureSceneEvent,
  type FormTreasureSnapshot
} from "./FormTreasureScene";
import { resolveFormRouteJudgement } from "./formTreasureLogic";
import {
  buildCompositionPuzzleSceneConfig,
  mountCompositionPuzzleScene,
  type CompositionPlacedCard,
  type CompositionPuzzleController,
  type CompositionPuzzleSceneEvent,
  type CompositionPuzzleSnapshot
} from "./CompositionPuzzleScene";
import { evaluateCompositionPuzzleChecks } from "./compositionPuzzleLogic";
import { compositionMelodyFilled, generateScaleNoteNames, normalizeScaleType, normalizeTonic, numberedNoteLabel, rhythmAttackCount, rhythmPattern, slotsPerBarForMeter, transposeNoteName, type CompositionMeter, type CompositionScaleType } from "./compositionPuzzleLogic";
import { buildPitchEvidenceSummary } from "./pitchLadderEvidence";
import {
  buildTimbreDetectiveSceneConfig,
  mountTimbreDetectiveScene,
  type TimbreCaseState,
  type TimbreDetectiveController,
  type TimbreDetectiveSceneEvent,
  type TimbreDetectiveSnapshot
} from "./TimbreDetectiveScene";
import { arcadeAssetsForState, type ArcadeAssetState } from "./arcadeAssetRegistry";
import { RhythmNotation } from "../music-components/RhythmNotation";
import { captureVoicePitchDirection, createMusicGameAudioFacade, playTimbreProfile, playToneSequence, type VoiceDirection, type VoicePitchResult } from "./audio";
import { pitchDirectionFromInputAction, resolvePitchLadderKeyAction, resolvePitchLadderSwipeAction } from "./pitchLadderInput";
import { RUNTIME_SHELL_REGISTRY, resolveRuntimeShellKey, type RuntimeShellKey } from "./runtimeShellRegistry";
import { templatePose, templateProp, templateReward, templateVisualPackForConfig } from "./templateVisualAssets";
import { resolveTimbreCaseJudgement } from "./timbreDetectiveLogic";
import {
  mergeCompositionEntityExecutionConfig,
  mergeFormEntityExecutionConfig,
  mergeMeterEntityExecutionConfig,
  mergePitchEntityExecutionConfig,
  mergeRhythmEntityExecutionConfig,
  mergeSolfegeEntityExecutionConfig,
  mergeTimbreEntityExecutionConfig
} from "./musicEntityExecution";
import type {
  ExperienceScript,
  GameplayBlueprint,
  LessonPlayable,
  MusicLogicContract,
  Round,
  StudentGameState,
  StudentTaskCopy,
  LooseRecord,
  PresentationPack,
  ThemePack
} from "./types";

type RuntimeProps = {
  state: StudentGameState;
  feedback: string;
  setFeedback: (value: string) => void;
  onProgress: (active: number, cleared: number) => void;
  onComplete: () => void;
};

const noteLabel = (note: string) => ({
  do: "C",
  re: "D",
  mi: "E",
  fa: "F",
  sol: "G",
  la: "A",
  ti: "B",
  do_high: "C'"
}[note] || note);
type SkinFamily = NonNullable<ThemePack["skin_family"]>;

export function StudentGameApp({ state }: { state: StudentGameState }) {
  const workflow = state.workflow ?? {};
  const blueprint = workflow.gameplay_blueprint ?? {};
  const experience = workflow.experience_script ?? {};
  const theme = mergePresentationPack(workflow.theme_pack ?? {}, workflow.presentation_pack ?? {});
  const presentationPack = workflow.presentation_pack ?? {};
  const lessonContract = state.lesson_game_contract ?? {};
  const lessonPlayable = lessonContract.playable_game ?? {};
  const isLessonRuntime = workflow.workflow_kind === "lesson_game" && Boolean(lessonPlayable.operation_type);
  const [feedback, setFeedback] = useState("先听清任务，再开始挑战。");
  const [activeProgress, setActiveProgress] = useState(0);
  const [clearedProgress, setClearedProgress] = useState(0);
  const [completed, setCompleted] = useState(false);

  useTheme(theme);

  const gameTitle =
    blueprint.student_facing_name || lessonContract.game_name || state.instance?.template_label || "课堂音乐游戏";
  const taskText = isLessonRuntime
    ? blueprint.prompt || lessonPlayable.prompt || lessonContract.game_mechanic || "先听，再操作，最后回到课堂表达。"
    : blueprint.prompt ||
      [state.instance?.student_task?.listen, state.instance?.student_task?.do, state.instance?.student_task?.pass]
        .filter(Boolean)
        .join("；") ||
      "先听，再开始挑战。";
  const progression = experience.progression?.length
    ? experience.progression
    : [{ emotion: "轻松上手", reward: "完成第一关" }];
  const runtimeProps: RuntimeProps = {
    state,
    feedback,
    setFeedback,
    onProgress: (active, cleared) => {
      setActiveProgress(active);
      setClearedProgress(cleared);
    },
    onComplete: () => setCompleted(true)
  };
  const skinFamily = resolveSkinFamily(theme, blueprint.operation_type || lessonPlayable.operation_type || "");
  const skinId = resolveSkinId(state, theme);
  const playMode = resolvePlayMode(state, blueprint, presentationPack);
  const experienceVariantId = resolveExperienceVariantId(state, blueprint, presentationPack);
  const sharedLayoutProps: WorldLayoutProps = {
    state,
    blueprint,
    experience,
    theme,
    lessonContract,
    lessonPlayable,
    isLessonRuntime,
    gameTitle,
    taskText,
    progression,
    feedback,
    activeProgress,
    clearedProgress,
    completed,
    playMode,
    experienceVariantId,
    runtimeProps
  };

  const runtimeShellKey = resolveRuntimeShellKey(state, isLessonRuntime);
  const runtimeShell = runtimeShellKey ? RUNTIME_SHELL_REGISTRY[runtimeShellKey] : null;
  const RuntimeShellComponent = runtimeShellKey ? RUNTIME_SHELL_COMPONENTS[runtimeShellKey] : null;
  if (runtimeShell && RuntimeShellComponent) {
    return (
      <main
        className={[
          "student-shell",
          runtimeShell.pageClass,
          `age-profile-${ageUiProfile(state)}`,
          `skin-${skinId}`,
          `play-mode-${safeClass(playMode)}`,
          `variant-${safeClass(experienceVariantId)}`,
          completed ? "is-complete" : "",
          presentationPack.motion_profile?.tempo ? `motion-${presentationPack.motion_profile.tempo}` : ""
        ].join(" ")}
        data-skin={skinId}
        data-runtime-shell={runtimeShell.key}
        data-experience-variant={experienceVariantId}
        data-play-mode={playMode}
        data-game-genre={runtimeShell.gameGenre}
        data-hud-preset={runtimeShell.hudPreset}
      >
        <RuntimeShellComponent {...sharedLayoutProps} />
      </main>
    );
  }

  return (
    <main
      className={[
        "student-shell",
        `age-profile-${ageUiProfile(state)}`,
        `world-${skinFamily}`,
        `skin-${skinId}`,
        `play-mode-${safeClass(playMode)}`,
        `variant-${safeClass(experienceVariantId)}`,
        completed ? "is-complete" : "",
        presentationPack.motion_profile?.tempo ? `motion-${presentationPack.motion_profile.tempo}` : ""
      ].join(" ")}
      data-skin={skinId}
      data-experience-variant={experienceVariantId}
      data-play-mode={playMode}
    >
      {skinFamily === "race_world" ? <RaceWorldLayout {...sharedLayoutProps} /> : null}
      {skinFamily === "casebook_world" ? <CasebookWorldLayout {...sharedLayoutProps} /> : null}
      {skinFamily === "pulse_world" ? <PulseWorldLayout {...sharedLayoutProps} /> : null}
      {skinFamily === "target_world" ? <TargetWorldLayout {...sharedLayoutProps} /> : null}
      {skinFamily === "trail_world" ? <TrailWorldLayout {...sharedLayoutProps} /> : null}
    </main>
  );
}

function useTheme(theme: ThemePack) {
  useEffect(() => {
    const root = document.documentElement;
    const palette = theme.palette ?? {};
    if (palette.primary) root.style.setProperty("--student-primary", palette.primary);
    if (palette.accent) root.style.setProperty("--student-accent", palette.accent);
    if (palette.background) root.style.setProperty("--student-bg", palette.background);
    if (palette.success) root.style.setProperty("--student-success", palette.success);
    Object.entries(theme.css_variables ?? {}).forEach(([key, value]) => {
      if (key.startsWith("--") && typeof value === "string") {
        root.style.setProperty(key, value);
      }
    });
  }, [theme]);
}

function mergePresentationPack(theme: ThemePack, pack: PresentationPack): ThemePack {
  return {
    ...theme,
    skin_family: pack.skin_family || theme.skin_family,
    layout_variant: pack.layout_variant || theme.layout_variant,
    palette: {
      ...(theme.palette ?? {}),
      ...(pack.palette ?? {})
    },
    scene: {
      ...(theme.scene ?? {}),
      ...(pack.scene ?? {})
    },
    css_variables: {
      ...(theme.css_variables ?? {}),
      ...(pack.css_variables ?? {})
    },
    reward_token: pack.reward_style?.token || theme.reward_token
  };
}

type WorldLayoutProps = {
  state: StudentGameState;
  blueprint: GameplayBlueprint;
  experience: ExperienceScript;
  theme: ThemePack;
  lessonContract: NonNullable<StudentGameState["lesson_game_contract"]>;
  lessonPlayable: LessonPlayable;
  isLessonRuntime: boolean;
  gameTitle: string;
  taskText: string;
  progression: NonNullable<ExperienceScript["progression"]>;
  feedback: string;
  activeProgress: number;
  clearedProgress: number;
  completed: boolean;
  playMode: string;
  experienceVariantId: string;
  runtimeProps: RuntimeProps;
};

function resolveSkinFamily(theme: ThemePack, operationType: string): SkinFamily {
  if (theme.skin_family) return theme.skin_family;
  if (operationType.includes("timbre")) return "casebook_world";
  if (operationType.includes("beat")) return "race_world";
  if (operationType.includes("rhythm")) return "pulse_world";
  if (operationType.includes("solfege") || operationType.includes("target")) return "target_world";
  return "trail_world";
}

function resolveSkinId(state: StudentGameState, theme: ThemePack) {
  const configured = String(state.config?.skin_id || theme.theme_name || theme.skin_family || "classroom_adventure");
  return configured.toLowerCase().replace(/[^a-z0-9_-]+/g, "_");
}

function resolvePlayMode(state: StudentGameState, blueprint: GameplayBlueprint, pack: PresentationPack) {
  return String(
    blueprint.play_mode ||
      pack.play_mode ||
      pack.scene_skin?.play_mode_hint ||
      pack.hud_layout?.play_mode ||
      state.config?.skin_play_mode ||
      "standard"
  );
}

function resolveExperienceVariantId(state: StudentGameState, blueprint: GameplayBlueprint, pack: PresentationPack) {
  return String(
    blueprint.experience_variant_id ||
      pack.experience_variant_id ||
      pack.scene_skin?.experience_variant_id ||
      state.config?.experience_variant_id ||
      "classroom_variant"
  );
}

function safeClass(value: string) {
  return value.toLowerCase().replace(/[^a-z0-9_-]+/g, "_");
}

function isGameFirstBeatGuardian(state: StudentGameState) {
  return state.template_id === "beat_guardian_core" && state.config?.student_ui_mode === "game_first";
}

function readRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" && !Array.isArray(value) ? (value as Record<string, unknown>) : {};
}

function stringValue(value: unknown, fallback = "") {
  const text = String(value ?? "").trim();
  return text || fallback;
}

function templateIdOf(state: StudentGameState) {
  return String(state.template_id || state.config?.template_id || "");
}

function ageUiProfile(state: StudentGameState) {
  const value = String(state.config?.age_ui_profile || state.age_ui_profile || "upper_primary");
  return value === "lower_primary" || value === "junior_middle" ? value : "upper_primary";
}

function gameFantasyForState(state: StudentGameState) {
  return {
    beat_guardian_core: {
      eyebrow: "护盾挑战",
      title: "充能护盾",
      verb: "充能",
      reward: "护盾徽章",
      scene: "节拍护盾"
    },
    rhythm_echo_core: {
      eyebrow: "记忆挑战",
      title: "复刻节奏链",
      verb: "拍回",
      reward: "节奏星",
      scene: "节奏轨道"
    },
    pitch_ladder_core: {
      eyebrow: "登山挑战",
      title: "点亮音高路线",
      verb: "爬梯",
      reward: "旋律宝石",
      scene: "音高山路"
    },
    solfege_target_core: {
      eyebrow: "靶场挑战",
      title: "击中音名靶",
      verb: "命中",
      reward: "靶心星",
      scene: "音名靶场"
    },
    timbre_detective_core: {
      eyebrow: "破案挑战",
      title: "锁定声音嫌疑",
      verb: "破案",
      reward: "侦探章",
      scene: "声音案桌"
    },
    form_treasure_core: {
      eyebrow: "寻宝挑战",
      title: "找到曲式路线",
      verb: "寻宝",
      reward: "结构宝箱",
      scene: "曲式地图"
    }
  }[templateIdOf(state)] ?? {
    eyebrow: "闯关挑战",
    title: "完成音乐任务",
    verb: "挑战",
    reward: "通关章",
    scene: "音乐世界"
  };
}

function starsForScore(score: number, success: boolean) {
  if (!success) return Math.max(1, Math.min(2, Math.ceil(Math.max(0, score) / 45)));
  if (score >= 900) return 3;
  if (score >= 600) return 2;
  return 1;
}

function starsForPercent(percent: number, success: boolean) {
  if (!success) return percent >= 50 ? 2 : 1;
  if (percent >= 90) return 3;
  if (percent >= 70) return 2;
  return 1;
}

function StarRating({ value }: { value: number }) {
  return (
    <div className="arcade-star-rating" aria-label={`${value} 星评价`}>
      {[0, 1, 2].map((index) => (
        <Star key={index} size={22} fill={index < value ? "currentColor" : "none"} />
      ))}
    </div>
  );
}

function ArcadeLevelFlow({
  state,
  phase,
  children
}: {
  state: StudentGameState;
  phase: ArcadeAssetState;
  children: ReactNode;
}) {
  const assets = arcadeAssetsForState(state);
  return (
    <section
      className={[
        "arcade-level-flow",
        `arcade-template-${safeClass(assets.templateId)}`,
        assets.paletteClass,
        `arcade-phase-${phase}`
      ].join(" ")}
      data-arcade-template={assets.templateId}
      data-arcade-phase={phase}
    >
      <span className="arcade-stage-glow glow-left" aria-hidden="true" />
      <span className="arcade-stage-glow glow-right" aria-hidden="true" />
      {children}
    </section>
  );
}

function ArcadeCharacter({
  state,
  phase = "idle",
  compact = false
}: {
  state: StudentGameState;
  phase?: ArcadeAssetState;
  compact?: boolean;
}) {
  const assets = arcadeAssetsForState(state);
  const spec = assets.states[phase];
  return (
    <div className={["arcade-character-card", compact ? "compact" : "", spec.cssClass].join(" ")}>
      <span className="arcade-character-shadow" aria-hidden="true" />
      <span className="arcade-character-sprite" aria-hidden="true">{spec.glyph || assets.heroGlyph}</span>
      <span className="arcade-character-name">{assets.heroName}</span>
      {!compact ? <small>{assets.heroRole} · {spec.label}</small> : null}
    </div>
  );
}

function RhythmEchoStagePartner({ state, phase }: { state: StudentGameState; phase: ArcadeAssetState }) {
  const visualPack = templateVisualPackForConfig(state.config, "rhythm_echo_core");
  const pose = phase === "win"
    ? templatePose(visualPack, "win")
    : phase === "miss"
      ? templatePose(visualPack, "miss")
      : phase === "hit"
        ? templatePose(visualPack, "action")
        : templatePose(visualPack, "idle");
  if (!pose) return null;

  return (
    <div className="rhythm-stage-partner" aria-hidden="true">
      <span className="rhythm-stage-partner-halo" />
      <img src={pose} alt="" draggable={false} />
    </div>
  );
}

function ArcadeStageHeader({
  state,
  phase,
  objective,
  status
}: {
  state: StudentGameState;
  phase: ArcadeAssetState;
  objective?: string;
  status?: string;
}) {
  const assets = arcadeAssetsForState(state);
  return (
    <header className="arcade-stage-header">
      <ArcadeCharacter state={state} phase={phase} compact />
      <div className="arcade-stage-title">
        <span>{assets.stageTitle}</span>
        <strong>{objective || assets.stageProp}</strong>
      </div>
      <div className="arcade-stage-reward-slot">
        <span className="arcade-reward-token" aria-hidden="true">{assets.rewardGlyph}</span>
        <div>
          <small>目标奖励</small>
          <strong>{assets.rewardName}</strong>
        </div>
      </div>
      {status ? <Badge color={phase === "miss" ? "ruby" : phase === "win" ? "green" : "amber"} variant="solid">{status}</Badge> : null}
    </header>
  );
}

function ArcadeRewardBurst({
  state,
  success,
  label
}: {
  state: StudentGameState;
  success: boolean;
  label?: string;
}) {
  const assets = arcadeAssetsForState(state);
  return (
    <div className={["arcade-reward-burst", success ? "success" : "fail"].join(" ")} aria-hidden="true">
      <span className="reward-ring" />
      <span className="reward-token-big">{success ? assets.rewardGlyph : "再"}</span>
      <strong>{label || (success ? assets.successFx : assets.failFx)}</strong>
    </div>
  );
}

function ArcadeFailState({
  state,
  reason
}: {
  state: StudentGameState;
  reason: string;
}) {
  const assets = arcadeAssetsForState(state);
  return (
    <div className="arcade-fail-state" role="note">
      <ArcadeCharacter state={state} phase="miss" compact />
      <div>
        <strong>{assets.failFx}</strong>
        <span>{reason}</span>
      </div>
    </div>
  );
}

function ClassroomTaskStrip({ state, compact = false }: { state: StudentGameState; compact?: boolean }) {
  const task = taskCopyForState(state);
  if (compact) {
    return (
      <details className="classroom-task-strip compact">
        <summary>本关任务</summary>
        <span>{task.listen}</span>
        <span>{task.do}</span>
        <span>{task.pass}</span>
      </details>
    );
  }
  return (
    <section className="classroom-task-strip" aria-label="本局音乐任务">
      <span>{task.listen}</span>
      <span>{task.do}</span>
      <span>{task.pass}</span>
    </section>
  );
}

function missionBoardImageForState(state: StudentGameState) {
  const visualPack = templateVisualPackForConfig(state.config, templateIdOf(state));
  return visualPack.mission_board;
}

function MissionBoardArt({ state, compact = false }: { state: StudentGameState; compact?: boolean }) {
  const missionBoardImage = missionBoardImageForState(state);
  if (!missionBoardImage) return null;
  return (
    <img
      className={["arcade-task-board-art", compact ? "compact" : ""].join(" ")}
      src={missionBoardImage}
      alt="本关任务图"
    />
  );
}

function ArcadeStartOverlay({
  state,
  title,
  subtitle,
  actionLabel,
  onStart,
  disabled = false
}: {
  state: StudentGameState;
  title?: string;
  subtitle?: string;
  actionLabel?: string;
  onStart: () => void;
  disabled?: boolean;
}) {
  const fantasy = gameFantasyForState(state);
  const assets = arcadeAssetsForState(state);
  return (
    <section className="arcade-start-overlay" aria-label="关卡封面">
      <div className="arcade-cover-art">
        <span className="cover-burst" />
        <ArcadeCharacter state={state} phase="idle" />
        <em>{assets.stageProp}</em>
      </div>
      <div className="arcade-cover-copy">
        <Text className="eyebrow">{fantasy.eyebrow}</Text>
        <Heading size="6">{title || fantasy.title}</Heading>
        <p>{subtitle || taskCopyForState(state).do}</p>
        <MissionBoardArt state={state} />
        <div className="arcade-reference-chip">
          <span>玩法参考</span>
          <strong>{assets.referenceGame.title}</strong>
          <small>{assets.referenceGame.pattern}</small>
        </div>
        <div className="arcade-cover-reward">
          <span>{assets.rewardGlyph}</span>
          <strong>{assets.rewardName}</strong>
          <small>{assets.successFx}</small>
        </div>
        <Button className="game-action primary arcade-start-button" size="4" onClick={onStart} disabled={disabled}>
          <Play size={18} fill="currentColor" />
          {actionLabel || assets.startCta || "开始挑战"}
        </Button>
      </div>
      <ClassroomTaskStrip state={state} compact />
    </section>
  );
}

function ArcadeHudBar({
  state,
  level,
  score,
  energy,
  combo,
  comboLabel = "连击",
  status
}: {
  state: StudentGameState;
  level: string;
  score?: number;
  energy?: number;
  combo?: string | number;
  comboLabel?: string;
  status?: string;
}) {
  const fantasy = gameFantasyForState(state);
  const assets = arcadeAssetsForState(state);
  return (
    <header className="arcade-hud-bar">
      <div className="arcade-level-tag">
        <span>{fantasy.scene}</span>
        <strong>{level}</strong>
      </div>
      <div className="arcade-score-strip">
        {typeof score === "number" ? <span>得分 <strong>{Math.max(0, Math.round(score))}</strong></span> : null}
        {typeof energy === "number" ? <span>能量 <strong>{Math.max(0, Math.round(energy))}%</strong></span> : null}
        {combo !== undefined ? <span>{comboLabel} <strong>{combo}</strong></span> : null}
      </div>
      <div className="arcade-hud-reward">
        <span>{assets.rewardGlyph}</span>
        <strong>{assets.rewardName}</strong>
      </div>
      <div className="arcade-hud-reference">
        <small>参考</small>
        <strong>{assets.referenceGame.title}</strong>
      </div>
      {status ? <Badge color="amber" variant="solid">{status}</Badge> : null}
    </header>
  );
}

function ArcadeResultPanel({
  state,
  success,
  title,
  prompt,
  score,
  stars,
  badges,
  onReplay,
  onNext,
  nextDisabled,
  nextLabel = "下一关"
}: {
  state: StudentGameState;
  success: boolean;
  title: string;
  prompt: string;
  score?: number;
  stars: number;
  badges?: Array<[string, string]>;
  onReplay: () => void;
  onNext?: () => void;
  nextDisabled?: boolean;
  nextLabel?: string;
}) {
  const fantasy = gameFantasyForState(state);
  return (
    <div className="arcade-result-layer" role="status">
      <Card className="guardian-reflection-card arcade-result-card">
        <ArcadeRewardBurst state={state} success={success} />
        <Text className="eyebrow">{success ? "闯关成功" : "挑战复盘"}</Text>
        <Heading size="5">{title}</Heading>
        <StarRating value={stars} />
        <div className="arcade-reward-badge">
          <Trophy size={18} />
          <strong>{success ? fantasy.reward : "复盘机会"}</strong>
          {typeof score === "number" ? <span>{Math.max(0, Math.round(score))} 分</span> : null}
        </div>
        <Text as="p">{prompt}</Text>
        {!success ? <ArcadeFailState state={state} reason={prompt} /> : null}
        {badges?.length ? (
          <Flex gap="2" wrap="wrap">
            {badges.map(([label, value]) => (
              <Badge key={label} color="teal" variant="soft">{label} {value}</Badge>
            ))}
          </Flex>
        ) : null}
        <Flex className="arcade-result-actions" gap="2" wrap="wrap">
          <Button className="game-action primary" size="3" onClick={onReplay}>
            <RotateCcw size={16} />
            再玩一次
          </Button>
          <Button className="game-action" size="3" variant="soft" onClick={onNext || onReplay} disabled={nextDisabled}>
            {nextLabel}
          </Button>
        </Flex>
      </Card>
    </div>
  );
}

function taskCopyForState(state: StudentGameState): Required<StudentTaskCopy> {
  const fromState = readRecord(state.student_task_copy);
  const fromConfig = readRecord(state.config?.student_task_copy);
  const byTemplate: Record<string, Required<StudentTaskCopy>> = {
    beat_guardian_core: {
      listen: "听什么：听清稳定拍和第 1 拍重音周期。",
      do: "做什么：第 1 拍同步充能，用震波弹开靠近的怪物。",
      pass: "怎样过关：清掉全部弱拍怪物，别让护盾裂开。"
    },
    rhythm_echo_core: {
      listen: "听什么：先完整听一遍目标节奏。",
      do: "做什么：用点击、拍手或身体动作拍回来。",
      pass: "怎样过关：节奏顺序和拍点都稳定。"
    },
    pitch_ladder_core: {
      listen: "听什么：先听目标音或短旋律。",
      do: "做什么：判断更高、更低或走出台阶路线。",
      pass: "怎样过关：找对路线后唱出来。"
    },
    solfege_target_core: {
      listen: "听什么：听目标音，在心里找到音名。",
      do: "做什么：先击中音名，再唱回确认。",
      pass: "怎样过关：命中并完成唱回。"
    },
    timbre_detective_core: {
      listen: "听什么：听声音证物，抓住音色线索。",
      do: "做什么：选择嫌疑对象，再贴上证据词。",
      pass: "怎样过关：对象和音色证据都成立。"
    },
    form_treasure_core: {
      listen: "听什么：听每个段落是否重复、对比或再现。",
      do: "做什么：放结构卡，排出曲式路线。",
      pass: "怎样过关：路线正确，并能说出依据。"
    }
  };
  const fallback = byTemplate[templateIdOf(state)] || {
    listen: "听什么：先听清音乐任务。",
    do: "做什么：完成屏幕上的音乐操作。",
    pass: "怎样过关：操作正确，并能说出音乐依据。"
  };
  return {
    listen: stringValue(fromConfig.listen ?? fromState.listen, fallback.listen),
    do: stringValue(fromConfig.do ?? fromState.do, fallback.do),
    pass: stringValue(fromConfig.pass ?? fromState.pass, fallback.pass)
  };
}

function resultTransferPrompt(state: StudentGameState, fallback: string) {
  return stringValue(state.config?.result_transfer_prompt ?? state.result_transfer_prompt, fallback);
}

function reasonPrompt(state: StudentGameState, key: string, fallback: string) {
  const prompts = { ...readRecord(state.music_reason_prompts), ...readRecord(state.config?.music_reason_prompts) };
  return stringValue(prompts[key], fallback);
}

function VariantMissionRibbon({
  blueprint,
  theme,
  playMode,
  experienceVariantId
}: Pick<WorldLayoutProps, "blueprint" | "theme" | "playMode" | "experienceVariantId">) {
  const goal = blueprint.scene_goal || theme.scene_goal || theme.scene?.objective_noun || "完成音乐挑战";
  return (
    <aside className="variant-mission-ribbon" data-play-mode={playMode} data-experience-variant={experienceVariantId}>
      <span className="variant-pill">任务</span>
      <strong>{goal}</strong>
    </aside>
  );
}

function RadixGameShell({
  props,
  className,
  eyebrow,
  dataRuntimeShell,
  dataGameGenre,
  children,
  accent,
  aside
}: {
  props: WorldLayoutProps;
  className: string;
  eyebrow: string;
  dataRuntimeShell: RuntimeShellKey;
  dataGameGenre: string;
  children: ReactNode;
  accent?: ReactNode;
  aside?: ReactNode;
}) {
  const { gameTitle, taskText, completed, theme } = props;
  return (
    <section className={className} data-runtime-shell={dataRuntimeShell} data-game-genre={dataGameGenre} data-ui-library="radix-themes">
      <Card className="radix-game-shell-card">
        <Flex className="radix-game-shell-header" align="center" justify="between" gap="4" wrap="wrap">
          <Box className="radix-game-shell-title">
            <Text className="eyebrow">{eyebrow}</Text>
            <Heading size="6">{gameTitle}</Heading>
            <Text as="p" size="3">{taskText || "先听，再操作，完成音乐挑战。"}</Text>
          </Box>
          <Flex className="radix-game-shell-badges" gap="2" align="center" wrap="wrap">
            <Badge color={completed ? "green" : "amber"} variant="soft">{completed ? "已完成" : "挑战中"}</Badge>
            <Badge color="blue" variant="soft">{theme.reward_token || "奖励"}</Badge>
            {accent}
          </Flex>
        </Flex>
        <VariantMissionRibbon {...props} />
        {aside ? (
          <Flex className="radix-game-shell-body with-aside" gap="4" align="stretch">
            <Box className="radix-game-shell-main">{children}</Box>
            {aside}
          </Flex>
        ) : (
          <Box className="radix-game-shell-main">{children}</Box>
        )}
      </Card>
    </section>
  );
}

function BeatGuardianShell(props: WorldLayoutProps) {
  return (
    <RadixGameShell
      props={props}
      className="beat-guardian-arcade-shell"
      dataRuntimeShell="beat_guardian_shell"
      dataGameGenre="arcade_guardian"
      eyebrow="充能护盾"
      accent={<Badge color="teal" variant="solid">互动课堂界面</Badge>}
    >
      <BeatGuardianGame {...props.runtimeProps} />
    </RadixGameShell>
  );
}

function RhythmEchoMemoryShell(props: WorldLayoutProps) {
  return (
    <section
      className="rhythm-echo-memory-shell rhythm-echo-publish-shell"
      data-runtime-shell="rhythm_echo_shell"
      data-game-genre="memory_echo"
      data-ui-library="radix-themes"
    >
      <RhythmEchoGame {...props.runtimeProps} />
    </section>
  );
}

function RaceTimingShell(props: WorldLayoutProps) {
  const { runtimeProps, completed } = props;
  return (
    <RadixGameShell
      props={props}
      className="race-timing-shell"
      dataRuntimeShell="race_timing_shell"
      dataGameGenre="arcade_race"
      eyebrow="节拍竞速"
      accent={<Badge color="crimson" variant="solid">{completed ? "冲线" : "连击"}</Badge>}
    >
      <RaceTimingGame {...runtimeProps} />
    </RadixGameShell>
  );
}

function PatternBuilderShell(props: WorldLayoutProps) {
  const { runtimeProps, completed } = props;
  return (
    <RadixGameShell
      props={props}
      className="pattern-builder-shell"
      dataRuntimeShell="pattern_builder_shell"
      dataGameGenre="rhythm_builder"
      eyebrow="节奏工坊"
      accent={<Badge color="purple" variant="solid">{completed ? "完成" : "拼图"}</Badge>}
    >
      <PatternBuilderGame {...runtimeProps} />
    </RadixGameShell>
  );
}

function PitchLadderMapShell(props: WorldLayoutProps) {
  const { runtimeProps } = props;
  return (
    <section
      className="pitch-ladder-map-shell adventure-map-shell"
      data-runtime-shell="pitch_ladder_map_shell"
      data-game-genre="map_climb"
      data-game-experience="adventure_climb"
    >
      <section className="map-play-panel adventure-play-panel">
        <PitchLadderGame {...runtimeProps} />
      </section>
    </section>
  );
}

function SolfegeTargetShell(props: WorldLayoutProps) {
  const { runtimeProps, theme, completed } = props;
  return (
    <RadixGameShell
      props={props}
      className="solfege-target-shell"
      dataRuntimeShell="solfege_target_shell"
      dataGameGenre="target_range"
      eyebrow="音名靶场"
      accent={<Badge color="orange" variant="solid">{theme.reward_token || "靶心"}</Badge>}
    >
      <div className="target-range-stage">
        <span className="reticle-ring" aria-hidden="true" />
        <SolfegeTargetGame {...runtimeProps} />
      </div>
      {completed ? <div className="genre-result-chip">命中后开口唱回</div> : null}
    </RadixGameShell>
  );
}

function TimbreDetectiveShell(props: WorldLayoutProps) {
  const { runtimeProps, theme, completed } = props;
  return (
    <RadixGameShell
      props={props}
      className="timbre-detective-shell"
      dataRuntimeShell="timbre_detective_shell"
      dataGameGenre="detective_mystery"
      eyebrow="声音案卷"
      accent={<Badge color="brown" variant="solid">{completed ? "已破案" : theme.avatar?.name || "侦探"}</Badge>}
    >
      <div className="detective-desk-grid">
        <TimbreDetectiveGame {...runtimeProps} />
      </div>
    </RadixGameShell>
  );
}

function FormTreasureShell(props: WorldLayoutProps) {
  const { runtimeProps, theme, completed } = props;
  return (
    <RadixGameShell
      props={props}
      className="form-treasure-shell"
      dataRuntimeShell="form_treasure_shell"
      dataGameGenre="form_treasure_map"
      eyebrow="曲式寻宝"
      accent={<Badge color="yellow" variant="solid">{completed ? "已找到" : theme.reward_token || "宝藏"}</Badge>}
    >
      <FormTreasureGame {...runtimeProps} />
    </RadixGameShell>
  );
}

function CompositionPuzzleShell(props: WorldLayoutProps) {
  const { runtimeProps, theme, completed } = props;
  return (
    <RadixGameShell
      props={props}
      className="composition-puzzle-shell"
      dataRuntimeShell="composition_puzzle_shell"
      dataGameGenre="constrained_composition_puzzle"
      eyebrow="拼图创编工坊"
      accent={<Badge color="green" variant="solid">{completed ? "已创编" : theme.reward_token || "创编徽章"}</Badge>}
    >
      <CompositionPuzzleGame {...runtimeProps} />
    </RadixGameShell>
  );
}

const RUNTIME_SHELL_COMPONENTS: Record<RuntimeShellKey, ComponentType<WorldLayoutProps>> = {
  beat_guardian_shell: BeatGuardianShell,
  rhythm_echo_shell: RhythmEchoMemoryShell,
  race_timing_shell: RaceTimingShell,
  pattern_builder_shell: PatternBuilderShell,
  pitch_ladder_map_shell: PitchLadderMapShell,
  solfege_target_shell: SolfegeTargetShell,
  timbre_detective_shell: TimbreDetectiveShell,
  form_treasure_shell: FormTreasureShell,
  composition_puzzle_shell: CompositionPuzzleShell
};

function WorldBanner({
  state,
  blueprint,
  experience,
  theme,
  isLessonRuntime,
  gameTitle
}: Pick<WorldLayoutProps, "state" | "blueprint" | "experience" | "theme" | "isLessonRuntime" | "gameTitle">) {
  return (
    <section className="student-hero">
      <Box>
        <Text className="eyebrow">
          不亦乐乎 · {theme.scene?.setting || theme.theme_name || "学生游戏"}
        </Text>
        <Heading className="student-title">{gameTitle}</Heading>
        <Text as="p">{experience.opening_hook || state.proposal_card?.transfer_task || "先听，再开始挑战。"}</Text>
      </Box>
      <div className="hero-orb">
        <Badge color="teal" variant="soft">
          {isLessonRuntime ? "教案专属游戏" : "学生成品游戏"}
        </Badge>
        <strong>{theme.avatar?.name || "小乐手"}</strong>
        <span>{blueprint.player_verb || "开始挑战"}</span>
      </div>
    </section>
  );
}

function QuestCard({ label, title, body }: { label: string; title: string; body?: string }) {
  return (
    <Card className="quest-card">
      <Text className="eyebrow">{label}</Text>
      <Heading size="4">{title}</Heading>
      {body ? <Text as="p">{body}</Text> : null}
    </Card>
  );
}

function QuestRail({
  gameTitle,
  taskText,
  experience,
  blueprint
}: Pick<WorldLayoutProps, "gameTitle" | "taskText" | "experience" | "blueprint">) {
  return (
    <div className="quest-rail">
      <QuestCard label="本关任务" title={gameTitle} body={taskText} />
      <QuestCard label="第一步" title={experience.tutorial?.first_action_hint || "先试听目标，再开始第一步操作。"} />
      <QuestCard label="通关目标" title={blueprint.win_condition || "完成挑战。"} />
    </div>
  );
}

function CoachCard({
  icon,
  label,
  title,
  children
}: {
  icon: ReactNode;
  label: string;
  title: string;
  children: ReactNode;
}) {
  return (
    <Card className="coach-card">
      <Flex align="center" gap="2">
        {icon}
        <Text className="eyebrow">{label}</Text>
      </Flex>
      <Heading size="4">{title}</Heading>
      {children}
    </Card>
  );
}

function ProgressCoach({
  progression,
  activeProgress,
  clearedProgress,
  theme
}: Pick<WorldLayoutProps, "progression" | "activeProgress" | "clearedProgress" | "theme">) {
  return (
    <CoachCard icon={<Flag size={16} />} label="进度" title={`${theme.scene?.progress_noun || "闯关"}进度`}>
      <div className="progress-rail">
        {progression.map((item, index) => (
          <div
            key={`${item.round_id ?? index}`}
            className={[
              "progress-item",
              index < clearedProgress ? "done" : "",
              index === activeProgress ? "active" : ""
            ].join(" ")}
          >
            <strong>{item.emotion || `第 ${index + 1} 关`}</strong>
            <small>{item.reward || "继续挑战"}</small>
          </div>
        ))}
      </div>
    </CoachCard>
  );
}

function RewardCoach({
  progression,
  activeProgress,
  theme
}: Pick<WorldLayoutProps, "progression" | "activeProgress" | "theme">) {
  return (
    <CoachCard icon={<Sparkles size={16} />} label="奖励" title={`下一枚${theme.reward_token || "奖励"}`}>
      <p>{progression[Math.min(activeProgress, progression.length - 1)]?.reward || "继续挑战"}</p>
    </CoachCard>
  );
}

function ReplayCoach({ experience }: Pick<WorldLayoutProps, "experience">) {
  return (
    <CoachCard icon={<RotateCcw size={16} />} label="重玩" title="再玩一次">
      <p>{experience.replay_hook || "换一组材料，再挑战一次。"}</p>
    </CoachCard>
  );
}

function PlayStage({
  state,
  blueprint,
  theme,
  gameTitle,
  taskText,
  lessonContract,
  lessonPlayable,
  isLessonRuntime,
  feedback,
  completed,
  experience,
  runtimeProps
}: Pick<
  WorldLayoutProps,
  | "state"
  | "blueprint"
  | "theme"
  | "gameTitle"
  | "taskText"
  | "lessonContract"
  | "lessonPlayable"
  | "isLessonRuntime"
  | "feedback"
  | "completed"
  | "experience"
  | "runtimeProps"
>) {
  const gameFirst = isGameFirstBeatGuardian(state);
  return (
    <Card className={["play-stage", completed ? "complete" : ""].join(" ")}>
      {!gameFirst ? <SkinSceneDecor state={state} theme={theme} completed={completed} /> : null}
      {!gameFirst ? (
        <div className="play-stage-header">
          <div className="stage-avatar" aria-hidden="true">
            <Music2 size={22} />
          </div>
          <Box>
            <Text className="eyebrow">闯关任务</Text>
            <Heading size="5">{gameTitle}</Heading>
            <Text as="p">{taskText}</Text>
          </Box>
          <div className="mission-chip">
            <span>{blueprint.player_verb || "挑战"}</span>
            <strong>{theme.reward_token || "通关章"}</strong>
          </div>
        </div>
      ) : null}
      <GameRuntime
        {...runtimeProps}
        isLessonRuntime={isLessonRuntime}
        lessonPlayable={lessonPlayable}
        musicLogic={lessonContract.music_logic_contract ?? {}}
      />
      {!gameFirst ? (
        <div className={["feedback-card", completed ? "success" : ""].join(" ")}>
          <strong>{completed ? "通关反馈" : "即时反馈"}</strong>
          <span>{feedback}</span>
        </div>
      ) : null}
      {!gameFirst && completed ? (
        <div className="closure-card">
          <strong>通关后</strong>
          <p>{experience.closure_prompt || "说出你刚才听到的音乐依据。"}</p>
        </div>
      ) : null}
    </Card>
  );
}

function SkinSceneDecor({ state, theme, completed }: { state: StudentGameState; theme: ThemePack; completed: boolean }) {
  const skinId = resolveSkinId(state, theme);
  const prop = theme.scene?.supporting_prop || theme.scene?.objective_noun || "音乐任务";
  return (
    <div className="stage-scene" aria-hidden="true">
      <span className="scene-band" />
      <span className="scene-prop">{prop}</span>
      <span className="scene-token">{completed ? "已点亮" : theme.reward_token || "奖励"}</span>
      <span className={`scene-marker marker-${skinId}`} />
    </div>
  );
}

function TrailWorldLayout(props: WorldLayoutProps) {
  return <GameFrameLayout {...props} frame="trail" />;
}

function RaceWorldLayout(props: WorldLayoutProps) {
  return <GameFrameLayout {...props} frame="race" />;
}

function PulseWorldLayout(props: WorldLayoutProps) {
  return <GameFrameLayout {...props} frame="pulse" />;
}

function CasebookWorldLayout(props: WorldLayoutProps) {
  return <GameFrameLayout {...props} frame="casebook" />;
}

function TargetWorldLayout(props: WorldLayoutProps) {
  return <GameFrameLayout {...props} frame="target" />;
}

function GameFrameLayout(props: WorldLayoutProps & { frame: "trail" | "race" | "pulse" | "casebook" | "target" }) {
  const { frame, gameTitle, taskText, experience, blueprint, theme, isLessonRuntime, progression, activeProgress, clearedProgress, completed } = props;
  const gameFirst = isGameFirstBeatGuardian(props.state);
  return (
    <section className={`game-frame frame-${frame} ${gameFirst ? "game-frame-first" : ""}`}>
      <header className="game-hud">
        <div className="hud-brand">
          <span className="hud-kicker">{isLessonRuntime ? "本课专属游戏" : "学生成品游戏"}</span>
          <h1>{gameTitle}</h1>
        </div>
        <div className="hud-status">
          <span>{theme.scene?.setting || theme.theme_name || "音乐世界"}</span>
          <strong>{completed ? "已通关" : blueprint.player_verb || "挑战中"}</strong>
        </div>
        <div className="hud-progress" aria-label="闯关进度">
          {progression.map((item, index) => (
            <span
              key={`${item.round_id ?? index}`}
              className={[
                "hud-dot",
                index < clearedProgress ? "done" : "",
                index === activeProgress ? "active" : ""
              ].join(" ")}
              title={item.reward || `第 ${index + 1} 关`}
            />
          ))}
        </div>
      </header>
      <VariantMissionRibbon {...props} />

      <div className="game-main">
        <PlayStage {...props} />
        {!gameFirst ? <aside className="game-sidecar" aria-label="游戏提示">
          <div className="side-mission-card primary">
            <span>本关任务</span>
            <strong>{taskText}</strong>
          </div>
          <div className="side-mission-card">
            <span>第一步</span>
            <strong>{experience.tutorial?.first_action_hint || "先试听目标，再开始操作。"}</strong>
          </div>
          <div className="side-mission-card">
            <span>通关后</span>
            <strong>{experience.closure_prompt || blueprint.win_condition || "说出你的音乐依据。"}</strong>
          </div>
          <div className="side-reward-card">
            <Sparkles size={18} />
            <span>下一枚{theme.reward_token || "奖励"}</span>
            <strong>{progression[Math.min(activeProgress, progression.length - 1)]?.reward || "继续挑战"}</strong>
          </div>
        </aside> : null}
      </div>
    </section>
  );
}

function GameRuntime(
  props: RuntimeProps & {
    isLessonRuntime: boolean;
    lessonPlayable: LessonPlayable;
    musicLogic: MusicLogicContract;
  }
) {
  if (props.state.template_id === "beat_guardian_core") {
    return <BeatGuardianGame {...props} />;
  }
  if (props.state.template_id === "pitch_ladder_core") {
    return <PitchLadderGame {...props} />;
  }
  if (props.state.template_id === "solfege_target_core") {
    return <SolfegeTargetGame {...props} />;
  }
  if (props.state.template_id === "timbre_detective_core") {
    return <TimbreDetectiveGame {...props} />;
  }
  if (props.state.template_id === "form_treasure_core") {
    return <FormTreasureGame {...props} />;
  }
  if (props.state.template_id === "composition_puzzle_core") {
    return <CompositionPuzzleGame {...props} />;
  }
  if (props.isLessonRuntime && props.lessonPlayable.operation_type === "melody_path_draw") {
    return <LessonMelodyPath {...props} />;
  }
  if (props.isLessonRuntime) {
    return <LessonSequenceGame {...props} />;
  }
  return <RhythmEchoGame {...props} />;
}

function lessonRounds(playable: LessonPlayable, musicLogic: MusicLogicContract) {
  return playable.rounds?.length
    ? playable.rounds
    : musicLogic.rounds?.length
      ? musicLogic.rounds
      : [{ id: "round_1", label: "第 1 关", target_sequence: playable.target_sequence ?? [] }];
}

function lessonMidi(id: string, playable: LessonPlayable, musicLogic: MusicLogicContract) {
  const token = musicLogic.tokens?.find((item) => item.id === id);
  const material = playable.materials?.find((item) => item.id === id);
  return Number(token?.playback?.midi ?? material?.pitch ?? 60);
}

function playLessonSequence(ids: string[], playable: LessonPlayable, musicLogic: MusicLogicContract) {
  const audioUrl = ids
    .map((id) => playable.materials?.find((item) => item.id === id))
    .map((item) => item?.audio_clip_url || item?.source_audio_url || item?.audio_url || "")
    .find(Boolean);
  return playToneSequence(ids.map((id) => lessonMidi(id, playable, musicLogic) - 60), "triangle", 0.52, {
    audioUrl,
    instrument: "acoustic_grand_piano"
  });
}

function LessonSequenceGame({
  lessonPlayable,
  musicLogic,
  setFeedback,
  onProgress,
  onComplete
}: RuntimeProps & { lessonPlayable: LessonPlayable; musicLogic: MusicLogicContract }) {
  const rounds = lessonRounds(lessonPlayable, musicLogic);
  const materials = lessonPlayable.materials ?? [];
  const feedback = lessonPlayable.feedback ?? {};
  const [roundIndex, setRoundIndex] = useState(0);
  const [chosen, setChosen] = useState<string[]>([]);
  const [cleared, setCleared] = useState(0);
  const round = rounds[roundIndex % rounds.length];
  const target = round.target_sequence ?? lessonPlayable.target_sequence ?? [];

  useEffect(() => onProgress(roundIndex, cleared), [roundIndex, cleared]);

  const choose = (id: string) => {
    if (chosen.length >= target.length) return;
    const next = [...chosen, id];
    setChosen(next);
    setFeedback(next.length < target.length ? feedback.partial || "继续完成挑战。" : "答案已经摆好，试听或检查一下。");
  };

  const check = () => {
    if (!chosen.length) return setFeedback(feedback.empty || "先完成你的答案。");
    if (chosen.length < target.length) return setFeedback(feedback.partial || "还没有完成整组答案。");
    if (chosen.join("|") !== target.join("|")) return setFeedback(feedback.wrong || "再听一次，再调整。");
    const nextCleared = Math.max(cleared, roundIndex + 1);
    setCleared(nextCleared);
    if (roundIndex + 1 >= rounds.length) onComplete();
    setFeedback(roundIndex + 1 >= rounds.length ? feedback.success || "挑战成功。" : "这一关完成了，继续下一关。");
  };

  return (
    <>
      <GameControls
        controls={[
          ["试听目标", () => playLessonSequence(target, lessonPlayable, musicLogic) || setFeedback("当前浏览器不能播放声音，请由教师范唱目标音。")],
          ["试听我的排列", () => chosen.length ? playLessonSequence(chosen, lessonPlayable, musicLogic) : setFeedback(feedback.empty || "先完成你的答案。")],
          ["检查挑战", check],
          ["重来", () => setChosen([])],
          [
            "下一关",
            () => {
              setRoundIndex((value) => Math.min(value + 1, rounds.length - 1));
              setChosen([]);
            }
          ]
        ]}
      />
      <div className="mission-board">
        <Hud items={[["关卡", round.label || `${roundIndex + 1}/${rounds.length}`], ["目标长度", String(target.length)], ["已通关", `${cleared}/${rounds.length}`]]} />
        <div className="mission-card">
          <strong>本关任务</strong>
          <p>{round.prompt || lessonPlayable.prompt || "先听，再完成挑战。"}</p>
        </div>
        <div className="challenge-lane">
          {target.map((_, index) => (
            <span key={index} className="challenge-slot">
              {noteLabel(chosen[index] || "?")}
            </span>
          ))}
        </div>
        <div className="lesson-materials">
          {materials.map((item) => (
            <Button key={item.id} variant="soft" onClick={() => choose(item.id)}>
              {item.label || item.id}
            </Button>
          ))}
        </div>
      </div>
    </>
  );
}

function LessonMelodyPath({
  lessonPlayable,
  musicLogic,
  setFeedback,
  onProgress,
  onComplete
}: RuntimeProps & { lessonPlayable: LessonPlayable; musicLogic: MusicLogicContract }) {
  const rounds = lessonRounds(lessonPlayable, musicLogic);
  const feedback = lessonPlayable.feedback ?? {};
  const [roundIndex, setRoundIndex] = useState(0);
  const [route, setRoute] = useState<number[]>([]);
  const [cleared, setCleared] = useState(0);
  const [revealTarget, setRevealTarget] = useState(false);
  const round = rounds[roundIndex % rounds.length];
  const target = round.target_sequence ?? lessonPlayable.target_sequence ?? [];
  const targetRows = target.map((id) => rowForHeight(heightFor(id, lessonPlayable, musicLogic)));

  useEffect(() => onProgress(roundIndex, cleared), [roundIndex, cleared]);

  const choose = (column: number, row: number) => {
    const next = [...route];
    next[column] = row;
    setRoute(next);
    setFeedback(next.filter(Number.isFinite).length < target.length ? "继续把后面的路线画完整。" : "路线已经画好，可以先播放自己的路线。");
  };

  const routeIds = () => {
    const tokens = musicLogic.tokens ?? [];
    return route.map((row) => {
      const wantedHeight = 4 - row;
      const nearest = [...tokens].sort(
        (a, b) => Math.abs(Number(a.height_index || 0) - wantedHeight) - Math.abs(Number(b.height_index || 0) - wantedHeight)
      )[0];
      return nearest?.id || target[0];
    });
  };

  const check = () => {
    if (route.filter(Number.isFinite).length < targetRows.length) return setFeedback(feedback.empty || "先把路线画完整。");
    setRevealTarget(true);
    if (route.join("|") !== targetRows.join("|")) return setFeedback(feedback.wrong || "路线还需要调整。");
    const nextCleared = Math.max(cleared, roundIndex + 1);
    setCleared(nextCleared);
    if (roundIndex + 1 >= rounds.length) onComplete();
    setFeedback(roundIndex + 1 >= rounds.length ? feedback.success || "挑战成功。" : "路线正确，小角色出发了。准备下一关！");
  };

  return (
    <>
      <GameControls
        controls={[
          ["听乐句", () => playLessonSequence(target, lessonPlayable, musicLogic) || setFeedback("当前浏览器不能播放声音，请由教师范唱目标音。")],
          ["播放我的路线", () => route.length >= target.length ? playLessonSequence(routeIds(), lessonPlayable, musicLogic) : setFeedback(feedback.empty || "先把路线画完整。")],
          ["检查路线", check],
          [
            "重画",
            () => {
              setRoute([]);
              setRevealTarget(false);
            }
          ],
          [
            "下一关",
            () => {
              setRoundIndex((value) => Math.min(value + 1, rounds.length - 1));
              setRoute([]);
              setRevealTarget(false);
            }
          ]
        ]}
      />
      <div className="path-board">
        <Hud items={[["关卡", round.label || `${roundIndex + 1}/${rounds.length}`], ["需要落点", String(target.length)], ["已通关", `${cleared}/${rounds.length}`]]} />
        <div className="mission-card">
          <strong>本关任务</strong>
          <p>{round.prompt || lessonPlayable.prompt || "听旋律，画路线。"}</p>
        </div>
        <div className="path-legend">
          <span>高</span>
          <span>低</span>
        </div>
        <div className="path-grid" style={{ "--path-columns": Math.max(1, target.length) } as CSSProperties}>
          {Array.from({ length: 5 }).flatMap((_, row) =>
            Array.from({ length: target.length }).map((__, column) => {
              const selected = route[column] === row;
              const correct = revealTarget && targetRows[column] === row;
              return (
                <button
                  key={`${row}-${column}`}
                  className={["path-cell", selected ? "selected" : "", correct ? "correct" : ""].join(" ")}
                  onClick={() => choose(column, row)}
                  aria-label={`第 ${column + 1} 列第 ${row + 1} 行`}
                />
              );
            })
          )}
        </div>
      </div>
    </>
  );
}

function heightFor(id: string, playable: LessonPlayable, musicLogic: MusicLogicContract) {
  const token = musicLogic.tokens?.find((item) => item.id === id);
  if (Number.isFinite(Number(token?.height_index))) return Number(token?.height_index);
  return Math.max(0, Math.round((lessonMidi(id, playable, musicLogic) - 60) / 2));
}

function rowForHeight(height: number) {
  return Math.max(0, 4 - Math.min(4, Number(height || 0)));
}

function BeatGuardianGame({ state, setFeedback, onProgress, onComplete }: RuntimeProps) {
  const configKey = stableConfigKey({ config: state.config ?? {}, workflow: state.workflow ?? {} });
  const config = useMemo(() => mergeMeterEntityExecutionConfig(state, state.config ?? {}), [configKey]);
  const sceneConfigRef = useRef(buildBeatGuardianSceneConfig(config));
  const controllerRef = useRef<BeatGuardianController | null>(null);
  const stageRef = useRef<HTMLDivElement | null>(null);
  const callbacksRef = useRef({ setFeedback, onProgress, onComplete });
  const [snapshot, setSnapshot] = useState<BeatGuardianSnapshot>(() => initialBeatGuardianSnapshot(sceneConfigRef.current));
  const [coverVisible, setCoverVisible] = useState(false);

  useEffect(() => {
    callbacksRef.current = { setFeedback, onProgress, onComplete };
  }, [onComplete, onProgress, setFeedback]);

  useEffect(() => {
    sceneConfigRef.current = buildBeatGuardianSceneConfig(config);
    setSnapshot(initialBeatGuardianSnapshot(sceneConfigRef.current));
    setCoverVisible(false);
  }, [configKey, config]);

  useEffect(() => {
    if (!stageRef.current) return;
    stageRef.current.innerHTML = "";
    const controller = mountBeatGuardianScene(stageRef.current, sceneConfigRef.current, (event: BeatGuardianSceneEvent) => {
      setSnapshot(event.snapshot);
      if (event.message) callbacksRef.current.setFeedback(event.message);
      callbacksRef.current.onProgress(event.snapshot.currentBar, event.snapshot.hits);
      if (event.type === "mission_success") callbacksRef.current.onComplete();
    });
    controllerRef.current = controller;
    return () => {
      controller.destroy();
      controllerRef.current = null;
    };
  }, [configKey]);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.code !== "Space") return;
      event.preventDefault();
      controllerRef.current?.guard();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const start = () => {
    setCoverVisible(false);
    controllerRef.current?.start();
    setFeedback("预备拍");
  };

  const guard = () => {
    controllerRef.current?.guard();
  };

  const reset = () => {
    setCoverVisible(false);
    controllerRef.current?.reset();
    setSnapshot(initialBeatGuardianSnapshot(sceneConfigRef.current));
    setFeedback("准备");
  };
  const targetText = "1";
  const monsterTotal = snapshot.monsterTotal || BEAT_GUARDIAN_MONSTER_TOTAL;
  const monstersCleared = snapshot.monstersCleared || 0;
  const monstersRemaining = snapshot.monstersRemaining ?? Math.max(0, monsterTotal - monstersCleared);
  const dangerLevel = Math.round((snapshot.dangerLevel || 0) * 100);
  const missionLine = `第 ${targetText} 拍充能，用震波清掉靠近的弱拍怪物。`;
  const finished = snapshot.status === "success" || snapshot.status === "failed";
  const energyPercent = Math.round((snapshot.energy / Math.max(1, snapshot.energyMax)) * 100);
  const canStart = snapshot.status === "ready" || finished;
  const transferPrompt = resultTransferPrompt(state, "回到歌曲里，用身体律动预判每小节第 1 拍。");
  const learningEvidence = beatGuardianLearningEvidence(snapshot);
  const teacherObservation = beatGuardianTeacherObservation(snapshot);
  const evidenceMetrics = beatGuardianEvidenceMetrics(snapshot);
  const supportLevel = beatGuardianSupportLevel(sceneConfigRef.current);
  const failReason = snapshot.energy <= 0
    ? "失败条件：能量降到 0。下一次先稳住拍，再等第 1 拍充能。"
    : (snapshot.shieldCracks || 0) >= 6
      ? "失败条件：护盾出现 6 条裂缝。漏掉第 1 拍会让裂缝累积。"
      : snapshot.status === "failed" && monstersRemaining > 0
        ? "失败条件：本轮结束时怪物还没清完。第 1 拍充能会弹开并清掉靠近怪物。"
        : "失败条件：怪物还没清完。第 1 拍充能会弹开并清掉靠近怪物。";
  const feedbackText = snapshot.status === "success"
    ? reasonPrompt(state, "success", "怪物清场：说出你怎么提前预判第 1 拍。")
    : snapshot.status === "failed"
      ? failReason
      : classroomFeedback(snapshot.message, "看怪物靠近，等第 1 拍护盾最亮时同时充能。");
  const stars = starsForScore(snapshot.score + snapshot.maxCombo * 120, snapshot.status === "success");
  const arcadePhase: ArcadeAssetState = snapshot.status === "success" ? "win" : snapshot.status === "failed" ? "miss" : snapshot.combo > 0 ? "hit" : "idle";

  return (
    <ArcadeLevelFlow state={state} phase={arcadePhase}>
    <div className="beat-guardian-runtime arcade" data-engine-target="phaser_2d">
      {coverVisible && snapshot.status === "ready" ? (
        <ArcadeStartOverlay
          state={state}
          title="充能护盾，预判强拍"
          subtitle={missionLine}
          onStart={start}
        />
      ) : null}
      <ArcadeStageHeader state={state} phase={arcadePhase} objective={missionLine} status={guardianStatusLabel(snapshot.status)} />
        <ArcadeHudBar
          state={state}
          level={`充能点 ${targetText}`}
          score={snapshot.score}
          energy={energyPercent}
          combo={`${monstersCleared}/${monsterTotal}`}
          comboLabel="清怪"
        status={guardianStatusLabel(snapshot.status)}
      />
      <header className="arcade-topbar compact-template-topbar">
        <div className="arcade-title-lockup">
          <Text className="eyebrow">律动能量盾</Text>
          <Heading size="6">充能护盾</Heading>
        </div>
        <div className="arcade-mission" aria-label="本局任务">
          <MissionBoardArt state={state} compact />
          <div className="arcade-mission-copy">
            <strong>{missionLine}</strong>
            <span>{snapshot.skinObjective}</span>
          </div>
        </div>
        <Flex className="arcade-stat-strip" gap="2" wrap="wrap">
          <Badge color="amber" variant="solid">第 {targetText} 拍</Badge>
          <Badge color={supportLevel.tone} variant="soft">{supportLevel.label}</Badge>
          <Badge color={monstersRemaining <= 0 ? "green" : "amber"} variant="soft">怪物 {monstersCleared}/{monsterTotal}</Badge>
          <Badge color={energyPercent <= 28 ? "ruby" : "teal"} variant="soft">能量 {energyPercent}%</Badge>
          <Badge color={snapshot.shieldCracks ? "ruby" : "teal"} variant="soft">裂缝 {snapshot.shieldCracks || 0}</Badge>
          <Badge color={dangerLevel >= 70 ? "ruby" : dangerLevel >= 42 ? "amber" : "teal"} variant="soft">危险 {dangerLevel}%</Badge>
          <Badge color="blue" variant="soft">{snapshot.audioLabel}</Badge>
        </Flex>
      </header>

      <div
        className="beat-phaser-shell arcade-stage-card"
        data-engine="phaser_2d"
        data-scene="beat_guardian_scene"
        data-arcade-hud="true"
      >
        <div ref={stageRef} className="beat-phaser-stage" aria-label="充能护盾 Phaser 游戏舞台" />
      </div>

      <div className="arcade-bottom-hud">
        <Card className="guardian-feedback-card compact arcade-feedback">
          <Flex align="center" justify="between" gap="3" wrap="wrap">
            <Box>
              <Text className="eyebrow">反馈</Text>
              <Text as="p" size="5" weight="bold">{feedbackText}</Text>
            </Box>
            <Badge color={snapshot.status === "success" ? "green" : snapshot.status === "failed" ? "ruby" : "teal"} variant="solid">
              {guardianStatusLabel(snapshot.status)}
            </Badge>
          </Flex>
        </Card>
        <Card className="guardian-evidence-card">
          <div className="guardian-evidence-icon" aria-hidden="true">
            <ClipboardCheck size={18} />
          </div>
          <Box>
            <Text className="eyebrow">音乐依据</Text>
            <Text as="p" weight="bold">{learningEvidence}</Text>
            <Text as="span" className="guardian-evidence-note">{teacherObservation}</Text>
            <div className="guardian-evidence-grid" aria-label="节拍守卫观察指标">
              {evidenceMetrics.map((metric) => (
                <div key={metric.label} className="guardian-evidence-metric" data-tone={metric.tone}>
                  <strong>{metric.value}</strong>
                  <span>{metric.label}</span>
                </div>
              ))}
            </div>
          </Box>
        </Card>
        <Flex className="arcade-actions" gap="2" wrap="wrap">
          <Button className="game-action primary" size="3" onClick={start} disabled={!canStart && snapshot.status !== "ready"}>
            <Volume2 size={16} />
            开始
          </Button>
          <Button className="game-action primary guard-button" size="4" onClick={guard}>
            <Sparkles size={18} />
            充能
          </Button>
          <Button className="game-action" size="3" variant="soft" onClick={reset}>
            <RotateCcw size={16} />
            重试
          </Button>
        </Flex>
      </div>

      {finished ? (
        <ArcadeResultPanel
          state={state}
          success={snapshot.status === "success"}
          title={snapshot.status === "success" ? "怪物清场，护盾稳定！" : "这次哪里失稳了？"}
          prompt={snapshot.status === "success" ? `${learningEvidence} ${transferPrompt}` : `${teacherObservation} ${failReason}`}
          score={snapshot.score}
          stars={stars}
          badges={[["清除怪物", `${monstersCleared}/${monsterTotal}`], ["最高连击", String(snapshot.maxCombo)], ["支架", supportLevel.label], ["充能拍", targetText]]}
          onReplay={reset}
        />
      ) : null}
      <details className="guardian-teacher-details arcade-teacher-details">
        <summary>教师提示</summary>
        <p>{teacherObservation} 当前目标：{snapshot.skinObjective}；支架状态：{supportLevel.description}。</p>
      </details>
    </div>
    </ArcadeLevelFlow>
  );
}

function initialBeatGuardianSnapshot(config: ReturnType<typeof buildBeatGuardianSceneConfig>): BeatGuardianSnapshot {
  return {
    status: "ready",
    phase: "ready",
    currentBeat: 0,
    currentBar: 0,
    beatsPerBar: Number(config.beats_per_bar || 4),
    missionBars: Number(config.mission_duration_bars || 4),
    targetBeats: [1],
    hits: 0,
    misses: 0,
    falseAlarms: 0,
    combo: 0,
    maxCombo: 0,
    requiredCombo: Number(config.required_combo || 4),
    maxMistakes: Number(config.max_mistakes || 3),
    score: 0,
    energy: Number(config.energy_max || 100),
    energyMax: Number(config.energy_max || 100),
    countInRemaining: Number(config.count_in_beats || 0),
    progress: 0,
    audioMode: config.audio_mode || "internal_meter",
    audioLabel: config.lesson_audio_sync?.audio_url ? config.lesson_audio_sync.segment_label || "作品片段" : "强弱拍鼓点",
    skinObjective: config.skin_objective || "维持护盾",
    shieldCracks: 0,
    pulsePhase: 0,
    monstersRemaining: BEAT_GUARDIAN_MONSTER_TOTAL,
    monstersCleared: 0,
    monsterTotal: BEAT_GUARDIAN_MONSTER_TOTAL,
    dangerLevel: 0,
    judgementCounts: {},
    message: "准备"
  };
}

function beatGuardianLearningEvidence(snapshot: BeatGuardianSnapshot) {
  const counts = snapshot.judgementCounts ?? {};
  const accurate = Number(counts.perfect || 0) + Number(counts.good || 0);
  const early = Number(counts.early || 0) + Number(counts.too_early || 0);
  const late = Number(counts.late || 0);
  const missed = Number(counts.missed || 0);
  const wrong = Number(counts.wrong || 0);
  if (snapshot.status === "ready") return "先听稳定拍，等第 1 拍到来前在心里预备。";
  if (accurate >= Math.max(2, snapshot.requiredCombo)) return "能连续预判第 1 拍，动作和强拍基本同时发生。";
  if (missed > late && missed >= early) return "第 1 拍漏充偏多，需要在小节开始前先准备动作。";
  if (late > early && late > 0) return "常在听到强拍后补按，可以把动作提前到强拍瞬间。";
  if (early > 0) return "有抢拍倾向，需要先稳住周期，再等第 1 拍。";
  if (wrong > 0) return "弱拍误按偏多，要把弱拍当作蓄势时间。";
  return "正在建立稳定拍和强拍预判，请继续听小节周期。";
}

function beatGuardianTeacherObservation(snapshot: BeatGuardianSnapshot) {
  const counts = snapshot.judgementCounts ?? {};
  const accurate = Number(counts.perfect || 0) + Number(counts.good || 0);
  const errors = Number(counts.early || 0) + Number(counts.late || 0) + Number(counts.wrong || 0) + Number(counts.missed || 0);
  if (snapshot.status === "success") {
    return `教师观察：学生完成 ${accurate} 次有效强拍充能，最高连续 ${snapshot.maxCombo} 次。`;
  }
  if (snapshot.status === "failed") {
    return `教师观察：本轮出现 ${errors} 次节拍失稳，可让学生先口数或身体律动再挑战。`;
  }
  return `教师观察：当前有效充能 ${accurate} 次，留意是否靠听觉预判而不是只看画面。`;
}

function beatGuardianEvidenceMetrics(snapshot: BeatGuardianSnapshot): Array<{
  label: string;
  value: string;
  tone: "good" | "watch" | "alert";
}> {
  const counts = snapshot.judgementCounts ?? {};
  const accurate = Number(counts.perfect || 0) + Number(counts.good || 0);
  const early = Number(counts.early || 0) + Number(counts.too_early || 0);
  const late = Number(counts.late || 0);
  const missed = Number(counts.missed || 0);
  const wrong = Number(counts.wrong || 0);
  return [
    { label: "有效强拍", value: String(accurate), tone: accurate >= Math.max(1, snapshot.requiredCombo) ? "good" : "watch" },
    { label: "抢拍", value: String(early), tone: early ? "alert" : "good" },
    { label: "拖拍", value: String(late), tone: late ? "alert" : "good" },
    { label: "漏强拍", value: String(missed), tone: missed ? "alert" : "good" },
    { label: "弱拍误按", value: String(wrong), tone: wrong ? "alert" : "good" }
  ];
}

function beatGuardianSupportLevel(config: ReturnType<typeof buildBeatGuardianSceneConfig>): {
  label: string;
  description: string;
  tone: "green" | "blue" | "amber";
} {
  if (!config.show_beat_track && !config.visual_beat_hint) {
    return { label: "听觉挑战", description: "拍点轨道与同步亮点已撤掉，主要依靠听觉和身体预判。", tone: "amber" };
  }
  if (!config.show_weak_beat_hint || !config.visual_beat_hint) {
    return { label: "半支架", description: "保留关键强拍支架，弱拍或同步提示已弱化。", tone: "blue" };
  }
  return { label: "全支架", description: "保留强拍、弱拍和视觉拍点提示，适合入门建立周期感。", tone: "green" };
}

function shortStudentFeedback(message: string) {
  return (message || "准备").slice(0, 8);
}

function classroomFeedback(message: string, fallback: string) {
  const text = String(message || "").trim();
  return text || fallback;
}

function buildRhythmEchoEvidence(snapshot: RhythmEchoSnapshot, feedbackText: string, transferPrompt: string): {
  focus: string;
  nextStep: string;
  metrics: Array<{ label: string; value: string; tone: "good" | "watch" | "alert" }>;
} {
  const accuracy = Math.round(snapshot.accuracy * 100);
  const progress = Math.round(snapshot.progress * 100);
  const focus = snapshot.status === "success"
    ? "拍点和长短基本对齐"
    : snapshot.status === "failed"
      ? "复盘波形错位处"
      : feedbackText;
  const nextStep = snapshot.status === "success"
    ? transferPrompt
    : snapshot.status === "failed"
      ? "先复听目标节奏，再对照上下两条节奏轨道。"
      : "先听完整示范，再凭记忆拍回相同长短。";

  return {
    focus,
    nextStep,
    metrics: [
      { label: "准确率", value: `${accuracy}%`, tone: accuracy >= 80 ? "good" : accuracy >= 50 ? "watch" : "alert" },
      { label: "进度", value: `${progress}%`, tone: progress >= 80 ? "good" : "watch" },
      { label: "连击", value: String(snapshot.maxCombo), tone: snapshot.maxCombo >= Math.max(2, Math.ceil(snapshot.totalHits / 2)) ? "good" : "watch" },
      { label: "漏拍", value: String(snapshot.misses), tone: snapshot.misses ? "alert" : "good" },
      { label: "多拍", value: String(snapshot.extras), tone: snapshot.extras ? "alert" : "good" }
    ]
  };
}

function guardianStatusLabel(status: BeatGuardianSnapshot["status"]) {
  return {
    ready: "待开始",
    count_in: "预备拍",
    playing: "挑战中",
    success: "通关",
    failed: "复盘后重试"
  }[status];
}

function PitchLadderGame({ state, setFeedback, onProgress, onComplete }: RuntimeProps) {
  const configKey = stableConfigKey({ config: state.config ?? {}, workflow: state.workflow ?? {} });
  const config = useMemo(() => mergePitchEntityExecutionConfig(state, state.config ?? {}), [configKey]);
  const sceneConfigRef = useRef(buildPitchLadderSceneConfig(config));
  const controllerRef = useRef<PitchLadderController | null>(null);
  const stageRef = useRef<HTMLDivElement | null>(null);
  const touchStartRef = useRef<{ x: number; y: number } | null>(null);
  const pitchAudioRef = useRef(createMusicGameAudioFacade());
  const callbacksRef = useRef({ setFeedback, onProgress, onComplete });
  const [snapshot, setSnapshot] = useState<PitchLadderSnapshot>(() => initialPitchLadderSnapshot(sceneConfigRef.current));
  const [coverVisible, setCoverVisible] = useState(false);
  const [selectedDirection, setSelectedDirection] = useState<VoiceDirection | null>(null);
  const [voiceState, setVoiceState] = useState<"idle" | "capturing" | "detected" | "retry" | "fallback">("idle");
  const [voiceResult, setVoiceResult] = useState<VoicePitchResult | null>(null);
  const micEnabled = config.mic_assist_enabled !== false;

  useEffect(() => {
    callbacksRef.current = { setFeedback, onProgress, onComplete };
  }, [onComplete, onProgress, setFeedback]);

  useEffect(() => {
    sceneConfigRef.current = buildPitchLadderSceneConfig(config);
    setSnapshot(initialPitchLadderSnapshot(sceneConfigRef.current));
    setCoverVisible(false);
    setSelectedDirection(null);
    setVoiceState("idle");
    setVoiceResult(null);
  }, [config]);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      const action = resolvePitchLadderKeyAction(event.code);
      if (!action || event.repeat) return;
      event.preventDefault();
      const direction = pitchDirectionFromInputAction(action);
      if (direction) {
        selectDirection(direction);
        return;
      }
      if (action === "listen") listen();
      if (action === "voice_check") void startVoiceCheck();
      if (action === "teacher_confirm") confirmSingBackFallback();
      if (action === "reset") reset();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  });

  useEffect(() => {
    if (!stageRef.current) return;
    stageRef.current.innerHTML = "";
    const controller = mountPitchLadderScene(stageRef.current, sceneConfigRef.current, (event: PitchLadderSceneEvent) => {
      setSnapshot(event.snapshot);
      if (event.type === "preview_direction") {
        const choice = event.snapshot.selected[0];
        setSelectedDirection(isVoiceDirection(choice) ? choice : null);
        setVoiceState("idle");
        setVoiceResult(null);
      }
      if (event.type === "round_success" || event.type === "mission_success" || event.type === "reset") {
        setSelectedDirection(null);
        setVoiceState("idle");
        setVoiceResult(null);
      }
      if (event.message) callbacksRef.current.setFeedback(event.message);
      callbacksRef.current.onProgress(event.snapshot.currentRound, event.snapshot.cleared);
      if (event.type === "mission_success") callbacksRef.current.onComplete();
    });
    controllerRef.current = controller;
    return () => {
      controller.destroy();
      controllerRef.current = null;
    };
  }, [configKey]);

  const listen = () => {
    setCoverVisible(false);
    setSelectedDirection(null);
    setVoiceState("idle");
    setVoiceResult(null);
    controllerRef.current?.listen();
    pitchAudioRef.current.playPitchPrompt(pitchOffsetsForSnapshot(snapshot)) || setFeedback("当前浏览器不能播放声音，请由教师范唱目标音。");
  };

  const requirePitchListening = () => {
    if (snapshot.status !== "ready") return false;
    setFeedback(evidence.nextAction);
    return true;
  };

  const selectDirection = (direction: VoiceDirection) => {
    if (requirePitchListening()) return;
    setCoverVisible(false);
    setSelectedDirection(direction);
    setVoiceState("idle");
    setVoiceResult(null);
    controllerRef.current?.previewDirection(direction);
    setFeedback(`已选${voiceDirectionLabel(direction)}，现在唱/哼出这个方向。`);
  };

  const choosePitchNode = (note: string) => {
    if (requirePitchListening()) return;
    controllerRef.current?.chooseNode(note);
  };

  const confirmPitchSingBack = () => {
    if (requirePitchListening()) return;
    if (snapshot.status !== "round_clear") {
      setFeedback("先走对路线，再唱回确认。");
      return;
    }
    setFeedback("教师确认唱回，进入下一条路线。");
    pitchAudioRef.current.playHit();
    controllerRef.current?.confirmSingBack();
  };

  const startVoiceCheck = async () => {
    if (requirePitchListening()) return;
    if (!selectedDirection) {
      setFeedback("先听音，再选平台。");
      return;
    }
    if (!micEnabled) {
      setVoiceState("fallback");
      setFeedback("麦克风入口已关闭，可由教师确认唱回。");
      return;
    }
    setVoiceState("capturing");
    setVoiceResult(null);
    controllerRef.current?.startVoiceCharge();
    setFeedback("唱或哼两秒：让声音走出你选的方向。");
    const result = await captureVoicePitchDirection({
      onUpdate: (update) => controllerRef.current?.updateVoiceMeter(update.volumeLevel, update.pitchTrace)
    });
    setVoiceResult(result);
    controllerRef.current?.updateVoiceMeter(result.volumeLevel, result.pitchTrace);
    if (result.status === "ok" && result.direction) {
      setVoiceState("detected");
      setFeedback(`识别到：${voiceDirectionLabel(result.direction)}`);
      pitchAudioRef.current.playHit();
      controllerRef.current?.resolveVoiceAttempt(selectedDirection, result.direction);
      return;
    }
    setVoiceState(result.status === "blocked" || result.status === "unsupported" ? "fallback" : "retry");
    const message = voiceResultMessage(result.status);
    setFeedback(message);
    pitchAudioRef.current.playMiss();
    controllerRef.current?.voiceRetry(message);
  };

  const confirmSingBackFallback = () => {
    if (requirePitchListening()) return;
    if (!selectedDirection) {
      setFeedback("先完成高低听辨，再由教师确认唱回。");
      return;
    }
    setVoiceState("fallback");
    setVoiceResult({
      status: "ok",
      direction: selectedDirection,
      confidence: 1,
      volumeLevel: 1,
      stability: 1,
      pitchTrace: []
    });
    setFeedback("教师确认唱回，开始跳跃判定。");
    pitchAudioRef.current.playHit();
    controllerRef.current?.resolveVoiceAttempt(selectedDirection, selectedDirection);
  };

  const reset = () => {
    setCoverVisible(false);
    controllerRef.current?.reset();
    setSnapshot(initialPitchLadderSnapshot(sceneConfigRef.current));
    setSelectedDirection(null);
    setVoiceState("idle");
    setVoiceResult(null);
    setFeedback("听音");
  };

  const finished = snapshot.status === "mission_success" || snapshot.status === "mission_failed";
  const energyPercent = Math.round((snapshot.energy / Math.max(1, snapshot.energyMax)) * 100);
  const routeNodes = sceneConfigRef.current.route_nodes || [];
  const transferPrompt = resultTransferPrompt(state, "唱回这组音，并说出旋律往哪里走。");
  const feedbackText = snapshot.status === "mission_success"
    ? reasonPrompt(state, "success", "通关！唱回这组音。")
    : snapshot.status === "mission_failed"
      ? reasonPrompt(state, "wrong", "能量空了：再听高低方向。")
      : classroomFeedback(snapshot.message, "听音，点平台。");
  const pitchScore = Math.round((snapshot.cleared / Math.max(1, snapshot.totalRounds)) * 1000 - snapshot.mistakes * 120);
  const pitchStars = starsForPercent(Math.round((snapshot.cleared / Math.max(1, snapshot.totalRounds)) * 100), snapshot.status === "mission_success");
  const arcadePhase: ArcadeAssetState =
    snapshot.status === "mission_success" ? "win" : snapshot.status === "mission_failed" ? "miss" : snapshot.rewardsCollected > 0 ? "hit" : "idle";
  const evidence = buildPitchEvidenceSummary(snapshot);
  const pitchActionLocked = snapshot.status === "ready" || snapshot.status === "round_clear" || finished;
  const canConfirmPitchSingBack = snapshot.status === "round_clear";
  useEffect(() => {
    if (snapshot.status === "round_clear") pitchAudioRef.current.playReward();
    if (snapshot.status === "mission_failed") pitchAudioRef.current.playMiss();
  }, [snapshot.status, snapshot.rewardsCollected]);
  const voiceStatusText = voiceResult?.status === "ok" && voiceResult.direction
    ? `声音：${voiceDirectionLabel(voiceResult.direction)}`
    : selectedDirection
      ? `听辨：${voiceDirectionLabel(selectedDirection)}`
      : "先听音选平台";

  return (
    <ArcadeLevelFlow state={state} phase={arcadePhase}>
    <div className="pitch-ladder-runtime game-first-map adventure-climb-runtime" data-engine-target="phaser_2d" data-scene="pitch_ladder_scene">
      {coverVisible && snapshot.status === "ready" ? (
        <ArcadeStartOverlay
          state={state}
          title="爬上音高路线"
          subtitle={pitchAdventureObjective(snapshot.currentMode)}
          actionLabel="听音出发"
          onStart={listen}
        />
      ) : null}
      <ArcadeHudBar
        state={state}
        level={`第 ${Math.min(snapshot.currentRound + 1, snapshot.totalRounds)} 关`}
        energy={energyPercent}
        combo={`${snapshot.rewardsCollected}/${snapshot.rewardTotal}`}
      />

      <div
        className="pitch-phaser-shell"
        data-engine="phaser_2d"
        data-map-hud="true"
        onTouchStart={(event) => {
          const touch = event.changedTouches[0];
          touchStartRef.current = touch ? { x: touch.clientX, y: touch.clientY } : null;
        }}
        onTouchEnd={(event) => {
          const start = touchStartRef.current;
          const touch = event.changedTouches[0];
          touchStartRef.current = null;
          if (!start || !touch) return;
          const action = resolvePitchLadderSwipeAction(touch.clientX - start.x, touch.clientY - start.y);
          const direction = action ? pitchDirectionFromInputAction(action) : null;
          if (direction) selectDirection(direction);
        }}
      >
        <div ref={stageRef} className="pitch-phaser-stage" aria-label="音高爬梯 Phaser 地图舞台" />
      </div>

      <div className="pitch-map-hud adventure-map-hud">
        <Card className="pitch-feedback-card">
          <Flex align="center" justify="between" gap="3" wrap="wrap">
            <Box>
              <Text className="eyebrow">当前听辨</Text>
              <Text as="p" size="5" weight="bold">{feedbackText}</Text>
            </Box>
            <Badge color={snapshot.status === "mission_failed" ? "ruby" : snapshot.status === "mission_success" ? "green" : "teal"} variant="solid">
              {pitchStatusLabel(snapshot.status)}
            </Badge>
          </Flex>
        </Card>
        <div className="pitch-evidence-card" aria-label="音高学习证据">
          <div className="pitch-evidence-grid">
            <div>
              <span>目标音列</span>
              <strong>{evidence.target}</strong>
            </div>
            <div>
              <span>学生操作</span>
              <strong>{evidence.studentAction}</strong>
            </div>
            <div>
              <span>下一步</span>
              <strong>{evidence.nextAction}</strong>
            </div>
          </div>
          <div className="pitch-process-track" aria-label="课堂过程轨迹">
            {evidence.process.map((step) => (
              <span key={step.id} className={`pitch-process-step is-${step.state}`}>
                <em>{step.label}</em>
                <strong>{step.detail}</strong>
              </span>
            ))}
          </div>
        </div>
        <div className="pitch-map-actions" aria-label="音高爬梯课堂操作台">
          <div className="pitch-action-cluster is-listen">
            <span className="pitch-action-caption">1 听</span>
            <Button className="game-action primary" size="3" onClick={listen}>
              <Volume2 size={16} />
              听音
            </Button>
          </div>
          <div className={`pitch-action-cluster is-choose mode-${snapshot.currentMode}`}>
            <span className="pitch-action-caption">{snapshot.currentMode === "direction_pair" ? "2 辨" : "2 走"}</span>
            {snapshot.currentMode === "direction_pair" ? [
                ["higher", "↑", "高"],
                ["same", "—", "平"],
                ["lower", "↓", "低"]
              ].map(([value, symbol, label]) => (
                <Button
                  key={value}
                  className="game-action pitch-choice"
                  variant={selectedDirection === value ? "solid" : "soft"}
                  onClick={() => selectDirection(value as VoiceDirection)}
                  disabled={pitchActionLocked}
                >
                  <strong>{symbol}</strong> {label}
                </Button>
              )) : (
              routeNodes.map((node) => (
                <Button
                  key={node.note}
                  className="game-action pitch-node-choice"
                  variant={snapshot.selected.includes(node.note) ? "solid" : "soft"}
                  onClick={() => choosePitchNode(node.note)}
                  disabled={pitchActionLocked}
                >
                  {noteLabel(node.note)}
                </Button>
              ))
            )}
          </div>
          <div className="pitch-action-cluster is-confirm">
            <span className="pitch-action-caption">3 唱</span>
            {snapshot.currentMode === "direction_pair" ? (
              <>
                <Button className="game-action primary pitch-voice-action" size="3" onClick={startVoiceCheck} disabled={voiceState === "capturing" || pitchActionLocked}>
                  {voiceState === "capturing" ? "识别" : "唱"}
                </Button>
                <Button className="game-action" size="3" variant="soft" onClick={confirmSingBackFallback} disabled={pitchActionLocked}>
                  确认
                </Button>
              </>
            ) : (
              <Button className="game-action primary pitch-singback-confirm" size="3" onClick={confirmPitchSingBack} disabled={!canConfirmPitchSingBack}>
                唱回确认
              </Button>
            )}
          </div>
          <div className="pitch-action-cluster is-reset">
            <span className="pitch-action-caption">修正</span>
            <Button className="game-action" size="3" variant="soft" onClick={reset}>
              <RotateCcw size={16} />
              重来
            </Button>
          </div>
        </div>
        {snapshot.currentMode === "direction_pair" && (selectedDirection || voiceState !== "idle" || voiceResult) ? (
          <div className={`pitch-voice-panel is-${voiceState}`}>
            <span>{voiceStatusText}</span>
            <span>音量 {Math.round((voiceResult?.volumeLevel ?? 0) * 100)}%</span>
          </div>
        ) : null}
      </div>

      {finished ? (
        <ArcadeResultPanel
          state={state}
          success={snapshot.status === "mission_success"}
          title={snapshot.status === "mission_failed" ? "路线断了，再听方向" : "旋律路线点亮"}
          prompt={transferPrompt}
          score={pitchScore}
          stars={pitchStars}
          badges={[["目标", evidence.target], ["操作", evidence.studentAction], ["出口", evidence.checkpoint], ["失误", `${snapshot.mistakes}/${snapshot.mistakeLimit}`]]}
          onReplay={reset}
          nextLabel="下一条路线"
        />
      ) : null}
      <details className="guardian-teacher-details pitch-teacher-details">
        <summary>教师提示</summary>
        <p><strong>{evidence.nextAction}：</strong>{evidence.teacherCheckpoint}</p>
        <p>{evidence.review}</p>
      </details>
    </div>
    </ArcadeLevelFlow>
  );
}

function initialPitchLadderSnapshot(config: ReturnType<typeof buildPitchLadderSceneConfig>): PitchLadderSnapshot {
  const rounds = config.pitch_rounds || [];
  const firstRound = rounds[0] || {};
  const audioMode = config.audio_mode || "hybrid";
  return {
    status: "ready",
    currentRound: 0,
    totalRounds: rounds.length || 1,
    currentMode: config.current_mode || "direction_pair",
    sequence: (firstRound.sequence || []).map(String),
    labels: (firstRound.labels || firstRound.sequence || []).map(String),
    answer: Array.isArray(firstRound.answer) ? firstRound.answer.map(String) : String(firstRound.answer || ""),
    selected: [],
    progress: 0,
    cleared: 0,
    rewardsCollected: 0,
    rewardTotal: Number(config.reward_model?.tokens_required || rounds.length || 1),
    rewardTokenName: String(config.reward_model?.token_name || "旋律宝石"),
    mistakes: 0,
    mistakeLimit: Number(config.mistake_limit || 3),
    energy: Number(config.energy_max || 100),
    energyMax: Number(config.energy_max || 100),
    skinObjective: pitchSkinObjective(String(config.skin_play_mode || "mountain")),
    audioMode,
    audioLabel: audioMode === "lesson_audio" ? "作品片段" : "内置音高",
    message: "听音"
  };
}

function pitchOffsetsForSnapshot(snapshot: PitchLadderSnapshot) {
  const offsets = snapshot.sequence.map((note) => pitchMidiOffset(note));
  return offsets.length ? offsets : [0, 2];
}

function pitchMidiOffset(note: string) {
  return resolvePitchToken(note)?.semitone ?? 0;
}

function pitchModeLabel(mode: PitchLadderSnapshot["currentMode"]) {
  return {
    direction_pair: "听方向",
    single_solfege: "找音名",
    melody_path: "走旋律"
  }[mode];
}

function pitchAdventureObjective(mode: PitchLadderSnapshot["currentMode"]) {
  return {
    direction_pair: "听方向，判断高低",
    single_solfege: "听目标音，找到音名",
    melody_path: "听短旋律，走出路线"
  }[mode];
}

function pitchStatusLabel(status: PitchLadderSnapshot["status"]) {
  return {
    ready: "待开始",
    listening: "听音中",
    playing: "走路线",
    round_clear: "唱回",
    mission_success: "通关",
    mission_failed: "复盘"
  }[status];
}

function pitchSkinObjective(playMode: string) {
  return {
    mountain: "音高山路",
    cloud: "云梯升空",
    bamboo: "竹节爬梯",
    lantern: "灯塔点灯"
  }[playMode] ?? "音高路线";
}

function isVoiceDirection(value: string | undefined): value is VoiceDirection {
  return value === "higher" || value === "same" || value === "lower";
}

function voiceDirectionLabel(direction: VoiceDirection) {
  return {
    higher: "更高",
    same: "一样高",
    lower: "更低"
  }[direction];
}

function voiceResultMessage(status: VoicePitchResult["status"]) {
  return {
    ok: "声音方向已识别",
    too_quiet: "声音太轻，再唱响一点",
    too_short: "时间太短，再唱长一点",
    unstable: "音高不稳，再唱一次",
    blocked: "麦克风不可用，可由教师确认",
    unsupported: "浏览器不支持麦克风识别，可由教师确认"
  }[status];
}

function RhythmEchoGame({ state, setFeedback, onProgress, onComplete }: RuntimeProps) {
  const configKey = stableConfigKey({ config: state.config ?? {}, workflow: state.workflow ?? {} });
  const config = useMemo(() => mergeRhythmEntityExecutionConfig(state, state.config ?? {}), [configKey]);
  const [activeRound, setActiveRound] = useState(1);
  const sceneConfigRef = useRef(buildRhythmEchoSceneConfig({ ...config, active_round: activeRound }));
  const controllerRef = useRef<RhythmEchoController | null>(null);
  const stageRef = useRef<HTMLDivElement | null>(null);
  const callbacksRef = useRef({ setFeedback, onProgress, onComplete });
  const [snapshot, setSnapshot] = useState<RhythmEchoSnapshot>(() => initialRhythmEchoSnapshot(sceneConfigRef.current));
  const [tutorialOpen, setTutorialOpen] = useState(true);

  useEffect(() => {
    callbacksRef.current = { setFeedback, onProgress, onComplete };
  }, [onComplete, onProgress, setFeedback]);

  useEffect(() => {
    sceneConfigRef.current = buildRhythmEchoSceneConfig({ ...config, active_round: activeRound });
    setSnapshot(initialRhythmEchoSnapshot(sceneConfigRef.current));
  }, [activeRound, configKey, config]);

  useEffect(() => {
    if (!stageRef.current) return;
    stageRef.current.innerHTML = "";
    const controller = mountRhythmEchoScene(stageRef.current, sceneConfigRef.current, (event: RhythmEchoSceneEvent) => {
      setSnapshot(event.snapshot);
      if (event.message) callbacksRef.current.setFeedback(event.message);
      callbacksRef.current.onProgress(event.snapshot.currentRound, event.snapshot.cleared);
      if (event.type === "mission_success" && event.snapshot.cleared >= event.snapshot.totalRounds) callbacksRef.current.onComplete();
    });
    controllerRef.current = controller;
    return () => {
      controller.destroy();
      controllerRef.current = null;
    };
  }, [activeRound, configKey]);

  useEffect(() => {
    let pressed = false;
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.code !== "Space") return;
      event.preventDefault();
      if (tutorialOpen) return;
      if (pressed) return;
      pressed = true;
      controllerRef.current?.pressStart();
    };
    const handleKeyUp = (event: KeyboardEvent) => {
      if (event.code !== "Space") return;
      event.preventDefault();
      if (tutorialOpen) return;
      pressed = false;
      controllerRef.current?.pressEnd();
    };
    window.addEventListener("keydown", handleKeyDown);
    window.addEventListener("keyup", handleKeyUp);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
      window.removeEventListener("keyup", handleKeyUp);
    };
  }, [tutorialOpen]);

  const prepareOrPlayDemo = async () => {
    if (!snapshot.audioReady) {
      await controllerRef.current?.prepareAudio();
      return;
    }
    controllerRef.current?.demo();
    setFeedback("听示范");
  };

  const start = () => {
    controllerRef.current?.start();
    setFeedback(snapshot.audioReady ? "盲听复刻" : "先准备采样音色");
  };

  const beginTransmit = () => {
    controllerRef.current?.pressStart();
  };

  const endTransmit = () => {
    controllerRef.current?.pressEnd();
  };

  const reset = () => {
    controllerRef.current?.reset();
    setFeedback("准备");
  };

  const advanceRound = () => {
    if (snapshot.status !== "success") {
      reset();
      return;
    }
    setActiveRound((value) => Math.min(value + 1, Math.max(1, snapshot.totalRounds)));
    setTutorialOpen(true);
    setFeedback(activeRound >= snapshot.totalRounds ? "全部节奏关卡完成" : "进入下一关");
  };

  const finished = snapshot.status === "success" || snapshot.status === "failed";
  const energyPercent = Math.round((snapshot.energy / Math.max(1, snapshot.energyMax)) * 100);
  const accuracyPercent = Math.round(snapshot.accuracy * 100);
  const canStart = snapshot.status === "ready" || finished;
  const transferPrompt = resultTransferPrompt(state, "用口读或身体律动再表现一次节奏型。");
  const feedbackText = snapshot.status === "success"
    ? reasonPrompt(state, "success", "节奏复刻成功：说出它的长短和疏密特点。")
    : snapshot.status === "failed"
      ? reasonPrompt(state, "wrong_order", "顺序错了：再听长短和休止的位置。")
      : classroomFeedback(snapshot.message, "先完整听，再拍回来。");
  const rhythmEvidence = buildRhythmEchoEvidence(snapshot, feedbackText, transferPrompt);
  const rhythmStars = starsForPercent(accuracyPercent, snapshot.status === "success");
  const arcadePhase: ArcadeAssetState = snapshot.status === "success" ? "win" : snapshot.status === "failed" ? "miss" : snapshot.combo > 0 ? "hit" : "idle";
  const audioButtonLabel = snapshot.audioPreparing
    ? "准备中..."
    : snapshot.audioReady
      ? "听示范"
      : snapshot.audioError
        ? "重试音频"
        : "准备音频";
  const audioHint = snapshot.audioReady
    ? "SoundFont 木琴采样已就绪"
    : snapshot.audioError || "首次点击会加载采样，成功后才开始游戏";
  const referenceLabel = snapshot.durationLabel || snapshot.patternLabel || "短-短";
  const requiredPercent = Math.round(Number(sceneConfigRef.current.required_accuracy || 0.8) * 100);
  const closeTutorial = () => {
    setTutorialOpen(false);
    window.requestAnimationFrame(() => {
      stageRef.current?.scrollIntoView({ block: "start", behavior: "smooth" });
    });
  };

  return (
    <ArcadeLevelFlow state={state} phase={arcadePhase}>
    <div className="rhythm-echo-runtime arcade" data-engine-target="phaser_2d">
      <RhythmEchoTutorialOverlay
        open={tutorialOpen}
        totalHits={snapshot.totalHits}
        referenceLabel={referenceLabel}
        requiredPercent={requiredPercent}
        audioReady={snapshot.audioReady}
        onClose={closeTutorial}
      />
      <div
        className="rhythm-phaser-shell rhythm-arcade-stage-card"
        data-engine="phaser_2d"
        data-scene="rhythm_echo_scene"
        data-arcade-hud="true"
      >
        <div ref={stageRef} className="rhythm-phaser-stage" aria-label="节奏复刻 Phaser 游戏舞台" />
        <RhythmEchoStagePartner state={state} phase={arcadePhase} />
      </div>

      <div className="rhythm-arcade-bottom-hud rhythm-classroom-console">
        <Card className={`guardian-feedback-card compact arcade-feedback rhythm-feedback ${snapshot.audioError ? "audio-error" : ""}`}>
          <div className="rhythm-feedback-header">
            <Text className="eyebrow">课堂反馈</Text>
            <Badge color={snapshot.status === "success" ? "green" : snapshot.status === "failed" ? "ruby" : "teal"} variant="solid">
              {rhythmStatusLabel(snapshot.status)}
            </Badge>
          </div>
          <Text as="p" className="rhythm-feedback-main" weight="bold">{feedbackText}</Text>
          <div className="rhythm-feedback-steps" aria-label="节奏复刻学习路径">
            <span className={snapshot.audioReady ? "is-done" : ""}>听示范</span>
            <span className={snapshot.status === "recording" || finished ? "is-active" : ""}>凭记忆复刻</span>
            <span className={finished ? "is-done" : ""}>看波形复盘</span>
          </div>
          <Text as="p" size="2" className="rhythm-audio-hint">{audioHint}</Text>
        </Card>

        <Card className="rhythm-learning-evidence" aria-label="节奏复刻学习证据">
          <div>
            <Text className="eyebrow">学习证据</Text>
            <strong>{rhythmEvidence.focus}</strong>
            <span>{rhythmEvidence.nextStep}</span>
          </div>
          <div className="rhythm-evidence-grid">
            {rhythmEvidence.metrics.map((metric) => (
              <span key={metric.label} data-tone={metric.tone}>
                <strong>{metric.value}</strong>
                {metric.label}
              </span>
            ))}
          </div>
        </Card>

        <Flex className="rhythm-arcade-actions rhythm-classroom-actions" gap="2" wrap="wrap">
          <Button className="game-action rhythm-help-action" size="3" variant="soft" onClick={() => setTutorialOpen(true)} aria-label="打开玩法和通关标准">
            <Search size={16} />
            标准
          </Button>
          <Button
            className={`game-action rhythm-audio-action ${snapshot.audioReady ? "is-ready" : ""}`}
            size="3"
            variant={snapshot.audioReady ? "soft" : "solid"}
            onClick={prepareOrPlayDemo}
            disabled={snapshot.audioPreparing}
          >
            <Volume2 size={16} />
            {audioButtonLabel}
          </Button>
          <Button className="game-action primary" size="3" onClick={start} disabled={!snapshot.audioReady || (!canStart && snapshot.status !== "ready")}>
            <Sparkles size={16} />
            复刻
          </Button>
          <Button
            className="game-action primary tap-button"
            size="4"
            onPointerDown={beginTransmit}
            onPointerUp={endTransmit}
            onPointerCancel={endTransmit}
            onPointerLeave={endTransmit}
            disabled={!snapshot.audioReady}
          >
            <Flag size={18} />
            按住复刻
          </Button>
        </Flex>
      </div>

      {finished ? (
        <ArcadeResultPanel
          state={state}
          success={snapshot.status === "success"}
          title="看看目标节奏和复刻轨道是否对齐"
          prompt={transferPrompt}
          score={snapshot.score}
          stars={rhythmStars}
          badges={[
            ["关卡", `${Math.min(snapshot.currentRound + 1, snapshot.totalRounds)}/${snapshot.totalRounds}`],
            ["准确率", `${accuracyPercent}%`],
            ["最高连击", String(snapshot.maxCombo)],
            ["漏拍", String(snapshot.misses)],
            ["多拍", String(snapshot.extras)]
          ]}
          onReplay={reset}
          onNext={advanceRound}
          nextDisabled={snapshot.status !== "success" || snapshot.cleared >= snapshot.totalRounds}
          nextLabel={snapshot.cleared >= snapshot.totalRounds ? "全部完成" : "下一关"}
        />
      ) : null}
    </div>
    </ArcadeLevelFlow>
  );
}

function RhythmEchoTutorialOverlay({
  open,
  totalHits,
  referenceLabel,
  requiredPercent,
  audioReady,
  onClose
}: {
  open: boolean;
  totalHits: number;
  referenceLabel: string;
  requiredPercent: number;
  audioReady: boolean;
  onClose: () => void;
}) {
  if (!open) return null;
  return (
    <div className="rhythm-tutorial-layer" role="dialog" aria-modal="true" aria-labelledby="rhythm-tutorial-title">
      <section className="rhythm-tutorial-card">
        <div className="rhythm-tutorial-header">
          <Text className="eyebrow">前情提要</Text>
          <Heading id="rhythm-tutorial-title" size="6">节奏复刻任务说明</Heading>
          <p>先观察场景里的节奏伙伴，完整听一遍目标节奏，再把相同的位置和长短复刻到下方轨道。</p>
        </div>

        <div className="rhythm-reference-panel" aria-label="本局标准参考">
          <span>本局标准</span>
          <strong>{totalHits} 个节奏点 · {referenceLabel}</strong>
          <small>上方是目标节奏，下方是你的复刻轨道；看两条轨道是否在拍点和长短上对齐。</small>
        </div>

        <div className="rhythm-tutorial-grid">
          <article>
            <span>1</span>
            <strong>准备音频 / 听示范</strong>
            <p>{audioReady ? "采样已就绪，可以反复听目标节奏。" : "第一次先加载木琴采样，成功后再听目标节奏。"}</p>
          </article>
          <article>
            <span>2</span>
            <strong>盲听复刻</strong>
            <p>开始后目标会隐藏，你要凭刚才听到的节奏复刻。</p>
          </article>
          <article>
            <span>3</span>
            <strong>按住复刻</strong>
            <p>短音短按，长音长按；复刻轨道越贴近目标节奏，得分越高。</p>
          </article>
        </div>

        <div className="rhythm-judge-strip">
          <strong>通关标准：准确率达到 {requiredPercent}%</strong>
          <span>早了、晚了、太短、太长、多拍、漏拍都会扣能量；失败后看上下两条轨道哪里没对齐。</span>
        </div>

        <div className="rhythm-tutorial-actions">
          <Button className="game-action primary rhythm-tutorial-close" size="4" onClick={onClose}>
            知道了，开始挑战
          </Button>
        </div>
      </section>
    </div>
  );
}

function initialRhythmEchoSnapshot(config: ReturnType<typeof buildRhythmEchoSceneConfig>): RhythmEchoSnapshot {
  const timeline = config.pattern_timeline || [];
  const totalHits = timeline.filter((item) => item.hit_required).length;
  const audioMode = config.lesson_audio_sync?.audio_url ? "lesson_audio" : "internal_pattern";
  return {
    status: "ready",
    currentIndex: 0,
    totalHits,
    hits: 0,
    misses: 0,
    extras: 0,
    combo: 0,
    maxCombo: 0,
    score: 0,
    energy: Number(config.energy_max || 100),
    energyMax: Number(config.energy_max || 100),
    accuracy: 0,
    progress: 0,
    audioMode,
    audioLabel: audioMode === "lesson_audio" ? config.lesson_audio_sync?.segment_label || "作品片段" : "内置节奏",
    audioReady: false,
    audioPreparing: false,
    audioSource: undefined,
    currentRound: Math.max(0, Number(config.active_round || 1) - 1),
    totalRounds: Number(config.round_count || 1),
    cleared: 0,
    patternLabel: timeline.map((item) => item.label).join(" "),
    durationLabel: timeline
      .filter((item) => item.hit_required)
      .map((item) => (item.duration_beats >= 1.5 ? "长" : item.duration_beats <= 0.5 ? "短" : "中"))
      .join("-"),
    message: "准备"
  };
}

function RaceTimingGame({ state, setFeedback, onProgress, onComplete }: RuntimeProps) {
  const config = state.config ?? {};
  const sceneConfigRef = useRef(buildRaceTimingSceneConfig(config));
  const controllerRef = useRef<RaceTimingController | null>(null);
  const stageRef = useRef<HTMLDivElement | null>(null);
  const callbacksRef = useRef({ setFeedback, onProgress, onComplete });
  const [snapshot, setSnapshot] = useState<RaceTimingSnapshot>(() => initialRaceTimingSnapshot(sceneConfigRef.current));

  useEffect(() => {
    callbacksRef.current = { setFeedback, onProgress, onComplete };
  }, [onComplete, onProgress, setFeedback]);

  useEffect(() => {
    if (!stageRef.current) return;
    stageRef.current.innerHTML = "";
    const controller = mountRaceTimingScene(stageRef.current, sceneConfigRef.current, (event: RaceTimingSceneEvent) => {
      setSnapshot(event.snapshot);
      if (event.message) callbacksRef.current.setFeedback(event.message);
      callbacksRef.current.onProgress(event.snapshot.beat, event.snapshot.hits);
      if (event.type === "mission_success") callbacksRef.current.onComplete();
    });
    controllerRef.current = controller;
    return () => {
      controller.destroy();
      controllerRef.current = null;
    };
  }, []);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.code !== "Space") return;
      event.preventDefault();
      controllerRef.current?.tap();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const start = () => {
    controllerRef.current?.start();
    setFeedback("预备拍");
  };
  const tap = () => controllerRef.current?.tap();
  const reset = () => {
    controllerRef.current?.reset();
    setSnapshot(initialRaceTimingSnapshot(sceneConfigRef.current));
    setFeedback("准备");
  };
  const finished = snapshot.status === "success" || snapshot.status === "failed";
  const energyPercent = Math.round((snapshot.energy / Math.max(1, snapshot.energyMax)) * 100);
  const stars = starsForScore(snapshot.score + snapshot.maxCombo * 80, snapshot.status === "success");
  const arcadePhase: ArcadeAssetState = snapshot.status === "success" ? "win" : snapshot.status === "failed" ? "miss" : snapshot.combo > 0 ? "hit" : "idle";

  return (
    <ArcadeLevelFlow state={state} phase={arcadePhase}>
      <div className="race-timing-runtime arcade" data-engine-target="phaser_2d">
        <ArcadeStageHeader state={state} phase={arcadePhase} objective="按准拍点，让队伍冲过终点。" status={raceTimingStatusLabel(snapshot.status)} />
        <ArcadeHudBar
          state={state}
          level={`第 ${snapshot.beat}/${snapshot.totalBeats} 拍`}
          score={snapshot.score}
          energy={energyPercent}
          combo={`${snapshot.combo}/${snapshot.requiredCombo}`}
          status={raceTimingStatusLabel(snapshot.status)}
        />
        <div className="rhythm-phaser-shell rhythm-arcade-stage-card" data-engine="phaser_2d" data-scene="race_timing_scene">
          <div ref={stageRef} className="rhythm-phaser-stage" aria-label="节拍竞速 Phaser 游戏舞台" />
        </div>
        <div className="rhythm-arcade-bottom-hud">
          <Card className="guardian-feedback-card compact arcade-feedback rhythm-feedback">
            <Flex align="center" justify="between" gap="3" wrap="wrap">
              <Box>
                <Text className="eyebrow">反馈</Text>
                <Text as="p" size="5" weight="bold">{classroomFeedback(snapshot.message, "跟稳拍点。")}</Text>
              </Box>
              <Badge color={snapshot.status === "success" ? "green" : snapshot.status === "failed" ? "ruby" : "teal"} variant="solid">
                {raceTimingStatusLabel(snapshot.status)}
              </Badge>
            </Flex>
          </Card>
          <Flex className="rhythm-arcade-actions" gap="2" wrap="wrap">
            <Button className="game-action primary" size="3" onClick={start} disabled={snapshot.status === "racing" || snapshot.status === "count_in"}>
              <Play size={16} />
              开始竞速
            </Button>
            <Button className="game-action primary tap-button" size="4" onClick={tap}>
              <Flag size={18} />
              准拍推进
            </Button>
            <Button className="game-action" size="3" variant="soft" onClick={reset}>
              <RotateCcw size={16} />
              重试
            </Button>
          </Flex>
        </div>
        {finished ? (
          <ArcadeResultPanel
            state={state}
            success={snapshot.status === "success"}
            title="你怎样保持连续稳定拍？"
            prompt={resultTransferPrompt(state, "用身体律动跟着稳定拍再走一遍。")}
            score={snapshot.score}
            stars={stars}
            badges={[["最高连击", String(snapshot.maxCombo)], ["命中", String(snapshot.hits)]]}
            onReplay={reset}
          />
        ) : null}
      </div>
    </ArcadeLevelFlow>
  );
}

function PatternBuilderGame({ state, setFeedback, onProgress, onComplete }: RuntimeProps) {
  const config = state.config ?? {};
  const sceneConfigRef = useRef(buildPatternBuilderSceneConfig(config));
  const controllerRef = useRef<PatternBuilderController | null>(null);
  const stageRef = useRef<HTMLDivElement | null>(null);
  const callbacksRef = useRef({ setFeedback, onProgress, onComplete });
  const [snapshot, setSnapshot] = useState<PatternBuilderSnapshot>(() => initialPatternBuilderSnapshot(sceneConfigRef.current));

  useEffect(() => {
    callbacksRef.current = { setFeedback, onProgress, onComplete };
  }, [onComplete, onProgress, setFeedback]);

  useEffect(() => {
    if (!stageRef.current) return;
    stageRef.current.innerHTML = "";
    const controller = mountPatternBuilderScene(stageRef.current, sceneConfigRef.current, (event: PatternBuilderSceneEvent) => {
      setSnapshot(event.snapshot);
      if (event.message) callbacksRef.current.setFeedback(event.message);
      callbacksRef.current.onProgress(event.snapshot.placed.length, event.snapshot.status === "success" ? event.snapshot.target.length : event.snapshot.placed.length);
      if (event.type === "mission_success") callbacksRef.current.onComplete();
    });
    controllerRef.current = controller;
    return () => {
      controller.destroy();
      controllerRef.current = null;
    };
  }, []);

  const place = (token: PatternBuilderToken) => controllerRef.current?.place(token);
  const start = () => controllerRef.current?.start();
  const check = () => controllerRef.current?.check();
  const reset = () => {
    controllerRef.current?.reset();
    setSnapshot(initialPatternBuilderSnapshot(sceneConfigRef.current));
    setFeedback("准备");
  };
  const finished = snapshot.status === "success" || snapshot.status === "failed";
  const stars = starsForScore(snapshot.score, snapshot.status === "success");
  const arcadePhase: ArcadeAssetState = snapshot.status === "success" ? "win" : snapshot.status === "failed" ? "miss" : snapshot.placed.length > 0 ? "hit" : "idle";

  return (
    <ArcadeLevelFlow state={state} phase={arcadePhase}>
      <div className="pattern-builder-runtime arcade" data-engine-target="phaser_2d">
        <ArcadeStageHeader state={state} phase={arcadePhase} objective="用节奏卡拼出目标节奏。" status={patternBuilderStatusLabel(snapshot.status)} />
        <ArcadeHudBar
          state={state}
          level={`已放 ${snapshot.placed.length}/${snapshot.target.length}`}
          score={snapshot.score}
          energy={Math.round(snapshot.progress * 100)}
          combo={snapshot.attempts}
          status={patternBuilderStatusLabel(snapshot.status)}
        />
        <div className="rhythm-phaser-shell rhythm-arcade-stage-card" data-engine="phaser_2d" data-scene="pattern_builder_scene">
          <div ref={stageRef} className="rhythm-phaser-stage" aria-label="节奏工坊 Phaser 游戏舞台" />
        </div>
        <div className="rhythm-arcade-bottom-hud">
          <Card className="guardian-feedback-card compact arcade-feedback rhythm-feedback">
            <Flex align="center" justify="between" gap="3" wrap="wrap">
              <Box>
                <Text className="eyebrow">反馈</Text>
                <Text as="p" size="5" weight="bold">{classroomFeedback(snapshot.message, "听结构，再拼卡。")}</Text>
              </Box>
              <Badge color={snapshot.status === "success" ? "green" : snapshot.status === "failed" ? "ruby" : "teal"} variant="solid">
                {patternBuilderStatusLabel(snapshot.status)}
              </Badge>
            </Flex>
          </Card>
          <Flex className="rhythm-arcade-actions" gap="2" wrap="wrap">
            <Button className="game-action primary" size="3" onClick={start}>
              <Play size={16} />
              开始拼图
            </Button>
            <Button className="game-action" size="3" variant="soft" onClick={() => place("quarter")}>四分</Button>
            <Button className="game-action" size="3" variant="soft" onClick={() => place("eighth_pair")}>二八</Button>
            <Button className="game-action" size="3" variant="soft" onClick={() => place("rest")}>休止</Button>
            <Button className="game-action primary" size="3" onClick={check}>
              <Star size={16} />
              检查
            </Button>
            <Button className="game-action" size="3" variant="soft" onClick={reset}>
              <RotateCcw size={16} />
              重试
            </Button>
          </Flex>
        </div>
        {finished ? (
          <ArcadeResultPanel
            state={state}
            success={snapshot.status === "success"}
            title="这个节奏由哪些时值组成？"
            prompt={resultTransferPrompt(state, "说出四分、二八和休止的位置。")}
            score={snapshot.score}
            stars={stars}
            badges={[["尝试", String(snapshot.attempts)], ["结构", snapshot.target.join(" · ")]]}
            onReplay={reset}
          />
        ) : null}
      </div>
    </ArcadeLevelFlow>
  );
}

function initialRaceTimingSnapshot(config: ReturnType<typeof buildRaceTimingSceneConfig>): RaceTimingSnapshot {
  return {
    status: "ready",
    beat: 0,
    totalBeats: Number(config.round_count || 5) * 4,
    hits: 0,
    misses: 0,
    combo: 0,
    maxCombo: 0,
    requiredCombo: Number(config.combo_required || 4),
    score: 0,
    energy: Number(config.energy_max || 100),
    energyMax: Number(config.energy_max || 100),
    progress: 0,
    message: "准备"
  };
}

function initialPatternBuilderSnapshot(config: ReturnType<typeof buildPatternBuilderSceneConfig>): PatternBuilderSnapshot {
  const target = (config.pattern_steps || ["quarter", "eighth_pair", "quarter", "rest"]) as PatternBuilderToken[];
  return {
    status: "ready",
    target,
    placed: [],
    score: 0,
    attempts: 0,
    progress: 0,
    message: "准备"
  };
}

function raceTimingStatusLabel(status: RaceTimingSnapshot["status"]) {
  return {
    ready: "待开始",
    count_in: "预备拍",
    racing: "竞速中",
    success: "冲线",
    failed: "复盘后重试"
  }[status];
}

function patternBuilderStatusLabel(status: PatternBuilderSnapshot["status"]) {
  return {
    ready: "待开始",
    building: "拼节奏",
    success: "完成",
    failed: "复盘后重试"
  }[status];
}

function rhythmStatusLabel(status: RhythmEchoSnapshot["status"]) {
  return {
    ready: "待开始",
    demo: "听示范",
    blind_demo: "盲听",
    count_in: "预备",
    recording: "复刻中",
    success: "通关",
    failed: "复盘后重试"
  }[status];
}

function SolfegeTargetGame({ state, setFeedback, onProgress, onComplete }: RuntimeProps) {
  const configKey = stableConfigKey({ config: state.config ?? {}, workflow: state.workflow ?? {} });
  const config = useMemo(() => mergeSolfegeEntityExecutionConfig(state, state.config ?? {}), [configKey]);
  const sceneConfigRef = useRef(buildSolfegeTargetSceneConfig(config));
  const controllerRef = useRef<SolfegeTargetController | null>(null);
  const stageRef = useRef<HTMLDivElement | null>(null);
  const callbacksRef = useRef({ setFeedback, onProgress, onComplete });
  const [snapshot, setSnapshot] = useState<SolfegeTargetSnapshot>(() => initialSolfegeTargetSnapshot(sceneConfigRef.current));
  const [micState, setMicState] = useState<"idle" | "listening" | "voice" | "blocked">("idle");
  const [coverVisible, setCoverVisible] = useState(true);
  const micStreamRef = useRef<MediaStream | null>(null);
  const micContextRef = useRef<AudioContext | null>(null);
  const micPollTimeoutRef = useRef<number | null>(null);

  const stopMicAssist = () => {
    if (micPollTimeoutRef.current !== null) {
      window.clearTimeout(micPollTimeoutRef.current);
      micPollTimeoutRef.current = null;
    }
    micStreamRef.current?.getTracks().forEach((track) => track.stop());
    micStreamRef.current = null;
    void micContextRef.current?.close();
    micContextRef.current = null;
  };

  useEffect(() => {
    callbacksRef.current = { setFeedback, onProgress, onComplete };
  }, [onComplete, onProgress, setFeedback]);

  useEffect(() => {
    stopMicAssist();
    sceneConfigRef.current = buildSolfegeTargetSceneConfig(config);
    setSnapshot(initialSolfegeTargetSnapshot(sceneConfigRef.current));
    setMicState("idle");
    setCoverVisible(true);
  }, [config]);

  useEffect(() => {
    if (!stageRef.current) return;
    stageRef.current.innerHTML = "";
    const controller = mountSolfegeTargetScene(stageRef.current, sceneConfigRef.current, (event: SolfegeTargetSceneEvent) => {
      setSnapshot(event.snapshot);
      if (event.message) callbacksRef.current.setFeedback(event.message);
      callbacksRef.current.onProgress(event.snapshot.currentRound, event.snapshot.cleared);
      if (event.type === "mission_success") callbacksRef.current.onComplete();
    });
    controllerRef.current = controller;
    return () => {
      controller.destroy();
      controllerRef.current = null;
      stopMicAssist();
    };
  }, [configKey]);

  useEffect(() => {
    if (snapshot.status === "sing_back" && snapshot.micAssistEnabled && micState === "idle") {
      void startMicAssist();
    }
    if (snapshot.status !== "sing_back" && micState !== "idle") {
      stopMicAssist();
      setMicState("idle");
    }
  }, [micState, snapshot.micAssistEnabled, snapshot.status]);

  const listen = () => {
    setCoverVisible(false);
    controllerRef.current?.listen();
    playSolfegeSnapshot(snapshot) || setFeedback("当前浏览器不能播放声音，请由教师范唱目标音。");
  };

  const startMicAssist = async () => {
    if (micState === "listening" || micState === "voice") return;
    if (!snapshot.micAssistEnabled || !navigator.mediaDevices?.getUserMedia) {
      setMicState("blocked");
      setFeedback("麦克风不可用，请检查浏览器权限后再唱回。");
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stopMicAssist();
      micStreamRef.current = stream;
      setMicState("listening");
      setFeedback("麦克风已打开，请学生唱出刚击中的目标音。");
      const AudioCtor = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtor) {
        setMicState("blocked");
        setFeedback("当前浏览器不能检测麦克风，请换浏览器或检查权限。");
        return;
      }
      const context = new AudioCtor();
      micContextRef.current = context;
      const source = context.createMediaStreamSource(stream);
      const analyser = context.createAnalyser();
      analyser.fftSize = 512;
      source.connect(analyser);
      const data = new Uint8Array(analyser.frequencyBinCount);
      const startedAt = performance.now();
      let ticks = 0;
      const poll = () => {
        analyser.getByteFrequencyData(data);
        const average = data.reduce((sum, value) => sum + value, 0) / Math.max(1, data.length);
        if (performance.now() - startedAt > 450 && average > 10) {
          setMicState("voice");
          setFeedback("听到学生唱声了，现在可以确认唱回。");
          stopMicAssist();
          return;
        }
        ticks += 1;
        if (ticks < 60) {
          micPollTimeoutRef.current = window.setTimeout(poll, 120);
          return;
        }
        setMicState("blocked");
        setFeedback("还没有检测到唱声，请靠近麦克风再试一次。");
        stopMicAssist();
      };
      poll();
    } catch {
      setMicState("blocked");
      setFeedback("麦克风权限未开启，请允许麦克风后再唱回。");
    }
  };

  const confirmSingBack = () => {
    if (snapshot.micAssistEnabled && micState !== "voice") {
      setFeedback("请先让学生唱出目标音，麦克风检测到声音后再确认。");
      return;
    }
    stopMicAssist();
    setMicState("idle");
    controllerRef.current?.confirmSingBack();
  };

  const reset = () => {
    setCoverVisible(false);
    stopMicAssist();
    controllerRef.current?.reset();
    setSnapshot(initialSolfegeTargetSnapshot(sceneConfigRef.current));
    setMicState("idle");
    setFeedback("听目标音");
  };

  const finished = snapshot.status === "success" || snapshot.status === "failed";
  const energyPercent = Math.round((snapshot.energy / Math.max(1, snapshot.energyMax)) * 100);
  const targetNotes = sceneConfigRef.current.target_solfege || [];
  const targetSequenceLabel = solfegeSequenceLabel(snapshot);
  const voiceEvidence = solfegeVoiceEvidenceLabel(micState);
  const listeningEvidence = solfegeListeningEvidence(snapshot);
  const teacherConfirmLabel = micState === "voice" ? "确认唱回" : "先唱给麦克风";
  const canConfirmSingBack = snapshot.status === "success" || (snapshot.status === "sing_back" && (!snapshot.micAssistEnabled || micState === "voice"));
  const canStartMicAssist = snapshot.micAssistEnabled && snapshot.status === "sing_back" && micState !== "listening" && micState !== "voice";
  const transferPrompt = resultTransferPrompt(state, "说出这个音名在旋律里的位置感。");
  const feedbackText = solfegeFeedbackText(state, snapshot);
  const solfegeScore = snapshot.score;
  const solfegeStars = starsForScore(solfegeScore, snapshot.status === "success");
  const arcadePhase: ArcadeAssetState = snapshot.status === "success" ? "win" : snapshot.status === "failed" ? "miss" : snapshot.hits > 0 ? "hit" : "idle";

  return (
    <ArcadeLevelFlow state={state} phase={arcadePhase}>
    <div className="solfege-target-runtime game-first-target" data-engine-target="phaser_2d" data-scene="solfege_target_scene">
      {coverVisible && snapshot.status === "ready" ? (
        <ArcadeStartOverlay
          state={state}
          title="听音，击中音名靶"
          subtitle="先命中，再唱回，靶心才算点亮。"
          actionLabel="听目标音"
          onStart={listen}
        />
      ) : null}
      <div className="solfege-game-board" data-solfege-status={snapshot.status}>
        <div className="solfege-mini-hud" aria-label="音名打靶状态">
          <span className="solfege-mini-title">{snapshot.skinObjective}</span>
          <span>第 {Math.min(snapshot.currentRound + 1, snapshot.totalRounds)} 关</span>
          <span>{solfegeStatusLabel(snapshot.status)}</span>
          <span>分 {solfegeScore}</span>
          <span>能量 {energyPercent}%</span>
          <span>连击 {snapshot.combo}</span>
        </div>
        <div className="solfege-phaser-shell" data-engine="phaser_2d" data-target-hud="true">
          <div ref={stageRef} className="solfege-phaser-stage" aria-label="音名打靶 Phaser 靶场舞台" />
        </div>
        <div className="solfege-control-rail">
        <div className="solfege-feedback-strip" role="status">
          <strong>{solfegeStatusLabel(snapshot.status)}</strong>
          <span>{feedbackText}</span>
        </div>
        <div className="solfege-evidence-panel" aria-label="唱回证据">
          <div className="solfege-evidence-track">
            <span className={solfegeStepClass(snapshot.status, "listen")}>1 听</span>
            <span className={solfegeStepClass(snapshot.status, "target")}>2 击中</span>
            <span className={solfegeStepClass(snapshot.status, "sing")}>3 唱回</span>
            <span className={solfegeStepClass(snapshot.status, "confirm")}>4 确认</span>
          </div>
          <div className="solfege-evidence-body">
            <div>
              <span>目标音组</span>
              <strong>{targetSequenceLabel}</strong>
            </div>
            <div>
              <span>麦克风唱回</span>
              <strong>{voiceEvidence}</strong>
            </div>
            <div>
              <span>课堂确认</span>
              <strong>{snapshot.singBackConfirmed ? "已确认" : snapshot.status === "sing_back" ? (micState === "voice" ? "可确认" : "请先唱") : "先命中"}</strong>
            </div>
            <div className="solfege-evidence-reason" data-reason-state={listeningEvidence.tone}>
              <span>听辨依据</span>
              <strong>{listeningEvidence.text}</strong>
            </div>
          </div>
        </div>
        </div>
        <div className="solfege-action-dock">
          <div className="solfege-action-primary">
            <Button className="game-action primary" size="3" onClick={listen}>
              <Volume2 size={16} />
              听目标音
            </Button>
            <Button className="game-action solfege-mic-button" size="3" variant="soft" onClick={startMicAssist} disabled={!canStartMicAssist}>
              {micAssistLabel(micState)}
            </Button>
          </div>
          <div className="solfege-target-pad" aria-label="音名靶按钮">
            {targetNotes.map((note) => (
              <Button
                key={note}
                className="game-action solfege-fire-button"
                variant={snapshot.selected.includes(note) ? "solid" : "soft"}
                disabled={snapshot.status === "sing_back" || finished}
                onClick={() => controllerRef.current?.fire(note)}
              >
                {noteLabel(note)}
              </Button>
            ))}
          </div>
          <div className="solfege-action-primary">
            <Button className="game-action primary solfege-confirm-button" size="3" onClick={confirmSingBack} disabled={!canConfirmSingBack}>
              {teacherConfirmLabel}
            </Button>
            <Button className="game-action" size="3" variant="soft" onClick={reset}>
              <RotateCcw size={16} />
              重试
            </Button>
          </div>
        </div>
      </div>

      {finished ? (
        <ArcadeResultPanel
          state={state}
          success={snapshot.status === "success"}
          title={snapshot.status === "success" ? "唱回证据完成" : "回到目标音重新听"}
          prompt={transferPrompt}
          score={solfegeScore}
          stars={solfegeStars}
          badges={[["目标", targetSequenceLabel], ["命中", String(snapshot.hits)], ["最高连击", String(snapshot.maxCombo)], ["唱回", snapshot.singBackConfirmed ? "已确认" : "待确认"]]}
          onReplay={reset}
          nextLabel="下一靶"
        />
      ) : null}
      <details className="guardian-teacher-details solfege-teacher-details">
        <summary>教师提示</summary>
        <p>命中后必须唱回。麦克风检测到学生发声后，教师再确认音名是否准确。</p>
      </details>
    </div>
    </ArcadeLevelFlow>
  );
}

function initialSolfegeTargetSnapshot(config: ReturnType<typeof buildSolfegeTargetSceneConfig>): SolfegeTargetSnapshot {
  const rounds = config.solfege_rounds || [];
  const firstRound = rounds[0] || {};
  const audioMode = config.audio_mode || "hybrid";
  const answer = Array.isArray(firstRound.answer) ? firstRound.answer.map(String) : [String(firstRound.answer || "")].filter(Boolean);
  return {
    status: "ready",
    currentRound: 0,
    totalRounds: rounds.length || 1,
    currentMode: config.current_mode || "single_target",
    sequence: (firstRound.sequence || answer).map(String),
    labels: (firstRound.labels || firstRound.sequence || answer).map(String),
    answer,
    selected: [],
    combo: 0,
    maxCombo: 0,
    score: 0,
    hits: 0,
    misses: 0,
    cleared: 0,
    energy: Number(config.energy_max || 100),
    energyMax: Number(config.energy_max || 100),
    mistakeLimit: Number(config.mistake_limit || 3),
    progress: 0,
    skinObjective: solfegeSkinObjective(String(config.skin_play_mode || "star")),
    audioMode,
    audioLabel: audioMode === "lesson_audio" ? "作品片段" : "内置音高",
    singBackRequired: config.sing_back_required !== false,
    teacherConfirmRequired: config.teacher_confirm_required !== false,
    singBackConfirmed: false,
    expectedNote: answer[0],
    nextExpectedNote: answer[0],
    micAssistEnabled: config.mic_assist_enabled !== false,
    message: "听目标音"
  };
}

function playSolfegeSnapshot(snapshot: SolfegeTargetSnapshot) {
  const offsets = snapshot.sequence.map((note) => pitchMidiOffset(note));
  return playToneSequence(offsets.length ? offsets : [0], "triangle", 0.5);
}

function solfegeStatusLabel(status: SolfegeTargetSnapshot["status"]) {
  return {
    ready: "待开始",
    listening: "听音中",
    aiming: "瞄准",
    sing_back: "唱回",
    success: "通关",
    failed: "复盘"
  }[status];
}

function solfegeSequenceLabel(snapshot: SolfegeTargetSnapshot) {
  const labels = snapshot.labels.length ? snapshot.labels : snapshot.sequence;
  return labels.map(noteLabel).join(" - ") || "目标音";
}

function solfegeVoiceEvidenceLabel(state: "idle" | "listening" | "voice" | "blocked") {
  return {
    idle: "未检测",
    listening: "正在听",
    voice: "听到声音",
    blocked: "不可用"
  }[state];
}

function solfegeFeedbackText(state: StudentGameState, snapshot: SolfegeTargetSnapshot) {
  if (snapshot.lastJudgement === "miss") {
    const key = snapshot.mistakeReason || "wrong_target";
    return reasonPrompt(state, key, key === "chain_wrong" ? "顺序不稳：重新听整组音。" : "音名不对：先在心里唱出目标音。");
  }
  if (snapshot.status === "success") {
    return reasonPrompt(state, "success", "听辨和唱回完成：说出这个音的位置感。");
  }
  if (snapshot.status === "sing_back") {
    return reasonPrompt(state, "sing_back", "点击不是终点：请唱回目标音，再由教师确认。");
  }
  if (snapshot.lastJudgement === "hit" || snapshot.lastJudgement === "combo") {
    return reasonPrompt(state, "right_target", "击中音名：现在把它唱出来。");
  }
  if (snapshot.status === "failed") {
    return reasonPrompt(state, snapshot.mistakeReason || "wrong_target", "音名不对：先在心里唱出目标音。");
  }
  return classroomFeedback(snapshot.message, "先听目标音，再击中音名。");
}

function solfegeListeningEvidence(snapshot: SolfegeTargetSnapshot): { text: string; tone: "ready" | "listen" | "hit" | "miss" | "sing" | "success" } {
  const target = noteLabel(snapshot.nextExpectedNote || snapshot.expectedNote || snapshot.answer[0] || "");
  const expected = noteLabel(snapshot.expectedNote || snapshot.nextExpectedNote || snapshot.answer[0] || "");
  const chosen = snapshot.lastChosenNote ? noteLabel(snapshot.lastChosenNote) : "";
  const stepLabel = snapshot.answer.length > 1 && snapshot.lastShotIndex !== undefined ? `第${snapshot.lastShotIndex + 1}音` : "目标音";

  if (snapshot.lastJudgement === "miss" && chosen) {
    return {
      tone: "miss",
      text: snapshot.mistakeReason === "chain_wrong"
        ? `${stepLabel}应${expected}，你点${chosen}`
        : `你点${chosen}，目标是${expected}`
    };
  }
  if (snapshot.status === "success") {
    return { tone: "success", text: "说出它的位置感" };
  }
  if (snapshot.status === "sing_back") {
    return { tone: "sing", text: `${expected}已命中，唱回确认` };
  }
  if (snapshot.lastJudgement === "hit" || snapshot.lastJudgement === "combo") {
    return { tone: "hit", text: `${expected}已命中，继续保持` };
  }
  if (snapshot.status === "listening") {
    return { tone: "listen", text: `听${target}，先心唱` };
  }
  if (snapshot.status === "aiming") {
    return { tone: "listen", text: `默唱${target}再点击` };
  }
  return { tone: "ready", text: "先听，再心唱" };
}

function solfegeStepClass(status: SolfegeTargetSnapshot["status"], step: "listen" | "target" | "sing" | "confirm") {
  const activeByStep = {
    listen: status === "listening",
    target: status === "aiming",
    sing: status === "sing_back",
    confirm: status === "success"
  };
  const doneByStep = {
    listen: status !== "ready",
    target: status === "sing_back" || status === "success",
    sing: status === "success",
    confirm: status === "success"
  };
  return ["solfege-evidence-step", activeByStep[step] ? "is-active" : "", doneByStep[step] ? "is-done" : ""].filter(Boolean).join(" ");
}

function solfegeSkinObjective(playMode: string) {
  return {
    star: "音名星靶场",
    flower: "花朵绽放",
    lantern: "灯笼靶会",
    archery: "音乐弓箭场",
    bubble: "泡泡音名"
  }[playMode] ?? "音名靶场";
}

function micAssistLabel(state: "idle" | "listening" | "voice" | "blocked") {
  return {
    idle: "请唱出目标音",
    listening: "正在检测唱声",
    voice: "已检测到唱声",
    blocked: "重新检测"
  }[state];
}

function FormTreasureGame({ state, setFeedback, onProgress, onComplete }: RuntimeProps) {
  const configKey = stableConfigKey({ config: state.config ?? {}, workflow: state.workflow ?? {} });
  const config = useMemo(() => mergeFormEntityExecutionConfig(state, state.config ?? {}), [configKey]);
  const sceneConfigRef = useRef(buildFormTreasureSceneConfig(config));
  const controllerRef = useRef<FormTreasureController | null>(null);
  const stageRef = useRef<HTMLDivElement | null>(null);
  const [snapshot, setSnapshot] = useState<FormTreasureSnapshot>(() => initialFormTreasureSnapshot(sceneConfigRef.current));
  const [selectedPattern, setSelectedPattern] = useState<string[]>([]);
  const [routeSlots, setRouteSlots] = useState<string[]>(() => answerPatternSlots(sceneConfigRef.current.answer_pattern || ["A", "B", "A"]));
  const [activeCard, setActiveCard] = useState<FormStructureCard | null>(null);
  const [currentSegment, setCurrentSegment] = useState(0);
  const [finished, setFinished] = useState(false);
  const [started, setStarted] = useState(false);
  const [coverVisible, setCoverVisible] = useState(true);
  const segments = sceneConfigRef.current.timeline_segments || [];
  const cards = sceneConfigRef.current.structure_cards || [];
  const answerPattern = sceneConfigRef.current.answer_pattern || ["A", "B", "A"];

  useEffect(() => {
    sceneConfigRef.current = buildFormTreasureSceneConfig(config);
    setSnapshot(initialFormTreasureSnapshot(sceneConfigRef.current));
    setSelectedPattern([]);
    setRouteSlots(answerPatternSlots(sceneConfigRef.current.answer_pattern || ["A", "B", "A"]));
    setActiveCard(null);
    setCurrentSegment(0);
    setFinished(false);
    setStarted(false);
    setCoverVisible(true);
  }, [config]);

  useEffect(() => {
    if (!stageRef.current) return undefined;
    stageRef.current.innerHTML = "";
    const controller = mountFormTreasureScene(stageRef.current, sceneConfigRef.current, (event: FormTreasureSceneEvent) => {
      setSnapshot(event.snapshot);
      setRouteSlots(event.snapshot.routeSlots);
      setSelectedPattern(event.snapshot.selectedPattern);
      if (event.message) setFeedback(event.message);
      onProgress(event.snapshot.currentSegment, Math.round(event.snapshot.progress * event.snapshot.totalSegments));
      if (event.type === "mission_success") {
        setFinished(true);
        onComplete();
      }
    });
    controllerRef.current = controller;
    return () => controller.destroy();
  }, [configKey]);

  const listenSegment = () => {
    setCoverVisible(false);
    setStarted(true);
    const segment = segments[currentSegment] || segments[0];
    void playFormSegment(segment);
    controllerRef.current?.listenSegment(currentSegment);
    setFeedback(`${segment?.label || "段落"}：听它像主题、再现还是对比`);
    if (segments.length) setCurrentSegment((value) => (value + 1) % segments.length);
  };

  const selectCard = (card: FormStructureCard) => {
    if (finished) return;
    const next = activeCard?.label === card.label ? null : card;
    setActiveCard(next);
    controllerRef.current?.setActiveCard(next?.label || null);
    setFeedback(next ? `已拿起 ${next.label} 卡：点路线槽或场景段落位置放置` : "选择结构卡");
  };

  const removeLastCard = () => {
    const index = lastFilledSlotIndex(routeSlots);
    if (index < 0) return;
    const next = routeSlots.map((item, itemIndex) => itemIndex === index ? "" : item);
    setRouteSlots(next);
    setSelectedPattern(next.filter(Boolean));
    controllerRef.current?.removeCard(index);
    setFeedback("撤回一张结构卡");
  };

  const placeCard = (slotIndex: number) => {
    if (finished || !activeCard) return;
    const next = routeSlots.map((item, index) => index === slotIndex ? activeCard.label : item);
    setRouteSlots(next);
    setSelectedPattern(next.filter(Boolean));
    controllerRef.current?.placeCard(slotIndex, activeCard.label);
    setActiveCard(null);
    setFeedback(next.filter(Boolean).length === answerPattern.length ? "路线完整，可以验证" : "继续连接藏宝路线");
  };

  const useTreasureTool = (toolId: "compass" | "scroll" | "key") => {
    if (finished) return;
    setCoverVisible(false);
    setStarted(true);
    controllerRef.current?.useTool(toolId);
    setFeedback(toolId === "key" ? "钥匙会检查路线是否完整" : "获得一条听辨线索");
  };

  const verify = () => {
    const judgement = resolveFormRouteJudgement(routeSlots, answerPattern);
    controllerRef.current?.verifyPattern(judgement.routeSlots, judgement.correct);
    setFeedback(judgement.correct ? "破译曲式宝藏" : "路线还不对");
    if (judgement.correct) {
      setFinished(true);
      onComplete();
    }
  };

  const reset = () => {
    setFinished(false);
    setStarted(false);
    setCoverVisible(false);
    setSelectedPattern([]);
    setRouteSlots(answerPatternSlots(answerPattern));
    setActiveCard(null);
    setCurrentSegment(0);
    setSnapshot(initialFormTreasureSnapshot(sceneConfigRef.current));
    controllerRef.current?.reset();
    setFeedback("重新听段落");
  };
  const transferPrompt = resultTransferPrompt(state, "指出哪一段像 A 段，哪一段形成对比。");
  const feedbackText = finished
    ? reasonPrompt(state, "success", "曲式路线点亮：说出重复、对比或再现依据。")
    : classroomFeedback(snapshot.message, "听段落，放结构卡，验证路线。");
  const formScore = snapshot.score || (finished ? Math.max(300, 1000 - snapshot.attempts * 120) : selectedPattern.length * 120);
  const formStars = snapshot.stars || starsForScore(formScore, finished);
  const arcadePhase: ArcadeAssetState = finished ? "win" : snapshot.status === "failed" ? "miss" : selectedPattern.length > 0 ? "hit" : "idle";
  const routeComplete = routeSlots.every(Boolean);
  const nextSegmentNumber = segments.length ? currentSegment + 1 : 1;
  const segmentListenLabel = segments.length ? `听第 ${nextSegmentNumber} 段` : "听段落";
  const routePreview = routeSlots.map((item, index) => item || `第${index + 1}段`).join(" / ");
  const formStageTone = finished ? "success" : snapshot.status === "failed" ? "failed" : activeCard ? "placing" : started ? "listening" : "ready";
  const evidencePrompt = finished
    ? "回到作品片段，说出 A 段回来的依据。"
    : activeCard
      ? `把 ${activeCard.label} 卡放到你听到的段落位置。`
      : snapshot.status === "failed"
        ? "复听主题段，比较哪一段材料回来了。"
        : "按顺序复听段落，先判断相同还是对比。";
  const visualPack = templateVisualPackForConfig(config, "form_treasure_core");
  const heroPose = templatePose(visualPack, finished ? "win" : snapshot.status === "failed" ? "miss" : started || activeCard ? "action" : "idle");

  return (
    <ArcadeLevelFlow state={state} phase={arcadePhase}>
    <div
      className="form-treasure-runtime"
      data-scene="form_treasure_scene"
      data-engine="phaser_2d"
      data-hud="timeline_card_progress"
    >
      {coverVisible && !started && !finished ? (
        <section className="form-treasure-start-card" aria-label="曲式寻宝开局任务">
          <div>
            <Text className="eyebrow">寻宝挑战</Text>
            <Heading size="4">听段落，拼出藏宝路线</Heading>
            <p>{snapshot.formType} 曲式寻宝：放结构卡，验证路线。</p>
          </div>
          <Button className="game-action primary" size="4" onClick={listenSegment}>
            <Play size={18} fill="currentColor" />
            听第一段
          </Button>
        </section>
      ) : null}
      <ArcadeStageHeader
        state={state}
        phase={arcadePhase}
        objective={`${snapshot.formType} 曲式路线`}
        status={finished ? "宝箱开启" : formHintLabel(snapshot.hintMode)}
      />
      <ArcadeHudBar
        state={state}
        level={`${snapshot.formType} 路线`}
        score={formScore}
        combo={`${selectedPattern.length}/${answerPattern.length}`}
        status={finished ? "宝箱开启" : formHintLabel(snapshot.hintMode)}
      />
      <div className="form-treasure-topline" data-tone={formStageTone}>
        <div className="form-topline-main">
          <Badge color="amber" variant="solid">{snapshot.formType}</Badge>
          <strong>{feedbackText}</strong>
          <span>{evidencePrompt}</span>
        </div>
        <div className="form-topline-meta" aria-label="曲式寻宝状态">
          <Badge color="teal" variant="soft">提示：{formHintLabel(snapshot.hintMode)}</Badge>
          <Badge color={routeComplete ? "green" : "gray"} variant="soft">路线：{selectedPattern.length}/{answerPattern.length}</Badge>
          {activeCard ? <Badge color="amber" variant="solid">手中：{activeCard.label}</Badge> : null}
        </div>
      </div>

      <div className="form-learning-flow" aria-label="曲式寻宝学习步骤">
        <div className={["form-learning-step", started ? "is-done" : "", !started ? "is-active" : ""].join(" ")}>
          <Volume2 size={16} />
          <span>1 听段落</span>
        </div>
        <div className={["form-learning-step", selectedPattern.length ? "is-done" : "", started && !selectedPattern.length ? "is-active" : ""].join(" ")}>
          <Route size={16} />
          <span>2 排路线</span>
        </div>
        <div className={["form-learning-step", finished ? "is-done" : "", routeComplete && !finished ? "is-active" : ""].join(" ")}>
          <ClipboardCheck size={16} />
          <span>3 说依据</span>
        </div>
      </div>

      <div className="form-stage-frame" data-tone={formStageTone}>
        <div className="form-stage-rail" aria-label="曲式寻宝场景状态">
          <div>
            <Text className="eyebrow">场景寻宝</Text>
            <strong>{segmentListenLabel} · {routeComplete ? "准备验证" : "继续排路线"}</strong>
          </div>
          <span>{activeCard ? `放置 ${activeCard.label}` : routePreview}</span>
        </div>
        {heroPose ? (
          <div className="form-hero-portrait" aria-label="寻宝角色当前姿势">
            <img src={heroPose} alt="" />
            <span>{finished ? "开启宝箱" : activeCard ? "准备放卡" : started ? "正在听辨" : "寻宝队长"}</span>
          </div>
        ) : null}
        <div className="form-phaser-shell">
          <div ref={stageRef} className="form-phaser-stage" aria-label="曲式寻宝 Phaser 图像场景" />
        </div>
        <div className="form-route-slots" aria-label="已排列结构路线">
          {answerPattern.map((_, index) => (
            <button
              key={`slot_${index}`}
              type="button"
              className={[routeSlots[index] ? "filled" : "", activeCard && !routeSlots[index] ? "can-place" : ""].join(" ")}
              onClick={() => routeSlots[index] ? controllerRef.current?.removeCard(index) : placeCard(index)}
              disabled={finished || (!activeCard && !routeSlots[index])}
              aria-label={`第 ${index + 1} 段结构卡${routeSlots[index] ? `：${routeSlots[index]}` : "：待放置"}`}
            >
              <span className="form-route-slot-index">第{index + 1}段</span>
              <strong>{routeSlots[index] || "?"}</strong>
            </button>
          ))}
        </div>
      </div>

      <div className="form-card-dock" data-route-complete={routeComplete ? "true" : "false"}>
        <section className="form-card-zone" aria-label="结构卡选择">
        <div className="form-dock-heading">
          <Text className="eyebrow">结构卡</Text>
          <Heading size="4">听完段落后，把卡片排成曲式路线</Heading>
          <p>我的路线：{routePreview}</p>
        </div>
        <div className="form-card-grid">
          {cards.map((card) => (
            <Button
              key={card.id}
              className={["form-structure-card", activeCard?.label === card.label ? "selected" : ""].join(" ")}
              variant={activeCard?.label === card.label ? "solid" : "soft"}
              color="amber"
              onClick={() => selectCard(card)}
              disabled={finished}
            >
              <strong>{card.label}</strong>
              <span className="form-card-name">{card.name || `${card.label} 段`}</span>
            </Button>
          ))}
        </div>
        </section>
        <section className="form-tool-zone" aria-label="寻宝工具与操作">
        <div className="form-toolbelt" aria-label="寻宝工具">
          <Button className="game-action" size="3" variant="soft" color="teal" onClick={() => useTreasureTool("scroll")} disabled={finished}>
            <ScrollText size={16} />
            卷轴
          </Button>
          <Button className="game-action" size="3" variant="soft" color="teal" onClick={() => useTreasureTool("compass")} disabled={finished}>
            <Compass size={16} />
            指南针
          </Button>
          <Button className="game-action" size="3" variant="soft" color="teal" onClick={() => useTreasureTool("key")} disabled={finished}>
            <KeyRound size={16} />
            钥匙
          </Button>
        </div>
        <div className="form-actions">
          <Button className="game-action primary" size="3" onClick={listenSegment}>
            <Volume2 size={16} />
            {segmentListenLabel}
          </Button>
          <Button className="game-action" size="3" variant="soft" onClick={removeLastCard} disabled={!selectedPattern.length || finished}>
            撤回
          </Button>
          <Button className="game-action primary form-verify-button" size="3" onClick={verify} disabled={!routeComplete || finished}>
            <Route size={16} />
            验证路线
          </Button>
          <Button className="game-action" size="3" variant="soft" onClick={reset}>
            <RotateCcw size={16} />
            重试
          </Button>
        </div>
        </section>
      </div>

      {finished ? (
        <ArcadeResultPanel
          state={state}
          success
          title="宝箱开启，把路线说出来"
          prompt={transferPrompt}
          score={formScore}
          stars={formStars}
          badges={[["答案", answerPattern.join("-")], ["奖励", snapshot.skinObjective]]}
          onReplay={reset}
          nextLabel="下一张地图"
        />
      ) : null}

      <details className="guardian-teacher-details form-teacher-details">
        <summary>教师提示</summary>
        <p>曲式寻宝只训练听辨依据，不替学生讲解答案。建议先让学生说“为什么这里像 A 段/像 B 段”。</p>
      </details>
    </div>
    </ArcadeLevelFlow>
  );
}

function initialFormTreasureSnapshot(config: ReturnType<typeof buildFormTreasureSceneConfig>): FormTreasureSnapshot {
  const answerPattern = config.answer_pattern || ["A", "B", "A"];
  return {
    status: "ready",
    currentSegment: 0,
    totalSegments: config.timeline_segments?.length || answerPattern.length,
    selectedPattern: [],
    answerPattern,
    routeSlots: answerPatternSlots(answerPattern),
    activeSegment: 0,
    activeTool: null,
    score: 0,
    stars: 1,
    revealedClues: [],
    scenePhase: "idle",
    fxQueue: [],
    progress: 0,
    attempts: 0,
    hintMode: config.hint_mode || "partial",
    formType: config.form_type || "ABA",
    skinObjective: formSkinObjective(String(config.skin_play_mode || "map")),
    message: "听段落，排结构"
  };
}

function answerPatternSlots(answerPattern: string[]) {
  return answerPattern.map(() => "");
}

function lastFilledSlotIndex(slots: string[]) {
  for (let index = slots.length - 1; index >= 0; index -= 1) {
    if (slots[index]) return index;
  }
  return -1;
}

function playFormSegment(segment?: FormTimelineSegment) {
  const offsets = segment?.midi_offsets?.length ? segment.midi_offsets : [0, 4, 7, 4];
  return playToneSequence(offsets.map(Number), "sine", 0.42);
}

function formHintLabel(mode: FormTreasureSnapshot["hintMode"]) {
  return {
    guided: "引导",
    partial: "半提示",
    challenge: "挑战"
  }[mode];
}

function formSkinObjective(playMode: string) {
  return {
    map: "找到结构宝藏",
    constellation: "点亮星图航线",
    gallery: "归档音乐展品",
    train: "驶过段落站台",
    stage: "完成剧场分幕"
  }[playMode] ?? "点亮曲式路线";
}

const COMPOSITION_BPM_MIN = 40;
const COMPOSITION_BPM_MAX = 180;
const COMPOSITION_BPM_DEFAULT = 90;

function clampCompositionBpm(value: number) {
  if (!Number.isFinite(value)) return COMPOSITION_BPM_DEFAULT;
  return Math.min(COMPOSITION_BPM_MAX, Math.max(COMPOSITION_BPM_MIN, Math.round(value)));
}

function beatSecondsForBpm(bpm: number) {
  return 60 / clampCompositionBpm(bpm);
}

function CompositionPuzzleGame({ state, setFeedback, onProgress, onComplete }: RuntimeProps) {
  const configKey = stableConfigKey({ config: state.config ?? {}, workflow: state.workflow ?? {} });
  const config = useMemo(() => mergeCompositionEntityExecutionConfig(state, state.config ?? {}), [configKey]);
  const baseSceneConfig = buildCompositionPuzzleSceneConfig(config);
  const controllerRef = useRef<CompositionPuzzleController | null>(null);
  const stageRef = useRef<HTMLDivElement | null>(null);
  const callbacksRef = useRef({ setFeedback, onProgress, onComplete });
  const [selectedMeter, setSelectedMeter] = useState<CompositionMeter>(baseSceneConfig.selected_meter || "4/4");
  const [selectedTonic, setSelectedTonic] = useState(normalizeTonic(baseSceneConfig.selected_tonic || "C"));
  const [selectedScaleType, setSelectedScaleType] = useState<CompositionScaleType>(normalizeScaleType(baseSceneConfig.selected_scale_type || "major_pentatonic"));
  const [playbackTonic, setPlaybackTonic] = useState(normalizeTonic(baseSceneConfig.playback_tonic || baseSceneConfig.selected_tonic || "C"));
  const [compositionBpm, setCompositionBpm] = useState(COMPOSITION_BPM_DEFAULT);
  const [currentSegmentIndex, setCurrentSegmentIndex] = useState(0);
  const [allPlaced, setAllPlaced] = useState<CompositionPlacedCard[]>([]);
  const sceneConfig = useMemo(() => buildCompositionPuzzleSceneConfig({
    ...config,
    selected_meter: selectedMeter,
    meter: selectedMeter,
    slots_per_bar: slotsPerBarForMeter(selectedMeter),
    selected_tonic: selectedTonic,
    tonic: selectedTonic,
    selected_scale_type: selectedScaleType,
    scale_type: selectedScaleType,
    melody_cards: Array.isArray(config.melody_cards) && config.melody_cards.length
      ? config.melody_cards
      : generateScaleNoteNames(selectedTonic, selectedScaleType),
    playback_tonic: selectedTonic,
    current_segment_index: currentSegmentIndex,
    all_placed: allPlaced
  }), [config, selectedMeter, selectedTonic, selectedScaleType, currentSegmentIndex, allPlaced]);
  const [snapshot, setSnapshot] = useState<CompositionPuzzleSnapshot>(() => initialCompositionPuzzleSnapshot(sceneConfig));
  const [finished, setFinished] = useState(false);
  const [coverVisible, setCoverVisible] = useState(true);
  const [compositionPhase, setCompositionPhase] = useState<"rhythm" | "melody">("rhythm");
  const shelfCards = compositionShelfCards(sceneConfig);
  const rhythmShelfCards = shelfCards.filter((card) => card.rhythm);
  const melodyShelfCards = shelfCards.filter((card) => card.pitch);
  const selectedSlot = snapshot.segmentPlaced[snapshot.selectedSlotIndex] || null;
  const rhythmComplete = snapshot.segmentFilledSlots >= snapshot.segmentSlotCount;
  const melodyComplete = compositionMelodyFilled(snapshot.segmentPlaced);
  const meterOptions = sceneConfig.meter_options || ["2/4", "3/4", "4/4"];
  const tonicOptions = sceneConfig.tonic_options || ["C", "D", "E", "F", "G", "A"];
  const scaleOptions = sceneConfig.scale_options || ["major", "minor", "major_pentatonic"];

  useEffect(() => {
    callbacksRef.current = { setFeedback, onProgress, onComplete };
  }, [setFeedback, onProgress, onComplete]);

  useEffect(() => {
    controllerRef.current?.setPlaybackTonic(playbackTonic);
  }, [playbackTonic]);

  useEffect(() => {
    if (!stageRef.current) return undefined;
    stageRef.current.innerHTML = "";
    const controller = mountCompositionPuzzleScene(stageRef.current, sceneConfig, (event: CompositionPuzzleSceneEvent) => {
      setSnapshot(event.snapshot);
      setAllPlaced(event.snapshot.placed);
      if (event.message) callbacksRef.current.setFeedback(event.message);
      callbacksRef.current.onProgress(event.snapshot.filledSlots, Math.round(event.snapshot.progress * 100));
      if (event.type === "mission_success") {
        setFinished(true);
        callbacksRef.current.onComplete();
      }
    });
    controllerRef.current = controller;
    setFinished(false);
    setCompositionPhase("rhythm");
    setSnapshot(initialCompositionPuzzleSnapshot(sceneConfig));
    return () => controller.destroy();
  }, [config, selectedMeter, selectedTonic, selectedScaleType, currentSegmentIndex]);

  const start = () => {
    setCoverVisible(false);
    setFeedback("先选择节奏符号，拼满作品轨道。");
  };
  const placeCard = (card: CompositionPlacedCard) => {
    setCoverVisible(false);
    setFinished(false);
    controllerRef.current?.placeCard(card);
    setFeedback("节奏已放入作品轨道。");
    if (snapshot.segmentFilledSlots + Math.max(1, Number(card.beats || 1)) >= snapshot.segmentSlotCount) setCompositionPhase("melody");
  };
  const selectSlot = (index: number) => {
    controllerRef.current?.selectSlot(index);
    setCompositionPhase("melody");
    setFeedback("选择音名（简谱），把旋律填进这个节奏格。");
  };
  const fillPitch = (pitch: string) => {
    setCoverVisible(false);
    controllerRef.current?.fillPitch(pitch);
    setFeedback(`${numberedNoteLabel(pitch, selectedTonic)} 已填入当前节奏格。`);
  };
  const audition = () => {
    setCoverVisible(false);
    void playCompositionPhrase(snapshot.segmentPlaced, sceneConfig.selected_tonic, playbackTonic, compositionBpm);
    controllerRef.current?.audition(compositionBpm);
    setFeedback(`正在试听第 ${currentSegmentIndex + 1} 段：${compositionBpm} BPM`);
  };
  const auditionFull = () => {
    setCoverVisible(false);
    void playCompositionPhrase(allPlaced, sceneConfig.selected_tonic, playbackTonic, compositionBpm);
    setFeedback(`正在试听完整作品：${compositionTotalBars} 小节`);
  };
  const check = () => {
    controllerRef.current?.check(snapshot.teacherConfirmed);
    setFeedback("正在检查创编约束。");
  };
  const teacherConfirm = () => {
    controllerRef.current?.teacherConfirm();
    setFeedback("教师已确认创编理由。");
  };
  const reset = () => {
    setFinished(false);
    setCoverVisible(false);
    setCompositionPhase("rhythm");
    setAllPlaced([]);
    setCurrentSegmentIndex(0);
    controllerRef.current?.reset();
    setSnapshot(initialCompositionPuzzleSnapshot(sceneConfig));
    setFeedback("重新选择素材卡。");
  };
  const undo = () => {
    setCoverVisible(false);
    controllerRef.current?.undo();
    setFeedback("已撤回最后一张素材卡。");
  };
  const updateCompositionBpm = (value: number) => {
    setCompositionBpm(clampCompositionBpm(value));
  };

  const score = finished ? Math.max(300, 1000 - snapshot.attempts * 80) : Math.round(snapshot.progress * 420);
  const stars = starsForScore(score, finished);
  const arcadePhase: ArcadeAssetState = finished ? "win" : snapshot.status === "failed" ? "miss" : snapshot.segmentPlaced.length ? "hit" : "idle";
  const transferPrompt = resultTransferPrompt(state, "把作品拍读、唱出或用课堂乐器演一遍，并说明它满足了哪些音乐约束。");
  const progressText = `${snapshot.filledSlots}/${snapshot.slotCount}`;
  const segmentProgressText = `${snapshot.segmentFilledSlots}/${snapshot.segmentSlotCount}`;
  const compositionSegments = Math.max(1, Number(sceneConfig.composition_segments || 1));
  const compositionTotalBars = Math.max(1, Number(sceneConfig.composition_total_bars || sceneConfig.phrase_length_bars || 2));
  const hasMultipleSegments = compositionSegments > 1;
  const changeSegment = (index: number) => {
    const next = Math.max(0, Math.min(compositionSegments - 1, index));
    setCurrentSegmentIndex(next);
    setCompositionPhase("rhythm");
    setCoverVisible(false);
    setFeedback(`已切到第 ${next + 1} 段，继续创编。`);
  };

  return (
    <ArcadeLevelFlow state={state} phase={arcadePhase}>
      <div
        className="composition-puzzle-runtime"
        data-scene="composition_puzzle_scene"
        data-engine="phaser_2d"
        data-hud="constraint_checklist_progress"
      >
        {coverVisible && !finished ? (
          <ArcadeStartOverlay
            state={state}
            title="拖卡通关"
            subtitle={compositionModeCopy(String(sceneConfig.mode))}
            actionLabel="开始"
            onStart={start}
          />
        ) : null}
        <div className="composition-top-hud" aria-label="创编状态">
          <div>
            <Text className="composition-title">拼图创编工坊</Text>
            <span>{compositionModeShort(String(sceneConfig.mode))}</span>
          </div>
          <div className="composition-hud-chips">
            <strong>{selectedMeter}</strong>
            <span>{scaleTypeLabel(selectedScaleType)} · 1={selectedTonic}</span>
            <span>{compositionPhase === "rhythm" ? `本段 ${segmentProgressText}` : melodyComplete ? "音名（简谱）完成" : "填音中"}</span>
            <span>全曲 {progressText}</span>
            <b>{stars} 星</b>
          </div>
        </div>

        <div className="composition-game-board">
          <div className="composition-phaser-shell">
            <div ref={stageRef} className="composition-phaser-stage" aria-label="拼图创编 Phaser 作品轨道" />
          </div>
          <aside className="composition-side-panel" aria-label="创编设置和规则">
            <div className="composition-select-grid">
              <label>
                <span>节拍</span>
                <Select.Root value={selectedMeter} onValueChange={(value) => setSelectedMeter(value as CompositionMeter)}>
                  <Select.Trigger />
                  <Select.Content>
                    {meterOptions.map((meter) => <Select.Item key={meter} value={meter}>{meter}</Select.Item>)}
                  </Select.Content>
                </Select.Root>
              </label>
              <label>
                <span>调式</span>
                <Select.Root value={selectedScaleType} onValueChange={(value) => setSelectedScaleType(normalizeScaleType(value))}>
                  <Select.Trigger />
                  <Select.Content>
                    {scaleOptions.map((scale) => <Select.Item key={scale} value={scale}>{scaleTypeLabel(scale)}</Select.Item>)}
                  </Select.Content>
                </Select.Root>
              </label>
              <label>
                <span>主音</span>
                <Select.Root value={selectedTonic} onValueChange={(value) => {
                  const next = normalizeTonic(value);
                  setSelectedTonic(next);
                  setPlaybackTonic(next);
                }}>
                  <Select.Trigger />
                  <Select.Content>
                    {tonicOptions.map((tonic) => <Select.Item key={tonic} value={tonic}>{tonic}</Select.Item>)}
                  </Select.Content>
                </Select.Root>
              </label>
              <label>
                <span>播放调</span>
                <Select.Root value={playbackTonic} onValueChange={(value) => setPlaybackTonic(normalizeTonic(value))}>
                  <Select.Trigger />
                  <Select.Content>
                    {tonicOptions.map((tonic) => <Select.Item key={tonic} value={tonic}>{tonic}</Select.Item>)}
                  </Select.Content>
                </Select.Root>
              </label>
            </div>
            {hasMultipleSegments ? (
              <div className="composition-segment-switcher" aria-label="创编段落">
                {Array.from({ length: compositionSegments }).map((_, index) => (
                  <button
                    key={index}
                    type="button"
                    className={index === currentSegmentIndex ? "active" : ""}
                    onClick={() => changeSegment(index)}
                  >
                    第 {index + 1} 段
                  </button>
                ))}
              </div>
            ) : null}
            <div className="composition-checklist">
              {snapshot.checks.map((check) => (
                <span key={check.id} className={check.passed ? "passed" : ""}>
                  {check.passed ? "✓" : "○"} {check.label}
                </span>
              ))}
            </div>
          </aside>
        </div>

        <div className="composition-control-dock">
          <div className="composition-phase-tabs" aria-label="创编步骤">
            <button type="button" className={compositionPhase === "rhythm" ? "active" : ""} onClick={() => setCompositionPhase("rhythm")}>1 节奏</button>
            <button type="button" className={compositionPhase === "melody" ? "active" : ""} onClick={() => setCompositionPhase("melody")} disabled={!snapshot.segmentPlaced.length}>2 音名（简谱）</button>
          </div>

          {compositionPhase === "rhythm" && rhythmShelfCards.length ? (
            <div className="composition-card-shelf">
              <Text className="eyebrow">先拼节奏</Text>
              <div className="composition-card-grid">
                {rhythmShelfCards.map((card) => (
                  <Button
                    key={card.id}
                    className="composition-material-card rhythm"
                    variant="soft"
                    color="amber"
                    onClick={() => placeCard(card)}
                    disabled={finished}
                  >
                    <RhythmNotationIcon rhythm={card.rhythm || card.id} />
                  </Button>
                ))}
              </div>
            </div>
          ) : null}

          {compositionPhase === "melody" && melodyShelfCards.length ? (
            <div className="composition-card-shelf melody">
              <Text className="eyebrow">{selectedSlot ? "填入当前节奏格" : "先点选一个节奏格"}</Text>
              <div className="composition-slot-picker" aria-label="选择节奏格">
                {snapshot.segmentPlaced.map((slot, index) => (
                  <button key={`${slot.id}_${index}`} type="button" className={snapshot.selectedSlotIndex === index ? "active" : ""} onClick={() => selectSlot(index)}>
                    {index + 1}
                  </button>
                ))}
              </div>
              <div className="composition-card-grid melody">
                {melodyShelfCards.map((card) => {
                  return (
                    <Button
                      key={card.id}
                      className="composition-material-card melody"
                      variant="soft"
                      color="teal"
                      onClick={() => card.pitch && fillPitch(card.pitch)}
                      disabled={finished || !selectedSlot || rhythmAttackCount(selectedSlot.rhythm || selectedSlot.id) === 0}
                    >
                      {numberedNoteLabel(card.pitch, selectedTonic)}
                    </Button>
                  );
                })}
              </div>
            </div>
          ) : null}

          <label className="composition-bpm-control">
            <span className="composition-bpm-head">
              <span>速度</span>
              <strong>{compositionBpm} BPM</strong>
            </span>
            <input
              type="range"
              min={COMPOSITION_BPM_MIN}
              max={COMPOSITION_BPM_MAX}
              step={1}
              value={compositionBpm}
              onInput={(event) => updateCompositionBpm(Number(event.currentTarget.value))}
              onChange={(event) => updateCompositionBpm(Number(event.currentTarget.value))}
            />
          </label>

          <Flex className="composition-actions" gap="2" wrap="wrap">
            <Button className="game-action primary" size="3" onClick={audition} disabled={!snapshot.segmentPlaced.length || finished}>
              <Volume2 size={16} />
              试听本段
            </Button>
            <Button className="game-action primary" size="3" onClick={auditionFull} disabled={!snapshot.placed.length || finished}>
              <Volume2 size={16} />
              完整试听
            </Button>
            <Button className="game-action primary" size="3" onClick={check} disabled={!snapshot.placed.length || finished}>
              <Check size={16} />
              检查
            </Button>
            <Button className="game-action" size="3" variant="soft" onClick={() => setCompositionPhase(compositionPhase === "rhythm" && rhythmComplete ? "melody" : "rhythm")} disabled={finished || (compositionPhase === "rhythm" && !rhythmComplete)}>
              {compositionPhase === "rhythm" ? "填音" : "节奏"}
            </Button>
            <Button className="game-action" size="3" variant="soft" onClick={undo} disabled={!snapshot.segmentPlaced.length || finished}>
              <Undo2 size={16} />
              撤回
            </Button>
            <Button className="game-action" size="3" variant="soft" onClick={reset}>
              <RotateCcw size={16} />
              重来
            </Button>
            <Button className="game-action" size="3" variant="soft" onClick={teacherConfirm} disabled={finished || !sceneConfig.teacher_confirm_required}>
              确认
            </Button>
          </Flex>
        </div>

        {finished ? (
          <ArcadeResultPanel
            state={state}
            success
            title="创编完成"
            prompt={transferPrompt}
            score={score}
            stars={stars}
            badges={[["模式", compositionModeShort(String(sceneConfig.mode))], ["奖励", "创编徽章"]]}
            onReplay={reset}
            nextLabel="再来"
          />
        ) : null}

        <details className="guardian-teacher-details composition-teacher-details">
          <summary>教师确认</summary>
          <p>学生说明音名（简谱）和节奏型后点击确认。</p>
        </details>
      </div>
    </ArcadeLevelFlow>
  );
}

function initialCompositionPuzzleSnapshot(config: ReturnType<typeof buildCompositionPuzzleSceneConfig>): CompositionPuzzleSnapshot {
  const checks = evaluateCompositionPuzzleChecks(config, [], false, false);
  return {
    status: "ready",
    placed: [],
    segmentPlaced: [],
    checks,
    progress: 0,
    attempts: 0,
    score: 0,
    message: "选择素材卡",
    teacherConfirmed: false,
    auditioned: false,
    filledSlots: 0,
    slotCount: config.total_slots || (config.composition_total_bars || config.phrase_length_bars || 2) * (config.slots_per_bar || 4),
    segmentFilledSlots: 0,
    segmentSlotCount: config.segment_slots || (config.phrase_length_bars || 2) * (config.slots_per_bar || 4),
    currentSegmentIndex: config.current_segment_index || 0,
    compositionSegments: config.composition_segments || 1,
    totalBars: config.composition_total_bars || config.phrase_length_bars || 2,
    selectedSlotIndex: -1
  };
}

function compositionShelfCards(config: ReturnType<typeof buildCompositionPuzzleSceneConfig>): CompositionPlacedCard[] {
  const rhythmCards: CompositionPlacedCard[] = (config.rhythm_cards || []).map((item) => {
    if (typeof item === "string") {
      return { id: item, label: rhythmCardLabel(item), rhythm: item, beats: rhythmCardBeats(item), attackCount: rhythmAttackCount(item), pitches: [] };
    }
    return { id: item.id, label: rhythmCardLabel(item.id || item.label), rhythm: item.id, beats: Number(item.beats || rhythmCardBeats(item.id)), attackCount: rhythmAttackCount(item.id), pitches: [] };
  });
  const melodyCards: CompositionPlacedCard[] = (config.melody_cards || []).map((pitch) => ({ id: `pitch_${pitch}`, label: numberedNoteLabel(pitch, config.selected_tonic), pitch, beats: 1 }));
  if (config.mode === "rhythm_puzzle_composition") return rhythmCards;
  if (config.mode === "melody_puzzle_creation") return melodyCards;
  return rhythmCards.slice(0, 6).concat(melodyCards.slice(0, 5));
}

function playCompositionPhrase(cards: CompositionPlacedCard[], fromTonic = "C", playbackTonic = "C", bpm = COMPOSITION_BPM_DEFAULT) {
  const beatSeconds = beatSecondsForBpm(bpm);
  let cursor = 0;
  const events: Array<{ offset: number; start: number; duration: number }> = [];
  cards.forEach((card, index) => {
    const pattern = rhythmPattern(card.rhythm || card.id);
    if (!rhythmAttackCount(card.rhythm || card.id)) {
      cursor += beatSeconds;
      return;
    }
    const pitches = card.pitches?.length ? card.pitches : card.pitch ? [card.pitch] : [];
    let pitchIndex = 0;
    pattern.forEach((duration) => {
      const noteDuration = duration === "eighth" ? beatSeconds / 2 : duration === "sixteenth" ? beatSeconds / 4 : beatSeconds;
      if (duration === "rest") {
        cursor += noteDuration;
        return;
      }
      const pitch = pitches[pitchIndex];
      if (pitch) {
        const shiftedPitch = transposeNoteName(pitch, fromTonic, playbackTonic);
        events.push({
          offset: pitchOffset(shiftedPitch) ?? [0, 2, 4, 7][(index + pitchIndex) % 4],
          start: cursor,
          duration: Math.max(0.09, noteDuration * 0.78)
        });
      }
      pitchIndex += 1;
      cursor += noteDuration;
    });
  });
  if (!events.length) return false;
  return playToneSequence(events.map((event) => event.offset), "triangle", beatSeconds / 2, { events });
}

function pitchOffset(pitch?: string) {
  const catalogPitch = resolvePitchToken(pitch);
  if (catalogPitch) return catalogPitch.semitone;
  return ({
    C: 0,
    D: 2,
    "D#": 3,
    E: 4,
    F: 5,
    "F#": 6,
    G: 7,
    "G#": 8,
    A: 9,
    "A#": 10,
    B: 11,
    "C'": 12
  } as Record<string, number>)[String(pitch || "")];
}

function rhythmCardLabel(id: string) {
  return {
    quarter: "四分",
    eighth_pair: "二八",
    rest: "休止",
    half: "二分",
    dotted_quarter: "附点四分",
    syncopation: "小切分",
    sixteenth_four: "四个十六",
    eighth_sixteenth: "八十六",
    eighth_sixteenth_sixteenth: "八十六",
    sixteenth_eighth: "十六八",
    sixteenth_sixteenth_eighth: "十六八"
  }[id] || id;
}

function rhythmCardBeats(id: string) {
  return id === "half" ? 2 : 1;
}

function cardLabelForHud(card: CompositionPlacedCard) {
  return card.pitch ? noteLabel(card.pitch) : card.label;
}

function RhythmNotationIcon({ rhythm }: { rhythm: string }) {
  return <RhythmNotation rhythm={rhythm} className="composition-rhythm-svg" />;
}

function scaleTypeLabel(scale: string) {
  return {
    major: "大调",
    minor: "小调",
    major_pentatonic: "五声"
  }[scale] || "五声";
}

function compositionModeCopy(mode: string) {
  return {
    rhythm_puzzle_composition: "选节奏，填满轨道。",
    melody_puzzle_creation: "选音名（简谱），连成短句。",
    melody_rhythm_puzzle: "节奏 + 音名（简谱），拼成短句。"
  }[mode] || "拖卡创编。";
}

function compositionModeShort(mode: string) {
  return {
    rhythm_puzzle_composition: "节奏",
    melody_puzzle_creation: "音名（简谱）",
    melody_rhythm_puzzle: "节奏 + 音名"
  }[mode] || "创编";
}

function TimbreDetectiveGame({ state, setFeedback, onProgress, onComplete }: RuntimeProps) {
  const configKey = stableConfigKey({ config: state.config ?? {}, workflow: state.workflow ?? {} });
  const config = useMemo(() => mergeTimbreEntityExecutionConfig(state, state.config ?? {}), [configKey]);
  const sceneConfigRef = useRef(buildTimbreDetectiveSceneConfig(config));
  const controllerRef = useRef<TimbreDetectiveController | null>(null);
  const stageRef = useRef<HTMLDivElement | null>(null);
  const callbacksRef = useRef({ setFeedback, onProgress, onComplete });
  const cases = Array.isArray(config.clue_cases)
    ? (config.clue_cases as Round[])
    : Array.isArray(config.timbre_rounds)
      ? (config.timbre_rounds as Round[])
      : [];
  const suspectCards = Array.isArray(config.suspect_cards) ? (config.suspect_cards as Array<Record<string, string>>) : [];
  const evidenceTokens = Array.isArray(config.evidence_tokens) ? (config.evidence_tokens as Array<Record<string, string>>) : [];
  const skinMode = String(config.skin_play_mode || "casebook");
  const [index, setIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState("");
  const [selectedEvidence, setSelectedEvidence] = useState<string[]>([]);
  const [selectedContrastEvidence, setSelectedContrastEvidence] = useState("");
  const [heard, setHeard] = useState(false);
  const [lensOpen, setLensOpen] = useState(false);
  const [coverVisible, setCoverVisible] = useState(true);
  const [caseState, setCaseState] = useState<TimbreCaseState>("open");
  const [solvedCases, setSolvedCases] = useState(0);
  const round =
    cases[index % Math.max(1, cases.length)] ??
    ({
      prompt: "先听声音证物，再找出嫌疑乐器。",
      candidates: Array.isArray(config.instrument_pool) ? (config.instrument_pool as string[]) : [],
      evidence_options: Array.isArray(config.timbre_traits) ? (config.timbre_traits as string[]) : [],
      evidence_answer: [],
      answer: ""
    } satisfies Round);
  const totalCases = Math.max(1, cases.length);
  const evidenceNeed = Number(config.evidence_required || 1);
  const comparisonRequired = Boolean(round.comparison_reason_required && round.compare_with);
  const contrastOptions = round.contrast_evidence_options?.length ? round.contrast_evidence_options : round.evidence_options ?? [];
  const selectedEvidencePhrase = selectedEvidence.join("、") || "比较线索";
  const comparisonSentence = comparisonRequired
    ? `第一声更像“${selectedAnswer || round.target || "目标声"}”，因为它有“${selectedEvidencePhrase}”；不像“${round.compare_with || "对照声"}”，因为“${selectedContrastEvidence || "对照证据"}”。`
    : `我判断是“${selectedAnswer || "目标声"}”，因为它听起来有“${selectedEvidencePhrase}”。`;
  const visibleSuspects = (round.candidates ?? []).map((candidate) => {
    const card = suspectCards.find((item) => item.label === candidate || item.id === candidate);
    return card ?? { id: candidate, label: candidate, hint: "等待证据", visual: "声纹" };
  });
  const visibleEvidence = (round.evidence_options ?? []).map((trait) => {
    const token = evidenceTokens.find((item) => item.label === trait || item.id === trait);
    return token ?? { id: trait, label: trait, teacher_prompt: "这个词能说明你听到的声音吗？" };
  });
  const transferPrompt = resultTransferPrompt(state, "用一个音色词解释为什么是这个乐器/家族。");
  const detectiveScore = solvedCases * 280 + selectedEvidence.length * 80 + (selectedContrastEvidence ? 70 : 0) + (caseState === "solved" ? 240 : 0);
  const detectiveStars = starsForPercent(Math.round((solvedCases / totalCases) * 100), solvedCases >= totalCases);
  const arcadePhase: ArcadeAssetState = caseState === "solved" ? "win" : caseState === "wrong" || caseState === "evidence_missing" ? "miss" : selectedEvidence.length > 0 ? "hit" : "idle";
  const snapshot: TimbreDetectiveSnapshot = {
    status: caseState,
    currentCase: index % totalCases,
    totalCases,
    heard,
    selectedAnswer,
    selectedEvidence,
    solvedCases,
    score: detectiveScore,
    combo: selectedEvidence.length,
    evidenceNeed,
    message: timbreShortFeedback(caseState, selectedAnswer, selectedEvidence.length, evidenceNeed)
  };

  useEffect(() => onProgress(index % totalCases, solvedCases), [index, solvedCases, totalCases]);

  useEffect(() => {
    callbacksRef.current = { setFeedback, onProgress, onComplete };
  }, [onComplete, onProgress, setFeedback]);

  useEffect(() => {
    if (!stageRef.current) return;
    stageRef.current.innerHTML = "";
    const controller = mountTimbreDetectiveScene(
      stageRef.current,
      sceneConfigRef.current,
      snapshot,
      round,
      visibleSuspects,
      visibleEvidence,
      handleSceneEvent
    );
    controllerRef.current = controller;
    return () => {
      controller.destroy();
      controllerRef.current = null;
    };
  }, []);

  useEffect(() => {
    controllerRef.current?.setSnapshot(snapshot, round, visibleSuspects, visibleEvidence);
  }, [snapshot.status, snapshot.currentCase, snapshot.heard, snapshot.selectedAnswer, snapshot.selectedEvidence.join("|"), snapshot.solvedCases]);

  const nextRound = () => {
    setIndex((value) => value + 1);
    setSelectedAnswer("");
    setSelectedEvidence([]);
    setSelectedContrastEvidence("");
    setHeard(false);
    setLensOpen(false);
    setCaseState("open");
    setCoverVisible(false);
    setFeedback("听声音证物");
  };

  const playEvidence = () => {
    setCoverVisible(false);
    controllerRef.current?.playListenFx(round.audio_profile, round.compare_audio_profile);
    const primaryAudioUrl = timbreRoundAudioUrl(round);
    const compareAudioUrl = timbreRoundCompareAudioUrl(round);
    const played = playTimbreProfile(round.audio_profile || profileFromAudioUrl(primaryAudioUrl), {
      audioUrl: primaryAudioUrl,
      instrument: String(round.target || round.answer || round.family || "")
    });
    if (played && (round.compare_audio_profile || compareAudioUrl)) {
      window.setTimeout(
        () => playTimbreProfile(round.compare_audio_profile || profileFromAudioUrl(compareAudioUrl), {
          audioUrl: compareAudioUrl,
          instrument: String(round.compare_with || "")
        }),
        780
      );
    }
    if (!played) {
      setFeedback("可由教师现场示范");
      return;
    }
    setHeard(true);
    setFeedback(round.compare_audio_profile ? "比较两声" : "找线索");
  };

  function handleSceneEvent(event: TimbreDetectiveSceneEvent) {
    if (event.type === "listen_requested") {
      playEvidence();
      return;
    }
    if (event.type === "suspect_selected" && event.suspect) {
      setSelectedAnswer(event.suspect);
      setCaseState("open");
      callbacksRef.current.setFeedback(event.message || "已锁定嫌疑");
      return;
    }
    if (event.type === "evidence_selected" && event.evidence) {
      setSelectedEvidence(event.evidence);
      setCaseState("open");
      callbacksRef.current.setFeedback(event.message || "证据已贴上");
      return;
    }
    if (event.message) callbacksRef.current.setFeedback(event.message);
  }

  const submitCase = () => {
    if (!heard) {
      setCaseState("evidence_missing");
      setFeedback("先听声音证物");
      controllerRef.current?.showResult("evidence_missing");
      return;
    }
    if (!selectedAnswer) {
      setCaseState("wrong");
      setFeedback("先找嫌疑");
      controllerRef.current?.showResult("wrong");
      return;
    }
    if (selectedEvidence.length < evidenceNeed) {
      setCaseState("evidence_missing");
      setFeedback("还差一个可听见的比较线索");
      controllerRef.current?.showResult("evidence_missing");
      return;
    }
    if (comparisonRequired && !selectedContrastEvidence) {
      setCaseState("evidence_missing");
      setFeedback("还要选择一条对照比较线索");
      controllerRef.current?.showResult("evidence_missing");
      return;
    }
    const result = resolveTimbreCaseJudgement(round, selectedAnswer, selectedEvidence, selectedContrastEvidence, evidenceNeed, heard);
    if (result.judgement === "solved") {
      const nextSolved = Math.min(totalCases, solvedCases + 1);
      setSolvedCases(nextSolved);
      setCaseState("solved");
      setFeedback("破案成功");
      controllerRef.current?.showResult("solved");
      if (nextSolved >= totalCases) onComplete();
      return;
    }
    if (!result.answerOk) {
      setCaseState("wrong");
      setFeedback("嫌疑错了");
      controllerRef.current?.showResult("wrong");
      return;
    }
    if (comparisonRequired && !result.contrastOk) {
      setCaseState("evidence_missing");
      setFeedback("换一条更能说明两声差异的线索");
      controllerRef.current?.showResult("evidence_missing");
      return;
    }
    setCaseState("evidence_missing");
    setFeedback("再找一条可听见的比较线索");
    controllerRef.current?.showResult("evidence_missing");
  };

  const resetCase = () => {
    setSelectedAnswer("");
    setSelectedEvidence([]);
    setSelectedContrastEvidence("");
    setHeard(false);
    setLensOpen(false);
    setCaseState("open");
    controllerRef.current?.resetBoard();
    setFeedback("重新侦查");
  };

  return (
    <ArcadeLevelFlow state={state} phase={arcadePhase}>
      <div
        className={`timbre-desk-runtime dynamic-case-scene ${skinMode}`}
        data-engine="phaser_2d"
        data-scene="timbre_detective_scene"
        data-detective-hud="true"
      >
        <div className="timbre-game-viewport">
          <div className="timbre-phaser-shell">
            <div ref={stageRef} className="timbre-phaser-stage" aria-label="音色侦探 Phaser 动态破案舞台" />
          </div>

          <div className="timbre-top-strip" aria-label="案件状态">
            <Badge color={caseState === "solved" ? "green" : caseState === "wrong" ? "ruby" : "amber"} variant="solid">
              {timbreCaseStateLabel(caseState)}
            </Badge>
            <Badge color="teal" variant="soft">案件 {Math.min(index + 1, totalCases)}/{totalCases}</Badge>
            <Badge color="blue" variant="soft">证据 {selectedEvidence.length}/{evidenceNeed}</Badge>
            {selectedAnswer ? <Badge color="amber" variant="soft">嫌疑 {selectedAnswer}</Badge> : null}
            <span className="timbre-feedback-chip">{timbreShortFeedback(caseState, selectedAnswer, selectedEvidence.length, evidenceNeed)}</span>
          </div>

          <div className="timbre-action-pad" aria-label="推理操作">
            <Button className="game-action primary" size="3" onClick={playEvidence}>
              <Volume2 size={16} />
              听证物
            </Button>
            <Button className="game-action primary" size="3" onClick={submitCase}>提交推理</Button>
            <Button className="game-action" size="3" variant="soft" onClick={() => {
              setLensOpen((value) => !value);
              setFeedback(lensOpen ? "继续听证物" : "观察起音和延音");
            }}>
              <Search size={16} />
              放大镜
            </Button>
            <Button className="game-action" size="3" variant="soft" onClick={resetCase}>
              <RotateCcw size={16} />
              重试
            </Button>
            <Button className="game-action" size="3" variant="soft" onClick={nextRound}>下一案</Button>
          </div>

          {comparisonRequired && (heard || selectedAnswer || selectedEvidence.length > 0) ? (
            <TimbreReasonPanel
              round={round}
              selectedAnswer={selectedAnswer}
              selectedEvidence={selectedEvidence}
              selectedContrastEvidence={selectedContrastEvidence}
              contrastOptions={contrastOptions}
              disabled={caseState === "solved"}
              onSelect={(trait) => {
                setSelectedContrastEvidence(trait);
                setCaseState("open");
                setCoverVisible(false);
                setFeedback(`比较线索：${trait}`);
              }}
            />
          ) : null}

          {lensOpen ? <TimbreLensPanel round={round} selectedEvidence={selectedEvidence} /> : null}

          {coverVisible && !heard && !selectedAnswer && caseState === "open" ? (
            <ArcadeStartOverlay
              state={state}
              title="声音案卷开启"
              subtitle="点证物听声纹，在桌面上锁定嫌疑并贴上证据。"
              actionLabel="听声音证物"
              onStart={playEvidence}
            />
          ) : null}

          {config.ai_clue_enabled ? (
            <details className="teacher-ai-clue">
              <summary>教师辅助线索</summary>
              <p>{round.ai_teacher_clue || "教师可提示学生关注起音、延音和音色材质，但不要直接公布答案。"}</p>
            </details>
          ) : null}

          {caseState === "solved" ? (
            <ArcadeResultPanel
              state={state}
              success={caseState === "solved"}
              title="把比较线索说给同伴听"
              prompt={`${transferPrompt} ${comparisonSentence}`}
              score={detectiveScore}
              stars={detectiveStars}
              badges={[["已破案", `${solvedCases}/${totalCases}`], ["线索", selectedEvidencePhrase], ...(comparisonRequired ? [["对照", selectedContrastEvidence || "待补充"] as [string, string]] : [])]}
              onReplay={nextRound}
              nextLabel={solvedCases >= totalCases ? "再开一案" : "下一案"}
            />
          ) : null}
        </div>
      </div>
    </ArcadeLevelFlow>
  );
}

function timbreRoundAudioUrl(round: Round): string {
  return String(round.playback_url || round.audio_clip_url || round.audio_url || round.source_audio_url || round.audio_profile?.audio_url || round.audio_profile?.audio_clip_url || round.audio_profile?.source_audio_url || "").trim();
}

function timbreRoundCompareAudioUrl(round: Round): string {
  return String(round.compare_playback_url || round.compare_audio_clip_url || round.compare_audio_url || round.compare_source_audio_url || round.compare_audio_profile?.audio_url || round.compare_audio_profile?.audio_clip_url || round.compare_audio_profile?.source_audio_url || "").trim();
}

function profileFromAudioUrl(audioUrl: string) {
  return audioUrl ? { audio_url: audioUrl } : null;
}

function TimbreLensPanel({ round, selectedEvidence }: { round: Round; selectedEvidence: string[] }) {
  const profile = round.audio_profile ?? {};
  const compareProfile = round.compare_audio_profile ?? {};
  const brightness = Math.round(Number(profile.brightness ?? 0.55) * 100);
  const compareBrightness = Math.round(Number(compareProfile.brightness ?? 0.55) * 100);
  const attack = Number(profile.attack ?? 0.04);
  const compareAttack = Number(compareProfile.attack ?? attack);
  const release = Number(profile.release ?? 0.32);
  const compareRelease = Number(compareProfile.release ?? release);
  return (
    <div className="timbre-lens-panel" aria-label="音色放大镜线索">
      <span>
        <strong>起音</strong>
        {attack < compareAttack ? "第一声更直接" : attack > compareAttack ? "第一声进入更柔和" : "两声接近"}
      </span>
      <span>
        <strong>尾音</strong>
        {release > compareRelease ? "第一声保持更久" : release < compareRelease ? "第一声收得更快" : "两声接近"}
      </span>
      <span>
        <strong>相对亮度</strong>
        {brightness > compareBrightness ? "第一声更亮" : brightness < compareBrightness ? "第二声更亮" : "亮度接近"}
      </span>
      <em>{selectedEvidence.length ? `已选线索：${selectedEvidence.join("、")}` : "先听，再选比较线索"}</em>
    </div>
  );
}

function TimbreReasonPanel({
  round,
  selectedAnswer,
  selectedEvidence,
  selectedContrastEvidence,
  contrastOptions,
  disabled,
  onSelect
}: {
  round: Round;
  selectedAnswer: string;
  selectedEvidence: string[];
  selectedContrastEvidence: string;
  contrastOptions: string[];
  disabled: boolean;
  onSelect: (trait: string) => void;
}) {
  const target = selectedAnswer || round.target || "第一声";
  const contrast = round.compare_with || "对照声";
  const evidence = selectedEvidence.length ? selectedEvidence.join("、") : "先贴正向证据";
  const targetState = selectedAnswer ? "done" : "pending";
  const evidenceState = selectedEvidence.length ? "done" : "pending";
  const contrastState = selectedContrastEvidence ? "done" : "pending";
  return (
    <section className="timbre-reason-panel" aria-label="比较推理依据">
      <div className="timbre-reason-copy">
        <span>案卷批注 · 比较线索</span>
        <strong>{round.compare_prompt || `第一声更像${target}，还要说明为什么不像${contrast}。`}</strong>
        <p>
          更像<b>{target}</b>：<b>{evidence}</b>；对照线索：
          <b>{selectedContrastEvidence || "选一条相对差异"}</b>。
        </p>
      </div>
      <div className="timbre-reason-steps" aria-label="推理进度">
        <span data-step-state={targetState}>锁定：{selectedAnswer || "嫌疑对象"}</span>
        <span data-step-state={evidenceState}>像：{evidence}</span>
        <span data-step-state={contrastState}>不像：{selectedContrastEvidence || contrast}</span>
      </div>
      <div className="timbre-contrast-options" role="list" aria-label="不像对照声的依据">
        {contrastOptions.slice(0, 6).map((trait) => (
          <button
            key={trait}
            type="button"
            className={selectedContrastEvidence === trait ? "selected" : ""}
            onClick={() => onSelect(trait)}
            disabled={disabled}
            title={trait}
          >
            {shortTimbreCueLabel(trait)}
          </button>
        ))}
      </div>
    </section>
  );
}

function shortTimbreCueLabel(cue: string) {
  if (cue.includes("滑音")) return "滑音起伏";
  if (cue.includes("擦弦")) return "擦弦音头";
  if (cue.includes("稳定")) return "更稳定";
  if (cue.includes("明亮") || cue.includes("亮度") || cue.includes("高频")) return "更明亮";
  if (cue.includes("气流") || cue.includes("吹奏")) return "气流边缘";
  if (cue.includes("共鸣") && cue.includes("窄")) return "共鸣更窄";
  if (cue.includes("共鸣") && cue.includes("宽")) return "共鸣更宽";
  if (cue.includes("连贯")) return "线条连贯";
  return cue.length > 6 ? `${cue.slice(0, 6)}…` : cue;
}

function timbreCaseStateLabel(state: "open" | "solved" | "wrong" | "evidence_missing") {
  return {
    open: "侦查中",
    solved: "已破案",
    wrong: "再侦查",
    evidence_missing: "补证据"
  }[state];
}

function timbreShortFeedback(
  state: "open" | "solved" | "wrong" | "evidence_missing",
  selectedAnswer: string,
  evidenceCount: number,
  evidenceNeed: number
) {
  if (state === "solved") return "破案成功";
  if (state === "wrong") return selectedAnswer ? "嫌疑错了" : "先找嫌疑";
  if (state === "evidence_missing") return "证据不足";
  if (!selectedAnswer) return "找嫌疑";
  if (evidenceCount < evidenceNeed) return "贴证据";
  return "可提交";
}

function timbreReasonFeedback(state: StudentGameState, caseState: "open" | "solved" | "wrong" | "evidence_missing") {
  if (caseState === "solved") return reasonPrompt(state, "success", "证据成立：用音色词解释你的判断。");
  if (caseState === "wrong") return reasonPrompt(state, "wrong_source", "对象错了：复听发声方式和起音。");
  if (caseState === "evidence_missing") return reasonPrompt(state, "weak_evidence", "证据不足：换一个更能说明音色的词。");
  return "先听证物，再用“嫌疑对象 + 音色证据”破案。";
}

function evidenceIndexForLabel(label: string) {
  let total = 0;
  for (const char of label) total += char.charCodeAt(0);
  return 2 + (total % 6);
}

function GameControls({ controls }: { controls: Array<[string, () => unknown]> }) {
  return (
    <Flex className="game-controls" gap="3" wrap="wrap" mb="4">
      {controls.map(([label, onClick], index) => (
        <Button key={label} className={index <= 1 ? "game-action primary" : "game-action"} variant={index > 1 ? "soft" : "solid"} onClick={onClick}>
          {index === 0 ? <Volume2 size={16} /> : null}
          {label}
        </Button>
      ))}
    </Flex>
  );
}

function Hud({ items }: { items: Array<[string, string]> }) {
  return (
    <Flex gap="2" wrap="wrap">
      {items.map(([label, value]) => (
        <Badge key={label} color="teal" variant="soft">
          {label}：{value}
        </Badge>
      ))}
    </Flex>
  );
}

function stableConfigKey(value: unknown): string {
  return JSON.stringify(sortForStableKey(value));
}

function sortForStableKey(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(sortForStableKey);
  if (!value || typeof value !== "object") return value;
  return Object.keys(value as LooseRecord).sort().reduce<LooseRecord>((sorted, key) => {
    sorted[key] = sortForStableKey((value as LooseRecord)[key]);
    return sorted;
  }, {});
}

function stepLabel(step: string) {
  return {
    quarter: "四分",
    eighth_pair: "二八",
    rest: "休止",
    half: "二分",
    syncopation: "切分",
    sixteenth_four: "四个十六",
    eighth_sixteenth_sixteenth: "前八后十六",
    sixteenth_sixteenth_eighth: "前十六后八",
    eighth_sixteenth_sixteenth_eighth: "前八后十六 + 八"
  }[step] ?? step;
}
