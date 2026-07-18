"use strict";
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
Object.defineProperty(exports, "__esModule", { value: true });
var test_utils_1 = require("@vue/test-utils");
var vue_router_1 = require("vue-router");
var vitest_1 = require("vitest");
var textPreview_1 = require("../utils/textPreview");
var _a = vitest_1.vi.hoisted(function () { return ({ getLessonPlan: vitest_1.vi.fn(), presentLessonPlan: vitest_1.vi.fn() }); }), getLessonPlan = _a.getLessonPlan, presentLessonPlan = _a.presentLessonPlan;
vitest_1.vi.mock('../api/lessonPlanApi', function () { return ({
    lessonPlanApi: { getLessonPlan: getLessonPlan },
}); });
vitest_1.vi.mock('../utils/lessonPlanPresentation', function () { return ({ presentLessonPlan: presentLessonPlan }); });
var LessonParseResultView_vue_1 = require("./LessonParseResultView.vue");
(0, vitest_1.describe)('LessonParseResultView', function () {
    (0, vitest_1.it)('renders the bounded presentation summary and keeps raw content collapsed', function () { return __awaiter(void 0, void 0, void 0, function () {
        var router, wrapper;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    presentLessonPlan.mockReturnValue({
                        courseName: '闪烁的小星',
                        grade: '一年级',
                        objectives: ['能跟唱旋律'],
                        keyPoints: ['稳定节拍'],
                        process: [{ title: '律动导入', duration: '5分钟' }],
                        musicElements: ['旋律'],
                    });
                    getLessonPlan.mockResolvedValue({
                        id: 8,
                        title: '小星星',
                        rawText: '这是教案原文',
                        parsedJson: JSON.stringify({
                            courseName: '闪烁的小星',
                            grade: '一年级',
                            objectives: ['能跟唱旋律'],
                            keyPoints: ['稳定节拍'],
                            process: [{ title: '律动导入', duration: '5分钟' }],
                            musicElements: ['旋律'],
                        }),
                    });
                    router = (0, vue_router_1.createRouter)({
                        history: (0, vue_router_1.createMemoryHistory)(),
                        routes: [{ path: '/lesson-plans/:lessonPlanId/parse-result', component: LessonParseResultView_vue_1.default }],
                    });
                    return [4 /*yield*/, router.push('/lesson-plans/8/parse-result')];
                case 1:
                    _a.sent();
                    return [4 /*yield*/, router.isReady()];
                case 2:
                    _a.sent();
                    wrapper = (0, test_utils_1.mount)(LessonParseResultView_vue_1.default, {
                        global: {
                            plugins: [router],
                            stubs: { AppShell: { template: '<div><slot /></div>' } },
                        },
                    });
                    return [4 /*yield*/, (0, test_utils_1.flushPromises)()];
                case 3:
                    _a.sent();
                    (0, vitest_1.expect)(presentLessonPlan).toHaveBeenCalledWith(vitest_1.expect.objectContaining({ id: 8 }));
                    (0, vitest_1.expect)(wrapper.text()).toContain('闪烁的小星');
                    (0, vitest_1.expect)(wrapper.text()).toContain('一年级');
                    (0, vitest_1.expect)(wrapper.text()).toContain('音乐要素');
                    (0, vitest_1.expect)(wrapper.text()).toContain('能跟唱旋律');
                    (0, vitest_1.expect)(wrapper.text()).toContain('稳定节拍');
                    (0, vitest_1.expect)(wrapper.text()).toContain('律动导入');
                    (0, vitest_1.expect)(wrapper.findAll('details')).toHaveLength(2);
                    (0, vitest_1.expect)(wrapper.findAll('details').every(function (details) { return details.attributes('open') === undefined; })).toBe(true);
                    (0, vitest_1.expect)(wrapper.get('a.button.primary').text()).toBe('内容无误，设置课堂');
                    (0, vitest_1.expect)(wrapper.get('a.button.primary').attributes('href')).toBe('/packages/generate?lessonPlanId=8');
                    return [2 /*return*/];
            }
        });
    }); });
    (0, vitest_1.it)('caps both collapsed raw previews and explains when content is truncated', function () { return __awaiter(void 0, void 0, void 0, function () {
        var router, wrapper;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    presentLessonPlan.mockReturnValue({ courseName: '安全教案', grade: '', objectives: [], keyPoints: [], process: [], musicElements: [] });
                    getLessonPlan.mockResolvedValue({
                        id: 9,
                        title: '安全教案',
                        parsedJson: 'J'.repeat(textPreview_1.RAW_PREVIEW_MAX_LENGTH + 120),
                        rawText: 'R'.repeat(textPreview_1.RAW_PREVIEW_MAX_LENGTH + 120),
                    });
                    router = (0, vue_router_1.createRouter)({
                        history: (0, vue_router_1.createMemoryHistory)(),
                        routes: [{ path: '/lesson-plans/:lessonPlanId/parse-result', component: LessonParseResultView_vue_1.default }],
                    });
                    return [4 /*yield*/, router.push('/lesson-plans/9/parse-result')];
                case 1:
                    _a.sent();
                    return [4 /*yield*/, router.isReady()];
                case 2:
                    _a.sent();
                    wrapper = (0, test_utils_1.mount)(LessonParseResultView_vue_1.default, {
                        global: { plugins: [router], stubs: { AppShell: { template: '<div><slot /></div>' } } },
                    });
                    return [4 /*yield*/, (0, test_utils_1.flushPromises)()];
                case 3:
                    _a.sent();
                    (0, vitest_1.expect)(wrapper.findAll('.parse-raw-details pre').map(function (preview) { return preview.text().length; })).toEqual([textPreview_1.RAW_PREVIEW_MAX_LENGTH, textPreview_1.RAW_PREVIEW_MAX_LENGTH]);
                    (0, vitest_1.expect)(wrapper.findAll('.parse-preview-truncated')).toHaveLength(2);
                    (0, vitest_1.expect)(wrapper.findAll('.parse-preview-truncated').every(function (notice) { return notice.text().includes('内容已截断'); })).toBe(true);
                    return [2 /*return*/];
            }
        });
    }); });
});
