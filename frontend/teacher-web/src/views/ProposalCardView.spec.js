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
Object.defineProperty(exports, "__esModule", { value: true });
var test_utils_1 = require("@vue/test-utils");
var vue_router_1 = require("vue-router");
var vitest_1 = require("vitest");
var _a = vitest_1.vi.hoisted(function () { return ({ getProposal: vitest_1.vi.fn(), confirmProposal: vitest_1.vi.fn() }); }), getProposal = _a.getProposal, confirmProposal = _a.confirmProposal;
vitest_1.vi.mock('../api/packageApi', function () { return ({ packageApi: { getProposal: getProposal, confirmProposal: confirmProposal } }); });
var ProposalCardView_vue_1 = require("./ProposalCardView.vue");
var proposal = {
    id: 3, packageId: 34, packageInfo: { id: 34, lessonPlanId: 8, title: '小星星互动方案', status: 'generated' }, title: '小星星互动方案', versionNo: 1, content: '课程：音乐\n时长：40分钟\ntrace：private', status: 'generated', confirmStatus: 'pending',
    teachingObjectives: ['稳定拍点'], sourceLessonSections: ['律动导入'],
    activityNodes: [{ id: 9, title: '听辨旋律', nodeType: 'listening_activity', sortOrder: 1, components: [] }], components: [],
};
function makeRouter() {
    return (0, vue_router_1.createRouter)({
        history: (0, vue_router_1.createMemoryHistory)(),
        routes: [
            { path: '/packages/:packageId/proposal', component: ProposalCardView_vue_1.default },
            { path: '/packages/:packageId/edit', component: { template: '<div>编辑页</div>' } },
            { path: '/packages/generate', component: { template: '<div>设置课堂</div>' } },
            { path: '/lesson-plans/upload', component: { template: '<div>上传教案</div>' } },
        ],
    });
}
(0, vitest_1.describe)('ProposalCardView', function () {
    (0, vitest_1.beforeEach)(function () {
        getProposal.mockResolvedValue(proposal);
        confirmProposal.mockResolvedValue(__assign(__assign({}, proposal), { confirmStatus: 'confirmed' }));
    });
    (0, vitest_1.it)('shows the confirm-proposal workflow stage and collapses supporting details', function () { return __awaiter(void 0, void 0, void 0, function () {
        var router, wrapper;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    router = makeRouter();
                    return [4 /*yield*/, router.push('/packages/34/proposal')];
                case 1:
                    _a.sent();
                    return [4 /*yield*/, router.isReady()];
                case 2:
                    _a.sent();
                    wrapper = (0, test_utils_1.mount)(ProposalCardView_vue_1.default, {
                        global: { plugins: [router], stubs: { AppShell: { template: '<div><slot /></div>' }, LessonWorkspaceNav: { template: '<div />' } } },
                    });
                    return [4 /*yield*/, (0, test_utils_1.flushPromises)()];
                case 3:
                    _a.sent();
                    (0, vitest_1.expect)(wrapper.get('[data-stage="confirm-proposal"]').attributes('data-state')).toBe('current');
                    (0, vitest_1.expect)(wrapper.get('[data-testid="back-to-classroom-settings"]').text()).toBe('返回调整');
                    (0, vitest_1.expect)(wrapper.get('[data-testid="confirm-proposal"]').text()).toBe('确认方案，进入编辑');
                    (0, vitest_1.expect)(wrapper.get('details[data-testid="proposal-objectives"]').attributes('open')).toBeUndefined();
                    (0, vitest_1.expect)(wrapper.get('details[data-testid="proposal-source"]').attributes('open')).toBeUndefined();
                    return [2 /*return*/];
            }
        });
    }); });
    (0, vitest_1.it)('confirms once and goes directly to package editing', function () { return __awaiter(void 0, void 0, void 0, function () {
        var router, wrapper;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    router = makeRouter();
                    return [4 /*yield*/, router.push('/packages/34/proposal')];
                case 1:
                    _a.sent();
                    return [4 /*yield*/, router.isReady()];
                case 2:
                    _a.sent();
                    wrapper = (0, test_utils_1.mount)(ProposalCardView_vue_1.default, {
                        global: { plugins: [router], stubs: { AppShell: { template: '<div><slot /></div>' }, LessonWorkspaceNav: { template: '<div />' } } },
                    });
                    return [4 /*yield*/, (0, test_utils_1.flushPromises)()];
                case 3:
                    _a.sent();
                    return [4 /*yield*/, wrapper.get('[data-testid="confirm-proposal"]').trigger('click')];
                case 4:
                    _a.sent();
                    return [4 /*yield*/, (0, test_utils_1.flushPromises)()];
                case 5:
                    _a.sent();
                    (0, vitest_1.expect)(confirmProposal).toHaveBeenCalledWith(34);
                    (0, vitest_1.expect)(router.currentRoute.value.fullPath).toBe('/packages/34/edit');
                    return [2 /*return*/];
            }
        });
    }); });
    (0, vitest_1.it)('returns to the original lesson plan settings when the teacher adjusts the proposal', function () { return __awaiter(void 0, void 0, void 0, function () {
        var router, wrapper;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    router = makeRouter();
                    return [4 /*yield*/, router.push('/packages/34/proposal')];
                case 1:
                    _a.sent();
                    return [4 /*yield*/, router.isReady()];
                case 2:
                    _a.sent();
                    wrapper = (0, test_utils_1.mount)(ProposalCardView_vue_1.default, {
                        global: { plugins: [router], stubs: { AppShell: { template: '<div><slot /></div>' }, LessonWorkspaceNav: { template: '<div />' } } },
                    });
                    return [4 /*yield*/, (0, test_utils_1.flushPromises)()];
                case 3:
                    _a.sent();
                    return [4 /*yield*/, wrapper.get('[data-testid="back-to-classroom-settings"]').trigger('click')];
                case 4:
                    _a.sent();
                    return [4 /*yield*/, (0, test_utils_1.flushPromises)()];
                case 5:
                    _a.sent();
                    (0, vitest_1.expect)(router.currentRoute.value.fullPath).toBe('/packages/generate?lessonPlanId=8');
                    return [2 /*return*/];
            }
        });
    }); });
    (0, vitest_1.it)('does not offer confirmation again after the proposal is already confirmed', function () { return __awaiter(void 0, void 0, void 0, function () {
        var router, wrapper;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    getProposal.mockResolvedValue(__assign(__assign({}, proposal), { confirmStatus: 'confirmed' }));
                    router = makeRouter();
                    return [4 /*yield*/, router.push('/packages/34/proposal')];
                case 1:
                    _a.sent();
                    return [4 /*yield*/, router.isReady()];
                case 2:
                    _a.sent();
                    wrapper = (0, test_utils_1.mount)(ProposalCardView_vue_1.default, {
                        global: { plugins: [router], stubs: { AppShell: { template: '<div><slot /></div>' }, LessonWorkspaceNav: { template: '<div />' } } },
                    });
                    return [4 /*yield*/, (0, test_utils_1.flushPromises)()];
                case 3:
                    _a.sent();
                    (0, vitest_1.expect)(wrapper.find('[data-testid="confirm-proposal"]').exists()).toBe(false);
                    (0, vitest_1.expect)(wrapper.get('[data-testid="edit-confirmed-package"]').attributes('href')).toBe('/packages/34/edit');
                    return [2 /*return*/];
            }
        });
    }); });
});
