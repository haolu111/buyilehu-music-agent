import { createServer } from "node:http";
import { mkdirSync, writeFileSync } from "node:fs";
import { access, mkdtemp, readFile, rm, stat } from "node:fs/promises";
import { extname, join, resolve } from "node:path";
import { spawn } from "node:child_process";
import { setTimeout as delay } from "node:timers/promises";
import { fileURLToPath } from "node:url";
import { tmpdir } from "node:os";

const root = resolve(fileURLToPath(new URL("..", import.meta.url)));
const distDir = join(root, "dist");
const appStaticAssetsDir = resolve(root, "..", "app", "static", "assets");
const snapshotsDir = join(root, "tests", "browser-snapshots");
const reportPath = join(root, "tests", "browser-smoke-primary-activity.json");

const VIEWPORTS = [
  { name: "desktop", width: 1366, height: 900, mobile: false },
];

const SMOKE_TARGETS = [
  {
    id: "primary-activity",
    path: "/template-console/primary-activity-preview.html",
    rootSelector: "#primary-activity-root",
    screenshotPrefix: "primary-activity",
    beforeTexts: ["教师控制", "小学节奏热身", "节拍播放器", "节拍轨道", "节奏卡片", "虚拟乐器", "已落地教具", "稳定拍检查", "教师提示"],
    h1Text: "小学节奏热身",
    actionExpression: `document.querySelector('[aria-label="敲击节奏垫"]')?.click(); true`,
    afterText: "已敲 1 次",
    extraChecks: (before, after) => {
      const failures = [];
      if (!before.teacher_control_visible) failures.push("teacher control not visible");
      if (!before.rhythm_pad_visible) failures.push("rhythm pad not visible");
      if (!before.body_text.includes("至少记录 3 次拍点")) failures.push("missing tempo stability collection prompt");
      if (!after.body_text.includes("已敲 1 次")) failures.push("tap feedback did not update");
      if (!/稳定拍记录\s*1\s*次/.test(after.body_text)) failures.push("tempo stability tap record did not update");
      return failures;
    },
  },
  {
    id: "primary-library",
    path: "/template-console/primary-library.html",
    rootSelector: "#primary-library-root",
    screenshotPrefix: "primary-library",
    beforeTexts: ["音乐课堂活动库", "小学活动模板", "音乐教育依据", "音乐教育基础库", "审美感知", "学生音乐实践", "玩法模板目录", "rhythm_echo_core", "成熟运行", "body_percussion_core", "活动页就绪", "交互组件库", "game_hud", "answer_choice_grid", "not_standalone_game", "音乐规则与判定库", "rhythm_timing_judgement", "music_reason", "teacher_suggestion", "虚拟教具库", "instrument_cards", "生成乐器皮肤", "mood_picture_cards", "本地 image2 PNG", "虚拟乐器库", "tambourine", "first_user_click_required", "pitch_limited_to_material", "素材包模板", "generated_playable_instrument_pack", "生成 PNG 文件验收通过", "微活动模板", "one_minute_beat_check", "listen_once_vote", "材料实体解析库", "lesson_objective", "audio_clip", "missing_values_must_stay_missing", "材料绑定模板", "lyrics_rhythm_binder", "评价与记录模板", "tap_accuracy_record", "自适应模板", "slow_down_when_many_late", "投屏与导出模板", "projector_activity_view", "特殊课堂场景模板", "substitute_teacher_mode", "教师控制包", "tempo_control_pack", "teacher_priority_over_auto_adaptive", "visible_reason_required", "乐器听辨音频包", "primary_instrument_audio_pack", "外部生图兼容队列", "music_mood_picture_pack", "classroom_character_pack"],
    h1Text: "音乐课堂活动库",
    actionExpression: `true`,
    afterText: "外部生图兼容队列",
    extraChecks: (before) => {
      const failures = [];
      if (!before.body_text.includes("新增乐器必须先生成独立 PNG")) failures.push("missing generated asset save policy");
      if (!before.body_text.includes("本轮模板库固定图片资产用本地 image2 生成并入库")) failures.push("missing image2 material policy");
      if (!before.body_text.includes("采样优先演奏，近似音色必须标注")) failures.push("missing sampled playback policy");
      if (!before.body_text.includes("近似采样待补")) failures.push("missing approximate sample disclosure");
      if (!before.body_text.includes("SoundFont")) failures.push("missing instrument audio source kind");
      if (!before.body_text.includes("先判定教学目标")) failures.push("missing music education foundation panel");
      if (!before.body_text.includes("只让学生抢答")) failures.push("missing core competency avoid guidance");
      if (!before.body_text.includes("区分成熟运行")) failures.push("missing gameplay template status panel");
      if (!before.body_text.includes("核心循环")) failures.push("missing gameplay template core loop");
      if (!before.body_text.includes("React / Radix / dnd-kit / WebAudio")) failures.push("missing component library panel");
      if (!before.body_text.includes("空状态")) failures.push("missing component empty state contract");
      if (!before.body_text.includes("形成性反馈")) failures.push("missing music rule panel");
      if (!before.body_text.includes("student_feedback")) failures.push("missing music rule feedback contract");
      if (!before.body_text.includes("生成图只作为库乐队式演奏界面皮肤")) failures.push("missing asset pack template authenticity policy");
      if (!before.body_text.includes("替代实体教具")) failures.push("missing virtual teaching aid panel");
      if (!before.body_text.includes("generated_instrument_skin_visible")) failures.push("missing generated instrument skin gate");
      if (!before.body_text.includes("image_gen_png_file_verified")) failures.push("missing teaching aid image_gen gate");
      if (!before.body_text.includes("音频解锁 / 事件记录 / 教师控制")) failures.push("missing virtual instrument panel");
      if (!before.body_text.includes("group_controls_apply")) failures.push("missing virtual instrument group control gate");
      if (!before.body_text.includes("classroom_stage_background_pack")) failures.push("missing classroom background asset pack template");
      if (!before.body_text.includes("classroom_character_pack")) failures.push("missing classroom character asset pack");
      if (!before.body_text.includes("1 到 8 分钟快速插入课堂")) failures.push("missing micro activity template panel");
      if (!before.body_text.includes("全班投票结果可显示")) failures.push("missing listen once vote micro activity");
      if (!before.body_text.includes("教案先解析，缺项不编造")) failures.push("missing material entity parser panel");
      if (!before.body_text.includes("missing_values_must_stay_missing")) failures.push("missing material entity do-not-invent policy");
      if (!before.body_text.includes("教案材料到游戏组件")) failures.push("missing material binder panel");
      if (!before.body_text.includes("timbre_pool_binder")) failures.push("missing timbre material binder");
      if (!before.body_text.includes("课堂结果可导出")) failures.push("missing assessment record panel");
      if (!before.body_text.includes("exit_ticket_record")) failures.push("missing exit ticket record template");
      if (!before.body_text.includes("教师可见，可撤回")) failures.push("missing adaptive template panel");
      if (!before.body_text.includes("suggest_next_activity")) failures.push("missing next activity adaptive template");
      if (!before.body_text.includes("课堂交付产物")) failures.push("missing delivery template panel");
      if (!before.body_text.includes("classroom_result_export")) failures.push("missing classroom result export template");
      if (!before.body_text.includes("真实课堂模式")) failures.push("missing scenario template panel");
      if (!before.body_text.includes("festival_music_pack")) failures.push("missing festival scenario template");
      if (!before.body_text.includes("教师优先于自动自适应")) failures.push("missing teacher control priority contract");
      if (!before.body_text.includes("projector_safe")) failures.push("missing teacher control projector safety");
      return failures;
    },
  },
  {
    id: "instrument-family",
    path: "/template-console/instrument-family-preview.html",
    rootSelector: "#instrument-family-root",
    screenshotPrefix: "instrument-family",
    beforeTexts: ["乐器家族分类", "先听乐器声音", "选择乐器家族", "选择听到的依据", "教师观察点", "生成乐器皮肤", "小鼓"],
    h1Text: "乐器家族分类",
    actionExpressions: [
      `document.querySelector('[aria-label="播放乐器声音"]')?.click(); true`,
      `
        [...document.querySelectorAll('.family-choice-grid button')].find((node) => node.textContent.includes('吹奏'))?.click();
        [...document.querySelectorAll('.evidence-chip-grid button')].find((node) => node.textContent.includes('气息感'))?.click();
        true
      `,
    ],
    afterText: "属于吹奏",
    extraChecks: (before, after) => {
      const failures = [];
      if (!before.body_text.includes("先听再分")) failures.push("missing listen-first status");
      if (before.body_text.includes("不使用假图标")) failures.push("default instrument set still has pending real photos");
      if (!after.body_text.includes("笛子属于吹奏")) failures.push("instrument family feedback did not update");
      if (!after.body_text.includes("提交分类")) failures.push("missing submit action");
      return failures;
    },
  },
  {
    id: "lyrics-rhythm",
    path: "/template-console/lyrics-rhythm-preview.html",
    rootSelector: "#lyrics-rhythm-root",
    screenshotPrefix: "lyrics-rhythm",
    beforeTexts: ["歌词节奏训练", "小雨沙沙", "听后拍回", "开始训练：先听示范", "听示范", "拍回来", "看反馈", "本句节奏谱"],
    h1Text: "歌词节奏",
    actionExpressions: [
      `
        [...document.querySelectorAll('.lyrics-list button')].find((node) => node.textContent.includes('种子发芽'))?.click();
        true
      `,
    ],
    afterText: "种子发芽",
    extraChecks: (before, after) => {
      const failures = [];
      if (!before.body_text.includes("开始训练：先听示范")) failures.push("missing visible classroom training action");
      if (!before.body_text.includes("教师信息与审核记录")) failures.push("missing teacher review drawer");
      if (!after.body_text.includes("乐句 2/2")) failures.push("lyrics rhythm did not move to second phrase");
      if (!after.body_text.includes("96 BPM")) failures.push("phrase-specific bpm did not update");
      return failures;
    },
  },
  {
    id: "strong-weak-beat",
    path: "/template-console/strong-weak-beat-preview.html",
    rootSelector: "#strong-weak-beat-root",
    screenshotPrefix: "strong-weak-beat",
    beforeTexts: ["强弱拍律动", "强拍", "弱拍", "网页反馈", "练习主操作", "开始练习：先听示范"],
    h1Text: "强弱拍律动",
    actionExpressions: [
      `[...document.querySelectorAll('button')].find((node) => node.textContent.includes('开始练习：先听示范'))?.click(); true`,
    ],
    afterText: "正在播放示范",
    extraChecks: (before, after) => {
      const failures = [];
      if (!before.body_text.includes("先用网页判断强弱拍")) failures.push("missing strong/weak body movement pedagogy");
      if (!after.body_text.includes("正在播放示范")) failures.push("listening stage did not start");
      return failures;
    },
  },
  {
    id: "steady-beat-walk",
    path: "/template-console/steady-beat-walk-preview.html",
    rootSelector: "#steady-beat-walk-root",
    screenshotPrefix: "steady-beat-walk",
    beforeTexts: ["稳定拍行走", "先听稳定拍", "走一步", "拍手", "停住", "稳定拍检查", "行走记录"],
    h1Text: "稳定拍行走",
    actionExpressions: [
      `document.querySelector('[aria-label="播放稳定拍行走"]')?.click(); true`,
      `
        [...document.querySelectorAll('.steady-walk-action-panel button')].find((node) => node.textContent.includes('走一步'))?.click();
        true
      `,
      `
        [...document.querySelectorAll('.steady-walk-action-panel button')].find((node) => node.textContent.includes('拍手'))?.click();
        true
      `,
      `
        [...document.querySelectorAll('.steady-walk-action-panel button')].find((node) => node.textContent.includes('停住'))?.click();
        true
      `,
    ],
    afterText: "稳定拍行走已经成立",
    extraChecks: (before, after) => {
      const failures = [];
      if (!before.body_text.includes("先听稳定拍，再用走一步、拍手、停住")) failures.push("missing steady beat movement pedagogy");
      if (!before.body_text.includes("休止")) failures.push("missing rest concept");
      if (!after.body_text.includes("steady_beat_walk_record_v1")) failures.push("missing steady beat walk export");
      if (!after.body_text.includes("readyForClassWalk")) failures.push("missing class walk readiness");
      if (!after.body_text.includes("已记录")) failures.push("missing movement attempt summary");
      return failures;
    },
  },
  {
    id: "listening-choice",
    path: "/template-console/listening-choice-preview.html",
    rootSelector: "#listening-choice-root",
    screenshotPrefix: "listening-choice",
    beforeTexts: ["听赏情绪选择", "先完整听一遍", "选择音乐依据", "学生表达", "教师观察点", "项目生成图卡"],
    h1Text: "听赏情绪选择",
    actionExpressions: [
      `document.querySelector('[aria-label="播放音乐"]')?.click(); true`,
      `
        [...document.querySelectorAll('.mood-card-grid button')].find((node) => node.textContent.includes('欢快'))?.click();
        [...document.querySelectorAll('.evidence-chip-grid button')].find((node) => node.textContent.includes('速度较快'))?.click();
        true
      `,
      `
        [...document.querySelectorAll('.listening-summary button')].find((node) => node.textContent.includes('提交依据'))?.click();
        true
      `,
    ],
    afterText: "已提交：请复听并验证这个依据。",
    extraChecks: (before, after) => {
      const failures = [];
      if (!before.body_text.includes("先听音乐")) failures.push("missing listen-first instruction");
      if ((before.mood_card_image_count || 0) < 3) failures.push("mood symbol cards did not render");
      if (!after.body_text.includes("欢快")) failures.push("selected mood missing after submit");
      if (!after.body_text.includes("速度较快")) failures.push("selected evidence missing after submit");
      return failures;
    },
  },
  {
    id: "lesson-opening",
    path: "/template-console/lesson-opening-preview.html",
    rootSelector: "#lesson-opening-root",
    screenshotPrefix: "lesson-opening",
    beforeTexts: ["课堂导入钩子", "先听", "选择听到的感受或画面", "选择音乐依据", "教师开场卡"],
    h1Text: "课堂导入钩子",
    actionExpressions: [
      `document.querySelector('[aria-label="播放导入音乐"]')?.click(); true`,
      `
        [...document.querySelectorAll('.opening-card-grid button')].find((node) => node.textContent.includes('欢快'))?.click();
        [...document.querySelectorAll('.evidence-chip-grid button')].find((node) => node.textContent.includes('速度较快'))?.click();
        [...document.querySelectorAll('.opening-question-list button')].find((node) => node.textContent.includes('小雨'))?.click();
        true
      `,
      `
        [...document.querySelectorAll('.lesson-opening-summary button')].find((node) => node.textContent.includes('生成开场卡'))?.click();
        true
      `,
    ],
    afterText: "开场卡已保存。",
    extraChecks: (before, after) => {
      const failures = [];
      if (!before.body_text.includes("先听 20 到 40 秒")) failures.push("missing short listening hook instruction");
      if ((before.mood_card_image_count || 0) < 3) failures.push("opening mood cards did not render");
      if (!after.body_text.includes("lesson_opening_record_v1")) failures.push("missing lesson opening export");
      if (!after.body_text.includes("速度较快")) failures.push("opening evidence missing");
      if (!after.body_text.includes("进入分句学唱")) failures.push("opening next activity hint missing");
      return failures;
    },
  },
  {
    id: "rhythm-question",
    path: "/template-console/rhythm-question-preview.html",
    rootSelector: "#rhythm-question-root",
    screenshotPrefix: "rhythm-question",
    beforeTexts: ["节奏问答", "先听教师节奏问句", "问句", "答句", "换一张节奏卡", "音乐反馈", "问答记录"],
    h1Text: "节奏问答",
    actionExpressions: [
      `document.querySelector('[aria-label="播放节奏问句"]')?.click(); true`,
      `document.querySelector('[aria-label="回拍节奏答句"]')?.click(); true`,
      `document.querySelector('[aria-label="回拍节奏答句"]')?.click(); true`,
      `
        [...document.querySelectorAll('.rhythm-question-feedback button')].find((node) => node.textContent.includes('保存问答'))?.click();
        true
      `,
    ],
    afterText: "节奏问答已保存，可以小组接答。",
    extraChecks: (before, after) => {
      const failures = [];
      if (!before.body_text.includes("先听教师节奏问句，再用同拍号答句回拍")) failures.push("missing rhythm call-response pedagogy");
      if (!before.body_text.includes("先听问句再答")) failures.push("missing listen-first status");
      if (!after.body_text.includes("rhythm_question_answer_record_v1")) failures.push("missing rhythm question answer export");
      if (!after.body_text.includes("ready_for_group_share")) failures.push("missing group-share readiness export");
      if (!after.body_text.includes("请 A 组拍问句，B 组拍答句")) failures.push("missing group call-response next step");
      return failures;
    },
  },
  {
    id: "theme-return-action",
    path: "/template-console/theme-return-action-preview.html",
    rootSelector: "#theme-return-action-root",
    screenshotPrefix: "theme-return-action",
    beforeTexts: ["主题再现动作", "先听主题", "主题时间窗", "主题动作卡", "选择音乐依据", "主题再现记录"],
    h1Text: "主题再现动作",
    actionExpressions: [
      `document.querySelector('[aria-label="播放主题"]')?.click(); true`,
      `document.querySelector('[aria-label="复听主题再现"]')?.click(); true`,
      `
        [...document.querySelectorAll('.theme-action-grid button')].find((node) => node.textContent.includes('举主题卡'))?.click();
        [...document.querySelectorAll('.evidence-chip-grid button')].find((node) => node.textContent.includes('旋律相同'))?.click();
        true
      `,
      `
        [...document.querySelectorAll('.evidence-panel button')].find((node) => node.textContent.includes('记录本次反应'))?.click();
        true
      `,
    ],
    afterText: "主题再现记录已保存。",
    extraChecks: (before, after) => {
      const failures = [];
      if (!before.body_text.includes("先听清 A 主题")) failures.push("missing theme listen-first instruction");
      if (!after.body_text.includes("theme_return_action_record_v1")) failures.push("missing theme return export");
      if (!after.body_text.includes("准确：1 次")) failures.push("theme return correct count missing");
      if (!after.body_text.includes("旋律相同")) failures.push("theme return evidence missing");
      return failures;
    },
  },
  {
    id: "graphic-score",
    path: "/template-console/graphic-score-preview.html",
    rootSelector: "#graphic-score-root",
    screenshotPrefix: "graphic-score",
    beforeTexts: ["图形谱创编", "图形含义卡", "图形谱板", "音乐反馈", "创编记录"],
    h1Text: "图形谱创编",
    actionExpressions: [
      `document.querySelectorAll('.graphic-score-slot-grid button')[0]?.click(); true`,
      `
        [...document.querySelectorAll('.graphic-symbol-bank button')].find((node) => node.textContent.includes('线'))?.click();
        true
      `,
      `document.querySelectorAll('.graphic-score-slot-grid button')[1]?.click(); true`,
      `
        [...document.querySelectorAll('.graphic-symbol-bank button')].find((node) => node.textContent.includes('块'))?.click();
        true
      `,
      `document.querySelectorAll('.graphic-score-slot-grid button')[2]?.click(); true`,
      `
        [...document.querySelectorAll('.graphic-symbol-bank button')].find((node) => node.textContent.includes('点'))?.click();
        true
      `,
      `document.querySelectorAll('.graphic-score-slot-grid button')[3]?.click(); true`,
      `document.querySelector('[aria-label="播放图形谱"]')?.click(); true`,
      `
        [...document.querySelectorAll('.graphic-score-feedback button')].find((node) => node.textContent.includes('提交展示'))?.click();
        true
      `,
    ],
    afterText: "图形谱已保存，可以全班展示。",
    extraChecks: (before, after) => {
      const failures = [];
      if (!before.body_text.includes("高低、长短和强弱")) failures.push("missing graphic score music elements");
      if (!after.body_text.includes("graphic_score_record_v1")) failures.push("missing graphic score export");
      if (!after.body_text.includes("可表演")) failures.push("graphic score readiness missing");
      if (!after.body_text.includes("图形谱能表现高低")) failures.push("graphic score feedback missing");
      return failures;
    },
  },
  {
    id: "exit-ticket",
    path: "/template-console/exit-ticket-preview.html",
    rootSelector: "#exit-ticket-root",
    screenshotPrefix: "exit-ticket",
    beforeTexts: ["课堂出口票", "本课音乐目标", "选择一个音乐依据", "写一句音乐理由", "班级汇总", "导出 JSON", "教师观察点"],
    h1Text: "课堂出口票",
    actionExpressions: [
      `
        [...document.querySelectorAll('.evidence-chip-grid button')].find((node) => node.textContent.includes('重复/对比'))?.click();
        true
      `,
      `
        const area = document.querySelector('textarea');
        if (area) {
          const setter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set;
          setter.call(area, 'A段主题在最后又回来了');
          area.dispatchEvent(new Event('input', { bubbles: true }));
          area.dispatchEvent(new Event('change', { bubbles: true }));
        }
        true
      `,
      `document.querySelector('.exit-result button')?.click(); true`,
    ],
    afterText: "出口票完成",
    extraChecks: (before, after) => {
      const failures = [];
      if (!before.body_text.includes("补音乐依据")) failures.push("missing evidence-needed status");
      if (!after.body_text.includes("已提交")) failures.push("exit ticket did not submit");
      if (!after.body_text.includes("A段主题在最后又回来了")) failures.push("exit ticket reason missing");
      if (!after.body_text.includes("已记录 1 张出口票")) failures.push("exit ticket class summary did not update");
      if (!after.body_text.includes("下节课可先围绕")) failures.push("exit ticket review suggestion missing");
      if (!after.body_text.includes("exit_ticket_class_summary_v1")) failures.push("exit ticket JSON export missing");
      return failures;
    },
  },
  {
    id: "phrase-singing",
    path: "/template-console/phrase-singing-preview.html",
    rootSelector: "#phrase-singing-root",
    screenshotPrefix: "phrase-singing",
    beforeTexts: ["乐句学唱", "春天来了", "先听", "再唱", "教师确认", "乐句列表", "教师提示"],
    h1Text: "乐句学唱",
    actionExpressions: [
      `document.querySelector('[aria-label="试听当前乐句"]')?.click(); true`,
      `
        [...document.querySelectorAll('.teacher-confirm-card button')].find((node) => node.textContent.includes('通过这一句'))?.click();
        true
      `,
    ],
    afterText: "小鸟歌唱",
    extraChecks: (before, after) => {
      const failures = [];
      if (!before.body_text.includes("听一句、唱一句")) failures.push("missing phrase sing pedagogy");
      if (!after.body_text.includes("1/2")) failures.push("phrase singing progress did not advance");
      if (!after.body_text.includes("当前乐句 2")) failures.push("phrase singing did not move to second phrase");
      return failures;
    },
  },
  {
    id: "solfege-echo",
    path: "/template-console/solfege-echo-preview.html",
    rootSelector: "#solfege-echo-root",
    screenshotPrefix: "solfege-echo",
    beforeTexts: ["唱名回声", "教师唱", "学生回声模唱", "音高走向", "教师确认", "do re mi"],
    h1Text: "唱名回声",
    actionExpressions: [
      `document.querySelector('[aria-label="试听示范"]')?.click(); true`,
      `
        [...document.querySelectorAll('.teacher-confirm-card button')].find((node) => node.textContent.includes('学生已模唱'))?.click();
        true
      `,
    ],
    afterText: "1/2",
    extraChecks: (before, after) => {
      const failures = [];
      if (!before.body_text.includes("教师先唱，学生听后")) failures.push("missing solfege echo listen-first pedagogy");
      if (!before.body_text.includes("上行")) failures.push("missing pitch motion hint");
      if (!after.body_text.includes("mi sol la")) failures.push("solfege echo did not move to second phrase");
      if (!after.body_text.includes("1/2")) failures.push("solfege echo progress did not advance");
      return failures;
    },
  },
  {
    id: "melody-contour",
    path: "/template-console/melody-contour-preview.html",
    rootSelector: "#melody-contour-root",
    screenshotPrefix: "melody-contour",
    beforeTexts: ["旋律线描一描", "先听旋律短句", "上行", "下行", "平稳", "旋律线记录"],
    h1Text: "旋律线描一描",
    actionExpressions: [
      `document.querySelector('[aria-label="播放旋律线"]')?.click(); true`,
      `
        [...document.querySelectorAll('.melody-gesture-panel button')].find((node) => node.textContent.includes('手势向上'))?.click();
        true
      `,
      `
        [...document.querySelectorAll('.melody-gesture-panel button')].find((node) => node.textContent.includes('手势向上'))?.click();
        true
      `,
      `
        [...document.querySelectorAll('.melody-gesture-panel button')].find((node) => node.textContent.includes('手势向下'))?.click();
        true
      `,
    ],
    afterText: "旋律线跟踪稳定了",
    extraChecks: (before, after) => {
      const failures = [];
      if (!before.body_text.includes("先听旋律短句，再用手势")) failures.push("missing melody contour listen-before-gesture pedagogy");
      if (!after.body_text.includes("melody_contour_trace_record_v1")) failures.push("missing melody contour export");
      if (!after.body_text.includes("readyForSingingTransfer")) failures.push("missing melody contour singing transfer readiness");
      if (!after.body_text.includes("已跟踪")) failures.push("missing melody contour attempt summary");
      if (!after.body_text.includes("正确")) failures.push("missing melody contour correct summary");
      return failures;
    },
  },
  {
    id: "simple-score",
    path: "/template-console/simple-score-preview.html",
    rootSelector: "#simple-score-root",
    screenshotPrefix: "simple-score",
    beforeTexts: ["简谱跟读", "先听示范", "当前简谱", "1 2 3", "do re mi", "节奏卡", "教师确认"],
    h1Text: "简谱跟读",
    actionExpressions: [
      `document.querySelector('[aria-label="试听当前简谱"]')?.click(); true`,
      `
        [...document.querySelectorAll('.teacher-confirm-card button')].find((node) => node.textContent.includes('跟读通过'))?.click();
        true
      `,
    ],
    afterText: "3 5 6",
    extraChecks: (before, after) => {
      const failures = [];
      if (!before.body_text.includes("先听示范，再看简谱")) failures.push("missing score listen-before-read pedagogy");
      if (!before.body_text.includes("ta-a")) failures.push("missing half-note rhythm card");
      if (!after.body_text.includes("1/2")) failures.push("simple score progress did not advance");
      if (!after.body_text.includes("学生跟读：mi sol la")) failures.push("simple score did not move to second line");
      return failures;
    },
  },
  {
    id: "pentatonic-melody",
    path: "/template-console/pentatonic-melody-preview.html",
    rootSelector: "#pentatonic-melody-root",
    screenshotPrefix: "pentatonic-melody",
    beforeTexts: ["五声音条琴创编", "虚拟音条琴", "do、re、mi、sol、la", "节奏格", "创编检查", "教师确认", "创编记录"],
    h1Text: "五声音条琴创编",
    actionExpressions: [
      `
        [...document.querySelectorAll('.xylophone-keyboard button')].slice(0, 4).forEach((node) => node.click());
        true
      `,
      `document.querySelector('[aria-label="回放五声短句"]')?.click(); true`,
      `
        [...document.querySelectorAll('.teacher-confirm-card button')].find((node) => node.textContent.includes('确认创编'))?.click();
        true
      `,
    ],
    afterText: "创编完成，可以小组接龙改编。",
    extraChecks: (before, after) => {
      const failures = [];
      if (!before.body_text.includes("只用 do、re、mi、sol、la")) failures.push("missing pentatonic constraint");
      if ((before.body_text.match(/待放音/g) || []).length < 4) failures.push("missing pentatonic rhythm slots");
      if (!after.body_text.includes("4/4")) failures.push("pentatonic phrase slots did not fill");
      if (!after.body_text.includes("五声音级短句完成")) failures.push("pentatonic evaluation did not become ready");
      if (!after.body_text.includes("pentatonic_creation_record_v1")) failures.push("missing pentatonic creation export");
      if (!after.body_text.includes("修改：")) failures.push("missing pentatonic revision count");
      if (!after.body_text.includes("回放：")) failures.push("missing pentatonic audition count");
      if (!after.body_text.includes("下一组")) failures.push("missing pentatonic relay suggestion");
      return failures;
    },
  },
  {
    id: "phrase-difficult-repair",
    path: "/template-console/phrase-singing-preview.html",
    rootSelector: "#phrase-singing-root",
    screenshotPrefix: "phrase-difficult-repair",
    preloadExpression: `
      window.__PHRASE_SINGING_STATE__ = {
        workflow: {
          education_alignment: {
            primary_competency: "艺术表现",
            music_elements: ["乐句", "旋律", "换气"],
            student_practices: ["listen", "sing", "explain"]
          }
        },
        config: {
          lyrics_phrases: ["迎面吹来了凉爽的风"],
          melody_phrases: ["re mi sol mi re do"],
          bpm: 72,
          practice_variant: "difficult_phrase_repair",
          difficult_phrase: "迎面吹来了凉爽的风",
          breath_points: ["吹来了/凉爽的风"],
          slow_loop_enabled: true,
          show_breath_hint: true,
          teacher_confirm_required: true,
          show_pitch_hint: true
        }
      };
    `,
    beforeTexts: ["乐句学唱", "难点乐句重练", "慢速循环 72 BPM", "迎面吹来了凉爽的风", "换气点", "吹来了 / 凉爽的风", "旋律走向"],
    h1Text: "乐句学唱",
    actionExpressions: [
      `document.querySelector('[aria-label="试听当前乐句"]')?.click(); true`,
      `
        [...document.querySelectorAll('.teacher-confirm-card button')].find((node) => node.textContent.includes('通过这一句'))?.click();
        true
      `,
    ],
    afterText: "可以把所有乐句连起来完整演唱。",
    extraChecks: (before, after) => {
      const failures = [];
      if (!before.body_text.includes("慢速听唱难点乐句")) failures.push("missing difficult phrase singing pedagogy");
      if (!before.body_text.includes("re mi sol mi re do")) failures.push("missing melody direction hint");
      if (!after.body_text.includes("1/1")) failures.push("difficult phrase confirmation did not complete");
      return failures;
    },
  },
  {
    id: "orff-ensemble",
    path: "/template-console/orff-ensemble-preview.html",
    rootSelector: "#orff-ensemble-root",
    screenshotPrefix: "orff-ensemble",
    beforeTexts: ["奥尔夫打击乐合奏", "A组手鼓强拍", "B组木鱼稳定拍", "C组沙锤弱拍", "D组三角铁点缀", "共同节奏", "声部进入提示", "小组表现记录", "录制回放", "教师提示"],
    h1Text: "奥尔夫打击乐合奏",
    actionExpressions: [
      `document.querySelector('[aria-label="播放合奏"]')?.click(); true`,
      `
        [...document.querySelectorAll('.ensemble-part-card button')].find((node) => node.textContent.includes('静音'))?.click();
        true
      `,
      `
        (async () => {
          document.querySelector('[aria-label="开始声部进入计时"]')?.click();
          await new Promise((resolve) => setTimeout(resolve, 60));
          [...document.querySelectorAll('.ensemble-entry-card button')][0]?.click();
          return true;
        })()
      `,
      `
        [...document.querySelectorAll('.ensemble-record-card')][0]
          ?.querySelectorAll('.ensemble-criteria-grid button')
          ?.forEach((node) => node.click());
        const evidence = document.querySelector('[aria-label="A组音乐依据"]');
        if (evidence) {
          const setter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value')?.set;
          setter.call(evidence, '节奏稳定，进入整齐，能听同伴声部');
          evidence.dispatchEvent(new Event('input', { bubbles: true }));
          evidence.dispatchEvent(new Event('change', { bubbles: true }));
        }
        true
      `,
    ],
    afterText: "1/4 组可记录",
    extraChecks: (before, after) => {
      const failures = [];
      if (!before.body_text.includes("合奏时先听别人")) failures.push("missing ensemble listening rule");
      if (!after.body_text.includes("静音")) failures.push("mute state missing after action");
      if (!after.body_text.includes("准时进入")) failures.push("Orff entry timing did not record on-cue entry");
      if (!after.body_text.includes("orff_group_performance_record_v1")) failures.push("missing Orff group performance export");
      if (!after.body_text.includes("orff_ensemble_session_record_v1")) failures.push("missing Orff session recording export");
      if (!after.body_text.includes("orff_entry_attempt_summary_v1")) failures.push("missing Orff entry attempt summary");
      if (!after.body_text.includes("已记录")) failures.push("Orff session events did not record");
      if (!after.body_text.includes("A组可以记录")) failures.push("Orff performance record did not become ready");
      if (!after.body_text.includes("展示后请学生说出自己什么时候进入")) failures.push("missing transfer prompt");
      return failures;
    },
  },
  {
    id: "body-percussion",
    path: "/template-console/body-percussion-preview.html",
    rootSelector: "#body-percussion-root",
    screenshotPrefix: "body-percussion",
    beforeTexts: ["身体打击编排", "休止", "拍手", "拍腿", "跺脚", "停住", "教师观察点"],
    h1Text: "身体打击编排",
    actionExpressions: [
      `
        document.querySelector('.body-slot[data-body-rhythm="rest"] [data-body-action="跺脚"]')?.click();
        true
      `,
      `
        document.querySelector('.body-slot[data-body-rhythm="rest"] [data-body-action="停住"]')?.click();
        true
      `,
    ],
    afterText: "身体打击编排完成",
    extraChecks: (before, after) => {
      const failures = [];
      if (!before.body_text.includes("可展示")) failures.push("default body percussion should be ready");
      if (!after.body_text.includes("提交展示")) failures.push("missing performance submit action");
      if (!after.body_text.includes("休止也表现出来了")) failures.push("missing rest-aware feedback");
      return failures;
    },
  },
  {
    id: "group-relay",
    path: "/template-console/group-relay-preview.html",
    rootSelector: "#group-relay-root",
    screenshotPrefix: "group-relay",
    beforeTexts: ["小组接力展示", "A组拍第一小节", "音乐依据", "教师观察点", "先听同伴"],
    h1Text: "小组接力展示",
    actionExpressions: [
      `
        [...document.querySelectorAll('.group-relay-card.active button')].find((node) => node.textContent.includes('完成展示'))?.click();
        true
      `,
      `
        const area = document.querySelector('textarea[aria-label="填写小组接力音乐依据"]');
        if (area) {
          const setter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set;
          setter.call(area, '节奏稳定，进入整齐');
          area.dispatchEvent(new Event('input', { bubbles: true }));
          area.dispatchEvent(new Event('change', { bubbles: true }));
        }
        true
      `,
      `
        [...document.querySelectorAll('.relay-evidence-box button')].find((node) => node.textContent.includes('提交评价'))?.click();
        true
      `,
    ],
    afterText: "B组准备进入",
    extraChecks: (before, after) => {
      const failures = [];
      if (!before.body_text.includes("评价必须说出音乐依据")) failures.push("missing music evidence rule");
      if (!after.body_text.includes("B组接第二小节")) failures.push("next group did not stay visible");
      if (!after.body_text.includes("本组进入")) failures.push("next group did not become active");
      return failures;
    },
  },
  {
    id: "peer-feedback",
    path: "/template-console/peer-feedback-preview.html",
    rootSelector: "#peer-feedback-root",
    screenshotPrefix: "peer-feedback",
    beforeTexts: ["展示与同伴评价", "先听完整展示", "音乐依据", "同伴建议", "展示评价记录", "教师观察点"],
    h1Text: "展示与同伴评价",
    actionExpressions: [
      `
        [...document.querySelectorAll('.criteria-chip-grid button')].find((node) => node.textContent.includes('节奏稳定'))?.click();
        true
      `,
      `
        const area = document.querySelector('textarea[aria-label="填写同伴评价建议"]');
        if (area) {
          const setter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set;
          setter.call(area, '节奏稳定，如果休止处停得更整齐会更好');
          area.dispatchEvent(new Event('input', { bubbles: true }));
          area.dispatchEvent(new Event('change', { bubbles: true }));
        }
        true
      `,
      `
        [...document.querySelectorAll('.peer-feedback-panel button')].find((node) => node.textContent.includes('提交同伴评价'))?.click();
        true
      `,
    ],
    afterText: "正在评价：B组展示身体打击",
    extraChecks: (before, after) => {
      const failures = [];
      if (!before.body_text.includes("不能只说好听或喜欢")) failures.push("missing generic feedback guard");
      if (!before.body_text.includes("先听完整展示")) failures.push("missing listen-before-feedback pedagogy");
      if (!after.body_text.includes("peer_feedback_record_v1")) failures.push("missing peer feedback export");
      if (!after.body_text.includes("reviewedCount")) failures.push("missing peer feedback reviewed count");
      if (!after.body_text.includes("节奏稳定，如果休止处停得更整齐会更好")) failures.push("peer feedback suggestion did not save");
      if (!after.body_text.includes("B组展示身体打击")) failures.push("peer feedback did not advance to next group");
      return failures;
    },
  },
];

