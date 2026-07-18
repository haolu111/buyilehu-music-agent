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
var AppShell_vue_1 = require("../components/AppShell.vue");
var LessonWorkspaceNav_vue_1 = require("../components/LessonWorkspaceNav.vue");
var lessonPlanApi_1 = require("../api/lessonPlanApi");
var display_1 = require("../utils/display");
var lessonPlans = (0, vue_1.ref)([]);
var loading = (0, vue_1.ref)(false);
var error = (0, vue_1.ref)('');
var query = (0, vue_1.ref)('');
var statusFilter = (0, vue_1.ref)('all');
var filteredPlans = (0, vue_1.computed)(function () { return lessonPlans.value.filter(function (plan) { return (!query.value || plan.title.toLowerCase().includes(query.value.toLowerCase())) && (statusFilter.value === 'all' || plan.parseStatus === statusFilter.value); }); });
function loadLessonPlans() {
    return __awaiter(this, void 0, void 0, function () {
        var _a, e_1;
        return __generator(this, function (_b) {
            switch (_b.label) {
                case 0:
                    loading.value = true;
                    error.value = '';
                    _b.label = 1;
                case 1:
                    _b.trys.push([1, 3, 4, 5]);
                    _a = lessonPlans;
                    return [4 /*yield*/, lessonPlanApi_1.lessonPlanApi.listMine()];
                case 2:
                    _a.value = _b.sent();
                    return [3 /*break*/, 5];
                case 3:
                    e_1 = _b.sent();
                    error.value = e_1 instanceof Error ? e_1.message : '加载教案失败';
                    return [3 /*break*/, 5];
                case 4:
                    loading.value = false;
                    return [7 /*endfinally*/];
                case 5: return [2 /*return*/];
            }
        });
    });
}
function nextAction(plan) {
    if (plan.parseStatus === 'processing')
        return '查看解析进度';
    if (plan.parseStatus === 'failed')
        return '重新上传并解析';
    if (plan.status === 'confirmed')
        return '设置课堂';
    return '确认解析内容';
}
function nextRoute(plan) {
    if (plan.parseStatus === 'failed')
        return "/lesson-plans/upload?retryLessonPlanId=".concat(plan.id);
    return plan.status === 'confirmed' ? "/packages/generate?lessonPlanId=".concat(plan.id) : "/lesson-plans/".concat(plan.id, "/parse-result");
}
(0, vue_1.onMounted)(loadLessonPlans);
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
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "page-heading compact" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "eyebrow" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.h1, __VLS_intrinsicElements.h1)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
var __VLS_7 = {}.RouterLink;
/** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
// @ts-ignore
var __VLS_8 = __VLS_asFunctionalComponent(__VLS_7, new __VLS_7(__assign({ class: "button primary" }, { to: "/lesson-plans/upload" })));
var __VLS_9 = __VLS_8.apply(void 0, __spreadArray([__assign({ class: "button primary" }, { to: "/lesson-plans/upload" })], __VLS_functionalComponentArgsRest(__VLS_8), false));
__VLS_10.slots.default;
var __VLS_11 = {}.FileUp;
/** @type {[typeof __VLS_components.FileUp, ]} */ ;
// @ts-ignore
var __VLS_12 = __VLS_asFunctionalComponent(__VLS_11, new __VLS_11({
    size: (18),
    'aria-hidden': "true",
}));
var __VLS_13 = __VLS_12.apply(void 0, __spreadArray([{
        size: (18),
        'aria-hidden': "true",
    }], __VLS_functionalComponentArgsRest(__VLS_12), false));
var __VLS_10;
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "filter-bar" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)(__assign({ class: "search-field" }));
var __VLS_15 = {}.Search;
/** @type {[typeof __VLS_components.Search, ]} */ ;
// @ts-ignore
var __VLS_16 = __VLS_asFunctionalComponent(__VLS_15, new __VLS_15({
    size: (18),
    'aria-hidden': "true",
}));
var __VLS_17 = __VLS_16.apply(void 0, __spreadArray([{
        size: (18),
        'aria-hidden': "true",
    }], __VLS_functionalComponentArgsRest(__VLS_16), false));
