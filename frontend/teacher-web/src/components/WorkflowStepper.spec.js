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
var vue_1 = require("vue");
var vitest_1 = require("vitest");
var WorkflowStepper_vue_1 = require("./WorkflowStepper.vue");
(0, vitest_1.describe)('WorkflowStepper', function () {
    (0, vitest_1.it)('uses the approved six-stage teaching workflow and maps proposal review separately', function () {
        var router = (0, vue_router_1.createRouter)({
            history: (0, vue_router_1.createMemoryHistory)(),
            routes: [{ path: '/:pathMatch(.*)*', component: { template: '<div />' } }],
        });
        var wrapper = (0, test_utils_1.mount)(WorkflowStepper_vue_1.default, {
            props: {
                currentStage: 'confirm-proposal',
                lessonPlanId: 8,
                packageId: 13,
            },
            global: { plugins: [router] },
        });
        (0, vitest_1.expect)(wrapper.text()).toContain('上传教案');
        (0, vitest_1.expect)(wrapper.text()).toContain('确认内容');
        (0, vitest_1.expect)(wrapper.text()).toContain('设置课堂');
        (0, vitest_1.expect)(wrapper.text()).toContain('确认方案');
        (0, vitest_1.expect)(wrapper.text()).toContain('编辑互动包');
        (0, vitest_1.expect)(wrapper.text()).toContain('发布课堂');
        (0, vitest_1.expect)(wrapper.text()).not.toContain('课堂控制');
        (0, vitest_1.expect)(wrapper.get('[data-stage="upload-lesson"]').attributes('data-state')).toBe('completed');
        (0, vitest_1.expect)(wrapper.get('[data-stage="upload-lesson"] a').attributes('href')).toBe('/lesson-plans/upload');
        (0, vitest_1.expect)(wrapper.get('[data-stage="setup-classroom"] a').attributes('href')).toBe('/packages/generate?lessonPlanId=8');
        (0, vitest_1.expect)(wrapper.get('[data-stage="confirm-proposal"]').attributes('data-state')).toBe('current');
        (0, vitest_1.expect)(wrapper.get('[data-stage="confirm-proposal"]').attributes('aria-current')).toBe('step');
        (0, vitest_1.expect)(wrapper.get('[data-stage="edit-package"]').attributes('data-state')).toBe('upcoming');
        (0, vitest_1.expect)(wrapper.get('[data-stage="edit-package"] [aria-disabled="true"]').text()).toContain('编辑互动包');
    });
    (0, vitest_1.it)('uses router links for available internal workflow routes', function () { return __awaiter(void 0, void 0, void 0, function () {
        var router, wrapper;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    router = (0, vue_router_1.createRouter)({
                        history: (0, vue_router_1.createMemoryHistory)(),
                        routes: [
                            { path: '/current', component: { template: '<div />' } },
                            { path: '/lesson-plans/upload', component: { template: '<div />' } },
                        ],
                    });
                    return [4 /*yield*/, router.push('/current')];
                case 1:
                    _a.sent();
                    return [4 /*yield*/, router.isReady()];
                case 2:
                    _a.sent();
                    wrapper = (0, test_utils_1.mount)(WorkflowStepper_vue_1.default, {
                        props: { currentStage: 'confirm-content', lessonPlanId: 8 },
                        global: { plugins: [router] },
                    });
                    return [4 /*yield*/, wrapper.get('[data-stage="upload-lesson"] a').trigger('click')];
                case 3:
                    _a.sent();
                    return [4 /*yield*/, (0, vue_1.nextTick)()];
                case 4:
                    _a.sent();
                    return [4 /*yield*/, (0, test_utils_1.flushPromises)()];
                case 5:
                    _a.sent();
                    (0, vitest_1.expect)(router.currentRoute.value.path).toBe('/lesson-plans/upload');
                    return [2 /*return*/];
            }
        });
    }); });
});
