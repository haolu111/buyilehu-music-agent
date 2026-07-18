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
var _a;
Object.defineProperty(exports, "__esModule", { value: true });
/* placeholder */
var vue_1 = require("vue");
var vue_router_1 = require("vue-router");
var AppShell_vue_1 = require("../components/AppShell.vue");
var classroomApi_1 = require("../api/classroomApi");
var display_1 = require("../utils/display");
var route = (0, vue_router_1.useRoute)(), sessions = (0, vue_1.ref)([]), loading = (0, vue_1.ref)(false), error = (0, vue_1.ref)(''), activeStatus = (0, vue_1.ref)(String(route.query.view || 'all'));
var counts = (0, vue_1.computed)(function () { return ({ not_started: sessions.value.filter(function (x) { return x.status === 'not_started'; }).length, running: sessions.value.filter(function (x) { return ['running', 'paused'].includes(x.status); }).length, ended: sessions.value.filter(function (x) { return x.status === 'ended'; }).length }); });
var filtered = (0, vue_1.computed)(function () { return activeStatus.value === 'all' ? sessions.value : sessions.value.filter(function (x) { return activeStatus.value === 'running' ? ['running', 'paused'].includes(x.status) : x.status === activeStatus.value; }); });
function loadSessions() {
    return __awaiter(this, void 0, void 0, function () { var _a, e_1; return __generator(this, function (_b) {
        switch (_b.label) {
            case 0:
                loading.value = true;
                error.value = '';
                _b.label = 1;
            case 1:
                _b.trys.push([1, 3, 4, 5]);
                _a = sessions;
                return [4 /*yield*/, classroomApi_1.classroomApi.listActiveSessions()];
            case 2:
                _a.value = _b.sent();
                return [3 /*break*/, 5];
            case 3:
                e_1 = _b.sent();
                error.value = e_1 instanceof Error ? e_1.message : '加载课堂失败';
                return [3 /*break*/, 5];
            case 4:
                loading.value = false;
                return [7 /*endfinally*/];
            case 5: return [2 /*return*/];
        }
    }); });
}
(0, vue_1.onMounted)(loadSessions);
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
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "page-heading" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "eyebrow" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.h1, __VLS_intrinsicElements.h1)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign({ onClick: (__VLS_ctx.loadSessions) }, { class: "button" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.nav, __VLS_intrinsicElements.nav)(__assign({ class: "status-tabs" }, { 'aria-label': "课堂状态" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign({ onClick: function () {
        var _a = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            _a[_i] = arguments[_i];
        }
        var $event = _a[0];
        __VLS_ctx.activeStatus = 'all';
    } }, { class: ({ active: __VLS_ctx.activeStatus === 'all' }) }));
(__VLS_ctx.sessions.length);
__VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign({ onClick: function () {
        var _a = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            _a[_i] = arguments[_i];
        }
        var $event = _a[0];
        __VLS_ctx.activeStatus = 'not_started';
    } }, { class: ({ active: __VLS_ctx.activeStatus === 'not_started' }) }));
(__VLS_ctx.counts.not_started);
__VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign({ onClick: function () {
        var _a = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            _a[_i] = arguments[_i];
        }
        var $event = _a[0];
        __VLS_ctx.activeStatus = 'running';
    } }, { class: ({ active: __VLS_ctx.activeStatus === 'running' }) }));
(__VLS_ctx.counts.running);
__VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign({ onClick: function () {
        var _a = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            _a[_i] = arguments[_i];
        }
        var $event = _a[0];
        __VLS_ctx.activeStatus = 'ended';
    } }, { class: ({ active: __VLS_ctx.activeStatus === 'ended' }) }));
(__VLS_ctx.counts.ended);
if (__VLS_ctx.error) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "error" }));
    (__VLS_ctx.error);
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "session-list" }));
var _loop_1 = function (session) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.article, __VLS_intrinsicElements.article)(__assign({ key: (session.id) }, { class: "card session-card" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "session-date" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
    (__VLS_ctx.formatDateTime(session.scheduledStartAt || session.startedAt).split(' ')[0]);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
    (__VLS_ctx.formatDateTime(session.scheduledStartAt || session.startedAt).split(' ').slice(1).join(' '));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "session-info" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)(__assign({ class: "status-pill" }, { class: (session.status) }));
    (__VLS_ctx.statusText(session.status));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
    (session.courseTitle || '音乐课堂');
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
    (session.nodeStates.length);
    if (session.status === 'running' && session.currentNodeId) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
        (((_a = session.nodeStates.find(function (node) { return node.activityNodeId === session.currentNodeId; })) === null || _a === void 0 ? void 0 : _a.title) || '课堂活动');
    }
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "session-action" }));
    if (session.status === 'ended') {
        var __VLS_4 = {}.RouterLink;
        /** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
        // @ts-ignore
        var __VLS_5 = __VLS_asFunctionalComponent(__VLS_4, new __VLS_4(__assign({ class: "button primary-soft" }, { to: ("/classroom/".concat(session.id, "/report")) })));
        var __VLS_6 = __VLS_5.apply(void 0, __spreadArray([__assign({ class: "button primary-soft" }, { to: ("/classroom/".concat(session.id, "/report")) })], __VLS_functionalComponentArgsRest(__VLS_5), false));
        __VLS_7.slots.default;
    }
    else {
        var __VLS_8 = {}.RouterLink;
        /** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
        // @ts-ignore
        var __VLS_9 = __VLS_asFunctionalComponent(__VLS_8, new __VLS_8(__assign({ class: "button teaching" }, { to: ("/classroom/".concat(session.id, "/control")) })));
        var __VLS_10 = __VLS_9.apply(void 0, __spreadArray([__assign({ class: "button teaching" }, { to: ("/classroom/".concat(session.id, "/control")) })], __VLS_functionalComponentArgsRest(__VLS_9), false));
        __VLS_11.slots.default;
        (session.status === 'not_started' ? '开始课堂' : '进入控制台');
    }
};
var __VLS_7, __VLS_11;
for (var _i = 0, _b = __VLS_getVForSourceType((__VLS_ctx.filtered)); _i < _b.length; _i++) {
    var session = _b[_i][0];
    _loop_1(session);
}
if (!__VLS_ctx.filtered.length) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "empty-inline" }));
    (__VLS_ctx.loading ? '正在加载课堂…' : '当前分类下暂无课堂');
}
var __VLS_2;
/** @type {__VLS_StyleScopedClasses['page-heading']} */ ;
/** @type {__VLS_StyleScopedClasses['eyebrow']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['status-tabs']} */ ;
/** @type {__VLS_StyleScopedClasses['error']} */ ;
/** @type {__VLS_StyleScopedClasses['session-list']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['session-card']} */ ;
/** @type {__VLS_StyleScopedClasses['session-date']} */ ;
/** @type {__VLS_StyleScopedClasses['session-info']} */ ;
/** @type {__VLS_StyleScopedClasses['status-pill']} */ ;
/** @type {__VLS_StyleScopedClasses['session-action']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['primary-soft']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['teaching']} */ ;
/** @type {__VLS_StyleScopedClasses['empty-inline']} */ ;
var __VLS_dollars;
var __VLS_self = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () {
        return {
            AppShell: AppShell_vue_1.default,
            formatDateTime: display_1.formatDateTime,
            statusText: display_1.statusText,
            sessions: sessions,
            loading: loading,
            error: error,
            activeStatus: activeStatus,
            counts: counts,
            filtered: filtered,
            loadSessions: loadSessions,
        };
    },
});
exports.default = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () {
        return {};
    },
});
; /* PartiallyEnd: #4569/main.vue */
