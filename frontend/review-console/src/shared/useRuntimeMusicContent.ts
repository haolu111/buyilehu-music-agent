import { useEffect, useMemo, useState } from "react";

export type RuntimeMusicContent = {
  meters?: Array<{ id?: string; signature?: string; accentPattern?: string[] }>;
  rhythm_patterns?: Array<{ id?: string; tokens?: string[] }>;
  pitch_sets?: Array<{ id?: string; notes?: string[] }>;
  melody_phrases?: Array<{ id?: string; notes?: string[]; contour?: string[] }>;
  forms?: Array<{ id?: string; sections?: string[] }>;
  dynamics?: Array<{ id?: string; label?: string; symbol?: string }>;
  timbres?: Array<{ id?: string; label?: string; instrument?: string; family?: string }>;
  bpm?: number;
  bars?: number;
};

export function useRuntimeMusicContent() {
  const [content, setContent] = useState<RuntimeMusicContent>({});

  useEffect(() => {
    const receive = (event: MessageEvent) => {
      if (event.origin !== window.location.origin) return;
      if (event.data?.type !== "buyilehu:load-music-content") return;
      const incoming = event.data.config?.musicContent ?? event.data.config?.music_content;
      if (incoming && typeof incoming === "object") setContent(incoming);
    };
    window.addEventListener("message", receive);
    window.parent?.postMessage({ type: "buyilehu:activity-ready" }, window.location.origin);
    return () => window.removeEventListener("message", receive);
  }, []);

  return useMemo(() => ({
    content,
    config: {
      meter: content.meters?.[0]?.signature,
      bpm: content.bpm,
      cycle_count: content.bars,
      question_pattern: rhythmTokens(content.rhythm_patterns?.[0]?.tokens),
      answer_pattern: rhythmTokens(content.rhythm_patterns?.[1]?.tokens ?? content.rhythm_patterns?.[0]?.tokens),
      solfege_set: content.pitch_sets?.[0]?.notes,
      allowed_solfege: content.pitch_sets?.[0]?.notes,
      echo_phrases: content.melody_phrases?.map((item) => item.notes ?? []).filter((item) => item.length),
      melody_phrases: content.melody_phrases?.map((item) => (item.notes ?? []).join(" ")),
      pitch_motion: content.melody_phrases?.[0]?.contour,
      sections: content.forms?.[0]?.sections,
      form_sections: content.forms?.[0]?.sections,
      evidence_terms: content.dynamics?.map((item) => item.label ?? item.symbol ?? item.id ?? ""),
      instrument_pool: content.timbres?.map((item) => item.label ?? item.id ?? ""),
      family_set: Array.from(
        new Set(
          content.timbres
            ?.map((item) => item.family)
            .filter((value): value is string => Boolean(value)) ?? [],
        ),
      ),
      instrument: content.timbres?.[0]?.instrument,
    },
    revisionKey: JSON.stringify(content),
  }), [content]);
}

function rhythmTokens(tokens?: string[]) {
  const names: Record<string, string> = {
    ta: "quarter",
    "ti-ti": "eighth_pair",
    rest: "rest",
    "ta-a": "syncopation",
    ti: "eighth_pair",
  };
  return tokens?.map((token) => names[token] ?? token);
}
