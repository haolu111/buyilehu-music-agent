import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const source = readFileSync(join(root, "src/activity/StrongWeakBeatActivity.tsx"), "utf8");

assert.match(source, /听示范/, "the activity starts with a listening stage");
assert.match(source, /网页判断/, "web judgement is a distinct stage");
assert.match(source, /身体律动/, "body movement is a separate transfer stage");
assert.match(source, /现在离开按钮，只做身体动作/, "movement stage disables concurrent web input");
assert.match(source, /count_in/, "a count-in stage exists before student judgement");
assert.match(source, /预备拍/, "the activity tells students when the count-in is playing");
assert.match(source, /const showAccentChoices = stage === "count_in" \|\| stage === "judging"/, "accent choices stay visible during the count-in so students can locate them");
assert.match(source, /disabled=\{stage !== "judging"\}/, "accent choices remain disabled until the target beat begins");
assert.match(source, /<select/, "students can select a meter before the attempt");
assert.match(source, /type="number"/, "students can set the practice BPM before the attempt");
assert.match(source, /再听一次并重练/, "failed judgement has an explicit retry action");
assert.match(source, /handlePracticeSettingChange/, "changing meter or BPM resets the active attempt");
assert.doesNotMatch(source, /请选择身体动作/, "the web must not ask students to choose body actions while performing them");

console.log("strong weak beat activity contract passed");
