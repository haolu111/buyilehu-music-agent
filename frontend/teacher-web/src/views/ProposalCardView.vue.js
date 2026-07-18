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
var vue_1 = require("vue");
var lucide_vue_next_1 = require("lucide-vue-next");
var vue_router_1 = require("vue-router");
var AppShell_vue_1 = require("../components/AppShell.vue");
var LessonWorkspaceNav_vue_1 = require("../components/LessonWorkspaceNav.vue");
var WorkflowStepper_vue_1 = require("../components/WorkflowStepper.vue");
var InteractivePackagePreview_vue_1 = require("../components/InteractivePackagePreview.vue");
var packageApi_1 = require("../api/packageApi");
var presentationLabels_1 = require("../utils/presentationLabels");
var route = (0, vue_router_1.useRoute)();
var router = (0, vue_router_1.useRouter)();
var packageId = Number(route.params.packageId);
var proposal = (0, vue_1.ref)(null);
var loading = (0, vue_1.ref)(false);
var error = (0, vue_1.ref)('');
var previewOpen = (0, vue_1.ref)(false);
var contentEntries = (0, vue_1.computed)(function () {
    var _a, _b;
    return (((_b = (_a = proposal.value) === null || _a === void 0 ? void 0 : _a.content) === null || _b === void 0 ? void 0 : _b.split(/\r?\n/).map(function (line) { return line.trim(); }).filter(Boolean)) || []).map(function (line) {
        var separator = line.search(/[：:]/);
        return separator > 0 ? { label: line.slice(0, separator).trim(), value: line.slice(separator + 1).trim() } : { label: '方案说明', value: line };
    });
});
var summaryEntries = (0, vue_1.computed)(function () { return contentEntries.value.filter(function (entry) { return !/追踪|评分|request|trace/i.test(entry.label); }).slice(0, 4); });
var technicalEntries = (0, vue_1.computed)(function () { return contentEntries.value.filter(function (entry) { return !summaryEntries.value.includes(entry); }); });
var isConfirmed = (0, vue_1.computed)(function () { var _a; return ((_a = proposal.value) === null || _a === void 0 ? void 0 : _a.confirmStatus) === 'confirmed'; });
var statusText = (0, vue_1.computed)(function () { return isConfirmed.value ? '已确认' : '待确认'; });
function loadProposal() {
    return __awaiter(this, void 0, void 0, function () { var _a; return __generator(this, function (_b) {
        switch (_b.label) {
            case 0:
                _a = proposal;
                return [4 /*yield*/, packageApi_1.packageApi.getProposal(packageId)];
            case 1:
                _a.value = _b.sent();
                return [2 /*return*/];
        }
    }); });
}
function confirm() {
    return __awaiter(this, void 0, void 0, function () {
        var _a, err_1;
        return __generator(this, function (_b) {
            switch (_b.label) {
                case 0:
                    if (isConfirmed.value)
                        return [2 /*return*/];
                    loading.value = true;
                    error.value = '';
                    _b.label = 1;
                case 1:
                    _b.trys.push([1, 4, 5, 6]);
                    _a = proposal;
                    return [4 /*yield*/, packageApi_1.packageApi.confirmProposal(packageId)];
                case 2:
                    _a.value = _b.sent();
                    return [4 /*yield*/, router.push("/packages/".concat(packageId, "/edit"))];
                case 3:
                    _b.sent();
                    return [3 /*break*/, 6];
                case 4:
                    err_1 = _b.sent();
                    error.value = err_1 instanceof Error ? err_1.message : '确认方案失败，请重试';
                    return [3 /*break*/, 6];
                case 5:
                    loading.value = false;
                    return [7 /*endfinally*/];
                case 6: return [2 /*return*/];
            }
        });
    });
}
function returnToSettings() {
    var _a, _b;
    var lessonPlanId = (_b = (_a = proposal.value) === null || _a === void 0 ? void 0 : _a.packageInfo) === null || _b === void 0 ? void 0 : _b.lessonPlanId;
    router.push(lessonPlanId ? "/packages/generate?lessonPlanId=".concat(lessonPlanId) : '/packages/generate');
}
(0, vue_1.onMounted)(function () { return loadProposal().catch(function (err) { return (error.value = err instanceof Error ? err.message : '方案加载失败'); }); });
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
/** @type {[typeof WorkflowStepper, ]} */ ;
// @ts-ignore
var __VLS_7 = __VLS_asFunctionalComponent(WorkflowStepper_vue_1.default, new WorkflowStepper_vue_1.default({
    currentStage: "confirm-proposal",
    packageId: (__VLS_ctx.packageId),
}));
var __VLS_8 = __VLS_7.apply(void 0, __spreadArray([{
        currentStage: "confirm-proposal",
        packageId: (__VLS_ctx.packageId),
    }], __VLS_functionalComponentArgsRest(__VLS_7), false));
