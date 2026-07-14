# Vue 3 虚拟乐器组件交付包

此目录是交给前端工程师的正式 Vue 3 + TypeScript 组件包。组件本身不依赖 React；音频、触控、录制和 MIDI 均位于框架无关的 `core/`。

## 教师限定任务：供智能体调用的客观证据能力

智能体负责把教师教案、歌曲材料和课堂要求解析成一条**已确定的结构化任务**；本组件库只接收该任务和学生已经发生的演奏事件，返回客观证据。它不提供教师配置界面，也不负责推断教师教案的意图。

### 输入：已解析任务

```ts
import {
  evaluateInstrumentTask,
  type TeacherConstrainedInstrumentTask,
  type InstrumentPerformanceEvent,
} from "@music-education/virtual-instruments-vue/core/teacherConstrainedInstrumentTask";

const task: TeacherConstrainedInstrumentTask = {
  version: "teacher_constrained_instrument_task_v1",
  id: "grade-3-steady-beat-01",
  kind: "steady_beat",
  instrumentId: "virtual_snare_drum",
  gradePreset: "middle_primary",
  bpm: 100,
  targetEvents: [
    { id: "beat-1", offsetBeats: 0, zoneId: "center" },
    { id: "beat-2", offsetBeats: 1, zoneId: "center" },
  ],
};
```

定时类任务的 `targetEvents` 必须给出相对起点的 `offsetBeats`，以及 `zoneId` 或 `midi`（也可同时给出）。`gradePreset` 在运行时也会校验，且只能是 `lower_primary`、`middle_primary` 或 `upper_primary`。受限创编使用 `compositionRules`，只包含智能体已从教师要求中确定的客观限制：`allowedZoneIds`、`allowedMidi`、`requiredEventCount`、`endingMidi`、`requiredBeats`、`restWindowsBeats` 和可选的 `requiredRestCount`。

`restWindowsBeats` 仅用于 `constrained_composition`，每项是 `[startBeat, endBeat)`：从起始拍开始包含、到结束拍之前结束。学生事件落入该窗口，会产生 `rest_window_played:<index>` 违规、`restErrorCount`，以及一项带原始输入位置的 `rest_error` 事件结果。若同时提供 `requiredRestCount`，其 `{ min, max }` 必须包含已声明的休止窗口数量；未声明 `restWindowsBeats` 时不会猜测休止，也不会把 `requiredRestCount` 当成音乐性判断。

支持的六类任务如下：

| `kind` | 组件库能提供的客观证据 |
| --- | --- |
| `free_play` | 仅记录参与次数；不会自动判定对错。 |
| `steady_beat` | 按已给拍点进行一对一时间匹配。 |
| `rhythm_echo` | 按教师/智能体已确认的节奏音头进行一对一时间匹配。 |
| `melody_sequence` | 按给定 MIDI 或演奏区域及时间顺序进行一对一匹配。 |
| `ensemble_cue` | 按已给出的合奏进入提示、区域或 MIDI 与时间进行匹配。 |
| `constrained_composition` | 仅检查智能体传入的音、区域、数量、结束音与时长限制。 |

### 输入：学生演奏事件

事件来自虚拟乐器的实际触控、鼠标、键盘或 MIDI 输入；`timeMs` 是相对于本轮任务开始的有限、非负毫秒数，任何提供的 MIDI 也必须是有限数值。无需、也不应把教师评价写入事件中。

```ts
const performanceEvents: InstrumentPerformanceEvent[] = [
  { timeMs: 0, zoneId: "center", midi: 60 },
  { timeMs: 602, zoneId: "center", midi: 60 },
];
```

### 输出：客观证据，而非最终课堂结论

```ts
const evidence = evaluateInstrumentTask(task, performanceEvents);
// evidence.evidenceStatus: "evidence_pass" | "adjust" | "participation_only"
```

返回内容包括正确、偏早、偏晚、多拍、漏拍、休止误奏数量，参与次数、已匹配目标数、漏拍目标 ID、逐事件结果，以及受限创编的违规 ID（例如 `midi_not_allowed:61` 或 `rest_window_played:0`）。事件会按时间判定，但 `eventIndex` 始终指向学生提交数组中的原始位置，便于回放追溯。`evidence_pass` 只表示这条结构化任务的客观条件已满足；`adjust` 表示需要根据客观证据调整；`participation_only` 表示自由探索仅记录参与。稳定度不是此纯判定器的证据字段；需要时由课堂活动层基于已记录敲击另行计算。

