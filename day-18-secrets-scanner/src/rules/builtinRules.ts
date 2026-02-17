import type { Rule } from "../types/rule.js";

export const BUILTIN_RULES: Rule[] = [
  {
    ruleId: "aws-access-key-id",
    description: "AWS Access Key ID",
    regex: /\bAKIA[0-9A-Z]{16}\b/g,
    severity: "high"
  },
  {
    ruleId: "private-key",
    description: "Private key block",
    regex: /-----BEGIN (RSA|EC|OPENSSH|DSA) PRIVATE KEY-----/,
    severity: "high"
  },
  {
    ruleId: "bearer-token",
    description: "Bearer token",
    regex: /\bBearer\s+[A-Za-z0-9\-._~+/]+=*\b/g,
    severity: "medium"
  },
  {
    ruleId: "jwt",
    description: "JWT token",
    regex: /\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b/g,
    severity: "medium"
  },
  {
    ruleId: "generic-api-key",
    description: "Generic API key-like string",
    regex: /\b[A-Za-z0-9]{32,45}\b/g,
    severity: "low"
  }
];