const MIME_TYPES = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".svg": "image/svg+xml",
  ".woff": "font/woff",
  ".woff2": "font/woff2",
  ".mp3": "audio/mpeg",
  ".ogg": "audio/ogg",
};

async function main() {
  await assertBuilt();
  mkdirSync(snapshotsDir, { recursive: true });
  const server = await startStaticServer(distDir);
  const chrome = await launchChrome();
  const report = {
    version: "browser_smoke_report_v2",
    targets: SMOKE_TARGETS.map((target) => target.path),
    checked_at: new Date().toISOString(),
    status: "unknown",
    viewports: [],
    console_errors: [],
    screenshots: [],
  };

  try {
    const endpoint = await waitForDevTools(chrome.port);
    for (const target of SMOKE_TARGETS) {
      for (const viewport of VIEWPORTS) {
        const result = await smokeViewport(endpoint, server.origin, target, viewport);
        report.viewports.push(result.viewport_report);
        report.console_errors.push(...result.console_errors);
        report.screenshots.push(result.screenshot);
        console.log(`smoked ${target.id} ${viewport.name}`);
      }
    }
    const failures = report.viewports.flatMap((viewport) => viewport.failures);
    report.status = failures.length || report.console_errors.length ? "fail" : "pass";
    writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`);
    if (report.status !== "pass") {
      console.error(JSON.stringify(report, null, 2));
      process.exitCode = 1;
    } else {
      console.log(`Primary activity browser smoke passed. Report: ${reportPath}`);
    }
  } finally {
    await chrome.close();
    await server.close();
  }
}

async function assertBuilt() {
  await access(join(distDir, "primary-library.html"));
  await access(join(distDir, "primary-activity-preview.html"));
  await access(join(distDir, "instrument-family-preview.html"));
  await access(join(distDir, "lyrics-rhythm-preview.html"));
  await access(join(distDir, "strong-weak-beat-preview.html"));
  await access(join(distDir, "steady-beat-walk-preview.html"));
  await access(join(distDir, "listening-choice-preview.html"));
  await access(join(distDir, "rhythm-question-preview.html"));
  await access(join(distDir, "theme-return-action-preview.html"));
  await access(join(distDir, "graphic-score-preview.html"));
  await access(join(distDir, "body-percussion-preview.html"));
  await access(join(distDir, "group-relay-preview.html"));
  await access(join(distDir, "peer-feedback-preview.html"));
  await access(join(distDir, "exit-ticket-preview.html"));
  await access(join(distDir, "phrase-singing-preview.html"));
  await access(join(distDir, "solfege-echo-preview.html"));
  await access(join(distDir, "melody-contour-preview.html"));
  await access(join(distDir, "simple-score-preview.html"));
  await access(join(distDir, "pentatonic-melody-preview.html"));
  await access(join(distDir, "orff-ensemble-preview.html"));
}

async function startStaticServer(rootDir) {
  const server = createServer(async (request, response) => {
    try {
      const url = new URL(request.url || "/", "http://127.0.0.1");
      if (url.pathname === "/api/primary-activity-library") {
        const doubaoTasks = JSON.parse(
          await readFile(join(appStaticAssetsDir, "primary-asset-packs", "doubao-generation-tasks.json"), "utf-8")
        );
        response.writeHead(200, { "content-type": "application/json; charset=utf-8" });
        response.end(JSON.stringify({
          ...fallbackPrimaryLibraryPayload(),
          quality_report: {
            status: "pass",
            pending_doubao_generation_tasks: doubaoTasks.tasks || [],
            pending_image2_generation_tasks: []
          }
        }));
        return;
      }
      const pathname = url.pathname.startsWith("/template-console/")
        ? url.pathname.slice("/template-console".length)
        : url.pathname;
      const rawPath = decodeURIComponent(pathname === "/" ? "/primary-activity-preview.html" : pathname);
      const staticAssetPrefix = "/static/assets/";
      const servingAppStaticAsset = rawPath.startsWith(staticAssetPrefix);
      const filePath = servingAppStaticAsset
        ? resolve(join(appStaticAssetsDir, rawPath.slice(staticAssetPrefix.length)))
        : resolve(join(rootDir, rawPath));
      const allowedRoot = servingAppStaticAsset ? appStaticAssetsDir : rootDir;
      if (!filePath.startsWith(allowedRoot)) {
        response.writeHead(403);
        response.end("Forbidden");
        return;
      }
      const fileStat = await stat(filePath);
      if (!fileStat.isFile()) {
        response.writeHead(404);
        response.end("Not found");
        return;
      }
      response.writeHead(200, { "content-type": MIME_TYPES[extname(filePath)] || "application/octet-stream" });
      response.end(await readFile(filePath));
    } catch {
      response.writeHead(404);
      response.end("Not found");
    }
  });
  await new Promise((resolveReady) => server.listen(0, "127.0.0.1", resolveReady));
  const address = server.address();
  return {
    origin: `http://127.0.0.1:${address.port}`,
    close: () => new Promise((resolveClose) => server.close(resolveClose)),
  };
}

