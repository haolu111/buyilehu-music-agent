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
var _a, _b, _c, _d, _e;
Object.defineProperty(exports, "__esModule", { value: true });
/* placeholder */
var vue_1 = require("vue");
var vue_router_1 = require("vue-router");
var AppShell_vue_1 = require("../components/AppShell.vue");
var SubmissionResult_vue_1 = require("../components/SubmissionResult.vue");
var classroomApi_1 = require("../api/classroomApi");
var classApi_1 = require("../api/classApi");
var route = (0, vue_router_1.useRoute)();
var sessionId = Number(route.params.sessionId);
var session = (0, vue_1.ref)(null);
var submissions = (0, vue_1.ref)([]);
var classStudents = (0, vue_1.ref)([]);
var loading = (0, vue_1.ref)(false);
var error = (0, vue_1.ref)('');
var students = (0, vue_1.computed)(function () {
    var map = new Map();
    for (var _i = 0, _a = classStudents.value; _i < _a.length; _i++) {
        var student = _a[_i];
        var id = Number(student.studentId || student.id);
        map.set(id, student.realName || student.displayName || student.username || "\u5B66\u751F #".concat(id));
    }
    for (var _b = 0, _c = submissions.value; _b < _c.length; _b++) {
        var item = _c[_b];
        if (!map.has(item.studentId)) {
            map.set(item.studentId, item.studentName || "\u5B66\u751F #".concat(item.studentId));
        }
    }
    return Array.from(map.entries())
        .map(function (_a) {
        var id = _a[0], name = _a[1];
        return ({ id: id, name: name });
    })
        .sort(function (left, right) { return left.name.localeCompare(right.name); });
});
var nodes = (0, vue_1.computed)(function () { var _a; return ((_a = session.value) === null || _a === void 0 ? void 0 : _a.nodeStates) || []; });
var totalTaskCount = (0, vue_1.computed)(function () { return students.value.length * nodes.value.length; });
var completedSubmissions = (0, vue_1.computed)(function () {
    var keys = new Set();
    for (var _i = 0, _a = submissions.value; _i < _a.length; _i++) {
        var item = _a[_i];
        if (item.progressStatus === 'completed') {
            keys.add("".concat(item.studentId, "-").concat(item.nodeId));
        }
    }
    return keys.size;
});
var completionRate = (0, vue_1.computed)(function () {
    if (!totalTaskCount.value)
        return 0;
    return Math.round((completedSubmissions.value / totalTaskCount.value) * 100);
});
var averageScore = (0, vue_1.computed)(function () {
    var scored = submissions.value.filter(function (item) { return item.score != null; });
    if (!scored.length)
        return 0;
    var total = scored.reduce(function (sum, item) { return sum + Number(item.score || 0); }, 0);
    return Math.round(total / scored.length);
});
var pieStyle = (0, vue_1.computed)(function () { return ({
    background: "conic-gradient(#2a9d8f 0 ".concat(completionRate.value, "%, #e5e7eb ").concat(completionRate.value, "% 100%)"),
}); });
var nodeBars = (0, vue_1.computed)(function () { return nodes.value.map(function (node) {
    var nodeId = node.activityNodeId || node.id;
    var completed = new Set(submissions.value
        .filter(function (item) { return item.nodeId === nodeId && item.progressStatus === 'completed'; })
        .map(function (item) { return item.studentId; })).size;
    var rate = students.value.length ? Math.round((completed / students.value.length) * 100) : 0;
    return {
        id: nodeId,
        title: node.title,
        sortOrder: node.sortOrder,
        completed: completed,
        rate: rate,
    };
}); });
var scoreBuckets = (0, vue_1.computed)(function () {
    var buckets = [
        { label: '0-59', min: 0, max: 59, count: 0 },
        { label: '60-79', min: 60, max: 79, count: 0 },
        { label: '80-89', min: 80, max: 89, count: 0 },
        { label: '90-100', min: 90, max: 100, count: 0 },
    ];
    var _loop_1 = function (item) {
        if (item.score == null)
            return "continue";
        var score = Number(item.score);
        var bucket = buckets.find(function (part) { return score >= part.min && score <= part.max; });
        if (bucket)
            bucket.count += 1;
    };
    for (var _i = 0, _a = submissions.value; _i < _a.length; _i++) {
        var item = _a[_i];
        _loop_1(item);
    }
    var max = Math.max.apply(Math, __spreadArray([1], buckets.map(function (item) { return item.count; }), false));
    return buckets.map(function (item) { return (__assign(__assign({}, item), { rate: Math.round((item.count / max) * 100) })); });
});
var studentRows = (0, vue_1.computed)(function () { return students.value.map(function (student) {
    var studentSubmissions = submissions.value.filter(function (item) { return item.studentId === student.id; });
    var completedNodeIds = new Set(studentSubmissions
        .filter(function (item) { return item.progressStatus === 'completed'; })
        .map(function (item) { return item.nodeId; }));
    var scored = studentSubmissions.filter(function (item) { return item.score != null; });
    var score = scored.length
        ? Math.round(scored.reduce(function (sum, item) { return sum + Number(item.score || 0); }, 0) / scored.length)
        : null;
    return {
        id: student.id,
        name: student.name,
        completed: completedNodeIds.size,
        total: nodes.value.length,
        rate: nodes.value.length ? Math.round((completedNodeIds.size / nodes.value.length) * 100) : 0,
        score: score,
        submissions: studentSubmissions.sort(function (left, right) { return (left.sortOrder || 9999) - (right.sortOrder || 9999); }),
    };
}); });
function loadReport() {
    return __awaiter(this, void 0, void 0, function () {
        var sessionData, _a, submissionData, studentData, exception_1;
        return __generator(this, function (_b) {
            switch (_b.label) {
                case 0:
                    loading.value = true;
                    error.value = '';
                    _b.label = 1;
                case 1:
                    _b.trys.push([1, 4, 5, 6]);
                    return [4 /*yield*/, classroomApi_1.classroomApi.getSession(sessionId)];
                case 2:
                    sessionData = _b.sent();
                    return [4 /*yield*/, Promise.all([
                            classroomApi_1.classroomApi.listSubmissions(sessionId),
                            classApi_1.classApi.listStudents(sessionData.classId),
                        ])];
                case 3:
                    _a = _b.sent(), submissionData = _a[0], studentData = _a[1];
                    session.value = sessionData;
                    submissions.value = submissionData;
                    classStudents.value = studentData;
                    return [3 /*break*/, 6];
                case 4:
                    exception_1 = _b.sent();
                    error.value = exception_1 instanceof Error ? exception_1.message : '加载课程分析失败';
                    return [3 /*break*/, 6];
                case 5:
                    loading.value = false;
                    return [7 /*endfinally*/];
                case 6: return [2 /*return*/];
            }
        });
    });
}
function statusText(status) {
    var map = {
        not_started: '未开始',
        running: '进行中',
        paused: '已暂停',
        ended: '已结束',
        locked: '锁定',
        unlocked: '已解锁',
        completed: '已完成',
        doing: '进行中',
    };
    return status ? map[status] || status : '-';
}
(0, vue_1.onMounted)(loadReport);
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
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "section-header" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.h1, __VLS_intrinsicElements.h1)({});
(((_a = __VLS_ctx.session) === null || _a === void 0 ? void 0 : _a.courseTitle) || "\u8BFE\u5802\u5206\u6790 #".concat(__VLS_ctx.sessionId));
__VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "muted" }));
(((_b = __VLS_ctx.session) === null || _b === void 0 ? void 0 : _b.classId) || '-');
(__VLS_ctx.statusText((_c = __VLS_ctx.session) === null || _c === void 0 ? void 0 : _c.status));
__VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign(__assign({ onClick: (__VLS_ctx.loadReport) }, { class: "button" }), { type: "button" }));
if (__VLS_ctx.error) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "error" }));
    (__VLS_ctx.error);
}
if (__VLS_ctx.loading) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "muted" }));
}
if (__VLS_ctx.session && !__VLS_ctx.loading) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)(__assign({ class: "grid" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "stat" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
    (__VLS_ctx.students.length);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "stat" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
    (__VLS_ctx.completedSubmissions);
    (__VLS_ctx.totalTaskCount);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "stat" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
    (__VLS_ctx.completionRate);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "stat" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
    (__VLS_ctx.averageScore || '-');
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)(__assign({ class: "analysis-grid" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.article, __VLS_intrinsicElements.article)(__assign({ class: "card stack" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "pie-row" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "pie-chart" }, { style: (__VLS_ctx.pieStyle) }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
    (__VLS_ctx.completionRate);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "muted" }));
    (__VLS_ctx.completedSubmissions);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "muted" }));
    (Math.max(0, __VLS_ctx.totalTaskCount - __VLS_ctx.completedSubmissions));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.article, __VLS_intrinsicElements.article)(__assign({ class: "card stack" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "bar-list" }));
    for (var _i = 0, _f = __VLS_getVForSourceType((__VLS_ctx.scoreBuckets)); _i < _f.length; _i++) {
        var bucket = _f[_i][0];
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ key: (bucket.label) }, { class: "bar-row" }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
        (bucket.label);
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "bar-track" }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.i, __VLS_intrinsicElements.i)(__assign({ style: ({ width: "".concat(bucket.rate, "%") }) }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
        (bucket.count);
    }
    __VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)(__assign({ class: "card stack" }, { style: {} }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "bar-list" }));
    for (var _g = 0, _h = __VLS_getVForSourceType((__VLS_ctx.nodeBars)); _g < _h.length; _g++) {
        var node = _h[_g][0];
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ key: (node.id) }, { class: "bar-row wide-bar" }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
        (node.sortOrder);
        (node.title);
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "bar-track" }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.i, __VLS_intrinsicElements.i)(__assign({ style: ({ width: "".concat(node.rate, "%") }) }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
        (node.completed);
        (__VLS_ctx.students.length);
    }
    __VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)(__assign({ class: "card stack" }, { style: {} }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.table, __VLS_intrinsicElements.table)(__assign({ class: "data-table" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.thead, __VLS_intrinsicElements.thead)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.tr, __VLS_intrinsicElements.tr)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.th, __VLS_intrinsicElements.th)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.th, __VLS_intrinsicElements.th)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.th, __VLS_intrinsicElements.th)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.th, __VLS_intrinsicElements.th)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.tbody, __VLS_intrinsicElements.tbody)({});
    if (!__VLS_ctx.studentRows.length) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.tr, __VLS_intrinsicElements.tr)({});
        __VLS_asFunctionalElement(__VLS_intrinsicElements.td, __VLS_intrinsicElements.td)({
            colspan: "4",
        });
    }
    for (var _j = 0, _k = __VLS_getVForSourceType((__VLS_ctx.studentRows)); _j < _k.length; _j++) {
        var row = _k[_j][0];
        __VLS_asFunctionalElement(__VLS_intrinsicElements.tr, __VLS_intrinsicElements.tr)({
            key: (row.id),
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.td, __VLS_intrinsicElements.td)({});
        (row.name);
        __VLS_asFunctionalElement(__VLS_intrinsicElements.td, __VLS_intrinsicElements.td)({});
        (row.completed);
        (row.total);
        (row.rate);
        __VLS_asFunctionalElement(__VLS_intrinsicElements.td, __VLS_intrinsicElements.td)({});
        ((_d = row.score) !== null && _d !== void 0 ? _d : '-');
        __VLS_asFunctionalElement(__VLS_intrinsicElements.td, __VLS_intrinsicElements.td)({});
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "answer-list" }));
        for (var _l = 0, _m = __VLS_getVForSourceType((row.submissions)); _l < _m.length; _l++) {
            var item = _m[_l][0];
            __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ key: (item.progressId) }, { class: "answer-item" }));
            __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
            (item.nodeTitle || "\u73AF\u8282 #".concat(item.nodeId));
            __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
            (__VLS_ctx.statusText(item.progressStatus));
            ((_e = item.score) !== null && _e !== void 0 ? _e : '-');
            /** @type {[typeof SubmissionResult, ]} */ ;
            // @ts-ignore
            var __VLS_4 = __VLS_asFunctionalComponent(SubmissionResult_vue_1.default, new SubmissionResult_vue_1.default({
                value: (item.resultJson),
            }));
            var __VLS_5 = __VLS_4.apply(void 0, __spreadArray([{
                    value: (item.resultJson),
                }], __VLS_functionalComponentArgsRest(__VLS_4), false));
        }
    }
}
var __VLS_2;
/** @type {__VLS_StyleScopedClasses['section-header']} */ ;
/** @type {__VLS_StyleScopedClasses['muted']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['error']} */ ;
/** @type {__VLS_StyleScopedClasses['muted']} */ ;
/** @type {__VLS_StyleScopedClasses['grid']} */ ;
/** @type {__VLS_StyleScopedClasses['stat']} */ ;
/** @type {__VLS_StyleScopedClasses['stat']} */ ;
/** @type {__VLS_StyleScopedClasses['stat']} */ ;
/** @type {__VLS_StyleScopedClasses['stat']} */ ;
/** @type {__VLS_StyleScopedClasses['analysis-grid']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['stack']} */ ;
/** @type {__VLS_StyleScopedClasses['pie-row']} */ ;
/** @type {__VLS_StyleScopedClasses['pie-chart']} */ ;
/** @type {__VLS_StyleScopedClasses['muted']} */ ;
/** @type {__VLS_StyleScopedClasses['muted']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['stack']} */ ;
/** @type {__VLS_StyleScopedClasses['bar-list']} */ ;
/** @type {__VLS_StyleScopedClasses['bar-row']} */ ;
/** @type {__VLS_StyleScopedClasses['bar-track']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['stack']} */ ;
/** @type {__VLS_StyleScopedClasses['bar-list']} */ ;
/** @type {__VLS_StyleScopedClasses['bar-row']} */ ;
/** @type {__VLS_StyleScopedClasses['wide-bar']} */ ;
/** @type {__VLS_StyleScopedClasses['bar-track']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['stack']} */ ;
/** @type {__VLS_StyleScopedClasses['data-table']} */ ;
/** @type {__VLS_StyleScopedClasses['answer-list']} */ ;
/** @type {__VLS_StyleScopedClasses['answer-item']} */ ;
var __VLS_dollars;
var __VLS_self = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () {
        return {
            AppShell: AppShell_vue_1.default,
            SubmissionResult: SubmissionResult_vue_1.default,
            sessionId: sessionId,
            session: session,
            loading: loading,
            error: error,
            students: students,
            totalTaskCount: totalTaskCount,
            completedSubmissions: completedSubmissions,
            completionRate: completionRate,
            averageScore: averageScore,
            pieStyle: pieStyle,
            nodeBars: nodeBars,
            scoreBuckets: scoreBuckets,
            studentRows: studentRows,
            loadReport: loadReport,
            statusText: statusText,
        };
    },
});
exports.default = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () {
        return {};
    },
});
; /* PartiallyEnd: #4569/main.vue */
