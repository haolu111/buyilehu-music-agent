export { AudioPlayer } from "./AudioPlayer";
export { ComparePlayer, type ComparePlayerClip } from "./ComparePlayer";
export { RhythmCardBank } from "./RhythmCardBank";
export { MeterTrack } from "./MeterTrack";
export { TapFeedback } from "./TapFeedback";
export { SolfegeCardBank, type SolfegeCard } from "./SolfegeCardBank";
export { InstrumentCardGrid, type InstrumentCard } from "./InstrumentCardGrid";
export { PicturePromptCards, type PicturePromptCard } from "./PicturePromptCards";
export { FormCardTimeline, type FormSectionCard } from "./FormCardTimeline";
export { GraphicScoreCanvas, type GraphicScoreSymbol } from "./GraphicScoreCanvas";
export { RubricPanel, type RubricCriterion } from "./RubricPanel";
export { TeacherControlBar } from "./TeacherControlBar";
export { SongAudioWorkbench } from "./SongAudioWorkbench";
export { ScoreAudioSyncPlayer } from "./ScoreAudioSyncPlayer";
export { EarTrainingEngine } from "./EarTrainingEngine";
export { VocalChoirTraining } from "./VocalChoirTraining";
export { EnsembleConductor } from "./EnsembleConductor";

export type MusicComponentRuntimeContract = {
  musicElements: string[];
  studentActions: string[];
  inputShape: string[];
  outputShape: string[];
  usableActivities: string[];
  teacherControls: string[];
  acceptanceChecks: string[];
};

