import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const viteConfig = readFileSync(join(root, "vite.config.ts"), "utf8");
const reviewEntry = readFileSync(join(root, "music-education-review.html"), "utf8");

assert.doesNotMatch(viteConfig, /127\.0\.0\.1:5191/, "游戏素材不能指向已停用的 5191 服务");
assert.match(viteConfig, /"\/static"\s*:\s*"http:\/\/127\.0\.0\.1:8000"/, "游戏素材统一由正式后端提供");
assert.match(viteConfig, /server:\s*\{\s*port:\s*5176/, "组件总审核台默认使用独立的 5176 端口，不与教师端冲突");
assert.match(reviewEntry, /127\.0\.0\.1:5176\/template-console\/music-education-review\.html/, "从本地文件打开审核台时会跳转到审核库自己的端口");

console.log("vite static asset proxy tests passed");
