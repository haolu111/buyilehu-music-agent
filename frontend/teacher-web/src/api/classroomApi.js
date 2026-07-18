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
Object.defineProperty(exports, "__esModule", { value: true });
exports.classroomApi = void 0;
var request_1 = require("./request");
exports.classroomApi = {
    createSession: function (publicationId, payload) {
        if (payload === void 0) { payload = {}; }
        return (0, request_1.unwrap)(request_1.default.post('/classroom-sessions', __assign({ publicationId: publicationId }, payload)));
    },
    listActiveSessions: function () {
        return (0, request_1.unwrap)(request_1.default.get('/classroom-sessions/active'));
    },
    getSession: function (sessionId) {
        return (0, request_1.unwrap)(request_1.default.get("/classroom-sessions/".concat(sessionId)));
    },
    listSubmissions: function (sessionId) {
        return (0, request_1.unwrap)(request_1.default.get("/classroom-sessions/".concat(sessionId, "/submissions")));
    },
    start: function (sessionId) {
        return (0, request_1.unwrap)(request_1.default.post("/classroom-sessions/".concat(sessionId, "/start")));
    },
    unlockNode: function (sessionId, nodeId) {
        return (0, request_1.unwrap)(request_1.default.post("/classroom-sessions/".concat(sessionId, "/nodes/").concat(nodeId, "/unlock")));
    },
    pause: function (sessionId) {
        return (0, request_1.unwrap)(request_1.default.post("/classroom-sessions/".concat(sessionId, "/pause")));
    },
    end: function (sessionId) {
        return (0, request_1.unwrap)(request_1.default.post("/classroom-sessions/".concat(sessionId, "/end")));
    },
};
