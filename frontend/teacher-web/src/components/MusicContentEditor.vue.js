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
var props = defineProps();
var emit = defineEmits();
var catalog = {
    rhythm_pattern_ids: [
        { id: 'rhythm_ta_ta', label: '四分音符 × 2', resolved: { tokens: ['ta', 'ta'], beats: 2 } },
        { id: 'rhythm_titi_ta', label: '八分音符组 + 四分音符', resolved: { tokens: ['ti-ti', 'ta'], beats: 2 } },
        { id: 'rhythm_ta_rest', label: '四分音符 + 四分休止', resolved: { tokens: ['ta', 'rest'], beats: 2 } },
        { id: 'rhythm_syncopation', label: '切分节奏', resolved: { tokens: ['ti', 'ta-a', 'ti'], beats: 2 } },
    ],
    pitch_set_ids: [
        { id: 'pitch_do_re_mi', label: 'do re mi', resolved: { notes: ['do', 're', 'mi'] } },
        { id: 'pitch_do_re_mi_sol_la', label: '五声音阶 do re mi sol la', resolved: { notes: ['do', 're', 'mi', 'sol', 'la'] } },
        { id: 'pitch_diatonic', label: '七声音阶', resolved: { notes: ['do', 're', 'mi', 'fa', 'sol', 'la', 'ti'] } },
    ],
    melody_phrase_ids: [
        { id: 'melody_step_up', label: '级进上行', resolved: { notes: ['do', 're', 'mi', 'sol'], contour: ['same', 'up', 'up', 'up'] } },
        { id: 'melody_step_down', label: '级进下行', resolved: { notes: ['sol', 'mi', 're', 'do'], contour: ['same', 'down', 'down', 'down'] } },
        { id: 'melody_arch', label: '拱形旋律', resolved: { notes: ['do', 'mi', 'sol', 'mi', 'do'], contour: ['same', 'up', 'up', 'down', 'down'] } },
    ],
    form_ids: [
        { id: 'form_ab', label: '二段体 AB', resolved: { sections: ['A', 'B'] } },
        { id: 'form_aba', label: '三段体 ABA', resolved: { sections: ['A', 'B', 'A'] } },
        { id: 'form_aaba', label: 'AABA', resolved: { sections: ['A', 'A', 'B', 'A'] } },
        { id: 'form_rondo', label: '回旋曲式 ABACA', resolved: { sections: ['A', 'B', 'A', 'C', 'A'] } },
    ],
    dynamic_ids: [
        { id: 'dynamic_p', label: '弱 p', resolved: { symbol: 'p', gain: .35 } },
        { id: 'dynamic_mp', label: '中弱 mp', resolved: { symbol: 'mp', gain: .5 } },
        { id: 'dynamic_mf', label: '中强 mf', resolved: { symbol: 'mf', gain: .68 } },
        { id: 'dynamic_f', label: '强 f', resolved: { symbol: 'f', gain: .86 } },
        { id: 'dynamic_crescendo', label: '渐强', resolved: { symbol: '<', curve: 'crescendo' } },
        { id: 'dynamic_diminuendo', label: '渐弱', resolved: { symbol: '>', curve: 'diminuendo' } },
    ],
    timbre_ids: [
        { id: 'timbre_piano', label: '钢琴', resolved: { instrument: 'acoustic_grand_piano', family: '键盘乐器' } },
        { id: 'timbre_xylophone', label: '木琴', resolved: { instrument: 'xylophone', family: '打击乐器' } },
        { id: 'timbre_flute', label: '长笛', resolved: { instrument: 'flute', family: '木管乐器' } },
        { id: 'timbre_violin', label: '小提琴', resolved: { instrument: 'violin', family: '弦乐器' } },
        { id: 'timbre_drum', label: '鼓', resolved: { instrument: 'taiko_drum', family: '打击乐器' } },
    ],
};
var selection = (0, vue_1.reactive)(Object.fromEntries(Object.keys(catalog).map(function (key) { return [key, []]; })));
var resolvedKeys = {
    rhythm_pattern_ids: 'rhythm_patterns', pitch_set_ids: 'pitch_sets',
    melody_phrase_ids: 'melody_phrases', form_ids: 'forms',
    dynamic_ids: 'dynamics', timbre_ids: 'timbres',
};
(0, vue_1.watch)(function () { return props.initial; }, function (initial) {
    for (var _i = 0, _a = Object.keys(catalog); _i < _a.length; _i++) {
        var key = _a[_i];
        selection[key] = Array.isArray(initial === null || initial === void 0 ? void 0 : initial[key]) ? __spreadArray([], initial[key], true) : [];
    }
}, { immediate: true, deep: true });
(0, vue_1.watch)(selection, function () {
    var musicContent = {};
    var resolvedMusicContent = {};
    var _loop_1 = function (key, ids) {
        if (!ids.length)
            return "continue";
        musicContent[key] = __spreadArray([], ids, true);
        resolvedMusicContent[resolvedKeys[key]] = ids.map(function (id) {
            var option = catalog[key].find(function (item) { return item.id === id; });
            return __assign({ id: id, label: option.label }, option.resolved);
        });
    };
    for (var _i = 0, _a = Object.entries(selection); _i < _a.length; _i++) {
        var _b = _a[_i], key = _b[0], ids = _b[1];
        _loop_1(key, ids);
    }
    emit('change', { musicContent: musicContent, resolvedMusicContent: resolvedMusicContent });
}, { deep: true, immediate: true });
debugger; /* PartiallyEnd: #3632/scriptSetup.vue */
var __VLS_ctx = {};
var __VLS_components;
var __VLS_directives;
__VLS_asFunctionalElement(__VLS_intrinsicElements.section, __VLS_intrinsicElements.section)(__assign({ class: "music-content-editor" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.div, __VLS_intrinsicElements.div)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.h3, __VLS_intrinsicElements.h3)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.p, __VLS_intrinsicElements.p)(__assign({ class: "muted" }));
__VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.select, __VLS_intrinsicElements.select)({
    value: (__VLS_ctx.selection.rhythm_pattern_ids),
    multiple: true,
});
for (var _i = 0, _a = __VLS_getVForSourceType((__VLS_ctx.catalog.rhythm_pattern_ids)); _i < _a.length; _i++) {
    var item = _a[_i][0];
    __VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
        key: (item.id),
        value: (item.id),
    });
    (item.label);
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.select, __VLS_intrinsicElements.select)({
    value: (__VLS_ctx.selection.pitch_set_ids),
    multiple: true,
});
for (var _b = 0, _c = __VLS_getVForSourceType((__VLS_ctx.catalog.pitch_set_ids)); _b < _c.length; _b++) {
    var item = _c[_b][0];
    __VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
        key: (item.id),
        value: (item.id),
    });
    (item.label);
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.select, __VLS_intrinsicElements.select)({
    value: (__VLS_ctx.selection.melody_phrase_ids),
    multiple: true,
});
for (var _d = 0, _e = __VLS_getVForSourceType((__VLS_ctx.catalog.melody_phrase_ids)); _d < _e.length; _d++) {
    var item = _e[_d][0];
    __VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
        key: (item.id),
        value: (item.id),
    });
    (item.label);
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.select, __VLS_intrinsicElements.select)({
    value: (__VLS_ctx.selection.form_ids),
    multiple: true,
});
for (var _f = 0, _g = __VLS_getVForSourceType((__VLS_ctx.catalog.form_ids)); _f < _g.length; _f++) {
    var item = _g[_f][0];
    __VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
        key: (item.id),
        value: (item.id),
    });
    (item.label);
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.select, __VLS_intrinsicElements.select)({
    value: (__VLS_ctx.selection.dynamic_ids),
    multiple: true,
});
for (var _h = 0, _j = __VLS_getVForSourceType((__VLS_ctx.catalog.dynamic_ids)); _h < _j.length; _h++) {
    var item = _j[_h][0];
    __VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
        key: (item.id),
        value: (item.id),
    });
    (item.label);
}
__VLS_asFunctionalElement(__VLS_intrinsicElements.label, __VLS_intrinsicElements.label)({});
__VLS_asFunctionalElement(__VLS_intrinsicElements.select, __VLS_intrinsicElements.select)({
    value: (__VLS_ctx.selection.timbre_ids),
    multiple: true,
});
for (var _k = 0, _l = __VLS_getVForSourceType((__VLS_ctx.catalog.timbre_ids)); _k < _l.length; _k++) {
    var item = _l[_k][0];
    __VLS_asFunctionalElement(__VLS_intrinsicElements.option, __VLS_intrinsicElements.option)({
        key: (item.id),
        value: (item.id),
    });
    (item.label);
}
/** @type {__VLS_StyleScopedClasses['music-content-editor']} */ ;
/** @type {__VLS_StyleScopedClasses['muted']} */ ;
var __VLS_dollars;
var __VLS_self = (await Promise.resolve().then(function () { return require('vue'); })).defineComponent({
    setup: function () {
        return {
            catalog: catalog,
            selection: selection,
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
