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
var props = defineProps();
var labels = {
    observed: '完成内容', sequence: '节奏组合', title: '作品名称', notes: '创作说明',
    answer: '学生答案', choice: '选择结果', difficulty: '活动难度',
};
var observedLabels = {
    entry: '已进入课堂', meter_experience: '完成节拍体验', rhythm: '完成节奏活动',
    summary: '已查看课堂小结', creation: '完成音乐创编',
};
var fields = (0, vue_1.computed)(function () {
    if (!props.value)
        return [];
    try {
        var parsed = JSON.parse(props.value);
        if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed))
            return [{ label: '提交内容', value: String(parsed) }];
        return Object.entries(parsed).map(function (_a) {
            var key = _a[0], value = _a[1];
            return ({
                label: labels[key] || '活动记录',
                value: key === 'observed' ? (observedLabels[String(value)] || '已完成活动') : Array.isArray(value) ? value.join('、') : typeof value === 'object' ? '已保存活动数据' : String(value),
            });
        });
    }
    catch (_a) {
        return [{ label: '提交内容', value: props.value }];
    }
});
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
var __VLS_ctx = {};
var __VLS_components;
var __VLS_directives;
if (__VLS_ctx.fields.length) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "submission-result" }));
    for (var _i = 0, _a = __VLS_getVForSourceType((__VLS_ctx.fields)); _i < _a.length; _i++) {
        var field = _a[_i][0];
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
            key: ("".concat(field.label, "-").concat(field.value)),
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.small, __VLS_intrinsicElements.small)({});
        (field.label);
        __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
        (field.value);
    }
}
else {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)(__assign({ class: "muted" }));
}
/** @type {__VLS_StyleScopedClasses['submission-result']} */ ;
/** @type {__VLS_StyleScopedClasses['muted']} */ ;
var __VLS_dollars;
var __VLS_self = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () {
        return {
            fields: fields,
        };
    },
    __typeProps: {},
});
exports.default = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () {
        return {};
    },
    __typeProps: {},
});
; /* PartiallyEnd: #4569/main.vue */
