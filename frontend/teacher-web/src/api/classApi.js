"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.classApi = void 0;
var request_1 = require("./request");
exports.classApi = {
    createClass: function (className, description) {
        if (description === void 0) { description = ''; }
        return (0, request_1.unwrap)(request_1.default.post('/classes', { className: className, description: description }));
    },
    listClasses: function () {
        return (0, request_1.unwrap)(request_1.default.get('/classes'));
    },
    joinClass: function (inviteCode) {
        return (0, request_1.unwrap)(request_1.default.post('/classes/join', { inviteCode: inviteCode }));
    },
    listStudents: function (classId) {
        return (0, request_1.unwrap)(request_1.default.get("/classes/".concat(classId, "/students")));
    },
};
