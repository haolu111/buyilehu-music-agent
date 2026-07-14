import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import * as musicComponents from "../src/music-components";

const requiredExports = [
  "AudioPlayer",
  "ComparePlayer",
  "RhythmCardBank",
  "MeterTrack",
  "TapFeedback",
  "SolfegeCardBank",
  "InstrumentCardGrid",
  "PicturePromptCards",
  "FormCardTimeline",
  "GraphicScoreCanvas",
  "RubricPanel",
  "TeacherControlBar",
  "SongAudioWorkbench",
  "ScoreAudioSyncPlayer",
  "EarTrainingEngine",
  "VocalChoirTraining",
  "EnsembleConductor"
];

for (const componentName of requiredExports) {
  assert.equal(typeof musicComponents[componentName as keyof typeof musicComponents], "function", `${componentName} must be exported`);
}

const rhythmCardSource = readFileSync(join(dirname(dirname(fileURLToPath(import.meta.url))), "src/music-components/RhythmCardBank.tsx"), "utf8");
const meterTrackSource = readFileSync(join(dirname(dirname(fileURLToPath(import.meta.url))), "src/music-components/MeterTrack.tsx"), "utf8");
const graphicScoreActivitySource = readFileSync(join(dirname(dirname(fileURLToPath(import.meta.url))), "src/activity/GraphicScoreActivity.tsx"), "utf8");
assert.match(rhythmCardSource, /rhythm={card\.patternId}/, "rhythm cards draw notation from canonical pattern ids");
assert.match(rhythmCardSource, /onSelect/, "rhythm cards expose selection for composition activities");
assert.match(meterTrackSource, /rhythm={event\.patternId}/, "meter events draw notation from the same canonical pattern ids used for timing");
assert.match(graphicScoreActivitySource, /RhythmCardBank/, "graphic score composes the formal rhythm card component");
assert.match(graphicScoreActivitySource, /SolfegeCardBank/, "graphic score composes the formal solfege card component");
assert.match(graphicScoreActivitySource, /mixed_cards/, "graphic score keeps an explicit mixed-card mode");
assert.match(graphicScoreActivitySource, /allowOscillatorFallback:\s*false/, "mixed graphic score playback requires sampled piano audio");

assert.deepEqual(Object.keys(musicComponents.musicComponentRuntimeContracts).sort(), requiredExports.sort());

for (const componentName of requiredExports) {
  const contract = musicComponents.musicComponentRuntimeContracts[componentName];
  assert.ok(contract.musicElements.length > 0, `${componentName} declares supported music elements`);
  assert.ok(contract.studentActions.length > 0, `${componentName} declares supported student actions`);
  assert.ok(contract.inputShape.length > 0, `${componentName} declares input shape`);
  assert.ok(contract.outputShape.length > 0, `${componentName} declares output shape`);
  assert.ok(contract.teacherControls.length > 0, `${componentName} declares teacher controls`);
  assert.ok(contract.acceptanceChecks.length > 0, `${componentName} declares runtime acceptance checks`);
}
