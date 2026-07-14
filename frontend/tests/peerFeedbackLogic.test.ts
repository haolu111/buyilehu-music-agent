import { strict as assert } from "node:assert";
import {
  buildPeerFeedbackRecord,
  buildPeerFeedbackShowcases,
  evaluatePeerFeedback,
  hasSpecificMusicEvidence,
  submitPeerFeedback,
  updatePeerFeedbackEvidence,
  updatePeerFeedbackSuggestion
} from "../src/activity/peerFeedbackLogic";

const showcases = buildPeerFeedbackShowcases(
  ["A组展示节奏创编", "B组展示身体打击"],
  ["节奏稳定", "进入整齐", "能听同伴"]
);

assert.equal(showcases.length, 2);
assert.equal(showcases[0].status, "active");
assert.equal(showcases[1].status, "waiting");
assert.equal(hasSpecificMusicEvidence("很好听"), false);
assert.equal(hasSpecificMusicEvidence("节奏稳定，进入整齐"), true);

let current = updatePeerFeedbackEvidence(showcases, 0, "节奏稳定");
current = updatePeerFeedbackSuggestion(current, 0, "很好听");
assert.equal(evaluatePeerFeedback(current).status, "needs_specific_suggestion");

current = updatePeerFeedbackSuggestion(current, 0, "节奏稳定，如果休止处停得更整齐会更好");
current = submitPeerFeedback(current, 0);
assert.equal(current[0].status, "reviewed");
assert.equal(current[1].status, "active");

const record = buildPeerFeedbackRecord(current);
assert.equal(record.version, "peer_feedback_record_v1");
assert.equal(record.reviewedCount, 1);
assert.equal(record.readyForTeacherSummary, false);
assert.equal(record.entries[0].evidenceTerms[0], "节奏稳定");
