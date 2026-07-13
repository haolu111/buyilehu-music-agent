export type VirtualInstrumentSoundbankBuildSpec = {
  instrumentId: string;
  presetName: string;
  program: number;
  drum: boolean;
  midiNotes: number[];
  sourceId: "musescore_general_hq" | "vcsl_frame_drum_cc0";
  outputFormat: "sf3" | "sf2";
};

function range(min: number, max: number): number[] {
  return Array.from({ length: max - min + 1 }, (_, index) => min + index);
}

export const VIRTUAL_INSTRUMENT_SOUNDBANK_BUILD_PLAN: VirtualInstrumentSoundbankBuildSpec[] = [
  { instrumentId: "virtual_piano", presetName: "Grand Piano", program: 0, drum: false, midiNotes: range(48, 83), sourceId: "musescore_general_hq", outputFormat: "sf3" },
  { instrumentId: "virtual_xylophone", presetName: "Xylophone", program: 13, drum: false, midiNotes: range(60, 84), sourceId: "musescore_general_hq", outputFormat: "sf3" },
  { instrumentId: "virtual_marimba", presetName: "Marimba", program: 12, drum: false, midiNotes: range(48, 84), sourceId: "musescore_general_hq", outputFormat: "sf3" },
  { instrumentId: "virtual_glockenspiel", presetName: "Glockenspiel", program: 9, drum: false, midiNotes: range(72, 96), sourceId: "musescore_general_hq", outputFormat: "sf3" },
  { instrumentId: "virtual_frame_drum", presetName: "VCSL Frame Drum", program: 0, drum: true, midiNotes: [64, 63], sourceId: "vcsl_frame_drum_cc0", outputFormat: "sf2" },
  { instrumentId: "virtual_snare_drum", presetName: "Standard", program: 0, drum: true, midiNotes: [38, 37], sourceId: "musescore_general_hq", outputFormat: "sf3" },
  { instrumentId: "virtual_woodblock", presetName: "Standard", program: 0, drum: true, midiNotes: [76, 77], sourceId: "musescore_general_hq", outputFormat: "sf3" },
  { instrumentId: "virtual_shaker", presetName: "Standard", program: 0, drum: true, midiNotes: [70], sourceId: "musescore_general_hq", outputFormat: "sf3" },
  { instrumentId: "virtual_triangle", presetName: "Standard", program: 0, drum: true, midiNotes: [81, 80], sourceId: "musescore_general_hq", outputFormat: "sf3" },
  { instrumentId: "virtual_tambourine", presetName: "Standard", program: 0, drum: true, midiNotes: [54], sourceId: "musescore_general_hq", outputFormat: "sf3" },
];

export const METRONOME_SOUNDBANK_BUILD_SPEC: VirtualInstrumentSoundbankBuildSpec = {
  instrumentId: "virtual_metronome", presetName: "Standard", program: 0, drum: true,
  midiNotes: [33, 34], sourceId: "musescore_general_hq", outputFormat: "sf3",
};

export const ALL_CLASSROOM_SOUNDBANK_BUILD_SPECS = [
  ...VIRTUAL_INSTRUMENT_SOUNDBANK_BUILD_PLAN,
  METRONOME_SOUNDBANK_BUILD_SPEC,
];
