import { describe, it, expect } from "vitest";
import { mkdir, writeFile } from "fs/promises";
import * as path from "node:path";
import * as os from "node:os";
import { createIgnoreMatcher } from "../src/utils/ignoreMatcher.js";

describe("ignoreMatcher", () => {
  it("respects builtin ignore rules", async () => {
    const root = await mkdir(
      path.join(os.tmpdir(), `scanner-ignore-${Date.now()}`),
      { recursive: true }
    );

    const ig = await createIgnoreMatcher(root);

    expect(ig.ignores("node_modules/test.js")).toBe(true);
    expect(ig.ignores("dist/output.js")).toBe(true);
    expect(ig.ignores("src/index.ts")).toBe(false);
  });

  it("respects .gitignore rules", async () => {
    const root = await mkdir(
      path.join(os.tmpdir(), `scanner-gitignore-${Date.now()}`),
      { recursive: true }
    );

    await writeFile(path.join(root, ".gitignore"), "secret.txt");

    const ig = await createIgnoreMatcher(root);

    expect(ig.ignores("secret.txt")).toBe(true);
  });
});