export const musicComponentRuntimeContracts = {
  AudioPlayer: {
    musicElements: ["audio", "tempo", "phrase"],
    studentActions: ["listen", "replay"],
    inputShape: ["playing:boolean", "bpm:number"],
    outputShape: ["onToggle", "onPreviewPulse"],
    usableActivities: ["lesson_opening_hook", "listen_choose_explain", "rhythm_warmup"],
    teacherControls: ["play", "pause", "replay", "tempo"],
    acceptanceChecks: ["audio_playable", "listen_first"]
  },
  ComparePlayer: {
    musicElements: ["timbre", "tempo", "dynamics", "melody"],
    studentActions: ["listen", "compare", "explain"],
    inputShape: ["clips:ComparePlayerClip[]", "activeClipId?:string"],
    outputShape: ["onSelectClip", "onTogglePlay", "onReplay"],
    usableActivities: ["listen_choose_explain", "instrument_family_sorting", "lesson_opening_hook"],
    teacherControls: ["switch_audio", "replay", "reset"],
    acceptanceChecks: ["listen_before_choice", "evidence_required"]
  },
  RhythmCardBank: {
    musicElements: ["rhythm", "beat", "rest"],
    studentActions: ["listen", "tap", "arrange", "create"],
    inputShape: ["cards:RhythmCard[]", "activeCardId?:string"],
    outputShape: ["onSelect card id", "selected rhythm card state"],
    usableActivities: ["rhythm_warmup", "lyrics_rhythm", "body_percussion"],
    teacherControls: ["shuffle", "show_answer", "reset"],
    acceptanceChecks: ["rhythm_value_check", "student_operable"]
  },
  MeterTrack: {
    musicElements: ["meter", "beat", "bar"],
    studentActions: ["listen", "track", "tap"],
    inputShape: ["events:BeatTimelineEvent[]", "elapsedMs:number", "totalMs:number"],
    outputShape: ["visible beat progress"],
    usableActivities: ["strong_weak_beat", "orff_percussion_ensemble", "rhythm_warmup"],
    teacherControls: ["tempo", "pause", "reset"],
    acceptanceChecks: ["beat_points_visible", "meter_bound"]
  },
  TapFeedback: {
    musicElements: ["beat", "timing", "stability"],
    studentActions: ["tap", "revise"],
    inputShape: ["judgement?:TapTimingJudgement|RhythmTapJudgement", "score:number", "tapCount:number"],
    outputShape: ["correct/early/late/extra/rest feedback", "score badge"],
    usableActivities: ["strong_weak_beat", "rhythm_warmup"],
    teacherControls: ["reset", "difficulty"],
    acceptanceChecks: ["music_truth_bound", "one_target_one_match", "not_speed_only"]
  },
  SolfegeCardBank: {
    musicElements: ["solfege", "pitch", "melody"],
    studentActions: ["listen", "sing_back", "order"],
    inputShape: ["cards:SolfegeCard[]", "mode?:string"],
    outputShape: ["onSelect card id"],
    usableActivities: ["solfege_echo", "simple_score_following"],
    teacherControls: ["replay", "show_hint", "reset"],
    acceptanceChecks: ["listen_or_sing_back_required", "pitch_material_bound"]
  },
  InstrumentCardGrid: {
    musicElements: ["timbre", "instrument_family"],
    studentActions: ["listen", "classify", "explain"],
    inputShape: ["instruments:InstrumentCard[]"],
    outputShape: ["onSelect", "onPreviewAudio"],
    usableActivities: ["instrument_family_sorting", "timbre_detective"],
    teacherControls: ["replay", "show_family", "reset"],
    acceptanceChecks: ["real_audio_sample_required", "generated_image_not_real_photo"]
  },
  PicturePromptCards: {
    musicElements: ["mood", "image", "listening_question"],
    studentActions: ["listen", "choose", "explain"],
    inputShape: ["cards:PicturePromptCard[]", "listened:boolean"],
    outputShape: ["onSelect prompt card"],
    usableActivities: ["lesson_opening_hook", "listen_choose_explain"],
    teacherControls: ["replay", "hide_hint", "reset"],
    acceptanceChecks: ["listen_before_picture_choice", "question_visible"]
  },
  FormCardTimeline: {
    musicElements: ["form", "section", "phrase"],
    studentActions: ["listen", "arrange", "explain"],
    inputShape: ["sections:FormSectionCard[]", "answerPattern?:string[]"],
    outputShape: ["onReplaySection", "onReset"],
    usableActivities: ["form_treasure", "theme_return_action"],
    teacherControls: ["replay_section", "show_answer", "reset"],
    acceptanceChecks: ["audio_section_relisten", "form_pattern_bound"]
  },
  GraphicScoreCanvas: {
    musicElements: ["graphic_score", "sound_shape", "creation"],
    studentActions: ["create", "playback", "revise", "explain"],
    inputShape: ["symbols:GraphicScoreSymbol[]", "playbackReady?:boolean"],
    outputShape: ["onPlay", "onClear", "onSave"],
    usableActivities: ["graphic_score_create", "pentatonic_melody_create"],
    teacherControls: ["playback", "clear", "save"],
    acceptanceChecks: ["symbol_meaning_bound", "playback_and_revision"]
  },
  RubricPanel: {
    musicElements: ["assessment", "evidence", "performance"],
    studentActions: ["perform", "assess", "revise"],
    inputShape: ["criteria:RubricCriterion[]"],
    outputShape: ["onToggleCriterion", "onReset"],
    usableActivities: ["peer_feedback", "orff_percussion_ensemble", "classroom_band_roles"],
    teacherControls: ["confirm", "reset", "save"],
    acceptanceChecks: ["music_evidence_required", "reward_not_speed_only"]
  },
  TeacherControlBar: {
    musicElements: ["tempo", "meter", "classroom_flow"],
    studentActions: ["listen", "perform"],
    inputShape: ["bpm:number", "meter:PrimaryMeter", "repeatCount:number"],
    outputShape: ["onBpmChange", "onMeterChange", "onRepeatChange", "onReset"],
    usableActivities: ["all_primary_music_activities"],
    teacherControls: ["tempo", "meter", "repeat", "reset"],
    acceptanceChecks: ["teacher_reset_ready", "projector_readable"]
  },
  SongAudioWorkbench: {
    musicElements: ["song_audio", "phrase", "tempo", "key"],
    studentActions: ["listen", "replay", "compare"],
    inputShape: ["session:MusicMediaSession"],
    outputShape: ["updated media session", "confirmed loop range"],
    usableActivities: ["phrase_singing", "vocal_training", "score_following"],
    teacherControls: ["upload", "loop", "tempo", "transpose", "version", "reset"],
    acceptanceChecks: ["rights_source_visible", "teacher_material_priority", "audio_playable"]
  },
  ScoreAudioSyncPlayer: {
    musicElements: ["score", "melody", "rhythm", "lyrics"],
    studentActions: ["listen", "track", "read", "sing"],
    inputShape: ["timeline:NormalizedScoreTimeline"],
    outputShape: ["cursor position", "selected measure loop"],
    usableActivities: ["simple_score_following", "phrase_singing", "ensemble_rehearsal"],
    teacherControls: ["score_view", "play", "seek", "loop", "reset"],
    acceptanceChecks: ["score_to_sound_mapping", "teacher_confirmed_score", "shared_timeline"]
  },
  EarTrainingEngine: {
    musicElements: ["pitch", "interval", "rhythm", "melody", "tonality"],
    studentActions: ["listen", "choose", "tap", "sing_back", "explain"],
    inputShape: ["teacher constraints", "question types", "allowed pitches"],
    outputShape: ["objective answer evidence", "teacher sing-back confirmation"],
    usableActivities: ["solfege_echo", "rhythm_echo", "sight_singing"],
    teacherControls: ["question_type", "pitch_range", "solfege_system", "random_policy", "reset"],
    acceptanceChecks: ["teacher_material_priority", "objective_only_auto_judgement", "real_audio_required"]
  },
  VocalChoirTraining: {
    musicElements: ["voice", "breath", "phrase", "choir"],
    studentActions: ["listen", "prepare", "sing", "record", "replay", "revise"],
    inputShape: ["grade preset", "confirmed phrase", "safe range"],
    outputShape: ["local recording", "teacher confirmation record"],
    usableActivities: ["phrase_singing", "choir_rehearsal", "solfege_echo"],
    teacherControls: ["grade", "range", "record", "confirm", "reset"],
    acceptanceChecks: ["child_voice_safety", "local_recording_only", "no_automatic_vocal_grade"]
  },
  EnsembleConductor: {
    musicElements: ["multipart", "rhythm", "balance", "ensemble"],
    studentActions: ["listen", "enter", "perform", "cooperate", "assess"],
    inputShape: ["tracks:MusicTrack[]", "score timeline", "entry cues"],
    outputShape: ["audible mix", "entry evidence", "teacher assessment"],
    usableActivities: ["orff_ensemble", "classroom_band", "two_part_choir"],
    teacherControls: ["mute", "solo", "volume", "loop", "entry_cue", "reset"],
    acceptanceChecks: ["part_source_labeled", "count_in_separate", "teacher_confirm_boundary"]
  }
} satisfies Record<string, MusicComponentRuntimeContract>;
