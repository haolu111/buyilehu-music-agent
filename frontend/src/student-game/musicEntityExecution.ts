import type { GameVariantSpec, LooseRecord, MusicEntityExecution, StudentGameState } from "./types";
import { resolvePitchToken } from "../shared/pitchCatalog";

export function resolveMusicEntityExecution(state: StudentGameState): MusicEntityExecution {
  const workflow = state.workflow ?? {};
  return normalizeExecution(
    workflow.game_variant_spec ||
      workflow.gameplay_blueprint?.game_variant_spec ||
      workflow.render_spec?.music_entity_execution ||
      workflow.gameplay_blueprint?.music_entity_execution
  );
}

export function resolveVariantParameters(state: StudentGameState): LooseRecord {
  return resolveMusicEntityExecution(state).variant_parameters ?? {};
}

export function resolveEntitySlotBindings(state: StudentGameState): LooseRecord {
  const execution = resolveMusicEntityExecution(state);
  return execution.entity_application?.slot_bindings || execution.slot_bindings || {};
}

export function mergeMeterEntityExecutionConfig(state: StudentGameState, baseConfig: LooseRecord): LooseRecord {
  const { parameters, applicationParameters, slots } = executionParts(state);
  const merged: LooseRecord = { ...baseConfig, ...applicationParameters, ...parameters };
  const accentPattern = stringArray(slots["meter.accent_pattern"]);
  const beatCount = numberValue(slots["meter.beat_count"]);
  const meter = stringValue(merged.meter);
  const beatsFromMeter = meter ? numberValue(meter.split("/")[0]) : undefined;
  const beatsPerBar = beatCount ?? beatsFromMeter;
  if (beatsPerBar) merged.beats_per_bar = beatsPerBar;
  if (accentPattern.length) merged.accent_pattern = accentPattern;
  const targetBeats = numberArray(merged.target_beats);
  if (!targetBeats.length && accentPattern.length) {
    merged.target_beats = accentPattern
      .map((accent, index) => accent === "strong" ? index + 1 : 0)
      .filter((beat) => beat > 0);
  }
  return merged;
}

export function mergeRhythmEntityExecutionConfig(state: StudentGameState, baseConfig: LooseRecord): LooseRecord {
  const execution = resolveMusicEntityExecution(state);
  const { parameters, applicationParameters, slots } = executionParts(state);
  const merged: LooseRecord = { ...baseConfig, ...applicationParameters, ...parameters };
  if (requiresEntityConfirmation(execution)) {
    restoreBaseValue(merged, baseConfig, "pattern_steps");
    restoreBaseValue(merged, baseConfig, "pattern_timeline");
    restoreBaseValue(merged, baseConfig, "round_patches");
    merged.music_entity_confirmation_required = true;
    merged.music_entity_confirmation_reason = confirmationReason(execution);
    const pendingValue = pendingConfirmationValue(execution);
    if (pendingValue.length) merged.pending_music_entity_value = pendingValue;
    return merged;
  }
  const patternSteps = stringArray(
    slots["rhythm.pattern_steps"] ?? parameters.pattern_steps ?? applicationParameters.pattern_steps ?? merged.pattern_steps
  );
  if (patternSteps.length) merged.pattern_steps = patternSteps;
  const durationBeats = numberArray(slots["rhythm.duration_beats"]);
  if (durationBeats.length && patternSteps.length) {
    let currentBeat = 0;
    merged.pattern_timeline = patternSteps.flatMap((step, index) => {
      const items = rhythmTimelineItems(step, durationBeats[index] ?? 1, currentBeat);
      currentBeat += durationBeats[index] ?? items.reduce((sum, item) => sum + Number(item.duration_beats || 0), 0);
      return items;
    });
  }
  const roundPatches = isRecord(merged.round_patches) ? { ...merged.round_patches } : {};
  Object.entries(slots).forEach(([key, value]) => {
    const match = /^round_(\d+)\.target_rhythm$/.exec(key);
    const roundSteps = stringArray(value);
    if (!match || !roundSteps.length) return;
    roundPatches[`round_${match[1]}`] = { pattern_steps: roundSteps };
  });
  if (Object.keys(roundPatches).length) merged.round_patches = roundPatches;
  return merged;
}

