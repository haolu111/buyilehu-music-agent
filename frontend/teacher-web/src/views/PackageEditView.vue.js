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
var lucide_vue_next_1 = require("lucide-vue-next");
var vue_router_1 = require("vue-router");
var AppShell_vue_1 = require("../components/AppShell.vue");
var WorkflowStepper_vue_1 = require("../components/WorkflowStepper.vue");
var VersionHistoryPanel_vue_1 = require("../components/VersionHistoryPanel.vue");
var ActivityNodeEditView_vue_1 = require("./ActivityNodeEditView.vue");
var InteractivePackagePreview_vue_1 = require("../components/InteractivePackagePreview.vue");
var packageApi_1 = require("../api/packageApi");
var presentationLabels_1 = require("../utils/presentationLabels");
var route = (0, vue_router_1.useRoute)();
var packageId = Number(route.params.packageId);
var proposal = (0, vue_1.ref)(null);
var versions = (0, vue_1.ref)([]);
var selectedNodeId = (0, vue_1.ref)(null);
var loading = (0, vue_1.ref)(false);
var message = (0, vue_1.ref)('');
var error = (0, vue_1.ref)('');
var draft = (0, vue_1.ref)({});
var nodeFeedback = (0, vue_1.ref)('');
var selectedNode = (0, vue_1.computed)(function () { var _a; return ((_a = proposal.value) === null || _a === void 0 ? void 0 : _a.activityNodes.find(function (node) { return node.id === selectedNodeId.value; })) || null; });
function load() {
    return __awaiter(this, void 0, void 0, function () {
        var _a, _b, err_1;
        return __generator(this, function (_c) {
            switch (_c.label) {
                case 0:
                    loading.value = true;
                    error.value = '';
                    _c.label = 1;
                case 1:
                    _c.trys.push([1, 4, 5, 6]);
                    _a = proposal;
                    return [4 /*yield*/, packageApi_1.packageApi.getProposal(packageId)];
                case 2:
                    _a.value = _c.sent();
                    _b = versions;
                    return [4 /*yield*/, packageApi_1.packageApi.listVersions(packageId)];
                case 3:
                    _b.value = _c.sent();
                    if (!selectedNodeId.value && proposal.value.activityNodes.length > 0) {
                        selectedNodeId.value = proposal.value.activityNodes[0].id;
                    }
                    return [3 /*break*/, 6];
                case 4:
                    err_1 = _c.sent();
                    error.value = err_1 instanceof Error ? err_1.message : '加载互动包失败';
                    return [3 /*break*/, 6];
                case 5:
                    loading.value = false;
                    return [7 /*endfinally*/];
                case 6: return [2 /*return*/];
            }
        });
    });
}
function saveNode(payload) {
    return __awaiter(this, void 0, void 0, function () {
        var baseVersionId, result, err_2;
        var _a, _b;
        return __generator(this, function (_c) {
            switch (_c.label) {
                case 0:
                    baseVersionId = (_b = (_a = proposal.value) === null || _a === void 0 ? void 0 : _a.packageInfo) === null || _b === void 0 ? void 0 : _b.currentVersionId;
                    if (!selectedNodeId.value || !baseVersionId)
                        return [2 /*return*/];
                    loading.value = true;
                    message.value = '';
                    error.value = '';
                    _c.label = 1;
                case 1:
                    _c.trys.push([1, 4, 5, 6]);
                    return [4 /*yield*/, packageApi_1.packageApi.updateNodeConfig(packageId, selectedNodeId.value, baseVersionId, payload)];
                case 2:
                    result = _c.sent();
                    message.value = "\u5DF2\u751F\u6210 v".concat(result.versionNo);
                    return [4 /*yield*/, load()];
                case 3:
                    _c.sent();
                    return [3 /*break*/, 6];
                case 4:
                    err_2 = _c.sent();
                    error.value = err_2 instanceof Error ? err_2.message : '保存失败';
                    return [3 /*break*/, 6];
                case 5:
                    loading.value = false;
                    return [7 /*endfinally*/];
                case 6: return [2 /*return*/];
            }
        });
    });
}
function reviseSelectedNode() {
    return __awaiter(this, void 0, void 0, function () {
        var baseVersionId, feedback, result, err_3;
        var _a, _b;
        return __generator(this, function (_c) {
            switch (_c.label) {
                case 0:
                    baseVersionId = (_b = (_a = proposal.value) === null || _a === void 0 ? void 0 : _a.packageInfo) === null || _b === void 0 ? void 0 : _b.currentVersionId;
                    feedback = nodeFeedback.value.trim();
                    if (!selectedNodeId.value || !baseVersionId || !feedback)
                        return [2 /*return*/];
                    loading.value = true;
                    message.value = '';
                    error.value = '';
                    _c.label = 1;
                case 1:
                    _c.trys.push([1, 4, 5, 6]);
                    return [4 /*yield*/, packageApi_1.packageApi.reviseNodeWithAgent(packageId, selectedNodeId.value, baseVersionId, feedback)];
                case 2:
                    result = _c.sent();
                    message.value = "Agent \u5DF2\u53EA\u4FEE\u6539\u5F53\u524D\u8282\u70B9\uFF0C\u5E76\u751F\u6210 v".concat(result.versionNo);
                    nodeFeedback.value = '';
                    return [4 /*yield*/, load()];
                case 3:
                    _c.sent();
                    return [3 /*break*/, 6];
                case 4:
                    err_3 = _c.sent();
                    error.value = err_3 instanceof Error ? err_3.message : 'Agent 修改节点失败';
                    return [3 /*break*/, 6];
                case 5:
                    loading.value = false;
                    return [7 /*endfinally*/];
                case 6: return [2 /*return*/];
            }
        });
    });
}
(0, vue_1.onMounted)(load);
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
    currentStage: "edit-package",
    packageId: (__VLS_ctx.packageId),
}));
var __VLS_5 = __VLS_4.apply(void 0, __spreadArray([{
        currentStage: "edit-package",
        packageId: (__VLS_ctx.packageId),
    }], __VLS_functionalComponentArgsRest(__VLS_4), false));
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "section-header" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "eyebrow" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.h1, __VLS_intrinsicElements.h1)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "lead" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "button-row" }));
var __VLS_7 = {}.RouterLink;
/** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
// @ts-ignore
var __VLS_8 = __VLS_asFunctionalComponent(__VLS_7, new __VLS_7(__assign({ class: "button" }, { to: ("/packages/".concat(__VLS_ctx.packageId)) })));
var __VLS_9 = __VLS_8.apply(void 0, __spreadArray([__assign({ class: "button" }, { to: ("/packages/".concat(__VLS_ctx.packageId)) })], __VLS_functionalComponentArgsRest(__VLS_8), false));
__VLS_10.slots.default;
var __VLS_10;
var __VLS_11 = {}.RouterLink;
/** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
// @ts-ignore
var __VLS_12 = __VLS_asFunctionalComponent(__VLS_11, new __VLS_11(__assign({ class: "button primary" }, { dataTestid: "publish-classroom-next", to: ("/packages/".concat(__VLS_ctx.packageId, "/publish")) })));
var __VLS_13 = __VLS_12.apply(void 0, __spreadArray([__assign({ class: "button primary" }, { dataTestid: "publish-classroom-next", to: ("/packages/".concat(__VLS_ctx.packageId, "/publish")) })], __VLS_functionalComponentArgsRest(__VLS_12), false));
__VLS_14.slots.default;
var __VLS_15 = {}.Send;
/** @type {[typeof __VLS_components.Send, ]} */ ;
// @ts-ignore
var __VLS_16 = __VLS_asFunctionalComponent(__VLS_15, new __VLS_15({
    size: (18),
    'aria-hidden': "true",
}));
var __VLS_17 = __VLS_16.apply(void 0, __spreadArray([{
        size: (18),
        'aria-hidden': "true",
    }], __VLS_functionalComponentArgsRest(__VLS_16), false));
