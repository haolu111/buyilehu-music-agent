import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { formalRhythmName } from "../src/activity/rhythmNaming";

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const notationSource = readFileSync(join(root, "src/music-components/RhythmNotation.tsx"), "utf8");
assert.equal(notationSource.includes('rhythm === "syncopation" ? <path className="rhythm-note-tie"'), false, "小切分不应显示连音线或三连音式弧线");
assert.equal(notationSource.includes("rhythm-note-beamlet left"), true, "小切分首个十六分音符应有左侧副符杠");
assert.equal(notationSource.includes("rhythm-note-beamlet right"), true, "小切分末个十六分音符应有右侧副符杠");

assert.equal(formalRhythmName("eighth_triplet"), "八分音符三连音", "三连音应有正式名称");
assert.equal(notationSource.includes("rhythm-triplet-number"), true, "八分音符三连音谱形应显示数字 3");

assert.equal(formalRhythmName("eighth_rest"), "八分休止符", "八分休止符应有独立正式名称");
assert.match(
  notationSource,
  /rhythm === ["']eighth_rest["'][\s\S]*?<path[\s\S]*?className=["']rhythm-notation-eighth-rest["']/,
  "八分休止符应使用内联 SVG 谱形"
);
assert.equal(notationSource.includes("𝄾"), false, "八分休止符不应依赖系统字体渲染 Unicode 字符");

const reviewSource = readFileSync(join(root, "src/activity/MusicEducationReviewApp.tsx"), "utf8");
const rhythmPlaybackSection = reviewSource.match(/function playRhythm[\s\S]*?\n}\n/)?.[0] || "";
assert.match(rhythmPlaybackSection, /playHybridToneSequenceAsync/, "节奏试听应使用真实采样播放通道");
assert.match(rhythmPlaybackSection, /instrument:\s*["']acoustic_grand_piano["']/, "节奏试听默认使用钢琴音色");
assert.match(rhythmPlaybackSection, /allowOscillatorFallback:\s*false/, "节奏试听不能回退为振荡器音色");

assert.match(reviewSource, /id:\s*["']eighth_triplet["']/, "审核库应包含八分音符三连音");
assert.match(reviewSource, /id:\s*["']eighth_rest["']/, "审核库应包含八分休止符");
assert.match(reviewSource, /id:\s*["']syncopation["'][\s\S]*?start:\s*0\.25[\s\S]*?start:\s*0\.75/, "小切分试听应按十六-八-十六的 0、1/4、3/4 拍点播放");
assert.match(reviewSource, /id:\s*["']eighth_triplet["'][\s\S]*?start:\s*1\s*\/\s*3[\s\S]*?start:\s*2\s*\/\s*3/, "三连音试听应将一拍平均分成三份");
