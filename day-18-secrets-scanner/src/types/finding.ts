interface Finding {
  filePath: string;
  lineNumber: number;
  ruleId: string;
  matchType: "pattern" | "entropy";
  snippet: string;
  entropyScore?: number;
  severity: "low" | "medium" | "high";
}
