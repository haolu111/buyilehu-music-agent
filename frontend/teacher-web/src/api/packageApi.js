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
exports.packageApi = void 0;
var request_1 = require("./request");
var createIdempotencyKey = function () {
    var _a, _b, _c;
    return ((_c = (_b = (_a = globalThis.crypto) === null || _a === void 0 ? void 0 : _a.randomUUID) === null || _b === void 0 ? void 0 : _b.call(_a)) !== null && _c !== void 0 ? _c : "generation-".concat(Date.now(), "-").concat(Math.random().toString(36).slice(2)));
};
exports.packageApi = {
    createGenerationJob: function (lessonPlanId, preferences, idempotencyKey) {
        if (preferences === void 0) { preferences = {}; }
        if (idempotencyKey === void 0) { idempotencyKey = createIdempotencyKey(); }
        return (0, request_1.unwrap)(request_1.default.post('/generation-jobs', { lessonPlanId: lessonPlanId, preferences: preferences }, {
            headers: { 'Idempotency-Key': idempotencyKey },
            // Package generation performs both design and quality-audit model calls.
            timeout: 180000,
        }));
    },
    getGenerationJob: function (jobId) {
        return (0, request_1.unwrap)(request_1.default.get("/generation-jobs/".concat(jobId)));
    },
    watchGenerationJob: function (jobId, onStatus, onError) {
        var _this = this;
        var controller = new AbortController();
        var terminal = false;
        var waitToReconnect = function () { return new Promise(function (resolve) { return window.setTimeout(resolve, 1500); }); };
        var consume = function () { return __awaiter(_this, void 0, void 0, function () {
            var token, response, reader, decoder, buffer, _a, done, value, events, _i, events_1, event_1, data, status_1;
            return __generator(this, function (_b) {
                switch (_b.label) {
                    case 0:
                        token = localStorage.getItem('teacher_token');
                        return [4 /*yield*/, fetch("/api/v1/generation-jobs/".concat(jobId, "/events"), {
                                headers: __assign({ Accept: 'text/event-stream' }, (token ? { Authorization: "Bearer ".concat(token) } : {})),
                                signal: controller.signal,
                            })];
                    case 1:
                        response = _b.sent();
                        if (response.status === 401) {
                            localStorage.removeItem('teacher_token');
                            window.location.assign("/login?redirect=".concat(encodeURIComponent(window.location.pathname + window.location.search)));
                            return [2 /*return*/];
                        }
                        if (!response.ok || !response.body) {
                            throw new Error("\u72B6\u6001\u8BA2\u9605\u5931\u8D25 (".concat(response.status, ")"));
                        }
                        reader = response.body.getReader();
                        decoder = new TextDecoder();
                        buffer = '';
                        _b.label = 2;
                    case 2:
                        if (!(!terminal && !controller.signal.aborted)) return [3 /*break*/, 4];
                        return [4 /*yield*/, reader.read()];
                    case 3:
                        _a = _b.sent(), done = _a.done, value = _a.value;
                        if (done)
                            return [3 /*break*/, 4];
                        buffer += decoder.decode(value, { stream: true }).replace(/\r\n/g, '\n');
                        events = buffer.split('\n\n');
                        buffer = events.pop() || '';
                        for (_i = 0, events_1 = events; _i < events_1.length; _i++) {
                            event_1 = events_1[_i];
                            data = event_1.split('\n')
                                .filter(function (line) { return line.startsWith('data:'); })
                                .map(function (line) { return line.slice(5).trimStart(); })
                                .join('\n');
                            if (!data)
                                continue;
                            status_1 = JSON.parse(data);
                            terminal = status_1.status === 'success' || status_1.status === 'failed';
                            onStatus(status_1);
                        }
                        return [3 /*break*/, 2];
                    case 4: return [2 /*return*/];
                }
            });
        }); };
        void (function () { return __awaiter(_this, void 0, void 0, function () {
            var error_1, snapshot, _a;
            return __generator(this, function (_b) {
                switch (_b.label) {
                    case 0:
                        if (!(!terminal && !controller.signal.aborted)) return [3 /*break*/, 11];
                        _b.label = 1;
                    case 1:
                        _b.trys.push([1, 3, , 8]);
                        return [4 /*yield*/, consume()];
                    case 2:
                        _b.sent();
                        return [3 /*break*/, 8];
                    case 3:
                        error_1 = _b.sent();
                        if (controller.signal.aborted)
                            return [2 /*return*/];
                        _b.label = 4;
                    case 4:
                        _b.trys.push([4, 6, , 7]);
                        return [4 /*yield*/, exports.packageApi.getGenerationJob(jobId)];
                    case 5:
                        snapshot = _b.sent();
                        terminal = snapshot.status === 'success' || snapshot.status === 'failed';
                        onStatus(snapshot);
                        return [3 /*break*/, 7];
                    case 6:
                        _a = _b.sent();
                        onError(error_1 instanceof Error ? error_1 : new Error('生成状态连接已断开'));
                        return [3 /*break*/, 7];
                    case 7: return [3 /*break*/, 8];
                    case 8:
                        if (!(!terminal && !controller.signal.aborted)) return [3 /*break*/, 10];
                        return [4 /*yield*/, waitToReconnect()];
                    case 9:
                        _b.sent();
                        _b.label = 10;
                    case 10: return [3 /*break*/, 0];
                    case 11: return [2 /*return*/];
                }
            });
        }); })();
        return controller;
    },
    getProposal: function (packageId) {
        return (0, request_1.unwrap)(request_1.default.get("/packages/".concat(packageId, "/proposal")));
    },
    confirmProposal: function (packageId) {
        return (0, request_1.unwrap)(request_1.default.post("/packages/".concat(packageId, "/proposal/confirm")));
    },
    getPackage: function (packageId) {
        return (0, request_1.unwrap)(request_1.default.get("/packages/".concat(packageId)));
    },
    listPackages: function () {
        return (0, request_1.unwrap)(request_1.default.get('/packages'));
    },
    publishPackage: function (packageId, payload) {
        return (0, request_1.unwrap)(request_1.default.post("/packages/".concat(packageId, "/publish"), payload));
    },
    updateNodeConfig: function (packageId, nodeId, baseVersionId, payload) {
        return (0, request_1.unwrap)(request_1.default.patch("/packages/".concat(packageId, "/nodes/").concat(nodeId, "/config"), payload, {
            headers: { 'X-Package-Version': String(baseVersionId) },
        }));
    },
    modifyPackage: function (packageId, nodeId, baseVersionId, payload) {
        return (0, request_1.unwrap)(request_1.default.post("/packages/".concat(packageId, "/modify"), { nodeId: nodeId, baseVersionId: baseVersionId, config: payload }));
    },
    reviseNodeWithAgent: function (packageId, nodeId, baseVersionId, feedback) {
        return (0, request_1.unwrap)(request_1.default.post("/packages/".concat(packageId, "/modify"), {
            nodeId: nodeId,
            baseVersionId: baseVersionId,
            modifyType: 'agent_node_revision',
            feedback: feedback,
            config: {},
        }));
    },
    listVersions: function (packageId) {
        return (0, request_1.unwrap)(request_1.default.get("/packages/".concat(packageId, "/versions")));
    },
};
