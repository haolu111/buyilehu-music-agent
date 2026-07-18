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
var vue_router_1 = require("vue-router");
var AppShell_vue_1 = require("../components/AppShell.vue");
var WorkflowStepper_vue_1 = require("../components/WorkflowStepper.vue");
var packageApi_1 = require("../api/packageApi");
var classApi_1 = require("../api/classApi");
var route = (0, vue_router_1.useRoute)();
var router = (0, vue_router_1.useRouter)();
var packageId = Number(route.params.packageId);
var packageInfo = (0, vue_1.ref)(null);
var classes = (0, vue_1.ref)([]);
var versions = (0, vue_1.ref)([]);
var selectedClassIds = (0, vue_1.ref)([]);
var versionId = (0, vue_1.ref)('');
var courseTitle = (0, vue_1.ref)('');
var courseDescription = (0, vue_1.ref)('');
var scheduledStartAt = (0, vue_1.ref)('');
var reviewEnabled = (0, vue_1.ref)(false);
var loading = (0, vue_1.ref)(false);
var error = (0, vue_1.ref)('');
var message = (0, vue_1.ref)('选择班级和版本后即可创建课堂。创建后课堂默认未开始，需要到课堂管理中点击开始课堂。');
var canPublish = (0, vue_1.computed)(function () { return selectedClassIds.value.length > 0 && Boolean(versionId.value); });
function loadData() {
    return __awaiter(this, void 0, void 0, function () {
        var _a, pkg, mineClasses, versionList, defaultVersionId, exception_1;
        var _b;
        return __generator(this, function (_c) {
            switch (_c.label) {
                case 0:
                    loading.value = true;
                    error.value = '';
                    _c.label = 1;
                case 1:
                    _c.trys.push([1, 3, 4, 5]);
                    return [4 /*yield*/, Promise.all([
                            packageApi_1.packageApi.getPackage(packageId),
                            classApi_1.classApi.listClasses(),
                            packageApi_1.packageApi.listVersions(packageId),
                        ])];
                case 2:
                    _a = _c.sent(), pkg = _a[0], mineClasses = _a[1], versionList = _a[2];
                    packageInfo.value = pkg;
                    classes.value = mineClasses;
                    versions.value = versionList;
                    courseTitle.value = courseTitle.value || pkg.title;
                    if (selectedClassIds.value.length === 0 && mineClasses.length > 0) {
                        selectedClassIds.value = [mineClasses[0].id];
                    }
                    defaultVersionId = pkg.currentVersionId || ((_b = versionList[0]) === null || _b === void 0 ? void 0 : _b.id);
                    if (!versionId.value && defaultVersionId) {
                        versionId.value = String(defaultVersionId);
                    }
                    return [3 /*break*/, 5];
                case 3:
                    exception_1 = _c.sent();
                    error.value = exception_1 instanceof Error ? exception_1.message : '加载创建页面失败';
                    return [3 /*break*/, 5];
                case 4:
                    loading.value = false;
                    return [7 /*endfinally*/];
                case 5: return [2 /*return*/];
            }
        });
    });
}
function publish() {
    return __awaiter(this, void 0, void 0, function () {
        var exception_2;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    if (!canPublish.value) {
                        error.value = '请先选择班级和版本';
                        return [2 /*return*/];
                    }
                    loading.value = true;
                    error.value = '';
                    _a.label = 1;
                case 1:
                    _a.trys.push([1, 4, 5, 6]);
                    return [4 /*yield*/, packageApi_1.packageApi.publishPackage(packageId, {
                            classIds: selectedClassIds.value,
                            versionId: Number(versionId.value),
                            courseTitle: courseTitle.value,
                            courseDescription: courseDescription.value,
                            scheduledStartAt: scheduledStartAt.value || undefined,
                            startImmediately: false,
                            reviewEnabled: reviewEnabled.value,
                        })];
                case 2:
                    _a.sent();
                    message.value = '课堂已创建，当前未开始。请到课堂管理中点击开始课堂，系统会自动解锁第一个环节。';
                    return [4 /*yield*/, router.push('/classrooms')];
                case 3:
                    _a.sent();
                    return [3 /*break*/, 6];
                case 4:
                    exception_2 = _a.sent();
                    error.value = exception_2 instanceof Error ? exception_2.message : '创建课堂失败';
                    return [3 /*break*/, 6];
                case 5:
                    loading.value = false;
                    return [7 /*endfinally*/];
                case 6: return [2 /*return*/];
            }
        });
    });
}
function describeVersion(item) {
    return "\u7248\u672C ".concat(item.versionNo, " / \u7F16\u53F7 ").concat(item.id);
}
(0, vue_1.onMounted)(loadData);
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
    currentStage: "publish-classroom",
    packageId: (__VLS_ctx.packageId),
}));
var __VLS_5 = __VLS_4.apply(void 0, __spreadArray([{
        currentStage: "publish-classroom",
        packageId: (__VLS_ctx.packageId),
    }], __VLS_functionalComponentArgsRest(__VLS_4), false));
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "section-header" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "eyebrow" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.h1, __VLS_intrinsicElements.h1)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "muted" }));
var __VLS_7 = {}.RouterLink;
/** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
// @ts-ignore
var __VLS_8 = __VLS_asFunctionalComponent(__VLS_7, new __VLS_7(__assign({ class: "button" }, { to: ("/packages/".concat(__VLS_ctx.packageId)) })));
var __VLS_9 = __VLS_8.apply(void 0, __spreadArray([__assign({ class: "button" }, { to: ("/packages/".concat(__VLS_ctx.packageId)) })], __VLS_functionalComponentArgsRest(__VLS_8), false));
__VLS_10.slots.default;
var __VLS_10;
if (__VLS_ctx.error) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "error" }));
    (__VLS_ctx.error);
}
if (__VLS_ctx.packageInfo) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)(__assign({ class: "card stack" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "list-line" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
    (__VLS_ctx.packageInfo.title);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "muted" }));
    (__VLS_ctx.packageInfo.description || '暂无简介');
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)(__assign({ class: "tag" }));
    (__VLS_ctx.packageInfo.currentVersionId || '-');
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "muted" }));
    (__VLS_ctx.message);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "grid two" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
        placeholder: "例如：三拍子律动体验课",
    });
    (__VLS_ctx.courseTitle);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
        type: "datetime-local",
    });
    (__VLS_ctx.scheduledStartAt);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.textarea, __VLS_intrinsicElements.textarea)({
        value: (__VLS_ctx.courseDescription),
        rows: "3",
        placeholder: "给学生和教师看的课堂说明",
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.select, __VLS_intrinsicElements.select)({
        value: (__VLS_ctx.versionId),
    });
    __VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
        value: "",
    });
    for (var _i = 0, _a = __VLS_getVForSourceType((__VLS_ctx.versions)); _i < _a.length; _i++) {
        var item = _a[_i][0];
        __VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
            key: (item.id),
            value: (String(item.id)),
        });
        (__VLS_ctx.describeVersion(item));
    }
    __VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)(__assign({ class: "stack" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.h3, __VLS_intrinsicElements.h3)({});
    for (var _b = 0, _c = __VLS_getVForSourceType((__VLS_ctx.classes)); _b < _c.length; _b++) {
        var item = _c[_b][0];
        __VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)(__assign({ key: (item.id) }, { class: "inline-control" }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
            type: "checkbox",
            value: (item.id),
        });
        (__VLS_ctx.selectedClassIds);
        (item.id);
        (item.className);
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)(__assign({ class: "muted" }));
        (item.description);
    }
    __VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)(__assign({ class: "inline-control" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.input)({
        type: "checkbox",
    });
    (__VLS_ctx.reviewEnabled);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "button-row" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign(__assign({ onClick: (__VLS_ctx.publish) }, { class: "primary" }), { disabled: (__VLS_ctx.loading || !__VLS_ctx.canPublish) }));
    (__VLS_ctx.loading ? '创建中...' : '创建课堂');
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign(__assign({ onClick: (__VLS_ctx.loadData) }, { class: "button" }), { type: "button" }));
}
var __VLS_2;
/** @type {__VLS_StyleScopedClasses['section-header']} */ ;
/** @type {__VLS_StyleScopedClasses['eyebrow']} */ ;
/** @type {__VLS_StyleScopedClasses['muted']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['error']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['stack']} */ ;
/** @type {__VLS_StyleScopedClasses['list-line']} */ ;
/** @type {__VLS_StyleScopedClasses['muted']} */ ;
/** @type {__VLS_StyleScopedClasses['tag']} */ ;
/** @type {__VLS_StyleScopedClasses['muted']} */ ;
/** @type {__VLS_StyleScopedClasses['grid']} */ ;
/** @type {__VLS_StyleScopedClasses['two']} */ ;
/** @type {__VLS_StyleScopedClasses['stack']} */ ;
/** @type {__VLS_StyleScopedClasses['inline-control']} */ ;
/** @type {__VLS_StyleScopedClasses['muted']} */ ;
/** @type {__VLS_StyleScopedClasses['inline-control']} */ ;
/** @type {__VLS_StyleScopedClasses['button-row']} */ ;
/** @type {__VLS_StyleScopedClasses['primary']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
var __VLS_dollars;
var __VLS_self = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () {
        return {
            AppShell: AppShell_vue_1.default,
            WorkflowStepper: WorkflowStepper_vue_1.default,
            packageId: packageId,
            packageInfo: packageInfo,
            classes: classes,
            versions: versions,
            selectedClassIds: selectedClassIds,
            versionId: versionId,
            courseTitle: courseTitle,
            courseDescription: courseDescription,
            scheduledStartAt: scheduledStartAt,
            reviewEnabled: reviewEnabled,
            loading: loading,
            error: error,
            message: message,
            canPublish: canPublish,
            loadData: loadData,
            publish: publish,
            describeVersion: describeVersion,
        };
    },
});
exports.default = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () {
        return {};
    },
});
; /* PartiallyEnd: #4569/main.vue */
