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
Object.defineProperty(exports, "__esModule", { value: true });
/* placeholder */
var vue_1 = require("vue");
var vite_svg_1 = require("../assets/vite.svg");
var hero_png_1 = require("../assets/hero.png");
var vue_svg_1 = require("../assets/vue.svg");
var count = (0, vue_1.ref)(0);
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
var __VLS_ctx = {};
var __VLS_components;
var __VLS_directives;
__VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
    id: "center",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "hero" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.img)(__assign(__assign({ src: (__VLS_ctx.heroImg) }, { class: "base" }), { width: "170", height: "179", alt: "" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.img)(__assign(__assign({ src: (__VLS_ctx.vueLogo) }, { class: "framework" }), { alt: "Vue logo" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.img)(__assign(__assign({ src: (__VLS_ctx.viteLogo) }, { class: "vite" }), { alt: "Vite logo" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.h1, __VLS_intrinsicElements.h1)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.code, __VLS_intrinsicElements.code)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign(__assign({ onClick: function () {
        var _a = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            _a[_i] = arguments[_i];
        }
        var $event = _a[0];
        __VLS_ctx.count++;
    } }, { type: "button" }), { class: "counter" }));
(__VLS_ctx.count);
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "ticks" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
    id: "next-steps",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    id: "docs",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.svg, __VLS_intrinsicElements.svg)(__assign({ class: "icon" }, { role: "presentation", 'aria-hidden': "true" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.use, __VLS_intrinsicElements.use)({
    href: "/icons.svg#documentation-icon",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.ul, __VLS_intrinsicElements.ul)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.li, __VLS_intrinsicElements.li)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.a, __VLS_intrinsicElements.a)({
    href: "https://vite.dev/",
    target: "_blank",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.img)(__assign({ class: "logo" }, { src: (__VLS_ctx.viteLogo), alt: "" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.li, __VLS_intrinsicElements.li)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.a, __VLS_intrinsicElements.a)({
    href: "https://vuejs.org/",
    target: "_blank",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.img)(__assign({ class: "button-icon" }, { src: (__VLS_ctx.vueLogo), alt: "" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
    id: "social",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.svg, __VLS_intrinsicElements.svg)(__assign({ class: "icon" }, { role: "presentation", 'aria-hidden': "true" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.use, __VLS_intrinsicElements.use)({
    href: "/icons.svg#social-icon",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.ul, __VLS_intrinsicElements.ul)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.li, __VLS_intrinsicElements.li)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.a, __VLS_intrinsicElements.a)({
    href: "https://github.com/vitejs/vite",
    target: "_blank",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.svg, __VLS_intrinsicElements.svg)(__assign({ class: "button-icon" }, { role: "presentation", 'aria-hidden': "true" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.use, __VLS_intrinsicElements.use)({
    href: "/icons.svg#github-icon",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.li, __VLS_intrinsicElements.li)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.a, __VLS_intrinsicElements.a)({
    href: "https://chat.vite.dev/",
    target: "_blank",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.svg, __VLS_intrinsicElements.svg)(__assign({ class: "button-icon" }, { role: "presentation", 'aria-hidden': "true" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.use, __VLS_intrinsicElements.use)({
    href: "/icons.svg#discord-icon",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.li, __VLS_intrinsicElements.li)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.a, __VLS_intrinsicElements.a)({
    href: "https://x.com/vite_js",
    target: "_blank",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.svg, __VLS_intrinsicElements.svg)(__assign({ class: "button-icon" }, { role: "presentation", 'aria-hidden': "true" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.use, __VLS_intrinsicElements.use)({
    href: "/icons.svg#x-icon",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.li, __VLS_intrinsicElements.li)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.a, __VLS_intrinsicElements.a)({
    href: "https://bsky.app/profile/vite.dev",
    target: "_blank",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.svg, __VLS_intrinsicElements.svg)(__assign({ class: "button-icon" }, { role: "presentation", 'aria-hidden': "true" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.use, __VLS_intrinsicElements.use)({
    href: "/icons.svg#bluesky-icon",
});
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "ticks" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)({
    id: "spacer",
});
/** @type {__VLS_StyleScopedClasses['hero']} */ ;
/** @type {__VLS_StyleScopedClasses['base']} */ ;
/** @type {__VLS_StyleScopedClasses['framework']} */ ;
/** @type {__VLS_StyleScopedClasses['vite']} */ ;
/** @type {__VLS_StyleScopedClasses['counter']} */ ;
/** @type {__VLS_StyleScopedClasses['ticks']} */ ;
/** @type {__VLS_StyleScopedClasses['icon']} */ ;
/** @type {__VLS_StyleScopedClasses['logo']} */ ;
/** @type {__VLS_StyleScopedClasses['button-icon']} */ ;
/** @type {__VLS_StyleScopedClasses['icon']} */ ;
/** @type {__VLS_StyleScopedClasses['button-icon']} */ ;
/** @type {__VLS_StyleScopedClasses['button-icon']} */ ;
/** @type {__VLS_StyleScopedClasses['button-icon']} */ ;
/** @type {__VLS_StyleScopedClasses['button-icon']} */ ;
/** @type {__VLS_StyleScopedClasses['ticks']} */ ;
var __VLS_dollars;
var __VLS_self = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () {
        return {
            viteLogo: vite_svg_1.default,
            heroImg: hero_png_1.default,
            vueLogo: vue_svg_1.default,
            count: count,
        };
    },
});
exports.default = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () {
        return {};
    },
});
; /* PartiallyEnd: #4569/main.vue */
