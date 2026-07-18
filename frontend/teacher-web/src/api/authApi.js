"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.authApi = void 0;
var request_1 = require("./request");
exports.authApi = {
    login: function (username, password) {
        return (0, request_1.unwrap)(request_1.default.post('/auth/login', { username: username, password: password }));
    },
    me: function () {
        return (0, request_1.unwrap)(request_1.default.get('/auth/me'));
    },
};
