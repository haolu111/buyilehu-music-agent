import { Text } from "@radix-ui/themes";
import type { BeatTimelineEvent } from "../activity/rhythmWarmupLogic";
import { RhythmNotation } from "./RhythmNotation";

type MeterTrackProps = {
  events: BeatTimelineEvent[];
  elapsedMs: number;
  totalMs: number;
};

export function MeterTrack({ events, elapsedMs, totalMs }: MeterTrackProps) {
  const progress = totalMs > 0 ? Math.min(100, (elapsedMs / totalMs) * 100) : 0;
  return (
    <section className="primary-tool meter-track" aria-label="节拍轨道">
      <div className="tool-heading">
        <Text as="p" size="2" weight="bold">节拍轨道</Text>
        <Text as="p" size="1" color="gray">小节、拍点、休止一屏看清</Text>
      </div>
      <div className="track-progress">
        <span style={{ width: `${progress}%` }} />
      </div>
      <div className="beat-event-grid">
        {events.map((event) => (
          <div
            key={event.id}
            className={`beat-event ${event.hitRequired ? "hit" : "rest"} ${elapsedMs >= event.startMs ? "passed" : ""}`}
            style={{ "--event-color": event.color } as React.CSSProperties}
          >
            <span>{event.bar}-{event.beatInBar}</span>
            <strong>
              <RhythmNotation rhythm={event.patternId} label={event.syllable} />
            </strong>
          </div>
        ))}
      </div>
    </section>
  );
}
