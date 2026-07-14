export type FormRouteJudgement = {
  routeSlots: string[];
  answerPattern: string[];
  complete: boolean;
  correct: boolean;
  firstMismatchIndex: number;
};

export function resolveFormRouteJudgement(routeSlotsInput: unknown, answerPatternInput: unknown): FormRouteJudgement {
  const answerPattern = stringArray(answerPatternInput).map((item) => item.toUpperCase());
  const routeSlots = stringArray(routeSlotsInput).map((item) => item.toUpperCase()).slice(0, answerPattern.length);
  const paddedSlots = Array.from({ length: Math.max(1, answerPattern.length) }, (_, index) => routeSlots[index] || "");
  const complete = answerPattern.length > 0 && paddedSlots.every(Boolean);
  const firstMismatchIndex = paddedSlots.findIndex((item, index) => item !== answerPattern[index]);
  return {
    routeSlots: paddedSlots,
    answerPattern,
    complete,
    correct: complete && firstMismatchIndex < 0,
    firstMismatchIndex
  };
}

function stringArray(value: unknown): string[] {
  return Array.isArray(value) ? value.map(String).map((item) => item.trim()).filter(Boolean) : [];
}