export function mergePitchEntityExecutionConfig(state: StudentGameState, baseConfig: LooseRecord): LooseRecord {
  const { parameters, applicationParameters, slots } = executionParts(state);
  const merged: LooseRecord = { ...baseConfig, ...applicationParameters, ...parameters };
  const pitchRange = stringArray(
    parameters.pitch_range ?? applicationParameters.pitch_range ?? slots["round_1.target_melody"] ?? merged.pitch_range
  );
  if (pitchRange.length) merged.pitch_range = pitchRange;
  const roundSequences = roundSlotSequences(slots, "target_melody");
  if (roundSequences.length) {
    const rounds = paddedRounds(merged.pitch_rounds, Math.max(...roundSequences.map((item) => item.round)));
    roundSequences.forEach(({ round, sequence }) => {
      rounds[round - 1] = {
      id: `entity_pitch_${round}`,
      sequence,
      labels: sequence,
      midi_offsets: sequence.map(solfegeMidiOffset),
      answer: pitchRoundAnswer(sequence, merged)
      };
    });
    merged.pitch_rounds = rounds;
    if (!pitchRange.length) merged.pitch_range = uniqueStrings(roundSequences.flatMap((item) => item.sequence));
  }
  return merged;
}

export function mergeSolfegeEntityExecutionConfig(state: StudentGameState, baseConfig: LooseRecord): LooseRecord {
  const { parameters, applicationParameters, slots } = executionParts(state);
  const merged: LooseRecord = { ...baseConfig, ...applicationParameters, ...parameters };
  const targetSolfege = stringArray(
    parameters.target_solfege ?? applicationParameters.target_solfege ?? slots["round_1.target_solfege"] ?? merged.target_solfege
  );
  if (targetSolfege.length) merged.target_solfege = targetSolfege;
  const roundSequences = roundSlotSequences(slots, "target_solfege");
  if (roundSequences.length) {
    const rounds = paddedRounds(merged.solfege_rounds ?? merged.target_rounds, Math.max(...roundSequences.map((item) => item.round)));
    roundSequences.forEach(({ round, sequence }) => {
      rounds[round - 1] = {
      id: `entity_solfege_${round}`,
      sequence,
      labels: sequence,
      midi_offsets: sequence.map(solfegeMidiOffset),
      answer: sequence,
      sing_back_required: merged.sing_back_required !== false,
      teacher_confirm_required: merged.teacher_confirm_required !== false
      };
    });
    merged.solfege_rounds = rounds;
    merged.target_rounds = merged.solfege_rounds;
    if (!targetSolfege.length) merged.target_solfege = uniqueStrings(roundSequences.flatMap((item) => item.sequence));
  }
  return merged;
}

export function mergeFormEntityExecutionConfig(state: StudentGameState, baseConfig: LooseRecord): LooseRecord {
  const { parameters, applicationParameters, slots } = executionParts(state);
  const merged: LooseRecord = { ...baseConfig, ...applicationParameters, ...parameters };
  const answerPattern = stringArray(slots["form.answer_pattern"]);
  if (answerPattern.length) merged.answer_pattern = answerPattern;
  const timelineSegments = recordArray(slots["form.timeline_segments"]);
  if (timelineSegments.length) merged.timeline_segments = timelineSegments;
  if (answerPattern.length) {
    merged.structure_cards = Array.from(new Set(answerPattern)).map((label) => ({
      id: `card_${label}`,
      label,
      name: `${label} 段`,
      description: label === "A" ? "主题材料" : "对比材料"
    }));
  }
  return merged;
}