function fallbackPrimaryLibraryPayload() {
  return {
    music_education_foundation: {
      core_competencies: [
        {
          competency_id: "aesthetic_perception",
          label: "审美感知",
          classroom_meaning: "听辨音乐情绪、速度、力度、音色、旋律特点，形成感受和判断。",
          candidate_activities: ["听赏选择", "音色侦探"],
          avoid: "只让学生抢答，不要求聆听依据。"
        },
        {
          competency_id: "artistic_performance",
          label: "艺术表现",
          classroom_meaning: "用歌唱、演奏、律动、身体动作表现音乐。",
          candidate_activities: ["分句跟唱", "节奏复刻"],
          avoid: "只点按钮得分，没有唱、奏、动。"
        }
      ],
      student_practices: [
        { practice_id: "listen", label: "听", primary_classroom_meaning: "听情绪、速度、力度、音色、主题、段落。", candidate_activities: ["听赏选择"] },
        { practice_id: "sing", label: "唱", primary_classroom_meaning: "模唱、接唱、分句唱、唱名唱。", candidate_activities: ["分句跟唱"] }
      ],
      music_elements: [
        { element_id: "steady_beat", label: "稳定拍", primary_range: "感受均匀拍点", game_methods: ["跟拍"], grade_hint: "低段优先" },
        { element_id: "rhythm", label: "节奏", primary_range: "四分、八分、休止", game_methods: ["节奏卡"], grade_hint: "全学段" }
      ],
      grade_boundaries: [
        { grade_band: "lower_primary", label: "小学低段", learning_traits: "以感受、模仿、动作、图像为主。", design_requirements: "少文字、大按钮、多听多动、即时反馈。", avoid: "长说明、复杂规则、抽象术语。" }
      ],
      teaching_stages: [
        { stage_id: "lesson_opening", label: "导入", music_purpose: "激发兴趣、唤起经验、初步感受。", candidate_activities: ["听一遍投票"], avoid: "复杂闯关。" }
      ]
    },
    gameplay_templates: [
      {
        template_id: "rhythm_echo_core",
        label: "节奏复刻",
        primary_competency: "艺术表现",
        secondary_competency: "审美感知",
        music_elements: ["稳定拍", "节奏", "休止"],
        student_practices: ["listen", "tap", "move"],
        teaching_stages: ["律动/节奏", "复习巩固"],
        supported_materials: ["rhythm_pattern", "meter"],
        core_loop: ["listen", "remember", "tap", "feedback"],
        required_components: ["audio_player", "meter_track", "rhythm_pad"],
        required_rules: ["rhythm_timing_judgement"],
        required_teacher_controls: ["tempo_control_pack", "reset_pack"],
        optional_assets: ["reward_badge_pack"],
        difficulty_controls: ["bpm", "show_hint"],
        implementation_status: "runtime_ready",
        evidence: ["game_template_registry", "browser smoke"],
        applicable_activity_ids: ["rhythm_warmup"]
      },
      {
        template_id: "body_percussion_core",
        label: "身体打击工坊",
        primary_competency: "创意实践",
        music_elements: ["节奏", "节拍", "力度"],
        student_practices: ["move", "tap", "create"],
        teaching_stages: ["律动", "创编"],
        supported_materials: ["meter", "body_action_set"],
        core_loop: ["choose_action", "arrange", "perform", "revise"],
        required_components: ["body_action_cards", "meter_track"],
        required_rules: ["bar_length_rule"],
        required_teacher_controls: ["teacher_confirm_pack"],
        optional_assets: ["body_action_card_pack"],
        difficulty_controls: ["bar_count", "action_count"],
        implementation_status: "activity_ready",
        evidence: ["独立 React 学生活动页"],
        applicable_activity_ids: ["body_percussion_builder"]
      }
    ],
    component_library: [
      {
        component_id: "game_hud",
        name: "游戏状态 HUD",
        role: "game_shell",
        runtime: "react_radix_lucide",
        purpose: "显示本轮音乐任务的得分、星级、回合、剩余时间和当前音乐目标。",
        student_actions: ["observe", "revise"],
        music_elements: ["课堂进度", "音乐目标"],
        required_material_entities: [],
        teacher_controls: ["reset", "pause", "show_hint"],
        required_elements: ["分数", "回合", "音乐目标"],
        behaviors: ["不遮挡音乐操作区", "投屏可读"],
        interaction_modes: ["desktop_mouse", "projector_large_text"],
        empty_state: "未开始时显示本轮音乐任务和开始状态，不显示空分数。",
        error_state: "缺少活动状态时提示教师重置或重新生成活动。",
        called_by_template_ids: ["rhythm_echo_core", "timbre_detective_core"],
        open_source_dependencies: ["react", "radix", "lucide-react"],
        quality_gates: ["not_standalone_game", "readable_on_projector", "reset_ready"],
        education_notes: ["HUD 只能辅助课堂节奏，不能把音乐学习简化成抢分。"]
      },
      {
        component_id: "answer_choice_grid",
        name: "音乐选择网格",
        role: "music_operation",
        runtime: "react_radix",
        purpose: "用于情绪、速度、力度、音色、唱名等听后选择。",
        student_actions: ["listen", "choose", "explain"],
        music_elements: ["情绪", "速度", "力度", "音色"],
        required_material_entities: ["audio_clip"],
        teacher_controls: ["reset", "show_answer", "hide_hint"],
        required_elements: ["选项卡", "禁用态", "选择反馈"],
        behaviors: ["必须先听后选", "选择后要求音乐依据"],
        interaction_modes: ["desktop_mouse", "touch_screen", "projector_large_text"],
        empty_state: "没有选项时提示补充可听辨目标或证据词。",
        error_state: "音频未绑定时禁止选择并提示先绑定音频。",
        called_by_template_ids: ["listening_choice_core", "timbre_detective_core"],
        open_source_dependencies: ["react", "radix"],
        quality_gates: ["not_standalone_game", "listen_before_choice", "evidence_required"],
        education_notes: ["选择网格用于表达听觉判断，不能变成看图或猜词。"]
      }
    ],
    toolkit_catalog: [
      {
        activity_id: "rhythm_warmup",
        activity_name: "节奏热身",
        grade_bands: ["lower_primary", "middle_primary"],
        student_music_behaviors: ["listen", "tap", "move"],
        education_alignment: {
          primary_competency: "艺术表现",
          secondary_competency: "审美感知",
          student_practices: ["listen", "tap", "move"],
          music_elements: ["稳定拍", "节奏"],
          teaching_stages: ["导入", "节奏练习"],
          grade_fit: { lower_primary: "听、拍、动建立稳定拍。" },
          pedagogy_notes: ["先听到稳定拍，再用身体和节奏垫表现。"]
        },
        selected: {
          components: ["audio_player", "rhythm_card_bank", "meter_track", "tap_feedback", "teacher_control_bar"],
          teaching_aids: ["rhythm_cards"],
          virtual_instruments: ["rhythm_pad"],
          game_templates: []
        },
        why: "小学节奏热身优先让学生完成听、拍、动。"
      }
    ],
    teaching_aids: [
      {
        aid_id: "rhythm_cards",
        name: "节奏卡",
        replace_physical_aid: "实体节奏卡",
        material_entities: ["rhythm_pattern", "meter"],
        components: ["rhythm_card_bank", "audio_player"],
        student_actions: ["listen", "arrange", "tap"],
        teacher_controls: ["shuffle", "show_answer", "reset"],
        real_photo_required: false,
        doubao_required: false,
        asset_pack_required: "",
        asset_policy: { source: "vector_or_runtime_component", note: "运行时组件生成，不需要独立图片。" },
        quality_gates: ["material_bound", "student_operable", "teacher_reset_ready"]
      },
      {
        aid_id: "instrument_cards",
        name: "可演奏乐器皮肤卡",
        replace_physical_aid: "实体乐器图片卡和课堂乐器",
        material_entities: ["timbre_set", "instrument_pool", "audio_clip"],
        components: ["instrument_card_grid", "compare_player"],
        student_actions: ["listen", "match", "play", "explain"],
        teacher_controls: ["replay", "show_family", "reset"],
        real_photo_required: false,
        doubao_required: false,
        image_gen_required: true,
        asset_pack_required: "generated_playable_instrument_pack",
        asset_policy: { source: "image_gen_generated_png", note: "固定模板库里的乐器皮肤使用本地 image2 逐个生成，并绑定本地采样播放。" },
        quality_gates: ["listen_before_choice", "generated_instrument_skin_visible", "real_sample_playback", "evidence_required"]
      },
      {
        aid_id: "mood_picture_cards",
        name: "听赏情绪图卡",
        replace_physical_aid: "实体情绪图卡",
        material_entities: ["audio_clip", "expression_trait"],
        components: ["picture_prompt_cards", "compare_player"],
        student_actions: ["listen", "choose", "explain"],
        teacher_controls: ["replay", "hide_words", "reset"],
        real_photo_required: false,
        doubao_required: false,
        image_gen_required: true,
        asset_pack_required: "music_mood_picture_pack",
        asset_policy: { source: "image_gen_generated_png", note: "情绪图卡使用生成 PNG，并必须通过文件校验。" },
        quality_gates: ["listen_before_choice", "image_gen_png_file_verified", "evidence_required"]
      }
    ],
    virtual_instruments: [
      {
        instrument_id: "rhythm_pad",
        name: "虚拟节奏垫",
        replace_physical_instrument: "拍手/小鼓",
        input_modes: ["touch", "mouse", "keyboard"],
        sound_source: "webaudio_synthetic_drum",
        pitch_set: [],
        constraints: { record_events: true },
        teacher_controls: ["change_tempo", "show_beat", "reset"],
        quality_gates: ["sound_plays", "events_recorded", "teacher_controls_apply"],
        runtime_contract: {
          audio_unlock_required: true,
          student_event_schema: ["instrument_id", "timestamp_ms", "tap_index", "timing_status"],
          quality_gates: ["sound_plays", "events_recorded", "reset_clears_events"]
        }
      },
      {
        instrument_id: "tambourine",
        name: "虚拟铃鼓",
        replace_physical_instrument: "铃鼓",
        input_modes: ["touch", "mouse", "keyboard"],
        sound_source: "sample_or_webaudio_tambourine",
        pitch_set: [],
        constraints: { record_events: true, supports_roll: true },
        teacher_controls: ["change_tempo", "toggle_roll", "reset"],
        quality_gates: ["sound_plays", "events_recorded", "roll_mode_applies"],
        runtime_contract: {
          audio_unlock_required: true,
          student_event_schema: ["instrument_id", "timestamp_ms", "hit_type", "roll_mode", "beat_index"],
          quality_gates: ["sound_plays", "events_recorded", "reset_clears_events"]
        }
      },
      {
        instrument_id: "virtual_xylophone",
        name: "虚拟音条琴",
        replace_physical_instrument: "音条琴",
        input_modes: ["touch", "mouse", "keyboard"],
        sound_source: "webaudio_or_soundfont",
        pitch_set: ["do", "re", "mi", "sol", "la"],
        constraints: { only_allow_target_pitches: true, record_events: true },
        teacher_controls: ["change_tempo", "hide_labels", "limit_pitch_count", "reset"],
        quality_gates: ["sound_plays", "events_recorded", "material_bound"],
        runtime_contract: {
          audio_unlock_required: true,
          student_event_schema: ["instrument_id", "timestamp_ms", "pitch", "solfege", "slot_index"],
          quality_gates: ["sound_plays", "events_recorded", "pitch_limited_to_material", "reset_clears_events"]
        }
      },
      {
        instrument_id: "classroom_percussion_kit",
        name: "课堂打击乐套组",
        replace_physical_instrument: "奥尔夫打击乐器组",
        input_modes: ["touch", "mouse", "keyboard"],
        sound_source: "sample_or_webaudio_percussion",
        pitch_set: [],
        constraints: { record_events: true },
        teacher_controls: ["mute_group", "solo_group", "change_tempo", "reset"],
        quality_gates: ["sound_plays", "events_recorded", "group_controls_apply"],
        runtime_contract: {
          audio_unlock_required: true,
          student_event_schema: ["instrument_id", "timestamp_ms", "part_id", "group_id", "beat_index"],
          quality_gates: ["sound_plays", "events_recorded", "reset_clears_events"]
        }
      }
    ],
    asset_pack_templates: [
      {
        asset_pack_template_id: "generated_playable_instrument_pack",
        label: "生成式可演奏乐器皮肤包",
        source_kind: "image2",
        included_assets: [
          {
            asset_id: "virtual_hand_drum",
            file: "images/virtual_hand_drum.png",
            music_element: "音色",
            student_action: "play",
            accessibility_label: "虚拟小鼓生成插图"
          }
        ],
        usage: ["virtual_instrument_skin", "playable_instrument_card"],
        generation_requirement: {
          status: "ready_from_manifest",
          provider: "image2",
          save_policy: "每个单件乐器皮肤由本地生图器 image2 模型逐个生成 PNG；新增乐器必须先生成独立 PNG 再进入 ready 列表。"
        },
        authenticity_policy: "生成图只作为库乐队式演奏界面皮肤，不声明为真实照片；真实感由采样音频合同保证。",
        applicable_activity_ids: ["instrument_timbre_match", "instrument_family_sorting"],
        supports_teaching_aids: ["instrument_evidence_cards"],
        supports_virtual_instruments: ["virtual_hand_drum", "woodblock_claves", "shaker", "triangle_bell", "tambourine"],
        supports_ensemble_controllers: ["classroom_percussion_kit"],
        music_elements: ["音色", "乐器"],
        student_music_practices: ["listen", "play", "match"],
        classroom_role: "替代小学课堂可演奏乐器皮肤和实体乐器操作界面。",
        quality_gates: ["generated_instrument_skin_visible", "real_sample_playback", "no_web_photo_fallback"]
      },
      {
        asset_pack_template_id: "music_mood_picture_pack",
        label: "音乐情绪图卡包",
        source_kind: "image_gen_generated",
        included_assets: [
          {
            asset_id: "cheerful",
            file: "images/cheerful.png",
            music_element: "情绪",
            student_action: "choose",
            accessibility_label: "欢快情绪图卡"
          }
        ],
        usage: ["mood_card", "listening_intro"],
        generation_requirement: {
          status: "ready_from_manifest",
          provider: "image2",
          save_policy: "生成 PNG 已保存到 manifest 指定路径；这是模板库资产建设记录，不改变智能体核心逻辑。"
        },
        authenticity_policy: "使用生成 PNG 作为非写实情绪图，但不能代替真实乐器照片。",
        applicable_activity_ids: ["picture_listening_intro", "listen_choose_explain"],
        supports_teaching_aids: ["mood_picture_cards"],
        supports_virtual_instruments: [],
        music_elements: ["情绪", "速度", "力度"],
        student_music_practices: ["listen", "choose", "explain"],
        classroom_role: "替代实体情绪图卡，用于听赏初听后的情绪选择和音乐依据表达。",
        quality_gates: ["生成 PNG 文件验收通过", "学生必须说出音乐依据"]
      },
      {
        asset_pack_template_id: "classroom_character_pack",
        label: "课堂角色包",
        source_kind: "image_gen_generated",
        included_assets: [
          {
            asset_id: "music_helper",
            file: "images/music_helper.png",
            music_element: "任务引导",
            student_action: "follow",
            accessibility_label: "音乐小助手生成角色"
          }
        ],
        usage: ["classroom_role", "feedback_character"],
        generation_requirement: {
          status: "ready_from_manifest",
          provider: "image2",
          save_policy: "通用课堂角色 PNG 已保存到 manifest 指定路径；后续新增角色再逐张生成。"
        },
        authenticity_policy: "角色图只用于任务引导和反馈，不替代真实乐器照片或音乐材料。",
        applicable_activity_ids: ["rhythm_warmup", "listen_choose_explain"],
        supports_teaching_aids: ["picture_prompt_cards"],
        supports_virtual_instruments: [],
        music_elements: ["任务引导", "反馈"],
        student_music_practices: ["listen", "respond", "explain"],
        classroom_role: "作为低段课堂任务引导和反馈角色。",
        quality_gates: ["生成 PNG 文件验收通过", "角色只用于任务引导和反馈"]
      },
      {
        asset_pack_template_id: "classroom_stage_background_pack",
        label: "课堂舞台背景包",
        source_kind: "lesson_runtime_generated",
        included_assets: [
          {
            asset_id: "small_stage",
            file: "images/small_stage.png",
            music_element: "展示",
            student_action: "perform",
            accessibility_label: "小舞台背景"
          }
        ],
        usage: ["activity_background", "game_scene_background"],
        generation_requirement: {
          status: "lesson_runtime_generation_required",
          provider: "lesson_runtime_image_generation",
          save_policy: "收到具体教案和情景后生成 16:9 PNG，保存到本次活动产物 assets 目录。"
        },
        authenticity_policy: "背景是按教案临时生成情境图，不承担真实乐器或作品证据功能；不能遮挡音乐操作组件。",
        applicable_activity_ids: ["rhythm_warmup", "picture_listening_intro"],
        supports_teaching_aids: [],
        supports_virtual_instruments: [],
        music_elements: ["情境", "情绪"],
        student_music_practices: ["listen", "perform"],
        classroom_role: "替代实体舞台/情境背景板，用于投屏活动的空间与情境提示。",
        quality_gates: ["必须由教案主题、音乐材料、年级和活动任务触发生成", "背景接近 16:9 且无文字水印"]
      }
    ],
    micro_activity_templates: [
      {
        micro_activity_template_id: "one_minute_beat_check",
        label: "一分钟稳拍检查",
        duration_minutes: 1,
        classroom_use: "上课开始或节奏活动前快速检查全班拍点是否稳定。",
        component_ids: ["meter_track", "tap_feedback", "teacher_control_bar"],
        applicable_activity_ids: ["rhythm_warmup"],
        music_elements: ["稳定拍", "节奏"],
        student_music_practices: ["listen", "tap", "move"],
        teaching_stages: ["导入", "节奏练习"],
        teacher_controls: ["tempo", "reset"],
        acceptance: ["能快速开始", "能快速重置", "至少记录 3 次拍点"],
        quality_gates: ["学生先听稳定拍", "全班拍点记录可见"]
      },
      {
        micro_activity_template_id: "listen_once_vote",
        label: "听一遍投票",
        duration_minutes: 2,
        classroom_use: "欣赏初听后让学生选择听到的情绪、速度或力度，并显示全班投票结果。",
        component_ids: ["audio_player", "choice_cards", "rubric_panel"],
        applicable_activity_ids: ["picture_listening_intro"],
        music_elements: ["情绪", "速度", "力度"],
        student_music_practices: ["listen", "choose", "explain"],
        teaching_stages: ["导入", "初听/感受"],
        teacher_controls: ["playback", "result_review"],
        acceptance: ["全班投票结果可显示", "可复听"],
        quality_gates: ["必须先完整听一遍", "选择后追问音乐依据"]
      }
    ],
    material_entities: [
      {
        entity_id: "lesson_objective",
        label: "教学目标 / 音乐学习重点",
        source_kinds: ["lesson_text", "teacher_request", "manual_input"],
        structured_result_fields: ["objective_text", "music_elements", "student_practices", "grade_hint"],
        game_ready_schema: { value: "string" },
        matched_binder_ids: ["listening_evidence_binder", "group_task_binder"],
        recommended_gameplay_template_ids: ["listen_choose_explain", "exit_ticket_review"],
        quality_gates: ["do_not_invent", "objective_mentions_music_element"],
        teacher_confirm_required: ["music_element_focus"],
        do_not_invent_policy: "没有在教案、教师需求或上传材料中出现时，保持 missing，不自动编造。",
        music_education_use: "把教案目标转成活动选择依据，确保游戏练的是节奏、旋律、音色、曲式等音乐内容。"
      },
      {
        entity_id: "audio_clip",
        label: "音频片段",
        source_kinds: ["uploaded_audio", "audio_url", "manual_input"],
        structured_result_fields: ["url", "filename", "start_seconds", "end_seconds"],
        game_ready_schema: { url: "string" },
        matched_binder_ids: ["song_phrase_binder", "listening_evidence_binder", "form_segment_binder"],
        recommended_gameplay_template_ids: ["phrase_loop_singing", "listen_choose_explain", "theme_return_action"],
        quality_gates: ["do_not_invent", "audio_source_present"],
        teacher_confirm_required: ["audio_clip_boundary"],
        do_not_invent_policy: "没有在教案、教师需求或上传材料中出现时，保持 missing，不自动编造。",
        music_education_use: "支撑先听后唱、复听找证据、主题再现和音色听辨，不能用无声游戏替代聆听。"
      }
    ],
    material_binders: [
      {
        binder_id: "lyrics_rhythm_binder",
        label: "歌词节奏绑定",
        primary_material_kind: "lyrics_rhythm",
        input_entities: ["lyrics_phrase", "meter", "rhythm_pattern"],
        output_entities: ["lyrics_rhythm_strip", "stress_marks", "read_tap_sequence"],
        applicable_activity_ids: ["lyrics_rhythm_reading"],
        student_music_practices: ["listen", "read", "tap", "sing"],
        music_education_use: "把歌词、拍号和节奏型绑定成先按拍读、再拍出歌词节奏、最后回到演唱的材料。",
        quality_gates: ["lyrics_phrase_present", "meter_bound", "rhythm_value_check"]
      },
      {
        binder_id: "timbre_pool_binder",
        label: "音色池绑定",
        primary_material_kind: "instrument_pool",
        input_entities: ["instrument_pool", "instrument_family_set", "timbre_set", "audio_clip"],
        output_entities: ["instrument_cards", "timbre_word_cards", "compare_player_items"],
        applicable_activity_ids: ["instrument_timbre_match", "instrument_family_sorting"],
        student_music_practices: ["listen", "classify", "match", "explain"],
        music_education_use: "把乐器池、家族、音色词和听辨音频绑定成先听声音、再看真实照片和说依据的材料。",
        quality_gates: ["instrument_pool_present", "real_photo_gate", "audio_or_fallback_ready"]
      }
    ],
    assessment_record_templates: [
      {
        record_template_id: "tap_accuracy_record",
        label: "拍点准确记录",
        records: ["early_count", "on_time_count", "late_count", "steady_beat_accuracy"],
        output_forms: ["score", "summary_text", "json_export"],
        applicable_activity_ids: ["rhythm_warmup", "steady_beat_walk"],
        student_music_practices: ["listen", "tap", "move"],
        music_education_use: "记录学生是否先听稳定拍并在拍点上表现节奏，帮助教师判断要降速、复听还是增加挑战。",
        quality_gates: ["records_timing_evidence", "summary_visible", "json_export_available"]
      },
      {
        record_template_id: "exit_ticket_record",
        label: "课堂出口票记录",
        records: ["music_focus", "evidence_terms", "student_reason", "next_lesson_suggestion"],
        output_forms: ["class_list", "teacher_review_summary", "json_export"],
        applicable_activity_ids: ["exit_ticket_review"],
        student_music_practices: ["choose", "explain", "assess"],
        music_education_use: "在课堂收尾记录学生能否说出本课音乐要素和一个具体依据，供教师下节课复盘。",
        quality_gates: ["music_focus_present", "evidence_required", "teacher_review_ready"]
      }
    ],
    adaptive_templates: [
      {
        adaptive_template_id: "slow_down_when_many_late",
        label: "多数学生晚拍则降速",
        trigger_condition: "连续 2 轮晚拍或偏慢反馈较多，且活动目标仍是稳定拍、节奏或律动。",
        adjustment: "BPM 降低 8 到 12，并保留当前节奏/拍号材料。",
        teacher_visible_reason: "多数学生落在拍点后面，建议先降速复听，再回到原速。",
        undo_action: "恢复上一轮 BPM。",
        applicable_activity_ids: ["rhythm_warmup", "steady_beat_walk"],
        student_music_practices: ["listen", "tap", "move"],
        music_education_guardrails: ["不能改变课堂目标", "调整原因必须让教师看见", "教师必须能一键撤回"],
        quality_gates: ["teacher_reason_visible", "bpm_change_bounded", "undo_restores_previous_bpm"]
      },
      {
        adaptive_template_id: "suggest_next_activity",
        label: "活动后推荐下一步",
        trigger_condition: "当前活动完成，且已有记录模板或教师确认结果。",
        adjustment: "推荐一个巩固、挑战、展示或收尾活动，不自动跳转。",
        teacher_visible_reason: "根据刚才的课堂结果，给教师一个下一步建议，由教师决定是否采用。",
        undo_action: "关闭建议卡，不改变当前活动。",
        applicable_activity_ids: ["*"],
        student_music_practices: ["listen", "tap", "sing", "move", "play", "create", "perform", "assess"],
        music_education_guardrails: ["不能改变课堂目标", "调整原因必须让教师看见", "教师必须能一键撤回"],
        quality_gates: ["teacher_decides_next_step", "current_activity_preserved", "recommendation_uses_record_evidence"]
      }
    ],
    delivery_templates: [
      {
        delivery_template_id: "projector_activity_view",
        label: "投屏活动视图",
        form: "大字、大按钮、少文字、教师控制明显",
        purpose: "全班一起看、听、做，适合电子白板或教室大屏。",
        priority: "P0",
        output_formats: ["HTML", "React view"],
        applicable_activity_ids: ["*"],
        classroom_use: "用于课堂主屏，保证学生能在远处看清音乐材料、当前任务和教师控制。",
        quality_gates: ["large_text_readable", "teacher_controls_visible", "no_horizontal_overflow"]
      },
      {
        delivery_template_id: "classroom_result_export",
        label: "课堂结果导出",
        form: "JSON/CSV/截图",
        purpose: "课后复盘学生表现、出口票、小组评价和创编记录。",
        priority: "P1",
        output_formats: ["JSON", "CSV", "PNG"],
        applicable_activity_ids: ["rhythm_warmup", "exit_ticket_review"],
        classroom_use: "用于课后整理学生音乐学习证据，服务复盘、下节课调整和教研分享。",
        quality_gates: ["record_schema_bound", "student_privacy_safe", "teacher_summary_available"]
      }
    ],
    scenario_templates: [
      {
        scenario_template_id: "substitute_teacher_mode",
        label: "代课模式",
        classroom_scenario: "临时代课、教师不熟悉教材或需要低风险流程。",
        composition: "低风险听辨/节奏热身 + 清晰投屏步骤 + 自动提示 + 教师一键重置。",
        image_generation: "optional_image_gen",
        recommended_activity_ids: ["rhythm_warmup", "lesson_opening_hook", "listen_choose_explain"],
        teacher_controls: ["playback", "tempo", "show_hint", "reset", "result_review"],
        music_education_guardrails: ["不能脱离音乐学习目标", "不能只做课堂管理或普通游戏"],
        quality_gates: ["low_risk_flow", "teacher_prompt_visible", "reset_available"]
      },
      {
        scenario_template_id: "festival_music_pack",
        label: "节日音乐活动",
        classroom_scenario: "六一、春节、校园活动或主题音乐周。",
        composition: "节奏、动作、合奏、展示和祝福语创编，围绕节日音乐素材完成。",
        image_generation: "requires_image_gen",
        recommended_activity_ids: ["lesson_opening_hook", "body_percussion_builder", "orff_percussion_ensemble"],
        teacher_controls: ["tempo", "group_rotation", "classroom_timer", "result_review", "reset"],
        music_education_guardrails: ["不能脱离音乐学习目标", "必须绑定节日音乐材料"],
        quality_gates: ["festival_music_material_bound", "performance_or_creation_ready", "visual_assets_marked_if_missing"]
      }
    ],
    teacher_control_packs: [
      {
        control_pack_id: "tempo_control_pack",
        label: "速度控制包",
        classroom_problem: "教师需要根据学生表现现场调速。",
        controls: ["BPM", "慢速", "原速", "加速"],
        teacher_actions: ["set_bpm", "slow_down", "restore_tempo", "speed_up"],
        music_education_use: "用于节奏、学唱和器乐活动的分层练习。",
        quality_gates: ["tempo_applies", "student_state_preserved", "reset_restores_default"],
        control_logic: {
          reset_behavior: "一键回到本轮初始状态，保留原始音乐材料。",
          teacher_priority_over_auto_adaptive: true,
          auto_adjustment_requires_visible_reason: true,
          projector_safe: true,
          grade_band_policy: {
            lower_primary: "低段只显示必要控制。",
            middle_primary: "中段可增加难度和结果回看。",
            upper_primary: "高段可开放更多创编和导出控制。"
          }
        }
      },
      {
        control_pack_id: "mute_solo_pack",
        label: "合奏控制包",
        classroom_problem: "合奏时教师需要让某个声部独奏、静音或全开。",
        controls: ["全部", "独奏", "静音", "轮奏"],
        teacher_actions: ["all_on", "solo_group", "mute_group", "rotate_parts"],
        music_education_use: "用于听清声部、控制音量平衡和练习按时进入。",
        quality_gates: ["mute_applies", "solo_applies", "ensemble_state_recorded"],
        control_logic: {
          reset_behavior: "一键恢复全部声部打开，保留小组任务。",
          teacher_priority_over_auto_adaptive: true,
          auto_adjustment_requires_visible_reason: true,
          projector_safe: true,
          grade_band_policy: {
            lower_primary: "低段少用复杂声部控制。",
            middle_primary: "中段可独奏/全开对比。",
            upper_primary: "高段可静音、独奏、轮奏。"
          }
        }
      }
    ],
    music_rules: [
      {
        rule_id: "rhythm_timing_judgement",
        name: "拍点早晚判定",
        rule_family: "rhythm",
        inputs: ["tap_time_ms", "target_time_ms", "tolerance_ms"],
        outputs: ["early", "on_time", "late", "miss"],
        music_elements: ["稳定拍", "节奏"],
        student_practices: ["listen", "tap", "move"],
        feedback_contract: {
          status: "规则判定状态",
          music_reason: "说明学生表现背后的音乐原因",
          student_feedback: "给学生的短反馈",
          teacher_suggestion: "给教师的下一步调节建议",
          next_practice: "建议回到哪一步音乐实践",
          requires_teacher_confirm: "是否需要教师确认"
        },
        pedagogy_guardrails: ["低段重点反馈稳不稳、早还是晚"],
        applicable_activity_ids: ["rhythm_warmup"]
      }
    ],
    instrument_audio_packs: [
      {
        audio_pack_id: "primary_instrument_audio_pack",
        label: "小学乐器听辨音频包",
        sample_status: "fallback_ready_needs_open_samples",
        items: [
          {
            instrument_id: "dizi",
            label: "笛子",
            audio_source_kind: "soundfont_fallback",
            playback_instrument: "flute",
            is_real_sample: false,
            exact_real_instrument_sample: false,
            sample_fidelity: "not_real_sample",
            playable_status: "pending_exact_sample",
            classroom_note: "这是课堂可听 fallback，能支持先听再分，但不能标记为真实采样。"
          },
          {
            instrument_id: "hand_drum",
            label: "小鼓",
            audio_source_kind: "webaudio_synthesis",
            playback_instrument: "standard_drum_kit",
            is_real_sample: false,
            exact_real_instrument_sample: false,
            sample_fidelity: "not_real_sample",
            playable_status: "pending_exact_sample",
            classroom_note: "这是 WebAudio 合成打击音，能替代课堂即时操作音，但不能标记为真实采样。"
          }
        ]
      },
      {
        audio_pack_id: "primary_playable_instrument_sample_pack",
        label: "小学可演奏乐器采样演奏包",
        sample_status: "sampled_playback_ready_needs_exact_samples",
        items: [
          {
            instrument_id: "flute_playable_board",
            label: "长笛演奏板",
            audio_source_kind: "open_sample",
            playback_instrument: "flute",
            is_real_sample: true,
            exact_real_instrument_sample: true,
            sample_fidelity: "exact_open_sample",
            playable_status: "ready_real_sample",
            classroom_note: "这是本地 SoundFont 长笛采样音色，可用于长笛演奏板。"
          },
          {
            instrument_id: "dizi_playable_board",
            label: "笛子演奏板",
            audio_source_kind: "open_sample",
            playback_instrument: "flute",
            is_real_sample: true,
            exact_real_instrument_sample: false,
            sample_fidelity: "approximate_soundfont_sample",
            playable_status: "ready_soundfont_proxy",
            classroom_note: "这是本地 SoundFont 长笛采样近似音色，用于笛子演奏板先行可奏；待补笛子实录。"
          },
          {
            instrument_id: "shaker",
            label: "虚拟沙锤",
            audio_source_kind: "open_sample",
            playback_instrument: "agogo",
            is_real_sample: true,
            exact_real_instrument_sample: false,
            sample_fidelity: "approximate_soundfont_sample",
            playable_status: "ready_soundfont_proxy",
            classroom_note: "这是本地 SoundFont 近似采样，待补沙锤实录。"
          }
        ]
      }
    ]
  };
}

