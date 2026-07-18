"use strict";
var __assign = (this && this.__assign) || function () {
    __assign = Object.assign || function(t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
            s = arguments[i];
            for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                t[p] = s[p];
        }
        return t;
    };
    return __assign.apply(this, arguments);
};
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g = Object.create((typeof Iterator === "function" ? Iterator : Object).prototype);
    return g.next = verb(0), g["throw"] = verb(1), g["return"] = verb(2), typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (g && (g = 0, op[0] && (_ = 0)), _) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
var __spreadArray = (this && this.__spreadArray) || function (to, from, pack) {
    if (pack || arguments.length === 2) for (var i = 0, l = from.length, ar; i < l; i++) {
        if (ar || !(i in from)) {
            if (!ar) ar = Array.prototype.slice.call(from, 0, i);
            ar[i] = from[i];
        }
    }
    return to.concat(ar || Array.prototype.slice.call(from));
};
Object.defineProperty(exports, "__esModule", { value: true });
/* placeholder */
var vue_1 = require("vue");
var lucide_vue_next_1 = require("lucide-vue-next");
var vue_router_1 = require("vue-router");
var AppShell_vue_1 = require("../components/AppShell.vue");
var LessonWorkspaceNav_vue_1 = require("../components/LessonWorkspaceNav.vue");
var WorkflowStepper_vue_1 = require("../components/WorkflowStepper.vue");
var packageApi_1 = require("../api/packageApi");
var lessonPlanApi_1 = require("../api/lessonPlanApi");
var route = (0, vue_router_1.useRoute)();
var router = (0, vue_router_1.useRouter)();
var plans = (0, vue_1.ref)([]);
var lessonPlanId = (0, vue_1.ref)(String(route.query.lessonPlanId || ''));
var loading = (0, vue_1.ref)(false);
var error = (0, vue_1.ref)('');
var job = (0, vue_1.ref)(null);
var duration = (0, vue_1.ref)('40');
var mode = (0, vue_1.ref)('individual');
var density = (0, vue_1.ref)('standard');
var difficulty = (0, vue_1.ref)('grade');
var flow = (0, vue_1.ref)('teacher');
var theme = (0, vue_1.ref)('auto');
var statusSubscription = null;
var generationProgress = (0, vue_1.computed)(function () { var _a; return Math.max(0, Math.min(100, Number(((_a = job.value) === null || _a === void 0 ? void 0 : _a.progress) || 0))); });
var generationPhase = (0, vue_1.computed)(function () {
    var _a;
    if ((_a = job.value) === null || _a === void 0 ? void 0 : _a.message)
        return job.value.message;
    var progress = generationProgress.value;
    if (progress < 35)
        return '教学设计 Agent 正在生成活动结构';
    if (progress < 50)
        return '正在匹配一一对应的活动组件';
    if (progress < 75)
        return 'LangGraph 正在构建素材并执行教学质量审计';
    if (progress < 85)
        return '正在执行结构与业务校验';
    if (progress < 95)
        return '正在生成正式共享活动组件';
    return '正在保存活动包和审核报告';
});
var generationSteps = (0, vue_1.computed)(function () {
    var progress = generationProgress.value;
    return [
        { key: 'design', label: '教学设计', detail: '生成活动结构', start: 10, done: 35 },
        { key: 'matching', label: '组件匹配', detail: '建立活动与组件一一映射', start: 40, done: 50 },
        { key: 'materials', label: '活动构建', detail: '构建音乐素材与运行参数', start: 55, done: 75 },
        { key: 'audit', label: '质量审计', detail: '质量 Agent 与业务规则校验', start: 78, done: 85 },
        { key: 'persist', label: '保存发布', detail: '保存共享配置与审核报告', start: 88, done: 100 },
    ].map(function (step) { return (__assign(__assign({}, step), { state: progress >= step.done ? 'done' : progress >= step.start ? 'active' : 'waiting' })); });
});
function handleStatus(status) {
    return __awaiter(this, void 0, void 0, function () {
        var detail;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    job.value = status;
                    if (!(status.status === 'failed')) return [3 /*break*/, 1];
                    loading.value = false;
                    detail = status.errorMessage || '';
                    error.value = detail.includes('timed out')
                        ? '教学设计服务响应超时。本次任务已停止，请重新生成；系统会在审计模型超时时自动使用规则审计。'
                        : detail || '生成失败，请稍后重试';
                    statusSubscription === null || statusSubscription === void 0 ? void 0 : statusSubscription.abort();
                    return [3 /*break*/, 3];
                case 1:
                    if (!status.packageId) return [3 /*break*/, 3];
                    loading.value = false;
                    statusSubscription === null || statusSubscription === void 0 ? void 0 : statusSubscription.abort();
                    return [4 /*yield*/, router.push("/packages/".concat(status.packageId, "/proposal"))];
                case 2:
                    _a.sent();
                    _a.label = 3;
                case 3: return [2 /*return*/];
            }
        });
    });
}
function generate() {
    return __awaiter(this, void 0, void 0, function () {
        var created, caught_1;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    if (!lessonPlanId.value) {
                        error.value = '请选择一份已解析的教案';
                        return [2 /*return*/];
                    }
                    statusSubscription === null || statusSubscription === void 0 ? void 0 : statusSubscription.abort();
                    loading.value = true;
                    error.value = '';
                    job.value = null;
                    _a.label = 1;
                case 1:
                    _a.trys.push([1, 4, , 5]);
                    return [4 /*yield*/, packageApi_1.packageApi.createGenerationJob(Number(lessonPlanId.value), {
                            duration: Number(duration.value),
                            mode: mode.value,
                            density: density.value,
                            difficulty: difficulty.value,
                            flow: flow.value,
                            theme: theme.value,
                        })];
                case 2:
                    created = _a.sent();
                    return [4 /*yield*/, handleStatus(created)];
                case 3:
                    _a.sent();
                    if (created.status !== 'success' && created.status !== 'failed') {
                        statusSubscription = packageApi_1.packageApi.watchGenerationJob(created.id, handleStatus, function (subscriptionError) {
                            error.value = subscriptionError.message;
                        });
                    }
                    return [3 /*break*/, 5];
                case 4:
                    caught_1 = _a.sent();
                    loading.value = false;
                    error.value = caught_1 instanceof Error ? caught_1.message : '生成失败，请重试';
                    return [3 /*break*/, 5];
                case 5: return [2 /*return*/];
            }
        });
    });
}
(0, vue_1.onMounted)(function () { return __awaiter(void 0, void 0, void 0, function () {
    var _a, _b;
    return __generator(this, function (_c) {
        switch (_c.label) {
            case 0:
                _c.trys.push([0, 2, , 3]);
                _a = plans;
                return [4 /*yield*/, lessonPlanApi_1.lessonPlanApi.listMine()];
            case 1:
                _a.value = (_c.sent()).filter(function (item) { return item.parseStatus === 'success'; });
                return [3 /*break*/, 3];
            case 2:
                _b = _c.sent();
                error.value = '无法加载教案列表，请重试';
                return [3 /*break*/, 3];
            case 3: return [2 /*return*/];
        }
    });
}); });
(0, vue_1.onUnmounted)(function () { return statusSubscription === null || statusSubscription === void 0 ? void 0 : statusSubscription.abort(); });
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
var __VLS_ctx = {};
var __VLS_components;
var __VLS_directives;
/** @type {[typeof AppShell, typeof AppShell, ]} */ ;
// @ts-ignore
var __VLS_0 = __VLS_asFunctionalComponent(AppShell_vue_1.default, new AppShell_vue_1.default({}));
var __VLS_1 = __VLS_0.apply(void 0, __spreadArray([{}], __VLS_functionalComponentArgsRest(__VLS_0), false));
var __VLS_3 = {};
__VLS_2.slots.default;
/** @type {[typeof LessonWorkspaceNav, ]} */ ;
// @ts-ignore
var __VLS_4 = __VLS_asFunctionalComponent(LessonWorkspaceNav_vue_1.default, new LessonWorkspaceNav_vue_1.default({}));
var __VLS_5 = __VLS_4.apply(void 0, __spreadArray([{}], __VLS_functionalComponentArgsRest(__VLS_4), false));
/** @type {[typeof WorkflowStepper, ]} */ ;
// @ts-ignore
var __VLS_7 = __VLS_asFunctionalComponent(WorkflowStepper_vue_1.default, new WorkflowStepper_vue_1.default({
    currentStage: "setup-classroom",
    lessonPlanId: (__VLS_ctx.lessonPlanId),
}));
var __VLS_8 = __VLS_7.apply(void 0, __spreadArray([{
        currentStage: "setup-classroom",
        lessonPlanId: (__VLS_ctx.lessonPlanId),
    }], __VLS_functionalComponentArgsRest(__VLS_7), false));