export function mergeCompositionEntityExecutionConfig(state: StudentGameState, baseConfig: LooseRecord): LooseRecord {
  const { parameters, applicationParameters, slots } = executionParts(state);
  const merged: LooseRecord = { ...baseConfig, ...applicationParameters, ...parameters };
  const melodyCards = stringArray(parameters.melody_cards ?? applicationParameters.melody_cards ?? merged.melody_cards);
  const rhythmCards = compositionRhythmCards(parameters.rhythm_cards ?? applicationParameters.rhythm_cards ?? merged.rhythm_cards);
  const requiredElements = stringArray(parameters.required_elements ?? applicationParameters.required_elements ?? merged.required_elements);
  const constraintChecks = recordArray(slots["composition.constraint_checks"]);
  if (melodyCards.length) merged.melody_cards = melodyCards;
  if (rhythmCards.length) merged.rhythm_cards = rhythmCards;
  if (requiredElements.length) merged.required_elements = requiredElements;
  if (constraintChecks.length) merged.constraint_checks = constraintChecks;
  return merged;
}

function compositionRhythmCards(value: unknown): Array<string | LooseRecord> {
  if (!Array.isArray(value)) return [];
  return value
    .map((item): string | LooseRecord | null => {
      if (isRecord(item)) {
        const id = stringValue(item.id ?? item.label);
        if (!id) return null;
        return {
          ...item,
          id,
          label: stringValue(item.label ?? item.id) || id
        };
      }
      return String(item).trim();
    })
    .filter((item): item is string | LooseRecord => Boolean(item));
}

export function mergeTimbreEntityExecutionConfig(state: StudentGameState, baseConfig: LooseRecord): LooseRecord {
  const { parameters, applicationParameters, slots } = executionParts(state);
  const merged: LooseRecord = { ...baseConfig, ...applicationParameters, ...parameters };
  const instrumentPool = stringArray(parameters.instrument_pool ?? applicationParameters.instrument_pool ?? merged.instrument_pool);
  const traitPool = stringArray(parameters.timbre_traits ?? applicationParameters.timbre_traits ?? merged.timbre_traits);
  const comparisonPairs = pairArray(slots["timbre.comparison_pairs"]);
  const traitTargets = isRecord(slots["timbre.trait_targets"]) ? slots["timbre.trait_targets"] : {};
  if (instrumentPool.length >= 2) merged.instrument_pool = instrumentPool;
  if (traitPool.length) merged.timbre_traits = traitPool;
  const shouldBuildEntityRound = instrumentPool.length >= 2 && (
    comparisonPairs.length > 0 ||
    Object.keys(traitTargets).length > 0 ||
    Array.isArray(parameters.instrument_pool) ||
    Array.isArray(applicationParameters.instrument_pool)
  );
  if (shouldBuildEntityRound) {
    const [target, contrast] = comparisonPairs[0] ?? [instrumentPool[0], instrumentPool[1]];
    const targetTraits = stringArray(traitTargets[target]).length ? stringArray(traitTargets[target]) : traitPool.slice(0, 1);
    const contrastTraits = stringArray(traitTargets[contrast]).length
      ? stringArray(traitTargets[contrast])
      : traitPool.filter((trait) => !targetTraits.includes(trait)).slice(0, 1);
    merged.mode = merged.mode || "compare_twins";
    merged.evidence_required = Number(merged.evidence_required || Math.max(1, targetTraits.length));
    merged.timbre_rounds = [
      {
        id: "entity_timbre_1",
        mode: "compare_twins",
        prompt: `比较${target}和${contrast}的音色证据。`,
        compare_prompt: `第一声更像${target}，还要说明为什么不像${contrast}。`,
        target,
        answer: target,
        compare_with: contrast,
        candidates: instrumentPool,
        evidence_options: traitPool,
        evidence_answer: targetTraits,
        contrast_evidence_options: traitPool,
        contrast_evidence_answer: contrastTraits,
        comparison_reason_required: true,
        reason_frame: {
          target,
          contrast,
          sentence: `第一声更像${target}，因为它有{evidence}；不像${contrast}，因为{contrast_evidence}。`
        }
      }
    ];
    merged.clue_cases = merged.timbre_rounds;
  }
  return attachTimbreLessonAudio(merged);
}

function attachTimbreLessonAudio(config: LooseRecord): LooseRecord {
  const bindings = materialPlaybackBindings(config.material_binding_plan);
  if (!bindings.length) return config;
  const merged: LooseRecord = { ...config };
  merged.timbre_rounds = withPlaybackUrls(recordArray(merged.timbre_rounds), bindings);
  merged.clue_cases = withPlaybackUrls(recordArray(merged.clue_cases), bindings);
  return merged;
}