async function launchChrome() {
  const executable = await chromeExecutable();
  const port = 9222 + Math.floor(Math.random() * 1000);
  const userDataDir = await mkdtemp(join(tmpdir(), "primary-activity-smoke-"));
  const args = [
    `--remote-debugging-port=${port}`,
    `--user-data-dir=${userDataDir}`,
    "--headless=new",
    "--disable-gpu",
    "--no-first-run",
    "--no-default-browser-check",
    "about:blank",
  ];
  const child = spawn(executable, args, { stdio: "ignore" });
  return {
    port,
    close: async () => {
      if (!child.killed) child.kill("SIGTERM");
      await delay(250);
      await rm(userDataDir, { recursive: true, force: true });
    },
  };
}

async function chromeExecutable() {
  const candidates = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
  ];
  for (const candidate of candidates) {
    try {
      await access(candidate);
      return candidate;
    } catch {
      // Try the next known browser path.
    }
  }
  throw new Error("No local Chrome-compatible browser found for screenshot smoke.");
}

async function waitForDevTools(port) {
  const url = `http://127.0.0.1:${port}/json/version`;
  for (let attempt = 0; attempt < 80; attempt += 1) {
    try {
      const response = await fetch(url);
      if (response.ok) return { port };
    } catch {
      await delay(100);
    }
  }
  throw new Error("Chrome DevTools endpoint did not start.");
}

