import { describe, it, expect } from "vitest";
import { calculateShannonEntropy, isHighEntropyString } from "../src/scanner/entropyEngine.js";

describe("Entropy Engine", () => {
  it("calculates low entropy correctly", () => {
    const entropy = calculateShannonEntropy("aaaaaaaaaa");
    expect(entropy).toBe(0);
  });

  it("detects high entropy strings", () => {
    const random = "akdjf9834jskdfj9384jsdfkjsdfkjsdf";
    const result = isHighEntropyString(random, 3.0, 10);
    expect(result).toBe(true);
  });

  it("rejects short strings", () => {
    const result = isHighEntropyString("abc123");
    expect(result).toBe(false);
  });
});