function materialPlaybackBindings(plan: unknown): LooseRecord[] {
  if (!isRecord(plan) || !Array.isArray(plan.bindings)) return [];
  return plan.bindings
    .filter(isRecord)
    .filter((binding) => stringValue(binding.playback_url));
}

function withPlaybackUrls(rounds: LooseRecord[], bindings: LooseRecord[]): LooseRecord[] {
  if (!rounds.length) return rounds;
  return rounds.map((round, index) => {
    const binding = bindings[index % bindings.length];
    const playbackUrl = stringValue(binding.playback_url);
    if (!playbackUrl) return round;
    const next: LooseRecord = {
      ...round,
      playback_url: stringValue(round.playback_url) || playbackUrl,
      source_id: stringValue(round.source_id) || stringValue(binding.source_id),
      display_label: stringValue(round.display_label) || stringValue(binding.display_label)
    };
    next.audio_profile = withProfileAudio(round.audio_profile, playbackUrl);
    const compareBinding = bindings[(index + 1) % bindings.length];
    const compareUrl = stringValue(round.compare_playback_url) || stringValue(compareBinding?.playback_url);
    if (round.compare_audio_profile && compareUrl && compareUrl !== playbackUrl) {
      next.compare_playback_url = compareUrl;
      next.compare_audio_profile = withProfileAudio(round.compare_audio_profile, compareUrl);
    }
    return next;
  });
}

function withProfileAudio(profile: unknown, audioUrl: string): LooseRecord {
  const base = isRecord(profile) ? profile : {};
  return {
    ...base,
    audio_url: stringValue(base.audio_url) || audioUrl
  };
}

function executionParts(state: StudentGameState) {
  const execution = resolveMusicEntityExecution(state);
  const slotBindings = execution.slot_bindings ?? {};
  const applicationSlotBindings = execution.entity_application?.slot_bindings ?? {};
  return {
    parameters: execution.variant_parameters ?? {},
    applicationParameters: execution.entity_application?.game_parameters ?? {},
    slots: { ...slotBindings, ...applicationSlotBindings }
  };
}

function normalizeExecution(value: unknown): MusicEntityExecution {
  if (!isRecord(value)) return {};
  const spec = value as GameVariantSpec;
  const plan = isRecord(spec.execution_plan) ? spec.execution_plan : {};
  const planParameters = executionPlanWrites(plan.parameter_writes, "variant_parameters.");
  const planSlots = executionPlanWrites(plan.slot_writes, "slot_bindings.");
  const planApplication = isRecord(plan.entity_application_writes) ? plan.entity_application_writes : {};
  const planApplicationParameters = isRecord(planApplication.game_parameters) ? planApplication.game_parameters : {};
  const planApplicationSlots = isRecord(planApplication.slot_bindings) ? planApplication.slot_bindings : {};
  const baseParameters = isRecord(spec.variant_parameters) ? spec.variant_parameters : {};
  const baseSlots = isRecord(spec.slot_bindings) ? spec.slot_bindings : {};
  const baseApplication = isRecord(spec.entity_application) ? spec.entity_application : {};
  const baseApplicationParameters = isRecord(baseApplication.game_parameters) ? baseApplication.game_parameters : {};
  const baseApplicationSlots = isRecord(baseApplication.slot_bindings) ? baseApplication.slot_bindings : {};
  const variantParameters = { ...baseParameters, ...planParameters };
  const slotBindings = { ...baseSlots, ...planSlots };
  const applicationParameters = { ...baseApplicationParameters, ...planApplicationParameters };
  const applicationSlots = { ...baseApplicationSlots, ...planApplicationSlots };
  return {
    contract_schema_version: stringValue(spec.contract_schema_version),
    music_entity: isRecord(spec.music_entity) ? {
      canonical_id: stringValue(spec.music_entity.canonical_id),
      label: stringValue(spec.music_entity.label),
      entity_type: stringValue(spec.music_entity.entity_type)
    } : undefined,
    variant_parameters: Object.keys(variantParameters).length ? variantParameters : undefined,
    slot_bindings: Object.keys(slotBindings).length ? slotBindings : undefined,
    execution_plan: isRecord(spec.execution_plan) ? {
      version: stringValue(spec.execution_plan.version),
      template_id: stringValue(spec.execution_plan.template_id),
      status: stringValue(spec.execution_plan.status),
      blocked_reasons: stringArray(spec.execution_plan.blocked_reasons),
      entity_type: stringValue(spec.execution_plan.entity_type),
      canonical_id: stringValue(spec.execution_plan.canonical_id),
      parameter_writes: Array.isArray(spec.execution_plan.parameter_writes) ? spec.execution_plan.parameter_writes : undefined,
      slot_writes: Array.isArray(spec.execution_plan.slot_writes) ? spec.execution_plan.slot_writes : undefined,
      entity_application_writes: isRecord(spec.execution_plan.entity_application_writes) ? spec.execution_plan.entity_application_writes : undefined,
      requires_teacher_confirmation: Boolean(spec.execution_plan.requires_teacher_confirmation),
      template_capability_status: stringValue(spec.execution_plan.template_capability_status)
    } : undefined,
    confirmation_gates: Array.isArray(spec.confirmation_gates) ? spec.confirmation_gates : undefined,
    requires_teacher_confirmation: Boolean(spec.requires_teacher_confirmation),
    confirmation_reason: stringValue(spec.confirmation_reason),
    entity_application: isRecord(spec.entity_application) || Object.keys(applicationParameters).length || Object.keys(applicationSlots).length ? {
      template_id: stringValue(baseApplication.template_id),
      canonical_id: stringValue(baseApplication.canonical_id),
      entity_type: stringValue(baseApplication.entity_type),
      label: stringValue(baseApplication.label),
      game_parameters: Object.keys(applicationParameters).length ? applicationParameters : undefined,
      slot_bindings: Object.keys(applicationSlots).length ? applicationSlots : undefined,
      requires_teacher_confirmation: Boolean(baseApplication.requires_teacher_confirmation),
      confirmation_reason: stringValue(baseApplication.confirmation_reason)
    } : undefined
  };
}

