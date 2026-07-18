"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.presentLessonPlan = presentLessonPlan;
var MAX_ITEMS = 6;
var MAX_TEXT_LENGTH = 120;
var MAX_PARSED_JSON_LENGTH = 50000;
function isRecord(value) {
    return typeof value === 'object' && value !== null && !Array.isArray(value);
}
function asText(value) {
    return typeof value === 'string' ? value.replace(/\s+/g, ' ').trim().slice(0, MAX_TEXT_LENGTH) : '';
}
function asTextList(value) {
    var values = Array.isArray(value) ? value : typeof value === 'string' ? value.split(/[、,，；;]/) : [];
    return values.map(asText).filter(Boolean).slice(0, MAX_ITEMS);
}
function firstText(record, keys) {
    for (var _i = 0, keys_1 = keys; _i < keys_1.length; _i++) {
        var key = keys_1[_i];
        var text = asText(record[key]);
        if (text)
            return text;
    }
    return '';
}
function asProcess(value) {
    if (!Array.isArray(value))
        return [];
    return value.slice(0, MAX_ITEMS).flatMap(function (item) {
        if (!isRecord(item))
            return [];
        var title = firstText(item, ['title', 'name', 'step', 'content']);
        if (!title)
            return [];
        return [{ title: title, duration: firstText(item, ['duration', 'time', 'minutes']) }];
    });
}
function emptyPresentation(lessonPlan) {
    return {
        courseName: lessonPlan.courseName || lessonPlan.title,
        grade: lessonPlan.grade || '',
        objectives: [],
        keyPoints: [],
        process: [],
        musicElements: [],
    };
}
function presentLessonPlan(lessonPlan) {
    var _a, _b, _c, _d, _e, _f, _g, _h;
    var fallback = emptyPresentation(lessonPlan);
    if (!lessonPlan.parsedJson || lessonPlan.parsedJson.length > MAX_PARSED_JSON_LENGTH)
        return fallback;
    try {
        var parsed = JSON.parse(lessonPlan.parsedJson);
        if (!isRecord(parsed))
            return fallback;
        return {
            courseName: firstText(parsed, ['courseName', 'course_name', 'lessonName', 'title']) || fallback.courseName,
            grade: firstText(parsed, ['grade', 'gradeName', 'grade_name']) || fallback.grade,
            objectives: asTextList((_b = (_a = parsed.objectives) !== null && _a !== void 0 ? _a : parsed.teachingObjectives) !== null && _b !== void 0 ? _b : parsed.goals),
            keyPoints: asTextList((_d = (_c = parsed.keyPoints) !== null && _c !== void 0 ? _c : parsed.keyPointsAndDifficulties) !== null && _d !== void 0 ? _d : parsed.importantPoints),
            process: asProcess((_f = (_e = parsed.process) !== null && _e !== void 0 ? _e : parsed.teachingProcess) !== null && _f !== void 0 ? _f : parsed.steps),
            musicElements: asTextList((_h = (_g = parsed.musicElements) !== null && _g !== void 0 ? _g : parsed.musicElement) !== null && _h !== void 0 ? _h : parsed.elements),
        };
    }
    catch (_j) {
        return fallback;
    }
}
