import { getVirtualInstrumentDefinition } from "./virtualInstrumentCatalog";

export type MalletLayoutMode = "diatonic" | "chromatic" | "pentatonic";
export type PitchLabelMode = "hidden" | "note" | "solfege" | "number" | "note_number";
export type AccidentalPreference = "sharp" | "flat";

export type PitchLabelOptions = {
  mode: PitchLabelMode;
  tonicMidi?: number;
  accidentalPreference?: AccidentalPreference;
};

export type MalletBar = {
  id: string;
  midi: number;
  row: "natural" | "accidental";
  leftPercent: number;
  widthPercent: number;
  heightPercent: number;
};

export type MalletLayoutOptions = {
  instrumentId: string;
  mode: MalletLayoutMode;
  registerStartMidi: number;
};

const MODE_OFFSETS: Record<Exclude<MalletLayoutMode, "chromatic">, number[]> = {
  diatonic: [0, 2, 4, 5, 7, 9, 11, 12],
  pentatonic: [0, 2, 4, 7, 9, 12],
};
const NATURAL_OFFSETS = new Set([0, 2, 4, 5, 7, 9, 11, 12]);
const NOTE_NAMES_SHARP = ["C", "C♯", "D", "D♯", "E", "F", "F♯", "G", "G♯", "A", "A♯", "B"];
const NOTE_NAMES_FLAT = ["C", "D♭", "D", "E♭", "E", "F", "G♭", "G", "A♭", "A", "B♭", "B"];
const NUMBER_SHARP = ["1", "♯1", "2", "♯2", "3", "4", "♯4", "5", "♯5", "6", "♯6", "7"];
const NUMBER_FLAT = ["1", "♭2", "2", "♭3", "3", "4", "♭5", "5", "♭6", "6", "♭7", "7"];
const SOLFEGE_SHARP = ["do", "di", "re", "ri", "mi", "fa", "fi", "sol", "si", "la", "li", "ti"];
const SOLFEGE_FLAT = ["do", "ra", "re", "me", "mi", "fa", "se", "sol", "le", "la", "te", "ti"];

export function buildMalletLayout(options: MalletLayoutOptions): MalletBar[] {
  const definition = getVirtualInstrumentDefinition(options.instrumentId);
  if (definition.family !== "mallet" || !definition.pitchRange) throw new Error(`${options.instrumentId} is not a mallet instrument`);
  const { minMidi, maxMidi } = definition.pitchRange;
  if (options.registerStartMidi < minMidi || options.registerStartMidi + 12 > maxMidi) {
    throw new Error(`Register ${options.registerStartMidi}-${options.registerStartMidi + 12} exceeds ${options.instrumentId} range`);
  }
  const offsets = options.mode === "chromatic" ? Array.from({ length: 13 }, (_, index) => index) : MODE_OFFSETS[options.mode];
  const naturalCount = offsets.filter((offset) => NATURAL_OFFSETS.has(offset)).length;
  const naturalWidth = 86 / naturalCount;
  let naturalIndex = 0;
  return offsets.map((offset) => {
    const natural = NATURAL_OFFSETS.has(offset);
    const currentNaturalIndex = naturalIndex;
    if (natural) naturalIndex += 1;
    const leftPercent = natural
      ? 7 + currentNaturalIndex * naturalWidth
      : 7 + accidentalBoundaryIndex(offset) * naturalWidth - naturalWidth * 0.31;
    return {
      id: `midi-${options.registerStartMidi + offset}`,
      midi: options.registerStartMidi + offset,
      row: natural ? "natural" : "accidental",
      leftPercent,
      widthPercent: natural ? naturalWidth * 0.78 : naturalWidth * 0.6,
      heightPercent: natural ? 88 - offset * 1.45 : 51 - offset * 0.65,
    };
  });
}

export function formatPitchLabel(midi: number, options: PitchLabelOptions): string {
  if (options.mode === "hidden") return "";
  const accidental = options.accidentalPreference ?? "sharp";
  const pitchClass = modulo(midi, 12);
  const octave = Math.floor(midi / 12) - 1;
  const note = `${(accidental === "flat" ? NOTE_NAMES_FLAT : NOTE_NAMES_SHARP)[pitchClass]}${octave}`;
  const relative = modulo(midi - (options.tonicMidi ?? 60), 12);
  const number = (accidental === "flat" ? NUMBER_FLAT : NUMBER_SHARP)[relative];
  const solfege = (accidental === "flat" ? SOLFEGE_FLAT : SOLFEGE_SHARP)[relative];
  if (options.mode === "note") return note;
  if (options.mode === "number") return number;
  if (options.mode === "solfege") return solfege;
  return `${note} · ${number}`;
}

function accidentalBoundaryIndex(offset: number): number {
  const boundaries: Record<number, number> = { 1: 1, 3: 2, 6: 4, 8: 5, 10: 6 };
  return boundaries[offset] ?? 0;
}

function modulo(value: number, divisor: number): number {
  return ((value % divisor) + divisor) % divisor;
}

