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
var lucide_vue_next_1 = require("lucide-vue-next");
var AppShell_vue_1 = require("../components/AppShell.vue");
var WorkflowStepper_vue_1 = require("../components/WorkflowStepper.vue");
var lessonPlanApi_1 = require("../api/lessonPlanApi");
var router = (0, vue_router_1.useRouter)();
var route = (0, vue_router_1.useRoute)();
var items = (0, vue_1.ref)([]);
var nativeFileInput = (0, vue_1.ref)(null);
var loading = (0, vue_1.ref)(false);
var error = (0, vue_1.ref)('');
var dragging = (0, vue_1.ref)(false);
var acceptedExtensions = ['txt', 'docx', 'pdf'];
var isRetryUpload = (0, vue_1.computed)(function () { return Boolean(route.query.retryLessonPlanId); });
var isBatch = (0, vue_1.computed)(function () { return items.value.length > 1; });
var successCount = (0, vue_1.computed)(function () { return items.value.filter(function (item) { return item.status === 'success'; }).length; });
var failedCount = (0, vue_1.computed)(function () { return items.value.filter(function (item) { return item.status === 'failed'; }).length; });
var totalSize = (0, vue_1.computed)(function () {
    var bytes = items.value.reduce(function (sum, item) { return sum + item.file.size; }, 0);
    return "".concat((bytes / 1024 / 1024).toFixed(1), " MB");
});
function validateFile(file) {
    var _a;
    var extension = (_a = file.name.split('.').pop()) === null || _a === void 0 ? void 0 : _a.toLowerCase();
    if (!extension || !acceptedExtensions.includes(extension))
        return '请选择 DOCX、PDF 或 TXT 格式的教案';
    if (file.size > 20 * 1024 * 1024)
        return '文件不能超过 20MB';
    return '';
}
function addFiles(files) {
    var _a;
    if (!(files === null || files === void 0 ? void 0 : files.length))
        return;
    error.value = '';
    var additions = [];
    var errors = [];
    Array.from(files).forEach(function (file) {
        var validation = validateFile(file);
        if (validation) {
            errors.push("".concat(file.name, "\uFF1A").concat(validation));
            return;
        }
        var key = "".concat(file.name, "-").concat(file.size, "-").concat(file.lastModified);
        if (items.value.some(function (item) { return item.key === key; }) || additions.some(function (item) { return item.key === key; }))
            return;
        additions.push({
            key: key,
            file: file,
            title: file.name.replace(/\.[^.]+$/, ''),
            status: 'pending',
        });
    });
    (_a = items.value).push.apply(_a, additions);
    if (errors.length)
        error.value = errors.join('；');
    if (nativeFileInput.value)
        nativeFileInput.value.value = '';
}
function removeItem(key) {
    if (loading.value)
        return;
    items.value = items.value.filter(function (item) { return item.key !== key; });
    error.value = '';
}
function clearFiles() {
    if (loading.value)
        return;
    items.value = [];
    error.value = '';
    if (nativeFileInput.value)
        nativeFileInput.value.value = '';
}
function onFileChange(event) {
    addFiles(event.target.files || undefined);
}
function onDrop(event) {
    var _a;
    dragging.value = false;
    addFiles((_a = event.dataTransfer) === null || _a === void 0 ? void 0 : _a.files);
}
function upload() {
    return __awaiter(this, void 0, void 0, function () {
        var _i, _a, item, plan, e_1;
        return __generator(this, function (_b) {
            switch (_b.label) {
                case 0:
                    if (!items.value.length) {
                        error.value = '请先选择教案文件';
                        return [2 /*return*/];
                    }
                    loading.value = true;
                    error.value = '';
                    _i = 0, _a = items.value;
                    _b.label = 1;
                case 1:
                    if (!(_i < _a.length)) return [3 /*break*/, 6];
                    item = _a[_i];
                    if (item.status === 'success')
                        return [3 /*break*/, 5];
                    item.status = 'uploading';
                    item.error = '';
                    _b.label = 2;
                case 2:
                    _b.trys.push([2, 4, , 5]);
                    return [4 /*yield*/, lessonPlanApi_1.lessonPlanApi.upload(item.file, item.title)];
                case 3:
                    plan = _b.sent();
                    item.status = 'success';
                    item.lessonPlanId = plan.id;
                    return [3 /*break*/, 5];
                case 4:
                    e_1 = _b.sent();
                    item.status = 'failed';
                    item.error = e_1 instanceof Error ? e_1.message : '解析教案失败';
                    return [3 /*break*/, 5];
                case 5:
                    _i++;
                    return [3 /*break*/, 1];
                case 6:
                    loading.value = false;
                    if (!(items.value.length === 1 && successCount.value === 1)) return [3 /*break*/, 8];
                    return [4 /*yield*/, router.push("/lesson-plans/".concat(items.value[0].lessonPlanId, "/parse-result"))];
                case 7:
                    _b.sent();
                    _b.label = 8;
                case 8: return [2 /*return*/];
            }
        });
    });
}
function statusText(status) {
    return { pending: '等待上传', uploading: '正在解析', success: '解析成功', failed: '解析失败' }[status];
}
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
    currentStage: "upload-lesson",
}));
var __VLS_5 = __VLS_4.apply(void 0, __spreadArray([{
        currentStage: "upload-lesson",
    }], __VLS_functionalComponentArgsRest(__VLS_4), false));
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "page-heading compact" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "eyebrow" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.h1, __VLS_intrinsicElements.h1)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "upload-layout" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)(__assign({ class: "card upload-card" }));
if (__VLS_ctx.isRetryUpload) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "retry-upload-context" }));
    var __VLS_7 = {}.Sparkles;
    /** @type {[typeof __VLS_components.Sparkles, ]} */ ;
    // @ts-ignore
    var __VLS_8 = __VLS_asFunctionalComponent(__VLS_7, new __VLS_7({
        size: (16),
        'aria-hidden': "true",
    }));
    var __VLS_9 = __VLS_8.apply(void 0, __spreadArray([{
            size: (16),
            'aria-hidden': "true",
        }], __VLS_functionalComponentArgsRest(__VLS_8), false));
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)(__assign(__assign(__assign(__assign({ onDragover: function () {
        var _a = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            _a[_i] = arguments[_i];
        }
        var $event = _a[0];
        __VLS_ctx.dragging = true;
    } }, { onDragleave: function () {
        var _a = [];
        for (var _i = 0; _i < arguments.length; _i++) {
            _a[_i] = arguments[_i];
        }
        var $event = _a[0];
        __VLS_ctx.dragging = false;
    } }), { onDrop: (__VLS_ctx.onDrop) }), { class: "upload-zone" }), { class: ({ dragging: __VLS_ctx.dragging, selected: __VLS_ctx.items.length }) }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.input, __VLS_intrinsicElements.input)(__assign({ onChange: (__VLS_ctx.onFileChange) }, { ref: "nativeFileInput", type: "file", accept: ".txt,.docx,.pdf", multiple: true }));
