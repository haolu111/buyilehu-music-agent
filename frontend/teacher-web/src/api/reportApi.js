"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.reportApi = void 0;
var request_1 = require("./request");
exports.reportApi = {
    getClassroomReport: function (sessionId) {
        return (0, request_1.unwrap)(request_1.default.get("/reports/classroom-sessions/".concat(sessionId)));
    },
};
