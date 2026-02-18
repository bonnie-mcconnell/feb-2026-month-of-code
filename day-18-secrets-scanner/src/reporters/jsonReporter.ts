import type { Finding } from "../types/finding.js";

export function reportToJson(findings: Finding[]): string {
  return JSON.stringify(
    {
      total: findings.length,
      findings
    },
    null,
    2
  );
}
