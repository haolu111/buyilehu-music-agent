import assert from "node:assert/strict";
import {
  buildReviewItemCopy,
  createReviewPreviewRequestGuard,
  countMismatchCategories,
  defaultActivityTeachingRole,
  filterReviewItems,
  resolveInitialReviewCategory,
  type ReviewCatalogItem,
  type ReviewFilters
} from "../src/activity/musicEducationReviewCatalog";

const items: ReviewCatalogItem[] = [
  {
    id: "rhythm_warmup",
    name: "节奏热身",
    category: "activity",
    implementation_status: "live",
    purpose: "听后拍回节奏",
    music_elements: ["节奏", "稳定拍"],
    student_actions: ["listen", "tap"],
    teacher_focus: ["拍点是否稳定"],
    teaching_role: "core_practice",
    teaching_role_label: "核心音乐实践",
    web_boundary: "网页只提供练习材料和过程记录。",
    teacher_boundary: "教师判断学生实际拍击与表现。",
    agent_default_allowed: true,
    preview_kind: "activity_runtime",
    full_screen_url: "/rhythm",
    technical_details: { grade_bands: ["middle_primary"] }
  },
  {
    id: "audio_upload_compare",
    name: "音频上传与对比播放器",
    category: "component",
    lifecycle_status: "compatibility",
    implementation_status: "preview_ready",
    purpose: "对比听辨",
    music_elements: ["音色"],
    student_actions: ["listen"],
    teacher_focus: ["禁止智能体优先调用"],
    teaching_role: "evidence_capture",
    teaching_role_label: "网页证据采集",
    web_boundary: "网页只记录有限选择证据。",
    teacher_boundary: "教师补充音乐判断。",
    agent_default_allowed: false,
    preview_kind: "component_fixture",
    full_screen_url: "",
    technical_details: {}
  }
];

const defaultFilters: ReviewFilters = {
  search: "",
  gradeBand: "all",
  musicElement: "all",
  implementationStatus: "all",
  runnableOnly: false,
  teachingRole: "all"
};

assert.deepEqual(filterReviewItems(items, defaultFilters), items);
assert.deepEqual(filterReviewItems(items, { ...defaultFilters, search: "拍回" }).map((item) => item.id), ["rhythm_warmup"]);
assert.deepEqual(filterReviewItems(items, { ...defaultFilters, gradeBand: "middle_primary" }).map((item) => item.id), ["rhythm_warmup"]);
assert.deepEqual(filterReviewItems(items, { ...defaultFilters, musicElement: "音色" }).map((item) => item.id), ["audio_upload_compare"]);
assert.deepEqual(filterReviewItems(items, { ...defaultFilters, implementationStatus: "live" }).map((item) => item.id), ["rhythm_warmup"]);
assert.deepEqual(filterReviewItems(items, { ...defaultFilters, runnableOnly: true }).map((item) => item.id), ["rhythm_warmup"]);
assert.deepEqual(filterReviewItems(items, { ...defaultFilters, teachingRole: "core_practice" }).map((item) => item.id), ["rhythm_warmup"]);
assert.deepEqual(filterReviewItems(items, { ...defaultFilters, teachingRole: "evidence_capture" }).map((item) => item.id), ["audio_upload_compare"]);

const legacyActivity: ReviewCatalogItem = {
  ...items[0],
  id: "legacy_activity",
  teaching_role: undefined,
  teaching_role_label: undefined,
  web_boundary: undefined,
  teacher_boundary: undefined,
  agent_default_allowed: undefined
};
assert.equal(defaultActivityTeachingRole(items), "core_practice");
assert.equal(defaultActivityTeachingRole([items[0], legacyActivity]), "all");
assert.deepEqual(filterReviewItems([items[0], legacyActivity], defaultFilters).map((item) => item.id), ["rhythm_warmup", "legacy_activity"]);
assert.equal(resolveInitialReviewCategory(null), "activity", "the review console starts in classroom activities");
assert.equal(resolveInitialReviewCategory("game"), "game", "a valid review category in the URL is preserved");
assert.equal(resolveInitialReviewCategory("not-a-category"), "activity", "an invalid URL category falls back to classroom activities");

const previewRequestGuard = createReviewPreviewRequestGuard();
const slowA = previewRequestGuard.start();
const fastB = previewRequestGuard.start();
const renderedPreviews: string[] = [];
previewRequestGuard.commit(fastB, () => renderedPreviews.push("B"));
previewRequestGuard.commit(slowA, () => renderedPreviews.push("A"));
assert.deepEqual(renderedPreviews, ["B"], "a slow A preview cannot overwrite the later B selection");

assert.deepEqual(
  countMismatchCategories(
    { component: 44, activity: 31, game: 7, teaching_aid: 20, virtual_instrument: 13, material_binder: 9 },
    { component: 44, activity: 32, game: 7, teaching_aid: 20, virtual_instrument: 13, material_binder: 9 }
  ),
  ["activity"]
);

assert.equal(
  buildReviewItemCopy(items[1]),
  "音频上传与对比播放器（audio_upload_compare）\n分类：基础与专业组件\n审核重点：禁止智能体优先调用"
);

console.log("music education review catalog tests passed");
