import type { Finding } from "../types/finding.js";

const severityWeight: Record<string, number> = {
  critical: 4,
  high: 3,
  medium: 2,
  low: 1
};

export function stableSortFindings(findings: Finding[]): Finding[] {
  return [...findings].sort((a, b) => {
    const severityDiff =
      severityWeight[b.severity] - severityWeight[a.severity];

    if (severityDiff !== 0) return severityDiff;

    if (a.filePath !== b.filePath) {
      return a.filePath.localeCompare(b.filePath);
    }

    return a.lineNumber - b.lineNumber;
  });
}
