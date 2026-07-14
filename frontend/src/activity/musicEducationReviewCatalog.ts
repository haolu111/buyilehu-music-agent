export type ReviewCategory =
  | "component"
  | "activity"
  | "game"
  | "teaching_aid"
  | "virtual_instrument"
  | "material_binder";

export type ReviewCatalogItem = {
  id: string;
  name: string;
  category: ReviewCategory;
  lifecycle_status?: "official" | "compatibility" | "deprecated";
  implementation_status: "live" | "preview_ready" | "contract_only";
  purpose: string;
  music_elements: string[];
  student_actions: string[];
  teacher_focus: string[];
  teaching_role?: string;
  teaching_role_label?: string;
  web_boundary?: string;
  teacher_boundary?: string;
  agent_default_allowed?: boolean;
  preview_kind: string;
  full_screen_url: string;
  technical_details: Record<string, unknown>;
};

export type ReviewCatalog = {
  version: "music_education_review_catalog_v1";
  actual_counts: Record<ReviewCategory, number>;
  expected_counts: Record<ReviewCategory, number>;
  count_status: "pass" | "fail";
  activity_quality_report: ReviewQualityReport;
  game_quality_report: ReviewQualityReport;
  categories: Record<ReviewCategory, ReviewCatalogItem[]>;
};

export type ReviewQualityReport = {
  status: "pass" | "fail";
  blocking_failures?: Array<Record<string, unknown>>;
};

export type ReviewPreview = {
  version: "music_education_review_preview_v1";
  category: ReviewCategory;
  item_id: string;
  name: string;
  preview_kind: string;
  implementation_status: ReviewCatalogItem["implementation_status"];
  audit_example: true;
  example_label: string;
  full_screen_url: string;
  professional_summary: {
    purpose: string;
    music_elements: string[];
    student_actions: string[];
    teacher_focus: string[];
  };
  technical_details: Record<string, unknown>;
  flow?: Array<{ id: string; label: string; description: string }>;
  resettable?: boolean;
  fixture?: Record<string, unknown>;
  classroom_preview?: { replaces: string; components: string[] };
  audio_preview?: {
    audited: boolean;
    source: string;
    license: string;
    attribution: string;
    requires_combined_audio: boolean;
  };
  binding_example?: {
    source: Record<string, unknown>;
    structured_result: Record<string, unknown>;
    component_targets: string[];
  };
};

export type ReviewFilters = {
  search: string;
  gradeBand: string;
  musicElement: string;
  implementationStatus: "all" | ReviewCatalogItem["implementation_status"];
  runnableOnly: boolean;
  teachingRole: "all" | string;
};

export const REVIEW_CATEGORY_LABELS: Record<ReviewCategory, string> = {
  component: "基础与专业组件",
  activity: "课堂活动",
  game: "完整游戏模板",
  teaching_aid: "虚拟教具",
  virtual_instrument: "虚拟乐器",
  material_binder: "音乐材料绑定器"
};

export const REVIEW_CATEGORIES = Object.keys(REVIEW_CATEGORY_LABELS) as ReviewCategory[];

export function resolveInitialReviewCategory(requestedCategory: string | null): ReviewCategory {
  return requestedCategory && REVIEW_CATEGORIES.includes(requestedCategory as ReviewCategory)
    ? requestedCategory as ReviewCategory
    : "activity";
}

export function filterReviewItems(items: ReviewCatalogItem[], filters: ReviewFilters) {
  const query = filters.search.trim().toLocaleLowerCase();
  return items.filter((item) => {
    if (filters.runnableOnly && item.implementation_status !== "live") return false;
    if (filters.implementationStatus !== "all" && item.implementation_status !== filters.implementationStatus) return false;
    if (filters.teachingRole !== "all" && item.teaching_role !== filters.teachingRole) return false;
    if (filters.musicElement !== "all" && !item.music_elements.includes(filters.musicElement)) return false;
    const gradeBands = stringArray(item.technical_details.grade_bands);
    if (filters.gradeBand !== "all" && !gradeBands.includes(filters.gradeBand)) return false;
    if (!query) return true;
    const haystack = [
      item.id,
      item.name,
      item.purpose,
      ...item.music_elements,
      ...item.student_actions,
      ...item.teacher_focus,
      item.teaching_role,
      item.teaching_role_label,
      item.web_boundary,
      item.teacher_boundary
    ].join(" ").toLocaleLowerCase();
    return haystack.includes(query);
  });
}

export function defaultActivityTeachingRole(items: ReviewCatalogItem[]) {
  return items.length > 0 && items.every((item) => Boolean(item.teaching_role)) ? "core_practice" : "all";
}

export function createReviewPreviewRequestGuard() {
  let latestRequestId = 0;
  return {
    start() {
      latestRequestId += 1;
      return latestRequestId;
    },
    isCurrent(requestId: number) {
      return requestId === latestRequestId;
    },
    commit(requestId: number, apply: () => void) {
      if (requestId !== latestRequestId) return false;
      apply();
      return true;
    }
  };
}

export function countMismatchCategories(
  actual: Record<ReviewCategory, number>,
  expected: Record<ReviewCategory, number>
) {
  return REVIEW_CATEGORIES.filter((category) => actual[category] !== expected[category]);
}

export function buildReviewItemCopy(item: ReviewCatalogItem) {
  return `${item.name}（${item.id}）\n分类：${REVIEW_CATEGORY_LABELS[item.category]}\n审核重点：${item.teacher_focus.join("；") || "请检查课堂用途和音乐专业性"}`;
}

export function collectMusicElements(catalog: ReviewCatalog | null) {
  if (!catalog) return [];
  return Array.from(new Set(REVIEW_CATEGORIES.flatMap((category) => catalog.categories[category].flatMap((item) => item.music_elements))))
    .filter(Boolean)
    .sort((left, right) => left.localeCompare(right, "zh-CN"));
}

export function stringArray(value: unknown): string[] {
  return Array.isArray(value) ? value.map(String).filter(Boolean) : [];
}
