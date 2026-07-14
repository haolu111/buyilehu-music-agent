const moduleCards = Array.from(document.querySelectorAll(".module-card"));
const modeTabs = Array.from(document.querySelectorAll(".mode-tab"));
const appNavButtons = Array.from(document.querySelectorAll(".app-nav-button"));
const appOpenButtons = Array.from(document.querySelectorAll("[data-open-page]"));
const appPages = {
  home: document.querySelector("#home-page"),
  lesson: document.querySelector("#lesson-page"),
  direct: document.querySelector("#direct-page"),
  library: document.querySelector("#library-page"),
};
const lessonPage = document.querySelector("#lesson-page");
const directPage = document.querySelector("#direct-page");
const workPageTitle = document.querySelector("#work-page-title");
const workPageSubtitle = document.querySelector("#work-page-subtitle");
const modePanels = {
  direct: document.querySelector("#direct-mode-panel"),
  lesson: document.querySelector("#lesson-mode-panel"),
};
const needInput = document.querySelector("#need-input");
const generateForm = document.querySelector("#generate-form");
const directResultGuide = document.querySelector("#direct-result-guide");
const directResultGuideKicker = document.querySelector(".direct-result-guide-kicker");
const directResultGuideTitle = document.querySelector("#direct-result-guide-title");
const directResultGuideMessage = document.querySelector("#direct-result-guide-message");
const directResultPreviewLink = document.querySelector("#direct-result-preview-link");
const directResultFocusButton = document.querySelector("#direct-result-focus-button");
const generationStatusPanel = document.querySelector("#generation-status-panel");
const generationStatusPill = document.querySelector(".generation-status-pill");
const timeline = document.querySelector("#timeline");
const jobLog = document.querySelector("#job-log");
const jobLogStatus = document.querySelector("#job-log-status");
const jobLogList = document.querySelector("#job-log-list");
const artifactList = document.querySelector("#artifact-list");
const artifactTemplate = document.querySelector("#artifact-template");
const artifactDetailPanel = document.querySelector("#artifact-detail-panel");
const artifactDetailTemplate = document.querySelector("#artifact-detail-template");
const myTabs = Array.from(document.querySelectorAll("[data-my-view]"));
const myPanels = Array.from(document.querySelectorAll("[data-my-panel]"));
const myAccountEmail = document.querySelector("#my-account-email");
const accountPasswordForm = document.querySelector("#account-password-form");
const accountCodeButton = document.querySelector("#account-code-button");
const accountStatus = document.querySelector("#account-status");
const accountLogoutButton = document.querySelector("#account-logout-button");
const polishButton = document.querySelector("#polish-button");
const polishPanel = document.querySelector("#polish-panel");
const polishedInput = document.querySelector("#polished-input");
const applyPolishButton = document.querySelector("#apply-polish-button");
const closePolishButton = document.querySelector("#close-polish-button");
const chatForm = document.querySelector("#chat-form");
const chatInput = document.querySelector("#chat-input");
const chatMessages = document.querySelector("#chat-messages");
const chatSubmit = document.querySelector("#chat-submit");
const lessonGameForm = document.querySelector("#lesson-game-form");
const lessonText = document.querySelector("#lesson-text");
const lessonFile = document.querySelector("#lesson-file");
const scoreFile = document.querySelector("#score-file");
const audioFile = document.querySelector("#audio-file");
const songMaterialText = document.querySelector("#song-material-text");
const lessonExtra = document.querySelector("#lesson-extra");
const lessonGenerateButton = document.querySelector("#lesson-generate-button");
const directGenerationModeDesc = document.querySelector("#direct-generation-mode-desc");
const directFastModeButton = document.querySelector("#direct-fast-mode-button");
const directStrictModeButton = document.querySelector("#direct-strict-mode-button");
const lessonProposalPanel = document.querySelector("#lesson-proposal-panel");
const lessonProposalTitle = document.querySelector("#lesson-proposal-title");
const lessonMaterialBadge = document.querySelector("#lesson-material-badge");
const lessonScoreReview = document.querySelector("#lesson-score-review");
const lessonScoreReviewTitle = document.querySelector("#lesson-score-review-title");
const lessonScoreReviewMessage = document.querySelector("#lesson-score-review-message");
const lessonScoreReviewText = document.querySelector("#lesson-score-review-text");
const lessonScoreReviewAttempts = document.querySelector("#lesson-score-review-attempts");
const lessonScoreReviewApply = document.querySelector("#lesson-score-review-apply");
const lessonProposalSummary = document.querySelector("#lesson-proposal-summary");
const lessonProposalFlow = document.querySelector("#lesson-proposal-flow");
const lessonProposalChecks = document.querySelector("#lesson-proposal-checks");
const lessonTextMaterialPanel = document.querySelector("#lesson-text-material-panel");
const lessonTextMaterialMessage = document.querySelector("#lesson-text-material-message");
const lessonTextMaterialInput = document.querySelector("#lesson-text-material-input");
const lessonTextMaterialConfirmButton = document.querySelector("#lesson-text-material-confirm-button");
const lessonMaterialBindingPanel = document.querySelector("#lesson-material-binding-panel");
const lessonMaterialBindingStatus = document.querySelector("#lesson-material-binding-status");
const lessonMaterialBindingList = document.querySelector("#lesson-material-binding-list");
const lessonMaterialBindingConfirm = document.querySelector("#lesson-material-binding-confirm");
const lessonUnmatchedEditor = document.querySelector("#lesson-unmatched-editor");
const lessonUnmatchedEditFocus = document.querySelector("#lesson-unmatched-edit-focus");
const lessonUnmatchedEditStage = document.querySelector("#lesson-unmatched-edit-stage");
const lessonUnmatchedEditGameName = document.querySelector("#lesson-unmatched-edit-game-name");
const lessonUnmatchedEditStudentFlow = document.querySelector("#lesson-unmatched-edit-student-flow");
const lessonUnmatchedEditRules = document.querySelector("#lesson-unmatched-edit-rules");
const lessonGenerationModePanel = document.querySelector("#lesson-generation-mode-panel");
const lessonGenerationModeDesc = document.querySelector("#lesson-generation-mode-desc");
const lessonFastModeButton = document.querySelector("#lesson-fast-mode-button");
const lessonStrictModeButton = document.querySelector("#lesson-strict-mode-button");
const lessonAudioEditor = document.querySelector("#lesson-audio-editor");
const lessonAudioSource = document.querySelector("#lesson-audio-source");
const lessonAudioRows = document.querySelector("#lesson-audio-rows");
const lessonAudioStatus = document.querySelector("#lesson-audio-status");
const lessonAudioAddButton = document.querySelector("#lesson-audio-add-button");
const lessonAudioSaveButton = document.querySelector("#lesson-audio-save-button");
const lessonConfirmButton = document.querySelector("#lesson-confirm-button");
const lessonEditButton = document.querySelector("#lesson-edit-button");
const lessonOpenConfigButton = document.querySelector("#lesson-open-config-button");
const lessonUnmatchedConfirmButton = document.querySelector("#lesson-unmatched-confirm-button");
const lessonConfirmHint = document.querySelector("#lesson-confirm-hint");
const lessonConfigModal = document.querySelector("#lesson-config-modal");
const lessonConfigCloseButtons = Array.from(document.querySelectorAll("[data-lesson-config-close]"));
const runtimeBadge = document.querySelector("#runtime-badge");
const authShell = document.querySelector("#auth-shell");
const studioShell = document.querySelector("#studio-shell");
const authTabs = Array.from(document.querySelectorAll("[data-auth-tab]"));
const authForms = Array.from(document.querySelectorAll("[data-auth-form]"));
const authStatus = document.querySelector("#auth-status");
const loginForm = document.querySelector("#login-form");
const registerForm = document.querySelector("#register-form");
const forgotForm = document.querySelector("#forgot-form");
const registerCodeButton = document.querySelector("#register-code-button");
const forgotCodeButton = document.querySelector("#forgot-code-button");
const accountEmail = document.querySelector("#account-email");
const logoutButton = document.querySelector("#logout-button");

const modulePrefixes = {
  listening: "生成一个聆听编辑页：",
  performance: "生成一个表现关卡页：",
  creation: "生成一个创造拼图页：",
  music_game: "生成一个音乐小游戏：",
};

const activityLabels = {
  listening: "聆听工具",
  performance: "表现闯关",
  creation: "创造拼图",
  music_game: "音乐小游戏",
};

const modulePlaceholders = {
  listening: "例如：为二年级《小雨沙沙》生成一个聆听活动：内置三种声音材料“沙锤雨声、木鱼短声、小鼓重声”，学生点击试听后比较音色，选择最像雨声的一项，并从“轻、密、柔和、短促、厚重”中选择两个证据词；答对条件是选“沙锤雨声”且证据包含“轻、密”或“柔和”，最后说出理由。",
  performance: "例如：为一年级二拍子歌曲《闪烁的小星》生成一个三关表现闯关游戏：第一关听 4 小节音乐并点击每小节第 1 拍，第二关按强拍拍手、弱拍拍腿完成节奏，第三关跟随提示完整唱回一句；每关连续命中 4 次通过，失败可重试。",
  creation: "例如：为四年级五声音阶创编课生成一个旋律创造活动：素材固定为 do、re、mi、sol、la 和四分音符、八分音符、二分音符节奏卡；学生拖拽素材拼成 4 小节旋律，规则是每小节 4 拍、结尾落在 do 或 la，点击试听后可调整，满足规则即通关并说明创编理由。",
  music_game: "例如：为三年级旋律乐句结构课生成一个可玩的结构排列小游戏：内置三段旋律 A“do re mi sol”、B“mi sol la sol”、A 再现“do re mi sol”；学生点击试听三段，判断重复与对比，通过拖拽把结构卡排列成 A-B-A；排列正确后通关，并说出哪两段旋律相同、哪一段形成对比。",
};

let selectedModule = "listening";
let directGenerationMode = "fast";
let lessonGenerationMode = "fast";
let lessonGenerationModeRecommendation = null;
let activeLessonProposal = null;
let activeLessonProposalDefaults = {
  core_focus: "",
  stage: "",
  game_name: "",
  student_flow: [],
  rules: [],
};
const activeTemplateConfigs = {
  lesson: null,
  direct: null,
};
let activeLessonRecommendation = null;
let activeMaterialBindingPlan = null;
let activeTextMaterialDraft = null;
let lessonAudioPreviewTimer = null;
let inspirationChatSessionId = "";
let currentUser = null;
const artifactRevisionSessions = new Map();
const artifactCardsById = new Map();
let activeArtifactDetail = null;
const UPGRADE_FOCUS_ITEMS = ["真实音色", "音乐证据", "学习闭环", "课堂迁移", "移动端", "验收阻断项"];
const REVISION_PROGRESS_FALLBACKS = [
  "正在读取当前作品",
  "正在理解修改要求",
  "正在更新当前游戏",
  "正在同步试玩版本",
  "修改已保存",
];

initializeAuth();
loadRuntimeIdentity();
bindTemplateConfigBridge();

authTabs.forEach((button) => {
  button.addEventListener("click", () => {
    setAuthView(button.dataset.authTab || "login");
  });
});

loginForm?.addEventListener("submit", async (event) => {
  event.preventDefault();
  await submitAuthForm("/api/auth/login", {
    email: valueOf("#login-email"),
    password: valueOf("#login-password"),
  });
});

registerCodeButton?.addEventListener("click", async () => {
  await requestAuthCode(registerCodeButton, "/api/auth/register/request-code", valueOf("#register-email"));
});

registerForm?.addEventListener("submit", async (event) => {
  event.preventDefault();
  await submitAuthForm("/api/auth/register/complete", {
    email: valueOf("#register-email"),
    code: valueOf("#register-code"),
    password: valueOf("#register-password"),
    confirm_password: valueOf("#register-confirm-password"),
  });
});

forgotCodeButton?.addEventListener("click", async () => {
  await requestAuthCode(forgotCodeButton, "/api/auth/password/request-reset", valueOf("#forgot-email"));
});

forgotForm?.addEventListener("submit", async (event) => {
  event.preventDefault();
  await submitAuthForm("/api/auth/password/reset", {
    email: valueOf("#forgot-email"),
    code: valueOf("#forgot-code"),
    password: valueOf("#forgot-password"),
    confirm_password: valueOf("#forgot-confirm-password"),
  });
});

logoutButton?.addEventListener("click", async () => {
  await logoutCurrentUser(logoutButton);
});

accountLogoutButton?.addEventListener("click", async () => {
  await logoutCurrentUser(accountLogoutButton);
});

myTabs.forEach((button) => {
  button.addEventListener("click", () => {
    setMyView(button.dataset.myView || "works");
  });
});

accountCodeButton?.addEventListener("click", async () => {
  if (!currentUser?.email) {
    setAccountStatus("当前账号信息未加载，请刷新后再试。", "error");
    return;
  }
  accountCodeButton.disabled = true;
  const originalText = accountCodeButton.textContent;
  accountCodeButton.textContent = "发送中";
  try {
    await postForm("/api/auth/password/request-reset", { email: currentUser.email });
    setAccountStatus("验证码已发送，请查看邮箱。", "success");
  } catch (error) {
    setAccountStatus(error.message || "验证码发送失败。", "error");
  } finally {
    accountCodeButton.disabled = false;
    accountCodeButton.textContent = originalText;
  }
});

accountPasswordForm?.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!currentUser?.email) {
    setAccountStatus("当前账号信息未加载，请刷新后再试。", "error");
    return;
  }
  try {
    const data = await postForm("/api/auth/password/reset", {
      email: currentUser.email,
      code: valueOf("#account-reset-code"),
      password: valueOf("#account-new-password"),
      confirm_password: valueOf("#account-confirm-password"),
    });
    currentUser = data.user || currentUser;
    syncAccountIdentity();
    accountPasswordForm.reset();
    setAccountStatus("密码已修改。", "success");
  } catch (error) {
    setAccountStatus(error.message || "修改密码失败。", "error");
  }
});

appNavButtons.forEach((button) => {
  button.addEventListener("click", () => {
    openAppPage(button.dataset.appPage || "home");
  });
});

appOpenButtons.forEach((button) => {
  button.addEventListener("click", () => {
    openAppPage(button.dataset.openPage || "home");
  });
});

directFastModeButton?.addEventListener("click", () => {
  setDirectGenerationMode("fast");
});

directStrictModeButton?.addEventListener("click", () => {
  setDirectGenerationMode("strict");
});

lessonFastModeButton?.addEventListener("click", () => {
  setLessonGenerationMode("fast");
});

lessonStrictModeButton?.addEventListener("click", () => {
  setLessonGenerationMode("strict");
});

modeTabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    setMainMode(tab.dataset.dialogMode || "lesson");
  });
});

moduleCards.forEach((card) => {
  card.addEventListener("click", () => {
    selectedModule = card.dataset.module;
    moduleCards.forEach((item) => item.classList.toggle("active", item === card));
    updateNeedPlaceholder();
  });
});

updateNeedPlaceholder();
setDirectGenerationMode(directGenerationMode);
setLessonGenerationMode(lessonGenerationMode);

directResultFocusButton?.addEventListener("click", () => {
  if (!activeArtifactDetail) return;
  activeArtifactDetail.scrollIntoView({ behavior: "smooth", block: "start" });
  activeArtifactDetail.querySelector(".revision-chat-input, .revision-input, .preview-link")?.focus();
});

document.querySelectorAll(".prompt-chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    openAppPage("direct");
    setMainMode("direct");
    needInput.value = chip.dataset.prompt;
    hidePolishPanel();
    needInput.focus();
  });
});

polishButton.addEventListener("click", async () => {
  setMainMode("direct");
  const rawNeed = needInput.value.trim();
  if (!rawNeed) {
    setTimeline([["先写目标", "写一句也可以：曲目、年级、活动。", "blocked"]]);
    needInput.focus();
    return;
  }

  polishButton.disabled = true;
  polishButton.textContent = "润色中";
  setTimeline([["润色中", "正在整理为可生成的课堂需求。", "active"]]);

  const result = await polishNeed(rawNeed);
  polishButton.disabled = false;
  polishButton.textContent = "润色想法";

  if (!result) return;
  polishedInput.value = result.polished;
  polishPanel.hidden = false;
  polishedInput.focus();
  setTimeline([["润色完成", "确认后采用，再生成工具。", "done"]]);
});

applyPolishButton.addEventListener("click", () => {
  setMainMode("direct");
  const polished = polishedInput.value.trim();
  if (!polished) return;
  needInput.value = polished;
  hidePolishPanel();
  needInput.focus();
  setTimeline([["已采用", "可继续修改，或直接生成。", "done"]]);
});