教师必须保留对音乐表现、演奏技术、合奏平衡，以及创编作品质量与创作理由的专业判断。这些内容不能由本组件库自动判定，也不能由 `evidence_pass` 替代。

## 入口

```ts
import {
  VirtualInstrumentPlayer,
  type VirtualInstrumentPlayerProps,
} from "@music-education/virtual-instruments-vue";
```

```vue
<VirtualInstrumentPlayer
  instrument-id="virtual_piano"
  :register-start-midi="60"
  label-mode="number"
  :default-velocity="96"
  :show-controls="true"
  @ready="engine => console.log(engine)"
  @recordingstopped="recording => save(recording)"
/>
```

## Props

- `instrumentId`：十件正式乐器之一。
- `disabled`：禁用所有触控。
- `defaultVelocity`：无可靠压感时的力度，默认 96。
- `autoInitialize`：是否自动尝试启用声音；移动端建议保持 `false`，由用户点击按钮启动音频。
- `showControls`：显示录制、回放和 MIDI 导出。
- `reviewMode`：显示当前引擎、后备原因等审核证据。
- `layoutMode`：音条乐器的 `diatonic / chromatic / pentatonic` 教学模式。
- `registerStartMidi`：当前一屏音区；钢琴横屏两组、竖屏一组，音条乐器一组。
- `labelMode`：隐藏、音名、唱名、数字简谱或双标记。
- `tonicMidi`：唱名和数字简谱的可移动主音。
- `rollEnabled`：音条乐器长按滚奏开关；普通模式始终单次敲击。

## 专业演奏面板

- `PianoSurface`：真实黑白键比例、多指和弦、滑奏、压感和 CC64 延音。
- `MalletSurface`：木琴、马林巴、钟琴共享布局，保持各自音域、材质与音色。
- `PercussionGrid`：教师选择 2–6 件已审核打击乐和主奏法，学生同屏合奏。

```vue
<PercussionGrid :tiles="[
  { id: 'drum', instrumentId: 'virtual_frame_drum', zoneId: 'center', colorToken: 'clay' },
  { id: 'shaker', instrumentId: 'virtual_shaker', zoneId: 'short', colorToken: 'sage' },
]" />
```

## 对外方法

通过 Vue `ref` 可调用：

- `initialize()`
- `startRecording()`
- `stopRecording()`
- `replay(recording?)`
- `stopAll()`
- `exportMidi(recording?)`
- `getActiveEngine()`

## 音频策略

1. 优先使用 SpessaSynth AudioWorklet 和对应乐器的独立 SF3 包。
2. AudioWorklet、AudioContext 或 SoundFont 解码不可用时，自动切换本地真实采样后备映射。
3. 不使用振荡器、三角波或近似乐器替代。
4. 所有资源均从 `/runtime-assets/virtual-instruments/` 离线加载。

## 录制合同

- 保存演奏事件，不录制 WAV。
- 记录 note-on、note-off、力度、触控区、相对时间及钢琴延音 CC64。
- 最长 5 分钟。
- IndexedDB 本机保存。
- 支持原时序回放和标准 MIDI 文件导出。

## 工程接入清单

- 将 `contracts/music/virtual-instrument-catalog.v2.json` 与 `instrument-audio-license-manifest.v1.json` 纳入后端合同发布。
- 发布 `app/static/assets/virtual-instruments/` 下的 `audio/`、`skins/` 和授权说明。
- 将 `spessasynth_processor.min.js` 作为同源静态资源发布；Vite 当前会自动复制该文件。
- 保持 `Vue >= 3.5` 和 `spessasynth_lib 4.3.x`。
- 正式开放某件乐器前，由音乐教师在审核流程中人工确认其音乐性、可用性与课堂适配性，并将修改要求或确认结果交接给维护正式注册表的工程人员。当前审核页只用于查看、试听和试玩，不保存“通过 / 修改 / 拒绝”记录。

独立审核页入口：`/template-console/virtual-instrument-review.html`。
