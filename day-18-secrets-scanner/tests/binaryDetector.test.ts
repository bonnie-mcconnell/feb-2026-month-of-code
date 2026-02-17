import { describe, it, expect } from "vitest";
import { writeFile, mkdir } from "fs/promises";
import path from "path";
import os from "os";
import { isBinaryFile } from "../src/scanner/binaryDetector.js";

async function createTempDir(): Promise<string> {
  const dir = await mkdir(
    path.join(os.tmpdir(), `scanner-test-${Date.now()}`),
    { recursive: true }
  );
  return dir;
}

describe("binaryDetector", () => {
  it("detects text file as non-binary", async () => {
    const dir = await createTempDir();
    const filePath = path.join(dir, "test.txt");

    await writeFile(filePath, "This is normal ASCII text.");

    const result = await isBinaryFile(filePath);
    expect(result).toBe(false);
  });

  it("detects file with null bytes as binary", async () => {
    const dir = await createTempDir();
    const filePath = path.join(dir, "binary.bin");

    const buffer = Buffer.from([0, 159, 146, 150, 0, 0, 0]);
    await writeFile(filePath, buffer);

    const result = await isBinaryFile(filePath);
    expect(result).toBe(true);
  });
});
