import type { Finding } from "../types/finding.js";
import { calculateShannonEntropy } from "./entropyEngine.js";

export function scanWithEntropy(
  filePath: string,
  content: string,
  threshold: number = 4.5,
  minLength: number = 20
): Finding[] {
  const findings: Finding[] = [];
  const lines = content.split(/\r?\n/);

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    const entropy = calculateShannonEntropy(line);

    if (line.length >= minLength && entropy >= threshold) {
      findings.push({
        filePath,
        lineNumber: i + 1,
        ruleId: "high-entropy-string",
        description: "High entropy string detected",
        matchType: "entropy",
        snippet: line.slice(0, 20) + "...",
        entropyScore: entropy,
        severity: "medium"
      });
    }
  }

  return findings;
}
