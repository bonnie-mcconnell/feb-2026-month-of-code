import type { Finding } from "../types/finding.js";
import { calculateShannonEntropy } from "./entropyEngine.js";

const STRING_LITERAL_REGEX =
  /["'`](?<value>[A-Za-z0-9+/_=-]{20,})["'`]/g;

function looksLikeSecret(value: string): boolean {
  // Must contain at least one digit
  if (!/[0-9]/.test(value)) return false;

  // Must contain at least one letter
  if (!/[A-Za-z]/.test(value)) return false;

  // Avoid obvious camelCase identifiers
  if (/^[a-z]+([A-Z][a-z]+)+$/.test(value)) return false;

  return true;
}

export function scanWithEntropy(
  filePath: string,
  content: string,
  threshold: number = 3.5,
  minLength: number = 20
): Finding[] {
  const findings: Finding[] = [];
  const seen = new Set<string>();

  const matches = content.matchAll(STRING_LITERAL_REGEX);

  for (const match of matches) {
    const candidate = match.groups?.value;
    if (!candidate) continue;

    if (candidate.length < minLength) continue;
    if (!looksLikeSecret(candidate)) continue;

    const entropy = calculateShannonEntropy(candidate);

    if (entropy >= threshold) {
      const lineNumber =
        content.slice(0, match.index!).split(/\r?\n/).length;

      const key = `${filePath}:${lineNumber}:${candidate}`;
      if (seen.has(key)) continue;
      seen.add(key);

      findings.push({
        filePath,
        lineNumber,
        ruleId: "high-entropy-string",
        description: "High entropy string detected",
        matchType: "entropy",
        snippet: candidate.slice(0, 20) + "...",
        entropyScore: entropy,
        severity: "medium"
      });
    }
  }

  return findings;
}