async function smokeViewport(endpoint, origin, target, viewport) {
  const tab = await createTab(endpoint.port, `${origin}${target.path}`);
  const socket = new WebSocket(tab.webSocketDebuggerUrl);
  const cdp = createCdpClient(socket);
  const consoleErrors = [];
  await cdp.ready;
  cdp.on("Runtime.consoleAPICalled", (params) => {
    if (params.type === "error") {
      consoleErrors.push(params.args.map((arg) => arg.value || arg.description || "").join(" "));
    }
  });
  cdp.on("Runtime.exceptionThrown", (params) => {
    consoleErrors.push(params.exceptionDetails?.text || "Runtime exception");
  });
  await cdp.send("Runtime.enable");
  await cdp.send("Page.enable");
  await cdp.send("Emulation.setDeviceMetricsOverride", {
    width: viewport.width,
    height: viewport.height,
    deviceScaleFactor: viewport.mobile ? 2 : 1,
    mobile: viewport.mobile,
  });
  if (target.preloadExpression) {
    await cdp.send("Page.addScriptToEvaluateOnNewDocument", {
      source: target.preloadExpression,
    });
  }
  await cdp.send("Page.navigate", { url: `${origin}${target.path}` });
  await waitForLoad(cdp);
  await cdp.send("Runtime.evaluate", {
    expression: "document.fonts ? document.fonts.ready.then(() => true) : true",
    awaitPromise: true,
  });
  await delay(400);

  const before = await evaluate(cdp, smokeExpression(target.rootSelector));
  for (const expression of target.actionExpressions || [target.actionExpression]) {
    await cdp.send("Runtime.evaluate", {
      expression,
      awaitPromise: true,
    });
    await delay(180);
  }
  const after = await evaluate(cdp, smokeExpression(target.rootSelector));
  const screenshotFile = `${target.screenshotPrefix}-${viewport.name}.png`;
  const screenshotPath = join(snapshotsDir, screenshotFile);
  const screenshot = await cdp.send("Page.captureScreenshot", { format: "png", captureBeyondViewport: true });
  writeFileSync(screenshotPath, Buffer.from(screenshot.data, "base64"));
  socket.close();
  await closeTab(endpoint.port, tab.id);

  const failures = [];
  for (const text of target.beforeTexts) {
    if (!before.body_text.includes(text)) failures.push(`missing text: ${text}`);
  }
  if (!before.h1.includes(target.h1Text)) failures.push("missing h1");
  if (!after.body_text.includes(target.afterText)) failures.push(`missing after text: ${target.afterText}`);
  failures.push(...target.extraChecks(before, after));
  if (after.horizontal_overflow) failures.push("horizontal overflow detected");

  return {
    viewport_report: {
      target: target.id,
      name: viewport.name,
      viewport: { width: viewport.width, height: viewport.height, mobile: viewport.mobile },
      h1: before.h1,
      root_children: before.root_children,
      teacher_control_visible: before.teacher_control_visible,
      rhythm_pad_visible: before.rhythm_pad_visible,
      tap_feedback_after_click: after.tap_feedback,
      horizontal_overflow: after.horizontal_overflow,
      failures,
    },
    console_errors: consoleErrors,
    screenshot: {
      target: target.id,
      viewport: viewport.name,
      path: `frontend/tests/browser-snapshots/${screenshotFile}`,
      status: "captured",
    },
  };
}

