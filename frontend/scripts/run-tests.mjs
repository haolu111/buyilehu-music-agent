import { spawnSync } from "node:child_process";
import { mkdirSync, readdirSync, rmSync } from "node:fs";
import { basename, dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { buildSync } from "esbuild";

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const testsDir = join(root, "tests");
const outDir = join(root, ".tmp_frontend_tests");
mkdirSync(outDir, { recursive: true });

const tests = readdirSync(testsDir)
  .filter((file) => file.endsWith(".test.ts"))
  .sort();

let failures = 0;
for (const testFile of tests) {
  const entry = join(testsDir, testFile);
  const outfile = join(outDir, `${basename(testFile, ".ts")}.mjs`);
  try {
    buildSync({
      entryPoints: [entry],
      bundle: true,
      platform: "node",
      format: "esm",
      outfile,
      logLevel: "silent",
    });
    const result = spawnSync(process.execPath, [outfile], { stdio: "inherit" });
    if (result.status !== 0) failures += 1;
    else console.log(`✓ ${testFile}`);
  } catch (error) {
    failures += 1;
    console.error(`✗ ${testFile}`);
    console.error(error);
  }
}

rmSync(outDir, { recursive: true, force: true });

if (failures) {
  console.error(`${failures} frontend test file(s) failed.`);
  process.exit(1);
}

console.log(`${tests.length} frontend test file(s) passed.`);
