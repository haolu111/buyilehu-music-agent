"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var node_fs_1 = require("node:fs");
var node_path_1 = require("node:path");
var vitest_1 = require("vitest");
var styles = (0, node_fs_1.readFileSync)((0, node_path_1.resolve)(process.cwd(), 'src/style.css'), 'utf8');
(0, vitest_1.describe)('global mobile navigation styles', function () {
    (0, vitest_1.it)('keeps a single approved token root and does not restore horizontal sidebar navigation', function () {
        (0, vitest_1.expect)(styles.match(/^:root\s*\{/gm)).toHaveLength(1);
        (0, vitest_1.expect)(styles).not.toContain('.sidebar{position:static');
        (0, vitest_1.expect)(styles).not.toContain('grid-template-columns:repeat(5,120px)');
        (0, vitest_1.expect)(styles).not.toContain('button,.button { min-height:38px');
        (0, vitest_1.expect)(styles).toContain('.nav-label-mobile');
        (0, vitest_1.expect)(styles).toContain('.nav-label-desktop');
    });
    (0, vitest_1.it)('keeps proposal evidence styles consolidated after the details-panel refresh', function () {
        (0, vitest_1.expect)(styles.match(/\.proposal-evidence-grid\{/g)).toHaveLength(2);
        (0, vitest_1.expect)(styles.match(/\.objective-list\{/g)).toHaveLength(1);
        (0, vitest_1.expect)(styles.match(/\.source-section-list\{/g)).toHaveLength(2);
        (0, vitest_1.expect)(styles).toContain('.proposal-evidence>summary');
    });
});