/** @type {typeof __VLS_ctx.nativeFileInput} */ ;
if (__VLS_ctx.items.length) {
    var __VLS_11 = {}.FileCheck2;
    /** @type {[typeof __VLS_components.FileCheck2, ]} */ ;
    // @ts-ignore
    var __VLS_12 = __VLS_asFunctionalComponent(__VLS_11, new __VLS_11(__assign({ class: "upload-icon" }, { size: (27), 'aria-hidden': "true" })));
    var __VLS_13 = __VLS_12.apply(void 0, __spreadArray([__assign({ class: "upload-icon" }, { size: (27), 'aria-hidden': "true" })], __VLS_functionalComponentArgsRest(__VLS_12), false));
}
else {
    var __VLS_15 = {}.FileUp;
    /** @type {[typeof __VLS_components.FileUp, ]} */ ;
    // @ts-ignore
    var __VLS_16 = __VLS_asFunctionalComponent(__VLS_15, new __VLS_15(__assign({ class: "upload-icon" }, { size: (27), 'aria-hidden': "true" })));
    var __VLS_17 = __VLS_16.apply(void 0, __spreadArray([__assign({ class: "upload-icon" }, { size: (27), 'aria-hidden': "true" })], __VLS_functionalComponentArgsRest(__VLS_16), false));
}
if (!__VLS_ctx.items.length) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
    __VLS_asFunctionalElement(__VLS_intrinsicElements.small, __VLS_intrinsicElements.small)({});
}
else {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
    (__VLS_ctx.items.length);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.small, __VLS_intrinsicElements.small)({});
    (__VLS_ctx.totalSize);
}
if (__VLS_ctx.items.length) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "upload-file-list" }));
    var _loop_1 = function (item) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.article, __VLS_intrinsicElements.article)(__assign(__assign({ key: (item.key) }, { class: "upload-file-item" }), { 'data-status': (item.status) }));
        var __VLS_19 = {}.FileCheck2;
        /** @type {[typeof __VLS_components.FileCheck2, ]} */ ;
        // @ts-ignore
        var __VLS_20 = __VLS_asFunctionalComponent(__VLS_19, new __VLS_19({
            size: (20),
            'aria-hidden': "true",
        }));
        var __VLS_21 = __VLS_20.apply(void 0, __spreadArray([{
                size: (20),
                'aria-hidden': "true",
            }], __VLS_functionalComponentArgsRest(__VLS_20), false));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "upload-file-main" }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
        (item.file.name);
        __VLS_asFunctionalElement(__VLS_intrinsicElements.input, __VLS_intrinsicElements.input)({
            name: (__VLS_ctx.items.length === 1 ? 'lesson-title' : undefined),
            'aria-label': "教案标题",
            disabled: (__VLS_ctx.loading),
            placeholder: "教案标题",
        });
        (item.title);
        if (item.error) {
            __VLS_asFunctionalElement(__VLS_intrinsicElements.small, __VLS_intrinsicElements.small)(__assign({ class: "error" }));
            (item.error);
        }
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)(__assign({ class: "upload-file-status" }));
        if (item.status === 'success') {
            var __VLS_23 = {}.CheckCircle2;
            /** @type {[typeof __VLS_components.CheckCircle2, ]} */ ;
            // @ts-ignore
            var __VLS_24 = __VLS_asFunctionalComponent(__VLS_23, new __VLS_23({
                size: (17),
            }));
            var __VLS_25 = __VLS_24.apply(void 0, __spreadArray([{
                    size: (17),
                }], __VLS_functionalComponentArgsRest(__VLS_24), false));
        }
        else if (item.status === 'failed') {
            var __VLS_27 = {}.XCircle;
            /** @type {[typeof __VLS_components.XCircle, ]} */ ;
            // @ts-ignore
            var __VLS_28 = __VLS_asFunctionalComponent(__VLS_27, new __VLS_27({
                size: (17),
            }));
            var __VLS_29 = __VLS_28.apply(void 0, __spreadArray([{
                    size: (17),
                }], __VLS_functionalComponentArgsRest(__VLS_28), false));
        }
        (__VLS_ctx.statusText(item.status));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign(__assign({ onClick: function () {
                var _a = [];
                for (var _i = 0; _i < arguments.length; _i++) {
                    _a[_i] = arguments[_i];
                }
                var $event = _a[0];
                if (!(__VLS_ctx.items.length))
                    return;
                __VLS_ctx.removeItem(item.key);
            } }, { class: "icon-button" }), { type: "button", 'aria-label': "移除文件", disabled: (__VLS_ctx.loading) }));
        var __VLS_31 = {}.X;
        /** @type {[typeof __VLS_components.X, ]} */ ;
        // @ts-ignore
        var __VLS_32 = __VLS_asFunctionalComponent(__VLS_31, new __VLS_31({
            size: (17),
        }));
        var __VLS_33 = __VLS_32.apply(void 0, __spreadArray([{
                size: (17),
            }], __VLS_functionalComponentArgsRest(__VLS_32), false));
    };
    for (var _i = 0, _a = __VLS_getVForSourceType((__VLS_ctx.items)); _i < _a.length; _i++) {
        var item = _a[_i][0];
        _loop_1(item);
    }
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "button-row upload-actions" }));
if (__VLS_ctx.items.length) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign(__assign({ onClick: (__VLS_ctx.clearFiles) }, { class: "button ghost" }), { type: "button", disabled: (__VLS_ctx.loading) }));
    var __VLS_35 = {}.X;
    /** @type {[typeof __VLS_components.X, ]} */ ;
    // @ts-ignore
    var __VLS_36 = __VLS_asFunctionalComponent(__VLS_35, new __VLS_35({
        size: (17),
        'aria-hidden': "true",
    }));
    var __VLS_37 = __VLS_36.apply(void 0, __spreadArray([{
            size: (17),
            'aria-hidden': "true",
        }], __VLS_functionalComponentArgsRest(__VLS_36), false));
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign(__assign({ onClick: (__VLS_ctx.upload) }, { class: "button primary" }), { type: "button", 'data-testid': "lesson-upload-primary", disabled: (__VLS_ctx.loading || !__VLS_ctx.items.length) }));
var __VLS_39 = {}.Sparkles;
/** @type {[typeof __VLS_components.Sparkles, ]} */ ;
// @ts-ignore
var __VLS_40 = __VLS_asFunctionalComponent(__VLS_39, new __VLS_39({
    size: (17),
    'aria-hidden': "true",
}));
var __VLS_41 = __VLS_40.apply(void 0, __spreadArray([{
        size: (17),
        'aria-hidden': "true",
    }], __VLS_functionalComponentArgsRest(__VLS_40), false));
