"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var vitest_1 = require("vitest");
var lessonPlanPresentation_1 = require("./lessonPlanPresentation");
(0, vitest_1.describe)('presentLessonPlan', function () {
    (0, vitest_1.it)('maps parsed lesson data into a bounded teacher-facing summary', function () {
        var lessonPlan = {
            id: 8,
            title: '小星星',
            parsedJson: JSON.stringify({
                courseName: '闪烁的小星',
                grade: '一年级',
                objectives: ['能跟唱旋律', '感受四分音符'],
                keyPoints: ['稳定节拍'],
                process: [{ title: '律动导入', duration: '5分钟' }],
                musicElements: ['旋律', '节拍'],
            }),
        };
        (0, vitest_1.expect)((0, lessonPlanPresentation_1.presentLessonPlan)(lessonPlan)).toEqual({
            courseName: '闪烁的小星',
            grade: '一年级',
            objectives: ['能跟唱旋律', '感受四分音符'],
            keyPoints: ['稳定节拍'],
            process: [{ title: '律动导入', duration: '5分钟' }],
            musicElements: ['旋律', '节拍'],
        });
    });
    (0, vitest_1.it)('falls back to safe empty fields when parsed JSON is absent or invalid', function () {
        var lessonPlan = { id: 8, title: '春天在哪里', parsedJson: '{not json' };
        (0, vitest_1.expect)((0, lessonPlanPresentation_1.presentLessonPlan)(lessonPlan)).toEqual({
            courseName: '春天在哪里',
            grade: '',
            objectives: [],
            keyPoints: [],
            process: [],
            musicElements: [],
        });
    });
    (0, vitest_1.it)('bounds every summary field and list while preserving readable values', function () {
        var longText = '节'.repeat(160);
        var lessonPlan = {
            id: 9,
            title: '边界教案',
            parsedJson: JSON.stringify({
                courseName: longText,
                grade: longText,
                objectives: Array.from({ length: 8 }, function () { return longText; }),
                keyPoints: Array.from({ length: 8 }, function () { return longText; }),
                musicElements: Array.from({ length: 8 }, function () { return longText; }),
                process: Array.from({ length: 8 }, function () { return ({ title: longText, duration: longText }); }),
            }),
        };
        var summary = (0, lessonPlanPresentation_1.presentLessonPlan)(lessonPlan);
        (0, vitest_1.expect)(summary.courseName).toHaveLength(120);
        (0, vitest_1.expect)(summary.grade).toHaveLength(120);
        (0, vitest_1.expect)(summary.objectives).toHaveLength(6);
        (0, vitest_1.expect)(summary.keyPoints).toHaveLength(6);
        (0, vitest_1.expect)(summary.musicElements).toHaveLength(6);
        (0, vitest_1.expect)(summary.process).toHaveLength(6);
        (0, vitest_1.expect)(summary.objectives[0]).toHaveLength(120);
        (0, vitest_1.expect)(summary.process[0]).toEqual({ title: longText.slice(0, 120), duration: longText.slice(0, 120) });
    });
    (0, vitest_1.it)('does not parse oversized raw JSON', function () {
        var parse = vitest_1.vi.spyOn(JSON, 'parse');
        var lessonPlan = { id: 10, title: '安全教案', parsedJson: "{\"courseName\":\"".concat('节'.repeat(100000), "\"}") };
        (0, vitest_1.expect)((0, lessonPlanPresentation_1.presentLessonPlan)(lessonPlan)).toMatchObject({ courseName: '安全教案' });
        (0, vitest_1.expect)(parse).not.toHaveBeenCalled();
    });
});
