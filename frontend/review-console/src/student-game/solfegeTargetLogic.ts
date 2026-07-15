import type { SolfegeTargetMistakeReason } from "./SolfegeTargetScene";

export type SolfegeShotResult = {
  selected: string[];
  expected: string[];
  expectedNote: string;
  shotIndex: number;
  ok: boolean;
  completed: boolean;
  mistakeReason?: SolfegeTargetMistakeReason;
};

export function resolveSolfegeTargetShot(expectedInput: unknown, selectedAfterShotInput: unknown, noteInput: unknown): SolfegeShotResult {
  const expected = stringArray(expectedInput);
  const selected = stringArray(selectedAfterShotInput);
  const note = String(noteInput || "");
  const shotIndex = Math.max(0, Math.min(selected.length - 1, Math.max(0, expected.length - 1)));
  const expectedNote = expected[shotIndex] || note;
  const ok = selected.length <= expected.length && expectedNote === note;
  return {
    selected,
    expected,
    expectedNote,
    shotIndex,
    ok,
    completed: ok && selected.length >= expected.length,
    mistakeReason: ok ? undefined : expected.length > 1 ? "chain_wrong" : "wrong_target"
  };
}

function stringArray(value: unknown): string[] {
  return Array.isArray(value) ? value.map(String).map((item) => item.trim()).filter(Boolean) : [];
}
