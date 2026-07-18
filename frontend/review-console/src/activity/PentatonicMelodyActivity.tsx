import { Badge, Button, Container, Flex, Grid, Heading, Text } from "@radix-ui/themes";
import { CheckCircle2, Music2, RotateCcw, Volume2, X } from "lucide-react";
import { useMemo, useState } from "react";
import { playPlayableInstrumentSequence } from "../shared/realAudio";
import { playableInstrumentAssetFor } from "./playableInstrumentAssets";
import {
  buildPentatonicCreationExport,
  buildPentatonicCreationSummary,
  buildPentatonicMelodyPlan,
  evaluatePentatonicMelody,
  noteOffsetForSolfege,
  recordPentatonicCreationEvent,
  type PentatonicCreationEvent
} from "./pentatonicMelodyLogic";
import "./primaryActivity.css";
import { ReadableData } from "./ReadableData";

type PentatonicMelodyState = {
  workflow?: {
    education_alignment?: {
      primary_competency?: string;
      music_elements?: string[];
      student_practices?: string[];
    };
  };
  config?: {
    allowed_solfege?: string[];
    rhythm_pattern?: string[];
    meter?: string;
    composition_total_bars?: number;
    bpm?: number;
    virtual_instrument?: string;
    teacher_confirm_required?: boolean;
  };
};

declare global {
  interface Window {
    __PENTATONIC_MELODY_STATE__?: PentatonicMelodyState;
  }
}

const defaultState: PentatonicMelodyState = {
  workflow: {
    education_alignment: {
      primary_competency: "创意实践",
      music_elements: ["音高", "五声音阶", "节奏", "创编结构"],
      student_practices: ["play", "create", "listen", "revise"]
    }
  },
  config: {
    allowed_solfege: ["do", "re", "mi", "sol", "la"],
    rhythm_pattern: ["quarter", "quarter", "eighth_pair", "quarter"],
    meter: "2/4",
    composition_total_bars: 2,
    bpm: 88,
    virtual_instrument: "virtual_xylophone",
    teacher_confirm_required: true
  }
};

const SOLFEGE_LABELS: Record<string, string> = {
  do: "1 do",
  re: "2 re",
  mi: "3 mi",
  sol: "5 sol",
  la: "6 la"
};

