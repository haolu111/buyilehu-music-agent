import { readFileSync } from "node:fs";
import { join } from "node:path";

function equal<T>(actual: T, expected: T, label: string) {
  if (actual !== expected) throw new Error(`${label}: expected ${String(expected)}, got ${String(actual)}`);
}

const source = readFileSync(join(process.cwd(), "../app/static/assets/virtual-instruments/audio/virtual_frame_drum-wav-map.js"), "utf8");
const samples = [...source.matchAll(/"([A-G](?:b)?-?\d+)":"data:audio\/wav;base64,([^"]+)"/g)];
equal(samples.length, 2, "frame drum fallback contains center and edge recordings");

for (const [, noteName, encoded] of samples) {
  const bytes = Buffer.from(encoded, "base64");
  let peak = 0;
  for (let offset = 44; offset + 1 < bytes.length; offset += 2) peak = Math.max(peak, Math.abs(bytes.readInt16LE(offset)));
  if (peak < 8_000) throw new Error(`${noteName} frame-drum fallback is effectively silent: PCM peak ${peak}`);
}

