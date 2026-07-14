import { PitchLadderGameSystem } from "../src/student-game/pitchLadderSystem";

function assertEqual(actual: unknown, expected: unknown, label: string) {
  if (actual !== expected) {
    throw new Error(`${label}: expected ${String(expected)}, got ${String(actual)}`);
  }
}

function assertArrayEqual(actual: unknown[], expected: unknown[], label: string) {
  const actualText = JSON.stringify(actual);
  const expectedText = JSON.stringify(expected);
  if (actualText !== JSON.stringify(expected)) {
    throw new Error(`${label}: expected ${JSON.stringify(expected)}, got ${actualText}`);
  }
}

const melodySystem = new PitchLadderGameSystem({
  rounds: [
    { sequence: ["do", "re"], answer: ["do", "re"] },
    { sequence: ["mi"], answer: ["mi"] }
  ],
  energyMax: 100,
  mistakeLimit: 3
});

melodySystem.listen();
melodySystem.enterPlaying("路线");
assertEqual(melodySystem.chooseNode("do").type, "partial", "first route note is partial");
const firstRoundClear = melodySystem.chooseNode("re");
assertEqual(firstRoundClear.type, "round_clear", "route waits at sing-back checkpoint");
assertEqual(firstRoundClear.missionDone, false, "first round is not final");
assertEqual(melodySystem.state.status, "round_clear", "state stays in sing-back checkpoint");
assertArrayEqual(melodySystem.state.selected, ["do", "re"], "selected route stays visible");
const lockedRouteInput = melodySystem.chooseNode("do");
assertEqual(lockedRouteInput.type, "playing", "route input does not repeat reward while waiting for sing-back");
assertArrayEqual(melodySystem.state.selected, ["do", "re"], "route input is locked while waiting for sing-back");

const nextRound = melodySystem.confirmSingBack();
assertEqual(nextRound.type, "playing", "teacher confirmation advances to next round");
assertEqual(melodySystem.state.status, "ready", "next round returns to ready");
assertEqual(melodySystem.state.currentRound, 1, "current round advances after confirmation");

melodySystem.listen();
melodySystem.enterPlaying("路线");
const finalRoundClear = melodySystem.chooseNode("mi");
assertEqual(finalRoundClear.type, "round_clear", "final route also waits for sing-back");
assertEqual(finalRoundClear.missionDone, true, "final route remembers mission is complete");
assertEqual(melodySystem.state.status, "round_clear", "final state waits before mission success");

const finalConfirm = melodySystem.confirmSingBack();
assertEqual(finalConfirm.type, "mission_success", "final confirmation completes mission");
assertEqual(melodySystem.state.status, "mission_success", "state becomes mission success after teacher confirmation");

const directionSystem = new PitchLadderGameSystem({
  rounds: [{ sequence: ["do", "mi"], answer: "higher" }],
  energyMax: 100,
  mistakeLimit: 3
});

directionSystem.listen();
directionSystem.enterPlaying("选");
directionSystem.previewDirection("higher");
const directionResult = directionSystem.resolveVoiceAttempt("higher", "higher");
assertEqual(directionResult.type, "mission_success", "direction pair voice confirmation still completes final round");

const directionAdvanceSystem = new PitchLadderGameSystem({
  rounds: [
    { sequence: ["do", "re"], answer: "higher" },
    { sequence: ["re", "do"], answer: "lower" }
  ],
  energyMax: 100,
  mistakeLimit: 3
});

directionAdvanceSystem.listen();
directionAdvanceSystem.enterPlaying("选");
const firstDirectionRound = directionAdvanceSystem.resolveVoiceAttempt("higher", "higher");
assertEqual(firstDirectionRound.type, "round_clear", "non-final direction pair clears the round");
const advancedDirectionRound = directionAdvanceSystem.advanceRound();
assertEqual(advancedDirectionRound.type, "playing", "direction pair can auto-advance after clear animation");
assertEqual(directionAdvanceSystem.state.status, "ready", "direction pair returns to ready for the next round");
assertEqual(directionAdvanceSystem.state.currentRound, 1, "direction pair advances to the next round");
