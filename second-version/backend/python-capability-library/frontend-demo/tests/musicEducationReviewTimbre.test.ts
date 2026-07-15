import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const reviewSource = readFileSync(join(root, "src/activity/MusicEducationReviewApp.tsx"), "utf8");

assert.match(reviewSource, /EXACT_TIMBRE_DEFINITIONS\.map/, "审核页应从共享目录渲染 12 件真实采样乐器");
assert.match(reviewSource, /CC BY 3\.0/, "审核页应显示商业使用所需的授权信息");
assert.match(reviewSource, /baseMidi:\s*item\.preview\.baseMidi/, "每件乐器应使用自己的代表音域");
assert.match(reviewSource, /allowOscillatorFallback:\s*false/, "音色审核不得回退为振荡器");
assert.doesNotMatch(reviewSource, /const timbreItems:/, "审核页不应继续硬编码音色目录");
assert.doesNotMatch(reviewSource, /PENDING_EXACT_TIMBRE_DEFINITIONS/, "专业审核页不得再加载近似音色目录");
assert.doesNotMatch(reviewSource, /待补对应实录/, "专业审核页不得显示待补实录区");
