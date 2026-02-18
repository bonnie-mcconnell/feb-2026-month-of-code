export type MatchType = "pattern" | "entropy";
export type Severity = "low" | "medium" | "high" | "critical";

export interface Finding {
  filePath: string;
  lineNumber: number;
  ruleId: string;
  description: string;
  matchType: MatchType;
  snippet: string;
  entropyScore?: number;
  severity: Severity;
}