closePolishButton.addEventListener("click", () => {
  hidePolishPanel();
  needInput.focus();
});

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = chatInput.value.trim();
  if (!message) return;

  addChatMessage("user", message);
  chatInput.value = "";
  chatSubmit.disabled = true;
  chatSubmit.textContent = "整理中";
  const waitingMessage = addChatMessage("assistant", "正在整理。", false, true);

  const result = await sendChatMessage(message);
  waitingMessage.remove();
  chatSubmit.disabled = false;
  chatSubmit.textContent = "发送";

  if (!result?.reply) {
    addChatMessage("assistant", "没有整理成功。可以换一种说法，或直接写进生成框。");
    return;
  }
  addChatMessage("assistant", result.reply, Boolean(result.suggested_need), false, result.suggested_need);
});

generateForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  setMainMode("direct");
  const rawNeed = needInput.value.trim();
  if (!rawNeed) return;

  const need = normalizeNeed(rawNeed);
  setTimeline([
    ["理解需求", "整理目标和类型。", "active"],
    ["设计活动", "安排任务和互动。", "pending"],
    ["生成工具", "生成可打开页面。", "pending"],
  ]);

  const guidance = await guideNeed(need);
  if (!guidance.ready) {
    setTimeline([["需要补充", guidance.question || "请补充歌曲、素材、关卡或规则。", "blocked"]]);
    return;
  }

  setTimeline([
    ["需求确认", `类型：${guidance.activity_label || activityLabels[selectedModule]}`, "done"],
    ["设计活动", "生成任务和界面。", "active"],
    ["生成工具", "准备预览。", "pending"],
  ]);

  openAppPage("library");
  showDirectResultGuide("running");
  const result = await generateArtifact(guidance.normalized_need || need);
  if (!result) {
    showDirectResultGuide("failed", { message: "生成没有完成，请根据上方状态提示修改需求后再试。" });
    return;
  }

  setTimeline([
    ["需求已确认", result.spec.subtitle, "done"],
    ["活动已设计", `自检 ${result.brain?.self_critique?.score ?? "--"} 分。`, "done"],
    ["工具已生成", "可打开预览。", "done"],
  ]);

  const card = renderArtifact(result, { highlight: true });
  showDirectResultGuide("completed", result);
  focusGeneratedArtifact(card);
});

lessonGameForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  setMainMode("lesson");
  const text = lessonText.value.trim();
  const file = lessonFile.files?.[0];
  if (!text && !file) {
    setTimeline([["需要教案", "请粘贴正文，或上传文件。", "blocked"]]);
    lessonText.focus();
    return;
  }

  selectedModule = "music_game";
  moduleCards.forEach((item) => item.classList.toggle("active", item.dataset.module === "music_game"));
  updateNeedPlaceholder();
  lessonGenerateButton.disabled = true;
  lessonGenerateButton.textContent = "分析中";
  hideLessonProposal();
  setTimeline([
    ["分析教案", "识别目标、环节和音乐要素，随后推荐玩法方案。", "active"],
    ["提出方案", "确认后生成页面。", "pending"],
  ]);

  const result = await analyzeLessonGame(
    text,
    file,
    lessonExtra.value.trim(),
    scoreFile.files?.[0],
    audioFile.files?.[0],
    songMaterialText.value.trim()
  );
  lessonGenerateButton.disabled = false;
  lessonGenerateButton.textContent = "分析教案";
  if (!result) return;

  const analysis = result.lesson_analysis || {};
  activeLessonProposal = result;
  await syncLessonTemplateConfig(result.proposal_id);
  lessonGenerationModeRecommendation = result.generation_mode_recommendation || {
    recommended: "fast",
    reason: "分析结果已经足够清楚，可以先生成可试玩版本。",
    fast_description: "先生成可试玩版本。",
    strict_description: "后续可在作品页继续优化。",
  };
  setLessonGenerationMode("fast");
  renderLessonProposal(result);
  const game = analysis.recommended_game || {};
  setTimeline([
    ["教案已分析", `${analysis.song_name || "课例"}，建议放在${analysis.game_stage || "核心练习环节"}。`, "done"],
    ["确认方案", game.name ? `建议：${game.name}` : "请查看方案。", "active"],
  ]);
});

lessonConfirmButton?.addEventListener("click", async () => {
  await submitLessonGameConfirmation(lessonConfirmButton);
});

lessonUnmatchedConfirmButton?.addEventListener("click", async () => {
  await submitLessonGameConfirmation(lessonUnmatchedConfirmButton);
});

lessonOpenConfigButton?.addEventListener("click", () => {
  openLessonConfigModal();
});

lessonConfigCloseButtons.forEach((button) => {
  button.addEventListener("click", () => closeLessonConfigModal());
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && lessonConfigModal && !lessonConfigModal.hidden) {
    closeLessonConfigModal();
  }
});

lessonEditButton?.addEventListener("click", resetLessonProposalForEditing);

lessonMaterialBindingConfirm?.addEventListener("change", () => {
  if (!activeMaterialBindingPlan) return;
  const blockers = Array.isArray(activeMaterialBindingPlan.blocking_reasons)
    ? activeMaterialBindingPlan.blocking_reasons.filter(Boolean)
    : [];
  if (blockers.length) {
    lessonMaterialBindingConfirm.checked = false;
    activeMaterialBindingPlan = {
      ...activeMaterialBindingPlan,
      status: "blocked",
    };
    updateLessonConfirmAvailability();
    return;
  }
  activeMaterialBindingPlan = {
    ...activeMaterialBindingPlan,
    status: lessonMaterialBindingConfirm.checked ? "confirmed" : "needs_confirmation",
  };
  updateLessonConfirmAvailability();
});

lessonTextMaterialConfirmButton?.addEventListener("click", async () => {
  if (!activeLessonProposal?.proposal_id || !activeTextMaterialDraft) return;
  const confirmedText = lessonTextMaterialInput?.value.trim() || "";
  if (!confirmedText) {
    if (lessonTextMaterialMessage) lessonTextMaterialMessage.textContent = "请先确认或补充至少一行文字音乐材料。";
    lessonTextMaterialInput?.focus();
    return;
  }
  lessonTextMaterialConfirmButton.disabled = true;
  lessonTextMaterialConfirmButton.textContent = "确认中";
  try {
    const result = await confirmTextMaterial(activeLessonProposal.proposal_id, {
      ...activeTextMaterialDraft,
      confirmed_text: confirmedText,
    });
    activeLessonProposal = result;
    renderLessonProposal(result);
    setTimeline([
      ["文字材料已确认", "已转成可绑定的课堂材料。", "done"],
      ["确认绑定", "请确认材料放置后生成。", "active"],
    ]);
  } catch (error) {
    if (lessonTextMaterialMessage) lessonTextMaterialMessage.textContent = error.message || "文字材料确认失败。";
  } finally {
    lessonTextMaterialConfirmButton.disabled = false;
    lessonTextMaterialConfirmButton.textContent = "确认文字材料";
  }
});

async function submitLessonGameConfirmation(button) {
  if (!activeLessonProposal?.proposal_id) {
    setTimeline([["先分析教案", "上传或粘贴教案后再确认。", "blocked"]]);
    return;
  }
  if (!materialBindingIsConfirmed()) {
    setTimeline([["确认材料", "请先确认谱子和音频放到了正确的游戏位置，或使用常规音乐要素训练模式。", "blocked"]]);
    lessonMaterialBindingConfirm?.focus();
    return;
  }

  const originalText = button.textContent;
  button.disabled = true;
  button.textContent = "生成中";
  setTimeline([
    ["方案确认", "按当前方案生成。", "done"],
    [
      "生成页面",
      activeLessonRecommendation?.matched
        ? `已命中：${activeLessonRecommendation.template_label || "成熟游戏模板"}，将生成可试玩学生游戏。`
        : "生成可修改小游戏。",
      "active",
    ],
  ]);

  closeLessonConfigModal();
  openAppPage("library");
  showDirectResultGuide("lesson-generating");
  const result = await confirmLessonGame(activeLessonProposal.proposal_id, collectLessonProposalOverrides());
  button.disabled = false;
  button.textContent = originalText || "确认并生成";
  if (!result) {
    showDirectResultGuide("failed", {
      mode: "lesson",
      message: "教案游戏没有生成成功，请根据上方状态提示重新确认方案或再试一次。",
    });
    return;
  }

  setTimeline([
    ["方案确认", "已按当前方案生成。", "done"],
    [
      "工具已生成",
      templateRuntimeIsReact(result)
        ? `已生成新版游戏：${result.template_workflow?.instance?.template_label || activeLessonRecommendation?.template_label || "成熟游戏模板"}。`
        : "可打开，也可继续修改。",
      "done",
    ],
  ]);
  const card = renderArtifact(result, { highlight: true });
  showDirectResultGuide("completed", { ...result, mode: "lesson" });
  focusGeneratedArtifact(card);
}

function resetLessonProposalForEditing() {
  closeLessonConfigModal();
  hideLessonProposal();
  activeLessonProposal = null;
  activeMaterialBindingPlan = null;
  lessonText.focus();
  setTimeline([["继续调整", "修改教案或要求后再次分析。", "active"]]);
}

lessonScoreReviewApply?.addEventListener("click", () => {
  const text = lessonScoreReviewText?.value.trim() || "";
  if (!text) {
    if (lessonScoreReviewMessage) {
      lessonScoreReviewMessage.textContent = "请先填入可确认的文字谱，再重新分析。";
    }
    lessonScoreReviewText?.focus();
    return;
  }
  songMaterialText.value = text;
  hideLessonProposal();
  setTimeline([
    ["识谱已修正", "正在用确认后的文字谱重新分析教案。", "active"],
    ["提出方案", "重新生成更贴合歌曲材料的游戏方案。", "pending"],
  ]);
  lessonGameForm.requestSubmit();
});

lessonAudioSaveButton?.addEventListener("click", async () => {
  if (!activeLessonProposal?.proposal_id) {
    lessonAudioStatus.textContent = "请先分析教案。";
    return;
  }
  const mappings = collectLessonAudioMappings();
  if (!mappings.length) {
    lessonAudioStatus.textContent = "请先填写至少一组开始和结束秒数。";
    return;
  }
  lessonAudioSaveButton.disabled = true;
  lessonAudioSaveButton.textContent = "保存中";
  lessonAudioStatus.textContent = "正在切片并绑定到对应片段。";
  try {
    const result = await saveLessonAudioClips(activeLessonProposal.proposal_id, mappings);
    activeLessonProposal = result;
    markMaterialBindingConfirmedAfterAudioSave(result);
    renderLessonProposal(result);
    lessonAudioStatus.textContent = materialBindingIsConfirmed()
      ? "音频片段已保存并确认，可以继续调整参数或生成游戏。"
      : "音频片段已保存，后续生成会优先使用这些真实切片。";
  } catch (error) {
    lessonAudioStatus.textContent = error.message || "保存音频切片失败。";
  } finally {
    lessonAudioSaveButton.disabled = false;
    lessonAudioSaveButton.textContent = "保存切片";
  }
});

lessonAudioAddButton?.addEventListener("click", () => {
  if (!lessonAudioRows || lessonAudioEditor?.hidden) return;
  const nextIndex = lessonAudioRows.querySelectorAll(".lesson-audio-row").length + 1;
  lessonAudioRows.insertAdjacentHTML(
    "beforeend",
    renderLessonAudioRow(
      {
        id: `manual_clip_${Date.now()}`,
        label: `自定义片段 ${nextIndex}`,
        hint: "新增片段：边听边设置开始和结束。",
        start: "",
        end: "",
        manual: true,
      },
      nextIndex - 1,
      Number.isFinite(lessonAudioSource?.duration) ? lessonAudioSource.duration : ""
    )
  );
  syncAudioSeekRanges();
  lessonAudioStatus.textContent = `已增加“自定义片段 ${nextIndex}”，请设置开始和结束后保存。`;
});

lessonAudioRows?.addEventListener("click", (event) => {
  if (!(event.target instanceof Element)) return;
  const button = event.target.closest("[data-audio-action]");
  if (!button) return;
  const row = button.closest(".lesson-audio-row");
  if (!row) return;
  const action = button.dataset.audioAction;
  if (action === "delete") {
    const label = row.querySelector('[data-role="label"]')?.value || row.dataset.clipTarget || "这个片段";
    row.remove();
    renumberManualAudioRows();
    lessonAudioStatus.textContent = `已删除“${label}”。保存后会从生成材料里移除。`;
    return;
  }
  if (!lessonAudioSource) return;
  const current = roundAudioTime(lessonAudioSource.currentTime || 0);
  if (action === "set-start") {
    setAudioRowValue(row, "start", current);
    lessonAudioStatus.textContent = `已把当前位置 ${formatAudioTime(current)} 设为开始。`;
    return;
  }
  if (action === "set-end") {
    setAudioRowValue(row, "end", current);
    lessonAudioStatus.textContent = `已把当前位置 ${formatAudioTime(current)} 设为结束。`;
    return;
  }
  if (action === "preview") {
    previewAudioRow(row);
  }
});

lessonAudioRows?.addEventListener("input", (event) => {
  const target = event.target;
  if (!(target instanceof HTMLInputElement)) return;
  const row = target.closest(".lesson-audio-row");
  if (!row || !lessonAudioSource) return;
  if (target.dataset.role === "seek") {
    const nextTime = Number(target.value);
    if (Number.isFinite(nextTime)) {
      lessonAudioSource.currentTime = nextTime;
      const readout = row.querySelector("[data-role='seek-readout']");
      if (readout) readout.textContent = formatAudioTime(nextTime);
    }
  }
});

lessonAudioSource?.addEventListener("loadedmetadata", () => {
  syncAudioSeekRanges();
});

lessonAudioSource?.addEventListener("timeupdate", () => {
  const time = lessonAudioSource.currentTime || 0;
  document.querySelectorAll(".lesson-audio-row").forEach((row) => {
    const seek = row.querySelector("[data-role='seek']");
    const readout = row.querySelector("[data-role='seek-readout']");
    if (seek && document.activeElement !== seek) {
      seek.value = String(time);
    }
    if (readout) {
      readout.textContent = formatAudioTime(time);
    }
  });
});

async function initializeAuth() {
  if (shouldResumeDevSession()) {
    try {
      const response = await fetch("/api/auth/me");
      const data = await response.json();
      if (response.ok && data.authenticated && data.user) {
        currentUser = data.user;
        clearDevSessionMarker();
        await showStudioShell();
        return;
      }
    } catch {
      // Fall through to the normal manual login screen.
    }
  }

  await clearStartupSession();
  currentUser = null;
  setAuthView("login");
  showAuthShell("请输入账号密码登录。");
}

function shouldResumeDevSession() {
  return new URLSearchParams(window.location.search).get("dev_session") === "1";
}

function clearDevSessionMarker() {
  const url = new URL(window.location.href);
  if (!url.searchParams.has("dev_session")) return;
  url.searchParams.delete("dev_session");
  window.history.replaceState({}, "", `${url.pathname}${url.search}${url.hash}`);
}

async function clearStartupSession() {
  try {
    await fetch("/api/auth/logout", { method: "POST" });
  } catch {
    // Keep the login screen available even if the cookie cleanup cannot complete.
  }
}

function redirectToLogin(message = "auth-required") {
  const currentPath = window.location.pathname + window.location.search + window.location.hash;
  const next = encodeURIComponent(window.location.pathname === "/login" ? "/" : currentPath);
  window.location.assign(`/login?next=${next}&message=${encodeURIComponent(message)}`);
}

function showAuthShell(message = "") {
  document.body.dataset.authState = "signed-out";
  if (authShell) authShell.hidden = false;
  if (studioShell) studioShell.hidden = true;
  if (authStatus && message) authStatus.textContent = message;
  if (accountEmail) accountEmail.textContent = "未登录";
}

async function showStudioShell() {
  document.body.dataset.authState = "signed-in";
  if (authShell) authShell.hidden = true;
  if (studioShell) studioShell.hidden = false;
  syncAccountIdentity();
  if (authStatus) authStatus.textContent = "";
  openAppPage(document.body.dataset.activePage || "home");
  await loadUserArtifacts();
}

function syncAccountIdentity() {
  const email = currentUser?.email || "未登录";
  if (accountEmail) accountEmail.textContent = email;
  if (myAccountEmail) myAccountEmail.textContent = email;
}

function setAuthView(view) {
  const nextView = ["login", "register", "forgot"].includes(view) ? view : "login";
  document.querySelector(".auth-card")?.setAttribute("data-auth-view", nextView);
  authTabs.forEach((button) => button.classList.toggle("active", button.dataset.authTab === nextView));
  authForms.forEach((form) => {
    const active = form.dataset.authForm === nextView;
    form.hidden = !active;
    form.classList.toggle("active", active);
  });
  if (authStatus) authStatus.textContent = "";
}

async function requestAuthCode(button, url, email) {
  if (!email) {
    setAuthStatus("请先填写邮箱地址。", "error");
    return;
  }
  button.disabled = true;
  const originalText = button.textContent;
  button.textContent = "发送中";
  try {
    await postForm(url, { email });
    setAuthStatus("验证码已发送，请查看邮箱。", "success");
  } catch (error) {
    setAuthStatus(error.message || "验证码发送失败。", "error");
  } finally {
    button.disabled = false;
    button.textContent = originalText;
  }
}

