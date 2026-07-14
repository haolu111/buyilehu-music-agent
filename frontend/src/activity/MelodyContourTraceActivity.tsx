import { Badge, Button, Container, Flex, Grid, Heading, Text } from "@radix-ui/themes";
import { CheckCircle2, MoveUpRight, RotateCcw, Volume2 } from "lucide-react";
import { useMemo, useRef, useState, type PointerEvent } from "react";
import { playPlayableInstrumentSequence } from "../shared/realAudio";
import { buildMelodyContourTracePlan, contourToneOffsets } from "./melodyContourTraceLogic";
import "./primaryActivity.css";

type MelodyContourState = {
  workflow?: {
    education_alignment?: {
      primary_competency?: string;
      music_elements?: string[];
      student_practices?: string[];
    };
  };
  config?: {
    pitch_motion?: string[];
    melody_phrases?: string[];
    bpm?: number;
  };
};

type DrawingPoint = { x: number; y: number };

declare global {
  interface Window {
    __MELODY_CONTOUR_STATE__?: MelodyContourState;
  }
}

const defaultState: MelodyContourState = {
  workflow: {
    education_alignment: {
      primary_competency: "艺术表现",
      music_elements: ["旋律", "音高"],
      student_practices: ["listen", "move", "sing", "explain"]
    }
  },
  config: {
    pitch_motion: ["up", "up", "down", "same"],
    melody_phrases: ["do re mi sol mi"],
    bpm: 86,
  }
};