(__VLS_ctx.loading ? "\u6B63\u5728\u89E3\u6790 ".concat(__VLS_ctx.successCount + __VLS_ctx.failedCount + 1, "/").concat(__VLS_ctx.items.length, "\u2026") : (__VLS_ctx.isBatch ? "\u6279\u91CF\u89E3\u6790 ".concat(__VLS_ctx.items.length, " \u4EFD\u6559\u6848") : '解析教案'));
if (__VLS_ctx.isBatch && __VLS_ctx.successCount) {
    var __VLS_43 = {}.RouterLink;
    /** @type {[typeof __VLS_components.RouterLink, typeof __VLS_components.RouterLink, ]} */ ;
    // @ts-ignore
    var __VLS_44 = __VLS_asFunctionalComponent(__VLS_43, new __VLS_43(__assign({ class: "button" }, { to: "/lesson-plans/history" })));
    var __VLS_45 = __VLS_44.apply(void 0, __spreadArray([__assign({ class: "button" }, { to: "/lesson-plans/history" })], __VLS_functionalComponentArgsRest(__VLS_44), false));
    __VLS_46.slots.default;
    (__VLS_ctx.successCount);
    var __VLS_46;
}
if (__VLS_ctx.error) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "error" }));
    (__VLS_ctx.error);
}
if (__VLS_ctx.isBatch && !__VLS_ctx.loading && (__VLS_ctx.successCount || __VLS_ctx.failedCount)) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "upload-summary" }));
    (__VLS_ctx.successCount);
    (__VLS_ctx.failedCount);
    if (__VLS_ctx.failedCount) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
    }
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.aside, __VLS_intrinsicElements.aside)(__assign({ class: "card upload-note" }));
var __VLS_47 = {}.Sparkles;
/** @type {[typeof __VLS_components.Sparkles, ]} */ ;
// @ts-ignore
var __VLS_48 = __VLS_asFunctionalComponent(__VLS_47, new __VLS_47({
    size: (23),
    'aria-hidden': "true",
}));
var __VLS_49 = __VLS_48.apply(void 0, __spreadArray([{
        size: (23),
        'aria-hidden': "true",
    }], __VLS_functionalComponentArgsRest(__VLS_48), false));
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
var __VLS_2;
/** @type {__VLS_StyleScopedClasses['page-heading']} */ ;
/** @type {__VLS_StyleScopedClasses['compact']} */ ;
/** @type {__VLS_StyleScopedClasses['eyebrow']} */ ;
/** @type {__VLS_StyleScopedClasses['upload-layout']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['upload-card']} */ ;
/** @type {__VLS_StyleScopedClasses['retry-upload-context']} */ ;
/** @type {__VLS_StyleScopedClasses['upload-zone']} */ ;
/** @type {__VLS_StyleScopedClasses['upload-icon']} */ ;
/** @type {__VLS_StyleScopedClasses['upload-icon']} */ ;
/** @type {__VLS_StyleScopedClasses['upload-file-list']} */ ;
/** @type {__VLS_StyleScopedClasses['upload-file-item']} */ ;
/** @type {__VLS_StyleScopedClasses['upload-file-main']} */ ;
/** @type {__VLS_StyleScopedClasses['error']} */ ;
/** @type {__VLS_StyleScopedClasses['upload-file-status']} */ ;
/** @type {__VLS_StyleScopedClasses['icon-button']} */ ;
/** @type {__VLS_StyleScopedClasses['button-row']} */ ;
/** @type {__VLS_StyleScopedClasses['upload-actions']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['ghost']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['primary']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['error']} */ ;
/** @type {__VLS_StyleScopedClasses['upload-summary']} */ ;
/** @type {__VLS_StyleScopedClasses['card']} */ ;
/** @type {__VLS_StyleScopedClasses['upload-note']} */ ;
var __VLS_dollars;
var __VLS_self = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () {
        return {
            CheckCircle2: lucide_vue_next_1.CheckCircle2,
            FileCheck2: lucide_vue_next_1.FileCheck2,
            FileUp: lucide_vue_next_1.FileUp,
            Sparkles: lucide_vue_next_1.Sparkles,
            X: lucide_vue_next_1.X,
            XCircle: lucide_vue_next_1.XCircle,
            AppShell: AppShell_vue_1.default,
            WorkflowStepper: WorkflowStepper_vue_1.default,
            items: items,
            nativeFileInput: nativeFileInput,
            loading: loading,
            error: error,
            dragging: dragging,
            isRetryUpload: isRetryUpload,
            isBatch: isBatch,
            successCount: successCount,
            failedCount: failedCount,
            totalSize: totalSize,
            removeItem: removeItem,
            clearFiles: clearFiles,
            onFileChange: onFileChange,
            onDrop: onDrop,
            upload: upload,
            statusText: statusText,
        };
    },
});
exports.default = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () {
        return {};
    },
});
; /* PartiallyEnd: #4569/main.vue */
