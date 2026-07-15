import catalogData from "../../../../contracts/music/instrument-timbre-catalog.v1.json";

export type TimbrePreview = {
  baseMidi: number;
  offsets: number[];
  gap: number;
  duration: number;
  gain: number;
};

export type ExactTimbreDefinition = {
  id: string;
  label: string;
  familyId: "keyboard" | "plucked_string" | "bowed_string" | "woodwind" | "brass" | "free_reed" | "percussion";
  familyLabel: string;
  classroomFamily: string;
  playbackInstrument: string;
  sampleFidelity: "exact_open_sample";
  evidenceTerms: string[];
  classroomNote: string;
  preview: TimbrePreview;
};

export type PendingExactTimbreDefinition = {
  id: string;
  label: string;
  familyLabel: string;
  playbackInstrument: string;
  sampleFidelity: "close_soundfont_sample" | "approximate_soundfont_sample";
  evidenceTerms: string[];
  classroomNote: string;
  requiredExactAsset: string;
  preview: TimbrePreview;
};

export type TimbreSampleLibrary = {
  id: string;
  format: string;
  license: string;
  licenseUrl: string;
  sourceUrl: string;
  attribution: string;
};

type InstrumentTimbreCatalog = {
  version: string;
  sampleLibrary: TimbreSampleLibrary;
  exactTimbres: ExactTimbreDefinition[];
  pendingExactTimbres: PendingExactTimbreDefinition[];
};

const catalog = catalogData as InstrumentTimbreCatalog;

export const INSTRUMENT_TIMBRE_CATALOG_VERSION = catalog.version;
export const SAMPLE_LIBRARY = catalog.sampleLibrary;
export const EXACT_TIMBRE_DEFINITIONS = catalog.exactTimbres;
export const PENDING_EXACT_TIMBRE_DEFINITIONS = catalog.pendingExactTimbres;
