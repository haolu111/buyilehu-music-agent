import { readFileSync } from "node:fs";
import { join } from "node:path";

function equal<T>(actual: T, expected: T, label: string) {
  if (actual !== expected) throw new Error(`${label}: expected ${String(expected)}, got ${String(actual)}`);
}

const source = readFileSync(join(process.cwd(), "../../app/static/assets/virtual-instruments/audio/virtual_frame_drum-wav-map.js"), "utf8");
const samples = [...source.matchAll(/"([A-G](?:b)?-?\d+)":"data:audio\/wav;base64,([^"]+)"/g)];
equal(samples.length, 2, "frame drum fallback contains center and edge recordings");

for (const [, noteName, encoded] of samples) {
  const bytes = Buffer.from(encoded, "base64");
  const dataChunk = bytes.indexOf(Buffer.from("data"));
  if (dataChunk < 0) throw new Error(`${noteName} frame-drum fallback has no WAV data chunk`);
  const dataStart = dataChunk + 8;
  const dataSize = bytes.readUInt32LE(dataChunk + 4);
  let peak = 0;
  let sumSquares = 0;
  let sampleCount = 0;
  for (let offset = dataStart; offset + 1 < Math.min(bytes.length, dataStart + dataSize); offset += 2) {
    const sample = bytes.readInt16LE(offset);
    peak = Math.max(peak, Math.abs(sample));
    sumSquares += sample * sample;
    sampleCount += 1;
  }
  const rms = Math.sqrt(sumSquares / Math.max(1, sampleCount));
  if (peak < 20_000 || rms < 500) throw new Error(`${noteName} frame-drum fallback is effectively silent: PCM peak ${peak}, RMS ${rms}`);
}

