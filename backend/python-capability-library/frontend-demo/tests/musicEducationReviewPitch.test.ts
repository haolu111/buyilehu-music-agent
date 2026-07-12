import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const reviewSource = readFileSync(join(root, "src/activity/MusicEducationReviewApp.tsx"), "utf8");
const reviewStyles = readFileSync(join(root, "src/activity/primaryActivity.css"), "utf8");

assert.match(reviewSource, /PITCH_REGISTERS\.map/, "审核页应从共享目录渲染三个音组");
assert.match(reviewSource, /REGISTERED_PITCH_DEFINITIONS\.filter/, "每个音组应从共享目录筛选 12 张绝对音高卡");
assert.match(reviewSource, /data-register-id=/, "每个音组应提供稳定的审核分区标识");
assert.match(reviewSource, /十二平均律单音库/, "单音库应作为独立审核分区");
assert.match(reviewSource, /旋律组合示例/, "原有旋律应保留在独立组合示例分区");
assert.match(reviewSource, /pitchIds:/, "旋律组合应引用单音 ID 而非重复半音数组");
assert.match(reviewSource, /sequenceToMidiOffsets/, "旋律播放应从单音 ID 序列派生 MIDI 偏移");
assert.match(reviewSource, /registeredPitchToMidi/, "单音试听应使用注册音高的绝对 MIDI");
assert.match(reviewSource, /function NumberNotationPitchLabel/, "审核页应使用结构化简谱音高标签");
assert.match(reviewSource, /octaveMark === ["']upper_dot["'] \? ["']top["']/, "小字二组简谱应映射为上加点");
assert.match(reviewSource, /octaveMark === ["']lower_dot["'] \? ["']bottom["']/, "小字组简谱应映射为下加点");
assert.match(reviewSource, /pitch-octave-dot-\$\{dotPosition\}/, "简谱点应作为独立元素附着到数字");
assert.match(reviewStyles, /\.pitch-octave-dot-top/, "样式应将高音点定位在数字上方");
assert.match(reviewStyles, /\.pitch-octave-dot-bottom/, "样式应将低音点定位在数字下方");

const melodyPlaybackSection = reviewSource.match(/async function playPitchPreview[\s\S]*?\n}\n/)?.[0] || "";
assert.match(melodyPlaybackSection, /playHybridToneSequenceAsync/, "单音和旋律应使用真实采样播放通道");
assert.match(melodyPlaybackSection, /instrument:\s*["']acoustic_grand_piano["']/, "旋律审核默认使用真实钢琴");
assert.match(melodyPlaybackSection, /allowOscillatorFallback:\s*false/, "旋律审核不得回退为振荡器音色");
assert.doesNotMatch(reviewSource, /function playReviewToneSequence/, "审核页不应保留旋律振荡器播放器");

const registeredPitchPlaybackSection = reviewSource.match(/async function playRegisteredPitchPreview[\s\S]*?\n}\n/)?.[0] || "";
assert.match(registeredPitchPlaybackSection, /baseMidi:\s*0/, "绝对 MIDI 试听应以 0 为播放基准");
assert.match(registeredPitchPlaybackSection, /allowOscillatorFallback:\s*false/, "绝对音高试听不得回退为振荡器音色");