function smokeExpression(rootSelector) {
  return `(() => {
    const bodyText = document.body?.innerText || "";
    const tapNode = Array.from(document.querySelectorAll('p,span,div')).find((node) => (node.textContent || '').includes('已敲'));
    return {
      title: document.title,
      h1: document.querySelector('h1')?.textContent || '',
      body_text: bodyText,
      root_children: document.querySelector(${JSON.stringify(rootSelector)})?.children.length || 0,
      teacher_control_visible: !!document.querySelector('[aria-label="教师控制条"]')?.getBoundingClientRect().width,
      rhythm_pad_visible: !!document.querySelector('[aria-label="敲击节奏垫"]')?.getBoundingClientRect().width,
      tap_feedback: tapNode?.textContent || '',
      mood_card_image_count: document.querySelectorAll('.mood-card img').length,
      generated_asset_task_count: document.querySelectorAll('.doubao-task-card').length,
      horizontal_overflow: document.documentElement.scrollWidth > window.innerWidth + 2
    };
  })()`;
}

async function evaluate(cdp, expression) {
  const result = await cdp.send("Runtime.evaluate", {
    expression,
    returnByValue: true,
    awaitPromise: true,
  });
  return result.result.value;
}

async function createTab(port, url) {
  const response = await fetchWithTimeout(`http://127.0.0.1:${port}/json/new?${encodeURIComponent(url)}`, { method: "PUT" }, 5000);
  if (!response.ok) throw new Error(`Unable to create Chrome tab: ${response.status}`);
  return response.json();
}

