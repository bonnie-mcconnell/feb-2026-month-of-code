import { describe, it, expect } from "vitest";
import { scanDirectory } from "../src/scanner/scanner.js";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const fixturesDir = path.join(__dirname, "fixtures");

describe("Integration: secrets scanner", () => {
  it("detects AWS access key", async () => {
    const findings = await scanDirectory(fixturesDir);

    const awsFinding = findings.find(f =>
      f.ruleId === "aws-access-key-id"
    );

    expect(awsFinding).toBeDefined();
    expect(awsFinding?.severity).toBe("high");
  });

  it("detects entropy strings", async () => {
    const findings = await scanDirectory(fixturesDir);

    const entropyFinding = findings.find(f =>
      f.ruleId === "high-entropy-string"
    );

    expect(entropyFinding).toBeDefined();
  });

  it("does not flag clean files falsely", async () => {
    const findings = await scanDirectory(fixturesDir);

    const cleanFileFindings = findings.filter(f =>
      f.filePath.endsWith("clean.txt")
    );

    expect(cleanFileFindings.length).toBe(0);
  });
});
