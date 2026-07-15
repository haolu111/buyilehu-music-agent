import type { Round } from "./types";

export type TimbreCaseJudgement = "solved" | "wrong" | "evidence_missing";

export type TimbreCaseResult = {
  judgement: TimbreCaseJudgement;
  answerOk: boolean;
  evidenceOk: boolean;
  contrastOk: boolean;
  heardOk: boolean;
};

export function resolveTimbreCaseJudgement(
  round: Round,
  selectedAnswerInput: unknown,
  selectedEvidenceInput: unknown,
  selectedContrastEvidenceInput: unknown,
  evidenceNeedInput: unknown,
  heardInput = true
): TimbreCaseResult {
  const selectedAnswer = String(selectedAnswerInput || "");
  const selectedEvidence = stringArray(selectedEvidenceInput);
  const selectedContrastEvidence = String(selectedContrastEvidenceInput || "");
  const evidenceNeed = Math.max(1, Number(evidenceNeedInput) || 1);
  const comparisonRequired = Boolean(round.comparison_reason_required && round.compare_with);
  const heardOk = Boolean(heardInput);
  const answerOk = Array.isArray(round.answer)
    ? round.answer.map(String).includes(selectedAnswer)
    : selectedAnswer === String(round.answer || "");
  const evidenceOk = stringArray(round.evidence_answer).filter((item) => selectedEvidence.includes(item)).length >= evidenceNeed;
  const contrastOk = !comparisonRequired || stringArray(round.contrast_evidence_answer).includes(selectedContrastEvidence);
  if (!heardOk || !selectedAnswer || selectedEvidence.length < evidenceNeed || (comparisonRequired && !selectedContrastEvidence)) {
    return { judgement: "evidence_missing", answerOk, evidenceOk, contrastOk, heardOk };
  }
  if (!answerOk) return { judgement: "wrong", answerOk, evidenceOk, contrastOk, heardOk };
  if (!evidenceOk || !contrastOk) return { judgement: "evidence_missing", answerOk, evidenceOk, contrastOk, heardOk };
  return { judgement: "solved", answerOk, evidenceOk, contrastOk, heardOk };
}

function stringArray(value: unknown): string[] {
  return Array.isArray(value) ? value.map(String).map((item) => item.trim()).filter(Boolean) : [];
}
