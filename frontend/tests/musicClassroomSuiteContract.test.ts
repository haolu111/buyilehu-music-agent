import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import * as musicComponents from "../src/music-components";
import {
  FIRST_BATCH_COMPONENTS,
  buildDefaultMusicMediaSession,
  canUseScoreForStudentJudgement,
  type NormalizedScoreTimeline
} from "../src/shared/musicMediaContracts";

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const componentNames = [
  "SongAudioWorkbench",
  "ScoreAudioSyncPlayer",
  "EarTrainingEngine",
  "VocalChoirTraining",
  "EnsembleConductor"
] as const;

assert.deepEqual(
  FIRST_BATCH_COMPONENTS.map((component) => component.id),
  [
    "song_audio_workbench",
    "score_audio_sync_player",
    "ear_training_engine",
    "vocal_choir_training",
    "ensemble_conductor"
  ]
);
assert.equal(FIRST_BATCH_COMPONENTS[0]?.name, "音乐要素控制器", "the first component keeps its stable id but exposes the replacement name");

for (const name of componentNames) {
  assert.equal(typeof musicComponents[name], "function", `${name} must be exported by the component library`);
  const source = readFileSync(join(root, `src/music-components/${name}.tsx`), "utf8");
  assert.match(source, /teacher/i, `${name} exposes a teacher boundary`);
}

const session = buildDefaultMusicMediaSession({
  sessionId: "class-1",
  sourceUrl: "/uploads/song.mp3",
  sourceKind: "teacher_upload"
});
assert.equal(session.version, "music_media_session_v1");
assert.equal(session.recordingPolicy, "local_session_only");
assert.equal(session.networkMode, "single_device_classroom");
assert.equal(session.transport.playbackRate, 1);
assert.equal(session.transport.transposeSemitones, 0);

const draftTimeline: NormalizedScoreTimeline = {
  version: "normalized_score_timeline_v1",
  source: "recognized_draft",
  teacherConfirmed: false,
  meterMap: [{ measure: 1, meter: "2/4" }],
  tempoMap: [{ measure: 1, bpm: 88 }],
  keyMap: [{ measure: 1, tonic: "C", mode: "major" }],
  events: []
};
assert.equal(canUseScoreForStudentJudgement(draftTimeline), false);

const confirmedTimeline: NormalizedScoreTimeline = {
  ...draftTimeline,
  source: "musicxml",
  teacherConfirmed: true
};
assert.equal(canUseScoreForStudentJudgement(confirmedTimeline), true);

const reviewSource = readFileSync(join(root, "src/activity/MusicEducationReviewApp.tsx"), "utf8");
assert.match(reviewSource, /FIRST_BATCH_COMPONENTS\.map/, "the professional review library renders every first-batch component from the shared contract");
assert.match(reviewSource, /music-classroom-suite\.html\?component=/, "each review card opens the real classroom component");

const viteSource = readFileSync(join(root, "vite.config.ts"), "utf8");
assert.match(viteSource, /music-classroom-suite/, "the first batch has a standalone classroom suite entry");

const suiteSource = readFileSync(join(root, "src/activity/MusicClassroomSuiteApp.tsx"), "utf8");
assert.match(suiteSource, /__MUSIC_CLASSROOM_SUITE_STATE__/, "agent runtime state can configure the classroom suite");
assert.match(suiteSource, /media_session|mediaSession/, "the shared media session reaches the rendered component");

const scoreSource = readFileSync(join(root, "src/music-components/ScoreAudioSyncPlayer.tsx"), "utf8");
assert.match(scoreSource, /OpenSheetMusicDisplay/, "confirmed MusicXML can use a maintained score renderer");

const workbenchSource = readFileSync(join(root, "src/music-components/SongAudioWorkbench.tsx"), "utf8");
const elementControllerSource = readFileSync(join(root, "src/music-components/musicElementController.ts"), "utf8");
assert.match(workbenchSource, /音乐要素控制器/, "the first component renders the existing music element controller");
assert.match(workbenchSource, /大小调[／/]调式转换/, "the controller exposes mode transformation");
assert.match(workbenchSource, /节奏密度/, "the controller exposes rhythm-density transformation");
assert.match(workbenchSource, /音色切换/, "the controller exposes timbre transformation");
assert.match(workbenchSource, /uploadListeningSource/, "the workbench uses the shared listening upload adapter");
assert.match(workbenchSource, /transformListeningSession/, "the workbench uses the shared listening transform adapter");
assert.doesNotMatch(workbenchSource, /\/api\/music-media\/render-variant/, "the replaced workbench no longer calls the simplified media variant endpoint");
assert.match(elementControllerSource, /\/api\/listening\/upload/, "the adapter reuses the existing listening upload endpoint");
assert.match(elementControllerSource, /\/api\/listening\/transform/, "the adapter reuses the existing listening transform endpoint");

const conductorSource = readFileSync(join(root, "src/music-components/EnsembleConductor.tsx"), "utf8");
const suiteCssSource = readFileSync(join(root, "src/activity/musicClassroomSuite.css"), "utf8");
assert.match(conductorSource, /className="conductor-actions"/, "conductor transport controls expose a responsive layout hook");
assert.match(suiteCssSource, /\.conductor-actions\s*\{[^}]*flex-wrap:\s*wrap/s, "conductor transport controls wrap instead of widening mobile pages");
assert.match(suiteCssSource, /\.music-element-control-grid\s*\{/, "the music element controller has a dedicated control layout");
assert.match(suiteCssSource, /\.music-element-compare-grid\s*\{/, "original and transformed audio use a dedicated comparison layout");
assert.match(suiteCssSource, /@media\s*\(max-width:\s*1100px\)/, "the controller has an explicit tablet breakpoint");
assert.match(conductorSource, /playbackRun\.current\s*!==\s*run/, "paused or superseded conductor runs cannot schedule a later entrance");
assert.match(conductorSource, /clearScheduledCueHandles/, "teacher pause clears every pending conductor cue");
assert.match(scoreSource, /cursor\.reset\(\)/, "MusicXML cursor resets against the normalized score timeline");
assert.match(scoreSource, /cursor\.next\(\)/, "MusicXML cursor advances with the active score event");

const packageSource = JSON.parse(readFileSync(join(root, "package.json"), "utf8"));
assert.ok(packageSource.dependencies.opensheetmusicdisplay, "OpenSheetMusicDisplay is a declared production dependency");