export function PentatonicMelodyActivity({ state = window.__PENTATONIC_MELODY_STATE__ ?? defaultState }: { state?: PentatonicMelodyState }) {
  const config = state.config ?? defaultState.config ?? {};
  const plan = useMemo(() => buildPentatonicMelodyPlan({
    solfegeSet: config.allowed_solfege,
    rhythmPattern: config.rhythm_pattern,
    meter: config.meter,
    compositionTotalBars: config.composition_total_bars,
    bpm: config.bpm
  }), [config.allowed_solfege, config.bpm, config.composition_total_bars, config.meter, config.rhythm_pattern]);
  const alignment = state.workflow?.education_alignment ?? defaultState.workflow?.education_alignment ?? {};
  const [placedNotes, setPlacedNotes] = useState<string[]>([]);
  const [auditioned, setAuditioned] = useState(false);
  const [confirmed, setConfirmed] = useState(false);
  const [creationEvents, setCreationEvents] = useState<PentatonicCreationEvent[]>([]);
  const evaluation = evaluatePentatonicMelody(plan, placedNotes, auditioned);
  const creationSummary = useMemo(
    () => buildPentatonicCreationSummary(plan, placedNotes, creationEvents, auditioned),
    [auditioned, creationEvents, placedNotes, plan]
  );
  const creationExport = useMemo(() => buildPentatonicCreationExport(creationSummary), [creationSummary]);

  const placeNote = (note: string) => {
    if (placedNotes.length >= plan.slots.length) return;
    const slotIndex = placedNotes.length;
    setPlacedNotes((current) => [...current, note]);
    setCreationEvents((current) => recordPentatonicCreationEvent(current, {
      eventType: "place_note",
      note,
      slotIndex,
      timestampMs: Date.now(),
    }));
    setAuditioned(false);
    playPlayableInstrumentSequence([noteOffsetForSolfege(note)], {
      instrument: config.virtual_instrument || "virtual_xylophone",
      gap: 0.18,
      duration: 0.18,
      gain: 0.62,
      baseMidi: 60,
      oscillatorWave: "triangle"
    });
  };

  const audition = () => {
    if (!placedNotes.length) return;
    setAuditioned(true);
    setCreationEvents((current) => recordPentatonicCreationEvent(current, {
      eventType: "audition_phrase",
      notes: placedNotes,
      timestampMs: Date.now(),
    }));
    playPlayableInstrumentSequence(placedNotes.map(noteOffsetForSolfege), {
      instrument: config.virtual_instrument || "virtual_xylophone",
      gap: 60 / plan.bpm,
      duration: 0.32,
      gain: 0.62,
      baseMidi: 60,
      oscillatorWave: "triangle"
    });
  };

  const undo = () => {
    const note = placedNotes[placedNotes.length - 1];
    const slotIndex = Math.max(0, placedNotes.length - 1);
    setPlacedNotes((current) => current.slice(0, -1));
    if (note) {
      setCreationEvents((current) => recordPentatonicCreationEvent(current, {
        eventType: "undo_note",
        note,
        slotIndex,
        timestampMs: Date.now(),
      }));
    }
    setAuditioned(false);
    setConfirmed(false);
  };

  const reset = () => {
    setPlacedNotes([]);
    setAuditioned(false);
    setConfirmed(false);
    setCreationEvents([]);
  };

  const confirmCreation = () => {
    setConfirmed(true);
    setCreationEvents((current) => recordPentatonicCreationEvent(current, {
      eventType: "teacher_confirm",
      notes: placedNotes,
      timestampMs: Date.now(),
    }));
  };

  return (
    <main className="primary-activity-shell pentatonic-melody-shell">
      <Container size="4" px="4">
        <section className="teacher-control-bar">
          <Flex align="center" justify="between" gap="3" wrap="wrap">
            <Flex align="center" gap="2" wrap="wrap">
              <Music2 size={18} />
              <Text weight="bold">五声音条琴控制</Text>
              <Badge color="green" variant="soft">{placedNotes.length}/{plan.slots.length}</Badge>
              <Badge color="amber" variant="soft">{plan.meter} · {plan.bpm} BPM</Badge>
            </Flex>
            <Flex gap="2" wrap="wrap">
              <Button highContrast onClick={audition} disabled={!placedNotes.length} aria-label="回放五声短句">
                <Volume2 size={17} />
                回放
              </Button>
              <Button variant="soft" onClick={undo} disabled={!placedNotes.length} aria-label="撤回一个音">
                <X size={17} />
              </Button>
              <Button variant="soft" color="gray" onClick={reset} aria-label="重置">
                <RotateCcw size={17} />
              </Button>
            </Flex>
          </Flex>
        </section>

        <Grid columns={{ initial: "1", md: "1.08fr .92fr" }} gap="4" className="activity-stage">
          <section className="activity-board pentatonic-board" aria-label="五声音条琴创编活动">
            <Flex align="center" gap="2" wrap="wrap">
              <Badge color="green" variant="soft">{alignment.primary_competency ?? "创意实践"}</Badge>
              {(alignment.music_elements ?? []).map((element) => <Badge key={element} color="amber" variant="soft">{element}</Badge>)}
            </Flex>
            <Heading as="h1" size="8" className="activity-title">五声音条琴创编</Heading>
            <Text as="p" size="3" color="gray" className="activity-subtitle">
              只用 do、re、mi、sol、la 填入节奏格，回放后修改，再说明五声短句怎么组成。
            </Text>

            <Text weight="bold" className="tool-label">虚拟音条琴</Text>
            <PlayableInstrumentBanner instrument={config.virtual_instrument || "virtual_xylophone"} />
            <div className="xylophone-keyboard" aria-label="虚拟音条琴">
              {plan.allowedSolfege.map((note, index) => (
                <button key={note} type="button" className={`tone-${index}`} onClick={() => placeNote(note)}>
                  <strong>{SOLFEGE_LABELS[note] ?? note}</strong>
                  <span>敲</span>
                </button>
              ))}
            </div>

            <div className="pentatonic-slot-grid" aria-label="五声创编节奏格">
              {plan.slots.map((slot, index) => (
                <div key={slot.id} className={`pentatonic-slot ${placedNotes[index] ? "filled" : ""}`}>
                  <span>{slot.beatIndex}</span>
                  <strong>{placedNotes[index] ? SOLFEGE_LABELS[placedNotes[index]] : "待放音"}</strong>
                  <small>{slot.label}</small>
                </div>
              ))}
            </div>
          </section>

          <aside className="activity-side" aria-label="五声创编确认区">
            <section className={`primary-tool pentatonic-result ${evaluation.status}`}>
              <Text weight="bold">创编检查</Text>
              <p>{evaluation.message}</p>
              <p>规则：只用五声音级，填满节奏格，回放后再确认。</p>
            </section>

            <section className="primary-tool teacher-confirm-card">
              <Flex align="center" gap="2">
                <CheckCircle2 size={20} />
                <Text weight="bold">教师确认</Text>
              </Flex>
              <Text as="p" size="2" color="gray">学生说出用了哪些五声音级和节奏办法后确认。</Text>
              <Button size="4" highContrast disabled={evaluation.status !== "ready"} onClick={confirmCreation}>
                <CheckCircle2 size={18} />
                确认创编
              </Button>
              {confirmed ? <Text weight="bold" color="green">创编完成，可以小组接龙改编。</Text> : null}
            </section>

            <section className="primary-tool pentatonic-record-panel">
              <Text weight="bold">创编记录</Text>
              <div className="pentatonic-record-grid">
                <span>音级：{creationSummary.noteSequence || "待创编"}</span>
                <span>节奏：{creationSummary.rhythmSequence}</span>
                <span>修改：{creationSummary.revisionCount} 次</span>
                <span>回放：{creationSummary.auditionCount} 次</span>
              </div>
              <p>{creationSummary.teacherNextStep}</p>
              <ReadableData value={creationExport} />
            </section>

            <section className="primary-tool classroom-prompts">
              <Text weight="bold">教师提示</Text>
              <p>没有实体音条琴时，用这组虚拟音条替代；仍要让学生听、改、说。</p>
              <p>如果短句太平，可以让学生尝试上行、下行或结束回到 do/la。</p>
            </section>
          </aside>
        </Grid>
      </Container>
    </main>
  );
}

function PlayableInstrumentBanner({ instrument }: { instrument: string }) {
  const skin = playableInstrumentAssetFor(instrument);
  return (
    <div className={`playable-instrument-banner ${skin.status}`}>
      {skin.url ? <img src={skin.url} alt={`${skin.label}生成乐器皮肤`} /> : <span>待生成/待接入 {skin.label}</span>}
    </div>
  );
}
