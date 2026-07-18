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
var _a, _b;
Object.defineProperty(exports, "__esModule", { value: true });
/* placeholder */
var vue_1 = require("vue");
var lucide_vue_next_1 = require("lucide-vue-next");
var AppShell_vue_1 = require("../components/AppShell.vue");
var authStore_1 = require("../stores/authStore");
var classApi_1 = require("../api/classApi");
var classroomApi_1 = require("../api/classroomApi");
var lessonPlanApi_1 = require("../api/lessonPlanApi");
var packageApi_1 = require("../api/packageApi");
var display_1 = require("../utils/display");
var music_children_orff_banner_png_1 = require("../assets/music-children-orff-banner.png");
var music_dashboard_decorations_png_1 = require("../assets/music-dashboard-decorations.png");
var music_workspace_stickers_png_1 = require("../assets/music-workspace-stickers.png");
var auth = (0, authStore_1.useAuthStore)();
var sessions = (0, vue_1.ref)([]);
var classes = (0, vue_1.ref)([]);
var plans = (0, vue_1.ref)([]);
var packages = (0, vue_1.ref)([]);
var loading = (0, vue_1.ref)(true);
var loadError = (0, vue_1.ref)('');
var teacherName = (0, vue_1.computed)(function () { var _a, _b; return ((_a = auth.user) === null || _a === void 0 ? void 0 : _a.displayName) || ((_b = auth.user) === null || _b === void 0 ? void 0 : _b.realName) || '老师'; });
var liveSession = (0, vue_1.computed)(function () { return sessions.value.find(function (item) { return ['running', 'paused'].includes(item.status); }) || sessions.value.find(function (item) { return item.status === 'not_started'; }); });
var pendingPlans = (0, vue_1.computed)(function () { return plans.value.filter(function (item) { return item.parseStatus === 'success' && item.status !== 'confirmed'; }).length; });
var readyPackageStatuses = ['generated', 'confirmed', 'draft', 'modified'];
var readyPackages = (0, vue_1.computed)(function () { return packages.value.filter(function (item) { return readyPackageStatuses.includes(item.status); }).length; });
var firstReadyPackage = (0, vue_1.computed)(function () { return packages.value.find(function (item) { return readyPackageStatuses.includes(item.status); }); });
var upcomingCount = (0, vue_1.computed)(function () { return sessions.value.filter(function (item) { return item.status === 'not_started'; }).length; });
var recentPackages = (0, vue_1.computed)(function () { return packages.value.slice(0, 2); });
var recentClasses = (0, vue_1.computed)(function () { return classes.value.slice(0, 2); });
var visibleContinueItems = (0, vue_1.computed)(function () { return continueItems.value.slice(0, 2); });
var classroomEntryRoute = (0, vue_1.computed)(function () { return liveSession.value ? "/classroom/".concat(liveSession.value.id, "/control") : '/classrooms'; });
var currentClassNode = (0, vue_1.computed)(function () { var _a, _b; return ((_a = liveSession.value) === null || _a === void 0 ? void 0 : _a.nodeStates.find(function (node) { var _a; return node.activityNodeId === ((_a = liveSession.value) === null || _a === void 0 ? void 0 : _a.currentNodeId); })) || ((_b = liveSession.value) === null || _b === void 0 ? void 0 : _b.nodeStates.find(function (node) { return node.status === 'unlocked'; })); });
var unlockedNodeCount = (0, vue_1.computed)(function () { var _a; return ((_a = liveSession.value) === null || _a === void 0 ? void 0 : _a.nodeStates.filter(function (node) { return node.status === 'unlocked'; }).length) || 0; });
var classroomProgress = (0, vue_1.computed)(function () {
    var _a;
    var total = ((_a = liveSession.value) === null || _a === void 0 ? void 0 : _a.nodeStates.length) || 0;
    return total ? Math.round((unlockedNodeCount.value / total) * 100) : 0;
});
var classroomActionLabel = (0, vue_1.computed)(function () {
    var _a, _b;
    if (((_a = liveSession.value) === null || _a === void 0 ? void 0 : _a.status) === 'not_started')
        return '开始课堂';
    if (((_b = liveSession.value) === null || _b === void 0 ? void 0 : _b.status) === 'paused')
        return '继续课堂';
    return '进入课堂';
});
var preparationStages = [
    { label: '上传', icon: lucide_vue_next_1.FileUp },
    { label: '确认', icon: lucide_vue_next_1.CheckCircle2 },
    { label: '设置', icon: lucide_vue_next_1.Settings2 },
    { label: '发布', icon: lucide_vue_next_1.Send },
];
var packageTodo = (0, vue_1.computed)(function () {
    var item = firstReadyPackage.value;
    if (!item)
        return undefined;
    if (item.status === 'generated')
        return { id: 'packages', count: readyPackages.value, label: '个互动包待继续', action: '确认互动方案', to: "/packages/".concat(item.id, "/proposal"), icon: lucide_vue_next_1.FileMusic, testId: 'continue-package-item' };
    if (item.status === 'modified')
        return { id: 'packages', count: readyPackages.value, label: '个互动包待发布', action: '发布课堂', to: "/packages/".concat(item.id, "/publish"), icon: lucide_vue_next_1.FileMusic, testId: 'continue-package-item' };
    return { id: 'packages', count: readyPackages.value, label: '个互动包待继续', action: item.status === 'draft' ? '继续编辑互动包' : '编辑互动包', to: "/packages/".concat(item.id, "/edit"), icon: lucide_vue_next_1.FileMusic, testId: 'continue-package-item' };
});
var continueItems = (0, vue_1.computed)(function () { return [
    pendingPlans.value > 0 ? { id: 'plans', count: pendingPlans.value, label: '份教案待确认', action: '确认解析内容', to: '/lesson-plans/history', icon: lucide_vue_next_1.ClipboardCheck, testId: 'continue-plan-item' } : undefined,
    packageTodo.value,
    upcomingCount.value > 0 ? { id: 'classrooms', count: upcomingCount.value, label: '节课堂待开始', action: '查看课堂', to: '/classrooms', icon: lucide_vue_next_1.CalendarClock, testId: 'continue-classroom-item' } : undefined,
].filter(Boolean); });
function packageDestination(item) {
    if (item.status === 'generated')
        return "/packages/".concat(item.id, "/proposal");
    if (item.status === 'modified')
        return "/packages/".concat(item.id, "/publish");
    if (['draft', 'confirmed'].includes(item.status))
        return "/packages/".concat(item.id, "/edit");
    return "/packages/".concat(item.id);
}
function packageNextAction(item) {
    if (item.status === 'generated')
        return '确认方案';
    if (item.status === 'modified')
        return '发布课堂';
    if (['draft', 'confirmed'].includes(item.status))
        return '继续编辑';
    return '查看详情';
}
function packageLessonPlanLabel(item) {
    var _a, _b, _c;
    var sourcePlanName = (_c = (_b = (_a = item.description) === null || _a === void 0 ? void 0 : _a.match(/《([^》]+)》/)) === null || _b === void 0 ? void 0 : _b[1]) === null || _c === void 0 ? void 0 : _c.trim();
    if (sourcePlanName)
        return "\u300A".concat(sourcePlanName, "\u300B\u6559\u6848");
    var packageName = item.title.replace(/互动包$/, '').trim();
    return packageName ? "".concat(packageName, "\u6559\u6848") : '音乐教案';
}
function listDashboardClasses() {
    return __awaiter(this, void 0, void 0, function () {
        var classList, visibleClasses, studentResults;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0: return [4 /*yield*/, classApi_1.classApi.listClasses()];
                case 1:
                    classList = _a.sent();
                    visibleClasses = classList.slice(0, 2);
                    return [4 /*yield*/, Promise.allSettled(visibleClasses.map(function (item) { return classApi_1.classApi.listStudents(item.id); }))];
                case 2:
                    studentResults = _a.sent();
                    return [2 /*return*/, classList.map(function (item, index) {
                            var studentResult = studentResults[index];
                            return (studentResult === null || studentResult === void 0 ? void 0 : studentResult.status) === 'fulfilled'
                                ? __assign(__assign({}, item), { studentCount: studentResult.value.length }) : item;
                        })];
            }
        });
    });
}
function loadDashboard() {
    return __awaiter(this, void 0, void 0, function () {
        var results;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    loading.value = true;
                    loadError.value = '';
                    return [4 /*yield*/, Promise.allSettled([classroomApi_1.classroomApi.listActiveSessions(), lessonPlanApi_1.lessonPlanApi.listMine(), packageApi_1.packageApi.listPackages(), listDashboardClasses()])];
                case 1:
                    results = _a.sent();
                    if (results[0].status === 'fulfilled')
                        sessions.value = results[0].value;
                    if (results[1].status === 'fulfilled')
                        plans.value = results[1].value;
                    if (results[2].status === 'fulfilled')
                        packages.value = results[2].value;
                    if (results[3].status === 'fulfilled')
                        classes.value = results[3].value;
                    if (results.some(function (result) { return result.status === 'rejected'; }))
                        loadError.value = '部分教学数据暂时无法加载，请重试。';
                    loading.value = false;
                    return [2 /*return*/];
            }
        });
    });
}
(0, vue_1.onMounted)(function () {
    if (!auth.user)
        auth.fetchMe().catch(function () { return undefined; });
    loadDashboard();
});
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
__VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)(__assign({ class: "dashboard-hero" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "dashboard-hero-copy" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.h1, __VLS_intrinsicElements.h1)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
(__VLS_ctx.teacherName);
__VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "hero-preparation-flow" }, { 'aria-label': "备课顺序" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.ol, __VLS_intrinsicElements.ol)({});
for (var _i = 0, _c = __VLS_getVForSourceType((__VLS_ctx.preparationStages)); _i < _c.length; _i++) {
    var _d = _c[_i], stage = _d[0], index = _d[1];
    __VLS_asFunctionalElement(__VLS_intrinsicElements.li, __VLS_intrinsicElements.li)({
        key: (stage.label),
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.i, __VLS_intrinsicElements.i)(__assign({ class: ("hero-flow-".concat(index)) }));
    var __VLS_4 = ((stage.icon));
    // @ts-ignore
    var __VLS_5 = __VLS_asFunctionalComponent(__VLS_4, new __VLS_4({
        size: (15),
        'aria-hidden': "true",
    }));
    var __VLS_6 = __VLS_5.apply(void 0, __spreadArray([{
            size: (15),
            'aria-hidden': "true",
        }], __VLS_functionalComponentArgsRest(__VLS_5), false));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
    (stage.label);
    if (index < __VLS_ctx.preparationStages.length - 1) {
        var __VLS_8 = {}.ArrowRight;
        /** @type {[typeof __VLS_components.ArrowRight, ]} */ ;
        // @ts-ignore
        var __VLS_9 = __VLS_asFunctionalComponent(__VLS_8, new __VLS_8({
            size: (14),
            'aria-hidden': "true",
        }));
        var __VLS_10 = __VLS_9.apply(void 0, __spreadArray([{
                size: (14),
                'aria-hidden': "true",
            }], __VLS_functionalComponentArgsRest(__VLS_9), false));
    }
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "dashboard-primary-actions" }, { 'data-testid': "dashboard-primary-actions" }));
var __VLS_12 = {}.RouterLink;
/** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
// @ts-ignore
var __VLS_13 = __VLS_asFunctionalComponent(__VLS_12, new __VLS_12(__assign({ class: "button primary" }, { to: "/lesson-plans/upload" })));
var __VLS_14 = __VLS_13.apply(void 0, __spreadArray([__assign({ class: "button primary" }, { to: "/lesson-plans/upload" })], __VLS_functionalComponentArgsRest(__VLS_13), false));
__VLS_15.slots.default;
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)(__assign({ class: "hero-action-icon" }));
var __VLS_16 = {}.FileUp;
/** @type {[typeof __VLS_components.FileUp, ]} */ ;
// @ts-ignore
var __VLS_17 = __VLS_asFunctionalComponent(__VLS_16, new __VLS_16({
    size: (22),
    'aria-hidden': "true",
}));
var __VLS_18 = __VLS_17.apply(void 0, __spreadArray([{
        size: (22),
        'aria-hidden': "true",
    }], __VLS_functionalComponentArgsRest(__VLS_17), false));
