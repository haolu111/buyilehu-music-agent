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
var vue_router_1 = require("vue-router");
var route = (0, vue_router_1.useRoute)();
var items = [
    { label: '我的教案', to: '/lesson-plans/history', match: '/lesson-plans/history' },
    { label: '上传教案', to: '/lesson-plans/upload', match: '/lesson-plans/upload' },
    { label: '生成互动包', to: '/packages/generate', match: '/packages/generate' },
];
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
var __VLS_ctx = {};
var __VLS_components;
var __VLS_directives;
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "workspace-context" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "breadcrumb" }));
(((_a = __VLS_ctx.items.find(function (item) { return __VLS_ctx.route.path.startsWith(item.match); })) === null || _a === void 0 ? void 0 : _a.label) || '内容详情');
__VLS_asFunctionalElement(__VLS_intrinsicElements.nav, __VLS_intrinsicElements.nav)(__assign({ class: "workspace-tabs" }, { 'aria-label': "教案与互动包" }));
for (var _i = 0, _b = __VLS_getVForSourceType((__VLS_ctx.items)); _i < _b.length; _i++) {
    var item = _b[_i][0];
    var __VLS_0 = {}.RouterLink;
    /** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
    // @ts-ignore
    var __VLS_1 = __VLS_asFunctionalComponent(__VLS_0, new __VLS_0(__assign({ key: (item.to), to: (item.to) }, { class: ({ active: __VLS_ctx.route.path.startsWith(item.match) }) })));
    var __VLS_2 = __VLS_1.apply(void 0, __spreadArray([__assign({ key: (item.to), to: (item.to) }, { class: ({ active: __VLS_ctx.route.path.startsWith(item.match) }) })], __VLS_functionalComponentArgsRest(__VLS_1), false));
    __VLS_3.slots.default;
    (item.label);
    var __VLS_3;
}
/** @type {__VLS_StyleScopedClasses['workspace-context']} */ ;
/** @type {__VLS_StyleScopedClasses['breadcrumb']} */ ;
/** @type {__VLS_StyleScopedClasses['workspace-tabs']} */ ;
var __VLS_dollars;
var __VLS_self = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () {
        return {
            route: route,
            items: items,
        };
    },
});
exports.default = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () {
        return {};
    },
});
; /* PartiallyEnd: #4569/main.vue */
