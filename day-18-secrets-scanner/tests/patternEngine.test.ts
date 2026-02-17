import { describe, it, expect } from "vitest";
import { scanWithPatterns } from "../src/scanner/patternEngine.js";
import { BUILTIN_RULES } from "../src/rules/builtinRules.js";

describe("patternEngine", () => {
  it("detects AWS access key", () => {
    const content = "const key = 'AKIA1234567890ABCDEF';";
    const findings = scanWithPatterns("test.js", content, BUILTIN_RULES);

    expect(findings.length).toBeGreaterThan(0);
    expect(findings[0].ruleId).toBe("aws-access-key-id");
  });

  it("does not flag normal strings", () => {
    const content = "const name = 'hello world';";
    const findings = scanWithPatterns("test.js", content, BUILTIN_RULES);

    expect(findings.length).toBe(0);
  });

  it("detects JWT format", () => {
    const jwt =
      "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9." +
      "eyJzdWIiOiIxMjM0NTY3ODkwIn0." +
      "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c";

    const findings = scanWithPatterns("auth.js", jwt, BUILTIN_RULES);

    expect(findings.some(f => f.ruleId === "jwt")).toBe(true);
  });
});
