import type { VoiceDirection } from "./audio";

export type PitchLadderInputAction =
  | "listen"
  | "choose_higher"
  | "choose_same"
  | "choose_lower"
  | "voice_check"
  | "teacher_confirm"
  | "reset";

export type PitchLadderInputBindings = Record<PitchLadderInputAction, string[]>;

export const PITCH_LADDER_INPUT_BINDINGS: PitchLadderInputBindings = {
  listen: ["Space", "KeyL"],
  choose_higher: ["ArrowUp", "KeyW"],
  choose_same: ["ArrowRight", "KeyD"],
  choose_lower: ["ArrowDown", "KeyS"],
  voice_check: ["Enter", "KeyV"],
  teacher_confirm: ["KeyT"],
  reset: ["KeyR"]
};

export function pitchDirectionFromInputAction(action: PitchLadderInputAction): VoiceDirection | null {
  if (action === "choose_higher") return "higher";
  if (action === "choose_same") return "same";
  if (action === "choose_lower") return "lower";
  return null;
}

export function resolvePitchLadderKeyAction(code: string, bindings: PitchLadderInputBindings = PITCH_LADDER_INPUT_BINDINGS): PitchLadderInputAction | null {
  const found = (Object.entries(bindings) as Array<[PitchLadderInputAction, string[]]>).find(([, keys]) => keys.includes(code));
  return found?.[0] ?? null;
}

export function resolvePitchLadderSwipeAction(deltaX: number, deltaY: number): PitchLadderInputAction | null {
  const absX = Math.abs(deltaX);
  const absY = Math.abs(deltaY);
  if (Math.max(absX, absY) < 34) return null;
  if (absY >= absX && deltaY < 0) return "choose_higher";
  if (absY >= absX && deltaY > 0) return "choose_lower";
  return "choose_same";
}