async function submitAuthForm(url, fields) {
  try {
    const data = await postForm(url, fields);
    currentUser = data.user;
    await showStudioShell();
  } catch (error) {
    setAuthStatus(error.message || "账号操作失败。", "error");
  }
}

async function postForm(url, fields) {
  const payload = new FormData();
  Object.entries(fields).forEach(([key, value]) => payload.append(key, value || ""));
  const response = await fetch(url, {
    method: "POST",
    body: payload,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || data.detail || "请求失败。");
  }
  return data;
}

function setAuthStatus(message, state = "") {
  if (!authStatus) return;
  authStatus.textContent = message;
  authStatus.dataset.state = state;
}

function setAccountStatus(message, state = "") {
  if (!accountStatus) return;
  accountStatus.textContent = message;
  accountStatus.dataset.state = state;
}

async function logoutCurrentUser(button) {
  if (button) button.disabled = true;
  try {
    await fetch("/api/auth/logout", { method: "POST" });
  } finally {
    if (button) button.disabled = false;
    currentUser = null;
    redirectToLogin("logged-out");
  }
}

function valueOf(selector) {
  return document.querySelector(selector)?.value.trim() || "";
}

async function loadUserArtifacts() {
  try {
    const response = await fetch("/api/artifacts");
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || data.detail || "作品加载失败");
    const artifacts = Array.isArray(data.artifacts) ? data.artifacts : [];
    artifactList.innerHTML = "";
    artifactCardsById.clear();
    closeArtifactDetail();
    if (!artifacts.length) {
      renderEmptyArtifactState();
      return;
    }
    artifacts.slice().reverse().forEach((artifact) => renderArtifact(artifact, { select: false }));
  } catch (error) {
    artifactList.innerHTML = "";
    renderEmptyArtifactState(error.message || "作品加载失败，请稍后再试。");
  }
}

function renderEmptyArtifactState(message = "生成完成后在这里打开和继续修改。") {
  artifactList.innerHTML = `
    <article class="empty-state">
      <div class="empty-illustration" aria-hidden="true"></div>
      <strong>还没有生成结果</strong>
      <p>${escapeHtml(message)}</p>
    </article>
  `;
}

function normalizeNeed(rawNeed) {
  const prefix = modulePrefixes[selectedModule] || "";
  if (
    rawNeed.startsWith("生成一个") ||
    rawNeed.includes("聆听") ||
    rawNeed.includes("表现") ||
    rawNeed.includes("创造") ||
    rawNeed.includes("小游戏") ||
    rawNeed.includes("游戏")
  ) {
    return rawNeed;
  }
  return `${prefix}${rawNeed}`;
}

function normalizeGenerationMode(mode) {
  return mode === "strict" ? "strict" : "fast";
}

function extractGenerationModeFromSpec(specText) {
  try {
    const spec = JSON.parse(specText || "{}");
    return spec.generation_mode || spec.lesson_generation_policy?.mode || "strict";
  } catch {
    return "strict";
  }
}

function setMainMode(mode) {
  const nextMode = mode === "direct" ? "direct" : "lesson";
  modeTabs.forEach((tab) => {
    const active = tab.dataset.dialogMode === nextMode;
    tab.classList.toggle("active", active);
    tab.setAttribute("aria-selected", active ? "true" : "false");
  });
  Object.entries(modePanels).forEach(([panelMode, panel]) => {
    if (!panel) return;
    panel.hidden = panelMode !== nextMode;
    panel.classList.toggle("is-active", panelMode === nextMode);
  });
  if (lessonPage) {
    lessonPage.dataset.workMode = "lesson";
  }
  if (directPage) {
    directPage.dataset.workMode = "direct";
  }
  updateWorkModeCopy(nextMode);
  syncAppNav(nextMode);
}

function setDirectGenerationMode(mode) {
  directGenerationMode = normalizeGenerationMode(mode);
  updateGenerationModeButtons(
    [
      [directFastModeButton, "fast"],
      [directStrictModeButton, "strict"],
    ],
    directGenerationMode
  );
  updateDirectGenerationModeCopy();
}

function setLessonGenerationMode(mode) {
  lessonGenerationMode = normalizeGenerationMode(mode);
  updateGenerationModeButtons(
    [
      [lessonFastModeButton, "fast"],
      [lessonStrictModeButton, "strict"],
    ],
    lessonGenerationMode
  );
  updateLessonGenerationModeCopy();
}

function updateGenerationModeButtons(buttonPairs, activeMode) {
  buttonPairs.forEach(([button, mode]) => {
    if (!button) return;
    const active = mode === activeMode;
    button.classList.toggle("active", active);
    button.setAttribute("aria-pressed", active ? "true" : "false");
  });
}

function updateDirectGenerationModeCopy() {
  if (!directGenerationModeDesc) return;
  directGenerationModeDesc.textContent = "先生成可试玩版本，完成后可在作品页继续优化。";
}

function updateLessonGenerationModeCopy() {
  if (!lessonGenerationModePanel || !lessonGenerationModeDesc) return;
  lessonGenerationModeDesc.textContent = "先生成可试玩版本，完成后可在作品页继续优化。";
  lessonGenerationModePanel.hidden = true;
}

