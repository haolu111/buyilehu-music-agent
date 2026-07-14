import { Badge, Button, Flex, Grid, Select, Text } from "@radix-ui/themes";
import { CheckCircle2, RotateCcw, Volume2 } from "lucide-react";
import { useMemo, useState } from "react";
import { playHybridToneSequenceAsync } from "../shared/realAudio";
import { buildEarTrainingRounds, type EarTrainingQuestionType } from "./musicClassroomLogic";
import { MusicClassroomFrame } from "./MusicClassroomFrame";

const typeLabels: Record<EarTrainingQuestionType, string> = { single_pitch: "单音", interval: "音程", rhythm: "节奏", short_melody: "短旋律", tonal_center: "主音感" };

export function EarTrainingEngine() {
  const [type, setType] = useState<EarTrainingQuestionType>("single_pitch");
  const [index, setIndex] = useState(0);
  const [answer, setAnswer] = useState("");
  const [feedback, setFeedback] = useState("先听题，再作答");
  const [allowRandom, setAllowRandom] = useState(false);
  const rounds = useMemo(() => buildEarTrainingRounds({ questionTypes: [type], allowedMidi: [60, 62, 64, 65, 67, 69, 71], allowRandom, count: 5 }), [allowRandom, type]);
  const round = rounds[index % rounds.length];

  const listen = async () => {
    setFeedback("正在播放真实钢琴音色…");
    const result = await playHybridToneSequenceAsync(round.midi.map((midi) => midi - 60), { instrument: "acoustic_grand_piano", baseMidi: 60, gap: type === "rhythm" ? .32 : .55, duration: .3, allowOscillatorFallback: false });
    setFeedback(result.ok ? "已经听完，请作答" : "真实钢琴音色加载失败，请教师检查声音资源");
  };
  const submit = (choice: string) => { setAnswer(choice); setFeedback(choice === round.answer ? "正确：再用声音唱回或说出依据" : `再听一次：当前选择“${choice}”`); };
  const next = () => { setIndex((value) => (value + 1) % rounds.length); setAnswer(""); setFeedback("先听题，再作答"); };

  return (
    <MusicClassroomFrame kicker="第一批 · 03" title="视唱练耳引擎" summary="教师限定材料和难度后，学生完成听、选、拍、唱回和说明。" teacherBoundary="网页判断选择、键盘和节奏点击；学生真实视唱、模唱及音乐表现由教师确认。">
      <Flex className="classroom-engine-toolbar" gap="3" wrap="wrap" align="end">
        <label className="classroom-field compact"><span>训练类型</span><Select.Root value={type} onValueChange={(value) => { setType(value as EarTrainingQuestionType); setIndex(0); setAnswer(""); }}><Select.Trigger /><Select.Content>{Object.entries(typeLabels).map(([id, label]) => <Select.Item key={id} value={id}>{label}</Select.Item>)}</Select.Content></Select.Root></label>
        <label className="classroom-check"><input type="checkbox" checked={allowRandom} onChange={(event) => setAllowRandom(event.target.checked)} />教师允许在限定音级内随机</label>
        <Badge color="amber" variant="soft">首调唱名 · 可切固定调</Badge>
      </Flex>
      <Grid columns={{ initial: "1", md: ".76fr 1.24fr" }} gap="4">
        <section className="classroom-console-panel ear-question-card">
          <Text size="2" color="gray">第 {index + 1} 题 · {typeLabels[type]}</Text><strong>{round.prompt}</strong>
          <Button size="4" highContrast onClick={() => void listen()}><Volume2 size={21} />听题</Button>
          <div className="ear-feedback" data-correct={answer === round.answer || undefined}>{feedback}</div>
          <Flex gap="2" wrap="wrap"><Button variant="soft" onClick={next}>下一题</Button><Button variant="soft" color="gray" onClick={() => { setIndex(0); setAnswer(""); setFeedback("先听题，再作答"); }}><RotateCcw size={16} />重置</Button></Flex>
        </section>
        <section className="classroom-console-panel">
          <Text weight="bold">学生作答</Text>
          <div className="ear-choice-grid">{round.choices.map((choice) => <button key={choice} type="button" className={answer === choice ? "selected" : ""} onClick={() => submit(choice)}>{answer === choice && choice === round.answer ? <CheckCircle2 size={18} /> : null}<strong>{choice}</strong></button>)}</div>
          <div className="teacher-confirm-strip"><span>唱回／构唱</span><Button size="2" variant="soft">教师确认已完成</Button></div>
        </section>
      </Grid>
    </MusicClassroomFrame>
  );
}
