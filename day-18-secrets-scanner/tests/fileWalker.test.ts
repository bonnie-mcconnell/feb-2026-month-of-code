import { describe, it, expect } from "vitest";
import { mkdir, writeFile } from "fs/promises";
import path from "path";
import os from "os";
import { createIgnoreMatcher } from "../src/utils/ignoreMatcher.js";
import { walkFiles } from "../src/scanner/fileWalker.js";

describe("fileWalker", () => {
  it("walks files and skips ignored + binary", async () => {
    const root = await mkdir(
      path.join(os.tmpdir(), `scanner-walk-${Date.now()}`),
      { recursive: true }
    );

    await mkdir(path.join(root, "node_modules"), { recursive: true });

    await writeFile(path.join(root, "clean.txt"), "hello world");
    await writeFile(path.join(root, "node_modules", "ignored.js"), "ignored");

    const binaryBuffer = Buffer.from([0, 0, 0, 0, 0]);
    await writeFile(path.join(root, "binary.bin"), binaryBuffer);

    const ig = await createIgnoreMatcher(root);

    const files: string[] = [];

    for await (const file of walkFiles(root, ig)) {
      files.push(path.basename(file));
    }

    expect(files).toContain("clean.txt");
    expect(files).not.toContain("ignored.js");
    expect(files).not.toContain("binary.bin");
  });
});
