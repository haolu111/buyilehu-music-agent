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
var lucide_vue_next_1 = require("lucide-vue-next");
var vue_1 = require("vue");
var vue_router_1 = require("vue-router");
var authStore_1 = require("../stores/authStore");
var buyilehu_logo_sidebar_png_1 = require("../assets/buyilehu-logo-sidebar.png");
var sidebar_music_notes_png_1 = require("../assets/sidebar-music-notes.png");
var route = (0, vue_router_1.useRoute)();
var router = (0, vue_router_1.useRouter)();
var auth = (0, authStore_1.useAuthStore)();
var teacherName = (0, vue_1.computed)(function () { var _a, _b, _c; return ((_a = auth.user) === null || _a === void 0 ? void 0 : _a.displayName) || ((_b = auth.user) === null || _b === void 0 ? void 0 : _b.realName) || ((_c = auth.user) === null || _c === void 0 ? void 0 : _c.username) || '音乐教师'; });
var workspacePageClass = (0, vue_1.computed)(function () {
    var path = route.path;
    if (path.startsWith('/lesson-plans') || path.startsWith('/packages'))
        return 'workspace-page prep-workspace-page';
    if (path.startsWith('/classes'))
        return 'workspace-page class-workspace-page';
    if (path.startsWith('/classrooms') || path.startsWith('/classroom/'))
        return 'workspace-page classroom-workspace-page';
    if (path.startsWith('/reports'))
        return 'workspace-page report-workspace-page';
    if (path.startsWith('/profile') || path.startsWith('/settings') || path.startsWith('/help'))
        return 'workspace-page account-workspace-page';
    return '';
});
var navItems = [
    { label: '工作台', compactLabel: '首页', icon: lucide_vue_next_1.LayoutDashboard, to: '/dashboard', matches: ['/dashboard'] },
    { label: '教案与互动包', compactLabel: '备课', icon: lucide_vue_next_1.FileMusic, to: '/lesson-plans/history', matches: ['/lesson-plans', '/packages'] },
    { label: '班级与学生', compactLabel: '班级', icon: lucide_vue_next_1.Users, to: '/classes', matches: ['/classes'] },
    { label: '课堂教学', compactLabel: '上课', icon: lucide_vue_next_1.Presentation, to: '/classrooms', matches: ['/classrooms', '/classroom/'] },
    { label: '数据报告', compactLabel: '报告', icon: lucide_vue_next_1.ChartNoAxesCombined, to: '/reports', matches: ['/reports'] },
];
function isActive(item) {
    if (item.label === '数据报告' && route.path.endsWith('/report'))
        return true;
    if (item.label === '课堂教学' && route.path.endsWith('/report'))
        return false;
    return item.matches.some(function (path) { return route.path === path || route.path.startsWith("".concat(path, "/")) || (path.endsWith('/') && route.path.startsWith(path)); });
}
function logout() {
    return __awaiter(this, void 0, void 0, function () { return __generator(this, function (_a) {
        switch (_a.label) {
            case 0:
                auth.logout();
                return [4 /*yield*/, router.push('/login')];
            case 1:
                _a.sent();
                return [2 /*return*/];
        }
    }); });
}
(0, vue_1.onMounted)(function () { if (!auth.user && auth.isLoggedIn)
    auth.fetchMe().catch(function () { return undefined; }); });
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
var __VLS_ctx = {};
var __VLS_components;
var __VLS_directives;
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "app-shell" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.aside, __VLS_intrinsicElements.aside)(__assign({ class: "sidebar" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "brand brand-logo-lockup" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.img)(__assign({ class: "brand-logo-image" }, { src: (__VLS_ctx.buyilehuLogo), alt: "不亦乐乎" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.nav, __VLS_intrinsicElements.nav)(__assign({ class: "nav" }, { 'aria-label': "主导航" }));
for (var _i = 0, _a = __VLS_getVForSourceType((__VLS_ctx.navItems)); _i < _a.length; _i++) {
    var item = _a[_i][0];
    var __VLS_0 = {}.RouterLink;
    /** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
    // @ts-ignore
    var __VLS_1 = __VLS_asFunctionalComponent(__VLS_0, new __VLS_0(__assign({ key: (item.label), to: (item.to), 'aria-label': (item.label), activeClass: "route-match", exactActiveClass: "route-exact-match" }, { class: ({ active: __VLS_ctx.isActive(item) }) })));
    var __VLS_2 = __VLS_1.apply(void 0, __spreadArray([__assign({ key: (item.label), to: (item.to), 'aria-label': (item.label), activeClass: "route-match", exactActiveClass: "route-exact-match" }, { class: ({ active: __VLS_ctx.isActive(item) }) })], __VLS_functionalComponentArgsRest(__VLS_1), false));
    __VLS_3.slots.default;
    var __VLS_4 = ((item.icon));
    // @ts-ignore
    var __VLS_5 = __VLS_asFunctionalComponent(__VLS_4, new __VLS_4({
        size: (18),
        strokeWidth: "2",
        'aria-hidden': "true",
    }));
    var __VLS_6 = __VLS_5.apply(void 0, __spreadArray([{
            size: (18),
            strokeWidth: "2",
            'aria-hidden': "true",
        }], __VLS_functionalComponentArgsRest(__VLS_5), false));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)(__assign({ class: "nav-label-desktop" }, { 'aria-hidden': "true" }));
    (item.label);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)(__assign({ class: "nav-label-mobile" }, { 'aria-hidden': "true" }));
    (item.compactLabel);
    var __VLS_3;
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "sidebar-art" }, { 'aria-hidden': "true" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.img)({
    src: (__VLS_ctx.sidebarMusicNotes),
    alt: "",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.main, __VLS_intrinsicElements.main)(__assign({ class: "main" }, { class: ({ 'dashboard-main': __VLS_ctx.route.path === '/dashboard' }) }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.header, __VLS_intrinsicElements.header)(__assign({ class: "topbar" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.details, __VLS_intrinsicElements.details)(__assign({ class: "teacher-menu" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.summary, __VLS_intrinsicElements.summary)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)(__assign({ class: "teacher-avatar" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
(__VLS_ctx.teacherName);
__VLS_asFunctionalElement(__VLS_intrinsicElements.small, __VLS_intrinsicElements.small)({});
var __VLS_8 = {}.ChevronDown;
/** @type {[typeof __VLS_components.ChevronDown, ]} */ ;
// @ts-ignore
var __VLS_9 = __VLS_asFunctionalComponent(__VLS_8, new __VLS_8({
    size: (18),
    'aria-hidden': "true",
}));
var __VLS_10 = __VLS_9.apply(void 0, __spreadArray([{
        size: (18),
        'aria-hidden': "true",
    }], __VLS_functionalComponentArgsRest(__VLS_9), false));
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "teacher-menu-panel" }));
var __VLS_12 = {}.RouterLink;
/** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
// @ts-ignore
var __VLS_13 = __VLS_asFunctionalComponent(__VLS_12, new __VLS_12({
    to: "/profile",
}));
var __VLS_14 = __VLS_13.apply(void 0, __spreadArray([{
        to: "/profile",
    }], __VLS_functionalComponentArgsRest(__VLS_13), false));
__VLS_15.slots.default;
var __VLS_15;
var __VLS_16 = {}.RouterLink;
/** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
// @ts-ignore
var __VLS_17 = __VLS_asFunctionalComponent(__VLS_16, new __VLS_16({
    to: "/settings",
}));
var __VLS_18 = __VLS_17.apply(void 0, __spreadArray([{
        to: "/settings",
    }], __VLS_functionalComponentArgsRest(__VLS_17), false));
__VLS_19.slots.default;
var __VLS_19;
var __VLS_20 = {}.RouterLink;
/** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
// @ts-ignore
var __VLS_21 = __VLS_asFunctionalComponent(__VLS_20, new __VLS_20({
    to: "/help",
}));
var __VLS_22 = __VLS_21.apply(void 0, __spreadArray([{
        to: "/help",
    }], __VLS_functionalComponentArgsRest(__VLS_21), false));
__VLS_23.slots.default;
var __VLS_23;
__VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign(__assign({ onClick: (__VLS_ctx.logout) }, { class: "danger-text" }), { type: "button" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)(__assign({ class: "page" }, { class: ([{ 'dashboard-page': __VLS_ctx.route.path === '/dashboard' }, __VLS_ctx.workspacePageClass]) }));
var __VLS_24 = {};
/** @type {__VLS_StyleScopedClasses['app-shell']} */ ;
/** @type {__VLS_StyleScopedClasses['sidebar']} */ ;
/** @type {__VLS_StyleScopedClasses['brand']} */ ;
/** @type {__VLS_StyleScopedClasses['brand-logo-lockup']} */ ;
/** @type {__VLS_StyleScopedClasses['brand-logo-image']} */ ;
/** @type {__VLS_StyleScopedClasses['nav']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-label-desktop']} */ ;
/** @type {__VLS_StyleScopedClasses['nav-label-mobile']} */ ;
/** @type {__VLS_StyleScopedClasses['sidebar-art']} */ ;
/** @type {__VLS_StyleScopedClasses['main']} */ ;
/** @type {__VLS_StyleScopedClasses['topbar']} */ ;
/** @type {__VLS_StyleScopedClasses['teacher-menu']} */ ;
/** @type {__VLS_StyleScopedClasses['teacher-avatar']} */ ;
/** @type {__VLS_StyleScopedClasses['teacher-menu-panel']} */ ;
/** @type {__VLS_StyleScopedClasses['danger-text']} */ ;
/** @type {__VLS_StyleScopedClasses['page']} */ ;
// @ts-ignore
var __VLS_25 = __VLS_24;
var __VLS_dollars;
var __VLS_self = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () {
        return {
            ChevronDown: lucide_vue_next_1.ChevronDown,
            buyilehuLogo: buyilehu_logo_sidebar_png_1.default,
            sidebarMusicNotes: sidebar_music_notes_png_1.default,
            route: route,
            teacherName: teacherName,
            workspacePageClass: workspacePageClass,
            navItems: navItems,
            isActive: isActive,
            logout: logout,
        };
    },
});
var __VLS_component = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () {
        return {};
    },
});
exports.default = {};
; /* PartiallyEnd: #4569/main.vue */
