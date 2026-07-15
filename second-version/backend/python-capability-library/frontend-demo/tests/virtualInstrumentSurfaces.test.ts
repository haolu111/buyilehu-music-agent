import {
  buildMalletLayout,
  formatPitchLabel,
} from "../src/virtual-instruments/core/malletLayout";
import { buildPianoLayout } from "../src/virtual-instruments/core/pianoLayout";
import { validatePercussionGrid } from "../src/virtual-instruments/core/percussionGrid";

function assertEqual<T>(actual: T, expected: T, label: string) {
  if (actual !== expected) throw new Error(`${label}: expected ${String(expected)}, got ${String(actual)}`);
}

function assertDeepEqual(actual: unknown, expected: unknown, label: string) {
  const left = JSON.stringify(actual);
  const right = JSON.stringify(expected);
  if (left !== right) throw new Error(`${label}: expected ${right}, got ${left}`);
}

const diatonic = buildMalletLayout({ instrumentId: "virtual_xylophone", mode: "diatonic", registerStartMidi: 60 });
assertDeepEqual(diatonic.map((bar) => bar.midi), [60, 62, 64, 65, 67, 69, 71, 72], "diatonic mode is one classroom octave with endpoint");

const chromatic = buildMalletLayout({ instrumentId: "virtual_xylophone", mode: "chromatic", registerStartMidi: 60 });
assertEqual(chromatic.length, 13, "chromatic mode includes twelve pitch classes and octave endpoint");
assertDeepEqual(chromatic.filter((bar) => bar.row === "accidental").map((bar) => bar.midi), [61, 63, 66, 68, 70], "chromatic accidentals occupy the upper row");

const pentatonic = buildMalletLayout({ instrumentId: "virtual_xylophone", mode: "pentatonic", registerStartMidi: 60 });
assertDeepEqual(pentatonic.map((bar) => bar.midi), [60, 62, 64, 67, 69, 72], "pentatonic mode exposes 1 2 3 5 6 and high tonic");
assertEqual(formatPitchLabel(66, { mode: "number", tonicMidi: 60, accidentalPreference: "sharp" }), "♯4", "number labels follow the selected tonic");
assertEqual(formatPitchLabel(66, { mode: "number", tonicMidi: 61, accidentalPreference: "flat" }), "4", "moveable number labels transpose with tonic");

const piano = buildPianoLayout({ startMidi: 60, octaveCount: 2 });
assertEqual(piano.length, 24, "landscape piano shows two octaves without duplicate endpoint");
assertEqual(piano.filter((key) => key.kind === "white").length, 14, "two piano octaves contain fourteen white keys");
assertDeepEqual(piano.filter((key) => key.kind === "black").slice(0, 5).map((key) => key.midi), [61, 63, 66, 68, 70], "black keys follow real piano pattern");
assertEqual(piano.every((key) => key.widthPercent > 0 && key.leftPercent >= 0), true, "piano keys have usable geometry");

const grid = validatePercussionGrid([
  { id: "drum", instrumentId: "virtual_frame_drum", zoneId: "center", colorToken: "clay" },
  { id: "shaker", instrumentId: "virtual_shaker", zoneId: "short", colorToken: "sage" },
]);
assertEqual(grid.length, 2, "percussion grid accepts two teacher-selected instruments");
let rejected = false;
try {
  validatePercussionGrid([{ id: "piano", instrumentId: "virtual_piano", zoneId: "midi-60", colorToken: "ink" }]);
} catch {
  rejected = true;
}
assertEqual(rejected, true, "percussion grid rejects non-percussion instruments");
