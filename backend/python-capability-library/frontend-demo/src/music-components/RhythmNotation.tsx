import { formalRhythmName } from "../activity/rhythmNaming";

type RhythmNotationProps = {
  rhythm: string;
  className?: string;
  label?: string;
};

const NOTE_X: Record<string, number[]> = {
  quarter: [62],
  quarter_2: [62],
  half: [62],
  dotted_half: [62],
  dotted_quarter: [52, 82],
  eighth_pair: [48, 78],
  eighth_sixteenth: [44, 72, 92],
  eighth_sixteenth_sixteenth: [40, 74, 96],
  sixteenth_eighth: [40, 60, 88],
  sixteenth_sixteenth_eighth: [34, 56, 92],
  sixteenth_four: [34, 56, 78, 100],
  sixteenth_run: [34, 56, 78, 100],
  syncopation: [40, 64, 88],
  eighth_triplet: [40, 64, 88],
};

export function RhythmNotation({ rhythm, className = "", label }: RhythmNotationProps) {
  const accessibleLabel = label ?? formalRhythmName(rhythm);
  if (rhythm === "rest") {
    return (
      <svg className={`rhythm-notation ${className}`} viewBox="0 0 128 84" role="img" aria-label={accessibleLabel}>
        <path className="rhythm-notation-rest" d="M58 14h24l-14 23h20l-26 34 8-25H48z" />
      </svg>
    );
  }
  if (rhythm === "eighth_rest") {
    return (
      <svg className={`rhythm-notation ${className}`} viewBox="0 0 128 84" role="img" aria-label={accessibleLabel}>
        {/* Inline geometry avoids missing-glyph boxes on systems without a music font. */}
        <path
          className="rhythm-notation-eighth-rest"
          d="M55 12c-8 0-14 6-14 13s6 13 14 13c5 0 10-2 15-6L56 70c-2 5 1 10 7 10 4 0 7-2 9-7l14-50c1-4-1-7-5-8-3-1-6 1-9 4l-5 5c-1-7-5-12-12-12Z"
        />
      </svg>
    );
  }

  const xs = NOTE_X[rhythm] ?? NOTE_X.quarter;
  const stemTop = rhythm === "half" || rhythm === "dotted_half" ? 18 : rhythm === "eighth_triplet" ? 24 : 14;
  const stemBottom = 56;
  const beamCount = beamRows(rhythm);
  const filled = rhythm !== "half" && rhythm !== "dotted_half";

  return (
    <svg className={`rhythm-notation ${className}`} viewBox="0 0 128 84" role="img" aria-label={accessibleLabel}>
      {xs.map((x, index) => (
        <g key={`${rhythm}-${x}-${index}`}>
          <ellipse
            className={filled ? "rhythm-note-head filled" : "rhythm-note-head open"}
            cx={x}
            cy={58}
            rx="8.8"
            ry="6.5"
            transform={`rotate(-22 ${x} 58)`}
          />
          <line className="rhythm-note-stem" x1={x + 8} y1={57} x2={x + 8} y2={stemTop} />
          {hasDot(rhythm, index) ? <circle className="rhythm-note-dot" cx={x + 22} cy="56" r="2.8" /> : null}
        </g>
      ))}
      {rhythm === "syncopation" ? (
        <g>
          <path className="rhythm-note-beam" d={beamPath(rhythm, xs, stemTop)} />
          <path className="rhythm-note-beam rhythm-note-beamlet left" d="M48 22H60" />
          <path className="rhythm-note-beam rhythm-note-beamlet right" d="M84 22H96" />
        </g>
      ) : beamCount > 0 ? (
        <g>
          {Array.from({ length: beamCount }).map((_, row) => (
            <path
              key={`${rhythm}-beam-${row}`}
              className="rhythm-note-beam"
              d={beamPath(rhythm, xs, stemTop + row * 8)}
            />
          ))}
        </g>
      ) : null}
      {rhythm === "eighth_triplet" ? <text className="rhythm-triplet-number" x="64" y="15" textAnchor="middle">3</text> : null}
      <line className="rhythm-notation-baseline" x1="20" y1={stemBottom + 17} x2="108" y2={stemBottom + 17} />
    </svg>
  );
}

function beamRows(rhythm: string): number {
  if (rhythm === "sixteenth_four" || rhythm === "sixteenth_run") return 2;
  if (
    rhythm === "eighth_sixteenth" ||
    rhythm === "eighth_sixteenth_sixteenth" ||
    rhythm === "sixteenth_eighth" ||
    rhythm === "sixteenth_sixteenth_eighth" ||
    rhythm === "syncopation"
  ) return 2;
  if (rhythm === "eighth_pair" || rhythm === "eighth_triplet") return 1;
  return 0;
}

function beamPath(rhythm: string, xs: number[], y: number): string {
  const rightStems = xs.map((x) => x + 8);
  if ((rhythm === "eighth_sixteenth" || rhythm === "eighth_sixteenth_sixteenth") && rightStems.length >= 3 && y > 14) {
    return `M${rightStems[1]} ${y}H${rightStems[2]}`;
  }
  if ((rhythm === "sixteenth_eighth" || rhythm === "sixteenth_sixteenth_eighth") && rightStems.length >= 3 && y > 14) {
    return `M${rightStems[0]} ${y}H${rightStems[1]}`;
  }
  return `M${rightStems[0]} ${y}H${rightStems[rightStems.length - 1]}`;
}

function hasDot(rhythm: string, index: number): boolean {
  return rhythm === "dotted_half" || (rhythm === "dotted_quarter" && index === 0);
}
