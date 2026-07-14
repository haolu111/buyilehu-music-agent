import { VIRTUAL_INSTRUMENT_DEFINITIONS } from "./virtualInstrumentCatalog";

export type ReviewDecision = "pending" | "approved" | "modify" | "rejected";
export type ReviewGateId = "visual" | "audio" | "touch" | "metronome" | "gameplay";
export const REVIEW_GATES: Array<{ id: ReviewGateId; label: string; description: string }> = [
  { id: "visual", label: "视觉与图片", description: "图片真实、比例正确、主体边界清楚" },
  { id: "audio", label: "真实音色", description: "真实采样、奏法和音高对应正确" },
  { id: "touch", label: "触控区域", description: "主体可击、空白静音、手势符合实物" },
  { id: "metronome", label: "节拍器适配", description: "预备拍与演奏声部清楚分离" },
  { id: "gameplay", label: "课堂玩法", description: "四种玩法边界适合中小学课堂" },
];
export const REVIEW_TARGET_IDS = [...VIRTUAL_INSTRUMENT_DEFINITIONS.map((item) => item.id), "virtual_percussion_grid"];
export type ReviewGateRecord = { decision: ReviewDecision; notes: string; reviewedAt: string | null };
export type ReviewDocument = { version: "virtual_instrument_review_v2"; updatedAt: string; targets: Record<string, { gates: Record<ReviewGateId, ReviewGateRecord> }> };

function blankGate(): ReviewGateRecord { return { decision: "pending", notes: "", reviewedAt: null }; }
export function createReviewDocument(): ReviewDocument {
  return { version: "virtual_instrument_review_v2", updatedAt: new Date(0).toISOString(), targets: Object.fromEntries(REVIEW_TARGET_IDS.map((id) => [id, { gates: Object.fromEntries(REVIEW_GATES.map((gate) => [gate.id, blankGate()])) as Record<ReviewGateId, ReviewGateRecord> }])) };
}
export function updateReviewGate(document: ReviewDocument, targetId: string, gateId: ReviewGateId, decision: ReviewDecision, notes: string): ReviewDocument {
  const target = document.targets[targetId]; if (!target) throw new Error(`Unknown review target: ${targetId}`);
  target.gates[gateId] = { decision, notes, reviewedAt: new Date().toISOString() }; document.updatedAt = new Date().toISOString(); return document;
}
export function reviewReleaseReady(document: ReviewDocument): boolean { return REVIEW_TARGET_IDS.every((id) => REVIEW_GATES.every((gate) => document.targets[id]?.gates[gate.id]?.decision === "approved")); }
export function exportReviewDocument(document: ReviewDocument): string { return JSON.stringify(document, null, 2); }
export function importReviewDocument(json: string): ReviewDocument {
  const parsed = JSON.parse(json) as ReviewDocument;
  if (parsed.version !== "virtual_instrument_review_v2") throw new Error("Unsupported review document");
  for (const id of REVIEW_TARGET_IDS) if (!parsed.targets[id]) throw new Error(`Missing review target: ${id}`);
  return parsed;
}