__VLS_asFunctionalElement(__VLS_intrinsicElements.header, __VLS_intrinsicElements.header)(__assign({ class: "page-heading compact" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "eyebrow" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.h1, __VLS_intrinsicElements.h1)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)(__assign({ class: "card generation-form" }, { 'aria-busy': (__VLS_ctx.loading) }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)(__assign({ class: "full-field field-with-icon" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
var __VLS_10 = {}.FileText;
/** @type {[typeof __VLS_components.FileText, ]} */ ;
// @ts-ignore
var __VLS_11 = __VLS_asFunctionalComponent(__VLS_10, new __VLS_10({
    size: (18),
    'aria-hidden': "true",
}));
var __VLS_12 = __VLS_11.apply(void 0, __spreadArray([{
        size: (18),
        'aria-hidden': "true",
    }], __VLS_functionalComponentArgsRest(__VLS_11), false));
__VLS_asFunctionalElement(__VLS_intrinsicElements.select, __VLS_intrinsicElements.select)({
    value: (__VLS_ctx.lessonPlanId),
    name: "lesson-plan",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
    value: "",
    disabled: true,
});
for (var _i = 0, _a = __VLS_getVForSourceType((__VLS_ctx.plans)); _i < _a.length; _i++) {
    var plan = _a[_i][0];
    __VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
        key: (plan.id),
        value: (String(plan.id)),
    });
    (plan.title);
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "settings-grid essentials-grid" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)(__assign({ class: "field-with-icon" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
var __VLS_14 = {}.Clock3;
/** @type {[typeof __VLS_components.Clock3, ]} */ ;
// @ts-ignore
var __VLS_15 = __VLS_asFunctionalComponent(__VLS_14, new __VLS_14({
    size: (18),
    'aria-hidden': "true",
}));
var __VLS_16 = __VLS_15.apply(void 0, __spreadArray([{
        size: (18),
        'aria-hidden': "true",
    }], __VLS_functionalComponentArgsRest(__VLS_15), false));
__VLS_asFunctionalElement(__VLS_intrinsicElements.select, __VLS_intrinsicElements.select)({
    value: (__VLS_ctx.duration),
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
    value: "30",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
    value: "40",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
    value: "45",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)(__assign({ class: "field-with-icon" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
var __VLS_18 = {}.UsersRound;
/** @type {[typeof __VLS_components.UsersRound, ]} */ ;
// @ts-ignore
var __VLS_19 = __VLS_asFunctionalComponent(__VLS_18, new __VLS_18({
    size: (18),
    'aria-hidden': "true",
}));
var __VLS_20 = __VLS_19.apply(void 0, __spreadArray([{
        size: (18),
        'aria-hidden': "true",
    }], __VLS_functionalComponentArgsRest(__VLS_19), false));
__VLS_asFunctionalElement(__VLS_intrinsicElements.select, __VLS_intrinsicElements.select)({
    value: (__VLS_ctx.mode),
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
    value: "individual",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
    value: "group",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
    value: "teacher",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.details, __VLS_intrinsicElements.details)(__assign({ class: "generation-advanced" }, { 'data-testid': "advanced-generation-settings" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.summary, __VLS_intrinsicElements.summary)({});
var __VLS_22 = {}.Settings2;
/** @type {[typeof __VLS_components.Settings2, ]} */ ;
// @ts-ignore
var __VLS_23 = __VLS_asFunctionalComponent(__VLS_22, new __VLS_22({
    size: (18),
    'aria-hidden': "true",
}));
var __VLS_24 = __VLS_23.apply(void 0, __spreadArray([{
        size: (18),
        'aria-hidden': "true",
    }], __VLS_functionalComponentArgsRest(__VLS_23), false));
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "settings-grid" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.select, __VLS_intrinsicElements.select)({
    value: (__VLS_ctx.density),
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
    value: "light",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
    value: "standard",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
    value: "rich",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.select, __VLS_intrinsicElements.select)({
    value: (__VLS_ctx.difficulty),
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
    value: "grade",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
    value: "easy",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
    value: "hard",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.select, __VLS_intrinsicElements.select)({
    value: (__VLS_ctx.flow),
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
    value: "teacher",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
    value: "auto",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.select, __VLS_intrinsicElements.select)({
    value: (__VLS_ctx.theme),
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
    value: "auto",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
    value: "stage",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
    value: "nature",
});
if (__VLS_ctx.error) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "error" }, { role: "alert" }));
    (__VLS_ctx.error);
}
if (__VLS_ctx.loading && __VLS_ctx.job) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)(__assign({ class: "generation-progress" }, { 'aria-live': "polite" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
    (__VLS_ctx.generationPhase);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
    (__VLS_ctx.generationProgress);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.progress, __VLS_intrinsicElements.progress)({
        value: (__VLS_ctx.generationProgress),
        max: "100",
    });
    (__VLS_ctx.generationProgress);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.ol, __VLS_intrinsicElements.ol)(__assign({ class: "generation-timeline" }, { 'aria-label': "生成步骤" }));
    for (var _b = 0, _c = __VLS_getVForSourceType((__VLS_ctx.generationSteps)); _b < _c.length; _b++) {
        var step = _c[_b][0];
        __VLS_asFunctionalElement(__VLS_intrinsicElements.li, __VLS_intrinsicElements.li)(__assign({ key: (step.key) }, { class: ("is-".concat(step.state)) }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.i, __VLS_intrinsicElements.i)({
            'aria-hidden': "true",
        });
        (step.state === 'done' ? '✓' : step.state === 'active' ? '●' : '');
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
        __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
        (step.label);
        __VLS_asFunctionalElement(__VLS_intrinsicElements.small, __VLS_intrinsicElements.small)({});
        (step.detail);
        __VLS_asFunctionalElement(__VLS_intrinsicElements.em, __VLS_intrinsicElements.em)({});
        (step.state === 'done' ? '已完成' : step.state === 'active' ? '进行中' : '等待中');
    }
    __VLS_asFunctionalElement(__VLS_intrinsicElements.small, __VLS_intrinsicElements.small)({});
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "button-row end" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign(__assign({ onClick: (__VLS_ctx.generate) }, { class: "button primary" }), { 'data-testid': "generate-package", disabled: (__VLS_ctx.loading || !__VLS_ctx.lessonPlanId) }));
var __VLS_26 = {}.Sparkles;
/** @type {[typeof __VLS_components.Sparkles, ]} */ ;
// @ts-ignore
var __VLS_27 = __VLS_asFunctionalComponent(__VLS_26, new __VLS_26({
    size: (18),
    'aria-hidden': "true",
}));
var __VLS_28 = __VLS_27.apply(void 0, __spreadArray([{
        size: (18),
        'aria-hidden': "true",
    }], __VLS_functionalComponentArgsRest(__VLS_27), false));
(__VLS_ctx.loading ? '正在生成方案…' : '生成活动方案');
var __VLS_2;
/** @type {__VLS_StyleScopedClasses['page-heading']} */ ;
/** @type {__VLS_StyleScopedClasses['compact']} */ ;
/** @type {__VLS_StyleScopedClasses['eyebrow']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['generation-form']} */ ;
/** @type {__VLS_StyleScopedClasses['full-field']} */ ;
/** @type {__VLS_StyleScopedClasses['field-with-icon']} */ ;
/** @type {__VLS_StyleScopedClasses['settings-grid']} */ ;
/** @type {__VLS_StyleScopedClasses['essentials-grid']} */ ;
/** @type {__VLS_StyleScopedClasses['field-with-icon']} */ ;
/** @type {__VLS_StyleScopedClasses['field-with-icon']} */ ;
/** @type {__VLS_StyleScopedClasses['generation-advanced']} */ ;
/** @type {__VLS_StyleScopedClasses['settings-grid']} */ ;
/** @type {__VLS_StyleScopedClasses['error']} */ ;
/** @type {__VLS_StyleScopedClasses['generation-progress']} */ ;
/** @type {__VLS_StyleScopedClasses['generation-timeline']} */ ;
/** @type {__VLS_StyleScopedClasses['button-row']} */ ;
/** @type {__VLS_StyleScopedClasses['end']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['primary']} */ ;
var __VLS_dollars;
var __VLS_self = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () {
        return {
            Clock3: lucide_vue_next_1.Clock3,
            FileText: lucide_vue_next_1.FileText,
            Settings2: lucide_vue_next_1.Settings2,
            Sparkles: lucide_vue_next_1.Sparkles,
            UsersRound: lucide_vue_next_1.UsersRound,
            AppShell: AppShell_vue_1.default,
            LessonWorkspaceNav: LessonWorkspaceNav_vue_1.default,
            WorkflowStepper: WorkflowStepper_vue_1.default,
            plans: plans,
            lessonPlanId: lessonPlanId,
            loading: loading,
            error: error,
            job: job,
            duration: duration,
            mode: mode,
            density: density,
            difficulty: difficulty,
            flow: flow,
            theme: theme,
            generationProgress: generationProgress,
            generationPhase: generationPhase,
            generationSteps: generationSteps,
            generate: generate,
        };
    },
});
exports.default = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () {
        return {};
    },
});
; /* PartiallyEnd: #4569/main.vue */
