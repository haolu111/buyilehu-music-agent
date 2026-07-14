import catalogData from "../../../contracts/music/pitch-catalog.v1.json";

export type PitchDefinition = {
  id: string;
  semitone: number;
  role: "pitch_class" | "octave_endpoint";
  numberLabels: string[];
  letterNames: string[];
  solfegeAliases: string[];
  inputAliases: string[];
};

export type PitchRegisterDefinition = {
  id: "small" | "small_one" | "small_two";
  chineseName: string;
  scientificOctave: 3 | 4 | 5;
  baseMidi: 48 | 60 | 72;
  octaveMark: "lower_dot" | "none" | "upper_dot";
};

export type RegisteredPitchDefinition = {
  id: string;
  pitchId: string;
  registerId: PitchRegisterDefinition["id"];
  midi: number;
  semitone: number;
  numberLabels: string[];
  scientificLabels: string[];
};

type PitchCatalog = {
  version: string;
  tuning: "12_tet";
  stepsPerOctave: number;
  defaultTonicMidi: number;
  registers: PitchRegisterDefinition[];
  pitches: PitchDefinition[];
};

const catalog = catalogData as PitchCatalog;

export const PITCH_CATALOG_VERSION = catalog.version;
export const DEFAULT_TONIC_MIDI = catalog.defaultTonicMidi;
export const PITCH_DEFINITIONS = catalog.pitches;
export const PITCH_CLASS_DEFINITIONS = PITCH_DEFINITIONS.filter((pitch) => pitch.role === "pitch_class");
export const PITCH_REGISTERS = catalog.registers;
export const REGISTERED_PITCH_DEFINITIONS: RegisteredPitchDefinition[] = PITCH_REGISTERS.flatMap((register) =>
  PITCH_CLASS_DEFINITIONS.map((pitch) => ({
    id: `${register.id}:${pitch.id}`,
    pitchId: pitch.id,
    registerId: register.id,
    midi: register.baseMidi + pitch.semitone,
    semitone: pitch.semitone,
    numberLabels: pitch.numberLabels,
    scientificLabels: pitch.letterNames.map((name) => `${name}${register.scientificOctave}`)
  }))
);

const pitchByAlias = new Map<string, PitchDefinition>();
for (const pitch of PITCH_DEFINITIONS) {
  for (const alias of [pitch.id, ...pitch.numberLabels, ...pitch.solfegeAliases, ...pitch.inputAliases]) {
    pitchByAlias.set(normalizePitchToken(alias), pitch);
  }
}

const registeredPitchByAlias = new Map<string, RegisteredPitchDefinition>();
for (const pitch of REGISTERED_PITCH_DEFINITIONS) {
  for (const alias of [pitch.id, ...pitch.scientificLabels]) {
    registeredPitchByAlias.set(normalizeRegisteredPitchToken(alias), pitch);
  }
}

export function resolvePitchToken(token: unknown): PitchDefinition | undefined {
  return pitchByAlias.get(normalizePitchToken(token));
}

export function resolveRegisteredPitchToken(token: unknown): RegisteredPitchDefinition | undefined {
  return registeredPitchByAlias.get(normalizeRegisteredPitchToken(token));
}

export function pitchToMidi(token: unknown, tonicMidi = DEFAULT_TONIC_MIDI): number {
  const pitch = resolvePitchToken(token);
  if (!pitch) throw new Error(`Unknown pitch token: ${String(token)}`);
  return Math.round(Number(tonicMidi)) + pitch.semitone;
}

export function registeredPitchToMidi(token: unknown): number {
  const pitch = resolveRegisteredPitchToken(token);
  if (!pitch) throw new Error(`Unknown registered pitch token: ${String(token)}`);
  return pitch.midi;
}

export function sequenceToMidiOffsets(tokens: unknown[]): number[] {
  return tokens.map((token) => {
    const pitch = resolvePitchToken(token);
    if (!pitch) throw new Error(`Unknown pitch token: ${String(token)}`);
    return pitch.semitone;
  });
}

function normalizePitchToken(token: unknown): string {
  return String(token ?? "").trim().toLocaleLowerCase();
}

function normalizeRegisteredPitchToken(token: unknown): string {
  return String(token ?? "")
    .trim()
    .toLocaleLowerCase()
    .replace(/([a-g])#/g, "$1♯")
    .replace(/([a-g])b/g, "$1♭");
}
