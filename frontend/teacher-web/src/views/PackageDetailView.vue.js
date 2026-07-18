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
var AppShell_vue_1 = require("../components/AppShell.vue");
var LessonWorkspaceNav_vue_1 = require("../components/LessonWorkspaceNav.vue");
var packageApi_1 = require("../api/packageApi");
var display_1 = require("../utils/display");
var route = (0, vue_router_1.useRoute)();
var packageId = Number(route.params.packageId);
var packageInfo = (0, vue_1.ref)(null);
var packages = (0, vue_1.ref)([]);
var error = (0, vue_1.ref)('');
(0, vue_1.onMounted)(function () { return __awaiter(void 0, void 0, void 0, function () {
    var _a, _b, exception_1;
    return __generator(this, function (_c) {
        switch (_c.label) {
            case 0:
                _c.trys.push([0, 3, , 4]);
                _a = packageInfo;
                return [4 /*yield*/, packageApi_1.packageApi.getPackage(packageId)];
            case 1:
                _a.value = _c.sent();
                _b = packages;
                return [4 /*yield*/, packageApi_1.packageApi.listPackages()];
            case 2:
                _b.value = _c.sent();
                return [3 /*break*/, 4];
            case 3:
                exception_1 = _c.sent();
                error.value = exception_1 instanceof Error ? exception_1.message : '加载互动包失败';
                return [3 /*break*/, 4];
            case 4: return [2 /*return*/];
        }
    });
}); });
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
var __VLS_8 = __VLS_asFunctionalComponent(__VLS_7, new __VLS_7(__assign({ class: "button" }, { to: "/lesson-plans/history" })));
var __VLS_9 = __VLS_8.apply(void 0, __spreadArray([__assign({ class: "button" }, { to: "/lesson-plans/history" })], __VLS_functionalComponentArgsRest(__VLS_8), false));
__VLS_10.slots.default;
var __VLS_11 = {}.ArrowLeft;
/** @type {[typeof __VLS_components.ArrowLeft, ]} */ ;
// @ts-ignore
var __VLS_12 = __VLS_asFunctionalComponent(__VLS_11, new __VLS_11({
    size: (17),
    'aria-hidden': "true",
}));
var __VLS_13 = __VLS_12.apply(void 0, __spreadArray([{
        size: (17),
        'aria-hidden': "true",
    }], __VLS_functionalComponentArgsRest(__VLS_12), false));
