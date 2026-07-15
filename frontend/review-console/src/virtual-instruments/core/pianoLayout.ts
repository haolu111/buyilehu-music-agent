export type PianoKey = {
  id: string;
  midi: number;
  kind: "white" | "black";
  leftPercent: number;
  widthPercent: number;
};

export function buildPianoLayout(options: { startMidi: number; octaveCount: 1 | 2 }): PianoKey[] {
  if (options.startMidi % 12 !== 0) throw new Error("Piano register must start on C");
  const noteCount = options.octaveCount * 12;
  const whiteCount = options.octaveCount * 7;
  const whiteWidth = 100 / whiteCount;
  const blackWidth = whiteWidth * 0.62;
  let whiteIndex = 0;
  return Array.from({ length: noteCount }, (_, index) => {
    const midi = options.startMidi + index;
    const pitchClass = midi % 12;
    const black = [1, 3, 6, 8, 10].includes(pitchClass);
    if (black) {
      return {
        id: `midi-${midi}`,
        midi,
        kind: "black" as const,
        leftPercent: whiteIndex * whiteWidth - blackWidth / 2,
        widthPercent: blackWidth,
      };
    }
    const key = {
      id: `midi-${midi}`,
      midi,
      kind: "white" as const,
      leftPercent: whiteIndex * whiteWidth,
      widthPercent: whiteWidth,
    };
    whiteIndex += 1;
    return key;
  });
}

