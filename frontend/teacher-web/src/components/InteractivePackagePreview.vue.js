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
var __spreadArray = (this && this.__spreadArray) || function (to, from, pack) {
    if (pack || arguments.length === 2) for (var i = 0, l = from.length, ar; i < l; i++) {
        if (ar || !(i in from)) {
            if (!ar) ar = Array.prototype.slice.call(from, 0, i);
            ar[i] = from[i];
        }
    }
    return to.concat(ar || Array.prototype.slice.call(from));
};
Object.defineProperty(exports, "__esModule", { value: true });
/* placeholder */
var vue_1 = require("vue");
var reviewedActivityFrame_1 = require("../../../shared-activity-runtime/reviewedActivityFrame");
var props = defineProps();
(0, reviewedActivityFrame_1.registerReviewedActivityElement)();
var emit = defineEmits();
var previewIndex = (0, vue_1.ref)(0);
var testResult = (0, vue_1.ref)('');
var sequence = (0, vue_1.ref)([]);
var selectedRole = (0, vue_1.ref)('');
var completedSteps = (0, vue_1.ref)([]);
var explanation = (0, vue_1.ref)('');
var rhythmSubmitted = (0, vue_1.ref)(false);
var rhythmPlaying = (0, vue_1.ref)(false);
var visibleNodes = (0, vue_1.computed)(function () { return props.nodes.filter(function (node) { return !parseConfig(node).hidden; }); });
var activeNode = (0, vue_1.computed)(function () {
    if (props.mode === 'single' && props.selectedNodeId) {
        return props.nodes.find(function (node) { return node.id === props.selectedNodeId; }) || null;
    }
    return visibleNodes.value[previewIndex.value] || null;
});
var runtime = (0, vue_1.computed)(function () { return parseConfig(activeNode.value).activityRuntime || {}; });
var nodeConfig = (0, vue_1.computed)(function () { return parseConfig(activeNode.value); });
var runtimeProps = (0, vue_1.computed)(function () {
    var _a, _b, _c, _d, _e, _f, _g, _h;
    var value = __assign({}, (runtime.value.props || {}));
    if (((_a = activeNode.value) === null || _a === void 0 ? void 0 : _a.id) !== props.selectedNodeId || !((_b = props.draft) === null || _b === void 0 ? void 0 : _b.resolvedMusicContent))
        return value;
    var content = props.draft.resolvedMusicContent;
    value.musicContent = content;
    if ((_c = content.rhythm_patterns) === null || _c === void 0 ? void 0 : _c.length) {
        value.rhythmPatterns = content.rhythm_patterns;
        value.targetSequence = content.rhythm_patterns.flatMap(function (item) { return item.tokens || []; });
    }
    if ((_d = content.pitch_sets) === null || _d === void 0 ? void 0 : _d.length) {
        value.pitchSets = content.pitch_sets;
        value.tokens = content.pitch_sets[0].notes || [];
    }
    if ((_e = content.melody_phrases) === null || _e === void 0 ? void 0 : _e.length) {
        value.melodyPhrases = content.melody_phrases;
        value.notes = content.melody_phrases[0].contour || content.melody_phrases[0].notes || [];
    }
    if ((_f = content.forms) === null || _f === void 0 ? void 0 : _f.length) {
        value.forms = content.forms;
        value.sections = content.forms[0].sections || [];
    }
    if ((_g = content.dynamics) === null || _g === void 0 ? void 0 : _g.length)
        value.dynamics = content.dynamics;
    if ((_h = content.timbres) === null || _h === void 0 ? void 0 : _h.length) {
        value.timbres = content.timbres;
        value.items = content.timbres.map(function (item) { return item.label; });
        value.instrument = content.timbres[0].instrument;
    }
    return value;
});
var renderer = (0, vue_1.computed)(function () { var _a; return runtime.value.renderer || fallbackRenderer(((_a = activeNode.value) === null || _a === void 0 ? void 0 : _a.nodeType) || ''); });
var legacyRenderer = (0, vue_1.computed)(function () { return runtime.value.legacyRenderer || renderer.value; });
var displayTitle = (0, vue_1.computed)(function () {
    var _a, _b, _c;
    return ((_a = activeNode.value) === null || _a === void 0 ? void 0 : _a.id) === props.selectedNodeId && ((_b = props.draft) === null || _b === void 0 ? void 0 : _b.title)
        ? props.draft.title
        : ((_c = activeNode.value) === null || _c === void 0 ? void 0 : _c.title) || '未选择活动';
});
var displayPrompt = (0, vue_1.computed)(function () {
    var _a, _b;
    return translateText(((_a = activeNode.value) === null || _a === void 0 ? void 0 : _a.id) === props.selectedNodeId && ((_b = props.draft) === null || _b === void 0 ? void 0 : _b.description)
        ? props.draft.description
        : nodeConfig.value.recommendationReason || runtimeProps.value.prompt || defaultPrompt(renderer.value));
});
var rhythmCount = (0, vue_1.computed)(function () {
    var _a, _b;
    return ((_a = activeNode.value) === null || _a === void 0 ? void 0 : _a.id) === props.selectedNodeId && ((_b = props.draft) === null || _b === void 0 ? void 0 : _b.rhythmCardCount) != null
        ? props.draft.rhythmCardCount
        : runtimeProps.value.maxBeats || 4;
});
var rhythmTarget = (0, vue_1.computed)(function () {
    var configured = runtimeProps.value.targetSequence;
    var source = Array.isArray(configured) && configured.length
        ? configured.map(String)
        : ['ta', 'ti-ti', 'ta', 'rest'];
    return source.slice(0, rhythmCount.value);
});
var rhythmCorrect = (0, vue_1.computed)(function () {
    return sequence.value.length === rhythmTarget.value.length
        && sequence.value.every(function (token, index) { return token === rhythmTarget.value[index]; });
});
var virtualInstrumentUrl = (0, vue_1.computed)(function () {
    var _a, _b;
    var task = runtimeProps.value.task || {};
    var keys = Array.isArray(runtimeProps.value.keys) ? runtimeProps.value.keys : [];
    var instrumentId = runtimeProps.value.instrumentId
        || task.instrumentId
        || ((_a = runtimeProps.value.instrument) === null || _a === void 0 ? void 0 : _a.id)
        || ((_b = runtimeProps.value.instrument) === null || _b === void 0 ? void 0 : _b.instrumentId)
        || (runtimeProps.value.activityId === 'xylophone_creation' ? 'virtual_xylophone' : null)
        || (/melody|pitch|keyboard|piano/.test(String(runtimeProps.value.activityId || '')) ? 'virtual_piano' : null)
        || (keys.some(function (key) { return String(key.zoneId || '').match(/center|edge/); }) ? 'virtual_frame_drum' : null)
        || (keys.some(function (key) { return Number.isFinite(key.midi); }) ? 'virtual_piano' : null)
        || 'virtual_frame_drum';
    var bytes = new TextEncoder().encode(JSON.stringify({
        instrumentId: instrumentId,
        prompt: displayPrompt.value,
        task: task,
    }));
    var binary = '';
    bytes.forEach(function (byte) { binary += String.fromCharCode(byte); });
    var encoded = btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
    return "/template-console/virtual-instrument-player.html?config=".concat(encodeURIComponent(encoded));
});
var metaLabels = (0, vue_1.computed)(function () {
    var _a;
    return [
        nodeTypeLabel(runtime.value.nodeType || ((_a = activeNode.value) === null || _a === void 0 ? void 0 : _a.nodeType) || ''),
        runtime.value.family
            ? "".concat(familyLabel(runtime.value.family), " \u00B7 ").concat(variantLabel(runtime.value.variant || ''))
            : '',
        rendererLabel(renderer.value),
    ].filter(Boolean);
});
(0, vue_1.watch)(activeNode, resetTest);
function parseConfig(node) {
    if (!(node === null || node === void 0 ? void 0 : node.configJson))
        return {};
    try {
        return JSON.parse(node.configJson);
    }
    catch (_a) {
        return {};
    }
}
function fallbackRenderer(type) {
    if (type.includes('summary'))
        return 'summary';
    if (type.includes('creation'))
        return 'creation-panel';
    if (type === 'instrument_task' || type.includes('instrument'))
        return 'virtual-instrument';
    if (type === 'game' || type.includes('rhythm'))
        return 'rhythm-drag';
    if (type.includes('singing'))
        return 'singing-practice';
    if (type.includes('ensemble'))
        return 'ensemble-roles';
    return 'completion';
}
function resetTest() {
    testResult.value = '';
    sequence.value = [];
    selectedRole.value = '';
    completedSteps.value = [];
    explanation.value = '';
    rhythmSubmitted.value = false;
    rhythmPlaying.value = false;
}
function choose(value) { testResult.value = "\u5DF2\u9009\u62E9\uFF1A".concat(translateText(String(value))); }
function add(value) {
    if (renderer.value === 'rhythm-drag' && sequence.value.length >= rhythmTarget.value.length)
        return;
    rhythmSubmitted.value = false;
    sequence.value.push(String(value));
    testResult.value = "\u5F53\u524D\u7ED3\u679C\uFF1A".concat(sequence.value.map(translateText).join(' · '));
}
function rhythmLabel(value) {
    if (value === 'ta')
        return '♩ 四分音符（1拍）';
    if (value === 'ti-ti')
        return '♫ 两个八分音符（1拍）';
    if (value === 'rest')
        return '𝄽 四分休止（1拍）';
    return translateText(value);
}
function playRhythmTarget() {
    if (rhythmPlaying.value)
        return;
    var AudioContextClass = window.AudioContext;
    if (!AudioContextClass)
        return;
    var context = new AudioContextClass();
    void context.resume();
    rhythmPlaying.value = true;
    rhythmTarget.value.forEach(function (token, beatIndex) {
        if (token === 'rest')
            return;
        var hits = token === 'ti-ti' ? 2 : 1;
        for (var hit = 0; hit < hits; hit += 1) {
            var start = context.currentTime + .05 + beatIndex * .56 + hit * .56 / hits;
            var oscillator = context.createOscillator();
            var gain = context.createGain();
            oscillator.type = 'square';
            oscillator.frequency.value = 196;
            gain.gain.setValueAtTime(.14, start);
            gain.gain.exponentialRampToValueAtTime(.001, start + .09);
            oscillator.connect(gain).connect(context.destination);
            oscillator.start(start);
            oscillator.stop(start + .1);
        }
    });
    window.setTimeout(function () { rhythmPlaying.value = false; void context.close(); }, rhythmTarget.value.length * 560 + 200);
}
function undoRhythm() { rhythmSubmitted.value = false; sequence.value.pop(); testResult.value = ''; }
function clearRhythm() { rhythmSubmitted.value = false; sequence.value = []; testResult.value = ''; }
function submitRhythm() {
    rhythmSubmitted.value = true;
    testResult.value = rhythmCorrect.value
        ? '完全正确！已准确还原目标节奏。'
        : '还不完全正确：红色拍位需要修改，可以重新播放目标节奏。';
}
function toggleStep(step) {
    completedSteps.value = completedSteps.value.includes(step)
        ? completedSteps.value.filter(function (item) { return item !== step; })
        : __spreadArray(__spreadArray([], completedSteps.value, true), [step], false);
    testResult.value = "\u5DF2\u5B8C\u6210 ".concat(completedSteps.value.length, " \u4E2A\u6392\u7EC3\u6B65\u9AA4");
}
function previous() { previewIndex.value = Math.max(0, previewIndex.value - 1); }
function next() { previewIndex.value = Math.min(visibleNodes.value.length - 1, previewIndex.value + 1); }
function finish(message) {
    if (message === void 0) { message = '试玩操作正常，实际课堂中将记录学生提交。'; }
    testResult.value = message;
}
var translations = {
    listen: '聆听', choose: '选择', explain: '说明理由', assess: '评价',
    perform: '表演', cooperate: '合作', create: '创编', revise: '修改',
    tap: '拍击', move: '律动', sing: '演唱', read: '朗读', play: '演奏',
    activity: '教学活动', game: '音乐游戏', instrument_task: '虚拟乐器任务',
    beat_rhythm: '节拍与节奏', lyrics_rhythm: '歌词节奏', phrase_singing: '乐句学唱',
    pitch_score: '音高与谱面', guided_listening: '引导聆听', music_structure: '音乐结构',
    music_creation: '音乐创编', ensemble: '合奏与排练',
    performance_reflection: '展示与反思', virtual_instrument: '虚拟乐器',
    peer_feedback: '同伴评价', exit_ticket: '课堂回顾', phrase_loop: '分句循环',
    whole_phrase: '完整乐句', steady_beat: '稳定拍', melody_sequence: '旋律序列',
    rhythm_echo: '节奏模仿', orff_percussion: '奥尔夫打击乐', band_roles: '小乐队分声部',
    relay_performance: '小组接力展示', conductor_rehearsal: '多声部排练与指挥',
};
function translateText(value) {
    var result = value;
    Object.entries(translations).forEach(function (_a) {
        var key = _a[0], label = _a[1];
        result = result.replace(new RegExp("\\b".concat(key, "\\b"), 'gi'), label);
    });
    return result.replace(/_/g, ' ');
}
function nodeTypeLabel(value) {
    var map = {
        activity: '教学活动', game: '音乐游戏', instrument_task: '虚拟乐器任务',
        entry: '课堂导入', listening_activity: '聆听活动', rhythm_game: '节奏活动',
        meter_experience: '节拍体验', singing_practice: '演唱练习',
        creation_workshop: '音乐创编', melody_activity: '旋律活动',
        timbre_activity: '音色活动', form_activity: '曲式活动',
        instrument_activity: '虚拟乐器', ensemble_activity: '合奏活动', summary: '课堂总结',
    };
    return map[value] || translateText(value);
}
function familyLabel(value) { return translations[value] || translateText(value); }
function variantLabel(value) { return translations[value] || translateText(value); }
function rendererLabel(value) {
    var map = {
        'meter-compare': '节拍比较', 'rhythm-drag': '节奏卡编排',
        'creation-panel': '音乐创编', summary: '课堂总结',
        'singing-practice': '乐句跟唱', 'listening-choice': '聆听选择',
        'solfege-sort': '唱名排序', 'melody-trace': '旋律线描画',
        'timbre-match': '音色配对', 'form-order': '曲式排序',
        'virtual-instrument': '虚拟乐器演奏', 'ensemble-roles': '分声部排练',
        completion: '活动完成',
    };
    return map[value] || translateText(value);
}
function defaultPrompt(value) {
    var map = {
        'meter-compare': '聆听并比较不同拍号的强弱规律。',
        'rhythm-drag': '选择节奏卡，完成目标节奏。',
        'creation-panel': '根据课堂要求完成一段音乐创编。',
        summary: '回顾本课学习内容，并说明自己的音乐发现。',
        'singing-practice': '先听示范，再逐句跟唱。',
        'listening-choice': '聆听音乐，选择感受并说明音乐依据。',
        'solfege-sort': '聆听并按正确顺序排列唱名。',
        'melody-trace': '聆听旋律，描画音高走向。',
        'timbre-match': '聆听音色，将乐器与类别配对。',
        'form-order': '聆听段落，排列曲式结构。',
        'virtual-instrument': '使用虚拟乐器完成指定演奏任务。',
        'ensemble-roles': '选择声部并完成分组排练。',
    };
    return map[value] || '按要求完成当前音乐活动。';
}
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
var __VLS_ctx = {};
var __VLS_components;
var __VLS_directives;
/** @type {__VLS_StyleScopedClasses['virtual-instrument-preview']} */ ;
/** @type {__VLS_StyleScopedClasses['rhythm-heading']} */ ;
/** @type {__VLS_StyleScopedClasses['rhythm-progress']} */ ;
/** @type {__VLS_StyleScopedClasses['rhythm-answer']} */ ;
/** @type {__VLS_StyleScopedClasses['rhythm-answer']} */ ;
/** @type {__VLS_StyleScopedClasses['rhythm-answer']} */ ;
/** @type {__VLS_StyleScopedClasses['rhythm-answer']} */ ;
/** @type {__VLS_StyleScopedClasses['rhythm-answer']} */ ;
/** @type {__VLS_StyleScopedClasses['rhythm-answer']} */ ;
/** @type {__VLS_StyleScopedClasses['rhythm-answer']} */ ;
/** @type {__VLS_StyleScopedClasses['rhythm-actions']} */ ;
/** @type {__VLS_StyleScopedClasses['virtual-instrument-preview']} */ ;
// CSS variable injection 
// CSS variable injection end 
__VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)(__assign({ class: "package-preview" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.header, __VLS_intrinsicElements.header)(__assign({ class: "preview-toolbar" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)(__assign({ class: "tag" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.h2, __VLS_intrinsicElements.h2)({});
(__VLS_ctx.displayTitle);
__VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
(__VLS_ctx.displayPrompt);
__VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign(__assign({ onClick: (__VLS_ctx.resetTest) }, { class: "button" }), { type: "button" }));
if (__VLS_ctx.mode === 'package') {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "preview-flow" }));
    var _loop_1 = function (node, index) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign(__assign({ onClick: function () {
                var _a = [];
                for (var _i = 0; _i < arguments.length; _i++) {
                    _a[_i] = arguments[_i];
                }
                var $event = _a[0];
                if (!(__VLS_ctx.mode === 'package'))
                    return;
                __VLS_ctx.previewIndex = index;
                __VLS_ctx.emit('select', node.id);
            } }, { key: (node.id), type: "button" }), { class: ({ active: index === __VLS_ctx.previewIndex }) }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
        (index + 1);
        (node.title);
    };
    for (var _i = 0, _a = __VLS_getVForSourceType((__VLS_ctx.visibleNodes)); _i < _a.length; _i++) {
        var _b = _a[_i], node = _b[0], index = _b[1];
        _loop_1(node, index);
    }
}
if (__VLS_ctx.activeNode) {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "preview-device" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "preview-meta" }));
    for (var _c = 0, _d = __VLS_getVForSourceType((__VLS_ctx.metaLabels)); _c < _d.length; _c++) {
        var label = _d[_c][0];
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
            key: (label),
        });
        (label);
    }
    if (__VLS_ctx.runtime.componentUrl) {
        var __VLS_0 = {}.BuyilehuReviewedActivity;
        /** @type {[typeof __VLS_components.BuyilehuReviewedActivity, typeof __VLS_components.buyilehuReviewedActivity, ]} */ ;
        // @ts-ignore
        var __VLS_1 = __VLS_asFunctionalComponent(__VLS_0, new __VLS_0({
            url: (__VLS_ctx.runtime.componentUrl),
            title: (__VLS_ctx.displayTitle),
            config: (__VLS_ctx.runtimeProps),
        }));
        var __VLS_2 = __VLS_1.apply(void 0, __spreadArray([{
                url: (__VLS_ctx.runtime.componentUrl),
                title: (__VLS_ctx.displayTitle),
                config: (__VLS_ctx.runtimeProps),
            }], __VLS_functionalComponentArgsRest(__VLS_1), false));
    }
    else if (__VLS_ctx.legacyRenderer === 'meter-compare') {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "preview-interaction" }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "preview-buttons" }));
        var _loop_2 = function (meter) {
            __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign({ onClick: function () {
                    var _a = [];
                    for (var _i = 0; _i < arguments.length; _i++) {
                        _a[_i] = arguments[_i];
                    }
                    var $event = _a[0];
                    if (!(__VLS_ctx.activeNode))
                        return;
                    if (!!(__VLS_ctx.runtime.componentUrl))
                        return;
                    if (!(__VLS_ctx.legacyRenderer === 'meter-compare'))
                        return;
                    __VLS_ctx.choose("".concat(meter, " \u62CD"));
                } }, { key: (meter), type: "button" }));
            (meter);
        };
        for (var _e = 0, _f = __VLS_getVForSourceType((__VLS_ctx.runtimeProps.meters || ['2/4', '3/4'])); _e < _f.length; _e++) {
            var meter = _f[_e][0];
            _loop_2(meter);
        }
        __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign({ onClick: function () {
                var _a = [];
                for (var _i = 0; _i < arguments.length; _i++) {
                    _a[_i] = arguments[_i];
                }
                var $event = _a[0];
                if (!(__VLS_ctx.activeNode))
                    return;
                if (!!(__VLS_ctx.runtime.componentUrl))
                    return;
                if (!(__VLS_ctx.legacyRenderer === 'meter-compare'))
                    return;
                __VLS_ctx.add('强拍');
            } }, { type: "button" }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign({ onClick: function () {
                var _a = [];
                for (var _i = 0; _i < arguments.length; _i++) {
                    _a[_i] = arguments[_i];
                }
                var $event = _a[0];
                if (!(__VLS_ctx.activeNode))
                    return;
                if (!!(__VLS_ctx.runtime.componentUrl))
                    return;
                if (!(__VLS_ctx.legacyRenderer === 'meter-compare'))
                    return;
                __VLS_ctx.add('弱拍');
            } }, { type: "button" }));
    }
    else if (__VLS_ctx.legacyRenderer === 'rhythm-drag') {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "preview-interaction" }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "rhythm-heading" }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
        __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
        __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
        __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign(__assign({ onClick: (__VLS_ctx.playRhythmTarget) }, { class: "button primary" }), { type: "button", disabled: (__VLS_ctx.rhythmPlaying) }));
        (__VLS_ctx.rhythmPlaying ? '正在播放…' : '▶ 播放目标节奏');
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "preview-buttons" }));
        var _loop_3 = function (card) {
            __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign({ onClick: function () {
                    var _a = [];
                    for (var _i = 0; _i < arguments.length; _i++) {
                        _a[_i] = arguments[_i];
                    }
                    var $event = _a[0];
                    if (!(__VLS_ctx.activeNode))
                        return;
                    if (!!(__VLS_ctx.runtime.componentUrl))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'meter-compare'))
                        return;
                    if (!(__VLS_ctx.legacyRenderer === 'rhythm-drag'))
                        return;
                    __VLS_ctx.add(card.name);
                } }, { key: (card.name), type: "button" }));
            (__VLS_ctx.rhythmLabel(card.name));
        };
        for (var _g = 0, _h = __VLS_getVForSourceType((__VLS_ctx.runtimeProps.cards || [{ name: 'ta' }, { name: 'ti-ti' }, { name: 'rest' }])); _g < _h.length; _g++) {
            var card = _h[_g][0];
            _loop_3(card);
        }
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "rhythm-progress" }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.strong, __VLS_intrinsicElements.strong)({});
        __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
        (__VLS_ctx.sequence.length);
        (__VLS_ctx.rhythmTarget.length);
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "rhythm-answer" }));
        var _loop_4 = function (token, index) {
            __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign(__assign({ onClick: function () {
                    var _a = [];
                    for (var _i = 0; _i < arguments.length; _i++) {
                        _a[_i] = arguments[_i];
                    }
                    var $event = _a[0];
                    if (!(__VLS_ctx.activeNode))
                        return;
                    if (!!(__VLS_ctx.runtime.componentUrl))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'meter-compare'))
                        return;
                    if (!(__VLS_ctx.legacyRenderer === 'rhythm-drag'))
                        return;
                    __VLS_ctx.sequence.splice(index, 1);
                    __VLS_ctx.rhythmSubmitted = false;
                } }, { key: ("".concat(token, "-").concat(index)), type: "button" }), { class: ({ correct: __VLS_ctx.rhythmSubmitted && token === __VLS_ctx.rhythmTarget[index], wrong: __VLS_ctx.rhythmSubmitted && token !== __VLS_ctx.rhythmTarget[index] }) }));
            __VLS_asFunctionalElement(__VLS_intrinsicElements.small, __VLS_intrinsicElements.small)({});
            (index + 1);
            (__VLS_ctx.rhythmLabel(token));
        };
        for (var _j = 0, _k = __VLS_getVForSourceType((__VLS_ctx.sequence)); _j < _k.length; _j++) {
            var _l = _k[_j], token = _l[0], index = _l[1];
            _loop_4(token, index);
        }
        for (var _m = 0, _o = __VLS_getVForSourceType((__VLS_ctx.rhythmTarget.length - __VLS_ctx.sequence.length)); _m < _o.length; _m++) {
            var slot = _o[_m][0];
            __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({
                key: (slot),
            });
            (__VLS_ctx.sequence.length + slot);
        }
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "rhythm-actions" }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign(__assign({ onClick: (__VLS_ctx.undoRhythm) }, { class: "button" }), { type: "button", disabled: (!__VLS_ctx.sequence.length) }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign(__assign({ onClick: (__VLS_ctx.clearRhythm) }, { class: "button" }), { type: "button", disabled: (!__VLS_ctx.sequence.length) }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign(__assign({ onClick: (__VLS_ctx.submitRhythm) }, { class: "button primary" }), { type: "button", disabled: (__VLS_ctx.sequence.length !== __VLS_ctx.rhythmTarget.length) }));
    }
    else if (__VLS_ctx.legacyRenderer === 'virtual-instrument') {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "preview-interaction virtual-instrument-preview" }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.iframe)({
            src: (__VLS_ctx.virtualInstrumentUrl),
            title: "虚拟乐器课堂预览",
            allow: "autoplay",
        });
    }
    else if (__VLS_ctx.legacyRenderer === 'listening-choice') {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "preview-interaction" }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "preview-buttons" }));
        var _loop_5 = function (option) {
            __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign({ onClick: function () {
                    var _a = [];
                    for (var _i = 0; _i < arguments.length; _i++) {
                        _a[_i] = arguments[_i];
                    }
                    var $event = _a[0];
                    if (!(__VLS_ctx.activeNode))
                        return;
                    if (!!(__VLS_ctx.runtime.componentUrl))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'meter-compare'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'rhythm-drag'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'virtual-instrument'))
                        return;
                    if (!(__VLS_ctx.legacyRenderer === 'listening-choice'))
                        return;
                    __VLS_ctx.choose(option);
                } }, { key: (option), type: "button" }));
            (__VLS_ctx.translateText(option));
        };
        for (var _p = 0, _q = __VLS_getVForSourceType((__VLS_ctx.runtimeProps.options || ['欢快', '安静', '优美'])); _p < _q.length; _p++) {
            var option = _q[_p][0];
            _loop_5(option);
        }
        __VLS_asFunctionalElement(__VLS_intrinsicElements.textarea, __VLS_intrinsicElements.textarea)({
            value: (__VLS_ctx.explanation),
            placeholder: "写一句音乐依据，例如：速度较快、力度较强",
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign(__assign({ onClick: function () {
                var _a = [];
                for (var _i = 0; _i < arguments.length; _i++) {
                    _a[_i] = arguments[_i];
                }
                var $event = _a[0];
                if (!(__VLS_ctx.activeNode))
                    return;
                if (!!(__VLS_ctx.runtime.componentUrl))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'meter-compare'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'rhythm-drag'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'virtual-instrument'))
                    return;
                if (!(__VLS_ctx.legacyRenderer === 'listening-choice'))
                    return;
                __VLS_ctx.finish('聆听选择和理由可以正常提交。');
            } }, { class: "button primary" }), { type: "button" }));
    }
    else if (__VLS_ctx.legacyRenderer === 'singing-practice') {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "preview-interaction" }));
        for (var _r = 0, _s = __VLS_getVForSourceType((__VLS_ctx.runtimeProps.phrases || ['第一乐句', '第二乐句'])); _r < _s.length; _r++) {
            var phrase = _s[_r][0];
            __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({
                key: (phrase),
            });
            (__VLS_ctx.translateText(phrase));
        }
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "preview-buttons" }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign({ onClick: function () {
                var _a = [];
                for (var _i = 0; _i < arguments.length; _i++) {
                    _a[_i] = arguments[_i];
                }
                var $event = _a[0];
                if (!(__VLS_ctx.activeNode))
                    return;
                if (!!(__VLS_ctx.runtime.componentUrl))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'meter-compare'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'rhythm-drag'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'virtual-instrument'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'listening-choice'))
                    return;
                if (!(__VLS_ctx.legacyRenderer === 'singing-practice'))
                    return;
                __VLS_ctx.finish('示范乐句已播放。');
            } }, { type: "button" }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign({ onClick: function () {
                var _a = [];
                for (var _i = 0; _i < arguments.length; _i++) {
                    _a[_i] = arguments[_i];
                }
                var $event = _a[0];
                if (!(__VLS_ctx.activeNode))
                    return;
                if (!!(__VLS_ctx.runtime.componentUrl))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'meter-compare'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'rhythm-drag'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'virtual-instrument'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'listening-choice'))
                    return;
                if (!(__VLS_ctx.legacyRenderer === 'singing-practice'))
                    return;
                __VLS_ctx.finish('已模拟完成一次跟唱录音。');
            } }, { type: "button" }));
    }
    else if (__VLS_ctx.legacyRenderer === 'solfege-sort') {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "preview-interaction" }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "preview-buttons" }));
        var _loop_6 = function (token) {
            __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign({ onClick: function () {
                    var _a = [];
                    for (var _i = 0; _i < arguments.length; _i++) {
                        _a[_i] = arguments[_i];
                    }
                    var $event = _a[0];
                    if (!(__VLS_ctx.activeNode))
                        return;
                    if (!!(__VLS_ctx.runtime.componentUrl))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'meter-compare'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'rhythm-drag'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'virtual-instrument'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'listening-choice'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'singing-practice'))
                        return;
                    if (!(__VLS_ctx.legacyRenderer === 'solfege-sort'))
                        return;
                    __VLS_ctx.add(token);
                } }, { key: (token), type: "button" }));
            (token);
        };
        for (var _t = 0, _u = __VLS_getVForSourceType((__VLS_ctx.runtimeProps.tokens || ['do', 're', 'mi', 'sol'])); _t < _u.length; _t++) {
            var token = _u[_t][0];
            _loop_6(token);
        }
        __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign(__assign({ onClick: function () {
                var _a = [];
                for (var _i = 0; _i < arguments.length; _i++) {
                    _a[_i] = arguments[_i];
                }
                var $event = _a[0];
                if (!(__VLS_ctx.activeNode))
                    return;
                if (!!(__VLS_ctx.runtime.componentUrl))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'meter-compare'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'rhythm-drag'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'virtual-instrument'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'listening-choice'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'singing-practice'))
                    return;
                if (!(__VLS_ctx.legacyRenderer === 'solfege-sort'))
                    return;
                __VLS_ctx.finish('唱名顺序可以正常提交。');
            } }, { class: "button primary" }), { type: "button" }));
    }
    else if (__VLS_ctx.legacyRenderer === 'melody-trace') {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "preview-interaction" }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "preview-buttons" }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign({ onClick: function () {
                var _a = [];
                for (var _i = 0; _i < arguments.length; _i++) {
                    _a[_i] = arguments[_i];
                }
                var $event = _a[0];
                if (!(__VLS_ctx.activeNode))
                    return;
                if (!!(__VLS_ctx.runtime.componentUrl))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'meter-compare'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'rhythm-drag'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'virtual-instrument'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'listening-choice'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'singing-practice'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'solfege-sort'))
                    return;
                if (!(__VLS_ctx.legacyRenderer === 'melody-trace'))
                    return;
                __VLS_ctx.add('上行');
            } }, { type: "button" }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign({ onClick: function () {
                var _a = [];
                for (var _i = 0; _i < arguments.length; _i++) {
                    _a[_i] = arguments[_i];
                }
                var $event = _a[0];
                if (!(__VLS_ctx.activeNode))
                    return;
                if (!!(__VLS_ctx.runtime.componentUrl))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'meter-compare'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'rhythm-drag'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'virtual-instrument'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'listening-choice'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'singing-practice'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'solfege-sort'))
                    return;
                if (!(__VLS_ctx.legacyRenderer === 'melody-trace'))
                    return;
                __VLS_ctx.add('平行');
            } }, { type: "button" }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign({ onClick: function () {
                var _a = [];
                for (var _i = 0; _i < arguments.length; _i++) {
                    _a[_i] = arguments[_i];
                }
                var $event = _a[0];
                if (!(__VLS_ctx.activeNode))
                    return;
                if (!!(__VLS_ctx.runtime.componentUrl))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'meter-compare'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'rhythm-drag'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'virtual-instrument'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'listening-choice'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'singing-practice'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'solfege-sort'))
                    return;
                if (!(__VLS_ctx.legacyRenderer === 'melody-trace'))
                    return;
                __VLS_ctx.add('下行');
            } }, { type: "button" }));
    }
    else if (__VLS_ctx.legacyRenderer === 'timbre-match') {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "preview-interaction" }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "preview-match-grid" }));
        var _loop_7 = function (item) {
            __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign({ onClick: function () {
                    var _a = [];
                    for (var _i = 0; _i < arguments.length; _i++) {
                        _a[_i] = arguments[_i];
                    }
                    var $event = _a[0];
                    if (!(__VLS_ctx.activeNode))
                        return;
                    if (!!(__VLS_ctx.runtime.componentUrl))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'meter-compare'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'rhythm-drag'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'virtual-instrument'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'listening-choice'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'singing-practice'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'solfege-sort'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'melody-trace'))
                        return;
                    if (!(__VLS_ctx.legacyRenderer === 'timbre-match'))
                        return;
                    __VLS_ctx.add(item);
                } }, { key: (item), type: "button" }));
            (__VLS_ctx.translateText(item));
        };
        for (var _v = 0, _w = __VLS_getVForSourceType((__VLS_ctx.runtimeProps.items || ['小提琴', '长笛', '小号', '鼓'])); _v < _w.length; _v++) {
            var item = _w[_v][0];
            _loop_7(item);
        }
        var _loop_8 = function (option) {
            __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign({ onClick: function () {
                    var _a = [];
                    for (var _i = 0; _i < arguments.length; _i++) {
                        _a[_i] = arguments[_i];
                    }
                    var $event = _a[0];
                    if (!(__VLS_ctx.activeNode))
                        return;
                    if (!!(__VLS_ctx.runtime.componentUrl))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'meter-compare'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'rhythm-drag'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'virtual-instrument'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'listening-choice'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'singing-practice'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'solfege-sort'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'melody-trace'))
                        return;
                    if (!(__VLS_ctx.legacyRenderer === 'timbre-match'))
                        return;
                    __VLS_ctx.choose(option);
                } }, { key: (option), type: "button" }));
            (__VLS_ctx.translateText(option));
        };
        for (var _x = 0, _y = __VLS_getVForSourceType((__VLS_ctx.runtimeProps.options || ['弦乐器', '木管乐器', '铜管乐器', '打击乐器'])); _x < _y.length; _x++) {
            var option = _y[_x][0];
            _loop_8(option);
        }
    }
    else if (__VLS_ctx.legacyRenderer === 'form-order') {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "preview-interaction" }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "preview-buttons" }));
        var _loop_9 = function (section) {
            __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign({ onClick: function () {
                    var _a = [];
                    for (var _i = 0; _i < arguments.length; _i++) {
                        _a[_i] = arguments[_i];
                    }
                    var $event = _a[0];
                    if (!(__VLS_ctx.activeNode))
                        return;
                    if (!!(__VLS_ctx.runtime.componentUrl))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'meter-compare'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'rhythm-drag'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'virtual-instrument'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'listening-choice'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'singing-practice'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'solfege-sort'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'melody-trace'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'timbre-match'))
                        return;
                    if (!(__VLS_ctx.legacyRenderer === 'form-order'))
                        return;
                    __VLS_ctx.add(section);
                } }, { key: (section), type: "button" }));
            (__VLS_ctx.translateText(section));
        };
        for (var _z = 0, _0 = __VLS_getVForSourceType((__VLS_ctx.runtimeProps.sections || ['引子', 'A段', 'B段', '尾声'])); _z < _0.length; _z++) {
            var section = _0[_z][0];
            _loop_9(section);
        }
        __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign(__assign({ onClick: function () {
                var _a = [];
                for (var _i = 0; _i < arguments.length; _i++) {
                    _a[_i] = arguments[_i];
                }
                var $event = _a[0];
                if (!(__VLS_ctx.activeNode))
                    return;
                if (!!(__VLS_ctx.runtime.componentUrl))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'meter-compare'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'rhythm-drag'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'virtual-instrument'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'listening-choice'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'singing-practice'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'solfege-sort'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'melody-trace'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'timbre-match'))
                    return;
                if (!(__VLS_ctx.legacyRenderer === 'form-order'))
                    return;
                __VLS_ctx.finish('曲式顺序可以正常提交。');
            } }, { class: "button primary" }), { type: "button" }));
    }
    else if (__VLS_ctx.legacyRenderer === 'creation-panel') {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "preview-interaction" }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.textarea, __VLS_intrinsicElements.textarea)({
            placeholder: (__VLS_ctx.runtimeProps.defaultTitle || '输入学生创编内容'),
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign(__assign({ onClick: function () {
                var _a = [];
                for (var _i = 0; _i < arguments.length; _i++) {
                    _a[_i] = arguments[_i];
                }
                var $event = _a[0];
                if (!(__VLS_ctx.activeNode))
                    return;
                if (!!(__VLS_ctx.runtime.componentUrl))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'meter-compare'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'rhythm-drag'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'virtual-instrument'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'listening-choice'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'singing-practice'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'solfege-sort'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'melody-trace'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'timbre-match'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'form-order'))
                    return;
                if (!(__VLS_ctx.legacyRenderer === 'creation-panel'))
                    return;
                __VLS_ctx.finish('创编内容可以正常提交。');
            } }, { class: "button primary" }), { type: "button" }));
    }
    else if (__VLS_ctx.legacyRenderer === 'ensemble-roles') {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "preview-interaction" }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "preview-buttons" }));
        var _loop_10 = function (role) {
            __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign(__assign({ onClick: function () {
                    var _a = [];
                    for (var _i = 0; _i < arguments.length; _i++) {
                        _a[_i] = arguments[_i];
                    }
                    var $event = _a[0];
                    if (!(__VLS_ctx.activeNode))
                        return;
                    if (!!(__VLS_ctx.runtime.componentUrl))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'meter-compare'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'rhythm-drag'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'virtual-instrument'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'listening-choice'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'singing-practice'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'solfege-sort'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'melody-trace'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'timbre-match'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'form-order'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'creation-panel'))
                        return;
                    if (!(__VLS_ctx.legacyRenderer === 'ensemble-roles'))
                        return;
                    __VLS_ctx.selectedRole = role;
                    __VLS_ctx.choose(role);
                } }, { key: (role), type: "button" }), { class: ({ selected: __VLS_ctx.selectedRole === role }) }));
            (__VLS_ctx.translateText(role));
        };
        for (var _1 = 0, _2 = __VLS_getVForSourceType((__VLS_ctx.runtimeProps.roles || ['节奏组', '旋律组', '音色组', '指挥'])); _1 < _2.length; _1++) {
            var role = _2[_1][0];
            _loop_10(role);
        }
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "preview-checklist" }));
        var _loop_11 = function (step) {
            __VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({
                key: (step),
            });
            __VLS_asFunctionalElement(__VLS_intrinsicElements.input)(__assign({ onChange: function () {
                    var _a = [];
                    for (var _i = 0; _i < arguments.length; _i++) {
                        _a[_i] = arguments[_i];
                    }
                    var $event = _a[0];
                    if (!(__VLS_ctx.activeNode))
                        return;
                    if (!!(__VLS_ctx.runtime.componentUrl))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'meter-compare'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'rhythm-drag'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'virtual-instrument'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'listening-choice'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'singing-practice'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'solfege-sort'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'melody-trace'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'timbre-match'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'form-order'))
                        return;
                    if (!!(__VLS_ctx.legacyRenderer === 'creation-panel'))
                        return;
                    if (!(__VLS_ctx.legacyRenderer === 'ensemble-roles'))
                        return;
                    __VLS_ctx.toggleStep(step);
                } }, { type: "checkbox", checked: (__VLS_ctx.completedSteps.includes(step)) }));
            (__VLS_ctx.translateText(step));
        };
        for (var _3 = 0, _4 = __VLS_getVForSourceType((__VLS_ctx.runtimeProps.steps || ['确认声部', '分组练习', '合奏排练', '完成展示'])); _3 < _4.length; _3++) {
            var step = _4[_3][0];
            _loop_11(step);
        }
        __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign(__assign({ onClick: function () {
                var _a = [];
                for (var _i = 0; _i < arguments.length; _i++) {
                    _a[_i] = arguments[_i];
                }
                var $event = _a[0];
                if (!(__VLS_ctx.activeNode))
                    return;
                if (!!(__VLS_ctx.runtime.componentUrl))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'meter-compare'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'rhythm-drag'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'virtual-instrument'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'listening-choice'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'singing-practice'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'solfege-sort'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'melody-trace'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'timbre-match'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'form-order'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'creation-panel'))
                    return;
                if (!(__VLS_ctx.legacyRenderer === 'ensemble-roles'))
                    return;
                __VLS_ctx.finish('声部选择和排练记录可以正常提交。');
            } }, { class: "button primary" }), { type: "button", disabled: (!__VLS_ctx.selectedRole) }));
    }
    else if (__VLS_ctx.legacyRenderer === 'summary') {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "preview-interaction" }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.h3, __VLS_intrinsicElements.h3)({});
        __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "preview-buttons" }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign({ onClick: function () {
                var _a = [];
                for (var _i = 0; _i < arguments.length; _i++) {
                    _a[_i] = arguments[_i];
                }
                var $event = _a[0];
                if (!(__VLS_ctx.activeNode))
                    return;
                if (!!(__VLS_ctx.runtime.componentUrl))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'meter-compare'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'rhythm-drag'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'virtual-instrument'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'listening-choice'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'singing-practice'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'solfege-sort'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'melody-trace'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'timbre-match'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'form-order'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'creation-panel'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'ensemble-roles'))
                    return;
                if (!(__VLS_ctx.legacyRenderer === 'summary'))
                    return;
                __VLS_ctx.choose('节拍与节奏');
            } }, { type: "button" }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign({ onClick: function () {
                var _a = [];
                for (var _i = 0; _i < arguments.length; _i++) {
                    _a[_i] = arguments[_i];
                }
                var $event = _a[0];
                if (!(__VLS_ctx.activeNode))
                    return;
                if (!!(__VLS_ctx.runtime.componentUrl))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'meter-compare'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'rhythm-drag'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'virtual-instrument'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'listening-choice'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'singing-practice'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'solfege-sort'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'melody-trace'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'timbre-match'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'form-order'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'creation-panel'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'ensemble-roles'))
                    return;
                if (!(__VLS_ctx.legacyRenderer === 'summary'))
                    return;
                __VLS_ctx.choose('旋律与音高');
            } }, { type: "button" }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign({ onClick: function () {
                var _a = [];
                for (var _i = 0; _i < arguments.length; _i++) {
                    _a[_i] = arguments[_i];
                }
                var $event = _a[0];
                if (!(__VLS_ctx.activeNode))
                    return;
                if (!!(__VLS_ctx.runtime.componentUrl))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'meter-compare'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'rhythm-drag'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'virtual-instrument'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'listening-choice'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'singing-practice'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'solfege-sort'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'melody-trace'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'timbre-match'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'form-order'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'creation-panel'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'ensemble-roles'))
                    return;
                if (!(__VLS_ctx.legacyRenderer === 'summary'))
                    return;
                __VLS_ctx.choose('合作与表现');
            } }, { type: "button" }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.textarea, __VLS_intrinsicElements.textarea)({
            value: (__VLS_ctx.explanation),
            placeholder: "我的音乐发现是……",
        });
        __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign(__assign({ onClick: function () {
                var _a = [];
                for (var _i = 0; _i < arguments.length; _i++) {
                    _a[_i] = arguments[_i];
                }
                var $event = _a[0];
                if (!(__VLS_ctx.activeNode))
                    return;
                if (!!(__VLS_ctx.runtime.componentUrl))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'meter-compare'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'rhythm-drag'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'virtual-instrument'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'listening-choice'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'singing-practice'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'solfege-sort'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'melody-trace'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'timbre-match'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'form-order'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'creation-panel'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'ensemble-roles'))
                    return;
                if (!(__VLS_ctx.legacyRenderer === 'summary'))
                    return;
                __VLS_ctx.finish('课堂回顾可以正常提交。');
            } }, { class: "button primary" }), { type: "button" }));
    }
    else {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)(__assign({ class: "preview-interaction" }));
        __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)({});
        __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign(__assign({ onClick: function () {
                var _a = [];
                for (var _i = 0; _i < arguments.length; _i++) {
                    _a[_i] = arguments[_i];
                }
                var $event = _a[0];
                if (!(__VLS_ctx.activeNode))
                    return;
                if (!!(__VLS_ctx.runtime.componentUrl))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'meter-compare'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'rhythm-drag'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'virtual-instrument'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'listening-choice'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'singing-practice'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'solfege-sort'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'melody-trace'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'timbre-match'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'form-order'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'creation-panel'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'ensemble-roles'))
                    return;
                if (!!(__VLS_ctx.legacyRenderer === 'summary'))
                    return;
                __VLS_ctx.finish();
            } }, { class: "button primary" }), { type: "button" }));
    }
    if (__VLS_ctx.testResult) {
        __VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "preview-result" }));
        (__VLS_ctx.testResult);
    }
}
if (__VLS_ctx.mode === 'package') {
    __VLS_asFunctionalElement(__VLS_intrinsicElements.footer, __VLS_intrinsicElements.footer)(__assign({ class: "preview-navigation" }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign(__assign({ onClick: (__VLS_ctx.previous) }, { class: "button" }), { type: "button", disabled: (__VLS_ctx.previewIndex === 0) }));
    __VLS_asFunctionalElement(__VLS_intrinsicElements.span, __VLS_intrinsicElements.span)({});
    (__VLS_ctx.previewIndex + 1);
    (__VLS_ctx.visibleNodes.length);
    __VLS_asFunctionalElement(__VLS_intrinsicElements.button, __VLS_intrinsicElements.button)(__assign(__assign({ onClick: (__VLS_ctx.next) }, { class: "button primary" }), { type: "button", disabled: (__VLS_ctx.previewIndex >= __VLS_ctx.visibleNodes.length - 1) }));
}
/** @type {__VLS_StyleScopedClasses['package-preview']} */ ;
/** @type {__VLS_StyleScopedClasses['preview-toolbar']} */ ;
/** @type {__VLS_StyleScopedClasses['tag']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['preview-flow']} */ ;
/** @type {__VLS_StyleScopedClasses['preview-device']} */ ;
/** @type {__VLS_StyleScopedClasses['preview-meta']} */ ;
/** @type {__VLS_StyleScopedClasses['preview-interaction']} */ ;
/** @type {__VLS_StyleScopedClasses['preview-buttons']} */ ;
/** @type {__VLS_StyleScopedClasses['preview-interaction']} */ ;
/** @type {__VLS_StyleScopedClasses['rhythm-heading']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['primary']} */ ;
/** @type {__VLS_StyleScopedClasses['preview-buttons']} */ ;
/** @type {__VLS_StyleScopedClasses['rhythm-progress']} */ ;
/** @type {__VLS_StyleScopedClasses['rhythm-answer']} */ ;
/** @type {__VLS_StyleScopedClasses['rhythm-actions']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['primary']} */ ;
/** @type {__VLS_StyleScopedClasses['preview-interaction']} */ ;
/** @type {__VLS_StyleScopedClasses['virtual-instrument-preview']} */ ;
/** @type {__VLS_StyleScopedClasses['preview-interaction']} */ ;
/** @type {__VLS_StyleScopedClasses['preview-buttons']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['primary']} */ ;
/** @type {__VLS_StyleScopedClasses['preview-interaction']} */ ;
/** @type {__VLS_StyleScopedClasses['preview-buttons']} */ ;
/** @type {__VLS_StyleScopedClasses['preview-interaction']} */ ;
/** @type {__VLS_StyleScopedClasses['preview-buttons']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['primary']} */ ;
/** @type {__VLS_StyleScopedClasses['preview-interaction']} */ ;
/** @type {__VLS_StyleScopedClasses['preview-buttons']} */ ;
/** @type {__VLS_StyleScopedClasses['preview-interaction']} */ ;
/** @type {__VLS_StyleScopedClasses['preview-match-grid']} */ ;
/** @type {__VLS_StyleScopedClasses['preview-interaction']} */ ;
/** @type {__VLS_StyleScopedClasses['preview-buttons']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['primary']} */ ;
/** @type {__VLS_StyleScopedClasses['preview-interaction']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['primary']} */ ;
/** @type {__VLS_StyleScopedClasses['preview-interaction']} */ ;
/** @type {__VLS_StyleScopedClasses['preview-buttons']} */ ;
/** @type {__VLS_StyleScopedClasses['preview-checklist']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['primary']} */ ;
/** @type {__VLS_StyleScopedClasses['preview-interaction']} */ ;
/** @type {__VLS_StyleScopedClasses['preview-buttons']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['primary']} */ ;
/** @type {__VLS_StyleScopedClasses['preview-interaction']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['primary']} */ ;
/** @type {__VLS_StyleScopedClasses['preview-result']} */ ;
/** @type {__VLS_StyleScopedClasses['preview-navigation']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['button']} */ ;
/** @type {__VLS_StyleScopedClasses['primary']} */ ;
var __VLS_dollars;
var __VLS_self = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () {
        return {
            emit: emit,
            previewIndex: previewIndex,
            testResult: testResult,
            sequence: sequence,
            selectedRole: selectedRole,
            completedSteps: completedSteps,
            explanation: explanation,
            rhythmSubmitted: rhythmSubmitted,
            rhythmPlaying: rhythmPlaying,
            visibleNodes: visibleNodes,
            activeNode: activeNode,
            runtime: runtime,
            runtimeProps: runtimeProps,
            legacyRenderer: legacyRenderer,
            displayTitle: displayTitle,
            displayPrompt: displayPrompt,
            rhythmTarget: rhythmTarget,
            virtualInstrumentUrl: virtualInstrumentUrl,
            metaLabels: metaLabels,
            resetTest: resetTest,
            choose: choose,
            add: add,
            rhythmLabel: rhythmLabel,
            playRhythmTarget: playRhythmTarget,
            undoRhythm: undoRhythm,
            clearRhythm: clearRhythm,
            submitRhythm: submitRhythm,
            toggleStep: toggleStep,
            previous: previous,
            next: next,
            finish: finish,
            translateText: translateText,
        };
    },
    __typeEmits: {},
    __typeProps: {},
});
exports.default = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () {
        return {};
    },
    __typeEmits: {},
    __typeProps: {},
});
; /* PartiallyEnd: #4569/main.vue */