__VLS_asFunctionalElement(__VLS_intrinsicElements.input, __VLS_intrinsicElements.input)({
    placeholder: "搜索教案名称",
    'aria-label': "搜索教案名称",
});
(__VLS_ctx.query);
__VLS_asFunctionalElement(__VLS_intrinsicElements.select, __VLS_intrinsicElements.select)({
    value: (__VLS_ctx.statusFilter),
    'aria-label': "按解析状态筛选",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
    value: "all",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
    value: "success",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
    value: "processing",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
    value: "failed",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign(__assign({ onClick: (__VLS_ctx.loadLessonPlans) }, { class: "button ghost" }), { type: "button", disabled: (__VLS_ctx.loading) }));
var __VLS_19 = {}.RefreshCw;
/** @type {[typeof __VLS_components.RefreshCw, ]} */ ;
// @ts-ignore
var __VLS_20 = __VLS_asFunctionalComponent(__VLS_19, new __VLS_19({
    size: (17),
    'aria-hidden': "true",
}));
var __VLS_21 = __VLS_20.apply(void 0, __spreadArray([{
        size: (17),
        'aria-hidden': "true",
    }], __VLS_functionalComponentArgsRest(__VLS_20), false));
if (__VLS_ctx.error) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "error" }));
    (__VLS_ctx.error);
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)(__assign({ class: "lesson-plan-list" }, { 'aria-label': "教案列表" }));
for (var _i = 0, _a = __VLS_getVForSourceType((__VLS_ctx.filteredPlans)); _i < _a.length; _i++) {
    var plan = _a[_i][0];
    __VLS_asFunctionalElement(__VLS_intrinsicElements.article, __VLS_intrinsicElements.article)(__assign({ key: (plan.id) }, { class: "lesson-plan-row" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "lesson-plan-title" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
    (plan.title);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.small, __VLS_intrinsicElements.small)({});
    (__VLS_ctx.formatDateTime(plan.updatedAt || plan.createdAt));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)(__assign({ class: "status-pill" }, { class: (plan.parseStatus) }));
    (__VLS_ctx.statusText(plan.parseStatus));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)(__assign({ class: "lesson-plan-status" }));
    (plan.parseStatus === 'success' ? (plan.status === 'confirmed' ? '已确认' : '待确认') : '等待解析');
    var __VLS_23 = {}.RouterLink;
    /** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
    // @ts-ignore
    var __VLS_24 = __VLS_asFunctionalComponent(__VLS_23, new __VLS_23(__assign({ class: "button lesson-plan-action" }, { dataTestid: "lesson-plan-next-action", to: (__VLS_ctx.nextRoute(plan)) })));
    var __VLS_25 = __VLS_24.apply(void 0, __spreadArray([__assign({ class: "button lesson-plan-action" }, { dataTestid: "lesson-plan-next-action", to: (__VLS_ctx.nextRoute(plan)) })], __VLS_functionalComponentArgsRest(__VLS_24), false));
    __VLS_26.slots.default;
    (__VLS_ctx.nextAction(plan));
    var __VLS_27 = {}.ArrowRight;
    /** @type {[typeof __VLS_components.ArrowRight, ]} */ ;
    // @ts-ignore
    var __VLS_28 = __VLS_asFunctionalComponent(__VLS_27, new __VLS_27({
        size: (16),
        'aria-hidden': "true",
    }));
    var __VLS_29 = __VLS_28.apply(void 0, __spreadArray([{
            size: (16),
            'aria-hidden': "true",
        }], __VLS_functionalComponentArgsRest(__VLS_28), false));
    var __VLS_26;
}
if (!__VLS_ctx.filteredPlans.length) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "empty-inline" }));
    (__VLS_ctx.loading ? '正在加载教案…' : '没有符合条件的教案');
}
var __VLS_2;
/** @type {__VLS_StyleScopedClasses['page-heading']} */ ;
/** @type {__VLS_StyleScopedClasses['compact']} */ ;
/** @type {__VLS_StyleScopedClasses['eyebrow']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['primary']} */ ;
/** @type {__VLS_StyleScopedClasses['filter-bar']} */ ;
/** @type {__VLS_StyleScopedClasses['search-field']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['ghost']} */ ;
/** @type {__VLS_StyleScopedClasses['error']} */ ;
/** @type {__VLS_StyleScopedClasses['lesson-plan-list']} */ ;
/** @type {__VLS_StyleScopedClasses['lesson-plan-row']} */ ;
/** @type {__VLS_StyleScopedClasses['lesson-plan-title']} */ ;
/** @type {__VLS_StyleScopedClasses['status-pill']} */ ;
/** @type {__VLS_StyleScopedClasses['lesson-plan-status']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['lesson-plan-action']} */ ;
/** @type {__VLS_StyleScopedClasses['empty-inline']} */ ;
var __VLS_dollars;
var __VLS_self = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () {
        return {
            ArrowRight: lucide_vue_next_1.ArrowRight,
            FileUp: lucide_vue_next_1.FileUp,
            RefreshCw: lucide_vue_next_1.RefreshCw,
            Search: lucide_vue_next_1.Search,
            AppShell: AppShell_vue_1.default,
            LessonWorkspaceNav: LessonWorkspaceNav_vue_1.default,
            formatDateTime: display_1.formatDateTime,
            statusText: display_1.statusText,
            loading: loading,
            error: error,
            query: query,
            statusFilter: statusFilter,
            filteredPlans: filteredPlans,
            loadLessonPlans: loadLessonPlans,
            nextAction: nextAction,
            nextRoute: nextRoute,
        };
    },
});
exports.default = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () {
        return {};
    },
});
; /* PartiallyEnd: #4569/main.vue */