__VLS_asFunctionalElement(__VLS_intrinsicElements.header, __VLS_intrinsicElements.header)(__assign({ class: "page-heading proposal-page-heading" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "eyebrow" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.h1, __VLS_intrinsicElements.h1)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
if (__VLS_ctx.error) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "proposal-alert" }, { role: "alert" }));
    (__VLS_ctx.error);
}
if (!__VLS_ctx.proposal && !__VLS_ctx.error) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "proposal-loading" }, { 'aria-label': "正在加载方案" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span)({});
}
if (__VLS_ctx.proposal) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "proposal-layout" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)(__assign({ class: "proposal-decision" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "proposal-title-block" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "proposal-title-row" }));
    var __VLS_10 = {}.CheckCircle2;
    /** @type {[typeof __VLS_components.CheckCircle2, ]} */ ;
    // @ts-ignore
    var __VLS_11 = __VLS_asFunctionalComponent(__VLS_10, new __VLS_10(__assign({ class: "proposal-mark" }, { size: (24), 'aria-hidden': "true" })));
    var __VLS_12 = __VLS_11.apply(void 0, __spreadArray([__assign({ class: "proposal-mark" }, { size: (24), 'aria-hidden': "true" })], __VLS_functionalComponentArgsRest(__VLS_11), false));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)(__assign({ class: "status-pill" }, { class: (__VLS_ctx.proposal.confirmStatus) }));
    (__VLS_ctx.statusText);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
    (__VLS_ctx.proposal.title);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
    (__VLS_ctx.proposal.versionNo || 1);
    (__VLS_ctx.proposal.activityNodes.length);
    (__VLS_ctx.proposal.components.length);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "proposal-confirm-area" }));
    if (__VLS_ctx.isConfirmed) {
        var __VLS_14 = {}.RouterLink;
        /** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
        // @ts-ignore
        var __VLS_15 = __VLS_asFunctionalComponent(__VLS_14, new __VLS_14(__assign({ class: "button primary" }, { to: ("/packages/".concat(__VLS_ctx.packageId, "/edit")), dataTestid: "edit-confirmed-package" })));
        var __VLS_16 = __VLS_15.apply(void 0, __spreadArray([__assign({ class: "button primary" }, { to: ("/packages/".concat(__VLS_ctx.packageId, "/edit")), dataTestid: "edit-confirmed-package" })], __VLS_functionalComponentArgsRest(__VLS_15), false));
        __VLS_17.slots.default;
        var __VLS_18 = {}.Pencil;
        /** @type {[typeof __VLS_components.Pencil, ]} */ ;
        // @ts-ignore
        var __VLS_19 = __VLS_asFunctionalComponent(__VLS_18, new __VLS_18({
            size: (18),
            'aria-hidden': "true",
        }));
        var __VLS_20 = __VLS_19.apply(void 0, __spreadArray([{
                size: (18),
                'aria-hidden': "true",
            }], __VLS_functionalComponentArgsRest(__VLS_19), false));
        var __VLS_17;
    }
    else {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign(__assign({ onClick: (__VLS_ctx.returnToSettings) }, { class: "button ghost" }), { 'data-testid': "back-to-classroom-settings", type: "button" }));
        var __VLS_22 = {}.ArrowLeft;
        /** @type {[typeof __VLS_components.ArrowLeft, ]} */ ;
        // @ts-ignore
        var __VLS_23 = __VLS_asFunctionalComponent(__VLS_22, new __VLS_22({
            size: (18),
            'aria-hidden': "true",
        }));
        var __VLS_24 = __VLS_23.apply(void 0, __spreadArray([{
                size: (18),
                'aria-hidden': "true",
            }], __VLS_functionalComponentArgsRest(__VLS_23), false));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign(__assign({ onClick: (__VLS_ctx.confirm) }, { class: "button primary proposal-confirm" }), { 'data-testid': "confirm-proposal", disabled: (__VLS_ctx.loading) }));
        var __VLS_26 = {}.Sparkles;
        /** @type {[typeof __VLS_components.Sparkles, ]} */ ;
        // @ts-ignore
        var __VLS_27 = __VLS_asFunctionalComponent(__VLS_26, new __VLS_26({
            size: (18),
            'aria-hidden': "true",
        }));
        var __VLS_28 = __VLS_27.apply(void 0, __spreadArray([{
                size: (18),
                'aria-hidden': "true",
            }], __VLS_functionalComponentArgsRest(__VLS_27), false));
        (__VLS_ctx.loading ? '正在确认…' : '确认方案，进入编辑');
    }
    __VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)(__assign({ class: "proposal-brief" }, { 'aria-labelledby': "proposal-summary-title" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "proposal-section-heading" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({
        id: "proposal-summary-title",
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)(__assign({ class: "agent-badge" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.dl, __VLS_intrinsicElements.dl)(__assign({ class: "proposal-summary-list" }));
    for (var _i = 0, _a = __VLS_getVForSourceType((__VLS_ctx.summaryEntries)); _i < _a.length; _i++) {
        var entry = _a[_i][0];
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
            key: ("".concat(entry.label, "-").concat(entry.value)),
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.dt, __VLS_intrinsicElements.dt)({});
        (entry.label);
        __VLS_asFunctionalElement(__VLS_intrinsicElements.dd, __VLS_intrinsicElements.dd)({});
        (entry.value);
    }
    if (__VLS_ctx.technicalEntries.length) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.details, __VLS_intrinsicElements.details)(__assign({ class: "proposal-technical" }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.summary, __VLS_intrinsicElements.summary)({});
        __VLS_asFunctionalElement(__VLS_intrinsicElements.dl, __VLS_intrinsicElements.dl)({});
        for (var _b = 0, _c = __VLS_getVForSourceType((__VLS_ctx.technicalEntries)); _b < _c.length; _b++) {
            var entry = _c[_b][0];
            __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({
                key: ("".concat(entry.label, "-").concat(entry.value)),
            });
            __VLS_asFunctionalElement(__VLS_intrinsicElements.dt, __VLS_intrinsicElements.dt)({});
            (entry.label);
            __VLS_asFunctionalElement(__VLS_intrinsicElements.dd, __VLS_intrinsicElements.dd)({});
            (entry.value);
        }
    }
    __VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)(__assign({ class: "proposal-flow" }, { 'aria-labelledby': "proposal-flow-title" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "proposal-section-heading" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({
        id: "proposal-flow-title",
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
    (__VLS_ctx.proposal.activityNodes.length);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.ol, __VLS_intrinsicElements.ol)(__assign({ class: "proposal-node-list" }));
    for (var _d = 0, _e = __VLS_getVForSourceType((__VLS_ctx.proposal.activityNodes)); _d < _e.length; _d++) {
        var _f = _e[_d], node = _f[0], index = _f[1];
        __VLS_asFunctionalElement(__VLS_intrinsicElements.li, __VLS_intrinsicElements.li)({
            key: (node.id),
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "proposal-node-index" }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
        (String(index + 1).padStart(2, '0'));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "proposal-node-copy" }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
        (__VLS_ctx.nodeTypeDisplayName(node.nodeType));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.h3, __VLS_intrinsicElements.h3)({});
        (node.title);
        if (node.components.length) {
            __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "proposal-component-tags" }));
            for (var _g = 0, _h = __VLS_getVForSourceType((node.components)); _g < _h.length; _g++) {
                var component = _h[_g][0];
                __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
                    key: (component.id),
                });
                (__VLS_ctx.componentDisplayName(component.name, component.componentKey));
            }
        }
    }
    __VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)(__assign({ class: "proposal-evidence-grid" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.details, __VLS_intrinsicElements.details)(__assign({ class: "proposal-evidence" }, { 'data-testid': "proposal-objectives" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.summary, __VLS_intrinsicElements.summary)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.ol, __VLS_intrinsicElements.ol)(__assign({ class: "objective-list" }));
    for (var _j = 0, _k = __VLS_getVForSourceType((__VLS_ctx.proposal.teachingObjectives)); _j < _k.length; _j++) {
        var _l = _k[_j], item = _l[0], index = _l[1];
        __VLS_asFunctionalElement(__VLS_intrinsicElements.li, __VLS_intrinsicElements.li)({
            key: (item),
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
        (index + 1);
        __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
        (item);
    }
    __VLS_asFunctionalElement(__VLS_intrinsicElements.details, __VLS_intrinsicElements.details)(__assign({ class: "proposal-evidence" }, { 'data-testid': "proposal-source" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.summary, __VLS_intrinsicElements.summary)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.ul, __VLS_intrinsicElements.ul)(__assign({ class: "source-section-list" }));
    for (var _m = 0, _o = __VLS_getVForSourceType((__VLS_ctx.proposal.sourceLessonSections)); _m < _o.length; _m++) {
        var item = _o[_m][0];
        __VLS_asFunctionalElement(__VLS_intrinsicElements.li, __VLS_intrinsicElements.li)({
            key: (item),
        });
        (item);
    }
    if (__VLS_ctx.proposal.components.length) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)(__assign({ class: "proposal-components" }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
        __VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "proposal-component-tags large" }));
        for (var _p = 0, _q = __VLS_getVForSourceType((__VLS_ctx.proposal.components)); _p < _q.length; _p++) {
            var component = _q[_p][0];
            __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
                key: (component.id),
            });
            (__VLS_ctx.componentDisplayName(component.name, component.componentKey));
        }
    }
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign(__assign({ onClick: function () {
        var _a = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            _a[_i] = arguments[_i];
        }
        var $event = _a[0];
        __VLS_ctx.previewOpen = true;
    } }, { class: "button primary" }), { type: "button" }));
