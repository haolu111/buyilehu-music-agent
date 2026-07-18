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
Object.defineProperty(exports, "__esModule", { value: true });
/* placeholder */
var vue_1 = require("vue");
var vue_router_1 = require("vue-router");
var workflowStages = [
    { id: 'upload-lesson', label: '上传教案' },
    { id: 'confirm-content', label: '确认内容' },
    { id: 'setup-classroom', label: '设置课堂' },
    { id: 'confirm-proposal', label: '确认方案' },
    { id: 'edit-package', label: '编辑互动包' },
    { id: 'publish-classroom', label: '发布课堂' },
];
var classroomControlStage = { id: 'classroom-control', label: '课堂控制' };
var props = defineProps();
function defaultRoute(stage) {
    if (stage === 'upload-lesson')
        return '/lesson-plans/upload';
    if (stage === 'confirm-content' && props.lessonPlanId)
        return "/lesson-plans/".concat(props.lessonPlanId, "/parse-result");
    if (stage === 'setup-classroom' && props.lessonPlanId)
        return "/packages/generate?lessonPlanId=".concat(props.lessonPlanId);
    if (stage === 'confirm-proposal' && props.packageId)
        return "/packages/".concat(props.packageId, "/proposal");
    if (stage === 'edit-package' && props.packageId)
        return "/packages/".concat(props.packageId, "/edit");
    if (stage === 'publish-classroom' && props.packageId)
        return "/packages/".concat(props.packageId, "/publish");
    if (stage === 'classroom-control' && props.sessionId)
        return "/classroom/".concat(props.sessionId, "/control");
    return undefined;
}
var availableStages = (0, vue_1.computed)(function () { return props.showClassroomControl ? __spreadArray(__spreadArray([], workflowStages, true), [classroomControlStage], false) : workflowStages; });
var currentIndex = (0, vue_1.computed)(function () { return availableStages.value.findIndex(function (stage) { return stage.id === props.currentStage; }); });
var steps = (0, vue_1.computed)(function () { return availableStages.value.map(function (stage, index) {
    var _a;
    return (__assign(__assign({}, stage), { state: index < currentIndex.value ? 'completed' : index === currentIndex.value ? 'current' : 'upcoming', route: ((_a = props.routes) === null || _a === void 0 ? void 0 : _a[stage.id]) || defaultRoute(stage.id) }));
}); });
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
var __VLS_ctx = {};
var __VLS_components;
var __VLS_directives;
__VLS_asFunctionalElement(__VLS_intrinsicElements.nav, __VLS_intrinsicElements.nav)(__assign({ class: "workflow-stepper" }, { 'aria-label': "备课与课堂流程" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.ol, __VLS_intrinsicElements.ol)({});
for (var _i = 0, _a = __VLS_getVForSourceType((__VLS_ctx.steps)); _i < _a.length; _i++) {
    var _b = _a[_i], stage = _b[0], index = _b[1];
    __VLS_asFunctionalElement(__VLS_intrinsicElements.li, __VLS_intrinsicElements.li)({
        key: (stage.id),
        'data-stage': (stage.id),
        'data-state': (stage.state),
        'aria-current': (stage.state === 'current' ? 'step' : undefined),
    });
    if (stage.state === 'completed' && stage.route) {
        var __VLS_0 = {}.RouterLink;
        /** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
        // @ts-ignore
        var __VLS_1 = __VLS_asFunctionalComponent(__VLS_0, new __VLS_0({
            to: (stage.route),
        }));
        var __VLS_2 = __VLS_1.apply(void 0, __spreadArray([{
                to: (stage.route),
            }], __VLS_functionalComponentArgsRest(__VLS_1), false));
        __VLS_3.slots.default;
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)(__assign({ class: "workflow-stepper-number" }));
        (index + 1);
        (stage.label);
        var __VLS_3;
    }
    else {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
            'aria-disabled': (stage.state === 'upcoming' ? 'true' : undefined),
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)(__assign({ class: "workflow-stepper-number" }));
        (index + 1);
        (stage.label);
    }
}
/** @type {__VLS_StyleScopedClasses['workflow-stepper']} */ ;
/** @type {__VLS_StyleScopedClasses['workflow-stepper-number']} */ ;
/** @type {__VLS_StyleScopedClasses['workflow-stepper-number']} */ ;
var __VLS_dollars;
var __VLS_self = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () {
        return {
            RouterLink: vue_router_1.RouterLink,
            steps: steps,
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
