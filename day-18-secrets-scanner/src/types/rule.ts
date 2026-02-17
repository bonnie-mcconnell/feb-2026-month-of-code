import type { Severity } from "./finding.js";

export interface Rule {
  ruleId: string;
  description: string;
  regex: RegExp;
  severity: Severity;
}