if (__VLS_ctx.previewOpen && __VLS_ctx.proposal) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "preview-modal" }, { role: "dialog", 'aria-modal': "true", 'aria-label': "互动包预览" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "preview-modal-card" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "section-header compact" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "eyebrow" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign(__assign({ onClick: function () {
            var _a = [];
            for (var _i = 0; _i < arguments.length; _i++) {
                _a[_i] = arguments[_i];
            }
            var $event = _a[0];
            if (!(__VLS_ctx.previewOpen && __VLS_ctx.proposal))
                return;
            __VLS_ctx.previewOpen = false;
        } }, { class: "button" }), { type: "button" }));
    /** @type {[typeof InteractivePackagePreview, ]} */ ;
    // @ts-ignore
    var __VLS_30 = __VLS_asFunctionalComponent(InteractivePackagePreview_vue_1.default, new InteractivePackagePreview_vue_1.default({
        nodes: (__VLS_ctx.proposal.activityNodes),
        mode: "package",
    }));
    var __VLS_31 = __VLS_30.apply(void 0, __spreadArray([{
            nodes: (__VLS_ctx.proposal.activityNodes),
            mode: "package",
        }], __VLS_functionalComponentArgsRest(__VLS_30), false));
}
var __VLS_2;
/** @type {__VLS_StyleScopedClasses['page-heading']} */ ;
/** @type {__VLS_StyleScopedClasses['proposal-page-heading']} */ ;
/** @type {__VLS_StyleScopedClasses['eyebrow']} */ ;
/** @type {__VLS_StyleScopedClasses['proposal-alert']} */ ;
/** @type {__VLS_StyleScopedClasses['proposal-loading']} */ ;
/** @type {__VLS_StyleScopedClasses['proposal-layout']} */ ;
/** @type {__VLS_StyleScopedClasses['proposal-decision']} */ ;
/** @type {__VLS_StyleScopedClasses['proposal-title-block']} */ ;
/** @type {__VLS_StyleScopedClasses['proposal-title-row']} */ ;
/** @type {__VLS_StyleScopedClasses['proposal-mark']} */ ;
/** @type {__VLS_StyleScopedClasses['status-pill']} */ ;
/** @type {__VLS_StyleScopedClasses['proposal-confirm-area']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['primary']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['ghost']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['primary']} */ ;
/** @type {__VLS_StyleScopedClasses['proposal-confirm']} */ ;
/** @type {__VLS_StyleScopedClasses['proposal-brief']} */ ;
/** @type {__VLS_StyleScopedClasses['proposal-section-heading']} */ ;
/** @type {__VLS_StyleScopedClasses['agent-badge']} */ ;
/** @type {__VLS_StyleScopedClasses['proposal-summary-list']} */ ;
/** @type {__VLS_StyleScopedClasses['proposal-technical']} */ ;
/** @type {__VLS_StyleScopedClasses['proposal-flow']} */ ;
/** @type {__VLS_StyleScopedClasses['proposal-section-heading']} */ ;
/** @type {__VLS_StyleScopedClasses['proposal-node-list']} */ ;
/** @type {__VLS_StyleScopedClasses['proposal-node-index']} */ ;
/** @type {__VLS_StyleScopedClasses['proposal-node-copy']} */ ;
/** @type {__VLS_StyleScopedClasses['proposal-component-tags']} */ ;
/** @type {__VLS_StyleScopedClasses['proposal-evidence-grid']} */ ;
/** @type {__VLS_StyleScopedClasses['proposal-evidence']} */ ;
/** @type {__VLS_StyleScopedClasses['objective-list']} */ ;
/** @type {__VLS_StyleScopedClasses['proposal-evidence']} */ ;
/** @type {__VLS_StyleScopedClasses['source-section-list']} */ ;
/** @type {__VLS_StyleScopedClasses['proposal-components']} */ ;
/** @type {__VLS_StyleScopedClasses['proposal-component-tags']} */ ;
/** @type {__VLS_StyleScopedClasses['large']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['primary']} */ ;
/** @type {__VLS_StyleScopedClasses['preview-modal']} */ ;
/** @type {__VLS_StyleScopedClasses['preview-modal-card']} */ ;
/** @type {__VLS_StyleScopedClasses['section-header']} */ ;
/** @type {__VLS_StyleScopedClasses['compact']} */ ;
/** @type {__VLS_StyleScopedClasses['eyebrow']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
var __VLS_dollars;
var __VLS_self = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () {
        return {
            ArrowLeft: lucide_vue_next_1.ArrowLeft,
            CheckCircle2: lucide_vue_next_1.CheckCircle2,
            Pencil: lucide_vue_next_1.Pencil,
            Sparkles: lucide_vue_next_1.Sparkles,
            AppShell: AppShell_vue_1.default,
            LessonWorkspaceNav: LessonWorkspaceNav_vue_1.default,
            WorkflowStepper: WorkflowStepper_vue_1.default,
            InteractivePackagePreview: InteractivePackagePreview_vue_1.default,
            componentDisplayName: presentationLabels_1.componentDisplayName,
            nodeTypeDisplayName: presentationLabels_1.nodeTypeDisplayName,
            packageId: packageId,
            proposal: proposal,
            loading: loading,
            error: error,
            previewOpen: previewOpen,
            summaryEntries: summaryEntries,
            technicalEntries: technicalEntries,
            isConfirmed: isConfirmed,
            statusText: statusText,
            confirm: confirm,
            returnToSettings: returnToSettings,
        };
    },
});
exports.default = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () {
        return {};
    },
});
; /* PartiallyEnd: #4569/main.vue */
