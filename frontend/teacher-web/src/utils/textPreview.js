"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.RAW_PREVIEW_MAX_LENGTH = void 0;
exports.createTextPreview = createTextPreview;
exports.RAW_PREVIEW_MAX_LENGTH = 8000;
function createTextPreview(value) {
    var content = value || '';
    return {
        content: content.slice(0, exports.RAW_PREVIEW_MAX_LENGTH),
        truncated: content.length > exports.RAW_PREVIEW_MAX_LENGTH,
    };
}
