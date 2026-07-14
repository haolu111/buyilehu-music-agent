import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import {
  BasicSoundBank,
  SoundBankLoader,
  SpessaSynthProcessor,
} from "../frontend/node_modules/spessasynth_core/dist/index.js";
import { ALL_CLASSROOM_SOUNDBANK_BUILD_SPECS } from "../frontend/src/virtual-instruments/core/soundbankBuildPlan.ts";

const repositoryRoot = dirname(dirname(fileURLToPath(import.meta.url)));
const sourceDirectory = resolve(repositoryRoot, "app/static/assets/midi-js-soundfonts/FluidR3_GM");
const primaryDirectory = resolve(repositoryRoot, "app/static/assets/virtual-instruments/audio");
const outputDirectory = primaryDirectory;
const pitchedSources = {
  virtual_piano: "acoustic_grand_piano-mp3.js",
  virtual_xylophone: "xylophone-mp3.js",
  virtual_marimba: "marimba-mp3.js",
  virtual_glockenspiel: "glockenspiel-mp3.js",
};
const directWavSources = {
  virtual_frame_drum: {
    64: "third_party/audio/VCSL/frame-drum/HDrumL_Hand_rr1_Sum.wav",
    63: "third_party/audio/VCSL/frame-drum/HDrumL_HitMuted_v2_rr1_Sum.wav",
  },
};

mkdirSync(outputDirectory, { recursive: true });

for (const spec of ALL_CLASSROOM_SOUNDBANK_BUILD_SPECS) {
  const pitchedSource = pitchedSources[spec.instrumentId];
  const directWavSource = directWavSources[spec.instrumentId];
  const sampleMap = pitchedSource
    ? trimMidiJsMap(resolve(sourceDirectory, pitchedSource), spec.midiNotes)
    : directWavSource
      ? buildDirectWavMap(directWavSource, spec.midiNotes)
      : await renderPercussionMap(resolve(primaryDirectory, `${spec.instrumentId}.${spec.outputFormat}`), spec.midiNotes);
  const format = pitchedSource ? "mp3" : "wav";
  const outputPath = resolve(outputDirectory, `${spec.instrumentId}-${format}-map.js`);
  writeSampleMap(outputPath, spec.instrumentId, sampleMap);
  console.log(`${spec.instrumentId}\t${Object.keys(sampleMap).length} samples\t${format}`);
}

function buildDirectWavMap(sourceByMidi, midiNotes) {
  return Object.fromEntries(midiNotes.map((midi) => {
    const sourcePath = sourceByMidi[midi];
    if (!sourcePath) throw new Error(`Missing direct WAV source for MIDI ${midi}`);
    const bytes = readFileSync(resolve(repositoryRoot, sourcePath));
    return [midiToNoteName(midi), `data:audio/wav;base64,${bytes.toString("base64")}`];
  }));
}

function trimMidiJsMap(path, midiNotes) {
  const source = readFileSync(path, "utf8");
  const sourceMap = Object.fromEntries(
    [...source.matchAll(/^"([A-G](?:b)?-?\d+)":\s*"([^"]+)"/gm)].map((match) => [match[1], match[2]]),
  );
  if (Object.keys(sourceMap).length === 0) throw new Error(`Invalid MIDI-JS map: ${path}`);
  return Object.fromEntries(midiNotes.map((midi) => {
    const noteName = midiToNoteName(midi);
    const dataUrl = sourceMap[noteName];
    if (!dataUrl) throw new Error(`Missing ${noteName} in ${path}`);
    return [noteName, dataUrl];
  }));
}

async function renderPercussionMap(soundbankPath, midiNotes) {
  await BasicSoundBank.isSF3DecoderReady;
  const sourceBytes = readFileSync(soundbankPath);
  const sourceBuffer = sourceBytes.buffer.slice(sourceBytes.byteOffset, sourceBytes.byteOffset + sourceBytes.byteLength);
  const sampleMap = {};
  for (const midi of [...new Set(midiNotes)]) {
    const bank = SoundBankLoader.fromArrayBuffer(sourceBuffer.slice(0));
    const synthesizer = new SpessaSynthProcessor(44_100, { effectsEnabled: false, voiceCap: 32 });
    await synthesizer.processorInitialized;
    synthesizer.soundBankManager.addSoundBank(bank, "offline-pack");
    synthesizer.midiChannels[9].setDrums(true);
    synthesizer.programChange(9, 0);
    synthesizer.noteOn(9, midi, 96);
    const left = new Float32Array(44_100 * 4);
    const right = new Float32Array(left.length);
    for (let offset = 0; offset < left.length; offset += 128) {
      synthesizer.process(left, right, offset, Math.min(128, left.length - offset));
    }
    synthesizer.destroySynthProcessor();
    const mono = trimSilence(left, right, 44_100);
    sampleMap[midiToNoteName(midi)] = `data:audio/wav;base64,${encodeWave(mono, 44_100).toString("base64")}`;
  }
  return sampleMap;
}

function trimSilence(left, right, sampleRate) {
  const mono = new Float32Array(left.length);
  let lastAudible = 0;
  for (let index = 0; index < mono.length; index += 1) {
    mono[index] = (left[index] + right[index]) / 2;
    if (Math.abs(mono[index]) > 0.0001) lastAudible = index;
  }
  const end = Math.min(mono.length, lastAudible + Math.round(sampleRate * 0.12));
  return mono.slice(0, Math.max(end, Math.round(sampleRate * 0.1)));
}

function encodeWave(samples, sampleRate) {
  const dataSize = samples.length * 2;
  const buffer = Buffer.alloc(44 + dataSize);
  buffer.write("RIFF", 0);
  buffer.writeUInt32LE(36 + dataSize, 4);
  buffer.write("WAVEfmt ", 8);
  buffer.writeUInt32LE(16, 16);
  buffer.writeUInt16LE(1, 20);
  buffer.writeUInt16LE(1, 22);
  buffer.writeUInt32LE(sampleRate, 24);
  buffer.writeUInt32LE(sampleRate * 2, 28);
  buffer.writeUInt16LE(2, 32);
  buffer.writeUInt16LE(16, 34);
  buffer.write("data", 36);
  buffer.writeUInt32LE(dataSize, 40);
  for (let index = 0; index < samples.length; index += 1) {
    const sample = Math.max(-1, Math.min(1, samples[index]));
    buffer.writeInt16LE(Math.round(sample < 0 ? sample * 32768 : sample * 32767), 44 + index * 2);
  }
  return buffer;
}

function midiToNoteName(midi) {
  const names = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"];
  return `${names[midi % 12]}${Math.floor(midi / 12) - 1}`;
}

function writeSampleMap(path, instrumentId, sampleMap) {
  writeFileSync(path, `globalThis.__VIRTUAL_INSTRUMENT_SAMPLE_MAPS__ ??= {};\n` +
    `globalThis.__VIRTUAL_INSTRUMENT_SAMPLE_MAPS__[${JSON.stringify(instrumentId)}] = ${JSON.stringify(sampleMap)};\n`);
}
