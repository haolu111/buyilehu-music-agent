import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const source = readFileSync(join(root, "src/activity/PrimaryActivityLibraryApp.tsx"), "utf8");

assert.match(source, /image_generation: "none" \| "optional_image_gen" \| "requires_image_gen" \| string;/);
assert.match(source, /image_generation: "optional_image_gen"/);
assert.match(source, /image_generation: "requires_image_gen"/);
assert.doesNotMatch(source, /optional_doubao|requires_doubao/);

assert.match(source, /source_kind: "image_gen_generated"/);
assert.match(source, /status: "ready_from_manifest"/);
assert.match(source, /provider: "image_gen"/);
assert.match(source, /生成 PNG 文件验收通过/);
assert.doesNotMatch(source, /source_kind: "doubao_generated"/);
assert.doesNotMatch(source, /豆包 PNG 文件验收通过|豆包 PNG 待验收|豆包待生成|打开豆包/);

assert.match(source, /外部生图兼容队列|历史生图任务/);
assert.match(source, /当前没有外部生图任务；场景图由智能体按教案临时生成/);
