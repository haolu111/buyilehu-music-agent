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
var pinia_1 = require("pinia");
var vitest_1 = require("vitest");
var _a = vitest_1.vi.hoisted(function () { return ({
    listClasses: vitest_1.vi.fn(),
    listActiveSessions: vitest_1.vi.fn(),
    listMine: vitest_1.vi.fn(),
    listPackages: vitest_1.vi.fn(),
    upload: vitest_1.vi.fn(),
}); }), listClasses = _a.listClasses, listActiveSessions = _a.listActiveSessions, listMine = _a.listMine, listPackages = _a.listPackages, upload = _a.upload;
vitest_1.vi.mock('../api/classApi', function () { return ({ classApi: { listClasses: listClasses } }); });
vitest_1.vi.mock('../api/classroomApi', function () { return ({ classroomApi: { listActiveSessions: listActiveSessions } }); });
vitest_1.vi.mock('../api/lessonPlanApi', function () { return ({ lessonPlanApi: { listMine: listMine, upload: upload } }); });
vitest_1.vi.mock('../api/packageApi', function () { return ({ packageApi: { listPackages: listPackages } }); });
var DashboardView_vue_1 = require("./DashboardView.vue");
var LessonPlanHistoryView_vue_1 = require("./LessonPlanHistoryView.vue");
var LessonUploadView_vue_1 = require("./LessonUploadView.vue");
var authStore_1 = require("../stores/authStore");
function routerFor(component, path) {
    return (0, vue_router_1.createRouter)({ history: (0, vue_router_1.createMemoryHistory)(), routes: [{ path: path, component: component }, { path: '/:pathMatch(.*)*', component: { template: '<div />' } }] });
}
function shellStub() {
    return { AppShell: { template: '<div><slot /></div>' }, LessonWorkspaceNav: { template: '<div />' } };
}
(0, vitest_1.describe)('teacher entry flow', function () {
    (0, vitest_1.beforeEach)(function () {
        (0, pinia_1.setActivePinia)((0, pinia_1.createPinia)());
        (0, authStore_1.useAuthStore)().user = { id: 1, username: 'teacher', role: 'teacher', displayName: '林老师' };
        listClasses.mockResolvedValue([]);
        listPackages.mockResolvedValue([]);
        listMine.mockResolvedValue([]);
        listActiveSessions.mockResolvedValue([]);
    });
    (0, vitest_1.it)('keeps exactly two fixed dashboard actions and sends teachers to a live classroom', function () { return __awaiter(void 0, void 0, void 0, function () {
        var router, wrapper, actions;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    listActiveSessions.mockResolvedValue([{ id: 24, status: 'running', nodeStates: [], courseTitle: '节奏游戏' }]);
                    router = routerFor(DashboardView_vue_1.default, '/dashboard');
                    return [4 /*yield*/, router.push('/dashboard')];
                case 1:
                    _a.sent();
                    return [4 /*yield*/, router.isReady()];
                case 2:
                    _a.sent();
                    wrapper = (0, test_utils_1.mount)(DashboardView_vue_1.default, { global: { plugins: [router], stubs: shellStub() } });
                    return [4 /*yield*/, (0, test_utils_1.flushPromises)()];
                case 3:
                    _a.sent();
                    actions = wrapper.get('[data-testid="dashboard-primary-actions"]');
                    (0, vitest_1.expect)(actions.findAll('a')).toHaveLength(2);
                    (0, vitest_1.expect)(actions.text()).toContain('上传教案');
                    (0, vitest_1.expect)(actions.text()).toContain('进入课堂');
                    (0, vitest_1.expect)(actions.findAll('a').map(function (link) { return link.attributes('href'); })).toEqual(['/lesson-plans/upload', '/classroom/24/control']);
                    return [2 /*return*/];
            }
        });
    }); });
    (0, vitest_1.it)('keeps the primary actions clear beside a decorative music-classroom scene', function () { return __awaiter(void 0, void 0, void 0, function () {
        var router, wrapper, scene;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    router = routerFor(DashboardView_vue_1.default, '/dashboard');
                    return [4 /*yield*/, router.push('/dashboard')];
                case 1:
                    _a.sent();
                    return [4 /*yield*/, router.isReady()];
                case 2:
                    _a.sent();
                    wrapper = (0, test_utils_1.mount)(DashboardView_vue_1.default, { global: { plugins: [router], stubs: shellStub() } });
                    return [4 /*yield*/, (0, test_utils_1.flushPromises)()];
                case 3:
                    _a.sent();
                    scene = wrapper.get('[data-testid="dashboard-music-scene"]');
                    (0, vitest_1.expect)(scene.attributes('aria-hidden')).toBe('true');
                    (0, vitest_1.expect)(scene.get('img').attributes('alt')).toBe('');
                    (0, vitest_1.expect)(wrapper.get('[data-testid="dashboard-primary-actions"]').text()).toContain('上传教案');
                    (0, vitest_1.expect)(wrapper.get('[data-testid="dashboard-primary-actions"]').text()).toContain('进入课堂');
                    return [2 /*return*/];
            }
        });
    }); });
    (0, vitest_1.it)('keeps a paused classroom available from the dashboard entry action', function () { return __awaiter(void 0, void 0, void 0, function () {
        var router, wrapper;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    listActiveSessions.mockResolvedValue([{ id: 31, status: 'paused', nodeStates: [], courseTitle: '合唱排练' }]);
                    router = routerFor(DashboardView_vue_1.default, '/dashboard');
                    return [4 /*yield*/, router.push('/dashboard')];
                case 1:
                    _a.sent();
                    return [4 /*yield*/, router.isReady()];
                case 2:
                    _a.sent();
                    wrapper = (0, test_utils_1.mount)(DashboardView_vue_1.default, { global: { plugins: [router], stubs: shellStub() } });
                    return [4 /*yield*/, (0, test_utils_1.flushPromises)()];
                case 3:
                    _a.sent();
                    (0, vitest_1.expect)(wrapper.get('[data-testid="dashboard-primary-actions"]').findAll('a')[1].attributes('href')).toBe('/classroom/31/control');
                    return [2 /*return*/];
            }
        });
    }); });
    (0, vitest_1.it)('keeps an upcoming classroom available from the dashboard entry action', function () { return __awaiter(void 0, void 0, void 0, function () {
        var router, wrapper;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    listActiveSessions.mockResolvedValue([{ id: 32, status: 'not_started', nodeStates: [], courseTitle: '节拍练习' }]);
                    router = routerFor(DashboardView_vue_1.default, '/dashboard');
                    return [4 /*yield*/, router.push('/dashboard')];
                case 1:
                    _a.sent();
                    return [4 /*yield*/, router.isReady()];
                case 2:
                    _a.sent();
                    wrapper = (0, test_utils_1.mount)(DashboardView_vue_1.default, { global: { plugins: [router], stubs: shellStub() } });
                    return [4 /*yield*/, (0, test_utils_1.flushPromises)()];
                case 3:
                    _a.sent();
                    (0, vitest_1.expect)(wrapper.get('[data-testid="dashboard-primary-actions"]').findAll('a')[1].attributes('href')).toBe('/classroom/32/control');
                    return [2 /*return*/];
            }
        });
    }); });
    (0, vitest_1.it)('uses the classroom list for the dashboard classroom action and hides zero pending items', function () { return __awaiter(void 0, void 0, void 0, function () {
        var router, wrapper;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    router = routerFor(DashboardView_vue_1.default, '/dashboard');
                    return [4 /*yield*/, router.push('/dashboard')];
                case 1:
                    _a.sent();
                    return [4 /*yield*/, router.isReady()];
                case 2:
                    _a.sent();
                    wrapper = (0, test_utils_1.mount)(DashboardView_vue_1.default, { global: { plugins: [router], stubs: shellStub() } });
                    return [4 /*yield*/, (0, test_utils_1.flushPromises)()];
                case 3:
                    _a.sent();
                    (0, vitest_1.expect)(wrapper.get('[data-testid="dashboard-primary-actions"]').findAll('a')[1].attributes('href')).toBe('/classrooms');
                    (0, vitest_1.expect)(wrapper.findAll('[data-testid="continue-item"]')).toHaveLength(0);
                    (0, vitest_1.expect)(wrapper.get('[data-testid="continue-empty"]').text()).toContain('暂时没有待处理事项');
                    return [2 /*return*/];
            }
        });
    }); });
    (0, vitest_1.it)('sends the ready-package task to the counted generated package proposal', function () { return __awaiter(void 0, void 0, void 0, function () {
        var router, wrapper, packageAction;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    listPackages.mockResolvedValue([
                        { id: 51, title: '节奏冒险', status: 'generated' },
                        { id: 52, title: '旋律接龙', status: 'draft' },
                    ]);
                    router = routerFor(DashboardView_vue_1.default, '/dashboard');
                    return [4 /*yield*/, router.push('/dashboard')];
                case 1:
                    _a.sent();
                    return [4 /*yield*/, router.isReady()];
                case 2:
                    _a.sent();
                    wrapper = (0, test_utils_1.mount)(DashboardView_vue_1.default, { global: { plugins: [router], stubs: shellStub() } });
                    return [4 /*yield*/, (0, test_utils_1.flushPromises)()];
                case 3:
                    _a.sent();
                    packageAction = wrapper.get('[data-testid="continue-package-item"]');
                    (0, vitest_1.expect)(packageAction.attributes('href')).toBe('/packages/51/proposal');
                    (0, vitest_1.expect)(packageAction.text()).toContain('确认互动方案');
                    return [2 /*return*/];
            }
        });
    }); });
    (0, vitest_1.it)('sends a modified package to its classroom publishing flow', function () { return __awaiter(void 0, void 0, void 0, function () {
        var router, wrapper, packageAction;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    listPackages.mockResolvedValue([{ id: 53, title: '打击乐合奏', status: 'modified' }]);
                    router = routerFor(DashboardView_vue_1.default, '/dashboard');
                    return [4 /*yield*/, router.push('/dashboard')];
                case 1:
                    _a.sent();
                    return [4 /*yield*/, router.isReady()];
                case 2:
                    _a.sent();
                    wrapper = (0, test_utils_1.mount)(DashboardView_vue_1.default, { global: { plugins: [router], stubs: shellStub() } });
                    return [4 /*yield*/, (0, test_utils_1.flushPromises)()];
                case 3:
                    _a.sent();
                    packageAction = wrapper.get('[data-testid="continue-package-item"]');
                    (0, vitest_1.expect)(packageAction.attributes('href')).toBe('/packages/53/publish');
                    (0, vitest_1.expect)(packageAction.text()).toContain('发布课堂');
                    return [2 /*return*/];
            }
        });
    }); });
    (0, vitest_1.it)('shows a retry state instead of an empty dashboard when a data request fails', function () { return __awaiter(void 0, void 0, void 0, function () {
        var router, wrapper, callsBeforeRetry;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    listPackages.mockRejectedValueOnce(new Error('network unavailable'));
                    router = routerFor(DashboardView_vue_1.default, '/dashboard');
                    return [4 /*yield*/, router.push('/dashboard')];
                case 1:
                    _a.sent();
                    return [4 /*yield*/, router.isReady()];
                case 2:
                    _a.sent();
                    wrapper = (0, test_utils_1.mount)(DashboardView_vue_1.default, { global: { plugins: [router], stubs: shellStub() } });
                    return [4 /*yield*/, (0, test_utils_1.flushPromises)()];
                case 3:
                    _a.sent();
                    (0, vitest_1.expect)(wrapper.get('[data-testid="dashboard-load-error"]').text()).toContain('暂时无法加载');
                    (0, vitest_1.expect)(wrapper.get('[data-testid="dashboard-retry"]').text()).toContain('重试');
                    callsBeforeRetry = listPackages.mock.calls.length;
                    return [4 /*yield*/, wrapper.get('[data-testid="dashboard-retry"]').trigger('click')];
                case 4:
                    _a.sent();
                    return [4 /*yield*/, (0, test_utils_1.flushPromises)()];
                case 5:
                    _a.sent();
                    (0, vitest_1.expect)(listPackages).toHaveBeenCalledTimes(callsBeforeRetry + 1);
                    (0, vitest_1.expect)(wrapper.find('[data-testid="dashboard-load-error"]').exists()).toBe(false);
                    return [2 /*return*/];
            }
        });
    }); });
    (0, vitest_1.it)('reveals the lesson title after selecting a valid file and labels the primary action 解析教案', function () { return __awaiter(void 0, void 0, void 0, function () {
        var router, wrapper, fileInput;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    router = routerFor(LessonUploadView_vue_1.default, '/lesson-plans/upload');
                    return [4 /*yield*/, router.push('/lesson-plans/upload')];
                case 1:
                    _a.sent();
                    return [4 /*yield*/, router.isReady()];
                case 2:
                    _a.sent();
                    wrapper = (0, test_utils_1.mount)(LessonUploadView_vue_1.default, { global: { plugins: [router], stubs: shellStub() } });
                    (0, vitest_1.expect)(wrapper.find('input[name="lesson-title"]').exists()).toBe(false);
                    (0, vitest_1.expect)(wrapper.get('[data-testid="lesson-upload-primary"]').text()).toBe('解析教案');
                    (0, vitest_1.expect)(wrapper.get('[data-stage="upload-lesson"]').attributes('data-state')).toBe('current');
                    fileInput = wrapper.get('input[type="file"]');
                    Object.defineProperty(fileInput.element, 'files', { value: [new File(['lesson'], '小星星.docx', { type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' })] });
                    return [4 /*yield*/, fileInput.trigger('change')];
                case 3:
                    _a.sent();
                    (0, vitest_1.expect)(wrapper.get('input[name="lesson-title"]').element).toHaveProperty('value', '小星星');
                    return [2 /*return*/];
            }
        });
    }); });
    (0, vitest_1.it)('rejects unsupported and oversized uploads before exposing a title', function () { return __awaiter(void 0, void 0, void 0, function () {
        var router, wrapper, fileInput;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    router = routerFor(LessonUploadView_vue_1.default, '/lesson-plans/upload');
                    return [4 /*yield*/, router.push('/lesson-plans/upload')];
                case 1:
                    _a.sent();
                    return [4 /*yield*/, router.isReady()];
                case 2:
                    _a.sent();
                    wrapper = (0, test_utils_1.mount)(LessonUploadView_vue_1.default, { global: { plugins: [router], stubs: shellStub() } });
                    fileInput = wrapper.get('input[type="file"]');
                    Object.defineProperty(fileInput.element, 'files', { configurable: true, value: [new File(['bad'], '教案.exe', { type: 'application/octet-stream' })] });
                    return [4 /*yield*/, fileInput.trigger('change')];
                case 3:
                    _a.sent();
                    (0, vitest_1.expect)(wrapper.text()).toContain('请选择 DOCX、PDF 或 TXT 格式的教案');
                    (0, vitest_1.expect)(wrapper.find('input[name="lesson-title"]').exists()).toBe(false);
                    Object.defineProperty(fileInput.element, 'files', { configurable: true, value: [new File([new Uint8Array(20 * 1024 * 1024 + 1)], '太大的教案.pdf', { type: 'application/pdf' })] });
                    return [4 /*yield*/, fileInput.trigger('change')];
                case 4:
                    _a.sent();
                    (0, vitest_1.expect)(wrapper.text()).toContain('文件不能超过 20MB');
                    (0, vitest_1.expect)(wrapper.find('input[name="lesson-title"]').exists()).toBe(false);
                    return [2 /*return*/];
            }
        });
    }); });
    (0, vitest_1.it)('keeps an accepted lesson when an invalid additional file is rejected', function () { return __awaiter(void 0, void 0, void 0, function () {
        var router, wrapper, fileInput;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    router = routerFor(LessonUploadView_vue_1.default, '/lesson-plans/upload');
                    return [4 /*yield*/, router.push('/lesson-plans/upload')];
                case 1:
                    _a.sent();
                    return [4 /*yield*/, router.isReady()];
                case 2:
                    _a.sent();
                    wrapper = (0, test_utils_1.mount)(LessonUploadView_vue_1.default, { global: { plugins: [router], stubs: shellStub() } });
                    fileInput = wrapper.get('input[type="file"]');
                    Object.defineProperty(fileInput.element, 'files', { configurable: true, value: [new File(['lesson'], '小星星.docx')] });
                    return [4 /*yield*/, fileInput.trigger('change')];
                case 3:
                    _a.sent();
                    (0, vitest_1.expect)(wrapper.find('input[name="lesson-title"]').exists()).toBe(true);
                    Object.defineProperty(fileInput.element, 'value', { configurable: true, writable: true, value: 'C:\\fakepath\\坏文件.exe' });
                    Object.defineProperty(fileInput.element, 'files', { configurable: true, value: [new File(['bad'], '坏文件.exe')] });
                    return [4 /*yield*/, fileInput.trigger('change')];
                case 4:
                    _a.sent();
                    (0, vitest_1.expect)(wrapper.find('input[name="lesson-title"]').exists()).toBe(true);
                    (0, vitest_1.expect)(wrapper.get('[data-testid="lesson-upload-primary"]').attributes('disabled')).toBeUndefined();
                    (0, vitest_1.expect)(fileInput.element.value).toBe('');
                    return [2 /*return*/];
            }
        });
    }); });
    (0, vitest_1.it)('clears the native chooser on removal so the same file can be selected again', function () { return __awaiter(void 0, void 0, void 0, function () {
        var router, wrapper, fileInput, lesson;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    router = routerFor(LessonUploadView_vue_1.default, '/lesson-plans/upload');
                    return [4 /*yield*/, router.push('/lesson-plans/upload')];
                case 1:
                    _a.sent();
                    return [4 /*yield*/, router.isReady()];
                case 2:
                    _a.sent();
                    wrapper = (0, test_utils_1.mount)(LessonUploadView_vue_1.default, { global: { plugins: [router], stubs: shellStub() } });
                    fileInput = wrapper.get('input[type="file"]');
                    lesson = new File(['lesson'], '小星星.docx');
                    Object.defineProperty(fileInput.element, 'files', { configurable: true, value: [lesson] });
                    Object.defineProperty(fileInput.element, 'value', { configurable: true, writable: true, value: 'C:\\fakepath\\小星星.docx' });
                    return [4 /*yield*/, fileInput.trigger('change')];
                case 3:
                    _a.sent();
                    return [4 /*yield*/, wrapper.get('button.ghost').trigger('click')];
                case 4:
                    _a.sent();
                    (0, vitest_1.expect)(fileInput.element.value).toBe('');
                    (0, vitest_1.expect)(wrapper.get('[data-testid="lesson-upload-primary"]').attributes('disabled')).toBeDefined();
                    Object.defineProperty(fileInput.element, 'files', { configurable: true, value: [lesson] });
                    return [4 /*yield*/, fileInput.trigger('change')];
                case 5:
                    _a.sent();
                    (0, vitest_1.expect)(wrapper.get('input[name="lesson-title"]').element).toHaveProperty('value', '小星星');
                    return [2 /*return*/];
            }
        });
    }); });
    (0, vitest_1.it)('shows retry context but still requires a new lesson file', function () { return __awaiter(void 0, void 0, void 0, function () {
        var router, wrapper;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    router = routerFor(LessonUploadView_vue_1.default, '/lesson-plans/upload');
                    return [4 /*yield*/, router.push('/lesson-plans/upload?retryLessonPlanId=2')];
                case 1:
                    _a.sent();
                    return [4 /*yield*/, router.isReady()];
                case 2:
                    _a.sent();
                    wrapper = (0, test_utils_1.mount)(LessonUploadView_vue_1.default, { global: { plugins: [router], stubs: shellStub() } });
                    (0, vitest_1.expect)(wrapper.text()).toContain('重新上传教案后将开始新的解析');
                    (0, vitest_1.expect)(wrapper.get('[data-testid="lesson-upload-primary"]').attributes('disabled')).toBeDefined();
                    return [2 /*return*/];
            }
        });
    }); });
    (0, vitest_1.it)('maps each lesson plan status to one clear next action', function () { return __awaiter(void 0, void 0, void 0, function () {
        var router, wrapper, actions;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    listMine.mockResolvedValue([
                        { id: 1, title: '解析中的教案', parseStatus: 'processing', status: 'pending' },
                        { id: 2, title: '失败的教案', parseStatus: 'failed', status: 'pending' },
                        { id: 3, title: '待确认教案', parseStatus: 'success', status: 'pending' },
                        { id: 4, title: '已确认教案', parseStatus: 'success', status: 'confirmed' },
                    ]);
                    router = routerFor(LessonPlanHistoryView_vue_1.default, '/lesson-plans/history');
                    return [4 /*yield*/, router.push('/lesson-plans/history')];
                case 1:
                    _a.sent();
                    return [4 /*yield*/, router.isReady()];
                case 2:
                    _a.sent();
                    wrapper = (0, test_utils_1.mount)(LessonPlanHistoryView_vue_1.default, { global: { plugins: [router], stubs: shellStub() } });
                    return [4 /*yield*/, (0, test_utils_1.flushPromises)()];
                case 3:
                    _a.sent();
                    actions = wrapper.findAll('[data-testid="lesson-plan-next-action"]');
                    (0, vitest_1.expect)(actions.map(function (action) { return action.text(); })).toEqual(['查看解析进度', '重新上传并解析', '确认解析内容', '设置课堂']);
                    (0, vitest_1.expect)(actions.map(function (action) { return action.attributes('href'); })).toEqual([
                        '/lesson-plans/1/parse-result',
                        '/lesson-plans/upload?retryLessonPlanId=2',
                        '/lesson-plans/3/parse-result',
                        '/packages/generate?lessonPlanId=4',
                    ]);
                    return [2 /*return*/];
            }
        });
    }); });
});
