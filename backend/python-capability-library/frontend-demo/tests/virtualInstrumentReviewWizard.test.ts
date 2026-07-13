import { REVIEW_GATES, REVIEW_TARGET_IDS, createReviewDocument, updateReviewGate, reviewReleaseReady, exportReviewDocument, importReviewDocument } from "../src/virtual-instruments/core/reviewWizard";

function equal<T>(actual: T, expected: T, label: string) {
  if (actual !== expected) throw new Error(`${label}: expected ${String(expected)}, got ${String(actual)}`);
}

equal(REVIEW_TARGET_IDS.length, 11, "ten instruments and percussion grid are reviewed");
equal(REVIEW_GATES.length, 5, "each target has five ordered gates");
const review = createReviewDocument();
for (const targetId of REVIEW_TARGET_IDS) {
  for (const gate of REVIEW_GATES) updateReviewGate(review, targetId, gate.id, "approved", "已核验");
}
equal(reviewReleaseReady(review), true, "all gates approved opens release gate");
updateReviewGate(review, REVIEW_TARGET_IDS[0], REVIEW_GATES[0].id, "modify", "图片比例需调整");
equal(reviewReleaseReady(review), false, "one modification blocks release");
const restored = importReviewDocument(exportReviewDocument(review));
equal(restored.targets[REVIEW_TARGET_IDS[0]].gates.visual.decision, "modify", "review JSON round-trips");