var __VLS_15;
var __VLS_20 = {}.RouterLink;
/** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
// @ts-ignore
var __VLS_21 = __VLS_asFunctionalComponent(__VLS_20, new __VLS_20(__assign({ class: "button teaching" }, { to: (__VLS_ctx.classroomEntryRoute) })));
var __VLS_22 = __VLS_21.apply(void 0, __spreadArray([__assign({ class: "button teaching" }, { to: (__VLS_ctx.classroomEntryRoute) })], __VLS_functionalComponentArgsRest(__VLS_21), false));
__VLS_23.slots.default;
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)(__assign({ class: "hero-action-icon" }));
var __VLS_24 = {}.PlayCircle;
/** @type {[typeof __VLS_components.PlayCircle, ]} */ ;
// @ts-ignore
var __VLS_25 = __VLS_asFunctionalComponent(__VLS_24, new __VLS_24({
    size: (24),
    'aria-hidden': "true",
}));
var __VLS_26 = __VLS_25.apply(void 0, __spreadArray([{
        size: (24),
        'aria-hidden': "true",
    }], __VLS_functionalComponentArgsRest(__VLS_25), false));
var __VLS_23;
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "dashboard-hero-scene" }, { 'data-testid': "dashboard-music-scene", 'aria-hidden': "true" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.img)({
    src: (__VLS_ctx.musicClassroomHero),
    alt: "",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)(__assign({ class: "dashboard-overview-grid" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.article, __VLS_intrinsicElements.article)(__assign({ class: "card dashboard-panel current-class-panel" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "dashboard-panel-heading" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)(__assign(__assign({ class: "panel-art-icon decoration-chalkboard" }, { style: ({ backgroundImage: "url(".concat(__VLS_ctx.musicDashboardDecorations, ")") }) }), { 'aria-hidden': "true" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
if (__VLS_ctx.liveSession) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "current-class-body" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "current-class-summary" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)(__assign(__assign({ class: "classroom-avatar" }, { style: ({ backgroundImage: "url(".concat(__VLS_ctx.musicWorkspaceStickers, ")") }) }), { 'aria-hidden': "true" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
    (__VLS_ctx.liveSession.courseTitle || '音乐互动课堂');
    __VLS_asFunctionalElement(__VLS_intrinsicElements.small, __VLS_intrinsicElements.small)({});
    (__VLS_ctx.formatDateTime(__VLS_ctx.liveSession.scheduledStartAt || __VLS_ctx.liveSession.startedAt));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)(__assign({ class: "status-pill" }, { class: (__VLS_ctx.liveSession.status) }));
    (__VLS_ctx.statusText(__VLS_ctx.liveSession.status));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "current-class-progress" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "current-class-metric" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.small, __VLS_intrinsicElements.small)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
    (((_a = __VLS_ctx.currentClassNode) === null || _a === void 0 ? void 0 : _a.title) || (__VLS_ctx.liveSession.status === 'not_started' ? '等待开始' : '课堂进行中'));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "current-class-metric progress-metric" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.small, __VLS_intrinsicElements.small)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
    (__VLS_ctx.unlockedNodeCount);
    (__VLS_ctx.liveSession.nodeStates.length);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)(__assign({ class: "class-progress-track" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.i, __VLS_intrinsicElements.i)(__assign({ style: ({ width: "".concat(__VLS_ctx.classroomProgress, "%") }) }));
    var __VLS_28 = {}.RouterLink;
    /** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
    // @ts-ignore
    var __VLS_29 = __VLS_asFunctionalComponent(__VLS_28, new __VLS_28(__assign({ class: "button primary current-class-action" }, { to: (__VLS_ctx.classroomEntryRoute) })));
    var __VLS_30 = __VLS_29.apply(void 0, __spreadArray([__assign({ class: "button primary current-class-action" }, { to: (__VLS_ctx.classroomEntryRoute) })], __VLS_functionalComponentArgsRest(__VLS_29), false));
    __VLS_31.slots.default;
    var __VLS_32 = {}.PlayCircle;
    /** @type {[typeof __VLS_components.PlayCircle, ]} */ ;
    // @ts-ignore
    var __VLS_33 = __VLS_asFunctionalComponent(__VLS_32, new __VLS_32({
        size: (17),
        'aria-hidden': "true",
    }));
    var __VLS_34 = __VLS_33.apply(void 0, __spreadArray([{
            size: (17),
            'aria-hidden': "true",
        }], __VLS_functionalComponentArgsRest(__VLS_33), false));
    (__VLS_ctx.classroomActionLabel);
    var __VLS_31;
}
else {
    var __VLS_36 = {}.RouterLink;
    /** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
    // @ts-ignore
    var __VLS_37 = __VLS_asFunctionalComponent(__VLS_36, new __VLS_36(__assign({ class: "current-class-summary empty" }, { to: "/classrooms" })));
    var __VLS_38 = __VLS_37.apply(void 0, __spreadArray([__assign({ class: "current-class-summary empty" }, { to: "/classrooms" })], __VLS_functionalComponentArgsRest(__VLS_37), false));
    __VLS_39.slots.default;
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)(__assign(__assign({ class: "classroom-avatar" }, { style: ({ backgroundImage: "url(".concat(__VLS_ctx.musicWorkspaceStickers, ")") }) }), { 'aria-hidden': "true" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.small, __VLS_intrinsicElements.small)({});
    var __VLS_40 = {}.ArrowRight;
    /** @type {[typeof __VLS_components.ArrowRight, ]} */ ;
    // @ts-ignore
    var __VLS_41 = __VLS_asFunctionalComponent(__VLS_40, new __VLS_40({
        size: (17),
        'aria-hidden': "true",
    }));
    var __VLS_42 = __VLS_41.apply(void 0, __spreadArray([{
            size: (17),
            'aria-hidden': "true",
        }], __VLS_functionalComponentArgsRest(__VLS_41), false));
    var __VLS_39;
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.article, __VLS_intrinsicElements.article)(__assign({ class: "card dashboard-panel continue-panel" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "dashboard-panel-heading" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)(__assign(__assign({ class: "panel-art-icon decoration-cards" }, { style: ({ backgroundImage: "url(".concat(__VLS_ctx.musicDashboardDecorations, ")") }) }), { 'aria-hidden': "true" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
if (__VLS_ctx.continueItems.length) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
    (__VLS_ctx.continueItems.length);
}
if (__VLS_ctx.loadError) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "dashboard-load-error" }, { 'data-testid': "dashboard-load-error" }));
    var __VLS_44 = {}.CircleAlert;
    /** @type {[typeof __VLS_components.CircleAlert, ]} */ ;
    // @ts-ignore
    var __VLS_45 = __VLS_asFunctionalComponent(__VLS_44, new __VLS_44({
        size: (20),
        'aria-hidden': "true",
    }));
    var __VLS_46 = __VLS_45.apply(void 0, __spreadArray([{
            size: (20),
            'aria-hidden': "true",
        }], __VLS_functionalComponentArgsRest(__VLS_45), false));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
    (__VLS_ctx.loadError);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign(__assign({ onClick: (__VLS_ctx.loadDashboard) }, { class: "button ghost" }), { type: "button", 'data-testid': "dashboard-retry", disabled: (__VLS_ctx.loading) }));
    var __VLS_48 = {}.RefreshCw;
    /** @type {[typeof __VLS_components.RefreshCw, ]} */ ;
    // @ts-ignore
    var __VLS_49 = __VLS_asFunctionalComponent(__VLS_48, new __VLS_48({
        size: (16),
        'aria-hidden': "true",
    }));
    var __VLS_50 = __VLS_49.apply(void 0, __spreadArray([{
            size: (16),
            'aria-hidden': "true",
        }], __VLS_functionalComponentArgsRest(__VLS_49), false));
}
else if (__VLS_ctx.visibleContinueItems.length) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "continue-list" }));
    for (var _e = 0, _f = __VLS_getVForSourceType((__VLS_ctx.visibleContinueItems)); _e < _f.length; _e++) {
        var item = _f[_e][0];
        var __VLS_52 = {}.RouterLink;
        /** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
        // @ts-ignore
        var __VLS_53 = __VLS_asFunctionalComponent(__VLS_52, new __VLS_52({
            key: (item.id),
            to: (item.to),
            dataTestid: (item.testId),
        }));
        var __VLS_54 = __VLS_53.apply(void 0, __spreadArray([{
                key: (item.id),
                to: (item.to),
                dataTestid: (item.testId),
            }], __VLS_functionalComponentArgsRest(__VLS_53), false));
        __VLS_55.slots.default;
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)(__assign({ class: "continue-icon" }));
        var __VLS_56 = ((item.icon));
        // @ts-ignore
        var __VLS_57 = __VLS_asFunctionalComponent(__VLS_56, new __VLS_56({
            size: (18),
            'aria-hidden': "true",
        }));
        var __VLS_58 = __VLS_57.apply(void 0, __spreadArray([{
                size: (18),
                'aria-hidden': "true",
            }], __VLS_functionalComponentArgsRest(__VLS_57), false));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
        __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
        (item.count);
        (item.label);
        __VLS_asFunctionalElement(__VLS_intrinsicElements.small, __VLS_intrinsicElements.small)({});
        (item.action);
        var __VLS_60 = {}.ArrowRight;
        /** @type {[typeof __VLS_components.ArrowRight, ]} */ ;
        // @ts-ignore
        var __VLS_61 = __VLS_asFunctionalComponent(__VLS_60, new __VLS_60({
            size: (18),
            'aria-hidden': "true",
        }));
        var __VLS_62 = __VLS_61.apply(void 0, __spreadArray([{
                size: (18),
                'aria-hidden': "true",
            }], __VLS_functionalComponentArgsRest(__VLS_61), false));
        var __VLS_55;
    }
}
else {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "continue-empty" }, { 'data-testid': "continue-empty" }));
    var __VLS_64 = {}.ClipboardCheck;
    /** @type {[typeof __VLS_components.ClipboardCheck, ]} */ ;
    // @ts-ignore
    var __VLS_65 = __VLS_asFunctionalComponent(__VLS_64, new __VLS_64({
        size: (20),
        'aria-hidden': "true",
    }));
    var __VLS_66 = __VLS_65.apply(void 0, __spreadArray([{
            size: (20),
            'aria-hidden': "true",
        }], __VLS_functionalComponentArgsRest(__VLS_65), false));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
    (__VLS_ctx.loading ? '正在同步待办…' : '暂时没有待处理事项');
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)(__assign({ class: "dashboard-bottom-grid" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)(__assign({ class: "recent-section card" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "section-header" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "dashboard-panel-heading" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)(__assign(__assign({ class: "panel-art-icon decoration-tambourine" }, { style: ({ backgroundImage: "url(".concat(__VLS_ctx.musicDashboardDecorations, ")") }) }), { 'aria-hidden': "true" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
if (__VLS_ctx.packages.length) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)(__assign({ class: "recent-package-count" }));
    (__VLS_ctx.packages.length);
}
var __VLS_68 = {}.RouterLink;
/** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
// @ts-ignore
var __VLS_69 = __VLS_asFunctionalComponent(__VLS_68, new __VLS_68(__assign({ class: "text-link" }, { to: "/lesson-plans/history" })));
var __VLS_70 = __VLS_69.apply(void 0, __spreadArray([__assign({ class: "text-link" }, { to: "/lesson-plans/history" })], __VLS_functionalComponentArgsRest(__VLS_69), false));
__VLS_71.slots.default;
var __VLS_72 = {}.ArrowRight;
/** @type {[typeof __VLS_components.ArrowRight, ]} */ ;
// @ts-ignore
var __VLS_73 = __VLS_asFunctionalComponent(__VLS_72, new __VLS_72({
    size: (16),
    'aria-hidden': "true",
}));
var __VLS_74 = __VLS_73.apply(void 0, __spreadArray([{
        size: (16),
        'aria-hidden': "true",
    }], __VLS_functionalComponentArgsRest(__VLS_73), false));
var __VLS_71;
if (__VLS_ctx.recentPackages.length) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "package-list" }));
    for (var _g = 0, _h = __VLS_getVForSourceType((__VLS_ctx.recentPackages)); _g < _h.length; _g++) {
        var _j = _h[_g], item = _j[0], index = _j[1];
        __VLS_asFunctionalElement(__VLS_intrinsicElements.article, __VLS_intrinsicElements.article)(__assign({ key: (item.id) }, { class: "package-list-item" }));
        var __VLS_76 = {}.RouterLink;
        /** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
        // @ts-ignore
        var __VLS_77 = __VLS_asFunctionalComponent(__VLS_76, new __VLS_76(__assign({ class: "package-card-content" }, { to: ("/packages/".concat(item.id)) })));
        var __VLS_78 = __VLS_77.apply(void 0, __spreadArray([__assign({ class: "package-card-content" }, { to: ("/packages/".concat(item.id)) })], __VLS_functionalComponentArgsRest(__VLS_77), false));
        __VLS_79.slots.default;
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)(__assign(__assign(__assign({ class: "package-art" }, { class: ("package-art-".concat(index % 4)) }), { style: ({ backgroundImage: "url(".concat(__VLS_ctx.musicWorkspaceStickers, ")") }) }), { 'aria-hidden': "true" }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)(__assign({ class: "package-card-copy" }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
        (item.title);
        __VLS_asFunctionalElement(__VLS_intrinsicElements.small, __VLS_intrinsicElements.small)({});
        (__VLS_ctx.packageLessonPlanLabel(item));
        var __VLS_79;
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "package-card-footer" }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)(__assign({ class: "status-pill" }));
        (__VLS_ctx.statusText(item.status));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)(__assign({ class: "package-card-actions" }));
        var __VLS_80 = {}.RouterLink;
        /** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
        // @ts-ignore
        var __VLS_81 = __VLS_asFunctionalComponent(__VLS_80, new __VLS_80(__assign({ class: "package-detail-action" }, { to: ("/packages/".concat(item.id)) })));
        var __VLS_82 = __VLS_81.apply(void 0, __spreadArray([__assign({ class: "package-detail-action" }, { to: ("/packages/".concat(item.id)) })], __VLS_functionalComponentArgsRest(__VLS_81), false));
        __VLS_83.slots.default;
        var __VLS_83;
        var __VLS_84 = {}.RouterLink;
        /** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
        // @ts-ignore
        var __VLS_85 = __VLS_asFunctionalComponent(__VLS_84, new __VLS_84(__assign({ class: "package-next-action" }, { to: (__VLS_ctx.packageDestination(item)) })));
        var __VLS_86 = __VLS_85.apply(void 0, __spreadArray([__assign({ class: "package-next-action" }, { to: (__VLS_ctx.packageDestination(item)) })], __VLS_functionalComponentArgsRest(__VLS_85), false));
        __VLS_87.slots.default;
        (__VLS_ctx.packageNextAction(item));
        var __VLS_88 = {}.ArrowRight;
        /** @type {[typeof __VLS_components.ArrowRight, ]} */ ;
        // @ts-ignore
        var __VLS_89 = __VLS_asFunctionalComponent(__VLS_88, new __VLS_88({
            size: (15),
            'aria-hidden': "true",
        }));
        var __VLS_90 = __VLS_89.apply(void 0, __spreadArray([{
                size: (15),
                'aria-hidden': "true",
            }], __VLS_functionalComponentArgsRest(__VLS_89), false));
        var __VLS_87;
    }
}
else {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "empty-inline" }));
    (__VLS_ctx.loadError ? '暂时无法同步互动包，请重试。' : __VLS_ctx.loading ? '正在同步教学内容…' : '还没有互动包，上传教案后即可开始生成。');
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)(__assign({ class: "class-management-panel card" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "section-header" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "dashboard-panel-heading" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)(__assign({ class: "class-panel-icon" }));
var __VLS_92 = {}.UsersRound;
/** @type {[typeof __VLS_components.UsersRound, ]} */ ;
// @ts-ignore
var __VLS_93 = __VLS_asFunctionalComponent(__VLS_92, new __VLS_92({
    size: (18),
    'aria-hidden': "true",
}));
var __VLS_94 = __VLS_93.apply(void 0, __spreadArray([{
        size: (18),
        'aria-hidden': "true",
    }], __VLS_functionalComponentArgsRest(__VLS_93), false));
__VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
if (__VLS_ctx.classes.length) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)(__assign({ class: "recent-package-count" }));
    (__VLS_ctx.classes.length);
}
var __VLS_96 = {}.RouterLink;
/** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
// @ts-ignore
var __VLS_97 = __VLS_asFunctionalComponent(__VLS_96, new __VLS_96(__assign({ class: "text-link" }, { to: "/classes" })));
var __VLS_98 = __VLS_97.apply(void 0, __spreadArray([__assign({ class: "text-link" }, { to: "/classes" })], __VLS_functionalComponentArgsRest(__VLS_97), false));
__VLS_99.slots.default;
var __VLS_100 = {}.ArrowRight;
/** @type {[typeof __VLS_components.ArrowRight, ]} */ ;
// @ts-ignore
var __VLS_101 = __VLS_asFunctionalComponent(__VLS_100, new __VLS_100({
    size: (16),
    'aria-hidden': "true",
}));
var __VLS_102 = __VLS_101.apply(void 0, __spreadArray([{
        size: (16),
        'aria-hidden': "true",
    }], __VLS_functionalComponentArgsRest(__VLS_101), false));