async function closeTab(port, id) {
  await fetchWithTimeout(`http://127.0.0.1:${port}/json/close/${id}`, {}, 1000).catch(() => {});
}

async function fetchWithTimeout(url, options = {}, timeoutMs = 5000) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, { ...options, signal: controller.signal });
  } finally {
    clearTimeout(timeout);
  }
}

async function waitForLoad(cdp) {
  await new Promise((resolveLoad) => {
    const timeout = setTimeout(resolveLoad, 5000);
    cdp.on("Page.loadEventFired", () => {
      clearTimeout(timeout);
      resolveLoad();
    });
  });
}

function createCdpClient(socket) {
  let nextId = 1;
  const pending = new Map();
  const listeners = new Map();
  const ready = new Promise((resolveReady, rejectReady) => {
    socket.addEventListener("open", resolveReady, { once: true });
    socket.addEventListener("error", rejectReady, { once: true });
  });
  socket.addEventListener("message", (event) => {
    const message = JSON.parse(event.data);
    if (message.id && pending.has(message.id)) {
      const { resolveRequest, rejectRequest } = pending.get(message.id);
      pending.delete(message.id);
      if (message.error) rejectRequest(new Error(message.error.message));
      else resolveRequest(message.result || {});
      return;
    }
    if (message.method && listeners.has(message.method)) {
      for (const listener of listeners.get(message.method)) listener(message.params || {});
    }
  });
  return {
    ready,
    send(method, params = {}) {
      const id = nextId++;
      socket.send(JSON.stringify({ id, method, params }));
      return new Promise((resolveRequest, rejectRequest) => {
        pending.set(id, { resolveRequest, rejectRequest });
      });
    },
    on(method, listener) {
      if (!listeners.has(method)) listeners.set(method, []);
      listeners.get(method).push(listener);
    },
  };
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
