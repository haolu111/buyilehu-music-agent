import { Badge, Button, Flex, Grid, Select, Text } from "@radix-ui/themes";
import { CheckCircle2, Mic2, Play, RotateCcw, ShieldCheck, Square, Volume2 } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import type { GradePreset } from "../shared/musicMediaContracts";
import { playHybridToneSequenceAsync } from "../shared/realAudio";
import { vocalSafetyPreset } from "./musicClassroomLogic";
import { MusicClassroomFrame } from "./MusicClassroomFrame";

const stages = ["听示范", "身体与呼吸准备", "发声练习", "乐句练习", "回听与教师反馈"];

export function VocalChoirTraining() {
  const [grade, setGrade] = useState<GradePreset>("middle_primary");
  const [stage, setStage] = useState(0);
  const [recording, setRecording] = useState(false);
  const [recordingUrl, setRecordingUrl] = useState("");
  const [micStatus, setMicStatus] = useState("麦克风只用于本机本节课回听");
  const [teacherChecks, setTeacherChecks] = useState({ natural: false, diction: false, blend: false });
  const recorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const preset = vocalSafetyPreset(grade);

  useEffect(() => () => {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    if (recordingUrl) URL.revokeObjectURL(recordingUrl);
  }, [recordingUrl]);

  const playReference = async () => {
    await playHybridToneSequenceAsync([0, 2, 4, 5, 4, 2, 0], { instrument: "acoustic_grand_piano", baseMidi: preset.comfortableMidi[0], gap: .48, duration: .38, allowOscillatorFallback: false });
  };

  const startRecording = async () => {
    if (!navigator.mediaDevices?.getUserMedia || typeof MediaRecorder === "undefined") { setMicStatus("本设备不支持录音，请由教师现场确认"); return; }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream; chunksRef.current = [];
      const recorder = new MediaRecorder(stream); recorderRef.current = recorder;
      recorder.ondataavailable = (event) => { if (event.data.size) chunksRef.current.push(event.data); };
      recorder.onstop = () => {
        const url = URL.createObjectURL(new Blob(chunksRef.current, { type: recorder.mimeType || "audio/webm" }));
        setRecordingUrl(url); setMicStatus("录音只保存在当前浏览器会话，可立即回听");
        stream.getTracks().forEach((track) => track.stop());
      };
      recorder.start(); setRecording(true); setMicStatus("正在录音：请用自然声音，不喊唱");
    } catch { setMicStatus("麦克风权限未开启，仍可继续教师现场确认"); }
  };
  const stopRecording = () => { recorderRef.current?.stop(); setRecording(false); };
  const allConfirmed = Object.values(teacherChecks).every(Boolean);

  return (
    <MusicClassroomFrame kicker="第一批 · 04" title="合唱与嗓音训练组件" summary="按儿童安全边界完成听、准备、发声、乐句和反馈，不用机器分数替代教师耳朵。" teacherBoundary="音色、气息、共鸣、咬字、声部融合和音乐表现必须由教师判断。">
      <Flex className="vocal-safety-strip" gap="3" align="center" wrap="wrap"><ShieldCheck size={22} /><strong>{preset.cue}</strong><Badge color="amber" variant="soft">舒适音域 MIDI {preset.comfortableMidi[0]}–{preset.comfortableMidi[1]}</Badge><Badge color="teal" variant="soft">连续练习不超过 {preset.continuousMinutes} 分钟</Badge><Select.Root value={grade} onValueChange={(value) => setGrade(value as GradePreset)}><Select.Trigger /><Select.Content><Select.Item value="lower_primary">小学低段</Select.Item><Select.Item value="middle_primary">小学中段</Select.Item><Select.Item value="upper_primary">小学高段</Select.Item></Select.Content></Select.Root></Flex>
      <div className="classroom-stage-path">{stages.map((label, index) => <button key={label} className={index === stage ? "active" : index < stage ? "done" : ""} onClick={() => setStage(index)}><span>{index + 1}</span><strong>{label}</strong></button>)}</div>
      <Grid columns={{ initial: "1", md: "1fr 1fr" }} gap="4">
        <section className="classroom-console-panel vocal-practice-card">
          <Text size="2" color="gray">当前阶段 {stage + 1}/5</Text><strong>{stages[stage]}</strong>
          <p>{stageCue(stage)}</p>
          <Flex gap="2" wrap="wrap"><Button size="3" highContrast onClick={() => void playReference()}><Volume2 size={18} />听钢琴参考</Button>{stage >= 2 ? (!recording ? <Button size="3" variant="soft" onClick={() => void startRecording()}><Mic2 size={18} />本机录音</Button> : <Button size="3" color="ruby" onClick={stopRecording}><Square size={17} />停止录音</Button>) : null}</Flex>
          <div className={`vocal-level-visual ${recording ? "recording" : ""}`} aria-hidden="true">{Array.from({ length: 18 }, (_, index) => <i key={index} style={{ height: `${28 + index % 5 * 11}%` }} />)}</div>
          <Text size="2" color="gray">{micStatus}</Text>
          {recordingUrl ? <audio controls src={recordingUrl} className="classroom-local-recording" /> : null}
          <Flex gap="2"><Button variant="soft" onClick={() => setStage(Math.min(stages.length - 1, stage + 1))}>完成本步，继续</Button><Button variant="soft" color="gray" onClick={() => setStage(0)}><RotateCcw size={16} />重练</Button></Flex>
        </section>
        <section className="classroom-console-panel teacher-vocal-checks">
          <Text weight="bold">教师听辨确认</Text>
          {([['natural', '自然发声，没有喊唱'], ['diction', '歌词与咬字符合课堂要求'], ['blend', '声部能互相聆听并基本融合']] as const).map(([id, label]) => <label key={id}><input type="checkbox" checked={teacherChecks[id]} onChange={(event) => setTeacherChecks((current) => ({ ...current, [id]: event.target.checked }))} /><span>{label}</span></label>)}
          <div className={allConfirmed ? "teacher-pass-card ready" : "teacher-pass-card"}>{allConfirmed ? <CheckCircle2 size={24} /> : <Play size={24} />}<strong>{allConfirmed ? "可以进入合唱展示" : "等待教师完成三项确认"}</strong></div>
        </section>
      </Grid>
    </MusicClassroomFrame>
  );
}

function stageCue(stage: number) {
  return ["先完整聆听乐句和自然音色。", "放松肩颈，安静吸气，避免夸张深吸。", "在舒适音区轻声连唱，不追求大音量。", "按乐句循环，先单声部，再进入轮唱或二声部。", "学生先自评，再由教师给出具体音乐反馈。"][stage];
}
