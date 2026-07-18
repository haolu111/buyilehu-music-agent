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
var _a = vitest_1.vi.hoisted(function () { return ({
    listMine: vitest_1.vi.fn(),
    createGenerationJob: vitest_1.vi.fn(),
}); }), listMine = _a.listMine, createGenerationJob = _a.createGenerationJob;
vitest_1.vi.mock('../api/lessonPlanApi', function () { return ({ lessonPlanApi: { listMine: listMine } }); });
vitest_1.vi.mock('../api/packageApi', function () { return ({ packageApi: { createGenerationJob: createGenerationJob } }); });
var PackageGenerateView_vue_1 = require("./PackageGenerateView.vue");
function makeRouter() {
    return (0, vue_router_1.createRouter)({
        history: (0, vue_router_1.createMemoryHistory)(),
        routes: [
            { path: '/packages/generate', component: PackageGenerateView_vue_1.default },
            { path: '/packages/:packageId/proposal', component: { template: '<div />' } },
        ],
    });
}
(0, vitest_1.describe)('PackageGenerateView', function () {
    (0, vitest_1.beforeEach)(function () {
        listMine.mockResolvedValue([{ id: 8, title: '小星星', parseStatus: 'success' }]);
        createGenerationJob.mockResolvedValue({ id: 2, lessonPlanId: 8, status: 'completed', packageId: 34 });
    });
    (0, vitest_1.it)('uses the setup-classroom workflow step and keeps advanced options closed by default', function () { return __awaiter(void 0, void 0, void 0, function () {
        var router, wrapper, advanced;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    router = makeRouter();
                    return [4 /*yield*/, router.push('/packages/generate?lessonPlanId=8')];
                case 1:
                    _a.sent();
                    return [4 /*yield*/, router.isReady()];
                case 2:
                    _a.sent();
                    wrapper = (0, test_utils_1.mount)(PackageGenerateView_vue_1.default, {
                        global: { plugins: [router], stubs: { AppShell: { template: '<div><slot /></div>' }, LessonWorkspaceNav: { template: '<div />' } } },
                    });
                    return [4 /*yield*/, (0, test_utils_1.flushPromises)()];
                case 3:
                    _a.sent();
                    (0, vitest_1.expect)(wrapper.get('[data-stage="setup-classroom"]').attributes('data-state')).toBe('current');
                    (0, vitest_1.expect)(wrapper.get('select[name="lesson-plan"]').element.value).toBe('8');
                    advanced = wrapper.get('details[data-testid="advanced-generation-settings"]');
                    (0, vitest_1.expect)(advanced.attributes('open')).toBeUndefined();
                    (0, vitest_1.expect)(advanced.text()).toContain('活动密度');
                    (0, vitest_1.expect)(advanced.text()).toContain('视觉情境');
                    return [2 /*return*/];
            }
        });
    }); });
    (0, vitest_1.it)('keeps the selected lesson and all existing defaults in the generation request', function () { return __awaiter(void 0, void 0, void 0, function () {
        var router, wrapper;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    router = makeRouter();
                    return [4 /*yield*/, router.push('/packages/generate?lessonPlanId=8')];
                case 1:
                    _a.sent();
                    return [4 /*yield*/, router.isReady()];
                case 2:
                    _a.sent();
                    wrapper = (0, test_utils_1.mount)(PackageGenerateView_vue_1.default, {
                        global: { plugins: [router], stubs: { AppShell: { template: '<div><slot /></div>' }, LessonWorkspaceNav: { template: '<div />' } } },
                    });
                    return [4 /*yield*/, (0, test_utils_1.flushPromises)()];
                case 3:
                    _a.sent();
                    return [4 /*yield*/, wrapper.get('[data-testid="generate-package"]').trigger('click')];
                case 4:
                    _a.sent();
                    return [4 /*yield*/, (0, test_utils_1.flushPromises)()];
                case 5:
                    _a.sent();
                    (0, vitest_1.expect)(createGenerationJob).toHaveBeenCalledWith(8, {
                        duration: 40, mode: 'individual', density: 'standard', difficulty: 'grade', flow: 'teacher', theme: 'auto',
                    });
                    (0, vitest_1.expect)(router.currentRoute.value.fullPath).toBe('/packages/34/proposal');
                    return [2 /*return*/];
            }
        });
    }); });
});
