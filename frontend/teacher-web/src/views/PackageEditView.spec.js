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
var _a = vitest_1.vi.hoisted(function () { return ({ getProposal: vitest_1.vi.fn(), listVersions: vitest_1.vi.fn() }); }), getProposal = _a.getProposal, listVersions = _a.listVersions;
vitest_1.vi.mock('../api/packageApi', function () { return ({ packageApi: { getProposal: getProposal, listVersions: listVersions } }); });
var PackageEditView_vue_1 = require("./PackageEditView.vue");
(0, vitest_1.describe)('PackageEditView', function () {
    (0, vitest_1.beforeEach)(function () {
        getProposal.mockResolvedValue({ id: 3, packageId: 34, title: '小星星互动包', content: '', status: 'draft', confirmStatus: 'confirmed', teachingObjectives: [], sourceLessonSections: [], activityNodes: [], components: [] });
        listVersions.mockResolvedValue([]);
    });
    (0, vitest_1.it)('marks editing as the current workflow stage and provides the publishing next action', function () { return __awaiter(void 0, void 0, void 0, function () {
        var router, wrapper;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    router = (0, vue_router_1.createRouter)({
                        history: (0, vue_router_1.createMemoryHistory)(),
                        routes: [
                            { path: '/packages/:packageId/edit', component: PackageEditView_vue_1.default },
                            { path: '/packages/:packageId/proposal', component: { template: '<div>确认方案</div>' } },
                            { path: '/packages/:packageId', component: { template: '<div>详情</div>' } },
                            { path: '/packages/:packageId/publish', component: { template: '<div>发布</div>' } },
                            { path: '/lesson-plans/upload', component: { template: '<div>上传</div>' } },
                        ],
                    });
                    return [4 /*yield*/, router.push('/packages/34/edit')];
                case 1:
                    _a.sent();
                    return [4 /*yield*/, router.isReady()];
                case 2:
                    _a.sent();
                    wrapper = (0, test_utils_1.mount)(PackageEditView_vue_1.default, {
                        global: {
                            plugins: [router],
                            stubs: {
                                AppShell: { template: '<div><slot /></div>' },
                                VersionHistoryPanel: { template: '<div />' },
                                ActivityNodeEditView: { template: '<div />' },
                            },
                        },
                    });
                    return [4 /*yield*/, (0, test_utils_1.flushPromises)()];
                case 3:
                    _a.sent();
                    (0, vitest_1.expect)(wrapper.get('[data-stage="edit-package"]').attributes('data-state')).toBe('current');
                    (0, vitest_1.expect)(wrapper.get('[data-testid="publish-classroom-next"]').text()).toContain('发布到班级');
                    (0, vitest_1.expect)(wrapper.get('[data-testid="publish-classroom-next"]').attributes('href')).toBe('/packages/34/publish');
                    (0, vitest_1.expect)(wrapper.get('a.button:not([data-testid])').attributes('href')).toBe('/packages/34');
                    return [2 /*return*/];
            }
        });
    }); });
});