var __VLS_10;
if (__VLS_ctx.error) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "error" }));
    (__VLS_ctx.error);
}
if (__VLS_ctx.packageInfo) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)(__assign({ class: "card package-detail-summary" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "section-header compact" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)(__assign({ class: "status-pill" }, { class: (__VLS_ctx.packageInfo.status) }));
    (__VLS_ctx.statusText(__VLS_ctx.packageInfo.status));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
    (__VLS_ctx.packageInfo.title);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "muted" }));
    (__VLS_ctx.packageInfo.description || '课堂互动活动包');
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)(__assign({ class: "tag" }));
    (__VLS_ctx.packageInfo.currentVersionId || '—');
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "package-detail-actions" }));
    var __VLS_15 = {}.RouterLink;
    /** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
    // @ts-ignore
    var __VLS_16 = __VLS_asFunctionalComponent(__VLS_15, new __VLS_15(__assign({ class: "button" }, { to: ("/packages/".concat(__VLS_ctx.packageId, "/proposal")) })));
    var __VLS_17 = __VLS_16.apply(void 0, __spreadArray([__assign({ class: "button" }, { to: ("/packages/".concat(__VLS_ctx.packageId, "/proposal")) })], __VLS_functionalComponentArgsRest(__VLS_16), false));
    __VLS_18.slots.default;
    var __VLS_19 = {}.Eye;
    /** @type {[typeof __VLS_components.Eye, ]} */ ;
    // @ts-ignore
    var __VLS_20 = __VLS_asFunctionalComponent(__VLS_19, new __VLS_19({
        size: (17),
        'aria-hidden': "true",
    }));
    var __VLS_21 = __VLS_20.apply(void 0, __spreadArray([{
            size: (17),
            'aria-hidden': "true",
        }], __VLS_functionalComponentArgsRest(__VLS_20), false));
    var __VLS_18;
    var __VLS_23 = {}.RouterLink;
    /** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
    // @ts-ignore
    var __VLS_24 = __VLS_asFunctionalComponent(__VLS_23, new __VLS_23(__assign({ class: "button primary-soft" }, { to: ("/packages/".concat(__VLS_ctx.packageId, "/edit")) })));
    var __VLS_25 = __VLS_24.apply(void 0, __spreadArray([__assign({ class: "button primary-soft" }, { to: ("/packages/".concat(__VLS_ctx.packageId, "/edit")) })], __VLS_functionalComponentArgsRest(__VLS_24), false));
    __VLS_26.slots.default;
    var __VLS_27 = {}.Pencil;
    /** @type {[typeof __VLS_components.Pencil, ]} */ ;
    // @ts-ignore
    var __VLS_28 = __VLS_asFunctionalComponent(__VLS_27, new __VLS_27({
        size: (17),
        'aria-hidden': "true",
    }));
    var __VLS_29 = __VLS_28.apply(void 0, __spreadArray([{
            size: (17),
            'aria-hidden': "true",
        }], __VLS_functionalComponentArgsRest(__VLS_28), false));
    var __VLS_26;
    var __VLS_31 = {}.RouterLink;
    /** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
    // @ts-ignore
    var __VLS_32 = __VLS_asFunctionalComponent(__VLS_31, new __VLS_31(__assign({ class: "button primary" }, { to: ("/packages/".concat(__VLS_ctx.packageId, "/publish")) })));
    var __VLS_33 = __VLS_32.apply(void 0, __spreadArray([__assign({ class: "button primary" }, { to: ("/packages/".concat(__VLS_ctx.packageId, "/publish")) })], __VLS_functionalComponentArgsRest(__VLS_32), false));
    __VLS_34.slots.default;
    var __VLS_35 = {}.Send;
    /** @type {[typeof __VLS_components.Send, ]} */ ;
    // @ts-ignore
    var __VLS_36 = __VLS_asFunctionalComponent(__VLS_35, new __VLS_35({
        size: (17),
        'aria-hidden': "true",
    }));
    var __VLS_37 = __VLS_36.apply(void 0, __spreadArray([{
            size: (17),
            'aria-hidden': "true",
        }], __VLS_functionalComponentArgsRest(__VLS_36), false));
    var __VLS_34;
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)(__assign({ class: "card package-library-panel" }, { style: {} }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "section-header compact" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.h3, __VLS_intrinsicElements.h3)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "muted" }));
for (var _i = 0, _a = __VLS_getVForSourceType((__VLS_ctx.packages)); _i < _a.length; _i++) {
    var item = _a[_i][0];
    var __VLS_39 = {}.RouterLink;
    /** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
    // @ts-ignore
    var __VLS_40 = __VLS_asFunctionalComponent(__VLS_39, new __VLS_39(__assign(__assign({ key: (item.id) }, { class: "list-line" }), { to: ("/packages/".concat(item.id)) })));
    var __VLS_41 = __VLS_40.apply(void 0, __spreadArray([__assign(__assign({ key: (item.id) }, { class: "list-line" }), { to: ("/packages/".concat(item.id)) })], __VLS_functionalComponentArgsRest(__VLS_40), false));
    __VLS_42.slots.default;
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
    (item.title);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.small, __VLS_intrinsicElements.small)(__assign({ class: "muted" }));
    (item.description || '课堂互动活动包');
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)(__assign({ class: "status-pill" }, { class: (item.status) }));
    (__VLS_ctx.statusText(item.status));
    var __VLS_42;
}
var __VLS_2;
/** @type {__VLS_StyleScopedClasses['page-heading']} */ ;
/** @type {__VLS_StyleScopedClasses['compact']} */ ;
/** @type {__VLS_StyleScopedClasses['eyebrow']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['error']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['package-detail-summary']} */ ;
/** @type {__VLS_StyleScopedClasses['section-header']} */ ;
/** @type {__VLS_StyleScopedClasses['compact']} */ ;
/** @type {__VLS_StyleScopedClasses['status-pill']} */ ;
/** @type {__VLS_StyleScopedClasses['muted']} */ ;
/** @type {__VLS_StyleScopedClasses['tag']} */ ;
/** @type {__VLS_StyleScopedClasses['package-detail-actions']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['primary-soft']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['primary']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['package-library-panel']} */ ;
/** @type {__VLS_StyleScopedClasses['section-header']} */ ;
/** @type {__VLS_StyleScopedClasses['compact']} */ ;
/** @type {__VLS_StyleScopedClasses['muted']} */ ;
/** @type {__VLS_StyleScopedClasses['list-line']} */ ;
/** @type {__VLS_StyleScopedClasses['muted']} */ ;
/** @type {__VLS_StyleScopedClasses['status-pill']} */ ;
var __VLS_dollars;
var __VLS_self = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () {
        return {
            ArrowLeft: lucide_vue_next_1.ArrowLeft,
            Eye: lucide_vue_next_1.Eye,
            Pencil: lucide_vue_next_1.Pencil,
            Send: lucide_vue_next_1.Send,
            AppShell: AppShell_vue_1.default,
            LessonWorkspaceNav: LessonWorkspaceNav_vue_1.default,
            statusText: display_1.statusText,
            packageId: packageId,
            packageInfo: packageInfo,
            packages: packages,
            error: error,
        };
    },
});
exports.default = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () {
        return {};
    },
});
; /* PartiallyEnd: #4569/main.vue */
