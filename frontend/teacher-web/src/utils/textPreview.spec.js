"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var vitest_1 = require("vitest");
var textPreview_1 = require("./textPreview");
(0, vitest_1.describe)('createTextPreview', function () {
    (0, vitest_1.it)('caps oversized content and marks the preview as truncated', function () {
        var preview = (0, textPreview_1.createTextPreview)('教'.repeat(textPreview_1.RAW_PREVIEW_MAX_LENGTH + 1));
        (0, vitest_1.expect)(preview.content).toHaveLength(textPreview_1.RAW_PREVIEW_MAX_LENGTH);
        (0, vitest_1.expect)(preview.truncated).toBe(true);
    });
});
