"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var vue_router_1 = require("vue-router");
var authStore_1 = require("../stores/authStore");
var router = (0, vue_router_1.createRouter)({
    history: (0, vue_router_1.createWebHistory)(),
    routes: [
        { path: '/', redirect: '/dashboard' },
        { path: '/login', component: function () { return Promise.resolve().then(function () { return require('../views/LoginView.vue'); }); }, meta: { public: true } },
        { path: '/dashboard', component: function () { return Promise.resolve().then(function () { return require('../views/DashboardView.vue'); }); } },
        { path: '/profile', component: function () { return Promise.resolve().then(function () { return require('../views/TeacherProfileView.vue'); }); } },
        { path: '/settings', component: function () { return Promise.resolve().then(function () { return require('../views/AccountSettingsView.vue'); }); } },
        { path: '/help', component: function () { return Promise.resolve().then(function () { return require('../views/HelpCenterView.vue'); }); } },
        { path: '/classes', component: function () { return Promise.resolve().then(function () { return require('../views/ClassListView.vue'); }); } },
        { path: '/classes/:classId', component: function () { return Promise.resolve().then(function () { return require('../views/ClassDetailView.vue'); }); } },
        { path: '/lesson-plans/upload', component: function () { return Promise.resolve().then(function () { return require('../views/LessonUploadView.vue'); }); } },
        { path: '/lesson-plans/history', component: function () { return Promise.resolve().then(function () { return require('../views/LessonPlanHistoryView.vue'); }); } },
        { path: '/lesson-plans/:lessonPlanId/parse-result', component: function () { return Promise.resolve().then(function () { return require('../views/LessonParseResultView.vue'); }); } },
        { path: '/packages/generate', component: function () { return Promise.resolve().then(function () { return require('../views/PackageGenerateView.vue'); }); } },
        { path: '/packages/:packageId/proposal', component: function () { return Promise.resolve().then(function () { return require('../views/ProposalCardView.vue'); }); } },
        { path: '/packages/:packageId', component: function () { return Promise.resolve().then(function () { return require('../views/PackageDetailView.vue'); }); } },
        { path: '/packages/:packageId/publish', component: function () { return Promise.resolve().then(function () { return require('../views/PublishPackageView.vue'); }); } },
        { path: '/classrooms', component: function () { return Promise.resolve().then(function () { return require('../views/ClassroomListView.vue'); }); } },
        { path: '/reports', component: function () { return Promise.resolve().then(function () { return require('../views/ReportCenterView.vue'); }); } },
        { path: '/classroom/:sessionId/control', component: function () { return Promise.resolve().then(function () { return require('../views/ClassroomControlView.vue'); }); } },
        { path: '/classroom/:sessionId/report', component: function () { return Promise.resolve().then(function () { return require('../views/ClassroomReportView.vue'); }); } },
        { path: '/packages/:packageId/edit', component: function () { return Promise.resolve().then(function () { return require('../views/PackageEditView.vue'); }); } },
    ],
});
router.beforeEach(function (to) {
    var auth = (0, authStore_1.useAuthStore)();
    if (!to.meta.public && !auth.isLoggedIn) {
        return { path: '/login', query: { redirect: to.fullPath } };
    }
});
exports.default = router;