function openAppPage(page) {
  const nextPage = ["home", "lesson", "direct", "library"].includes(page) ? page : "home";
  if (nextPage === "library") {
    setMyView("works");
  }
  document.body.dataset.activePage = nextPage;
  Object.entries(appPages).forEach(([pageName, panel]) => {
    if (!panel) return;
    const active = pageName === nextPage;
    panel.hidden = !active;
    panel.classList.toggle("is-active", active);
  });
  if (page === "lesson" || page === "direct") {
    setMainMode(page);
  } else {
    syncAppNav(page);
  }
  resetPageScrollState(nextPage);
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function setMyView(view) {
  const nextView = view === "account" ? "account" : "works";
  myTabs.forEach((button) => {
    const active = button.dataset.myView === nextView;
    button.classList.toggle("active", active);
    button.setAttribute("aria-selected", active ? "true" : "false");
  });
  myPanels.forEach((panel) => {
    const active = panel.dataset.myPanel === nextView;
    panel.hidden = !active;
    panel.classList.toggle("is-active", active);
  });
  if (nextView === "account") {
    syncAccountIdentity();
    setAccountStatus("");
  }
}

function resetPageScrollState(page) {
  const panel = appPages[page];
  if (!panel) return;

  panel
    .querySelectorAll(
      ".app-work-card, .app-library, .dialog-mode-panel--lesson, .dialog-mode-panel--direct, .timeline, .artifact-list, .chat-messages"
        + ", .lesson-game-card--embedded"
    )
    .forEach((node) => {
      node.scrollTop = 0;
      node.scrollLeft = 0;
    });
}

function syncAppNav(page) {
  const activePage = page;
  appNavButtons.forEach((button) => {
    const active = button.dataset.appPage === activePage;
    button.classList.toggle("active", active);
    button.setAttribute("aria-current", active ? "page" : "false");
  });
}

function updateWorkModeCopy(mode) {
  if (!workPageTitle || !workPageSubtitle) return;
  if (mode === "direct") {
    workPageTitle.textContent = "直接生成工具";
    workPageSubtitle.textContent = "写下课堂目标，智能体会生成可打开、可继续修改的音乐工具。";
  } else {
    workPageTitle.textContent = "教案生成游戏";
    workPageSubtitle.textContent = "上传教案，先确认教学重点和玩法，再生成音乐课堂游戏。";
  }
}

function updateNeedPlaceholder() {
  needInput.placeholder = modulePlaceholders[selectedModule] || modulePlaceholders.listening;
}

async function guideNeed(need) {
  const payload = new FormData();
  payload.append("need", need);
  try {
    const response = await fetch("/api/agent/guide", {
      method: "POST",
      body: payload,
    });
    return await response.json();
  } catch {
    return {
      ready: true,
      normalized_need: need,
      activity_label: activityLabels[selectedModule],
    };
  }
}

async function polishNeed(need) {
  const payload = new FormData();
  payload.append("need", need);

  try {
    const response = await fetch("/api/agent/polish", {
      method: "POST",
      body: payload,
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "润色失败");
    }
    return data;
  } catch (error) {
    setTimeline([["润色失败", error.message || "请稍后再试，或先手动补充想法。", "blocked"]]);
    return null;
  }
}

async function sendChatMessage(message) {
  const payload = new FormData();
  payload.append("message", message);
  if (inspirationChatSessionId) {
    payload.append("session_id", inspirationChatSessionId);
  }

  try {
    const response = await fetch("/api/agent/chat", {
      method: "POST",
      body: payload,
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "对话失败");
    }
    if (data.session_id) {
      inspirationChatSessionId = data.session_id;
    }
    return data;
  } catch {
    return null;
  }
}

function addChatMessage(role, text, reusable = false, loading = false, suggestedNeed = "") {
  const message = document.createElement("article");
  message.className = `chat-message ${role}${loading ? " loading" : ""}`;
  message.innerHTML = `
    <span>${role === "user" ? "我的想法" : "灵感助手"}</span>
    <p>${escapeHtml(text).replaceAll("\n", "<br />")}</p>
  `;

  if (reusable) {
    const useButton = document.createElement("button");
    useButton.type = "button";
    useButton.className = "use-chat-button";
    useButton.textContent = "放入生成框";
    useButton.addEventListener("click", () => {
      openAppPage("direct");
      setMainMode("direct");
      needInput.value = suggestedNeed || text;
      hidePolishPanel();
      needInput.focus();
      setTimeline([["已放入", "可继续修改，或直接生成。", "done"]]);
    });
    message.appendChild(useButton);
  }

  chatMessages.appendChild(message);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return message;
}

async function generateArtifact(need) {
  const payload = new FormData();
  payload.append("need", need);
  payload.append("force_local", "false");
  payload.append("generation_mode", directGenerationMode);
  payload.append("activity_type", selectedModule);
  if (selectedModule === "music_game" && activeTemplateConfigs.direct) {
    payload.append("template_config", JSON.stringify(activeTemplateConfigs.direct));
  }

  try {
    resetJobLog("已提交");
    const response = await fetch("/api/agent/generate-webpage-job", {
      method: "POST",
      body: payload,
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "生成失败");
    }
    if (!data.job_id) return data;
    return await waitForJob(data.job_id, "生成课堂工具");
  } catch (error) {
    setTimeline([
      ["生成失败", error.message || "请换一种更具体的描述。", "blocked"],
    ]);
    return null;
  }
}

async function analyzeLessonGame(lessonTextValue, lessonFileValue, extraNeed, scoreFileValue, audioFileValue, songMaterialTextValue) {
  const payload = new FormData();
  payload.append("lesson_text", lessonTextValue);
  payload.append("extra_need", extraNeed || "");
  payload.append("song_material_text", songMaterialTextValue || "");
  if (lessonFileValue) {
    payload.append("lesson_file", lessonFileValue);
  }
  if (scoreFileValue) {
    payload.append("score_file", scoreFileValue);
  }
  if (audioFileValue) {
    payload.append("audio_file", audioFileValue);
  }

  try {
    const response = await fetch("/api/lesson/analyze-game", {
      method: "POST",
      body: payload,
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "分析失败");
    }
    return data;
  } catch (error) {
    setTimeline([
      ["分析失败", error.message || "请粘贴更完整的教案，或换文件再试。", "blocked"],
    ]);
    return null;
  }
}

async function confirmLessonGame(proposalId, overrides = {}) {
  const payload = new FormData();
  payload.append("proposal_id", proposalId);
  payload.append("force_local", "false");
  payload.append("proposal_overrides", JSON.stringify(overrides || {}));
  payload.append("generation_mode", lessonGenerationMode);
  payload.append("confirmed_material_binding_plan", JSON.stringify(activeMaterialBindingPlan || {}));
  const adjustmentContract =
    activeLessonProposal?.music_element_adjustment_contract ||
    activeLessonProposal?.proposal?.music_element_adjustment_contract ||
    activeLessonProposal?.lesson_analysis?.music_element_adjustment_contract ||
    {};
  payload.append("music_element_adjustment", JSON.stringify(adjustmentContract));
  if (activeTemplateConfigs.lesson) {
    payload.append("template_config", JSON.stringify(activeTemplateConfigs.lesson));
  }

  try {
    resetJobLog("已提交");
    const response = await fetch("/api/lesson/confirm-game-job", {
      method: "POST",
      body: payload,
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "生成失败");
    }
    if (!data.job_id) return data;
    return await waitForJob(data.job_id, "确认后生成网页");
  } catch (error) {
    setTimeline([
      ["生成失败", error.message || "请重新分析教案后再确认。", "blocked"],
    ]);
    return null;
  }
}

async function confirmTextMaterial(proposalId, draft) {
  const payload = new FormData();
  payload.append("proposal_id", proposalId);
  payload.append("text_material_draft", JSON.stringify(draft || {}));
  const response = await fetch("/api/lesson/confirm-text-material", {
    method: "POST",
    body: payload,
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "文字材料确认失败");
  }
  return data;
}

function renderLessonProposal(data) {
  const proposal = data.proposal || {};
  const analysis = data.lesson_analysis || {};
  const game = analysis.recommended_game || {};
  activeMaterialBindingPlan = normalizeMaterialBindingPlan(data.material_binding_plan || proposal.material_binding_plan || analysis.material_binding_plan || {});
  activeTextMaterialDraft = normalizeTextMaterialDraft(data.text_material_draft || proposal.text_material_draft || analysis.text_material_draft || {});
  const songMaterialSummary = proposal.song_material_summary || analysis.song_material_summary || {};
  const scoreReview = proposal.score_review || analysis.score_review || data.song_material?.score_review || data.song_material?.source?.score_review || {};
  lessonProposalPanel.hidden = false;
  bindLessonFrameToProposal(data.proposal_id || "");
  lessonProposalTitle.textContent = proposal.title || "课堂小游戏方案";
  renderLessonMaterialBadge(songMaterialSummary, proposal.song_anchor || {});
  renderLessonScoreReview(scoreReview);
  const evidence = proposal.evidence ? `我抓到的教案依据是：“${proposal.evidence}”。` : "";
  const winCondition = proposal.win_condition ? `目标是：${proposal.win_condition}` : "";
  const selected = proposal.selected_segment || {};
  const songAnchor = proposal.song_anchor || {};
  const lessonFit = proposal.lesson_fit || analysis.lesson_fit || {};
  const templateGroundedPlan =
    proposal.template_grounded_game_plan ||
    analysis.template_grounded_game_plan ||
    analysis.lesson_context?.template_grounded_game_plan ||
    {};
  const adjustmentContract =
    proposal.music_element_adjustment_contract ||
    data.music_element_adjustment_contract ||
    analysis.music_element_adjustment_contract ||
    lessonFit.music_element_adjustment_contract ||
    {};
  const fitEvidence = lessonFit.lesson_evidence || {};
  const materialBinding = lessonFit.material_binding || {};
  const songLine = songAnchor.enabled
    ? songAnchor.selected_phrase?.label
      ? `歌曲材料已接入：${songAnchor.song_title || "当前歌曲"}，使用${songAnchor.selected_phrase.label}。`
      : `歌曲材料已接入：${songAnchor.song_title || "当前歌曲"}，还需要确认具体旋律片段。`
    : songAnchor.required
      ? "这节课需要谱子支撑，请上传歌曲材料或填写核心乐句后再生成。"
    : "";
  const segmentLine = selected.task
    ? `建议把“${selected.stage || proposal.stage || "核心练习环节"}”中的“${selected.task}”做成主游戏。`
    : "";
  const fitLine = lessonFit.fit_summary
    ? `贴合层判断：${lessonFit.fit_summary}`
    : "";
  const transferLine = lessonFit.transfer_task
    ? `游戏后迁移：${lessonFit.transfer_task}`
    : "";
  lessonProposalSummary.textContent =
    `放在${proposal.stage || "核心练习环节"}，聚焦“${proposal.core_focus || "综合音乐感知"}”。${songLine}${segmentLine}${fitLine}${transferLine}${evidence}${proposal.idea || ""}${winCondition}`;
  lessonProposalFlow.innerHTML = renderProposalList(proposal.student_flow || []);
  const decisionItems = [
    ...(templateGroundedPlan.template_label || templateGroundedPlan.game_name
      ? [`匹配模板：${templateGroundedPlan.template_label || templateGroundedPlan.game_name}`]
      : []),
    ...(Array.isArray(templateGroundedPlan.reason_items)
      ? templateGroundedPlan.reason_items.filter((item) => !String(item || "").startsWith("匹配模板")).slice(0, 2)
      : []),
    ...templateSkinDecisionItems(data),
    ...musicElementAdjustmentDecisionItems(adjustmentContract),
    ...(lessonFit.fit_summary ? [`教案贴合：${lessonFit.fit_summary}`] : []),
    ...(fitEvidence.target_objective ? [`贴合目标：${fitEvidence.target_objective}`] : []),
    ...(materialBinding.selected_phrase_label ? [`绑定片段：${materialBinding.song_title || "当前作品"} ${materialBinding.selected_phrase_label}`] : []),
    ...(lessonFit.transfer_task ? [`迁移闭环：${lessonFit.transfer_task}`] : []),
    ...(proposal.decision_trace || []),
    ...(proposal.goal_task_mapping || [])
      .slice(0, 2)
    .map((item) => `${item.goal || "课堂目标"} -> ${item.best_stage || "课堂环节"} -> ${item.gameable_point || "可操作任务"}`),
    ...(proposal.teacher_checks || []),
  ];
  lessonProposalChecks.innerHTML = renderProposalList(Array.from(new Set(decisionItems.filter(Boolean))).slice(0, 6));
  activeLessonProposalDefaults = {
    core_focus: proposal.core_focus || "",
    stage: proposal.stage || "",
    game_name: proposal.game_name || templateGroundedPlan.game_name || game.name || proposal.title || "",
    student_flow: proposal.student_flow || [],
    rules: [
      ...(proposal.game_rules || []),
      ...(proposal.win_condition ? [`通关标准：${proposal.win_condition}`] : []),
    ],
  };
  lessonUnmatchedEditFocus.value = activeLessonProposalDefaults.core_focus;
  lessonUnmatchedEditStage.value = activeLessonProposalDefaults.stage;
  lessonUnmatchedEditGameName.value = activeLessonProposalDefaults.game_name;
  lessonUnmatchedEditStudentFlow.value = activeLessonProposalDefaults.student_flow.join("\n");
  lessonUnmatchedEditRules.value = activeLessonProposalDefaults.rules.join("\n");
  renderLessonAudioEditor(proposal.audio_clip_editor || {});
  renderTextMaterialDraft(activeTextMaterialDraft);
  renderMaterialBindingPlan(activeMaterialBindingPlan);
  renderLessonProposalActions(Boolean(activeLessonRecommendation?.matched));
  updateLessonConfirmAvailability();
  closeLessonConfigModal();
}

function musicElementAdjustmentDecisionItems(contract) {
  if (!contract || !contract.version) return [];
  const focus = contract.lesson_focus || {};
  const match = contract.template_match || {};
  const adjustments = Array.isArray(contract.element_adjustments)
    ? contract.element_adjustments
    : [];
  const unsupported = Array.isArray(contract.unsupported_elements)
    ? contract.unsupported_elements
    : [];
  const items = [];
  if (focus.primary_element) {
    items.push(`识别重点：${focus.primary_element}`);
  }
  if (match.template_label || match.template_id) {
    const confidence = typeof match.confidence === "number" ? `，置信度 ${Math.round(match.confidence * 100)}%` : "";
    items.push(`匹配模板：${match.template_label || match.template_id}${confidence}`);
  }
  adjustments.slice(0, 3).forEach((item) => {
    if (item.teacher_label) items.push(`音乐要素调整：${item.teacher_label}`);
  });
  if (unsupported.length) {
    items.push("暂不支持要素：力度、速度或表情类要素需要专属模板，当前不会硬套六模板。");
  }
  return items;
}

function templateSkinDecisionItems(data) {
  const contract = data.lesson_template_contract || data.template_fidelity_contract || {};
  const workflowContract = data.workflow?.template_fidelity_contract || {};
  const proposal = data.proposal || {};
  const templateLabel =
    contract.template_label ||
    activeLessonRecommendation?.template_label ||
    proposal.template_label ||
    workflowContract.template_id ||
    contract.template_id ||
    "";
  const skinId =
    activeTemplateConfigs.lesson?.skin_id ||
    workflowContract.selected_skin_id ||
    proposal.skin_id ||
    contract.selected_skin_id ||
    "";
  const skinLabel =
    activeTemplateConfigs.lesson?.theme ||
    proposal.skin_label ||
    skinLabelFromRecommendation(skinId) ||
    skinId ||
    "";
  if (!templateLabel && !skinLabel) return [];
  const source = workflowContract.skin_selection_source || contract.skin_selection_source || "";
  const sourceLabel = {
    teacher_selected: "教师已选择",
    lesson_recommended: "教案推荐",
    template_default: "模板默认",
  }[source] || "可切换";
  return [`当前使用${templateLabel || "成熟游戏"}模板 · 皮肤：${skinLabel || "模板默认"}（${sourceLabel}）`];
}

function skinLabelFromRecommendation(skinId) {
  if (!skinId || !activeLessonRecommendation?.skins) return "";
  const skin = activeLessonRecommendation.skins.find((item) => item.skin_id === skinId);
  return skin?.label || "";
}

function bindLessonFrameToProposal(proposalId) {
  if (!proposalId) return;
  const lessonFrame = getTemplateFrames().find((frame) => frame.dataset.templateContext === "lesson");
  if (!lessonFrame) return;
  const lessonFrameSrc = `/template-console/?context=lesson&proposal_id=${encodeURIComponent(proposalId)}`;
  if (lessonFrame.getAttribute("src") !== lessonFrameSrc) {
    lessonFrame.setAttribute("src", lessonFrameSrc);
  }
}

function syncLessonFrameWhenReady(lessonFrame) {
  if (!lessonFrame) return;
  lessonFrame.addEventListener("load", () => sendLessonTemplateState(lessonFrame), { once: true });
  sendLessonTemplateState(lessonFrame);
}

function renderLessonProposalActions(hasMatchedTemplate) {
  if (lessonOpenConfigButton) lessonOpenConfigButton.hidden = !hasMatchedTemplate;
  if (lessonConfirmButton) lessonConfirmButton.hidden = !hasMatchedTemplate;
  if (lessonUnmatchedConfirmButton) lessonUnmatchedConfirmButton.hidden = true;
  if (lessonUnmatchedEditor) lessonUnmatchedEditor.hidden = hasMatchedTemplate;
  updateLessonConfirmAvailability();
}

function renderTextMaterialDraft(draft) {
  if (!lessonTextMaterialPanel || !lessonTextMaterialInput || !lessonTextMaterialMessage || !lessonTextMaterialConfirmButton) return;
  const enabled = Boolean(draft && draft.status);
  lessonTextMaterialPanel.hidden = !enabled;
  if (!enabled) {
    lessonTextMaterialInput.value = "";
    lessonTextMaterialMessage.textContent = "";
    return;
  }
  lessonTextMaterialInput.value = draft.confirmed_text || "";
  lessonTextMaterialInput.disabled = draft.status === "confirmed";
  lessonTextMaterialConfirmButton.hidden = draft.status === "confirmed";
  lessonTextMaterialMessage.textContent = draft.status === "confirmed"
    ? "文字材料已确认，会作为本次游戏的临时谱面材料。"
    : draft.message || "请确认或修正后再进入材料绑定。";
}

function normalizeTextMaterialDraft(draft) {
  if (!draft || typeof draft !== "object") return null;
  return draft;
}

function renderMaterialBindingPlan(plan) {
  if (!lessonMaterialBindingPanel || !lessonMaterialBindingList || !lessonMaterialBindingStatus || !lessonMaterialBindingConfirm) return;
  const bindings = Array.isArray(plan?.bindings) ? plan.bindings : [];
  const notRequired = plan?.status === "not_required" || plan?.delivery_mode === "element_training_game";
  const enabled = Boolean(plan?.template_id || bindings.length);
  lessonMaterialBindingPanel.hidden = !enabled;
  lessonMaterialBindingConfirm.checked = plan?.status === "confirmed";
  if (!enabled) {
    lessonMaterialBindingStatus.textContent = "";
    lessonMaterialBindingList.innerHTML = "";
    return;
  }
  if (notRequired) {
    lessonMaterialBindingConfirm.closest("label")?.setAttribute("hidden", "");
    lessonMaterialBindingStatus.textContent = plan.message || "当前为常规音乐要素训练，将使用模板训练材料生成。";
    lessonMaterialBindingList.innerHTML = "";
    return;
  }
  lessonMaterialBindingConfirm.closest("label")?.removeAttribute("hidden");
  const blockers = materialBindingBlockers(plan);
  const waitingForText = waitingForTextMaterialConfirmation();
  lessonMaterialBindingConfirm.disabled = Boolean(blockers.length || waitingForText);
  lessonMaterialBindingStatus.textContent = waitingForText
    ? blockers.length
      ? `请先在上方填写或确认文字材料，再重新生成可放置的材料表。当前阻断：${blockers[0]}`
      : "请先在上方填写或确认文字材料，系统会重新生成可放置的材料表。"
    : blockers.length
      ? `暂不能生成：${blockers[0]}`
      : "请逐项确认谱子用于答案、音频用于播放的位置。";
  lessonMaterialBindingList.innerHTML = bindings
    .map((binding, index) => {
      const sourceLabel = binding.display_label || binding.source_id || "未绑定";
      const usage = binding.playback_url
        ? "播放"
        : binding.answer_data && Object.keys(binding.answer_data).length
          ? "判定"
          : "材料";
      const confidence = binding.confidence === "low" ? "需核对" : binding.confidence === "missing" ? "缺材料" : "可用";
      const options = materialOptionsForBinding(plan, binding);
      return `
        <article class="lesson-material-binding-item ${escapeHtml(binding.confidence || "")}">
          <strong>${escapeHtml(binding.slot_label || binding.slot || "游戏位置")}</strong>
          ${options.length ? `
            <select data-binding-index="${index}">
              ${options.map((option) => `<option value="${escapeHtml(option.id)}" ${option.id === binding.source_id ? "selected" : ""}>${escapeHtml(option.label)}</option>`).join("")}
            </select>
          ` : `<span>${escapeHtml(sourceLabel)}</span>`}
          <small>${escapeHtml(usage)} · ${escapeHtml(sourceKindLabel(binding.source_kind))} · ${escapeHtml(confidence)}</small>
        </article>
      `;
    })
    .join("");
}

lessonMaterialBindingList?.addEventListener("change", (event) => {
  const select = event.target.closest("[data-binding-index]");
  if (!select || !activeMaterialBindingPlan) return;
  const index = Number(select.dataset.bindingIndex);
  const binding = activeMaterialBindingPlan.bindings?.[index];
  if (!binding) return;
  const option = materialOptionsForBinding(activeMaterialBindingPlan, binding).find((item) => item.id === select.value);
  if (!option) return;
  const nextBindings = activeMaterialBindingPlan.bindings.map((item, itemIndex) => {
    if (itemIndex !== index) return item;
    return {
      ...item,
      source_id: option.id,
      display_label: option.label,
      source_kind: option.source_kind,
      answer_data: option.answer_data || {},
      playback_url: option.playback_url || "",
      confidence: option.confidence || item.confidence || "medium",
    };
  });
  activeMaterialBindingPlan = {
    ...activeMaterialBindingPlan,
    status: "needs_confirmation",
    bindings: nextBindings,
  };
  renderMaterialBindingPlan(activeMaterialBindingPlan);
  updateLessonConfirmAvailability();
});

function materialOptionsForBinding(plan, binding) {
  const materials = plan?.available_materials || {};
  const kind = binding.slot_kind || "";
  const source = kind === "playback" ? materials.audio : materials.score;
  return Array.isArray(source) ? source : [];
}

function normalizeMaterialBindingPlan(plan) {
  if (!plan || typeof plan !== "object") return null;
  return {
    ...plan,
    status: plan.status === "confirmed" ? "confirmed" : plan.status || "needs_confirmation",
  };
}

function materialBindingIsConfirmed() {
  return Boolean(
    activeMaterialBindingPlan &&
      (activeMaterialBindingPlan.status === "confirmed" || activeMaterialBindingPlan.status === "not_required")
  );
}

function materialBindingBlockers(plan = activeMaterialBindingPlan) {
  return Array.isArray(plan?.blocking_reasons) ? plan.blocking_reasons.filter(Boolean) : [];
}

function waitingForTextMaterialConfirmation() {
  return Boolean(activeTextMaterialDraft && activeTextMaterialDraft.status === "needs_teacher_confirmation");
}

function materialBindingCanAutoConfirm(plan = activeMaterialBindingPlan) {
  return Boolean(
    plan &&
      plan.status !== "not_required" &&
      !materialBindingBlockers(plan).length
  );
}

function markMaterialBindingConfirmedAfterAudioSave(result) {
  const plan = normalizeMaterialBindingPlan(
    result?.material_binding_plan ||
      result?.proposal?.material_binding_plan ||
      result?.lesson_analysis?.material_binding_plan ||
      {}
  );
  if (!plan) return;
  const blockers = materialBindingBlockers(plan);
  const canUsePlan = materialBindingCanAutoConfirm(plan);
  const confirmedPlan = {
    ...plan,
    status: "confirmed",
    teacher_confirmed: true,
    confirmation_source: "manual_audio_clip_save",
    fallback_reason: canUsePlan ? plan.fallback_reason : "audio_clip_saved_playable_fallback",
    fallback_detail: blockers[0] || plan.fallback_detail || "",
  };
  activeMaterialBindingPlan = confirmedPlan;
  if (activeTextMaterialDraft?.status === "needs_teacher_confirmation") {
    activeTextMaterialDraft = {
      ...activeTextMaterialDraft,
      status: "bypassed_for_playable_game",
      blocking: false,
      message: "已先生成可玩版本，谱面可后续补充精修。",
    };
  }
  if (activeLessonProposal) activeLessonProposal.material_binding_plan = confirmedPlan;
  if (result) result.material_binding_plan = confirmedPlan;
  if (result?.proposal) result.proposal.material_binding_plan = confirmedPlan;
  if (result?.lesson_analysis) result.lesson_analysis.material_binding_plan = confirmedPlan;
  if (result) result.text_material_draft = activeTextMaterialDraft;
  if (result?.proposal) result.proposal.text_material_draft = activeTextMaterialDraft;
  if (result?.lesson_analysis) result.lesson_analysis.text_material_draft = activeTextMaterialDraft;
}

function lessonConfirmStatusMessage() {
  if (!activeLessonProposal?.proposal_id) return "";
  const blockers = materialBindingBlockers();
  if (blockers.length && !materialBindingIsConfirmed()) return `将先生成可玩版本，谱面可后续补充。当前材料提示：${blockers[0]}`;
  if (materialBindingIsConfirmed()) return "材料已确认，可以调整参数或生成游戏。";
  if (waitingForTextMaterialConfirmation()) return "将先生成可玩版本，谱面可后续补充。";
  if (activeMaterialBindingPlan) return "请确认材料放置，或保存切片后再生成。";
  return "";
}

function updateLessonConfirmAvailability() {
  const confirmed = materialBindingIsConfirmed();
  if (lessonConfirmButton && !lessonConfirmButton.hidden) {
    lessonConfirmButton.disabled = !Boolean(activeLessonProposal?.proposal_id && (confirmed || activeMaterialBindingPlan));
  }
  if (lessonOpenConfigButton && !lessonOpenConfigButton.hidden) {
    lessonOpenConfigButton.disabled = !Boolean(activeLessonProposal?.proposal_id);
  }
  if (lessonConfirmHint) {
    const message = lessonConfirmStatusMessage();
    lessonConfirmHint.hidden = !message;
    lessonConfirmHint.textContent = message;
  }
}

function sourceKindLabel(kind) {
  return {
    score: "谱面",
    text_score: "文字谱",
    audio_clip: "音频切片",
    source_audio: "整段音频",
    midi_transcription: "音频识别",
  }[kind] || "材料";
}

function openLessonConfigModal() {
  if (!lessonConfigModal || !activeLessonRecommendation?.matched) return;
  lessonConfigModal.hidden = false;
  document.body.classList.add("lesson-config-open");
  const lessonFrame = getTemplateFrames().find((frame) => frame.dataset.templateContext === "lesson");
  if (lessonFrame) {
    bindLessonFrameToProposal(activeLessonProposal?.proposal_id || "");
    syncLessonFrameWhenReady(lessonFrame);
  }
}

function closeLessonConfigModal() {
  if (!lessonConfigModal) return;
  lessonConfigModal.hidden = true;
  document.body.classList.remove("lesson-config-open");
}

function renderLessonMaterialBadge(summary, songAnchor) {
  if (!lessonMaterialBadge) return;
  const enabled = Boolean(summary && summary.enabled) || Boolean(songAnchor && songAnchor.enabled);
  lessonMaterialBadge.hidden = !enabled;
  if (!enabled) {
    lessonMaterialBadge.textContent = "";
    return;
  }
  const parts = [];
  const kind = summary.source_kind || songAnchor?.source_kind || "歌曲材料";
  parts.push(`已接入${kind}`);
  if (summary.source_filename || songAnchor?.source_filename) parts.push(summary.source_filename || songAnchor.source_filename);
  if (summary.song_title || songAnchor?.song_title) parts.push(summary.song_title || songAnchor.song_title);
  const phraseCount = Number.isFinite(summary.phrase_count) ? summary.phrase_count : songAnchor?.phrase_count;
  if (Number.isFinite(phraseCount) && phraseCount > 0) parts.push(`${phraseCount}个片段`);
  if (summary.has_audio || songAnchor?.has_audio) parts.push("含音频");
  if (songAnchor?.selected_phrase?.label) parts.push(`当前使用：${songAnchor.selected_phrase.label}`);
  if (summary.score_review_status === "needs_confirmation" || summary.requires_manual_confirmation) parts.push("需核对识谱");
  if (summary.score_review_status === "failed") parts.push("识谱需修正");
  if (summary.used_for_generation || songAnchor?.enabled) parts.push("已参与生成");
  lessonMaterialBadge.textContent = parts.join(" · ");
}

function renderLessonScoreReview(review) {
  if (!lessonScoreReview || !lessonScoreReviewText) return;
  const enabled = Boolean(review && review.enabled);
  lessonScoreReview.hidden = !enabled;
  if (!enabled) {
    lessonScoreReviewText.value = "";
    if (lessonScoreReviewAttempts) lessonScoreReviewAttempts.innerHTML = "";
    return;
  }
  const status = review.status || "";
  const phraseCount = Number(review.phrase_count || 0);
  const statusLabel = scoreReviewStatusLabel(status);
  if (lessonScoreReviewTitle) {
    lessonScoreReviewTitle.textContent = `${statusLabel}${phraseCount ? ` · ${phraseCount}个片段` : ""}`;
  }
  if (lessonScoreReviewMessage) {
    lessonScoreReviewMessage.textContent = review.message || "请核对识别结果，确认无误后再生成。";
  }
  const extraLines = [
    review.key_signature ? `调号：${review.key_signature}` : "",
    review.time_signature ? `拍号：${review.time_signature}` : "",
    review.tempo_text ? `速度：${review.tempo_text}` : "",
    Number(review.lyrics_count || 0) > 0 ? `歌词片段：${review.lyrics_count}处` : "",
    Number(review.recognized_phrase_count || 0) > 0 ? `识别到乐句摘要：${review.recognized_phrase_count}条` : "",
  ].filter(Boolean);
  const baseText = review.suggested_text_hint || review.recognized_text || review.recognized_text_preview || "";
  lessonScoreReviewText.value = [baseText, ...extraLines].filter(Boolean).join("\n");
  if (lessonScoreReviewAttempts) {
    const attempts = Array.isArray(review.attempts) ? review.attempts : [];
    lessonScoreReviewAttempts.innerHTML = attempts
      .slice(0, 4)
      .map((attempt) => {
        const engine = attempt.engine || "识别引擎";
        const state = attempt.status || (attempt.available ? "已尝试" : "未启用");
        const message = attempt.message || attempt.preview || "";
        return `<span>${escapeHtml(engine)}：${escapeHtml(state)}${message ? ` · ${escapeHtml(message)}` : ""}</span>`;
      })
      .join("");
  }
}

function scoreReviewStatusLabel(status) {
  if (status === "confirmed") return "已确认";
  if (status === "parsed") return "已识别";
  if (status === "needs_confirmation") return "需要核对";
  if (status === "failed") return "识别不稳";
  return "请核对";
}

function collectLessonProposalOverrides() {
  const useUnmatchedFields = !activeLessonRecommendation?.matched;
  return {
    core_focus: useUnmatchedFields ? lessonUnmatchedEditFocus.value.trim() : activeLessonProposalDefaults.core_focus,
    stage: useUnmatchedFields ? lessonUnmatchedEditStage.value.trim() : activeLessonProposalDefaults.stage,
    game_name: useUnmatchedFields ? lessonUnmatchedEditGameName.value.trim() : activeLessonProposalDefaults.game_name,
    student_flow: useUnmatchedFields ? splitEditableLines(lessonUnmatchedEditStudentFlow.value) : activeLessonProposalDefaults.student_flow,
    rules: useUnmatchedFields
      ? splitEditableLines(lessonUnmatchedEditRules.value)
      : activeLessonProposalDefaults.rules,
  };
}

function splitEditableLines(value) {
  return value
    .split(/\n+/)
    .map((item) => item.trim().replace(/^[-•\d.、\s]+/, ""))
    .filter(Boolean);
}

function renderProposalList(items) {
  return (items.length ? items : ["方案已准备好，确认后生成。"])
    .map((item) => `<li>${escapeHtml(item)}</li>`)
    .join("");
}

function hideLessonProposal() {
  if (lessonProposalPanel) {
    lessonProposalPanel.hidden = true;
  }
}

function renderLessonAudioEditor(editor) {
  if (!lessonAudioEditor || !lessonAudioRows || !lessonAudioSource) return;
  const enabled = Boolean(editor && editor.enabled && editor.source_audio_url && Array.isArray(editor.targets) && editor.targets.length);
  lessonAudioEditor.hidden = !enabled;
  if (!enabled) {
    lessonAudioRows.innerHTML = "";
    lessonAudioSource.removeAttribute("src");
    lessonAudioSource.load();
    lessonAudioStatus.textContent = "";
    return;
  }
  lessonAudioSource.src = editor.source_audio_url;
  const duration = Number.isFinite(lessonAudioSource.duration) ? lessonAudioSource.duration : "";
  lessonAudioRows.innerHTML = (editor.targets || [])
    .map((target, index) => renderLessonAudioRow(target, index, duration))
    .join("");
  syncAudioSeekRanges();
  lessonAudioStatus.textContent = editor.tip || "边听边切：播放原音，定位到合适位置后设置开始和结束。";
}

function renderLessonAudioRow(target, index, duration) {
  const id = target.id || `target_${index + 1}`;
  const label = target.label || `片段 ${index + 1}`;
  const clipUrl = target.audio_clip_url || "";
  return `
    <div class="lesson-audio-row" data-clip-target="${escapeHtml(id)}">
      <div class="lesson-audio-row-title">
        <label>
          <span>片段名称</span>
          <input type="text" value="${escapeHtml(label)}" data-role="label" />
        </label>
        <small>${escapeHtml(target.hint || "填写开始和结束秒数，保存后会绑定到这个片段。")}</small>
      </div>
      <div class="lesson-audio-seeker">
        <div>
          <span>定位</span>
          <strong data-role="seek-readout">00:00.0</strong>
        </div>
        <input type="range" min="0" max="${escapeHtml(String(duration || 1))}" step="0.1" value="0" data-role="seek" />
        <div class="lesson-audio-tools">
          <button type="button" data-audio-action="set-start">设为开始</button>
          <button type="button" data-audio-action="set-end">设为结束</button>
          <button type="button" data-audio-action="preview">试听切片</button>
          ${clipUrl ? `<a href="${escapeHtml(clipUrl)}" download target="_blank" rel="noreferrer" class="lesson-audio-download">下载片段</a>` : ""}
          <button type="button" data-audio-action="delete">删除</button>
        </div>
      </div>
      <label>
        <span>开始</span>
        <input type="number" min="0" step="0.1" value="${escapeHtml(String(target.start ?? ""))}" data-role="start" />
      </label>
      <label>
        <span>结束</span>
        <input type="number" min="0" step="0.1" value="${escapeHtml(String(target.end ?? ""))}" data-role="end" />
      </label>
    </div>
  `;
}

function collectLessonAudioMappings() {
  const rows = Array.from(document.querySelectorAll(".lesson-audio-row"));
  let invalidCount = 0;
  const mappings = rows
    .map((row) => {
      const id = row.dataset.clipTarget || "";
      const label = row.querySelector('[data-role="label"]')?.value.trim() || id || "自定义片段";
      const start = Number(row.querySelector('[data-role="start"]')?.value || "");
      const end = Number(row.querySelector('[data-role="end"]')?.value || "");
      const valid = id && label && Number.isFinite(start) && Number.isFinite(end) && end > start;
      row.classList.toggle("invalid", !valid);
      if (!valid) invalidCount += 1;
      return { id, label, start, end };
    });
  if (invalidCount) {
    lessonAudioStatus.textContent = "请检查红色片段：每个保留的片段都要有名称、开始和结束，且结束要大于开始。";
    return [];
  }
  return mappings;
}

function syncAudioSeekRanges() {
  if (!lessonAudioSource) return;
  const max = Number.isFinite(lessonAudioSource.duration) && lessonAudioSource.duration > 0
    ? lessonAudioSource.duration
    : 1;
  document.querySelectorAll(".lesson-audio-row [data-role='seek']").forEach((input) => {
    input.max = String(roundAudioTime(max));
  });
}

function setAudioRowValue(row, role, value) {
  const input = row.querySelector(`[data-role="${role}"]`);
  if (input) {
    input.value = String(roundAudioTime(value));
  }
}

function renumberManualAudioRows() {
  document.querySelectorAll(".lesson-audio-row").forEach((row, index) => {
    const input = row.querySelector('[data-role="label"]');
    if (!input?.value.trim()) {
      input.value = `片段 ${index + 1}`;
    }
  });
}

function previewAudioRow(row) {
  if (!lessonAudioSource) return;
  const start = Number(row.querySelector('[data-role="start"]')?.value || "");
  const end = Number(row.querySelector('[data-role="end"]')?.value || "");
  if (!Number.isFinite(start) || !Number.isFinite(end) || end <= start) {
    lessonAudioStatus.textContent = "请先设置有效的开始和结束，再试听切片。";
    return;
  }
  clearInterval(lessonAudioPreviewTimer);
  lessonAudioSource.currentTime = start;
  lessonAudioSource.play();
  lessonAudioStatus.textContent = `正在试听：${formatAudioTime(start)} - ${formatAudioTime(end)}`;
  lessonAudioPreviewTimer = window.setInterval(() => {
    if (!lessonAudioSource || lessonAudioSource.currentTime >= end) {
      lessonAudioSource.pause();
      clearInterval(lessonAudioPreviewTimer);
      lessonAudioPreviewTimer = null;
      lessonAudioStatus.textContent = `试听结束：${formatAudioTime(start)} - ${formatAudioTime(end)}`;
    }
  }, 80);
}

function roundAudioTime(value) {
  return Math.max(0, Math.round(Number(value || 0) * 10) / 10);
}

function formatAudioTime(value) {
  const total = Math.max(0, Number(value || 0));
  const minutes = Math.floor(total / 60);
  const seconds = Math.floor(total % 60);
  const tenths = Math.floor((total - Math.floor(total)) * 10);
  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}.${tenths}`;
}

async function saveLessonAudioClips(proposalId, mappings = []) {
  const payload = new FormData();
  payload.append("proposal_id", proposalId);
  payload.append("clip_mappings", JSON.stringify(mappings || []));
  const response = await fetch("/api/lesson/save-audio-clips", {
    method: "POST",
    body: payload,
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "保存音频切片失败。");
  }
  return data;
}

function renderArtifact(data, options = {}) {
  if (artifactList.querySelector(".empty-state")) {
    artifactList.innerHTML = "";
  }

  const card = artifactTemplate.content.firstElementChild.cloneNode(true);
  updateArtifactDataset(card, data);
  updateArtifactCard(card, data);
  bindArtifactCard(card);

  artifactList.prepend(card);
  if (card.dataset.artifactId) {
    artifactCardsById.set(card.dataset.artifactId, card);
  }
  if (options.select !== false) {
    selectArtifact(card);
  }
  if (options.highlight) {
    highlightNewArtifact(card);
  }
  return card;
}

function showDirectResultGuide(state, data = {}) {
  if (!directResultGuide || !directResultGuideTitle || !directResultGuideMessage) return;
  directResultGuide.hidden = false;
  directResultGuide.dataset.state = state;

  const spec = data.spec || {};
  const title = spec.title || data.title || "新作品";
  const pageUrl = data.page_url || "";
  const previewUrl = pageUrl ? withPreviewCacheBust(pageUrl, data.updated_at || data.file_path || Date.now()) : "";
  const message = data.message || "";
  const mode = data.mode === "lesson" || state.startsWith("lesson-") ? "lesson" : "direct";

  if (directResultGuideKicker) {
    directResultGuideKicker.textContent = mode === "lesson" ? "教案生成" : "直接生成";
  }

  if (state === "running") {
    directResultGuideTitle.textContent = "正在生成";
    directResultGuideMessage.textContent = "正在生成，你已经来到“我的作品”。生成完成后，新作品会出现在下方。";
  } else if (state === "lesson-generating") {
    directResultGuideTitle.textContent = "正在生成教案游戏";
    directResultGuideMessage.textContent = "正在按已确认的教案方案生成作品。生成完成后，新作品会出现在下方。";
  } else if (state === "completed") {
    directResultGuideTitle.textContent = `新作品已生成：${title}`;
    directResultGuideMessage.textContent = "下方已自动选中新作品。可以先试玩，也可以继续修改细节。";
  } else if (state === "blocked") {
    directResultGuideTitle.textContent = "还需要补充信息";
    directResultGuideMessage.textContent = message || "请补充歌曲、素材、关卡或规则后再生成。";
  } else if (state === "failed") {
    directResultGuideTitle.textContent = "生成没有完成";
    directResultGuideMessage.textContent = message || "请根据生成状态里的提示调整需求后再试。";
  } else {
    directResultGuide.hidden = true;
  }

  if (directResultPreviewLink) {
    directResultPreviewLink.href = previewUrl || "#";
    directResultPreviewLink.hidden = state !== "completed" || !pageUrl;
    directResultPreviewLink.toggleAttribute("aria-disabled", state !== "completed" || !pageUrl);
  }
  if (directResultFocusButton) {
    directResultFocusButton.textContent = "继续修改";
    directResultFocusButton.hidden = state !== "completed";
  }
}

function highlightNewArtifact(card) {
  if (!card) return;
  card.classList.add("is-new-result");
  window.setTimeout(() => {
    card.classList.remove("is-new-result");
  }, 4200);
}

function focusGeneratedArtifact(card) {
  if (!card) return;
  card.scrollIntoView({ behavior: "smooth", block: "nearest", inline: "nearest" });
}

function updateArtifactCard(card, data) {
  updateArtifactDataset(card, data);
  updateArtifactSummary(card, data);
}

function updateArtifactDataset(card, data) {
  const spec = data.spec || {};
  card.dataset.spec = JSON.stringify(spec);
  card.dataset.brain = JSON.stringify(data.brain || {});
  card.dataset.execution = JSON.stringify(data.execution || {});
  card.dataset.lessonAnalysis = JSON.stringify(data.lesson_analysis || {});
  card.dataset.filePath = data.file_path || card.dataset.filePath || "";
  card.dataset.pageUrl = data.page_url || card.dataset.pageUrl || "";
  card.dataset.artifactId = data.artifact_id || card.dataset.artifactId || "";
  card.dataset.artifactPayload = JSON.stringify(data || {});
}

function updateArtifactSummary(card, data) {
  const spec = data.spec || {};

  card.querySelector(".artifact-type").textContent = activityLabels[spec.activity_type] || "音乐工具";
  const mode = normalizeGenerationMode(spec.generation_mode || data.execution?.generation_mode);
  const modeBadge = card.querySelector(".artifact-mode");
  if (modeBadge) {
    modeBadge.textContent = `当前：${generationModeLabel(mode)}`;
    modeBadge.dataset.mode = mode;
  }
  card.querySelector("h3").textContent = data.revision ? `${spec.title || "音乐课堂工具"} · 已修改` : spec.title || "音乐课堂工具";
  card.querySelector(".artifact-subtitle").textContent = spec.subtitle || "课堂工具已生成。";
  const updatedAt = formatArtifactDate(data.updated_at || data.created_at);
  card.querySelector(".artifact-meta").innerHTML = [
    ["曲目", spec.song_name || "自选歌曲"],
    ["学段", spec.grade_band || "小学"],
    ["类型", activityLabels[spec.activity_type] || "音乐工具"],
    ["版本", generationModeLabel(mode)],
    ["更新", updatedAt || "刚刚"],
  ]
    .map(([key, value]) => `<div><dt>${escapeHtml(key)}</dt><dd>${escapeHtml(value)}</dd></div>`)
    .join("");
  const pageUrl = data.page_url || card.dataset.pageUrl || "";
  const previewUrl = pageUrl ? withPreviewCacheBust(pageUrl, data.updated_at || data.revision || data.file_path || Date.now()) : "";
  const previewFrame = card.querySelector(".artifact-preview-frame");
  const previewEmpty = card.querySelector(".artifact-preview-empty");
  if (previewFrame) {
    if (previewUrl) {
      if (previewFrame.getAttribute("src") !== previewUrl) {
        previewFrame.src = previewUrl;
      }
      previewFrame.title = `${spec.title || "音乐课堂工具"}预览`;
      previewFrame.hidden = false;
    } else {
      previewFrame.removeAttribute("src");
      previewFrame.hidden = true;
    }
  }
  if (previewEmpty) {
    previewEmpty.hidden = Boolean(pageUrl);
  }
  const previewLink = card.querySelector(".preview-link");
  if (previewLink) {
    previewLink.href = previewUrl || "#";
    previewLink.toggleAttribute("aria-disabled", !pageUrl);
  }
  const downloadLink = card.querySelector(".download-link");
  if (downloadLink) {
    downloadLink.href = card.dataset.artifactId ? `/api/artifacts/${encodeURIComponent(card.dataset.artifactId)}/download` : "#";
    downloadLink.setAttribute("download", "");
  }
}

function updateArtifactDetail(detail, data) {
  const spec = data.spec || {};
  updateArtifactDataset(detail, data);
  updateArtifactSummary(detail, data);
  renderModeReport(detail, spec, data.execution || {});
  renderRuntimeReport(detail, spec, data.execution || {}, data.runtime_marker || {});
  renderTemplateSwitchDelivery(detail, spec);
  renderTeacherConfirmationPanel(detail, spec);
  renderRevisionVersionContext(detail, spec);
  renderBrainReport(detail, data.brain || {});
  renderLessonAnalysis(detail, data.lesson_analysis || {});
  renderExecutionReport(detail, data.execution || {});
  renderUpgradePanel(detail, spec, data.execution || {}, data.lesson_analysis || {}, data.brain || {});
}

function withPreviewCacheBust(url, marker) {
  if (!url) return "";
  const separator = url.includes("?") ? "&" : "?";
  return `${url}${separator}v=${encodeURIComponent(String(marker || Date.now()))}`;
}

function bindArtifactCard(card) {
  const openDetail = () => selectArtifact(card);
  card.querySelector(".artifact-card-preview")?.addEventListener("click", openDetail);
  card.querySelector(".artifact-card-preview")?.addEventListener("keydown", (event) => {
    if (event.key !== "Enter" && event.key !== " ") return;
    event.preventDefault();
    openDetail();
  });
  card.querySelector(".artifact-card-main")?.addEventListener("click", openDetail);
  card.querySelector(".artifact-select-button")?.addEventListener("click", (event) => {
    event.preventDefault();
    event.stopPropagation();
    openDetail();
  });
  card.querySelector(".preview-link")?.addEventListener("click", (event) => event.stopPropagation());
  card.querySelector(".download-link")?.addEventListener("click", (event) => event.stopPropagation());
  card.querySelector(".delete-artifact-button")?.addEventListener("click", async (event) => {
    event.preventDefault();
    event.stopPropagation();
    await deleteArtifactFromElement(card);
  });
}

function selectArtifact(card) {
  if (!artifactDetailPanel || !artifactDetailTemplate) return;
  const payload = parseJsonDataset(card.dataset.artifactPayload, {});
  artifactCardsById.forEach((item) => item.classList.toggle("is-selected", item === card));
  artifactDetailPanel.hidden = false;
  artifactDetailPanel.innerHTML = "";
  const detail = artifactDetailTemplate.content.firstElementChild.cloneNode(true);
  updateArtifactDetail(detail, payload);
  bindRevisionForm(detail);
  bindRevisionChat(detail);
  bindUpgradeButton(detail);
  bindArtifactDetailActions(detail);
  artifactDetailPanel.appendChild(detail);
  activeArtifactDetail = detail;
}

function bindArtifactDetailActions(detail) {
  detail.querySelector(".preview-link")?.addEventListener("click", (event) => event.stopPropagation());
  detail.querySelector(".download-link")?.addEventListener("click", (event) => event.stopPropagation());
  detail.querySelector(".template-switch-notice")?.addEventListener("click", async (event) => {
    const action = event.target.closest("[data-switch-action]");
    if (!action) return;
    event.preventDefault();
    event.stopPropagation();
    await handleTemplateSwitchRetry(detail, action);
  });
  detail.querySelector(".teacher-confirmation-panel")?.addEventListener("click", async (event) => {
    const action = event.target.closest("[data-confirmation-action]");
    if (!action) return;
    event.preventDefault();
    event.stopPropagation();
    await handleTeacherConfirmation(detail, action);
  });
  detail.querySelector(".delete-artifact-button")?.addEventListener("click", async (event) => {
    event.preventDefault();
    event.stopPropagation();
    await deleteArtifactFromElement(detail);
  });
}

function closeArtifactDetail() {
  activeArtifactDetail = null;
  artifactCardsById.forEach((item) => item.classList.remove("is-selected"));
  if (!artifactDetailPanel) return;
  artifactDetailPanel.hidden = true;
  artifactDetailPanel.innerHTML = `
    <div class="artifact-detail-empty">
      <strong>选择一个作品继续修改</strong>
      <p>左侧卡片只是目录，点开后这里会显示当前作品的预览入口、生成摘要和修改工具。</p>
    </div>
  `;
}

async function deleteArtifactFromElement(element) {
  const artifactId = element.dataset.artifactId || "";
  if (!artifactId) return;
  const payload = parseJsonDataset(element.dataset.artifactPayload, {});
  const title = payload?.spec?.title || "这个作品";
  if (!window.confirm(`确定删除「${title}」吗？删除后会同时移除生成文件。`)) return;
  const response = await fetch(`/api/artifacts/${encodeURIComponent(artifactId)}`, {
    method: "DELETE",
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    window.alert(data.error || data.detail || "删除失败，请稍后再试。");
    return;
  }
  removeArtifactCard(artifactId);
  setTimeline([["作品已删除", "已从我的作品和生成文件中移除。", "done"]]);
}

function removeArtifactCard(artifactId) {
  const card = artifactCardsById.get(artifactId);
  if (card) card.remove();
  artifactCardsById.delete(artifactId);
  if (activeArtifactDetail?.dataset.artifactId === artifactId) {
    closeArtifactDetail();
  }
  if (!artifactCardsById.size) {
    renderEmptyArtifactState();
  }
}

function syncArtifactUpdate(element, data) {
  const artifactId = data.artifact_id || element.dataset.artifactId || "";
  const card = artifactCardsById.get(artifactId);
  if (card) {
    updateArtifactCard(card, data);
  }
  if (activeArtifactDetail?.dataset.artifactId === artifactId) {
    updateArtifactDetail(activeArtifactDetail, data);
  } else {
    updateArtifactDetail(element, data);
  }
}

async function handleTemplateSwitchRetry(detail, action) {
  if (action.dataset.switchAction !== "retry") return;
  const messages = detail.querySelector(".revision-chat-messages");
  action.disabled = true;
  action.textContent = "重新生成中";
  appendRevisionChatMessage(messages, "assistant", "正在重新生成新版本，旧版本仍可查看。");
  setTimeline([
    ["保留旧版本", "旧版本仍可打开查看。", "done"],
    ["重新生成新版本", "正在按已确认的玩法重新生成学生游戏。", "active"],
    ["保存结果", "完成后会更新当前作品。", "pending"],
  ]);

  try {
    resetJobLog("已提交");
    const sessionId = await ensureArtifactRevisionSession(detail);
    const result = await applyArtifactRevisionSession(
      sessionId,
      normalizeGenerationMode(extractGenerationModeFromSpec(detail.dataset.spec)),
      detail.dataset.artifactId
    );
    if (!result) return;
    syncArtifactUpdate(detail, result);
    artifactRevisionSessions.set(detail, {
      sessionId,
      analysis: null,
    });
    appendRevisionChatMessage(messages, "assistant", revisionResultTeacherMessage(result));
    setTimeline([
      ["玩法已确认", "已沿用当前新玩法设置。", "done"],
      ["新版本已生成", "玩法已切换，新版本已经可以继续编辑。", "done"],
      ["旧版本保留", "仍可从提示卡片中查看旧版本。", "done"],
    ]);
  } catch (error) {
    appendRevisionChatMessage(messages, "assistant", error.message || "重新生成失败，请稍后再试。");
    setTimeline([["重新生成失败", error.message || "请稍后再试。", "blocked"]]);
  } finally {
    action.disabled = false;
    action.textContent = "重试发布";
  }
}

function parseJsonDataset(value, fallback = {}) {
  try {
    return JSON.parse(value || "");
  } catch {
    return fallback;
  }
}

function formatArtifactDate(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return date.toLocaleString("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function renderLessonAnalysis(card, analysis) {
  const panel = card.querySelector(".lesson-analysis");
  if (!panel) return;

  const game = analysis.recommended_game || {};
  const summaryLine = card.querySelector(".lesson-analysis-material");
  const hasAnalysis = Boolean(analysis.song_name || game.name || analysis.game_stage);
  panel.hidden = !hasAnalysis;
  if (!hasAnalysis) return;

  panel.querySelector(".lesson-game-name").textContent = game.name || "课堂小游戏";
  const materialSummary = analysis.song_material_summary || (analysis.lesson_context || {}).song_material_summary || {};
  if (summaryLine) {
    const parts = [];
    if (materialSummary.enabled) {
      parts.push(`已接入${materialSummary.source_kind || "歌曲材料"}`);
      if (materialSummary.source_filename) parts.push(materialSummary.source_filename);
      if (Number.isFinite(materialSummary.phrase_count) && materialSummary.phrase_count > 0) parts.push(`${materialSummary.phrase_count}个片段`);
      if (materialSummary.has_audio) parts.push("含音频");
      if (materialSummary.used_for_generation) parts.push("已用于生成");
    }
    if (!parts.length && game?.uses_song_material) {
      parts.push("歌曲材料已参与生成");
    }
    summaryLine.textContent = parts.length ? parts.join(" · ") : "";
    summaryLine.hidden = !parts.length;
  }
  const elements = (analysis.music_elements || []).slice(0, 3).join("、") || "综合音乐感知";
  panel.querySelector(".lesson-analysis-summary").textContent =
    `${analysis.song_name || "课例"}，${analysis.grade_band || "小学"}，建议放在${analysis.game_stage || "核心练习环节"}，聚焦${elements}。`;
}

function renderBrainReport(card, brain) {
  const panel = card.querySelector(".brain-report");
  if (!panel) return;

  const critique = brain.self_critique || {};
  const planning = brain.planning || {};
  const hardening = brain.auto_hardening || {};
  const reflection = brain.reflection || {};
  const hasBrain = Boolean(critique.summary || planning.objective || reflection.status);

  panel.hidden = !hasBrain;
  if (!hasBrain) return;

  const score = critique.score ?? "--";
  const verdict = critique.verdict || "unknown";
  panel.dataset.verdict = verdict;
  panel.querySelector(".brain-score").textContent = `自检 ${score} 分`;
  panel.querySelector(".brain-summary").textContent = critique.summary || planning.objective || "已完成规划和自检。";

  const decisions = [
    ...(planning.decisions || []),
    ...(hardening.applied ? hardening.changes || [] : []),
  ].slice(0, 5);
  const actions = [
    ...(critique.risks || []),
    ...(reflection.next_steps || []),
  ].slice(0, 5);

  panel.querySelector(".brain-decisions").innerHTML = renderBrainList(
    decisions.length ? decisions : ["已生成可复核的规划摘要。"]
  );
  panel.querySelector(".brain-actions").innerHTML = renderBrainList(
    actions.length ? actions : ["自检未发现阻断问题。"]
  );
}

function renderModeReport(card, spec, execution) {
  const panel = card.querySelector(".mode-report");
  if (!panel) return;

  const mode = normalizeGenerationMode(spec.generation_mode || execution.generation_mode);
  panel.hidden = false;
  panel.dataset.mode = mode;
  panel.querySelector(".mode-report-mode").textContent = mode === "strict" ? "已优化" : "初版检查";
  panel.querySelector(".mode-report-summary").textContent =
    mode === "strict"
      ? "已完成更完整的运行性检查和教学贴合检查，适合进一步定稿使用。"
      : "已优先确认页面可打开、可操作、可播放；如需更完整检查，可使用下方优化作品。";

  const results = execution.results || {};
  const layers = Array.isArray(execution.validation_layers) && execution.validation_layers.length
    ? execution.validation_layers.map((layer) => ({
      label: layer.label,
      status: layer.status,
      hint: layer.description,
    }))
    : [
      {
        label: "第一层：能不能跑",
        status: combinedLayerStatus(results, ["frontend_artifact_builder", "browser_qa_agent", "code_interpreter"]),
        hint: "页面文件、脚本结构、按钮入口和预览打开。",
      },
      {
        label: "第二层：音乐是否成立",
        status: combinedLayerStatus(results, ["music_logic_agent", "music_tool_calculator"]),
        hint: "旋律、节奏、音色、材料和判定逻辑。",
      },
      {
        label: "第三层：是否贴合教案",
        status: combinedLayerStatus(results, ["lesson_fit_agent"]),
        hint: mode === "fast" ? "初版中更多作为提醒。" : "优化后会更认真拦截跑偏。",
      },
      {
        label: "修复层：是否自动优化",
        status: combinedLayerStatus(results, ["repair_agent", "versioning_agent"]),
        hint: "记录修复、版本保存和剩余风险。",
      },
    ];
  panel.querySelector(".mode-report-layers").innerHTML = layers
    .map((layer) => {
      return `
        <li data-status="${escapeHtml(layer.status)}">
          <span>${escapeHtml(layer.label)}</span>
          <strong>${escapeHtml(executionStatusLabel(layer.status))}</strong>
          <small>${escapeHtml(layer.hint)}</small>
        </li>
      `;
    })
    .join("");
}

function combinedLayerStatus(results, keys) {
  const statuses = keys
    .map((key) => results[key]?.status)
    .filter(Boolean);
  if (!statuses.length) return "skipped";
  if (statuses.includes("failed")) return "failed";
  if (statuses.includes("warning") || statuses.includes("passed_with_warnings")) return "warning";
  if (statuses.includes("repaired")) return "repaired";
  if (statuses.includes("running")) return "running";
  return "passed";
}

function generationModeLabel(mode) {
  return normalizeGenerationMode(mode) === "strict" ? "已优化" : "初版";
}

function renderRuntimeReport(card, spec, execution, payloadRuntimeMarker = {}) {
  const panel = card.querySelector(".runtime-report");
  if (!panel) return;

  const marker = payloadRuntimeMarker?.runtime_source
    ? payloadRuntimeMarker
    : spec.runtime_marker?.runtime_source
      ? spec.runtime_marker
      : execution.runtime_marker || {};
  const musicGame = spec.music_game || {};
  const templateWorkflow = spec.template_workflow || {};
  const templateInstance = spec.template_instance || templateWorkflow.instance || {};
  const templateLabel = musicGame.template_label || templateInstance.template_label || "成熟游戏模板";
  const hasMatchedTemplate = Boolean(
    musicGame.template_id ||
      musicGame.matched_template_id ||
      spec.matched_template_id ||
      spec.template_match?.template_id ||
      templateInstance.template_id
  );
  const isReactRuntime = marker.runtime_source === "react_student_runtime";
  const isTemplateGame = spec.generation_mode === "composed_template_game" || hasMatchedTemplate;

  if (!isReactRuntime && !isTemplateGame) {
    panel.hidden = true;
    return;
  }

  panel.hidden = false;
  panel.dataset.status = isReactRuntime ? "react" : "legacy";
  panel.querySelector(".runtime-status").textContent = isReactRuntime ? `当前玩法：${templateLabel}` : "旧版本";
  panel.querySelector(".runtime-summary").textContent = isReactRuntime
    ? "已生成可试玩版本。后续修改会继续基于这个游戏版本进行。"
    : "这是较早生成的作品。建议重新生成或继续修改成新版游戏。";
}

function renderTemplateSwitchDelivery(card, spec) {
  const panel = card.querySelector(".template-switch-notice");
  if (!panel) return;
  const info = readTemplateSwitchDeliveryInfo(spec);
  if (!info || !info.status) {
    panel.hidden = true;
    return;
  }
  const status = info.status === "failed" ? "需要处理" : "已完成";
  const message =
    info.teacher_message ||
    (info.status === "failed"
      ? "发布没有成功，但旧版本还在，新的玩法设置也已经保留。"
      : "玩法已切换，新版本已经可以继续编辑。");
  panel.hidden = false;
  panel.dataset.status = info.status === "failed" ? "failed" : "published";
  panel.querySelector(".template-switch-notice-status").textContent = status;
  panel.querySelector(".template-switch-notice-message").textContent = message;
  const actions = [
    info.current_version_url ? ["继续编辑新版本", info.current_version_url, "current"] : null,
    info.previous_version_url ? ["查看旧版本", info.previous_version_url, "previous"] : null,
    info.status === "failed" ? ["重试发布", ""] : null,
  ].filter(Boolean);
  panel.querySelector(".template-switch-notice-actions").innerHTML = actions
    .map(([label, href, role]) => {
      if (!href) {
        return `<button type="button" class="template-switch-action" data-switch-action="retry">${escapeHtml(label)}</button>`;
      }
      if (role === "previous") {
        return `<a class="template-switch-action" data-version-role="previous" href="${escapeHtml(href)}" target="_blank" rel="noreferrer">${escapeHtml(label)}</a>`;
      }
      return `<a class="template-switch-action" data-version-role="current" href="${escapeHtml(href)}" target="_blank" rel="noreferrer">${escapeHtml(label)}</a>`;
    })
    .join("");
}

function renderTeacherConfirmationPanel(card, spec) {
  const panel = card.querySelector(".teacher-confirmation-panel");
  if (!panel) return;
  const cards = readTeacherConfirmationCards(spec).filter((item) => item && item.status !== "confirmed");
  if (!cards.length) {
    panel.hidden = true;
    return;
  }
  panel.hidden = false;
  panel.querySelector(".teacher-confirmation-status").textContent = "等待确认";
  panel.querySelector(".teacher-confirmation-list").innerHTML = cards
    .map((item) => {
      const rawValue = JSON.stringify(item.raw_value ?? "");
      return `
        <article class="teacher-confirmation-card">
          <div>
            <strong>${escapeHtml(item.title || "请确认音乐材料")}</strong>
            <p>${escapeHtml(item.teacher_message || "请确认后再用于学生游戏。")}</p>
          </div>
          <dl>
            <div><dt>候选内容</dt><dd>${escapeHtml(item.display_value || "待补充")}</dd></div>
            <div><dt>来源</dt><dd>${escapeHtml(item.source_label || "课堂材料")}</dd></div>
          </dl>
          <div class="teacher-confirmation-actions">
            <button type="button" data-confirmation-action="confirm" data-gate-index="${Number(item.gate_index || 0)}" data-confirmation-value="${escapeHtml(rawValue)}">确认用于游戏</button>
            <button type="button" data-confirmation-action="edit">我来改一下</button>
          </div>
        </article>
      `;
    })
    .join("");
}

function readTeacherConfirmationCards(spec) {
  const handoffCards =
    spec?.frontend_handoff_contract?.presentation_inputs?.music_entity_execution?.teacher_confirmation_cards;
  if (Array.isArray(handoffCards)) return handoffCards;
  const renderCards = spec?.render_spec?.music_entity_execution?.teacher_confirmation_cards;
  if (Array.isArray(renderCards)) return renderCards;
  const workflowCards = spec?.template_workflow?.game_variant_spec?.teacher_confirmation_cards;
  return Array.isArray(workflowCards) ? workflowCards : [];
}

async function handleTeacherConfirmation(detail, action) {
  const kind = action.dataset.confirmationAction || "";
  const messages = detail.querySelector(".revision-chat-messages");
  if (kind === "edit") {
    const input = detail.querySelector(".revision-chat-input");
    if (input) {
      input.value = "我想改一下这张材料确认卡里的候选内容：";
      input.focus();
    }
    appendRevisionChatMessage(messages, "assistant", "可以，直接告诉我你想改成什么，我会先检查当前玩法能不能承接。");
    return;
  }
  if (kind !== "confirm") return;
  action.disabled = true;
  action.textContent = "确认中";
  appendRevisionChatMessage(messages, "assistant", "正在确认音乐材料，并刷新当前试玩版本。");
  setTimeline([
    ["确认材料", "正在把候选内容写入当前游戏。", "active"],
    ["刷新试玩", "确认后会更新当前作品。", "pending"],
  ]);
  try {
    resetJobLog("已提交");
    const sessionId = await ensureArtifactRevisionSession(detail);
    const result = await applyTeacherConfirmationSession(
      sessionId,
      Number(action.dataset.gateIndex || 0),
      action.dataset.confirmationValue || "",
      detail.dataset.artifactId || ""
    );
    if (!result) return;
    syncArtifactUpdate(detail, result);
    artifactRevisionSessions.set(detail, {
      sessionId,
      analysis: null,
    });
    appendRevisionChatMessage(messages, "assistant", result.teacher_confirmation?.teacher_message || "已确认音乐材料，并刷新当前试玩版本。");
    setTimeline([
      ["材料已确认", "候选内容已用于当前游戏。", "done"],
      ["试玩已刷新", "当前作品已经更新。", "done"],
    ]);
  } catch (error) {
    appendRevisionChatMessage(messages, "assistant", error.message || "确认失败，请稍后再试。");
    setTimeline([["确认失败", error.message || "请稍后再试。", "blocked"]]);
  } finally {
    action.disabled = false;
    action.textContent = "确认用于游戏";
  }
}

function renderRevisionVersionContext(card, spec) {
  const panel = card.querySelector(".revision-version-context");
  if (!panel) return;
  const info = readTemplateSwitchDeliveryInfo(spec);
  const musicGame = spec.music_game || {};
  const instance = spec.template_instance || {};
  const label = info.to_template_label || musicGame.template_label || instance.template_label || "";
  if (!info.status && !label) {
    panel.hidden = true;
    return;
  }
  const versionName = info.status === "published" ? `当前新版本：${label || "新玩法"}` : `当前版本：${label || "当前玩法"}`;
  const note =
    info.status === "failed"
      ? "新版本还没有生成成功，后续修改会先保留在当前新玩法设置里。"
      : "后续修改会应用到这个版本；旧版本只用于打开查看。";
  panel.hidden = false;
  panel.setAttribute("aria-label", "当前编辑版本");
  panel.querySelector(".revision-version-name").textContent = versionName;
  panel.querySelector(".revision-version-note").textContent = note;
}

function readTemplateSwitchDeliveryInfo(spec) {
  const source = spec || {};
  return (
    source.frontend_handoff_contract?.presentation_inputs?.template_switch_delivery ||
    source.template_switch_delivery ||
    {}
  );
}

function revisionResultTeacherMessage(result) {
  const feedback = result?.revision_chat_feedback || result?.revision_chat?.feedback || {};
  if (feedback.teacher_message) return feedback.teacher_message;
  if (feedback.status === "applied") return `本次已改：${feedback.applied_summary || "已按你的要求更新当前游戏。"}`;
  if (feedback.status === "needs_clarification" || feedback.status === "no_effect") {
    return feedback.teacher_message || "这次没有改到游戏：请说明要改哪一关、哪种音乐材料、难度或提示方式。";
  }
  const info =
    [readTemplateSwitchDeliveryInfo(result?.spec), readTemplateSwitchDeliveryInfo(result), result?.template_switch_delivery].find(
      (candidate) => candidate?.status || candidate?.teacher_message
    ) || {};
  if (info.teacher_message) return info.teacher_message;
  if (info.status === "failed") return "发布没有成功，但旧版本还在，新的玩法设置也已经保留。";
  if (info.status) return "玩法已切换，新版本已经可以继续编辑。";
  return "修改已经应用完成，可以直接打开预览查看。";
}

function templateRuntimeIsReact(payload) {
  const marker = payload?.runtime_marker || payload?.spec?.runtime_marker || payload?.execution?.runtime_marker || {};
  return marker.runtime_source === "react_student_runtime" && payload?.generation_mode === "composed_template_game";
}

function renderBrainList(items) {
  return items.map((item) => `<li>${escapeHtml(item)}</li>`).join("");
}

function renderExecutionReport(card, execution) {
  const panel = card.querySelector(".execution-report");
  if (!panel) return;

  const hasExecution = Boolean(execution.status || execution.summary);
  panel.hidden = !hasExecution;
  if (!hasExecution) return;

  const status = execution.status || "unknown";
  const mode = normalizeGenerationMode(execution.generation_mode || card.querySelector(".artifact-mode")?.dataset.mode);
  panel.dataset.status = status;
  panel.querySelector(".execution-status").textContent = executionStatusLabel(status);
  panel.querySelector(".execution-summary").textContent = buildExecutionSummaryText(execution, mode);

  const results = execution.results || {};
  const agents = [
    ["frontend_artifact_builder", "页面效果"],
    ["music_logic_agent", "音乐逻辑"],
    ["lesson_fit_agent", "课例贴合"],
    ["browser_qa_agent", "打开预览"],
    ["repair_agent", "自动优化"],
    ["versioning_agent", "版本保存"],
    ["music_tool_calculator", "音乐规则"],
    ["code_interpreter", "代码结构"],
    ["optional_search_agent", "资料补充"],
  ];
  panel.querySelector(".execution-agents").innerHTML = agents
    .filter(([key]) => results[key])
    .map(([key, label]) => {
      const result = results[key] || {};
      return `<li><span>${escapeHtml(label)}</span><strong>${escapeHtml(executionStatusLabel(result.status || "unknown"))}</strong></li>`;
    })
    .join("");
}

function buildExecutionSummaryText(execution, mode) {
  const summary = friendlyEventMessage(
    execution.summary || "已完成页面、音乐逻辑和课堂可用性检查。",
    "execution-orchestrator"
  );
  const layers = Array.isArray(execution.validation_layers) ? execution.validation_layers : [];
  const blockingFailed = layers.filter((layer) => layer?.blocking && layer?.status === "failed");
  const reminderLayers = layers.filter((layer) => !layer?.blocking && ["warning", "failed", "passed_with_warnings"].includes(layer?.status));

  if (normalizeGenerationMode(mode) === "fast" && !blockingFailed.length && reminderLayers.length) {
    return `${summary} 当前增量修改已优先保证页面可用，课例贴合和教学完整度中的剩余问题暂作为提醒保留。`;
  }
  return summary;
}

function renderUpgradePanel(card, spec, execution, lessonAnalysis, brain) {
  const panel = card.querySelector(".upgrade-panel");
  const statusNode = card.querySelector(".upgrade-status");
  const summaryNode = card.querySelector(".upgrade-summary");
  const focusList = card.querySelector(".upgrade-focus-list");
  const button = card.querySelector(".upgrade-button");
  if (!panel || !statusNode || !summaryNode || !focusList || !button) return;

  const mode = normalizeGenerationMode(spec.generation_mode || execution.generation_mode);
  const failedAgents = collectExecutionAgentLabels(execution, ["failed"]);
  const warningAgents = collectExecutionAgentLabels(execution, ["warning", "passed_with_warnings"]);
  const hasLessonContext = Boolean(lessonAnalysis && Object.keys(lessonAnalysis).length);
  const canUpgrade = mode === "fast";

  panel.hidden = !canUpgrade && mode !== "strict";
  panel.dataset.state = canUpgrade ? "ready" : "done";
  statusNode.textContent = canUpgrade ? "可优化" : "已优化";
  summaryNode.textContent = canUpgrade
    ? buildUpgradeSummary(execution.summary || "", failedAgents, warningAgents, hasLessonContext, brain)
    : "当前作品已经完成优化，后续修改会继续沿用现有页面做小步精修。";
  focusList.innerHTML = UPGRADE_FOCUS_ITEMS.map((item) => `<li>${escapeHtml(item)}</li>`).join("");
  button.hidden = !canUpgrade;
  button.disabled = !canUpgrade;
  button.textContent = "优化作品";
}

function buildUpgradeSummary(executionSummary, failedAgents, warningAgents, hasLessonContext, brain) {
  const parts = [
    "基于当前结果继续优化，保留页面结构、交互方式、视觉风格和已通过功能，不会从零重做。",
  ];
  if (executionSummary) {
    parts.push(`当前验收摘要：${executionSummary}`);
  }
  if (failedAgents.length) {
    parts.push(`优先补齐阻断项：${failedAgents.join("、")}。`);
  } else if (warningAgents.length) {
    parts.push(`当前主要提醒项：${warningAgents.join("、")}。`);
  }
  if (hasLessonContext) {
    parts.push("优化时会继承当前教案分析结果与生成摘要，重点补课堂贴合、学习闭环和课堂迁移。");
  }
  if (brain?.self_critique?.summary) {
    parts.push(`生成摘要：${brain.self_critique.summary}`);
  }
  return parts.join("");
}

function collectExecutionAgentLabels(execution, statuses) {
  const results = execution?.results || {};
  const mapping = [
    ["frontend_artifact_builder", "页面效果"],
    ["music_logic_agent", "音乐逻辑"],
    ["lesson_fit_agent", "课例贴合"],
    ["browser_qa_agent", "打开预览"],
    ["repair_agent", "自动优化"],
    ["versioning_agent", "版本保存"],
    ["music_tool_calculator", "音乐规则"],
    ["code_interpreter", "代码结构"],
    ["optional_search_agent", "资料补充"],
  ];
  return mapping.filter(([key]) => statuses.includes(results[key]?.status)).map(([, label]) => label);
}

function executionStatusLabel(status) {
  const labels = {
    passed: "通过",
    passed_with_warnings: "有提醒",
    warning: "提醒",
    failed: "失败",
    repaired: "已修复",
    skipped: "跳过",
    running: "执行中",
    unknown: "未知",
  };
  return labels[status] || status;
}

function bindRevisionForm(card) {
  const form = card.querySelector(".revision-form");
  const input = card.querySelector(".revision-input");
  const button = form.querySelector("button");
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const revision = input.value.trim();
    if (!revision) {
      input.focus();
      return;
    }

    button.disabled = true;
    button.textContent = "生成中";
    setTimeline([
      ["读取工具", "理解修改要求。", "active"],
      ["增量修改", "保留原页面，只改指定部分。", "pending"],
      ["更新工具", "写回当前页面文件。", "pending"],
    ]);

    const result = await reviseArtifact(
      card.dataset.spec,
      revision,
      card.dataset.filePath,
      card.dataset.pageUrl,
      card.dataset.artifactId
    );
    button.disabled = false;
    button.textContent = "提交修改";

    if (!result) return;
    input.value = "";
    setTimeline([
      ["修改要求已确认", revision, "done"],
      ["工具已更新", `已完成增量修改。自检 ${result.brain?.self_critique?.score ?? "--"} 分。`, "done"],
      ["可以预览", "打开当前工具查看。", "done"],
    ]);
    syncArtifactUpdate(card, result);
  });
}

function bindRevisionChat(card) {
  const form = card.querySelector(".revision-chat-form");
  const input = card.querySelector(".revision-chat-input");
  const sendButton = card.querySelector(".revision-chat-send");
  const applyButton = card.querySelector(".revision-chat-apply");
  const messages = card.querySelector(".revision-chat-messages");
  if (!form || !input || !sendButton || !applyButton || !messages) return;

  const handleSend = async (event) => {
    event.preventDefault();
    event.stopPropagation();
    const message = input.value.trim();
    if (!message) {
      input.focus();
      return;
    }

    appendRevisionChatMessage(messages, "user", message);
    input.value = "";
    sendButton.disabled = true;
    const loading = appendRevisionChatMessage(messages, "assistant", "正在理解你的修改意图。", true);

    try {
      const sessionId = await ensureArtifactRevisionSession(card);
      const result = await sendArtifactRevisionMessage(sessionId, message);
      loading.remove();
      const analysis = result.analysis || {};
      appendRevisionChatMessage(messages, "assistant", analysis.reply || "我已经理解了这次修改方向。");
      artifactRevisionSessions.set(card, {
        sessionId,
        analysis,
      });
      applyButton.disabled = !analysis.revision_instruction;
      if (analysis.clarifying_question) {
        appendRevisionChatMessage(messages, "assistant", analysis.clarifying_question);
      }
    } catch (error) {
      loading.remove();
      appendRevisionChatMessage(messages, "assistant", error.message || "没有理解成功，请换一种说法。");
    } finally {
      sendButton.disabled = false;
    }
  };

  form.addEventListener("submit", handleSend);
  sendButton.addEventListener("click", handleSend);

  applyButton.addEventListener("click", async () => {
    const session = artifactRevisionSessions.get(card);
    if (!session?.sessionId) return;

    applyButton.disabled = true;
    const progressMessage = appendRevisionChatMessage(messages, "assistant", "正在读取当前作品。", true);
    setTimeline([
      ["整理修改", "修改助手已整理你的要求。", "done"],
      ["更新作品", "正在按你的要求更新当前作品。", "active"],
      ["保存结果", "保存到当前作品。", "pending"],
    ]);

    try {
      resetJobLog("已提交");
      const result = await applyArtifactRevisionSession(
        session.sessionId,
        normalizeGenerationMode(extractGenerationModeFromSpec(card.dataset.spec)),
        card.dataset.artifactId,
        {
          onProgress: (event, job) => {
            updateRevisionChatMessage(progressMessage, revisionProgressMessage(event, job?.status));
          },
        }
      );
      if (!result) return;
      syncArtifactUpdate(card, result);
      artifactRevisionSessions.set(card, {
        sessionId: session.sessionId,
        analysis: null,
      });
      applyButton.disabled = true;
      updateRevisionChatMessage(progressMessage, "修改已保存，可以打开当前作品查看。");
      progressMessage.classList.remove("loading");
      appendRevisionChatMessage(messages, "assistant", revisionResultTeacherMessage(result));
      setTimeline([
        ["修改说明已确认", "修改助手已完成整理。", "done"],
        ["作品已更新", `已按要求完成修改。自检 ${result.brain?.self_critique?.score ?? "--"} 分。`, "done"],
        ["可以预览", "打开当前作品查看。", "done"],
      ]);
    } catch (error) {
      updateRevisionChatMessage(progressMessage, error.message || "应用修改失败。");
      progressMessage.classList.remove("loading");
      appendRevisionChatMessage(messages, "assistant", error.message || "应用修改失败。");
      setTimeline([["修改失败", error.message || "请稍后再试。", "blocked"]]);
    } finally {
      applyButton.disabled = !artifactRevisionSessions.get(card)?.analysis?.revision_instruction;
    }
  });
}

function bindUpgradeButton(card) {
  const button = card.querySelector(".upgrade-button");
  const panel = card.querySelector(".upgrade-panel");
  const statusNode = card.querySelector(".upgrade-status");
  if (!button || !panel || !statusNode) return;

  button.addEventListener("click", async () => {
    button.disabled = true;
    button.hidden = false;
    button.textContent = "优化中";
    panel.dataset.state = "running";
    statusNode.textContent = "优化中";
    setTimeline([
      ["读取当前作品", "继承当前页面、结构、风格和已通过项。", "done"],
      ["优化作品", "补真实音色、音乐证据、学习闭环、课堂迁移和阻断项。", "active"],
      ["更新当前作品", "在现有结果上做最小必要增强。", "pending"],
    ]);

    try {
      resetJobLog("已提交");
      const result = await upgradeArtifact(card);
      if (!result) return;
      syncArtifactUpdate(card, result);
      setTimeline([
        ["读取当前作品", "已继承当前结果。", "done"],
        ["优化作品", `已完成优化。自检 ${result.brain?.self_critique?.score ?? "--"} 分。`, "done"],
        ["可以预览", "打开当前工具查看优化后的版本。", "done"],
      ]);
    } catch (error) {
      panel.dataset.state = "ready";
      statusNode.textContent = "可优化";
      button.disabled = false;
      button.textContent = "优化作品";
      setTimeline([["优化失败", error.message || "请稍后再试。", "blocked"]]);
    }
  });
}

async function ensureArtifactRevisionSession(card) {
  const existing = artifactRevisionSessions.get(card);
  if (existing?.sessionId) return existing.sessionId;

  const payload = new FormData();
  payload.append("current_spec", card.dataset.spec || "{}");
  payload.append("current_file_path", card.dataset.filePath || "");
  payload.append("current_page_url", card.dataset.pageUrl || "");
  payload.append("current_artifact_id", card.dataset.artifactId || "");
  const response = await fetch("/api/agent/artifact-revision/session", {
    method: "POST",
    body: payload,
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "无法创建修改会话");
  }
  artifactRevisionSessions.set(card, {
    sessionId: data.session_id,
    analysis: null,
  });
  return data.session_id;
}

async function sendArtifactRevisionMessage(sessionId, message) {
  const payload = new FormData();
  payload.append("message", message);
  const response = await fetch(`/api/agent/artifact-revision/session/${encodeURIComponent(sessionId)}/message`, {
    method: "POST",
    body: payload,
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "修改理解失败");
  }
  return data;
}

async function applyArtifactRevisionSession(sessionId, generationMode = "strict", artifactId = "", options = {}) {
  const payload = new FormData();
  payload.append("force_local", "false");
  payload.append("generation_mode", normalizeGenerationMode(generationMode));
  payload.append("current_artifact_id", artifactId || "");
  const response = await fetch(`/api/agent/artifact-revision/session/${encodeURIComponent(sessionId)}/apply-job`, {
    method: "POST",
    body: payload,
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "应用修改失败");
  }
  if (!data.job_id) return data;
  return await waitForJob(data.job_id, "应用对话修改", options);
}

async function applyTeacherConfirmationSession(sessionId, gateIndex, confirmedValue = "", artifactId = "") {
  const payload = new FormData();
  payload.append("gate_index", String(gateIndex));
  payload.append("confirmed_value", confirmedValue || "");
  payload.append("current_artifact_id", artifactId || "");
  const response = await fetch(`/api/agent/artifact-revision/session/${encodeURIComponent(sessionId)}/teacher-confirmation/apply-job`, {
    method: "POST",
    body: payload,
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "确认材料失败");
  }
  if (!data.job_id) return data;
  return await waitForJob(data.job_id, "确认音乐材料");
}

function appendRevisionChatMessage(container, role, text, loading = false) {
  const message = document.createElement("article");
  message.className = `revision-chat-message ${role}${loading ? " loading" : ""}`;
  message.innerHTML = `
    <span>${role === "user" ? "我的修改" : "修改助手"}</span>
    <p>${escapeHtml(text).replaceAll("\n", "<br />")}</p>
  `;
  container.appendChild(message);
  container.scrollTop = container.scrollHeight;
  return message;
}

function updateRevisionChatMessage(message, text) {
  if (!message) return;
  const body = message.querySelector("p");
  if (!body) return;
  body.innerHTML = escapeHtml(text).replaceAll("\n", "<br />");
  const container = message.closest(".revision-chat-messages");
  if (container) {
    container.scrollTop = container.scrollHeight;
  }
}

function revisionProgressMessage(event, status = "") {
  if (status === "completed") return "修改已保存，可以打开当前作品查看。";
  return friendlyEventMessage(event?.message || `${REVISION_PROGRESS_FALLBACKS[2]}。`, event?.agent || "revision-progress", status);
}

async function reviseArtifact(currentSpec, revision, currentFilePath, currentPageUrl, artifactId = "") {
  const payload = new FormData();
  payload.append("current_spec", currentSpec);
  payload.append("revision", revision);
  payload.append("current_file_path", currentFilePath || "");
  payload.append("current_page_url", currentPageUrl || "");
  payload.append("current_artifact_id", artifactId || "");
  payload.append("force_local", "false");
  payload.append("generation_mode", normalizeGenerationMode(extractGenerationModeFromSpec(currentSpec)));

  try {
    resetJobLog("已提交");
    const response = await fetch("/api/agent/revise-webpage-job", {
      method: "POST",
      body: payload,
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "修改失败");
    }
    if (!data.job_id) return data;
    return await waitForJob(data.job_id, "修改当前工具");
  } catch (error) {
    setTimeline([["修改失败", error.message || "请写得更具体一点。", "blocked"]]);
    return null;
  }
}

async function upgradeArtifact(card) {
  const payload = new FormData();
  payload.append("current_spec", card.dataset.spec || "{}");
  payload.append("current_file_path", card.dataset.filePath || "");
  payload.append("current_page_url", card.dataset.pageUrl || "");
  payload.append("current_artifact_id", card.dataset.artifactId || "");
  payload.append("current_execution", card.dataset.execution || "{}");
  payload.append("current_lesson_analysis", card.dataset.lessonAnalysis || "{}");
  payload.append("current_brain", card.dataset.brain || "{}");
  payload.append("force_local", "false");

  const response = await fetch("/api/agent/upgrade-webpage-job", {
    method: "POST",
    body: payload,
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "优化失败");
  }
  if (!data.job_id) return data;
  return await waitForJob(data.job_id, "升级当前作品");
}

async function waitForJob(jobId, label, options = {}) {
  let lastEventCount = 0;
  let missingCount = 0;
  const terminalFailures = new Set(["failed", "timeout", "cancelled", "dead_letter"]);
  for (;;) {
    const response = await fetch(`/api/agent/jobs/${encodeURIComponent(jobId)}`);
    const job = await response.json();
    if (!response.ok) {
      missingCount += 1;
      if (response.status === 404 && missingCount < 8) {
        setTimeline([
          [label, "正在恢复后台任务状态，请稍等。", "active"],
          ["后台状态", "同步中", "pending"],
        ]);
        await sleep(900);
        continue;
      }
      throw new Error(job.error || "后台任务丢失");
    }
    missingCount = 0;

    renderJobLog(job);
    const events = job.events || [];
    if (events.length !== lastEventCount) {
      const latest = events[events.length - 1];
      if (latest) {
        const isFailedTerminal = terminalFailures.has(job.status);
        options.onProgress?.(latest, job);
        setTimeline([
          [label, friendlyEventMessage(latest.message, latest.agent, job.status), isFailedTerminal ? "blocked" : job.status === "completed" ? "done" : "active"],
          ["后台状态", jobStatusLabel(job.status), job.status === "completed" ? "done" : isFailedTerminal ? "blocked" : "pending"],
        ]);
      }
      lastEventCount = events.length;
    }

    if (job.status === "completed") {
      return job.result;
    }
    if (terminalFailures.has(job.status)) {
      throw new Error(job.error || "后台执行失败");
    }
    await sleep(900);
  }
}

function resetJobLog(status = "等待中") {
  if (!jobLog) return;
  showGenerationStatusPanel("queued");
  jobLog.hidden = false;
  jobLogStatus.textContent = status;
  jobLog.dataset.status = "queued";
  jobLogList.innerHTML = "";
}

function renderJobLog(job) {
  if (!jobLog) return;
  showGenerationStatusPanel(job.status || "running");
  jobLog.hidden = false;
  jobLogStatus.textContent = jobStatusLabel(job.status);
  jobLog.dataset.status = job.status || "unknown";
  if (generationStatusPanel) {
    generationStatusPanel.dataset.status = job.status || "unknown";
  }
  jobLogList.innerHTML = (job.events || [])
    .slice(-18)
    .map((event) => {
      const time = event.time ? new Date(event.time).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }) : "";
      return `
        <li class="${escapeHtml(event.level || "info")}">
          <span>${escapeHtml(time)}</span>
          <strong>${escapeHtml(friendlyAgentLabel(event.agent))}</strong>
          <p>${escapeHtml(friendlyEventMessage(event.message, event.agent, job.status))}</p>
        </li>
      `;
    })
    .join("");
}

function friendlyAgentLabel(agent) {
  const labels = {
    "lesson-game-designer": "教案分析",
    "model-gateway": "需求整理",
    "agent-brain": "课堂规划",
    "revision-progress": "修改进度",
    "frontend-artifact-builder": "页面生成",
    "opencode-runtime": "页面生成",
    "execution-orchestrator": "质量检查",
    system: "系统",
  };
  return labels[agent] || "生成助手";
}

function friendlyEventMessage(message, agent, status = "") {
  const text = String(message || "");
  if (status === "timeout") return "后台执行超时了。";
  if (status === "cancelled") return "后台任务已取消。";
  if (status === "dead_letter") return "任务已停止自动重试。";
  if (agent === "revision-progress") {
    return text || "正在更新当前游戏。";
  }
  if (agent === "frontend-artifact-builder") {
    if (text.includes("恢复")) return "已补齐页面的可操作区域。";
    if (text.includes("生成")) return "页面主体已生成。";
    return "正在确认页面可用。";
  }
  if (agent === "execution-orchestrator") {
    if (text.includes("完成")) return "质量检查完成。";
    return "正在检查页面、音乐逻辑和课堂可用性。";
  }
  if (agent === "opencode-runtime") {
    if (text.includes("结束")) return "页面生成完成。";
    return "正在生成页面。";
  }
  if (text.includes("OpenCode")) {
    return text.includes("结束") ? "页面生成完成。" : "正在生成页面。";
  }
  if (text.includes("多智能体执行层") || text.includes("代码解释器")) {
    return text.replace("多智能体执行层", "质量检查").replace("代码解释器", "课堂逻辑检查");
  }
  if (text.includes("frontend_artifact_builder") || text.includes("frontend-artifact-builder")) {
    return "页面生成检查完成。";
  }
  if (text.includes("任务包")) {
    return "正在整理生成信息。";
  }
  return text;
}

function jobStatusLabel(status) {
  const labels = {
    queued: "排队中",
    running: "执行中",
    completed: "已完成",
    failed: "失败",
    cancelled: "已取消",
    dead_letter: "失败",
    timeout: "超时",
  };
  return labels[status] || status || "未知";
}

function sleep(ms) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

function bindTemplateConfigBridge() {
  window.addEventListener("message", (event) => {
    if (event.origin !== window.location.origin) return;
    if (event.data?.type === "buyilehu-template-console-ready") {
      const sourceFrame = getTemplateFrames().find((frame) => frame.contentWindow === event.source);
      if (sourceFrame?.dataset.templateContext === "lesson") {
        sendLessonTemplateState(sourceFrame);
      }
      return;
    }
    if (event.data?.type === "buyilehu-template-config" && event.data.config) {
      const sourceFrame = getTemplateFrames().find((frame) => frame.contentWindow === event.source);
      const activePage = document.body.dataset.activePage || "home";
      if (sourceFrame && !sourceFrame.closest(".lesson-config-modal") && !sourceFrame.closest(`[data-page="${activePage}"]`)) return;
      const context = sourceFrame?.dataset.templateContext === "lesson" ? "lesson" : "direct";
      activeTemplateConfigs[context] = event.data.config;
    }
  });
}

function getTemplateFrames() {
  return Array.from(document.querySelectorAll(".agent-template-frame"));
}

function sendLessonTemplateState(lessonFrame) {
  if (!lessonFrame?.contentWindow) return;
  if (activeLessonRecommendation) {
    lessonFrame.contentWindow.postMessage(
      {
        type: "buyilehu-load-lesson-recommendation",
        recommendation: activeLessonRecommendation,
      },
      window.location.origin
    );
  }
  if (activeTemplateConfigs.lesson) {
    lessonFrame.contentWindow.postMessage(
      {
        type: "buyilehu-load-template-config",
        config: activeTemplateConfigs.lesson,
      },
      window.location.origin
    );
  }
}

async function syncLessonTemplateConfig(proposalId) {
  if (!proposalId) return;
  try {
    const response = await fetch("/api/workflows/lesson-game/plan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ proposal_id: proposalId }),
    });
    const data = await response.json();
    if (!response.ok) return;
    const workflow = data.workflow || {};
    const instance = workflow.instance || {};
    const proposalCard = workflow.proposal_card || {};
    const lessonFit = workflow.source?.lesson_fit || proposalCard.lesson_fit || {};
    const templateHint = lessonFit.template_hint || {};
    const adjustmentContract =
      workflow.source?.music_element_adjustment_contract ||
      lessonFit.music_element_adjustment_contract ||
      data.music_element_adjustment_contract ||
      {};
    const lessonRecommendation = {
      matched: Boolean(instance.template_id),
      template_id: instance.template_id || "",
      template_label: instance.template_label || proposalCard.template_label || "",
      selected_skin_id: workflow.template_fidelity_contract?.selected_skin_id || instance.config?.skin_id || "",
      selected_skin_label: instance.skin?.label || "",
      skin_selection_source: workflow.template_fidelity_contract?.skin_selection_source || "",
      skins: workflow.template_fidelity_contract?.allowed_skin_ids?.map((skinId) => ({ skin_id: skinId })) || [],
      lesson_focus: proposalCard.music_element || lessonFit.lesson_evidence?.music_element || "",
      lesson_stage: lessonFit.lesson_evidence?.target_stage || "",
      fit_summary: proposalCard.fit_summary || lessonFit.fit_summary || "",
      reason: templateHint.reason || "",
      match_status: templateHint.match_status || (instance.template_id ? "exact" : "unmatched"),
      music_element_adjustment_contract: adjustmentContract,
    };
    activeLessonRecommendation = lessonRecommendation;
    const lessonFrame = getTemplateFrames().find((frame) => frame.dataset.templateContext === "lesson");
    if (!lessonFrame) return;
    bindLessonFrameToProposal(proposalId);

    const config = instance.config;
    if (!config || !instance.template_id) {
      activeTemplateConfigs.lesson = null;
      syncLessonFrameWhenReady(lessonFrame);
      return;
    }
    activeTemplateConfigs.lesson = config;
    syncLessonFrameWhenReady(lessonFrame);
  } catch {
    // The teacher can still configure manually if the recommendation preview is unavailable.
  }
}

function setTimeline(items) {
  showGenerationStatusPanel(inferTimelineStatus(items));
  timeline.innerHTML = items
    .map(([title, body, state]) => {
      return `
        <article class="timeline-item ${escapeHtml(state)}">
          <strong>${escapeHtml(title)}</strong>
          <p>${escapeHtml(body)}</p>
        </article>
      `;
    })
    .join("");
}

function showGenerationStatusPanel(status = "active") {
  if (!generationStatusPanel) return;
  generationStatusPanel.hidden = false;
  generationStatusPanel.dataset.status = status || "active";
  if (generationStatusPill) {
    generationStatusPill.textContent = generationStatusLabel(status);
  }
}

function inferTimelineStatus(items) {
  const states = (items || []).map((item) => item?.[2]).filter(Boolean);
  if (states.includes("blocked")) return "failed";
  if (states.includes("active")) return "running";
  if (states.length && states.every((state) => state === "done")) return "completed";
  return "queued";
}

function generationStatusLabel(status) {
  const terminalFailures = new Set(["failed", "timeout", "cancelled", "dead_letter"]);
  if (status === "completed") return "已完成";
  if (status === "queued" || status === "pending") return "排队中";
  if (status === "running" || status === "active") return "生成中";
  if (terminalFailures.has(status)) return "需要处理";
  return "生成中";
}

function hidePolishPanel() {
  polishPanel.hidden = true;
}

async function loadRuntimeIdentity() {
  if (!runtimeBadge) return;
  runtimeBadge.remove();
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
