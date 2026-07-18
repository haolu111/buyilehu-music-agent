"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.lessonPlanApi = void 0;
var request_1 = require("./request");
exports.lessonPlanApi = {
    upload: function (file, title) {
        var formData = new FormData();
        formData.append('file', file);
        if (title) {
            formData.append('title', title);
        }
        return (0, request_1.unwrap)(request_1.default.post('/lesson-plans', formData));
    },
    getLessonPlan: function (lessonPlanId) {
        return (0, request_1.unwrap)(request_1.default.get("/lesson-plans/".concat(lessonPlanId)));
    },
    listMine: function () {
        return (0, request_1.unwrap)(request_1.default.get('/lesson-plans/mine'));
    },
};
