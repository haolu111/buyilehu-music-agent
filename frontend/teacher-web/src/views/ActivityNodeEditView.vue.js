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
var _a, _b;
Object.defineProperty(exports, "__esModule", { value: true });
/* placeholder */
var vue_1 = require("vue");
var ActivityNodeConfigForm_vue_1 = require("../components/ActivityNodeConfigForm.vue");
var ComponentParamEditor_vue_1 = require("../components/ComponentParamEditor.vue");
var MusicContentEditor_vue_1 = require("../components/MusicContentEditor.vue");
var props = defineProps();
var emit = defineEmits();
var componentParams = {};
var formPayload = {};
var musicPayload = {};
var initialMusicContent = (0, vue_1.computed)(function () {
    var _a;
    var node = (_a = props.proposal) === null || _a === void 0 ? void 0 : _a.activityNodes.find(function (item) { return item.id === props.selectedNodeId; });
    if (!(node === null || node === void 0 ? void 0 : node.configJson))
        return {};
    try {
        return JSON.parse(node.configJson).musicContent || {};
    }
    catch (_b) {
        return {};
    }
});
function save(payload) {
    emit('save', __assign(__assign(__assign({}, payload), musicPayload), { componentParams: componentParams }));
}
function preview(payload) {
    formPayload = __assign(__assign({}, formPayload), payload);
    emit('change', __assign(__assign(__assign({}, formPayload), musicPayload), { componentParams: componentParams }));
}
function updateMusic(payload) {
    musicPayload = payload;
    emit('change', __assign(__assign(__assign({}, formPayload), musicPayload), { componentParams: componentParams }));
}
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
var __VLS_ctx = {};
var __VLS_components;
var __VLS_directives;
__VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)(__assign({ class: "card stack" }));
if (__VLS_ctx.proposal && __VLS_ctx.selectedNodeId) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
    /** @type {[typeof ActivityNodeConfigForm, ]} */ ;
    // @ts-ignore
    var __VLS_0 = __VLS_asFunctionalComponent(ActivityNodeConfigForm_vue_1.default, new ActivityNodeConfigForm_vue_1.default(__assign(__assign({ 'onSave': {} }, { 'onChange': {} }), { initialTitle: ((_a = __VLS_ctx.proposal.activityNodes.find(function (node) { return node.id === __VLS_ctx.selectedNodeId; })) === null || _a === void 0 ? void 0 : _a.title) })));
    var __VLS_1 = __VLS_0.apply(void 0, __spreadArray([__assign(__assign({ 'onSave': {} }, { 'onChange': {} }), { initialTitle: ((_b = __VLS_ctx.proposal.activityNodes.find(function (node) { return node.id === __VLS_ctx.selectedNodeId; })) === null || _b === void 0 ? void 0 : _b.title) })], __VLS_functionalComponentArgsRest(__VLS_0), false));
    var __VLS_3 = void 0;
    var __VLS_4 = void 0;
    var __VLS_5 = void 0;
    var __VLS_6 = {
        onSave: (__VLS_ctx.save)
    };
    var __VLS_7 = {
        onChange: (__VLS_ctx.preview)
    };
    var __VLS_2;
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "sub-panel" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h3, __VLS_intrinsicElements.h3)({});
    /** @type {[typeof ComponentParamEditor, ]} */ ;
    // @ts-ignore
    var __VLS_8 = __VLS_asFunctionalComponent(ComponentParamEditor_vue_1.default, new ComponentParamEditor_vue_1.default(__assign({ 'onChange': {} })));
    var __VLS_9 = __VLS_8.apply(void 0, __spreadArray([__assign({ 'onChange': {} })], __VLS_functionalComponentArgsRest(__VLS_8), false));
    var __VLS_11 = void 0;
    var __VLS_12 = void 0;
    var __VLS_13 = void 0;
    var __VLS_14 = {
        onChange: function () {
            var _a = [];
            for (var _i = 0; _i < arguments.length; _i++) {
                _a[_i] = arguments[_i];
            }
            var $event = _a[0];
            if (!(__VLS_ctx.proposal && __VLS_ctx.selectedNodeId))
                return;
            __VLS_ctx.componentParams = $event;
            __VLS_ctx.preview({});
        }
    };
    var __VLS_10;
    /** @type {[typeof MusicContentEditor, ]} */ ;
    // @ts-ignore
    var __VLS_15 = __VLS_asFunctionalComponent(MusicContentEditor_vue_1.default, new MusicContentEditor_vue_1.default(__assign({ 'onChange': {} }, { initial: (__VLS_ctx.initialMusicContent) })));
    var __VLS_16 = __VLS_15.apply(void 0, __spreadArray([__assign({ 'onChange': {} }, { initial: (__VLS_ctx.initialMusicContent) })], __VLS_functionalComponentArgsRest(__VLS_15), false));
    var __VLS_18 = void 0;
    var __VLS_19 = void 0;
    var __VLS_20 = void 0;
    var __VLS_21 = {
        onChange: (__VLS_ctx.updateMusic)
    };
    var __VLS_17;
}
else {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "muted" }));
}
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['stack']} */ ;
/** @type {__VLS_StyleScopedClasses['sub-panel']} */ ;
/** @type {__VLS_StyleScopedClasses['muted']} */ ;
var __VLS_dollars;
var __VLS_self = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () {
        return {
            ActivityNodeConfigForm: ActivityNodeConfigForm_vue_1.default,
            ComponentParamEditor: ComponentParamEditor_vue_1.default,
            MusicContentEditor: MusicContentEditor_vue_1.default,
            componentParams: componentParams,
            initialMusicContent: initialMusicContent,
            save: save,
            preview: preview,
            updateMusic: updateMusic,
        };
    },
    __typeEmits: {},
    __typeProps: {},
});
exports.default = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () {
        return {};
    },
    __typeEmits: {},
    __typeProps: {},
});
; /* PartiallyEnd: #4569/main.vue */
