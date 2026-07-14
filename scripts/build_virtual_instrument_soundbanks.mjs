import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { basename, dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import {
  BasicInstrument,
  BasicPreset,
  BasicSample,
  BasicSoundBank,
  SampleTypes,
  SoundBankLoader,
} from "../frontend/node_modules/spessasynth_core/dist/index.js";
import { ALL_CLASSROOM_SOUNDBANK_BUILD_SPECS } from "../frontend/src/virtual-instruments/core/soundbankBuildPlan.ts";

const repositoryRoot = dirname(dirname(fileURLToPath(import.meta.url)));
const sourcePath = resolve(
  repositoryRoot,
  process.argv[2] ?? "tmp/virtual-instruments-source/deb-extract/usr/share/sounds/sf3/MuseScore_General_Full.sf3",
);
const outputDirectory = resolve(
  repositoryRoot,
  process.argv[3] ?? "app/static/assets/virtual-instruments/audio",
);

const sourceBytes = readFileSync(sourcePath);
const sourceBuffer = sourceBytes.buffer.slice(sourceBytes.byteOffset, sourceBytes.byteOffset + sourceBytes.byteLength);
const sourceBank = SoundBankLoader.fromArrayBuffer(sourceBuffer);
const allVelocities = new Set(Array.from({ length: 127 }, (_, index) => index + 1));

mkdirSync(outputDirectory, { recursive: true });

for (const spec of ALL_CLASSROOM_SOUNDBANK_BUILD_SPECS) {
  if (spec.sourceId === "vcsl_frame_drum_cc0") {
    const outputBank = buildVcslFrameDrumBank();
    const outputBytes = outputBank.writeSF2({ software: "Virtual instrument soundbank builder" });
    const outputPath = resolve(outputDirectory, `${spec.instrumentId}.${spec.outputFormat}`);
    writeFileSync(outputPath, Buffer.from(outputBytes));
    verifySoundbank(outputBytes, outputPath);
    console.log(`${spec.instrumentId}\t${outputBytes.byteLength}\t${outputBank.samples.length} exact VCSL samples`);
    continue;
  }
  const sourcePreset = sourceBank.presets.find(
    (preset) => preset.name === spec.presetName && preset.program === spec.program && preset.isDrum === spec.drum,
  );
  if (!sourcePreset) throw new Error(`Missing source preset for ${spec.instrumentId}: ${spec.presetName}`);

  const outputBank = new BasicSoundBank("sf2");
  outputBank.soundBankInfo = {
    ...sourceBank.soundBankInfo,
    name: `${spec.instrumentId} offline classroom pack`,
    product: "Music Education Virtual Instruments",
    engineer: "Built from MuseScore General with SpessaSynth Core",
    copyright: sourceBank.soundBankInfo.copyright,
  };
  const outputPreset = outputBank.clonePreset(sourcePreset);
  const keyVelocities = new Map(spec.midiNotes.map((note) => [note, new Set(allVelocities)]));
  outputBank.trim(new Map([[outputPreset, keyVelocities]]));
  const outputBytes = outputBank.writeSF2({ software: "Virtual instrument soundbank builder" });
  const outputPath = resolve(outputDirectory, `${spec.instrumentId}.${spec.outputFormat}`);
  writeFileSync(outputPath, Buffer.from(outputBytes));
  const verificationBank = verifySoundbank(outputBytes, outputPath);
  console.log(`${spec.instrumentId}\t${outputBytes.byteLength}\t${verificationBank.samples.length} samples`);
}

function buildVcslFrameDrumBank() {
  const frameDrumSources = [
    { midi: 64, name: "VCSL Frame Drum Center", file: "HDrumL_Hand_rr1_Sum.wav" },
    { midi: 63, name: "VCSL Frame Drum Edge Muted", file: "HDrumL_HitMuted_v2_rr1_Sum.wav" },
  ];
  const bank = new BasicSoundBank("sf2");
  bank.soundBankInfo = {
    ...bank.soundBankInfo,
    name: "VCSL Frame Drum classroom pack",
    product: "Music Education Virtual Instruments",
    engineer: "Built from VCSL CC0 samples with SpessaSynth Core",
    copyright: "Versilian Community Sample Library (VCSL), CC0 1.0",
  };
  const instrument = new BasicInstrument();
  instrument.name = "VCSL Frame Drum";
  for (const source of frameDrumSources) {
    const wavPath = resolve(repositoryRoot, "third_party/audio/VCSL/frame-drum", source.file);
    const wav = decodePcm16Wave(readFileSync(wavPath));
    const sample = new BasicSample(
      source.name,
      wav.sampleRate,
      source.midi,
      0,
      SampleTypes.monoSample,
      0,
      wav.audio.length - 1,
    );
    sample.setAudioData(wav.audio, wav.sampleRate);
    bank.addSamples(sample);
    const zone = instrument.createZone(sample);
    zone.keyRange = { min: source.midi, max: source.midi };
  }
  bank.addInstruments(instrument);
  const preset = new BasicPreset(bank);
  preset.name = "VCSL Frame Drum";
  preset.program = 0;
  preset.bankMSB = 0;
  preset.bankLSB = 0;
  preset.isGMGSDrum = true;
  preset.createZone(instrument);
  bank.addPresets(preset);
  bank.flush();
  return bank;
}

function decodePcm16Wave(bytes) {
  let cursor = 12;
  let format = null;
  let data = null;
  while (cursor + 8 <= bytes.length) {
    const id = bytes.toString("ascii", cursor, cursor + 4);
    const size = bytes.readUInt32LE(cursor + 4);
    const start = cursor + 8;
    if (id === "fmt ") {
      format = {
        encoding: bytes.readUInt16LE(start),
        channels: bytes.readUInt16LE(start + 2),
        sampleRate: bytes.readUInt32LE(start + 4),
        bitsPerSample: bytes.readUInt16LE(start + 14),
      };
    } else if (id === "data") {
      data = bytes.subarray(start, start + size);
    }
    cursor = start + size + (size % 2);
  }
  if (!format || !data || format.encoding !== 1 || format.bitsPerSample !== 16) {
    throw new Error("VCSL frame-drum source must be PCM 16-bit WAV");
  }
  const frames = data.length / 2 / format.channels;
  const audio = new Float32Array(frames);
  for (let frame = 0; frame < frames; frame += 1) {
    let sum = 0;
    for (let channel = 0; channel < format.channels; channel += 1) {
      sum += data.readInt16LE((frame * format.channels + channel) * 2) / 32768;
    }
    audio[frame] = sum / format.channels;
  }
  return { audio, sampleRate: format.sampleRate };
}

function verifySoundbank(outputBytes, outputPath) {
  const verificationBank = SoundBankLoader.fromArrayBuffer(outputBytes);
  if (verificationBank.presets.length !== 1 || verificationBank.samples.length === 0) {
    throw new Error(`Generated soundbank failed verification: ${basename(outputPath)}`);
  }
  return verificationBank;
}
