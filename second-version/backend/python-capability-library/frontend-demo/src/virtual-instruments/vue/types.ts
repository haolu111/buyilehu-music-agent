import type { AccidentalPreference, MalletLayoutMode, PitchLabelMode } from "../core/malletLayout";

export type VirtualInstrumentPlayerProps = {
  instrumentId: string;
  disabled?: boolean;
  defaultVelocity?: number;
  autoInitialize?: boolean;
  showControls?: boolean;
  reviewMode?: boolean;
  layoutMode?: MalletLayoutMode;
  registerStartMidi?: number;
  labelMode?: PitchLabelMode;
  tonicMidi?: number;
  accidentalPreference?: AccidentalPreference;
  rollEnabled?: boolean;
  rollIntervalMs?: number;
};
