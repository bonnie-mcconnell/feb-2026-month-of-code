import { describe, it, expect } from "vitest";
import { spawn } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const fixturesDir = path.join(__dirname, "fixtures");

describe("CLI exit code", () => {
  it("returns exit code 1 when secrets found", async () => {
    const cliPath = path.join(__dirname, "../dist/index.js");

    const result = await new Promise<number>((resolve) => {
      const child = spawn("node", [cliPath, fixturesDir]);

      child.on("exit", code => resolve(code ?? 0));
    });

    expect(result).toBe(1);
  });
});
