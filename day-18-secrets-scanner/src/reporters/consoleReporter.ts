import type { Finding, Severity } from "../types/finding.js";

export function reportToConsole(findings: Finding[]): void {
  if (findings.length === 0) {
    console.log("✔ No secrets detected.");
    return;
  }

  const severityCount: Record<Severity, number> = {
    critical: 0,
    high: 0,
    medium: 0,
    low: 0
  };

  for (const finding of findings) {
    severityCount[finding.severity]++;

    console.log(
      `[${finding.severity.toUpperCase()}] ${finding.ruleId}`
    );
    console.log(`  File: ${finding.filePath}`);
    console.log(`  Line: ${finding.lineNumber}`);
    console.log(`  Description: ${finding.description}`);
    console.log(`  Snippet: ${finding.snippet}`);

    if (finding.entropyScore !== undefined) {
      console.log(`  Entropy: ${finding.entropyScore.toFixed(2)}`);
    }

    console.log("");
  }

  console.log("Summary:");
  console.log(`  Critical: ${severityCount.critical}`);
  console.log(`  High:     ${severityCount.high}`);
  console.log(`  Medium:   ${severityCount.medium}`);
  console.log(`  Low:      ${severityCount.low}`);
  console.log("");
  console.log(`Total findings: ${findings.length}`);
}
