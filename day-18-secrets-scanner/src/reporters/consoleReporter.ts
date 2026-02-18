import type { Finding } from "../types/finding.js";

export function reportToConsole(findings: Finding[]): void {
  if (findings.length === 0) {
    console.log("✔ No secrets detected.");
    return;
  }

  for (const finding of findings) {
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

  console.log(`Found ${findings.length} potential secrets.`);
}