function executionPlanWrites(value: unknown, prefix: string): LooseRecord {
  if (!Array.isArray(value)) return {};
  return value.reduce<LooseRecord>((result, item) => {
    if (!isRecord(item)) return result;
    const path = stringValue(item.path);
    if (!path?.startsWith(prefix)) return result;
    const key = path.slice(prefix.length);
    if (!key) return result;
    result[key] = item.value;
    return result;
  }, {});
}

function requiresEntityConfirmation(execution: MusicEntityExecution) {
  if (execution.requires_teacher_confirmation) return true;
  if (execution.entity_application?.requires_teacher_confirmation) return true;
  const gates = Array.isArray(execution.confirmation_gates) ? execution.confirmation_gates : [];
  return gates.some((gate) => isRecord(gate) && gate.status !== "confirmed");
}

function confirmationReason(execution: MusicEntityExecution) {
  return (
    execution.confirmation_reason ||
    execution.entity_application?.confirmation_reason ||
    "音乐实体需要教师确认后才能作为正式答案。"
  );
}

function pendingConfirmationValue(execution: MusicEntityExecution) {
  const gates = Array.isArray(execution.confirmation_gates) ? execution.confirmation_gates : [];
  const gate = gates.find((item) => isRecord(item) && item.status !== "confirmed");
  return stringArray(isRecord(gate) ? gate.proposed_value : undefined);
}

function restoreBaseValue(target: LooseRecord, baseConfig: LooseRecord, key: string) {
  if (key in baseConfig) {
    target[key] = baseConfig[key];
    return;
  }
  delete target[key];
}

function stringValue(value: unknown): string | undefined {
  const text = String(value ?? "").trim();
  return text || undefined;
}

function stringArray(value: unknown): string[] {
  return Array.isArray(value) ? value.map(String).map((item) => item.trim()).filter(Boolean) : [];
}

function numberArray(value: unknown): number[] {
  return Array.isArray(value) ? value.map(Number).filter((item) => Number.isFinite(item)) : [];
}

function numberValue(value: unknown): number | undefined {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : undefined;
}