var __VLS_99;
if (__VLS_ctx.recentClasses.length) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "dashboard-class-list" }));
    for (var _k = 0, _l = __VLS_getVForSourceType((__VLS_ctx.recentClasses)); _k < _l.length; _k++) {
        var item = _l[_k][0];
        var __VLS_104 = {}.RouterLink;
        /** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
        // @ts-ignore
        var __VLS_105 = __VLS_asFunctionalComponent(__VLS_104, new __VLS_104({
            key: (item.id),
            to: ("/classes/".concat(item.id)),
        }));
        var __VLS_106 = __VLS_105.apply(void 0, __spreadArray([{
                key: (item.id),
                to: ("/classes/".concat(item.id)),
            }], __VLS_functionalComponentArgsRest(__VLS_105), false));
        __VLS_107.slots.default;
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)(__assign({ class: "dashboard-class-icon" }));
        var __VLS_108 = {}.UsersRound;
        /** @type {[typeof __VLS_components.UsersRound, ]} */ ;
        // @ts-ignore
        var __VLS_109 = __VLS_asFunctionalComponent(__VLS_108, new __VLS_108({
            size: (19),
            'aria-hidden': "true",
        }));
        var __VLS_110 = __VLS_109.apply(void 0, __spreadArray([{
                size: (19),
                'aria-hidden': "true",
            }], __VLS_functionalComponentArgsRest(__VLS_109), false));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
        __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
        (item.className);
        __VLS_asFunctionalElement(__VLS_intrinsicElements.small, __VLS_intrinsicElements.small)({});
        (item.description || '音乐课堂班级');
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)(__assign({ class: "dashboard-student-count" }, { 'data-testid': "dashboard-class-student-count" }));
        ((_b = item.studentCount) !== null && _b !== void 0 ? _b : 0);
        var __VLS_112 = {}.ArrowRight;
        /** @type {[typeof __VLS_components.ArrowRight, ]} */ ;
        // @ts-ignore
        var __VLS_113 = __VLS_asFunctionalComponent(__VLS_112, new __VLS_112({
            size: (17),
            'aria-hidden': "true",
        }));
        var __VLS_114 = __VLS_113.apply(void 0, __spreadArray([{
                size: (17),
                'aria-hidden': "true",
            }], __VLS_functionalComponentArgsRest(__VLS_113), false));
        var __VLS_107;
    }
}
else {
    var __VLS_116 = {}.RouterLink;
    /** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
    // @ts-ignore
    var __VLS_117 = __VLS_asFunctionalComponent(__VLS_116, new __VLS_116(__assign({ class: "class-management-empty" }, { to: "/classes" })));
    var __VLS_118 = __VLS_117.apply(void 0, __spreadArray([__assign({ class: "class-management-empty" }, { to: "/classes" })], __VLS_functionalComponentArgsRest(__VLS_117), false));
    __VLS_119.slots.default;
    var __VLS_120 = {}.UsersRound;
    /** @type {[typeof __VLS_components.UsersRound, ]} */ ;
    // @ts-ignore
    var __VLS_121 = __VLS_asFunctionalComponent(__VLS_120, new __VLS_120({
        size: (21),
        'aria-hidden': "true",
    }));
    var __VLS_122 = __VLS_121.apply(void 0, __spreadArray([{
            size: (21),
            'aria-hidden': "true",
        }], __VLS_functionalComponentArgsRest(__VLS_121), false));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
    (__VLS_ctx.loading ? '正在同步班级…' : '还没有班级，前往创建');
    var __VLS_124 = {}.ArrowRight;
    /** @type {[typeof __VLS_components.ArrowRight, ]} */ ;
    // @ts-ignore
    var __VLS_125 = __VLS_asFunctionalComponent(__VLS_124, new __VLS_124({
        size: (17),
        'aria-hidden': "true",
    }));
    var __VLS_126 = __VLS_125.apply(void 0, __spreadArray([{
            size: (17),
            'aria-hidden': "true",
        }], __VLS_functionalComponentArgsRest(__VLS_125), false));
    var __VLS_119;
}
var __VLS_2;
/** @type {__VLS_StyleScopedClasses['dashboard-hero']} */ ;
/** @type {__VLS_StyleScopedClasses['dashboard-hero-copy']} */ ;
/** @type {__VLS_StyleScopedClasses['hero-preparation-flow']} */ ;
/** @type {__VLS_StyleScopedClasses['dashboard-primary-actions']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['primary']} */ ;
/** @type {__VLS_StyleScopedClasses['hero-action-icon']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['teaching']} */ ;
/** @type {__VLS_StyleScopedClasses['hero-action-icon']} */ ;
/** @type {__VLS_StyleScopedClasses['dashboard-hero-scene']} */ ;
/** @type {__VLS_StyleScopedClasses['dashboard-overview-grid']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['dashboard-panel']} */ ;
/** @type {__VLS_StyleScopedClasses['current-class-panel']} */ ;
/** @type {__VLS_StyleScopedClasses['dashboard-panel-heading']} */ ;
/** @type {__VLS_StyleScopedClasses['panel-art-icon']} */ ;
/** @type {__VLS_StyleScopedClasses['decoration-chalkboard']} */ ;
/** @type {__VLS_StyleScopedClasses['current-class-body']} */ ;
/** @type {__VLS_StyleScopedClasses['current-class-summary']} */ ;
/** @type {__VLS_StyleScopedClasses['classroom-avatar']} */ ;
/** @type {__VLS_StyleScopedClasses['status-pill']} */ ;
/** @type {__VLS_StyleScopedClasses['current-class-progress']} */ ;
/** @type {__VLS_StyleScopedClasses['current-class-metric']} */ ;
/** @type {__VLS_StyleScopedClasses['current-class-metric']} */ ;
/** @type {__VLS_StyleScopedClasses['progress-metric']} */ ;
/** @type {__VLS_StyleScopedClasses['class-progress-track']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['primary']} */ ;
/** @type {__VLS_StyleScopedClasses['current-class-action']} */ ;
/** @type {__VLS_StyleScopedClasses['current-class-summary']} */ ;
/** @type {__VLS_StyleScopedClasses['empty']} */ ;
/** @type {__VLS_StyleScopedClasses['classroom-avatar']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['dashboard-panel']} */ ;
/** @type {__VLS_StyleScopedClasses['continue-panel']} */ ;
/** @type {__VLS_StyleScopedClasses['dashboard-panel-heading']} */ ;
/** @type {__VLS_StyleScopedClasses['panel-art-icon']} */ ;
/** @type {__VLS_StyleScopedClasses['decoration-cards']} */ ;
/** @type {__VLS_StyleScopedClasses['dashboard-load-error']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['ghost']} */ ;
/** @type {__VLS_StyleScopedClasses['continue-list']} */ ;
/** @type {__VLS_StyleScopedClasses['continue-icon']} */ ;
/** @type {__VLS_StyleScopedClasses['continue-empty']} */ ;
/** @type {__VLS_StyleScopedClasses['dashboard-bottom-grid']} */ ;
/** @type {__VLS_StyleScopedClasses['recent-section']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['section-header']} */ ;
/** @type {__VLS_StyleScopedClasses['dashboard-panel-heading']} */ ;
/** @type {__VLS_StyleScopedClasses['panel-art-icon']} */ ;
/** @type {__VLS_StyleScopedClasses['decoration-tambourine']} */ ;
/** @type {__VLS_StyleScopedClasses['recent-package-count']} */ ;
/** @type {__VLS_StyleScopedClasses['text-link']} */ ;
/** @type {__VLS_StyleScopedClasses['package-list']} */ ;
/** @type {__VLS_StyleScopedClasses['package-list-item']} */ ;
/** @type {__VLS_StyleScopedClasses['package-card-content']} */ ;
/** @type {__VLS_StyleScopedClasses['package-art']} */ ;
/** @type {__VLS_StyleScopedClasses['package-card-copy']} */ ;
/** @type {__VLS_StyleScopedClasses['package-card-footer']} */ ;
/** @type {__VLS_StyleScopedClasses['status-pill']} */ ;
/** @type {__VLS_StyleScopedClasses['package-card-actions']} */ ;
/** @type {__VLS_StyleScopedClasses['package-detail-action']} */ ;
/** @type {__VLS_StyleScopedClasses['package-next-action']} */ ;
/** @type {__VLS_StyleScopedClasses['empty-inline']} */ ;
/** @type {__VLS_StyleScopedClasses['class-management-panel']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['section-header']} */ ;
/** @type {__VLS_StyleScopedClasses['dashboard-panel-heading']} */ ;
/** @type {__VLS_StyleScopedClasses['class-panel-icon']} */ ;
/** @type {__VLS_StyleScopedClasses['recent-package-count']} */ ;
/** @type {__VLS_StyleScopedClasses['text-link']} */ ;
/** @type {__VLS_StyleScopedClasses['dashboard-class-list']} */ ;
/** @type {__VLS_StyleScopedClasses['dashboard-class-icon']} */ ;
/** @type {__VLS_StyleScopedClasses['dashboard-student-count']} */ ;
/** @type {__VLS_StyleScopedClasses['class-management-empty']} */ ;
var __VLS_dollars;
var __VLS_self = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () {
        return {
            ArrowRight: lucide_vue_next_1.ArrowRight,
            CircleAlert: lucide_vue_next_1.CircleAlert,
            ClipboardCheck: lucide_vue_next_1.ClipboardCheck,
            FileUp: lucide_vue_next_1.FileUp,
            PlayCircle: lucide_vue_next_1.PlayCircle,
            RefreshCw: lucide_vue_next_1.RefreshCw,
            UsersRound: lucide_vue_next_1.UsersRound,
            AppShell: AppShell_vue_1.default,
            formatDateTime: display_1.formatDateTime,
            statusText: display_1.statusText,
            musicClassroomHero: music_children_orff_banner_png_1.default,
            musicDashboardDecorations: music_dashboard_decorations_png_1.default,
            musicWorkspaceStickers: music_workspace_stickers_png_1.default,
            classes: classes,
            packages: packages,
            loading: loading,
            loadError: loadError,
            teacherName: teacherName,
            liveSession: liveSession,
            recentPackages: recentPackages,
            recentClasses: recentClasses,
            visibleContinueItems: visibleContinueItems,
            classroomEntryRoute: classroomEntryRoute,
            currentClassNode: currentClassNode,
            unlockedNodeCount: unlockedNodeCount,
            classroomProgress: classroomProgress,
            classroomActionLabel: classroomActionLabel,
            preparationStages: preparationStages,
            continueItems: continueItems,
            packageDestination: packageDestination,
            packageNextAction: packageNextAction,
            packageLessonPlanLabel: packageLessonPlanLabel,
            loadDashboard: loadDashboard,
        };
    },
});
exports.default = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () {
        return {};
    },
});
; /* PartiallyEnd: #4569/main.vue */
