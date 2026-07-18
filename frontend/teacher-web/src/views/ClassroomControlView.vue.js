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
var _a, _b, _c, _d, _e, _f;
Object.defineProperty(exports, "__esModule", { value: true });
/* placeholder */
var vue_1 = require("vue");
var vue_router_1 = require("vue-router");
var AppShell_vue_1 = require("../components/AppShell.vue");
var SubmissionResult_vue_1 = require("../components/SubmissionResult.vue");
var WorkflowStepper_vue_1 = require("../components/WorkflowStepper.vue");
var classroomApi_1 = require("../api/classroomApi");
var presentationLabels_1 = require("../utils/presentationLabels");
var route = (0, vue_router_1.useRoute)();
var sessionId = Number(route.params.sessionId);
var session = (0, vue_1.ref)(null);
var submissions = (0, vue_1.ref)([]);
var loading = (0, vue_1.ref)(false);
var error = (0, vue_1.ref)('');
var message = (0, vue_1.ref)('');
var page = (0, vue_1.ref)(1);
var pageSize = (0, vue_1.ref)(8);
var timer = 0;
var currentNode = (0, vue_1.computed)(function () { var _a; return ((_a = session.value) === null || _a === void 0 ? void 0 : _a.nodeStates.find(function (node) { var _a; return node.activityNodeId === ((_a = session.value) === null || _a === void 0 ? void 0 : _a.currentNodeId); })) || null; });
var nextLockedNode = (0, vue_1.computed)(function () { var _a; return ((_a = session.value) === null || _a === void 0 ? void 0 : _a.nodeStates.find(function (node) { return node.status === 'locked'; })) || null; });
var latestSubmissions = (0, vue_1.computed)(function () {
    var map = new Map();
    for (var _i = 0, _a = submissions.value; _i < _a.length; _i++) {
        var item = _a[_i];
        var key = "".concat(item.studentId, "-").concat(item.nodeId);
        var existing = map.get(key);
        if (!existing || String(item.lastActiveAt || '') >= String(existing.lastActiveAt || '')) {
            map.set(key, item);
        }
    }
    return Array.from(map.values()).sort(function (left, right) {
        var studentCompare = String(left.studentName || '').localeCompare(String(right.studentName || ''));
        if (studentCompare !== 0)
            return studentCompare;
        return (left.sortOrder || 9999) - (right.sortOrder || 9999);
    });
});
var pageCount = (0, vue_1.computed)(function () { return Math.max(1, Math.ceil(latestSubmissions.value.length / pageSize.value)); });
var pagedSubmissions = (0, vue_1.computed)(function () {
    var start = (page.value - 1) * pageSize.value;
    return latestSubmissions.value.slice(start, start + pageSize.value);
});
function loadData() {
    return __awaiter(this, arguments, void 0, function (silent) {
        var _a, sessionData, submissionData, exception_1;
        if (silent === void 0) { silent = false; }
        return __generator(this, function (_b) {
            switch (_b.label) {
                case 0:
                    if (!silent)
                        loading.value = true;
                    error.value = '';
                    _b.label = 1;
                case 1:
                    _b.trys.push([1, 3, 4, 5]);
                    return [4 /*yield*/, Promise.all([
                            classroomApi_1.classroomApi.getSession(sessionId),
                            classroomApi_1.classroomApi.listSubmissions(sessionId),
                        ])];
                case 2:
                    _a = _b.sent(), sessionData = _a[0], submissionData = _a[1];
                    session.value = sessionData;
                    submissions.value = submissionData;
                    if (page.value > pageCount.value)
                        page.value = pageCount.value;
                    return [3 /*break*/, 5];
                case 3:
                    exception_1 = _b.sent();
                    error.value = exception_1 instanceof Error ? exception_1.message : '加载课堂失败';
                    return [3 /*break*/, 5];
                case 4:
                    loading.value = false;
                    return [7 /*endfinally*/];
                case 5: return [2 /*return*/];
            }
        });
    });
}
function startSession() {
    return __awaiter(this, void 0, void 0, function () {
        var _a, exception_2;
        return __generator(this, function (_b) {
            switch (_b.label) {
                case 0:
                    _b.trys.push([0, 3, , 4]);
                    _a = session;
                    return [4 /*yield*/, classroomApi_1.classroomApi.start(sessionId)];
                case 1:
                    _a.value = _b.sent();
                    message.value = '课堂已开始，第一个环节已解锁';
                    return [4 /*yield*/, loadData(true)];
                case 2:
                    _b.sent();
                    return [3 /*break*/, 4];
                case 3:
                    exception_2 = _b.sent();
                    error.value = exception_2 instanceof Error ? exception_2.message : '开始课堂失败';
                    return [3 /*break*/, 4];
                case 4: return [2 /*return*/];
            }
        });
    });
}
function unlock(nodeId) {
    return __awaiter(this, void 0, void 0, function () {
        var _a, exception_3;
        return __generator(this, function (_b) {
            switch (_b.label) {
                case 0:
                    if (!nodeId)
                        return [2 /*return*/];
                    _b.label = 1;
                case 1:
                    _b.trys.push([1, 4, , 5]);
                    _a = session;
                    return [4 /*yield*/, classroomApi_1.classroomApi.unlockNode(sessionId, nodeId)];
                case 2:
                    _a.value = _b.sent();
                    message.value = '环节已解锁';
                    return [4 /*yield*/, loadData(true)];
                case 3:
                    _b.sent();
                    return [3 /*break*/, 5];
                case 4:
                    exception_3 = _b.sent();
                    error.value = exception_3 instanceof Error ? exception_3.message : '解锁失败';
                    return [3 /*break*/, 5];
                case 5: return [2 /*return*/];
            }
        });
    });
}
function pauseSession() {
    return __awaiter(this, void 0, void 0, function () {
        var _a, exception_4;
        return __generator(this, function (_b) {
            switch (_b.label) {
                case 0:
                    _b.trys.push([0, 3, , 4]);
                    _a = session;
                    return [4 /*yield*/, classroomApi_1.classroomApi.pause(sessionId)];
                case 1:
                    _a.value = _b.sent();
                    message.value = '课堂已暂停';
                    return [4 /*yield*/, loadData(true)];
                case 2:
                    _b.sent();
                    return [3 /*break*/, 4];
                case 3:
                    exception_4 = _b.sent();
                    error.value = exception_4 instanceof Error ? exception_4.message : '暂停失败';
                    return [3 /*break*/, 4];
                case 4: return [2 /*return*/];
            }
        });
    });
}
function endSession() {
    return __awaiter(this, void 0, void 0, function () {
        var _a, exception_5;
        return __generator(this, function (_b) {
            switch (_b.label) {
                case 0:
                    _b.trys.push([0, 3, , 4]);
                    _a = session;
                    return [4 /*yield*/, classroomApi_1.classroomApi.end(sessionId)];
                case 1:
                    _a.value = _b.sent();
                    message.value = '课堂已结束，可查看课程分析';
                    return [4 /*yield*/, loadData(true)];
                case 2:
                    _b.sent();
                    return [3 /*break*/, 4];
                case 3:
                    exception_5 = _b.sent();
                    error.value = exception_5 instanceof Error ? exception_5.message : '结束失败';
                    return [3 /*break*/, 4];
                case 4: return [2 /*return*/];
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
function prevPage() {
    page.value = Math.max(1, page.value - 1);
}
function nextPage() {
    page.value = Math.min(pageCount.value, page.value + 1);
}
(0, vue_1.onMounted)(function () {
    loadData();
    timer = window.setInterval(function () { return loadData(true); }, 3000);
});
(0, vue_1.onBeforeUnmount)(function () { return window.clearInterval(timer); });
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
/** @type {[typeof WorkflowStepper, ]} */ ;
// @ts-ignore
var __VLS_4 = __VLS_asFunctionalComponent(WorkflowStepper_vue_1.default, new WorkflowStepper_vue_1.default({
    currentStage: "classroom-control",
    sessionId: (__VLS_ctx.sessionId),
    showClassroomControl: true,
}));
var __VLS_5 = __VLS_4.apply(void 0, __spreadArray([{
        currentStage: "classroom-control",
        sessionId: (__VLS_ctx.sessionId),
        showClassroomControl: true,
    }], __VLS_functionalComponentArgsRest(__VLS_4), false));
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "section-header" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.h1, __VLS_intrinsicElements.h1)({});
(((_a = __VLS_ctx.session) === null || _a === void 0 ? void 0 : _a.courseTitle) || "\u8BFE\u5802 #".concat(__VLS_ctx.sessionId));
__VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "muted" }));
(((_b = __VLS_ctx.session) === null || _b === void 0 ? void 0 : _b.classId) || '-');
(__VLS_ctx.statusText((_c = __VLS_ctx.session) === null || _c === void 0 ? void 0 : _c.status));
if ((_d = __VLS_ctx.session) === null || _d === void 0 ? void 0 : _d.scheduledStartAt) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
    (__VLS_ctx.session.scheduledStartAt);
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "button-row" }, { style: {} }));
var __VLS_7 = {}.RouterLink;
/** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
// @ts-ignore
var __VLS_8 = __VLS_asFunctionalComponent(__VLS_7, new __VLS_7(__assign({ class: "button primary" }, { to: ("/classroom/".concat(__VLS_ctx.sessionId, "/report")) })));
var __VLS_9 = __VLS_8.apply(void 0, __spreadArray([__assign({ class: "button primary" }, { to: ("/classroom/".concat(__VLS_ctx.sessionId, "/report")) })], __VLS_functionalComponentArgsRest(__VLS_8), false));
__VLS_10.slots.default;
var __VLS_10;
__VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign(__assign({ onClick: function () {
        var _a = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            _a[_i] = arguments[_i];
        }
        var $event = _a[0];
        __VLS_ctx.loadData();
    } }, { class: "button" }), { type: "button" }));
if (__VLS_ctx.error) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "error" }));
    (__VLS_ctx.error);
}
if (__VLS_ctx.message) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "success" }));
    (__VLS_ctx.message);
}
if (__VLS_ctx.session) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)(__assign({ class: "card stack" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "muted" }));
    (__VLS_ctx.session.courseDescription || '暂无课程简介');
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "button-row" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign(__assign({ onClick: (__VLS_ctx.startSession) }, { class: "primary" }), { type: "button", disabled: (__VLS_ctx.session.status === 'running' || __VLS_ctx.session.status === 'ended') }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign(__assign({ onClick: function () {
            var _a;
            var _b = [];
            for (var _i = 0; _i < arguments.length; _i++) {
                _b[_i] = arguments[_i];
            }
            var $event = _b[0];
            if (!(__VLS_ctx.session))
                return;
            __VLS_ctx.unlock((_a = __VLS_ctx.nextLockedNode) === null || _a === void 0 ? void 0 : _a.activityNodeId);
        } }, { class: "button" }), { type: "button", disabled: (__VLS_ctx.session.status !== 'running' || !__VLS_ctx.nextLockedNode) }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign(__assign({ onClick: (__VLS_ctx.pauseSession) }, { class: "button" }), { type: "button", disabled: (__VLS_ctx.session.status !== 'running') }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign(__assign({ onClick: (__VLS_ctx.endSession) }, { class: "button" }), { type: "button", disabled: (__VLS_ctx.session.status === 'ended') }));
}
if (__VLS_ctx.session) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)(__assign({ class: "card stack" }, { style: {} }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "list" }));
    var _loop_1 = function (node) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ key: (node.id) }, { class: "list-line" }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
        __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
        (node.sortOrder);
        (node.title);
        __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "muted" }));
        (__VLS_ctx.nodeTypeDisplayName(node.nodeType));
        (__VLS_ctx.statusText(node.status));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign(__assign({ onClick: function () {
                var _a = [];
                for (var _i = 0; _i < arguments.length; _i++) {
                    _a[_i] = arguments[_i];
                }
                var $event = _a[0];
                if (!(__VLS_ctx.session))
                    return;
                __VLS_ctx.unlock(node.activityNodeId);
            } }, { class: "button" }), { type: "button", disabled: (__VLS_ctx.session.status !== 'running' || node.status === 'unlocked') }));
    };
    for (var _i = 0, _g = __VLS_getVForSourceType((__VLS_ctx.session.nodeStates)); _i < _g.length; _i++) {
        var node = _g[_i][0];
        _loop_1(node);
    }
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "muted" }));
    (((_e = __VLS_ctx.currentNode) === null || _e === void 0 ? void 0 : _e.title) || '尚未选择');
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)(__assign({ class: "card stack" }, { style: {} }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "section-header compact" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "muted" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)(__assign({ class: "tag" }));
(__VLS_ctx.latestSubmissions.length);
if (__VLS_ctx.loading) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "muted" }));
}
else if (!__VLS_ctx.latestSubmissions.length) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "muted" }));
}
else {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.table, __VLS_intrinsicElements.table)(__assign({ class: "data-table" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.thead, __VLS_intrinsicElements.thead)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.tr, __VLS_intrinsicElements.tr)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.th, __VLS_intrinsicElements.th)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.th, __VLS_intrinsicElements.th)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.th, __VLS_intrinsicElements.th)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.th, __VLS_intrinsicElements.th)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.th, __VLS_intrinsicElements.th)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.th, __VLS_intrinsicElements.th)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.tbody, __VLS_intrinsicElements.tbody)({});
    for (var _h = 0, _j = __VLS_getVForSourceType((__VLS_ctx.pagedSubmissions)); _h < _j.length; _h++) {
        var item = _j[_h][0];
        __VLS_asFunctionalElement(__VLS_intrinsicElements.tr, __VLS_intrinsicElements.tr)({
            key: ("".concat(item.studentId, "-").concat(item.nodeId)),
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.td, __VLS_intrinsicElements.td)({});
        (item.studentName || "\u5B66\u751F #".concat(item.studentId));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.td, __VLS_intrinsicElements.td)({});
        (item.nodeTitle || "\u73AF\u8282 #".concat(item.nodeId));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.td, __VLS_intrinsicElements.td)({});
        (__VLS_ctx.statusText(item.progressStatus));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.td, __VLS_intrinsicElements.td)({});
        ((_f = item.score) !== null && _f !== void 0 ? _f : '-');
        __VLS_asFunctionalElement(__VLS_intrinsicElements.td, __VLS_intrinsicElements.td)({});
        /** @type {[typeof SubmissionResult, ]} */ ;
        // @ts-ignore
        var __VLS_11 = __VLS_asFunctionalComponent(SubmissionResult_vue_1.default, new SubmissionResult_vue_1.default({
            value: (item.resultJson),
        }));
        var __VLS_12 = __VLS_11.apply(void 0, __spreadArray([{
                value: (item.resultJson),
            }], __VLS_functionalComponentArgsRest(__VLS_11), false));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.td, __VLS_intrinsicElements.td)({});
        (item.lastActiveAt || '-');
    }
}
if (__VLS_ctx.latestSubmissions.length) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "button-row" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign(__assign({ onClick: (__VLS_ctx.prevPage) }, { class: "button" }), { type: "button", disabled: (__VLS_ctx.page <= 1) }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)(__assign({ class: "muted" }));
    (__VLS_ctx.page);
    (__VLS_ctx.pageCount);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign(__assign({ onClick: (__VLS_ctx.nextPage) }, { class: "button" }), { type: "button", disabled: (__VLS_ctx.page >= __VLS_ctx.pageCount) }));
}
var __VLS_2;
/** @type {__VLS_StyleScopedClasses['section-header']} */ ;
/** @type {__VLS_StyleScopedClasses['muted']} */ ;
/** @type {__VLS_StyleScopedClasses['button-row']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['primary']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['error']} */ ;
/** @type {__VLS_StyleScopedClasses['success']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['stack']} */ ;
/** @type {__VLS_StyleScopedClasses['muted']} */ ;
/** @type {__VLS_StyleScopedClasses['button-row']} */ ;
/** @type {__VLS_StyleScopedClasses['primary']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['stack']} */ ;
/** @type {__VLS_StyleScopedClasses['list']} */ ;
/** @type {__VLS_StyleScopedClasses['list-line']} */ ;
/** @type {__VLS_StyleScopedClasses['muted']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['muted']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['stack']} */ ;
/** @type {__VLS_StyleScopedClasses['section-header']} */ ;
/** @type {__VLS_StyleScopedClasses['compact']} */ ;
/** @type {__VLS_StyleScopedClasses['muted']} */ ;
/** @type {__VLS_StyleScopedClasses['tag']} */ ;
/** @type {__VLS_StyleScopedClasses['muted']} */ ;
/** @type {__VLS_StyleScopedClasses['muted']} */ ;
/** @type {__VLS_StyleScopedClasses['data-table']} */ ;
/** @type {__VLS_StyleScopedClasses['button-row']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['muted']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
var __VLS_dollars;
var __VLS_self = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () {
        return {
            AppShell: AppShell_vue_1.default,
            SubmissionResult: SubmissionResult_vue_1.default,
            WorkflowStepper: WorkflowStepper_vue_1.default,
            nodeTypeDisplayName: presentationLabels_1.nodeTypeDisplayName,
            sessionId: sessionId,
            session: session,
            loading: loading,
            error: error,
            message: message,
            page: page,
            currentNode: currentNode,
            nextLockedNode: nextLockedNode,
            latestSubmissions: latestSubmissions,
            pageCount: pageCount,
            pagedSubmissions: pagedSubmissions,
            loadData: loadData,
            startSession: startSession,
            unlock: unlock,
            pauseSession: pauseSession,
            endSession: endSession,
            statusText: statusText,
            prevPage: prevPage,
            nextPage: nextPage,
        };
    },
});
exports.default = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () {
        return {};
    },
});
; /* PartiallyEnd: #4569/main.vue */
