import { getVirtualInstrumentDefinition } from "./virtualInstrumentCatalog";

export type PercussionGridTile = {
  id: string;
  instrumentId: string;
  zoneId: string;
  colorToken: string;
};

export function validatePercussionGrid(tiles: PercussionGridTile[]): PercussionGridTile[] {
  if (tiles.length < 2 || tiles.length > 6) throw new Error("Percussion grid requires 2-6 instruments");
  const ids = new Set<string>();
  return tiles.map((tile) => {
    if (!tile.id || ids.has(tile.id)) throw new Error(`Duplicate percussion grid tile id: ${tile.id}`);
    ids.add(tile.id);
    const instrument = getVirtualInstrumentDefinition(tile.instrumentId);
    if (instrument.family !== "percussion") throw new Error(`${tile.instrumentId} is not a percussion instrument`);
    if (!instrument.zones.some((zone) => zone.id === tile.zoneId)) {
      throw new Error(`Unknown zone ${tile.zoneId} for ${tile.instrumentId}`);
    }
    return { ...tile };
  });
}

