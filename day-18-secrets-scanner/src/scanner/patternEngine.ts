import type { Rule } from "../types/rule.js";
import type { Finding } from "../types/finding.js";

export function scanWithPatterns(
  filePath: string,
  content: string,
  rules: Rule[]
): Finding[] {
  const findings: Finding[] = [];
  const lines = content.split(/\r?\n/);

  for (let lineIndex = 0; lineIndex < lines.length; lineIndex++) {
    const line = lines[lineIndex];

    for (const rule of rules) {
      rule.regex.lastIndex = 0;

      let match: RegExpExecArray | null;

      while ((match = rule.regex.exec(line)) !== null) {
        const snippet = redact(match[0]);

        findings.push({
          filePath,
          lineNumber: lineIndex + 1,
          ruleId: rule.ruleId,
          matchType: "pattern",
          snippet,
          severity: rule.severity
        });
      }
    }
  }

  return findings;
}

function redact(value: string): string {
  if (value.length <= 8) return "[REDACTED]";
  return value.slice(0, 4) + "..." + value.slice(-4);
}
