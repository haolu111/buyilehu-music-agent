import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const reviewSource = readFileSync(join(root, "src/activity/MusicEducationReviewApp.tsx"), "utf8");
const reviewCss = readFileSync(join(root, "src/activity/primaryActivity.css"), "utf8");

assert.match(reviewSource, /\/api\/music-education-review\/catalog/, "the review console reads the formal backend catalog");
assert.match(reviewSource, /\/api\/music-education-review\/previews\//, "each selected item loads its deterministic review preview");
assert.match(reviewSource, /REVIEW_CATEGORIES\.map/, "all six formal categories are rendered from the shared category list");
assert.match(reviewSource, /filterReviewItems/, "catalog cards use the tested search and filter rules");
assert.match(reviewSource, /32[\s\S]*32[\s\S]*7[\s\S]*17[\s\S]*11[\s\S]*9/, "the interface explains the latest formal catalog counts");
assert.match(reviewSource, /\u590d\u5236\u9879\u76ee\u4fe1\u606f|复制项目信息/, "items expose copyable names and ids for requesting source changes");
assert.match(reviewSource, /全屏打开/, "live previews can open their full classroom surface");
assert.match(reviewSource, /打开调用该教具的课堂活动/, "teaching aids open the real classroom activity that uses them");
assert.match(reviewSource, /后台智能体调用器/, "material binders are clearly marked as backend-only rather than fake student pages");
assert.match(reviewSource, /课堂角色/, "the catalog exposes a teaching-role filter");
assert.match(reviewSource, /resolveInitialReviewCategory/, "the review console starts in classroom activities unless a URL category is supplied");
assert.match(reviewSource, /学生主体实践/, "the review panel distinguishes what students actually do");
assert.match(reviewSource, /网页只做什么/, "the review panel exposes the web boundary");
assert.match(reviewSource, /必须由教师判断什么/, "the review panel exposes the teacher boundary");
assert.match(reviewSource, /不能作为课堂主活动/, "evidence activities cannot masquerade as main classroom activities");
assert.match(reviewSource, /待补角色/, "legacy activities without a role remain visible and explicitly marked for completion");
assert.match(reviewSource, /createReviewPreviewRequestGuard/, "the selected preview is protected against out-of-order responses");
assert.doesNotMatch(reviewSource, /function ReviewOnlyActions/, "the review page no longer exposes fake unsaved pass/revise/reject controls");
assert.doesNotMatch(reviewSource, /data-status="pass"/, "fake review status buttons are removed");
assert.doesNotMatch(reviewCss, /\.music-review-mark-buttons/, "unused review-mark controls and their color-only states are removed");
assert.match(reviewCss, /\.music-review-console-layout\s*\{/, "the total review console has a dedicated desktop layout");
assert.match(reviewCss, /@media\s*\(max-width:\s*1100px\)/, "the total review console has a tablet breakpoint");

console.log("music education total review console contract passed");