function recordArray(value: unknown): LooseRecord[] {
  return Array.isArray(value) ? value.filter(isRecord) : [];
}

function pairArray(value: unknown): Array<[string, string]> {
  if (!Array.isArray(value)) return [];
  return value
    .filter((item): item is unknown[] => Array.isArray(item) && item.length >= 2)
    .map((item) => [String(item[0] || ""), String(item[1] || "")] as [string, string])
    .filter(([first, second]) => Boolean(first && second));
}

function isRecord(value: unknown): value is LooseRecord {
  return Boolean(value && typeof value === "object" && !Array.isArray(value));
}

function rhythmLabel(step: string) {
  if (step === "eighth_pair" || step === "eighth") return "二八";
  if (step === "half") return "二分";
  if (step === "dotted_quarter") return "附点四分";
  if (step === "rest") return "休";
  if (step === "syncopation") return "切分";
  if (step === "sixteenth_four") return "四个十六";
  if (step === "eighth_sixteenth_sixteenth_eighth") return "八十六十六八";
  return "四分";
}

function rhythmTimelineItems(step: string, durationBeats: number, startBeat: number) {
  if (step === "eighth_pair") {
    const unit = durationBeats > 0 ? durationBeats / 2 : 0.5;
    return [
      { step: "eighth", label: rhythmLabel("eighth"), time_beats: startBeat, duration_beats: unit, hit_required: true },
      { step: "eighth", label: rhythmLabel("eighth"), time_beats: startBeat + unit, duration_beats: unit, hit_required: true }
    ];
  }
  if (step === "syncopation") {
    const unit = durationBeats > 0 ? durationBeats / 4 : 0.5;
    return [
      { step: "eighth", label: rhythmLabel("eighth"), time_beats: startBeat, duration_beats: unit, hit_required: true },
      { step: "quarter", label: rhythmLabel("quarter"), time_beats: startBeat + unit, duration_beats: unit * 2, hit_required: true },
      { step: "eighth", label: rhythmLabel("eighth"), time_beats: startBeat + unit * 3, duration_beats: unit, hit_required: true }
    ];
  }
  return [{
    step,
    label: rhythmLabel(step),
    time_beats: startBeat,
    duration_beats: durationBeats,
    hit_required: step !== "rest"
  }];
}

function roundSlotSequences(slots: LooseRecord, slotName: string) {
  return Object.entries(slots)
    .map(([key, value]) => {
      const match = new RegExp(`^round_(\\d+)\\.${slotName}$`).exec(key);
      const sequence = stringArray(value);
      return match && sequence.length ? { round: Number(match[1]), sequence } : null;
    })
    .filter((item): item is { round: number; sequence: string[] } => Boolean(item))
    .sort((first, second) => first.round - second.round);
}

function paddedRounds(value: unknown, total: number): LooseRecord[] {
  const existing = recordArray(value);
  return Array.from({ length: Math.max(1, total) }, (_, index) => ({ ...(existing[index] ?? {}), id: String(existing[index]?.id || `entity_round_${index + 1}`) }));
}

function uniqueStrings(values: string[]) {
  return values.filter((value, index) => values.indexOf(value) === index);
}

function pitchRoundAnswer(sequence: string[], config: LooseRecord) {
  const mode = String(config.current_mode || config.target_pattern_type || config.mode || "");
  if (mode === "melody_path" || mode === "melody_climb" || mode === "single_solfege" || mode === "solfege_ladder") {
    return sequence;
  }
  return pitchAnswer(sequence);
}

function pitchAnswer(sequence: string[]) {
  if (sequence.length < 2) return sequence[0] || "higher";
  const first = solfegeMidiOffset(sequence[0]);
  const last = solfegeMidiOffset(sequence[sequence.length - 1]);
  if (last > first) return "higher";
  if (last < first) return "lower";
  return "same";
}

function solfegeMidiOffset(note: unknown) {
  const pitch = resolvePitchToken(note);
  if (pitch) return pitch.semitone;
  return ({
    C: 0,
    D: 2,
    E: 4,
    F: 5,
    G: 7,
    A: 9,
    B: 11,
    "C'": 12
  } as Record<string, number>)[String(note)] ?? 0;
}