export function MelodyContourTraceActivity({ state = window.__MELODY_CONTOUR_STATE__ ?? defaultState }: { state?: MelodyContourState }) {
  const config = state.config ?? defaultState.config ?? {};
  const alignment = state.workflow?.education_alignment ?? defaultState.workflow?.education_alignment ?? {};
  const plan = useMemo(() => buildMelodyContourTracePlan({
    pitchMotion: config.pitch_motion,
    melodyPhrases: config.melody_phrases,
    bpm: config.bpm,
  }), [config.bpm, config.melody_phrases, config.pitch_motion]);
  const drawingBoardRef = useRef<SVGSVGElement>(null);
  const [hasListenedMelody, setHasListenedMelody] = useState(false);
  const [drawingPoints, setDrawingPoints] = useState<DrawingPoint[]>([]);
  const [isDrawing, setIsDrawing] = useState(false);
  const drawingStatus = !hasListenedMelody ? "needs_listening" : drawingPoints.length < 2 ? "needs_drawing" : "teacher_review";
  const teacherSuggestion = drawingStatus === "needs_listening"
    ? "先完整听一遍旋律，再在空白画板上画出你听到的高低走向。"
    : drawingStatus === "needs_drawing"
      ? "请用一条连续线画出刚才听到的旋律走向；没有唯一标准线。"
      : "网页已记录学生的描画轨迹。请教师结合再次聆听、学生说明和唱回，判断高低走向是否表达准确。";
  const record = {
    version: "melody_contour_free_draw_record_v2",
    melodyPhrases: plan.melodyPhrases,
    listenedBeforeDrawing: hasListenedMelody,
    drawingPointCount: drawingPoints.length,
    drawingPoints,
    awaitingTeacherReview: drawingStatus === "teacher_review",
    teacherSuggestion,
  };

  const playMelody = () => {
    setHasListenedMelody(true);
    playPlayableInstrumentSequence(contourToneOffsets(plan), {
      instrument: "xylophone",
      gap: 60 / plan.bpm,
      duration: 0.28,
      gain: 0.56,
      baseMidi: 60,
      oscillatorWave: "triangle"
    });
  };

  const pointFromEvent = (event: PointerEvent<SVGSVGElement>): DrawingPoint => {
    const bounds = drawingBoardRef.current?.getBoundingClientRect();
    if (!bounds) return { x: 0, y: 0 };
    return {
      x: clamp(((event.clientX - bounds.left) / bounds.width) * 100),
      y: clamp(((event.clientY - bounds.top) / bounds.height) * 100),
    };
  };

  const handleDrawStart = (event: PointerEvent<SVGSVGElement>) => {
    if (!hasListenedMelody) return;
    event.currentTarget.setPointerCapture(event.pointerId);
    setDrawingPoints([pointFromEvent(event)]);
    setIsDrawing(true);
  };

  const handleDrawMove = (event: PointerEvent<SVGSVGElement>) => {
    if (!isDrawing || !hasListenedMelody) return;
    const point = pointFromEvent(event);
    setDrawingPoints((current) => [...current, point]);
  };

  const finishDrawing = () => setIsDrawing(false);

  const reset = () => {
    setHasListenedMelody(false);
    setDrawingPoints([]);
    setIsDrawing(false);
  };

  return (
    <main className="primary-activity-shell melody-contour-shell">
      <Container size="4" px="4">
        <section className="teacher-control-bar">
          <Flex align="center" justify="between" gap="3" wrap="wrap">
            <Flex align="center" gap="2" wrap="wrap">
              <MoveUpRight size={18} />
              <Text weight="bold">旋律线控制</Text>
              <Badge color={drawingStatus === "teacher_review" ? "green" : "amber"} variant="soft">
                {drawingStatus === "teacher_review" ? "等待教师审核" : "先听旋律"}
              </Badge>
              <Badge color="teal" variant="soft">{plan.bpm} BPM</Badge>
            </Flex>
            <Flex gap="2" wrap="wrap">
              <Button highContrast onClick={playMelody} aria-label="播放旋律">
                <Volume2 size={17} />
                播放旋律
              </Button>
              <Button variant="soft" color="gray" onClick={reset} aria-label="重置旋律线">
                <RotateCcw size={17} />
                重画
              </Button>
            </Flex>
          </Flex>
        </section>

        <Grid columns={{ initial: "1", md: "1.08fr .92fr" }} gap="4" className="activity-stage">
          <section className="activity-board melody-contour-board" aria-label="旋律线描一描活动">
            <Flex align="center" gap="2" wrap="wrap">
              <Badge color="green" variant="soft">{alignment.primary_competency ?? "艺术表现"}</Badge>
              {(alignment.music_elements ?? []).map((element) => <Badge key={element} color="amber" variant="soft">{element}</Badge>)}
            </Flex>
            <Heading as="h1" size="8" className="activity-title">旋律线描一描</Heading>
            <Text as="p" size="3" color="gray" className="activity-subtitle">
              先听旋律短句，再在空白画板上自由画出你听到的高低走向；不提供预设答案线。
            </Text>

            <svg
              ref={drawingBoardRef}
              className={`melody-contour-svg melody-contour-free-draw ${isDrawing ? "drawing" : ""}`}
              viewBox="0 0 100 100"
              role="application"
              aria-label={hasListenedMelody ? "旋律自由描画板" : "请先播放旋律后再描画"}
              onPointerDown={handleDrawStart}
              onPointerMove={handleDrawMove}
              onPointerUp={finishDrawing}
              onPointerCancel={finishDrawing}
            >
              <line x1="8" y1="18" x2="92" y2="18" className="melody-contour-guide" />
              <line x1="8" y1="50" x2="92" y2="50" className="melody-contour-guide" />
              <line x1="8" y1="82" x2="92" y2="82" className="melody-contour-guide" />
              <text x="5" y="19">高</text>
              <text x="5" y="51">中</text>
              <text x="5" y="83">低</text>
              {drawingPoints.length > 1 ? <polyline points={drawingPoints.map((point) => `${point.x},${point.y}`).join(" ")} fill="none" stroke="#176a5b" strokeWidth="3.6" strokeLinecap="round" strokeLinejoin="round" /> : null}
              {!hasListenedMelody ? <text x="50" y="50" className="melody-contour-placeholder">先听旋律，再开始画</text> : null}
            </svg>

            <section className="primary-tool melody-phrase-card">
              <Text weight="bold">当前旋律短句</Text>
              <strong>{plan.melodyPhrases[0]}</strong>
            </section>
          </section>

          <aside className="activity-side" aria-label="旋律线操作区">
            <section className="primary-tool melody-gesture-panel">
              <Flex align="center" gap="2">
                <MoveUpRight size={20} />
                <Text weight="bold">学生自由描画</Text>
              </Flex>
              <p>{hasListenedMelody ? "请根据自己听到的旋律走向自由画线。网页不会把任何预设线当作标准答案。" : "点击“播放旋律”后，画板才会开始记录学生的自由描画。"}</p>
            </section>

            <section className={`primary-tool melody-contour-feedback ${drawingStatus}`}>
              <Flex align="center" gap="2">
                <CheckCircle2 size={20} />
                <Text weight="bold">教师审核</Text>
              </Flex>
              <p>{teacherSuggestion}</p>
              <div className="melody-contour-summary-grid">
                <span>已听旋律</span>
                <strong>{hasListenedMelody ? "是" : "否"}</strong>
                <span>描画点</span>
                <strong>{drawingPoints.length}</strong>
                <span>网页结论</span>
                <strong>不自动判定</strong>
              </div>
            </section>

            <section className="primary-tool melody-contour-record">
              <Text weight="bold">旋律线记录</Text>
              <pre aria-label="旋律线记录导出 JSON">{JSON.stringify(record, null, 2)}</pre>
            </section>
          </aside>
        </Grid>
      </Container>
    </main>
  );
}

function clamp(value: number) {
  return Math.max(0, Math.min(100, Math.round(value * 10) / 10));
}
