import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const source = readFileSync(join(root, "src", "activity", "MelodyContourTraceActivity.tsx"), "utf8");

assert.match(source, /onPointerDown/, "学生要能在旋律区开始自由描画");
assert.match(source, /onPointerMove/, "学生要能连续描画自己的旋律线");
assert.doesNotMatch(source, /judgeMelodyContourGesture/, "自由描画不能由预设方向按钮判定正误");
assert.match(source, /教师审核/, "旋律表达是否准确必须保留给教师审核");

console.log("melody contour free-draw view tests passed");