var __VLS_14;
if (__VLS_ctx.message) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "tag" }));
    (__VLS_ctx.message);
}
if (__VLS_ctx.error) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "error" }));
    (__VLS_ctx.error);
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)(__assign({ class: "edit-layout" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "card stack" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
var _loop_1 = function (node) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign(__assign(__assign({ onClick: function () {
            var _a = [];
            for (var _i = 0; _i < arguments.length; _i++) {
                _a[_i] = arguments[_i];
            }
            var $event = _a[0];
            __VLS_ctx.selectedNodeId = node.id;
        } }, { key: (node.id), type: "button" }), { class: "node-select" }), { class: ({ active: node.id === __VLS_ctx.selectedNodeId }) }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
    (node.sortOrder);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
    (node.title);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.small, __VLS_intrinsicElements.small)({});
    (__VLS_ctx.nodeTypeDisplayName(node.nodeType));
};
for (var _i = 0, _b = __VLS_getVForSourceType((((_a = __VLS_ctx.proposal) === null || _a === void 0 ? void 0 : _a.activityNodes) || [])); _i < _b.length; _i++) {
    var node = _b[_i][0];
    _loop_1(node);
}
/** @type {[typeof ActivityNodeEditView, ]} */ ;
// @ts-ignore
var __VLS_19 = __VLS_asFunctionalComponent(ActivityNodeEditView_vue_1.default, new ActivityNodeEditView_vue_1.default(__assign(__assign({ 'onSave': {} }, { 'onChange': {} }), { proposal: (__VLS_ctx.proposal), selectedNodeId: (__VLS_ctx.selectedNodeId) })));
var __VLS_20 = __VLS_19.apply(void 0, __spreadArray([__assign(__assign({ 'onSave': {} }, { 'onChange': {} }), { proposal: (__VLS_ctx.proposal), selectedNodeId: (__VLS_ctx.selectedNodeId) })], __VLS_functionalComponentArgsRest(__VLS_19), false));
var __VLS_22;
var __VLS_23;
var __VLS_24;
var __VLS_25 = {
    onSave: (__VLS_ctx.saveNode)
};
var __VLS_26 = {
    onChange: function () {
        var _a = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            _a[_i] = arguments[_i];
        }
        var $event = _a[0];
        __VLS_ctx.draft = $event;
    }
};
var __VLS_21;
/** @type {[typeof VersionHistoryPanel, ]} */ ;
// @ts-ignore
var __VLS_27 = __VLS_asFunctionalComponent(VersionHistoryPanel_vue_1.default, new VersionHistoryPanel_vue_1.default({
    versions: (__VLS_ctx.versions),
}));
var __VLS_28 = __VLS_27.apply(void 0, __spreadArray([{
        versions: (__VLS_ctx.versions),
    }], __VLS_functionalComponentArgsRest(__VLS_27), false));
if (__VLS_ctx.selectedNode) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)(__assign({ class: "card stack" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
    (__VLS_ctx.selectedNode.title);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "muted" }));
    (__VLS_ctx.selectedNode.components.length);
    for (var _c = 0, _d = __VLS_getVForSourceType((__VLS_ctx.selectedNode.components)); _c < _d.length; _c++) {
        var component = _d[_c][0];
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)(__assign({ key: (component.id) }, { class: "tag" }));
        (__VLS_ctx.componentDisplayName(component.name, component.componentKey));
    }
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "agent-node-revision" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "eyebrow" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h3, __VLS_intrinsicElements.h3)({});
    (__VLS_ctx.selectedNode.title);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "muted" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.textarea)({
        value: (__VLS_ctx.nodeFeedback),
        'data-testid': "node-agent-feedback",
        maxlength: "2000",
        rows: "4",
        placeholder: "例如：这个活动对三年级偏难，请保留活动目标，把节奏卡数量降到 4，并增加一次教师示范提示。",
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "button-row" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.small, __VLS_intrinsicElements.small)(__assign({ class: "muted" }));
    (__VLS_ctx.nodeFeedback.length);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign(__assign({ onClick: (__VLS_ctx.reviseSelectedNode) }, { class: "button primary" }), { 'data-testid': "revise-node-with-agent", type: "button", disabled: (__VLS_ctx.loading || !__VLS_ctx.nodeFeedback.trim()) }));
    (__VLS_ctx.loading ? 'Agent 修改中…' : '提交建议并修改当前节点');
}
if (__VLS_ctx.selectedNode && __VLS_ctx.proposal) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)(__assign({ class: "card stack live-preview-panel" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "eyebrow" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "muted" }));
    /** @type {[typeof InteractivePackagePreview, ]} */ ;
    // @ts-ignore
    var __VLS_30 = __VLS_asFunctionalComponent(InteractivePackagePreview_vue_1.default, new InteractivePackagePreview_vue_1.default({
        nodes: (__VLS_ctx.proposal.activityNodes),
        selectedNodeId: (__VLS_ctx.selectedNodeId),
        draft: (__VLS_ctx.draft),
        mode: "single",
    }));
    var __VLS_31 = __VLS_30.apply(void 0, __spreadArray([{
            nodes: (__VLS_ctx.proposal.activityNodes),
            selectedNodeId: (__VLS_ctx.selectedNodeId),
            draft: (__VLS_ctx.draft),
            mode: "single",
        }], __VLS_functionalComponentArgsRest(__VLS_30), false));
}
var __VLS_2;
/** @type {__VLS_StyleScopedClasses['section-header']} */ ;
/** @type {__VLS_StyleScopedClasses['eyebrow']} */ ;
/** @type {__VLS_StyleScopedClasses['lead']} */ ;
/** @type {__VLS_StyleScopedClasses['button-row']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['primary']} */ ;
/** @type {__VLS_StyleScopedClasses['tag']} */ ;
/** @type {__VLS_StyleScopedClasses['error']} */ ;
/** @type {__VLS_StyleScopedClasses['edit-layout']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['stack']} */ ;
/** @type {__VLS_StyleScopedClasses['node-select']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['stack']} */ ;
/** @type {__VLS_StyleScopedClasses['muted']} */ ;
/** @type {__VLS_StyleScopedClasses['tag']} */ ;
/** @type {__VLS_StyleScopedClasses['agent-node-revision']} */ ;
/** @type {__VLS_StyleScopedClasses['eyebrow']} */ ;
/** @type {__VLS_StyleScopedClasses['muted']} */ ;
/** @type {__VLS_StyleScopedClasses['button-row']} */ ;
/** @type {__VLS_StyleScopedClasses['muted']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['primary']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['stack']} */ ;
/** @type {__VLS_StyleScopedClasses['live-preview-panel']} */ ;
/** @type {__VLS_StyleScopedClasses['eyebrow']} */ ;
/** @type {__VLS_StyleScopedClasses['muted']} */ ;
var __VLS_dollars;
var __VLS_self = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () {
        return {
            Send: lucide_vue_next_1.Send,
            AppShell: AppShell_vue_1.default,
            WorkflowStepper: WorkflowStepper_vue_1.default,
            VersionHistoryPanel: VersionHistoryPanel_vue_1.default,
            ActivityNodeEditView: ActivityNodeEditView_vue_1.default,
            InteractivePackagePreview: InteractivePackagePreview_vue_1.default,
            componentDisplayName: presentationLabels_1.componentDisplayName,
            nodeTypeDisplayName: presentationLabels_1.nodeTypeDisplayName,
            packageId: packageId,
            proposal: proposal,
            versions: versions,
            selectedNodeId: selectedNodeId,
            loading: loading,
            message: message,
            error: error,
            draft: draft,
            nodeFeedback: nodeFeedback,
            selectedNode: selectedNode,
            saveNode: saveNode,
            reviseSelectedNode: reviseSelectedNode,
        };
    },
});
exports.default = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () {
        return {};
    },
});
; /* PartiallyEnd: #4569/main.vue */
