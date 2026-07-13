import { getVirtualInstrumentDefinition, type VirtualInstrumentZoneAction } from "./virtualInstrumentCatalog";

export type PlayableHitArea = { x: number; y: number; width: number; height: number };

export type PlayableZone = {
  id: string;
  label: string;
  midi: number;
  action: VirtualInstrumentZoneAction;
  hitArea: PlayableHitArea;
};

export function buildPlayableZones(instrumentId: string): PlayableZone[] {
  const instrument = getVirtualInstrumentDefinition(instrumentId);
  if (instrument.pitchRange) {
    const { minMidi, maxMidi } = instrument.pitchRange;
    const count = Math.max(0, maxMidi - minMidi + 1);
    return Array.from({ length: count }, (_, index) => ({
      id: `midi-${minMidi + index}`,
      label: midiLabel(minMidi + index),
      midi: minMidi + index,
      action: "note" as const,
      hitArea: { x: index / count * 100, y: 0, width: 100 / count, height: 100 }
    }));
  }
  const count = Math.max(1, instrument.zones.length);
  return instrument.zones.map((zone, index) => ({
    ...zone,
    hitArea: { x: index / count * 100, y: 0, width: 100 / count, height: 100 }
  }));
}

function midiLabel(midi: number) {
  const names = ["C", "C♯", "D", "E♭", "E", "F", "F♯", "G", "A♭", "A", "B♭", "B"];
  return `${names[midi % 12]}${Math.floor(midi / 12) - 1}`;
}
